#!/usr/bin/env python3
"""Run the unmodified supplied finite tests with package-local imports."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run(output: Path | None = None) -> int:
    sys.path.insert(0, str(ROOT / "code"))
    bound = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [ROOT / "code/institutional_reasoning.py",
                       ROOT / "code/tests/test_institutional_reasoning.py"]}
    suite = unittest.defaultTestLoader.discover(str(ROOT / "code/tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    success = result.wasSuccessful() and result.testsRun == 17
    if output:
        if output.exists():
            raise ValueError("Refusing to replace an existing execution receipt")
        output.write_text(json.dumps({
            "schema": "institutions.finite-checks.v1", "python": platform.python_version(),
            "tests_run": result.testsRun, "success": success, "source_hashes": bound,
            "exhaustive_cases": {"recoverability": 216, "side_information": 216},
            "scope": "Exact finite synthetic cases. No Python-to-Lean refinement or live council experiment."
        }, indent=2) + "\n", encoding="utf-8")
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="Write a new receipt explicitly")
    args = parser.parse_args()
    raise SystemExit(run(args.receipt))
