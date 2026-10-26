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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "code"))
from deposit_paths import read_manifest, safe_path, walk_files

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
MANIFEST = ROOT / "SHA256SUMS"

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", ".lake",
    "dist", "build", "htmlcov", "dev_rips", "rt", "target",
    "b", "scratch",
    "_support", "evidence", "reconstruction_v1",
}
EXCLUDED_NAMES = {"SHA256SUMS", ".coverage", ".env", "DEPOSIT_CHECKLIST.md", ".gitkeep", "density_lift.zip.sha256"}
EXCLUDED_SUFFIXES = {".zip", ".pyc", ".pyo", ".tmp", ".log", ".aux", ".toc", ".out"}

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
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/replay_lean_axiom_census.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=180, check=False,
    )
    return [] if result.returncode == 0 else [result.stdout + result.stderr]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify paper deposit package.")
    parser.add_argument("--lean", action="store_true", help="Run Lean verification and axiom audit.")
    parser.add_argument("--test", action="append", default=[], help="Named test file; repeat as needed.")
    parser.add_argument("--run-tests", action="store_true", help="Run all pytest test files in code/tests/.")
    parser.add_argument("--require-archive", action="store_true", help="Require the sealed archive and sidecar.")
    parser.add_argument("--archive", type=Path, help="Verify an explicit ZIP and its sidecar.")
    args = parser.parse_args()

    all_errors: list[str] = []
    from tools.validate_release import validate_metadata
    all_errors.extend(validate_metadata(ROOT))
    if args.require_archive or args.archive is not None:
        from tools.rebuild_release import validate
        archive_errors = validate(ROOT, args.archive)
        all_errors.extend(archive_errors)
        if not archive_errors:
            print("OK: complete archive, sidecar and member bytes verified.")
    else:
        print("Archive verification NOT performed; use --require-archive.")

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

    if args.run_tests:
        test_errors = check_tests([])
        all_errors.extend(test_errors)
        for error in test_errors:
            print(f"FAIL: {error}")
        if not test_errors:
            print("OK: all test files passed.")

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
        print(f"\nVerification FAILED with {len(all_errors)} errors.")
        return 1

    print("\nVerification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
