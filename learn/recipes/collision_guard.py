"""Recipe: report collision guard (guide 01).

Block a handoff when two tasks reach the next agent with the same message and
need different answers. One StreamingFiberMonitor per run does the work.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: Online refusal of a handoff whose report collides with an earlier one on the declared query.
2. What it does not support: A claim that tasks this run never saw are collision-free.
3. Narrowest defensible claim: The demo's second handoff returns REPORT_INSUFFICIENT with the colliding pair; the enriched run returns DECODER_VERIFIED.
4. Host duty that remains: The host chooses which fields are the report and which are the query.
"""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Mapping

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import StreamingFiberMonitor  # noqa: E402

from learn.support import dumps, finish  # noqa: E402

RECIPE_ID = "collision_guard"
EXPECTED_STATUS = "REPORT_INSUFFICIENT"


class HandoffGuard:
    """Wrap your handoff call. ``report`` is what the next agent sees; ``query`` is what it must decide."""

    def __init__(self, run_id: str) -> None:
        self.monitor = StreamingFiberMonitor(scope_id=run_id)

    def check(self, task_id: str, report: Mapping[str, Any], query: Mapping[str, Any]) -> dict[str, Any]:
        receipt = self.monitor.observe(task_id, dict(report), dict(query))
        return {
            "allowed": receipt["status"] != "REPORT_INSUFFICIENT",
            "colliding_pair": receipt.get("colliding_pair"),
            "receipt": receipt,
        }

    def summary(self) -> dict[str, Any]:
        return self.monitor.get_receipt()


def _run(run_id: str, handoffs: list[tuple[str, dict, dict]]) -> dict[str, Any]:
    guard = HandoffGuard(run_id)
    decisions = [guard.check(task_id, report, query) for task_id, report, query in handoffs]
    summary = guard.summary()
    return {
        "allowed": [d["allowed"] for d in decisions],
        "colliding_pair": next((d["colliding_pair"] for d in decisions if d["colliding_pair"]), None),
        "status": summary["status"],
        "contract_status": summary["contract_status"],
        "authority_effect": summary["authority_effect"],
        "schema": summary["schema"],
    }


def demo() -> dict[str, Any]:
    thin = _run("recipe-collision-thin", [
        ("task-a", {"summary": "ship the etl job"}, {"approval_tier": 3}),
        ("task-b", {"summary": "ship the etl job"}, {"approval_tier": 1}),
    ])
    enriched = _run("recipe-collision-enriched", [
        ("task-a", {"summary": "ship the etl job", "approval_tier": 3}, {"approval_tier": 3}),
        ("task-b", {"summary": "ship the etl job", "approval_tier": 1}, {"approval_tier": 1}),
    ])
    return finish({
        "recipe_id": RECIPE_ID,
        "schema": thin["schema"],
        "authority_effect": thin["authority_effect"],
        "status": thin["status"],
        "thin_allowed": thin["allowed"],
        "colliding_pair": thin["colliding_pair"],
        "enriched_status": enriched["status"],
        "enriched_allowed": enriched["allowed"],
    })


def main() -> int:
    row = demo()
    print(dumps(row))
    return 0 if row["status"] == EXPECTED_STATUS else 1


if __name__ == "__main__":
    sys.exit(main())
