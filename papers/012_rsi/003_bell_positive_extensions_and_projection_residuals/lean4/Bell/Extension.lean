import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Algebra.Order.BigOperators.GroupWithZero.Finset
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Algebra.Subalgebra.Basic
import Mathlib.Algebra.Module.LinearMap.Defs
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! Finite stochastic Bell locality and positive deterministic extensions. -/
noncomputable section
open scoped BigOperators
namespace Bell
attribute [local instance] Classical.propDecidable

structure Probability {I : Type} [Fintype I] (w : I → ℝ) : Prop where
  nonneg : ∀ i, 0 ≤ w i
  total : ∑ i, w i = 1

abbrev Assignment (X Y A B : Type) := (X → A) × (Y → B)
abbrev Behavior (X Y A B : Type) := X → Y → A → B → ℝ

def marginal {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
    (q : Assignment X Y A B → ℝ) : Behavior X Y A B := by
  classical
  exact fun x y a b => ∑ ω, if ω.1 x = a ∧ ω.2 y = b then q ω else 0

def PositiveExtension {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] (p : Behavior X Y A B) : Prop :=
  ∃ q, Probability q ∧ marginal q = p

def responseWeight {R : Type*} [CommSemiring R] {X A : Type} [Fintype X] (r : X → A → R) (α : X → A) : R :=
  ∏ x, r x (α x)

theorem response_total {R : Type*} [CommSemiring R] {X A : Type} [Fintype X] [Fintype A]
    (r : X → A → R) (hn : ∀ x, ∑ a, r x a = 1) :
    ∑ α, responseWeight r α = 1 := by
  classical
  simp only [responseWeight]
  rw [← Fintype.prod_sum]
  simp [hn]

theorem response_marginal {R : Type*} [CommSemiring R] {X A : Type} [Fintype X] [Fintype A]
    (r : X → A → R) (hn : ∀ x, ∑ a, r x a = 1) (x : X) (a : A) :
    (∑ α : X → A, if α x = a then responseWeight r α else 0) = r x a := by
  classical
  let s : X → A → R := fun i b => r i b * (if i = x then (if b = a then 1 else 0) else 1)
  have hs (α : X → A) : responseWeight s α =
      if α x = a then responseWeight r α else 0 := by
    simp only [responseWeight, s, Finset.prod_mul_distrib]
    have hi : (∏ i : X, if i = x then (if α i = a then (1:R) else 0) else 1) =
        if α x = a then 1 else 0 := by simp
    rw [hi]
    split_ifs <;> simp
  calc
    _ = ∑ α, responseWeight s α := by simp_rw [hs]
    _ = ∏ i, ∑ b, s i b := (Fintype.prod_sum _).symm
    _ = r x a := by
      rw [Finset.prod_eq_single x]
      · simp [s]
      · intro i _ hix; simp [s, hix, hn]
      · simp

structure LocalModel {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] (p : Behavior X Y A B) where
  Hidden : Type
  finiteHidden : Fintype Hidden
  weight : Hidden → ℝ
  probability : @Probability Hidden finiteHidden weight
  alice : Hidden → X → A → ℝ
  bob : Hidden → Y → B → ℝ
  alice_probability : ∀ l x, Probability (alice l x)
  bob_probability : ∀ l y, Probability (bob l y)
  reproduces : ∀ x y a b, p x y a b =
    @Finset.sum Hidden ℝ _ (@Finset.univ Hidden finiteHidden)
      (fun l => weight l * (alice l x a * bob l y b))

attribute [instance] LocalModel.finiteHidden

def deterministicExtension {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p)
    (ω : Assignment X Y A B) : ℝ :=
  ∑ l, m.weight l * (responseWeight (m.alice l) ω.1 * responseWeight (m.bob l) ω.2)

theorem extension_nonnegative {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p) (ω) :
    0 ≤ deterministicExtension m ω := by
  apply Finset.sum_nonneg
  intro l _
  exact mul_nonneg (m.probability.nonneg l) (mul_nonneg
    (Finset.prod_nonneg fun x _ => (m.alice_probability l x).nonneg _)
    (Finset.prod_nonneg fun y _ => (m.bob_probability l y).nonneg _))

theorem extension_total {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p) :
    ∑ ω, deterministicExtension m ω = 1 := by
  classical
  simp only [deterministicExtension]
  rw [Finset.sum_comm]
  simp only [← Finset.mul_sum, Fintype.sum_prod_type, ← Finset.mul_sum, ← Finset.sum_mul]
  simp only [response_total _ (fun x => (m.alice_probability _ x).total),
    response_total _ (fun y => (m.bob_probability _ y).total), mul_one]
  exact m.probability.total

theorem extension_marginal {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p) :
    marginal (deterministicExtension m) = p := by
  classical
  funext x y a b
  unfold marginal deterministicExtension
  have hs (P : Prop) [Decidable P] (f : m.Hidden → ℝ) :
      (if P then ∑ l, m.weight l * f l else 0) =
      ∑ l, m.weight l * (if P then f l else 0) := by
    by_cases hP : P <;> simp [hP]
  simp_rw [hs]
  rw [Finset.sum_comm, m.reproduces]
  apply Finset.sum_congr rfl
  intro l _
  rw [← Finset.mul_sum, Fintype.sum_prod_type]
  congr 1
  have hi (α : X → A) (β : Y → B) :
      (if α x = a ∧ β y = b then responseWeight (m.alice l) α * responseWeight (m.bob l) β else 0) =
      (if α x = a then responseWeight (m.alice l) α else 0) *
      (if β y = b then responseWeight (m.bob l) β else 0) := by
    split_ifs <;> simp_all
  simp_rw [hi, ← Finset.mul_sum, ← Finset.sum_mul]
  rw [response_marginal _ (fun i => (m.alice_probability l i).total),
    response_marginal _ (fun i => (m.bob_probability l i).total)]

theorem local_positive_extension {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p) :
    PositiveExtension p :=
  ⟨deterministicExtension m, ⟨extension_nonnegative m, extension_total m⟩, extension_marginal m⟩

theorem positive_extension_local {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (h : PositiveExtension p) :
    Nonempty (LocalModel p) := by
  classical
  obtain ⟨q, hq, hp⟩ := h
  refine ⟨{
    Hidden := Assignment X Y A B
    finiteHidden := inferInstance
    weight := q
    probability := hq
    alice := fun ω x a => if ω.1 x = a then 1 else 0
    bob := fun ω y b => if ω.2 y = b then 1 else 0
    alice_probability := ?_
    bob_probability := ?_
    reproduces := ?_ }⟩
  · intro ω x
    constructor
    · intro a; split_ifs <;> norm_num
    · simp
  · intro ω y
    constructor
    · intro b; split_ifs <;> norm_num
    · simp
  · intro x y a b
    rw [← hp]
    unfold marginal
    apply Finset.sum_congr rfl
    intro ω _
    split_ifs <;> simp_all

theorem positive_extension_iff_local {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] (p : Behavior X Y A B) :
    PositiveExtension p ↔ Nonempty (LocalModel p) := by
  constructor
  · exact positive_extension_local
  · rintro ⟨m⟩; exact local_positive_extension m

end Bell
