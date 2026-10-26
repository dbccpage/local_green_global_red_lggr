"""Unit tests for Finite Authority and Non-Terminal Computation."""

from __future__ import annotations

from fractions import Fraction
import math
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_finite_authority_core import (
    EvaluatedPathKernel,
    GateStack,
    LGGRObstruction,
    ProposalTrace,
    RefusalReason,
    TerminalOutcome,
    TerminalStatus,
    TerminalWitness,
    compute_minimal_verdict_refinement,
    detect_counterfeit_descent,
    evaluate_halted_trace,
)


def test_epk_exact_rational_and_exponential_computation():
    t1 = ProposalTrace(
        trace_id="gamma_1",
        input_claim="x",
        extracted_answer="y",
        proposal_probability=Fraction(6, 10),
        cost=Fraction(1),
        residual_risk=Fraction(0),
    )
    t2 = ProposalTrace(
        trace_id="gamma_2",
        input_claim="x",
        extracted_answer="y",
        proposal_probability=Fraction(4, 10),
        cost=Fraction(2),
        residual_risk=Fraction(1),
    )

    epk = EvaluatedPathKernel(cost_sensitivity=Fraction(1), risk_sensitivity=Fraction(1))

    # 1. Exact rational Pade surrogate:
    # t1 discount = 1 / (1 + 1 + 0) = 1/2. Mass = 6/10 * 1/2 = 3/10
    # t2 discount = 1 / (1 + 2 + 1) = 1/4. Mass = 4/10 * 1/4 = 1/10
    # Total = 4/10 = 2/5 = 0.4
    rational_mass = epk.compute_rational_kernel([t1, t2], evaluator=lambda t: True)
    assert rational_mass == Fraction(2, 5)

    # 2. Continuous exponential kernel:
    # t1: 0.6 * exp(-1) = 0.2207276647...
    # t2: 0.4 * exp(-(2+1)) = 0.4 * exp(-3) = 0.019914827...
    # Total = 0.24064249...
    exp_mass = epk.compute_exponential_kernel([t1, t2], evaluator=lambda t: True)
    assert pytest.approx(0.24064249, rel=1e-5) == exp_mass

    # Filtering works on both
    filtered_rat = epk.compute_rational_kernel([t1, t2], evaluator=lambda t: t.trace_id == "gamma_1")
    assert filtered_rat == Fraction(3, 10)

    filtered_exp = epk.compute_exponential_kernel([t1, t2], evaluator=lambda t: t.trace_id == "gamma_1")
    assert pytest.approx(float(Fraction(6, 10)) * math.exp(-1), rel=1e-5) == filtered_exp


def test_epk_input_validation_rejects_negative_and_floats():
    # Negative cost
    with pytest.raises(ValueError):
        ProposalTrace(
            trace_id="g",
            input_claim="x",
            extracted_answer="y",
            proposal_probability=Fraction(1, 2),
            cost=Fraction(-1),
        )

    # Negative residual risk
    with pytest.raises(ValueError):
        ProposalTrace(
            trace_id="g",
            input_claim="x",
            extracted_answer="y",
            proposal_probability=Fraction(1, 2),
            residual_risk=Fraction(-1),
        )

    # Float rejection on exact rational fields
    with pytest.raises(TypeError):
        ProposalTrace(
            trace_id="g",
            input_claim="x",
            extracted_answer="y",
            proposal_probability=0.5,  # type: ignore[arg-type]
        )

    # Negative sensitivities
    with pytest.raises(ValueError):
        EvaluatedPathKernel(cost_sensitivity=Fraction(-1))
    with pytest.raises(ValueError):
        EvaluatedPathKernel(risk_sensitivity=Fraction(-1))


def test_gate_stack_schema_and_boolean_enforcement():
    all_passing = GateStack(
        c1_proposal_generated=True,
        c2_parseable_output=True,
        c3_canonicalization_succeeds=True,
        c4_verifier_accepts=True,
        c5_unique_answer_fiber=True,
        c6_replay_confirms=True,
        c7_leakage_provenance_clean=True,
        c8_terminal_gate_accepts=True,
    )
    passed, reason = all_passing.evaluate()
    assert passed is True
    assert reason is None

    # Test each gate failure mapping
    failing_c3 = GateStack(True, True, False, True, True, True, True, True)
    assert failing_c3.evaluate() == (False, RefusalReason.CANONICALIZER_FAILURE)

    failing_c5 = GateStack(True, True, True, True, False, True, True, True)
    assert failing_c5.evaluate() == (False, RefusalReason.AMBIGUOUS_ANSWER_FIBER)

    failing_c7 = GateStack(True, True, True, True, True, True, False, True)
    assert failing_c7.evaluate() == (False, RefusalReason.LEAKAGE_DETECTED)

    # String truthiness rejection: GateStack(*['False']*8) MUST raise TypeError
    with pytest.raises(TypeError):
        GateStack(*["False"] * 8)  # type: ignore[arg-type]


def test_halting_does_not_imply_authority_and_checklist_scoping():
    trace = ProposalTrace(
        trace_id="turing_halt_01",
        input_claim="TM_INPUT",
        extracted_answer="TM_OUTPUT",
        proposal_probability=Fraction(1),
        is_halted=True,
    )

    valid_gates = GateStack(
        c1_proposal_generated=True,
        c2_parseable_output=True,
        c3_canonicalization_succeeds=True,
        c4_verifier_accepts=True,
        c5_unique_answer_fiber=True,
        c6_replay_confirms=True,
        c7_leakage_provenance_clean=True,
        c8_terminal_gate_accepts=True,
    )

    # 1. Halting without gates -> NON_AUTHORITY_HALT
    outcome_no_gates = evaluate_halted_trace(trace, gates=None)
    assert outcome_no_gates.status == TerminalStatus.NON_AUTHORITY_HALT
    assert outcome_no_gates.refusal_reason == RefusalReason.NON_AUTHORITY_TERMINAL

    # 2. Halting with passing gates but NO terminal witness -> CHECKLIST_CERTIFIED (not AUTHORITY!)
    outcome_checklist = evaluate_halted_trace(trace, gates=valid_gates, terminal_witness=None)
    assert outcome_checklist.status == TerminalStatus.CHECKLIST_CERTIFIED
    assert "sufficiency to operational authority is refused" in outcome_checklist.details

    # 3. Halting with passing gates AND verified terminal witness -> AUTHORITY
    auth_witness = TerminalWitness(
        terminal_id="term_01",
        is_auth_proof="proof_is_auth_turing_01",
        verified_answer="TM_OUTPUT",
    )
    outcome_auth = evaluate_halted_trace(trace, gates=valid_gates, terminal_witness=auth_witness)
    assert outcome_auth.status == TerminalStatus.AUTHORITY

    # 4. Terminal witness answer mismatch -> REFUSAL (TERMINAL_MISMATCH)
    mismatched_witness = TerminalWitness(
        terminal_id="term_01",
        is_auth_proof="proof_is_auth_turing_01",
        verified_answer="DIFFERENT_ANSWER",
    )
    outcome_mismatch = evaluate_halted_trace(trace, gates=valid_gates, terminal_witness=mismatched_witness)
    assert outcome_mismatch.status == TerminalStatus.REFUSAL
    assert outcome_mismatch.refusal_reason == RefusalReason.TERMINAL_MISMATCH

    # 5. Un-halted trace -> PROPOSAL_ONLY
    unhalted = ProposalTrace(
        trace_id="running_01",
        input_claim="x",
        extracted_answer="y",
        proposal_probability=Fraction(1, 2),
        is_halted=False,
    )
    assert evaluate_halted_trace(unhalted, gates=valid_gates).status == TerminalStatus.PROPOSAL_ONLY


def test_counterfeit_descent_detection_and_missing_evidence_safeguards():
    counterfeit_trace = ProposalTrace(
        trace_id="llm_fake_cert",
        input_claim="Prove Theorem X",
        extracted_answer="Verified by Q.E.D.",
        proposal_probability=Fraction(99, 100),
        surface_signs={"has_citations": True, "has_json_tags": True, "claims_confidence": True},
    )

    # 1. Non-zero residual defect mass with surface signs -> COUNTERFEIT_PACKET
    is_counterfeit, outcome = detect_counterfeit_descent(
        trace=counterfeit_trace,
        residual_defect_mass=Fraction(1, 10),
    )
    assert is_counterfeit is True
    assert outcome.status == TerminalStatus.REFUSAL
    assert outcome.refusal_reason == RefusalReason.COUNTERFEIT_PACKET

    # 2. Non-zero residual defect mass without surface signs -> VERIFIER_REJECTED
    plain_trace = ProposalTrace(
        trace_id="plain",
        input_claim="x",
        extracted_answer="y",
        proposal_probability=Fraction(1),
        surface_signs={},
    )
    is_counterfeit, outcome = detect_counterfeit_descent(
        trace=plain_trace,
        residual_defect_mass=Fraction(1, 10),
    )
    assert is_counterfeit is False
    assert outcome.status == TerminalStatus.REFUSAL
    assert outcome.refusal_reason == RefusalReason.VERIFIER_REJECTED

    # 3. Reviewer probe: detect_counterfeit_descent(trace, 0) without gates must NOT return AUTHORITY!
    unhalted_bad = ProposalTrace(
        trace_id="bad_unhalted",
        input_claim="compute 2+2",
        extracted_answer="5",  # Incorrect answer
        proposal_probability=Fraction(1),
        is_halted=False,       # Unhalted
    )
    _, outcome_unhalted = detect_counterfeit_descent(unhalted_bad, residual_defect_mass=Fraction(0))
    assert outcome_unhalted.status == TerminalStatus.PROPOSAL_ONLY

    # Halted trace with 0 residual but no gates -> NON_AUTHORITY_HALT (not AUTHORITY)
    halted_plain = ProposalTrace(
        trace_id="halted_plain",
        input_claim="compute 2+2",
        extracted_answer="4",
        proposal_probability=Fraction(1),
        is_halted=True,
    )
    _, outcome_no_gates = detect_counterfeit_descent(halted_plain, residual_defect_mass=Fraction(0), gates=None)
    assert outcome_no_gates.status == TerminalStatus.NON_AUTHORITY_HALT

    # 4. Halted trace with 0 residual and passing gates, but NO witness -> CHECKLIST_CERTIFIED (not AUTHORITY)
    all_passing = GateStack(True, True, True, True, True, True, True, True)
    _, outcome_checklist = detect_counterfeit_descent(
        halted_plain,
        residual_defect_mass=Fraction(0),
        gates=all_passing,
        terminal_witness=None,
    )
    assert outcome_checklist.status == TerminalStatus.CHECKLIST_CERTIFIED

    # 5. Halted trace with 0 residual, passing gates, AND verified witness -> AUTHORITY
    valid_witness = TerminalWitness("t_2plus2", "proof_arith_4", "4")
    _, outcome_auth = detect_counterfeit_descent(
        halted_plain,
        residual_defect_mass=Fraction(0),
        gates=all_passing,
        terminal_witness=valid_witness,
    )
    assert outcome_auth.status == TerminalStatus.AUTHORITY


def test_lggr_quotient_obstruction_exhaustive_carrier_and_counterexample():
    # 1. Standard valid LGGR setup on carrier:
    carrier_valid = ["state_0", "state_1"]
    zero_rel = lambda x, y: (x, y) in [("state_0", "state_1"), ("state_1", "state_0"), ("state_0", "state_0"), ("state_1", "state_1")]
    local_dashboard = lambda s: "GREEN"
    global_verdict = lambda s: "PASS" if s == "state_0" else "FAIL"

    lggr_valid = LGGRObstruction(
        zero_relation=zero_rel,
        local_dashboard=local_dashboard,
        global_verdict=global_verdict,
        carrier=carrier_valid,
    )
    assert lggr_valid.check_local_factorization() is True
    assert lggr_valid.check_joint_factorization() is False
    assert lggr_valid.verify_lggr_obstruction() is True

    # 2. Reviewer probe: three mutually equivalent states with local GREEN, GREEN, RED
    # Carrier = [s0, s1, s2]
    # zero_rel: all three are mutually equivalent (single class)
    # L(s0)=GREEN, L(s1)=GREEN, L(s2)=RED
    # G(s0)=PASS, G(s1)=FAIL, G(s2)=PASS
    carrier_probe = ["s0", "s1", "s2"]
    probe_zero_rel = lambda x, y: True  # All three are in the same class
    probe_local = lambda s: "RED" if s == "s2" else "GREEN"
    probe_global = lambda s: "FAIL" if s == "s1" else "PASS"

    lggr_probe = LGGRObstruction(
        zero_relation=probe_zero_rel,
        local_dashboard=probe_local,
        global_verdict=probe_global,
        carrier=carrier_probe,
    )

    # Local dashboard FAILS to factor on the class {s0, s1, s2} because L(s0) != L(s2)
    assert lggr_probe.check_local_factorization() is False
    # LGGR obstruction MUST be False (Local Green is rejected!)
    assert lggr_probe.verify_lggr_obstruction() is False


def test_minimal_verdict_refinement_derivation():
    # Carrier X = {x0, x1, x2, x3, x4}
    carrier = ["x0", "x1", "x2", "x3", "x4"]

    # Initial quotient map q partitions into 2 classes:
    # q(x0) = q(x1) = q(x2) = "Q0"
    # q(x3) = q(x4) = "Q1"
    quotient_map = lambda s: "Q0" if s in ["x0", "x1", "x2"] else "Q1"

    # Global verdict map G:
    # On Q0: G(x0)="PASS", G(x1)="FAIL", G(x2)="PASS" (2 distinct verdicts: split!)
    # On Q1: G(x3)="OK", G(x4)="OK" (1 distinct verdict: no split)
    def verdict_map(s: str) -> str:
        if s == "x0":
            return "PASS"
        if s == "x1":
            return "FAIL"
        if s == "x2":
            return "PASS"
        return "OK"

    result = compute_minimal_verdict_refinement(carrier, quotient_map, verdict_map)

    assert result.carrier_size == 5
    assert result.original_quotient_size == 2
    # Q0 splits into 2 classes ({x0, x2} and {x1}); Q1 remains 1 class ({x3, x4})
    # Refined quotient size = 3
    assert result.refined_quotient_size == 3
    # Class increase = sum_{u in Q} (|G(q^{-1}(u))| - 1) = (2 - 1) + (1 - 1) = 1
    assert result.class_increase == 1

    # Check split witness
    assert len(result.splits) == 1
    witness = result.splits[0]
    assert witness.quotient_class == "Q0"
    assert witness.state_a in ["x0", "x2"]
    assert witness.state_b == "x1"
    assert witness.verdict_a != witness.verdict_b
