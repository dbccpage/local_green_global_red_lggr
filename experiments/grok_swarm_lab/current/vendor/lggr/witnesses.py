"""Scoped witness composition for the report's finite cumulative-budget model.

All checks refer to supplied state evidence. This module cannot observe a
running application, authenticate an owner, or authorize a merge.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .common import ValidationError, boolean, digest, exact_int, fields, json_value, sequence, text


@dataclass(frozen=True)
class BudgetPolicy:
    policy_id: str = "budget-policy/v1"
    spec_id: str = "cumulative-budget/v1"
    evaluator_id: str = "bounded-step/v1"
    representation_id: str = "integer-state/v1"
    authority_id: str = "external-owner/v1"
    allowed_states: tuple[int, ...] = (0, 1, 2)
    max_step: int = 1
    max_total: int = 1
    query_scope: str = "endpoint"

    def __post_init__(self) -> None:
        for name in ("policy_id", "spec_id", "evaluator_id", "representation_id", "authority_id"):
            text(getattr(self, name), name)
        states = tuple(sequence(self.allowed_states, "allowed_states"))
        for state in states:
            exact_int(state, "allowed state")
        if not states or len(set(states)) != len(states):
            raise ValidationError("allowed_states must be nonempty and have no duplicates")
        object.__setattr__(self, "allowed_states", states)
        exact_int(self.max_step, "max_step", minimum=0)
        exact_int(self.max_total, "max_total", minimum=0)
        if self.query_scope not in ("endpoint", "every_prefix"):
            raise ValidationError("query_scope must be endpoint or every_prefix")

    @property
    def sha256(self) -> str:
        return digest(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BudgetPolicy:
        fields(data, set(cls.__dataclass_fields__))
        return cls(**data)


@dataclass(frozen=True)
class StateRef:
    state_id: str
    value: int | None

    def __post_init__(self) -> None:
        text(self.state_id, "state_id")
        if self.value is not None:
            exact_int(self.value, "state value")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StateRef:
        fields(data, {"state_id", "value"})
        return cls(**data)


@dataclass(frozen=True)
class StepWitness:
    witness_id: str
    source: StateRef
    target: StateRef
    policy_sha256: str
    evaluator_id: str
    spec_id: str
    representation_id: str
    authority_id: str
    observed_magnitude: int | None
    local_accepted: bool
    smoke_passed: bool
    obligations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("witness_id", "evaluator_id", "spec_id", "representation_id", "authority_id"):
            text(getattr(self, name), name)
        if (type(self.policy_sha256) is not str or len(self.policy_sha256) != 64 or
                any(c not in "0123456789abcdef" for c in self.policy_sha256)):
            raise ValidationError("policy_sha256 must be a lowercase SHA-256 hex digest")
        if not isinstance(self.source, StateRef) or not isinstance(self.target, StateRef):
            raise ValidationError("source and target must be StateRef objects")
        if self.observed_magnitude is not None:
            exact_int(self.observed_magnitude, "observed_magnitude", minimum=0)
        boolean(self.local_accepted, "local_accepted")
        boolean(self.smoke_passed, "smoke_passed")
        obligations = tuple(sequence(self.obligations, "obligations"))
        for obligation in obligations:
            text(obligation, "obligation")
        object.__setattr__(self, "obligations", obligations)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StepWitness:
        names = set(cls.__dataclass_fields__)
        fields(data, names - {"obligations"}, {"obligations"})
        values = dict(data)
        values["source"] = StateRef.from_dict(values["source"])
        values["target"] = StateRef.from_dict(values["target"])
        return cls(**values)


def local_accepts(policy: BudgetPolicy, old: int, new: int) -> bool:
    exact_int(old, "old")
    exact_int(new, "new")
    return old in policy.allowed_states and new in policy.allowed_states and abs(new - old) <= policy.max_step


def make_witness(policy: BudgetPolicy, source: StateRef, target: StateRef,
                 *, witness_id: str, obligations: tuple[str, ...] = ()) -> StepWitness:
    """Construct evidence using the declared finite model, not an LLM opinion."""
    if source.value is None or target.value is None:
        raise ValidationError("make_witness requires observed endpoints")
    return StepWitness(witness_id, source, target, policy.sha256, policy.evaluator_id,
                       policy.spec_id, policy.representation_id, policy.authority_id,
                       abs(target.value - source.value),
                       local_accepts(policy, source.value, target.value),
                       target.value in policy.allowed_states, obligations)


def audit_history(policy: BudgetPolicy, baseline: StateRef, witnesses: Iterable[StepWitness],
                  *, prior_obligations: tuple[str, ...] = ()) -> dict[str, Any]:
    """Replay local evidence and the protected cumulative query.

    An endpoint violation, a missing witness and an unauthorized semantic
    change are separate findings. A conservative primary status does not
    discard other findings. Obligations are unioned across the entire supplied
    trace and prior receipt; this API has no self-authorized clearing operation.
    """
    if not isinstance(policy, BudgetPolicy) or not isinstance(baseline, StateRef):
        raise ValidationError("policy and baseline have incorrect types")
    steps = tuple(witnesses)
    if any(not isinstance(w, StepWitness) for w in steps):
        raise ValidationError("Every witness must be a StepWitness")
    prior_obligations = tuple(sequence(prior_obligations, "prior_obligations"))
    for item in prior_obligations:
        text(item, "prior obligation")

    findings: list[dict[str, Any]] = []
    obligations = set(prior_obligations)

    def add(kind: str, code: str, message: str, witness_id: str | None = None,
            **evidence: Any) -> None:
        findings.append({"kind": kind, "code": code, "message": message,
                         "witness_id": witness_id, "evidence": evidence})

    state_values: dict[str, int] = {}
    structurally_valid = True
    for state in (baseline, *(s for w in steps for s in (w.source, w.target))):
        if state.value is not None:
            previous = state_values.get(state.state_id)
            if previous is not None and previous != state.value:
                structurally_valid = False
                add("INVALID_WITNESS", "CONFLICTING_STATE", "One state identity has conflicting values.",
                    state_id=state.state_id, values=[previous, state.value])
            state_values[state.state_id] = state.value
    witness_ids: set[str] = set()
    expected_source = baseline.state_id
    same_representation = True
    local_checks: list[dict[str, Any]] = []
    for step in steps:
        wid = step.witness_id
        obligations.update(step.obligations)
        if wid in witness_ids:
            structurally_valid = False
            add("INVALID_WITNESS", "DUPLICATE_WITNESS", "Witness identities must be unique.", wid)
        witness_ids.add(wid)
        if step.source.state_id != expected_source:
            structurally_valid = False
            add("INVALID_WITNESS", "BOUNDARY_MISMATCH", "Adjacent witness endpoints do not match.", wid,
                expected=expected_source, actual=step.source.state_id)
        expected_source = step.target.state_id
        if step.policy_sha256 != policy.sha256:
            add("AUTHORITY_REQUIRED", "POLICY_MANIFEST_CHANGED", "Policy contents are not the protected manifest.", wid)
        for name in ("evaluator_id", "spec_id", "authority_id"):
            if getattr(step, name) != getattr(policy, name):
                add("AUTHORITY_REQUIRED", "SEMANTIC_SCOPE_CHANGED",
                    "A changed evaluator, specification or authority needs a separately admitted transition.", wid,
                    field=name, expected=getattr(policy, name), actual=getattr(step, name))
        rep_ok = step.representation_id == policy.representation_id
        if not rep_ok:
            same_representation = False
            add("UNSUPPORTED", "REPRESENTATION_TRANSPORT_REQUIRED",
                "The budget adapter does not infer semantic transport from representation names.", wid)
        a, b = state_values.get(step.source.state_id), state_values.get(step.target.state_id)
        check: dict[str, Any] = {"witness_id": wid, "claimed_local_acceptance": step.local_accepted,
                                 "claimed_smoke_pass": step.smoke_passed,
                                 "protected_policy_acceptance": None, "signed_delta": None}
        if a is None or b is None:
            add("WITNESS_INCOMPLETE", "MISSING_ENDPOINT", "Pass reports do not establish signed endpoint changes.", wid)
        elif rep_ok:
            accepted = local_accepts(policy, a, b)
            smoke = b in policy.allowed_states
            check.update(protected_policy_acceptance=accepted, signed_delta=b - a,
                         protected_smoke_pass=smoke)
            if step.observed_magnitude is not None and step.observed_magnitude != abs(b - a):
                add("INVALID_WITNESS", "MAGNITUDE_MISMATCH", "Recorded magnitude contradicts the supplied endpoints.", wid)
            # A claim made under a different evaluator/spec is not silently
            # reinterpreted as a claim under the protected one.
            same_meaning = (step.evaluator_id == policy.evaluator_id and step.spec_id == policy.spec_id
                            and step.policy_sha256 == policy.sha256)
            if same_meaning and (step.local_accepted != accepted or step.smoke_passed != smoke):
                add("INVALID_WITNESS", "VERDICT_MISMATCH", "Claimed local verdict contradicts replay.", wid,
                    replay_local=accepted, replay_smoke=smoke)
            if not accepted or not smoke:
                add("LOCAL_REJECTED", "LOCAL_RULE_FAILED", "This step fails the protected local rule or smoke check.", wid)
        local_checks.append(check)

    if baseline.value is None:
        add("WITNESS_INCOMPLETE", "BASELINE_UNOBSERVED", "The protected baseline needs an observed value.")
    elif baseline.value not in policy.allowed_states:
        structurally_valid = False
        add("INVALID_WITNESS", "BASELINE_OUTSIDE_DOMAIN", "Baseline is outside the declared state domain.")

    arithmetic: dict[str, Any] | None = None
    values_complete = (baseline.value is not None and all(c["signed_delta"] is not None for c in local_checks))
    if structurally_valid and same_representation and values_complete:
        base = baseline.value
        # values_complete explicitly guarantees base is an integer.
        if base is None:
            raise RuntimeError("Internal baseline validation failure")
        deltas = [c["signed_delta"] for c in local_checks]
        total = sum(deltas)
        final = state_values[steps[-1].target.state_id] if steps else base
        if total != final - base:
            raise RuntimeError("Internal telescoping check failed")
        prefix_checks = []
        partial = 0
        for step, delta in zip(steps, deltas):
            partial += delta
            prefix_checks.append({"witness_id": step.witness_id, "signed_total": partial,
                                  "within_bound": abs(partial) <= policy.max_total})
        endpoint_ok = abs(total) <= policy.max_total
        prefixes_ok = all(p["within_bound"] for p in prefix_checks)
        global_ok = endpoint_ok if policy.query_scope == "endpoint" else prefixes_ok
        arithmetic = {"baseline": base, "final": final, "signed_deltas": deltas,
                      "signed_total": total, "bound": policy.max_total,
                      "endpoint_verdict": endpoint_ok, "every_prefix_verdict": prefixes_ok,
                      "query_scope": policy.query_scope, "global_verdict": global_ok,
                      "prefix_checks": prefix_checks}
        if not global_ok:
            add("OBSTRUCTION_DETECTED", "PROTECTED_QUERY_FALSE",
                "The supplied endpoint evidence falsifies the declared cumulative requirement.",
                query_scope=policy.query_scope, signed_total=total, bound=policy.max_total,
                violated_prefixes=[p for p in prefix_checks if not p["within_bound"]])

    if obligations:
        add("WITNESS_INCOMPLETE", "OPEN_OBLIGATIONS", "Unresolved obligations have been retained, not silently cleared.",
            obligations=sorted(obligations))
    priority = ["INVALID_WITNESS", "AUTHORITY_REQUIRED", "UNSUPPORTED", "LOCAL_REJECTED",
                "OBSTRUCTION_DETECTED", "WITNESS_INCOMPLETE"]
    kinds = {finding["kind"] for finding in findings}
    status = next((kind for kind in priority if kind in kinds), "COMPOSITION_VERIFIED")
    body = {"schema": "lggr.audit.v1", "authority_effect": "None", "status": status,
            "composition_certified": status == "COMPOSITION_VERIFIED", "policy_sha256": policy.sha256,
            "query_scope": policy.query_scope,
            "input_sha256": digest({"policy": policy, "baseline": baseline, "witnesses": steps,
                                    "prior_obligations": prior_obligations}),
            "local_checks": local_checks, "arithmetic": arithmetic, "findings": findings,
            "unresolved_obligations": sorted(obligations),
            "scope": "Supplied finite trace under the protected budget policy; not runtime or merge authorization."}
    return {**body, "receipt_sha256": digest(body)}


def audit_document(data: dict[str, Any]) -> dict[str, Any]:
    fields(data, {"policy", "baseline", "witnesses"}, {"prior_obligations"})
    return audit_history(BudgetPolicy.from_dict(data["policy"]), StateRef.from_dict(data["baseline"]),
                         [StepWitness.from_dict(w) for w in sequence(data["witnesses"], "witnesses")],
                         prior_obligations=tuple(sequence(data.get("prior_obligations", []), "prior_obligations")))


def history_document(values: Iterable[int], *, policy: BudgetPolicy | None = None) -> dict[str, Any]:
    """Convenience constructor for finite, observed examples."""
    policy = policy or BudgetPolicy()
    values = tuple(values)
    if not values:
        raise ValidationError("A history must include a baseline")
    states = [StateRef(f"s{i}", value) for i, value in enumerate(values)]
    witnesses = [make_witness(policy, a, b, witness_id=f"w{i:03d}")
                 for i, (a, b) in enumerate(zip(states, states[1:]), start=1)]
    return json_value({"policy": policy, "baseline": states[0], "witnesses": witnesses,
                       "prior_obligations": []})
