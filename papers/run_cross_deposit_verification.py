#!/usr/bin/env python3
"""Cross-deposit verification harness for all six LGGR paper packages.

AuthorityEffect: None.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PACKAGES = [
    "lggr_i_evaluated_path_kernels",
    "lggr_ii_organizational_gluing",
    "lggr_iii_epk_gtla_overlay",
    "lggr_iv_finite_presentations_completion_relative",
    "lggr_v_local_green_global_red",
    "lggr_vi_nonlinear_aggregation_and_adjoint_probing",
]


def main() -> int:
    env = os.environ.copy()
    env["PYTEST_ADDOPTS"] = "-p no:asyncio"

    print("=" * 72)
    print("CROSS-DEPOSIT VERIFICATION SUITE: 6 LGGR PACKAGES")
    print("=" * 72)

    results: list[tuple[str, int, float, str]] = []
    total_start = time.time()

    for idx, pkg in enumerate(PACKAGES, start=1):
        pkg_dir = BASE_DIR / pkg
        script = pkg_dir / "verify_deposit.py"
        if not script.is_file():
            print(f"[{idx}/6] FAIL: Missing {script}")
            return 1

        print(f"[{idx}/6] Verifying {pkg}...")
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "verify_deposit.py"],
            cwd=pkg_dir,
            capture_output=True,
            text=True,
            env=env,
        )
        duration = time.time() - t0

        out = (proc.stdout or "") + (proc.stderr or "")
        summary_lines = [
            ln.strip()
            for ln in out.splitlines()
            if "verified" in ln.lower()
            or "ok:" in ln.lower()
            or "success" in ln.lower()
            or "tests:" in ln.lower()
        ]
        last_line = summary_lines[-1] if summary_lines else (out.splitlines()[-1] if out.splitlines() else "No output")
        status = "PASS" if proc.returncode == 0 else "FAIL"
        print(f"     Status: {status} ({duration:.2f}s) | Exit Code: {proc.returncode}")
        print(f"     Detail: {last_line}")
        results.append((pkg, proc.returncode, duration, last_line))

    print("=" * 72)
    all_passed = all(code == 0 for _, code, _, _ in results)
    final_status = "100% PASSED (6/6)" if all_passed else "SOME FAILED"
    print(f"FINAL STATUS: {final_status}")
    print(f"Total Duration: {time.time() - total_start:.2f}s")
    print("=" * 72)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
