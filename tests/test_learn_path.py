"""Prepared-half locks for the learn/ course. Your-turn dicts are not read."""
from __future__ import annotations

import io
import json
import re
import unittest
from pathlib import Path

from learn.harness_adapter import bind, wire_handoff, wire_review_cycle, wire_tool_loop
from learn.support import LESSONS, RECIPES, load_lesson, load_recipe


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

    def test_negative_external_sample_stays_an_obstruction(self) -> None:
        declaration = {
            "scope_id": "adapter-ngd",
            "query_scope": "endpoint",
            "bound": 2,
            "global_sample_source": "external",
            "authority_id": "external-owner/v1",
            "evaluator_id": "bounded-step/v1",
            "policy_id": "budget-policy/v1",
            "allowed_states": [0, 1, 2],
            "max_step": 1,
        }
        receipts = wire_tool_loop(declaration, [{
            "before": {"state_id": "s0", "value": 0},
            "after": {"state_id": "s1", "value": 1},
            "global_sample": 0,
        }])
        self.assertEqual([item["status"] for item in receipts], ["ALERT", "OBSTRUCTION_DETECTED"])
        summary = receipts[-1]["monitor_receipt"]
        self.assertFalse(summary["composition_certified"])
        self.assertEqual(summary["alerts_count"], 1)
        self.assertEqual(summary["findings"][0]["code"], "NGD_DEFECT_DETECTED")

    def test_tool_loop_stops_on_refusal(self) -> None:
        declaration = {
            "scope_id": "adapter-stop",
            "query_scope": "endpoint",
            "bound": 2,
            "global_sample_source": "external",
            "authority_id": "external-owner/v1",
            "evaluator_id": "bounded-step/v1",
            "policy_id": "budget-policy/v1",
            "allowed_states": [0, 1, 2],
            "max_step": 2,
        }
        accepted = {
            "before": {"state_id": "s0", "value": 0},
            "after": {"state_id": "s1", "value": 1},
            "signed_delta": 1,
            "global_sample": 1,
        }
        proposer = wire_tool_loop(declaration, [
            accepted,
            {
                "before": {"state_id": "s1", "value": 1},
                "after": {"state_id": "s2", "value": 0},
                "global_sample": 1,
                "global_sample_source": "proposer",
            },
        ])
        self.assertEqual([item["status"] for item in proposer], ["OK", "GLOBAL_SAMPLE_REJECTED"])
        mismatch = wire_tool_loop(declaration, [
            accepted,
            {
                "before": {"state_id": "s1", "value": 1},
                "after": {"state_id": "s2", "value": 0},
                "signed_delta": 5,
                "global_sample": 1,
            },
        ])
        self.assertEqual([item["status"] for item in mismatch], ["OK", "SIGNED_DELTA_MISMATCH"])

    def test_omitted_refined_report_uses_the_coarse_report(self) -> None:
        declaration = {
            "scope_id": "adapter-refined-fallback",
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
            "use_refined_report": True,
        })
        scored = guard.generation({
            "state_id": "h1",
            "coarse_report": {"channel": "summary"},
            "target": "1",
            "prediction": "1/2",
            "use_refined_report": True,
            "evaluate": True,
            "generation_id": "g0",
        })
        self.assertEqual(scored["status"], "RSI_FIBER_CEILING_LOCKED_LGGR")
        self.assertEqual(scored["monitor_receipt"]["coarse_half_spread_ceiling"], "1/2")


class RecipeTests(unittest.TestCase):
    """Guide snippets import these recipes, so these locks cover the guides too."""

    def _demo(self, name: str) -> dict:
        module = load_recipe(name)
        row = module.demo()
        self.assertEqual(row["recipe_id"], name)
        self.assertEqual(row["status"], module.EXPECTED_STATUS)
        self.assertEqual(row["authority_effect"], "None")
        return row

    def test_every_recipe_is_registered(self) -> None:
        on_disk = {p.stem for p in Path("learn/recipes").glob("*.py") if p.stem != "__init__"}
        self.assertEqual(on_disk, set(RECIPES))

    def test_collision_guard_blocks_second_handoff(self) -> None:
        row = self._demo("collision_guard")
        self.assertEqual(row["thin_allowed"], [True, False])
        self.assertEqual(row["colliding_pair"]["left"]["state_id"], "task-a")
        self.assertEqual(row["enriched_status"], "DECODER_VERIFIED")
        self.assertEqual(row["enriched_allowed"], [True, True])

    def test_authority_firewall(self) -> None:
        row = self._demo("authority_firewall")
        self.assertEqual(row["tampered_codes"], ["POLICY_MANIFEST_CHANGED"])
        self.assertEqual(row["honest_status"], "COMPOSITION_VERIFIED")
        self.assertIs(row["honest_certified"], True)
        self.assertEqual(row["self_signed_status"], "GLOBAL_SAMPLE_REJECTED")
        self.assertEqual(row["owed_status"], "WITNESS_INCOMPLETE")
        self.assertEqual(row["owed_obligations"], ["recheck_schema"])

    def test_authority_firewall_scope_fields(self) -> None:
        import dataclasses
        from lggr import StateRef, make_witness
        module = load_recipe("authority_firewall")
        policy = module._policy()
        for field in ("evaluator_id", "spec_id", "authority_id"):
            fw = module.AuthorityFirewall(policy, StateRef("s0", 0))
            changed = dataclasses.replace(policy, **{field: "agent-chosen"})
            fw.admit_witness(make_witness(changed, StateRef("s0", 0), StateRef("s1", 1), witness_id="w001"),
                             global_sample=1, sample_source="external")
            verdict = fw.verdict()
            self.assertEqual(verdict["status"], "AUTHORITY_REQUIRED")
            self.assertIn("SEMANTIC_SCOPE_CHANGED", {f["code"] for f in verdict["findings"]})

    def test_check_selector_never_accepts_a_failing_world(self) -> None:
        row = self._demo("check_selector")
        self.assertEqual(row["bought"], ["schema", "fee_e2e"])
        self.assertEqual(row["spent"], 4)
        for world in row["every_world"]:
            expected = "accept" if world["world"] == "H1-clean" else "reject"
            self.assertEqual(world["decision"], expected)
            self.assertLessEqual(world["spent"], 4)
        self.assertEqual(row["cheapest_first_decision"], "defer")

    def test_check_selector_host_rule(self) -> None:
        module = load_recipe("check_selector")
        self.assertEqual(module.host_rule([]), "model_mismatch")
        both = [{"id": "p", "verdict": "pass"}, {"id": "f", "verdict": "fail"}]
        self.assertEqual(module.host_rule(both), "defer")

    def test_checked_memory_labels(self) -> None:
        row = self._demo("checked_memory")
        self.assertEqual(row["after_restart"], "FRESH")
        self.assertEqual(row["after_source_edit"], "STALE_SOURCE")
        self.assertEqual(row["after_policy_change"], "STALE_CONTRACT")
        self.assertEqual(row["two_writers"], ["CONFLICT", "CONFLICT"])
        self.assertEqual(row["obligations_every_recall"], [1, 1, 1])

    def test_checked_memory_representation_change(self) -> None:
        import dataclasses
        from lggr import BudgetPolicy
        module = load_recipe("checked_memory")
        policy = BudgetPolicy()
        memory = module.CheckedMemory()
        memory.append("k", "v", source_ref="a", source_text="x", policy=policy)
        moved = dataclasses.replace(policy, representation_id="rep-v2")
        hit = memory.recall("k", sources={"a": "x"}, policy=moved)["records"][0]
        self.assertEqual(hit["status"], "TRANSPORT_REQUIRED")


class SidecarTests(unittest.TestCase):
    def _serve(self, lines: list[dict]) -> list[dict]:
        from learn.sidecar import serve
        out = io.StringIO()
        serve(io.StringIO("\n".join(json.dumps(line) for line in lines) + "\n"), out)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    _DECLARE = {"declare": {
        "scope_id": "sidecar-test", "query_scope": "every_prefix", "bound": 1,
        "global_sample_source": "external", "authority_id": "release-owner",
        "evaluator_id": "ci-local/v1", "policy_id": "deploy-budget/v1",
    }}

    def test_round_trip_matches_adapter(self) -> None:
        receipts = self._serve([
            self._DECLARE,
            {"event": "handoff", "state_id": "a", "report": {"s": "ship"}, "query": {"tier": 3}},
            {"event": "handoff", "state_id": "b", "report": {"s": "ship"}, "query": {"tier": 1}},
            {"event": "step", "before": {"state_id": "s0", "value": 0},
             "after": {"state_id": "s1", "value": 1}, "global_sample": 1},
            {"event": "summary"},
        ])
        self.assertEqual([r["status"] for r in receipts],
                         ["DECLARED", "OK", "REPORT_INSUFFICIENT", "OK", "COMPOSITION_VERIFIED"])
        self.assertTrue(all(r["authority_effect"] == "None" for r in receipts))

    def test_bad_lines_are_reported_not_fatal(self) -> None:
        receipts = self._serve([{"event": "summary"}, self._DECLARE, {"event": "bogus"}, {"event": "summary"}])
        self.assertEqual([r["status"] for r in receipts],
                         ["INVALID_EVENT", "DECLARED", "INVALID_EVENT", "WITNESS_INCOMPLETE"])

    def test_proposer_sample_is_rejected_at_declaration(self) -> None:
        declare = {"declare": {**self._DECLARE["declare"], "global_sample_source": "proposer"}}
        receipts = self._serve([declare, {"event": "summary"}])
        self.assertEqual([r["status"] for r in receipts], ["GLOBAL_SAMPLE_REJECTED", "GLOBAL_SAMPLE_REJECTED"])


class GuideLinkTests(unittest.TestCase):
    def test_relative_links_in_learn_markdown_resolve(self) -> None:
        for doc in list(Path("learn").glob("*.md")) + list(Path("learn/guides").glob("*.md")):
            text = doc.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                self.assertTrue((doc.parent / target).exists(), f"{doc}: broken link {target}")


if __name__ == "__main__":
    unittest.main()
