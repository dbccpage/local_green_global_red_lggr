/-
Paper 020, Tier 2c: mechanization of the set-isomorphism hypothesis G1.

This module formalizes Condition G1 directly as a certified type equivalence
(bijection) between the space of full paths and the disjoint union of Cartesian
products of boundary segments:

    Ω(S_a, S_c) ≅ ⨆_{S_b ∈ B} Ω(S_b, S_c) × Ω(S_a, S_b)

It proves:
1. The abstract set-isomorphism G1 as an `Equiv` structure with left and right
   inverses (retraction and section).
2. The finite kernel composition theorem on raw flat path lists generated from
   boundary segments, without requiring pre-decomposed row-list data structures.
-/

import «03_kernel_composition»
import «03b_product_of_sums»

namespace PaperAE004

/-- Explicit type-level equivalence (bijection) between types α and β. -/
structure Equiv (α : Type u) (β : Type v) where
  toFun : α → β
  invFun : β → α
  left_inv : ∀ a, invFun (toFun a) = a
  right_inv : ∀ b, toFun (invFun b) = b

infixl:25 " ≃ " => Equiv

/-- Structural condition G1: unique intermediate boundary-slice decomposition.
    Given a state space, intermediate boundary slice, and path spaces,
    every full path decomposes uniquely into a boundary witness and a pair of
    boundary-anchored segments, and conversely every such pair concatenates to
    a full path. -/
structure G1_BoundarySliceDecomposition
    (State Boundary : Type)
    (toState : Boundary → State)
    (a c : State)
    (Path : State → State → Type) where
  concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c
  split : Path a c → (b : Boundary) × (Path (toState b) c × Path a (toState b))
  split_concat : ∀ (b : Boundary) (γ₂ : Path (toState b) c) (γ₁ : Path a (toState b)),
    split (concat γ₂ γ₁) = ⟨b, (γ₂, γ₁)⟩
  concat_split : ∀ (γ : Path a c),
    let d := split γ
    concat d.2.1 d.2.2 = γ

/-- Theorem G1: The set-isomorphism hypothesis G1 induces a certified type equivalence
    between the full path space Ω(S_a, S_c) and the dependent sum (disjoint union)
    over boundary states S_b ∈ B of the Cartesian products Ω(S_b, S_c) × Ω(S_a, S_b). -/
def g1_set_isomorphism
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (g1 : G1_BoundarySliceDecomposition State Boundary toState a c Path) :
    Path a c ≃ ((b : Boundary) × (Path (toState b) c × Path a (toState b))) where
  toFun := g1.split
  invFun := fun d => g1.concat d.2.1 d.2.2
  left_inv := fun γ => g1.concat_split γ
  right_inv := fun ⟨b, (γ₂, γ₁)⟩ => g1.split_concat b γ₂ γ₁

/-- Flat Cartesian product of paths over a single boundary state b.
    Produces raw full paths directly in (Path a c) without wrapping in SegmentPair. -/
def boundaryFullPaths
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c)
    (b : Boundary) (rights : List (Path (toState b) c)) (lefts : List (Path a (toState b))) :
    List (Path a c) :=
  match rights with
  | [] => []
  | r :: rs => (lefts.map fun l => concat r l) ++ boundaryFullPaths concat b rs lefts

/-- Raw flat paths generated across all declared boundary states in a boundary slice.
    This is a flat List (Path a c), containing NO row grouping or pair wrappers. -/
def rawFullPaths
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c)
    (boundaries : List Boundary)
    (rights : (b : Boundary) → List (Path (toState b) c))
    (lefts : (b : Boundary) → List (Path a (toState b))) :
    List (Path a c) :=
  match boundaries with
  | [] => []
  | b :: bs => boundaryFullPaths concat b (rights b) (lefts b) ++ rawFullPaths concat bs rights lefts

/-- Helper: scalar multiplication distribution over list map sum. -/
theorem list_sum_const_mul {α : Type} (xs : List α) (c : Int) (f : α → Int) :
    (xs.map fun x => c * f x).sum = c * (xs.map f).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih => simp [ih, Int.mul_add]

/-- Lemma: Single-right segment product-of-sums on raw paths. -/
theorem raw_single_right_sum
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c)
    (b : Boundary) (r : Path (toState b) c) (lefts : List (Path a (toState b)))
    (w : Path a c → Int) (wLeft : Path a (toState b) → Int) (wRight : Path (toState b) c → Int)
    (hFact : ∀ l, w (concat r l) = wRight r * wLeft l) :
    ((lefts.map fun l => w (concat r l)).sum) = wRight r * (lefts.map wLeft).sum := by
  calc
    ((lefts.map fun l => w (concat r l)).sum)
        = (lefts.map fun l => wRight r * wLeft l).sum := by
            exact list_sum_map_congr_mem lefts (fun l => w (concat r l))
              (fun l => wRight r * wLeft l) (fun l _hmem => hFact l)
    _ = wRight r * (lefts.map wLeft).sum :=
            list_sum_const_mul lefts (wRight r) wLeft

/-- Lemma: Factorization of raw full paths over a single boundary slice state. -/
theorem raw_boundary_paths_factorization
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c)
    (b : Boundary) (rights : List (Path (toState b) c)) (lefts : List (Path a (toState b)))
    (w : Path a c → Int) (wLeft : Path a (toState b) → Int) (wRight : Path (toState b) c → Int)
    (hFact : ∀ (r : Path (toState b) c) (l : Path a (toState b)), w (concat r l) = wRight r * wLeft l) :
    ((boundaryFullPaths concat b rights lefts).map w).sum =
      (rights.map wRight).sum * (lefts.map wLeft).sum := by
  induction rights with
  | nil => simp [boundaryFullPaths]
  | cons r rs ih =>
      have hsingle : ((lefts.map fun l => w (concat r l)).sum) = wRight r * (lefts.map wLeft).sum :=
        raw_single_right_sum concat b r lefts w wLeft wRight (hFact r)
      have hrowmap :
          (List.map (w ∘ fun l => concat r l) lefts).sum =
            (lefts.map fun l => w (concat r l)).sum := by
        rfl
      calc
        ((boundaryFullPaths concat b (r :: rs) lefts).map w).sum
            = ((List.map (w ∘ fun l => concat r l) lefts).sum) +
              ((boundaryFullPaths concat b rs lefts).map w).sum := by
                simp [boundaryFullPaths, List.map_append]
        _ = (lefts.map fun l => w (concat r l)).sum +
              ((boundaryFullPaths concat b rs lefts).map w).sum := by
                rw [hrowmap]
        _ = wRight r * (lefts.map wLeft).sum +
              ((boundaryFullPaths concat b rs lefts).map w).sum := by
                rw [hsingle]
        _ = wRight r * (lefts.map wLeft).sum +
              (rs.map wRight).sum * (lefts.map wLeft).sum := by
                rw [ih]
        _ = ((r :: rs).map wRight).sum * (lefts.map wLeft).sum := by
                simp [Int.add_mul]

/-- Theorem: Kernel composition on raw flat paths.
    Given raw full paths generated by the G1 boundary slice Cartesian decomposition,
    the sum of the global evaluated contribution w over raw full paths factors as the
    sum over boundary states of the product of local segment sums, without pre-decomposed
    row data structures. -/
theorem raw_kernel_composition_under_G1_G2_G3
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c)
    (boundaries : List Boundary)
    (rights : (b : Boundary) → List (Path (toState b) c))
    (lefts : (b : Boundary) → List (Path a (toState b)))
    (w : Path a c → Int)
    (wLeft : ∀ {b : Boundary}, Path a (toState b) → Int)
    (wRight : ∀ {b : Boundary}, Path (toState b) c → Int)
    (hFact : ∀ (b : Boundary) (r : Path (toState b) c) (l : Path a (toState b)),
      w (concat r l) = wRight r * wLeft l) :
    ((rawFullPaths concat boundaries rights lefts).map w).sum =
      (boundaries.map fun b => ((rights b).map wRight).sum * ((lefts b).map wLeft).sum).sum := by
  induction boundaries with
  | nil => rfl
  | cons b bs ih =>
      have hhead :
          ((boundaryFullPaths concat b (rights b) (lefts b)).map w).sum =
            ((rights b).map wRight).sum * ((lefts b).map wLeft).sum :=
        raw_boundary_paths_factorization concat b (rights b) (lefts b) w wLeft wRight (hFact b)
      calc
        ((rawFullPaths concat (b :: bs) rights lefts).map w).sum
            = ((boundaryFullPaths concat b (rights b) (lefts b)).map w).sum +
              ((rawFullPaths concat bs rights lefts).map w).sum := by
                simp [rawFullPaths, List.map_append]
        _ = ((rights b).map wRight).sum * ((lefts b).map wLeft).sum +
              ((rawFullPaths concat bs rights lefts).map w).sum := by
                rw [hhead]
        _ = ((rights b).map wRight).sum * ((lefts b).map wLeft).sum +
              (bs.map fun b' => ((rights b').map wRight).sum * ((lefts b').map wLeft).sum).sum := by
                rw [ih]
        _ = ((b :: bs).map fun b' => ((rights b').map wRight).sum * ((lefts b').map wLeft).sum).sum := by
                rfl

#print axioms g1_set_isomorphism
#print axioms raw_kernel_composition_under_G1_G2_G3

end PaperAE004
