/-
Paper 020, Tier 2: finite kernel composition over a declared boundary slice.

G1 is represented as data: a finite list of boundary rows, each containing
the decomposed composite paths routed through that boundary state.  The theorem
then separates the two algebraic responsibilities:

* finite boundary reindexing: summing the flattened rows equals summing each
  boundary row and then summing over boundaries;
* G2/G3 pointwise factorization: global contribution equals the product-form
  local contribution on every decomposed path.
-/

import «02_delta_partition»

namespace PaperAE004

structure SegmentPair (Boundary Left Right : Type) where
  boundary : Boundary
  left : Left
  right : Right

def flatten {α : Type} : List (List α) → List α
  | [] => []
  | row :: rows => row ++ flatten rows

def flatKernel {α : Type} (rows : List (List α)) (contribution : α → Int) : Int :=
  ((flatten rows).map contribution).sum

def boundaryKernel {α : Type} (rows : List (List α)) (contribution : α → Int) : Int :=
  (rows.map fun row => (row.map contribution).sum).sum

theorem finite_boundary_sum_reindexing {α : Type}
    (rows : List (List α)) (contribution : α → Int) :
    flatKernel rows contribution = boundaryKernel rows contribution := by
  induction rows with
  | nil =>
      rfl
  | cons row rows ih =>
      calc
        flatKernel (row :: rows) contribution
            = (row.map contribution).sum + flatKernel rows contribution := by
                simp [flatKernel, flatten, List.map_append]
        _ = (row.map contribution).sum + boundaryKernel rows contribution := by
                rw [ih]
        _ = boundaryKernel (row :: rows) contribution := by
                rfl

theorem list_sum_map_congr_mem {α : Type} (xs : List α) (f g : α → Int)
    (h : ∀ x, x ∈ xs → f x = g x) :
    (xs.map f).sum = (xs.map g).sum := by
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      have hx : x ∈ x :: xs := by simp
      have htail : ∀ y, y ∈ xs → f y = g y := by
        intro y hy
        exact h y (by simp [hy])
      simp [h x hx, ih htail]

def globalContribution {α : Type}
    (globalEval globalWeight : α → Int) (p : α) : Int :=
  globalEval p * globalWeight p

def factoredContribution {Boundary Left Right : Type}
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (weightLeft : Left → Int) (weightRight : Right → Int)
    (p : SegmentPair Boundary Left Right) : Int :=
  (evalRight p.right * evalLeft p.left) *
    (weightRight p.right * weightLeft p.left)

theorem pointwise_factorization_gives_contribution
    {Boundary Left Right : Type}
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (weightLeft : Left → Int) (weightRight : Right → Int)
    (globalEval globalWeight : SegmentPair Boundary Left Right → Int)
    (p : SegmentPair Boundary Left Right)
    (hEval : globalEval p = evalRight p.right * evalLeft p.left)
    (hWeight : globalWeight p = weightRight p.right * weightLeft p.left) :
    globalContribution globalEval globalWeight p =
      factoredContribution evalLeft evalRight weightLeft weightRight p := by
  unfold globalContribution factoredContribution
  rw [hEval, hWeight]

theorem kernel_pair_sum_reindexing_under_G1_G2_G3
    {Boundary Left Right : Type}
    (rows : List (List (SegmentPair Boundary Left Right)))
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (weightLeft : Left → Int) (weightRight : Right → Int)
    (globalEval globalWeight : SegmentPair Boundary Left Right → Int)
    (hEval :
      ∀ p, p ∈ flatten rows → globalEval p = evalRight p.right * evalLeft p.left)
    (hWeight :
      ∀ p, p ∈ flatten rows → globalWeight p = weightRight p.right * weightLeft p.left) :
    flatKernel rows (globalContribution globalEval globalWeight) =
      boundaryKernel rows
        (factoredContribution evalLeft evalRight weightLeft weightRight) := by
  have hpoint :
      ∀ p, p ∈ flatten rows →
        globalContribution globalEval globalWeight p =
          factoredContribution (Boundary := Boundary)
            evalLeft evalRight weightLeft weightRight p := by
    intro p hp
    exact pointwise_factorization_gives_contribution
      evalLeft evalRight weightLeft weightRight globalEval globalWeight p
      (hEval p hp) (hWeight p hp)
  calc
    flatKernel rows (globalContribution globalEval globalWeight)
        = ((flatten rows).map
            (factoredContribution (Boundary := Boundary)
              evalLeft evalRight weightLeft weightRight)).sum := by
            exact list_sum_map_congr_mem (flatten rows)
              (globalContribution globalEval globalWeight)
              (factoredContribution (Boundary := Boundary)
                evalLeft evalRight weightLeft weightRight) hpoint
    _ = boundaryKernel rows
          (factoredContribution (Boundary := Boundary)
            evalLeft evalRight weightLeft weightRight) :=
        finite_boundary_sum_reindexing rows
          (factoredContribution (Boundary := Boundary)
            evalLeft evalRight weightLeft weightRight)

#print axioms PaperAE004.finite_boundary_sum_reindexing
#print axioms PaperAE004.pointwise_factorization_gives_contribution
#print axioms PaperAE004.kernel_pair_sum_reindexing_under_G1_G2_G3

end PaperAE004
