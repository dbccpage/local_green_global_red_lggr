"""Finite reference implementation for *Local Green, Global Red III*.

The module implements the paper's actual finite objects: binary verdict
defects, the sample identity, an explicit boundary-bijection audit for path
composition, and evaluator descent through computed quotient classes.  It
does not turn declared Boolean gates into theorem evidence.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction
import math
from typing import Callable, Hashable, Iterable, Mapping, Sequence, TypeVar


class InvalidVerdictError(ValueError):
    """A purported evaluator verdict was not the integer 0 or 1."""


class InvariantViolationError(RuntimeError):
    """A derived finite identity disagreed with its defining arithmetic."""


class NumericalRefusalError(InvariantViolationError):
    """Numerical evaluation produced non-finite values (overflow, underflow, or NaN)."""


class PathDataError(ValueError):
    """Finite path data were malformed or ambiguously identified."""


class CompositionHypothesisError(ValueError):
    """At least one computed path-composition hypothesis failed."""


class QuotientDescentError(ValueError):
    """An evaluator varied inside a computed equivalence class."""


class ObservationChangedError(ValueError):
    """A fixed-observation comparison was requested for different triples."""


class DetectorAdequacyError(ValueError):
    """A finite output sample cannot even witness a nonconstant evaluator."""


class DefectSign(str, Enum):
    """The three possible signs of a binary evaluator defect."""

    NEGATIVE = "negative"
    ZERO = "zero"
    POSITIVE = "positive"


def _require_binary(name: str, value: int) -> None:
    if type(value) is not int or value not in (0, 1):
        raise InvalidVerdictError(f"{name} must be the integer 0 or 1, got {value!r}")


def classify_defect(delta: int) -> DefectSign:
    """Classify an integer as negative, zero, or positive."""

    if delta < 0:
        return DefectSign.NEGATIVE
    if delta > 0:
        return DefectSign.POSITIVE
    return DefectSign.ZERO


@dataclass(frozen=True)
class EvaluatorVerdictTriple:
    """Local verdicts ``e1``, ``e2`` and composite verdict ``eg``."""

    e1: int
    e2: int
    eg: int

    def __post_init__(self) -> None:
        _require_binary("e1", self.e1)
        _require_binary("e2", self.e2)
        _require_binary("eg", self.eg)

    @property
    def local_product(self) -> int:
        return self.e1 * self.e2

    @property
    def evaluator_defect(self) -> int:
        return self.eg - self.local_product

    @property
    def defect_sign(self) -> DefectSign:
        return classify_defect(self.evaluator_defect)

    @property
    def is_local_green_global_red(self) -> bool:
        return (self.e1, self.e2, self.eg) == (1, 1, 0)


@dataclass(frozen=True)
class AggregateAudit:
    """Exact integer totals for one finite sample."""

    global_sum: int
    local_product_sum: int
    defect_sum: int
    pointwise_defects: tuple[int, ...]

    @property
    def n_negative(self) -> int:
        """Count of negative defects Delta_E = -1 (N_-)."""
        return sum(1 for defect in self.pointwise_defects if defect == -1)

    @property
    def n_positive(self) -> int:
        """Count of positive defects Delta_E = +1 (N_+)."""
        return sum(1 for defect in self.pointwise_defects if defect == 1)

    @property
    def disagreement_count(self) -> int:
        """Disagreement count M = N_+ + N_- = sum |Delta_i|.

        M = 0 certifies pointwise agreement on the observed sample.
        """
        return sum(abs(defect) for defect in self.pointwise_defects)

    @property
    def has_aggregate_cancellation(self) -> bool:
        return self.defect_sum == 0 and self.disagreement_count > 0


def audit_sample(samples: Iterable[EvaluatorVerdictTriple]) -> AggregateAudit:
    """Compute the finite identity ``sum(eg) - sum(e1*e2) = sum(defect)``."""

    sample = tuple(samples)
    global_sum = sum(item.eg for item in sample)
    local_sum = sum(item.local_product for item in sample)
    pointwise = tuple(item.evaluator_defect for item in sample)
    defect_sum = sum(pointwise)
    if global_sum - local_sum != defect_sum:
        raise InvariantViolationError(
            f"finite identity failed: {global_sum} - {local_sum} != {defect_sum}"
        )
    return AggregateAudit(global_sum, local_sum, defect_sum, pointwise)


PHONE_SAMPLE = (
    EvaluatorVerdictTriple(1, 1, 1),
    EvaluatorVerdictTriple(1, 1, 0),
    EvaluatorVerdictTriple(1, 1, 0),
    EvaluatorVerdictTriple(0, 1, 0),
    EvaluatorVerdictTriple(0, 0, 0),
)


def phone_test() -> AggregateAudit:
    """Replay the five archived triples with totals ``(1, 3, -2)``."""

    result = audit_sample(PHONE_SAMPLE)
    if (result.global_sum, result.local_product_sum, result.defect_sum) != (1, 3, -2):
        raise InvariantViolationError("the fixed five-trace totals changed")
    return result


def _require_name(label: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PathDataError(f"{label} must be a nonempty string")


def _require_nonnegative_finite(label: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction, Decimal)):
        raise PathDataError(f"{label} must be a finite nonnegative number")
    try:
        val_float = float(value)
    except OverflowError as err:
        raise PathDataError(f"{label} must be a finite nonnegative number") from err
    if not math.isfinite(val_float) or val_float < 0:
        raise PathDataError(f"{label} must be a finite nonnegative number")


def _to_exact_rational(
    value: int | float | Fraction | Decimal, label: str
) -> Fraction:
    """Convert an admitted cost or mass to an exact rational representation.

    Exact integers, Fractions, and Decimals are converted without loss.
    Floating-point values are converted via their decimal string representation
    to preserve exact values declared as decimal numbers (e.g. 0.4, 0.2, 0.08)
    as well as exact dyadic/scientific values without floating-point truncation.
    """
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, (float, Decimal)):
        return Fraction(str(value))
    raise PathDataError(f"{label} has unsupported type {type(value)!r}")


@dataclass(frozen=True)
class PathSegment:
    """One admitted path segment, including its evaluated weight data."""

    identifier: str
    source: str
    target: str
    cost: float | int | Fraction | Decimal
    verdict: int
    proposal_mass: float | int | Fraction | Decimal = 1.0

    def __post_init__(self) -> None:
        _require_name("segment identifier", self.identifier)
        _require_name("segment source", self.source)
        _require_name("segment target", self.target)
        _require_nonnegative_finite("segment cost", self.cost)
        _require_binary("segment verdict", self.verdict)
        _require_nonnegative_finite("segment proposal mass", self.proposal_mass)

    @property
    def exact_cost(self) -> Fraction:
        return _to_exact_rational(self.cost, "segment cost")

    @property
    def exact_proposal_mass(self) -> Fraction:
        return _to_exact_rational(self.proposal_mass, "segment proposal mass")


@dataclass(frozen=True)
class CompositePath:
    """An admitted composite identified with two declared segment ids."""

    identifier: str
    first_id: str
    second_id: str
    cost: float | int | Fraction | Decimal
    verdict: int
    proposal_mass: float | int | Fraction | Decimal = 1.0

    def __post_init__(self) -> None:
        _require_name("composite identifier", self.identifier)
        _require_name("first segment id", self.first_id)
        _require_name("second segment id", self.second_id)
        _require_nonnegative_finite("composite cost", self.cost)
        _require_binary("composite verdict", self.verdict)
        _require_nonnegative_finite("composite proposal mass", self.proposal_mass)

    @property
    def exact_cost(self) -> Fraction:
        return _to_exact_rational(self.cost, "composite cost")

    @property
    def exact_proposal_mass(self) -> Fraction:
        return _to_exact_rational(self.proposal_mass, "composite proposal mass")


T = TypeVar("T")


def _unique_index(records: Sequence[T], label: str) -> dict[str, T]:
    index: dict[str, T] = {}
    for record in records:
        identifier = getattr(record, "identifier")
        if identifier in index:
            raise PathDataError(f"duplicate {label} identifier: {identifier}")
        index[identifier] = record
    return index


# (boundary state, second-segment id, first-segment id), matching
# Gamma(c,b) x Gamma(b,a) in the paper.
CompatiblePair = tuple[str, str, str]


def compatible_segment_pairs(
    first_segments: Sequence[PathSegment],
    second_segments: Sequence[PathSegment],
) -> tuple[CompatiblePair, ...]:
    """Return the disjoint union of compatible pairs, tagged by boundary state."""

    _unique_index(first_segments, "first segment")
    _unique_index(second_segments, "second segment")
    return tuple(
        (first.target, second.identifier, first.identifier)
        for first in first_segments
        for second in second_segments
        if first.target == second.source
    )


@dataclass(frozen=True)
class BoundaryBijectionReport:
    """Comparison of admitted composites with all compatible segment pairs."""

    expected_pairs: tuple[CompatiblePair, ...]
    observed_pairs: tuple[CompatiblePair, ...]
    issues: tuple[str, ...]

    @property
    def is_bijection(self) -> bool:
        return not self.issues


def boundary_bijection_report(
    first_segments: Sequence[PathSegment],
    second_segments: Sequence[PathSegment],
    composites: Sequence[CompositePath],
) -> BoundaryBijectionReport:
    """Compute G1: composites biject with the disjoint union of compatible pairs."""

    first_by_id = _unique_index(first_segments, "first segment")
    second_by_id = _unique_index(second_segments, "second segment")
    _unique_index(composites, "composite")
    expected = compatible_segment_pairs(first_segments, second_segments)
    observed: list[CompatiblePair] = []
    issues: list[str] = []

    for composite in composites:
        first = first_by_id.get(composite.first_id)
        second = second_by_id.get(composite.second_id)
        if first is None or second is None:
            issues.append(f"G1: {composite.identifier} refers to an unknown segment")
            continue
        pair = (first.target, second.identifier, first.identifier)
        observed.append(pair)
        if first.target != second.source:
            issues.append(f"G1: {composite.identifier} joins incompatible segments")

    expected_counts = Counter(expected)
    observed_counts = Counter(observed)
    for pair, count in sorted((expected_counts - observed_counts).items()):
        issues.append(f"G1: compatible pair {pair!r} is missing {count} time(s)")
    for pair, count in sorted((observed_counts - expected_counts).items()):
        issues.append(f"G1: pair {pair!r} is extra or duplicated {count} time(s)")

    return BoundaryBijectionReport(expected, tuple(observed), tuple(issues))


@dataclass(frozen=True)
class KernelCompositionAudit:
    """Computed G1--G4 results and the two sides of the finite kernel identity."""

    g1_bijection: bool
    g2_cost_additive: bool
    g3_evaluator_factorized: bool
    g4_proposal_factorized: bool | None
    composed_value: float
    convolution_value: float
    issues: tuple[str, ...]

    @property
    def residual(self) -> float:
        return self.composed_value - self.convolution_value

    @property
    def is_finite(self) -> bool:
        return (
            math.isfinite(self.composed_value)
            and math.isfinite(self.convolution_value)
            and math.isfinite(self.residual)
        )

    @property
    def numerical_status(self) -> str:
        if self.is_finite:
            return "finite"
        if (
            math.isnan(self.residual)
            or math.isnan(self.composed_value)
            or math.isnan(self.convolution_value)
        ):
            return "nan_residual"
        return "overflow"

    @property
    def hypotheses_hold(self) -> bool:
        return (
            self.g1_bijection
            and self.g2_cost_additive
            and self.g3_evaluator_factorized
            and self.g4_proposal_factorized is not False
        )

    @property
    def identity_holds(self) -> bool:
        if not self.is_finite:
            return False
        return math.isclose(
            self.composed_value,
            self.convolution_value,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


def _kernel_weight(
    verdict: int, cost: float, proposal_mass: float, decay: float, weighted: bool
) -> float:
    mass = proposal_mass if weighted else 1.0
    return verdict * mass * math.exp(-decay * cost)


def audit_kernel_composition(
    first_segments: Sequence[PathSegment],
    second_segments: Sequence[PathSegment],
    composites: Sequence[CompositePath],
    *,
    decay: float,
    proposal_weighted: bool = False,
) -> KernelCompositionAudit:
    """Evaluate the finite kernel and derive each composition hypothesis from data."""

    _require_nonnegative_finite("decay", decay)
    first = tuple(first_segments)
    second = tuple(second_segments)
    joined = tuple(composites)
    report = boundary_bijection_report(first, second, joined)
    first_by_id = _unique_index(first, "first segment")
    second_by_id = _unique_index(second, "second segment")
    issues = list(report.issues)
    valid_references = True

    for composite in joined:
        left = first_by_id.get(composite.first_id)
        right = second_by_id.get(composite.second_id)
        if left is None or right is None:
            valid_references = False
            continue
        if composite.exact_cost != left.exact_cost + right.exact_cost:
            issues.append(f"G2: cost is not additive for {composite.identifier}")
        if composite.verdict != left.verdict * right.verdict:
            issues.append(f"G3: verdict does not factor for {composite.identifier}")
        if (
            proposal_weighted
            and composite.exact_proposal_mass
            != left.exact_proposal_mass * right.exact_proposal_mass
        ):
            issues.append(
                f"G4: proposal mass does not factor for {composite.identifier}"
            )

    composed_value = sum(
        _kernel_weight(
            item.verdict,
            float(item.cost),
            float(item.proposal_mass),
            float(decay),
            proposal_weighted,
        )
        for item in joined
    )
    convolution_value = sum(
        _kernel_weight(
            left.verdict,
            float(left.cost),
            float(left.proposal_mass),
            float(decay),
            proposal_weighted,
        )
        * _kernel_weight(
            right.verdict,
            float(right.cost),
            float(right.proposal_mass),
            float(decay),
            proposal_weighted,
        )
        for left in first
        for right in second
        if left.target == right.source
    )
    g2 = valid_references and not any(issue.startswith("G2:") for issue in issues)
    g3 = valid_references and not any(issue.startswith("G3:") for issue in issues)
    g4 = (
        valid_references and not any(issue.startswith("G4:") for issue in issues)
        if proposal_weighted
        else None
    )
    return KernelCompositionAudit(
        report.is_bijection,
        g2,
        g3,
        g4,
        composed_value,
        convolution_value,
        tuple(issues),
    )


def assert_kernel_composition(
    *args: object, **kwargs: object
) -> KernelCompositionAudit:
    """Return a clean audit or explain which data-derived hypothesis failed."""

    audit = audit_kernel_composition(*args, **kwargs)  # type: ignore[arg-type]
    if not audit.hypotheses_hold:
        raise CompositionHypothesisError("; ".join(audit.issues))
    if not audit.is_finite:
        raise NumericalRefusalError(
            f"numerical representation failed ({audit.numerical_status}): "
            f"composed={audit.composed_value!r}, convolution={audit.convolution_value!r}, "
            f"residual={audit.residual!r}"
        )
    if not audit.identity_holds:
        raise InvariantViolationError(
            f"kernel identity failed with residual {audit.residual!r}"
        )
    return audit


def integer_boundary_products(
    groups: Sequence[tuple[Sequence[int], Sequence[int]]],
) -> list[int]:
    """Flatten each boundary into left-weight times right-weight."""

    products: list[int] = []
    for left, right in groups:
        for scale in left:
            products.extend(scale * weight for weight in right)
    return products


def integer_group_convolution(
    groups: Sequence[tuple[Sequence[int], Sequence[int]]],
) -> int:
    """Sum over boundaries of left-sum times right-sum."""

    return sum(sum(left) * sum(right) for left, right in groups)


def integer_kernel_residual_is_zero(
    groups: Sequence[tuple[Sequence[int], Sequence[int]]],
    composite: Sequence[int],
) -> bool:
    """Return whether flattened integer boundary products have residual zero."""

    expected = integer_boundary_products(groups)
    if list(composite) != expected:
        raise ValueError("composite weights are not the flattened boundary products")
    return sum(composite) - integer_group_convolution(groups) == 0


U = TypeVar("U")


@dataclass(frozen=True)
class QuotientClassViolation:
    """One computed class on which the evaluator is not constant."""

    class_id: Hashable
    member_indices: tuple[int, ...]
    verdicts: tuple[int, ...]


def _evaluated_classes(
    elements: Iterable[U],
    class_of: Callable[[U], Hashable],
    evaluate: Callable[[U], int],
) -> dict[Hashable, list[tuple[int, int]]]:
    classes: dict[Hashable, list[tuple[int, int]]] = {}
    for index, element in enumerate(elements):
        class_id = class_of(element)
        try:
            hash(class_id)
        except TypeError as error:
            raise TypeError("quotient class identifiers must be hashable") from error
        verdict = evaluate(element)
        _require_binary(f"evaluator output at index {index}", verdict)
        classes.setdefault(class_id, []).append((index, verdict))
    return classes


def quotient_class_violations(
    elements: Iterable[U],
    class_of: Callable[[U], Hashable],
    evaluate: Callable[[U], int],
) -> tuple[QuotientClassViolation, ...]:
    """Compute all equivalence classes and report exactly the mixed ones."""

    violations = []
    for class_id, members in _evaluated_classes(elements, class_of, evaluate).items():
        verdicts = tuple(verdict for _, verdict in members)
        if len(set(verdicts)) > 1:
            violations.append(
                QuotientClassViolation(
                    class_id,
                    tuple(index for index, _ in members),
                    verdicts,
                )
            )
    return tuple(violations)


def descend_evaluator(
    elements: Iterable[U],
    class_of: Callable[[U], Hashable],
    evaluate: Callable[[U], int],
) -> Mapping[Hashable, int]:
    """Construct the unique quotient evaluator exactly when every class is invariant.

    An evaluator E descends through the quotient projection q: X -> X/~ to a
    well-defined function \\bar{E}: X/~ -> {0, 1} with E = \\bar{E} \\circ q if and
    only if E is constant on each equivalence class. Surjectivity of q makes
    \\bar{E} unique when it exists.
    """

    classes = _evaluated_classes(elements, class_of, evaluate)
    mixed = [
        class_id
        for class_id, members in classes.items()
        if len({verdict for _, verdict in members}) > 1
    ]
    if mixed:
        raise QuotientDescentError(f"evaluator varies in quotient classes {mixed!r}")
    return {class_id: members[0][1] for class_id, members in classes.items()}


ROLE_NAMES = (
    "finite obstruction",
    "foundations",
    "representation",
    "observer",
    "continuum shadow",
    "action and alignment",
)


@dataclass(frozen=True)
class RoleOverlay:
    """The common verdict record plus role-specific descriptive context."""

    role: str
    verdict: EvaluatorVerdictTriple
    context: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if self.role not in ROLE_NAMES:
            raise ValueError(f"unknown role: {self.role!r}")
        if not self.context or any(not key or not value for key, value in self.context):
            raise ValueError("role context must contain nonempty key/value pairs")


def observer_score(weight: int, residual: int) -> int:
    """The declared observation-envelope score ``S_w(R) = wR``."""

    return weight * residual


def fixed_observation_preserves_defect(
    before: EvaluatorVerdictTriple, after: EvaluatorVerdictTriple
) -> bool:
    """Check Proposition 5 on actual pre/post triples, not a supplied truth flag."""

    if before != after:
        raise ObservationChangedError("the pre/post verdict triples are not fixed")
    return before.evaluator_defect == after.evaluator_defect


def require_non_collapsing(outputs: Iterable[int]) -> bool:
    """Reject empty, singleton, or constant finite output samples.

    Passing this check is deliberately not a task-specific adequacy proof.
    """

    sample = tuple(outputs)
    for index, value in enumerate(sample):
        _require_binary(f"evaluator output at index {index}", value)
    if len(sample) < 2 or len(set(sample)) < 2:
        raise DetectorAdequacyError(
            "the observed outputs do not witness a nonconstant evaluator"
        )
    return True
