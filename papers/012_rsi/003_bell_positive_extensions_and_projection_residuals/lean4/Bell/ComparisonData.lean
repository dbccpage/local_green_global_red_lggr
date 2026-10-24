import Bell.BinaryScenarios

/-! Integer certificates generated from the independently checked LP fixture.
Assignment order is converted from lexicographic tuples to little-endian bits.
All finite assertions use kernel evaluation, not native_decide. -/
open scoped BigOperators
namespace Bell.ComparisonData
open Bell.BinaryScenarios
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def pI : Fin 64 → ℤ := ![35, 93, 93, 35, 93, 35, 35, 349, 120, 8, 8, 120, 8, 120, 120, 264, 120, 8, 8, 120, 8, 120, 120, 264, 125, 3, 3, 125, 3, 125, 125, 259, 120, 8, 8, 120, 8, 120, 120, 264, 125, 3, 3, 125, 3, 125, 125, 259, 125, 3, 3, 125, 3, 125, 125, 259, 120, 8, 8, 120, 8, 120, 120, 264]

def gammaI : Fin 64 → ℤ := ![35, 3, 0, 0, 3, 0, 3, 0, 0, 3, 0, 0, 0, 0, 0, 35, 3, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 85, 0, 3, 0, 0, 3, 0, 0, 0, 0, 0, 0, 8, 0, 0, 8, 0, 0, 0, 0, 35, 0, 0, 0, 85, 0, 0, 8, 0, 35, 85, 0, 94]

def yI : Fin 64 → ℤ := ![1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def qI : Fin 64 → ℤ := ![109, 4, 0, 0, 4, 0, 4, 0, 0, 4, -1, 0, 0, 0, 0, 0, 4, 0, 4, 0, 0, -1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 121, 0, 4, -1, 0, 4, 0, 0, 0, -72, 71, 0, 10, 0, 0, 81, 35, 0, 0, 0, 0, 0, 0, 0, 121, 0, 0, 81, 35, 35, 86, 0, 22]

def zI : Fin 64 → ℤ := ![-2, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0]

theorem p_nonnegative : ∀ i, 0 ≤ pI i := by decide

theorem p_total : (∑ i, pI i) = 6144 := by decide

theorem gamma_nonnegative : ∀ g, 0 ≤ gammaI g := by decide

theorem gamma_feasible : ∀ i, (∑ g, gammaI g * merminAI g i) ≤ pI i := by decide

theorem gamma_total : (∑ g, gammaI g) = 540 := by decide

theorem y_nonnegative : ∀ i, 0 ≤ yI i := by decide

theorem y_feasible : ∀ g, 1 ≤ ∑ i, yI i * merminAI g i := by decide

theorem cf_gap : (∑ i, yI i * pI i) = 540 := by decide

theorem q_total : (∑ g, qI g) = 768 := by decide

theorem q_projects : ∀ i, (∑ g, qI g * merminAI g i) = pI i := by decide

theorem q_mass : (∑ g, max (-qI g) 0) = 75 := by decide

theorem z_feasible : ∀ g, -2 ≤ (∑ i, zI i * merminAI g i) ∧ (∑ i, zI i * merminAI g i) ≤ 0 := by decide

theorem n_gap : (∑ i, zI i * pI i) = 150 := by decide

end Bell.ComparisonData
