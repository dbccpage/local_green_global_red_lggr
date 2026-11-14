/-
Paper 020, Tier 10: EGD zero gate and cancellation separation.

The absolute evaluator gluing defect count is zero exactly when every sampled
trace is ZDR. A signed mean defect of zero is weaker: NGD and PGD can cancel in
the signed sum while EGD remains positive.
-/

import «07_dashboard_insufficiency»
import «09_defect_class_normal_forms»

namespace PaperAE004

def isEGDTriple (t : EvalTriple) : Bool :=
  isNGDTriple t || isPGDTriple t

def egdCount (samples : List EvalTriple) : Nat :=
  classCount isEGDTriple samples

def allZDR (samples : List EvalTriple) : Prop :=
  ∀ t, t ∈ samples → isZDRTriple t = true

def cancellationSamples : List EvalTriple :=
  [{ e1 := true, e2 := true, eg := false },
    { e1 := false, e2 := false, eg := true }]

theorem egd_false_iff_zdr_true (t : EvalTriple) :
    isEGDTriple t = false ↔ isZDRTriple t = true := by
  rcases t with ⟨e1, e2, eg⟩
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem egd_true_iff_zdr_false (t : EvalTriple) :
    isEGDTriple t = true ↔ isZDRTriple t = false := by
  rcases t with ⟨e1, e2, eg⟩
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem egd_count_zero_iff_all_zdr (samples : List EvalTriple) :
    egdCount samples = 0 ↔ allZDR samples := by
  induction samples with
  | nil =>
      simp [egdCount, classCount, allZDR]
  | cons x xs ih =>
      rcases x with ⟨e1, e2, eg⟩
      cases e1 <;> cases e2 <;> cases eg <;>
        simp [
          egdCount,
          classCount,
          allZDR,
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
      all_goals
        simpa [
          egdCount,
          allZDR,
          isZDRTriple,
          isZDR,
          deltaEval,
          localProduct,
          b2i
        ] using ih

theorem cancellation_sample_zero_delta_but_positive_egd :
    deltaSum cancellationSamples = 0 ∧
      egdCount cancellationSamples = 2 ∧
      classCount isNGDTriple cancellationSamples = 1 ∧
      classCount isPGDTriple cancellationSamples = 1 ∧
      classCount isZDRTriple cancellationSamples = 0 := by
  decide

theorem zero_mean_delta_does_not_force_zero_egd :
    ∃ samples : List EvalTriple,
      deltaSum samples = 0 ∧ egdCount samples ≠ 0 := by
  exact ⟨cancellationSamples, by decide, by decide⟩

#print axioms PaperAE004.egd_false_iff_zdr_true
#print axioms PaperAE004.egd_true_iff_zdr_false
#print axioms PaperAE004.egd_count_zero_iff_all_zdr
#print axioms PaperAE004.cancellation_sample_zero_delta_but_positive_egd
#print axioms PaperAE004.zero_mean_delta_does_not_force_zero_egd

end PaperAE004
