"""Lesson 03: A prefix is not an endpoint.

0 -> 1 -> 2 under bound 1 alerts on every_prefix at the second step.
0 -> 1 -> 2 -> 1 can pass an endpoint query and fail every_prefix.
BudgetPolicy defaults to endpoint because that is the source report's question.

AuthorityEffect: None.
Standard library only: Python 3.10+.
See also cookbooks/02_streaming_budget_audit.py.

Artifact Summary:
1. What it supports: A streaming alert when a prefix total leaves the declared bound, and the endpoint/prefix split on a round trip.
2. What it does not support: A detector stronger than the signed totals of the supplied values.
3. Narrowest defensible claim: The prepared streaming receipt has status ALERT and alert reason PREFIX_BUDGET_EXCEEDED.
4. Host duty that remains: The host picks endpoint or every_prefix to match the requirement it actually has.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import BudgetPolicy, StateRef, StreamingAuditMonitor, audit_document, history_document, make_witness  # noqa: E402

from learn.support import dumps, finish, load_json  # noqa: E402

EXPECTED_STATUS = "ALERT"


def _policy(trace: dict, query_scope: str) -> BudgetPolicy:
    return BudgetPolicy(
        allowed_states=tuple(trace["allowed_states"]),
        max_step=trace["max_step"],
        max_total=trace["bound"],
        query_scope=query_scope,
    )


def stream(trace: dict, values: list[int], query_scope: str) -> dict:
    policy = _policy(trace, query_scope)
    states = [StateRef(f"s{i}", value) for i, value in enumerate(values)]
    monitor = StreamingAuditMonitor(policy, states[0])
    last = None
    for index, (source, target) in enumerate(zip(states, states[1:]), start=1):
        witness = make_witness(policy, source, target, witness_id=f"w{index:03d}")
        last = monitor.step(witness, global_evaluator_sample=1)
    if last is None:
        raise RuntimeError("A history needs at least one step")
    return last


def batch(trace: dict, values: list[int], query_scope: str) -> dict:
    policy = _policy(trace, query_scope)
    return audit_document(history_document(values, policy=policy))


def prepared() -> dict:
    trace = load_json("03_histories.json")
    alert = stream(trace, trace["obstruction"], "every_prefix")
    endpoint = batch(trace, trace["round_trip"], "endpoint")
    prefix = batch(trace, trace["round_trip"], "every_prefix")
    return finish({
        "lesson_id": "03",
        "schema": alert["schema"],
        "authority_effect": alert["authority_effect"],
        "status": alert["status"],
        "alert_reasons": alert["alert_reasons"],
        "classification": alert["classification"],
        "cumulative_delta": alert["cumulative_delta"],
        "endpoint_status": endpoint["status"],
        "endpoint_global_verdict": endpoint["arithmetic"]["global_verdict"],
        "endpoint_every_prefix_verdict": endpoint["arithmetic"]["every_prefix_verdict"],
        "prefix_status": prefix["status"],
        "prefix_global_verdict": prefix["arithmetic"]["global_verdict"],
    })


def your_turn() -> dict:
    # Your turn: set query_scope to the requirement you actually have.
    trace = {
        "allowed_states": [0, 1, 2],
        "max_step": 1,
        "bound": 1,
    }
    values = [0, 1, 2, 1]
    query_scope = "endpoint"
    receipt = batch(trace, values, query_scope)
    return finish({
        "lesson_id": "03",
        "schema": receipt["schema"],
        "authority_effect": receipt["authority_effect"],
        "status": receipt["status"],
        "query_scope": query_scope,
        "global_verdict": receipt["arithmetic"]["global_verdict"],
        "every_prefix_verdict": receipt["arithmetic"]["every_prefix_verdict"],
    })


def main() -> int:
    row = prepared()
    print("Lesson 03 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 03 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
