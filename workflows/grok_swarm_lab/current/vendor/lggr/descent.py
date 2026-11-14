"""Executable decoder-or-collision on an explicitly supplied finite table.

This is an algorithm on finite data, not an algorithm deciding arbitrary
software semantics or the infinite classical existence theorem.
"""
from __future__ import annotations

import json
from typing import Any, Iterable

from .common import ValidationError, canonical, digest, fields, text


def _rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    seen: set[str] = set()
    for row in rows:
        fields(row, {"state_id", "report", "query"})
        state_id = text(row["state_id"], "state_id")
        if state_id in seen:
            raise ValidationError(f"Duplicate state_id: {state_id}")
        seen.add(state_id)
        # Copy through canonical JSON, so the result does not alias caller data.
        normalized.append(json.loads(canonical(row)))
    return sorted(normalized, key=lambda item: item["state_id"])


def _scope(scope_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"scope_id": text(scope_id, "scope_id"), "carrier_size": len(rows),
            "table_sha256": digest(rows), "coverage": "supplied finite table only"}


def analyze_descent(rows: Iterable[dict[str, Any]], *, scope_id: str) -> dict[str, Any]:
    """Return a decoder on realized reports, or two equal-report/different-query states.

    Report/query equality is canonical, type-sensitive JSON equality. Thus
    True and 1, or "1" and 1, are different observations. Complexity is linear
    in input size after deterministic sorting of state IDs.
    """
    table = _rows(rows)
    result: dict[str, Any] = {"schema": "lggr.descent.v1", "authority_effect": "None",
                              **_scope(scope_id, table)}
    representatives: dict[str, dict[str, Any]] = {}
    for row in table:
        report_key = canonical(row["report"])
        old = representatives.get(report_key)
        if old is not None and canonical(old["query"]) != canonical(row["query"]):
            return {**result, "status": "REPORT_INSUFFICIENT",
                    "collision": {"left": old, "right": row},
                    "realized_history_violation": None,
                    "meaning": "These reports cannot determine this query on the supplied carrier."}
        representatives.setdefault(report_key, row)
    decoder = [{"report": representatives[key]["report"], "query": representatives[key]["query"]}
               for key in sorted(representatives)]
    return {**result, "status": "DECODER_VERIFIED", "decoder": decoder,
            "meaning": "The supplied query is constant on every realized report fiber in this finite table."}


def verify_descent_certificate(rows: Iterable[dict[str, Any]], certificate: dict[str, Any]) -> bool:
    """Replay the certificate against supplied table data; never trust its status alone.

    Returns False for a malformed/tampered certificate. Malformed *table*
    input raises ValidationError, because it does not declare a finite carrier.
    """
    table = _rows(rows)
    try:
        if not isinstance(certificate, dict):
            return False
        if (certificate.get("schema") != "lggr.descent.v1" or
                certificate.get("authority_effect") != "None"):
            return False
        expected = _scope(certificate.get("scope_id"), table)
        if any(canonical(certificate.get(k)) != canonical(v) for k, v in expected.items()):
            return False
        base_fields = {"schema", "authority_effect", "scope_id", "carrier_size", "table_sha256", "coverage", "status", "meaning"}
        if certificate.get("status") == "REPORT_INSUFFICIENT":
            fields(certificate, base_fields | {"collision", "realized_history_violation"})
            if (certificate["realized_history_violation"] is not None or
                    certificate["meaning"] != "These reports cannot determine this query on the supplied carrier."):
                return False
            collision = certificate["collision"]
            fields(collision, {"left", "right"})
            by_id = {r["state_id"]: r for r in table}
            a, b = collision["left"], collision["right"]
            return (canonical(by_id[a["state_id"]]) == canonical(a) and
                    canonical(by_id[b["state_id"]]) == canonical(b) and
                    canonical(a["report"]) == canonical(b["report"]) and
                    canonical(a["query"]) != canonical(b["query"]))
        if certificate.get("status") == "DECODER_VERIFIED":
            fields(certificate, base_fields | {"decoder"})
            if certificate["meaning"] != "The supplied query is constant on every realized report fiber in this finite table.":
                return False
            entries = certificate["decoder"]
            if not isinstance(entries, list):
                return False
            mapping: dict[str, str] = {}
            for entry in entries:
                fields(entry, {"report", "query"})
                key = canonical(entry["report"])
                if key in mapping:
                    return False
                mapping[key] = canonical(entry["query"])
            return (set(mapping) == {canonical(r["report"]) for r in table} and
                    all(mapping[canonical(r["report"])] == canonical(r["query"]) for r in table))
        return False
    except (KeyError, TypeError, ValueError):
        return False


def decode(certificate: dict[str, Any], report: Any) -> Any:
    """Apply a *previously replayed* decoder. Unknown reports are not extrapolated.

    Call verify_descent_certificate with the source table before trusting a
    certificate from outside your process. This lookup cannot authenticate it.
    """
    if certificate.get("status") != "DECODER_VERIFIED":
        raise ValidationError("A decoder certificate is required")
    key = canonical(report)
    for entry in certificate["decoder"]:
        if canonical(entry["report"]) == key:
            return json.loads(canonical(entry["query"]))
    raise KeyError("Report is outside the certified realized image")


def evaluator_defect(first: bool | int, second: bool | int, global_verdict: bool | int) -> dict[str, Any]:
    """Delta = Eg - E1*E2, reimplemented from the supplied report's EPK definition."""
    values = (first, second, global_verdict)
    if any(type(v) not in (bool, int) or v not in (0, 1) for v in values):
        raise ValidationError("Evaluator verdicts must be Boolean or integer 0/1")
    a, b, g = map(int, values)
    delta = g - a * b
    return {"local": [a, b], "global": g, "delta": delta,
            "defect_kind": {-1: "NGD", 0: "ZDR", 1: "PGD"}[delta]}
