"""Verify run directories: hash chain, committed source binding, deterministic replay, saved summary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from ._path import ROOT
from swarm.hashing import digest, load_events


def verify(directory):
    directory = Path(directory).resolve()
    events = next(directory.glob("events.jsonl*"))
    records = load_events(events)
    meta = records[0]["data"]
    with tempfile.TemporaryDirectory(prefix="lggr-rsi-replay-") as tmp:
        for name, expected in meta["source_hashes"].items():
            path = Path(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("unsafe source path")
            blob = subprocess.check_output(["git", "show", f"{meta['source_commit']}:{name}"], cwd=ROOT)
            if hashlib.sha256(blob).hexdigest() != expected:
                raise ValueError("committed source differs from recorded hash: " + name)
            target = Path(tmp) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
        env = dict(os.environ, PYTHONPATH=tmp)
        env.pop("ANTHROPIC_API_KEY", None)
        result = subprocess.run([sys.executable, "-m", "experiments.lggr_rsi_swarm.runner", "replay", str(events)],
                                cwd=tmp, env=env, text=True, capture_output=True)
        if result.returncode:
            raise ValueError(result.stderr[-2000:])
        replayed = json.loads(result.stdout)
    reused = 0
    if meta["config"].get("prefix_from"):
        primary = {}
        for name in meta["config"]["prefix_from"]:
            for r in load_events(directory.parent.parent / "evaluation" / name / "events.jsonl.gz"):
                if r["kind"] == "response":
                    primary[r["data"]["key"]] = r["data"]["body"]
        for r in records:
            if r["kind"] == "response" and r["data"].get("reused"):
                if primary.get(r["data"]["key"]) != r["data"]["body"]:
                    raise ValueError("reused response differs from the primary record: " + r["data"]["key"])
                reused += 1
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    if replayed["summary_sha256"] != digest(summary):
        raise ValueError("saved summary differs from replay")
    return {"run": directory.name, "events": len(records), "source_files": len(meta["source_hashes"]),
            "source_commit": meta["source_commit"], "replay_complete": replayed["complete"], "summary_verified": True,
            "reused_primary_responses_verified": reused}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+")
    args = parser.parse_args()
    print(json.dumps([verify(p) for p in args.directories], indent=1))
