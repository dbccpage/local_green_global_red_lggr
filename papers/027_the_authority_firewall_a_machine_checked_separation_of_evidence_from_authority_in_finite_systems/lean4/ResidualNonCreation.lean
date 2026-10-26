/-
Copyright (c) 2026 Jeremy H. Carroll. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/

/-!
# Residual Non-Creation, Seven Operational Guards, and Typed Component Bridge

Formal verification of:
1. Pointwise Coproduct Separation Theorem (Theorem 3.1):
   In a binary coproduct terminal type `Terminal := AuthEvidence ⊕ ResidualOutcome`,
   residual terminals mapped via `Sum.inr` cannot inhabit the authority summand `Sum.inl`.
2. Dependent Family Emptiness (Theorem 3.2):
   Whenever the residual layer is inhabited, the universal family of authority extractors is empty.
3. Mechanization of the Seven Operational Guards (Definition 2.2, IsAuth_S):
   Formalization of validHash, replayMatches, terminalizerPresent, kappaZero,
   deltaZero, descentWitness, and replayFresh.
4. Guard Factorization Theorem:
   Operational authority IsAuth_S factors through structural coproduct authority IsAuth.
5. Discrete Diagnostic Cochain Complex & Quotient:
   0-cochains C⁰, 1-cochains C¹, coboundary d⁰, and obstruction predicate (nonzero class in Q¹).
6. Typed Component Bridge:
   The diagnostic cochain route R : Q¹_{≠ 0} → Sum.inr and guarded authority route Π♯ : GuardedAuthEvidence → Sum.inl
   have strictly disjoint images; non-repairable obstructions strictly falsify truthful delta guards.

Namespace: `OmegaCore.ResidualClosureLayer`
Axioms: None (fully constructive, `#print axioms` reports no axioms).
-/

namespace OmegaCore.ResidualClosureLayer

/- =========================================================================
   Part 1: Raw Coproduct Separation Core (Zero-Guard Pointwise Theorem)
   ========================================================================= -/

/-- Authority terminal payload inhabiting the `Sum.inl` summand. -/
structure AuthEvidence where
  packetId : String
  terminalizerId : String
  replayable : Bool
  deriving DecidableEq, Repr

/-- Residual terminalizer codomain inhabiting the `Sum.inr` summand. -/
inductive ResidualOutcome where
  | residualClass : String → ResidualOutcome
  | residualFailure : String → ResidualOutcome
  deriving DecidableEq, Repr

/-- The binary coproduct terminal type `𝕋 = 𝕋_auth ⊕ (𝕋_res + 𝔽_res)`. -/
abbrev Terminal : Type := AuthEvidence ⊕ ResidualOutcome

/-- Authority predicate: a terminal value lies in the `Sum.inl` summand. -/
def IsAuth (t : Terminal) : Prop := ∃ e : AuthEvidence, t = Sum.inl e

/-- Residual terminalizer mapping every residual into the `Sum.inr` summand. -/
abbrev residualTerminal (r : ResidualOutcome) : Terminal := Sum.inr r

/-- Pointwise Coproduct Separation Theorem (Theorem 3.1):
    Residual terminalization produces a value in the residual summand and
    cannot identify that value with an authority terminal. -/
theorem residual_not_auth (r : ResidualOutcome) : ¬ IsAuth (residualTerminal r) := by
  intro ⟨e, he⟩
  contradiction

/-- Authority extractor dependent family over all residual outcomes. -/
abbrev AuthExtractor : Prop := ∀ (r : ResidualOutcome), IsAuth (residualTerminal r)

/-- Dependent-Family Emptiness (Theorem 3.2):
    Whenever the residual layer is inhabited, the universal family of
    authority extractors is uninhabited. -/
theorem nat_residual_auth_empty (r0 : ResidualOutcome) : AuthExtractor → False := by
  intro α
  exact residual_not_auth r0 (α r0)

/-- Positive unpacking: any authority terminal carries an `AuthEvidence` record. -/
theorem authority_only_via_evidence (t : Terminal) (h : IsAuth t) :
    ∃ e : AuthEvidence, t = Sum.inl e := h

/-- Concrete finite witness proving inhabitation of `ResidualOutcome`. -/
def residualWitness : ResidualOutcome :=
  ResidualOutcome.residualClass "q42"

/-- Unconditional emptiness of the authority extractor family using the concrete witness. -/
theorem authExtractor_empty : AuthExtractor → False :=
  nat_residual_auth_empty residualWitness


/- =========================================================================
   Part 2: Discrete Diagnostic Cochain Complex
   ========================================================================= -/

/-- Directed cell complex topology for discrete transition networks. -/
structure ComplexTopology (V E : Type) where
  src : E → V
  tgt : E → V

/-- Discrete 0-cochains: potentials on vertices (integer-valued). -/
def C0 (V : Type) := V → Int

/-- Discrete 1-cochains: transition discrepancies on edges. -/
def C1 (E : Type) := E → Int

/-- Discrete coboundary operator d⁰ : C⁰ → C¹. -/
def d0 {V E : Type} (top : ComplexTopology V E) (s : C0 V) : C1 E :=
  fun e => s (top.tgt e) - s (top.src e)

/-- Exact repair predicate: a 1-cochain is a coboundary (zero defect mass δ = 0). -/
def IsCoboundary {V E : Type} (top : ComplexTopology V E) (c : C1 E) : Prop :=
  ∃ s : C0 V, d0 top s = c

/-- Non-repairable obstruction predicate: nonzero class in Q¹ = C¹ / im(d⁰). -/
def IsObstruction {V E : Type} (top : ComplexTopology V E) (c : C1 E) : Prop :=
  ¬ IsCoboundary top c


/- =========================================================================
   Part 3: Mechanization of the Seven Operational Guards (IsAuth_S)
   ========================================================================= -/

/-- The seven operational guards of Definition 2.2. -/
structure SevenGuards where
  validHash : Bool
  replayMatches : Bool
  terminalizerPresent : Bool
  kappaZero : Bool
  deltaZero : Bool
  descentWitness : Bool
  replayFresh : Bool
  deriving DecidableEq, Repr

/-- Conjunction of all seven operational guards. -/
def AllGuardsPass (g : SevenGuards) : Prop :=
  g.validHash = true ∧
  g.replayMatches = true ∧
  g.terminalizerPresent = true ∧
  g.kappaZero = true ∧
  g.deltaZero = true ∧
  g.descentWitness = true ∧
  g.replayFresh = true

/-- Guarded authority evidence requiring proof of all seven guards. -/
structure GuardedAuthEvidence where
  packetId : String
  verifierId : String
  guards : SevenGuards
  guards_pass : AllGuardsPass guards

/-- Diagnostic residual codomain for obstruction reports and guard failures. -/
inductive DiagnosticResidual where
  | nonRepairableObstruction (code : String) (desc : String) : DiagnosticResidual
  | guardFailure (guard_name : String) : DiagnosticResidual
  | unverifiedSearch (kappa : Nat) : DiagnosticResidual
  deriving DecidableEq, Repr

/-- Guarded terminal coproduct 𝕋_guarded = GuardedAuthEvidence ⊕ DiagnosticResidual. -/
abbrev GuardedTerminal := GuardedAuthEvidence ⊕ DiagnosticResidual

/-- Guarded summand membership predicate. -/
def IsGuardedAuth (t : GuardedTerminal) : Prop :=
  ∃ e : GuardedAuthEvidence, t = Sum.inl e

/-- Operational seven-guard authority predicate IsAuth_S. -/
def IsAuth_S (t : GuardedTerminal) : Prop :=
  ∃ e : GuardedAuthEvidence, t = Sum.inl e ∧ AllGuardsPass e.guards

/-- Guard Factorization Theorem:
    Operational authority IsAuth_S factors through structural coproduct authority IsGuardedAuth. -/
theorem is_auth_s_factors_through_is_auth (t : GuardedTerminal) :
    IsAuth_S t → IsGuardedAuth t := by
  intro ⟨e, he_eq, _⟩
  exact ⟨e, he_eq⟩

/-- Guard Satisfaction Theorem:
    Any validly constructed GuardedAuthEvidence satisfies IsAuth_S. -/
theorem guarded_evidence_satisfies_is_auth_s (e : GuardedAuthEvidence) :
    IsAuth_S (Sum.inl e : GuardedTerminal) := by
  exact ⟨e, rfl, e.guards_pass⟩

/-- Diagnostic terminalizer mapping residual outcomes into Sum.inr. -/
def diagnosticTerminal (r : DiagnosticResidual) : GuardedTerminal :=
  Sum.inr r

/-- Pointwise constructor disjointness for guarded terminals:
    Diagnostic residuals cannot inhabit the guarded authority summand. -/
theorem diagnostic_not_guarded_auth (r : DiagnosticResidual) :
    ¬ IsGuardedAuth (diagnosticTerminal r) := by
  intro ⟨e, he⟩
  contradiction

/-- Diagnostic terminals cannot satisfy the operational seven-guard predicate. -/
theorem diagnostic_not_auth_s (r : DiagnosticResidual) :
    ¬ IsAuth_S (diagnosticTerminal r) := by
  intro h_s
  have h_auth := is_auth_s_factors_through_is_auth (diagnosticTerminal r) h_s
  exact diagnostic_not_guarded_auth r h_auth


/- =========================================================================
   Part 4: Typed Component Bridge
   ========================================================================= -/

/-- Canonical diagnostic route: maps an obstruction to a diagnostic terminal. -/
def diagnosticRoute (code : String) (desc : String) : GuardedTerminal :=
  Sum.inr (DiagnosticResidual.nonRepairableObstruction code desc)

/-- Canonical guarded authority route: maps verified evidence to an authority terminal. -/
def authorityRoute (e : GuardedAuthEvidence) : GuardedTerminal :=
  Sum.inl e

/-- Bridge Mutual Exclusion Theorem:
    The diagnostic cochain route and the guarded authority route have strictly disjoint images. -/
theorem bridge_mutual_exclusion
    (code : String) (desc : String)
    (e : GuardedAuthEvidence) :
    diagnosticRoute code desc ≠ authorityRoute e := by
  intro h_eq
  contradiction

/-- Bridge Soundness Theorem:
    A diagnostic route terminal carries no authority under either IsGuardedAuth or IsAuth_S. -/
theorem bridge_diagnostic_carries_no_authority (code : String) (desc : String) :
    ¬ IsGuardedAuth (diagnosticRoute code desc) ∧ ¬ IsAuth_S (diagnosticRoute code desc) := by
  constructor
  · intro ⟨e, he⟩
    contradiction
  · intro h_s
    have ⟨e, he⟩ := is_auth_s_factors_through_is_auth (diagnosticRoute code desc) h_s
    contradiction

/-- Truthful delta guard: deltaZero can only claim true if the cochain defect is a coboundary. -/
def DeltaGuardTruthful {V E : Type} (top : ComplexTopology V E) (g : SevenGuards) (c : C1 E) : Prop :=
  g.deltaZero = true → IsCoboundary top c

/-- Obstruction Defect Refusal Theorem:
    If a cochain is an obstruction (non-repairable), no evidence whose deltaZero
    guard is truthful can claim all seven guards pass for that cochain. -/
theorem obstruction_cannot_pass_truthful_guards
    {V E : Type} (top : ComplexTopology V E)
    (c : C1 E) (h_obs : IsObstruction top c)
    (g : SevenGuards) (h_truth : DeltaGuardTruthful top g c) :
    AllGuardsPass g → False := by
  intro h_pass
  have h_delta : g.deltaZero = true := h_pass.2.2.2.2.1
  have h_coboundary : IsCoboundary top c := h_truth h_delta
  exact h_obs h_coboundary

/-- Discrete Diagnostic Cochain Bridge:
    Maps an obstructed 1-cochain to the diagnostic residual terminal. -/
def cochainToDiagnostic {V E : Type} (_top : ComplexTopology V E)
    (_c : C1 E) (_h_obs : IsObstruction _top _c) : GuardedTerminal :=
  diagnosticRoute "NON_REPAIRABLE_OBSTRUCTION" "cochain has non-zero class in Q¹ = C¹/im(d⁰)"

/-- Cochain Bridge Terminal Disjointness:
    Any cochain proven to be an obstruction lands in a terminal that cannot be authority. -/
theorem cochain_bridge_obstruction_disjoint
    {V E : Type} (top : ComplexTopology V E)
    (c : C1 E) (h_obs : IsObstruction top c) :
    ¬ IsGuardedAuth (cochainToDiagnostic top c h_obs) := by
  intro ⟨e, he⟩
  contradiction

/-- Cochain Bridge Operational Disjointness:
    Any cochain proven to be an obstruction lands in a terminal that cannot satisfy IsAuth_S. -/
theorem cochain_bridge_obstruction_not_auth_s
    {V E : Type} (top : ComplexTopology V E)
    (c : C1 E) (h_obs : IsObstruction top c) :
    ¬ IsAuth_S (cochainToDiagnostic top c h_obs) := by
  intro h_s
  have h_auth := is_auth_s_factors_through_is_auth (cochainToDiagnostic top c h_obs) h_s
  exact cochain_bridge_obstruction_disjoint top c h_obs h_auth

/- =========================================================================
   Part 5: Axiom Verification (All Theorems Depend on Zero External Axioms)
   ========================================================================= -/

#print axioms residual_not_auth
#print axioms nat_residual_auth_empty
#print axioms authority_only_via_evidence
#print axioms authExtractor_empty
#print axioms is_auth_s_factors_through_is_auth
#print axioms guarded_evidence_satisfies_is_auth_s
#print axioms diagnostic_not_guarded_auth
#print axioms diagnostic_not_auth_s
#print axioms bridge_mutual_exclusion
#print axioms bridge_diagnostic_carries_no_authority
#print axioms obstruction_cannot_pass_truthful_guards
#print axioms cochain_bridge_obstruction_disjoint
#print axioms cochain_bridge_obstruction_not_auth_s

end OmegaCore.ResidualClosureLayer
