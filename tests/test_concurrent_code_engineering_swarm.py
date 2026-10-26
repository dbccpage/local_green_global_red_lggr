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
    DIAMOND_SWARM_MODELS,
    DIAMOND_WORKTREE_BRANCHES,
    JACOBIAN_PRICING_SOURCE,
    JACOBIAN_SETTLEMENT_BLIND_SOURCE,
    JACOBIAN_SETTLEMENT_OBSERVABLE_SOURCE,
    JACOBIAN_TAX_ALIGNED_SOURCE,
    JACOBIAN_TAX_DRIFT_SOURCE,
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
    QUORUM_PRICING_SOURCE,
    QUORUM_SETTLEMENT_QUORUM_SOURCE,
    QUORUM_SETTLEMENT_STRICT_SOURCE,
    QUORUM_TAX_ALIGNED_SOURCE,
    QUORUM_TAX_DRIFT_SOURCE,
    BoundaryQuorumCodeWorkspace,
    CPTPChannelCodeWorkspace,
    CatalystCodeWorkspace,
    CoalitionalCodeWorkspace,
    CodeWorkspace,
    DiamondCodeWorkspace,
    JacobianCodeWorkspace,
    KInductionCodeWorkspace,
    LeaseOverlapCodeWorkspace,
    MayerVietorisCodeWorkspace,
    OptionalStoppingCodeWorkspace,
    ReggeHolonomyCodeWorkspace,
    ReplayOrderCodeWorkspace,
    StatefulDFACodeWorkspace,
    WindowedDriftCodeWorkspace,
    catalyst_fixture,
    coalitional_fixture,
    cptp_fixture,
    dfa_fixture,
    diamond_fixture,
    fixture,
    jacobian_fixture,
    kinduction_fixture,
    lease_fixture,
    mv_fixture,
    quorum_fixture,
    regge_fixture,
    replay_fixture,
    run_coalitional_local_unit_tests,
    run_cptp_local_unit_tests,
    run_dfa_local_unit_tests,
    run_diamond_local_unit_tests,
    run_jacobian_local_unit_tests,
    run_kinduction_local_unit_tests,
    run_lease_local_unit_tests,
    run_local_unit_tests,
    run_mv_local_unit_tests,
    run_quorum_local_unit_tests,
    run_regge_local_unit_tests,
    run_replay_local_unit_tests,
    run_stop_local_unit_tests,
    run_win_local_unit_tests,
    stop_fixture,
    win_fixture,
)
from experiments.concurrent_code_engineering_swarm.runner import (
    CodeBatchClient,
    campaign,
    catalyst_campaign,
    coalitional_campaign,
    cptp_campaign,
    dfa_campaign,
    diamond_campaign,
    jacobian_campaign,
    kinduction_campaign,
    lease_campaign,
    mv_campaign,
    quorum_campaign,
    regge_campaign,
    replay,
    replay_campaign,
    stop_campaign,
    win_campaign,
)
from experiments.live_five_agent_swarm.client import Events, event_digest
from lggr.streaming import (
    StreamingCodebaseBoundaryQuorumMonitor,
    StreamingCodebaseCPTPChannelMonitor,
    StreamingCodebaseCatalystEvolutionMonitor,
    StreamingCodebaseCoalitionalMonitor,
    StreamingCodebaseInterfaceMergeMonitor,
    StreamingCodebaseJacobianSoundnessMonitor,
    StreamingCodebaseKInductionMonitor,
    StreamingCodebaseLeaseOverlapMonitor,
    StreamingCodebaseMayerVietorisMonitor,
    StreamingCodebaseOptionalStoppingMonitor,
    StreamingCodebaseReggeHolonomyMonitor,
    StreamingCodebaseReplayOrderMonitor,
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


if __name__ == "__main__":
    unittest.main()
