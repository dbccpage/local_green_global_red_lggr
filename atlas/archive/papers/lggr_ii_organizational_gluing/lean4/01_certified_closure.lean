namespace PaperAE005

structure BoundaryClosureConditions where
  gRep : Bool
  gAuth : Bool
  gTime : Bool
  deriving DecidableEq, Repr

def certifiedClosurePossible (c : BoundaryClosureConditions) : Bool :=
  c.gRep && c.gAuth && c.gTime

theorem certified_closure_requires_auth (c : BoundaryClosureConditions)
    (h : certifiedClosurePossible c = true) : c.gAuth = true := by
  unfold certifiedClosurePossible at h
  revert h
  cases c.gRep <;> cases c.gAuth <;> cases c.gTime <;> decide

theorem boundary_owner_not_sufficient :
    ∃ c : BoundaryClosureConditions, c.gAuth = true ∧ certifiedClosurePossible c = false := by
  refine ⟨⟨false, true, true⟩, by decide, by decide⟩

theorem owner_not_sufficient_without_rep :
    ∃ c : BoundaryClosureConditions, c.gAuth = true ∧ c.gRep = false ∧ certifiedClosurePossible c = false := by
  refine ⟨⟨false, true, true⟩, by decide, by decide, by decide⟩

theorem owner_not_sufficient_without_time :
    ∃ c : BoundaryClosureConditions, c.gAuth = true ∧ c.gTime = false ∧ certifiedClosurePossible c = false := by
  refine ⟨⟨true, true, false⟩, by decide, by decide, by decide⟩

theorem conjunction_requires_all_three (c : BoundaryClosureConditions) :
    certifiedClosurePossible c = true ↔ (c.gRep = true ∧ c.gAuth = true ∧ c.gTime = true) := by
  unfold certifiedClosurePossible
  cases c.gRep <;> cases c.gAuth <;> cases c.gTime <;> decide

theorem any_missing_blocks_closure (c : BoundaryClosureConditions)
    (h : c.gRep = false ∨ c.gAuth = false ∨ c.gTime = false) :
    certifiedClosurePossible c = false := by
  unfold certifiedClosurePossible
  rcases h with h1 | h2 | h3
  · rw [h1]; rfl
  · rw [h2]; cases c.gRep <;> rfl
  · rw [h3]; cases c.gRep <;> cases c.gAuth <;> rfl
-- Governance-focused aliases; earlier names remain available for compatibility.
abbrev governancePrerequisitesSatisfied := certifiedClosurePossible

theorem governance_prerequisites_require_auth (c : BoundaryClosureConditions)
    (h : governancePrerequisitesSatisfied c = true) : c.gAuth = true :=
  certified_closure_requires_auth c h

end PaperAE005
