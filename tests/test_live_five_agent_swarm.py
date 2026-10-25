"""Offline tests of the live pilot's tools, independent judge, budgets and replay."""
from copy import deepcopy
from decimal import Decimal
import itertools
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
import urllib.response

from experiments.live_five_agent_swarm.client import Events, LiveClient, RunStopped, MODELS, request, reservation, response_message, charge
from experiments.live_five_agent_swarm.domain import Board, fixture, findings, certificates
from experiments.live_five_agent_swarm.oracle import feasible, judge
from experiments.live_five_agent_swarm.runner import agent_turn, campaign, inject, replay, source_hashes, system
from experiments.live_five_agent_swarm.client import event_digest as digest


class StubClient:
    """Deterministic tool-using test double; never used in live mode."""
    def __init__(self, events):
        self.events, self.calls, self.spent = events, 0, Decimal(0)
    def complete(self, model, messages):
        payload = request(model, messages)
        self.events.emit("api_request", {"request": payload, "reserved_usd": str(reservation(payload))})
        self.calls += 1
        worker = messages[0]["content"].split("dispatch agent ")[1].split(",")[0]
        name, args = "inspect_board", {}
        if messages[-1]["role"] == "tool":
            board = json.loads(messages[-1]["content"])
            if "jobs" in board:
                job = next(j for j in board["jobs"] if j["id"] == worker)
                taken = {p["slot"] for w,p in {**board["proposals"], **board["completed"]}.items() if w != worker}
                slots = sorted(set(job["allowed_slots"]) & set(board["active_slots"]) - taken)
                if slots:
                    name = "propose"
                    args = {"slot": slots[0], "epoch": board["epoch"],
                            "total_cents": sum(x["unit_cents"]*x["quantity"] for x in job["items"])}
                else:
                    name, args = "escalate", {"reason": "No available unclaimed allowed slot"}
        message = {"role": "assistant", "content": None,
                   "tool_calls": [{"id": f"call-{self.calls}", "type": "function",
                                   "function": {"name": name, "arguments": json.dumps(args)}}]}
        raw = {"id": f"test-{self.calls}", "model": model, "usage": {"cost": 0.0001},
               "choices": [{"message": message, "finish_reason": "tool_calls"}]}
        self.events.emit("api_response", {"response": raw, "elapsed_seconds": 0.01,
                         "charged_usd": "0.0001", "cost_reported": True})
        self.spent += Decimal("0.0001")
        return message


class LiveFiveAgentTests(unittest.TestCase):
    def filled(self, seed=3101):
        state = fixture(seed)
        used = set()
        for job in state["jobs"]:
            slot = sorted(set(job["allowed_slots"]) - used)[0]
            used.add(slot)
            state["proposals"][job["id"]] = {"slot": slot, "epoch": 0,
                "total_cents": sum(x["unit_cents"]*x["quantity"] for x in job["items"])}
        return state

    def test_tools_reject_wrong_types_ownership_and_missing_observation(self):
        board = Board(self.filled())
        for amount in (True, "5", 0.9):
            p = deepcopy(board.state["proposals"]["worker-0"]);p["total_cents"] = amount
            self.assertFalse(board.tool("worker-0", "propose", p)["accepted"])
        p = deepcopy(board.state["proposals"]["worker-0"]);p["worker"] = "worker-1"
        self.assertFalse(board.tool("worker-0", "propose", p)["accepted"])
        board.execute(["worker-0", "worker-1"])
        self.assertFalse(board.tool("worker-0", "propose", board.state["proposals"]["worker-0"])["accepted"])
        self.assertEqual(len(board.rows()), 2)
        board.close()

    def test_calculator_is_bounded_arithmetic_not_allocation(self):
        board = Board(fixture(3101))
        self.assertEqual(board.tool("worker-0", "calculate_total", {"items": [{"unit_cents": 17, "quantity": 3}]})["value"], 51)
        self.assertEqual(board.state["proposals"], {})
        self.assertFalse(board.tool("worker-0", "calculate_total", {"items": [{"unit_cents": True, "quantity": 3}]})["accepted"])
        board.close()

    def test_escalation_requires_nonblank_reason_and_preserves_truncation(self):
        board = Board(fixture(3101))
        self.addCleanup(board.close)
        for reason in ("", " ", "\t\r\n", "\u2003\u00a0"):
            with self.subTest(reason=reason):
                result = board.tool("worker-0", "escalate", {"reason": reason})
                self.assertFalse(result["accepted"])
                self.assertNotIn("escalated", result)
        for reason in ("No available slot", "  No available slot\n", "x" * 1001):
            with self.subTest(length=len(reason)):
                self.assertEqual(board.tool("worker-0", "escalate", {"reason": reason}),
                                 {"escalated": True, "reason": reason[:1000]})

    def test_malformed_tool_calls_record_failed_cases(self):
        for call in (None, [], "call", 1, {}, {"function": None},
                     {"function": []}, {"function": "inspect_board"}, {"function": 1}):
            with self.subTest(call=call):
                events = Events()
                client = StubClient(events)
                message = {"role": "assistant", "tool_calls": [call]}
                with patch.object(client, "complete", return_value=message):
                    summary = campaign(client, events, {"seeds": [3101]})
                self.assertTrue(summary["cases"][0]["baseline_failed"])
                self.assertEqual(sum(r["kind"] == "invalid_model_output" for r in events.records), 10)
                self.assertTrue(any(r["kind"] == "case_result" for r in events.records))
                self.assertFalse(any(r["kind"] == "tool" for r in events.records))

    def test_rejected_inspection_does_not_authorize_proposal(self):
        board = Board(fixture(3101))
        self.addCleanup(board.close)
        events = Events()
        proposal = self.filled()["proposals"]["worker-0"]

        def call(name, args, id_):
            return {"id": id_, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}

        client = Mock()
        client.complete.side_effect = [
            {"role": "assistant", "tool_calls": [call("inspect_board", {"extra": 1}, "bad"),
                                                  call("propose", proposal, "blocked")]},
            {"role": "assistant", "tool_calls": [call("inspect_board", {}, "good"),
                                                  call("inspect_board", {"extra": 1}, "bad-again"),
                                                  call("propose", proposal, "allowed")]},
        ]
        history = [{"role": "system", "content": system("worker-0")}]
        self.assertFalse(agent_turn(client, events, board, history, "worker-0", {}))
        results = [r["data"]["result"] for r in events.records if r["kind"] == "tool"]
        self.assertFalse(results[0]["accepted"])
        self.assertEqual(results[1], {"accepted": False, "error": "inspect the current board before acting"})
        self.assertIn("jobs", results[2])
        self.assertFalse(results[3]["accepted"])
        self.assertTrue(results[4]["accepted"])
        self.assertEqual(board.state["proposals"], {"worker-0": proposal})

    def test_injection_preserves_done_work_and_distinguishes_feasibility(self):
        board = Board(self.filled());board.execute(["worker-0", "worker-1"])
        before = deepcopy(board.state)
        feasible_state, _ = inject(before, "withdrawal")
        impossible, _ = inject(before, "infeasible")
        self.assertTrue(feasible(feasible_state));self.assertFalse(feasible(impossible))
        self.assertEqual(before["completed"], feasible_state["completed"])
        self.assertTrue(findings(feasible_state))
        cert = certificates(before, feasible_state)
        self.assertEqual(cert["fiber"]["status"], "REPORT_INSUFFICIENT")
        self.assertTrue(cert["resource_budget_obstructions"])
        board.close()

    def test_independent_judge_agrees_with_gate_on_finite_allocations(self):
        state = self.filled()
        state["jobs"] = state["jobs"][:3]
        state["proposals"] = {j["id"]: state["proposals"][j["id"]] for j in state["jobs"]}
        for slots in itertools.product(state["slots"][:4], repeat=3):
            for job, slot in zip(state["jobs"], slots):
                state["proposals"][job["id"]]["slot"] = slot
            rows = [{"worker": w, **p} for w,p in state["proposals"].items()]
            self.assertEqual(not findings(state), judge(state, rows, [])["complete"])
        rows[0]["total_cents"] += 1
        self.assertFalse(judge(state, rows, [])["valid_execution"])

    def test_budget_stops_before_network_and_missing_cost_reserves(self):
        with patch("experiments.live_five_agent_swarm.client.load_openrouter_credentials", return_value=("fake", MODELS[0])):
            client = LiveClient(Events(), "0.000001")
        with patch("urllib.request.build_opener") as send, self.assertRaises(RunStopped):
            client.complete(MODELS[0], [{"role": "user", "content": "hi"}])
        send.assert_not_called()
        self.assertEqual(client.calls, 0)
        self.assertEqual(charge({"usage": {}}, Decimal("0.1")), (Decimal("0.1"), False))
        self.assertEqual(charge({"usage": {"cost": "NaN"}}, Decimal("0.1")), (Decimal("0.1"), False))
        self.assertEqual(charge({"usage": {"cost": 0.0001}}, Decimal("0.1")), (Decimal("0.0001"), True))

    def test_credentialed_redirects_stop_without_sending_another_request(self):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                events = Events()
                with patch("experiments.live_five_agent_swarm.client.load_openrouter_credentials",
                           return_value=("fake", MODELS[0])):
                    client = LiveClient(events, "10")
                response = urllib.response.addinfourl(io.BytesIO(b""),
                    {"location": "https://other.invalid/collect"},
                    "https://openrouter.ai/api/v1/chat/completions", status)
                response.msg = "Redirect"
                with response, patch("urllib.request.HTTPSHandler.https_open", return_value=response) as send:
                    with self.assertRaisesRegex(RunStopped, "provider request failed"):
                        client.complete(MODELS[0], [{"role": "user", "content": "hi"}])
                send.assert_called_once()
                req = send.call_args.args[0]
                self.assertEqual(req.full_url, "https://openrouter.ai/api/v1/chat/completions")
                self.assertEqual(req.get_header("Authorization"), "Bearer fake")
                self.assertEqual(req.get_method(), "POST")
                self.assertEqual(client.calls, 1)
                self.assertEqual(events.records[-1]["kind"], "api_error")
                self.assertEqual(events.records[-1]["data"]["http_status"], status)
                self.assertEqual(str(client.spent), events.records[0]["data"]["reserved_usd"])

    def test_budget_stopped_run_replays_through_cli(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"events.jsonl"
            events = Events(path)
            config = {"seeds": [3101], "development": True, "models": MODELS, "budget_usd": "0.000001"}
            events.emit("start", {"schema": "lggr.live_five_agent_events.v1", "config": config,
                                  "source_hashes": source_hashes(), "source_commit": "test-double"})
            with patch("experiments.live_five_agent_swarm.client.load_openrouter_credentials", return_value=("fake", MODELS[0])):
                client = LiveClient(events, config["budget_usd"])
            try:
                campaign(client, events, config)
                self.fail("budget should stop before any API call")
            except RunStopped as error:
                events.emit("stopped", {"reason": str(error), "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent)})
            completed = subprocess.run([sys.executable, "-m", "experiments.live_five_agent_swarm.runner", "replay", str(path)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "stopped")

    def test_malformed_tool_shapes_and_failed_inspection_cannot_act(self):
        class Responses:
            def __init__(self, calls): self.calls = calls
            def complete(self, *args): return {"role": "assistant", "tool_calls": self.calls}
        def call(name, args):
            return {"id": name, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}
        board = Board(fixture(3101))
        self.addCleanup(board.close)
        for calls in ([None], [{"function": None}], [call("inspect_board", {"extra": True}), call("escalate", {"reason": "no slots"})]):
            events = Events()
            self.assertFalse(agent_turn(Responses(calls), events, board, [], "worker-0", {}))
            self.assertFalse(any(e["kind"] == "tool" and e["data"]["result"].get("escalated") for e in events.records))
        for reason in ("", " ", "\n", " "*1000+"hidden"):
            self.assertFalse(board.tool("worker-0", "escalate", {"reason": reason}).get("escalated", False))
        self.assertTrue(board.tool("worker-0", "escalate", {"reason": "No capacity"})["escalated"])

    def test_redirects_are_rejected_and_malformed_provider_shapes_are_safe(self):
        import urllib.request
        import urllib.error
        from experiments.live_five_agent_swarm.client import RejectRedirects
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": "Bearer fake"})
        with self.assertRaises(urllib.error.HTTPError):
            RejectRedirects().redirect_request(req, None, 302, "redirect", {}, "https://other.invalid")
        for raw in (None, [], {"model": None}, {"model": MODELS[0], "choices": [None]}):
            with self.assertRaises(ValueError): response_message(raw, MODELS[0])
            self.assertEqual(charge(raw, Decimal("0.1")), (Decimal("0.1"), False))

    def test_actual_model_identity_and_truncation_rejected(self):
        raw = {"model": "other/model", "choices": [{"message": {"role": "assistant"}, "finish_reason": "stop"}]}
        with self.assertRaises(ValueError):response_message(raw, MODELS[0])
        raw["model"] = MODELS[0];raw["choices"][0]["finish_reason"] = "length"
        with self.assertRaises(ValueError):response_message(raw, MODELS[0])

    def test_complete_paired_campaign_and_adversarial_replay(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"events.jsonl"
            events = Events(path)
            config = {"seeds": list(range(4101,4107)), "development": False, "models": MODELS, "budget_usd": "10"}
            events.emit("start", {"schema": "lggr.live_five_agent_events.v1", "config": config,
                                  "source_hashes": source_hashes(), "source_commit": "test-double"})
            summary = campaign(StubClient(events), events, config)
            self.assertEqual(summary["invalid_execution_count"], 0)
            self.assertEqual(len(summary["cases"]), 6)
            self.assertTrue(all(not c["baseline_failed"] for c in summary["cases"]))
            self.assertTrue(all(a["outcome"] == "completed" for c in summary["cases"] if c["kind"] == "control" for a in c["arms"]))
            self.assertTrue(all(a["outcome"] == "safe_escalated" for c in summary["cases"] if c["kind"] == "infeasible" for a in c["arms"]))
            self.assertEqual(replay(path), summary)
            records = deepcopy(events.records)
            tool = next(x for x in records if x["kind"] == "tool" and x["data"]["call"]["function"]["name"] == "propose")
            tool["data"]["result"]["accepted"] = False
            for i, record in enumerate(records):
                record["previous"] = records[i-1]["sha256"] if i else None
                record["sha256"] = digest({k:v for k,v in record.items() if k != "sha256"})
            path.write_text("\n".join(json.dumps(r) for r in records),encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "replay differs"):
                replay(path)


if __name__ == "__main__":
    unittest.main()
