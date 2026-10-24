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
    "*_monograph.tex",
    "*_monograph.pdf",
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

AXIOM_WHITELIST = frozenset({"Quot.sound", "propext", "Classical.choice", "Classical.choice"})


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

        # Check paper header compliance on monograph
        monographs = [
            p for p in ROOT.glob("*.md")
            if p.name.lower() not in ("readme.md", "review_scope.md")
            and not p.name.endswith(("_change_log.md", "_claim_ledger.md", "_supplement.md", "supplement.md"))
        ]
        if monographs:
            mono_path = monographs[0]
            try:
                from omega_engine_atlas.coda_atlas._kits.paper_header_schema import parse_paper_header
                parse_paper_header(mono_path.read_text(encoding="utf-8"), strict=True)
            except ImportError:
                pass  # Standalone environment without repo import
            except Exception as exc:
                errors.append(f"Monograph header non-compliant ({mono_path.name}): {exc}")
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


def sealed_snapshot(manifest_path: Path) -> dict[str, str]:
    """Retain original expectations, including the manifest's own bytes."""
    expected = dict(read_manifest(ROOT, manifest_path))
    expected[manifest_path.relative_to(ROOT).as_posix()] = sha256_of(manifest_path)
    return expected


def check_seal_unchanged(expected: dict[str, str]) -> list[str]:
    errors = []
    for relative, digest in expected.items():
        path = safe_path(ROOT, relative)
        if not path.is_file() or sha256_of(path) != digest:
            errors.append(f"Sealed file changed during verification: {relative}")
    return errors


def check_lean() -> list[str]:
    errors = []
    sys.path.insert(0, str(ROOT / 'tools'))
    from vendor_evidence import validate_vendor
    validate_vendor(ROOT)
    for tool, option in [("replay_lean_axiom_census.py", "--replay"),
                         ("replay_full_axiom_census.py", "--check"),
                         ("replay_simplex_implementation.py", "--replay")]:
        result = subprocess.run([sys.executable, str(ROOT / "tools" / tool), option],
                                cwd=ROOT, capture_output=True, text=True,
                                encoding="utf-8", timeout=2100)
        if result.returncode:
            errors.append(result.stdout + result.stderr)
    validate_vendor(ROOT, cache_root=ROOT / 'lean4/.lake/vendor')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify paper deposit package.")
    parser.add_argument("--lean", action="store_true", help="Run Lean verification and axiom audit.")
    parser.add_argument("--test", action="append", default=[], help="Named test file; repeat as needed.")
    args = parser.parse_args()

    all_errors: list[str] = []
    manifest_target = MANIFEST if MANIFEST.is_file() else ROOT / "MANIFEST.sha256"
    original_seal = {}
    try:
        original_seal = sealed_snapshot(manifest_target)
    except (OSError, ValueError) as error:
        all_errors.append(f"Cannot capture original seal: {error}")
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from replay_live_memory_evidence import replay
        replay(ROOT)
        print("OK: live memory trial evidence replayed offline, including failed arithmetic.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        all_errors.append(f"Memory evidence replay failed: {error}")
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from replay_review_corrections import replay as replay_review_corrections
        replay_review_corrections(ROOT)
        print("OK: Review source custody and uncertainty-adjusted example replayed.")
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        all_errors.append("Review corrections: " + str(error))
    mind = subprocess.run([sys.executable, str(ROOT / 'tools/replay_mind_expansion.py')],
                          cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=120)
    if mind.returncode:
        all_errors.append('Mind expansion source/replay drift: ' + mind.stdout + mind.stderr)
    else:
        print(mind.stdout.strip())
    from rebuild_release import validate
    all_errors.extend(validate(ROOT))
    generated = subprocess.run([sys.executable, str(ROOT / 'tools/generate_lp_certificates.py'), '--check'],
                               cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=120)
    if generated.returncode:
        all_errors.append('Solver certificate source drift: ' + generated.stdout + generated.stderr)
    executions = subprocess.run([sys.executable, str(ROOT / 'tools/replay_simplex_implementation.py'), '--check'],
                               cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=120)
    if executions.returncode:
        all_errors.append('Simplex execution source drift: ' + executions.stdout + executions.stderr)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from paper_spine import verify_render
        verify_render(ROOT)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        all_errors.append(f"Document binding failed: {error}")

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
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            lean_errors = [f"Lean verification did not complete: {error}"]
        all_errors.extend(lean_errors)
        if lean_errors:
            print("FAIL: Lean checks failed.")
            for err in lean_errors:
                print(f"  - {err}")
        else:
            print("OK: Lean proofs and axiom census verified.")

    try:
        seal_errors = check_seal_unchanged(original_seal) + check_manifest(manifest_target)
    except (OSError, ValueError) as error:
        seal_errors = [str(error)]
    all_errors.extend(seal_errors)
    if not seal_errors and original_seal:
        print("OK: original sealed bytes and final two-way sweep preserved.")
    for error in seal_errors:
        print(f"FAIL: {error}")

    if all_errors:
        print(f"\nVerification FAILED with {len(all_errors)} errors.")
        return 1

    print("\nVerification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
