"""Stable JSON custody and measured, atomic attempt accounting."""
from __future__ import annotations
import hashlib
import json
import threading
from pathlib import Path
from typing import Any, Callable

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def save(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

class BudgetExhausted(RuntimeError):
    pass

class SharedBudget:
    """One permit per issued attempt, including failed calls and repairs.

    Identical retries are NEW attempts. Delivery of an already issued event is
    NOT an attempt. The lock covers admission and reservation before effects.
    """
    def __init__(self, limit: int):
        if type(limit) is not int or limit < 0:
            raise ValueError("resource limit must be a nonnegative integer")
        self.limit = limit
        self.attempts: list[dict] = []
        self._lock = threading.Lock()

    def reserve(self, kind: str, branch: str = "shared") -> dict:
        with self._lock:
            if len(self.attempts) >= self.limit:
                raise BudgetExhausted("shared attempt budget exhausted before issue")
            rec = {"attempt_id": f"attempt-{len(self.attempts) + 1:03d}",
                   "branch": branch, "kind": kind, "cost": 1, "issued": True}
            self.attempts.append(rec)
            return dict(rec)

    def execute(self, kind: str, effect: Callable, branch: str = "shared"):
        permit = self.reserve(kind, branch)
        return permit, effect()

    @property
    def remaining(self) -> int:
        return self.limit - len(self.attempts)
