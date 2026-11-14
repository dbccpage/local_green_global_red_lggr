"""
Break-and-recover mutation tests for LGGR II.

Probes fault injection, domain contract violations, collapsing detectors,
additive overflows, and unsupported evidence-level escalation.
"""

import pytest
from organizational_gluing_core import (
    BoundaryCut,
    BoundaryOwner,
    CompositionRecord,
    DefinitionalNecessityGuard,
    DetectorAdequacyGuard,
    EvaluatorGluingDefect,
    EvidenceCeiling,
    FunctionUnit,
    LocalValidator,
    NonAdditivityAuditor,
    ObservedPerformanceTrace,
    OrganizationalClosureConditions,
    OrganizationalEvaluatorSystem,
    WeakSufficiencyAuditor,
)


class TestInvasiveFaultInjections:
    """12 break-and-recover mutation tests."""

    def test_injection_1_non_binary_validator_verdict(self):
        BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        # Mutate validator to return float 0.5
        v_bad = LocalValidator("VBad", f1, lambda t: 0.5)  # type: ignore
        with pytest.raises(ValueError, match="must return an exact bool"):
            v_bad.evaluate({})

        # Recovery: wrap with an explicit Boolean threshold
        v_recovered = LocalValidator("VFixed", f1, lambda t: v_bad.evaluator_fn(t) >= 1.0)
        assert v_recovered.evaluate({}) == 0

    def test_injection_2_non_binary_global_evaluator_verdict(self):
        cut = BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        v1 = LocalValidator("V1", f1, lambda t: True)
        # Mutate global evaluator to return string
        sys_bad = OrganizationalEvaluatorSystem(cut, [f1], [v1], lambda t: "PASS")  # type: ignore
        with pytest.raises(ValueError, match="must return an exact bool"):
            sys_bad.evaluate({})

        # Recovery: exact Boolean verdict
        sys_recovered = OrganizationalEvaluatorSystem(cut, [f1], [v1], lambda t: bool(t.get("success")))
        assert sys_recovered.evaluate({"success": True}).delta_E == 0

    def test_injection_3_missing_boundary_owner_refuses_closure(self):
        cond_no_owner = OrganizationalClosureConditions(g_rep=True, g_auth=False, g_time=True)
        # Break: Attempt to declare boundary certified closed (L^1_declared = 0)
        with pytest.raises(PermissionError, match="requires G_auth"):
            DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_no_owner, declared_L1_zero=True)

        # Recovery: Appoint accountable boundary owner
        owner = BoundaryOwner("Alice", "Chief Risk Officer", has_authority=True, has_accountability=True)
        cond_recovered = OrganizationalClosureConditions(g_rep=True, g_auth=owner.is_complete, g_time=True)
        DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_recovered, declared_L1_zero=True)

    def test_injection_4_authority_without_accountability_refuses_closure(self):
        owner_no_acc = BoundaryOwner("Bob", "TechLead", has_authority=True, has_accountability=False)
        assert owner_no_acc.is_complete is False
        cond = OrganizationalClosureConditions(g_rep=True, g_auth=owner_no_acc.is_complete, g_time=True)
        with pytest.raises(PermissionError, match="requires G_auth"):
            DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond, declared_L1_zero=True)

        # Recovery: Bind accountability to global business outcome
        owner_acc = BoundaryOwner("Bob", "TechLead", has_authority=True, has_accountability=True)
        cond_rec = OrganizationalClosureConditions(g_rep=True, g_auth=owner_acc.is_complete, g_time=True)
        DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_rec, declared_L1_zero=True)

    def test_injection_5_accountability_without_authority_refuses_closure(self):
        owner_no_auth = BoundaryOwner("Charlie", "ProductManager", has_authority=False, has_accountability=True)
        assert owner_no_auth.is_complete is False
        cond = OrganizationalClosureConditions(g_rep=True, g_auth=owner_no_auth.is_complete, g_time=True)
        with pytest.raises(PermissionError, match="requires G_auth"):
            DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond, declared_L1_zero=True)

        # Recovery: Grant authority to install boundary tests
        owner_auth = BoundaryOwner("Charlie", "ProductManager", has_authority=True, has_accountability=True)
        cond_rec = OrganizationalClosureConditions(g_rep=True, g_auth=owner_auth.is_complete, g_time=True)
        DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_rec, declared_L1_zero=True)

    def test_injection_6_corrupted_cut_tokens(self):
        with pytest.raises(ValueError, match="non-empty incoming and outgoing"):
            BoundaryCut("Cut", "", "Out")
        with pytest.raises(ValueError, match="non-empty name"):
            BoundaryCut("   ", "In", "Out")

        # Recovery: Well-formed cut
        cut = BoundaryCut("Cut", "In_Token", "Out_Token")
        assert cut.name == "Cut"

    def test_injection_7_collapsing_detector_caught(self):
        BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        # Collapsing validator that is identical to EG
        v_collapse = LocalValidator("VCollapse", f1, lambda t: t["outcome"])
        global_eval = lambda t: t["outcome"]
        traces = [{"outcome": False}, {"outcome": True}, {"outcome": True}]

        is_collapsing = DetectorAdequacyGuard.is_aligned_validator_collapsing([v_collapse], traces, global_eval)
        assert is_collapsing is True

        # A copied E_G validator alone collapses, but a failing peer prevents
        # collapse when the complete product disagrees with a passing E_G.
        v_peer = LocalValidator("VPeer", f1, lambda t: t["peer"])
        traces_with_failure = [
            {"outcome": False, "peer": False},
            {"outcome": True, "peer": False},
        ]
        assert DetectorAdequacyGuard.is_aligned_validator_collapsing(
            [v_collapse, v_peer], traces_with_failure, global_eval
        ) is False

        # Recovery: independent local evidence with no product/global collapse.
        v_independent = LocalValidator("VIndep", f1, lambda t: t["internal_check"])
        traces_indep = [
            {"outcome": False, "internal_check": True},
            {"outcome": True, "internal_check": False},
        ]
        assert DetectorAdequacyGuard.is_aligned_validator_collapsing(
            [v_independent], traces_indep, global_eval
        ) is False

    def test_injection_8_degenerate_green_refused_without_certificate(self):
        defect_green = EvaluatorGluingDefect(0, 1, (1, 1), 1)
        audit_res = DetectorAdequacyGuard.audit_verdict(defect_green, has_detector_adequacy_cert=False)
        assert audit_res["soundness"] == "UNSOUND_AS_CERTIFICATE"
        assert audit_res["certified"] is False

        # Recovery: Caller-declared adequacy certificate is reported as diagnostic observation,
        # never minting certified closure without verified owner and governance audit.
        audit_res_cert = DetectorAdequacyGuard.audit_verdict(defect_green, has_detector_adequacy_cert=True)
        assert audit_res_cert["soundness"] == "OBSERVED_AGREEMENT_ADEQUACY_DECLARED"
        assert audit_res_cert["certified"] is False

    def test_injection_9_additive_defect_sum_overflow(self):
        # Three failed channels summing to -3
        raw_sum = NonAdditivityAuditor.direct_scalar_sum([-1, -1, -1])
        assert NonAdditivityAuditor.is_range_violation(raw_sum) is True

        # Recovery: Replace direct scalar addition with non-disjoint Shapley attribution
        players = ["rep", "auth", "time"]
        v_fn = lambda c: 1.0 if set(players).issubset(c) else 0.0
        phi = NonAdditivityAuditor.compute_shapley_attribution(players, v_fn)
        # Each channel receives 1/3, summing to 1.0 within bounded scope
        assert all(0.0 <= val <= 1.0 for val in phi.values())
        assert pytest.approx(sum(phi.values()), 0.001) == 1.0

    def test_injection_10_weak_sufficiency_spoof_refuted(self):
        res = WeakSufficiencyAuditor.evaluate_counterexample()
        # Even though representation completely determines EG (weak sufficiency),
        # evaluator factorization fails: EG != E1 * E2
        assert res["refutes_factorization_implication"] is True

    def test_injection_11_temporal_mismatch_blocks_closure(self):
        cond_clock_desync = OrganizationalClosureConditions(g_rep=True, g_auth=True, g_time=False)
        assert cond_clock_desync.governance_prerequisites_satisfied is False
        assert DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(
            cond_clock_desync.g_auth, cond_clock_desync.g_rep, cond_clock_desync.g_time
        ) is True

        # Recovery: Synchronize temporal gauges
        cond_sync = OrganizationalClosureConditions(g_rep=True, g_auth=True, g_time=True)
        assert cond_sync.governance_prerequisites_satisfied is True

    def test_injection_12_evidence_ceiling_escalation_capped(self):
        trace = ObservedPerformanceTrace("C-1", "COMP-1", "L", "R", True, True, False)
        # Attempt to create record with CertifiedTerminal authority via from_trace
        rec = CompositionRecord.from_trace(trace, claimed_ceiling=EvidenceCeiling.CertifiedTerminal)
        # Asserts prospective ceiling is strictly capped at BoundaryChecked
        assert rec.evidence_ceiling == EvidenceCeiling.BoundaryChecked
        assert rec.evidence_ceiling != EvidenceCeiling.CertifiedTerminal

        # Direct construction or replace attempting CertifiedTerminal raises PermissionError
        with pytest.raises(PermissionError):
            CompositionRecord("COMP-1", "L", "R", True, True, False, -1, EvidenceCeiling.CertifiedTerminal)
        from dataclasses import replace
        with pytest.raises(PermissionError):
            replace(rec, evidence_ceiling=EvidenceCeiling.CertifiedTerminal)
