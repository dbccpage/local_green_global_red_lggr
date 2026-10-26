"""The only path from hidden truth to observations: a priced, budgeted check gateway.

Agents, advisors and selectors never receive the hidden assignment. They obtain
observations only through `Gateway.run`, which charges the check's cost against a
budget, refuses unknown, repeated or unaffordable checks without charge, and
replaces designated checks' results with a malformed record in malformed controls.
"""
from .domain import MALFORMED, outcome


class Denied(Exception):
    pass


class Gateway:
    def __init__(self, instance, files, budget):
        self._instance, self._files = instance, dict(files)
        self.budget, self.spent, self.log = budget, 0, []
        self.costs = {c["id"]: c["cost"] for c in instance["checks"]}

    @property
    def remaining(self):
        return self.budget - self.spent

    def run(self, cid):
        if cid not in self.costs:
            raise Denied(f"unknown check id {cid!r}")
        if any(entry["check"] == cid for entry in self.log):
            raise Denied(f"{cid} was already run; results are deterministic")
        if self.costs[cid] > self.remaining:
            raise Denied(f"{cid} costs {self.costs[cid]} but only {self.remaining} units remain")
        check = next(c for c in self._instance["checks"] if c["id"] == cid)
        result = MALFORMED if cid in self._instance["malformed"] else outcome(self._instance, check, self._files, self._instance["truth"])
        self.spent += self.costs[cid]
        self.log.append({"check": cid, "result": result, "cost": self.costs[cid], "spent": self.spent})
        return result

    def observations(self):
        return [(e["check"], e["result"]) for e in self.log]


def render_result(cid, result):
    if result == MALFORMED:
        return f"{cid}: MALFORMED record (log truncated; no usable result)"
    return f"{cid}: {result}"
