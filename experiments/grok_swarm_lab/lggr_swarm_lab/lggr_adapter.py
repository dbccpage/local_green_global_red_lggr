"""Thin use of the unchanged pinned dependency; safe narrower interfaces.

Never call its lossy merge. The host's immutable EvidenceBook owns merge,
costs, and scoped global samples. No sample label becomes current task truth.
"""
from __future__ import annotations
from lggr import analyze_descent, verify_descent_certificate, BudgetPolicy, StateRef, make_witness, audit_history

def certify(view: dict, development: dict | None) -> list[dict]:
    receipts = []
    if development:
        rows, cert = development["rows"], development["certificate"]
        if not verify_descent_certificate(rows,cert):
            raise ValueError("development collision certificate does not replay")
        receipts.append({"kind":"development-fiber", "certificate":cert,
                         "current_task_verdict":None, "coverage":"development examples only"})
        if "semantics" in view["observations"]:
            refined = development["refined_rows"]
            new = analyze_descent(refined,scope_id="development-unit-refinement.v2")
            if not verify_descent_certificate(refined,new):
                raise ValueError("refinement certificate does not replay")
            receipts.append({"kind":"refined-development-fiber","certificate":new,
                             "current_task_verdict":None,"coverage":"development examples only; unseen input checked separately"})
    c = view["contract"]
    path = view["state_path"]
    if any(type(v) is not int or not -100<=v<=100 for v in path):
        return receipts
    versions = c.get("required_versions",{})
    p = BudgetPolicy(policy_id="lab-state-budget/"+versions.get("policy","v1"),
                     spec_id="state-budget-subquery/"+versions.get("specification","v1"),
                     evaluator_id="state-budget-check/"+versions.get("evaluator","v1"),
                     representation_id="integer-state/v1",
                     allowed_states=tuple(range(-100,101)),max_step=c.get("max_step",2),
                     max_total=c.get("max_total",1),query_scope=c["query_scope"])
    states = [StateRef(f"state-{i}",v) for i,v in enumerate(path)]
    if len(states)>1:
        ws = [make_witness(p,a,b,witness_id=f"step-{i}") for i,(a,b) in enumerate(zip(states,states[1:]))]
        rec = audit_history(p,states[0],ws,prior_obligations=tuple(view.get("obligations",[])))
        receipts.append({"kind":"state-budget","certificate":rec,"terminal":view.get("terminal",False),
                         "admission_effect":"host separately enforces declared scope",
                         "current_task_verdict":None})
    return receipts
