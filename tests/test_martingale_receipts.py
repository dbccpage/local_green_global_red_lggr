"""Exact finite checks for independent martingale, conservation and loss verdicts."""
from fractions import Fraction
from itertools import product
import random
import unittest

from lggr.common import digest
from lggr.streaming import StreamingMartingaleOptionalStoppingMonitor


class TestMartingaleReceiptSemantics(unittest.TestCase):
    def test_non_martingale_within_budget_is_local_red_global_green(self):
        mon = StreamingMartingaleOptionalStoppingMonitor(1)
        rec = mon.record_stopped_tree("positive_drift", 0, 1, 1, 1, 1, 1, 1)
        self.assertEqual(rec["stopped_expectation"], "1")
        self.assertEqual(rec["tail_drawdown"], "0")
        self.assertEqual(rec["local_martingale_product"], 0)
        self.assertEqual(rec["global_drawdown_evaluator"], 1)
        self.assertEqual(rec["evaluator_defect"], 1)
        self.assertEqual(rec["joint_admission_evaluator"], 0)
        self.assertFalse(rec["optional_stopping_theorem_applicable"])
        self.assertFalse(rec["optional_stopping_conservation_verified"])
        self.assertEqual(rec["classification"], "NON_MARTINGALE_DRIFT_REJECTED")
        self.assertEqual(rec["contract_status"], "OBSTRUCTED_LGGR")
        receipt = mon.get_receipt()
        self.assertFalse(receipt["all_optional_stopping_theorems_applicable"])
        self.assertFalse(receipt["all_optional_stopping_conservations_verified"])

    def test_non_martingale_over_budget_rejects_both_evaluators(self):
        mon = StreamingMartingaleOptionalStoppingMonitor(1)
        rec = mon.record_stopped_tree("negative_drift", 0, -2, -2, -2, -2, -2, -2)
        self.assertEqual(rec["local_martingale_product"], 0)
        self.assertEqual(rec["global_drawdown_evaluator"], 0)
        self.assertEqual(rec["evaluator_defect"], 0)
        self.assertEqual(rec["joint_admission_evaluator"], 0)
        self.assertFalse(rec["optional_stopping_conservation_verified"])

    def test_applicable_theorem_conserves_even_when_budget_fails(self):
        for budget, expected_global in [(1, 0), (3, 1)]:
            with self.subTest(budget=budget):
                mon = StreamingMartingaleOptionalStoppingMonitor(budget)
                rec = mon.record_stopped_tree("fair", 0, 1, -1, 2, 0, 1, -3)
                self.assertEqual(rec["stopped_win_probability"], "3/4")
                self.assertTrue(rec["optional_stopping_theorem_applicable"])
                self.assertTrue(rec["optional_stopping_conservation_verified"])
                self.assertEqual(rec["local_martingale_product"], 1)
                self.assertEqual(rec["global_drawdown_evaluator"], expected_global)
                self.assertEqual(rec["joint_admission_evaluator"], expected_global)
                self.assertEqual(rec["evaluator_defect"], expected_global - 1)
                receipt = mon.get_receipt()
                self.assertTrue(receipt["all_optional_stopping_theorems_applicable"])
                self.assertTrue(receipt["all_optional_stopping_conservations_verified"])

    def test_accidental_conservation_does_not_establish_applicability(self):
        # The two branch drifts cancel in both expectations, but neither is zero.
        mon = StreamingMartingaleOptionalStoppingMonitor(1)
        rec = mon.record_stopped_tree(
            "cancelling_drift", 0, 0, 0, 1, 1, -1, -1,
            stop_on_step1_up=False, stop_on_step1_down=False,
        )
        self.assertEqual(rec["stopped_expectation"], "0")
        self.assertEqual(rec["horizon2_expectation"], "0")
        self.assertTrue(rec["optional_stopping_conservation_verified"])
        self.assertFalse(rec["optional_stopping_theorem_applicable"])
        self.assertEqual(rec["joint_admission_evaluator"], 0)
        self.assertEqual(rec["contract_status"], "OBSTRUCTED_LGGR")
        receipt = mon.get_receipt()
        self.assertTrue(receipt["all_optional_stopping_conservations_verified"])
        self.assertFalse(receipt["all_optional_stopping_theorems_applicable"])

    def test_conservation_requires_both_expectations(self):
        cases = [
            ((0, 0, 0, 1, 1, 1, 1), (True, True), "0", "1"),
            ((0, 1, -1, 0, 0, 0, 0), (True, False), "1/2", "0"),
        ]
        for values, stops, stopped, horizon in cases:
            with self.subTest(values=values):
                mon = StreamingMartingaleOptionalStoppingMonitor(2)
                rec = mon.record_stopped_tree(
                    "one_equality", *values,
                    stop_on_step1_up=stops[0], stop_on_step1_down=stops[1],
                )
                self.assertEqual(rec["stopped_expectation"], stopped)
                self.assertEqual(rec["horizon2_expectation"], horizon)
                self.assertFalse(rec["optional_stopping_conservation_verified"])

    def test_loss_metric_uses_initial_value_and_stopped_terminal_values(self):
        mon = StreamingMartingaleOptionalStoppingMonitor(15)
        rec = mon.record_stopped_tree(
            "peak_drop", 0, 10, -10, 30, -10, -10, -10,
            stop_on_step1_up=False, stop_on_step1_down=False,
        )
        self.assertTrue(rec["optional_stopping_theorem_applicable"])
        self.assertEqual(rec["tail_drawdown"], "10")
        self.assertEqual(rec["global_drawdown_evaluator"], 1)
        # The path (0, 10, -10) loses 20 from its peak; that is outside this metric.
        self.assertGreater(10 - (-10), 15)
        stopped = mon.record_stopped_tree(
            "unreached_loss", 0, 1, -1, 101, -99, 99, -101,
            stop_on_step1_up=True, stop_on_step1_down=True,
        )
        self.assertEqual(stopped["tail_drawdown"], "1")
        self.assertEqual(stopped["global_drawdown_evaluator"], 1)

    def test_mixed_receipt_retains_rejection_and_binds_new_fields(self):
        mon = StreamingMartingaleOptionalStoppingMonitor(3)
        mon.record_stopped_tree("fair", 0, 1, -1, 2, 0, 1, -3)
        mon.record_stopped_tree("invalid", 0, 1, 1, 1, 1, 1, 1)
        receipt = mon.get_receipt()
        self.assertEqual(receipt["non_martingale_tree_ids"], ["invalid"])
        self.assertEqual(receipt["tail_drawdown_ngd_tree_ids"], [])
        self.assertEqual(receipt["contract_status"], "OBSTRUCTED_LGGR")
        self.assertFalse(receipt["all_optional_stopping_conservations_verified"])
        self.assertFalse(receipt["all_optional_stopping_theorems_applicable"])
        checksum = receipt.pop("receipt_sha256")
        self.assertEqual(digest(receipt), checksum)
        receipt["trees"][1]["joint_admission_evaluator"] = 1
        self.assertNotEqual(digest(receipt), checksum)

    def test_2000_exact_cases_against_path_enumeration(self):
        # Independently enumerate complete paths and their increments. Stopping
        # repeats a first-step outcome on both descendant paths; no distribution
        # construction or monitor implementation helper is reused by this oracle.
        rng = random.Random(48)
        probabilities = [Fraction(1, 5), Fraction(1, 3), Fraction(1, 2),
                         Fraction(3, 5), Fraction(2, 3), Fraction(4, 5)]
        for case in range(500):
            p, u, d = [rng.choice(probabilities) for _ in range(3)]
            root = Fraction(rng.randint(-9, 9), rng.randint(1, 7))
            first = [Fraction(rng.randint(-9, 9), rng.randint(1, 7))]
            first.append((root - p * first[0]) / (1 - p))
            leaves = []
            for branch_value, conditional in zip(first, (u, d)):
                left = Fraction(rng.randint(-9, 9), rng.randint(1, 7))
                leaves.extend([left, (branch_value - conditional * left) / (1 - conditional)])
            # Include root drift, conditional drift and cancelling branch drifts.
            if case % 4 == 1:
                root += Fraction(1, 7)
            elif case % 4 == 2:
                leaves[0] += Fraction(1, 11)
            elif case % 4 == 3:
                leaves[0] += 1
                leaves[1] += 1
                leaves[2] -= p / (1 - p)
                leaves[3] -= p / (1 - p)
            budget = Fraction(rng.randint(0, 35), rng.randint(1, 5))
            paths = []
            for branch, child in product(range(2), repeat=2):
                weight = (p if branch == 0 else 1 - p)
                conditional = (u, d)[branch]
                weight *= conditional if child == 0 else 1 - conditional
                paths.append((branch, weight, first[branch], leaves[2 * branch + child]))
            root_drift = sum(w * (middle - root) for _, w, middle, _ in paths)
            branch_drifts = [sum(w * (end - middle) for b, w, middle, end in paths if b == branch)
                             for branch in range(2)]
            local = int(root_drift == 0 and all(delta == 0 for delta in branch_drifts))
            horizon = sum(w * end for _, w, _, end in paths)
            for stops in product((False, True), repeat=2):
                with self.subTest(case=case, stops=stops):
                    terminal = [(w, middle if stops[b] else end) for b, w, middle, end in paths]
                    expected = sum(w * value for w, value in terminal)
                    win = sum((w for w, value in terminal if value > root), Fraction())
                    loss = max(Fraction(), root - min(value for _, value in terminal))
                    global_verdict = int(loss <= budget)
                    mon = StreamingMartingaleOptionalStoppingMonitor(budget)
                    rec = mon.record_stopped_tree(
                        str(case), root, *first, *leaves, p_1=p, p_u=u, p_d=d,
                        stop_on_step1_up=stops[0], stop_on_step1_down=stops[1],
                    )
                    self.assertEqual(Fraction(rec["stopped_expectation"]), expected)
                    self.assertEqual(Fraction(rec["horizon2_expectation"]), horizon)
                    self.assertEqual(Fraction(rec["stopped_win_probability"]), win)
                    self.assertEqual(Fraction(rec["tail_drawdown"]), loss)
                    self.assertEqual(rec["local_martingale_product"], local)
                    self.assertEqual(rec["global_drawdown_evaluator"], global_verdict)
                    self.assertEqual(rec["joint_admission_evaluator"], local * global_verdict)
                    self.assertEqual(rec["evaluator_defect"], global_verdict - local)
                    self.assertEqual(rec["optional_stopping_theorem_applicable"], bool(local))
                    self.assertEqual(rec["optional_stopping_conservation_verified"],
                                     expected == root and horizon == root)
                    self.assertEqual(rec["contract_status"],
                                     "COMPOSABLE_LGGG" if local * global_verdict else "OBSTRUCTED_LGGR")


if __name__ == "__main__":
    unittest.main()
