"""Preregistered runners, separate evidence acquisition, and exact summaries.

Evaluation answers are produced only after a host terminal decision.  The fixed
trace collector is an offline diagnostic acquisition with separately counted
costs, not a continuation that bypasses a stopped interactive host's budget.
"""
from __future__ import annotations

from collections import Counter
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys
import time

from . import ROOT, controller, tools
from .common import canonical, digest, save
from .evidence import EvidenceBook, EvidenceError, branch_event
from .fixtures import FAMILIES, generate_cases
from .host import Host, replay, run_case


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_protocol(root: Path = ROOT, protocol: Path | None = None) -> dict:
    root = Path(root)
    frozen = json.loads((root / "evidence/protocol-freeze.json").read_text(encoding="utf-8"))
    for name, expected in frozen["files"].items():
        if _sha(root / name) != expected:
            raise ValueError("frozen protocol/oracle dependency changed: " + name)
    if protocol is not None and _sha(Path(protocol)) != frozen["files"]["protocol.json"]:
        raise ValueError("requested protocol is not the frozen protocol")
    for split, info in frozen["splits"].items():
        cases = generate_cases(split)
        if len(cases) != info["case_count"] or digest(cases) != info["case_sha256"]:
            raise ValueError("generated split differs from frozen bytes: " + split)
    return frozen


def build_development(root: Path = ROOT) -> dict:
    """Execute two development artifacts before obtaining their oracle labels."""
    from lggr import analyze_descent, verify_descent_certificate
    from lggr.streaming import StreamingFiberMonitor
    from .oracle import judge

    root = Path(root)
    verify_protocol(root)
    target = root / "evidence/development.json"
    bindings = {name: _sha(root / name) for name in
                ("lggr_swarm_lab/fixtures.py", "lggr_swarm_lab/oracle.py", "lggr_swarm_lab/tools.py",
                 "vendor/lggr/descent.py", "vendor/lggr/streaming.py", "evidence/protocol-freeze.json")}
    if target.exists():
        existing = json.loads(target.read_text(encoding="utf-8"))
        if existing.get("source_bindings") == bindings:
            if not verify_descent_certificate(existing["rows"], existing["certificate"]):
                raise ValueError("stored development collision certificate changed")
            if not verify_descent_certificate(existing["refined_rows"], existing["refined_certificate"]):
                raise ValueError("stored development refinement certificate changed")
            expected = existing.pop("receipt_sha256", None)
            if digest(existing) != expected:
                raise ValueError("stored development receipt changed")
            existing["receipt_sha256"] = expected
            return existing
        if (root / "evidence/controller-freeze.json").exists():
            raise ValueError("development evidence dependency changed after controller freeze")
        # Development implementation can evolve before evaluation. Retain the
        # original labelled executions, rather than overwrite their custody.
        save(root / "evidence/development-history" / (_sha(target) + ".json"), existing)
    rows, refined, executions = [], [], []
    monitor = StreamingFiberMonitor(scope_id="executed-development-ledgers.v1")
    for case in generate_cases("development")[:2]:
        proposal = deepcopy(case["scenario"]["worker_proposals"])
        started = time.perf_counter_ns()
        branches = {
            "orders": tools.execute_branch("orders", {k: case["source"][k] for k in ("orders", "customers")}, proposal),
            "refunds": tools.execute_branch("refunds", {"refunds": case["source"]["refunds"]}, proposal),
        }
        output = tools.integrate(branches, proposal["integrator"])
        execution_ns = time.perf_counter_ns() - started
        # The first oracle call occurs only after the actual SQL output exists.
        judgment = judge(case, output, {"action": "development_label"})
        label = judgment["task_correct"]
        if type(label) is not bool:
            raise ValueError("only a completed labelled execution may enter the development table")
        semantics = tools.probe("semantics", case, branches)
        coarse = {"operation": "ledger", "schema": "coarse.v1", "orders": len(case["source"]["orders"]),
                  "refunds": len(case["source"]["refunds"])}
        row = {"state_id": case["case_id"], "report": coarse, "query": label}
        rows.append(row)
        refined.append({**row, "report": {"base": coarse, "semantics": semantics}})
        monitor.observe(row["state_id"], coarse, label, metadata=semantics)
        executions.append({"case_id": case["case_id"], "input": case, "input_sha256": digest(case),
                           "planner": proposal, "branches": branches, "output": output,
                           "output_sha256": digest(output), "semantics_observation": semantics,
                           "query_label": label, "query_label_source": "independent oracle after sqlite.integrate",
                           "expected_output_sha256": judgment["expected_output_sha256"],
                           "executed_tool_attempts": 4, "execution_ns": execution_ns,
                           "cost_scope": "two branch transforms, integration, one semantics probe; excludes Python judge/reasoning"})
    certificate = analyze_descent(rows, scope_id="executed-development-ledgers.v1")
    refined_certificate = analyze_descent(refined, scope_id="development-unit-refinement.v2")
    if not verify_descent_certificate(rows, certificate) or not verify_descent_certificate(refined, refined_certificate):
        raise ValueError("development certificate verification failed")
    synthesized = monitor.synthesize_minimal_refinement(
        candidate_keys=["order_scale_to_cents", "refund_scale_to_cents", "refund_sign"])
    result = {"schema": "swarm-lab.development.v1", "created_utc": _utc(), "source_bindings": bindings,
              "rows": rows, "certificate": certificate, "refined_rows": refined,
              "refined_certificate": refined_certificate, "streaming_collision": monitor.get_receipt(),
              "minimal_refinement": synthesized, "executions": executions,
              "lost_distinction": "order amount scale to cents", "authority_effect": "None",
              "scope": "Exactly two completed development executions; no claim of general sufficiency or current-task failure.",
              "query": "Does the actual proposed ledger equal the independently recomputed task answer?",
              "operational_use": "The certificate motivates acquiring named metadata. It does not reveal the current held-out answer."}
    result["receipt_sha256"] = digest(result)
    save(target, result)
    return result


def production_sources(root: Path = ROOT) -> dict:
    root = Path(root)
    paths = sorted((root / "lggr_swarm_lab").glob("*.py")) + sorted((root / "vendor").rglob("*.py"))
    paths += [root / "protocol.json", root / "evidence/protocol-freeze.json", root / "evidence/development.json"]
    paths += [root / "native_session.py"]
    return {p.relative_to(root).as_posix(): _sha(p) for p in paths}


def freeze_controllers(root: Path = ROOT) -> dict:
    """Create once before evaluation; any later source/evidence change fails."""
    root = Path(root)
    verify_protocol(root)
    target = root / "evidence/controller-freeze.json"
    current = production_sources(root)
    if target.exists():
        record = json.loads(target.read_text(encoding="utf-8"))
        if record.get("files") != current:
            old = record.get("files", {})
            changed = sorted(k for k in set(old) | set(current) if old.get(k) != current.get(k))
            raise ValueError("controller freeze mismatch; preserve the original experiment: " + ", ".join(changed))
        return record
    record = {"schema": "swarm-lab.controller-freeze.v1", "frozen_at_utc": _utc(),
              "phase": "before_first_held_out_run", "files": current,
              "source_set_sha256": digest(current), "authority_effect": "None",
              "rule": "No controller tuning on evaluation outcomes. Changed production source requires a separately identified experiment, preserving this freeze."}
    save(target, record)
    return record


def _normal_decision(decision: dict) -> dict:
    return {"action": decision["action"], "probe": decision.get("probe"), "plan": decision.get("plan"),
            "findings": sorted(({k: f[k] for k in ("code", "status", "detail")} for f in decision["findings"]), key=canonical)}


def _fixed_fingerprint(record: dict) -> str:
    stable = {k: record[k] for k in (
        "input_sha256", "source_run_fingerprint", "public_view", "normalized_decisions", "decisions",
        "complete", "diagnostic_acquisition_cost", "reused_artifacts", "supplemental_candidate")}
    stable["acquisitions"] = [{k: v for k, v in acquisition.items() if k != "elapsed_ns"}
                              for acquisition in record["acquisitions"]]
    return digest(stable)


def collect_fixed_trace(source_run: dict, development: dict) -> dict:
    """Acquire complete permitted evidence outside the interactive comparison.

    Stopped actions stay stopped in the original run. Supplemental effects here
    have a separate diagnostic cost ledger and do not prove online feasibility.
    No independent-oracle answer enters the identical B/C view.
    """
    case = source_run["input"]
    contract, scenario = case["public"]["contract"], case["scenario"]
    plan = deepcopy(scenario["worker_proposals"])
    branches, acquisitions = {}, []

    def acquire(kind, effect, inputs):
        start = time.perf_counter_ns()
        value = effect()
        acquisitions.append({"attempt_id": f"diagnostic-{len(acquisitions) + 1:03d}", "kind": kind,
                             "cost": 1, "source": "offline_sqlite_diagnostic", "input_sha256": digest(inputs),
                             "result": deepcopy(value), "result_sha256": digest(value),
                             "elapsed_ns": time.perf_counter_ns() - start})
        return value

    # Reuse real, preserved worker artifacts, not an expected answer.
    reused = []
    for key, item in source_run["artifacts"].items():
        data = item["data"]
        if item["source"] == "sqlite worker" and isinstance(data, dict) and data.get("branch") in ("orders", "refunds"):
            branches[data["branch"]] = deepcopy(data)
            reused.append({"artifact_id": key, "sha256": item["sha256"]})
    for branch in ("orders", "refunds"):
        if branch not in branches:
            source = {k: case["source"][k] for k in (("orders", "customers") if branch == "orders" else ("refunds",))}
            branches[branch] = acquire("supplemental-worker:" + branch,
                lambda b=branch, s=source: tools.execute_branch(b, s, plan), {"source": source, "planner": plan})
    candidate = source_run.get("candidate")
    if candidate is None:
        candidate = acquire("supplemental-integration", lambda: tools.integrate(branches, plan["integrator"]),
                            {"branches": branches, "proposal": plan["integrator"]})
    observations = {}
    for name in case["public"]["allowed_probes"]:
        # Diagnostic collection includes the same deterministic transient
        # failures, but reports its own acquisition costs outside run budgets.
        for retry in range(scenario.get("probe_failures", {}).get(name, 0)):
            def failed_probe(n=retry):
                with closing(tools.connection(case["source"])) as con:
                    con.execute("SELECT count(*) FROM orders").fetchone()
                return {"tool_error": "fixture transient 503", "attempt": n + 1}
            acquire("probe-failure:" + name, failed_probe, {"probe": name, "source_sha256": digest(case["source"])})
        observations[name] = acquire("probe:" + name, lambda n=name: tools.probe(n, case, branches),
                                     {"probe": name, "source_sha256": digest(case["source"]), "branches_sha256": digest(branches)})
    samples = []
    for raw in scenario.get("negative_evidence", []):
        def auxiliary(raw=raw):
            with closing(tools.connection({})) as con:
                con.execute("CREATE TABLE auxiliary(query_id TEXT,verdict INTEGER)")
                con.execute("INSERT INTO auxiliary VALUES (?,?)", (raw["query_id"], int(raw["global_verdict"])))
                return bool(con.execute("SELECT verdict FROM auxiliary").fetchone()[0])
        verdict = acquire("auxiliary-query", auxiliary, raw)
        samples.append({"query_id": raw["query_id"], "scope": raw.get("scope", "endpoint"),
                        "baseline": raw.get("baseline", 0), "verdict": verdict,
                        "terminal": raw.get("terminal", True), "source": "sqlite.branch_contract"})
    policy = contract.get("policy_version", "policy.v1")
    root_event = branch_event("plan", {"attempts": []}, policy_version=policy, role="planner")
    events = {branch: branch_event(branch, {
        "artifact": branches[branch], "obligations": [o["id"] for o in scenario.get("obligations", []) if o["branch"] == branch],
        "global_samples": samples if branch == "refunds" else [], "attempts": []}, parents=["plan"], policy_version=policy, role=branch)
        for branch in ("orders", "refunds")}
    arrivals = [root_event] + [deepcopy(events[name]) for name in scenario.get("arrival_plan", []) if name in events]
    merged, event_error = None, None
    try:
        merged = EvidenceBook(contract).merge(arrivals)
    except EvidenceError as error:
        event_error = str(error)
    obligations = {o["id"] for o in scenario.get("obligations", [])}
    obligations.update(merged["obligations"] if merged else [])
    for identifier, fact in observations.get("obligation_evidence", {}).items():
        if fact.get("verified") is True:
            obligations.discard(identifier)
    state_path = deepcopy(source_run["summary"]["state_path"])
    complete_state = len(state_path) >= len(scenario["drift_path"])
    # Supplemental artifacts do not invent missing numerical state observations.
    view = {"contract": deepcopy(contract),
            "initial_report": {"operation": "ledger", "schema": "coarse.v1", "orders": len(case["source"]["orders"]), "refunds": len(case["source"]["refunds"])},
            "plan": plan, "observations": observations, "allowed_probes": list(case["public"]["allowed_probes"]),
            "state_path": state_path, "terminal": complete_state and candidate is not None,
            "obligations": sorted(obligations), "transition": deepcopy(scenario["transition"]),
            "global_samples": deepcopy(merged["global_samples"] if merged else []),
            "unsupported_samples": merged.get("unsupported", False) if merged else False,
            "branches_executed": len(branches) == 2,
            "missing_branches": [b for b in ("orders", "refunds") if not merged or b not in {e["event_id"] for e in merged["ordered"]}],
            "event_error": event_error,
            "remaining_attempts": max(0, contract["resource_limit"] - len(source_run["summary"]["attempts"])),
            "exhausted_probes": []}
    decisions, costs = {}, {}
    for mode in ("B", "C"):
        started = time.perf_counter_ns()
        decisions[mode] = controller.decide(deepcopy(view), mode, controller.development_evidence(development))
        costs[mode] = time.perf_counter_ns() - started
    normalized = {mode: _normal_decision(decisions[mode]) for mode in ("B", "C")}
    complete = complete_state and len(branches) == 2 and set(observations) == set(case["public"]["allowed_probes"])
    record = {"schema": "swarm-lab.fixed-trace.v1", "case_id": case["case_id"], "input_sha256": source_run["input_sha256"],
              "source_run_fingerprint": source_run["replay_fingerprint"], "public_view": view, "view_sha256": digest(view),
              "reused_artifacts": reused, "supplemental_candidate": candidate, "acquisitions": acquisitions,
              "original_interactive_attempts": len(source_run["summary"]["attempts"]),
              "diagnostic_acquisition_cost": len(acquisitions), "diagnostic_acquisition_ns": sum(a["elapsed_ns"] for a in acquisitions),
              "cost_scope": "Separate offline diagnostic effects; excluded from interactive A/B/C costs and original host budget. They do not authorize a stopped runtime to continue.",
              "coverage": "complete permitted evidence" if complete else "partial; excluded from complete denominator",
              "complete": complete, "unavailable_required_probes": sorted(set(contract["required_evidence_probes"]) - set(case["public"]["allowed_probes"])),
              "coverage_meaning": "All available probes, branch artifacts and recorded terminal state are supplied identically. An unavailable resolving probe remains explicitly unknown.",
              "decisions": decisions, "normalized_decisions": normalized, "decisions_equal": normalized["B"] == normalized["C"],
              "findings_equal": normalized["B"]["findings"] == normalized["C"]["findings"],
              "controller_ns": costs, "authority_effect": "None"}
    record["comparison_fingerprint"] = _fixed_fingerprint(record)
    return record


def _run_metrics(run: dict, replay_receipt: dict) -> dict:
    attempts = run["summary"]["attempts"]
    by_role = Counter(a["branch"] for a in attempts)
    probes = [a for a in attempts if a["kind"].startswith("probe:")]
    return {**deepcopy(run["metrics"]), "issued_tool_attempts": len(attempts),
            "issued_probe_attempts": len(probes), "issued_repair_attempts": sum(a["kind"] == "repair-plan" for a in attempts),
            "consumed_cost": sum(a["cost"] for a in attempts), "cost_by_role": dict(sorted(by_role.items())),
            "worker_branch_cost": by_role["orders"] + by_role["refunds"],
            "shared_cost": by_role["shared"], "other_role_cost": sum(n for role, n in by_role.items() if role not in ("orders", "refunds", "shared")),
            "observations": [a["kind"].split(":", 1)[1] for a in probes],
            "replay_elapsed_ns": replay_receipt["elapsed_ns"], "replay_passed": replay_receipt["replayed"]}


def _ratio(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator}


def summarize(records: list[dict]) -> dict:
    n = len(records)
    counts = {
        "cases": n, "committed": sum(r["action"] == "commit" for r in records),
        "correct_committed": sum(r["action"] == "commit" and r["judgment"]["task_correct"] is True for r in records),
        "invalid_committed": sum(r["action"] == "commit" and r["judgment"]["task_correct"] is False for r in records),
        "admissible_committed": sum(r["action"] == "commit" and r["judgment"]["admissible"] for r in records),
        "inadmissible_committed": sum(r["action"] == "commit" and not r["judgment"]["admissible"] for r in records),
        "deferred": sum(r["action"] == "defer" for r in records), "blocked": sum(r["action"] == "block" for r in records),
        "correct_candidate_refused": sum(r["action"] != "commit" and r["judgment"]["candidate_correct"] is True for r in records),
        "observed_correct_candidates": sum(r["judgment"]["candidate_correct"] is True for r in records),
        "tasks_with_unresolved_obligations": sum(bool(r["judgment"]["unresolved_obligations"]) for r in records),
        "unresolved_obligations": sum(len(r["judgment"]["unresolved_obligations"]) for r in records),
        "labelled_completed": sum(r["global_verdict"] is not None for r in records),
        "unknown_global": sum(r["global_verdict"] is None for r in records),
    }
    defects = {kind: sum(r["defect_kind"] == kind for r in records) for kind in ("NGD", "ZDR", "PGD", "UNKNOWN")}
    totals = {name: sum(r["metrics"].get(name, 0) or 0 for r in records) for name in (
        "issued_tool_attempts", "issued_probe_attempts", "issued_repair_attempts", "successful_repairs", "consumed_cost",
        "worker_branch_cost", "shared_cost", "other_role_cost", "evidence_bytes", "initial_report_bytes", "final_report_bytes",
        "elapsed_ns", "controller_and_certificate_ns", "replay_elapsed_ns", "certificate_consumed_decisions")}
    return {"counts": counts, "rates": {
        "completion": _ratio(counts["committed"], n), "valid_completion": _ratio(counts["correct_committed"], n),
        "task_correctness_of_committed": _ratio(counts["correct_committed"], counts["committed"]),
        "invalid_output_acceptance": _ratio(counts["invalid_committed"], counts["committed"]),
        "inadmissible_output_acceptance": _ratio(counts["inadmissible_committed"], counts["committed"]),
        "valid_candidate_refusal": _ratio(counts["correct_candidate_refused"], counts["observed_correct_candidates"]),
        "deferred": _ratio(counts["deferred"], n), "blocked": _ratio(counts["blocked"], n)},
        "defects": defects, "defect_denominator": counts["labelled_completed"], "totals": totals,
        "detection_steps": [r["metrics"].get("detection_step") for r in records],
        "model_tokens": None, "model_cost": None, "model_usage_status": "unmeasured; deterministic fixture evaluation",
        "refusal_limit": "Only actually produced candidates are scored. An unexecuted but potentially solvable task is not silently assigned a counterfactual passing artifact."}


def _replay_receipt(run: dict) -> dict:
    started = time.perf_counter_ns()
    try:
        result = replay(run)
    except Exception as error:
        result = {"replayed": False, "error_type": type(error).__name__, "error": str(error)}
    return {**result, "elapsed_ns": time.perf_counter_ns() - started}


def _fresh_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"output directory is not empty; choose a fresh path to preserve previous evidence: {path}")
    path.mkdir(parents=True, exist_ok=True)


def benchmark(protocol: str | Path, output: str | Path, split: str = "evaluation") -> dict:
    protocol, output = Path(protocol).resolve(), Path(output).resolve()
    if split not in ("development", "evaluation"):
        raise ValueError("split must be development or evaluation")
    frozen = verify_protocol(ROOT, protocol)
    development = build_development()
    controller_freeze = freeze_controllers() if split == "evaluation" else None
    _fresh_output(output)
    command = {"argv": sys.argv, "python": sys.version, "platform": platform.platform(), "sqlite": sqlite3.sqlite_version,
               "started_utc": _utc(), "split": split, "exit_code": None, "source_set_sha256": digest(production_sources())}
    save(output / "command-log.json", command)
    records, fixed_records, errors = [], [], []
    try:
        for case in generate_cases(split):
            case_runs = {}
            for mode in ("A", "B", "C"):
                run = run_case(case, mode, development)
                filename = f"runs/{case['case_id']}.{mode}.json"
                save(output / filename, run)
                replay_receipt = _replay_receipt(run)
                save(output / f"replays/{case['case_id']}.{mode}.json", replay_receipt)
                if not replay_receipt["replayed"]:
                    errors.append({"case_id": case["case_id"], "mode": mode, "phase": "host-replay", **replay_receipt})
                record = {"case_id": case["case_id"], "family": case["family"], "mode": mode, "file": filename,
                          "run_id": run["run_id"], "action": run["action"], "status": run["status"], "residual": run["residual"],
                          "judgment": run["judgment"], "local_verdicts": run["local_verdicts"], "global_verdict": run["global_verdict"],
                          "defect": run["defect"], "defect_kind": run["defect_kind"], "metrics": _run_metrics(run, replay_receipt)}
                records.append(record)
                case_runs[mode] = run
            fixed = collect_fixed_trace(case_runs["A"], development)
            fixed["source_run_file"] = f"../runs/{case['case_id']}.A.json"
            fixed["source_run_sha256"] = _sha(output / "runs" / f"{case['case_id']}.A.json")
            started = time.perf_counter_ns()
            repeated = collect_fixed_trace(case_runs["A"], development)
            fixed["replay_elapsed_ns"] = time.perf_counter_ns() - started
            fixed["replay_passed"] = fixed["comparison_fingerprint"] == repeated["comparison_fingerprint"]
            if not fixed["replay_passed"]:
                errors.append({"case_id": case["case_id"], "phase": "fixed-trace-replay", "error": "recomputed evidence/decisions differ"})
            save(output / "fixed-traces" / f"{case['case_id']}.json", fixed)
            fixed_records.append({k: fixed[k] for k in ("case_id", "coverage", "complete", "unavailable_required_probes",
                "decisions_equal", "findings_equal", "normalized_decisions", "diagnostic_acquisition_cost", "diagnostic_acquisition_ns", "controller_ns", "replay_elapsed_ns", "replay_passed")})
        modes = {mode: summarize([r for r in records if r["mode"] == mode]) for mode in ("A", "B", "C")}
        families = {family: {mode: summarize([r for r in records if r["mode"] == mode and r["family"] == family]) for mode in ("A", "B", "C")} for family in FAMILIES}
        pairs = []
        for case in generate_cases(split):
            pair = {r["mode"]: r for r in records if r["case_id"] == case["case_id"]}
            pairs.append({"case_id": case["case_id"], "B_C_actions_equal": pair["B"]["action"] == pair["C"]["action"],
                          "B_C_task_outcomes_equal": pair["B"]["judgment"]["task_correct"] == pair["C"]["judgment"]["task_correct"],
                          "B_C_observations_equal": pair["B"]["metrics"]["observations"] == pair["C"]["metrics"]["observations"],
                          "C_minus_B_issued_attempts": pair["C"]["metrics"]["issued_tool_attempts"] - pair["B"]["metrics"]["issued_tool_attempts"],
                          "A_C_actions_differ": pair["A"]["action"] != pair["C"]["action"],
                          "A_C_task_outcomes_differ": pair["A"]["judgment"]["task_correct"] != pair["C"]["judgment"]["task_correct"]})
        complete = [f for f in fixed_records if f["complete"]]
        results = {"schema": "swarm-lab.results.v1", "split": split, "created_utc": _utc(),
                   "protocol_sha256": _sha(protocol), "protocol_freeze": frozen,
                   "controller_freeze": controller_freeze, "development_receipt_sha256": development["receipt_sha256"],
                   "execution": "deterministic offline fault injection with real SQLite effects",
                   "mode_summary": modes, "family_summary": families, "runs": records,
                   "interactive_pairs": pairs, "fixed_trace_comparisons": fixed_records,
                   "fixed_trace_summary": {"cases": len(fixed_records), "complete_cases": len(complete),
                        "complete_decision_agreement": _ratio(sum(f["decisions_equal"] for f in complete), len(complete)),
                        "complete_findings_agreement": _ratio(sum(f["findings_equal"] for f in complete), len(complete)),
                        "separate_diagnostic_acquisition_cost": sum(f["diagnostic_acquisition_cost"] for f in fixed_records)},
                   "replay_failures": errors, "claim_scope": "Finite preregistered fixture variants, not independent natural model failures or population reliability.",
                   "authority_effect": "None"}
        save(output / "results.json", results)
        command.update(finished_utc=_utc(), exit_code=0 if not errors else 1)
        save(output / "command-log.json", command)
        return results
    except Exception as error:
        command.update(finished_utc=_utc(), exit_code=1, error_type=type(error).__name__, error=str(error))
        save(output / "command-log.json", command)
        raise


def demo(output: str | Path) -> dict:
    output = Path(output).resolve()
    _fresh_output(output)
    development = build_development()
    cases = generate_cases("development")
    ambiguous = cases[1]
    unresolved = next(c for c in cases if c["family"] == "evidence_resolution" and c["variant"] == 1)
    selected = [(cases[0], "C", "correct"), (ambiguous, "A", "coarse-ablation"),
                (ambiguous, "C", "repaired"), (unresolved, "C", "unresolved")]
    summaries = []
    for case, mode, label in selected:
        run = run_case(case, mode, development)
        save(output / (label + ".json"), run)
        check = _replay_receipt(run)
        save(output / (label + ".replay.json"), check)
        summaries.append({"example": label, "file": label + ".json", "case_id": case["case_id"], "mode": mode,
                          "action": run["action"], "task_correct": run["judgment"]["task_correct"],
                          "admissibility": run["judgment"]["admissibility_status"], "residual": run["residual"],
                          "tool_attempts": len(run["summary"]["attempts"]), "replay": check})
    result = {"development_certificate": development["certificate"], "minimal_refinement": development["minimal_refinement"],
              "examples": summaries, "scope": "Four development demonstrations; no held-out result or universal certificate.",
              "authority_effect": "None"}
    save(output / "demo.json", result)
    return result


def replay_file(path: str | Path) -> dict:
    path = Path(path).resolve()
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "swarm-lab.fixed-trace.v1":
        return replay(value)
    source_path = (path.parent / value["source_run_file"]).resolve()
    if _sha(source_path) != value["source_run_sha256"]:
        raise EvidenceError("fixed trace source run bytes changed")
    source_run = json.loads(source_path.read_text(encoding="utf-8"))
    replay(source_run)
    repeated = collect_fixed_trace(source_run, source_run["development"])
    if _fixed_fingerprint(value) != value["comparison_fingerprint"]:
        raise EvidenceError("stored fixed trace content changed")
    if repeated["comparison_fingerprint"] != value["comparison_fingerprint"]:
        raise EvidenceError("fixed trace evidence or decisions changed")
    if digest(value["public_view"]) != value["view_sha256"]:
        raise EvidenceError("fixed public view bytes changed")
    normalized = {mode: _normal_decision(value["decisions"][mode]) for mode in ("B", "C")}
    if normalized != value["normalized_decisions"] or normalized != repeated["normalized_decisions"]:
        raise EvidenceError("fixed trace stored decisions changed")
    return {"replayed": True, "complete": value["complete"], "decisions_equal": value["decisions_equal"],
            "meaning": "Offline identical-evidence interpretation check; original interactive host decision is preserved."}
