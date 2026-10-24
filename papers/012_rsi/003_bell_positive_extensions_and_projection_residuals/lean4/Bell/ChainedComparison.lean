import Bell.ChainedData

/-! Exact packing and signed-extension optima for the full nine-context chained line. -/
noncomputable section
open scoped BigOperators
namespace Bell.ChainedComparison
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality
set_option maxHeartbeats 1000000
set_option maxRecDepth 100000

def A (g : Fin 64) (i : Fin 36) : ℝ := ChainedData.A g i
def c (i : Fin 36) : ℝ := ChainedData.c i
def plus (g : Fin 64) : ℝ := ChainedData.plus g
def minus (g : Fin 64) : ℝ := ChainedData.minus g
def point (v : ℝ) (i : Fin 36) : ℝ := (1+v*c i)/4
def extension (v : ℝ) (g : Fin 64) : ℝ :=
  ((2+3*v)*plus g + (2-3*v)*minus g)/48
def localPart (v : ℝ) (g : Fin 64) : ℝ := (1-v)*plus g/4
def dual (i : Fin 36) : ℝ := ChainedData.y i

theorem plus_total : ∑ g, plus g = 12 := by
  dsimp only [plus]; exact_mod_cast ChainedData.plus_count
theorem minus_total : ∑ g, minus g = 12 := by
  dsimp only [minus]; exact_mod_cast ChainedData.minus_count
theorem plus_projects (i : Fin 36) : (∑ g, plus g*A g i) = 3+2*c i := by
  dsimp only [plus,A,c]
  exact_mod_cast ChainedData.plus_fiber i
theorem minus_projects (i : Fin 36) : (∑ g, minus g*A g i) = 3-2*c i := by
  dsimp only [minus,A,c]
  exact_mod_cast ChainedData.minus_fiber i
theorem columns (g : Fin 64) : ∑ i, A g i = 9 := by
  dsimp only [A]; exact_mod_cast ChainedData.column g
theorem coefficient_values (i : Fin 36) : c i = -1 ∨ c i = 0 ∨ c i = 1 := by
  dsimp only [c]
  exact_mod_cast ChainedData.coefficients i
theorem sum_coefficients : ∑ i, c i = 0 := by
  dsimp only [c]; exact_mod_cast ChainedData.sum_c

theorem point_nonnegative (v : ℝ) (hv : 0 ≤ v) (h1 : v ≤ 1) :
    ∀ i, 0 ≤ point v i := by
  intro i
  rcases coefficient_values i with h | h | h <;> simp [point,h] <;> linarith

theorem point_total (v : ℝ) : ∑ i, point v i = 9 := by
  norm_num [point, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.sum_div,
    sum_coefficients]

theorem extension_total (v : ℝ) : ∑ g, extension v g = 1 := by
  simp only [extension, ← Finset.sum_div, Finset.sum_add_distrib,
    ← Finset.mul_sum, plus_total, minus_total]
  ring

theorem extension_projects (v : ℝ) : mix A (extension v) = point v := by
  funext i
  simp only [mix, extension, add_mul, div_mul_eq_mul_div, mul_assoc,
    ← Finset.sum_div, Finset.sum_add_distrib, ← Finset.mul_sum,
    plus_projects, minus_projects, point]
  ring

theorem local_total (v : ℝ) : ∑ g, localPart v g = 3*(1-v) := by
  simp only [localPart, ← Finset.sum_div, ← Finset.mul_sum, plus_total]
  ring

theorem local_projects (v : ℝ) (i : Fin 36) :
    mix A (localPart v) i = (1-v)*(3+2*c i)/4 := by
  simp only [mix, localPart, div_mul_eq_mul_div, mul_assoc, ← Finset.sum_div,
    ← Finset.mul_sum, plus_projects]

theorem local_feasible (v : ℝ) (hv : 2/3 ≤ v) (h1 : v ≤ 1) :
    Packing A (point v) (localPart v) := by
  constructor
  · intro g
    have h : 0 ≤ plus g := by unfold plus ChainedData.plus; split_ifs <;> norm_num
    exact div_nonneg (mul_nonneg (by linarith) h) (by norm_num)
  · intro i
    rw [local_projects]
    rcases coefficient_values i with h | h | h <;> simp [point,h] <;> linarith

theorem dual_feasible : (∀ i, 0 ≤ dual i) ∧ ∀ g, 1 ≤ pairing dual (A g) := by
  constructor
  · intro i; dsimp only [dual]; exact_mod_cast ChainedData.dual_nonnegative i
  · intro g; dsimp only [pairing,dual,A]; exact_mod_cast ChainedData.dual_cover g

theorem dual_value (v : ℝ) : pairing dual (point v) = 3*(1-v) := by
  have h1 : (∑ i, dual i) = 12 := by
    dsimp only [dual]; exact_mod_cast ChainedData.dual_sum
  have hc : (∑ i, dual i*c i) = -12 := by
    dsimp only [dual,c]; exact_mod_cast ChainedData.dual_c
  have he (i : Fin 36) : dual i*point v i = (dual i+v*(dual i*c i))/4 := by
    unfold point; ring
  simp only [pairing, he, ← Finset.sum_div, Finset.sum_add_distrib,
    ← Finset.mul_sum, h1,hc]
  ring

theorem contextual_fraction (v : ℝ) (hv : 2/3 ≤ v) (h1 : v ≤ 1) :
    fraction A (point v) = 3*v-2 := by
  have h := certificate_exact A (point v) dual (localPart v)
    (weights_bounded A (point v) 9 (by norm_num) columns (point_total v))
    (point_nonnegative v (by linarith) h1) (local_feasible v hv h1)
    dual_feasible.1 dual_feasible.2 (by rw [dual_value, local_total])
  rw [local_total] at h
  linarith

theorem extension_mass (v : ℝ) (hv : 2/3 ≤ v) :
    negativeMass (extension v) = (3*v-2)/4 := by
  have h (g : Fin 64) : max (-extension v g) 0 = (3*v-2)/48 * minus g := by
    rcases ChainedData.score_values g with hk | hk | hk
    · simp [extension, plus, minus, ChainedData.plus, ChainedData.minus, hk]
      rw [max_eq_left (by linarith)]
      ring
    · simp [extension, plus, minus, ChainedData.plus, ChainedData.minus, hk]
    · simp [extension, plus, minus, ChainedData.plus, ChainedData.minus, hk]
      linarith
  simp only [negativeMass, h, ← Finset.mul_sum, minus_total]
  ring

theorem score (v : ℝ) : pairing c (point v) = 6*v := by
  have hs : (∑ i, c i*c i) = 24 := by
    dsimp only [c]; exact_mod_cast ChainedData.sum_c_sq
  have he (i : Fin 36) : c i*point v i = (c i+v*(c i*c i))/4 := by
    unfold point; ring
  simp only [pairing, he, ← Finset.sum_div, Finset.sum_add_distrib,
    ← Finset.mul_sum, sum_coefficients,hs]
  ring

theorem score_column (g : Fin 64) : pairing c (A g) = (ChainedData.K g:ℝ) := by
  unfold pairing c A ChainedData.K
  push_cast
  rfl

theorem negative_mass_lower (v : ℝ) (q : Fin 64 → ℝ)
    (hq : mix A q = point v) (hn : ∑ g, q g = 1) :
    (3*v-2)/4 ≤ negativeMass q := by
  have hd (g : Fin 64) :
      -1 ≤ pairing (fun i => c i/8) (A g) + (-1/2) ∧
      pairing (fun i => c i/8) (A g) + (-1/2) ≤ 0 := by
    have he : pairing (fun i => c i/8) (A g) = (ChainedData.K g:ℝ)/8 := by
      simp only [pairing, div_mul_eq_mul_div, ← Finset.sum_div]
      rw [show (∑ i, c i*A g i) = (ChainedData.K g:ℝ) from score_column g]
    rw [he]
    rcases ChainedData.score_values g with hk | hk | hk <;> simp [hk] <;> norm_num
  have hw := negative_mass_weak_duality A (point v) (fun i => c i/8) q (-1/2) hq hn hd
  have he : pairing (fun i => c i/8) (point v) = 6*v/8 := by
    simp only [pairing, div_mul_eq_mul_div, ← Finset.sum_div]
    rw [show (∑ i, c i*point v i) = 6*v from score v]
  rw [he] at hw
  linarith

/-- The factor four is exact on this line, for real optimizations over all 64 assignments. -/
theorem exact_comparison (v : ℝ) (hv : 2/3 ≤ v) (h1 : v ≤ 1) :
    fraction A (point v) = 4*negativeMass (extension v) ∧
    mix A (extension v) = point v ∧ (∑ g, extension v g = 1) ∧
    ∀ q, mix A q = point v → (∑ g, q g = 1) →
      negativeMass (extension v) ≤ negativeMass q := by
  refine ⟨?_, extension_projects v, extension_total v, ?_⟩
  · rw [contextual_fraction v hv h1, extension_mass v hv]; ring
  · intro q hq hn
    rw [extension_mass v hv]
    exact negative_mass_lower v q hq hn

theorem strict_separation (v : ℝ) (hv : 2/3 < v) (h1 : v ≤ 1) :
    2*negativeMass (extension v) < fraction A (point v) := by
  rw [contextual_fraction v hv.le h1, extension_mass v hv.le]
  linarith

end Bell.ChainedComparison

