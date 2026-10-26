"""Frozen analysis: co-primary P1/P2 with Holm, family-stratified cluster bootstrap, secondaries, power.

python -m experiments.lggr_rsi_swarm.analyze results EVIDENCE_DIR   -> RESULTS.json (+ printed summary)
python -m experiments.lggr_rsi_swarm.analyze power DEV_RUN_DIR     -> power simulation (recorded before evaluation)
"""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import json
from pathlib import Path
import random

import numpy as np

from ._path import ROOT  # noqa: F401
from .generate import FAMILIES, build
from swarm.domain import local_report
from swarm.evidence_access import Gateway
from swarm.grading import classify
from swarm.hashing import load_events
from swarm.selectors import Space, acquire

HERE = Path(__file__).resolve().parent
RESAMPLES, SEED, ALPHA, MARGIN = 10000, 20261026, 0.05, 0.10


def cluster_bootstrap(rows, resamples=RESAMPLES, seed=SEED):
    """rows: list of (instance, family, diff). Returns estimate, CI, two-sided percentile p."""
    by_family = defaultdict(lambda: defaultdict(list))
    for inst, fam, diff in rows:
        by_family[fam][inst].append(diff)
    estimate = float(np.mean([d for _, _, d in rows])) if rows else float("nan")
    rng = np.random.default_rng(seed)
    families = []
    for fam in sorted(by_family):
        clusters = [by_family[fam][i] for i in sorted(by_family[fam])]
        families.append((np.array([sum(c) for c in clusters], float), np.array([len(c) for c in clusters], float)))
    stats = np.empty(resamples)
    for b in range(resamples):
        total, count = 0.0, 0.0
        for sums, sizes in families:
            idx = rng.integers(0, len(sums), len(sums))
            total += sums[idx].sum()
            count += sizes[idx].sum()
        stats[b] = total / count
    lo, hi = np.percentile(stats, [2.5, 97.5])
    p = min(1.0, 2 * min((stats <= 0).mean(), (stats >= 0).mean()))
    return {"estimate": estimate, "ci95": [float(lo), float(hi)], "p_two_sided": float(p), "n_rows": len(rows),
            "n_clusters": int(sum(len(s) for s, _ in families)), "resamples": resamples}


def holm(pvalues, alpha=ALPHA):
    order = sorted(pvalues, key=lambda k: pvalues[k])
    out, stop = {}, False
    for rank, key in enumerate(order):
        threshold = alpha / (len(order) - rank)
        reject = not stop and pvalues[key] <= threshold
        stop = stop or not reject
        out[key] = {"p": pvalues[key], "threshold": threshold, "significant": reject}
    return out


def interpret(result, significant):
    lo, hi = result["ci95"]
    if significant and result["estimate"] > 0:
        return "benefit"
    if significant and result["estimate"] < 0:
        return "disadvantage"
    if -MARGIN < lo and hi < MARGIN:
        return "practical_equivalence"
    return "inconclusive"


def load_summaries(evidence):
    swarm, rsi = [], []
    for path in sorted(Path(evidence).glob("*/summary.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        (swarm if data["part"] == "swarm" else rsi).append(data)
    return swarm, rsi


def charges(evidence):
    """USD charged per request key prefix category, from events."""
    by_cat = Counter()
    total = Decimal(0)
    for path in sorted(Path(evidence).glob("*/events.jsonl*")):
        for r in load_events(path):
            if r["kind"] == "response":
                key, usd = r["data"]["key"], Decimal(r["data"]["charged_usd"])
                total += usd
                parts = key.split("/")
                cat = ("repair" if "/rep" in key else "controller-" + key.split("/ctl-")[1].split("/")[0] if "/ctl-" in key
                       else "rsi-" + parts[2].split("-")[1] if "/rsi-" in key else "proposal")
                by_cat[cat] += usd
    return {k: str(v) for k, v in by_cat.items()}, str(total)


def rate(items, pred):
    items = list(items)
    return {"n": len(items), "k": sum(1 for x in items if pred(x)), "rate": (sum(1 for x in items if pred(x)) / len(items)) if items else None}


def results(evidence):
    swarm, rsi = load_summaries(evidence)
    offline = [o for s in swarm for o in s["offline"]]
    ctl = [c for s in swarm for c in s["controllers"]]
    repair = [r for s in swarm for r in s["repair"]]
    rsi_rows = [r for s in rsi for r in s["rsi"]]
    p1 = [(o["instance"], o["family"], int(o["arms"]["C@4"]["class"] == "correct") - int(o["arms"]["B@4"]["class"] == "correct")) for o in offline]
    by = defaultdict(dict)
    for c in ctl:
        by[(c["instance"], c["draw"])][c["arm"]] = c
    p2 = [(i, v["L-C"]["family"], int(v["L-C"]["class"] == "correct") - int(v["L-B"]["class"] == "correct"))
          for (i, d), v in sorted(by.items()) if "L-C" in v and "L-B" in v]
    primary = {"P1": cluster_bootstrap(p1), "P2": cluster_bootstrap(p2)}
    adjusted = holm({k: v["p_two_sided"] for k, v in primary.items()})
    for k in primary:
        primary[k]["holm"] = adjusted[k]
        primary[k]["interpretation"] = interpret(primary[k], adjusted[k]["significant"])
    if primary["P1"]["interpretation"] == "benefit" and primary["P2"]["interpretation"] == "practical_equivalence":
        primary["P2"]["interpretation"] = "absorbed_by_agent"

    offline_table = {}
    for arm in ["A"] + [f"{a}@{b}" for a in ["B", "C", "round_robin", "recently_changed", "dependency_risk"] for b in [1, 2, 4, 8]]:
        rows = [o["arms"][arm] for o in offline]
        offline_table[arm] = {cls: sum(r["class"] == cls for r in rows) for cls in ["correct", "false_accept", "false_reject", "defer", "false_mismatch"]}
        offline_table[arm]["n"] = len(rows)
        spent = [r.get("units_to_resolve") for r in rows if r.get("units_to_resolve") is not None]
        offline_table[arm]["mean_units_to_resolve"] = float(np.mean(spent)) if spent else None
    strata = {}
    for key, pred in {"family": lambda o: o["family"], "control": lambda o: o["control"], "distractor": lambda o: o.get("distractor", False),
                      "initially_resolved": lambda o: o["initial_host_rule"] != "defer"}.items():
        groups = defaultdict(list)
        for o in offline:
            groups[str(pred(o))].append(int(o["arms"]["C@4"]["class"] == "correct") - int(o["arms"]["B@4"]["class"] == "correct"))
        strata[key] = {g: {"n": len(v), "mean_C_minus_B": float(np.mean(v))} for g, v in sorted(groups.items())}
    controller_table = {}
    for arm in ["L-0", "L-B", "L-C"]:
        rows = [c for c in ctl if c["arm"] == arm]
        controller_table[arm] = {
            "n": len(rows),
            "agent": {cls: sum(r["class"] == cls for r in rows) for cls in ["correct", "false_accept", "false_reject", "defer", "false_mismatch"]},
            "host_rule_on_agent_evidence": {cls: sum(r["host_class"] == cls for r in rows) for cls in ["correct", "false_accept", "false_reject", "defer", "false_mismatch"]},
            "agreement": rate(rows, lambda r: r["agreement"]),
            "compliance": rate([r for r in rows if r["complied"] is not None], lambda r: r["complied"]),
            "mean_units_spent": float(np.mean([r["spent"] for r in rows])) if rows else None,
            "mean_turns": float(np.mean([r["turns"] for r in rows])) if rows else None,
            "denied_tool_calls": sum(r["denied"] for r in rows),
            "failures": sum(bool(r["failure"]) for r in rows),
        }
    repair_table = {}
    for arm in ["L-B", "L-C"]:
        rows = [r for r in repair if r["arm"] == arm]
        repair_table[arm] = {"n": len(rows), "repaired_system_passes": rate(rows, lambda r: r["grader"]["system_passes"]),
                             "passed_before": rate(rows, lambda r: r["before"]),
                             "controller_correct": rate(rows, lambda r: r["controller"]["class"] == "correct"),
                             "controller_false_accept": rate(rows, lambda r: r["controller"]["class"] == "false_accept")}
    rsi_table = {}
    for arm in ["C", "D"]:
        rows = [r for r in rsi_rows if r["arm"] == arm]
        rsi_table[arm] = {"n": len(rows), "v2_system_passes": rate(rows, lambda r: r["grader"]["system_passes"]),
                          "v2_local_green": rate(rows, lambda r: r["grader"]["local_green"]),
                          "learn_final_passes": rate(rows, lambda r: r["learn_final"]["system_passes"]),
                          "mean_memory_records": float(np.mean([len(r["memory"]["records"]) for r in rows])) if rows else None,
                          "mean_obligations": float(np.mean([len(r["memory"]["obligations"]) for r in rows])) if rows else None}
    by_cat, total = charges(evidence)
    correct_ctl = {arm: controller_table[arm]["agent"]["correct"] for arm in controller_table}
    cost_per_correct = {arm: (str(Decimal(by_cat.get("controller-" + arm, "0")) / correct_ctl[arm]) if correct_ctl[arm] else None)
                        for arm in correct_ctl}
    return {"schema": "lggr.rsi_swarm.results.v1", "primary": primary, "offline": offline_table, "p1_strata": strata,
            "controllers": controller_table, "repair": repair_table, "rsi": rsi_table, "charges_usd": by_cat, "total_charged_usd": total,
            "controller_cost_per_correct_usd": cost_per_correct, "n_offline": len(offline), "n_controllers": len(ctl)}


def simulate_p1(n_instances=400, draws=3, seed=7001):
    """Offline P1 simulation on fresh (non-evaluation) generator seeds with a sensible-agent snapshot model."""
    rng = random.Random(seed)
    rows = []
    for i in range(n_instances):
        fam = FAMILIES[i % 4]
        slot = i // 4 % 100
        control = "clean" if slot < 80 else "malformed" if slot < 90 else "out_of_model"
        inst = build(700000 + i, "simulation", fam, control)
        for _ in range(draws):
            files, t, lat = {}, 0, rng.choice([0, 1, 2])
            for m in inst["modules"]:
                options = []
                for _ in range(400):
                    vals = {p: rng.randint(s["lo"], min(s["hi"], s["lo"] + 50)) for p, s in m["params"].items()}
                    vals.update({p: s["hi"] for p, s in m["params"].items() if p in ("buffer", "accept_hi", "timeout") and rng.random() < 0.7})
                    content = "\n".join(f"{k} = {v}" for k, v in vals.items())
                    if local_report(inst, m, {m["file"]: content})["pass"]:
                        options.append(vals)
                vals = dict(rng.choice(options)) if options else {p: s["lo"] for p, s in m["params"].items()}
                if "start" in vals:
                    vals["start"], t = t, t + vals["ticks"] + lat
                files[m["file"]] = "\n".join(f"{k} = {v}" for k, v in vals.items())
            space = Space(inst, files)
            from swarm.domain import target
            want = target(inst, files)
            res = {arm: acquire(arm, space, Gateway(inst, files, 4).run, 4)["decision"] for arm in ("B", "C")}
            rows.append((inst["id"], fam, int(res["C"] == want) - int(res["B"] == want)))
    return rows


def power(dev_dir=None, sims=400, seed=11):
    """Power at alpha 0.025 (Holm first step) for P1 (offline simulation) and P2 (effect grid)."""
    rows = simulate_p1()
    p1 = cluster_bootstrap(rows, resamples=2000)
    # Resample-based power: draw instance clusters with replacement, test with a normal cluster approximation.
    rng = np.random.default_rng(seed)
    clusters = defaultdict(list)
    for inst, fam, d in rows:
        clusters[inst].append(d)
    sums = np.array([sum(v) for v in clusters.values()], float)
    sizes = np.array([len(v) for v in clusters.values()], float)
    hits = 0
    for _ in range(sims):
        idx = rng.integers(0, len(sums), len(sums))
        s, n = sums[idx], sizes[idx]
        mean = s.sum() / n.sum()
        resid = s - mean * n
        se = np.sqrt((resid ** 2).sum()) / n.sum()
        hits += abs(mean / se) > 2.2414 if se > 0 else mean != 0
    p2_grid = {}
    for effect in (0.03, 0.05, 0.08, 0.10):
        for discord in (0.2, 0.4):
            hits2 = 0
            for _ in range(sims):
                d = []
                for i in range(400):
                    shared = rng.random()
                    for _ in range(3):
                        u = 0.5 * shared + 0.5 * rng.random()
                        d.append(1 if u < discord / 2 + effect / 2 else -1 if u > 1 - (discord / 2 - effect / 2) else 0)
                arr = np.array(d, float).reshape(400, 3)
                s = arr.sum(1)
                mean = s.sum() / arr.size
                se = np.sqrt(((s - mean * 3) ** 2).sum()) / arr.size
                hits2 += abs(mean / se) > 2.2414 if se > 0 else 0
            p2_grid[f"effect={effect},discordance={discord}"] = hits2 / sims
    return {"alpha": 0.025, "P1_simulated": {"estimate": p1["estimate"], "ci95": p1["ci95"], "power": hits / sims,
                                             "model": "sensible-agent snapshots on fresh generator seeds 700000+"},
            "P2_grid": p2_grid, "note": "P2 power depends on live agent behaviour; grid over effect size and discordance, "
                                        "within-instance correlation 0.5."}


def sensitivity(evaluation, sensitivity_dir):
    """Recompute P1/P2 and repair outcomes with cap-affected cases replaced by their higher-cap reruns."""
    swarm, _ = load_summaries(evaluation)
    sens = json.loads((Path(sensitivity_dir) / "summary.json").read_text(encoding="utf-8"))
    replaced = {(o["instance"], o["draw"]) for o in sens["offline"]}

    def merge(field):
        rows = [x for s in swarm for x in s[field] if (x["instance"], x["draw"]) not in replaced]
        return rows + list(sens[field])
    offline, ctl, repair = merge("offline"), merge("controllers"), merge("repair")
    p1 = [(o["instance"], o["family"], int(o["arms"]["C@4"]["class"] == "correct") - int(o["arms"]["B@4"]["class"] == "correct")) for o in offline]
    by = defaultdict(dict)
    for c in ctl:
        by[(c["instance"], c["draw"])][c["arm"]] = c
    p2 = [(i, v["L-C"]["family"], int(v["L-C"]["class"] == "correct") - int(v["L-B"]["class"] == "correct"))
          for (i, d), v in sorted(by.items()) if "L-C" in v and "L-B" in v]
    affected_only = [r for r in p1 if any(r[0] == i for i, _ in replaced)]
    primary_affected = [(o["instance"], o["family"], int(o["arms"]["C@4"]["class"] == "correct") - int(o["arms"]["B@4"]["class"] == "correct"))
                        for s in swarm for o in s["offline"] if (o["instance"], o["draw"]) in replaced]
    return {"replaced_cases": len(replaced), "P1": cluster_bootstrap(p1), "P2": cluster_bootstrap(p2),
            "P1_affected_cases_primary_mean": float(np.mean([d for _, _, d in primary_affected])) if primary_affected else None,
            "P1_affected_cases_rerun_mean": float(np.mean([int(o["arms"]["C@4"]["class"] == "correct") - int(o["arms"]["B@4"]["class"] == "correct") for o in sens["offline"]])),
            "controller_failures": {arm: sum(bool(c["failure"]) for c in ctl if c["arm"] == arm) for arm in ("L-0", "L-B", "L-C")},
            "controller_correct": {arm: rate([c for c in ctl if c["arm"] == arm], lambda c: c["class"] == "correct") for arm in ("L-0", "L-B", "L-C")},
            "repair": {arm: {"repaired_system_passes": rate([r for r in repair if r["arm"] == arm], lambda r: r["grader"]["system_passes"]),
                             "controller_correct": rate([r for r in repair if r["arm"] == arm], lambda r: r["controller"]["class"] == "correct")}
                       for arm in ("L-B", "L-C")},
            "n_affected_rows_in_p1": len(affected_only)}


def category(key):
    if "/rsi-" in key:
        return "rsi"
    if "/rep" in key:
        return "repair-controller" if "/ctl/" in key else "repair-wave"
    if "/ctl-" in key:
        return "controller"
    return "proposal"


def devstats(paths):
    """Measured per-request cost, tokens, cache use and failures by request category."""
    stats = defaultdict(lambda: Counter())
    failures = Counter()
    for path in paths:
        for r in load_events(path):
            if r["kind"] == "request":
                stats[category(r["data"]["key"])]["max_count"] = max(stats[category(r["data"]["key"])]["max_count"], r["data"]["count"] or 0)
            if r["kind"] != "response":
                continue
            d = r["data"]
            s = stats[category(d["key"])]
            s["requests"] += 1
            s["usd_micro"] += int(Decimal(d["charged_usd"]) * 10 ** 6)
            if d["failure"]:
                failures[(category(d["key"]), d["failure"].get("kind"))] += 1
            if d["body"]:
                u = d["body"]["usage"]
                for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
                    s[k] += u.get(k) or 0
    out = {}
    for cat, s in stats.items():
        n = s["requests"]
        inp = s["input_tokens"] + s["cache_creation_input_tokens"] + s["cache_read_input_tokens"]
        out[cat] = {"requests": n, "usd": s["usd_micro"] / 1e6, "usd_per_request": s["usd_micro"] / 1e6 / n if n else None,
                    "mean_prompt_tokens": inp / n if n else None, "mean_output_tokens": s["output_tokens"] / n if n else None,
                    "cache_read_share": s["cache_read_input_tokens"] / inp if inp else None, "max_counted_input": s["max_count"]}
    return {"by_category": out, "failures": {f"{a}:{b}": v for (a, b), v in failures.items()}}


def project(dev, turns=None):
    """Project evaluation spend from measured per-request costs and the frozen design's request counts."""
    c = dev["by_category"]
    per = {k: v["usd_per_request"] for k, v in c.items()}
    ctl_turns = turns or 4.0
    counts = {"proposal": 400 * 3 * 5 * 2,
              "controller": (400 * 3 * 2 + 100 * 3) * ctl_turns,
              "repair-wave": 60 * 3 * 2 * 5 * 2,
              "repair-controller": 60 * 3 * 2 * ctl_turns,
              "rsi": 30 * 3 * 2 * 3 * 2 * 5}
    usd = {k: counts[k] * (per.get(k) or per.get("controller") or max(p for p in per.values() if p)) for k in counts}
    return {"requests": counts, "usd": usd, "total_usd": sum(usd.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["results", "power", "devstats", "sensitivity"])
    parser.add_argument("path", nargs="?")
    parser.add_argument("--out")
    parser.add_argument("--sensitivity-dir")
    args = parser.parse_args()
    if args.mode == "sensitivity":
        out = sensitivity(args.path, args.sensitivity_dir)
    elif args.mode == "devstats":
        stats = devstats(sorted(Path(args.path).glob("*/events.jsonl*")))
        out = {"dev": stats, "projection": project(stats)}
    else:
        out = power(args.path) if args.mode == "power" else results(args.path)
    text = json.dumps(out, indent=1, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
