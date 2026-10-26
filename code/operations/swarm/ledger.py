"""Persistent, transactional spend ledger with wave reservations.

Amounts are Decimal USD strings. A wave is reserved as a whole (all or nothing)
before any of its requests launch; every request then settles (reported usage),
fails (keeps its full reservation) or is released (refused before dispatch, never
sent). A new wave cannot be reserved while any reservation is outstanding.
Reservations found outstanding when the ledger is opened (a crash) are converted
to retained charges.
"""
from decimal import Decimal
import json
import os
from pathlib import Path
import threading
import time

RATES = {"input": Decimal("0.10"), "cache_write": Decimal("0.125"), "cache_read": Decimal("0.01"), "output": Decimal("0.50")}
MAX_INPUT, MAX_OUTPUT = 10000, 4096
RESERVATION = (MAX_INPUT * RATES["cache_write"] + MAX_OUTPUT * RATES["output"]) / Decimal(10 ** 6)
TOTAL_CEILING = Decimal("150")  # lowered from 160 at the owner's request (protocol R4)
PHASE_CEILINGS = {"development": Decimal("20"), "evaluation": Decimal("140"), "sensitivity": Decimal("20")}


class BudgetExceeded(Exception):
    pass


def usage_cost(usage):
    """USD charge from a Messages usage object (dict). Unknown extra fields are ignored."""
    tokens = {
        "input": usage.get("input_tokens") or 0,
        "cache_write": usage.get("cache_creation_input_tokens") or 0,
        "cache_read": usage.get("cache_read_input_tokens") or 0,
        "output": usage.get("output_tokens") or 0,
    }
    for value in tokens.values():
        if not isinstance(value, int) or value < 0:
            raise ValueError("invalid usage token count")
    return sum(Decimal(tokens[k]) * RATES[k] for k in tokens) / Decimal(10 ** 6)


class Ledger:
    def __init__(self, path, phase, persist=True, reservation=RESERVATION):
        if phase not in PHASE_CEILINGS:
            raise ValueError("unknown phase")
        self.path, self.phase, self.persist = Path(path) if path else None, phase, persist
        self.lock = threading.Lock()
        self.reservation = reservation
        self.recovered = []
        if self.path and self.path.exists():
            self.state = json.loads(self.path.read_text(encoding="utf-8"))
            for p in PHASE_CEILINGS:
                self.state["phases"].setdefault(p, {"settled": "0", "retained": "0", "requests": 0})
            for key, item in sorted(self.state["inflight"].items()):
                self.state["phases"][item["phase"]]["retained"] = str(Decimal(self.state["phases"][item["phase"]]["retained"]) + Decimal(item["amount"]))
                self.recovered.append(key)
            self.state["inflight"] = {}
            self._save()
        else:
            self.state = {"schema": "lggr.rsi_swarm.ledger.v1", "inflight": {},
                          "phases": {p: {"settled": "0", "retained": "0", "requests": 0} for p in PHASE_CEILINGS}}
            self._save()

    def _save(self):
        if not (self.path and self.persist):
            return
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        for attempt in range(50):  # Windows may briefly lock the target (indexers, scanners); local file op only
            try:
                os.replace(tmp, self.path)
                return
            except PermissionError:
                if attempt == 49:
                    raise
                time.sleep(0.1)

    def committed(self, phase=None):
        phases = [phase] if phase else list(PHASE_CEILINGS)
        total = sum((Decimal(self.state["phases"][p]["settled"]) + Decimal(self.state["phases"][p]["retained"]) for p in phases), Decimal(0))
        total += sum((Decimal(i["amount"]) for i in self.state["inflight"].values() if phase in (None, i["phase"])), Decimal(0))
        return total

    def reserve_wave(self, keys):
        with self.lock:
            if self.state["inflight"]:
                raise BudgetExceeded("previous wave has unsettled requests")
            if len(set(keys)) != len(keys):
                raise ValueError("duplicate request keys")
            need = self.reservation * len(keys)
            if self.committed() + need > TOTAL_CEILING or self.committed(self.phase) + need > PHASE_CEILINGS[self.phase]:
                raise BudgetExceeded(f"wave of {len(keys)} requests would exceed the {self.phase} or total ceiling")
            for key in keys:
                self.state["inflight"][key] = {"phase": self.phase, "amount": str(self.reservation)}
            self._save()
            return str(need)

    def _close(self, key):
        item = self.state["inflight"].pop(key)
        return self.state["phases"][item["phase"]]

    def settle(self, key, usage):
        cost = usage_cost(usage)
        with self.lock:
            if cost > self.reservation:
                raise BudgetExceeded("charge exceeds reservation")
            bucket = self._close(key)
            bucket["settled"] = str(Decimal(bucket["settled"]) + cost)
            bucket["requests"] += 1
            self._save()
        return cost

    def fail(self, key):
        with self.lock:
            bucket = self._close(key)
            bucket["retained"] = str(Decimal(bucket["retained"]) + self.reservation)
            bucket["requests"] += 1
            self._save()
        return self.reservation

    def release(self, key):
        with self.lock:
            self._close(key)
            self._save()
        return Decimal(0)

    def outstanding(self):
        return len(self.state["inflight"])

    def summary(self):
        return {"phases": self.state["phases"], "committed_total_usd": str(self.committed()), "recovered_crash_reservations": self.recovered}
