"""Pure controllers. No fixture, oracle, filesystem, or task-ID lookup access.

A checks local shape only. B is the complete conventional contract checker.
C uses the same complete contract and adds replayed LGGR certificates. Equal
actions are a preregistered possible result, not a reason to weaken B.
"""
from __future__ import annotations
from copy import deepcopy
from .common import digest

def development_evidence(development: dict | None) -> dict | None:
    """Only allowed labelled reports/certificates cross the controller boundary."""
    if development is None:
        return None
    return {key:deepcopy(development[key]) for key in ("rows","certificate","refined_rows")}

def conventional_findings(view: dict) -> list[dict]:
    findings = []
    def add(code, status, detail):
        findings.append({"code":code,"status":status,"detail":detail})
    c, obs = view["contract"], view["observations"]
    path = view["state_path"]
    if any(type(x) is not int for x in path):
        add("MALFORMED_STATE","malformed","states require exact integer observations")
        return findings
    if any(abs(b-a)>c.get("max_step",2) for a,b in zip(path,path[1:])):
        add("LOCAL_STEP_BREACH","obstructed","observed transition exceeds declared local bound")
    if any(x < -100 or x > 100 for x in path):
        add("UNSUPPORTED_STATE_DOMAIN","unsupported","arithmetic adapter domain is [-100,100]")
    base, bound = c.get("baseline",0), c.get("max_total",1)
    if c["query_scope"] == "every_prefix" and any(abs(x-base)>bound for x in path):
        add("PREFIX_BREACH","obstructed","declared every-prefix state bound failed")
    if view.get("terminal") and abs(path[-1]-base)>bound:
        add("ENDPOINT_BREACH","obstructed","terminal state bound failed")
    if view.get("event_error"):
        add("EVENT_INTEGRITY","malformed",view["event_error"])
    if view.get("missing_branches"):
        add("MISSING_WITNESS","unknown",view["missing_branches"])
    transition = view.get("transition",{"kind":"none"})
    if transition.get("kind","none") != "none":
        migration = obs.get("migration")
        if migration is None:
            add("MIGRATION_EVIDENCE","unknown","transition requires admitted registry evidence")
        elif not migration["validated"]:
            add("UNSUPPORTED_TRANSITION","unsupported",transition)
    for oid in view.get("obligations",[]):
        add("OPEN_OBLIGATION","unknown",oid)
    for sample in view.get("global_samples",[]):
        if sample["query_id"] in c.get("required_auxiliary_queries",[]) and sample["verdict"] is False:
            add("AUXILIARY_NEGATIVE","obstructed",sample)
    if view.get("unsupported_samples"):
        add("UNSUPPORTED_SAMPLE_SCOPE","unsupported",view["unsupported_samples"])
    for probe in c.get("required_evidence_probes",["semantics","branch_evidence"]):
        if probe == "branch_evidence" and not view.get("branches_executed"):
            continue
        if probe not in obs:
            add("MISSING_EVIDENCE","unknown",probe)
    if "branch_evidence" in obs:
        evidence = obs["branch_evidence"]
        for branch, target in (("orders","orders"),("refunds","refunds")):
            b = evidence["branches"].get(branch)
            s = evidence["source_counts"][target]
            if b and (b["rows"] != s["rows"] or b["unique_ids"] != s["unique_ids"] or b["negative_amounts"]):
                add("BRANCH_INVARIANT","obstructed",branch)
    if view.get("branches_executed") and "semantics" in obs:
        sem, plan = obs["semantics"], view["plan"]
        comparisons = (("orders", "scale_to_cents",sem["order_scale_to_cents"]),
                       ("refunds","scale_to_cents",sem["refund_scale_to_cents"]),
                       ("refunds","sign",sem["refund_sign"]),
                       ("integrator","refund_multiplier",1))
        for branch,key,expected in comparisons:
            if plan[branch].get(key) != expected:
                add("SEMANTIC_OPERATION_MISMATCH","obstructed",{"branch":branch,"field":key,"expected":expected,"observed":plan[branch].get(key)})
    return findings

def decide(view: dict, mode: str, development: dict | None = None) -> dict:
    if mode not in ("A","B","C"):
        raise ValueError("mode must be A, B or C")
    if mode == "A":
        return {"action":"proceed","reason":"local-schema-only ablation","findings":[],"certificates":[]}
    findings = conventional_findings(view)
    certificates = []
    if mode == "C":
        from .lggr_adapter import certify
        certificates = certify(view, development)
        # Runtime consumer of a verified certificate, before the ordinary
        # missing-evidence fallback. It requests an observation; it does NOT
        # treat the development collision as failure of the current input.
        for entry in certificates:
            cert = entry["certificate"]
            if (entry["kind"] == "development-fiber" and cert["status"] == "REPORT_INSUFFICIENT"
                    and "semantics" not in view["observations"]
                    and not any(f["status"] in ("obstructed","malformed","unsupported") for f in findings)):
                pair = cert["collision"]
                if view["initial_report"] == pair["left"]["report"]:
                    if "semantics" not in view["allowed_probes"]:
                        return {"action":"defer","reason":"certified ambiguous report; resolving probe unavailable",
                                "findings":findings,"certificates":certificates,"certificate_consumed":True}
                    if "semantics" not in view.get("exhausted_probes",[]):
                        return {"action":"probe","probe":"semantics","reason":"certified collision triggers unit/sign observation",
                                "findings":findings,"certificates":certificates,"certificate_consumed":True}
            if entry["kind"] == "state-budget" and (view["terminal"] or view["contract"]["query_scope"] == "every_prefix"):
                arithmetic = cert.get("arithmetic",{})
                if arithmetic.get("global_verdict") is False:
                    return {"action":"block","reason":"LGGR exact declared-scope budget certificate",
                            "findings":findings,"certificates":certificates,"certificate_consumed":True}
    decisive = [f for f in findings if f["status"] in ("obstructed","malformed","unsupported")]
    if decisive:
        return {"action":"block","reason":decisive[0]["code"],"findings":findings,"certificates":certificates}
    needed = []
    if view.get("transition",{}).get("kind","none") != "none" and "migration" not in view["observations"]:
        needed.append("migration")
    if view.get("obligations") and "obligation_evidence" not in view["observations"]:
        needed.append("obligation_evidence")
    needed += [f["detail"] for f in findings if f["code"] == "MISSING_EVIDENCE"]
    for name in needed:
        if name not in view["allowed_probes"]:
            return {"action":"defer","reason":f"unavailable resolving observation: {name}","findings":findings,"certificates":certificates}
        if name not in view.get("exhausted_probes",[]):
            reason = "complete-contract evidence requirement"
            if mode == "C" and name == "semantics" and development:
                reason = "verified development collision; request named lost unit/sign distinctions"
            return {"action":"probe","probe":name,"reason":reason,"findings":findings,"certificates":certificates}
    if findings:
        return {"action":"defer","reason":"residual unresolved evidence or obligation","findings":findings,"certificates":certificates}
    if not view.get("branches_executed"):
        plan = deepcopy(view["plan"])
        sem = view["observations"]["semantics"]
        plan["orders"].update(scale_to_cents=sem["order_scale_to_cents"],join_mode="first",omit_last=False)
        plan["refunds"].update(scale_to_cents=sem["refund_scale_to_cents"],sign=sem["refund_sign"],omit_last=False,duplicate=False)
        plan["integrator"].update(refund_multiplier=1)
        if plan != view["plan"]:
            return {"action":"repair_plan","plan":plan,"reason":"observed metadata and declared reconciliation contract","findings":[],"certificates":certificates}
    return {"action":"proceed","reason":"complete declared contract evidence available","findings":[],"certificates":certificates}

def decision_fingerprint(decision: dict) -> str:
    return digest(decision)
