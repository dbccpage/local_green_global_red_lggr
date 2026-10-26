"""Finite query fixtures with explicit coverage and transport requirements."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable, Dict, FrozenSet, List

from models import Terminal, TerminalStatus
from pipeline import Refusal, RefusalM, Success


@dataclass(frozen=True)
class FiniteShadow:
    """A local finite check with declared query coverage and checked horizon."""
    index: str
    projection_data: Any
    covered_queries: FrozenSet[str]
    coherent_through: int
    is_valid: bool


@dataclass(frozen=True)
class TransportCertificate:
    """A trusted structural transport assertion for one query and one shadow pair."""
    source_index: str
    target_index: str
    query: str
    loss_bound: Fraction
    is_certified: bool

    def __post_init__(self) -> None:
        if not isinstance(self.loss_bound, Fraction):
            raise TypeError("Transport loss bounds must use exact Fraction values")
        if self.loss_bound < 0:
            raise ValueError("Transport loss bounds must be non-negative")


def evaluate_query_relative_coherence(
    continuum_object: Any,
    query: str,
    shadows: List[FiniteShadow],
    certificates: List[TransportCertificate],
    verifiers: Dict[str, Callable[[Any, str], bool]],
    maximum_loss: Fraction = Fraction(1, 20),
) -> RefusalM[Terminal]:
    """Check a declared finite query contract and return only bounded coherence.

    ``continuum_object`` remains an external semantic object: this fixture does
    not prove a cofinal approximation theorem or grant execution authority.
    """
    del continuum_object
    if not shadows:
        return Refusal("No finite shadows provided: continuum objects cannot self-authorize")

    indexes = [shadow.index for shadow in shadows]
    if len(set(indexes)) != len(indexes):
        return Refusal("Finite-shadow indexes must be unique")
    if any(query not in shadow.covered_queries for shadow in shadows):
        return Refusal(f"Query {query} lacks declared coverage at one or more finite shadows")

    for shadow in shadows:
        if not shadow.is_valid:
            return Refusal(f"Finite shadow {shadow.index} failed local verification")
        verifier = verifiers.get(shadow.index)
        if verifier is None or not verifier(shadow.projection_data, query):
            return Refusal(f"Query {query} refused at finite shadow {shadow.index}")

    expected_pairs = {
        frozenset((left.index, right.index))
        for position, left in enumerate(shadows)
        for right in shadows[position + 1 :]
    }
    seen_pairs: set[frozenset[str]] = set()
    for certificate in certificates:
        pair = frozenset((certificate.source_index, certificate.target_index))
        if (
            len(pair) != 2
            or pair not in expected_pairs
            or certificate.query != query
            or not certificate.is_certified
            or certificate.loss_bound > maximum_loss
            or pair in seen_pairs
        ):
            return Refusal("Finite-shadow transport contract is incomplete or incompatible")
        seen_pairs.add(pair)
    if seen_pairs != expected_pairs:
        return Refusal("Finite-shadow transport coverage is incomplete for the declared query")

    checked_horizon = min(shadow.coherent_through for shadow in shadows)
    return Success(
        Terminal(
            status=TerminalStatus.COHERENT_UP_TO,
            reason=f"Query {query} is coherently checked through finite horizon {checked_horizon}",
        )
    )


def evaluate_query_relative_authority(*args: Any, **kwargs: Any) -> RefusalM[Terminal]:
    """Compatibility name; finite shadows yield bounded coherence, never authority."""
    return evaluate_query_relative_coherence(*args, **kwargs)
