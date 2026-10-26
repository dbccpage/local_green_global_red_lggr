"""Deterministic generator for LGGR/RSI swarm instances, subsets and arm orders.

Run `python -m experiments.lggr_rsi_swarm.generate` to (re)write instances.json and
print its digest. The digest is recorded in every run's start event.
"""
from copy import deepcopy
import json
from pathlib import Path
import random

from ._path import swarm  # noqa: F401  (adds code/operations to sys.path)
from swarm.domain import hypotheses, constraint_names
from swarm.hashing import digest

HERE = Path(__file__).resolve().parent
FAMILIES = ["allocation", "temporal", "interface", "combined"]
EVAL_SEEDS = list(range(500000, 500400))
DEV_SEEDS = list(range(900000, 900008))
N_CHECKS = 16
MAX_HYPOTHESES = 216


def X(module, param):
    return {"x": f"{module}.{param}"}


def T(name):
    return {"t": name}


def add(*a):
    return {"+": list(a)}


def mul(*a):
    return {"*": list(a)}


def C(cid, lhs, op, rhs, text):
    return {"id": cid, "lhs": lhs, "op": op, "rhs": rhs, "text": text}


def module(name, owner, params, local):
    return {"name": name, "owner": owner, "file": f"modules/{name}.cfg", "params": params, "local": local}


def P(lo, hi, text):
    return {"lo": lo, "hi": hi, "text": text}


def H(name, domain, text):
    return {"name": name, "domain": list(domain), "text": text}


DISTRACTOR = {"allocation": H("zone", [0, 1, 2], "availability-zone id assigned to the pool by operations"),
              "temporal": H("region", [0, 1, 2], "region id of the scheduler host"),
              "interface": H("codec", [0, 1, 2], "codec revision tag reported by the router"),
              "combined": H("rack", [0, 1, 2], "rack id of the worker pool")}


def draw_params(family, rng):
    if family == "allocation":
        return {"d": [rng.randint(4, 9) for _ in range(3)], "shift": rng.choice([-1, 0, 1])}
    if family == "temporal":
        return {"w": [rng.randint(6, 14) for _ in range(3)], "shift": rng.choice([-1, 0, 1])}
    if family == "interface":
        return {"n": rng.randint(3, 6), "shift": rng.choice([0, 1])}
    return {"d": [rng.randint(4, 8) for _ in range(3)], "k": [rng.randint(2, 4) for _ in range(3)], "shift": rng.choice([-1, 0, 1])}


def build_family(family, p):
    owners = ["impl-0", "impl-1", "impl-2"]
    if family == "allocation":
        names, d, s = ["ingest", "transform", "export"], p["d"], p["shift"]
        mods = [module(n, o, {"reserve": P(1, 15, "pool units reserved per replica"),
                              "replicas": P(1, 3, "number of replicas")},
                       [C("L1", mul(X(n, "reserve"), X(n, "replicas")), ">=", d[i], f"cover demand {d[i]}"),
                        C("L2", mul(X(n, "reserve"), X(n, "replicas")), "<=", d[i] + 3, "no hoarding beyond demand+3")])
                for i, (n, o) in enumerate(zip(names, owners))]
        S, M = sum(d), max(d)
        hidden = [H("cap", [S + 1 + s, S + 4 + s, S + 7 + s], "shared pool capacity in units"),
                  H("ovh", [0, 1, 2], "runtime overhead units added to every replica"),
                  H("node", [M - 1, M + 1, M + 3], "largest single-replica footprint a node accepts")]
        glob = [C("G1", add(*[mul(add(X(n, "reserve"), T("ovh")), X(n, "replicas")) for n in names]), "<=", T("cap"),
                  "total footprint including per-replica overhead fits the pool"),
                C("G2", add({"max": [X(n, "reserve") for n in names]}, T("ovh")), "<=", T("node"),
                  "every replica (reserve + overhead) fits on one node")]
    elif family == "temporal":
        names, w, s = ["plan", "build", "ship"], p["w"], p["shift"]
        mods = []
        for i, (n, o) in enumerate(zip(names, owners)):
            local = [C("L1", mul(X(n, "rate"), X(n, "ticks")), ">=", w[i], f"complete work {w[i]}"),
                     C("L2", mul(X(n, "rate"), X(n, "ticks")), "<=", w[i] + 2, "spend at most work+2")]
            if i == 0:
                local.append(C("L3", X(n, "start"), "<=", 2, "the first stage starts by tick 2"))
            mods.append(module(n, o, {"start": P(0, 30, "start tick"), "ticks": P(1, 6, "duration in ticks"),
                                      "rate": P(1, 8, "budget units drawn per tick")}, local))
        spend = [mul(X(n, "rate"), X(n, "ticks")) for n in names]
        deadline = sum((wi + 3) // 4 for wi in w) + 3
        hidden = [H("base", [w[0] + s, w[0] + 2 + s, w[0] + 4 + s], "budget available at stage 1"),
                  H("refill", [w[1] - 1, w[1] + 1, w[1] + 3], "budget added at each later stage"),
                  H("lat", [0, 1, 2], "handoff latency in ticks between stages"),
                  H("setup", [0, 1], "setup cost charged per stage")]
        glob = [C("P1", add(spend[0], T("setup")), "<=", T("base"), "stage-1 prefix within budget"),
                C("P2", add(spend[0], spend[1], mul(2, T("setup"))), "<=", add(T("base"), T("refill")), "stage-2 prefix within budget"),
                C("P3", add(*spend, mul(3, T("setup"))), "<=", add(T("base"), mul(2, T("refill"))), "stage-3 prefix within budget"),
                C("O1", X("build", "start"), ">=", add(X("plan", "start"), X("plan", "ticks"), T("lat")), "build starts after plan hands off"),
                C("O2", X("ship", "start"), ">=", add(X("build", "start"), X("build", "ticks"), T("lat")), "ship starts after build hands off"),
                C("D1", add(X("ship", "start"), X("ship", "ticks"), T("lat")), "<=", deadline, f"delivered by tick {deadline}")]
    elif family == "interface":
        names, n, s = ["producer", "router", "consumer"], p["n"], p["shift"]
        mods = [module("producer", "impl-0", {"batch": P(1, 40, "items per emitted batch")},
                       [C("L1", X("producer", "batch"), ">=", n, f"emit at least {n} items per batch"),
                        C("L2", X("producer", "batch"), "<=", n + 3, "batch at most demand+3")]),
                module("router", "impl-1", {"buffer": P(1, 500, "router buffer slots")},
                       [C("L1", X("router", "buffer"), "<=", 10 * n + 6 + s, "router memory limit")]),
                module("consumer", "impl-2", {"accept_hi": P(1, 500, "upper bound of accepted elements"),
                                              "timeout": P(1, 40, "processing timeout in ticks")},
                       [C("L1", X("consumer", "accept_hi"), "<=", 10 * n + 8 + s, "consumer memory limit"),
                        C("L2", X("consumer", "timeout"), "<=", 2 * n - 1 + s, "timeout service limit")])]
        hidden = [H("scale", [8, 10, 12], "elements per batch item after router conversion"),
                  H("jitter", [0, 1, 2, 3], "extra elements added by retransmission"),
                  H("incl", [0, 1], "1 if the consumer's upper bound is exclusive"),
                  H("lat", [1, 2], "consumer ticks per batch item")]
        load = add(mul(X("producer", "batch"), T("scale")), T("jitter"))
        glob = [C("I1", load, "<=", X("router", "buffer"), "router buffer holds a converted batch"),
                C("I2", add(load, T("incl")), "<=", X("consumer", "accept_hi"), "consumer accepts a converted batch"),
                C("I3", mul(T("lat"), X("producer", "batch")), "<=", X("consumer", "timeout"), "consumer finishes a batch before timeout")]
    else:
        names, d, k, s = ["ingest", "transform", "export"], p["d"], p["k"], p["shift"]
        mods = [module(nm, o, {"reserve": P(1, 12, "pool units reserved per replica"), "replicas": P(1, 3, "number of replicas"),
                               "start": P(0, 30, "start tick"), "ticks": P(1, 4, "duration in ticks")},
                       [C("L1", mul(X(nm, "reserve"), X(nm, "replicas")), ">=", d[i], f"cover demand {d[i]}"),
                        C("L2", mul(X(nm, "reserve"), X(nm, "replicas")), "<=", d[i] + 3, "no hoarding beyond demand+3"),
                        C("L3", mul(X(nm, "ticks"), X(nm, "replicas")), ">=", k[i] + 1, f"replica-ticks cover work {k[i] + 1}")])
                for i, (nm, o) in enumerate(zip(names, owners))]
        S = sum(d)
        deadline = sum(k) + 4
        hidden = [H("cap", [S + 2 + s, S + 5 + s, S + 8 + s], "shared pool capacity in units"),
                  H("ovh", [0, 1, 2], "runtime overhead units added to every replica"),
                  H("lat", [0, 1, 2], "handoff latency in ticks between stages")]
        glob = [C("G1", add(*[mul(add(X(nm, "reserve"), T("ovh")), X(nm, "replicas")) for nm in names]), "<=", T("cap"),
                  "total footprint including per-replica overhead fits the pool"),
                C("O1", X("transform", "start"), ">=", add(X("ingest", "start"), X("ingest", "ticks"), T("lat")), "transform starts after ingest hands off"),
                C("O2", X("export", "start"), ">=", add(X("transform", "start"), X("transform", "ticks"), T("lat")), "export starts after transform hands off"),
                C("D1", add(X("export", "start"), X("export", "ticks"), T("lat")), "<=", deadline, f"delivered by tick {deadline}")]
    return mods, hidden, glob


def make_checks(instance, rng):
    hidden = instance["hidden"]
    integ = []
    for c in instance["global"]:
        n_t = len(constraint_names(c, "t"))
        integ.append({"kind": "integration", "constraint": c["id"], "cost": 2 if n_t <= 1 else 4,
                      "text": f"integration test of {c['id']} against the frozen module files (pass/fail)"})
    measures = [{"kind": "measure", "param": h["name"], "cost": 2, "text": f"measure {h['name']} exactly in staging (returns the value)"}
                for h in hidden]
    probes, extra = [], []
    for h in hidden:
        thresholds = h["domain"][1:]
        mid = thresholds[(len(thresholds) - 1) // 2]
        for t in thresholds:
            item = {"kind": "probe", "param": h["name"], "threshold": t, "cost": 1,
                    "text": f"staging probe: is {h['name']} >= {t}? (yes/no)"}
            (probes if t == mid else extra).append(item)
    locals_ = [{"kind": "local", "module": m["name"], "cost": 1, "text": f"re-run {m['name']}'s local tests (pass/fail)"}
               for m in instance["modules"]]
    sums = []
    for i in range(len(hidden)):
        for j in range(i + 1, len(hidden)):
            a, b = hidden[i], hidden[j]
            t = (min(a["domain"]) + max(a["domain"]) + min(b["domain"]) + max(b["domain"]) + 1) // 2
            sums.append({"kind": "sum_probe", "params": [a["name"], b["name"]], "threshold": t, "cost": 2,
                         "text": f"combined probe: is {a['name']} + {b['name']} >= {t}? (yes/no)"})
    rng.shuffle(extra)
    rng.shuffle(sums)
    ordered = integ + measures + probes + locals_[:1] + extra + sums + locals_[1:]
    chosen = ordered[:N_CHECKS]
    if len(chosen) != N_CHECKS:
        raise ValueError("not enough checks")
    rng.shuffle(chosen)
    for index, check in enumerate(chosen, 1):
        check["id"] = f"K{index:02d}"
    return sorted(chosen, key=lambda c: c["id"])


def build(seed, split, family, control, overrides=None):
    rng = random.Random(seed)
    params = draw_params(family, rng)
    if overrides:
        params = overrides(deepcopy(params))
    mods, hidden, glob = build_family(family, params)
    distractor = rng.random() < 0.5
    if distractor:
        hidden.append(deepcopy(DISTRACTOR[family]))
    instance = {"id": f"{split[:3]}-{seed}", "seed": seed, "split": split, "family": family, "control": control,
                "params": params, "distractor": distractor, "modules": mods, "hidden": hidden, "global": glob}
    if len(hypotheses(instance)) > MAX_HYPOTHESES:
        raise ValueError("hypothesis space too large")
    instance["checks"] = make_checks(instance, rng)
    truth = {h["name"]: rng.choice(h["domain"]) for h in hidden}
    malformed = []
    if control == "out_of_model":
        used = [h for h in hidden if any(h["name"] in constraint_names(c, "t") for c in glob)]
        h = rng.choice(used)
        step = h["domain"][-1] - h["domain"][-2]
        truth[h["name"]] = h["domain"][-1] + step
    elif control == "malformed":
        informative = [c["id"] for c in instance["checks"] if c["kind"] != "local"]
        malformed = sorted(rng.sample(informative, rng.choice([1, 2])))
    instance["truth"] = truth
    instance["malformed"] = malformed
    instance["arm_seed"] = rng.randrange(2 ** 31)
    return instance


def v2_overrides(family):
    """RSI contract revision: one demand rises by one and the stage-1/pool capacity domain drops one step."""
    def change(p):
        if family in ("allocation", "combined"):
            p["d"][1] += 1
            p["shift"] -= 1
        elif family == "temporal":
            p["w"][1] += 1
            p["shift"] -= 1
        else:
            p["n"] += 1
            p["shift"] -= 1
        return p
    return change


def build_v2(instance):
    v2 = build(instance["seed"], instance["split"], instance["family"], instance["control"], v2_overrides(instance["family"]))
    v2["id"] = instance["id"] + "-v2"
    return v2


def controls_for(index):
    slot = index % 100
    return "clean" if slot < 80 else "malformed" if slot < 90 else "out_of_model"


def generate():
    evaluation = []
    for i, seed in enumerate(EVAL_SEEDS):
        family = FAMILIES[i // 100]
        evaluation.append(build(seed, "evaluation", family, controls_for(i)))
    dev_controls = ["clean", "malformed", "clean", "out_of_model", "clean", "clean", "malformed", "clean"]
    development = [build(seed, "development", FAMILIES[i // 2], dev_controls[i]) for i, seed in enumerate(DEV_SEEDS)]
    rng = random.Random(20261026)
    by_family = {f: [x["id"] for x in evaluation if x["family"] == f] for f in FAMILIES}
    clean = {f: [x["id"] for x in evaluation if x["family"] == f and x["control"] == "clean"] for f in FAMILIES}
    l0 = sorted(sum((rng.sample(by_family[f], 25) for f in FAMILIES), []))
    repair = sorted(sum((rng.sample(clean[f], 15) for f in FAMILIES), []))
    rsi_counts = dict(zip(FAMILIES, [8, 8, 7, 7]))
    rsi = sorted(sum((rng.sample(clean[f], rsi_counts[f]) for f in FAMILIES), []))
    dev_ids = [x["id"] for x in development]
    subsets = {"l0": l0, "repair": repair, "rsi": rsi,
               "dev_l0": dev_ids, "dev_repair": [dev_ids[0], dev_ids[4]], "dev_rsi": [dev_ids[2], dev_ids[5]]}
    return {"schema": "lggr.rsi_swarm.instances.v1", "evaluation": evaluation, "development": development, "subsets": subsets}


def load():
    data = json.loads((HERE / "instances.json").read_text(encoding="utf-8"))
    if data != generate():
        raise ValueError("instances.json differs from the generator")
    return data


def main():
    data = generate()
    (HERE / "instances.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"instances_sha256": digest(data), "evaluation": len(data["evaluation"]),
                      "development": len(data["development"]),
                      "subset_sizes": {k: len(v) for k, v in data["subsets"].items()}}))


if __name__ == "__main__":
    main()
