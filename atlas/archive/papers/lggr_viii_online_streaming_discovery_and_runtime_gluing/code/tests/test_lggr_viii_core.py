"""
test_lggr_viii_core.py — Unit test suite for LGGR Volume VIII core module.

AuthorityEffect: None.

Verifies mathematical claims C-01 through C-14:
- Claims C-01 to C-12: Algorithmic counterparts of Lean 4 theorems.
- Claim C-13: OpenRouter empirical defect rate benchmark receipt verification.
- Claim C-14: Tests 1–4 live online discovery deterministic replay verification.
"""

from __future__ import annotations

from fractions import Fraction
import json
import pathlib
import sys
import unittest

CODE_DIR = pathlib.Path(__file__).resolve().parents[1]
PKG_DIR = CODE_DIR.parent
RECEIPTS_DIR = PKG_DIR / "receipts"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import lggr_viii_core as viii  # noqa: E402


class TestLggrVIIICore(unittest.TestCase):
    """Test suite covering Volume VIII core algorithms and claim ledger bindings."""

    def test_to_fraction_type_validation(self) -> None:
        """Verify exact rational converter rejects floats/bools and handles fractions."""
        self.assertEqual(viii.to_fraction(5), Fraction(5, 1))
        self.assertEqual(viii.to_fraction("4/3"), Fraction(4, 3))
        self.assertEqual(viii.to_fraction(Fraction(2, 7)), Fraction(2, 7))
        with self.assertRaises(TypeError):
            viii.to_fraction(0.5)  # float forbidden
        with self.assertRaises(TypeError):
            viii.to_fraction(True)  # bool forbidden

    def test_online_fiber_collision_detector(self) -> None:
        """Claim C-01: Collision detection and monotonicity under trace extension."""
        monitor = viii.StreamingFiberMonitor(scope_id="test_scope_c01")
        # Step 0: state_0 with report 'A' and query True
        res0 = monitor.observe(state_id="s0", report={"tag": "A"}, query={"ok": True})
        self.assertEqual(res0["status"], "OK")
        self.assertEqual(monitor.status, "COMPOSABLE_LGGG")
        self.assertIsNone(monitor.collision)

        # Step 1: state_1 with distinct report 'B'
        res1 = monitor.observe(state_id="s1", report={"tag": "B"}, query={"ok": True})
        self.assertEqual(res1["status"], "OK")
        self.assertEqual(monitor.status, "COMPOSABLE_LGGG")

        # Step 2: state_2 shares report 'A' but query is False -> Collision!
        res2 = monitor.observe(state_id="s2", report={"tag": "A"}, query={"ok": False})
        self.assertEqual(res2["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(monitor.status, "OBSTRUCTED_LGGR")
        self.assertIsNotNone(monitor.collision)
        self.assertEqual(monitor.collision["left"]["state_id"], "s0")
        self.assertEqual(monitor.collision["right"]["state_id"], "s2")

        # Trace extension: subsequent steps cannot remove the collision (monotonicity)
        res3 = monitor.observe(state_id="s3", report={"tag": "C"}, query={"ok": True})
        self.assertEqual(res3["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(monitor.status, "OBSTRUCTED_LGGR")
        self.assertIsNotNone(monitor.collision)

    def test_postprocessing_preserves_streaming_collision(self) -> None:
        """Claim C-02: Deterministic postprocessing preserves streaming collisions."""
        monitor = viii.StreamingFiberMonitor()
        monitor.observe(state_id="x", report={"key": "id", "meta": 1}, query=1)
        monitor.observe(state_id="y", report={"key": "id", "meta": 1}, query=0)
        self.assertEqual(monitor.status, "OBSTRUCTED_LGGR")

        # Postprocessing: strip metadata, keep only key
        postprocessor = lambda rep: {"key": rep["key"]}
        self.assertTrue(monitor.verify_postprocessing_invariance(postprocessor))

    def test_streaming_verdict_ceiling(self) -> None:
        """Claim C-03: Report-only monitor verdict ceiling on colliding fibers."""
        monitor = viii.StreamingFiberMonitor()
        monitor.observe(state_id="x", report="rep_alpha", query=1)
        monitor.observe(state_id="y", report="rep_alpha", query=0)

        # Evaluator predicting constant 1: disagrees with state y
        eval_one = lambda rep: 1
        res_one = monitor.evaluate_verdict_ceiling(eval_one)
        self.assertTrue(res_one["disagreement_found"])
        self.assertTrue(res_one["right_disagrees"])

        # Evaluator predicting constant 0: disagrees with state x
        eval_zero = lambda rep: 0
        res_zero = monitor.evaluate_verdict_ceiling(eval_zero)
        self.assertTrue(res_zero["disagreement_found"])
        self.assertTrue(res_zero["left_disagrees"])

    def test_streaming_defect_tracking(self) -> None:
        """Claim C-04: Streaming evaluator defect trichotomy Delta_E in {-1, 0, 1}."""
        evaluator = viii.StreamingOnlineEvaluator()
        # Case 1: local pass, global pass -> ZDR (0)
        res1 = evaluator.evaluate_step(stage_pass=True, global_pass=True)
        self.assertEqual(res1["defect"], 0)
        self.assertEqual(res1["classification"], "ZDR")

        # Case 2: local pass, global fail -> NGD (-1)
        evaluator2 = viii.StreamingOnlineEvaluator()
        res2 = evaluator2.evaluate_step(stage_pass=True, global_pass=False)
        self.assertEqual(res2["defect"], -1)
        self.assertEqual(res2["classification"], "NGD")

        # Case 3: local fail, global pass -> PGD (+1)
        evaluator3 = viii.StreamingOnlineEvaluator()
        res3 = evaluator3.evaluate_step(stage_pass=False, global_pass=True)
        self.assertEqual(res3["defect"], 1)
        self.assertEqual(res3["classification"], "PGD")

    def test_streaming_chain_telescoping(self) -> None:
        """Claim C-05: Arbitrary-length signed step drift telescoping."""
        monitor = viii.StreamingAuditMonitor(max_total=10)
        monitor.initialize(start_state=5)

        deltas = [3, -2, 4, -1, 7, -3]
        for d in deltas:
            monitor.step(d)
            self.assertTrue(monitor.verify_telescoping())

        # Final state check: 5 + sum(deltas) = 5 + 8 = 13
        self.assertEqual(monitor.current_state, 13)
        self.assertEqual(monitor.current_state - monitor.start_state, sum(deltas))

    def test_online_prefix_vs_endpoint(self) -> None:
        """Claim C-06: Strict separation of online every-prefix vs endpoint admissibility."""
        # Trace [0, 1, 2, 1] with budget B = 1
        monitor = viii.StreamingAuditMonitor(max_total=1, query_scope="every_prefix")
        monitor.initialize(0)

        # Step 1: delta = 1 -> state = 1 <= 1 (OK)
        s1 = monitor.step(1)
        self.assertEqual(s1["status"], "OK")

        # Step 2: delta = 1 -> state = 2 > 1 (ALERT, prefix exceeded)
        s2 = monitor.step(1)
        self.assertEqual(s2["status"], "ALERT")
        self.assertEqual(monitor.alert_step_index, 1)

        # Step 3: delta = -1 -> state = 1 <= 1 (endpoint passes)
        s3 = monitor.step(-1)

        # Endpoint would pass, but every_prefix fails
        self.assertTrue(monitor.check_endpoint_bound())
        self.assertFalse(monitor.check_every_prefix_bound())

    def test_early_stopping_soundness(self) -> None:
        """Claim C-07: Monotonicity of prefix budget violation and sound early stopping."""
        monitor = viii.StreamingAuditMonitor(max_total=2, query_scope="every_prefix")
        monitor.initialize(0)
        monitor.step(3)  # Exceeds max_total 2 at step 0
        self.assertEqual(monitor.status, "OBSTRUCTED_LGGR")

        # Continue with any transitions: prefix admissibility cannot be restored
        for d in (-1, -1, -1, 0, 1):
            monitor.step(d)
            self.assertFalse(monitor.check_every_prefix_bound())
            self.assertEqual(monitor.status, "OBSTRUCTED_LGGR")

    def test_streaming_unsigned_report_collision(self) -> None:
        """Claim C-08: Streaming unsigned step-magnitude report collision."""
        # Safe history [0, 1, 0] vs excursion history [0, 1, 2]
        # Step magnitudes: |1 - 0| = 1, |0 - 1| = 1 -> report [1, 1]
        # Step magnitudes: |1 - 0| = 1, |2 - 1| = 1 -> report [1, 1]
        hist_good = [0, 1, 0]
        hist_bad = [0, 1, 2]

        mags_good = [abs(hist_good[i] - hist_good[i-1]) for i in range(1, len(hist_good))]
        mags_bad = [abs(hist_bad[i] - hist_bad[i-1]) for i in range(1, len(hist_bad))]
        self.assertEqual(mags_good, [1, 1])
        self.assertEqual(mags_bad, [1, 1])

        # Endpoint query: |endpoint - start| <= 1
        q_good = abs(hist_good[-1] - hist_good[0]) <= 1  # True (0 <= 1)
        q_bad = abs(hist_bad[-1] - hist_bad[0]) <= 1   # False (2 > 1)
        self.assertTrue(q_good)
        self.assertFalse(q_bad)

        # Fiber monitor registers collision
        fiber_mon = viii.StreamingFiberMonitor()
        fiber_mon.observe(state_id="hist_good", report=mags_good, query=q_good)
        res_col = fiber_mon.observe(state_id="hist_bad", report=mags_bad, query=q_bad)
        self.assertEqual(res_col["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(fiber_mon.status, "OBSTRUCTED_LGGR")

    def test_open_chain_exactness(self) -> None:
        """Claim C-09: Acyclic tree handoffs have exact potential and zero L1 repair cost."""
        cochain_mon = viii.StreamingCochainMonitor()
        # Add edge 1: A -> B with value 1/2
        r1 = cochain_mon.add_edge("Agent_A", "Agent_B", "1/2")
        self.assertFalse(r1["cycle_closed"])

        # Add edge 2: B -> C with value 1/3
        r2 = cochain_mon.add_edge("Agent_B", "Agent_C", "1/3")
        self.assertFalse(r2["cycle_closed"])
        self.assertEqual(r2["circulation"], Fraction(0))
        self.assertEqual(r2["repair_distance"], Fraction(0))
        self.assertEqual(r2["potential"]["Agent_A"], Fraction(0))
        self.assertEqual(r2["potential"]["Agent_B"], Fraction(1, 2))
        self.assertEqual(r2["potential"]["Agent_C"], Fraction(5, 6))

    def test_incremental_cycle_closure_obstruction(self) -> None:
        """Claim C-10: Incremental cycle closure obstruction and L1 dual witness."""
        cochain_mon = viii.StreamingCochainMonitor()
        cochain_mon.add_edge("Agent_A", "Agent_B", "1/2")
        cochain_mon.add_edge("Agent_B", "Agent_C", "1/3")
        # Add edge 3: C -> A with value 1/2, closing cycle A->B->C->A
        r3 = cochain_mon.add_edge("Agent_C", "Agent_A", "1/2")
        self.assertTrue(r3["cycle_closed"])
        self.assertEqual(r3["circulation"], Fraction(4, 3))
        self.assertEqual(r3["repair_distance"], Fraction(4, 3))
        self.assertIsNotNone(r3["dual_witness"])

    def test_boundary_sufficient_gluing(self) -> None:
        """Claim C-11: Boundary-sufficient gluing certifies composable LGGG (Delta_E = 0)."""
        res = viii.StreamingOnlineEvaluator.verify_gluing_certification(
            stage_passes=[True, True],
            global_pass=True,
            boundary_sufficient=True,
        )
        self.assertTrue(res["composable_lggg"])
        self.assertEqual(res["defect"], 0)

    def test_boundary_insufficiency_forces_defect(self) -> None:
        """Claim C-12: Boundary insufficiency forces defect on colliding fiber."""
        # On colliding fiber: both pass locally, but global oracle diverges
        has_defect = viii.StreamingOnlineEvaluator.verify_forced_defect(
            left_local_pass=True,
            right_local_pass=True,
            left_global_pass=True,
            right_global_pass=False,
        )
        self.assertTrue(has_defect)

    def test_empirical_ngd_pgd_rates(self) -> None:
        """Claim C-13: Empirical OpenRouter benchmark receipt verification."""
        receipt_file = RECEIPTS_DIR / "empirical_ngd_benchmark.json"
        self.assertTrue(receipt_file.exists(), f"Missing receipt: {receipt_file}")

        with open(receipt_file, "r", encoding="utf-8") as f:
            receipt = json.load(f)

        verif = viii.BenchmarkReplayVerifier.verify_empirical_benchmark_receipt(receipt)
        self.assertEqual(verif["N"], 8)
        self.assertEqual(verif["LPR"], Fraction(1))
        self.assertEqual(verif["GPR"], Fraction(1))
        self.assertEqual(verif["NGD_rate"], Fraction(0))
        self.assertEqual(verif["ZDR_rate"], Fraction(1))
        self.assertEqual(verif["PGD_rate"], Fraction(0))
        self.assertTrue(verif["partition_valid"])
        self.assertTrue(verif["matches_metrics"])

    def test_online_discovery_replay_tests_1_to_4(self) -> None:
        """Claim C-14: Deterministic replay verification across Tests 1–4."""
        # Test 1 Replay
        t1_file = RECEIPTS_DIR / "test1_fiber_collision.json"
        self.assertTrue(t1_file.exists())
        with open(t1_file, "r", encoding="utf-8") as f:
            t1_receipt = json.load(f)
        v1 = viii.BenchmarkReplayVerifier.verify_test1_replay(t1_receipt)
        self.assertTrue(v1["matches_receipt"])
        self.assertEqual(v1["collision_step_index"], 1)
        self.assertEqual(v1["final_status"], "OBSTRUCTED_LGGR")

        # Test 2 Replay
        t2_file = RECEIPTS_DIR / "test2_prefix_breach.json"
        self.assertTrue(t2_file.exists())
        with open(t2_file, "r", encoding="utf-8") as f:
            t2_receipt = json.load(f)
        v2 = viii.BenchmarkReplayVerifier.verify_test2_replay(t2_receipt)
        self.assertTrue(v2["matches_receipt"])
        self.assertEqual(v2["alert_step_index"], 1)
        self.assertTrue(v2["endpoint_would_pass"])
        self.assertEqual(v2["final_status"], "OBSTRUCTED_LGGR")

        # Test 3 Replay
        t3_file = RECEIPTS_DIR / "test3_cochain_cycle.json"
        self.assertTrue(t3_file.exists())
        with open(t3_file, "r", encoding="utf-8") as f:
            t3_receipt = json.load(f)
        v3 = viii.BenchmarkReplayVerifier.verify_test3_replay(t3_receipt)
        self.assertTrue(v3["matches_receipt"])
        self.assertEqual(v3["cycle_closing_edge_index"], 2)
        self.assertEqual(v3["closure_defect"], Fraction(4, 3))
        self.assertEqual(v3["l1_repair_distance"], Fraction(4, 3))

        # Test 4 Replay
        t4_file = RECEIPTS_DIR / "test4_composable_lggg.json"
        self.assertTrue(t4_file.exists())
        with open(t4_file, "r", encoding="utf-8") as f:
            t4_receipt = json.load(f)
        v4 = viii.BenchmarkReplayVerifier.verify_test4_replay(t4_receipt)
        self.assertTrue(v4["matches_receipt"])
        self.assertFalse(v4["collision_detected"])
        self.assertEqual(v4["final_status"], "COMPOSABLE_LGGG")


if __name__ == "__main__":
    unittest.main()
