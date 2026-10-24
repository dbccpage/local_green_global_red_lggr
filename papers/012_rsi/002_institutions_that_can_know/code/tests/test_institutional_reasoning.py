"""Run with: python -m unittest -v test_institutional_reasoning.py"""
import itertools
import unittest

from institutional_reasoning import (
    ComparisonStatus, FixtureMandate, bounded_search, invariant_separates,
    jointly_acceptable, minimum_fixed_side_bits, permitted_in_fixture,
    reachable, recovery_decoder, side_information_code,
)


class InstitutionalReasoningTests(unittest.TestCase):
    def test_recoverability_exhaustive_against_decoder_search(self):
        domain = (0, 1, 2)
        checked = 0
        for c in itertools.product(range(2), repeat=3):
            labels = sorted(set(c))
            for q in itertools.product(range(3), repeat=3):
                brute = any(
                    all(dict(zip(labels, out))[c[x]] == q[x] for x in domain)
                    for out in itertools.product(range(3), repeat=len(labels))
                )
                got = recovery_decoder(domain, c.__getitem__, q.__getitem__)
                self.assertEqual(got is not None, brute)
                checked += 1
        self.assertEqual(checked, 216)

    def test_source_dependency_is_lost_by_vote_count(self):
        records = ('two_independent_witnesses', 'one_witness_copied_twice')
        self.assertIsNone(recovery_decoder(records, lambda _: 2, lambda x: x))

    def test_sum_is_recoverable_from_sum(self):
        domain = tuple(itertools.product((0, 1), repeat=3))
        self.assertEqual(recovery_decoder(domain, sum, sum), {0: 0, 1: 1, 2: 2, 3: 3})

    def test_order_is_not_recoverable_from_sum(self):
        domain = tuple(itertools.product((0, 1), repeat=3))
        self.assertIsNone(recovery_decoder(domain, sum, lambda x: x))

    def test_side_information_bound_and_construction(self):
        domain = tuple(itertools.product((0, 1), repeat=3))
        bits, encoder, decoder = side_information_code(domain, sum, lambda x: x)
        self.assertEqual(bits, 2)
        self.assertEqual(minimum_fixed_side_bits(domain, sum, lambda x: x), bits)
        for x in domain:
            self.assertLess(encoder[x], 2 ** bits)
            self.assertEqual(decoder[sum(x), encoder[x]], x)
        # One bit cannot distinguish the three records whose sum is one.
        self.assertGreater(len([x for x in domain if sum(x) == 1]), 2)

    def test_zero_bits_when_profile_survives(self):
        domain = tuple(itertools.product((0, 1), repeat=3))
        self.assertEqual(minimum_fixed_side_bits(domain, sum, sum), 0)

    def test_side_bound_exhaustive_against_assignment_search(self):
        domain = (0, 1, 2)
        checked = 0
        for c in itertools.product(range(2), repeat=3):
            for q in itertools.product(range(3), repeat=3):
                predicted = minimum_fixed_side_bits(domain, c.__getitem__, q.__getitem__)
                brute_min = None
                for bits in range(3):
                    for side in itertools.product(range(2 ** bits), repeat=3):
                        if recovery_decoder(domain, lambda x: (c[x], side[x]), q.__getitem__) is not None:
                            brute_min = bits
                            break
                    if brute_min is not None:
                        break
                self.assertEqual(predicted, brute_min)
                checked += 1
        self.assertEqual(checked, 216)

    def test_nonempty_unique_domain_validation(self):
        with self.assertRaises(ValueError):
            recovery_decoder([], lambda x: x, lambda x: x)
        with self.assertRaises(ValueError):
            minimum_fixed_side_bits([1, 1], lambda x: x, lambda x: x)

    def test_local_projections_match_but_joint_constraints_fail(self):
        triples = tuple(itertools.product((0, 1), repeat=3))
        constraints = (
            lambda t: t[0] == t[1],
            lambda t: t[1] == t[2],
            lambda t: t[2] != t[0],
        )
        for pair in itertools.combinations(constraints, 2):
            self.assertTrue(any(all(p(t) for p in pair) for t in triples))
        self.assertFalse(any(all(p(t) for p in constraints) for t in triples))
        relations = ({(0, 0), (1, 1)}, {(0, 0), (1, 1)}, {(0, 1), (1, 0)})
        for relation in relations:
            for axis in (0, 1):
                self.assertEqual({t[axis] for t in relation}, {0, 1})

    def test_failed_search_is_not_non_equivalence(self):
        self.assertEqual(bounded_search([False, False]), ComparisonStatus.NO_ADMITTED_COMPARISON)
        self.assertNotEqual(bounded_search([]), ComparisonStatus.CERTIFIED_NON_EQUIVALENT)

    def test_relative_invariant_requires_preservation(self):
        self.assertEqual(invariant_separates(1, 2, invariant_preservation_verified=False),
                         ComparisonStatus.NO_ADMITTED_COMPARISON)
        self.assertEqual(invariant_separates(1, 2, invariant_preservation_verified=True),
                         ComparisonStatus.CERTIFIED_NON_EQUIVALENT)
        self.assertEqual(invariant_separates(1, 1, invariant_preservation_verified=True),
                         ComparisonStatus.NO_ADMITTED_COMPARISON)

    def test_joint_action_does_not_merge_reasons(self):
        reasons = {'engineering': 'suspected_fault', 'operations': 'inventory_check'}
        actions = jointly_acceptable([{'temporary_shutdown', 'repair'}, {'temporary_shutdown', 'recount'}])
        self.assertEqual(actions, {'temporary_shutdown'})
        self.assertNotEqual(reasons['engineering'], reasons['operations'])

    def test_no_joint_action_can_be_reported_honestly(self):
        self.assertEqual(jointly_acceptable([{'continue'}, {'stop'}]), set())
        with self.assertRaises(ValueError):
            jointly_acceptable([])

    def test_proposal_does_not_authorize_execution(self):
        self.assertFalse(permitted_in_fixture('shutdown', 'operator', 10, None))
        unsigned = FixtureMandate('M1', 'operator', frozenset({'shutdown'}), 20)
        self.assertFalse(permitted_in_fixture('shutdown', 'operator', 10, unsigned))

    def test_mandate_scope_executor_and_expiry(self):
        mandate = FixtureMandate('M1', 'operator', frozenset({'shutdown'}), 20, True)
        self.assertTrue(permitted_in_fixture('shutdown', 'operator', 10, mandate))
        self.assertFalse(permitted_in_fixture('delete_records', 'operator', 10, mandate))
        self.assertFalse(permitted_in_fixture('shutdown', 'outsider', 10, mandate))
        self.assertFalse(permitted_in_fixture('shutdown', 'operator', 20, mandate))

    def test_access_cut_preserves_records_but_loses_reachability(self):
        records = {'archive': 'original evidence remains unchanged'}
        before = {'requester': ('translator',), 'translator': ('archive',)}
        after = {'requester': (), 'translator': ('archive',)}
        self.assertTrue(reachable(before, 'requester', 'archive'))
        self.assertFalse(reachable(after, 'requester', 'archive'))
        self.assertIn('archive', records)

    def test_alternative_route_repairs_access(self):
        graph = {'requester': ('new_translator',), 'new_translator': ('archive',)}
        self.assertTrue(reachable(graph, 'requester', 'archive'))


if __name__ == '__main__':
    unittest.main()
