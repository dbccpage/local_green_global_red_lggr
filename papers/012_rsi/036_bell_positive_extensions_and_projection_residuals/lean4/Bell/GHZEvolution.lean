import Bell.BinaryScenarios
import Bell.QuantumExample
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Inverse

/-! An explicit three-qubit unitary orbit, its X/Y Born table, and exact
contextuality exit windows. Time is dimensionless (coupling times time).
The Hamiltonian acts only on the span of |000> and |111>. -/
noncomputable section
open scoped BigOperators ComplexConjugate
namespace Bell.GHZEvolution
open Bell.LinearProgramming Bell.NegativeMassFamilies Bell.BinaryScenarios
set_option maxHeartbeats 2000000

abbrev Index := Bool × Bool × Bool
abbrev Operator := Matrix Index Index ℂ

def state (c s : ℝ) : EuclideanSpace ℂ Index := WithLp.toLp 2
  (fun i => if i = (false,false,false) then (c:ℂ)
    else if i = (true,true,true) then (-s:ℂ) else 0)

def pauli (x : Bool) : Matrix Bool Bool ℂ := fun r k =>
  if r = k then 0 else if x then (if r then Complex.I else -Complex.I) else 1

def effect (x a : Bool) : Matrix Bool Bool ℂ :=
  (1/2:ℂ) • (1 - (Bell.CHSH.sign a : ℂ) • pauli x)

def measurement (i : Fin 64) : Operator := fun r k =>
  effect (i.val/32 == 1) (i.val/4%2 == 1) r.1 k.1 *
  effect (i.val/16%2 == 1) (i.val/2%2 == 1) r.2.1 k.2.1 *
  effect (i.val/8%2 == 1) (i.val%2 == 1) r.2.2 k.2.2

def mean (c s : ℝ) (T : Operator) : ℝ :=
  (∑ i, star (state c s i) * ∑ j, T i j * state c s j).re

def born (c s : ℝ) : Fin 64 → ℝ := fun i => mean c s (measurement i)

theorem state_norm_sq (c s : ℝ) : ‖state c s‖ ^ 2 = c^2+s^2 := by
  simp [EuclideanSpace.norm_sq_eq, state, Fintype.sum_prod_type,
    Complex.norm_real, Real.norm_eq_abs, sq_abs]
  ring

theorem orbit_unit (t : ℝ) : ‖state (Real.cos t) (Real.sin t)‖ = 1 := by
  have h := state_norm_sq (Real.cos t) (Real.sin t)
  have hs := Real.sin_sq_add_cos_sq t
  nlinarith [norm_nonneg (state (Real.cos t) (Real.sin t))]

theorem pauli_hermitian (x : Bool) : (pauli x).conjTranspose = pauli x := by
  ext r k
  cases x <;> cases r <;> cases k <;> simp [pauli, Matrix.conjTranspose_apply]

theorem pauli_square (x : Bool) : pauli x * pauli x = 1 := by
  ext r k
  cases x <;> cases r <;> cases k <;>
    norm_num [pauli, Matrix.mul_apply, Fintype.sum_bool, Matrix.one_apply]

theorem effects_total (x : Bool) : effect x false + effect x true = 1 := by
  ext r k
  cases x <;> cases r <;> cases k <;>
    norm_num [effect, pauli, Bell.CHSH.sign, Matrix.one_apply]

theorem effect_projector (x a : Bool) : effect x a * effect x a = effect x a := by
  ext r k
  cases x <;> cases a <;> cases r <;> cases k <;>
    norm_num [effect, pauli, Bell.CHSH.sign, Matrix.mul_apply,
      Fintype.sum_bool, Matrix.one_apply, Complex.ext_iff, Complex.mul_re, Complex.mul_im]

theorem mean_corners (c s : ℝ) (T : Operator) :
    mean c s T = c^2 * (T (false,false,false) (false,false,false)).re +
      s^2 * (T (true,true,true) (true,true,true)).re -
      c*s*((T (false,false,false) (true,true,true)).re +
        (T (true,true,true) (false,false,false)).re) := by
  simp [mean, state, Fintype.sum_prod_type, Complex.mul_re, Complex.mul_im]
  ring

theorem born_formula (c s : ℝ) (h : c^2+s^2=1) :
    born c s = behavior mermin (2*c*s) := by
  funext i
  unfold born
  rw [mean_corners]
  fin_cases i <;>
    norm_num [measurement, effect, pauli, Bell.CHSH.sign, Matrix.one_apply,
      behavior, mermin, merminCI, spin, Complex.mul_re, Complex.mul_im] <;>
    nlinarith

theorem orbit_born (t : ℝ) :
    born (Real.cos t) (Real.sin t) = behavior mermin (Real.sin (2*t)) := by
  rw [born_formula _ _ (by nlinarith [Real.sin_sq_add_cos_sq t])]
  congr 1
  rw [Real.sin_two_mul]
  ring

/-- The real rotation block; multiplying by i gives a Hermitian Hamiltonian. -/
def generator : Matrix Bool Bool ℂ := fun r k =>
  if r = k then 0 else if r then -1 else 1

def rotation (t : ℝ) : Matrix Bool Bool ℂ := fun r k =>
  if r = k then (Real.cos t : ℂ) else
    if r then (-Real.sin t : ℂ) else (Real.sin t : ℂ)

theorem generator_skew : generator.conjTranspose = -generator := by
  ext r k
  cases r <;> cases k <;> simp [generator, Matrix.conjTranspose_apply]

theorem rotation_unitary (t : ℝ) : (rotation t).conjTranspose * rotation t = 1 := by
  have h : (Real.cos t : ℂ)^2 + (Real.sin t : ℂ)^2 = 1 := by
    exact_mod_cast (show Real.cos t ^ 2 + Real.sin t ^ 2 = 1 by
      nlinarith [Real.sin_sq_add_cos_sq t])
  ext r k
  cases r <;> cases k <;>
    simp [rotation, Matrix.conjTranspose_apply, Matrix.mul_apply,
      -Complex.ofReal_cos, -Complex.ofReal_sin] <;>
      ring_nf at * <;> assumption

theorem rotation_zero : rotation 0 = 1 := by
  ext r k
  cases r <;> cases k <;> simp [rotation]

theorem rotation_add (t u : ℝ) : rotation (t+u) = rotation t * rotation u := by
  ext r k
  cases r <;> cases k <;>
    simp [rotation, Matrix.mul_apply, Real.cos_add, Real.sin_add,
      Complex.ofReal_add, Complex.ofReal_sub, Complex.ofReal_mul] <;> ring

theorem hamiltonian_hermitian :
    (Complex.I • generator).conjTranspose = Complex.I • generator := by
  ext r k
  cases r <;> cases k <;> simp [generator, Matrix.conjTranspose_apply]

def visibility (t : ℝ) : ℝ := Real.sin (2*t)
def mass (t : ℝ) : ℝ := max 0 (visibility t - 1/2)
def cf (t : ℝ) : ℝ := max 0 (2*visibility t - 1)

theorem visibility_range (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4) :
    0 ≤ visibility t ∧ visibility t ≤ 1 := by
  exact ⟨Real.sin_nonneg_of_nonneg_of_le_pi (by linarith) (by linarith [Real.pi_pos]),
    Real.sin_le_one _⟩

theorem orbit_optima (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4) :
    Bell.ContextualFraction.fraction mermin.A (born (Real.cos t) (Real.sin t)) = cf t ∧
    Bell.SignedDuality.negativeMass (extension mermin (visibility t)) = mass t ∧
    ∀ q, mix mermin.A q = born (Real.cos t) (Real.sin t) → (∑ g, q g = 1) →
      mass t ≤ Bell.SignedDuality.negativeMass q := by
  rw [orbit_born]
  have hv := visibility_range t ht ht1
  exact ⟨mermin_contextual_fraction _ hv.1 hv.2,
    (mermin_negative_mass _ hv.1).2.2.1, (mermin_negative_mass _ hv.1).2.2.2⟩

theorem comparison (t : ℝ) : cf t = 2*mass t := by
  dsimp [cf, mass]
  by_cases h : visibility t ≤ 1/2
  · rw [max_eq_left (by linarith), max_eq_left (by linarith)]; ring
  · rw [max_eq_right (by linarith), max_eq_right (by linarith)]; ring

end Bell.GHZEvolution
