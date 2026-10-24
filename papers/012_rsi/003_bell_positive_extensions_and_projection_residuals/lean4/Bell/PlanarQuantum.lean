import Bell.QuantumExample
import Bell.QuantumState
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic

/-! Arbitrary real planar binary projective measurements on the Bell pair. -/
noncomputable section
open scoped BigOperators ComplexConjugate ComplexOrder
namespace Bell.PlanarQuantum
open Bell.QuantumExample
set_option maxHeartbeats 2000000

def direction (z x : ℝ) : Matrix Bool Bool ℂ := (z:ℂ) • Z + (x:ℂ) • X
def effect (z x : ℝ) (a : Bool) : Matrix Bool Bool ℂ :=
  (1/2:ℂ) • (1 + (Bell.CHSH.sign a:ℂ) • direction z x)
def born (z x w y : ℝ) (a b : Bool) : ℝ :=
  mean t (Matrix.kronecker (effect z x a) (effect w y b))

theorem effect_hermitian (z x : ℝ) (a : Bool) :
    (effect z x a).conjTranspose = effect z x a := by
  ext r k
  cases a <;> cases r <;> cases k <;>
    simp [effect, direction, Z, X, Bell.CHSH.sign, Matrix.conjTranspose_apply]
  all_goals ring

theorem effect_projector (z x : ℝ) (h : z^2+x^2=1) (a : Bool) :
    effect z x a * effect z x a = effect z x a := by
  ext r k
  cases a <;> cases r <;> cases k <;>
    norm_num [effect, direction, Z, X, Bell.CHSH.sign, Matrix.mul_apply,
      Matrix.one_apply, Complex.ext_iff, Complex.mul_re, Complex.mul_im] <;> nlinarith

theorem effects_total (z x : ℝ) : effect z x false + effect z x true = 1 := by
  ext r k
  norm_num [effect, Matrix.add_apply, Matrix.smul_apply, smul_eq_mul,
    Matrix.sub_apply, Bell.CHSH.sign]
  ring

theorem local_povm (z x : ℝ) (h : z^2+x^2=1) :
    Bell.QuantumState.BinaryPOVM (effect z x) := by
  refine ⟨?_, effects_total z x⟩
  intro a
  have hp := Matrix.posSemidef_conjTranspose_mul_self (effect z x a)
  rw [effect_hermitian, effect_projector z x h] at hp
  exact hp

theorem born_formula (z x w y : ℝ) (a b : Bool) :
    born z x w y a b = (1+Bell.CHSH.sign a*Bell.CHSH.sign b*(z*w+x*y))/4 := by
  have ht : t^2=1/2 := by nlinarith [t_normalization]
  unfold born
  rw [mean_four_entries,ht]
  cases a <;> cases b <;>
    norm_num [effect, direction, Z, X, Bell.CHSH.sign, Matrix.kronecker_apply,
      Matrix.one_apply, Complex.mul_re, Complex.mul_im] <;> ring

theorem angle_povm (θ : ℝ) :
    Bell.QuantumState.BinaryPOVM (effect (Real.cos θ) (Real.sin θ)) := by
  apply local_povm
  nlinarith [Real.sin_sq_add_cos_sq θ]

theorem angle_born (θ φ : ℝ) (a b : Bool) :
    born (Real.cos θ) (Real.sin θ) (Real.cos φ) (Real.sin φ) a b =
      (1+Bell.CHSH.sign a*Bell.CHSH.sign b*Real.cos (θ-φ))/4 := by
  rw [born_formula, Real.cos_sub]

end Bell.PlanarQuantum
