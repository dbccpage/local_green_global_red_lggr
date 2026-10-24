import ErrorBudget

namespace EpistemicNoGo.MindContracts

/-- The greatest sound report-only acceptance set is the set of wholly correct fibers. -/
def wholeFiber {X Y : Type*} (q : X → Y) (correct : X → Prop) (y : Y) : Prop :=
  ∀ x, q x = y → correct x

theorem whole_fiber_sound {X Y : Type*} (q : X → Y) (correct : X → Prop) (x : X)
    (h : wholeFiber q correct (q x)) : correct x := h x rfl

theorem whole_fiber_maximal {X Y : Type*} (q : X → Y) (correct : X → Prop)
    (accept : Y → Prop) (sound : ∀ x, accept (q x) → correct x) :
    ∀ y, accept y → wholeFiber q correct y := by
  intro y hy x hx
  apply sound x
  simpa [hx] using hy

/-- A score-error certificate yields a decision guarantee without full state recovery. -/
theorem score_regret {A : Type*} (value score : A → ℝ) (chosen : A) (b : ℝ)
    (error : ∀ a, |value a - score a| ≤ b)
    (best : ∀ a, score a ≤ score chosen) :
    ∀ a, value a - value chosen ≤ 2 * b := by
  intro a
  have ha := (abs_le.mp (error a)).2
  have hc := (abs_le.mp (error chosen)).1
  linarith [best a]

theorem score_gap_unique {A : Type*} (value score : A → ℝ) (chosen : A) (b : ℝ)
    (error : ∀ a, |value a - score a| ≤ b)
    (gap : ∀ a, a ≠ chosen → 2 * b < score chosen - score a) :
    ∀ a, a ≠ chosen → value a < value chosen := by
  intro a hne
  have ha := (abs_le.mp (error a)).2
  have hc := (abs_le.mp (error chosen)).1
  linarith [gap a hne]

/-- A large valid upper bound does not imply a large actual error. -/
theorem upper_bound_does_not_force_failure (tolerance : ℝ) (h : 0 ≤ tolerance) :
    ∃ actual bound : ℝ, 0 ≤ actual ∧ actual ≤ bound ∧ tolerance < bound ∧ actual ≤ tolerance := by
  exact ⟨0, tolerance + 1, le_rfl, by linarith, by linarith, h⟩

end EpistemicNoGo.MindContracts
