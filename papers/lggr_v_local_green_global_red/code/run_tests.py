"""Standalone test runner enforcing 100% test coverage."""
import os
import sys

import pytest

if __name__ == "__main__":
    code_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(code_dir)
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)

    args = [
        ".",
        "-v",
        "--cov=code_core",
        "--cov=code_blind_spots",
        "--cov=code_witnesses",
        "--cov=code_theorems",
        "--cov=code_quotient_solver",
        "--cov=code_exact_obstruction",
        "--cov=code_cli",
        "--cov-report=term-missing",
        "--cov-fail-under=100",
    ]
    try:
        exit_code = pytest.main(args)
    finally:
        cov_file = os.path.join(code_dir, ".coverage")
        if os.path.isfile(cov_file):
            try:
                os.remove(cov_file)
            except OSError:
                pass
    sys.exit(exit_code)
