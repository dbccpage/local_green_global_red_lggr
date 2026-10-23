"""CLI: python -m lggr --help. Standard library only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .common import ValidationError, boolean, canonical, fields, json_value, loads_strict, sequence, text
from .descent import analyze_descent, verify_descent_certificate
from .examples import run_demo
from .linear import classify_cochain, verify_l1_certificate
from .transport import verify_transport
from .witnesses import audit_document


def _read(path: str) -> Any:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
    return loads_strict(raw)


def _emit(result: Any, output: str | None) -> None:
    raw = json.dumps(json_value(result), indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(raw, encoding="utf-8")
    else:
        sys.stdout.write(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scoped LGGR certificate verification. AuthorityEffect: None.")
    subs = parser.add_subparsers(dest="command", required=True)
    descriptions = {"demo": "Reproduce all examples and the exhaustive finite census",
                    "audit": "Replay a finite history and its protected budget query",
                    "descent": "Construct a decoder or a report-collision certificate",
                    "linear": "Verify an exact weighted-L1 primal/dual certificate",
                    "cochain": "Check exactness/closure on a declared rational complex",
                    "transport": "Verify commuting transport and optional retraction",
                    "replay": "Replay a descent or audit receipt against its original input"}
    for name, help_text in descriptions.items():
        sub = subs.add_parser(name, help=help_text)
        if name != "demo":
            sub.add_argument("input", help="UTF-8 JSON file, or '-' for stdin")
        if name == "replay":
            sub.add_argument("certificate", help="Receipt JSON file")
        sub.add_argument("--output", "-o", help="Write JSON to this path instead of stdout")
    args = parser.parse_args(argv)
    try:
        data = _read(args.input) if args.command != "demo" else None
        if args.command == "demo":
            result, success = run_demo(), True
        elif args.command == "audit":
            result = audit_document(data)
            success = result["status"] == "COMPOSITION_VERIFIED"
        elif args.command == "descent":
            fields(data, {"scope_id", "rows"})
            result = analyze_descent(sequence(data["rows"], "rows"), scope_id=text(data["scope_id"], "scope_id"))
            success = result["status"] == "DECODER_VERIFIED"
        elif args.command == "linear":
            fields(data, {"D", "h", "weights", "potential", "dual"})
            result = verify_l1_certificate(**data)
            success = result["status"] in ("OPTIMALITY_VERIFIED", "LOWER_BOUND_VERIFIED")
        elif args.command == "cochain":
            fields(data, {"D0", "h"}, {"D1"})
            result = classify_cochain(**data)
            success = result["status"] in ("EXACT", "EXACT_REPAIR")
        elif args.command == "transport":
            fields(data, {"D_source", "D_target", "F0", "F1"}, {"G0", "G1", "require_reflection"})
            reflection = boolean(data.get("require_reflection", False), "require_reflection")
            result = verify_transport(**{k: v for k, v in data.items() if k != "require_reflection"})
            success = (result["status"] in ("COMMUTING_TRANSPORT_VERIFIED", "RETRACTION_VERIFIED")
                       and (not reflection or result["nonrepairability_reflection_verified"]))
        else:
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
