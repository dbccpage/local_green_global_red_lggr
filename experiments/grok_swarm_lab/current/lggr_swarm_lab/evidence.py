"""Application envelope, evidence-preserving union, and replay checks.

Application status names are not LGGR API status names. Hashes bind bytes;
the host is trusted to collect observations. No producer authentication follows.
"""
from __future__ import annotations
from .requirements import requirements, matches
from copy import deepcopy
from .common import canonical, digest

STATUSES = ("verified-on-declared-domain", "observed-so-far", "unknown",
            "obstructed", "malformed", "unsupported")

class EvidenceError(ValueError):
    pass

class EvidenceBook:
    def __init__(self, contract: dict):
        self.contract = deepcopy(contract)
        self.events: dict[str, dict] = {}

    def merge(self, events: list[dict]) -> dict:
        """Validate a complete causal union before committing any of it.

        Evidence originates in the laboratory host's trusted tool boundary.
        Structural checks and hashes do not authenticate an outside producer.
        Samples keep their original proposition, including unknown verdicts.
        """
        proposed = deepcopy(self.events)
        for event in events:
            if not isinstance(event, dict) or not isinstance(event.get("payload"), dict):
                raise EvidenceError("malformed branch event")
            if not isinstance(event.get("event_id"), str) or not event["event_id"]:
                raise EvidenceError("malformed event identity")
            parents = event.get("parent_ids")
            if (not isinstance(parents, list) or
                    any(not isinstance(p, str) or not p for p in parents) or
                    len(set(parents)) != len(parents)):
                raise EvidenceError("malformed causal parents")
            eid = event["event_id"]
            if digest(event["payload"]) != event.get("payload_hash"):
                raise EvidenceError("altered branch artifact")
            if event.get("policy_version") != self.contract.get("policy_version", "policy.v1"):
                raise EvidenceError("changed policy needs explicit host admission")
            if eid in proposed and canonical(proposed[eid]) != canonical(event):
                raise EvidenceError("conflicting replay of an event identity")
            proposed[eid] = deepcopy(event)
        # Delivery order is not causal order. Missing parents remain unknown.
        ordered, remaining = [], dict(proposed)
        while remaining:
            ready = sorted(k for k, v in remaining.items()
                           if all(p in {x["event_id"] for x in ordered} for p in v["parent_ids"]))
            if not ready:
                raise EvidenceError("missing causal parent or causal cycle")
            for key in ready:
                ordered.append(remaining.pop(key))
        obligations, samples, attempts = set(), [], {}
        for event in ordered:
            payload = event["payload"]
            for name in ("obligations", "discharges", "global_samples", "attempts"):
                if not isinstance(payload.get(name, []), list):
                    raise EvidenceError(f"malformed {name}")
            for oid in payload.get("obligations", []):
                if not isinstance(oid, str) or not oid:
                    raise EvidenceError("malformed obligation identity")
                obligations.add(oid)
            for discharge in payload.get("discharges", []):
                if not isinstance(discharge, dict) or not isinstance(discharge.get("id"), str) or not discharge["id"]:
                    raise EvidenceError("malformed obligation discharge")
                evidence = discharge.get("evidence")
                if (not isinstance(evidence, dict) or
                        evidence.get("source") != "sqlite.obligation_evidence" or
                        evidence.get("verified") is not True):
                    raise EvidenceError("discharge lacks checked tool evidence")
                obligations.discard(discharge["id"])
            for sample in payload.get("global_samples", []):
                if (not isinstance(sample, dict) or
                        not isinstance(sample.get("query_id"), str) or not sample["query_id"] or
                        "baseline" not in sample or
                        sample.get("scope") not in ("endpoint", "every_prefix") or
                        "verdict" not in sample or
                        (sample["verdict"] is not None and type(sample["verdict"]) is not bool) or
                        not isinstance(sample.get("source"), str) or not sample["source"]):
                    raise EvidenceError("malformed global sample")
                samples.append(sample)
            for attempt in payload.get("attempts", []):
                if (not isinstance(attempt, dict) or
                        not isinstance(attempt.get("attempt_id"), str) or not attempt["attempt_id"] or
                        type(attempt.get("cost")) is not int or attempt["cost"] != 1 or
                        ("issued" in attempt and attempt["issued"] is not True)):
                    raise EvidenceError("each issued laboratory attempt has integer cost one")
                key = attempt["attempt_id"]
                if key in attempts and attempts[key] != attempt:
                    raise EvidenceError("conflicting cost attribution")
                attempts[key] = attempt

        try:
            declarations = requirements(self.contract)
        except ValueError as error:
            raise EvidenceError(str(error)) from error
        if self.contract.get("query_id"):
            declarations.append({"query_id": self.contract["query_id"],
                                 "scope": self.contract.get("query_scope"),
                                 **({"baseline": self.contract["baseline"]} if "baseline" in self.contract else {})})
        groups = {}
        for sample in samples:
            identity = {k: sample[k] for k in ("query_id", "baseline", "scope")}
            key = canonical(identity)
            if key not in groups:
                supported = any(matches(declaration, sample) for declaration in declarations)
                groups[key] = {**identity, "supported": supported, "samples": []}
            groups[key]["samples"].append(sample)
        scope_groups = [groups[key] for key in sorted(groups)]
        self.events = deepcopy(proposed)
        return {"ordered": ordered, "obligations": sorted(obligations),
                "global_samples": samples, "cost": sum(a["cost"] for a in attempts.values()),
                "unique_attempts": list(attempts.values()),
                "scope_groups": scope_groups,
                "mixed_scope": len(scope_groups) > 1,
                "unsupported": any(not group["supported"] for group in scope_groups),
                "deduplication_rule": "identical event/attempt ID once; conflicting reuse rejected"}

def branch_event(event_id: str, payload: dict, *, parents=(), policy_version="policy.v1", role="worker") -> dict:
    return {"event_id": event_id, "parent_ids": list(parents), "payload": payload,
            "payload_hash": digest(payload), "policy_version": policy_version, "role": role}

def verify_chain(run: dict) -> None:
    if digest(run["input"]) != run["input_sha256"]:
        raise EvidenceError("input hash mismatch")
    previous = "0" * 64
    seen = set()
    for seq, event in enumerate(run["events"]):
        data = {k:v for k,v in event.items() if k != "event_sha256"}
        if event["seq"] != seq or event["previous_sha256"] != previous:
            raise EvidenceError("event sequence/chain changed")
        if event["event_id"] in seen:
            raise EvidenceError("repeated event identity in sequential receipt")
        if not all(parent in seen for parent in event["causal_parents"]):
            raise EvidenceError("missing causal input")
        if digest(data) != event["event_sha256"]:
            raise EvidenceError("event bytes changed")
        previous = event["event_sha256"]
        seen.add(event["event_id"])
    for key, artifact in run["artifacts"].items():
        if digest(artifact["data"]) != artifact["sha256"]:
            raise EvidenceError(f"artifact hash mismatch: {key}")
    for event in run["events"]:
        for ref in event["input_artifacts"] + event["output_artifacts"]:
            if ref["id"] not in run["artifacts"] or run["artifacts"][ref["id"]]["sha256"] != ref["sha256"]:
                raise EvidenceError("event references altered/missing artifact")
