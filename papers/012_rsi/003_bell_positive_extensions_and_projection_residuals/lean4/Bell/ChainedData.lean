import Bell.BinaryScenarios

/-! All nine contexts of the two-party, three-setting, binary-outcome scenario.
Finite integer identities are checked by the Lean kernel. -/
open scoped BigOperators
namespace Bell.ChainedData
open Bell.BinaryScenarios
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def C (x y : ℕ) : ℤ :=
  if x = 0 then (if y = 0 then 1 else if y = 2 then -1 else 0)
  else if x = 1 then (if y = 2 then 0 else 1)
  else (if y = 0 then 0 else 1)
def A (g : Fin 64) (i : Fin 36) : ℤ :=
  if bit g (i.val/12) == i.val/2%2 && bit g (3+i.val/4%3) == i.val%2 then 1 else 0
def c (i : Fin 36) : ℤ := C (i.val/12) (i.val/4%3) * spin (i.val/2%2) * spin (i.val%2)
def K (g : Fin 64) : ℤ := ∑ i, c i * A g i
def plus (g : Fin 64) : ℤ := if K g = 4 then 1 else 0
def minus (g : Fin 64) : ℤ := if K g = -4 then 1 else 0
def y (i : Fin 36) : ℤ := (|c i| - c i)/2

/-- Every pair of three-setting deterministic response functions is enumerated. -/
theorem assignment_complete : ∀ a b : Fin 3 → Bool, ∃ g : Fin 64,
    (∀ x : Fin 3, bit g x = if a x then 1 else 0) ∧
    (∀ y : Fin 3, bit g (3+y.val) = if b y then 1 else 0) := by decide

theorem binary : ∀ g i, A g i = 0 ∨ A g i = 1 := by decide
theorem column : ∀ g, ∑ i, A g i = 9 := by decide
theorem coefficients : ∀ i, c i = -1 ∨ c i = 0 ∨ c i = 1 := by decide
theorem score_values : ∀ g, K g = -4 ∨ K g = 0 ∨ K g = 4 := by decide
theorem plus_count : ∑ g, plus g = 12 := by decide
theorem minus_count : ∑ g, minus g = 12 := by decide
theorem plus_fiber : ∀ i, ∑ g, plus g * A g i = 3 + 2*c i := by decide
theorem minus_fiber : ∀ i, ∑ g, minus g * A g i = 3 - 2*c i := by decide
theorem sum_c : ∑ i, c i = 0 := by decide
theorem sum_c_sq : ∑ i, c i * c i = 24 := by decide
theorem dual_nonnegative : ∀ i, 0 ≤ y i := by decide
theorem dual_cover : ∀ g, 1 ≤ ∑ i, y i * A g i := by decide
theorem dual_sum : ∑ i, y i = 12 := by decide
theorem dual_c : ∑ i, y i * c i = -12 := by decide

end Bell.ChainedData
