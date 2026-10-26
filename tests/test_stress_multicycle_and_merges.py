"""Stress tests for StreamingCochainMonitor and StreamingFiberMonitor.

Covers:
1. Larger multi-cycle communication graphs with heterogeneous rational edge weights
   (parallel multi-edges, self-loops, 8-cycle cactus graphs, coupled diamond graphs
   in both shared-bottleneck and outer-chord pivot regimes, K4 tetrahedral meshes,
   and 6-cycle multi-stage ladder graphs).
2. Asynchronous edge-arrival permutation invariance of global L1 repair distance.
3. Concurrent asynchronous branch merges on StreamingCochainMonitor and
   StreamingFiberMonitor (including cross-branch LGGR discovery from locally
   composable LGGG branches, idempotent at-least-once re-delivery, and
   arrival-order permutation invariance).

Zero external dependencies: Python standard library unittest and fractions only.
AuthorityEffect: None.
"""
from __future__ import annotations

from fractions import Fraction
import itertools
import random
import time
import unittest

from lggr.common import ValidationError
from lggr.streaming import (
    StreamingAdversarialSchemaSideChannelMonitor,
    StreamingAuditMonitor,
    StreamingBaselineComparator,
    StreamingBellPolytopeMonitor,
    StreamingBoundaryQuorumInterfaceMonitor,
    StreamingBoundedDepthKInductionMonitor,
    StreamingCPTPBlindspotCompletionMonitor,
    StreamingCPTPTraceMonitor,
    StreamingCatalystDegradationMonitor,
    StreamingCatalystRejuvenationScheduleMonitor,
    StreamingCoalitionalAttributionMonitor,
    StreamingCoalitionalSynergyMaskingMonitor,
    StreamingCochainMonitor,
    StreamingCodebaseCPTPChannelMonitor,
    StreamingCodebaseCatalystEvolutionMonitor,
    StreamingCodebaseCoalitionalMonitor,
    StreamingCodebaseInterfaceMergeMonitor,
    StreamingCodebaseKInductionMonitor,
    StreamingCodebaseMayerVietorisMonitor,
    StreamingCodebaseOptionalStoppingMonitor,
    StreamingCodebaseReggeHolonomyMonitor,
    StreamingCodebaseReplayOrderMonitor,
    StreamingCodebaseWindowedDriftMonitor,
    StreamingConcurrentLeaseOverlapMonitor,
    StreamingContextualSheafMonitor,
    StreamingCrossRoleDeduplicationMonitor,
    StreamingDFAGrammarGluingMonitor,
    StreamingDFAResetTokenGluingMonitor,
    StreamingDashboardAdequacyMonitor,
    StreamingDeadlinePriorityQueueMonitor,
    StreamingDefectSoundnessMonitor,
    StreamingDiamondCodebasePullbackMonitor,
    StreamingDisagreementPreservingCouncilMonitor,
    StreamingDiscreteCurvatureMonitor,
    StreamingDynamicSchemaSynthesisMonitor,
    StreamingEqualInfoMigrationObligationMonitor,
    StreamingFiberMonitor,
    StreamingFigureEightWedgeHodgeMonitor,
    StreamingGovernedPolicyRelaxationMonitor,
    StreamingGramProbeMonitor,
    StreamingHodgeDecompositionMonitor,
    StreamingLinearizedPipelineJacobianMonitor,
    StreamingMartingaleOptionalStoppingMonitor,
    StreamingMayerVietorisMonitor,
    StreamingMayerVietorisReconciliationMonitor,
    StreamingMinimumSlackPolicyRelaxationMonitor,
    StreamingMultiLoopCupHodgeMonitor,
    StreamingMultiTurnPairwiseTranscriptMonitor,
    StreamingOptionalStoppingDrawdownMonitor,
    StreamingOrganizationalGluingMonitor,
    StreamingOverloadedDeadlineBinPackingMonitor,
    StreamingPathKernelMonitor,
    StreamingPolicyRankingOrderReversalMonitor,
    StreamingPolicyRatchetDriftMonitor,
    StreamingPositiveExtensionMonitor,
    StreamingProductRetractionMonitor,
    StreamingProjectiveTowerMonitor,
    StreamingPullbackMediatorFactorizationMonitor,
    StreamingPullbackSquareMonitor,
    StreamingRSIFiberCeilingMonitor,
    StreamingReggeDeficitCurvatureMonitor,
    StreamingReggeGaussBonnetHolonomyMonitor,
    StreamingReplayOrderEnvelopeMonitor,
    StreamingReplayOrderMonitor,
    StreamingSharedChordDiamondHodgeMonitor,
    StreamingSimplicialCupMonitor,
    StreamingSimultaneousBudgetSplitMonitor,
    StreamingSixRoleOverlayMonitor,
    StreamingStageVsE2EIntegrationMonitor,
    StreamingStatefulCodebaseDFAMonitor,
    StreamingThreePartyConstantBoundMonitor,
    StreamingThresholdGovernanceMonitor,
    StreamingToolAssistedFiberSplittingMonitor,
    StreamingTransportMonitor,
    StreamingVariableDurationGracefulSheddingMonitor,
    StreamingWatcherDropoutGramAuditMonitor,
    StreamingWeightedPolicyRelaxationMonitor,
    StreamingWindowedDriftMonitor,
    StreamingWindowedDriftRebalancingMonitor,
)
from lggr.witnesses import BudgetPolicy, StateRef, StepWitness


class TestStressCochainMultiCycleAndWeights(unittest.TestCase):
    """Stress tests for StreamingCochainMonitor on multi-cycle heterogeneous graphs."""

    def test_parallel_multi_edge_branch_merge_and_self_loop(self) -> None:
        """Parallel edges between Fork and Join with heterogeneous rational weights."""
        mon = StreamingCochainMonitor()
        # Branch 0: Fork -> Join (value 1/2, weight 5/7)
        r0 = mon.add_edge("Fork", "Join", "1/2", weight="5/7")
        self.assertEqual(r0["status"], "OPEN_TREE")

        # Branch 1: Fork -> Join (value 4/3, weight 2/9) -> closes 2-edge parallel cycle
        # Defect = 4/3 - 1/2 = 5/6; min weight = min(5/7, 2/9) = 2/9 -> L1 = 5/27
        r1 = mon.add_edge("Fork", "Join", "4/3", weight="2/9")
        self.assertEqual(r1["status"], "CYCLE_CLOSED")
        self.assertEqual(r1["closure_defect"], Fraction(5, 6))
        self.assertEqual(r1["l1_repair_distance"], Fraction(5, 27))
        self.assertEqual(r1["certificate_status"], "OPTIMALITY_VERIFIED")

        # Branch 2: Fork -> Join (value 1/2, weight 3/11) -> consistent with Branch 0
        r2 = mon.add_edge("Fork", "Join", "1/2", weight="3/11")
        self.assertEqual(r2["status"], "CYCLE_CLOSED")
        self.assertEqual(r2["closure_defect"], Fraction(0))
        self.assertEqual(r2["l1_repair_distance"], Fraction(0))
        self.assertEqual(r2["certificate_status"], "OPTIMALITY_VERIFIED")

        # Self-loop on Join (Join -> Join, value 3/5, weight 4/13)
        r3 = mon.add_edge("Join", "Join", "3/5", weight="4/13")
        self.assertEqual(r3["status"], "CYCLE_CLOSED")
        self.assertEqual(r3["closure_defect"], Fraction(3, 5))
        self.assertEqual(r3["l1_repair_distance"], Fraction(12, 65))
        self.assertEqual(r3["certificate_status"], "OPTIMALITY_VERIFIED")

        # Global multi-cycle L1 repair distance: 5/27 + 0 + 12/65 = 649/1755
        global_res = mon.solve_global_l1_repair()
        self.assertEqual(global_res["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(
            Fraction(global_res["global_l1_repair_distance"]),
            Fraction(5, 27) + Fraction(12, 65),
        )
        self.assertEqual(global_res["certificate"]["duality_gap"], "0")

    def test_eight_cycle_cactus_heterogeneous_prime_weights(self) -> None:
        """8 edge-disjoint cycles with prime-denominator weights sum exactly."""
        mon = StreamingCochainMonitor()
        primes = [3, 5, 7, 11, 13, 17, 19, 23]
        expected_total = Fraction(0)

        for idx, p in enumerate(primes):
            hub = f"H_{idx}"
            a = f"A_{idx}"
            b = f"B_{idx}"
            if idx > 0:
                # Bridge connecting cactus components
                bridge_res = mon.add_edge(f"H_{idx - 1}", hub, Fraction(1, p), weight=Fraction(2, p))
                self.assertEqual(bridge_res["status"], "OPEN_TREE")

            w1 = Fraction(3, p)
            w2 = Fraction(2, p)
            w3 = Fraction(5, p)  # min weight on cycle is w2 = 2/p
            h1 = Fraction(1, p)
            h2 = Fraction(2, p)
            h3 = Fraction(1, 2)  # defect = h3 - (h1 + h2) = 1/2 - 3/p

            mon.add_edge(hub, a, h1, weight=w1)
            mon.add_edge(a, b, h2, weight=w2)
            rc = mon.add_edge(hub, b, h3, weight=w3)
            self.assertEqual(rc["status"], "CYCLE_CLOSED")
            self.assertEqual(rc["certificate_status"], "OPTIMALITY_VERIFIED")

            defect = abs(h3 - (h1 + h2))
            cycle_cost = w2 * defect
            self.assertEqual(rc["l1_repair_distance"], cycle_cost)
            expected_total += cycle_cost

        summary = mon.get_receipt()
        self.assertEqual(summary["status"], "OBSTRUCTED_CYCLE")
        self.assertEqual(summary["cycles_detected"], 8)
        self.assertEqual(summary["global_certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(Fraction(summary["global_l1_repair_distance"]), expected_total)

    def test_coupled_diamond_shared_chord_vs_outer_pivot(self) -> None:
        """Coupled 2-cycle diamond graph in both shared-bottleneck and tree-pivot regimes."""
        # Regime A: Shared diagonal A->C arrives first (entering the spanning forest)
        # with smallest weight (w = 2/7) and value 1.
        # Then both outer paths A->B->C and A->D->C close fundamental cycles of defect -1,
        # each reporting single-cycle repair cost 2/7 (sum = 4/7), while the global solver
        # pivots A->C out of the tree to repair both cycles simultaneously for cost 2/7 < 4/7.
        mon_a = StreamingCochainMonitor()
        mon_a.add_edge("A", "C", 1, weight="2/7")
        mon_a.add_edge("A", "B", 0, weight="5/7")
        c1_a = mon_a.add_edge("B", "C", 0, weight="3/5")
        mon_a.add_edge("A", "D", 0, weight="4/5")
        c2_a = mon_a.add_edge("D", "C", 0, weight="2/3")

        self.assertEqual(c1_a["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(c2_a["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(c1_a["l1_repair_distance"], Fraction(2, 7))
        self.assertEqual(c2_a["l1_repair_distance"], Fraction(2, 7))
        glob_a = mon_a.solve_global_l1_repair()
        self.assertEqual(glob_a["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(glob_a["certificate"]["duality_gap"], "0")
        # Strictly less than sum of individual fundamental cycle costs (2/7 + 2/7 = 4/7)
        self.assertEqual(Fraction(glob_a["global_l1_repair_distance"]), Fraction(2, 7))
        self.assertLess(
            Fraction(glob_a["global_l1_repair_distance"]),
            c1_a["l1_repair_distance"] + c2_a["l1_repair_distance"],
        )

        # Regime B: Shared diagonal A->C is heavy (w = 5), while outer edges B->C (w = 1/3)
        # and D->C (w = 1/5) are light. Optimal global repair keeps A->C in the tree
        # and repairs B->C and D->C for total cost 1/3 + 1/5 = 8/15.
        mon_b = StreamingCochainMonitor()
        mon_b.add_edge("A", "B", 0, weight=2)
        mon_b.add_edge("B", "C", 0, weight="1/3")
        mon_b.add_edge("A", "C", 1, weight=5)
        mon_b.add_edge("B", "D", 0, weight=2)
        mon_b.add_edge("D", "C", 0, weight="1/5")

        glob_b = mon_b.solve_global_l1_repair()
        self.assertEqual(glob_b["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(glob_b["certificate"]["duality_gap"], "0")
        self.assertEqual(
            Fraction(glob_b["global_l1_repair_distance"]),
            Fraction(1, 3) + Fraction(1, 5),
        )

    def test_coupled_k4_tetrahedral_mesh_and_arrival_permutation_invariance(self) -> None:
        """K4 complete 4-agent mesh (6 edges, b1 = 3 coupled cycles) across 20 arrival orders."""
        edges = [
            ("N0", "N1", Fraction(1, 2), Fraction(7, 5)),
            ("N1", "N2", Fraction(1, 3), Fraction(4, 3)),
            ("N2", "N3", Fraction(-1, 4), Fraction(9, 7)),
            ("N0", "N2", Fraction(3, 2), Fraction(2, 5)),
            ("N1", "N3", Fraction(-1, 2), Fraction(3, 11)),
            ("N0", "N3", Fraction(5, 6), Fraction(5, 13)),
        ]

        rng = random.Random(20261024)
        reference_cost: Fraction | None = None

        for trial in range(20):
            shuffled = list(edges)
            if trial > 0:
                rng.shuffle(shuffled)
            mon = StreamingCochainMonitor()
            closed_count = 0
            for u, v, val, wt in shuffled:
                res = mon.add_edge(u, v, val, weight=wt)
                if res["cycle_detected"]:
                    closed_count += 1
                    self.assertEqual(res["certificate_status"], "OPTIMALITY_VERIFIED")
            self.assertEqual(closed_count, 3)

            glob = mon.solve_global_l1_repair()
            self.assertEqual(glob["certificate_status"], "OPTIMALITY_VERIFIED")
            self.assertEqual(glob["certificate"]["duality_gap"], "0")
            cost = Fraction(glob["global_l1_repair_distance"])
            if reference_cost is None:
                reference_cost = cost
            else:
                self.assertEqual(cost, reference_cost)

    def test_six_cycle_ladder_graph_heterogeneous_weights(self) -> None:
        """6-cycle multi-stage ladder graph (14 vertices, 19 edges, b1 = 6 coupled cycles)."""
        mon = StreamingCochainMonitor()
        # 7 rungs: L_i -> R_i for i = 0..6, plus rails L_i -> L_{i+1} and R_i -> R_{i+1}
        for i in range(7):
            rung_w = Fraction(10 + i, 3)
            rung_h = Fraction((-1) ** i, i + 2)
            r_rung = mon.add_edge(f"L_{i}", f"R_{i}", rung_h, weight=rung_w)
            if i == 0:
                self.assertEqual(r_rung["status"], "OPEN_TREE")

            if i > 0:
                rail_l_w = Fraction(5, i + 1)
                rail_r_w = Fraction(1, 2 * i + 1)  # light right rail chord
                mon.add_edge(f"L_{i - 1}", f"L_{i}", Fraction(1, 3), weight=rail_l_w)
                r_close = mon.add_edge(f"R_{i - 1}", f"R_{i}", Fraction(1, 5), weight=rail_r_w)
                self.assertEqual(r_close["status"], "CYCLE_CLOSED")
                self.assertEqual(r_close["certificate_status"], "OPTIMALITY_VERIFIED")

        summary = mon.get_receipt()
        self.assertEqual(summary["cycles_detected"], 6)
        self.assertEqual(summary["global_certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertGreater(Fraction(summary["global_l1_repair_distance"]), Fraction(0))

    def test_concurrent_branch_cochain_merge(self) -> None:
        """Two locally acyclic branch cochain monitors close frustrated cycles upon merge."""
        branch_left = StreamingCochainMonitor()
        branch_left.add_edge("Root", "Mid_1", "1/2", weight="3/4")
        branch_left.add_edge("Mid_1", "Join_A", "1/4", weight="2/3")
        branch_left.add_edge("Mid_1", "Join_B", "2/3", weight="5/6")
        self.assertEqual(branch_left.get_receipt()["status"], "OPEN_TREE")

        branch_right = StreamingCochainMonitor()
        branch_right.add_edge("Root", "Mid_2", "1/3", weight="4/5")
        branch_right.add_edge("Mid_2", "Join_A", "1/6", weight="1/5")
        branch_right.add_edge("Mid_2", "Join_B", "1/3", weight="3/7")
        self.assertEqual(branch_right.get_receipt()["status"], "OPEN_TREE")

        merge_receipt = branch_left.merge(branch_right)
        self.assertEqual(merge_receipt["schema"], "lggr.online_cochain_merge.v1")
        self.assertEqual(merge_receipt["merged_edges_count"], 3)
        self.assertEqual(merge_receipt["new_cycles_closed"], 2)
        self.assertEqual(merge_receipt["new_nonrepairable_cycles"], 2)
        self.assertEqual(merge_receipt["status"], "OBSTRUCTED_CYCLE")
        self.assertEqual(merge_receipt["global_certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertGreater(Fraction(merge_receipt["global_l1_repair_distance"]), Fraction(0))


class TestStressFiberConcurrentBranchMerges(unittest.TestCase):
    """Stress tests for StreamingFiberMonitor under concurrent asynchronous branch merges."""

    def test_four_locally_green_branches_discover_cross_branch_lggr_on_merge(self) -> None:
        """Four branches are each COMPOSABLE_LGGG in isolation but collide on merge."""
        branches = [StreamingFiberMonitor(scope_id=f"branch_{b}") for b in range(4)]

        # Each branch observes 25 states; within each branch, reports are fiber-constant
        for b_idx, mon in enumerate(branches):
            for k in range(24):
                res = mon.observe(
                    f"b{b_idx}_s{k}",
                    report={"branch_group": k % 6, "schema": "v1"},
                    query={"safe": (k % 2 == 0)},
                )
                self.assertEqual(res["status"], "OK")
            # Shared boundary report across branches 1 and 3 with conflicting query
            shared_query = {"safe": True} if b_idx != 3 else {"safe": False}
            res_last = mon.observe(
                f"b{b_idx}_shared_handoff",
                report={"handoff_tag": "underspecified_summary", "local_green": True},
                query=shared_query,
            )
            self.assertEqual(res_last["status"], "OK")
            self.assertFalse(mon.is_obstructed)
            self.assertEqual(mon.get_receipt()["contract_status"], "COMPOSABLE_LGGG")

        # Coordinator merges branches 0, 1, 2 -> still COMPOSABLE_LGGG
        coordinator = StreamingFiberMonitor(scope_id="swarm_coordinator")
        for b_idx in (0, 1, 2):
            m_res = coordinator.merge(branches[b_idx])
            self.assertEqual(m_res["contract_status"], "COMPOSABLE_LGGG")
            self.assertFalse(m_res["cross_branch_lggr_discovered"])

        # Merging branch 3 triggers cross-branch LGGR discovery
        m_res_3 = coordinator.merge(branches[3])
        self.assertEqual(m_res_3["schema"], "lggr.online_branch_merge.v1")
        self.assertTrue(m_res_3["cross_branch_lggr_discovered"])
        self.assertEqual(m_res_3["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(m_res_3["contract_status"], "OBSTRUCTED_LGGR")
        self.assertIsNotNone(m_res_3["colliding_pair"])

    def test_asynchronous_interleaving_permutation_invariance_and_idempotency(self) -> None:
        """All 24 branch arrival permutations yield identical decoder or collision status."""
        branch_streams = [
            [
                (f"b0_{i}", {"stage": "parse", "bucket": i % 3}, {"ok": (i % 3) != 2})
                for i in range(10)
            ],
            [
                (f"b1_{i}", {"stage": "typecheck", "bucket": i % 4}, {"ok": (i % 4) == 0})
                for i in range(10)
            ],
            [
                (f"b2_{i}", {"stage": "verify", "bucket": i % 5}, {"ok": True})
                for i in range(10)
            ],
            [
                (f"b3_{i}", {"stage": "emit", "bucket": i % 2}, {"ok": (i % 2) == 1})
                for i in range(10)
            ],
        ]

        baseline_decoder = None
        for perm in itertools.permutations(range(4)):
            mon = StreamingFiberMonitor(scope_id="perm_lggg")
            # Interleave observations round-robin across the permuted branch order
            for step_i in range(10):
                for b_idx in perm:
                    sid, rep, qry = branch_streams[b_idx][step_i]
                    res = mon.observe(sid, rep, qry)
                    self.assertEqual(res["status"], "OK")
                    # Simulate at-least-once duplicate message re-delivery on even steps
                    if step_i % 2 == 0:
                        dup_res = mon.observe(sid, rep, qry)
                        self.assertEqual(dup_res["status"], "OK")

            receipt = mon.get_receipt()
            self.assertEqual(receipt["status"], "DECODER_VERIFIED")
            self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
            self.assertEqual(receipt["carrier_size"], 40)
            if baseline_decoder is None:
                baseline_decoder = receipt["decoder"]
            else:
                self.assertEqual(receipt["decoder"], baseline_decoder)

    def test_conflicting_reobservation_across_branch_merge_rejected(self) -> None:
        """Conflicting state_id payload during branch merge raises ValidationError."""
        b1 = StreamingFiberMonitor(scope_id="b1")
        b2 = StreamingFiberMonitor(scope_id="b2")
        b1.observe("shared_state_id", {"r": 1}, {"q": 1})
        b2.observe("shared_state_id", {"r": 1}, {"q": 2})

        with self.assertRaises(ValidationError):
            b1.merge(b2)


class TestHigherGenusLatencyAndPivots(unittest.TestCase):
    """Benchmark runtime latency and pivot counts on higher-genus graphs (b_1 >= 25)
    with adversarial weight degeneracies.
    """

    def test_k9_complete_graph_b1_28_adversarial_weight_ties(self) -> None:
        """Complete directed graph K9 (|V|=9, |E|=36, b_1=28) with 3-tier tied weights."""
        mon = StreamingCochainMonitor()
        # Adversarial tied weights from {1/3, 1/2, 1} and frustrated cochain values
        tied_weights = [Fraction(1, 3), Fraction(1, 2), Fraction(1, 1)]
        edge_idx = 0
        for i in range(9):
            for j in range(i + 1, 9):
                wt = tied_weights[(i + j) % 3]
                # Perturb edge values on chords to create coupled frustration + zero-residual ties
                val = Fraction((i - j) % 4 - 1, 2) if (i + j) % 2 == 0 else Fraction(0)
                mon.add_edge(f"V_{i}", f"V_{j}", val, weight=wt)
                edge_idx += 1

        self.assertEqual(len(mon.edges), 36)
        self.assertEqual(len(mon.cycles), 28)  # b_1 = 36 - 9 + 1 = 28 >= 25

        t0 = time.perf_counter()
        glob = mon.solve_global_l1_repair()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(glob["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(glob["certificate"]["duality_gap"], "0")
        self.assertGreaterEqual(glob["pivots_count"], 0)
        self.assertLess(elapsed_ms, 5000.0)
        self.assertGreater(Fraction(glob["global_l1_repair_distance"]), Fraction(0))

    def test_toroidal_grid_6x6_b1_37_degenerate_chords(self) -> None:
        """6x6 torus grid (|V|=36, |E|=72, b_1=37) with uniform/degenerate rational weights."""
        mon = StreamingCochainMonitor()
        rows, cols = 6, 6
        for r in range(rows):
            for c in range(cols):
                u = f"N_{r}_{c}"
                v_right = f"N_{r}_{(c + 1) % cols}"
                v_down = f"N_{(r + 1) % rows}_{c}"
                # Adversarial degenerate weights: many identical weights 1/2 and 1/4
                w_h = Fraction(1, 2) if (r + c) % 2 == 0 else Fraction(1, 4)
                w_v = Fraction(1, 2) if (r * c) % 2 == 0 else Fraction(1, 4)
                # Inject localized vortex defects at 6 plaquettes; zero elsewhere (high degeneracy)
                h_right = Fraction(1, 3) if (r == c) else Fraction(0)
                h_down = Fraction(-1, 5) if (r + c == 5) else Fraction(0)
                mon.add_edge(u, v_right, h_right, weight=w_h)
                mon.add_edge(u, v_down, h_down, weight=w_v)

        self.assertEqual(len(mon.edges), 72)
        self.assertEqual(len(mon.cycles), 37)  # b_1 = 72 - 36 + 1 = 37 >= 25

        t0 = time.perf_counter()
        glob = mon.solve_global_l1_repair()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(glob["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(glob["certificate"]["duality_gap"], "0")
        self.assertGreaterEqual(glob["pivots_count"], 0)
        self.assertLess(elapsed_ms, 5000.0)
        self.assertGreater(Fraction(glob["global_l1_repair_distance"]), Fraction(0))

    def test_adversarial_forced_multi_pivot_dense_b1_30(self) -> None:
        """Dense graph (b_1 = 30) where heavy spanning tree is non-optimal and forces cut pivots."""
        mon = StreamingCochainMonitor()
        # Spine of 10 vertices S_0 -> S_1 -> ... -> S_9 with weight 1 (total 9 edges)
        for i in range(9):
            mon.add_edge(f"S_{i}", f"S_{i + 1}", 0, weight=1)

        # Add 30 chords across the spine (b_1 = 30):
        # 20 chords bridging S_0 -> S_9 through shared intermediate hubs with weight 2/5 and value 1
        for k in range(30):
            u_idx = k % 4
            v_idx = 9 - (k % 3)
            wt = Fraction(2, 5) if k % 2 == 0 else Fraction(3, 10)
            val = Fraction(1) if k < 20 else Fraction(-1, 2)
            mon.add_edge(f"S_{u_idx}", f"S_{v_idx}", val, weight=wt)

        self.assertEqual(len(mon.cycles), 30)  # b_1 = 30 >= 25

        t0 = time.perf_counter()
        glob = mon.solve_global_l1_repair()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(glob["certificate_status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(glob["certificate"]["duality_gap"], "0")
        # Here the 30 light chords overpower the weight-1 spine edges, forcing > 0 min-cut pivots!
        self.assertGreater(glob["pivots_count"], 0)
        self.assertLess(elapsed_ms, 5000.0)


class TestStreamingTwoCellCohomology(unittest.TestCase):
    """Online 2-cell coboundary vs. first cohomology H^1 classification."""

    def test_filled_triangle_closure_failure_vs_exact(self) -> None:
        """Filled 2-cell detects local closure failure (D1 h != 0) vs exact coboundary."""
        mon = StreamingCochainMonitor()
        # Register 2-cell before all edges arrive -> PENDING_EDGES
        r_pending = mon.add_two_cell(
            "face_012",
            [("V0", "V1", 1), ("V1", "V2", 1), ("V0", "V2", -1)],
        )
        self.assertEqual(r_pending["status"], "PENDING_EDGES")
        self.assertFalse(r_pending["complete_edges"])

        mon.add_edge("V0", "V1", "1/2")
        mon.add_edge("V1", "V2", "1/2")
        mon.add_edge("V0", "V2", "1/3")  # D1 h = 1/2 + 1/2 - 1/3 = 2/3 != 0

        coh = mon.classify_streaming_cohomology()
        self.assertEqual(coh["status"], "CLOSURE_FAILURE")
        self.assertFalse(coh["repair_exists"])
        self.assertFalse(coh["represents_nonzero_H1"])

    def test_closed_nonexact_cohomology_around_unfilled_hole(self) -> None:
        """Filled triangle (D1 h = 0) glued to unfilled loop (h not in im(D0)) -> CLOSED_NONEXACT."""
        mon = StreamingCochainMonitor()
        # Triangle (V0, V1, V2) has exact/closed values: h01 = 0, h12 = 0, h02 = 0
        mon.add_edge("V0", "V1", 0)
        mon.add_edge("V1", "V2", 0)
        mon.add_edge("V0", "V2", 0)
        # Unfilled loop (V0, V2, V3) has nonzero circulation: h23 = 1, h03 = 0
        mon.add_edge("V2", "V3", 1)
        mon.add_edge("V0", "V3", 0)

        # Declare the filled 2-cell on Triangle (V0, V1, V2) ONLY; loop (V0, V2, V3) is unfilled
        r_cell = mon.add_two_cell(
            "filled_triangle_012",
            [("V0", "V1", 1), ("V1", "V2", 1), ("V0", "V2", -1)],
        )
        self.assertEqual(r_cell["status"], "CELL_CLOSED")
        self.assertEqual(r_cell["coboundary_value"], "0")

        coh = mon.classify_streaming_cohomology()
        self.assertEqual(coh["status"], "CLOSED_NONEXACT")
        self.assertFalse(coh["repair_exists"])
        self.assertTrue(coh["represents_nonzero_H1"])
        self.assertEqual(coh["closure"], ["0"])

    def test_invalid_two_cell_boundary_detected(self) -> None:
        """Open path declared as a 2-cell boundary violates D1 D0 = 0 -> INVALID_COMPLEX."""
        mon = StreamingCochainMonitor()
        mon.add_edge("V0", "V1", 1)
        mon.add_edge("V1", "V2", 1)
        r_bad = mon.add_two_cell("open_path", [("V0", "V1", 1), ("V1", "V2", 1)])
        self.assertEqual(r_bad["status"], "INVALID_COMPLEX")
        self.assertEqual(mon.classify_streaming_cohomology()["status"], "INVALID_COMPLEX")


class TestStreamingTransportMonitor(unittest.TestCase):
    """Online chain-retraction vs. lossy coarse-graining projection tests."""

    def test_lossy_chord_dropping_projection_masks_cycle_obstruction(self) -> None:
        """Dropping the closing chord maps an obstructed 3-cycle onto a repairable 2-edge tree."""
        src = StreamingCochainMonitor()
        src.add_edge("V0", "V1", 1)
        src.add_edge("V1", "V2", 1)
        src.add_edge("V0", "V2", 1)  # frustrated cycle: 1 + 1 != 1

        tgt = StreamingCochainMonitor()
        tgt.add_edge("V0", "V1", 1)
        tgt.add_edge("V1", "V2", 1)  # open 2-edge tree

        tmon = StreamingTransportMonitor(src, tgt)
        # F0 = I_3 (3 vertices -> 3 vertices), F1 drops edge 2 (the closing chord V0->V2)
        f0 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        f1 = [[1, 0, 0], [0, 1, 0]]
        res = tmon.audit_projection(f0, f1)

        self.assertEqual(res["status"], "LOSSY_PROJECTION_LGGR")
        self.assertEqual(res["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(res["forward_commutes"])
        self.assertFalse(res["source_repairable"])
        self.assertTrue(res["target_repairable"])
        self.assertTrue(res["lossy_projection_lggr"])

    def test_faithful_retraction_reflects_source_obstruction(self) -> None:
        """Faithful chain retraction (G1 F1 = I, G0 F0 = I) reflects cycle nonrepairability."""
        src = StreamingCochainMonitor()
        src.add_edge("V0", "V1", 1)
        src.add_edge("V1", "V2", 1)
        src.add_edge("V0", "V2", 1)  # frustrated 3-cycle

        tgt = StreamingCochainMonitor()
        tgt.add_edge("V0", "V1", 1)
        tgt.add_edge("V1", "V2", 1)
        tgt.add_edge("V0", "V2", 1)
        tgt.add_edge("V2", "V3", 0)  # extra leaf edge in target

        tmon = StreamingTransportMonitor(src, tgt)
        # F0 embeds (V0, V1, V2) -> (V0, V1, V2, V3=V2) so D_t F0 on edge (V2->V3) is 0
        f0 = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]]
        f1 = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]
        g0 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]
        g1 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]

        res = tmon.audit_projection(f0, f1, G0=g0, G1=g1)
        self.assertEqual(res["status"], "RETRACTION_VERIFIED")
        self.assertEqual(res["contract_status"], "REFLECTED_LGGR")
        self.assertTrue(res["nonrepairability_reflection_verified"])
        self.assertFalse(res["source_repairable"])
        self.assertFalse(res["target_repairable"])
        self.assertFalse(res["lossy_projection_lggr"])

    def test_synthesize_chain_retraction_success_and_impossibility(self) -> None:
        """Synthesize exact rational chain retraction (G0, G1) when injective, or reject when lossy."""
        src = StreamingCochainMonitor()
        src.add_edge("V0", "V1", 1)
        src.add_edge("V1", "V2", 1)
        src.add_edge("V0", "V2", 1)  # frustrated 3-cycle

        # Case 1: Lossy projection onto 2-edge tree -> NO_RETRACTION_EXISTS
        tgt_lossy = StreamingCochainMonitor()
        tgt_lossy.add_edge("V0", "V1", 1)
        tgt_lossy.add_edge("V1", "V2", 1)
        tmon_lossy = StreamingTransportMonitor(src, tgt_lossy)
        f0_lossy = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        f1_lossy = [[1, 0, 0], [0, 1, 0]]
        syn_lossy = tmon_lossy.synthesize_chain_retraction(f0_lossy, f1_lossy)
        self.assertEqual(syn_lossy["status"], "NO_RETRACTION_EXISTS")
        self.assertFalse(syn_lossy["retraction_exists"])
        self.assertIsNone(syn_lossy["G0"])
        self.assertIsNone(syn_lossy["G1"])
        self.assertEqual(syn_lossy["audit"]["status"], "LOSSY_PROJECTION_LGGR")

        # Case 2: Faithful embedding into 4-vertex, 4-edge graph -> RETRACTION_SYNTHESIZED
        tgt_faithful = StreamingCochainMonitor()
        tgt_faithful.add_edge("V0", "V1", 1)
        tgt_faithful.add_edge("V1", "V2", 1)
        tgt_faithful.add_edge("V0", "V2", 1)
        tgt_faithful.add_edge("V2", "V3", 0)
        tmon_faithful = StreamingTransportMonitor(src, tgt_faithful)
        f0_faith = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]]
        f1_faith = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]
        syn_faith = tmon_faithful.synthesize_chain_retraction(f0_faith, f1_faith)
        self.assertEqual(syn_faith["status"], "RETRACTION_SYNTHESIZED")
        self.assertTrue(syn_faith["retraction_exists"])
        self.assertIsNotNone(syn_faith["G0"])
        self.assertIsNotNone(syn_faith["G1"])
        self.assertEqual(syn_faith["audit"]["status"], "RETRACTION_VERIFIED")
        self.assertEqual(syn_faith["audit"]["contract_status"], "REFLECTED_LGGR")


class TestStreamingPositiveExtensionMonitor(unittest.TestCase):
    """Online observer-fiber minimax error floor and positive-extension order reversal tests."""

    def test_online_observer_fiber_minimax_floor_monotonicity(self) -> None:
        """Minimax error floor and midpoint estimator update monotonically on indistinguishable fibers."""
        pmon = StreamingPositiveExtensionMonitor()

        r1 = pmon.observe_target("s1", {"report_tag": "green"}, Fraction(2))
        self.assertEqual(r1["fiber_minimax_error_floor"], "0")
        self.assertEqual(r1["fiber_midpoint_estimator"], "2")
        self.assertEqual(r1["status"], "EXACT_FIBER_DECODER")
        self.assertEqual(r1["contract_status"], "COMPOSABLE_LGGG")

        r2 = pmon.observe_target("s2", {"report_tag": "green"}, Fraction(8))
        self.assertEqual(r2["fiber_minimax_error_floor"], "3")
        self.assertEqual(r2["fiber_midpoint_estimator"], "5")
        self.assertEqual(r2["global_minimax_error_floor"], "3")
        self.assertEqual(r2["status"], "NONZERO_MINIMAX_FLOOR")
        self.assertEqual(r2["contract_status"], "OBSTRUCTED_LGGR")

        # Interior state s3 with target 5 preserves the minimax floor at 3
        r3 = pmon.observe_target("s3", {"report_tag": "green"}, Fraction(5))
        self.assertEqual(r3["fiber_minimax_error_floor"], "3")
        self.assertEqual(r3["fiber_midpoint_estimator"], "5")

        # Wider state s4 with target 11 increases the minimax floor to (11 - 2) / 2 = 9/2
        r4 = pmon.observe_target("s4", {"report_tag": "green"}, Fraction(11))
        self.assertEqual(r4["fiber_minimax_error_floor"], "9/2")
        self.assertEqual(r4["fiber_midpoint_estimator"], "13/2")
        self.assertEqual(pmon.get_receipt()["global_minimax_error_floor"], "9/2")

    def test_ghz_rnd2_vs_mermin_q58_order_reversal(self) -> None:
        """Certify CF > 2 * N_min at p_* (GHZ rnd2) and strict order reversal against Q_{5/8}."""
        pmon = StreamingPositiveExtensionMonitor()

        # p_* (GHZ rnd2, 8 contexts): local packing = 540/768 = 45/64 -> CF = 19/64, N_min = 75/768 = 25/256
        res_pstar = pmon.audit_signed_extension(
            "ghz_rnd2_pstar",
            num_contexts=8,
            local_packing_mass=Fraction(540, 768),
            negative_mass=Fraction(75, 768),
        )
        self.assertEqual(res_pstar["status"], "CF_EXCEEDS_TWO_NEG_MASS")
        self.assertEqual(res_pstar["contextual_fraction"], "19/64")
        self.assertEqual(res_pstar["negative_mass"], "25/256")
        self.assertTrue(res_pstar["excess_identity_verified"])
        self.assertTrue(res_pstar["m_context_bound_verified"])
        self.assertTrue(res_pstar["exceeds_two_negative_mass"])

        # Mermin isotropic state Q_{5/8} (4 contexts): local packing = 3/4 -> CF = 1/4, N_min = 1/8
        res_q58 = pmon.audit_signed_extension(
            "mermin_q58",
            num_contexts=4,
            local_packing_mass=Fraction(576, 768),
            negative_mass=Fraction(96, 768),
        )
        self.assertEqual(res_q58["status"], "EXTENSION_BOUND_VERIFIED")
        self.assertEqual(res_q58["contextual_fraction"], "1/4")
        self.assertEqual(res_q58["negative_mass"], "1/8")

        cmp_res = pmon.compare_extension_order("mermin_q58", "ghz_rnd2_pstar")
        self.assertEqual(cmp_res["status"], "ORDER_REVERSAL_DETECTED")
        self.assertTrue(cmp_res["order_reversal_detected"])

    def test_cli_stream_minimax_mode_and_selftest(self) -> None:
        """Exercise CLI stream --monitor minimax and selftest entry points."""
        import io
        from contextlib import redirect_stdout
        from lggr.__main__ import main, run_selftest

        st = run_selftest()
        self.assertEqual(st["status"], "PASS")
        self.assertEqual(st["details"]["streaming"], "PASS")

        # Nonzero minimax floor exits with 1 (OBSTRUCTED_LGGR)
        import tempfile
        import os
        import json

        events = [
            {"state_id": "s1", "report": {"tag": "ok"}, "target_value": 2},
            {"state_id": "s2", "report": {"tag": "ok"}, "target_value": 6},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
            for ev in events:
                tf.write(json.dumps(ev) + "\n")
            tpath = tf.name
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["stream", "--monitor", "minimax", tpath])
            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["monitor"], "minimax")
            self.assertEqual(out["status"], "OBSTRUCTED_LGGR")
            self.assertEqual(out["final_receipt"]["global_minimax_error_floor"], "2")
        finally:
            os.remove(tpath)


class TestStreamingAuditBranchSplice(unittest.TestCase):
    """Cross-branch witness splicing tests for StreamingAuditMonitor.merge()."""

    def test_two_locally_green_stage_traces_breach_budget_on_splice(self) -> None:
        """Two sub-traces each have |Delta| = 2 <= 3 (COMPOSABLE_LGGG) but splice to |Delta| = 4 > 3."""
        policy = BudgetPolicy(
            policy_id="splice-policy",
            max_step=2,
            max_total=3,
            allowed_states=tuple(range(-10, 11)),
            query_scope="every_prefix",
            evaluator_id="bounded-step/v1",
            spec_id="cumulative-budget/v1",
            representation_id="integer-state/v1",
            authority_id="external-owner/v1",
        )
        s0 = StateRef("S0", 0)
        s1 = StateRef("S1", 2)
        s2 = StateRef("S2", 4)

        w1 = StepWitness(
            witness_id="w_stage1",
            source=s0,
            target=s1,
            observed_magnitude=2,
            local_accepted=True,
            smoke_passed=True,
            policy_sha256=policy.sha256,
        )
        w2 = StepWitness(
            witness_id="w_stage2",
            source=s1,
            target=s2,
            observed_magnitude=2,
            local_accepted=True,
            smoke_passed=True,
            policy_sha256=policy.sha256,
        )

        mon_upstream = StreamingAuditMonitor(policy, baseline=s0)
        mon_upstream.step(w1)
        self.assertEqual(mon_upstream.get_receipt()["contract_status"], "COMPOSABLE_LGGG")

        mon_downstream = StreamingAuditMonitor(policy, baseline=s1)
        mon_downstream.step(w2)
        self.assertEqual(mon_downstream.get_receipt()["contract_status"], "COMPOSABLE_LGGG")

        merge_res = mon_upstream.merge(mon_downstream)
        self.assertFalse(merge_res["target_was_obstructed"])
        self.assertFalse(merge_res["source_was_obstructed"])
        self.assertTrue(merge_res["cross_branch_lggr_discovered"])
        self.assertEqual(merge_res["cumulative_delta"], 4)
        self.assertEqual(merge_res["contract_status"], "OBSTRUCTED_LGGR")

    def test_coarsened_macro_stage_masks_internal_prefix_breach(self) -> None:
        """Grouping steps [1, 2] on trajectory (0 -> 1 -> 3 -> 1) with B=2 detects masked excursion."""
        policy = BudgetPolicy(
            policy_id="coarsen-policy",
            max_step=2,
            max_total=2,
            allowed_states=tuple(range(-10, 11)),
            query_scope="every_prefix",
            evaluator_id="bounded-step/v1",
            spec_id="cumulative-budget/v1",
            representation_id="integer-state/v1",
            authority_id="external-owner/v1",
        )
        s0 = StateRef("S0", 0)
        s1 = StateRef("S1", 1)
        s2 = StateRef("S2", 3)
        s3 = StateRef("S3", 1)

        mon = StreamingAuditMonitor(policy, baseline=s0)
        mon.step(StepWitness(
            witness_id="w_c1", source=s0, target=s1, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        ))
        mon.step(StepWitness(
            witness_id="w_c2", source=s1, target=s2, observed_magnitude=2,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        ))
        mon.step(StepWitness(
            witness_id="w_c3", source=s2, target=s3, observed_magnitude=2,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        ))

        # Coarsening steps 2 and 3 into a single macro-stage [1, 2] hides step index 1 (delta=3 > 2)
        coarse_res = mon.audit_coarsened_partition([1, 2])
        self.assertEqual(coarse_res["status"], "COARSENED_EXCURSION_MASKED")
        self.assertEqual(coarse_res["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(coarse_res["fine_prefix_breach"])
        self.assertFalse(coarse_res["coarse_prefix_breach"])
        self.assertTrue(coarse_res["hidden_excursion_masked"])
        self.assertEqual(coarse_res["fine_breach_step_indices"], [1])

        # Fine partition [1, 1, 1] exposes the breach at macro boundary 1
        fine_res = mon.audit_coarsened_partition([1, 1, 1])
        self.assertEqual(fine_res["status"], "COARSENING_PRESERVES_VERDICT")
        self.assertTrue(fine_res["coarse_prefix_breach"])
        self.assertFalse(fine_res["hidden_excursion_masked"])

    def test_synthesize_minimal_refinement_resolves_or_refuses_collision(self) -> None:
        """Synthesize minimal metadata key subset that restores report-fiber sufficiency."""
        fmon = StreamingFiberMonitor(scope_id="schema-refine-test")
        # Both states share base report {"workload": "etl"}, collide on query,
        # have identical metadata "region": "us-east", and differ on metadata "kms_tier"
        fmon.observe(
            "t1",
            report={"workload": "etl"},
            query={"approved": True},
            metadata={"region": "us-east", "kms_tier": "tier-3"},
        )
        fmon.observe(
            "t2",
            report={"workload": "etl"},
            query={"approved": False},
            metadata={"region": "us-east", "kms_tier": "tier-1"},
        )
        self.assertTrue(fmon.is_obstructed)

        # Inspecting all metadata keys finds minimal 1-key refinement ["kms_tier"]
        syn = fmon.synthesize_minimal_refinement()
        self.assertEqual(syn["status"], "REFINEMENT_SYNTHESIZED")
        self.assertTrue(syn["refinement_found"])
        self.assertEqual(syn["minimal_keys"], ["kms_tier"])
        self.assertEqual(syn["refined_contract_status"], "COMPOSABLE_LGGG")

        # Restricting candidate keys to ["region"] only -> REFINEMENT_INSUFFICIENT
        syn_bad = fmon.synthesize_minimal_refinement(candidate_keys=["region"])
        self.assertEqual(syn_bad["status"], "REFINEMENT_INSUFFICIENT")
        self.assertFalse(syn_bad["refinement_found"])
        self.assertIsNone(syn_bad["minimal_keys"])
        self.assertEqual(syn_bad["refined_contract_status"], "OBSTRUCTED_LGGR")


class TestStreamingBaselineComparator(unittest.TestCase):
    """Equal-information comparative benchmark: conventional baseline vs. LGGR audit."""

    def test_comparative_evaluation_across_excursions_migrations_and_obligations(self) -> None:
        """Compare conventional local+endpoint checker against LGGR across 4 trace classes."""
        policy = BudgetPolicy(
            policy_id="comp-policy",
            max_step=1,
            max_total=1,
            allowed_states=(-2, -1, 0, 1, 2),
            query_scope="every_prefix",
            evaluator_id="bounded-step/v1",
            spec_id="cumulative-budget/v1",
            representation_id="integer-state/v1",
            authority_id="external-owner/v1",
        )
        comp = StreamingBaselineComparator(policy)
        s0 = StateRef("S0", 0)
        s1 = StateRef("S1", 1)
        s2 = StateRef("S2", 2)
        s3 = StateRef("S3", 1)

        # 1. Valid trace (S0=0 -> S1=1): both accept
        w_ok = StepWitness(
            witness_id="w_ok", source=s0, target=s1, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        )
        r_good = comp.compare_trace("trace_valid", s0, [w_ok])
        self.assertEqual(r_good["status"], "AGREEMENT_VERIFIED")
        self.assertTrue(r_good["conventional_accepts"])
        self.assertTrue(r_good["lggr_accepts"])
        self.assertFalse(r_good["conventional_false_acceptance"])

        # 2. Mid-flight prefix excursion (0 -> 1 -> 2 -> 1): conventional falsely accepts, LGGR localizes step 1
        w_ex1 = StepWitness(
            witness_id="w_ex1", source=s0, target=s1, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        )
        w_ex2 = StepWitness(
            witness_id="w_ex2", source=s1, target=s2, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        )
        w_ex3 = StepWitness(
            witness_id="w_ex3", source=s2, target=s3, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
        )
        r_exc = comp.compare_trace("trace_prefix_excursion", s0, [w_ex1, w_ex2, w_ex3])
        self.assertEqual(r_exc["status"], "CONVENTIONAL_FALSE_ACCEPTANCE")
        self.assertTrue(r_exc["conventional_false_acceptance"])
        self.assertEqual(r_exc["first_fault_step_index"], 1)

        # 3. Silent representation migration at step 1: conventional falsely accepts, LGGR localizes step 1
        w_mig = StepWitness(
            witness_id="w_mig", source=s1, target=s0, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
            representation_id="migrated-state/v2",
        )
        r_mig = comp.compare_trace("trace_rep_migration", s0, [w_ok, w_mig])
        self.assertEqual(r_mig["status"], "CONVENTIONAL_FALSE_ACCEPTANCE")
        self.assertTrue(r_mig["conventional_false_acceptance"])
        self.assertEqual(r_mig["first_fault_step_index"], 1)

        # 4. Retained deferred obligation across later empty-obligation step
        w_ob1 = StepWitness(
            witness_id="w_ob1", source=s0, target=s1, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
            obligations=("verify_schema_v2",),
        )
        w_ob2 = StepWitness(
            witness_id="w_ob2", source=s1, target=s0, observed_magnitude=1,
            local_accepted=True, smoke_passed=True, policy_sha256=policy.sha256,
            obligations=(),
        )
        r_ob = comp.compare_trace("trace_deferred_obligation", s0, [w_ob1, w_ob2])
        self.assertEqual(r_ob["status"], "CONVENTIONAL_FALSE_ACCEPTANCE")
        self.assertTrue(r_ob["conventional_false_acceptance"])
        self.assertEqual(r_ob["retained_obligations"], ["verify_schema_v2"])
        self.assertEqual(r_ob["lggr_batch_status"], "WITNESS_INCOMPLETE")

        summary = comp.get_receipt()
        self.assertEqual(summary["traces_evaluated"], 4)
        self.assertEqual(summary["conventional_false_acceptances"], 3)
        self.assertEqual(summary["conventional_false_refusals"], 0)
        # Open obligations are now localized online as well as in batch replay.
        self.assertEqual(summary["faults_localized_online"], 3)
        self.assertEqual(summary["traces_with_retained_obligations"], 1)

    def test_cycle_basis_sensitivity_and_complementary_slackness(self) -> None:
        """Verify fundamental cycle matrix C D0 = 0 and complementary slackness on coupled diamond."""
        mon = StreamingCochainMonitor()
        mon.add_edge("A", "C", 0, weight=Fraction(3, 2))
        mon.add_edge("A", "B", 1, weight=Fraction(5, 1))
        mon.add_edge("B", "C", 1, weight=Fraction(5, 1))
        mon.add_edge("A", "D", 1, weight=Fraction(5, 1))
        mon.add_edge("D", "C", 1, weight=Fraction(5, 1))

        sens = mon.analyze_cycle_basis_sensitivity()
        self.assertEqual(sens["betti_1"], 2)
        self.assertTrue(sens["cycle_annihilates_coboundary"])
        self.assertTrue(sens["complementary_slackness_verified"])
        self.assertEqual(sens["global_l1_repair_distance"], "3")
        # Shared diagonal edge 0 (A->C) carries residual |r_0| = 2, while outer edges have 0 residual
        self.assertEqual(sens["active_repair_edges"], [0])
        self.assertEqual(sens["marginal_weight_sensitivity"], ["2", "0", "0", "0", "0"])

        # Exact rational pivot threshold for shared diagonal edge 0:
        # w_0 = 3/2, |r_0| = 2, alternative outer-wing cut cost = 5*2 + 5*2 = 20 -> w_0^crit = 10, margin = 17/2
        piv0 = mon.compute_edge_pivot_threshold(0)
        self.assertEqual(piv0["status"], "PIVOT_THRESHOLD_LOCATED")
        self.assertTrue(piv0["is_active_bottleneck"])
        self.assertEqual(piv0["current_weight"], "3/2")
        self.assertEqual(piv0["current_residual_magnitude"], "2")
        self.assertEqual(piv0["critical_weight"], "10")
        self.assertEqual(piv0["weight_margin"], "17/2")
        self.assertEqual(piv0["post_pivot_residual_magnitude"], "0")

        # Inactive outer edge 1 (A->B) has zero residual -> INACTIVE_ZERO_RESIDUAL
        piv1 = mon.compute_edge_pivot_threshold(1)
        self.assertEqual(piv1["status"], "INACTIVE_ZERO_RESIDUAL")
        self.assertFalse(piv1["is_active_bottleneck"])
        self.assertIsNone(piv1["critical_weight"])

    def test_six_role_overlay_and_cancellation_masking(self) -> None:
        """Verify LGGR III six-role overlay context guards and D=0 vs M>0 cancellation masking."""
        mon = StreamingSixRoleOverlayMonitor(scope_id="six-role-test")

        valid_contexts = {
            "finite_obstruction": {
                "carrier": "X_6",
                "degree": 1,
                "comparison_map": "d_0",
                "quotient_gauge": "grounded_v0",
                "replay_data": "sha256:abc",
            },
            "foundations": {"diagnostic_only": True, "authority_effect": "None"},
            "representation": {"operation": "F1_D0", "transport_witness": "F1_D0"},
            "observer": {"left_envelope": "scale_w1", "right_envelope": "scale_w1"},
            "continuum_shadow": {"finite_calculation": True, "limit_statement_distinct": True},
            "action_and_alignment": {
                "residual_routed_as_feedback": True,
                "relabeled_as_success": False,
            },
        }

        for role, ctx in valid_contexts.items():
            res = mon.record_evaluation(role, 1, 1, 1, context=ctx)
            self.assertEqual(res["status"], "ROLE_OVERLAY_VERIFIED")
            self.assertEqual(res["contract_status"], "COMPOSABLE_LGGG")
            self.assertTrue(res["identity_g_minus_l_eq_d"])

        sum_ok = mon.get_receipt()
        self.assertEqual(sum_ok["status"], "ROLE_OVERLAY_VERIFIED")
        self.assertEqual(sum_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(sum_ok["records_count"], 6)
        self.assertEqual(sum_ok["disagreement_count"], 0)

        # Now add PGD (0, 1, 1) -> defect +1, then NGD (1, 1, 0) -> defect -1
        # Signed defect sum D = +1 + (-1) = 0, but disagreement count M = 2 > 0
        r_pgd = mon.record_evaluation(
            "observer", 0, 1, 1, context=valid_contexts["observer"], weight=Fraction(3, 2)
        )
        self.assertEqual(r_pgd["classification"], "PGD")
        self.assertEqual(r_pgd["status"], "POINTWISE_DISAGREEMENT")

        r_ngd = mon.record_evaluation(
            "finite_obstruction",
            1,
            1,
            0,
            context=valid_contexts["finite_obstruction"],
            weight=Fraction(5, 2),
        )
        self.assertEqual(r_ngd["classification"], "NGD")
        self.assertEqual(r_ngd["sample_signed_defect_sum"], 0)
        self.assertEqual(r_ngd["sample_disagreement_count"], 2)
        self.assertTrue(r_ngd["cancellation_masked"])
        self.assertEqual(r_ngd["status"], "CANCELLATION_MASKED_LGGR")
        self.assertEqual(r_ngd["contract_status"], "OBSTRUCTED_LGGR")

        sum_masked = mon.get_receipt()
        self.assertEqual(sum_masked["status"], "CANCELLATION_MASKED_LGGR")
        self.assertTrue(sum_masked["identity_g_minus_l_eq_d"])
        self.assertTrue(sum_masked["identity_d_eq_npos_minus_nneg"])
        self.assertEqual(sum_masked["weighted_disagreement_sum"], "4")

        # Verify context envelope violation when observer envelopes differ (Proposition 4)
        r_env = mon.record_evaluation(
            "observer",
            1,
            1,
            1,
            context={"left_envelope": "w=1", "right_envelope": "w=2"},
        )
        self.assertEqual(r_env["status"], "CONTEXT_ENVELOPE_VIOLATION")
        self.assertFalse(r_env["context_valid"])
        self.assertIn("OBSERVATION_ENVELOPE_MISMATCH", r_env["context_violation_reasons"])

    def test_completion_relative_obstruction_and_moving_witnesses(self) -> None:
        """Verify LGGR IV moving-witness stage collisions and 3x+1 mod 2^n completion obstruction."""
        fmon = StreamingFiberMonitor(scope_id="completion-relative-test")
        # Three states where stage 1 key ('bit1') collides s0 and s1, while stage 2 keys ('bit1','bit2')
        # separate s1 from s0 but collide s0 and s2 (moving witness shift!)
        fmon.observe("s0", "rep_base", 0, metadata={"bit1": 0, "bit2": 0, "bit3": 0})
        fmon.observe("s1", "rep_base", 1, metadata={"bit1": 0, "bit2": 1, "bit3": 1})
        fmon.observe("s2", "rep_base", 1, metadata={"bit1": 0, "bit2": 0, "bit3": 1})

        res_obs = fmon.audit_completion_relative_extension(
            stage_key_ladder=[["bit1"], ["bit1", "bit2"]],
            congruence_coeff=3,
            congruence_offset=1,
            num_dyadic_stages=4,
        )
        self.assertEqual(res_obs["status"], "COMPLETION_ONLY_WITNESS_LGGR")
        self.assertEqual(res_obs["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(res_obs["all_finite_stages_green"])
        self.assertTrue(res_obs["compatible_thread_verified"])
        self.assertEqual(res_obs["completed_rational_witness"], "-1/3")
        self.assertFalse(res_obs["reflection_descends_to_integer_carrier"])
        self.assertTrue(res_obs["completion_only_witness_lggr"])
        self.assertTrue(res_obs["moving_witness_shifted"])
        self.assertEqual(
            [s["witness_x_n"] for s in res_obs["dyadic_stage_thread"]],
            [-1, 1, -3, 5],
        )

        # Now verify a reflection-descending case (3x + 3 == 0 mod 2^n -> r_hat = -1 in Z)
        # with jointly separating stage key ['bit1', 'bit2', 'bit3']
        res_desc = fmon.audit_completion_relative_extension(
            stage_key_ladder=[["bit1", "bit2", "bit3"]],
            congruence_coeff=3,
            congruence_offset=3,
            num_dyadic_stages=4,
        )
        self.assertEqual(res_desc["status"], "REFLECTION_DESCENT_VERIFIED")
        self.assertEqual(res_desc["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(res_desc["completed_rational_witness"], "-1")
        self.assertTrue(res_desc["reflection_descends_to_integer_carrier"])
        self.assertFalse(res_desc["completion_only_witness_lggr"])

    def test_disjoint_colliding_pairs_and_predictor_error_ceiling(self) -> None:
        """Verify disjoint colliding-pair packing and majority-vote error floor."""
        fmon = StreamingFiberMonitor(scope_id="error-ceiling-test")
        # Fiber 'rep_A': 5 states with queries [0, 0, 1, 1, 2] -> n_A=5, m_A=2 -> floor=3, k_A=2
        fmon.observe("a1", "rep_A", 0)
        fmon.observe("a2", "rep_A", 0)
        fmon.observe("a3", "rep_A", 1)
        fmon.observe("a4", "rep_A", 1)
        fmon.observe("a5", "rep_A", 2)
        # Fiber 'rep_B': 4 states with queries [10, 10, 20, 20] -> n_B=4, m_B=2 -> floor=2, k_B=2
        fmon.observe("b1", "rep_B", 10)
        fmon.observe("b2", "rep_B", 10)
        fmon.observe("b3", "rep_B", 20)
        fmon.observe("b4", "rep_B", 20)

        # Evaluate with optimal majority-vote predictor {'rep_A': 0, 'rep_B': 10}
        res_opt = fmon.evaluate_predictor_error_ceiling({"rep_A": 0, "rep_B": 10})
        self.assertEqual(res_opt["status"], "NONZERO_ERROR_CEILING_LGGR")
        self.assertEqual(res_opt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(res_opt["carrier_size"], 9)
        self.assertEqual(res_opt["disjoint_colliding_pairs_count"], 4)
        self.assertEqual(res_opt["majority_vote_error_floor"], 5)
        self.assertEqual(res_opt["majority_vote_error_rate"], "5/9")
        self.assertEqual(res_opt["predictor_errors"], 5)
        self.assertEqual(res_opt["predictor_error_rate"], "5/9")
        self.assertTrue(res_opt["pair_ceiling_verified"])
        self.assertTrue(res_opt["floor_inequality_verified"])

        # Evaluate with suboptimal predictor {'rep_A': 2, 'rep_B': 20} -> 4 + 2 = 6 errors
        res_sub = fmon.evaluate_predictor_error_ceiling({"rep_A": 2, "rep_B": 20})
        self.assertEqual(res_sub["predictor_errors"], 6)
        self.assertEqual(res_sub["predictor_error_rate"], "2/3")
        self.assertTrue(res_sub["pair_ceiling_verified"])
        self.assertTrue(res_sub["floor_inequality_verified"])

    def test_gram_probe_monitor_and_nullspace_blindspot(self) -> None:
        """Verify LGGR VI Gram kernel identity, centered two-query probe, sign-cube recovery, and ker(Q) blindspot."""
        gmon = StreamingGramProbeMonitor([[1, 0]], scope_id="gram-probe-test")

        # 1. Visible state x = [3, 5] with direction u = [2, 1] and step_size = 1/2
        r_vis = gmon.probe_state(
            "visible_x",
            [3, 5],
            step_size=Fraction(1, 2),
            direction=[2, 1],
        )
        self.assertEqual(r_vis["status"], "ADJOINT_SIGNAL_VERIFIED")
        self.assertEqual(r_vis["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_vis["observation_qx"], ["3"])
        self.assertEqual(r_vis["gram_response_hx"], ["3", "0"])
        self.assertEqual(r_vis["quadratic_energy"], "9/2")
        self.assertEqual(r_vis["centered_directional_probe"], "6")
        self.assertEqual(r_vis["expected_gram_pairing"], "6")
        self.assertTrue(r_vis["gram_kernel_identity_verified"])
        self.assertTrue(r_vis["directional_identity_verified"])
        self.assertEqual(r_vis["sign_cube_recovered_hx"], ["3", "0"])
        self.assertTrue(r_vis["sign_cube_identity_verified"])

        # 2. Hidden nullspace state k = [0, 1] in ker(Q0) -> GRAM_NULLSPACE_BLINDSPOT_LGGR
        r_hid = gmon.probe_state("hidden_k", [0, 1], step_size=Fraction(1, 3), direction=[1, 1])
        self.assertEqual(r_hid["status"], "GRAM_NULLSPACE_BLINDSPOT_LGGR")
        self.assertEqual(r_hid["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_hid["observation_qx"], ["0"])
        self.assertEqual(r_hid["gram_response_hx"], ["0", "0"])
        self.assertTrue(r_hid["is_nullspace_blindspot"])
        self.assertTrue(r_hid["gram_kernel_identity_verified"])
        self.assertTrue(r_hid["directional_identity_verified"])
        self.assertTrue(r_hid["sign_cube_identity_verified"])

        summary = gmon.get_receipt()
        self.assertEqual(summary["status"], "GRAM_NULLSPACE_BLINDSPOT_LGGR")
        self.assertEqual(summary["nullspace_blindspots_count"], 1)
        self.assertTrue(summary["all_gram_identities_verified"])

        # 3. Break/recover fixture Q1 = [[1, 1/4]] makes k = [0, 1] detectable
        gmon_rec = StreamingGramProbeMonitor([[1, Fraction(1, 4)]])
        r_det = gmon_rec.probe_state("detected_k", [0, 1], step_size=Fraction(1, 2))
        self.assertEqual(r_det["status"], "ADJOINT_SIGNAL_VERIFIED")
        self.assertEqual(r_det["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_det["observation_qx"], ["1/4"])
        self.assertEqual(r_det["gram_response_hx"], ["1/4", "1/16"])
        self.assertEqual(r_det["sign_cube_recovered_hx"], ["1/4", "1/16"])

    def test_path_kernel_composition_and_two_channel_discrepancy(self) -> None:
        """Verify LGGR I / III evaluated path-kernel composition and two-channel residual decomposition."""
        # 1. Exact G1-G3 composition across two boundary slices B1, B2
        kmon_ok = StreamingPathKernelMonitor(scope_id="kernel-ok")
        kmon_ok.add_stage1_segment("g1_b1", "A", "B1", Fraction(3, 2), 1)
        kmon_ok.add_stage2_segment("g2_b1", "B1", "C", Fraction(2, 1), 1)
        kmon_ok.add_stage1_segment("g1_b2", "A", "B2", Fraction(5, 2), 1)
        kmon_ok.add_stage2_segment("g2_b2", "B2", "C", Fraction(4, 5), 1)
        c1 = kmon_ok.observe_composite("comp_b1", "g1_b1", "g2_b1", 1)
        c2 = kmon_ok.observe_composite("comp_b2", "g1_b2", "g2_b2", 1)
        self.assertTrue(c1["two_channel_identity_verified"])
        self.assertTrue(c2["two_channel_identity_verified"])

        aud_ok = kmon_ok.audit_kernel_composition("A", "C")
        self.assertEqual(aud_ok["status"], "KERNEL_COMPOSITION_VERIFIED")
        self.assertEqual(aud_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(aud_ok["g1_bijection_verified"])
        self.assertEqual(aud_ok["global_evaluated_kernel"], "5")
        self.assertEqual(aud_ok["factored_boundary_kernel_sum"], "5")
        self.assertEqual(aud_ok["kernel_discrepancy"], "0")
        self.assertTrue(aud_ok["discrepancy_identity_verified"])

        # 2. Two-channel NGD + weight defect: B1 has NGD (1,1,0) with w1*w2=3,
        #    B2 has PGD (0,1,1) with w1*w2=2 and global_weight=7/2 (delta_w = 3/2)
        kmon_def = StreamingPathKernelMonitor(scope_id="kernel-defect")
        kmon_def.add_stage1_segment("s1_b1", "A", "B1", Fraction(3, 2), 1)
        kmon_def.add_stage2_segment("s2_b1", "B1", "C", Fraction(2, 1), 1)
        kmon_def.add_stage1_segment("s1_b2", "A", "B2", Fraction(2, 1), 0)
        kmon_def.add_stage2_segment("s2_b2", "B2", "C", Fraction(1, 1), 1)
        d1 = kmon_def.observe_composite("c_b1", "s1_b1", "s2_b1", 0, global_weight=Fraction(4, 1))
        d2 = kmon_def.observe_composite("c_b2", "s1_b2", "s2_b2", 1, global_weight=Fraction(7, 2))
        self.assertTrue(d1["two_channel_identity_verified"])
        self.assertTrue(d2["two_channel_identity_verified"])

        aud_def = kmon_def.audit_kernel_composition("A", "C")
        self.assertEqual(aud_def["status"], "NGD_KERNEL_DEFECT_LGGR")
        self.assertEqual(aud_def["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(aud_def["discrepancy_identity_verified"])
        # Factored sum = 3 + 0 = 3; global Z = 0*4 + 1*(7/2) = 7/2 -> discrepancy = 1/2
        # R_E = -1*3 + 1*2 = -1; R_w = (1*1 + (-1)*1) + (0*(3/2) + 1*(3/2)) = 3/2 -> R_E + R_w = 1/2
        self.assertEqual(aud_def["kernel_discrepancy"], "1/2")
        self.assertEqual(aud_def["evaluator_residual_re"], "-1")
        self.assertEqual(aud_def["weight_residual_rw"], "3/2")

    def test_organizational_gluing_weak_sufficiency_and_carrier_mixing(self) -> None:
        """Verify LGGR II weak vs. product sufficiency (M3/M4) and carrier-mixing forced NGD (M8/M9)."""
        omon = StreamingOrganizationalGluingMonitor(scope_id="org-gluing-test")

        # 1. Checked-closure eligible trace: E1=1, E2=1, EG=1, R3=1, G=True
        r_ok = omon.observe_boundary("t1", "left_A", "right_A", 1, 1, 1, r3=1)
        self.assertEqual(r_ok["status"], "CHECKED_CLOSURE_VERIFIED")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(r_ok["checked_closure_eligible"])
        self.assertTrue(r_ok["weak_sufficient"])
        self.assertTrue(r_ok["product_sufficient"])
        self.assertTrue(r_ok["m4_equivalence_verified"])

        # 2. Claim M3 witness: E1=1, E2=1, EG=0, R3=0, G=True -> WEAK_SUFFICIENT_NONFACTORED_LGGR
        r_m3 = omon.observe_boundary("t2", "left_B", "right_B", 1, 1, 0, r3=0)
        self.assertEqual(r_m3["status"], "WEAK_SUFFICIENT_NONFACTORED_LGGR")
        self.assertEqual(r_m3["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(r_m3["weak_sufficient"])
        self.assertFalse(r_m3["product_sufficient"])
        self.assertFalse(r_m3["factorizes"])
        self.assertTrue(r_m3["m4_equivalence_verified"])

        # 3. Claims M8 & M9: t3 shares joint carrier ("left_A", "right_A") with t1,
        #    local evaluators pass (1, 1), but EG(t3) = 0 != 1 = EG(t1) -> forced NGD on mixed class
        r_mix = omon.observe_boundary("t3", "left_A", "right_A", 1, 1, 0, r3=0)
        self.assertEqual(r_mix["status"], "CARRIER_MIXING_OBSTRUCTED_LGGR")
        self.assertIsNotNone(r_mix["carrier_mixing_collision"])
        self.assertTrue(r_mix["carrier_mixing_collision"]["locally_green_forced_ngd"])

        summary = omon.get_receipt()
        self.assertEqual(summary["status"], "CARRIER_MIXING_OBSTRUCTED_LGGR")
        self.assertEqual(summary["carrier_mixing_collisions_count"], 1)
        self.assertEqual(summary["weak_nonfactored_count"], 2)
        self.assertTrue(summary["all_m4_equivalences_verified"])

    def test_defect_soundness_coupled_compensation_and_minkowski_repair(self) -> None:
        """Verify LGGR V realizable soundness (im(D) cap ker(Q) == {0}), stealth scaling, and Minkowski repair."""
        # 1. Theorem 6 Coupled Soundness: D maps (v1, v2) -> (-v1, -v2, -v1, -v2)
        #    Q measures coord 0 on interface 0 and coord 1 on interface 1 -> dim(ker Q)=2, but im(D) cap ker(Q)={0}
        d_coupled = [[-1, 0], [0, -1], [-1, 0], [0, -1]]
        q_coupled = [[1, 0, 0, 0], [0, 0, 0, 1]]
        smon_coup = StreamingDefectSoundnessMonitor(d_coupled, q_coupled, scope_id="coupled-sound")
        r_coup = smon_coup.audit_soundness()
        self.assertEqual(r_coup["status"], "COUPLED_SOUNDNESS_VERIFIED_LGGG")
        self.assertEqual(r_coup["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(r_coup["soundness_holds"])
        self.assertEqual(r_coup["ambient_blindspot_dimension"], 2)
        self.assertEqual(r_coup["realizable_blindspot_dimension"], 0)
        self.assertTrue(r_coup["coupled_compensation_active"])

        # 2. Theorem 3 Stealth Realizable Defect at prescribed severity R = 7/2
        d_unsound = [[1, 0], [0, 1], [0, 1]]
        q_unsound = [[1, 0, 0]]
        smon_uns = StreamingDefectSoundnessMonitor(d_unsound, q_unsound, scope_id="stealth-unsound")
        r_uns = smon_uns.audit_soundness(target_severity=Fraction(7, 2))
        self.assertEqual(r_uns["status"], "STEALTH_REALIZABLE_DEFECT_LGGR")
        self.assertEqual(r_uns["contract_status"], "OBSTRUCTED_LGGR")
        self.assertFalse(r_uns["soundness_holds"])
        self.assertEqual(r_uns["realizable_blindspot_dimension"], 1)
        self.assertEqual(r_uns["stealth_global_inconsistency"], "7/2")
        self.assertEqual(r_uns["stealth_evaluator_score"], "0")

        # 3. Minkowski coupled repair lemma on omega = (1, -1)
        mink = smon_coup.evaluate_coupled_minkowski_repair(1, -1)
        self.assertEqual(mink["status"], "NONEXACT_QUOTIENT_DEFECT")
        self.assertEqual(mink["phi_1_repair_distance"], "2")
        self.assertEqual(mink["phi_2_squared_repair_distance"], "2")
        self.assertEqual(mink["phi_inf_repair_distance"], "1")
        self.assertEqual(mink["unique_l2_linf_minimizer_alpha"], "0")
        self.assertEqual(mink["l1_minimizer_interval"], ["-1", "1"])
        self.assertTrue(mink["chain_inequality_verified"])

    def test_dashboard_adequacy_reconstruction_and_collapsing_detector(self) -> None:
        """Verify LGGR I (E9-E18) and LGGR II (M6-M7) dashboard reconstruction and collapsing detector."""
        # 1. Mixed sample with ZDR (1, 1, 1), NGD (1, 1, 0), PGD (1, 0, 1), and joint failure (0, 1, 0)
        dmon = StreamingDashboardAdequacyMonitor(scope_id="dashboard-mixed")
        dmon.record_trace("t1", 1, 1, 1)  # ZDR, L=1, Eg=1
        dmon.record_trace("t2", 1, 1, 0)  # NGD, L=1, Eg=0
        dmon.record_trace("t3", 1, 0, 1)  # PGD, L=0, Eg=1
        r_mix = dmon.record_trace("t4", 0, 1, 0)  # ZDR joint failure, L=0, Eg=0

        self.assertEqual(r_mix["status"], "NGD_DEFECT_PRESENT_LGGR")
        self.assertEqual(r_mix["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_mix["sample_size"], 4)
        self.assertEqual(r_mix["n_pos_pgd"], 1)
        self.assertEqual(r_mix["n_neg_ngd"], 1)
        self.assertEqual(r_mix["n_zero_zdr"], 2)
        self.assertEqual(r_mix["disagreement_count_m"], 2)
        self.assertEqual(r_mix["signed_defect_sum_d"], 0)
        self.assertEqual(r_mix["local_pass_rate_lpr"], "1/2")
        self.assertEqual(r_mix["global_pass_rate_gpr"], "1/2")
        self.assertEqual(r_mix["evaluator_gluing_disagreement_egd"], "1/2")
        self.assertEqual(r_mix["mean_signed_defect"], "0")
        self.assertEqual(r_mix["global_failure_count"], 2)
        self.assertEqual(r_mix["joint_local_global_failure_count"], 1)
        self.assertTrue(r_mix["reconstruction_identities_verified"])
        self.assertTrue(r_mix["ngd_bounded_by_local_passes"])
        self.assertTrue(r_mix["global_failure_partition_verified"])
        self.assertTrue(r_mix["all_packet_recoveries_verified"])

        # 2. Claim M7 Product-Collapsing Detector: E1 copies Eg, E2 == 1 -> L == Eg tautologically
        dmon_collapse = StreamingDashboardAdequacyMonitor(
            scope_id="dashboard-collapse", copied_global_validator=True
        )
        dmon_collapse.record_trace("c1", 1, 1, 1)
        r_col = dmon_collapse.record_trace("c2", 0, 1, 0)
        self.assertEqual(r_col["status"], "PRODUCT_COLLAPSING_DETECTOR_LGGR")
        self.assertEqual(r_col["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(r_col["product_collapsing_detected"])

        # 3. Claim M6 All-Zero Agreement at Failure: Eg == L == 0 everywhere -> Delta_E == 0 with 0 global passes
        dmon_zero = StreamingDashboardAdequacyMonitor(scope_id="dashboard-all-fail")
        r_zero = dmon_zero.record_trace("z1", 0, 0, 0)
        self.assertEqual(r_zero["status"], "ZERO_DEFECT_ALL_FAIL_LGGR")
        self.assertEqual(r_zero["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(r_zero["all_zero_agreement_at_failure"])

    def test_bell_polytope_chsh_threshold_and_negative_mass(self) -> None:
        """Verify LGGR VII 4-context CHSH Bell polytope bound, v=1/2 threshold, and N_min / CF identity."""
        bmon = StreamingBellPolytopeMonitor(scope_id="bell-chsh-test")

        # 1. Critical visibility threshold v = 1/2 -> S = 2, N_min = 0, LOCAL_LHV_EXTENSION_LGGG
        r_crit = bmon.observe_isotropic_pr_mixture("iso_v_1_2", Fraction(1, 2))
        self.assertEqual(r_crit["status"], "LOCAL_LHV_EXTENSION_LGGG")
        self.assertEqual(r_crit["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_crit["canonical_chsh_s"], "2")
        self.assertEqual(r_crit["min_negative_mass_n_min"], "0")
        self.assertEqual(r_crit["contextual_fraction_cf"], "0")
        self.assertEqual(r_crit["local_packing_fraction"], "1")
        self.assertFalse(r_crit["above_visibility_threshold"])
        self.assertTrue(r_crit["all_16_lhv_vertices_bounded_by_2"])
        self.assertTrue(r_crit["packing_identity_verified"])

        # 2. Tsirelson rational approximant visibility v = 17/24 > 1/2 -> S = 17/6, N_min = 5/24, CF = 5/12
        r_tsir = bmon.observe_isotropic_pr_mixture("iso_v_17_24", Fraction(17, 24))
        self.assertEqual(r_tsir["status"], "BELL_NONLOCAL_OBSTRUCTION_LGGR")
        self.assertEqual(r_tsir["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_tsir["canonical_chsh_s"], "17/6")
        self.assertEqual(r_tsir["min_negative_mass_n_min"], "5/24")
        self.assertEqual(r_tsir["contextual_fraction_cf"], "5/12")
        self.assertEqual(r_tsir["local_packing_fraction"], "7/12")
        self.assertTrue(r_tsir["above_visibility_threshold"])
        self.assertTrue(r_tsir["packing_identity_verified"])

        # 3. PR-box algebraic maximum v = 1 -> S = 4, N_min = 1/2, CF = 1
        r_pr = bmon.observe_isotropic_pr_mixture("pr_box", 1)
        self.assertEqual(r_pr["status"], "BELL_NONLOCAL_OBSTRUCTION_LGGR")
        self.assertEqual(r_pr["canonical_chsh_s"], "4")
        self.assertEqual(r_pr["min_negative_mass_n_min"], "1/2")
        self.assertEqual(r_pr["contextual_fraction_cf"], "1")
        self.assertEqual(r_pr["local_packing_fraction"], "0")
        self.assertTrue(r_pr["packing_identity_verified"])

        summary = bmon.get_receipt()
        self.assertEqual(summary["status"], "BELL_NONLOCAL_OBSTRUCTION_LGGR")
        self.assertEqual(summary["observed_models_count"], 3)
        self.assertEqual(summary["local_lhv_models"], ["iso_v_1_2"])
        self.assertEqual(summary["nonlocal_obstructed_models"], ["iso_v_17_24", "pr_box"])
        self.assertEqual(summary["max_chsh_s_observed"], "4")
        self.assertEqual(summary["max_negative_mass_n_min"], "1/2")
        self.assertTrue(summary["all_16_lhv_vertices_bounded_by_2"])
        self.assertTrue(summary["all_packing_identities_verified"])

    def test_product_retraction_residual_vs_local_extension(self) -> None:
        """Verify LGGR VII product-state retraction residual F_p = p - p_A x p_B vs. local LHV extension."""
        pmon = StreamingProductRetractionMonitor(scope_id="prod-retraction-test")

        # 1. Single bivariate table for shared coin 1/2 [00] + 1/2 [11]:
        #    det = 1/4, F_p = [[1/4, -1/4], [-1/4, 1/4]], ||F_p||_1 = 1
        t_coin = pmon.observe_bivariate_table("shared_coin", Fraction(1, 2), 0, 0, Fraction(1, 2))
        self.assertEqual(t_coin["status"], "CORRELATED_NONPRODUCT_TABLE")
        self.assertFalse(t_coin["is_product_state"])
        self.assertEqual(t_coin["determinant"], "1/4")
        self.assertEqual(t_coin["l1_product_residual"], "1")
        self.assertTrue(t_coin["determinant_identity_verified"])
        self.assertTrue(t_coin["zero_row_marginals_verified"])
        self.assertTrue(t_coin["zero_col_marginals_verified"])
        self.assertTrue(t_coin["retraction_idempotence_verified"])

        # 2. 4-context product state: uniform 1/4 everywhere -> ||F_p||_1 = 0, N_min = 0
        unif = (Fraction(1, 4), Fraction(1, 4), Fraction(1, 4), Fraction(1, 4))
        m_prod = pmon.observe_four_context_tables(
            "product_uniform",
            {"00": unif, "01": unif, "10": unif, "11": unif},
        )
        self.assertEqual(m_prod["status"], "PRODUCT_FACTORIZED_LGGG")
        self.assertEqual(m_prod["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(m_prod["max_l1_product_residual"], "0")
        self.assertEqual(m_prod["min_negative_mass_n_min"], "0")
        self.assertFalse(m_prod["classical_correlation_without_nonlocality"])

        # 3. 4-context classical shared coin: ||F_p||_1 = 1 > 0 in every context, yet S = 2 and N_min = 0
        coin = (Fraction(1, 2), 0, 0, Fraction(1, 2))
        m_corr = pmon.observe_four_context_tables(
            "classical_shared_coin",
            {"00": coin, "01": coin, "10": coin, "11": coin},
        )
        self.assertEqual(m_corr["status"], "CLASSICAL_CORRELATION_LHV_LGGG")
        self.assertEqual(m_corr["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(m_corr["max_l1_product_residual"], "1")
        self.assertEqual(m_corr["canonical_chsh_s"], "2")
        self.assertEqual(m_corr["min_negative_mass_n_min"], "0")
        self.assertTrue(m_corr["classical_correlation_without_nonlocality"])
        self.assertTrue(m_corr["all_retraction_identities_verified"])

        # 4. 4-context PR-box: ||F_p||_1 = 1 in every context AND S = 4 -> N_min = 1/2 > 0
        anticoin = (0, Fraction(1, 2), Fraction(1, 2), 0)
        m_pr = pmon.observe_four_context_tables(
            "pr_box_tables",
            {"00": coin, "01": coin, "10": coin, "11": anticoin},
        )
        self.assertEqual(m_pr["status"], "BELL_NONLOCAL_OBSTRUCTION_LGGR")
        self.assertEqual(m_pr["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(m_pr["max_l1_product_residual"], "1")
        self.assertEqual(m_pr["canonical_chsh_s"], "4")
        self.assertEqual(m_pr["min_negative_mass_n_min"], "1/2")
        self.assertFalse(m_pr["classical_correlation_without_nonlocality"])

        summary = pmon.get_receipt()
        self.assertEqual(summary["status"], "BELL_NONLOCAL_OBSTRUCTION_LGGR")
        self.assertEqual(summary["product_factorized_models"], ["product_uniform"])
        self.assertEqual(summary["classical_correlation_lhv_models"], ["classical_shared_coin"])
        self.assertEqual(summary["bell_nonlocal_models"], ["pr_box_tables"])
        self.assertTrue(summary["all_retraction_identities_verified"])

    def test_rsi_fiber_ceiling_invariance_and_refinement(self) -> None:
        """Verify LGGR VII evidence-preserving RSI fiber ceiling invariance across generations and refinement."""
        rmon = StreamingRSIFiberCeilingMonitor(scope_id="rsi-ceiling-test")

        # Colliding states x1, x2 share coarse report "rep_A" with target values 1 and 6
        # -> spread W = 5, half-spread ceiling = 5/2, midpoint = 7/2
        rmon.observe_state("x1", "rep_A", 1, refined_report="rep_A_low")
        rmon.observe_state("x2", "rep_A", 6, refined_report="rep_A_high")
        # Non-colliding state x3 on "rep_B" with target value 4
        rmon.observe_state("x3", "rep_B", 4, refined_report="rep_B_exact")

        # Generation 0: initial coarse predictor -> rep_A: 1, rep_B: 4 (error on x2 is |6 - 1| = 5 >= 5/2)
        g0 = rmon.evaluate_generation("gen_0", {"rep_A": 1, "rep_B": 4})
        self.assertEqual(g0["status"], "RSI_FIBER_CEILING_LOCKED_LGGR")
        self.assertEqual(g0["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(g0["worst_case_error"], "5")
        self.assertEqual(g0["coarse_half_spread_ceiling"], "5/2")
        self.assertFalse(g0["attains_minimax_midpoint_floor"])
        self.assertTrue(g0["invariance_lower_bound_verified"])

        # Generation 1: recursive update shifts rep_A -> 4 (error on x1 is |1 - 4| = 3 >= 5/2)
        g1 = rmon.evaluate_generation("gen_1", {"rep_A": 4, "rep_B": 4})
        self.assertEqual(g1["status"], "RSI_FIBER_CEILING_LOCKED_LGGR")
        self.assertEqual(g1["worst_case_error"], "3")
        self.assertTrue(g1["invariance_lower_bound_verified"])

        # Generation 2: optimal midpoint predictor rep_A -> 7/2 attains the exact minimax floor 5/2
        g2 = rmon.evaluate_generation("gen_2_midpoint", {"rep_A": Fraction(7, 2), "rep_B": 4})
        self.assertEqual(g2["status"], "RSI_FIBER_CEILING_LOCKED_LGGR")
        self.assertEqual(g2["worst_case_error"], "5/2")
        self.assertTrue(g2["attains_minimax_midpoint_floor"])
        self.assertTrue(g2["invariance_lower_bound_verified"])

        # Generation 3 (with sensor refinement p'): splits rep_A into rep_A_low and rep_A_high -> error = 0
        g3 = rmon.evaluate_generation(
            "gen_3_refined",
            {"rep_A_low": 1, "rep_A_high": 6, "rep_B_exact": 4},
            use_refined_report=True,
        )
        self.assertEqual(g3["status"], "EVIDENCE_REFINEMENT_RESOLVED_LGGG")
        self.assertEqual(g3["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(g3["worst_case_error"], "0")
        self.assertTrue(g3["broke_coarse_ceiling_via_refinement"])
        self.assertTrue(g3["invariance_lower_bound_verified"])

        summary = rmon.get_receipt()
        self.assertEqual(summary["status"], "EVIDENCE_REFINEMENT_RESOLVED_LGGG")
        self.assertEqual(summary["coarse_half_spread_ceiling"], "5/2")
        self.assertEqual(summary["refined_half_spread_ceiling"], "0")
        self.assertEqual(summary["evidence_preserving_generations_count"], 3)
        self.assertEqual(summary["refined_generations_count"], 1)
        self.assertTrue(summary["all_invariance_lower_bounds_verified"])
        self.assertTrue(summary["refinement_resolved"])

    def test_coalitional_shapley_attribution_and_nonadditive_defect(self) -> None:
        """Verify LGGR II exact rational Shapley attribution axioms and non-additive evaluator defect separation."""
        cmon = StreamingCoalitionalAttributionMonitor(scope_id="shapley-test")

        # 1. Canonical 2-evaluator NGD trace: E1=1, E2=1, Eg=0 -> Delta_E = -1
        #    v({}) = 0, v({E1}) = -1, v({E2}) = -1, v({E1, E2}) = -1
        #    Shapley attributions: phi_1 = -1/2, phi_2 = -1/2 (sum = -1), whereas naive singleton sum = -2 != -1
        g_ngd = cmon.audit_evaluator_defect_game("ngd_trace_110", 1, 1, 0)
        self.assertEqual(g_ngd["status"], "NONADDITIVE_COALITIONAL_DEFECT_LGGR")
        self.assertEqual(g_ngd["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(g_ngd["shapley_attributions"]["E1"], "-1/2")
        self.assertEqual(g_ngd["shapley_attributions"]["E2"], "-1/2")
        self.assertEqual(g_ngd["shapley_sum"], "-1")
        self.assertEqual(g_ngd["naive_singleton_marginal_sum"], "-2")
        self.assertEqual(g_ngd["synergy_interaction_term"], "1")
        self.assertFalse(g_ngd["raw_singleton_sum_equals_grand_value"])
        self.assertEqual(g_ngd["symmetric_player_pairs"], [["E1", "E2"]])
        self.assertTrue(g_ngd["efficiency_verified"])
        self.assertTrue(g_ngd["symmetry_verified"])
        self.assertTrue(g_ngd["dummy_player_axiom_verified"])

        # 2. 3-player game with two symmetric active players (P1, P2) and one dummy player (P3):
        #    v(S) = 3 if {P1, P2} <= S, 1 if exactly one of {P1, P2} in S, 0 otherwise.
        #    P3 has 0 marginal contribution everywhere -> phi(P3) = 0, phi(P1) = phi(P2) = 3/2
        g_3p = cmon.observe_coalition_game(
            "three_player_with_dummy",
            ["P1", "P2", "P3"],
            {
                "": 0,
                "P1": 1,
                "P2": 1,
                "P3": 0,
                "P1,P2": 3,
                "P1,P3": 1,
                "P2,P3": 1,
                "P1,P2,P3": 3,
            },
        )
        self.assertEqual(g_3p["status"], "NONADDITIVE_SYNERGY_ATTRIBUTION")
        self.assertEqual(g_3p["shapley_attributions"]["P1"], "3/2")
        self.assertEqual(g_3p["shapley_attributions"]["P2"], "3/2")
        self.assertEqual(g_3p["shapley_attributions"]["P3"], "0")
        self.assertEqual(g_3p["shapley_sum"], "3")
        self.assertEqual(g_3p["dummy_players"], ["P3"])
        self.assertEqual(g_3p["symmetric_player_pairs"], [["P1", "P2"]])
        self.assertTrue(g_3p["efficiency_verified"])
        self.assertTrue(g_3p["symmetry_verified"])
        self.assertTrue(g_3p["dummy_player_axiom_verified"])

        summary = cmon.get_receipt()
        self.assertEqual(summary["status"], "NONADDITIVE_COALITIONAL_DEFECT_LGGR")
        self.assertEqual(summary["audited_games_count"], 2)
        self.assertEqual(summary["nonadditive_defect_games"], ["ngd_trace_110"])
        self.assertTrue(summary["all_efficiency_verified"])
        self.assertTrue(summary["all_symmetry_verified"])
        self.assertTrue(summary["all_dummy_player_axioms_verified"])

    def test_threshold_governance_quorum_vs_product_defect(self) -> None:
        """Verify LGGR II k-of-n quorum threshold vs. strict product aggregator defect separation."""
        tmon = StreamingThresholdGovernanceMonitor(3, 2, scope_id="quorum-2of3-test")

        # 1. Coherent unanimous pass: (1, 1, 1) with eg = 1 -> L = 1, M = 1, Delta_prod = 0, Delta_quorum = 0
        r_ok = tmon.record_vote("t_coherent", [1, 1, 1], 1)
        self.assertEqual(r_ok["status"], "THRESHOLD_GOVERNANCE_COHERENT_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_ok["latest_trace"]["trace_status"], "THRESHOLD_GOVERNANCE_COHERENT_LGGG")

        # 2. Quorum-recovered PGD: (1, 1, 0) with eg = 1 -> L = 0, M = 1, Delta_prod = +1, Delta_quorum = 0
        r_pgd = tmon.record_vote("t_quorum_pgd", [1, 1, 0], 1)
        self.assertEqual(r_pgd["status"], "QUORUM_RECOVERED_PGD")
        self.assertEqual(r_pgd["latest_trace"]["delta_product"], 1)
        self.assertEqual(r_pgd["latest_trace"]["delta_quorum"], 0)
        self.assertEqual(r_pgd["latest_trace"]["quorum_inflation_gap"], 1)

        # 3. Quorum-masked defect: (1, 1, 0) with eg = 0 -> validator 3 vetoes (L = 0, Delta_prod = 0),
        #    but 2-of-3 quorum passes (M = 1, Delta_quorum = -1)
        r_qmask = tmon.record_vote("t_quorum_masked", [1, 1, 0], 0)
        self.assertEqual(r_qmask["status"], "QUORUM_MASKED_DEFECT_LGGR")
        self.assertEqual(r_qmask["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_qmask["latest_trace"]["delta_product"], 0)
        self.assertEqual(r_qmask["latest_trace"]["delta_quorum"], -1)
        self.assertEqual(r_qmask["latest_trace"]["quorum_inflation_gap"], 1)

        # 4. Unanimous NGD: (1, 1, 1) with eg = 0 -> both L = 1 and M = 1 incur -1 defect
        r_ungd = tmon.record_vote("t_unanimous_ngd", [1, 1, 1], 0)
        self.assertEqual(r_ungd["status"], "UNANIMOUS_NGD_DEFECT_LGGR")
        self.assertEqual(r_ungd["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_ungd["unanimous_ngd_count"], 1)
        self.assertEqual(r_ungd["quorum_masked_ngd_count"], 1)
        self.assertEqual(r_ungd["quorum_recovered_pgd_count"], 1)
        self.assertEqual(r_ungd["coherent_count"], 1)
        self.assertTrue(r_ungd["all_monotonicity_verified"])
        self.assertTrue(r_ungd["all_defect_difference_identities_verified"])

    def test_cptp_trace_preservation_blindspot_and_composition(self) -> None:
        """Verify Kraus channel R_TP = sum K_r^T K_r - I_d, state-blindspot masking, and composition identity."""
        # 1. Exact rational CPTP channel: K1 = [[3/5, 0], [0, 1]], K2 = [[0, 0], [4/5, 0]]
        #    K1^T K1 + K2^T K2 = [[9/25 + 16/25, 0], [0, 1]] = I_2 -> R_TP = 0
        k1_tp = [[Fraction(3, 5), 0], [0, 1]]
        k2_tp = [[0, 0], [Fraction(4, 5), 0]]
        mon_tp = StreamingCPTPTraceMonitor([k1_tp, k2_tp], scope_id="cptp-tp")
        p_tp = mon_tp.probe_state("rho_mixed", [[Fraction(1, 2), 0], [0, Fraction(1, 2)]])
        self.assertEqual(p_tp["status"], "OPERATOR_TP_VERIFIED_LGGG")
        self.assertEqual(p_tp["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(p_tp["operator_trace_preserving"])
        self.assertEqual(p_tp["trace_discrepancy"], "0")
        self.assertTrue(p_tp["trace_discrepancy_identity_verified"])

        # 2. Non-TP channel with state blindspot: K_bad1 = [[1, 0], [0, 0]], K_bad2 = [[1, 0], [0, 0]]
        #    sum K^T K = [[2, 0], [0, 0]], so R_TP = [[1, 0], [0, -1]] != 0 (L1 norm = 2)
        k_bad = [[[1, 0], [0, 0]], [[1, 0], [0, 0]]]
        mon_bad = StreamingCPTPTraceMonitor(k_bad, scope_id="cptp-non-tp")
        # Probing maximally mixed state [[1/2, 0], [0, 1/2]] gives tr(rho * R_TP) = 1/2 - 1/2 = 0 (blindspot!)
        p_blind = mon_bad.probe_state("rho_half_id", [[Fraction(1, 2), 0], [0, Fraction(1, 2)]])
        self.assertEqual(p_blind["status"], "STATE_BLINDSPOT_NON_TP_LGGR")
        self.assertEqual(p_blind["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(p_blind["state_blindspot_masked"])
        self.assertEqual(p_blind["trace_discrepancy"], "0")
        self.assertEqual(p_blind["residual_l1_norm"], "2")
        self.assertTrue(p_blind["trace_discrepancy_identity_verified"])

        # Probing |0><0| = [[1, 0], [0, 0]] exposes overt trace violation: tr(E(rho)) - tr(rho) = 1
        p_viol = mon_bad.probe_state("rho_ket0", [[1, 0], [0, 0]])
        self.assertEqual(p_viol["status"], "STATE_TRACE_VIOLATION_LGGR")
        self.assertEqual(p_viol["trace_discrepancy"], "1")
        self.assertTrue(p_viol["trace_discrepancy_identity_verified"])

        # 3. Two-channel composition identity: R_TP(E2 o E1) == R_TP(E1) + E1^dagger(R_TP(E2))
        comp = mon_bad.audit_composition("bad_then_tp", [k1_tp, k2_tp])
        self.assertEqual(comp["status"], "COMPOSED_NON_TP_DEFECT_LGGR")
        self.assertTrue(comp["composition_residual_identity_verified"])

        summary = mon_bad.get_receipt()
        self.assertEqual(summary["status"], "STATE_BLINDSPOT_NON_TP_LGGR")
        self.assertEqual(summary["blindspot_state_ids"], ["rho_half_id"])
        self.assertTrue(summary["all_state_discrepancy_identities_verified"])
        self.assertTrue(summary["all_composition_identities_verified"])

    def test_windowed_drift_horizon_breach_and_partition_bound(self) -> None:
        """Verify LGGR I/VIII sliding-window local green vs. full-horizon cumulative budget breach."""
        # Window size W = 2, window budget B_W = 2, global budget B_global = 3
        wmon = StreamingWindowedDriftMonitor(2, 2, 3, scope_id="window-drift-test")

        # Steps 1..3 with drift 1 each: window sum <= 2, cumulative drift <= 3 -> within both budgets
        wmon.record_step("s1", 1)
        wmon.record_step("s2", 1)
        r3 = wmon.record_step("s3", 1)
        self.assertEqual(r3["status"], "WINDOW_AND_HORIZON_WITHIN_BUDGET_LGGG")
        self.assertEqual(r3["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r3["current_window_sum"], "2")
        self.assertEqual(r3["cumulative_horizon_drift"], "3")
        self.assertTrue(r3["block_partition_bound_verified"])

        # Step 4 with drift 1: contiguous 2-step window is still 1 + 1 = 2 <= B_W,
        # but cumulative horizon drift is 4 > 3 = B_global -> SLIDING_WINDOW_HORIZON_BREACH_LGGR
        r4 = wmon.record_step("s4", 1)
        self.assertEqual(r4["status"], "SLIDING_WINDOW_HORIZON_BREACH_LGGR")
        self.assertEqual(r4["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r4["current_window_sum"], "2")
        self.assertEqual(r4["max_window_sum"], "2")
        self.assertEqual(r4["cumulative_horizon_drift"], "4")
        self.assertTrue(r4["all_windows_within_budget"])
        self.assertFalse(r4["horizon_within_budget"])
        self.assertTrue(r4["sliding_window_masked_breach"])
        self.assertTrue(r4["block_partition_bound_verified"])

        # Step 5 with drift 2: contiguous 2-step window is 1 + 2 = 3 > 2 = B_W -> LOCAL_WINDOW_BUDGET_BREACH
        r5 = wmon.record_step("s5", 2)
        self.assertEqual(r5["status"], "LOCAL_WINDOW_BUDGET_BREACH")
        self.assertFalse(r5["all_windows_within_budget"])
        self.assertTrue(r5["block_partition_bound_verified"])

    def test_replay_order_endpoint_invariance_and_prefix_divergence(self) -> None:
        """Verify LGGR VIII commutative endpoint invariance vs. arrival-masked causal prefix breach."""
        # 1. Arrival-masked causal breach: causal sequence is (e_debit: +3 at causal_index=1, e_credit: -2 at causal_index=2)
        #    Under prefix budget B_prefix = 2, if e_credit (-2) arrives first and e_debit (+3) arrives second:
        #    - Arrival prefixes: [-2, 1] -> max = 1 <= 2 (arrival order looks green!)
        #    - Causal prefixes: [3, 1] -> max = 3 > 2 (causal order breaches B_prefix = 2!)
        #    - Endpoint sum in both orders: 1
        rmon = StreamingReplayOrderMonitor(2, scope_id="replay-order-test")
        rmon.register_event("e_credit", -2, causal_index=2)
        r_masked = rmon.register_event("e_debit", 3, causal_index=1)

        self.assertEqual(r_masked["status"], "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR")
        self.assertEqual(r_masked["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_masked["common_endpoint_sum"], "1")
        self.assertEqual(r_masked["arrival_max_prefix"], "1")
        self.assertEqual(r_masked["causal_max_prefix"], "3")
        self.assertEqual(r_masked["worst_permutation_max_prefix"], "3")
        self.assertEqual(r_masked["positive_delta_mass"], "3")
        self.assertTrue(r_masked["arrival_within_budget"])
        self.assertFalse(r_masked["causal_within_budget"])
        self.assertTrue(r_masked["arrival_masked_causal_breach"])
        self.assertTrue(r_masked["prefix_order_diverged"])
        self.assertTrue(r_masked["endpoint_permutation_invariance_verified"])
        self.assertTrue(r_masked["positive_sum_equals_worst_permutation_max_verified"])

        # 2. Permutation-robust prefix stream: positive delta mass <= B_prefix = 3
        rmon_ok = StreamingReplayOrderMonitor(3, scope_id="replay-robust-test")
        rmon_ok.register_event("p1", 1, causal_index=1)
        r_ok = rmon_ok.register_event("p2", 2, causal_index=2)
        self.assertEqual(r_ok["status"], "PERMUTATION_ROBUST_PREFIX_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(r_ok["endpoint_permutation_invariance_verified"])
        self.assertTrue(r_ok["positive_sum_equals_worst_permutation_max_verified"])

    def test_simplicial_cup_product_and_leibniz_cocycle_identity(self) -> None:
        """Verify Alexander-Whitney discrete cup product and graded Leibniz cocycle identity on 2-simplices."""
        smon = StreamingSimplicialCupMonitor(scope_id="simplicial-cup-test")

        # 1. Trivial cup cocycle: d^1 alpha = 0, d^1 beta = 0, alpha_{01} = 0 -> alpha cup beta = 0
        s_triv = smon.evaluate_two_simplex(
            "sigma_trivial",
            "v0",
            "v1",
            "v2",
            alpha_01=0,
            alpha_12=2,
            alpha_02=2,
            beta_01=1,
            beta_12=0,
            beta_02=1,
            f_v0=3,
            f_v1=5,
            f_v2=9,
        )
        self.assertEqual(s_triv["status"], "EXACT_TRIVIAL_CUP_COCYCLE_LGGG")
        self.assertEqual(s_triv["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(s_triv["alpha_cup_beta"], "0")
        self.assertTrue(s_triv["leibniz_identity_verified"])
        self.assertTrue(s_triv["exact_coboundary_d1_d0_zero_verified"])

        # 2. Non-trivial cup cocycle obstruction: alpha = (2, 3, 5) with d^1 alpha = 3 - 5 + 2 = 0,
        #    beta = (4, -1, 3) with d^1 beta = -1 - 3 + 4 = 0,
        #    yet alpha cup beta = 2 * (-1) = -2 != 0 and commutator = -2 - 12 = -14
        s_cup = smon.evaluate_two_simplex(
            "sigma_nontrivial_cup",
            "v0",
            "v1",
            "v2",
            alpha_01=2,
            alpha_12=3,
            alpha_02=5,
            beta_01=4,
            beta_12=-1,
            beta_02=3,
            f_v0=2,
            f_v1=7,
            f_v2=-1,
        )
        self.assertEqual(s_cup["status"], "NONTRIVIAL_CUP_COCYCLE_OBSTRUCTION_LGGR")
        self.assertEqual(s_cup["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(s_cup["d1_alpha"], "0")
        self.assertEqual(s_cup["d1_beta"], "0")
        self.assertEqual(s_cup["alpha_cup_beta"], "-2")
        self.assertEqual(s_cup["beta_cup_alpha"], "12")
        self.assertEqual(s_cup["cup_commutator"], "-14")
        self.assertTrue(s_cup["leibniz_identity_verified"])
        self.assertTrue(s_cup["exact_coboundary_d1_d0_zero_verified"])

        # 3. Non-cocycle coboundary: d^1 alpha = 1 + 1 - 1 = 1 != 0
        s_non = smon.evaluate_two_simplex(
            "sigma_non_cocycle",
            "v0",
            "v1",
            "v2",
            alpha_01=1,
            alpha_12=1,
            alpha_02=1,
            beta_01=1,
            beta_12=2,
            beta_02=3,
            f_v0=1,
            f_v1=4,
            f_v2=6,
        )
        self.assertEqual(s_non["status"], "NON_COCYCLE_COBOUNDARY_LGGR")
        self.assertEqual(s_non["d1_alpha"], "1")
        self.assertTrue(s_non["leibniz_identity_verified"])

        summary = smon.get_receipt()
        self.assertEqual(summary["status"], "NON_COCYCLE_COBOUNDARY_LGGR")
        self.assertEqual(summary["non_cocycle_simplex_ids"], ["sigma_non_cocycle"])
        self.assertEqual(summary["nontrivial_cup_simplex_ids"], ["sigma_nontrivial_cup"])
        self.assertTrue(summary["all_leibniz_identities_verified"])
        self.assertTrue(summary["all_d1_d0_zero_verified"])

    def test_mayer_vietoris_local_exactness_and_connecting_obstruction(self) -> None:
        """Verify Mayer-Vietoris connecting homomorphism obstruction on locally exact subcomplex covers."""
        # 1. Locally exact U (top arc A->M1->B with sum 1+1=2) and locally exact V
        #    (bottom arc A->M2->B with sum 0+(-1)=-1) meeting at disconnected overlap {A, B}:
        #    delta(A) = 0 - 0 = 0, delta(B) = 2 - (-1) = 3 -> spread = 3 != 0
        mv_bad = StreamingMayerVietorisMonitor(scope_id="mv-obstructed-circle")
        mv_bad.record_edge("A", "M1", 1, in_u=True, in_v=False)
        mv_bad.record_edge("M1", "B", 1, in_u=True, in_v=False)
        mv_bad.record_edge("A", "M2", 0, in_u=False, in_v=True)
        r_bad = mv_bad.record_edge("M2", "B", -1, in_u=False, in_v=True)

        self.assertEqual(r_bad["status"], "MAYER_VIETORIS_CONNECTING_OBSTRUCTION_LGGR")
        self.assertEqual(r_bad["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(r_bad["u_locally_exact"])
        self.assertTrue(r_bad["v_locally_exact"])
        self.assertFalse(r_bad["union_globally_exact"])
        self.assertEqual(r_bad["overlap_vertices"], ["A", "B"])
        self.assertEqual(r_bad["intersection_difference_cocycle"], {"A": "0", "B": "3"})
        self.assertEqual(r_bad["connecting_coboundary_spread"], "3")
        self.assertIsNone(r_bad["glued_global_potential"])
        self.assertTrue(r_bad["intersection_cocycle_locally_constant_verified"])
        self.assertTrue(r_bad["mayer_vietoris_equivalence_verified"])

        # 2. Compatible locally exact cover: U has A->M1->B with sum 1+1=2,
        #    V has A->M2->B with sum 3+(-1)=2 -> delta(A) = 0, delta(B) = 0 -> glues globally!
        mv_ok = StreamingMayerVietorisMonitor(scope_id="mv-exact-circle")
        mv_ok.record_edge("A", "M1", 1, in_u=True, in_v=False)
        mv_ok.record_edge("M1", "B", 1, in_u=True, in_v=False)
        mv_ok.record_edge("A", "M2", 3, in_u=False, in_v=True)
        r_ok = mv_ok.record_edge("M2", "B", -1, in_u=False, in_v=True)

        self.assertEqual(r_ok["status"], "MAYER_VIETORIS_EXACT_GLUED_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(r_ok["u_locally_exact"])
        self.assertTrue(r_ok["v_locally_exact"])
        self.assertTrue(r_ok["union_globally_exact"])
        self.assertEqual(r_ok["connecting_coboundary_spread"], "0")
        self.assertEqual(
            r_ok["glued_global_potential"],
            {"A": "0", "B": "2", "M1": "1", "M2": "3"},
        )
        self.assertTrue(r_ok["mayer_vietoris_equivalence_verified"])

    def test_hodge_decomposition_exact_coexact_and_harmonic_separation(self) -> None:
        """Verify orthogonal discrete Hodge decomposition into exact, coexact, and harmonic components."""
        mon = StreamingHodgeDecompositionMonitor(scope_id="hodge-test")

        # Triangle D0: e0=(v0->v1), e1=(v1->v2), e2=(v2->v0)
        d0_tri = [
            [-1, 1, 0],
            [0, -1, 1],
            [1, 0, -1],
        ]

        # 1. Purely exact gradient h = (1, 2, -3) = D0([0, 1, 3])
        r_exact = mon.record_complex_cochain("tri_exact", d0_tri, [1, 2, -3], D1=None)
        self.assertEqual(r_exact["classification"], "EXACT_GRADIENT_LGGG")
        self.assertEqual(r_exact["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_exact["h_exact"], ["1", "2", "-3"])
        self.assertEqual(r_exact["h_coexact"], ["0", "0", "0"])
        self.assertEqual(r_exact["h_harmonic"], ["0", "0", "0"])
        self.assertTrue(r_exact["orthogonality_verified"])
        self.assertTrue(r_exact["pythagorean_energy_verified"])

        # 2. Unfilled triangle with h = (3, 0, 0) -> h_exact = (2, -1, -1), h_harm = (1, 1, 1)
        r_harm = mon.record_complex_cochain("tri_unfilled_harmonic", d0_tri, [3, 0, 0], D1=None)
        self.assertEqual(r_harm["classification"], "HARMONIC_COHOMOLOGY_OBSTRUCTION_LGGR")
        self.assertEqual(r_harm["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_harm["h_exact"], ["2", "-1", "-1"])
        self.assertEqual(r_harm["h_coexact"], ["0", "0", "0"])
        self.assertEqual(r_harm["h_harmonic"], ["1", "1", "1"])
        self.assertEqual(r_harm["norm2_total"], "9")
        self.assertEqual(r_harm["norm2_exact"], "6")
        self.assertEqual(r_harm["norm2_harmonic"], "3")
        self.assertTrue(r_harm["laplacian_kernel_verified"])

        # 3. Filled triangle D1 = [[1, 1, 1]] with h = (3, 0, 0) -> h_exact = (2, -1, -1),
        #    h_coexact = (1, 1, 1), h_harm = (0, 0, 0)
        r_coexact = mon.record_complex_cochain("tri_filled_coexact", d0_tri, [3, 0, 0], D1=[[1, 1, 1]])
        self.assertEqual(r_coexact["classification"], "COEXACT_CURL_OBSTRUCTION_LGGR")
        self.assertEqual(r_coexact["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_coexact["h_exact"], ["2", "-1", "-1"])
        self.assertEqual(r_coexact["h_coexact"], ["1", "1", "1"])
        self.assertEqual(r_coexact["h_harmonic"], ["0", "0", "0"])
        self.assertEqual(r_coexact["norm2_coexact"], "3")
        self.assertEqual(r_coexact["norm2_harmonic"], "0")

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_hodge_decomposition.v1")
        self.assertEqual(receipt["status"], "HODGE_OBSTRUCTED_LGGR")
        self.assertEqual(receipt["harmonic_obstructed_ids"], ["tri_unfilled_harmonic"])
        self.assertEqual(receipt["coexact_obstructed_ids"], ["tri_filled_coexact"])
        self.assertTrue(receipt["all_orthogonality_verified"])
        self.assertTrue(receipt["all_pythagorean_energy_verified"])
        self.assertTrue(receipt["all_laplacian_kernels_verified"])

    def test_dfa_grammar_gluing_boundary_state_mismatch_vs_reset_coherence(self) -> None:
        """Verify DFA tape grammar gluing separates non-reset accepting boundary NGD from reset-coherent LGGG."""
        # 3-state DFA: q0 (initial, accepting on reset), q1 (accepting single 'a'), q2 (sink on second 'a')
        # Here F = {"q0", "q1"} so 'r' (stay at q0) is a reset-accepting segment,
        # while 'a' (q0 -> q1) is a non-reset accepting segment that moves to q2 on a second 'a'.
        transitions = {
            "q0": {"a": "q1", "r": "q0"},
            "q1": {"a": "q2", "r": "q0"},
            "q2": {"a": "q2", "r": "q2"},
        }

        # 1. Non-reset boundary mismatch NGD: w1 = ["a"] (q0->q1 in F) and w2 = ["a"] (q0->q1 in F locally,
        #    but q1->q2 not in F globally!)
        dfa_ngd = StreamingDFAGrammarGluingMonitor(
            ["q0", "q1", "q2"],
            ["a", "r"],
            transitions,
            "q0",
            ["q0", "q1"],
            scope_id="dfa-ngd-test",
        )
        s1 = dfa_ngd.record_segment("seg_1", ["a"])
        s2 = dfa_ngd.record_segment("seg_2", ["a"])
        self.assertEqual(s1["local_pass_from_q0"], 1)
        self.assertFalse(s1["is_reset_idempotent_on_q0"])
        self.assertEqual(s2["local_pass_from_q0"], 1)
        self.assertEqual(s2["chained_end_state"], "q2")
        self.assertEqual(s2["chained_prefix_accepted"], 0)

        r_ngd = dfa_ngd.get_receipt()
        self.assertEqual(r_ngd["schema"], "lggr.online_dfa_grammar_gluing.v1")
        self.assertEqual(r_ngd["status"], "DFA_BOUNDARY_STATE_MISMATCH_NGD_LGGR")
        self.assertEqual(r_ngd["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_ngd["local_product_aggregator"], 1)
        self.assertEqual(r_ngd["global_concatenated_evaluator"], 0)
        self.assertEqual(r_ngd["evaluator_defect"], -1)
        self.assertEqual(r_ngd["non_reset_accepting_segment_ids"], ["seg_1", "seg_2"])
        self.assertTrue(r_ngd["all_monoid_homomorphisms_verified"])

        # 2. Reset-coherent LGGG: w1 = ["a", "r"] (q0->q1->q0 in F, reset-idempotent) followed by w2 = ["a"] (q0->q1 in F)
        dfa_ok = StreamingDFAGrammarGluingMonitor(
            ["q0", "q1", "q2"],
            ["a", "r"],
            transitions,
            "q0",
            ["q0", "q1"],
            scope_id="dfa-ok-test",
        )
        dfa_ok.record_segment("seg_reset", ["a", "r"])
        dfa_ok.record_segment("seg_next", ["a"])
        r_ok = dfa_ok.get_receipt()
        self.assertEqual(r_ok["status"], "DFA_CONCATENATION_COHERENT_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_ok["evaluator_defect"], 0)
        self.assertTrue(r_ok["all_monoid_homomorphisms_verified"])

    def test_catalyst_degradation_residual_accumulation_and_cycle_ceiling(self) -> None:
        """Verify constructor catalyst degradation monitor separates bounded cycles from multi-cycle exhaustion NGD."""
        # 1. Multi-cycle exhaustion NGD: tau_cat = 5, per_cycle_local_tolerance = 2, wear = +2 per cycle
        #    Cycle ceiling = floor(5 / 2) = 2; cycle 3 reaches cumulative wear 6 > 5 -> NGD (L=1, Eg=0, Delta_E=-1)
        cat_ngd = StreamingCatalystDegradationMonitor(
            initial_catalyst_state=10,
            catalyst_tolerance=5,
            per_cycle_local_tolerance=2,
            scope_id="catalyst-exhaustion-test",
        )
        c1 = cat_ngd.record_cycle("cyc_1", "S0", "S1", True, 2)
        c2 = cat_ngd.record_cycle("cyc_2", "S0", "S1", True, 2)
        c3 = cat_ngd.record_cycle("cyc_3", "S0", "S1", True, 2)

        self.assertEqual(c1["uniform_wear_cycle_ceiling"], 2)
        self.assertTrue(c1["within_global_catalyst_tolerance"])
        self.assertTrue(c2["within_global_catalyst_tolerance"])
        self.assertFalse(c3["within_global_catalyst_tolerance"])

        r_ngd = cat_ngd.get_receipt()
        self.assertEqual(r_ngd["schema"], "lggr.online_catalyst_degradation.v1")
        self.assertEqual(r_ngd["status"], "CATALYST_DEGRADATION_EXHAUSTION_NGD_LGGR")
        self.assertEqual(r_ngd["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_ngd["local_product_aggregator"], 1)
        self.assertEqual(r_ngd["global_evaluator"], 0)
        self.assertEqual(r_ngd["evaluator_defect"], -1)
        self.assertEqual(r_ngd["cumulative_catalyst_drift"], "6")
        self.assertEqual(r_ngd["exhausted_cycle_ids"], ["cyc_3"])
        self.assertTrue(r_ngd["all_telescoping_identities_verified"])

        # 2. Ideal exact catalyst restoration: wear +1 followed by regeneration -1 -> terminal drift 0, max dev 1 <= 5
        cat_bounded = StreamingCatalystDegradationMonitor(
            initial_catalyst_state=10,
            catalyst_tolerance=5,
            per_cycle_local_tolerance=2,
            scope_id="catalyst-bounded-test",
        )
        cat_bounded.record_cycle("cyc_1", "S0", "S1", True, 1)
        cat_bounded.record_cycle("cyc_2", "S0", "S1", True, -1)
        r_bounded = cat_bounded.get_receipt()
        self.assertEqual(r_bounded["status"], "BOUNDED_APPROXIMATE_CATALYST_LGGG")
        self.assertEqual(r_bounded["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_bounded["cumulative_catalyst_drift"], "0")
        self.assertEqual(r_bounded["max_catalyst_deviation"], "1")
        self.assertEqual(r_bounded["evaluator_defect"], 0)

    def test_discrete_curvature_hodge_laplacian_dirichlet_energy_and_kernel(self) -> None:
        """Verify discrete 1-form Hodge Laplacian Dirichlet energy identity and harmonic kernel separation."""
        mon = StreamingDiscreteCurvatureMonitor(scope_id="curvature-test")
        d0_tri = [
            [-1, 1, 0],
            [0, -1, 1],
            [1, 0, -1],
        ]

        # 1. Exact gradient flow h = (1, 2, -3) = D0([0, 1, 3]) -> curl = 0, div = (-4, -1, 5), E_div = 16+1+25 = 42
        r_grad = mon.record_laplacian_probe("tri_gradient", d0_tri, [1, 2, -3], D1=[[1, 1, 1]])
        self.assertEqual(r_grad["classification"], "PURE_DIVERGENCE_GRADIENT_FLOW_LGGG")
        self.assertEqual(r_grad["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_grad["divergence_energy"], "42")
        self.assertEqual(r_grad["curl_energy"], "0")
        self.assertEqual(r_grad["dirichlet_energy"], "42")
        self.assertFalse(r_grad["in_laplacian_kernel"])
        self.assertTrue(r_grad["dirichlet_energy_identity_verified"])
        self.assertTrue(r_grad["operator_orthogonality_verified"])

        # 2. Unfilled triangle with h = (1, 1, 1) -> D0^T h = (0, 0, 0), D1 = None -> E_Dir = 0, in ker(L1)
        r_harm = mon.record_laplacian_probe("tri_unfilled_harmonic", d0_tri, [1, 1, 1], D1=None)
        self.assertEqual(r_harm["classification"], "HARMONIC_ZERO_ENERGY_KERNEL_OBSTRUCTION_LGGR")
        self.assertEqual(r_harm["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_harm["dirichlet_energy"], "0")
        self.assertTrue(r_harm["in_laplacian_kernel"])
        self.assertFalse(r_harm["is_exact_coboundary"])
        self.assertTrue(r_harm["kernel_equivalence_verified"])

        # 3. Filled triangle D1 = [[1, 1, 1]] with h = (1, 1, 1) -> D0^T h = (0, 0, 0), D1 h = (3) -> E_Dir = 9
        r_curl = mon.record_laplacian_probe("tri_filled_curl", d0_tri, [1, 1, 1], D1=[[1, 1, 1]])
        self.assertEqual(r_curl["classification"], "CURL_OR_MIXED_ENERGY_OBSTRUCTION_LGGR")
        self.assertEqual(r_curl["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_curl["divergence_energy"], "0")
        self.assertEqual(r_curl["curl_energy"], "9")
        self.assertEqual(r_curl["dirichlet_energy"], "9")
        self.assertFalse(r_curl["in_laplacian_kernel"])

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_discrete_curvature.v1")
        self.assertEqual(receipt["status"], "CURVATURE_OR_HARMONIC_OBSTRUCTED_LGGR")
        self.assertEqual(receipt["harmonic_kernel_probe_ids"], ["tri_unfilled_harmonic"])
        self.assertEqual(receipt["curl_obstructed_probe_ids"], ["tri_filled_curl"])
        self.assertTrue(receipt["all_dirichlet_energy_identities_verified"])
        self.assertTrue(receipt["all_operator_orthogonalities_verified"])
        self.assertTrue(receipt["all_kernel_equivalences_verified"])

    def test_contextual_sheaf_three_cycle_presheaf_obstruction_vs_global_section(self) -> None:
        """Verify 3-cycle empirical presheaf monitor separates Specker hollow-triangle contextuality from global joint sections."""
        mon = StreamingContextualSheafMonitor(scope_id="contextual-sheaf-test")

        # 1. Specker / anti-correlated 3-cycle: p_XY = (0, 1/2, 1/2, 0) on AB, BC, CA
        #    Pairwise marginals all equal 1/2 (no-signaling), yet d000 + d111 = -1/2 < 0 -> no global section!
        anti = ["0", "1/2", "1/2", "0"]
        r_ctx = mon.record_three_cycle_model("specker_hollow_triangle", anti, anti, anti)
        self.assertEqual(r_ctx["classification"], "CONTEXTUAL_HOLLOW_TRIANGLE_OBSTRUCTION_LGGR")
        self.assertEqual(r_ctx["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(r_ctx["no_signaling_verified"])
        self.assertEqual(r_ctx["d000_plus_d111_invariant"], "-1/2")
        self.assertEqual(r_ctx["alpha_min"], "0")
        self.assertEqual(r_ctx["alpha_max"], "-1/2")
        self.assertEqual(r_ctx["infeasibility_gap"], "1/2")
        self.assertFalse(r_ctx["global_section_exists"])
        self.assertIsNone(r_ctx["witness_global_joint"])
        self.assertTrue(r_ctx["affine_marginal_recovery_verified"])

        # 2. Positively correlated 3-cycle: p_XY = (1/2, 0, 0, 1/2) on AB, BC, CA -> global GHZ-like mixture 1/2|000> + 1/2|111>
        corr = ["1/2", "0", "0", "1/2"]
        r_ok = mon.record_three_cycle_model("correlated_global_section", corr, corr, corr)
        self.assertEqual(r_ok["classification"], "GLOBAL_JOINT_SECTION_EXTENSIBLE_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertTrue(r_ok["no_signaling_verified"])
        self.assertTrue(r_ok["global_section_exists"])
        self.assertEqual(r_ok["witness_global_joint"]["000"], "1/2")
        self.assertEqual(r_ok["witness_global_joint"]["111"], "1/2")
        self.assertTrue(r_ok["affine_marginal_recovery_verified"])

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_contextual_sheaf.v1")
        self.assertEqual(receipt["status"], "PRESHEAF_SECTION_OBSTRUCTED_LGGR")
        self.assertEqual(receipt["contextual_obstructed_model_ids"], ["specker_hollow_triangle"])
        self.assertEqual(receipt["signaling_obstructed_model_ids"], [])
        self.assertTrue(receipt["all_affine_marginal_recoveries_verified"])

    def test_regge_deficit_curvature_and_discrete_gauss_bonnet(self) -> None:
        """Verify 2D Regge hinge deficit curvature monitor separates conical apex NGD from flat 6-triangle stars."""
        # 1. Conical 4-equilateral-triangle pyramid around interior apex 'v0' with boundary 'b1..b4'
        #    Each equilateral triangle has angles (1/6, 1/6, 1/6) summing to 1/2 -> L = 1
        #    Interior deficit at v0: 1 - 4*(1/6) = 1/3 != 0 -> E_g = 0, Delta_E = -1
        #    Boundary turns at b1..b4: 1/2 - 2*(1/6) = 1/6 each -> Gauss-Bonnet sum = 1/3 + 4*(1/6) = 1 = chi
        cone = StreamingReggeDeficitCurvatureMonitor(
            interior_vertices=["v0"],
            boundary_vertices=["b1", "b2", "b3", "b4"],
            scope_id="regge-cone-test",
        )
        eq_angles = ["1/6", "1/6", "1/6"]
        cone.record_triangle("t1", ["v0", "b1", "b2"], eq_angles)
        cone.record_triangle("t2", ["v0", "b2", "b3"], eq_angles)
        cone.record_triangle("t3", ["v0", "b3", "b4"], eq_angles)
        cone.record_triangle("t4", ["v0", "b4", "b1"], eq_angles)

        r_cone = cone.get_receipt()
        self.assertEqual(r_cone["schema"], "lggr.online_regge_deficit_curvature.v1")
        self.assertEqual(r_cone["status"], "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR")
        self.assertEqual(r_cone["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_cone["euler_characteristic"], 1)
        self.assertEqual(r_cone["interior_deficits"], {"v0": "1/3"})
        self.assertEqual(r_cone["sum_boundary_turn"], "2/3")
        self.assertEqual(r_cone["total_gauss_bonnet_curvature"], "1")
        self.assertEqual(r_cone["local_product_aggregator"], 1)
        self.assertEqual(r_cone["global_flatness_evaluator"], 0)
        self.assertEqual(r_cone["evaluator_defect"], -1)
        self.assertTrue(r_cone["angle_balance_identity_verified"])
        self.assertTrue(r_cone["gauss_bonnet_euler_identity_verified"])

        # 2. Flat 6-equilateral-triangle hexagonal wheel around interior vertex 'v0' with boundary 'b1..b6'
        #    Interior deficit at v0: 1 - 6*(1/6) = 0 -> E_g = 1, Delta_E = 0
        #    Boundary turns at b1..b6: 1/2 - 2*(1/6) = 1/6 each -> Gauss-Bonnet sum = 0 + 6*(1/6) = 1 = chi
        flat = StreamingReggeDeficitCurvatureMonitor(
            interior_vertices=["v0"],
            boundary_vertices=["b1", "b2", "b3", "b4", "b5", "b6"],
            scope_id="regge-flat-test",
        )
        for i in range(6):
            u = f"b{i + 1}"
            w = f"b{((i + 1) % 6) + 1}"
            flat.record_triangle(f"hex_{i + 1}", ["v0", u, w], eq_angles)

        r_flat = flat.get_receipt()
        self.assertEqual(r_flat["status"], "FLAT_EUCLIDEAN_LATTICE_LGGG")
        self.assertEqual(r_flat["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_flat["interior_deficits"], {"v0": "0"})
        self.assertEqual(r_flat["total_gauss_bonnet_curvature"], "1")
        self.assertEqual(r_flat["evaluator_defect"], 0)
        self.assertTrue(r_flat["gauss_bonnet_euler_identity_verified"])

    def test_pullback_square_compatibility_and_universal_cone_mediator(self) -> None:
        """Verify categorical fibered pullback monitor separates interface mismatch NGD from universal cone mediators."""
        # Cospan A -f-> C <-g- B:
        # f(a0) = c0, f(a1) = c1, f(a2) = c1
        # g(b0) = c0, g(b1) = c1
        # Pullback carrier P = {(a0, b0, c0), (a1, b1, c1), (a2, b1, c1)}
        f_map = {"a0": "c0", "a1": "c1", "a2": "c1"}
        g_map = {"b0": "c0", "b1": "c1"}

        mon = StreamingPullbackSquareMonitor(f_map, g_map, scope_id="pullback-test")

        # 1. Compatible pair (a0, b0) over singleton fiber c0
        p1 = mon.record_branch_pair("pair_c0_unique", "a0", "b0")
        self.assertTrue(p1["in_pullback_square"])
        self.assertEqual(p1["evaluator_defect"], 0)
        self.assertTrue(p1["interface_uniquely_identifies_pair"])

        # 2. Compatible pair (a1, b1) over size-2 fiber c1
        p2 = mon.record_branch_pair("pair_c1_ambiguous", "a1", "b1")
        self.assertTrue(p2["in_pullback_square"])
        self.assertEqual(p2["interface_fiber_size"], 2)
        self.assertFalse(p2["interface_uniquely_identifies_pair"])

        # 3. Interface mismatch NGD pair (a2, b0): f(a2) = c1 != c0 = g(b0)
        p3 = mon.record_branch_pair("pair_mismatch_ngd", "a2", "b0")
        self.assertFalse(p3["in_pullback_square"])
        self.assertEqual(p3["local_product"], 1)
        self.assertEqual(p3["global_pullback_evaluator"], 0)
        self.assertEqual(p3["evaluator_defect"], -1)

        # 4. Commuting cone W = {w0, w1} vs non-commuting cone
        c_ok = mon.verify_cone_mediator("cone_valid", {"w0": "a0", "w1": "a2"}, {"w0": "b0", "w1": "b1"})
        self.assertTrue(c_ok["commutes_over_c"])
        self.assertEqual(c_ok["universal_mediator"], {"w0": ["a0", "b0"], "w1": ["a2", "b1"]})
        self.assertTrue(c_ok["mediator_uniqueness_and_projection_verified"])

        c_bad = mon.verify_cone_mediator("cone_invalid", {"w0": "a0", "w1": "a2"}, {"w0": "b0", "w1": "b0"})
        self.assertFalse(c_bad["commutes_over_c"])
        self.assertEqual(c_bad["mismatched_apex_states"], ["w1"])
        self.assertIsNone(c_bad["universal_mediator"])

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_pullback_square.v1")
        self.assertEqual(receipt["status"], "PULLBACK_INTERFACE_MISMATCH_NGD_LGGR")
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(receipt["pullback_carrier_size"], 3)
        self.assertEqual(receipt["ngd_mismatch_pair_ids"], ["pair_mismatch_ngd"])
        self.assertEqual(receipt["ambiguous_fiber_pair_ids"], ["pair_c1_ambiguous"])

    def test_martingale_optional_stopping_expectation_conservation_vs_tail_drawdown_ngd(self) -> None:
        """Verify bounded-horizon martingale optional stopping conservation vs asymmetric tail drawdown NGD."""
        mon = StreamingMartingaleOptionalStoppingMonitor(
            max_tail_drawdown_budget=1,
            scope_id="martingale-ost-test",
        )

        # 1. Double-or-nothing asymmetric stopping on fair martingale:
        #    x0 = 0; step 1: (+1, -1); step 2 from -1: (+1, -3)
        #    Stop at step 1 if up (+1, prob 1/2), continue to step 2 if down (+1 prob 1/4, -3 prob 1/4)
        #    Stopped expectation = 1/2*(1) + 1/4*(1) + 1/4*(-3) = 0 == x0, win prob = 3/4,
        #    but tail drawdown = 0 - (-3) = 3 > 1 -> NGD (L=1, Eg=0, Delta_E=-1)
        r_skew = mon.record_stopped_tree(
            "double_or_nothing_skew",
            x0=0,
            x_u=1,
            x_d=-1,
            x_uu=2,
            x_ud=0,
            x_du=1,
            x_dd=-3,
            stop_on_step1_up=True,
            stop_on_step1_down=False,
        )
        self.assertEqual(r_skew["classification"], "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR")
        self.assertEqual(r_skew["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_skew["stopped_expectation"], "0")
        self.assertEqual(r_skew["horizon2_expectation"], "0")
        self.assertEqual(r_skew["stopped_win_probability"], "3/4")
        self.assertEqual(r_skew["tail_drawdown"], "3")
        self.assertEqual(r_skew["local_martingale_product"], 1)
        self.assertEqual(r_skew["global_drawdown_evaluator"], 0)
        self.assertEqual(r_skew["evaluator_defect"], -1)
        self.assertTrue(r_skew["optional_stopping_conservation_verified"])

        # 2. Immediate stop at t=1 on both branches: (+1, -1) -> tail drawdown = 1 <= 1 -> LGGG
        r_ok = mon.record_stopped_tree(
            "bounded_step1_stop",
            x0=0,
            x_u=1,
            x_d=-1,
            x_uu=2,
            x_ud=0,
            x_du=0,
            x_dd=-2,
            stop_on_step1_up=True,
            stop_on_step1_down=True,
        )
        self.assertEqual(r_ok["classification"], "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_ok["stopped_expectation"], "0")
        self.assertEqual(r_ok["tail_drawdown"], "1")
        self.assertEqual(r_ok["evaluator_defect"], 0)

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_martingale_optional_stopping.v1")
        self.assertEqual(receipt["status"], "OPTIONAL_STOPPING_DRAWDOWN_OBSTRUCTED_LGGR")
        self.assertEqual(receipt["tail_drawdown_ngd_tree_ids"], ["double_or_nothing_skew"])
        self.assertTrue(receipt["all_optional_stopping_conservations_verified"])

    def test_projective_tower_derived_limit_r1_lifting_obstruction(self) -> None:
        """Verify LGGR IV projective tower monitor separates 3x+1=0 mod 2^n R^1 lim^1 obstruction from integer lifts."""
        # 1. Obstructed 3x + 1 = 0 (mod 2^n) tower: x1 = 1 (mod 2), x2 = 1 (mod 4), x3 = 5 (mod 8)
        #    Every finite stage is solvable and compatible (L = 1), yet x_inf = -1/3 not in Z -> Eg = 0, Delta_E = -1
        tower_bad = StreamingProjectiveTowerMonitor(3, 1, scope_id="tower-3x-plus-1")
        tower_bad.record_stage("stage_mod_2", 2, 1)
        tower_bad.record_stage("stage_mod_4", 4, 1)
        tower_bad.record_stage("stage_mod_8", 8, 5)

        r_bad = tower_bad.get_receipt()
        self.assertEqual(r_bad["schema"], "lggr.online_projective_tower.v1")
        self.assertEqual(r_bad["status"], "DERIVED_LIMIT_R1_LIFTING_OBSTRUCTION_NGD_LGGR")
        self.assertEqual(r_bad["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(r_bad["rational_completion_root"], "-1/3")
        self.assertIsNone(r_bad["integral_global_root"])
        self.assertEqual(r_bad["r1_lim_coset_residual_mod_z"], "2/3")
        self.assertEqual(r_bad["local_product_aggregator"], 1)
        self.assertEqual(r_bad["global_integral_lift_evaluator"], 0)
        self.assertEqual(r_bad["evaluator_defect"], -1)

        # 2. Positive control: 3x - 6 = 0 (mod 2^n) with x1 = 0 (mod 2), x2 = 2 (mod 4), x3 = 2 (mod 8)
        #    Global integer root x_* = 2 in Z lifts all stages -> L = 1, Eg = 1, Delta_E = 0
        tower_ok = StreamingProjectiveTowerMonitor(3, -6, scope_id="tower-3x-minus-6")
        tower_ok.record_stage("stage_mod_2", 2, 0)
        tower_ok.record_stage("stage_mod_4", 4, 2)
        tower_ok.record_stage("stage_mod_8", 8, 2)

        r_ok = tower_ok.get_receipt()
        self.assertEqual(r_ok["status"], "INTEGRAL_GLOBAL_LIFT_COHERENT_LGGG")
        self.assertEqual(r_ok["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r_ok["integral_global_root"], 2)
        self.assertEqual(r_ok["r1_lim_coset_residual_mod_z"], "0")
        self.assertEqual(r_ok["evaluator_defect"], 0)

    def test_skew_repair_norm_attainment_divergence_and_l1_budget_breach(self) -> None:
        """Verify LGGR V Remark LGR-R4 skew repair monitor separates l^infty attainment from l^1 budget."""
        from lggr import StreamingSkewRepairMonitor

        mon = StreamingSkewRepairMonitor(scope_id="skew-repair-audit")

        # 1. Non-exact probe omega = (1, -1) with 2a - b = 3 != 0:
        #    alpha_1 = 1/2 (Phi_1 = 3/2), alpha_2 = 1/5 (Phi_2^2 = 9/5), alpha_inf = 0 (Phi_inf = 1).
        #    Selecting candidate_alpha = alpha_inf = 0 passes coordinatewise l^infty bounds <= 1 (L = 1),
        #    but incurs ||r(0)||_1 = 2 > 3/2 = Phi_1 (Eg = 0, Delta_E = -1).
        p_div = mon.record_probe("omega_1_minus_1_linf_selected", 1, -1)
        self.assertEqual(p_div["skew_discrepancy_2a_minus_b"], "3")
        self.assertEqual(p_div["alpha_1"], "1/2")
        self.assertEqual(p_div["alpha_2"], "1/5")
        self.assertEqual(p_div["alpha_inf"], "0")
        self.assertEqual(p_div["phi_1"], "3/2")
        self.assertEqual(p_div["phi_2_squared"], "9/5")
        self.assertEqual(p_div["phi_inf"], "1")
        self.assertTrue(p_div["closed_form_identities_hold"])
        self.assertTrue(p_div["minimizers_strictly_diverge"])
        self.assertEqual(p_div["candidate_l1_cost"], "2")
        self.assertEqual(p_div["local_product_aggregator"], 1)
        self.assertEqual(p_div["global_l1_budget_evaluator"], 0)
        self.assertEqual(p_div["evaluator_defect"], -1)
        self.assertEqual(p_div["probe_status"], "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR")

        # 2. Exact probe omega = (1, 2) with 2a - b = 0:
        #    alpha_1 = alpha_2 = alpha_inf = -1, Phi_1 = Phi_2^2 = Phi_inf = 0 -> L = 1, Eg = 1, Delta_E = 0
        p_exact = mon.record_probe("omega_1_2_exact", 1, 2)
        self.assertEqual(p_exact["skew_discrepancy_2a_minus_b"], "0")
        self.assertEqual(p_exact["alpha_1"], "-1")
        self.assertEqual(p_exact["alpha_2"], "-1")
        self.assertEqual(p_exact["alpha_inf"], "-1")
        self.assertFalse(p_exact["minimizers_strictly_diverge"])
        self.assertEqual(p_exact["evaluator_defect"], 0)
        self.assertEqual(p_exact["probe_status"], "SKEW_REPAIR_BUDGET_COHERENT_LGGG")

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_skew_repair.v1")
        self.assertEqual(receipt["status"], "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR")
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(receipt["all_closed_form_identities_verified"])
        self.assertEqual(receipt["skew_norm_divergence_probe_ids"], ["omega_1_minus_1_linf_selected"])

    def test_mermin_peres_magic_square_parity_obstruction(self) -> None:
        """Verify 3x3 Mermin-Peres parity monitor separates 6-context satisfiability from global parity obstruction."""
        from lggr import StreamingMerminPeresParityMonitor

        mon = StreamingMerminPeresParityMonitor(scope_id="mermin-peres-audit")

        # 1. Canonical Mermin-Peres magic square: row targets (+1, +1, +1), col targets (+1, +1, -1)
        #    All 6 contexts are locally satisfied (L = 1), yet prod(R) = +1 != -1 = prod(C),
        #    so max_satisfied = 5 out of 6, min_violated = 1, Eg = 0, Delta_E = -1.
        g_mp = mon.record_grid(
            "mermin_peres_canonical",
            row_targets=[1, 1, 1],
            col_targets=[1, 1, -1],
        )
        self.assertEqual(g_mp["row_target_product"], 1)
        self.assertEqual(g_mp["col_target_product"], -1)
        self.assertTrue(g_mp["parity_mismatch_obstruction"])
        self.assertEqual(g_mp["max_satisfied_contexts_out_of_6"], 5)
        self.assertEqual(g_mp["min_violated_contexts"], 1)
        self.assertEqual(g_mp["global_noncontextual_witness_count"], 0)
        self.assertFalse(g_mp["global_noncontextual_assignment_exists"])
        self.assertEqual(g_mp["local_product_aggregator"], 1)
        self.assertEqual(g_mp["global_noncontextual_evaluator"], 0)
        self.assertEqual(g_mp["evaluator_defect"], -1)
        self.assertEqual(g_mp["grid_status"], "MERMIN_PERES_PARITY_OBSTRUCTION_LGGR")

        # 2. Positive control: non-contextual parity targets (+1, +1, +1) and (+1, +1, +1)
        #    prod(R) = +1 == +1 = prod(C), 16 global non-contextual witnesses exist -> L = 1, Eg = 1, Delta_E = 0
        g_ok = mon.record_grid(
            "noncontextual_even_grid",
            row_targets=[1, 1, 1],
            col_targets=[1, 1, 1],
        )
        self.assertFalse(g_ok["parity_mismatch_obstruction"])
        self.assertEqual(g_ok["max_satisfied_contexts_out_of_6"], 6)
        self.assertEqual(g_ok["min_violated_contexts"], 0)
        self.assertEqual(g_ok["global_noncontextual_witness_count"], 16)
        self.assertTrue(g_ok["global_noncontextual_assignment_exists"])
        self.assertEqual(g_ok["evaluator_defect"], 0)
        self.assertEqual(g_ok["grid_status"], "NONCONTEXTUAL_PARITY_COHERENT_LGGG")

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_mermin_peres_parity.v1")
        self.assertEqual(receipt["status"], "MERMIN_PERES_PARITY_OBSTRUCTION_LGGR")
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(receipt["parity_obstructed_grid_ids"], ["mermin_peres_canonical"])

    def test_side_information_channel_capacity_and_fiber_error_floor(self) -> None:
        """Verify 012_rsi/002 IK-04/IK-05 side-information capacity monitor enforces K - S error floor."""
        from lggr import StreamingSideInformationCapacityMonitor

        mon = StreamingSideInformationCapacityMonitor(scope_id="side-info-capacity-audit")

        # 1. Capacity-deficient 1-bit channel (S = 2) on a 4-value report fiber (K = 4):
        #    Every state emits a valid symbol in {0, 1} (L = 1), yet K - S = 4 - 2 = 2
        #    forces at least 2 distinct-target collisions (Eg = 0, Delta_E = -1).
        f_bad = mon.record_fiber_channel(
            "fiber_k4_s2_deficit",
            [
                {"state_id": "x0", "query_value": 10, "side_symbol": 0},
                {"state_id": "x1", "query_value": 20, "side_symbol": 0},
                {"state_id": "x2", "query_value": 30, "side_symbol": 1},
                {"state_id": "x3", "query_value": 40, "side_symbol": 1},
            ],
            channel_capacity_s=2,
            error_budget=0,
        )
        self.assertEqual(f_bad["distinct_query_values_k"], 4)
        self.assertEqual(f_bad["channel_capacity_s"], 2)
        self.assertEqual(f_bad["capacity_error_floor_k_minus_s"], 2)
        self.assertEqual(f_bad["realized_subfiber_error_floor"], 2)
        self.assertEqual(f_bad["realized_sample_error_floor"], 2)
        self.assertTrue(f_bad["pigeonhole_bound_verified"])
        self.assertEqual(f_bad["local_product_aggregator"], 1)
        self.assertEqual(f_bad["global_decodability_evaluator"], 0)
        self.assertEqual(f_bad["evaluator_defect"], -1)
        self.assertEqual(f_bad["fiber_status"], "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR")

        # 2. Positive control: 2-bit channel (S = 4 >= K = 4) with injective side symbols:
        #    Each sub-fiber has 1 distinct query value -> error floor = 0, L = 1, Eg = 1, Delta_E = 0
        f_ok = mon.record_fiber_channel(
            "fiber_k4_s4_sufficient",
            [
                {"state_id": "x0", "query_value": 10, "side_symbol": 0},
                {"state_id": "x1", "query_value": 20, "side_symbol": 1},
                {"state_id": "x2", "query_value": 30, "side_symbol": 2},
                {"state_id": "x3", "query_value": 40, "side_symbol": 3},
            ],
            channel_capacity_s=4,
            error_budget=0,
        )
        self.assertEqual(f_ok["capacity_error_floor_k_minus_s"], 0)
        self.assertEqual(f_ok["realized_subfiber_error_floor"], 0)
        self.assertEqual(f_ok["evaluator_defect"], 0)
        self.assertEqual(f_ok["fiber_status"], "SIDE_INFORMATION_SUFFICIENT_LGGG")

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_side_information_capacity.v1")
        self.assertEqual(receipt["status"], "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR")
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(receipt["all_pigeonhole_bounds_verified"])
        self.assertEqual(receipt["capacity_deficit_fiber_ids"], ["fiber_k4_s2_deficit"])

    def test_product_of_experts_disjoint_support_collapse_vs_mixture(self) -> None:
        """Verify LGGR I §7.2 Product-of-Experts monitor separates disjoint-support collapse from MoE."""
        from lggr import StreamingProductOfExpertsMonitor

        mon = StreamingProductOfExpertsMonitor(scope_id="poe-vs-moe-audit")

        # 1. Disjoint supports: Expert 1 = [1, 0], Expert 2 = [0, 1]
        #    Both experts have positive mass (L = 1) and D_MoE = 1 > 0,
        #    yet D_PoE = 1*0 + 0*1 = 0 collapses (Eg = 0, Delta_E = -1).
        r_bad = mon.record_expert_scores("disjoint_experts", [[1, 0], [0, 1]])
        self.assertEqual(r_bad["expert_masses"], ["1", "1"])
        self.assertEqual(r_bad["joint_support_indices"], [])
        self.assertEqual(r_bad["poe_partition_sum"], "0")
        self.assertIsNone(r_bad["poe_normalized_distribution"])
        self.assertEqual(r_bad["moe_partition_sum"], "1")
        self.assertEqual(r_bad["moe_normalized_distribution"], ["1/2", "1/2"])
        self.assertEqual(r_bad["local_product_aggregator"], 1)
        self.assertEqual(r_bad["global_poe_normalizable_evaluator"], 0)
        self.assertEqual(r_bad["evaluator_defect"], -1)
        self.assertEqual(r_bad["round_status"], "POE_DISJOINT_SUPPORT_COLLAPSE_LGGR")

        # 2. Overlapping supports: Expert 1 = [1, 1], Expert 2 = [1, 0]
        #    D_PoE = 1 > 0 -> L = 1, Eg = 1, Delta_E = 0
        r_ok = mon.record_expert_scores("overlapping_experts", [[1, 1], [1, 0]])
        self.assertEqual(r_ok["joint_support_indices"], [0])
        self.assertEqual(r_ok["poe_partition_sum"], "1")
        self.assertEqual(r_ok["poe_normalized_distribution"], ["1", "0"])
        self.assertEqual(r_ok["evaluator_defect"], 0)
        self.assertEqual(r_ok["round_status"], "POE_AND_MOE_COHERENT_LGGG")

        receipt = mon.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_product_of_experts.v1")
        self.assertEqual(receipt["status"], "POE_DISJOINT_SUPPORT_COLLAPSE_LGGR")
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertEqual(receipt["poe_collapsed_round_ids"], ["disjoint_experts"])

    def test_infeasible_coupled_empty_intersection_oscillation_and_escalation(self) -> None:
        """Verify Theorem 57 infeasible coupled empty-intersection oscillation detection & escalation."""
        from lggr import StreamingJointMultiMonitorRepairGuard

        guard = StreamingJointMultiMonitorRepairGuard(scope_id="infeasible-coupled-audit")

        candidates = [
            {"action_id": "S=2_alpha=0", "global_a_pass": False, "global_b_pass": True},
            {"action_id": "S=4_alpha=-4/3", "global_a_pass": True, "global_b_pass": False},
        ]

        # Disagreement between feasible_intersection_empty and candidate_actions must raise ValidationError
        with self.assertRaises(ValidationError):
            guard.record_coupled_trajectory(
                "bad_mismatch",
                pair_name="Infeasible_SideInfo_x_SkewRepair",
                monitor_a_name="StreamingSideInformationCapacityMonitor",
                monitor_b_name="StreamingSkewRepairMonitor",
                model_id="synthetic",
                feasible_intersection_empty=False,
                candidate_actions=candidates,
                rounds=[
                    {
                        "feedback_mode": "r0",
                        "status_a": "OBSTRUCTED",
                        "status_b": "OBSTRUCTED",
                        "local_a_pass": True,
                        "global_a_pass": False,
                        "local_b_pass": True,
                        "global_b_pass": False,
                    },
                    {
                        "feedback_mode": "r1",
                        "status_a": "PASS",
                        "status_b": "OBSTRUCTED",
                        "local_a_pass": True,
                        "global_a_pass": True,
                        "local_b_pass": True,
                        "global_b_pass": False,
                    },
                ],
            )

        rec = guard.record_coupled_trajectory(
            "oscillating_infeasible_traj",
            pair_name="Infeasible_SideInfo_x_SkewRepair",
            monitor_a_name="StreamingSideInformationCapacityMonitor",
            monitor_b_name="StreamingSkewRepairMonitor",
            model_id="synthetic",
            feasible_intersection_empty=True,
            candidate_actions=candidates,
            rounds=[
                {
                    "feedback_mode": "r0_baseline",
                    "status_a": "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR",
                    "status_b": "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR",
                    "local_a_pass": True,
                    "global_a_pass": False,
                    "local_b_pass": True,
                    "global_b_pass": False,
                },
                {
                    "feedback_mode": "r1_priority_a",
                    "status_a": "SIDE_INFORMATION_SUFFICIENT_LGGG",
                    "status_b": "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR",
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": False,
                },
                {
                    "feedback_mode": "r2_priority_b",
                    "status_a": "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR",
                    "status_b": "SKEW_REPAIR_BUDGET_COHERENT_LGGG",
                    "local_a_pass": True,
                    "global_a_pass": False,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
            ],
        )
        self.assertTrue(rec["feasible_intersection_empty"])
        self.assertTrue(rec["whack_a_mole_oscillation_detected"])
        self.assertEqual(rec["oscillation_l1_step_distance"], 2)
        self.assertTrue(rec["halted_and_escalated"])
        self.assertEqual(
            rec["trajectory_status"],
            "INFEASIBLE_EMPTY_INTERSECTION_OSCILLATION_HALTED_AND_ESCALATED_LGGR",
        )
        self.assertEqual(
            rec["escalation_action"],
            "HALT_OSCILLATING_REPAIR_AND_ESCALATE_INFEASIBLE_COUPLED_CONSTRAINTS",
        )

        receipt = guard.get_receipt()
        self.assertEqual(receipt["status"], "INFEASIBLE_COUPLED_REGIME_HALTED_AND_ESCALATED_LGGR")
        self.assertEqual(receipt["whack_a_mole_oscillation_rate"], "1")
        self.assertEqual(receipt["halt_and_escalate_rate"], "1")

    def test_governed_policy_relaxation_handoff_vs_self_relaxation(self) -> None:
        """Verify StreamingGovernedPolicyRelaxationMonitor separates unauthorized self-relaxation from external authority handoff."""
        mon = StreamingGovernedPolicyRelaxationMonitor(
            scope_id="unit_governed_policy_relaxation"
        )
        p0 = BudgetPolicy(
            policy_id="coupled-sideinfo-skew/v1",
            spec_id="side-channel-capacity-and-l1-skew-budget/v1",
            evaluator_id="joint-sideinfo-skew/v1",
            representation_id="channel-capacity-s/v1",
            authority_id="external-owner/v1",
            allowed_states=(1, 2),
            max_step=2,
            max_total=2,
            query_scope="every_prefix",
        )
        p1 = BudgetPolicy(
            policy_id="coupled-sideinfo-skew/v2-relaxed",
            spec_id="side-channel-capacity-and-l1-skew-budget/v2",
            evaluator_id="joint-sideinfo-skew/v1",
            representation_id="channel-capacity-s/v1",
            authority_id="external-human-authority-gate/v2",
            allowed_states=(1, 2, 3, 4),
            max_step=3,
            max_total=4,
            query_scope="every_prefix",
        )
        esc_sha = "a" * 64

        # Identical prior and relaxed policy SHA-256 must raise ValidationError
        with self.assertRaises(ValidationError):
            mon.record_relaxation_handoff(
                handoff_id="bad_same_policy",
                pair_name="Relaxed_SideInfo_x_SkewRepair",
                model_id="synthetic",
                prior_escalation_receipt_sha256=esc_sha,
                prior_policy_sha256=p0.sha256,
                relaxed_policy_sha256=p0.sha256,
                authority_id=p1.authority_id,
                authority_grant_verified=True,
                pre_handoff_halted_and_escalated=True,
                relaxed_candidate_actions=[
                    {"action_id": "S=4_alpha=0", "global_a_pass": True, "global_b_pass": True}
                ],
                unauthorized_self_relaxation_attempt={
                    "authority_grant_verified": False,
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
                post_handoff_round={
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
            )

        rec = mon.record_relaxation_handoff(
            handoff_id="handoff_valid_1",
            pair_name="Relaxed_SideInfo_x_SkewRepair",
            model_id="synthetic",
            prior_escalation_receipt_sha256=esc_sha,
            prior_policy_sha256=p0.sha256,
            relaxed_policy_sha256=p1.sha256,
            authority_id=p1.authority_id,
            authority_grant_verified=True,
            pre_handoff_halted_and_escalated=True,
            relaxed_candidate_actions=[
                {"action_id": "S=2_alpha=0", "global_a_pass": False, "global_b_pass": True},
                {"action_id": "S=4_alpha=0_relaxed_B1=4", "global_a_pass": True, "global_b_pass": True},
            ],
            unauthorized_self_relaxation_attempt={
                "authority_grant_verified": False,
                "local_a_pass": True,
                "global_a_pass": True,
                "local_b_pass": True,
                "global_b_pass": True,
            },
            post_handoff_round={
                "round_index": 2,
                "local_a_pass": True,
                "global_a_pass": True,
                "local_b_pass": True,
                "global_b_pass": True,
                "status_a": "SIDE_INFORMATION_SUFFICIENT_LGGG",
                "status_b": "SKEW_REPAIR_BUDGET_COHERENT_LGGG",
            },
        )
        self.assertTrue(rec["digest_chain_valid"])
        self.assertTrue(rec["relaxed_pareto_nonempty"])
        self.assertTrue(rec["unauthorized_self_relaxation_attempt"]["rejected"])
        self.assertEqual(
            rec["unauthorized_self_relaxation_attempt"]["status"],
            "UNAUTHORIZED_SELF_RELAXATION_REJECTED_LGGR",
        )
        self.assertEqual(rec["unauthorized_self_relaxation_attempt"]["defect"], -1)
        self.assertTrue(rec["pareto_restored"])
        self.assertEqual(rec["handoff_status"], "GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG")

        receipt = mon.emit_receipt()
        self.assertEqual(receipt["status"], "GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["unauthorized_self_relaxation_rejection_rate"], "1")
        self.assertEqual(receipt["post_handoff_pareto_restoration_rate"], "1")

    def test_minimum_slack_policy_relaxation_vs_over_permissive_grant(self) -> None:
        """Verify StreamingMinimumSlackPolicyRelaxationMonitor separates over-permissive grants from minimum-slack Pareto relaxations."""
        mon = StreamingMinimumSlackPolicyRelaxationMonitor(
            scope_id="unit_minimum_slack_policy_relaxation"
        )
        esc_sha = "a" * 64
        p0_sha = "b" * 64
        p1_sha = "c" * 64
        p2_sha = "d" * 64
        p3_sha = "e" * 64

        rec = mon.record_minimum_slack_evaluation(
            evaluation_id="eval_min_slack_1",
            pair_name="MinSlack_SideInfo_x_SkewRepair",
            model_id="synthetic",
            prior_escalation_receipt_sha256=esc_sha,
            prior_policy_sha256=p0_sha,
            prior_policy_vector=[2, 2, 2],
            candidate_policies=[
                {
                    "policy_id": "P1_under_relaxed",
                    "policy_sha256": p1_sha,
                    "policy_vector": [3, 3, 3],
                    "restores_pareto_intersection": False,
                },
                {
                    "policy_id": "P2_minimum_slack_pareto",
                    "policy_sha256": p2_sha,
                    "policy_vector": [4, 4, 4],
                    "restores_pareto_intersection": True,
                },
                {
                    "policy_id": "P3_over_permissive_grant",
                    "policy_sha256": p3_sha,
                    "policy_vector": [8, 8, 8],
                    "restores_pareto_intersection": True,
                },
            ],
            rounds=[
                {
                    "round_index": 0,
                    "feedback_mode": "round_1_heuristic_headroom_selection",
                    "selected_policy_id": "P3_over_permissive_grant",
                    "authority_grant_verified": True,
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
                {
                    "round_index": 1,
                    "feedback_mode": "round_2_minimum_slack_receipt_audited",
                    "selected_policy_id": "P2_minimum_slack_pareto",
                    "authority_grant_verified": True,
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
            ],
        )
        self.assertEqual(rec["minimum_pareto_l1_slack"], "6")
        self.assertEqual(rec["optimal_minimum_slack_policy_ids"], ["P2_minimum_slack_pareto"])
        self.assertTrue(rec["round_1_over_permissive_breach"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        # Round 1 (P3): local_pass=True, global_pass=False, defect=-1, excess_slack=12
        r0 = rec["rounds"][0]
        self.assertTrue(r0["local_pass"])
        self.assertFalse(r0["global_pass"])
        self.assertEqual(r0["defect"], -1)
        self.assertEqual(r0["selected_l1_policy_slack"], "18")
        self.assertEqual(r0["excess_policy_slack_l1"], "12")
        self.assertEqual(
            r0["round_status"], "OVER_PERMISSIVE_POLICY_RELAXATION_SLACK_BREACH_LGGR"
        )

        # Round 2 (P2): local_pass=True, global_pass=True, defect=0, excess_slack=0
        r1 = rec["rounds"][1]
        self.assertTrue(r1["local_pass"])
        self.assertTrue(r1["global_pass"])
        self.assertEqual(r1["defect"], 0)
        self.assertEqual(r1["selected_l1_policy_slack"], "6")
        self.assertEqual(r1["excess_policy_slack_l1"], "0")
        self.assertEqual(
            r1["round_status"], "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG"
        )

        receipt = mon.emit_receipt()
        self.assertEqual(
            receipt["status"], "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG"
        )
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["round_1_over_permissive_breach_rate"], "1")
        self.assertEqual(receipt["single_round_minimum_slack_rate"], "0")
        self.assertEqual(receipt["multi_round_minimum_slack_rate"], "1")
        self.assertEqual(receipt["multi_round_minimum_slack_gain"], "1")

    def test_weighted_policy_relaxation_tie_breaking_vs_unweighted_slack(self) -> None:
        """Verify StreamingWeightedPolicyRelaxationMonitor separates equal-unweighted-slack ties under asymmetric risk weights."""
        mon = StreamingWeightedPolicyRelaxationMonitor(
            scope_id="unit_weighted_policy_relaxation"
        )
        esc_sha = "a" * 64
        p0_sha = "b" * 64
        pa_sha = "c" * 64
        pb_sha = "d" * 64

        rec = mon.record_weighted_relaxation_evaluation(
            evaluation_id="eval_weighted_1",
            pair_name="Weighted_SideInfo_x_SkewRepair",
            model_id="synthetic",
            prior_escalation_receipt_sha256=esc_sha,
            prior_policy_sha256=p0_sha,
            prior_policy_vector=[2, 0, 2],
            risk_weight_vector=[1, 5, 1],
            candidate_policies=[
                {
                    "policy_id": "PA_low_risk_capacity_expansion",
                    "policy_sha256": pa_sha,
                    "policy_vector": [4, 0, 4],
                    "restores_pareto_intersection": True,
                },
                {
                    "policy_id": "PB_high_risk_error_relaxation",
                    "policy_sha256": pb_sha,
                    "policy_vector": [2, 2, 4],
                    "restores_pareto_intersection": True,
                },
            ],
            rounds=[
                {
                    "round_index": 0,
                    "feedback_mode": "round_1_unweighted_tie_selection",
                    "selected_policy_id": "PB_high_risk_error_relaxation",
                    "authority_grant_verified": True,
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
                {
                    "round_index": 1,
                    "feedback_mode": "round_2_risk_weighted_receipt_audited",
                    "selected_policy_id": "PA_low_risk_capacity_expansion",
                    "authority_grant_verified": True,
                    "local_a_pass": True,
                    "global_a_pass": True,
                    "local_b_pass": True,
                    "global_b_pass": True,
                },
            ],
        )
        self.assertEqual(rec["minimum_unweighted_l1_slack"], "4")
        self.assertEqual(
            rec["unweighted_minimum_tie_policy_ids"],
            ["PA_low_risk_capacity_expansion", "PB_high_risk_error_relaxation"],
        )
        self.assertEqual(rec["minimum_weighted_l1_slack"], "4")
        self.assertEqual(rec["optimal_weighted_policy_ids"], ["PA_low_risk_capacity_expansion"])
        self.assertTrue(rec["round_1_unweighted_tie_high_risk_breach"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        # Round 1 (PB): unweighted_excess=0 (local_pass=True), weighted_excess=8 > 0 (global_pass=False, defect=-1)
        r0 = rec["rounds"][0]
        self.assertTrue(r0["local_pass"])
        self.assertFalse(r0["global_pass"])
        self.assertEqual(r0["defect"], -1)
        self.assertEqual(r0["selected_unweighted_l1_slack"], "4")
        self.assertEqual(r0["unweighted_excess_slack_l1"], "0")
        self.assertEqual(r0["selected_weighted_l1_slack"], "12")
        self.assertEqual(r0["weighted_excess_slack_l1"], "8")
        self.assertEqual(
            r0["round_status"], "UNWEIGHTED_TIE_HIGH_RISK_RELAXATION_REJECTED_LGGR"
        )

        # Round 2 (PA): unweighted_excess=0 (local_pass=True), weighted_excess=0 (global_pass=True, defect=0)
        r1 = rec["rounds"][1]
        self.assertTrue(r1["local_pass"])
        self.assertTrue(r1["global_pass"])
        self.assertEqual(r1["defect"], 0)
        self.assertEqual(r1["selected_unweighted_l1_slack"], "4")
        self.assertEqual(r1["unweighted_excess_slack_l1"], "0")
        self.assertEqual(r1["selected_weighted_l1_slack"], "4")
        self.assertEqual(r1["weighted_excess_slack_l1"], "0")
        self.assertEqual(
            r1["round_status"], "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG"
        )

        receipt = mon.emit_receipt()
        self.assertEqual(
            receipt["status"], "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG"
        )
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["round_1_unweighted_tie_high_risk_breach_rate"], "1")
        self.assertEqual(receipt["single_round_weighted_convergence_rate"], "0")
        self.assertEqual(receipt["multi_round_weighted_convergence_rate"], "1")
        self.assertEqual(receipt["multi_round_weighted_convergence_gain"], "1")

    def test_policy_ratchet_drift_vs_lease_revocation(self) -> None:
        """Theorem 61: Multi-step cumulative policy-relaxation drift (ratchet effect) vs. scoped lease revocation."""
        mon = StreamingPolicyRatchetDriftMonitor(scope_id="unit_policy_ratchet_drift")
        rec = mon.record_incident_trajectory(
            trajectory_id="ratchet_3inc_unit",
            model_id="openai/gpt-4o-mini",
            prior_escalation_receipt_sha256="sha256_prior_weighted_eval",
            baseline_policy_sha256="sha256_p0_2_3_0",
            baseline_policy_vector=[2, 3, 0],
            risk_weight_vector=[2, 3, 4],
            step_slack_budget=4,
            horizon_drift_ceiling=4,
            unrevoked_ratchet_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "prior_lease_revoked": False,
                    "authority_signature_valid": True,
                    "pre_incident_policy_vector": [2, 3, 0],
                    "post_incident_policy_vector": [4, 3, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "prior_lease_revoked": False,
                    "authority_signature_valid": True,
                    "pre_incident_policy_vector": [4, 3, 0],
                    "post_incident_policy_vector": [4, 4, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "prior_lease_revoked": False,
                    "authority_signature_valid": True,
                    "pre_incident_policy_vector": [4, 4, 0],
                    "post_incident_policy_vector": [4, 4, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
            lease_revoked_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "prior_lease_revoked": True,
                    "authority_signature_valid": True,
                    "pre_incident_policy_vector": [2, 3, 0],
                    "post_incident_policy_vector": [4, 3, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "prior_lease_revoked": True,
                    "authority_signature_valid": True,
                    "pre_incident_policy_vector": [2, 3, 0],
                    "post_incident_policy_vector": [2, 4, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "prior_lease_revoked": True,
                    "authority_signature_valid": True,
                    "pre_incident_policy_vector": [2, 3, 0],
                    "post_incident_policy_vector": [2, 3, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
        )
        p1 = rec["phase_1_unrevoked_ratchet_chain"]
        self.assertEqual(p1["local_chain_indicator_L"], 1)
        self.assertEqual(p1["global_chain_indicator_E_g"], 0)
        self.assertEqual(p1["chain_evaluator_defect"], -1)
        self.assertEqual(p1["sum_step_weighted_l1_slacks"], "11")
        self.assertEqual(p1["final_horizon_weighted_l1_drift"], "11")
        self.assertEqual(p1["max_horizon_weighted_l1_drift"], "11")
        self.assertTrue(p1["telescoping_ratchet_equality_holds"])
        self.assertEqual(p1["first_horizon_breach_incident_index"], 2)
        self.assertEqual(p1["chain_status"], "CUMULATIVE_POLICY_RATCHET_HORIZON_BREACH_LGGR")

        p2 = rec["phase_2_lease_revoked_chain"]
        self.assertEqual(p2["local_chain_indicator_L"], 1)
        self.assertEqual(p2["global_chain_indicator_E_g"], 1)
        self.assertEqual(p2["chain_evaluator_defect"], 0)
        self.assertEqual(p2["max_horizon_weighted_l1_drift"], "4")
        self.assertIsNone(p2["first_horizon_breach_incident_index"])
        self.assertEqual(p2["chain_status"], "SCOPED_LEASE_REVOCATION_HORIZON_COHERENT_LGGG")

        self.assertEqual(rec["horizon_weighted_drift_reduction"], "7")
        self.assertTrue(rec["phase_1_ratchet_horizon_breach"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        receipt = mon.emit_receipt()
        self.assertEqual(receipt["status"], "SCOPED_LEASE_REVOCATION_HORIZON_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["phase_1_ratchet_horizon_breach_rate"], "1")
        self.assertEqual(receipt["single_round_horizon_coherence_rate"], "0")
        self.assertEqual(receipt["multi_round_lease_revoked_coherence_rate"], "1")
        self.assertEqual(receipt["lease_revocation_coherence_gain"], "1")

    def test_concurrent_lease_overlap_vs_overlap_accounting(self) -> None:
        """Theorem 62: Concurrent overlapping incident leases vs. lease-overlap accounting."""
        mon = StreamingConcurrentLeaseOverlapMonitor(scope_id="unit_concurrent_lease_overlap")
        rec = mon.record_overlap_schedule(
            schedule_id="overlap_3inc_unit",
            model_id="openai/gpt-4o-mini",
            prior_ratchet_receipt_sha256="sha256_prior_ratchet_eval",
            baseline_policy_sha256="sha256_p0_2_3_0",
            baseline_policy_vector=[2, 3, 0],
            risk_weight_vector=[2, 3, 4],
            individual_lease_budget=4,
            horizon_drift_ceiling=6,
            uncoordinated_overlapping_leases=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "arrival_tick": 0,
                    "expiration_tick": 3,
                    "overlap_accounting_enforced": False,
                    "authority_signature_valid": True,
                    "lease_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "arrival_tick": 1,
                    "expiration_tick": 4,
                    "overlap_accounting_enforced": False,
                    "authority_signature_valid": True,
                    "lease_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "arrival_tick": 2,
                    "expiration_tick": 5,
                    "overlap_accounting_enforced": False,
                    "authority_signature_valid": True,
                    "lease_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
            overlap_accounted_leases=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "arrival_tick": 0,
                    "expiration_tick": 1,
                    "overlap_accounting_enforced": True,
                    "authority_signature_valid": True,
                    "lease_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "arrival_tick": 1,
                    "expiration_tick": 2,
                    "overlap_accounting_enforced": True,
                    "authority_signature_valid": True,
                    "lease_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "arrival_tick": 2,
                    "expiration_tick": 3,
                    "overlap_accounting_enforced": True,
                    "authority_signature_valid": True,
                    "lease_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
        )
        p1 = rec["phase_1_uncoordinated_overlap_schedule"]
        self.assertEqual(p1["local_schedule_indicator_L"], 1)
        self.assertEqual(p1["global_schedule_indicator_E_g"], 0)
        self.assertEqual(p1["schedule_evaluator_defect"], -1)
        self.assertEqual(p1["max_concurrent_active_leases"], 3)
        self.assertEqual(p1["overlap_tick_count"], 3)
        self.assertEqual(p1["breach_tick_count"], 3)
        self.assertEqual(p1["peak_concurrent_weighted_l1_drift"], "11")
        self.assertEqual(p1["peak_drift_tick"], 2)
        self.assertEqual(p1["first_horizon_breach_tick"], 1)
        self.assertEqual(p1["schedule_status"], "CONCURRENT_LEASE_OVERLAP_HORIZON_BREACH_LGGR")

        p2 = rec["phase_2_overlap_accounted_schedule"]
        self.assertEqual(p2["local_schedule_indicator_L"], 1)
        self.assertEqual(p2["global_schedule_indicator_E_g"], 1)
        self.assertEqual(p2["schedule_evaluator_defect"], 0)
        self.assertEqual(p2["max_concurrent_active_leases"], 1)
        self.assertEqual(p2["overlap_tick_count"], 0)
        self.assertEqual(p2["breach_tick_count"], 0)
        self.assertEqual(p2["peak_concurrent_weighted_l1_drift"], "4")
        self.assertIsNone(p2["first_horizon_breach_tick"])
        self.assertEqual(p2["schedule_status"], "LEASE_OVERLAP_ACCOUNTING_HORIZON_COHERENT_LGGG")

        self.assertEqual(rec["peak_concurrent_weighted_drift_reduction"], "7")
        self.assertTrue(rec["phase_1_overlap_horizon_breach"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        receipt = mon.emit_receipt()
        self.assertEqual(receipt["status"], "LEASE_OVERLAP_ACCOUNTING_HORIZON_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["phase_1_overlap_horizon_breach_rate"], "1")
        self.assertEqual(receipt["single_round_overlap_coherence_rate"], "0")
        self.assertEqual(receipt["multi_round_overlap_accounted_coherence_rate"], "1")
        self.assertEqual(receipt["overlap_accounting_coherence_gain"], "1")

    def test_simultaneous_budget_split_vs_priority_queueing(self) -> None:
        """Theorem 63: Non-preemptible simultaneous incidents under fractional budget-splitting vs. priority queueing."""
        mon = StreamingSimultaneousBudgetSplitMonitor(scope_id="unit_simultaneous_budget_split")
        rec = mon.record_simultaneous_burst(
            burst_id="sim_burst_3inc_unit",
            model_id="openai/gpt-4o-mini",
            prior_overlap_receipt_sha256="sha256_prior_overlap_eval",
            baseline_policy_sha256="sha256_p0_2_3_0",
            baseline_policy_vector=[2, 3, 0],
            risk_weight_vector=[2, 3, 4],
            individual_lease_budget=4,
            horizon_drift_ceiling=6,
            fractional_split_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "priority_rank": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "non_preemptible": True,
                    "priority_queue_enforced": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [1, 0, 0],
                    "post_relaxation_monitor_a_passed": False,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "priority_rank": 2,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "non_preemptible": True,
                    "priority_queue_enforced": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "priority_rank": 3,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "non_preemptible": True,
                    "priority_queue_enforced": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": False,
                },
            ],
            priority_queued_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "priority_rank": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "non_preemptible": True,
                    "priority_queue_enforced": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "priority_rank": 2,
                    "arrival_tick": 0,
                    "execution_tick": 1,
                    "completion_tick": 2,
                    "non_preemptible": True,
                    "priority_queue_enforced": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "priority_rank": 3,
                    "arrival_tick": 0,
                    "execution_tick": 2,
                    "completion_tick": 3,
                    "non_preemptible": True,
                    "priority_queue_enforced": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
        )
        p1 = rec["phase_1_fractional_budget_split"]
        self.assertTrue(p1["simultaneous_arrival_verified"])
        self.assertEqual(p1["joint_simultaneous_pareto_floor_l1_w"], "11")
        self.assertTrue(p1["joint_pareto_floor_exceeds_horizon"])
        self.assertEqual(p1["local_burst_indicator_L"], 1)
        self.assertEqual(p1["global_burst_indicator_E_g"], 0)
        self.assertEqual(p1["burst_evaluator_defect"], -1)
        self.assertEqual(p1["peak_concurrent_weighted_l1_drift"], "5")
        self.assertEqual(p1["starved_incident_count"], 2)
        self.assertEqual(p1["burst_status"], "FRACTIONAL_BUDGET_SPLIT_UNDER_PARETO_FLOOR_LGGR")

        p2 = rec["phase_2_priority_queued_admission"]
        self.assertTrue(p2["simultaneous_arrival_verified"])
        self.assertEqual(p2["local_burst_indicator_L"], 1)
        self.assertEqual(p2["global_burst_indicator_E_g"], 1)
        self.assertEqual(p2["burst_evaluator_defect"], 0)
        self.assertEqual(p2["peak_concurrent_weighted_l1_drift"], "4")
        self.assertEqual(p2["starved_incident_count"], 0)
        self.assertEqual(p2["burst_status"], "PRIORITY_QUEUE_DEFERRED_ADMISSION_COHERENT_LGGG")

        self.assertEqual(rec["starved_incidents_eliminated"], 2)
        self.assertTrue(rec["phase_1_fractional_split_starvation"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        receipt = mon.emit_receipt()
        self.assertEqual(receipt["status"], "PRIORITY_QUEUE_DEFERRED_ADMISSION_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["phase_1_fractional_split_starvation_rate"], "1")
        self.assertEqual(receipt["single_round_split_coherence_rate"], "0")
        self.assertEqual(receipt["multi_round_priority_queued_coherence_rate"], "1")
        self.assertEqual(receipt["priority_queue_coherence_gain"], "1")

    def test_deadline_priority_queue_static_vs_edf(self) -> None:
        """Theorem 64: Deadline-constrained priority queueing under simultaneous bursts (static priority vs. EDF)."""
        mon = StreamingDeadlinePriorityQueueMonitor(scope_id="unit_deadline_priority_queue")
        rec = mon.record_deadline_queue_comparison(
            queue_id="deadline_queue_3inc_unit",
            model_id="openai/gpt-4o-mini",
            prior_split_receipt_sha256="sha256_prior_split_eval",
            baseline_policy_sha256="sha256_p0_2_3_0",
            baseline_policy_vector=[2, 3, 0],
            risk_weight_vector=[2, 3, 4],
            individual_lease_budget=4,
            horizon_drift_ceiling=6,
            static_priority_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "static_priority_rank": 1,
                    "sla_deadline_tick": 3,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "edf_policy_enforced": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "static_priority_rank": 2,
                    "sla_deadline_tick": 2,
                    "arrival_tick": 0,
                    "execution_tick": 1,
                    "completion_tick": 2,
                    "edf_policy_enforced": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "static_priority_rank": 3,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 2,
                    "completion_tick": 3,
                    "edf_policy_enforced": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
            edf_queued_incidents=[
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "static_priority_rank": 3,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "edf_policy_enforced": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "static_priority_rank": 2,
                    "sla_deadline_tick": 2,
                    "arrival_tick": 0,
                    "execution_tick": 1,
                    "completion_tick": 2,
                    "edf_policy_enforced": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "static_priority_rank": 1,
                    "sla_deadline_tick": 3,
                    "arrival_tick": 0,
                    "execution_tick": 2,
                    "completion_tick": 3,
                    "edf_policy_enforced": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
        )
        p1 = rec["phase_1_static_priority_queue"]
        self.assertTrue(p1["simultaneous_arrival_verified"])
        self.assertFalse(p1["edf_order_verified"])
        self.assertEqual(p1["local_queue_indicator_L"], 1)
        self.assertEqual(p1["global_queue_indicator_E_g"], 0)
        self.assertEqual(p1["queue_evaluator_defect"], -1)
        self.assertEqual(p1["max_lateness_ticks"], 2)
        self.assertEqual(p1["deadline_miss_count"], 1)
        self.assertEqual(p1["queue_status"], "STATIC_PRIORITY_SLA_DEADLINE_BREACH_LGGR")

        p2 = rec["phase_2_edf_deadline_queue"]
        self.assertTrue(p2["simultaneous_arrival_verified"])
        self.assertTrue(p2["edf_order_verified"])
        self.assertEqual(p2["local_queue_indicator_L"], 1)
        self.assertEqual(p2["global_queue_indicator_E_g"], 1)
        self.assertEqual(p2["queue_evaluator_defect"], 0)
        self.assertEqual(p2["max_lateness_ticks"], 0)
        self.assertEqual(p2["deadline_miss_count"], 0)
        self.assertEqual(p2["queue_status"], "EDF_DEADLINE_COHERENT_QUEUE_VERIFIED_LGGG")

        self.assertEqual(rec["max_lateness_reduction_ticks"], 2)
        self.assertTrue(rec["phase_1_static_deadline_breach"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        receipt = mon.emit_receipt()
        self.assertEqual(receipt["status"], "EDF_DEADLINE_COHERENT_QUEUE_VERIFIED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["phase_1_static_deadline_breach_rate"], "1")
        self.assertEqual(receipt["single_round_static_deadline_coherence_rate"], "0")
        self.assertEqual(receipt["multi_round_edf_deadline_coherence_rate"], "1")
        self.assertEqual(receipt["edf_deadline_coherence_gain"], "1")

    def test_overloaded_deadline_bin_packing_and_escalation(self) -> None:
        """Theorem 65: Overloaded SLA deadline bursts (serial EDF overload vs. halt-and-escalate vs. selective bin-packing)."""
        mon = StreamingOverloadedDeadlineBinPackingMonitor(
            scope_id="unit_overloaded_deadline_bin_packing"
        )
        rec = mon.record_overloaded_deadline_burst(
            burst_id="overloaded_burst_3inc_unit",
            model_id="openai/gpt-4o-mini",
            prior_deadline_receipt_sha256="sha256_prior_deadline_eval",
            baseline_policy_sha256="sha256_p0_2_3_0",
            baseline_policy_vector=[2, 3, 0],
            risk_weight_vector=[2, 3, 4],
            individual_lease_budget=4,
            initial_horizon_drift_ceiling=6,
            expanded_horizon_drift_ceiling=7,
            serial_edf_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "static_priority_rank": 1,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "selective_bin_packing_enforced": False,
                    "halt_and_escalate_triggered": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "static_priority_rank": 2,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 1,
                    "completion_tick": 2,
                    "selective_bin_packing_enforced": False,
                    "halt_and_escalate_triggered": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "static_priority_rank": 3,
                    "sla_deadline_tick": 2,
                    "arrival_tick": 0,
                    "execution_tick": 2,
                    "completion_tick": 3,
                    "selective_bin_packing_enforced": False,
                    "halt_and_escalate_triggered": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
            overload_escalation_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "static_priority_rank": 1,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "selective_bin_packing_enforced": False,
                    "halt_and_escalate_triggered": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "static_priority_rank": 2,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "selective_bin_packing_enforced": False,
                    "halt_and_escalate_triggered": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "static_priority_rank": 3,
                    "sla_deadline_tick": 2,
                    "arrival_tick": 0,
                    "execution_tick": 1,
                    "completion_tick": 2,
                    "selective_bin_packing_enforced": False,
                    "halt_and_escalate_triggered": True,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
            selective_bin_packed_incidents=[
                {
                    "incident_index": 1,
                    "incident_pair_id": "SideInfo_x_SkewRepair",
                    "static_priority_rank": 1,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "selective_bin_packing_enforced": True,
                    "halt_and_escalate_triggered": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [2, 0, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 2,
                    "incident_pair_id": "PoE_x_SkewRepair",
                    "static_priority_rank": 2,
                    "sla_deadline_tick": 1,
                    "arrival_tick": 0,
                    "execution_tick": 0,
                    "completion_tick": 1,
                    "selective_bin_packing_enforced": True,
                    "halt_and_escalate_triggered": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 3,
                    "allocated_delta_vector": [0, 1, 0],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
                {
                    "incident_index": 3,
                    "incident_pair_id": "ProjectiveTower_x_MerminPeres",
                    "static_priority_rank": 3,
                    "sla_deadline_tick": 2,
                    "arrival_tick": 0,
                    "execution_tick": 1,
                    "completion_tick": 2,
                    "selective_bin_packing_enforced": True,
                    "halt_and_escalate_triggered": False,
                    "authority_signature_valid": True,
                    "minimum_weighted_pareto_floor": 4,
                    "allocated_delta_vector": [0, 0, 1],
                    "post_relaxation_monitor_a_passed": True,
                    "post_relaxation_monitor_b_passed": True,
                },
            ],
        )
        p1 = rec["phase_1_serial_edf_overload"]
        self.assertEqual(p1["local_phase_indicator_L"], 1)
        self.assertEqual(p1["global_phase_indicator_E_g"], 0)
        self.assertEqual(p1["phase_evaluator_defect"], -1)
        self.assertEqual(p1["deadline_miss_count"], 2)
        self.assertEqual(p1["max_lateness_ticks"], 1)
        self.assertEqual(p1["phase_status"], "SERIAL_EDF_SLA_DEADLINE_OVERLOAD_LGGR")

        p2 = rec["phase_2_overload_halt_and_escalate"]
        self.assertEqual(p2["mandatory_slot0_pareto_load_l1_w"], "7")
        self.assertTrue(p2["slot0_overload_infeasible_under_horizon"])
        self.assertEqual(p2["required_emergency_horizon_ceiling"], "7")
        self.assertEqual(p2["required_emergency_horizon_expansion"], "1")
        self.assertTrue(p2["halt_and_escalate_verified"])
        self.assertEqual(p2["local_phase_indicator_L"], 1)
        self.assertEqual(p2["global_phase_indicator_E_g"], 0)
        self.assertEqual(p2["phase_evaluator_defect"], -1)
        self.assertEqual(
            p2["phase_status"], "OVERLOADED_DEADLINE_BURST_HALTED_AND_ESCALATED_LGGR"
        )

        p3 = rec["phase_3_selective_bin_packed_edf"]
        self.assertEqual(p3["local_phase_indicator_L"], 1)
        self.assertEqual(p3["global_phase_indicator_E_g"], 1)
        self.assertEqual(p3["phase_evaluator_defect"], 0)
        self.assertEqual(p3["peak_concurrent_weighted_l1_drift"], "7")
        self.assertEqual(p3["deadline_miss_count"], 0)
        self.assertEqual(p3["max_lateness_ticks"], 0)
        self.assertEqual(p3["phase_status"], "EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG")

        self.assertEqual(rec["deadline_misses_eliminated"], 2)
        self.assertEqual(rec["max_lateness_reduction_ticks"], 1)
        self.assertTrue(rec["phase_1_serial_edf_deadline_breach"])
        self.assertTrue(rec["phase_2_halted_and_escalated"])
        self.assertFalse(rec["converged_single_round"])
        self.assertTrue(rec["converged_multi_round"])

        receipt = mon.emit_receipt()
        self.assertEqual(receipt["status"], "EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["phase_1_serial_edf_deadline_breach_rate"], "1")
        self.assertEqual(receipt["phase_2_halt_and_escalate_rate"], "1")
        self.assertEqual(receipt["single_round_serial_edf_coherence_rate"], "0")
        self.assertEqual(receipt["multi_round_bin_packed_edf_coherence_rate"], "1")
        self.assertEqual(receipt["bin_packed_edf_coherence_gain"], "1")

    def test_variable_duration_graceful_degradation_shedding(self) -> None:
        """Verify Theorem 66: multi-tick variable duration (p=(2, 1, 1)) and graceful-degradation shedding under denied horizon expansion."""
        mon = StreamingVariableDurationGracefulSheddingMonitor(
            scope_id="unit-variable-duration-shedding-scope"
        )
        rec = mon.observe_burst(
            burst_id="burst-var-dur-01",
            baseline_policy=[2, 3, 0],
            risk_weights=[2, 3, 4],
            per_incident_lease_budget=4,
            horizon_drift_ceiling=7,
            arrival_tick=0,
            expansion_denied=True,
            incidents=[
                {
                    "duration_ticks": 2,
                    "sla_deadline_tick": 2,
                    "min_weighted_pareto_floor": 4,
                    "criticality_weight": 10,
                    "phase_1_deferral_lease_delta": [2, 0, 0],
                    "phase_1_start_tick": 0,
                    "phase_1_restores_pareto": True,
                    "phase_1_candidate_passes": True,
                    "phase_2_inverted_shed_lease_delta": [0, 0, 0],
                    "phase_2_start_tick": 0,
                    "phase_2_shed": True,
                    "phase_2_restores_pareto": True,
                    "phase_2_candidate_passes": True,
                    "phase_3_governed_shed_lease_delta": [2, 0, 0],
                    "phase_3_start_tick": 0,
                    "phase_3_shed": False,
                    "phase_3_restores_pareto": True,
                    "phase_3_candidate_passes": True,
                },
                {
                    "duration_ticks": 1,
                    "sla_deadline_tick": 1,
                    "min_weighted_pareto_floor": 3,
                    "criticality_weight": 8,
                    "phase_1_deferral_lease_delta": [0, 1, 0],
                    "phase_1_start_tick": 0,
                    "phase_1_restores_pareto": True,
                    "phase_1_candidate_passes": True,
                    "phase_2_inverted_shed_lease_delta": [0, 1, 0],
                    "phase_2_start_tick": 0,
                    "phase_2_shed": False,
                    "phase_2_restores_pareto": True,
                    "phase_2_candidate_passes": True,
                    "phase_3_governed_shed_lease_delta": [0, 1, 0],
                    "phase_3_start_tick": 0,
                    "phase_3_shed": False,
                    "phase_3_restores_pareto": True,
                    "phase_3_candidate_passes": True,
                },
                {
                    "duration_ticks": 1,
                    "sla_deadline_tick": 2,
                    "min_weighted_pareto_floor": 4,
                    "criticality_weight": 3,
                    "phase_1_deferral_lease_delta": [0, 0, 1],
                    "phase_1_start_tick": 2,
                    "phase_1_restores_pareto": True,
                    "phase_1_candidate_passes": True,
                    "phase_2_inverted_shed_lease_delta": [0, 0, 1],
                    "phase_2_start_tick": 0,
                    "phase_2_shed": False,
                    "phase_2_restores_pareto": True,
                    "phase_2_candidate_passes": True,
                    "phase_3_governed_shed_lease_delta": [0, 0, 0],
                    "phase_3_start_tick": 0,
                    "phase_3_shed": True,
                    "phase_3_restores_pareto": True,
                    "phase_3_candidate_passes": True,
                },
            ],
        )
        self.assertFalse(rec["full_retention_schedulable_under_horizon"])
        self.assertEqual(rec["optimal_shed_incident_indices"], [2])
        self.assertEqual(rec["minimum_criticality_loss"], "3")
        self.assertEqual(rec["optimal_retained_criticality"], "18")
        self.assertEqual(rec["phase_1_local_green"], 1)
        self.assertEqual(rec["phase_1_global_green"], 0)
        self.assertEqual(rec["phase_1_defect"], -1)
        self.assertEqual(rec["phase_1_status"], "VARIABLE_DURATION_DEADLINE_OVERLOAD_LGGR")
        self.assertEqual(rec["phase_2_local_green"], 1)
        self.assertEqual(rec["phase_2_global_green"], 0)
        self.assertEqual(rec["phase_2_defect"], -1)
        self.assertEqual(rec["phase_2_status"], "SUBOPTIMAL_CRITICALITY_SHEDDING_LGGR")
        self.assertEqual(rec["phase_3_local_green"], 1)
        self.assertEqual(rec["phase_3_global_green"], 1)
        self.assertEqual(rec["phase_3_defect"], 0)
        self.assertEqual(rec["phase_3_status"], "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["single_round_coherence_rate"], "0")
        self.assertEqual(receipt["multi_round_graceful_shedding_coherence_rate"], "1")
        self.assertEqual(receipt["graceful_shedding_coherence_gain"], "1")

    def test_linearized_pipeline_jacobian_soundness(self) -> None:
        """Verify Theorem 67: linearized state-estimation Jacobian soundness im(D) cap ker(Q) == {0} vs. stealth blindspot."""
        mon = StreamingLinearizedPipelineJacobianMonitor(
            defect_matrix=[[1, -1, 0], [0, 1, -1], [1, 0, -1]],
            blind_measurement_matrix=[[1, 1, 0]],
            coupled_measurement_matrix=[[1, 0, 0], [0, 1, 0]],
            full_measurement_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            scope_id="unit-linearized-jacobian-scope",
        )
        obs = mon.observe_pipeline_perturbation(
            evaluation_id="eval-01",
            state_perturbation=[1, 0, 1],
        )
        self.assertEqual(obs["interface_defect_omega"], ["1", "-1", "0"])
        self.assertEqual(obs["true_l1_inconsistency"], "2")
        self.assertEqual(obs["blind_measured_l1_score"], "0")
        self.assertEqual(obs["blind_realizable_blindspot_dim"], 1)
        self.assertEqual(obs["blind_local_green"], 1)
        self.assertEqual(obs["blind_global_green"], 0)
        self.assertEqual(obs["blind_defect"], -1)
        self.assertEqual(obs["coupled_measured_l1_score"], "2")
        self.assertEqual(obs["coupled_ambient_blindspot_dim"], 1)
        self.assertEqual(obs["coupled_realizable_blindspot_dim"], 0)
        self.assertEqual(obs["coupled_local_green"], 1)
        self.assertEqual(obs["coupled_global_green"], 1)
        self.assertEqual(obs["coupled_defect"], 0)
        self.assertEqual(obs["full_realizable_blindspot_dim"], 0)
        self.assertEqual(obs["full_defect"], 0)

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "COUPLED_SOUNDNESS_VERIFIED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["blind_coherence_rate"], "0")
        self.assertEqual(receipt["coupled_coherence_rate"], "1")
        self.assertEqual(receipt["coupled_soundness_gain"], "1")

    def test_watcher_dropout_gram_rank_deficiency(self) -> None:
        """Verify Theorem 68: watcher-dropout and Gram rank-deficiency audit along task-critical directions."""
        mon = StreamingWatcherDropoutGramAuditMonitor(
            observation_matrix=[
                [1, 1, 0],
                [2, 2, 0],
                [0, 1, 1],
                [1, 0, 1],
            ],
            scope_id="unit-watcher-dropout-gram-scope",
        )
        obs = mon.observe_watcher_dropout(
            evaluation_id="eval-drop-01",
            critical_direction=[1, -1, 1],
            redundant_dropout_row=1,
            critical_dropout_row=3,
        )
        self.assertEqual(obs["full_rank"], 3)
        self.assertEqual(obs["full_nullspace_dim"], 0)
        self.assertEqual(obs["full_norm_squared"], "4")
        self.assertEqual(obs["redundant_dropout_rank"], 3)
        self.assertEqual(obs["redundant_dropout_nullspace_dim"], 0)
        self.assertEqual(obs["redundant_dropout_norm_squared"], "4")
        self.assertEqual(obs["redundant_local_green"], 1)
        self.assertEqual(obs["redundant_global_green"], 1)
        self.assertEqual(obs["redundant_defect"], 0)
        self.assertEqual(obs["critical_dropout_rank"], 2)
        self.assertEqual(obs["critical_dropout_nullspace_dim"], 1)
        self.assertEqual(obs["critical_dropout_norm_squared"], "0")
        self.assertEqual(obs["critical_local_green"], 1)
        self.assertEqual(obs["critical_global_green"], 0)
        self.assertEqual(obs["critical_defect"], -1)
        self.assertEqual(obs["critical_status"], "CRITICAL_WATCHER_DROPOUT_BLINDSPOT_LGGR")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "WATCHER_DROPOUT_RANK_AUDIT_VERIFIED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["dropout_ranks_by_row"], [3, 3, 2, 2])
        self.assertEqual(receipt["critical_dropout_coherence_rate"], "0")
        self.assertEqual(receipt["redundant_dropout_coherence_rate"], "1")
        self.assertEqual(receipt["watcher_retention_coherence_gain"], "1")

    def test_policy_ranking_cf_vs_neg_mass_order_reversal(self) -> None:
        """Verify Theorem 69: multi-evaluator policy ranking under CF(p) vs. N_min(p) metric order reversal."""
        mon = StreamingPolicyRankingOrderReversalMonitor(
            scope_id="unit-policy-ranking-order-reversal-scope"
        )
        obs = mon.observe_policy_pair(
            evaluation_id="eval-order-rev-01",
            num_contexts=8,
            policy_a_id="Q_5_8",
            policy_a_packing_mass="576/768",
            policy_a_negative_mass="96/768",
            policy_b_id="p_star",
            policy_b_packing_mass="540/768",
            policy_b_negative_mass="75/768",
            negative_mass_ceiling="80/768",
            phase_3_selected_policy_id="p_star",
        )
        self.assertEqual(obs["policy_a_contextual_fraction"], "1/4")
        self.assertEqual(obs["policy_a_negative_mass"], "1/8")
        self.assertEqual(obs["policy_b_contextual_fraction"], "19/64")
        self.assertEqual(obs["policy_b_negative_mass"], "25/256")
        self.assertTrue(obs["order_reversal_detected"])
        self.assertTrue(obs["policy_b_exceeds_two_negative_mass"])
        self.assertTrue(obs["m_context_bound_verified"])
        self.assertEqual(obs["phase_1_cf_only_local_green"], 1)
        self.assertEqual(obs["phase_1_cf_only_global_green"], 0)
        self.assertEqual(obs["phase_1_cf_only_defect"], -1)
        self.assertEqual(obs["phase_2_surrogate_local_green"], 1)
        self.assertEqual(obs["phase_2_surrogate_global_green"], 0)
        self.assertEqual(obs["phase_2_surrogate_defect"], -1)
        self.assertEqual(obs["phase_3_dual_local_green"], 1)
        self.assertEqual(obs["phase_3_dual_global_green"], 1)
        self.assertEqual(obs["phase_3_dual_defect"], 0)

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "DUAL_METRIC_ORDER_REVERSAL_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["cf_only_coherence_rate"], "0")
        self.assertEqual(receipt["dual_metric_coherence_rate"], "1")
        self.assertEqual(receipt["dual_metric_coherence_gain"], "1")

    def test_rsi_tool_assisted_fiber_splitting_vs_unassisted_reflection(self) -> None:
        """Verify Theorem 70: RSI unassisted self-reflection invariance vs. multi-turn tool-assisted fiber splitting."""
        mon = StreamingToolAssistedFiberSplittingMonitor(
            scope_id="unit-tool-assisted-fiber-splitting-scope"
        )
        states_spec = [
            {
                "state_id": "x00",
                "target_value": 0,
                "coarse_report": "coarse_summary_pass",
                "partial_tool_report": "bit1_low",
                "full_tool_report": "bit1_low_bit2_low",
            },
            {
                "state_id": "x01",
                "target_value": 4,
                "coarse_report": "coarse_summary_pass",
                "partial_tool_report": "bit1_low",
                "full_tool_report": "bit1_low_bit2_high",
            },
            {
                "state_id": "x10",
                "target_value": 8,
                "coarse_report": "coarse_summary_pass",
                "partial_tool_report": "bit1_high",
                "full_tool_report": "bit1_high_bit2_low",
            },
            {
                "state_id": "x11",
                "target_value": 12,
                "coarse_report": "coarse_summary_pass",
                "partial_tool_report": "bit1_high",
                "full_tool_report": "bit1_high_bit2_high",
            },
        ]
        obs = mon.evaluate_trajectory(
            trajectory_id="traj-rsi-split-01",
            states=states_spec,
            unassisted_predictions={"coarse_summary_pass": 6},
            partial_tool_predictions={"bit1_low": 2, "bit1_high": 10},
            full_tool_predictions={
                "bit1_low_bit2_low": 0,
                "bit1_low_bit2_high": 4,
                "bit1_high_bit2_low": 8,
                "bit1_high_bit2_high": 12,
            },
        )
        self.assertEqual(obs["coarse_fiber_width_w0"], "12")
        self.assertEqual(obs["coarse_minimax_floor_0"], "6")
        self.assertEqual(obs["partial_tool_width_w1"], "4")
        self.assertEqual(obs["partial_tool_floor_1"], "2")
        self.assertEqual(obs["full_tool_width_w2"], "0")
        self.assertEqual(obs["full_tool_floor_2"], "0")
        self.assertEqual(obs["unassisted_worst_case_error"], "6")
        self.assertEqual(obs["partial_tool_worst_case_error"], "2")
        self.assertEqual(obs["full_tool_worst_case_error"], "0")
        self.assertEqual(obs["phase_1_unassisted_local_green"], 1)
        self.assertEqual(obs["phase_1_unassisted_global_green"], 0)
        self.assertEqual(obs["phase_1_unassisted_defect"], -1)
        self.assertEqual(obs["phase_2_partial_tool_local_green"], 1)
        self.assertEqual(obs["phase_2_partial_tool_global_green"], 0)
        self.assertEqual(obs["phase_2_partial_tool_defect"], -1)
        self.assertEqual(obs["phase_3_full_tool_local_green"], 1)
        self.assertEqual(obs["phase_3_full_tool_global_green"], 1)
        self.assertEqual(obs["phase_3_full_tool_defect"], 0)

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["unassisted_resolution_rate"], "0")
        self.assertEqual(receipt["tool_assisted_resolution_rate"], "1")
        self.assertEqual(receipt["tool_assisted_resolution_gain"], "1")

    def test_multi_turn_pairwise_transcript_contextuality_audit(self) -> None:
        """Verify Theorem 71: multi-turn pairwise constraint contextuality audit before code generation."""
        mon = StreamingMultiTurnPairwiseTranscriptMonitor(
            scope_id="unit-multi-turn-pairwise-transcript-scope"
        )
        obs = mon.evaluate_transcript(
            transcript_id="transcript-pairwise-01",
            table_ab=["0", "1/2", "1/2", "0"],
            table_bc=["0", "1/2", "1/2", "0"],
            signaling_table_ca=["1/4", "1/2", "0", "1/4"],
            contextual_table_ca=["0", "1/2", "1/2", "0"],
            reconciled_table_ca=["1/2", "0", "0", "1/2"],
        )
        self.assertFalse(obs["phase_1_no_signaling_verified"])
        self.assertEqual(obs["phase_1_local_green"], 0)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], 0)
        self.assertEqual(obs["phase_1_status"], "SIGNALING_MARGINAL_MISMATCH_LGGR")

        self.assertTrue(obs["phase_2_no_signaling_verified"])
        self.assertEqual(obs["phase_2_alpha_min"], "0")
        self.assertEqual(obs["phase_2_alpha_max"], "-1/2")
        self.assertEqual(obs["phase_2_infeasibility_gap"], "1/2")
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "CONTEXTUAL_HOLLOW_TRIANGLE_OBSTRUCTION_LGGR")

        self.assertTrue(obs["phase_3_no_signaling_verified"])
        self.assertEqual(obs["phase_3_alpha_min"], "0")
        self.assertEqual(obs["phase_3_alpha_max"], "0")
        self.assertEqual(obs["phase_3_infeasibility_gap"], "0")
        self.assertEqual(obs["phase_3_witness_global_joint"]["010"], "1/2")
        self.assertEqual(obs["phase_3_witness_global_joint"]["101"], "1/2")
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "GLOBAL_JOINT_SECTION_EXTENSIBLE_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "PRE_GENERATION_SHEAF_RECONCILED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["ungated_contextual_coherence_rate"], "0")
        self.assertEqual(receipt["sheaf_reconciled_coherence_rate"], "1")
        self.assertEqual(receipt["sheaf_reconciliation_coherence_gain"], "1")

    def test_disagreement_preserving_side_channel_council_vs_collapsing_consensus(self) -> None:
        """Verify Theorem 72: disagreement-preserving side-channel council S >= K > 2 vs. collapsing consensus."""
        mon = StreamingDisagreementPreservingCouncilMonitor(
            scope_id="unit-disagreement-preserving-council-scope"
        )
        obs = mon.evaluate_council(
            evaluation_id="council-eval-01",
            root_causes=("auth_bypass", "race_condition", "memory_leak", "sql_injection"),
            binary_symbols=(0, 0, 1, 1),
            council_symbols=(0, 1, 2, 3),
            council_capacity_s=4,
            disjoint_expert_scores=(("1", "0"), ("0", "1")),
            shared_expert_scores=(("3/4", "1/4"), ("1/4", "3/4")),
        )
        self.assertEqual(obs["distinct_root_causes_k"], 4)
        self.assertEqual(obs["consensus_collision_floor"], 3)
        self.assertEqual(obs["binary_tag_collision_floor"], 2)
        self.assertEqual(obs["council_collision_floor"], 0)
        self.assertEqual(obs["consensus_poe_partition_sum"], "0")
        self.assertEqual(obs["council_poe_partition_sum"], "3/8")
        self.assertEqual(obs["phase_1_consensus_local_green"], 1)
        self.assertEqual(obs["phase_1_consensus_global_green"], 0)
        self.assertEqual(obs["phase_1_consensus_defect"], -1)
        self.assertEqual(obs["phase_2_binary_local_green"], 1)
        self.assertEqual(obs["phase_2_binary_global_green"], 0)
        self.assertEqual(obs["phase_2_binary_defect"], -1)
        self.assertEqual(obs["phase_3_council_local_green"], 1)
        self.assertEqual(obs["phase_3_council_global_green"], 1)
        self.assertEqual(obs["phase_3_council_defect"], 0)

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["collapsing_consensus_coherence_rate"], "0")
        self.assertEqual(receipt["disagreement_council_coherence_rate"], "1")
        self.assertEqual(receipt["disagreement_council_coherence_gain"], "1")

    def test_bounded_depth_k_induction_tower_and_carrier_completion(self) -> None:
        """Verify Theorem 73: bounded-depth symbolic execution & k-induction projective tower vs. reachable carrier."""
        mon = StreamingBoundedDepthKInductionMonitor(
            reachable_carrier_max=10,
            scope_id="unit-bounded-depth-k-induction-scope",
        )
        obs = mon.evaluate_k_induction_harness(
            evaluation_id="k-ind-eval-01",
            moduli=(2, 4, 8, 16),
            fractional_thread=(1, 1, 5, 5),
            out_of_carrier_thread=(1, 3, 7, 15),
            reachable_thread=(0, 2, 2, 2),
        )
        self.assertEqual(obs["phase_1_rational_root"], "-1/3")
        self.assertIsNone(obs["phase_1_integral_root"])
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "R1_FRACTIONAL_COMPLETION_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_2_integral_root"], -1)
        self.assertFalse(obs["phase_2_in_reachable_carrier"])
        self.assertEqual(obs["phase_2_tail_step_difference"], 8)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "OUT_OF_CARRIER_COMPLETION_WITNESS_LGGR")

        self.assertEqual(obs["phase_3_integral_root"], 2)
        self.assertTrue(obs["phase_3_in_reachable_carrier"])
        self.assertEqual(obs["phase_3_tail_step_difference"], 0)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "REACHABLE_CARRIER_LIFT_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "REACHABLE_CARRIER_LIFT_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["out_of_carrier_coherence_rate"], "0")
        self.assertEqual(receipt["reachable_carrier_coherence_rate"], "1")
        self.assertEqual(receipt["reachable_carrier_coherence_gain"], "1")

    def test_boundary_mixing_and_quorum_masking_interface_schema_audit(self) -> None:
        """Verify Theorem 74: pass-flag carrier mixing and 2-of-3 quorum masking vs. full boundary payload and strict product."""
        mon = StreamingBoundaryQuorumInterfaceMonitor(
            n_validators=3,
            quorum_k=2,
            scope_id="unit-boundary-quorum-interface-scope",
        )
        obs = mon.evaluate_interface_schema(
            evaluation_id="iface-eval-01",
            matched_boundary_left={"pass": 1, "schema_v": 2},
            matched_boundary_right={"pass": 1, "schema_v": 2},
            skew_boundary_left={"pass": 1, "schema_v": 2},
            skew_boundary_right={"pass": 1, "schema_v": 1},
            quorum_votes=(1, 1, 0),
            eg_matched=1,
            eg_skew=0,
        )
        self.assertEqual(obs["local_product"], 0)
        self.assertEqual(obs["quorum_verdict"], 1)
        self.assertEqual(obs["quorum_inflation"], 1)
        self.assertEqual(obs["phase_1_carrier_mixing_collisions"], 1)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "PASS_FLAG_CARRIER_MIXING_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_2_quorum_masked_count"], 1)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "QUORUM_MASKED_VETO_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_3_carrier_mixing_collisions"], 0)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["pass_quorum_coherence_rate"], "0")
        self.assertEqual(receipt["full_product_coherence_rate"], "1")
        self.assertEqual(receipt["interface_coherence_gain"], "1")

    def test_cross_role_schema_validation_and_double_count_audit(self) -> None:
        """Verify Theorem 75: cross-role verdict triple drift and persona double-counting vs. trace-ID deduplication."""
        mon = StreamingCrossRoleDeduplicationMonitor(
            scope_id="unit-cross-role-deduplication-scope",
        )
        obs = mon.evaluate_cross_role_log(
            evaluation_id="cross-role-eval-01",
            drift_log_entries=[
                {"trace_id": "tr-01", "role": "finite_obstruction", "e1": 1, "e2": 1, "eg": 0},
                {"trace_id": "tr-01", "role": "action_and_alignment", "e1": 1, "e2": 1, "eg": 1},
            ],
            shared_role_entries=[
                {"trace_id": "tr-01", "role": "finite_obstruction", "e1": 1, "e2": 1, "eg": 0},
                {"trace_id": "tr-01", "role": "foundations", "e1": 1, "e2": 1, "eg": 0},
                {"trace_id": "tr-02", "role": "representation", "e1": 1, "e2": 1, "eg": 0},
                {"trace_id": "tr-03", "role": "observer", "e1": 0, "e2": 1, "eg": 1},
                {"trace_id": "tr-03", "role": "continuum_shadow", "e1": 0, "e2": 1, "eg": 1},
                {"trace_id": "tr-03", "role": "action_and_alignment", "e1": 0, "e2": 1, "eg": 1},
            ],
        )
        self.assertEqual(obs["raw_role_entries_count"], 6)
        self.assertEqual(obs["unique_traces_count"], 3)
        self.assertEqual(obs["double_counted_entries_count"], 3)
        self.assertEqual(obs["raw_signed_defect_sum"], 0)
        self.assertEqual(obs["unique_signed_defect_sum"], -1)
        self.assertEqual(obs["multiplicity_inflation"], 1)

        self.assertEqual(obs["phase_1_verdict_drift_count"], 1)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "CROSS_ROLE_VERDICT_DRIFT_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "SHARED_TRACE_DOUBLE_COUNT_MASKING_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["undeduplicated_coherence_rate"], "0")
        self.assertEqual(receipt["deduplicated_coherence_rate"], "1")
        self.assertEqual(receipt["cross_role_deduplication_gain"], "1")

    def test_stage_unit_vs_e2e_integration_kernel_and_dashboard_audit(self) -> None:
        """Verify Theorem 76: stage-level unit tests vs. E2E integration oracles under path-kernel and 4-tuple dashboard."""
        mon = StreamingStageVsE2EIntegrationMonitor(
            scope_id="unit-stage-vs-e2e-integration-scope",
        )
        obs = mon.evaluate_stage_vs_e2e(
            evaluation_id="stage-e2e-eval-01",
            masked_e2e_verdicts=(1, 0, 1, 0),
            ngd_e2e_verdicts=(1, 0, 0, 0),
            repaired_e2e_verdicts=(1, 1, 0, 0),
        )
        self.assertEqual(obs["factored_stage_kernel_product"], "2")
        self.assertEqual(obs["phase_1_global_kernel"], "2")
        self.assertEqual(obs["phase_1_ngd_rate"], "1/4")
        self.assertEqual(obs["phase_1_pgd_rate"], "1/4")
        self.assertEqual(obs["phase_1_egd_rate"], "1/2")
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "CANCELLATION_MASKED_STAGE_KERNEL_LGGR")

        self.assertEqual(obs["phase_2_global_kernel"], "1")
        self.assertEqual(obs["phase_2_evaluator_residual"], "-1")
        self.assertEqual(obs["phase_2_ngd_rate"], "1/4")
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "NGD_INTEGRATION_REGRESSION_LGGR")

        self.assertEqual(obs["phase_3_global_kernel"], "2")
        self.assertEqual(obs["phase_3_egd_rate"], "0")
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["collapsing_dashboard_coherence_rate"], "0")
        self.assertEqual(receipt["four_tuple_kernel_coherence_rate"], "1")
        self.assertEqual(receipt["dashboard_kernel_coherence_gain"], "1")

    def test_three_party_no_signalling_c3_interval_family_audit(self) -> None:
        """Verify Theorem 77: parameterized 8-context three-party slice bounding c_3 in [228/75, 7]."""
        mon = StreamingThreePartyConstantBoundMonitor(
            scope_id="unit-three-party-c3-bound-scope",
        )
        obs = mon.evaluate_parameterized_slice(
            evaluation_id="c3-slice-eval-01",
            slice_steps=(0, 1, 2, 3, 4),
        )
        self.assertEqual(obs["c3_lower_bound"], "76/25")
        self.assertEqual(obs["c3_upper_bound"], "7")
        self.assertEqual(obs["interior_k2_ratio"], "140/57")
        self.assertEqual(obs["endpoint_k4_ratio"], "76/25")
        self.assertTrue(obs["ratios_strictly_increasing"])

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "BIPARTITE_C2_BOUND_VIOLATION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "C3_INTEGER_THREE_CEILING_VIOLATION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["c3_certified_lower_bound"], "76/25")
        self.assertEqual(receipt["c3_constructive_upper_bound"], "7")
        self.assertEqual(receipt["surrogate_ceiling_coherence_rate"], "0")
        self.assertEqual(receipt["certified_bracket_coherence_rate"], "1")
        self.assertEqual(receipt["c3_bracket_coherence_gain"], "1")

    def test_dynamic_boundary_schema_synthesis_under_online_collisions(self) -> None:
        """Verify Theorem 78: automated boundary schema synthesis dynamically expanding report features."""
        mon = StreamingDynamicSchemaSynthesisMonitor(
            scope_id="unit-dynamic-schema-synthesis-scope",
        )
        obs = mon.evaluate_dynamic_synthesis(
            evaluation_id="dyn-schema-eval-01",
            candidate_keys=("k_noise", "k1", "k2"),
        )
        self.assertEqual(len(obs["step_2_synthesized_keys"]), 1)
        self.assertEqual(obs["step_3_synthesized_keys"], ["k1", "k2"])
        self.assertTrue(obs["distractor_excluded"])
        self.assertEqual(obs["final_decoder_size"], 4)

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "STATIC_SCHEMA_FIBER_COLLISION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "SINGLE_FEATURE_MOVING_COLLISION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["locked_schema_coherence_rate"], "0")
        self.assertEqual(receipt["dynamic_synthesis_coherence_rate"], "1")
        self.assertEqual(receipt["dynamic_schema_coherence_gain"], "1")

    def test_adversarial_prompt_injection_schema_and_side_channel_audit(self) -> None:
        """Verify Theorem 79: adversarial prompt injection schema synthesis and side-channel bit allocation."""
        mon = StreamingAdversarialSchemaSideChannelMonitor(
            scope_id="unit-adversarial-schema-side-channel-scope",
        )
        obs = mon.evaluate_adversarial_injection(
            evaluation_id="adv-schema-eval-01",
        )
        self.assertEqual(obs["synthesized_host_keys"], ["k_host_1", "k_host_2"])
        self.assertTrue(obs["unauthenticated_key_excluded"])
        self.assertEqual(obs["distinct_injection_classes_k"], 4)
        self.assertEqual(obs["underallocated_side_channel_s"], 2)
        self.assertEqual(obs["authenticated_side_channel_s"], 4)
        self.assertEqual(obs["underallocated_collision_floor"], 2)
        self.assertEqual(obs["authenticated_collision_floor"], 0)

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "SPOOFED_METADATA_INJECTION_COLLISION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "SIDE_CHANNEL_UNDERALLOCATION_FLOOR_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["unauthenticated_or_underallocated_coherence_rate"], "0")
        self.assertEqual(receipt["host_authenticated_coherence_rate"], "1")
        self.assertEqual(receipt["host_authenticated_coherence_gain"], "1")

    def test_equal_info_baseline_vs_lggr_migration_and_obligation_audit(self) -> None:
        """Verify Theorem 80: equal-information comparative evaluation across representation migrations and obligations."""
        mon = StreamingEqualInfoMigrationObligationMonitor(
            scope_id="unit-equal-info-migration-obligation-scope",
        )
        obs = mon.evaluate_equal_info_comparison(
            evaluation_id="eq-info-eval-01",
        )
        self.assertEqual(obs["phase_1_first_fault_step"], 1)
        self.assertEqual(obs["phase_2_first_fault_step"], 1)
        self.assertEqual(obs["phase_2_retained_obligations"], ["recheck_schema_invariant"])
        self.assertIsNone(obs["phase_3_first_fault_step"])

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(
            obs["phase_1_status"],
            "UNCERTIFIED_REPRESENTATION_MIGRATION_FALSE_ACCEPT_LGGR",
        )

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(
            obs["phase_2_status"],
            "DEFERRED_OBLIGATION_PREFIX_EXCURSION_FALSE_ACCEPT_LGGR",
        )

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(
            obs["phase_3_status"],
            "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG",
        )

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["conventional_checker_soundness_rate"], "0")
        self.assertEqual(receipt["lggr_equal_info_soundness_rate"], "1")
        self.assertEqual(receipt["equal_info_soundness_gain"], "1")

    def test_multi_cycle_catalyst_wear_vs_periodic_rejuvenation_schedule(self) -> None:
        """Verify Theorem 81: multi-cycle constructor catalyst wear vs. periodic rejuvenation schedule."""
        mon = StreamingCatalystRejuvenationScheduleMonitor(
            scope_id="unit-catalyst-rejuvenation-schedule-scope",
        )
        obs = mon.evaluate_rejuvenation_schedules(
            evaluation_id="cat-rejuv-eval-01",
        )
        self.assertEqual(obs["uniform_wear_cycle_ceiling"], 3)
        self.assertEqual(obs["phase_1_max_deviation"], "4/3")
        self.assertEqual(obs["phase_2_max_deviation"], "4/3")
        self.assertEqual(obs["phase_2_terminal_deviation"], "1")
        self.assertEqual(obs["phase_3_max_deviation"], "2/3")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "UNSCHEDULED_CATALYST_WEAR_EXHAUSTION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "LATE_REJUVENATION_PREFIX_EXHAUSTION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["unscheduled_or_late_coherence_rate"], "0")
        self.assertEqual(receipt["periodic_rejuvenation_coherence_rate"], "1")
        self.assertEqual(receipt["periodic_rejuvenation_coherence_gain"], "1")

    def test_dfa_non_resetting_concatenation_vs_explicit_reset_gluing(self) -> None:
        """Verify Theorem 82: tool-call DFA non-resetting concatenation vs. explicit reset-token gluing."""
        mon = StreamingDFAResetTokenGluingMonitor(
            scope_id="unit-dfa-reset-token-gluing-scope",
        )
        obs = mon.evaluate_dfa_reset_gluing(
            evaluation_id="dfa-reset-eval-01",
        )
        self.assertEqual(obs["phase_1_terminal_state"], "q3_err")
        self.assertEqual(obs["phase_2_terminal_state"], "q3_err")
        self.assertEqual(obs["phase_3_terminal_state"], "q0_idle")
        self.assertEqual(obs["phase_1_non_reset_count"], 2)
        self.assertEqual(obs["phase_2_non_reset_count"], 1)
        self.assertEqual(obs["phase_3_non_reset_count"], 0)

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "NON_RESET_DFA_CONCATENATION_MISMATCH_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "UNRELEASED_PREFIX_TRAP_STATE_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["non_reset_concatenation_coherence_rate"], "0")
        self.assertEqual(receipt["explicit_reset_gluing_coherence_rate"], "1")
        self.assertEqual(receipt["explicit_reset_gluing_coherence_gain"], "1")

    def test_cptp_state_blindspot_vs_operator_residual_and_completion(self) -> None:
        """Verify Theorem 83: state-dependent CPTP trace preservation vs. operator residual and completion."""
        mon = StreamingCPTPBlindspotCompletionMonitor(
            scope_id="unit-cptp-blindspot-completion-scope",
        )
        obs = mon.evaluate_cptp_completion(
            evaluation_id="cptp-comp-eval-01",
        )
        self.assertEqual(obs["incomplete_residual_l1_norm"], "1")
        self.assertEqual(obs["completed_residual_l1_norm"], "0")
        self.assertEqual(obs["phase_1_trace_discrepancy"], "0")
        self.assertEqual(obs["phase_2_trace_discrepancy"], "-1")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "STATE_BLINDSPOT_NON_TP_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "EXCITED_STATE_TRACE_LEAKAGE_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["incomplete_channel_coherence_rate"], "0")
        self.assertEqual(receipt["completed_channel_coherence_rate"], "1")
        self.assertEqual(receipt["cptp_completion_coherence_gain"], "1")

    def test_mayer_vietoris_disconnected_overlap_and_coboundary_reconciliation(self) -> None:
        """Verify Theorem 84: Mayer-Vietoris disconnected interface gluing and coboundary reconciliation."""
        mon = StreamingMayerVietorisReconciliationMonitor(
            scope_id="unit-mayer-vietoris-reconciliation-scope",
        )
        obs = mon.evaluate_mv_reconciliation(
            evaluation_id="mv-reconcil-eval-01",
        )
        self.assertEqual(obs["phase_1_coboundary_spread"], "2")
        self.assertEqual(obs["phase_2_coboundary_spread"], "1")
        self.assertEqual(obs["phase_3_coboundary_spread"], "0")
        self.assertEqual(
            obs["glued_global_potential"],
            {"u": "0", "v": "0", "w0": "-1", "w1": "2"},
        )

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "MAYER_VIETORIS_CONNECTING_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "RESIDUAL_OVERLAP_SPREAD_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["unreconciled_overlap_coherence_rate"], "0")
        self.assertEqual(receipt["reconciled_coboundary_coherence_rate"], "1")
        self.assertEqual(receipt["mv_reconciliation_coherence_gain"], "1")

    def test_asynchronous_replay_order_prefix_peak_envelope_and_robustness(self) -> None:
        """Verify Theorem 85: asynchronous arrival-order permutation prefix-peak envelope and robustness."""
        mon = StreamingReplayOrderEnvelopeMonitor(
            scope_id="unit-replay-order-envelope-scope",
        )
        obs = mon.evaluate_replay_envelope(
            evaluation_id="replay-env-eval-01",
        )
        self.assertEqual(obs["phase_1_arrival_max_prefix"], "2")
        self.assertEqual(obs["phase_1_causal_max_prefix"], "4")
        self.assertEqual(obs["phase_2_causal_max_prefix"], "2")
        self.assertEqual(obs["phase_2_worst_max_prefix"], "4")
        self.assertEqual(obs["phase_3_worst_max_prefix"], "3")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "PERMUTATION_ROBUST_PREFIX_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "PERMUTATION_ROBUST_PREFIX_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["order_fragile_coherence_rate"], "0")
        self.assertEqual(receipt["permutation_robust_coherence_rate"], "1")
        self.assertEqual(receipt["replay_envelope_coherence_gain"], "1")

    def test_sliding_window_truncation_vs_horizon_rebalancing_audit(self) -> None:
        """Verify Theorem 86: sliding-window local green vs. full-horizon cumulative drift and rebalancing."""
        mon = StreamingWindowedDriftRebalancingMonitor(
            window_size=2,
            window_budget=2,
            global_budget=3,
            scope_id="unit-windowed-drift-rebalancing-scope",
        )
        obs = mon.record_rebalancing_evaluation(
            "windowed-rebal-eval-01",
            phase_1_drifts=[1, 1, 1, 1, 1, 1],
            phase_2_drifts=[1, 1, 1, 1, -1, -1],
            phase_3_drifts=[1, 1, -1, 1, -1, 1],
        )
        self.assertEqual(obs["phase_1_max_window_sum"], "2")
        self.assertEqual(obs["phase_1_cumulative_drift"], "6")
        self.assertEqual(obs["phase_2_max_window_sum"], "2")
        self.assertEqual(obs["phase_2_cumulative_drift"], "2")
        self.assertEqual(obs["phase_2_max_prefix_drift"], "4")
        self.assertEqual(obs["phase_3_max_window_sum"], "2")
        self.assertEqual(obs["phase_3_max_prefix_drift"], "2")
        self.assertEqual(obs["phase_3_cumulative_drift"], "2")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "SLIDING_WINDOW_HORIZON_BREACH_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "LATE_REBALANCING_PREFIX_HORIZON_BREACH_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "PERIODIC_REBALANCED_HORIZON_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "PERIODIC_REBALANCED_HORIZON_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["unrebalanced_coherence_rate"], "0")
        self.assertEqual(receipt["periodic_rebalanced_coherence_rate"], "1")
        self.assertEqual(receipt["horizon_rebalancing_coherence_gain"], "1")

    def test_optional_stopping_early_gain_skew_vs_tail_drawdown_cap(self) -> None:
        """Verify Theorem 87: optional-stopping early-gain halting vs. tail-drawdown cap."""
        mon = StreamingOptionalStoppingDrawdownMonitor(
            max_tail_drawdown_budget=1,
            scope_id="unit-optional-stopping-drawdown-scope",
        )
        obs = mon.record_stopping_evaluation(
            "optional-stopping-eval-01",
        )
        self.assertEqual(obs["phase_1_stopped_expectation"], "0")
        self.assertEqual(obs["phase_1_win_probability"], "3/4")
        self.assertEqual(obs["phase_1_tail_drawdown"], "3")
        self.assertEqual(obs["phase_2_stopped_expectation"], "0")
        self.assertEqual(obs["phase_2_tail_drawdown"], "2")
        self.assertEqual(obs["phase_3_stopped_expectation"], "0")
        self.assertEqual(obs["phase_3_tail_drawdown"], "1")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "RESIDUAL_TAIL_DRAWDOWN_BREACH_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["uncapped_stopping_coherence_rate"], "0")
        self.assertEqual(receipt["loss_capped_stopping_coherence_rate"], "1")
        self.assertEqual(receipt["drawdown_cap_coherence_gain"], "1")

    def test_regge_hinge_deficit_curvature_and_boundary_gauss_bonnet_holonomy(self) -> None:
        """Verify Theorem 88: 2D Regge hinge deficit curvature and boundary Gauss-Bonnet holonomy."""
        mon = StreamingReggeGaussBonnetHolonomyMonitor(
            scope_id="unit-regge-gauss-bonnet-holonomy-scope",
        )
        obs = mon.record_holonomy_evaluation(
            "regge-holonomy-eval-01",
        )
        self.assertEqual(obs["euler_characteristic"], 1)
        self.assertEqual(obs["phase_1_apex_deficit"], "1/3")
        self.assertEqual(obs["phase_1_boundary_turn_sum"], "2/3")
        self.assertEqual(obs["phase_2_apex_deficit"], "1/6")
        self.assertEqual(obs["phase_2_boundary_turn_sum"], "5/6")
        self.assertEqual(obs["phase_3_apex_deficit"], "0")
        self.assertEqual(obs["phase_3_boundary_turn_sum"], "1")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "RESIDUAL_HINGE_DEFICIT_CURVATURE_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "FLAT_EUCLIDEAN_LATTICE_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "FLAT_EUCLIDEAN_LATTICE_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["curved_star_coherence_rate"], "0")
        self.assertEqual(receipt["flat_holonomy_coherence_rate"], "1")
        self.assertEqual(receipt["regge_holonomy_coherence_gain"], "1")

    def test_coalitional_shapley_attribution_under_synergistic_fault_masking(self) -> None:
        """Verify Theorem 89: coalitional Shapley attribution under synergistic and leave-one-out fault masking."""
        mon = StreamingCoalitionalSynergyMaskingMonitor(
            scope_id="unit-coalitional-synergy-masking-scope",
        )
        obs = mon.record_synergy_evaluation(
            "coalitional-synergy-eval-01",
        )
        self.assertEqual(obs["phase_1_singleton_sum"], "0")
        self.assertEqual(obs["phase_1_synergy_term"], "-2")
        self.assertEqual(obs["phase_1_shapley_attributions"], {"A1": "-1", "A2": "-1"})
        self.assertEqual(obs["phase_2_leave_one_out_marginals"], ["0", "0"])
        self.assertEqual(obs["phase_2_synergy_term"], "1")
        self.assertEqual(obs["phase_2_shapley_attributions"], {"A1": "-1/2", "A2": "-1/2"})
        self.assertEqual(obs["phase_3_synergy_term"], "0")
        self.assertEqual(obs["phase_3_shapley_attributions"], {"A1": "0", "A2": "0"})

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "NONADDITIVE_COALITIONAL_DEFECT_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "LEAVE_ONE_OUT_MASKED_COALITIONAL_DEFECT_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["masked_coalition_coherence_rate"], "0")
        self.assertEqual(receipt["shapley_resolved_coherence_rate"], "1")
        self.assertEqual(receipt["coalitional_attribution_coherence_gain"], "1")

    def test_pullback_square_mediator_uniqueness_and_interface_factorization_audit(self) -> None:
        """Verify Theorem 90: pullback square mediator uniqueness and ambiguous interface factorization."""
        mon = StreamingPullbackMediatorFactorizationMonitor(
            scope_id="unit-pullback-mediator-factorization-scope",
        )
        obs = mon.record_factorization_evaluation(
            "pullback-factorization-eval-01",
        )
        self.assertFalse(obs["phase_1_in_pullback"])
        self.assertFalse(obs["phase_1_cone_commutes"])
        self.assertEqual(obs["phase_2_interface_fiber_size"], 4)
        self.assertFalse(obs["phase_2_interface_uniquely_identifies_pair"])
        self.assertEqual(obs["phase_3_interface_fiber_size"], 1)
        self.assertTrue(obs["phase_3_interface_uniquely_identifies_pair"])
        self.assertEqual(
            obs["phase_3_universal_mediator"],
            {
                "w0": ["a0", "b0"],
                "w1": ["a1", "b1"],
                "w2": ["a2", "b2"],
                "w3": ["a3", "b3"],
            },
        )

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "PULLBACK_INTERFACE_MISMATCH_NGD_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "AMBIGUOUS_PULLBACK_INTERFACE_FIBER_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "PULLBACK_FIBER_GLUED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "PULLBACK_FIBER_GLUED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["coarse_interface_coherence_rate"], "0")
        self.assertEqual(receipt["universal_mediator_coherence_rate"], "1")
        self.assertEqual(receipt["pullback_factorization_coherence_gain"], "1")

    def test_multi_loop_two_complex_cup_product_and_hodge_harmonic_kernel_audit(self) -> None:
        """Verify Theorem 91: multi-loop 2-complex cup-product and discrete Hodge-Laplacian harmonic kernel."""
        mon = StreamingMultiLoopCupHodgeMonitor(
            scope_id="unit-multi-loop-cup-hodge-scope",
        )
        obs = mon.record_multi_loop_evaluation(
            "multi-loop-cup-hodge-eval-01",
        )
        self.assertEqual(obs["phase_1_norm2_exact"], "6")
        self.assertEqual(obs["phase_1_norm2_coexact"], "3")
        self.assertEqual(obs["phase_1_norm2_harmonic"], "3")
        self.assertEqual(obs["phase_1_norm2_total"], "12")
        self.assertEqual(obs["phase_1_alpha_cup_beta"], "-2")
        self.assertEqual(obs["phase_2_norm2_coexact"], "0")
        self.assertEqual(obs["phase_2_norm2_harmonic"], "3")
        self.assertEqual(obs["phase_2_harmonic_dirichlet_energy"], "0")
        self.assertEqual(obs["phase_2_alpha_cup_beta"], "0")
        self.assertEqual(obs["phase_3_norm2_exact"], "8")
        self.assertEqual(obs["phase_3_norm2_coexact"], "0")
        self.assertEqual(obs["phase_3_norm2_harmonic"], "0")
        self.assertEqual(obs["phase_3_alpha_cup_beta"], "0")

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "MIXED_CURL_AND_HARMONIC_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "HARMONIC_ZERO_ENERGY_KERNEL_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "EXACT_GRADIENT_AND_CUP_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "EXACT_GRADIENT_AND_CUP_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["obstructed_multi_loop_coherence_rate"], "0")
        self.assertEqual(receipt["exact_cup_hodge_coherence_rate"], "1")
        self.assertEqual(receipt["multi_loop_hodge_coherence_gain"], "1")

    def test_figure_eight_wedge_junction_gauge_shift_and_mayer_vietoris_hodge_audit(self) -> None:
        """Verify Theorem 92: figure-eight wedge junction gauge propagation and Mayer-Vietoris Hodge audit."""
        mon = StreamingFigureEightWedgeHodgeMonitor(
            scope_id="unit-figure-eight-wedge-hodge-scope",
        )
        obs = mon.record_wedge_evaluation(
            "figure-eight-wedge-eval-01",
        )
        self.assertEqual(obs["overlap_vertices"], ["v0"])
        self.assertEqual(obs["phase_1_norm2_exact"], "6")
        self.assertEqual(obs["phase_1_norm2_coexact"], "3")
        self.assertEqual(obs["phase_1_norm2_harmonic"], "3")
        self.assertEqual(obs["phase_1_norm2_total"], "12")
        self.assertFalse(obs["phase_1_u_locally_exact"])
        self.assertFalse(obs["phase_1_v_locally_exact"])

        self.assertEqual(obs["phase_2_norm2_exact"], "2")
        self.assertEqual(obs["phase_2_norm2_coexact"], "0")
        self.assertEqual(obs["phase_2_norm2_harmonic"], "3")
        self.assertTrue(obs["phase_2_u_locally_exact"])
        self.assertFalse(obs["phase_2_v_locally_exact"])

        self.assertEqual(obs["phase_3_norm2_exact"], "20")
        self.assertEqual(obs["phase_3_norm2_coexact"], "0")
        self.assertEqual(obs["phase_3_norm2_harmonic"], "0")
        self.assertTrue(obs["phase_3_u_locally_exact"])
        self.assertTrue(obs["phase_3_v_locally_exact"])
        self.assertTrue(obs["phase_3_union_globally_exact"])
        self.assertEqual(obs["phase_3_connecting_coboundary_spread"], "0")
        self.assertEqual(
            obs["phase_3_glued_global_potential"],
            {"v0": "0", "v1": "2", "v2": "1", "v3": "3", "v4": "1"},
        )

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "WEDGE_CURL_AND_HARMONIC_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "WEDGE_HARMONIC_LOOP_OBSTRUCTION_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "WEDGE_GAUGE_GLUED_EXACT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "WEDGE_GAUGE_GLUED_EXACT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["obstructed_wedge_coherence_rate"], "0")
        self.assertEqual(receipt["synchronized_wedge_gauge_coherence_rate"], "1")
        self.assertEqual(receipt["figure_eight_wedge_coherence_gain"], "1")

    def test_shared_chord_bicyclic_diamond_hodge_and_mayer_vietoris_audit(self) -> None:
        """Verify Theorem 93: shared-chord bicyclic diamond Hodge and Mayer-Vietoris coupling audit."""
        mon = StreamingSharedChordDiamondHodgeMonitor(
            scope_id="unit-shared-chord-diamond-hodge-scope",
        )
        obs = mon.record_diamond_evaluation(
            "shared-chord-diamond-eval-01",
        )
        self.assertEqual(obs["overlap_vertices"], ["v0", "v1"])
        self.assertEqual(obs["phase_1_norm2_exact"], "3")
        self.assertEqual(obs["phase_1_norm2_coexact"], "3")
        self.assertEqual(obs["phase_1_norm2_harmonic"], "24")
        self.assertEqual(obs["phase_1_norm2_total"], "30")
        self.assertFalse(obs["phase_1_u_locally_exact"])
        self.assertFalse(obs["phase_1_v_locally_exact"])

        self.assertEqual(obs["phase_2_norm2_exact"], "3")
        self.assertEqual(obs["phase_2_norm2_coexact"], "0")
        self.assertEqual(obs["phase_2_norm2_harmonic"], "24")
        self.assertEqual(obs["phase_2_h_harmonic"], ["-2", "1", "1", "-3", "-3"])
        self.assertTrue(obs["phase_2_u_locally_exact"])
        self.assertFalse(obs["phase_2_v_locally_exact"])

        self.assertEqual(obs["phase_3_norm2_exact"], "7")
        self.assertEqual(obs["phase_3_norm2_coexact"], "0")
        self.assertEqual(obs["phase_3_norm2_harmonic"], "0")
        self.assertTrue(obs["phase_3_u_locally_exact"])
        self.assertTrue(obs["phase_3_v_locally_exact"])
        self.assertTrue(obs["phase_3_union_globally_exact"])
        self.assertEqual(obs["phase_3_connecting_coboundary_spread"], "0")
        self.assertEqual(
            obs["phase_3_glued_global_potential"],
            {"v0": "0", "v1": "1", "v2": "2", "v3": "0"},
        )

        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "DIAMOND_CHORD_CURL_AND_HARMONIC_LGGR")

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "DIAMOND_COUPLED_HARMONIC_COUNTERFLOW_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "DIAMOND_CHORD_GLUED_EXACT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "DIAMOND_CHORD_GLUED_EXACT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["obstructed_diamond_chord_coherence_rate"], "0")
        self.assertEqual(receipt["glued_diamond_chord_coherence_rate"], "1")
        self.assertEqual(receipt["shared_chord_diamond_coherence_gain"], "1")

    def test_concurrent_code_swarm_symmetry_broken_directive_vs_bilateral_oscillation(self) -> None:
        """Verify Theorem 94: concurrent code-engineering swarm interface merge and role directives."""
        mon = StreamingCodebaseInterfaceMergeMonitor(
            scope_id="unit-concurrent-code-swarm-directive-scope",
        )
        obs = mon.record_three_phase_code_swarm_audit(
            "concurrent-code-swarm-eval-01",
        )
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "CROSS_MODULE_INTERFACE_OR_CONSERVATION_DEFECT_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_CANONICAL_INTERFACE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "ALIGN_TO_UPSTREAM_PRICING_SCHEMA",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "ALIGN_SCHEMA_AND_CONSERVATION_INVARIANT",
        )

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "CROSS_MODULE_INTERFACE_OR_CONSERVATION_DEFECT_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_MERGE_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_MERGE_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_diamond_codebase_pullback_mediator_contract_synthesis_audit(self) -> None:
        """Verify Theorem 95: diamond-dependency codebase pullback-mediator contract synthesis."""
        mon = StreamingDiamondCodebasePullbackMonitor(
            scope_id="unit-diamond-codebase-pullback-scope",
        )
        obs = mon.record_three_phase_diamond_codebase_audit(
            "diamond-codebase-pullback-eval-01",
        )
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertFalse(obs["phase_1_in_pullback"])
        self.assertEqual(obs["phase_1_status"], "PULLBACK_INTERFACE_MISMATCH_NGD_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_CANONICAL_INTERFACE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "SYNTHESIZE_PULLBACK_MEDIATOR_TAX_CONTRACT",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "SYNTHESIZE_PULLBACK_MEDIATOR_FEE_CONTRACT",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-3"]["action"],
            "ENFORCE_PULLBACK_MEDIATOR_AND_DIAMOND_CONSERVATION",
        )

        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_interface_fiber_size"], 4)
        self.assertEqual(obs["phase_2_status"], "AMBIGUOUS_PULLBACK_INTERFACE_FIBER_LGGR")

        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_interface_fiber_size"], 1)
        self.assertEqual(obs["phase_3_status"], "DIAMOND_PULLBACK_CONTRACT_SYNTHESIZED_LGGG")
        self.assertEqual(
            obs["phase_3_universal_mediator"],
            {"w_diamond": ["b_net_v1_900", "c_net_v1_900"]},
        )

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "DIAMOND_PULLBACK_CONTRACT_SYNTHESIZED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_iterative_codebase_feature_evolution_catalyst_debt_and_rejuvenation_audit(self) -> None:
        """Verify Theorem 96: multi-round codebase feature-evolution catalyst technical-debt & rejuvenation."""
        mon = StreamingCodebaseCatalystEvolutionMonitor(
            scope_id="unit-codebase-catalyst-evolution-scope",
        )
        obs = mon.record_three_phase_codebase_catalyst_audit(
            "codebase-catalyst-eval-01",
        )
        self.assertEqual(obs["uniform_wear_ticket_ceiling"], 2)
        self.assertEqual(obs["phase_1_terminal_debt"], 6)
        self.assertEqual(obs["phase_1_max_debt"], 6)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "CATALYST_TECHNICAL_DEBT_CEILING_BREACH_NGD_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "REJUVENATE_CATALYST_PURGE_SHIMS",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "REJUVENATE_CATALYST_PURGE_SHIMS",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "REJUVENATE_CATALYST_PURGE_SHIMS",
        )

        self.assertEqual(obs["phase_2_terminal_debt"], 4)
        self.assertEqual(obs["phase_2_max_debt"], 6)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "LATE_CATALYST_CLEANUP_PREFIX_BREACH_LGGR")

        self.assertEqual(obs["phase_3_pre_rejuvenation_debt"], 4)
        self.assertEqual(obs["phase_3_terminal_debt"], 0)
        self.assertEqual(obs["phase_3_max_debt"], 4)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_CATALYST_REJUVENATION_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_CATALYST_REJUVENATION_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["current_catalyst_debt"], 0)
        self.assertEqual(receipt["max_catalyst_debt_seen"], 4)

    def test_stateful_codebase_transaction_dfa_reset_gluing_audit(self) -> None:
        """Verify Theorem 97: stateful transaction codebase DFA non-resetting concatenation vs reset gluing."""
        mon = StreamingStatefulCodebaseDFAMonitor(
            scope_id="unit-stateful-codebase-dfa-scope",
        )
        obs = mon.record_three_phase_stateful_codebase_dfa_audit(
            "stateful-codebase-dfa-eval-01",
        )
        self.assertEqual(obs["phase_1_non_reset_count"], 3)
        self.assertEqual(obs["phase_1_terminal_state"], "q3_err")
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "NON_RESET_DFA_CONCATENATION_MISMATCH_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "ENFORCE_DFA_RESET_TOKEN_RELEASE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "ENFORCE_DFA_RESET_TOKEN_RELEASE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "ENFORCE_DFA_RESET_TOKEN_RELEASE",
        )

        self.assertEqual(obs["phase_2_non_reset_count"], 1)
        self.assertEqual(obs["phase_2_terminal_state"], "q3_err")
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "UNRELEASED_PREFIX_TRAP_STATE_LGGR")

        self.assertEqual(obs["phase_3_non_reset_count"], 0)
        self.assertEqual(obs["phase_3_terminal_state"], "q0_idle")
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_DFA_RESET_GLUING_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_DFA_RESET_GLUING_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_async_codebase_replay_order_prefix_envelope_and_barrier_gluing_audit(self) -> None:
        """Verify Theorem 98: async codebase replay-order prefix drawdown vs causal-barrier gluing."""
        mon = StreamingCodebaseReplayOrderMonitor(
            prefix_budget=900,
            scope_id="unit-codebase-replay-order-scope",
        )
        obs = mon.record_three_phase_codebase_replay_order_audit(
            "codebase-replay-order-eval-01",
        )
        self.assertEqual(obs["prefix_budget_cents"], 900)
        self.assertEqual(obs["phase_1_arrival_max_prefix_cents"], 180)
        self.assertEqual(obs["phase_1_causal_max_prefix_cents"], 1080)
        self.assertEqual(obs["phase_1_worst_max_prefix_cents"], 1080)
        self.assertEqual(obs["phase_1_endpoint_sum_cents"], 180)
        self.assertEqual(obs["phase_1_missing_barriers"], 3)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "ENFORCE_CAUSAL_BARRIER_AND_PRENETTED_DELTA",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "ENFORCE_CAUSAL_BARRIER_AND_PRENETTED_DELTA",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "ENFORCE_CAUSAL_BARRIER_AND_PRENETTED_DELTA",
        )

        self.assertEqual(obs["phase_2_arrival_max_prefix_cents"], 900)
        self.assertEqual(obs["phase_2_causal_max_prefix_cents"], 900)
        self.assertEqual(obs["phase_2_worst_max_prefix_cents"], 1080)
        self.assertEqual(obs["phase_2_endpoint_sum_cents"], 180)
        self.assertEqual(obs["phase_2_missing_barriers"], 3)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR")

        self.assertEqual(obs["phase_3_arrival_max_prefix_cents"], 900)
        self.assertEqual(obs["phase_3_causal_max_prefix_cents"], 900)
        self.assertEqual(obs["phase_3_worst_max_prefix_cents"], 900)
        self.assertEqual(obs["phase_3_endpoint_sum_cents"], 180)
        self.assertEqual(obs["phase_3_missing_barriers"], 0)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_REPLAY_ORDER_BARRIER_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_REPLAY_ORDER_BARRIER_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_coalitional_codebase_synergistic_fault_masking_and_shapley_audit(self) -> None:
        """Verify Theorem 99: coalitional codebase leave-one-out masking vs exact Shapley attribution."""
        mon = StreamingCodebaseCoalitionalMonitor(
            scope_id="unit-codebase-coalitional-shapley-scope",
        )
        obs = mon.record_three_phase_codebase_coalitional_audit(
            "codebase-coalitional-eval-01",
        )
        self.assertEqual(
            obs["phase_1_leave_one_out_marginals"],
            {"pricing_coalition": 0, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(obs["phase_1_grand_value"], -1)
        self.assertEqual(
            obs["phase_1_two_times_shapley"],
            {"pricing_coalition": -1, "tax_coalition": 0, "settlement_coalition": -1},
        )
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "LEAVE_ONE_OUT_MASKED_COALITIONAL_DEFECT_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "REPAIR_SHAPLEY_ATTRIBUTED_MODULE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "HOLD_EXONERATED_DUMMY_MODULE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "REPAIR_SHAPLEY_ATTRIBUTED_MODULE",
        )

        self.assertEqual(
            obs["phase_2_leave_one_out_marginals"],
            {"pricing_coalition": -1, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(
            obs["phase_2_two_times_shapley"],
            {"pricing_coalition": -2, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "SINGLE_MODULE_RESIDUAL_COALITIONAL_DEFECT_LGGR")

        self.assertEqual(
            obs["phase_3_leave_one_out_marginals"],
            {"pricing_coalition": 0, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(
            obs["phase_3_two_times_shapley"],
            {"pricing_coalition": 0, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_COALITIONAL_SHAPLEY_COHERENT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_COALITIONAL_SHAPLEY_COHERENT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_mayer_vietoris_codebase_disconnected_overlap_and_coboundary_audit(self) -> None:
        """Verify Theorem 100: Mayer-Vietoris codebase disconnected overlap coboundary reconciliation."""
        mon = StreamingCodebaseMayerVietorisMonitor(
            scope_id="unit-codebase-mayer-vietoris-scope",
        )
        obs = mon.record_three_phase_codebase_mayer_vietoris_audit(
            "codebase-mv-eval-01",
        )
        self.assertEqual(obs["phase_1_fu_w1_cents"], 1110)
        self.assertEqual(obs["phase_1_fv_w1_cents"], 1050)
        self.assertEqual(obs["phase_1_coboundary_spread_cents"], 60)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "MAYER_VIETORIS_DISCONNECTED_OVERLAP_OBSTRUCTION_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_ANCHOR_POTENTIAL_ZERO",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "RECONCILE_SUBSWARM_U_COBOUNDARY",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "RECONCILE_SUBSWARM_V_COBOUNDARY",
        )

        self.assertEqual(obs["phase_2_fu_w1_cents"], 1110)
        self.assertEqual(obs["phase_2_fv_w1_cents"], 1080)
        self.assertEqual(obs["phase_2_coboundary_spread_cents"], 30)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "RESIDUAL_MAYER_VIETORIS_COBOUNDARY_SPREAD_LGGR")

        self.assertEqual(obs["phase_3_fu_w1_cents"], 1080)
        self.assertEqual(obs["phase_3_fv_w1_cents"], 1080)
        self.assertEqual(obs["phase_3_coboundary_spread_cents"], 0)
        self.assertTrue(obs["phase_3_union_globally_exact"])
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_MAYER_VIETORIS_RECONCILED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_MAYER_VIETORIS_RECONCILED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_windowed_drift_codebase_horizon_truncation_and_rebalancing_audit(self) -> None:
        """Verify Theorem 101: Windowed-drift codebase horizon truncation and periodic rebalancing."""
        mon = StreamingCodebaseWindowedDriftMonitor(
            scope_id="unit-codebase-windowed-drift-scope",
        )
        obs = mon.record_three_phase_codebase_windowed_drift_audit(
            "codebase-win-eval-01",
        )
        self.assertEqual(obs["phase_1_max_window_sum_cents"], 2)
        self.assertEqual(obs["phase_1_max_prefix_drift_cents"], 6)
        self.assertEqual(obs["phase_1_terminal_drift_cents"], 6)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "SLIDING_WINDOW_HORIZON_BREACH_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "ENFORCE_INTRA_WINDOW_ZERO_SUM_SWEEP",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "ENFORCE_INTRA_WINDOW_ZERO_SUM_SWEEP",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "ENFORCE_INTRA_WINDOW_ZERO_SUM_SWEEP",
        )

        self.assertEqual(obs["phase_2_max_window_sum_cents"], 2)
        self.assertEqual(obs["phase_2_max_prefix_drift_cents"], 4)
        self.assertEqual(obs["phase_2_terminal_drift_cents"], 2)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "LATE_TERMINAL_REBALANCING_PREFIX_BREACH_LGGR")

        self.assertEqual(obs["phase_3_max_window_sum_cents"], 1)
        self.assertEqual(obs["phase_3_max_prefix_drift_cents"], 1)
        self.assertEqual(obs["phase_3_terminal_drift_cents"], 0)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_WINDOWED_DRIFT_REBALANCED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_WINDOWED_DRIFT_REBALANCED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_optional_stopping_codebase_early_gain_skew_and_drawdown_cap_audit(self) -> None:
        """Verify Theorem 102: Martingale optional-stopping codebase early-gain halting vs. tail-drawdown cap."""
        mon = StreamingCodebaseOptionalStoppingMonitor(
            scope_id="unit-codebase-optional-stopping-scope",
        )
        obs = mon.record_three_phase_codebase_optional_stopping_audit(
            "codebase-stop-eval-01",
        )
        self.assertEqual(obs["phase_1_stopped_expectation_cents"], 0)
        self.assertEqual(obs["phase_1_tail_drawdown_cents"], 300)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_STEP1_MARTINGALE_ROOT",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "HOLD_UPPER_CONTINUATION_BRANCH",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "ENFORCE_LOSS_CAPPED_STEP1_HALT",
        )

        self.assertEqual(obs["phase_2_stopped_expectation_cents"], 0)
        self.assertEqual(obs["phase_2_tail_drawdown_cents"], 200)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "RESIDUAL_TAIL_DRAWDOWN_BREACH_LGGR")

        self.assertEqual(obs["phase_3_stopped_expectation_cents"], 0)
        self.assertEqual(obs["phase_3_tail_drawdown_cents"], 100)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_OPTIONAL_STOPPING_DRAWDOWN_CAPPED_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_OPTIONAL_STOPPING_DRAWDOWN_CAPPED_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_cptp_codebase_state_blindspot_and_operator_completion_audit(self) -> None:
        """Verify Theorem 103: State-dependent CPTP channel codebase trace blindspot vs. operator completeness."""
        mon = StreamingCodebaseCPTPChannelMonitor(
            scope_id="unit-codebase-cptp-channel-scope",
        )
        obs = mon.record_three_phase_codebase_cptp_audit(
            "codebase-cptp-eval-01",
        )
        self.assertEqual(obs["phase_1_residual_l1_norm"], 2)
        self.assertEqual(obs["phase_1_trace_discrepancy_rho0"], 0)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "CPTP_STATE_BLINDSPOT_NON_TP_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_GROUND_KRAUS_SECTOR",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "COMPLETE_TAX_KRAUS_SECTOR",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "COMPLETE_SETTLEMENT_KRAUS_SECTOR",
        )

        self.assertEqual(obs["phase_2_residual_l1_norm"], 1)
        self.assertEqual(obs["phase_2_trace_discrepancy_rho2"], -1)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "EXCITED_STATE_TRACE_LEAKAGE_LGGR")

        self.assertEqual(obs["phase_3_residual_l1_norm"], 0)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_CPTP_OPERATOR_COMPLETE_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_CPTP_OPERATOR_COMPLETE_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_regge_codebase_hinge_deficit_and_gauss_bonnet_holonomy_audit(self) -> None:
        """Verify Theorem 104: Simplicial mesh Regge hinge-deficit curvature & boundary Gauss-Bonnet holonomy."""
        mon = StreamingCodebaseReggeHolonomyMonitor(
            scope_id="unit-codebase-regge-holonomy-scope",
        )
        obs = mon.record_three_phase_codebase_regge_audit(
            "codebase-regge-eval-01",
        )
        self.assertEqual(obs["phase_1_apex_deficit_units"], 12)
        self.assertEqual(obs["phase_1_boundary_turn_sum_units"], 24)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_FLAT_PRICING_SECTOR",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "FLATTEN_TAX_SECTOR_HINGE",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "FLATTEN_SETTLEMENT_SECTOR_HINGE",
        )

        self.assertEqual(obs["phase_2_apex_deficit_units"], 6)
        self.assertEqual(obs["phase_2_boundary_turn_sum_units"], 30)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "RESIDUAL_HINGE_DEFICIT_CURVATURE_LGGR")

        self.assertEqual(obs["phase_3_apex_deficit_units"], 0)
        self.assertEqual(obs["phase_3_boundary_turn_sum_units"], 36)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_REGGE_HOLONOMY_FLAT_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_REGGE_HOLONOMY_FLAT_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)

    def test_kinduction_codebase_bounded_unrolling_and_invariant_strengthening_audit(self) -> None:
        """Verify Theorem 105: Bounded-depth k-induction horizon escape & non-negative carrier invariant strengthening."""
        mon = StreamingCodebaseKInductionMonitor(
            scope_id="unit-codebase-k-induction-scope",
        )
        obs = mon.record_three_phase_codebase_k_induction_audit(
            "codebase-k-induction-eval-01",
        )
        self.assertIsNone(obs["phase_1_tax_integral_root"])
        self.assertEqual(obs["phase_1_settle_integral_root"], -1)
        self.assertEqual(obs["phase_1_settle_depth4_overflow"], 8)
        self.assertEqual(obs["phase_1_local_green"], 1)
        self.assertEqual(obs["phase_1_global_green"], 0)
        self.assertEqual(obs["phase_1_defect"], -1)
        self.assertEqual(obs["phase_1_status"], "K_INDUCTION_BOUNDED_HORIZON_ESCAPE_NGD_LGGR")
        self.assertEqual(
            obs["phase_1_directives"]["worker-0"]["action"],
            "HOLD_INDUCTIVE_PRICING_ANCHOR",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-1"]["action"],
            "STRENGTHEN_TAX_TOWER_INVARIANT",
        )
        self.assertEqual(
            obs["phase_1_directives"]["worker-2"]["action"],
            "STRENGTHEN_SETTLEMENT_CARRIER_INVARIANT",
        )

        self.assertEqual(obs["phase_2_tax_integral_root"], 2)
        self.assertEqual(obs["phase_2_settle_integral_root"], -1)
        self.assertEqual(obs["phase_2_settle_depth4_overflow"], 8)
        self.assertEqual(obs["phase_2_local_green"], 1)
        self.assertEqual(obs["phase_2_global_green"], 0)
        self.assertEqual(obs["phase_2_defect"], -1)
        self.assertEqual(obs["phase_2_status"], "K_INDUCTION_OUT_OF_CARRIER_STEP_UNSOUND_LGGR")

        self.assertEqual(obs["phase_3_tax_integral_root"], 2)
        self.assertEqual(obs["phase_3_settle_integral_root"], 2)
        self.assertEqual(obs["phase_3_settle_depth4_overflow"], 0)
        self.assertEqual(obs["phase_3_local_green"], 1)
        self.assertEqual(obs["phase_3_global_green"], 1)
        self.assertEqual(obs["phase_3_defect"], 0)
        self.assertEqual(obs["phase_3_status"], "CODEBASE_K_INDUCTION_SOUND_LGGG")

        receipt = mon.current_receipt()
        self.assertEqual(receipt["status"], "CODEBASE_K_INDUCTION_SOUND_LGGG")
        self.assertEqual(receipt["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(receipt["lggr_obstruction_count"], 2)
        self.assertEqual(receipt["lggg_coherent_count"], 1)


if __name__ == "__main__":
    unittest.main()
