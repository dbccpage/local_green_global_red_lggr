"""Unit, sandbox, concurrent wave, and tamper-evident replay tests for the code-engineering swarm."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from experiments.concurrent_code_engineering_swarm.domain import (
    CANONICAL_DIAMOND_AGGREGATOR_SOURCE,
    CANONICAL_FEE_BRANCH_SOURCE,
    CANONICAL_PRICING_CHANNEL_SOURCE,
    CANONICAL_PRICING_COALITION_SOURCE,
    CANONICAL_PRICING_EVENTS_SOURCE,
    CANONICAL_PRICING_MESH_SOURCE,
    CANONICAL_PRICING_MV_SOURCE,
    CANONICAL_PRICING_SOURCE,
    CANONICAL_PRICING_STOP_SOURCE,
    CANONICAL_PRICING_TX_SOURCE,
    CANONICAL_PRICING_WIN_SOURCE,
    CANONICAL_QUOTE_ANCHOR_SOURCE,
    CANONICAL_SETTLEMENT_CHANNEL_SOURCE,
    CANONICAL_SETTLEMENT_COALITION_SOURCE,
    CANONICAL_SETTLEMENT_EVENTS_SOURCE,
    CANONICAL_SETTLEMENT_MESH_SOURCE,
    CANONICAL_SETTLEMENT_MV_SOURCE,
    CANONICAL_SETTLEMENT_SOURCE,
    CANONICAL_SETTLEMENT_STOP_SOURCE,
    CANONICAL_SETTLEMENT_TX_SOURCE,
    CANONICAL_SETTLEMENT_WIN_SOURCE,
    CANONICAL_TAX_BRANCH_SOURCE,
    CANONICAL_TAX_CHANNEL_SOURCE,
    CANONICAL_TAX_COALITION_SOURCE,
    CANONICAL_TAX_EVENTS_SOURCE,
    CANONICAL_TAX_MESH_SOURCE,
    CANONICAL_TAX_MV_SOURCE,
    CANONICAL_TAX_SOURCE,
    CANONICAL_TAX_STOP_SOURCE,
    CANONICAL_TAX_TX_SOURCE,
    CANONICAL_TAX_WIN_SOURCE,
    CODE_SWARM_MODELS,
    COUNCIL_PRICING_ANCHOR_SRC,
    COUNCIL_SETTLEMENT_COLLAPSING_SRC,
    COUNCIL_SETTLEMENT_FULL_SRC,
    COUNCIL_TAX_BINARY_SRC,
    DIAMOND_SWARM_MODELS,
    DIAMOND_WORKTREE_BRANCHES,
    GRAM_PRICING_SOURCE,
    GRAM_SETTLEMENT_DROPOUT_SOURCE,
    GRAM_SETTLEMENT_RESTORED_SOURCE,
    GRAM_TAX_DROPOUT_SOURCE,
    GRAM_TAX_RESTORED_SOURCE,
    JACOBIAN_PRICING_SOURCE,
    JACOBIAN_SETTLEMENT_BLIND_SOURCE,
    JACOBIAN_SETTLEMENT_OBSERVABLE_SOURCE,
    JACOBIAN_TAX_ALIGNED_SOURCE,
    JACOBIAN_TAX_DRIFT_SOURCE,
    KERNEL_PRICING_ANCHOR_SRC,
    KERNEL_SETTLEMENT_NGD_SRC,
    KERNEL_SETTLEMENT_REPAIRED_SRC,
    KERNEL_TAX_NO_FALLBACK_SRC,
    KINDUCTION_PRICING_SOURCE,
    KINDUCTION_SETTLEMENT_ESCAPE_SOURCE,
    KINDUCTION_SETTLEMENT_SOUND_SOURCE,
    KINDUCTION_TAX_FRACTIONAL_SOURCE,
    KINDUCTION_TAX_SOUND_SOURCE,
    LEASE_PRICING_SOURCE,
    LEASE_SETTLEMENT_OVERLAP_SOURCE,
    LEASE_SETTLEMENT_SERIALIZED_SOURCE,
    LEASE_TAX_OVERLAP_SOURCE,
    LEASE_TAX_SERIALIZED_SOURCE,
    POLICY_PRICING_ANCHOR_SRC,
    POLICY_SETTLEMENT_CF_ONLY_SRC,
    POLICY_SETTLEMENT_DUAL_METRIC_SRC,
    POLICY_TAX_M_CONTEXT_SRC,
    POLICY_TAX_SURROGATE_SRC,
    QUORUM_PRICING_SOURCE,
    QUORUM_SETTLEMENT_QUORUM_SOURCE,
    QUORUM_SETTLEMENT_STRICT_SOURCE,
    QUORUM_TAX_ALIGNED_SOURCE,
    QUORUM_TAX_DRIFT_SOURCE,
    ROLE_PRICING_ANCHOR_SRC,
    ROLE_SETTLEMENT_DEDUP_SRC,
    ROLE_SETTLEMENT_RAW_P1_SRC,
    ROLE_SETTLEMENT_RAW_P2_SRC,
    ROLE_TAX_PRESERVED_SRC,
    SHEAF_PRICING_SOURCE,
    SHEAF_SETTLEMENT_CONTEXTUAL_SOURCE,
    SHEAF_SETTLEMENT_RECONCILED_SOURCE,
    SHEAF_TAX_CONTEXTUAL_SOURCE,
    SHEAF_TAX_RECONCILED_SOURCE,
    SPLIT_PRICING_ANCHOR_SRC,
    SPLIT_SETTLEMENT_FULL_SRC,
    SPLIT_TAX_1BIT_SRC,
    BoundaryQuorumCodeWorkspace,
    CPTPChannelCodeWorkspace,
    CatalystCodeWorkspace,
    CoalitionalCodeWorkspace,
    CodeWorkspace,
    ContextualSheafCodeWorkspace,
    DiamondCodeWorkspace,
    DisagreementCouncilCodeWorkspace,
    FiberSplittingCodeWorkspace,
    JacobianCodeWorkspace,
    KInductionCodeWorkspace,
    LeaseOverlapCodeWorkspace,
     MayerVietorisCodeWorkspace,
    OptionalStoppingCodeWorkspace,
    PathKernelDashboardCodeWorkspace,
    PolicyReversalCodeWorkspace,
    ReggeHolonomyCodeWorkspace,
    ReplayOrderCodeWorkspace,
    SixRoleDeduplicationCodeWorkspace,
    StatefulDFACodeWorkspace,
    WatcherDropoutCodeWorkspace,
    WindowedDriftCodeWorkspace,
    catalyst_fixture,
    coalitional_fixture,
    council_fixture,
    cptp_fixture,
    dfa_fixture,
    diamond_fixture,
    fixture,
    gram_fixture,
    jacobian_fixture,
    kinduction_fixture,
    lease_fixture,
    mv_fixture,
    path_kernel_fixture,
    policy_fixture,
    quorum_fixture,
    regge_fixture,
    replay_fixture,
    run_coalitional_local_unit_tests,
    run_council_local_unit_tests,
    run_cptp_local_unit_tests,
    run_dfa_local_unit_tests,
    run_diamond_local_unit_tests,
    run_gram_local_unit_tests,
    run_jacobian_local_unit_tests,
    run_kinduction_local_unit_tests,
    run_lease_local_unit_tests,
    run_local_unit_tests,
    run_mv_local_unit_tests,
    run_path_kernel_local_unit_tests,
    run_policy_local_unit_tests,
    run_quorum_local_unit_tests,
    run_regge_local_unit_tests,
    run_replay_local_unit_tests,
    run_sheaf_local_unit_tests,
    run_six_role_local_unit_tests,
    run_split_local_unit_tests,
    run_stop_local_unit_tests,
    run_win_local_unit_tests,
    sheaf_fixture,
    six_role_fixture,
    split_fixture,
    stop_fixture,
    win_fixture,
)
from experiments.concurrent_code_engineering_swarm.runner import (
    CodeBatchClient,
    campaign,
    catalyst_campaign,
    coalitional_campaign,
    council_campaign,
    cptp_campaign,
    dfa_campaign,
    diamond_campaign,
    gram_campaign,
    jacobian_campaign,
    kinduction_campaign,
    lease_campaign,
    mv_campaign,
    path_kernel_campaign,
    policy_campaign,
    quorum_campaign,
    regge_campaign,
    replay,
    replay_campaign,
    sheaf_campaign,
    six_role_campaign,
    split_campaign,
    stop_campaign,
    win_campaign,
)
from experiments.live_five_agent_swarm.client import Events, event_digest
from lggr.streaming import (
    StreamingCodebaseBoundaryQuorumMonitor,
    StreamingCodebaseCPTPChannelMonitor,
    StreamingCodebaseCatalystEvolutionMonitor,
    StreamingCodebaseCoalitionalMonitor,
    StreamingCodebaseContextualSheafMonitor,
    StreamingCodebaseDisagreementCouncilMonitor,
    StreamingCodebaseFiberSplittingMonitor,
    StreamingCodebaseInterfaceMergeMonitor,
    StreamingCodebaseJacobianSoundnessMonitor,
    StreamingCodebaseKInductionMonitor,
    StreamingCodebaseLeaseOverlapMonitor,
    StreamingCodebaseMayerVietorisMonitor,
    StreamingCodebaseOptionalStoppingMonitor,
    StreamingCodebasePathKernelDashboardMonitor,
    StreamingCodebasePolicyReversalMonitor,
    StreamingCodebaseReggeHolonomyMonitor,
    StreamingCodebaseReplayOrderMonitor,
    StreamingCodebaseSixRoleDeduplicationMonitor,
    StreamingCodebaseWatcherDropoutMonitor,
    StreamingCodebaseWindowedDriftMonitor,
    StreamingDiamondCodebasePullbackMonitor,
    StreamingStatefulCodebaseDFAMonitor,
)


def stub_code_transport(payload: dict) -> dict:
    """Deterministic stub transport simulating 3 concurrent coding agents."""
    messages = payload["messages"]
    sys_msg = messages[0]["content"]
    worker = sys_msg.split("agent ")[1].split(",")[0]

    # First turn in wave: call inspect_workspace
    if messages[-1]["role"] == "user":
        tool_call = {
            "id": f"call_inspect_{worker}",
            "type": "function",
            "function": {"name": "inspect_workspace", "arguments": "{}"},
        }
    else:
        inspected = json.loads(messages[-1]["content"])
        if inspected.get("infeasible_constraint") is not None:
            tool_call = {
                "id": f"call_esc_{worker}",
                "type": "function",
                "function": {
                    "name": "escalate",
                    "arguments": json.dumps(
                        {"reason": "Immutable upstream batch limit conflicts with downstream minimum."}
                    ),
                },
            }
        else:
            canonical_map = {
                "worker-0": CANONICAL_PRICING_SOURCE,
                "worker-1": CANONICAL_TAX_SOURCE,
                "worker-2": CANONICAL_SETTLEMENT_SOURCE,
            }
            tool_call = {
                "id": f"call_patch_{worker}",
                "type": "function",
                "function": {
                    "name": "submit_module_patch",
                    "arguments": json.dumps({"source_code": canonical_map[worker]}),
                },
            }

    return {
        "response": {
            "model": payload["model"],
            "usage": {"cost": "0.0001"},
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "role": "assistant",
                        "tool_calls": [tool_call],
                    },
                }
            ],
        },
        "started_ns": 10,
        "finished_ns": 20,
    }


class ConcurrentCodeEngineeringSwarmTests(unittest.TestCase):
    def test_ast_sandbox_rejects_forbidden_imports_and_builtins(self) -> None:
        bad_os = "import os\ndef compute_quote(items, discount_bps):\n    return {}\n"
        rep_os = StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast("pricing", bad_os)
        self.assertTrue(rep_os["syntax_ok"])
        self.assertFalse(rep_os["sandbox_ok"])
        self.assertIn("forbidden_import:os", rep_os["sandbox_violations"])

        bad_eval = "def compute_quote(items, discount_bps):\n    return eval('{}')\n"
        rep_eval = StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast("pricing", bad_eval)
        self.assertTrue(rep_eval["syntax_ok"])
        self.assertFalse(rep_eval["sandbox_ok"])
        self.assertIn("forbidden_call:eval", rep_eval["sandbox_violations"])

    def test_local_green_unit_tests_vs_stagewise_lggr_merge_gate(self) -> None:
        state = fixture(6102)  # 6102 % 3 == 0 -> schema_and_fee_drift
        self.assertEqual(state["kind"], "schema_and_fee_drift")
        ws = CodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing": True, "tax_engine": True, "settlement_router": True},
        )

        mon = StreamingCodebaseInterfaceMergeMonitor(scope_id="unit-stagewise-gate")
        rec = mon.evaluate_codebase_merge(
            "eval-6102-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        # Verify BOTH tax_engine schema mismatch AND settlement_router fee-base drift are caught in wave 0
        self.assertEqual(len(rec["contract_mismatches"]), 1)
        self.assertEqual(rec["contract_mismatches"][0]["worker"], "worker-1")
        self.assertEqual(len(rec["conservation_defects"]), 1)
        self.assertEqual(rec["conservation_defects"][0]["worker"], "worker-2")
        self.assertEqual(rec["conservation_defects"][0]["fee_base_drift_cents"], 5)

    def test_campaign_and_tamper_evident_replay(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "seeds": [6100, 6101, 6102],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_code_transport)
            summary = campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)

            # Tamper check on gate receipt
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["global_green"] = 1 - gate_rec["global_green"]
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_pilot_evidence_replay_if_present(self) -> None:
        pilot_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "pilot_run"
            / "events.jsonl"
        )
        if pilot_events.exists():
            replayed = replay(pilot_events)
            self.assertEqual(replayed["schema"], "lggr.concurrent_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_diamond_local_green_worktree_tests_vs_pullback_mediator_merge_gate(self) -> None:
        state = diamond_fixture(7200)  # 7200 % 3 == 0 -> incompatible_middle_branch_extensions
        self.assertEqual(state["kind"], "incompatible_middle_branch_extensions")
        ws = DiamondCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {
                "quote_anchor": True,
                "tax_branch": True,
                "fee_branch": True,
                "diamond_aggregator": True,
            },
        )

        mon = StreamingDiamondCodebasePullbackMonitor(scope_id="unit-diamond-gate")
        rec = mon.evaluate_diamond_codebase_merge(
            "eval-7200-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertFalse(rec["in_pullback_square"])
        self.assertEqual(rec["interface_fiber_size"], 0)
        self.assertEqual(len(rec["contract_mismatches"]), 2)
        self.assertEqual(len(rec["conservation_defects"]), 1)
        self.assertEqual(rec["conservation_defects"][0]["worker"], "worker-3")
        self.assertEqual(rec["conservation_defects"][0]["payout_drift_cents"], 180)

        # Verify 3-phase audit on StreamingDiamondCodebasePullbackMonitor
        audit = mon.record_three_phase_diamond_codebase_audit("diamond-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_interface_fiber_size"], 4)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_interface_fiber_size"], 1)
        self.assertEqual(
            audit["phase_3_universal_mediator"],
            {"w_diamond": ["b_net_v1_900", "c_net_v1_900"]},
        )

    def test_diamond_campaign_and_tamper_evident_replay(self) -> None:
        def stub_diamond_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Immutable upstream 2-decimal precision conflicts with downstream 4-decimal requirement."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_QUOTE_ANCHOR_SOURCE,
                        "worker-1": CANONICAL_TAX_BRANCH_SOURCE,
                        "worker-2": CANONICAL_FEE_BRANCH_SOURCE,
                        "worker-3": CANONICAL_DIAMOND_AGGREGATOR_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "diamond",
                "seeds": [7200, 7201, 7202],
                "models": DIAMOND_SWARM_MODELS,
                "worktree_branches": dict(DIAMOND_WORKTREE_BRANCHES),
                "budget_usd": "0.60",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.60", transport=stub_diamond_transport)
            summary = diamond_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.diamond_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 4)

            # Tamper check on diamond gate receipt
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["in_pullback_square"] = not gate_rec["in_pullback_square"]
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_diamond_pilot_evidence_replay_if_present(self) -> None:
        diamond_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "diamond_pilot_run"
            / "events.jsonl"
        )
        diamond_summary = diamond_events.with_name("summary.json")
        if diamond_events.exists() and diamond_summary.exists():
            replayed = replay(diamond_events)
            self.assertEqual(replayed["schema"], "lggr.diamond_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_catalyst_workspace_and_evolution_monitor_detects_shim_debt(self) -> None:
        state = catalyst_fixture(8301)  # multi_ticket_catalyst_debt_breach
        ws = CatalystCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing": True, "tax_engine": True, "settlement_router": True},
        )

        mon = StreamingCodebaseCatalystEvolutionMonitor(scope_id="unit-catalyst-gate")
        rec = mon.evaluate_ticket_step(
            "eval-8301-wave0",
            ticket_id=state["ticket_id"],
            sources=ws.state["sources"],
            local_test_results=verdicts,
            previous_catalyst_debt=state["previous_catalyst_debt"],
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["previous_catalyst_debt"], 4)
        self.assertEqual(rec["catalyst_wear_delta"], 2)
        self.assertEqual(rec["total_catalyst_debt"], 6)
        self.assertEqual(rec["status"], "CATALYST_TECHNICAL_DEBT_CEILING_BREACH_NGD_LGGR")
        self.assertEqual(
            rec["module_debt_breakdown"]["pricing"]["dead_helper_functions"],
            ["_legacy_discount_shim"],
        )
        self.assertEqual(
            rec["module_debt_breakdown"]["pricing"]["deprecated_alias_keys"],
            ["legacy_subtotal_cents"],
        )

        # Verify 3-phase audit on StreamingCodebaseCatalystEvolutionMonitor
        audit = mon.record_three_phase_codebase_catalyst_audit("catalyst-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_1_terminal_debt"], 6)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_terminal_debt"], 4)
        self.assertEqual(audit["phase_2_max_debt"], 6)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_terminal_debt"], 0)
        self.assertEqual(audit["phase_3_max_debt"], 4)

    def test_catalyst_campaign_and_tamper_evident_replay(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "catalyst",
                "seeds": [8300, 8301, 8302],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_code_transport)
            summary = catalyst_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.catalyst_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on catalyst gate debt field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["total_catalyst_debt"] = int(gate_rec["total_catalyst_debt"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_catalyst_pilot_evidence_replay_if_present(self) -> None:
        cat_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "catalyst_pilot_run"
            / "events.jsonl"
        )
        cat_summary = cat_events.with_name("summary.json")
        if cat_events.exists() and cat_summary.exists():
            replayed = replay(cat_events)
            self.assertEqual(replayed["schema"], "lggr.catalyst_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_dfa_workspace_and_stateful_monitor_detects_unreleased_lock_trap(self) -> None:
        state = dfa_fixture(9402)  # unreleased_session_lock_trap (9402 % 3 == 0)
        ws = StatefulDFACodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_tx": True, "tax_tx": True, "settlement_tx": True},
        )

        mon = StreamingStatefulCodebaseDFAMonitor(scope_id="unit-dfa-gate")
        rec = mon.evaluate_stateful_codebase_dfa(
            "eval-9402-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["non_reset_module_count"], 3)
        self.assertEqual(rec["terminal_session_state"], "q3_err")
        self.assertEqual(rec["status"], "NON_RESET_DFA_CONCATENATION_MISMATCH_LGGR")

        audit = mon.record_three_phase_stateful_codebase_dfa_audit("dfa-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_1_non_reset_count"], 3)
        self.assertEqual(audit["phase_1_terminal_state"], "q3_err")
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_non_reset_count"], 1)
        self.assertEqual(audit["phase_2_terminal_state"], "q3_err")
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_non_reset_count"], 0)
        self.assertEqual(audit["phase_3_terminal_state"], "q0_idle")

    def test_dfa_campaign_and_tamper_evident_replay(self) -> None:
        def stub_dfa_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Upstream lock hold conflicts with downstream idle entry requirement."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_TX_SOURCE,
                        "worker-1": CANONICAL_TAX_TX_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_TX_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "dfa",
                "seeds": [9400, 9401, 9402],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_dfa_transport)
            summary = dfa_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.stateful_dfa_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on DFA gate non_reset_module_count field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["non_reset_module_count"] = int(gate_rec["non_reset_module_count"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_dfa_pilot_evidence_replay_if_present(self) -> None:
        dfa_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "dfa_pilot_run"
            / "events.jsonl"
        )
        dfa_summary = dfa_events.with_name("summary.json")
        if dfa_events.exists() and dfa_summary.exists():
            replayed = replay(dfa_events)
            self.assertEqual(replayed["schema"], "lggr.stateful_dfa_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_replay_workspace_and_monitor_detects_arrival_masked_causal_breach(self) -> None:
        state = replay_fixture(9501)  # arrival_masked_replay_breach (9501 % 3 == 0)
        ws = ReplayOrderCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_events": True, "tax_events": True, "settlement_events": True},
        )

        mon = StreamingCodebaseReplayOrderMonitor(prefix_budget=900, scope_id="unit-replay-gate")
        rec = mon.evaluate_codebase_replay_order(
            "eval-9501-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["arrival_max_prefix_cents"], 180)
        self.assertEqual(rec["causal_max_prefix_cents"], 1080)
        self.assertEqual(rec["worst_permutation_max_prefix_cents"], 1080)
        self.assertEqual(rec["common_endpoint_sum_cents"], 180)
        self.assertEqual(rec["missing_barrier_count"], 3)
        self.assertEqual(rec["status"], "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR")

        audit = mon.record_three_phase_codebase_replay_order_audit("replay-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_1_arrival_max_prefix_cents"], 180)
        self.assertEqual(audit["phase_1_causal_max_prefix_cents"], 1080)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_causal_max_prefix_cents"], 900)
        self.assertEqual(audit["phase_2_worst_max_prefix_cents"], 1080)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_worst_max_prefix_cents"], 900)
        self.assertEqual(audit["phase_3_missing_barriers"], 0)

    def test_replay_campaign_and_tamper_evident_replay(self) -> None:
        def stub_replay_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Locked escrow reservation 1000 cents exceeds prefix budget 900 cents."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_EVENTS_SOURCE,
                        "worker-1": CANONICAL_TAX_EVENTS_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_EVENTS_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "replay",
                "seeds": [9500, 9501, 9502],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_replay_transport)
            summary = replay_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.replay_order_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on replay gate worst_permutation_max_prefix_cents field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["worst_permutation_max_prefix_cents"] = int(gate_rec["worst_permutation_max_prefix_cents"]) + 10
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_replay_pilot_evidence_replay_if_present(self) -> None:
        rep_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "replay_pilot_run"
            / "events.jsonl"
        )
        rep_summary = rep_events.with_name("summary.json")
        if rep_events.exists() and rep_summary.exists():
            replayed = replay(rep_events)
            self.assertEqual(replayed["schema"], "lggr.replay_order_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_coalitional_workspace_and_monitor_detects_leave_one_out_masked_synergistic_defect(self) -> None:
        state = coalitional_fixture(9600)  # synergistic_fee_basis_fallback_shims (9600 % 3 == 0)
        ws = CoalitionalCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_coalition": True, "tax_coalition": True, "settlement_coalition": True},
        )

        mon = StreamingCodebaseCoalitionalMonitor(scope_id="unit-coalitional-gate")
        rec = mon.evaluate_codebase_coalitions(
            "eval-9600-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["grand_coalition_value"], -1)
        self.assertEqual(
            rec["leave_one_out_marginals"],
            {"pricing_coalition": 0, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(rec["pairwise_pricing_settlement_synergy"], 1)
        self.assertEqual(
            rec["two_times_shapley_attributions"],
            {"pricing_coalition": -1, "tax_coalition": 0, "settlement_coalition": -1},
        )
        self.assertEqual(rec["status"], "LEAVE_ONE_OUT_MASKED_COALITIONAL_DEFECT_LGGR")

        audit = mon.record_three_phase_codebase_coalitional_audit("coalitional-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(
            audit["phase_1_leave_one_out_marginals"],
            {"pricing_coalition": 0, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(
            audit["phase_1_two_times_shapley"],
            {"pricing_coalition": -1, "tax_coalition": 0, "settlement_coalition": -1},
        )
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(
            audit["phase_2_two_times_shapley"],
            {"pricing_coalition": -2, "tax_coalition": 0, "settlement_coalition": 0},
        )
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(
            audit["phase_3_two_times_shapley"],
            {"pricing_coalition": 0, "tax_coalition": 0, "settlement_coalition": 0},
        )

    def test_coalitional_campaign_and_tamper_evident_replay(self) -> None:
        def stub_coalitional_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Locked legacy fee-basis floor 1000 cents conflicts with net_cents 900."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_COALITION_SOURCE,
                        "worker-1": CANONICAL_TAX_COALITION_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_COALITION_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "coalitional",
                "seeds": [9600, 9601, 9602],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_coalitional_transport)
            summary = coalitional_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.coalitional_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on coalitional gate grand_coalition_value field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["grand_coalition_value"] = int(gate_rec["grand_coalition_value"]) - 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_coalitional_pilot_evidence_replay_if_present(self) -> None:
        coal_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "coalitional_pilot_run"
            / "events.jsonl"
        )
        coal_summary = coal_events.with_name("summary.json")
        if coal_events.exists() and coal_summary.exists():
            replayed = replay(coal_events)
            self.assertEqual(replayed["schema"], "lggr.coalitional_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_mayer_vietoris_workspace_and_monitor_detects_disconnected_overlap_jump(self) -> None:
        state = mv_fixture(9702)  # disconnected_overlap_coboundary_jump (9702 % 3 == 0)
        ws = MayerVietorisCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_mv": True, "tax_mv": True, "settlement_mv": True},
        )

        mon = StreamingCodebaseMayerVietorisMonitor(scope_id="unit-mv-gate")
        rec = mon.evaluate_codebase_mayer_vietoris(
            "eval-9702-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertTrue(rec["u_locally_exact"])
        self.assertTrue(rec["v_locally_exact"])
        self.assertFalse(rec["union_globally_exact"])
        self.assertEqual(rec["fu_w1_cents"], 1110)
        self.assertEqual(rec["fv_w1_cents"], 1050)
        self.assertEqual(rec["coboundary_spread_cents"], 60)
        self.assertEqual(rec["status"], "MAYER_VIETORIS_DISCONNECTED_OVERLAP_OBSTRUCTION_LGGR")

        audit = mon.record_three_phase_codebase_mayer_vietoris_audit("mv-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_1_coboundary_spread_cents"], 60)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_coboundary_spread_cents"], 30)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_coboundary_spread_cents"], 0)
        self.assertTrue(audit["phase_3_union_globally_exact"])

    def test_mayer_vietoris_campaign_and_tamper_evident_replay(self) -> None:
        def stub_mv_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Subswarm U is locked at eur_clearing_delta_cents=210 (f_U(w1)=1110 != 1080)."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_MV_SOURCE,
                        "worker-1": CANONICAL_TAX_MV_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_MV_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "mayer_vietoris",
                "seeds": [9700, 9701, 9702],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_mv_transport)
            summary = mv_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.mayer_vietoris_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on Mayer-Vietoris gate coboundary_spread_cents field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["coboundary_spread_cents"] = int(gate_rec["coboundary_spread_cents"]) + 10
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_mayer_vietoris_pilot_evidence_replay_if_present(self) -> None:
        mv_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "mayer_vietoris_pilot_run"
            / "events.jsonl"
        )
        mv_summary = mv_events.with_name("summary.json")
        if mv_events.exists() and mv_summary.exists():
            replayed = replay(mv_events)
            self.assertEqual(replayed["schema"], "lggr.mayer_vietoris_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_windowed_drift_workspace_and_monitor_detects_horizon_breach(self) -> None:
        state = win_fixture(9801)  # unrebalanced_sliding_window_rounding_drift (9801 % 3 == 0)
        ws = WindowedDriftCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_win": True, "tax_win": True, "settlement_win": True},
        )

        mon = StreamingCodebaseWindowedDriftMonitor(scope_id="unit-win-gate")
        rec = mon.evaluate_codebase_windowed_drift(
            "eval-9801-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["max_window_sum_cents"], 2)
        self.assertEqual(rec["max_prefix_drift_cents"], 6)
        self.assertEqual(rec["terminal_drift_cents"], 6)
        self.assertEqual(rec["status"], "SLIDING_WINDOW_HORIZON_BREACH_LGGR")

        audit = mon.record_three_phase_codebase_windowed_drift_audit("win-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_1_max_prefix_drift_cents"], 6)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_max_prefix_drift_cents"], 4)
        self.assertEqual(audit["phase_2_terminal_drift_cents"], 2)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_max_prefix_drift_cents"], 1)
        self.assertEqual(audit["phase_3_terminal_drift_cents"], 0)

    def test_windowed_drift_campaign_and_tamper_evident_replay(self) -> None:
        def stub_win_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Upstream modules locked at [1, 1], causing prefix drift 4 > 3 at epoch 4."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_WIN_SOURCE,
                        "worker-1": CANONICAL_TAX_WIN_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_WIN_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "windowed_drift",
                "seeds": [9800, 9801, 9802],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_win_transport)
            summary = win_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.windowed_drift_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on windowed_drift gate max_prefix_drift_cents field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["max_prefix_drift_cents"] = int(gate_rec["max_prefix_drift_cents"]) + 2
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_windowed_drift_pilot_evidence_replay_if_present(self) -> None:
        win_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "windowed_drift_pilot_run"
            / "events.jsonl"
        )
        win_summary = win_events.with_name("summary.json")
        if win_events.exists() and win_summary.exists():
            replayed = replay(win_events)
            self.assertEqual(replayed["schema"], "lggr.windowed_drift_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_optional_stopping_workspace_and_monitor_detects_tail_drawdown_breach(self) -> None:
        state = stop_fixture(9900)  # double_down_recovery_stake_tail_drawdown (9900 % 3 == 0)
        ws = OptionalStoppingCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_stop": True, "tax_stop": True, "settlement_stop": True},
        )

        mon = StreamingCodebaseOptionalStoppingMonitor(scope_id="unit-stop-gate")
        rec = mon.evaluate_codebase_optional_stopping(
            "eval-9900-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["stopped_expectation_cents"], 0)
        self.assertEqual(rec["tail_drawdown_cents"], 300)
        self.assertFalse(rec["stop_on_step1_down"])
        self.assertEqual(rec["status"], "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR")

        audit = mon.record_three_phase_codebase_optional_stopping_audit("stop-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_1_tail_drawdown_cents"], 300)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_2_tail_drawdown_cents"], 200)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_tail_drawdown_cents"], 100)
        self.assertEqual(audit["phase_3_stopped_expectation_cents"], 0)

    def test_optional_stopping_campaign_and_tamper_evident_replay(self) -> None:
        def stub_stop_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_msg = messages[0]["content"]
            worker = sys_msg.split("agent ")[1].split(",")[0]
            if messages[-1]["role"] == "user":
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                inspected = json.loads(messages[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "settlement_stop is locked at x_dd=-300, exceeding tail drawdown cap 100."}
                            ),
                        },
                    }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_STOP_SOURCE,
                        "worker-1": CANONICAL_TAX_STOP_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_STOP_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "optional_stopping",
                "seeds": [9900, 9901, 9902],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_stop_transport)
            summary = stop_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.optional_stopping_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on optional_stopping gate tail_drawdown_cents field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["tail_drawdown_cents"] = int(gate_rec["tail_drawdown_cents"]) + 50
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_optional_stopping_pilot_evidence_replay_if_present(self) -> None:
        stop_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "optional_stopping_pilot_run"
            / "events.jsonl"
        )
        stop_summary = stop_events.with_name("summary.json")
        if stop_events.exists() and stop_summary.exists():
            replayed = replay(stop_events)
            self.assertEqual(replayed["schema"], "lggr.optional_stopping_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 3)

    def test_cptp_channel_workspace_and_monitor_detects_state_blindspot_and_completes_operator(self) -> None:
        state = cptp_fixture(10000)
        ws = CPTPChannelCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_channel": True, "tax_channel": True, "settlement_channel": True},
        )

        mon = StreamingCodebaseCPTPChannelMonitor(scope_id="unit-cptp-gate")
        rec = mon.evaluate_codebase_cptp_channel(
            "eval-10000-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["k0_diag"], 1)
        self.assertEqual(rec["k1_diag"], 0)
        self.assertEqual(rec["k2_diag"], 0)
        self.assertEqual(rec["residual_l1_norm"], 2)
        self.assertEqual(rec["trace_discrepancy_rho0"], 0)
        self.assertEqual(rec["trace_discrepancy_rho1"], -1)
        self.assertEqual(rec["trace_discrepancy_rho2"], -1)
        self.assertEqual(rec["status"], "CPTP_STATE_BLINDSPOT_NON_TP_LGGR")

        audit = mon.record_three_phase_codebase_cptp_audit("cptp-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_status"], "CODEBASE_CPTP_OPERATOR_COMPLETE_LGGG")

    def test_cptp_channel_campaign_and_deterministic_replay(self) -> None:
        def stub_cptp_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}" in sys_text:
                    worker = w
                    break
            arm = "A"
            if "Arm B" in sys_text:
                arm = "B"
            elif "Arm C" in sys_text:
                arm = "C"

            has_tool_result = any(m.get("role") == "tool" for m in messages)
            if not has_tool_result:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
                last_user = json.loads(user_msgs[-1])
                if last_user.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible CPTP Kraus channel completion lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_Result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                    inspected = json.loads(tool_Result_msg["content"])
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": CANONICAL_TAX_CHANNEL_SOURCE}),
                            },
                        }
                    else:
                        tool_Result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                        inspected = json.loads(tool_Result_msg["content"])
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_CHANNEL_SOURCE,
                        "worker-1": CANONICAL_TAX_CHANNEL_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_CHANNEL_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "cptp",
                "seeds": [10000, 10001],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_cptp_transport)
            summary = cptp_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.cptp_channel_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on CPTP gate residual_l1_norm field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["residual_l1_norm"] = int(gate_rec["residual_l1_norm"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_cptp_pilot_evidence_replay_if_present(self) -> None:
        cptp_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "cptp_pilot_run"
            / "events.jsonl"
        )
        cptp_summary = cptp_events.with_name("summary.json")
        if cptp_events.exists() and cptp_summary.exists():
            replayed = replay(cptp_events)
            self.assertEqual(replayed["schema"], "lggr.cptp_channel_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_regge_holonomy_workspace_and_monitor_detects_hinge_deficit_and_flattens_star(self) -> None:
        state = regge_fixture(10100)
        ws = ReggeHolonomyCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_mesh": True, "tax_mesh": True, "settlement_mesh": True},
        )

        mon = StreamingCodebaseReggeHolonomyMonitor(scope_id="unit-regge-gate")
        rec = mon.evaluate_codebase_regge_holonomy(
            "eval-10100-wave0",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec["local_green"], 1)
        self.assertEqual(rec["global_green"], 0)
        self.assertEqual(rec["defect"], -1)
        self.assertEqual(rec["t0_angles_units"], [12, 3, 3])
        self.assertEqual(rec["t1_angles_units"], [6, 6, 6])
        self.assertEqual(rec["t2_angles_units"], [6, 6, 6])
        self.assertEqual(rec["apex_deficit_units"], 12)
        self.assertEqual(rec["boundary_turn_sum_units"], 24)
        self.assertTrue(rec["gauss_bonnet_equals_euler"])
        self.assertEqual(rec["status"], "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR")

        audit = mon.record_three_phase_codebase_regge_audit("regge-3phase-unit")
        self.assertEqual(audit["phase_1_defect"], -1)
        self.assertEqual(audit["phase_2_defect"], -1)
        self.assertEqual(audit["phase_3_defect"], 0)
        self.assertEqual(audit["phase_3_status"], "CODEBASE_REGGE_HOLONOMY_FLAT_LGGG")

    def test_regge_holonomy_campaign_and_deterministic_replay(self) -> None:
        def stub_regge_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}" in sys_text:
                    worker = w
                    break
            arm = "A"
            if "Arm B" in sys_text:
                arm = "B"
            elif "Arm C" in sys_text:
                arm = "C"

            has_tool_result = any(m.get("role") == "tool" for m in messages)
            if not has_tool_result:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
                last_user = json.loads(user_msgs[-1])
                if last_user.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible Regge hinge-deficit curvature lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_Result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                    inspected = json.loads(tool_Result_msg["content"])
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": CANONICAL_TAX_MESH_SOURCE}),
                            },
                        }
                    else:
                        tool_Result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                        inspected = json.loads(tool_Result_msg["content"])
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": CANONICAL_PRICING_MESH_SOURCE,
                        "worker-1": CANONICAL_TAX_MESH_SOURCE,
                        "worker-2": CANONICAL_SETTLEMENT_MESH_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {"cost": "0.0001"},
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "regge",
                "seeds": [10100, 10101],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_regge_transport)
            summary = regge_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.regge_holonomy_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on Regge gate apex_deficit_units field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["apex_deficit_units"] = int(gate_rec["apex_deficit_units"]) + 6
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_regge_pilot_evidence_replay_if_present(self) -> None:
        regge_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "regge_pilot_run"
            / "events.jsonl"
        )
        regge_summary = regge_events.with_name("summary.json")
        if regge_events.exists() and regge_summary.exists():
            replayed = replay(regge_events)
            self.assertEqual(replayed["schema"], "lggr.regge_holonomy_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_kinduction_code_workspace_and_three_phase_monitor(self) -> None:
        fx = kinduction_fixture(10200)
        ws = KInductionCodeWorkspace(fx)
        verdicts = ws.local_verdicts()
        self.assertTrue(all(verdicts.values()))

        mon = StreamingCodebaseKInductionMonitor(scope_id="test-kinduction-swarm")
        p1 = mon.evaluate_codebase_k_induction(
            "p1",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(p1["local_green"], 1)
        self.assertEqual(p1["global_green"], 0)
        self.assertEqual(p1["defect"], -1)
        self.assertEqual(p1["status"], "K_INDUCTION_BOUNDED_HORIZON_ESCAPE_NGD_LGGR")
        self.assertIsNone(p1["tax_integral_root"])
        self.assertEqual(p1["settle_integral_root"], -1)
        self.assertEqual(p1["settle_depth4_overflow"], 8)

        # Phase 2: worker-1 stabilizes at x_* = 2, worker-2 still out-of-carrier x_* = -1
        res_t = ws.tool("worker-1", "submit_module_patch", {"source_code": KINDUCTION_TAX_SOUND_SOURCE})
        self.assertTrue(res_t["accepted"])
        p2 = mon.evaluate_codebase_k_induction(
            "p2",
            sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(p2["local_green"], 1)
        self.assertEqual(p2["global_green"], 0)
        self.assertEqual(p2["defect"], -1)
        self.assertEqual(p2["status"], "K_INDUCTION_OUT_OF_CARRIER_STEP_UNSOUND_LGGR")
        self.assertEqual(p2["tax_integral_root"], 2)
        self.assertEqual(p2["settle_depth4_overflow"], 8)

        # Phase 3: both workers stabilize at x_* = 2 in [0, 10]
        res_s = ws.tool("worker-2", "submit_module_patch", {"source_code": KINDUCTION_SETTLEMENT_SOUND_SOURCE})
        self.assertTrue(res_s["accepted"])
        p3 = mon.evaluate_codebase_k_induction(
            "p3",
            sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(p3["local_green"], 1)
        self.assertEqual(p3["global_green"], 1)
        self.assertEqual(p3["defect"], 0)
        self.assertEqual(p3["status"], "CODEBASE_K_INDUCTION_SOUND_LGGG")
        self.assertEqual(p3["settle_depth4_overflow"], 0)

    def test_kinduction_campaign_and_tamper_detection(self) -> None:
        def stub_kinduction_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}" in sys_text:
                    worker = w
                    break
            arm = "A"
            if "Arm B" in sys_text:
                arm = "B"
            elif "Arm C" in sys_text:
                arm = "C"

            has_tool_result = any(m.get("role") == "tool" for m in messages)
            if not has_tool_result:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
                last_user = json.loads(user_msgs[-1])
                if last_user.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible k-induction carrier lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                    inspected = json.loads(tool_result_msg["content"])
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": KINDUCTION_TAX_SOUND_SOURCE}),
                            },
                        }
                    else:
                        tool_result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                        inspected = json.loads(tool_result_msg["content"])
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": KINDUCTION_PRICING_SOURCE,
                        "worker-1": KINDUCTION_TAX_SOUND_SOURCE,
                        "worker-2": KINDUCTION_SETTLEMENT_SOUND_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "kinduction",
                "seeds": [10200, 10201],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_kinduction_transport)
            summary = kinduction_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.k_induction_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on kinduction gate settle_depth4_overflow field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["settle_depth4_overflow"] = int(gate_rec["settle_depth4_overflow"]) + 8
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_kinduction_pilot_evidence_replay_if_present(self) -> None:
        kinduction_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "kinduction_pilot_run"
            / "events.jsonl"
        )
        kinduction_summary = kinduction_events.with_name("summary.json")
        if kinduction_events.exists() and kinduction_summary.exists():
            replayed = replay(kinduction_events)
            self.assertEqual(replayed["schema"], "lggr.k_induction_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_jacobian_code_workspace_and_three_phase_monitor(self) -> None:
        fx = jacobian_fixture(10300)
        ws = JacobianCodeWorkspace(fx)
        verdicts = ws.local_verdicts()
        self.assertTrue(all(verdicts.values()))

        mon = StreamingCodebaseJacobianSoundnessMonitor(scope_id="test-jacobian-swarm")
        p1 = mon.evaluate_codebase_jacobian(
            "p1",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(p1["local_green"], 1)
        self.assertEqual(p1["global_green"], 0)
        self.assertEqual(p1["defect"], -1)
        self.assertEqual(p1["status"], "JACOBIAN_STEALTH_BLINDSPOT_NGD_LGGR")
        self.assertEqual(p1["true_l1_defect"], 2)
        self.assertEqual(p1["measured_l1_score"], 0)
        self.assertEqual(p1["realizable_blindspot_dim"], 1)

        # Phase 2: worker-1 aligns tax_state_s2 = 1, worker-2 retains redundant telemetry [1, 1, 0]
        res_t = ws.tool("worker-1", "submit_module_patch", {"source_code": JACOBIAN_TAX_ALIGNED_SOURCE})
        self.assertTrue(res_t["accepted"])
        p2 = mon.evaluate_codebase_jacobian(
            "p2",
            sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(p2["local_green"], 1)
        self.assertEqual(p2["global_green"], 0)
        self.assertEqual(p2["defect"], -1)
        self.assertEqual(p2["status"], "JACOBIAN_RANK_DEFICIENT_OBSERVER_LGGR")
        self.assertEqual(p2["true_l1_defect"], 0)
        self.assertEqual(p2["realizable_blindspot_dim"], 1)

        # Phase 3: worker-2 augments settle_telemetry_row = [0, 1, 0]
        res_s = ws.tool("worker-2", "submit_module_patch", {"source_code": JACOBIAN_SETTLEMENT_OBSERVABLE_SOURCE})
        self.assertTrue(res_s["accepted"])
        p3 = mon.evaluate_codebase_jacobian(
            "p3",
            sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(p3["local_green"], 1)
        self.assertEqual(p3["global_green"], 1)
        self.assertEqual(p3["defect"], 0)
        self.assertEqual(p3["status"], "CODEBASE_JACOBIAN_OBSERVABLE_LGGG")
        self.assertEqual(p3["realizable_blindspot_dim"], 0)

    def test_jacobian_campaign_and_tamper_detection(self) -> None:
        def stub_jacobian_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}" in sys_text:
                    worker = w
                    break
            arm = "A"
            if "Arm B" in sys_text:
                arm = "B"
            elif "Arm C" in sys_text:
                arm = "C"

            has_tool_result = any(m.get("role") == "tool" for m in messages)
            if not has_tool_result:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                inspected = json.loads(tool_result_msg["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible Jacobian blindspot lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": JACOBIAN_TAX_ALIGNED_SOURCE}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": JACOBIAN_PRICING_SOURCE,
                        "worker-1": JACOBIAN_TAX_ALIGNED_SOURCE,
                        "worker-2": JACOBIAN_SETTLEMENT_OBSERVABLE_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "jacobian",
                "seeds": [10300, 10301],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_jacobian_transport)
            summary = jacobian_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.jacobian_soundness_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on Jacobian gate realizable_blindspot_dim field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["realizable_blindspot_dim"] = int(gate_rec["realizable_blindspot_dim"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_jacobian_pilot_evidence_replay_if_present(self) -> None:
        jacobian_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "jacobian_pilot_run"
            / "events.jsonl"
        )
        jacobian_summary = jacobian_events.with_name("summary.json")
        if jacobian_events.exists() and jacobian_summary.exists():
            replayed = replay(jacobian_events)
            self.assertEqual(replayed["schema"], "lggr.jacobian_soundness_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_quorum_initial_fixture_is_local_green_global_red(self) -> None:
        state = quorum_fixture(10400)
        ws = BoundaryQuorumCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_quorum": True, "tax_quorum": True, "settlement_quorum": True},
        )
        mon = StreamingCodebaseBoundaryQuorumMonitor(scope_id="unit-quorum-init")
        rec1 = mon.evaluate_codebase_quorum(
            "eval-quorum-p1",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec1["local_green"], 1)
        self.assertEqual(rec1["global_green"], 0)
        self.assertEqual(rec1["defect"], -1)
        self.assertEqual(rec1["local_product"], 0)
        self.assertEqual(rec1["quorum_verdict"], 1)
        self.assertEqual(rec1["quorum_inflation"], 1)
        self.assertEqual(rec1["status"], "BOUNDARY_QUORUM_MASKED_DRIFT_NGD_LGGR")

        # Phase 2: align tax_quorum while settlement_quorum retains quorum_2_of_3 governance
        sources_p2 = dict(ws.state["sources"])
        sources_p2["tax_quorum"] = QUORUM_TAX_ALIGNED_SOURCE
        rec2 = mon.evaluate_codebase_quorum(
            "eval-quorum-p2",
            sources=sources_p2,
            local_test_results=verdicts,
        )
        self.assertEqual(rec2["local_green"], 1)
        self.assertEqual(rec2["global_green"], 0)
        self.assertEqual(rec2["defect"], -1)
        self.assertEqual(rec2["quorum_reserve_cents"], 9)
        self.assertEqual(rec2["status"], "BOUNDARY_QUORUM_UNVERIFIED_GATE_LGGR")

        # Phase 3: enforce strict_product governance in settlement_quorum
        sources_p3 = dict(sources_p2)
        sources_p3["settlement_quorum"] = QUORUM_SETTLEMENT_STRICT_SOURCE
        rec3 = mon.evaluate_codebase_quorum(
            "eval-quorum-p3",
            sources=sources_p3,
            local_test_results=verdicts,
        )
        self.assertEqual(rec3["local_green"], 1)
        self.assertEqual(rec3["global_green"], 1)
        self.assertEqual(rec3["defect"], 0)
        self.assertEqual(rec3["quorum_reserve_cents"], 0)
        self.assertEqual(rec3["status"], "CODEBASE_BOUNDARY_PRODUCT_COHERENT_LGGG")

    def test_quorum_campaign_and_tamper_detection(self) -> None:
        def stub_quorum_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}" in sys_text:
                    worker = w
                    break
            arm = "A"
            if "Arm B" in sys_text:
                arm = "B"
            elif "Arm C" in sys_text:
                arm = "C"

            has_tool_result = any(m.get("role") == "tool" for m in messages)
            if not has_tool_result:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                inspected = json.loads(tool_result_msg["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible quorum governance lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": QUORUM_TAX_ALIGNED_SOURCE}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": QUORUM_PRICING_SOURCE,
                        "worker-1": QUORUM_TAX_ALIGNED_SOURCE,
                        "worker-2": QUORUM_SETTLEMENT_STRICT_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "quorum",
                "seeds": [10400, 10401],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_quorum_transport)
            summary = quorum_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.boundary_quorum_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on quorum gate quorum_reserve_cents field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["quorum_reserve_cents"] = int(gate_rec["quorum_reserve_cents"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_quorum_pilot_evidence_replay_if_present(self) -> None:
        quorum_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "quorum_pilot_run"
            / "events.jsonl"
        )
        quorum_summary = quorum_events.with_name("summary.json")
        if quorum_events.exists() and quorum_summary.exists():
            replayed = replay(quorum_events)
            self.assertEqual(replayed["schema"], "lggr.boundary_quorum_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_lease_initial_fixture_is_local_green_global_red(self) -> None:
        state = lease_fixture(10500)
        ws = LeaseOverlapCodeWorkspace(state)
        verdicts = ws.local_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_lease": True, "tax_lease": True, "settlement_lease": True},
        )
        mon = StreamingCodebaseLeaseOverlapMonitor(scope_id="unit-lease-init")
        rec1 = mon.evaluate_codebase_lease(
            "eval-lease-p1",
            sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(rec1["local_green"], 1)
        self.assertEqual(rec1["global_green"], 0)
        self.assertEqual(rec1["defect"], -1)
        self.assertEqual(rec1["lease_windows"], [[0, 1], [0, 3], [0, 3]])
        self.assertEqual(rec1["fencing_tokens"], [1, 1, 1])
        self.assertEqual(rec1["peak_concurrent_drift"], 11)
        self.assertEqual(rec1["status"], "LEASE_OVERLAP_SPLIT_BRAIN_NGD_LGGR")

        # Phase 2: serialize tax_lease while settlement_lease retains concurrent start
        sources_p2 = dict(ws.state["sources"])
        sources_p2["tax_lease"] = LEASE_TAX_SERIALIZED_SOURCE
        rec2 = mon.evaluate_codebase_lease(
            "eval-lease-p2",
            sources=sources_p2,
            local_test_results=verdicts,
        )
        self.assertEqual(rec2["local_green"], 1)
        self.assertEqual(rec2["global_green"], 0)
        self.assertEqual(rec2["defect"], -1)
        self.assertEqual(rec2["lease_windows"], [[0, 1], [1, 2], [1, 4]])
        self.assertEqual(rec2["fencing_tokens"], [1, 2, 2])
        self.assertEqual(rec2["peak_concurrent_drift"], 7)
        self.assertEqual(rec2["status"], "LEASE_PARTIAL_FENCING_COLLISION_LGGR")

        # Phase 3: serialize settlement_lease with monotonic fencing token
        sources_p3 = dict(sources_p2)
        sources_p3["settlement_lease"] = LEASE_SETTLEMENT_SERIALIZED_SOURCE
        rec3 = mon.evaluate_codebase_lease(
            "eval-lease-p3",
            sources=sources_p3,
            local_test_results=verdicts,
        )
        self.assertEqual(rec3["local_green"], 1)
        self.assertEqual(rec3["global_green"], 1)
        self.assertEqual(rec3["defect"], 0)
        self.assertEqual(rec3["lease_windows"], [[0, 1], [1, 2], [2, 3]])
        self.assertEqual(rec3["fencing_tokens"], [1, 2, 3])
        self.assertEqual(rec3["peak_concurrent_drift"], 4)
        self.assertEqual(rec3["split_brain_reserve_cents"], 0)
        self.assertEqual(rec3["status"], "CODEBASE_LEASE_FENCING_SERIALIZED_LGGG")

    def test_lease_campaign_and_tamper_detection(self) -> None:
        def stub_lease_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}" in sys_text:
                    worker = w
                    break
            arm = "A"
            if "Arm B" in sys_text:
                arm = "B"
            elif "Arm C" in sys_text:
                arm = "C"

            has_tool_result = any(m.get("role") == "tool" for m in messages)
            if not has_tool_result:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_result_msg = [m for m in messages if m.get("role") == "tool"][-1]
                inspected = json.loads(tool_result_msg["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible lease overlap lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": LEASE_TAX_SERIALIZED_SOURCE}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": LEASE_PRICING_SOURCE,
                        "worker-1": LEASE_TAX_SERIALIZED_SOURCE,
                        "worker-2": LEASE_SETTLEMENT_SERIALIZED_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "lease",
                "seeds": [10500, 10502],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_lease_transport)
            summary = lease_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.lease_overlap_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on lease gate peak_concurrent_drift field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["peak_concurrent_drift"] = int(gate_rec["peak_concurrent_drift"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_lease_pilot_evidence_replay_if_present(self) -> None:
        lease_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "lease_pilot_run"
            / "events.jsonl"
        )
        lease_summary = lease_events.with_name("summary.json")
        if lease_events.exists() and lease_summary.exists():
            replayed = replay(lease_events)
            self.assertEqual(replayed["schema"], "lggr.lease_overlap_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_contextual_sheaf_hollow_triangle_vs_global_section_reconciled(self) -> None:
        state = sheaf_fixture(10602)
        ws = ContextualSheafCodeWorkspace(state)
        local_res = ws.local_verdicts()
        self.assertEqual(
            local_res,
            {"pricing_sheaf": True, "tax_sheaf": True, "settlement_sheaf": True},
        )

        monitor = StreamingCodebaseContextualSheafMonitor(scope_id="test-sheaf")
        obs1 = monitor.evaluate_sheaf_merge(
            "wave-0-contextual",
            module_sources=ws.state["sources"],
            local_test_results=local_res,
        )
        self.assertEqual(obs1["local_green"], 1)
        self.assertEqual(obs1["global_green"], 0)
        self.assertEqual(obs1["defect"], -1)
        self.assertEqual(obs1["q_bc_num"], 0)
        self.assertEqual(obs1["q_ca_num"], 0)
        self.assertEqual(obs1["scaled_gap_m4"], 2)
        self.assertEqual(obs1["contextuality_reserve_cents"], 11)
        self.assertEqual(obs1["merchant_payout_cents"], 862)
        self.assertEqual(obs1["status"], "CONTEXTUAL_SHEAF_HOLLOW_TRIANGLE_NGD_LGGR")
        self.assertEqual(
            obs1["compact_role_directives"]["worker-0"]["action"],
            "HOLD_ANCHOR_PAIRWISE_TABLE_AB",
        )
        self.assertEqual(
            obs1["compact_role_directives"]["worker-1"]["action"],
            "RECONCILE_TAX_PAIRWISE_TABLE_BC_Q1",
        )
        self.assertEqual(
            obs1["compact_role_directives"]["worker-2"]["action"],
            "RECONCILE_SETTLEMENT_PAIRWISE_TABLE_CA_Q1",
        )

        # Partial repair: tax_sheaf reconciles table_bc (q_bc_num = 1) while settlement_sheaf stays at q_ca_num = 0
        res_b = ws.tool("worker-1", "submit_module_patch", {"source_code": SHEAF_TAX_RECONCILED_SOURCE})
        self.assertTrue(res_b["accepted"])
        obs2 = monitor.evaluate_sheaf_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(obs2["local_green"], 1)
        self.assertEqual(obs2["global_green"], 0)
        self.assertEqual(obs2["defect"], -1)
        self.assertEqual(obs2["q_bc_num"], 1)
        self.assertEqual(obs2["q_ca_num"], 0)
        self.assertEqual(obs2["scaled_gap_m4"], 1)
        self.assertEqual(obs2["status"], "CONTEXTUAL_SHEAF_PARTIAL_RECONCILIATION_LGGR")

        # Full repair: settlement_sheaf reconciles table_ca (q_ca_num = 1, reserve = 0)
        res_c = ws.tool("worker-2", "submit_module_patch", {"source_code": SHEAF_SETTLEMENT_RECONCILED_SOURCE})
        self.assertTrue(res_c["accepted"])
        obs3 = monitor.evaluate_sheaf_merge(
            "wave-1-reconciled",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(obs3["local_green"], 1)
        self.assertEqual(obs3["global_green"], 1)
        self.assertEqual(obs3["defect"], 0)
        self.assertEqual(obs3["q_bc_num"], 1)
        self.assertEqual(obs3["q_ca_num"], 1)
        self.assertEqual(obs3["scaled_gap_m4"], 0)
        self.assertEqual(obs3["contextuality_reserve_cents"], 0)
        self.assertEqual(obs3["merchant_payout_cents"], 873)
        self.assertEqual(obs3["status"], "CODEBASE_CONTEXTUAL_SHEAF_RECONCILED_LGGG")

    def test_contextual_sheaf_sandbox_rejects_imports_and_failing_patches(self) -> None:
        bad_import = run_sheaf_local_unit_tests(
            "tax_sheaf",
            "import os\ndef tax_sheaf(pricing_quote, tax_rate_bps):\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = ContextualSheafCodeWorkspace(sheaf_fixture(10602))
        bad_patch = ws.tool(
            "worker-1",
            "submit_module_patch",
            {"source_code": "def tax_sheaf(pricing_quote, tax_rate_bps):\n    return {'tax_cents': 0}\n"},
        )
        self.assertFalse(bad_patch["accepted"])

        ws_locked = ContextualSheafCodeWorkspace(sheaf_fixture(10600))
        locked_patch = ws_locked.tool(
            "worker-1",
            "submit_module_patch",
            {"source_code": SHEAF_TAX_RECONCILED_SOURCE},
        )
        self.assertFalse(locked_patch["accepted"])

    def test_concurrent_sheaf_campaign_replay_and_tamper_detection(self) -> None:
        def stub_sheaf_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}," in sys_text:
                    worker = w
                    break
            arm = "A"
            for a in ("A", "B", "C"):
                if f"(Arm {a})" in sys_text:
                    arm = a
                    break

            has_tool_response = any(m.get("role") == "tool" for m in messages)
            if not has_tool_response:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msgs = [m for m in messages if m.get("role") == "tool"]
                inspected = json.loads(tool_msgs[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible hollow-triangle contextual sheaf lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": SHEAF_TAX_RECONCILED_SOURCE}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": SHEAF_PRICING_SOURCE,
                        "worker-1": SHEAF_TAX_RECONCILED_SOURCE,
                        "worker-2": SHEAF_SETTLEMENT_RECONCILED_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "contextuality",
                "seeds": [10602, 10600],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_sheaf_transport)
            summary = sheaf_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.contextual_sheaf_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on sheaf gate scaled_gap_m4 field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["scaled_gap_m4"] = int(gate_rec["scaled_gap_m4"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_contextuality_pilot_evidence_replay_if_present(self) -> None:
        sheaf_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "contextuality_pilot_run"
            / "events.jsonl"
        )
        sheaf_summary = sheaf_events.with_name("summary.json")
        if sheaf_events.exists() and sheaf_summary.exists():
            replayed = replay(sheaf_events)
            self.assertEqual(replayed["schema"], "lggr.contextual_sheaf_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_watcher_dropout_gram_blindspot_vs_full_rank_restoration(self) -> None:
        state = gram_fixture(10700)
        ws = WatcherDropoutCodeWorkspace(state)
        local_res = ws.local_verdicts()
        self.assertEqual(
            local_res,
            {"pricing_gram": True, "tax_gram": True, "settlement_gram": True},
        )

        monitor = StreamingCodebaseWatcherDropoutMonitor(scope_id="test-gram")
        obs1 = monitor.evaluate_gram_merge(
            "wave-0-dropout",
            module_sources=ws.state["sources"],
            local_test_results=local_res,
        )
        self.assertEqual(obs1["local_green"], 1)
        self.assertEqual(obs1["global_green"], 0)
        self.assertEqual(obs1["defect"], -1)
        self.assertEqual(obs1["gram_rank"], 2)
        self.assertEqual(obs1["nullspace_dim"], 1)
        self.assertEqual(obs1["crit_norm_squared"], 0)
        self.assertEqual(obs1["dropout_reserve_cents"], 12)
        self.assertEqual(obs1["merchant_payout_cents"], 861)
        self.assertEqual(obs1["status"], "WATCHER_DROPOUT_GRAM_BLINDSPOT_NGD_LGGR")
        self.assertEqual(
            obs1["compact_role_directives"]["worker-0"]["action"],
            "HOLD_ANCHOR_PRICING_WATCHER_ROW_110",
        )
        self.assertEqual(
            obs1["compact_role_directives"]["worker-1"]["action"],
            "RESTORE_TAX_WATCHER_ROW_011",
        )
        self.assertEqual(
            obs1["compact_role_directives"]["worker-2"]["action"],
            "RESTORE_SETTLEMENT_CRITICAL_WATCHER_ROW_101",
        )

        # Partial repair: tax_gram updates row to [0, 1, 1] while settlement_gram stays at [0, 1, 1]
        res_b = ws.tool("worker-1", "submit_module_patch", {"source_code": GRAM_TAX_RESTORED_SOURCE})
        self.assertTrue(res_b["accepted"])
        obs2 = monitor.evaluate_gram_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(obs2["local_green"], 1)
        self.assertEqual(obs2["global_green"], 0)
        self.assertEqual(obs2["defect"], -1)
        self.assertEqual(obs2["gram_rank"], 2)
        self.assertEqual(obs2["nullspace_dim"], 1)
        self.assertEqual(obs2["crit_norm_squared"], 0)
        self.assertEqual(obs2["status"], "WATCHER_DROPOUT_PARTIAL_ROW_COLLISION_LGGR")

        # Full repair: settlement_gram restores critical row [1, 0, 1] and reserve = 0
        res_c = ws.tool("worker-2", "submit_module_patch", {"source_code": GRAM_SETTLEMENT_RESTORED_SOURCE})
        self.assertTrue(res_c["accepted"])
        obs3 = monitor.evaluate_gram_merge(
            "wave-1-restored",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_verdicts(),
        )
        self.assertEqual(obs3["local_green"], 1)
        self.assertEqual(obs3["global_green"], 1)
        self.assertEqual(obs3["defect"], 0)
        self.assertEqual(obs3["gram_rank"], 3)
        self.assertEqual(obs3["nullspace_dim"], 0)
        self.assertEqual(obs3["crit_norm_squared"], 4)
        self.assertEqual(obs3["dropout_reserve_cents"], 0)
        self.assertEqual(obs3["merchant_payout_cents"], 873)
        self.assertEqual(obs3["status"], "CODEBASE_WATCHER_GRAM_FULL_RANK_RESTORED_LGGG")

    def test_watcher_dropout_sandbox_rejects_imports_and_failing_patches(self) -> None:
        bad_import = run_gram_local_unit_tests(
            "tax_gram",
            "import os\ndef tax_gram(pricing_quote, tax_rate_bps):\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = WatcherDropoutCodeWorkspace(gram_fixture(10700))
        bad_patch = ws.tool(
            "worker-1",
            "submit_module_patch",
            {"source_code": "def tax_gram(pricing_quote, tax_rate_bps):\n    return {'tax_cents': 0}\n"},
        )
        self.assertFalse(bad_patch["accepted"])

        ws_locked = WatcherDropoutCodeWorkspace(gram_fixture(10701))
        locked_patch = ws_locked.tool(
            "worker-1",
            "submit_module_patch",
            {"source_code": GRAM_TAX_RESTORED_SOURCE},
        )
        self.assertFalse(locked_patch["accepted"])

    def test_concurrent_gram_campaign_replay_and_tamper_detection(self) -> None:
        def stub_gram_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_text = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"agent {w}," in sys_text:
                    worker = w
                    break
            arm = "A"
            for a in ("A", "B", "C"):
                if f"(Arm {a})" in sys_text:
                    arm = a
                    break

            has_tool_response = any(m.get("role") == "tool" for m in messages)
            if not has_tool_response:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msgs = [m for m in messages if m.get("role") == "tool"]
                inspected = json.loads(tool_msgs[-1]["content"])
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Infeasible watcher-dropout Gram blindspot lock."}
                            ),
                        },
                    }
                elif arm == "A":
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif arm == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": GRAM_TAX_RESTORED_SOURCE}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": GRAM_PRICING_SOURCE,
                        "worker-1": GRAM_TAX_RESTORED_SOURCE,
                        "worker-2": GRAM_SETTLEMENT_RESTORED_SOURCE,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "gram_dropout",
                "seeds": [10700, 10701],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_gram_transport)
            summary = gram_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.watcher_dropout_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            # Tamper check on gram gate gram_rank field
            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["gram_rank"] = int(gate_rec["gram_rank"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_gram_dropout_pilot_evidence_replay_if_present(self) -> None:
        gram_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "gram_dropout_pilot_run"
            / "events.jsonl"
        )
        gram_summary = gram_events.with_name("summary.json")
        if gram_events.exists() and gram_summary.exists():
            replayed = replay(gram_events)
            self.assertEqual(replayed["schema"], "lggr.watcher_dropout_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_policy_reversal_local_green_global_red_and_dual_metric_repair(self) -> None:
        ws = PolicyReversalCodeWorkspace(policy_fixture(10800))
        verdicts = ws.local_test_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_policy": True, "tax_policy": True, "settlement_policy": True},
        )

        mon = StreamingCodebasePolicyReversalMonitor(scope_id="test-policy-swarm")
        res0 = mon.evaluate_policy_merge(
            "wave-0",
            module_sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(res0["local_green"], 1)
        self.assertEqual(res0["global_green"], 0)
        self.assertEqual(res0["defect"], -1)
        self.assertEqual(res0["selected_policy_id"], "Q_5_8")
        self.assertEqual(res0["selected_neg_num"], 96)
        self.assertEqual(res0["policy_violation_surcharge_cents"], 16)
        self.assertTrue(res0["surrogate_two_bound_assumed"])

        # Partial repair: tax_policy enforces m-context bound, settlement_policy still CF-only
        p1 = ws.tool("worker-1", "submit_module_patch", {"source_code": POLICY_TAX_M_CONTEXT_SRC})
        self.assertTrue(p1["accepted"])
        res1 = mon.evaluate_policy_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res1["local_green"], 1)
        self.assertEqual(res1["global_green"], 0)
        self.assertEqual(res1["defect"], -1)
        self.assertFalse(res1["surrogate_two_bound_assumed"])
        self.assertEqual(res1["selected_policy_id"], "Q_5_8")

        # Full repair: settlement_policy selects Policy B ('p_star') via dual-metric (CF, N_min) audit
        p2 = ws.tool("worker-2", "submit_module_patch", {"source_code": POLICY_SETTLEMENT_DUAL_METRIC_SRC})
        self.assertTrue(p2["accepted"])
        res2 = mon.evaluate_policy_merge(
            "wave-1-repaired",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res2["local_green"], 1)
        self.assertEqual(res2["global_green"], 1)
        self.assertEqual(res2["defect"], 0)
        self.assertEqual(res2["selected_policy_id"], "p_star")
        self.assertEqual(res2["selected_neg_num"], 75)
        self.assertEqual(res2["policy_violation_surcharge_cents"], 0)
        self.assertEqual(res2["merchant_payout_cents"], 873)

    def test_policy_reversal_sandbox_rejects_imports_and_failing_patches(self) -> None:
        bad_import = run_policy_local_unit_tests(
            "tax_policy",
            "import os\ndef tax_policy(pricing_quote: dict, tax_rate_bps: int) -> dict:\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = PolicyReversalCodeWorkspace(policy_fixture(10801))
        locked_res = ws.tool("worker-1", "submit_module_patch", {"source_code": POLICY_TAX_M_CONTEXT_SRC})
        self.assertFalse(locked_res["accepted"])
        self.assertIn("locked", locked_res["error"])

    def test_policy_reversal_concurrent_campaign_and_tamper_evident_replay(self) -> None:
        def stub_policy_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_prompt = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"`{w}`" in sys_prompt:
                    worker = w
                    break
            has_tool_resp = any(m.get("role") == "tool" for m in messages)
            if not has_tool_resp:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msg = next(m for m in reversed(messages) if m.get("role") == "tool")
                inspected = json.loads(tool_msg["content"])
                fb = inspected.get("merge_gate_feedback", {})
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Tax and Settlement policy modules are hardware-locked under contradictory CF-only vs N_min ceiling constraints."}
                            ),
                        },
                    }
                elif fb.get("arm") == "A":
                    tool_call = {
                        "id": f"call_hold_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif fb.get("arm") == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": POLICY_TAX_M_CONTEXT_SRC}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_hold_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": POLICY_PRICING_ANCHOR_SRC,
                        "worker-1": POLICY_TAX_M_CONTEXT_SRC,
                        "worker-2": POLICY_SETTLEMENT_DUAL_METRIC_SRC,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "policy_reversal",
                "seeds": [10800, 10801],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_policy_transport)
            summary = policy_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.policy_reversal_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["selected_neg_num"] = int(gate_rec["selected_neg_num"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_policy_reversal_pilot_evidence_replay_if_present(self) -> None:
        policy_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "policy_reversal_pilot_run"
            / "events.jsonl"
        )
        policy_summary = policy_events.with_name("summary.json")
        if policy_events.exists() and policy_summary.exists():
            replayed = replay(policy_events)
            self.assertEqual(replayed["schema"], "lggr.policy_reversal_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_fiber_splitting_initial_fixture_is_local_green_global_red(self) -> None:
        state = split_fixture(10900)
        ws = FiberSplittingCodeWorkspace(state)
        verdicts = ws.local_test_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_split": True, "tax_split": True, "settlement_split": True},
        )

        mon = StreamingCodebaseFiberSplittingMonitor(scope_id="test-split-swarm")
        res0 = mon.evaluate_split_merge(
            "wave-0",
            module_sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(res0["local_green"], 1)
        self.assertEqual(res0["global_green"], 0)
        self.assertEqual(res0["defect"], -1)
        self.assertEqual(res0["active_fiber_width"], 12)
        self.assertEqual(res0["active_minimax_floor"], 6)
        self.assertEqual(res0["worst_case_error"], 6)
        self.assertEqual(res0["ambiguity_surcharge_cents"], 6)
        self.assertEqual(res0["merchant_payout_cents"], 867)

        # Partial repair: tax_split adds 1-bit probe b_1(x), settlement_split still unassisted
        p1 = ws.tool("worker-1", "submit_module_patch", {"source_code": SPLIT_TAX_1BIT_SRC})
        self.assertTrue(p1["accepted"])
        res1 = mon.evaluate_split_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res1["local_green"], 1)
        self.assertEqual(res1["global_green"], 0)
        self.assertEqual(res1["defect"], -1)
        self.assertEqual(res1["active_fiber_width"], 4)
        self.assertEqual(res1["active_minimax_floor"], 2)

        # Full repair: settlement_split adds 2nd-bit probe b_2(x) and resolves all 4 states into singletons
        p2 = ws.tool("worker-2", "submit_module_patch", {"source_code": SPLIT_SETTLEMENT_FULL_SRC})
        self.assertTrue(p2["accepted"])
        res2 = mon.evaluate_split_merge(
            "wave-1-repaired",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res2["local_green"], 1)
        self.assertEqual(res2["global_green"], 1)
        self.assertEqual(res2["defect"], 0)
        self.assertEqual(res2["active_fiber_width"], 0)
        self.assertEqual(res2["active_minimax_floor"], 0)
        self.assertEqual(res2["worst_case_error"], 0)
        self.assertEqual(res2["ambiguity_surcharge_cents"], 0)
        self.assertEqual(res2["merchant_payout_cents"], 873)

    def test_fiber_splitting_sandbox_rejects_imports_and_failing_patches(self) -> None:
        bad_import = run_split_local_unit_tests(
            "tax_split",
            "import os\ndef tax_split(pricing_quote: dict, tax_rate_bps: int) -> dict:\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = FiberSplittingCodeWorkspace(split_fixture(10901))
        locked_res = ws.tool("worker-1", "submit_module_patch", {"source_code": SPLIT_TAX_1BIT_SRC})
        self.assertFalse(locked_res["accepted"])
        self.assertIn("locked", locked_res["error"])

    def test_fiber_splitting_concurrent_campaign_and_tamper_evident_replay(self) -> None:
        def stub_split_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_prompt = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"`{w}`" in sys_prompt:
                    worker = w
                    break
            has_tool_resp = any(m.get("role") == "tool" for m in messages)
            if not has_tool_resp:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msg = next(m for m in reversed(messages) if m.get("role") == "tool")
                inspected = json.loads(tool_msg["content"])
                fb = inspected.get("merge_gate_feedback", {})
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Tax and Settlement modules are hardware-locked to unassisted reflection without external probe bits."}
                            ),
                        },
                    }
                elif fb.get("arm") == "A":
                    tool_call = {
                        "id": f"call_hold_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif fb.get("arm") == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": SPLIT_TAX_1BIT_SRC}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_hold_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": SPLIT_PRICING_ANCHOR_SRC,
                        "worker-1": SPLIT_TAX_1BIT_SRC,
                        "worker-2": SPLIT_SETTLEMENT_FULL_SRC,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "fiber_splitting",
                "seeds": [10900, 10901],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_split_transport)
            summary = split_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.fiber_splitting_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["active_fiber_width"] = int(gate_rec["active_fiber_width"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_fiber_splitting_pilot_evidence_replay_if_present(self) -> None:
        split_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "fiber_splitting_pilot_run"
            / "events.jsonl"
        )
        split_summary = split_events.with_name("summary.json")
        if split_events.exists() and split_summary.exists():
            replayed = replay(split_events)
            self.assertEqual(replayed["schema"], "lggr.fiber_splitting_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_disagreement_council_initial_fixture_is_local_green_global_red(self) -> None:
        state = council_fixture(11000)
        ws = DisagreementCouncilCodeWorkspace(state)
        verdicts = ws.local_test_verdicts()
        self.assertEqual(
            verdicts,
            {"pricing_council": True, "tax_council": True, "settlement_council": True},
        )

        mon = StreamingCodebaseDisagreementCouncilMonitor(scope_id="test-council-swarm")
        res0 = mon.evaluate_council_merge(
            "wave-0",
            module_sources=ws.state["sources"],
            local_test_results=verdicts,
        )
        self.assertEqual(res0["local_green"], 1)
        self.assertEqual(res0["global_green"], 0)
        self.assertEqual(res0["defect"], -1)
        self.assertEqual(res0["active_collision_floor"], 2)
        self.assertEqual(res0["poe_partition_sum"], "0")
        self.assertEqual(res0["council_collision_surcharge_cents"], 10)
        self.assertEqual(res0["merchant_payout_cents"], 863)

        # Partial repair: tax_council and settlement_council emit binary symbols [0, 0, 1] (S_bin=2 < K=3, surcharge=5)
        binary_settlement_src = COUNCIL_SETTLEMENT_COLLAPSING_SRC.replace("[0, 0, 0]", "[0, 0, 1]").replace(
            "surcharge = 10", "surcharge = 5"
        )
        p1 = ws.tool("worker-1", "submit_module_patch", {"source_code": COUNCIL_TAX_BINARY_SRC})
        self.assertTrue(p1["accepted"])
        p1_s = ws.tool("worker-2", "submit_module_patch", {"source_code": binary_settlement_src})
        self.assertTrue(p1_s["accepted"])
        res1 = mon.evaluate_council_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res1["local_green"], 1)
        self.assertEqual(res1["global_green"], 0)
        self.assertEqual(res1["defect"], -1)
        self.assertEqual(res1["active_collision_floor"], 1)
        self.assertEqual(res1["council_collision_surcharge_cents"], 5)
        self.assertEqual(res1["merchant_payout_cents"], 868)
        self.assertEqual(res1["status"], "BINARY_TAG_CODEBASE_CAPACITY_DEFICIT_LGGR")

        # Full repair: settlement_council emits S=3 disagreement-preserving council symbols [0, 1, 2]
        p2 = ws.tool("worker-2", "submit_module_patch", {"source_code": COUNCIL_SETTLEMENT_FULL_SRC})
        self.assertTrue(p2["accepted"])
        res2 = mon.evaluate_council_merge(
            "wave-1-repaired",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res2["local_green"], 1)
        self.assertEqual(res2["global_green"], 1)
        self.assertEqual(res2["defect"], 0)
        self.assertEqual(res2["active_collision_floor"], 0)
        self.assertEqual(res2["poe_partition_sum"], "3/8")
        self.assertEqual(res2["council_collision_surcharge_cents"], 0)
        self.assertEqual(res2["merchant_payout_cents"], 873)

    def test_disagreement_council_sandbox_rejects_imports_and_failing_patches(self) -> None:
        bad_import = run_council_local_unit_tests(
            "tax_council",
            "import os\ndef tax_council(pricing_quote: dict, tax_rate_bps: int) -> dict:\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = DisagreementCouncilCodeWorkspace(council_fixture(11001))
        locked_res = ws.tool("worker-1", "submit_module_patch", {"source_code": COUNCIL_TAX_BINARY_SRC})
        self.assertFalse(locked_res["accepted"])
        self.assertIn("locked", locked_res["error"])

    def test_disagreement_council_concurrent_campaign_and_tamper_evident_replay(self) -> None:
        def stub_council_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_prompt = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"`{w}`" in sys_prompt:
                    worker = w
                    break
            has_tool_resp = any(m.get("role") == "tool" for m in messages)
            if not has_tool_resp:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msg = next(m for m in reversed(messages) if m.get("role") == "tool")
                inspected = json.loads(tool_msg["content"])
                fb = inspected.get("merge_gate_feedback", {})
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Tax and Settlement council modules are hardware-locked to collapsing scalar consensus [0, 0, 0]."}
                            ),
                        },
                    }
                elif fb.get("arm") == "A":
                    tool_call = {
                        "id": f"call_hold_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif fb.get("arm") == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": COUNCIL_TAX_BINARY_SRC}),
                            },
                        }
                    elif worker == "worker-2":
                        binary_settlement_src = COUNCIL_SETTLEMENT_COLLAPSING_SRC.replace(
                            "[0, 0, 0]", "[0, 0, 1]"
                        ).replace("surcharge = 10", "surcharge = 5")
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": binary_settlement_src}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_hold_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": COUNCIL_PRICING_ANCHOR_SRC,
                        "worker-1": COUNCIL_TAX_BINARY_SRC,
                        "worker-2": COUNCIL_SETTLEMENT_FULL_SRC,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "council",
                "seeds": [11000, 11001],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_council_transport)
            summary = council_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.disagreement_council_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["active_collision_floor"] = int(gate_rec["active_collision_floor"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_disagreement_council_pilot_evidence_replay_if_present(self) -> None:
        council_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "council_pilot_run"
            / "events.jsonl"
        )
        council_summary = council_events.with_name("summary.json")
        if council_events.exists() and council_summary.exists():
            replayed = replay(council_events)
            self.assertEqual(replayed["schema"], "lggr.disagreement_council_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_six_role_initial_fixture_is_local_green_global_red(self) -> None:
        """Verify initial six-role fixture is Local Green / Global Red and repairs across phases."""
        ws = SixRoleDeduplicationCodeWorkspace(six_role_fixture(11100))
        mon = StreamingCodebaseSixRoleDeduplicationMonitor(scope_id="test-six-role-unit")
        res0 = mon.evaluate_six_role_merge(
            "wave-0",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res0["local_green"], 1)
        self.assertEqual(res0["global_green"], 0)
        self.assertEqual(res0["defect"], -1)
        self.assertEqual(res0["verdict_drift_count"], 1)
        self.assertEqual(res0["double_counted_entries_active"], 3)
        self.assertEqual(res0["role_dedup_surcharge_cents"], 20)
        self.assertEqual(res0["merchant_payout_cents"], 853)
        self.assertEqual(res0["status"], "CROSS_ROLE_VERDICT_DRIFT_AND_DOUBLE_COUNT_LGGR")

        # Partial repair: tax_role preserves verdict triple (drift=0), settlement_role still un-deduplicated (surcharge=15)
        p1 = ws.tool("worker-1", "submit_module_patch", {"source_code": ROLE_TAX_PRESERVED_SRC})
        self.assertTrue(p1["accepted"])
        p1_s = ws.tool("worker-2", "submit_module_patch", {"source_code": ROLE_SETTLEMENT_RAW_P2_SRC})
        self.assertTrue(p1_s["accepted"])
        res1 = mon.evaluate_six_role_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res1["local_green"], 1)
        self.assertEqual(res1["global_green"], 0)
        self.assertEqual(res1["defect"], -1)
        self.assertEqual(res1["verdict_drift_count"], 0)
        self.assertEqual(res1["double_counted_entries_active"], 3)
        self.assertEqual(res1["role_dedup_surcharge_cents"], 15)
        self.assertEqual(res1["merchant_payout_cents"], 858)
        self.assertEqual(res1["status"], "SHARED_TRACE_DOUBLE_COUNT_MASKING_LGGR")

        # Full repair: settlement_role enables trace-ID deduplication with surcharge=0
        p2 = ws.tool("worker-2", "submit_module_patch", {"source_code": ROLE_SETTLEMENT_DEDUP_SRC})
        self.assertTrue(p2["accepted"])
        res2 = mon.evaluate_six_role_merge(
            "wave-1-repaired",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res2["local_green"], 1)
        self.assertEqual(res2["global_green"], 1)
        self.assertEqual(res2["defect"], 0)
        self.assertEqual(res2["verdict_drift_count"], 0)
        self.assertEqual(res2["double_counted_entries_active"], 0)
        self.assertEqual(res2["role_dedup_surcharge_cents"], 0)
        self.assertEqual(res2["merchant_payout_cents"], 873)
        self.assertEqual(res2["status"], "CODEBASE_SIX_ROLE_DEDUPLICATED_COHERENT_LGGG")

    def test_six_role_sandbox_rejects_imports_and_failing_patches(self) -> None:
        """Verify six-role sandbox rejects forbidden imports and hardware-locked patches."""
        bad_import = run_six_role_local_unit_tests(
            "tax_role",
            "import os\ndef tax_role(pricing_quote: dict, tax_rate_bps: int) -> dict:\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = SixRoleDeduplicationCodeWorkspace(six_role_fixture(11101))
        locked_res = ws.tool("worker-1", "submit_module_patch", {"source_code": ROLE_TAX_PRESERVED_SRC})
        self.assertFalse(locked_res["accepted"])
        self.assertIn("locked", locked_res["error"])

    def test_six_role_concurrent_campaign_and_tamper_evident_replay(self) -> None:
        """Verify 3-arm six-role concurrent campaign, deterministic replay, and tamper detection."""
        def stub_six_role_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_prompt = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"`{w}`" in sys_prompt:
                    worker = w
                    break
            has_tool_resp = any(m.get("role") == "tool" for m in messages)
            if not has_tool_resp:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msg = next(m for m in reversed(messages) if m.get("role") == "tool")
                inspected = json.loads(tool_msg["content"])
                fb = inspected.get("merge_gate_feedback", {})
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Tax and Settlement six-role modules are hardware-locked to drifting un-deduplicated role logs."}
                            ),
                        },
                    }
                elif fb.get("arm") == "A":
                    tool_call = {
                        "id": f"call_hold_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif fb.get("arm") == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": ROLE_TAX_PRESERVED_SRC}),
                            },
                        }
                    elif worker == "worker-2":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": ROLE_SETTLEMENT_RAW_P2_SRC}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_hold_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": ROLE_PRICING_ANCHOR_SRC,
                        "worker-1": ROLE_TAX_PRESERVED_SRC,
                        "worker-2": ROLE_SETTLEMENT_DEDUP_SRC,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "six_role",
                "seeds": [11100, 11101],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_six_role_transport)
            summary = six_role_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.six_role_deduplication_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["double_counted_entries_active"] = int(gate_rec["double_counted_entries_active"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_six_role_pilot_evidence_replay_if_present(self) -> None:
        """Replay live six-role pilot evidence offline if present."""
        six_role_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "six_role_pilot_run"
            / "events.jsonl"
        )
        six_role_summary = six_role_events.with_name("summary.json")
        if six_role_events.exists() and six_role_summary.exists():
            replayed = replay(six_role_events)
            self.assertEqual(replayed["schema"], "lggr.six_role_deduplication_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)

    def test_path_kernel_initial_fixture_is_local_green_global_red(self) -> None:
        """Verify initial path-kernel fixture is Local Green / Global Red and repairs across phases."""
        ws = PathKernelDashboardCodeWorkspace(path_kernel_fixture(11200))
        mon = StreamingCodebasePathKernelDashboardMonitor(scope_id="test-path-kernel-unit")
        res0 = mon.evaluate_path_kernel_merge(
            "wave-0",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res0["local_green"], 1)
        self.assertEqual(res0["global_green"], 0)
        self.assertEqual(res0["defect"], -1)
        self.assertEqual(res0["egd_count"], 2)
        self.assertEqual(res0["evaluator_residual_re"], 0)
        self.assertEqual(res0["kernel_discrepancy_surcharge_cents"], 10)
        self.assertEqual(res0["merchant_payout_cents"], 863)
        self.assertEqual(res0["status"], "CANCELLATION_MASKED_STAGE_KERNEL_CODEBASE_LGGR")

        # Partial repair: disable PGD fallback (egd=1, r_e=-1, surcharge=5)
        p1 = ws.tool("worker-1", "submit_module_patch", {"source_code": KERNEL_TAX_NO_FALLBACK_SRC})
        self.assertTrue(p1["accepted"])
        p1_s = ws.tool("worker-2", "submit_module_patch", {"source_code": KERNEL_SETTLEMENT_NGD_SRC})
        self.assertTrue(p1_s["accepted"])
        res1 = mon.evaluate_path_kernel_merge(
            "wave-1-partial",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res1["local_green"], 1)
        self.assertEqual(res1["global_green"], 0)
        self.assertEqual(res1["defect"], -1)
        self.assertEqual(res1["egd_count"], 1)
        self.assertEqual(res1["evaluator_residual_re"], -1)
        self.assertEqual(res1["kernel_discrepancy_surcharge_cents"], 5)
        self.assertEqual(res1["merchant_payout_cents"], 868)
        self.assertEqual(res1["status"], "NGD_INTEGRATION_REGRESSION_CODEBASE_LGGR")

        # Full repair: settlement_kernel repairs boundary E2E verdicts and enables 4-tuple dashboard
        p2 = ws.tool("worker-2", "submit_module_patch", {"source_code": KERNEL_SETTLEMENT_REPAIRED_SRC})
        self.assertTrue(p2["accepted"])
        res2 = mon.evaluate_path_kernel_merge(
            "wave-1-repaired",
            module_sources=ws.state["sources"],
            local_test_results=ws.local_test_verdicts(),
        )
        self.assertEqual(res2["local_green"], 1)
        self.assertEqual(res2["global_green"], 1)
        self.assertEqual(res2["defect"], 0)
        self.assertEqual(res2["egd_count"], 0)
        self.assertEqual(res2["evaluator_residual_re"], 0)
        self.assertEqual(res2["kernel_discrepancy_surcharge_cents"], 0)
        self.assertEqual(res2["merchant_payout_cents"], 873)
        self.assertEqual(res2["status"], "CODEBASE_PATH_KERNEL_DASHBOARD_COHERENT_LGGG")

    def test_path_kernel_sandbox_rejects_imports_and_failing_patches(self) -> None:
        """Verify path-kernel sandbox rejects forbidden imports and hardware-locked patches."""
        bad_import = run_path_kernel_local_unit_tests(
            "tax_kernel",
            "import os\ndef tax_kernel(pricing_quote: dict, tax_rate_bps: int) -> dict:\n    return {}\n",
        )
        self.assertFalse(bad_import["passed"])
        self.assertIn("forbidden_import", bad_import["error"])

        ws = PathKernelDashboardCodeWorkspace(path_kernel_fixture(11201))
        locked_res = ws.tool("worker-1", "submit_module_patch", {"source_code": KERNEL_TAX_NO_FALLBACK_SRC})
        self.assertFalse(locked_res["accepted"])
        self.assertIn("locked", locked_res["error"])

    def test_path_kernel_concurrent_campaign_and_tamper_evident_replay(self) -> None:
        """Verify 3-arm path-kernel concurrent campaign, deterministic replay, and tamper detection."""
        def stub_path_kernel_transport(payload: dict) -> dict:
            messages = payload["messages"]
            sys_prompt = messages[0]["content"]
            worker = "worker-0"
            for w in ("worker-0", "worker-1", "worker-2"):
                if f"`{w}`" in sys_prompt:
                    worker = w
                    break
            has_tool_resp = any(m.get("role") == "tool" for m in messages)
            if not has_tool_resp:
                tool_call = {
                    "id": f"call_inspect_{worker}",
                    "type": "function",
                    "function": {"name": "inspect_workspace", "arguments": "{}"},
                }
            else:
                tool_msg = next(m for m in reversed(messages) if m.get("role") == "tool")
                inspected = json.loads(tool_msg["content"])
                fb = inspected.get("merge_gate_feedback", {})
                if inspected.get("infeasible_constraint") is not None:
                    tool_call = {
                        "id": f"call_esc_{worker}",
                        "type": "function",
                        "function": {
                            "name": "escalate",
                            "arguments": json.dumps(
                                {"reason": "Tax and Settlement path-kernel modules are hardware-locked to PGD fallback cancellation masking."}
                            ),
                        },
                    }
                elif fb.get("arm") == "A":
                    tool_call = {
                        "id": f"call_hold_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": inspected["source_code"]}),
                        },
                    }
                elif fb.get("arm") == "B":
                    if worker == "worker-1":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": KERNEL_TAX_NO_FALLBACK_SRC}),
                            },
                        }
                    elif worker == "worker-2":
                        tool_call = {
                            "id": f"call_patch_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": KERNEL_SETTLEMENT_NGD_SRC}),
                            },
                        }
                    else:
                        tool_call = {
                            "id": f"call_hold_{worker}",
                            "type": "function",
                            "function": {
                                "name": "submit_module_patch",
                                "arguments": json.dumps({"source_code": inspected["source_code"]}),
                            },
                        }
                else:
                    canonical_map = {
                        "worker-0": KERNEL_PRICING_ANCHOR_SRC,
                        "worker-1": KERNEL_TAX_NO_FALLBACK_SRC,
                        "worker-2": KERNEL_SETTLEMENT_REPAIRED_SRC,
                    }
                    tool_call = {
                        "id": f"call_patch_{worker}",
                        "type": "function",
                        "function": {
                            "name": "submit_module_patch",
                            "arguments": json.dumps({"source_code": canonical_map[worker]}),
                        },
                    }
            return {
                "response": {
                    "model": payload["model"],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                        "cost": 0.0001,
                    },
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "tool_calls": [tool_call],
                            },
                        }
                    ],
                },
                "started_ns": 10,
                "finished_ns": 20,
            }

        with tempfile.TemporaryDirectory() as td:
            events_path = Path(td) / "events.jsonl"
            events = Events(events_path)
            config = {
                "topology": "path_kernel",
                "seeds": [11200, 11201],
                "models": CODE_SWARM_MODELS,
                "budget_usd": "0.50",
            }
            events.emit("start", {"config": config})
            client = CodeBatchClient(events, "0.50", transport=stub_path_kernel_transport)
            summary = path_kernel_campaign(client, events, config)
            (Path(td) / "summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )

            replayed = replay(events_path)
            self.assertEqual(replayed, summary)
            self.assertEqual(replayed["schema"], "lggr.path_kernel_dashboard_code_engineering_swarm.v1")
            self.assertEqual(replayed["max_inflight_requests"], 3)

            records = deepcopy(events.records)
            gate_rec = next(r["data"] for r in records if r["kind"] == "gate")
            gate_rec["egd_count"] = int(gate_rec["egd_count"]) + 1
            for i, r in enumerate(records):
                r["previous"] = records[i - 1]["sha256"] if i else None
                r["sha256"] = event_digest({k: v for k, v in r.items() if k != "sha256"})
            events_path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                replay(events_path)

    def test_live_path_kernel_pilot_evidence_replay_if_present(self) -> None:
        """Replay live path-kernel pilot evidence offline if present."""
        pk_events = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "concurrent_code_engineering_swarm"
            / "evidence"
            / "path_kernel_pilot_run"
            / "events.jsonl"
        )
        pk_summary = pk_events.with_name("summary.json")
        if pk_events.exists() and pk_summary.exists():
            replayed = replay(pk_events)
            self.assertEqual(replayed["schema"], "lggr.path_kernel_dashboard_code_engineering_swarm.v1")
            self.assertEqual(len(replayed["cases"]), 2)


if __name__ == "__main__":
    unittest.main()
