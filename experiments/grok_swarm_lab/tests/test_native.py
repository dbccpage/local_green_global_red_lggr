"""Recorded native responses remain proposals; SQL and judging are host work."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from lggr_swarm_lab import ROOT
from lggr_swarm_lab.fixtures import generate_cases
from lggr_swarm_lab.host import run_case, replay


class NativeProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / "evidence/native"
        read = lambda name: json.loads((folder / name).read_text(encoding="utf-8"))
        cls.native = {"planner_input":read("planner-input.json"),"planner_response":read("planner-response.json"),
            "plan":read("planner-response.json")["plan"],
            "worker_responses":{b:read(b+"-response.json") for b in ("orders","refunds")}}
        cls.case = next(c for c in generate_cases("development") if c["family"]=="equal_reports" and c["variant"]==1)

    def test_only_actual_response_events_are_native(self):
        run = run_case(self.case, "C", native=self.native)
        self.assertEqual(run["action"], "commit")
        self.assertTrue(run["judgment"]["task_correct"])
        native = [e for e in run["events"] if e["agent_execution_mode"]=="native_codex_proposal"]
        self.assertEqual([e["role"] for e in native], ["planner","orders","refunds"])
        self.assertTrue(all(e["kind"] in ("native-planner-response","native-worker-proposal") for e in native))
        self.assertTrue(replay(run)["replayed"])

    def test_planner_and_workers_bind_actual_input(self):
        for target in ("planner_response", "worker_responses"):
            native = deepcopy(self.native)
            response = native[target] if target=="planner_response" else native[target]["orders"]
            response["input_sha256"] = "0"*64
            run = run_case(self.case, "C", native=native)
            self.assertEqual(run["action"], "block")
            self.assertEqual(run["status"], "malformed")
            self.assertEqual(run["metrics"]["canary_effects"], 0)


if __name__=="__main__":
    unittest.main()
