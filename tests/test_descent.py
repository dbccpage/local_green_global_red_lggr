import copy
import itertools
import unittest

from lggr import ValidationError, analyze_descent, decode, evaluator_defect, verify_descent_certificate
from lggr.examples import example_documents, finite_census


class DescentTests(unittest.TestCase):
    def test_collision_is_not_a_realized_violation(self):
        data = example_documents()['report_collision']
        result = analyze_descent(data['rows'], scope_id=data['scope_id'])
        self.assertEqual(result['status'], 'REPORT_INSUFFICIENT')
        self.assertIsNone(result['realized_history_violation'])
        self.assertTrue(verify_descent_certificate(data['rows'], result))
        self.assertEqual(result['collision']['left']['report'], result['collision']['right']['report'])
        self.assertNotEqual(result['collision']['left']['query'], result['collision']['right']['query'])

    def test_refinement_decodes_on_realized_image(self):
        data = example_documents()['refined_reports']
        result = analyze_descent(data['rows'], scope_id=data['scope_id'])
        self.assertEqual(result['status'], 'DECODER_VERIFIED')
        self.assertTrue(verify_descent_certificate(data['rows'], result))
        self.assertTrue(decode(result, [1, -1]))
        self.assertFalse(decode(result, [1, 1]))
        with self.assertRaises(KeyError):
            decode(result, [999])

    def test_complete_216_case_census(self):
        result = finite_census()
        self.assertEqual(result, {'factorization_cases': 216, 'decoders': 126, 'collisions': 90,
                                  'boolean_verdict_cases': 8})

    def test_all_eight_defects(self):
        for a, b, g in itertools.product((0, 1), repeat=3):
            with self.subTest(a=a, b=b, g=g):
                result = evaluator_defect(a, b, g)
                delta = g - a * b
                self.assertEqual(result['delta'], delta)
                self.assertEqual(result['defect_kind'], {-1: 'NGD', 0: 'ZDR', 1: 'PGD'}[delta])

    def test_defect_rejects_non_boolean_numbers(self):
        for value in (-1, 2, '1', 1.0, None):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                evaluator_defect(value, 1, 0)

    def test_empty_carrier_is_explicitly_vacuous(self):
        result = analyze_descent([], scope_id='empty')
        self.assertEqual(result['carrier_size'], 0)
        self.assertEqual(result['decoder'], [])
        self.assertTrue(verify_descent_certificate([], result))
        with self.assertRaises(KeyError):
            decode(result, 0)

    def test_boolean_and_integer_reports_remain_distinct(self):
        rows = [{'state_id': 'a', 'report': True, 'query': False},
                {'state_id': 'b', 'report': 1, 'query': True}]
        result = analyze_descent(rows, scope_id='types')
        self.assertEqual(result['status'], 'DECODER_VERIFIED')
        self.assertFalse(decode(result, True))
        self.assertTrue(decode(result, 1))

    def test_boolean_and_integer_targets_remain_distinct(self):
        rows = [{'state_id': 'a', 'report': 'same', 'query': True},
                {'state_id': 'b', 'report': 'same', 'query': 1}]
        self.assertEqual(analyze_descent(rows, scope_id='types')['status'], 'REPORT_INSUFFICIENT')

    def test_object_key_order_does_not_invent_distinctions(self):
        rows = [{'state_id': 'a', 'report': {'x': 1, 'y': 2}, 'query': False},
                {'state_id': 'b', 'report': {'y': 2, 'x': 1}, 'query': True}]
        self.assertEqual(analyze_descent(rows, scope_id='objects')['status'], 'REPORT_INSUFFICIENT')

    def test_duplicate_state_ids_rejected(self):
        row = {'state_id': 'a', 'report': 1, 'query': True}
        with self.assertRaises(ValidationError):
            analyze_descent([row, row], scope_id='bad')

    def test_unknown_fields_and_floats_rejected(self):
        for row in ({'state_id': 'a', 'report': 0, 'query': True, 'ignore_me': 1},
                    {'state_id': 'a', 'report': 0.1, 'query': True}):
            with self.assertRaises(ValidationError):
                analyze_descent([row], scope_id='bad')

    def test_tampered_collision_fails_replay(self):
        data = example_documents()['report_collision']
        cert = analyze_descent(data['rows'], scope_id=data['scope_id'])
        cert['collision']['left']['query'] = cert['collision']['right']['query']
        self.assertFalse(verify_descent_certificate(data['rows'], cert))

    def test_tampered_decoder_or_table_fails_replay(self):
        rows = [{'state_id': 'a', 'report': 0, 'query': True}]
        cert = analyze_descent(rows, scope_id='one')
        bad_cert = copy.deepcopy(cert)
        bad_cert['decoder'][0]['query'] = False
        self.assertFalse(verify_descent_certificate(rows, bad_cert))
        changed = [{'state_id': 'a', 'report': 0, 'query': False}]
        self.assertFalse(verify_descent_certificate(changed, cert))
        bad_cert = copy.deepcopy(cert)
        bad_cert['decoder'].append({'report': 'unrealized', 'query': True})
        self.assertFalse(verify_descent_certificate(rows, bad_cert))

    def test_malformed_certificate_rejected(self):
        rows = [{'state_id': 'a', 'report': 0, 'query': True}]
        for certificate in ({}, None, {'schema': 'incorrect'}):
            self.assertFalse(verify_descent_certificate(rows, certificate))

    def test_certificate_does_not_alias_mutable_input(self):
        rows = [{'state_id': 'a', 'report': [1], 'query': True}]
        cert = analyze_descent(rows, scope_id='copy')
        rows[0]['report'][0] = 99
        self.assertEqual(cert['decoder'][0]['report'], [1])

    def test_row_order_is_irrelevant(self):
        data = example_documents()['report_collision']
        self.assertEqual(analyze_descent(data['rows'], scope_id='same'),
                         analyze_descent(reversed(data['rows']), scope_id='same'))

    def test_a_collision_receipt_cannot_claim_realized_failure(self):
        data = example_documents()['report_collision']
        certificate = analyze_descent(data['rows'], scope_id=data['scope_id'])
        certificate['realized_history_violation'] = True
        self.assertFalse(verify_descent_certificate(data['rows'], certificate))

    def test_extra_authorization_field_cannot_be_smuggled_into_certificate(self):
        data = example_documents()['refined_reports']
        certificate = analyze_descent(data['rows'], scope_id=data['scope_id'])
        certificate['merge_authorized'] = True
        self.assertFalse(verify_descent_certificate(data['rows'], certificate))

    def test_unverified_semantic_caption_cannot_be_substituted(self):
        data = example_documents()['refined_reports']
        certificate = analyze_descent(data['rows'], scope_id=data['scope_id'])
        certificate['meaning'] = 'This establishes universal AI safety.'
        self.assertFalse(verify_descent_certificate(data['rows'], certificate))
