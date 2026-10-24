import Bell.FullChainBounds

/-! A quantified asymptotic coefficient for complete equally spaced chains. -/
noncomputable section
namespace Bell.ChainAsymptotic
open Bell.ChainAnalysis

theorem eventual_coefficient (k : ℝ) (hk : 2*(Real.sqrt 2+1) < k) :
    ∃ cutoff : ℕ, ∀ n : ℕ, cutoff ≤ n → ∀ CF N : ℝ, CF ≤ 1 →
      score (alice n) (bobLow n) (bobHigh n) ≤ 2*(1+2*N) → CF ≤ k*N := by
  have hs := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)
  have hn := Real.sqrt_nonneg (2:ℝ)
  have hroot : 1 < Real.sqrt 2 := by nlinarith
  have hk0 : 0 < k := by linarith
  let d := 2*Real.sqrt 2-2-4/k
  have hd : 0 < d := by
    have hp := mul_lt_mul_of_pos_left hk (by linarith : 0 < 2*Real.sqrt 2-2)
    have hprod : 4 < (2*Real.sqrt 2-2)*k := by nlinarith
    have hh := (div_lt_iff₀ hk0).2 hprod
    dsimp [d]; linarith
  obtain ⟨cutoff,hcut⟩ := exists_nat_gt (max 64 (6*Real.pi/d))
  refine ⟨cutoff,?_⟩
  intro n hcn CF N hCF hS
  have hcr : (cutoff:ℝ) ≤ n := by exact_mod_cast hcn
  have hn64 : (64:ℝ) < n := (le_max_left _ _).trans_lt (hcut.trans_le hcr)
  have hn0 : (0:ℝ) < n := by linarith
  have hn4 : 4 ≤ n := by norm_cast at hn64; omega
  have hdiv : 6*Real.pi/d < (n:ℝ) := (le_max_right _ _).trans_lt (hcut.trans_le hcr)
  have he : 6*Real.pi/(n:ℝ) < d := by
    apply (div_lt_iff₀ hn0).2
    have hh := (div_lt_iff₀ hd).mp hdiv
    nlinarith
  have hN := full_grid_mass_bound n hn4 N hS
  have hlow : 1/k ≤ N := by
    dsimp [d] at he
    simp only [div_eq_mul_inv] at he hN ⊢
    linarith
  have hmul : 1 ≤ k*N := by
    have hh := (div_le_iff₀ hk0).mp hlow
    simpa [mul_comm] using hh
  exact hCF.trans hmul

end Bell.ChainAsymptotic
