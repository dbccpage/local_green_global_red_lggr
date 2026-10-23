import unittest
from fractions import Fraction

from lggr import ValidationError, classify_cochain, verify_l1_certificate
from lggr.examples import D_TRIANGLE, example_documents
from lggr.linear import matvec, matrix, solve_exact, vector


class LinearTests(unittest.TestCase):
    def test_exact_matching_certificate_proves_phi_one(self):
        result = verify_l1_certificate(**example_documents()['triangle_l1'])
        self.assertEqual(result['status'], 'OPTIMALITY_VERIFIED')
        self.assertEqual(result['D_transpose_dual'], ['0', '0', '0'])
        self.assertEqual(result['residual'], ['0', '0', '-1'])
        self.assertEqual(result['lower_bound'], '1')
        self.assertEqual(result['upper_bound'], '1')
        self.assertEqual(result['optimum'], '1')
        self.assertTrue(result['repair_impossible'])

    def test_wrong_annihilator_cannot_certify_a_bound(self):
        data = example_documents()['triangle_l1']
        data['dual'] = [1, 0, 0]
        result = verify_l1_certificate(**data)
        self.assertEqual(result['status'], 'INVALID_CERTIFICATE')
        self.assertFalse(result['dual_annihilates'])
        self.assertIsNone(result['lower_bound'])
        self.assertFalse(result['repair_impossible'])

    def test_unbounded_dual_rejected_even_when_pairing_matches(self):
        data = example_documents()['triangle_l1']
        data['dual'] = [2, 2, -2]
        result = verify_l1_certificate(**data)
        self.assertEqual(result['status'], 'INVALID_CERTIFICATE')
        self.assertFalse(result['dual_bounded'])

    def test_nonmatching_primal_proves_lower_bound_not_optimum(self):
        data = example_documents()['triangle_l1']
        data['potential'] = [0, 0, 0]
        result = verify_l1_certificate(**data)
        self.assertEqual(result['status'], 'LOWER_BOUND_VERIFIED')
        self.assertEqual(result['lower_bound'], '1')
        self.assertEqual(result['upper_bound'], '3')
        self.assertIsNone(result['optimum'])
        self.assertTrue(result['repair_impossible'])

    def test_negative_lower_bound_does_not_prove_nonrepairability(self):
        data = example_documents()['triangle_l1']
        data['dual'] = [-1, -1, 1]
        result = verify_l1_certificate(**data)
        self.assertEqual(result['status'], 'LOWER_BOUND_VERIFIED')
        self.assertEqual(result['lower_bound'], '-1')
        self.assertFalse(result['repair_impossible'])

    def test_fractional_weights_are_exact(self):
        data = example_documents()['triangle_l1']
        data['weights'] = ['1/3', '1/3', '1/3']
        data['dual'] = ['1/3', '1/3', '-1/3']
        result = verify_l1_certificate(**data)
        self.assertEqual(result['status'], 'OPTIMALITY_VERIFIED')
        self.assertEqual(result['optimum'], '1/3')
        self.assertEqual(result['duality_gap'], '0')

    def test_exact_repair_proves_zero_optimum(self):
        data = example_documents()['triangle_l1']
        data['h'] = [1, 1, 2]
        result = verify_l1_certificate(**data)
        self.assertEqual(result['status'], 'OPTIMALITY_VERIFIED')
        self.assertEqual(result['optimum'], '0')
        self.assertTrue(result['supplied_potential_repairs'])
        self.assertFalse(result['repair_impossible'])

    def test_zero_and_negative_weights_are_invalid_input(self):
        for weight in (0, -1):
            data = example_documents()['triangle_l1']
            data['weights'][0] = weight
            with self.assertRaises(ValidationError):
                verify_l1_certificate(**data)

    def test_float_and_boolean_coefficients_are_rejected(self):
        for value in (0.1, True):
            data = example_documents()['triangle_l1']
            data['dual'][0] = value
            with self.assertRaises(ValidationError):
                verify_l1_certificate(**data)

    def test_shape_and_denominator_errors_are_rejected(self):
        for key, value in (('D', []), ('D', [[1], [1, 2]]), ('h', [1]), ('dual', ['1/0', 1, -1])):
            data = example_documents()['triangle_l1']
            data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValidationError):
                verify_l1_certificate(**data)

    def test_unfilled_triangle_is_closed_nonexact(self):
        result = classify_cochain(**example_documents()['triangle_unfilled'])
        self.assertEqual(result['status'], 'CLOSED_NONEXACT')
        self.assertTrue(result['represents_nonzero_H1'])
        self.assertFalse(result['repair_exists'])

    def test_filled_triangle_has_closure_failure_not_H1_class(self):
        result = classify_cochain(**example_documents()['triangle_filled'])
        self.assertEqual(result['status'], 'CLOSURE_FAILURE')
        self.assertEqual(result['closure'], ['1'])
        self.assertFalse(result['represents_nonzero_H1'])

    def test_budget_differences_are_exact(self):
        result = classify_cochain(**example_documents()['budget_exact_cochain'])
        self.assertEqual(result['status'], 'EXACT')
        self.assertTrue(result['repair_exists'])
        self.assertFalse(result['represents_nonzero_H1'])
        d, h = matrix(D_TRIANGLE, 'D'), vector([1, 1, 2], 'h')
        potential = vector(result['potential'], 'potential')
        self.assertEqual(matvec(d, potential), h)

    def test_missing_D1_does_not_invent_a_cohomology_class(self):
        result = classify_cochain(D_TRIANGLE, [1, 1, 1])
        self.assertEqual(result['status'], 'NONREPAIRABLE')
        self.assertIsNone(result['represents_nonzero_H1'])

    def test_noncomplex_is_rejected(self):
        result = classify_cochain(D_TRIANGLE, [1, 1, 1], [[1, 1, 1]])
        self.assertEqual(result['status'], 'INVALID_COMPLEX')
        self.assertIsNone(result['represents_nonzero_H1'])

    def test_underdetermined_and_inconsistent_exact_systems(self):
        d = matrix([[1, 1], [2, 2]], 'D')
        solution = solve_exact(d, vector([3, 6], 'h'))
        self.assertIsNotNone(solution)
        self.assertEqual(matvec(d, solution), vector([3, 6], 'h'))
        self.assertIsNone(solve_exact(d, vector([3, 7], 'h')))

    def test_exact_elimination_requires_row_swap(self):
        d = matrix([[0, 2], [1, 1]], 'D')
        solution = solve_exact(d, vector([1, 1], 'h'))
        self.assertEqual(solution, (Fraction(1, 2), Fraction(1, 2)))

    def test_dual_bound_against_independent_finite_potential_search(self):
        # A finite search is only a cross-check, not the proof of the optimum.
        import itertools
        d = matrix(D_TRIANGLE, 'D')
        h = vector([1, 1, 1], 'h')
        costs = []
        for values in itertools.product(range(-2, 3), repeat=3):
            dx = matvec(d, vector(values, 'x'))
            costs.append(sum(abs(a - b) for a, b in zip(h, dx)))
        self.assertEqual(min(costs), 1)
        self.assertTrue(all(c >= 1 for c in costs))
