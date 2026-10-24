"""Counterexamples at real host/evidence/tool boundaries, without live APIs."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import threading
import unittest
from unittest import mock

from lggr_swarm_lab.common import BudgetExhausted, SharedBudget, digest
from lggr_swarm_lab.evidence import EvidenceBook, EvidenceError, branch_event, verify_chain
from lggr_swarm_lab.tools import execute_branch, integrate


def attempt(name, branch="shared"):
    return {"attempt_id": name, "kind": "sqlite", "branch": branch,
            "issued": True, "cost": 1}


def sample(verdict, query_id="ledger", scope="endpoint", baseline=0):
    return {"query_id": query_id, "baseline": baseline, "scope": scope,
            "verdict": verdict, "source": "sqlite.branch_contract"}


class TestSharedBudgetAdversarial(unittest.TestCase):
    def test_parallel_attempts_reserve_before_real_effect(self):
        budget, gate, effects = SharedBudget(3), threading.Barrier(12), []
        effects_lock = threading.Lock()

        def worker(index):
            gate.wait(timeout=5)

            def effect():
                with effects_lock:
                    effects.append(index)
                return index
            try:
                budget.execute("parallel", effect, f"branch-{index}")
                return True
            except BudgetExhausted:
                return False

        with ThreadPoolExecutor(max_workers=12) as pool:
            admitted = list(pool.map(worker, range(12)))
        self.assertEqual(sum(admitted), 3)
        self.assertEqual(len(effects), 3)
        self.assertEqual(len(budget.attempts), 3)
        self.assertEqual(len({a["attempt_id"] for a in budget.attempts}), 3)
        self.assertEqual(budget.remaining, 0)

    def test_failed_calls_and_retries_are_consumed(self):
        budget, effects = SharedBudget(2), []

        def unavailable():
            effects.append("attempt")
            raise OSError("fixture HTTP 503")
        for _ in range(2):
            with self.assertRaises(OSError):
                budget.execute("retry", unavailable, "worker")
        with self.assertRaises(BudgetExhausted):
            budget.execute("retry", unavailable, "worker")
        self.assertEqual(effects, ["attempt", "attempt"])
        self.assertEqual(sum(a["cost"] for a in budget.attempts), 2)

    def test_budget_types_reject_boolean_negative_and_fractional(self):
        for invalid in (True, False, -1, 1.0, "1"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                SharedBudget(invalid)


class TestEvidenceMergeAdversarial(unittest.TestCase):
    def setUp(self):
        self.contract = {"policy_version": "policy.v1", "query_id": "ledger",
                         "query_scope": "endpoint", "baseline": 0}
        self.book = EvidenceBook(self.contract)

    def test_reordered_duplicate_merge_retains_negative_cost_and_obligation(self):
        up = branch_event("up", {"attempts": [attempt("a1", "up")],
                                 "global_samples": [sample(True)],
                                 "obligations": ["customer-evidence"]})
        down = branch_event("down", {"attempts": [attempt("a2", "down")],
                                     "global_samples": [sample(False)],
                                     "obligations": []}, parents=("up",))
        result = self.book.merge([down, up, down])
        self.assertEqual([e["event_id"] for e in result["ordered"]], ["up", "down"])
        self.assertEqual(result["global_samples"], [sample(True), sample(False)])
        self.assertEqual(result["cost"], 2)
        self.assertEqual(result["obligations"], ["customer-evidence"])
        self.assertFalse(result["unsupported"])
        result2 = self.book.merge([down])
        self.assertEqual(result2["cost"], 2)
        self.assertEqual(len(result2["global_samples"]), 2)

    def test_missing_parent_cycle_and_conflicting_replay_are_rejected(self):
        bad_batches = [
            [branch_event("orphan", {}, parents=("missing",))],
            [branch_event("a", {}, parents=("b",)), branch_event("b", {}, parents=("a",))],
            [branch_event("a", {"value": 1}), branch_event("a", {"value": 2})],
        ]
        for batch in bad_batches:
            with self.subTest(batch=batch), self.assertRaises(EvidenceError):
                self.book.merge(batch)
            self.assertEqual(self.book.events, {})

    def test_bad_discharge_does_not_mutate_book(self):
        up = branch_event("up", {"obligations": ["owed"]})
        self.book.merge([up])
        before = deepcopy(self.book.events)
        for evidence in (None, {}, "verified", {"source": "sqlite.obligation_evidence", "verified": 1},
                         {"source": "agent-assertion", "verified": True}):
            bad = branch_event("bad", {"discharges": [{"id": "owed", "evidence": evidence}]}, parents=("up",))
            with self.subTest(evidence=evidence), self.assertRaises(EvidenceError):
                self.book.merge([bad])
            self.assertEqual(self.book.events, before)
            self.assertEqual(self.book.merge([])["obligations"], ["owed"])
        good = branch_event("good", {"discharges": [{"id": "owed", "evidence":
                             {"source": "sqlite.obligation_evidence", "verified": True}}]}, parents=("up",))
        self.assertEqual(self.book.merge([good])["obligations"], [])

    def test_conflicting_attribution_is_transactional(self):
        up = branch_event("up", {"attempts": [attempt("same", "up")]})
        self.book.merge([up])
        with self.assertRaises(EvidenceError):
            self.book.merge([branch_event("down", {"attempts": [attempt("same", "down")]}, parents=("up",))])
        self.assertEqual(set(self.book.events), {"up"})
        self.assertEqual(self.book.merge([])["cost"], 1)

    def test_costs_cannot_be_negative_refunds_or_boolean(self):
        for cost in (-1, 0, 2, True, 1.0, "1"):
            invalid = attempt("bad")
            invalid["cost"] = cost
            with self.subTest(cost=cost), self.assertRaises(EvidenceError):
                self.book.merge([branch_event("bad", {"attempts": [invalid]})])
            self.assertEqual(self.book.events, {})

    def test_artifact_policy_and_malformed_sample_are_rejected(self):
        altered = branch_event("altered", {"answer": 1})
        altered["payload"]["answer"] = 2
        cases = [altered, branch_event("policy", {}, policy_version="policy.v2")]
        for invalid in ({}, sample("true"), sample(1), {**sample(True), "source": ""},
                        {**sample(True), "scope": "branch"}):
            cases.append(branch_event("sample", {"global_samples": [invalid]}))
        for event in cases:
            with self.subTest(event=event), self.assertRaises(EvidenceError):
                self.book.merge([event])
        self.assertEqual(self.book.events, {})

    def test_query_scope_and_unknown_are_not_recast(self):
        original = [sample(None), sample(False, "other", "every_prefix", 17)]
        result = self.book.merge([branch_event("mixed", {"global_samples": original})])
        self.assertEqual(result["global_samples"], original)
        self.assertIsNone(result["global_samples"][0]["verdict"])
        self.assertTrue(result["mixed_scope"])
        self.assertTrue(result["unsupported"])
        self.assertEqual(len(result["scope_groups"]), 2)

    def test_declared_auxiliary_query_is_separate_and_supported(self):
        book = EvidenceBook({**self.contract, "required_auxiliary_queries": [
            {"query_id": "aux", "scope": "every_prefix", "baseline": 7}]})
        samples = [sample(True), sample(False, "aux", "every_prefix", 7)]
        result = book.merge([branch_event("mixed", {"global_samples": samples})])
        self.assertTrue(result["mixed_scope"])
        self.assertFalse(result["unsupported"])
        self.assertEqual(result["global_samples"], samples)
        mismatch = book.merge([branch_event("different-baseline", {
            "global_samples": [sample(True, "aux", "every_prefix", 8)]})])
        self.assertTrue(mismatch["unsupported"])

    def test_input_and_returned_mutation_do_not_change_retained_evidence(self):
        event = branch_event("once", {"obligations": ["owed"]})
        result = self.book.merge([event])
        event["payload"]["obligations"].clear()
        result["ordered"][0]["payload"]["obligations"].clear()
        self.assertEqual(self.book.merge([])["obligations"], ["owed"])


class TestActualSQLiteTransformations(unittest.TestCase):
    def test_refund_sign_and_dollars_are_applied_exactly(self):
        source = {"customers": [{"customer_id": "c", "region": "north"}],
                  "orders": [{"order_id": "o", "customer_id": "c", "amount": 17}],
                  "refunds": [{"refund_id": "r", "order_id": "o", "amount": -3}]}
        planner = {"orders": {"scale_to_cents": 100, "join_mode": "first"},
                   "refunds": {"scale_to_cents": 100, "sign": -1}}
        branches = {b: execute_branch(b, source, planner) for b in ("orders", "refunds")}
        result = integrate(branches, {"refund_multiplier": 1})
        self.assertEqual(result, [{"order_id": "o", "customer_id": "c", "region": "north",
                                   "gross_cents": 1700, "refund_cents": 300, "net_cents": 1400}])
        self.assertTrue(all(b["local_pass"] for b in branches.values()))
        self.assertTrue(all(b["planner_sha256"] == digest(planner) for b in branches.values()))

    def test_duplicate_join_has_real_effect_despite_local_success(self):
        source = {"customers": [{"customer_id": "c", "region": "north"}] * 2,
                  "orders": [{"order_id": "o", "customer_id": "c", "amount": 1700}],
                  "refunds": []}
        planner = {"orders": {"scale_to_cents": 1, "join_mode": "all"},
                   "refunds": {"scale_to_cents": 1, "sign": 1}}
        branches = {b: execute_branch(b, source, planner) for b in ("orders", "refunds")}
        result = integrate(branches, {"refund_multiplier": 1})
        self.assertTrue(all(b["local_pass"] for b in branches.values()))
        self.assertEqual(len(result), 2)
        self.assertEqual(sum(r["net_cents"] for r in result), 3400)


class TestReceiptChainAdversarial(unittest.TestCase):
    def make_run(self):
        source = {"orders": [{"order_id": "o", "amount": 123}]}
        artifact = {"data": {"rows": [{"order_id": "o", "net_cents": 123}]}}
        artifact["sha256"] = digest(artifact["data"])
        events, previous = [], "0" * 64
        for seq in range(2):
            event = {"seq": seq, "event_id": f"e{seq}", "previous_sha256": previous,
                     "causal_parents": [] if seq == 0 else ["e0"],
                     "input_artifacts": [],
                     "output_artifacts": [{"id": "output", "sha256": artifact["sha256"]}],
                     "host_action": "defer"}
            event["event_sha256"] = digest(event)
            previous = event["event_sha256"]
            events.append(event)
        return {"input": source, "input_sha256": digest(source), "events": events,
                "artifacts": {"output": artifact}}

    def test_changed_input_artifact_and_event_are_detected(self):
        run = self.make_run()
        verify_chain(run)
        variants = []
        changed = deepcopy(run)
        changed["input"]["orders"][0]["amount"] = 999
        variants.append(changed)
        changed = deepcopy(run)
        changed["artifacts"]["output"]["data"]["rows"][0]["net_cents"] = 999
        variants.append(changed)
        changed = deepcopy(run)
        changed["events"][0]["host_action"] = "commit"
        variants.append(changed)
        for changed in variants:
            with self.subTest(changed=changed), self.assertRaises(EvidenceError):
                verify_chain(changed)

    def test_rehashed_artifact_still_requires_event_binding(self):
        run = self.make_run()
        run["artifacts"]["output"]["data"]["rows"][0]["net_cents"] = 999
        run["artifacts"]["output"]["sha256"] = digest(run["artifacts"]["output"]["data"])
        with self.assertRaises(EvidenceError):
            verify_chain(run)

    def test_duplicate_sequential_identity_rejected_even_with_valid_hash(self):
        run = self.make_run()
        event = run["events"][1]
        event["event_id"] = "e0"
        event["event_sha256"] = digest({k: v for k, v in event.items() if k != "event_sha256"})
        with self.assertRaises(EvidenceError):
            verify_chain(run)


class TestHostAdversarial(unittest.TestCase):
    """Only development fixtures: held-out evaluation stays outside tuning."""
    @classmethod
    def setUpClass(cls):
        from lggr_swarm_lab.fixtures import generate_cases
        cls.cases = generate_cases("development")

    def case(self, family, variant=0):
        return deepcopy(next(c for c in self.cases if c["family"] == family and c["variant"] == variant))

    @staticmethod
    def reseal(run):
        from lggr_swarm_lab.host import replay_fingerprint
        for artifact in run["artifacts"].values():
            artifact["sha256"] = digest(artifact["data"])
        previous = "0" * 64
        for event in run["events"]:
            event["previous_sha256"] = previous
            for ref in event["input_artifacts"] + event["output_artifacts"]:
                ref["sha256"] = run["artifacts"][ref["id"]]["sha256"]
            event["event_sha256"] = digest({k: v for k, v in event.items() if k != "event_sha256"})
            previous = event["event_sha256"]
        run["replay_fingerprint"] = replay_fingerprint(run)

    def test_ablation_changes_operations_and_independent_outcome(self):
        from lggr_swarm_lab.host import run_case
        case = self.case("composition")
        raw, guarded = run_case(case, "A"), run_case(case, "C")
        self.assertEqual(raw["action"], "commit")
        self.assertIs(raw["judgment"]["task_correct"], False)
        self.assertEqual(guarded["action"], "commit")
        self.assertIs(guarded["judgment"]["task_correct"], True)
        self.assertTrue(guarded["judgment"]["admissible"])
        self.assertGreater(guarded["metrics"]["repair_attempts"], 0)
        self.assertNotEqual([d["decision"]["action"] for d in raw["decisions"]],
                            [d["decision"]["action"] for d in guarded["decisions"]])

    def test_prefix_block_prevents_next_host_effect(self):
        from lggr_swarm_lab.host import Host
        host = Host(self.case("query_scope", 1), "C")
        run = host.run()
        self.assertEqual(run["action"], "block")
        self.assertEqual(run["metrics"]["canary_effects"], 1)
        self.assertEqual(run["summary"]["state_path"], [0, 2])
        effects, before = [], len(host.budget.attempts)
        with self.assertRaises(BudgetExhausted):
            host.issue("post-breach-canary", lambda: effects.append("forbidden"))
        self.assertEqual(effects, [])
        self.assertEqual(len(host.budget.attempts), before)

    def test_terminal_scope_permits_recovery_without_refunding_costs(self):
        from lggr_swarm_lab.host import run_case
        for mode in ("B", "C"):
            with self.subTest(mode=mode):
                run = run_case(self.case("query_scope"), mode)
                self.assertEqual(run["summary"]["state_path"], [0, 2, 1])
                self.assertEqual(run["action"], "commit")
                self.assertTrue(run["judgment"]["task_correct"])
                self.assertTrue(run["judgment"]["admissible"])
                self.assertEqual(sum(a["cost"] for a in run["summary"]["attempts"]), run["metrics"]["attempts"])
                self.assertEqual(run["metrics"]["canary_effects"], 3)

    def test_obligation_survives_empty_report_then_checked_discharge(self):
        from lggr_swarm_lab.host import run_case, replay
        unresolved = run_case(self.case("obligations"), "C")
        self.assertEqual(unresolved["action"], "defer")
        self.assertEqual(unresolved["judgment"]["unresolved_obligations"], ["refund-evidence"])
        merged = next(e["observed"]["merged"] for e in unresolved["events"] if e["kind"] == "branch-merge")
        refund_report = next(e for e in merged["ordered"] if e["event_id"] == "refunds")
        self.assertEqual(refund_report["payload"]["obligations"], ["refund-evidence"])
        later_empty = next(e for e in merged["ordered"] if e["event_id"] == "later-empty-report")
        self.assertEqual(later_empty["payload"]["obligations"], [])
        self.assertEqual(merged["obligations"], ["refund-evidence"])
        self.assertFalse(replay(unresolved)["admitted"])
        resolved = run_case(self.case("obligations", 1), "C")
        self.assertEqual(resolved["action"], "commit")
        self.assertEqual(resolved["judgment"]["unresolved_obligations"], [])
        self.assertTrue(any(e["op"] == "discharge" and e["evidence"]["source"] == "sqlite.obligation_evidence"
                            for e in resolved["summary"]["obligation_events"]))

    def test_missing_witness_and_tampered_branch_never_admit(self):
        from lggr_swarm_lab.host import run_case
        missing = run_case(self.case("event_integrity", 1), "C")
        self.assertEqual(missing["action"], "defer")
        self.assertIsNone(missing["output"])
        tampered_case = self.case("event_integrity")
        tampered_case["scenario"]["arrival_plan"].append("tamper-local-pass")
        tampered = run_case(tampered_case, "C")
        self.assertEqual(tampered["action"], "block")
        self.assertEqual(tampered["status"], "malformed")
        self.assertIsNone(tampered["output"])

    def test_duplicate_and_reordered_arrivals_do_not_execute_again(self):
        from lggr_swarm_lab.host import run_case
        results = []
        for arrivals in (["orders", "refunds"], ["refunds", "orders"],
                         ["orders", "orders", "refunds", "refunds"]):
            case = self.case("event_integrity")
            case["scenario"]["arrival_plan"] = arrivals
            results.append(run_case(case, "C"))
        self.assertTrue(all(r["action"] == "commit" for r in results))
        self.assertTrue(all(r["output"] == results[0]["output"] for r in results))
        self.assertEqual(len({r["metrics"]["attempts"] for r in results}), 1)
        self.assertTrue(all(r["metrics"]["canary_effects"] == 3 for r in results))

    def test_merge_preserves_negative_auxiliary_and_real_costs(self):
        from lggr_swarm_lab.host import run_case
        run = run_case(self.case("merge_retention"), "C")
        self.assertEqual(run["action"], "block")
        self.assertIsNone(run["global_verdict"])
        samples = run["summary"]["negative_evidence"]
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0]["query_id"], "auxiliary_branch_contract")
        self.assertIs(samples[0]["verdict"], False)
        merged = next(e["observed"]["merged"] for e in run["events"] if e["kind"] == "branch-merge")
        self.assertEqual(merged["cost"], run["metrics"]["attempts"])
        extras = [a for a in run["summary"]["attempts"] if a["kind"] == "branch-extra-query"]
        self.assertEqual(len(extras), 10)
        self.assertEqual(sum(a["cost"] for a in extras), 10)
        self.assertNotIn("missing_scoped_source_sample:auxiliary_branch_contract", run["judgment"]["admissibility_reasons"])

    def test_failed_probe_retries_exhaust_shared_budget_without_false_pass(self):
        from lggr_swarm_lab.host import run_case
        run = run_case(self.case("shared_budget"), "C")
        self.assertEqual(run["action"], "defer")
        self.assertIn("exhausted", run["residual"])
        self.assertEqual(run["metrics"]["attempts"], 4)
        self.assertEqual(run["metrics"]["canary_effects"], 0)
        self.assertEqual(run["metrics"]["probe_attempts"], 3)
        self.assertIsNone(run["global_verdict"])
        self.assertIsNone(run["defect"])
        self.assertLess(len(run["decisions"]), 10)

    def test_unavailable_observation_is_unknown_and_replay_is_not_admission(self):
        from lggr_swarm_lab.host import run_case, replay
        run = run_case(self.case("evidence_resolution", 1), "C")
        self.assertEqual(run["action"], "defer")
        self.assertEqual(run["status"], "unknown")
        self.assertIsNone(run["global_verdict"])
        self.assertIsNone(run["judgment"]["task_correct"])
        self.assertEqual(run["defect_kind"], "UNKNOWN")
        receipt = replay(run)
        self.assertTrue(receipt["replayed"])
        self.assertFalse(receipt["admitted"])
        self.assertEqual(receipt["action"], "defer")

    def test_fully_resealed_false_admission_fails_fresh_replay(self):
        from lggr_swarm_lab.host import run_case, replay
        forged = run_case(self.case("evidence_resolution", 1), "C")
        forged["action"] = forged["summary"]["action"] = "commit"
        forged["status"] = "verified-on-declared-domain"
        forged["output"] = []
        forged["judgment"]["task_correct"] = True
        forged["global_verdict"] = True
        forged["defect"] = 0
        forged["events"][-1]["observed"]["action"] = "commit"
        forged["events"][-1]["observed"]["status"] = "verified-on-declared-domain"
        self.reseal(forged)
        verify_chain(forged)  # The attack is internally hash-consistent.
        with self.assertRaisesRegex(EvidenceError, "fresh tool/decision/oracle replay differs"):
            replay(forged)

    def test_fully_resealed_certificate_change_fails_fresh_replay(self):
        from lggr_swarm_lab.host import run_case, replay
        forged = run_case(self.case("query_scope"), "C")
        changed = 0
        for event in forged["events"]:
            for certificate in event["observed"].get("certificates", []):
                certificate["current_task_verdict"] = True
                changed += 1
        self.assertGreater(changed, 0)
        self.reseal(forged)
        verify_chain(forged)
        with self.assertRaises(EvidenceError):
            replay(forged)

    def test_judge_runs_only_after_decision_and_views_exclude_protected_inputs(self):
        from lggr_swarm_lab.host import Host
        from lggr_swarm_lab import controller, oracle
        host = Host(self.case("completion_controls"), "C")
        original_decide, original_judge = controller.decide, oracle.judge
        views, judges = [], []

        def checked_decide(view, mode, development=None):
            self.assertTrue(set(view).isdisjoint({"case_id", "family", "variant", "source", "semantics",
                                                 "expected", "expected_output", "judgment", "task_correct"}))
            self.assertEqual(judges, [])
            views.append(deepcopy(view))
            return original_decide(view, mode, development)

        def checked_judge(*args, **kwargs):
            self.assertEqual(host.events[-1]["kind"], "terminal-decision")
            self.assertTrue(views)
            judges.append(True)
            return original_judge(*args, **kwargs)

        with mock.patch.object(controller, "decide", checked_decide), mock.patch.object(oracle, "judge", checked_judge):
            result = host.run()
        self.assertEqual(judges, [True])
        self.assertEqual(result["action"], "commit")

    def test_claimed_valid_migration_needs_registered_mapping(self):
        from lggr_swarm_lab.host import run_case
        supported = run_case(self.case("version_transition"), "C")
        unsupported = run_case(self.case("version_transition", 1), "C")
        self.assertEqual(supported["action"], "commit")
        self.assertEqual(unsupported["action"], "block")
        case = self.case("version_transition")
        case["scenario"]["transition"]["mapping"] = "drop_refunds"
        claimed = run_case(case, "C")
        self.assertEqual(claimed["action"], "block")
        self.assertEqual(claimed["status"], "unsupported")

    def development_evidence(self):
        from lggr_swarm_lab.host import run_case
        from lggr_swarm_lab.tools import probe
        from lggr import analyze_descent
        rows, refined = [], []
        for variant in (0, 1):
            case = self.case("equal_reports", variant)
            executed = run_case(case, "A")
            report = executed["events"][0]["observed"]["initial_report"]
            self.assertIs(type(executed["global_verdict"]), bool)
            row = {"state_id": f"verified-development-{variant}", "report": report,
                   "query": executed["global_verdict"]}
            rows.append(row)
            observation = probe("semantics", case, {})
            refined.append({**row, "report": {**report, "observed_semantics": observation}})
        return {"rows": rows, "refined_rows": refined,
                "certificate": analyze_descent(rows, scope_id="adversarial-verified-development")}

    def test_verified_collision_drives_probe_and_retains_unknown_current_verdict(self):
        from lggr_swarm_lab.host import run_case
        development = self.development_evidence()
        collision = development["certificate"]
        self.assertEqual(collision["status"], "REPORT_INSUFFICIENT")
        self.assertEqual(collision["collision"]["left"]["report"], collision["collision"]["right"]["report"])
        self.assertNotEqual(collision["collision"]["left"]["query"], collision["collision"]["right"]["query"])
        run = run_case(self.case("equal_reports", 1), "C", development)
        initial = run["decisions"][0]["decision"]
        self.assertEqual(initial["action"], "probe")
        self.assertEqual(initial["probe"], "semantics")
        self.assertTrue(initial["certificate_consumed"])
        self.assertTrue(all(c["current_task_verdict"] is None for c in initial["certificates"]))
        self.assertEqual(run["action"], "commit")
        self.assertTrue(run["judgment"]["task_correct"])
        self.assertEqual(run["development"]["certificate"], collision)
        refined = [c for d in run["decisions"] for c in d["decision"]["certificates"]
                   if c["kind"] == "refined-development-fiber"]
        self.assertTrue(refined)
        self.assertTrue(all(c["certificate"]["coverage"] == "supplied finite table only" for c in refined))
        self.assertTrue(all(c["current_task_verdict"] is None for c in refined))

    def test_unavailable_collision_probe_defers_without_labelling_task_false(self):
        from lggr_swarm_lab.host import run_case
        run = run_case(self.case("evidence_resolution", 1), "C", self.development_evidence())
        self.assertEqual(run["action"], "defer")
        self.assertTrue(run["decisions"][0]["decision"]["certificate_consumed"])
        self.assertIsNone(run["global_verdict"])
        self.assertIsNone(run["defect"])

    def test_collision_probe_cannot_override_existing_prefix_block(self):
        from lggr_swarm_lab.host import Host
        from lggr_swarm_lab.controller import decide
        host = Host(self.case("query_scope", 1), "C")
        try:
            view = host.view()
            view["state_path"] = [0, 2]
            decision = decide(view, "C", self.development_evidence())
            self.assertEqual(decision["action"], "block")
        finally:
            host.state_db.close()

    def test_local_step_and_domain_failures_precede_evidence_requests(self):
        from lggr_swarm_lab.host import Host
        from lggr_swarm_lab.controller import decide
        host = Host(self.case("completion_controls"), "C")
        try:
            base = host.view()
            for mode in ("B", "C"):
                for path, step, code in (([0, 3, 1], 2, "LOCAL_STEP_BREACH"),
                                         ([0, 101], 200, "UNSUPPORTED_STATE_DOMAIN")):
                    with self.subTest(mode=mode, code=code):
                        view = deepcopy(base)
                        view["state_path"] = path
                        view["contract"].update(max_step=step, max_total=200)
                        decision = decide(view, mode)
                        self.assertEqual(decision["action"], "block")
                        self.assertIn(code, {f["code"] for f in decision["findings"]})
        finally:
            host.state_db.close()

    def test_forged_development_certificate_blocks_before_worker_effects(self):
        from lggr_swarm_lab.host import run_case
        development = self.development_evidence()
        development["certificate"]["collision"]["right"]["query"] = True
        run = run_case(self.case("equal_reports", 1), "C", development)
        self.assertEqual(run["action"], "block")
        self.assertEqual(run["status"], "malformed")
        self.assertEqual(run["metrics"]["canary_effects"], 0)

    def test_caller_local_pass_field_is_recomputed_from_real_execution(self):
        from lggr_swarm_lab.host import run_case
        case = self.case("completion_controls")
        plan = case["scenario"]["worker_proposals"]
        plan["orders"]["local_pass"] = False
        plan["refunds"]["local_pass"] = False
        run = run_case(case, "C")
        results = [a["data"] for a in run["artifacts"].values() if a["source"] == "sqlite worker"]
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result["operation"]["local_pass"] is False for result in results))
        self.assertTrue(all(result["local_pass"] is True for result in results))
        self.assertTrue(run["judgment"]["task_correct"])

    def test_full_development_provenance_is_filtered_before_controller_call(self):
        from lggr_swarm_lab import controller
        from lggr_swarm_lab.host import run_case
        path = Path(__file__).resolve().parents[1] / "evidence" / "development.json"
        full = json.loads(path.read_text(encoding="utf-8"))
        allowed = {"rows", "certificate", "refined_rows"}
        self.assertIn("executions", full)
        self.assertIn("source_bindings", full)
        self.assertGreater(len(set(full) - allowed), 0)
        original_decide = controller.decide
        observed_modes = []

        def checked_decide(view, mode, development=None):
            self.assertEqual(set(development), allowed)
            self.assertEqual(development, {key: full[key] for key in allowed})
            observed_modes.append(mode)
            return original_decide(view, mode, development)

        with mock.patch.object(controller, "decide", checked_decide):
            for mode in ("B", "C"):
                run = run_case(self.case("completion_controls"), mode, full)
                self.assertEqual(run["action"], "commit")
                self.assertEqual(run["development"], full)
        self.assertEqual(set(observed_modes), {"B", "C"})


if __name__ == "__main__":
    unittest.main()
