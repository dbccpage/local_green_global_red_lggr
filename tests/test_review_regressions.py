"""Offline adversarial checks for PR47/50/51 review findings."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from typing import get_type_hints
import unittest
from unittest.mock import patch

from lggr.benchmarks import (OpenRouterClient, FrontierInputError, _run_frontier_traces_for_model,
                             run_frontier_monitors_benchmark, verify_frontier_benchmark)
from lggr.common import digest
from lggr.streaming import StreamingProductOfExpertsMonitor

ROOT = Path(__file__).resolve().parents[1]


def seal(value):
    value["receipt_sha256"] = digest({k: v for k, v in value.items() if k != "receipt_sha256"})


class Responses:
    def __init__(self, model, responses):
        self.model, self.responses, self.completion_count = model, iter(responses), 0
    def complete(self, prompt, **kwargs):
        self.completion_count += 1
        return next(self.responses)


class FrontierReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((ROOT / "receipts/live_benchmarks/frontier_monitors_benchmark.json").read_text())
        cls.model = cls.receipt["models_evaluated"][0]
        cls.responses = [c for t in cls.receipt["traces"][:10] for c in t["completions"]]

    def test_published_responses_regenerate_complete_receipts(self):
        result = verify_frontier_benchmark(self.receipt)
        self.assertEqual((result["trace_count"], result["completion_count"]), (50, 100))

    def test_hashes_and_recomputed_evidence_reject_tampering(self):
        for field in ("prompt", "response", "count", "model_count", "receipt_body", "parsed", "label", "model"):
            for reseal in (False, True):
                with self.subTest(field=field, reseal=reseal):
                    value = deepcopy(self.receipt)
                    tr = value["traces"][0]
                    if field == "prompt": tr["prompts"][0] = "nonsense"
                    elif field == "response": tr["completions"][0] = "nonsense"
                    elif field == "count": value["total_completions"] = 0
                    elif field == "model_count": value["per_model_metrics"][self.model]["completion_count"] = 0
                    elif field == "receipt_body": tr["monitor_receipt"]["status"] = "FORGED"
                    elif field == "parsed": tr["parsed_inputs"]["stages"][0]["candidate_x"] = 7
                    elif field == "label": tr["classification"] = "FORGED"
                    elif field == "model": tr["model"] = "other/model"
                    if reseal:
                        seal(tr["monitor_receipt"])
                        seal(value)
                    with self.assertRaises(ValueError): verify_frontier_benchmark(value)

    def test_malformed_output_never_becomes_a_green_trace(self):
        mutations = [(2, '{"modulus":2,"candidate_x":0.9}'), (2, '{"modulus":2,"candidate_x":true}'),
                     (2, '{"modulus":4,"candidate_x":0}'), (4, '{}'), (6, '{}'),
                     (8, '{"row_context_assignments":[[true,1,1],[1,1,1],[1,1,1]]}'),
                     (12, '{"s0_symbol":0.9,"s1_symbol":1}'), (16, '{"scores":[0.9,0,0]}'), (16, '{"scores":[-1,1,1]}'),
                     (0, '{"modulus":2,"candidate_x":1,"candidate_x":0}')]
        for index, response in mutations:
            with self.subTest(index=index, response=response):
                responses = self.responses.copy()
                responses[index] = response
                with self.assertRaises(FrontierInputError):
                    _run_frontier_traces_for_model(Responses(self.model, responses))

    def test_runner_records_malformed_responses_and_replays_them(self):
        responses = self.responses.copy()
        responses[6] = '{}'
        with tempfile.TemporaryDirectory() as directory, patch('lggr.benchmarks.OpenRouterClient',
                side_effect=lambda model, **kw: Responses(model, responses)):
            result = run_frontier_monitors_benchmark([self.model], directory)
        self.assertEqual(result["traces"], [])
        self.assertEqual(result["model_failures"][self.model]["status"], "MALFORMED_INPUT")
        self.assertEqual(result["model_failures"][self.model]["exchanges"][-1]["response"], '{}')
        self.assertEqual(result["total_completions"], 7)
        self.assertEqual(verify_frontier_benchmark(result)["malformed_models"], [self.model])

    def test_successful_v2_run_replays(self):
        with tempfile.TemporaryDirectory() as directory, patch('lggr.benchmarks.OpenRouterClient',
                side_effect=lambda model, **kw: Responses(model, self.responses)):
            result = run_frontier_monitors_benchmark([self.model], directory)
        self.assertEqual(verify_frontier_benchmark(result)["trace_count"], 10)

    def test_explicit_model_overrides_environment_default(self):
        with patch('lggr.benchmarks.load_openrouter_credentials', return_value=('mock', 'deepseek/deepseek-chat')):
            self.assertEqual(OpenRouterClient(model='openai/gpt-4o-mini').model, 'openai/gpt-4o-mini')
            self.assertEqual(OpenRouterClient().model, 'deepseek/deepseek-chat')
            self.assertEqual(OpenRouterClient(api_key='mock', model='openai/gpt-4o-mini').model, 'openai/gpt-4o-mini')

    def test_runner_rejects_mislabeled_client(self):
        with tempfile.TemporaryDirectory() as directory, patch('lggr.benchmarks.OpenRouterClient',
                return_value=Responses('wrong/model', self.responses)):
            with self.assertRaisesRegex(ValueError, 'configured model'):
                run_frontier_monitors_benchmark([self.model], directory)

    def test_public_poe_annotations_resolve(self):
        self.assertIn('expert_scores', get_type_hints(StreamingProductOfExpertsMonitor.record_expert_scores))
