import copy
import itertools
import unittest
from dataclasses import replace

from lggr import BudgetPolicy, StateRef, StepWitness, ValidationError, audit_document, audit_history, history_document, make_witness
from lggr.common import digest
from lggr.examples import example_documents
from lggr.witnesses import local_accepts


class WitnessTests(unittest.TestCase):
    def test_bad_trace_locally_green_globally_red(self):
        doc = history_document((0, 1, 2))
        result = audit_document(doc)
        self.assertEqual(result['status'], 'OBSTRUCTION_DETECTED')
        self.assertTrue(all(c['protected_policy_acceptance'] for c in result['local_checks']))
        self.assertEqual(result['arithmetic']['signed_total'], 2)
        self.assertFalse(result['arithmetic']['global_verdict'])
        self.assertFalse(result['composition_certified'])
        self.assertEqual(result['authority_effect'], 'None')

    def test_good_trace(self):
        result = audit_document(history_document((0, 1, 0)))
        self.assertEqual(result['status'], 'COMPOSITION_VERIFIED')
        self.assertEqual(result['arithmetic']['signed_deltas'], [1, -1])
        self.assertTrue(result['arithmetic']['global_verdict'])

    def test_protected_negative_probes_still_fail(self):
        policy = BudgetPolicy()
        self.assertFalse(local_accepts(policy, 0, 2))
        self.assertFalse(local_accepts(policy, 0, 3))
        self.assertTrue(local_accepts(policy, 0, 1))
        self.assertTrue(local_accepts(policy, 1, 2))

    def test_reports_alone_do_not_establish_violation(self):
        result = audit_document(example_documents()['reports_only'])
        self.assertEqual(result['status'], 'WITNESS_INCOMPLETE')
        self.assertIsNone(result['arithmetic'])
        self.assertFalse(result['composition_certified'])

    def test_all_363_histories_up_to_five_states_against_independent_check(self):
        count = 0
        for n in range(1, 6):
            for history in itertools.product((0, 1, 2), repeat=n):
                count += 1
                result = audit_document(history_document(history))
                local_ok = all(abs(b - a) <= 1 for a, b in zip(history, history[1:]))
                global_ok = abs(history[-1] - history[0]) <= 1
                expected = ('LOCAL_REJECTED' if not local_ok else
                            'COMPOSITION_VERIFIED' if global_ok else 'OBSTRUCTION_DETECTED')
                self.assertEqual(result['status'], expected, history)
                self.assertEqual(result['arithmetic']['global_verdict'], global_ok, history)
        self.assertEqual(count, 363)

    def test_baseline_only_is_scoped_zero_step_composition(self):
        result = audit_document(history_document((1,)))
        self.assertEqual(result['status'], 'COMPOSITION_VERIFIED')
        self.assertEqual(result['arithmetic']['signed_total'], 0)

    def test_empty_history_constructor_rejected(self):
        with self.assertRaises(ValidationError):
            history_document(())

    def test_forged_positive_local_verdict_is_invalid(self):
        doc = history_document((0, 2))
        doc['witnesses'][0]['local_accepted'] = True
        result = audit_document(doc)
        self.assertEqual(result['status'], 'INVALID_WITNESS')
        self.assertIn('LOCAL_REJECTED', {f['kind'] for f in result['findings']})

    def test_accurate_negative_local_verdict_is_local_rejection(self):
        result = audit_document(history_document((0, 2)))
        self.assertEqual(result['status'], 'LOCAL_REJECTED')
        self.assertNotIn('INVALID_WITNESS', {f['kind'] for f in result['findings']})

    def test_forged_magnitude_is_invalid(self):
        doc = history_document((0, 1))
        doc['witnesses'][0]['observed_magnitude'] = 0
        self.assertEqual(audit_document(doc)['status'], 'INVALID_WITNESS')

    def test_forged_smoke_verdict_is_invalid(self):
        doc = history_document((0, 1))
        doc['witnesses'][0]['smoke_passed'] = False
        self.assertEqual(audit_document(doc)['status'], 'INVALID_WITNESS')

    def test_boundary_mismatch_is_not_called_a_global_violation(self):
        doc = history_document((0, 1, 2))
        doc['witnesses'][1]['source']['state_id'] = 'unrelated-version'
        result = audit_document(doc)
        self.assertEqual(result['status'], 'INVALID_WITNESS')
        self.assertIsNone(result['arithmetic'])

    def test_conflicting_values_for_same_identity_are_invalid(self):
        doc = history_document((0, 1, 2))
        doc['witnesses'][1]['source']['value'] = 0
        result = audit_document(doc)
        self.assertEqual(result['status'], 'INVALID_WITNESS')
        self.assertIsNone(result['arithmetic'])

    def test_duplicate_witness_is_invalid(self):
        doc = history_document((0, 1, 0))
        doc['witnesses'][1]['witness_id'] = doc['witnesses'][0]['witness_id']
        self.assertEqual(audit_document(doc)['status'], 'INVALID_WITNESS')

    def test_baseline_must_be_observed(self):
        doc = history_document((0, 1))
        doc['baseline']['value'] = None
        self.assertEqual(audit_document(doc)['status'], 'WITNESS_INCOMPLETE')

    def test_baseline_must_be_legal(self):
        result = audit_document(history_document((3, 2)))
        self.assertEqual(result['status'], 'INVALID_WITNESS')

    def test_signed_endpoints_can_reconstruct_missing_duplicate_value(self):
        doc = history_document((0, 1, 0))
        doc['witnesses'][1]['source']['value'] = None
        self.assertEqual(audit_document(doc)['status'], 'COMPOSITION_VERIFIED')

    def test_authority_changes_do_not_self_authorize(self):
        result = audit_document(example_documents()['authority_changed'])
        self.assertEqual(result['status'], 'AUTHORITY_REQUIRED')
        self.assertFalse(result['composition_certified'])

    def test_evaluator_and_spec_changes_require_separate_transition(self):
        for key in ('evaluator_id', 'spec_id'):
            with self.subTest(key=key):
                doc = history_document((0, 1))
                doc['witnesses'][0][key] += '/changed'
                self.assertEqual(audit_document(doc)['status'], 'AUTHORITY_REQUIRED')

    def test_policy_hash_binds_contents_not_just_name(self):
        doc = history_document((0, 1))
        doc['policy']['max_total'] = 2
        result = audit_document(doc)
        self.assertEqual(result['status'], 'AUTHORITY_REQUIRED')

    def test_representation_change_is_not_silently_reinterpreted(self):
        doc = history_document((0, 1))
        doc['witnesses'][0]['representation_id'] = 'opaque-encoding/v2'
        result = audit_document(doc)
        self.assertEqual(result['status'], 'UNSUPPORTED')
        self.assertIsNone(result['arithmetic'])

    def test_early_obligation_survives_later_empty_list(self):
        doc = example_documents()['open_obligation']
        self.assertEqual(doc['witnesses'][1]['obligations'], [])
        result = audit_document(doc)
        self.assertEqual(result['status'], 'WITNESS_INCOMPLETE')
        self.assertEqual(result['unresolved_obligations'], ['verify-new-interface-semantics'])
        self.assertTrue(result['arithmetic']['global_verdict'])

    def test_prior_obligations_are_retained(self):
        doc = history_document((0, 1))
        doc['prior_obligations'] = ['old-obligation']
        result = audit_document(doc)
        self.assertEqual(result['unresolved_obligations'], ['old-obligation'])
        self.assertEqual(result['status'], 'WITNESS_INCOMPLETE')

    def test_endpoint_and_every_prefix_are_distinct_explicit_queries(self):
        endpoint = audit_document(history_document((0, 1, 2, 1)))
        self.assertEqual(endpoint['status'], 'COMPOSITION_VERIFIED')
        self.assertTrue(endpoint['arithmetic']['endpoint_verdict'])
        self.assertFalse(endpoint['arithmetic']['every_prefix_verdict'])
        prefix = audit_document(history_document((0, 1, 2, 1),
                                policy=BudgetPolicy(query_scope='every_prefix')))
        self.assertEqual(prefix['status'], 'OBSTRUCTION_DETECTED')
        self.assertTrue(prefix['arithmetic']['endpoint_verdict'])
        self.assertFalse(prefix['arithmetic']['global_verdict'])

    def test_negative_and_nonunit_bounds(self):
        policy = BudgetPolicy(allowed_states=(-4, -2, 0, 2, 4), max_step=2, max_total=2)
        result = audit_document(history_document((0, -2, -4), policy=policy))
        self.assertEqual(result['status'], 'OBSTRUCTION_DETECTED')
        self.assertEqual(result['arithmetic']['signed_total'], -4)

    def test_invalid_policy_rejected(self):
        for kw in ({'max_step': -1}, {'max_total': True}, {'allowed_states': ()},
                   {'allowed_states': (0, 0)}, {'allowed_states': (True, 1)}, {'query_scope': 'unknown'}):
            with self.subTest(kw=kw), self.assertRaises(ValidationError):
                BudgetPolicy(**kw)

    def test_bool_is_not_an_integer_state(self):
        with self.assertRaises(ValidationError):
            StateRef('state', True)

    def test_unknown_input_field_rejected(self):
        doc = history_document((0, 1))
        doc['approve_anyway'] = True
        with self.assertRaises(ValidationError):
            audit_document(doc)

    def test_receipt_hash_reproduces_and_input_is_unchanged(self):
        doc = history_document((0, 1, 2))
        original = copy.deepcopy(doc)
        a, b = audit_document(doc), audit_document(doc)
        self.assertEqual(a, b)
        self.assertEqual(doc, original)
        body = {k: v for k, v in a.items() if k != 'receipt_sha256'}
        self.assertEqual(a['receipt_sha256'], digest(body))

    def test_multiple_failures_are_retained_not_hidden_by_primary_status(self):
        doc = history_document((0, 1, 2))
        doc['witnesses'][-1]['authority_id'] = 'other-owner'
        result = audit_document(doc)
        kinds = {f['kind'] for f in result['findings']}
        self.assertIn('AUTHORITY_REQUIRED', kinds)
        self.assertIn('OBSTRUCTION_DETECTED', kinds)
        self.assertFalse(result['arithmetic']['global_verdict'])
