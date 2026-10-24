import Bell.ComparisonData

/-! Exact real primal/dual certificates for a separation of CF and 2N.
Integer finite checks are transported to real optimization statements. -/
noncomputable section
open scoped BigOperators
namespace Bell.Comparison
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality
open Bell.BinaryScenarios

def point (i : Fin 64) : ℝ := (ComparisonData.pI i : ℝ)/768
def localPart (g : Fin 64) : ℝ := (ComparisonData.gammaI g : ℝ)/768
def cfDual (i : Fin 64) : ℝ := (ComparisonData.yI i : ℝ)
def signedPart (g : Fin 64) : ℝ := (ComparisonData.qI g : ℝ)/768
def nDual (i : Fin 64) : ℝ := (ComparisonData.zI i : ℝ)/2

theorem point_nonnegative : ∀ i, 0 ≤ point i := by
  intro i
  exact div_nonneg (by exact_mod_cast ComparisonData.p_nonnegative i) (by norm_num)

theorem point_total : ∑ i, point i = 8 := by
  have h : (∑ i, (ComparisonData.pI i : ℝ)) = 6144 := by exact_mod_cast ComparisonData.p_total
  simp only [point, ← Finset.sum_div, h]
  norm_num

theorem local_feasible : Packing mermin.A point localPart := by
  constructor
  · intro g
    exact div_nonneg (by exact_mod_cast ComparisonData.gamma_nonnegative g) (by norm_num)
  · intro i
    change (∑ g, (ComparisonData.gammaI g:ℝ)/768 * (merminAI g i:ℝ)) ≤
      (ComparisonData.pI i:ℝ)/768
    simp only [div_mul_eq_mul_div, ← Finset.sum_div]
    apply div_le_div_of_nonneg_right _ (by norm_num)
    exact_mod_cast ComparisonData.gamma_feasible i

theorem local_total : ∑ g, localPart g = 45/64 := by
  have h : (∑ g, (ComparisonData.gammaI g:ℝ)) = 540 := by exact_mod_cast ComparisonData.gamma_total
  simp only [localPart, ← Finset.sum_div, h]
  norm_num

theorem cf_dual_feasible : (∀ i, 0 ≤ cfDual i) ∧ ∀ g, 1 ≤ pairing cfDual (mermin.A g) := by
  constructor
  · intro i; dsimp only [cfDual]; exact_mod_cast ComparisonData.y_nonnegative i
  · intro g
    change 1 ≤ ∑ i, (ComparisonData.yI i:ℝ) * (merminAI g i:ℝ)
    exact_mod_cast ComparisonData.y_feasible g

theorem cf_dual_value : pairing cfDual point = 45/64 := by
  have h : (∑ i, (ComparisonData.yI i:ℝ) * (ComparisonData.pI i:ℝ)) = 540 := by
    exact_mod_cast ComparisonData.cf_gap
  simp only [pairing, cfDual, point, ← mul_div_assoc, ← Finset.sum_div, h]
  norm_num

theorem contextual_fraction : fraction mermin.A point = 19/64 := by
  have hb := weights_bounded mermin.A point 8 (by norm_num) mermin.column point_total
  have he := certificate_exact mermin.A point cfDual localPart hb point_nonnegative
    local_feasible cf_dual_feasible.1 cf_dual_feasible.2 (by rw [cf_dual_value, local_total])
  rw [local_total] at he
  norm_num at he
  exact he

theorem signed_total : ∑ g, signedPart g = 1 := by
  have h : (∑ g, (ComparisonData.qI g:ℝ)) = 768 := by exact_mod_cast ComparisonData.q_total
  simp only [signedPart, ← Finset.sum_div, h]
  norm_num

theorem signed_projects : mix mermin.A signedPart = point := by
  funext i
  change (∑ g, (ComparisonData.qI g:ℝ)/768 * (merminAI g i:ℝ)) =
    (ComparisonData.pI i:ℝ)/768
  simp only [div_mul_eq_mul_div, ← Finset.sum_div]
  congr 1
  exact_mod_cast ComparisonData.q_projects i

theorem signed_mass : negativeMass signedPart = 25/256 := by
  have scale (x : ℝ) : max (-(x/768)) 0 = max (-x) 0 / 768 := by
    rcases le_total 0 x with h | h
    · have hx : 0 ≤ x/768 := div_nonneg h (by norm_num)
      rw [max_eq_right (by linarith), max_eq_right (by linarith)]
      norm_num
    · have hx : x/768 ≤ 0 := div_nonpos_of_nonpos_of_nonneg h (by norm_num)
      rw [max_eq_left (by linarith), max_eq_left (by linarith)]
      ring
  have h : (∑ g, max (-(ComparisonData.qI g:ℝ)) 0) = 75 := by
    exact_mod_cast ComparisonData.q_mass
  simp only [negativeMass, signedPart, scale, ← Finset.sum_div, h]
  norm_num

theorem n_dual_feasible : ∀ g, -1 ≤ pairing nDual (mermin.A g) + 0 ∧
    pairing nDual (mermin.A g) + 0 ≤ 0 := by
  intro g
  have hlo : -2 ≤ ∑ i, (ComparisonData.zI i:ℝ) * (merminAI g i:ℝ) := by
    exact_mod_cast (ComparisonData.z_feasible g).1
  have hhi : (∑ i, (ComparisonData.zI i:ℝ) * (merminAI g i:ℝ)) ≤ 0 := by
    exact_mod_cast (ComparisonData.z_feasible g).2
  change -1 ≤ (∑ i, (ComparisonData.zI i:ℝ)/2 * (merminAI g i:ℝ)) + 0 ∧
    (∑ i, (ComparisonData.zI i:ℝ)/2 * (merminAI g i:ℝ)) + 0 ≤ 0
  simp only [div_mul_eq_mul_div, ← Finset.sum_div]
  constructor <;> linarith

theorem n_dual_value : pairing nDual point = 25/256 := by
  have h : (∑ i, (ComparisonData.zI i:ℝ) * (ComparisonData.pI i:ℝ)) = 150 := by
    exact_mod_cast ComparisonData.n_gap
  have he : ∀ i, nDual i * point i =
      ((ComparisonData.zI i:ℝ)*(ComparisonData.pI i:ℝ))/1536 := by
    intro i; dsimp [nDual,point]; ring
  simp only [pairing, he, ← Finset.sum_div, h]
  norm_num

theorem negative_mass_optimal (q : Fin 64 → ℝ)
    (hq : mix mermin.A q = point) (hn : ∑ g, q g = 1) :
    25/256 ≤ negativeMass q := by
  have h := negative_mass_weak_duality mermin.A point nDual q 0 hq hn n_dual_feasible
  simpa [n_dual_value] using h

/-- Explicit violation with an attained minimum and every competing real extension excluded. -/
theorem cf_gt_twice_negative_mass :
    fraction mermin.A point > 2 * negativeMass signedPart ∧
    mix mermin.A signedPart = point ∧ (∑ g, signedPart g = 1) ∧
    ∀ q, mix mermin.A q = point → (∑ g, q g = 1) →
      negativeMass signedPart ≤ negativeMass q := by
  refine ⟨?_, signed_projects, signed_total, ?_⟩
  · rw [contextual_fraction, signed_mass]; norm_num
  · intro q hq hn
    rw [signed_mass]
    exact negative_mass_optimal q hq hn

/-- CF and minimum signed mass can rank two explicit no-signalling behaviors oppositely. -/
theorem ranking_reversal :
    fraction mermin.A (Bell.NegativeMassFamilies.behavior mermin (5/8)) <
      fraction mermin.A point ∧
    negativeMass signedPart <
      negativeMass (Bell.NegativeMassFamilies.extension mermin (5/8)) := by
  rw [contextual_fraction, signed_mass,
    mermin_contextual_fraction (5/8) (by norm_num) (by norm_num),
    Bell.NegativeMassFamilies.extension_negative_mass mermin (5/8) (by norm_num)]
  norm_num

end Bell.Comparison

