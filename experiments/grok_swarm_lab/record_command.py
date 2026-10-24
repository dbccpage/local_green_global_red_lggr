"""Run a command and retain its actual output, timestamps and exit code."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
name, *command = sys.argv[1:]
if not name or not command or Path(name).name != name:
    raise SystemExit("usage: python record_command.py NAME COMMAND [ARG ...]")
destination = root / "evidence/commands"
destination.mkdir(parents=True, exist_ok=True)
log = destination / (name + ".txt")
receipt = destination / (name + ".json")
if log.exists() or receipt.exists():
    raise SystemExit("command evidence already exists; use a new name")
started = datetime.now(timezone.utc).isoformat()
tick = time.perf_counter_ns()
result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output = result.stdout.decode("utf-8", errors="replace")
log.write_text(output, encoding="utf-8")
receipt.write_text(json.dumps({"argv":command,"cwd":str(root),"started_utc":started,
    "finished_utc":datetime.now(timezone.utc).isoformat(),"elapsed_ns":time.perf_counter_ns()-tick,
    "exit_code":result.returncode,"python":sys.version,"platform":platform.platform(),
    "output_file":log.relative_to(root).as_posix()}, indent=2)+"\n", encoding="utf-8")
print(output[-8000:])
print(json.dumps({"receipt":str(receipt),"exit_code":result.returncode}))
raise SystemExit(result.returncode)
