"""Tests for lggr_guard, the pre-merge composition gate.

AuthorityEffect: None.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lggr.common import ValidationError  # noqa: E402
from lggr_guard import (Candidate, CompositionGate, Contract, Fact, Ledger, LedgerTampered,  # noqa: E402
                        MemoryComposer, Suite, drift_budget, equals, minimal_failing_set)
from lggr_guard import ledger_demo as demo  # noqa: E402

HAS_GIT = shutil.which("git") is not None


def flag_suite(**extra) -> Suite:
    """Contract: 'safe' must hold. A change can make the gate read 'key' instead of 'gate_on'."""
    return Suite(
        facts=(Fact("safe", (True, False)), Fact("level"), Fact("note")),
        contracts=(equals("safe-holds", "safe", True), drift_budget("level-drift", "level", 2)),
        observe=lambda s: {"safe": (s.get("key", False) if s.get("reads_key") else s["gate_on"]) and not s["bypass"],
                           "level": s["level"], "note": s["note"]},
        **extra)


def memory_gate(suite: Suite | None = None, base: dict | None = None):
    suite = suite or flag_suite()
    composer = MemoryComposer(base or {"gate_on": True, "bypass": False, "level": 0, "note": "x"}, suite.observe)
    ledger = Ledger.memory()
    ledger.record_checkpoint("cfg@0", composer.facts([]), smoke="passed")
    return CompositionGate(suite, composer, ledger), ledger


def accept(gate: CompositionGate, ledger: Ledger, change: Candidate) -> dict:
    receipt = gate.check(change)
    ledger.record_accept(change, receipt, approved_by="owner")
    return receipt


class MinimalSetTests(unittest.TestCase):
    def test_finds_the_pair_among_noise(self):
        changes = [Candidate(str(i)) for i in range(6)]
        fails = lambda s: {"1", "4"} <= {c.change_id for c in s}
        self.assertEqual([c.change_id for c in minimal_failing_set(changes, fails)], ["1", "4"])

    def test_empty_when_base_fails(self):
        self.assertEqual(minimal_failing_set([Candidate("a")], lambda s: True), [])


class CompositionTests(unittest.TestCase):
    def test_lggr_names_only_the_jointly_guilty_changes(self):
        gate, ledger = memory_gate()
        # P2 makes the gate depend on a key; candidate drops the key. Noise changes touch other facts.
        noise1 = Candidate("noise1", {"level": 1}, ref={"level": 1})
        p2 = Candidate("P2", {}, ref=lambda s: s.update(reads_key=True, key=True))
        noise3 = Candidate("noise3", {"level": 2}, ref={"level": 2})
        for change in (noise1, p2, noise3):
            self.assertEqual(accept(gate, ledger, change)["status"], "COMPOSITION_VERIFIED")
        cand = Candidate("C", {}, ref=lambda s: s.pop("key", None))
        receipt = CompositionGate(gate.suite, gate.composer, ledger).check(cand)
        self.assertEqual(receipt["status"], "LOCAL_GREEN_GLOBAL_RED")
        lggr = next(f for f in receipt["findings"] if f["kind"] == "LOCAL_GREEN_GLOBAL_RED")
        self.assertEqual(lggr["changes"], ["P2", "C"])
        self.assertEqual(lggr["contract"], "safe-holds")
        self.assertFalse(receipt["allowed"])

    def test_local_red_is_not_called_lggr(self):
        gate, _ = memory_gate()
        receipt = gate.check(Candidate("C", {"safe": False}, ref={"bypass": True}))
        self.assertEqual(receipt["status"], "LOCAL_RED")

    def test_drift_is_cumulative_against_the_anchor(self):
        gate, ledger = memory_gate()
        ledger.record_anchor({"safe": True, "level": 0, "note": "x"}, approved_by="owner")
        bump = lambda s: s.__setitem__("level", s["level"] + 1)
        accept(gate, ledger, Candidate("L1", {"level": 1}, ref=bump))
        accept(CompositionGate(gate.suite, gate.composer, ledger), ledger, Candidate("L2", {"level": 2}, ref=bump))
        receipt = CompositionGate(gate.suite, gate.composer, ledger).check(Candidate("L3", {"level": 3}, ref=bump))
        self.assertEqual(receipt["status"], "LOCAL_GREEN_GLOBAL_RED")
        finding = next(f for f in receipt["findings"] if f["kind"] == "LOCAL_GREEN_GLOBAL_RED")
        self.assertEqual(finding["changes"], ["L1", "L2", "L3"])
        self.assertEqual(finding["contract"], "level-drift")

    def test_checkpoint_resets_pending_but_not_anchor(self):
        gate, ledger = memory_gate()
        ledger.record_anchor({"safe": True, "level": 0, "note": "x"}, approved_by="owner")
        accept(gate, ledger, Candidate("L1", {"level": 1}, ref={"level": 1}))
        ledger.record_checkpoint("cfg@1", {"safe": True, "level": 1, "note": "x"}, smoke="passed")
        self.assertEqual(ledger.pending(), [])
        self.assertEqual(ledger.anchor_facts["level"], 0)

    def test_blame_after_red_smoke(self):
        gate, ledger = memory_gate()
        a = Candidate("A", {}, ref=lambda s: s.update(reads_key=True, key=True))
        b = Candidate("B", {}, ref=lambda s: s.pop("key", None))
        noise = Candidate("N", {"level": 1}, ref={"level": 1})
        # Simulate two gates that each saw only main (the race the ledger exists to stop).
        for change in (a, noise, b):
            fresh = Ledger(list(ledger.entries[:1]))
            ledger.record_accept(change, CompositionGate(gate.suite, gate.composer, fresh).check(change),
                                 approved_by="owner")
        receipt = CompositionGate(gate.suite, gate.composer, ledger).blame()
        finding = next(f for f in receipt["findings"] if f["contract"] == "safe-holds")
        self.assertEqual(finding["changes"], ["A", "B"])
        self.assertEqual(finding["kind"], "LOCAL_GREEN_GLOBAL_RED")


class ModelMismatchTests(unittest.TestCase):
    def test_undeclared_effect_blocks_even_when_contracts_hold(self):
        gate, _ = memory_gate()
        receipt = gate.check(Candidate("C", {}, ref={"note": "quiet"}))
        self.assertEqual(receipt["status"], "MODEL_MISMATCH")
        codes = {f["code"] for f in receipt["findings"]}
        self.assertEqual(codes, {"UNDECLARED_EFFECT", "UNCOVERED_EFFECT"})

    def test_declared_effect_passes(self):
        gate, _ = memory_gate()
        receipt = gate.check(Candidate("C", {"level": 1}, ref={"level": 1}))
        self.assertEqual(receipt["status"], "COMPOSITION_VERIFIED")

    def test_declared_but_absent(self):
        gate, _ = memory_gate()
        receipt = gate.check(Candidate("C", {"level": 1}, ref={}))
        self.assertIn("DECLARED_EFFECT_ABSENT", {f.get("code") for f in receipt["findings"]})

    def test_out_of_domain_and_unknown_fact(self):
        suite = flag_suite()
        suite.observe = lambda s: {"safe": "maybe", "level": 0, "note": "x", "surprise": 1}
        gate, _ = memory_gate(suite)
        codes = {f.get("code") for f in gate.check(Candidate("C"))["findings"]}
        self.assertTrue({"OUT_OF_DOMAIN", "UNDECLARED_FACT"} <= codes)

    def test_observer_failure_fails_closed(self):
        gate, ledger = memory_gate()
        receipt = gate.check(Candidate("C", {}, ref=lambda s: s.pop("gate_on")))
        self.assertEqual(receipt["status"], "MODEL_MISMATCH")
        self.assertEqual(receipt["findings"][0]["code"], "OBSERVER_FAILED")

    def test_declaration_collision_is_reported(self):
        gate, _ = memory_gate()
        gate.check(Candidate("quiet1", {}, ref={}))
        receipt = gate.check(Candidate("quiet2", {}, ref={"note": "q"}))
        self.assertEqual(receipt["declaration_sufficiency"], "REPORT_INSUFFICIENT")


class AuthorityTests(unittest.TestCase):
    def test_weakened_contract_trips_probe(self):
        weak = Contract("weak", ("safe",), lambda f, a: True, probe=({"safe": False}, {}))
        suite = flag_suite()
        suite.contracts = (*suite.contracts, weak)
        gate, _ = memory_gate(suite)
        self.assertEqual(gate.check(Candidate("C"))["status"], "GUARD_PROBE_FAILED")

    def test_protected_path(self):
        gate, _ = memory_gate()
        receipt = gate.check(Candidate("C", {}, ref={"_touches": [".lggr/suite.py"]}))
        self.assertEqual(receipt["status"], "AUTHORITY_REQUIRED")

    def test_ledger_refuses_red_accept_and_detects_tamper(self):
        gate, ledger = memory_gate()
        bad = Candidate("C", {"safe": False}, ref={"bypass": True})
        with self.assertRaises(ValidationError):
            ledger.record_accept(bad, gate.check(bad), approved_by="owner")
        ledger.entries[0]["smoke"] = "skipped"
        with self.assertRaises(LedgerTampered):
            ledger.verify()

    def test_obligations_stay_open_until_cleared(self):
        gate, ledger = memory_gate()
        accept(gate, ledger, Candidate("A", {"level": 1}, ("add protected test",), ref={"level": 1}))
        receipt = CompositionGate(gate.suite, gate.composer, ledger).check(Candidate("B"))
        self.assertEqual(receipt["unresolved_obligations"], [{"change_id": "A", "obligation": "add protected test"}])
        ledger.record_clear("A", "add protected test", approved_by="owner")
        self.assertEqual(ledger.open_obligations(), [])


@unittest.skipUnless(HAS_GIT, "git not installed")
class GitTests(unittest.TestCase):
    def test_demo_statuses(self):
        with tempfile.TemporaryDirectory() as td:
            rows = demo.run_git_demo(Path(td)) + demo.run_drift_demo()
        got = [(r["status"], r["changes"]) for r in rows]
        self.assertEqual(got, [
            ("COMPOSITION_VERIFIED", ["A"]),
            ("COMPOSITION_VERIFIED", ["B"]),
            ("LOCAL_GREEN_GLOBAL_RED", ["A", "B"]),
            ("LOCAL_RED", ["C"]),
            ("AUTHORITY_REQUIRED", ["D"]),
            ("MODEL_MISMATCH", ["F"]),
            ("COMPOSITION_VERIFIED", ["F'"]),
            ("LOCAL_GREEN_GLOBAL_RED", ["E1", "E2"]),
        ])

    def test_cli_round_trip(self):
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        with tempfile.TemporaryDirectory() as td:
            repo = demo.build_repo(Path(td))
            ledger = Path(td) / "ledger.jsonl"

            def cli(*args):
                proc = subprocess.run([sys.executable, "-m", "lggr_guard", "--repo", str(repo),
                                       "--ledger", str(ledger), *args], capture_output=True, text=True,
                                      env=env, cwd=str(ROOT))
                return proc.returncode, proc.stdout

            self.assertEqual(cli("init", "--approved-by", "owner")[0], 0)
            self.assertEqual(cli("accept", "A-configurable-precheck", "--id", "A", "--approved-by", "owner")[0], 0)
            code, out = cli("check", "B-reject-unknown-keys", "--id", "B")
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out)["status"], "LOCAL_GREEN_GLOBAL_RED")
            code, out = cli("status")
            self.assertEqual(json.loads(out)["pending"], ["A"])


if __name__ == "__main__":
    unittest.main()
