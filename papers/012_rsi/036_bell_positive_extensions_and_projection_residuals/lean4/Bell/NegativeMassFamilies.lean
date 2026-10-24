import Bell.ContextualFraction

/-! Real-parameter certificate families. All finite identities are instantiated
below for the CHSH and eight-context Mermin incidence matrices. -/
noncomputable section
open scoped BigOperators
namespace Bell.NegativeMassFamilies
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality

structure Line (I G : Type) [Fintype I] [Fintype G] where
  A : G → I → ℝ
  c : I → ℝ
  K : G → ℝ
  D : ℝ
  d : ℝ
  m : ℝ
  D_pos : 0 < D
  d_pos : 0 < d
  m_pos : 0 < m
  binary : ∀ g i, A g i = 0 ∨ A g i = 1
  column : ∀ g, ∑ i, A g i = m
  card : (Fintype.card G : ℝ) = D
  sumK : ∑ g, K g = 0
  negative_count : (∑ g, if K g = -2 then (1:ℝ) else 0) = D/2
  K_values : ∀ g, K g = -2 ∨ K g = 2
  c_values : ∀ i, c i = -1 ∨ c i = 0 ∨ c i = 1
  fiber_count : ∀ i, ∑ g, A g i = D/d
  fiber_K : ∀ i, ∑ g, K g * A g i = D/d * c i
  score_column : ∀ g, pairing c (A g) = K g
  active_column : ∀ g, pairing (fun i => |c i|) (A g) = 4
  sumc : ∑ i, c i = 0
  sumc2 : ∑ i, c i * c i = 4*d

variable {I G : Type} [Fintype I] [Fintype G]

def extension (L : Line I G) (v : ℝ) : G → ℝ := fun g => (1+v*L.K g)/L.D
def behavior (L : Line I G) (v : ℝ) : I → ℝ := fun i => (1+v*L.c i)/L.d

theorem extension_total (L : Line I G) (v : ℝ) : ∑ g, extension L v g = 1 := by
  simp only [extension, ← Finset.sum_div, Finset.sum_add_distrib, ← Finset.mul_sum]
  simp [L.sumK, L.card, ne_of_gt L.D_pos]

theorem extension_projects (L : Line I G) (v : ℝ) :
    mix L.A (extension L v) = behavior L v := by
  funext i
  simp only [mix, extension, behavior, div_mul_eq_mul_div, add_mul, one_mul,
    ← Finset.sum_div, Finset.sum_add_distrib, mul_assoc, ← Finset.mul_sum]
  rw [L.fiber_count, L.fiber_K]
  field_simp [ne_of_gt L.D_pos, ne_of_gt L.d_pos]

theorem behavior_total (L : Line I G) (v : ℝ) : ∑ i, behavior L v i = L.m := by
  rw [← extension_projects, sum_mix]
  simp_rw [L.column]
  rw [← Finset.sum_mul, extension_total, one_mul]

theorem behavior_nonnegative (L : Line I G) (v : ℝ) (hv : 0 ≤ v) (hv1 : v ≤ 1) :
    ∀ i, 0 ≤ behavior L v i := by
  intro i
  apply div_nonneg _ (le_of_lt L.d_pos)
  rcases L.c_values i with h | h | h <;> rw [h] <;> nlinarith

theorem behavior_score (L : Line I G) (v : ℝ) :
    pairing L.c (behavior L v) = 4*v := by
  simp only [pairing, behavior, ← mul_div_assoc]
  rw [← Finset.sum_div]
  have h : ∀ i, L.c i * (1+v*L.c i) = L.c i + v*(L.c i*L.c i) := by intro i; ring
  simp_rw [h, Finset.sum_add_distrib, ← Finset.mul_sum, L.sumc, L.sumc2]
  field_simp [ne_of_gt L.D_pos, ne_of_gt L.d_pos]
  ring

theorem extension_nonnegative (L : Line I G) (v : ℝ) (hv : 0 ≤ v) (hv2 : v ≤ 1/2) :
    ∀ g, 0 ≤ extension L v g := by
  intro g
  apply div_nonneg _ (le_of_lt L.D_pos)
  rcases L.K_values g with h | h <;> rw [h] <;> nlinarith

theorem extension_negative_mass (L : Line I G) (v : ℝ) (hv : 0 ≤ v) :
    negativeMass (extension L v) = max 0 (v-1/2) := by
  classical
  have pt : ∀ g, max (-(extension L v g)) 0 =
      (2 * max 0 (v-1/2) / L.D) * (if L.K g = -2 then 1 else 0) := by
    intro g
    rcases L.K_values g with hk | hk
    · simp only [extension, hk, ite_true, mul_one]
      by_cases h : v ≤ 1/2
      · rw [max_eq_left (by linarith : v-1/2 ≤ 0), max_eq_right]
        · simp
        · apply neg_nonpos.mpr; apply div_nonneg _ (le_of_lt L.D_pos); nlinarith
      · have h' : 0 ≤ v-1/2 := by linarith
        rw [max_eq_right h', max_eq_left]
        · field_simp [ne_of_gt L.D_pos, ne_of_gt L.d_pos]; ring
        · apply neg_nonneg.mpr; apply div_nonpos_of_nonpos_of_nonneg _ (le_of_lt L.D_pos); nlinarith
    · simp only [extension, hk, show ¬((2:ℝ) = -2) by norm_num, ite_false, mul_zero]
      apply max_eq_right
      apply neg_nonpos.mpr; apply div_nonneg _ (le_of_lt L.D_pos); nlinarith
  simp only [negativeMass, pt]
  rw [← Finset.mul_sum, L.negative_count]
  field_simp [ne_of_gt L.D_pos, ne_of_gt L.d_pos]

theorem negative_mass_lower (L : Line I G) (v : ℝ) (q : G → ℝ)
    (hq : mix L.A q = behavior L v) (hn : ∑ g, q g = 1) :
    max 0 (v-1/2) ≤ negativeMass q := by
  let α : I → ℝ := fun i => L.c i / 4
  have hcol : ∀ g, pairing α (L.A g) = L.K g / 4 := by
    intro g
    simp only [pairing, α, div_mul_eq_mul_div, ← Finset.sum_div]
    rw [← L.score_column g]
    rfl
  have hd : ∀ g, -1 ≤ pairing α (L.A g) + (-1/2) ∧
      pairing α (L.A g) + (-1/2) ≤ 0 := by
    intro g; rw [hcol]
    rcases L.K_values g with h | h <;> rw [h] <;> norm_num
  have h := negative_mass_weak_duality L.A (behavior L v) α q (-1/2) hq hn hd
  have he : pairing α (behavior L v) = v := by
    simp only [pairing, α, div_mul_eq_mul_div, ← Finset.sum_div]
    change pairing L.c (behavior L v) / 4 = v
    rw [behavior_score]; ring
  rw [he] at h
  apply max_le
  · exact Finset.sum_nonneg (fun g _ => le_max_right _ _)
  · linarith

/-- An explicit real signed extension attains the minimum against every real competitor. -/
theorem negative_mass_exact (L : Line I G) (v : ℝ) (hv : 0 ≤ v) :
    (∑ g, extension L v g = 1) ∧
    mix L.A (extension L v) = behavior L v ∧
    negativeMass (extension L v) = max 0 (v-1/2) ∧
    ∀ q, mix L.A q = behavior L v → (∑ g, q g = 1) →
      max 0 (v-1/2) ≤ negativeMass q :=
  ⟨extension_total L v, extension_projects L v, extension_negative_mass L v hv,
    fun q hq hn => negative_mass_lower L v q hq hn⟩

def cfWitness (L : Line I G) : I → ℝ := fun i => (|L.c i| - L.c i)/2

theorem cf_witness_feasible (L : Line I G) :
    (∀ i, 0 ≤ cfWitness L i) ∧ ∀ g, 1 ≤ pairing (cfWitness L) (L.A g) := by
  constructor
  · intro i; exact div_nonneg (sub_nonneg.mpr (le_abs_self _)) (by norm_num)
  · intro g
    have he : pairing (cfWitness L) (L.A g) = (4-L.K g)/2 := by
      simp only [pairing, cfWitness, div_mul_eq_mul_div, sub_mul, ← Finset.sum_div,
        Finset.sum_sub_distrib]
      rw [show (∑ i, |L.c i| * L.A g i) = 4 from L.active_column g,
        show (∑ i, L.c i * L.A g i) = L.K g from L.score_column g]
    rw [he]
    rcases L.K_values g with h | h <;> rw [h] <;> norm_num

theorem cf_witness_value (L : Line I G) (v : ℝ) :
    pairing (cfWitness L) (behavior L v) = 2-2*v := by
  have pt : ∀ i, cfWitness L i * behavior L v i =
      ((L.c i*L.c i - L.c i) + v*(L.c i-L.c i*L.c i))/(2*L.d) := by
    intro i
    dsimp [cfWitness, behavior]
    rcases L.c_values i with h | h | h <;> rw [h] <;>
      norm_num
    ring
  unfold pairing
  simp_rw [pt]
  rw [← Finset.sum_div, Finset.sum_add_distrib, Finset.sum_sub_distrib,
    ← Finset.mul_sum, Finset.sum_sub_distrib, L.sumc, L.sumc2]
  field_simp [ne_of_gt L.D_pos, ne_of_gt L.d_pos]
  ring

theorem contextual_fraction_exact (L : Line I G) (v : ℝ) (hv : 0 ≤ v) (hv1 : v ≤ 1) :
    fraction L.A (behavior L v) = max 0 (2*v-1) := by
  have hp := behavior_nonnegative L v hv hv1
  have hb := weights_bounded L.A (behavior L v) L.m L.m_pos L.column (behavior_total L v)
  have hlo := lower_of_dual L.A (behavior L v) (cfWitness L) hp
    (cf_witness_feasible L).1 (cf_witness_feasible L).2
  rw [cf_witness_value] at hlo
  have hzero := fraction_nonnegative L.A (behavior L v) L.m L.m_pos L.column
    (behavior_total L v) hp
  apply le_antisymm
  · by_cases h : v ≤ 1/2
    · have hpack : Packing L.A (behavior L v) (extension L v) :=
        ⟨extension_nonnegative L v hv h, fun i => le_of_eq (congrFun (extension_projects L v) i)⟩
      have hupper := upper_of_packing L.A (behavior L v) hb hpack
      rw [extension_total] at hupper
      rw [max_eq_left (by linarith : 2*v-1 ≤ 0)]
      linarith
    · let γ : G → ℝ := fun g => (2-2*v) * extension L (1/2) g
      have hγ : Packing L.A (behavior L v) γ := by
        constructor
        · intro g
          exact mul_nonneg (by linarith) (extension_nonnegative L (1/2) (by norm_num) (by norm_num) g)
        · intro i
          have he : mix L.A γ i = (2-2*v) * behavior L (1/2) i := by
            simp only [mix, γ, mul_assoc, ← Finset.mul_sum]
            rw [show (∑ g, extension L (1/2) g * L.A g i) = behavior L (1/2) i from
              congrFun (extension_projects L (1/2)) i]
          rw [he]
          have hr := behavior_nonnegative L 1 (by norm_num) (by norm_num) i
          have hid : behavior L v i - (2-2*v) * behavior L (1/2) i =
              (2*v-1) * behavior L 1 i := by
            dsimp [behavior]; field_simp [ne_of_gt L.D_pos, ne_of_gt L.d_pos]; ring
          have := mul_nonneg (by linarith : 0 ≤ 2*v-1) hr
          linarith
      have hsum : ∑ g, γ g = 2-2*v := by
        dsimp [γ]; rw [← Finset.mul_sum, extension_total, mul_one]
      have hu := upper_of_packing L.A (behavior L v) hb hγ
      rw [hsum] at hu
      rw [max_eq_right (by linarith : 0 ≤ 2*v-1)]
      linarith
  · exact max_le hzero (by linarith)

end Bell.NegativeMassFamilies

