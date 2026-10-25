"""Verify archived source binding, deterministic replay, and actual SQLite rows."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def verify(directory):
    directory = Path(directory).resolve()
    rows = [json.loads(line) for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    metadata = rows[0]["data"]
    if not re.fullmatch(r"[0-9a-f]{40}", metadata["source_commit"]):
        raise ValueError("invalid source commit")
    with zipfile.ZipFile(directory / "source_snapshot.zip") as z, tempfile.TemporaryDirectory(prefix="lggr-replay-") as td:
        if sorted(z.namelist()) != sorted(metadata["source_hashes"]):
            raise ValueError("source archive membership differs")
        for name, expected in metadata["source_hashes"].items():
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or ":" in name:
                raise ValueError("unsafe archive member")
            raw = z.read(name)
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("source archive hash differs")
            committed = subprocess.check_output(["git", "show", metadata["source_commit"]+":"+name], cwd=ROOT)
            if committed != raw:
                raise ValueError("source differs from its recorded Git commit")
            target = Path(td) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        result = subprocess.run([sys.executable, "-m", "experiments.concurrent_five_agent_swarm.runner", "replay", str(directory / "events.jsonl")],
                                cwd=td, text=True, capture_output=True)
        if result.returncode:
            raise ValueError(result.stderr)
        replay = json.loads(result.stdout)
    # The frozen replay has validated every event, including interrupted runs.
    # Derive physical outputs from execution events, not only a final summary.
    expected = {}
    for event in rows:
        kind, data = event["kind"], event["data"]
        if kind == "case_start":
            seed = data["seed"]
            expected[f"{seed}-baseline.sqlite"] = []
        elif kind == "initial_execution" and data["executed"]:
            expected[f"{seed}-baseline.sqlite"] = data["rows"]
        elif kind == "arm_start":
            expected[f"{seed}-{data['arm']}.sqlite"] = [
                {"worker": w, **p} for w,p in sorted(data["state"]["completed"].items())]
        elif kind == "execution" and data["executed"]:
            expected[f"{seed}-{data['arm']}.sqlite"] = data["rows"]
    if {p.name for p in directory.glob("*.sqlite")} != set(expected):
        raise ValueError("SQLite file set differs")
    database_count = 0
    for filename, wanted in expected.items():
        db = sqlite3.connect((directory / filename).as_uri()+"?mode=ro", uri=True)
        actual = [dict(zip(("worker", "slot", "total_cents", "epoch"), r)) for r in db.execute("SELECT worker,slot,total_cents,epoch FROM dispatch ORDER BY worker")]
        db.close()
        if actual != wanted:
            raise ValueError("SQLite output differs: " + filename)
        database_count += 1
    replay["completed_cases"] = sum(e["kind"] == "case_result" for e in rows)
    replay["attempted_cases"] = sum(e["kind"] == "case_start" for e in rows)
    replay["stopped"] = rows[-1]["kind"] == "stopped"
    return {"run": directory.name, "source_commit_verified": True, "source_files": len(metadata["source_hashes"]),
            "sqlite_files_verified": database_count, **replay}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+")
    args = parser.parse_args()
    print(json.dumps([verify(p) for p in args.directories], indent=2))
