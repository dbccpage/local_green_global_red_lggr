/-
Paper 020, Tier 13: two-rate dashboard insufficiency.

Even the paired dashboard (local pass count, global pass count) does not
determine the absolute evaluator gluing defect. NGD and PGD can cancel in the
signed gap while leaving EGD positive.
-/

import «12_signed_defect_balance»

namespace PaperAE004

def rateMatchedCleanSamples : List EvalTriple :=
  [{ e1 := true, e2 := true, eg := true },
    { e1 := false, e2 := false, eg := false }]

def rateMatchedCancellingSamples : List EvalTriple :=
  [{ e1 := true, e2 := true, eg := false },
    { e1 := false, e2 := false, eg := true }]

theorem rate_matched_clean_sample_counts :
    rateMatchedCleanSamples.length = 2 ∧
      localPassCount rateMatchedCleanSamples = 1 ∧
      globalPassCount rateMatchedCleanSamples = 1 ∧
      deltaSum rateMatchedCleanSamples = 0 ∧
      egdCount rateMatchedCleanSamples = 0 ∧
      classCount isNGDTriple rateMatchedCleanSamples = 0 ∧
      classCount isPGDTriple rateMatchedCleanSamples = 0 ∧
      classCount isZDRTriple rateMatchedCleanSamples = 2 := by
  decide

theorem rate_matched_cancelling_sample_counts :
    rateMatchedCancellingSamples.length = 2 ∧
      localPassCount rateMatchedCancellingSamples = 1 ∧
      globalPassCount rateMatchedCancellingSamples = 1 ∧
      deltaSum rateMatchedCancellingSamples = 0 ∧
      egdCount rateMatchedCancellingSamples = 2 ∧
      classCount isNGDTriple rateMatchedCancellingSamples = 1 ∧
      classCount isPGDTriple rateMatchedCancellingSamples = 1 ∧
      classCount isZDRTriple rateMatchedCancellingSamples = 0 := by
  decide

theorem same_lpr_gpr_and_delta_sum_different_egd :
    rateMatchedCleanSamples.length = rateMatchedCancellingSamples.length ∧
      localPassCount rateMatchedCleanSamples =
        localPassCount rateMatchedCancellingSamples ∧
      globalPassCount rateMatchedCleanSamples =
        globalPassCount rateMatchedCancellingSamples ∧
      deltaSum rateMatchedCleanSamples = deltaSum rateMatchedCancellingSamples ∧
      egdCount rateMatchedCleanSamples ≠
        egdCount rateMatchedCancellingSamples ∧
      classCount isNGDTriple rateMatchedCleanSamples ≠
        classCount isNGDTriple rateMatchedCancellingSamples ∧
      classCount isPGDTriple rateMatchedCleanSamples ≠
        classCount isPGDTriple rateMatchedCancellingSamples ∧
      classCount isZDRTriple rateMatchedCleanSamples ≠
        classCount isZDRTriple rateMatchedCancellingSamples := by
  decide

theorem pass_rates_do_not_determine_egd :
    ∃ clean cancelling : List EvalTriple,
      clean.length = cancelling.length ∧
        localPassCount clean = localPassCount cancelling ∧
        globalPassCount clean = globalPassCount cancelling ∧
        deltaSum clean = deltaSum cancelling ∧
        egdCount clean ≠ egdCount cancelling := by
  exact ⟨rateMatchedCleanSamples, rateMatchedCancellingSamples, by decide⟩

theorem pass_rates_do_not_determine_defect_partition :
    ∃ clean cancelling : List EvalTriple,
      clean.length = cancelling.length ∧
        localPassCount clean = localPassCount cancelling ∧
        globalPassCount clean = globalPassCount cancelling ∧
        deltaSum clean = deltaSum cancelling ∧
        classCount isNGDTriple clean ≠ classCount isNGDTriple cancelling ∧
        classCount isPGDTriple clean ≠ classCount isPGDTriple cancelling ∧
        classCount isZDRTriple clean ≠ classCount isZDRTriple cancelling := by
  exact ⟨rateMatchedCleanSamples, rateMatchedCancellingSamples, by decide⟩

#print axioms PaperAE004.rate_matched_clean_sample_counts
#print axioms PaperAE004.rate_matched_cancelling_sample_counts
#print axioms PaperAE004.same_lpr_gpr_and_delta_sum_different_egd
#print axioms PaperAE004.pass_rates_do_not_determine_egd
#print axioms PaperAE004.pass_rates_do_not_determine_defect_partition

end PaperAE004
