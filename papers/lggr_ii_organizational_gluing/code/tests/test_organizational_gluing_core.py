"""
Unit tests for the organizational evaluator gluing core.

Targeting full statement and branch coverage of organizational_gluing_core.py.
"""

from dataclasses import replace
import pytest
from organizational_gluing_core import (
    BooleanBoundary,
    BoundaryCut,
    BoundaryOwner,
    CaseStudyFactory,
    CompositionRecord,
    ComposedTrace,
    DefectSign,
    DefinitionalNecessityGuard,
    DetectorAdequacyGuard,
    EvaluatorGluingDefect,
    EvidenceCeiling,
    FiniteTheoremCensus,
    FunctionUnit,
    LocalValidator,
    NonAdditivityAuditor,
    ObservedPerformanceTrace,
    OrganizationalClosureConditions,
    OrganizationalEvaluatorSystem,
    WeakSufficiencyAuditor,
    carrier_local_product,
    evaluator_factorization,
    joint_carrier,
    org_delta,
    product_sufficiency,
    weak_boundary_sufficiency,
)


class TestBoundaryCutAndUnits:
    def test_valid_boundary_cut(self):
        cut = BoundaryCut("Cut1", "IncomingPole", "OutgoingPole", "A test cut")
        assert cut.name == "Cut1"
        assert cut.incoming_token == "IncomingPole"
        assert cut.outgoing_token == "OutgoingPole"
        assert cut.description == "A test cut"

    def test_invalid_boundary_cut_empty_name(self):
        with pytest.raises(ValueError, match="non-empty name"):
            BoundaryCut("", "In", "Out")

    def test_invalid_boundary_cut_empty_tokens(self):
        with pytest.raises(ValueError, match="non-empty incoming and outgoing"):
            BoundaryCut("Cut", "", "Out")
        with pytest.raises(ValueError, match="non-empty incoming and outgoing"):
            BoundaryCut("Cut", "In", "   ")

    def test_function_unit(self):
        fn = FunctionUnit("Eng", "Engineering", "Builds things")
        assert fn.name == "Eng"
        assert fn.department == "Engineering"


class TestBoundaryOwner:
    def test_owner_completeness(self):
        # Both authority and accountability
        o1 = BoundaryOwner("Alice", "VP", has_authority=True, has_accountability=True)
        assert o1.is_complete is True

        # Authority without accountability
        o2 = BoundaryOwner("Bob", "Director", has_authority=True, has_accountability=False)
        assert o2.is_complete is False

        # Accountability without authority
        o3 = BoundaryOwner("Charlie", "PM", has_authority=False, has_accountability=True)
        assert o3.is_complete is False

        # Neither
        o4 = BoundaryOwner("Dave", "Intern", has_authority=False, has_accountability=False)
        assert o4.is_complete is False

    def test_owner_rejects_non_boolean_flags(self):
        for invalid in (0, 1, "True", "False", None, 1.0):
            with pytest.raises(TypeError, match="must be an exact bool"):
                BoundaryOwner("Alice", "VP", has_authority=invalid, has_accountability=True)  # type: ignore
            with pytest.raises(TypeError, match="must be an exact bool"):
                BoundaryOwner("Alice", "VP", has_authority=True, has_accountability=invalid)  # type: ignore


class TestEvaluatorGluingDefect:
    def test_defect_trichotomy_and_invariants(self):
        # Local green, global red: EG=0, local_prod=1 => delta = -1
        d_lggr = EvaluatorGluingDefect(
            delta_E=-1,
            global_evaluator_pass=0,
            local_evaluator_passes=(1, 1),
            local_product=1,
        )
        assert d_lggr.is_local_green_global_red is True
        assert d_lggr.is_evaluator_agreement is False
        assert d_lggr.is_unearned_success is False
        assert d_lggr.defect_sign == DefectSign.LOCAL_GREEN_GLOBAL_RED

        # Composing (all pass): EG=1, local_prod=1 => delta = 0
        d_comp = EvaluatorGluingDefect(
            delta_E=0,
            global_evaluator_pass=1,
            local_evaluator_passes=(1, 1),
            local_product=1,
        )
        assert d_comp.is_evaluator_agreement is True
        assert d_comp.defect_sign == DefectSign.EVALUATOR_AGREEMENT

        # Composing (all fail): EG=0, local_prod=0 => delta = 0
        d_fail = EvaluatorGluingDefect(
            delta_E=0,
            global_evaluator_pass=0,
            local_evaluator_passes=(0, 1),
            local_product=0,
        )
        assert d_fail.is_evaluator_agreement is True

        # Unearned success: EG=1, local_prod=0 => delta = 1
        d_unearned = EvaluatorGluingDefect(
            delta_E=1,
            global_evaluator_pass=1,
            local_evaluator_passes=(0, 1),
            local_product=0,
        )
        assert d_unearned.is_unearned_success is True
        assert d_unearned.defect_sign == DefectSign.UNEARNED_SUCCESS

    def test_invalid_defect_construction(self):
        with pytest.raises(ValueError, match="must be in"):
            EvaluatorGluingDefect(delta_E=-2, global_evaluator_pass=0, local_evaluator_passes=(1,), local_product=1)
        with pytest.raises(ValueError, match="global_evaluator_pass must be a binary integer"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=2, local_evaluator_passes=(1,), local_product=1)
        with pytest.raises(ValueError, match="local_evaluator_passes must be binary"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=1, local_evaluator_passes=(2,), local_product=1)
        with pytest.raises(ValueError, match="binary integer"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=1.0, local_evaluator_passes=(1,), local_product=1)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="binary integers"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=1, local_evaluator_passes=(1.0,), local_product=1)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="local_product must be a binary integer"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=1, local_evaluator_passes=(1,), local_product=1.0)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="delta_E must be in"):
            EvaluatorGluingDefect(delta_E=False, global_evaluator_pass=1, local_evaluator_passes=(1,), local_product=1)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="local_product mismatch"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=1, local_evaluator_passes=(1, 0), local_product=1)
        with pytest.raises(ValueError, match="delta_E mismatch"):
            EvaluatorGluingDefect(delta_E=0, global_evaluator_pass=0, local_evaluator_passes=(1, 1), local_product=1)

    def test_defect_local_evaluator_passes_materializes_immutable_tuple(self):
        mutable_passes = [1, 1]
        defect = EvaluatorGluingDefect(
            delta_E=-1, global_evaluator_pass=0, local_evaluator_passes=mutable_passes, local_product=1  # type: ignore[arg-type]
        )
        assert isinstance(defect.local_evaluator_passes, tuple)
        assert defect.local_evaluator_passes == (1, 1)
        mutable_passes[0] = 0
        mutable_passes.append(0)
        assert defect.local_evaluator_passes == (1, 1)

    def test_defect_local_evaluator_passes_iterator_consumed_once(self):
        # Generator yielding 0 and 1 has local_product 0.
        # If consumed twice without materialization, the second iteration sees an empty iterator
        # where all() vacuously returns True, wrongly accepting local_product=1.
        it_bad = (x for x in (0, 1))
        with pytest.raises(ValueError, match="local_product mismatch"):
            EvaluatorGluingDefect(
                delta_E=0, global_evaluator_pass=1, local_evaluator_passes=it_bad, local_product=1  # type: ignore[arg-type]
            )
        it_good = (x for x in (0, 1))
        defect = EvaluatorGluingDefect(
            delta_E=1, global_evaluator_pass=1, local_evaluator_passes=it_good, local_product=0  # type: ignore[arg-type]
        )
        assert defect.local_evaluator_passes == (0, 1)
        assert defect.local_product == 0
        assert defect.delta_E == 1


class TestOrganizationalEvaluatorSystem:
    def test_empty_validators_raises(self):
        cut = BoundaryCut("Cut", "In", "Out")
        with pytest.raises(ValueError, match="at least one local validator"):
            OrganizationalEvaluatorSystem(cut, [], [], lambda t: True)

    def test_system_evaluation_success(self):
        cut = BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        f2 = FunctionUnit("F2", "D2")
        v1 = LocalValidator("V1", f1, lambda t: t["v1"])
        v2 = LocalValidator("V2", f2, lambda t: t["v2"])
        global_fn = lambda t: t["g"]
        owner = BoundaryOwner("Alice", "Lead", True, True)

        sys = OrganizationalEvaluatorSystem(cut, [f1, f2], [v1, v2], global_fn, owner)

        # Trace 1: LGGR
        defect = sys.evaluate({"v1": True, "v2": True, "g": False})
        assert defect.delta_E == -1
        assert defect.local_evaluator_passes == (1, 1)
        assert defect.global_evaluator_pass == 0
        assert type(defect.delta_E) is int
        assert type(defect.global_evaluator_pass) is int
        assert all(type(value) is int for value in defect.local_evaluator_passes)

        # Trace 2: Composing
        defect2 = sys.evaluate({"v1": True, "v2": True, "g": True})
        assert defect2.delta_E == 0

    def test_validator_non_binary_raises(self):
        BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        for bad_value in (0, 1, 0.0, 1.0, "true", None):
            v1 = LocalValidator("V1", f1, lambda t, value=bad_value: value)  # type: ignore[arg-type]
            with pytest.raises(ValueError, match="must return an exact bool"):
                v1.evaluate({})

    def test_global_evaluator_non_binary_raises(self):
        cut = BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        v1 = LocalValidator("V1", f1, lambda t: True)
        for bad_value in (0, 1, 0.0, 1.0, "PASS", None):
            sys = OrganizationalEvaluatorSystem(
                cut, [f1], [v1], lambda t, value=bad_value: value  # type: ignore[arg-type]
            )
            with pytest.raises(ValueError, match="must return an exact bool"):
                sys.evaluate({})


class TestOrganizationalClosureConditions:
    def test_conjunction_and_checked_closure_eligibility(self):
        c_all = OrganizationalClosureConditions(g_rep=True, g_auth=True, g_time=True)
        assert c_all.governance_prerequisites_satisfied is True

        # Checked closure eligibility requires BOTH governance AND evaluator agreement
        defect_agree = EvaluatorGluingDefect(0, 1, (1, 1), 1)
        defect_lggr = EvaluatorGluingDefect(-1, 0, (1, 1), 1)
        assert c_all.is_checked_closure_eligible(defect_agree) is True
        assert c_all.is_checked_closure_eligible(defect_lggr) is False  # P0: governance alone insufficient

        c_no_rep = OrganizationalClosureConditions(g_rep=False, g_auth=True, g_time=True)
        assert c_no_rep.governance_prerequisites_satisfied is False
        assert c_no_rep.is_checked_closure_eligible(defect_agree) is False

        c_no_auth = OrganizationalClosureConditions(g_rep=True, g_auth=False, g_time=True)
        assert c_no_auth.governance_prerequisites_satisfied is False

        c_no_time = OrganizationalClosureConditions(g_rep=True, g_auth=True, g_time=False)
        assert c_no_time.governance_prerequisites_satisfied is False

    def test_closure_conditions_reject_non_boolean_flags(self):
        for invalid in (0, 1, "True", "False", None, 1.0):
            with pytest.raises(TypeError, match="must be an exact bool"):
                OrganizationalClosureConditions(g_rep=invalid, g_auth=True, g_time=True)  # type: ignore
            with pytest.raises(TypeError, match="must be an exact bool"):
                OrganizationalClosureConditions(g_rep=True, g_auth=invalid, g_time=True)  # type: ignore
            with pytest.raises(TypeError, match="must be an exact bool"):
                OrganizationalClosureConditions(g_rep=True, g_auth=True, g_time=invalid)  # type: ignore

    def test_boundary_governance_audit(self):
        # Case 1: Defect is LGGR (-1), governance prerequisites partially fail
        cond = OrganizationalClosureConditions(g_rep=False, g_auth=True, g_time=True)
        defect_lggr = EvaluatorGluingDefect(-1, 0, (1, 1), 1)
        audit = cond.audit_boundary_governance(defect_lggr)
        assert audit["evaluator_agrees"] is False
        assert audit["closure_eligible"] is False
        assert audit["governance_prerequisites_satisfied"] is False
        assert "G_rep" in audit["failed_prerequisites"]

        # Case 2: Defect is Composing (0), governance prerequisites hold
        cond_ok = OrganizationalClosureConditions(g_rep=True, g_auth=True, g_time=True)
        defect_comp = EvaluatorGluingDefect(0, 1, (1, 1), 1)
        audit_comp = cond_ok.audit_boundary_governance(defect_comp)
        assert audit_comp["evaluator_agrees"] is True
        assert audit_comp["closure_eligible"] is True
        assert audit_comp["governance_prerequisites_satisfied"] is True
        assert len(audit_comp["failed_prerequisites"]) == 0

        # Case 3: Lemma 4.4 counterexample: all governance conditions True, but defect is -1
        audit_lemma = cond_ok.audit_boundary_governance(defect_lggr)
        assert audit_lemma["evaluator_agrees"] is False
        assert audit_lemma["governance_prerequisites_satisfied"] is True
        assert audit_lemma["closure_eligible"] is False

        # Verify contrapositive_audit alias behaves identically
        assert cond_ok.contrapositive_audit(defect_comp) == audit_comp


class TestDefinitionalNecessityGuard:
    def test_auth_necessity_enforcement(self):
        cond_ok = OrganizationalClosureConditions(True, True, True)
        # No raise when auth is present
        DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_ok, declared_L1_zero=True)

        cond_no_auth = OrganizationalClosureConditions(True, False, True)
        with pytest.raises(PermissionError, match="requires G_auth"):
            DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_no_auth, declared_L1_zero=True)

        # When L1 is not zero, no PermissionError is raised regardless of G_auth
        DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond_no_auth, declared_L1_zero=False)

    def test_owner_alone_insufficient(self):
        assert DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=True, g_rep=False, g_time=True) is True
        assert DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=True, g_rep=True, g_time=False) is True
        assert DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=True, g_rep=True, g_time=True) is False
        assert DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=False, g_rep=True, g_time=True) is False

    def test_guard_rejects_non_boolean_inputs(self):
        cond = OrganizationalClosureConditions(True, True, True)
        for invalid in (0, 1, "True", "False", None, 1.0):
            with pytest.raises(TypeError, match="must be an exact bool"):
                DefinitionalNecessityGuard.assert_auth_required_for_declared_closure(cond, declared_L1_zero=invalid)  # type: ignore
            with pytest.raises(TypeError, match="must be an exact bool"):
                DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=invalid, g_rep=True, g_time=True)  # type: ignore
            with pytest.raises(TypeError, match="must be an exact bool"):
                DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=True, g_rep=invalid, g_time=True)  # type: ignore
            with pytest.raises(TypeError, match="must be an exact bool"):
                DefinitionalNecessityGuard.assert_owner_alone_is_insufficient(g_auth=True, g_rep=True, g_time=invalid)  # type: ignore


class TestNonAdditivityAuditor:
    def test_direct_scalar_sum_range_violation(self):
        # 3 channel defects each equal to -1
        total = NonAdditivityAuditor.direct_scalar_sum([-1, -1, -1])
        assert total == -3
        assert NonAdditivityAuditor.is_range_violation(total) is True

        # In-range sum
        total_ok = NonAdditivityAuditor.direct_scalar_sum([-1, 1, 0])
        assert total_ok == 0
        assert NonAdditivityAuditor.is_range_violation(total_ok) is False

    def test_shapley_attribution(self):
        players = ["rep", "auth", "time"]

        # Coalitional game where all 3 are required for closure (value = 1.0, otherwise 0.0)
        def v_conjunction(coalition):
            if set(players).issubset(coalition):
                return 1.0
            return 0.0

        phi = NonAdditivityAuditor.compute_shapley_attribution(players, v_conjunction)
        assert pytest.approx(phi["rep"], 0.001) == 1.0 / 3.0
        assert pytest.approx(phi["auth"], 0.001) == 1.0 / 3.0
        assert pytest.approx(phi["time"], 0.001) == 1.0 / 3.0
        assert pytest.approx(sum(phi.values()), 0.001) == 1.0

    def test_shapley_duplicate_players_raises(self):
        with pytest.raises(ValueError, match="unique identifiers"):
            NonAdditivityAuditor.compute_shapley_attribution(["rep", "rep"], lambda s: 1.0)

    def test_shapley_non_finite_value_raises(self):
        with pytest.raises(ValueError, match="non-finite value"):
            NonAdditivityAuditor.compute_shapley_attribution(["rep"], lambda s: float("inf"))


class TestWeakSufficiencyAuditor:
    def test_weak_sufficiency_counterexample(self):
        res = WeakSufficiencyAuditor.evaluate_counterexample()
        assert res["weak_sufficiency_holds"] is True
        assert res["g_auth"] is True
        assert res["g_time"] is True
        assert res["evaluator_factorization_holds"] is False
        assert res["delta_E"] == -1
        assert res["refutes_factorization_implication"] is True


class TestDetectorAdequacyGuard:
    def test_aligned_collapsing_detector(self):
        BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        # Validator proxies global outcome exactly
        v_proxy = LocalValidator("Proxy", f1, lambda t: t["g"])
        global_fn = lambda t: t["g"]
        traces = [{"g": False}, {"g": True}, {"g": False}]

        is_collapsing = DetectorAdequacyGuard.is_aligned_validator_collapsing([v_proxy], traces, global_fn)
        assert is_collapsing is True

    def test_copied_global_validator_with_failing_peer_is_not_collapsing(self):
        unit = FunctionUnit("F", "D")
        copied_global = LocalValidator("copied global", unit, lambda t: t["g"])
        peer = LocalValidator("peer", unit, lambda t: t["peer"])
        global_fn = lambda t: t["g"]

        # The copied validator agrees pointwise, but at the second trace the
        # peer fails while E_G passes. Hence the complete local product is 0
        # and E_G is 1: M7's premise is false and the detector is not collapsed.
        traces = [
            {"g": False, "peer": False},
            {"g": True, "peer": False},
        ]
        assert DetectorAdequacyGuard.is_aligned_validator_collapsing(
            [copied_global, peer], traces, global_fn
        ) is False

        repaired = [
            {"g": False, "peer": True},
            {"g": True, "peer": True},
        ]
        assert DetectorAdequacyGuard.is_aligned_validator_collapsing(
            [copied_global, peer], repaired, global_fn
        ) is True

    def test_aligned_detector_empty_traces_raises(self):
        BoundaryCut("Cut", "In", "Out")
        f1 = FunctionUnit("F1", "D1")
        v = LocalValidator("V", f1, lambda t: True)
        with pytest.raises(ValueError, match="sample_traces must be non-empty"):
            DetectorAdequacyGuard.is_aligned_validator_collapsing([v], [], lambda t: True)
        with pytest.raises(ValueError, match="validators must be non-empty"):
            DetectorAdequacyGuard.is_aligned_validator_collapsing([], [{}], lambda t: True)

    def test_audit_verdict_asymmetry_and_diagnostics(self):
        # 1. RED verdict: Sound as detection of non-factorization
        d_red = EvaluatorGluingDefect(-1, 0, (1, 1), 1)
        r_red = DetectorAdequacyGuard.audit_verdict(d_red, has_detector_adequacy_cert=False)
        assert r_red["verdict"] == "RED"
        assert r_red["soundness"] == "SOUND_AS_DETECTION"
        assert r_red["certified"] is False

        # 2. GREEN without adequacy cert: Unsound as certificate
        d_green = EvaluatorGluingDefect(0, 1, (1, 1), 1)
        r_green_nocert = DetectorAdequacyGuard.audit_verdict(d_green, has_detector_adequacy_cert=False)
        assert r_green_nocert["verdict"] == "GREEN"
        assert r_green_nocert["soundness"] == "UNSOUND_AS_CERTIFICATE"
        assert r_green_nocert["certified"] is False
        assert r_green_nocert["message"] == "Observed passing evaluator agreement, but detector adequacy has not been established; diagnostic only."

    def test_audit_verdict_rejects_non_boolean_cert(self):
        d_green = EvaluatorGluingDefect(0, 1, (1, 1), 1)
        for invalid in (0, 1, "True", "False", None, 1.0):
            with pytest.raises(TypeError, match="must be an exact bool"):
                DetectorAdequacyGuard.audit_verdict(d_green, has_detector_adequacy_cert=invalid)  # type: ignore

        # 3. GREEN with adequacy cert: Diagnostic only, NOT certified closure
        r_green_cert = DetectorAdequacyGuard.audit_verdict(d_green, has_detector_adequacy_cert=True)
        assert r_green_cert["verdict"] == "GREEN"
        assert r_green_cert["soundness"] == "OBSERVED_AGREEMENT_ADEQUACY_DECLARED"
        assert r_green_cert["certified"] is False

        # 4. Joint failure agreement (EG=0, prod=0): Agreement at failure is not success
        d_joint_fail = EvaluatorGluingDefect(0, 0, (0, 0), 0)
        r_joint = DetectorAdequacyGuard.audit_verdict(d_joint_fail, has_detector_adequacy_cert=True)
        assert r_joint["verdict"] == "AGREEMENT_AT_FAILURE"
        assert r_joint["soundness"] == "OBSERVED_JOINT_FAILURE"
        assert r_joint["certified"] is False

        # 5. Unearned success (EG=1, prod=0)
        d_unearned = EvaluatorGluingDefect(1, 1, (0, 0), 0)
        r_unearned = DetectorAdequacyGuard.audit_verdict(d_unearned)
        assert r_unearned["verdict"] == "UNEARNED_SUCCESS"
        assert r_unearned["soundness"] == "DIAGNOSTIC_ANOMALY"
        assert r_unearned["certified"] is False


class TestCaseStudyWitnesses:
    def test_pear_therapeutics(self):
        sys, cond, defect = CaseStudyFactory.create_pear_therapeutics()
        assert defect.delta_E == -1
        assert defect.is_local_green_global_red is True
        assert cond.g_auth is False
        assert sys.boundary_owner.has_authority is True
        assert sys.boundary_owner.has_accountability is False
        assert sys.boundary_owner.is_complete is False

    def test_northvolt_ett(self):
        sys, cond, defect = CaseStudyFactory.create_northvolt_ett()
        assert defect.delta_E == -1
        assert defect.is_local_green_global_red is True
        assert cond.g_auth is False
        assert sys.boundary_owner.has_authority is False
        assert sys.boundary_owner.has_accountability is True
        assert sys.boundary_owner.is_complete is False

    def test_boeing_mcas(self):
        sys, cond, defect = CaseStudyFactory.create_boeing_mcas()
        assert defect.delta_E == -1
        assert defect.is_local_green_global_red is True
        assert cond.g_auth is False
        assert cond.g_time is False
        assert sys.boundary_owner is None


class TestObservedPerformanceTraceAndRecord:
    def test_schema_mapping_and_ceiling_capping(self):
        trace = ObservedPerformanceTrace(
            contract_id="CNT-001",
            composed_id="COMP-001",
            left_id="LEFT-01",
            right_id="RIGHT-01",
            local_left_pass=True,
            local_right_pass=True,
            global_pass=False,
        )

        rec = CompositionRecord.from_trace(trace, claimed_ceiling=EvidenceCeiling.EmpiricalOracleRequired)
        assert rec.composed_id == "COMP-001"
        assert rec.delta_E == -1
        assert rec.evidence_ceiling == EvidenceCeiling.BoundaryChecked

        # Even if a caller claims CertifiedTerminal, prospective findings are capped
        rec2 = CompositionRecord.from_trace(trace, claimed_ceiling=EvidenceCeiling.CertifiedTerminal)
        assert rec2.evidence_ceiling == EvidenceCeiling.BoundaryChecked

    def test_trace_rejects_non_boolean_verdicts(self):
        with pytest.raises(TypeError, match="must be a bool"):
            ObservedPerformanceTrace("CNT-01", "COMP-01", "L", "R", True, True, "False")  # type: ignore
        with pytest.raises(TypeError, match="must be a bool"):
            ObservedPerformanceTrace("CNT-01", "COMP-01", "L", "R", 1, True, True)  # type: ignore

    def test_composition_record_invariants_and_ceiling_guard(self):
        # Valid construction
        r = CompositionRecord("comp", "l", "r", True, True, False, -1, EvidenceCeiling.BoundaryChecked)
        assert r.delta_E == -1

        # Direct construction with delta_E outside {-1, 0, 1} raises ValueError
        with pytest.raises(ValueError, match="must be in"):
            CompositionRecord("comp", "l", "r", True, True, False, 999, EvidenceCeiling.BoundaryChecked)

        # Direct construction with delta_E mismatch raises ValueError
        with pytest.raises(ValueError, match="delta_E mismatch"):
            CompositionRecord("comp", "l", "r", True, True, False, 0, EvidenceCeiling.BoundaryChecked)

        # Direct construction with non-boolean raises TypeError
        with pytest.raises(TypeError, match="must be a bool"):
            CompositionRecord("comp", "l", "r", "True", True, False, -1, EvidenceCeiling.BoundaryChecked)  # type: ignore

        # Direct construction with bool for delta_E (e.g. False == 0, True == 1) raises ValueError
        with pytest.raises(ValueError, match="must be in"):
            CompositionRecord("comp", "l", "r", True, True, False, False, EvidenceCeiling.BoundaryChecked)  # type: ignore
        with pytest.raises(ValueError, match="must be in"):
            CompositionRecord("comp", "l", "r", True, False, True, True, EvidenceCeiling.BoundaryChecked)  # type: ignore

        # Direct construction with elevated ceiling raises PermissionError
        with pytest.raises(PermissionError, match="restricted to BoundaryChecked"):
            CompositionRecord("comp", "l", "r", True, True, False, -1, EvidenceCeiling.CertifiedTerminal)

        # Elevation via dataclasses.replace raises PermissionError
        with pytest.raises(PermissionError, match="restricted to BoundaryChecked"):
            replace(r, evidence_ceiling=EvidenceCeiling.CertifiedTerminal)


class TestFiniteRegressionCases:
    """Verify the finite guards retained from earlier regression reports."""

    def test_regression_cases(self):
        # 1. The weak-sufficiency witness refutes factorization without false eligibility.
        d = EvaluatorGluingDefect(-1, 0, (1, 1), 1)
        c = OrganizationalClosureConditions(True, True, True)
        assert WeakSufficiencyAuditor.evaluate_counterexample()["refutes_factorization_implication"]
        audit = c.audit_boundary_governance(d)
        assert audit["governance_prerequisites_satisfied"] is True
        assert audit["evaluator_agrees"] is False
        assert audit["closure_eligible"] is False

        # 2. Bare boolean adequacy cert cannot produce certified closure
        green = EvaluatorGluingDefect(0, 1, (1, 1), 1)
        res_green = DetectorAdequacyGuard.audit_verdict(green, has_detector_adequacy_cert=True)
        assert res_green["certified"] is False
        assert res_green["soundness"] == "OBSERVED_AGREEMENT_ADEQUACY_DECLARED"

        # 3. Impossible record delta_E is rejected
        with pytest.raises(ValueError):
            CompositionRecord("comp", "left", "right", True, True, False, 999, EvidenceCeiling.BoundaryChecked)

        # 4. Textual boolean in trace is rejected with TypeError
        with pytest.raises(TypeError):
            ObservedPerformanceTrace("c", "comp", "left", "right", True, True, "False")  # type: ignore

        # 5. Elevated ceiling via replace is rejected
        r = CompositionRecord("comp", "left", "right", True, True, False, -1, EvidenceCeiling.BoundaryChecked)
        with pytest.raises(PermissionError):
            replace(r, evidence_ceiling=EvidenceCeiling.CertifiedTerminal)

        # 6. Duplicate player IDs in Shapley value are rejected
        with pytest.raises(ValueError, match="unique identifiers"):
            NonAdditivityAuditor.compute_shapley_attribution(["rep", "rep"], lambda s: float("rep" in s))


class TestFiniteTheoremCensus:
    """Finite checks for M4, M8, and M9. Each assertion calls the shipped census."""

    def test_product_sufficiency_iff_on_boolean_cube(self):
        census = FiniteTheoremCensus.product_sufficiency_iff_factorization_census()
        assert census["recovered"] == 128
        assert census["matched"] == 128
        assert census["unconditional_disagreements"] == 128

        recovered = BooleanBoundary(True, True, False, (True, True, False), True, True)
        assert weak_boundary_sufficiency(recovered) is True
        assert product_sufficiency(recovered) is False
        assert evaluator_factorization(recovered) is False

        dropped = BooleanBoundary(True, True, True, (True, True, False), True, True)
        assert weak_boundary_sufficiency(dropped) is False
        assert product_sufficiency(dropped) is False
        assert evaluator_factorization(dropped) is True

    def test_boolean_boundary_rejects_malformed_records(self):
        with pytest.raises(ValueError, match="3-tuple"):
            BooleanBoundary(True, True, True, [True, True, True], True, True)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="3-tuple"):
            BooleanBoundary(True, True, True, (True, True), True, True)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="e1"):
            BooleanBoundary(1, True, True, (True, True, True), True, True)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="rep\\[2\\]"):
            BooleanBoundary(True, True, True, (True, True, 1), True, True)  # type: ignore[arg-type]

    def test_mixed_carrier_class_has_no_quotient_factor(self):
        first = ComposedTrace(left=("p", "hidden-a"), right="q")
        second = ComposedTrace(left=("p", "hidden-b"), right="q")
        pi1 = lambda left: left[0]
        pi2 = lambda right: right
        assert joint_carrier(pi1, pi2, first) == joint_carrier(pi1, pi2, second)

        mixed = FiniteTheoremCensus.quotient_factor_table(
            [first, second],
            pi1,
            pi2,
            lambda trace: trace.left[1] == "hidden-a",
        )
        assert mixed["factors"] is False
        assert mixed["blocked_classes"] == (("p", "q"),)
        assert mixed["factor"] == {}

        constant = FiniteTheoremCensus.quotient_factor_table(
            [first, second],
            pi1,
            pi2,
            lambda trace: True,
        )
        assert constant["factors"] is True
        assert constant["factor"] == {("p", "q"): True}
        assert constant["blocked_classes"] == ()

    def test_quotient_factor_table_rejects_empty_and_nonbool(self):
        with pytest.raises(ValueError, match="nonempty"):
            FiniteTheoremCensus.quotient_factor_table(
                [],
                lambda left: left,
                lambda right: right,
                lambda trace: True,
            )
        with pytest.raises(TypeError, match="global evaluator"):
            FiniteTheoremCensus.quotient_factor_table(
                [ComposedTrace(left=0, right=0)],
                lambda left: left,
                lambda right: right,
                lambda trace: 1,  # type: ignore[return-value]
            )

    def test_local_green_mixing_selects_negative_defect(self):
        first = ComposedTrace(left=(0, 0), right=0)
        second = ComposedTrace(left=(0, 1), right=0)
        pi1 = lambda left: left[0]
        pi2 = lambda right: right
        e1 = lambda carrier: carrier == 0
        e2 = lambda carrier: carrier == 0

        global_false_on_first = FiniteTheoremCensus.negative_defect_witness(
            first,
            second,
            pi1,
            pi2,
            e1,
            e2,
            lambda trace: trace.left[1] == 1,
        )
        assert global_false_on_first["local_transported"] is True
        assert global_false_on_first["witness_is_first"] is True
        assert global_false_on_first["witness_delta"] == -1
        assert global_false_on_first["delta_trace"] == -1
        assert global_false_on_first["delta_other"] == 0

        global_false_on_second = FiniteTheoremCensus.negative_defect_witness(
            first,
            second,
            pi1,
            pi2,
            e1,
            e2,
            lambda trace: trace.left[1] == 0,
        )
        assert global_false_on_second["witness_is_first"] is False
        assert global_false_on_second["witness_delta"] == -1
        assert global_false_on_second["delta_trace"] == 0
        assert global_false_on_second["delta_other"] == -1

    def test_negative_defect_requires_carrier_local_green_mixing(self):
        first = ComposedTrace(left=(0, 0), right=0)
        second = ComposedTrace(left=(0, 1), right=0)
        other_carrier = ComposedTrace(left=(1, 0), right=0)
        pi1 = lambda left: left[0]
        pi2 = lambda right: right
        e1 = lambda carrier: carrier == 0
        e2 = lambda carrier: carrier == 0

        with pytest.raises(ValueError, match="joint-carrier"):
            FiniteTheoremCensus.negative_defect_witness(
                first, other_carrier, pi1, pi2, e1, e2, lambda trace: True,
            )
        with pytest.raises(ValueError, match="locally green"):
            FiniteTheoremCensus.negative_defect_witness(
                first,
                second,
                pi1,
                pi2,
                lambda carrier: False,
                e2,
                lambda trace: trace.left[1] == 0,
            )
        with pytest.raises(ValueError, match="locally green"):
            FiniteTheoremCensus.negative_defect_witness(
                first,
                second,
                pi1,
                pi2,
                e1,
                lambda carrier: False,
                lambda trace: trace.left[1] == 0,
            )
        with pytest.raises(ValueError, match="do not differ"):
            FiniteTheoremCensus.negative_defect_witness(
                first, second, pi1, pi2, e1, e2, lambda trace: True,
            )
        with pytest.raises(TypeError, match="global evaluator"):
            FiniteTheoremCensus.negative_defect_witness(
                first, second, pi1, pi2, e1, e2, lambda trace: 0,  # type: ignore[return-value]
            )
        with pytest.raises(TypeError, match="e1"):
            FiniteTheoremCensus.negative_defect_witness(
                first, second, pi1, pi2, lambda carrier: 1, e2, lambda trace: False,  # type: ignore[return-value]
            )

        assert org_delta(True, False) == 1
        assert org_delta(False, False) == 0
        assert carrier_local_product(
            lambda carrier: True,
            lambda carrier: False,
            pi1,
            pi2,
            first,
        ) is False

    def test_negative_defect_rejects_failed_transport(self):
        first = ComposedTrace(left=(0, 0), right=0)
        second = ComposedTrace(left=(0, 1), right=0)
        pi1 = lambda left: left[0]
        pi2 = lambda right: right
        call_count = [0]

        def stateful_e1(carrier):
            call_count[0] += 1
            return call_count[0] == 1  # True on first call, False on second call

        e2 = lambda carrier: True
        with pytest.raises(ValueError, match="failed to transport"):
            FiniteTheoremCensus.negative_defect_witness(
                first, second, pi1, pi2, stateful_e1, e2, lambda trace: trace.left[1] == 0
            )


def test_generate_figures(monkeypatch, tmp_path):
    import os
    import tempfile
    import generate_figures

    fake_module = tmp_path / "code" / "generate_figures.py"
    monkeypatch.setattr(generate_figures, "__file__", str(fake_module))
    default_dir = generate_figures.ensure_export_dir()
    assert default_dir == str(tmp_path / "code" / ".." / "public_export")
    assert os.path.isdir(default_dir)

    with tempfile.TemporaryDirectory() as tmp_dir:
        import matplotlib.pyplot as plt
        try:
            generate_figures.generate_figure_1(tmp_dir)
            generate_figures.generate_figure_2(tmp_dir)
        finally:
            plt.close("all")
        assert os.path.exists(os.path.join(tmp_dir, "figure_1_organizational_cut_architecture.png"))
        assert os.path.exists(os.path.join(tmp_dir, "figure_1_organizational_cut_architecture.pdf"))
        assert os.path.exists(os.path.join(tmp_dir, "figure_2_case_studies_defect_matrix.png"))
        assert os.path.exists(os.path.join(tmp_dir, "figure_2_case_studies_defect_matrix.pdf"))
        for pdf_name in (
            "figure_1_organizational_cut_architecture.pdf",
            "figure_2_case_studies_defect_matrix.pdf",
        ):
            with open(os.path.join(tmp_dir, pdf_name), "rb") as stream:
                pdf_bytes = stream.read()
            assert b"/CreationDate (D:20260915120000Z)" in pdf_bytes
            assert b"/ModDate (D:20260915120000Z)" in pdf_bytes
