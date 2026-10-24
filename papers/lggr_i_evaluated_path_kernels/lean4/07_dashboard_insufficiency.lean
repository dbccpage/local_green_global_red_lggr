/-
Paper 020, Tier 6: local-pass dashboards are insufficient.

Two finite samples can have the same local pass count and the same sample size
while disagreeing on global pass count, NGD count, and evaluator-defect sum.
This mechanizes the paper's dashboard warning: local activity alone does not
measure composed reliability.
-/

import «02_delta_partition»

namespace PaperAE004

def isLocalGreenTriple (t : EvalTriple) : Bool :=
  localProduct t.e1 t.e2 == 1

def isGlobalGreenTriple (t : EvalTriple) : Bool :=
  t.eg

def localPassCount (samples : List EvalTriple) : Nat :=
  classCount isLocalGreenTriple samples

def globalPassCount (samples : List EvalTriple) : Nat :=
  classCount isGlobalGreenTriple samples

def deltaSum (samples : List EvalTriple) : Int :=
  (samples.map fun t => deltaEval t.e1 t.e2 t.eg).sum

def singletonAllGreen : List EvalTriple :=
  [{ e1 := true, e2 := true, eg := true }]

def singletonLocalGreenGlobalRed : List EvalTriple :=
  [{ e1 := true, e2 := true, eg := false }]

theorem singleton_all_green_dashboard_counts :
    localPassCount singletonAllGreen = 1 ∧
      globalPassCount singletonAllGreen = 1 ∧
      classCount isNGDTriple singletonAllGreen = 0 ∧
      deltaSum singletonAllGreen = 0 := by
  decide

theorem singleton_lggr_dashboard_counts :
    localPassCount singletonLocalGreenGlobalRed = 1 ∧
      globalPassCount singletonLocalGreenGlobalRed = 0 ∧
      classCount isNGDTriple singletonLocalGreenGlobalRed = 1 ∧
      deltaSum singletonLocalGreenGlobalRed = -1 := by
  decide

theorem same_local_pass_count_different_global_ngd_and_delta :
    localPassCount singletonAllGreen =
        localPassCount singletonLocalGreenGlobalRed ∧
      singletonAllGreen.length = singletonLocalGreenGlobalRed.length ∧
      globalPassCount singletonAllGreen ≠
        globalPassCount singletonLocalGreenGlobalRed ∧
      classCount isNGDTriple singletonAllGreen ≠
        classCount isNGDTriple singletonLocalGreenGlobalRed ∧
      deltaSum singletonAllGreen ≠
        deltaSum singletonLocalGreenGlobalRed := by
  decide

theorem local_pass_count_does_not_determine_global_pass_count :
    ∃ s t : List EvalTriple,
      s.length = t.length ∧
        localPassCount s = localPassCount t ∧
        globalPassCount s ≠ globalPassCount t := by
  exact
    ⟨singletonAllGreen,
      singletonLocalGreenGlobalRed,
      rfl,
      rfl,
      by decide⟩

theorem local_pass_count_does_not_determine_ngd_count :
    ∃ s t : List EvalTriple,
      s.length = t.length ∧
        localPassCount s = localPassCount t ∧
        classCount isNGDTriple s ≠ classCount isNGDTriple t := by
  exact
    ⟨singletonAllGreen,
      singletonLocalGreenGlobalRed,
      rfl,
      rfl,
      by decide⟩

theorem local_pass_count_does_not_determine_delta_sum :
    ∃ s t : List EvalTriple,
      s.length = t.length ∧
        localPassCount s = localPassCount t ∧
        deltaSum s ≠ deltaSum t := by
  exact
    ⟨singletonAllGreen,
      singletonLocalGreenGlobalRed,
      rfl,
      rfl,
      by decide⟩

theorem all_local_green_can_be_all_global_red :
    ∃ samples : List EvalTriple,
      localPassCount samples = samples.length ∧
        globalPassCount samples = 0 ∧
        classCount isNGDTriple samples = samples.length ∧
        deltaSum samples = -1 := by
  exact
    ⟨singletonLocalGreenGlobalRed,
      rfl,
      rfl,
      rfl,
      rfl⟩

#print axioms PaperAE004.singleton_all_green_dashboard_counts
#print axioms PaperAE004.singleton_lggr_dashboard_counts
#print axioms PaperAE004.same_local_pass_count_different_global_ngd_and_delta
#print axioms PaperAE004.local_pass_count_does_not_determine_global_pass_count
#print axioms PaperAE004.local_pass_count_does_not_determine_ngd_count
#print axioms PaperAE004.local_pass_count_does_not_determine_delta_sum
#print axioms PaperAE004.all_local_green_can_be_all_global_red

end PaperAE004
