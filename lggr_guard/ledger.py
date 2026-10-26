"""Hash-chained, append-only ledger of anchors, accepted changes, and full checks.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Entry kinds:
  checkpoint  a full post-merge check passed on ``ref``; pending changes reset
  anchor      the owner approved ``facts`` as the reference for drift contracts
  accept      a change passed the gate and the named approver accepted it
  clear       the owner cleared an open obligation

Keep the file where the agents cannot write it. The CLI default is inside
``.git/``, which no branch or pull request can change.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from lggr.common import ValidationError, digest

from .model import Candidate

GENESIS = "0" * 64
KINDS = ("checkpoint", "anchor", "accept", "clear")


class LedgerTampered(ValidationError):
    """The hash chain does not verify. The gate refuses to run on it."""


@dataclass
class Ledger:
    entries: list[dict[str, Any]]
    path: Path | None = None
    live_refs: dict[str, Any] | None = None  # in-process refs (callables) that JSON cannot hold

    # ------------------------------------------------------------------ io
    @classmethod
    def load(cls, path: str | Path) -> "Ledger":
        p = Path(path)
        entries = []
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    entries.append(json.loads(line))
        ledger = cls(entries, p)
        ledger.verify()
        return ledger

    @classmethod
    def memory(cls) -> "Ledger":
        return cls([], None)

    def verify(self) -> None:
        prev = GENESIS
        for i, entry in enumerate(self.entries):
            body = {k: v for k, v in entry.items() if k != "entry_sha256"}
            if entry.get("seq") != i or entry.get("prev") != prev or digest(body) != entry.get("entry_sha256"):
                raise LedgerTampered(f"ledger entry {i} does not verify")
            if entry.get("kind") not in KINDS:
                raise LedgerTampered(f"ledger entry {i} has unknown kind")
            prev = entry["entry_sha256"]

    def append(self, kind: str, **payload: Any) -> dict[str, Any]:
        if kind not in KINDS:
            raise ValidationError(f"unknown ledger kind {kind}")
        prev = self.entries[-1]["entry_sha256"] if self.entries else GENESIS
        body = {"seq": len(self.entries), "prev": prev, "kind": kind, **payload}
        entry = {**body, "entry_sha256": digest(body)}
        self.entries.append(entry)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    # ------------------------------------------------------------- queries
    def _last_index(self, kind: str) -> int:
        return max((i for i, e in enumerate(self.entries) if e["kind"] == kind), default=-1)

    @property
    def checkpoint(self) -> dict[str, Any] | None:
        i = self._last_index("checkpoint")
        return self.entries[i] if i >= 0 else None

    @property
    def anchor_facts(self) -> dict[str, Any] | None:
        i = self._last_index("anchor")
        return dict(self.entries[i]["facts"]) if i >= 0 else None

    def pending(self) -> list[Candidate]:
        """Accepted changes since the last full check, in acceptance order."""
        start = self._last_index("checkpoint") + 1
        out = []
        for e in self.entries[start:]:
            if e["kind"] == "accept":
                ref = tuple(e["ref"]) if isinstance(e.get("ref"), list) else e.get("ref")
                if ref is None and self.live_refs:
                    ref = self.live_refs.get(e["change_id"])
                out.append(Candidate(e["change_id"], dict(e.get("declares", {})),
                                  tuple(e.get("obligations", ())), ref))
        return out

    def open_obligations(self) -> list[dict[str, str]]:
        cleared = {(e["change_id"], e["obligation"]) for e in self.entries if e["kind"] == "clear"}
        out = []
        for e in self.entries:
            if e["kind"] == "accept":
                for ob in e.get("obligations", ()):
                    if (e["change_id"], ob) not in cleared:
                        out.append({"change_id": e["change_id"], "obligation": ob})
        return out

    # ------------------------------------------------------------- writers
    def record_checkpoint(self, ref: Any, facts: dict[str, Any], *, smoke: str) -> dict[str, Any]:
        return self.append("checkpoint", ref=ref, facts=facts, smoke=smoke)

    def record_anchor(self, facts: dict[str, Any], *, approved_by: str) -> dict[str, Any]:
        return self.append("anchor", facts=facts, approved_by=approved_by)

    def record_accept(self, change: Candidate, receipt: dict[str, Any], *, approved_by: str) -> dict[str, Any]:
        if receipt.get("status") != "COMPOSITION_VERIFIED":
            raise ValidationError(f"refusing to accept {change.change_id}: gate status {receipt.get('status')}")
        if receipt.get("candidate") != change.change_id:
            raise ValidationError("receipt is for a different change")
        ref = list(change.ref) if isinstance(change.ref, tuple) else change.ref
        if callable(ref):
            self.live_refs = {**(self.live_refs or {}), change.change_id: ref}
            ref = None
        return self.append("accept", change_id=change.change_id, declares=dict(change.declares),
                           obligations=list(change.obligations), ref=ref,
                           receipt_sha256=receipt["receipt_sha256"], approved_by=approved_by,
                           suite_sha256=receipt["suite_sha256"])

    def record_clear(self, change_id: str, obligation: str, *, approved_by: str) -> dict[str, Any]:
        if {"change_id": change_id, "obligation": obligation} not in self.open_obligations():
            raise ValidationError(f"no open obligation {obligation!r} on {change_id}")
        return self.append("clear", change_id=change_id, obligation=obligation, approved_by=approved_by)

    def suite_hashes(self) -> Iterable[str]:
        start = self._last_index("checkpoint") + 1
        return {e["suite_sha256"] for e in self.entries[start:] if e["kind"] == "accept"}
