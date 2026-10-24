"""Central LLM Gateway Adapter for external provider access.

Thin Python adapter connecting callers to external model providers (OpenRouter, etc.)
with shared budget admission and strict AuthorityEffect: None enforcement.

AuthorityEffect: None.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from typing import Any, Dict, Optional, Sequence

from omega_engine_operations.domain.rop.result import Err
from omega_engine_woland.domain.providers.budget import BudgetController
from omega_engine_woland.domain.providers.types import (
    CandidateRequest,
    DecodingParamsV1,
    Provider,
    ProviderConfigError,
    ProviderError,
)

from .adapters.model_backends import (
    DEFAULT_BUDGET_LIMIT_MICROUSD as DEFAULT_BUDGET_LIMIT_MICROUSD,
    DEFAULT_CASCADE_MODELS,
    resolve_openrouter_api_key as resolve_openrouter_api_key,
)
from .wire import decode_reply


@dataclass(frozen=True)
class LlmReply:
    """Standardized response from an external LLM completion."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float | None
    raw_response: Dict[str, Any]
    authority_effect: str = "None"
    reserved_microusd: int | None = None
    estimated_microusd: int | None = None
    settled_microusd: int | None = None

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, LlmReply)
        return (
            self.content == other.content
            and self.input_tokens == other.input_tokens
            and self.output_tokens == other.output_tokens
            and self.model == other.model
            and self.cost_usd == other.cost_usd
            and self.raw_response == other.raw_response
            and self.authority_effect == other.authority_effect
            and self.reserved_microusd == other.reserved_microusd
            and self.estimated_microusd == other.estimated_microusd
            and self.settled_microusd == other.settled_microusd
        )

    def __hash__(self) -> int:
        return hash((
            type(self),
            self.content,
            self.input_tokens,
            self.output_tokens,
            self.model,
            self.cost_usd,
            self.authority_effect,
            self.reserved_microusd,
            self.estimated_microusd,
            self.settled_microusd,
        ))


class LlmGateway:
    """Plain-prompt facade over an injected, accounted PFP run gateway.

    Selection preferences do not authorize fallback after failure. Credentials,
    transport timeout and continuing accounting belong to the existing gateway.
    Constructor-only use remains inspectable for the retired seat executor.
    """

    def __init__(
        self,
        *,
        model: Optional[str] = None,
        fallback_models: Optional[Sequence[str]] = None,
        budget_controller: Optional[BudgetController] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 2048,
        timeout: float = 30.0,
        gateway=None,
        memory=None,
        memory_keys: Optional[Sequence[str]] = None,
    ) -> None:
        from uuid import uuid4
        from omega_engine_pfp.infrastructure.estimated_gateway import (
            DurableRunGateway, EstimatedBudgetGateway,
        )

        if gateway is not None and not isinstance(gateway, (EstimatedBudgetGateway, DurableRunGateway)):
            raise ProviderConfigError("PFP_ACCOUNTED_GATEWAY_REQUIRED")
        self._gateway = gateway
        from .residual_memory import ResidualMemory
        if memory is not None and type(memory) is not ResidualMemory:
            raise ProviderConfigError("EXACT_RESIDUAL_MEMORY_REQUIRED")
        if (memory is None) != (memory_keys is None):
            raise ProviderConfigError("MEMORY_AND_KEYS_REQUIRED_TOGETHER")
        self._memory = memory
        self._memory_keys = None if memory_keys is None else list(memory_keys)
        self._run_id = uuid4().hex
        self.last_turn = None
        self.turn_history = []
        self._legacy_budget = budget_controller

        if fallback_models is not None:
            self.cascade_models = tuple(fallback_models)
            if not self.cascade_models:
                raise ValueError("fallback_models must not be empty")
            self.model = self.cascade_models[0]
        elif model is not None:
            self.cascade_models = (model,)
            self.model = model
        else:
            cascade_env = os.environ.get("OPENROUTER_CASCADE_MODELS")
            if cascade_env:
                self.cascade_models = tuple(m.strip() for m in cascade_env.split(",") if m.strip())
                if not self.cascade_models:
                    raise ValueError("OPENROUTER_CASCADE_MODELS must not be empty")
                self.model = self.cascade_models[0]
            else:
                default_env = os.environ.get("OPENROUTER_MODEL")
                if default_env:
                    self.cascade_models = (default_env,)
                    self.model = default_env
                else:
                    self.cascade_models = DEFAULT_CASCADE_MODELS
                    self.model = self.cascade_models[0]

        self.budget_controller = (budget_controller if budget_controller is not None
            else getattr(gateway, "budget", None))
        self.max_tokens = max_tokens
        self.timeout = timeout

    def _observe_action(self, record, attempt_id):
        """Retain existing custody, including interrupted sends, without another ledger."""
        if self._gateway is None:
            return
        try:
            claim = self._gateway.action(attempt_id)
            record["attempt_claim"] = claim
            record["attempted"] = claim["state"] != "refused_before_dispatch"
            if "wire_file" in claim and record["provider_wire"] is None:
                from omega_engine_pfp.infrastructure.pilot_matrix import _wire
                record["provider_wire"] = _wire(self._gateway.raw_reply(attempt_id))
        except KeyError:
            pass
        except Exception as exc:
            # The original error/cancellation still propagates. Missing custody
            # must not imply that an attempted send was free.
            record["custody_error"] = type(exc).__name__

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model_override: Optional[str] = None,
    ) -> LlmReply:
        """Check the actual bound reply; failures never select another model."""
        import json
        from omega_engine_pfp.infrastructure.pilot_matrix import validate_pilot_gateways, _wire
        from omega_engine_pfp.infrastructure.task_turn import prepare_task_turn, PfpTurnRefusal

        model = model_override or self.model
        attempt_id = f"llm-facade:{self._run_id}:{len(self.turn_history)}"
        record = dict(ok=False, content=None, error=None, pfp=None, usage={},
            provider_wire=None, attempt_state=None, attempt_claim=None, attempted=False,
            custody_error=None, cost_usd=None, reserved_microusd=None,
            estimated_microusd=None)
        self.last_turn = record
        self.turn_history.append(record)
        try:
            if self._gateway is None:
                raise ProviderConfigError("PFP_ACCOUNTED_GATEWAY_REQUIRED")
            if self._legacy_budget is not None and self._legacy_budget is not getattr(self._gateway, "budget", None):
                raise ProviderConfigError("PFP_LEGACY_BUDGET_CONFLICT: use the existing gateway controller")
            validate_pilot_gateways({model: self._gateway}, [model], max_tokens=self.max_tokens)
            if self._memory is not None:
                recalled = self._memory.prepare(user_prompt, model=model, keys=self._memory_keys)
                if not recalled.ok:
                    record["error"] = recalled.code
                    raise ProviderError(recalled.code)
                record["memory"] = recalled.value
                user_prompt = recalled.value["user"]
            request = CandidateRequest(system=system_prompt, user=user_prompt,
                decoding=DecodingParamsV1())
            turn = prepare_task_turn(system=system_prompt, user=user_prompt,
                task_id=f"llm-facade:{self._run_id}", attempt_id=attempt_id,
                answer_schema={"anyOf": [{"type": "object"}, {"type": "array"},
                    {"type": "string", "minLength": 1}]}, checker_id="plain-prompt-shape-only-v1")
            record["binding"] = turn.binding
            mediated = replace(request, system=turn.prompt.system, user=turn.prompt.user)
            result = self._gateway.for_action(attempt_id).complete_result(mediated,
                provider=Provider.OPENROUTER, model=model)
            if isinstance(result, Err):
                record["error"] = result.error.code
                record["provider_wire"] = result.error.response_metadata() or None
                raise result.error.cause if result.error.cause is not None else ProviderError(result.error.code)
            outcome = result.value
            candidate, admitted = outcome.candidate, outcome.admitted
            record.update(provider_wire=_wire(outcome.reply_bytes), attempt_state=outcome.state,
                cost_usd=candidate.cost_usd,
                usage=dict(prompt_tokens=candidate.input_tokens, completion_tokens=candidate.output_tokens,
                    cost=candidate.cost_usd, generation_id=candidate.generation_id),
                reserved_microusd=admitted.receipt.cost_microusd if admitted.receipt is not None else None,
                estimated_microusd=admitted.estimated_microusd)
            if candidate.model != model:
                raise ProviderError("PROVIDER_IDENTITY_MISMATCH")
            checked = turn.check_completion(candidate.content)
            record["pfp"] = checked
            if (outcome.state not in {"CompletedSettled", "CompletedPendingSettlement"}
                    or not checked["schema_valid"] or checked["failure_class"] != "NONE"):
                raise PfpTurnRefusal(checked, candidate=candidate, budget_receipt=admitted.receipt,
                    attempt_state=outcome.state if outcome.state not in
                        {"CompletedSettled", "CompletedPendingSettlement"} else None)
            answer = checked["answer"]
            content = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
            try:
                content.encode("utf-8")
            except UnicodeEncodeError:
                raise PfpTurnRefusal({**checked, "schema_valid": False,
                    "failure_class": "INVALID_UTF8", "reason": "INVALID_ANSWER_UNICODE"}) from None
            record.update(ok=True, content=content)
            self._observe_action(record, attempt_id)
            return LlmReply(content=content, input_tokens=candidate.input_tokens,
                output_tokens=candidate.output_tokens, model=candidate.model,
                cost_usd=candidate.cost_usd,
                raw_response=dict(decode_reply(outcome.reply_bytes)),
                authority_effect="None", reserved_microusd=record["reserved_microusd"],
                estimated_microusd=record["estimated_microusd"])
        except BaseException as exc:
            record["error"] = record["error"] or getattr(exc, "code", type(exc).__name__)
            self._observe_action(record, attempt_id)
            if not record["attempted"] and record["custody_error"] is None:
                record["cost_usd"] = 0.0
            raise

    def learn(self, rows):
        """Candidate facts commit only through the source/residual checker."""
        from .residual_memory import MemoryResult
        if self._memory is None:
            return MemoryResult(code="MEMORY_NOT_CONFIGURED")
        return self._memory.learn(rows)
