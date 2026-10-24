"""Lesson 07: Another generation on the same report.

Two histories share one coarse report. Targets are 0 and 1, so the half-spread
ceiling is 1/2. Three predictors that factor through that report, including the
midpoint, stay at or above the ceiling. A refined report that splits the two
histories, and a predictor that uses it, resolves the floor on this table.

Internal updates of a predictor that still sees only the coarse report do not
undercut the half-spread. A finer observation can. Paper 000 is the reading
for the scoped finite-carrier statements. This lesson calls
StreamingRSIFiberCeilingMonitor.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: Three evidence-preserving generations and one refined generation on the supplied pair.
2. What it does not support: A blanket claim that recursive improvement is impossible, or a ceiling for a predictor that receives a new observation.
3. Narrowest defensible claim: Each coarse generation status is RSI_FIBER_CEILING_LOCKED_LGGR and the coarse half-spread ceiling is 1/2. The refined generation status is EVIDENCE_REFINEMENT_RESOLVED_LGGG.
4. Host duty that remains: Lowering the floor takes a finer observation or a declared restriction of the carrier. The host records which one it used.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import StreamingRSIFiberCeilingMonitor  # noqa: E402
from lggr.common import canonical  # noqa: E402

from learn.support import dumps, finish, load_json  # noqa: E402

EXPECTED_STATUS = "RSI_FIBER_CEILING_LOCKED_LGGR"


def _monitor(trace: dict) -> StreamingRSIFiberCeilingMonitor:
    monitor = StreamingRSIFiberCeilingMonitor(scope_id=trace["scope_id"])
    for state in trace["states"]:
        monitor.observe_state(
            state["state_id"],
            state["coarse_report"],
            state["target"],
            refined_report=state["refined_report"],
        )
    return monitor


def prepared() -> dict:
    trace = load_json("07_generations.json")
    monitor = _monitor(trace)
    coarse_key = canonical(trace["states"][0]["coarse_report"])
    coarse = []
    for index, prediction in enumerate(trace["coarse_predictions"]):
        receipt = monitor.evaluate_generation(
            f"g{index}",
            {coarse_key: prediction},
            use_refined_report=False,
        )
        coarse.append(receipt)
    refined_predictor = {}
    for state in trace["states"]:
        bit = str(state["refined_report"]["bit"])
        refined_predictor[canonical(state["refined_report"])] = trace["refined_predictions"][bit]
    refined = monitor.evaluate_generation("g-refined", refined_predictor, use_refined_report=True)
    return finish({
        "lesson_id": "07",
        "schema": coarse[0]["schema"],
        "authority_effect": coarse[0]["authority_effect"],
        "status": coarse[0]["status"],
        "coarse_half_spread_ceiling": coarse[0]["coarse_half_spread_ceiling"],
        "coarse_statuses": [item["status"] for item in coarse],
        "coarse_worst_case_errors": [item["worst_case_error"] for item in coarse],
        "midpoint_attained": coarse[1]["attains_minimax_midpoint_floor"],
        "refined_status": refined["status"],
        "refined_worst_case_error": refined["worst_case_error"],
        "refined_broke_coarse_ceiling": refined["broke_coarse_ceiling_via_refinement"],
    })


def your_turn() -> dict:
    # Your turn: point prediction at the same coarse report, then try a third value.
    # The half-spread on this pair stays 1/2 for every such prediction.
    trace = load_json("07_generations.json")
    monitor = _monitor(trace)
    prediction = "1/4"
    receipt = monitor.evaluate_generation(
        "your-turn",
        {canonical(trace["states"][0]["coarse_report"]): prediction},
        use_refined_report=False,
    )
    return finish({
        "lesson_id": "07",
        "schema": receipt["schema"],
        "authority_effect": receipt["authority_effect"],
        "status": receipt["status"],
        "prediction": prediction,
        "worst_case_error": receipt["worst_case_error"],
        "coarse_half_spread_ceiling": receipt["coarse_half_spread_ceiling"],
    })


def main() -> int:
    row = prepared()
    print("Lesson 07 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS:
        return 1
    print("\nLesson 07 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
