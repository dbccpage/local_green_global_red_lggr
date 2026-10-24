import Bell.Extension
import Mathlib.Algebra.Order.Archimedean.Real.Basic

/-! Finite scalar observer fibers: sufficiency, attained minimax, and recursion. -/
noncomputable section
open scoped BigOperators
namespace Bell.Observer
variable {H Y : Type} [Fintype H] [Nonempty H]

def fiber (O : H → Y) (y : Y) : Finset H := by
  classical
  exact Finset.univ.filter (fun h => O h = y)

omit [Nonempty H] in
theorem mem_fiber (O : H → Y) (y : Y) (h : H) : h ∈ fiber O y ↔ O h = y := by
  classical
  simp [fiber]

omit [Nonempty H] in
theorem fiber_nonempty (O : H → Y) (h : H) : (fiber O (O h)).Nonempty :=
  ⟨h, (mem_fiber O (O h) h).2 rfl⟩

def lo (O : H → Y) (f : H → ℝ) (y : Y) : ℝ := by
  classical
  exact if hy : (fiber O y).Nonempty then (fiber O y).inf' hy f else 0

def hi (O : H → Y) (f : H → ℝ) (y : Y) : ℝ := by
  classical
  exact if hy : (fiber O y).Nonempty then (fiber O y).sup' hy f else 0

def width (O : H → Y) (f : H → ℝ) (y : Y) : ℝ := hi O f y - lo O f y
def midpoint (O : H → Y) (f : H → ℝ) (y : Y) : ℝ := (lo O f y + hi O f y) / 2
def risk (O : H → Y) (f : H → ℝ) (g : Y → ℝ) : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty (fun h => |f h - g (O h)|)
def maxWidth (O : H → Y) (f : H → ℝ) : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty (fun h => width O f (O h))

omit [Nonempty H] in
theorem fiber_bounds (O : H → Y) (f : H → ℝ) (h : H) :
    lo O f (O h) ≤ f h ∧ f h ≤ hi O f (O h) := by
  classical
  simp only [lo, hi, dite_eq_left (fiber_nonempty O h)]
  exact ⟨Finset.inf'_le _ ((mem_fiber O (O h) h).2 rfl),
    Finset.le_sup' _ ((mem_fiber O (O h) h).2 rfl)⟩

omit [Nonempty H] in
theorem fiber_extrema (O : H → Y) (f : H → ℝ) (h : H) :
    ∃ a b, O a = O h ∧ O b = O h ∧ lo O f (O h) = f a ∧ hi O f (O h) = f b := by
  classical
  obtain ⟨a, ha, ea⟩ := Finset.exists_mem_eq_inf' (fiber_nonempty O h) f
  obtain ⟨b, hb, eb⟩ := Finset.exists_mem_eq_sup' (fiber_nonempty O h) f
  exact ⟨a, b, (mem_fiber _ _ _).1 ha, (mem_fiber _ _ _).1 hb,
    by simpa [lo, fiber_nonempty] using ea, by simpa [hi, fiber_nonempty] using eb⟩

theorem error_le_risk (O : H → Y) (f : H → ℝ) (g : Y → ℝ) (h : H) :
    |f h - g (O h)| ≤ risk O f g := Finset.le_sup' (fun h => |f h - g (O h)|) (Finset.mem_univ h)

theorem pair_error_lower_bound (a b z : ℝ) :
    |a - b| ≤ |a - z| + |b - z| := by
  calc
    |a - b| = |(a - z) + (z - b)| := by congr 1; ring
    _ ≤ |a - z| + |z - b| := abs_add_le _ _
    _ = _ := by rw [abs_sub_comm z b]

theorem same_fiber_error_limit (O : H → Y) (f : H → ℝ) (g : Y → ℝ)
    (a b : H) (hab : O a = O b) : |f a - f b| / 2 ≤ risk O f g := by
  have ha := error_le_risk O f g a
  have hb := error_le_risk O f g b
  have hp := pair_error_lower_bound (f a) (f b) (g (O a))
  rw [← hab] at hb
  linarith

theorem minimax_lower (O : H → Y) (f : H → ℝ) (g : Y → ℝ) :
    maxWidth O f / 2 ≤ risk O f g := by
  have h : maxWidth O f ≤ 2 * risk O f g := by
    apply Finset.sup'_le
    intro h _
    obtain ⟨a, b, ha, hb, ea, eb⟩ := fiber_extrema O f h
    have hp := same_fiber_error_limit O f g b a (hb.trans ha.symm)
    have he : width O f (O h) = f b - f a := by rw [width, ea, eb]
    rw [he]
    have habs := le_abs_self (f b - f a)
    linarith
  linarith

omit [Nonempty H] in
theorem midpoint_error (O : H → Y) (f : H → ℝ) (h : H) :
    |f h - midpoint O f (O h)| ≤ width O f (O h) / 2 := by
  obtain ⟨ha, hb⟩ := fiber_bounds O f h
  unfold midpoint width
  apply abs_le.mpr
  constructor <;> linarith

theorem midpoint_optimal (O : H → Y) (f : H → ℝ) :
    risk O f (midpoint O f) = maxWidth O f / 2 := by
  apply le_antisymm
  · apply Finset.sup'_le
    intro h _
    have he := midpoint_error O f h
    have hw : width O f (O h) ≤ maxWidth O f := Finset.le_sup' (fun h => width O f (O h)) (Finset.mem_univ h)
    linarith
  · exact minimax_lower O f _

theorem scalar_minimax (O : H → Y) (f : H → ℝ) :
    sInf (Set.range (risk O f)) = maxWidth O f / 2 := by
  apply csInf_eq_of_forall_ge_of_forall_gt_exists_lt
  · exact ⟨_, ⟨midpoint O f, rfl⟩⟩
  · rintro a ⟨g, rfl⟩
    exact minimax_lower O f g
  · intro w hw
    exact ⟨_, ⟨midpoint O f, rfl⟩, by rw [midpoint_optimal]; exact hw⟩

theorem factors_iff_constant_on_fibers {H Y : Type} (O : H → Y) (f : H → ℝ) :
    (∃ g : Y → ℝ, ∀ h, f h = g (O h)) ↔
      (∀ a b, O a = O b → f a = f b) := by
  classical
  constructor
  · rintro ⟨g, hg⟩ a b hab
    rw [hg, hg, hab]
  · intro hf
    let g : Y → ℝ := fun y => if hy : ∃ h, O h = y then f hy.choose else 0
    refine ⟨g, ?_⟩
    intro h
    have hh : ∃ a, O a = O h := ⟨h, rfl⟩
    simp only [g, dite_eq_left hh]
    exact hf h hh.choose hh.choose_spec.symm

theorem refinement_cannot_increase_minimax {Z : Type} (O : H → Y) (O' : H → Z)
    (decode : Z → Y) (hrefine : ∀ h, decode (O' h) = O h) (f : H → ℝ) :
    maxWidth O' f / 2 ≤ maxWidth O f / 2 := by
  have hl := minimax_lower O' f (fun z => midpoint O f (decode z))
  have he : risk O' f (fun z => midpoint O f (decode z)) = risk O f (midpoint O f) := by
    simp only [risk, hrefine]
  rw [he, midpoint_optimal] at hl
  exact hl

def iterateReport {S : Type} (O : H → Y) (initial : S)
    (update : ℕ → Y → S → S) : ℕ → H → S
  | 0, _ => initial
  | n + 1, h => update n (O h) (iterateReport O initial update n h)

omit [Fintype H] [Nonempty H] in
theorem recursion_preserves_fibers {S : Type} (O : H → Y) (initial : S)
    (update : ℕ → Y → S → S) (a b : H) (hab : O a = O b) (n : ℕ) :
    iterateReport O initial update n a = iterateReport O initial update n b := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [iterateReport, hab, ih]

theorem recursion_error_floor {S : Type} (O : H → Y) (f : H → ℝ) (initial : S)
    (update : ℕ → Y → S → S) (readout : S → ℝ) (n : ℕ) :
    maxWidth O f / 2 ≤ Finset.univ.sup' Finset.univ_nonempty
      (fun h => |f h - readout (iterateReport O initial update n h)|) := by
  have hf : ∀ a b, O a = O b →
      readout (iterateReport O initial update n a) = readout (iterateReport O initial update n b) := by
    intro a b hab
    rw [recursion_preserves_fibers O initial update a b hab n]
  obtain ⟨g, hg⟩ := (factors_iff_constant_on_fibers O _).2 hf
  simp_rw [hg]
  exact minimax_lower O f g

def expectedError {Z : Type} [Fintype Z] (O : H → Y) (f : H → ℝ)
    (w : Y → Z → ℝ) (g : Z → Y → ℝ) (h : H) : ℝ :=
  ∑ z, w (O h) z * |f h - g z (O h)|

theorem randomized_error_floor {Z : Type} [Fintype Z] (O : H → Y) (f : H → ℝ)
    (w : Y → Z → ℝ) (hw : ∀ y, Probability (w y)) (g : Z → Y → ℝ) :
    maxWidth O f / 2 ≤ Finset.univ.sup' Finset.univ_nonempty (expectedError O f w g) := by
  let r := Finset.univ.sup' Finset.univ_nonempty (expectedError O f w g)
  have hl : maxWidth O f ≤ 2 * r := by
    apply Finset.sup'_le
    intro h _
    obtain ⟨a, b, ha, hb, ea, eb⟩ := fiber_extrema O f h
    have hp : f b - f a ≤ expectedError O f w g a + expectedError O f w g b := by
      calc
        f b - f a = ∑ z, w (O h) z * (f b - f a) := by rw [← Finset.sum_mul, (hw (O h)).total, one_mul]
        _ ≤ ∑ z, w (O h) z * (|f a - g z (O h)| + |f b - g z (O h)|) := by
          apply Finset.sum_le_sum
          intro z _
          apply mul_le_mul_of_nonneg_left _ ((hw (O h)).nonneg z)
          have ht := pair_error_lower_bound (f a) (f b) (g z (O h))
          have ht' := le_abs_self (f b - f a)
          rw [abs_sub_comm (f a) (f b)] at ht
          linarith
        _ = _ := by simp [expectedError, ha, hb, mul_add, Finset.sum_add_distrib]
    have hla : expectedError O f w g a ≤ r := Finset.le_sup' _ (Finset.mem_univ a)
    have hlb : expectedError O f w g b ≤ r := Finset.le_sup' _ (Finset.mem_univ b)
    unfold width
    rw [ea, eb]
    linarith
  change maxWidth O f / 2 ≤ r
  linarith

end Bell.Observer
