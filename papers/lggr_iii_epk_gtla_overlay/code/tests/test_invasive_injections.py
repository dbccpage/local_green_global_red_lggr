"""Twelve paired break-detect-recover mutations for the public finite model."""

from __future__ import annotations

from dataclasses import replace

import pytest

import epk_gtla_overlay_core as core
from epk_gtla_overlay_core import CompositePath, EvaluatorVerdictTriple, PathSegment


def fixture() -> tuple[
    tuple[PathSegment, ...], tuple[PathSegment, ...], tuple[CompositePath, ...]
]:
    first = (PathSegment("ab", "a", "b", 1, 1, 0.4),)
    second = (PathSegment("bc", "b", "c", 2, 1, 0.5),)
    composites = (CompositePath("abc", "ab", "bc", 3, 1, 0.2),)
    return first, second, composites


def test_mutation_01_nonbinary_verdict_then_binary_recovery() -> None:
    with pytest.raises(core.InvalidVerdictError):
        EvaluatorVerdictTriple(1, 2, 0)
    assert EvaluatorVerdictTriple(1, 1, 0).evaluator_defect == -1


def test_mutation_02_missing_compatible_pair_then_restore() -> None:
    first, second, composites = fixture()
    assert not core.boundary_bijection_report(first, second, ()).is_bijection
    assert core.boundary_bijection_report(first, second, composites).is_bijection


def test_mutation_03_duplicate_pair_then_unique_recovery() -> None:
    first, second, composites = fixture()
    duplicate = replace(composites[0], identifier="abc-copy")
    broken = core.boundary_bijection_report(first, second, composites + (duplicate,))
    assert not broken.is_bijection
    assert any("duplicated" in issue for issue in broken.issues)
    assert core.boundary_bijection_report(first, second, composites).is_bijection


def test_mutation_04_unknown_segment_then_declared_recovery() -> None:
    first, second, composites = fixture()
    unknown = (replace(composites[0], first_id="not-declared"),)
    broken = core.audit_kernel_composition(first, second, unknown, decay=1)
    assert not broken.g1_bijection and not broken.g2_cost_additive
    assert core.audit_kernel_composition(
        first, second, composites, decay=1
    ).hypotheses_hold


def test_mutation_05_incompatible_boundary_then_compatible_recovery() -> None:
    first, second, composites = fixture()
    wrong_second = (replace(second[0], source="elsewhere"),)
    broken = core.boundary_bijection_report(first, wrong_second, composites)
    assert not broken.is_bijection
    assert any("incompatible" in issue for issue in broken.issues)
    assert core.boundary_bijection_report(first, second, composites).is_bijection


def test_mutation_06_nonadditive_cost_then_sum_recovery() -> None:
    first, second, composites = fixture()
    broken = core.audit_kernel_composition(
        first, second, (replace(composites[0], cost=4),), decay=1
    )
    assert not broken.g2_cost_additive
    assert core.audit_kernel_composition(
        first, second, composites, decay=1
    ).g2_cost_additive


def test_mutation_07_nonfactorized_verdict_then_product_recovery() -> None:
    first, second, composites = fixture()
    broken = core.audit_kernel_composition(
        first, second, (replace(composites[0], verdict=0),), decay=1
    )
    assert not broken.g3_evaluator_factorized
    assert core.audit_kernel_composition(
        first, second, composites, decay=1
    ).g3_evaluator_factorized


def test_mutation_08_nonfactorized_proposal_then_product_recovery() -> None:
    first, second, composites = fixture()
    broken = core.audit_kernel_composition(
        first,
        second,
        (replace(composites[0], proposal_mass=0.3),),
        decay=1,
        proposal_weighted=True,
    )
    assert broken.g4_proposal_factorized is False
    healed = core.audit_kernel_composition(
        first, second, composites, decay=1, proposal_weighted=True
    )
    assert healed.g4_proposal_factorized is True


def test_mutation_09_aggregate_cancellation_then_pointwise_recovery() -> None:
    masked = core.audit_sample(
        (EvaluatorVerdictTriple(0, 1, 1), EvaluatorVerdictTriple(1, 1, 0))
    )
    assert masked.defect_sum == 0 and masked.has_aggregate_cancellation
    healed = core.audit_sample((EvaluatorVerdictTriple(1, 1, 1),))
    assert healed.defect_sum == 0 and not healed.has_aggregate_cancellation


def test_mutation_10_mixed_quotient_class_then_split_recovery() -> None:
    """Test that mixed quotient class obstructs descent; splitting refines the quotient.

    Splitting an equivalence class by verdict changes the equivalence relation and
    refines the partition (altering the quotient projection q). This demonstrates
    descent on a refined quotient, not repair while preserving the original relation.
    """
    elements = (("one", 0), ("one", 1))
    with pytest.raises(core.QuotientDescentError):
        core.descend_evaluator(elements, lambda item: item[0], lambda item: item[1])
    healed = core.descend_evaluator(
        elements, lambda item: (item[0], item[1]), lambda item: item[1]
    )
    assert healed == {("one", 0): 0, ("one", 1): 1}



def test_mutation_11_constant_detector_then_variable_recovery() -> None:
    with pytest.raises(core.DetectorAdequacyError):
        core.require_non_collapsing((1, 1, 1))
    assert core.require_non_collapsing((1, 0, 1))


def test_mutation_12_changed_observation_then_fixed_recovery() -> None:
    before = EvaluatorVerdictTriple(1, 1, 0)
    with pytest.raises(core.ObservationChangedError):
        core.fixed_observation_preserves_defect(before, EvaluatorVerdictTriple(1, 1, 1))
    assert core.fixed_observation_preserves_defect(before, before)
