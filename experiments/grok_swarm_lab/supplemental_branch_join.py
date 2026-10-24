"""Separate, finite SQL demonstration of a genuinely cross-branch invariant.

This does not change the frozen ledger task: negative net amounts remain valid
arithmetic there. The additional contract here forbids refunds above gross.
The A/B/C names identify supplemental guard policies, not new benchmark runs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import threading
import time


ROOT = Path(__file__).resolve().parent
ORIGINAL_CONNECT = sqlite3.connect
SQL_CONTEXT = threading.local()
JOIN_SQL = """SELECT g.order_id, g.gross_cents,
       coalesce(r.refund_cents, 0) AS refund_cents,
       g.gross_cents - coalesce(r.refund_cents, 0) AS net_cents
FROM gross g
LEFT JOIN (
    SELECT order_id, sum(refund_cents) AS refund_cents
    FROM refunded GROUP BY order_id
) r ON g.order_id = r.order_id
WHERE coalesce(r.refund_cents, 0) > g.gross_cents
ORDER BY g.order_id"""


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def object_hash(value):
    return hashlib.sha256(encode(value).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def independent_reference(payload):
    """Pure Python reference, executed in a separate process from raw inputs.

    No SQLite, application transform, controller, checker, or oracle is used.
    The subprocess receives no mode, decision, candidate rows, or expected label.
    """
    source, semantics = payload["source"], payload["semantics"]
    customers = {}
    for row in source["customers"]:
        customers.setdefault(row["customer_id"], row["region"])
    refunds = {}
    for row in source["refunds"]:
        amount = row["amount"] * semantics["refund_scale_to_cents"] * semantics["refund_sign"]
        refunds[row["order_id"]] = refunds.get(row["order_id"], 0) + amount
    rows, violations = [], []
    for row in sorted(source["orders"], key=lambda item: item["order_id"]):
        gross = row["amount"] * semantics["order_scale_to_cents"]
        refund = refunds.get(row["order_id"], 0)
        rows.append({"order_id": row["order_id"], "customer_id": row["customer_id"],
                     "region": customers[row["customer_id"]], "gross_cents": gross,
                     "refund_cents": refund, "net_cents": gross - refund})
        if refund > gross:
            violations.append({"order_id": row["order_id"], "gross_cents": gross,
                               "refund_cents": refund, "net_cents": gross - refund})
    return {"rows": rows, "violations": violations,
            "additional_contract_satisfied": len(violations) == 0,
            "input_sha256": object_hash(payload),
            "implementation": "separate-process Python integer loops over original inputs"}


def traced_connect(*args, **kwargs):
    connection = ORIGINAL_CONNECT(*args, **kwargs)
    statements = getattr(SQL_CONTEXT, "statements", None)
    if statements is not None:
        connection.set_trace_callback(statements.append)
    return connection


def traced_call(function, *args):
    statements = []
    SQL_CONTEXT.statements = statements
    try:
        result = function(*args)
    finally:
        del SQL_CONTEXT.statements
    return result, statements


def local_check(branch, source_slice, artifact):
    """Only this branch's source slice and output participate in these checks."""
    key = "order_id" if branch == "orders" else "refund_id"
    money = "gross_cents" if branch == "orders" else "refund_cents"
    rows = artifact["rows"]
    source_ids = [row[key] for row in source_slice[branch]]
    output_ids = [row[key] for row in rows]
    checks = {"complete": Counter(source_ids) == Counter(output_ids),
              "unique": len(output_ids) == len(set(output_ids)),
              "nonnegative_integer_amounts": all(type(row[money]) is int and row[money] >= 0 for row in rows),
              "tool_schema_pass": artifact["local_pass"]}
    return {"checks": checks, "pass": all(checks.values()),
            "input_scope": sorted(source_slice), "source_ids": source_ids,
            "output_ids": output_ids}


def join_guard(branches):
    """A real relational query over both actual worker outputs."""
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    try:
        con.executescript("CREATE TABLE gross(order_id TEXT, gross_cents INTEGER);"
                          "CREATE TABLE refunded(order_id TEXT, refund_cents INTEGER);")
        con.executemany("INSERT INTO gross VALUES (?, ?)",
                        [(row["order_id"], row["gross_cents"]) for row in branches["orders"]["rows"]])
        con.executemany("INSERT INTO refunded VALUES (?, ?)",
                        [(row["order_id"], row["refund_cents"]) for row in branches["refunds"]["rows"]])
        violations = [dict(row) for row in con.execute(JOIN_SQL)]
        return {"pass": not violations, "violations": violations, "sql": JOIN_SQL,
                "source": "SQLite relational query over both preserved branch outputs"}
    finally:
        con.close()


def execute_policy(source, planner, mode):
    from lggr_swarm_lab.common import SharedBudget
    from lggr_swarm_lab import tools

    tick = time.perf_counter_ns()
    budget = SharedBudget(4)
    barrier = threading.Barrier(2)

    def worker(branch):
        permitted_slice = ({"orders": source["orders"], "customers": source["customers"]}
                           if branch == "orders" else {"refunds": source["refunds"]})
        permit = budget.reserve("sqlite_transform_and_branch_local_validation", branch)
        ready_ns = time.perf_counter_ns()
        barrier.wait(timeout=10)
        start_ns = time.perf_counter_ns()
        artifact, statements = traced_call(tools.execute_branch, branch, permitted_slice, planner)
        end_ns = time.perf_counter_ns()
        local = local_check(branch, permitted_slice, artifact)
        return {"permit": permit, "artifact": artifact, "local_validation": local,
                "sql_statements": statements, "thread_id": threading.get_ident(),
                "ready_ns": ready_ns, "transform_start_ns": start_ns,
                "transform_end_ns": end_ns, "elapsed_transform_ns": end_ns - start_ns}

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="join-worker") as executor:
        futures = {branch: executor.submit(worker, branch) for branch in ("orders", "refunds")}
        workers = {branch: future.result() for branch, future in futures.items()}
    branches = {branch: worker["artifact"] for branch, worker in workers.items()}
    local_pass = all(worker["local_validation"]["pass"] for worker in workers.values())
    permit = budget.reserve("sqlite_integrate", "shared")
    candidate, integration_sql = traced_call(tools.integrate, branches, planner["integrator"])
    integration = {"permit": permit, "rows": candidate, "sql_statements": integration_sql}
    guard = None
    if mode in ("B", "C"):
        permit = budget.reserve("sqlite_additional_join_contract", "shared")
        result, guard_sql = traced_call(join_guard, branches)
        guard = {"permit": permit, "result": result, "sql_statements": guard_sql}
    action = "commit" if local_pass and (guard is None or guard["result"]["pass"]) else "block"
    decision = {"action": action, "local_pass": local_pass,
                "additional_contract_checked": guard is not None,
                "basis": "branch-local validation" if mode == "A" else "branch-local validation plus identical SQL join guard"}
    decision_recorded_ns = time.perf_counter_ns()
    overlap = max(0, min(worker["transform_end_ns"] for worker in workers.values()) -
                  max(worker["transform_start_ns"] for worker in workers.values()))
    return {"mode": mode, "workers": workers, "integration": integration, "guard": guard,
            "decision": decision, "decision_sha256": object_hash(decision),
            "decision_recorded_ns": decision_recorded_ns,
            "committed_rows": candidate if action == "commit" else None,
            "concurrency": {"executor_workers": 2, "rendezvous_participants": 2,
                            "distinct_worker_threads": len({worker["thread_id"] for worker in workers.values()}),
                            "observed_transform_call_overlap_ns": overlap},
            "cost": {"budget_limit": budget.limit, "issued_attempts": budget.attempts,
                     "attempt_count": len(budget.attempts), "remaining": budget.remaining,
                     "branch_attempts": sum(attempt["branch"] != "shared" for attempt in budget.attempts),
                     "shared_attempts": sum(attempt["branch"] == "shared" for attempt in budget.attempts),
                     "host_elapsed_ns_before_reference": decision_recorded_ns - tick}}


def verify_frozen_sources():
    receipt = ROOT / "evidence/controller-freeze.json"
    frozen = json.loads(receipt.read_text(encoding="utf-8"))
    mismatches = [path for path, sha in frozen["files"].items() if file_hash(ROOT / path) != sha]
    if mismatches:
        raise RuntimeError("existing controller freeze changed: " + ", ".join(mismatches))
    return {"manifest_sha256": file_hash(receipt), "files_checked": len(frozen["files"]), "match": True}


def run(output):
    if output.exists():
        raise RuntimeError("supplemental evidence already exists; choose a new output")
    logs = output.parent / (output.stem + "-logs")
    if logs.exists():
        raise RuntimeError("supplemental logs already exist; choose a new output")
    before = verify_frozen_sources()
    started = datetime.now(timezone.utc).isoformat()
    semantics = {"order_scale_to_cents": 1, "refund_scale_to_cents": 1, "refund_sign": 1,
                 "customer_resolution": "first"}
    planner = {"orders": {"operation": "orders", "scale_to_cents": 1, "join_mode": "first", "omit_last": False},
               "refunds": {"operation": "refunds", "scale_to_cents": 1, "sign": 1, "omit_last": False, "duplicate": False},
               "integrator": {"operation": "integrate", "refund_multiplier": 1}}
    cases = []
    sqlite3.connect = traced_connect
    try:
        for name, refund in (("compatible", 50), ("overrefund", 150)):
            source = {"customers": [{"customer_id": "c0", "region": "north"}, {"customer_id": "c1", "region": "south"}],
                      "orders": [{"order_id": "o0", "customer_id": "c0", "amount": 100}, {"order_id": "o1", "customer_id": "c1", "amount": 200}],
                      "refunds": [{"refund_id": "r0", "order_id": "o0", "amount": refund}, {"refund_id": "r1", "order_id": "o1", "amount": 40}]}
            runs = [execute_policy(source, planner, mode) for mode in ("A", "B", "C")]
            # Each policy's complete decision exists before independent truth is computed.
            reference_input = {"source": source, "semantics": semantics}
            reference_start = time.perf_counter_ns()
            command = [sys.executable, str(Path(__file__).resolve()), "--reference"]
            process = subprocess.run(command, input=encode(reference_input), text=True,
                                     capture_output=True, check=False, timeout=30)
            reference_elapsed = time.perf_counter_ns() - reference_start
            if process.returncode:
                raise RuntimeError("independent reference failed: " + process.stderr)
            reference = json.loads(process.stdout)
            for run_record in runs:
                assert run_record["decision_recorded_ns"] < reference_start
                assert object_hash(run_record["decision"]) == run_record["decision_sha256"]
                candidate_correct = run_record["integration"]["rows"] == reference["rows"]
                action = run_record["decision"]["action"]
                run_record["independent_outcome"] = {
                    "candidate_arithmetic_correct": candidate_correct,
                    "committed_arithmetic_correct": candidate_correct if action == "commit" else None,
                    "additional_contract_satisfied": reference["additional_contract_satisfied"],
                    "committed_additional_contract_valid": reference["additional_contract_satisfied"] if action == "commit" else None,
                    "host_guard_matches_reference": None if run_record["guard"] is None else run_record["guard"]["result"]["violations"] == reference["violations"]}
                assert candidate_correct and run_record["decision"]["local_pass"]
                assert run_record["concurrency"]["distinct_worker_threads"] == 2
                expected_action = "commit" if run_record["mode"] == "A" or reference["additional_contract_satisfied"] else "block"
                assert action == expected_action
                assert run_record["independent_outcome"]["host_guard_matches_reference"] is not False
                statements = []
                for branch, worker in run_record["workers"].items():
                    statements.extend(["-- worker: " + branch, *worker["sql_statements"]])
                statements.extend(["-- integration", *run_record["integration"]["sql_statements"]])
                if run_record["guard"]:
                    statements.extend(["-- additional join guard", *run_record["guard"]["sql_statements"]])
                sql_path = logs / (name + "-" + run_record["mode"] + ".sql")
                sql_path.parent.mkdir(parents=True, exist_ok=True)
                sql_path.write_text("\n".join(statements) + "\n", encoding="utf-8")
                run_record["sql_log"] = {"path": str(sql_path.relative_to(ROOT)), "sha256": file_hash(sql_path)}
                run_record["cost"]["retained_execution_artifact_bytes"] = len(encode(run_record).encode("utf-8"))
            assert runs[1]["decision"] == runs[2]["decision"]
            assert runs[1]["guard"]["result"] == runs[2]["guard"]["result"]
            cases.append({"case_id": name, "source": source, "source_sha256": object_hash(source),
                          "semantics": semantics, "planner": planner, "runs": runs,
                          "reference": reference,
                          "reference_execution": {"argv": command, "input_sha256": object_hash(reference_input),
                                                  "stdout": process.stdout, "stderr": process.stderr,
                                                  "exit_code": process.returncode, "elapsed_ns": reference_elapsed,
                                                  "started_after_all_host_decisions": True,
                                                  "not_charged_to_controller_budget": True}})
    finally:
        sqlite3.connect = ORIGINAL_CONNECT
    after = verify_frozen_sources()
    assert before == after
    sources = ["supplemental_branch_join.py", "lggr_swarm_lab/tools.py", "lggr_swarm_lab/common.py",
               "protocol.json", "lggr_swarm_lab/fixtures.py", "lggr_swarm_lab/oracle.py"]
    report = {"kind": "supplemental-cross-branch-SQL-demonstration", "schema_version": 1,
              "authority_effect": "None", "started_utc": started,
              "finished_utc": datetime.now(timezone.utc).isoformat(),
              "scope": {"cases": 2, "policy_runs": 6,
                        "additional_contract": "For each order, summed normalized refunds must not exceed normalized gross.",
                        "original_ledger_truth_unchanged": True,
                        "included_in_frozen_72_case_benchmark": False,
                        "timing_provenance": "Design requested before held-out evaluation; supplemental execution occurred after it. No production sources or controller policies were changed.",
                        "policies": "A uses branch-local validation. B/C are identical complete supplemental SQL guards; these are explicit local policy adapters, not frozen controller evaluation runs.",
                        "claims": "Finite actual-SQL cross-branch conflict and shared permit accounting only. No LGGR superiority, cochain interpretation, or held-out generalization claim.",
                        "runtime": "Deterministic host proposals and real concurrent SQLite transforms; no live model/API calls.",
                        "concurrency": "Two independent executor threads rendezvous before each transform; observed transform-call overlap is reported, not assumed.",
                        "cost_units": "One shared permit per issued branch transform including local validation, integration, or join guard. Static proposal construction and host bookkeeping are uncharged; independent reference subprocess cost is reported separately.",
                        "trace_instrumentation": "Process-local sqlite3.connect wrapper installs trace callbacks; existing tool source and SQL results are unchanged.",
                        "artifact_bytes": "Canonical serialized per-run evidence before insertion of this byte-count field; excludes the enclosing source/reference report and duplicate SQL log files."},
              "environment": {"python": sys.version, "platform": platform.platform(), "sqlite": sqlite3.sqlite_version},
              "source_sha256": {path: file_hash(ROOT / path) for path in sources},
              "controller_freeze_before": before, "controller_freeze_after": after,
              "cases": cases,
              "checks": {"all_twelve_branch_local_validations_pass": True,
                         "all_six_candidates_have_independently_correct_arithmetic": True,
                         "A_commits_compatible_and_overrefund": True,
                         "B_and_C_both_commit_compatible_and_block_overrefund": True,
                         "B_and_C_join_findings_and_decisions_equal": True,
                         "references_computed_after_decisions_from_original_inputs_only": True,
                         "frozen_source_hashes_unchanged": True}}
    write_json(output, report)
    receipt = {"evidence_path": str(output.relative_to(ROOT)), "evidence_sha256": file_hash(output),
               "script_sha256": file_hash(__file__), "policy_runs": 6, "case_count": 2,
               "checks_passed": all(report["checks"].values()),
               "attempts_by_mode": {mode: sum(run["cost"]["attempt_count"] for case in cases for run in case["runs"] if run["mode"] == mode) for mode in ("A", "B", "C")},
               "observed_transform_overlap_all_six_runs": all(run["concurrency"]["observed_transform_call_overlap_ns"] > 0 for case in cases for run in case["runs"])}
    write_json(logs / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/supplemental-branch-join.json")
    args = parser.parse_args()
    if args.reference:
        print(encode(independent_reference(json.load(sys.stdin))))
    else:
        run(args.output.resolve())


if __name__ == "__main__":
    main()
