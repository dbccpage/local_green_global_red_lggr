/-
Copyright (c) 2026 Jeremy H. Carroll. All rights reserved.
Released under Apache 2.0 license.
Authors: Jeremy H. Carroll

Paper: The Omega Tower: Role Non-Impersonation and Authority Preservation in Agentic AI
Module: RoleNonImpersonation.RoleFailure
Description: Constructor-level formalization of the six conserved authority roles,
the six characteristic failure modes, and their pairwise injective/invertible correspondence.
-/

namespace RoleNonImpersonation

/-- The six conserved roles in an authority-preserving agentic architecture. -/
inductive Role where
  | obstruction : Role
  | authority : Role
  | transport : Role
  | comparison : Role
  | shadow : Role
  | residual : Role
  deriving DecidableEq, Repr

/-- The six characteristic authority failure modes arising from role collapse. -/
inductive FailureMode where
  | undetectedObstruction : FailureMode
  | proposalBecomesAction : FailureMode
  | silentRepresentationMutation : FailureMode
  | comparisonBecomesLaundering : FailureMode
  | continuumShadowBecomesFakeAuthority : FailureMode
  | residualGetsHiddenOrRenamed : FailureMode
  deriving DecidableEq, Repr

/-- The canonical bijection mapping a removed or collapsed role to its characteristic failure mode. -/
def roleToFailure : Role → FailureMode
  | Role.obstruction => FailureMode.undetectedObstruction
  | Role.authority => FailureMode.proposalBecomesAction
  | Role.transport => FailureMode.silentRepresentationMutation
  | Role.comparison => FailureMode.comparisonBecomesLaundering
  | Role.shadow => FailureMode.continuumShadowBecomesFakeAuthority
  | Role.residual => FailureMode.residualGetsHiddenOrRenamed

/-- The inverse mapping recovering the removed role from its observed failure mode. -/
def failureToRole : FailureMode → Role
  | FailureMode.undetectedObstruction => Role.obstruction
  | FailureMode.proposalBecomesAction => Role.authority
  | FailureMode.silentRepresentationMutation => Role.transport
  | FailureMode.comparisonBecomesLaundering => Role.comparison
  | FailureMode.continuumShadowBecomesFakeAuthority => Role.shadow
  | FailureMode.residualGetsHiddenOrRenamed => Role.residual

/-- Left inverse: failureToRole (roleToFailure r) = r for all roles. -/
@[simp]
theorem failureToRole_roleToFailure (r : Role) : failureToRole (roleToFailure r) = r := by
  cases r <;> rfl

/-- Right inverse: roleToFailure (failureToRole f) = f for all failure modes. -/
@[simp]
theorem roleToFailure_failureToRole (f : FailureMode) : roleToFailure (failureToRole f) = f := by
  cases f <;> rfl

/-- Injectivity of the roleToFailure mapping. Distinct roles have distinct failure modes. -/
theorem roleToFailure_injective (r1 r2 : Role) (h : roleToFailure r1 = roleToFailure r2) : r1 = r2 := by
  have h_inv : failureToRole (roleToFailure r1) = failureToRole (roleToFailure r2) := congrArg failureToRole h
  rw [failureToRole_roleToFailure, failureToRole_roleToFailure] at h_inv
  exact h_inv

/-- Contrapositive injectivity: r1 ≠ r2 implies roleToFailure r1 ≠ roleToFailure r2. -/
theorem roleToFailure_ne_of_ne (r1 r2 : Role) (h : r1 ≠ r2) : roleToFailure r1 ≠ roleToFailure r2 := by
  intro h_eq
  exact h (roleToFailure_injective r1 r2 h_eq)

/-- Injectivity of the failureToRole mapping. -/
theorem failureToRole_injective (f1 f2 : FailureMode) (h : failureToRole f1 = failureToRole f2) : f1 = f2 := by
  have h_inv : roleToFailure (failureToRole f1) = roleToFailure (failureToRole f2) := congrArg roleToFailure h
  rw [roleToFailure_failureToRole, roleToFailure_failureToRole] at h_inv
  exact h_inv

/-- Model of role collapse with optional reintroduction. -/
def collapseOutcome (removed : Role) (reintroduced : Bool) : Option FailureMode :=
  if reintroduced then none else some (roleToFailure removed)

/-- Theorem: Collapsing a role without reintroducing equivalent machinery hits the named failure. -/
theorem collapse_without_reintroduction_hits_named_failure (r : Role) :
    collapseOutcome r false = some (roleToFailure r) := by
  rfl

/-- Theorem: Observing a failure mode uniquely identifies the removed role via the inverse mapping. -/
theorem collapse_failure_identifies_removed_role (r : Role) (f : FailureMode)
    (h : collapseOutcome r false = some f) : failureToRole f = r := by
  injection h with h_eq
  rw [← h_eq, failureToRole_roleToFailure]

/-- Readiness predicate: all six obligations must be discharged. -/
structure ObligationStatus where
  obstructionDischarged : Bool
  authorityDischarged : Bool
  transportDischarged : Bool
  comparisonDischarged : Bool
  shadowDischarged : Bool
  residualDischarged : Bool
  deriving DecidableEq, Repr

def isGloballyReady (status : ObligationStatus) : Bool :=
  status.obstructionDischarged &&
  status.authorityDischarged &&
  status.transportDischarged &&
  status.comparisonDischarged &&
  status.shadowDischarged &&
  status.residualDischarged

/-- Theorem: If any obligation is missing (false), the system is not globally ready. -/
theorem missing_obligation_not_ready (s : ObligationStatus) (h : s.obstructionDischarged = false) :
    isGloballyReady s = false := by
  unfold isGloballyReady
  rw [h]
  rfl

theorem missing_authority_not_ready (s : ObligationStatus) (h : s.authorityDischarged = false) :
    isGloballyReady s = false := by
  unfold isGloballyReady
  rw [h]
  cases s.obstructionDischarged <;> rfl

end RoleNonImpersonation
