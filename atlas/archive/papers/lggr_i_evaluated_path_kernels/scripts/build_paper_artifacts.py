"""Build Paper I with the hash-bound shared pdfLaTeX publication kit."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PAPER_STEM = "lggr_i_evaluated_path_kernels"
RELEASE_DATE = "2026-10-15"
PAPER_MD = PACKAGE_ROOT / f"{PAPER_STEM}.md"
BUNDLED_PREAMBLE = PACKAGE_ROOT / "scripts" / "obstruction-preamble.tex"
TEX_OUT = PACKAGE_ROOT / f"{PAPER_STEM}.tex"
PDF_OUT = PACKAGE_ROOT / f"{PAPER_STEM}.pdf"
BUILD_LOG_NAME = f"{PAPER_STEM}-{RELEASE_DATE}-pdflatex.log"
CANONICAL_PREAMBLE_REL = (
    Path("coda_university")
    / "_kits"
    / "obstruction_paper_kit"
    / "obstruction_preamble.tex"
)
CANONICAL_PREAMBLE_SHA256 = (
    "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
)
PDFLATEX_RUNS = 2

# Noon UTC preserves the public release date in UTC and North American time
# zones and fixes TeX's CreationDate/ModDate inputs.
SOURCE_DATE_EPOCH = "1789473600"

PDF_METADATA = r"""\hypersetup{
  pdftitle={Local Green, Global Red I: Evaluated Path Kernels for Composed Agent Reliability},
  pdfauthor={Jeremy H. Carroll},
  pdfsubject={Version 1.2.4; 2026-10-15; preprint; Zenodo lineage DOI 10.5281/zenodo.20675803},
  pdfkeywords={evaluated path kernels, evaluator gluing defect, finite sample identities, Lean 4, reproducible research, composed agents, AI reliability}
}"""

BUILD_DIAGNOSTIC_MARKERS = (
    "Missing character:",
    "Unable to load picture or PDF file",
    "ignored error:",
    "Overfull \\hbox",
    "Overfull \\vbox",
    "Float too large for page",
    "Dimension too large",
)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate_canonical_preamble() -> Path | None:
    for ancestor in (PACKAGE_ROOT, *PACKAGE_ROOT.parents):
        candidate = ancestor / CANONICAL_PREAMBLE_REL
        if candidate.is_file():
            return candidate
    return None


def validated_preamble() -> Path:
    if not BUNDLED_PREAMBLE.is_file():
        raise SystemExit("BLOCKED: bundled obstruction preamble is missing")
    bundled_hash = sha256_of(BUNDLED_PREAMBLE)
    if bundled_hash != CANONICAL_PREAMBLE_SHA256:
        raise SystemExit(
            "BLOCKED: bundled obstruction preamble hash mismatch "
            f"(expected {CANONICAL_PREAMBLE_SHA256}, got {bundled_hash})"
        )

    canonical = locate_canonical_preamble()
    if canonical is None:
        # The released archive is intentionally self-contained.
        return BUNDLED_PREAMBLE
    canonical_hash = sha256_of(canonical)
    if canonical_hash != CANONICAL_PREAMBLE_SHA256:
        raise SystemExit(
            "BLOCKED: live canonical obstruction preamble hash mismatch "
            f"(expected {CANONICAL_PREAMBLE_SHA256}, got {canonical_hash})"
        )
    if canonical.read_bytes() != BUNDLED_PREAMBLE.read_bytes():
        raise SystemExit(
            "BLOCKED: bundled preamble differs from the live canonical kit"
        )
    return canonical


def need(tool: str) -> str:
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
    command = [
        pandoc,
        "--from",
        (
            "markdown+tex_math_dollars+tex_math_single_backslash+pipe_tables"
            "+raw_tex+backtick_code_blocks+fenced_code_attributes"
        ),
        "--include-in-header",
        str(validated_preamble()),
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
    output = run.stdout.decode("utf-8", errors="replace")
    errors = run.stderr.decode("utf-8", errors="replace")
    if run.returncode:
        raise SystemExit(f"pandoc failed:\n{output}{errors}")

    text = destination.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    documentclass_start = next(
        (index for index, line in enumerate(lines) if line.startswith("\\documentclass")),
        None,
    )
    if documentclass_start is None:
        raise SystemExit("BLOCKED: Pandoc output has no document class")
    documentclass_end = next(
        (
            index
            for index in range(documentclass_start, len(lines))
            if lines[index].rstrip().endswith("{article}")
        ),
        None,
    )
    if documentclass_end is None:
        raise SystemExit("BLOCKED: Pandoc output has an unterminated document class")
    # MiKTeX otherwise seeds the trailer ID on each invocation.
    lines.insert(documentclass_end + 1, "\\pdftrailerid{}")

    begin_document = next(
        (index for index, line in enumerate(lines) if line == "\\begin{document}"),
        None,
    )
    if begin_document is None:
        raise SystemExit("BLOCKED: Pandoc output has no document body")
    lines.insert(begin_document, PDF_METADATA)
    destination.write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )
    return destination


def build_pdf(tex: Path, destination: Path, log_destination: Path) -> Path:
    pdflatex = need("pdflatex")
    environment = dict(os.environ)
    environment["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    environment["FORCE_SOURCE_DATE"] = "1"

    with tempfile.TemporaryDirectory(prefix="lggr-i-pdf-") as raw_tmp:
        temporary = Path(raw_tmp)
        working_tex = temporary / tex.name
        shutil.copyfile(tex, working_tex)
        shutil.copytree(PACKAGE_ROOT / "public_export", temporary / "public_export")

        final_log = ""
        for pass_number in range(1, PDFLATEX_RUNS + 1):
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
            log = temporary / f"{working_tex.stem}.log"
            if log.is_file():
                final_log = log.read_text(encoding="utf-8", errors="replace")
            if run.returncode:
                tail = "\n".join(final_log.splitlines()[-50:])
                raise SystemExit(
                    f"pdflatex pass {pass_number} failed:\n{tail}\n"
                    f"{transcript[-2000:]}"
                )
            observed = [
                marker
                for marker in BUILD_DIAGNOSTIC_MARKERS
                if marker in transcript or marker in final_log
            ]
            if observed:
                raise SystemExit(
                    f"pdflatex pass {pass_number} emitted release-blocking "
                    "diagnostics: " + ", ".join(observed)
                )

        engine_banner = next(
            (line for line in final_log.splitlines() if line.startswith("This is ")),
            "",
        )
        if not engine_banner.startswith("This is pdfTeX"):
            raise SystemExit(
                "BLOCKED: build log engine banner is not pdfTeX: "
                f"{engine_banner or '(missing)'}"
            )

        shutil.copyfile(temporary / f"{tex.stem}.pdf", destination)
        log_destination.parent.mkdir(parents=True, exist_ok=True)
        log_destination.write_text(final_log, encoding="utf-8", newline="\n")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex-only", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="write TeX, PDF, and the final pdfLaTeX log to this directory",
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
    print(
        f"Build complete: {PDFLATEX_RUNS} pdfLaTeX passes; "
        f"layout log {log_out}"
    )


if __name__ == "__main__":
    main()
