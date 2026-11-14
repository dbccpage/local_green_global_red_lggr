"""Unit tests for the Authority Firewall reference implementation."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_authority_firewall_core import (
    AuthEvidence,
    AuthorityFirewall,
    Coproduct,
    FirewallViolationError,
    IsAuthGuards,
    ResidualClass,
    ResidualFailure,
    SolverAuditSimulation,
    auth_terminal,
    is_auth,
    residual_not_auth,
    residual_terminal,
)


def test_coproduct_constructor_disjointness():
    evidence = AuthEvidence(packet_id="P1", terminalizer_id="T1", replayable=True)
    residual = ResidualClass(class_id="q42", defect_mass=Fraction(1, 10))

    t_auth = auth_terminal(evidence)
    t_res = residual_terminal(residual)

    assert t_auth.is_inl is True
    assert t_auth.is_inr is False
    assert t_auth.inl_value == evidence

    assert t_res.is_inl is False
    assert t_res.is_inr is True
    assert t_res.inr_value == residual

    with pytest.raises(ValueError, match="Attempted to access inr_value on an inl summand"):
        _ = t_auth.inr_value

    with pytest.raises(ValueError, match="Attempted to access inl_value on an inr summand"):
        _ = t_res.inl_value


def test_pointwise_separation_theorem():
    r_class = ResidualClass(class_id="q42", defect_mass=Fraction(3, 100))
    r_fail = ResidualFailure(failure_mode="CYCLE_OBSTRUCTION", reason="Cohomology class non-zero")

    assert residual_not_auth(r_class) is True
    assert is_auth(residual_terminal(r_class)) is False

    assert residual_not_auth(r_fail) is True
    assert is_auth(residual_terminal(r_fail)) is False


def test_af02_witness_blocks_total_auth_extractor():
    witness = ResidualClass(class_id="q42", defect_mass=Fraction(3, 100))
    assert residual_not_auth(witness) is True
    assert is_auth(residual_terminal(witness)) is False


def test_refuse_residual_promotion():
    firewall = AuthorityFirewall()
    r = ResidualClass(class_id="q10", defect_mass=Fraction(1, 2))

    with pytest.raises(FirewallViolationError, match="Firewall Refusal"):
        firewall.attempt_residual_promotion(r)


def test_seven_guards_predicate():
    passing_guards = IsAuthGuards(
        verified_replay_hash=True,
        matching_replay=True,
        terminalizer_present=True,
        exhaustive_search=True,
        zero_defect=True,
        descent_witness=True,
        replay_freshness=True,
    )
    assert passing_guards.all_guards_met() is True

    failing_exhaustiveness = IsAuthGuards(
        verified_replay_hash=True,
        matching_replay=True,
        terminalizer_present=True,
        exhaustive_search=False,  # kappa != 0
        zero_defect=True,
        descent_witness=True,
        replay_freshness=True,
    )
    assert failing_exhaustiveness.all_guards_met() is False

    firewall = AuthorityFirewall(require_seven_guards=True)
    evidence = AuthEvidence(packet_id="P_FAIL", terminalizer_id="T_FAIL", replayable=True)

    routed = firewall.route_outcome(authority_evidence=evidence, guards=failing_exhaustiveness)
    assert routed.is_inl is False
    assert routed.is_inr is True
    assert isinstance(routed.inr_value, ResidualFailure)
    assert routed.inr_value.failure_mode == "GUARD_FAILURE"


def test_solver_audit_simulation_refusal():
    simulation = SolverAuditSimulation()
    audit = simulation.run_adversarial_audit()

    assert audit["missing_truth_tables"] == 233
    assert audit["exhaustiveness_survives"] is False
    assert audit["evaluator_independent"] is False
    assert audit["guards_passed"] is False

    firewall = AuthorityFirewall(require_seven_guards=True)
    terminal = simulation.evaluate_with_firewall(firewall)

    assert is_auth(terminal) is False
    assert terminal.is_inr is True
    defect = terminal.inr_value
    assert isinstance(defect, ResidualClass)
    assert defect.class_id == "AST_SHIFT_EXPR_DEFECT"
    assert defect.defect_mass == Fraction(233, 25768)


def test_genuine_authority_promotion():
    firewall = AuthorityFirewall(require_seven_guards=True)
    guards = IsAuthGuards(
        verified_replay_hash=True,
        matching_replay=True,
        terminalizer_present=True,
        exhaustive_search=True,
        zero_defect=True,
        descent_witness=True,
        replay_freshness=True,
    )
    evidence = AuthEvidence(packet_id="P_OK", terminalizer_id="T_OK", replayable=True)

    terminal = firewall.route_outcome(authority_evidence=evidence, guards=guards)
    assert is_auth(terminal) is True
    assert terminal.is_inl is True
    assert terminal.inl_value == evidence


def test_coproduct_rejects_empty_payload_or_mismatched_state():
    with pytest.raises(ValueError, match="requires a non-None _inl_val"):
        _ = Coproduct(is_inl=True, _inl_val=None, _inr_val=None)

    with pytest.raises(ValueError, match="requires a non-None _inr_val"):
        _ = Coproduct(is_inl=False, _inl_val=None, _inr_val=None)

    with pytest.raises(ValueError, match="Cannot construct inl with None payload"):
        _ = Coproduct.inl(None)

    with pytest.raises(ValueError, match="Cannot construct inr with None payload"):
        _ = Coproduct.inr(None)

    with pytest.raises(TypeError, match="is_inl must be an exact boolean"):
        _ = Coproduct(is_inl="True", _inl_val="data")  # type: ignore


def test_route_outcome_rejects_residual_passed_as_authority():
    firewall = AuthorityFirewall(require_seven_guards=True)
    residual = ResidualClass(class_id="q1", defect_mass=Fraction(1, 4))
    guards = IsAuthGuards(
        verified_replay_hash=True,
        matching_replay=True,
        terminalizer_present=True,
        exhaustive_search=True,
        zero_defect=True,
        descent_witness=True,
        replay_freshness=True,
    )

    with pytest.raises(TypeError, match="authority_evidence must be an instance of AuthEvidence"):
        _ = firewall.route_outcome(authority_evidence=residual, guards=guards)  # type: ignore


def test_guards_reject_non_boolean_values():
    with pytest.raises(TypeError, match="Guard 'verified_replay_hash' must be an exact boolean"):
        _ = IsAuthGuards(
            verified_replay_hash="False",  # type: ignore
            matching_replay=True,
            terminalizer_present=True,
            exhaustive_search=True,
            zero_defect=True,
            descent_witness=True,
            replay_freshness=True,
        )


def test_auth_evidence_validation_and_unreplayable_rejection():
    with pytest.raises(ValueError, match="packet_id must be a non-empty string"):
        _ = AuthEvidence(packet_id="", terminalizer_id="T1", replayable=True)

    with pytest.raises(ValueError, match="terminalizer_id must be a non-empty string"):
        _ = AuthEvidence(packet_id="P1", terminalizer_id="  ", replayable=True)

    with pytest.raises(TypeError, match="replayable must be an exact boolean"):
        _ = AuthEvidence(packet_id="P1", terminalizer_id="T1", replayable="yes")  # type: ignore

    # Unreplayable evidence must be refused authority promotion even with passing guards
    firewall = AuthorityFirewall(require_seven_guards=True)
    guards = IsAuthGuards(
        verified_replay_hash=True,
        matching_replay=True,
        terminalizer_present=True,
        exhaustive_search=True,
        zero_defect=True,
        descent_witness=True,
        replay_freshness=True,
    )
    unreplayable_evidence = AuthEvidence(packet_id="P_UNREPLAY", terminalizer_id="T1", replayable=False)
    routed = firewall.route_outcome(authority_evidence=unreplayable_evidence, guards=guards)
    assert routed.is_inr is True
    assert isinstance(routed.inr_value, ResidualFailure)
    assert routed.inr_value.failure_mode == "GUARD_FAILURE"

