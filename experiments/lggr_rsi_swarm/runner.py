"""LGGR/RSI live swarm: proposal waves, offline arms, live controllers, repair and RSI.

Usage:
  python -m experiments.lggr_rsi_swarm.runner live  OUTDIR --split development|evaluation --part swarm|rsi --chunk N
  python -m experiments.lggr_rsi_swarm.runner replay OUTDIR/events.jsonl[.gz]
The same `campaign` code runs live and in replay; replay feeds recorded provider
results back and requires every event to be reproduced exactly.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

from ._path import ROOT
from .generate import build_v2, load
from swarm.advisors import note as advisor_note
from swarm.domain import catalog_text, global_contract_text, local_contract_text, local_report
from swarm.evidence_access import Denied as CheckDenied, Gateway, render_result
from swarm.grading import full_verification, classify
from swarm.hashing import Events, compress, digest, load_events
from swarm.ledger import Ledger
from swarm.memory import Memory
from swarm.selectors import ARMS, Space, acquire, host_rule
from swarm.tool_host import Denied, ToolError, TOOLSETS, Workspace, validate
from swarm.transport import (API_VERSION, MODEL, AnthropicTransport, HaltRun, ReplayTransport,
                             response_failure, run_wave)

HERE = Path(__file__).resolve().parent
AGENTS = ["impl-0", "impl-1", "impl-2", "tester", "challenger"]
BUDGETS = [1, 2, 4, 8]
PRIMARY_BUDGET = 4
CONTROLLER_TURNS, REPAIR_CONTROLLER_TURNS = 6, 5
SWARM_CHUNK, RSI_CHUNK = 20, 10
DRAWS = [0, 1, 2]

COMMON = ("You are {agent}, one of five agents building a small configured system: impl-0, impl-1 and impl-2 each own one "
          "module file; tester checks integration; challenger looks for ways the integrated system could fail. Work runs in "
          "synchronous waves. In each wave you get exactly one turn: make every tool call you need in that single turn. The "
          "host executes your calls after the turn (in agent order) and shows the results at the start of your next wave, "
          "together with new team-board notes. Module files are integer `key = value` configurations that the host evaluates "
          "against public contracts; they are never executed. The global contract depends on hidden environment parameters "
          "whose possible values are public but whose true values nobody can observe in this phase. Local tests check only "
          "one module's own contract. End every turn with post_note giving your status: success (you believe the integrated "
          "system satisfies the global contract), concern, or blocked. Be concise.")
ROLE = {
    "impl": ("You own module {module} (file {file}). Write the complete file with write_file, run your local tests, and choose "
             "values you expect to satisfy the global contract for as many possible hidden values as you can. Coordinate "
             "through notes."),
    "tester": ("You own no module. Read the module files and contracts, look for global-contract violations under the possible "
               "hidden values, and post concrete findings for the implementers."),
    "challenger": ("You own no module. Argue against premature acceptance: identify combinations of hidden values under which "
                   "the integrated system would fail, and post them for the implementers."),
}
RSI_EXTRA = (" Team memory (memory_* tools) persists across session restarts; record durable lessons with memory_append and "
             "obligations with memory_mark_obligation, and consult memory_recall before relying on earlier conclusions.")


def system_text(agent, instance, rsi=False):
    role = "impl" if agent.startswith("impl") else agent
    module = next((m for m in instance["modules"] if m["owner"] == agent), None)
    text = COMMON.format(agent=agent) + " " + ROLE[role].format(module=module["name"] if module else "", file=module["file"] if module else "")
    return text + (RSI_EXTRA if rsi else "")


def opening_text(agent, ws, header):
    instance = ws.instance
    parts = [header, global_contract_text(instance)]
    own = next((m for m in instance["modules"] if m["owner"] == agent), None)
    mods = [own] if own else instance["modules"]
    parts += [local_contract_text(m) for m in mods]
    parts.append("Current files:\n" + "\n".join(f"--- {m['file']}\n{ws.files[m['file']]}" for m in instance["modules"]))
    return "\n\n".join(parts)


def board_text(ws, since_wave, phase):
    notes = [n for n in ws.board if n["phase"] == phase and n["wave"] >= since_wave]
    if not notes:
        return "Team board: no new notes."
    return "Team board:\n" + "\n".join(f"  [{n['agent']}] ({n['status']}) {n['text']}" for n in notes)


def files_text(ws):
    return "\n".join(f"--- {m['file']}\n{ws.files[m['file']]}" for m in ws.instance["modules"])


class Session:
    def __init__(self, sid, system, toolset, parallel=True):
        self.sid, self.system, self.toolset, self.parallel = sid, system, toolset, parallel
        self.messages, self.logged, self.pending, self.dead = [], 0, [], False

    def fork(self, sid):
        other = deepcopy(self)
        other.sid = sid
        return other

    def user(self, blocks):
        self.messages.append({"role": "user", "content": blocks})

    def payload(self):
        choice = {"type": "auto"} if self.parallel else {"type": "auto", "disable_parallel_tool_use": True}
        return {"model": MODEL, "max_tokens": 4096,
                "system": [{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
                "tools": TOOLSETS[self.toolset], "tool_choice": choice,
                "thinking": {"type": "adaptive", "display": "summarized"}, "output_config": {"effort": "low"},
                "cache_control": {"type": "ephemeral"}, "messages": self.messages}


def text(t):
    return {"type": "text", "text": t}


class Campaign:
    def __init__(self, data, config, transport, ledger, events):
        self.data, self.config, self.transport, self.ledger, self.events = data, config, transport, ledger, events
        self.index = {i["id"]: i for i in data["evaluation"] + data["development"]}
        self.expected_model = config.get("resolved_model")
        self.rng = random.Random(config["chunk_seed"])

    # ---- provider waves -------------------------------------------------
    def wave(self, label, items):
        """items: list of (key, session). Returns {key: body or None}."""
        items = [(k, s) for k, s in items if not s.dead]
        order = list(items)
        self.rng.shuffle(order)
        requests = [(k, deepcopy(s.payload())) for k, s in order]
        payload_of = dict(requests)
        results, reserved = run_wave(self.transport, self.ledger, requests)
        self.events.emit("wave", {"label": label, "requests": len(requests), "reserved_usd": reserved,
                                  "dispatch_order": [k for k, _ in order]})
        out = {}
        for key, session in sorted(items, key=lambda kv: kv[0]):
            r = results[key]
            self.events.emit("request", {"key": key, "session": session.sid, "payload_sha256": digest(payload_of[key]),
                                         "delta": session.messages[session.logged:], "count": r.get("count")})
            failure = r.get("failure")
            body = r.get("body")
            if r["outcome"] == "ok":
                if self.expected_model is None:
                    self.expected_model = body.get("model")
                failure = response_failure(body, self.expected_model)
            elif r["outcome"] == "refused_input":
                failure = {"stage": "count_tokens", "kind": "input_over_limit"}
            self.events.emit("response", {"key": key, "outcome": r["outcome"] if not failure else "failure",
                                          "transport_outcome": r["outcome"], "transport_failure": r.get("failure"),
                                          "failure": failure, "body": body, "headers": r.get("headers"),
                                          "elapsed": r.get("elapsed"), "charged_usd": r["charged_usd"]})
            if failure:
                session.dead = True
                out[key] = None
                continue
            session.messages.append({"role": "assistant", "content": body["content"]})
            session.logged = len(session.messages)
            out[key] = body
        return out

    def tool_calls(self, key, body):
        return [b for b in body["content"] if b.get("type") == "tool_use"]

    def run_tools(self, key, session, body, ws, agent, phase, wave, memory=None, handler=None):
        results, counts = [], {"calls": 0, "errors": 0, "denied": 0}
        for block in self.tool_calls(key, body):
            name, args = block.get("name"), block.get("input")
            denied = False
            try:
                validate(session.toolset, name, args)
                if handler and name in ("run_check", "submit_verdict"):
                    content, error = handler(name, args)
                else:
                    content, error = ws.execute(agent, phase, wave, name, args, memory=memory), False
            except Denied as exc:
                content, error, denied = str(exc), True, True
            except ToolError as exc:
                content, error = str(exc), True
            counts["calls"] += 1
            counts["errors"] += error
            counts["denied"] += denied
            self.events.emit("tool", {"key": key, "agent": agent, "phase": phase, "tool_use_id": block.get("id"),
                                      "name": name, "input": args, "result": content, "is_error": error, "denied": denied})
            item = {"type": "tool_result", "tool_use_id": block.get("id"), "content": content}
            if error:
                item["is_error"] = True
            results.append(item)
        session.pending = results
        return counts

    # ---- proposal ---------------------------------------------------------
    def proposal(self, cases):
        state = {}
        for inst, draw in cases:
            ws = Workspace(inst)
            sessions = {a: Session(f"{inst['id']}/d{draw}/{a}", system_text(a, inst), "swarm") for a in AGENTS}
            for a, s in sessions.items():
                s.user([text(opening_text(a, ws, f"PROPOSAL PHASE, wave 1 of 2. You are {a}."))])
            state[(inst["id"], draw)] = {"inst": inst, "draw": draw, "ws": ws, "sessions": sessions,
                                         "tools": {a: {"calls": 0, "errors": 0, "denied": 0} for a in AGENTS}}
        for wave in (1, 2):
            items = []
            for st in state.values():
                for a in AGENTS:
                    s = st["sessions"][a]
                    if wave == 2 and not s.dead:
                        s.user(s.pending + [text(f"PROPOSAL PHASE, wave 2 of 2 (final). After this wave the module files are "
                                                 f"frozen.\n{board_text(st['ws'], 1, 'proposal')}\nCurrent files:\n{files_text(st['ws'])}")])
                    items.append((f"{s.sid}/p{wave}", s))
            bodies = self.wave(f"proposal-{wave}", items)
            for st in state.values():
                for a in AGENTS:
                    s = st["sessions"][a]
                    body = bodies.get(f"{s.sid}/p{wave}")
                    if body is not None:
                        c = self.run_tools(f"{s.sid}/p{wave}", s, body, st["ws"], a, "proposal", wave)
                        for k in c:
                            st["tools"][a][k] += c[k]
        for st in state.values():
            ws = st["ws"]
            st["snapshot"] = dict(ws.files)
            self.events.emit("snapshot", {"instance": st["inst"]["id"], "draw": st["draw"], "files": ws.files,
                                          "status": ws.status, "board": ws.board, "write_order": ws.write_order,
                                          "dead": [a for a in AGENTS if st["sessions"][a].dead], "tools": st["tools"]})
        return state

    def offline(self, st):
        inst, files = st["inst"], st["snapshot"]
        space = Space(inst, files)
        st["space"] = space
        wanted = full_verification(inst, files)["target"]
        shadow = "accept" if all(st["ws"].status.get(a) == "success" for a in AGENTS) else "reject"
        arms = {"A": {"decision": shadow, "class": classify(shadow, wanted), "spent": 0}}
        for arm in ARMS:
            for budget in BUDGETS:
                gate = Gateway(inst, files, budget)
                r = acquire(arm, space, gate.run, budget, {"write_order": st["ws"].write_order})
                r["class"] = classify(r["decision"], wanted)
                arms[f"{arm}@{budget}"] = r
        result = {"instance": inst["id"], "draw": st["draw"], "family": inst["family"], "control": inst["control"],
                  "distractor": inst["distractor"], "target": wanted, "hypotheses": len(space.hyps),
                  "initial_host_rule": host_rule(space, []), "arms": arms}
        self.events.emit("offline", result)
        return result

    # ---- live controllers -------------------------------------------------
    def controllers(self, specs, label, turns):
        for turn in range(1, turns + 1):
            active = [c for c in specs if not c["done"] and not c["session"].dead]
            if not active:
                break
            items = []
            for c in active:
                if turn > 1:
                    extra = [] if c["session"].pending else [text(f"Reminder: call run_check or submit_verdict ({turns - turn + 1} turns left).")]
                    c["session"].user(c["session"].pending + extra)
                items.append((f"{c['prefix']}/t{turn}", c["session"]))
            bodies = self.wave(f"{label}-t{turn}", items)
            for c in active:
                key = f"{c['prefix']}/t{turn}"
                body = bodies.get(key)
                c["turns"] = turn
                if body is None:
                    c["failure"] = True
                    continue
                handler = self._check_handler(c)
                counts = self.run_tools(key, c["session"], body, c["ws"], "challenger", "controller", turn, handler=handler)
                c["denied"] += counts["denied"]
                c["errors"] += counts["errors"]
        for c in specs:
            if c["verdict"] is None:
                c["verdict"] = "defer"
        return specs

    def _check_handler(self, c):
        def handle(name, args):
            if c["done"]:
                return "the verdict was already submitted", True
            if name == "submit_verdict":
                c["verdict"], c["explanation"], c["cited"] = args["verdict"], args["explanation"], args["cited_check_ids"]
                c["done"] = True
                return "verdict recorded", False
            gate = c["gateway"]
            try:
                result = gate.run(args["check_id"])
                body, error = f"{render_result(args['check_id'], result)}. Spent {gate.spent} of {gate.budget} units.", False
                if c["first_check"] is None:
                    c["first_check"] = args["check_id"]
            except CheckDenied as exc:
                body, error = f"refused (no charge): {exc}", True
                c["denied"] += 1
            obs = c["prior"] + gate.observations()
            used = set(c["carried_ids"]) | {e["check"] for e in gate.log}
            note_text, _ = advisor_note(c["arm"], c["space"], obs, gate.remaining, used)
            return f"{body}\n{note_text}", error
        return handle

    def controller_spec(self, prefix, arm, session, ws, inst, files, space, budget, prior=(), carried_ids=()):
        gate = Gateway(inst, files, budget)
        note_text, recommended = advisor_note(arm, space, list(prior), budget, set(carried_ids))
        return {"prefix": prefix, "arm": arm, "session": session, "ws": ws, "space": space, "gateway": gate,
                "prior": list(prior), "carried_ids": list(carried_ids), "done": False, "verdict": None, "explanation": None,
                "cited": [], "turns": 0, "denied": 0, "errors": 0, "failure": False, "first_check": None,
                "initial_note": note_text, "recommended": recommended}

    def controller_text(self, inst, files, turns, header):
        lines = [header,
                 f"You may buy evidence with run_check (one call per turn) from a budget of {PRIMARY_BUDGET} units, then call "
                 "submit_verdict with: accept (the frozen system satisfies all local and global constraints under the TRUE hidden "
                 "values), reject (it does not), model_mismatch (the observations are inconsistent with every listed combination "
                 f"of hidden values), or defer (you cannot decide). At most {turns} turns; without a verdict the result is defer. "
                 "Check results are exact and deterministic; a result marked MALFORMED carries no information.",
                 "Frozen files:\n" + files_text_from(inst, files),
                 "Local tests: " + ", ".join(f"{m['name']} {'pass' if local_report(inst, m, files)['pass'] else 'FAIL'}" for m in inst["modules"]),
                 "Candidate checks:\n" + catalog_text(inst)]
        return "\n\n".join(lines)

    def controller_result(self, c, st, wanted, phase):
        obs = c["prior"] + c["gateway"].observations()
        host = host_rule(c["space"], obs)
        result = {"instance": st["inst"]["id"], "draw": st["draw"], "family": st["inst"]["family"], "control": st["inst"]["control"],
                  "phase": phase, "arm": c["arm"], "target": wanted, "verdict": c["verdict"], "class": classify(c["verdict"], wanted),
                  "host_rule_on_agent_evidence": host, "host_class": classify(host, wanted), "agreement": host == c["verdict"],
                  "checks": c["gateway"].log, "spent": c["gateway"].spent, "turns": c["turns"], "denied": c["denied"],
                  "tool_errors": c["errors"], "failure": c["failure"] or c["session"].dead, "explanation": c["explanation"],
                  "cited": c["cited"], "first_check": c["first_check"], "recommended": c["recommended"],
                  "complied": (c["first_check"] in c["recommended"]) if c["first_check"] else None,
                  "initial_note": c["initial_note"]}
        self.events.emit("controller", result)
        return result

    def arm_order(self, inst, arms):
        order = list(arms)
        random.Random(inst["arm_seed"]).shuffle(order)
        return order

    def live_controllers(self, state, l0_ids):
        specs = []
        for st in state.values():
            inst, files, chal = st["inst"], st["snapshot"], st["sessions"]["challenger"]
            arms = ["L-B", "L-C"] + (["L-0"] if inst["id"] in l0_ids else [])
            st["controllers"] = {}
            for arm in self.arm_order(inst, arms):
                session = chal.fork(f"{chal.sid}/ctl-{arm}")
                session.parallel = False
                c = self.controller_spec(f"{session.sid}", arm, session, st["ws"].fork(), inst, files, st["space"], PRIMARY_BUDGET)
                if not chal.dead:
                    session.user(session.pending + [text(self.controller_text(inst, files, CONTROLLER_TURNS,
                                 "CONTROLLER PHASE. The proposal waves are over and the module files are frozen. You are now the "
                                 "verification controller for this snapshot.")), text(c["initial_note"])])
                st["controllers"][arm] = c
                specs.append(c)
        self.controllers(specs, "controller", CONTROLLER_TURNS)
        results = []
        for st in state.values():
            wanted = full_verification(st["inst"], st["snapshot"])["target"]
            for arm, c in st["controllers"].items():
                results.append(self.controller_result(c, st, wanted, "controller"))
        return results

    # ---- repair -------------------------------------------------------------
    def repair(self, state, repair_ids):
        branches = []
        for st in state.values():
            inst = st["inst"]
            if inst["id"] not in repair_ids:
                continue
            for arm in self.arm_order(inst, ["L-B", "L-C"]):
                ctl = st["controllers"][arm]
                ws = st["ws"].fork()
                sessions = {a: st["sessions"][a].fork(f"{st['sessions'][a].sid}/rep-{arm}") for a in AGENTS if a != "challenger"}
                sessions["challenger"] = ctl["session"].fork(f"{ctl['session'].sid}/rep")
                checks = "; ".join(f"{e['check']} -> {e['result']}" for e in ctl["gateway"].log) or "none"
                report = (f"REPAIR PHASE, wave 1 of 2. The controller verified the frozen snapshot. Checks run: {checks}. "
                          f"Controller verdict: {ctl['verdict']}"
                          + (f" ({ctl['explanation']})" if ctl["explanation"] else "") +
                          ". You may revise your files (write_file is enabled again for owners), then the files are re-verified.")
                branches.append({"st": st, "arm": arm, "ws": ws, "sessions": sessions, "report": report, "ctl": ctl})
        for wave in (1, 2):
            items = []
            for b in branches:
                for a in AGENTS:
                    s = b["sessions"][a]
                    if s.dead:
                        continue
                    msg = b["report"] if wave == 1 else (f"REPAIR PHASE, wave 2 of 2 (final). After this wave the files are frozen "
                                                         f"and re-verified.\n{board_text(b['ws'], 1, 'repair')}\nCurrent files:\n{files_text(b['ws'])}")
                    s.user(s.pending + [text(msg)])
                    items.append((f"{s.sid}/r{wave}", s))
            bodies = self.wave(f"repair-{wave}", items)
            for b in branches:
                for a in AGENTS:
                    s = b["sessions"][a]
                    body = bodies.get(f"{s.sid}/r{wave}")
                    if body is not None:
                        self.run_tools(f"{s.sid}/r{wave}", s, body, b["ws"], a, "repair", wave)
        specs = []
        for b in branches:
            st, inst = b["st"], b["st"]["inst"]
            files = dict(b["ws"].files)
            b["files"] = files
            space = Space(inst, files)
            old = b["ctl"]["prior"] + b["ctl"]["gateway"].observations()
            carried = [(cid, r) for cid, r in old if space.checks[cid]["kind"] in ("probe", "sum_probe", "measure")]
            chal = b["sessions"]["challenger"]
            c = self.controller_spec(f"{chal.sid}/ctl", b["arm"], chal, b["ws"], inst, files, space, PRIMARY_BUDGET,
                                     prior=carried, carried_ids=[cid for cid, _ in carried])
            if not chal.dead:
                chal.user(chal.pending + [text(self.controller_text(inst, files, REPAIR_CONTROLLER_TURNS,
                          "REPAIR VERIFICATION. The repaired files are frozen. You are again the verification controller, with 4 new "
                          "budget units. Earlier probe/measure results about hidden parameters remain valid; earlier integration and "
                          "local-test results referred to the old files.")), text(c["initial_note"])])
            b["spec"] = c
            specs.append(c)
        self.controllers(specs, "repair-controller", REPAIR_CONTROLLER_TURNS)
        results = []
        for b in branches:
            st = b["st"]
            grade = full_verification(st["inst"], b["files"])
            res = self.controller_result(b["spec"], st, grade["target"], "repair")
            out = {"instance": st["inst"]["id"], "draw": st["draw"], "family": st["inst"]["family"], "arm": b["arm"],
                   "files": b["files"], "grader": grade, "controller": res,
                   "before": full_verification(st["inst"], st["snapshot"])["system_passes"]}
            self.events.emit("repair", out)
            results.append(out)
        return results

    # ---- RSI ----------------------------------------------------------------
    def rsi(self, cases):
        runs = []
        for inst, draw in cases:
            v2 = build_v2(inst)
            for arm in self.arm_order(inst, ["C", "D"]):
                ws = Workspace(inst)
                runs.append({"inst": inst, "v2": v2, "draw": draw, "arm": arm, "ws": ws, "memory": Memory(bound=arm == "D"),
                             "prefix": f"{inst['id']}/d{draw}/rsi-{arm}"})

        def fresh(run, phase_tag, ws, header):
            sessions = {}
            for a in AGENTS:
                s = Session(f"{run['prefix']}/{phase_tag}/{a}", system_text(a, ws.instance, rsi=True), "rsi")
                s.user([text(opening_text(a, ws, header.format(agent=a)))])
                sessions[a] = s
            return sessions

        def go(phase, tag, wave, message):
            items = []
            for run in runs:
                for a in AGENTS:
                    s = run["sessions"][a]
                    if s.dead:
                        continue
                    if message is not None:
                        s.user(s.pending + [text(message(run, a))])
                    items.append((f"{s.sid}/{tag}{wave}", s))
            bodies = self.wave(f"rsi-{tag}{wave}", items)
            for run in runs:
                for a in AGENTS:
                    s = run["sessions"][a]
                    body = bodies.get(f"{s.sid}/{tag}{wave}")
                    if body is not None:
                        self.run_tools(f"{s.sid}/{tag}{wave}", s, body, run["ws"], a, phase, wave, memory=run["memory"])

        for run in runs:
            run["sessions"] = fresh(run, "learn", run["ws"], "LEARN PHASE, wave 1 of 2. You are {agent}.")
        go("rsi_learn", "l", 1, None)

        def postmortem(run, a):
            g = full_verification(run["inst"], run["ws"].files)
            gl = ", ".join(f"{k} {'pass' if v else 'FAIL'}" for k, v in g["global"].items())
            lo = ", ".join(f"{k} {'pass' if v else 'FAIL'}" for k, v in g["local"].items())
            measured = ", ".join(f"{k}={v}" for k, v in run["inst"]["truth"].items())
            return (f"LEARN PHASE, wave 2 of 2. POSTMORTEM from production verification of the current files: local tests {lo}; "
                    f"global constraints {gl}. Measured hidden values in this deployment: {measured}. Fix what you own and "
                    f"record durable lessons and obligations in team memory.\n{board_text(run['ws'], 1, 'rsi_learn')}")
        for run in runs:
            run["learn_grade"] = full_verification(run["inst"], run["ws"].files)
        go("rsi_learn", "l", 2, postmortem)
        for run in runs:
            run["learn_final"] = full_verification(run["inst"], run["ws"].files)
            run["ws"] = run["ws"].fork(instance=run["v2"])
            run["sessions"] = fresh(run, "restart", run["ws"],
                                    "RESTART PHASE, wave 1 of 2. You are {agent}, starting a fresh session; earlier sessions ended. "
                                    "Team memory persists. Contracts may have been revised since the files were written. This is an "
                                    "orientation phase: write_file is disabled; read, recall and reconcile memory, and post notes.")
        go("rsi_restart", "s", 1, None)
        go("rsi_restart", "s", 2, lambda run, a: f"RESTART PHASE, wave 2 of 2 (orientation; write_file disabled).\n{board_text(run['ws'], 1, 'rsi_restart')}")
        go("rsi_use", "u", 1, lambda run, a: f"USE PHASE, wave 1 of 2. write_file is enabled. Make the system satisfy the CURRENT contracts.\n"
                                             f"{board_text(run['ws'], 1, 'rsi_restart')}")
        go("rsi_use", "u", 2, lambda run, a: f"USE PHASE, wave 2 of 2 (final). After this wave the files are frozen and verified.\n"
                                             f"{board_text(run['ws'], 1, 'rsi_use')}\nCurrent files:\n{files_text(run['ws'])}")
        results = []
        for run in runs:
            grade = full_verification(run["v2"], run["ws"].files)
            out = {"instance": run["inst"]["id"], "draw": run["draw"], "family": run["inst"]["family"], "arm": run["arm"],
                   "files": run["ws"].files, "learn_grade": run["learn_grade"], "learn_final": run["learn_final"], "grader": grade,
                   "memory": run["memory"].state(), "dead": [a for a in AGENTS if run["sessions"][a].dead]}
            self.events.emit("rsi", out)
            results.append(out)
        return results

    # ---- driver -------------------------------------------------------------
    def run(self):
        cfg = self.config
        cases = [(self.index[i], d) for i in cfg["instances"] for d in cfg["draws"]]
        summary = {"part": cfg["part"], "chunk": cfg["chunk"], "split": cfg["split"]}
        if cfg["part"] == "swarm":
            state = self.proposal(cases)
            summary["offline"] = [self.offline(st) for st in state.values()]
            summary["controllers"] = self.live_controllers(state, set(cfg["l0"]))
            summary["repair"] = self.repair(state, set(cfg["repair"]))
        else:
            summary["rsi"] = self.rsi(cases)
        summary["resolved_model"] = self.expected_model
        self.events.emit("summary", {"part": cfg["part"], "chunk": cfg["chunk"], "resolved_model": self.expected_model,
                                     "counts": {k: len(v) for k, v in summary.items() if isinstance(v, list)}})
        return summary


def files_text_from(inst, files):
    return "\n".join(f"--- {m['file']}\n{files[m['file']]}" for m in inst["modules"])


def chunk_config(data, split, part, chunk, resolved_model=None):
    subsets = data["subsets"]
    if split == "development":
        ids = [i["id"] for i in data["development"]]
        l0, repair, rsi = subsets["dev_l0"], subsets["dev_repair"], subsets["dev_rsi"]
        draws = [0]
        if part == "rsi":
            ids = rsi
        if chunk != 0:
            raise ValueError("development has a single chunk")
    else:
        l0, repair, rsi = subsets["l0"], subsets["repair"], subsets["rsi"]
        draws = DRAWS
        ids = [i["id"] for i in data["evaluation"]] if part == "swarm" else rsi
        size = SWARM_CHUNK if part == "swarm" else RSI_CHUNK
        # Interleave families inside each chunk.
        families = {}
        for i in ids:
            families.setdefault(next(x["family"] for x in data["evaluation"] if x["id"] == i), []).append(i)
        mixed = [x for group in zip(*families.values()) for x in group] + [x for g in families.values() for x in g[min(map(len, families.values())):]]
        ids = mixed[chunk * size:(chunk + 1) * size]
        if not ids:
            raise ValueError("chunk out of range")
    return {"split": split, "part": part, "chunk": chunk, "instances": ids, "draws": draws, "l0": l0, "repair": repair,
            "chunk_seed": int(hashlib.sha256(f"{split}/{part}/{chunk}".encode()).hexdigest()[:8], 16),
            "resolved_model": resolved_model}


def source_hashes():
    paths = sorted(list((ROOT / "code" / "operations" / "swarm").glob("*.py")) + list(HERE.glob("*.py"))
                   + [HERE / "PROTOCOL.md", HERE / "instances.json"])
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def replay(path):
    records = load_events(path)
    meta = records[0]["data"]
    if records[0]["kind"] != "start":
        raise ValueError("first event must be start")
    if meta["source_hashes"] != source_hashes():
        raise ValueError("source freeze differs")
    data = load()
    if digest(data) != meta["instances_sha256"]:
        raise ValueError("instances differ")
    recorded, requests = {}, {}
    for r in records:
        d = r["data"]
        if r["kind"] == "request":
            requests[d["key"]] = d
        elif r["kind"] == "response":
            result = {"outcome": d["transport_outcome"], "count": requests[d["key"]]["count"], "elapsed": d["elapsed"]}
            if d["transport_outcome"] == "ok":
                result.update(body=d["body"], headers=d["headers"])
            elif d["transport_outcome"] == "failure":
                result["failure"] = d["transport_failure"]
            recorded[d["key"]] = {"payload_sha256": requests[d["key"]]["payload_sha256"], "result": result}
    events = Events(expected=records)
    events.emit("start", meta)
    ledger = Ledger(None, meta["config"]["split"], persist=False)
    transport = ReplayTransport(recorded, meta["sdk_version"])
    campaign = Campaign(data, meta["config"], transport, ledger, events)
    try:
        summary = campaign.run()
    except HaltRun as error:
        events.emit("halted", {"reason": str(error)})
        summary = None
    if len(events.records) != len(records):
        raise ValueError("trailing events in recording")
    return {"replayed": True, "events": len(records), "complete": summary is not None,
            "summary_sha256": digest(json.loads(json.dumps(summary))) if summary is not None else None}


def execute(data, config, transport, ledger, out, model_info, commit, hashes):
    """Run one chunk, writing events.jsonl(.gz) and summary.json into `out`."""
    events = Events(out / "events.jsonl")
    meta = {"schema": "lggr.rsi_swarm.events.v1", "config": config, "source_hashes": hashes, "source_commit": commit,
            "instances_sha256": digest(data), "sdk_version": transport.sdk_version, "api_version": API_VERSION,
            "model": MODEL, "model_info": model_info, "recovered_reservations": ledger.recovered}
    events.emit("start", meta)
    campaign = Campaign(data, config, transport, ledger, events)
    try:
        summary = campaign.run()
    except HaltRun as error:
        events.emit("halted", {"reason": str(error)})
        raise
    (out / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return compress(out / "events.jsonl"), summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "replay"])
    parser.add_argument("path")
    parser.add_argument("--split", choices=["development", "evaluation"])
    parser.add_argument("--part", choices=["swarm", "rsi"])
    parser.add_argument("--chunk", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=16)
    parser.add_argument("--min-interval", type=float, default=0.0)
    parser.add_argument("--resolved-model", default=None)
    args = parser.parse_args()
    if args.mode == "replay":
        print(json.dumps(replay(args.path)))
        return
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    hashes = source_hashes()
    for name, value in hashes.items():
        blob = subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != value:
            raise SystemExit("live source is not committed: " + name)
    data = load()
    config = chunk_config(data, args.split, args.part, args.chunk, args.resolved_model)
    out = Path(args.path)
    out.mkdir(parents=True, exist_ok=False)
    ledger = Ledger(HERE / "evidence" / "ledger.json", args.split)
    transport = AnthropicTransport(concurrency=args.concurrency, min_interval=args.min_interval)
    try:
        execute(data, config, transport, ledger, out, transport.model_info(), commit, hashes)
    except HaltRun as error:
        raise SystemExit("halted: " + str(error))
    print(json.dumps({"complete": True, "chunk": args.chunk, "part": args.part, "ledger": ledger.summary()}))


if __name__ == "__main__":
    sys.exit(main())
