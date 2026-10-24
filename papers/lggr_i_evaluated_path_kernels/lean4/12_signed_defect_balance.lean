/-
Paper 020, Tier 12: signed defect balance.

The signed evaluator-defect sum is the PGD count minus the NGD count. This is
the signed counterpart to the absolute EGD decomposition: EGD counts both
off-diagonal defect modes, while the signed mean lets PGD and NGD cancel.
-/

import «11_egd_decomposition»

namespace PaperAE004

theorem deltaSum_cons (x : EvalTriple) (xs : List EvalTriple) :
    deltaSum (x :: xs) = deltaEval x.e1 x.e2 x.eg + deltaSum xs := by
  rfl

theorem localPassCount_cons (x : EvalTriple) (xs : List EvalTriple) :
    localPassCount (x :: xs) =
      (if isLocalGreenTriple x then 1 else 0) + localPassCount xs := by
  rfl

theorem globalPassCount_cons (x : EvalTriple) (xs : List EvalTriple) :
    globalPassCount (x :: xs) =
      (if isGlobalGreenTriple x then 1 else 0) + globalPassCount xs := by
  rfl

theorem pointwise_delta_eq_pgd_minus_ngd_indicator (t : EvalTriple) :
    deltaEval t.e1 t.e2 t.eg =
      (if isPGDTriple t then (1 : Int) else 0) -
        (if isNGDTriple t then (1 : Int) else 0) := by
  rcases t with ⟨e1, e2, eg⟩
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem pointwise_global_minus_local_indicator_eq_delta (t : EvalTriple) :
    (if isGlobalGreenTriple t then (1 : Int) else 0) -
        (if isLocalGreenTriple t then (1 : Int) else 0) =
      deltaEval t.e1 t.e2 t.eg := by
  rcases t with ⟨e1, e2, eg⟩
  cases e1 <;> cases e2 <;> cases eg <;> decide

theorem delta_sum_eq_pgd_count_minus_ngd_count
    (samples : List EvalTriple) :
    deltaSum samples =
      (classCount isPGDTriple samples : Int) -
        (classCount isNGDTriple samples : Int) := by
  induction samples with
  | nil =>
      rfl
  | cons x xs ih =>
      calc
        deltaSum (x :: xs)
            = deltaEval x.e1 x.e2 x.eg + deltaSum xs := by
              rw [deltaSum_cons]
        _ = ((if isPGDTriple x then (1 : Int) else 0) -
                (if isNGDTriple x then (1 : Int) else 0)) +
              ((classCount isPGDTriple xs : Int) -
                (classCount isNGDTriple xs : Int)) := by
              rw [pointwise_delta_eq_pgd_minus_ngd_indicator, ih]
        _ = (classCount isPGDTriple (x :: xs) : Int) -
              (classCount isNGDTriple (x :: xs) : Int) := by
              rcases x with ⟨e1, e2, eg⟩
              cases e1 <;> cases e2 <;> cases eg <;>
                simp [
                  classCount,
                  isNGDTriple,
                  isPGDTriple,
                  isNGD,
                  isPGD,
                  deltaEval,
                  localProduct,
                  b2i
                ]
              all_goals omega

theorem global_minus_local_count_eq_delta_sum
    (samples : List EvalTriple) :
    (globalPassCount samples : Int) - (localPassCount samples : Int) =
      deltaSum samples := by
  induction samples with
  | nil =>
      rfl
  | cons x xs ih =>
      calc
        (globalPassCount (x :: xs) : Int) -
            (localPassCount (x :: xs) : Int)
            =
              ((if isGlobalGreenTriple x then (1 : Int) else 0) +
                  (globalPassCount xs : Int)) -
                ((if isLocalGreenTriple x then (1 : Int) else 0) +
                  (localPassCount xs : Int)) := by
              rw [globalPassCount_cons, localPassCount_cons]
              rcases x with ⟨e1, e2, eg⟩
              cases e1 <;> cases e2 <;> cases eg <;>
                simp [isGlobalGreenTriple, isLocalGreenTriple, localProduct, b2i]
        _ = ((if isGlobalGreenTriple x then (1 : Int) else 0) -
                (if isLocalGreenTriple x then (1 : Int) else 0)) +
              ((globalPassCount xs : Int) - (localPassCount xs : Int)) := by
              omega
        _ = deltaEval x.e1 x.e2 x.eg + deltaSum xs := by
              rw [pointwise_global_minus_local_indicator_eq_delta, ih]
        _ = deltaSum (x :: xs) := by
              rw [deltaSum_cons]

theorem global_minus_local_count_eq_pgd_minus_ngd
    (samples : List EvalTriple) :
    (globalPassCount samples : Int) - (localPassCount samples : Int) =
      (classCount isPGDTriple samples : Int) -
        (classCount isNGDTriple samples : Int) := by
  rw [
    global_minus_local_count_eq_delta_sum,
    delta_sum_eq_pgd_count_minus_ngd_count
  ]

theorem zero_signed_delta_iff_ngd_pgd_counts_balance
    (samples : List EvalTriple) :
    deltaSum samples = 0 ↔
      classCount isNGDTriple samples = classCount isPGDTriple samples := by
  rw [delta_sum_eq_pgd_count_minus_ngd_count]
  constructor <;> intro h <;> omega

theorem global_count_eq_local_count_iff_ngd_pgd_counts_balance
    (samples : List EvalTriple) :
    globalPassCount samples = localPassCount samples ↔
      classCount isNGDTriple samples = classCount isPGDTriple samples := by
  have hbalance := global_minus_local_count_eq_pgd_minus_ngd samples
  constructor
  · intro h
    have hzero :
        (globalPassCount samples : Int) - (localPassCount samples : Int) = 0 := by
      omega
    rw [hbalance] at hzero
    omega
  · intro h
    have hzero :
        (classCount isPGDTriple samples : Int) -
            (classCount isNGDTriple samples : Int) = 0 := by
      omega
    rw [← hbalance] at hzero
    omega

#print axioms PaperAE004.deltaSum_cons
#print axioms PaperAE004.pointwise_delta_eq_pgd_minus_ngd_indicator
#print axioms PaperAE004.pointwise_global_minus_local_indicator_eq_delta
#print axioms PaperAE004.delta_sum_eq_pgd_count_minus_ngd_count
#print axioms PaperAE004.global_minus_local_count_eq_delta_sum
#print axioms PaperAE004.global_minus_local_count_eq_pgd_minus_ngd
#print axioms PaperAE004.zero_signed_delta_iff_ngd_pgd_counts_balance
#print axioms PaperAE004.global_count_eq_local_count_iff_ngd_pgd_counts_balance

end PaperAE004
