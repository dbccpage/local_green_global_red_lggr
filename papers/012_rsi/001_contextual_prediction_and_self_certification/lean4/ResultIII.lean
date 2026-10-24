/-!
# Result III: no self-grounding (parts b and d)

III.a is a typing rule and is mechanised in `ResultIV.lean` as a policy
invariant. III.c (Tarski and Löb under hypothesis H3) is IMPORTED and is not
mechanised here.

Mechanised in this file:

* III.b. Every prefix of a verified hash-chained ledger verifies, so internal
  verification cannot detect a truncated tail. Completeness needs a tip pinned
  outside the ledger. A concrete instance shows the pinned comparison
  separating a ledger from its truncation, and a tampered payload failing.
* III.d. A verdict invariant under a relabeling cannot separate a carrier from
  its relabeling; without the invariance hypothesis the statement is false.

The digest function is a parameter. Nothing here assumes collision
resistance, and nothing here models a cryptographic hash.
-/
namespace EpistemicNoGo.ResultIII

/-- A ledger entry: a payload and its recorded digest. -/
abbrev Entry := Nat × Nat

/-- `verifyFrom h prev es` checks that each recorded digest equals
`h previous_digest payload`, starting from `prev`. -/
def verifyFrom (h : Nat → Nat → Nat) : Nat → List Entry → Bool
  | _, [] => true
  | prev, (p, d) :: rest => (d == h prev p) && verifyFrom h d rest

/-- The tip digest of a ledger, `genesis` when empty. -/
def tip (genesis : Nat) : List Entry → Nat
  | [] => genesis
  | es => (es.getLast?.map (·.2)).getD genesis

theorem verifyFrom_append_left (h : Nat → Nat → Nat) (prev : Nat) (xs ys : List Entry)
    (hv : verifyFrom h prev (xs ++ ys) = true) : verifyFrom h prev xs = true := by
  induction xs generalizing prev with
  | nil => rfl
  | cons x xs ih =>
    obtain ⟨p, d⟩ := x
    simp only [List.cons_append, verifyFrom, Bool.and_eq_true] at hv ⊢
    exact ⟨hv.1, ih d hv.2⟩

/-- III.b, internal half: every prefix of a verified ledger verifies. -/
theorem prefix_verifies (h : Nat → Nat → Nat) (genesis n : Nat) (es : List Entry)
    (hv : verifyFrom h genesis es = true) : verifyFrom h genesis (es.take n) = true := by
  have : es = es.take n ++ es.drop n := (List.take_append_drop n es).symm
  rw [this] at hv
  exact verifyFrom_append_left h genesis _ _ hv

/-- A ledger is complete against a pinned tip when it verifies and its tip is
the pin. -/
def completeAgainst (h : Nat → Nat → Nat) (genesis pinned : Nat) (es : List Entry) : Bool :=
  verifyFrom h genesis es && (tip genesis es == pinned)

/-! ### A concrete instance -/

/-- A toy digest, used only to exhibit the structure. -/
def hh (prev payload : Nat) : Nat := 2 * prev + payload + 1

/-- Genesis digest zero; payloads 5 and 7. -/
def ledger : List Entry := [(5, 6), (7, 20)]

theorem ledger_verifies : verifyFrom hh 0 ledger = true := by decide

/-- The truncated ledger also verifies: truncation is invisible to the internal
check. -/
theorem truncation_is_invisible : verifyFrom hh 0 (ledger.take 1) = true := by decide

/-- With the tip pinned outside the ledger at the full tip, the full ledger is
complete and its truncation is not. -/
theorem pinned_tip_separates :
    completeAgainst hh 0 20 ledger = true ∧ completeAgainst hh 0 20 (ledger.take 1) = false := by
  decide

/-- A tampered payload fails the internal check. -/
theorem tamper_detected : verifyFrom hh 0 [(5, 6), (8, 20)] = false := by decide

/-- Internal verification does not decide completeness: two ledgers, both
verified, one complete against the pin and one not. -/
theorem internal_verification_is_not_completeness :
    ∃ l l' : List Entry, verifyFrom hh 0 l = true ∧ verifyFrom hh 0 l' = true ∧
      completeAgainst hh 0 20 l = true ∧ completeAgainst hh 0 20 l' = false :=
  ⟨ledger, ledger.take 1, ledger_verifies, truncation_is_invisible,
    pinned_tip_separates.1, pinned_tip_separates.2⟩

/-! ### III.d relabeling blindness -/

/-- An invariant verdict cannot separate a carrier from its relabeling. -/
theorem invariant_verdict_blind {C R : Type} (V : C → R) (g : C → C)
    (hinv : ∀ K, V (g K) = V K) (K : C) : V (g K) = V K := hinv K

/-- A verdict that factors through an invariant export cannot either. -/
theorem invariant_export_blind {C X R : Type} (Exp : C → X) (Vbar : X → R) (g : C → C)
    (hExp : ∀ K, Exp (g K) = Exp K) (K : C) : Vbar (Exp (g K)) = Vbar (Exp K) := by
  rw [hExp]

/-- Carriers are token lists; the relabeling swaps tokens 0 and 1. -/
def relabel01 (n : Nat) : Nat := if n = 0 then 1 else if n = 1 then 0 else n

def relabelCarrier (K : List Nat) : List Nat := K.map relabel01

/-- The verdict "the first token is 0". -/
def firstIsZero (K : List Nat) : Bool := (K.head?.map (· == 0)).getD false

/-- Without the invariance hypothesis the statement is false: this verdict
separates a carrier from its relabeling. -/
theorem noninvariant_verdict_separates : firstIsZero [0] ≠ firstIsZero (relabelCarrier [0]) := by
  decide

end EpistemicNoGo.ResultIII
