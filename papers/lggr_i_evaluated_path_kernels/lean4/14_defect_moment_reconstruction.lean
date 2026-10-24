/-
Paper 020, Tier 14: defect moment reconstruction.

The absolute defect count and signed defect sum are the two moments that
reconstruct the NGD and PGD counts. With sample size, they also reconstruct ZDR.
-/

import «13_two_rate_dashboard_insufficiency»

namespace PaperAE004

theorem egd_plus_delta_eq_twice_pgd_count (samples : List EvalTriple) :
    (egdCount samples : Int) + deltaSum samples =
      2 * (classCount isPGDTriple samples : Int) := by
  have hE := egd_count_eq_ngd_plus_pgd samples
  have hD := delta_sum_eq_pgd_count_minus_ngd_count samples
  omega

theorem egd_minus_delta_eq_twice_ngd_count (samples : List EvalTriple) :
    (egdCount samples : Int) - deltaSum samples =
      2 * (classCount isNGDTriple samples : Int) := by
  have hE := egd_count_eq_ngd_plus_pgd samples
  have hD := delta_sum_eq_pgd_count_minus_ngd_count samples
  omega

theorem same_egd_and_delta_sum_imply_same_ngd_pgd_counts
    (xs ys : List EvalTriple)
    (hE : egdCount xs = egdCount ys)
    (hD : deltaSum xs = deltaSum ys) :
    classCount isNGDTriple xs = classCount isNGDTriple ys ∧
      classCount isPGDTriple xs = classCount isPGDTriple ys := by
  have hPxs := egd_plus_delta_eq_twice_pgd_count xs
  have hPys := egd_plus_delta_eq_twice_pgd_count ys
  have hNxs := egd_minus_delta_eq_twice_ngd_count xs
  have hNys := egd_minus_delta_eq_twice_ngd_count ys
  constructor <;> omega

theorem same_length_egd_and_delta_sum_imply_same_defect_partition
    (xs ys : List EvalTriple)
    (hLen : xs.length = ys.length)
    (hE : egdCount xs = egdCount ys)
    (hD : deltaSum xs = deltaSum ys) :
    classCount isNGDTriple xs = classCount isNGDTriple ys ∧
      classCount isPGDTriple xs = classCount isPGDTriple ys ∧
      classCount isZDRTriple xs = classCount isZDRTriple ys := by
  have hNP := same_egd_and_delta_sum_imply_same_ngd_pgd_counts xs ys hE hD
  have hZxs := egd_zdr_count_partition xs
  have hZys := egd_zdr_count_partition ys
  constructor
  · exact hNP.left
  · constructor
    · exact hNP.right
    · omega

#print axioms PaperAE004.egd_plus_delta_eq_twice_pgd_count
#print axioms PaperAE004.egd_minus_delta_eq_twice_ngd_count
#print axioms PaperAE004.same_egd_and_delta_sum_imply_same_ngd_pgd_counts
#print axioms PaperAE004.same_length_egd_and_delta_sum_imply_same_defect_partition

end PaperAE004
