/-
Paper 020, Tier 1: pointwise defect partition and cancellation witness.

The signed evaluator defect is always one of -1, 0, or +1 for binary
evaluators.  The three defect classes form an exhaustive pointwise partition,
and a zero net residual need not imply every pointwise defect is zero.
-/

import «01_local_green_counterexample»

namespace PaperAE004

def isNGD (e1 e2 eg : Bool) : Bool := deltaEval e1 e2 eg == -1
def isPGD (e1 e2 eg : Bool) : Bool := deltaEval e1 e2 eg == 1
def isZDR (e1 e2 eg : Bool) : Bool := deltaEval e1 e2 eg == 0

theorem exactly_one_defect_class (e1 e2 eg : Bool) :
    (isNGD e1 e2 eg = true ∧ isPGD e1 e2 eg = false ∧ isZDR e1 e2 eg = false) ∨
    (isNGD e1 e2 eg = false ∧ isPGD e1 e2 eg = true ∧ isZDR e1 e2 eg = false) ∨
    (isNGD e1 e2 eg = false ∧ isPGD e1 e2 eg = false ∧ isZDR e1 e2 eg = true) := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem ngd_pgd_zdr_exhaustive (e1 e2 eg : Bool) :
    isNGD e1 e2 eg = true ∨
    isPGD e1 e2 eg = true ∨
    isZDR e1 e2 eg = true := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem ngd_pgd_zdr_pairwise_disjoint (e1 e2 eg : Bool) :
    ¬ (isNGD e1 e2 eg = true ∧ isPGD e1 e2 eg = true) ∧
    ¬ (isNGD e1 e2 eg = true ∧ isZDR e1 e2 eg = true) ∧
    ¬ (isPGD e1 e2 eg = true ∧ isZDR e1 e2 eg = true) := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

structure EvalTriple where
  e1 : Bool
  e2 : Bool
  eg : Bool

def isNGDTriple (t : EvalTriple) : Bool := isNGD t.e1 t.e2 t.eg
def isPGDTriple (t : EvalTriple) : Bool := isPGD t.e1 t.e2 t.eg
def isZDRTriple (t : EvalTriple) : Bool := isZDR t.e1 t.e2 t.eg

def classCount (cls : EvalTriple → Bool) : List EvalTriple → Nat
  | [] => 0
  | x :: xs => (if cls x then 1 else 0) + classCount cls xs

theorem defect_class_count_partition (samples : List EvalTriple) :
    classCount isNGDTriple samples +
      classCount isPGDTriple samples +
      classCount isZDRTriple samples =
    samples.length := by
  induction samples with
  | nil =>
      rfl
  | cons x xs ih =>
      cases x with
      | mk e1 e2 eg =>
          cases e1 <;> cases e2 <;> cases eg <;>
            simp [
              classCount,
              isNGDTriple,
              isPGDTriple,
              isZDRTriple,
              isNGD,
              isPGD,
              isZDR,
              deltaEval,
              localProduct,
              b2i,
              ih,
              Nat.add_assoc,
              Nat.add_comm,
              Nat.add_left_comm
            ]

def cancellationDeltaNeg : Int := deltaEval true true false
def cancellationDeltaPos : Int := deltaEval false false true

theorem cancellation_negative_delta :
    cancellationDeltaNeg = -1 := by
  rfl

theorem cancellation_positive_delta :
    cancellationDeltaPos = 1 := by
  rfl

theorem cancellation_net_zero :
    cancellationDeltaNeg + cancellationDeltaPos = 0 := by
  rfl

theorem cancellation_not_pointwise_zero :
    cancellationDeltaNeg ≠ 0 ∧ cancellationDeltaPos ≠ 0 := by
  decide

#print axioms PaperAE004.exactly_one_defect_class
#print axioms PaperAE004.ngd_pgd_zdr_exhaustive
#print axioms PaperAE004.defect_class_count_partition
#print axioms PaperAE004.cancellation_net_zero
#print axioms PaperAE004.cancellation_not_pointwise_zero

end PaperAE004
