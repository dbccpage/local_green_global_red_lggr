"""Tests for F_2^3 three-key configuration merge worked example and counterfeit closure detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cochain_example import (
    CochainConflictState,
    audit_merge_execution,
    d0,
    d1,
    evaluate_cochain,
    is_exact,
    run_collapsed_merge_without_residual_role,
    run_full_stack_merge,
)
from models import CoreResidualClass, FailureMode, TerminalStatus


def test_zero_defect_clean_merge():
    """Identical configurations yield zero cochain and clean resolution."""
    state = CochainConflictState(source_a=(1, 0, 1), source_b=(1, 0, 1))
    assert state.is_exact_zero()
    assert state.difference_cochain == (0, 0, 0)
    assert evaluate_cochain(state) == CoreResidualClass.RESOLVED_EXACT

    # Without an explicit receipt registry, authority is withheld fail-closed
    terminal_no_reg = run_full_stack_merge(state)
    assert terminal_no_reg.status == TerminalStatus.REFUSAL
    assert terminal_no_reg.is_authority is False

    # With explicit registry and proposal binding, authority is issued with receipt
    from models import AuthorityReceiptRegistry, Proposal
    registry = AuthorityReceiptRegistry("merge_registry")
    proposal = Proposal(id=77, payload="merge_test")
    terminal_with_reg = run_full_stack_merge(state, registry=registry, proposal=proposal)
    assert terminal_with_reg.status == TerminalStatus.AUTHORITY
    assert terminal_with_reg.is_authority is True
    assert terminal_with_reg.token is not None
    assert terminal_with_reg.token.proposal_id == 77
    assert registry.validates(proposal, terminal_with_reg.token) is True
    assert audit_merge_execution(state, terminal_with_reg) is None


def test_section_3_1_worked_example_non_zero_conflict():
    """Verify section 3.1 scenario: conflict on key 2 produces r = (0, 1, 0)."""
    # Source A has key 2 = 0; Source B has key 2 = 1
    state = CochainConflictState(source_a=(1, 0, 0), source_b=(1, 1, 0))
    r = state.difference_cochain
    assert r == (0, 1, 0)
    assert not state.is_exact_zero()

    # The stated d1 sends the third coordinate to F_2, so this residual is closed.
    assert state.boundary_d1() == 0
    assert not is_exact(r)
    assert evaluate_cochain(state) == CoreResidualClass.CLOSED_RESIDUAL

    # 1. Compliant Full-Stack run:
    # Residual Closure role lawfully houses the conflict as ResidualClosed
    compliant_terminal = run_full_stack_merge(state)
    assert compliant_terminal.status == TerminalStatus.RESIDUAL_CLOSED
    assert compliant_terminal.residual_class == CoreResidualClass.CLOSED_RESIDUAL

    # Compliant run passes audit without flagging counterfeit closure
    audit_compliant = audit_merge_execution(state, compliant_terminal)
    assert audit_compliant is None

    # 2. Collapsed run (Residual Closure role removed):
    # System falsely outputs ResolvedExact without repair witness
    collapsed_terminal = run_collapsed_merge_without_residual_role(state)
    assert collapsed_terminal.status == TerminalStatus.AUTHORITY

    # Auditor immediately detects counterfeit closure from ledger row!
    audit_collapsed = audit_merge_execution(state, collapsed_terminal)
    assert audit_collapsed == FailureMode.RESIDUAL_GETS_HIDDEN_OR_RENAMED


def test_repair_witness_must_be_a_preimage_under_d0():
    """A repair is valid only if d0(alpha) equals the residual exactly."""
    state = CochainConflictState(source_a=(1, 0, 0), source_b=(0, 0, 0))
    assert state.difference_cochain == d0(1)
    assert is_exact(state.difference_cochain)
    assert d1(state.difference_cochain) == 0
    collapsed_terminal = run_collapsed_merge_without_residual_role(state)
    assert audit_merge_execution(state, collapsed_terminal, repair_witness=1) is None


def test_nonzero_boundary_is_open_not_closed():
    state = CochainConflictState(source_a=(0, 0, 1), source_b=(0, 0, 0))
    assert state.boundary_d1() == 1
    assert evaluate_cochain(state) == CoreResidualClass.OPEN_RESIDUAL


def test_exact_nonzero_residual_is_not_closed_non_exact():
    """A residual in im(d0) is repairable by a witness; it is not a closed non-exact residual."""
    state = CochainConflictState(source_a=(1, 0, 0), source_b=(0, 0, 0))
    assert is_exact(state.difference_cochain)
    assert evaluate_cochain(state) == CoreResidualClass.RESOLVED_EXACT
    terminal = run_full_stack_merge(state)
    assert terminal.status == TerminalStatus.REFUSAL
    assert not terminal.is_authority
