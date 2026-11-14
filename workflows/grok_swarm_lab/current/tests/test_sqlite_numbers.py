"""Exact money boundaries for the generic integer SQLite operation schema."""
from copy import deepcopy
import sqlite3
import unittest

from lggr_swarm_lab.tools import execute_branch, integrate


class TestSQLiteNumbers(unittest.TestCase):
    def setUp(self):
        self.source = {
            "customers": [{"customer_id": "c", "region": "north"}],
            "orders": [{"order_id": "o", "customer_id": "c", "amount": 13}],
            "refunds": [{"refund_id": "r", "order_id": "o", "amount": 3}],
        }
        self.plan = {"orders": {"scale_to_cents": 1, "join_mode": "first", "omit_last": False},
                     "refunds": {"scale_to_cents": 1, "sign": 1, "omit_last": False, "duplicate": False}}

    def branches(self, source=None, plan=None):
        source, plan = source or self.source, plan or self.plan
        return {branch: execute_branch(branch, source, plan) for branch in ("orders", "refunds")}

    def test_general_positive_scales_and_integer_multipliers(self):
        for scale in (3, 10, 125):
            plan = deepcopy(self.plan)
            plan["orders"]["scale_to_cents"] = scale
            plan["refunds"]["scale_to_cents"] = scale
            branches = self.branches(plan=plan)
            for multiplier in (0, 3, -4, 17):
                with self.subTest(scale=scale, multiplier=multiplier):
                    result = integrate(branches, {"refund_multiplier": multiplier})
                    self.assertEqual(result[0]["gross_cents"], 13 * scale)
                    self.assertEqual(result[0]["refund_cents"], 3 * scale)
                    self.assertEqual(result[0]["net_cents"], (13 - 3 * multiplier) * scale)
                    self.assertTrue(all(type(result[0][name]) is int
                                        for name in ("gross_cents", "refund_cents", "net_cents")))

    def test_boolean_noninteger_and_nonpositive_scales_are_rejected(self):
        for branch in ("orders", "refunds"):
            for scale in (True, False, 0, -1, 1.0, "10", None):
                with self.subTest(branch=branch, scale=scale):
                    plan = deepcopy(self.plan)
                    plan[branch]["scale_to_cents"] = scale
                    with self.assertRaises(ValueError):
                        execute_branch(branch, self.source, plan)

    def test_boolean_or_noninteger_sign_and_multiplier_are_rejected(self):
        for invalid in (True, False, 1.0, "1", None):
            with self.subTest(invalid=invalid):
                plan = deepcopy(self.plan)
                plan["refunds"]["sign"] = invalid
                with self.assertRaises(ValueError):
                    execute_branch("refunds", self.source, plan)
                with self.assertRaises(ValueError):
                    integrate(self.branches(), {"refund_multiplier": invalid})

    def test_large_exact_integer_values_stay_exact_within_sqlite_range(self):
        source = deepcopy(self.source)
        source["orders"][0]["amount"] = 2**60 + 7
        source["refunds"][0]["amount"] = 2**40 + 3
        result = integrate(self.branches(source=source), {"refund_multiplier": 3})
        self.assertEqual(result[0]["net_cents"], 2**60 + 7 - 3 * (2**40 + 3))
        self.assertIs(type(result[0]["net_cents"]), int)

    def test_sqlite_branch_multiplication_overflow_cannot_be_a_money_result(self):
        for branch, table in (("orders", "orders"), ("refunds", "refunds")):
            with self.subTest(branch=branch):
                source, plan = deepcopy(self.source), deepcopy(self.plan)
                source[table][0]["amount"] = 2**62
                plan[branch]["scale_to_cents"] = 4
                with self.assertRaises((ValueError, OverflowError, sqlite3.Error)):
                    execute_branch(branch, source, plan)

    def test_sqlite_sum_and_net_overflow_do_not_escape_as_float(self):
        source = deepcopy(self.source)
        source["orders"][0]["amount"] = 2**62
        source["refunds"][0]["amount"] = 2**62
        branches = self.branches(source=source)
        with self.assertRaises((ValueError, OverflowError, sqlite3.Error)):
            integrate(branches, {"refund_multiplier": -1})
        branches["refunds"]["rows"].append({"refund_id": "r2", "order_id": "o", "refund_cents": 2**62})
        with self.assertRaises((ValueError, OverflowError, sqlite3.Error)):
            integrate(branches, {"refund_multiplier": 1})

    def test_python_integer_binding_overflow_is_explicit(self):
        plan = deepcopy(self.plan)
        plan["orders"]["scale_to_cents"] = 2**64
        with self.assertRaises((ValueError, OverflowError, sqlite3.Error)):
            execute_branch("orders", self.source, plan)
        with self.assertRaises((ValueError, OverflowError, sqlite3.Error)):
            integrate(self.branches(), {"refund_multiplier": 2**64})

    def test_noninteger_source_money_cannot_be_laundered_by_sqlite_affinity(self):
        for table, branch in (("orders", "orders"), ("refunds", "refunds")):
            for invalid in (True, False, 1.0, 1.25, "13", None):
                with self.subTest(table=table, invalid=invalid):
                    source = deepcopy(self.source)
                    source[table][0]["amount"] = invalid
                    with self.assertRaises((ValueError, TypeError)):
                        execute_branch(branch, source, self.plan)

    def test_noninteger_branch_money_cannot_be_laundered_at_integration(self):
        for branch, field in (("orders", "gross_cents"), ("refunds", "refund_cents")):
            for invalid in (True, False, 1.0, 1.25, "13", None):
                with self.subTest(branch=branch, invalid=invalid):
                    branches = self.branches()
                    branches[branch]["rows"][0][field] = invalid
                    with self.assertRaises((ValueError, TypeError)):
                        integrate(branches, {"refund_multiplier": 1})


if __name__ == "__main__":
    unittest.main()
