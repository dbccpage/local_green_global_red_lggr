import Std.Tactic

/-! Finite-prefix budgets. No decrease is required beyond the declared horizon.
The interleaved statement counts charged lift events, not elapsed clock ticks. -/
namespace PrefixBounds

def spent (cost : Nat → Nat) : Nat → Nat
  | 0 => 0
  | k + 1 => spent cost k + cost k

theorem spending_prefix_invariant (budget cost : Nat → Nat) (L : Nat)
    (h : ∀ k, k < L → budget (k + 1) + cost k ≤ budget k) :
    ∀ k, k ≤ L → spent cost k + budget k ≤ budget 0 := by
  intro k
  induction k with
  | zero => intro _; simp [spent]
  | succ k ih =>
    intro hk
    have hp := ih (Nat.le_trans (Nat.le_succ k) hk)
    have hs := h k (Nat.lt_of_lt_of_le (Nat.lt_succ_self k) hk)
    simp only [spent]
    omega

theorem unit_spending (k : Nat) : spent (fun _ => 1) k = k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [spent, ih]

theorem refinement_prefix_bound (n L : Nat) (pairs : Nat → Nat)
    (h0 : pairs 0 ≤ n * n)
    (hstep : ∀ k, k < L → pairs (k + 1) + 1 ≤ pairs k) :
    L + pairs L ≤ n * n ∧ L ≤ n * n := by
  have h := spending_prefix_invariant pairs (fun _ => 1) L hstep L (Nat.le_refl L)
  rw [unit_spending] at h
  omega

theorem lift_prefix_bound (L : Nat) (budget : Nat → Nat)
    (hdrop : ∀ k, k < L → budget (k + 1) < budget k) :
    L + budget L ≤ budget 0 ∧ L ≤ budget 0 := by
  have hs : ∀ k, k < L → budget (k + 1) + 1 ≤ budget k := by
    intro k hk
    exact hdrop k hk
  have h := spending_prefix_invariant budget (fun _ => 1) L hs L (Nat.le_refl L)
  rw [unit_spending] at h
  omega

theorem interleaved_lift_event_bound (L : Nat) (budget : Nat → Nat)
    (lift : Nat → Bool)
    (hmono : ∀ k, k < L → budget (k + 1) ≤ budget k)
    (hdrop : ∀ k, k < L → lift k = true → budget (k + 1) < budget k) :
    spent (fun k => if lift k then 1 else 0) L + budget L ≤ budget 0 := by
  apply spending_prefix_invariant budget (fun k => if lift k then 1 else 0) L _ L (Nat.le_refl L)
  intro k hk
  cases hl : lift k with
  | false => simpa [hl] using hmono k hk
  | true =>
    have hd := hdrop k hk hl
    simp only [hl, Bool.true_eq, if_true]
    omega

end PrefixBounds
