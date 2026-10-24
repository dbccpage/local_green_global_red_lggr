"""Offline adversarial checks for repair evidence, permitted edits and replay."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lggr import benchmarks as bench
from lggr.common import ValidationError, digest
from lggr.streaming import StreamingClosedLoopRepairMonitor

ROOT = Path(__file__).resolve().parent.parent


def seal(record):
    record["receipt_sha256"] = digest({k: v for k, v in record.items() if k != "receipt_sha256"})
    return record


class ClosedLoopValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads((ROOT / "receipts/live_benchmarks/closed_loop_repair_benchmark.json").read_text(encoding="utf-8"))
        cls.model = cls.published["models_evaluated"][0]
        cls.responses = [c for t in cls.published["trajectories"] if t["model_id"] == cls.model for c in t["completions"]]

    def run_fixture(self, replacements=None, *, models=None):
        responses = self.responses.copy()
        for index, response in (replacements or {}).items():
            responses[index] = response if isinstance(response, str) else json.dumps(response)

        class Client:
            def __init__(self, model, **kwargs):
                self.model, self.responses = model, iter(responses)
            def complete(self, prompt, **kwargs):
                return next(self.responses)

        with tempfile.TemporaryDirectory() as directory, patch.object(bench, "OpenRouterClient", Client):
            result = bench.run_closed_loop_repair_benchmark(models or [self.model], directory)
            saved = json.loads((Path(directory) / "closed_loop_repair_benchmark_v2.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, result)
            self.assertFalse((Path(directory) / "closed_loop_repair_benchmark.json").exists())
        return result

    def record(self, monitor, rounds):
        return monitor.record_trajectory("test", monitor_name="frontier", model_id="model", rounds=rounds)

    def test_boolean_fields_reject_coercion_and_missing_values(self):
        for field in ("local_pass", "global_pass"):
            for value in ("false", "true", 0, 1, None, [], {}):
                with self.subTest(field=field, value=value):
                    monitor = StreamingClosedLoopRepairMonitor()
                    rounds = deepcopy(self.published["trajectories"][0]["rounds"])
                    rounds[-1][field] = value
                    with self.assertRaises(ValidationError):
                        self.record(monitor, rounds)
                    self.assertEqual(monitor.trajectories, [])
            rounds = deepcopy(self.published["trajectories"][0]["rounds"])
            del rounds[-1][field]
            with self.assertRaises(ValidationError):
                self.record(StreamingClosedLoopRepairMonitor(), rounds)

    def test_contract_status_must_match_both_verdicts(self):
        for local, global_ in ((True, True), (True, False), (False, True), (False, False)):
            rounds = deepcopy(self.published["trajectories"][0]["rounds"])
            rounds[-1].update(local_pass=local, global_pass=global_,
                              contract_status="COMPOSABLE_LGGG" if local and global_ else "OBSTRUCTED_LGGR")
            monitor = StreamingClosedLoopRepairMonitor()
            result = self.record(monitor, rounds)
            self.assertEqual(result["converged_multi_round"], local and global_)
            rounds[-1]["contract_status"] = "OBSTRUCTED_LGGR" if local and global_ else "COMPOSABLE_LGGG"
            with self.assertRaises(ValidationError):
                self.record(monitor, rounds)
            self.assertEqual(len(monitor.trajectories), 1)

    def test_published_replay_reports_historical_exceptions(self):
        result = bench.verify_closed_loop_repair_benchmark(self.published)
        self.assertEqual((result["trajectory_count"], result["completion_count"]), (25, 50))
        self.assertEqual((result["single_round_success_count"], result["final_round_success_count"]), (15, 25))
        self.assertEqual([x["handling"] for x in result["legacy_noncanonical_responses"]],
                         ["extracted_embedded_json", "substituted_fallback_inputs"])

    def test_balanced_rehashed_labels_cannot_override_frontier_receipts(self):
        data = deepcopy(self.published)
        failed = next(t for t in data["trajectories"] if t["monitor_name"] == "StreamingProjectiveTowerMonitor" and not t["rounds"][1]["global_pass"])
        passed = next(t for t in data["trajectories"] if t["rounds"][1]["global_pass"])
        failed["rounds"][1].update(local_pass=True, global_pass=True, contract_status="COMPOSABLE_LGGG")
        passed["rounds"][1].update(local_pass=True, global_pass=False, contract_status="OBSTRUCTED_LGGR")
        monitor = StreamingClosedLoopRepairMonitor(scope_id="live_closed_loop_frontier_repair")
        for trajectory in data["trajectories"]:
            trajectory.update(monitor.record_trajectory(trajectory["trajectory_id"], monitor_name=trajectory["monitor_name"],
                                                       model_id=trajectory["model_id"], rounds=trajectory["rounds"]))
        forged = seal(bench._closed_loop_benchmark_body(data["models_evaluated"], data["trajectories"], 50, monitor.get_receipt()))
        self.assertEqual(forged["single_round_convergence_rate"], self.published["single_round_convergence_rate"])
        with self.assertRaisesRegex(ValueError, "trajectories differ"):
            bench.verify_closed_loop_repair_benchmark(forged)

    def test_rehashed_raw_response_prompt_and_input_tampering_rejected(self):
        for target in ("completions", "prompts", "round_inputs"):
            with self.subTest(target=target):
                data = deepcopy(self.published)
                data["trajectories"][0][target][0] = "nonsense" if target != "round_inputs" else {"const_b": 6}
                with self.assertRaises(ValueError):
                    bench.verify_closed_loop_repair_benchmark(seal(data))

    def test_unrecognized_legacy_fallback_is_rejected(self):
        data = deepcopy(self.published)
        trajectory = next(t for t in data["trajectories"] if t["model_id"].startswith("meta-llama/") and t["monitor_name"] == "StreamingProductOfExpertsMonitor")
        trajectory["completions"][0] = "arbitrary substituted text"
        with self.assertRaisesRegex(ValueError, "unrecognized historical"):
            bench.verify_closed_loop_repair_benchmark(seal(data))

    def test_every_summary_and_both_hash_layers_are_verified(self):
        for field in ("total_completions", "trajectory_count", "single_round_convergence_rate", "meaning"):
            data = deepcopy(self.published)
            data[field] = "tampered"
            with self.subTest(field=field), self.assertRaises(ValueError):
                bench.verify_closed_loop_repair_benchmark(seal(data))
        data = deepcopy(self.published)
        data["receipt_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            bench.verify_closed_loop_repair_benchmark(data)
        for reseal_nested in (False, True):
            for nested in ("aggregate", "frontier"):
                data = deepcopy(self.published)
                receipt = data["closed_loop_monitor_receipt"] if nested == "aggregate" else data["trajectories"][0]["round_receipts"][1]
                receipt["status"] = "altered"
                if reseal_nested:
                    seal(receipt)
                with self.subTest(nested=nested, reseal=reseal_nested), self.assertRaises(ValueError):
                    bench.verify_closed_loop_repair_benchmark(seal(data))

    def test_strict_v2_roundtrip(self):
        result = self.run_fixture()
        replay = bench.verify_closed_loop_repair_benchmark(result)
        self.assertEqual((replay["trajectory_count"], replay["completion_count"]), (5, 10))
        self.assertEqual(replay["final_round_success_count"], 5)
        self.assertEqual(result["validation_status"], "COMPLETE")
        self.assertEqual(replay["legacy_noncanonical_responses"], [])

    def test_green_frontier_does_not_waive_permitted_edit(self):
        cases = [
            (1, {"const_b": 6, "x_mod2": 0, "x_mod4": 2}, "smallest_permitted_shift"),
            (5, {"col_targets": [-1, -1, 1], "global_grid": [[-1, -1, 1], [1, 1, 1], [1, 1, 1]]}, "exactly_one_column_flip"),
            (7, {"channel_capacity_s": 5, "symbols": [0, 1, 2, 3]}, "minimum_capacity"),
            (9, {"expert_scores": [[1, 1, 1], [1, 1, 1]]}, "normalized_rows"),
            (9, {"expert_scores": [["1/2", "1/2", "0"], ["0", "1/2", "1/2"]]}, "quarter_mass_transfer"),
        ]
        for index, response, check in cases:
            with self.subTest(check=check):
                result = self.run_fixture({index: response})
                trajectory = result["trajectories"][index // 2]
                self.assertTrue(trajectory["frontier_rounds"][2]["local_pass"])
                self.assertTrue(trajectory["frontier_rounds"][2]["global_pass"])
                self.assertFalse(trajectory["repair_constraints"][2][check])
                self.assertFalse(trajectory["converged_multi_round"])
                self.assertEqual(trajectory["contract_status"], "OBSTRUCTED_LGGR")
                self.assertTrue(bench.verify_closed_loop_repair_benchmark(result)["replayed"])

    def test_round_one_constraints_also_apply(self):
        result = self.run_fixture({0: {"const_b": 6, "x_mod2": 0, "x_mod4": 2}})
        trajectory = result["trajectories"][0]
        self.assertTrue(trajectory["frontier_rounds"][1]["global_pass"])
        self.assertFalse(trajectory["converged_single_round"])
        self.assertTrue(trajectory["converged_multi_round"])
        self.assertTrue(bench.verify_closed_loop_repair_benchmark(result)["replayed"])

    def test_rehashed_v2_constraint_and_summary_tampering_rejected(self):
        result = self.run_fixture({7: {"channel_capacity_s": 5, "symbols": [0, 1, 2, 3]}})
        for field in ("repair_constraints", "frontier_rounds", "converged_multi_round"):
            data = deepcopy(result)
            data["trajectories"][3][field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                bench.verify_closed_loop_repair_benchmark(seal(data))

    def test_malformed_responses_are_retained_without_certified_fallback(self):
        for response in ("{}", "nonsense", '{"const_b":3,"x_mod2":0.9,"x_mod4":3}',
                         '{"const_b":3,"x_mod2":true,"x_mod4":3}',
                         '{"const_b":3,"const_b":6,"x_mod2":1,"x_mod4":3}'):
            with self.subTest(response=response):
                result = self.run_fixture({0: response})
                self.assertEqual(result["trajectories"], [])
                self.assertIsNone(result["closed_loop_monitor_receipt"])
                self.assertEqual(result["validation_status"], "INCOMPLETE_MALFORMED_INPUT")
                self.assertEqual(result["model_failures"][self.model]["exchanges"][0]["response"], response)
                replay = bench.verify_closed_loop_repair_benchmark(result)
                self.assertEqual(replay["completion_count"], 1)
                self.assertEqual(replay["malformed_models"], [self.model])

    def test_late_malformed_response_does_not_leave_partial_aggregate(self):
        result = self.run_fixture({8: '{"expert_scores": [["3/4", "1/4", "0"], ["0", "1/4", "3/4"]]"}'})
        self.assertEqual(result["trajectories"], [])
        self.assertEqual(result["total_completions"], 9)
        self.assertIsNone(result["closed_loop_monitor_receipt"])
        self.assertTrue(bench.verify_closed_loop_repair_benchmark(result)["replayed"])

    def test_model_identity_mismatch_rejected(self):
        class Client:
            model = "other/model"
        with self.assertRaisesRegex(ValueError, "configured model differs"):
            bench._ClosedLoopClient(Client(), self.model)


if __name__ == "__main__":
    unittest.main()
