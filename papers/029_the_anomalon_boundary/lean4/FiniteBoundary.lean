namespace AnomalonBoundary

inductive DefectStatus where
  | vanishesAsGauge
  | activeIncoherence
  | survivingPrimitiveDifference
  deriving DecidableEq, Repr

def classify (isExact isClosed : Bool) (closureDefect : Int) : Option DefectStatus :=
  if closureDefect < 0 then
    none
  else if isExact then
    if !isClosed || closureDefect > 0 then none else some DefectStatus.vanishesAsGauge
  else if !isClosed || closureDefect > 0 then
    some DefectStatus.activeIncoherence
  else
    some DefectStatus.survivingPrimitiveDifference

theorem exact_closed_vanishes :
    classify true true 0 = some DefectStatus.vanishesAsGauge := rfl

theorem unclosed_is_active :
    classify false false 1 = some DefectStatus.activeIncoherence := rfl

theorem closed_nonexact_survives :
    classify false true 0 = some DefectStatus.survivingPrimitiveDifference := rfl

def applyD0 (a b c : Int) : Int × Int × Int :=
  (-a + b, -b + c, a - c)

def d1Zero (_h : Int × Int × Int) : Int :=
  0

def d1Face (h : Int × Int × Int) : Int :=
  h.1 + h.2.1 + h.2.2

theorem c3_zero_coboundary (a b c : Int) : d1Zero (applyD0 a b c) = 0 := rfl

theorem c3_exact_witness : applyD0 2 0 1 = (-2, 1, 1) := by
  decide

theorem c3_cycle_closed : d1Zero (1, 1, 1) = 0 := rfl

theorem c3_cycle_not_exact (a b c : Int) : applyD0 a b c ≠ (1, 1, 1) := by
  intro h
  have h1 : -a + b = 1 := congrArg (fun p : Int × Int × Int => p.1) h
  have h2 : -b + c = 1 := congrArg (fun p : Int × Int × Int => p.2.1) h
  have h3 : a - c = 1 := congrArg (fun p : Int × Int × Int => p.2.2) h
  have hsum : (-a + b) + (-b + c) + (a - c) = 3 := by
    rw [h1, h2, h3]
    decide
  have hzero : (-a + b) + (-b + c) + (a - c) = 0 := by
    omega
  omega

theorem filled_triangle_comp (a b c : Int) : d1Face (applyD0 a b c) = 0 := by
  simp [d1Face, applyD0]
  omega

theorem filled_triangle_curvature : d1Face (1, 0, 0) = 1 := by
  decide

theorem bad_square_not_complex :
    ((1 * 1 + 1 * 0), (1 * 0 + 1 * 1)) ≠ ((0 : Int), 0) := by
  decide

inductive Continuation where
  | typedRefusal
  | liftRequest
  | restartSeed
  deriving DecidableEq, Repr

inductive ContinuationStatus where
  | refusalRecorded
  | liftRequested
  | restartScheduled
  | liftAuthorized
  deriving DecidableEq, Repr

def requestStatus : Continuation → ContinuationStatus
  | Continuation.typedRefusal => ContinuationStatus.refusalRecorded
  | Continuation.liftRequest => ContinuationStatus.liftRequested
  | Continuation.restartSeed => ContinuationStatus.restartScheduled

theorem request_refusal : requestStatus Continuation.typedRefusal = ContinuationStatus.refusalRecorded := rfl

theorem request_lift : requestStatus Continuation.liftRequest = ContinuationStatus.liftRequested := rfl

theorem request_restart : requestStatus Continuation.restartSeed = ContinuationStatus.restartScheduled := rfl

def authorizeLift (metric : Int) : Option ContinuationStatus :=
  if metric > 0 then some ContinuationStatus.liftAuthorized else none

theorem authorize_positive : authorizeLift 1 = some ContinuationStatus.liftAuthorized := by
  decide

theorem authorize_zero : authorizeLift 0 = none := by
  decide

def promotesAuthority : Bool :=
  false

theorem anomalon_does_not_promote : promotesAuthority = false := rfl

structure KnowableRoles where
  carrier : Bool
  localState : Bool
  gauge : Bool
  coboundary : Bool
  comparison : Bool
  residual : Bool
  closure : Bool
  observer : Bool
  terminal : Bool
  continuation : Bool
  deriving DecidableEq, Repr

def rolesComplete (r : KnowableRoles) : Bool :=
  r.carrier && r.localState && r.gauge && r.coboundary && r.comparison &&
    r.residual && r.closure && r.observer && r.terminal && r.continuation

def fullRoles : KnowableRoles where
  carrier := true
  localState := true
  gauge := true
  coboundary := true
  comparison := true
  residual := true
  closure := true
  observer := true
  terminal := true
  continuation := true

def brokenRoles : KnowableRoles :=
  { fullRoles with gauge := false, closure := false }

theorem full_roles_complete : rolesComplete fullRoles = true := rfl

theorem broken_roles_incomplete : rolesComplete brokenRoles = false := rfl

end AnomalonBoundary
