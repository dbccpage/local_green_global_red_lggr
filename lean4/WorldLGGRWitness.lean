import PrimitiveDifference

/-!
# Reusable Local-Green / Global-Red witnesses

This module wraps the shared-kernel pair-obstruction theorems in two
proof-carrying type classes.  The exact class uses equality in the observer
codomains.  The modulo class uses explicitly supplied setoids.

Type-class resolution only assembles a result after a witness instance has
already supplied two source points, their source `ZeroRel` proof, local
congruence, and global separation.  This module provides no generic instance,
enumerator, decision procedure, or search over arbitrary carriers.  Its only
instances are the concrete Bool regressions below.

The primitive-difference notation is not parsed or derived here; the module
imports the typed `PrimitiveDifference` structure.  No authority transition is
claimed.
-/

namespace OmegaWorld
namespace LGGRWitness

open OmegaCore

universe u v w

/--
Exact LGGR evidence: the local observer respects the declared source
`ZeroRel`, while one zero-related pair is separated by the global observer.
-/
class ExactLGGRWitness
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η) where
  left : α
  right : α
  sourceZeroRelated : P.ZeroRel left right
  localCongruent : P.InvariantCongruent diagnostic
  globalSeparated : global left ≠ global right

/-- The complete exact witness and factorization obstruction. -/
structure ExactLGGRResult
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η) where
  left : α
  right : α
  sourceZeroRelated : P.ZeroRel left right
  localEqual : diagnostic left = diagnostic right
  globalUnequal : global left ≠ global right
  pairUnequal :
    (diagnostic left, global left) ≠ (diagnostic right, global right)
  localFactor :
    ∃ F : P.ResidualQuotient → γ,
      ∀ x : α, F (P.classOf x) = diagnostic x
  pairDoesNotFactor :
    ¬ (∃ F : P.ResidualQuotient → γ × η,
      ∀ x : α, F (P.classOf x) = (diagnostic x, global x))

/--
One-line exact proof surface: `by exact exactLGGRFromInstance` works whenever
the surrounding scope contains an `ExactLGGRWitness` instance.
-/
def exactLGGRFromInstance
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η)
    [witness : ExactLGGRWitness P diagnostic global] :
    ExactLGGRResult P diagnostic global := by
  have obstruction :=
    PrimitiveDifference.localGreenGlobalRed_pair_witness_and_obstruction
      P diagnostic global witness.localCongruent witness.sourceZeroRelated
        witness.globalSeparated
  exact
    { left := witness.left
      right := witness.right
      sourceZeroRelated := witness.sourceZeroRelated
      localEqual := obstruction.1
      globalUnequal := witness.globalSeparated
      pairUnequal := obstruction.2.1
      localFactor := obstruction.2.2.1
      pairDoesNotFactor := obstruction.2.2.2 }

/--
Classical proposition-level alternative: a locally congruent diagnostic either
pairs with the global observer through the quotient, or a zero-related LGGR
pair exists.  This is not an executable branch decision or witness search.
-/
theorem exactPairFactorOrLGGRWitness
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η)
    (diagnosticCongruent : P.InvariantCongruent diagnostic) :
    (∃ F : P.ResidualQuotient → γ × η,
        ∀ x : α, F (P.classOf x) = (diagnostic x, global x)) ∨
      ∃ left right : α,
        P.ZeroRel left right ∧
          diagnostic left = diagnostic right ∧
          global left ≠ global right := by
  classical
  by_cases globalCongruent : P.InvariantCongruent global
  · left
    exact (PrimitiveDifference.invariantFactor_pair_exists_iff
      P diagnostic global).2 ⟨diagnosticCongruent, globalCongruent⟩
  · right
    apply Classical.byContradiction
    intro noWitness
    apply globalCongruent
    intro left right sourceZeroRelated
    apply Classical.byContradiction
    intro globalSeparated
    exact noWitness
      ⟨left, right, sourceZeroRelated,
        diagnosticCongruent left right sourceZeroRelated,
        globalSeparated⟩

/--
Setoid-modulo LGGR evidence.  Local agreement is measured by `S`; global
separation is failure of the independently declared relation `T`.
-/
class SetoidLGGRWitness
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η)
    (S : Setoid γ) (T : Setoid η) where
  left : α
  right : α
  sourceZeroRelated : P.ZeroRel left right
  localCongruent : P.InvariantCongruentMod diagnostic S
  globalSeparated : ¬ T.r (global left) (global right)

/-- The complete setoid-modulo witness and quotient-factor obstruction. -/
structure SetoidLGGRResult
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η)
    (S : Setoid γ) (T : Setoid η) where
  left : α
  right : α
  sourceZeroRelated : P.ZeroRel left right
  localRelated : S.r (diagnostic left) (diagnostic right)
  globalNotRelated : ¬ T.r (global left) (global right)
  localFactor :
    ∃ F : P.ResidualQuotient → Quotient S,
      ∀ x : α, F (P.classOf x) = Quotient.mk S (diagnostic x)
  pairDoesNotFactor :
    ¬ (∃ F : P.ResidualQuotient →
          Quotient (PrimitiveDifference.productSetoid S T),
      ∀ x : α,
        F (P.classOf x) =
          Quotient.mk (PrimitiveDifference.productSetoid S T)
            (diagnostic x, global x))

/--
One-line modulo proof surface: `by exact setoidLGGRFromInstance` works only
after an explicit `SetoidLGGRWitness` instance has supplied the evidence.
-/
def setoidLGGRFromInstance
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η)
    (S : Setoid γ) (T : Setoid η)
    [witness : SetoidLGGRWitness P diagnostic global S T] :
    SetoidLGGRResult P diagnostic global S T := by
  have obstruction :=
    PrimitiveDifference.localGreenGlobalRed_pair_mod_obstruction_of_witness
      P diagnostic global S T witness.localCongruent witness.sourceZeroRelated
        witness.globalSeparated
  exact
    { left := witness.left
      right := witness.right
      sourceZeroRelated := witness.sourceZeroRelated
      localRelated :=
        witness.localCongruent witness.left witness.right
          witness.sourceZeroRelated
      globalNotRelated := witness.globalSeparated
      localFactor := obstruction.1
      pairDoesNotFactor := obstruction.2 }

/--
Setoid-modulo factor-or-witness alternative.  As above, classical excluded
middle proves the proposition but supplies no executable infinite-carrier
search procedure and installs no type-class instance.
-/
theorem setoidPairFactorOrLGGRWitness
    {α : Type u} {β : Type v} {γ η : Type w}
    (P : PrimitiveDifference α β) (diagnostic : α → γ) (global : α → η)
    (S : Setoid γ) (T : Setoid η)
    (diagnosticCongruent : P.InvariantCongruentMod diagnostic S) :
    (∃ F : P.ResidualQuotient →
          Quotient (PrimitiveDifference.productSetoid S T),
        ∀ x : α,
          F (P.classOf x) =
            Quotient.mk (PrimitiveDifference.productSetoid S T)
              (diagnostic x, global x)) ∨
      ∃ left right : α,
        P.ZeroRel left right ∧
          S.r (diagnostic left) (diagnostic right) ∧
          ¬ T.r (global left) (global right) := by
  classical
  by_cases globalCongruent : P.InvariantCongruentMod global T
  · left
    exact (PrimitiveDifference.invariantFactorMod_pair_exists_iff
      P diagnostic global S T).2 ⟨diagnosticCongruent, globalCongruent⟩
  · right
    apply Classical.byContradiction
    intro noWitness
    apply globalCongruent
    intro left right sourceZeroRelated
    apply Classical.byContradiction
    intro globalSeparated
    exact noWitness
      ⟨left, right, sourceZeroRelated,
        diagnosticCongruent left right sourceZeroRelated,
        globalSeparated⟩

/-- Equality presented explicitly as a setoid for modulo regression tests. -/
def equalitySetoid (α : Type u) : Setoid α where
  r := Eq
  iseqv := by
    constructor
    · intro x
      rfl
    · intro x y hxy
      exact hxy.symm
    · intro x y z hxy hyz
      exact hxy.trans hyz

/-- A local diagnostic that deliberately forgets its Bool input. -/
def boolLocal (_input : Bool) : Bool := false

/-- The globally visible Bool coordinate. -/
def boolGlobal (input : Bool) : Bool := input

/-- Concrete exact LGGR evidence on the shared-kernel Bool fixture. -/
instance boolExactLGGRWitness :
    ExactLGGRWitness
      PrimitiveDifference.boolAllZeroNonconstant boolLocal boolGlobal where
  left := true
  right := false
  sourceZeroRelated := True.intro
  localCongruent := by
    intro _left _right _zeroRelated
    rfl
  globalSeparated := by
    decide

/-- The exact Bool regression uses the one-line type-class proof surface. -/
def boolExactLGGRRegression :
    ExactLGGRResult
      PrimitiveDifference.boolAllZeroNonconstant boolLocal boolGlobal := by
  exact exactLGGRFromInstance _ _ _

/-- Concrete equality-setoid LGGR evidence on the same Bool fixture. -/
instance boolSetoidLGGRWitness :
    SetoidLGGRWitness
      PrimitiveDifference.boolAllZeroNonconstant boolLocal boolGlobal
      (equalitySetoid Bool) (equalitySetoid Bool) where
  left := true
  right := false
  sourceZeroRelated := True.intro
  localCongruent := by
    intro _left _right _zeroRelated
    rfl
  globalSeparated := by
    change true ≠ false
    decide

/-- The modulo Bool regression also closes through one type-class-driven line. -/
def boolSetoidLGGRRegression :
    SetoidLGGRResult
      PrimitiveDifference.boolAllZeroNonconstant boolLocal boolGlobal
      (equalitySetoid Bool) (equalitySetoid Bool) := by
  exact setoidLGGRFromInstance _ _ _ _ _

/-- Local scope metadata; this is a checked snapshot, not non-derivability. -/
inductive AuthorityEffect where
  | none
deriving DecidableEq, Repr

structure ScopeBoundary where
  importsOnlyTypedPrimitiveDifference : Bool
  parsesPrimitiveGlyph : Bool
  derivesPrimitiveGlyph : Bool
  genericExactWitnessInstanceProvided : Bool
  genericSetoidWitnessInstanceProvided : Bool
  arbitraryInfiniteCarrierSearchClaimed : Bool
  authorityEffect : AuthorityEffect
deriving DecidableEq, Repr

def scopeBoundary : ScopeBoundary :=
  { importsOnlyTypedPrimitiveDifference := true
    parsesPrimitiveGlyph := false
    derivesPrimitiveGlyph := false
    genericExactWitnessInstanceProvided := false
    genericSetoidWitnessInstanceProvided := false
    arbitraryInfiniteCarrierSearchClaimed := false
    authorityEffect := .none }

theorem scope_boundary_snapshot :
    scopeBoundary.importsOnlyTypedPrimitiveDifference = true ∧
      scopeBoundary.parsesPrimitiveGlyph = false ∧
      scopeBoundary.derivesPrimitiveGlyph = false ∧
      scopeBoundary.genericExactWitnessInstanceProvided = false ∧
      scopeBoundary.genericSetoidWitnessInstanceProvided = false ∧
      scopeBoundary.arbitraryInfiniteCarrierSearchClaimed = false ∧
      scopeBoundary.authorityEffect = .none := by
  decide

#print axioms exactLGGRFromInstance
#print axioms exactPairFactorOrLGGRWitness
#print axioms setoidLGGRFromInstance
#print axioms setoidPairFactorOrLGGRWitness
#print axioms boolExactLGGRRegression
#print axioms boolSetoidLGGRRegression
#print axioms scope_boundary_snapshot

end LGGRWitness
end OmegaWorld
