#!/usr/bin/env python3
"""One-command verifier for the research paper deposit.

Deterministic, two-way verification:
1. Every file listed in SHA256SUMS exists and matches its recorded hash.
2. Sweep: no unrecorded non-excluded file is present in the deposit tree.
3. Fail-closed symlink rejection: rejects any unauthorized symlink.
4. Structural artifacts are present and non-empty.
5. The exact Fraction replay prints its receipt and its unittest module passes.
6. lean4/minkowski_repair.lean elaborates with the pinned toolchain binary.
   That file is not a Lake root. Optional (--lean) still runs lake build.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
        targets = sorted(
            p.relative_to(ROOT).as_posix()
            for directory in (ROOT / "code", ROOT / "code" / "tests")
            for p in directory.glob("test_*.py")
        )
    if not targets:
        return ["No test files found in code/ or code/tests/"]
    errors: list[str] = []
    for target in targets:
        try:
            path = safe_path(ROOT, target)
            relative = path.relative_to(ROOT)
            if (relative.parent.as_posix() not in {"code", "code/tests"}
                    or not path.name.startswith("test_") or path.suffix != ".py"
                    or not path.is_file()):
                raise ValueError(f"Invalid test target: {target}")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", target, "-q"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                timeout=180, check=False,
            )
            # Pytest's no-tests-collected status is a failure, not a vacuous pass.
            if result.returncode:
                errors.append(f"Pytest failure in {target}:\n{result.stdout}\n{result.stderr}")
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            errors.append(str(error))
    return errors


def _toolchain_roots() -> list[Path]:
    roots = [Path.home() / ".elan"]
    if os.environ.get("ELAN_HOME"):
        roots.insert(0, Path(os.environ["ELAN_HOME"]))
    for here in (ROOT, *ROOT.parents):
        roots.append(here / ".elan")
    return list(dict.fromkeys(roots))


def _matches_version(executable: Path, version: str) -> bool:
    try:
        result = subprocess.run(
            [str(executable), "--version"], cwd=tempfile.gettempdir(),
            capture_output=True, text=True, encoding="utf-8", timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    match = re.match(r"Lean \(version ([^,\s)]+)", result.stdout)
    return result.returncode == 0 and match is not None and match[1] == version


def toolchain_lean() -> Path | None:
    """Resolve an installed compiler and validate the exact pin; never install."""
    pin = (ROOT / "lean4" / "lean-toolchain").read_text(encoding="utf-8").strip()
    match = re.fullmatch(r"leanprover/lean4:v(\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)", pin)
    if match is None:
        raise ValueError(f"Unsupported Lean toolchain pin: {pin!r}")
    version = match[1]
    executable = "lean.exe" if os.name == "nt" else "lean"
    for base in _toolchain_roots():
        candidate = base / "toolchains" / ("leanprover--lean4---v" + version) / "bin" / executable
        if candidate.is_file():
            return candidate if _matches_version(candidate, version) else None
    found = shutil.which("lean")
    if not found:
        return None
    candidate = Path(found)
    # Elan launchers may install while invoking lean. Resolve the pin with
    # `elan which` instead; this command only identifies an installed binary.
    elan = candidate.with_name("elan.exe" if os.name == "nt" else "elan")
    if elan.is_file():
        env = dict(os.environ, ELAN_TOOLCHAIN=pin)
        try:
            result = subprocess.run(
                [str(elan), "which", "lean"], cwd=tempfile.gettempdir(), env=env,
                capture_output=True, text=True, encoding="utf-8", timeout=10, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if result.returncode:
            return None
        candidate = Path(result.stdout.strip())
        if not candidate.is_file() or candidate == Path(found):
            return None
    return candidate if _matches_version(candidate, version) else None


def check_exact_replay() -> list[str]:
    errors: list[str] = []
    receipt = subprocess.run(
        [sys.executable, str(ROOT / "code" / "lgr_replay.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    print(receipt.stdout.strip())
    if receipt.returncode != 0:
        errors.append(f"lgr_replay receipt failed:\n{receipt.stdout}\n{receipt.stderr}")
    else:
        for needle in (
            "r2-l1=2",
            "r2-l2sq=2",
            "r2-linf=1",
            "r2-interval=-1,1",
            "r2-mid=0",
            "r4-l1=3/2",
            "r4-l2sq=9/5",
            "r4-linf=1",
            "r4-alpha=1/2,1/5,0",
        ):
            if needle not in receipt.stdout:
                errors.append(f"receipt missing {needle}")
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "code", "-p", "test_lgr_replay.py", "-v"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    combined = tests.stdout + tests.stderr
    print(combined)
    if tests.returncode != 0 or "\nOK" not in combined:
        errors.append(f"exact replay tests failed:\n{combined}")
    return errors


def check_minkowski() -> list[str]:
    lean_dir = ROOT / "lean4"
    source = lean_dir / "minkowski_repair.lean"
    if not source.is_file():
        return ["Missing lean4/minkowski_repair.lean"]
    executable = toolchain_lean()
    if executable is None:
        return ["An installed Lean compiler matching lean4/lean-toolchain was not found; refusing to download"]
    with tempfile.TemporaryDirectory(prefix="lggr5-minkowski-") as temporary:
        olean = Path(temporary) / "minkowski_repair.olean"
        temp_source = Path(temporary) / source.name
        shutil.copy2(source, temp_source)
        result = subprocess.run(
            [str(executable), f"--o={olean}", str(temp_source)], cwd=str(temporary),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=180, check=False,
        )
    print(result.stdout)
    if result.stderr.strip():
        print(result.stderr)
    if result.returncode != 0:
        return [f"minkowski_repair.lean failed:\n{result.stdout}\n{result.stderr}"]
    errors: list[str] = []
    required = set(re.findall(r"^#print axioms (MinkowskiRepair\.\w+)$", source.read_text(encoding="utf-8"), re.M))
    reported = set(re.findall(r"^'(MinkowskiRepair\.\w+)' (?:depends on axioms:|does not depend on any axioms)", result.stdout, re.M))
    if len(required) != 19 or reported != required:
        errors.append(f"Rational repair census mismatch: expected 19 named reports; missing={sorted(required - reported)}, unexpected={sorted(reported - required)}")
    for line in result.stdout.splitlines():
        if "depends on axioms:" not in line:
            continue
        axioms_part = line.split("depends on axioms:", 1)[1].strip().strip("[]")
        for axiom in axioms_part.split(","):
            axiom_name = axiom.strip()
            if axiom_name and axiom_name not in AXIOM_WHITELIST:
                errors.append(f"Unauthorized axiom dependency: {axiom_name} in '{line}'")
            if axiom_name == "sorryAx":
                errors.append(f"sorry in '{line}'")
    return errors


def check_lean() -> list[str]:
    """Build pinned Lake roots and compare every named census entry."""
    lean_dir = ROOT / "lean4"
    executable = toolchain_lean()
    if executable is None:
        return ["Exact pinned Lean compiler unavailable; refusing Lake replay"]
    lake = executable.with_name("lake.exe" if os.name == "nt" else "lake")
    if not lake.is_file():
        return ["Lake binary beside the validated Lean compiler is unavailable"]
    # Offline replay: an absent local dependency must not trigger a git clone.
    import json
    dependencies = json.loads((lean_dir / "lake-manifest.json").read_text(encoding="utf-8"))
    for package in dependencies["packages"]:
        directory = lean_dir / dependencies["packagesDir"] / package["name"]
        if not directory.is_dir():
            return [f"Missing local Lake dependency: {package['name']}; refusing to download"]
        revision = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "HEAD"], capture_output=True,
            text=True, encoding="utf-8", timeout=10, check=False,
        )
        if not (directory / ".git").exists() or revision.returncode or revision.stdout.strip() != package["rev"]:
            return [f"Local Lake dependency revision differs from its pin: {package['name']}; refusing to fetch"]
    env = dict(os.environ)
    env["PATH"] = str(executable.parent) + os.pathsep + env.get("PATH", "")
    build = subprocess.run(
        [str(lake), "build"], cwd=lean_dir, env=env, capture_output=True,
        text=True, encoding="utf-8", timeout=180, check=False,
    )
    if build.returncode:
        return [f"Lake build failed:\n{build.stdout}\n{build.stderr}"]
    # Reuse the shipped parser/generator rather than accepting a partial report.
    sys.path.insert(0, str(ROOT / "tools"))
    import replay_lean_axiom_census as census
    census.check_census(ROOT)
    result = subprocess.run(
        [str(lake), "env", "lean", "Census.lean"], cwd=lean_dir, env=env,
        capture_output=True, text=True, encoding="utf-8", timeout=180, check=False,
    )
    if result.returncode:
        return [f"Lean census failed:\n{result.stdout}\n{result.stderr}"]
    actual = census._declarations(result.stdout, "current Lean replay")
    if actual != census.parse_report(ROOT):
        return ["Lean census declaration names or axiom sets differ from axiom_report.txt"]
    errors = []
    for declaration in actual:
        for axiom in sorted(declaration.axioms - AXIOM_WHITELIST):
            errors.append(f"Unauthorized axiom dependency: {axiom} in {declaration.name}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify paper deposit package.")
    parser.add_argument("--lean", action="store_true", help="Run Lean verification and axiom audit.")
    parser.add_argument("--test", action="append", default=[], help="Named test file; repeat as needed.")
    args = parser.parse_args(argv)

    all_errors: list[str] = []
    metadata = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "sync_metadata.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    print(metadata.stdout.strip())
    if metadata.returncode:
        all_errors.append(f"Publication metadata mismatch: {metadata.stdout} {metadata.stderr}")

    manifest_target = MANIFEST
    if not manifest_target.exists() and (ROOT / "MANIFEST.sha256").is_file():
        manifest_target = ROOT / "MANIFEST.sha256"

    manifest_errors = check_manifest(manifest_target)
    all_errors.extend(manifest_errors)
    initial_manifest_digest = sha256_of(manifest_target) if not manifest_errors else None
    if manifest_errors:
        print(f"FAIL: Manifest checks failed ({len(manifest_errors)} issues):")
        for err in manifest_errors:
            print(f"  - {err}")
    else:
        print("OK: Manifest and two-way sweep checks passed.")

    try:
        replay_errors = check_exact_replay()
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        replay_errors = [f"Exact replay did not complete: {error}"]
    all_errors.extend(replay_errors)
    if replay_errors:
        print("FAIL: Exact Fraction replay failed.")
        for err in replay_errors:
            print(f"  - {err}")
    else:
        print("OK: Exact Fraction replay matched.")

    try:
        minkowski_errors = check_minkowski()
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        minkowski_errors = [f"Minkowski Lean check did not complete: {error}"]
    all_errors.extend(minkowski_errors)
    if minkowski_errors:
        print("FAIL: Minkowski Lean check failed.")
        for err in minkowski_errors:
            print(f"  - {err}")
    else:
        print("OK: minkowski_repair.lean elaborated with no sorry.")

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

    # Recheck after every mutable verification subprocess. Pin the initial
    # control digest as well, so a child cannot silently repin changed payload.
    post_errors = check_manifest(manifest_target)
    if initial_manifest_digest is not None and not post_errors:
        if sha256_of(manifest_target) != initial_manifest_digest:
            post_errors.append("Integrity manifest changed during verification")
    all_errors.extend(post_errors)
    for error in post_errors:
        print(f"FAIL: Post-replay integrity: {error}")

    if all_errors:
        print(f"\nVerification FAILED with {len(all_errors)} errors.")
        return 1

    print("\nVerification PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
