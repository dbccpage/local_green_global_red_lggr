#!/usr/bin/env python3
"""Capture Paper I's fresh theorem-level Lean axiom report."""

from __future__ import annotations

import sys
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verify_deposit import AXIOM_REPORT, capture_axiom_report  # noqa: E402


def main() -> int:
    rendered, reports, problems = capture_axiom_report(ROOT)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    destination = ROOT / AXIOM_REPORT
    destination.write_text(rendered, encoding="utf-8", newline="\n")
    print(
        f"wrote {destination.relative_to(ROOT)} with "
        f"{len(reports)} theorem-level reports"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
