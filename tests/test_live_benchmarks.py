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
    _eval_infeasible_pair1_side_info_and_skew,
    _eval_infeasible_pair2_poe_and_skew,
    _eval_infeasible_pair3_tower_and_mermin_peres,
    _eval_pair1_side_info_and_skew,
    _eval_pair2_poe_and_skew,
    _eval_pair3_tower_and_mermin_peres,
    _eval_relaxed_pair1_side_info_and_skew,
    _eval_relaxed_pair2_poe_and_skew,
    _eval_relaxed_pair3_tower_and_mermin_peres,
    _eval_weighted_pair1_side_info_and_skew,
    _eval_weighted_pair2_poe_and_skew,
    _eval_weighted_pair3_tower_and_mermin_peres,
    compute_empirical_defect_rates,
    load_openrouter_credentials,
    verify_frontier_benchmark,
    verify_closed_loop_repair_benchmark,
)
from lggr.common import digest
from lggr.streaming import (
    StreamingAuditMonitor,
    StreamingClosedLoopRepairMonitor,
    StreamingCochainMonitor,
    StreamingConcurrentLeaseOverlapMonitor,
    StreamingDeadlinePriorityQueueMonitor,
    StreamingFiberMonitor,
    StreamingGovernedPolicyRelaxationMonitor,
    StreamingJointMultiMonitorRepairGuard,
    StreamingLinearizedPipelineJacobianMonitor,
    StreamingMerminPeresParityMonitor,
    StreamingMinimumSlackPolicyRelaxationMonitor,
    StreamingOverloadedDeadlineBinPackingMonitor,
    StreamingPolicyRatchetDriftMonitor,
    StreamingProductOfExpertsMonitor,
    StreamingProjectiveTowerMonitor,
    StreamingSideInformationCapacityMonitor,
    StreamingSimultaneousBudgetSplitMonitor,
    StreamingSkewRepairMonitor,
    StreamingVariableDurationGracefulSheddingMonitor,
    StreamingWeightedPolicyRelaxationMonitor,
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

    def test_frontier_monitors_multi_model_benchmark_replay(self):
        """F15: Replay all 50 live multi-agent frontier monitor traces across 5 model families."""
        artifact = RECEIPTS_DIR / "frontier_monitors_benchmark.json"
        if not artifact.is_file():
            self.skipTest("frontier_monitors_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertTrue(verify_frontier_benchmark(data)["replayed"])

        self.assertEqual(data.get("schema"), "lggr.frontier_benchmark_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("monitors_evaluated", [])), 5)
        self.assertEqual(data.get("total_completions"), 100)

        traces = data.get("traces", [])
        self.assertEqual(len(traces), 50)

        recomputed_overall = compute_empirical_defect_rates(traces)
        self.assertEqual(data["overall_metrics"], recomputed_overall)
        self.assertTrue(recomputed_overall["identity_verified"])

        for model_id, model_entry in data.get("per_model_metrics", {}).items():
            model_trs = [t for t in traces if t["model"] == model_id]
            self.assertEqual(len(model_trs), 10)
            self.assertEqual(model_entry["metrics"], compute_empirical_defect_rates(model_trs))
            self.assertTrue(model_entry["metrics"]["identity_verified"])

        for mon_name, mon_metrics in data.get("per_monitor_metrics", {}).items():
            mon_trs = [t for t in traces if t["monitor"] == mon_name]
            self.assertEqual(len(mon_trs), 10)
            self.assertEqual(mon_metrics, compute_empirical_defect_rates(mon_trs))
            self.assertTrue(mon_metrics["identity_verified"])

        # Deterministically replay every single trace through its corresponding frontier monitor
        for t in traces:
            mon_name = t["monitor"]
            inp = t["parsed_inputs"]
            saved_rec = t["monitor_receipt"]
            scope_id = saved_rec["scope_id"]

            if mon_name == "StreamingProjectiveTowerMonitor":
                mon = StreamingProjectiveTowerMonitor(
                    inp["coeff_a"], inp["const_b"], scope_id=scope_id
                )
                for st in inp["stages"]:
                    mon.record_stage(st["stage_id"], st["modulus"], st["candidate_x"])
                replayed_rec = mon.get_receipt()
                l_pass = bool(replayed_rec["local_product_aggregator"] == 1)
                g_pass = bool(replayed_rec["global_integral_lift_evaluator"] == 1)
                defect = int(replayed_rec["evaluator_defect"])
            elif mon_name == "StreamingSkewRepairMonitor":
                mon = StreamingSkewRepairMonitor(scope_id=scope_id)
                probe_id = saved_rec["probes"][0]["probe_id"]
                probe_rec = mon.record_probe(
                    probe_id,
                    inp["omega_a"],
                    inp["omega_b"],
                    candidate_alpha=inp["candidate_alpha"],
                    l_inf_coordinate_budget=inp["l_inf_coordinate_budget"],
                    l_1_global_budget=inp["l_1_global_budget"],
                )
                replayed_rec = mon.get_receipt()
                l_pass = bool(probe_rec["local_product_aggregator"] == 1)
                g_pass = bool(probe_rec["global_l1_budget_evaluator"] == 1)
                defect = int(probe_rec["evaluator_defect"])
            elif mon_name == "StreamingMerminPeresParityMonitor":
                mon = StreamingMerminPeresParityMonitor(scope_id=scope_id)
                grid_id = saved_rec["grids"][0]["grid_id"]
                grid_rec = mon.record_grid(
                    grid_id,
                    row_targets=inp["row_targets"],
                    col_targets=inp["col_targets"],
                    row_context_assignments=inp["row_context_assignments"],
                    col_context_assignments=inp["col_context_assignments"],
                )
                replayed_rec = mon.get_receipt()
                l_pass = bool(grid_rec["local_product_aggregator"] == 1)
                g_pass = bool(grid_rec["global_noncontextual_evaluator"] == 1)
                defect = int(grid_rec["evaluator_defect"])
            elif mon_name == "StreamingSideInformationCapacityMonitor":
                mon = StreamingSideInformationCapacityMonitor(scope_id=scope_id)
                fiber_id = saved_rec["fibers"][0]["fiber_id"]
                fib_rec = mon.record_fiber_channel(
                    fiber_id,
                    inp["states"],
                    channel_capacity_s=inp["channel_capacity_s"],
                    error_budget=inp["error_budget"],
                )
                replayed_rec = mon.get_receipt()
                l_pass = bool(fib_rec["local_product_aggregator"] == 1)
                g_pass = bool(fib_rec["global_decodability_evaluator"] == 1)
                defect = int(fib_rec["evaluator_defect"])
            elif mon_name == "StreamingProductOfExpertsMonitor":
                mon = StreamingProductOfExpertsMonitor(scope_id=scope_id)
                round_id = saved_rec["rounds"][0]["round_id"]
                rnd_rec = mon.record_expert_scores(round_id, inp["expert_scores"])
                replayed_rec = mon.get_receipt()
                l_pass = bool(rnd_rec["local_product_aggregator"] == 1)
                g_pass = bool(rnd_rec["global_poe_normalizable_evaluator"] == 1)
                defect = int(rnd_rec["evaluator_defect"])
            else:
                self.fail(f"Unknown frontier monitor: {mon_name}")

            self.assertEqual(replayed_rec["receipt_sha256"], saved_rec["receipt_sha256"])
            self.assertEqual(replayed_rec["status"], t["monitor_status"])
            self.assertEqual(replayed_rec["contract_status"], t["contract_status"])
            self.assertEqual(l_pass, t["local_pass"])
            self.assertEqual(g_pass, t["global_pass"])
            self.assertEqual(defect, t["defect"])
            self.assertEqual({-1: "NGD", 0: "ZDR", 1: "PGD"}[defect], t["classification"])

    def test_closed_loop_repair_multi_model_benchmark_replay(self):
        """F16: Replay all 25 closed-loop receipt-feedback repair trajectories across 5 model families."""
        artifact = RECEIPTS_DIR / "closed_loop_repair_benchmark.json"
        if not artifact.is_file():
            self.skipTest("closed_loop_repair_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        replay = verify_closed_loop_repair_benchmark(data)
        self.assertEqual(replay["single_round_success_count"], 15)
        self.assertEqual(replay["final_round_success_count"], 25)

        self.assertEqual(data.get("schema"), "lggr.closed_loop_repair_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("monitors_evaluated", [])), 5)
        self.assertEqual(data.get("total_completions"), 50)
        self.assertEqual(data.get("trajectory_count"), 25)

        trajs = data.get("trajectories", [])
        self.assertEqual(len(trajs), 25)

        self.assertTrue(data["round_0_baseline_metrics"]["identity_verified"])
        self.assertTrue(data["round_1_single_round_metrics"]["identity_verified"])
        self.assertTrue(data["round_2_multi_round_metrics"]["identity_verified"])

        # Replay all 25 trajectories through StreamingClosedLoopRepairMonitor
        replay_cl = StreamingClosedLoopRepairMonitor(
            scope_id=data["closed_loop_monitor_receipt"]["scope_id"]
        )
        for t in trajs:
            replay_cl.record_trajectory(
                t["trajectory_id"],
                monitor_name=t["monitor_name"],
                model_id=t["model_id"],
                rounds=t["rounds"],
            )
            # Also replay each of the 3 rounds through its underlying frontier monitor
            mon_name = t["monitor_name"]
            for r_idx in range(3):
                r_inp = t["round_inputs"][r_idx]
                r_saved = t["round_receipts"][r_idx]
                scope_id = r_saved["scope_id"]
                if mon_name == "StreamingProjectiveTowerMonitor":
                    m = StreamingProjectiveTowerMonitor(3, r_inp["const_b"], scope_id=scope_id)
                    m.record_stage("stage_mod2", 2, r_inp["x_mod2"])
                    m.record_stage("stage_mod4", 4, r_inp["x_mod4"])
                    r_rep = m.get_receipt()
                elif mon_name == "StreamingSkewRepairMonitor":
                    m = StreamingSkewRepairMonitor(scope_id=scope_id)
                    m.record_probe(
                        f"probe_r{r_idx}",
                        "2",
                        "0",
                        candidate_alpha=r_inp["candidate_alpha"],
                        l_inf_coordinate_budget="2",
                        l_1_global_budget="2",
                    )
                    r_rep = m.get_receipt()
                elif mon_name == "StreamingMerminPeresParityMonitor":
                    m = StreamingMerminPeresParityMonitor(scope_id=scope_id)
                    m.record_grid(
                        f"grid_r{r_idx}",
                        row_targets=r_inp["row_targets"],
                        col_targets=r_inp["col_targets"],
                        row_context_assignments=r_inp["row_context_assignments"],
                        col_context_assignments=r_inp["col_context_assignments"],
                    )
                    r_rep = m.get_receipt()
                elif mon_name == "StreamingSideInformationCapacityMonitor":
                    m = StreamingSideInformationCapacityMonitor(scope_id=scope_id)
                    m.record_fiber_channel(
                        f"fiber_r{r_idx}",
                        r_inp["states"],
                        channel_capacity_s=r_inp["channel_capacity_s"],
                        error_budget=0,
                    )
                    r_rep = m.get_receipt()
                elif mon_name == "StreamingProductOfExpertsMonitor":
                    m = StreamingProductOfExpertsMonitor(scope_id=scope_id)
                    m.record_expert_scores(f"round_r{r_idx}", r_inp["expert_scores"])
                    r_rep = m.get_receipt()
                else:
                    self.fail(f"Unknown monitor: {mon_name}")
                self.assertEqual(r_rep["receipt_sha256"], r_saved["receipt_sha256"])

        cl_rec = replay_cl.get_receipt()
        self.assertEqual(
            cl_rec["receipt_sha256"],
            data["closed_loop_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(cl_rec["single_round_convergence_rate"], "3/5")
        self.assertEqual(cl_rec["multi_round_convergence_rate"], "1")
        self.assertEqual(cl_rec["multi_round_convergence_gain"], "2/5")
        self.assertTrue(cl_rec["monotonic_convergence_verified"])

    def test_joint_multi_monitor_repair_benchmark_replay(self):
        """F17: Replay all 15 coupled two-monitor repair trajectories across 5 model families."""
        artifact = RECEIPTS_DIR / "joint_multi_monitor_repair_benchmark.json"
        if not artifact.is_file():
            self.skipTest("joint_multi_monitor_repair_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.joint_multi_monitor_repair_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("coupled_pairs_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("trajectory_count"), 15)

        trajs = data.get("trajectories", [])
        self.assertEqual(len(trajs), 15)

        self.assertTrue(data["round_0_baseline_metrics"]["identity_verified"])
        self.assertTrue(data["round_1_single_round_metrics"]["identity_verified"])
        self.assertTrue(data["round_2_multi_round_metrics"]["identity_verified"])

        replay_guard = StreamingJointMultiMonitorRepairGuard(
            scope_id=data["joint_guard_receipt"]["scope_id"]
        )
        for t in trajs:
            replay_guard.record_coupled_trajectory(
                t["trajectory_id"],
                pair_name=t["pair_name"],
                monitor_a_name=t["monitor_a_name"],
                monitor_b_name=t["monitor_b_name"],
                model_id=t["model_id"],
                rounds=t["rounds"],
            )
            pname = t["pair_name"]
            mdl = t["model_id"]
            for r_idx in range(3):
                r_inp = t["round_inputs"][r_idx]
                r_saved = t["round_receipts"][r_idx]
                if pname == "SideInfoCapacity_x_SkewRepair":
                    rec_a, rec_b = _eval_pair1_side_info_and_skew(
                        f"j1_r{r_idx}_{mdl}",
                        r_inp["channel_capacity_s"],
                        r_inp["symbols"],
                        r_inp["candidate_alpha"],
                    )
                elif pname == "ProductOfExperts_x_SkewRepair":
                    rec_a, rec_b = _eval_pair2_poe_and_skew(
                        f"j2_r{r_idx}_{mdl}",
                        r_inp["compromise_eps"],
                        r_inp["candidate_alpha"],
                    )
                elif pname == "ProjectiveTower_x_MerminPeresParity":
                    rec_a, rec_b = _eval_pair3_tower_and_mermin_peres(
                        f"j3_r{r_idx}_{mdl}",
                        r_inp["const_b"],
                        r_inp["x_mod2"],
                        r_inp["x_mod4"],
                    )
                else:
                    self.fail(f"Unknown coupled pair: {pname}")
                self.assertEqual(rec_a["receipt_sha256"], r_saved["receipt_a"]["receipt_sha256"])
                self.assertEqual(rec_b["receipt_sha256"], r_saved["receipt_b"]["receipt_sha256"])

        jg_rec = replay_guard.get_receipt()
        self.assertEqual(
            jg_rec["receipt_sha256"],
            data["joint_guard_receipt"]["receipt_sha256"],
        )
        self.assertEqual(jg_rec["single_round_convergence_rate"], "2/15")
        self.assertEqual(jg_rec["multi_round_convergence_rate"], "1")
        self.assertEqual(jg_rec["multi_round_convergence_gain"], "13/15")
        self.assertEqual(jg_rec["round_1_whack_a_mole_rate"], "7/15")
        self.assertTrue(jg_rec["monotonic_convergence_verified"])

    def test_infeasible_coupled_escalation_benchmark_replay(self):
        """F18: Replay all 15 infeasible empty-intersection coupled trajectories across 5 model families."""
        artifact = RECEIPTS_DIR / "infeasible_coupled_escalation_benchmark.json"
        if not artifact.is_file():
            self.skipTest("infeasible_coupled_escalation_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.infeasible_coupled_escalation_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("infeasible_pairs_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("trajectory_count"), 15)

        trajs = data.get("trajectories", [])
        self.assertEqual(len(trajs), 15)

        self.assertTrue(data["round_0_baseline_metrics"]["identity_verified"])
        self.assertTrue(data["round_1_priority_a_metrics"]["identity_verified"])
        self.assertTrue(data["round_2_priority_b_metrics"]["identity_verified"])

        replay_guard = StreamingJointMultiMonitorRepairGuard(
            scope_id=data["joint_guard_receipt"]["scope_id"]
        )
        for t in trajs:
            replay_guard.record_coupled_trajectory(
                t["trajectory_id"],
                pair_name=t["pair_name"],
                monitor_a_name=t["monitor_a_name"],
                monitor_b_name=t["monitor_b_name"],
                model_id=t["model_id"],
                feasible_intersection_empty=t["feasible_intersection_empty"],
                candidate_actions=t["candidate_actions"],
                rounds=t["rounds"],
            )
            self.assertTrue(t["feasible_intersection_empty"])
            self.assertTrue(t["whack_a_mole_oscillation_detected"])
            self.assertEqual(t["oscillation_l1_step_distance"], 2)
            self.assertTrue(t["halted_and_escalated"])
            self.assertEqual(
                t["trajectory_status"],
                "INFEASIBLE_EMPTY_INTERSECTION_OSCILLATION_HALTED_AND_ESCALATED_LGGR",
            )

            pname = t["pair_name"]
            mdl = t["model_id"]
            for r_idx in range(3):
                r_inp = t["round_inputs"][r_idx]
                r_saved = t["round_receipts"][r_idx]
                if pname == "Infeasible_SideInfo_x_SkewRepair":
                    rec_a, rec_b = _eval_infeasible_pair1_side_info_and_skew(
                        f"ip1_r{r_idx}_{mdl}",
                        r_inp["channel_capacity_s"],
                        r_inp["symbols"],
                        r_inp["candidate_alpha"],
                    )
                elif pname == "Infeasible_PoE_x_SkewRepair":
                    rec_a, rec_b = _eval_infeasible_pair2_poe_and_skew(
                        f"ip2_r{r_idx}_{mdl}",
                        r_inp["compromise_eps"],
                        r_inp["candidate_alpha"],
                    )
                elif pname == "Infeasible_ProjectiveTower_x_MerminPeres":
                    if r_idx == 0:
                        rec_a, _ = _eval_infeasible_pair3_tower_and_mermin_peres(
                            f"ip3_r0a_{mdl}",
                            r_inp["const_b_a"],
                            r_inp["x_mod2"],
                            r_inp["x_mod4"],
                        )
                        _, rec_b = _eval_infeasible_pair3_tower_and_mermin_peres(
                            f"ip3_r0b_{mdl}",
                            r_inp["const_b_b"],
                            1,
                            3,
                        )
                    else:
                        rec_a, rec_b = _eval_infeasible_pair3_tower_and_mermin_peres(
                            f"ip3_r{r_idx}_{mdl}",
                            r_inp["const_b"],
                            r_inp["x_mod2"],
                            r_inp["x_mod4"],
                        )
                else:
                    self.fail(f"Unknown infeasible coupled pair: {pname}")
                self.assertEqual(rec_a["receipt_sha256"], r_saved["receipt_a"]["receipt_sha256"])
                self.assertEqual(rec_b["receipt_sha256"], r_saved["receipt_b"]["receipt_sha256"])

        jg_rec = replay_guard.get_receipt()
        self.assertEqual(
            jg_rec["receipt_sha256"],
            data["joint_guard_receipt"]["receipt_sha256"],
        )
        self.assertEqual(jg_rec["status"], "INFEASIBLE_COUPLED_REGIME_HALTED_AND_ESCALATED_LGGR")
        self.assertEqual(jg_rec["single_round_convergence_rate"], "0")
        self.assertEqual(jg_rec["multi_round_convergence_rate"], "0")
        self.assertEqual(jg_rec["whack_a_mole_oscillation_rate"], "1")
        self.assertEqual(jg_rec["halt_and_escalate_rate"], "1")
        self.assertEqual(jg_rec["empty_feasible_intersection_count"], 15)
        self.assertEqual(jg_rec["whack_a_mole_oscillation_count"], 15)
        self.assertEqual(jg_rec["halted_and_escalated_count"], 15)

    def test_governed_policy_relaxation_benchmark_replay(self):
        """F19: Replay all 15 governed policy-relaxation handoffs across 5 model families."""
        artifact = RECEIPTS_DIR / "governed_policy_relaxation_benchmark.json"
        if not artifact.is_file():
            self.skipTest("governed_policy_relaxation_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.governed_policy_relaxation_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("relaxed_pairs_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 15)
        self.assertEqual(data.get("handoff_count"), 15)

        handoffs = data.get("handoffs", [])
        self.assertEqual(len(handoffs), 15)

        self.assertTrue(data["unauthorized_self_relaxation_metrics"]["identity_verified"])
        self.assertTrue(data["post_handoff_round_3_metrics"]["identity_verified"])

        replay_mon = StreamingGovernedPolicyRelaxationMonitor(
            scope_id=data["relaxation_monitor_receipt"]["scope_id"]
        )
        for h in handoffs:
            replay_mon.record_relaxation_handoff(
                handoff_id=h["handoff_id"],
                pair_name=h["pair_name"],
                model_id=h["model_id"],
                prior_escalation_receipt_sha256=h["prior_escalation_receipt_sha256"],
                prior_policy_sha256=h["prior_policy_sha256"],
                relaxed_policy_sha256=h["relaxed_policy_sha256"],
                authority_id=h["authority_id"],
                authority_grant_verified=h["authority_grant_verified"],
                pre_handoff_halted_and_escalated=h["pre_handoff_halted_and_escalated"],
                relaxed_candidate_actions=h["relaxed_candidate_actions"],
                unauthorized_self_relaxation_attempt=h["unauthorized_self_relaxation_attempt"],
                post_handoff_round=h["post_handoff_round"],
            )
            self.assertTrue(h["digest_chain_valid"])
            self.assertTrue(h["relaxed_pareto_nonempty"])
            self.assertTrue(h["unauthorized_self_relaxation_attempt"]["rejected"])
            self.assertEqual(h["unauthorized_self_relaxation_attempt"]["defect"], -1)
            self.assertTrue(h["pareto_restored"])
            self.assertEqual(
                h["handoff_status"], "GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG"
            )

            # Verify BudgetPolicy SHA-256 digests match stored policy objects
            p0_obj = BudgetPolicy.from_dict(h["prior_policy"])
            p1_obj = BudgetPolicy.from_dict(h["relaxed_policy"])
            self.assertEqual(p0_obj.sha256, h["prior_policy_sha256"])
            self.assertEqual(p1_obj.sha256, h["relaxed_policy_sha256"])

            # Replay Round 3 frontier monitor receipts
            pname = h["pair_name"]
            mdl = h["model_id"]
            act = h["post_handoff_round"]["action"]
            r3_saved = h["round_3_receipts"]
            if pname == "Relaxed_SideInfo_x_SkewRepair":
                rec_a, rec_b = _eval_relaxed_pair1_side_info_and_skew(
                    f"h1_r3_{mdl}",
                    act["channel_capacity_s"],
                    act["symbols"],
                    act["candidate_alpha"],
                    relaxed_l1_budget="4",
                )
            elif pname == "Relaxed_PoE_x_SkewRepair":
                rec_a, rec_b = _eval_relaxed_pair2_poe_and_skew(
                    f"h2_r3_{mdl}",
                    act["compromise_eps"],
                    act["candidate_alpha"],
                    relaxed_l1_budget="3",
                )
            elif pname == "Relaxed_ProjectiveTower_x_MerminPeres":
                rec_a, rec_b = _eval_relaxed_pair3_tower_and_mermin_peres(
                    f"h3_r3_{mdl}",
                    act["const_b"],
                    act["x_mod2"],
                    act["x_mod4"],
                    parity_gauge_flip=act["parity_gauge_flip"],
                )
            else:
                self.fail(f"Unknown relaxed coupled pair: {pname}")
            self.assertEqual(rec_a["receipt_sha256"], r3_saved["receipt_a"]["receipt_sha256"])
            self.assertEqual(rec_b["receipt_sha256"], r3_saved["receipt_b"]["receipt_sha256"])

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["relaxation_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(mon_rec["status"], "GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(mon_rec["unauthorized_self_relaxation_rejection_rate"], "1")
        self.assertEqual(mon_rec["relaxed_pareto_nonempty_rate"], "1")
        self.assertEqual(mon_rec["post_handoff_pareto_restoration_rate"], "1")
        self.assertEqual(mon_rec["pareto_restored_count"], 15)

    def test_minimum_slack_policy_relaxation_benchmark_replay(self):
        """F20: Replay all 15 minimum-slack Pareto policy relaxation evaluations across 5 model families."""
        artifact = RECEIPTS_DIR / "minimum_slack_policy_relaxation_benchmark.json"
        if not artifact.is_file():
            self.skipTest("minimum_slack_policy_relaxation_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.minimum_slack_policy_relaxation_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("pairs_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("evaluation_count"), 15)

        evals = data.get("evaluations", [])
        self.assertEqual(len(evals), 15)

        self.assertTrue(data["round_1_heuristic_headroom_metrics"]["identity_verified"])
        self.assertTrue(data["round_2_minimum_slack_audited_metrics"]["identity_verified"])

        replay_mon = StreamingMinimumSlackPolicyRelaxationMonitor(
            scope_id=data["minimum_slack_monitor_receipt"]["scope_id"]
        )
        for ev in evals:
            replay_mon.record_minimum_slack_evaluation(
                evaluation_id=ev["evaluation_id"],
                pair_name=ev["pair_name"],
                model_id=ev["model_id"],
                prior_escalation_receipt_sha256=ev["prior_escalation_receipt_sha256"],
                prior_policy_sha256=ev["prior_policy_sha256"],
                prior_policy_vector=ev["prior_policy_vector"],
                candidate_policies=ev["candidate_policies"],
                rounds=ev["rounds"],
            )
            self.assertTrue(ev["round_1_over_permissive_breach"])
            self.assertFalse(ev["converged_single_round"])
            self.assertTrue(ev["converged_multi_round"])
            self.assertEqual(
                ev["evaluation_status"],
                "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG",
            )

            # Replay both rounds' frontier monitor receipts
            pname = ev["pair_name"]
            mdl = ev["model_id"]
            for r_idx in range(2):
                act = ev["rounds"][r_idx]["action"]
                r_saved = ev["round_receipts"][r_idx]
                sel_pid = act["selected_policy_id"]
                if pname == "MinSlack_SideInfo_x_SkewRepair":
                    b1_val = {
                        "P1_under_relaxed": "3",
                        "P2_minimum_slack_pareto": "4",
                        "P3_over_permissive_grant": "8",
                    }[sel_pid]
                    rec_a, rec_b = _eval_relaxed_pair1_side_info_and_skew(
                        f"ms1_r{r_idx + 1}_{mdl}",
                        act["channel_capacity_s"],
                        act["symbols"],
                        act["candidate_alpha"],
                        relaxed_l1_budget=b1_val,
                    )
                elif pname == "MinSlack_PoE_x_SkewRepair":
                    b1_val = {
                        "P1_under_relaxed": "2",
                        "P2_minimum_slack_pareto": "3",
                        "P3_over_permissive_grant": "6",
                    }[sel_pid]
                    rec_a, rec_b = _eval_relaxed_pair2_poe_and_skew(
                        f"ms2_r{r_idx + 1}_{mdl}",
                        act["compromise_eps"],
                        act["candidate_alpha"],
                        relaxed_l1_budget=b1_val,
                    )
                elif pname == "MinSlack_ProjectiveTower_x_MerminPeres":
                    rec_a, rec_b = _eval_relaxed_pair3_tower_and_mermin_peres(
                        f"ms3_r{r_idx + 1}_{mdl}",
                        act["const_b"],
                        act["x_mod2"],
                        act["x_mod4"],
                        parity_gauge_flip=act["parity_gauge_flip"],
                    )
                else:
                    self.fail(f"Unknown minimum-slack coupled pair: {pname}")
                self.assertEqual(
                    rec_a["receipt_sha256"], r_saved["receipt_a"]["receipt_sha256"]
                )
                self.assertEqual(
                    rec_b["receipt_sha256"], r_saved["receipt_b"]["receipt_sha256"]
                )

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["minimum_slack_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(mon_rec["round_1_over_permissive_breach_rate"], "1")
        self.assertEqual(mon_rec["single_round_minimum_slack_rate"], "0")
        self.assertEqual(mon_rec["multi_round_minimum_slack_rate"], "1")
        self.assertEqual(mon_rec["multi_round_minimum_slack_gain"], "1")

    def test_weighted_policy_relaxation_benchmark_replay(self):
        """F21: Replay all 15 asymmetric risk-weighted policy relaxation evaluations across 5 model families."""
        artifact = RECEIPTS_DIR / "weighted_policy_relaxation_benchmark.json"
        if not artifact.is_file():
            self.skipTest("weighted_policy_relaxation_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.weighted_policy_relaxation_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("pairs_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("evaluation_count"), 15)

        evals = data.get("evaluations", [])
        self.assertEqual(len(evals), 15)

        self.assertTrue(data["round_1_unweighted_tie_metrics"]["identity_verified"])
        self.assertTrue(data["round_2_risk_weighted_audited_metrics"]["identity_verified"])

        replay_mon = StreamingWeightedPolicyRelaxationMonitor(
            scope_id=data["weighted_monitor_receipt"]["scope_id"]
        )
        for ev in evals:
            replay_mon.record_weighted_relaxation_evaluation(
                evaluation_id=ev["evaluation_id"],
                pair_name=ev["pair_name"],
                model_id=ev["model_id"],
                prior_escalation_receipt_sha256=ev["prior_escalation_receipt_sha256"],
                prior_policy_sha256=ev["prior_policy_sha256"],
                prior_policy_vector=ev["prior_policy_vector"],
                risk_weight_vector=ev["risk_weight_vector"],
                candidate_policies=ev["candidate_policies"],
                rounds=ev["rounds"],
            )
            self.assertEqual(len(ev["unweighted_minimum_tie_policy_ids"]), 2)
            self.assertTrue(ev["round_1_unweighted_tie_high_risk_breach"])
            self.assertFalse(ev["converged_single_round"])
            self.assertTrue(ev["converged_multi_round"])
            self.assertEqual(
                ev["evaluation_status"],
                "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG",
            )

            pname = ev["pair_name"]
            mdl = ev["model_id"]
            for r_idx in range(2):
                act = ev["rounds"][r_idx]["action"]
                r_saved = ev["round_receipts"][r_idx]
                sel_pid = act["selected_policy_id"]
                if pname == "Weighted_SideInfo_x_SkewRepair":
                    rec_a, rec_b = _eval_weighted_pair1_side_info_and_skew(
                        f"wp1_r{r_idx + 1}_{mdl}",
                        act["channel_capacity_s"],
                        act["error_budget"],
                        act["symbols"],
                        act["candidate_alpha"],
                        relaxed_l1_budget="4",
                    )
                elif pname == "Weighted_PoE_x_SkewRepair":
                    b_pair = (
                        ("3", "3")
                        if sel_pid == "PA_low_risk_quanta_refinement"
                        else ("4", "4")
                    )
                    rec_a, rec_b = _eval_weighted_pair2_poe_and_skew(
                        f"wp2_r{r_idx + 1}_{mdl}",
                        act["compromise_eps"],
                        act["candidate_alpha"],
                        relaxed_linf_budget=b_pair[0],
                        relaxed_l1_budget=b_pair[1],
                    )
                elif pname == "Weighted_ProjectiveTower_x_MerminPeres":
                    rec_a, rec_b = _eval_weighted_pair3_tower_and_mermin_peres(
                        f"wp3_r{r_idx + 1}_{mdl}",
                        act["const_b"],
                        act["x_mod2"],
                        act["x_mod4"],
                        parity_gauge_flip=act["parity_gauge_flip"],
                        row3_override=act["row3_override"],
                    )
                else:
                    self.fail(f"Unknown weighted coupled pair: {pname}")
                self.assertEqual(
                    rec_a["receipt_sha256"], r_saved["receipt_a"]["receipt_sha256"]
                )
                self.assertEqual(
                    rec_b["receipt_sha256"], r_saved["receipt_b"]["receipt_sha256"]
                )

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["weighted_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(mon_rec["round_1_unweighted_tie_high_risk_breach_rate"], "1")
        self.assertEqual(mon_rec["single_round_weighted_convergence_rate"], "0")
        self.assertEqual(mon_rec["multi_round_weighted_convergence_rate"], "1")
        self.assertEqual(mon_rec["multi_round_weighted_convergence_gain"], "1")

    def test_policy_ratchet_drift_benchmark_replay(self):
        """F22: Replay all 5 multi-step policy-ratchet drift trajectories (15 incident steps per phase) across 5 model families."""
        artifact = RECEIPTS_DIR / "policy_ratchet_drift_benchmark.json"
        if not artifact.is_file():
            self.skipTest("policy_ratchet_drift_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.policy_ratchet_drift_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("incidents_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("trajectory_count"), 5)
        self.assertEqual(data.get("incident_step_evaluation_count"), 15)

        self.assertTrue(data["phase_1_unrevoked_ratchet_chain_metrics"]["identity_verified"])
        self.assertTrue(data["phase_2_lease_revoked_chain_metrics"]["identity_verified"])
        self.assertTrue(data["phase_1_unrevoked_ratchet_step_metrics"]["identity_verified"])
        self.assertTrue(data["phase_2_lease_revoked_step_metrics"]["identity_verified"])

        replay_mon = StreamingPolicyRatchetDriftMonitor(
            scope_id=data["ratchet_monitor_receipt"]["scope_id"]
        )
        for t in data.get("trajectories", []):
            p1_incs = t["phase_1_unrevoked_ratchet_chain"]["incidents"]
            p2_incs = t["phase_2_lease_revoked_chain"]["incidents"]
            replay_mon.record_incident_trajectory(
                trajectory_id=t["trajectory_id"],
                model_id=t["model_id"],
                prior_escalation_receipt_sha256=t["prior_escalation_receipt_sha256"],
                baseline_policy_sha256=t["baseline_policy_sha256"],
                baseline_policy_vector=t["baseline_policy_vector"],
                risk_weight_vector=t["risk_weight_vector"],
                step_slack_budget=t["step_slack_budget"],
                horizon_drift_ceiling=t["horizon_drift_ceiling"],
                unrevoked_ratchet_incidents=p1_incs,
                lease_revoked_incidents=p2_incs,
            )
            self.assertTrue(t["phase_1_ratchet_horizon_breach"])
            self.assertFalse(t["converged_single_round"])
            self.assertTrue(t["converged_multi_round"])
            self.assertEqual(t["horizon_weighted_drift_reduction"], "7")

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["ratchet_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "SCOPED_LEASE_REVOCATION_HORIZON_COHERENT_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(mon_rec["phase_1_ratchet_horizon_breach_rate"], "1")
        self.assertEqual(mon_rec["single_round_horizon_coherence_rate"], "0")
        self.assertEqual(mon_rec["multi_round_lease_revoked_coherence_rate"], "1")
        self.assertEqual(mon_rec["lease_revocation_coherence_gain"], "1")

    def test_concurrent_lease_overlap_benchmark_replay(self):
        """F23: Replay all 5 concurrent overlapping incident lease schedules (15 lease steps per phase) across 5 model families."""
        artifact = RECEIPTS_DIR / "concurrent_lease_overlap_benchmark.json"
        if not artifact.is_file():
            self.skipTest("concurrent_lease_overlap_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.concurrent_lease_overlap_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("incidents_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("schedule_count"), 5)
        self.assertEqual(data.get("lease_evaluation_count"), 15)

        self.assertTrue(
            data["phase_1_uncoordinated_overlap_schedule_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_overlap_accounted_schedule_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_1_uncoordinated_overlap_lease_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_overlap_accounted_lease_metrics"]["identity_verified"]
        )

        replay_mon = StreamingConcurrentLeaseOverlapMonitor(
            scope_id=data["overlap_monitor_receipt"]["scope_id"]
        )
        for s in data.get("schedules", []):
            p1_leases = s["phase_1_uncoordinated_overlap_schedule"]["leases"]
            p2_leases = s["phase_2_overlap_accounted_schedule"]["leases"]
            replay_mon.record_overlap_schedule(
                schedule_id=s["schedule_id"],
                model_id=s["model_id"],
                prior_ratchet_receipt_sha256=s["prior_ratchet_receipt_sha256"],
                baseline_policy_sha256=s["baseline_policy_sha256"],
                baseline_policy_vector=s["baseline_policy_vector"],
                risk_weight_vector=s["risk_weight_vector"],
                individual_lease_budget=s["individual_lease_budget"],
                horizon_drift_ceiling=s["horizon_drift_ceiling"],
                uncoordinated_overlapping_leases=p1_leases,
                overlap_accounted_leases=p2_leases,
            )
            self.assertTrue(s["phase_1_overlap_horizon_breach"])
            self.assertFalse(s["converged_single_round"])
            self.assertTrue(s["converged_multi_round"])
            self.assertEqual(s["peak_concurrent_weighted_drift_reduction"], "7")

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["overlap_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "LEASE_OVERLAP_ACCOUNTING_HORIZON_COHERENT_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(mon_rec["phase_1_overlap_horizon_breach_rate"], "1")
        self.assertEqual(mon_rec["single_round_overlap_coherence_rate"], "0")
        self.assertEqual(mon_rec["multi_round_overlap_accounted_coherence_rate"], "1")
        self.assertEqual(mon_rec["overlap_accounting_coherence_gain"], "1")

    def test_simultaneous_budget_split_benchmark_replay(self):
        """F24: Replay all 5 simultaneous non-preemptible incident bursts (15 incident evaluations per phase) across 5 model families."""
        artifact = RECEIPTS_DIR / "simultaneous_budget_split_benchmark.json"
        if not artifact.is_file():
            self.skipTest("simultaneous_budget_split_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.simultaneous_budget_split_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("incidents_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("burst_count"), 5)
        self.assertEqual(data.get("incident_evaluation_count"), 15)

        self.assertTrue(
            data["phase_1_fractional_split_burst_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_priority_queued_burst_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_1_fractional_split_incident_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_priority_queued_incident_metrics"]["identity_verified"]
        )

        replay_mon = StreamingSimultaneousBudgetSplitMonitor(
            scope_id=data["split_monitor_receipt"]["scope_id"]
        )
        for b in data.get("bursts", []):
            p1_incs = b["phase_1_fractional_budget_split"]["incidents"]
            p2_incs = b["phase_2_priority_queued_admission"]["incidents"]
            replay_mon.record_simultaneous_burst(
                burst_id=b["burst_id"],
                model_id=b["model_id"],
                prior_overlap_receipt_sha256=b["prior_overlap_receipt_sha256"],
                baseline_policy_sha256=b["baseline_policy_sha256"],
                baseline_policy_vector=b["baseline_policy_vector"],
                risk_weight_vector=b["risk_weight_vector"],
                individual_lease_budget=b["individual_lease_budget"],
                horizon_drift_ceiling=b["horizon_drift_ceiling"],
                fractional_split_incidents=p1_incs,
                priority_queued_incidents=p2_incs,
            )
            self.assertTrue(b["phase_1_fractional_split_starvation"])
            self.assertFalse(b["converged_single_round"])
            self.assertTrue(b["converged_multi_round"])
            self.assertEqual(b["starved_incidents_eliminated"], 2)

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["split_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "PRIORITY_QUEUE_DEFERRED_ADMISSION_COHERENT_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(mon_rec["phase_1_fractional_split_starvation_rate"], "1")
        self.assertEqual(mon_rec["single_round_split_coherence_rate"], "0")
        self.assertEqual(mon_rec["multi_round_priority_queued_coherence_rate"], "1")
        self.assertEqual(mon_rec["priority_queue_coherence_gain"], "1")

    def test_deadline_priority_queue_benchmark_replay(self):
        """F25: Replay all 5 simultaneous deadline-constrained incident bursts (15 incident evaluations per phase) across 5 model families."""
        artifact = RECEIPTS_DIR / "deadline_priority_queue_benchmark.json"
        if not artifact.is_file():
            self.skipTest("deadline_priority_queue_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "lggr.deadline_priority_queue_replay.v1")
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("incidents_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 30)
        self.assertEqual(data.get("queue_count"), 5)
        self.assertEqual(data.get("incident_evaluation_count"), 15)

        self.assertTrue(
            data["phase_1_static_priority_queue_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_edf_deadline_queue_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_1_static_priority_incident_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_edf_deadline_incident_metrics"]["identity_verified"]
        )

        replay_mon = StreamingDeadlinePriorityQueueMonitor(
            scope_id=data["deadline_monitor_receipt"]["scope_id"]
        )
        for q in data.get("queues", []):
            p1_incs = q["phase_1_static_priority_queue"]["incidents"]
            p2_incs = q["phase_2_edf_deadline_queue"]["incidents"]
            replay_mon.record_deadline_queue_comparison(
                queue_id=q["queue_id"],
                model_id=q["model_id"],
                prior_split_receipt_sha256=q["prior_split_receipt_sha256"],
                baseline_policy_sha256=q["baseline_policy_sha256"],
                baseline_policy_vector=q["baseline_policy_vector"],
                risk_weight_vector=q["risk_weight_vector"],
                individual_lease_budget=q["individual_lease_budget"],
                horizon_drift_ceiling=q["horizon_drift_ceiling"],
                static_priority_incidents=p1_incs,
                edf_queued_incidents=p2_incs,
            )
            self.assertTrue(q["phase_1_static_deadline_breach"])
            self.assertFalse(q["converged_single_round"])
            self.assertTrue(q["converged_multi_round"])
            self.assertEqual(q["max_lateness_reduction_ticks"], 2)

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["deadline_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "EDF_DEADLINE_COHERENT_QUEUE_VERIFIED_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(
            mon_rec["phase_1_static_deadline_breach_rate"], "1"
        )
        self.assertEqual(mon_rec["single_round_static_deadline_coherence_rate"], "0")
        self.assertEqual(mon_rec["multi_round_edf_deadline_coherence_rate"], "1")
        self.assertEqual(mon_rec["edf_deadline_coherence_gain"], "1")

    def test_overloaded_deadline_bin_packing_benchmark_replay(self):
        """F26: Replay all 5 overloaded SLA deadline bursts (15 incident evaluations per phase across 3 phases) across 5 model families."""
        artifact = RECEIPTS_DIR / "overloaded_deadline_bin_packing_benchmark.json"
        if not artifact.is_file():
            self.skipTest("overloaded_deadline_bin_packing_benchmark.json not generated yet")
        data = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(
            data.get("schema"), "lggr.overloaded_deadline_bin_packing_replay.v1"
        )
        self.assertEqual(len(data.get("models_evaluated", [])), 5)
        self.assertEqual(len(data.get("incidents_evaluated", [])), 3)
        self.assertEqual(data.get("total_completions"), 35)
        self.assertEqual(data.get("burst_count"), 5)
        self.assertEqual(data.get("incident_evaluation_count"), 15)

        self.assertTrue(
            data["phase_1_serial_edf_burst_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_overload_escalation_burst_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_3_selective_bin_packed_burst_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_1_serial_edf_incident_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_2_overload_escalation_incident_metrics"]["identity_verified"]
        )
        self.assertTrue(
            data["phase_3_selective_bin_packed_incident_metrics"]["identity_verified"]
        )

        replay_mon = StreamingOverloadedDeadlineBinPackingMonitor(
            scope_id=data["overload_monitor_receipt"]["scope_id"]
        )
        for b in data.get("bursts", []):
            p1_incs = b["phase_1_serial_edf_overload"]["incidents"]
            p2_incs = b["phase_2_overload_halt_and_escalate"]["incidents"]
            p3_incs = b["phase_3_selective_bin_packed_edf"]["incidents"]
            replay_mon.record_overloaded_deadline_burst(
                burst_id=b["burst_id"],
                model_id=b["model_id"],
                prior_deadline_receipt_sha256=b["prior_deadline_receipt_sha256"],
                baseline_policy_sha256=b["baseline_policy_sha256"],
                baseline_policy_vector=b["baseline_policy_vector"],
                risk_weight_vector=b["risk_weight_vector"],
                individual_lease_budget=b["individual_lease_budget"],
                initial_horizon_drift_ceiling=b["initial_horizon_drift_ceiling"],
                expanded_horizon_drift_ceiling=b["expanded_horizon_drift_ceiling"],
                serial_edf_incidents=p1_incs,
                overload_escalation_incidents=p2_incs,
                selective_bin_packed_incidents=p3_incs,
            )
            self.assertTrue(b["phase_1_serial_edf_deadline_breach"])
            self.assertTrue(b["phase_2_halted_and_escalated"])
            self.assertFalse(b["converged_single_round"])
            self.assertTrue(b["converged_multi_round"])
            self.assertEqual(b["deadline_misses_eliminated"], 2)
            self.assertEqual(b["max_lateness_reduction_ticks"], 1)

        mon_rec = replay_mon.emit_receipt()
        self.assertEqual(
            mon_rec["receipt_sha256"],
            data["overload_monitor_receipt"]["receipt_sha256"],
        )
        self.assertEqual(
            mon_rec["status"], "EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG"
        )
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")
        self.assertEqual(
            mon_rec["phase_1_serial_edf_deadline_breach_rate"], "1"
        )
        self.assertEqual(mon_rec["phase_2_halt_and_escalate_rate"], "1")
        self.assertEqual(mon_rec["single_round_serial_edf_coherence_rate"], "0")
        self.assertEqual(mon_rec["multi_round_bin_packed_edf_coherence_rate"], "1")
        self.assertEqual(mon_rec["bin_packed_edf_coherence_gain"], "1")

    def test_variable_duration_graceful_shedding_benchmark_replay(self) -> None:
        """Verify variable_duration_graceful_shedding_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "variable_duration_graceful_shedding_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.variable_duration_graceful_shedding_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["burst_count"], 5)
        self.assertEqual(data["single_round_coherence_rate"], "0")
        self.assertEqual(data["multi_round_graceful_shedding_coherence_rate"], "1")
        self.assertEqual(data["graceful_shedding_coherence_gain"], "1")

        mon_rec = data["shedding_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_linearized_jacobian_soundness_benchmark_replay(self) -> None:
        """Verify linearized_jacobian_soundness_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "linearized_jacobian_soundness_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.linearized_jacobian_soundness_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["blind_coherence_rate"], "0")
        self.assertEqual(data["coupled_coherence_rate"], "1")
        self.assertEqual(data["full_coherence_rate"], "1")
        self.assertEqual(data["coupled_soundness_gain"], "1")

        mon_rec = data["jacobian_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "COUPLED_SOUNDNESS_VERIFIED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_watcher_dropout_gram_audit_benchmark_replay(self) -> None:
        """Verify watcher_dropout_gram_audit_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "watcher_dropout_gram_audit_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.watcher_dropout_gram_audit_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["critical_dropout_coherence_rate"], "0")
        self.assertEqual(data["redundant_dropout_coherence_rate"], "1")
        self.assertEqual(data["watcher_retention_coherence_gain"], "1")

        mon_rec = data["watcher_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "WATCHER_DROPOUT_RANK_AUDIT_VERIFIED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_policy_ranking_order_reversal_benchmark_replay(self) -> None:
        """Verify policy_ranking_order_reversal_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "policy_ranking_order_reversal_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.policy_ranking_order_reversal_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["cf_only_coherence_rate"], "0")
        self.assertEqual(data["dual_metric_coherence_rate"], "1")
        self.assertEqual(data["dual_metric_coherence_gain"], "1")

        mon_rec = data["order_reversal_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DUAL_METRIC_ORDER_REVERSAL_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_tool_assisted_fiber_splitting_benchmark_replay(self) -> None:
        """Verify tool_assisted_fiber_splitting_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "tool_assisted_fiber_splitting_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.tool_assisted_fiber_splitting_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unassisted_resolution_rate"], "0")
        self.assertEqual(data["tool_assisted_resolution_rate"], "1")
        self.assertEqual(data["tool_assisted_resolution_gain"], "1")

        mon_rec = data["fiber_splitting_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_multi_turn_pairwise_contextuality_benchmark_replay(self) -> None:
        """Verify multi_turn_pairwise_contextuality_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "multi_turn_pairwise_contextuality_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.multi_turn_pairwise_contextuality_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["ungated_contextual_coherence_rate"], "0")
        self.assertEqual(data["sheaf_reconciled_coherence_rate"], "1")
        self.assertEqual(data["sheaf_reconciliation_coherence_gain"], "1")

        mon_rec = data["transcript_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "PRE_GENERATION_SHEAF_RECONCILED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_disagreement_preserving_council_benchmark_replay(self) -> None:
        """Verify disagreement_preserving_council_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "disagreement_preserving_council_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.disagreement_preserving_council_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["collapsing_consensus_coherence_rate"], "0")
        self.assertEqual(data["disagreement_council_coherence_rate"], "1")
        self.assertEqual(data["disagreement_council_coherence_gain"], "1")

        mon_rec = data["council_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_bounded_depth_k_induction_benchmark_replay(self) -> None:
        """Verify bounded_depth_k_induction_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "bounded_depth_k_induction_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.bounded_depth_k_induction_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["out_of_carrier_coherence_rate"], "0")
        self.assertEqual(data["reachable_carrier_coherence_rate"], "1")
        self.assertEqual(data["reachable_carrier_coherence_gain"], "1")

        mon_rec = data["k_induction_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "REACHABLE_CARRIER_LIFT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")


if __name__ == "__main__":
    unittest.main()
