/-!
Primitive difference quotient kernel.

This file records the minimum data needed for the zero-difference relation,
the quotient by that relation, and the condition under which `δ` descends to
the quotient.
-/

namespace OmegaCore

universe u v w z

structure PrimitiveDifference (α : Type u) (β : Type v) where
  δ : α → α → β
  Zero : β → Prop
  zero_refl : ∀ x : α, Zero (δ x x)
  zero_symm : ∀ x y : α, Zero (δ x y) → Zero (δ y x)
  zero_trans : ∀ x y z : α, Zero (δ x y) → Zero (δ y z) → Zero (δ x z)

namespace PrimitiveDifference

variable {α : Type u} {β : Type v} {γ η : Type w} {κ : Type z}

def ZeroRel (P : PrimitiveDifference α β) (x y : α) : Prop :=
  P.Zero (P.δ x y)

theorem zeroRel_refl (P : PrimitiveDifference α β) :
    ∀ x : α, P.ZeroRel x x :=
  P.zero_refl

theorem zeroRel_symm (P : PrimitiveDifference α β) :
    ∀ {x y : α}, P.ZeroRel x y → P.ZeroRel y x :=
  fun {x y} => P.zero_symm x y

theorem zeroRel_trans (P : PrimitiveDifference α β) :
    ∀ {x y z : α}, P.ZeroRel x y → P.ZeroRel y z → P.ZeroRel x z :=
  fun {x y z} => P.zero_trans x y z

theorem zeroRel_equivalence (P : PrimitiveDifference α β) :
    Equivalence P.ZeroRel where
  refl := zeroRel_refl P
  symm := zeroRel_symm P
  trans := zeroRel_trans P

def zeroSetoid (P : PrimitiveDifference α β) : Setoid α where
  r := P.ZeroRel
  iseqv := zeroRel_equivalence P

def ResidualQuotient (P : PrimitiveDifference α β) : Type u :=
  Quotient (zeroSetoid P)

def classOf (P : PrimitiveDifference α β) (x : α) : P.ResidualQuotient :=
  Quotient.mk (zeroSetoid P) x

theorem classOf_eq_of_zero
    (P : PrimitiveDifference α β) {x y : α} (hxy : P.ZeroRel x y) :
    P.classOf x = P.classOf y :=
  Quotient.sound hxy

theorem classOf_eq_iff_zeroRel
    (P : PrimitiveDifference α β) {x y : α} :
    P.classOf x = P.classOf y ↔ P.ZeroRel x y := by
  constructor
  · exact Quotient.exact
  · exact classOf_eq_of_zero P

def DeltaCongruent (P : PrimitiveDifference α β) : Prop :=
  ∀ x x' y y' : α,
    P.ZeroRel x x' →
    P.ZeroRel y y' →
    P.δ x y = P.δ x' y'

def deltaFactor
    (P : PrimitiveDifference α β) (hcongr : P.DeltaCongruent) :
    P.ResidualQuotient → P.ResidualQuotient → β :=
  Quotient.lift₂
    (s₁ := zeroSetoid P)
    (s₂ := zeroSetoid P)
    (fun x y => P.δ x y)
    (by
      intro x y x' y' hx hy
      exact hcongr x x' y y' hx hy)

theorem deltaFactor_classOf_classOf
    (P : PrimitiveDifference α β) (hcongr : P.DeltaCongruent)
    (x y : α) :
    P.deltaFactor hcongr (P.classOf x) (P.classOf y) = P.δ x y := by
  rfl

theorem deltaFactor_requires_congruence
    (P : PrimitiveDifference α β)
    (F : P.ResidualQuotient → P.ResidualQuotient → β)
    (hF : ∀ x y : α, F (P.classOf x) (P.classOf y) = P.δ x y) :
    P.DeltaCongruent := by
  intro x x' y y' hx hy
  calc
    P.δ x y = F (P.classOf x) (P.classOf y) := (hF x y).symm
    _ = F (P.classOf x') (P.classOf y') := by
      rw [classOf_eq_of_zero P hx, classOf_eq_of_zero P hy]
    _ = P.δ x' y' := hF x' y'

theorem deltaFactor_exists_iff_deltaCongruent
    (P : PrimitiveDifference α β) :
    (∃ F : P.ResidualQuotient → P.ResidualQuotient → β,
        ∀ x y : α, F (P.classOf x) (P.classOf y) = P.δ x y)
      ↔ P.DeltaCongruent := by
  constructor
  · intro h
    rcases h with ⟨F, hF⟩
    exact deltaFactor_requires_congruence P F hF
  · intro hcongr
    exact ⟨P.deltaFactor hcongr, deltaFactor_classOf_classOf P hcongr⟩

theorem deltaFactor_unique
    (P : PrimitiveDifference α β) (hcongr : P.DeltaCongruent)
    (F : P.ResidualQuotient → P.ResidualQuotient → β)
    (hF : ∀ x y : α, F (P.classOf x) (P.classOf y) = P.δ x y) :
    F = P.deltaFactor hcongr := by
  funext qx qy
  refine Quotient.inductionOn₂ qx qy ?_
  intro x y
  change F (P.classOf x) (P.classOf y) =
    P.deltaFactor hcongr (P.classOf x) (P.classOf y)
  rw [hF x y, deltaFactor_classOf_classOf P hcongr x y]

theorem deltaFactor_no_factor_of_not_deltaCongruent
    (P : PrimitiveDifference α β) (hδ : ¬ P.DeltaCongruent) :
    ¬ (∃ F : P.ResidualQuotient → P.ResidualQuotient → β,
        ∀ x y : α, F (P.classOf x) (P.classOf y) = P.δ x y) := by
  intro h
  exact hδ ((deltaFactor_exists_iff_deltaCongruent P).mp h)

theorem deltaFactor_no_factor_of_zeroRel_ne
    (P : PrimitiveDifference α β)
    {x x' y y' : α}
    (hxx : P.ZeroRel x x') (hyy : P.ZeroRel y y')
    (hne : P.δ x y ≠ P.δ x' y') :
    ¬ (∃ F : P.ResidualQuotient → P.ResidualQuotient → β,
        ∀ x y : α, F (P.classOf x) (P.classOf y) = P.δ x y) := by
  intro h
  have hcongr : P.DeltaCongruent :=
    (deltaFactor_exists_iff_deltaCongruent P).mp h
  exact hne (hcongr x x' y y' hxx hyy)

def DeltaCongruentMod (P : PrimitiveDifference α β) (S : Setoid β) : Prop :=
  ∀ x x' y y' : α,
    P.ZeroRel x x' →
    P.ZeroRel y y' →
    S.r (P.δ x y) (P.δ x' y')

def deltaFactorMod
    (P : PrimitiveDifference α β) (S : Setoid β)
    (hcongr : P.DeltaCongruentMod S) :
    P.ResidualQuotient → P.ResidualQuotient → Quotient S :=
  Quotient.lift₂
    (s₁ := zeroSetoid P)
    (s₂ := zeroSetoid P)
    (fun x y => Quotient.mk S (P.δ x y))
    (by
      intro x y x' y' hx hy
      exact Quotient.sound (hcongr x x' y y' hx hy))

theorem deltaFactorMod_classOf_classOf
    (P : PrimitiveDifference α β) (S : Setoid β)
    (hcongr : P.DeltaCongruentMod S) (x y : α) :
    P.deltaFactorMod S hcongr (P.classOf x) (P.classOf y) =
      Quotient.mk S (P.δ x y) :=
  rfl

theorem deltaFactorMod_requires_congruence
    (P : PrimitiveDifference α β) (S : Setoid β)
    (F : P.ResidualQuotient → P.ResidualQuotient → Quotient S)
    (hF : ∀ x y : α,
      F (P.classOf x) (P.classOf y) = Quotient.mk S (P.δ x y)) :
    P.DeltaCongruentMod S := by
  intro x x' y y' hx hy
  apply Quotient.exact
  calc
    Quotient.mk S (P.δ x y) =
        F (P.classOf x) (P.classOf y) := (hF x y).symm
    _ = F (P.classOf x') (P.classOf y') := by
      rw [classOf_eq_of_zero P hx, classOf_eq_of_zero P hy]
    _ = Quotient.mk S (P.δ x' y') := hF x' y'

theorem deltaFactorMod_exists_iff_deltaCongruentMod
    (P : PrimitiveDifference α β) (S : Setoid β) :
    (∃ F : P.ResidualQuotient → P.ResidualQuotient → Quotient S,
        ∀ x y : α,
          F (P.classOf x) (P.classOf y) = Quotient.mk S (P.δ x y))
      ↔ P.DeltaCongruentMod S := by
  constructor
  · intro h
    rcases h with ⟨F, hF⟩
    exact deltaFactorMod_requires_congruence P S F hF
  · intro hcongr
    exact ⟨P.deltaFactorMod S hcongr,
      deltaFactorMod_classOf_classOf P S hcongr⟩

theorem deltaFactorMod_no_factor_of_not_deltaCongruentMod
    (P : PrimitiveDifference α β) (S : Setoid β)
    (hδ : ¬ P.DeltaCongruentMod S) :
    ¬ (∃ F : P.ResidualQuotient → P.ResidualQuotient → Quotient S,
        ∀ x y : α,
          F (P.classOf x) (P.classOf y) = Quotient.mk S (P.δ x y)) := by
  intro h
  exact hδ ((deltaFactorMod_exists_iff_deltaCongruentMod P S).mp h)

theorem deltaFactorMod_no_factor_of_zeroRel_not_rel
    (P : PrimitiveDifference α β) (S : Setoid β)
    {x x' y y' : α}
    (hxx : P.ZeroRel x x') (hyy : P.ZeroRel y y')
    (hne : ¬ S.r (P.δ x y) (P.δ x' y')) :
    ¬ (∃ F : P.ResidualQuotient → P.ResidualQuotient → Quotient S,
        ∀ x y : α,
          F (P.classOf x) (P.classOf y) = Quotient.mk S (P.δ x y)) := by
  intro h
  have hcongr : P.DeltaCongruentMod S :=
    (deltaFactorMod_exists_iff_deltaCongruentMod P S).mp h
  exact hne (hcongr x x' y y' hxx hyy)

def quotientMapOfSetoidImp
    (S T : Setoid γ) (hST : ∀ a b : γ, S.r a b → T.r a b) :
    Quotient S → Quotient T :=
  Quotient.lift
    (fun a => Quotient.mk T a)
    (by
      intro a b hab
      exact Quotient.sound (hST a b hab))

theorem quotientMapOfSetoidImp_mk
    (S T : Setoid γ) (hST : ∀ a b : γ, S.r a b → T.r a b)
    (a : γ) :
    quotientMapOfSetoidImp S T hST (Quotient.mk S a) = Quotient.mk T a :=
  rfl

theorem deltaCongruentMod_of_setoid_imp
    (P : PrimitiveDifference α β) (S T : Setoid β)
    (hST : ∀ a b : β, S.r a b → T.r a b)
    (hδ : P.DeltaCongruentMod S) :
    P.DeltaCongruentMod T := by
  intro x x' y y' hxx hyy
  exact hST (P.δ x y) (P.δ x' y') (hδ x x' y y' hxx hyy)

theorem deltaFactorMod_exists_of_setoid_imp
    (P : PrimitiveDifference α β) (S T : Setoid β)
    (hST : ∀ a b : β, S.r a b → T.r a b) :
    (∃ F : P.ResidualQuotient → P.ResidualQuotient → Quotient S,
        ∀ x y : α,
          F (P.classOf x) (P.classOf y) = Quotient.mk S (P.δ x y)) →
      ∃ F : P.ResidualQuotient → P.ResidualQuotient → Quotient T,
        ∀ x y : α,
          F (P.classOf x) (P.classOf y) = Quotient.mk T (P.δ x y) := by
  intro h
  rcases h with ⟨F, hF⟩
  exact
    ⟨fun q r => quotientMapOfSetoidImp S T hST (F q r),
      by
        intro x y
        change
          quotientMapOfSetoidImp S T hST
            (F (P.classOf x) (P.classOf y)) = Quotient.mk T (P.δ x y)
        rw [hF x y]
        exact quotientMapOfSetoidImp_mk S T hST (P.δ x y)⟩

def boolAllZeroNonconstant : PrimitiveDifference Bool Bool where
  δ := fun x _ => x
  Zero := fun _ => True
  zero_refl := by
    intro x
    exact True.intro
  zero_symm := by
    intro x y hxy
    exact True.intro
  zero_trans := by
    intro x y z hxy hyz
    exact True.intro

theorem boolAllZeroNonconstant_not_deltaCongruent :
    ¬ boolAllZeroNonconstant.DeltaCongruent := by
  intro hcongr
  have htf : true = false :=
    hcongr true false false false True.intro True.intro
  cases htf

theorem boolAllZeroNonconstant_no_factorization :
    ¬ (∃ F :
          boolAllZeroNonconstant.ResidualQuotient →
          boolAllZeroNonconstant.ResidualQuotient →
          Bool,
        ∀ x y : Bool,
          F (boolAllZeroNonconstant.classOf x)
            (boolAllZeroNonconstant.classOf y) =
          boolAllZeroNonconstant.δ x y) := by
  exact deltaFactor_no_factor_of_not_deltaCongruent
    boolAllZeroNonconstant boolAllZeroNonconstant_not_deltaCongruent

def InvariantCongruent (P : PrimitiveDifference α β) (φ : α → γ) : Prop :=
  ∀ x y : α, P.ZeroRel x y → φ x = φ y

def invariantFactor
    (P : PrimitiveDifference α β) (φ : α → γ)
    (hcongr : P.InvariantCongruent φ) :
    P.ResidualQuotient → γ :=
  Quotient.lift
    (s := zeroSetoid P)
    φ
    (by
      intro x y hxy
      exact hcongr x y hxy)

theorem invariantFactor_classOf
    (P : PrimitiveDifference α β) (φ : α → γ)
    (hcongr : P.InvariantCongruent φ) (x : α) :
    P.invariantFactor φ hcongr (P.classOf x) = φ x :=
  rfl

theorem invariantFactor_unique
    (P : PrimitiveDifference α β) (φ : α → γ)
    (hcongr : P.InvariantCongruent φ)
    (F : P.ResidualQuotient → γ)
    (hF : ∀ x : α, F (P.classOf x) = φ x) :
    F = P.invariantFactor φ hcongr := by
  funext q
  refine Quotient.inductionOn q ?_
  intro x
  change F (P.classOf x) = P.invariantFactor φ hcongr (P.classOf x)
  rw [hF x, invariantFactor_classOf P φ hcongr x]

theorem invariantFactor_requires_congruence
    (P : PrimitiveDifference α β) (φ : α → γ)
    (F : P.ResidualQuotient → γ)
    (hF : ∀ x : α, F (P.classOf x) = φ x) :
    P.InvariantCongruent φ := by
  intro x y hxy
  calc
    φ x = F (P.classOf x) := (hF x).symm
    _ = F (P.classOf y) := by
      rw [classOf_eq_of_zero P hxy]
    _ = φ y := hF y

theorem invariantFactor_exists_iff_invariantCongruent
    (P : PrimitiveDifference α β) (φ : α → γ) :
    (∃ F : P.ResidualQuotient → γ,
        ∀ x : α, F (P.classOf x) = φ x)
      ↔ P.InvariantCongruent φ := by
  constructor
  · intro h
    rcases h with ⟨F, hF⟩
    exact invariantFactor_requires_congruence P φ F hF
  · intro hcongr
    exact ⟨P.invariantFactor φ hcongr, invariantFactor_classOf P φ hcongr⟩

theorem invariantFactor_no_factor_of_not_invariant
    (P : PrimitiveDifference α β) (φ : α → γ)
    (hφ : ¬ P.InvariantCongruent φ) :
    ¬ (∃ F : P.ResidualQuotient → γ,
        ∀ x : α, F (P.classOf x) = φ x) := by
  intro h
  exact hφ ((invariantFactor_exists_iff_invariantCongruent P φ).mp h)

theorem invariantFactor_no_factor_of_zeroRel_ne
    (P : PrimitiveDifference α β) (φ : α → γ)
    {x y : α} (hxy : P.ZeroRel x y) (hne : φ x ≠ φ y) :
    ¬ (∃ F : P.ResidualQuotient → γ,
        ∀ x : α, F (P.classOf x) = φ x) := by
  intro h
  have hcongr : P.InvariantCongruent φ :=
    (invariantFactor_exists_iff_invariantCongruent P φ).mp h
  exact hne (hcongr x y hxy)

theorem invariantCongruent_pair_iff
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η) :
    P.InvariantCongruent (fun x : α => (φ x, ψ x)) ↔
      P.InvariantCongruent φ ∧ P.InvariantCongruent ψ := by
  constructor
  · intro h
    constructor
    · intro x y hxy
      exact congrArg Prod.fst (h x y hxy)
    · intro x y hxy
      exact congrArg Prod.snd (h x y hxy)
  · intro h x y hxy
    exact Prod.ext (h.1 x y hxy) (h.2 x y hxy)

theorem invariantFactor_pair_exists_iff
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η) :
    (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x))
      ↔ P.InvariantCongruent φ ∧ P.InvariantCongruent ψ :=
  (invariantFactor_exists_iff_invariantCongruent
    P (fun x : α => (φ x, ψ x))).trans
    (invariantCongruent_pair_iff P φ ψ)

theorem invariantFactor_pair_exists_iff_component_factors
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η) :
    (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x))
      ↔
        (∃ Fφ : P.ResidualQuotient → γ,
          ∀ x : α, Fφ (P.classOf x) = φ x) ∧
        (∃ Fψ : P.ResidualQuotient → η,
          ∀ x : α, Fψ (P.classOf x) = ψ x) := by
  constructor
  · intro h
    have hinv := (invariantFactor_pair_exists_iff P φ ψ).mp h
    exact
      ⟨(invariantFactor_exists_iff_invariantCongruent P φ).mpr hinv.1,
        (invariantFactor_exists_iff_invariantCongruent P ψ).mpr hinv.2⟩
  · intro h
    exact (invariantFactor_pair_exists_iff P φ ψ).mpr
      ⟨(invariantFactor_exists_iff_invariantCongruent P φ).mp h.1,
        (invariantFactor_exists_iff_invariantCongruent P ψ).mp h.2⟩

theorem invariantPair_no_factor_of_left_not_invariant
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (hφ : ¬ P.InvariantCongruent φ) :
    ¬ (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x)) := by
  intro h
  exact hφ ((invariantFactor_pair_exists_iff P φ ψ).mp h).1

theorem invariantPair_no_factor_of_right_not_invariant
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (hψ : ¬ P.InvariantCongruent ψ) :
    ¬ (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x)) := by
  intro h
  exact hψ ((invariantFactor_pair_exists_iff P φ ψ).mp h).2

theorem not_invariantCongruent_of_zeroRel_ne
    (P : PrimitiveDifference α β) (φ : α → γ)
    {x y : α} (hxy : P.ZeroRel x y) (hne : φ x ≠ φ y) :
    ¬ P.InvariantCongruent φ := by
  intro hcongr
  exact hne (hcongr x y hxy)

theorem localGreenGlobalRed_pair_obstruction
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (hφ : P.InvariantCongruent φ)
    (hψ : ¬ P.InvariantCongruent ψ) :
    (∃ F : P.ResidualQuotient → γ,
        ∀ x : α, F (P.classOf x) = φ x) ∧
      ¬ (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x)) := by
  constructor
  · exact (invariantFactor_exists_iff_invariantCongruent P φ).mpr hφ
  · exact invariantPair_no_factor_of_right_not_invariant P φ ψ hψ

theorem localGreenGlobalRed_pair_obstruction_of_witness
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (hφ : P.InvariantCongruent φ)
    {x y : α} (hxy : P.ZeroRel x y) (hne : ψ x ≠ ψ y) :
    (∃ F : P.ResidualQuotient → γ,
        ∀ x : α, F (P.classOf x) = φ x) ∧
      ¬ (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x)) := by
  exact localGreenGlobalRed_pair_obstruction P φ ψ hφ
    (not_invariantCongruent_of_zeroRel_ne P ψ hxy hne)

theorem localGreenGlobalRed_pair_witness_and_obstruction
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (hφ : P.InvariantCongruent φ)
    {x y : α} (hxy : P.ZeroRel x y) (hne : ψ x ≠ ψ y) :
    φ x = φ y ∧
      (φ x, ψ x) ≠ (φ y, ψ y) ∧
      (∃ F : P.ResidualQuotient → γ,
        ∀ x : α, F (P.classOf x) = φ x) ∧
      ¬ (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (φ x, ψ x)) := by
  refine ⟨hφ x y hxy, ?_, ?_⟩
  · intro hpair
    exact hne (congrArg Prod.snd hpair)
  · exact localGreenGlobalRed_pair_obstruction_of_witness P φ ψ hφ hxy hne

def contextFingerprintPD (κ : Type z) (φ : α → γ) :
    PrimitiveDifference (κ × α) Prop where
  δ := fun x y => φ x.2 = φ y.2
  Zero := fun h => h
  zero_refl := by
    intro x
    rfl
  zero_symm := by
    intro _ _ h
    exact h.symm
  zero_trans := by
    intro _ _ _ hxy hyz
    exact hxy.trans hyz

def contextLocal (φ : α → γ) (x : κ × α) : γ :=
  φ x.2

def contextGlobal (ψ : α → η) (x : κ × α) : η :=
  ψ x.2

theorem contextFingerprint_invariant (φ : α → γ) :
    (contextFingerprintPD κ φ).InvariantCongruent
      (contextLocal (κ := κ) φ) := by
  intro _ _ h
  exact h

theorem context_witness_zero_related
    (φ : α → γ) {x y : α} (c₀ c₁ : κ) (hφxy : φ x = φ y) :
    (contextFingerprintPD κ φ).ZeroRel (c₀, x) (c₁, y) :=
  hφxy

theorem context_global_differs
    (ψ : α → η) {x y : α} (c₀ c₁ : κ) (hne : ψ x ≠ ψ y) :
    contextGlobal (κ := κ) ψ (c₀, x) ≠
      contextGlobal (κ := κ) ψ (c₁, y) :=
  hne

theorem localGreenGlobalRed_context_obstruction_of_witness
    (φ : α → γ) (ψ : α → η)
    {x y : α} (c₀ c₁ : κ)
    (hφxy : φ x = φ y) (hne : ψ x ≠ ψ y) :
    (∃ F : (contextFingerprintPD κ φ).ResidualQuotient → γ,
        ∀ s : κ × α,
          F ((contextFingerprintPD κ φ).classOf s) =
            contextLocal (κ := κ) φ s) ∧
      ¬ (∃ F : (contextFingerprintPD κ φ).ResidualQuotient → γ × η,
        ∀ s : κ × α,
          F ((contextFingerprintPD κ φ).classOf s) =
            (contextLocal (κ := κ) φ s, contextGlobal (κ := κ) ψ s)) := by
  exact localGreenGlobalRed_pair_obstruction_of_witness
    (contextFingerprintPD κ φ)
    (contextLocal (κ := κ) φ)
    (contextGlobal (κ := κ) ψ)
    (contextFingerprint_invariant (κ := κ) φ)
    (context_witness_zero_related (κ := κ) φ c₀ c₁ hφxy)
    (context_global_differs (κ := κ) ψ c₀ c₁ hne)

def InvariantCongruentMod
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ) : Prop :=
  ∀ x y : α, P.ZeroRel x y → S.r (φ x) (φ y)

def invariantFactorMod
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ)
    (hcongr : P.InvariantCongruentMod φ S) :
    P.ResidualQuotient → Quotient S :=
  Quotient.lift
    (s := zeroSetoid P)
    (fun x => Quotient.mk S (φ x))
    (by
      intro x y hxy
      exact Quotient.sound (hcongr x y hxy))

theorem invariantFactorMod_classOf
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ)
    (hcongr : P.InvariantCongruentMod φ S) (x : α) :
    P.invariantFactorMod φ S hcongr (P.classOf x) =
      Quotient.mk S (φ x) :=
  rfl

theorem invariantFactorMod_requires_congruence
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ)
    (F : P.ResidualQuotient → Quotient S)
    (hF : ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x)) :
    P.InvariantCongruentMod φ S := by
  intro x y hxy
  apply Quotient.exact
  calc
    Quotient.mk S (φ x) = F (P.classOf x) := (hF x).symm
    _ = F (P.classOf y) := by
      rw [classOf_eq_of_zero P hxy]
    _ = Quotient.mk S (φ y) := hF y

theorem invariantFactorMod_exists_iff_invariantCongruentMod
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ) :
    (∃ F : P.ResidualQuotient → Quotient S,
        ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x))
      ↔ P.InvariantCongruentMod φ S := by
  constructor
  · intro h
    rcases h with ⟨F, hF⟩
    exact invariantFactorMod_requires_congruence P φ S F hF
  · intro hcongr
    exact ⟨P.invariantFactorMod φ S hcongr,
      invariantFactorMod_classOf P φ S hcongr⟩

theorem invariantFactorMod_no_factor_of_not_invariantCongruentMod
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ)
    (hφ : ¬ P.InvariantCongruentMod φ S) :
    ¬ (∃ F : P.ResidualQuotient → Quotient S,
        ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x)) := by
  intro h
  exact hφ ((invariantFactorMod_exists_iff_invariantCongruentMod P φ S).mp h)

theorem invariantFactorMod_no_factor_of_zeroRel_not_rel
    (P : PrimitiveDifference α β) (φ : α → γ) (S : Setoid γ)
    {x y : α} (hxy : P.ZeroRel x y) (hne : ¬ S.r (φ x) (φ y)) :
    ¬ (∃ F : P.ResidualQuotient → Quotient S,
        ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x)) := by
  intro h
  have hcongr : P.InvariantCongruentMod φ S :=
    (invariantFactorMod_exists_iff_invariantCongruentMod P φ S).mp h
  exact hne (hcongr x y hxy)

theorem invariantCongruentMod_of_setoid_imp
    (P : PrimitiveDifference α β) (φ : α → γ) (S T : Setoid γ)
    (hST : ∀ a b : γ, S.r a b → T.r a b)
    (hφ : P.InvariantCongruentMod φ S) :
    P.InvariantCongruentMod φ T := by
  intro x y hxy
  exact hST (φ x) (φ y) (hφ x y hxy)

theorem invariantFactorMod_exists_of_setoid_imp
    (P : PrimitiveDifference α β) (φ : α → γ) (S T : Setoid γ)
    (hST : ∀ a b : γ, S.r a b → T.r a b) :
    (∃ F : P.ResidualQuotient → Quotient S,
        ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x)) →
      ∃ F : P.ResidualQuotient → Quotient T,
        ∀ x : α, F (P.classOf x) = Quotient.mk T (φ x) := by
  intro h
  rcases h with ⟨F, hF⟩
  exact
    ⟨fun q => quotientMapOfSetoidImp S T hST (F q),
      by
        intro x
        change
          quotientMapOfSetoidImp S T hST (F (P.classOf x)) =
            Quotient.mk T (φ x)
        rw [hF x]
        exact quotientMapOfSetoidImp_mk S T hST (φ x)⟩

def productSetoid (S : Setoid γ) (T : Setoid η) : Setoid (γ × η) where
  r p q := S.r p.1 q.1 ∧ T.r p.2 q.2
  iseqv := by
    constructor
    · intro p
      exact ⟨S.refl p.1, T.refl p.2⟩
    · intro p q hpq
      exact ⟨S.symm hpq.1, T.symm hpq.2⟩
    · intro p q r hpq hqr
      exact ⟨S.trans hpq.1 hqr.1, T.trans hpq.2 hqr.2⟩

theorem invariantCongruentMod_pair_iff
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η) :
    P.InvariantCongruentMod (fun x : α => (φ x, ψ x)) (productSetoid S T)
      ↔ P.InvariantCongruentMod φ S ∧ P.InvariantCongruentMod ψ T := by
  constructor
  · intro h
    constructor
    · intro x y hxy
      exact (h x y hxy).1
    · intro x y hxy
      exact (h x y hxy).2
  · intro h x y hxy
    exact ⟨h.1 x y hxy, h.2 x y hxy⟩

theorem invariantFactorMod_pair_exists_iff
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η) :
    (∃ F : P.ResidualQuotient → Quotient (productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (productSetoid S T) (φ x, ψ x))
      ↔ P.InvariantCongruentMod φ S ∧ P.InvariantCongruentMod ψ T :=
  (invariantFactorMod_exists_iff_invariantCongruentMod
    P (fun x : α => (φ x, ψ x)) (productSetoid S T)).trans
    (invariantCongruentMod_pair_iff P φ ψ S T)

theorem invariantFactorMod_pair_exists_iff_component_factors
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η) :
    (∃ F : P.ResidualQuotient → Quotient (productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (productSetoid S T) (φ x, ψ x))
      ↔
        (∃ Fφ : P.ResidualQuotient → Quotient S,
          ∀ x : α, Fφ (P.classOf x) = Quotient.mk S (φ x)) ∧
        (∃ Fψ : P.ResidualQuotient → Quotient T,
          ∀ x : α, Fψ (P.classOf x) = Quotient.mk T (ψ x)) := by
  constructor
  · intro h
    have hinv := (invariantFactorMod_pair_exists_iff P φ ψ S T).mp h
    exact
      ⟨(invariantFactorMod_exists_iff_invariantCongruentMod P φ S).mpr hinv.1,
        (invariantFactorMod_exists_iff_invariantCongruentMod P ψ T).mpr hinv.2⟩
  · intro h
    exact (invariantFactorMod_pair_exists_iff P φ ψ S T).mpr
      ⟨(invariantFactorMod_exists_iff_invariantCongruentMod P φ S).mp h.1,
        (invariantFactorMod_exists_iff_invariantCongruentMod P ψ T).mp h.2⟩

theorem invariantPairMod_no_factor_of_left_not_invariantCongruentMod
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η)
    (hφ : ¬ P.InvariantCongruentMod φ S) :
    ¬ (∃ F : P.ResidualQuotient → Quotient (productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (productSetoid S T) (φ x, ψ x)) := by
  intro h
  exact hφ ((invariantFactorMod_pair_exists_iff P φ ψ S T).mp h).1

theorem invariantPairMod_no_factor_of_right_not_invariantCongruentMod
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η)
    (hψ : ¬ P.InvariantCongruentMod ψ T) :
    ¬ (∃ F : P.ResidualQuotient → Quotient (productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (productSetoid S T) (φ x, ψ x)) := by
  intro h
  exact hψ ((invariantFactorMod_pair_exists_iff P φ ψ S T).mp h).2

theorem localGreenGlobalRed_pair_mod_obstruction
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η)
    (hφ : P.InvariantCongruentMod φ S)
    (hψ : ¬ P.InvariantCongruentMod ψ T) :
    (∃ F : P.ResidualQuotient → Quotient S,
        ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x)) ∧
      ¬ (∃ F : P.ResidualQuotient → Quotient (productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (productSetoid S T) (φ x, ψ x)) := by
  constructor
  · exact (invariantFactorMod_exists_iff_invariantCongruentMod P φ S).mpr hφ
  · exact invariantPairMod_no_factor_of_right_not_invariantCongruentMod
      P φ ψ S T hψ

theorem localGreenGlobalRed_pair_mod_obstruction_of_witness
    (P : PrimitiveDifference α β) (φ : α → γ) (ψ : α → η)
    (S : Setoid γ) (T : Setoid η)
    (hφ : P.InvariantCongruentMod φ S)
    {x y : α} (hxy : P.ZeroRel x y) (hne : ¬ T.r (ψ x) (ψ y)) :
    (∃ F : P.ResidualQuotient → Quotient S,
        ∀ x : α, F (P.classOf x) = Quotient.mk S (φ x)) ∧
      ¬ (∃ F : P.ResidualQuotient → Quotient (productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (productSetoid S T) (φ x, ψ x)) := by
  exact localGreenGlobalRed_pair_mod_obstruction P φ ψ S T hφ
    (by
      intro hψ
      exact hne (hψ x y hxy))

theorem boolAllZeroNonconstant_classifier_not_invariantCongruent :
    ¬ boolAllZeroNonconstant.InvariantCongruent (fun x : Bool => x) := by
  intro hcongr
  have htf : true = false :=
    hcongr true false True.intro
  cases htf

theorem boolAllZeroNonconstant_no_invariant_factorization :
    ¬ (∃ F : boolAllZeroNonconstant.ResidualQuotient → Bool,
        ∀ x : Bool,
          F (boolAllZeroNonconstant.classOf x) = x) := by
  intro h
  rcases h with ⟨F, hF⟩
  exact boolAllZeroNonconstant_classifier_not_invariantCongruent
    (invariantFactor_requires_congruence
      boolAllZeroNonconstant (fun x : Bool => x) F hF)

end PrimitiveDifference

structure QuotientCompatiblePrimitiveDifference (α : Type u) (β : Type v)
    extends PrimitiveDifference α β where
  delta_congr : toPrimitiveDifference.DeltaCongruent

structure PointedPrimitiveDifference (α : Type u) (β : Type v)
    extends PrimitiveDifference α β where
  zero : α

namespace PointedPrimitiveDifference

variable {α : Type u} {β : Type v}

def zeroClass (P : PointedPrimitiveDifference α β) :
    PrimitiveDifference.ResidualQuotient P.toPrimitiveDifference :=
  PrimitiveDifference.classOf P.toPrimitiveDifference P.zero

def IsZeroClass
    (P : PointedPrimitiveDifference α β)
    (q : PrimitiveDifference.ResidualQuotient P.toPrimitiveDifference) : Prop :=
  q = P.zeroClass

end PointedPrimitiveDifference

/-! ## Phase Fiber Interference & Non-L1 Residual Mass (QM_060/QM_061) -/

/-- Primitive Difference for Phase Fiber Interference:
    Compares the L1 diagonal mass sum `w1 + w2` with the superposed norm `|w1 + w2 + Δ_int|`. -/
def interferencePrimitiveDifference (w1 w2 delta_int : Int) : Int :=
  (w1 + w2 + delta_int) - (w1 + w2)

@[simp]
theorem interferencePrimitiveDifference_eq (w1 w2 delta_int : Int) :
    interferencePrimitiveDifference w1 w2 delta_int = delta_int := by
  dsimp [interferencePrimitiveDifference]
  omega

/-- `interferencePrimitiveDifference w1 w2 d = d`, so it is non-zero exactly when `d` is.

    Named for where it is used, not for what it proves: this is the identity
    function on `d`. It does not show that diagonal L1 data cannot carry phase
    interference -- that is an argument about the model, made elsewhere. -/
theorem interference_nonzero_of_delta_nonzero (w1 w2 delta_int : Int) (h : delta_int ≠ 0) :
    interferencePrimitiveDifference w1 w2 delta_int ≠ 0 := by
  simpa using h

/-! ## Product Non-Factorization & Separability Primitive Difference (QM_070/QM_071) -/

/-- Bipartite product defect Primitive Difference:
    δ_prod = w(a,b) - (margA(a) * margB(b) / W). -/
def productDefectPrimitiveDifference (w_ab marg_a marg_b total : Int) : Int :=
  w_ab * total - marg_a * marg_b

/-- The bipartite defect `w_ab * total - marg_a * marg_b` is non-zero exactly
    when `w_ab * total ≠ marg_a * marg_b`. Integer subtraction; the content is in
    choosing that expression as the defect, not in this lemma. -/
theorem product_defect_nonzero_of_nonfactor (w_ab marg_a marg_b total : Int)
    (h : w_ab * total ≠ marg_a * marg_b) :
    productDefectPrimitiveDifference w_ab marg_a marg_b total ≠ 0 := by
  dsimp [productDefectPrimitiveDifference]
  omega

/-! ## Mermin-Peres Contextuality Primitive Difference (QM_120/QM_121) -/

/-- Parity cochain contextuality Primitive Difference:
    Compares local context products (+1) with global parity closure (-1). -/
def contextualityPrimitiveDifference (local_prod global_target : Int) : Int :=
  local_prod - global_target

/-- `local_prod - global_target ≠ 0` given `local_prod ≠ global_target`.

    Over `Int`, for any two values. It is not about contextuality: nothing here
    constrains the products to be parity closures, and no Kochen-Specker-style
    obstruction is derived. -/
theorem contextuality_nonzero_of_parity_failure (local_prod global_target : Int)
    (h : local_prod ≠ global_target) :
    contextualityPrimitiveDifference local_prod global_target ≠ 0 := by
  dsimp [contextualityPrimitiveDifference]
  omega

/-! ## CPTP Trace-Norm & Dual Witness Primitive Difference (QM_080/QM_081) -/

/-- CPTP trace-norm defect Primitive Difference:
    Compares local trace distance gauge ||ρ - σ||_tr with CPTP contracted image ||E(ρ) - E(σ)||_tr. -/
def cptpTraceNormPrimitiveDifference (dist_orig dist_cptp : Int) : Int :=
  dist_orig - dist_cptp

/-- `dist_orig - dist_cptp ≠ 0` given `dist_orig > dist_cptp`.

    Integer inequality. Nothing here is a CPTP map, a trace norm, or a
    contraction theorem; the names are labels on two integers. -/
theorem cptp_trace_norm_nonzero_of_residual (dist_orig dist_cptp : Int)
    (h : dist_orig > dist_cptp) :
    cptpTraceNormPrimitiveDifference dist_orig dist_cptp ≠ 0 := by
  dsimp [cptpTraceNormPrimitiveDifference]
  omega

/-! ## LQG & GR Kinematical Holonomy Curvature Primitive Difference (QM_110/QM_111) -/

/-- Non-abelian closed-loop holonomy Primitive Difference:
    Compares flat gauge Wilson loop (+1) with non-abelian commutator curvature (-1 for Q8 plaquette). -/
def holonomyCurvaturePrimitiveDifference (flat_hol nonabelian_hol : Int) : Int :=
  flat_hol - nonabelian_hol

/-- `flat_hol - nonabelian_hol ≠ 0` given the two differ.

    Integer subtraction. No holonomy is computed, no curvature is defined, and
    the Q8 commutator is mentioned nowhere in the statement. -/
theorem holonomy_curvature_nonzero_of_nonabelian (flat_hol nonabelian_hol : Int)
    (h : flat_hol ≠ nonabelian_hol) :
    holonomyCurvaturePrimitiveDifference flat_hol nonabelian_hol ≠ 0 := by
  dsimp [holonomyCurvaturePrimitiveDifference]
  omega

/-! ## Authority Non-Promotion & Interpretation Shadow Primitive Difference (QM_090/QM_092) -/

/-- Authority non-promotion defect Primitive Difference:
    Compares formally derived structure score with unsealed authority status. -/
def authorityNonPromotionPrimitiveDifference (derived_score auth_sealed : Int) : Int :=
  derived_score - auth_sealed

/-- `derived_score - auth_sealed ≠ 0` given the two differ.

    This does not prove `StructureDerived ⊬ IsAuth`. That is a statement about a
    derivability relation between judgements; this is a subtraction of two
    integers, and the firewall it is named for is a policy, argued in prose. -/
theorem authority_non_promotion_nonzero_of_unsealed (derived_score auth_sealed : Int)
    (h : derived_score ≠ auth_sealed) :
    authorityNonPromotionPrimitiveDifference derived_score auth_sealed ≠ 0 := by
  dsimp [authorityNonPromotionPrimitiveDifference]
  omega

/-! ## Gell-Mann--Hartle Decoherence Primitive Difference (QM_043) -/

/-- Gell-Mann--Hartle two-history integer residual. It compares a declared
global integer weight with a local diagonal integer weight; no probability,
positivity, or normalization structure is encoded. -/
def gellMannDecoherencePrimitiveDifference (total_prob diag_sum : Int) : Int :=
  total_prob - diag_sum

/-- The two-history integer presentation makes the decoherence residual exactly
`2 * D12`: the global total differs from the locally visible diagonal sum only
by the off-diagonal interference contribution. -/
theorem gellMannDecoherencePrimitiveDifference_eq_offdiagonal
    (d11 d12 d22 : Int) :
    gellMannDecoherencePrimitiveDifference
        (d11 + d22 + 2 * d12) (d11 + d22) =
      2 * d12 := by
  dsimp [gellMannDecoherencePrimitiveDifference]
  omega

/-- The two-history residual vanishes exactly when the off-diagonal integer
coordinate vanishes. -/
theorem gellMannDecoherencePrimitiveDifference_eq_zero_iff
    (d11 d12 d22 : Int) :
    gellMannDecoherencePrimitiveDifference
        (d11 + d22 + 2 * d12) (d11 + d22) = 0 ↔
      d12 = 0 := by
  constructor
  · intro h
    rw [gellMannDecoherencePrimitiveDifference_eq_offdiagonal] at h
    omega
  · intro h
    rw [gellMannDecoherencePrimitiveDifference_eq_offdiagonal]
    omega

/-- The two-history residual is nonzero exactly when the off-diagonal integer
coordinate is nonzero. -/
theorem gellMannDecoherencePrimitiveDifference_ne_zero_iff
    (d11 d12 d22 : Int) :
    gellMannDecoherencePrimitiveDifference
        (d11 + d22 + 2 * d12) (d11 + d22) ≠ 0 ↔
      d12 ≠ 0 := by
  constructor
  · intro hres hd12
    apply hres
    exact (gellMannDecoherencePrimitiveDifference_eq_zero_iff d11 d12 d22).2 hd12
  · intro hd12 hres
    apply hd12
    exact (gellMannDecoherencePrimitiveDifference_eq_zero_iff d11 d12 d22).1 hres

/-- Generic nonzero residual theorem. When global and local integer weights
differ, their Primitive Difference is nonzero. -/
theorem decoherence_nonzero_of_offdiagonal (total_prob diag_sum : Int)
    (h : total_prob ≠ diag_sum) :
    gellMannDecoherencePrimitiveDifference total_prob diag_sum ≠ 0 := by
  dsimp [gellMannDecoherencePrimitiveDifference]
  omega

/-- A nonzero off-diagonal coordinate makes the two-history integer Primitive
Difference nonzero. -/
theorem decoherence_nonzero_of_offdiagonal_weight
    (d11 d12 d22 : Int) (h : d12 ≠ 0) :
    gellMannDecoherencePrimitiveDifference
        (d11 + d22 + 2 * d12) (d11 + d22) ≠ 0 := by
  dsimp [gellMannDecoherencePrimitiveDifference]
  omega

/-! ## Fault-Tolerance Threshold Repair Capacity Primitive Difference (QM_100/QM_101/QM_102) -/

/-- Threshold repair capacity defect Primitive Difference:
    Compares physical defect error count with unabsorbed logical pairing residual. -/
def thresholdRepairCapacityPrimitiveDifference (physical_defects repair_absorbed : Int) : Int :=
  physical_defects - repair_absorbed

/-- `physical_defects - repair_absorbed ≠ 0` given the first exceeds the second.

    Integer inequality. No syndrome, no repair image `B^1`, and no threshold
    result appears in the statement; those live in the prose that names it. -/
theorem threshold_repair_nonzero_of_unabsorbed (physical_defects repair_absorbed : Int)
    (h : physical_defects > repair_absorbed) :
    thresholdRepairCapacityPrimitiveDifference physical_defects repair_absorbed ≠ 0 := by
  dsimp [thresholdRepairCapacityPrimitiveDifference]
  omega

/-! ## Classical Limit Cochain Projection Primitive Difference (QM_112) -/

/-- Classical limit cochain projection defect Primitive Difference:
    Compares full U(1) phase fiber 1-cochain state with classical stationary 0-cochain projection. -/
def classicalLimitPrimitiveDifference (phase_state classical_proj : Int) : Int :=
  phase_state - classical_proj

/-- `phase_state - classical_proj ≠ 0` given the two differ.

    Integer subtraction. It is not a classical-limit theorem: no limit is taken,
    and neither argument is constrained to be a phase or a projection. -/
theorem classical_limit_nonzero_of_unprojected (phase_state classical_proj : Int)
    (h : phase_state ≠ classical_proj) :
    classicalLimitPrimitiveDifference phase_state classical_proj ≠ 0 := by
  dsimp [classicalLimitPrimitiveDifference]
  omega

end OmegaCore

/- ------------------------------------------------------------------
   Merged from derive_genesis_foundational_docs (PR #203).
   These six declarations are disjoint from the OmegaCore /
   PointedPrimitiveDifference material above; the merge keeps both.
   ------------------------------------------------------------------ -/

-- Primitive Difference for Finite Quantum Carriers in Lean 4

namespace PrimitiveDifference

/-- Primitive difference operator D(x, y) := y - x on discrete integer coordinates. -/
def diff (x y : Int) : Int :=
  y - x

/-- Sameness relation certified by vanishing primitive difference. -/
def isSame (x y : Int) : Prop :=
  diff x y = 0

/-- Sameness is reflexive: identical coordinates yield zero primitive difference. -/
theorem diff_self (x : Int) : diff x x = 0 := by
  dsimp [diff]
  omega

/-- Primitive difference certifies sameness: zero difference holds if and only if coordinates are equal. -/
theorem same_iff_eq (x y : Int) : isSame x y ↔ x = y := by
  dsimp [isSame, diff]
  constructor
  · intro h
    omega
  · intro h
    omega

/-- Primitive difference is strictly antisymmetric: D(x, y) = - D(y, x). -/
theorem diff_antisymm (x y : Int) : diff x y = - diff y x := by
  dsimp [diff]
  omega

/-- 1-cocycle identity on discrete 0-simplexes: D(x, y) + D(y, z) = D(x, z). -/
theorem diff_cocycle (x y z : Int) : diff x y + diff y z = diff x z := by
  dsimp [diff]
  omega

#print axioms diff_self
#print axioms same_iff_eq
#print axioms diff_antisymm
#print axioms diff_cocycle

end PrimitiveDifference
