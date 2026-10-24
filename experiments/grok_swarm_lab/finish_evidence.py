"""Audit required deliverables and bind release bytes to the clean execution."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from lggr_swarm_lab import ROOT
from lggr_swarm_lab.benchmark import freeze_controllers, production_sources, verify_protocol
from lggr_swarm_lab.common import save

read = lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
protocol = verify_protocol(ROOT)
frozen = freeze_controllers(ROOT)
assert production_sources(ROOT) == frozen["files"]
evaluation = read("evidence/evaluation/results.json")
development = read("evidence/development-release/results.json")
clean = read("evidence/clean-extraction.json")
review = read("evidence/final-adversarial-audit.json")
native = read("evidence/native/run.json")
assert clean["success"] and clean["repeated_evaluation_matches"]
assert not clean["repeated_evaluation_replay_failures"]
assert not review["failures"]
assert len(evaluation["runs"]) == 144 and len(development["runs"]) == 72
assert not evaluation["replay_failures"] and not development["replay_failures"]
assert evaluation["fixed_trace_summary"]["complete_decision_agreement"] == {"numerator":48,"denominator":48}
assert all(s["counts"]["cases"]==4 for family in evaluation["family_summary"].values() for s in family.values())
assert native["action"]=="commit" and native["judgment"]["task_correct"] and native["judgment"]["admissible"]
assert [e["role"] for e in native["events"] if e["agent_execution_mode"]=="native_codex_proposal"]==["planner","orders","refunds"]
assert all(read("evidence/commands/"+name+".json")["exit_code"]==0 for name in
           ("tests-final-v2","evaluation","development-release","demo-release","native-final-v2","supplemental-branch-join","clean-extraction-v2"))
test_log=(ROOT/"evidence/commands/tests-final-v2.txt").read_text(encoding="utf-8")
assert re.search(r"Ran 67 tests",test_log) and re.search(r"\bOK\b",test_log)
bridged = {}
for name, expected in clean["source_and_data_hashes"].items():
    critical = (name.startswith(("lggr_swarm_lab/","vendor/","tests/","evidence/evaluation/","evidence/demo-release/","evidence/native/"))
                or name in ("protocol.json","native_session.py","supplemental_branch_join.py","evidence/controller-freeze.json","evidence/protocol-freeze.json","evidence/development.json"))
    if critical:
        assert sha(ROOT/name)==expected, "release byte differs from clean execution: "+name
        bridged[name]=expected
requirements = [
    ("candidate selection and source interpretation",["protocol.json","SOURCE_MAP.md","evidence/upstream/inspected_source_manifest.json"]),
    ("real dependent SQLite branches and native role demonstration",["lggr_swarm_lab/host.py","lggr_swarm_lab/tools.py","evidence/native/provenance.json","evidence/native/run.json"]),
    ("runtime collision request, refinement, repair and unresolved case",["evidence/development.json","evidence/demo-release/repaired.json","evidence/demo-release/unresolved.json"]),
    ("frozen protocol, oracle, splits and allowed probes",["protocol.json","evidence/protocol-freeze.json","evidence/controller-freeze.json","lggr_swarm_lab/oracle.py"]),
    ("24 development and48 evaluation cases, all12 families",["evidence/development-release/results.json","evidence/evaluation/results.json"]),
    ("fair A/B/C interactive and identical-evidence comparison",["lggr_swarm_lab/controller.py","evidence/evaluation/results.json","evidence/final-adversarial-audit.json"]),
    ("genuine cross-branch compatible and conflicting SQL outputs",["supplemental_branch_join.py","evidence/supplemental-branch-join.json"]),
    ("scope-aware stop/recovery, cost retention, obligations, tamper and replay",["tests/test_adversarial.py","tests/test_native.py","tests/test_sqlite_numbers.py","evidence/commands/tests-final-v2.txt"]),
    ("upstream regressions, unmodified pin, honest original tests and Lean scope",["upstream_findings.md","evidence/upstream/verification_summary.json","evidence/upstream/vendor_manifest.json","evidence/upstream/lean-verification.json"]),
    ("six-part report, exact counts, costs and limitations",["REPORT.md","evidence/evaluation/results.json"]),
    ("one-command entry points, actual command logs, clean execution",["README.md","lggr_swarm_lab/__main__.py","evidence/clean-extraction.json","evidence/commands/clean-extraction-v2.json"]),
    ("source environment and archive construction/checksums",["evidence/environment.json","build_bundle.py","verify_bundle.py"]),
]
items=[]
for name, paths in requirements:
    assert all((ROOT/path).is_file() for path in paths),name
    items.append({"requirement":name,"completed":True,"evidence":paths})
source_paths=sorted(p for p in ROOT.rglob("*.py") if not any(x in p.relative_to(ROOT).parts for x in ("__pycache__","dist","tmp")))
save(ROOT/"evidence/source-manifest.json",{"recorded_utc":datetime.now(timezone.utc).isoformat(),
    "dependency_commit":"6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85","production_freeze_unchanged":True,
    "files":{p.relative_to(ROOT).as_posix():sha(p) for p in source_paths},
    "meaning":"Final executable source bytes, including root native/supplemental/release helpers and tests. Byte identity is not correctness."})
save(ROOT/"evidence/completion-audit.json",{"created_utc":datetime.now(timezone.utc).isoformat(),
    "requirements":items,"all_requirements_accounted_for":True,"frozen_sources_unchanged":True,
    "clean_execution_success":True,"clean_candidate_archive_sha256":clean["archive_sha256"],
    "final_runtime_test_and_trace_bytes_match_clean_execution":True,"bridged_files":bridged,
    "release_difference":"Final archive adds clean-extraction logs, source/completion manifests and history explanation; executed runtime, tests and final traces remain byte-identical.",
    "explicit_limits":["finite deterministic templates, no population inference","B/C reliability tie, C has extra cost","native token/billing usage unmeasured","first causal fault origin unmeasured","cross-branch diagnostic has a separately declared supplemental contract","original upstream failures retained","certificates/hashes do not authenticate or authorize external actions"],
    "authority_effect":"None"})
print(json.dumps({"requirements":len(items),"all_accounted_for":True,"bridged_files":len(bridged),"source_files":len(source_paths)}))
