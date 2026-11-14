/-
Paper 020, Tier 5: activation-density algebra and single-crossing sign pattern.

This file deliberately does not claim a full Mathlib calculus formalization.
It mechanizes the algebraic derivative expression used in the paper and the
sign-pattern consequence under an explicit single-crossing hypothesis.  The
derivation of single-crossing from primitive curve assumptions remains PL-020-1.
-/

import «05_proposal_weighted_composition»

namespace PaperAE004

def activationScore (capability defect : Int) : Int :=
  capability * (1 - defect)

def activationDerivativeExpression
    (capability capabilityDeriv defect defectDeriv : Int) : Int :=
  capabilityDeriv * (1 - defect) - capability * defectDeriv

theorem activation_derivative_formula
    (capability capabilityDeriv defect defectDeriv : Int) :
    activationDerivativeExpression
      capability capabilityDeriv defect defectDeriv =
        capabilityDeriv * (1 - defect) - capability * defectDeriv := by
  rfl

theorem activation_first_order_condition
    (capability capabilityDeriv defect defectDeriv : Int)
    (h :
      activationDerivativeExpression
        capability capabilityDeriv defect defectDeriv = 0) :
    capabilityDeriv * (1 - defect) = capability * defectDeriv := by
  unfold activationDerivativeExpression at h
  exact Int.sub_eq_zero.mp h

def SingleCrossing (derivative : Int → Int) (alphaStar : Int) : Prop :=
  (∀ alpha, alpha < alphaStar → 0 < derivative alpha) ∧
  (∀ alpha, alphaStar < alpha → derivative alpha < 0)

theorem sign_positive_before_single_crossing
    (derivative : Int → Int) (alphaStar alpha : Int)
    (h : SingleCrossing derivative alphaStar)
    (hlt : alpha < alphaStar) :
    0 < derivative alpha :=
  h.1 alpha hlt

theorem sign_negative_after_single_crossing
    (derivative : Int → Int) (alphaStar alpha : Int)
    (h : SingleCrossing derivative alphaStar)
    (hgt : alphaStar < alpha) :
    derivative alpha < 0 :=
  h.2 alpha hgt

def alwaysPositiveDerivative (_alpha : Int) : Int := 1

theorem always_positive_derivative_has_no_negative_side :
    ¬ ∃ alpha : Int, alwaysPositiveDerivative alpha < 0 := by
  intro h
  cases h with
  | intro alpha hneg =>
      change (1 : Int) < 0 at hneg
      have hnot : ¬ (1 : Int) < 0 := by
        decide
      exact hnot hneg

#print axioms PaperAE004.activation_derivative_formula
#print axioms PaperAE004.activation_first_order_condition
#print axioms PaperAE004.sign_positive_before_single_crossing
#print axioms PaperAE004.sign_negative_after_single_crossing
#print axioms PaperAE004.always_positive_derivative_has_no_negative_side

end PaperAE004
