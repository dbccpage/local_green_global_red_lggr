"""Tests for residual honesty taxonomy and honest refusal terminals."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from classifier import (
    CochainEvaluation,
    classify_terminal_outcome,
    evaluate_cochain_defect,
    gate_authority_issuance,
)
from cochain_example import d0, d1, is_exact
from models import (
    AuthorityReceiptRegistry,
    CoreResidualClass,
    MathematicalDefectClass,
    Proposal,
    TerminalStatus,
)


def test_budget_exhaustion_honest_refusal():
    """Verify that exhausting budget triggers BudgetUnknown ('I do not know') rather than counterfeiting."""
    terminal = classify_terminal_outcome(
        defect_mass=0.0,
        boundary_mass=0.0,
        max_dim_checked=2,
        budget_remaining=0,  # Exhausted budget!
    )
    assert terminal.status == TerminalStatus.BUDGET_UNKNOWN
    assert "honest refusal" in terminal.reason


def test_zero_defect_clean_closure():
    """Zero defect mass produces exact mathematical evaluation; authority requires distinct gate."""
    registry = AuthorityReceiptRegistry("test_exact_verifier")
    proposal = Proposal(id=42, payload="test_payload_42")

    # Step 1: Mathematical evaluation
    eval_result = evaluate_cochain_defect(defect_mass=0.0, boundary_mass=0.0)
    assert eval_result.defect_class == MathematicalDefectClass.ZERO_DEFECT
    assert eval_result.is_exact is True
    assert eval_result.is_closed is True

    # Step 2: Classifier alone does NOT manufacture authority
    terminal = classify_terminal_outcome(
        defect_mass=0.0,
        boundary_mass=0.0,
        max_dim_checked=2,
        budget_remaining=100,
    )
    assert terminal.status == TerminalStatus.REFUSAL
    assert terminal.is_authority is False
    assert terminal.residual_class == CoreResidualClass.RESOLVED_EXACT

    # Step 3: Distinct authority gate checks contract & registry to issue authority
    auth_terminal = gate_authority_issuance(proposal, eval_result, registry)
    assert auth_terminal.status == TerminalStatus.AUTHORITY
    assert auth_terminal.is_authority is True
    assert auth_terminal.residual_class == CoreResidualClass.RESOLVED_EXACT
    assert auth_terminal.token is not None
    assert auth_terminal.token.proposal_id == 42
    assert auth_terminal.token.is_well_formed_for(proposal) is True
    assert registry.validates(proposal, auth_terminal.token) is True


def test_closed_residual_stable_survivor():
    """Non-zero defect with zero boundary and non-exact status produces ClosedResidual."""
    terminal = classify_terminal_outcome(
        defect_mass=1.5,
        boundary_mass=0.0,
        is_exact=False,
        max_dim_checked=2,
        budget_remaining=100,
    )
    assert terminal.status == TerminalStatus.RESIDUAL_CLOSED
    assert terminal.residual_class == CoreResidualClass.CLOSED_RESIDUAL
    assert "persistent closed residual" in terminal.reason


def test_open_boundary_residual():
    """Non-zero boundary produces OpenResidual."""
    terminal = classify_terminal_outcome(
        defect_mass=2.0,
        boundary_mass=0.8,
        max_dim_checked=3,
        budget_remaining=50,
    )
    assert terminal.status == TerminalStatus.RESIDUAL_OPEN
    assert terminal.residual_class == CoreResidualClass.OPEN_RESIDUAL
    assert "Open boundary defect" in terminal.reason


def test_information_deficiency_equal_mass_counterexample():
    """Regression test for Review Finding 1:
    r_e = (1, 0, 0) is exact (r_e = d0(1)), mass = 1, boundary = 0.
    r_h = (0, 1, 0) is non-exact (r_h not in im d0), mass = 1, boundary = 0.
    Norms alone cannot distinguish them; cochain data or exactness certificate is required.
    """
    # 1. Unchecked masses alone fail closed with Information Deficiency ValueError
    with pytest.raises(ValueError, match="Information deficiency"):
        evaluate_cochain_defect(defect_mass=1.0, boundary_mass=0.0)

    # 2. With differential and cochain data, the two are correctly distinguished:
    r_e = (1, 0, 0)
    r_h = (0, 1, 0)

    eval_exact = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r_e,
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
    )
    assert eval_exact.defect_class == MathematicalDefectClass.EXACT_REPAIRABLE
    assert eval_exact.is_exact is True
    assert eval_exact.is_closed is True

    eval_non_exact = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r_h,
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
    )
    assert eval_non_exact.defect_class == MathematicalDefectClass.CLOSED_NON_EXACT
    assert eval_non_exact.is_exact is False
    assert eval_non_exact.is_closed is True


def test_inconsistent_zero_defect_nonzero_boundary_rejected():
    """Regression test for Review Finding 2:
    Zero defect cannot have nonzero boundary in a linear complex (d1(0) = 0).
    Inconsistent inputs must be rejected fail-closed.
    """
    with pytest.raises(ValueError, match="Inconsistent cochain evaluation"):
        evaluate_cochain_defect(defect_mass=0.0, boundary_mass=1.0)


def test_authority_issuance_requires_verified_repair_for_exact_nonzero():
    """Exact nonzero defect cannot receive authority without a verified repair witness."""
    registry = AuthorityReceiptRegistry("test_repair_verifier")
    proposal = Proposal(id=99, payload="repair_test")
    r_e = (1, 0, 0)

    # Without repair witness: authority withheld
    eval_no_witness = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r_e,
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
        repair_witness=None,
    )
    t_no_witness = gate_authority_issuance(proposal, eval_no_witness, registry)
    assert t_no_witness.status == TerminalStatus.REFUSAL
    assert not t_no_witness.is_authority

    # With verified repair witness alpha=1 (d0(1) == (1,0,0)): authority granted
    eval_with_witness = evaluate_cochain_defect(
        defect_mass=1.0,
        boundary_mass=0.0,
        cochain=r_e,
        d0_fn=d0,
        d1_fn=d1,
        is_exact_fn=is_exact,
        repair_witness=1,
    )
    t_with_witness = gate_authority_issuance(proposal, eval_with_witness, registry)
    assert t_with_witness.status == TerminalStatus.AUTHORITY
    assert t_with_witness.is_authority is True
    assert registry.validates(proposal, t_with_witness.token) is True
