import «03_non_additivity»

namespace PaperAE005

theorem aligned_validator_collapsing_detector (eG : Bool) :
    orgDelta eG eG = 0 := by
  cases eG <;> rfl

theorem aligned_validator_proxy_collapsing_detector (eG : Bool) (other_passes : Bool)
    (h_other : other_passes = true) :
    orgDelta eG (eG && other_passes) = 0 := by
  rw [h_other]
  cases eG <;> rfl

theorem red_verdict_sound_detection (eG : Bool) (eLocalProd : Bool)
    (h : orgDelta eG eLocalProd = -1) :
    eLocalProd = true ∧ eG = false := by
  cases eG <;> cases eLocalProd <;> revert h <;> decide

theorem green_verdict_unsound_as_certificate :
    ∃ eG eLocalProd : Bool, orgDelta eG eLocalProd = 0 ∧ ¬ (eG = true ∧ eLocalProd = true) := by
  refine ⟨false, false, by rfl, by decide⟩
-- Defect-focused aliases; earlier names remain available for compatibility.
theorem zero_defect_does_not_imply_all_pass :
    ∃ eG eLocalProd : Bool, orgDelta eG eLocalProd = 0 ∧ ¬ (eG = true ∧ eLocalProd = true) :=
  green_verdict_unsound_as_certificate

theorem aligned_local_product_forces_zero_defect (eG : Bool) :
    orgDelta eG eG = 0 :=
  aligned_validator_collapsing_detector eG

theorem aligned_validator_forces_zero_defect (eG : Bool) :
    orgDelta eG eG = 0 :=
  aligned_local_product_forces_zero_defect eG

end PaperAE005
