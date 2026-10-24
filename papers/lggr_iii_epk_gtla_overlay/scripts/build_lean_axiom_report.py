#!/usr/bin/env python3
"""Rebuild the deterministic theorem-level Lean axiom report."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "lean4"
REPORT = LEAN_ROOT / "AXIOM_REPORT.txt"
PROJECT_FILES = (
    "Core.lean",
    "check_axioms.lean",
    "lake-manifest.json",
    "lakefile.lean",
    "lean-toolchain",
)
EXPECTED_REPORTS = 12
REPORT_LINE = re.compile(
    r"^'LGGR3\.[^']+' (?:does not depend on any axioms|depends on axioms: .+)$"
)


def render(census_output: str) -> str:
    lines = [line for line in census_output.splitlines() if REPORT_LINE.fullmatch(line)]
    if len(lines) != EXPECTED_REPORTS:
        raise SystemExit(
            f"BLOCKED: expected {EXPECTED_REPORTS} theorem reports, found {len(lines)}"
        )
    toolchain = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    return (
        "Local Green, Global Red III — theorem-level Lean axiom report\n"
        "Date: 2026-10-15\n"
        f"Toolchain: {toolchain}\n"
        "Default build target: LGGR3 (Core.lean)\n"
        "Census command: lake env lean check_axioms.lean\n"
        f"Theorem reports: {EXPECTED_REPORTS}\n\n"
        + "\n".join(lines)
        + "\n"
    )


def current_report() -> str:
    with tempfile.TemporaryDirectory(prefix="lggr3-axioms-") as temp:
        project = Path(temp) / "lean4"
        project.mkdir()
        for name in PROJECT_FILES:
            shutil.copy2(LEAN_ROOT / name, project / name)
        build = subprocess.run(
            ["lake", "build"], cwd=project, capture_output=True, text=True, check=False
        )
        if build.returncode:
            raise SystemExit("lake build failed:\n" + build.stdout + build.stderr)
        census = subprocess.run(
            ["lake", "env", "lean", "check_axioms.lean"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        if census.returncode:
            raise SystemExit("axiom census failed:\n" + census.stdout + census.stderr)
        return render(census.stdout + census.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fresh = current_report()
    if args.check:
        if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != fresh:
            print("FAIL: lean4/AXIOM_REPORT.txt is stale or missing")
            return 1
        print(f"OK: {EXPECTED_REPORTS} current theorem-level axiom reports match")
        return 0
    REPORT.write_text(fresh, encoding="utf-8", newline="\n")
    print(f"wrote {REPORT.relative_to(ROOT).as_posix()}: {EXPECTED_REPORTS} reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
