import Bell.SmoothedComparison

/-! Selected Archimedean shadows of the finite certificate sequence.
These are limits in the usual real metric, not an assertion about physical ontology. -/
noncomputable section
namespace Bell.ContinuumShadows
open Bell.SmoothedComparison

def scaleNorm (h : ℝ) : ℝ := 1-h/3+h^3/3

theorem reciprocal_norm (k : ℝ) (hk : k ≠ 0) :
    normSquare k = scaleNorm (1/k) := by
  unfold normSquare scaleNorm
  field_simp
  ring

theorem massCap_bound (k : ℝ) (hk : 2 ≤ k) :
    0 < massCap k ∧ massCap k < 2/(3*k) := by
  have hk0 : 0 < k := by linarith
  have hs := (norm_bounds k hk).1
  have hn : 0 < normSquare k := by linarith
  have hnum : 1-normSquare k < 1/(3*k) := by
    unfold normSquare
    apply (lt_div_iff₀ (by positivity : 0 < 3*k)).2
    field_simp
    nlinarith
  refine ⟨massCap_positive k hk,?_⟩
  unfold massCap
  apply (div_lt_iff₀ hn).2
  have hc : 0 < 1/(3*k) := by positivity
  have he : 2/(3*k) = 2*(1/(3*k)) := by ring
  rw [he]
  nlinarith

theorem fraction_deficit_bound (k : ℝ) (hk : 2 ≤ k) :
    0 < 1-fractionFloor k ∧ 1-fractionFloor k < 2/k := by
  have hk0 : 0 < k := by linarith
  have hs := (norm_bounds k hk).1
  have hn : 0 < normSquare k := by linarith
  have he : 1-fractionFloor k = 1/(k*normSquare k) := by unfold fractionFloor; ring
  rw [he]
  constructor
  · positivity
  · apply (div_lt_iff₀ (mul_pos hk0 hn)).2
    field_simp
    nlinarith

/-- An explicit epsilon cutoff for any actual values inside the proved envelopes. -/
theorem shadow_error_bound (k cf nm ε : ℝ) (hk : 2 ≤ k) (hε : 0 < ε)
    (hcut : 2/ε < k) (hcf : fractionFloor k ≤ cf) (hcf1 : cf ≤ 1)
    (hn0 : 0 ≤ nm) (hn : nm ≤ massCap k) :
    |cf-1| < ε ∧ |nm| < ε := by
  have hk0 : 0 < k := by linarith
  have he : 2/k < ε := by
    apply (div_lt_iff₀ hk0).2
    have := (div_lt_iff₀ hε).1 hcut
    nlinarith
  have hf := (fraction_deficit_bound k hk).2
  have hm := (massCap_bound k hk).2
  have hsmall : 2/(3*k) ≤ 2/k := by
    apply div_le_div_of_nonneg_left (by norm_num) hk0
    linarith
  rw [abs_of_nonpos (by linarith : cf-1 ≤ 0),abs_of_nonneg hn0]
  constructor <;> linarith

/-- No real-valued endpoint can continuously extend the diverging ratio envelope. -/
theorem no_finite_ratio_endpoint :
    ¬ ∃ L : ℝ, ∀ ε : ℝ, 0 < ε → ∃ K : ℕ, ∀ k : ℕ,
      K ≤ k → 2 ≤ k → |ratioFloor k-L| < ε := by
  rintro ⟨L,hL⟩
  obtain ⟨K,hK⟩ := hL 1 (by norm_num)
  obtain ⟨j,hj⟩ := exists_nat_gt (|L|+K+5)
  have hjR : (2:ℝ) ≤ j := by
    have := abs_nonneg L
    have : (0:ℝ) ≤ K := by positivity
    linarith
  have hjN : 2 ≤ j := by exact_mod_cast hjR
  have hKj : K ≤ j := by
    have : (K:ℝ) ≤ j := by have := abs_nonneg L; linarith
    exact_mod_cast this
  have hh := (abs_lt.mp (hK j hKj hjN)).2
  have hg := ratio_grows (j:ℝ) hjR
  have := le_abs_self L
  linarith

end Bell.ContinuumShadows
