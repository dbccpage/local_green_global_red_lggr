"""Synthetic shared dispatch workspace and conventional admission checks."""
from copy import deepcopy
import json
import random
import sqlite3

from lggr.streaming import StreamingAuditMonitor, StreamingFiberMonitor
from lggr.witnesses import BudgetPolicy, StateRef, make_witness


def fixture(seed):
    rng = random.Random(seed)
    slots = [f"slot-{i}" for i in range(8)]
    jobs = []
    for i in range(5):
        jobs.append({"id": f"worker-{i}", "items": [
            {"unit_cents": rng.randrange(11, 150), "quantity": rng.randrange(1, 5)} for _ in range(6)],
            "allowed_slots": sorted(rng.sample(slots, 5))})
    return {"seed": seed, "epoch": 0, "slots": slots, "active_slots": slots.copy(),
            "jobs": jobs, "proposals": {}, "completed": {}}


def local_ok(job, proposal):
    return (isinstance(proposal, dict) and type(proposal.get("epoch")) is int
            and type(proposal.get("total_cents")) is int
            and proposal["total_cents"] == sum(x["unit_cents"] * x["quantity"] for x in job["items"])
            and proposal.get("slot") in job["allowed_slots"])


def findings(state):
    result, used = [], {}
    for job in state["jobs"]:
        jid = job["id"]
        p = state["completed"].get(jid) or state["proposals"].get(jid)
        if not local_ok(job, p):
            result.append({"code": "LOCAL_INVALID_OR_MISSING", "worker": jid})
            continue
        if jid not in state["completed"] and p["epoch"] != state["epoch"]:
            result.append({"code": "STALE_EPOCH", "worker": jid, "observed": p["epoch"], "required": state["epoch"]})
        if p["slot"] not in state["active_slots"]:
            result.append({"code": "RESOURCE_UNAVAILABLE", "worker": jid, "slot": p["slot"]})
        if p["slot"] in used:
            result.append({"code": "RESOURCE_COLLISION", "workers": [used[p["slot"]], jid], "slot": p["slot"]})
        used[p["slot"]] = jid
    return result


def certificates(before, state):
    fiber = StreamingFiberMonitor(scope_id="live-dispatch-local-report")
    for name, snap in (("before", before), ("current", state)):
        bits = [local_ok(j, snap["completed"].get(j["id"]) or snap["proposals"].get(j["id"])) for j in snap["jobs"]]
        fiber.observe(name, {"local_checks": bits}, {"global_admissible": not findings(snap)})
    budgets = []
    for slot in state["slots"]:
        policy = BudgetPolicy(allowed_states=tuple(range(6)), max_step=1,
                              max_total=int(slot in state["active_slots"]), query_scope="endpoint")
        mon = StreamingAuditMonitor(policy)
        count = 0
        for i, job in enumerate(state["jobs"]):
            p = state["completed"].get(job["id"]) or state["proposals"].get(job["id"], {})
            nxt = count + int(p.get("slot") == slot)
            mon.step(make_witness(policy, StateRef(f"s{i}", count), StateRef(f"s{i+1}", nxt), witness_id=f"{slot}-{i}"))
            count = nxt
        receipt = mon.get_receipt()
        if count > int(slot in state["active_slots"]):
            budgets.append({"slot": slot, "receipt": receipt})
    return {"fiber": fiber.get_receipt(), "resource_budget_obstructions": budgets}


class Board:
    """Only host-validated proposals become actual SQLite dispatch rows."""
    def __init__(self, state, path=":memory:"):
        self.state = deepcopy(state)
        self.db = sqlite3.connect(str(path))
        self.db.execute("CREATE TABLE IF NOT EXISTS dispatch(worker TEXT PRIMARY KEY, slot TEXT UNIQUE, total_cents INTEGER, epoch INTEGER)")
        for worker, p in self.state["completed"].items():
            self.db.execute("INSERT INTO dispatch VALUES(?,?,?,?)", (worker, p["slot"], p["total_cents"], p["epoch"]))
        self.db.commit()

    def tool(self, worker, name, arguments):
        job = next(j for j in self.state["jobs"] if j["id"] == worker)
        if name == "inspect_board" and arguments == {}:
            return deepcopy(self.state)
        if name == "calculate_total":
            items = arguments.get("items")
            if set(arguments) != {"items"} or not isinstance(items, list) or not 1 <= len(items) <= 20:
                return {"accepted": False, "error": "provide 1 to 20 line items"}
            if any(not isinstance(item, dict) or set(item) != {"unit_cents", "quantity"}
                   or any(type(v) is not int or not 0 <= v <= 100000 for v in item.values()) for item in items):
                return {"accepted": False, "error": "bounded exact integer line items required"}
            return {"value": sum(item["unit_cents"] * item["quantity"] for item in items),
                    "scope": "arithmetic on supplied items only; no resource assignment"}
        if name == "escalate" and set(arguments) == {"reason"} and isinstance(arguments["reason"], str):
            return {"escalated": True, "reason": arguments["reason"][:1000]}
        if name != "propose" or set(arguments) != {"slot", "total_cents", "epoch"}:
            return {"accepted": False, "error": "unsupported tool or fields"}
        if worker in self.state["completed"]:
            return {"accepted": False, "error": "completed work is immutable"}
        if not local_ok(job, arguments):
            return {"accepted": False, "error": "own invoice arithmetic, allowed slot, or exact integer types failed; recompute from source items"}
        self.state["proposals"][worker] = deepcopy(arguments)
        return {"accepted": True, "scope": "local proposal only; global admission is separate"}

    def execute(self, workers):
        errors = findings(self.state)
        if errors:
            return {"executed": False, "findings": errors}
        with self.db:
            for worker in workers:
                if worker in self.state["completed"]:
                    raise ValueError("cannot execute a job twice")
                p = self.state["proposals"][worker]
                self.db.execute("INSERT INTO dispatch VALUES(?,?,?,?)", (worker, p["slot"], p["total_cents"], p["epoch"]))
        for worker in workers:
            self.state["completed"][worker] = deepcopy(self.state["proposals"][worker])
        return {"executed": True, "workers": list(workers), "rows": self.rows()}

    def rows(self):
        return [dict(zip(("worker", "slot", "total_cents", "epoch"), r)) for r in
                self.db.execute("SELECT worker,slot,total_cents,epoch FROM dispatch ORDER BY worker")]

    def close(self):
        self.db.close()
