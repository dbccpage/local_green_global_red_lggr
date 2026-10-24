/-
Paper 020, Tier 11: EGD decomposition.

EGD is the absolute gluing-defect count. Pointwise, it is exactly the
NGD-or-PGD predicate. On finite samples, its count is the sum of NGD and PGD
counts, and EGD together with ZDR partitions the sample.
-/

import «10_egd_zero_gate»

namespace PaperAE004

theorem pointwise_egd_iff_ngd_or_pgd (t : EvalTriple) :
    isEGDTriple t = true ↔ isNGDTriple t = true ∨ isPGDTriple t = true := by
  rcases t with ⟨e1, e2, eg⟩
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem egd_count_eq_ngd_plus_pgd (samples : List EvalTriple) :
    egdCount samples =
      classCount isNGDTriple samples + classCount isPGDTriple samples := by
  induction samples with
  | nil =>
      rfl
  | cons x xs ih =>
      have ih' : classCount isEGDTriple xs =
          classCount isNGDTriple xs + classCount isPGDTriple xs := by
        simpa [egdCount] using ih
      rcases x with ⟨e1, e2, eg⟩
      cases e1 <;> cases e2 <;> cases eg <;>
        simp [
          egdCount,
          classCount,
          isEGDTriple,
          isNGDTriple,
          isPGDTriple,
          isNGD,
          isPGD,
          deltaEval,
          localProduct,
          b2i,
          Nat.add_assoc,
          Nat.add_left_comm
        ]
      all_goals omega

theorem egd_zdr_count_partition (samples : List EvalTriple) :
    egdCount samples + classCount isZDRTriple samples = samples.length := by
  induction samples with
  | nil =>
      rfl
  | cons x xs ih =>
      have ih' :
          classCount isEGDTriple xs + classCount isZDRTriple xs = xs.length := by
        simpa [egdCount] using ih
      rcases x with ⟨e1, e2, eg⟩
      cases e1 <;> cases e2 <;> cases eg <;>
        simp [
          egdCount,
          classCount,
          isEGDTriple,
          isNGDTriple,
          isPGDTriple,
          isZDRTriple,
          isNGD,
          isPGD,
          isZDR,
          deltaEval,
          localProduct,
          b2i,
          Nat.add_assoc,
          Nat.add_left_comm
        ]
      all_goals omega

theorem egd_count_eq_length_minus_zdr_count (samples : List EvalTriple) :
    egdCount samples = samples.length - classCount isZDRTriple samples := by
  have h := egd_zdr_count_partition samples
  omega

#print axioms PaperAE004.pointwise_egd_iff_ngd_or_pgd
#print axioms PaperAE004.egd_count_eq_ngd_plus_pgd
#print axioms PaperAE004.egd_zdr_count_partition
#print axioms PaperAE004.egd_count_eq_length_minus_zdr_count

end PaperAE004
