"""Run original upstream verification with explicit source/version attribution.

The containing complete Git checkout provides original tests and receipts.
Pinned modules are compiled verbatim with their original checkout filenames,
so test resources resolve in that complete checkout. Runtime imports use vendor.
CLI subprocesses run the complete current checkout; its relevant Python APIs
and CLI are verified unchanged by source comparison before this run.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import types
import unittest

PIN = "6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85"
LAB = Path(__file__).resolve().parents[2]
ROOT = LAB.parents[1]
EVIDENCE = Path(__file__).resolve().parent
PAPER = "papers/lggr_viii_online_streaming_discovery_and_runtime_gluing"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_pinned_tests() -> int:
    sys.path.insert(0, str(LAB / "vendor"))
    paths = [p for p in git("ls-tree", "-r", "--name-only", PIN, "tests").decode().splitlines()
             if p.endswith(".py") and not p.endswith("test_e2e_suite.py")]
    suite = unittest.TestSuite()
    sources = []
    for i, path in enumerate(paths):
        data = git("show", f"{PIN}:{path}")
        module = types.ModuleType(f"pinned_original_test_{i}")
        module.__file__ = str(ROOT / path)
        sys.modules[module.__name__] = module
        exec(compile(data, module.__file__, "exec"), module.__dict__)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        sources.append({"path": path, "git_blob_sha1": git("rev-parse", f"{PIN}:{path}").decode().strip(),
                        "sha256": sha(data)})
    buf = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    elapsed = time.perf_counter() - start
    log = EVIDENCE / "pinned-root-tests.txt"
    log.write_text(buf.getvalue(), encoding="utf-8")
    code = 0 if result.wasSuccessful() else 1
    record = {"schema": "grok-swarm-lab.verification.v1", "suite": "pinned-root-original-tests",
              "upstream_commit": PIN, "checkout_commit": git("rev-parse", "HEAD").decode().strip(),
              "command": [sys.executable, str(Path(__file__).resolve()), "--suite", "pinned-root"],
              "exit_code": code, "tests_run": result.testsRun,
              "failures": [test.id() for test, _ in result.failures],
              "errors": [test.id() for test, _ in result.errors],
              "skips": [{"id": test.id(), "reason": reason} for test, reason in result.skipped],
              "elapsed_seconds": elapsed, "python": sys.version, "platform": platform.platform(),
              "sources": sources, "log": log.name,
              "scope": "Pinned tests/library in complete current checkout; metadata-dependent test_e2e_suite.py excluded. CLI subprocesses use current root package, whose existing relevant APIs are unchanged; addition is an unused martingale monitor."}
    (EVIDENCE / "pinned-root-tests.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("suite", "exit_code", "tests_run", "failures", "errors", "skips", "elapsed_seconds")}, indent=2))
    return code


def run_subprocess_suite(name: str) -> int:
    if name == "companion":
        args = [sys.executable, "-m", "unittest", f"{PAPER}/code/tests/test_lggr_viii_core.py", "-v"]
    elif name == "current-root-all":
        args = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    elif name in ("selftest", "demo"):
        args = [sys.executable, "-m", "lggr", name]
    elif name == "cookbook04":
        args = [sys.executable, "cookbooks/04_swarm_runtime_guard.py"]
    else:
        raise ValueError(name)
    env = dict(os.environ)
    temp = EVIDENCE / "tmp"
    temp.mkdir(exist_ok=True)
    env.update(TEMP=str(temp), TMP=str(temp), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    checkout_before = git("rev-parse", "HEAD").decode().strip()
    start = time.perf_counter()
    proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=240)
    elapsed = time.perf_counter() - start
    log = EVIDENCE / f"{name}.txt"
    log.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    checkout_after = git("rev-parse", "HEAD").decode().strip()
    record = {"schema": "grok-swarm-lab.verification.v1", "suite": name,
              "command": args, "cwd": str(ROOT), "exit_code": proc.returncode,
              "elapsed_seconds": elapsed,
              "checkout_commit_observed_before_run": checkout_before,
              "checkout_commit_observed_after_run": checkout_after,
              "head_stable_during_run": checkout_before == checkout_after,
              "python": sys.version, "log": log.name,
              "scope": "Complete checkout, no test expectations modified"}
    (EVIDENCE / f"{name}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    print((proc.stdout + proc.stderr)[-5000:])
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True,
                        choices=("pinned-root", "companion", "current-root-all", "selftest", "demo", "cookbook04"))
    args = parser.parse_args()
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.chdir(ROOT)
    temp = EVIDENCE / "tmp"
    temp.mkdir(exist_ok=True)
    os.environ.update(TEMP=str(temp), TMP=str(temp), PYTHONUTF8="1")
    return run_pinned_tests() if args.suite == "pinned-root" else run_subprocess_suite(args.suite)


if __name__ == "__main__":
    raise SystemExit(main())
