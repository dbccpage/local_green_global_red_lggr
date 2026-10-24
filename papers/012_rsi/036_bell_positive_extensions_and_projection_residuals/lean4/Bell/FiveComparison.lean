import Bell.FiveData

/-! Both exact real optima for the complete rational five-setting behavior. -/
noncomputable section
open scoped BigOperators
namespace Bell.FiveComparison
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality Bell.SparseCertificates
def A (g : Fin 1024) (i : Fin 100) : ℝ := FiveData.A g i
def point (i : Fin 100) : ℝ := FiveData.pn i / 136900
def qsmall (j : Fin 31) : ℝ := FiveData.qn j / 136900
def hsmall (j : Fin 20) : ℝ := FiveData.hn j / 136900
def extension := push FiveData.qid qsmall
def localPart := push FiveData.hid hsmall
def dual (i : Fin 100) : ℝ := FiveData.y i
def negativeDual (i : Fin 100) : ℝ := FiveData.z i

theorem point_nonnegative : ∀ i, 0 ≤ point i := by
  intro i; exact div_nonneg (by exact_mod_cast FiveData.cells_nonnegative i) (by norm_num)
theorem point_total : ∑ i, point i = 25 := by
  have h : (∑ i, (FiveData.pn i:ℝ)) = 3422500 := by exact_mod_cast FiveData.point_total
  simp only [point, ← Finset.sum_div, h]; norm_num
theorem weights_bounded : BddAbove (weights A point) := by
  let A0 (g : Fin 1024) (i : Fin 4) := A g ⟨i.val,by omega⟩
  let p0 (i : Fin 4) := point ⟨i.val,by omega⟩
  have hc (g : Fin 1024) : ∑ i, A0 g i = 1 := by
    dsimp only [A0,A]; exact_mod_cast FiveData.first_context g
  have hp : ∑ i, p0 i = 1 := by
    have hh : (∑ i : Fin 4, (FiveData.pn ⟨i.val,by omega⟩:ℝ)) = 136900 := by
      exact_mod_cast FiveData.context_total 0
    simp only [p0,point,← Finset.sum_div,hh]; norm_num
  refine ⟨1,?_⟩
  intro w ⟨q,hq,hw⟩
  rw [← hw]
  exact packing_mass_le A0 p0 1 (by norm_num) hc hp ⟨hq.1,fun i => hq.2 ⟨i.val,by omega⟩⟩
theorem extension_total : ∑ g, extension g = 1 := by
  have h : (∑ j, (FiveData.qn j:ℝ)) = 136900 := by exact_mod_cast FiveData.signed_total
  simp only [extension, push_total, qsmall, ← Finset.sum_div, h]; norm_num
theorem extension_projects : mix A extension = point := by
  funext i
  have h : (∑ j, (FiveData.qn j:ℝ)*(FiveData.A (FiveData.qid j) i:ℝ)) = FiveData.pn i := by
    exact_mod_cast FiveData.signed_projects i
  simp only [extension, push_mix, qsmall, A, div_mul_eq_mul_div, ← Finset.sum_div, h, point]
theorem extension_mass_upper : negativeMass extension ≤ 167/925 := by
  have h := push_negative_le FiveData.qid qsmall
  have hs : (∑ j, max (-(FiveData.qn j:ℝ)) 0) = 24716 := by
    exact_mod_cast FiveData.signed_negative
  have he (j : Fin 31) : max (-qsmall j) 0 = max (-(FiveData.qn j:ℝ)) 0/136900 := by
    simpa only [qsmall, neg_div, zero_div] using
      (max_div_div_right (by norm_num : (0:ℝ) ≤ 136900) (-(FiveData.qn j:ℝ)) 0)
  simp_rw [he] at h
  rw [← Finset.sum_div, hs] at h
  change negativeMass (push FiveData.qid qsmall) ≤ _
  convert h using 1; norm_num
theorem local_total : ∑ g, localPart g = 227/925 := by
  have h : (∑ j, (FiveData.hn j:ℝ)) = 33596 := by exact_mod_cast FiveData.packing_total
  simp only [localPart, push_total, hsmall, ← Finset.sum_div, h]; norm_num
theorem local_feasible : Packing A point localPart := by
  constructor
  · apply push_nonnegative; intro j
    exact div_nonneg (by exact_mod_cast FiveData.packing_nonnegative j) (by norm_num)
  · intro i
    have h : (∑ j, (FiveData.hn j:ℝ)*(FiveData.A (FiveData.hid j) i:ℝ)) ≤ FiveData.pn i := by
      exact_mod_cast FiveData.packing_projects i
    simp only [localPart, push_mix, hsmall, A, div_mul_eq_mul_div, ← Finset.sum_div, point]
    exact div_le_div_of_nonneg_right h (by norm_num)
theorem dual_feasible : (∀ i, 0 ≤ dual i) ∧ ∀ g, 1 ≤ pairing dual (A g) := by
  constructor
  · intro i; dsimp only [dual]; exact_mod_cast FiveData.cover_nonnegative i
  · intro g; dsimp only [pairing,dual,A]; exact_mod_cast FiveData.cover g
theorem dual_value : pairing dual point = 227/925 := by
  have h : (∑ i, (FiveData.y i:ℝ)*(FiveData.pn i:ℝ)) = 33596 := by
    exact_mod_cast FiveData.cover_value
  simp only [pairing, dual, point, ← mul_div_assoc, ← Finset.sum_div, h]; norm_num
theorem contextual_fraction : fraction A point = 698/925 := by
  have h := certificate_exact A point dual localPart
    weights_bounded
    point_nonnegative local_feasible dual_feasible.1 dual_feasible.2
    (by rw [dual_value,local_total])
  rw [local_total] at h; linarith
theorem negative_mass_lower (q : Fin 1024 → ℝ) (hq : mix A q = point)
    (hn : ∑ g, q g = 1) : 167/925 ≤ negativeMass q := by
  have hd (g : Fin 1024) : -1 ≤ pairing negativeDual (A g)+0 ∧
      pairing negativeDual (A g)+0 ≤ 0 := by
    simp only [add_zero,pairing,negativeDual,A]
    exact_mod_cast FiveData.signed_dual g
  have h := negative_mass_weak_duality A point negativeDual q 0 hq hn hd
  have hs : (∑ i, (FiveData.z i:ℝ)*(FiveData.pn i:ℝ)) = 24716 := by
    exact_mod_cast FiveData.signed_dual_value
  simp only [pairing, negativeDual, point, ← mul_div_assoc, ← Finset.sum_div, hs, add_zero] at h
  convert h using 1; norm_num
theorem extension_mass : negativeMass extension = 167/925 :=
  le_antisymm extension_mass_upper (negative_mass_lower extension extension_projects extension_total)
theorem exact_counterexample : fraction A point = 698/925 ∧
    negativeMass extension = 167/925 ∧ 4*negativeMass extension < fraction A point ∧
    (∀ q, mix A q = point → (∑ g, q g = 1) → negativeMass extension ≤ negativeMass q) := by
  refine ⟨contextual_fraction,extension_mass,?_,?_⟩
  · rw [contextual_fraction,extension_mass]; norm_num
  · intro q hq hn; rw [extension_mass]; exact negative_mass_lower q hq hn
theorem universal_coefficient (k : ℝ) (hk : fraction A point ≤ k*negativeMass extension) :
    698/167 ≤ k := by
  rw [contextual_fraction,extension_mass] at hk
  linarith
end Bell.FiveComparison
