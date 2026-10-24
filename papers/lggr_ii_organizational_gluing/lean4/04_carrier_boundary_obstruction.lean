import primitive_difference
import «03_non_additivity»

namespace PaperAE005

open OmegaCore

universe u v w z

structure ComposedTrace (α : Type u) (β : Type v) where
  left : α
  right : β

def jointCarrier {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q) (c : ComposedTrace α β) : P × Q :=
  (π1 c.left, π2 c.right)

def jointCarrierPD {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q) :
    PrimitiveDifference (ComposedTrace α β) Prop where
  δ := fun a b => jointCarrier π1 π2 a = jointCarrier π1 π2 b
  Zero := fun h => h
  zero_refl := fun _ => rfl
  zero_symm := fun _ _ h => h.symm
  zero_trans := fun _ _ _ hxy hyz => hxy.trans hyz

def orgDeltaComposed {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q)
    (e1 : P → Bool) (e2 : Q → Bool) (Eg : ComposedTrace α β → Bool)
    (c : ComposedTrace α β) : Int :=
  orgDelta (Eg c) (e1 (π1 c.left) && e2 (π2 c.right))

def LocallyGreen {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q) (e1 : P → Bool) (e2 : Q → Bool)
    (c : ComposedTrace α β) : Prop :=
  e1 (π1 c.left) = true ∧ e2 (π2 c.right) = true

theorem locally_green_transport {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q) (e1 : P → Bool) (e2 : Q → Bool)
    {c c' : ComposedTrace α β}
    (hclass : jointCarrier π1 π2 c = jointCarrier π1 π2 c')
    (hgreen : LocallyGreen π1 π2 e1 e2 c) :
    LocallyGreen π1 π2 e1 e2 c' := by
  obtain ⟨hg1, hg2⟩ := hgreen
  have h1 : π1 c.left = π1 c'.left := congrArg Prod.fst hclass
  have h2 : π2 c.right = π2 c'.right := congrArg Prod.snd hclass
  refine ⟨?_, ?_⟩
  · rw [← h1]; exact hg1
  · rw [← h2]; exact hg2

theorem boundary_carrier_mixing_forces_lggr
    {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q) (e1 : P → Bool) (e2 : Q → Bool)
    (Eg : ComposedTrace α β → Bool) {c c' : ComposedTrace α β}
    (hclass : jointCarrier π1 π2 c = jointCarrier π1 π2 c')
    (hgreen : LocallyGreen π1 π2 e1 e2 c)
    (hmix : Eg c ≠ Eg c') :
    ∃ d : ComposedTrace α β,
      (d = c ∨ d = c') ∧
      jointCarrier π1 π2 d = jointCarrier π1 π2 c ∧
      orgDeltaComposed π1 π2 e1 e2 Eg d = -1 := by
  obtain ⟨hg1, hg2⟩ := hgreen
  obtain ⟨hg1', hg2'⟩ := locally_green_transport π1 π2 e1 e2 hclass ⟨hg1, hg2⟩
  cases hEc : Eg c with
  | false =>
    refine ⟨c, Or.inl rfl, rfl, ?_⟩
    unfold orgDeltaComposed orgDelta
    rw [hEc, hg1, hg2]
    rfl
  | true =>
    have hEc' : Eg c' = false := by
      cases hEc' : Eg c' with
      | false => rfl
      | true =>
        rw [hEc, hEc'] at hmix
        exact absurd rfl hmix
    refine ⟨c', Or.inr rfl, hclass.symm, ?_⟩
    unfold orgDeltaComposed orgDelta
    rw [hEc', hg1', hg2']
    rfl

theorem boundary_carrier_mixing_blocks_quotient_factorization
    {α : Type u} {β : Type v} {P : Type w} {Q : Type z}
    (π1 : α → P) (π2 : β → Q)
    (Eg : ComposedTrace α β → Bool) {c c' : ComposedTrace α β}
    (hclass : jointCarrier π1 π2 c = jointCarrier π1 π2 c')
    (hmix : Eg c ≠ Eg c') :
    ¬ (∃ F : (jointCarrierPD π1 π2).ResidualQuotient → Bool,
        ∀ x : ComposedTrace α β,
          F ((jointCarrierPD π1 π2).classOf x) = Eg x) := by
  intro ⟨F, hF⟩
  have hz : (jointCarrierPD π1 π2).ZeroRel c c' := hclass
  have h_eq : (jointCarrierPD π1 π2).classOf c = (jointCarrierPD π1 π2).classOf c' :=
    (jointCarrierPD π1 π2).classOf_eq_of_zero hz
  have hFc := hF c
  have hFc' := hF c'
  rw [← hFc, ← hFc', h_eq] at hmix
  exact hmix rfl

end PaperAE005
