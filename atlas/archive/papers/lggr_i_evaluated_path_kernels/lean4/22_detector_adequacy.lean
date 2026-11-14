/-
Paper 020, Tier 22: corrected DetectorAdequacy structural target.

This file mechanizes only the finite Boolean count identity, its strict
criterion, two false-red counterexamples, and implications of an explicitly
assumed structural guard. It does not mechanize blind-spot capacity and does
not discharge the exact BSC-CERT obligation.
-/

import «17_defect_packet_non_sufficiency»

namespace PaperAE004

def isLRGRTriple (t : EvalTriple) : Bool :=
  (!isLocalGreenTriple t) && (!t.eg)

def isGlobalFailureTriple (t : EvalTriple) : Bool :=
  !t.eg

def globalFailureCount (samples : List EvalTriple) : Nat :=
  classCount isGlobalFailureTriple samples

def lrgrCount (samples : List EvalTriple) : Nat :=
  classCount isLRGRTriple samples

theorem sample_count_eq_global_pass_add_global_failure (samples : List EvalTriple) :
    samples.length = globalPassCount samples + globalFailureCount samples := by
  induction samples with
  | nil =>
      rfl
  | cons t ts ih =>
      cases t with
      | mk e1 e2 eg =>
          cases eg <;>
            simp [
              globalPassCount,
              globalFailureCount,
              classCount,
              isGlobalGreenTriple,
              isGlobalFailureTriple,
              ih
            ] <;> omega

theorem global_failure_indicator_eq_ngd_add_lrgr (t : EvalTriple) :
    (if isGlobalFailureTriple t then 1 else 0 : Nat) =
      (if isNGDTriple t then 1 else 0) +
      (if isLRGRTriple t then 1 else 0) := by
  cases t with
  | mk e1 e2 eg =>
      cases e1 <;> cases e2 <;> cases eg <;>
        decide

theorem global_failure_count_eq_ngd_add_lrgr (samples : List EvalTriple) :
    globalFailureCount samples =
      classCount isNGDTriple samples + lrgrCount samples := by
  induction samples with
  | nil =>
      rfl
  | cons t ts ih =>
      change
        (if isGlobalFailureTriple t then 1 else 0) + globalFailureCount ts =
          ((if isNGDTriple t then 1 else 0) + classCount isNGDTriple ts) +
          ((if isLRGRTriple t then 1 else 0) + lrgrCount ts)
      rw [global_failure_indicator_eq_ngd_add_lrgr, ih]
      omega

/-- Finite-count form of the general identity `1 - GPR = NGD + LRGR`. -/
theorem one_minus_gpr_eq_ngd_add_lrgr (samples : List EvalTriple) :
    samples.length - globalPassCount samples =
      classCount isNGDTriple samples + lrgrCount samples := by
  have partition := sample_count_eq_global_pass_add_global_failure samples
  rw [global_failure_count_eq_ngd_add_lrgr] at partition
  omega

theorem ngd_strictly_below_global_failure_iff_lrgr_positive
    (samples : List EvalTriple) :
    classCount isNGDTriple samples < globalFailureCount samples ↔
      0 < lrgrCount samples := by
  rw [global_failure_count_eq_ngd_add_lrgr]
  omega

def falseRedTwoRecord : List EvalTriple :=
  [
    { e1 := true, e2 := true, eg := false },
    { e1 := true, e2 := true, eg := true }
  ]

theorem false_red_two_record_counts :
    falseRedTwoRecord.length = 2 ∧
      globalPassCount falseRedTwoRecord = 1 ∧
      globalFailureCount falseRedTwoRecord = 1 ∧
      classCount isNGDTriple falseRedTwoRecord = 1 ∧
      lrgrCount falseRedTwoRecord = 0 := by
  decide

def falseRedStrongFourRecord : List EvalTriple :=
  [
    { e1 := true, e2 := true, eg := false },
    { e1 := true, e2 := false, eg := true },
    { e1 := false, e2 := true, eg := true },
    { e1 := false, e2 := false, eg := true }
  ]

theorem false_red_strong_four_record_counts :
    falseRedStrongFourRecord.length = 4 ∧
      globalPassCount falseRedStrongFourRecord = 3 ∧
      globalFailureCount falseRedStrongFourRecord = 1 ∧
      classCount isNGDTriple falseRedStrongFourRecord = 1 ∧
      lrgrCount falseRedStrongFourRecord = 0 := by
  decide

theorem false_red_strong_four_record_evaluators_nonconstant :
    (falseRedStrongFourRecord.map (fun t => t.e1) =
      [true, true, false, false]) ∧
    (falseRedStrongFourRecord.map (fun t => t.e2) =
      [true, false, true, false]) ∧
    (falseRedStrongFourRecord.map (fun t => t.eg) =
      [false, true, true, true]) := by
  decide

/-- Abstract propositions named by a deployment schema; this does not decide them. -/
structure DetectorStructuralClaims where
  protectedDistinctionsNonempty : Prop
  evaluatorDeclarationsComplete : Prop
  projectionsSeparateProtectedPairs : Prop
  genuineInteriorCut : Prop
  evaluatorsNonconstant : Prop
  localProductNonconstant : Prop
  globalDiffersFromLocalProduct : Prop
  carrierClosedDisclosed : Prop
  blindSpotsDisclosed : Prop

/-- Proofs of the exact structural claims. No spectral/capacity field occurs here. -/
structure DetectorStructuralGuard
    (samples : List EvalTriple)
    (claims : DetectorStructuralClaims) : Prop where
  corpusNonempty : samples ≠ []
  protectedDistinctionsNonempty : claims.protectedDistinctionsNonempty
  evaluatorDeclarationsComplete : claims.evaluatorDeclarationsComplete
  projectionsSeparateProtectedPairs : claims.projectionsSeparateProtectedPairs
  genuineInteriorCut : claims.genuineInteriorCut
  evaluatorsNonconstant : claims.evaluatorsNonconstant
  localProductNonconstant : claims.localProductNonconstant
  globalDiffersFromLocalProduct : claims.globalDiffersFromLocalProduct
  carrierClosedDisclosed : claims.carrierClosedDisclosed
  blindSpotsDisclosed : claims.blindSpotsDisclosed
  ngdWitness : ∃ t ∈ samples, isNGDTriple t = true
  lrgrWitness : ∃ t ∈ samples, isLRGRTriple t = true

theorem classCount_positive_of_member
    (cls : EvalTriple → Bool)
    {samples : List EvalTriple}
    {t : EvalTriple}
    (membership : t ∈ samples)
    (witness : cls t = true) :
    0 < classCount cls samples := by
  induction samples with
  | nil =>
      simp at membership
  | cons head tail ih =>
      simp only [List.mem_cons] at membership
      rcases membership with rfl | membership
      · simp [classCount, witness] <;> omega
      · have tailPositive : 0 < classCount cls tail := ih membership
        simp only [classCount]
        split <;> omega

theorem structural_guard_implies_lrgr_positive
    {samples : List EvalTriple}
    {claims : DetectorStructuralClaims}
    (guard : DetectorStructuralGuard samples claims) :
    0 < lrgrCount samples := by
  obtain ⟨t, membership, witness⟩ := guard.lrgrWitness
  exact classCount_positive_of_member isLRGRTriple membership witness

theorem structural_guard_implies_ngd_strictly_below_global_failure
    {samples : List EvalTriple}
    {claims : DetectorStructuralClaims}
    (guard : DetectorStructuralGuard samples claims) :
    classCount isNGDTriple samples < globalFailureCount samples := by
  rw [ngd_strictly_below_global_failure_iff_lrgr_positive]
  exact structural_guard_implies_lrgr_positive guard

#print axioms PaperAE004.sample_count_eq_global_pass_add_global_failure
#print axioms PaperAE004.global_failure_count_eq_ngd_add_lrgr
#print axioms PaperAE004.one_minus_gpr_eq_ngd_add_lrgr
#print axioms PaperAE004.ngd_strictly_below_global_failure_iff_lrgr_positive
#print axioms PaperAE004.false_red_two_record_counts
#print axioms PaperAE004.false_red_strong_four_record_counts
#print axioms PaperAE004.false_red_strong_four_record_evaluators_nonconstant
#print axioms PaperAE004.structural_guard_implies_lrgr_positive
#print axioms PaperAE004.structural_guard_implies_ngd_strictly_below_global_failure

end PaperAE004
