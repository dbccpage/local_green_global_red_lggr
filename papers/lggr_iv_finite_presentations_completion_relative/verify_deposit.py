#!/usr/bin/env python3
"""One-command verifier for the Local Green, Global Red IV deposit.

Deterministic, two-way verification:
1. Every file listed in SHA256SUMS exists and matches its recorded hash.
2. Sweep: no extra file is present in the deposit tree that SHA256SUMS does not list.
3. Required release files are present and non-empty.
4. Python test suite passes with >= 95% branch coverage on production modules.
5. Optional (--lean): lake build succeeds and axiom census stays within whitelist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS"

IGNORED_DIR_NAMES = {
    "__pycache__", ".pytest_cache", ".lake", "b", "scratch",
    ".ipynb_checkpoints", ".mypy_cache", ".ruff_cache", ".git",
    "_support", "dev_rips", "rt",
}
IGNORED_FILE_NAMES = {"SHA256SUMS", ".coverage", "DEPOSIT_CHECKLIST.md"}
IGNORED_FILE_SUFFIXES = {".zip"}

REQUIRED_FILES = (
    "code/lggr_iv_core.py",
    "code/generate_figures.py",
    "code/tests/test_lggr_iv_core.py",
    "code/tests/test_derived_limits.py",
    "code/tests/test_rational_duality.py",
    "code/tests/test_figures.py",
    "code/tests/test_notebook.py",
    "jupyter_notebooks/001_finite_presentations.ipynb",
    "lggr_iv_finite_presentations_completion_relative.md",
    "lggr_iv_finite_presentations_completion_relative.tex",
    "lggr_iv_finite_presentations_completion_relative.pdf",
    "lggr_iv_finite_presentations_completion_relative_claim_ledger.md",
    "lggr_iv_finite_presentations_completion_relative_change_log.md",
    "public_export/figure_1_refinement_tower_and_completion.png",
    "public_export/figure_1_refinement_tower_and_completion.pdf",
    "docs/descriptions.md",
    "docs/keywords.md",
    "docs/lean_claim_map.md",
    "docs/nonclaims.md",
    "docs/quick_start.md",
    "docs/references.md",
    "lean4/core.lean",
    "lean4/lakefile.lean",
    "lean4/lake-manifest.json",
    "lean4/lean-toolchain",
    "lean4/check_axioms.lean",
    "lean4/axiom_report.txt",
    "LICENSE",
    "LICENSE-CODE",
    "MANIFEST.sha256",
    "pyproject.toml",
    "README.md",
    "scripts/build_deposit_zip.py",
    "scripts/build_paper_artifacts.py",
    "scripts/obstruction-preamble.tex",
    "scripts/regen_sha256sums.py",
    "verify_deposit.py",
)

AXIOM_WHITELIST = frozenset({"Quot.sound", "propext", "Classical.choice"})


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest(manifest_path: Path) -> list[str]:
    if not manifest_path.is_file():
        return [f"Missing manifest file: {manifest_path}"]
    errors: list[str] = []
    recorded_files: set[Path] = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(f"Malformed manifest line: {line}")
            continue
        expected_hash, rel_path = parts
        file_path = ROOT / rel_path
        if not file_path.is_file():
            errors.append(f"Recorded file missing on disk: {rel_path}")
            continue
        actual_hash = sha256_of(file_path)
        if actual_hash != expected_hash:
            errors.append(f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}")
        recorded_files.add(file_path.resolve())

    # Sweep check for unexpected files
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if any(part in IGNORED_DIR_NAMES for part in rel.parts):
            continue
        try:
            if not p.is_file() or p.is_symlink():
                continue
        except OSError:
            continue
        if p.name in IGNORED_FILE_NAMES or p.suffix in IGNORED_FILE_SUFFIXES:
            continue
        if p.resolve() not in recorded_files:
            errors.append(f"Unrecorded extra file present on disk: {rel.as_posix()}")

    return errors


def check_required_files() -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        if not path.is_file():
            errors.append(f"Required release file missing: {rel_path}")
        elif path.stat().st_size == 0:
            errors.append(f"Required release file is empty: {rel_path}")
    return errors


def run_python_suite() -> list[str]:
    errors: list[str] = []
    cov_file = ROOT / "scratch" / "cov.json"
    cov_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m", "pytest",
        "-n", "8",
        "--basetemp=scratch/pytest_tmp",
        "code/tests",
        "--cov=lggr_iv_core",
        "--cov=generate_figures",
        "--cov-branch",
        f"--cov-report=json:{cov_file}",
    ]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        errors.append(f"Python test suite failed (exit {res.returncode}):\n{res.stdout}\n{res.stderr}")
        return errors

    if not cov_file.is_file():
        errors.append("Coverage report JSON was not produced")
        return errors

    data = json.loads(cov_file.read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    percent_covered = totals.get("percent_covered", 0.0)
    if percent_covered < 95.0:
        errors.append(f"Coverage threshold failure: {percent_covered:.1f}% < 95.0%")

    return errors


def check_lean_suite() -> list[str]:
    errors: list[str] = []
    lean_dir = ROOT / "lean4"
    if not lean_dir.is_dir():
        return ["lean4 directory missing"]

    # Check for placeholder tokens
    for source in lean_dir.glob("*.lean"):
        text = source.read_text(encoding="utf-8")
        if re.search(r"\b(?:sorry|admit)\b", text):
            errors.append(f"Placeholder proof token found in {source.name}")

    ignored = shutil.ignore_patterns(".lake", "b", "__pycache__")
    with tempfile.TemporaryDirectory(prefix="lggr4-lean-") as raw_tmp:
        replay = Path(raw_tmp) / "lean4"
        shutil.copytree(lean_dir, replay, ignore=ignored)

        build_res = subprocess.run(
            ["lake", "build"],
            cwd=replay,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if build_res.returncode != 0:
            errors.append(f"lake build failed:\n{build_res.stdout}\n{build_res.stderr}")
            return errors

        census_res = subprocess.run(
            ["lake", "env", "lean", "check_axioms.lean"],
            cwd=replay,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if census_res.returncode != 0:
            errors.append(f"check_axioms.lean failed:\n{census_res.stdout}\n{census_res.stderr}")
            return errors

        reports = [l for l in census_res.stdout.splitlines() if "axioms" in l]
        if len(reports) != 11:
            errors.append(f"Expected 11 axiom reports, got {len(reports)}")

        for line in reports:
            if "does not depend on any axioms" in line:
                continue
            _, _, tail = line.partition("depends on axioms: ")
            names = [n.strip(" []") for n in re.split(r"[,\s]+", tail) if n.strip(" []")]
            for n in names:
                if n not in AXIOM_WHITELIST:
                    errors.append(f"Axiom '{n}' outside whitelist in: {line}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify LGGR IV deposit.")
    parser.add_argument("--lean", action="store_true", help="Include Lean build and axiom check.")
    args = parser.parse_args()

    print("Running LGGR IV Deposit Verification...")

    # 1. Required files check
    print("Checking required files...")
    req_errors = check_required_files()
    if req_errors:
        for err in req_errors:
            print(f"  FAIL: {err}")
        return 1
    print("  OK: All required files present and non-empty.")

    # 2. Python test suite and coverage
    print("Running Python test suite and coverage gate...")
    py_errors = run_python_suite()
    if py_errors:
        for err in py_errors:
            print(f"  FAIL: {err}")
        return 1
    print("  OK: Python tests passed with >= 95% coverage.")

    # 3. Optional Lean check
    if args.lean:
        print("Running Lean formalization build and axiom census...")
        lean_errors = check_lean_suite()
        if lean_errors:
            for err in lean_errors:
                print(f"  FAIL: {err}")
            return 1
        print("  OK: Lean formalization built clean; all axioms within whitelist.")

    # 4. Manifest consistency
    print("Verifying SHA256SUMS manifest...")
    manifest_errors = check_manifest(MANIFEST)
    if manifest_errors:
        for err in manifest_errors:
            print(f"  FAIL: {err}")
        return 1
    print("  OK: Manifest verified bit-for-bit in both directions.")

    print("\nSUCCESS: All LGGR IV verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
