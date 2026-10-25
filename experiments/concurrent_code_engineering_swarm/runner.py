"""Concurrent multi-agent code-engineering swarm runner and offline replay."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import threading
import time
from typing import Any
import urllib.error
import urllib.request

from experiments.concurrent_five_agent_swarm.client import MAX_CALLS, peak_inflight
from experiments.live_five_agent_swarm.client import (
    Events,
     MAX_OUTPUT,
    RunStopped,
    charge,
    load_openrouter_credentials,
    open_private,
    reservation,
    response_message,
)
from lggr.streaming import StreamingCodebaseInterfaceMergeMonitor
from .domain import CODE_SWARM_MODELS, WORKER_MODULES, CodeWorkspace, fixture

CODE_SWARM_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "inspect_workspace",
            "description": (
                "Inspect your owned Python module source code, its local unit test verdict, "
                "peer module function signatures, and any specification constraints."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_local_tests",
            "description": "Execute your module's isolated local unit test suite.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_module_patch",
            "description": (
                "Submit a complete Python implementation for your owned module. "
                "Must pass AST sandbox validation and your module's local unit tests."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Complete Python source code for your owned module.",
                    }
                },
                "required": ["source_code"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate",
            "description": (
                "Report why cross-module integration cannot be resolved within your owned "
                "module's permissions (e.g., locked upstream specification contradiction)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                },
                "required": ["reason"],
                "additionalProperties": False,
            },
        },
    },
]


def code_request(model: str, messages: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model": model,
        "messages": deepcopy(messages),
        "tools": CODE_SWARM_TOOLS,
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": MAX_OUTPUT,
        "provider": {"max_price": {"prompt": 1, "completion": 5}, "allow_fallbacks": False},
    }


class CodeBatchClient:
    """Concurrent wave client for code-engineering agents with pre-reserved budgets."""

    def __init__(self, events: Events, budget: str | Decimal, source: list[dict[str, Any]] | None = None, transport: Any = None) -> None:
        self.events = events
        self.limit = Decimal(str(budget))
        self.source = source
        if not self.limit.is_finite() or not 0 < self.limit <= 10:
            raise ValueError("invalid budget")
        self.spent = Decimal(0)
        self.calls = 0
        self.wave = 0
        self.max_inflight = 0
        self.concurrent_waves = 0
        self.lock = threading.Lock()
        self.transport = transport or self.send
        self.key: str | None = None
        if source is None and transport is None:
            self.key, _ = load_openrouter_credentials()
            if not self.key:
                raise RunStopped("OpenRouter credentials unavailable")

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        started = time.monotonic_ns()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": "Bearer " + str(self.key),
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with open_private(req, timeout=60) as stream:
                body = stream.read().decode("utf-8")
            try:
                result: dict[str, Any] = {"response": json.loads(body)}
            except ValueError:
                result = {"error": "invalid_json", "response_text": body}
        except Exception as error:
            result = {"error": type(error).__name__, "http_status": getattr(error, "code", None)}
            if isinstance(error, urllib.error.HTTPError):
                error.close()
        return {**result, "started_ns": started, "finished_ns": time.monotonic_ns()}

    def batch(self, calls: list[tuple[str, list[dict[str, Any]]]]) -> list[Any]:
        with self.lock:
            if not 1 <= len(calls) <= 3:
                raise ValueError("one to three requests per wave required")
            payloads = [code_request(model, messages) for model, messages in calls]
            reserves = [reservation(p) for p in payloads]
            if self.calls + len(calls) > MAX_CALLS or self.spent + sum(reserves) > self.limit:
                raise RunStopped("API attempt or spending ceiling reached")
            self.wave += 1
            identifiers = list(range(self.calls, self.calls + len(calls)))
            self.calls += len(calls)
            self.spent += sum(reserves)
            for ident, payload, reserved in zip(identifiers, payloads, reserves):
                self.events.emit(
                    "api_request",
                    {
                        "request_id": ident,
                        "wave": self.wave,
                        "request": payload,
                        "reserved_usd": str(reserved),
                    },
                )
            if self.source is None:
                with ThreadPoolExecutor(max_workers=len(calls)) as pool:
                    observed = list(pool.map(self.transport, payloads))
            else:
                pos = len(self.events.records)
                observed = [self.source[pos + i]["data"]["observation"] for i in range(len(calls))]
            peak = peak_inflight(observed)
            self.max_inflight = max(self.max_inflight, peak)
            self.concurrent_waves += int(peak > 1)
            messages: list[Any] = []
            stopped = False
            for ident, payload, reserved, obs in zip(identifiers, payloads, reserves, observed):
                if "response" in obs:
                    raw = obs["response"]
                    charged, reported = charge(raw, reserved)
                    self.spent += charged - reserved
                    self.events.emit(
                        "api_response",
                        {
                            "request_id": ident,
                            "wave": self.wave,
                            "response": raw,
                            "observation": obs,
                            "charged_usd": str(charged),
                            "cost_reported": reported,
                        },
                    )
                    stopped |= charged > reserved
                    try:
                        messages.append(response_message(raw, payload["model"]))
                    except ValueError as error:
                        messages.append(error)
                else:
                    self.events.emit(
                        "api_error",
                        {
                            "request_id": ident,
                            "wave": self.wave,
                            "observation": obs,
                            "charged_upper_bound_usd": str(reserved),
                        },
                    )
                    stopped = True
            self.events.emit(
                "wave_result",
                {
                    "wave": self.wave,
                    "requests": len(calls),
                    "peak_inflight": peak,
                    "charged_or_reserved_usd": str(self.spent),
                },
            )
            if stopped:
                raise RunStopped("provider failure or over-reservation charge; all in-flight requests settled")
            return messages


def system_prompt(worker: str) -> str:
    module_name = WORKER_MODULES[worker]
    return (
        f"You are software engineering agent {worker}, owner of Python module `{module_name}.py` "
        "in a 3-module financial settlement pipeline (`pricing` -> `tax_engine` -> `settlement_router`). "
        "Always call `inspect_workspace` first. "
        "ONLY call `escalate` if `infeasible_constraint` in `inspect_workspace` is non-null. "
        "Otherwise, NEVER call `escalate`: always call `submit_module_patch` with the complete Python "
        "source code for your module (if your module needs no change or your role directive says "
        "`HOLD_CANONICAL_INTERFACE`, submit your existing `source_code` unchanged via `submit_module_patch`)."
    )


def merge_gate(events: Events, workspace: CodeWorkspace, arm: str, step_tag: str) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingCodebaseInterfaceMergeMonitor(
        scope_id=f"code-swarm-gate-{arm}-{step_tag}"
    )
    eval_rec = monitor.evaluate_codebase_merge(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    # Full cryptographic receipt is logged in the host gate event, NOT dumped raw into agent prompts
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "contract_mismatches": eval_rec["contract_mismatches"],
            "conservation_defects": eval_rec["conservation_defects"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def agent_session(
    events: Events,
    workspace: CodeWorkspace,
    history: list[dict[str, Any]],
    worker: str,
    feedback: dict[str, Any],
):
    idx = int(worker.rsplit("-", 1)[1])
    model = CODE_SWARM_MODELS[idx]
    history.append(
        {
            "role": "user",
            "content": json.dumps(
                {
                    "instruction": "Call inspect_workspace first, then submit_module_patch or escalate.",
                    "feedback": feedback,
                },
                sort_keys=True,
            ),
        }
    )
    events.emit("agent_turn", {"worker": worker, "model": model, "feedback": feedback})
    inspected = False
    for _ in range(3):
        try:
            message = yield (model, history)
        except ValueError as error:
            events.emit("invalid_model_output", {"worker": worker, "reason": str(error)})
            return False
        history.append(message)
        calls = message.get("tool_calls", [])
        if not isinstance(calls, list) or len(calls) > 6:
            events.emit("invalid_model_output", {"worker": worker, "reason": "invalid tool call list"})
            return False
        if not calls:
            history.append(
                {
                    "role": "user",
                    "content": "Call inspect_workspace and then submit_module_patch or escalate.",
                }
            )
            continue
        done = False
        escalated = False
        for call in calls:
            fn = call.get("function", {}) if isinstance(call, dict) else {}
            name = fn.get("name")
            try:
                args = json.loads(fn.get("arguments", "{}"))
                if not isinstance(args, dict):
                    raise ValueError("arguments must be an object")
                if name != "inspect_workspace" and not inspected:
                    result = {"accepted": False, "error": "call inspect_workspace before acting"}
                else:
                    result = workspace.tool(worker, str(name), args)
                    inspected |= name == "inspect_workspace" and "owned_module" in result
            except Exception:
                result = {"accepted": False, "error": "malformed tool arguments"}
            events.emit("tool", {"worker": worker, "call": call, "result": result})
            history.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", "missing"),
                    "content": json.dumps(result, sort_keys=True),
                }
            )
            done |= result.get("accepted") is True or result.get("escalated") is True
            escalated |= result.get("escalated") is True
        if done:
            return escalated
    events.emit("agent_turn_exhausted", {"worker": worker})
    return False


def round_turns(
    client: CodeBatchClient,
    events: Events,
    workspace: CodeWorkspace,
    histories: dict[str, list[dict[str, Any]]],
    workers: list[str],
    per_worker_feedback: dict[str, dict[str, Any]],
) -> int:
    generators = {
        w: agent_session(events, workspace, histories[w], w, per_worker_feedback[w])
        for w in workers
    }
    pending: dict[str, Any] = {}
    escalations = 0
    for w, gen in generators.items():
        pending[w] = next(gen)
    while pending:
        answers = client.batch(list(pending.values()))
        following: dict[str, Any] = {}
        for (w, _), answer in zip(pending.items(), answers):
            try:
                if isinstance(answer, Exception):
                    following[w] = generators[w].throw(answer)
                else:
                    following[w] = generators[w].send(answer)
            except StopIteration as stop:
                escalations += int(bool(stop.value))
        pending = following
    return escalations


def campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = CodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    if arm == "A":
                        per_worker_fb[w] = {
                            "arm": "A_generic_ci_red",
                            "message": "Merged pipeline integration failed. Inspect your workspace and submit a module patch or escalate if infeasible.",
                        }
                    elif arm == "B":
                        # Conventional sequential pipeline traceback: reports only the first uncaught stage exception
                        per_worker_fb[w] = {
                            "arm": "B_sequential_pipeline_traceback",
                            "first_sequential_traceback": eval_rec["integration_trace"].get(
                                "first_sequential_traceback"
                            ),
                            "infeasible_constraint": base_state["infeasible_constraint"],
                        }
                    else:
                        # Arm C: Compact, role-scoped, symmetry-broken LGGR directive (no receipt hash bloat)
                        per_worker_fb[w] = {
                            "arm": "C_compact_lggr_role_directive",
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }
                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, _ = merge_gate(events, ws, arm, f"wave-{wave_idx}")
            if eval_rec["global_green"] == 1 and feasible_case:
                outcome = "completed"
            elif not feasible_case and escalations > 0 and eval_rec["global_green"] == 0:
                outcome = "safe_escalated"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "waves_run": waves_run,
                "escalations": escalations,
                "api_attempts": client.calls - start_calls,
                "cost_usd": str(client.spent - start_cost),
            }
            events.emit("arm_result", arm_res)
            arms_out.append(arm_res)

        case_res = {"seed": seed, "kind": base_state["kind"], "arms": arms_out}
        events.emit("case_result", case_res)
        cases.append(case_res)

    summary = {
        "schema": "lggr.concurrent_code_engineering_swarm.v1",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent Python code-engineering swarm comparing generic CI failure (A), "
            "uncoordinated integration findings (B), and compact role-scoped LGGR directives (C) "
            "with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def replay(path: str | Path) -> dict[str, Any]:
    records = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
    metadata = records[0]["data"]
    if records[0]["kind"] != "start":
        raise ValueError("missing start event")
    config = metadata["config"]
    events = Events(expected=records)
    events.emit("start", metadata)
    client = CodeBatchClient(events, config["budget_usd"], source=records)
    try:
        summary = campaign(client, events, config)
    except RunStopped as error:
        summary = {
            "reason": str(error),
            "api_attempts": client.calls,
            "charged_or_reserved_usd": str(client.spent),
        }
        events.emit("stopped", summary)
    if len(events.records) != len(records):
        raise ValueError("trailing events in replay log")
    saved = Path(path).with_name("summary.json")
    if saved.exists() and json.loads(saved.read_text(encoding="utf-8")) != summary:
        raise ValueError("saved summary differs from derived replay")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "replay"])
    parser.add_argument("path")
    parser.add_argument("--seeds", nargs="+", type=int, default=[6100, 6101, 6102])
    parser.add_argument("--budget", default="0.50")
    args = parser.parse_args()
    target = Path(args.path)
    if args.mode == "replay":
        summary = replay(target)
        print(
            json.dumps(
                {
                    "replayed": True,
                    "api_attempts": summary["api_attempts"],
                    "cases": len(summary.get("cases", [])),
                }
            )
        )
        return
    target.mkdir(parents=True, exist_ok=True)
    events_path = target / "events.jsonl"
    if events_path.exists():
        raise ValueError(f"evidence log {events_path} already exists")
    config = {
        "seeds": args.seeds,
        "models": CODE_SWARM_MODELS,
        "budget_usd": str(args.budget),
    }
    events = Events(events_path)
    events.emit("start", {"config": config})
    client = CodeBatchClient(events, args.budget)
    summary = campaign(client, events, config)
    (target / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "COMPLETED",
                "api_attempts": summary["api_attempts"],
                "charged_or_reserved_usd": summary["charged_or_reserved_usd"],
                "max_inflight_requests": summary["max_inflight_requests"],
            }
        )
    )


if __name__ == "__main__":
    main()
