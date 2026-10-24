"""Finite examples for Institutions That Can Know, version 0.1.

Python 3.10+, standard library only. These utilities check finite models;
they do not authenticate real evidence, grant authority, or run an AI council.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Hashable, Iterable, Mapping, Sequence, TypeVar

X = TypeVar('X', bound=Hashable)
Y = TypeVar('Y', bound=Hashable)
Z = TypeVar('Z', bound=Hashable)


def _domain(records: Iterable[X]) -> tuple[X, ...]:
    """Materialize a finite nonempty domain without silently merging records."""
    result = tuple(records)
    if not result:
        raise ValueError('The admitted domain must be nonempty.')
    if len(set(result)) != len(result):
        raise ValueError('Duplicate domain records are not admitted.')
    return result


def recovery_decoder(
    records: Iterable[X],
    compression: Callable[[X], Y],
    question: Callable[[X], Z],
) -> dict[Y, Z] | None:
    """Return the exact finite decoder, or None for a witnessed collision.

    Assumes the supplied functions are deterministic. Only the given domain
    is checked; the function makes no assertion about unseen records.
    """
    table: dict[Y, Z] = {}
    for record in _domain(records):
        y, answer = compression(record), question(record)
        if y in table and table[y] != answer:
            return None
        table[y] = answer
    return table


def minimum_fixed_side_bits(
    records: Iterable[X],
    compression: Callable[[X], Y],
    profile: Callable[[X], Z],
) -> int:
    """Exact Proposition 3 bound; excludes codebook/specification cost."""
    fibers: dict[Y, set[Z]] = defaultdict(set)
    for record in _domain(records):
        fibers[compression(record)].add(profile(record))
    maximum = max(map(len, fibers.values()))
    return (maximum - 1).bit_length()  # Exact ceil(log2(maximum)).


def side_information_code(
    records: Iterable[X],
    compression: Callable[[X], Y],
    profile: Callable[[X], Z],
) -> tuple[int, dict[X, int], dict[tuple[Y, int], Z]]:
    """Construct a code attaining the finite bound, with shared codebooks.

    Indices depend on first occurrence in the supplied ordered domain.
    This is not a claim of optimal runtime or compact codebook storage.
    """
    domain = _domain(records)
    indices: dict[Y, dict[Z, int]] = defaultdict(dict)
    encoder: dict[X, int] = {}
    decoder: dict[tuple[Y, int], Z] = {}
    for record in domain:
        y, value = compression(record), profile(record)
        local = indices[y]
        if value not in local:
            local[value] = len(local)
        code = local[value]
        encoder[record] = code
        decoder[y, code] = value
    bits = (max(map(len, indices.values())) - 1).bit_length()
    return bits, encoder, decoder


class ComparisonStatus(str, Enum):
    FOUND = 'comparison_found'
    NO_ADMITTED_COMPARISON = 'no_admitted_comparison'
    CERTIFIED_NON_EQUIVALENT = 'certified_non_equivalent'


def bounded_search(candidates: Sequence[bool]) -> ComparisonStatus:
    """Failure in a supplied candidate list is not an impossibility proof."""
    return (ComparisonStatus.FOUND if any(candidates)
            else ComparisonStatus.NO_ADMITTED_COMPARISON)


def invariant_separates(
    left: Z, right: Z, *, invariant_preservation_verified: bool
) -> ComparisonStatus:
    """Model a relative certificate; the Boolean is a fixture, not a verifier."""
    if not invariant_preservation_verified:
        return ComparisonStatus.NO_ADMITTED_COMPARISON
    if left != right:
        return ComparisonStatus.CERTIFIED_NON_EQUIVALENT
    # Equal invariants need not be a complete equivalence test.
    return ComparisonStatus.NO_ADMITTED_COMPARISON


def jointly_acceptable(action_sets: Sequence[set[str]]) -> set[str]:
    if not action_sets:
        raise ValueError('At least one participant is required.')
    return set.intersection(*(set(actions) for actions in action_sets))


@dataclass(frozen=True)
class FixtureMandate:
    """Sandbox record only: external verification is not implemented here."""
    mandate_id: str
    executor: str
    allowed_actions: frozenset[str]
    expires_at: int
    externally_verified: bool = False


def permitted_in_fixture(
    action: str, executor: str, now: int, mandate: FixtureMandate | None
) -> bool:
    """No votes or persuasive findings can substitute for the fixture mandate."""
    return bool(
        mandate is not None
        and mandate.mandate_id
        and mandate.externally_verified
        and mandate.executor == executor
        and action in mandate.allowed_actions
        and now < mandate.expires_at
    )


def reachable(graph: Mapping[str, Iterable[str]], start: str, target: str) -> bool:
    """Directed finite reachability; missing node entries have no outgoing edges."""
    queue = deque([start])
    seen = {start}
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        for neighbor in graph.get(node, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return False
