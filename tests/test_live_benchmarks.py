"""Offline unit test suite replaying live swarm benchmarks and rate calculations.

Verifies live trace receipts in receipts/live_benchmarks/ completely offline
with zero network access.
AuthorityEffect: None. Replay and online evidence verification only.
"""
from __future__ import annotations

import ast
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any
import unittest

from lggr.benchmarks import (
    OpenRouterClient,
    compute_empirical_defect_rates,
    load_openrouter_credentials,
)
from lggr.common import digest
from lggr.streaming import (
    StreamingAuditMonitor,
    StreamingCochainMonitor,
    StreamingFiberMonitor,
)
from lggr.witnesses import BudgetPolicy, StateRef, StepWitness

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS_DIR = ROOT / "receipts" / "live_benchmarks"


class TestOpenRouterCredentialLoader(unittest.TestCase):
    """F08: Zero-dependency OpenRouter credential resolver tests."""

    def test_openrouter_keyword_and_env_resolution(self):
        """F08-1: Credential resolver handles OPENROUTER environment variables."""
        test_key = "sk-or-v1-mock-test-key-abcdef"
        test_model = "openai/gpt-4o-mini"
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            env_file.write_text(
                f"OPENROUTER_API_KEY={test_key}\nOPENROUTER_MODEL={test_model}\n",
                encoding="utf-8",
            )
            key, model = load_openrouter_credentials([str(env_file)])
            self.assertEqual(key, test_key)
            self.assertEqual(model, test_model)

    def test_openrouter_quote_and_comment_parsing(self):
        """F08-2 & F08-3: Parses quotes, whitespace, comments, and export prefix."""
        sample_env = (
            "# Top-level comment\n"
            "export OPENROUTER_API_KEY=\"sk-test-quoted-value\"\n"
            "OPENROUTER_MODEL='custom/test-model'\n"
            "IGNORED_LINE_WITHOUT_EQUALS\n"
            "# Trailing comment\n"
        )
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            env_file.write_text(sample_env, encoding="utf-8")
            key, model = load_openrouter_credentials([str(env_file)])
            self.assertEqual(key, "sk-test-quoted-value")
            self.assertEqual(model, "custom/test-model")

    def test_openrouter_missing_file_graceful(self):
        """F08-4: Nonexistent candidate paths return None without unhandled exception."""
        nonexistent = [r"C:\nonexistent_path_12345\.env"]
        orig_key = os.environ.pop("OPENROUTER_API_KEY", None)
        try:
            key, model = load_openrouter_credentials(nonexistent)
            self.assertIsNone(key)
            self.assertEqual(model, "openai/gpt-4o-mini")
        finally:
            if orig_key is not None:
                os.environ["OPENROUTER_API_KEY"] = orig_key

    def test_openrouter_client_budget_guard(self):
        """Ensures request counter guard raises exception if completion limit exceeded."""
        client = OpenRouterClient(api_key="mock_key", max_completions=2)
        client.completion_count = 2
        with self.assertRaises(RuntimeError) as ctx:
            client.complete("Test prompt")
        self.assertIn("Request budget limit reached", str(ctx.exception))
        # Ensure no key leakage in error
        self.assertNotIn("mock_key", str(ctx.exception))


class TestEmpiricalDefectRateComputation(unittest.TestCase):
    """F09: Empirical NGD, ZDR, PGD rate and partition identity calculations."""

    def test_empty_traces_rate_computation(self):
        """F09-1: Empty traces yield zero rates and safe partition identity."""
        metrics = compute_empirical_defect_rates([])
        self.assertEqual(metrics["N"], 0)
        self.assertEqual(metrics["NGD_rate"], "0")
        self.assertEqual(metrics["ZDR_rate"], "0")
        self.assertTrue(metrics["identity_verified"])

    def test_homogeneous_zdr_rates(self):
        """F09-2: Homogeneous ZDR traces yield 1.0 ZDR rate and 0.0 NGD rate."""
        traces = [
            {"local_pass": True, "global_pass": True, "defect": 0},
            {"local_pass": True, "global_pass": True, "defect": 0},
        ]
        metrics = compute_empirical_defect_rates(traces)
        self.assertEqual(metrics["ZDR_rate"], "1")
        self.assertEqual(metrics["NGD_rate"], "0")
        self.assertEqual(metrics["mean_defect"], "0")
        self.assertTrue(metrics["identity_verified"])

    def test_homogeneous_ngd_rates(self):
        """F09-3: Homogeneous NGD traces yield 1.0 NGD rate and -1.0 mean defect."""
        traces = [
            {"local_pass": True, "global_pass": False, "defect": -1},
            {"local_pass": True, "global_pass": False, "defect": -1},
        ]
        metrics = compute_empirical_defect_rates(traces)
        self.assertEqual(metrics["NGD_rate"], "1")
        self.assertEqual(metrics["mean_defect"], "-1")
        self.assertEqual(metrics["EGD_rate"], "-1")
        self.assertTrue(metrics["identity_verified"])

    def test_mixed_distribution_rates_and_identity(self):
        """F09-4 & F09-5: Mixed traces compute exact rational proportions and partition identity."""
        traces = [
            {"local_pass": True, "global_pass": False, "defect": -1},  # NGD
            {"local_pass": True, "global_pass": True, "defect": 0},   # ZDR
            {"local_pass": False, "global_pass": True, "defect": 1},  # PGD
            {"local_pass": False, "global_pass": False, "defect": 0}, # LRGR
        ]
        metrics = compute_empirical_defect_rates(traces)
        self.assertEqual(metrics["N"], 4)
        self.assertEqual(Fraction(metrics["NGD_rate"]), Fraction(1, 4))
        self.assertEqual(Fraction(metrics["ZDR_rate"]), Fraction(2, 4))
        self.assertEqual(Fraction(metrics["PGD_rate"]), Fraction(1, 4))
        self.assertEqual(Fraction(metrics["LRGR_rate"]), Fraction(1, 4))
        self.assertEqual(Fraction(metrics["LPR"]), Fraction(2, 4))
        self.assertEqual(Fraction(metrics["GPR"]), Fraction(2, 4))
        self.assertEqual(Fraction(metrics["EGD_rate"]), Fraction(0, 4))
        self.assertTrue(metrics["identity_verified"])


class TestOfflineTraceReplay(unittest.TestCase):
    """F10-F14: Deterministic offline replay of live benchmark receipts."""

    def test_f10_test1_fiber_collision_replay(self):
        """F10: Replay Test 1 fiber collision trace and verify online detection."""
        artifact = RECEIPTS_DIR / "test1_fiber_collision.json"
        if not artifact.is_file():
            self.skipTest("test1_fiber_collision.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.trace_replay.v1")
        self.assertEqual(data.get("final_status"), "OBSTRUCTED_LGGR")
        self.assertEqual(data.get("collision_step_index"), 1)
        self.assertIn("left", data.get("colliding_pair", {}))
        self.assertIn("right", data.get("colliding_pair", {}))

        # Independent offline replay verification through StreamingFiberMonitor
        mon = StreamingFiberMonitor(scope_id="offline_replay_test1")
        steps = data.get("steps", [])
        self.assertGreaterEqual(len(steps), 2)
        r0 = mon.observe("s1", report=steps[0]["report"], query=steps[0]["query"])
        self.assertEqual(r0["status"], "OK")
        self.assertFalse(mon.is_obstructed)

        r1 = mon.observe("s2", report=steps[1]["report"], query=steps[1]["query"])
        self.assertEqual(r1["status"], "REPORT_INSUFFICIENT")
        self.assertTrue(mon.is_obstructed)
        self.assertEqual(mon.status, "OBSTRUCTED_LGGR")

    def test_f11_test2_prefix_breach_replay(self):
        """F11: Replay Test 2 streaming prefix drift and verify mid-flight early stop."""
        artifact = RECEIPTS_DIR / "test2_prefix_breach.json"
        if not artifact.is_file():
            self.skipTest("test2_prefix_breach.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.trace_replay.v1")
        self.assertEqual(data.get("policy", {}).get("query_scope"), "every_prefix")
        self.assertEqual(data.get("alert_step_index"), 1)
        self.assertTrue(data.get("endpoint_would_pass"))

        alert_receipt = data.get("alert_receipt", {})
        self.assertIn("cumulative_delta", alert_receipt)
        self.assertIn("max_total", alert_receipt)
        self.assertGreater(alert_receipt["cumulative_delta"], alert_receipt["max_total"])

        # Independent offline replay through StreamingAuditMonitor
        pol = BudgetPolicy(
            allowed_states=tuple(range(-25, 25)),
            max_step=data["policy"]["max_step"],
            max_total=data["policy"]["max_total"],
            query_scope="every_prefix",
        )
        mon = StreamingAuditMonitor(policy=pol)
        witnesses_data = data.get("step_witnesses", [])

        # Step 1
        w1 = StepWitness(
            source=StateRef("s0", 0),
            target=StateRef("s1", witnesses_data[0]["delta"]),
            declared_magnitude=abs(witnesses_data[0]["delta"]),
            local_rule_accepts=True,
            smoke_test_passed=True,
            prior_obligations_satisfied=True,
            policy_hash=pol.sha256,
        )
        res1 = mon.step(w1)
        self.assertEqual(res1["status"], "OK")

        # Step 2: excursion causing breach
        w2 = StepWitness(
            source=StateRef("s1", witnesses_data[0]["delta"]),
            target=StateRef("s2", witnesses_data[1]["cumulative"]),
            declared_magnitude=abs(witnesses_data[1]["delta"]),
            local_rule_accepts=True,
            smoke_test_passed=True,
            prior_obligations_satisfied=True,
            policy_hash=pol.sha256,
        )
        res2 = mon.step(w2)
        self.assertEqual(res2["status"], "ALERT")
        self.assertEqual(mon.status, "OBSTRUCTED_LGGR")

    def test_f12_test3_cochain_cycle_replay(self):
        """F12: Replay Test 3 incremental 1-cochain cycle closure and L1 repair."""
        artifact = RECEIPTS_DIR / "test3_cochain_cycle.json"
        if not artifact.is_file():
            self.skipTest("test3_cochain_cycle.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.trace_replay.v1")
        edges = data.get("edges", [])
        self.assertEqual(len(edges), 3)
        self.assertEqual(data.get("cycle_closing_edge_index"), 2)
        self.assertNotEqual(data.get("closure_defect"), "0")
        self.assertIn("l1_repair_distance", data)
        self.assertIn("dual_witness", data)

        # Independent offline replay through StreamingCochainMonitor
        mon = StreamingCochainMonitor()
        r1 = mon.add_edge(edges[0]["source"], edges[0]["target"], Fraction(edges[0]["value"]))
        self.assertEqual(r1["status"], "OPEN_TREE")

        r2 = mon.add_edge(edges[1]["source"], edges[1]["target"], Fraction(edges[1]["value"]))
        self.assertEqual(r2["status"], "OPEN_TREE")

        r3 = mon.add_edge(edges[2]["source"], edges[2]["target"], Fraction(edges[2]["value"]))
        self.assertEqual(r3["status"], "CYCLE_CLOSED")
        self.assertEqual(str(r3["closure_defect"]), data["closure_defect"])
        self.assertEqual(str(r3["l1_repair_distance"]), data["l1_repair_distance"])

    def test_f13_test4_composable_lggg_replay(self):
        """F13: Replay Test 4 boundary-sufficient schema and composable LGGG certification."""
        artifact = RECEIPTS_DIR / "test4_composable_lggg.json"
        if not artifact.is_file():
            self.skipTest("test4_composable_lggg.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.trace_replay.v1")
        self.assertTrue(data.get("boundary_sufficient"))
        self.assertFalse(data.get("collision_detected"))
        self.assertEqual(data.get("max_evaluator_defect"), 0)
        self.assertEqual(data.get("final_status"), "COMPOSABLE_LGGG")

        # Independent offline replay through StreamingFiberMonitor
        mon = StreamingFiberMonitor(scope_id="offline_replay_test4")
        steps = data.get("steps", [])
        for step in steps:
            res = mon.observe(step["state_id"], report=step["report"], query=step["query"])
            self.assertEqual(res["status"], "OK")
        self.assertFalse(mon.is_obstructed)
        self.assertEqual(mon.status, "COMPOSABLE_LGGG")

    def test_empirical_ngd_benchmark_replay(self):
        """Replay empirical NGD benchmark traces and verify Volume I Section 9 metrics."""
        artifact = RECEIPTS_DIR / "empirical_ngd_benchmark.json"
        if not artifact.is_file():
            self.skipTest("empirical_ngd_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.trace_replay.v1")
        self.assertLessEqual(data.get("completion_count", 0), 40)
        metrics = data.get("metrics", {})
        self.assertTrue(metrics.get("identity_verified"))

        # Recompute metrics from stored traces
        traces = data.get("traces", [])
        self.assertGreater(len(traces), 0)
        recomputed = compute_empirical_defect_rates(traces)

        self.assertEqual(metrics["N"], recomputed["N"])
        self.assertEqual(metrics["LPR"], recomputed["LPR"])
        self.assertEqual(metrics["GPR"], recomputed["GPR"])
        self.assertEqual(metrics["NGD_rate"], recomputed["NGD_rate"])
        self.assertEqual(metrics["ZDR_rate"], recomputed["ZDR_rate"])
        self.assertEqual(metrics["PGD_rate"], recomputed["PGD_rate"])
        self.assertEqual(metrics["mean_defect"], recomputed["mean_defect"])
        self.assertEqual(metrics["EGD_rate"], recomputed["EGD_rate"])
        self.assertTrue(recomputed["identity_verified"])

        # Re-verify that at least one trace exhibits NGD (Delta_E = -1) or ZDR (Delta_E = 0)
        defects = [t["defect"] for t in traces]
        self.assertIn(0, defects, "Should contain ZDR traces")
        # Ensure classifications match defects
        for t in traces:
            expected_class = {-1: "NGD", 0: "ZDR", 1: "PGD"}[t["defect"]]
            self.assertEqual(t["classification"], expected_class)


if __name__ == "__main__":
    unittest.main()
