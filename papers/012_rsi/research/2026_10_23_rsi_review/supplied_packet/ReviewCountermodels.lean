import RelationalRsiNoGo
import RsiImpossible

/- Reviewer negative control: structural alignment and a finite report carrier
   can coexist with an infinite improving trajectory when report-grounded
   dominance is absent. This is consistent with the actual main theorem. -/
namespace ReviewCountermodels
open OmegaRelationalRsi

def equalityDifference : PrimitiveDifference Nat Bool where
  diff := fun x y => decide (x = y)
  zero := true

def oneReport : FiniteRelationalUniverse Nat Unit where
  carrier := [()]
  report := fun _ => ()
  complete := by intro _; exact List.Mem.head []

theorem succ_is_structurally_aligned :
    RelationallyAligned equalityDifference
      (fun _ : Nat => ())
      (fun _ _ : Unit => True)
      (fun _ : Nat => fun _ _ : Unit => ())
      Nat.succ := by
  constructor
  · intro x y h
    have hxy : x = y := by simpa [ZeroRel, equalityDifference] using h
    subst y
    simp [ZeroRel, equalityDifference]
  · intro x y _
    rfl
  · intro s _ i j x _ _
    rfl

def natDominance : StrictDominance Nat where
  dom := fun x y => y < x
  irrefl := Nat.lt_irrefl
  trans := by intro x y z hxy hyz; exact Nat.lt_trans hyz hxy

def growingTrajectory : RsiTrajectory Nat where
  phi := Nat.succ
  seq := id
  ord := natDominance
  step_eq := by intro k; rfl
  strictly_improves := Nat.lt_succ_self

theorem growing_trajectory_is_not_report_grounded :
    ¬ ReportGroundedDominance oneReport.report growingTrajectory.ord := by
  exact lemma1c_goodhart_metric_collapse_on_collision growingTrajectory oneReport.report
    (i := 0) (j := 1) (by decide) rfl

/- The existing refinement/budget lemmas quantify over globally strictly
   decreasing natural-valued sequences. Those hypotheses are inconsistent;
   finite-prefix statements require a length-indexed hypothesis instead. -/
theorem no_total_budget_satisfies_drop (budget : Nat → Nat)
    (h : ∀ k, budget (k + 1) < budget k) : False := by
  have hb := (lemma2c_licensed_lift_budget_bound budget h (budget 0 + 1)).2
  exact Nat.not_succ_le_self (budget 0) hb

theorem no_total_refinement_satisfies_drop (n : Nat) (pairs : Nat → Nat)
    (h0 : pairs 0 ≤ n * n)
    (h : ∀ k, pairs (k + 1) + 1 ≤ pairs k) : False := by
  have hb := (lemma2b_epistemic_horizon_refinement_bound n pairs h0 h (n * n + 1)).2
  exact Nat.not_succ_le_self (n * n) hb

end ReviewCountermodels

#print axioms ReviewCountermodels.succ_is_structurally_aligned
#print axioms ReviewCountermodels.growing_trajectory_is_not_report_grounded
#print axioms ReviewCountermodels.no_total_budget_satisfies_drop
#print axioms ReviewCountermodels.no_total_refinement_satisfies_drop
