"""Harness for RSI Lean 4 and Python Verification Gate Execution.

AuthorityEffect: None.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

RSI_DIR = Path(__file__).resolve().parent
REPO_ROOT = RSI_DIR.parents[2]


def run_rsi_verification_gate() -> dict[str, object]:
    """Executes the Python/Rust/Lean verification test suite for Paper 012 RSI."""
    test_path = (
        REPO_ROOT
        / "omega_engine_atlas"
        / "coda_atlas"
        / "F004_papers"
        / "012_rsi"
        / "000_relational_reasoning_and_rsi_impossibility"
        / "code"
        / "tests"
        / "test_rsi_impossible_lean_verification.py"
    )
    cmd = ["py", "-3.12", "-m", "pytest", str(test_path), "-v"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    passed = (res.returncode == 0) and ("88 passed" in res.stdout or "passed" in res.stdout)
    return {
        "status": "PASS" if passed else "FAIL",
        "returncode": res.returncode,
        "raw_stdout": res.stdout,
        "raw_stderr": res.stderr,
    }


if __name__ == "__main__":
    result = run_rsi_verification_gate()
    print(json.dumps(result, indent=2))
