/- Institutions That Can Know, version 0.1.0.
Recovery is relative to declared functions on a source domain. These proofs do
not assert truth of records, operational authorization, or empirical efficacy. -/
namespace InstitutionalReasoning

universe u v w t

def Image {X : Type u} {Y : Type v} (C : X → Y) :=
  {y : Y // ∃ x, C x = y}

def compress {X : Type u} {Y : Type v} (C : X → Y) (x : X) : Image C :=
  ⟨C x, x, rfl⟩

def FiberConstant {X : Type u} {Y : Type v} {Z : Type w}
    (C : X → Y) (q : X → Z) : Prop :=
  ∀ x x', C x = C x' → q x = q x'

def Recoverable {X : Type u} {Y : Type v} {Z : Type w}
    (C : X → Y) (q : X → Z) : Prop :=
  ∃ d : Image C → Z, ∀ x, d (compress C x) = q x

/-- Proposition 1 requires the admitted relation to preserve the invariant. -/
theorem relative_non_identification {P : Type u} {V : Type v}
    (admitted : P → P → Prop) (J : P → V)
    (preserves : ∀ a b, admitted a b → J a = J b)
    (a b : P) (separates : J a ≠ J b) : ¬ admitted a b := by
  intro h
  exact separates (preserves a b h)

/-- Proposition 2, on the actual image, without a nonempty codomain premise. -/
theorem recoverable_iff_fiber_constant {X : Type u} {Y : Type v} {Z : Type w}
    (C : X → Y) (q : X → Z) : Recoverable C q ↔ FiberConstant C q := by
  constructor
  · rintro ⟨d, hd⟩ x x' h
    have he : compress C x = compress C x' := Subtype.ext h
    exact (hd x).symm.trans ((congrArg d he).trans (hd x'))
  · intro h
    classical
    refine ⟨fun y => q (Classical.choose y.property), ?_⟩
    intro x
    apply h
    exact Classical.choose_spec (compress C x).property

theorem profile_fiber_constant_iff {X : Type u} {Y : Type v} {Z : Type w}
    {I : Type t} (C : X → Y) (q : I → X → Z) :
    FiberConstant C (fun x i => q i x) ↔ ∀ i, FiberConstant C (q i) := by
  constructor
  · intro h i x x' hc
    exact congrFun (h x x' hc) i
  · intro h x x' hc
    funext i
    exact h i x x' hc

theorem profile_recoverable_iff {X : Type u} {Y : Type v} {Z : Type w}
    {I : Type t} (C : X → Y) (q : I → X → Z) :
    Recoverable C (fun x i => q i x) ↔ ∀ i, FiberConstant C (q i) := by
  exact (recoverable_iff_fiber_constant C _).trans (profile_fiber_constant_iff C q)

/-- A side record refines exactly the fibers which its values distinguish. -/
theorem side_recovery_iff {X : Type u} {Y : Type v} {Z : Type w} {S : Type t}
    (C : X → Y) (side : X → S) (q : X → Z) :
    Recoverable (fun x => (C x, side x)) q ↔
      ∀ x x', C x = C x' → side x = side x' → q x = q x' := by
  rw [recoverable_iff_fiber_constant]
  constructor
  · intro h x x' hc hs
    exact h x x' (Prod.ext hc hs)
  · intro h x x' he
    exact h x x' (congrArg Prod.fst he) (congrArg Prod.snd he)

/-- The separation step of Proposition 3; not the general cardinality bound. -/
theorem distinct_answers_require_distinct_side_codes
    {X : Type u} {Y : Type v} {Z : Type w} {S : Type t}
    (C : X → Y) (side : X → S) (q : X → Z)
    (recovers : Recoverable (fun x => (C x, side x)) q)
    (x x' : X) (same_summary : C x = C x') (different_answer : q x ≠ q x') :
    side x ≠ side x' := by
  intro same_side
  exact different_answer ((side_recovery_iff C side q).mp recovers x x' same_summary same_side)

theorem joint_constraint_obstruction {A : Type u} (a b c : A)
    (hab : a = b) (hbc : b = c) (hca : c ≠ a) : False := by
  exact hca (hab.trans hbc).symm

/-- Intersection membership gives each constraint, not execution authority. -/
theorem joint_action_respects_each_constraint {I : Type u} {A : Type v}
    (acceptable : I → A → Prop) (a : A) (joint : ∀ i, acceptable i a)
    (i : I) : acceptable i a := by
  exact joint i

end InstitutionalReasoning
