"""Unit tests for The Anomalon Boundary reference implementation."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_anomalon_boundary_core import (
    AnomalonBoundary,
    CochainComplex,
    CochainDefect,
    ContinuationType,
    DefectStatus,
    FirewallViolationError,
    LiftPreservationWitness,
    MinimalKnowableSystem,
)


def test_defect_classification_trichotomy():
    # 1. Exact discrepancy (in im(d^0), closed, zero curvature)
    d_exact = CochainDefect(
        defect_id="d1",
        mass=Fraction(1, 4),
        is_closed=True,
        is_exact=True,
        closure_defect=Fraction(0),
    )
    assert d_exact.classify() == DefectStatus.VANISHES_AS_GAUGE

    # 2. Active closure failure (d^1 h != 0, Gamma_2 > 0)
    d_unclosed = CochainDefect(
        defect_id="d2",
        mass=Fraction(1, 2),
        is_closed=False,
        is_exact=False,
        closure_defect=Fraction(1, 8),
    )
    assert d_unclosed.classify() == DefectStatus.ACTIVE_INCOHERENCE

    # 3. Closed non-exact discrepancy (d^1 h == 0, h not in im(d^0))
    d_survivor = CochainDefect(
        defect_id="d3",
        mass=Fraction(3, 8),
        is_closed=True,
        is_exact=False,
        closure_defect=Fraction(0),
    )
    assert d_survivor.classify() == DefectStatus.SURVIVING_PRIMITIVE_DIFFERENCE


def test_cochain_complex_explicit_matrix_computation():
    # Cycle graph C_3: 3 vertices, 3 directed edges, no 2-cells (C^2 = 1 with zero coboundary)
    # d0 maps vertices to edges (e01 = v1 - v0, e12 = v2 - v1, e20 = v0 - v2)
    d0 = [
        [-1, 1, 0],   # e01
        [0, -1, 1],   # e12
        [1, 0, -1],   # e20
    ]
    # d1: 1-row zero coboundary (closed 1-chain cycle complex)
    d1 = [
        [0, 0, 0]
    ]

    complex_c3 = CochainComplex(d0=d0, d1=d1)

    # 1. Exact cochain: h = d0 * [2, 0, 1] = [-2, 1, 1]
    h_exact = [-2, 1, 1]
    defect_exact = complex_c3.analyze_defect(h_exact, defect_id="exact-1")
    assert defect_exact.is_closed is True
    assert defect_exact.is_exact is True
    assert defect_exact.closure_defect == Fraction(0)
    assert defect_exact.classify() == DefectStatus.VANISHES_AS_GAUGE

    # 2. Closed non-exact cochain: cycle h = [1, 1, 1] (generates H^1(C_3) != 0)
    h_cycle = [1, 1, 1]
    defect_cycle = complex_c3.analyze_defect(h_cycle, defect_id="cycle-1")
    assert defect_cycle.is_closed is True
    assert defect_cycle.is_exact is False
    assert defect_cycle.closure_defect == Fraction(0)
    assert defect_cycle.classify() == DefectStatus.SURVIVING_PRIMITIVE_DIFFERENCE

    # 3. Complex with non-trivial curvature d1: triangle with face f012 (d1 = [1, 1, 1])
    d1_face = [[1, 1, 1]]
    complex_filled = CochainComplex(d0=d0, d1=d1_face)

    # Non-closed cochain on filled triangle: h = [1, 0, 0] -> d1 h = 1 != 0
    defect_unclosed = complex_filled.analyze_defect([1, 0, 0], defect_id="unclosed-1")
    assert defect_unclosed.is_closed is False
    assert defect_unclosed.is_exact is False
    assert defect_unclosed.closure_defect == Fraction(1)
    assert defect_unclosed.classify() == DefectStatus.ACTIVE_INCOHERENCE


def test_cochain_defect_rejects_inconsistent_input():
    # Direct probe 1: exact defect with positive closure defect must fail
    with pytest.raises(ValueError, match="Inconsistent cochain defect: an exact discrepancy must be closed"):
        CochainDefect(
            defect_id="inconsistent-1",
            mass=Fraction(1),
            is_closed=True,
            is_exact=True,
            closure_defect=Fraction(1, 2),
        )

    # Direct probe 2: exact defect with is_closed=False must fail
    with pytest.raises(ValueError, match="Inconsistent cochain defect: an exact discrepancy must be closed"):
        CochainDefect(
            defect_id="inconsistent-2",
            mass=Fraction(1),
            is_closed=False,
            is_exact=True,
            closure_defect=Fraction(0),
        )

    # Direct probe 3: negative closure defect must fail
    with pytest.raises(ValueError, match="closure_defect cannot be negative"):
        CochainDefect(
            defect_id="inconsistent-3",
            mass=Fraction(1),
            is_closed=True,
            is_exact=False,
            closure_defect=Fraction(-1, 2),
        )

    # Direct probe 4: negative mass must fail
    with pytest.raises(ValueError, match="mass cannot be negative"):
        CochainDefect(
            defect_id="inconsistent-4",
            mass=Fraction(-1),
            is_closed=True,
            is_exact=False,
            closure_defect=Fraction(0),
        )

    # Direct probe 5: invalid complex where d1 * d0 != 0 must fail
    d0_bad = [[1, 0], [0, 1]]
    d1_bad = [[1, 1]]  # d1 * d0 = [1, 1] != [0, 0]
    with pytest.raises(ValueError, match="Invalid cochain complex:.*Coboundary condition d\\^1 d\\^0 = 0 fails"):
        CochainComplex(d0=d0_bad, d1=d1_bad)


def test_anomalon_boundary_validation():
    # Reject non-positive residual mass
    with pytest.raises(ValueError, match="strictly positive residual mass"):
        AnomalonBoundary(residual_id="R1", residual_mass=Fraction(0), exhausted_repairs_count=3)

    with pytest.raises(ValueError, match="strictly positive residual mass"):
        AnomalonBoundary(residual_id="R1", residual_mass=Fraction(-1, 2), exhausted_repairs_count=3)

    # Reject non-positive exhausted repairs count
    with pytest.raises(ValueError, match="exhausted_repairs_count > 0"):
        AnomalonBoundary(residual_id="R1", residual_mass=Fraction(1), exhausted_repairs_count=0)

    # Reject empty residual ID
    with pytest.raises(ValueError, match="non-empty residual_id"):
        AnomalonBoundary(residual_id="  ", residual_mass=Fraction(1), exhausted_repairs_count=1)


def test_anomalon_boundary_continuations():
    boundary = AnomalonBoundary(
        residual_id="RESIDUAL-S42",
        residual_mass=Fraction(7, 10),
        exhausted_repairs_count=5,
    )

    # 1. Typed refusal
    res_refusal = boundary.request_continuation(
        ContinuationType.TYPED_REFUSAL,
        witness_or_reason="Current 1-complex lacks degree of freedom to repair S42",
    )
    assert res_refusal["continuation"] == ContinuationType.TYPED_REFUSAL
    assert res_refusal["status"] == "REFUSAL_RECORDED"

    # 2. Lift request (requested, not yet authorized)
    res_lift = boundary.request_continuation(
        ContinuationType.LIFT_REQUEST,
        witness_or_reason="Extend 1-skeleton with 2-cell boundary sigma_2",
    )
    assert res_lift["continuation"] == ContinuationType.LIFT_REQUEST
    assert res_lift["status"] == "LIFT_REQUESTED"

    # 3. Restart seed
    res_restart = boundary.request_continuation(
        ContinuationType.RESTART_SEED,
        witness_or_reason="Seed next cycle with residual mass 7/10",
    )
    assert res_restart["continuation"] == ContinuationType.RESTART_SEED
    assert res_restart["status"] == "RESTART_SCHEDULED"

    # Reject arbitrary string instead of ContinuationType enum
    with pytest.raises(TypeError, match="continuation_type must be a ContinuationType enum instance"):
        boundary.request_continuation("ArbitraryString", witness_or_reason="reason")  # type: ignore

    # Reject empty witness or reason
    with pytest.raises(ValueError, match="requires non-empty witness or reason string"):
        boundary.request_continuation(ContinuationType.TYPED_REFUSAL, witness_or_reason="")


def test_anomalon_boundary_lift_authorization():
    boundary = AnomalonBoundary(
        residual_id="RESIDUAL-S42",
        residual_mass=Fraction(7, 10),
        exhausted_repairs_count=5,
    )

    # Valid preservation witness Delta_Lambda > 0
    valid_witness = LiftPreservationWitness(
        contract_id="CONTRACT-PRESERVE-2D",
        target_dimension=2,
        preservation_metric=Fraction(1, 4),
    )
    auth_result = boundary.authorize_lift(valid_witness)
    assert auth_result["status"] == "LIFT_AUTHORIZED"
    assert auth_result["target_dimension"] == 2
    assert auth_result["preservation_metric"] == Fraction(1, 4)

    # Reject invalid preservation metric (Delta_Lambda <= 0)
    with pytest.raises(ValueError, match="Preservation metric Delta_Lambda must be strictly positive"):
        LiftPreservationWitness(
            contract_id="CONTRACT-BAD",
            target_dimension=2,
            preservation_metric=Fraction(0),
        )

    # Reject non-witness object in authorize_lift
    with pytest.raises(FirewallViolationError, match="requires a valid LiftPreservationWitness"):
        boundary.authorize_lift("not a witness")  # type: ignore


def test_anomalon_non_promotion_rule():
    boundary = AnomalonBoundary(
        residual_id="RESIDUAL-UNRESOLVED",
        residual_mass=Fraction(1),
        exhausted_repairs_count=10,
    )

    with pytest.raises(FirewallViolationError, match="Firewall Refusal: Anomalon boundary"):
        boundary.assert_no_authority_promotion()


def test_minimal_knowable_system_completeness():
    mks_complete = MinimalKnowableSystem()
    is_ok, missing = mks_complete.check_completeness()
    assert is_ok is True
    assert missing == []

    mks_broken = MinimalKnowableSystem(
        gauge=False,
        closure_defect=False,
    )
    is_ok2, missing2 = mks_broken.check_completeness()
    assert is_ok2 is False
    assert "Gauge" in missing2
    assert "Closure defect" in missing2
