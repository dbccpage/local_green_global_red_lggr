"""Deterministic core implementation for representation abundance and finite selectors.

This module formalizes:
1. Witnessed difference quotients and observer equivalence classes.
2. Finite terminal selectors with deterministic verifiers and terminalizers.
3. The Local-Green Global-Red boundary gate over discrete cochain complexes.
4. Concrete landscape vacua evaluations with exact rational arithmetic.

All mathematical computations use exact rational arithmetic (fractions.Fraction)
to eliminate floating-point drift and ensure local reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from types import MappingProxyType
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple


def _to_exact_fraction(val: object, field_name: str = "value") -> Fraction:
    """Convert an input to an exact Fraction, rejecting Python floats.

    Accepts:
        - fractions.Fraction instances (returned unchanged)
        - int instances
        - str representing integers, rationals ('p/q'), or explicit decimals ('0.1')

    Rejects:
        - float instances (to prevent precision drift and spurious discrepancies)
        - any other non-convertible type
    """
    if isinstance(val, bool):
        raise TypeError(f"Boolean input {field_name} is not an exact numeric value.")
    if isinstance(val, float):
        raise TypeError(
            f"Floating-point input {field_name}={val!r} is rejected to prevent precision drift. "
            "Pass an exact int, decimal string (e.g. '0.1'), or fractions.Fraction."
        )
    if isinstance(val, Fraction):
        return val
    if isinstance(val, (int, str)):
        return Fraction(val)
    raise TypeError(
        f"Unsupported type {type(val).__name__} for {field_name}; expected int, str, or Fraction."
    )


class TerminalVerdict(str, Enum):
    """Candidate verifier and family terminal categories; their allowed subsets differ."""

    ACCEPTED = "ACCEPTED"
    SURVIVOR = "SURVIVOR"
    REFUTED = "REFUTED"
    UNDERDETERMINED = "UNDERDETERMINED"
    REFUSED = "REFUSED"


@dataclass(frozen=True)
class ObservableDatum:
    """An exact observed datum with measurement tolerance."""

    name: str
    value: Fraction
    tolerance: Fraction = field(default_factory=lambda: Fraction(0, 1))

    def __post_init__(self) -> None:
        if isinstance(self.value, float) or isinstance(self.tolerance, float):
            raise TypeError(
                "Floating-point values are rejected; use int, decimal string, or Fraction."
            )
        if not isinstance(self.value, Fraction):
            object.__setattr__(
                self, "value", _to_exact_fraction(self.value, f"value for '{self.name}'")
            )
        if not isinstance(self.tolerance, Fraction):
            object.__setattr__(
                self,
                "tolerance",
                _to_exact_fraction(self.tolerance, f"tolerance for '{self.name}'"),
            )
        if self.tolerance < 0:
            raise ValueError(f"Tolerance must be non-negative, got {self.tolerance}")


@dataclass(frozen=True)
class EvidenceRecord:
    """A finite record of observed evidence.

    Premise Note (External Certification):
        The operational selector takes certified evidence as an explicit input premise.
        Verification of instrumental calibration, experimental provenance, and certificate
        authenticity occurs upstream / outside this deterministic computational selector.
    """

    record_id: str
    observables: Mapping[str, ObservableDatum]
    certificate: Optional[str] = None

    def __post_init__(self) -> None:
        clean_obs = {}
        for k, v in self.observables.items():
            if isinstance(v, ObservableDatum):
                clean_obs[k] = v
            elif isinstance(v, tuple) and len(v) == 2:
                clean_obs[k] = ObservableDatum(
                    name=k,
                    value=_to_exact_fraction(v[0], f"value for '{k}'"),
                    tolerance=_to_exact_fraction(v[1], f"tolerance for '{k}'"),
                )
            else:
                raise TypeError(
                    f"Expected ObservableDatum or (value, tolerance) tuple for '{k}', got {type(v).__name__}"
                )
        object.__setattr__(self, "observables", MappingProxyType(clean_obs))

    @classmethod
    def from_dict(
        cls,
        record_id: str,
        data: Mapping[str, Tuple[int | str | Fraction, int | str | Fraction]],
        certificate: Optional[str] = None,
    ) -> EvidenceRecord:
        """Create evidence record from mapping of name -> (value, tolerance)."""
        obs = {}
        for k, (v, tol) in data.items():
            obs[k] = ObservableDatum(
                name=k,
                value=_to_exact_fraction(v, f"value for '{k}'"),
                tolerance=_to_exact_fraction(tol, f"tolerance for '{k}'"),
            )
        return cls(record_id=record_id, observables=obs, certificate=certificate)


@dataclass(frozen=True)
class CandidateModel:
    """A candidate model within a representation proposal space."""

    candidate_id: str
    predictions: Mapping[str, Fraction]
    internal_parameters: Mapping[str, Fraction] = field(default_factory=dict)

    def __post_init__(self) -> None:
        clean_preds = {
            k: _to_exact_fraction(v, f"prediction for '{k}'") for k, v in self.predictions.items()
        }
        object.__setattr__(self, "predictions", MappingProxyType(clean_preds))

        clean_params = {
            k: _to_exact_fraction(v, f"parameter for '{k}'")
            for k, v in self.internal_parameters.items()
        }
        object.__setattr__(self, "internal_parameters", MappingProxyType(clean_params))

    @classmethod
    def from_dict(
        cls,
        candidate_id: str,
        predictions: Mapping[str, int | str | Fraction],
        params: Optional[Mapping[str, int | str | Fraction]] = None,
    ) -> CandidateModel:
        preds = {k: _to_exact_fraction(v, f"prediction for '{k}'") for k, v in predictions.items()}
        p_dict = {}
        if params:
            p_dict = {k: _to_exact_fraction(v, f"parameter for '{k}'") for k, v in params.items()}
        return cls(candidate_id=candidate_id, predictions=preds, internal_parameters=p_dict)


@dataclass(frozen=True)
class EvaluationReceipt:
    """Receipt documenting verification of a candidate model against evidence."""

    candidate_id: str
    evidence_record_id: str
    discrepancies: Mapping[str, Fraction]
    max_discrepancy: Fraction
    l1_discrepancy: Fraction
    is_consistent: bool
    is_complete: bool
    verdict: TerminalVerdict
    details: str

    def __post_init__(self) -> None:
        if self.verdict not in {
            TerminalVerdict.SURVIVOR,
            TerminalVerdict.REFUTED,
            TerminalVerdict.REFUSED,
        }:
            raise ValueError("Candidate receipts require a candidate-level verdict.")
        object.__setattr__(self, "discrepancies", MappingProxyType(dict(self.discrepancies)))


@dataclass(frozen=True)
class FamilySelectionResult:
    """Family terminalization bound to the declared alternatives and evidence ID."""

    evidence_record_id: str
    candidate_ids: Tuple[str, ...]
    verdict: TerminalVerdict
    selected_candidate_id: Optional[str]
    receipts: Mapping[str, EvaluationReceipt]

    def __post_init__(self) -> None:
        object.__setattr__(self, "receipts", MappingProxyType(dict(self.receipts)))


class WitnessedDifferenceQuotient:
    """Analyzes candidate representation spaces modulo observer evaluation equivalence."""

    def __init__(self, observer_observables: Sequence[str]):
        self.observer_observables = tuple(sorted(observer_observables))

    def observe(self, candidate: CandidateModel) -> Tuple[Tuple[str, Optional[Fraction]], ...]:
        """Project a candidate to the observer's observable profile."""
        profile = []
        for obs in self.observer_observables:
            val = candidate.predictions.get(obs)
            profile.append((obs, val))
        return tuple(profile)

    def partition_quotient(
        self, candidates: Sequence[CandidateModel]
    ) -> Dict[Tuple[Tuple[str, Optional[Fraction]], ...], List[CandidateModel]]:
        """Partition candidates into equivalence classes S / ker(O)."""
        if not candidates:
            return {}
        identifiers = [c.candidate_id for c in candidates]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(
                "Candidate identifiers must be unique within a declared candidate family."
            )

        quotient: Dict[Tuple[Tuple[str, Optional[Fraction]], ...], List[CandidateModel]] = {}
        for c in candidates:
            profile = self.observe(c)
            if profile not in quotient:
                quotient[profile] = []
            quotient[profile].append(c)
        return quotient

    def underdetermination_ratio(self, candidates: Sequence[CandidateModel]) -> Fraction:
        """Compute the ratio |F| / |F / ker(O)|.

        The underdetermination ratio is defined only for non-empty candidate families F
        with unique candidate identifiers. A ratio > 1 indicates that representation
        abundance exceeds observer distinction capacity.
        """
        if not candidates:
            raise ValueError(
                "Underdetermination ratio is defined only for non-empty candidate families."
            )

        identifiers = [c.candidate_id for c in candidates]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(
                "Candidate identifiers must be unique within a declared candidate family."
            )

        quotient = self.partition_quotient(candidates)
        return Fraction(len(candidates), len(quotient))

    def observation_decision_agrees(
        self,
        first: CandidateModel,
        second: CandidateModel,
        decision: Callable[[Tuple[Tuple[str, Optional[Fraction]], ...]], object],
    ) -> bool:
        """Finite instance of observation_decision_agrees.

        Returns False unless the two candidates are distinct and share an
        observation profile. Otherwise the decision, which receives only that
        profile, agrees on both.
        """
        if first.candidate_id == second.candidate_id:
            return False
        profile_first = self.observe(first)
        profile_second = self.observe(second)
        if profile_first != profile_second:
            return False
        return decision(profile_first) == decision(profile_second)

    def plenitude_inflates(
        self,
        family: Sequence[CandidateModel],
        extended: Sequence[CandidateModel],
    ) -> bool:
        """Finite instance of plenitude_inflation.

        Returns False unless ``family`` is a nonempty proper identifier subset
        of ``extended``, retained identifiers have identical model content, and the
        two families have the same observation profiles.
        Otherwise compares the shipped underdetermination ratios.
        """
        if not family or not extended:
            return False
        family_ids = [candidate.candidate_id for candidate in family]
        extended_ids = [candidate.candidate_id for candidate in extended]
        if len(set(family_ids)) != len(family_ids) or len(set(extended_ids)) != len(extended_ids):
            return False
        if not set(family_ids) < set(extended_ids):
            return False
        retained = {candidate.candidate_id: candidate for candidate in extended}
        if any(retained[candidate.candidate_id] != candidate for candidate in family):
            return False
        family_profiles = set(self.partition_quotient(family))
        extended_profiles = set(self.partition_quotient(extended))
        if family_profiles != extended_profiles:
            return False
        return self.underdetermination_ratio(extended) > self.underdetermination_ratio(family)


class FiniteTerminalSelector:
    """Evaluate a declared finite family against explicit, per-observable evidence.

    The selector never manufactures a discrepancy for unavailable data and never
    substitutes a global tolerance for an explicitly declared zero tolerance.
    Incomplete evidence routes to ``REFUSED`` rather than to refutation or
    acceptance.
    """

    def verify_candidate(
        self, evidence: EvidenceRecord, candidate: CandidateModel
    ) -> EvaluationReceipt:
        """Run deterministic verification of a candidate against an evidence record."""
        discrepancies: Dict[str, Fraction] = {}
        missing: List[str] = []
        is_consistent = True

        if not evidence.observables:
            return EvaluationReceipt(
                candidate_id=candidate.candidate_id,
                evidence_record_id=evidence.record_id,
                discrepancies={},
                max_discrepancy=Fraction(0, 1),
                l1_discrepancy=Fraction(0, 1),
                is_consistent=False,
                is_complete=False,
                verdict=TerminalVerdict.REFUSED,
                details="Selection refused: the evidence record contains no observables.",
            )

        for name, obs in evidence.observables.items():
            if name not in candidate.predictions:
                missing.append(name)
                is_consistent = False
                continue

            pred = candidate.predictions[name]
            diff = abs(pred - obs.value)
            discrepancies[name] = diff
            if diff > obs.tolerance:
                is_consistent = False

        if not discrepancies:
            max_d = Fraction(0, 1)
            l1_d = Fraction(0, 1)
        else:
            max_d = max(discrepancies.values())
            l1_d = sum(discrepancies.values())

        if missing:
            verdict = TerminalVerdict.REFUSED
            details = (
                f"Selection refused: candidate {candidate.candidate_id} has no prediction for "
                f"{', '.join(sorted(missing))}."
            )
        elif not is_consistent:
            verdict = TerminalVerdict.REFUTED
            details = (
                f"Candidate {candidate.candidate_id} refuted by evidence: max discrepancy {max_d}."
            )
        else:
            verdict = TerminalVerdict.SURVIVOR
            details = (
                f"Candidate {candidate.candidate_id} consistent with evidence within tolerance."
            )

        return EvaluationReceipt(
            candidate_id=candidate.candidate_id,
            evidence_record_id=evidence.record_id,
            discrepancies=discrepancies,
            max_discrepancy=max_d,
            l1_discrepancy=l1_d,
            is_consistent=is_consistent,
            is_complete=not missing,
            verdict=verdict,
            details=details,
        )

    def select_family(
        self, evidence: EvidenceRecord, candidates: Sequence[CandidateModel]
    ) -> FamilySelectionResult:
        """Return family context; candidate receipts retain their verifier verdicts.

        Callers use result.verdict and result.receipts rather than tuple unpacking.
        Evidence IDs are supplied labels, not authenticity certificates.
        """
        identifiers = tuple(candidate.candidate_id for candidate in candidates)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Candidate identifiers must be unique within a declared family")
        receipts = {
            candidate.candidate_id: self.verify_candidate(evidence, candidate)
            for candidate in candidates
        }
        survivors = [
            identifier
            for identifier, receipt in receipts.items()
            if receipt.verdict == TerminalVerdict.SURVIVOR
        ]
        if not candidates or any(not receipt.is_complete for receipt in receipts.values()):
            verdict = TerminalVerdict.REFUSED
        elif not survivors:
            verdict = TerminalVerdict.REFUTED
        elif len(survivors) == 1:
            verdict = TerminalVerdict.ACCEPTED
        else:
            verdict = TerminalVerdict.UNDERDETERMINED
        return FamilySelectionResult(
            evidence_record_id=evidence.record_id,
            candidate_ids=identifiers,
            verdict=verdict,
            selected_candidate_id=survivors[0] if verdict == TerminalVerdict.ACCEPTED else None,
            receipts=receipts,
        )

    def acceptance_relaxes_when_another_survivor_joins(
        self,
        evidence: EvidenceRecord,
        family: Sequence[CandidateModel],
        extra: CandidateModel,
    ) -> bool:
        """Check loss of unique family selection when a new survivor is added."""
        if extra.candidate_id in {candidate.candidate_id for candidate in family}:
            return False
        original = self.select_family(evidence, family)
        if original.verdict != TerminalVerdict.ACCEPTED or original.selected_candidate_id is None:
            return False
        enlarged = self.select_family(evidence, [*family, extra])
        return (
            enlarged.verdict == TerminalVerdict.UNDERDETERMINED
            and enlarged.receipts[original.selected_candidate_id].verdict
            == TerminalVerdict.SURVIVOR
        )


@dataclass(frozen=True)
class DirectedEdge:
    """A directed edge between two discrete vertices."""

    source: int
    target: int


class LocalGreenGlobalRedGate:
    """Evaluates 1-cochain cycle complexes to detect False-Green conditions and cycle obstructions.

    Models a discrete graph G = (V, E) with cochain spaces:
    C^0(V, Q) -> C^1(E, Q) via coboundary d_0.
    """

    def __init__(self, num_vertices: int, edges: Sequence[Tuple[int, int]]):
        if type(num_vertices) is not int or num_vertices < 0:
            raise ValueError("num_vertices must be a nonnegative integer.")
        self.num_vertices = num_vertices
        self.edges = tuple(DirectedEdge(u, v) for u, v in edges)
        unoriented = set()
        for edge in self.edges:
            if any(
                type(v) is not int or not 0 <= v < num_vertices for v in (edge.source, edge.target)
            ):
                raise ValueError("Edge vertices must be integer indices in the graph.")
            key = frozenset((edge.source, edge.target))
            if edge.source == edge.target or key in unoriented:
                raise ValueError("Store one orientation per edge, without loops or duplicates.")
            unoriented.add(key)
        self.edge_index = {self.edges[i]: i for i in range(len(self.edges))}

    def validate_cycle(self, cycle_edges: Sequence[Tuple[int, int, int]]) -> None:
        """Validate that cycle_edges is non-empty, uses valid graph edges, and forms a closed cycle.

        Each element of cycle_edges is (u, v, sign) where sign is in {-1, 1}.
        If sign == 1, the step traverses along the edge u -> v.
        If sign == -1, the step traverses along the edge v -> u.
        The step must use an edge existing in self.edges.
        """
        if not cycle_edges:
            raise ValueError("Cycle must be non-empty.")

        traversed_steps: List[Tuple[int, int]] = []
        for idx, step in enumerate(cycle_edges):
            if len(step) != 3:
                raise ValueError(f"Step {idx} must be a 3-tuple (u, v, sign), got {step}")
            u, v, sign = step
            if type(sign) is not int or sign not in (-1, 1):
                raise ValueError(f"Step {idx}: sign must be +1 or -1, got {sign}")
            if type(u) is not int or type(v) is not int:
                raise ValueError("Cycle vertices must be integer indices.")
            forward = DirectedEdge(u, v)
            reverse = DirectedEdge(v, u)
            if forward not in self.edges and reverse not in self.edges:
                raise ValueError(f"Step {idx}: edge ({u}, {v}) is not an edge in the graph.")
            start = u if sign == 1 else v
            end = v if sign == 1 else u
            traversed_steps.append((start, end))

        k = len(traversed_steps)
        for i in range(k):
            current_end = traversed_steps[i][1]
            next_start = traversed_steps[(i + 1) % k][0]
            if current_end != next_start:
                raise ValueError(
                    f"Cycle is not closed: step {i} ends at vertex {current_end}, "
                    f"but step {(i + 1) % k} starts at vertex {next_start}."
                )

    def coboundary_0(
        self, vertex_field: Mapping[int, int | str | Fraction]
    ) -> Dict[DirectedEdge, Fraction]:
        """Compute coboundary (d_0 f)(u, v) = f(v) - f(u)."""
        edge_field: Dict[DirectedEdge, Fraction] = {}
        for edge in self.edges:
            if edge.target not in vertex_field:
                raise ValueError(
                    f"Missing vertex {edge.target} in vertex_field for edge ({edge.source}, {edge.target})"
                )
            if edge.source not in vertex_field:
                raise ValueError(
                    f"Missing vertex {edge.source} in vertex_field for edge ({edge.source}, {edge.target})"
                )
            fv = _to_exact_fraction(vertex_field[edge.target], f"vertex {edge.target}")
            fu = _to_exact_fraction(vertex_field[edge.source], f"vertex {edge.source}")
            edge_field[edge] = fv - fu
        return edge_field

    def cycle_holonomy(
        self,
        edge_field: Mapping[DirectedEdge, int | str | Fraction],
        cycle_edges: Sequence[Tuple[int, int, int]],
    ) -> Fraction:
        """Compute holonomy around a cycle: sum s_i * omega(e_i) where s_i in {-1, 1}."""
        self.validate_cycle(cycle_edges)
        values = self._canonical_values(edge_field, "edge_field")
        total = Fraction(0, 1)
        for u, v, sign in cycle_edges:
            stored = self._stored_edge(u, v)
            stored_sign = sign if stored == DirectedEdge(u, v) else -sign
            total += stored_sign * values[stored]
        return total

    def evaluate_local_green(
        self,
        edge_field: Mapping[DirectedEdge, int | str | Fraction],
        tolerances: Mapping[DirectedEdge, int | str | Fraction],
        allow_sparse_default: bool = False,
    ) -> bool:
        """Check whether edge_field is locally consistent ('Local Green') on all edges.

        By default (allow_sparse_default=False), the evaluator enforces a complete input contract:
        every edge in the graph must have an explicitly declared value and non-negative tolerance.
        Passing incomplete records raises ValueError rather than defaulting unmeasured edges to 0.
        If allow_sparse_default=True, missing edges are treated as 0 value and 0 tolerance.
        """
        values = self._canonical_values(edge_field, "edge_field", allow_sparse_default)
        caps = self._canonical_values(tolerances, "tolerances", allow_sparse_default)
        if any(tau < 0 for tau in caps.values()):
            raise ValueError("Negative tolerance on graph edge.")
        return all(abs(values[edge]) <= caps[edge] for edge in self.edges)

    def _canonical_values(
        self,
        supplied: Mapping[DirectedEdge, int | str | Fraction],
        name: str,
        allow_sparse_default: bool = False,
    ) -> Dict[DirectedEdge, Fraction]:
        """Use only the declared stored-edge domain, including for sparse inputs."""
        if set(supplied) - set(self.edges):
            raise ValueError(f"Noncanonical {name}: entries outside stored graph edges.")
        if not allow_sparse_default and set(self.edges) - set(supplied):
            raise ValueError(f"Incomplete {name}: declare every stored graph edge.")
        return {
            edge: _to_exact_fraction(supplied.get(edge, 0), f"{name} {edge}") for edge in self.edges
        }

    def check_evaluator_soundness(
        self,
        vertex_field: Mapping[int, int | str | Fraction],
        cycle_edges: Sequence[Tuple[int, int, int]],
    ) -> bool:
        """Verify the Evaluator Soundness Theorem: exact coboundaries have zero cycle holonomy.

        For any f in C^0, holonomy around any closed cycle of d_0 f must be identically zero.
        """
        self.validate_cycle(cycle_edges)
        edge_field = self.coboundary_0(vertex_field)
        holonomy = self.cycle_holonomy(edge_field, cycle_edges)
        return holonomy == Fraction(0, 1)

    def _stored_edge(self, source: int, target: int) -> DirectedEdge | None:
        forward = DirectedEdge(source, target)
        reverse = DirectedEdge(target, source)
        if forward in self.edge_index:
            return forward
        if reverse in self.edge_index:
            return reverse
        return None

    def false_green_witness(
        self,
        cycle_edges: Sequence[Tuple[int, int, int]],
        tolerances: Mapping[DirectedEdge, int | str | Fraction],
    ) -> bool:
        """Construct the rational half-minimum witness and test it.

        Returns False unless the cycle is closed, has length at least 3, uses
        each stored edge at most once, and every cycle tolerance is positive.
        Otherwise builds ``omega = sign * eps`` with ``eps = tau_min / 2``,
        then calls the shipped local-green and holonomy checks.
        """
        try:
            self.validate_cycle(cycle_edges)
        except ValueError:
            return False
        if len(cycle_edges) < 3:
            return False
        for edge in self.edges:
            if edge not in tolerances:
                return False
        used: set[DirectedEdge] = set()
        cycle_taus: list[Fraction] = []
        assignments: list[tuple[DirectedEdge, int]] = []
        for source, target, sign in cycle_edges:
            stored = self._stored_edge(source, target)
            if stored is None or stored in used:
                return False
            used.add(stored)
            tau = _to_exact_fraction(tolerances[stored], "cycle tolerance")
            if tau <= 0:
                return False
            cycle_taus.append(tau)
            stored_sign = sign if stored == DirectedEdge(source, target) else -sign
            assignments.append((stored, stored_sign))
        epsilon = min(cycle_taus) / 2
        if epsilon <= 0:
            return False
        edge_field: dict[DirectedEdge, Fraction] = {edge: Fraction(0) for edge in self.edges}
        for stored, stored_sign in assignments:
            edge_field[stored] = Fraction(stored_sign) * epsilon
        if not self.evaluate_local_green(edge_field, tolerances):
            return False
        holonomy = self.cycle_holonomy(edge_field, cycle_edges)
        return holonomy == len(cycle_edges) * epsilon and holonomy != 0

    def cycle_defect_within_tolerance_sum(
        self,
        edge_field: Mapping[DirectedEdge, int | str | Fraction],
        tolerances: Mapping[DirectedEdge, int | str | Fraction],
        cycle_edges: Sequence[Tuple[int, int, int]],
    ) -> bool:
        """Return whether a Local-Green field obeys the signed tolerance sum."""
        try:
            if not self.evaluate_local_green(edge_field, tolerances):
                return False
            holonomy = abs(self.cycle_holonomy(edge_field, cycle_edges))
        except (ValueError, KeyError):
            return False
        total = Fraction(0)
        for source, target, _sign in cycle_edges:
            stored = self._stored_edge(source, target)
            if stored is None or stored not in tolerances:
                return False
            tau = _to_exact_fraction(tolerances[stored], "cycle tolerance")
            if tau < 0:
                return False
            total += tau
        return holonomy <= total

    def sharp_cycle_attains_tolerance_sum(
        self,
        tolerances: Mapping[DirectedEdge, int | str | Fraction],
        cycle_edges: Sequence[Tuple[int, int, int]],
    ) -> bool:
        """Attain the tolerance sum on an edge-simple closed cycle, including zero.

        Repeated stored edges are outside this construction's domain. The bound
        checker still accepts general closed walks and counts every traversal.
        """
        try:
            self.validate_cycle(cycle_edges)
        except ValueError:
            return False
        edge_field: dict[DirectedEdge, Fraction] = {edge: Fraction(0) for edge in self.edges}
        total = Fraction(0)
        used: set[DirectedEdge] = set()
        for source, target, sign in cycle_edges:
            stored = self._stored_edge(source, target)
            if stored is None or stored not in tolerances or stored in used:
                return False
            used.add(stored)
            tau = _to_exact_fraction(tolerances[stored], "cycle tolerance")
            if tau < 0:
                return False
            stored_sign = sign if stored == DirectedEdge(source, target) else -sign
            edge_field[stored] = Fraction(stored_sign) * tau
            total += tau
        for edge in self.edges:
            if edge not in tolerances:
                return False
        try:
            holonomy = self.cycle_holonomy(edge_field, cycle_edges)
        except (ValueError, KeyError):
            return False
        return holonomy == total and self.cycle_defect_within_tolerance_sum(
            edge_field, tolerances, cycle_edges
        )


class LandscapeVacuaModel:
    """Reference multi-vacuum landscape model demonstrating the representation-authority gap."""

    @staticmethod
    def standard_five_vacua() -> List[CandidateModel]:
        """Generate a toy landscape of 5 distinct vacua with 4 observable predictions:

        - lambda_cc: cosmological constant analogue
        - gauge_rank: rank of low-energy gauge group
        - num_generations: count of fermion generations
        - higgs_mass_sq: scalar mass parameter
        """
        v1 = CandidateModel.from_dict(
            "Vacuum_1",
            {
                "lambda_cc": Fraction(1, 100),
                "gauge_rank": Fraction(4, 1),
                "num_generations": Fraction(3, 1),
                "higgs_mass_sq": Fraction(125, 1),
            },
        )
        v2 = CandidateModel.from_dict(
            "Vacuum_2",
            {
                "lambda_cc": Fraction(1, 100),
                "gauge_rank": Fraction(4, 1),
                "num_generations": Fraction(3, 1),
                "higgs_mass_sq": Fraction(250, 1),  # Differs from V1 only on higgs_mass_sq
            },
        )
        v3 = CandidateModel.from_dict(
            "Vacuum_3",
            {
                "lambda_cc": Fraction(-1, 100),  # Negative cosmological constant
                "gauge_rank": Fraction(4, 1),
                "num_generations": Fraction(3, 1),
                "higgs_mass_sq": Fraction(125, 1),
            },
        )
        v4 = CandidateModel.from_dict(
            "Vacuum_4",
            {
                "lambda_cc": Fraction(1, 100),
                "gauge_rank": Fraction(5, 1),  # Non-standard gauge rank
                "num_generations": Fraction(3, 1),
                "higgs_mass_sq": Fraction(125, 1),
            },
        )
        v5 = CandidateModel.from_dict(
            "Vacuum_5",
            {
                "lambda_cc": Fraction(1, 100),
                "gauge_rank": Fraction(4, 1),
                "num_generations": Fraction(2, 1),  # Two generations
                "higgs_mass_sq": Fraction(125, 1),
            },
        )
        return [v1, v2, v3, v4, v5]
