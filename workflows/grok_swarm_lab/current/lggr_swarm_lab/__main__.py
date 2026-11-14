"""One-command demo, tests, benchmark and preserved-evidence replay."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from . import ROOT
from .benchmark import benchmark, demo, replay_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Finite SQLite LGGR handoff laboratory; no API key required.")
    commands = parser.add_subparsers(dest="command", required=True)
    d = commands.add_parser("demo", help="Execute four development examples and replay every trace")
    d.add_argument("--output", type=Path, default=Path("demo-results"))
    b = commands.add_parser("benchmark", help="Run frozen A/B/C interactive and identical-evidence comparisons")
    b.add_argument("--protocol", type=Path, default=Path("protocol.json"))
    b.add_argument("--output", type=Path, default=Path("results"))
    b.add_argument("--split", choices=("development", "evaluation"), default="evaluation")
    r = commands.add_parser("replay", help="Replay a stored interactive or fixed-evidence trace")
    r.add_argument("path", type=Path)
    commands.add_parser("tests", help="Run standard-library unittest discovery")
    args = parser.parse_args(argv)
    try:
        if args.command == "tests":
            return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT).returncode
        if args.command == "demo":
            result = demo(args.output)
            print(json.dumps(result, indent=2, sort_keys=True))
            return int(any(not e["replay"]["replayed"] for e in result["examples"]))
        if args.command == "replay":
            print(json.dumps(replay_file(args.path), indent=2, sort_keys=True))
            return 0
        result = benchmark(args.protocol, args.output, args.split)
        print(json.dumps({"output": str(args.output.resolve()), "split": result["split"],
                          "mode_summary": result["mode_summary"], "fixed_trace_summary": result["fixed_trace_summary"],
                          "replay_failures": result["replay_failures"]}, indent=2, sort_keys=True))
        return int(bool(result["replay_failures"]))
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
