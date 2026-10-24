"""Build the checked Lean report and the TeX/PDF release forms for LGGR IV."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEM = "lggr_iv_finite_presentations_completion_relative"
MARKDOWN = ROOT / f"{STEM}.md"
PACKAGED_PREAMBLE = ROOT / "scripts" / "obstruction-preamble.tex"
CANONICAL_PREAMBLE_REL = (
    Path("coda_university")
    / "_kits"
    / "obstruction_paper_kit"
    / "obstruction_preamble.tex"
)
CANONICAL_PREAMBLE_SHA256 = (
    "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
)
TEX = ROOT / f"{STEM}.tex"
PDF = ROOT / f"{STEM}.pdf"
LEAN_DIR = ROOT / "lean4"
AXIOM_REPORT = LEAN_DIR / "axiom_report.txt"
LEAN_TARGET = "LGGR4"
EXPECTED_AXIOM_REPORTS = 11
AXIOM_WHITELIST = frozenset({"Quot.sound", "propext", "Classical.choice"})
PDFLATEX_RUNS = 2
SOURCE_DATE_EPOCH = "1789732800"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def executable(name: str, fallback: Path) -> str:
    found = shutil.which(name)
    if found:
        return found
    if fallback.is_file():
        return str(fallback)
    raise SystemExit(f"BLOCKED: {name} was not found")


def run_capture(
    command: list[str], cwd: Path, env: dict[str, str] | None = None
) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode:
        raise SystemExit(f"FAILED: {' '.join(command)}\n{output.strip()[-6000:]}")
    return output


def normalized_output(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    return "\n".join(line.rstrip() for line in lines).strip() + "\n"


def locate_canonical_preamble() -> Path | None:
    for base in (ROOT, *ROOT.parents):
        candidate = base / CANONICAL_PREAMBLE_REL
        if candidate.is_file():
            return candidate
    return None


def validated_preamble() -> Path:
    if sha256_of(PACKAGED_PREAMBLE) != CANONICAL_PREAMBLE_SHA256:
        raise SystemExit("BLOCKED: packaged obstruction preamble hash mismatch")
    canonical = locate_canonical_preamble()
    if canonical is None:
        return PACKAGED_PREAMBLE
    if sha256_of(canonical) != CANONICAL_PREAMBLE_SHA256:
        raise SystemExit("BLOCKED: live canonical obstruction preamble hash mismatch")
    if canonical.read_bytes() != PACKAGED_PREAMBLE.read_bytes():
        raise SystemExit("BLOCKED: packaged preamble differs from the live canonical kit")
    return canonical


def pandoc_command(pandoc: str, preamble: Path, date: str = "2026-10-15") -> list[str]:
    return [
        pandoc,
        "--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex+pipe_tables",
        f"--include-in-header={preamble}",
        "--highlight-style=tango",
        "-V", "colorlinks=true",
        "-V", "linkcolor=oblink",
        "-V", "urlcolor=oblink",
        "-V", "citecolor=oblink",
        "-V", "fontsize=11pt",
        "-M", f"date={date}",
        "-s",
        "-o", str(TEX),
        str(MARKDOWN),
    ]


def pdflatex_command(pdflatex: str, output_dir: Path) -> list[str]:
    return [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={output_dir}",
        TEX.name,
    ]


def render_axiom_report(lean_version: str, census: str, date: str = "2026-10-15") -> str:
    return (
        "Paper IV Lean axiom report\n"
        f"Date: {date}\n"
        f"Toolchain: {lean_version.strip()}\n"
        f"Build target: {LEAN_TARGET}\n"
        "Build result: success\n"
        "Census command: lake env lean check_axioms.lean\n\n"
        f"{normalized_output(census)}"
    )


def validate_axiom_census(census: str) -> None:
    reports = [line for line in census.splitlines() if "axioms" in line]
    if len(reports) != EXPECTED_AXIOM_REPORTS:
        raise SystemExit(
            f"BLOCKED: expected {EXPECTED_AXIOM_REPORTS} axiom reports, got {len(reports)}"
        )
    unexpected: list[str] = []
    for line in reports:
        if "does not depend on any axioms" in line:
            continue
        _, _, tail = line.partition("depends on axioms: ")
        names = [name.strip(" []") for name in re.split(r"[,\s]+", tail) if name.strip(" []")]
        unexpected.extend(name for name in names if name not in AXIOM_WHITELIST)
    if unexpected:
        raise SystemExit(f"BLOCKED: axioms outside whitelist: {sorted(set(unexpected))}")


def build_lean_report() -> None:
    for source in LEAN_DIR.glob("*.lean"):
        if re.search(r"\b(?:sorry|admit)\b", source.read_text(encoding="utf-8")):
            raise SystemExit(f"BLOCKED: placeholder proof token in {source.name}")
    with tempfile.TemporaryDirectory(prefix="lggr4-lean-build-") as raw:
        work = Path(raw)
        for source in LEAN_DIR.iterdir():
            if source.is_file() and source.name != AXIOM_REPORT.name:
                shutil.copy2(source, work / source.name)
        lean_version = normalized_output(
            run_capture(["lake", "env", "lean", "--version"], work)
        ).strip()
        lean_version = re.sub(
            r",\s*[a-zA-Z0-9_]+-(?:w64-windows-gnu|unknown-linux-gnu|apple-darwin)[^,]*,",
            ",",
            lean_version,
        )
        run_capture(["lake", "build", LEAN_TARGET], work)
        census = run_capture(["lake", "env", "lean", "check_axioms.lean"], work)
    validate_axiom_census(census)
    m_text = MARKDOWN.read_text(encoding="utf-8")
    m_date = re.search(r"\*{1,2}Date:\*{1,2}\s*(\d{4}-\d{2}-\d{2})", m_text)
    paper_date = m_date.group(1) if m_date else "2026-10-15"
    AXIOM_REPORT.write_text(
        render_axiom_report(lean_version, census, date=paper_date), encoding="utf-8", newline="\n"
    )


def build_tex() -> None:
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    pandoc = executable("pandoc", local / "Pandoc" / "pandoc.exe")
    m_text = MARKDOWN.read_text(encoding="utf-8")
    m_date = re.search(r"\*{1,2}Date:\*{1,2}\s*(\d{4}-\d{2}-\d{2})", m_text)
    paper_date = m_date.group(1) if m_date else "2026-10-15"
    run_capture(pandoc_command(pandoc, validated_preamble(), date=paper_date), ROOT)
    text = TEX.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
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
    lines.insert(documentclass_end + 1, "\\pdftrailerid{}")
    TEX.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_pdf() -> None:
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    pdflatex = executable(
        "pdflatex",
        local / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64" / "pdflatex.exe",
    )
    env = dict(os.environ)
    env.update({"SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH, "FORCE_SOURCE_DATE": "1"})
    with tempfile.TemporaryDirectory(prefix="lggr4-paper-") as raw:
        work = Path(raw)
        shutil.copy2(TEX, work / TEX.name)
        if (ROOT / "public_export").is_dir():
            shutil.copytree(ROOT / "public_export", work / "public_export")
        for _ in range(PDFLATEX_RUNS):
            run_capture(pdflatex_command(pdflatex, work), work, env)
        shutil.copy2(work / PDF.name, PDF)


def main() -> None:
    build_lean_report()
    build_tex()
    build_pdf()
    print(f"built {AXIOM_REPORT.relative_to(ROOT)}, {TEX.name}, and {PDF.name}")


if __name__ == "__main__":
    main()
