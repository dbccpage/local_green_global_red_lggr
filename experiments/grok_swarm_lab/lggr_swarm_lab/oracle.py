"""Evaluation-only Python reference, independent of SQLite/application/LGGR code.

The task answer is recomputed from original source rows and protected semantics.
The reference never imports the application transformer, checker, or controller.
Task correctness, evidence admissibility, and lack of a committed output are
different results.  In particular, a defer is never an observed passing label.
"""
from __future__ import annotations

import hashlib
import json


_COLUMNS = ("order_id", "customer_id", "region", "gross_cents", "refund_cents", "net_cents")
_MONEY = ("gross_cents", "refund_cents", "net_cents")


def _bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _integer(value: object, label: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an exact integer")
    return value


def reference_rows(case: dict) -> list[dict]:
    """Interpret source rows using loops/dictionaries and exact integer arithmetic.

    For each original order, use the first customer row with its customer_id;
    normalize gross amount by its declared scale; aggregate each original refund
    exactly once using its declared scale and sign; subtract that magnitude.
    No SQLite query or proposed transformation is used here.
    """
    source, sem = case["source"], case["semantics"]
    if sem.get("customer_resolution") != "first":
        raise ValueError("unsupported reference customer resolution")
    order_scale = _integer(sem["order_scale_to_cents"], "order scale")
    refund_scale = _integer(sem["refund_scale_to_cents"], "refund scale")
    refund_sign = _integer(sem["refund_sign"], "refund sign")
    if order_scale <= 0 or refund_scale <= 0 or refund_sign not in (-1, 1):
        raise ValueError("invalid reference monetary semantics")
    customers = {}
    for row in source["customers"]:
        if row["customer_id"] not in customers:
            customers[row["customer_id"]] = row["region"]
    orders = {}
    for row in source["orders"]:
        if row["order_id"] in orders:
            raise ValueError("source order IDs must be unique")
        if row["customer_id"] not in customers:
            raise ValueError("source order has no authoritative customer")
        orders[row["order_id"]] = row
    refunds = {order_id: 0 for order_id in orders}
    refund_ids = set()
    for row in source["refunds"]:
        if row["refund_id"] in refund_ids:
            raise ValueError("source refund IDs must be unique")
        refund_ids.add(row["refund_id"])
        if row["order_id"] not in orders:
            raise ValueError("source refund refers to an absent order")
        amount = _integer(row["amount"], "refund amount") * refund_scale * refund_sign
        if amount < 0:
            raise ValueError("refund sign metadata fails to normalize a magnitude")
        refunds[row["order_id"]] += amount
    result = []
    for order_id in sorted(orders):
        row = orders[order_id]
        gross = _integer(row["amount"], "order amount") * order_scale
        refund = refunds[order_id]
        result.append({"order_id": order_id, "customer_id": row["customer_id"],
                       "region": customers[row["customer_id"]], "gross_cents": gross,
                       "refund_cents": refund, "net_cents": gross - refund})
    return result


def _artifact_correct(artifact: object, expected: list[dict]) -> bool | None:
    if artifact is None:
        return None
    if not isinstance(artifact, list) or len(artifact) != len(expected):
        return False
    for row in artifact:
        if not isinstance(row, dict) or set(row) != set(_COLUMNS):
            return False
        if any(type(row[name]) is not int for name in _MONEY):
            return False
        if any(type(row[name]) is not str for name in ("order_id", "customer_id", "region")):
            return False
    # Ordering and multiplicity are part of the output contract.
    return artifact == expected


def judge(case: dict, artifact_or_none: list[dict] | None, trace_summary: dict | None = None) -> dict:
    """Score a completed run after controller decisions are irrevocably recorded.

    ``artifact_or_none`` is the committed output, or a completed development
    execution being labelled.  A deferred/blocked runtime must pass None; its
    candidate, when one exists, goes in ``trace_summary['candidate_rows']``.
    Admissibility is reconstructed from factual summary fields, never from a
    controller finding, LGGR verdict, family name, or injected expected label.
    This finite laboratory judge does not authenticate external producers.
    """
    trace = trace_summary or {}
    expected = reference_rows(case)
    contract = case["public"]["contract"]
    problems: list[tuple[str, str]] = []

    def problem(status: str, reason: str) -> None:
        item = (status, reason)
        if item not in problems:
            problems.append(item)

    observations = trace.get("observations", [])
    observed = {}
    for obs in observations:
        if not isinstance(obs, dict) or not isinstance(obs.get("probe"), str):
            problem("malformed", "malformed_observation")
            continue
        result = obs.get("result")
        if result is None or (isinstance(result, dict) and (result.get("error") or result.get("tool_error"))):
            continue
        if obs["probe"] not in case["public"]["allowed_probes"]:
            problem("unsupported", "observation_outside_allowed_probe_set")
        if not obs.get("source"):
            problem("unknown", "observation_source_missing")
        observed[obs["probe"]] = result
    for probe in contract.get("required_evidence_probes", []):
        if probe not in observed:
            problem("unknown", "missing_evidence:" + probe)
    semantics_observation = observed.get("semantics")
    if semantics_observation is not None:
        fields = ("order_scale_to_cents", "refund_scale_to_cents", "refund_sign")
        if not isinstance(semantics_observation, dict) or any(
            type(semantics_observation.get(k)) is not int or semantics_observation.get(k) != case["semantics"][k]
            for k in fields
        ):
            problem("malformed", "semantic_evidence_mismatch")

    attempts = {}
    consumed_cost = 0
    for attempt in trace.get("attempts", []):
        if not isinstance(attempt, dict) or not isinstance(attempt.get("attempt_id"), str):
            problem("malformed", "malformed_attempt")
            continue
        if not attempt.get("issued", False):
            continue
        key = attempt["attempt_id"]
        if key in attempts:
            if attempts[key] != attempt:
                problem("malformed", "conflicting_attempt_replay")
            continue
        attempts[key] = attempt
        cost = attempt.get("cost")
        if type(cost) is not int or cost < 0:
            problem("malformed", "invalid_consumption_cost")
            continue
        consumed_cost += cost
    if not attempts:
        problem("unknown", "missing_execution_cost_evidence")
    if consumed_cost > contract["resource_limit"]:
        problem("obstructed", "shared_resource_limit_exceeded")

    path = trace.get("state_path", [])
    terminal = (artifact_or_none is not None or trace.get("candidate_rows") is not None
                or trace.get("terminal", False) is True)
    if not path:
        problem("unknown", "state_path_missing")
    elif any(type(state) is not int for state in path):
        problem("malformed", "state_path_not_integer")
    else:
        if path[0] != contract["baseline"]:
            problem("obstructed", "state_baseline_mismatch")
        if any(abs(b - a) > contract["max_step"] for a, b in zip(path, path[1:])):
            problem("obstructed", "local_step_bound_exceeded")
        if contract["query_scope"] == "every_prefix":
            if any(abs(state - contract["baseline"]) > contract["max_total"] for state in path):
                problem("obstructed", "every_prefix_bound_exceeded")
        elif contract["query_scope"] == "endpoint":
            if not terminal:
                problem("unknown", "terminal_endpoint_not_observed")
            elif abs(path[-1] - contract["baseline"]) > contract["max_total"]:
                problem("obstructed", "terminal_endpoint_bound_exceeded")
        else:
            problem("unsupported", "unknown_query_scope")

    source_obligations = {item["id"]: item for item in case["scenario"].get("obligations", [])}
    outstanding = set(source_obligations)
    available_facts = observed.get("obligation_evidence", {})
    for event in trace.get("obligation_events", []):
        if not isinstance(event, dict) or not isinstance(event.get("id"), str):
            problem("malformed", "malformed_obligation_event")
            continue
        identifier = event["id"]
        if event.get("op") == "open":
            outstanding.add(identifier)
        elif event.get("op") == "discharge":
            evidence = event.get("evidence")
            fact = available_facts.get(identifier) if isinstance(available_facts, dict) else None
            source = source_obligations.get(identifier, {})
            valid = (source.get("discharge_available") is True and isinstance(evidence, dict)
                     and evidence.get("verified") is True and evidence.get("source") == "sqlite.obligation_evidence"
                     and fact == evidence)
            if valid:
                outstanding.discard(identifier)
            else:
                problem("malformed", "invalid_obligation_discharge:" + identifier)
        else:
            problem("malformed", "unknown_obligation_operation")
    if outstanding:
        problem("unknown", "unresolved_obligations")

    transition = case["scenario"].get("transition", {"kind": "none"})
    if transition.get("kind") == "unsupported":
        problem("unsupported", "unsupported_semantic_transition")
    elif transition.get("kind") == "validated":
        matching = [event for event in trace.get("transitions", [])
                    if event.get("from_version") == transition["from_version"]
                    and event.get("to_version") == transition["to_version"]]
        migration = observed.get("migration")
        valid = (isinstance(migration, dict) and migration.get("validated") is True
                 and migration.get("transition") == transition
                 and any(event.get("validated") is True and event.get("evidence") == migration for event in matching))
        if not valid:
            problem("unknown", "transition_validation_missing")
    for event in trace.get("transitions", []):
        if event.get("from_version") != event.get("to_version") and transition.get("kind") == "none":
            problem("unsupported", "undeclared_semantic_transition")

    arrivals = {}
    roles = set()
    for event in trace.get("arrival_events", []):
        if not isinstance(event, dict) or not isinstance(event.get("event_id"), str):
            problem("malformed", "malformed_arrival_event")
            continue
        key = event["event_id"]
        if key in arrivals and arrivals[key] != event:
            problem("malformed", "conflicting_event_replay")
        arrivals[key] = event
        roles.add(event.get("role"))
        if not event.get("payload_hash"):
            problem("unknown", "arrival_payload_hash_missing")
    for role in contract.get("required_event_roles", []):
        if role not in roles:
            problem("unknown", "missing_branch_event:" + role)
    # Arrival order does not determine causal order.  Check cycles among the
    # supplied fragment; full parent closure and payload hashes are replay duties.
    visiting, visited = set(), set()

    def cycle(key: str) -> bool:
        if key in visiting:
            return True
        if key in visited:
            return False
        visiting.add(key)
        for parent in arrivals[key].get("parent_ids", []):
            if parent in arrivals and cycle(parent):
                return True
        visiting.remove(key)
        visited.add(key)
        return False

    if any(cycle(key) for key in arrivals):
        problem("malformed", "cyclic_causal_events")

    retained_samples = trace.get("negative_evidence", [])
    for query_id in contract.get("required_auxiliary_queries", []):
        originals = [sample for sample in case["scenario"].get("negative_evidence", []) if sample["query_id"] == query_id]
        for sample in originals:
            retained = any(
                isinstance(item, dict) and item.get("query_id") == sample["query_id"]
                and item.get("scope") == sample.get("scope", "endpoint")
                and item.get("baseline") == sample.get("baseline", 0)
                and item.get("terminal") is sample.get("terminal", True)
                and item.get("verdict") is sample["global_verdict"]
                and item.get("source") == "sqlite.branch_contract"
                for item in retained_samples
            )
            if not retained:
                problem("unknown", "missing_scoped_source_sample:" + query_id)
            if sample["global_verdict"] is False:
                problem("obstructed", "auxiliary_requirement_false:" + query_id)

    priority = {"malformed": 4, "unsupported": 3, "obstructed": 2, "unknown": 1}
    status = max((item[0] for item in problems), key=lambda x: priority[x]) if problems else "admissible"
    return {
        "task_correct": _artifact_correct(artifact_or_none, expected),
        "candidate_correct": _artifact_correct(trace.get("candidate_rows"), expected),
        "admissible": not problems, "admissibility_status": status,
        "admissibility_reasons": [reason for _, reason in problems],
        "unresolved_obligations": sorted(outstanding), "consumed_cost": consumed_cost,
        "expected_output_sha256": hashlib.sha256(_bytes(expected)).hexdigest(),
        "expected_row_count": len(expected),
        "truth_provenance": "Independent integer Python interpretation of original source rows and protected monetary metadata; no application, SQL transform, LGGR verdict or controller imports.",
        "scope": "This frozen finite synthetic fixture and declared local laboratory contract only.",
        "authority_effect": "None",
    }
