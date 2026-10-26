"""Frozen decisions: detect when a hosted reviewer/evaluator has changed under you.

Record past accepted/rejected decisions with their inputs. Before trusting a reviewer
(after a provider update, a prompt edit, or periodically), replay the frozen cases and
compare. Disagreement above the threshold means the evaluator is no longer the one
that produced your history: treat its verdicts as out-of-model until a human re-anchors.

In our 3,600-session swarm experiment every false accept, by agents and by the
deterministic host rule alike, came from out-of-model cases where the world had moved
outside the declared model. Pass/fail checks agreed with each other and were both
wrong. That failure needs an explicit mismatch alarm; this is one.

AuthorityEffect: None.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class FrozenDecisions:
    def __init__(self, path):
        self.path = Path(path)
        self.cases = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []

    def freeze(self, case_id, case_input, decision):
        """Add an owner-confirmed decision. Cases are never edited, only appended."""
        if any(c["id"] == case_id for c in self.cases):
            raise ValueError(f"case {case_id!r} already frozen")
        self.cases.append({"id": case_id, "input": case_input, "decision": decision, "input_sha256": _digest(case_input)})
        self.path.write_text(json.dumps(self.cases, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    def replay(self, reviewer, min_agreement=0.95):
        """Run `reviewer(case_input) -> decision` on every frozen case."""
        mismatches = []
        for case in self.cases:
            if _digest(case["input"]) != case["input_sha256"]:
                raise ValueError(f"frozen case {case['id']} was edited")
            got = reviewer(case["input"])
            if got != case["decision"]:
                mismatches.append({"id": case["id"], "frozen": case["decision"], "now": got})
        n = len(self.cases)
        agreement = 1.0 if n == 0 else 1 - len(mismatches) / n
        return {"cases": n, "agreement": agreement, "mismatches": mismatches,
                "alarm": agreement < min_agreement,
                "meaning": "evaluator changed: treat its verdicts as out-of-model until re-anchored"
                           if agreement < min_agreement else "evaluator matches frozen history"}
