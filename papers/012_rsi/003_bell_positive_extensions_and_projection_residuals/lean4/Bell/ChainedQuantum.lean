import Bell.ChainedComparison
import Bell.QuantumExample
import Bell.QuantumState

/-! A two-qubit realization of the full 3-by-3 chained behavior, with a strict
CF > 2N separation. All states, effects and Born probabilities are explicit. -/
noncomputable section
open scoped BigOperators ComplexConjugate ComplexOrder
namespace Bell.ChainedQuantum
open Bell.QuantumExample
set_option maxHeartbeats 4000000

def direction (u : ℝ) (side : Bool) (setting : Fin 3) : Matrix Bool Bool ℂ :=
  if side then
    if setting = 0 then (u:ℂ) • Z + (1/2:ℂ) • X
    else if setting = 1 then X else (-u:ℂ) • Z + (1/2:ℂ) • X
  else
    if setting = 0 then Z
    else if setting = 1 then (1/2:ℂ) • Z + (u:ℂ) • X
    else (-1/2:ℂ) • Z + (u:ℂ) • X

def effect (u : ℝ) (side : Bool) (setting : Fin 3) (a : Bool) : Matrix Bool Bool ℂ :=
  (1/2:ℂ) • (1 - (Bell.CHSH.sign a:ℂ) • direction u side setting)

def measurement (u : ℝ) (i : Fin 36) : Operator :=
  Matrix.kronecker (effect u false ⟨i.val/12, by omega⟩ (i.val/2%2 == 1))
    (effect u true ⟨i.val/4%3, by omega⟩ (i.val%2 == 1))
def born (u : ℝ) (i : Fin 36) : ℝ := mean t (measurement u i)

theorem direction_hermitian (u : ℝ) (side : Bool) (s : Fin 3) :
    (direction u side s).conjTranspose = direction u side s := by
  ext r k
  cases side <;> fin_cases s <;> cases r <;> cases k <;>
    simp [direction, Z, X, Matrix.conjTranspose_apply]

theorem direction_square (u : ℝ) (hu : u^2=3/4) (side : Bool) (s : Fin 3) :
    direction u side s * direction u side s = 1 := by
  ext r k
  cases side <;> fin_cases s <;> cases r <;> cases k <;>
    norm_num [direction, Z, X, Matrix.mul_apply, Matrix.one_apply,
      Complex.ext_iff, Complex.mul_re, Complex.mul_im] <;> nlinarith [hu]

theorem effect_hermitian (u : ℝ) (side : Bool) (s : Fin 3) (a : Bool) :
    (effect u side s a).conjTranspose = effect u side s a := by
  ext r k
  cases side <;> fin_cases s <;> cases a <;> cases r <;> cases k <;>
    simp [effect, direction, Z, X, Bell.CHSH.sign, Matrix.conjTranspose_apply]; ring

theorem effect_projector (u : ℝ) (hu : u^2=3/4) (side : Bool) (s : Fin 3) (a : Bool) :
    effect u side s a * effect u side s a = effect u side s a := by
  ext r k
  cases side <;> fin_cases s <;> cases a <;> cases r <;> cases k <;>
    norm_num [effect, direction, Z, X, Bell.CHSH.sign, Matrix.mul_apply,
      Matrix.one_apply, Complex.ext_iff, Complex.mul_re, Complex.mul_im] <;> nlinarith

theorem effects_total (u : ℝ) (side : Bool) (s : Fin 3) :
    effect u side s false + effect u side s true = 1 := by
  ext r k
  norm_num [effect, Matrix.add_apply, Matrix.smul_apply, smul_eq_mul,
    Matrix.sub_apply, Bell.CHSH.sign]
  ring

theorem local_povm (u : ℝ) (hu : u^2=3/4) (side : Bool) (s : Fin 3) :
    Bell.QuantumState.BinaryPOVM (effect u side s) := by
  refine ⟨?_, effects_total u side s⟩
  intro a
  have h := Matrix.posSemidef_conjTranspose_mul_self (effect u side s a)
  rw [effect_hermitian, effect_projector u hu] at h
  exact h

theorem born_formula (u : ℝ) :
    born u = ChainedComparison.point u := by
  have ht : t^2=1/2 := by nlinarith [t_normalization]
  funext i
  unfold born
  rw [mean_four_entries,ht]
  fin_cases i <;>
    norm_num [measurement, effect, direction, Z, X, Bell.CHSH.sign,
      Matrix.kronecker_apply, Matrix.one_apply, ChainedComparison.point,
      ChainedComparison.c, ChainedData.c, ChainedData.C, Bell.BinaryScenarios.spin,
      Complex.mul_re, Complex.mul_im] <;> nlinarith

def visibility : ℝ := Real.sqrt 3/2

theorem visibility_square : visibility^2=3/4 := by
  have h := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 3)
  dsimp [visibility]
  nlinarith

theorem visibility_range : 2/3 < visibility ∧ visibility ≤ 1 := by
  have h := visibility_square
  have hn : 0 ≤ visibility := by unfold visibility; positivity
  constructor <;> nlinarith

theorem quantum_realization :
    ‖state t‖ = 1 ∧
    (∀ side s, Bell.QuantumState.BinaryPOVM (effect visibility side s)) ∧
    born visibility = ChainedComparison.point visibility :=
  ⟨bell_state_unit, local_povm visibility visibility_square, born_formula visibility⟩

/-- An actual tensor-product Born behavior with a minimum over all real signed extensions. -/
theorem quantum_counterexample :
    Bell.ContextualFraction.fraction ChainedComparison.A (born visibility) =
      (3*Real.sqrt 3-4)/2 ∧
    Bell.SignedDuality.negativeMass (ChainedComparison.extension visibility) =
      (3*Real.sqrt 3-4)/8 ∧
    2*Bell.SignedDuality.negativeMass (ChainedComparison.extension visibility) <
      Bell.ContextualFraction.fraction ChainedComparison.A (born visibility) ∧
    Bell.LinearProgramming.mix ChainedComparison.A (ChainedComparison.extension visibility) =
      born visibility ∧
    (∑ g, ChainedComparison.extension visibility g = 1) ∧
    ∀ q, Bell.LinearProgramming.mix ChainedComparison.A q = born visibility →
      (∑ g, q g = 1) →
      Bell.SignedDuality.negativeMass (ChainedComparison.extension visibility) ≤
        Bell.SignedDuality.negativeMass q := by
  rw [born_formula visibility]
  have hc := ChainedComparison.exact_comparison visibility visibility_range.1.le visibility_range.2
  refine ⟨?_,?_, ChainedComparison.strict_separation visibility visibility_range.1 visibility_range.2,
    hc.2.1,hc.2.2.1,hc.2.2.2⟩
  · rw [ChainedComparison.contextual_fraction visibility visibility_range.1.le visibility_range.2]
    unfold visibility; ring
  · rw [ChainedComparison.extension_mass visibility visibility_range.1.le]
    unfold visibility; ring

/-- Any coefficient bounding CF by minimum negative mass on every quantum behavior
must be at least four, already for this two-qubit experiment. -/
theorem universal_coefficient_at_least_four (k : ℝ)
    (h : Bell.ContextualFraction.fraction ChainedComparison.A (born visibility) ≤
      k*Bell.SignedDuality.negativeMass (ChainedComparison.extension visibility)) : 4 ≤ k := by
  have he := quantum_counterexample
  rw [he.1,he.2.1] at h
  have hp : 0 < 3*Real.sqrt 3-4 := by
    have hv := visibility_range.1
    unfold visibility at hv
    linarith
  nlinarith

end Bell.ChainedQuantum

