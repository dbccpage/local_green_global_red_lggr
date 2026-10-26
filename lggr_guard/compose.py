"""Composition gate: catch changes that pass alone but fail (or drift) together.

A change is never judged only by itself. The gate evaluates every change on the
last accepted state, then the composition of all pending changes, and reports:

- NGD (local green, global red): every change passes alone, the composition fails.
  The witness is every minimal failing subset (fails, while each proper subset passes).
- Undeclared / emergent behaviour: an observable behaviour that differs from the
  base in the composition but that no change declared. "Emergent" means no single
  change produced it on its own: it only appears when changes are combined.
- Cumulative drift: metrics are measured against the anchor (the last accepted
  state), not the previous step, so small steps cannot add up unnoticed. The first
  prefix of the change sequence that leaves the budget is reported.

AuthorityEffect: None. The gate returns evidence and a verdict; whoever owns the
merge decides. Standard library only (plus lggr.descent for the defect class).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Callable, Iterable

try:
    from lggr.descent import evaluator_defect
except ImportError:  # standalone copy: same definition, Delta = Eg - E1*E2
    def evaluator_defect(first, second, global_verdict):
        a, b, g = int(first), int(second), int(global_verdict)
        delta = g - a * b
        return {"local": [a, b], "global": g, "delta": delta, "defect_kind": {-1: "NGD", 0: "ZDR", 1: "PGD"}[delta]}


@dataclass(frozen=True)
class Change:
    """A proposed modification. `apply(state) -> new state`; `declares` lists behaviours it may change."""
    name: str
    apply: Callable[[Any], Any]
    declares: frozenset = field(default_factory=frozenset)


@dataclass(frozen=True)
class Check:
    """A pass/fail invariant or probe (e.g. 'the gate still rejects a known-broken input')."""
    name: str
    passes: Callable[[Any], bool]


@dataclass(frozen=True)
class Metric:
    """A number whose total movement away from the anchor must stay within `budget`."""
    name: str
    value: Callable[[Any], float]
    budget: float


def _run(base, changes):
    state = base
    for change in changes:
        state = change.apply(state)
    return state


def _evaluate(state, checks, observe):
    failed = [c.name for c in checks if not c.passes(state)]
    return {"pass": not failed, "failed": failed, "behaviour": observe(state) if observe else {}}


def _subsets(n, exhaustive_limit):
    if n <= exhaustive_limit:
        return [s for k in range(1, n + 1) for s in combinations(range(n), k)]
    return [(i,) for i in range(n)] + [tuple(range(n))]


def compose_check(base, changes: Iterable[Change], checks: Iterable[Check], *, observe=None,
                  metrics: Iterable[Metric] = (), anchor=None, exhaustive_limit: int = 5) -> dict:
    """Judge pending `changes` (in merge order) against `base`, the last accepted state.

    `observe(state) -> dict` names observable behaviours (flags, thresholds, enabled checks).
    `anchor` defaults to `base`; pass the state at the last owner-approved release to bound
    drift across many merges.
    """
    changes, checks, metrics = list(changes), list(checks), list(metrics)
    anchor = base if anchor is None else anchor
    base_eval = _evaluate(base, checks, observe)
    runs = {}
    for subset in _subsets(len(changes), exhaustive_limit):
        runs[subset] = _evaluate(_run(base, [changes[i] for i in subset]), checks, observe)
    full = tuple(range(len(changes)))
    singles = [runs[(i,)] for i in range(len(changes))]
    local_green = all(r["pass"] for r in singles)
    global_green = runs[full]["pass"] if changes else base_eval["pass"]
    defect = evaluator_defect(int(local_green), 1, int(global_green))

    # Minimal failing subsets: fail, and every proper subset that was evaluated passes.
    minimal = []
    for subset, r in sorted(runs.items(), key=lambda kv: (len(kv[0]), kv[0])):
        if r["pass"] or len(subset) == 1:
            continue
        proper = [runs.get(s) for k in range(1, len(subset)) for s in combinations(subset, k)]
        if all(p is not None and p["pass"] for p in proper):
            minimal.append({"changes": [changes[i].name for i in subset], "failed_checks": r["failed"]})

    # Undeclared / emergent behaviour in the composition.
    declared = set().union(*(c.declares for c in changes)) if changes else set()
    undeclared = []
    if observe:
        before, after = base_eval["behaviour"], runs[full]["behaviour"] if changes else base_eval["behaviour"]
        for key in sorted(set(before) | set(after)):
            if before.get(key) != after.get(key) and key not in declared:
                alone = [changes[i].name for i in range(len(changes)) if runs[(i,)]["behaviour"].get(key) != before.get(key)]
                undeclared.append({"behaviour": key, "base": before.get(key), "composed": after.get(key),
                                   "changed_alone_by": alone, "emergent": not alone})

    # Cumulative drift against the anchor along the merge order.
    drift = []
    for metric in metrics:
        start = metric.value(anchor)
        path, excursion = [], None
        state = base
        for i, change in enumerate(changes):
            state = change.apply(state)
            total = metric.value(state) - start
            step = metric.value(state) - metric.value(_run(base, changes[:i]))
            path.append({"after": change.name, "step": step, "total_from_anchor": total})
            if excursion is None and abs(total) > metric.budget:
                excursion = change.name
        drift.append({"metric": metric.name, "anchor": start, "budget": metric.budget, "path": path,
                      "first_excursion_after": excursion, "within_budget": excursion is None})

    reasons = []
    if not global_green:
        reasons.append("composition fails checks: " + ", ".join(runs[full]["failed"] if changes else base_eval["failed"]))
    if undeclared:
        reasons.append("undeclared behaviour change: " + ", ".join(u["behaviour"] for u in undeclared))
    reasons += [f"{d['metric']} drifted beyond budget {d['budget']} after {d['first_excursion_after']}" for d in drift if not d["within_budget"]]
    return {
        "verdict": "accept" if not reasons else "reject",
        "reasons": reasons,
        "local_green": local_green,
        "global_green": global_green,
        "defect": defect["defect_kind"],  # NGD = local green, global red
        "per_change": {changes[i].name: singles[i] for i in range(len(changes))},
        "composed": runs[full] if changes else base_eval,
        "minimal_failing_sets": minimal,
        "undeclared": undeclared,
        "drift": drift,
        "subsets_evaluated": len(runs),
    }
