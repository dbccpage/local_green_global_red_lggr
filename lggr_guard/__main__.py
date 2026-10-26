"""CLI: compose real git branches before merging.

python -m lggr_guard compose --base main --branch feat-a --branch feat-b \
    --check "python -m pytest -q tests/probes" --protect tests/probes \
    [--observe "python tools/observe.py"] [--declare feat-a=parallelism] [--log decisions.jsonl]

Exit status: 0 accept, 1 reject (NGD, undeclared behaviour or drift), 2 usage error.
"""
import argparse
import json
import sys

from .git import compose_branches
from .log import DecisionLog


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lggr_guard")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compose", help="check branches alone and together against the base")
    c.add_argument("--repo", default=".")
    c.add_argument("--base", default="main")
    c.add_argument("--branch", action="append", required=True, help="in merge order; repeat")
    c.add_argument("--check", required=True, help="shell command; exit 0 = pass")
    c.add_argument("--observe", help="shell command printing a JSON object of observable behaviours")
    c.add_argument("--declare", action="append", default=[], help="branch=behaviour[,behaviour...] the branch may change")
    c.add_argument("--protect", action="append", default=[], help="path reset to the base version before checking")
    c.add_argument("--log", help="append the decision to this hash-chained JSONL log")
    args = parser.parse_args(argv)
    declares = {}
    for item in args.declare:
        branch, _, keys = item.partition("=")
        declares[branch] = [k for k in keys.split(",") if k]
    report = compose_branches(args.repo, args.base, args.branch, args.check, args.observe, declares, args.protect)
    if args.log:
        DecisionLog(args.log).append("compose", {k: report[k] for k in ("base", "verdict", "reasons", "defect", "minimal_failing_sets", "undeclared")}
                                     | {"branches": args.branch})
    print(json.dumps({k: v for k, v in report.items() if k != "details"}, indent=1, sort_keys=True, default=str))
    return 0 if report["verdict"] == "accept" else 1


if __name__ == "__main__":
    sys.exit(main())
