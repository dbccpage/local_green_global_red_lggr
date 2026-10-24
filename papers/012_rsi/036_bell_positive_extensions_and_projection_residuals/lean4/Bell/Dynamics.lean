import Bell.QuantumTrace

/-! Conditional finite-time oriented witnesses. Taylor control is a premise,
not a claim about an unspecified equation of motion. -/
noncomputable section
open scoped BigOperators Matrix.Norms.L2Operator
open Bell.QuantumState Bell.QuantumTrace Bell.CHSH
namespace Bell.Dynamics
variable {n : Type} [Fintype n] [DecidableEq n]

theorem trace_decomposition (ρ σ v E B : Operator n) (t : ℝ)
    (hd : ρ = σ + (t : ℂ) • v + E) :
    mean ρ B = mean σ B + t * mean v B + mean E B := by
  rw [hd, mean_add_left, mean_add_left, mean_real_smul]

theorem dynamical_witness (ρ σ v E B : Operator n) (t κ : ℝ)
    (hE : E.IsHermitian) (hd : ρ = σ + (t : ℂ) • v + E)
    (hr : traceNorm E hE ≤ κ * t ^ 2) :
    t * mean v B - ‖asOperator B‖ * κ * t ^ 2 - (2 - mean σ B) ≤
      mean ρ B - 2 := by
  have hb := trace_operator_bound E B hE
  have hm := mul_le_mul_of_nonneg_left hr (norm_nonneg (asOperator B))
  have ha := neg_abs_le (mean E B)
  rw [trace_decomposition ρ σ v E B t hd]
  nlinarith

theorem oriented_repair_bound (p l : Table) (L : ℝ)
    (hl : Bell.PositiveExtension l) (hL : L ≤ score p - 2) :
    max 0 L / 8 ≤ tv p l := by
  have hb := chsh_repair_lower_bound p l hl
  have ha := le_abs_self (score p)
  have hm : max 0 L ≤ max 0 (|score p| - 2) := max_le_max_left 0 (by linarith)
  linarith

theorem dynamical_born_repair (ρ σ v E : Operator n) (t κ : ℝ)
    (M N : Bool → Bool → Operator n) (l : Table)
    (hl : Bell.PositiveExtension l) (hE : E.IsHermitian)
    (hd : ρ = σ + (t : ℂ) • v + E) (hr : traceNorm E hE ≤ κ * t ^ 2) :
    let B := chshMatrix (observable (M false)) (observable (M true))
      (observable (N false)) (observable (N true))
    max 0 (t * mean v B - ‖asOperator B‖ * κ * t ^ 2 - (2 - mean σ B)) / 8 ≤
      tv (Bell.QuantumMeasurement.behavior ρ M N) l := by
  dsimp only
  apply oriented_repair_bound _ l _ hl
  rw [Bell.QuantumMeasurement.born_score_trace]
  exact dynamical_witness ρ σ v E _ t κ hE hd hr

theorem uncertain_oriented_repair (observed actual l : Table) (L ε : ℝ)
    (hl : Bell.PositiveExtension l) (he : tv observed actual ≤ ε)
    (hL : L ≤ score observed - 2) :
    max 0 (L - 8 * ε) / 8 ≤ tv actual l := by
  have hs := score_lipschitz observed actual
  have ha := le_abs_self (score observed - score actual)
  apply oriented_repair_bound actual l _ hl
  linarith

theorem oriented_exit (p : Table) (L : ℝ) (hL : L ≤ score p - 2) (hp : 0 < L) :
    ¬ Bell.PositiveExtension p := by
  apply violation_no_extension
  have ha := le_abs_self (score p)
  linarith

theorem quadratic_exit_window (b c t : ℝ)
    (ht : 0 < t) (hwindow : c * t < b) : 0 < t * b - c * t ^ 2 := by
  have h := mul_pos ht (sub_pos.mpr hwindow)
  nlinarith

theorem quadratic_linear_rate (b c t : ℝ) (ht : 0 ≤ t)
    (hwindow : c * t ≤ b / 2) : t * b / 2 ≤ t * b - c * t ^ 2 := by
  have h := mul_le_mul_of_nonneg_left hwindow ht
  nlinarith

theorem zero_remainder_window (b t : ℝ) (hb : 0 < b) (ht : 0 < t) :
    0 < t * b - (0 : ℝ) * t ^ 2 := by simpa using mul_pos ht hb

theorem face_exit_rate (p l : Table) (b c t : ℝ) (hl : Bell.PositiveExtension l)
    (ht : 0 ≤ t) (hwindow : c * t ≤ b / 2)
    (hscore : t * b - c * t ^ 2 ≤ score p - 2) : t * b / 16 ≤ tv p l := by
  have hr := quadratic_linear_rate b c t ht hwindow
  have hb := oriented_repair_bound p l _ hl hscore
  have hm := le_max_right 0 (t * b - c * t ^ 2)
  linarith

end Bell.Dynamics
