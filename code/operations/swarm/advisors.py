"""Advisor notes for live controllers. Inputs: public space + acquired observations only."""
from .selectors import affordable, pairs, rank_b, rank_c


def _fmt(h):
    return "{" + ", ".join(f"{k}={v}" for k, v in h.items()) + "}"


def note(arm, space, observations, remaining, used):
    """Return (text, recommended check ids)."""
    candidates = affordable(space, remaining, used)
    alive = space.alive(observations)
    head = f"advisor note: {remaining} budget units remain."
    if arm == "L-0":
        listed = ", ".join(f"{cid} (cost {space.checks[cid]['cost']})" for cid in candidates) or "none affordable"
        return f"{head} Unrun checks: {listed}.", list(candidates)
    if arm == "L-B":
        top = [s for s in rank_b(space, alive, candidates) if s[0] > 0][:3]
        if not top:
            return f"{head} No affordable check has positive expected information gain.", []
        listed = "; ".join(f"{cid} (cost {space.checks[cid]['cost']}, expected information gain "
                           f"{score * space.checks[cid]['cost']:.2f} bits)" for score, cid in top)
        return f"{head} Highest expected information gain per unit cost: {listed}.", [cid for _, cid in top]
    if arm == "L-C":
        if not alive:
            return f"{head} No hypothesis is consistent with the observations so far.", []
        if pairs(space, alive) == 0:
            return f"{head} Every hypothesis consistent with the observations gives the same verdict.", []
        ranked = rank_c(space, alive, candidates)
        top = ranked[0][2] if ranked and (ranked[0][0] > 0 or ranked[0][1] > 0) else None
        passing = [i for i in alive if space.verdicts[i]]
        failing = [i for i in alive if not space.verdicts[i]]
        p = passing[0]
        if top is not None:
            row = space.predicted[top]
            p = next((i for i in passing if any(row[i] != row[j] for j in failing)), p)
            failing = [j for j in failing if row[j] != row[p]] or failing

        def distance(j):
            return sum(space.hyps[p][k] != space.hyps[j][k] for k in space.hyps[p])
        f = min(failing, key=lambda j: (distance(j), j))
        separating = [cid for cid in candidates if space.predicted[cid][p] != space.predicted[cid][f]]
        sep = ", ".join(f"{cid} (cost {space.checks[cid]['cost']})" for cid in separating) or "none affordable"
        return (f"{head} Surviving pair: under {_fmt(space.hyps[p])} the system passes; under {_fmt(space.hyps[f])} "
                f"it fails. Checks that separate them: {sep}."), separating
    raise ValueError("unknown advisor arm " + arm)
