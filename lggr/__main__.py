"""CLI: python -m lggr --help. Standard library only."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
from typing import Any

from .common import (
    ValidationError,
    boolean,
    canonical,
    digest,
    fields,
    json_value,
    loads_strict,
    sequence,
    text,
)
from .descent import analyze_descent, verify_descent_certificate
from .examples import example_documents, run_demo
from .linear import classify_cochain, verify_l1_certificate
from .streaming import (
    StreamingAuditMonitor,
    StreamingCochainMonitor,
    StreamingFiberMonitor,
)
from .transport import verify_transport
from .witnesses import (
    BudgetPolicy,
    StateRef,
    StepWitness,
    audit_document,
    audit_history,
    make_witness,
)


def _read(path: str) -> Any:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
    return loads_strict(raw)


def _read_lines(path: str) -> list[Any]:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
    stripped = raw.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        parsed = loads_strict(stripped)
        return list(sequence(parsed, "event list"))
    events = []
    for line in raw.splitlines():
        line_s = line.strip()
        if line_s:
            events.append(loads_strict(line_s))
    return events


def _emit(result: Any, output: str | None) -> None:
    raw = json.dumps(json_value(result), indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(raw, encoding="utf-8")
    else:
        sys.stdout.write(raw)


def run_selftest() -> dict[str, Any]:
    """Execute internal self-tests across all lggr modules and return verified receipt."""
    details: dict[str, str] = {}

    # 1. descent
    try:
        t1 = analyze_descent([{"state_id": "s1", "report": "r1", "query": 1},
                              {"state_id": "s2", "report": "r2", "query": 2}], scope_id="selftest")
        t2 = analyze_descent([{"state_id": "s1", "report": "r1", "query": 1},
                              {"state_id": "s2", "report": "r1", "query": 2}], scope_id="selftest")
        if t1["status"] != "DECODER_VERIFIED" or t2["status"] != "REPORT_INSUFFICIENT":
            raise RuntimeError(f"Unexpected descent status: t1={t1['status']}, t2={t2['status']}")
        details["descent"] = "PASS"
    except Exception as exc:
        details["descent"] = f"FAIL: {exc}"

    # 2. linear
    try:
        doc = example_documents()["triangle_l1"]
        l1 = verify_l1_certificate(**doc)
        if l1["status"] != "OPTIMALITY_VERIFIED" or l1["optimum"] != "1":
            raise RuntimeError(f"Unexpected linear status: {l1['status']}, optimum={l1.get('optimum')}")
        details["linear"] = "PASS"
    except Exception as exc:
        details["linear"] = f"FAIL: {exc}"

    # 3. cochain
    try:
        c_unfilled = classify_cochain(**example_documents()["triangle_unfilled"])
        c_filled = classify_cochain(**example_documents()["triangle_filled"])
        if c_unfilled["status"] != "CLOSED_NONEXACT" or c_filled["status"] != "CLOSURE_FAILURE":
            raise RuntimeError(f"Unexpected cochain status: unfilled={c_unfilled['status']}, filled={c_filled['status']}")
        details["cochain"] = "PASS"
    except Exception as exc:
        details["cochain"] = f"FAIL: {exc}"

    # 4. transport
    try:
        t_doc = {k: v for k, v in example_documents()["faithful_transport"].items() if k != "require_reflection"}
        tr = verify_transport(**t_doc)
        if tr["status"] != "RETRACTION_VERIFIED" or not tr["nonrepairability_reflection_verified"]:
            raise RuntimeError(f"Unexpected transport status: {tr['status']}")
        details["transport"] = "PASS"
    except Exception as exc:
        details["transport"] = f"FAIL: {exc}"

    # 5. witnesses
    try:
        p = BudgetPolicy()
        s0, s1, s2 = StateRef("s0", 0), StateRef("s1", 1), StateRef("s2", 2)
        w1 = make_witness(p, s0, s1, witness_id="w1")
        w2 = make_witness(p, s1, s2, witness_id="w2")
        good = audit_history(p, s0, [w1])
        bad = audit_history(p, s0, [w1, w2])
        if good["status"] != "COMPOSITION_VERIFIED" or bad["status"] != "OBSTRUCTION_DETECTED":
            raise RuntimeError(f"Unexpected witness status: good={good['status']}, bad={bad['status']}")
        details["witnesses"] = "PASS"
    except Exception as exc:
        details["witnesses"] = f"FAIL: {exc}"

    # 6. streaming
    try:
        fm = StreamingFiberMonitor(scope_id="selftest")
        o1 = fm.observe("s1", {"rep": 1}, 10)
        o2 = fm.observe("s2", {"rep": 2}, 20)
        o3 = fm.observe("s3", {"rep": 1}, 30)
        if o1["status"] != "OK" or o3["status"] != "REPORT_INSUFFICIENT" or not fm.is_obstructed:
            raise RuntimeError("Fiber monitor selftest failed")

        policy = BudgetPolicy(query_scope="every_prefix", max_total=1)
        s0_ref, s1_ref, s2_ref = StateRef("s0", 0), StateRef("s1", 1), StateRef("s2", 2)
        sw1 = make_witness(policy, s0_ref, s1_ref, witness_id="sw1")
        sw2 = make_witness(policy, s1_ref, s2_ref, witness_id="sw2")
        am = StreamingAuditMonitor(policy, s0_ref)
        st1 = am.step(sw1, global_evaluator_sample=1)
        st2 = am.step(sw2, global_evaluator_sample=1)
        if st1["status"] != "OK" or st1["defect"] != 0 or st1["classification"] != "ZDR":
            raise RuntimeError("Audit monitor step 1 failed")
        if st2["status"] != "ALERT" or am.status != "OBSTRUCTED_LGGR":
            raise RuntimeError("Audit monitor step 2 alert failed")

        cm = StreamingCochainMonitor()
        cm.add_edge("0", "1", 1, 1)
        cm.add_edge("1", "2", 1, 1)
        c_res = cm.add_edge("0", "2", 1, 1)
        if (c_res["status"] != "CYCLE_CLOSED" or
                abs(c_res["closure_defect"]) != Fraction(1) or
                c_res["l1_repair_distance"] != Fraction(1)):
            raise RuntimeError("Cochain monitor cycle closure failed")

        details["streaming"] = "PASS"
    except Exception as exc:
        details["streaming"] = f"FAIL: {exc}"

    all_passed = all(status == "PASS" for status in details.values())
    modules = ["descent", "linear", "cochain", "transport", "witnesses", "streaming"]
    result = {
        "schema": "lggr.selftest.v1",
        "authority_effect": "None",
        "status": "PASS" if all_passed else "FAIL",
        "modules_tested": modules,
        "tests_executed": len(modules),
        "tests_passed": sum(1 for m in modules if details.get(m) == "PASS"),
        "details": details,
    }
    return json_value({**result, "receipt_sha256": digest(result)})


def _handle_stream(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    events = _read_lines(args.input)
    step_receipts: list[dict[str, Any]] = []

    if args.monitor == "fiber":
        monitor_fiber = StreamingFiberMonitor(scope_id=args.scope_id)
        for ev in events:
            fields(ev, {"state_id", "report", "query"}, {"metadata"})
            step_res = monitor_fiber.observe(
                ev["state_id"], ev["report"], ev["query"],
                metadata=ev.get("metadata")
            )
            step_receipts.append(step_res)
        final_receipt = monitor_fiber.get_receipt()
        success = not monitor_fiber.is_obstructed
        summary = {
            "schema": "lggr.stream.v1",
            "authority_effect": "None",
            "monitor": "fiber",
            "status": "COMPOSABLE_LGGG" if success else "OBSTRUCTED_LGGR",
            "events_processed": len(step_receipts),
            "step_receipts": step_receipts,
            "final_receipt": final_receipt,
        }
        return summary, success

    elif args.monitor == "audit":
        if args.policy:
            p_raw = loads_strict(Path(args.policy).read_text(encoding="utf-8-sig"))
            policy = BudgetPolicy.from_dict(p_raw)
        else:
            policy = BudgetPolicy()
        if args.baseline:
            b_raw = loads_strict(Path(args.baseline).read_text(encoding="utf-8-sig"))
            baseline = StateRef.from_dict(b_raw)
        else:
            baseline = None
        monitor_audit = StreamingAuditMonitor(policy, baseline)
        for ev in events:
            if "witness" in ev:
                w_data = ev["witness"]
                g_sample = ev.get("global_evaluator_sample")
                cost = ev.get("step_cost", 0)
            else:
                w_data = {k: v for k, v in ev.items() if k not in ("global_evaluator_sample", "step_cost")}
                g_sample = ev.get("global_evaluator_sample")
                cost = ev.get("step_cost", 0)
            witness = StepWitness.from_dict(w_data)
            step_res = monitor_audit.step(witness, global_evaluator_sample=g_sample, step_cost=cost)
            step_receipts.append(step_res)
        final_receipt = monitor_audit.get_receipt()
        success = (len(monitor_audit.alerts) == 0 and final_receipt.get("status") == "COMPOSITION_VERIFIED")
        summary = {
            "schema": "lggr.stream.v1",
            "authority_effect": "None",
            "monitor": "audit",
            "status": "COMPOSABLE_LGGG" if success else "OBSTRUCTED_LGGR",
            "events_processed": len(step_receipts),
            "step_receipts": step_receipts,
            "final_receipt": final_receipt,
        }
        return summary, success

    else:  # cochain
        monitor_cochain = StreamingCochainMonitor()
        for ev in events:
            src = ev.get("source") or ev.get("u")
            tgt = ev.get("target") or ev.get("v")
            val = ev.get("value") if "value" in ev else ev.get("h")
            wt = ev.get("weight") if "weight" in ev else 1
            if src is None or tgt is None or val is None:
                raise ValidationError("Cochain event must specify source/u, target/v, and value/h")
            step_res = monitor_cochain.add_edge(src, tgt, val, wt)
            step_receipts.append(step_res)
        final_receipt = monitor_cochain.get_receipt()
        success = not any(c["closure_defect"] != 0 for c in monitor_cochain.cycles)
        summary = {
            "schema": "lggr.stream.v1",
            "authority_effect": "None",
            "monitor": "cochain",
            "status": "COMPOSABLE_LGGG" if success else "OBSTRUCTED_LGGR",
            "events_processed": len(step_receipts),
            "step_receipts": step_receipts,
            "final_receipt": final_receipt,
        }
        return summary, success


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scoped LGGR certificate verification. AuthorityEffect: None.")
    subs = parser.add_subparsers(dest="command", required=True)
    descriptions = {
        "demo": "Reproduce all examples and the exhaustive finite census",
        "selftest": "Execute internal self-tests across all modules and emit verified receipt",
        "stream": "Consume line-delimited streaming JSON events and emit online receipts",
        "audit": "Replay a finite history and its protected budget query",
        "descent": "Construct a decoder or a report-collision certificate",
        "linear": "Verify an exact weighted-L1 primal/dual certificate",
        "cochain": "Check exactness/closure on a declared rational complex",
        "transport": "Verify commuting transport and optional retraction",
        "replay": "Replay a descent or audit receipt against its original input",
    }
    for name, help_text in descriptions.items():
        sub = subs.add_parser(name, help=help_text)
        if name in ("demo", "selftest"):
            sub.add_argument("--output", "-o", help="Write JSON to this path instead of stdout")
        elif name == "stream":
            sub.add_argument("input", nargs="?", default="-", help="Line-delimited JSON file, or '-' for stdin")
            sub.add_argument("--monitor", "-m", choices=["fiber", "audit", "cochain"], required=True,
                             help="Streaming monitor type")
            sub.add_argument("--scope-id", default="online-stream", help="Scope identifier for fiber monitor")
            sub.add_argument("--policy", help="Path to JSON BudgetPolicy for audit monitor")
            sub.add_argument("--baseline", help="Path to JSON StateRef for audit monitor")
            sub.add_argument("--output", "-o", help="Write JSON to this path instead of stdout")
        else:
            sub.add_argument("input", help="UTF-8 JSON file, or '-' for stdin")
            if name == "replay":
                sub.add_argument("certificate", help="Receipt JSON file")
            sub.add_argument("--output", "-o", help="Write JSON to this path instead of stdout")

    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result, success = run_demo(), True
        elif args.command == "selftest":
            result = run_selftest()
            success = result["status"] == "PASS"
        elif args.command == "stream":
            result, success = _handle_stream(args)
        elif args.command == "audit":
            data = _read(args.input)
            result = audit_document(data)
            success = result["status"] == "COMPOSITION_VERIFIED"
        elif args.command == "descent":
            data = _read(args.input)
            fields(data, {"scope_id", "rows"})
            result = analyze_descent(sequence(data["rows"], "rows"), scope_id=text(data["scope_id"], "scope_id"))
            success = result["status"] == "DECODER_VERIFIED"
        elif args.command == "linear":
            data = _read(args.input)
            fields(data, {"D", "h", "weights", "potential", "dual"})
            result = verify_l1_certificate(**data)
            success = result["status"] in ("OPTIMALITY_VERIFIED", "LOWER_BOUND_VERIFIED")
        elif args.command == "cochain":
            data = _read(args.input)
            fields(data, {"D0", "h"}, {"D1"})
            result = classify_cochain(**data)
            success = result["status"] in ("EXACT", "EXACT_REPAIR")
        elif args.command == "transport":
            data = _read(args.input)
            fields(data, {"D_source", "D_target", "F0", "F1"}, {"G0", "G1", "require_reflection"})
            reflection = boolean(data.get("require_reflection", False), "require_reflection")
            result = verify_transport(**{k: v for k, v in data.items() if k != "require_reflection"})
            success = (result["status"] in ("COMMUTING_TRANSPORT_VERIFIED", "RETRACTION_VERIFIED")
                       and (not reflection or result["nonrepairability_reflection_verified"]))
        else:  # replay
            data = _read(args.input)
            certificate = _read(args.certificate)
            if not isinstance(certificate, dict):
                raise ValidationError("Certificate must be a JSON object")
            schema = certificate.get("schema")
            if schema == "lggr.descent.v1":
                fields(data, {"scope_id", "rows"})
                success = (certificate.get("scope_id") == data["scope_id"] and
                           verify_descent_certificate(sequence(data["rows"], "rows"), certificate))
            elif schema == "lggr.audit.v1":
                success = canonical(audit_document(data)) == canonical(certificate)
            else:
                raise ValidationError("replay supports lggr.descent.v1 and lggr.audit.v1")
            result = {"schema": "lggr.replay.v1", "authority_effect": "None",
                      "status": "REPLAY_VERIFIED" if success else "REPLAY_MISMATCH",
                      "meaning": "Receipt matches the supplied input; a valid negative receipt is still negative."}
        _emit(result, args.output)
        return 0 if success else 1
    except (ValidationError, OSError, UnicodeError, RecursionError) as exc:
        sys.stderr.write(json.dumps({"schema": "lggr.error.v1", "authority_effect": "None",
                                     "status": "INPUT_ERROR", "error": str(exc)}) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
