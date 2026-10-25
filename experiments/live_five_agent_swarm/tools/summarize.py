"""Derive descriptive pilot tables from complete retained run evidence."""
from decimal import Decimal
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def summarize():
    runs = {}
    for name in ("development", "development-v2", "evaluation"):
        directory = BASE / "evidence" / name
        summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
        events = [json.loads(x) for x in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        responses = [x["data"] for x in events if x["kind"] == "api_response"]
        requests = [x for x in events if x["kind"] == "api_request"]
        if summary["api_attempts"] != len(requests):
            raise ValueError("API count mismatch")
        measured_cost = sum(Decimal(x["charged_usd"]) for x in responses)
        if measured_cost != Decimal(summary["charged_or_reserved_usd"]):
            raise ValueError("cost mismatch")
        provider = json.loads((directory / "provider_verification.json").read_text(encoding="utf-8"))
        if {r["response_id"] for r in provider["generations"]} != {r["response"]["id"] for r in responses}:
            raise ValueError("provider generation coverage mismatch")
        runs[name] = {"api_attempts": len(requests), "cost_usd": str(measured_cost),
                      "provider_records_matched": sum(bool(r.get("id_matches") and r.get("model_matches") and r.get("cost_matches")) for r in provider["generations"]),
                      "source_commit": events[0]["data"]["source_commit"],
                      "prompt_tokens": sum(r["response"].get("usage", {}).get("prompt_tokens", 0) for r in responses),
                      "completion_tokens": sum(r["response"].get("usage", {}).get("completion_tokens", 0) for r in responses),
                      "baseline_failed_seeds": [c["seed"] for c in summary["cases"] if c["baseline_failed"]]}
    evaluation = json.loads((BASE / "evidence/evaluation/summary.json").read_text(encoding="utf-8"))
    eval_events = [json.loads(x) for x in (BASE / "evidence/evaluation/events.jsonl").read_text(encoding="utf-8").splitlines()]
    table = []
    for arm in ("A", "B", "C"):
        row = {"arm": arm}
        for kind in ("withdrawal", "infeasible", "control"):
            cases = [c for c in evaluation["cases"] if c["kind"] == kind]
            outcomes = [next((a for a in c["arms"] if a["arm"] == arm), None) for c in cases]
            target = "safe_escalated" if kind == "infeasible" else "completed"
            row[kind] = {"successful": sum(a is not None and a["outcome"] == target for a in outcomes), "total": len(cases)}
        arms = [a for c in evaluation["cases"] for a in c["arms"] if a["arm"] == arm]
        row.update(api_attempts=sum(a["api_attempts"] for a in arms),
                   cost_usd=str(sum(Decimal(a["cost_usd"]) for a in arms)),
                   blocked_attempts=sum(a["blocked_attempts"] for a in arms),
                   initial_local_green_global_red=sum(a["initial_local_green_global_red"] for a in arms),
                   invalid_executions=sum(not a["judge"]["valid_execution"] for a in arms))
        row["blocked_attempts_scope"] = "Pre-repair blocked feedback passes; terminal execution rejections counted separately"
        row["terminal_execution_rejections"] = sum(e["kind"] == "execution" and e["data"]["arm"] == arm and not e["data"]["executed"] for e in eval_events)
        table.append(row)
    result = {"schema": "lggr.five_agent_pilot_report.v1", "authority_effect": "None", "runs": runs,
              "total_api_attempts": sum(r["api_attempts"] for r in runs.values()),
              "total_cost_usd": str(sum(Decimal(r["cost_usd"]) for r in runs.values())), "budget_usd": "10",
              "evaluation_by_arm": table,
              "evaluation_shared_baseline_cost_usd": str(sum(Decimal(c["baseline_cost_usd"]) for c in evaluation["cases"])),
              "interpretation": "Small paired synthetic fault-injection pilot. Shared admission gate means zero invalid executions cannot be attributed to LGGR. Opposite outcomes across two withdrawal seeds do not establish superiority."}
    (BASE / "RESULTS.json").write_text(json.dumps(result, indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    summarize()
