/-
Paper 020, Tier 0: local-green/global-red counterexample and phone-test totals.

This file mechanizes the smallest finite witness in the paper:
local validators can both pass while the composed/global evaluator fails.
It also records the integer totals behind the five-trace phone test.
-/

namespace PaperAE004

def b2i (b : Bool) : Int := if b then 1 else 0

def localProduct (e1 e2 : Bool) : Int := b2i e1 * b2i e2

def deltaEval (e1 e2 eg : Bool) : Int :=
  b2i eg - localProduct e1 e2

theorem local_green_global_red_counterexample :
    deltaEval true true false = -1 := by
  rfl

theorem deltaEval_range (e1 e2 eg : Bool) :
    deltaEval e1 e2 eg = -1 ∨
    deltaEval e1 e2 eg = 0 ∨
    deltaEval e1 e2 eg = 1 := by
  cases e1 <;> cases e2 <;> cases eg <;> decide

/- The five traces from Paper 020 §1.6:
   (true,true,true), (true,true,false), (true,true,false),
   (true,false,false), (false,true,false). -/

def phoneLocalSum : Int :=
  localProduct true true +
  localProduct true true +
  localProduct true true +
  localProduct true false +
  localProduct false true

def phoneGlobalSum : Int :=
  b2i true +
  b2i false +
  b2i false +
  b2i false +
  b2i false

def phoneDeltaSum : Int :=
  deltaEval true true true +
  deltaEval true true false +
  deltaEval true true false +
  deltaEval true false false +
  deltaEval false true false

def phoneNegativeDefectCount : Nat :=
  (if deltaEval true true true == -1 then 1 else 0) +
  (if deltaEval true true false == -1 then 1 else 0) +
  (if deltaEval true true false == -1 then 1 else 0) +
  (if deltaEval true false false == -1 then 1 else 0) +
  (if deltaEval false true false == -1 then 1 else 0)

theorem phone_local_sum : phoneLocalSum = 3 := by
  rfl

theorem phone_global_sum : phoneGlobalSum = 1 := by
  rfl

theorem phone_delta_sum : phoneDeltaSum = -2 := by
  rfl

theorem phone_identity_global_minus_local :
    phoneGlobalSum - phoneLocalSum = phoneDeltaSum := by
  rfl

theorem phone_negative_defect_count :
    phoneNegativeDefectCount = 2 := by
  decide

#print axioms PaperAE004.local_green_global_red_counterexample
#print axioms PaperAE004.deltaEval_range
#print axioms PaperAE004.phone_identity_global_minus_local

end PaperAE004
