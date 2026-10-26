"""Lesson 09: The pass comes from outside.

A declaration whose global sample comes from the proposer is rejected before
any monitor runs. examples/authority_changed.json yields AUTHORITY_REQUIRED.
examples/open_obligation.json keeps the obligation and yields WITNESS_INCOMPLETE
on the batch witness audit.

The stage that proposes a change is not the stage that supplies the global
sample. A panel the swarm selects is evidence the host may read. It is not a
grant. AuthorityEffect remains the string None.

AuthorityEffect: None.
Standard library only: Python 3.10+.
Used by learn/guides/02_authority_firewall.md.

Artifact Summary:
1. What it supports: Rejection of a proposer-supplied global sample, the authority fixture, and the open-obligation fixture.
2. What it does not support: An API that clears obligations, or a self-signed pass.
3. Narrowest defensible claim: The prepared adapter receipt status is GLOBAL_SAMPLE_REJECTED. The authority fixture status is AUTHORITY_REQUIRED. The obligation fixture status is WITNESS_INCOMPLETE and the obligation string is still on the receipt.
4. Host duty that remains: The host supplies the global sample from outside, and reads unresolved_obligations even when a streaming summary looks green.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import audit_document  # noqa: E402

from learn.harness_adapter import wire_tool_loop  # noqa: E402
from learn.support import dumps, finish, load_json, load_repo_json  # noqa: E402

EXPECTED_STATUS = "GLOBAL_SAMPLE_REJECTED"


def _external_declaration() -> dict:
    return {
        "scope_id": "learn-09-external",
        "query_scope": "endpoint",
        "bound": 1,
        "global_sample_source": "external",
        "authority_id": "external-owner/v1",
        "evaluator_id": "bounded-step/v1",
        "policy_id": "budget-policy/v1",
        "allowed_states": [0, 1, 2],
        "max_step": 1,
    }


def prepared() -> dict:
    trace = load_json("09_outside.json")
    rejected = wire_tool_loop(
        trace["proposer_declaration"],
        [{
            "before": {"state_id": "s0", "value": 0},
            "after": {"state_id": "s1", "value": 1},
            "global_sample": 1,
            "global_sample_source": "proposer",
        }],
    )
    authority = audit_document(load_repo_json(trace["authority_example"]))
    obligation = audit_document(load_repo_json(trace["obligation_example"]))
    return finish({
        "lesson_id": "09",
        "schema": rejected[0]["lesson_schema"],
        "authority_effect": rejected[0]["authority_effect"],
        "status": rejected[0]["status"],
        "monitor_receipt": rejected[0]["monitor_receipt"],
        "authority_status": authority["status"],
        "authority_effect_on_audit": authority["authority_effect"],
        "obligation_status": obligation["status"],
        "unresolved_obligations": obligation["unresolved_obligations"],
    })


def your_turn() -> dict:
    # Your turn: keep global_sample_source external, and name your own steps.
    # The sample below is a stand-in for a checker that is not the proposer.
    steps = [
        {
            "before": {"state_id": "s0", "value": 0},
            "after": {"state_id": "s1", "value": 1},
            "signed_delta": 1,
            "global_sample": 1,
            "global_sample_source": "external",
        },
        {
            "before": {"state_id": "s1", "value": 1},
            "after": {"state_id": "s2", "value": 0},
            "signed_delta": -1,
            "global_sample": 1,
            "global_sample_source": "external",
            "obligations": ["host-still-owes-this"],
        },
    ]
    receipts = wire_tool_loop(_external_declaration(), steps)
    summary = receipts[-1]
    return finish({
        "lesson_id": "09",
        "schema": summary["lesson_schema"],
        "authority_effect": summary["authority_effect"],
        "status": summary["status"],
        "unresolved_obligations": summary["monitor_receipt"]["unresolved_obligations"],
        "step_statuses": [item["status"] for item in receipts[:-1]],
    })


def main() -> int:
    row = prepared()
    print("Lesson 09 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 09 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
