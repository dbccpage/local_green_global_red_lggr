"""Lesson 01: Same summary, different job.

Two handoffs share a report and differ on the downstream query. The fiber
monitor returns the colliding pair. The your-turn dict adds the field that
splits those reports on this table.

AuthorityEffect: None.
Standard library only: Python 3.10+.
Used by learn/guides/01_report_collision.md.
See also cookbooks/01_online_fiber_monitoring.py.

Artifact Summary:
1. What it supports: Online detection of a report collision on a supplied two-row handoff.
2. What it does not support: A claim that unobserved tasks are collision-free.
3. Narrowest defensible claim: The prepared receipt status is REPORT_INSUFFICIENT and contract_status is OBSTRUCTED_LGGR, with the colliding pair named.
4. Host duty that remains: The host chooses which fields are the report and which are the query. A decoder is certified only on the rows submitted.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import StreamingFiberMonitor  # noqa: E402

from learn.support import dumps, finish, load_json  # noqa: E402

EXPECTED_STATUS = "REPORT_INSUFFICIENT"


def run(scope_id: str, observations: list[dict]) -> dict:
    monitor = StreamingFiberMonitor(scope_id=scope_id)
    steps = []
    for row in observations:
        steps.append(monitor.observe(row["state_id"], row["report"], row["query"]))
    summary = monitor.get_receipt()
    return finish({
        "lesson_id": "01",
        "schema": summary["schema"],
        "authority_effect": summary["authority_effect"],
        "status": summary["status"],
        "contract_status": summary["contract_status"],
        "steps": steps,
        "summary": summary,
    })


def prepared() -> dict:
    trace = load_json("01_collision.json")
    return run(trace["scope_id"], trace["observations"])


def your_turn() -> dict:
    # Your turn: keep the queries, and put the tier on the report.
    # Delete "approval_tier" from both reports to watch the collision return.
    observations = [
        {
            "state_id": "task-a",
            "report": {"summary": "ship the etl job", "approval_tier": 3},
            "query": {"approval_tier": 3},
        },
        {
            "state_id": "task-b",
            "report": {"summary": "ship the etl job", "approval_tier": 1},
            "query": {"approval_tier": 1},
        },
    ]
    return run("learn-01-your-turn", observations)


def main() -> int:
    row = prepared()
    print("Lesson 01 prepared")
    print(dumps(row["summary"]))
    if row["status"] != EXPECTED_STATUS:
        return 1
    turned = your_turn()
    print("\nLesson 01 your turn")
    print(dumps(turned["summary"]))
    print(f"your-turn status: {turned['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
