"""Offline reproductions against the byte-preserved reviewed LGGR dependency.

No live client call is issued. The only OpenRouter exercise mocks urlopen and
sleep, supplies a fake key directly, and never resolves credentials.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from dataclasses import asdict, replace
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
from unittest.mock import patch
from urllib.error import HTTPError

LAB = Path(__file__).resolve().parents[2]
VENDOR = LAB / "vendor"
sys.dont_write_bytecode = True
sys.path.insert(0, str(VENDOR))

import lggr
from lggr import BudgetPolicy, StateRef, audit_history, make_witness
from lggr.benchmarks import OpenRouterClient
from lggr.__main__ import main as cli_main
from lggr.streaming import StreamingAuditMonitor, StreamingBaselineComparator


def verify_vendor() -> dict:
    manifest = json.loads((LAB / "evidence/upstream/vendor_manifest.json").read_text())
    for item in manifest["files"]:
        content = (LAB / item["bundled_path"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise RuntimeError(f"Changed upstream dependency: {item['bundled_path']}")
    if not Path(lggr.__file__).is_relative_to(VENDOR):
        raise RuntimeError("The dependency did not import from the pinned vendor directory")
    return manifest


def merge_reproduction() -> dict:
    policy = BudgetPolicy(query_scope="every_prefix")
    s0, s1, s2 = StateRef("s0", 0), StateRef("s1", 1), StateRef("s2", 0)
    up, down = StreamingAuditMonitor(policy, s0), StreamingAuditMonitor(policy, s1)
    up_event = up.step(make_witness(policy, s0, s1, witness_id="up"),
                       global_evaluator_sample=1, step_cost=3)
    down_event = down.step(make_witness(policy, s1, s2, witness_id="down"),
                           global_evaluator_sample=0, step_cost=7)
    down_receipt = down.get_receipt()
    merged = up.merge(down)
    final = up.get_receipt()
    reproduced = (down_receipt["status"] == "OBSTRUCTION_DETECTED"
                  and merged["status"] == "COMPOSITION_VERIFIED"
                  and final["running_cost"] == 3)
    return {"finding_reproduced": reproduced, "up_event": up_event,
            "down_event": down_event, "down_receipt_before_merge": down_receipt,
            "merge_receipt": merged, "merged_receipt": final,
            "expected_unique_attempt_cost": 10,
            "semantic_limit": "The supplied 0 sample has no query/baseline envelope in this API; retain it as source evidence without claiming it automatically answers the composed query."}


def endpoint_reproduction(directory: Path) -> dict:
    cases = {}
    for scope in ("endpoint", "every_prefix"):
        policy = BudgetPolicy(allowed_states=(0, 1, 2), max_step=2, max_total=1,
                              query_scope=scope)
        states = [StateRef(f"s{i}", value) for i, value in enumerate((0, 2, 1))]
        witnesses = [make_witness(policy, a, b, witness_id=f"w{i}")
                     for i, (a, b) in enumerate(zip(states, states[1:]))]
        monitor = StreamingAuditMonitor(policy, states[0])
        events = [monitor.step(w) for w in witnesses]
        batch = audit_history(policy, states[0], witnesses)
        cases[scope] = {"step_receipts": events, "summary": monitor.get_receipt(),
                        "batch": batch}
        if scope == "endpoint":
            policy_path = directory / "endpoint_policy.json"
            events_path = directory / "endpoint_events.jsonl"
            policy_path.write_text(json.dumps(asdict(policy), indent=2) + "\n")
            events_path.write_text("".join(json.dumps(asdict(w)) + "\n" for w in witnesses))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_main(["stream", str(events_path), "--monitor", "audit",
                                 "--policy", str(policy_path)])
            cases[scope]["cli_exit_code"] = code
            cases[scope]["cli_receipt"] = json.loads(buf.getvalue())
    cases["finding_reproduced"] = (
        cases["endpoint"]["step_receipts"][0]["status"] == "ALERT"
        and cases["endpoint"]["summary"]["status"] == "COMPOSITION_VERIFIED"
        and cases["endpoint"]["cli_exit_code"] == 1
        and cases["every_prefix"]["summary"]["status"] == "OBSTRUCTION_DETECTED")
    return cases


def retry_reproduction() -> dict:
    client = OpenRouterClient(api_key="offline-fixture-key", max_completions=2)
    failure = HTTPError("https://offline.invalid/never-issued", 503, "mock unavailable", {}, None)
    error = None
    with patch("lggr.benchmarks.urllib.request.urlopen", side_effect=failure) as network:
        with patch("lggr.benchmarks.time.sleep") as sleeper:
            try:
                client.complete("offline budget regression")
            except RuntimeError as exc:
                error = str(exc)
    return {"finding_reproduced": network.call_count == 3 and client.completion_count == 3,
            "network_access": False, "attempts_mocked": network.call_count,
            "counter": client.completion_count, "configured_cap": client.max_completions,
            "sleep_calls_mocked": sleeper.call_count, "error": error}


def comparator_reproduction() -> dict:
    p = BudgetPolicy(allowed_states=(-2, -1, 0, 1, 2), max_step=1,
                     max_total=1, query_scope="every_prefix")
    s0, s1, s2, s3 = [StateRef(f"s{i}", value) for i, value in enumerate((0, 1, 2, 1))]
    def w(a, b, ident, obligations=()):
        return make_witness(p, a, b, witness_id=ident, obligations=obligations)
    traces = {
        "valid": [w(s0, s1, "ok")],
        "prefix_excursion": [w(s0, s1, "a"), w(s1, s2, "b"), w(s2, s3, "c")],
        "representation_migration": [w(s0, s1, "d"), replace(w(s1, s0, "e"), representation_id="unsupported/v2")],
        "deferred_obligation": [w(s0, s1, "f", ("verify_schema_v2",)), w(s1, s0, "g")],
    }
    monitor = StreamingBaselineComparator(p)
    records = [monitor.compare_trace(name, s0, steps) for name, steps in traces.items()]
    summary = monitor.get_receipt()
    return {"finding_reproduced": summary["faults_localized_online"] == 3,
            "records": records, "summary": summary,
            "baseline_limit": "The baseline checks local flags and endpoint only; disagreement is not independently established accuracy against a complete conventional contract checker."}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("regressions.json"))
    args = parser.parse_args()
    manifest = verify_vendor()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results = {"schema": "grok-swarm-lab.upstream-regressions.v1",
               "upstream_commit": manifest["reviewed_commit"],
               "python": sys.version, "platform": platform.platform(),
               "loaded_dependency": str(Path(lggr.__file__).resolve()),
               "dependency_modified": False, "authority_effect": "None",
               "merge_negative_evidence_and_cost": merge_reproduction(),
               "endpoint_vs_every_prefix": endpoint_reproduction(args.output.parent),
               "retry_cap": retry_reproduction(),
               "comparator": comparator_reproduction()}
    outcomes = {key: value["finding_reproduced"] for key, value in results.items()
                if isinstance(value, dict) and "finding_reproduced" in value}
    results["all_findings_reproduced"] = all(outcomes.values())
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"findings": outcomes, "output": str(args.output)}, indent=2))
    return 0 if results["all_findings_reproduced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
