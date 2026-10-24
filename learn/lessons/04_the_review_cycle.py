"""Lesson 04: The review cycle.

A -> B -> C -> A with equal edge values closes with a nonzero coboundary defect
and an exact rational repair distance. The budget example in
examples/budget_exact_cochain.json is an exact coboundary in its supplied
complex, so that drift is not presented here as a cohomology class.

AuthorityEffect: None.
Standard library only: Python 3.10+.
See also cookbooks/03_cochain_cycle_repair.py.

Artifact Summary:
1. What it supports: Cycle closure on three supplied review edges, plus an exactness classification of the budget cochain.
2. What it does not support: Reading a nonzero cycle defect as a claim about the world outside the values.
3. Narrowest defensible claim: The closing edge has status CYCLE_CLOSED and a nonzero closure_defect. The budget example status is EXACT.
4. Host duty that remains: The host supplies the edge values and the complex. The repair distance is a distance in that complex.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import StreamingCochainMonitor, classify_cochain  # noqa: E402

from learn.support import dumps, finish, load_json, load_repo_json  # noqa: E402

EXPECTED_STATUS = "CYCLE_CLOSED"


def prepared() -> dict:
    trace = load_json("04_cycle.json")
    monitor = StreamingCochainMonitor()
    steps = []
    for edge in trace["edges"]:
        steps.append(monitor.add_edge(edge["src"], edge["dst"], edge["value"]))
    closing = steps[-1]
    exact_doc = load_repo_json(trace["exact_example"])
    exact = classify_cochain(exact_doc["D0"], exact_doc["h"], exact_doc.get("D1"))
    return finish({
        "lesson_id": "04",
        "schema": closing["schema"],
        "authority_effect": closing["authority_effect"],
        "status": closing["status"],
        "closure_defect": closing["closure_defect"],
        "l1_repair_distance": closing["l1_repair_distance"],
        "meaning": closing["meaning"],
        "exact_status": exact["status"],
        "exact_represents_nonzero_H1": exact["represents_nonzero_H1"],
        "steps": steps,
    })


def your_turn() -> dict:
    # Your turn: put your reviewers' numeric judgments on the edges.
    edges = [
        {"src": "reviewer-a", "dst": "reviewer-b", "value": "1"},
        {"src": "reviewer-b", "dst": "reviewer-c", "value": "1"},
        {"src": "reviewer-c", "dst": "reviewer-a", "value": "-2"},
    ]
    monitor = StreamingCochainMonitor()
    closing = None
    for edge in edges:
        closing = monitor.add_edge(edge["src"], edge["dst"], edge["value"])
    assert closing is not None
    return finish({
        "lesson_id": "04",
        "schema": closing["schema"],
        "authority_effect": closing["authority_effect"],
        "status": closing["status"],
        "closure_defect": closing["closure_defect"],
        "meaning": closing["meaning"],
    })


def main() -> int:
    row = prepared()
    print("Lesson 04 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 04 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
