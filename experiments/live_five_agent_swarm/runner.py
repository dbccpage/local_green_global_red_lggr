"""Five live tool-using agents, paired fault recovery arms, and offline replay."""
import argparse
from copy import deepcopy
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import subprocess

from .client import Events, LiveClient, ReplayClient, RunStopped, MODELS
from .domain import Board, fixture, findings, local_ok, certificates
from .oracle import feasible, judge

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TOOLS = [
    {"type": "function", "function": {"name": "inspect_board", "description": "Read current invoice items, allowed and active slots, epoch, peer proposals and immutable completed work.",
      "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "calculate_total", "description": "Compute exact arithmetic on your supplied invoice line items. This does not choose slots or repair allocations.",
      "parameters": {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"unit_cents": {"type": "integer"}, "quantity": {"type": "integer"}}, "required": ["unit_cents", "quantity"], "additionalProperties": False}}},
                     "required": ["items"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "propose", "description": "Submit or revise ONLY your own invoice total and slot at the observed epoch. Admission is checked separately.",
      "parameters": {"type": "object", "properties": {"slot": {"type": "string"}, "total_cents": {"type": "integer"}, "epoch": {"type": "integer"}},
                     "required": ["slot", "total_cents", "epoch"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "escalate", "description": "Report why completion cannot currently be justified, without changing work or inventing resources.",
      "parameters": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"], "additionalProperties": False}}},
]


def source_hashes():
    paths = list(HERE.glob("*.py")) + [HERE / "PROTOCOL.md"] + list((ROOT / "lggr").glob("*.py"))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def system(worker):
    return (f"You are autonomous dispatch agent {worker}, one of five peer workers. You own ONLY the job with your worker ID. "
            "Use inspect_board before acting. Use calculate_total with your source item list for invoice arithmetic. "
            "Choose an allowed, currently active slot not used by another worker, and use the CURRENT epoch. "
            "Inspect peer proposals: preserve nonconflicting claims where possible; if competing, lower worker ID has priority. "
            "Only tool calls propose or escalate count as actions. Never change another worker's work. "
            "Completed work is immutable. After resource changes, revise your pending proposal or escalate with a concrete reason "
            "if you cannot justify a complete unique allocation. Do not invent slots or alter source items. "
            "You may inspect the board more than once. No solution oracle is available to you.")


def agent_turn(client, events, board, history, worker, feedback):
    index = int(worker.rsplit("-", 1)[1])
    history.append({"role": "user", "content": json.dumps({"instruction": "Inspect, then act on your own pending job.", "feedback": feedback}, sort_keys=True)})
    events.emit("agent_turn", {"worker": worker, "model": MODELS[index], "feedback": feedback})
    inspected = False
    for _ in range(4):
        try:
            message = client.complete(MODELS[index], history)
        except ValueError as error:
            events.emit("invalid_model_output", {"worker": worker, "reason": str(error)})
            return False
        history.append(message)
        calls = message.get("tool_calls", [])
        if not isinstance(calls, list) or len(calls) > 8:
            events.emit("invalid_model_output", {"worker": worker, "reason": "invalid tool call list"})
            return False
        if any(not isinstance(call, dict) or not isinstance(call.get("function"), dict) for call in calls):
            events.emit("invalid_model_output", {"worker": worker, "reason": "invalid tool call shape"})
            return False
        if not calls:
            history.append({"role": "user", "content": "Use inspect_board and then propose or escalate; prose alone cannot change the workspace."})
            continue
        done, escalation = False, False
        for call in calls:
            function = call.get("function", {})
            name = function.get("name")
            try:
                def unique(pairs):
                    d = {}
                    for key, value in pairs:
                        if key in d:
                            raise ValueError("duplicate field")
                        d[key] = value
                    return d
                args = json.loads(function.get("arguments", ""), object_pairs_hook=unique)
                if not isinstance(args, dict):
                    raise ValueError("arguments must be an object")
                if name != "inspect_board" and not inspected:
                    result = {"accepted": False, "error": "inspect the current board before acting"}
                else:
                    result = board.tool(worker, name, args)
                    inspected |= name == "inspect_board" and "jobs" in result
            except (ValueError, TypeError, KeyError):
                result = {"accepted": False, "error": "malformed tool arguments"}
            events.emit("tool", {"worker": worker, "call": call, "result": result})
            history.append({"role": "tool", "tool_call_id": call.get("id", "missing"), "content": json.dumps(result, sort_keys=True)})
            done |= result.get("accepted") is True or result.get("escalated") is True
            escalation |= result.get("escalated") is True
        if done:
            return escalation
    events.emit("agent_turn_exhausted", {"worker": worker})
    return False


def inject(before, kind):
    state = deepcopy(before)
    if kind == "control":
        return state, {"kind": kind, "removed_slots": []}
    state["epoch"] += 1
    completed = {p["slot"] for p in state["completed"].values()}
    if kind == "infeasible":
        remaining = sorted(set(state["active_slots"]) - completed)[:2]
        state["active_slots"] = sorted(completed | set(remaining))
        assert not feasible(state)
    else:
        occupied = sorted({p["slot"] for w, p in state["proposals"].items() if w not in state["completed"]})
        for slot in occupied:
            state["active_slots"] = [s for s in before["active_slots"] if s != slot]
            if feasible(state):
                break
        else:
            raise ValueError("fixture offers no feasible occupied-slot withdrawal")
    return state, {"kind": kind, "removed_slots": sorted(set(before["active_slots"]) - set(state["active_slots"])),
                   "old_epoch": before["epoch"], "new_epoch": state["epoch"]}


def gate(events, before, board, arm):
    errors = findings(board.state)
    cert = certificates(before, board.state) if arm == "C" else None
    local = [local_ok(j, board.state["completed"].get(j["id"]) or board.state["proposals"].get(j["id"])) for j in board.state["jobs"]]
    events.emit("gate", {"arm": arm, "findings": errors, "local_verdicts": local,
                         "global_pass": not errors, "certificate": cert})
    return errors, cert, all(local) and bool(errors)


def campaign(client, events, config, output=None):
    with ExitStack() as resources:
        return _campaign(client, events, config, output, resources)


def _campaign(client, events, config, output, resources):
    results = []
    for seed in config["seeds"]:
        kind = "withdrawal" if seed in (3101, 4101, 4102) else "infeasible" if seed in (4103, 4104) else "control"
        state = fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": kind, "fixture": state})
        board = Board(state, output / f"{seed}-baseline.sqlite" if output else ":memory:")
        resources.callback(board.close)
        histories = {j["id"]: [{"role": "system", "content": system(j["id"])}] for j in state["jobs"]}
        base_calls, base_cost = client.calls, client.spent
        for initial_pass in range(2):
            for worker, history in histories.items():
                agent_turn(client, events, board, history, worker, {"phase": "initial", "pass": initial_pass, "findings": findings(board.state)})
            if not findings(board.state):
                break
        if findings(board.state):
            result = {"seed": seed, "kind": kind, "baseline_failed": True, "arms": [],
                      "baseline_calls": client.calls-base_calls, "baseline_cost_usd": str(client.spent-base_cost)}
            events.emit("case_result", result)
            results.append(result)
            board.close()
            continue
        executed = board.execute(["worker-0", "worker-1"])
        events.emit("initial_execution", executed)
        before, preserved = deepcopy(board.state), board.rows()
        after, fault = inject(before, kind)
        events.emit("intervention", {"fault": fault, "state": after, "oracle_feasible": feasible(after)})
        board.close()
        baseline_calls = client.calls - base_calls
        baseline_cost = client.spent - base_cost
        arms = []
        order = ["A", "B", "C"]
        order = order[seed % 3:] + order[:seed % 3]
        for arm in order:
            work = Board(after, output / f"{seed}-{arm}.sqlite" if output else ":memory:")
            resources.callback(work.close)
            history = deepcopy(histories)
            events.emit("arm_start", {"seed": seed, "arm": arm, "state": after})
            calls, cost, escalations, blocked, turns = client.calls, client.spent, 0, 0, 0
            errors, cert, initial_ngd = gate(events, before, work, arm)
            for repair_pass in range(2):
                if not errors:
                    break
                blocked += 1
                if arm == "A":
                    feedback = {"phase": "recovery", "message": "The combined plan cannot execute. Reinspect the workspace and reconsider your own plan."}
                else:
                    feedback = {"phase": "recovery", "findings": errors}
                    if arm == "C":
                        feedback["lggr"] = cert
                for worker in ("worker-2", "worker-3", "worker-4"):
                    escalations += int(agent_turn(client, events, work, history[worker], worker, feedback))
                    turns += 1
                errors, cert, _ = gate(events, before, work, arm)
            execution = work.execute(["worker-2", "worker-3", "worker-4"])
            events.emit("execution", {"arm": arm, **execution})
            verdict = judge(work.state, work.rows(), preserved)
            outcome = ("completed" if verdict["complete"] else "safe_escalated" if not verdict["feasible"] and escalations else "blocked_unresolved")
            result = {"arm": arm, "outcome": outcome, "judge": verdict,
                      "initial_local_green_global_red": initial_ngd, "blocked_attempts": blocked,
                      "agent_turns": turns, "agent_escalations": escalations, "api_attempts": client.calls-calls,
                      "cost_usd": str(client.spent-cost), "rows": work.rows()}
            events.emit("arm_result", result)
            arms.append(result)
            work.close()
        result = {"seed": seed, "kind": kind, "baseline_failed": False, "arms": arms,
                  "baseline_calls": baseline_calls, "baseline_cost_usd": str(baseline_cost)}
        events.emit("case_result", result)
        results.append(result)
        if output:
            print(json.dumps({"seed": seed, "kind": kind, "outcomes": {a["arm"]: a["outcome"] for a in arms}, "charged_usd": str(client.spent)}), flush=True)
    summary = {"schema": "lggr.live_five_agent_pilot.v1", "authority_effect": "None", "cases": results,
               "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent),
               "invalid_execution_count": sum(not a["judge"]["valid_execution"] for r in results for a in r["arms"]),
               "scope": "Paired synthetic fault-injection pilot; descriptive outcomes, no population rate or superiority claim."}
    events.emit("summary", summary)
    return summary


def replay(path):
    records = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
    metadata = records[0]["data"]
    if records[0]["kind"] != "start" or metadata["source_hashes"] != source_hashes():
        raise ValueError("source freeze differs")
    config = metadata["config"]
    expected_seeds = [3101] if config["development"] else list(range(4101, 4107))
    if config["seeds"] != expected_seeds or config["models"] != MODELS or not 0 < float(config["budget_usd"]) <= 10:
        raise ValueError("configuration differs from the frozen protocol")
    events = Events(expected=records)
    events.emit("start", metadata)
    client = ReplayClient(events, records)
    try:
        result = campaign(client, events, config)
    except RunStopped as error:
        result = {"reason": str(error), "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent)}
        events.emit("stopped", result)
    if len(events.records) != len(records):
        raise ValueError("trailing events")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "replay"])
    parser.add_argument("path")
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--budget", type=float, default=10)
    args = parser.parse_args()
    if args.mode == "replay":
        summary = replay(args.path)
        saved = Path(args.path).with_name("summary.json")
        if saved.exists() and json.loads(saved.read_text(encoding="utf-8")) != summary:
            raise ValueError("saved summary differs from replay")
        print(json.dumps({"replayed": True, "api_attempts": summary["api_attempts"],
                          "cases": len(summary.get("cases", [])),
                          "status": "complete" if "cases" in summary else "stopped"}))
        return
    if not 0 < args.budget <= 10:
        raise ValueError("pilot budget must be in (0, 10]")
    output = Path(args.path)
    output.mkdir(parents=True, exist_ok=False)
    config = {"seeds": [3101] if args.development else list(range(4101, 4107)),
              "budget_usd": str(args.budget), "models": MODELS, "development": args.development}
    events = Events(output / "events.jsonl")
    metadata = {"schema": "lggr.live_five_agent_events.v1", "config": config,
                "source_hashes": source_hashes(), "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    events.emit("start", metadata)
    client = LiveClient(events, args.budget)
    try:
        summary = campaign(client, events, config, output)
    except RunStopped as error:
        events.emit("stopped", {"reason": str(error), "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent)})
        raise SystemExit(str(error))
    (output / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"complete": True, "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent)}))


if __name__ == "__main__":
    main()
