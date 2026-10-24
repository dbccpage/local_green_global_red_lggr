"""Summarize preserved logs, retaining diagnostic failures and source limits."""
from __future__ import annotations

import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def main():
    rows = []
    names = ("pinned-root-tests", "companion", "current-root-all", "selftest", "demo", "cookbook04")
    for name in names:
        path = HERE / f"{name}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        if "checkout_commit" in record:
            record["checkout_commit_observed_after_run"] = record.pop("checkout_commit")
            record["checkout_commit_observed_before_run"] = None
            record["head_stable_during_run"] = None
        if name == "current-root-all":
            record["scope"] = "Supplemental diagnostic run in complete checkout that changed concurrently; not exact-head acceptance evidence. Original output retained without expectation changes."
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        log = (HERE / record["log"]).read_text(encoding="utf-8")
        counts = re.findall(r"Ran (\d+) tests? in", log)
        failures = re.findall(r"FAILED \(failures=(\d+)\)", log)
        rows.append({"artifact": name, "exit_code": record["exit_code"],
                     "tests_run": int(counts[-1]) if counts else None,
                     "failures": int(failures[-1]) if failures else 0,
                     "log": record["log"], "receipt": path.name, "scope": record["scope"]})
    regressions = json.loads((HERE / "regressions.json").read_text())
    lean = json.loads((HERE / "lean-verification.json").read_text())
    result = {"schema": "grok-swarm-lab.upstream-verification-summary.v1",
              "reviewed_commit": regressions["upstream_commit"],
              "regressions_reproduced": regressions["all_findings_reproduced"],
              "original_tests": rows,
              "root_and_paper_lean_compilation_succeeded": lean["all_succeeded"],
              "live_api_requests": 0,
              "dependency_modified": False,
              "application_validation": "Recorded separately; these original upstream tests do not validate the new ledger host."}
    (HERE / "verification_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
