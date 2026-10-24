/-
Paper 020, Tier 3: defect-corrected kernel identities.

These theorems mechanize the exact bookkeeping behind the Evaluator Gluing
Defect residual.  The weights are abstract integer weights; a later analytic
specialization may instantiate them with nonnegative real `exp (-β A)` weights.
-/

import «03_kernel_composition»

namespace PaperAE004

def weightedKernel {α : Type}
    (rows : List (List α)) (eval weight : α → Int) : Int :=
  flatKernel rows (fun p => eval p * weight p)

def evaluatorResidual {α : Type}
    (rows : List (List α)) (delta weight : α → Int) : Int :=
  flatKernel rows (fun p => delta p * weight p)

theorem pointwise_eval_defect_identity {α : Type}
    (localEval delta weight : α → Int) (p : α) :
    (localEval p + delta p) * weight p =
      localEval p * weight p + delta p * weight p := by
  rw [Int.add_mul]

theorem list_sum_map_add {α : Type} (xs : List α) (f g : α → Int) :
    (xs.map (fun x => f x + g x)).sum =
      (xs.map f).sum + (xs.map g).sum := by
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      simp [ih, Int.add_assoc, Int.add_left_comm]

theorem defect_corrected_kernel_identity {α : Type}
    (rows : List (List α)) (localEval delta weight : α → Int) :
    weightedKernel rows (fun p => localEval p + delta p) weight =
      weightedKernel rows localEval weight + evaluatorResidual rows delta weight := by
  unfold weightedKernel evaluatorResidual flatKernel
  calc
    ((flatten rows).map (fun p => (localEval p + delta p) * weight p)).sum
        = ((flatten rows).map
            (fun p => localEval p * weight p + delta p * weight p)).sum := by
            exact list_sum_map_congr_mem (flatten rows)
              (fun p => (localEval p + delta p) * weight p)
              (fun p => localEval p * weight p + delta p * weight p)
              (fun p _hp => pointwise_eval_defect_identity localEval delta weight p)
    _ = ((flatten rows).map (fun p => localEval p * weight p)).sum +
          ((flatten rows).map (fun p => delta p * weight p)).sum :=
            list_sum_map_add (flatten rows)
              (fun p => localEval p * weight p)
              (fun p => delta p * weight p)

def correctedCompositeContribution {α : Type}
    (localEval deltaEval localWeight deltaWeight : α → Int) (p : α) : Int :=
  (localEval p + deltaEval p) * (localWeight p + deltaWeight p)

def fullyCorrectedExpansion {α : Type}
    (localEval deltaEval localWeight deltaWeight : α → Int) (p : α) : Int :=
  localEval p * localWeight p +
  deltaEval p * localWeight p +
  localEval p * deltaWeight p +
  deltaEval p * deltaWeight p

theorem pointwise_full_defect_expansion {α : Type}
    (localEval deltaEval localWeight deltaWeight : α → Int) (p : α) :
    correctedCompositeContribution localEval deltaEval localWeight deltaWeight p =
      fullyCorrectedExpansion localEval deltaEval localWeight deltaWeight p := by
  simp [
    correctedCompositeContribution,
    fullyCorrectedExpansion,
    Int.add_mul,
    Int.mul_add,
    Int.add_assoc,
    Int.add_left_comm,
    Int.add_comm
  ]

theorem fully_corrected_kernel_identity {α : Type}
    (rows : List (List α))
    (localEval deltaEval localWeight deltaWeight : α → Int) :
    flatKernel rows
        (correctedCompositeContribution localEval deltaEval localWeight deltaWeight) =
      flatKernel rows
        (fullyCorrectedExpansion localEval deltaEval localWeight deltaWeight) := by
  unfold flatKernel
  exact list_sum_map_congr_mem (flatten rows)
    (correctedCompositeContribution localEval deltaEval localWeight deltaWeight)
    (fullyCorrectedExpansion localEval deltaEval localWeight deltaWeight)
    (fun p _hp =>
      pointwise_full_defect_expansion localEval deltaEval localWeight deltaWeight p)

#print axioms PaperAE004.pointwise_eval_defect_identity
#print axioms PaperAE004.defect_corrected_kernel_identity
#print axioms PaperAE004.pointwise_full_defect_expansion
#print axioms PaperAE004.fully_corrected_kernel_identity

end PaperAE004
