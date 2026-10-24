import Simplex

open scoped BigOperators
namespace EpistemicNoGo.CertifiedOutcomes
open Simplex

structure InfeasibilityCertificate (m : ℕ) where
  y : Fin m → ℚ
  pivots : ℕ

structure UnboundednessCertificate (n : ℕ) where
  x : Fin n → ℚ
  d : Fin n → ℚ
  pivots : ℕ

def infeasibleValid {m n} (P : Problem m n) (C : InfeasibilityCertificate m) : Prop :=
  (∀ j, 0 ≤ ∑ i, P.A i j * C.y i) ∧ (∑ i, P.b i * C.y i) < 0

def unboundedValid {m n} (P : Problem m n) (C : UnboundednessCertificate n) : Prop :=
  (∀ j, 0 ≤ C.x j) ∧ (∀ i, ∑ j, P.A i j * C.x j = P.b i) ∧
  (∀ j, 0 ≤ C.d j) ∧ (∀ i, ∑ j, P.A i j * C.d j = 0) ∧
  (∑ j, P.c j * C.d j) < 0

instance {m n} (P : Problem m n) (C : InfeasibilityCertificate m) :
    Decidable (infeasibleValid P C) := inferInstanceAs (Decidable (_ ∧ _))
instance {m n} (P : Problem m n) (C : UnboundednessCertificate n) :
    Decidable (unboundedValid P C) := inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _))

/-- Farkas soundness excludes every real feasible vector, not only rational ones. -/
theorem infeasible_excludes_real {m n} (P : Problem m n) (C : InfeasibilityCertificate m)
    (h : infeasibleValid P C) :
    ¬ ∃ x : Fin n → ℝ, (∀ j, 0 ≤ x j) ∧
      (∀ i, ∑ j, (P.A i j : ℝ) * x j = (P.b i : ℝ)) := by
  rintro ⟨x, hx, hAx⟩
  have hy : ∀ j, 0 ≤ ∑ i, (P.A i j : ℝ) * (C.y i : ℝ) := by
    intro j
    exact_mod_cast h.1 j
  have hb : (∑ i, (P.b i : ℝ) * (C.y i : ℝ)) < 0 := by exact_mod_cast h.2
  have hid : (∑ i, (P.b i : ℝ) * (C.y i : ℝ)) =
      ∑ j, (∑ i, (P.A i j : ℝ) * (C.y i : ℝ)) * x j := by
    simp_rw [← hAx, Finset.sum_mul]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro j _
    apply Finset.sum_congr rfl
    intro i _
    ring
  have hn := Finset.sum_nonneg (s := Finset.univ)
    (fun j _ => mul_nonneg (hy j) (hx j))
  linarith

theorem ray_real_feasible {m n} (P : Problem m n) (C : UnboundednessCertificate n)
    (h : unboundedValid P C) (t : ℝ) (ht : 0 ≤ t) :
    (∀ j, 0 ≤ (C.x j : ℝ) + t * (C.d j : ℝ)) ∧
    (∀ i, ∑ j, (P.A i j : ℝ) * ((C.x j : ℝ) + t * (C.d j : ℝ)) = (P.b i : ℝ)) := by
  constructor
  · intro j
    have hx : (0 : ℝ) ≤ (C.x j : ℝ) := by exact_mod_cast h.1 j
    have hd : (0 : ℝ) ≤ (C.d j : ℝ) := by exact_mod_cast h.2.2.1 j
    exact add_nonneg hx (mul_nonneg ht hd)
  · intro i
    have hx : (∑ j, (P.A i j : ℝ) * (C.x j : ℝ)) = (P.b i : ℝ) := by
      exact_mod_cast h.2.1 i
    have hd : (∑ j, (P.A i j : ℝ) * (C.d j : ℝ)) = 0 := by
      exact_mod_cast h.2.2.2.1 i
    simp_rw [mul_add, ← mul_left_comm t, Finset.sum_add_distrib, ← Finset.mul_sum]
    rw [hx, hd]
    ring

theorem ray_real_objective {m n} (P : Problem m n) (C : UnboundednessCertificate n) (t : ℝ) :
    (∑ j, (P.c j : ℝ) * ((C.x j : ℝ) + t * (C.d j : ℝ))) =
      (∑ j, (P.c j : ℝ) * (C.x j : ℝ)) + t * ∑ j, (P.c j : ℝ) * (C.d j : ℝ) := by
  simp_rw [mul_add, ← mul_left_comm t, Finset.sum_add_distrib, ← Finset.mul_sum]

/-- A checked base and ray produce real feasible points below every real floor. -/
theorem unbounded_below_real {m n} (P : Problem m n) (C : UnboundednessCertificate n)
    (h : unboundedValid P C) (floor : ℝ) :
    ∃ x : Fin n → ℝ, (∀ j, 0 ≤ x j) ∧
      (∀ i, ∑ j, (P.A i j : ℝ) * x j = (P.b i : ℝ)) ∧
      (∑ j, (P.c j : ℝ) * x j) < floor := by
  let v : ℝ := ∑ j, (P.c j : ℝ) * (C.x j : ℝ)
  let d : ℝ := ∑ j, (P.c j : ℝ) * (C.d j : ℝ)
  have hd : d < 0 := by
    dsimp [d]
    exact_mod_cast h.2.2.2.2
  let t := max 0 ((v - floor + 1) / (-d))
  have ht : 0 ≤ t := le_max_left _ _
  have hstep : v - floor + 1 ≤ t * (-d) :=
    (div_le_iff₀ (by linarith : 0 < -d)).mp (le_max_right _ _)
  refine ⟨fun j => (C.x j : ℝ) + t * (C.d j : ℝ),
    (ray_real_feasible P C h t ht).1, (ray_real_feasible P C h t ht).2, ?_⟩
  rw [ray_real_objective]
  change v + t * d < floor
  nlinarith

inductive Outcome (m n : ℕ) where
  | optimal : Certificate m n → Outcome m n
  | infeasible : InfeasibilityCertificate m → Outcome m n
  | unbounded : UnboundednessCertificate n → Outcome m n

def outcomeValid {m n} (P : Problem m n) : Outcome m n → Prop
  | .optimal C => valid P C
  | .infeasible C => infeasibleValid P C
  | .unbounded C => unboundedValid P C

instance {m n} (P : Problem m n) (o : Outcome m n) : Decidable (outcomeValid P o) := by
  cases o <;> unfold outcomeValid <;> infer_instance

def accept {m n} (P : Problem m n) (o : Outcome m n) : Except Refusal (Outcome m n) :=
  if outcomeValid P o then .ok o else .error .certificate

theorem accept_correct {m n} (P : Problem m n) (o r : Outcome m n)
    (h : accept P o = .ok r) : outcomeValid P r := by
  unfold accept at h
  split at h
  · cases h; assumption
  · contradiction

structure Stop (m n : ℕ) where
  run : Run m n
  ray : Option (Fin n)

/-- Retain the terminal tableau and entering column for independently checked ray extraction. -/
def search {m n} : ℕ → Tableau m n → Except Refusal (Stop m n)
  | fuel, T => match entering T with
    | none => .ok ⟨⟨T, fuel, []⟩, none⟩
    | some j => match leaving T j with
      | none => .ok ⟨⟨T, fuel, []⟩, some j⟩
      | some i => match fuel with
        | 0 => .error .budget
        | k + 1 => match search k (pivot T i (orig j)) with
          | .error e => .error e
          | .ok S => .ok { S with run := { S.run with trace := (i, orig j) :: S.run.trace } }

theorem search_budget_exact {m n} (fuel : ℕ) (T : Tableau m n) (S : Stop m n)
    (h : search fuel T = .ok S) : S.run.trace.length + S.run.remaining = fuel := by
  induction fuel generalizing T S with
  | zero =>
    rw [search] at h
    split at h
    · cases h; rfl
    · split at h
      · cases h; rfl
      · contradiction
  | succ k ih =>
    rw [search] at h
    split at h
    · cases h; simp
    · split at h
      · cases h; simp
      · dsimp only at h
        split at h
        · contradiction
        · cases h
          simp only [List.length_cons]
          have hh := ih _ _ (by assumption)
          omega

def candidate {m n} (P : Problem m n) (budget : ℕ) : Except Refusal (Outcome m n) := do
  let one ← search budget (initial P)
  if one.ray.isSome then throw .certificate
  if one.run.table.obj (rhsCol m n) ≠ 0 then
    return .infeasible ⟨fun i => sign P i * (one.run.table.obj (art i) - 1),
      budget - one.run.remaining⟩
  let clean ← cleanup (List.finRange m) one.run.remaining one.run.table
  let two ← search clean.remaining (phaseTwo P clean.table)
  let C := extract P budget two.run
  match two.ray with
  | none => return .optimal C
  | some j =>
    let d := two.run.table.active.foldl (fun d i => fun k =>
      if k.val = two.run.table.basis i then -two.run.table.row i (orig j) else d k)
      (fun k => if k = j then 1 else 0)
    return .unbounded ⟨C.x, d, C.pivots⟩

def solveCertified {m n} (P : Problem m n) (budget : ℕ) : Except Refusal (Outcome m n) := do
  let o ← candidate P budget
  accept P o

theorem solve_certified_correct {m n} (P : Problem m n) (budget : ℕ) (o : Outcome m n)
    (h : solveCertified P budget = .ok o) : outcomeValid P o := by
  unfold solveCertified at h
  simp only [bind, Except.bind] at h
  split at h
  · contradiction
  · exact accept_correct P _ o h

theorem solve_infeasible_correct {m n} (P : Problem m n) (budget : ℕ)
    (C : InfeasibilityCertificate m) (h : solveCertified P budget = .ok (.infeasible C)) :
    ¬ ∃ x : Fin n → ℝ, (∀ j, 0 ≤ x j) ∧
      (∀ i, ∑ j, (P.A i j : ℝ) * x j = (P.b i : ℝ)) :=
  infeasible_excludes_real P C (solve_certified_correct P budget _ h)

theorem solve_unbounded_correct {m n} (P : Problem m n) (budget : ℕ)
    (C : UnboundednessCertificate n) (h : solveCertified P budget = .ok (.unbounded C))
    (floor : ℝ) : ∃ x : Fin n → ℝ, (∀ j, 0 ≤ x j) ∧
      (∀ i, ∑ j, (P.A i j : ℝ) * x j = (P.b i : ℝ)) ∧
      (∑ j, (P.c j : ℝ) * x j) < floor :=
  unbounded_below_real P C (solve_certified_correct P budget _ h) floor

theorem solve_optimal_correct {m n} (P : Problem m n) (budget : ℕ)
    (C : Certificate m n) (h : solveCertified P budget = .ok (.optimal C))
    (x : Fin n → ℝ) (hx : ∀ j, 0 ≤ x j)
    (hAx : ∀ i, ∑ j, (P.A i j : ℝ) * x j = (P.b i : ℝ)) :
    (C.value : ℝ) ≤ ∑ j, (P.c j : ℝ) * x j :=
  valid_is_real_optimal P C (solve_certified_correct P budget _ h) x hx hAx

end EpistemicNoGo.CertifiedOutcomes
