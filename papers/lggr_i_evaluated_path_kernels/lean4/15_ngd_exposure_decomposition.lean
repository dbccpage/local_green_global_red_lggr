/-
Paper 020, Tier 15: NGD exposure decomposition.

Local-green traces split into globally green local passes and negative gluing
defects. This is the finite count invariant behind the conditional NGD rate:
the NGD numerator is always bounded by the local-pass denominator.
-/

import «14_defect_moment_reconstruction»

namespace PaperAE004

def isLocalAndGlobalGreenTriple (t : EvalTriple) : Bool :=
  isLocalGreenTriple t && isGlobalGreenTriple t

def localAndGlobalGreenCount (samples : List EvalTriple) : Nat :=
  classCount isLocalAndGlobalGreenTriple samples

theorem pointwise_local_green_iff_lgg_or_ngd (t : EvalTriple) :
    isLocalGreenTriple t = true ↔
      isLocalAndGlobalGreenTriple t = true ∨ isNGDTriple t = true := by
  rcases t with ⟨e1, e2, eg⟩
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem local_pass_count_eq_lgg_count_plus_ngd_count
    (samples : List EvalTriple) :
    localPassCount samples =
      localAndGlobalGreenCount samples + classCount isNGDTriple samples := by
  induction samples with
  | nil =>
      rfl
  | cons x xs ih =>
      have ih' :
          classCount isLocalGreenTriple xs =
            classCount isLocalAndGlobalGreenTriple xs +
              classCount isNGDTriple xs := by
        simpa [localPassCount, localAndGlobalGreenCount] using ih
      rcases x with ⟨e1, e2, eg⟩
      cases e1 <;> cases e2 <;> cases eg <;>
        simp [
          localPassCount,
          localAndGlobalGreenCount,
          classCount,
          isLocalAndGlobalGreenTriple,
          isLocalGreenTriple,
          isGlobalGreenTriple,
          isNGDTriple,
          isNGD,
          deltaEval,
          localProduct,
          b2i
        ]
      all_goals omega

theorem ngd_count_le_local_pass_count (samples : List EvalTriple) :
    classCount isNGDTriple samples ≤ localPassCount samples := by
  have h := local_pass_count_eq_lgg_count_plus_ngd_count samples
  omega

theorem local_pass_count_zero_implies_ngd_count_zero
    (samples : List EvalTriple) :
    localPassCount samples = 0 → classCount isNGDTriple samples = 0 := by
  intro hzero
  have h := local_pass_count_eq_lgg_count_plus_ngd_count samples
  omega

theorem ngd_count_positive_implies_local_pass_count_positive
    (samples : List EvalTriple) :
    0 < classCount isNGDTriple samples → 0 < localPassCount samples := by
  intro hpos
  have h := ngd_count_le_local_pass_count samples
  omega

#print axioms PaperAE004.pointwise_local_green_iff_lgg_or_ngd
#print axioms PaperAE004.local_pass_count_eq_lgg_count_plus_ngd_count
#print axioms PaperAE004.ngd_count_le_local_pass_count
#print axioms PaperAE004.local_pass_count_zero_implies_ngd_count_zero
#print axioms PaperAE004.ngd_count_positive_implies_local_pass_count_positive

end PaperAE004
