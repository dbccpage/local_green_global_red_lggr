/-
Copyright (c) 2026 Jeremy H. Carroll. All rights reserved.
Released under Apache 2.0 license.
Authors: Jeremy H. Carroll

Paper: The Omega Tower: Role Non-Impersonation and Authority Preservation in Agentic AI
Module: RoleNonImpersonation.AuthorityResidual
Description: Formalization of the Proposal/Authority boundary, terminal constructors,
disjointness theorems, replayable token validity, and residual honesty classification.
-/

namespace RoleNonImpersonation

/-- An unverified proposal entering the agentic pipeline. -/
structure Proposal where
  id : Nat
  payload : String
  deriving DecidableEq, Repr

/-- A verified authority token carrying explicit verifier and replay custody. -/
structure AuthorityToken where
  proposalId : Nat
  verifier : String
  replayable : Bool
  receiptDigest : String
  deriving DecidableEq, Repr

/-- Terminal output constructors for an execution pipeline. -/
inductive Terminal where
  | authority (token : AuthorityToken) : Terminal
  | residualClosed (residualClass : String) : Terminal
  | residualOpen (boundaryDefect : String) : Terminal
  | refusal (reason : String) : Terminal
  | budgetUnknown : Terminal
  deriving DecidableEq, Repr

def isAuthorityTerminal : Terminal → Bool
  | Terminal.authority _ => true
  | _ => false

def isResidualTerminal : Terminal → Bool
  | Terminal.residualClosed _ => true
  | Terminal.residualOpen _ => true
  | _ => false

def isRefusalTerminal : Terminal → Bool
  | Terminal.refusal _ => true
  | Terminal.budgetUnknown => true
  | _ => false

/-- Terminal Disjointness: Authority is disjoint from Residual. -/
theorem authority_not_residual (t : Terminal) (h : isAuthorityTerminal t = true) :
    isResidualTerminal t = false := by
  cases t <;> trivial

/-- Terminal Disjointness: Authority is disjoint from Refusal. -/
theorem authority_not_refusal (t : Terminal) (h : isAuthorityTerminal t = true) :
    isRefusalTerminal t = false := by
  cases t <;> trivial

/-- Terminal Disjointness: Residual is disjoint from Refusal. -/
theorem residual_not_refusal (t : Terminal) (h : isResidualTerminal t = true) :
    isRefusalTerminal t = false := by
  cases t <;> trivial

/-- Validity specification for an authority token:
Must match proposal id, be certified replayable, have a non-empty verifier identity,
and carry an explicit cryptographic receipt digest. -/
def isValidAuthorityToken (p : Proposal) (tok : AuthorityToken) : Prop :=
  tok.proposalId = p.id ∧
  tok.replayable = true ∧
  tok.verifier ≠ "" ∧
  tok.receiptDigest ≠ ""

/-- The formal Authority dependent type Auth(p):
Requires that the pipeline outputs an authority terminal with a valid, replayable token. -/
def Auth (p : Proposal) (pipeline : Proposal → Terminal) : Prop :=
  ∃ tok, pipeline p = Terminal.authority tok ∧ isValidAuthorityToken p tok

/-- Theorem: A pipeline yielding a residual terminal confers NO authority. -/
theorem residual_output_not_auth (p : Proposal) (pipe : Proposal → Terminal) (r : String)
    (h : pipe p = Terminal.residualClosed r) : ¬ Auth p pipe := by
  intro h_auth
  rcases h_auth with ⟨tok, h_pipe, _⟩
  rw [h] at h_pipe
  contradiction

/-- Theorem: A pipeline yielding an open residual confers NO authority. -/
theorem residual_open_not_auth (p : Proposal) (pipe : Proposal → Terminal) (b : String)
    (h : pipe p = Terminal.residualOpen b) : ¬ Auth p pipe := by
  intro h_auth
  rcases h_auth with ⟨tok, h_pipe, _⟩
  rw [h] at h_pipe
  contradiction

/-- Theorem: A pipeline yielding a refusal confers NO authority. -/
theorem refusal_output_not_auth (p : Proposal) (pipe : Proposal → Terminal) (err : String)
    (h : pipe p = Terminal.refusal err) : ¬ Auth p pipe := by
  intro h_auth
  rcases h_auth with ⟨tok, h_pipe, _⟩
  rw [h] at h_pipe
  contradiction

/-- Theorem: A pipeline yielding budget unknown confers NO authority. -/
theorem budget_unknown_not_auth (p : Proposal) (pipe : Proposal → Terminal)
    (h : pipe p = Terminal.budgetUnknown) : ¬ Auth p pipe := by
  intro h_auth
  rcases h_auth with ⟨tok, h_pipe, _⟩
  rw [h] at h_pipe
  contradiction

/-- Theorem: An unreplayed token cannot satisfy the validity contract. -/
theorem unreplayed_token_invalid (p : Proposal) (tok : AuthorityToken)
    (h : tok.replayable = false) : ¬ isValidAuthorityToken p tok := by
  intro h_val
  have h_rep := h_val.2.1
  rw [h] at h_rep
  contradiction

/-- Three-way core cohomological classification of residuals. -/
inductive CoreResidualClass where
  | resolvedExact : CoreResidualClass
  | closedResidual : CoreResidualClass
  | openResidual : CoreResidualClass
  deriving DecidableEq, Repr

def classifyResidual (isExact : Bool) (isClosed : Bool) : CoreResidualClass :=
  if isExact then CoreResidualClass.resolvedExact
  else if isClosed then CoreResidualClass.closedResidual
  else CoreResidualClass.openResidual

/-- Honest classification theorem: Non-exact defect cannot be classified as resolved exact. -/
theorem non_exact_residual_not_resolved (isClosed : Bool) :
    classifyResidual false isClosed ≠ CoreResidualClass.resolvedExact := by
  unfold classifyResidual
  split
  · contradiction
  · split <;> intro h <;> contradiction

/-- Renaming contradiction theorem: Claiming resolved exact when defect is non-exact
is a provable contradiction. -/
theorem renamed_non_exact_as_resolved_contradiction (isClosed : Bool)
    (h_claimed : classifyResidual false isClosed = CoreResidualClass.resolvedExact) : False := by
  have h_neq := non_exact_residual_not_resolved isClosed
  exact h_neq h_claimed

end RoleNonImpersonation
