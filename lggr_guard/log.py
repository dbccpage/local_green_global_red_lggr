"""Append-only, hash-chained decision log: who proposed, what was judged by which evaluator, why.

Editing or deleting any earlier record breaks the chain, so `verify` detects it.
AuthorityEffect: None.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class DecisionLog:
    def __init__(self, path):
        self.path = Path(path)

    def records(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append(self, kind, data):
        records = self.records()
        body = {"index": len(records), "previous": records[-1]["sha256"] if records else None, "kind": kind, "data": data}
        record = {**body, "sha256": _digest(body)}
        with open(self.path, "a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(record, sort_keys=True, default=str) + "\n")
        return record

    def verify(self):
        previous = None
        for i, r in enumerate(self.records()):
            body = {k: r[k] for k in ("index", "previous", "kind", "data")}
            if r["index"] != i or r["previous"] != previous or _digest(body) != r["sha256"]:
                return {"ok": False, "broken_at": i}
            previous = r["sha256"]
        return {"ok": True, "records": len(self.records())}
