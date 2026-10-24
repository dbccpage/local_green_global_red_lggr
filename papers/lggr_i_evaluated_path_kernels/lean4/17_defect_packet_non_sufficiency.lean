/-
Paper 020, Tier 17: defect-packet non-sufficiency.

The diagnostic quotient carries the defect packet, but the converse is false.
The defect packet deliberately records non-compositionality; it does not replace
the local/global verdict pair needed for LPR and GPR.
-/

import «16_diagnostic_quotient_sufficiency»

namespace PaperAE004

def localRedGlobalRedTriple : EvalTriple :=
  { e1 := false, e2 := false, eg := false }

theorem diagnostic_dashboard_zero_implies_defect_packet_eq
    {x y : EvalTriple}
    (hxy : diagnosticDashboardPrimitiveDifference.ZeroRel x y) :
    defectPacket x = defectPacket y :=
  defect_packet_invariant_on_diagnostic_dashboard x y hxy

theorem defect_packet_eq_does_not_imply_diagnostic_dashboard_zero :
    ∃ x y : EvalTriple,
      defectPacket x = defectPacket y ∧
        ¬ diagnosticDashboardPrimitiveDifference.ZeroRel x y := by
  refine ⟨allGreenTriple, localRedGlobalRedTriple, ?_, ?_⟩
  · rfl
  · intro h
    simp [
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
      allGreenTriple,
      localRedGlobalRedTriple,
      isLocalGreenTriple,
      isGlobalGreenTriple,
      localProduct,
      b2i
    ] at h

theorem same_defect_packet_can_have_different_local_and_global_verdicts :
    defectPacket allGreenTriple = defectPacket localRedGlobalRedTriple ∧
      isLocalGreenTriple allGreenTriple ≠
        isLocalGreenTriple localRedGlobalRedTriple ∧
      isGlobalGreenTriple allGreenTriple ≠
        isGlobalGreenTriple localRedGlobalRedTriple := by
  decide

theorem defect_packet_does_not_determine_local_pass_count :
    ∃ x y : EvalTriple,
      defectPacket x = defectPacket y ∧
        isLocalGreenTriple x ≠ isLocalGreenTriple y := by
  exact
    ⟨allGreenTriple,
      localRedGlobalRedTriple,
      by decide,
      by decide⟩

theorem defect_packet_does_not_determine_global_verdict :
    ∃ x y : EvalTriple,
      defectPacket x = defectPacket y ∧
        isGlobalGreenTriple x ≠ isGlobalGreenTriple y := by
  exact
    ⟨allGreenTriple,
      localRedGlobalRedTriple,
      by decide,
      by decide⟩

#print axioms PaperAE004.diagnostic_dashboard_zero_implies_defect_packet_eq
#print axioms PaperAE004.defect_packet_eq_does_not_imply_diagnostic_dashboard_zero
#print axioms PaperAE004.same_defect_packet_can_have_different_local_and_global_verdicts
#print axioms PaperAE004.defect_packet_does_not_determine_local_pass_count
#print axioms PaperAE004.defect_packet_does_not_determine_global_verdict

end PaperAE004
