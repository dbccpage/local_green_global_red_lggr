"""Read-only provider-side generation/usage cross-check. Never prints keys."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import sys
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lggr.benchmarks import load_openrouter_credentials
from experiments.live_five_agent_swarm.client import open_private


def verify(directory):
    directory = Path(directory)
    events = [json.loads(line) for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    responses = [e["data"]["response"] for e in events if e["kind"] == "api_response"]
    key, _ = load_openrouter_credentials()
    with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as stream:
        catalog = json.load(stream)["data"]
    requested = {r["model"] for r in responses}
    aliases = {m["id"]: m.get("canonical_slug", m["id"]) for m in catalog if m["id"] in requested}
    def check(response):
        identifier = response["id"]
        req = urllib.request.Request("https://openrouter.ai/api/v1/generation?"+urllib.parse.urlencode({"id": identifier}),
                                     headers={"Authorization": "Bearer "+key})
        try:
            with open_private(req, timeout=30) as stream:
                data = json.load(stream)["data"]
            kept = {k:data.get(k) for k in ("id", "model", "provider_name", "total_cost", "tokens_prompt", "tokens_completion", "native_tokens_prompt", "native_tokens_completion", "created_at", "finish_reason")}
            cost_matches = Decimal(str(data["total_cost"])) == Decimal(str(response["usage"]["cost"]))
            return {"response_id": identifier, "generation": kept, "id_matches": data["id"] == identifier,
                    "response_model": response["model"], "model_matches": data["model"] in (response["model"], aliases.get(response["model"])), "cost_matches": cost_matches}
        except Exception as error:
            return {"response_id": identifier, "verification_error": type(error).__name__}
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(check, responses))
    result = {"schema": "lggr.provider_generation_crosscheck.v1", "queried_at_utc": datetime.now(timezone.utc).isoformat(),
              "read_only_endpoint": "https://openrouter.ai/api/v1/generation", "canonical_alias_source": "https://openrouter.ai/api/v1/models", "canonical_aliases": aliases, "response_count": len(responses),
              "all_matched": all(r.get("id_matches") and r.get("model_matches") and r.get("cost_matches") for r in records),
              "generations": records}
    (directory / "provider_verification.json").write_text(json.dumps(result, indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"run": directory.name, "response_count": len(responses), "all_matched": result["all_matched"]}), flush=True)


if __name__ == "__main__":
    for directory in sys.argv[1:]:
        verify(directory)
