import Bell.Extension
import Mathlib.Algebra.Algebra.Pi
import Mathlib.Algebra.Algebra.Subalgebra.Lattice
import Mathlib.Algebra.BigOperators.Pi

/-! An arbitrary latent carrier, with averaging on a declared function algebra.
The hypotheses state precisely the linearity, normalization and positivity used
by the integral argument; they do not assume a positive extension exists. -/
noncomputable section
open scoped BigOperators
namespace Bell
attribute [local instance] Classical.propDecidable

structure AveragedModel {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] (p : Behavior X Y A B) where
  Hidden : Type
  functions : Subalgebra ℝ (Hidden → ℝ)
  average : functions →ₗ[ℝ] ℝ
  average_one : average 1 = 1
  average_nonnegative : ∀ (f : functions), (∀ l, 0 ≤ f.val l) → 0 ≤ average f
  alice : X → A → functions
  bob : Y → B → functions
  alice_nonnegative : ∀ x a l, 0 ≤ (alice x a).val l
  bob_nonnegative : ∀ y b l, 0 ≤ (bob y b).val l
  alice_total : ∀ x, ∑ a, alice x a = 1
  bob_total : ∀ y, ∑ b, bob y b = 1
  reproduces : ∀ x y a b, p x y a b = average (alice x a * bob y b)

def averagedExtension {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : AveragedModel p)
    (ω : Assignment X Y A B) : ℝ :=
  m.average (responseWeight m.alice ω.1 * responseWeight m.bob ω.2)

theorem averaged_extension_nonnegative {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : AveragedModel p) (ω) :
    0 ≤ averagedExtension m ω := by
  apply m.average_nonnegative
  intro l
  change 0 ≤ (responseWeight m.alice ω.1).val l * (responseWeight m.bob ω.2).val l
  have eval_product (r : X → A → m.functions) (α : X → A) :
      (responseWeight r α).val l = ∏ x, (r x (α x)).val l := by
    simp [responseWeight]
  have eval_product' (r : Y → B → m.functions) (β : Y → B) :
      (responseWeight r β).val l = ∏ y, (r y (β y)).val l := by
    simp [responseWeight]
  rw [eval_product, eval_product']
  exact mul_nonneg (Finset.prod_nonneg fun x _ => m.alice_nonnegative x _ l)
    (Finset.prod_nonneg fun y _ => m.bob_nonnegative y _ l)

theorem averaged_extension_total {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : AveragedModel p) :
    ∑ ω, averagedExtension m ω = 1 := by
  unfold averagedExtension
  rw [← map_sum]
  simp only [Fintype.sum_prod_type, ← Finset.mul_sum, ← Finset.sum_mul,
    response_total _ m.alice_total, response_total _ m.bob_total, one_mul, m.average_one]

theorem averaged_extension_marginal {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : AveragedModel p) :
    marginal (averagedExtension m) = p := by
  funext x y a b
  unfold marginal averagedExtension
  have hi (P : Prop) [Decidable P] (z : m.functions) :
      (if P then m.average z else 0) = m.average (if P then z else 0) := by
    split_ifs <;> simp
  simp_rw [hi]
  rw [← map_sum, m.reproduces]
  congr 1
  rw [Fintype.sum_prod_type]
  have hp (α : X → A) (β : Y → B) :
      (if α x = a ∧ β y = b then responseWeight m.alice α * responseWeight m.bob β else 0) =
      (if α x = a then responseWeight m.alice α else 0) *
      (if β y = b then responseWeight m.bob β else 0) := by
    split_ifs <;> simp_all
  simp_rw [hp, ← Finset.mul_sum, ← Finset.sum_mul]
  rw [response_marginal _ m.alice_total, response_marginal _ m.bob_total]

theorem averaged_positive_extension {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : AveragedModel p) :
    PositiveExtension p :=
  ⟨averagedExtension m, ⟨averaged_extension_nonnegative m, averaged_extension_total m⟩,
    averaged_extension_marginal m⟩

theorem finite_model_as_averaged {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p) :
    Nonempty (AveragedModel p) := by
  let S : Subalgebra ℝ (m.Hidden → ℝ) := ⊤
  let E : S →ₗ[ℝ] ℝ := {
    toFun := fun f => ∑ l, m.weight l * f.val l
    map_add' := by intro f g; simp [mul_add, Finset.sum_add_distrib]
    map_smul' := by
      intro c f
      simp only [Subalgebra.coe_smul, Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro l _
      ring }
  refine ⟨{
    Hidden := m.Hidden
    functions := S
    average := E
    average_one := ?_
    average_nonnegative := ?_
    alice := fun x a => ⟨fun l => m.alice l x a, by trivial⟩
    bob := fun y b => ⟨fun l => m.bob l y b, by trivial⟩
    alice_nonnegative := fun x a l => (m.alice_probability l x).nonneg a
    bob_nonnegative := fun y b l => (m.bob_probability l y).nonneg b
    alice_total := ?_
    bob_total := ?_
    reproduces := ?_ }⟩
  · simpa [E] using m.probability.total
  · intro f hf
    exact Finset.sum_nonneg (fun l _ => mul_nonneg (m.probability.nonneg l) (hf l))
  · intro x
    apply Subtype.ext
    funext l
    simpa using (m.alice_probability l x).total
  · intro y
    apply Subtype.ext
    funext l
    simpa using (m.bob_probability l y).total
  · exact m.reproduces

theorem positive_extension_iff_averaged {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] (p : Behavior X Y A B) :
    PositiveExtension p ↔ Nonempty (AveragedModel p) := by
  constructor
  · intro hp
    obtain ⟨m⟩ := positive_extension_local hp
    exact finite_model_as_averaged m
  · rintro ⟨m⟩
    exact averaged_positive_extension m

end Bell
