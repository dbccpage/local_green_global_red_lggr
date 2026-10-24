"""Prepared-half locks for the learn/ course. Your-turn dicts are not read."""
from __future__ import annotations

import unittest

from learn.harness_adapter import bind, wire_handoff, wire_review_cycle, wire_tool_loop
from learn.support import LESSONS, load_lesson


EXPECTED = {
    "00": "WITNESS_INCOMPLETE",
    "01": "REPORT_INSUFFICIENT",
    "02": "NGD",
    "03": "ALERT",
    "04": "CYCLE_CLOSED",
    "05": "RETRACTION_VERIFIED",
    "06": "COMPOSABLE_LGGG",
    "07": "RSI_FIBER_CEILING_LOCKED_LGGR",
    "08": "THREE_STOPS_RECORDED",
    "09": "GLOBAL_SAMPLE_REJECTED",
}


def _row(lesson_id: str) -> dict:
    stem = dict(LESSONS)[lesson_id]
    module = load_lesson(stem)
    row = module.prepared()
    if row["status"] != module.EXPECTED_STATUS or row["status"] != EXPECTED[lesson_id]:
        raise AssertionError(f"{lesson_id} status drifted: {row['status']}")
    if row["authority_effect"] != "None":
        raise AssertionError(lesson_id)
    return row


class LearnPathTests(unittest.TestCase):
    def test_scorecard_statuses(self) -> None:
        for lesson_id, _stem in LESSONS:
            row = _row(lesson_id)
            self.assertEqual(row["status"], EXPECTED[lesson_id])
            self.assertEqual(row["lesson_id"], lesson_id)

    def test_lesson_00_emits_no_contract_status(self) -> None:
        row = _row("00")
        self.assertNotIn("contract_status", row)
        self.assertEqual(row["missing"], ["scope_id", "report", "query"])

    def test_lesson_01_names_the_collision(self) -> None:
        row = _row("01")
        self.assertEqual(row["contract_status"], "OBSTRUCTED_LGGR")
        self.assertIn("collision", row["summary"])

    def test_lesson_02_panel(self) -> None:
        row = _row("02")
        self.assertEqual(row["delta"], -1)
        self.assertEqual([item["defect_kind"] for item in row["rows"]], ["NGD", "ZDR", "PGD"])
        self.assertEqual([item["delta"] for item in row["rows"]], [-1, 0, 1])

    def test_lesson_03_prefix_and_endpoint_differ(self) -> None:
        row = _row("03")
        self.assertIn("PREFIX_BUDGET_EXCEEDED", row["alert_reasons"])
        self.assertEqual(row["endpoint_status"], "COMPOSITION_VERIFIED")
        self.assertIs(row["endpoint_global_verdict"], True)
        self.assertIs(row["endpoint_every_prefix_verdict"], False)
        self.assertEqual(row["prefix_status"], "OBSTRUCTION_DETECTED")
        self.assertIs(row["prefix_global_verdict"], False)

    def test_lesson_04_cycle_and_exact_coboundary(self) -> None:
        row = _row("04")
        self.assertNotEqual(row["closure_defect"], "0")
        self.assertEqual(row["exact_status"], "EXACT")
        self.assertIs(row["exact_represents_nonzero_H1"], False)

    def test_lesson_05_lossy_map_does_not_reflect(self) -> None:
        row = _row("05")
        self.assertIs(row["faithful_reflection"], True)
        self.assertEqual(row["lossy_status"], "COMMUTING_TRANSPORT_VERIFIED")
        self.assertIs(row["lossy_forward_commutes"], True)
        self.assertIs(row["lossy_reflection"], False)
        self.assertIs(row["lossy_reflection_certified"], False)

    def test_lesson_06_boundary(self) -> None:
        row = _row("06")
        self.assertEqual(row["fiber_status"], "DECODER_VERIFIED")
        self.assertEqual(row["audit_status"], "COMPOSITION_VERIFIED")
        self.assertIs(row["composition_certified"], True)
        self.assertEqual(row["step_classifications"], ["ZDR", "ZDR", "ZDR"])
        self.assertEqual(row["step_defects"], [0, 0, 0])

    def test_lesson_07_ceiling_and_refinement(self) -> None:
        row = _row("07")
        self.assertEqual(row["coarse_half_spread_ceiling"], "1/2")
        self.assertEqual(row["coarse_statuses"], [
            "RSI_FIBER_CEILING_LOCKED_LGGR",
            "RSI_FIBER_CEILING_LOCKED_LGGR",
            "RSI_FIBER_CEILING_LOCKED_LGGR",
        ])
        self.assertIs(row["midpoint_attained"], True)
        self.assertEqual(row["refined_status"], "EVIDENCE_REFINEMENT_RESOLVED_LGGG")
        self.assertEqual(row["refined_worst_case_error"], "0")

    def test_lesson_08_maps_three_receipts(self) -> None:
        row = _row("08")
        mapped = {item["reason"]: item["status"] for item in row["stops"]}
        self.assertEqual(mapped, {
            "REPORT_COLLISION": "REPORT_INSUFFICIENT",
            "LIFT_BUDGET_EXHAUSTION": "ALERT",
            "OVERLAP_GLUING_REFUSAL": "CYCLE_CLOSED",
        })

    def test_lesson_09_external_sample_and_obligations(self) -> None:
        row = _row("09")
        self.assertIsNone(row["monitor_receipt"])
        self.assertEqual(row["authority_status"], "AUTHORITY_REQUIRED")
        self.assertEqual(row["obligation_status"], "WITNESS_INCOMPLETE")
        self.assertIn("verify-new-interface-semantics", row["unresolved_obligations"])

    def test_adapter_rejects_proposer_sample(self) -> None:
        declaration = {
            "scope_id": "adapter",
            "query_scope": "endpoint",
            "bound": 1,
            "global_sample_source": "external",
            "authority_id": "external-owner/v1",
            "evaluator_id": "bounded-step/v1",
            "policy_id": "budget-policy/v1",
        }
        guard = bind(declaration)
        rejected = guard.step({
            "before": {"state_id": "s0", "value": 0},
            "after": {"state_id": "s1", "value": 1},
            "global_sample": 1,
            "global_sample_source": "proposer",
        })
        self.assertEqual(rejected["status"], "GLOBAL_SAMPLE_REJECTED")
        self.assertIsNone(rejected["monitor_receipt"])
        self.assertEqual(rejected["authority_effect"], "None")

    def test_adapter_keeps_obligations(self) -> None:
        declaration = {
            "scope_id": "adapter-obligations",
            "query_scope": "endpoint",
            "bound": 1,
            "global_sample_source": "external",
            "authority_id": "external-owner/v1",
            "evaluator_id": "bounded-step/v1",
            "policy_id": "budget-policy/v1",
            "allowed_states": [0, 1],
        }
        receipts = wire_tool_loop(declaration, [{
            "before": {"state_id": "s0", "value": 0},
            "after": {"state_id": "s1", "value": 1},
            "global_sample": 1,
            "obligations": ["keep-me"],
        }])
        summary = receipts[-1]["monitor_receipt"]
        self.assertIn("keep-me", summary["unresolved_obligations"])
        self.assertFalse(hasattr(bind(declaration), "clear_obligations"))

    def test_adapter_wires_handoff_and_cycle(self) -> None:
        declaration = {
            "scope_id": "adapter-shapes",
            "query_scope": "endpoint",
            "bound": 1,
            "global_sample_source": "external",
            "authority_id": "external-owner/v1",
            "evaluator_id": "bounded-step/v1",
            "policy_id": "budget-policy/v1",
        }
        handoffs = wire_handoff(declaration, [
            {"state_id": "a", "report": {"summary": "same"}, "query": {"tier": 1}},
            {"state_id": "b", "report": {"summary": "same"}, "query": {"tier": 2}},
        ])
        self.assertEqual(handoffs[-1]["status"], "REPORT_INSUFFICIENT")
        edges = wire_review_cycle(declaration, [
            {"src": "A", "dst": "B", "value": "1"},
            {"src": "B", "dst": "C", "value": "1"},
            {"src": "C", "dst": "A", "value": "1"},
        ])
        self.assertEqual(edges[-1]["status"], "CYCLE_CLOSED")
        self.assertNotEqual(edges[-1]["monitor_receipt"]["closure_defect"], "0")

    def test_adapter_generation_keeps_the_coarse_ceiling(self) -> None:
        declaration = {
            "scope_id": "adapter-rsi",
            "query_scope": "endpoint",
            "bound": 1,
            "global_sample_source": "external",
            "authority_id": "external-owner/v1",
            "evaluator_id": "bounded-step/v1",
            "policy_id": "budget-policy/v1",
        }
        guard = bind(declaration)
        guard.generation({
            "state_id": "h0",
            "coarse_report": {"channel": "summary"},
            "target": "0",
            "prediction": "1/2",
        })
        scored = guard.generation({
            "state_id": "h1",
            "coarse_report": {"channel": "summary"},
            "target": "1",
            "prediction": "1/2",
            "evaluate": True,
            "generation_id": "g0",
        })
        self.assertEqual(scored["status"], "RSI_FIBER_CEILING_LOCKED_LGGR")
        self.assertEqual(scored["monitor_receipt"]["coarse_half_spread_ceiling"], "1/2")


if __name__ == "__main__":
    unittest.main()
