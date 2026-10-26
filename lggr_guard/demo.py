"""Three runnable scenarios from a real self-modifying agent pipeline.  python -m lggr_guard.demo

1. Two self-modifications each pass the gate alone; together they silently disable the
   pre-review check (local green, global red). The gate names the pair and the emergent change.
2. Three small threshold relaxations, each within its per-change tolerance, add up to a
   drift beyond the budget measured from the last approved anchor.
3. The hosted reviewer changes under you: replaying frozen decisions raises the alarm.
"""
import json
import tempfile
from pathlib import Path

from .compose import Change, Check, Metric, compose_check
from .frozen import FrozenDecisions

PROFILES = {"default": {}, "fast": {"precheck": False, "parallel": 4}}


def effective(state):
    settings = PROFILES[state["profile"]]
    precheck = settings.get("precheck", True) if state["precheck_configurable"] else True
    return {"precheck_enabled": precheck, "parallel": settings.get("parallel", 1),
            "review_threshold": state["review_threshold"]}


def pre_review_gate(state, change_declares_behaviour):
    """The gate under protection: with precheck on, undeclared behaviour changes go back to the worker."""
    return "back_to_worker" if effective(state)["precheck_enabled"] and not change_declares_behaviour else "to_review"


MAIN = {"profile": "default", "precheck_configurable": False, "review_threshold": 0.80}

make_configurable = Change("make-precheck-configurable", lambda s: {**s, "precheck_configurable": True},
                           frozenset({"precheck_configurable"}))  # refactor: default stays on
adopt_fast_profile = Change("adopt-fast-profile", lambda s: {**s, "profile": "fast"}, frozenset({"parallel"}))
probe = Check("probe: gate still returns an undeclared change to the worker",
              lambda s: pre_review_gate(s, change_declares_behaviour=False) == "back_to_worker")


def observe(state):
    return {**effective(state), "precheck_configurable": state["precheck_configurable"]}


def scenario_composition():
    return compose_check(MAIN, [make_configurable, adopt_fast_profile], [probe], observe=observe)


def scenario_drift():
    relax = [Change(f"relax-threshold-{i}", lambda s: {**s, "review_threshold": round(s["review_threshold"] - 0.03, 4)},
                    frozenset({"review_threshold"})) for i in (1, 2, 3)]
    return compose_check(MAIN, relax, [probe], observe=observe,
                         metrics=[Metric("review_threshold", lambda s: s["review_threshold"], budget=0.05)])


def scenario_reviewer_drift():
    with tempfile.TemporaryDirectory() as tmp:
        frozen = FrozenDecisions(Path(tmp) / "frozen.json")
        for i in range(20):
            frozen.freeze(f"pr-{i}", {"declared": i % 3 != 0, "tests_weakened": i % 5 == 0},
                          "reject" if i % 3 == 0 or i % 5 == 0 else "accept")

        def reviewer_v1(case):
            return "reject" if (not case["declared"]) or case["tests_weakened"] else "accept"

        def reviewer_v2(case):  # provider update: stops flagging weakened tests
            return "reject" if not case["declared"] else "accept"
        return {"before_update": frozen.replay(reviewer_v1), "after_update": frozen.replay(reviewer_v2)}


def main():
    one = scenario_composition()
    print("1. composition:", json.dumps({k: one[k] for k in ("verdict", "defect", "reasons", "minimal_failing_sets", "undeclared")}, indent=1))
    print("   each alone:", {k: v["pass"] for k, v in one["per_change"].items()})
    two = scenario_drift()
    d = two["drift"][0]
    print("2. drift:", two["verdict"], "-", two["reasons"])
    print("   path:", [(p["after"], round(p["step"], 3), round(p["total_from_anchor"], 3)) for p in d["path"]])
    three = scenario_reviewer_drift()
    print("3. reviewer:", {k: (v["agreement"], v["alarm"]) for k, v in three.items()})
    print("  ", three["after_update"]["meaning"], "- mismatched cases:", [m["id"] for m in three["after_update"]["mismatches"]])


if __name__ == "__main__":
    main()
