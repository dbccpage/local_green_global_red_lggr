/-
Paper 020, Tier 2b: product-of-sums bridge for boundary rows.

`L020_03_KernelComposition` proves rowwise pair-sum reindexing.  This file
adds the missing finite matrix step: when a boundary row is explicitly the
Cartesian product of right and left segment lists, the row pair-sum factors as
the product of the two segment sums.
-/

import «03_kernel_composition»

namespace PaperAE004

structure BoundaryRow (Boundary Left Right : Type) where
  boundary : Boundary
  lefts : List Left
  rights : List Right

def cartesianPairs {Boundary Left Right : Type}
    (boundary : Boundary) (lefts : List Left) : List Right → List (SegmentPair Boundary Left Right)
  | [] => []
  | right :: rights =>
      (lefts.map fun left => { boundary := boundary, left := left, right := right }) ++
        cartesianPairs boundary lefts rights

def BoundaryRow.pairs {Boundary Left Right : Type}
    (row : BoundaryRow Boundary Left Right) : List (SegmentPair Boundary Left Right) :=
  cartesianPairs row.boundary row.lefts row.rights

def pairProductContribution {Boundary Left Right : Type}
    (wLeft : Left → Int) (wRight : Right → Int)
    (p : SegmentPair Boundary Left Right) : Int :=
  wRight p.right * wLeft p.left

@[simp] theorem pairProductContribution_mk
    {Boundary Left Right : Type}
    (boundary : Boundary) (left : Left) (right : Right)
    (wLeft : Left → Int) (wRight : Right → Int) :
    pairProductContribution (Boundary := Boundary) wLeft wRight
      { boundary := boundary, left := left, right := right } =
      wRight right * wLeft left := by
  rfl

def segmentSum {α : Type} (xs : List α) (w : α → Int) : Int :=
  (xs.map w).sum

def rowMatrixProduct {Boundary Left Right : Type}
    (wLeft : Left → Int) (wRight : Right → Int)
    (row : BoundaryRow Boundary Left Right) : Int :=
  segmentSum row.rights wRight * segmentSum row.lefts wLeft

def matrixKernel {Boundary Left Right : Type}
    (rows : List (BoundaryRow Boundary Left Right))
    (wLeft : Left → Int) (wRight : Right → Int) : Int :=
  (rows.map fun row => rowMatrixProduct wLeft wRight row).sum

theorem single_right_product_sum {Left Right : Type}
    (lefts : List Left) (right : Right)
    (wLeft : Left → Int) (wRight : Right → Int) :
    ((lefts.map fun left => wRight right * wLeft left).sum) =
      wRight right * (lefts.map wLeft).sum := by
  induction lefts with
  | nil =>
      simp
  | cons left lefts ih =>
      simp [ih, Int.mul_add]

theorem row_cartesian_product_factorization
    {Boundary Left Right : Type}
    (boundary : Boundary) (lefts : List Left) (rights : List Right)
    (wLeft : Left → Int) (wRight : Right → Int) :
    ((cartesianPairs boundary lefts rights).map
        (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum =
      (rights.map wRight).sum * (lefts.map wLeft).sum := by
  induction rights with
  | nil =>
      simp [cartesianPairs]
  | cons right rights ih =>
      have hsingle :
          (lefts.map fun left => wRight right * wLeft left).sum =
            wRight right * (lefts.map wLeft).sum := by
        exact single_right_product_sum lefts right wLeft wRight
      have hrowmap :
          (List.map
            (pairProductContribution (Boundary := Boundary) wLeft wRight ∘
              fun left => { boundary := boundary, left := left, right := right })
            lefts).sum =
            (lefts.map fun left => wRight right * wLeft left).sum := by
        exact list_sum_map_congr_mem lefts
          (pairProductContribution (Boundary := Boundary) wLeft wRight ∘
            fun left => { boundary := boundary, left := left, right := right })
          (fun left => wRight right * wLeft left)
          (fun left _hmem => by rfl)
      calc
        ((cartesianPairs boundary lefts (right :: rights)).map
            (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum
            =
              (List.map
                (pairProductContribution (Boundary := Boundary) wLeft wRight ∘
                  fun left => { boundary := boundary, left := left, right := right })
                lefts).sum +
              ((cartesianPairs boundary lefts rights).map
                (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum := by
                simp [cartesianPairs, List.map_append]
        _ = (lefts.map fun left => wRight right * wLeft left).sum +
              ((cartesianPairs boundary lefts rights).map
                (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum := by
                rw [hrowmap]
        _ = wRight right * (lefts.map wLeft).sum +
              ((cartesianPairs boundary lefts rights).map
                (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum := by
                rw [hsingle]
        _ = wRight right * (lefts.map wLeft).sum +
              (rights.map wRight).sum * (lefts.map wLeft).sum := by
                rw [ih]
        _ = ((right :: rights).map wRight).sum * (lefts.map wLeft).sum := by
                simp [Int.add_mul]

theorem boundary_rows_product_of_sums
    {Boundary Left Right : Type}
    (rows : List (BoundaryRow Boundary Left Right))
    (wLeft : Left → Int) (wRight : Right → Int) :
    boundaryKernel (rows.map BoundaryRow.pairs)
        (pairProductContribution (Boundary := Boundary) wLeft wRight) =
      matrixKernel rows wLeft wRight := by
  induction rows with
  | nil =>
      rfl
  | cons row rows ih =>
      calc
        boundaryKernel ((row :: rows).map BoundaryRow.pairs)
            (pairProductContribution (Boundary := Boundary) wLeft wRight)
            =
              (row.pairs.map
                (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum +
              boundaryKernel (rows.map BoundaryRow.pairs)
                (pairProductContribution (Boundary := Boundary) wLeft wRight) := by
                rfl
        _ = rowMatrixProduct wLeft wRight row +
              boundaryKernel (rows.map BoundaryRow.pairs)
                (pairProductContribution (Boundary := Boundary) wLeft wRight) := by
                unfold BoundaryRow.pairs rowMatrixProduct segmentSum
                rw [row_cartesian_product_factorization]
        _ = rowMatrixProduct wLeft wRight row + matrixKernel rows wLeft wRight := by
                rw [ih]
        _ = matrixKernel (row :: rows) wLeft wRight := by
                rfl

theorem kernel_composition_under_G1_G2_G3
    {Boundary Left Right : Type}
    (rows : List (BoundaryRow Boundary Left Right))
    (wLeft : Left → Int) (wRight : Right → Int)
    (globalEval globalWeight : SegmentPair Boundary Left Right → Int)
    (hContribution :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalContribution globalEval globalWeight p =
          pairProductContribution (Boundary := Boundary) wLeft wRight p) :
    flatKernel (rows.map BoundaryRow.pairs)
        (globalContribution globalEval globalWeight) =
      matrixKernel rows wLeft wRight := by
  calc
    flatKernel (rows.map BoundaryRow.pairs)
        (globalContribution globalEval globalWeight)
        =
          ((flatten (rows.map BoundaryRow.pairs)).map
            (pairProductContribution (Boundary := Boundary) wLeft wRight)).sum := by
            exact list_sum_map_congr_mem (flatten (rows.map BoundaryRow.pairs))
              (globalContribution globalEval globalWeight)
              (pairProductContribution (Boundary := Boundary) wLeft wRight)
              hContribution
    _ = boundaryKernel (rows.map BoundaryRow.pairs)
          (pairProductContribution (Boundary := Boundary) wLeft wRight) := by
            exact finite_boundary_sum_reindexing (rows.map BoundaryRow.pairs)
              (pairProductContribution (Boundary := Boundary) wLeft wRight)
    _ = matrixKernel rows wLeft wRight := by
            exact boundary_rows_product_of_sums rows wLeft wRight

#print axioms PaperAE004.single_right_product_sum
#print axioms PaperAE004.row_cartesian_product_factorization
#print axioms PaperAE004.boundary_rows_product_of_sums
#print axioms PaperAE004.kernel_composition_under_G1_G2_G3

end PaperAE004
