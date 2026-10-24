"""Lesson 05: Moving the ledger.

examples/faithful_transport.json has a commuting square and a retraction.
examples/lossy_transport.json commutes and does not reflect nonrepairability.
Forward commutation preserves repairs. A checked left inverse is what carries
nonrepairability the other way.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: The two supplied transport fixtures, including the require_reflection flag on the lossy map.
2. What it does not support: Inferring a retraction from a representation name.
3. Narrowest defensible claim: The faithful receipt status is RETRACTION_VERIFIED. The lossy receipt commutes and nonrepairability_reflection_verified is false.
4. Host duty that remains: Re-encode a tool ledger only after this check, and keep the source ledger if reflection is uncertified.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import verify_transport  # noqa: E402

from learn.support import dumps, finish, load_json, load_repo_json  # noqa: E402

EXPECTED_STATUS = "RETRACTION_VERIFIED"


def _run(document: dict) -> dict:
    reflection = bool(document.get("require_reflection", False))
    payload = {key: value for key, value in document.items() if key != "require_reflection"}
    receipt = verify_transport(**payload)
    return {
        "receipt": receipt,
        "require_reflection": reflection,
        "reflection_certified": (not reflection) or bool(receipt["nonrepairability_reflection_verified"]),
    }


def prepared() -> dict:
    trace = load_json("05_examples.json")
    faithful = _run(load_repo_json(trace["faithful"]))
    lossy = _run(load_repo_json(trace["lossy"]))
    return finish({
        "lesson_id": "05",
        "schema": faithful["receipt"]["schema"],
        "authority_effect": faithful["receipt"]["authority_effect"],
        "status": faithful["receipt"]["status"],
        "faithful_reflection": faithful["receipt"]["nonrepairability_reflection_verified"],
        "lossy_status": lossy["receipt"]["status"],
        "lossy_forward_commutes": lossy["receipt"]["forward_commutes"],
        "lossy_reflection": lossy["receipt"]["nonrepairability_reflection_verified"],
        "lossy_require_reflection": lossy["require_reflection"],
        "lossy_reflection_certified": lossy["reflection_certified"],
    })


def your_turn() -> dict:
    # Your turn: replace F0/F1 with the map from your old tool schema to the new one.
    # Leave G0/G1 out until you have a left inverse.
    document = {
        "D_source": [[-1, 1, 0], [0, -1, 1], [-1, 0, 1]],
        "D_target": [[0]],
        "F0": [[0, 0, 0]],
        "F1": [[0, 0, 0]],
        "require_reflection": True,
    }
    checked = _run(document)
    receipt = checked["receipt"]
    return finish({
        "lesson_id": "05",
        "schema": receipt["schema"],
        "authority_effect": receipt["authority_effect"],
        "status": receipt["status"],
        "forward_commutes": receipt["forward_commutes"],
        "reflection_certified": checked["reflection_certified"],
    })


def main() -> int:
    row = prepared()
    print("Lesson 05 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 05 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
