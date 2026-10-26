"""Recipe: collision-guided check selection (guide 03).

A verifier with a small budget keeps the hypotheses that still fit what it has
observed. While a pass hypothesis and a fail hypothesis share the observed
report, the verdict is undetermined: StreamingFiberMonitor names such a pair.
The selector buys a check that separates that pair, preferring the one that
removes the most opposite-verdict pairs in the worst case, per unit cost.

This is a simplified form of policy C in the LGGR/RSI swarm experiment
(experiments/lggr_rsi_swarm/REPORT.md). There the full policy beat
expected-uncertainty-reduction selection under the host rule (+0.268 at 4
units) and added nothing as advice to live agents. This recipe's own
performance was not measured.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: A deterministic selector and the shared host decision rule on a supplied finite hypothesis set.
2. What it does not support: Any claim that the selector outperforms another policy, or that the hypothesis set is complete.
3. Narrowest defensible claim: In the demo the selector buys schema then fee_e2e, spends 4 of 4 units, and the host rule returns accept.
4. Host duty that remains: The host enumerates the hypotheses from public contracts, prices the checks, and runs them outside the proposing agents.
"""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Callable, Mapping

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import StreamingFiberMonitor  # noqa: E402

from learn.support import dumps, finish  # noqa: E402

RECIPE_ID = "check_selector"
EXPECTED_STATUS = "accept"

Hypothesis = Mapping[str, Any]  # {"id": str, "outcomes": {check_id: bool}, "verdict": "pass" | "fail"}


def surviving(hypotheses: list[Hypothesis], observed: Mapping[str, bool]) -> list[Hypothesis]:
    return [h for h in hypotheses if all(h["outcomes"][c] == v for c, v in observed.items())]


def colliding_pair(survivors: list[Hypothesis], observed: Mapping[str, bool]) -> dict[str, Any] | None:
    """A pass and a fail that share the observed report, or None when the verdict is determined."""
    monitor = StreamingFiberMonitor(scope_id="check-selection")
    for h in survivors:
        report = {c: h["outcomes"][c] for c in sorted(observed)}
        receipt = monitor.observe(h["id"], report, h["verdict"])
        if receipt["status"] == "REPORT_INSUFFICIENT":
            return receipt["colliding_pair"]
    return None


def _opposite_pairs(hs: list[Hypothesis]) -> int:
    passes = sum(1 for h in hs if h["verdict"] == "pass")
    return passes * (len(hs) - passes)


def select_check(survivors: list[Hypothesis], observed: Mapping[str, bool],
                 costs: Mapping[str, int], remaining: int) -> str | None:
    pair = colliding_pair(survivors, observed)
    if pair is None:
        return None
    by_id = {h["id"]: h for h in survivors}
    left, right = by_id[pair["left"]["state_id"]], by_id[pair["right"]["state_id"]]
    before = _opposite_pairs(survivors)
    best: tuple | None = None
    for check, cost in costs.items():
        if check in observed or cost > remaining or left["outcomes"][check] == right["outcomes"][check]:
            continue
        worst = max(_opposite_pairs([h for h in survivors if h["outcomes"][check] == v]) for v in (True, False))
        key = (-(before - worst) / cost, cost, check)
        if best is None or key < best:
            best = key
    return None if best is None else best[2]


def host_rule(survivors: list[Hypothesis]) -> str:
    """Shared decision rule: never accepts while a fail hypothesis survives."""
    verdicts = {h["verdict"] for h in survivors}
    if not verdicts:
        return "model_mismatch"
    if verdicts == {"pass"}:
        return "accept"
    if verdicts == {"fail"}:
        return "reject"
    return "defer"


def run(hypotheses: list[Hypothesis], costs: Mapping[str, int], budget: int,
        run_check: Callable[[str], bool]) -> dict[str, Any]:
    observed: dict[str, bool] = {}
    spent = 0
    while True:
        survivors = surviving(hypotheses, observed)
        check = select_check(survivors, observed, costs, budget - spent)
        if check is None:
            break
        observed[check] = run_check(check)
        spent += costs[check]
    survivors = surviving(hypotheses, observed)
    return {"bought": list(observed), "observed": observed, "spent": spent,
            "survivors": [h["id"] for h in survivors], "decision": host_rule(survivors)}


def _demo_hypotheses() -> list[Hypothesis]:
    # unit_a and lint pass in every hypothesis, so buying them cannot change the verdict.
    base = {"unit_a": True, "unit_b": True, "lint": True}
    rows = [
        ("H1-clean", {"schema": True, "fee_e2e": True}, "pass"),
        ("H2-key-mismatch", {"schema": False, "fee_e2e": True}, "fail"),
        ("H3-fee-drift", {"schema": True, "fee_e2e": False}, "fail"),
        ("H4-both", {"schema": False, "fee_e2e": False, "unit_b": False}, "fail"),
    ]
    return [{"id": i, "outcomes": {**base, **o}, "verdict": v} for i, o, v in rows]


def demo() -> dict[str, Any]:
    hypotheses = _demo_hypotheses()
    costs = {"unit_a": 1, "unit_b": 1, "lint": 1, "schema": 2, "fee_e2e": 2}
    truth = hypotheses[0]["outcomes"]
    result = run(hypotheses, costs, budget=4, run_check=lambda c: truth[c])
    worlds = []
    for world in hypotheses:
        r = run(hypotheses, costs, budget=4, run_check=lambda c, w=world: w["outcomes"][c])
        worlds.append({"world": world["id"], "decision": r["decision"], "spent": r["spent"]})
    # Toy contrast, not evidence: buy cheapest checks first until the budget runs out.
    naive: dict[str, bool] = {}
    left = 4
    for check in sorted(costs, key=lambda c: (costs[c], c)):
        if costs[check] <= left:
            naive[check] = truth[check]
            left -= costs[check]
    return finish({
        "recipe_id": RECIPE_ID,
        "schema": "learn.recipe.check_selector.v1",
        "authority_effect": "None",
        "status": result["decision"],
        "bought": result["bought"],
        "spent": result["spent"],
        "survivors": result["survivors"],
        "every_world": worlds,
        "cheapest_first_bought": list(naive),
        "cheapest_first_decision": host_rule(surviving(hypotheses, naive)),
    })


def main() -> int:
    row = demo()
    print(dumps(row))
    return 0 if row["status"] == EXPECTED_STATUS else 1


if __name__ == "__main__":
    sys.exit(main())
