"""Invasive Mutation and Break-and-Recover Injection Test Suite for Paper 012.

Implements break-and-recover assertions across all 8 mutation fault modes:
1. Vacuous / Degenerate Evaluator Injections (DetectorAdequacyGuard warnings & exceptions)
2. Boundary-Slice Decomposition Non-Uniqueness (Condition G1 violations & recovery)
3. Sign-Balance Cancellation Stress Tests (E[Delta_E] = 0 with EGD = 1.0 masking)
4. Random Path Permutation Invariants & Reversal Breaks
5. Corrupted Probability Distributions & Non-Binary Verdicts
6. Negative Actions, Costs, and Risks
7. MoE Weight Mutations & Threshold Boundary Invasions
8. Metric Identity Tampering & Independent Verification Recovery

Target: 100% robust break-and-recover verification of error gates and mathematical boundaries.
AuthorityEffect: None.
Anchoring: sealed-derivation-v1 (3100c4e).
"""

from __future__ import annotations

import random
import pytest

from epk_core import (
    BoundarySlice,
    ComposedTrajectory,
    DetectorAdequacyGuard,
    DetectorAdequacyStatus,
    EPKMetrics,
    EvaluatorVerdictTriple,
    MetricReport,
    ReliabilityModels,
    State,
    TrajectorySegment,
    make_five_trace_phone_test,
)


class TestVacuousAndDegenerateEvaluatorInjections:
    """Fault Mode 1: Degenerate / Vacuous Evaluator Injections and DetectorAdequacyGuard."""

    def test_vacuous_local_evaluator_break_and_recovery(self):
        """
        Break: Adversary provides evaluators where local stages trivially pass every trace
        (E_1 = 1, E_2 = 1 identically).
        DetectorAdequacyGuard flags VACUOUS_LOCAL.
        Recovery: Introduce genuine failing local traces; guard confirms no listed degeneracy observed.
        """
        # Break: All local pass identically
        vacuous_traces = [
            EvaluatorVerdictTriple(e1=1, e2=1, eg=1),
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),  # NGD failure
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
        ]
        flags_broken = DetectorAdequacyGuard.audit(vacuous_traces)
        assert DetectorAdequacyStatus.VACUOUS_LOCAL in flags_broken
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED not in flags_broken

        # Recovery: Add traces with genuine local rejections
        recovered_traces = vacuous_traces + [
            EvaluatorVerdictTriple(e1=0, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=1, e2=0, eg=0),
        ]
        flags_recovered = DetectorAdequacyGuard.audit(recovered_traces)
        assert DetectorAdequacyStatus.VACUOUS_LOCAL not in flags_recovered
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED in flags_recovered

    def test_all_rejecting_evaluator_break_and_recovery(self):
        """
        Break: Evaluator is dead / always-rejecting (E_1 = 0 on all traces).
        DetectorAdequacyGuard flags ALL_REJECTING.
        Recovery: Replace with active evaluator having passing instances.
        """
        dead_traces = [
            EvaluatorVerdictTriple(e1=0, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=0, e2=0, eg=0),
        ]
        flags_broken = DetectorAdequacyGuard.audit(dead_traces)
        assert DetectorAdequacyStatus.ALL_REJECTING in flags_broken

        # Recovery: Active traces included
        recovered_traces = dead_traces + [
            EvaluatorVerdictTriple(e1=1, e2=1, eg=1),
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
        ]
        flags_recovered = DetectorAdequacyGuard.audit(recovered_traces)
        assert DetectorAdequacyStatus.ALL_REJECTING not in flags_recovered

    def test_tautological_coupling_break_and_recovery(self):
        """
        Break: Evaluator artificially defines E_g := E_1 * E_2 across all traces
        without measuring true integration behavior (Delta_E = 0 forced identically).
        DetectorAdequacyGuard flags TAUTOLOGICAL_COUPLING.
        Recovery: Inject empirical non-factoring traces exhibiting non-zero defect.
        """
        tautological_traces = [
            EvaluatorVerdictTriple(e1=1, e2=1, eg=1),
            EvaluatorVerdictTriple(e1=1, e2=0, eg=0),
            EvaluatorVerdictTriple(e1=0, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=0, e2=0, eg=0),
        ]
        flags_broken = DetectorAdequacyGuard.audit(tautological_traces)
        assert DetectorAdequacyStatus.TAUTOLOGICAL_COUPLING in flags_broken

        # Recovery: Inject a non-tautological integration failure (NGD)
        recovered_traces = tautological_traces + [
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
        ]
        flags_recovered = DetectorAdequacyGuard.audit(recovered_traces)
        assert DetectorAdequacyStatus.TAUTOLOGICAL_COUPLING not in flags_recovered
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED in flags_recovered

    def test_empty_sample_break_and_recovery(self):
        """
        Break: Empty trace set passed to metrics computation or adequacy guard.
        Recovery: Providing non-empty valid sample computes cleanly.
        """
        with pytest.raises(ValueError, match="empty trace set"):
            EPKMetrics.compute([])

        # Adequacy guard handles empty trace set by flagging ALL_REJECTING
        assert DetectorAdequacyGuard.audit([]) == [DetectorAdequacyStatus.ALL_REJECTING]

        # Recovery: Providing valid sample
        valid_sample = [EvaluatorVerdictTriple(1, 1, 1)]
        report = EPKMetrics.compute(valid_sample)
        assert report.sample_size == 1
        assert report.lpr == 1.0


class TestBoundarySliceDecompositionViolations:
    """Fault Mode 2: Boundary-Slice Decomposition Non-Uniqueness (Condition G1)."""

    def test_boundary_slice_condition_g1_break_and_recovery_by_slice_expansion(self):
        """
        Break: Trajectories leak through an unmonitored intermediate boundary state.
        BoundarySlice.validate_unique_decomposition detects the violation.
        Recovery: Expand the declared boundary slice B to include the leaking state.
        """
        s0 = State("S_start")
        s_b1 = State("S_boundary_1")
        s_leak = State("S_unmonitored_leak")
        s_end = State("S_terminal")

        # Declared slice only knows about s_b1
        b_slice = BoundarySlice(states={s_b1})

        # Path 1: legitimate decomposition through s_b1
        traj_legit = ComposedTrajectory(
            TrajectorySegment(s0, s_b1, ("step1",)),
            TrajectorySegment(s_b1, s_end, ("step2",)),
        )
        # Path 2: leaked decomposition through unmodeled intermediate state
        traj_leaked = ComposedTrajectory(
            TrajectorySegment(s0, s_leak, ("step1_alt",)),
            TrajectorySegment(s_leak, s_end, ("step2_alt",)),
        )

        # Break: Slice validation fails on leaked trajectory
        is_valid, violations = b_slice.validate_unique_decomposition([traj_legit, traj_leaked])
        assert not is_valid
        assert len(violations) == 1
        assert "S_unmonitored_leak" in violations[0]

        # Recovery Method 1: Expand boundary slice B to cover the leak
        b_slice_expanded = BoundarySlice(states={s_b1, s_leak})
        is_valid_rec, violations_rec = b_slice_expanded.validate_unique_decomposition(
            [traj_legit, traj_leaked]
        )
        assert is_valid_rec
        assert len(violations_rec) == 0

    def test_boundary_slice_break_and_recovery_by_path_filtering(self):
        """
        Break: System receives heterogeneous paths, some of which do not pass through B.
        Recovery: Filter the trajectory ensemble to only include paths passing through B.
        """
        s0 = State("S0")
        s_b = State("S_b")
        s_other = State("S_other")
        s_end = State("S1")
        bslice = BoundarySlice(states={s_b})

        t_good = ComposedTrajectory(
            TrajectorySegment(s0, s_b, ("a",)),
            TrajectorySegment(s_b, s_end, ("b",)),
        )
        t_bad = ComposedTrajectory(
            TrajectorySegment(s0, s_other, ("a",)),
            TrajectorySegment(s_other, s_end, ("b",)),
        )

        # Break
        assert not bslice.validate_unique_decomposition([t_good, t_bad])[0]

        # Recovery Method 2: Filter to admissible boundary paths
        filtered_trajectories = [t for t in [t_good, t_bad] if bslice.contains(t.intermediate_state)]
        is_valid, violations = bslice.validate_unique_decomposition(filtered_trajectories)
        assert is_valid
        assert len(filtered_trajectories) == 1
        assert violations == []


class TestSignBalanceCancellationMasking:
    """Fault Mode 3: Sign-Balance Cancellation Stress Tests (E[Delta_E] = 0 with EGD = 1.0)."""

    def test_cancellation_masking_break_and_unmasking_recovery(self):
        """
        Break: An adversary constructs a pipeline where local-safety failures (NGD)
        are perfectly cancelled in expectation by accidental rescues (PGD).
        The net pass rates GPR and LPR are identical (GPR - LPR = 0), hiding the defect!
        Diagnostic Break Catch: EGD = NGD + PGD = 1.0 (100% of paths are defective!)
        Recovery: Decouple signed mean Delta_E from absolute defect mass EGD to expose the hazard.
        """
        # 10 traces total: 5 pure NGD (Delta_E = -1) and 5 pure PGD (Delta_E = +1)
        adversarial_sample = [
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),  # NGD: Local Green, Global Red
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
            EvaluatorVerdictTriple(e1=0, e2=1, eg=1),  # PGD: Local Red, Global Green
            EvaluatorVerdictTriple(e1=1, e2=0, eg=1),
            EvaluatorVerdictTriple(e1=0, e2=0, eg=1),
            EvaluatorVerdictTriple(e1=0, e2=1, eg=1),
            EvaluatorVerdictTriple(e1=1, e2=0, eg=1),
        ]
        report = EPKMetrics.compute(adversarial_sample)

        # Break Demonstration: Superficially, pass rate difference is zero!
        assert report.lpr == 0.50
        assert report.gpr == 0.50
        assert pytest.approx(report.mean_delta_e) == 0.0
        assert report.delta_sum == 0

        # The mathematical identities still strictly hold
        assert pytest.approx(report.gpr - report.lpr) == report.mean_delta_e

        # Diagnostic Catch: The system catches 100% composition breakdown via EGD
        assert report.ngd_all == 0.50
        assert report.pgd == 0.50
        assert report.zdr == 0.00
        assert report.egd == 1.00  # Every single trace suffered an evaluator gluing defect!

        # Recovery / Unmasking: The system inspects EGD and isolates the NGD safety failures
        assert report.egd > 0.0  # Proves composition is NOT factored despite mean_delta_e == 0
        ngd_failures = [t for t in adversarial_sample if t.is_ngd]
        assert len(ngd_failures) == 5


class TestRandomPathPermutationInvariants:
    """Fault Mode 4: Random Path Permutation Invariants & Reversal Breaks."""

    def test_permutation_invariance_across_random_shuffles(self):
        """
        Verifies that EPK metrics, count balances, and metric identities are
        strictly invariant under arbitrary permutations of the trace order.
        """
        rng = random.Random(42)
        base_sample = (
            [EvaluatorVerdictTriple(1, 1, 0)] * 7  # NGD
            + [EvaluatorVerdictTriple(0, 1, 1)] * 3  # PGD
            + [EvaluatorVerdictTriple(1, 1, 1)] * 10  # ZDR pass
            + [EvaluatorVerdictTriple(0, 0, 0)] * 5   # ZDR fail
        )
        base_report = EPKMetrics.compute(base_sample)

        for trial in range(10):
            shuffled = list(base_sample)
            rng.shuffle(shuffled)
            perm_report = EPKMetrics.compute(shuffled)

            # Assert complete numerical and structural identity
            assert perm_report.sample_size == base_report.sample_size
            assert perm_report.local_pass_count == base_report.local_pass_count
            assert perm_report.global_pass_count == base_report.global_pass_count
            assert perm_report.delta_sum == base_report.delta_sum
            assert perm_report.ngd_count == base_report.ngd_count
            assert perm_report.pgd_count == base_report.pgd_count
            assert perm_report.zdr_count == base_report.zdr_count

            assert pytest.approx(perm_report.lpr, abs=1e-15) == base_report.lpr
            assert pytest.approx(perm_report.gpr, abs=1e-15) == base_report.gpr
            assert pytest.approx(perm_report.mean_delta_e, abs=1e-15) == base_report.mean_delta_e
            assert pytest.approx(perm_report.ngd_all, abs=1e-15) == base_report.ngd_all
            assert pytest.approx(perm_report.pgd, abs=1e-15) == base_report.pgd
            assert pytest.approx(perm_report.zdr, abs=1e-15) == base_report.zdr
            assert pytest.approx(perm_report.egd, abs=1e-15) == base_report.egd

    def test_trajectory_segment_order_reversal_break_and_recovery(self):
        """
        Break: Reversing segment order (gamma_1 after gamma_2) breaks boundary matching
        whenever start and end states are distinct (S_start != S_terminal).
        Recovery: Compose in correct forward order.
        """
        s_start = State("S_alpha")
        s_mid = State("S_beta")
        s_end = State("S_gamma")

        seg1 = TrajectorySegment(s_start, s_mid, ("act1",))
        seg2 = TrajectorySegment(s_mid, s_end, ("act2",))

        # Valid composition: seg1 then seg2
        comp_valid = ComposedTrajectory(seg1, seg2)
        assert comp_valid.start_state == s_start
        assert comp_valid.end_state == s_end

        # Break: Attempt reversed composition (seg2 then seg1)
        with pytest.raises(ValueError, match="Boundary state mismatch"):
            ComposedTrajectory(seg2, seg1)


class TestCorruptedProbabilityAndVerdicts:
    """Fault Mode 5: Corrupted Probability Distributions & Non-Binary Verdicts."""

    def test_corrupt_non_binary_verdict_break_and_recovery(self):
        """
        Break: Inject non-binary values into EvaluatorVerdictTriple.
        Recovery: Map or threshold values into {0, 1}.
        """
        with pytest.raises(ValueError, match="Verdicts must be binary in \\{0, 1\\}"):
            EvaluatorVerdictTriple(e1=2, e2=1, eg=1)

        with pytest.raises(ValueError, match="Verdicts must be binary in \\{0, 1\\}"):
            EvaluatorVerdictTriple(e1=1, e2=-1, eg=0)

        with pytest.raises(ValueError, match="Verdicts must be binary in \\{0, 1\\}"):
            EvaluatorVerdictTriple(e1=1, e2=1, eg=99)

        # Recovery: Binary verdicts succeed
        recovered = EvaluatorVerdictTriple(e1=1, e2=1, eg=0)
        assert recovered.delta_eval == -1

    def test_corrupt_proposal_probability_break_and_recovery(self):
        """
        Break: Inject invalid proposal probability (p <= 0 or p > 1) into TrajectorySegment.
        Recovery: Normalize/clamp probability to (0, 1].
        """
        s0 = State("S0")
        s1 = State("S1")

        for bad_p in (0.0, -0.5, 1.0001, 10.0):
            with pytest.raises(ValueError, match="Proposal probability must be in \\(0, 1\\]"):
                TrajectorySegment(s0, s1, ("act",), proposal_prob=bad_p)

        # Recovery: Valid probability
        seg_rec = TrajectorySegment(s0, s1, ("act",), proposal_prob=0.95)
        assert seg_rec.proposal_prob == 0.95


class TestNegativeActionsCostsAndRisks:
    """Fault Mode 6: Negative Costs, Risks, and Raw Actions."""

    def test_negative_cost_break_and_recovery(self):
        """
        Break: Inject negative path cost into TrajectorySegment.
        Recovery: Correct to non-negative cost.
        """
        s0 = State("S0")
        s1 = State("S1")
        with pytest.raises(ValueError, match="Cost must be non-negative"):
            TrajectorySegment(s0, s1, ("act",), cost=-2.0)

        # Recovery
        valid_seg = TrajectorySegment(s0, s1, ("act",), cost=0.0)
        assert valid_seg.cost == 0.0

    def test_negative_risk_break_and_recovery(self):
        """
        Break: Inject negative path risk into TrajectorySegment.
        Recovery: Correct to non-negative risk.
        """
        s0 = State("S0")
        s1 = State("S1")
        with pytest.raises(ValueError, match="Risk must be non-negative"):
            TrajectorySegment(s0, s1, ("act",), risk=-0.01)

        # Recovery
        valid_seg = TrajectorySegment(s0, s1, ("act",), risk=0.5)
        assert valid_seg.risk == 0.5


class TestMoEWeightMutationsAndThresholdBoundaries:
    """Fault Mode 7: MoE Weight Mutations & Threshold Boundary Invasions."""

    def test_moe_weight_length_mismatch_break_and_recovery(self):
        """
        Break: Mixture-of-Experts called with mismatched verdicts and weights lengths.
        Recovery: Provide matching length weights.
        """
        with pytest.raises(ValueError, match="matching lengths"):
            ReliabilityModels.mixture_of_experts_pass([1, 1, 0], [0.5, 0.5])

        # Recovery
        assert ReliabilityModels.mixture_of_experts_pass([1, 1, 0], [0.5, 0.25, 0.25]) == 1

    def test_moe_threshold_exact_boundary_transitions(self):
        """
        Break & Recovery: Test step function at the exact threshold boundary.
        Weighted score = 0.5.
        threshold = 0.5000000 -> 1 (pass)
        threshold = 0.5000001 -> 0 (break/fail)
        """
        verdicts = [1, 0]
        weights = [1.0, 1.0]  # weighted average score = 1.0 / 2.0 = 0.5

        # At boundary: passes
        assert ReliabilityModels.mixture_of_experts_pass(verdicts, weights, threshold=0.5) == 1

        # Infinitesimally above boundary: fails
        assert ReliabilityModels.mixture_of_experts_pass(verdicts, weights, threshold=0.5000001) == 0

        # Recovery by increasing weight of passing expert
        recovered_weights = [1.01, 1.0]
        assert ReliabilityModels.mixture_of_experts_pass(verdicts, recovered_weights, threshold=0.5000001) == 1

    def test_moe_all_zero_weights_safe_handling(self):
        """
        Invasive injection: All weights are zero.
        Verifies zero-division guard (w_sum > 0 else 1.0).
        """
        assert ReliabilityModels.mixture_of_experts_pass([1, 1], [0.0, 0.0], threshold=0.5) == 0


class TestMetricIdentityTampering:
    """Fault Mode 8: Metric Identity Tampering & Independent Verification Recovery."""

    def test_tampered_gpr_lpr_mean_delta_break_and_recovery(self):
        """
        Break: Tamper with GPR - LPR = mean(Delta_E).
        Recovery: Restore accurate mean_delta_e from sample.
        """
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Break: Tamper mean_delta_e
        corrupted = MetricReport(
            sample_size=report.sample_size,
            lpr=report.lpr,
            gpr=report.gpr,
            mean_delta_e=0.999,  # Corrupted!
            ngd_all=report.ngd_all,
            ngd_cond=report.ngd_cond,
            pgd=report.pgd,
            zdr=report.zdr,
            egd=report.egd,
            ngd_count=report.ngd_count,
            pgd_count=report.pgd_count,
            zdr_count=report.zdr_count,
            local_pass_count=report.local_pass_count,
            global_pass_count=report.global_pass_count,
            delta_sum=report.delta_sum,
        )
        with pytest.raises(AssertionError, match="Identity GPR - LPR = mean"):
            EPKMetrics.verify_identities(corrupted)

        # Recovery: Recompute authentic mean_delta_e
        corrupted.mean_delta_e = report.mean_delta_e
        EPKMetrics.verify_identities(corrupted)

    def test_tampered_partition_unity_break_and_recovery(self):
        """
        Break: Tamper with NGD + PGD + ZDR = 1.0 partition identity.
        Recovery: Recompute true rates.
        """
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Break: Corrupt ngd_all
        corrupted = MetricReport(
            sample_size=report.sample_size,
            lpr=report.lpr,
            gpr=report.gpr,
            mean_delta_e=report.mean_delta_e,
            ngd_all=0.75,  # Corrupted: sum is 0.75 + 0.0 + 0.60 = 1.35
            ngd_cond=report.ngd_cond,
            pgd=report.pgd,
            zdr=report.zdr,
            egd=report.egd,
            ngd_count=report.ngd_count,
            pgd_count=report.pgd_count,
            zdr_count=report.zdr_count,
            local_pass_count=report.local_pass_count,
            global_pass_count=report.global_pass_count,
            delta_sum=report.delta_sum,
        )
        with pytest.raises(AssertionError, match="Partition identity NGD \\+ PGD \\+ ZDR = 1 failed"):
            EPKMetrics.verify_identities(corrupted)

        # Recovery
        corrupted.ngd_all = report.ngd_all
        EPKMetrics.verify_identities(corrupted)

    def test_tampered_egd_decomposition_break_and_recovery(self):
        """
        Break: Tamper with EGD = NGD + PGD = 1 - ZDR.
        Recovery: Restore authentic EGD.
        """
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Break: Corrupt egd
        corrupted = MetricReport(
            sample_size=report.sample_size,
            lpr=report.lpr,
            gpr=report.gpr,
            mean_delta_e=report.mean_delta_e,
            ngd_all=report.ngd_all,
            ngd_cond=report.ngd_cond,
            pgd=report.pgd,
            zdr=report.zdr,
            egd=0.10,  # Corrupted: true egd is 0.40
            ngd_count=report.ngd_count,
            pgd_count=report.pgd_count,
            zdr_count=report.zdr_count,
            local_pass_count=report.local_pass_count,
            global_pass_count=report.global_pass_count,
            delta_sum=report.delta_sum,
        )
        with pytest.raises(AssertionError, match="Identity EGD = NGD \\+ PGD failed"):
            EPKMetrics.verify_identities(corrupted)

        # Recovery
        corrupted.egd = report.egd
        EPKMetrics.verify_identities(corrupted)

    def test_tampered_signed_count_balance_break_and_recovery(self):
        """
        Break: Tamper with delta_sum = pgd_count - ngd_count.
        Recovery: Restore authentic delta_sum.
        """
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Break: Corrupt delta_sum
        corrupted = MetricReport(
            sample_size=report.sample_size,
            lpr=report.lpr,
            gpr=report.gpr,
            mean_delta_e=report.mean_delta_e,
            ngd_all=report.ngd_all,
            ngd_cond=report.ngd_cond,
            pgd=report.pgd,
            zdr=report.zdr,
            egd=report.egd,
            ngd_count=report.ngd_count,
            pgd_count=report.pgd_count,
            zdr_count=report.zdr_count,
            local_pass_count=report.local_pass_count,
            global_pass_count=report.global_pass_count,
            delta_sum=0,  # Corrupted: true delta_sum is -2
        )
        with pytest.raises(AssertionError, match="Signed count balance failed"):
            EPKMetrics.verify_identities(corrupted)

        # Recovery
        corrupted.delta_sum = report.delta_sum
        EPKMetrics.verify_identities(corrupted)

    def test_tampered_count_gap_break_and_recovery(self):
        """
        Break: Tamper with global_pass_count - local_pass_count = delta_sum.
        Recovery: Restore authentic global_pass_count.
        """
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Break: Corrupt global_pass_count
        corrupted = MetricReport(
            sample_size=report.sample_size,
            lpr=report.lpr,
            gpr=report.gpr,
            mean_delta_e=report.mean_delta_e,
            ngd_all=report.ngd_all,
            ngd_cond=report.ngd_cond,
            pgd=report.pgd,
            zdr=report.zdr,
            egd=report.egd,
            ngd_count=report.ngd_count,
            pgd_count=report.pgd_count,
            zdr_count=report.zdr_count,
            local_pass_count=report.local_pass_count,
            global_pass_count=100,  # Corrupted: 100 - 3 != -2
            delta_sum=report.delta_sum,
        )
        with pytest.raises(AssertionError, match="Count gap global - local != delta_sum"):
            EPKMetrics.verify_identities(corrupted)

        # Recovery
        corrupted.global_pass_count = report.global_pass_count
        EPKMetrics.verify_identities(corrupted)
