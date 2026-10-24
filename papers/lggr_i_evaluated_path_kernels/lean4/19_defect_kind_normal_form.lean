/-
Paper 020, Tier 19: defect-kind normal form.

The full defect packet has exactly the same discriminating power as a
three-valued defect kind: NGD, PGD, or ZDR. Pairing that canonical defect kind
with either absolute verdict bit is complete for the diagnostic quotient.
-/

import «18_defect_packet_one_bit_reconstruction»

namespace PaperAE004

inductive DefectKind where
  | ngd
  | pgd
  | zdr
deriving DecidableEq, Repr

def defectKind (t : EvalTriple) : DefectKind :=
  if isNGDTriple t then
    DefectKind.ngd
  else if isPGDTriple t then
    DefectKind.pgd
  else
    DefectKind.zdr

def defectKindWithLocal (t : EvalTriple) : DefectKind × Bool :=
  (defectKind t, isLocalGreenTriple t)

def defectKindWithGlobal (t : EvalTriple) : DefectKind × Bool :=
  (defectKind t, isGlobalGreenTriple t)

theorem defect_packet_eq_iff_defect_kind_eq
    (x y : EvalTriple) :
    defectPacket x = defectPacket y ↔ defectKind x = defectKind y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      defectPacket,
      defectKind,
      tripleEvaluatorDefect,
      isEGDTriple,
      isNGDTriple,
      isPGDTriple,
      isZDRTriple,
      isNGD,
      isPGD,
      isZDR,
      deltaEval,
      localProduct,
      b2i
    ]

theorem defect_kind_with_local_eq_iff_diagnostic_dashboard_zero
    (x y : EvalTriple) :
    defectKindWithLocal x = defectKindWithLocal y ↔
      diagnosticDashboardPrimitiveDifference.ZeroRel x y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      defectKindWithLocal,
      defectKind,
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      isNGDTriple,
      isPGDTriple,
      isNGD,
      isPGD,
      deltaEval,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ]

theorem defect_kind_with_global_eq_iff_diagnostic_dashboard_zero
    (x y : EvalTriple) :
    defectKindWithGlobal x = defectKindWithGlobal y ↔
      diagnosticDashboardPrimitiveDifference.ZeroRel x y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      defectKindWithGlobal,
      defectKind,
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      isNGDTriple,
      isPGDTriple,
      isNGD,
      isPGD,
      deltaEval,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ]

theorem defect_kind_plus_local_determines_global
    {x y : EvalTriple}
    (hkind : defectKind x = defectKind y)
    (hlocal : isLocalGreenTriple x = isLocalGreenTriple y) :
    isGlobalGreenTriple x = isGlobalGreenTriple y := by
  have hpair : defectKindWithLocal x = defectKindWithLocal y := by
    simp [defectKindWithLocal, hkind, hlocal]
  have hdiag :=
    (defect_kind_with_local_eq_iff_diagnostic_dashboard_zero x y).1 hpair
  exact (diagnostic_dashboard_zero_iff_same_local_and_global x y).1 hdiag |>.2

theorem defect_kind_plus_global_determines_local
    {x y : EvalTriple}
    (hkind : defectKind x = defectKind y)
    (hglobal : isGlobalGreenTriple x = isGlobalGreenTriple y) :
    isLocalGreenTriple x = isLocalGreenTriple y := by
  have hpair : defectKindWithGlobal x = defectKindWithGlobal y := by
    simp [defectKindWithGlobal, hkind, hglobal]
  have hdiag :=
    (defect_kind_with_global_eq_iff_diagnostic_dashboard_zero x y).1 hpair
  exact (diagnostic_dashboard_zero_iff_same_local_and_global x y).1 hdiag |>.1

theorem defect_kind_with_local_factors_through_diagnostic_dashboard :
    ∃ F :
        OmegaCore.PrimitiveDifference.ResidualQuotient
            diagnosticDashboardPrimitiveDifference → DefectKind × Bool,
      ∀ x : EvalTriple,
        F (OmegaCore.PrimitiveDifference.classOf
              diagnosticDashboardPrimitiveDifference x) =
          defectKindWithLocal x := by
  refine
    (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
      diagnosticDashboardPrimitiveDifference defectKindWithLocal).2 ?_
  intro x y hxy
  exact
    (defect_kind_with_local_eq_iff_diagnostic_dashboard_zero x y).2 hxy

theorem defect_kind_with_global_factors_through_diagnostic_dashboard :
    ∃ F :
        OmegaCore.PrimitiveDifference.ResidualQuotient
            diagnosticDashboardPrimitiveDifference → DefectKind × Bool,
      ∀ x : EvalTriple,
        F (OmegaCore.PrimitiveDifference.classOf
              diagnosticDashboardPrimitiveDifference x) =
          defectKindWithGlobal x := by
  refine
    (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
      diagnosticDashboardPrimitiveDifference defectKindWithGlobal).2 ?_
  intro x y hxy
  exact
    (defect_kind_with_global_eq_iff_diagnostic_dashboard_zero x y).2 hxy

#print axioms PaperAE004.defect_packet_eq_iff_defect_kind_eq
#print axioms PaperAE004.defect_kind_with_local_eq_iff_diagnostic_dashboard_zero
#print axioms PaperAE004.defect_kind_with_global_eq_iff_diagnostic_dashboard_zero
#print axioms PaperAE004.defect_kind_plus_local_determines_global
#print axioms PaperAE004.defect_kind_plus_global_determines_local
#print axioms PaperAE004.defect_kind_with_local_factors_through_diagnostic_dashboard
#print axioms PaperAE004.defect_kind_with_global_factors_through_diagnostic_dashboard

end PaperAE004
