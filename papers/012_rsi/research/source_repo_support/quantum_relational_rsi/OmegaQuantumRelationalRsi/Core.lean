import Mathlib

namespace OmegaQuantumRelationalRsi

/-! ## Round 1 core: report-grounded strict order on an arbitrary state type -/

structure ReportGrounded {S C : Type*} (report : S → C) (gt : S → S → Prop) : Prop where
  irrefl : ∀ ρ, ¬ gt ρ ρ
  trans : ∀ ρ σ τ, gt ρ σ → gt σ τ → gt ρ τ
  grounded : ∀ ρ₁ ρ₂ σ₁ σ₂, report ρ₁ = report ρ₂ → report σ₁ = report σ₂ →
    gt ρ₁ σ₁ → gt ρ₂ σ₂

/-- Round 1 Lemma Q.2(a): equal reports exclude strict dominance. -/
theorem no_dominance_of_report_eq {S C : Type*} {report : S → C} {gt : S → S → Prop}
    (h : ReportGrounded report gt) {ρ σ : S} (e : report ρ = report σ) : ¬ gt ρ σ :=
  fun hg => h.irrefl σ (h.grounded ρ σ σ σ e rfl hg)

/-- Bounded chain closure: if every step below `n` is a strict improvement,
then every later state below `n` dominates every earlier one. -/
theorem chain_dominates {S : Type*} {gt : S → S → Prop}
    (htrans : ∀ ρ σ τ, gt ρ σ → gt σ τ → gt ρ τ) (f : ℕ → S) (n : ℕ)
    (hstep : ∀ k, k < n → gt (f (k+1)) (f k)) :
    ∀ i j, i < j → j ≤ n → gt (f j) (f i) := by
  intro i j hij hjn
  induction j with
  | zero => exact absurd hij (Nat.not_lt_zero i)
  | succ j ih =>
    have hjn' : j < n := hjn
    rcases Nat.lt_or_eq_of_le (Nat.lt_succ_iff.mp hij) with hlt | heq
    · exact htrans _ _ _ (hstep j hjn') (ih hlt (Nat.le_of_lt hjn'))
    · rw [heq]; exact hstep j hjn'

/-- Round 1 Theorem Q.1 (0-based indexing): along any trajectory, some step with index
`≤ card C` fails to be a strict report-grounded improvement. -/
theorem report_collision_horizon {S C : Type*} [Fintype C]
    (report : S → C) (gt : S → S → Prop) (h : ReportGrounded report gt) (f : ℕ → S) :
    ∃ k, k ≤ Fintype.card C ∧ ¬ gt (f (k+1)) (f k) := by
  by_contra hall
  push_neg at hall
  -- hall : ∀ k, k ≤ Fintype.card C → gt (f (k+1)) (f k)
  have hstep : ∀ k, k < Fintype.card C + 1 → gt (f (k+1)) (f k) :=
    fun k hk => hall k (Nat.lt_succ_iff.mp hk)
  have hchain := chain_dominates h.trans f (Fintype.card C + 1) hstep
  obtain ⟨i, j, hne, hij⟩ := Fintype.exists_ne_map_eq_of_card_lt
    (fun i : Fin (Fintype.card C + 1) => report (f i.val))
    (by rw [Fintype.card_fin]; exact Nat.lt_succ_self _)
  rcases lt_or_gt_of_ne hne with hlt | hlt
  · exact no_dominance_of_report_eq h hij.symm
      (hchain i.val j.val (Fin.lt_def.mp hlt) (Nat.le_of_lt j.isLt))
  · exact no_dominance_of_report_eq h hij
      (hchain j.val i.val (Fin.lt_def.mp hlt) (Nat.le_of_lt i.isLt))

/-! ## Round 2 core: strictly descending integer budget -/

/-- Invariant: purification count plus remaining budget never exceeds the initial budget. -/
theorem lift_budget_invariant (B : ℕ → ℕ) (pur : ℕ → Prop) [DecidablePred pur]
    (hdec : ∀ k, pur k → B (k+1) < B k) (hmono : ∀ k, B (k+1) ≤ B k) :
    ∀ n, ((Finset.range n).filter pur).card + B n ≤ B 0 := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.range_succ, Finset.filter_insert]
    by_cases hp : pur n
    · rw [if_pos hp]
      have h1 := Finset.card_insert_le n ((Finset.range n).filter pur)
      have h2 := hdec n hp
      omega
    · rw [if_neg hp]
      have h2 := hmono n
      omega

/-- Round 2 Theorem Q.2(a): at most `B 0` purification steps occur in any prefix. -/
theorem lift_budget_exhaustion (B : ℕ → ℕ) (pur : ℕ → Prop) [DecidablePred pur]
    (hdec : ∀ k, pur k → B (k+1) < B k) (hmono : ∀ k, B (k+1) ≤ B k) :
    ∀ n, ((Finset.range n).filter pur).card ≤ B 0 :=
  fun n => le_trans (Nat.le_add_right _ _) (lift_budget_invariant B pur hdec hmono n)

/-! ## Round 3 core: gluing predicate on a finite coverage complex -/

structure CoverageComplex (V : Type*) where
  edges : Finset (V × V)

/-- Φ₁(δ_k) = 0 iff no in-window report change on any coverage edge (Round 3 Lemma 2.1). -/
def gluesAt {V C : Type*} (K : CoverageComplex V)
    (rep : V → ℕ → C) (lat : V → V → ℕ → ℕ) (k : ℕ) : Prop :=
  ∀ e ∈ K.edges,
    rep e.2 (k - lat e.1 e.2 k) = rep e.2 k ∧ rep e.1 (k - lat e.2 e.1 k) = rep e.1 k

/-! ## Round 2 representability: Baker as an explicit hypothesis (never an axiom) -/

/-- Shape of the Baker consequence (B*) used in Theorem Q.2.1. -/
def BakerLinearForms : Prop :=
  ∀ (n : ℕ) (α β : Fin n → ℝ),
    (∀ i, IsAlgebraic ℚ (α i) ∧ 0 < α i) → (∀ i, IsAlgebraic ℚ (β i)) →
    (∑ i, β i * Real.log (α i)) ≠ 0 →
    Transcendental ℚ (∑ i, β i * Real.log (α i))

/-- Round 2 Theorem Q.2.1(1), conditional on `BakerLinearForms`.
`hlt` follows from `hrank` and `hsum` but is taken as a hypothesis here. -/
theorem entropy_transcendental_of_baker (hB : BakerLinearForms) (n : ℕ) (p : Fin n → ℝ)
    (halg : ∀ i, IsAlgebraic ℚ (p i)) (hpos : ∀ i, 0 < p i) (hlt : ∀ i, p i < 1)
    (hrank : 2 ≤ n) :
    Transcendental ℚ (-(∑ i, p i * Real.log (p i))) := by
  haveI : Nonempty (Fin n) := ⟨⟨0, by omega⟩⟩
  have hterm : ∀ i, 0 < -p i * Real.log (p i) := fun i =>
    mul_pos_of_neg_of_neg (by linarith [hpos i]) (Real.log_neg (hpos i) (hlt i))
  have hsumpos : 0 < ∑ i, -p i * Real.log (p i) :=
    Finset.sum_pos (fun i _ => hterm i) Finset.univ_nonempty
  have heq : -(∑ i, p i * Real.log (p i)) = ∑ i, -p i * Real.log (p i) := by
    rw [← Finset.sum_neg_distrib]
    simp only [neg_mul]
  rw [heq]
  exact hB n p (fun i => -p i) (fun i => ⟨halg i, hpos i⟩) (fun i => (halg i).neg)
    (ne_of_gt hsumpos)

/-! ## Composite (corrected statement; see Round 5 header, correction 1) -/

/-- Round 4 Theorem Q.Master, clauses (i)+(iii)+(vii), combinatorial content:
if every admitted strict improvement is a purification claim (`hpur`) and every
purification claim strictly decrements an integer budget (`hdec`), then the first
non-admitted index is `≤ min (card C) (B 0)`. Renamed from `quantum_rsi_impossible`. -/
theorem quantum_rsi_bounded_horizon {S C : Type*} [Fintype C]
    (report : S → C) (gt : S → S → Prop) (h : ReportGrounded report gt)
    (f : ℕ → S) (B : ℕ → ℕ) (pur : ℕ → Prop)
    (hdec : ∀ k, pur k → B (k+1) < B k)
    (hpur : ∀ k, gt (f (k+1)) (f k) → pur k) :
    ∃ k, k ≤ min (Fintype.card C) (B 0) ∧ ¬ gt (f (k+1)) (f k) := by
  by_contra hall
  push_neg at hall
  -- hall : ∀ k, k ≤ min (card C) (B 0) → gt (f (k+1)) (f k)
  have hbud : ∀ k, k ≤ min (Fintype.card C) (B 0) + 1 → B k + k ≤ B 0 := by
    intro k
    induction k with
    | zero => intro _; simp
    | succ k ih =>
      intro hk
      have hk' : k ≤ min (Fintype.card C) (B 0) := by omega
      have h1 := hdec k (hpur k (hall k hk'))
      have h2 := ih (by omega)
      omega
  have hm := hbud (min (Fintype.card C) (B 0) + 1) le_rfl
  obtain ⟨k, hk, hng⟩ := report_collision_horizon report gt h f
  exact hng (hall k (by omega))

end OmegaQuantumRelationalRsi
