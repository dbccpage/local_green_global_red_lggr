/-
Paper 020, Tier 8: semantic normal forms for defect classes.

The signed evaluator-defect classes are not just names for arithmetic cases.
For binary local and global evaluators, NGD is exactly local-green/global-red,
PGD is exactly local-red/global-green, and ZDR is exactly agreement between the
global evaluator and the local product.
-/

import «02_delta_partition»

namespace PaperAE004

theorem ngd_iff_local_green_global_red (e1 e2 eg : Bool) :
    isNGD e1 e2 eg = true ↔ localProduct e1 e2 = 1 ∧ b2i eg = 0 := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem pgd_iff_local_red_global_green (e1 e2 eg : Bool) :
    isPGD e1 e2 eg = true ↔ localProduct e1 e2 = 0 ∧ b2i eg = 1 := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem zdr_iff_global_equals_local_product (e1 e2 eg : Bool) :
    isZDR e1 e2 eg = true ↔ b2i eg = localProduct e1 e2 := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem local_green_global_red_iff_ngd (e1 e2 eg : Bool) :
    localProduct e1 e2 = 1 ∧ b2i eg = 0 ↔ isNGD e1 e2 eg = true := by
  exact (ngd_iff_local_green_global_red e1 e2 eg).symm

theorem defect_class_semantic_normal_forms (e1 e2 eg : Bool) :
    (isNGD e1 e2 eg = true ↔ localProduct e1 e2 = 1 ∧ b2i eg = 0) ∧
      (isPGD e1 e2 eg = true ↔ localProduct e1 e2 = 0 ∧ b2i eg = 1) ∧
      (isZDR e1 e2 eg = true ↔ b2i eg = localProduct e1 e2) := by
  exact
    ⟨ngd_iff_local_green_global_red e1 e2 eg,
      pgd_iff_local_red_global_green e1 e2 eg,
      zdr_iff_global_equals_local_product e1 e2 eg⟩

#print axioms PaperAE004.ngd_iff_local_green_global_red
#print axioms PaperAE004.pgd_iff_local_red_global_green
#print axioms PaperAE004.zdr_iff_global_equals_local_product
#print axioms PaperAE004.local_green_global_red_iff_ngd
#print axioms PaperAE004.defect_class_semantic_normal_forms

end PaperAE004
