"""Concurrent API waves; deterministic tool application and independent judging."""
import argparse
from copy import deepcopy
from contextlib import ExitStack
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import zipfile

from experiments.live_five_agent_swarm.client import Events, RunStopped, MODELS
from experiments.live_five_agent_swarm.domain import Board, fixture, findings, local_ok, certificates
from experiments.live_five_agent_swarm.oracle import feasible, judge
from experiments.live_five_agent_swarm.runner import inject, system, gate
from .client import BatchClient

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SEEDS = {"development": [5100], "evaluation": list(range(5200, 5218))}
PRIOR_SPEND = Decimal("0.57951748")


def source_hashes():
    paths = list(HERE.glob("*.py")) + [HERE / "PROTOCOL.md"]
    paths += list((ROOT / "experiments/live_five_agent_swarm").glob("*.py"))
    paths += list((ROOT / "lggr").glob("*.py"))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def capacity_diagnostics(state):
    """Conventional exhaustive Hall check, independent of the matching judge.

    Available equally to B and C. Returns a deficiency witness, never a repair.
    """
    occupied = {p["slot"] for p in state["completed"].values()}
    pending = [j for j in state["jobs"] if j["id"] not in state["completed"]]
    choices = {j["id"]: set(j["allowed_slots"]) & set(state["active_slots"]) - occupied for j in pending}
    for size in range(1, len(pending)+1):
        for subset in itertools.combinations(sorted(choices), size):
            slots = sorted(set().union(*(choices[w] for w in subset)))
            if len(slots) < size:
                return {"feasible": False, "workers": list(subset), "available_slots": slots,
                        "required": size, "available": len(slots)}
    return {"feasible": True, "scope": "exact finite Hall check; no assignment supplied"}


def agent_session(events, board, history, worker, feedback):
    index = int(worker.rsplit("-", 1)[1])
    history.append({"role": "user", "content": json.dumps({"instruction": "Inspect, then act on your own pending job.", "feedback": feedback}, sort_keys=True)})
    events.emit("agent_turn", {"worker": worker, "model": MODELS[index], "feedback": feedback})
    inspected = False
    for _ in range(4):
        try:
            message = yield (MODELS[index], history)
        except ValueError as error:
            events.emit("invalid_model_output", {"worker": worker, "reason": str(error)})
            return False
        history.append(message)
        calls = message.get("tool_calls", [])
        if not isinstance(calls, list) or len(calls) > 8:
            events.emit("invalid_model_output", {"worker": worker, "reason": "invalid tool call list"})
            return False
        if not calls:
            history.append({"role": "user", "content": "Use inspect_board and then propose or escalate; prose alone cannot change the workspace."})
            continue
        done, escalation = False, False
        if any(not isinstance(call, dict) or not isinstance(call.get("function"), dict)
               or not isinstance(call.get("id"), str) or not call["id"]
               or call.get("type") != "function"
               or not isinstance(call["function"].get("name"), str)
               or not isinstance(call["function"].get("arguments"), str) for call in calls):
            events.emit("invalid_model_output", {"worker": worker, "reason": "invalid tool call shape"})
            return False
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


def round_turns(client, events, board, histories, workers, feedback):
    # Advance all sessions to their next model request before issuing a wave.
    # Network calls overlap; tool results are applied in stable worker order.
    generators = {w: agent_session(events, board, histories[w], w, feedback) for w in workers}
    pending, escalations = {}, 0
    for w, gen in generators.items():
        pending[w] = next(gen)
    while pending:
        answers = client.batch(list(pending.values()))
        following = {}
        for (w, _), answer in zip(pending.items(), answers):
            try:
                following[w] = generators[w].throw(answer) if isinstance(answer, Exception) else generators[w].send(answer)
            except StopIteration as stop:
                escalations += int(bool(stop.value))
        pending = following
    return escalations


def campaign(client, events, config, output=None):
    with ExitStack() as resources:
        return _campaign(client, events, config, output, resources)


def _campaign(client, events, config, output, resources):
    results = []
    for seed in config["seeds"]:
        kind = ("withdrawal", "infeasible", "control")[config["seeds"].index(seed) % 3]
        state = fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": kind, "fixture": state})
        board = Board(state, output / f"{seed}-baseline.sqlite" if output else ":memory:")
        resources.callback(board.close)
        histories = {j["id"]: [{"role": "system", "content": system(j["id"])}] for j in state["jobs"]}
        base_calls, base_cost = client.calls, client.spent
        for initial_pass in range(4):
            round_turns(client, events, board, histories, list(histories), {"phase": "initial", "pass": initial_pass, "findings": findings(board.state), "capacity": capacity_diagnostics(board.state)})
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
            for repair_pass in range(3):
                if not errors:
                    break
                blocked += 1
                if arm == "A":
                    feedback = {"phase": "recovery", "message": "The combined plan cannot execute. Reinspect the workspace and reconsider your own plan."}
                else:
                    feedback = {"phase": "recovery", "findings": errors, "capacity": capacity_diagnostics(work.state)}
                    if arm == "C":
                        feedback["lggr"] = cert
                escalations += round_turns(client, events, work, history, ["worker-2", "worker-3", "worker-4"], feedback)
                turns += 3
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
    summary = {"schema": "lggr.concurrent_five_agent_pilot.v1", "authority_effect": "None", "cases": results,
               "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent),
               "max_inflight_requests": client.max_inflight, "concurrent_waves": client.concurrent_waves,
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
    if config["seeds"] != SEEDS[config["phase"]] or config["models"] != MODELS:
        raise ValueError("configuration differs from the frozen protocol")
    events = Events(expected=records)
    events.emit("start", metadata)
    client = BatchClient(events, config["budget_usd"], source=records)
    try:
        summary = campaign(client, events, config)
    except RunStopped as error:
        summary = {"reason": str(error), "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent)}
        events.emit("stopped", summary)
    if len(events.records) != len(records):
        raise ValueError("trailing events")
    saved = Path(path).with_name("summary.json")
    if saved.exists() and json.loads(saved.read_text(encoding="utf-8")) != summary:
        raise ValueError("saved summary differs from derived replay")
    return summary


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+"\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "replay"])
    parser.add_argument("path")
    parser.add_argument("--phase", choices=list(SEEDS), default="evaluation")
    parser.add_argument("--budget", default="4")
    args = parser.parse_args()
    if args.mode == "replay":
        summary = replay(args.path)
        print(json.dumps({"replayed": True, "api_attempts": summary["api_attempts"], "cases": len(summary.get("cases", []))}))
        return
    limit = Decimal(args.budget)
    if not limit.is_finite() or not 0 < limit <= 10-PRIOR_SPEND:
        raise ValueError("budget must fit remaining pilot allowance")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    hashes = source_hashes()
    for name, digest in hashes.items():
        blob = subprocess.check_output(["git", "show", commit+":"+name], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != digest:
            raise ValueError("live source is not committed: " + name)
    output = Path(args.path).resolve()
    evidence = (HERE/"evidence").resolve()
    if output.parent != evidence:
        raise ValueError("live runs must reside directly in this experiment's evidence directory")
    evidence.mkdir(exist_ok=True)
    ledger_path = evidence/"budget.json"
    # This exclusive lock is held for the run. A crash retains the full allocation
    # and lock; recovery requires reconciling evidence before another paid run.
    with (evidence/"budget.lock").open("x", encoding="utf-8") as lock:
        lock.write(commit)
    client = None
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {
            "ceiling_usd": "10", "prior_pilot_usd": str(PRIOR_SPEND), "runs": []}
        if ledger["ceiling_usd"] != "10" or ledger["prior_pilot_usd"] != str(PRIOR_SPEND):
            raise ValueError("budget ledger header differs")
        used = PRIOR_SPEND + sum(Decimal(r["charged_or_reserved_usd"]) for r in ledger["runs"])
        if used + limit > 10:
            raise ValueError("cumulative pilot budget would be exceeded")
        output.mkdir(exist_ok=False)
        ledger["runs"].append({"path": output.name, "status": "reserved", "charged_or_reserved_usd": str(limit)})
        write_json(ledger_path, ledger)
        config = {"phase": args.phase, "seeds": SEEDS[args.phase], "models": MODELS,
                  "budget_usd": str(limit), "prior_charged_or_reserved_usd": str(used)}
        events = Events(output/"events.jsonl")
        metadata = {"schema": "lggr.concurrent_five_agent_events.v1", "source_commit": commit,
                    "source_hashes": hashes, "config": config}
        events.emit("start", metadata)
        with zipfile.ZipFile(output/"source_snapshot.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for name in hashes:
                archive.writestr(name, (ROOT/name).read_bytes())
        client = BatchClient(events, limit)
        try:
            summary = campaign(client, events, config, output)
        except RunStopped as error:
            summary = {"reason": str(error), "api_attempts": client.calls, "charged_or_reserved_usd": str(client.spent)}
            events.emit("stopped", summary)
        write_json(output/"summary.json", summary)
        ledger["runs"][-1].update(status="settled", charged_or_reserved_usd=str(client.spent))
        write_json(ledger_path, ledger)
        print(json.dumps({"complete": "cases" in summary, "calls": client.calls, "charged_usd": str(client.spent),
                          "pilot_total_usd": str(used+client.spent)}), flush=True)
    finally:
        # Unexpected failures retain their full ledger reservation.
        (evidence/"budget.lock").unlink()


if __name__ == "__main__":
    main()
