"""Reproducible examples from the supplied LGGR report, plus explicit extensions."""
from __future__ import annotations

from copy import deepcopy
from itertools import product
from typing import Any

from .descent import analyze_descent, evaluator_defect, verify_descent_certificate
from .linear import classify_cochain, verify_l1_certificate
from .transport import verify_transport
from .witnesses import audit_document, history_document

D_TRIANGLE = [[-1, 1, 0], [0, -1, 1], [-1, 0, 1]]


def example_documents() -> dict[str, dict[str, Any]]:
    bad, good = history_document((0, 1, 2)), history_document((0, 1, 0))
    incomplete = deepcopy(bad)
    for w in incomplete["witnesses"]:
        w["source"]["value"] = None
        w["target"]["value"] = None
    authority = deepcopy(good)
    authority["witnesses"][-1]["authority_id"] = "different-owner/v2"
    obligations = deepcopy(good)
    obligations["witnesses"][0]["obligations"] = ["verify-new-interface-semantics"]

    def reports(doc: dict[str, Any]) -> list[list[Any]]:
        return [[w["observed_magnitude"], w["local_accepted"], w["smoke_passed"]] for w in doc["witnesses"]]

    rows = [{"state_id": "good:0,1,0", "report": reports(good), "query": True},
            {"state_id": "bad:0,1,2", "report": reports(bad), "query": False}]
    refined_rows = [{"state_id": "good:0,1,0", "report": [1, -1], "query": True},
                    {"state_id": "bad:0,1,2", "report": [1, 1], "query": False}]
    linear = {"D": D_TRIANGLE, "h": [1, 1, 1], "weights": [1, 1, 1],
              "potential": [0, 1, 2], "dual": [1, 1, -1]}
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    permutation = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    target = [D_TRIANGLE[1], D_TRIANGLE[0], D_TRIANGLE[2]]
    faithful = {"D_source": D_TRIANGLE, "D_target": target, "F0": identity, "F1": permutation,
                "G0": identity, "G1": permutation, "require_reflection": True}
    lossy = {"D_source": D_TRIANGLE, "D_target": [[0]], "F0": [[0, 0, 0]],
             "F1": [[0, 0, 0]], "require_reflection": True}
    return {"bad_history": bad, "good_history": good, "reports_only": incomplete,
            "authority_changed": authority, "open_obligation": obligations,
            "report_collision": {"scope_id": "two-budget-histories/restricted-reports", "rows": rows},
            "refined_reports": {"scope_id": "two-budget-histories/signed-deltas", "rows": refined_rows},
            "triangle_l1": linear,
            "triangle_unfilled": {"D0": D_TRIANGLE, "h": [1, 1, 1], "D1": []},
            "triangle_filled": {"D0": D_TRIANGLE, "h": [1, 1, 1], "D1": [[1, 1, -1]]},
            "budget_exact_cochain": {"D0": D_TRIANGLE, "h": [1, 1, 2], "D1": [[1, 1, -1]]},
            "faithful_transport": faithful, "lossy_transport": lossy}


def finite_census() -> dict[str, int]:
    """Independently enumerate all 216 three-state report/query instances."""
    cases = 0
    collisions = decoders = 0
    for report in product(range(3), repeat=3):
        for query in product((False, True), repeat=3):
            rows = [{"state_id": str(i), "report": report[i], "query": query[i]} for i in range(3)]
            certificate = analyze_descent(rows, scope_id="three-state-census")
            # Separate brute-force decoder enumeration, not the grouping algorithm.
            exists = any(all(mapping[report[i]] == query[i] for i in range(3))
                         for mapping in product((False, True), repeat=3))
            if (certificate["status"] == "DECODER_VERIFIED") != exists:
                raise RuntimeError("Finite decoder census failed")
            if not verify_descent_certificate(rows, certificate):
                raise RuntimeError("Certificate replay failed")
            cases += 1
            decoders += int(exists)
            collisions += int(not exists)
    verdicts = 0
    for a, b, g in product((0, 1), repeat=3):
        result = evaluator_defect(a, b, g)
        if result["delta"] != g - a * b:
            raise RuntimeError("Evaluator defect census failed")
        verdicts += 1
    return {"factorization_cases": cases, "decoders": decoders, "collisions": collisions,
            "boolean_verdict_cases": verdicts}


def run_demo() -> dict[str, Any]:
    docs = example_documents()
    audits = {name: audit_document(docs[name]) for name in
              ("bad_history", "good_history", "reports_only", "authority_changed", "open_obligation")}
    expected = {"bad_history": "OBSTRUCTION_DETECTED", "good_history": "COMPOSITION_VERIFIED",
                "reports_only": "WITNESS_INCOMPLETE", "authority_changed": "AUTHORITY_REQUIRED",
                "open_obligation": "WITNESS_INCOMPLETE"}
    if any(audits[k]["status"] != v for k, v in expected.items()):
        raise RuntimeError("Demonstration did not reproduce the expected audit outcomes")
    descent = {name: analyze_descent(docs[name]["rows"], scope_id=docs[name]["scope_id"])
               for name in ("report_collision", "refined_reports")}
    transport = {}
    for name in ("faithful_transport", "lossy_transport"):
        data = {k: v for k, v in docs[name].items() if k != "require_reflection"}
        transport[name] = verify_transport(**data)
    return {"schema": "lggr.demo.v1", "authority_effect": "None", "audits": audits,
            "descent": descent, "evaluator_defect": evaluator_defect(1, 1, 0),
            "l1_certificate": verify_l1_certificate(**docs["triangle_l1"]),
            "cochains": {name: classify_cochain(**docs[name]) for name in
                         ("triangle_unfilled", "triangle_filled", "budget_exact_cochain")},
            "transport": transport, "finite_census": finite_census(),
            "comparison": {"previous_state_gate_accepts_bad_history": True,
                           "fixed_baseline_check_accepts_bad_history": False,
                           "witness_adapter_accepts_bad_history": False,
                           "extra_detection_power_over_fixed_baseline_demonstrated": False},
            "limitations": ["Not a native OE/QM integration or fresh Lean proof replay.",
                            "All evidence concerns explicitly supplied finite data.",
                            "A collision certifies report insufficiency, not which history occurred.",
                            "Runtime observations, owner authority and immutable storage remain external."]}
