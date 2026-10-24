/-!
# Result IV: the three-role gate

This file models the decision procedure `verify_three_role_authority` of the
repository's contract crate. The model is written independently in Lean and is
not machine-linked to the Rust source; agreement is by reading and by the
fixture tests of the Rust crate.

Simplifications of the model against the Rust source: an identifier is blank
when every character is whitespace (the source tests `trim().is_empty()`); the
packet digest of the receipt is omitted; the refusal constructors carry no
payload.

The gate decides role identity on identifiers. Two identifiers that name one
agent in the world are invisible to it (identity binding is outside the
function). Satisfying the policy yields a receipt that carries no authority;
see `receipt_carries_no_authority`.
-/
namespace EpistemicNoGo.ResultIV

structure Principal where
  id : String
  trustRoot : Option String

inductive Basis where
  | certificate
  | prose
  deriving DecidableEq

structure Packet where
  attemptId : String
  proposer : Principal
  evaluator : Principal
  authorizer : Principal
  basis : Basis

structure Policy where
  admittedRoots : List String
  allowSelfAuthorization : Bool
  allowSelfEvaluation : Bool

/-- Policy with both self-roles refused. -/
def Policy.strict (roots : List String) : Policy := ⟨roots, false, false⟩

inductive Refusal where
  | selfAuthorizationProposer
  | selfAuthorizationEvaluator
  | selfEvaluation
  | noExternalRoot
  | proseAuthority
  | malformed

/-- The effect a receipt carries. There is one constructor. -/
inductive Effect where
  | none

structure Receipt where
  attemptId : String
  root : String
  effect : Effect

/-- An identifier is blank when it has no non-whitespace character. -/
def blank (s : String) : Bool := s.toList.all Char.isWhitespace

/-- All four identifiers of the packet are non-blank. -/
def wellFormed (pk : Packet) : Bool :=
  !(blank pk.proposer.id || blank pk.evaluator.id || blank pk.authorizer.id || blank pk.attemptId)

/-- The gate. Every path that is not an explicit pass is a refusal. -/
def verify (pk : Packet) (pol : Policy) : Except Refusal Receipt :=
  if !wellFormed pk then
    .error .malformed
  else if !pol.allowSelfAuthorization && pk.proposer.id == pk.authorizer.id then
    .error .selfAuthorizationProposer
  else if !pol.allowSelfAuthorization && pk.evaluator.id == pk.authorizer.id then
    .error .selfAuthorizationEvaluator
  else if !pol.allowSelfEvaluation && pk.proposer.id == pk.evaluator.id then
    .error .selfEvaluation
  else if pk.basis == .prose then
    .error .proseAuthority
  else
    match pk.authorizer.trustRoot with
    | some r =>
      if pol.admittedRoots.contains r && r != pk.proposer.id && r != pk.evaluator.id then
        .ok ⟨pk.attemptId, r, .none⟩
      else .error .noExternalRoot
    | none => .error .noExternalRoot

def IsRefusal {α : Type} : Except Refusal α → Prop
  | .error _ => True
  | .ok _ => False

/-! ### Statements -/

/-- [POLICY INVARIANT, by construction] A receipt carries no authority: the
effect type has one inhabitant. This is the typing rule of III.a; it is not a
theorem about any reasoner. -/
theorem receipt_carries_no_authority (r : Receipt) : r.effect = .none := by
  cases r.effect; rfl

/-- A well-formed packet in which the proposer is the authorizer is refused
under the strict policy, whatever the claimed competence (the packet has no
competence field). -/
theorem proposer_cannot_authorize (pk : Packet) (roots : List String)
    (hwf : wellFormed pk = true)
    (hpa : pk.proposer.id = pk.authorizer.id) :
    IsRefusal (verify pk (Policy.strict roots)) := by
  simp [verify, Policy.strict, hwf, hpa, IsRefusal]

theorem evaluator_cannot_authorize (pk : Packet) (roots : List String)
    (hwf : wellFormed pk = true)
    (hea : pk.evaluator.id = pk.authorizer.id) :
    IsRefusal (verify pk (Policy.strict roots)) := by
  simp only [verify, Policy.strict, hwf]
  by_cases hpa : pk.proposer.id = pk.authorizer.id
  · simp [hpa, IsRefusal]
  · simp [hpa, hea, IsRefusal]

/-- Prose standing is refused, provided the role identifiers are distinct. -/
theorem prose_standing_refused (pk : Packet) (roots : List String)
    (hwf : wellFormed pk = true)
    (hpa : pk.proposer.id ≠ pk.authorizer.id) (hea : pk.evaluator.id ≠ pk.authorizer.id)
    (hpe : pk.proposer.id ≠ pk.evaluator.id) (hb : pk.basis = .prose) :
    IsRefusal (verify pk (Policy.strict roots)) := by
  simp [verify, Policy.strict, hwf, hpa, hea, hpe, hb, IsRefusal]

/-- Soundness of a pass: whenever the gate returns a receipt under the strict
policy, the three identifiers are pairwise distinct, the standing is a
certificate, and the root is admitted and is neither the proposer nor the
evaluator. -/
theorem pass_implies_policy (pk : Packet) (roots : List String) (r : Receipt)
    (h : verify pk (Policy.strict roots) = .ok r) :
    pk.proposer.id ≠ pk.authorizer.id ∧ pk.evaluator.id ≠ pk.authorizer.id ∧
    pk.proposer.id ≠ pk.evaluator.id ∧ pk.basis = .certificate ∧
    ∃ root, pk.authorizer.trustRoot = some root ∧ root ∈ roots ∧
      root ≠ pk.proposer.id ∧ root ≠ pk.evaluator.id := by
  unfold verify Policy.strict at h
  split at h
  · cases h
  rename_i hwf
  split at h
  · cases h
  rename_i hpa
  split at h
  · cases h
  rename_i hea
  split at h
  · cases h
  rename_i hpe
  split at h
  · cases h
  rename_i hb
  cases hroot : pk.authorizer.trustRoot with
  | none => simp [hroot] at h
  | some root =>
    simp only [hroot] at h
    split at h
    · rename_i hc
      simp only [Bool.and_eq_true, bne_iff_ne, ne_eq, List.contains_iff_mem] at hc
      simp only [Bool.not_false, Bool.true_and, beq_iff_eq] at hpa hea hpe
      refine ⟨hpa, hea, hpe, ?_, root, rfl, hc.1.1, hc.1.2, hc.2⟩
      cases hbs : pk.basis
      · rfl
      · simp [hbs] at hb
    · cases h

/-- Delegated standing is admitted: with pairwise distinct identifiers, a
certificate and an admitted external root, the gate issues a receipt. What the
gate cannot supply is the delegation itself. -/
theorem delegated_standing_admitted (pk : Packet) (roots : List String) (root : String)
    (hwf : wellFormed pk = true)
    (hpa : pk.proposer.id ≠ pk.authorizer.id) (hea : pk.evaluator.id ≠ pk.authorizer.id)
    (hpe : pk.proposer.id ≠ pk.evaluator.id) (hb : pk.basis = .certificate)
    (hroot : pk.authorizer.trustRoot = some root) (hadm : root ∈ roots)
    (hrp : root ≠ pk.proposer.id) (hre : root ≠ pk.evaluator.id) :
    ∃ r, verify pk (Policy.strict roots) = .ok r := by
  have hbp : (pk.basis == Basis.prose) = false := by simp [hb]
  refine ⟨⟨pk.attemptId, root, .none⟩, ?_⟩
  simp [verify, Policy.strict, hwf, hpa, hea, hpe, hbp, hroot, hadm, hrp, hre]

/-! ### Composition: a chain with a refused link confers nothing -/

def composeAttempts : List (Packet × Policy) → Except Refusal (Option Receipt)
  | [] => .ok none
  | (pk, pol) :: rest =>
    match verify pk pol with
    | .error e => .error e
    | .ok r =>
      match composeAttempts rest with
      | .error e => .error e
      | .ok none => .ok (some r)
      | .ok (some r') => .ok (some r')

theorem compose_refused_link (l : List (Packet × Policy))
    (hl : ∃ x, x ∈ l ∧ IsRefusal (verify x.1 x.2)) :
    IsRefusal (composeAttempts l) := by
  induction l with
  | nil => obtain ⟨x, hx, _⟩ := hl; simp at hx
  | cons y ys ih =>
    obtain ⟨x, hx, hr⟩ := hl
    obtain ⟨pk, pol⟩ := y
    simp only [composeAttempts]
    cases hv : verify pk pol with
    | error e => simp [IsRefusal]
    | ok r =>
      simp only []
      rcases List.mem_cons.mp hx with rfl | hx'
      · simp [hv, IsRefusal] at hr
      · have := ih ⟨x, hx', hr⟩
        cases hc : composeAttempts ys with
        | error e => simp [IsRefusal]
        | ok o => simp [hc, IsRefusal] at this

/-! ### What the gate does not see -/

/-- Identity binding is outside the function: a packet whose three identifiers
are distinct strings passes even if all three name one agent in the world. The
witness exhibits only the string-level behaviour. -/
def distinctStringsPacket : Packet :=
  ⟨"att-1", ⟨"agent-1", none⟩, ⟨"agent-1-alias", none⟩, ⟨"agent-1-second-alias", some "root:R"⟩,
    .certificate⟩

theorem distinct_strings_pass :
    ∃ r, verify distinctStringsPacket (Policy.strict ["root:R"]) = .ok r := by
  refine ⟨⟨"att-1", "root:R", .none⟩, ?_⟩
  rfl

end EpistemicNoGo.ResultIV
