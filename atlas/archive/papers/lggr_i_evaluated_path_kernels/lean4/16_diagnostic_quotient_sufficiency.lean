/-
Paper 020, Tier 16: diagnostic quotient sufficiency.

The local-only quotient is too coarse, but the quotient that records both the
local-product verdict and global verdict is sufficient for the defect packet.
Thus the EPK dashboard requires the local/global comparison pair, not hidden
model internals.
-/

import «15_ngd_exposure_decomposition»
import «08_primitive_difference_bridge»

namespace PaperAE004

structure DefectPacket where
  delta : Int
  ngd : Bool
  pgd : Bool
  zdr : Bool
  egd : Bool
deriving DecidableEq

def sameDiagnosticDashboardDiff (x y : EvalTriple) : Bool :=
  (isLocalGreenTriple x == isLocalGreenTriple y) &&
    (isGlobalGreenTriple x == isGlobalGreenTriple y)

def diagnosticDashboardPrimitiveDifference :
    OmegaCore.PrimitiveDifference EvalTriple Bool where
  δ := sameDiagnosticDashboardDiff
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

def defectPacket (t : EvalTriple) : DefectPacket :=
  { delta := tripleEvaluatorDefect t
    ngd := isNGDTriple t
    pgd := isPGDTriple t
    zdr := isZDRTriple t
    egd := isEGDTriple t }

theorem diagnostic_dashboard_zero_iff_same_local_and_global
    (x y : EvalTriple) :
    diagnosticDashboardPrimitiveDifference.ZeroRel x y ↔
      isLocalGreenTriple x = isLocalGreenTriple y ∧
        isGlobalGreenTriple x = isGlobalGreenTriple y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ]

theorem diagnostic_dashboard_refines_local_dashboard
    {x y : EvalTriple}
    (hxy : diagnosticDashboardPrimitiveDifference.ZeroRel x y) :
    localDashboardPrimitiveDifference.ZeroRel x y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      localDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      sameLocalGreenDiff,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ] at hxy ⊢

theorem diagnostic_dashboard_separates_all_green_and_lggr :
    ¬ diagnosticDashboardPrimitiveDifference.ZeroRel allGreenTriple lggrTriple := by
  intro h
  simp [
    OmegaCore.PrimitiveDifference.ZeroRel,
    diagnosticDashboardPrimitiveDifference,
    sameDiagnosticDashboardDiff,
    allGreenTriple,
    lggrTriple,
    isLocalGreenTriple,
    isGlobalGreenTriple,
    localProduct,
    b2i
  ] at h

theorem defect_packet_invariant_on_diagnostic_dashboard :
    OmegaCore.PrimitiveDifference.InvariantCongruent
      diagnosticDashboardPrimitiveDifference defectPacket := by
  intro x y hxy
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      defectPacket,
      tripleEvaluatorDefect,
      isEGDTriple,
      isNGDTriple,
      isPGDTriple,
      isZDRTriple,
      isNGD,
      isPGD,
      isZDR,
      deltaEval,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ] at hxy ⊢

theorem defect_packet_factors_through_diagnostic_dashboard_quotient :
    ∃ F :
        OmegaCore.PrimitiveDifference.ResidualQuotient
            diagnosticDashboardPrimitiveDifference → DefectPacket,
      ∀ x : EvalTriple,
        F (OmegaCore.PrimitiveDifference.classOf
              diagnosticDashboardPrimitiveDifference x) =
          defectPacket x := by
  exact
    (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
      diagnosticDashboardPrimitiveDifference defectPacket).2
      defect_packet_invariant_on_diagnostic_dashboard

#print axioms PaperAE004.diagnostic_dashboard_zero_iff_same_local_and_global
#print axioms PaperAE004.diagnostic_dashboard_refines_local_dashboard
#print axioms PaperAE004.diagnostic_dashboard_separates_all_green_and_lggr
#print axioms PaperAE004.defect_packet_invariant_on_diagnostic_dashboard
#print axioms PaperAE004.defect_packet_factors_through_diagnostic_dashboard_quotient

end PaperAE004
