"""Lesson 08: Three ways a loop stops.

The finite transition harness names three terminals. This lesson maps them
onto receipts from lessons 01, 03, and 04. It does not reimplement
MultiAgentCommunicatingHypergraph.

Adding agents can delay a repeated report out to the product of the
report-alphabet sizes. The joint report still only carries that product
alphabet. The machine-checked finite-carrier statements are in paper 000.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: A single object whose three stop reasons are the prepared statuses of lessons 01, 03, and 04.
2. What it does not support: A new simulator of asynchronous swarms, or a horizon computed by this script.
3. Narrowest defensible claim: REPORT_COLLISION maps to REPORT_INSUFFICIENT, LIFT_BUDGET_EXHAUSTION maps to ALERT, and OVERLAP_GLUING_REFUSAL maps to CYCLE_CLOSED, each taken from that lesson's prepared receipt.
4. Host duty that remains: The host keeps the underlying receipt, not only the stop-reason name.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from learn.support import STEM_BY_ID, dumps, finish, load_json, load_lesson  # noqa: E402

EXPECTED_STATUS = "THREE_STOPS_RECORDED"


def prepared() -> dict:
    trace = load_json("08_stops.json")
    stops = []
    for item in trace["stops"]:
        row = load_lesson(STEM_BY_ID[item["lesson"]]).prepared()
        stops.append({
            "reason": item["reason"],
            "lesson": item["lesson"],
            "status": row["status"],
            "schema": row["schema"],
            "matched": row["status"] == item["equals"],
        })
    matched = all(item["matched"] for item in stops)
    return finish({
        "lesson_id": "08",
        "schema": "learn.stop_reasons.v1",
        "authority_effect": "None",
        "status": "THREE_STOPS_RECORDED" if matched else "STOP_MAP_MISMATCH",
        "reading": trace["reading"],
        "stops": stops,
        "paper": "papers/012_rsi/000_relational_reasoning_and_rsi_impossibility/",
    })


def your_turn() -> dict:
    # Your turn: this map is the whole lesson. Point your runbook at the three receipts.
    row = prepared()
    return finish({
        "lesson_id": "08",
        "schema": row["schema"],
        "authority_effect": "None",
        "status": row["status"],
        "runbook": [f"{item['reason']} -> lesson {item['lesson']} ({item['status']})" for item in row["stops"]],
    })


def main() -> int:
    row = prepared()
    print("Lesson 08 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 08 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
