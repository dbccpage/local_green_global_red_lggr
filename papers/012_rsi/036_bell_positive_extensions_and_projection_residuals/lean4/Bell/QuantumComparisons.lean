import Bell.BinaryScenarios
import Bell.QuantumExample

/-! Quantum-restricted comparison on the specified isotropic CHSH line.
The Hilbert-space hypothesis yields the cap; it is not an arbitrary
assumed scalar ceiling. These are not claims about all Bell scenarios. -/
noncomputable section
open scoped BigOperators
namespace Bell.QuantumComparisons
open Bell.LinearProgramming Bell.NegativeMassFamilies Bell.BinaryScenarios

def nCHSH (v : ℝ) : ℝ := max 0 (v-1/2)
def cfCHSH (v : ℝ) : ℝ := max 0 (2*v-1)

theorem line_comparison (v : ℝ) : cfCHSH v = 2*nCHSH v := by
  dsimp [cfCHSH, nCHSH]
  by_cases h : v ≤ 1/2
  · rw [max_eq_left (by linarith), max_eq_left (by linarith)]; ring
  · rw [max_eq_right (by linarith), max_eq_right (by linarith)]; ring

theorem capped_comparison (v : ℝ) (hv : 0 ≤ v) (hcap : 4*v ≤ 2*Real.sqrt 2) :
    Bell.ContextualFraction.fraction chsh.A (behavior chsh v) = 2*nCHSH v ∧
    nCHSH v ≤ (Real.sqrt 2-1)/2 ∧
    Bell.ContextualFraction.fraction chsh.A (behavior chsh v) ≤ Real.sqrt 2-1 := by
  have hs := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)
  have hz := Real.sqrt_nonneg (2:ℝ)
  have h1 : v ≤ 1 := by nlinarith
  have hn : nCHSH v ≤ (Real.sqrt 2-1)/2 := by
    apply max_le <;> nlinarith
  rw [chsh_contextual_fraction v hv h1]
  have hc := line_comparison v
  dsimp [cfCHSH] at hc
  exact ⟨hc, hn, by linarith⟩

theorem quantum_line_comparison {E : Type} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (A₀ A₁ B₀ B₁ : E →L[ℂ] E)
    (hA₀ : ‖A₀‖ ≤ 1) (hA₁ : ‖A₁‖ ≤ 1) (hB₀ : ‖B₀‖ ≤ 1) (hB₁ : ‖B₁‖ ≤ 1)
    (ψ : E) (hψ : ‖ψ‖=1) (v : ℝ) (hv : 0 ≤ v)
    (hscore : Bell.Quantum.expectation ψ (Bell.Quantum.chsh A₀ A₁ B₀ B₁) = 4*v) :
    Bell.ContextualFraction.fraction chsh.A (behavior chsh v) = 2*nCHSH v ∧
    nCHSH v ≤ (Real.sqrt 2-1)/2 ∧
    Bell.ContextualFraction.fraction chsh.A (behavior chsh v) ≤ Real.sqrt 2-1 := by
  have h := Bell.Quantum.tsirelson_pure_state_bound A₀ A₁ B₀ B₁ hA₀ hA₁ hB₀ hB₁ ψ hψ
  rw [hscore, abs_of_nonneg (by positivity)] at h
  exact capped_comparison v hv h

theorem cap_attained : nCHSH Bell.QuantumExample.t = (Real.sqrt 2-1)/2 ∧
    cfCHSH Bell.QuantumExample.t = Real.sqrt 2-1 := by
  have hs := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)
  have hz := Real.sqrt_nonneg (2:ℝ)
  have hn : Real.sqrt 2 ≠ 0 := by nlinarith
  have he : Bell.QuantumExample.t = Real.sqrt 2/2 := by
    unfold Bell.QuantumExample.t
    field_simp
    nlinarith
  dsimp [nCHSH, cfCHSH]
  rw [he, max_eq_right (by nlinarith), max_eq_right (by nlinarith)]
  constructor <;> ring

end Bell.QuantumComparisons
