import EmbeddedQuantitative

namespace EpistemicNoGo.QueryBudget

inductive Plan (A : Type) where
  | leaf
  | ask (query : A) (no yes : Plan A)

def depth {A : Type} : Plan A → Nat
  | .leaf => 0
  | .ask _ no yes => 1 + max (depth no) (depth yes)

def branch {W A : Type} [DecidableEq W] (observe : A → W → Bool)
    (s : Finset W) (a : A) (answer : Bool) : Finset W :=
  s.filter (fun w => observe a w = answer)

def valid {W A : Type} [DecidableEq W] [DecidableEq A]
    (observe : A → W → Bool) (allowed : List A) (done : Finset W → Bool) :
    Plan A → Finset W → Prop
  | .leaf, s => done s = true
  | .ask a no yes, s => a ∈ allowed ∧
      valid observe allowed done no (branch observe s a false) ∧
      valid observe allowed done yes (branch observe s a true)

def possible {W A : Type} [DecidableEq W] [DecidableEq A]
    (observe : A → W → Bool) (allowed : List A) (done : Finset W → Bool) :
    Nat → Finset W → Bool
  | 0, s => done s
  | n + 1, s => done s || allowed.any (fun a =>
      possible observe allowed done n (branch observe s a false) &&
      possible observe allowed done n (branch observe s a true))

theorem possible_iff_bounded_plan {W A : Type} [DecidableEq W] [DecidableEq A]
    (observe : A → W → Bool) (allowed : List A) (done : Finset W → Bool)
    (n : Nat) (s : Finset W) :
    possible observe allowed done n s = true ↔
      ∃ p, valid observe allowed done p s ∧ depth p ≤ n := by
  induction n generalizing s with
  | zero =>
    constructor
    · intro h; exact ⟨.leaf, h, Nat.le_refl _⟩
    · intro ⟨p, hp, hd⟩
      cases p with
      | leaf => exact hp
      | ask a no yes => simp [depth] at hd
  | succ n ih =>
    simp only [possible, Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true]
    constructor
    · intro h
      rcases h with h | ⟨a, ha, hn, hy⟩
      · exact ⟨.leaf, h, Nat.zero_le _⟩
      · obtain ⟨no, hno, dno⟩ := (ih _).mp hn
        obtain ⟨yes, hyes, dyes⟩ := (ih _).mp hy
        exact ⟨.ask a no yes, ⟨ha, hno, hyes⟩, by simp only [depth]; omega⟩
    · intro ⟨p, hp, hd⟩
      cases p with
      | leaf => exact Or.inl hp
      | ask a no yes =>
        obtain ⟨ha, hn, hy⟩ := hp
        have dn : depth no ≤ n := by simp only [depth] at hd; omega
        have dy : depth yes ≤ n := by simp only [depth] at hd; omega
        exact Or.inr ⟨a, ha, (ih _).mpr ⟨no, hn, dn⟩, (ih _).mpr ⟨yes, hy, dy⟩⟩

theorem rejected_budget_excludes_plan {W A : Type} [DecidableEq W] [DecidableEq A]
    (observe : A → W → Bool) (allowed : List A) (done : Finset W → Bool)
    (n : Nat) (s : Finset W) (h : possible observe allowed done n s = false) :
    ¬ ∃ p, valid observe allowed done p s ∧ depth p ≤ n := by
  intro existsPlan
  have := (possible_iff_bounded_plan observe allowed done n s).mpr existsPlan
  simp [h] at this

def leafBelief {W A : Type} [DecidableEq W] (observe : A → W → Bool)
    (world : W) : Plan A → Finset W → Finset W
  | .leaf, s => s
  | .ask a no yes, s =>
      if observe a world then leafBelief observe world yes (branch observe s a true)
      else leafBelief observe world no (branch observe s a false)

theorem actual_world_retained {W A : Type} [DecidableEq W]
    (observe : A → W → Bool) (world : W) (p : Plan A) (s : Finset W)
    (hw : world ∈ s) : world ∈ leafBelief observe world p s := by
  induction p generalizing s with
  | leaf => exact hw
  | ask a no yes hn hy =>
    simp only [leafBelief]
    split
    next h => apply hy; simp [branch, hw, h]
    next h => apply hn; simp [branch, hw, Bool.eq_false_iff.mpr h]

theorem valid_reaches_checked_leaf {W A : Type} [DecidableEq W] [DecidableEq A]
    (observe : A → W → Bool) (allowed : List A) (done : Finset W → Bool)
    (world : W) (p : Plan A) (s : Finset W) (h : valid observe allowed done p s) :
    done (leafBelief observe world p s) = true := by
  induction p generalizing s with
  | leaf => exact h
  | ask a no yes hn hy =>
    simp only [leafBelief]
    split
    · exact hy _ h.2.2
    · exact hn _ h.2.1

theorem checked_leaf_error {W A : Type} [DecidableEq W] [DecidableEq A]
    (observe : A → W → Bool) (allowed : List A) (done : Finset W → Bool)
    (target : W → ℝ) (estimate : Finset W → ℝ) (epsilon : ℝ)
    (leafSound : ∀ s, done s = true → ∀ w ∈ s, |target w - estimate s| ≤ epsilon)
    (world : W) (p : Plan A) (s : Finset W) (hw : world ∈ s)
    (h : valid observe allowed done p s) :
    |target world - estimate (leafBelief observe world p s)| ≤ epsilon :=
  leafSound _ (valid_reaches_checked_leaf observe allowed done world p s h) world
    (actual_world_retained observe world p s hw)

theorem informative_branch_card_lt {W A : Type} [DecidableEq W]
    (observe : A → W → Bool) (s : Finset W) (a : A) (answer : Bool)
    (other : W) (mem : other ∈ s) (different : observe a other ≠ answer) :
    (branch observe s a answer).card < s.card := by
  apply Finset.card_lt_card
  apply Finset.ssubset_iff_subset_ne.mpr
  constructor
  · exact Finset.filter_subset _ _
  · intro h
    have ho : other ∈ branch observe s a answer := h.symm ▸ mem
    exact different (Finset.mem_filter.mp ho).2

def fixtureObserve (a : Fin 3) (w : Fin 4) : Bool :=
  if a = 0 then decide (2 ≤ w.val)
  else if a = 1 then decide (w.val = 1)
  else decide (w.val = 3)

def fixtureDone (s : Finset (Fin 4)) : Bool := decide (s.card ≤ 1)

theorem fixture_two_queries_suffice :
    possible fixtureObserve [0, 1, 2] fixtureDone 2 Finset.univ = true := by decide

theorem fixture_one_query_insufficient :
    possible fixtureObserve [0, 1, 2] fixtureDone 1 Finset.univ = false := by decide

theorem fixture_every_fixed_pair_collides :
    ∀ a b : Fin 3, ∃ x y : Fin 4, x ≠ y ∧ fixtureObserve a x = fixtureObserve a y ∧
      fixtureObserve b x = fixtureObserve b y := by decide

theorem fixture_fixed_three_identify :
    ∀ x y : Fin 4, (∀ a : Fin 3, fixtureObserve a x = fixtureObserve a y) → x = y := by decide

theorem fixture_no_allowed_query_refuses :
    possible fixtureObserve [] fixtureDone 4 Finset.univ = false := by decide

end EpistemicNoGo.QueryBudget
