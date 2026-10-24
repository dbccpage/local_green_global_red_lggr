/-!
# Core L023-03: Non-Additivity Audit and Direct Summation Range Obstruction

Mechanizes Lemma 4.2.1: Three binary channel defects in {-1, 0, 1}
cannot form a direct scalar sum for the binary evaluator defect channel, because
(-1) + (-1) + (-1) = -3 leaves {-1, 0, 1}.

Also establishes orgDelta_range, organizational_lggr_instance (rfl on 0 - 1 = -1),
and the complete defect trichotomy.
-/

namespace PaperAE005

def BinaryDefect (x : Int) : Prop :=
  x = -1 ∨ x = 0 ∨ x = 1

theorem three_binary_defects_sum_can_leave_binary_range :
    ∃ d1 d2 d3 : Int, BinaryDefect d1 ∧ BinaryDefect d2 ∧ BinaryDefect d3 ∧ ¬ BinaryDefect (d1 + d2 + d3) := by
  refine ⟨-1, -1, -1, ?_, ?_, ?_, ?_⟩
  · left; rfl
  · left; rfl
  · left; rfl
  · intro h
    rcases h with h | h | h <;> revert h <;> decide

def orgDelta (eG : Bool) (eLocalProd : Bool) : Int :=
  (if eG then 1 else 0) - (if eLocalProd then 1 else 0)

theorem orgDelta_range (eG : Bool) (eLocalProd : Bool) :
    BinaryDefect (orgDelta eG eLocalProd) := by
  unfold orgDelta BinaryDefect
  cases eG <;> cases eLocalProd <;> decide

theorem organizational_lggr_instance :
    orgDelta false true = -1 := by
  rfl

theorem organizational_all_pass_instance :
    orgDelta true true = 0 := by
  rfl

theorem organizational_all_fail_instance :
    orgDelta false false = 0 := by
  rfl

theorem organizational_unearned_success_instance :
    orgDelta true false = 1 := by
  rfl

theorem orgDelta_is_negative_one_iff (eG : Bool) (eLocalProd : Bool) :
    orgDelta eG eLocalProd = -1 ↔ (eG = false ∧ eLocalProd = true) := by
  unfold orgDelta
  cases eG <;> cases eLocalProd <;> decide

end PaperAE005
