import Bell.ContextualFraction

/-! Sparse certificates live on the complete assignment space by pushforward. -/
noncomputable section
open scoped BigOperators
namespace Bell.SparseCertificates
open Bell.LinearProgramming Bell.SignedDuality
variable {G J I : Type} [Fintype G] [Fintype J] [Fintype I] [DecidableEq G]

def push (f : J → G) (q : J → ℝ) (g : G) : ℝ := ∑ j, if f j = g then q j else 0

theorem push_total (f : J → G) (q : J → ℝ) : ∑ g, push f q g = ∑ j, q j := by
  simp only [push]
  rw [Finset.sum_comm]
  simp

omit [Fintype I] in
theorem push_mix (A : G → I → ℝ) (f : J → G) (q : J → ℝ) (i : I) :
    mix A (push f q) i = ∑ j, q j * A (f j) i := by
  simp only [mix, push, Finset.sum_mul]
  rw [Finset.sum_comm]
  simp [ite_mul]

omit [Fintype G] in
theorem push_nonnegative (f : J → G) (q : J → ℝ) (hq : ∀ j, 0 ≤ q j) :
    ∀ g, 0 ≤ push f q g := by
  intro g
  exact Finset.sum_nonneg (fun j _ => by split_ifs <;> simp_all)

theorem push_negative_le (f : J → G) (q : J → ℝ) :
    negativeMass (push f q) ≤ ∑ j, max (-q j) 0 := by
  have hg (g : G) : max (-push f q g) 0 ≤
      ∑ j, if f j = g then max (-q j) 0 else 0 := by
    apply max_le
    · rw [push, ← Finset.sum_neg_distrib]
      apply Finset.sum_le_sum
      intro j _
      split_ifs <;> simp
    · exact Finset.sum_nonneg (fun j _ => by split_ifs <;> simp)
  calc
    _ ≤ ∑ g, ∑ j, if f j = g then max (-q j) 0 else 0 := Finset.sum_le_sum (fun g _ => hg g)
    _ = _ := by rw [Finset.sum_comm]; simp

end Bell.SparseCertificates
