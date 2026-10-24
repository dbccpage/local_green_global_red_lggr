import Bell.QuantumState
import Mathlib.Analysis.Matrix.Order

/-! Actual joint Born tables for commuting binary POVMs and local tensor lifts. -/
noncomputable section
open scoped BigOperators ComplexOrder MatrixOrder Matrix.Norms.L2Operator
open Matrix Bell.QuantumState
namespace Bell.QuantumMeasurement

variable {n : Type} [Fintype n] [DecidableEq n]

def behavior (ρ : Operator n) (M N : Bool → Bool → Operator n) : Bell.CHSH.Table :=
  fun x y a b => mean ρ (M x a * N y b)

def CrossCommute (M N : Bool → Bool → Operator n) : Prop :=
  ∀ x y a b, Commute (M x a) (N y b)

theorem joint_effect_positive (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : CrossCommute M N) (x y a b : Bool) : (M x a * N y b).PosSemidef :=
  (Commute.mul_nonneg ((hM x).positive a).nonneg ((hN y).positive b).nonneg
    (hc x y a b)).posSemidef

theorem born_nonnegative (ρ : Operator n) (hρ : Density ρ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : CrossCommute M N) (x y a b : Bool) : 0 ≤ behavior ρ M N x y a b :=
  density_mean_nonneg _ _ hρ (joint_effect_positive M N hM hN hc x y a b)

theorem born_complex_trace (ρ : Operator n) (hρ : Density ρ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : CrossCommute M N) (x y a b : Bool) :
    (behavior ρ M N x y a b : ℂ) = (ρ * (M x a * N y b)).trace := by
  apply Complex.ext
  · rfl
  · simp only [Complex.ofReal_im]
    exact (density_trace_real ρ _ hρ (joint_effect_positive M N hM hN hc x y a b).isHermitian).symm

theorem born_alice_marginal (ρ : Operator n) (M N : Bool → Bool → Operator n)
    (hN : ∀ y, BinaryPOVM (N y)) (x y a : Bool) :
    ∑ b, behavior ρ M N x y a b = mean ρ (M x a) := by
  have h : mean ρ (M x a * (N y false + N y true)) = mean ρ (M x a) := by
    rw [(hN y).total, mul_one]
  simpa [behavior, Fintype.sum_bool, mul_add, mean_add, add_comm] using h

theorem born_bob_marginal (ρ : Operator n) (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (x y b : Bool) :
    ∑ a, behavior ρ M N x y a b = mean ρ (N y b) := by
  have h : mean ρ ((M x false + M x true) * N y b) = mean ρ (N y b) := by
    rw [(hM x).total, one_mul]
  simpa [behavior, Fintype.sum_bool, add_mul, mean_add, add_comm] using h

theorem born_normalized (ρ : Operator n) (hρ : Density ρ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) (x y : Bool) :
    ∑ r : Bool × Bool, behavior ρ M N x y r.1 r.2 = 1 := by
  simp only [Fintype.sum_prod_type, born_alice_marginal ρ M N hN]
  have h : mean ρ (M x false + M x true) = 1 := by rw [(hM x).total, mean_one ρ hρ]
  simpa [Fintype.sum_bool, mean_add, add_comm] using h

theorem born_probability (ρ : Operator n) (hρ : Density ρ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : CrossCommute M N) (x y : Bool) :
    Bell.Probability (fun r : Bool × Bool => behavior ρ M N x y r.1 r.2) :=
  ⟨fun r => born_nonnegative ρ hρ M N hM hN hc x y r.1 r.2,
    born_normalized ρ hρ M N hM hN x y⟩

theorem born_score_trace (ρ : Operator n) (M N : Bool → Bool → Operator n) :
    Bell.CHSH.score (behavior ρ M N) =
      mean ρ (chshMatrix (observable (M false)) (observable (M true))
        (observable (N false)) (observable (N true))) := by
  simp [Bell.CHSH.score, Fintype.sum_prod_type, Bell.CHSH.coefficient,
    Bell.CHSH.sign, behavior, chshMatrix, observable, mul_add, mul_sub, sub_mul,
    mean_add, mean_sub]
  ring

theorem born_chsh_bound (ρ : Operator n) (hρ : Density ρ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) :
    |Bell.CHSH.score (behavior ρ M N)| ≤ 2 * Real.sqrt 2 := by
  rw [born_score_trace]
  exact density_povm_chsh_bound ρ hρ M N hM hN

variable {m : Type} [Fintype m] [DecidableEq m]

def leftLift (M : Bool → Operator n) : Bool → Operator (n × m) :=
  fun a => Matrix.kronecker (M a) 1

def rightLift (N : Bool → Operator m) : Bool → Operator (n × m) :=
  fun b => Matrix.kronecker 1 (N b)

theorem leftLift_povm (M : Bool → Operator n) (hM : BinaryPOVM M) :
    BinaryPOVM (leftLift (m := m) M) := by
  refine ⟨fun a => (hM.positive a).kronecker Matrix.PosSemidef.one, ?_⟩
  change Matrix.kronecker (M false) (1 : Operator m) + Matrix.kronecker (M true) 1 = 1
  simp only [Matrix.kronecker]
  rw [← Matrix.add_kronecker, hM.total, Matrix.one_kronecker_one]

theorem rightLift_povm (N : Bool → Operator m) (hN : BinaryPOVM N) :
    BinaryPOVM (rightLift (n := n) N) := by
  refine ⟨fun b => Matrix.PosSemidef.one.kronecker (hN.positive b), ?_⟩
  change Matrix.kronecker (1 : Operator n) (N false) + Matrix.kronecker 1 (N true) = 1
  simp only [Matrix.kronecker]
  rw [← Matrix.kronecker_add, hN.total, Matrix.one_kronecker_one]

theorem tensor_cross_commute (M : Bool → Bool → Operator n)
    (N : Bool → Bool → Operator m) :
    CrossCommute (fun x => leftLift (m := m) (M x)) (fun y => rightLift (n := n) (N y)) := by
  intro x y a b
  change Matrix.kronecker (M x a) 1 * Matrix.kronecker 1 (N y b) =
    Matrix.kronecker 1 (N y b) * Matrix.kronecker (M x a) 1
  simp only [Matrix.kronecker, ← Matrix.mul_kronecker_mul, mul_one, one_mul]

def tensorBehavior (ρ : Operator (n × m)) (M : Bool → Bool → Operator n)
    (N : Bool → Bool → Operator m) : Bell.CHSH.Table :=
  fun x y a b => mean ρ (Matrix.kronecker (M x a) (N y b))

theorem tensor_behavior_eq (ρ : Operator (n × m)) (M : Bool → Bool → Operator n)
    (N : Bool → Bool → Operator m) : tensorBehavior ρ M N =
      behavior ρ (fun x => leftLift (m := m) (M x)) (fun y => rightLift (n := n) (N y)) := by
  funext x y a b
  simp [tensorBehavior, behavior, leftLift, rightLift, ← Matrix.mul_kronecker_mul]

theorem tensor_born_probability (ρ : Operator (n × m)) (hρ : Density ρ)
    (M : Bool → Bool → Operator n) (N : Bool → Bool → Operator m)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) (x y : Bool) :
    Bell.Probability (fun r : Bool × Bool => tensorBehavior ρ M N x y r.1 r.2) := by
  rw [tensor_behavior_eq]
  exact born_probability ρ hρ _ _ (fun x => leftLift_povm _ (hM x))
    (fun y => rightLift_povm _ (hN y)) (tensor_cross_commute M N) x y

theorem tensor_born_chsh_bound (ρ : Operator (n × m)) (hρ : Density ρ)
    (M : Bool → Bool → Operator n) (N : Bool → Bool → Operator m)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) :
    |Bell.CHSH.score (tensorBehavior ρ M N)| ≤ 2 * Real.sqrt 2 := by
  rw [tensor_behavior_eq]
  exact born_chsh_bound ρ hρ _ _ (fun x => leftLift_povm _ (hM x))
    (fun y => rightLift_povm _ (hN y))

end Bell.QuantumMeasurement
