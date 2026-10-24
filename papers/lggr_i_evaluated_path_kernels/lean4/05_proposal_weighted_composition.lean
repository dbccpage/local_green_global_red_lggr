/-
Paper 020, Tier 4: proposal-weighted POCv2 composition.

This file instantiates the Tier 2 kernel-composition theorem with segment
weights that combine proposal mass and action/cost weight.  G4 is represented
as pointwise proposal factorization on each decomposed composite path.
-/

import «03b_product_of_sums»
import «04_defect_corrected_kernel»

namespace PaperAE004

def proposalActionWeight {α : Type}
    (proposal action : α → Int) (x : α) : Int :=
  proposal x * action x

def proposalWeightedContribution {α : Type}
    (eval proposal action : α → Int) (x : α) : Int :=
  eval x * proposalActionWeight proposal action x

theorem proposal_action_weight_factorizes
    {Boundary Left Right : Type}
    (proposalLeft actionLeft : Left → Int)
    (proposalRight actionRight : Right → Int)
    (globalProposal globalAction : SegmentPair Boundary Left Right → Int)
    (p : SegmentPair Boundary Left Right)
    (hProposal :
      globalProposal p = proposalRight p.right * proposalLeft p.left)
    (hAction :
      globalAction p = actionRight p.right * actionLeft p.left) :
    proposalActionWeight globalProposal globalAction p =
      proposalActionWeight proposalRight actionRight p.right *
        proposalActionWeight proposalLeft actionLeft p.left := by
  simp [
    proposalActionWeight,
    hProposal,
    hAction,
    Int.mul_left_comm,
    Int.mul_comm
  ]

theorem proposal_weighted_pair_sum_reindexing_under_G1_G2_G3_G4
    {Boundary Left Right : Type}
    (rows : List (List (SegmentPair Boundary Left Right)))
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (proposalLeft actionLeft : Left → Int)
    (proposalRight actionRight : Right → Int)
    (globalEval globalProposal globalAction :
      SegmentPair Boundary Left Right → Int)
    (hEval :
      ∀ p, p ∈ flatten rows → globalEval p = evalRight p.right * evalLeft p.left)
    (hProposal :
      ∀ p, p ∈ flatten rows →
        globalProposal p = proposalRight p.right * proposalLeft p.left)
    (hAction :
      ∀ p, p ∈ flatten rows →
        globalAction p = actionRight p.right * actionLeft p.left) :
    flatKernel rows
        (proposalWeightedContribution globalEval globalProposal globalAction) =
      boundaryKernel rows
        (factoredContribution (Boundary := Boundary)
          evalLeft evalRight
          (proposalActionWeight proposalLeft actionLeft)
          (proposalActionWeight proposalRight actionRight)) := by
  exact kernel_pair_sum_reindexing_under_G1_G2_G3 rows
    evalLeft evalRight
    (proposalActionWeight proposalLeft actionLeft)
    (proposalActionWeight proposalRight actionRight)
    globalEval
    (proposalActionWeight globalProposal globalAction)
    hEval
    (fun p hp =>
      proposal_action_weight_factorizes
        proposalLeft actionLeft proposalRight actionRight
        globalProposal globalAction p
        (hProposal p hp) (hAction p hp))

#print axioms PaperAE004.proposal_action_weight_factorizes
#print axioms PaperAE004.proposal_weighted_pair_sum_reindexing_under_G1_G2_G3_G4

theorem proposal_weighted_composition_under_G1_G2_G3_G4
    {Boundary Left Right : Type}
    (rows : List (BoundaryRow Boundary Left Right))
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (proposalLeft actionLeft : Left → Int)
    (proposalRight actionRight : Right → Int)
    (globalEval globalProposal globalAction :
      SegmentPair Boundary Left Right → Int)
    (hEval :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalEval p = evalRight p.right * evalLeft p.left)
    (hProposal :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalProposal p = proposalRight p.right * proposalLeft p.left)
    (hAction :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalAction p = actionRight p.right * actionLeft p.left) :
    flatKernel (rows.map BoundaryRow.pairs)
        (proposalWeightedContribution globalEval globalProposal globalAction) =
      matrixKernel rows
        (fun left => evalLeft left *
          proposalActionWeight proposalLeft actionLeft left)
        (fun right => evalRight right *
          proposalActionWeight proposalRight actionRight right) := by
  exact kernel_composition_under_G1_G2_G3 rows
    (fun left => evalLeft left *
      proposalActionWeight proposalLeft actionLeft left)
    (fun right => evalRight right *
      proposalActionWeight proposalRight actionRight right)
    globalEval
    (proposalActionWeight globalProposal globalAction)
    (fun p hp => by
      unfold globalContribution pairProductContribution
      rw [hEval p hp]
      rw [proposal_action_weight_factorizes
        proposalLeft actionLeft proposalRight actionRight
        globalProposal globalAction p
        (hProposal p hp) (hAction p hp)]
      simp [Int.mul_assoc, Int.mul_left_comm, Int.mul_comm])

#print axioms PaperAE004.proposal_weighted_composition_under_G1_G2_G3_G4

end PaperAE004
