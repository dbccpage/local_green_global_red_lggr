#!/usr/bin/env python3
"""Capture or verify Paper VI's deterministic theorem-level axiom report."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "lean4" / "AXIOM_REPORT.txt"


def load_verifier() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "lggr_vi_verify_for_axioms", ROOT / "verify_deposit.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_deposit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare a fresh census with the bundled report without writing",
    )
    args = parser.parse_args(argv)

    verifier = load_verifier()
    report, reports, problems = verifier.capture_axiom_report(ROOT)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1

    if args.check:
        if not REPORT.is_file():
            print(f"FAIL: missing {REPORT}", file=sys.stderr)
            return 1
        if REPORT.read_text(encoding="utf-8") != report:
            print("FAIL: bundled axiom report is stale", file=sys.stderr)
            return 1
        print(f"axiom report matches {len(reports)} freshly elaborated theorems")
        return 0

    REPORT.write_text(report, encoding="utf-8", newline="\n")
    print(f"wrote {REPORT} from {len(reports)} freshly elaborated theorems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
