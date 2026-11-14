#!/usr/bin/env python3
"""One-command verifier for the research paper deposit.

Deterministic, two-way verification:
1. Every file listed in SHA256SUMS exists and matches its recorded hash.
2. Sweep: no unrecorded non-excluded file is present in the deposit tree.
3. Fail-closed symlink rejection: rejects any unauthorized symlink.
4. Structural artifacts are present and non-empty.
5. Optional/Default named test files pass (--test).
6. Optional (--lean): lake build succeeds and axiom census stays within whitelist.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "code"))
from deposit_paths import read_manifest, safe_path, walk_files

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS"

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", ".lake",
    "dist", "build", "htmlcov", "dev_rips", "rt", "target",
    "b", "scratch",
    "_support", "evidence", "reconstruction_v1",
}
EXCLUDED_NAMES = {"SHA256SUMS", ".coverage", ".env", "DEPOSIT_CHECKLIST.md", ".gitkeep"}
EXCLUDED_SUFFIXES = {".zip", ".pyc", ".pyo", ".tmp", ".log"}

REQUIRED_PATTERNS = (
    "*_monograph.md",
    "*_change_log.md",
    "README.md",
    "LICENSE",
    "LICENSE-CODE",
    "MANIFEST.sha256",
    "pyproject.toml",
    "zenodo_metadata.json",
    "docs/descriptions.md",
    "docs/references.md",
    "code/deposit_paths.py",
)

AXIOM_WHITELIST = frozenset({"Quot.sound", "propext", "Classical.choice", "choice"})


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        excluded_names = set(EXCLUDED_NAMES)
        if manifest_path.name == "MANIFEST.sha256":
            excluded_names.add("MANIFEST.sha256")
        expected_files = walk_files(ROOT, EXCLUDED_DIRS, excluded_names, EXCLUDED_SUFFIXES)
        entries = read_manifest(ROOT, manifest_path)
        recorded = {relative for relative, _ in entries}
        for relative, digest in entries:
            path = safe_path(ROOT, relative)
            if not path.is_file():
                errors.append(f"Recorded file missing: {relative}")
            elif sha256_of(path) != digest:
                errors.append(f"Hash mismatch: {relative}")
        expected = {path.relative_to(ROOT).as_posix() for path in expected_files}
        for relative in sorted(expected - recorded):
            errors.append(f"Unrecorded deposit file: {relative}")
        for relative in sorted(recorded - expected):
            errors.append(f"Excluded file listed in manifest: {relative}")

        # Check required structural files/patterns
        for pattern in REQUIRED_PATTERNS:
            if "/" in pattern:
                target = ROOT / pattern
                if not target.is_file() or not target.stat().st_size:
                    errors.append(f"Required file missing or empty: {pattern}")
            else:
                matches = list(ROOT.glob(pattern))
                if pattern == "*_monograph.md" and not matches:
                    matches = [
                        p for p in ROOT.glob("*.md")
                        if p.name.lower() not in ("readme.md", "review_scope.md")
                        and not p.name.endswith(("_change_log.md", "_claim_ledger.md", "_supplement.md", "supplement.md"))
                    ]
                if pattern == "*_change_log.md" and not matches:
                    matches = list(ROOT.glob("paper_change_log.md"))
                if not matches or not any(m.stat().st_size > 0 for m in matches):
                    errors.append(f"Required file pattern missing or empty: {pattern}")
    except (OSError, ValueError) as error:
        errors.append(str(error))
    return errors


def check_tests(targets: list[str]) -> list[str]:
    if not targets:
        tests_dir = ROOT / "code" / "tests"
        if tests_dir.is_dir():
            targets = [p.relative_to(ROOT).as_posix() for p in tests_dir.glob("test_*.py")]
    if not targets:
        return ["No test files found in code/tests/"]
    errors: list[str] = []
    for target in targets:
        try:
            path = safe_path(ROOT, target)
            if not target.startswith("code/tests/test_") or path.suffix != ".py" or not path.is_file():
                raise ValueError(f"Invalid test target: {target}")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", target, "-q"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
            if result.returncode:
                errors.append(f"Pytest failure in {target}:\n{result.stdout}\n{result.stderr}")
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            errors.append(str(error))
    return errors


def check_lean() -> list[str]:
    lean_dir = ROOT / "lean4"
    if not (lean_dir / "lakefile.lean").is_file() and not (lean_dir / "lakefile.toml").is_file():
        return ["Missing lean4/lakefile.lean or lakefile.toml"]
    errors: list[str] = []
    build_result = subprocess.run(
        ["lake", "build"], cwd=str(lean_dir), capture_output=True, text=True, encoding="utf-8", timeout=60, check=False
    )
    if build_result.returncode != 0:
        errors.append(f"lake build failed:\n{build_result.stdout}\n{build_result.stderr}")
        return errors

    census_lean = lean_dir / "Census.lean"
    root_lean = lean_dir / "Core.lean"
    target_lean = census_lean if census_lean.is_file() else (root_lean if root_lean.is_file() else None)
    if target_lean is not None:
        census_result = subprocess.run(
            ["lake", "env", "lean", target_lean.name],
            cwd=str(lean_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        if census_result.returncode != 0:
            errors.append(f"axiom census failed:\n{census_result.stdout}\n{census_result.stderr}")
            return errors

        for line in census_result.stdout.splitlines():
            line = line.strip()
            if "depends on axioms:" in line:
                axioms_part = line.split("depends on axioms:")[1].strip()
                axioms_part = axioms_part.strip("[]")
                for ax in axioms_part.split(","):
                    ax_name = ax.strip()
                    if ax_name and ax_name not in AXIOM_WHITELIST:
                        errors.append(f"Unauthorized axiom dependency: {ax_name} in '{line}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify paper deposit package.")
    parser.add_argument("--lean", action="store_true", help="Run Lean verification and axiom audit.")
    parser.add_argument("--test", action="append", default=[], help="Named test file; repeat as needed.")
    args = parser.parse_args()

    all_errors: list[str] = []

    witness = subprocess.run([sys.executable, str(ROOT / "code/verify_witnesses.py")],
                             cwd=ROOT, capture_output=True, text=True, timeout=30, check=False)
    if witness.returncode:
        all_errors.append("Primal/dual certificate check failed: " + witness.stdout + witness.stderr)
    else:
        print("OK: exact finite primal/dual certificates passed.")

    # A byte-consistent archive may still contain a stale conversion receipt.
    # Check the canonical equation and render bindings without rebuilding them.
    try:
        spine_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/paper_spine.py"), "verify"],
            cwd=ROOT, capture_output=True, text=True, timeout=180, check=False)
        if spine_result.returncode:
            all_errors.append("Canonical spine/render verification failed: " + spine_result.stdout + spine_result.stderr)
        else:
            print("OK: canonical spine and MD/TeX/text/PDF render bindings passed.")
    except (OSError, subprocess.TimeoutExpired) as error:
        all_errors.append(str(error))

    manifest_target = MANIFEST
    if not manifest_target.is_file() and (ROOT / "MANIFEST.sha256").is_file():
        manifest_target = ROOT / "MANIFEST.sha256"

    manifest_errors = check_manifest(manifest_target)
    all_errors.extend(manifest_errors)
    if manifest_errors:
        print(f"FAIL: Manifest checks failed ({len(manifest_errors)} issues):")
        for err in manifest_errors:
            print(f"  - {err}")
    else:
        print("OK: Manifest and two-way sweep checks passed.")

    if args.test:
        test_errors = check_tests(args.test)
        all_errors.extend(test_errors)
        for error in test_errors:
            print(f"FAIL: {error}")
        if not test_errors:
            print("OK: selected test files passed.")

    if args.lean:
        try:
            lean_errors = check_lean()
        except (OSError, subprocess.TimeoutExpired) as error:
            lean_errors = [f"Lean verification did not complete: {error}"]
        all_errors.extend(lean_errors)
        if lean_errors:
            print("FAIL: Lean checks failed.")
            for err in lean_errors:
                print(f"  - {err}")
        else:
            print("OK: Lean proofs and axiom census verified.")

    if all_errors:
        for error in all_errors:
            print(f"FAIL: {error}")
        print(f"\nVerification FAILED with {len(all_errors)} errors.")
        return 1

    print("\nVerification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
