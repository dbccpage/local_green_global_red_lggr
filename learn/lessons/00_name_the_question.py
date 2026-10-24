"""Lesson 00: Name the question.

Three local passes and no declared query. The script emits no composability
status until scope_id, report, and query exist.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: A refusal receipt when a trace has local passes and omits the declaration.
2. What it does not support: A composability label for an undeclared question.
3. Narrowest defensible claim: With scope_id, report, or query absent, status is WITNESS_INCOMPLETE and no contract status is set.
4. Host duty that remains: The host names the carrier, the report, the query, and who may supply a global sample.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from learn.support import dumps, finish, load_json  # noqa: E402

EXPECTED_STATUS = "WITNESS_INCOMPLETE"


def _missing(trace: dict) -> list[str]:
    missing = []
    if not str(trace.get("scope_id") or "").strip():
        missing.append("scope_id")
    steps = trace.get("steps") or []
    has_report = "report" in trace or any(isinstance(step, dict) and "report" in step for step in steps)
    has_query = "query" in trace or any(isinstance(step, dict) and "query" in step for step in steps)
    if not has_report:
        missing.append("report")
    if not has_query:
        missing.append("query")
    return missing


def assess(trace: dict) -> dict:
    missing = _missing(trace)
    if missing:
        return finish({
            "lesson_id": "00",
            "schema": "learn.declaration.v1",
            "authority_effect": "None",
            "status": "WITNESS_INCOMPLETE",
            "missing": missing,
            "local_passes": list(trace.get("local_passes") or []),
            "meaning": "No composability status is emitted until scope_id, report, and query are declared.",
        })
    return finish({
        "lesson_id": "00",
        "schema": "learn.declaration.v1",
        "authority_effect": "None",
        "status": "DECLARED",
        "missing": [],
        "meaning": "The declaration names a scope, a report, and a query. It is not a global pass.",
    })


def prepared() -> dict:
    return assess(load_json("00_local_passes.json"))


def your_turn() -> dict:
    # Your turn: replace the report and query with the objects your next stage actually sees.
    declared = {
        "scope_id": "my-harness-run",
        "report": {"summary": "tool loop finished"},
        "query": {"tickets_closed": True},
        "local_passes": ["retrieve", "edit", "reply"],
    }
    return assess(declared)


def main() -> int:
    row = prepared()
    print("Lesson 00 prepared")
    print(dumps(row))
    if row["status"] != EXPECTED_STATUS or "contract_status" in row:
        return 1
    print("\nLesson 00 your turn")
    print(dumps(your_turn()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
