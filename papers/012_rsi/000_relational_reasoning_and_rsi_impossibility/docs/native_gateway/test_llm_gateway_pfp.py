"""Plain-prompt LlmGateway uses actual bound PFP replies and one run allowance."""

import json
from dataclasses import FrozenInstanceError, fields

import pytest

from omega_engine_pfp.tests.test_pilot_matrix_pfp import make_gateway
from omega_engine_woland.infrastructure.providers.llm_gateway import LlmGateway, LlmReply
from omega_engine_pfp.infrastructure.task_turn import PfpTurnRefusal
from omega_engine_woland.domain.providers.budget import BudgetController
from omega_engine_woland.domain.providers.types import ProviderConfigError, ProviderError


def test_plain_facade_requires_accounted_bound_reply(tmp_path):
    gateway, provider = make_gateway(tmp_path, answer="actual inner answer")
    facade = LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256)
    reply = facade.complete("Solve the public task.", "public input")
    assert reply.content == "actual inner answer"
    assert reply.cost_usd == 0.000001 and reply.input_tokens == 12 and reply.output_tokens == 8
    assert reply.raw_response == json.loads(provider.raw)
    assert json.loads(provider.calls[0].user)["input"]["prompt"] == "public input"
    assert reply.reserved_microusd is None and reply.estimated_microusd > 0
    assert reply.settled_microusd is None and reply.authority_effect == "None"
    assert facade.last_turn["pfp"]["evidence_grade"] == "UNVERIFIED"


@pytest.mark.parametrize("completion", ["not JSON",
    '{"task_id":"wrong","attempt_id":"wrong","input_sha256":"wrong","answer":"proposal"}'])
def test_malformed_or_wrong_binding_keeps_actual_wire_not_an_answer(tmp_path, completion):
    gateway, provider = make_gateway(tmp_path, raw_content=completion)
    facade = LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256)
    with pytest.raises(PfpTurnRefusal):
        facade.complete("public task", "input")
    import base64
    assert base64.b64decode(facade.last_turn["provider_wire"]["raw_reply_base64"]) == provider.raw
    assert not facade.last_turn["ok"] and facade.last_turn["content"] is None
    assert facade.last_turn["cost_usd"] == 0.000001 and len(provider.calls) == 1


def test_unknown_cost_stops_shared_gateway_without_fallback(tmp_path):
    gateway, provider = make_gateway(tmp_path, cost=None)
    facade = LlmGateway(fallback_models=("vendor/model", "vendor/other"), gateway=gateway, max_tokens=256)
    with pytest.raises(PfpTurnRefusal, match="CompletedCostUnknown"):
        facade.complete("task", "first")
    assert facade.last_turn["cost_usd"] is None and facade.last_turn["attempted"]
    assert facade.last_turn["provider_wire"]
    with pytest.raises(ProviderError, match="UNRECONCILED_ATTEMPT"):
        facade.complete("task", "second")
    assert len(provider.calls) == 1 and facade.model == "vendor/model"


def test_two_facades_and_restart_share_one_call_allowance(tmp_path):
    gateway, provider = make_gateway(tmp_path, answer="actual", max_calls=1)
    first = LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256)
    second = LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256)
    assert first.complete("task", "first").content == "actual"
    with pytest.raises(ProviderError, match="CALL_ALLOWANCE_EXHAUSTED"):
        second.complete("task", "second")
    assert second.last_turn["cost_usd"] == 0.0 and not second.last_turn["attempted"]
    reopened, new_provider = make_gateway(tmp_path, answer="actual", max_calls=1)
    with pytest.raises(ProviderError, match="CALL_ALLOWANCE_EXHAUSTED"):
        LlmGateway(model="vendor/model", gateway=reopened, max_tokens=256).complete("task", "restart")
    assert len(provider.calls) == 1 and not new_provider.calls


def test_model_override_and_output_bound_refuse_before_send(tmp_path):
    gateway, provider = make_gateway(tmp_path)
    facade = LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256)
    with pytest.raises(ValueError, match="PRICING_MODEL_MISMATCH"):
        facade.complete("task", "input", model_override="vendor/other")
    with pytest.raises(ValueError, match="PFP_OUTPUT_BOUND_MISMATCH"):
        LlmGateway(model="vendor/model", gateway=gateway, max_tokens=512).complete("task", "input")
    assert not provider.calls


def test_key_only_bare_gateway_and_conflicting_budget_never_dispatch(tmp_path, monkeypatch):
    from omega_engine_woland.infrastructure.providers import llm_gateway as module
    monkeypatch.setattr(module, "resolve_openrouter_api_key", lambda *a: pytest.fail("resolved credentials"))
    facade = LlmGateway(model="vendor/model", api_key="synthetic-unused")
    with pytest.raises(ProviderConfigError, match="PFP_ACCOUNTED_GATEWAY_REQUIRED"):
        facade.complete("task", "input")
    gateway, provider = make_gateway(tmp_path)
    with pytest.raises(ProviderConfigError, match="PFP_ACCOUNTED_GATEWAY_REQUIRED"):
        LlmGateway(model="vendor/model", gateway=gateway.gateway)
    with pytest.raises(ProviderConfigError, match="PFP_LEGACY_BUDGET_CONFLICT"):
        LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256,
            budget_controller=BudgetController(1)).complete("task", "input")
    assert not provider.calls


def test_hard_pending_completion_preserves_admission_fields_and_model_override(tmp_path):
    from omega_engine_pfp.tests.test_durable_run_budget import bind, SyntheticTransport, MODEL, OTHER_MODEL
    class BoundTransport(SyntheticTransport):
        def dispatch(self, admitted):
            self.calls.append(admitted)
            task = json.loads(admitted.request.user)
            answer = {key: task[key] for key in ("task_id", "attempt_id", "input_sha256")}
            answer["answer"] = "actual bound answer"
            return json.dumps(dict(id="generation-" + admitted.attempt_id, model=admitted.model,
                usage=dict(prompt_tokens=8, completion_tokens=4, cost="0.001"),
                choices=[dict(message=dict(content=json.dumps(answer)))])).encode()
    gateway, transport = bind(tmp_path, BoundTransport(), max_calls=2)
    facade = LlmGateway(model=MODEL, gateway=gateway, max_tokens=20)
    reply = facade.complete("public task", "input", model_override=OTHER_MODEL)
    assert reply.model == OTHER_MODEL and reply.content == "actual bound answer"
    assert reply.reserved_microusd == 10000 and reply.estimated_microusd > 0
    assert reply.settled_microusd is None and reply.cost_usd == 0.001
    assert facade.last_turn["attempt_state"] == "CompletedPendingSettlement"
    assert len(transport.calls) == 1 and transport.calls[0].max_output_tokens == 20


def test_llm_reply_exact_frozen_fields_equality_and_hash_remain():
    assert [field.name for field in fields(LlmReply)] == ["content", "input_tokens", "output_tokens",
        "model", "cost_usd", "raw_response", "authority_effect", "reserved_microusd",
        "estimated_microusd", "settled_microusd"]
    first = LlmReply("actual", 1, 2, "model", None, {"exact": "wire"})
    same = LlmReply("actual", 1, 2, "model", None, {"exact": "wire"})
    assert first == same and hash(first) == hash(same)
    with pytest.raises(FrozenInstanceError):
        first.content = "changed"
    class Child(LlmReply):
        pass
    assert first != Child("actual", 1, 2, "model", None, {"exact": "wire"})
