import Bell.FiveComparison
import Bell.PlanarQuantum

/-! A complete 25-context quantum counterexample to the factor-four bound. -/
noncomputable section
namespace Bell.FiveQuantum
open Bell.PlanarQuantum
set_option maxHeartbeats 2000000
def az (s : Fin 5) : ℝ := FiveData.az s/185
def ax (s : Fin 5) : ℝ := FiveData.ax s/185
def bz (s : Fin 5) : ℝ := FiveData.bz s/185
def bx (s : Fin 5) : ℝ := FiveData.bx s/185
def table (i : Fin 100) : ℝ := born
  (az ⟨i.val/20,by omega⟩) (ax ⟨i.val/20,by omega⟩)
  (bz ⟨i.val/4%5,by omega⟩) (bx ⟨i.val/4%5,by omega⟩)
  (i.val/2%2 == 1) (i.val%2 == 1)

theorem alice_unit (s : Fin 5) : az s^2+ax s^2=1 := by
  have h : (FiveData.az s:ℝ)^2+(FiveData.ax s:ℝ)^2=34225 := by
    exact_mod_cast FiveData.directions.1 s
  dsimp [az,ax]; nlinarith
theorem bob_unit (s : Fin 5) : bz s^2+bx s^2=1 := by
  have h : (FiveData.bz s:ℝ)^2+(FiveData.bx s:ℝ)^2=34225 := by
    exact_mod_cast FiveData.directions.2 s
  dsimp [bz,bx]; nlinarith
theorem alice_povm (s : Fin 5) : Bell.QuantumState.BinaryPOVM (effect (az s) (ax s)) :=
  local_povm _ _ (alice_unit s)
theorem bob_povm (s : Fin 5) : Bell.QuantumState.BinaryPOVM (effect (bz s) (bx s)) :=
  local_povm _ _ (bob_unit s)
theorem born_table : table = FiveComparison.point := by
  funext i
  unfold table
  rw [born_formula]
  fin_cases i <;> norm_num [az,ax,bz,bx,FiveComparison.point,FiveData.pn,
    FiveData.az,FiveData.ax,FiveData.bz,FiveData.bx,Bell.CHSH.sign]
theorem quantum_realization :
    ‖Bell.QuantumExample.state Bell.QuantumExample.t‖ = 1 ∧
    (∀ s, Bell.QuantumState.BinaryPOVM (effect (az s) (ax s))) ∧
    (∀ s, Bell.QuantumState.BinaryPOVM (effect (bz s) (bx s))) ∧
    table = FiveComparison.point :=
  ⟨Bell.QuantumExample.bell_state_unit,alice_povm,bob_povm,born_table⟩
theorem quantum_counterexample :
    Bell.ContextualFraction.fraction FiveComparison.A table = 698/925 ∧
    Bell.SignedDuality.negativeMass FiveComparison.extension = 167/925 ∧
    4*Bell.SignedDuality.negativeMass FiveComparison.extension <
      Bell.ContextualFraction.fraction FiveComparison.A table := by
  rw [born_table]
  exact ⟨FiveComparison.contextual_fraction,FiveComparison.extension_mass,
    FiveComparison.exact_counterexample.2.2.1⟩
end Bell.FiveQuantum
