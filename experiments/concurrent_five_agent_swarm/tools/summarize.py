"""Summarize verified completed AND interrupted runs without dropping seeds."""
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.concurrent_five_agent_swarm.verify import verify
HERE = Path(__file__).resolve().parents[1]


def summarize():
    evidence = HERE / "evidence"
    ledger = json.loads((evidence/"budget.json").read_text(encoding="utf-8"))
    runs, cases, arms_started, arm_results = [], {}, set(), {}
    paired_trials = []
    usage = {a: {"calls": 0, "cost": Decimal(0)} for a in ("baseline", "A", "B", "C")}
    unknown_reserved, received = Decimal(0), 0
    unverified_generations = []
    for entry in ledger["runs"]:
        path = evidence/entry["path"]
        checked = verify(path)
        summary = json.loads((path/"summary.json").read_text(encoding="utf-8"))
        events = [json.loads(s) for s in (path/"events.jsonl").read_text(encoding="utf-8").splitlines()]
        responses = [e["data"] for e in events if e["kind"] == "api_response"]
        errors = [e["data"] for e in events if e["kind"] == "api_error"]
        cost = sum((Decimal(e["charged_usd"]) for e in responses), Decimal(0))
        reserve = sum((Decimal(e["charged_upper_bound_usd"]) for e in errors), Decimal(0))
        reserve += sum((Decimal(e["charged_usd"]) for e in responses if not e["cost_reported"]), Decimal(0))
        charged = cost + sum((Decimal(e["charged_upper_bound_usd"]) for e in errors), Decimal(0))
        assert charged == Decimal(summary["charged_or_reserved_usd"]) == Decimal(entry["charged_or_reserved_usd"])
        assert len(responses)+len(errors) == summary["api_attempts"]
        provider = json.loads((path/"provider_verification.json").read_text(encoding="utf-8"))
        raw = {e["response"]["id"]: e["response"] for e in responses}
        records = {r["response_id"]: r for r in provider["generations"]}
        assert len(raw) == len(responses) and len(records) == len(provider["generations"]) and set(raw) == set(records)
        for ident, response in raw.items():
            if records[ident].get("verification_error"):
                unverified_generations.append({"run": path.name, **records[ident]})
                continue
            generation = records[ident]["generation"]
            assert generation["id"] == ident
            assert Decimal(str(generation["total_cost"])) == Decimal(str(response["usage"]["cost"]))
            assert generation["model"] in (response["model"], provider["canonical_aliases"].get(response["model"]))
        unknown_reserved += reserve
        received += len(responses)
        waves = [e["data"]["peak_inflight"] for e in events if e["kind"] == "wave_result"]
        phase = events[0]["data"]["config"]["phase"]
        runs.append({"run": path.name, "phase": phase, "api_attempts": summary["api_attempts"],
            "received_responses": len(responses), "cost_or_reserve_usd": str(charged),
            "max_inflight_requests": max(waves, default=0), "concurrent_waves": sum(x>1 for x in waves), "verification": checked})
        if phase == "development": continue
        for event in events:
            kind, data = event["kind"], event["data"]
            if kind == "case_start":
                seed, active_arm = data["seed"], "baseline"
                assert seed not in cases, "evaluation seed must not be retried"
                cases[seed] = {"kind": data["kind"], "baseline_failed": False, "finished": False}
            elif kind == "arm_start":
                active_arm = data["arm"]
                arms_started.add((seed, active_arm))
            elif kind == "arm_result": arm_results[(seed, data["arm"])] = data
            elif kind == "case_result":
                cases[seed].update(baseline_failed=data["baseline_failed"], finished=True)
                paired_trials.extend(data["arms"])
            elif kind in ("api_response", "api_error"):
                usage[active_arm]["calls"] += 1
                usage[active_arm]["cost"] += Decimal(data["charged_usd"] if kind == "api_response" else data["charged_upper_bound_usd"])
    outcomes = {}
    for seed in range(5200, 5218):
        case = cases.get(seed)
        outcomes[seed] = {}
        for arm in "ABC":
            result = arm_results.get((seed, arm))
            outcomes[seed][arm] = (result["outcome"] if result else "not_started" if case is None else
                "baseline_failed" if case["baseline_failed"] else
                "provider_interrupted" if (seed, arm) in arms_started else "not_run_after_provider_interrupt")
    conditions = {}
    for offset, kind in enumerate(("withdrawal", "infeasible", "control")):
        seeds = [s for s in range(5200, 5218) if (s-5200)%3 == offset]
        conditions[kind] = {"seeds": len(seeds), "baseline_failed": sum(cases.get(s, {}).get("baseline_failed", False) for s in seeds),
            "arms": {a: dict(Counter(outcomes[s][a] for s in seeds)) for a in "ABC"}}
    by_arm = {}
    for arm in ("baseline", "A", "B", "C"):
        trials = [r for (s,a),r in arm_results.items() if a == arm]
        by_arm[arm] = {"finished_arms": len(trials), "calls": usage[arm]["calls"], "cost_or_reserve_usd": str(usage[arm]["cost"]),
            "invalid_executions": sum(not a["judge"]["valid_execution"] for a in trials),
            "terminal_execution_rejections": sum(not a["judge"]["complete"] for a in trials)}
    paired_usage = {arm: {"trials": sum(a["arm"] == arm for a in paired_trials),
        "calls": sum(a["api_attempts"] for a in paired_trials if a["arm"] == arm),
        "cost_or_reserve_usd": str(sum((Decimal(a["cost_usd"]) for a in paired_trials if a["arm"] == arm), Decimal(0)))} for arm in "ABC"}
    pairs = Counter()
    for s in range(5200, 5218, 3):
        if (s,"B") in arm_results and (s,"C") in arm_results:
            pairs[str((outcomes[s]['B'] == 'completed', outcomes[s]['C'] == 'completed'))] += 1
    new_spend = sum((Decimal(r["cost_or_reserve_usd"]) for r in runs), Decimal(0))
    total = Decimal(ledger["prior_pilot_usd"]) + new_spend
    assert total <= Decimal(ledger["ceiling_usd"]) == 10
    result = {"schema": "lggr.concurrent_swarm_results.v2", "runs": runs, "conditions": conditions,
        "evaluation_usage": by_arm, "paired_evaluation_usage": paired_usage, "seed_outcomes": outcomes, "paired_B_C_withdrawal_success": dict(pairs),
        "evaluation_cases_started": len(cases), "evaluation_cases_finished": sum(c['finished'] for c in cases.values()),
        "new_api_attempts": sum(r['api_attempts'] for r in runs), "new_received_responses": received,
        "provider_verified_generations": received-len(unverified_generations), "unverified_generations": unverified_generations,
        "prior_pilot_usd": ledger["prior_pilot_usd"], "new_charged_or_reserved_usd": str(new_spend),
        "unconfirmed_reserved_usd": str(unknown_reserved), "pilot_total_charged_or_reserved_usd": str(total),
        "remaining_usd": str(10-total),
        "scope": "Descriptive concurrent synthetic pilot; initial failures and interrupted arms retained; no general superiority claim."}
    (HERE/"RESULTS.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": summarize()
