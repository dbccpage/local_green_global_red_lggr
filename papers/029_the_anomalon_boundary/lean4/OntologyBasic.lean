/-!
Current authority boundary for the Omega Engine.

This module is intentionally prior to time, space, coordinates, Hilbert
spaces, probability, computation, triangles, infinity, and finiteness.  Those
are representation layers, typed structures, lifts, observers, or residual
packets.  They do not have authority solely by being expressible.

The current authority boundary used here is:

  Real₀ = PrimitiveDifference ∪ Structure

The declarations below do not add Lean kernel axioms.  They package the
Anomalon axiom set as explicit data so later files must carry the relevant
witnesses instead of silently promoting representation-layer language.

This file does not identify the most primitive cosmological object.  Carrier,
Primitive Difference, and Structure are typed authority/descent interfaces for
the current engine layer, not an origin theorem about the lower primitive layer.
-/

namespace OmegaCosmology
namespace Ontology

universe u v

/-- A primitive difference is a declared distinction with a measurement target. -/
structure PrimitiveDifference where
  Source : Sort u
  Target : Sort v
  delta : Source → Source → Target

/--
Structure carries two typed senses that must not be conflated (see PaperFOC000c §2.1
and `Ontology.Anomalon`):

* the `Carrier` field is CARRIER-Structure — a declared precondition that a
  `PrimitiveDifference` presupposes (its `Source`).  It does NOT result from
  obstruction;
* `resultsFromObstruction` marks RESIDUAL-Structure — what a primitive difference
  produces.

The remaining fields (`persists`, `composes`, `stabilizes`, `records`) may hold in
either sense.  All fields are deliberately propositional: specific domains must
instantiate them with their own certificates.  The carrier/residual order is a
definability order, never an authority order.
-/
structure Structure where
  /-- CARRIER-Structure: a declared precondition (the `Source` of a difference); it
  does not result from obstruction. -/
  Carrier : Sort u
  persists : Prop
  composes : Prop
  stabilizes : Prop
  records : Prop
  /-- RESIDUAL-Structure marker: this sense is what a primitive difference produces. -/
  resultsFromObstruction : Prop

/-- The two current authority-descent channels allowed by the ontology boundary. -/
inductive Real0 where
  | primitiveDifference : PrimitiveDifference → Real0
  | structure : Structure → Real0

/--
Terminal status for a claim after descent.  This is an authority status, not a
truth-value shortcut.
-/
inductive TerminalStatus where
  | certified
  | repaired
  | lifted
  | stabilized
  | refused
  | noRule
  | budgetUnknown
deriving DecidableEq

/-- A terminal status that grants positive authority. -/
def TerminalStatus.Authoritative : TerminalStatus → Prop
  | .certified => True
  | .repaired => True
  | .lifted => True
  | .stabilized => True
  | .refused => False
  | .noRule => False
  | .budgetUnknown => False

/-- A terminal status that is an explicit typed refusal rather than authority. -/
def TerminalStatus.TypedRefusal : TerminalStatus → Prop
  | .refused => True
  | .noRule => True
  | .budgetUnknown => True
  | .certified => False
  | .repaired => False
  | .lifted => False
  | .stabilized => False

/--
A claim packet starts as representation-layer material.  It earns authority only
by descending to primitive difference or structure; otherwise it must carry a
typed refusal.

Note: This is an authority boundary schema, not a complete descent verifier.
Future hardening should replace raw Prop fields with explicit witness structures.
-/
structure ClaimPacket where
  Representation : Sort u
  descendsToPrimitiveDifference : Prop
  descendsToStructure : Prop
  typedRefusal : Prop
  terminalStatus : TerminalStatus

/-- A claim has current-boundary descent when it reaches one of the two authority channels. -/
def ClaimPacket.DescendsToReal0 (packet : ClaimPacket) : Prop :=
  packet.descendsToPrimitiveDifference ∨ packet.descendsToStructure

/-- A claim is admissibly terminalized when it descends or is explicitly refused. -/
def ClaimPacket.Terminalized (packet : ClaimPacket) : Prop :=
  packet.DescendsToReal0 ∨ packet.typedRefusal

/--
Positive claim authority requires both descent and an authoritative status.
Note that this is a policy invariant by construction: it defines what it means
for a packet to possess authority within the boundary specification, rather than
executing an algorithmic verification of descent.
-/
def ClaimPacket.HasAuthority (packet : ClaimPacket) : Prop :=
  packet.DescendsToReal0 ∧ packet.terminalStatus.Authoritative

/--
A validated claim packet is a claim packet that has satisfied the boundary policy:
1. It is terminalized (either descends to Real0 or carries an explicit refusal witness).
2. Any authoritative status requires witnessed descent to Real0 (authority cannot be declared without descent).
-/
structure ValidatedClaimPacket extends ClaimPacket.{u} where
  terminalized : toClaimPacket.Terminalized
  authority_descent : toClaimPacket.terminalStatus.Authoritative → toClaimPacket.DescendsToReal0

/--
Truth is terminalized structure under declared witness conditions.
A TruthPacket packages an already-authorized claim; it does not derive authority
from witnessConditions alone.
-/
structure TruthPacket extends ClaimPacket where
  witnessConditions : Prop
  terminalizedStructure : descendsToStructure
  witnessed : witnessConditions
  authority : toClaimPacket.HasAuthority

/--
Convert a TruthPacket to a ValidatedClaimPacket.
-/
def TruthPacket.toValidatedClaimPacket (truth : TruthPacket.{u}) : ValidatedClaimPacket.{u} where
  toClaimPacket := truth.toClaimPacket
  terminalized := Or.inl (Or.inr truth.terminalizedStructure)
  authority_descent := fun _ => Or.inr truth.terminalizedStructure

/--
The compact axiom set is represented as data, not as global Lean axioms.
Instantiating it for a domain records the exact authority policy being used.
Quantifiers are restricted to validated claim packets.
-/
structure AnomalonAxiomSet where
  primitiveDifferenceIsReal :
    ∀ _D : PrimitiveDifference.{0, 0}, Real0
  structureIsReal :
    ∀ _S : Structure.{0}, Real0
  claimsDescendOrRefuse :
    ∀ packet : ValidatedClaimPacket.{u}, packet.toClaimPacket.Terminalized
  noRepresentationAuthorityByDefault :
    ∀ packet : ValidatedClaimPacket.{u},
      packet.toClaimPacket.terminalStatus.Authoritative → packet.toClaimPacket.DescendsToReal0
  truthIsTerminalizedStructure :
    ∀ truth : TruthPacket.{u}, truth.toClaimPacket.HasAuthority

/-- Canonical packaging of Primitive Difference at the current authority boundary. -/
def primitiveDifferenceReal (D : PrimitiveDifference) : Real0 :=
  Real0.primitiveDifference D

/-- Canonical packaging of Structure at the current authority boundary. -/
def structureReal (S : Structure) : Real0 :=
  Real0.structure S

/--
Concrete exhibited inhabitant of AnomalonAxiomSet, demonstrating consistency
of the policy specification.
-/
def defaultAnomalonAxioms : AnomalonAxiomSet.{u} where
  primitiveDifferenceIsReal := fun D => Real0.primitiveDifference D
  structureIsReal := fun S => Real0.structure S
  claimsDescendOrRefuse := fun p => p.terminalized
  noRepresentationAuthorityByDefault := fun p => p.authority_descent
  truthIsTerminalizedStructure := fun t => t.authority

/--
Construct a ValidatedClaimPacket carrying a typed refusal.
-/
def ValidatedClaimPacket.ofRefusal (Representation : Sort u) : ValidatedClaimPacket.{u} where
  Representation := Representation
  descendsToPrimitiveDifference := False
  descendsToStructure := False
  typedRefusal := True
  terminalStatus := TerminalStatus.refused
  terminalized := Or.inr True.intro
  authority_descent := by
    intro hAuth
    cases hAuth

/--
Construct a ValidatedClaimPacket carrying witnessed primitive difference descent.
-/
def ValidatedClaimPacket.ofPrimitiveDifference (Representation : Sort u) : ValidatedClaimPacket.{u} where
  Representation := Representation
  descendsToPrimitiveDifference := True
  descendsToStructure := False
  typedRefusal := False
  terminalStatus := TerminalStatus.certified
  terminalized := Or.inl (Or.inl True.intro)
  authority_descent := fun _ => Or.inl True.intro

/--
Construct a ValidatedClaimPacket carrying witnessed structure descent.
-/
def ValidatedClaimPacket.ofStructure (Representation : Sort u) : ValidatedClaimPacket.{u} where
  Representation := Representation
  descendsToPrimitiveDifference := False
  descendsToStructure := True
  typedRefusal := False
  terminalStatus := TerminalStatus.certified
  terminalized := Or.inl (Or.inr True.intro)
  authority_descent := fun _ => Or.inr True.intro

/--
Policy invariant by construction: an authoritative packet must descend to Real0.
This is definitional from `HasAuthority`: it ensures representation alone cannot
possess authority, reserving 'verified descent' for concrete certificate checkers.
-/
theorem no_authority_without_descent
    (packet : ClaimPacket)
    (h : packet.HasAuthority) :
    packet.DescendsToReal0 :=
  h.1

theorem authoritative_status_is_not_enough
    (A : AnomalonAxiomSet.{u})
    (packet : ValidatedClaimPacket.{u})
    (hStatus : packet.toClaimPacket.terminalStatus.Authoritative) :
    packet.toClaimPacket.DescendsToReal0 :=
  A.noRepresentationAuthorityByDefault packet hStatus

theorem terminalized_without_descent_is_refusal
    (packet : ClaimPacket)
    (hTerminal : packet.Terminalized)
    (hNoDescent : ¬ packet.DescendsToReal0) :
    packet.typedRefusal := by
  cases hTerminal with
  | inl hDescent => exact False.elim (hNoDescent hDescent)
  | inr hRefusal => exact hRefusal

theorem truth_packet_has_authority
    (truth : TruthPacket) :
    truth.toClaimPacket.HasAuthority :=
  truth.authority

theorem truth_packet_descends_to_structure
    (truth : TruthPacket) :
    truth.toClaimPacket.descendsToStructure :=
  truth.terminalizedStructure

theorem truth_packet_descends_to_real0
    (truth : TruthPacket) :
    truth.toClaimPacket.DescendsToReal0 :=
  Or.inr truth.terminalizedStructure

theorem typed_refusal_is_terminalized
    (packet : ClaimPacket)
    (hRefusal : packet.typedRefusal) :
    packet.Terminalized :=
  Or.inr hRefusal

theorem primitive_difference_descent_terminalized
    (packet : ClaimPacket)
    (hPD : packet.descendsToPrimitiveDifference) :
    packet.Terminalized :=
  Or.inl (Or.inl hPD)

theorem structure_descent_terminalized
    (packet : ClaimPacket)
    (hStructure : packet.descendsToStructure) :
    packet.Terminalized :=
  Or.inl (Or.inr hStructure)

end Ontology
end OmegaCosmology
