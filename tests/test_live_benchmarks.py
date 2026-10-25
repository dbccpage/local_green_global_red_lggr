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
    StreamingFiberMonitor,
    StreamingJointMultiMonitorRepairGuard,
    StreamingMerminPeresParityMonitor,
    StreamingProductOfExpertsMonitor,
    StreamingProjectiveTowerMonitor,
    StreamingSideInformationCapacityMonitor,
    StreamingSkewRepairMonitor,
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


if __name__ == "__main__":
    unittest.main()
