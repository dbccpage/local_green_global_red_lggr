"""Unit tests for the thin Paper III reference implementation."""

from __future__ import annotations

import math
from unittest.mock import patch

import pytest

import epk_gtla_overlay_core as core
from epk_gtla_overlay_core import (
    AggregateAudit,
    CompositePath,
    CompositionHypothesisError,
    DefectSign,
    DetectorAdequacyError,
    EvaluatorVerdictTriple,
    InvalidVerdictError,
    InvariantViolationError,
    KernelCompositionAudit,
    NumericalRefusalError,
    ObservationChangedError,
    PathDataError,
    PathSegment,
    QuotientDescentError,
    ROLE_NAMES,
    RoleOverlay,
)


def clean_paths() -> tuple[
    tuple[PathSegment, ...], tuple[PathSegment, ...], tuple[CompositePath, ...]
]:
    first = (
        PathSegment("ab-pass", "a", "b", 1.0, 1, 0.4),
        PathSegment("ad-stop", "a", "d", 2.0, 0, 0.3),
    )
    second = (
        PathSegment("bc-pass", "b", "c", 2.0, 1, 0.5),
        PathSegment("bc-stop", "b", "c", 3.0, 0, 0.2),
        PathSegment("dc-pass", "d", "c", 1.0, 1, 0.6),
    )
    composites = (
        CompositePath("abc-pass", "ab-pass", "bc-pass", 3.0, 1, 0.2),
        CompositePath("abc-stop", "ab-pass", "bc-stop", 4.0, 0, 0.08),
        CompositePath("adc-stop", "ad-stop", "dc-pass", 3.0, 0, 0.18),
    )
    return first, second, composites


@pytest.mark.parametrize(
    ("values", "defect", "sign", "is_lggr"),
    [
        ((0, 0, 0), 0, DefectSign.ZERO, False),
        ((0, 0, 1), 1, DefectSign.POSITIVE, False),
        ((0, 1, 0), 0, DefectSign.ZERO, False),
        ((0, 1, 1), 1, DefectSign.POSITIVE, False),
        ((1, 0, 0), 0, DefectSign.ZERO, False),
        ((1, 0, 1), 1, DefectSign.POSITIVE, False),
        ((1, 1, 0), -1, DefectSign.NEGATIVE, True),
        ((1, 1, 1), 0, DefectSign.ZERO, False),
    ],
)
def test_all_binary_triples(values, defect, sign, is_lggr) -> None:
    triple = EvaluatorVerdictTriple(*values)
    assert triple.local_product == values[0] * values[1]
    assert triple.evaluator_defect == defect
    assert triple.defect_sign is sign
    assert triple.is_local_green_global_red is is_lggr


@pytest.mark.parametrize(
    "values",
    [(2, 0, 0), (0, -1, 0), (0, 0, 3), (True, 0, 0), (0, False, 0)],
)
def test_invalid_verdicts_are_rejected(values) -> None:
    with pytest.raises(InvalidVerdictError):
        EvaluatorVerdictTriple(*values)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(-7, DefectSign.NEGATIVE), (0, DefectSign.ZERO), (9, DefectSign.POSITIVE)],
)
def test_classify_defect(value: int, expected: DefectSign) -> None:
    assert core.classify_defect(value) is expected


def test_finite_sample_identity_and_empty_sample() -> None:
    assert core.audit_sample(()) == AggregateAudit(0, 0, 0, ())
    result = core.audit_sample(
        (EvaluatorVerdictTriple(0, 1, 1), EvaluatorVerdictTriple(1, 1, 0))
    )
    assert (result.global_sum, result.local_product_sum, result.defect_sum) == (1, 1, 0)
    assert result.pointwise_defects == (1, -1)
    assert result.has_aggregate_cancellation


def test_phone_test_exact_totals() -> None:
    result = core.phone_test()
    assert (result.global_sum, result.local_product_sum, result.defect_sum) == (
        1,
        3,
        -2,
    )
    assert not result.has_aggregate_cancellation


def test_arithmetic_defence_is_executable() -> None:
    with patch("builtins.sum", side_effect=[1, 0, 0]):
        with pytest.raises(InvariantViolationError, match="finite identity failed"):
            core.audit_sample(())


def test_phone_fixture_defence_is_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(core, "audit_sample", lambda _: AggregateAudit(9, 9, 9, ()))
    with pytest.raises(InvariantViolationError, match="five-trace totals"):
        core.phone_test()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: PathSegment("", "a", "b", 0, 1),
        lambda: PathSegment("s", "", "b", 0, 1),
        lambda: PathSegment("s", "a", "", 0, 1),
        lambda: PathSegment("s", "a", "b", -1, 1),
        lambda: PathSegment("s", "a", "b", math.inf, 1),
        lambda: PathSegment("s", "a", "b", True, 1),
        lambda: PathSegment("s", "a", "b", 0, 2),
        lambda: PathSegment("s", "a", "b", 0, 1, -0.1),
        lambda: CompositePath("", "x", "y", 0, 1),
        lambda: CompositePath("c", "", "y", 0, 1),
        lambda: CompositePath("c", "x", "", 0, 1),
        lambda: CompositePath("c", "x", "y", float("nan"), 1),
        lambda: CompositePath("c", "x", "y", 0, False),
        lambda: CompositePath("c", "x", "y", 0, 1, float("inf")),
    ],
)
def test_malformed_path_records_are_rejected(factory) -> None:
    with pytest.raises((PathDataError, InvalidVerdictError)):
        factory()


def test_compatible_pairs_are_boundary_tagged() -> None:
    first, second, _ = clean_paths()
    assert core.compatible_segment_pairs(first, second) == (
        ("b", "bc-pass", "ab-pass"),
        ("b", "bc-stop", "ab-pass"),
        ("d", "dc-pass", "ad-stop"),
    )


@pytest.mark.parametrize("side", ["first", "second", "composite"])
def test_duplicate_identifiers_are_rejected(side: str) -> None:
    first, second, composites = clean_paths()
    if side == "first":
        first = first + (first[0],)
    elif side == "second":
        second = second + (second[0],)
    else:
        composites = composites + (composites[0],)
    with pytest.raises(PathDataError, match="duplicate"):
        core.boundary_bijection_report(first, second, composites)


def test_explicit_boundary_bijection_and_unweighted_kernel() -> None:
    first, second, composites = clean_paths()
    report = core.boundary_bijection_report(first, second, composites)
    assert report.is_bijection
    assert report.observed_pairs == report.expected_pairs
    audit = core.audit_kernel_composition(first, second, composites, decay=0.5)
    assert (
        audit.g1_bijection and audit.g2_cost_additive and audit.g3_evaluator_factorized
    )
    assert audit.g4_proposal_factorized is None
    assert audit.hypotheses_hold and audit.identity_holds
    assert math.isclose(audit.residual, 0.0, abs_tol=1e-12)


def test_integer_kernel_reindexes() -> None:
    groups = (
        ((2, 3), (4, -1)),
        ((-2,), (5, 0)),
    )
    composite = core.integer_boundary_products(groups)
    assert composite == [8, -2, 12, -3, -10, 0]
    assert core.integer_group_convolution(groups) == sum(composite)
    assert core.integer_kernel_residual_is_zero(groups, composite)
    assert core.integer_kernel_residual_is_zero((), [])
    with pytest.raises(ValueError, match="flattened boundary products"):
        core.integer_kernel_residual_is_zero(groups, [0])


def test_proposal_weighted_kernel_uses_computed_g4() -> None:
    first, second, composites = clean_paths()
    audit = core.assert_kernel_composition(
        first, second, composites, decay=0.75, proposal_weighted=True
    )
    assert audit.g4_proposal_factorized is True
    assert audit.identity_holds


@pytest.mark.parametrize("decay", [-0.1, math.inf, True, "1"])
def test_invalid_decay_is_rejected(decay) -> None:
    first, second, composites = clean_paths()
    with pytest.raises(PathDataError, match="decay"):
        core.audit_kernel_composition(first, second, composites, decay=decay)


def test_kernel_audit_properties_cover_failure_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failed = KernelCompositionAudit(False, True, True, None, 1.0, 2.0, ("G1: missing",))
    assert not failed.hypotheses_hold
    assert not failed.identity_holds
    assert failed.residual == -1.0
    monkeypatch.setattr(core, "audit_kernel_composition", lambda *a, **k: failed)
    with pytest.raises(CompositionHypothesisError, match="G1"):
        core.assert_kernel_composition((), (), (), decay=0)


def test_kernel_internal_identity_defence(monkeypatch: pytest.MonkeyPatch) -> None:
    impossible = KernelCompositionAudit(True, True, True, None, 1.0, 2.0, ())
    monkeypatch.setattr(core, "audit_kernel_composition", lambda *a, **k: impossible)
    with pytest.raises(InvariantViolationError, match="kernel identity failed"):
        core.assert_kernel_composition((), (), (), decay=0)


def test_actual_quotient_classes_construct_descended_evaluator() -> None:
    elements = (("a", 0), ("a", 2), ("b", 1))
    class_of = lambda item: item[0]
    evaluate = lambda item: item[1] % 2
    assert core.quotient_class_violations(elements, class_of, evaluate) == ()
    assert core.descend_evaluator(elements, class_of, evaluate) == {"a": 0, "b": 1}
    assert core.descend_evaluator((), class_of, evaluate) == {}


def test_actual_mixed_class_blocks_descent() -> None:
    elements = (("same", 0), ("same", 1))
    violations = core.quotient_class_violations(
        elements, lambda item: item[0], lambda item: item[1]
    )
    assert violations[0].class_id == "same"
    assert violations[0].member_indices == (0, 1)
    assert violations[0].verdicts == (0, 1)
    with pytest.raises(QuotientDescentError, match="same"):
        core.descend_evaluator(elements, lambda item: item[0], lambda item: item[1])


def test_quotient_checker_rejects_bad_outputs_and_class_ids() -> None:
    with pytest.raises(InvalidVerdictError):
        core.quotient_class_violations([0], lambda _: "a", lambda _: 2)
    with pytest.raises(TypeError, match="hashable"):
        core.quotient_class_violations([0], lambda _: [], lambda _: 0)  # type: ignore[return-value,arg-type]


def test_role_overlay_has_exact_six_roles_and_context() -> None:
    verdict = EvaluatorVerdictTriple(1, 1, 0)
    records = tuple(
        RoleOverlay(role, verdict, (("scope", "declared"),)) for role in ROLE_NAMES
    )
    assert len(records) == 6
    with pytest.raises(ValueError, match="unknown role"):
        RoleOverlay("seventh role", verdict, (("scope", "declared"),))
    with pytest.raises(ValueError, match="nonempty"):
        RoleOverlay(ROLE_NAMES[0], verdict, ())
    with pytest.raises(ValueError, match="nonempty"):
        RoleOverlay(ROLE_NAMES[0], verdict, (("", "value"),))


def test_observer_score_and_fixed_observation() -> None:
    before = EvaluatorVerdictTriple(1, 1, 0)
    assert core.observer_score(1, 1) == 1
    assert core.observer_score(2, 1) == 2
    assert core.fixed_observation_preserves_defect(before, before)
    with pytest.raises(ObservationChangedError):
        core.fixed_observation_preserves_defect(before, EvaluatorVerdictTriple(1, 1, 1))


@pytest.mark.parametrize("outputs", [(), (1,), (0, 0), (1, 1, 1)])
def test_collapsing_samples_are_rejected(outputs) -> None:
    with pytest.raises(DetectorAdequacyError):
        core.require_non_collapsing(outputs)


def test_noncollapsing_sample_and_invalid_output() -> None:
    assert core.require_non_collapsing((0, 1, 0))
    with pytest.raises(InvalidVerdictError):
        core.require_non_collapsing((0, 3))


def test_aggregate_audit_properties_and_disagreement_count() -> None:
    audit0 = core.audit_sample(())
    assert audit0.n_negative == 0
    assert audit0.n_positive == 0
    assert audit0.disagreement_count == 0
    assert not audit0.has_aggregate_cancellation

    audit = core.audit_sample(
        (
            EvaluatorVerdictTriple(0, 1, 1),
            EvaluatorVerdictTriple(1, 1, 0),
        )
    )
    assert audit.n_positive == 1
    assert audit.n_negative == 1
    assert audit.disagreement_count == 2
    assert audit.defect_sum == 0
    assert audit.has_aggregate_cancellation is True


# --- Regression tests for review findings (5 cases) ---


def test_regression_g2_integer_discrepancy() -> None:
    """Exact discrepancy of 1 at lambda=0 must be rejected by G2 additivity."""
    first = (PathSegment("p1", "a", "b", cost=2**54, verdict=1),)
    second = (PathSegment("p2", "b", "c", cost=0, verdict=1),)
    composite = (CompositePath("c1", "p1", "p2", cost=2**54 + 1, verdict=1),)
    audit = core.audit_kernel_composition(first, second, composite, decay=0)
    assert not audit.g2_cost_additive
    assert not audit.hypotheses_hold
    assert any("G2: cost is not additive" in issue for issue in audit.issues)
    with pytest.raises(CompositionHypothesisError, match="G2: cost is not additive"):
        core.assert_kernel_composition(first, second, composite, decay=0)


def test_regression_g2_small_discrepancy_lambda_one() -> None:
    """Small dyadic cost discrepancy eps=2^-41 must be rejected by G2 additivity at lambda=1."""
    first = (PathSegment("p1", "a", "b", cost=0, verdict=1),)
    second = (PathSegment("p2", "b", "c", cost=0, verdict=1),)
    eps = 2.0**-41
    composite = (CompositePath("c1", "p1", "p2", cost=eps, verdict=1),)
    audit = core.audit_kernel_composition(first, second, composite, decay=1)
    assert not audit.g2_cost_additive
    assert not audit.hypotheses_hold
    with pytest.raises(CompositionHypothesisError, match="G2: cost is not additive"):
        core.assert_kernel_composition(first, second, composite, decay=1)


def test_regression_g2_small_discrepancy_large_lambda() -> None:
    """Small dyadic cost discrepancy at lambda=2^41 must fail closed as hypothesis error."""
    first = (PathSegment("p1", "a", "b", cost=0, verdict=1),)
    second = (PathSegment("p2", "b", "c", cost=0, verdict=1),)
    eps = 2.0**-41
    composite = (CompositePath("c1", "p1", "p2", cost=eps, verdict=1),)
    audit = core.audit_kernel_composition(first, second, composite, decay=2.0**41)
    assert not audit.g2_cost_additive
    assert not audit.hypotheses_hold
    with pytest.raises(CompositionHypothesisError, match="G2: cost is not additive"):
        core.assert_kernel_composition(first, second, composite, decay=2.0**41)


def test_regression_g4_proposal_mass_factorization() -> None:
    """Non-factorized proposal masses must be rejected by G4 check."""
    first = (PathSegment("p1", "a", "b", cost=0, verdict=1, proposal_mass=2.0**-41),)
    second = (PathSegment("p2", "b", "c", cost=0, verdict=1, proposal_mass=1.0),)
    composite = (CompositePath("c1", "p1", "p2", cost=0, verdict=1, proposal_mass=0.0),)
    audit = core.audit_kernel_composition(
        first, second, composite, decay=0, proposal_weighted=True
    )
    assert not audit.g4_proposal_factorized
    assert not audit.hypotheses_hold
    with pytest.raises(
        CompositionHypothesisError, match="G4: proposal mass does not factor"
    ):
        core.assert_kernel_composition(
            first, second, composite, decay=0, proposal_weighted=True
        )


def test_regression_nonfinite_overflow_refusal() -> None:
    """Valid inputs producing intermediate float overflow must raise NumericalRefusalError."""
    first = (
        PathSegment("p1a", "a", "b", cost=0, verdict=1, proposal_mass=1e308),
        PathSegment("p1b", "a", "b", cost=0, verdict=1, proposal_mass=1e308),
    )
    second = (PathSegment("p2", "b", "c", cost=0, verdict=1, proposal_mass=1.0),)
    composites = (
        CompositePath("c1a", "p1a", "p2", cost=0, verdict=1, proposal_mass=1e308),
        CompositePath("c1b", "p1b", "p2", cost=0, verdict=1, proposal_mass=1e308),
    )
    audit = core.audit_kernel_composition(
        first, second, composites, decay=0, proposal_weighted=True
    )
    assert audit.hypotheses_hold is True
    assert math.isinf(audit.composed_value)
    assert math.isinf(audit.convolution_value)
    assert math.isnan(audit.residual)
    assert audit.is_finite is False
    assert audit.identity_holds is False
    assert audit.numerical_status in ("nan_residual", "overflow")
    with pytest.raises(
        NumericalRefusalError, match="numerical representation failed"
    ):
        core.assert_kernel_composition(
            first, second, composites, decay=0, proposal_weighted=True
        )


# --- Independent bounded controls (3 suites) ---


def test_control_all_4681_binary_samples_lengths_0_to_4() -> None:
    """Verify finite sample identities across all 4,681 binary samples of lengths 0-4."""
    import itertools

    binary_triples = [
        EvaluatorVerdictTriple(eg, e1, e2)
        for eg in (0, 1)
        for e1 in (0, 1)
        for e2 in (0, 1)
    ]
    sample_count = 0
    for length in range(5):
        for sample in itertools.product(binary_triples, repeat=length):
            sample_count += 1
            audit = core.audit_sample(sample)
            assert audit.global_sum - audit.local_product_sum == audit.defect_sum
            assert audit.disagreement_count == audit.n_positive + audit.n_negative
            assert audit.disagreement_count == sum(
                abs(d) for d in audit.pointwise_defects
            )
            assert audit.defect_sum == audit.n_positive - audit.n_negative
            assert audit.has_aggregate_cancellation == (
                audit.defect_sum == 0 and audit.disagreement_count > 0
            )
    assert sample_count == 4681


def test_control_200_deterministic_integer_kernel_cases() -> None:
    """Verify integer kernel reindexing and zero residual across 200 deterministic cases."""
    cases_checked = 0
    for n_groups in range(1, 11):
        for seed_offset in range(20):
            groups = []
            for g in range(n_groups):
                left_len = (g + seed_offset) % 4 + 1
                right_len = (g * 2 + seed_offset) % 4 + 1
                left = tuple((i * 3 - seed_offset) for i in range(left_len))
                right = tuple((j * 2 - g) for j in range(right_len))
                groups.append((left, right))
            groups_tuple = tuple(groups)
            composite = core.integer_boundary_products(groups_tuple)
            assert core.integer_kernel_residual_is_zero(groups_tuple, composite) is True
            cases_checked += 1
    assert cases_checked == 200


def _all_partitions(elements: list[int]) -> list[list[list[int]]]:
    if not elements:
        return [[]]
    first = elements[0]
    rest_partitions = _all_partitions(elements[1:])
    result = []
    for p in rest_partitions:
        result.append([[first]] + p)
        for i in range(len(p)):
            result.append(p[:i] + [p[i] + [first]] + p[i + 1:])
    return result


def test_control_1955_partition_evaluator_combinations() -> None:
    """Verify quotient descent obstruction across all 1,955 partition/evaluator pairs on sizes 0-5."""
    import itertools

    combos_checked = 0
    for n in range(6):
        carrier = list(range(n))
        partitions = _all_partitions(carrier)
        evaluators = list(itertools.product((0, 1), repeat=n)) if n > 0 else [()]
        for part in partitions:
            elem_to_class: dict[int, int] = {}
            for class_idx, block in enumerate(part):
                for elem in block:
                    elem_to_class[elem] = class_idx

            def class_of(x: int, e2c=elem_to_class) -> int:
                return e2c[x]

            for ev in evaluators:
                combos_checked += 1

                def evaluate(x: int, ev_tuple=ev) -> int:
                    return ev_tuple[x]

                violations = core.quotient_class_violations(carrier, class_of, evaluate)
                is_constant = all(
                    len({ev[x] for x in block}) <= 1 for block in part
                )
                if is_constant:
                    assert violations == ()
                    descended = core.descend_evaluator(carrier, class_of, evaluate)
                    for x in carrier:
                        assert descended[class_of(x)] == evaluate(x)
                else:
                    assert len(violations) > 0
                    with pytest.raises(core.QuotientDescentError):
                        core.descend_evaluator(carrier, class_of, evaluate)
    assert combos_checked == 1955


def test_exact_rational_and_numerical_status_coverage() -> None:
    from decimal import Decimal
    from fractions import Fraction

    # Fraction and Decimal paths in PathSegment
    seg_frac = PathSegment(
        "s1", "a", "b", cost=Fraction(1, 2), verdict=1, proposal_mass=Fraction(3, 4)
    )
    assert seg_frac.exact_cost == Fraction(1, 2)
    assert seg_frac.exact_proposal_mass == Fraction(3, 4)

    seg_dec = PathSegment(
        "s2", "b", "c", cost=Decimal("0.5"), verdict=1, proposal_mass=Decimal("0.75")
    )
    assert seg_dec.exact_cost == Fraction(1, 2)
    assert seg_dec.exact_proposal_mass == Fraction(3, 4)

    # OverflowError in _require_nonnegative_finite
    with pytest.raises(PathDataError, match="finite nonnegative"):
        PathSegment("s3", "a", "b", cost=Fraction(10**1000, 1), verdict=1)

    # Unsupported type in _to_exact_rational
    with pytest.raises(PathDataError, match="unsupported type"):
        core._to_exact_rational("not_a_number", "test")  # type: ignore[arg-type]

    # numerical_status: "finite", "overflow", "nan_residual"
    finite_audit = KernelCompositionAudit(True, True, True, None, 1.0, 1.0, ())
    assert finite_audit.numerical_status == "finite"

    overflow_audit = KernelCompositionAudit(True, True, True, None, math.inf, 1.0, ())
    assert overflow_audit.numerical_status == "overflow"

    nan_audit = KernelCompositionAudit(True, True, True, None, float("nan"), 1.0, ())
    assert nan_audit.numerical_status == "nan_residual"


