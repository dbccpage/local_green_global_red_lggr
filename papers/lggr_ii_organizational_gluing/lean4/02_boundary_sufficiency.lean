/-!
# Core L023-02: Boundary Sufficiency Audit and Factorization Equivalence

Mechanizes Lemma 4.4: Weak boundary sufficiency (the boundary representation
recovering the global outcome E_G) plus authority closure and temporal coherence does
not force evaluator factorization E_G = E_1 * E_2.

Also mechanizes the equivalence between product-sufficiency and evaluator factorization.
-/

namespace PaperAE005

structure BooleanBoundary where
  e1 : Bool
  e2 : Bool
  eG : Bool
  rep : Bool × Bool × Bool
  gAuth : Bool
  gTime : Bool
  deriving DecidableEq, Repr

def weakBoundarySufficiency (b : BooleanBoundary) : Prop :=
  b.rep.2.2 = b.eG

def evaluatorFactorization (b : BooleanBoundary) : Prop :=
  b.eG = (b.e1 && b.e2)

theorem weak_boundary_sufficiency_does_not_force_factorization :
    ∃ b : BooleanBoundary,
      weakBoundarySufficiency b ∧
      b.gAuth = true ∧
      b.gTime = true ∧
      ¬ evaluatorFactorization b := by
  refine ⟨⟨true, true, false, (true, true, false), true, true⟩, ?_⟩
  dsimp [weakBoundarySufficiency, evaluatorFactorization]
  decide

def productSufficiency (b : BooleanBoundary) : Prop :=
  b.rep.2.2 = (b.e1 && b.e2)

theorem product_sufficiency_iff_evaluator_factorization (b : BooleanBoundary)
    (h_rec : weakBoundarySufficiency b) :
    productSufficiency b ↔ evaluatorFactorization b := by
  dsimp [weakBoundarySufficiency] at h_rec
  dsimp [productSufficiency, evaluatorFactorization]
  rw [h_rec]

end PaperAE005
