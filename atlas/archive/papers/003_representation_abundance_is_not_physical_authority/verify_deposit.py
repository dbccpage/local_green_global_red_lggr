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
import os
import re
import runpy
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "code"))
from deposit_paths import read_manifest, safe_path, walk_files

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    ".lake",
    "dist",
    "build",
    "htmlcov",
    "dev_rips",
    "rt",
    "target",
    "b",
    "scratch",
    "_support",
    "evidence",
    "reconstruction_v1",
}
EXCLUDED_NAMES = {"SHA256SUMS", ".coverage", ".env", "DEPOSIT_CHECKLIST.md", ".gitkeep"}
EXCLUDED_SUFFIXES = {".zip", ".pyc", ".pyo", ".tmp"}

REQUIRED_PATTERNS = (
    "*_monograph.md",
    "*_change_log.md",
    "*_claim_ledger.md",
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

AXIOM_WHITELIST = frozenset({"Quot.sound", "propext", "Classical.choice"})
EXPECTED_DECLARATIONS = frozenset(
    {
        "observation_decision_agrees",
        "plenitude_inflation",
        "cycle_coboundary_holonomy_zero",
        "false_green_holonomy",
        "false_green_local",
        "cycle_defect_bound",
        "sharp_cycle_attains",
        "unique_acceptance_breaks",
    }
)
validate_archive = runpy.run_path(str(ROOT / "tools/rebuild_release.py"))["validate"]


def capture_release_state() -> dict[str, str]:
    """Revalidate payload, regular controls and the selected complete ZIP bytes."""
    errors = check_manifest(ROOT / "SHA256SUMS")
    errors.extend(validate_archive(ROOT))
    if errors:
        raise ValueError("Release integrity: " + "; ".join(errors))
    paths = walk_files(ROOT, EXCLUDED_DIRS, EXCLUDED_NAMES, EXCLUDED_SUFFIXES)
    paths += [ROOT / "SHA256SUMS", *ROOT.glob("*.zip")]
    state = {}
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        safe_path(ROOT, relative)
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError(f"Nonregular release control: {relative}")
        state[relative] = sha256_of(path)
    return state


def run_preserving_release(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    before = capture_release_state()
    try:
        result = subprocess.run(command, check=False, **kwargs)
    finally:
        after = capture_release_state()
        if before != after:
            raise ValueError("Release bytes or membership changed during subprocess.")
    return result


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
                        p
                        for p in ROOT.glob("*.md")
                        if p.name.lower() not in ("readme.md", "review_scope.md")
                        and not p.name.endswith(
                            (
                                "_change_log.md",
                                "_claim_ledger.md",
                                "_supplement.md",
                                "supplement.md",
                            )
                        )
                    ]
                if pattern == "*_change_log.md" and not matches:
                    matches = list(ROOT.glob("paper_change_log.md"))
                if pattern == "*_claim_ledger.md" and not matches:
                    matches = list(ROOT.glob("paper_claim_ledger.md"))
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
            if (
                not target.startswith("code/tests/test_")
                or path.suffix != ".py"
                or not path.is_file()
            ):
                raise ValueError(f"Invalid test target: {target}")
            env = dict(
                os.environ,
                PYTHONDONTWRITEBYTECODE="1",
                PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
                PYTHONPATH=str(ROOT / "code"),
            )
            with tempfile.TemporaryDirectory(prefix="representation-tests-") as temp:
                result = run_preserving_release(
                    [sys.executable, "-m", "pytest", target, "-q", "--basetemp", temp],
                    env=env,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
            if not result.returncode:
                print(result.stdout.strip())
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
    if not (lean_dir / "Census.lean").is_file():
        return ["Missing mandatory lean4/Census.lean"]

    def source_state(directory: Path) -> dict[str, str]:
        return {
            path.relative_to(directory).as_posix(): sha256_of(path)
            for path in walk_files(directory, EXCLUDED_DIRS, set(), EXCLUDED_SUFFIXES)
        }

    expected_sources = source_state(lean_dir)
    with tempfile.TemporaryDirectory(prefix="repr-lean-") as raw_temp:
        work = Path(raw_temp) / "lean4"
        shutil.copytree(lean_dir, work, ignore=shutil.ignore_patterns(".lake", "__pycache__"))
        if source_state(work) != expected_sources:
            return ["Copied Lean sources differ from release sources"]

        def run_lean(command: list[str]) -> subprocess.CompletedProcess:
            try:
                return run_preserving_release(
                    command,
                    cwd=str(work),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=60,
                )
            finally:
                if source_state(work) != expected_sources:
                    raise ValueError("Copied Lean sources changed during compilation.")

        build_result = run_lean(["lake", "build"])
        if build_result.returncode:
            return [f"lake build failed:\n{build_result.stdout}\n{build_result.stderr}"]
        census_result = run_lean(["lake", "env", "lean", "Census.lean"])
        if census_result.returncode:
            return [f"axiom census failed:\n{census_result.stdout}\n{census_result.stderr}"]

    found = set()
    for line in census_result.stdout.splitlines():
        match = re.fullmatch(
            r"'([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", line.strip()
        )
        if match is None:
            continue
        declaration, axioms = match.groups()
        if declaration in found:
            errors.append(f"Duplicate census declaration: {declaration}")
        found.add(declaration)
        for axiom in (axioms or "").split(","):
            if axiom.strip() and axiom.strip() not in AXIOM_WHITELIST:
                errors.append(f"Unauthorized axiom dependency: {axiom.strip()}")
    if found != EXPECTED_DECLARATIONS:
        errors.append(
            f"Census inventory mismatch: expected {sorted(EXPECTED_DECLARATIONS)}, got {sorted(found)}"
        )

    return errors


def main() -> int:
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.stderr.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Verify paper deposit package.")
    parser.add_argument(
        "--lean", action="store_true", help="Run Lean verification and axiom audit."
    )
    parser.add_argument(
        "--test", action="append", default=[], help="Named test file; repeat as needed."
    )
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

    try:
        capture_release_state()
    except (OSError, UnicodeError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1
    print("OK: manifests, two-way sweep and canonical ZIP passed.")

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
        except (OSError, UnicodeError, ValueError, subprocess.TimeoutExpired) as error:
            lean_errors = [f"Lean verification did not complete: {error}"]
        all_errors.extend(lean_errors)
        if lean_errors:
            print("FAIL: Lean checks failed.")
            for err in lean_errors:
                print(f"  - {err}")
        else:
            print("OK: eight supporting Lean components and their axiom census verified.")

    if all_errors:
        for error in all_errors:
            print(f"FAIL: {error}")
        print(f"\nVerification FAILED with {len(all_errors)} errors.")
        return 1

    print("\nVerification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
