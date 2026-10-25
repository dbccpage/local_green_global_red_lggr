"""Independent exhaustive feasibility and output judge. Never supplies a repair."""

def feasible(state):
    occupied = {p["slot"] for p in state["completed"].values()}
    choices = [set(job["allowed_slots"]) & set(state["active_slots"]) - occupied
               for job in state["jobs"] if job["id"] not in state["completed"]]
    def search(todo, taken):
        if not todo:
            return True
        return any(search(todo[1:], taken | {slot}) for slot in todo[0] - taken)
    return search(sorted(choices, key=len), set())


def judge(state, rows, preserved_rows):
    errors, seen_workers, seen_slots = [], set(), set()
    jobs = {j["id"]: j for j in state["jobs"]}
    for row in rows:
        worker, slot = row["worker"], row["slot"]
        if worker not in jobs or worker in seen_workers:
            errors.append("unknown or duplicate worker")
            continue
        job = jobs[worker]
        expected = 0
        for item in job["items"]:
            for _ in range(item["quantity"]):
                expected += item["unit_cents"]
        if type(row["total_cents"]) is not int or row["total_cents"] != expected:
            errors.append("incorrect invoice")
        if slot not in job["allowed_slots"] or slot not in state["active_slots"] or slot in seen_slots:
            errors.append("invalid resource assignment")
        if worker not in {r["worker"] for r in preserved_rows} and row["epoch"] != state["epoch"]:
            errors.append("stale execution")
        seen_slots.add(slot)
        seen_workers.add(worker)
    current = {r["worker"]: r for r in rows}
    if any(current.get(r["worker"]) != r for r in preserved_rows):
        errors.append("completed output changed")
    return {"valid_execution": not errors, "complete": not errors and seen_workers == set(jobs),
            "completed_jobs": len(seen_workers), "errors": errors, "feasible": feasible(state)}
