import Bell.CHSH
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.Normed.Operator.Basic
import Mathlib.Analysis.Real.Sqrt

/-! Tsirelson's bound from contraction and Hilbert-space geometry. -/
noncomputable section
open scoped BigOperators ComplexConjugate
namespace Bell.Quantum

variable {E : Type} [NormedAddCommGroup E] [InnerProductSpace ℂ E]

/-- Hermiticity is stated through the inner-product identity; dichotomicity is
an involution. These assumptions imply contraction rather than assume it. -/
structure Dichotomic (T : E →L[ℂ] E) : Prop where
  symmetric : ∀ u v, inner ℂ (T u) v = inner ℂ u (T v)
  involution : ∀ v, T (T v) = v

theorem dichotomic_preserves_norm (T : E →L[ℂ] E) (h : Dichotomic T) (v : E) :
    ‖T v‖ = ‖v‖ := by
  have hi := h.symmetric v (T v)
  rw [h.involution] at hi
  have hs := congrArg Complex.re hi
  change RCLike.re (inner ℂ (T v) (T v)) = RCLike.re (inner ℂ v v) at hs
  rw [inner_self_eq_norm_sq, inner_self_eq_norm_sq] at hs
  exact (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).1 hs

theorem dichotomic_contraction (T : E →L[ℂ] E) (h : Dichotomic T) : ‖T‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro v
  rw [dichotomic_preserves_norm T h v, one_mul]

/-- CHSH operator with Alice on the left of Bob. -/
def chsh (A₀ A₁ B₀ B₁ : E →L[ℂ] E) : E →L[ℂ] E :=
  A₀.comp (B₀ + B₁) + A₁.comp (B₀ - B₁)

theorem sum_difference_bound (u v : E) (r : ℝ) (hr : 0 ≤ r)
    (hu : ‖u‖ ≤ r) (hv : ‖v‖ ≤ r) :
    ‖u + v‖ + ‖u - v‖ ≤ 2 * Real.sqrt 2 * r := by
  have hp := parallelogram_law_with_norm ℂ u v
  have hu2 : ‖u‖ ^ 2 ≤ r ^ 2 := (sq_le_sq₀ (norm_nonneg _) hr).2 hu
  have hv2 : ‖v‖ ^ 2 ≤ r ^ 2 := (sq_le_sq₀ (norm_nonneg _) hr).2 hv
  have hs : (Real.sqrt 2) ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hb : (‖u + v‖ + ‖u - v‖) ^ 2 ≤ (2 * Real.sqrt 2 * r) ^ 2 := by
    nlinarith [sq_nonneg (‖u + v‖ - ‖u - v‖)]
  exact (sq_le_sq₀ (add_nonneg (norm_nonneg _) (norm_nonneg _))
    (mul_nonneg (mul_nonneg (by norm_num) (Real.sqrt_nonneg _)) hr)).1 hb

theorem contraction_apply (T : E →L[ℂ] E) (hT : ‖T‖ ≤ 1) (v : E) : ‖T v‖ ≤ ‖v‖ := by
  calc
    ‖T v‖ ≤ ‖T‖ * ‖v‖ := T.le_opNorm v
    _ ≤ 1 * ‖v‖ := mul_le_mul_of_nonneg_right hT (norm_nonneg _)
    _ = ‖v‖ := one_mul _

theorem chsh_apply_bound (A₀ A₁ B₀ B₁ : E →L[ℂ] E)
    (hA₀ : ‖A₀‖ ≤ 1) (hA₁ : ‖A₁‖ ≤ 1) (hB₀ : ‖B₀‖ ≤ 1) (hB₁ : ‖B₁‖ ≤ 1) (ψ : E) :
    ‖chsh A₀ A₁ B₀ B₁ ψ‖ ≤ 2 * Real.sqrt 2 * ‖ψ‖ := by
  calc
    _ ≤ ‖A₀ (B₀ ψ + B₁ ψ)‖ + ‖A₁ (B₀ ψ - B₁ ψ)‖ := norm_add_le _ _
    _ ≤ ‖B₀ ψ + B₁ ψ‖ + ‖B₀ ψ - B₁ ψ‖ :=
      add_le_add (contraction_apply A₀ hA₀ _) (contraction_apply A₁ hA₁ _)
    _ ≤ _ := sum_difference_bound _ _ _ (norm_nonneg _) (contraction_apply B₀ hB₀ ψ)
      (contraction_apply B₁ hB₁ ψ)

theorem tsirelson_operator_bound (A₀ A₁ B₀ B₁ : E →L[ℂ] E)
    (hA₀ : ‖A₀‖ ≤ 1) (hA₁ : ‖A₁‖ ≤ 1) (hB₀ : ‖B₀‖ ≤ 1) (hB₁ : ‖B₁‖ ≤ 1) :
    ‖chsh A₀ A₁ B₀ B₁‖ ≤ 2 * Real.sqrt 2 := by
  exact ContinuousLinearMap.opNorm_le_bound _ (by positivity)
    (chsh_apply_bound A₀ A₁ B₀ B₁ hA₀ hA₁ hB₀ hB₁)

def expectation (ψ : E) (T : E →L[ℂ] E) : ℝ := (inner ℂ ψ (T ψ)).re

theorem tsirelson_pure_state_bound (A₀ A₁ B₀ B₁ : E →L[ℂ] E)
    (hA₀ : ‖A₀‖ ≤ 1) (hA₁ : ‖A₁‖ ≤ 1) (hB₀ : ‖B₀‖ ≤ 1) (hB₁ : ‖B₁‖ ≤ 1)
    (ψ : E) (hψ : ‖ψ‖ = 1) : |expectation ψ (chsh A₀ A₁ B₀ B₁)| ≤ 2 * Real.sqrt 2 := by
  calc
    _ ≤ ‖inner ℂ ψ (chsh A₀ A₁ B₀ B₁ ψ)‖ := Complex.abs_re_le_norm _
    _ ≤ ‖ψ‖ * ‖chsh A₀ A₁ B₀ B₁ ψ‖ := norm_inner_le_norm _ _
    _ ≤ ‖ψ‖ * (2 * Real.sqrt 2 * ‖ψ‖) :=
      mul_le_mul_of_nonneg_left (chsh_apply_bound _ _ _ _ hA₀ hA₁ hB₀ hB₁ ψ) (norm_nonneg _)
    _ = _ := by rw [hψ]; ring

theorem tsirelson_mixed_state_bound {I : Type} [Fintype I] (w : I → ℝ) (hw : Probability w)
    (A₀ A₁ B₀ B₁ : E →L[ℂ] E)
    (hA₀ : ‖A₀‖ ≤ 1) (hA₁ : ‖A₁‖ ≤ 1) (hB₀ : ‖B₀‖ ≤ 1) (hB₁ : ‖B₁‖ ≤ 1)
    (ψ : I → E) (hψ : ∀ i, ‖ψ i‖ = 1) :
    |∑ i, w i * expectation (ψ i) (chsh A₀ A₁ B₀ B₁)| ≤ 2 * Real.sqrt 2 := by
  calc
    _ ≤ ∑ i, |w i * expectation (ψ i) (chsh A₀ A₁ B₀ B₁)| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ i, w i * |expectation (ψ i) (chsh A₀ A₁ B₀ B₁)| := by
      simp_rw [abs_mul, abs_of_nonneg (hw.nonneg _)]
    _ ≤ ∑ i, w i * (2 * Real.sqrt 2) := Finset.sum_le_sum fun i _ =>
      mul_le_mul_of_nonneg_left
        (tsirelson_pure_state_bound _ _ _ _ hA₀ hA₁ hB₀ hB₁ (ψ i) (hψ i)) (hw.nonneg i)
    _ = _ := by rw [← Finset.sum_mul, hw.total, one_mul]


theorem tsirelson_dichotomic_bound (A₀ A₁ B₀ B₁ : E →L[ℂ] E)
    (hA₀ : Dichotomic A₀) (hA₁ : Dichotomic A₁)
    (hB₀ : Dichotomic B₀) (hB₁ : Dichotomic B₁)
    (ψ : E) (hψ : ‖ψ‖ = 1) : |expectation ψ (chsh A₀ A₁ B₀ B₁)| ≤ 2 * Real.sqrt 2 :=
  tsirelson_pure_state_bound _ _ _ _ (dichotomic_contraction _ hA₀)
    (dichotomic_contraction _ hA₁) (dichotomic_contraction _ hB₀)
    (dichotomic_contraction _ hB₁) ψ hψ

end Bell.Quantum

