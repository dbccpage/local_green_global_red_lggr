"""Unit, sandbox, concurrent wave, and tamper-evident replay tests for the code-engineering swarm."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from experiments.concurrent_code_engineering_swarm.domain import (
    CANONICAL_PRICING_SOURCE,
    CANONICAL_SETTLEMENT_SOURCE,
    CANONICAL_TAX_SOURCE,
    CODE_SWARM_MODELS,
    CodeWorkspace,
    fixture,
    run_local_unit_tests,
)
from experiments.concurrent_code_engineering_swarm.runner import (
    CodeBatchClient,
    campaign,
    replay,
)
from experiments.live_five_agent_swarm.client import Events, event_digest
from lggr.streaming import StreamingCodebaseInterfaceMergeMonitor


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


if __name__ == "__main__":
    unittest.main()
