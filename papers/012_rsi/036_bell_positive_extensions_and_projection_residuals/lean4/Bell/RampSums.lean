import Bell.SmoothedComparison

/-! Exact finite ramp sums used by the smoothed-square-wave construction. -/
noncomputable section
open scoped BigOperators
namespace Bell.RampSums

theorem sum_linear (n : ℕ) :
    (∑ j ∈ Finset.range n, (j:ℝ)) = (n:ℝ)*((n:ℝ)-1)/2 := by
  induction n with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ,ih]; push_cast; ring

theorem sum_square (n : ℕ) :
    (∑ j ∈ Finset.range n, (j:ℝ)^2) = (n:ℝ)*((n:ℝ)-1)*(2*(n:ℝ)-1)/6 := by
  induction n with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ,ih]; push_cast; ring

def ramp (k j : ℕ) : ℝ := -1+2*(j:ℝ)/(k:ℝ)

theorem ramp_bounds (k j : ℕ) (hk : 0 < k) (hj : j ≤ k) :
    -1 ≤ ramp k j ∧ ramp k j ≤ 1 := by
  have hkR : (0:ℝ) < k := by exact_mod_cast hk
  have hjR : (j:ℝ) ≤ k := by exact_mod_cast hj
  have h0 : 0 ≤ 2*(j:ℝ)/(k:ℝ) := by positivity
  have h2 : 2*(j:ℝ)/(k:ℝ) ≤ 2 := (div_le_iff₀ hkR).2 (by linarith)
  dsimp [ramp]; constructor <;> linarith

theorem ramp_difference (k j : ℕ) : ramp k (j+1)-ramp k j = 2/(k:ℝ) := by
  dsimp [ramp]; push_cast; ring

theorem ramp_square_sum (k : ℕ) (hk : 0 < k) :
    (∑ j ∈ Finset.range k, ramp k j ^ 2) = ((k:ℝ)^2+2)/(3*(k:ℝ)) := by
  have hk0 : (k:ℝ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hk)
  have he (j : ℕ) : ramp k j^2 = 1 - (4/(k:ℝ))*(j:ℝ) + (4/(k:ℝ)^2)*(j:ℝ)^2 := by
    dsimp [ramp]; ring
  simp_rw [he]
  rw [Finset.sum_add_distrib,Finset.sum_sub_distrib,← Finset.mul_sum,
    ← Finset.mul_sum,sum_linear,sum_square]
  simp only [Finset.sum_const,Finset.card_range,nsmul_eq_mul,mul_one]
  field_simp
  ring

/-- The two ramps plus the two flat stretches have total square D*s. -/
theorem full_square_sum (k : ℕ) (hk : 2 ≤ k) :
    2*((∑ j ∈ Finset.range k, ramp k j ^ 2) + (2*k*k-k:ℕ)) =
      (4*(k:ℝ)^2)*Bell.SmoothedComparison.normSquare k := by
  have hkle : k ≤ 2*k*k := by nlinarith
  have hk0 : (k:ℝ) ≠ 0 := by exact_mod_cast (show k ≠ 0 by omega)
  rw [ramp_square_sum k (by omega),Nat.cast_sub hkle]
  push_cast
  dsimp [Bell.SmoothedComparison.normSquare]
  field_simp
  ring

/-- There are exactly two ramps of k increments of size 2/k. -/
theorem active_edge_energy (k : ℕ) (hk : 0 < k) :
    2*(∑ j ∈ Finset.range k, (ramp k (j+1)-ramp k j)^2) = 8/(k:ℝ) := by
  have hk0 : (k:ℝ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hk)
  simp_rw [ramp_difference]
  simp only [Finset.sum_const,Finset.card_range,nsmul_eq_mul]
  field_simp
  ring

theorem norm_energy_to_visibility (k s v : ℝ) (hk : 0 < k) (hs : 0 < s)
    (h : 2*(4*k^2*s)*(1-v) = 8/k) : k^2*(1-v) = 1/(k*s) := by
  apply (eq_div_iff (ne_of_gt (mul_pos hk hs))).2
  have he := (eq_div_iff hk.ne').1 h
  nlinarith

end Bell.RampSums
