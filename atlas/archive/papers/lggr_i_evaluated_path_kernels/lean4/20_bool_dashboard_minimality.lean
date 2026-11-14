/-
Paper 020, Tier 20: Boolean-dashboard minimality.

The exact diagnostic quotient has more information than one Boolean bit can
carry. Three canonical traces already occupy three pairwise distinct diagnostic
classes, so no Bool-valued dashboard key can have equality exactly coincide
with diagnostic zero-equivalence.
-/

import «19_defect_kind_normal_form»

namespace PaperAE004

theorem three_pairwise_distinct_diagnostic_classes :
    ¬ diagnosticDashboardPrimitiveDifference.ZeroRel allGreenTriple lggrTriple ∧
      ¬ diagnosticDashboardPrimitiveDifference.ZeroRel
          allGreenTriple localRedGlobalRedTriple ∧
      ¬ diagnosticDashboardPrimitiveDifference.ZeroRel
          lggrTriple localRedGlobalRedTriple := by
  simp [
    allGreenTriple,
    lggrTriple,
    localRedGlobalRedTriple,
    OmegaCore.PrimitiveDifference.ZeroRel,
    diagnosticDashboardPrimitiveDifference,
    sameDiagnosticDashboardDiff,
    isLocalGreenTriple,
    isGlobalGreenTriple,
    localProduct,
    b2i
  ]

theorem bool_dashboard_cannot_be_exact_diagnostic_dashboard :
    ¬ (∃ f : EvalTriple → Bool,
        ∀ x y : EvalTriple,
          (f x = f y ↔
            diagnosticDashboardPrimitiveDifference.ZeroRel x y)) := by
  intro h
  rcases h with ⟨f, hf⟩
  let a := allGreenTriple
  let b := lggrTriple
  let c := localRedGlobalRedTriple
  by_cases hab : f a = f b
  · have hzero := (hf a b).1 hab
    simp [
      a,
      b,
      allGreenTriple,
      lggrTriple,
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ] at hzero
  · by_cases hac : f a = f c
    · have hzero := (hf a c).1 hac
      simp [
        a,
        c,
        allGreenTriple,
        localRedGlobalRedTriple,
        OmegaCore.PrimitiveDifference.ZeroRel,
        diagnosticDashboardPrimitiveDifference,
        sameDiagnosticDashboardDiff,
        isLocalGreenTriple,
        isGlobalGreenTriple,
        localProduct,
        b2i
      ] at hzero
    · have hbc : f b = f c := by
        cases ha : f a <;> cases hb : f b <;> cases hc : f c <;>
          simp [ha, hb, hc] at hab hac ⊢
      have hzero := (hf b c).1 hbc
      simp [
        b,
        c,
        lggrTriple,
        localRedGlobalRedTriple,
        OmegaCore.PrimitiveDifference.ZeroRel,
        diagnosticDashboardPrimitiveDifference,
        sameDiagnosticDashboardDiff,
        isLocalGreenTriple,
        isGlobalGreenTriple,
        localProduct,
        b2i
      ] at hzero

theorem exact_diagnostic_dashboard_needs_non_bool_key :
    ∀ f : EvalTriple → Bool,
      ¬ (∀ x y : EvalTriple,
          (f x = f y ↔
            diagnosticDashboardPrimitiveDifference.ZeroRel x y)) := by
  intro f hf
  exact bool_dashboard_cannot_be_exact_diagnostic_dashboard ⟨f, hf⟩

#print axioms PaperAE004.three_pairwise_distinct_diagnostic_classes
#print axioms PaperAE004.bool_dashboard_cannot_be_exact_diagnostic_dashboard
#print axioms PaperAE004.exact_diagnostic_dashboard_needs_non_bool_key

end PaperAE004
