import Bell.ContextualFraction
import Bell.ChainAsymptotic

/-! Normalized local Gram certificates and their unbounded comparison envelope.
The finite profile and Clifford realization are separate from these certificate lemmas. -/
noncomputable section
open scoped BigOperators
namespace Bell.SmoothedComparison
open Bell.LinearProgramming Bell.SignedDuality Bell.ContextualFraction
variable {G I : Type} [Fintype G] [Fintype I]

def signed (l w : G → ℝ) (s : ℝ) (g : G) : ℝ :=
  l g / s - (1-s) / s * w g

theorem signed_total (l w : G → ℝ) (s : ℝ) (hs : 0 < s)
    (hl : ∑ g, l g = 1) (hw : ∑ g, w g = 1) :
    ∑ g, signed l w s g = 1 := by
  simp only [signed, Finset.sum_sub_distrib, ← Finset.sum_div,
    ← Finset.mul_sum, hl, hw]
  field_simp
  ring

omit [Fintype I] in
theorem signed_projects (A : G → I → ℝ) (l w : G → ℝ) (s : ℝ) (i : I) :
    mix A (signed l w s) i = mix A l i / s - (1-s) / s * mix A w i := by
  simp only [mix, signed, sub_mul, div_mul_eq_mul_div, Finset.sum_sub_distrib,
    Finset.sum_div, mul_assoc, Finset.mul_sum]

theorem signed_mass_bound (l w : G → ℝ) (s : ℝ) (hs : 0 < s) (hs1 : s ≤ 1)
    (hl : ∀ g, 0 ≤ l g) (hw : ∀ g, 0 ≤ w g) (hwt : ∑ g, w g = 1) :
    negativeMass (signed l w s) ≤ (1-s)/s := by
  have hc : 0 ≤ (1-s)/s := div_nonneg (by linarith) hs.le
  calc
    _ ≤ ∑ g, (1-s)/s * w g := by
      apply Finset.sum_le_sum
      intro g _
      apply max_le
      · dsimp [signed]; have := div_nonneg (hl g) hs.le; linarith
      · exact mul_nonneg hc (hw g)
    _ = _ := by rw [← Finset.mul_sum, hwt, mul_one]

theorem behavior_decomposition (s c a b : ℝ) (hs : s ≠ 0) :
    (1+a*b*(s*c))/4/s - (1-s)/s*(1/4) = (1+a*b*c)/4 := by
  field_simp
  ring

def normSquare (k : ℝ) : ℝ := 1 - (k^2-1)/(3*k^3)
def massCap (k : ℝ) : ℝ := (1-normSquare k)/normSquare k
def fractionFloor (k : ℝ) : ℝ := 1 - 1/(k*normSquare k)
def ratioFloor (k : ℝ) : ℝ := 3*k-4+3/(k+1)

theorem norm_bounds (k : ℝ) (hk : 2 ≤ k) :
    1/2 < normSquare k ∧ normSquare k < 1 := by
  have hk0 : 0 < k := by linarith
  have hd : 0 < 3*k^3 := by positivity
  have hsq : 0 < k^2-1 := by nlinarith
  have hc : k^2-1 < (3*k^3)/2 := by nlinarith [sq_nonneg (k-1)]
  constructor
  · have : (k^2-1)/(3*k^3) < 1/2 := (div_lt_iff₀ hd).2 (by linarith)
    dsimp [normSquare]; linarith
  · have := div_pos hsq hd
    dsimp [normSquare]; linarith

theorem massCap_positive (k : ℝ) (hk : 2 ≤ k) : 0 < massCap k := by
  obtain ⟨h0,h1⟩ := norm_bounds k hk
  exact div_pos (by linarith) (by linarith)

theorem ratio_identity (k : ℝ) (hk : 2 ≤ k) :
    fractionFloor k = ratioFloor k * massCap k := by
  have hk0 : k ≠ 0 := by linarith
  have hn : normSquare k ≠ 0 := ne_of_gt (lt_trans (by norm_num) (norm_bounds k hk).1)
  have hk1 : k+1 ≠ 0 := by linarith
  have he : normSquare k - 1/k = ratioFloor k * (1-normSquare k) := by
    dsimp [normSquare,ratioFloor]
    field_simp
    ring
  calc
    fractionFloor k = (normSquare k - 1/k)/normSquare k := by
      dsimp [fractionFloor]
      field_simp
    _ = (ratioFloor k * (1-normSquare k))/normSquare k := by rw [he]
    _ = _ := by rw [mul_div_assoc]; rfl

theorem ratio_grows (k : ℝ) (hk : 2 ≤ k) : 3*k-4 < ratioFloor k := by
  have : 0 < 3/(k+1) := div_pos (by norm_num) (by linarith)
  dsimp [ratioFloor]; linarith

theorem fractionFloor_positive (k : ℝ) (hk : 2 ≤ k) : 0 < fractionFloor k := by
  rw [ratio_identity k hk]
  exact mul_pos (by have := ratio_grows k hk; linarith) (massCap_positive k hk)

/-- A lower CF witness and an upper signed-mass certificate suffice; no optimal
signed extension or packing is assumed. -/
theorem comparison_from_certificates (k cf nm : ℝ) (hk : 2 ≤ k)
    (hu : nm ≤ massCap k) (hl : fractionFloor k ≤ cf) :
    ratioFloor k * nm ≤ cf := by
  have hr : 0 ≤ ratioFloor k := by have := ratio_grows k hk; linarith
  have := mul_le_mul_of_nonneg_left hu hr
  rw [← ratio_identity k hk] at this
  linarith

/-- Quantified failure of every proposed nonnegative constant, for any sequence
satisfying the explicit certificate envelopes. -/
theorem no_uniform_coefficient (cf nm : ℕ → ℝ)
    (hcf : ∀ k : ℕ, 2 ≤ k → fractionFloor k ≤ cf k)
    (hn : ∀ k : ℕ, 2 ≤ k → nm k ≤ massCap k) :
    ∀ C : ℝ, 0 ≤ C → ∃ k : ℕ, 2 ≤ k ∧ C * nm k < cf k := by
  intro C hC
  obtain ⟨k,hk⟩ := exists_nat_gt (C+4)
  have hkR : 2 ≤ (k:ℝ) := by linarith
  have hkN : 2 ≤ k := by exact_mod_cast hkR
  have hr : C < ratioFloor k := by have := ratio_grows k hkR; linarith
  have hm := massCap_positive (k:ℝ) hkR
  have hlt := mul_lt_mul_of_pos_right hr hm
  rw [← ratio_identity (k:ℝ) hkR] at hlt
  exact ⟨k,hkN,lt_of_le_of_lt (mul_le_mul_of_nonneg_left (hn k hkN) hC)
    (lt_of_lt_of_le hlt (hcf k hkN))⟩

end Bell.SmoothedComparison
