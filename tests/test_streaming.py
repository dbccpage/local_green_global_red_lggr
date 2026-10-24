"""Comprehensive unit tests for streaming runtime monitors in lggr.streaming.

Zero external dependencies: Python standard library unittest only.
AuthorityEffect: None.
"""
from __future__ import annotations

from fractions import Fraction
import unittest

from lggr.common import ValidationError
from lggr.streaming import (
    StreamingAuditMonitor,
    StreamingCochainMonitor,
    StreamingFiberMonitor,
)
from lggr.witnesses import BudgetPolicy, StateRef, StepWitness, make_witness


class TestStreamingFiberMonitor(unittest.TestCase):
    def test_initial_state(self):
        monitor = StreamingFiberMonitor(scope_id="test-scope")
        self.assertFalse(monitor.is_obstructed)
        self.assertEqual(monitor.status, "COMPOSABLE_LGGG")
        self.assertEqual(len(monitor.history), 0)

    def test_distinct_reports_pass(self):
        monitor = StreamingFiberMonitor(scope_id="test-scope")
        r1 = monitor.observe("s1", {"mode": "alpha"}, {"approved": True})
        r2 = monitor.observe("s2", {"mode": "beta"}, {"approved": False})

        self.assertEqual(r1["status"], "OK")
        self.assertEqual(r1["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(r2["status"], "OK")
        self.assertFalse(monitor.is_obstructed)

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["status"], "DECODER_VERIFIED")
        self.assertEqual(len(receipt["decoder"]), 2)

    def test_identical_report_and_query_pass(self):
        monitor = StreamingFiberMonitor(scope_id="test-scope")
        r1 = monitor.observe("s1", "report_A", 42)
        r2 = monitor.observe("s2", "report_A", 42)

        self.assertEqual(r1["status"], "OK")
        self.assertEqual(r2["status"], "OK")
        self.assertFalse(monitor.is_obstructed)

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["status"], "DECODER_VERIFIED")
        self.assertEqual(len(receipt["decoder"]), 1)

    def test_fiber_collision_detection(self):
        monitor = StreamingFiberMonitor(scope_id="collision-test")
        r1 = monitor.observe("s1", "shared_report", {"safe": True})
        self.assertEqual(r1["status"], "OK")
        self.assertFalse(monitor.is_obstructed)

        # Same report, differing query -> collision
        r2 = monitor.observe("s2", "shared_report", {"safe": False})
        self.assertEqual(r2["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(r2["contract_status"], "OBSTRUCTED_LGGR")
        self.assertTrue(monitor.is_obstructed)
        self.assertIsNotNone(r2["colliding_pair"])
        self.assertEqual(r2["colliding_pair"]["left"]["state_id"], "s1")
        self.assertEqual(r2["colliding_pair"]["right"]["state_id"], "s2")

        # Subsequent observation remains obstructed
        r3 = monitor.observe("s3", "other_report", {"safe": True})
        self.assertEqual(r3["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(r3["contract_status"], "OBSTRUCTED_LGGR")

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["schema"], "lggr.online_collision.v1")
        self.assertEqual(receipt["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")

    def test_duplicate_state_id_idempotency_and_conflict(self):
        monitor = StreamingFiberMonitor()
        monitor.observe("s1", "rep1", "q1")
        # Idempotent re-observation of identical state
        dup = monitor.observe("s1", "rep1", "q1")
        self.assertEqual(dup["status"], "OK")
        self.assertEqual(len(monitor.history), 1)

        # Conflicting state observation raises ValidationError
        with self.assertRaises(ValidationError):
            monitor.observe("s1", "rep1", "different_q")

    def test_type_sensitivity_preservation(self):
        monitor = StreamingFiberMonitor()
        # True vs 1 must not be aliased
        monitor.observe("s1", "rep", True)
        res = monitor.observe("s2", "rep", 1)
        self.assertEqual(res["status"], "REPORT_INSUFFICIENT")
        self.assertTrue(monitor.is_obstructed)


class TestStreamingAuditMonitor(unittest.TestCase):
    def setUp(self):
        self.policy = BudgetPolicy(allowed_states=(0, 1, 2), max_step=1, max_total=1, query_scope="endpoint")
        self.s0 = StateRef("s0", 0)
        self.s1 = StateRef("s1", 1)
        self.s2 = StateRef("s2", 2)

    def test_good_history_passes(self):
        monitor = StreamingAuditMonitor(self.policy, self.s0)
        w1 = make_witness(self.policy, self.s0, self.s1, witness_id="w001")
        step_res = monitor.step(w1, global_evaluator_sample=1, step_cost=10)

        self.assertEqual(step_res["status"], "OK")
        self.assertEqual(step_res["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(step_res["defect"], 0)
        self.assertEqual(step_res["classification"], "ZDR")
        self.assertEqual(step_res["running_cost"], 10)
        self.assertEqual(step_res["cumulative_delta"], 1)

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["status"], "COMPOSITION_VERIFIED")
        self.assertTrue(receipt["composition_certified"])

    def test_every_prefix_vs_endpoint_scope(self):
        # 0 -> 2 -> 1: intermediate delta is +2 (exceeds max_total=1)
        policy_prefix = BudgetPolicy(allowed_states=(0, 1, 2), max_step=2, max_total=1, query_scope="every_prefix")
        policy_endpoint = BudgetPolicy(allowed_states=(0, 1, 2), max_step=2, max_total=1, query_scope="endpoint")

        w1_p = make_witness(policy_prefix, self.s0, self.s2, witness_id="w1")
        w2_p = make_witness(policy_prefix, self.s2, self.s1, witness_id="w2")

        monitor_prefix = StreamingAuditMonitor(policy_prefix, self.s0)
        r1_p = monitor_prefix.step(w1_p)
        self.assertEqual(r1_p["status"], "ALERT")
        self.assertIn("PREFIX_BUDGET_EXCEEDED", r1_p["alert_reasons"])
        self.assertEqual(monitor_prefix.status, "OBSTRUCTED_LGGR")
        monitor_prefix.step(w2_p)
        prefix_receipt = monitor_prefix.get_receipt()
        self.assertEqual(prefix_receipt["status"], "OBSTRUCTION_DETECTED")
        self.assertFalse(prefix_receipt["composition_certified"])
        self.assertEqual(prefix_receipt["alerts_count"], 1)

        # Under endpoint policy, intermediate spike does not trigger early alert
        w1_e = make_witness(policy_endpoint, self.s0, self.s2, witness_id="w1")
        w2_e = make_witness(policy_endpoint, self.s2, self.s1, witness_id="w2")

        monitor_endpoint = StreamingAuditMonitor(policy_endpoint, self.s0)
        r1_e = monitor_endpoint.step(w1_e)
        self.assertEqual(r1_e["status"], "OK")
        self.assertFalse(r1_e["g4_prefix_ok"])
        r2_e = monitor_endpoint.step(w2_e)
        self.assertEqual(r2_e["status"], "OK")
        endpoint_receipt = monitor_endpoint.get_receipt()
        self.assertEqual(endpoint_receipt["status"], "COMPOSITION_VERIFIED")
        self.assertTrue(endpoint_receipt["composition_certified"])
        self.assertEqual(endpoint_receipt["alerts_count"], 0)

    def test_endpoint_receipt_rejects_unrecovered_excursion(self):
        policy = BudgetPolicy(allowed_states=(-2, 0, 2), max_step=2, max_total=1, query_scope="endpoint")
        for value in (-2, 2):
            with self.subTest(value=value):
                monitor = StreamingAuditMonitor(policy, self.s0)
                witness = make_witness(policy, self.s0, StateRef("end", value), witness_id="w1")
                step = monitor.step(witness)
                self.assertEqual(step["status"], "OK")
                self.assertFalse(step["g4_prefix_ok"])
                receipt = monitor.get_receipt()
                self.assertEqual(receipt["status"], "OBSTRUCTION_DETECTED")
                self.assertFalse(receipt["composition_certified"])
                self.assertEqual(receipt["alerts_count"], 0)
                self.assertIn("PROTECTED_QUERY_FALSE", {f["code"] for f in receipt["findings"]})

    def test_intermediate_endpoint_receipt_does_not_poison_live_recovery(self):
        policy = BudgetPolicy(allowed_states=(0, 1, 2), max_step=2, max_total=1, query_scope="endpoint")
        for negative_sample in (False, True):
            with self.subTest(negative_sample=negative_sample):
                monitor = StreamingAuditMonitor(policy, self.s0)
                monitor.step(make_witness(policy, self.s0, self.s2, witness_id="w1"),
                             global_evaluator_sample=0 if negative_sample else None)
                self.assertEqual(monitor.get_receipt()["contract_status"], "OBSTRUCTED_LGGR")
                result = monitor.step(make_witness(policy, self.s2, self.s1, witness_id="w2"))
                expected = "OBSTRUCTED_LGGR" if negative_sample else "COMPOSABLE_LGGG"
                self.assertEqual(result["contract_status"], expected)
                self.assertEqual(monitor.get_receipt()["contract_status"], expected)
                self.assertEqual(monitor.get_receipt(), monitor.get_receipt())

    def test_endpoint_recovery_retains_other_obstructions(self):
        policy = BudgetPolicy(allowed_states=(0, 1, 2), max_step=2, max_total=1, query_scope="endpoint")
        for fault in ("boundary", "global_sample"):
            with self.subTest(fault=fault):
                monitor = StreamingAuditMonitor(policy, self.s0)
                first = make_witness(policy, self.s0, self.s2, witness_id="w1")
                monitor.step(first, global_evaluator_sample=0 if fault == "global_sample" else None)
                source = StateRef("wrong_boundary", 2) if fault == "boundary" else self.s2
                monitor.step(make_witness(policy, source, self.s1, witness_id="w2"))
                receipt = monitor.get_receipt()
                self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
                self.assertFalse(receipt["composition_certified"])
                self.assertEqual(receipt["alerts_count"], 1)
                code = "BOUNDARY_MISMATCH" if fault == "boundary" else "NGD_DEFECT_DETECTED"
                self.assertIn(code, {f["code"] for f in receipt["findings"]})

    def test_g1_boundary_mismatch_alert(self):
        monitor = StreamingAuditMonitor(self.policy, self.s0)
        w1 = make_witness(self.policy, self.s0, self.s1, witness_id="w1")
        # Step 2 starts at s0 instead of expected s1
        w2 = make_witness(self.policy, self.s0, self.s1, witness_id="w2")

        monitor.step(w1)
        r2 = monitor.step(w2)
        self.assertEqual(r2["status"], "ALERT")
        self.assertFalse(r2["g1_glued"])
        self.assertTrue(any("BOUNDARY_MISMATCH" in reason for reason in r2["alert_reasons"]))

    def test_g3_evaluator_defect_classification(self):
        # Test NGD: local checks green, but global check red -> Delta_E = -1
        monitor = StreamingAuditMonitor(self.policy, self.s0)
        w1 = make_witness(self.policy, self.s0, self.s1, witness_id="w1")
        res = monitor.step(w1, global_evaluator_sample=0)  # Eg = 0, P_1 = 1

        self.assertEqual(res["status"], "ALERT")
        self.assertEqual(res["defect"], -1)
        self.assertEqual(res["classification"], "NGD")
        self.assertIn("NGD_DEFECT_DETECTED", res["alert_reasons"])

        # Test PGD: local checks red, global check green -> Delta_E = +1
        # Create a step witness with local_accepted=False
        bad_witness = StepWitness(
            witness_id="w_bad", source=self.s0, target=self.s1,
            policy_sha256=self.policy.sha256, evaluator_id=self.policy.evaluator_id,
            spec_id=self.policy.spec_id, representation_id=self.policy.representation_id,
            authority_id=self.policy.authority_id, observed_magnitude=1,
            local_accepted=False, smoke_passed=True
        )
        monitor2 = StreamingAuditMonitor(self.policy, self.s0)
        res_pgd = monitor2.step(bad_witness, global_evaluator_sample=1)
        self.assertEqual(res_pgd["defect"], 1)
        self.assertEqual(res_pgd["classification"], "PGD")

    def test_obligations_retention(self):
        monitor = StreamingAuditMonitor(self.policy, self.s0)
        w1 = make_witness(self.policy, self.s0, self.s1, witness_id="w1", obligations=("ob1", "ob2"))
        monitor.step(w1)
        receipt = monitor.get_receipt()
        self.assertEqual(receipt["unresolved_obligations"], ["ob1", "ob2"])


class TestStreamingCochainMonitor(unittest.TestCase):
    def test_open_tree(self):
        monitor = StreamingCochainMonitor()
        r1 = monitor.add_edge("A", "B", 1, 1)
        r2 = monitor.add_edge("B", "C", 2, 1)

        self.assertEqual(r1["status"], "OPEN_TREE")
        self.assertFalse(r1["cycle_detected"])
        self.assertIsNone(r1["closure_defect"])

        self.assertEqual(r2["status"], "OPEN_TREE")
        self.assertFalse(r2["cycle_detected"])

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["status"], "OPEN_TREE")
        self.assertEqual(receipt["cycles_detected"], 0)

    def test_exact_cycle_closure(self):
        # A -> B (1), B -> C (1), A -> C (2)
        # Consistent cycle: (A->B) + (B->C) - (A->C) = 1 + 1 - 2 = 0
        monitor = StreamingCochainMonitor()
        monitor.add_edge("A", "B", 1, 1)
        monitor.add_edge("B", "C", 1, 1)
        r3 = monitor.add_edge("A", "C", 2, 1)

        self.assertEqual(r3["status"], "CYCLE_CLOSED")
        self.assertTrue(r3["cycle_detected"])
        self.assertEqual(r3["closure_defect"], Fraction(0))
        self.assertEqual(r3["l1_repair_distance"], Fraction(0))
        self.assertEqual(r3["certificate_status"], "OPTIMALITY_VERIFIED")

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["status"], "EXACT_REPAIR")
        self.assertEqual(receipt["cycles_detected"], 1)
        self.assertEqual(receipt["nonrepairable_cycles"], 0)

    def test_inconsistent_triangle_l1_repair(self):
        # Classic triangle with closure failure:
        # A -> B (1, w=1), B -> C (1, w=1), A -> C (1, w=1)
        # Defect = 1, min_weight = 1 -> L1 repair distance = 1
        monitor = StreamingCochainMonitor()
        monitor.add_edge("0", "1", 1, 1)
        monitor.add_edge("1", "2", 1, 1)
        r3 = monitor.add_edge("0", "2", 1, 1)

        self.assertEqual(r3["status"], "CYCLE_CLOSED")
        self.assertTrue(r3["cycle_detected"])
        self.assertEqual(abs(r3["closure_defect"]), Fraction(1))
        self.assertEqual(r3["l1_repair_distance"], Fraction(1))
        self.assertEqual(r3["certificate_status"], "OPTIMALITY_VERIFIED")

        # Verify dual witness properties
        dual = r3["dual_witness"]
        self.assertIsNotNone(dual)

        receipt = monitor.get_receipt()
        self.assertEqual(receipt["status"], "OBSTRUCTED_CYCLE")
        self.assertEqual(receipt["nonrepairable_cycles"], 1)

    def test_fractional_weights_and_bottleneck(self):
        monitor = StreamingCochainMonitor()
        monitor.add_edge("0", "1", "1/2", weight="1/3")
        monitor.add_edge("1", "2", "1/2", weight="1/2")
        # Defect = 1/2 + 1/2 - 0 = 1. Min weight is 1/3. Distance = 1/3 * 1 = 1/3.
        r3 = monitor.add_edge("0", "2", 0, weight=1)

        self.assertEqual(r3["status"], "CYCLE_CLOSED")
        self.assertEqual(abs(r3["closure_defect"]), Fraction(1))
        self.assertEqual(r3["l1_repair_distance"], Fraction(1, 3))
        self.assertEqual(r3["certificate_status"], "OPTIMALITY_VERIFIED")

    def test_invalid_weights_rejected(self):
        monitor = StreamingCochainMonitor()
        with self.assertRaises(ValidationError):
            monitor.add_edge("A", "B", 1, weight=0)
        with self.assertRaises(ValidationError):
            monitor.add_edge("A", "B", 1, weight=-1)


if __name__ == "__main__":
    unittest.main()
