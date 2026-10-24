"""Build matching TeX and PDF artifacts from the canonical Markdown."""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = ROOT / "lggr_iii_epk_gtla_overlay.md"
PREAMBLE = ROOT / "scripts" / "obstruction-preamble.tex"
TEX = ROOT / "lggr_iii_epk_gtla_overlay.tex"
PDF = ROOT / "lggr_iii_epk_gtla_overlay.pdf"

TITLE = "Local Green, Global Red III"
SUBTITLE = "A finite evaluator overlay across six system roles"
AUTHOR = "Jeremy H. Carroll"
DATE = "2026-10-15"
SOURCE_EPOCH = "1791633600"
CANONICAL_PREAMBLE_SHA256 = (
    "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
)
MAX_PDFLATEX_PASSES = 4
VERSION = "1.5.2"
LICENSE = "CC-BY-4.0"
PDF_SUBJECT = f"Version: {VERSION}; Date: {DATE}; License: {LICENSE}"

WINDOWS_FALLBACKS = {
    "pandoc": Path.home() / "AppData/Local/Pandoc/pandoc.exe",
    "pdflatex": (
        Path.home()
        / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"
    ),
}


def need(name: str) -> str:
    discovered = shutil.which(name)
    if discovered:
        return discovered
    fallback = WINDOWS_FALLBACKS.get(name)
    if fallback and fallback.is_file():
        return str(fallback)
    raise SystemExit(f"BLOCKED: {name} was not found")


def version(name: str) -> str:
    process = subprocess.run(
        [need(name), "--version"], capture_output=True, check=False, timeout=120
    )
    lines = process.stdout.decode("utf-8", errors="replace").splitlines()
    return lines[0].strip() if lines else f"{name} version unavailable"


def source_body() -> str:
    text = MARKDOWN.read_text(encoding="utf-8")
    marker = "## Abstract"
    if marker not in text:
        raise SystemExit("BLOCKED: manuscript has no abstract")
    return text[text.index(marker) :]


def build_tex(destination: Path) -> Path:
    metadata = (
        "---\n"
        f"title-meta: '{TITLE}'\n"
        f"author-meta: '{AUTHOR}'\n"
        f"date-meta: '{DATE}'\n"
        f"subject: '{PDF_SUBJECT}'\n"
        "keywords:\n"
        "- finite evaluator defect\n"
        "- boundary bijection\n"
        "- quotient descent\n"
        "documentclass: article\n"
        "fontsize: 11pt\n"
        "colorlinks: true\n"
        "---\n\n"
    )
    centered_header = (
        "\\begin{center}\n"
        f"{{\\LARGE\\bfseries {TITLE}\\par}}\n"
        "\\vskip 0.4em\n"
        f"{{\\large\\itshape {SUBTITLE}\\par}}\n"
        "\\vskip 0.8em\n"
        "{\\normalsize\n"
        f"\\textbf{{Author:}} {AUTHOR}\\par\n"
        "\\vskip 0.2em\n"
        f"\\textbf{{Date:}} {DATE}\\par\n"
        "\\vskip 0.2em\n"
        f"\\textbf{{Version:}} {VERSION}\\par\n"
        "\\vskip 0.2em\n"
        f"\\textbf{{License:}} {LICENSE}\\par\n"
        "}\n"
        "\\end{center}\n"
        "\\vskip 1.5em\n\n"
    )
    with tempfile.TemporaryDirectory(prefix="lggr3-pandoc-") as temp:
        source = Path(temp) / "paper.md"
        source.write_text(metadata + centered_header + source_body(), encoding="utf-8", newline="\n")
        process = subprocess.run(
            [
                need("pandoc"),
                str(source),
                "--from",
                "markdown+tex_math_dollars+pipe_tables+raw_tex"
                "+backtick_code_blocks+fenced_code_attributes",
                "--to",
                "latex",
                "--standalone",
                "--pdf-engine",
                "pdflatex",
                "--include-in-header",
                str(PREAMBLE),
                "--highlight-style",
                "kate",
                "--wrap",
                "preserve",
                "-V",
                "geometry:margin=1in",
                "-V",
                "linkcolor=RoyalBlue",
                "-o",
                str(destination),
            ],
            cwd=ROOT,
            capture_output=True,
            check=False,
            timeout=1800,
        )
    if process.returncode:
        raise SystemExit(
            "pandoc failed:\n"
            + process.stdout.decode("utf-8", errors="replace")
            + process.stderr.decode("utf-8", errors="replace")
        )
    generated = destination.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    document_class = re.compile(
        rb"(\\documentclass(?:\[[^]]*\])?\{article\}\n)", re.DOTALL
    )
    generated, count = document_class.subn(
        rb"\1\\pdftrailerid{}\n", generated, count=1
    )
    if count != 1:
        raise SystemExit("BLOCKED: could not pin the pdfLaTeX trailer identifier")
    source_hash = hashlib.sha256(MARKDOWN.read_bytes()).hexdigest()
    destination.write_bytes(
        f"% markdown-sha256: {source_hash}\n".encode("ascii") + generated
    )
    return destination


_MISSING = re.compile(r"^Missing character: There is no (.+?) in font (.+?)!?$", re.M)
_OVERFULL = re.compile(
    r"^Overfull \\hbox \(([0-9.]+)pt too wide\)(?: in paragraph at lines (\S+))?",
    re.M,
)
OVERFULL_LIMIT_PT = 0.5


def audit_log(log: str) -> None:
    missing = _MISSING.findall(log)
    overfull = [
        (float(width), lines or "?")
        for width, lines in _OVERFULL.findall(log)
        if float(width) > OVERFULL_LIMIT_PT
    ]
    if missing or overfull:
        details = []
        if missing:
            details.append(f"{len(missing)} missing character warning(s)")
        if overfull:
            worst = max(width for width, _ in overfull)
            details.append(
                f"{len(overfull)} overfull box(es), worst {worst:.2f} pt"
            )
        raise SystemExit("PDF layout audit failed: " + "; ".join(details))


def build_pdf(tex: Path, destination: Path) -> Path:
    environment = {
        **os.environ,
        "SOURCE_DATE_EPOCH": SOURCE_EPOCH,
        "FORCE_SOURCE_DATE": "1",
    }
    if digest(PREAMBLE) != CANONICAL_PREAMBLE_SHA256:
        raise SystemExit("BLOCKED: bundled preamble differs from the live canonical kit")
    with tempfile.TemporaryDirectory(prefix="lggr3-pdflatex-") as temp:
        directory = Path(temp)
        work = directory / tex.name
        aux_path = directory / f"{work.stem}.aux"
        shutil.copy2(tex, work)
        prev_aux: bytes | None = None
        converged = False
        final_log = ""
        for pass_number in range(1, MAX_PDFLATEX_PASSES + 1):
            process = subprocess.run(
                [
                    need("pdflatex"),
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    work.name,
                ],
                cwd=directory,
                capture_output=True,
                check=False,
                timeout=1800,
                env=environment,
            )
            log_path = directory / f"{work.stem}.log"
            log = (
                log_path.read_text(encoding="utf-8", errors="replace")
                if log_path.is_file()
                else process.stdout.decode("utf-8", errors="replace")
            )
            if process.returncode:
                raise SystemExit(
                    f"pdfLaTeX pass {pass_number} failed:\n"
                    + "\n".join(log.splitlines()[-50:])
                )
            audit_log(log)
            final_log = log
            cur_aux = aux_path.read_bytes() if aux_path.is_file() else b""
            has_rerun_warning = "Rerun to get cross-references right" in log
            if pass_number >= 2 and cur_aux == prev_aux and not has_rerun_warning:
                converged = True
                break
            prev_aux = cur_aux

        if not converged:
            raise SystemExit(
                f"BLOCKED: pdfLaTeX did not converge within {MAX_PDFLATEX_PASSES} passes"
            )
        audit_log(final_log)
        shutil.copy2(directory / f"{work.stem}.pdf", destination)
    return destination


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(tex: Path, pdf: Path, tex_only: bool = False) -> None:
    build_tex(tex)
    if not tex_only:
        build_pdf(tex, pdf)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex-only", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    for required in (MARKDOWN, PREAMBLE):
        if not required.is_file():
            raise SystemExit(f"BLOCKED: missing {required}")

    print(f"source: {MARKDOWN.name} ({digest(MARKDOWN)[:16]})")
    if digest(PREAMBLE) != CANONICAL_PREAMBLE_SHA256:
        raise SystemExit("BLOCKED: bundled preamble differs from the live canonical kit")
    print(f"toolchain: {version('pandoc')} | {version('pdflatex')}")

    if args.check:
        with tempfile.TemporaryDirectory(prefix="lggr3-artifacts-") as temp:
            probe_tex = Path(temp) / TEX.name
            probe_pdf = Path(temp) / PDF.name
            build(probe_tex, probe_pdf)
            tex_same = TEX.is_file() and filecmp.cmp(probe_tex, TEX, shallow=False)
            pdf_same = PDF.is_file() and filecmp.cmp(probe_pdf, PDF, shallow=False)
            print(f"tex match: {tex_same}; pdf match: {pdf_same}")
            return 0 if tex_same and pdf_same else 1

    build(TEX, PDF, tex_only=args.tex_only)
    print(f"tex: {TEX.name} ({digest(TEX)[:16]})")
    if not args.tex_only:
        print(f"pdf: {PDF.name} ({digest(PDF)[:16]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
