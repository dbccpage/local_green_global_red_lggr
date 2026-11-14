"""Build Paper VI with shared pdfLaTeX style."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PAPER_STEM = "lggr_vi_nonlinear_aggregation_and_adjoint_probing"
RELEASE_DATE = "2026-10-15"
PAPER_MD = PACKAGE_ROOT / f"{PAPER_STEM}.md"
BUNDLED_PREAMBLE = PACKAGE_ROOT / "scripts" / "obstruction-preamble.tex"
TEX_OUT = PACKAGE_ROOT / f"{PAPER_STEM}.tex"
PDF_OUT = PACKAGE_ROOT / f"{PAPER_STEM}.pdf"
BUILD_LOG_NAME = f"{PAPER_STEM}-{RELEASE_DATE}-pdflatex.log"
FIGURES = (
    "figure_1_kernel_and_adjoint.png",
    "figure_2_sign_probe_error.png",
)

# Noon UTC keeps the calendar date on 2026-10-15 in both UTC and North
# American time zones while remaining deterministic.
SOURCE_EPOCH = 1760529600
SHARED_PREAMBLE_SHA256 = (
    "050ff13b2c82b6136fc4bbd9b2fc160fc0483ff7f96508277697b0316c584158"
)


def shared_preamble() -> Path | None:
    """Locate the live obstruction-paper-kit preamble when available."""

    for ancestor in (PACKAGE_ROOT, *PACKAGE_ROOT.parents):
        for subpath in ("coda_atlas", "coda_university"):
            candidate = (
                ancestor
                / subpath
                / "_kits"
                / "obstruction_paper_kit"
                / "obstruction_preamble.tex"
            )
            if candidate.is_file():
                return candidate
    return None


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_shared_preamble() -> Path:
    """Use the hash-bound live kit, with an exact bundled archive fallback."""

    source = shared_preamble()
    if source is not None:
        observed = sha256_of(source)
        if observed != SHARED_PREAMBLE_SHA256:
            raise SystemExit(
                "BLOCKED: shared obstruction preamble changed; review and re-pin "
                f"its hash (expected {SHARED_PREAMBLE_SHA256}, got {observed})"
            )
        source_bytes = source.read_bytes()
        if not BUNDLED_PREAMBLE.is_file() or BUNDLED_PREAMBLE.read_bytes() != source_bytes:
            BUNDLED_PREAMBLE.write_bytes(source_bytes)
        print(f"Shared preamble: {source} ({observed})")

    if not BUNDLED_PREAMBLE.is_file():
        raise SystemExit(
            "BLOCKED: neither the live nor bundled obstruction preamble is available"
        )
    bundled_hash = sha256_of(BUNDLED_PREAMBLE)
    if bundled_hash != SHARED_PREAMBLE_SHA256:
        raise SystemExit(
            "BLOCKED: bundled obstruction preamble does not match the canonical "
            f"hash (expected {SHARED_PREAMBLE_SHA256}, got {bundled_hash})"
        )
    if source is None:
        print(
            "Shared preamble: live CODA tree unavailable; using exact bundled copy "
            f"({bundled_hash})"
        )
    return BUNDLED_PREAMBLE


def need(tool: str) -> str:
    """Resolve a build tool, including standard per-user Windows installs."""

    path = shutil.which(tool)
    if path:
        return path

    local_app_data = os.environ.get("LOCALAPPDATA")
    if os.name == "nt" and local_app_data:
        base = Path(local_app_data)
        fallbacks = {
            "pandoc": base / "Pandoc" / "pandoc.exe",
            "pdflatex": (
                base
                / "Programs"
                / "MiKTeX"
                / "miktex"
                / "bin"
                / "x64"
                / "pdflatex.exe"
            ),
        }
        candidate = fallbacks.get(tool)
        if candidate and candidate.is_file():
            return str(candidate)

    raise SystemExit(f"BLOCKED: {tool} not found on PATH or a known user-local path")


def build_tex(destination: Path) -> Path:
    pandoc = need("pandoc")
    preamble = sync_shared_preamble()
    command = [
        pandoc,
        "--from",
        (
            "markdown+tex_math_dollars+tex_math_single_backslash+pipe_tables"
            "+raw_tex+backtick_code_blocks+fenced_code_attributes"
        ),
        "--include-in-header",
        str(preamble),
        "--highlight-style",
        "tango",
        "--wrap",
        "preserve",
        "-V",
        "colorlinks=true",
        "-V",
        "linkcolor=oblink",
        "-V",
        "urlcolor=oblink",
        "-V",
        "citecolor=oblink",
        "-V",
        "fontsize=11pt",
        "-V",
        "title-meta=Blind Spots Under Nonlinear Aggregation and Adjoint Probing",
        "-V",
        "author-meta=Jeremy H. Carroll",
        "-V",
        "keywords=observation operator, kernel, nonlinear aggregation, Gram operator, adjoint probing, singular values, Lean 4",
        "-V",
        "pdftitle=Blind Spots Under Nonlinear Aggregation and Adjoint Probing",
        "-V",
        "pdfauthor=Jeremy H. Carroll",
        "-V",
        "pdfkeywords=observation operator, kernel, nonlinear aggregation, Gram operator, adjoint probing, singular values, Lean 4",
        "-V",
        "pdfsubject=Finite observation blind spots, Gram response, and adjoint probing",
        "-M",
        f"date={RELEASE_DATE}",
        "-s",
        "-o",
        str(destination),
        str(PAPER_MD),
    ]
    run = subprocess.run(
        command,
        cwd=PACKAGE_ROOT,
        capture_output=True,
        timeout=1800,
        check=False,
    )
    stderr = run.stderr.decode("utf-8", errors="replace")
    if run.returncode != 0:
        raise SystemExit(
            "pandoc failed:\n"
            + run.stdout.decode("utf-8", errors="replace")
            + stderr
        )
    for line in stderr.strip().splitlines()[:10]:
        if line.strip():
            print(f"    pandoc: {line}")

    destination.write_bytes(
        destination.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    )
    return destination


def build_pdf(tex: Path, destination: Path, log_destination: Path) -> Path:
    pdflatex = need("pdflatex")
    environment = dict(os.environ)
    environment["SOURCE_DATE_EPOCH"] = str(SOURCE_EPOCH)
    environment["FORCE_SOURCE_DATE"] = "1"

    with tempfile.TemporaryDirectory(prefix="lggr-vi-pdf-") as raw_tmp:
        temporary = Path(raw_tmp)
        working_tex = temporary / tex.name
        shutil.copyfile(tex, working_tex)
        temporary_figures = temporary / "figures"
        temporary_figures.mkdir()
        for figure_name in FIGURES:
            shutil.copyfile(
                PACKAGE_ROOT / "figures" / figure_name,
                temporary_figures / figure_name,
            )

        final_log = ""
        for pass_number in (1, 2):
            run = subprocess.run(
                [
                    pdflatex,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    working_tex.name,
                ],
                cwd=temporary,
                capture_output=True,
                timeout=1800,
                env=environment,
                check=False,
            )
            transcript = run.stdout.decode(
                "utf-8", errors="replace"
            ) + run.stderr.decode("utf-8", errors="replace")
            if run.returncode != 0:
                log = temporary / f"{working_tex.stem}.log"
                tail = ""
                if log.exists():
                    tail = "\n".join(
                        log.read_text(
                            encoding="utf-8", errors="replace"
                        ).splitlines()[-50:]
                    )
                raise SystemExit(
                    f"pdflatex pass {pass_number} failed:\n{tail}\n{transcript[-2000:]}"
                )
            log = temporary / f"{working_tex.stem}.log"
            final_log = log.read_text(encoding="utf-8", errors="replace")
            serious_markers = (
                "Missing character:",
                "Unable to load picture or PDF file",
                "ignored error:",
                "Overfull \\hbox",
                "Overfull \\vbox",
                "Float too large for page",
                "Dimension too large",
            )
            observed = [
                marker
                for marker in serious_markers
                if marker in transcript or marker in final_log
            ]
            if observed:
                raise SystemExit(
                    f"pdflatex pass {pass_number} emitted release-blocking diagnostics: "
                    + ", ".join(observed)
                )

        shutil.copyfile(temporary / f"{tex.stem}.pdf", destination)
        log_destination.parent.mkdir(parents=True, exist_ok=True)
        log_destination.write_text(final_log, encoding="utf-8", newline="\n")
    print(f"Build log: {log_destination}")
    print("Layout diagnostics: no missing glyphs, clipping markers, or overfull boxes")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex-only", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="write TeX, PDF, and the build log to this directory",
    )
    args = parser.parse_args()

    if args.output_dir is None:
        tex_out = TEX_OUT
        pdf_out = PDF_OUT
        log_out = PACKAGE_ROOT / "dist" / BUILD_LOG_NAME
    else:
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        tex_out = output_dir / TEX_OUT.name
        pdf_out = output_dir / PDF_OUT.name
        log_out = output_dir / BUILD_LOG_NAME

    print(f"Building TeX: {tex_out}")
    build_tex(tex_out)
    if args.tex_only:
        return

    print(f"Building PDF: {pdf_out}")
    build_pdf(tex_out, pdf_out, log_out)
    print("Build complete.")


if __name__ == "__main__":
    main()
