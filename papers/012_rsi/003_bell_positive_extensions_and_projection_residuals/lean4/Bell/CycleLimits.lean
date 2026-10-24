import Bell.CycleParity
import Bell.ChainAnalysis

/-! Quantum visibility and unbounded comparison in the cycle parity quotient.
The measured-cycle/full-table distinction is part of the statement. -/
noncomputable section
namespace Bell.CycleLimits
open Bell.CycleParity Bell.ChainAnalysis Bell.PlanarQuantum
def δ (n : ℕ) : ℝ := Real.pi/M n
def visibility (n : ℕ) : ℝ := Real.cos (δ n)

theorem quantum_visibility (n : ℕ) (hn : 3 ≤ n) :
    M n-2 < M n*visibility n ∧ visibility n ≤ 1 := by
  have hm := size_ge n
  have hm10 : (10:ℝ) ≤ M n := by dsimp [M,size]; norm_cast; omega
  have hδ : |δ n| ≤ 1 := by
    rw [abs_of_nonneg (by unfold δ; positivity)]
    unfold δ
    apply (div_le_one (by linarith)).2
    linarith [Real.pi_le_four]
  have hc := cosine_quadratic (δ n) hδ
  have hsq : (δ n)^2 < 2/M n := by
    unfold δ
    rw [div_pow]
    apply (div_lt_iff₀ (by nlinarith : 0 < (M n)^2)).2
    calc
      Real.pi^2 < 2*M n := by nlinarith [Real.pi_le_four,Real.pi_pos]
      _ = 2/M n*(M n)^2 := by field_simp [show M n ≠ 0 by linarith]
  constructor
  · change M n-2 < M n*Real.cos (δ n)
    have h := mul_lt_mul_of_pos_left hsq (by linarith : 0 < M n)
    have he : M n*(2/M n)=2 := by field_simp [show M n ≠ 0 by linarith]
    rw [he] at h
    nlinarith
  · exact Real.cos_le_one _

theorem cycle_quantum_cells (n : ℕ) (j : ℝ) (a b : Bool) :
    born (Real.cos (2*j*δ n)) (Real.sin (2*j*δ n))
      (Real.cos ((2*j+1)*δ n)) (Real.sin ((2*j+1)*δ n)) a b =
        (1+Bell.CHSH.sign a*Bell.CHSH.sign b*visibility n)/4 ∧
    born (Real.cos (2*(j+1)*δ n)) (Real.sin (2*(j+1)*δ n))
      (Real.cos ((2*j+1)*δ n)) (Real.sin ((2*j+1)*δ n)) a b =
        (1+Bell.CHSH.sign a*Bell.CHSH.sign b*visibility n)/4 := by
  constructor <;> rw [angle_born]
  · rw [show 2*j*δ n-(2*j+1)*δ n = -δ n by ring,Real.cos_neg]
    rfl
  · rw [show 2*(j+1)*δ n-(2*j+1)*δ n = δ n by ring]
    rfl

theorem closing_quantum_cell (n : ℕ) (a b : Bool) :
    born 1 0 (Real.cos ((M n-1)*δ n)) (Real.sin ((M n-1)*δ n)) a b =
      (1-Bell.CHSH.sign a*Bell.CHSH.sign b*visibility n)/4 := by
  have hm := size_ge n
  have he : (M n-1)*δ n = Real.pi-δ n := by
    unfold δ
    field_simp [show M n ≠ 0 by linarith]
  rw [born_formula,he,Real.cos_pi_sub]
  unfold visibility
  ring

theorem cycle_unbounded (K : ℝ) : ∃ n : ℕ,
    0 < Bell.SignedDuality.negativeMass (extension n (visibility n)) ∧
    K*Bell.SignedDuality.negativeMass (extension n (visibility n)) <
      Bell.ContextualFraction.fraction (A n) (point n (visibility n)) := by
  obtain ⟨n,hn⟩ := exists_nat_gt (max K 3)
  have hn3 : 3 ≤ n := by have := (le_max_right K 3).trans hn.le; exact_mod_cast this
  have hk : K < (n:ℝ) := (le_max_left K 3).trans_lt hn
  have hv := quantum_visibility n hn3
  have hm := size_ge n
  have he := exact_comparison n (visibility n) hv.1.le hv.2
  have hp : 0 < mass n (visibility n) := by unfold mass; apply div_pos <;> linarith
  refine ⟨n,he.1.symm ▸ hp,?_⟩
  rw [he.1,he.2]
  apply mul_lt_mul_of_pos_right _ hp
  dsimp [M,size]
  push_cast
  linarith

end Bell.CycleLimits
