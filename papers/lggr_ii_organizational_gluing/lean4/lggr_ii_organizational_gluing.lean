import core

namespace LGGR2

open PaperAE005

theorem governance_prerequisites_require_boundary_owner
    (c : BoundaryClosureConditions)
    (h : governancePrerequisitesSatisfied c = true) :
    c.gAuth = true :=
  governance_prerequisites_require_auth c h

-- Compatibility alias retained for earlier clients.
theorem certified_closure_requires_boundary_owner
    (c : BoundaryClosureConditions)
    (h : certifiedClosurePossible c = true) :
    c.gAuth = true :=
  governance_prerequisites_require_boundary_owner c h

theorem boundary_owner_alone_is_insufficient :
    ∃ c : BoundaryClosureConditions,
      c.gAuth = true ∧ certifiedClosurePossible c = false :=
  boundary_owner_not_sufficient

theorem non_additivity_range_obstruction :
    ∃ d1 d2 d3 : Int,
      BinaryDefect d1 ∧ BinaryDefect d2 ∧ BinaryDefect d3 ∧ ¬ BinaryDefect (d1 + d2 + d3) :=
  three_binary_defects_sum_can_leave_binary_range

theorem weak_sufficiency_counterexample :
    ∃ b : BooleanBoundary,
      weakBoundarySufficiency b ∧
      b.gAuth = true ∧
      b.gTime = true ∧
      ¬ evaluatorFactorization b :=
  weak_boundary_sufficiency_does_not_force_factorization

theorem worked_instance_lggr :
    orgDelta false true = -1 :=
  organizational_lggr_instance

theorem aligned_detector_collapses (eG : Bool) :
    orgDelta eG eG = 0 :=
  aligned_validator_collapsing_detector eG

theorem red_is_sound_detection (eG : Bool) (eLocalProd : Bool)
    (h : orgDelta eG eLocalProd = -1) :
    eLocalProd = true ∧ eG = false :=
  red_verdict_sound_detection eG eLocalProd h

end LGGR2
