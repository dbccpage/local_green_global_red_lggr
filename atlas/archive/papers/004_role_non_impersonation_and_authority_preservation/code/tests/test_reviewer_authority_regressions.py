"""Regression tests addressing the external authority preservation review findings.

Verifies:
1. Claimed zero mass with nonzero boundary or nonzero cochain is rejected fail-closed.
2. Negative, infinite, and NaN defect/boundary masses are rejected.
3. Missing differential d0_fn leaves repair witness unverified and refuses authority.
4. Incorrect repair witness d0(alpha) != r is rejected and refuses authority.
5. Tampered or forged CochainEvaluation labels cannot bypass the authority gate.
6. Vector-valued differentials with canceling signed sums (e.g. (1, -1)) are not treated as zero boundary.
7. CochainConflictState enforces exactly 3 coordinates in F_2, preventing silent truncation.
8. Proposal-bound evaluation records prevent authority cross-issuance across different proposals.
"""

from __future__ import annotations

import dataclasses
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from classifier import (
    CochainEvaluation,
    evaluate_cochain_defect,
    gate_authority_issuance,
)
from cochain_example import CochainConflictState, d0, d1, is_exact
from models import (
    AuthorityReceiptRegistry,
    AuthorityToken,
    CoreResidualClass,
    MathematicalDefectClass,
    Proposal,
    TerminalStatus,
)
from pipeline import verify_authority


# --- 1 & 2: Claimed zero mass overrides and invalid numeric inputs ---

def test_claimed_zero_mass_with_nonzero_boundary_rejected():
    """Claimed defect_mass=0.0 cannot override a computed nonzero boundary."""
    with pytest.raises(ValueError, match="Inconsistent cochain evaluation"):
        evaluate_cochain_defect(
            defect_mass=0.0,
            boundary_mass=0.0,
            cochain=(0, 0, 1),
            d1_fn=d1,
            is_exact_fn=is_exact,
        )


def test_claimed_zero_mass_with_closed_non_exact_cochain_rejected():
    """Claimed defect_mass=0.0 cannot override a nonzero non-exact cochain."""
    with pytest.raises(ValueError, match="Inconsistent cochain evaluation"):
        evaluate_cochain_defect(
            defect_mass=0.0,
            boundary_mass=0.0,
            cochain=(0, 1, 0),
            d1_fn=d1,
            is_exact_fn=is_exact,
        )


def test_negative_defect_mass_rejected():
    with pytest.raises(ValueError, match="Invalid defect_mass"):
        evaluate_cochain_defect(defect_mass=-1.0, boundary_mass=0.0)


def test_nan_and_inf_defect_mass_rejected():
    with pytest.raises(ValueError, match="Invalid defect_mass"):
        evaluate_cochain_defect(defect_mass=float("nan"), boundary_mass=0.0)
    with pytest.raises(ValueError, match="Invalid defect_mass"):
        evaluate_cochain_defect(defect_mass=float("inf"), boundary_mass=0.0)


def test_negative_and_nan_boundary_mass_rejected():
    with pytest.raises(ValueError, match="Invalid boundary_mass"):
        evaluate_cochain_defect(defect_mass=1.0, boundary_mass=-0.5)
    with pytest.raises(ValueError, match="Invalid boundary_mass"):
        evaluate_cochain_defect(defect_mass=1.0, boundary_mass=float("nan"))
    with pytest.raises(ValueError, match="Invalid boundary_mass"):
        evaluate_cochain_defect(defect_mass=1.0, boundary_mass=float("inf"))


# --- 3 & 4: Witness verification and missing differential ---

def test_missing_d0_differential_leaves_witness_unverified_and_refuses_authority():
    """Omitting d0_fn means the witness equation was not checked; authority must be refused."""
    registry = AuthorityReceiptRegistry("test_witness_verifier")
    proposal = Proposal(id=1, payload="witness_missing_d0_test")
    r = (1, 0, 0)
    alpha = 0  # Note: d0(0) = (0,0,0) != (1,0,0), so this is also a wrong witness

    # Supply d1 and is_exact, but omit d0_fn
    evaluation = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r,
        d1_fn=d1,
        is_exact_fn=is_exact,
        repair_witness=alpha,
        d0_fn=None,
    )
    assert evaluation.defect_class == MathematicalDefectClass.EXACT_REPAIRABLE
    assert evaluation.witness_verified is False
    assert evaluation.repair_witness is None

    # Gate must refuse authority
    terminal = gate_authority_issuance(proposal, evaluation, registry)
    assert terminal.status == TerminalStatus.REFUSAL
    assert not terminal.is_authority
    assert verify_authority(proposal, terminal, registry) is False


def test_invalid_repair_witness_equation_rejected():
    """Supplying d0_fn when d0(alpha) != r must reject the witness and refuse authority."""
    registry = AuthorityReceiptRegistry("test_witness_verifier")
    proposal = Proposal(id=2, payload="witness_wrong_value_test")
    r = (1, 0, 0)
    alpha = 0  # d0(0) = (0, 0, 0) != (1, 0, 0)

    evaluation = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r,
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
        repair_witness=alpha,
    )
    assert evaluation.witness_verified is False
    assert evaluation.repair_witness is None

    terminal = gate_authority_issuance(proposal, evaluation, registry)
    assert terminal.status == TerminalStatus.REFUSAL
    assert not terminal.is_authority
    assert verify_authority(proposal, terminal, registry) is False


def test_valid_repair_witness_equation_grants_authority():
    """Supplying valid witness alpha=1 where d0(1) == (1,0,0) grants authority."""
    registry = AuthorityReceiptRegistry("test_witness_verifier")
    proposal = Proposal(id=3, payload="witness_correct_value_test")
    r = (1, 0, 0)
    alpha = 1

    evaluation = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r,
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
        repair_witness=alpha,
    )
    assert evaluation.witness_verified is True
    assert evaluation.repair_witness == 1

    terminal = gate_authority_issuance(proposal, evaluation, registry)
    assert terminal.status == TerminalStatus.AUTHORITY
    assert terminal.is_authority is True
    assert verify_authority(proposal, terminal, registry) is True


# --- 5: Forged evaluation label cannot bypass the authority gate ---

def test_forged_evaluation_label_rejected_by_invariants():
    """Replacing defect_class on an honest evaluation violates dataclass invariants."""
    honest_eval = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=(0, 1, 0),
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
    )
    assert honest_eval.defect_class == MathematicalDefectClass.CLOSED_NON_EXACT

    # Forging defect_class to ZERO_DEFECT must be rejected by dataclass post_init
    with pytest.raises(ValueError, match="ZERO_DEFECT requires defect_mass == 0.0"):
        dataclasses.replace(
            honest_eval,
            defect_class=MathematicalDefectClass.ZERO_DEFECT,
        )


def test_gate_rechecks_metrics_and_refuses_inconsistent_evidence():
    """Even if an inconsistent evaluation bypasses dataclass creation, the gate refuses."""
    registry = AuthorityReceiptRegistry("test_gate_verifier")
    proposal = Proposal(id=4, payload="forgery_test")

    # Construct an invalid object bypassing constructor via object.__setattr__
    mock_eval = CochainEvaluation(
        defect_mass=0.0,
        boundary_mass=0.0,
        is_exact=True,
        is_closed=True,
        defect_class=MathematicalDefectClass.ZERO_DEFECT,
    )
    object.__setattr__(mock_eval, "defect_mass", 1.0)  # corrupt defect_mass

    terminal = gate_authority_issuance(proposal, mock_eval, registry)
    assert terminal.status == TerminalStatus.REFUSAL
    assert not terminal.is_authority
    assert verify_authority(proposal, terminal, registry) is False


# --- 6: Vector differential with canceling signed sums ---

def test_vector_differential_signed_sum_cannot_hide_nonzero_boundary():
    """Real linear complex d1(x) = (x, -x) has nonzero boundary (1, -1) for r=1."""
    def d1_vector(x):
        return (x, -x)

    evaluation = evaluate_cochain_defect(
        defect_mass=1.0,
        cochain=1,
        d1_fn=d1_vector,
        is_exact_fn=lambda _: False,
    )
    # L1 norm of (1, -1) is 1 + 1 = 2.0 > 0.0
    assert evaluation.boundary_mass == 2.0
    assert evaluation.is_closed is False
    assert evaluation.defect_class == MathematicalDefectClass.OPEN_DEFECT


# --- 7: CochainConflictState carrier validation ---

def test_cochain_conflict_state_rejects_unequal_lengths():
    """Unequal configuration lengths must raise ValueError, not silently truncate."""
    with pytest.raises(ValueError, match="Configuration vectors must have exactly 3 coordinates"):
        CochainConflictState(source_a=(0, 0, 0, 1), source_b=(0, 0, 0))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Configuration vectors must have exactly 3 coordinates"):
        CochainConflictState(source_a=(0, 0), source_b=(0, 0, 0))  # type: ignore[arg-type]


def test_cochain_conflict_state_rejects_non_binary_values():
    """Values outside F_2 must raise ValueError."""
    with pytest.raises(ValueError, match="must be in F_2"):
        CochainConflictState(source_a=(2, 0, 0), source_b=(0, 0, 0))


# --- 8: Proposal binding ---

def test_proposal_binding_prevents_cross_issuance():
    """Evaluation bound to proposal A cannot authorize proposal B."""
    registry = AuthorityReceiptRegistry("test_binding_verifier")
    proposal_a = Proposal(id=10, payload="task_a")
    proposal_b = Proposal(id=20, payload="task_b")

    eval_a = evaluate_cochain_defect(
        defect_mass=0.0,
        boundary_mass=0.0,
        proposal_id=proposal_a.id,
    )

    # Authority for proposal_a succeeds
    term_a = gate_authority_issuance(proposal_a, eval_a, registry)
    assert term_a.status == TerminalStatus.AUTHORITY
    assert verify_authority(proposal_a, term_a, registry) is True

    # Attempting to use eval_a for proposal_b is refused fail-closed
    term_b = gate_authority_issuance(proposal_b, eval_a, registry)
    assert term_b.status == TerminalStatus.REFUSAL
    assert not term_b.is_authority
    assert verify_authority(proposal_b, term_b, registry) is False
