"""Run evaluation chunks sequentially with a cumulative spend gate. Never retries a failed chunk.

python -m experiments.lggr_rsi_swarm.drive --target 100
Stops before a chunk if committed spend plus that chunk's worst-case cost (twice the largest chunk
cost so far, or the full reservation of its request count before any chunk ran) would exceed the target.
"""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

from .runner import HERE, RSI_CHUNK, SWARM_CHUNK

PLAN = [("swarm", c) for c in range(400 // SWARM_CHUNK)] + [("rsi", c) for c in range(30 // RSI_CHUNK)]


def committed():
    state = json.loads((HERE / "evidence" / "ledger.json").read_text(encoding="utf-8"))
    return sum(Decimal(p["settled"]) + Decimal(p["retained"]) for p in state["phases"].values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Decimal, default=Decimal("100"))
    parser.add_argument("--resolved-model", default="claude-haiku-5-5")
    parser.add_argument("--concurrency", type=int, default=24)
    args = parser.parse_args()
    root = HERE / "evidence" / "evaluation"
    root.mkdir(parents=True, exist_ok=True)
    largest = Decimal("4")  # conservative prior for one chunk before any measurement
    for part, chunk in PLAN:
        out = root / f"{part}-{chunk:02d}"
        if (out / "summary.json").exists():
            continue
        if out.exists():
            print(json.dumps({"stop": "incomplete chunk directory present", "chunk": out.name}), flush=True)
            return 2
        before = committed()
        if before + 2 * largest > args.target:
            print(json.dumps({"stop": "spend gate", "committed_usd": str(before), "next": out.name}), flush=True)
            return 3
        result = subprocess.run([sys.executable, "-m", "experiments.lggr_rsi_swarm.runner", "live", str(out), "--split", "evaluation",
                                 "--part", part, "--chunk", str(chunk), "--concurrency", str(args.concurrency),
                                 "--resolved-model", args.resolved_model])
        spent = committed() - before
        largest = spent if out.name == "swarm-00" else max(largest, spent)
        print(json.dumps({"chunk": out.name, "exit": result.returncode, "chunk_usd": str(spent), "committed_usd": str(committed())}), flush=True)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
