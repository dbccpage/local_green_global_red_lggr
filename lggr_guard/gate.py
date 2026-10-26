"""The composition gate: check a candidate against main plus everything accepted since the last full check.

AuthorityEffect: None. A receipt is evidence for the host's merge rule, not permission to merge.
Standard library only: Python 3.10+.

Statuses, most severe first:
  GUARD_PROBE_FAILED       a contract no longer rejects its own known-bad probe
  AUTHORITY_REQUIRED       the candidate edits a protected path, or the ledger was written under another suite
  MERGE_CONFLICT           the candidate does not apply on top of the pending changes
  LOCAL_RED                the candidate breaks a contract on its own
  LOCAL_GREEN_GLOBAL_RED   each change passes alone; a named set of them breaks a named contract
  MODEL_MISMATCH           observations fall outside the declared model (undeclared or out-of-domain effects)
  COMPOSITION_VERIFIED     every contract holds on the composition and every observed effect was declared
"""
from __future__ import annotations

from typing import Any, Callable, Sequence

from lggr import StreamingFiberMonitor
from lggr.common import digest, json_value

from .replay import CompositionError
from .ledger import Ledger
from .model import Candidate, Contract, Facts, Suite

SCHEMA = "lggr_guard.receipt.v1"
PRIORITY = ("GUARD_PROBE_FAILED", "AUTHORITY_REQUIRED", "MERGE_CONFLICT", "BASE_RED", "LOCAL_RED",
            "LOCAL_GREEN_GLOBAL_RED", "MODEL_MISMATCH")


def minimal_failing_set(pending: Sequence[Candidate], fails: Callable[[Sequence[Candidate]], bool]) -> list[Candidate]:
    """Shrink ``pending`` to a 1-minimal subset that still fails: dropping any one member makes it pass.

    Linear in ``len(pending)`` compositions when one change is to blame, quadratic at worst.
    """
    keep = list(pending)
    i = 0
    while i < len(keep):
        trial = keep[:i] + keep[i + 1:]
        if fails(trial):
            keep = trial
        else:
            i += 1
    return keep


class CompositionGate:
    """Host-owned. Build it from a suite read from main, a composer rooted at the last checkpoint, and the ledger."""

    def __init__(self, suite: Suite, composer: Any, ledger: Ledger, *, scope_id: str = "lggr-guard") -> None:
        self.suite = suite
        self.composer = composer
        self.ledger = ledger
        self._cache: dict[tuple[str, ...], dict[str, Any] | CompositionError] = {}
        # Declaration sufficiency: do declarations determine observed effects? (guide 01's collision monitor)
        self.declaration_monitor = StreamingFiberMonitor(scope_id=f"{scope_id}/declarations")

    # ------------------------------------------------------------ helpers
    def _facts(self, changes: Sequence[Candidate]) -> dict[str, Any]:
        key = tuple(c.change_id for c in changes)
        if key not in self._cache:
            try:
                self._cache[key] = self.composer.facts(changes)
            except CompositionError as exc:
                self._cache[key] = exc
        hit = self._cache[key]
        if isinstance(hit, CompositionError):
            raise hit
        return hit

    def _anchor(self, base_facts: Facts) -> dict[str, Any]:
        return self.ledger.anchor_facts or dict(base_facts)

    def _broken(self, facts: Facts, anchor: Facts) -> list[Contract]:
        out = []
        for contract in self.suite.contracts:
            try:
                ok = bool(contract.holds(facts, anchor))
            except Exception:
                ok = False
            if not ok:
                out.append(contract)
        return out

    def _breaks(self, changes: Sequence[Candidate], contract: Contract, anchor: Facts) -> bool:
        try:
            facts = self._facts(changes)
        except CompositionError:
            return True
        return contract in self._broken(facts, anchor)

    def probe_suite(self) -> list[dict[str, Any]]:
        """Every contract must still reject its probe. Run before every check."""
        findings = []
        for contract in self.suite.contracts:
            if contract.probe is None:
                continue
            facts, anchor = contract.probe
            try:
                accepted = bool(contract.holds(facts, anchor))
            except Exception:
                accepted = False  # raising on bad input still rejects it
            if accepted:
                findings.append({"kind": "GUARD_PROBE_FAILED", "contract": contract.contract_id,
                                 "message": "Contract accepted its own known-bad probe."})
        return findings

    def model_findings(self, facts: Facts) -> list[dict[str, Any]]:
        fmap = self.suite.fact_map
        out = []
        for name, value in facts.items():
            if name not in fmap:
                out.append({"kind": "MODEL_MISMATCH", "code": "UNDECLARED_FACT", "fact": name, "value": value,
                            "message": "Observer reported a fact the suite does not declare."})
            elif not fmap[name].admits(value):
                out.append({"kind": "MODEL_MISMATCH", "code": "OUT_OF_DOMAIN", "fact": name, "value": value,
                            "message": "Observed value is outside the fact's declared domain."})
        for name in fmap:
            if name not in facts:
                out.append({"kind": "MODEL_MISMATCH", "code": "FACT_NOT_OBSERVED", "fact": name,
                            "message": "Observer did not report a declared fact."})
        return out

    # -------------------------------------------------------------- check
    def check(self, candidate: Candidate) -> dict[str, Any]:
        pending = self.ledger.pending()
        if any(c.change_id == candidate.change_id for c in pending):
            raise ValueError(f"{candidate.change_id} is already accepted since the last checkpoint")
        findings: list[dict[str, Any]] = self.probe_suite()

        touched = sorted(self.composer.touched(candidate))
        protected = [p for p in touched if any(p == q or p.startswith(q) for q in self.suite.protected_paths)]
        if protected:
            findings.append({"kind": "AUTHORITY_REQUIRED", "code": "PROTECTED_PATH", "paths": protected,
                             "message": "Candidate edits files the gate reads from main. Owner approval required; "
                                        "the gate keeps using main's version."})
        other_suites = sorted(set(self.ledger.suite_hashes()) - {self.suite.source_sha256})
        if other_suites:
            findings.append({"kind": "AUTHORITY_REQUIRED", "code": "SUITE_CHANGED_SINCE_CHECKPOINT",
                             "message": "Pending changes were accepted under a different suite. Run a full check "
                                        "and checkpoint before accepting more."})

        before = after = None
        try:
            before = self._facts(pending)
            after = self._facts([*pending, candidate])
        except CompositionError as exc:
            if before is None:
                findings.append({"kind": "MERGE_CONFLICT" if exc.code == "MERGE_CONFLICT" else "MODEL_MISMATCH",
                                 "code": f"PENDING_{exc.code}", "change": exc.change_id, "detail": exc.detail})
            elif exc.code == "MERGE_CONFLICT":
                culprits = minimal_failing_set(
                    pending, lambda subset: self._conflicts([*subset, candidate]))
                findings.append({"kind": "MERGE_CONFLICT", "code": "TEXTUAL_CONFLICT",
                                 "changes": [c.change_id for c in culprits] + [candidate.change_id],
                                 "detail": exc.detail})
            else:
                findings.append({"kind": "MODEL_MISMATCH", "code": exc.code, "detail": exc.detail,
                                 "message": "The composition could not be observed. Treated as out of model."})
        observed_delta: dict[str, Any] = {}
        if before is not None and after is not None:
            findings += self.model_findings(after)
            anchor = self._anchor(self._facts([]))
            already = {c.contract_id for c in self._broken(before, anchor)}
            if already:
                findings.append({"kind": "LOCAL_GREEN_GLOBAL_RED", "code": "PENDING_ALREADY_RED",
                                 "contracts": sorted(already),
                                 "message": "Main plus pending is red before this candidate. Run `python -m lggr_guard blame`."})
            for contract in self._broken(after, anchor):
                if contract.contract_id in already:
                    continue
                findings.append(self._attribute(contract, pending, candidate, anchor, before, after))
            observed_delta = {k: {"from": before.get(k), "to": after[k]}
                              for k in after if before.get(k) != after[k]}
            findings += self._declaration_findings(candidate, observed_delta, after)

        kinds = {f["kind"] for f in findings}
        status = next((k for k in PRIORITY if k in kinds), "COMPOSITION_VERIFIED")
        body = {
            "schema": SCHEMA,
            "authority_effect": "None",
            "status": status,
            "allowed": status == "COMPOSITION_VERIFIED",
            "candidate": candidate.change_id,
            "declares": dict(candidate.declares),
            "pending": [c.change_id for c in pending],
            "base": (self.ledger.checkpoint or {}).get("ref"),
            "observed_delta": observed_delta,
            "findings": findings,
            "unresolved_obligations": self.ledger.open_obligations()
            + [{"change_id": candidate.change_id, "obligation": o} for o in candidate.obligations],
            "declaration_sufficiency": self.declaration_monitor.get_receipt()["status"],
            "suite_sha256": self.suite.source_sha256,
            "compositions_built": self.composer.builds,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def _conflicts(self, changes: Sequence[Candidate]) -> bool:
        try:
            self._facts(changes)
            return False
        except CompositionError as exc:
            return exc.code == "MERGE_CONFLICT"

    def _attribute(self, contract: Contract, pending: Sequence[Candidate], candidate: Candidate,
                   anchor: Facts, before: Facts, after: Facts) -> dict[str, Any]:
        reads = {k: {"from": before.get(k), "to": after.get(k)} for k in contract.reads}
        if self._breaks([candidate], contract, anchor):
            return {"kind": "LOCAL_RED", "contract": contract.contract_id, "description": contract.description,
                    "changes": [candidate.change_id], "facts": reads,
                    "message": "The candidate breaks this contract on its own."}
        culprits = minimal_failing_set(pending, lambda subset: self._breaks([*subset, candidate], contract, anchor))
        names = [c.change_id for c in culprits] + [candidate.change_id]
        return {"kind": "LOCAL_GREEN_GLOBAL_RED", "contract": contract.contract_id,
                "description": contract.description, "changes": names, "facts": reads,
                "drop_any_one": "green",
                "message": f"{' + '.join(names)} jointly break {contract.contract_id}; "
                           "drop any one of them and it holds."}

    def _declaration_findings(self, candidate: Candidate, delta: dict[str, Any], after: Facts) -> list[dict[str, Any]]:
        out = []
        undeclared = sorted(set(delta) - set(candidate.declares))
        if undeclared:
            out.append({"kind": "MODEL_MISMATCH", "code": "UNDECLARED_EFFECT", "facts": undeclared,
                        "message": "The candidate changed behaviour it did not declare."})
        missing = sorted(k for k, v in candidate.declares.items() if after.get(k) != v)
        if missing:
            out.append({"kind": "MODEL_MISMATCH", "code": "DECLARED_EFFECT_ABSENT", "facts": missing,
                        "message": "The candidate declared effects that were not observed."})
        uncovered = sorted(k for k in delta if not self.suite.readers(k))
        if uncovered:
            out.append({"kind": "MODEL_MISMATCH", "code": "UNCOVERED_EFFECT", "facts": uncovered,
                        "message": "Observed effect is read by no contract. Add a contract or confirm with the owner."})
        report = {"declares": dict(candidate.declares)}
        query = {k: v["to"] for k, v in sorted(delta.items())}
        self.declaration_monitor.observe(candidate.change_id, report, query)
        return out

    # -------------------------------------------------------------- blame
    def blame(self) -> dict[str, Any]:
        """After a failed post-merge smoke: name the minimal pending set behind each broken contract."""
        pending = self.ledger.pending()
        findings = self.probe_suite()
        try:
            base = self._facts([])
            facts = self._facts(pending)
        except CompositionError as exc:
            findings.append({"kind": "MODEL_MISMATCH", "code": exc.code, "detail": exc.detail})
            facts = None
        if facts is not None:
            findings += self.model_findings(facts)
            anchor = self._anchor(base)
            for contract in self._broken(facts, anchor):
                culprits = minimal_failing_set(pending, lambda s, c=contract: self._breaks(s, c, anchor))
                kind = {0: "BASE_RED", 1: "LOCAL_RED"}.get(len(culprits), "LOCAL_GREEN_GLOBAL_RED")
                findings.append({"kind": kind, "contract": contract.contract_id,
                                 "changes": [c.change_id for c in culprits],
                                 "facts": {k: {"from": base.get(k), "to": facts.get(k)} for k in contract.reads}})
        kinds = {f["kind"] for f in findings}
        status = next((k for k in PRIORITY if k in kinds), "COMPOSITION_VERIFIED")
        body = {"schema": SCHEMA, "authority_effect": "None", "status": status, "mode": "blame",
                "pending": [c.change_id for c in pending], "findings": findings,
                "suite_sha256": self.suite.source_sha256, "compositions_built": self.composer.builds}
        return json_value({**body, "receipt_sha256": digest(body)})
