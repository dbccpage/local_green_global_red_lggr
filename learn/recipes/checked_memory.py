"""Recipe: checked memory (guide 04).

Each record is bound to the hash of the source it was read from and the hash of
the contract it was written under. Recall recomputes both and labels every
record instead of silently dropping it. Open obligations come back on every
recall. A changed representation is a migration, not a reread.

This applies the audit monitor's manifest pin (POLICY_MANIFEST_CHANGED,
REPRESENTATION_TRANSPORT_REQUIRED) to memory. It mirrors backend D of the
LGGR/RSI swarm experiment's RSI battery (experiments/lggr_rsi_swarm/REPORT.md).
There it was inconclusive: 40/90 versus 36/90 passes after a contract change,
p = 0.29. This recipe makes no performance claim.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: Labelling recalled records FRESH, STALE_SOURCE, STALE_CONTRACT, TRANSPORT_REQUIRED, or CONFLICT, and returning open obligations, across a save and load.
2. What it does not support: Deciding whether a stale record is still true, or clearing an obligation.
3. Narrowest defensible claim: In the demo the record recalled after a restart is FRESH, then STALE_SOURCE after the source changes, then STALE_CONTRACT after max_total changes, and the obligation is returned each time.
4. Host duty that remains: The host supplies current source text and the current policy at recall time, and decides what an agent may do with a stale record.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import BudgetPolicy  # noqa: E402

from learn.support import dumps, finish  # noqa: E402

RECIPE_ID = "checked_memory"
EXPECTED_STATUS = "STALE_CONTRACT"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class CheckedMemory:
    """Same four calls an agent tool layer exposes: append, recall, mark_obligation, list_obligations."""

    def __init__(self, records: list[dict[str, Any]] | None = None,
                 obligations: dict[str, str] | None = None) -> None:
        self.records = list(records or [])
        self.obligations = dict(obligations or {})

    def append(self, key: str, content: str, *, source_ref: str, source_text: str,
               policy: BudgetPolicy) -> None:
        self.records.append({
            "key": key, "content": content, "source_ref": source_ref,
            "source_sha256": _sha(source_text), "contract_sha256": policy.sha256,
            "representation_id": policy.representation_id,
        })

    def mark_obligation(self, key: str, text: str) -> None:
        self.obligations[key] = text

    def list_obligations(self) -> list[dict[str, str]]:
        return [{"key": k, "text": v} for k, v in sorted(self.obligations.items())]

    def recall(self, query: str, *, sources: Mapping[str, str], policy: BudgetPolicy) -> dict[str, Any]:
        hits = []
        for record in self.records:
            if query not in record["key"]:
                continue
            current = sources.get(record["source_ref"])
            if record["representation_id"] != policy.representation_id:
                status = "TRANSPORT_REQUIRED"
            elif record["contract_sha256"] != policy.sha256:
                status = "STALE_CONTRACT"
            elif current is None or _sha(current) != record["source_sha256"]:
                status = "STALE_SOURCE"
            else:
                status = "FRESH"
            hits.append({**record, "status": status})
        fresh_by_key: dict[str, set[str]] = {}
        for hit in hits:
            if hit["status"] == "FRESH":
                fresh_by_key.setdefault(hit["key"], set()).add(hit["content"])
        for hit in hits:
            if hit["status"] == "FRESH" and len(fresh_by_key[hit["key"]]) > 1:
                hit["status"] = "CONFLICT"
        return {"records": hits, "obligations": self.list_obligations()}

    def save(self, path: Path) -> None:
        path.write_text(json.dumps({"records": self.records, "obligations": self.obligations},
                                   indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "CheckedMemory":
        body = json.loads(path.read_text(encoding="utf-8"))
        return cls(body["records"], body["obligations"])


def demo() -> dict[str, Any]:
    policy = BudgetPolicy(policy_id="settlement/v1", authority_id="release-owner",
                          max_total=1, query_scope="every_prefix")
    contract = "def compute_quote(items) -> {'net_cents': int}"
    memory = CheckedMemory()
    memory.append("pricing.output_key", "net_cents", source_ref="pricing.py", source_text=contract, policy=policy)
    memory.mark_obligation("tax_engine", "recheck tax_engine after any pricing schema change")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "memory.json"
        memory.save(path)
        restarted = CheckedMemory.load(path)

    after_restart = restarted.recall("pricing", sources={"pricing.py": contract}, policy=policy)
    changed = "def compute_quote(items) -> {'net_amount_cents': int}"
    after_edit = restarted.recall("pricing", sources={"pricing.py": changed}, policy=policy)
    loosened = dataclasses.replace(policy, max_total=2)
    after_policy = restarted.recall("pricing", sources={"pricing.py": contract}, policy=loosened)

    restarted.append("pricing.output_key", "net_amount_cents", source_ref="pricing.py",
                     source_text=contract, policy=policy)
    conflicted = restarted.recall("pricing", sources={"pricing.py": contract}, policy=policy)

    return finish({
        "recipe_id": RECIPE_ID,
        "schema": "learn.recipe.checked_memory.v1",
        "authority_effect": "None",
        "status": after_policy["records"][0]["status"],
        "after_restart": after_restart["records"][0]["status"],
        "after_source_edit": after_edit["records"][0]["status"],
        "after_policy_change": after_policy["records"][0]["status"],
        "two_writers": [r["status"] for r in conflicted["records"]],
        "obligations_every_recall": [len(r["obligations"]) for r in (after_restart, after_edit, after_policy)],
    })


def main() -> int:
    row = demo()
    print(dumps(row))
    return 0 if row["status"] == EXPECTED_STATUS else 1


if __name__ == "__main__":
    sys.exit(main())
