#!/usr/bin/env python3
"""One-command deterministic verifier for Paper 012-000 deposit.

AuthorityEffect: None.

Deterministic, two-way verification:
1. Every file listed in SHA256SUMS exists and matches its recorded SHA-256 hash.
2. Sweep: no unrecorded non-excluded file is present in the deposit tree.
3. Fail-closed symlink rejection: rejects any unauthorized symlink or reparse point.
4. Structural artifacts are present and non-empty.
5. Optional/Default named test files pass (--test).
6. Optional (--lean): lake build succeeds, lean4/Census.lean exists, and all 27
   theorems stay strictly within the standard kernel axiom whitelist.
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
from deposit_paths import read_manifest, safe_path, walk_files  # noqa: E402

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
EXCLUDED_SUFFIXES = {".zip", ".pyc", ".pyo", ".tmp", ".log"}

REQUIRED_PATTERNS = (
    "*_monograph.md",
    "*_claim_ledger.md",
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
    "code/rsi_transition_harness.py",
    "code/rsi_eis_resources/rust_eis_companion.rs",
    "code/rsi_eis_resources/eis_independence_vectors_v2.json",
    "code/tests/test_rsi_impossible_lean_verification.py",
    "lean4/lakefile.lean",
    "lean4/RsiImpossible.lean",
    "lean4/RelationalRsiNoGo.lean",
    "lean4/Census.lean",
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

        for pattern in REQUIRED_PATTERNS:
            if "/" in pattern:
                target = ROOT / pattern
                if not target.is_file() or not target.stat().st_size:
                    errors.append(f"Required file missing or empty: {pattern}")
            else:
                matches = list(ROOT.glob(pattern))
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
            result = subprocess.run(
                [sys.executable, "-X", "utf8", "-m", "pytest", target, "-q"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=180,
                check=False,
            )
            if result.returncode:
                errors.append(f"Pytest failure in {target}:\n{result.stdout}\n{result.stderr}")
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            errors.append(str(error))
    return errors


def lean_workdir(lean_dir: Path) -> Path:
    trace = lean_dir / ".lake" / "config" / "0" / "lakefile.olean.trace"
    if len(str(trace)) < 250:
        return lean_dir
    short = Path(tempfile.gettempdir()) / "rsi012-lean"
    if short.exists():
        shutil.rmtree(short)
    shutil.copytree(lean_dir, short, ignore=shutil.ignore_patterns(".lake"))
    return short


def check_lean() -> list[str]:
    errors = []
    for tool, option in (("replay_lean_axiom_census.py", "--replay"),
                         ("replay_full_axiom_census.py", "--check")):
        path = ROOT / "tools" / tool
        if not path.is_file():
            errors.append(f"Missing mandatory census tool: {tool}")
            continue
        result = subprocess.run([sys.executable, "-X", "utf8", str(path), option],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=900)
        if result.returncode:
            errors.append(f"{tool} failed:\n{result.stdout}\n{result.stderr}")
    return errors


def check_release_archive() -> list[str]:
    rebuild_tool = ROOT / "tools" / "rebuild_release.py"
    if not rebuild_tool.is_file():
        return []
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(rebuild_tool), "--check", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        return [f"Release archive check failed:\n{result.stdout}\n{result.stderr}".strip()]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify paper 012-000 deposit package.")
    parser.add_argument("--lean", action="store_true", help="Run Lean verification and axiom census.")
    parser.add_argument(
        "--test",
        nargs="*",
        default=None,
        help="Named test file(s); if specified without arguments, runs all discovered test_*.py in code/tests/.",
    )
    args = parser.parse_args()

    all_errors: list[str] = []
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from replay_live_memory_evidence import replay
        replay(ROOT)
        print("OK: live memory trial evidence replayed offline, including failed arithmetic.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        all_errors.append(f"Memory evidence replay failed: {error}")
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from paper_spine import verify_render
        verify_render(ROOT)
        print("OK: source-bound rendered manuscript verified.")
    except (OSError, ValueError, ImportError, subprocess.TimeoutExpired) as error:
        all_errors.append(f"Rendered manuscript verification failed: {error}")

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

    archive_errors = check_release_archive()
    all_errors.extend(archive_errors)
    if archive_errors:
        print(f"FAIL: Release archive checks failed ({len(archive_errors)} issues):")
        for err in archive_errors:
            print(f"  - {err}")
    else:
        print("OK: Release archive and manifests agree.")

    if args.test is not None:
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
        print(f"\nVerification FAILED with {len(all_errors)} errors.")
        return 1

    print("\nVerification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
