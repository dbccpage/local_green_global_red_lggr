/-
Paper 020, Tier 18: defect-packet one-bit reconstruction.

The defect packet alone is not a verdict dashboard, but the packet plus either
absolute verdict bit is complete for the diagnostic local/global quotient. This
is the sharp positive counterpart to Tier 17's non-sufficiency result.
-/

import «17_defect_packet_non_sufficiency»

namespace PaperAE004

def defectPacketWithLocal (t : EvalTriple) : DefectPacket × Bool :=
  (defectPacket t, isLocalGreenTriple t)

def defectPacketWithGlobal (t : EvalTriple) : DefectPacket × Bool :=
  (defectPacket t, isGlobalGreenTriple t)

theorem defect_packet_with_local_eq_iff_diagnostic_dashboard_zero
    (x y : EvalTriple) :
    defectPacketWithLocal x = defectPacketWithLocal y ↔
      diagnosticDashboardPrimitiveDifference.ZeroRel x y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      defectPacketWithLocal,
      defectPacket,
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
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
    ]

theorem defect_packet_with_global_eq_iff_diagnostic_dashboard_zero
    (x y : EvalTriple) :
    defectPacketWithGlobal x = defectPacketWithGlobal y ↔
      diagnosticDashboardPrimitiveDifference.ZeroRel x y := by
  rcases x with ⟨x1, x2, xg⟩
  rcases y with ⟨y1, y2, yg⟩
  cases x1 <;> cases x2 <;> cases xg <;>
    cases y1 <;> cases y2 <;> cases yg <;>
    simp [
      defectPacketWithGlobal,
      defectPacket,
      OmegaCore.PrimitiveDifference.ZeroRel,
      diagnosticDashboardPrimitiveDifference,
      sameDiagnosticDashboardDiff,
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
    ]

theorem defect_packet_plus_local_determines_global
    {x y : EvalTriple}
    (hpacket : defectPacket x = defectPacket y)
    (hlocal : isLocalGreenTriple x = isLocalGreenTriple y) :
    isGlobalGreenTriple x = isGlobalGreenTriple y := by
  have hpair : defectPacketWithLocal x = defectPacketWithLocal y := by
    simp [defectPacketWithLocal, hpacket, hlocal]
  have hdiag :=
    (defect_packet_with_local_eq_iff_diagnostic_dashboard_zero x y).1 hpair
  exact (diagnostic_dashboard_zero_iff_same_local_and_global x y).1 hdiag |>.2

theorem defect_packet_plus_global_determines_local
    {x y : EvalTriple}
    (hpacket : defectPacket x = defectPacket y)
    (hglobal : isGlobalGreenTriple x = isGlobalGreenTriple y) :
    isLocalGreenTriple x = isLocalGreenTriple y := by
  have hpair : defectPacketWithGlobal x = defectPacketWithGlobal y := by
    simp [defectPacketWithGlobal, hpacket, hglobal]
  have hdiag :=
    (defect_packet_with_global_eq_iff_diagnostic_dashboard_zero x y).1 hpair
  exact (diagnostic_dashboard_zero_iff_same_local_and_global x y).1 hdiag |>.1

theorem defect_packet_with_local_factors_through_diagnostic_dashboard :
    ∃ F :
        OmegaCore.PrimitiveDifference.ResidualQuotient
            diagnosticDashboardPrimitiveDifference → DefectPacket × Bool,
      ∀ x : EvalTriple,
        F (OmegaCore.PrimitiveDifference.classOf
              diagnosticDashboardPrimitiveDifference x) =
          defectPacketWithLocal x := by
  refine
    (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
      diagnosticDashboardPrimitiveDifference defectPacketWithLocal).2 ?_
  intro x y hxy
  exact
    (defect_packet_with_local_eq_iff_diagnostic_dashboard_zero x y).2 hxy

theorem defect_packet_with_global_factors_through_diagnostic_dashboard :
    ∃ F :
        OmegaCore.PrimitiveDifference.ResidualQuotient
            diagnosticDashboardPrimitiveDifference → DefectPacket × Bool,
      ∀ x : EvalTriple,
        F (OmegaCore.PrimitiveDifference.classOf
              diagnosticDashboardPrimitiveDifference x) =
          defectPacketWithGlobal x := by
  refine
    (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
      diagnosticDashboardPrimitiveDifference defectPacketWithGlobal).2 ?_
  intro x y hxy
  exact
    (defect_packet_with_global_eq_iff_diagnostic_dashboard_zero x y).2 hxy

#print axioms PaperAE004.defect_packet_with_local_eq_iff_diagnostic_dashboard_zero
#print axioms PaperAE004.defect_packet_with_global_eq_iff_diagnostic_dashboard_zero
#print axioms PaperAE004.defect_packet_plus_local_determines_global
#print axioms PaperAE004.defect_packet_plus_global_determines_local
#print axioms PaperAE004.defect_packet_with_local_factors_through_diagnostic_dashboard
#print axioms PaperAE004.defect_packet_with_global_factors_through_diagnostic_dashboard

end PaperAE004
