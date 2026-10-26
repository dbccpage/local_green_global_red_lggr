"""Declared model for the composition gate: facts, contracts, changes, suite.

AuthorityEffect: None.
Standard library only: Python 3.10+.

A *fact* is one observable property of the running system (``precheck.bounces_undeclared``).
A *contract* is a predicate over facts that must hold on every composition.
A *change* carries what it declares it will alter. The host, not the change,
observes what it actually alters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any, Callable, Mapping

from lggr.common import ValidationError, canonical

Facts = Mapping[str, Any]


@dataclass(frozen=True)
class Fact:
    """One observable. ``allowed`` is a tuple of legal values, or None for any exact JSON scalar."""

    name: str
    allowed: tuple[Any, ...] | None = None
    description: str = ""

    def admits(self, value: Any) -> bool:
        if type(value) not in (bool, int, str) and value is not None:
            return False
        return self.allowed is None or value in self.allowed


@dataclass(frozen=True)
class Contract:
    """A global obligation. ``holds(facts, anchor)`` must return True on every accepted composition.

    ``anchor`` holds the owner-approved facts, so a contract can bound cumulative drift
    rather than step size. ``probe`` is a ``(facts, anchor)`` pair the contract must
    reject; the gate runs every probe before every check, so a contract that has
    stopped rejecting known-bad input stops the gate.
    """

    contract_id: str
    reads: tuple[str, ...]
    holds: Callable[[Facts, Facts], bool]
    description: str = ""
    probe: tuple[Facts, Facts] | None = None


@dataclass(frozen=True)
class Candidate:
    """A candidate or accepted change.

    ``declares`` maps each fact the change says it alters to its new value; an empty
    mapping says "no behaviour change". ``ref`` is composer-specific: a
    ``(parent_sha, head_sha)`` pair for git, a callable or dict patch in memory.
    """

    change_id: str
    declares: Mapping[str, Any] = field(default_factory=dict)
    obligations: tuple[str, ...] = ()
    ref: Any = None


def drift_budget(contract_id: str, fact: str, max_total: int, *, description: str = "") -> Contract:
    """Cumulative bound: |fact - anchor[fact]| <= max_total, however many steps it took."""

    def holds(facts: Facts, anchor: Facts) -> bool:
        return abs(int(facts[fact]) - int(anchor[fact])) <= max_total

    return Contract(contract_id, (fact,), holds,
                    description or f"{fact} stays within {max_total} of the owner-approved anchor",
                    probe=({fact: max_total + 1}, {fact: 0}))


def equals(contract_id: str, fact: str, value: Any, *, description: str = "") -> Contract:
    """Pin one fact. The probe is the same fact with any other value."""
    bad = (not value) if isinstance(value, bool) else f"not-{value}"
    return Contract(contract_id, (fact,), lambda facts, _anchor: facts[fact] == value,
                    description or f"{fact} == {value!r}", probe=({fact: bad}, {}))


@dataclass
class Suite:
    """Everything the gate trusts, loaded from main and never from the candidate."""

    facts: tuple[Fact, ...]
    contracts: tuple[Contract, ...]
    observe: Callable[[Any], dict[str, Any]]
    protected_paths: tuple[str, ...] = (".lggr/",)
    source_sha256: str = ""

    def __post_init__(self) -> None:
        names = [f.name for f in self.facts]
        if len(set(names)) != len(names):
            raise ValidationError("fact names must be unique")
        ids = [c.contract_id for c in self.contracts]
        if len(set(ids)) != len(ids):
            raise ValidationError("contract ids must be unique")
        for contract in self.contracts:
            unknown = set(contract.reads) - set(names)
            if unknown:
                raise ValidationError(f"contract {contract.contract_id} reads undeclared facts {sorted(unknown)}")
        if not self.source_sha256:
            ids_text = canonical({"facts": names, "contracts": ids, "protected": list(self.protected_paths)})
            self.source_sha256 = hashlib.sha256(ids_text.encode()).hexdigest()

    @property
    def fact_map(self) -> dict[str, Fact]:
        return {f.name: f for f in self.facts}

    def readers(self, fact: str) -> list[str]:
        return [c.contract_id for c in self.contracts if fact in c.reads]
