"""Meaningful reference and protocol tests; no application results are inspected."""
import copy
import unittest

from lggr_swarm_lab.fixtures import FAMILIES, digest, generate_cases
from lggr_swarm_lab.oracle import judge, reference_rows


def clean_trace(case):
    return {
        "action": "commit", "state_path": [0, 0, 0],
        "attempts": [{"attempt_id": "a1", "branch": "host", "cost": 1, "issued": True, "kind": "execute"}],
        "observations": [
            {"probe": "semantics", "source": "sqlite.metadata", "result": {k: case["semantics"][k] for k in ("order_scale_to_cents", "refund_scale_to_cents", "refund_sign")}},
            {"probe": "branch_evidence", "source": "sqlite.branches", "result": {"source_counts": {}, "branches": {}}},
        ],
        "obligation_events": [], "transitions": [], "negative_evidence": [],
        "arrival_events": [
            {"event_id": "orders", "parent_ids": ["planner"], "payload_hash": "o", "role": "orders"},
            {"event_id": "refunds", "parent_ids": ["planner"], "payload_hash": "r", "role": "refunds"},
        ],
    }


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.case = generate_cases("development")[0]

    def test_independent_hand_computed_money_and_first_customer(self):
        case = copy.deepcopy(self.case)
        case["source"] = {
            "customers": [{"customer_id": "c", "region": "first"}, {"customer_id": "c", "region": "second"}],
            "orders": [{"order_id": "b", "customer_id": "c", "amount": 9}, {"order_id": "a", "customer_id": "c", "amount": 12}],
            "refunds": [{"refund_id": "r0", "order_id": "a", "amount": -3}, {"refund_id": "r1", "order_id": "a", "amount": -2}],
        }
        case["semantics"].update(order_scale_to_cents=100, refund_scale_to_cents=10, refund_sign=-1)
        self.assertEqual(reference_rows(case), [
            {"order_id": "a", "customer_id": "c", "region": "first", "gross_cents": 1200, "refund_cents": 50, "net_cents": 1150},
            {"order_id": "b", "customer_id": "c", "region": "first", "gross_cents": 900, "refund_cents": 0, "net_cents": 900},
        ])

    def test_source_duplicates_not_silently_reinterpreted(self):
        case = copy.deepcopy(self.case)
        case["source"]["orders"].append(copy.deepcopy(case["source"]["orders"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            reference_rows(case)

    def test_correct_artifact_and_wrong_cent_rejected_independently(self):
        rows = reference_rows(self.case)
        self.assertTrue(judge(self.case, rows, clean_trace(self.case))["task_correct"])
        rows[0]["net_cents"] += 1
        result = judge(self.case, rows, clean_trace(self.case))
        self.assertFalse(result["task_correct"])
        self.assertTrue(result["admissible"])  # Evidence validity is a separate target.

    def test_boolean_money_duplicate_row_and_order_are_not_accepted(self):
        rows = reference_rows(self.case)
        wrong = copy.deepcopy(rows)
        wrong[0]["gross_cents"] = True
        self.assertFalse(judge(self.case, wrong)["task_correct"])
        self.assertFalse(judge(self.case, rows + rows[:1])["task_correct"])
        self.assertFalse(judge(self.case, list(reversed(rows)))["task_correct"])

    def test_defer_is_not_a_passing_label_but_candidate_can_be_correct(self):
        trace = clean_trace(self.case)
        trace.update(action="defer", candidate_rows=reference_rows(self.case))
        trace["observations"] = []
        result = judge(self.case, None, trace)
        self.assertIsNone(result["task_correct"])
        self.assertTrue(result["candidate_correct"])
        self.assertEqual(result["admissibility_status"], "unknown")

    def test_forged_semantic_observation_is_not_admissible(self):
        trace = clean_trace(self.case)
        trace["observations"][0]["result"]["order_scale_to_cents"] = 100
        result = judge(self.case, reference_rows(self.case), trace)
        self.assertEqual(result["admissibility_status"], "malformed")
        self.assertIn("semantic_evidence_mismatch", result["admissibility_reasons"])

    def test_endpoint_recovery_and_prefix_violation_are_distinct(self):
        trace = clean_trace(self.case)
        trace["state_path"] = [0, 2, 1]
        self.assertTrue(judge(self.case, reference_rows(self.case), trace)["admissible"])
        self.case["public"]["contract"]["query_scope"] = "every_prefix"
        result = judge(self.case, reference_rows(self.case), trace)
        self.assertIn("every_prefix_bound_exceeded", result["admissibility_reasons"])

    def test_intermediate_endpoint_is_unknown_not_terminal_failure(self):
        trace = clean_trace(self.case)
        trace.update(action="defer", state_path=[0, 2])
        result = judge(self.case, None, trace)
        self.assertIn("terminal_endpoint_not_observed", result["admissibility_reasons"])
        self.assertNotIn("terminal_endpoint_bound_exceeded", result["admissibility_reasons"])

    def test_irreversible_attempt_cost_does_not_cancel_with_state(self):
        trace = clean_trace(self.case)
        trace["state_path"] = [0, 1, 0]
        trace["attempts"] += [{"attempt_id": f"a{i}", "branch": "refunds", "cost": 1, "issued": True, "kind": "retry"} for i in range(2, 22)]
        result = judge(self.case, reference_rows(self.case), trace)
        self.assertEqual(result["consumed_cost"], 21)
        self.assertIn("shared_resource_limit_exceeded", result["admissibility_reasons"])

    def test_attempt_replay_deduplicates_only_identical_events(self):
        trace = clean_trace(self.case)
        trace["attempts"].append(copy.deepcopy(trace["attempts"][0]))
        self.assertEqual(judge(self.case, reference_rows(self.case), trace)["consumed_cost"], 1)
        trace["attempts"][-1]["cost"] = 2
        self.assertIn("conflicting_attempt_replay", judge(self.case, reference_rows(self.case), trace)["admissibility_reasons"])

    def test_empty_later_obligation_report_does_not_erase_debt(self):
        self.case["scenario"]["obligations"] = [{"id": "proof", "branch": "refunds", "discharge_available": True}]
        trace = clean_trace(self.case)
        result = judge(self.case, reference_rows(self.case), trace)
        self.assertEqual(result["unresolved_obligations"], ["proof"])
        fact = {"source": "sqlite.obligation_evidence", "verified": True}
        trace["observations"].append({"probe": "obligation_evidence", "source": "sqlite.obligation_evidence", "result": {"proof": fact}})
        trace["obligation_events"].append({"op": "discharge", "id": "proof", "evidence": fact})
        self.assertTrue(judge(self.case, reference_rows(self.case), trace)["admissible"])

    def test_forged_obligation_discharge_is_malformed(self):
        self.case["scenario"]["obligations"] = [{"id": "proof", "branch": "refunds", "discharge_available": False}]
        trace = clean_trace(self.case)
        fact = {"source": "sqlite.obligation_evidence", "verified": True}
        trace["observations"].append({"probe": "obligation_evidence", "source": "sqlite", "result": {"proof": fact}})
        trace["obligation_events"].append({"op": "discharge", "id": "proof", "evidence": fact})
        self.assertEqual(judge(self.case, reference_rows(self.case), trace)["admissibility_status"], "malformed")

    def test_validated_transition_needs_actual_mapping_evidence(self):
        transition = {"kind": "validated", "dimension": "report_schema", "from_version": "v1", "to_version": "v2", "mapping": "identity_ledger_columns"}
        self.case["scenario"]["transition"] = transition
        trace = clean_trace(self.case)
        self.assertIn("transition_validation_missing", judge(self.case, reference_rows(self.case), trace)["admissibility_reasons"])
        fact = {"validated": True, "transition": transition, "source": "sqlite.migrations"}
        trace["observations"].append({"probe": "migration", "source": "sqlite.migrations", "result": fact})
        trace["transitions"].append({"from_version": "v1", "to_version": "v2", "evidence": fact, "validated": True})
        self.assertTrue(judge(self.case, reference_rows(self.case), trace)["admissible"])

    def test_arrival_reordering_and_identical_duplicate_are_benign(self):
        trace = clean_trace(self.case)
        trace["arrival_events"].reverse()
        trace["arrival_events"].append(copy.deepcopy(trace["arrival_events"][0]))
        self.assertTrue(judge(self.case, reference_rows(self.case), trace)["admissible"])
        trace["arrival_events"][-1]["payload_hash"] = "altered"
        self.assertIn("conflicting_event_replay", judge(self.case, reference_rows(self.case), trace)["admissibility_reasons"])

    def test_omitted_branch_event_is_unknown(self):
        trace = clean_trace(self.case)
        trace["arrival_events"] = trace["arrival_events"][:1]
        self.assertIn("missing_branch_event:refunds", judge(self.case, reference_rows(self.case), trace)["admissibility_reasons"])

    def test_negative_auxiliary_sample_does_not_change_ledger_truth(self):
        sample = {"query_id": "aux", "scope": "endpoint", "baseline": 0, "global_verdict": False}
        self.case["public"]["contract"]["required_auxiliary_queries"] = ["aux"]
        self.case["scenario"]["negative_evidence"] = [sample]
        trace = clean_trace(self.case)
        trace["negative_evidence"] = [{"query_id": "aux", "scope": "endpoint", "baseline": 0,
                                       "verdict": False, "terminal": True, "source": "sqlite.branch_contract"}]
        result = judge(self.case, reference_rows(self.case), trace)
        self.assertTrue(result["task_correct"])
        self.assertFalse(result["admissible"])
        self.assertIn("auxiliary_requirement_false:aux", result["admissibility_reasons"])


class FixtureProtocolTests(unittest.TestCase):
    def test_frozen_split_counts_seeds_and_repeatability(self):
        dev, evaluation = generate_cases("dev"), generate_cases("eval")
        self.assertEqual((len(dev), len(evaluation)), (24, 48))
        for family in FAMILIES:
            self.assertEqual(sum(c["family"] == family for c in dev), 2)
            self.assertEqual(sum(c["family"] == family for c in evaluation), 4)
        self.assertEqual(digest(dev), digest(generate_cases("development")))
        self.assertNotEqual(digest(dev), digest(evaluation))
        self.assertTrue({c["case_id"] for c in dev}.isdisjoint({c["case_id"] for c in evaluation}))

    def test_development_collision_has_same_raw_source_different_truth(self):
        first, second = generate_cases("development")[:2]
        self.assertEqual(first["source"], second["source"])
        self.assertEqual(first["scenario"]["worker_proposals"], second["scenario"]["worker_proposals"])
        self.assertNotEqual(reference_rows(first), reference_rows(second))
        # No expected answer, family, or substantive identifier is supplied in
        # the controller's public input. Actual labels require a later run.
        self.assertEqual(first["public"], second["public"])
        self.assertNotIn("family", first["public"])
        self.assertNotIn("case_id", first["public"])

    def test_development_source_fixtures_have_well_defined_reference(self):
        for case in generate_cases("development"):
            with self.subTest(case=case["case_id"]):
                rows = reference_rows(case)
                self.assertEqual(len(rows), len(case["source"]["orders"]))
                self.assertTrue(all(type(row["net_cents"]) is int for row in rows))


if __name__ == "__main__":
    unittest.main()
