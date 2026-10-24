import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lggr.common import ValidationError, loads_strict

ROOT = Path(__file__).resolve().parents[1]


def run(*args, input_text=None, optimized=False):
    return subprocess.run([sys.executable, *(['-O'] if optimized else []), '-m', 'lggr', *args],
                          cwd=ROOT, text=True, encoding='utf-8', input=input_text,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)


class CliTests(unittest.TestCase):
    def test_demo_runs(self):
        result = run('demo')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['finite_census']['factorization_cases'], 216)
        self.assertFalse(data['comparison']['extra_detection_power_over_fixed_baseline_demonstrated'])

    def test_good_audit_exits_zero(self):
        result = run('audit', 'examples/good_history.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'COMPOSITION_VERIFIED')

    def test_bad_audit_exits_nonzero(self):
        result = run('audit', 'examples/bad_history.json')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'OBSTRUCTION_DETECTED')

    def test_optimized_python_does_not_disable_validation(self):
        result = run('audit', 'examples/bad_history.json', optimized=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'OBSTRUCTION_DETECTED')

    def test_collision_is_a_negative_result(self):
        result = run('descent', 'examples/report_collision.json')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'REPORT_INSUFFICIENT')

    def test_positive_linear_certificate(self):
        result = run('linear', 'examples/triangle_l1.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['optimum'], '1')

    def test_require_reflection_fails_on_lossy_map(self):
        result = run('transport', 'examples/lossy_transport.json')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(json.loads(result.stdout)['forward_commutes'])
        self.assertFalse(json.loads(result.stdout)['nonrepairability_reflection_verified'])

    def test_reflection_passes_on_retraction(self):
        result = run('transport', 'examples/faithful_transport.json')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_input_returns_json_error_not_traceback(self):
        for raw in ('{', '{"policy":1}', '{"x":1,"x":2}', '[NaN]', '{"a":0.5}'):
            result = run('audit', '-', input_text=raw)
            self.assertEqual(result.returncode, 2, raw)
            self.assertEqual(json.loads(result.stderr)['status'], 'INPUT_ERROR')
            self.assertNotIn('Traceback', result.stderr)

    def test_missing_file_is_input_error(self):
        result = run('audit', 'does-not-exist.json')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)['status'], 'INPUT_ERROR')

    def test_stdin_and_output_file(self):
        raw = (ROOT / 'examples/good_history.json').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'nested' / 'receipt.json'
            result = run('audit', '-', '-o', str(dest), input_text=raw)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(dest.read_text())['status'], 'COMPOSITION_VERIFIED')
            self.assertEqual(result.stdout, '')

    def test_audit_receipt_replay_and_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'receipt.json'
            original = run('audit', 'examples/bad_history.json', '-o', str(path))
            self.assertEqual(original.returncode, 1)
            replay = run('replay', 'examples/bad_history.json', str(path))
            # A valid negative receipt replays successfully without becoming an admission.
            self.assertEqual(replay.returncode, 0, replay.stderr)
            receipt = json.loads(path.read_text())
            receipt['status'] = 'COMPOSITION_VERIFIED'
            path.write_text(json.dumps(receipt))
            replay = run('replay', 'examples/bad_history.json', str(path))
            self.assertEqual(replay.returncode, 1)
            self.assertEqual(json.loads(replay.stdout)['status'], 'REPLAY_MISMATCH')

    def test_collision_certificate_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'collision.json'
            result = run('descent', 'examples/report_collision.json', '-o', str(path))
            self.assertEqual(result.returncode, 1)
            replay = run('replay', 'examples/report_collision.json', str(path))
            self.assertEqual(replay.returncode, 0, replay.stderr)

    def test_unknown_command_fails(self):
        result = run('admit-without-proof')
        self.assertEqual(result.returncode, 2)

    def test_duplicate_keys_rejected_at_parser_boundary(self):
        with self.assertRaises(ValidationError):
            loads_strict('{"report":false,"report":true}')

    def test_selftest_exits_zero(self):
        result = run('selftest')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['schema'], 'lggr.selftest.v1')
        self.assertEqual(data['status'], 'PASS')
        self.assertIn('streaming', data['modules_tested'])
        self.assertEqual(data['tests_passed'], len(data['modules_tested']))

    def test_selftest_with_output_file(self):
        with tempfile.TemporaryDirectory() as directory:
            out_file = Path(directory) / 'selftest_receipt.json'
            result = run('selftest', '-o', str(out_file))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '')
            self.assertTrue(out_file.exists())
            data = json.loads(out_file.read_text(encoding='utf-8'))
            self.assertEqual(data['schema'], 'lggr.selftest.v1')
            self.assertEqual(data['status'], 'PASS')

    def test_stream_help(self):
        result = run('stream', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--monitor', result.stdout)

    def test_stream_fiber_composable_exits_zero(self):
        lines = (
            '{"state_id": "s1", "report": "rep_1", "query": 1}\n'
            '{"state_id": "s2", "report": "rep_2", "query": 2}\n'
        )
        result = run('stream', '--monitor', 'fiber', '-', input_text=lines)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['schema'], 'lggr.stream.v1')
        self.assertEqual(data['status'], 'COMPOSABLE_LGGG')
        self.assertEqual(data['events_processed'], 2)
        self.assertEqual(data['final_receipt']['status'], 'DECODER_VERIFIED')

    def test_stream_fiber_collision_exits_nonzero(self):
        lines = (
            '{"state_id": "s1", "report": "rep_A", "query": 1}\n'
            '{"state_id": "s2", "report": "rep_A", "query": 2}\n'
        )
        result = run('stream', '--monitor', 'fiber', '-', input_text=lines)
        self.assertEqual(result.returncode, 1, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['schema'], 'lggr.stream.v1')
        self.assertEqual(data['status'], 'OBSTRUCTED_LGGR')
        self.assertEqual(data['final_receipt']['status'], 'REPORT_INSUFFICIENT')
        self.assertIsNotNone(data['final_receipt']['collision'])

    def test_stream_audit_composable_exits_zero(self):
        good_raw = json.loads((ROOT / 'examples/good_history.json').read_text(encoding='utf-8'))
        policy = good_raw['policy']
        baseline = good_raw['baseline']
        witnesses = good_raw['witnesses']
        lines = '\n'.join(json.dumps(w) for w in witnesses) + '\n'
        with tempfile.TemporaryDirectory() as directory:
            pol_path = Path(directory) / 'policy.json'
            base_path = Path(directory) / 'base.json'
            pol_path.write_text(json.dumps(policy), encoding='utf-8')
            base_path.write_text(json.dumps(baseline), encoding='utf-8')
            result = run('stream', '--monitor', 'audit', '--policy', str(pol_path),
                         '--baseline', str(base_path), '-', input_text=lines)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data['status'], 'COMPOSABLE_LGGG')
            self.assertEqual(data['final_receipt']['status'], 'COMPOSITION_VERIFIED')

    def test_stream_audit_alert_exits_nonzero(self):
        bad_raw = json.loads((ROOT / 'examples/bad_history.json').read_text(encoding='utf-8'))
        policy = bad_raw['policy']
        baseline = bad_raw['baseline']
        witnesses = bad_raw['witnesses']
        lines = '\n'.join(json.dumps(w) for w in witnesses) + '\n'
        with tempfile.TemporaryDirectory() as directory:
            pol_path = Path(directory) / 'policy.json'
            base_path = Path(directory) / 'base.json'
            pol_path.write_text(json.dumps(policy), encoding='utf-8')
            base_path.write_text(json.dumps(baseline), encoding='utf-8')
            result = run('stream', '--monitor', 'audit', '--policy', str(pol_path),
                         '--baseline', str(base_path), '-', input_text=lines)
            self.assertEqual(result.returncode, 1, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data['status'], 'OBSTRUCTED_LGGR')

    def test_stream_cochain_open_tree_exits_zero(self):
        lines = (
            '{"source": "0", "target": "1", "value": 1, "weight": 1}\n'
            '{"source": "1", "target": "2", "value": 1, "weight": 1}\n'
        )
        result = run('stream', '--monitor', 'cochain', '-', input_text=lines)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'COMPOSABLE_LGGG')
        self.assertEqual(data['final_receipt']['status'], 'OPEN_TREE')

    def test_stream_cochain_cycle_defect_exits_nonzero(self):
        lines = (
            '{"source": "0", "target": "1", "value": 1, "weight": 1}\n'
            '{"source": "1", "target": "2", "value": 1, "weight": 1}\n'
            '{"source": "0", "target": "2", "value": 1, "weight": 1}\n'
        )
        result = run('stream', '--monitor', 'cochain', '-', input_text=lines)
        self.assertEqual(result.returncode, 1, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'OBSTRUCTED_LGGR')
        self.assertEqual(data['final_receipt']['status'], 'OBSTRUCTED_CYCLE')
        self.assertEqual(data['final_receipt']['nonrepairable_cycles'], 1)
