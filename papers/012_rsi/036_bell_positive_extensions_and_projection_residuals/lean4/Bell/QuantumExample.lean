import Bell.Quantum
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Matrix.Kronecker

/-! Exact complex two-qubit Bell state and local dichotomic observables. -/
noncomputable section
open scoped BigOperators ComplexConjugate
namespace Bell.QuantumExample

abbrev Index := Bool × Bool
abbrev Operator := Matrix Index Index ℂ

def Z : Matrix Bool Bool ℂ := fun i j => if i = j then (if i then -1 else 1) else 0
def X : Matrix Bool Bool ℂ := fun i j => if i = j then 0 else 1

def alice (x : Bool) : Operator := Matrix.kronecker (if x then X else Z) 1

def bob (t : ℝ) (y : Bool) : Operator :=
  Matrix.kronecker 1 ((t : ℂ) • (Z + (if y then -X else X)))

def state (t : ℝ) : EuclideanSpace ℂ Index :=
  WithLp.toLp 2 (fun i => if i.1 = i.2 then (t : ℂ) else 0)

def mean (t : ℝ) (T : Operator) : ℝ :=
  (∑ i, star ((state t) i) * ∑ j, T i j * (state t) j).re

def outcomeProjector (T : Operator) (a : Bool) : Operator :=
  (1 / 2 : ℂ) • (1 + (CHSH.sign a : ℂ) • T)

def behavior (t : ℝ) : CHSH.Table := fun x y a b =>
  mean t (outcomeProjector (alice x) a * outcomeProjector (bob t y) b)

theorem mean_eq_inner (t : ℝ) (T : Operator) :
    mean t T = (inner ℂ (state t) (Matrix.toEuclideanLin T (state t))).re := by
  unfold mean
  congr 1
  change (∑ i, star (state t i) * ∑ j, T i j * state t j) =
    ∑ i, (∑ j, T i j * state t j) * star (state t i)
  exact Finset.sum_congr rfl (fun _ _ => mul_comm _ _)

theorem state_norm_sq (t : ℝ) : ‖state t‖ ^ 2 = 2 * t ^ 2 := by
  simp [EuclideanSpace.norm_sq_eq, state, Fintype.sum_prod_type,
    Complex.norm_real, Real.norm_eq_abs, sq_abs]
  ring

theorem alice_hermitian (x : Bool) : (alice x).conjTranspose = alice x := by
  ext ⟨i,j⟩ ⟨k,l⟩
  cases x <;> cases i <;> cases j <;> cases k <;> cases l <;>
    norm_num [alice, X, Z, Matrix.kronecker_apply, Matrix.conjTranspose_apply, Matrix.one_apply]

theorem bob_hermitian (t : ℝ) (y : Bool) : (bob t y).conjTranspose = bob t y := by
  ext ⟨i,j⟩ ⟨k,l⟩
  cases y <;> cases i <;> cases j <;> cases k <;> cases l <;>
    simp [bob, X, Z, Matrix.conjTranspose_apply]

theorem alice_square (x : Bool) : alice x * alice x = 1 := by
  ext ⟨i,j⟩ ⟨k,l⟩
  cases x <;> cases i <;> cases j <;> cases k <;> cases l <;>
    norm_num [alice, X, Z, Matrix.kronecker_apply, Matrix.mul_apply,
      Fintype.sum_prod_type, Fintype.sum_bool, Matrix.one_apply]

theorem bob_square (t : ℝ) (ht : 2 * t ^ 2 = 1) (y : Bool) : bob t y * bob t y = 1 := by
  have htC : 2 * (t : ℂ) ^ 2 = 1 := by exact_mod_cast ht
  ext ⟨i,j⟩ ⟨k,l⟩
  cases y <;> cases i <;> cases j <;> cases k <;> cases l <;>
    norm_num [bob, X, Z, Matrix.kronecker_apply, Matrix.mul_apply,
      Fintype.sum_prod_type, Fintype.sum_bool, Matrix.one_apply] <;> (convert htC using 1; ring)

theorem local_commutation (t : ℝ) (x y : Bool) : alice x * bob t y = bob t y * alice x := by
  ext ⟨i,j⟩ ⟨k,l⟩
  cases x <;> cases y <;> cases i <;> cases j <;> cases k <;> cases l <;>
    simp [alice, bob, X, Z, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.one_apply]

theorem mean_four_entries (t : ℝ) (T : Operator) :
    mean t T = t ^ 2 * (T (false,false) (false,false) + T (false,false) (true,true) +
      T (true,true) (false,false) + T (true,true) (true,true)).re := by
  simp [mean, state, Fintype.sum_prod_type, Complex.mul_re, Complex.mul_im]
  ring

set_option maxHeartbeats 2000000 in
theorem born_formula (t : ℝ) (ht : 2 * t ^ 2 = 1) : behavior t = CHSH.isotropic t := by
  funext x y a b
  unfold behavior
  rw [mean_four_entries]
  cases x <;> cases y <;> cases a <;> cases b <;>
    norm_num [outcomeProjector, alice, bob, X, Z,
      CHSH.isotropic, CHSH.coefficient, CHSH.sign,
      Matrix.kronecker_apply, Matrix.mul_apply, Matrix.one_apply,
      Fintype.sum_prod_type, Fintype.sum_bool, Complex.mul_re, Complex.add_re,
      Complex.mul_im, Complex.add_im] <;> nlinarith [ht, congrArg (fun z : ℝ => z * t) ht]

def t : ℝ := 1 / Real.sqrt 2

theorem t_normalization : 2 * t ^ 2 = 1 := by
  unfold t
  have hs := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)
  have hn : Real.sqrt 2 ≠ 0 := ne_of_gt (Real.sqrt_pos.2 (by norm_num))
  field_simp
  nlinarith

theorem bell_state_unit : ‖state t‖ = 1 := by
  have h := state_norm_sq t
  rw [t_normalization] at h
  nlinarith [norm_nonneg (state t)]

theorem tsirelson_attained : CHSH.score (behavior t) = 2 * Real.sqrt 2 := by
  rw [born_formula t t_normalization, CHSH.isotropic_score]
  unfold t
  have hs := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)
  have hn : Real.sqrt 2 ≠ 0 := ne_of_gt (Real.sqrt_pos.2 (by norm_num))
  field_simp
  nlinarith

theorem bell_behavior_no_positive_extension : ¬ PositiveExtension (behavior t) := by
  apply CHSH.violation_no_extension
  rw [tsirelson_attained, abs_of_nonneg (by positivity)]
  have hs := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)
  have hn := Real.sqrt_nonneg (2 : ℝ)
  nlinarith

end Bell.QuantumExample
