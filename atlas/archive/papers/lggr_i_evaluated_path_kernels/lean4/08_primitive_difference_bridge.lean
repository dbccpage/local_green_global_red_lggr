/-
Paper 020, Tier 7: primitive-difference bridge for local dashboards.

The local dashboard quotient identifies traces that have the same local-green
reading. The all-green trace and the local-green/global-red trace are zero-related
for that quotient, but the global evaluator and signed evaluator defect are not
invariant on the zero relation. Therefore they cannot be read as quotient
diagnostics of the local dashboard alone.
-/

import «07_dashboard_insufficiency»
import primitive_difference

namespace PaperAE004

def allGreenTriple : EvalTriple :=
  { e1 := true, e2 := true, eg := true }

def lggrTriple : EvalTriple :=
  { e1 := true, e2 := true, eg := false }

def sameLocalGreenDiff (x y : EvalTriple) : Bool :=
  isLocalGreenTriple x == isLocalGreenTriple y

def localDashboardPrimitiveDifference :
    OmegaCore.PrimitiveDifference EvalTriple Bool where
  δ := sameLocalGreenDiff
  Zero := fun b => b = true
  zero_refl := by
    intro x
    rcases x with ⟨x1, x2, xg⟩
    cases x1 <;> cases x2 <;> cases xg <;> decide
  zero_symm := by
    intro x y hxy
    rcases x with ⟨x1, x2, xg⟩
    rcases y with ⟨y1, y2, yg⟩
    cases x1 <;> cases x2 <;> cases xg <;>
      cases y1 <;> cases y2 <;> cases yg <;>
      cases hxy <;> decide
  zero_trans := by
    intro x y z hxy hyz
    rcases x with ⟨x1, x2, xg⟩
    rcases y with ⟨y1, y2, yg⟩
    rcases z with ⟨z1, z2, zg⟩
    cases x1 <;> cases x2 <;> cases xg <;>
      cases y1 <;> cases y2 <;> cases yg <;>
      cases z1 <;> cases z2 <;> cases zg <;>
      cases hxy <;> cases hyz <;> decide

def tripleEvaluatorDefect (t : EvalTriple) : Int :=
  deltaEval t.e1 t.e2 t.eg

theorem local_dashboard_zero_identifies_all_green_and_lggr :
    localDashboardPrimitiveDifference.ZeroRel allGreenTriple lggrTriple := by
  rfl

theorem global_classifier_not_invariant_on_local_dashboard_zero :
    ¬ OmegaCore.PrimitiveDifference.InvariantCongruent
        localDashboardPrimitiveDifference isGlobalGreenTriple := by
  intro hcongr
  have hbad := hcongr allGreenTriple lggrTriple
    local_dashboard_zero_identifies_all_green_and_lggr
  change true = false at hbad
  cases hbad

theorem evaluator_defect_not_invariant_on_local_dashboard_zero :
    ¬ OmegaCore.PrimitiveDifference.InvariantCongruent
        localDashboardPrimitiveDifference tripleEvaluatorDefect := by
  intro hcongr
  have hbad := hcongr allGreenTriple lggrTriple
    local_dashboard_zero_identifies_all_green_and_lggr
  change (0 : Int) = -1 at hbad
  cases hbad

theorem global_classifier_no_factor_through_local_dashboard_quotient :
    ¬ (∃ F :
          OmegaCore.PrimitiveDifference.ResidualQuotient
              localDashboardPrimitiveDifference → Bool,
        ∀ x : EvalTriple,
          F (OmegaCore.PrimitiveDifference.classOf
                localDashboardPrimitiveDifference x) =
            isGlobalGreenTriple x) := by
  intro h
  rcases h with ⟨F, hF⟩
  exact global_classifier_not_invariant_on_local_dashboard_zero
    (OmegaCore.PrimitiveDifference.invariantFactor_requires_congruence
      localDashboardPrimitiveDifference isGlobalGreenTriple F hF)

theorem evaluator_defect_no_factor_through_local_dashboard_quotient :
    ¬ (∃ F :
          OmegaCore.PrimitiveDifference.ResidualQuotient
              localDashboardPrimitiveDifference → Int,
        ∀ x : EvalTriple,
          F (OmegaCore.PrimitiveDifference.classOf
                localDashboardPrimitiveDifference x) =
            tripleEvaluatorDefect x) := by
  intro h
  rcases h with ⟨F, hF⟩
  exact evaluator_defect_not_invariant_on_local_dashboard_zero
    (OmegaCore.PrimitiveDifference.invariantFactor_requires_congruence
      localDashboardPrimitiveDifference tripleEvaluatorDefect F hF)

#print axioms PaperAE004.local_dashboard_zero_identifies_all_green_and_lggr
#print axioms PaperAE004.global_classifier_not_invariant_on_local_dashboard_zero
#print axioms PaperAE004.evaluator_defect_not_invariant_on_local_dashboard_zero
#print axioms PaperAE004.global_classifier_no_factor_through_local_dashboard_quotient
#print axioms PaperAE004.evaluator_defect_no_factor_through_local_dashboard_quotient

end PaperAE004
