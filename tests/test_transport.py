import unittest

from lggr import ValidationError, classify_cochain, verify_transport
from lggr.examples import D_TRIANGLE, example_documents


def data(name):
    return {k: v for k, v in example_documents()[name].items() if k != 'require_reflection'}


class TransportTests(unittest.TestCase):
    def test_nontrivial_permutation_retraction(self):
        result = verify_transport(**data('faithful_transport'))
        self.assertEqual(result['status'], 'RETRACTION_VERIFIED')
        self.assertTrue(result['repair_preservation_verified'])
        self.assertTrue(result['nonrepairability_reflection_verified'])

    def test_lossy_map_commutes_without_reflection(self):
        result = verify_transport(**data('lossy_transport'))
        self.assertEqual(result['status'], 'COMMUTING_TRANSPORT_VERIFIED')
        self.assertTrue(result['repair_preservation_verified'])
        self.assertFalse(result['nonrepairability_reflection_verified'])

    def test_lossy_map_can_kill_source_obstruction(self):
        source = classify_cochain(D_TRIANGLE, [1, 1, 1])
        target = classify_cochain([[0]], [0])
        self.assertFalse(source['repair_exists'])
        self.assertTrue(target['repair_exists'])
        self.assertFalse(verify_transport(**data('lossy_transport'))['nonrepairability_reflection_verified'])

    def test_noncommuting_forward_map_is_invalid(self):
        doc = data('faithful_transport')
        doc.pop('G0')
        doc.pop('G1')
        doc['F1'][0][0] += 1
        result = verify_transport(**doc)
        self.assertEqual(result['status'], 'INVALID_TRANSPORT')
        self.assertFalse(result['repair_preservation_verified'])

    def test_wrong_left_inverse_cannot_certify_reflection(self):
        doc = data('faithful_transport')
        doc['G0'] = [[0, 0, 0]] * 3
        result = verify_transport(**doc)
        self.assertEqual(result['status'], 'RETRACTION_REJECTED')
        self.assertTrue(result['forward_commutes'])
        self.assertFalse(result['nonrepairability_reflection_verified'])

    def test_zero_pseudoinverse_does_not_rescue_lossy_transport(self):
        doc = data('lossy_transport')
        doc['G0'] = [[0], [0], [0]]
        doc['G1'] = [[0], [0], [0]]
        self.assertEqual(verify_transport(**doc)['status'], 'RETRACTION_REJECTED')

    def test_partial_retraction_is_invalid_input(self):
        doc = data('faithful_transport')
        doc.pop('G1')
        with self.assertRaises(ValidationError):
            verify_transport(**doc)

    def test_wrong_shape_is_invalid_input(self):
        doc = data('faithful_transport')
        doc['F0'] = [[1]]
        with self.assertRaises(ValidationError):
            verify_transport(**doc)
