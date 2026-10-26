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
from lggr.streaming import (
    StreamingCodebaseBoundaryQuorumMonitor,
    StreamingCodebaseCPTPChannelMonitor,
    StreamingCodebaseCatalystEvolutionMonitor,
    StreamingCodebaseCoalitionalMonitor,
    StreamingCodebaseContextualSheafMonitor,
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
from .domain import (
    COALITIONAL_WORKER_MODULES,
    CODE_SWARM_MODELS,
    CPTP_WORKER_MODULES,
    DFA_WORKER_MODULES,
    DIAMOND_SWARM_MODELS,
    DIAMOND_WORKER_MODULES,
    DIAMOND_WORKTREE_BRANCHES,
    JACOBIAN_WORKER_MODULES,
    KINDUCTION_WORKER_MODULES,
    LEASE_WORKER_MODULES,
    MV_WORKER_MODULES,
    QUORUM_WORKER_MODULES,
    REGGE_WORKER_MODULES,
    REPLAY_WORKER_MODULES,
    SHEAF_WORKER_MODULES,
    STOP_WORKER_MODULES,
    WIN_WORKER_MODULES,
    WORKER_MODULES,
    BoundaryQuorumCodeWorkspace,
    CPTPChannelCodeWorkspace,
    CatalystCodeWorkspace,
    CoalitionalCodeWorkspace,
    CodeWorkspace,
    ContextualSheafCodeWorkspace,
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
    sheaf_fixture,
    stop_fixture,
    win_fixture,
)

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
        result: dict[str, Any] = {"error": "uninitialized"}
        for attempt in range(6):
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
                    result = {"response": json.loads(body)}
                except ValueError:
                    result = {"error": "invalid_json", "response_text": body}
                break
            except Exception as error:
                code = getattr(error, "code", None)
                result = {"error": type(error).__name__, "http_status": code}
                if isinstance(error, urllib.error.HTTPError):
                    error.close()
                if code in (429, 502, 503) and attempt < 5:
                    time.sleep(3.0 * (attempt + 1))
                    continue
                break
        return {**result, "started_ns": started, "finished_ns": time.monotonic_ns()}

    def batch(self, calls: list[tuple[str, list[dict[str, Any]]]]) -> list[Any]:
        with self.lock:
            if not 1 <= len(calls) <= 4:
                raise ValueError("one to four requests per wave required")
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
    workspace: CodeWorkspace | DiamondCodeWorkspace,
    history: list[dict[str, Any]],
    worker: str,
    feedback: dict[str, Any],
    models: list[str] = CODE_SWARM_MODELS,
):
    idx = int(worker.rsplit("-", 1)[1])
    model = models[idx]
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
    workspace: CodeWorkspace | DiamondCodeWorkspace,
    histories: dict[str, list[dict[str, Any]]],
    workers: list[str],
    per_worker_feedback: dict[str, dict[str, Any]],
    models: list[str] = CODE_SWARM_MODELS,
) -> int:
    generators = {
        w: agent_session(events, workspace, histories[w], w, per_worker_feedback[w], models=models)
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


def diamond_system_prompt(worker: str) -> str:
    module_name = DIAMOND_WORKER_MODULES[worker]
    branch_name = DIAMOND_WORKTREE_BRANCHES[worker]
    return (
        f"You are software engineering agent {worker}, owner of Python module `{module_name}.py` "
        f"on isolated git worktree branch `{branch_name}` in a 4-module diamond-dependency settlement "
        "codebase (`quote_anchor` A -> `tax_branch` B, `quote_anchor` A -> `fee_branch` C, "
        "and B, C -> `diamond_aggregator` D). "
        "Always call `inspect_workspace` first. "
        "ONLY call `escalate` if `infeasible_constraint` in `inspect_workspace` is non-null. "
        "Otherwise, NEVER call `escalate`: always call `submit_module_patch` with the complete Python "
        "source code for your module (if your module needs no change or your role directive says "
        "`HOLD_CANONICAL_INTERFACE`, submit your existing `source_code` unchanged via `submit_module_patch`)."
    )


def diamond_merge_gate(
    events: Events, workspace: DiamondCodeWorkspace, arm: str, step_tag: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingDiamondCodebasePullbackMonitor(
        scope_id=f"diamond-code-swarm-gate-{arm}-{step_tag}"
    )
    eval_rec = monitor.evaluate_diamond_codebase_merge(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "in_pullback_square": eval_rec["in_pullback_square"],
            "interface_fiber_size": eval_rec["interface_fiber_size"],
            "interface_uniquely_identifies_pair": eval_rec["interface_uniquely_identifies_pair"],
            "universal_cone_mediator": eval_rec["universal_cone_mediator"],
            "contract_mismatches": eval_rec["contract_mismatches"],
            "conservation_defects": eval_rec["conservation_defects"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def diamond_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2", "worker-3"]
    for seed in config["seeds"]:
        base_state = diamond_fixture(seed)
        events.emit(
            "case_start",
            {
                "seed": seed,
                "kind": base_state["kind"],
                "worktree_branches": base_state["worktree_branches"],
                "fixture": base_state,
            },
        )
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = DiamondCodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": diamond_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = diamond_merge_gate(events, ws, arm, "wave-0")
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
                            "worktree_branch": DIAMOND_WORKTREE_BRANCHES[w],
                            "message": (
                                "Diamond worktree merge integration failed across A -> (B, C) -> D. "
                                "Inspect your workspace and submit a module patch or escalate if infeasible."
                            ),
                        }
                    elif arm == "B":
                        per_worker_fb[w] = {
                            "arm": "B_sequential_branch_traceback",
                            "worktree_branch": DIAMOND_WORKTREE_BRANCHES[w],
                            "first_sequential_traceback": eval_rec["integration_trace"].get(
                                "first_sequential_traceback"
                            ),
                            "infeasible_constraint": base_state["infeasible_constraint"],
                        }
                    else:
                        per_worker_fb[w] = {
                            "arm": "C_pullback_mediated_lggr_directive",
                            "worktree_branch": DIAMOND_WORKTREE_BRANCHES[w],
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }
                escalations += round_turns(
                    client, events, ws, histories, workers, per_worker_fb, models=DIAMOND_SWARM_MODELS
                )
                eval_rec, _ = diamond_merge_gate(events, ws, arm, f"wave-{wave_idx}")
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
                "final_in_pullback_square": eval_rec["in_pullback_square"],
                "final_interface_fiber_size": eval_rec["interface_fiber_size"],
                "final_universal_cone_mediator": eval_rec["universal_cone_mediator"],
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
        "schema": "lggr.diamond_code_engineering_swarm.v1",
        "topology": "diamond",
        "authority_effect": "None",
        "worktree_branches": dict(DIAMOND_WORKTREE_BRANCHES),
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 4-agent diamond-dependency Python code-engineering swarm across isolated git worktree "
            "branches (A -> B, A -> C, B, C -> D) comparing generic CI failure (A), sequential branch traceback (B), "
            "and pullback-mediated LGGR directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


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


def catalyst_system_prompt(worker: str) -> str:
    module_name = WORKER_MODULES[worker]
    return (
        f"You are software engineering agent {worker}, owner of Python module `{module_name}.py` "
        "in a 3-module settlement codebase (`pricing` -> `tax_engine` -> `settlement_router`) "
        "evolving across sequential feature tickets (t = 1, 2, 3). "
        "Always call `inspect_workspace` first. "
        "ONLY call `escalate` if `infeasible_constraint` in `inspect_workspace` is non-null. "
        "Otherwise, NEVER call `escalate`: always call `submit_module_patch` with the complete Python "
        "source code for your module (if your feedback or directive says no change or hold, submit your "
        "existing `source_code` unchanged via `submit_module_patch`)."
    )


def catalyst_merge_gate(
    events: Events,
    workspace: CatalystCodeWorkspace,
    arm: str,
    step_tag: str,
    *,
    rejuvenation_scheduled: bool = False,
    seed_max_debt_seen: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingCodebaseCatalystEvolutionMonitor(
        per_ticket_local_tolerance=workspace.state.get("per_ticket_local_tolerance", 2),
        global_catalyst_ceiling=workspace.state.get("global_catalyst_ceiling", 4),
        scope_id=f"catalyst-code-swarm-gate-{arm}-{step_tag}",
    )
    if seed_max_debt_seen is not None:
        monitor.max_catalyst_debt_seen = int(seed_max_debt_seen)
    eval_rec = monitor.evaluate_ticket_step(
        f"eval-{arm}-{step_tag}",
        ticket_id=workspace.state.get("ticket_id", "ticket_3_conservation_and_rejuvenation"),
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        previous_catalyst_debt=workspace.state.get("previous_catalyst_debt", 0),
        rejuvenation_scheduled=rejuvenation_scheduled,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "ticket_id": eval_rec["ticket_id"],
            "previous_catalyst_debt": eval_rec["previous_catalyst_debt"],
            "catalyst_wear_delta": eval_rec["catalyst_wear_delta"],
            "total_catalyst_debt": eval_rec["total_catalyst_debt"],
            "max_catalyst_debt_seen": eval_rec["max_catalyst_debt_seen"],
            "rejuvenation_scheduled": eval_rec["rejuvenation_scheduled"],
            "functional_e2e_ok": eval_rec["functional_e2e_ok"],
            "step_wear_within_budget": eval_rec["step_wear_within_budget"],
            "within_global_catalyst_ceiling": eval_rec["within_global_catalyst_ceiling"],
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "module_debt_breakdown": eval_rec["module_debt_breakdown"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def catalyst_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = catalyst_fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = CatalystCodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": catalyst_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = catalyst_merge_gate(events, ws, arm, "wave-0", rejuvenation_scheduled=False)
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    if arm == "A":
                        # Arm A: Functional-only / single-ticket complexity-delta gate (blind to cumulative catalyst ceiling)
                        per_worker_fb[w] = {
                            "arm": "A_functional_and_step_delta_gate",
                            "ticket_id": base_state["ticket_id"],
                            "functional_unit_and_e2e_tests_passed": eval_rec["functional_e2e_ok"],
                            "step_complexity_delta_within_ticket_budget": eval_rec["step_wear_within_budget"],
                            "infeasible_constraint": base_state["infeasible_constraint"],
                            "message": (
                                "Ticket 3 functional unit and E2E settlement tests passed, and single-ticket "
                                "complexity delta delta_C = 2 <= 2 is within the per-ticket step budget. "
                                "If `infeasible_constraint` is non-null, call `escalate`; otherwise preserve "
                                "your current working module implementation by submitting your existing "
                                "`source_code` unchanged via `submit_module_patch`."
                            ),
                        }
                    elif arm == "B":
                        # Arm B: Late post-breach partial cleanup (only the latest ticket's module worker-2 is asked to clean up)
                        if w == "worker-2":
                            per_worker_fb[w] = {
                                "arm": "B_late_last_ticket_module_cleanup",
                                "ticket_id": base_state["ticket_id"],
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Post-Ticket-3 lint check: if `infeasible_constraint` is non-null, call `escalate`; "
                                    "otherwise remove `_compat_fee_fallback` and `'shim_payout_cents'` from "
                                    "`settlement_router.py` while keeping canonical return keys."
                                ),
                            }
                        else:
                            per_worker_fb[w] = {
                                "arm": "B_late_last_ticket_module_cleanup",
                                "ticket_id": base_state["ticket_id"],
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Tickets 1 and 2 already merged and passed E2E tests. If `infeasible_constraint` "
                                    "is non-null, call `escalate`; otherwise do NOT modify your earlier-ticket module "
                                    "and submit your existing `source_code` unchanged via `submit_module_patch`."
                                ),
                            }
                    else:
                        # Arm C: Scheduled LGGR Catalyst Rejuvenation Gate (coordinated 3-module shim & dead-helper purge)
                        per_worker_fb[w] = {
                            "arm": "C_scheduled_lggr_catalyst_rejuvenation_directive",
                            "ticket_id": base_state["ticket_id"],
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }
                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                # Arm B records the late cleanup after the prefix peak C_3 = 6 already occurred;
                # Arm C executes the scheduled rejuvenation pass from C_2 = 4 -> C_3 = 0.
                seed_peak = 6 if arm == "B" else 4
                eval_rec, _ = catalyst_merge_gate(
                    events,
                    ws,
                    arm,
                    f"wave-{wave_idx}",
                    rejuvenation_scheduled=True,
                    seed_max_debt_seen=seed_peak,
                )
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
                "final_total_catalyst_debt": eval_rec["total_catalyst_debt"],
                "final_max_catalyst_debt_seen": eval_rec["max_catalyst_debt_seen"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.catalyst_code_engineering_swarm.v1",
        "topology": "catalyst",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent iterative feature-evolution Python code-engineering swarm across sequential "
            "feature tickets (t = 1, 2, 3) comparing functional/step-delta gating (A), late single-module "
            "cleanup after ceiling breach (B), and scheduled LGGR catalyst rejuvenation directives (C) "
            "with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def dfa_system_prompt(worker: str) -> str:
    module_name = DFA_WORKER_MODULES[worker]
    return (
        f"You are software engineering agent {worker}, owner of stateful transaction Python module `{module_name}.py` "
        "in a 3-stage settlement pipeline (`pricing_tx` -> `tax_tx` -> `settlement_tx`) sharing a "
        "`TransactionSession` state machine (`q0_idle`, `q1_lock`, `q2_done`, `q3_err`). "
        "Always call `inspect_workspace` first. "
        "ONLY call `escalate` if `infeasible_constraint` in `inspect_workspace` is non-null. "
        "Otherwise, NEVER call `escalate`: always call `submit_module_patch` with the complete Python "
        "source code for your module (if your feedback or directive says no change or hold, submit your "
        "existing `source_code` unchanged via `submit_module_patch`)."
    )


def dfa_merge_gate(
    events: Events,
    workspace: StatefulDFACodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingStatefulCodebaseDFAMonitor(
        scope_id=f"dfa-code-swarm-gate-{arm}-{step_tag}"
    )
    eval_rec = monitor.evaluate_stateful_codebase_dfa(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "segment_tokens": eval_rec["segment_tokens"],
            "non_reset_accepting_modules": eval_rec["non_reset_accepting_modules"],
            "non_reset_module_count": eval_rec["non_reset_module_count"],
            "terminal_session_state": eval_rec["terminal_session_state"],
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def dfa_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = dfa_fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = StatefulDFACodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": dfa_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = dfa_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    if arm == "A":
                        # Arm A: Fresh-fixture local unit-test acceptance gate (accepts q2_done in F)
                        per_worker_fb[w] = {
                            "arm": "A_isolated_fixture_acceptance_gate",
                            "local_unit_test_passed": True,
                            "local_end_state_in_accepting_set_F": True,
                            "infeasible_constraint": base_state["infeasible_constraint"],
                            "message": (
                                "Your module's isolated unit test passed and reached accepting state 'q2_done' "
                                "in F = {'q0_idle', 'q2_done'}. If `infeasible_constraint` is non-null, call "
                                "`escalate`; otherwise preserve your current working implementation by submitting "
                                "your existing `source_code` unchanged via `submit_module_patch`."
                            ),
                        }
                    elif arm == "B":
                        # Arm B: Exception-site traceback routing (blames downstream stages where trap occurs)
                        if w == "worker-0":
                            per_worker_fb[w] = {
                                "arm": "B_exception_site_traceback_routing",
                                "first_sequential_traceback": eval_rec["integration_trace"].get(
                                    "first_sequential_traceback"
                                ),
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Stage 1 (`pricing_tx.execute_pricing_tx`) completed and committed without "
                                    "raising any exception; the runtime trap occurred downstream in `tax_tx`. "
                                    "If `infeasible_constraint` is non-null, call `escalate`; otherwise do NOT "
                                    "modify `pricing_tx.py` and submit your existing `source_code` unchanged via "
                                    "`submit_module_patch`."
                                ),
                            }
                        else:
                            per_worker_fb[w] = {
                                "arm": "B_exception_site_traceback_routing",
                                "first_sequential_traceback": eval_rec["integration_trace"].get(
                                    "first_sequential_traceback"
                                ),
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Downstream transaction stage raised `TransactionProtocolTrapError`. "
                                    "If `infeasible_constraint` is non-null, call `escalate`; otherwise append "
                                    "`session.release()` after `session.commit()` in your module and submit via "
                                    "`submit_module_patch`."
                                ),
                            }
                    else:
                        # Arm C: Explicit LGGR DFA Reset-Token Gluing Directive across all non-reset modules
                        per_worker_fb[w] = {
                            "arm": "C_explicit_lggr_dfa_reset_gluing_directive",
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }
                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, _ = dfa_merge_gate(events, ws, arm, f"wave-{wave_idx}")
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
                "final_non_reset_module_count": eval_rec["non_reset_module_count"],
                "final_terminal_session_state": eval_rec["terminal_session_state"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.stateful_dfa_code_engineering_swarm.v1",
        "topology": "dfa",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent stateful transaction Python code-engineering swarm (`pricing_tx` -> `tax_tx` -> "
            "`settlement_tx`) comparing fresh-fixture acceptance gating (A), exception-site traceback routing (B), "
            "and explicit LGGR DFA reset-token gluing directives (C) with full cryptographic receipts retained "
            "in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def replay_system_prompt(worker: str) -> str:
    module_name = REPLAY_WORKER_MODULES[worker]
    return (
        f"You are software engineering agent {worker}, owner of asynchronous event-driven Python module `{module_name}.py` "
        "in a 3-stage escrow settlement pipeline (`pricing_events` -> `tax_events` -> `settlement_events`) sharing an "
        "`AsyncEscrowBus(prefix_budget=900)`. "
        "Always call `inspect_workspace` first. "
        "ONLY call `escalate` if `infeasible_constraint` in `inspect_workspace` is non-null. "
        "Otherwise, NEVER call `escalate`: always call `submit_module_patch` with the complete Python "
        "source code for your module (if your feedback or directive says no change or hold, submit your "
        "existing `source_code` unchanged via `submit_module_patch`)."
    )


def replay_merge_gate(
    events: Events,
    workspace: ReplayOrderCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingCodebaseReplayOrderMonitor(
        prefix_budget=900,
        scope_id=f"replay-code-swarm-gate-{arm}-{step_tag}",
    )
    eval_rec = monitor.evaluate_codebase_replay_order(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "stage_events": eval_rec["stage_events"],
            "stage_barriers": eval_rec["stage_barriers"],
            "missing_barrier_modules": eval_rec["missing_barrier_modules"],
            "missing_barrier_count": eval_rec["missing_barrier_count"],
            "arrival_max_prefix_cents": eval_rec["arrival_max_prefix_cents"],
            "causal_max_prefix_cents": eval_rec["causal_max_prefix_cents"],
            "worst_permutation_max_prefix_cents": eval_rec["worst_permutation_max_prefix_cents"],
            "common_endpoint_sum_cents": eval_rec["common_endpoint_sum_cents"],
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def replay_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = replay_fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = ReplayOrderCodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": replay_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = replay_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    if arm == "A":
                        # Arm A: Endpoint sum + arrival-order prefix gate (blind to arrival-masked causal breach)
                        per_worker_fb[w] = {
                            "arm": "A_endpoint_and_arrival_prefix_gate",
                            "local_unit_test_passed": True,
                            "arrival_max_prefix_cents": eval_rec["arrival_max_prefix_cents"],
                            "common_endpoint_sum_cents": eval_rec["common_endpoint_sum_cents"],
                            "infeasible_constraint": base_state["infeasible_constraint"],
                            "message": (
                                "Your module's isolated unit test passed, terminal escrow sum is 180 cents, and "
                                f"arrival-order max prefix is {eval_rec['arrival_max_prefix_cents']} <= 900 cents. "
                                "If `infeasible_constraint` is non-null, call `escalate`; otherwise preserve your "
                                "current working implementation by submitting your existing `source_code` unchanged "
                                "via `submit_module_patch`."
                            ),
                        }
                    elif arm == "B":
                        # Arm B: Causal index interleaving without positive-mass netting or stage barriers
                        if w == "worker-0":
                            per_worker_fb[w] = {
                                "arm": "B_causal_interleaving_without_positive_mass_netting",
                                "causal_max_prefix_cents": eval_rec["causal_max_prefix_cents"],
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Stage 1 (`pricing_events`) reserves 900 cents within the 900-cent budget. "
                                    "If `infeasible_constraint` is non-null, call `escalate`; otherwise keep "
                                    "`pricing_events.py` unchanged and submit your existing `source_code` via "
                                    "`submit_module_patch`."
                                ),
                            }
                        elif w == "worker-1":
                            per_worker_fb[w] = {
                                "arm": "B_causal_interleaving_without_positive_mass_netting",
                                "causal_max_prefix_cents": eval_rec["causal_max_prefix_cents"],
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Causal prefix reached 1080 > 900 when `tax_escrow` ran at `causal_index=2` "
                                    "before `settlement_release`. If `infeasible_constraint` is non-null, call "
                                    "`escalate`; otherwise change `causal_index=2` to `causal_index=3` in "
                                    "`bus.publish('tax_escrow', tax, causal_index=3)` (do NOT add `commit_barrier`) "
                                    "and submit via `submit_module_patch`."
                                ),
                            }
                        else:
                            per_worker_fb[w] = {
                                "arm": "B_causal_interleaving_without_positive_mass_netting",
                                "causal_max_prefix_cents": eval_rec["causal_max_prefix_cents"],
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "Causal prefix reached 1080 > 900 when `settlement_release` ran at `causal_index=3`. "
                                    "If `infeasible_constraint` is non-null, call `escalate`; otherwise update "
                                    "`settlement_events.py` to call `bus.publish('settlement_release', -(payout + fee), "
                                    "causal_index=2, priority_arrival=False)` (do NOT add `commit_barrier`) so release "
                                    "is interleaved at `causal_index=2`, and submit via `submit_module_patch`."
                                ),
                            }
                    else:
                        # Arm C: Explicit LGGR Replay-Order Barrier & Pre-Netted Escrow Directive
                        per_worker_fb[w] = {
                            "arm": "C_explicit_lggr_replay_order_barrier_directive",
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }
                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, _ = replay_merge_gate(events, ws, arm, f"wave-{wave_idx}")
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
                "final_arrival_max_prefix_cents": eval_rec["arrival_max_prefix_cents"],
                "final_causal_max_prefix_cents": eval_rec["causal_max_prefix_cents"],
                "final_worst_permutation_max_prefix_cents": eval_rec["worst_permutation_max_prefix_cents"],
                "final_missing_barrier_count": eval_rec["missing_barrier_count"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.replay_order_code_engineering_swarm.v1",
        "topology": "replay",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent asynchronous event-driven Python code-engineering swarm (`pricing_events` -> "
            "`tax_events` -> `settlement_events`) comparing arrival-order/endpoint gating (A), causal index "
            "interleaving without positive-mass netting (B), and explicit LGGR causal-barrier & pre-netted "
            "escrow directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def coalitional_system_prompt(worker: str) -> str:
    module_name = COALITIONAL_WORKER_MODULES[worker]
    return (
        f"You are software engineering agent {worker}, owner of Python module `{module_name}.py` "
        "in a 3-stage settlement codebase (`pricing_coalition` -> `tax_coalition` -> `settlement_coalition`). "
        "Always call `inspect_workspace` first. "
        "ONLY call `escalate` if `infeasible_constraint` in `inspect_workspace` is non-null. "
        "Otherwise, NEVER call `escalate`: always call `submit_module_patch` with the complete Python "
        "source code for your module (if your feedback or directive says no change or hold, submit your "
        "existing `source_code` unchanged via `submit_module_patch`)."
    )


def coalitional_merge_gate(
    events: Events,
    workspace: CoalitionalCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingCodebaseCoalitionalMonitor(
        scope_id=f"coalitional-code-swarm-gate-{arm}-{step_tag}",
    )
    eval_rec = monitor.evaluate_codebase_coalitions(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "characteristic_values": eval_rec["characteristic_values"],
            "grand_coalition_value": eval_rec["grand_coalition_value"],
            "leave_one_out_marginals": eval_rec["leave_one_out_marginals"],
            "shapley_attributions": eval_rec["shapley_attributions"],
            "two_times_shapley_attributions": eval_rec["two_times_shapley_attributions"],
            "dummy_players": eval_rec["dummy_players"],
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def coalitional_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = coalitional_fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = CoalitionalCodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": coalitional_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = coalitional_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    mname = COALITIONAL_WORKER_MODULES[w]
                    if arm == "A":
                        # Arm A: Single-module leave-one-out ablation bisection (blind when Delta_{-i} = 0)
                        per_worker_fb[w] = {
                            "arm": "A_leave_one_out_ablation_bisection",
                            "local_unit_test_passed": True,
                            "leave_one_out_marginal": eval_rec["leave_one_out_marginals"][mname],
                            "infeasible_constraint": base_state["infeasible_constraint"],
                            "message": (
                                f"Single-module leave-one-out ablation on `{mname}.py` measured marginal "
                                f"Delta_{{-{mname}}} = {eval_rec['leave_one_out_marginals'][mname]} (reverting your "
                                "module alone did not change the E2E verdict). If `infeasible_constraint` is non-null, "
                                "call `escalate`; otherwise preserve your current implementation by submitting your "
                                "existing `source_code` unchanged via `submit_module_patch`."
                            ),
                        }
                    elif arm == "B":
                        # Arm B: Downstream assertion-site blame (repairs only settlement_coalition where fee check fails)
                        if w in ("worker-0", "worker-1"):
                            per_worker_fb[w] = {
                                "arm": "B_downstream_assertion_site_blame",
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    f"Upstream module `{mname}.py` returned without raising an assertion failure; "
                                    "the E2E fee drift assertion failed in Stage 3 (`settlement_coalition.py`). "
                                    "If `infeasible_constraint` is non-null, call `escalate`; otherwise keep your "
                                    "existing `source_code` unchanged and submit via `submit_module_patch`."
                                ),
                            }
                        else:
                            per_worker_fb[w] = {
                                "arm": "B_downstream_assertion_site_blame",
                                "infeasible_constraint": base_state["infeasible_constraint"],
                                "message": (
                                    "E2E assertion failed in `settlement_coalition.py` (`platform_fee_cents = 30 != 27`). "
                                    "If `infeasible_constraint` is non-null, call `escalate`; otherwise remove the "
                                    "`max(..., 1000)` shim so `basis = int(taxed_quote.get('fee_basis_cents', net))` "
                                    "and submit via `submit_module_patch`."
                                ),
                            }
                    else:
                        # Arm C: Explicit LGGR 2^3 Coalitional Shapley Attribution Directive
                        per_worker_fb[w] = {
                            "arm": "C_explicit_lggr_coalitional_shapley_directive",
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }
                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, _ = coalitional_merge_gate(events, ws, arm, f"wave-{wave_idx}")
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
                "final_leave_one_out_marginals": eval_rec["leave_one_out_marginals"],
                "final_two_times_shapley": eval_rec["two_times_shapley_attributions"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.coalitional_code_engineering_swarm.v1",
        "topology": "coalitional",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent coalitional Python code-engineering swarm (`pricing_coalition` -> "
            "`tax_coalition` -> `settlement_coalition`) comparing single-module leave-one-out ablation "
            "bisection (A), downstream assertion-site blame (B), and explicit LGGR 2^3 coalitional Shapley "
            "attribution directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def mv_system_prompt(worker: str) -> str:
    module_name = MV_WORKER_MODULES[worker]
    return (
        f"You are concurrent code-engineering agent {worker}, sole owner of `{module_name}.py` "
        "in a 3-module multi-currency settlement codebase (`pricing_mv.py` -> `tax_mv.py` -> `settlement_mv.py`) "
        "partitioned into two subswarm covers `U` and `V` over disconnected overlap `U cap V = {w0, w1}`.\n"
        "Workflow:\n"
        "1. Call `inspect_workspace` first to inspect your module's Python source code, isolated "
        "unit test result, and `infeasible_constraint`.\n"
        "2. If `infeasible_constraint` is non-null, call `escalate` with a concise explanation of the "
        "Mayer-Vietoris clearing lock contradiction.\n"
        "3. Otherwise, follow the merge-gate feedback in the user prompt. If instructed to keep your "
        "module unchanged, submit your current `source_code` via `submit_module_patch`. If instructed "
        "to reconcile your module's clearing delta/offset on `w1`, submit the complete updated Python "
        "source for your owned module via `submit_module_patch`."
    )


def mv_merge_gate(
    events: Events,
    workspace: MayerVietorisCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingCodebaseMayerVietorisMonitor(
        scope_id=f"mv-code-swarm-gate-{arm}-{step_tag}",
    )
    eval_rec = monitor.evaluate_codebase_mayer_vietoris(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "u_locally_exact": eval_rec["u_locally_exact"],
            "v_locally_exact": eval_rec["v_locally_exact"],
            "union_globally_exact": eval_rec["union_globally_exact"],
            "fu_w1_cents": eval_rec["fu_w1_cents"],
            "fv_w1_cents": eval_rec["fv_w1_cents"],
            "coboundary_spread_cents": eval_rec["coboundary_spread_cents"],
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def mv_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = mv_fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = MayerVietorisCodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": mv_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = mv_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    mname = MV_WORKER_MODULES[w]
                    if arm == "A":
                        per_worker_fb[w] = {
                            "arm": "A_isolated_subswarm_exactness_gate",
                            "local_unit_test_passed": True,
                            "u_locally_exact": eval_rec["u_locally_exact"],
                            "v_locally_exact": eval_rec["v_locally_exact"],
                            "global_integration_passed": False,
                            "instruction": (
                                f"Your module `{mname}.py` passed its isolated unit test and its subswarm is "
                                "locally tree-exact (`u_locally_exact = True`, `v_locally_exact = True`). "
                                "If `infeasible_constraint` is non-null, call `escalate`. Otherwise, because "
                                "your subswarm is locally exact, keep your existing `source_code` unchanged "
                                "and submit via `submit_module_patch`."
                            ),
                        }
                    elif arm == "B":
                        if w == "worker-2":
                            per_worker_fb[w] = {
                                "arm": "B_one_sided_subswarm_v_adjustment",
                                "local_unit_test_passed": True,
                                "fv_w1_cents": eval_rec["fv_w1_cents"],
                                "instruction": (
                                    "If `infeasible_constraint` is non-null, call `escalate`. Otherwise, "
                                    "update `compute_settlement_mv` in `settlement_mv.py` so `'clearing_offset_cents': tax` "
                                    "(`180`), setting `f_V(w1) = 900 + 180 = 1080` while preserving return keys "
                                    "`['gross_cents', 'platform_fee_cents', 'tax_reserve_cents', 'merchant_payout_cents', 'clearing_offset_cents']`."
                                ),
                            }
                        else:
                            per_worker_fb[w] = {
                                "arm": "B_one_sided_subswarm_v_adjustment",
                                "local_unit_test_passed": True,
                                "instruction": (
                                    "If `infeasible_constraint` is non-null, call `escalate`. Otherwise, "
                                    "downstream subswarm `V` (`settlement_mv.py`) is adjusting its clearing offset; "
                                    f"keep your `{mname}.py` `source_code` unchanged and submit via `submit_module_patch`."
                                ),
                            }
                    else:
                        per_worker_fb[w] = {
                            "arm": "C_explicit_lggr_mayer_vietoris_coboundary_directive",
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }

                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, _ = mv_merge_gate(events, ws, arm, f"wave-{wave_idx}")

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
                "final_fu_w1_cents": eval_rec["fu_w1_cents"],
                "final_fv_w1_cents": eval_rec["fv_w1_cents"],
                "final_coboundary_spread_cents": eval_rec["coboundary_spread_cents"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.mayer_vietoris_code_engineering_swarm.v1",
        "topology": "mayer_vietoris",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent Mayer-Vietoris Python code-engineering swarm (`pricing_mv` -> `tax_mv` -> "
            "`settlement_mv`) comparing isolated subswarm exactness gating (A), one-sided subswarm V adjustment (B), "
            "and explicit LGGR Mayer-Vietoris connecting-coboundary reconciliation directives (C) with full "
            "cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def win_system_prompt(worker: str) -> str:
    module_name = WIN_WORKER_MODULES[worker]
    return (
        f"You are concurrent code-engineering agent {worker}, sole owner of `{module_name}.py` "
        "in a 3-module multi-epoch settlement codebase (`pricing_win.py` -> `tax_win.py` -> `settlement_win.py`) "
        "under sliding window `W = 2`, window budget `B_W = 2`, and 6-epoch global horizon budget `B_global = 3`.\n"
        "Workflow:\n"
        "1. Call `inspect_workspace` first to inspect your module's Python source code, isolated "
        "sliding-window unit test result, and `infeasible_constraint`.\n"
        "2. If `infeasible_constraint` is non-null, call `escalate` with a concise explanation of the "
        "windowed-drift lock contradiction.\n"
        "3. Otherwise, follow the merge-gate feedback in the user prompt. If instructed to keep your "
        "module unchanged, submit your current `source_code` via `submit_module_patch`. If instructed "
        "to update `'epoch_drifts_cents'`, submit the complete updated Python source for your owned "
        "module via `submit_module_patch`."
    )


def win_merge_gate(
    events: Events,
    workspace: WindowedDriftCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    monitor = StreamingCodebaseWindowedDriftMonitor(
        window_size=2,
        window_budget=2,
        global_budget=3,
        scope_id=f"win-code-swarm-gate-{arm}-{step_tag}",
    )
    eval_rec = monitor.evaluate_codebase_windowed_drift(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=workspace.local_verdicts(),
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    full_receipt = monitor.current_receipt()
    events.emit(
        "gate",
        {
            "arm": arm,
            "step_tag": step_tag,
            "max_window_sum_cents": eval_rec["max_window_sum_cents"],
            "max_prefix_drift_cents": eval_rec["max_prefix_drift_cents"],
            "terminal_drift_cents": eval_rec["terminal_drift_cents"],
            "unrebalanced_module_count": eval_rec["unrebalanced_module_count"],
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "status": eval_rec["status"],
            "host_lggr_receipt_sha256": full_receipt["receipt_sha256"],
            "host_lggr_receipt": full_receipt,
        },
    )
    return eval_rec, full_receipt


def win_campaign(client: CodeBatchClient, events: Events, config: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = ["worker-0", "worker-1", "worker-2"]
    for seed in config["seeds"]:
        base_state = win_fixture(seed)
        events.emit("case_start", {"seed": seed, "kind": base_state["kind"], "fixture": base_state})
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = WindowedDriftCodeWorkspace(base_state)
            histories = {w: [{"role": "system", "content": win_system_prompt(w)}] for w in workers}
            events.emit("arm_start", {"seed": seed, "arm": arm, "kind": base_state["kind"]})
            start_calls = client.calls
            start_cost = client.spent
            escalations = 0
            waves_run = 0
            eval_rec, _ = win_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0
            feasible_case = base_state["infeasible_constraint"] is None

            for wave_idx in range(1, 3):
                if eval_rec["global_green"] == 1 or (not feasible_case and escalations > 0):
                    break
                waves_run += 1
                per_worker_fb: dict[str, dict[str, Any]] = {}
                for w in workers:
                    mname = WIN_WORKER_MODULES[w]
                    if arm == "A":
                        per_worker_fb[w] = {
                            "arm": "A_sliding_window_local_gate",
                            "local_unit_test_passed": True,
                            "max_window_sum_cents": eval_rec["max_window_sum_cents"],
                            "window_budget_cents": eval_rec["window_budget_cents"],
                            "instruction": (
                                f"Your module `{mname}.py` passed its isolated unit test and satisfies the "
                                "length-2 sliding-window budget (`max_window_sum_cents = 2 <= 2`). "
                                "If `infeasible_constraint` is non-null, call `escalate`. Otherwise, keep your "
                                "existing `source_code` unchanged and submit via `submit_module_patch`."
                            ),
                        }
                    elif arm == "B":
                        if w == "worker-2":
                            per_worker_fb[w] = {
                                "arm": "B_late_terminal_module_sweep",
                                "local_unit_test_passed": True,
                                "instruction": (
                                    "If `infeasible_constraint` is non-null, call `escalate`. Otherwise, "
                                    "update `compute_settlement_win` in `settlement_win.py` so `'epoch_drifts_cents': [-1, -1]` "
                                    "to bring terminal 6-epoch drift down to `2 <= 3`, while preserving return keys "
                                    "`['gross_cents', 'platform_fee_cents', 'tax_reserve_cents', 'merchant_payout_cents', 'epoch_drifts_cents']`."
                                ),
                            }
                        else:
                            per_worker_fb[w] = {
                                "arm": "B_late_terminal_module_sweep",
                                "local_unit_test_passed": True,
                                "instruction": (
                                    "If `infeasible_constraint` is non-null, call `escalate`. Otherwise, "
                                    "downstream `settlement_win.py` is performing a terminal drift sweep; keep your "
                                    f"`{mname}.py` `source_code` unchanged and submit via `submit_module_patch`."
                                ),
                            }
                    else:
                        per_worker_fb[w] = {
                            "arm": "C_explicit_lggr_windowed_drift_rebalancing_directive",
                            "role_directive": eval_rec["compact_role_directives"][w],
                        }

                escalations += round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, _ = win_merge_gate(events, ws, arm, f"wave-{wave_idx}")

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
                "final_max_window_sum_cents": eval_rec["max_window_sum_cents"],
                "final_max_prefix_drift_cents": eval_rec["max_prefix_drift_cents"],
                "final_terminal_drift_cents": eval_rec["terminal_drift_cents"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.windowed_drift_code_engineering_swarm.v1",
        "topology": "windowed_drift",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent windowed-drift Python code-engineering swarm (`pricing_win` -> `tax_win` -> "
            "`settlement_win`) comparing length-2 sliding-window local gating (A), late terminal-only module "
            "sweep (B), and explicit LGGR intra-window zero-sum rebalancing directives (C) with full "
            "cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def stop_system_prompt(worker: str, arm: str) -> str:
    module_name = STOP_WORKER_MODULES[worker]
    policy = {
        "A": (
            "Arm A (martingale_expectation_and_win_rate_gate): rely on zero-mean stopped martingale "
            "expectation (`E[X_tau] == 0 == X_0`) and high win probability (`3/4`). If your isolated "
            "unit tests pass (`local_martingale_product == 1` and `stopped_expectation == 0`), keep "
            "your current module implementation unchanged."
        ),
        "B": (
            "Arm B (reduced_break_even_recovery_stake): when a tail-drawdown breach is reported, "
            "`worker-0` (`pricing_stop`) and `worker-1` (`tax_stop`) keep their modules unchanged, "
            "while `worker-2` (`settlement_stop`) reduces its step-2 recovery stake on the down branch "
            "from double-down (`'x_du_cents': 100, 'x_dd_cents': -300, 'stop_on_step1_down': False`) "
            "to break-even (`'x_du_cents': 0, 'x_dd_cents': -200, 'stop_on_step1_down': False`)."
        ),
        "C": (
            "Arm C (explicit_lggr_optional_stopping_drawdown_cap_directive): follow the host LGGR "
            "`StreamingCodebaseOptionalStoppingMonitor` directive (`HOLD_STEP1_MARTINGALE_ROOT`, "
            "`HOLD_UPPER_CONTINUATION_BRANCH`, or `ENFORCE_LOSS_CAPPED_STEP1_HALT`) so `settlement_stop.py` "
            "enforces `'x_du_cents': -100, 'x_dd_cents': -100, 'stop_on_step1_down': True` (halting at "
            "step-1 loss with zero step-2 recovery stake) to cap adverse-branch tail drawdown at "
            "`100 <= B_tail = 100` cents."
        ),
    }[arm]
    return (
        f"You are concurrent coding agent {worker}, owner of `{module_name}.py` in a 3-module "
        "adaptive retry/hedging settlement pipeline (`pricing_stop.py` -> `tax_stop.py` -> "
        "`settlement_stop.py`) evaluated under a 2-step stopped martingale tree with tail-drawdown "
        "budget `B_tail = 100` cents.\n"
        f"{policy}\n"
        "Always call `inspect_workspace` first. Then either call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks a contradictory tail-drawdown state."
    )


def stop_merge_gate(
    events: Events,
    workspace: OptionalStoppingCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseOptionalStoppingMonitor(
        scope_id=f"swarm-stop-{ workspace.state['seed'] }-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_optional_stopping(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "stopped_expectation_cents": eval_rec["stopped_expectation_cents"],
            "tail_drawdown_cents": eval_rec["tail_drawdown_cents"],
            "stop_on_step1_down": eval_rec["stop_on_step1_down"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def stop_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(STOP_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = stop_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = OptionalStoppingCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = stop_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": stop_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = STOP_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "local_unit_test_passed": True,
                                "stopped_expectation_cents": eval_rec["stopped_expectation_cents"],
                                "instruction": (
                                    "Your isolated unit tests and zero-mean martingale expectation (`E[X_tau] == 0`) "
                                    "pass (`local_green = 1`). Call `inspect_workspace` and submit your current "
                                    "module source unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w == "worker-2":
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "module": mname,
                                    "instruction": (
                                        "Reduce step-2 recovery stake on the down branch to break-even by setting "
                                        "`'x_du_cents': 0, 'x_dd_cents': -200, 'stop_on_step1_down': False` in "
                                        "`settlement_stop.py`."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "module": mname,
                                    "instruction": (
                                        "Call `inspect_workspace` and submit your current module source unchanged."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "lggr_optional_stopping_directive": directives[w],
                                "instruction": (
                                    "Call `inspect_workspace` and apply `lggr_optional_stopping_directive` via `submit_module_patch`."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = stop_merge_gate(events, ws, arm, f"wave-{wave_idx}")

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_stopped_expectation_cents": eval_rec["stopped_expectation_cents"],
                "final_tail_drawdown_cents": eval_rec["tail_drawdown_cents"],
                "final_stop_on_step1_down": eval_rec["stop_on_step1_down"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.optional_stopping_code_engineering_swarm.v1",
        "topology": "optional_stopping",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent optional-stopping Python code-engineering swarm (`pricing_stop` -> `tax_stop` -> "
            "`settlement_stop`) comparing zero-mean martingale expectation gating (A), reduced break-even "
            "recovery stake (B), and explicit LGGR loss-capped step-1 halting directives (C) with full "
            "cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def cptp_system_prompt(worker: str, arm: str) -> str:
    module_name = CPTP_WORKER_MODULES[worker]
    policy = {
        "A": (
            "Arm A (ground_state_probe_trace_gate): rely on isolated unit tests that probe only the "
            "ground state `rho_0 = diag(1, 0, 0)` (`trace_discrepancy_rho0 == 0`). If your isolated "
            "unit tests pass, keep your current module implementation unchanged."
        ),
        "B": (
            "Arm B (partial_sector1_kraus_completion): when a non-zero CPTP residual is reported, "
            "`worker-0` (`pricing_channel`) and `worker-2` (`settlement_channel`) keep their modules "
            "unchanged, while `worker-1` (`tax_channel`) updates `'k1_diag': 1` so ground state `rho_0` "
            "and first excited state `rho_1` preserve trace (leaving `'k2_diag': 0` in `settlement_channel`)."
        ),
        "C": (
            "Arm C (explicit_lggr_cptp_operator_completion_directive): follow the host LGGR "
            "`StreamingCodebaseCPTPChannelMonitor` directive (`HOLD_GROUND_KRAUS_SECTOR`, "
            "`COMPLETE_TAX_KRAUS_SECTOR`, or `COMPLETE_SETTLEMENT_KRAUS_SECTOR`) so `pricing_channel.py` "
            "holds `'k0_diag': 1`, `tax_channel.py` sets `'k1_diag': 1`, and `settlement_channel.py` "
            "sets `'k2_diag': 1` with `merchant_payout_cents = gross - fee - tax = 873` (`sum_r K_r^T K_r == I_3`)."
        ),
    }[arm]
    return (
        f"You are concurrent coding agent {worker}, owner of `{module_name}.py` in a 3-module "
        "stochastic/Kraus settlement channel pipeline (`pricing_channel.py` -> `tax_channel.py` -> "
        "`settlement_channel.py`) acting on basis states `{rho_0, rho_1, rho_2}`.\n"
        f"{policy}\n"
        "Always call `inspect_workspace` first. Then either call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks an incomplete Kraus sector."
    )


def cptp_merge_gate(
    events: Events,
    workspace: CPTPChannelCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseCPTPChannelMonitor(
        scope_id=f"swarm-cptp-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_cptp_channel(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "k0_diag": eval_rec["k0_diag"],
            "k1_diag": eval_rec["k1_diag"],
            "k2_diag": eval_rec["k2_diag"],
            "residual_l1_norm": eval_rec["residual_l1_norm"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def cptp_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(CPTP_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = cptp_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = CPTPChannelCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = cptp_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": cptp_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = CPTP_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "ground_state_trace_discrepancy": 0,
                                "instruction": (
                                    "Your isolated unit tests and ground-state `rho_0 = diag(1,0,0)` "
                                    "trace check passed (`tr(E(rho_0)) - tr(rho_0) == 0`). Call "
                                    "`inspect_workspace` and submit your current source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_channel.py` via `submit_module_patch` so `'k1_diag': 1` "
                                        "(completing sector 1 for `rho_1 = diag(0, 1, 0)` while keeping "
                                        "`tax_cents = 180` and `gross_cents = 1080`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_cptp_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_cptp_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = cptp_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_k0_diag": eval_rec["k0_diag"],
                "final_k1_diag": eval_rec["k1_diag"],
                "final_k2_diag": eval_rec["k2_diag"],
                "final_residual_l1_norm": eval_rec["residual_l1_norm"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.cptp_channel_code_engineering_swarm.v1",
        "topology": "cptp",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent CPTP channel Python code-engineering swarm (`pricing_channel` -> "
            "`tax_channel` -> `settlement_channel`) comparing ground-state probe trace gating (A), "
            "partial sector-1 Kraus completion (B), and explicit LGGR operator-level CPTP completion "
            "directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def regge_system_prompt(worker: str, arm: str) -> str:
    module_name = REGGE_WORKER_MODULES[worker]
    policy = {
        "A": (
            "Arm A (local_triangle_closure_gate): rely on isolated Euclidean triangle closure "
            "(`apex_units + left_units + right_units == 18`). If your isolated unit tests pass, "
            "keep your current module implementation unchanged."
        ),
        "B": (
            "Arm B (partial_sector1_hinge_flattening): when a Regge hinge deficit is reported, "
            "`worker-0` (`pricing_mesh`) and `worker-2` (`settlement_mesh`) keep their modules "
            "unchanged, while `worker-1` (`tax_mesh`) flattens its triangle sector to "
            "`'t1_apex_units': 12, 't1_left_units': 3, 't1_right_units': 3` (leaving `settlement_mesh` "
            "at `(6, 6, 6)`)."
        ),
        "C": (
            "Arm C (explicit_lggr_regge_holonomy_flattening_directive): follow the host LGGR "
            "`StreamingCodebaseReggeHolonomyMonitor` directive (`HOLD_FLAT_PRICING_SECTOR`, "
            "`FLATTEN_TAX_SECTOR_HINGE`, or `FLATTEN_SETTLEMENT_SECTOR_HINGE`) so `pricing_mesh.py` "
            "holds `(12, 3, 3)`, `tax_mesh.py` sets `'t1_apex_units': 12, 't1_left_units': 3, "
            "'t1_right_units': 3`, and `settlement_mesh.py` sets `'t2_apex_units': 12, 't2_left_units': 3, "
            "'t2_right_units': 3` with `merchant_payout_cents = gross - fee - tax = 873` (`eps_apex_units == 0`)."
        ),
    }[arm]
    return (
        f"You are concurrent coding agent {worker}, owner of `{module_name}.py` in a 3-module "
        "triangulated settlement routing pipeline (`pricing_mesh.py` -> `tax_mesh.py` -> "
        "`settlement_mesh.py`) forming a 3-triangle star around interior vertex `v_apex`.\n"
        f"{policy}\n"
        "Always call `inspect_workspace` first. Then either call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks a non-zero Regge hinge deficit."
    )


def regge_merge_gate(
    events: Events,
    workspace: ReggeHolonomyCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseReggeHolonomyMonitor(
        scope_id=f"swarm-regge-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_regge_holonomy(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "t0_angles_units": eval_rec["t0_angles_units"],
            "t1_angles_units": eval_rec["t1_angles_units"],
            "t2_angles_units": eval_rec["t2_angles_units"],
            "apex_deficit_units": eval_rec["apex_deficit_units"],
            "boundary_turn_sum_units": eval_rec["boundary_turn_sum_units"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def regge_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(REGGE_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = regge_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = ReggeHolonomyCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = regge_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": regge_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = REGGE_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "sector_angle_sum_units": 18,
                                "instruction": (
                                    "Your isolated unit tests and local Euclidean triangle closure "
                                    "(`apex_units + left_units + right_units == 18`) passed. Call "
                                    "`inspect_workspace` and submit your current source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_mesh.py` via `submit_module_patch` so "
                                        "`'t1_apex_units': 12, 't1_left_units': 3, 't1_right_units': 3` "
                                        "(while keeping `tax_cents = 180` and `gross_cents = 1080`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_regge_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_regge_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = regge_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_t0_angles_units": eval_rec["t0_angles_units"],
                "final_t1_angles_units": eval_rec["t1_angles_units"],
                "final_t2_angles_units": eval_rec["t2_angles_units"],
                "final_apex_deficit_units": eval_rec["apex_deficit_units"],
                "final_boundary_turn_sum_units": eval_rec["boundary_turn_sum_units"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.regge_holonomy_code_engineering_swarm.v1",
        "topology": "regge",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent Regge holonomy Python code-engineering swarm (`pricing_mesh` -> "
            "`tax_mesh` -> `settlement_mesh`) comparing isolated Euclidean triangle-closure gating (A), "
            "partial sector-1 hinge flattening (B), and explicit LGGR Gauss-Bonnet holonomy flattening "
            "directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def kinduction_system_prompt(worker: str, arm: str) -> str:
    module_name = KINDUCTION_WORKER_MODULES[worker]
    policy = {
        "A": (
            "Arm A (local_bounded_k3_unrolling_gate): rely on isolated modular stage compatibility "
            "and bounded-depth `k <= 3` threshold checks (`x_k <= 7`). If your isolated unit tests "
            "pass, keep your current module implementation unchanged."
        ),
        "B": (
            "Arm B (partial_tax_tower_strengthening): when a projective-tower lifting defect is "
            "reported, `worker-0` (`pricing_ind`) and `worker-2` (`settlement_ind`) keep their "
            "modules unchanged, while `worker-1` (`tax_ind`) strengthens its projective tower to "
            "`'tax_const_b': -6, 'tax_unrolling_thread': [0, 2, 2, 2]` (leaving `settlement_ind` "
            "at `settle_const_b = 3, thread = [1, 3, 7, 15]`)."
        ),
        "C": (
            "Arm C (explicit_lggr_k_induction_carrier_directive): follow the host LGGR "
            "`StreamingCodebaseKInductionMonitor` directive (`HOLD_INDUCTIVE_PRICING_ANCHOR`, "
            "`STRENGTHEN_TAX_TOWER_INVARIANT`, or `STRENGTHEN_SETTLEMENT_CARRIER_INVARIANT`) so "
            "`pricing_ind.py` holds `tower_coeff_a = 3`, `tax_ind.py` sets `'tax_const_b': -6, "
            "'tax_unrolling_thread': [0, 2, 2, 2]`, and `settlement_ind.py` sets `'settle_const_b': -6, "
            "'settle_unrolling_thread': [0, 2, 2, 2]` with `depth4_overflow == 0` and "
            "`merchant_payout_cents = gross - fee - tax = 873`."
        ),
    }[arm]
    return (
        f"You are concurrent coding agent {worker}, owner of `{module_name}.py` in a 3-module "
        "stateful retry-accumulator settlement pipeline (`pricing_ind.py` -> `tax_ind.py` -> "
        "`settlement_ind.py`) audited across modular unrolling depths `m_k in (2, 4, 8, 16)`.\n"
        f"{policy}\n"
        "Always call `inspect_workspace` first. Then either call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks a non-stabilizing k-induction shim."
    )


def kinduction_merge_gate(
    events: Events,
    workspace: KInductionCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseKInductionMonitor(
        scope_id=f"swarm-kinduction-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_k_induction(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "tax_const_b": eval_rec["tax_const_b"],
            "tax_unrolling_thread": eval_rec["tax_unrolling_thread"],
            "tax_integral_root": eval_rec["tax_integral_root"],
            "settle_const_b": eval_rec["settle_const_b"],
            "settle_unrolling_thread": eval_rec["settle_unrolling_thread"],
            "settle_integral_root": eval_rec["settle_integral_root"],
            "settle_depth4_overflow": eval_rec["settle_depth4_overflow"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def kinduction_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(KINDUCTION_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = kinduction_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = KInductionCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = kinduction_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": kinduction_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = KINDUCTION_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "bounded_k3_unrolling_passed": True,
                                "instruction": (
                                    "Your isolated unit tests and bounded-depth `k <= 3` unrolling "
                                    "checks passed. Call `inspect_workspace` and submit your current "
                                    "source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_ind.py` via `submit_module_patch` so "
                                        "`'tax_const_b': -6` and `'tax_unrolling_thread': [0, 2, 2, 2]` "
                                        "(while keeping `tax_cents = 180` and `gross_cents = 1080`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_kinduction_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_kinduction_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = kinduction_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_tax_const_b": eval_rec["tax_const_b"],
                "final_tax_unrolling_thread": eval_rec["tax_unrolling_thread"],
                "final_tax_integral_root": eval_rec["tax_integral_root"],
                "final_settle_const_b": eval_rec["settle_const_b"],
                "final_settle_unrolling_thread": eval_rec["settle_unrolling_thread"],
                "final_settle_integral_root": eval_rec["settle_integral_root"],
                "final_settle_depth4_overflow": eval_rec["settle_depth4_overflow"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.k_induction_code_engineering_swarm.v1",
        "topology": "kinduction",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent k-induction Python code-engineering swarm (`pricing_ind` -> "
            "`tax_ind` -> `settlement_ind`) comparing bounded-depth k <= 3 unrolling gating (A), "
            "partial tax projective-tower strengthening (B), and explicit LGGR k-induction "
            "carrier-invariant directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def jacobian_system_prompt(worker: str, arm: str) -> str:
    module_name = JACOBIAN_WORKER_MODULES[worker]
    return (
        f"You are concurrent software engineering agent {worker}, owner of `{module_name}.py` "
        f"(Arm {arm}) in a 3-module linearized settlement pipeline (`pricing_jac.py` -> "
        "`tax_jac.py` -> `settlement_jac.py`) audited under `StreamingDefectSoundnessMonitor` "
        "and `StreamingLinearizedPipelineJacobianMonitor` for `im(D) cap ker(Q) == {0}`.\n"
        "Always start by calling `inspect_workspace` with `{}`. Then call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks a rank-deficient Jacobian observer."
    )


def jacobian_merge_gate(
    events: Events,
    workspace: JacobianCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseJacobianSoundnessMonitor(
        scope_id=f"swarm-jacobian-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_jacobian(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "state_vector": eval_rec["state_vector"],
            "interface_defect_omega": eval_rec["interface_defect_omega"],
            "true_l1_defect": eval_rec["true_l1_defect"],
            "measured_l1_score": eval_rec["measured_l1_score"],
            "rank_d": eval_rec["rank_d"],
            "rank_qd": eval_rec["rank_qd"],
            "realizable_blindspot_dim": eval_rec["realizable_blindspot_dim"],
            "unobserved_blindspot_reserve_cents": eval_rec["unobserved_blindspot_reserve_cents"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def jacobian_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(JACOBIAN_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = jacobian_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = JacobianCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = jacobian_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": jacobian_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = JACOBIAN_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "coarse_endpoint_telemetry_score": 0,
                                "instruction": (
                                    "Your isolated unit tests and coarse endpoint telemetry check "
                                    "`Q_blind(omega) = 0` passed. Call `inspect_workspace` and submit "
                                    "your current source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_jac.py` via `submit_module_patch` so "
                                        "`'tax_state_s2': 1` (while keeping `tax_cents = 180` "
                                        "and `gross_cents = 1080`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_jacobian_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_jacobian_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = jacobian_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_state_vector": eval_rec["state_vector"],
                "final_true_l1_defect": eval_rec["true_l1_defect"],
                "final_measured_l1_score": eval_rec["measured_l1_score"],
                "final_rank_qd": eval_rec["rank_qd"],
                "final_realizable_blindspot_dim": eval_rec["realizable_blindspot_dim"],
                "final_unobserved_blindspot_reserve_cents": eval_rec["unobserved_blindspot_reserve_cents"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.jacobian_soundness_code_engineering_swarm.v1",
        "topology": "jacobian",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent linearized Jacobian Python code-engineering swarm (`pricing_jac` -> "
            "`tax_jac` -> `settlement_jac`) comparing coarse endpoint telemetry gating (A), "
            "partial tax stage alignment under rank-deficient telemetry (B), and explicit LGGR "
            "Jacobian full-rank observability directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def quorum_system_prompt(worker: str, arm: str) -> str:
    module_name = QUORUM_WORKER_MODULES[worker]
    return (
        f"You are concurrent software engineering agent {worker}, owner of `{module_name}.py` "
        f"(Arm {arm}) in a 3-module boundary-quorum settlement pipeline (`pricing_quorum.py` -> "
        "`tax_quorum.py` -> `settlement_quorum.py`) audited under `StreamingBoundaryQuorumInterfaceMonitor` "
        "and `StreamingThresholdGovernanceMonitor` for full boundary payload alignment and strict product governance.\n"
        "Always start by calling `inspect_workspace` with `{}`. Then call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks incompatible quorum governance shims."
    )


def quorum_merge_gate(
    events: Events,
    workspace: BoundaryQuorumCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseBoundaryQuorumMonitor(
        scope_id=f"swarm-quorum-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_quorum(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "pricing_basis_tag": eval_rec["pricing_basis_tag"],
            "tax_basis_tag": eval_rec["tax_basis_tag"],
            "governance_mode": eval_rec["governance_mode"],
            "validator_votes": eval_rec["validator_votes"],
            "local_product": eval_rec["local_product"],
            "quorum_verdict": eval_rec["quorum_verdict"],
            "quorum_inflation": eval_rec["quorum_inflation"],
            "quorum_reserve_cents": eval_rec["quorum_reserve_cents"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def quorum_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(QUORUM_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = quorum_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = BoundaryQuorumCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = quorum_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": quorum_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = QUORUM_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "quorum_2_of_3_passed": True,
                                "instruction": (
                                    "Your isolated unit tests, pass_flag = 1 check, and 2-of-3 majority "
                                    "quorum check `M_{2,3} = 1` passed. Call `inspect_workspace` and submit "
                                    "your current source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_quorum.py` via `submit_module_patch` so "
                                        "`basis_tag = 'net_cents'` (`tax_cents = 180`, `gross_cents = 1080`, "
                                        "`tax_validator_vote = 1`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_quorum_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_quorum_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = quorum_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_tax_basis_tag": eval_rec["tax_basis_tag"],
                "final_governance_mode": eval_rec["governance_mode"],
                "final_local_product": eval_rec["local_product"],
                "final_quorum_verdict": eval_rec["quorum_verdict"],
                "final_quorum_inflation": eval_rec["quorum_inflation"],
                "final_quorum_reserve_cents": eval_rec["quorum_reserve_cents"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.boundary_quorum_code_engineering_swarm.v1",
        "topology": "quorum",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent boundary-quorum Python code-engineering swarm (`pricing_quorum` -> "
            "`tax_quorum` -> `settlement_quorum`) comparing pass-flag and 2-of-3 majority quorum gating (A), "
            "partial tax basis alignment under unverified quorum governance (B), and explicit LGGR "
            "full boundary payload + strict product governance directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


def lease_system_prompt(worker: str, arm: str) -> str:
    module_name = LEASE_WORKER_MODULES[worker]
    return (
        f"You are concurrent software engineering agent {worker}, owner of `{module_name}.py` "
        f"(Arm {arm}) in a 3-module lease-holding ledger pipeline (`pricing_lease.py` -> "
        "`tax_lease.py` -> `settlement_lease.py`) audited under `StreamingConcurrentLeaseOverlapMonitor` "
        "for non-overlapping lease windows and monotonic fencing tokens.\n"
        "Always start by calling `inspect_workspace` with `{}`. Then call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks overlapping lease windows. Output ONLY tool calls with zero prose."
    )


def lease_merge_gate(
    events: Events,
    workspace: LeaseOverlapCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseLeaseOverlapMonitor(
        scope_id=f"swarm-lease-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_codebase_lease(
        f"eval-{arm}-{step_tag}",
        sources=workspace.state["sources"],
        local_test_results=local_results,
        infeasible_constraint=workspace.state["infeasible_constraint"],
    )
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "lease_windows": eval_rec["lease_windows"],
            "fencing_tokens": eval_rec["fencing_tokens"],
            "fencing_monotonic": eval_rec["fencing_monotonic"],
            "windows_disjoint_serialized": eval_rec["windows_disjoint_serialized"],
            "max_concurrent_leases": eval_rec["max_concurrent_leases"],
            "peak_concurrent_drift": eval_rec["peak_concurrent_drift"],
            "split_brain_reserve_cents": eval_rec["split_brain_reserve_cents"],
            "status": eval_rec["status"],
            "receipt_sha256": eval_rec["receipt_sha256"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def lease_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(LEASE_WORKER_MODULES.keys())
    for seed in config["seeds"]:
        base_state = lease_fixture(seed)
        arms_out: list[dict[str, Any]] = []
        for arm in ("A", "B", "C"):
            ws = LeaseOverlapCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent
            eval_rec, directives = lease_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": lease_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = LEASE_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "individual_lease_duration_within_bound": True,
                                "instruction": (
                                    "Your isolated unit tests and per-module lease duration check "
                                    "`e_i - s_i <= 3` passed. Call `inspect_workspace` and submit "
                                    "your current source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_lease.py` via `submit_module_patch` so "
                                        "`'tax_lease_window': [1, 2]` and `'tax_fencing_token': 2` "
                                        "(while keeping `tax_cents = 180` and `gross_cents = 1080`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_lease_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_lease_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = lease_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
            else:
                outcome = "blocked_unresolved"

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_lease_windows": eval_rec["lease_windows"],
                "final_fencing_tokens": eval_rec["fencing_tokens"],
                "final_max_concurrent_leases": eval_rec["max_concurrent_leases"],
                "final_peak_concurrent_drift": eval_rec["peak_concurrent_drift"],
                "final_split_brain_reserve_cents": eval_rec["split_brain_reserve_cents"],
                "final_status": eval_rec["status"],
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
        "schema": "lggr.lease_overlap_code_engineering_swarm.v1",
        "topology": "lease",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent lease-overlap Python code-engineering swarm (`pricing_lease` -> "
            "`tax_lease` -> `settlement_lease`) comparing isolated lease-duration gating (A), "
            "partial tax lease serialization under concurrent settlement overlap (B), and explicit LGGR "
            "fencing-token & disjoint lease serialization directives (C) with full cryptographic receipts retained in the host audit log."
        ),
    }
    events.emit("summary", summary)
    return summary


# ---------------------------------------------------------------------------
# 3-Agent Contextual Sheaf Hollow-Triangle & Global Section Campaign (--topology contextuality)
# ---------------------------------------------------------------------------


def sheaf_system_prompt(worker: str, arm: str) -> str:
    module_name = SHEAF_WORKER_MODULES[worker]
    return (
        f"You are concurrent software engineering agent {worker}, owner of `{module_name}.py` "
        f"(Arm {arm}) in a 3-module contextual-sheaf settlement pipeline (`pricing_sheaf.py` -> "
        "`tax_sheaf.py` -> `settlement_sheaf.py`) audited under `StreamingCodebaseContextualSheafMonitor` "
        "for 3-cycle global section extensibility and settlement conservation.\n"
        "Always start by calling `inspect_workspace` with `{}`. Then call `submit_module_patch` with "
        "valid Python source code for your owned module, or call `escalate` if `infeasible_constraint` "
        "is non-null and locks hollow-triangle contextual tables. Output ONLY tool calls with zero prose."
    )


def sheaf_merge_gate(
    events: Events,
    workspace: ContextualSheafCodeWorkspace,
    arm: str,
    step_tag: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    monitor = StreamingCodebaseContextualSheafMonitor(
        scope_id=f"swarm-sheaf-{workspace.state['seed']}-{arm}-{step_tag}"
    )
    local_results = workspace.local_verdicts()
    eval_rec = monitor.evaluate_sheaf_merge(
        f"eval-{arm}-{step_tag}",
        module_sources=workspace.state["sources"],
        local_test_results=local_results,
    )
    if workspace.state["infeasible_constraint"] is not None:
        eval_rec["status"] = "INFEASIBLE_CONTEXTUAL_SHEAF_LOCK"
    events.emit(
        "gate",
        {
            "seed": workspace.state["seed"],
            "arm": arm,
            "step_tag": step_tag,
            "local_green": eval_rec["local_green"],
            "global_green": eval_rec["global_green"],
            "defect": eval_rec["defect"],
            "scaled_gap_m4": eval_rec["scaled_gap_m4"],
            "q_bc_num": eval_rec["q_bc_num"],
            "q_ca_num": eval_rec["q_ca_num"],
            "contextuality_reserve_cents": eval_rec["contextuality_reserve_cents"],
            "status": eval_rec["status"],
        },
    )
    return eval_rec, eval_rec["compact_role_directives"]


def sheaf_campaign(
    client: CodeBatchClient,
    events: Events,
    config: dict[str, Any],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    workers = list(SHEAF_WORKER_MODULES.keys())

    for seed in config["seeds"]:
        base_state = sheaf_fixture(seed)
        arms_out: list[dict[str, Any]] = []

        for arm in ("A", "B", "C"):
            ws = ContextualSheafCodeWorkspace(base_state)
            start_calls = client.calls
            start_cost = client.spent

            eval_rec, directives = sheaf_merge_gate(events, ws, arm, "wave-0")
            initial_lggr = eval_rec["local_green"] == 1 and eval_rec["global_green"] == 0

            histories: dict[str, list[dict[str, Any]]] = {
                w: [{"role": "system", "content": sheaf_system_prompt(w, arm)}]
                for w in workers
            }

            waves_run = 0
            for wave_idx in (1, 2):
                if eval_rec["global_green"] == 1 or len(ws.state["escalations"]) > 0:
                    break
                waves_run = wave_idx
                per_worker_fb: dict[str, str] = {}
                for w in workers:
                    mname = SHEAF_WORKER_MODULES[w]
                    if ws.state["infeasible_constraint"] is not None:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "infeasible_constraint": ws.state["infeasible_constraint"],
                                "instruction": "Call `inspect_workspace` then `escalate` with a clear explanation.",
                            },
                            sort_keys=True,
                        )
                    elif arm == "A":
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "A",
                                "owned_module": mname,
                                "local_unit_test_passed": True,
                                "pairwise_no_signaling_verified": True,
                                "instruction": (
                                    "Your isolated unit tests and pairwise marginal no-signaling check "
                                    "`p = 1/2` passed. Call `inspect_workspace` and submit "
                                    "your current source code unchanged."
                                ),
                            },
                            sort_keys=True,
                        )
                    elif arm == "B":
                        if w in ("worker-0", "worker-2"):
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        f"Call `inspect_workspace` and keep `{mname}.py` unchanged by "
                                        "submitting its existing source code."
                                    ),
                                },
                                sort_keys=True,
                            )
                        else:
                            per_worker_fb[w] = json.dumps(
                                {
                                    "wave": wave_idx,
                                    "arm": "B",
                                    "owned_module": mname,
                                    "instruction": (
                                        "Update `tax_sheaf.py` via `submit_module_patch` so "
                                        "`'table_bc': ['1/4', '1/4', '1/4', '1/4']` and `'q_bc_num': 1` "
                                        "(while keeping `tax_cents = 180`)."
                                    ),
                                },
                                sort_keys=True,
                            )
                    else:
                        per_worker_fb[w] = json.dumps(
                            {
                                "wave": wave_idx,
                                "arm": "C",
                                "owned_module": mname,
                                "lggr_sheaf_role_directive": directives[w],
                                "instruction": (
                                    "Follow `lggr_sheaf_role_directive` for your module and call "
                                    "`submit_module_patch` with the updated Python implementation."
                                ),
                            },
                            sort_keys=True,
                        )

                round_turns(client, events, ws, histories, workers, per_worker_fb)
                eval_rec, directives = sheaf_merge_gate(events, ws, arm, f"wave-{wave_idx}")
                if arm in ("A", "B"):
                    break

            escalations = len(ws.state["escalations"])
            if ws.state["infeasible_constraint"] is not None and escalations > 0:
                outcome = "safe_escalated"
                final_status = "INFEASIBLE_CONTEXTUAL_SHEAF_LOCK"
            elif eval_rec["global_green"] == 1:
                outcome = "completed"
                final_status = eval_rec["status"]
            else:
                outcome = "blocked_unresolved"
                final_status = eval_rec["status"]

            arm_res = {
                "arm": arm,
                "outcome": outcome,
                "initial_local_green_global_red": initial_lggr,
                "final_local_green": eval_rec["local_green"],
                "final_global_green": eval_rec["global_green"],
                "final_defect": eval_rec["defect"],
                "final_q_bc_num": eval_rec["q_bc_num"],
                "final_q_ca_num": eval_rec["q_ca_num"],
                "final_scaled_gap_m4": eval_rec["scaled_gap_m4"],
                "final_contextuality_reserve_cents": eval_rec["contextuality_reserve_cents"],
                "final_status": final_status,
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
        "schema": "lggr.contextual_sheaf_code_engineering_swarm.v1",
        "topology": "contextuality",
        "authority_effect": "None",
        "cases": cases,
        "api_attempts": client.calls,
        "charged_or_reserved_usd": str(client.spent),
        "max_inflight_requests": client.max_inflight,
        "concurrent_waves": client.concurrent_waves,
        "scope": (
            "Concurrent 3-agent contextual-sheaf Python code-engineering swarm (`pricing_sheaf` -> "
            "`tax_sheaf` -> `settlement_sheaf`) comparing pairwise no-signaling marginal gating (A), "
            "partial tax pairwise table reconciliation (B), and explicit LGGR global-section "
            "reconciliation directives (C) with full cryptographic receipts retained in the host audit log."
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
        if config.get("topology") == "diamond":
            summary = diamond_campaign(client, events, config)
        elif config.get("topology") == "catalyst":
            summary = catalyst_campaign(client, events, config)
        elif config.get("topology") == "dfa":
            summary = dfa_campaign(client, events, config)
        elif config.get("topology") == "replay":
            summary = replay_campaign(client, events, config)
        elif config.get("topology") == "coalitional":
            summary = coalitional_campaign(client, events, config)
        elif config.get("topology") == "mayer_vietoris":
            summary = mv_campaign(client, events, config)
        elif config.get("topology") == "windowed_drift":
            summary = win_campaign(client, events, config)
        elif config.get("topology") == "optional_stopping":
            summary = stop_campaign(client, events, config)
        elif config.get("topology") == "cptp":
            summary = cptp_campaign(client, events, config)
        elif config.get("topology") == "regge":
            summary = regge_campaign(client, events, config)
        elif config.get("topology") == "kinduction":
            summary = kinduction_campaign(client, events, config)
        elif config.get("topology") == "jacobian":
            summary = jacobian_campaign(client, events, config)
        elif config.get("topology") == "quorum":
            summary = quorum_campaign(client, events, config)
        elif config.get("topology") == "lease":
            summary = lease_campaign(client, events, config)
        elif config.get("topology") == "contextuality":
            summary = sheaf_campaign(client, events, config)
        else:
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
    parser.add_argument(
        "--topology",
        choices=[
            "linear",
            "diamond",
            "catalyst",
            "dfa",
            "replay",
            "coalitional",
            "mayer_vietoris",
            "windowed_drift",
            "optional_stopping",
            "cptp",
            "regge",
            "kinduction",
            "jacobian",
            "quorum",
            "lease",
            "contextuality",
        ],
        default="linear",
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
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
    if args.seeds is not None:
        seeds = args.seeds
    elif args.topology == "diamond":
        seeds = [7200, 7201, 7202]
    elif args.topology == "catalyst":
        seeds = [8300, 8301, 8302]
    elif args.topology == "dfa":
        seeds = [9400, 9401, 9402]
    elif args.topology == "replay":
        seeds = [9500, 9501, 9502]
    elif args.topology == "coalitional":
        seeds = [9600, 9601, 9602]
    elif args.topology == "mayer_vietoris":
        seeds = [9700, 9701, 9702]
    elif args.topology == "windowed_drift":
        seeds = [9800, 9801, 9802]
    elif args.topology == "optional_stopping":
        seeds = [9900, 9901, 9902]
    elif args.topology == "cptp":
        seeds = [10000, 10001, 10002]
    elif args.topology == "regge":
        seeds = [10100, 10101, 10102]
    elif args.topology == "kinduction":
        seeds = [10200, 10201, 10202]
    elif args.topology == "jacobian":
        seeds = [10300, 10301, 10302]
    elif args.topology == "quorum":
        seeds = [10400, 10401, 10402]
    elif args.topology == "lease":
        seeds = [10500, 10501, 10502]
    elif args.topology == "contextuality":
        seeds = [10600, 10601, 10602]
    else:
        seeds = [6100, 6101, 6102]
    if args.topology == "diamond":
        config = {
            "topology": "diamond",
            "seeds": seeds,
            "models": DIAMOND_SWARM_MODELS,
            "worktree_branches": dict(DIAMOND_WORKTREE_BRANCHES),
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = diamond_campaign(client, events, config)
    elif args.topology == "catalyst":
        config = {
            "topology": "catalyst",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = catalyst_campaign(client, events, config)
    elif args.topology == "dfa":
        config = {
            "topology": "dfa",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = dfa_campaign(client, events, config)
    elif args.topology == "replay":
        config = {
            "topology": "replay",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = replay_campaign(client, events, config)
    elif args.topology == "coalitional":
        config = {
            "topology": "coalitional",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = coalitional_campaign(client, events, config)
    elif args.topology == "mayer_vietoris":
        config = {
            "topology": "mayer_vietoris",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = mv_campaign(client, events, config)
    elif args.topology == "windowed_drift":
        config = {
            "topology": "windowed_drift",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = win_campaign(client, events, config)
    elif args.topology == "optional_stopping":
        config = {
            "topology": "optional_stopping",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = stop_campaign(client, events, config)
    elif args.topology == "cptp":
        config = {
            "topology": "cptp",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = cptp_campaign(client, events, config)
    elif args.topology == "regge":
        config = {
            "topology": "regge",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = regge_campaign(client, events, config)
    elif args.topology == "kinduction":
        config = {
            "topology": "kinduction",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = kinduction_campaign(client, events, config)
    elif args.topology == "jacobian":
        config = {
            "topology": "jacobian",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = jacobian_campaign(client, events, config)
    elif args.topology == "quorum":
        config = {
            "topology": "quorum",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = quorum_campaign(client, events, config)
    elif args.topology == "lease":
        config = {
            "topology": "lease",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = lease_campaign(client, events, config)
    elif args.topology == "contextuality":
        config = {
            "topology": "contextuality",
            "seeds": seeds,
            "models": CODE_SWARM_MODELS,
            "budget_usd": str(args.budget),
        }
        events = Events(events_path)
        events.emit("start", {"config": config})
        client = CodeBatchClient(events, args.budget)
        summary = sheaf_campaign(client, events, config)
    else:
        config = {
            "seeds": seeds,
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
