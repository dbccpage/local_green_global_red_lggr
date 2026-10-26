"""Lesson 06: A boundary that holds.

Enriched reports keep the query constant on each fiber of this table.
The stage witnesses satisfy the streaming gluing checks, and each supplied
global sample gives Delta_E = 0. This is schema work for a declared query.
See cookbooks/04_swarm_runtime_guard.py for the same shape as a demo.

AuthorityEffect: None.
Standard library only: Python 3.10+.
Used by learn/guides/01_report_collision.md.

Artifact Summary:
1. What it supports: DECODER_VERIFIED on the enriched rows, and COMPOSITION_VERIFIED with contract_status COMPOSABLE_LGGG on the stage trace.
2. What it does not support: A method that makes an arbitrary swarm boundary-sufficient.
3. Narrowest defensible claim: On these rows the fiber receipt status is DECODER_VERIFIED and the audit contract_status is COMPOSABLE_LGGG, with each step classification ZDR.
4. Host duty that remains: The host writes the report fields that the query depends on, and still supplies the global sample from outside.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import BudgetPolicy, StateRef, StreamingAuditMonitor, StreamingFiberMonitor, make_witness  # noqa: E402

from learn.support import dumps, finish, load_json  # noqa: E402

EXPECTED_STATUS = "COMPOSABLE_LGGG"


def prepared() -> dict:
    trace = load_json("06_swarm.json")
    fiber = StreamingFiberMonitor(scope_id=trace["scope_id"])
    for row in trace["observations"]:
        fiber.observe(row["state_id"], row["report"], row["query"])
    fiber_receipt = fiber.get_receipt()

    policy_fields = trace["policy"]
    policy = BudgetPolicy(
        allowed_states=tuple(policy_fields["allowed_states"]),
        max_step=policy_fields["max_step"],
        max_total=policy_fields["max_total"],
        query_scope=policy_fields["query_scope"],
        evaluator_id=policy_fields["evaluator_id"],
        spec_id=policy_fields["spec_id"],
        authority_id=policy_fields["authority_id"],
    )
    first = trace["stages"][0]
    baseline = StateRef(first["source"], first["source_value"])
    audit = StreamingAuditMonitor(policy, baseline)
    step_receipts = []
    for stage in trace["stages"]:
        witness = make_witness(
            policy,
            StateRef(stage["source"], stage["source_value"]),
            StateRef(stage["target"], stage["target_value"]),
            witness_id=stage["witness_id"],
        )
        step_receipts.append(audit.step(witness, global_evaluator_sample=stage["global_sample"]))
    audit_receipt = audit.get_receipt()
    return finish({
        "lesson_id": "06",
        "schema": audit_receipt["schema"],
        "authority_effect": audit_receipt["authority_effect"],
        "status": audit_receipt["contract_status"],
        "audit_status": audit_receipt["status"],
        "composition_certified": audit_receipt["composition_certified"],
        "fiber_status": fiber_receipt["status"],
        "fiber_contract_status": fiber_receipt["contract_status"],
        "step_classifications": [step["classification"] for step in step_receipts],
        "step_defects": [step["defect"] for step in step_receipts],
    })


def your_turn() -> dict:
    # Your turn: add the field your downstream stage branches on, to the report.
    report_a = {"summary": "ship the etl job", "approval_tier": 3}
    report_b = {"summary": "ship the etl job", "approval_tier": 1}
    fiber = StreamingFiberMonitor(scope_id="learn-06-your-turn")
    fiber.observe("task-a", report_a, {"approval_tier": 3})
    fiber.observe("task-b", report_b, {"approval_tier": 1})
    receipt = fiber.get_receipt()
    return finish({
        "lesson_id": "06",
        "schema": receipt["schema"],
        "authority_effect": receipt["authority_effect"],
        "status": receipt["status"],
        "contract_status": receipt["contract_status"],
    })


def main() -> int:
    row = prepared()
    print("Lesson 06 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 06 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
