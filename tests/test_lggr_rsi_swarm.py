"""Offline tests for the LGGR/RSI live swarm experiment (no network)."""
from copy import deepcopy
from decimal import Decimal
import gzip
import itertools
import json
from pathlib import Path
import re
import tempfile
import threading
import unittest

from experiments.lggr_rsi_swarm import runner
from experiments.lggr_rsi_swarm.generate import build, build_v2, generate, load
from swarm.advisors import note
from swarm.domain import MALFORMED, local_report
from swarm.evidence_access import Denied as CheckDenied, Gateway
from swarm.grading import full_verification
from swarm.hashing import ReplayMismatch, canonical, load_events, verify_chain
from swarm.ledger import RESERVATION, BudgetExceeded, Ledger, usage_cost
from swarm.memory import Memory
from swarm.selectors import Space, acquire, host_rule, info_gain, pair_elimination
from swarm.tool_host import RSI_TOOLS, SWARM_TOOLS, Denied, ToolError, Workspace, validate
from swarm.transport import FakeTransport, HaltRun, run_wave

DATA = load()
DEV = {i["id"]: i for i in DATA["development"]}


def green_config(module, instance):
    """Smallest local-green assignment for a module, starts laid out later by the caller."""
    params = list(module["params"])
    ranges = [range(module["params"][p]["lo"], min(module["params"][p]["hi"], module["params"][p]["lo"] + 60) + 1)
              if p != "start" else [0] for p in params]
    for combo in itertools.product(*ranges):
        values = dict(zip(params, combo))
        content = "\n".join(f"{k} = {v}" for k, v in values.items())
        if local_report(instance, module, {module["file"]: content})["pass"]:
            return values
    raise AssertionError("no local-green config")


def files_for(instance, lat=1):
    files, t = {}, 0
    for m in instance["modules"]:
        values = green_config(m, instance)
        if "start" in values:
            values["start"], t = t, t + values["ticks"] + lat
        files[m["file"]] = "\n".join(f"{k} = {v}" for k, v in values.items())
    return files


def last_text(payload):
    content = payload["messages"][-1]["content"]
    return "\n".join(b.get("text", "") if b.get("type") == "text" else str(b.get("content", "")) for b in content)


class FakeModel:
    """Scripted agent behaviour keyed on request keys; exercises every tool path."""

    def __init__(self, instances, fail_keys=()):
        self.instances, self.fail_keys, self.calls = instances, set(fail_keys), 0
        self.lock = threading.Lock()

    def body(self, key, blocks, stop="tool_use"):
        content = [{"type": "thinking", "thinking": "summary", "signature": "sig-" + key}]
        for i, (name, args) in enumerate(blocks):
            content.append({"type": "tool_use", "id": f"toolu_{abs(hash(key)) % 10 ** 8}_{i}", "name": name, "input": args})
        if not blocks:
            content.append({"type": "text", "text": "done"})
            stop = "end_turn"
        return {"id": "msg_" + key, "type": "message", "role": "assistant", "model": "claude-haiku-5-5", "content": content,
                "stop_reason": stop, "usage": {"input_tokens": 900, "cache_creation_input_tokens": 300,
                                                "cache_read_input_tokens": 1200, "output_tokens": 250}}

    def __call__(self, key, payload):
        with self.lock:
            self.calls += 1
        if key in self.fail_keys:
            return {"__failure__": {"stage": "create", "kind": "InternalServerError", "http_status": 500}}
        inst_id = key.split("/")[0]
        inst = self.instances[inst_id]
        agent = next(a for a in runner.AGENTS if f"/{a}" in key)
        if "/ctl" in key:
            text = last_text(payload)
            ids = re.findall(r"K\d\d", text.split("advisor note:")[-1]) if "advisor note:" in text else []
            turn = int(key.rsplit("/t", 1)[1])
            if turn == 1 and ids:
                return self.body(key, [("run_check", {"check_id": ids[0]})])
            if turn == 2:
                return self.body(key, [("run_check", {"check_id": "K99"})])
            return self.body(key, [("submit_verdict", {"verdict": "reject", "explanation": "fake", "cited_check_ids": ids[:1]})])
        owned = next((m for m in inst["modules"] if m["owner"] == agent), None)
        if "/rsi-" in key:
            calls = [("memory_recall", {"query": ""}), ("memory_append", {"key": "cap", "content": "lesson", "source_ref": "contract:global"})]
            if owned and ("/u1" in key or "/l1" in key):
                calls.append(("write_file", {"path": owned["file"], "content": files_for(inst)[owned["file"]]}))
            if "/s1" in key:
                calls.append(("write_file", {"path": owned["file"] if owned else "x", "content": "x = 1"}))
            calls.append(("post_note", {"text": "ok", "status": "success"}))
            return self.body(key, calls)
        if owned:
            calls = [("write_file", {"path": owned["file"], "content": files_for(inst)[owned["file"]]}), ("run_local_tests", {}),
                     ("post_note", {"text": "written", "status": "success"})]
        else:
            calls = [("read_file", {"path": inst["modules"][0]["file"]}), ("run_check", {"check_id": "K01"}),
                     ("write_file", {"path": inst["modules"][0]["file"], "content": "hijack = 1"}),
                     ("post_note", {"text": "checked", "status": "success" if agent == "tester" else "concern"})]
        if key.endswith("/p2") and agent == "impl-1":
            return self.body(key, [])
        return self.body(key, calls)


def run_fake(tmp, part="swarm", fail_keys=()):
    data = DATA
    config = runner.chunk_config(data, "development", part, 0)
    instances = {i["id"]: i for i in data["development"]}
    model = FakeModel(instances, fail_keys)
    transport = FakeTransport(model)
    ledger = Ledger(Path(tmp) / "ledger.json", "development")
    out = Path(tmp) / f"run-{part}"
    out.mkdir()
    path, summary = runner.execute(data, config, transport, ledger, out, {"id": "claude-haiku-5-5"}, "0" * 40, runner.source_hashes())
    return path, summary, ledger, model


class GeneratorTests(unittest.TestCase):
    def test_balanced_and_deterministic(self):
        self.assertEqual(DATA, generate())
        ev = DATA["evaluation"]
        self.assertEqual(len(ev), 400)
        for fam in ("allocation", "temporal", "interface", "combined"):
            rows = [i for i in ev if i["family"] == fam]
            self.assertEqual(len(rows), 100)
            self.assertEqual(sum(i["control"] == "clean" for i in rows), 80)
        for inst in ev + DATA["development"]:
            self.assertEqual(len(inst["checks"]), 16)
            self.assertTrue({c["cost"] for c in inst["checks"]} <= {1, 2, 4})
        dev_ids = {i["id"] for i in DATA["development"]}
        self.assertFalse(dev_ids & {i["id"] for i in ev})
        sub = DATA["subsets"]
        self.assertEqual((len(sub["l0"]), len(sub["repair"]), len(sub["rsi"])), (100, 60, 30))

    def test_out_of_model_truth_outside_domain(self):
        for inst in DATA["evaluation"]:
            outside = [h["name"] for h in inst["hidden"] if inst["truth"][h["name"]] not in h["domain"]]
            self.assertEqual(bool(outside), inst["control"] == "out_of_model")

    def test_v2_changes_contract(self):
        inst = DATA["evaluation"][0]
        v2 = build_v2(inst)
        self.assertNotEqual(runner.global_contract_text(inst), runner.global_contract_text(v2))


class LedgerTests(unittest.TestCase):
    def test_reservation_constant(self):
        self.assertEqual(RESERVATION, Decimal("0.003298"))
        self.assertEqual(usage_cost({"input_tokens": 10 ** 6, "output_tokens": 0}), Decimal("0.10"))

    def test_wave_is_all_or_nothing_and_blocks_next_wave(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "l.json", "development")
            n = int(Decimal("20") / RESERVATION)
            with self.assertRaises(BudgetExceeded):
                ledger.reserve_wave([f"k{i}" for i in range(n + 1)])
            self.assertEqual(ledger.outstanding(), 0)
            ledger.reserve_wave(["a", "b"])
            with self.assertRaises(BudgetExceeded):
                ledger.reserve_wave(["c"])

    def test_concurrent_settlement_race(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "l.json", "development")
            keys = [f"k{i}" for i in range(200)]
            ledger.reserve_wave(keys)
            usage = {"input_tokens": 1000, "output_tokens": 100}
            threads = [threading.Thread(target=(ledger.settle if i % 2 else ledger.fail), args=((k, usage) if i % 2 else (k,)))
                       for i, k in enumerate(keys)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(ledger.outstanding(), 0)
            phase = ledger.state["phases"]["development"]
            self.assertEqual(Decimal(phase["settled"]), 100 * usage_cost(usage))
            self.assertEqual(Decimal(phase["retained"]), 100 * RESERVATION)
            self.assertEqual(phase["requests"], 200)

    def test_interrupted_requests_keep_allocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "l.json"
            ledger = Ledger(path, "development")
            ledger.reserve_wave(["a", "b", "c"])
            ledger.settle("a", {"input_tokens": 10, "output_tokens": 10})
            # crash: b and c never settle
            reopened = Ledger(path, "evaluation")
            self.assertEqual(reopened.recovered, ["b", "c"])
            self.assertEqual(Decimal(reopened.state["phases"]["development"]["retained"]), 2 * RESERVATION)
            reopened.reserve_wave(["d"])

    def test_total_ceiling_spans_phases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "l.json"
            ledger = Ledger(path, "evaluation")
            ledger.state["phases"]["development"]["settled"] = "20"
            ledger.state["phases"]["evaluation"]["settled"] = "139.999"
            with self.assertRaises(BudgetExceeded):
                ledger.reserve_wave(["x"])

    def test_run_wave_settles_everything_and_failures_retain(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "l.json", "development")
            model = FakeModel(DEV, fail_keys={"dev-900000/d0/impl-0/p1"})
            reqs = [("dev-900000/d0/impl-0/p1", {}), ("dev-900000/d0/impl-1/p1", {})]
            results, _ = run_wave(FakeTransport(model), ledger, reqs)
            self.assertEqual(ledger.outstanding(), 0)
            self.assertEqual(results["dev-900000/d0/impl-0/p1"]["charged_usd"], str(RESERVATION))
            self.assertEqual(results["dev-900000/d0/impl-0/p1"]["outcome"], "failure")


class SelectorTests(unittest.TestCase):
    def tiny(self):
        inst = deepcopy(DEV["dev-900000"])
        return inst, files_for(inst)

    def test_host_rule_and_malformed(self):
        inst, files = self.tiny()
        space = Space(inst, files)
        self.assertEqual(host_rule(space, []), "defer" if len({*space.verdicts}) == 2 else ("accept" if space.verdicts[0] else "reject"))
        cid = inst["checks"][0]["id"]
        self.assertEqual(space.alive([(cid, MALFORMED)]), list(range(len(space.hyps))))
        self.assertEqual(host_rule(space, [(cid, "no-such-outcome")]), "model_mismatch")

    def test_counterexample_b_prefers_distractor_c_prefers_verdict(self):
        hidden = [{"name": "a", "domain": [0, 1], "text": ""}, {"name": "z", "domain": [0, 1, 2, 3], "text": ""}]
        inst = {"modules": [{"name": "m", "owner": "impl-0", "file": "m.cfg", "params": {"v": {"lo": 0, "hi": 9, "text": ""}}, "local": []}],
                "hidden": hidden, "global": [{"id": "G1", "lhs": {"t": "a"}, "op": "<=", "rhs": 0, "text": ""}],
                "checks": [{"id": "K01", "kind": "measure", "param": "z", "cost": 1, "text": ""},
                           {"id": "K02", "kind": "probe", "param": "a", "threshold": 1, "cost": 1, "text": ""},
                           {"id": "K03", "kind": "measure", "param": "a", "cost": 1, "text": ""}],
                "truth": {"a": 1, "z": 2}, "malformed": [], "control": "clean"}
        files = {"m.cfg": "v = 1"}
        space = Space(inst, files)
        alive = space.alive([])
        self.assertGreater(info_gain(space, alive, "K01"), info_gain(space, alive, "K02"))
        # Splitting on the distractor still removes cross pairs (15 of 16); the decisive probe removes all 16.
        self.assertEqual(pair_elimination(space, alive, "K01")[0], 15)
        self.assertEqual(pair_elimination(space, alive, "K02")[0], 16)
        b = acquire("B", space, Gateway(inst, files, 1).run, 1)
        c = acquire("C", space, Gateway(inst, files, 1).run, 1)
        self.assertEqual(b["steps"][0]["check"], "K01")
        self.assertEqual(b["decision"], "defer")
        self.assertEqual(c["steps"][0]["check"], "K02")  # tie with K03 broken by id
        self.assertEqual(c["decision"], "reject")

    def test_c_uses_only_consistent_witnesses(self):
        inst, files = self.tiny()
        space = Space(inst, files)
        gate = Gateway(inst, files, 8)
        r = acquire("C", space, gate.run, 8)
        obs = gate.observations()
        for step in range(len(obs)):
            alive = space.alive(obs[:step])
            self.assertTrue(all(i in range(len(space.hyps)) for i in alive))
        self.assertEqual(r["decision"], host_rule(space, obs))


class AccessTests(unittest.TestCase):
    def test_gateway_denials_charge_nothing(self):
        inst = DEV["dev-900000"]
        files = files_for(inst)
        gate = Gateway(inst, files, 2)
        expensive = next(c["id"] for c in inst["checks"] if c["cost"] == 4)
        with self.assertRaises(CheckDenied):
            gate.run(expensive)
        with self.assertRaises(CheckDenied):
            gate.run("K99")
        cheap = next(c["id"] for c in inst["checks"] if c["cost"] == 1)
        gate.run(cheap)
        with self.assertRaises(CheckDenied):
            gate.run(cheap)
        self.assertEqual(gate.spent, 1)

    def test_no_uncharged_tool_reveals_hidden_values(self):
        for inst in DATA["development"]:
            ws = Workspace(inst)
            outputs = [ws.contract("global")] + [ws.contract(m["name"]) for m in inst["modules"]]
            for m in inst["modules"]:
                ws.execute(m["owner"], "proposal", 1, "write_file", {"path": m["file"], "content": files_for(inst)[m["file"]]})
                outputs.append(ws.execute(m["owner"], "proposal", 1, "run_local_tests", {}))
            blob = "\n".join(outputs)
            self.assertNotIn("truth", blob)
            for agent in runner.AGENTS:
                for phase in ("proposal", "repair"):
                    with self.assertRaises(Denied):
                        ws.execute(agent, phase, 1, "run_check", {"check_id": "K01"})
            with self.assertRaises(Denied):
                ws.execute("tester", "proposal", 1, "write_file", {"path": inst["modules"][0]["file"], "content": ""})
            with self.assertRaises(Denied):
                ws.execute("impl-0", "controller", 1, "write_file", {"path": inst["modules"][0]["file"], "content": ""})
            with self.assertRaises(Denied):
                ws.execute("impl-0", "rsi_restart", 1, "write_file", {"path": inst["modules"][0]["file"], "content": ""})

    def test_strict_tool_schemas_and_validation(self):
        for tool in SWARM_TOOLS + RSI_TOOLS:
            self.assertTrue(tool["strict"])
            self.assertFalse(tool["input_schema"]["additionalProperties"])
            self.assertEqual(sorted(tool["input_schema"]["required"]), sorted(tool["input_schema"]["properties"]))
        with self.assertRaises(ToolError):
            validate("swarm", "submit_verdict", {"verdict": "maybe", "explanation": "", "cited_check_ids": []})
        with self.assertRaises(ToolError):
            validate("swarm", "run_check", {"check_id": "K01", "extra": 1})
        with self.assertRaises(ToolError):
            validate("swarm", "memory_recall", {"query": ""})


class AdvisorTests(unittest.TestCase):
    def test_advisor_has_no_hidden_state_leakage(self):
        import random
        rng = random.Random(7)
        for inst in DATA["development"] + DATA["evaluation"][:40]:
            files = files_for(inst)
            space = Space(inst, files)
            obs = []
            gate = Gateway(inst, files, 4)
            acquire("C", space, gate.run, 4)
            obs = gate.observations()
            noised = deepcopy(inst)
            noised["truth"] = {h["name"]: rng.choice(h["domain"]) for h in inst["hidden"]}
            noised["malformed"] = []
            space2 = Space(noised, files)
            for arm in ("L-0", "L-B", "L-C"):
                for k in range(len(obs) + 1):
                    used = {c for c, _ in obs[:k]}
                    self.assertEqual(note(arm, space, obs[:k], 4, used), note(arm, space2, obs[:k], 4, used))

    def test_prompt_parity_byte_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, summary, _, _ = run_fake(tmp)
            records = load_events(path)
            # Rebuild the first controller request of each arm from the replay of the recorded deltas.
            firsts = {}
            for r in records:
                if r["kind"] == "request" and "/ctl-" in r["data"]["key"] and r["data"]["key"].endswith("/t1") and "/rep" not in r["data"]["key"]:
                    inst = r["data"]["key"].split("/")[0]
                    arm = r["data"]["key"].split("/ctl-")[1].split("/")[0]
                    firsts.setdefault(inst, {})[arm] = r["data"]["delta"]
            self.assertTrue(firsts)
            for inst, arms in firsts.items():
                self.assertGreaterEqual(len(arms), 2)
                stripped = set()
                for arm, delta in arms.items():
                    msg = deepcopy(delta[-1])
                    self.assertTrue(msg["content"][-1]["text"].startswith("advisor note:"))
                    msg["content"] = msg["content"][:-1]
                    stripped.add(canonical(delta[:-1] + [msg]))
                self.assertEqual(len(stripped), 1)


class MemoryTests(unittest.TestCase):
    def test_stale_and_conflict_in_bound_arm_only(self):
        inst = DATA["evaluation"][0]
        v2 = build_v2(inst)
        for bound in (False, True):
            mem, ws = Memory(bound), Workspace(inst)
            mem.call("impl-0", "memory_append", {"key": "cap", "content": "cap is 20", "source_ref": "contract:global"}, ws.source_text)
            mem.call("impl-1", "memory_append", {"key": "cap", "content": "cap is 23", "source_ref": "contract:global"}, ws.source_text)
            mem.call("impl-1", "memory_mark_obligation", {"text": "re-verify", "source_ref": "contract:global"}, ws.source_text)
            ws2 = ws.fork(instance=v2)
            out = json.loads(mem.call("tester", "memory_recall", {"query": "cap"}, ws2.source_text))
            if bound:
                self.assertTrue(all(r["stale"] and r["conflict"] for r in out["records"]))
                self.assertEqual(len(out["open_obligations"]), 1)
                fresh = json.loads(mem.call("tester", "memory_recall", {"query": ""}, ws.source_text))
                self.assertFalse(any(r["stale"] for r in fresh["records"]))
            else:
                self.assertNotIn("open_obligations", out)
                self.assertTrue(all("stale" not in r for r in out["records"]))
            with self.assertRaises(ToolError):
                mem.call("x", "memory_append", {"key": "k", "content": "c", "source_ref": "nowhere"}, ws.source_text)


class CampaignReplayTests(unittest.TestCase):
    def test_swarm_campaign_replays_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, summary, ledger, model = run_fake(tmp, fail_keys={"dev-900002/d0/tester/p2"})
            self.assertEqual(ledger.outstanding(), 0)
            self.assertEqual(len(summary["offline"]), 8)
            arms = {(c["instance"], c["arm"]) for c in summary["controllers"]}
            self.assertEqual(len(arms), 8 * 3)
            self.assertEqual(len(summary["repair"]), 4)
            records = load_events(path)
            kinds = {r["kind"] for r in records}
            self.assertTrue({"tool", "offline", "controller", "repair", "snapshot"} <= kinds)
            denied = [r for r in records if r["kind"] == "tool" and r["data"]["denied"]]
            self.assertTrue(any(r["data"]["name"] == "run_check" for r in denied))
            self.assertTrue(any(r["data"]["name"] == "write_file" for r in denied))
            for c in summary["controllers"]:
                space = Space(DEV[c["instance"]], _snapshot(records, c["instance"]))
                self.assertEqual(c["host_rule_on_agent_evidence"], host_rule(space, [(e["check"], e["result"]) for e in c["checks"]]))
            result = runner.replay(path)
            self.assertTrue(result["complete"])
            # tamper with a tool result but keep the hash chain valid -> replay must fail
            tampered = Path(tmp) / "tampered.jsonl"
            changed = deepcopy(records)
            index = next(i for i, r in enumerate(changed) if r["kind"] == "offline")
            changed[index]["data"]["arms"]["C@4"]["decision"] = "accept" if changed[index]["data"]["arms"]["C@4"]["decision"] != "accept" else "reject"
            rechain(changed)
            tampered.write_text("".join(json.dumps(r) + "\n" for r in changed), encoding="utf-8")
            with self.assertRaises(ReplayMismatch):
                runner.replay(tampered)
            # tamper without re-chaining -> chain check fails
            broken = deepcopy(records)
            broken[5]["data"]["x"] = 1
            with self.assertRaises(ReplayMismatch):
                verify_chain(broken)
            # tamper with a recorded provider usage -> charge replay differs
            usage = deepcopy(records)
            index = next(i for i, r in enumerate(usage) if r["kind"] == "response" and r["data"]["body"])
            usage[index]["data"]["body"]["usage"]["output_tokens"] += 1
            rechain(usage)
            tampered.write_text("".join(json.dumps(r) + "\n" for r in usage), encoding="utf-8")
            with self.assertRaises(ReplayMismatch):
                runner.replay(tampered)

    def test_rsi_campaign_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, summary, ledger, model = run_fake(tmp, part="rsi")
            self.assertEqual(len(summary["rsi"]), 4)
            self.assertEqual({r["arm"] for r in summary["rsi"]}, {"C", "D"})
            records = load_events(path)
            restart_writes = [r for r in records if r["kind"] == "tool" and r["data"]["phase"] == "rsi_restart" and r["data"]["name"] == "write_file"]
            self.assertTrue(restart_writes and all(r["data"]["denied"] for r in restart_writes))
            self.assertTrue(runner.replay(path)["complete"])

    def test_model_drift_halts(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = runner.chunk_config(DATA, "development", "swarm", 0, resolved_model="claude-haiku-5-5")
            model = FakeModel(DEV)

            def drift(key, payload):
                body = model(key, payload)
                if key.endswith("/p2"):
                    body["model"] = "claude-other"
                return body
            out = Path(tmp) / "run"
            out.mkdir()
            with self.assertRaises(HaltRun):
                runner.execute(DATA, config, FakeTransport(drift), Ledger(Path(tmp) / "l.json", "development"), out, {}, "0" * 40, runner.source_hashes())


def _snapshot(records, instance):
    return next(r["data"]["files"] for r in records if r["kind"] == "snapshot" and r["data"]["instance"] == instance)


def rechain(records):
    from swarm.hashing import digest
    previous = None
    for i, r in enumerate(records):
        r["index"], r["previous"] = i, previous
        r["sha256"] = digest({k: r[k] for k in ("index", "previous", "kind", "data")})
        previous = r["sha256"]


if __name__ == "__main__":
    unittest.main()
