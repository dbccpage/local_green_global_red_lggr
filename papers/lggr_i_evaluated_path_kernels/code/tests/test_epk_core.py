"""Unit Test Suite for Evaluated Path Kernel (EPK) Core Engine.

Verifies exact mathematical identities, Phone Test metrics, kernel composition,
G1-G3 boundary conditions, proposal weighting, and reliability models.

Target: >=95% coverage across code/epk_core.py with genuine assertions.
AuthorityEffect: None.
Anchoring: sealed-derivation-v1 (3100c4e).
"""

from __future__ import annotations

import math
import runpy
import sys
from pathlib import Path
import numpy as np
import pytest

from epk_core import (
    BoundarySlice,
    ComposedPath,
    ComposedTrajectory,
    DefectKind,
    DetectorAdequacyGuard,
    DetectorAdequacyStatus,
    EPKMetrics,
    EvaluatedPathKernel,
    Evaluator,
    EvaluatorSet,
    EvaluatorVerdictTriple,
    MetricReport,
    MultiChannelDefect,
    PathSegment,
    ReliabilityModels,
    State,
    Trajectory,
    TrajectorySegment,
    calculate_epk,
    calculate_evaluator_defect,
    calculate_proposal_weighted_epk,
    make_five_trace_phone_test,
)


class TestEPKDataStructures:
    """Tests discrete state, segment, trajectory, and slice abstractions."""

    def test_state_creation_and_properties(self):
        s1 = State("S0")
        s2 = State("S0")
        s3 = State("S1")
        assert s1 == s2
        assert s1 != s3
        assert s1.label == "S0"
        assert s1.id == "S0"  # Verifies State.id property
        assert hash(s1) == hash(s2)
        assert len({s1, s2, s3}) == 2

    def test_trajectory_segment_valid(self):
        s0 = State("S0")
        s1 = State("S1")
        seg = TrajectorySegment(
            start_state=s0,
            end_state=s1,
            actions=("a1", "a2"),
            cost=2.5,
            risk=0.5,
            proposal_prob=0.8,
            raw_action=1.2,
            metadata={"agent_id": "agent_alpha"},
        )
        assert seg.start_state == s0
        assert seg.end_state == s1
        assert seg.source == s0  # Verifies TrajectorySegment.source property
        assert seg.target == s1  # Verifies TrajectorySegment.target property
        assert seg.action == 1.2  # Verifies TrajectorySegment.action property
        assert seg.cost == 2.5
        assert seg.risk == 0.5
        assert seg.proposal_prob == 0.8
        assert seg.raw_action == 1.2
        assert seg.actions == ("a1", "a2")
        assert seg.metadata["agent_id"] == "agent_alpha"

    def test_trajectory_segment_defaults(self):
        s0 = State("S0")
        s1 = State("S1")
        seg_default = TrajectorySegment(s0, s1, ("step",))
        assert seg_default.cost == 0.0
        assert seg_default.risk == 0.0
        assert seg_default.proposal_prob == 1.0
        assert seg_default.raw_action == 0.0
        assert seg_default.metadata == {}

    def test_composed_trajectory_properties_and_aliases(self):
        s0 = State("S0")
        sb = State("Sb")
        s1 = State("S1")
        seg1 = TrajectorySegment(s0, sb, ("a1",), cost=1.0, risk=0.2, proposal_prob=0.9, raw_action=0.5)
        seg2 = TrajectorySegment(sb, s1, ("a2",), cost=2.0, risk=0.3, proposal_prob=0.8, raw_action=0.7)
        comp = ComposedTrajectory(seg1, seg2)

        assert comp.start_state == s0
        assert comp.intermediate_state == sb
        assert comp.end_state == s1
        assert comp.combined_actions == ("a1", "a2")
        assert comp.total_cost == 3.0
        assert comp.total_risk == 0.5
        assert pytest.approx(comp.proposal_product) == 0.72
        assert pytest.approx(comp.total_raw_action) == 1.2

        # Verify canonical aliases from PROJECT.md
        assert PathSegment is TrajectorySegment
        assert ComposedPath is ComposedTrajectory
        assert Trajectory is ComposedTrajectory
        assert Evaluator is EvaluatorSet

    def test_boundary_slice_validation(self):
        s0 = State("S0")
        sb1 = State("Sb1")
        sb2 = State("Sb2")
        s_out = State("S_other")
        s1 = State("S1")

        bslice = BoundarySlice(states={sb1, sb2})
        assert bslice.contains(sb1)
        assert bslice.contains(sb2)
        assert not bslice.contains(s_out)

        comp1 = ComposedTrajectory(
            TrajectorySegment(s0, sb1, ("a",)),
            TrajectorySegment(sb1, s1, ("b",)),
        )
        comp2 = ComposedTrajectory(
            TrajectorySegment(s0, s_out, ("a",)),
            TrajectorySegment(s_out, s1, ("b",)),
        )

        is_valid1, violations1 = bslice.validate_unique_decomposition([comp1])
        assert is_valid1
        assert len(violations1) == 0

        is_valid2, violations2 = bslice.validate_unique_decomposition([comp1, comp2])
        assert not is_valid2
        assert len(violations2) == 1
        assert "S_other" in violations2[0]


class TestEvaluatorVerdictTripleAndDefects:
    """Tests verdict evaluation, defect classification, and standalone calculators."""

    def test_defect_trichotomy_classification(self):
        # NGD: (1, 1, 0) -> Delta_E = -1
        t_ngd = EvaluatorVerdictTriple(1, 1, 0)
        assert t_ngd.local_product == 1
        assert t_ngd.delta_eval == -1
        assert t_ngd.defect_kind == DefectKind.NGD
        assert t_ngd.is_ngd
        assert not t_ngd.is_pgd
        assert not t_ngd.is_zdr

        # PGD: (0, 1, 1), (1, 0, 1), (0, 0, 1) -> Delta_E = 1
        for e1, e2 in [(0, 1), (1, 0), (0, 0)]:
            t_pgd = EvaluatorVerdictTriple(e1, e2, 1)
            assert t_pgd.local_product == 0
            assert t_pgd.delta_eval == 1
            assert t_pgd.defect_kind == DefectKind.PGD
            assert not t_pgd.is_ngd
            assert t_pgd.is_pgd
            assert not t_pgd.is_zdr

        # ZDR: (1, 1, 1), (0, 0, 0), (1, 0, 0), (0, 1, 0) -> Delta_E = 0
        for e1, e2, eg in [(1, 1, 1), (0, 0, 0), (1, 0, 0), (0, 1, 0)]:
            t_zdr = EvaluatorVerdictTriple(e1, e2, eg)
            assert t_zdr.delta_eval == 0
            assert t_zdr.defect_kind == DefectKind.ZDR
            assert not t_zdr.is_ngd
            assert not t_zdr.is_pgd
            assert t_zdr.is_zdr

    def test_defect_kind_enum_values(self):
        assert DefectKind.NGD.value == -1
        assert DefectKind.ZDR.value == 0
        assert DefectKind.PGD.value == 1
        assert DefectKind(-1) == DefectKind.NGD
        assert DefectKind(0) == DefectKind.ZDR
        assert DefectKind(1) == DefectKind.PGD

    def test_calculate_evaluator_defect_function(self):
        # 1. Using EvaluatorVerdictTriple instance
        triple_ngd = EvaluatorVerdictTriple(1, 1, 0)
        assert calculate_evaluator_defect(triple_ngd) == -1

        triple_pgd = EvaluatorVerdictTriple(0, 1, 1)
        assert calculate_evaluator_defect(triple_pgd) == 1

        triple_zdr = EvaluatorVerdictTriple(1, 1, 1)
        assert calculate_evaluator_defect(triple_zdr) == 0

        # 2. Using explicit arguments
        assert calculate_evaluator_defect(e1=1, e2=1, eg=0) == -1
        assert calculate_evaluator_defect(e1=0, e2=1, eg=1) == 1
        assert calculate_evaluator_defect(e1=1, e2=1, eg=1) == 0
        assert calculate_evaluator_defect(e1=0, e2=0, eg=0) == 0

        # 3. Using gamma1, gamma2 and eg keyword arguments
        assert calculate_evaluator_defect(gamma1=1, gamma2=1, eg=0) == -1
        assert calculate_evaluator_defect(gamma1=0, gamma2=1, eg=1) == 1

        # 4. Using the public three-positional API (e1, e2, eg)
        assert calculate_evaluator_defect(1, 1, 0) == -1
        assert calculate_evaluator_defect(0, 1, 1) == 1

        # 5. Backward-compatible five-position form (gamma1, gamma2, e1, e2, eg)
        assert calculate_evaluator_defect(None, None, 1, 1, 0) == -1
        assert calculate_evaluator_defect(None, None, 0, 1, 1) == 1

        # Ambiguous, incomplete, and non-binary calls fail closed.
        with pytest.raises(TypeError):
            calculate_evaluator_defect(triple_ngd, 1)
        with pytest.raises(TypeError):
            calculate_evaluator_defect(1, 1)
        with pytest.raises(ValueError):
            calculate_evaluator_defect(1, 1, 2)


class TestFiveTracePhoneTestAndIdentities:
    """Tests the canonical Section 1.6 Five-Trace Phone Test and mathematical identities."""

    def test_canonical_phone_test_exact_values(self):
        triples = make_five_trace_phone_test()
        report = EPKMetrics.compute(triples)

        # Basic sample statistics
        assert report.sample_size == 5
        assert report.local_pass_count == 3
        assert report.global_pass_count == 1
        assert report.delta_sum == -2
        assert report.ngd_count == 2
        assert report.pgd_count == 0
        assert report.zdr_count == 3

        # Rate metrics
        assert pytest.approx(report.lpr) == 0.60
        assert pytest.approx(report.gpr) == 0.20
        assert pytest.approx(report.mean_delta_e) == -0.40
        assert pytest.approx(report.ngd_all) == 0.40
        assert pytest.approx(report.ngd_cond) == 2 / 3
        assert pytest.approx(report.pgd) == 0.00
        assert pytest.approx(report.zdr) == 0.60
        assert pytest.approx(report.egd) == 0.40

        # Property accessors
        assert pytest.approx(report.expected_gluing_defect) == -0.40
        assert pytest.approx(report.ngd) == 0.40
        with pytest.warns(DeprecationWarning, match="pass-rate gap"):
            assert pytest.approx(report.rke) == 0.40

    def test_mathematical_identities_balanced_sample(self):
        # Heterogeneous sample with all defect kinds
        triples = [
            EvaluatorVerdictTriple(1, 1, 0),  # NGD (-1)
            EvaluatorVerdictTriple(1, 1, 0),  # NGD (-1)
            EvaluatorVerdictTriple(0, 1, 1),  # PGD (+1)
            EvaluatorVerdictTriple(1, 1, 1),  # ZDR (0)
            EvaluatorVerdictTriple(0, 0, 0),  # ZDR (0)
        ]
        report = EPKMetrics.compute(triples)

        # 1. GPR - LPR == mean(Delta_E)
        assert pytest.approx(report.gpr - report.lpr) == report.mean_delta_e
        # 2. Partition unity: NGD + PGD + ZDR == 1
        assert pytest.approx(report.ngd_all + report.pgd + report.zdr) == 1.0
        # 3. EGD == NGD + PGD == 1 - ZDR
        assert pytest.approx(report.egd) == report.ngd_all + report.pgd
        assert pytest.approx(report.egd) == 1.0 - report.zdr
        # 4. delta_sum == pgd_count - ngd_count
        assert report.delta_sum == report.pgd_count - report.ngd_count
        # 5. global_count - local_count == delta_sum
        assert report.global_pass_count - report.local_pass_count == report.delta_sum

    def test_pure_defect_samples(self):
        # Pure NGD sample
        pure_ngd = [EvaluatorVerdictTriple(1, 1, 0)] * 4
        rep_ngd = EPKMetrics.compute(pure_ngd)
        assert rep_ngd.lpr == 1.0
        assert rep_ngd.gpr == 0.0
        assert rep_ngd.mean_delta_e == -1.0
        assert rep_ngd.ngd_all == 1.0
        assert rep_ngd.pgd == 0.0
        assert rep_ngd.zdr == 0.0
        assert rep_ngd.egd == 1.0
        assert rep_ngd.ngd_cond == 1.0

        # Pure PGD sample
        pure_pgd = [EvaluatorVerdictTriple(0, 1, 1)] * 4
        rep_pgd = EPKMetrics.compute(pure_pgd)
        assert rep_pgd.lpr == 0.0
        assert rep_pgd.gpr == 1.0
        assert rep_pgd.mean_delta_e == 1.0
        assert rep_pgd.ngd_all == 0.0
        assert rep_pgd.pgd == 1.0
        assert rep_pgd.zdr == 0.0
        assert rep_pgd.egd == 1.0
        assert rep_pgd.ngd_cond is None  # No local passes, conditional NGD is None

        # Pure ZDR passing sample
        pure_zdr = [EvaluatorVerdictTriple(1, 1, 1)] * 4
        rep_zdr = EPKMetrics.compute(pure_zdr)
        assert rep_zdr.lpr == 1.0
        assert rep_zdr.gpr == 1.0
        assert rep_zdr.mean_delta_e == 0.0
        assert rep_zdr.ngd_all == 0.0
        assert rep_zdr.pgd == 0.0
        assert rep_zdr.zdr == 1.0
        assert rep_zdr.egd == 0.0


class TestEvaluatedPathKernelCalculusAndComposition:
    """Tests kernel computation, G1-G3 composition theorem, and error bounds."""

    def test_compute_kernel_basic_and_aliases(self):
        s0 = State("S0")
        s1 = State("S1")
        trajectories = [
            TrajectorySegment(s0, s1, ("step1",), raw_action=1.0, proposal_prob=0.5, cost=0.2, risk=0.1),
            TrajectorySegment(s0, s1, ("step2",), raw_action=2.0, proposal_prob=0.5, cost=0.4, risk=0.2),
        ]
        eval_pass = lambda _: 1
        eval_fail = lambda _: 0

        # compute_kernel with beta, lam, mu
        z = EvaluatedPathKernel.compute_kernel(trajectories, eval_pass, beta=1.0, lam=0.5, mu=0.5)
        # term 1: action = 1.0*1.0 + 0.5*0.2 + 0.5*0.1 = 1.15 -> 0.5 * exp(-1.15)
        # term 2: action = 1.0*2.0 + 0.5*0.4 + 0.5*0.2 = 2.30 -> 0.5 * exp(-2.30)
        expected = 0.5 * np.exp(-1.15) + 0.5 * np.exp(-2.30)
        assert pytest.approx(z) == expected

        # Verify calculate_epk and calculate_proposal_weighted_epk aliases
        z_alias1 = calculate_epk(trajectories, eval_pass, beta=1.0, lam=0.5, mu=0.5)
        z_alias2 = calculate_proposal_weighted_epk(trajectories, eval_pass, beta=1.0, lam=0.5, mu=0.5)
        assert pytest.approx(z_alias1) == expected
        assert pytest.approx(z_alias2) == expected

        # Zero mass with always-fail evaluator
        assert EvaluatedPathKernel.compute_kernel(trajectories, eval_fail) == 0.0

    def test_evaluate_composition_rke(self):
        z_direct = 0.85
        z_composed = 0.80
        rke, nrke = EvaluatedPathKernel.evaluate_composition(z_direct, z_composed)
        assert pytest.approx(rke) == 0.05
        assert pytest.approx(nrke) == 0.05 / 0.85

        # Edge case: zero direct kernel mass with epsilon stabilizer
        rke_zero, nrke_zero = EvaluatedPathKernel.evaluate_composition(0.0, 0.0, eps=1e-8)
        assert rke_zero == 0.0
        assert nrke_zero == 0.0

    def test_evaluator_residual_calculation(self):
        s0 = State("S0")
        sb = State("Sb")
        s1 = State("S1")
        seg1 = TrajectorySegment(s0, sb, ("a",), raw_action=0.5)
        seg2 = TrajectorySegment(sb, s1, ("b",), raw_action=0.5)
        comp = ComposedTrajectory(seg1, seg2)

        # Factored evaluators -> Delta_E = 0 -> R_Eval = 0
        eval_set_factored = EvaluatorSet(
            eval_1=lambda _: 1,
            eval_2=lambda _: 1,
            eval_g=lambda _: 1,
        )
        res_0 = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set_factored, beta=1.0)
        assert pytest.approx(res_0) == 0.0

        # LGGR failure -> Delta_E = -1 -> R_Eval = -exp(-1.0)
        eval_set_lggr = EvaluatorSet(
            eval_1=lambda _: 1,
            eval_2=lambda _: 1,
            eval_g=lambda _: 0,
        )
        res_neg = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set_lggr, beta=1.0)
        assert pytest.approx(res_neg) == -np.exp(-1.0)

        # PGD rescue -> Delta_E = +1 -> R_Eval = +exp(-1.0)
        eval_set_pgd = EvaluatorSet(
            eval_1=lambda _: 0,
            eval_2=lambda _: 1,
            eval_g=lambda _: 1,
        )
        res_pos = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set_pgd, beta=1.0)
        assert pytest.approx(res_pos) == float(np.exp(-1.0))

    def test_kernel_composition_theorem_under_g1_g3(self):
        """
        Verifies Theorem 1 (Section 2 action kernel): Under structural conditions G1 (boundary sufficiency),
        G2 (action additivity), and G3 (evaluator factorization Delta_E = 0),
        the unweighted action kernel factors exactly:
        Z_beta(S_c | S_a) = sum_{S_b in B} Z_beta(S_c | S_b) * Z_beta(S_b | S_a)
        yielding RKE == 0. Proposal probabilities are deliberately non-unit and do not enter the direct sum.
        """
        s_a = State("Sa")
        s_b1 = State("Sb1")
        s_b2 = State("Sb2")
        s_c = State("Sc")
        bslice = BoundarySlice(states={s_b1, s_b2})

        # Segments for Stage 1 (Sa -> Sb) with deliberately non-unit proposal probabilities
        seg1_b1 = TrajectorySegment(s_a, s_b1, ("step1_1",), raw_action=0.4, proposal_prob=0.6)
        seg1_b2 = TrajectorySegment(s_a, s_b2, ("step1_2",), raw_action=0.6, proposal_prob=0.4)

        # Segments for Stage 2 (Sb -> Sc) with deliberately non-unit proposal probabilities
        seg2_b1 = TrajectorySegment(s_b1, s_c, ("step2_1",), raw_action=0.5, proposal_prob=0.7)
        seg2_b2 = TrajectorySegment(s_b2, s_c, ("step2_2",), raw_action=0.8, proposal_prob=0.3)

        # Composed trajectories passing through B (G1 satisfied)
        comp_b1 = ComposedTrajectory(seg1_b1, seg2_b1)
        comp_b2 = ComposedTrajectory(seg1_b2, seg2_b2)
        valid_g1, _ = bslice.validate_unique_decomposition([comp_b1, comp_b2])
        assert valid_g1

        # G3 satisfied: Factored evaluators
        e1 = lambda seg: 1
        e2 = lambda seg: 1
        eg = lambda comp: 1
        eval_set = EvaluatorSet(eval_1=e1, eval_2=e2, eval_g=eg)

        # Calculate stage 1 action kernels for each boundary state in B
        z_b1_a = EvaluatedPathKernel.compute_action_kernel([seg1_b1], e1, beta=1.0)
        z_b2_a = EvaluatedPathKernel.compute_action_kernel([seg1_b2], e1, beta=1.0)

        # Calculate stage 2 action kernels from each boundary state to Sc
        z_c_b1 = EvaluatedPathKernel.compute_action_kernel([seg2_b1], e2, beta=1.0)
        z_c_b2 = EvaluatedPathKernel.compute_action_kernel([seg2_b2], e2, beta=1.0)

        # Composed sum over B
        z_composed_sum = (z_c_b1 * z_b1_a) + (z_c_b2 * z_b2_a)

        # Direct Section 2 action kernel: sum exp(-beta * (A_1 + A_2)) WITHOUT proposal factors
        # Path b1: action = 0.4 + 0.5 = 0.9 -> exp(-0.9)
        # Path b2: action = 0.6 + 0.8 = 1.4 -> exp(-1.4)
        term_b1 = float(np.exp(-0.9))
        term_b2 = float(np.exp(-1.4))
        z_direct = term_b1 + term_b2

        # Check exact equality under G1-G3
        assert pytest.approx(z_composed_sum) == z_direct
        rke, nrke = EvaluatedPathKernel.evaluate_composition(z_direct, z_composed_sum)
        assert pytest.approx(rke, abs=1e-15) == 0.0
        assert pytest.approx(nrke, abs=1e-15) == 0.0

        # Section 4 action residual is identically zero
        res = EvaluatedPathKernel.compute_action_evaluator_residual([comp_b1, comp_b2], eval_set, beta=1.0)
        assert pytest.approx(res, abs=1e-15) == 0.0

    def test_hybrid_composition_under_g1_g2_g3_g4(self):
        """
        Verifies hybrid composition: Under G1-G3 and G4 (proposal factorization),
        the tempered hybrid kernel factors with proposal weighting:
        Z_hybrid(S_c | S_a) = sum_{S_b in B} Z_hybrid(S_c | S_b) * Z_hybrid(S_b | S_a).
        """
        s_a = State("Sa")
        s_b1 = State("Sb1")
        s_b2 = State("Sb2")
        s_c = State("Sc")
        BoundarySlice(states={s_b1, s_b2})

        seg1_b1 = TrajectorySegment(s_a, s_b1, ("step1_1",), raw_action=0.4, proposal_prob=0.6)
        seg1_b2 = TrajectorySegment(s_a, s_b2, ("step1_2",), raw_action=0.6, proposal_prob=0.4)
        seg2_b1 = TrajectorySegment(s_b1, s_c, ("step2_1",), raw_action=0.5, proposal_prob=0.7)
        seg2_b2 = TrajectorySegment(s_b2, s_c, ("step2_2",), raw_action=0.8, proposal_prob=0.3)

        comp_b1 = ComposedTrajectory(seg1_b1, seg2_b1)
        comp_b2 = ComposedTrajectory(seg1_b2, seg2_b2)

        e1 = lambda seg: 1
        e2 = lambda seg: 1
        eg = lambda comp: 1
        eval_set = EvaluatorSet(eval_1=e1, eval_2=e2, eval_g=eg)

        z_b1_a = EvaluatedPathKernel.compute_hybrid_kernel([seg1_b1], e1, beta=1.0, lam=0.0, mu=0.0)
        z_b2_a = EvaluatedPathKernel.compute_hybrid_kernel([seg1_b2], e1, beta=1.0, lam=0.0, mu=0.0)
        z_c_b1 = EvaluatedPathKernel.compute_hybrid_kernel([seg2_b1], e2, beta=1.0, lam=0.0, mu=0.0)
        z_c_b2 = EvaluatedPathKernel.compute_hybrid_kernel([seg2_b2], e2, beta=1.0, lam=0.0, mu=0.0)

        z_composed_sum = (z_c_b1 * z_b1_a) + (z_c_b2 * z_b2_a)

        term_b1 = 0.42 * np.exp(-0.9)
        term_b2 = 0.12 * np.exp(-1.4)
        z_direct = term_b1 + term_b2

        assert pytest.approx(z_composed_sum) == z_direct
        rke, nrke = EvaluatedPathKernel.evaluate_composition(z_direct, z_composed_sum)
        assert pytest.approx(rke, abs=1e-15) == 0.0
        assert pytest.approx(nrke, abs=1e-15) == 0.0

        res = EvaluatedPathKernel.compute_hybrid_evaluator_residual([comp_b1, comp_b2], eval_set, beta=1.0, lam=0.0, mu=0.0)
        assert pytest.approx(res, abs=1e-15) == 0.0


class TestMultiChannelDefectAndProposalWeighting:
    """Tests POCv2 multi-channel defect calculations."""

    def test_multi_channel_defect_total(self):
        defect = MultiChannelDefect(
            delta_eval=-1,
            delta_cost=1.5,
            delta_risk=0.5,
            delta_prop=0.2,
            delta_action=2.0,
        )
        assert defect.delta_eval == -1
        assert defect.delta_action == 2.0
        # Delta_total = Delta_P + lambda * Delta_C + mu * Delta_R
        total = defect.total_effective_defect(lam=2.0, mu=3.0)
        # 0.2 + 2.0 * 1.5 + 3.0 * 0.5 = 0.2 + 3.0 + 1.5 = 4.7
        assert pytest.approx(total) == 4.7

        # Zero weights defaults to pure proposal defect
        assert pytest.approx(defect.total_effective_defect(lam=0.0, mu=0.0)) == 0.2


class TestReliabilityModelsAndAdequacy:
    """Tests PoE, MoE, Activation Density, and Detector Adequacy Guards."""

    def test_product_of_experts(self):
        assert ReliabilityModels.product_of_experts_pass([1, 1, 1]) == 1
        assert ReliabilityModels.product_of_experts_pass([1, 0, 1]) == 0
        assert ReliabilityModels.product_of_experts_pass([0, 0, 0]) == 0
        # Empty list is vacuous conjunction
        assert ReliabilityModels.product_of_experts_pass([]) == 1

    def test_mixture_of_experts(self):
        # Majority voting (3 experts, equal weights)
        weights = [1.0, 1.0, 1.0]
        assert ReliabilityModels.mixture_of_experts_pass([1, 1, 0], weights, threshold=0.5) == 1
        assert ReliabilityModels.mixture_of_experts_pass([1, 0, 0], weights, threshold=0.5) == 0

        # Weighted voting
        w_asymm = [0.6, 0.2, 0.2]
        assert ReliabilityModels.mixture_of_experts_pass([1, 0, 0], w_asymm, threshold=0.5) == 1
        assert ReliabilityModels.mixture_of_experts_pass([0, 1, 1], w_asymm, threshold=0.5) == 0

        # All-zero weights fallback protection (w_sum == 0)
        assert ReliabilityModels.mixture_of_experts_pass([1, 1], [0.0, 0.0], threshold=0.5) == 0

    def test_activation_density_first_order_condition(self):
        d_val = 0.2
        cost_val = 0.8
        cost_deriv = 0.5
        defect_deriv = 0.5 * (1.0 - 0.2) / 0.8
        assert ReliabilityModels.activation_density_foc(d_val, cost_deriv, defect_deriv, cost_val)
        # Non-matching derivatives return False
        assert not ReliabilityModels.activation_density_foc(d_val, cost_deriv, 10.0, cost_val)

    def test_activation_density_curve(self):
        alphas = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        c, d, s = ReliabilityModels.activation_density_curve(alphas)
        assert len(c) == 5
        assert len(d) == 5
        assert len(s) == 5
        # All values bounded in [0, 1]
        assert np.all(c >= 0.0) and np.all(c <= 1.0)
        assert np.all(d >= 0.0) and np.all(d <= 1.0)
        assert np.all(s >= 0.0) and np.all(s <= 1.0)
        # S = C * (1 - D)
        assert np.allclose(s, c * (1.0 - d))

    def test_optimal_activation_density(self):
        alpha_star, s_star = ReliabilityModels.find_optimal_activation_density()
        assert 0.1 < alpha_star < 0.9
        assert 0.0 < s_star < 1.0

        # Verify that alpha_star is strictly better than boundaries
        alphas_bound = np.array([0.01, alpha_star, 0.99])
        _, _, s_eval = ReliabilityModels.activation_density_curve(alphas_bound)
        assert s_star >= s_eval[0]
        assert s_star >= s_eval[2]

    def test_detector_adequacy_audits(self):
        # Adequate sample
        phone = make_five_trace_phone_test()
        warnings_phone = DetectorAdequacyGuard.audit(phone)
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED in warnings_phone

        # check alias
        assert DetectorAdequacyGuard.check(phone) == warnings_phone

        # Vacuous local (all e1=1 and e2=1)
        vacuous = [
            EvaluatorVerdictTriple(1, 1, 1),
            EvaluatorVerdictTriple(1, 1, 0),
        ]
        assert DetectorAdequacyStatus.VACUOUS_LOCAL in DetectorAdequacyGuard.audit(vacuous)

        # All-rejecting (e1 all 0 or e2 all 0)
        rejecting1 = [
            EvaluatorVerdictTriple(0, 1, 0),
            EvaluatorVerdictTriple(0, 0, 0),
        ]
        assert DetectorAdequacyStatus.ALL_REJECTING in DetectorAdequacyGuard.audit(rejecting1)

        rejecting2 = [
            EvaluatorVerdictTriple(1, 0, 0),
            EvaluatorVerdictTriple(0, 0, 0),
        ]
        assert DetectorAdequacyStatus.ALL_REJECTING in DetectorAdequacyGuard.audit(rejecting2)

        # Empty sample returns ALL_REJECTING
        assert DetectorAdequacyGuard.audit([]) == [DetectorAdequacyStatus.ALL_REJECTING]

        # Tautological coupling (all eg == e1 * e2)
        tautological = [
            EvaluatorVerdictTriple(1, 1, 1),
            EvaluatorVerdictTriple(1, 0, 0),
            EvaluatorVerdictTriple(0, 1, 0),
        ]
        assert DetectorAdequacyStatus.TAUTOLOGICAL_COUPLING in DetectorAdequacyGuard.audit(tautological)


@pytest.mark.xdist_group(name="figure_generation")
class TestFigureGeneration:
    """Tests that the publication figure generation runs cleanly."""

    def test_generate_figures_runs(self, tmp_path):
        import time

        from generate_figures import generate_all_figures

        first = tmp_path / "first"
        second = tmp_path / "second"
        fig_path = generate_all_figures(output_dir=first)
        assert fig_path.exists()
        assert fig_path.stat().st_size > 1000
        compat_path = first / "figure_1_lggr_diagnostics.png"
        assert compat_path.exists()
        assert compat_path.read_bytes() == fig_path.read_bytes()
        assert compat_path.with_suffix(".pdf").read_bytes() == fig_path.with_suffix(".pdf").read_bytes()

        # Cross a filesystem-clock tick.  Matplotlib's default PDF metadata
        # records wall time, so this comparison fails unless publication
        # metadata is fixed explicitly by the producer.
        time.sleep(1.1)
        second_path = generate_all_figures(output_dir=second)
        assert second_path.read_bytes() == fig_path.read_bytes()
        assert second_path.with_suffix(".pdf").read_bytes() == fig_path.with_suffix(".pdf").read_bytes()
        assert b"LGGR I deterministic figure producer" in fig_path.with_suffix(".pdf").read_bytes()

    def test_generate_figures_default_output(self, tmp_path, monkeypatch):
        """The API derives its documented public_export default from the module."""
        import generate_figures

        fake_source = tmp_path / "code" / "generate_figures.py"
        fake_source.parent.mkdir()
        monkeypatch.setattr(generate_figures, "__file__", str(fake_source))
        generated = generate_figures.generate_all_figures()
        assert generated == tmp_path / "public_export" / "figure_lggr_phase_boundary.png"

    def test_generate_figures_module_entrypoint_accepts_output_dir(
        self, tmp_path, monkeypatch
    ):
        """The real script entrypoint honors an isolated explicit output directory."""
        source_path = Path(__file__).resolve().parents[1] / "generate_figures.py"
        output = tmp_path / "public_export"
        monkeypatch.setattr(
            sys, "argv", [str(source_path), "--output-dir", str(output)]
        )
        runpy.run_path(str(source_path), run_name="__main__")
        expected = {
            "figure_lggr_phase_boundary.png",
            "figure_lggr_phase_boundary.pdf",
            "figure_1_lggr_diagnostics.png",
            "figure_1_lggr_diagnostics.pdf",
        }
        assert {path.name for path in output.iterdir()} == expected


class TestRepublicationCounterexampleRegressions:
    """Regression suite for expert review findings R1 through R11."""

    def test_r2_incomplete_cartesian_corpus_caught(self):
        a, b, c = map(State, ["a", "b", "c"])
        left = [TrajectorySegment(a, b, ("l1",)), TrajectorySegment(a, b, ("l2",))]
        right = [TrajectorySegment(b, c, ("r1",)), TrajectorySegment(b, c, ("r2",))]
        comps = [ComposedTrajectory(left[0], right[0]), ComposedTrajectory(left[1], right[1])]

        bslice = BoundarySlice({b})
        # Internal inference catches missing cross-pairs (2 observed vs 4 expected)
        is_valid, violations = bslice.validate_unique_decomposition(comps)
        assert not is_valid
        assert any("Incomplete Cartesian cross-product" in v for v in violations)

        # Explicit segment validation also catches missing pairs
        is_valid_exp, violations_exp = bslice.validate_unique_decomposition(
            comps, left_segments=left, right_segments=right
        )
        assert not is_valid_exp
        assert any("Missing Cartesian product trajectory" in v for v in violations_exp)

        # Duplicate decomposition branch with explicit segments
        dup_comps = comps + [ComposedTrajectory(left[0], right[0])]
        _, violations_dup = bslice.validate_unique_decomposition(
            dup_comps, left_segments=left, right_segments=right
        )
        assert any("Duplicate decomposition" in v for v in violations_dup)

        # Duplicate decomposition branch with inferred segments
        _, violations_dup_inferred = bslice.validate_unique_decomposition(dup_comps)
        assert any("Duplicate composed trajectories" in v for v in violations_dup_inferred)

    def test_g1_rejects_empty_global_family_with_compatible_segments(self):
        """G1 is not the vacuous one-way claim that every observed path splits."""
        a, b, c = map(State, ["a", "b", "c"])
        left = [TrajectorySegment(a, b, ("left",))]
        right = [TrajectorySegment(b, c, ("right",))]

        valid, violations = BoundarySlice({b}).validate_unique_decomposition(
            [], left_segments=left, right_segments=right
        )

        assert not valid
        assert violations == [
            "Missing Cartesian product trajectory for pair (('left',), ('right',)) through b."
        ]

    def test_four_term_contribution_expansion(self):
        """D3 retains both first-order residuals and their cross term."""
        e1, e2 = 1, 1
        w1, w2 = 2.0, 3.0
        delta_e, delta_w = -1, 5.0

        expanded = EvaluatedPathKernel.four_term_contribution(
            e1, e2, w1, w2, delta_e, delta_w
        )
        direct = (e1 * e2 + delta_e) * (w1 * w2 + delta_w)

        assert expanded == 6.0 - 6.0 + 5.0 - 5.0
        assert expanded == direct == 0.0

        with pytest.raises(ValueError, match="delta_e must lie"):
            EvaluatedPathKernel.four_term_contribution(1, 1, 2.0, 3.0, 2, 5.0)
        with pytest.raises(ValueError, match="must be finite"):
            EvaluatedPathKernel.four_term_contribution(1, 1, math.inf, 3.0, 0, 5.0)

    def test_e2_count_gap_equals_signed_defect_sum(self):
        sample = [
            EvaluatorVerdictTriple(1, 1, 0),
            EvaluatorVerdictTriple(0, 1, 1),
            EvaluatorVerdictTriple(1, 1, 1),
            EvaluatorVerdictTriple(1, 0, 0),
        ]
        report = EPKMetrics.compute(sample)
        assert report.global_pass_count - report.local_pass_count == report.delta_sum
        assert report.delta_sum == 0

    def test_e6_egd_zero_iff_all_zdr(self):
        all_zdr = [
            EvaluatorVerdictTriple(1, 1, 1),
            EvaluatorVerdictTriple(1, 0, 0),
            EvaluatorVerdictTriple(0, 1, 0),
        ]
        one_defect = all_zdr + [EvaluatorVerdictTriple(1, 1, 0)]

        for sample in (all_zdr, one_defect):
            report = EPKMetrics.compute(sample)
            every_trace_is_zdr = all(trace.is_zdr for trace in sample)
            assert (report.egd == 0.0) is every_trace_is_zdr

    def test_vacuous_local_accepts_collapse_defect_counts(self):
        sample = [
            EvaluatorVerdictTriple(1, 1, 1),
            EvaluatorVerdictTriple(1, 1, 0),
            EvaluatorVerdictTriple(1, 1, 0),
        ]
        report = EPKMetrics.compute(sample)

        assert report.ngd_all == report.egd
        assert report.egd == pytest.approx(1.0 - report.gpr)
        assert report.pgd_count == 0

    def test_r1_cancellation_with_full_cartesian_corpus(self):
        a, b, c = map(State, ["a", "b", "c"])
        left = [TrajectorySegment(a, b, ("l1",)), TrajectorySegment(a, b, ("l2",))]
        right = [TrajectorySegment(b, c, ("r1",))]
        full = [ComposedTrajectory(l, right[0]) for l in left]

        e1 = lambda s: int(s.actions == ("l1",))
        e2 = lambda s: 1
        eg = lambda t: 1 - e1(t.segment_1)

        z_g = sum(eg(t) for t in full)
        z_l = EvaluatedPathKernel.compute_kernel(left, e1) * EvaluatedPathKernel.compute_kernel([right[0]], e2)
        r = EvaluatedPathKernel.compute_evaluator_residual(full, EvaluatorSet(e1, e2, eg))
        triples = [EvaluatorVerdictTriple(e1(t.segment_1), e2(t.segment_2), eg(t)) for t in full]
        m = EPKMetrics.compute(triples)

        # Aggregate residual vanishes (R = 0.0) despite individual non-zero defects!
        assert z_g == 1.0
        assert z_l == 1.0
        assert r == 0.0
        assert m.ngd == 0.5
        assert m.pgd == 0.5
        assert m.egd == 1.0
        assert m.mean_delta_e == 0.0

    def test_r3_weighted_kernel_residual_exact_identity(self):
        a, b, c = map(State, ["a", "b", "c"])
        x = TrajectorySegment(a, b, ("x",), proposal_prob=0.5, raw_action=0.5, cost=1.0, risk=0.1)
        y = TrajectorySegment(b, c, ("y",), proposal_prob=0.5, raw_action=0.7, cost=1.5, risk=0.2)
        comp = ComposedTrajectory(x, y)

        eval_set = EvaluatorSet(lambda _: 1, lambda _: 1, lambda _: 0)
        z_l = (
            EvaluatedPathKernel.compute_kernel([x], lambda _: 1, beta=1.0, lam=0.5, mu=0.5)
            * EvaluatedPathKernel.compute_kernel([y], lambda _: 1, beta=1.0, lam=0.5, mu=0.5)
        )
        EvaluatedPathKernel.compute_kernel([comp.segment_1], lambda _: 0)  # 0
        r = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=1.0, lam=0.5, mu=0.5, mode="hybrid")
        r_helper = EvaluatedPathKernel.compute_hybrid_evaluator_residual([comp], eval_set, beta=1.0, lam=0.5, mu=0.5)

        assert pytest.approx(-z_l) == r
        assert pytest.approx(r) == r_helper

    def test_r4_pass_rate_gap_distinction_from_rke(self):
        triples = [EvaluatorVerdictTriple(1, 1, 0), EvaluatorVerdictTriple(1, 1, 0)]
        m = EPKMetrics.compute(triples)
        assert m.absolute_pass_rate_gap == 1.0
        with pytest.warns(DeprecationWarning, match="pass-rate gap"):
            assert m.rke == 1.0
        # Explicit RKE for two unit-weight NGD paths is 2.0
        explicit_rke, _ = EvaluatedPathKernel.evaluate_composition(0.0, 2.0)
        assert explicit_rke == 2.0
        assert m.absolute_pass_rate_gap != explicit_rke

    def test_r5_guard_detects_constant_degeneracies(self):
        t = EvaluatorVerdictTriple
        # Constant global zero
        res_zero = DetectorAdequacyGuard.audit([t(1, 1, 0), t(0, 1, 0), t(1, 0, 0)])
        assert DetectorAdequacyStatus.CONSTANT_GLOBAL_REJECT in res_zero
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED not in res_zero

        # Constant global one
        res_one = DetectorAdequacyGuard.audit([t(1, 1, 1), t(0, 1, 1), t(1, 0, 1)])
        assert DetectorAdequacyStatus.CONSTANT_GLOBAL_ACCEPT in res_one
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED not in res_one

        # Zero local product
        res_zlp = DetectorAdequacyGuard.audit([t(0, 1, 1), t(1, 0, 1)])
        assert DetectorAdequacyStatus.CONSTANT_LOCAL_PRODUCT_ZERO in res_zlp
        assert DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED not in res_zlp

        # Singleton boundary slice without trajectories is UNASSESSED (collapse unconfirmed)
        b_trivial = BoundarySlice({State("b_single")})
        res_unassessed = DetectorAdequacyGuard.audit([t(1, 1, 1), t(1, 1, 0), t(0, 1, 0), t(0, 0, 0)], boundary_slice=b_trivial)
        assert DetectorAdequacyStatus.SINGLETON_SLICE_CUT_UNASSESSED in res_unassessed

        # With confirmed terminal/identity collapse, flags TRIVIAL_SLICE
        s_single = State("b_single")
        comp_term = ComposedTrajectory(
            TrajectorySegment(State("a"), s_single, ("step1",), raw_action=1.0),
            TrajectorySegment(s_single, s_single, (), raw_action=0.0),
        )
        res_trivial = DetectorAdequacyGuard.audit(
            [t(1, 1, 1), t(1, 1, 0), t(0, 1, 0), t(0, 0, 0)],
            boundary_slice=b_trivial,
            composed_trajectories=[comp_term],
        )
        assert DetectorAdequacyStatus.TRIVIAL_SLICE in res_trivial

    def test_r10_monotone_activation_endpoint_accuracy(self):
        alpha_star, score_star = ReliabilityModels.find_optimal_activation_density(kappa=0.01)
        _, _, s_endpoint = ReliabilityModels.activation_density_curve(np.array([1.0]), kappa=0.01)
        assert alpha_star == 1.0
        assert pytest.approx(score_star) == s_endpoint[0] == 0.99

    def test_r11_input_contracts_type_and_domain_safety(self):
        a, c = State("a"), State("c")
        # calculate_evaluator_defect rejects floats
        with pytest.raises(TypeError, match="Verdicts must be integers in \\{0, 1\\}"):
            calculate_evaluator_defect(1.9, 1, 0.9)

        # Boolean verdicts accepted
        assert calculate_evaluator_defect(True, True, False) == -1
        assert EvaluatorVerdictTriple(True, False, True).delta_eval == 1

        # Float in EvaluatorVerdictTriple rejected
        with pytest.raises(TypeError):
            EvaluatorVerdictTriple(1.0, 0, 1)

        # Evaluator returning non-binary in compute_kernel rejected
        with pytest.raises(ValueError, match="Verdicts must be binary in \\{0, 1\\}"):
            EvaluatedPathKernel.compute_kernel([TrajectorySegment(a, c, ("x",))], lambda _: 2)

        with pytest.raises(TypeError):
            EvaluatedPathKernel.compute_kernel([TrajectorySegment(a, c, ("x",))], lambda _: 1.5)

        # TrajectorySegment negative raw action rejected
        with pytest.raises(ValueError, match="Raw action must be non-negative"):
            TrajectorySegment(a, c, ("x",), raw_action=-1.0)

        # TrajectorySegment non-finite parameters rejected
        with pytest.raises(ValueError, match="Raw action must be non-negative"):
            TrajectorySegment(a, c, ("x",), raw_action=float("nan"))

        with pytest.raises(ValueError, match="Cost must be non-negative"):
            TrajectorySegment(a, c, ("x",), cost=float("nan"))

        with pytest.raises(ValueError, match="Risk must be non-negative"):
            TrajectorySegment(a, c, ("x",), risk=float("nan"))

        with pytest.raises(ValueError, match="Proposal probability must be in \\(0, 1\\]"):
            TrajectorySegment(a, c, ("x",), proposal_prob=float("nan"))

    def test_undeclared_segments_rejected_in_g1_validation(self):
        """Review Finding 4: validate_unique_decomposition must check both directions of correspondence."""
        a, b, c = State("a"), State("b"), State("c")
        l1 = TrajectorySegment(a, b, ("l1",))
        l2 = TrajectorySegment(a, b, ("l2",))
        r1 = TrajectorySegment(b, c, ("r1",))

        t1 = ComposedTrajectory(l1, r1)
        t2 = ComposedTrajectory(l2, r1)
        b_slice = BoundarySlice({b})

        # When declared left set is only {l1} and right set is {r1},
        # t2 uses undeclared l2 and must be rejected as an invalid G1 correspondence.
        is_valid, violations = b_slice.validate_unique_decomposition(
            [t1, t2], left_segments=[l1], right_segments=[r1]
        )
        assert not is_valid
        assert any("undeclared left segment" in v for v in violations)

    def test_single_segment_argument_raises_value_error(self):
        """Supplying only one segment list must raise ValueError rather than silently falling back."""
        a, b = State("a"), State("b")
        l1 = TrajectorySegment(a, b, ("l1",))
        b_slice = BoundarySlice({b})
        with pytest.raises(ValueError, match="Both left_segments and right_segments must be supplied together"):
            b_slice.validate_unique_decomposition([], left_segments=[l1])

    def test_expert_and_kernel_input_validation(self):
        """Review Finding 11: PoE must reject non-binary inputs; kernels reject negative/NaN coefficients."""
        with pytest.raises(ValueError, match="Verdicts must be binary"):
            ReliabilityModels.product_of_experts_pass([2, 1])

        a, b = State("a"), State("b")
        traj = TrajectorySegment(a, b, ("x",), raw_action=1.0)

        with pytest.raises(ValueError, match="Kernel coefficients must be non-negative"):
            EvaluatedPathKernel.compute_kernel([traj], lambda _: 1, beta=-1.0)

        with pytest.raises(ValueError, match="Kernel coefficients must be finite"):
            EvaluatedPathKernel.compute_kernel([traj], lambda _: 1, beta=float("nan"))
        with pytest.raises(ValueError, match="Kernel coefficients must be finite"):
            EvaluatedPathKernel.compute_kernel([traj], lambda _: 1, beta=float("inf"))
        with pytest.raises(ValueError, match="Kernel coefficients must be finite"):
            EvaluatedPathKernel.compute_kernel([traj], lambda _: 1, beta=float("-inf"))

    def test_distinct_kernel_modes_and_functions(self):
        """Review Finding 5: distinct functions for Section 2, Section 11, and hybrid kernels."""
        a, b = State("a"), State("b")
        traj = TrajectorySegment(a, b, ("x",), proposal_prob=0.8, raw_action=1.0, cost=0.5, risk=0.2)
        evaluator = lambda _: 1

        k_act = EvaluatedPathKernel.compute_action_kernel([traj], evaluator, beta=1.0)
        k_prop = EvaluatedPathKernel.compute_proposal_cost_risk_kernel([traj], evaluator, lam=1.0, mu=1.0)
        k_hyb = EvaluatedPathKernel.compute_hybrid_kernel([traj], evaluator, beta=1.0, lam=1.0, mu=1.0)

        # Action: exp(-1.0) = 0.3678794
        assert pytest.approx(k_act) == np.exp(-1.0)
        # Proposal-cost-risk: 0.8 * exp(-0.5 - 0.2) = 0.8 * exp(-0.7)
        assert pytest.approx(k_prop) == 0.8 * np.exp(-0.7)
        # Hybrid: 0.8 * exp(-1.0 - 0.5 - 0.2) = 0.8 * exp(-1.7)
        assert pytest.approx(k_hyb) == 0.8 * np.exp(-1.7)

    def test_singleton_interior_cut_vs_terminal_cut_adequacy(self):
        """Review Finding 6: singleton boundary cut with nonidentity interior stages is not TRIVIAL_SLICE."""
        a, b, c = State("a"), State("b"), State("c")
        l1 = TrajectorySegment(a, b, ("step1",), raw_action=1.0)
        r1 = TrajectorySegment(b, c, ("step2",), raw_action=1.0)
        comp = ComposedTrajectory(l1, r1)
        b_slice = BoundarySlice({b})

        # Genuine interior cut: nonidentity stages
        res_interior = DetectorAdequacyGuard.audit(
            [EvaluatorVerdictTriple(1, 1, 1)],
            boundary_slice=b_slice,
            composed_trajectories=[comp],
        )
        assert DetectorAdequacyStatus.TRIVIAL_SLICE not in res_interior
        assert DetectorAdequacyStatus.SINGLETON_SLICE_CUT_UNASSESSED in res_interior

        # Singleton cut with no trajectories passed -> SINGLETON_SLICE_CUT_UNASSESSED (collapse unconfirmed)
        res_unassessed = DetectorAdequacyGuard.audit(
            [EvaluatorVerdictTriple(1, 1, 1)],
            boundary_slice=b_slice,
            composed_trajectories=None,
        )
        assert DetectorAdequacyStatus.TRIVIAL_SLICE not in res_unassessed
        assert DetectorAdequacyStatus.SINGLETON_SLICE_CUT_UNASSESSED in res_unassessed

        # Mixed cut: one identity/terminal path and one genuine interior path
        # Because not all paths collapse, the cut as a whole is UNASSESSED / non-trivial
        r_id = TrajectorySegment(c, c, (), raw_action=0.0)
        l_term = TrajectorySegment(a, c, ("step1",), raw_action=1.0)
        comp_term = ComposedTrajectory(l_term, r_id)
        res_mixed = DetectorAdequacyGuard.audit(
            [EvaluatorVerdictTriple(1, 1, 1), EvaluatorVerdictTriple(1, 1, 1)],
            boundary_slice=BoundarySlice({c}),
            composed_trajectories=[comp_term, comp],
        )
        assert DetectorAdequacyStatus.TRIVIAL_SLICE not in res_mixed
        assert DetectorAdequacyStatus.SINGLETON_SLICE_CUT_UNASSESSED in res_mixed

        # Terminal identity cut: all paths collapse to terminal/identity
        b_term = BoundarySlice({c})
        res_term = DetectorAdequacyGuard.audit(
            [EvaluatorVerdictTriple(1, 1, 1)],
            boundary_slice=b_term,
            composed_trajectories=[comp_term],
        )
        assert DetectorAdequacyStatus.TRIVIAL_SLICE in res_term

    def test_normalized_poe_and_moe_validation(self):
        """Test normalized PoE over candidate ensembles and MoE validation edge cases."""
        # 2 candidates, 2 experts:
        # candidate 0: expert masses [0.8, 0.5] -> prod = 0.40
        # candidate 1: expert masses [0.2, 0.5] -> prod = 0.10
        # sum = 0.50 -> normalized = [0.8, 0.2]
        candidates = [[0.8, 0.5], [0.2, 0.5]]
        val = ReliabilityModels.normalized_product_of_experts(candidates)
        assert pytest.approx(val) == [0.8, 0.2]
        assert pytest.approx(sum(val)) == 1.0

        # Hard refusal (zero mass) on one candidate
        candidates_with_zero = [[0.6, 0.4], [0.9, 0.0], [0.3, 0.8]]
        val2 = ReliabilityModels.normalized_product_of_experts(candidates_with_zero)
        assert pytest.approx(val2) == [0.5, 0.0, 0.5]

        # Validation edge cases:
        # 1. Empty candidate ensemble
        with pytest.raises(ValueError, match="must not be empty"):
            ReliabilityModels.normalized_product_of_experts([])

        # 2. Empty expert vector
        with pytest.raises(ValueError, match="at least one expert"):
            ReliabilityModels.normalized_product_of_experts([[]])

        # 3. Mismatched expert counts
        with pytest.raises(ValueError, match="expected 2"):
            ReliabilityModels.normalized_product_of_experts([[0.5, 0.5], [0.5]])

        # 4. Negative probabilities
        with pytest.raises(ValueError, match="must be non-negative"):
            ReliabilityModels.normalized_product_of_experts([[0.5, -0.1], [0.5, 0.5]])

        # 5. Non-finite probabilities
        with pytest.raises(ValueError, match="must be non-negative"):
            ReliabilityModels.normalized_product_of_experts([[float("nan"), 0.5], [0.5, 0.5]])

        # 6. Disjoint support (normalization denominator == 0)
        with pytest.raises(ValueError, match="positive normalization denominator"):
            ReliabilityModels.normalized_product_of_experts([[1.0, 0.0], [0.0, 1.0]])

        # MoE validation
        with pytest.raises(ValueError, match="Verdicts and weights must have matching lengths"):
            ReliabilityModels.mixture_of_experts_pass([1], [0.5, 0.5])


class TestReviewRegressionFindings:
    """Explicit regression tests for the peer review findings."""

    def test_g1_duplicate_segment_declarations_rejected(self):
        s_a, s_b, s_c = State("a"), State("b"), State("c")
        left = TrajectorySegment(s_a, s_b, ("l1",))
        right = TrajectorySegment(s_b, s_c, ("r1",))
        comp = ComposedTrajectory(left, right)
        b_slice = BoundarySlice({s_b})

        # Duplicated left segment
        ok_l, violations_l = b_slice.validate_unique_decomposition(
            [comp], left_segments=[left, left], right_segments=[right]
        )
        assert not ok_l
        assert any("Duplicate segment declaration in left_segments" in v for v in violations_l)

        # Duplicated right segment
        ok_r, violations_r = b_slice.validate_unique_decomposition(
            [comp], left_segments=[left], right_segments=[right, right]
        )
        assert not ok_r
        assert any("Duplicate segment declaration in right_segments" in v for v in violations_r)

        # Duplicated trajectories
        ok_t, violations_t = b_slice.validate_unique_decomposition(
            [comp, comp], left_segments=[left], right_segments=[right]
        )
        assert not ok_t
        assert any("Duplicate composed trajectory declaration" in v or "Duplicate decomposition" in v for v in violations_t)

    def test_poe_verdicts_order_independent_validation(self):
        # Short-circuit order must not swallow malformed inputs
        with pytest.raises(ValueError):
            ReliabilityModels.product_of_experts_pass([0, 2])
        with pytest.raises(ValueError):
            ReliabilityModels.product_of_experts_pass([2, 0])
        with pytest.raises(TypeError):
            ReliabilityModels.product_of_experts_pass([0, 0.5])
        with pytest.raises(TypeError):
            ReliabilityModels.product_of_experts_pass([0, float("nan")])

    def test_moe_weight_and_threshold_contracts(self):
        # Negative weights rejected
        with pytest.raises(ValueError, match="non-negative"):
            ReliabilityModels.mixture_of_experts_pass([1, 1], [1.0, -0.5])

        # NaN weights rejected
        with pytest.raises(ValueError, match="finite"):
            ReliabilityModels.mixture_of_experts_pass([1, 1], [1.0, float("nan")])

        # Threshold domain bounds [0, 1]
        with pytest.raises(ValueError, match="Threshold"):
            ReliabilityModels.mixture_of_experts_pass([1, 1], [1.0, 1.0], threshold=-0.1)
        with pytest.raises(ValueError, match="Threshold"):
            ReliabilityModels.mixture_of_experts_pass([1, 1], [1.0, 1.0], threshold=1.1)
        with pytest.raises(ValueError, match="Threshold"):
            ReliabilityModels.mixture_of_experts_pass([1, 1], [1.0, 1.0], threshold=float("nan"))

        # Empty ensemble rejected
        with pytest.raises(ValueError, match="must not be empty"):
            ReliabilityModels.mixture_of_experts_pass([], [])

        # All-zero weights outcome: explicit refusal (0) even at threshold 0.0
        assert ReliabilityModels.mixture_of_experts_pass([1, 1], [0.0, 0.0], threshold=0.0) == 0

        # Scale invariance on large finite positive weights (1e308 overflow protection)
        assert ReliabilityModels.mixture_of_experts_pass([1, 1], [1.0, 1.0]) == 1
        assert ReliabilityModels.mixture_of_experts_pass([1, 1], [1e308, 1e308]) == 1
        assert ReliabilityModels.mixture_of_experts_pass([0, 1], [1e308, 1e308], threshold=0.5) == 1
        assert ReliabilityModels.mixture_of_experts_pass([0, 1], [1e308, 1e308], threshold=0.5000001) == 0

    def test_normalized_poe_underflow_large_ensemble(self):
        # 1100 stages of 0.5 underflows in direct product to 0.0, but log-domain normalizes exactly to [0.5, 0.5]
        cand = [[0.5] * 1100, [0.5] * 1100]
        res = ReliabilityModels.normalized_product_of_experts(cand)
        assert pytest.approx(res) == [0.5, 0.5]
        assert pytest.approx(sum(res)) == 1.0

    def test_compute_evaluator_residual_beta_zero_overflow_action(self):
        # Two segments with action 1e308 whose sum overflows to inf
        s_a, s_b, s_c = State("a"), State("b"), State("c")
        seg1 = TrajectorySegment(s_a, s_b, ("s1",), raw_action=1e308)
        seg2 = TrajectorySegment(s_b, s_c, ("s2",), raw_action=1e308)
        comp = ComposedTrajectory(seg1, seg2)

        eval_set = EvaluatorSet(
            eval_1=lambda s: 1,
            eval_2=lambda s: 1,
            eval_g=lambda c: 0,  # NGD: Delta_E = -1
        )
        res = EvaluatedPathKernel.compute_evaluator_residual(
            [comp], eval_set, beta=0.0, mode="action"
        )
        assert np.isfinite(res)
        assert res == -1.0

        # Also kernel with beta=0
        k = EvaluatedPathKernel.compute_kernel([seg1], eval_set.eval_1, beta=0.0, mode="action")
        assert k == 1.0

    def test_verify_identities_rejects_nan_rates(self):
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Non-finite rate must trigger AssertionError
        report.mean_delta_e = float("nan")
        with pytest.raises(AssertionError, match="Identity check requires finite rate values"):
            EPKMetrics.verify_identities(report)

        report_lpr = EPKMetrics.compute(phone)
        report_lpr.lpr = float("nan")
        with pytest.raises(AssertionError, match="Identity check requires finite rate values"):
            EPKMetrics.verify_identities(report_lpr)

    def test_validate_report_full_integrity(self):
        phone = make_five_trace_phone_test()
        report = EPKMetrics.compute(phone)

        # Authentic report passes validation
        EPKMetrics.validate_report(report)

        # Sample size <= 0
        corrupt = MetricReport(**report.__dict__)
        corrupt.sample_size = 0
        with pytest.raises(ValueError, match="Sample size"):
            EPKMetrics.validate_report(corrupt)

        # ngd_cond = 999
        corrupt = MetricReport(**report.__dict__)
        corrupt.ngd_cond = 999.0
        with pytest.raises(AssertionError, match="ngd_cond"):
            EPKMetrics.validate_report(corrupt)

        # ngd_cond = NaN in verify_identities
        corrupt = MetricReport(**report.__dict__)
        corrupt.ngd_cond = float("nan")
        with pytest.raises(AssertionError, match="ngd_cond"):
            EPKMetrics.verify_identities(corrupt)

        # Rate/count inconsistency (lpr=0.7, gpr=0.3 with original 5-trace counts)
        corrupt = MetricReport(**report.__dict__)
        corrupt.lpr = 0.7
        corrupt.gpr = 0.3
        corrupt.mean_delta_e = -0.40  # keeps GPR - LPR = mean_delta_e satisfied!
        with pytest.raises(AssertionError, match="does not match count ratio"):
            EPKMetrics.validate_report(corrupt)

        # Negative count
        corrupt = MetricReport(**report.__dict__)
        corrupt.ngd_count = -1
        with pytest.raises(ValueError, match="Count 'ngd_count'"):
            EPKMetrics.validate_report(corrupt)

        # Partition mismatch
        corrupt = MetricReport(**report.__dict__)
        corrupt.zdr_count = report.zdr_count + 1
        with pytest.raises(AssertionError, match="Count partition failed"):
            EPKMetrics.validate_report(corrupt)

        # delta_sum mismatch
        corrupt = MetricReport(**report.__dict__)
        corrupt.delta_sum = True
        with pytest.raises(ValueError, match="delta_sum"):
            EPKMetrics.validate_report(corrupt)

        corrupt = MetricReport(**report.__dict__)
        corrupt.delta_sum = report.delta_sum + 1
        with pytest.raises(AssertionError, match="delta_sum"):
            EPKMetrics.validate_report(corrupt)

        # Pass count gap mismatch
        corrupt = MetricReport(**report.__dict__)
        corrupt.global_pass_count = report.global_pass_count + 1
        with pytest.raises(AssertionError, match="Count gap"):
            EPKMetrics.validate_report(corrupt)

        # egd mismatch
        corrupt = MetricReport(**report.__dict__)
        corrupt.egd = 0.99
        with pytest.raises(AssertionError, match="Rate 'egd'"):
            EPKMetrics.validate_report(corrupt)

        # local_pass_count == 0 cases
        zero_pass = MetricReport(
            sample_size=1, local_pass_count=0, global_pass_count=0, delta_sum=0,
            ngd_count=0, pgd_count=0, zdr_count=1, lpr=0.0, gpr=0.0, mean_delta_e=0.0,
            ngd_all=0.0, pgd=0.0, zdr=1.0, egd=0.0, ngd_cond=0.5
        )
        with pytest.raises(AssertionError, match="ngd_cond must be None"):
            EPKMetrics.validate_report(zero_pass)

        valid_zero_pass = MetricReport(
            sample_size=1, local_pass_count=0, global_pass_count=0, delta_sum=0,
            ngd_count=0, pgd_count=0, zdr_count=1, lpr=0.0, gpr=0.0, mean_delta_e=0.0,
            ngd_all=0.0, pgd=0.0, zdr=1.0, egd=0.0, ngd_cond=None
        )
        EPKMetrics.validate_report(valid_zero_pass)

        # local_pass_count > 0 with ngd_cond is None
        corrupt = MetricReport(**report.__dict__)
        corrupt.ngd_cond = None
        with pytest.raises(AssertionError, match="ngd_cond must not be None"):
            EPKMetrics.validate_report(corrupt)

    @staticmethod
    def _make_synthetic_report(n: int, local: int, global_: int, ngd: int, pgd: int) -> MetricReport:
        return MetricReport(
            sample_size=n,
            lpr=local / n,
            gpr=global_ / n,
            mean_delta_e=(pgd - ngd) / n,
            ngd_all=ngd / n,
            ngd_cond=ngd / local if local else None,
            pgd=pgd / n,
            zdr=(n - ngd - pgd) / n,
            egd=(ngd + pgd) / n,
            ngd_count=ngd,
            pgd_count=pgd,
            zdr_count=n - ngd - pgd,
            local_pass_count=local,
            global_pass_count=global_,
            delta_sum=pgd - ngd,
        )

    @pytest.mark.parametrize("n,local,global_,ngd,pgd", [
        (2, 0, 0, 1, 1),  # Negative local-green/global-green cell.
        (2, 2, 2, 1, 1),  # Negative local-red/global-red cell.
        (4, 1, 1, 2, 2),  # Conditional NGD would be 2.0.
    ])
    def test_impossible_joint_counts_are_rejected(self, n, local, global_, ngd, pgd):
        with pytest.raises((AssertionError, ValueError)):
            EPKMetrics.validate_report(self._make_synthetic_report(n, local, global_, ngd, pgd))

    def test_valid_cancellation_report_is_not_rejected(self):
        # A genuine NGD+PGD pair has one local and one global pass.
        EPKMetrics.validate_report(self._make_synthetic_report(2, 1, 1, 1, 1))

    def test_exhaustive_small_report_realizability(self):
        for n in range(1, 9):
            for ngd in range(n + 1):
                for pgd in range(n - ngd + 1):
                    for local in range(n + 1):
                        global_ = local + pgd - ngd
                        if not 0 <= global_ <= n:
                            continue
                        value = self._make_synthetic_report(n, local, global_, ngd, pgd)
                        realizable = ngd <= local and pgd <= n - local
                        if realizable:
                            EPKMetrics.validate_report(value)
                        else:
                            with pytest.raises((AssertionError, ValueError)):
                                EPKMetrics.validate_report(value)

    def test_additional_branch_coverage(self):
        s0 = State("s0")
        s1 = State("s1")
        s_out = State("s_out")
        b = BoundarySlice([s1])
        l_out = TrajectorySegment(s0, s_out, ("a",), 1.0, 1.0, 1.0, 1.0)
        l_in = TrajectorySegment(s0, s1, ("a",), 1.0, 1.0, 1.0, 1.0)
        r_bad_start = TrajectorySegment(s0, s1, ("b",), 1.0, 1.0, 1.0, 1.0)
        r_good = TrajectorySegment(s1, s0, ("b",), 1.0, 1.0, 1.0, 1.0)
        r_undeclared = TrajectorySegment(s1, s0, ("c",), 1.0, 1.0, 1.0, 1.0)

        # Left segment ends outside boundary (exercises branch)
        b.validate_unique_decomposition([], [l_out], [r_good])

        # Right segment start does not match left segment end (exercises branch)
        b.validate_unique_decomposition([], [l_in], [r_bad_start])

        # Composed trajectory with undeclared right segment
        traj_undeclared_r = ComposedTrajectory(l_in, r_undeclared)
        valid, violations = b.validate_unique_decomposition([traj_undeclared_r], [l_in], [r_good])
        assert not valid

        # Trajectory with NaN metrics in compute_kernel (using object.__setattr__ on frozen segment)
        traj_nan_cost = TrajectorySegment(s0, s1, ("a",), 1.0, 1.0, 1.0, 1.0)
        object.__setattr__(traj_nan_cost, "cost", float("nan"))
        with pytest.raises(ValueError, match="NaN metrics"):
            EvaluatedPathKernel.compute_kernel([traj_nan_cost], lambda t: 1)

    def test_four_term_contribution_nonzero_cases_and_oracle(self):
        # Nonzero PGD case from review verdict
        val_pgd = EvaluatedPathKernel.four_term_contribution(
            e1=0, e2=1, w1=2.0, w2=3.0, delta_e=1, delta_w=5.0
        )
        assert val_pgd == 11.0

        # Accepted ZDR
        val_zdr = EvaluatedPathKernel.four_term_contribution(
            e1=1, e2=1, w1=2.0, w2=3.0, delta_e=0, delta_w=0.0
        )
        assert val_zdr == 6.0

        # Signed negative weight defect
        val_neg_w = EvaluatedPathKernel.four_term_contribution(
            e1=1, e2=1, w1=2.0, w2=3.0, delta_e=0, delta_w=-2.0
        )
        assert val_neg_w == 4.0

        # Exhaustive integer oracle check
        for e1 in (0, 1):
            for e2 in (0, 1):
                for delta_e in (-1, 0, 1):
                    eg = e1 * e2 + delta_e
                    if eg not in (0, 1):
                        continue
                    for w1 in (1.0, 2.0, 3.0):
                        for w2 in (1.0, 2.0, 4.0):
                            for delta_w in (-2.0, 0.0, 3.0):
                                expected = float(eg * (w1 * w2 + delta_w))
                                actual = EvaluatedPathKernel.four_term_contribution(
                                    e1=e1, e2=e2, w1=w1, w2=w2, delta_e=delta_e, delta_w=delta_w
                                )
                                assert actual == pytest.approx(expected)

