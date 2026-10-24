"""Lesson 02: Local green is not the global question.

Delta_E = E_g - E_1 E_2, in {-1, 0, 1}, with the global sample supplied.
NGD, ZDR, and PGD are the Volume I–III names. Volumes V–VI use a different
all-green convention. This lesson uses the I–III delta.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: The three defect kinds on three supplied Boolean triples.
2. What it does not support: Manufacturing E_g from the local passes.
3. Narrowest defensible claim: The prepared primary row has defect_kind NGD and delta -1. The other two rows are ZDR and PGD.
4. Host duty that remains: Someone outside the proposing stage supplies the global sample.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import evaluator_defect  # noqa: E402

from learn.support import dumps, finish, load_json  # noqa: E402

EXPECTED_STATUS = "NGD"


def prepared() -> dict:
    trace = load_json("02_defects.json")
    rows = []
    for item in trace["rows"]:
        defect = evaluator_defect(item["local"][0], item["local"][1], item["global"])
        rows.append({"name": item["name"], **defect})
    primary = rows[0]
    return finish({
        "lesson_id": "02",
        "schema": "learn.evaluator_panel.v1",
        "authority_effect": "None",
        "status": primary["defect_kind"],
        "delta": primary["delta"],
        "rows": rows,
        "convention": "Volume I-III: Delta_E = Eg - E1*E2 in {-1, 0, 1}.",
    })


def your_turn() -> dict:
    # Your turn: set global_sample from your external checker, not from the agent.
    local_first = 1
    local_second = 1
    global_sample = 0
    defect = evaluator_defect(local_first, local_second, global_sample)
    return finish({
        "lesson_id": "02",
        "schema": "learn.evaluator_panel.v1",
        "authority_effect": "None",
        "status": defect["defect_kind"],
        "delta": defect["delta"],
        "rows": [{"name": "your turn", **defect}],
        "global_sample_source": "external",
    })


def main() -> int:
    row = prepared()
    print("Lesson 02 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS or row["delta"] != -1:
        return 1
    print("\nLesson 02 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
