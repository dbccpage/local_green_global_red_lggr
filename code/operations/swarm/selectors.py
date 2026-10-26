"""Host elimination rule and evidence selectors over a frozen snapshot.

Selectors read only public structure (contracts, hypotheses, predicted outcomes)
and acquired observations. Hidden truth reaches them only through observations
returned by evidence_access.
"""
from collections import Counter
from math import log2

from .domain import MALFORMED, check_modules, check_params, hypotheses, outcome, verdict

ARMS = ["B", "C", "round_robin", "recently_changed", "dependency_risk"]


class Space:
    """Hypotheses, their verdicts, and every check's predicted outcome for one snapshot."""

    def __init__(self, instance, files):
        self.instance = instance
        self.hyps = hypotheses(instance)
        self.verdicts = [verdict(instance, files, h) for h in self.hyps]
        self.checks = {c["id"]: c for c in instance["checks"]}
        self.predicted = {cid: [outcome(instance, c, files, h) for h in self.hyps] for cid, c in self.checks.items()}

    def alive(self, observations):
        keep = list(range(len(self.hyps)))
        for cid, result in observations:
            if result == MALFORMED:
                continue
            row = self.predicted[cid]
            keep = [i for i in keep if row[i] == result]
        return keep

    def carry(self, observations, instance=None):
        """Restrict to hidden-parameter-only observations (valid across snapshot changes)."""
        from .domain import theta_only
        return [(cid, r) for cid, r in observations if theta_only(self.checks[cid])]


def host_rule(space, observations):
    alive = space.alive(observations)
    if not alive:
        return "model_mismatch"
    values = {space.verdicts[i] for i in alive}
    if values == {True}:
        return "accept"
    if values == {False}:
        return "reject"
    return "defer"


def resolved(decision):
    return decision in ("accept", "reject", "model_mismatch")


def partition(space, alive, cid):
    groups = {}
    row = space.predicted[cid]
    for i in alive:
        groups.setdefault(row[i], []).append(i)
    return groups


def info_gain(space, alive, cid):
    """Entropy (bits) of the check's outcome under uniform weights = expected identity-entropy reduction."""
    if not alive:
        return 0.0
    counts = Counter(space.predicted[cid][i] for i in alive)
    n = len(alive)
    return -sum((k / n) * log2(k / n) for k in counts.values()) + 0.0


def pairs(space, alive):
    p = sum(1 for i in alive if space.verdicts[i])
    return p * (len(alive) - p)


def pair_elimination(space, alive, cid):
    total = pairs(space, alive)
    groups = partition(space, alive, cid)
    remaining = [pairs(space, g) for g in groups.values()]
    worst = total - max(remaining) if remaining else 0
    n = len(alive)
    expected = total - sum(len(g) / n * r for g, r in zip(groups.values(), remaining)) if n else 0.0
    return worst, expected


def affordable(space, remaining, used):
    return [cid for cid in sorted(space.checks) if cid not in used and space.checks[cid]["cost"] <= remaining]


def rank_b(space, alive, candidates):
    scored = [(info_gain(space, alive, cid) / space.checks[cid]["cost"], cid) for cid in candidates]
    return sorted(scored, key=lambda s: (-s[0], s[1]))


def rank_c(space, alive, candidates):
    scored = []
    for cid in candidates:
        worst, expected = pair_elimination(space, alive, cid)
        cost = space.checks[cid]["cost"]
        scored.append((worst / cost, expected / cost, cid))
    return sorted(scored, key=lambda s: (-s[0], -s[1], s[2]))


def choose(arm, space, alive, candidates, context):
    if not candidates:
        return None
    if arm == "B":
        best = rank_b(space, alive, candidates)[0]
        return best[1] if best[0] > 0 else None
    if arm == "C":
        best = rank_c(space, alive, candidates)[0]
        return best[2] if best[0] > 0 or best[1] > 0 else None
    if arm == "round_robin":
        return candidates[0]
    if arm == "recently_changed":
        order = context.get("write_order", [])
        rank = {m: order.index(m) for m in order}

        def key(cid):
            mods = check_modules(space.instance, space.checks[cid])
            recency = max((rank.get(m, -1) for m in mods), default=-1)
            return (-recency, cid)
        return sorted(candidates, key=key)[0]
    if arm == "dependency_risk":
        def key(cid):
            check = space.checks[cid]
            return (-(len(check_params(space.instance, check)) + len(check_modules(space.instance, check))), cid)
        return sorted(candidates, key=key)[0]
    raise ValueError("unknown arm " + arm)


def acquire(arm, space, observe, budget, context=None, prior=()):
    """Run one offline arm. `observe(cid)` returns the true (possibly malformed) outcome.

    Returns steps, observations, the final host-rule decision and units spent;
    `units_to_resolve` is the spend at which the host rule first resolved (or None).
    """
    context = context or {}
    observations, steps, used, spent = list(prior), [], set(), 0
    decision = host_rule(space, observations)
    units_to_resolve = 0 if resolved(decision) else None
    while not resolved(decision):
        alive = space.alive(observations)
        cid = choose(arm, space, alive, affordable(space, budget - spent, used), context)
        if cid is None:
            break
        result = observe(cid)
        used.add(cid)
        spent += space.checks[cid]["cost"]
        observations.append((cid, result))
        decision = host_rule(space, observations)
        steps.append({"check": cid, "result": result, "spent": spent, "decision": decision})
        if resolved(decision):
            units_to_resolve = spent
    return {"arm": arm, "budget": budget, "steps": steps, "decision": decision, "spent": spent,
            "units_to_resolve": units_to_resolve}
