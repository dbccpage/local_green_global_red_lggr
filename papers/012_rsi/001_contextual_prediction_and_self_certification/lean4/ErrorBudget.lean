import ContextualDuality

open scoped BigOperators
namespace EpistemicNoGo.ErrorBudget

open EpistemicNoGo.ContextualDuality

/-- Explicit observation bridge from a state-space enclosure to the raw l1
    uncertainty radius used by the contextuality witness. -/
theorem observation_radius {E I : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [Fintype I] (O : I → E →L[ℝ] ℝ) (x y : E) :
    (∑ i, |O i x - O i y|) ≤ (∑ i, ‖O i‖) * ‖x - y‖ := by
  rw [Finset.sum_mul]
  apply Finset.sum_le_sum
  intro i _
  simpa only [map_sub, Real.norm_eq_abs] using (O i).le_opNorm (x - y)

theorem nearest_distance_lipschitz {E : Type*} [NormedAddCommGroup E]
    (K : Set E) (e f x y : E) (hx : x ∈ K) (hy : y ∈ K)
    (hmin : ∀ z ∈ K, ‖e - x‖ ≤ ‖e - z‖)
    (hmin' : ∀ z ∈ K, ‖f - y‖ ≤ ‖f - z‖) :
    |‖e - x‖ - ‖f - y‖| ≤ ‖e - f‖ := by
  have h1 := (hmin y hy).trans (norm_sub_le_norm_sub_add_norm_sub e f y)
  have h2 := (hmin' x hx).trans (norm_sub_le_norm_sub_add_norm_sub f e x)
  rw [norm_sub_rev f e] at h2
  exact abs_le.mpr ⟨by linarith, by linarith⟩

/-- A replayed feasible witness remains valid throughout an explicitly supplied
    raw l1 uncertainty ball. No statistical coverage is inferred. -/
theorem uncertainty_adjusted_witness {I G : Type*} [Fintype I] [Fintype G]
    (A : G → I → ℝ) (truth observed y : I → ℝ) (z ρ : ℝ) (p : G → ℝ)
    (hp : ∀ g, 0 ≤ p g) (hs : ∑ g, p g = 1)
    (hy : ∀ i, |y i| ≤ 1) (hz : ∀ g, pairing y (A g) + z ≤ 0)
    (hρ : ∑ i, |observed i - truth i| ≤ ρ) :
    max 0 (pairing y observed + z - ρ) ≤ cost A truth p := by
  have hpert : pairing y observed - pairing y truth ≤ ρ := by
    calc
      _ = ∑ i, y i * (observed i - truth i) := by
        simp [pairing, mul_sub, Finset.sum_sub_distrib]
      _ ≤ ∑ i, |observed i - truth i| := by
        apply Finset.sum_le_sum
        intro i _
        calc
          _ ≤ |y i * (observed i - truth i)| := le_abs_self _
          _ = |y i| * |observed i - truth i| := abs_mul _ _
          _ ≤ 1 * |observed i - truth i| := mul_le_mul_of_nonneg_right (hy i) (abs_nonneg _)
          _ = _ := one_mul _
      _ ≤ ρ := hρ
  apply max_le
  · exact Finset.sum_nonneg (fun i _ => abs_nonneg _)
  · linarith [weak_duality A truth y p z hp hs hy hz]

def envelope (L initial : ℝ) (residual : ℕ → ℝ) : ℕ → ℝ
  | 0 => initial
  | k + 1 => L * envelope L initial residual k + residual k

/-- Error propagation for actual one-step maps and actual implementation
    defects. All integration, rounding, observation and adaptation error must
    be included in residual; an initial normal velocity is insufficient. -/
theorem trajectory_error_bound {E : Type*} [NormedAddCommGroup E]
    (F : ℕ → E → E) (exact approx : ℕ → E) (L initial : ℝ) (residual : ℕ → ℝ)
    (hL : 0 ≤ L) (hinit : ‖exact 0 - approx 0‖ ≤ initial)
    (hexact : ∀ k, exact (k + 1) = F k (exact k))
    (hlip : ∀ k x y, ‖F k x - F k y‖ ≤ L * ‖x - y‖)
    (hres : ∀ k, ‖F k (approx k) - approx (k + 1)‖ ≤ residual k) :
    ∀ k, ‖exact k - approx k‖ ≤ envelope L initial residual k := by
  intro k
  induction k with
  | zero => exact hinit
  | succ k ih =>
    rw [hexact k]
    calc
      ‖F k (exact k) - approx (k + 1)‖ ≤
          ‖F k (exact k) - F k (approx k)‖ + ‖F k (approx k) - approx (k + 1)‖ :=
        norm_sub_le_norm_sub_add_norm_sub _ _ _
      _ ≤ L * ‖exact k - approx k‖ + residual k := add_le_add (hlip k _ _) (hres k)
      _ ≤ envelope L initial residual (k + 1) :=
        add_le_add (mul_le_mul_of_nonneg_left ih hL) le_rfl

theorem constant_residual_envelope (L initial η : ℝ) (k : ℕ) :
    envelope L initial (fun _ => η) k = L ^ k * initial + (Finset.range k).sum (fun i => L ^ i) * η := by
  have hg : ∀ k : ℕ, L * (Finset.range k).sum (fun i => L ^ i) + 1 =
      (Finset.range k).sum (fun i => L ^ i) + L ^ k := by
    intro k
    induction k with
    | zero => simp
    | succ k ih =>
      rw [Finset.sum_range_succ, pow_succ]
      nlinarith
  induction k with
  | zero => simp [envelope]
  | succ k ih =>
    rw [envelope, ih, Finset.sum_range_succ, pow_succ]
    calc
      _ = L ^ k * L * initial +
          (L * (Finset.range k).sum (fun i => L ^ i) + 1) * η := by ring
      _ = _ := by rw [hg k]

theorem nonexpansive_envelope (initial η : ℝ) (k : ℕ) :
    envelope 1 initial (fun _ => η) k = initial + k * η := by
  rw [constant_residual_envelope]
  simp

/-- A sufficient waiting window under a certified constant residual cap.
    It is not a necessary failure time: the enclosure can be conservative. -/
theorem correction_window (initial η tolerance : ℝ) (k : ℕ)
    (hη : 0 < η) (hk : (k : ℝ) ≤ (tolerance - initial) / η) :
    envelope 1 initial (fun _ => η) k ≤ tolerance := by
  rw [nonexpansive_envelope]
  have hh := (le_div_iff₀ hη).mp hk
  linarith

/-- Conditional scalar consequence of the Duhamel enclosure in PO033 §3.1.
    The continuous-time enclosure and rate cap are hypotheses, not an ODE
    integration or quadrature theorem proved in this package. -/
theorem duhamel_waiting_window (error observable initial rate time tolerance : ℝ)
    (ho : 0 < observable) (hr : 0 < rate)
    (henclosure : error ≤ observable * (initial + rate * time))
    (ht : time ≤ (tolerance / observable - initial) / rate) : error ≤ tolerance := by
  have hh := (le_div_iff₀ hr).mp ht
  have hh' := (le_div_iff₀ ho).mp (by linarith : initial + rate * time ≤ tolerance / observable)
  nlinarith

/-- A leakage lower bound is useful as a threshold obstruction only when
    correction capacity is independently bounded in the same metric. -/
theorem correction_capacity_lower_bound (defect remaining removed ν K t c : ℝ)
    (hdefect : ν * t - K * t ^ 2 ≤ defect)
    (hremove : removed ≤ c * t) (hremaining : defect - removed ≤ remaining) :
    (ν - c) * t - K * t ^ 2 ≤ remaining := by nlinarith

theorem threshold_missed (defect remaining removed ν K t c tolerance : ℝ)
    (hdefect : ν * t - K * t ^ 2 ≤ defect)
    (hremove : removed ≤ c * t) (hremaining : defect - removed ≤ remaining)
    (hthreshold : tolerance < (ν - c) * t - K * t ^ 2) : tolerance < remaining :=
  hthreshold.trans_le (correction_capacity_lower_bound defect remaining removed ν K t c
    hdefect hremove hremaining)

end EpistemicNoGo.ErrorBudget
