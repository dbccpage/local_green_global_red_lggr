from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations, product
import unittest

from finite_limits import (checked_extension, distinguishing_word, fiber_certificate,
    future_partition, memory_capacity, optimal_queries, verify_fibers, verify_query_tree)


class ExactLimitsTests(unittest.TestCase):
    def test_scalar_minimax_and_explicit_decoder(self):
        certificate = fiber_certificate(("same", "same"), (112, 143))
        self.assertEqual(certificate["radius"], Q(31, 2))
        self.assertEqual(certificate["fibers"][0][-1], Q(255, 2))
        self.assertTrue(verify_fibers(("same", "same"), (112, 143), certificate))
        self.assertEqual(fiber_certificate(("old", "new"), (112, 143))["radius"], 0)

    def test_checked_update_does_not_erase_earlier_observations(self):
        old = ("old",), (112,)
        with self.assertRaisesRegex(ValueError, "MEMORY_CONTRACT_BROKEN"):
            checked_extension(*old, ("old",), (143,))
        view, values, certificate = checked_extension(*old, ("new",), (143,))
        self.assertEqual(values, (112, 143))
        self.assertEqual(certificate["radius"], 0)
        self.assertEqual(old, (("old",), (112,)))

    def test_memory_extension_for_new_actions(self):
        readout = (0, 0, 1, 1)
        self.assertEqual(memory_capacity(readout, ((0, 1, 2, 3),)), {"classes": 2, "fixed_length_bits": 1})
        self.assertEqual(memory_capacity(readout, ((0, 2, 1, 3),)), {"classes": 4, "fixed_length_bits": 2})
        self.assertEqual(distinguishing_word(readout, ((0, 2, 1, 3),), 0, 1), (0,))

    def test_all_four_state_binary_one_action_models(self):
        comparisons = 0
        for readout in product((0, 1), repeat=4):
            for action in product(range(4), repeat=4):
                classes = future_partition(readout, (action,))
                for x, y in product(range(4), repeat=2):
                    word = distinguishing_word(readout, (action,), x, y)
                    self.assertEqual(classes[x] == classes[y], word is None)
                    if word is not None:
                        u, v = x, y
                        for _ in word:
                            u, v = action[u], action[v]
                        self.assertNotEqual(readout[u], readout[v])
                    comparisons += 1
        self.assertEqual(comparisons, 65536)

    def test_adaptive_two_queries_versus_fixed_three(self):
        values = (0, 1, 2, 3)
        queries = ((0, 0, 1, 1), (0, 1, 0, 0), (0, 0, 0, 1))
        result = optimal_queries(values, queries)
        self.assertEqual(result[0], 2)
        self.assertTrue(verify_query_tree(values, queries, result))
        for selected in combinations(range(3), 2):
            signatures = tuple(str(tuple(queries[q][i] for q in selected)) for i in range(4))
            self.assertGreater(fiber_certificate(signatures, values)["radius"], 0)
        all_signatures = tuple(str(tuple(q[i] for q in queries)) for i in range(4))
        self.assertEqual(fiber_certificate(all_signatures, values)["radius"], 0)

    def test_unavailable_discriminating_query_refuses(self):
        values, queries = (0, 1), ((0, 0),)
        self.assertIsNone(optimal_queries(values, queries))
        self.assertTrue(verify_query_tree(values, queries, None))
        self.assertFalse(verify_query_tree(values, ((0, 1),), None))

    def test_tolerance_changes_the_declared_task(self):
        self.assertIsNone(optimal_queries((0, 2), ()))
        result = optimal_queries((0, 2), (), tolerance=Q(1))
        self.assertEqual(result, (0, {"value": "1"}))
        self.assertTrue(verify_query_tree((0, 2), (), result, tolerance=Q(1)))
        self.assertFalse(verify_query_tree((0, 2), (), result))

    def test_certificate_mutations_are_rejected(self):
        original = fiber_certificate((0, 0), (0, 2))
        changes = (("radius", Q(0)), ("diameter", Q(0)), ("witness", (0, 0)),
                   ("fibers", ()), ("radius", 1.0), ("diameter", True))
        for field, value in changes:
            altered = deepcopy(original)
            altered[field] = value
            self.assertFalse(verify_fibers((0, 0), (0, 2), altered), (field, value))

    def test_tree_cost_wrong_leaf_and_missing_outcome_are_rejected(self):
        values, queries = (0, 1), ((0, 1),)
        result = optimal_queries(values, queries)
        self.assertFalse(verify_query_tree(values, queries, (0, result[1])))
        altered = deepcopy(result)
        altered[1]["children"].pop("1")
        self.assertFalse(verify_query_tree(values, queries, altered))
        altered = deepcopy(result)
        altered[1]["children"]["1"]["value"] = "0"
        self.assertFalse(verify_query_tree(values, queries, altered))

    def test_sound_but_nonoptimal_tree_is_rejected(self):
        values = (0, 0, 1, 1)
        queries = ((0, 0, 1, 1), (0, 1, 0, 1))
        good = {"query": 0, "children": {"0": {"value": "0"}, "1": {"value": "1"}}}
        wasteful = {"query": 1, "children": {"0": deepcopy(good), "1": deepcopy(good)}}
        self.assertFalse(verify_query_tree(values, queries, (2, wasteful)))

    def test_finite_alphabet_is_not_a_finite_unbounded_history(self):
        histories = {bits for length in range(7) for bits in product((0, 1), repeat=length)}
        self.assertEqual(len(histories), 127)
        self.assertTrue(all(set(bits) <= {0, 1} for bits in histories))

    def test_semantic_self_knowledge_is_not_diagonal_prediction(self):
        checks = 0
        for record in product(range(4), repeat=4):
            for proposition in product((False, True), repeat=4):
                known = tuple(all(proposition[y] for y in range(4) if record[y] == record[x]) for x in range(4))
                for x in range(4):
                    if known[x]:
                        self.assertTrue(proposition[x])
                        self.assertTrue(all(known[y] for y in range(4) if record[y] == record[x]))
                    checks += 1
        self.assertEqual(checks, 16384)

    def test_exact_input_and_scope_limits_refuse(self):
        self.assertFalse(verify_fibers((False,), (0,), fiber_certificate((0,), (0,))))
        for bad in (True, 0.5, float("nan"), float("inf"), "1/2"):
            with self.assertRaises(ValueError):
                fiber_certificate((0,), (bad,))
        with self.assertRaises(ValueError):
            optimal_queries(tuple(range(13)), ())
        with self.assertRaises(ValueError):
            optimal_queries((0, 1), ((False, True),))
        with self.assertRaises(ValueError):
            future_partition((0, 1), ((0, 2),))
        with self.assertRaises(ValueError):
            checked_extension((0,), (0,), (), (), cap=-1)


if __name__ == "__main__":
    unittest.main()
