import Bell.Extension

/-! CHSH local bounds and uniform-setting total-variation witnesses. -/
noncomputable section
open scoped BigOperators
namespace Bell.CHSH
attribute [local instance] Classical.propDecidable
local instance (priority := high) : DecidableEq Bool := Classical.decEq Bool

def sign : Bool → ℝ | false => -1 | true => 1
abbrev Table := Behavior Bool Bool Bool Bool
abbrev Omega := Assignment Bool Bool Bool Bool
abbrev Row := Bool × Bool × Bool × Bool
def coefficient (x y a b : Bool) : ℝ :=
  (if x && y then -1 else 1) * sign a * sign b
def score (p : Table) : ℝ :=
  ∑ r : Row, coefficient r.1 r.2.1 r.2.2.1 r.2.2.2 * p r.1 r.2.1 r.2.2.1 r.2.2.2
def K (ω : Omega) : ℝ :=
  sign (ω.1 false) * (sign (ω.2 false) + sign (ω.2 true)) +
  sign (ω.1 true) * (sign (ω.2 false) - sign (ω.2 true))
def tv (p q : Table) : ℝ :=
  (∑ r : Row, |p r.1 r.2.1 r.2.2.1 r.2.2.2 - q r.1 r.2.1 r.2.2.1 r.2.2.2|) / 8

theorem coefficient_abs (x y a b : Bool) : |coefficient x y a b| = 1 := by
  cases x <;> cases y <;> cases a <;> cases b <;> norm_num [coefficient, sign]

theorem deterministic_values (ω : Omega) : K ω = -2 ∨ K ω = 2 := by
  unfold K
  cases ω.1 false <;> cases ω.1 true <;> cases ω.2 false <;> cases ω.2 true <;> norm_num [sign]

theorem deterministic_bound (ω : Omega) : |K ω| = 2 := by
  obtain h | h := deterministic_values ω <;> rw [h] <;> norm_num

theorem marginal_score (q : Omega → ℝ) : score (marginal q) = ∑ ω, q ω * K ω := by
  unfold score marginal
  simp_rw [Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro ω _
  simp only [Fintype.sum_prod_type]
  simp_rw [mul_ite, mul_zero]
  simp only [Fintype.sum_bool]
  unfold coefficient K
  cases ω.1 false <;> cases ω.1 true <;> cases ω.2 false <;> cases ω.2 true <;>
    norm_num [sign] <;> ring

theorem mixture_bound (q : Omega → ℝ) (hq : Probability q) :
    |∑ ω, q ω * K ω| ≤ 2 := by
  calc
    _ ≤ ∑ ω, |q ω * K ω| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ ω, q ω * 2 := by simp_rw [abs_mul, abs_of_nonneg (hq.nonneg _), deterministic_bound]
    _ = 2 := by rw [← Finset.sum_mul, hq.total, one_mul]

theorem positive_extension_chsh (p : Table) (hp : PositiveExtension p) : |score p| ≤ 2 := by
  obtain ⟨q, hq, rfl⟩ := hp
  rw [marginal_score]
  exact mixture_bound q hq

theorem stochastic_local_chsh (p : Table) (m : LocalModel p) : |score p| ≤ 2 :=
  positive_extension_chsh p (local_positive_extension m)

theorem violation_no_extension (p : Table) (h : 2 < |score p|) : ¬ PositiveExtension p := by
  intro hp
  exact (not_lt_of_ge (positive_extension_chsh p hp)) h

def negativeMass (q : Omega → ℝ) : ℝ := ∑ ω, max (-q ω) 0

theorem signed_total_variation (q : Omega → ℝ) (hq : ∑ ω, q ω = 1) :
    ∑ ω, |q ω| = 1 + 2 * negativeMass q := by
  have h (x : ℝ) : |x| = x + 2 * max (-x) 0 := by
    by_cases hx : 0 ≤ x
    · rw [abs_of_nonneg hx, max_eq_right (by linarith)]
      ring
    · have hn : x ≤ 0 := le_of_not_ge hx
      rw [abs_of_nonpos hn, max_eq_left (by linarith)]
      ring
  simp_rw [h]
  rw [Finset.sum_add_distrib, hq, ← Finset.mul_sum]
  rfl

theorem signed_chsh_bound (q : Omega → ℝ) (hq : ∑ ω, q ω = 1) :
    |score (marginal q)| ≤ 2 * (1 + 2 * negativeMass q) := by
  rw [marginal_score]
  calc
    _ ≤ ∑ ω, |q ω * K ω| := Finset.abs_sum_le_sum_abs _ _
    _ = _ := by
      simp_rw [abs_mul, deterministic_bound]
      rw [← Finset.sum_mul, signed_total_variation q hq]
      ring

theorem signed_negativity_lower_bound (q : Omega → ℝ) (hq : ∑ ω, q ω = 1) :
    max 0 (|score (marginal q)| - 2) / 4 ≤ negativeMass q := by
  have hs := signed_chsh_bound q hq
  have hn : 0 ≤ negativeMass q := Finset.sum_nonneg (fun _ _ => le_max_right _ _)
  apply (div_le_iff₀ (by norm_num : (0:ℝ) < 4)).2
  apply max_le <;> linarith

theorem tv_nonnegative (p q : Table) : 0 ≤ tv p q := by
  apply div_nonneg _ (by norm_num)
  exact Finset.sum_nonneg (fun _ _ => abs_nonneg _)

theorem score_lipschitz (p q : Table) : |score p - score q| ≤ 8 * tv p q := by
  have he : score p - score q = ∑ r : Row,
      coefficient r.1 r.2.1 r.2.2.1 r.2.2.2 *
        (p r.1 r.2.1 r.2.2.1 r.2.2.2 - q r.1 r.2.1 r.2.2.1 r.2.2.2) := by
    simp [score, mul_sub, Finset.sum_sub_distrib]
  rw [he]
  calc
    _ ≤ ∑ r : Row, |coefficient r.1 r.2.1 r.2.2.1 r.2.2.2 *
      (p r.1 r.2.1 r.2.2.1 r.2.2.2 - q r.1 r.2.1 r.2.2.1 r.2.2.2)| :=
        Finset.abs_sum_le_sum_abs _ _
    _ = _ := by simp_rw [abs_mul, coefficient_abs, one_mul]; unfold tv; ring

theorem chsh_repair_lower_bound (p l : Table) (hl : PositiveExtension l) :
    max 0 (|score p| - 2) / 8 ≤ tv p l := by
  have hd := score_lipschitz p l
  have hlb := positive_extension_chsh l hl
  have ht := abs_add_le (score p - score l) (score l)
  have he : score p - score l + score l = score p := by ring
  rw [he] at ht
  have hn := tv_nonnegative p l
  apply (div_le_iff₀ (by norm_num : (0:ℝ) < 8)).2
  apply max_le <;> linarith

theorem uncertain_repair_lower_bound (observed actual l : Table) (ε : ℝ)
    (hε : tv observed actual ≤ ε) (hl : PositiveExtension l) :
    max 0 (|score observed| - 2 - 8 * ε) / 8 ≤ tv actual l := by
  have ho := score_lipschitz observed actual
  have ha := score_lipschitz actual l
  have hb := positive_extension_chsh l hl
  have ht := abs_add_le (score observed - score actual) (score actual)
  have ht' := abs_add_le (score actual - score l) (score l)
  ring_nf at ht ht'
  have hn := tv_nonnegative actual l
  apply (div_le_iff₀ (by norm_num : (0:ℝ) < 8)).2
  apply max_le <;> linarith

theorem uncertainty_excludes_extension (observed actual : Table) (ε : ℝ)
    (hε : tv observed actual ≤ ε) (hv : 2 + 8 * ε < |score observed|) :
    ¬ PositiveExtension actual := by
  intro ha
  have h := uncertain_repair_lower_bound observed actual actual ε hε ha
  have hz : tv actual actual = 0 := by simp [tv]
  rw [hz] at h
  have hm := le_max_right 0 (|score observed| - 2 - 8 * ε)
  linarith

def isotropic (v : ℝ) : Table := fun x y a b => (1 + v * coefficient x y a b) / 4

theorem isotropic_score (v : ℝ) : score (isotropic v) = 4 * v := by
  norm_num [score, isotropic, Fintype.sum_prod_type, Fintype.sum_bool, coefficient, sign]
  ring

theorem isotropic_nonlocal (v : ℝ) (hv : 1 / 2 < v) : ¬ PositiveExtension (isotropic v) := by
  apply violation_no_extension
  rw [isotropic_score]
  have h := le_abs_self (4 * v)
  linarith

end Bell.CHSH
