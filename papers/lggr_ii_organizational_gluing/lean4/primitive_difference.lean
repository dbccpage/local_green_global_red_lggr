/-!
The quotient fragment used by the carrier-mixing theorem.

`ZeroRel` is supplied as data and proved to be an equivalence relation. The
paper uses only the quotient and the fact that zero-related representatives
have equal quotient classes.
-/

namespace OmegaCore

universe u v

structure PrimitiveDifference (α : Type u) (β : Type v) where
  δ : α → α → β
  Zero : β → Prop
  zero_refl : ∀ x, Zero (δ x x)
  zero_symm : ∀ x y, Zero (δ x y) → Zero (δ y x)
  zero_trans : ∀ x y z, Zero (δ x y) → Zero (δ y z) → Zero (δ x z)

namespace PrimitiveDifference

variable {α : Type u} {β : Type v}

def ZeroRel (P : PrimitiveDifference α β) (x y : α) : Prop :=
  P.Zero (P.δ x y)

theorem zeroRel_equivalence (P : PrimitiveDifference α β) :
    Equivalence P.ZeroRel where
  refl := P.zero_refl
  symm := P.zero_symm _ _
  trans := P.zero_trans _ _ _

def zeroSetoid (P : PrimitiveDifference α β) : Setoid α where
  r := P.ZeroRel
  iseqv := P.zeroRel_equivalence

def ResidualQuotient (P : PrimitiveDifference α β) : Type u :=
  Quotient P.zeroSetoid

def classOf (P : PrimitiveDifference α β) (x : α) : P.ResidualQuotient :=
  Quotient.mk P.zeroSetoid x

theorem classOf_eq_of_zero
    (P : PrimitiveDifference α β) {x y : α} (h : P.ZeroRel x y) :
    P.classOf x = P.classOf y :=
  Quotient.sound h

end PrimitiveDifference
end OmegaCore
