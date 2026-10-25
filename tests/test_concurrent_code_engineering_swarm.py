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
    CANONICAL_PRICING_EVENTS_SOURCE,
    CANONICAL_PRICING_SOURCE,
    CANONICAL_PRICING_TX_SOURCE,
    CANONICAL_QUOTE_ANCHOR_SOURCE,
    CANONICAL_SETTLEMENT_EVENTS_SOURCE,
    CANONICAL_SETTLEMENT_SOURCE,
    CANONICAL_SETTLEMENT_TX_SOURCE,
    CANONICAL_TAX_BRANCH_SOURCE,
    CANONICAL_TAX_EVENTS_SOURCE,
    CANONICAL_TAX_SOURCE,
    CANONICAL_TAX_TX_SOURCE,
    CODE_SWARM_MODELS,
    DIAMOND_SWARM_MODELS,
    DIAMOND_WORKTREE_BRANCHES,
    CatalystCodeWorkspace,
    CodeWorkspace,
    DiamondCodeWorkspace,
    ReplayOrderCodeWorkspace,
    StatefulDFACodeWorkspace,
    catalyst_fixture,
    dfa_fixture,
    diamond_fixture,
    fixture,
    replay_fixture,
    run_dfa_local_unit_tests,
    run_diamond_local_unit_tests,
    run_local_unit_tests,
    run_replay_local_unit_tests,
)
from experiments.concurrent_code_engineering_swarm.runner import (
    CodeBatchClient,
    campaign,
    catalyst_campaign,
    dfa_campaign,
    diamond_campaign,
    replay,
    replay_campaign,
)
from experiments.live_five_agent_swarm.client import Events, event_digest
from lggr.streaming import (
    StreamingCodebaseCatalystEvolutionMonitor,
    StreamingCodebaseInterfaceMergeMonitor,
    StreamingCodebaseReplayOrderMonitor,
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


if __name__ == "__main__":
    unittest.main()
