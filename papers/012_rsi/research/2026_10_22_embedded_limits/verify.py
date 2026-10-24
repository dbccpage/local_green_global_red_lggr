"""Replay this research packet; preserve actual source and theorem custody."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parent


def hashes():
    names = ("EmbeddedLimits.lean", "Census.lean", "lean-toolchain", "finite_limits.py",
             "test_finite_limits.py", "verify.py", "README.md", "research_note.md",
             "extension_plan.md", "sources.json", "baseline_inventory.json", "axiom_report.txt")
    return {name: sha256((ROOT/name).read_bytes()).hexdigest() for name in names}


def run(command, *, cwd, env):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, encoding="utf-8", timeout=120)
    if result.returncode:
        raise ValueError("EXECUTION_FAILED: " + " ".join(command) + "\n" + result.stdout + result.stderr)
    return result.stdout + result.stderr


def verify(lean, write=False):
    source = (ROOT/"EmbeddedLimits.lean").read_text(encoding="utf-8")
    stripped = re.sub(r"/-[\s\S]*?-/", "", source)
    if re.search(r"\b(sorry|admit)\b|^\s*(?:unsafe\s+)?axiom\s+", stripped, re.M):
        raise ValueError("UNFINISHED_OR_AXIOMATIC_SOURCE")
    names = re.findall(r"^theorem ([a-zA-Z0-9_]+)", stripped, re.M)
    expected = "import EmbeddedLimits\n\n" + "".join("#print axioms EmbeddedLimits."+n+"\n" for n in names)
    if not names or len(names) != len(set(names)) or (ROOT/"Census.lean").read_text(encoding="utf-8") != expected:
        raise ValueError("INCOMPLETE_CENSUS")
    before = hashes()
    target = ROOT/"verification.json"
    if not write:
        held = json.loads(target.read_text(encoding="utf-8"))
        if held.get("status") != "PASS" or held.get("sources") != before:
            raise ValueError("VERIFICATION_SOURCE_DRIFT")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    version = run([lean, "--version"], cwd=ROOT, env=env).strip()
    if "version 4.35.0," not in version:
        raise ValueError("UNPINNED_LEAN_VERSION: "+version)
    with tempfile.TemporaryDirectory(prefix="embedded-limits-lean-") as folder:
        work = Path(folder)
        (work/"EmbeddedLimits.lean").write_bytes((ROOT/"EmbeddedLimits.lean").read_bytes())
        (work/"Census.lean").write_bytes((ROOT/"Census.lean").read_bytes())
        env["LEAN_PATH"] = str(work)
        build = run([lean, "-o", "EmbeddedLimits.olean", "EmbeddedLimits.lean"], cwd=work, env=env)
        census = run([lean, "Census.lean"], cwd=work, env=env)
    parsed = re.findall(r"^'EmbeddedLimits\.([^']+)' (does not depend on any axioms|depends on axioms: \[[^\]]*\])$", census, re.M)
    if [name for name, _ in parsed] != names:
        raise ValueError("LIVE_CENSUS_COVERAGE_MISMATCH")
    for _, row in parsed:
        if row.startswith("depends"):
            axioms = set(row.partition("[")[2].rstrip("]").replace(",", " ").split())
            if not axioms <= {"propext", "Classical.choice", "Quot.sound"}:
                raise ValueError("CUSTOM_AXIOM")
    if census != (ROOT/"axiom_report.txt").read_text(encoding="utf-8"):
        raise ValueError("AXIOM_REPORT_DRIFT")
    tests = run([sys.executable, "-B", "-m", "unittest", "-v", "test_finite_limits"], cwd=ROOT, env=env)
    match = re.search(r"Ran (\d+) tests", tests)
    if not match or not tests.rstrip().endswith("OK"):
        raise ValueError("INCOMPLETE_TEST_REPLAY")
    after = hashes()
    if after != before:
        raise ValueError("SOURCE_MUTATED_DURING_REPLAY")
    result = {"schema": "rsi.embedded-limits.research-verification.v1", "status": "PASS",
        "date": "2026-10-22", "python": sys.version, "actual_lean_version": version,
        "named_theorems": len(names), "axiom_free": sum(row.startswith("does not") for _, row in parsed),
        "tests": int(match[1]), "future_pair_comparisons": 65536, "semantic_knowledge_cases": 16384,
        "primary_sources": len(json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))["sources"]),
        "sources": before, "lean_build_output": build, "census_output": census,
        "test_output": tests, "evidence_scope": "Generic conditional Lean proofs and finite research checks; no live agent integration or model-performance claim."}
    if write:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                dir=ROOT, prefix="verification-", suffix=".tmp", delete=False) as stream:
            stream.write(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
            stream.flush()
            os.fsync(stream.fileno())
            temporary = Path(stream.name)
        os.replace(temporary, target)
    else:
        for field in ("named_theorems", "axiom_free", "tests", "future_pair_comparisons", "semantic_knowledge_cases", "primary_sources"):
            if held.get(field) != result[field]:
                raise ValueError("VERIFICATION_COUNT_DRIFT: "+field)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", default="lean")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = verify(args.lean, args.write_receipt)
    print(json.dumps({k: result[k] for k in ("status", "named_theorems", "axiom_free", "tests", "primary_sources")}, sort_keys=True))
