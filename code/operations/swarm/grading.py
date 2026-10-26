"""Blind grader (full 16-unit verification) and decision scoring.

The grader is the only component besides evidence_access that reads hidden truth.
It is run after a phase's snapshot is frozen and its output is never sent to an
agent except in the RSI learn-phase postmortem, which the protocol specifies.
"""
from .domain import holds, local_green, local_report, snapshot_values, target

FULL_VERIFICATION_UNITS = 16


def full_verification(instance, files):
    x, _ = snapshot_values(instance, files)
    truth = instance["truth"]
    glob = {c["id"]: holds(c, x, truth) for c in instance["global"]}
    local = {m["name"]: local_report(instance, m, files)["pass"] for m in instance["modules"]}
    passes = all(local.values()) and all(glob.values())
    return {"units": FULL_VERIFICATION_UNITS, "local": local, "global": glob, "system_passes": passes,
            "local_green": local_green(instance, files), "target": target(instance, files)}


def classify(decision, wanted):
    if decision == wanted:
        return "correct"
    if decision == "defer":
        return "defer"
    if decision == "accept":
        return "false_accept"
    if decision == "reject":
        return "false_reject"
    return "false_mismatch"


def correct(decision, wanted):
    return decision == wanted
