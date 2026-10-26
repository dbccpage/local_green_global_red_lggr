/-
Finite statements of the representation-abundance deposit.
Profiles are natural numbers. Closed walks are lists of integer values.
A survivor list is a list of booleans.
-/

def walkHolonomy : List Int → Int
  | [] => 0
  | [_] => 0
  | a :: b :: rest => (b - a) + walkHolonomy (b :: rest)

theorem walkHolonomy_telescope :
    ∀ vals : List Int, (hne : vals ≠ []) →
      walkHolonomy vals = vals.getLast hne - vals.head hne
  | [], hne => by simp at hne
  | [_], _ => by simp [walkHolonomy, List.getLast, List.head]
  | a :: b :: rest, _ => by
      have hrest : b :: rest ≠ [] := by simp
      have ih := walkHolonomy_telescope (b :: rest) hrest
      simp [walkHolonomy, List.head, List.getLast, ih]
      omega

theorem cycle_coboundary_holonomy_zero (vals : List Int) (hne : vals ≠ [])
    (hclosed : vals.head hne = vals.getLast hne) :
    walkHolonomy vals = 0 := by
  rw [walkHolonomy_telescope vals hne, hclosed]
  omega

theorem observation_decision_agrees {α β γ : Type} (obs : α → β) (decide : β → γ)
    (s1 s2 : α) (h : obs s1 = obs s2) :
    decide (obs s1) = decide (obs s2) := by
  rw [h]

theorem plenitude_inflation (n d n' : Nat) (hd : 0 < d) (hn : n < n') :
    n * d < n' * d :=
  Nat.mul_lt_mul_of_pos_right hn hd

theorem false_green_holonomy (k : Nat) (eps : Int) (hk : 3 ≤ k) (he : 0 < eps) :
    0 < (k : Int) * eps := by
  have hkI : (0 : Int) < k := by omega
  exact Int.mul_pos hkI he

theorem false_green_local (eps tau : Int) (he : 0 < eps) (ht : eps < tau) :
    eps.natAbs ≤ tau.natAbs := by
  cases eps with
  | ofNat a =>
    cases tau with
    | ofNat b =>
      simp [Int.natAbs] at he ht ⊢
      omega
    | negSucc _ =>
      omega
  | negSucc _ =>
    omega

def tripleHolonomy : List (Int × Int × Nat) → Int
  | [] => 0
  | (s, w, _) :: rest => s * w + tripleHolonomy rest

def tripleTau : List (Int × Int × Nat) → Nat
  | [] => 0
  | (_, _, t) :: rest => t + tripleTau rest

theorem natAbs_signed_one (s w : Int) (hs : s = 1 ∨ s = -1) :
    (s * w).natAbs = w.natAbs := by
  cases hs with
  | inl h => simp [h]
  | inr h => simp [h]

theorem cycle_defect_bound :
    ∀ rows : List (Int × Int × Nat),
      (∀ r ∈ rows, r.fst = 1 ∨ r.fst = -1) →
      (∀ r ∈ rows, r.snd.fst.natAbs ≤ r.snd.snd) →
      (tripleHolonomy rows).natAbs ≤ tripleTau rows
  | [], _, _ => by simp [tripleHolonomy, tripleTau]
  | (s, w, t) :: rest, hsign, hcap => by
      have hs : s = 1 ∨ s = -1 := hsign (s, w, t) (by simp)
      have hw : w.natAbs ≤ t := hcap (s, w, t) (by simp)
      have hsign' : ∀ r ∈ rest, r.fst = 1 ∨ r.fst = -1 := by
        intro r hr
        exact hsign r (by simp [hr])
      have hcap' : ∀ r ∈ rest, r.snd.fst.natAbs ≤ r.snd.snd := by
        intro r hr
        exact hcap r (by simp [hr])
      have ih := cycle_defect_bound rest hsign' hcap'
      have hmul := natAbs_signed_one s w hs
      simp [tripleHolonomy, tripleTau] at ih ⊢
      calc (s * w + tripleHolonomy rest).natAbs
          ≤ (s * w).natAbs + (tripleHolonomy rest).natAbs := Int.natAbs_add_le _ _
        _ = w.natAbs + (tripleHolonomy rest).natAbs := by rw [hmul]
        _ ≤ t + tripleTau rest := Nat.add_le_add hw ih

def sharpRows : List Nat → List (Int × Int × Nat)
  | [] => []
  | t :: ts => (1, Int.ofNat t, t) :: sharpRows ts

theorem sharp_holonomy : ∀ taus : List Nat,
    tripleHolonomy (sharpRows taus) = Int.ofNat (tripleTau (sharpRows taus))
  | [] => by simp [sharpRows, tripleHolonomy, tripleTau]
  | t :: ts => by
      simp [sharpRows, tripleHolonomy, tripleTau, sharp_holonomy ts]

theorem sharp_cycle_attains (taus : List Nat) :
    (tripleHolonomy (sharpRows taus)).natAbs = tripleTau (sharpRows taus) := by
  rw [sharp_holonomy taus]
  simp [Int.natAbs]

def survivorCount : List Bool → Nat
  | [] => 0
  | b :: bs => (if b then 1 else 0) + survivorCount bs

theorem survivorCount_append_true (bs : List Bool) :
    survivorCount (bs ++ [true]) = survivorCount bs + 1 := by
  induction bs with
  | nil => simp [survivorCount]
  | cons b tl ih =>
    cases b <;> simp [survivorCount, ih, Nat.add_assoc, Nat.add_left_comm]

theorem unique_acceptance_breaks (bs : List Bool) (h : survivorCount bs = 1) :
    survivorCount (bs ++ [true]) = 2 := by
  rw [survivorCount_append_true, h]
