"""Tests for lggr_guard: composition gate, drift, frozen decisions, decision log, git mode."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lggr_guard import Change, Check, DecisionLog, FrozenDecisions, Metric, compose_check
from lggr_guard import demo
from lggr_guard.git import compose_branches


class ComposeTests(unittest.TestCase):
    def test_local_green_global_red_is_rejected_with_minimal_witness(self):
        report = demo.scenario_composition()
        self.assertEqual(report["verdict"], "reject")
        self.assertEqual(report["defect"], "NGD")
        self.assertTrue(report["local_green"])
        self.assertFalse(report["global_green"])
        self.assertEqual(report["minimal_failing_sets"][0]["changes"], ["make-precheck-configurable", "adopt-fast-profile"])
        self.assertEqual([(u["behaviour"], u["emergent"]) for u in report["undeclared"]], [("precheck_enabled", True)])

    def test_independent_declared_changes_are_accepted(self):
        a = Change("a", lambda s: {**s, "x": 1}, frozenset({"x"}))
        b = Change("b", lambda s: {**s, "y": 2}, frozenset({"y"}))
        report = compose_check({"x": 0, "y": 0}, [a, b], [Check("ok", lambda s: True)], observe=dict)
        self.assertEqual((report["verdict"], report["defect"]), ("accept", "ZDR"))

    def test_undeclared_single_change_is_not_emergent(self):
        a = Change("a", lambda s: {**s, "x": 1, "hidden": True}, frozenset({"x"}))
        report = compose_check({"x": 0, "hidden": False}, [a], [Check("ok", lambda s: True)], observe=dict)
        self.assertEqual(report["undeclared"], [{"behaviour": "hidden", "base": False, "composed": True,
                                                 "changed_alone_by": ["a"], "emergent": False}])

    def test_cumulative_drift_measured_from_anchor(self):
        report = demo.scenario_drift()
        drift = report["drift"][0]
        self.assertEqual(drift["first_excursion_after"], "relax-threshold-2")
        self.assertTrue(all(abs(p["step"]) <= 0.05 for p in drift["path"]))
        self.assertEqual(report["verdict"], "reject")

    def test_minimal_sets_exclude_supersets(self):
        flags = [Change(n, lambda s, n=n: s | {n}) for n in "abc"]
        report = compose_check(frozenset(), flags, [Check("not a and b", lambda s: not {"a", "b"} <= s)])
        self.assertEqual([m["changes"] for m in report["minimal_failing_sets"]], [["a", "b"]])


class FrozenAndLogTests(unittest.TestCase):
    def test_reviewer_drift_alarm(self):
        out = demo.scenario_reviewer_drift()
        self.assertFalse(out["before_update"]["alarm"])
        self.assertTrue(out["after_update"]["alarm"])

    def test_frozen_cases_cannot_be_edited(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "f.json"
            frozen = FrozenDecisions(path)
            frozen.freeze("c1", {"a": 1}, "accept")
            data = json.loads(path.read_text())
            data[0]["input"]["a"] = 2
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                FrozenDecisions(path).replay(lambda case: "accept")
            with self.assertRaises(ValueError):
                frozen.freeze("c1", {}, "reject")

    def test_decision_log_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = DecisionLog(Path(tmp) / "d.jsonl")
            log.append("compose", {"verdict": "reject"})
            log.append("compose", {"verdict": "accept"})
            self.assertTrue(log.verify()["ok"])
            lines = log.path.read_text().splitlines()
            lines[0] = lines[0].replace("reject", "accept")
            log.path.write_text("\n".join(lines) + "\n")
            self.assertEqual(log.verify(), {"ok": False, "broken_at": 0})


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True, capture_output=True)


class GitModeTests(unittest.TestCase):
    def test_branches_green_alone_red_together_and_protected_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q", "-b", "main")
            (repo / "gate.json").write_text(json.dumps({"precheck": True, "configurable": False}))
            (repo / "profile.json").write_text(json.dumps({}))
            (repo / "probe.py").write_text(
                "import json,sys\n"
                "g=json.load(open('gate.json')); p=json.load(open('profile.json'))\n"
                "on = p.get('precheck', True) if g['configurable'] else g['precheck']\n"
                "sys.exit(0 if on else 1)\n")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "base")

            def branch(name, files):
                git(repo, "checkout", "-q", "-b", name, "main")
                for fname, content in files.items():
                    (repo / fname).write_text(content)
                git(repo, "commit", "-q", "-am", name)
                git(repo, "checkout", "-q", "main")
            branch("configurable", {"gate.json": json.dumps({"precheck": True, "configurable": True})})
            branch("fast", {"profile.json": json.dumps({"precheck": False, "parallel": 4})})
            branch("weaken-probe", {"probe.py": "import sys\nsys.exit(0)\n",
                                    "gate.json": json.dumps({"precheck": False, "configurable": False})})

            check = f'"{sys.executable}" probe.py'
            report = compose_branches(repo, "main", ["fast", "configurable"], check)
            self.assertTrue(report["local_green"])
            self.assertEqual(report["defect"], "NGD")
            self.assertEqual(report["verdict"], "reject")
            weakened = compose_branches(repo, "main", ["weaken-probe"], check, protected=["probe.py"])
            self.assertEqual(weakened["verdict"], "reject")  # probe restored from main catches it
            unprotected = compose_branches(repo, "main", ["weaken-probe"], check)
            self.assertEqual(unprotected["verdict"], "accept")  # without protection the branch fools its own check
            listed = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True).stdout
            self.assertEqual(len(listed.strip().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
