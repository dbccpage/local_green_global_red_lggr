/-
Copyright (c) 2026 Jeremy H. Carroll. All rights reserved.
Released under Apache 2.0 license.
Authors: Jeremy H. Carroll

Paper: The Omega Tower: Role Non-Impersonation and Authority Preservation in Agentic AI
Module: RoleNonImpersonation.AuthorityDescent
Description: Formalization of maximal sound authority descent through a quotient/transport map.
Universal quantification along a map as the right adjoint to pullback (inverse image).
-/

namespace RoleNonImpersonation

/-- Universal quantification of a predicate A along a map q : X → Y.
Also called the maximal sound descent predicate A_safe. -/
def all_q {X Y : Type} (q : X → Y) (A : X → Prop) : Y → Prop :=
  fun y => ∀ x, q x = y → A x

/-- Inverse image / pullback of a predicate B on Y along q. -/
def pullback {X Y : Type} (q : X → Y) (B : Y → Prop) : X → Prop :=
  fun x => B (q x)

/-- Predicate containment / entailment. -/
def entails {Z : Type} (P Q : Z → Prop) : Prop :=
  ∀ z, P z → Q z

/-- Lawvere Adjunction:
pullback q B ⊆ A  ↔  B ⊆ all_q q A
(Inverse image is left adjoint to universal quantification along q.) -/
theorem lawvere_adjunction {X Y : Type} (q : X → Y) (A : X → Prop) (B : Y → Prop) :
    entails (pullback q B) A ↔ entails B (all_q q A) := by
  constructor
  · intro h_sub y hB x hq
    have h_pull : pullback q B x := by
      dsimp [pullback]
      rw [hq]
      exact hB
    exact h_sub x h_pull
  · intro h_sub x h_pull
    dsimp [pullback] at h_pull
    have h_all : all_q q A (q x) := h_sub (q x) h_pull
    exact h_all x rfl

/-- Property 1 (Soundness):
Pullback of all_q q A entails A.
That is, (all_q q A) (q x) → A x. -/
theorem descent_soundness {X Y : Type} (q : X → Y) (A : X → Prop) :
    entails (pullback q (all_q q A)) A := by
  intro x h_pull
  dsimp [pullback, all_q] at h_pull
  exact h_pull x rfl

/-- Property 2 (Maximality):
Any sound descent predicate B (meaning pullback q B ⊆ A) entails all_q q A. -/
theorem descent_maximality {X Y : Type} (q : X → Y) (A : X → Prop) (B : Y → Prop)
    (h_sound : entails (pullback q B) A) :
    entails B (all_q q A) := by
  exact (lawvere_adjunction q A B).mp h_sound

/-- Property 3 (Exact Preservation on Fiber-Constant Predicates):
(all_q q A) (q x) ↔ A x holds for all x iff A is constant on fibers of q. -/
def FiberConstant {X Y : Type} (q : X → Y) (A : X → Prop) : Prop :=
  ∀ x1 x2, q x1 = q x2 → (A x1 ↔ A x2)

theorem exact_preservation_iff_fiber_constant {X Y : Type} (q : X → Y) (A : X → Prop) :
    (∀ x, all_q q A (q x) ↔ A x) ↔ FiberConstant q A := by
  constructor
  · intro h_exact x1 x2 h_fiber
    constructor
    · intro hA1
      have h_all : all_q q A (q x1) := (h_exact x1).mpr hA1
      rw [h_fiber] at h_all
      exact (h_exact x2).mp h_all
    · intro hA2
      have h_all : all_q q A (q x2) := (h_exact x2).mpr hA2
      rw [← h_fiber] at h_all
      exact (h_exact x1).mp h_all
  · intro h_fiber x
    constructor
    · exact fun h_all => descent_soundness q A x h_all
    · intro hA x' hq
      exact (h_fiber x x' hq.symm).mp hA

/-- Mixed Fiber Obstruction:
If a fiber contains both an authorized state and an unauthorized state,
no predicate on Y can exactly reproduce A on that fiber. -/
theorem mixed_fiber_obstruction {X Y : Type} (q : X → Y) (A : X → Prop)
    (x_pos x_neg : X) (h_same_fiber : q x_pos = q x_neg)
    (h_pos : A x_pos) (h_neg : ¬ A x_neg) :
    ¬ ∃ (B : Y → Prop), (B (q x_pos) ↔ A x_pos) ∧ (B (q x_neg) ↔ A x_neg) := by
  intro ⟨B, h_iff_pos, h_iff_neg⟩
  have hB_pos : B (q x_pos) := h_iff_pos.mpr h_pos
  rw [h_same_fiber] at hB_pos
  have h_false : A x_neg := h_iff_neg.mp hB_pos
  exact h_neg h_false

/-- Property 4 (Compositionality):
Universal quantification along q2 ∘ q1 is equivalent to composing universal quantifications:
all_q q2 (all_q q1 A) = all_q (q2 ∘ q1) A. -/
theorem descent_composition {X Y Z : Type} (q1 : X → Y) (q2 : Y → Z) (A : X → Prop) :
    ∀ z, all_q q2 (all_q q1 A) z ↔ all_q (q2 ∘ q1) A z := by
  intro z
  constructor
  · intro h z_x h_comp
    dsimp [all_q] at h
    have h_q2 := h (q1 z_x) h_comp
    exact h_q2 z_x rfl
  · intro h y hq2 x hq1
    have h_comp : (q2 ∘ q1) x = z := by
      change q2 (q1 x) = z
      rw [hq1, hq2]
    exact h x h_comp

/-- Property 5 (Distribution over Conjunction):
Universal quantification along q distributes over conjunction of obligations:
all_q q (fun x => A1 x ∧ A2 x) y ↔ (all_q q A1 y ∧ all_q q A2 y). -/
theorem descent_conjunction {X Y : Type} (q : X → Y) (A1 A2 : X → Prop) :
    ∀ y, all_q q (fun x => A1 x ∧ A2 x) y ↔ (all_q q A1 y ∧ all_q q A2 y) := by
  intro y
  constructor
  · intro h
    constructor
    · intro x hq
      exact (h x hq).1
    · intro x hq
      exact (h x hq).2
  · intro ⟨h1, h2⟩ x hq
    exact ⟨h1 x hq, h2 x hq⟩

end RoleNonImpersonation
