"""JSON-lines sidecar over learn/harness_adapter.py for harnesses in any language.

Read one JSON object per line on stdin, write one receipt per line on stdout.
The first line is {"declare": <run declaration>}. Each later line is
{"event": "handoff" | "step" | "review_edge" | "generation", ...fields} or
{"event": "summary"}. Field names follow learn/HARNESS_CONTRACT.md. A bad line
yields {"status": "INVALID_EVENT", "error": ...} and the sidecar keeps reading.

AuthorityEffect: None. From the repository root: python -m learn.sidecar
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import IO, Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from learn.harness_adapter import RunGuard, bind, envelope  # noqa: E402

_EVENTS = ("handoff", "step", "review_edge", "generation", "summary")


def handle(guard: RunGuard | None, line: dict[str, Any]) -> tuple[RunGuard | None, dict[str, Any]]:
    if "declare" in line:
        guard = bind(line["declare"])
        status = guard.rejection["status"] if guard.rejection else "DECLARED"
        return guard, envelope(status, None, scope_id=line["declare"]["scope_id"])
    if guard is None:
        raise ValueError("first line must be a declaration")
    event = dict(line)
    kind = event.pop("event", None)
    if kind not in _EVENTS:
        raise ValueError(f"event must be one of {', '.join(_EVENTS)}")
    if kind == "summary":
        return guard, guard.summary()
    return guard, getattr(guard, kind)(event)


def serve(stdin: IO[str], stdout: IO[str]) -> int:
    guard: RunGuard | None = None
    for raw in stdin:
        if not raw.strip():
            continue
        try:
            guard, receipt = handle(guard, json.loads(raw))
        except Exception as exc:  # report and keep reading; the host decides whether to stop
            receipt = {"lesson_schema": "learn.harness_event.v1", "authority_effect": "None",
                       "status": "INVALID_EVENT", "error": f"{type(exc).__name__}: {exc}"}
        stdout.write(json.dumps(receipt, sort_keys=True) + "\n")
        stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(serve(sys.stdin, sys.stdout))
