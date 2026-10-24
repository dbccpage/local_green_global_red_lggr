"""Dict-event facade over the stdlib LGGR monitors.

A harness in another language can follow learn/HARNESS_CONTRACT.md and compare
its receipts with this reference. The adapter calls the existing monitors. It
does not call a model, admit an authority, or clear an obligation.

AuthorityEffect: None.
"""
from __future__ import annotations

from typing import Any

from lggr import (
    BudgetPolicy,
    StateRef,
    StreamingAuditMonitor,
    StreamingCochainMonitor,
    StreamingFiberMonitor,
    StreamingRSIFiberCeilingMonitor,
    make_witness,
)
from lggr.common import ValidationError, canonical, exact_int, fields, json_value, text

LESSON_SCHEMA = "learn.harness_event.v1"

_REQUIRED = {
    "scope_id",
    "query_scope",
    "bound",
    "global_sample_source",
    "authority_id",
    "evaluator_id",
    "policy_id",
}
_OPTIONAL = {"spec_id", "representation_id", "allowed_states", "max_step"}


def envelope(status: str, monitor_receipt: dict[str, Any] | None, **extra: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "lesson_schema": LESSON_SCHEMA,
        "authority_effect": "None",
        "status": status,
        "monitor_receipt": monitor_receipt,
    }
    body.update(extra)
    return json_value(body)


def _rejected(reason: str) -> dict[str, Any]:
    return envelope(
        "GLOBAL_SAMPLE_REJECTED",
        None,
        reason=reason,
        meaning="The global sample must come from outside the proposing stage.",
    )


class RunGuard:
    """One declared run. Methods accept the event dicts from the contract."""

    def __init__(self, declaration: dict[str, Any], rejection: dict[str, Any] | None, policy: BudgetPolicy | None):
        self.declaration = declaration
        self.rejection = rejection
        self.policy = policy
        self.fiber: StreamingFiberMonitor | None = None
        self.audit: StreamingAuditMonitor | None = None
        self.cochain: StreamingCochainMonitor | None = None
        self.rsi: StreamingRSIFiberCeilingMonitor | None = None
        self._coarse_predictions: dict[str, Any] = {}
        self._refined_predictions: dict[str, Any] = {}

    def _gate(self, event: dict[str, Any]) -> dict[str, Any] | None:
        if self.rejection is not None:
            return self.rejection
        source = event.get("global_sample_source", self.declaration["global_sample_source"])
        if source != "external":
            return _rejected("global_sample_source must be external")
        return None

    def handoff(self, event: dict[str, Any]) -> dict[str, Any]:
        gated = self._gate(event)
        if gated is not None:
            return gated
        fields(event, {"state_id", "report", "query"}, {"global_sample_source", "metadata"})
        if self.fiber is None:
            self.fiber = StreamingFiberMonitor(scope_id=self.declaration["scope_id"])
        metadata = event.get("metadata")
        receipt = self.fiber.observe(event["state_id"], event["report"], event["query"], metadata=metadata)
        return envelope(receipt["status"], receipt)

    def step(self, event: dict[str, Any]) -> dict[str, Any]:
        gated = self._gate(event)
        if gated is not None:
            return gated
        if self.policy is None:
            raise ValidationError("A bound declaration is required")
        fields(
            event,
            {"before", "after"},
            {"signed_delta", "global_sample", "global_sample_source", "obligations", "witness_id", "step_cost"},
        )
        before = StateRef.from_dict(event["before"])
        after = StateRef.from_dict(event["after"])
        if before.value is None or after.value is None:
            return envelope("WITNESS_INCOMPLETE", None, missing=["endpoint value"])
        if "signed_delta" in event and event["signed_delta"] != after.value - before.value:
            return envelope(
                "SIGNED_DELTA_MISMATCH",
                None,
                meaning="The declared signed_delta does not match the supplied endpoints.",
            )
        if self.audit is None:
            self.audit = StreamingAuditMonitor(self.policy, before)
        witness_id = event.get("witness_id") or f"w{len(self.audit.steps) + 1:03d}"
        obligations = tuple(event.get("obligations", ()))
        witness = make_witness(self.policy, before, after, witness_id=witness_id, obligations=obligations)
        sample = event.get("global_sample")
        step_cost = event.get("step_cost", 0)
        receipt = self.audit.step(witness, global_evaluator_sample=sample, step_cost=step_cost)
        return envelope(receipt["status"], receipt)

    def review_edge(self, event: dict[str, Any]) -> dict[str, Any]:
        gated = self._gate(event)
        if gated is not None:
            return gated
        fields(event, {"src", "dst", "value"}, {"weight", "global_sample_source"})
        if self.cochain is None:
            self.cochain = StreamingCochainMonitor()
        weight = event.get("weight", 1)
        receipt = self.cochain.add_edge(event["src"], event["dst"], event["value"], weight)
        return envelope(receipt["status"], json_value(receipt))

    def generation(self, event: dict[str, Any]) -> dict[str, Any]:
        """Record one state. When ``evaluate`` is true, score the stored predictions."""
        gated = self._gate(event)
        if gated is not None:
            return gated
        fields(
            event,
            {"state_id", "coarse_report", "target"},
            {"refined_report", "prediction", "use_refined_report", "evaluate", "generation_id", "global_sample_source"},
        )
        if self.rsi is None:
            self.rsi = StreamingRSIFiberCeilingMonitor(scope_id=self.declaration["scope_id"])
        refined = event.get("refined_report")
        recorded = self.rsi.observe_state(
            event["state_id"], event["coarse_report"], event["target"], refined_report=refined,
        )
        if "prediction" in event:
            use_refined_pred = bool(event.get("use_refined_report"))
            bucket = self._refined_predictions if use_refined_pred else self._coarse_predictions
            subject = refined if use_refined_pred else event["coarse_report"]
            # The monitor looks up the canonical report string.
            bucket[canonical(subject)] = event["prediction"]
        if not event.get("evaluate"):
            return envelope(recorded["status"], recorded)
        use_refined = bool(event.get("use_refined_report"))
        predictor = dict(self._refined_predictions if use_refined else self._coarse_predictions)
        generation_id = event.get("generation_id") or f"g{len(self.rsi.generations)}"
        scored = self.rsi.evaluate_generation(generation_id, predictor, use_refined_report=use_refined)
        return envelope(scored["status"], scored)

    def summary(self) -> dict[str, Any]:
        gated = self._gate({})
        if gated is not None:
            return gated
        if self.audit is None:
            return envelope("WITNESS_INCOMPLETE", None, missing=["steps"])
        receipt = self.audit.get_receipt()
        return envelope(receipt["status"], receipt)


def bind(declaration: dict[str, Any]) -> RunGuard:
    """Bind a run declaration. A non-external global sample never reaches a monitor."""
    fields(declaration, _REQUIRED, _OPTIONAL)
    text(declaration["scope_id"], "scope_id")
    text(declaration["authority_id"], "authority_id")
    text(declaration["evaluator_id"], "evaluator_id")
    text(declaration["policy_id"], "policy_id")
    text(declaration["global_sample_source"], "global_sample_source")
    if declaration["query_scope"] not in ("endpoint", "every_prefix"):
        raise ValidationError("query_scope must be endpoint or every_prefix")
    exact_int(declaration["bound"], "bound", minimum=0)
    if declaration["global_sample_source"] != "external":
        return RunGuard(json_value(declaration), _rejected("global_sample_source must be external"), None)
    allowed = declaration.get("allowed_states", [0, 1, 2])
    policy = BudgetPolicy(
        policy_id=declaration["policy_id"],
        spec_id=declaration.get("spec_id", "learn-harness/v1"),
        evaluator_id=declaration["evaluator_id"],
        representation_id=declaration.get("representation_id", "learn-declared/v1"),
        authority_id=declaration["authority_id"],
        allowed_states=tuple(allowed),
        max_step=declaration.get("max_step", 1),
        max_total=declaration["bound"],
        query_scope=declaration["query_scope"],
    )
    return RunGuard(json_value(declaration), None, policy)


def wire_tool_loop(declaration: dict[str, Any], steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sequential tool loop: one baseline, then each signed step."""
    guard = bind(declaration)
    receipts = []
    for index, step in enumerate(steps, start=1):
        event = dict(step)
        event.setdefault("witness_id", f"w{index:03d}")
        receipts.append(guard.step(event))
    if guard.rejection is None and guard.audit is not None:
        receipts.append(guard.summary())
    return receipts


def wire_handoff(declaration: dict[str, Any], handoffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Specifier-to-implementer handoffs. The query stays off the report until declared."""
    guard = bind(declaration)
    return [guard.handoff(event) for event in handoffs]


def wire_review_cycle(declaration: dict[str, Any], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Directed review edges. A closing edge carries the cycle defect when one exists."""
    guard = bind(declaration)
    return [guard.review_edge(event) for event in edges]
