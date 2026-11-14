"""Unit tests for The Authority Firewall and Verification Limits reference implementation."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_verification_limits_core import (
    AuthorityCapability,
    AuthorityWitness,
    CapabilityViolationError,
    DiscreteResidual,
    FinitePartitionCoverage,
    RuntimeResult,
    SixAxisEvidenceLattice,
    SovereignDescentVerifier,
    StructuralVerificationGate,
    TerminalVerdict,
    create_canonical_calibration_record,
    run_master_demo_scenarios,
)


def _sound_detector(r: DiscreteResidual) -> bool:
    return r.is_exact_zero


def _collapsing_detector(r: DiscreteResidual) -> bool:
    return True


def test_exact_rational_obstruction_properties():
    """Validates exact rational arithmetic and L1 norm calculations."""
    zero_res = DiscreteResidual.from_ints(0, 0, 0)
    assert zero_res.norm1 == Fraction(0, 1)
    assert zero_res.is_exact_zero is True

    frac_res = DiscreteResidual.from_fractions((1, 2), (-1, 3), (1, 6))
    # 1/2 + 1/3 + 1/6 = 3/6 + 2/6 + 1/6 = 1
    assert frac_res.norm1 == Fraction(1, 1)
    assert frac_res.is_exact_zero is False


def test_minimum_calibration_record_execution():
    """Validates calibration case execution against sound vs collapsing detectors."""
    record = create_canonical_calibration_record()

    # Sound detector: evaluates whether discrete residual is exact zero
    eval_sound = record.execute_calibration(_sound_detector)
    assert eval_sound.passed is True
    assert eval_sound.evaluated_cases == 4
    assert len(eval_sound.failures) == 0

    # Collapsing detector: maps all inputs to pass (false-green hazard)
    eval_collapsing = record.execute_calibration(_collapsing_detector)
    assert eval_collapsing.passed is False
    assert len(eval_collapsing.failures) >= 2  # Fails negative case and collapses collision pair

    gate = StructuralVerificationGate()
    result = RuntimeResult(
        result_id="RES_01",
        output_data="Candidate passes detector",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )

    # 1. No calibration record -> DetectorInadequate
    verdict_no_record = gate.evaluate_result(result, calibration_record=None)
    assert verdict_no_record == TerminalVerdict.DETECTOR_INADEQUATE

    # 2. Gating with collapsing detector fails calibration -> DetectorInadequate
    verdict_collapsing = gate.evaluate_result(
        result,
        calibration_record=record,
        detector=_collapsing_detector,
    )
    assert verdict_collapsing == TerminalVerdict.DETECTOR_INADEQUATE


def test_fabricated_witness_rejection():
    """Reproduces the peer review attack: verifies that invented evidence is strictly refused."""
    gate = StructuralVerificationGate()
    record = create_canonical_calibration_record()

    result = RuntimeResult(
        result_id="RES_TEST",
        output_data="Arbitrary output",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )

    # 1. Direct construction of AuthorityWitness by untrusted code fails immediately
    with pytest.raises(CapabilityViolationError, match="AuthorityWitness cannot be instantiated directly"):
        AuthorityWitness(
            verifier_id="invented",
            result_id="RES_TEST",
            content_hash="not-a-hash",
            signature="not-a-valid-sig",
            _token=None,  # type: ignore
        )

    # 2. Even if forged witness with invalid token somehow bypasses construction, gate refuses
    class _DummyForgedWitness:
        verifier_id = "invented"
        result_id = "RES_TEST"
        content_hash = "not-a-hash"
        signature = "not-a-valid-sig"
        _token = object()

        def is_valid_signature(self, secret: str) -> bool:
            return True

    verdict_dummy = gate.evaluate_result(
        result,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=_DummyForgedWitness(),  # type: ignore
    )
    assert verdict_dummy != TerminalVerdict.AUTHORITY_CERTIFIED
    assert verdict_dummy == TerminalVerdict.REFUSAL_DEFECT


def test_witness_forgery_defenses_and_object_bypass():
    """Directly addresses peer review P1: object(), empty, or unbound witnesses are strictly refused."""
    gate = StructuralVerificationGate()
    gate.register_verifier("SOV_01", "secret_key_123")
    record = create_canonical_calibration_record()

    valid_result = RuntimeResult(
        result_id="RES_VALID",
        output_data="Legitimate result",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )

    # P1 Exploits addressed:
    # Exploit A: passing object() as the witness MUST NOT return AuthorityCertified
    verdict_object = gate.evaluate_result(
        valid_result,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=object(),  # type: ignore
    )
    assert verdict_object == TerminalVerdict.REFUSAL_DEFECT

    # Exploit B: empty witness / missing fields
    class _EmptyWitness:
        verifier_id = ""
        result_id = ""
        content_hash = ""
        signature = ""
        _token = None

    verdict_empty = gate.evaluate_result(
        valid_result,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=_EmptyWitness(),  # type: ignore
    )
    assert verdict_empty == TerminalVerdict.REFUSAL_DEFECT

    # Exploit C: witness issued for result with non-zero residual
    verifier = SovereignDescentVerifier("SOV_01", "secret_key_123")
    unresolved_result = RuntimeResult(
        result_id="RES_UNRESOLVED",
        output_data="Unresolved defect",
        residual=DiscreteResidual.from_ints(1, 0, 0),
        is_halted=True,
        detector_passed=True,
    )
    # Verifier refuses to issue witness for non-zero residual
    with pytest.raises(ValueError, match="cannot issue witness for unresolved residual"):
        verifier.verify_and_issue_witness(unresolved_result)


def test_unbound_and_tampered_witness_rejection():
    """Validates that a witness bound to another result or tampered data is rejected."""
    secret = "sovereign_secret_key_123"
    verifier = SovereignDescentVerifier(verifier_id="SOV_01", secret_key=secret)

    gate = StructuralVerificationGate()
    gate.register_verifier("SOV_01", secret)
    record = create_canonical_calibration_record()

    res_a = RuntimeResult(
        result_id="RES_A",
        output_data="Data A",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )
    res_b = RuntimeResult(
        result_id="RES_B",
        output_data="Data B",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )

    witness_a = verifier.verify_and_issue_witness(res_a)

    # Case 1: Presenting witness A for result B (mismatched result_id)
    verdict_unbound = gate.evaluate_result(
        res_b,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=witness_a,
    )
    assert verdict_unbound == TerminalVerdict.REFUSAL_DEFECT

    # Case 2: Tampering with output data after witness generation
    tampered_a = RuntimeResult(
        result_id="RES_A",
        output_data="Tampered Data A",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )
    verdict_tampered = gate.evaluate_result(
        tampered_a,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=witness_a,
    )
    assert verdict_tampered == TerminalVerdict.REFUSAL_DEFECT


def test_genuine_sovereign_descent_witness_admission():
    """Validates that authentic sovereign descent witnesses are certified."""
    secret = "sovereign_secret_key_456"
    verifier = SovereignDescentVerifier(verifier_id="SOV_01", secret_key=secret)

    gate = StructuralVerificationGate()
    gate.register_verifier("SOV_01", secret)
    record = create_canonical_calibration_record()

    # Zero residual allows descent witness issuance
    valid_result = RuntimeResult(
        result_id="RES_VALID",
        output_data="Sound descent computation",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )
    witness = verifier.verify_and_issue_witness(valid_result)

    verdict = gate.evaluate_result(
        valid_result,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=witness,
    )
    assert verdict == TerminalVerdict.AUTHORITY_CERTIFIED

    # Non-zero residual forbids witness issuance
    defective_result = RuntimeResult(
        result_id="RES_DEFECTIVE",
        output_data="Unresolved residual",
        residual=DiscreteResidual.from_fractions((1, 2), (1, 2)),
        is_halted=True,
        detector_passed=True,
    )
    with pytest.raises(ValueError, match="cannot issue witness for unresolved residual"):
        verifier.verify_and_issue_witness(defective_result)


def test_capability_firewall_non_constructibility():
    """Validates capability protection boundaries: untrusted code cannot mint AuthorityCapability."""
    result = RuntimeResult(
        result_id="RESULT_DATA",
        output_data="Processed metrics",
        is_halted=True,
        detector_passed=True,
    )

    # 1. RuntimeResult cannot construct AuthorityCapability
    with pytest.raises(CapabilityViolationError, match="Capability Firewall: RuntimeResult"):
        result.to_authority_capability()

    # 2. Untrusted code cannot directly instantiate AuthorityCapability
    with pytest.raises(CapabilityViolationError, match="AuthorityCapability cannot be instantiated directly"):
        AuthorityCapability(
            grantee="UNTRUSTED",
            scope="ROOT",
            verifier_id="SOV_01",
            _token=None,  # type: ignore
        )

    # 3. Sovereign verifier mints capability only from verified witness
    verifier = SovereignDescentVerifier("SOV_01", "secret")
    valid_result = RuntimeResult(
        result_id="RES_OK",
        output_data="OK",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        detector_passed=True,
    )
    witness = verifier.verify_and_issue_witness(valid_result)
    cap = verifier.mint_capability(witness, scope="EXECUTE")
    assert cap.grantee == "RES_OK"
    assert cap.verifier_id == "SOV_01"


def test_fluent_halt_non_authority():
    """Syntactic halting and detector pass without descent witness yields FluentHaltNonAuthority."""
    gate = StructuralVerificationGate()
    record = create_canonical_calibration_record()

    result_no_witness = RuntimeResult(
        result_id="RES_FLUENT",
        output_data="Fluent text completion",
        residual=DiscreteResidual.from_ints(0, 0, 0),
        is_halted=True,
        detector_passed=True,
    )

    verdict = gate.evaluate_result(
        result_no_witness,
        calibration_record=record,
        detector=_sound_detector,
        authority_witness=None,
    )
    assert verdict == TerminalVerdict.FLUENT_HALT_NON_AUTHORITY


def test_six_axis_evidence_lattice_independence():
    """Cross-axis auto promotion is strictly forbidden."""
    lattice = SixAxisEvidenceLattice(
        mathematical=True,
        mechanization=True,
        implementation=False,
        empirical=False,
        security=False,
        authority=False,
    )

    # Green on math & lean does NOT promote implementation or authority
    assert lattice.can_auto_promote("mathematical", "authority") is False
    assert lattice.can_auto_promote("mechanization", "implementation") is False
    assert lattice.is_fully_verified() is False

    complete_lattice = SixAxisEvidenceLattice(
        mathematical=True,
        mechanization=True,
        implementation=True,
        empirical=True,
        security=True,
        authority=True,
    )
    assert complete_lattice.is_fully_verified() is True


def test_finite_calibration_completeness_and_sharp_coverage_bound():
    """Validates finite calibration completeness theorem and sharp partition coverage bound.
    
    Theorem: D = A on X <=> forall r in R, D(r) = A(r) when A and D are class-constant on X/~.
    Sharpness: omitting any equivalence class admits a class-constant counterexample detector.
    """
    # 1. Define finite carrier X with 3 partition classes under symmetry
    # Class 0: zero defects
    c0 = (DiscreteResidual.from_ints(0, 0),)
    # Class 1: unit defects (invariant under sign flip)
    c1 = (DiscreteResidual.from_ints(1, 0), DiscreteResidual.from_ints(-1, 0))
    # Class 2: two-unit defects
    c2 = (DiscreteResidual.from_ints(1, 1), DiscreteResidual.from_ints(-1, -1))

    partition = FinitePartitionCoverage(classes=(c0, c1, c2))
    assert len(partition.carrier) == 5

    # Ground truth specification A: accepts zero defect only
    def spec_A(r: DiscreteResidual) -> bool:
        return r.is_exact_zero

    # Verified class-constant
    assert partition.is_class_constant(spec_A) is True

    # Sound detector D: also accepts zero defect only
    def detector_D(r: DiscreteResidual) -> bool:
        return r.norm1 == 0

    assert partition.is_class_constant(detector_D) is True

    # Complete representative set R: one representative from each of the 3 classes
    R_complete = (
        DiscreteResidual.from_ints(0, 0),
        DiscreteResidual.from_ints(1, 0),
        DiscreteResidual.from_ints(1, 1),
    )

    # Theorem holds: complete coverage proves D = A on carrier X
    ok, err = partition.verify_coverage(spec_A, detector_D, R_complete)
    assert ok is True
    assert err is None

    # Incomplete representative set R_incomplete: omits Class 2
    R_incomplete = (
        DiscreteResidual.from_ints(0, 0),
        DiscreteResidual.from_ints(1, 0),
    )
    ok_incomp, err_incomp = partition.verify_coverage(spec_A, detector_D, R_incomplete)
    assert ok_incomp is False
    assert "Coverage incomplete" in str(err_incomp)

    # Sharpness: construct class-constant counterexample detector
    omitted_witness, counter_detector = partition.construct_omitted_class_counterexample(
        spec_A, R_incomplete
    )
    assert omitted_witness in c2
    assert partition.is_class_constant(counter_detector) is True

    # Agrees on all tested representatives in R_incomplete
    for r in R_incomplete:
        assert counter_detector(r) == spec_A(r)

    # Disagrees on the omitted witness!
    assert counter_detector(omitted_witness) != spec_A(omitted_witness)


def test_master_demo_seven_scenarios():
    """Validates the complete seven-scenario (plus baseline) master demo suite."""
    results = run_master_demo_scenarios()
    assert len(results) == 8

    # All scenarios evaluate to their declared fail-closed or certified verdicts
    for r in results:
        assert r.passed is True, f"Master demo scenario {r.scenario_id} failed: expected {r.expected_verdict}, got {r.actual_verdict}"

    scenarios_by_id = {r.scenario_id: r for r in results}
    assert scenarios_by_id["C1"].actual_verdict == TerminalVerdict.FLUENT_HALT_NON_AUTHORITY
    assert scenarios_by_id["O1"].actual_verdict == TerminalVerdict.DETECTOR_INADEQUATE
    assert scenarios_by_id["O2"].actual_verdict == TerminalVerdict.REFUSAL_DEFECT
    assert scenarios_by_id["O3"].actual_verdict == TerminalVerdict.REFUSAL_DEFECT
    assert scenarios_by_id["O4"].actual_verdict == TerminalVerdict.DETECTOR_INADEQUATE
    assert scenarios_by_id["O5"].actual_verdict == TerminalVerdict.REFUSAL_DEFECT
    assert scenarios_by_id["O6"].actual_verdict == TerminalVerdict.REFUSAL_DEFECT
    assert scenarios_by_id["O7"].actual_verdict == TerminalVerdict.AUTHORITY_CERTIFIED
