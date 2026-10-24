import Bell.ContextualFraction

/-! A chained failure witness on actual complete Bell assignments. -/
noncomputable section
open scoped BigOperators
namespace Bell.ChainWitness
set_option maxHeartbeats 500000
open Bell.ContextualFraction Bell.LinearProgramming
attribute [local instance] Classical.propDecidable
local instance (priority := high) : DecidableEq Bool := Classical.decEq Bool
local instance (priority := high) (n : ℕ) : DecidableEq (Fin n) := Classical.decEq (Fin n)

abbrev Table (n : ℕ) := Bell.Behavior (Fin (n+1)) (Fin (n+1)) Bool Bool
abbrev Global (n : ℕ) := Bell.Assignment (Fin (n+1)) (Fin (n+1)) Bool Bool

def mismatch {X Y : Type} (p : Bell.Behavior X Y Bool Bool) (x : X) (y : Y) : ℝ := p x y false true+p x y true false
def matching {X Y : Type} (p : Bell.Behavior X Y Bool Bool) (x : X) (y : Y) : ℝ := p x y false false+p x y true true
def score {n : ℕ} (p : Table n) : ℝ :=
  (∑ i, mismatch p i i) + (∑ i : Fin n, mismatch p i.succ i.castSucc) + matching p 0 (Fin.last n)

def count {n : ℕ} (g : Global n) : ℝ :=
  (∑ i, if g.1 i=g.2 i then 0 else 1) +
  (∑ i : Fin n, if g.1 i.succ=g.2 i.castSucc then 0 else 1) +
  (if g.1 0=g.2 (Fin.last n) then 1 else 0)

theorem some_failure (n : ℕ) (g : Global n) :
    (∃ i, g.1 i ≠ g.2 i) ∨ (∃ i : Fin n, g.1 i.succ ≠ g.2 i.castSucc) ∨
      g.1 0=g.2 (Fin.last n) := by
  by_cases h1 : ∃ i, g.1 i ≠ g.2 i
  · exact Or.inl h1
  by_cases h2 : ∃ i : Fin n, g.1 i.succ ≠ g.2 i.castSucc
  · exact Or.inr (Or.inl h2)
  have h1' : ∀ i, g.1 i=g.2 i := by simpa only [not_exists,not_not] using h1
  have h2' : ∀ i : Fin n, g.1 i.succ=g.2 i.castSucc := by
    simpa only [not_exists,not_not] using h2
  have hpath : ∀ i : Fin (n+1), g.1 i=g.1 0 := by
    intro i
    induction i using Fin.induction with
    | zero => rfl
    | succ i ih => rw [h2',← h1',ih]
  exact Or.inr (Or.inr ((hpath (Fin.last n)).symm.trans (h1' (Fin.last n))))

theorem count_lower (n : ℕ) (g : Global n) : 1 ≤ count g := by
  have hnon (a b : Bool) : (0:ℝ) ≤ if a=b then 0 else 1 := by split_ifs <;> norm_num
  have hfirst : (0:ℝ) ≤ ∑ i, if g.1 i=g.2 i then 0 else 1 :=
    Finset.sum_nonneg (fun i _ => hnon _ _)
  have hsecond : (0:ℝ) ≤ ∑ i : Fin n, if g.1 i.succ=g.2 i.castSucc then 0 else 1 :=
    Finset.sum_nonneg (fun i _ => hnon _ _)
  have hlast : (0:ℝ) ≤ if g.1 0=g.2 (Fin.last n) then 1 else 0 := by split_ifs <;> norm_num
  rcases some_failure n g with ⟨i,hi⟩ | ⟨i,hi⟩ | hi
  · have h := Finset.single_le_sum (fun j (_ : j ∈ Finset.univ) => hnon (g.1 j) (g.2 j)) (Finset.mem_univ i)
    rw [ite_eq_right hi] at h
    dsimp [count]; linarith
  · have h := Finset.single_le_sum (fun j (_ : j ∈ Finset.univ) => hnon (g.1 j.succ) (g.2 j.castSucc)) (Finset.mem_univ i)
    rw [ite_eq_right hi] at h
    dsimp [count]; linarith
  · dsimp [count]; rw [ite_eq_left hi]; linarith

theorem marginal_mismatch {X Y : Type} [Fintype X] [Fintype Y]
    (q : Bell.Assignment X Y Bool Bool → ℝ) (x : X) (y : Y) :
    mismatch (Bell.marginal q) x y = ∑ g, q g*(if g.1 x=g.2 y then 0 else 1) := by
  simp only [mismatch,Bell.marginal,← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro g _
  cases g.1 x <;> cases g.2 y <;> simp

theorem marginal_matching {X Y : Type} [Fintype X] [Fintype Y]
    (q : Bell.Assignment X Y Bool Bool → ℝ) (x : X) (y : Y) :
    matching (Bell.marginal q) x y = ∑ g, q g*(if g.1 x=g.2 y then 1 else 0) := by
  simp only [matching,Bell.marginal,← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro g _
  cases g.1 x <;> cases g.2 y <;> simp

theorem score_marginal (n : ℕ) (q : Global n → ℝ) :
    score (Bell.marginal q) = ∑ g, q g*count g := by
  simp only [score,marginal_mismatch,marginal_matching,count,mul_add,Finset.mul_sum,
    Finset.sum_add_distrib]
  rw [Finset.sum_comm (f := fun (i : Fin (n+1)) (g : Global n) =>
    q g * (if g.1 i=g.2 i then 0 else 1)),
    Finset.sum_comm (f := fun (i : Fin n) (g : Global n) =>
    q g * (if g.1 i.succ=g.2 i.castSucc then 0 else 1))]

theorem mass_le_score (n : ℕ) (q : Global n → ℝ) (hq : ∀ g, 0 ≤ q g) :
    (∑ g, q g) ≤ score (Bell.marginal q) := by
  rw [score_marginal]
  apply Finset.sum_le_sum
  intro g _
  have h := mul_le_mul_of_nonneg_left (count_lower n g) (hq g)
  simpa only [mul_one] using h

theorem score_monotone (n : ℕ) (p q : Table n) (h : ∀ x y a b, p x y a b ≤ q x y a b) :
    score p ≤ score q := by
  apply add_le_add
  · apply add_le_add <;> apply Finset.sum_le_sum <;> intro i _ <;>
      exact add_le_add (h _ _ _ _) (h _ _ _ _)
  · exact add_le_add (h _ _ _ _) (h _ _ _ _)

theorem fraction_lower (n : ℕ) (p : Table n) (hp : ∀ x y a b, 0 ≤ p x y a b) :
    1-score p ≤ fraction Bell.Repair.vertex (Bell.Repair.flatten p) := by
  have h : sSup (weights Bell.Repair.vertex (Bell.Repair.flatten p)) ≤ score p := by
    apply csSup_le (weights_nonempty _ _ (fun ⟨⟨x,y⟩,⟨a,b⟩⟩ => hp x y a b))
    rintro w ⟨q,hq,he⟩
    rw [← he]
    calc
      (∑ g, q g) ≤ score (Bell.marginal q) := mass_le_score n q hq.1
      _ ≤ score p := by
        apply score_monotone
        intro x y a b
        have hh := hq.2 ((x,y),(a,b))
        have heq := congrFun (Bell.Repair.marginal_eq_mix q) ((x,y),(a,b))
        exact heq.le.trans hh
  unfold fraction
  linarith

theorem packing_score_bound (n : ℕ) (p : Table n) (q : Global n → ℝ)
    (hq : Packing Bell.Repair.vertex (Bell.Repair.flatten p) q) :
    (∑ g, q g) ≤ score p := by
  apply (mass_le_score n q hq.1).trans
  apply score_monotone
  intro x y a b
  have hh := hq.2 ((x,y),(a,b))
  have heq := congrFun (Bell.Repair.marginal_eq_mix q) ((x,y),(a,b))
  exact heq.le.trans hh

theorem weights_bounded (n : ℕ) (p : Table n) :
    BddAbove (weights Bell.Repair.vertex (Bell.Repair.flatten p)) := by
  refine ⟨score p,?_⟩
  rintro w ⟨q,hq,he⟩
  rw [← he]
  exact packing_score_bound n p q hq

theorem fraction_le_one (n : ℕ) (p : Table n) (hp : ∀ x y a b, 0 ≤ p x y a b) :
    fraction Bell.Repair.vertex (Bell.Repair.flatten p) ≤ 1 :=
  Bell.ContextualFraction.fraction_le_one _ _ (weights_bounded n p)
    (fun ⟨⟨x,y⟩,⟨a,b⟩⟩ => hp x y a b)

end Bell.ChainWitness
