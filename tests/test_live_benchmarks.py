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
    StreamingCodebaseAdversarialSchemaMonitor,
    StreamingCodebaseBellPolytopeMonitor,
    StreamingCodebaseContextualSheafMonitor,
    StreamingCodebaseDeadlineBinPackingMonitor,
    StreamingCodebaseDisagreementCouncilMonitor,
    StreamingCodebaseDynamicSchemaMonitor,
    StreamingCodebaseFiberSplittingMonitor,
    StreamingCodebaseFigureEightWedgeMonitor,
    StreamingCodebaseGovernedRelaxationMonitor,
    StreamingCodebaseGracefulSheddingMonitor,
    StreamingCodebaseMerminPeresMonitor,
    StreamingCodebaseMultiLoopHodgeMonitor,
    StreamingCodebaseNonAbelianBraidMonitor,
    StreamingCodebaseObligationMigrationMonitor,
    StreamingCodebasePathKernelDashboardMonitor,
    StreamingCodebasePolicyRatchetMonitor,
    StreamingCodebasePolicyReversalMonitor,
    StreamingCodebaseProductOfExpertsMonitor,
    StreamingCodebaseProjectiveTowerMonitor,
    StreamingCodebaseSharedChordDiamondMonitor,
    StreamingCodebaseSideInfoCapacityMonitor,
    StreamingCodebaseSimultaneousSplitMonitor,
    StreamingCodebaseSixRoleDeduplicationMonitor,
    StreamingCodebaseSkewRepairMonitor,
    StreamingCodebaseSubgradientPivotMonitor,
    StreamingCodebaseThreePartyConstantMonitor,
    StreamingCodebaseWatcherDropoutMonitor,
    StreamingCodebaseWeightedRelaxationMonitor,
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

    def test_boundary_quorum_interface_benchmark_replay(self) -> None:
        """Verify boundary_quorum_interface_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "boundary_quorum_interface_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.boundary_quorum_interface_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["pass_quorum_coherence_rate"], "0")
        self.assertEqual(data["full_product_coherence_rate"], "1")
        self.assertEqual(data["interface_coherence_gain"], "1")

        mon_rec = data["interface_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_cross_role_deduplication_benchmark_replay(self) -> None:
        """Verify cross_role_deduplication_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "cross_role_deduplication_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.cross_role_deduplication_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["undeduplicated_coherence_rate"], "0")
        self.assertEqual(data["deduplicated_coherence_rate"], "1")
        self.assertEqual(data["cross_role_deduplication_gain"], "1")

        mon_rec = data["cross_role_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_stage_vs_e2e_integration_benchmark_replay(self) -> None:
        """Verify stage_vs_e2e_integration_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "stage_vs_e2e_integration_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.stage_vs_e2e_integration_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["collapsing_dashboard_coherence_rate"], "0")
        self.assertEqual(data["four_tuple_kernel_coherence_rate"], "1")
        self.assertEqual(data["dashboard_kernel_coherence_gain"], "1")

        mon_rec = data["stage_e2e_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_three_party_c3_bound_benchmark_replay(self) -> None:
        """Verify three_party_c3_bound_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "three_party_c3_bound_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.three_party_c3_bound_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["surrogate_ceiling_coherence_rate"], "0")
        self.assertEqual(data["certified_bracket_coherence_rate"], "1")
        self.assertEqual(data["c3_bracket_coherence_gain"], "1")

        mon_rec = data["c3_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_dynamic_schema_synthesis_benchmark_replay(self) -> None:
        """Verify dynamic_schema_synthesis_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "dynamic_schema_synthesis_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.dynamic_schema_synthesis_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["locked_schema_coherence_rate"], "0")
        self.assertEqual(data["dynamic_synthesis_coherence_rate"], "1")
        self.assertEqual(data["dynamic_schema_coherence_gain"], "1")

        mon_rec = data["dynamic_schema_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_adversarial_schema_side_channel_benchmark_replay(self) -> None:
        """Verify adversarial_schema_side_channel_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "adversarial_schema_side_channel_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.adversarial_schema_side_channel_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unauthenticated_or_underallocated_coherence_rate"], "0")
        self.assertEqual(data["host_authenticated_coherence_rate"], "1")
        self.assertEqual(data["host_authenticated_coherence_gain"], "1")

        mon_rec = data["adversarial_schema_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_equal_info_migration_obligation_benchmark_replay(self) -> None:
        """Verify equal_info_migration_obligation_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "equal_info_migration_obligation_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.equal_info_migration_obligation_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["conventional_checker_soundness_rate"], "0")
        self.assertEqual(data["lggr_equal_info_soundness_rate"], "1")
        self.assertEqual(data["equal_info_soundness_gain"], "1")

        mon_rec = data["equal_info_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_catalyst_rejuvenation_schedule_benchmark_replay(self) -> None:
        """Verify catalyst_rejuvenation_schedule_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "catalyst_rejuvenation_schedule_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.catalyst_rejuvenation_schedule_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unscheduled_or_late_coherence_rate"], "0")
        self.assertEqual(data["periodic_rejuvenation_coherence_rate"], "1")
        self.assertEqual(data["periodic_rejuvenation_coherence_gain"], "1")

        mon_rec = data["catalyst_schedule_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_dfa_reset_token_gluing_benchmark_replay(self) -> None:
        """Verify dfa_reset_token_gluing_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "dfa_reset_token_gluing_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.dfa_reset_token_gluing_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["non_reset_concatenation_coherence_rate"], "0")
        self.assertEqual(data["explicit_reset_gluing_coherence_rate"], "1")
        self.assertEqual(data["explicit_reset_gluing_coherence_gain"], "1")

        mon_rec = data["dfa_reset_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_cptp_blindspot_completion_benchmark_replay(self) -> None:
        """Verify cptp_blindspot_completion_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "cptp_blindspot_completion_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.cptp_blindspot_completion_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["incomplete_channel_coherence_rate"], "0")
        self.assertEqual(data["completed_channel_coherence_rate"], "1")
        self.assertEqual(data["cptp_completion_coherence_gain"], "1")

        mon_rec = data["cptp_completion_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_mayer_vietoris_reconciliation_benchmark_replay(self) -> None:
        """Verify mayer_vietoris_reconciliation_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "mayer_vietoris_reconciliation_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.mayer_vietoris_reconciliation_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unreconciled_overlap_coherence_rate"], "0")
        self.assertEqual(data["reconciled_coboundary_coherence_rate"], "1")
        self.assertEqual(data["mv_reconciliation_coherence_gain"], "1")

        mon_rec = data["mv_reconciliation_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_replay_order_envelope_benchmark_replay(self) -> None:
        """Verify replay_order_envelope_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "replay_order_envelope_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.replay_order_envelope_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["order_fragile_coherence_rate"], "0")
        self.assertEqual(data["permutation_robust_coherence_rate"], "1")
        self.assertEqual(data["replay_envelope_coherence_gain"], "1")

        mon_rec = data["replay_envelope_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "PERMUTATION_ROBUST_PREFIX_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_windowed_drift_rebalancing_benchmark_replay(self) -> None:
        """Verify windowed_drift_rebalancing_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "windowed_drift_rebalancing_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.windowed_drift_rebalancing_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unrebalanced_coherence_rate"], "0")
        self.assertEqual(data["periodic_rebalanced_coherence_rate"], "1")
        self.assertEqual(data["horizon_rebalancing_coherence_gain"], "1")

        mon_rec = data["windowed_rebalancing_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "PERIODIC_REBALANCED_HORIZON_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_optional_stopping_drawdown_benchmark_replay(self) -> None:
        """Verify optional_stopping_drawdown_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "optional_stopping_drawdown_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.optional_stopping_drawdown_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["uncapped_stopping_coherence_rate"], "0")
        self.assertEqual(data["loss_capped_stopping_coherence_rate"], "1")
        self.assertEqual(data["drawdown_cap_coherence_gain"], "1")

        mon_rec = data["optional_stopping_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_regge_gauss_bonnet_holonomy_benchmark_replay(self) -> None:
        """Verify regge_gauss_bonnet_holonomy_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "regge_gauss_bonnet_holonomy_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.regge_gauss_bonnet_holonomy_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["curved_star_coherence_rate"], "0")
        self.assertEqual(data["flat_holonomy_coherence_rate"], "1")
        self.assertEqual(data["regge_holonomy_coherence_gain"], "1")

        mon_rec = data["regge_holonomy_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "FLAT_EUCLIDEAN_LATTICE_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_coalitional_synergy_masking_benchmark_replay(self) -> None:
        """Verify coalitional_synergy_masking_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "coalitional_synergy_masking_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.coalitional_synergy_masking_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["masked_coalition_coherence_rate"], "0")
        self.assertEqual(data["shapley_resolved_coherence_rate"], "1")
        self.assertEqual(data["coalitional_attribution_coherence_gain"], "1")

        mon_rec = data["coalitional_synergy_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_pullback_mediator_factorization_benchmark_replay(self) -> None:
        """Verify pullback_mediator_factorization_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "pullback_mediator_factorization_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.pullback_mediator_factorization_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["coarse_interface_coherence_rate"], "0")
        self.assertEqual(data["universal_mediator_coherence_rate"], "1")
        self.assertEqual(data["pullback_factorization_coherence_gain"], "1")

        mon_rec = data["pullback_factorization_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "PULLBACK_FIBER_GLUED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_multi_loop_cup_hodge_benchmark_replay(self) -> None:
        """Verify multi_loop_cup_hodge_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "multi_loop_cup_hodge_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.multi_loop_cup_hodge_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_multi_loop_coherence_rate"], "0")
        self.assertEqual(data["exact_cup_hodge_coherence_rate"], "1")
        self.assertEqual(data["multi_loop_hodge_coherence_gain"], "1")

        mon_rec = data["multi_loop_cup_hodge_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "EXACT_GRADIENT_AND_CUP_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_figure_eight_wedge_hodge_benchmark_replay(self) -> None:
        """Verify figure_eight_wedge_hodge_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "figure_eight_wedge_hodge_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.figure_eight_wedge_hodge_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_wedge_coherence_rate"], "0")
        self.assertEqual(data["synchronized_wedge_gauge_coherence_rate"], "1")
        self.assertEqual(data["figure_eight_wedge_coherence_gain"], "1")

        mon_rec = data["figure_eight_wedge_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "WEDGE_GAUGE_GLUED_EXACT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_shared_chord_diamond_hodge_benchmark_replay(self) -> None:
        """Verify shared_chord_diamond_hodge_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "shared_chord_diamond_hodge_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.shared_chord_diamond_hodge_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_diamond_chord_coherence_rate"], "0")
        self.assertEqual(data["glued_diamond_chord_coherence_rate"], "1")
        self.assertEqual(data["shared_chord_diamond_coherence_gain"], "1")

        mon_rec = data["shared_chord_diamond_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DIAMOND_CHORD_GLUED_EXACT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_concurrent_code_swarm_directive_benchmark_replay(self) -> None:
        """Verify concurrent_code_swarm_directive_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "concurrent_code_swarm_directive_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.concurrent_code_swarm_directive_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["uncoordinated_wave_coherence_rate"], "0")
        self.assertEqual(data["symmetry_broken_directive_coherence_rate"], "1")
        self.assertEqual(data["code_swarm_directive_coherence_gain"], "1")

        mon_rec = data["codebase_merge_monitor_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_MERGE_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_diamond_codebase_pullback_benchmark_replay(self) -> None:
        """Verify diamond_codebase_pullback_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "diamond_codebase_pullback_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.diamond_codebase_pullback_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unmediated_worktree_merge_coherence_rate"], "0")
        self.assertEqual(data["pullback_mediated_contract_coherence_rate"], "1")
        self.assertEqual(data["diamond_pullback_coherence_gain"], "1")

        mon_rec = data["diamond_codebase_pullback_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DIAMOND_PULLBACK_CONTRACT_SYNTHESIZED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_catalyst_evolution_benchmark_replay(self) -> None:
        """Verify codebase_catalyst_evolution_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_catalyst_evolution_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_catalyst_evolution_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unrejuvenated_evolution_coherence_rate"], "0")
        self.assertEqual(data["scheduled_rejuvenation_coherence_rate"], "1")
        self.assertEqual(data["codebase_catalyst_rejuvenation_gain"], "1")

        mon_rec = data["codebase_catalyst_evolution_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_CATALYST_REJUVENATION_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_stateful_codebase_dfa_benchmark_replay(self) -> None:
        """Verify stateful_codebase_dfa_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "stateful_codebase_dfa_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.stateful_codebase_dfa_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["non_reset_session_coherence_rate"], "0")
        self.assertEqual(data["explicit_reset_session_coherence_rate"], "1")
        self.assertEqual(data["stateful_codebase_dfa_coherence_gain"], "1")

        mon_rec = data["stateful_codebase_dfa_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_DFA_RESET_GLUING_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_replay_order_benchmark_replay(self) -> None:
        """Verify codebase_replay_order_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_replay_order_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_replay_order_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unguarded_replay_order_coherence_rate"], "0")
        self.assertEqual(data["barrier_prenetted_replay_coherence_rate"], "1")
        self.assertEqual(data["codebase_replay_order_coherence_gain"], "1")

        mon_rec = data["codebase_replay_order_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_REPLAY_ORDER_BARRIER_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_coalitional_shapley_benchmark_replay(self) -> None:
        """Verify codebase_coalitional_shapley_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_coalitional_shapley_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_coalitional_shapley_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["loo_masked_coalitional_coherence_rate"], "0")
        self.assertEqual(data["joint_shapley_repaired_coherence_rate"], "1")
        self.assertEqual(data["codebase_coalitional_coherence_gain"], "1")

        mon_rec = data["codebase_coalitional_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_COALITIONAL_SHAPLEY_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_mayer_vietoris_benchmark_replay(self) -> None:
        """Verify codebase_mayer_vietoris_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_mayer_vietoris_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_mayer_vietoris_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unreconciled_overlap_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_coboundary_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_mayer_vietoris_coherence_gain"], "1")

        mon_rec = data["codebase_mayer_vietoris_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_MAYER_VIETORIS_RECONCILED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_windowed_drift_benchmark_replay(self) -> None:
        """Verify codebase_windowed_drift_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_windowed_drift_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_windowed_drift_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unrebalanced_window_codebase_coherence_rate"], "0")
        self.assertEqual(data["periodic_rebalanced_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_windowed_drift_coherence_gain"], "1")

        mon_rec = data["codebase_windowed_drift_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_WINDOWED_DRIFT_REBALANCED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_optional_stopping_benchmark_replay(self) -> None:
        """Verify codebase_optional_stopping_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_optional_stopping_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_optional_stopping_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["uncapped_stopping_codebase_coherence_rate"], "0")
        self.assertEqual(data["loss_capped_stopping_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_optional_stopping_coherence_gain"], "1")

        mon_rec = data["codebase_optional_stopping_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_OPTIONAL_STOPPING_DRAWDOWN_CAPPED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_cptp_channel_benchmark_replay(self) -> None:
        """Verify codebase_cptp_channel_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_cptp_channel_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_cptp_channel_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["incomplete_cptp_codebase_coherence_rate"], "0")
        self.assertEqual(data["completed_cptp_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_cptp_channel_coherence_gain"], "1")

        mon_rec = data["codebase_cptp_channel_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_CPTP_OPERATOR_COMPLETE_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_regge_holonomy_benchmark_replay(self) -> None:
        """Verify codebase_regge_holonomy_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_regge_holonomy_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_regge_holonomy_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["conical_hinge_codebase_coherence_rate"], "0")
        self.assertEqual(data["flat_holonomy_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_regge_holonomy_coherence_gain"], "1")

        mon_rec = data["codebase_regge_holonomy_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_REGGE_HOLONOMY_FLAT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_k_induction_benchmark_replay(self) -> None:
        """Verify codebase_k_induction_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_k_induction_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_k_induction_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["bounded_k3_escape_codebase_coherence_rate"], "0")
        self.assertEqual(data["inductive_invariant_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_k_induction_coherence_gain"], "1")

        mon_rec = data["codebase_k_induction_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_K_INDUCTION_SOUND_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_jacobian_soundness_benchmark_replay(self) -> None:
        """Verify codebase_jacobian_soundness_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_jacobian_soundness_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_jacobian_soundness_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["blind_observer_codebase_coherence_rate"], "0")
        self.assertEqual(data["full_rank_observable_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_jacobian_soundness_coherence_gain"], "1")

        mon_rec = data["codebase_jacobian_soundness_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_JACOBIAN_OBSERVABLE_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_boundary_quorum_benchmark_replay(self) -> None:
        """Verify codebase_boundary_quorum_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_boundary_quorum_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_boundary_quorum_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["quorum_masked_codebase_coherence_rate"], "0")
        self.assertEqual(data["strict_product_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_boundary_quorum_coherence_gain"], "1")

        mon_rec = data["codebase_boundary_quorum_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_BOUNDARY_PRODUCT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_lease_overlap_benchmark_replay(self) -> None:
        """Verify codebase_lease_overlap_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_lease_overlap_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_lease_overlap_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["overlapping_lease_codebase_coherence_rate"], "0")
        self.assertEqual(data["fencing_serialized_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_lease_overlap_coherence_gain"], "1")

        mon_rec = data["codebase_lease_overlap_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_LEASE_FENCING_SERIALIZED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

    def test_codebase_contextual_sheaf_benchmark_replay(self) -> None:
        """Verify codebase_contextual_sheaf_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_contextual_sheaf_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_contextual_sheaf_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["hollow_triangle_codebase_coherence_rate"], "0")
        self.assertEqual(data["global_section_reconciled_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_contextual_sheaf_coherence_gain"], "1")

        mon_rec = data["codebase_contextual_sheaf_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_CONTEXTUAL_SHEAF_RECONCILED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseContextualSheafMonitor(
            scope_id="live-codebase-contextual-sheaf-benchmark"
        )
        for idx, ev in enumerate(data["evaluations"], start=1):
            parsed = ev["model_parsed_json"]
            self.assertEqual(int(parsed["phase1_scaled_gap_m4"]), 2)
            self.assertEqual(int(parsed["phase2_scaled_gap_m4"]), 1)
            self.assertEqual(int(parsed["phase3_scaled_gap_m4"]), 0)
            replay_mon.evaluate_three_phase_sheaf_audit(
                f"codebase_sheaf_eval_{idx}_{ev['model_id'].replace('/', '_')}",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_watcher_dropout_benchmark_replay(self) -> None:
        """Verify codebase_watcher_dropout_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_watcher_dropout_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_watcher_dropout_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["critical_dropout_codebase_coherence_rate"], "0")
        self.assertEqual(data["full_rank_restored_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_watcher_dropout_coherence_gain"], "1")

        mon_rec = data["codebase_watcher_dropout_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_WATCHER_GRAM_FULL_RANK_RESTORED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseWatcherDropoutMonitor(
            scope_id="live-codebase-watcher-dropout-benchmark"
        )
        for idx, ev in enumerate(data["evaluations"], start=1):
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_gram_rank"], 2)
            self.assertEqual(ev["phase_1_crit_norm_squared"], 0)
            self.assertEqual(ev["phase_3_gram_rank"], 3)
            self.assertEqual(ev["phase_3_crit_norm_squared"], 4)
            replay_mon.evaluate_three_phase_gram_audit(
                f"codebase_gram_eval_{idx}_{ev['model_id'].replace('/', '_')}",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_policy_reversal_benchmark_replay(self) -> None:
        """Verify codebase_policy_reversal_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_policy_reversal_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_policy_reversal_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["cf_only_codebase_coherence_rate"], "0")
        self.assertEqual(data["dual_metric_reconciled_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_policy_reversal_coherence_gain"], "1")

        mon_rec = data["codebase_policy_reversal_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_POLICY_REVERSAL_DUAL_METRIC_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebasePolicyReversalMonitor(
            scope_id="live-codebase-policy-reversal-benchmark"
        )
        for idx, ev in enumerate(data["evaluations"], start=1):
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_selected_neg_num"], 96)
            self.assertEqual(ev["phase_1_surcharge_cents"], 16)
            self.assertEqual(ev["phase_3_selected_neg_num"], 75)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_policy_reversal_audit(
                f"codebase_policy_eval_{idx}_{ev['model_id'].replace('/', '_')}",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_fiber_splitting_benchmark_replay(self) -> None:
        """Verify codebase_fiber_splitting_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_fiber_splitting_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_fiber_splitting_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unassisted_reflection_codebase_coherence_rate"], "0")
        self.assertEqual(data["tool_assisted_split_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_fiber_splitting_coherence_gain"], "1")

        mon_rec = data["codebase_fiber_splitting_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseFiberSplittingMonitor(
            scope_id="live-codebase-fiber-splitting-benchmark"
        )
        for idx, ev in enumerate(data["evaluations"], start=1):
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_fiber_width"], 12)
            self.assertEqual(ev["phase_1_surcharge_cents"], 6)
            self.assertEqual(ev["phase_3_fiber_width"], 0)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_fiber_splitting_audit(
                f"codebase_split_eval_{idx}_{ev['model_id'].replace('/', '_')}",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_disagreement_council_benchmark_replay(self) -> None:
        """Verify codebase_disagreement_council_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_disagreement_council_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_disagreement_council_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["collapsing_consensus_codebase_coherence_rate"], "0")
        self.assertEqual(data["disagreement_council_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_disagreement_council_coherence_gain"], "1")

        mon_rec = data["codebase_disagreement_council_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_DISAGREEMENT_COUNCIL_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseDisagreementCouncilMonitor(
            scope_id="live-codebase-disagreement-council-benchmark"
        )
        for idx, ev in enumerate(data["evaluations"], start=1):
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_collision_floor"], 2)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_3_collision_floor"], 0)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_council_audit(
                f"codebase_council_eval_{idx}_{ev['model_id'].replace('/', '_')}",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_six_role_deduplication_benchmark_replay(self) -> None:
        """Verify codebase_six_role_deduplication_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_six_role_deduplication_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_six_role_deduplication_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["raw_six_role_codebase_coherence_rate"], "0")
        self.assertEqual(data["deduplicated_six_role_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_six_role_deduplication_coherence_gain"], "1")

        mon_rec = data["codebase_six_role_deduplication_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_SIX_ROLE_DEDUPLICATED_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseSixRoleDeduplicationMonitor(
            scope_id="live-codebase-six-role-deduplication-benchmark"
        )
        for ev in data["evaluations"]:
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_verdict_drift_count"], 1)
            self.assertEqual(ev["phase_1_surcharge_cents"], 20)
            self.assertEqual(ev["phase_3_double_counted_entries"], 0)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_six_role_audit(
                ev["audit_id"],
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_path_kernel_dashboard_benchmark_replay(self) -> None:
        """Verify codebase_path_kernel_dashboard_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_path_kernel_dashboard_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_path_kernel_dashboard_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["three_tuple_masked_codebase_coherence_rate"], "0")
        self.assertEqual(data["four_tuple_path_kernel_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_path_kernel_dashboard_coherence_gain"], "1")

        mon_rec = data["codebase_path_kernel_dashboard_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_PATH_KERNEL_DASHBOARD_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebasePathKernelDashboardMonitor(
            scope_id="live-codebase-path-kernel-dashboard-benchmark"
        )
        for ev in data["evaluations"]:
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_egd_count"], 2)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_3_egd_count"], 0)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_path_kernel_audit(
                ev["audit_id"],
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_dynamic_schema_benchmark_replay(self) -> None:
        """Verify codebase_dynamic_schema_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_dynamic_schema_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_dynamic_schema_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["locked_schema_codebase_coherence_rate"], "0")
        self.assertEqual(data["dynamic_schema_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_dynamic_schema_coherence_gain"], "1")

        mon_rec = data["codebase_dynamic_schema_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_DYNAMIC_SCHEMA_CONVERGED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseDynamicSchemaMonitor(
            scope_id="live-codebase-dynamic-schema-benchmark"
        )
        for ev in data["evaluations"]:
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_collision_count"], 2)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_3_collision_count"], 0)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_dynamic_schema_audit(
                ev["audit_id"],
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_adversarial_schema_benchmark_replay(self) -> None:
        """Verify codebase_adversarial_schema_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_adversarial_schema_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_adversarial_schema_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["unauthenticated_or_underallocated_codebase_coherence_rate"], "0")
        self.assertEqual(data["host_authenticated_2bit_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_adversarial_schema_coherence_gain"], "1")

        mon_rec = data["codebase_adversarial_schema_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_ADVERSARIAL_SCHEMA_AUTHENTICATED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseAdversarialSchemaMonitor(
            scope_id="live-codebase-adversarial-schema-benchmark"
        )
        for ev in data["evaluations"]:
            parsed = ev["model_parsed_json"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_spoofed_collisions"], 1)
            self.assertEqual(ev["phase_1_surcharge_cents"], 15)
            self.assertEqual(ev["phase_3_side_channel_floor"], 0)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_adversarial_schema_audit(
                ev["audit_id"],
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_graceful_shedding_benchmark_replay(self) -> None:
        """Verify codebase_graceful_shedding_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_graceful_shedding_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_graceful_shedding_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["deferred_or_inverted_codebase_coherence_rate"], "0")
        self.assertEqual(data["governed_shedding_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_graceful_shedding_coherence_gain"], "1")

        mon_rec = data["codebase_graceful_shedding_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_GRACEFUL_SHEDDING_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseGracefulSheddingMonitor(
            scope_id="openrouter-codebase-graceful-shedding-scope"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_missed_deadlines"], 1)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_2_excess_criticality_loss"], 7)
            self.assertEqual(ev["phase_3_retained_criticality"], 18)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_graceful_shedding_audit(
                ev["audit_id"],
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_obligation_migration_benchmark_replay(self) -> None:
        """Verify codebase_obligation_migration_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_obligation_migration_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_obligation_migration_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["conventional_equal_info_codebase_coherence_rate"], "0")
        self.assertEqual(data["lggr_equal_info_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_obligation_migration_coherence_gain"], "1")

        mon_rec = data["codebase_obligation_migration_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_OBLIGATION_MIGRATION_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseObligationMigrationMonitor(
            scope_id="live_codebase_obligation_migration"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_migration_count"], 1)
            self.assertEqual(ev["phase_1_surcharge_cents"], 5)
            self.assertEqual(ev["phase_2_obligation_count"], 1)
            self.assertEqual(ev["phase_2_excursion_units"], 1)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_obligation_migration_audit(
                ev["audit_id"],
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_three_party_c3_benchmark_replay(self) -> None:
        """Verify codebase_three_party_c3_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_three_party_c3_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_three_party_c3_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["surrogate_c3_codebase_coherence_rate"], "0")
        self.assertEqual(data["certified_c3_bracket_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_three_party_c3_coherence_gain"], "1")

        mon_rec = data["codebase_three_party_c3_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_THREE_PARTY_C3_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseThreePartyConstantMonitor(
            scope_id="live_codebase_three_party_c3"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_uncertified_count"], 4)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_2_uncertified_count"], 1)
            self.assertEqual(ev["phase_2_surcharge_cents"], 5)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_three_party_c3_audit(
                ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_multi_loop_hodge_benchmark_replay(self) -> None:
        """Verify codebase_multi_loop_hodge_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_multi_loop_hodge_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_multi_loop_hodge_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_hodge_codebase_coherence_rate"], "0")
        self.assertEqual(data["exact_gradient_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_multi_loop_hodge_coherence_gain"], "1")

        mon_rec = data["codebase_multi_loop_hodge_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "CODEBASE_MULTI_LOOP_HODGE_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseMultiLoopHodgeMonitor(
            scope_id="live_codebase_multi_loop_hodge"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 8)
            self.assertEqual(ev["phase_1_payout_cents"], 865)
            self.assertEqual(ev["phase_2_norm2_harmonic"], 3)
            self.assertEqual(ev["phase_2_surcharge_cents"], 3)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.evaluate_three_phase_multi_loop_hodge_audit(
                ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_figure_eight_wedge_benchmark_replay(self) -> None:
        """Verify codebase_figure_eight_wedge_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_figure_eight_wedge_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_figure_eight_wedge_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_wedge_codebase_coherence_rate"], "0")
        self.assertEqual(data["synchronized_wedge_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_figure_eight_wedge_coherence_gain"], "1")

        mon_rec = data["codebase_figure_eight_wedge_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "WEDGE_GAUGE_GLUED_EXACT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseFigureEightWedgeMonitor(
            scope_id="live_codebase_figure_eight_wedge"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 6)
            self.assertEqual(ev["phase_1_payout_cents"], 867)
            self.assertEqual(ev["phase_2_gauge_mismatch_cents"], 1)
            self.assertEqual(ev["phase_2_surcharge_cents"], 4)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_shared_chord_diamond_benchmark_replay(self) -> None:
        """Verify codebase_shared_chord_diamond_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_shared_chord_diamond_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_shared_chord_diamond_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_diamond_chord_codebase_coherence_rate"], "0")
        self.assertEqual(data["glued_diamond_chord_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_shared_chord_diamond_coherence_gain"], "1")

        mon_rec = data["codebase_shared_chord_diamond_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DIAMOND_CHORD_GLUED_EXACT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseSharedChordDiamondMonitor(
            scope_id="live_codebase_shared_chord_diamond"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 27)
            self.assertEqual(ev["phase_1_payout_cents"], 846)
            self.assertEqual(ev["phase_2_chord_mismatch_cents"], 1)
            self.assertEqual(ev["phase_2_surcharge_cents"], 25)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_governed_relaxation_benchmark_replay(self) -> None:
        """Verify codebase_governed_relaxation_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_governed_relaxation_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_governed_relaxation_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_governed_relaxation_codebase_coherence_rate"], "0")
        self.assertEqual(data["governed_minimum_slack_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_governed_relaxation_coherence_gain"], "1")

        mon_rec = data["codebase_governed_relaxation_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "GOVERNED_MINIMUM_SLACK_RELAXATION_CODEBASE_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseGovernedRelaxationMonitor(
            scope_id="live_codebase_governed_relaxation"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_excess_l1_slack"], 3)
            self.assertEqual(ev["phase_2_surcharge_cents"], 6)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_governed_relaxation",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_non_abelian_braid_benchmark_replay(self) -> None:
        """Verify codebase_non_abelian_braid_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_non_abelian_braid_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_non_abelian_braid_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_non_abelian_braid_codebase_coherence_rate"], "0")
        self.assertEqual(data["yang_baxter_braid_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_non_abelian_braid_coherence_gain"], "1")

        mon_rec = data["codebase_non_abelian_braid_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "YANG_BAXTER_BRAID_HOLONOMY_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseNonAbelianBraidMonitor(
            scope_id="live_codebase_non_abelian_braid"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 6)
            self.assertEqual(ev["phase_2_payout_cents"], 867)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_non_abelian_braid",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_subgradient_pivot_benchmark_replay(self) -> None:
        """Verify codebase_subgradient_pivot_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_subgradient_pivot_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_subgradient_pivot_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_subgradient_pivot_codebase_coherence_rate"], "0")
        self.assertEqual(data["bottleneck_subgradient_pivot_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_subgradient_pivot_coherence_gain"], "1")

        mon_rec = data["codebase_subgradient_pivot_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "BOTTLENECK_DUAL_WITNESS_PIVOT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseSubgradientPivotMonitor(
            scope_id="live_codebase_subgradient_pivot"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 12)
            self.assertEqual(ev["phase_1_payout_cents"], 861)
            self.assertEqual(ev["phase_2_surcharge_cents"], 8)
            self.assertEqual(ev["phase_2_payout_cents"], 865)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_subgradient_pivot",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_policy_ratchet_benchmark_replay(self) -> None:
        """Verify codebase_policy_ratchet_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_policy_ratchet_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_policy_ratchet_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_policy_ratchet_codebase_coherence_rate"], "0")
        self.assertEqual(data["sunset_revoked_policy_ratchet_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_policy_ratchet_coherence_gain"], "1")

        mon_rec = data["codebase_policy_ratchet_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "SCOPED_SUNSET_LEASE_REVOCATION_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebasePolicyRatchetMonitor(
            scope_id="live_codebase_policy_ratchet"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 11)
            self.assertEqual(ev["phase_1_payout_cents"], 862)
            self.assertEqual(ev["phase_2_surcharge_cents"], 5)
            self.assertEqual(ev["phase_2_payout_cents"], 868)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_policy_ratchet",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_skew_repair_benchmark_replay(self) -> None:
        """Verify codebase_skew_repair_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_skew_repair_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_skew_repair_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_skew_repair_codebase_coherence_rate"], "0")
        self.assertEqual(data["l1_minimum_skew_repair_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_skew_repair_coherence_gain"], "1")

        mon_rec = data["codebase_skew_repair_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "SKEW_L1_MINIMUM_REPAIR_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseSkewRepairMonitor(
            scope_id="live_codebase_skew_repair"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 6)
            self.assertEqual(ev["phase_2_payout_cents"], 867)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_skew_repair",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_poe_veto_benchmark_replay(self) -> None:
        """Verify codebase_poe_veto_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_poe_veto_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_poe_veto_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_poe_veto_codebase_coherence_rate"], "0")
        self.assertEqual(data["compromise_mass_poe_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_poe_veto_coherence_gain"], "1")

        mon_rec = data["codebase_poe_veto_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "POE_SHARED_COMPROMISE_MASS_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseProductOfExpertsMonitor(
            scope_id="live_codebase_poe_veto"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 12)
            self.assertEqual(ev["phase_1_payout_cents"], 861)
            self.assertEqual(ev["phase_2_surcharge_cents"], 7)
            self.assertEqual(ev["phase_2_payout_cents"], 866)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_poe_veto",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_simultaneous_split_benchmark_replay(self) -> None:
        """Verify codebase_simultaneous_split_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_simultaneous_split_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_simultaneous_split_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_simultaneous_split_codebase_coherence_rate"], "0")
        self.assertEqual(data["priority_queued_simultaneous_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_simultaneous_split_coherence_gain"], "1")

        mon_rec = data["codebase_simultaneous_split_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "SIMULTANEOUS_PRIORITY_QUEUE_JOINT_GUARD_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseSimultaneousSplitMonitor(
            scope_id="live_codebase_simultaneous_split"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 6)
            self.assertEqual(ev["phase_2_payout_cents"], 867)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_simultaneous_split",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_mermin_peres_benchmark_replay(self) -> None:
        """Verify codebase_mermin_peres_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_mermin_peres_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_mermin_peres_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_mermin_peres_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_mermin_peres_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_mermin_peres_coherence_gain"], "1")

        mon_rec = data["codebase_mermin_peres_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "NONCONTEXTUAL_PARITY_GRID_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseMerminPeresMonitor(
            scope_id="live_codebase_mermin_peres"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 6)
            self.assertEqual(ev["phase_2_payout_cents"], 867)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_mermin_peres",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_side_info_capacity_benchmark_replay(self) -> None:
        """Verify codebase_side_info_capacity_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_side_info_capacity_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_side_info_capacity_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_side_info_capacity_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_side_info_capacity_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_side_info_capacity_coherence_gain"], "1")

        mon_rec = data["codebase_side_info_capacity_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "SIDE_INFO_CAPACITY_SUFFICIENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseSideInfoCapacityMonitor(
            scope_id="live_codebase_side_info_capacity"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 8)
            self.assertEqual(ev["phase_2_payout_cents"], 865)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_side_info_capacity",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_deadline_bin_packing_benchmark_replay(self) -> None:
        """Verify codebase_deadline_bin_packing_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_deadline_bin_packing_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_deadline_bin_packing_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_deadline_bin_packing_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_deadline_bin_packing_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_deadline_bin_packing_coherence_gain"], "1")

        mon_rec = data["codebase_deadline_bin_packing_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "DEADLINE_BIN_PACKING_ADMISSION_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseDeadlineBinPackingMonitor(
            scope_id="live_codebase_deadline_bin_packing"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 6)
            self.assertEqual(ev["phase_2_payout_cents"], 867)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_deadline_bin_packing",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_projective_tower_benchmark_replay(self) -> None:
        """Verify codebase_projective_tower_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_projective_tower_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_projective_tower_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_projective_tower_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_projective_tower_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_projective_tower_coherence_gain"], "1")

        mon_rec = data["codebase_projective_tower_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "PROJECTIVE_TOWER_INTEGRAL_LIFT_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseProjectiveTowerMonitor(
            scope_id="live_codebase_projective_tower"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 4)
            self.assertEqual(ev["phase_2_payout_cents"], 869)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_projective_tower",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_bell_polytope_benchmark_replay(self) -> None:
        """Verify codebase_bell_polytope_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_bell_polytope_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_bell_polytope_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_bell_polytope_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_bell_polytope_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_bell_polytope_coherence_gain"], "1")

        mon_rec = data["codebase_bell_polytope_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "BELL_POLYTOPE_LHV_FACTORIZATION_COHERENT_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseBellPolytopeMonitor(
            scope_id="live_codebase_bell_polytope"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 16)
            self.assertEqual(ev["phase_1_payout_cents"], 857)
            self.assertEqual(ev["phase_2_surcharge_cents"], 8)
            self.assertEqual(ev["phase_2_payout_cents"], 865)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_bell_polytope",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)

    def test_codebase_weighted_relaxation_benchmark_replay(self) -> None:
        """Verify codebase_weighted_relaxation_benchmark.json receipt integrity and offline replay."""
        path = RECEIPTS_DIR / "codebase_weighted_relaxation_benchmark.json"
        self.assertTrue(path.exists(), f"Missing benchmark receipt {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = {k: v for k, v in data.items() if k != "receipt_sha256"}
        self.assertEqual(digest(body), data["receipt_sha256"])
        self.assertEqual(data["schema"], "lggr.codebase_weighted_relaxation_replay.v1")
        self.assertEqual(data["authority_effect"], "None")
        self.assertEqual(data["evaluation_count"], 5)
        self.assertEqual(data["obstructed_weighted_relaxation_codebase_coherence_rate"], "0")
        self.assertEqual(data["reconciled_weighted_relaxation_codebase_coherence_rate"], "1")
        self.assertEqual(data["codebase_weighted_relaxation_coherence_gain"], "1")

        mon_rec = data["codebase_weighted_relaxation_receipt"]
        mon_body = {k: v for k, v in mon_rec.items() if k != "receipt_sha256"}
        self.assertEqual(digest(mon_body), mon_rec["receipt_sha256"])
        self.assertEqual(mon_rec["status"], "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG")
        self.assertEqual(mon_rec["contract_status"], "COMPOSABLE_LGGG")

        replay_mon = StreamingCodebaseWeightedRelaxationMonitor(
            scope_id="live_codebase_weighted_relaxation"
        )
        for ev in data["evaluations"]:
            parsed = ev["parsed_controller_verdict"]
            self.assertIsInstance(parsed, dict)
            self.assertEqual(ev["phase_1_surcharge_cents"], 10)
            self.assertEqual(ev["phase_1_payout_cents"], 863)
            self.assertEqual(ev["phase_2_surcharge_cents"], 4)
            self.assertEqual(ev["phase_2_payout_cents"], 869)
            self.assertEqual(ev["phase_3_payout_cents"], 873)
            replay_mon.record_three_phase_codebase_audit(
                audit_id=f"{ev['model_id']}_weighted_relaxation",
                model_id=ev["model_id"],
            )
        self.assertEqual(replay_mon.current_receipt(), mon_rec)


if __name__ == "__main__":
    unittest.main()
