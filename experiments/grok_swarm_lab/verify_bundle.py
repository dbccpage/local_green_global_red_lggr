"""Clean extraction, byte verification, separate-process execution and replay."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import time
import uuid
import zipfile

root = Path(__file__).resolve().parent
archive = root / "dist/lggr-swarm-lab-2026-10-24.zip"
receipt_path = root / "evidence/clean-extraction.json"
output_dir = root / "evidence/clean-extraction-logs"
output_dir.mkdir(parents=True, exist_ok=True)
if receipt_path.exists():
    raise SystemExit("clean-extraction evidence already exists; preserve it")
temp_root = (root / "dist").resolve()
target = (temp_root / ("clean-check-" + uuid.uuid4().hex)).resolve()
assert target.is_relative_to(temp_root) and target != temp_root
target.mkdir()
try:
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not (target / name).resolve().is_relative_to(target):
                raise ValueError("archive member escapes extraction directory")
        z.extractall(target)
    lab = target / "grok_swarm_lab"
    checksums = {}
    for line in (lab / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = (lab / name).resolve()
        assert path.is_relative_to(lab)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("checksum differs: "+name)
        checksums[name] = actual
    commands = [
        ("tests", ["-m","unittest","discover","-s","tests","-v"]),
        ("demo", ["-m","lggr_swarm_lab","demo","--output","clean-demo"]),
        ("evaluation", ["-m","lggr_swarm_lab","benchmark","--protocol","protocol.json","--output","clean-evaluation","--split","evaluation"]),
        ("interactive-replay", ["-m","lggr_swarm_lab","replay","evidence/evaluation/runs/evaluation.query_scope.01.C.json"]),
        ("fixed-replay", ["-m","lggr_swarm_lab","replay","evidence/evaluation/fixed-traces/evaluation.equal_reports.00.json"]),
        ("native-replay", ["-m","lggr_swarm_lab","replay","evidence/native/run.json"]),
    ]
    receipts = []
    environment = {k:v for k,v in os.environ.items() if k not in ("PYTHONPATH","OPENAI_API_KEY","OPENROUTER_API_KEY")}
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for name, args in commands:
        tick = time.perf_counter_ns()
        result = subprocess.run([sys.executable,*args],cwd=lab,env=environment,
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log = output_dir / (name+".txt")
        log.write_bytes(result.stdout)
        receipts.append({"name":name,"argv":[sys.executable,*args],"exit_code":result.returncode,
                         "elapsed_ns":time.perf_counter_ns()-tick,"output_file":log.relative_to(root).as_posix()})
    original = json.loads((lab / "evidence/evaluation/results.json").read_text(encoding="utf-8"))
    repeated = json.loads((lab / "clean-evaluation/results.json").read_text(encoding="utf-8"))
    comparable = lambda r: {m:{k:s[k] for k in ("counts","defects","rates")} for m,s in r["mode_summary"].items()}
    outcomes_match = comparable(original)==comparable(repeated)
    receipt = {"created_utc":datetime.now(timezone.utc).isoformat(),"archive_sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),
        "manifested_files_verified":len(checksums),"source_and_data_hashes":checksums,"commands":receipts,
        "repeated_evaluation_matches":outcomes_match,"repeated_evaluation_replay_failures":repeated["replay_failures"],
        "git_required":False,"api_key_required":False,"native_model_calls_on_replay":0,
        "success":all(r["exit_code"]==0 for r in receipts) and outcomes_match and not repeated["replay_failures"]}
    receipt_path.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k!="source_and_data_hashes"},indent=2))
finally:
    # Remove only the fresh extraction directory checked inside this lab's dist.
    assert target.is_relative_to(temp_root) and target != temp_root
    shutil.rmtree(target)
raise SystemExit(0 if receipt["success"] else 1)
