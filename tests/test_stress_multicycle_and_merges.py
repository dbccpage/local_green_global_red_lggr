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
    StreamingAuditMonitor,
    StreamingCochainMonitor,
    StreamingFiberMonitor,
    StreamingPositiveExtensionMonitor,
    StreamingTransportMonitor,
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


if __name__ == "__main__":
    unittest.main()
