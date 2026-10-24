"""Compile byte-exact root and paper-local Lean sources separately, offline."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

PIN = "6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85"
HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parents[1]
PAPER = "papers/lggr_viii_online_streaming_discovery_and_runtime_gluing"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    # Use an already installed compiler, never install or update a toolchain.
    prefix = subprocess.check_output(["lean", "--print-prefix"], cwd=ROOT / "lean4", text=True).strip()
    compiler = Path(prefix) / "bin" / ("lean.exe" if os.name == "nt" else "lean")
    version = subprocess.check_output([str(compiler), "--version"], text=True).strip()
    groups = [("root", "lean4", ["LggrVII.lean", "LggrVIII.lean", "CheckAxioms.lean"]),
              ("paper-local", f"{PAPER}/lean4", ["LggrVIII.lean", "CheckAxioms.lean"])]
    records = []
    for group, upstream, names in groups:
        folder = HERE / "lean" / group
        folder.mkdir(parents=True, exist_ok=True)
        sources = []
        for name in names:
            path = f"{upstream}/{name}"
            content = git("show", f"{PIN}:{path}")
            (folder / name).write_bytes(content)
            sources.append({"path": path, "sha256": hashlib.sha256(content).hexdigest(),
                            "git_blob_sha1": git("rev-parse", f"{PIN}:{path}").decode().strip()})
        env = dict(os.environ)
        env["LEAN_PATH"] = str(folder)
        commands = []
        for name in names:
            args = [str(compiler), "-o", str(folder / name.replace(".lean", ".olean")), name]
            start = time.perf_counter()
            proc = subprocess.run(args, cwd=folder, env=env, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace", timeout=60)
            log_name = f"lean-{group}-{Path(name).stem}.txt"
            (HERE / log_name).write_text(proc.stdout + proc.stderr, encoding="utf-8")
            commands.append({"command": args, "cwd": str(folder), "exit_code": proc.returncode,
                             "elapsed_seconds": time.perf_counter() - start, "log": log_name})
            if proc.returncode:
                break
        records.append({"artifact": group, "sources": sources, "commands": commands,
                        "all_succeeded": len(commands) == len(names) and all(c["exit_code"] == 0 for c in commands)})
    receipt = {"schema": "grok-swarm-lab.lean-verification.v1", "reviewed_commit": PIN,
               "compiler_version": version, "artifacts": records,
               "scope": "Original source modules and original axiom census compiled separately. No application-specific theorem added, no identification of the two C10 orientations, no source archive or deployment certification.",
               "all_succeeded": all(r["all_succeeded"] for r in records)}
    (HERE / "lean-verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"compiler": version, "results": [{"artifact": r["artifact"], "passed": r["all_succeeded"]} for r in records]}, indent=2))
    return 0 if receipt["all_succeeded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
