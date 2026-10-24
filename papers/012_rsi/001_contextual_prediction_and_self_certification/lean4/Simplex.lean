import ContextualDuality

open scoped BigOperators
namespace EpistemicNoGo.Simplex

/- A total, executable exact-rational model of the deposited two-phase code.
   A resource refusal is an outcome, not an infeasibility/optimality theorem.
   No claim of general cross-language refinement or unbudgeted Bland termination. -/
structure Problem (m n : ℕ) where
  A : Fin m → Fin n → ℚ
  b : Fin m → ℚ
  c : Fin n → ℚ

structure Certificate (m n : ℕ) where
  x : Fin n → ℚ
  y : Fin m → ℚ
  value : ℚ
  pivots : ℕ

def valid {m n} (P : Problem m n) (C : Certificate m n) : Prop :=
  (∀ j, 0 ≤ C.x j) ∧ (∀ i, ∑ j, P.A i j * C.x j = P.b i) ∧
  (∀ j, ∑ i, P.A i j * C.y i ≤ P.c j) ∧
  (∑ j, P.c j * C.x j) = C.value ∧ (∑ i, P.b i * C.y i) = C.value

instance {m n} (P : Problem m n) (C : Certificate m n) : Decidable (valid P C) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _))

theorem standard_weak_duality {m n} (P : Problem m n) (x : Fin n → ℚ) (y : Fin m → ℚ)
    (hx : ∀ j, 0 ≤ x j) (hAx : ∀ i, ∑ j, P.A i j * x j = P.b i)
    (hy : ∀ j, ∑ i, P.A i j * y i ≤ P.c j) :
    ∑ i, P.b i * y i ≤ ∑ j, P.c j * x j := by
  calc
    ∑ i, P.b i * y i = ∑ j, (∑ i, P.A i j * y i) * x j := by
      simp_rw [← hAx, Finset.sum_mul]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro j _
      apply Finset.sum_congr rfl
      intro i _
      ring
    _ ≤ _ := Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_right (hy j) (hx j))

theorem valid_is_optimal {m n} (P : Problem m n) (C : Certificate m n) (h : valid P C) :
    ∀ x : Fin n → ℚ, (∀ j, 0 ≤ x j) → (∀ i, ∑ j, P.A i j * x j = P.b i) →
      C.value ≤ ∑ j, P.c j * x j := by
  intro x hx hAx
  rw [← h.2.2.2.2]
  exact standard_weak_duality P x C.y hx hAx h.2.2.1

abbrev Col (m n : ℕ) := Fin (n + m + 1)
def orig {m n} (j : Fin n) : Col m n := ⟨j, by omega⟩
def rhsCol (m n : ℕ) : Col m n := ⟨n + m, by omega⟩
def art {m n} (i : Fin m) : Col m n := ⟨n + i, by omega⟩

structure Tableau (m n : ℕ) where
  row : Fin m → Col m n → ℚ
  obj : Col m n → ℚ
  basis : Fin m → ℕ
  active : List (Fin m)

/-- Materialize each exact row once; otherwise a chain of functional row
    updates would reevaluate earlier pivots exponentially during execution. -/
def memo {k : ℕ} (f : Fin k → ℚ) : Vector ℚ k := Vector.ofFn f

theorem vector_get_ofFn {α : Type*} {k : ℕ} (f : Fin k → α) (i : Fin k) :
    (Vector.ofFn f)[i.val] = f i := by simp

attribute [simp] vector_get_ofFn

theorem memo_apply {k : ℕ} (f : Fin k → ℚ) (i : Fin k) : (memo f)[i.val] = f i := by
  simp [memo]

def pivot {m n} (T : Tableau m n) (r : Fin m) (c : Col m n) : Tableau m n :=
  { T with
    row := let a := Vector.ofFn (fun i => Vector.ofFn (fun j =>
      if i = r then T.row r j / T.row r c
      else T.row i j - T.row i c * (T.row r j / T.row r c)))
      fun i j => a[i.val][j.val]
    obj := let a := memo (fun j => T.obj j - T.obj c * (T.row r j / T.row r c))
      fun j => a[j.val]
    basis := Function.update T.basis r c.val }

theorem pivot_column {m n} (T : Tableau m n) (r : Fin m) (c : Col m n)
    (h : T.row r c ≠ 0) :
    (pivot T r c).row r c = 1 ∧ (∀ i, i ≠ r → (pivot T r c).row i c = 0) ∧
    (pivot T r c).obj c = 0 := by
  simp [pivot, memo, h]

def rowEval {m n} (T : Tableau m n) (v : Col m n → ℚ) (i : Fin m) : ℚ :=
  ∑ j, T.row i j * v j

theorem pivot_row_eval {m n} (T : Tableau m n) (r : Fin m) (c : Col m n)
    (v : Col m n → ℚ) (i : Fin m) :
    rowEval (pivot T r c) v i =
      if i = r then rowEval T v r / T.row r c
      else rowEval T v i - T.row i c * (rowEval T v r / T.row r c) := by
  by_cases hi : i = r
  · subst i
    simp only [rowEval, pivot, vector_get_ofFn, ite_true]
    rw [Finset.sum_div]
    apply Finset.sum_congr rfl
    intro j _
    ring
  · simp only [rowEval, pivot, vector_get_ofFn, if_neg hi]
    simp_rw [sub_mul, mul_assoc, div_mul_eq_mul_div]
    rw [Finset.sum_sub_distrib, ← Finset.mul_sum, Finset.sum_div]

/-- Row elimination is reversible, including zero-valued (degenerate) RHS. -/
theorem pivot_preserves_equations {m n} (T : Tableau m n) (r : Fin m) (c : Col m n)
    (h : T.row r c ≠ 0) (v : Col m n → ℚ) :
    (∀ i, rowEval (pivot T r c) v i = 0) ↔ (∀ i, rowEval T v i = 0) := by
  constructor
  · intro hv
    have hr : rowEval T v r = 0 := by
      have hh := hv r
      rw [pivot_row_eval, if_pos rfl, div_eq_zero_iff] at hh
      exact hh.resolve_right h
    intro i
    have hh := hv i
    rw [pivot_row_eval] at hh
    by_cases hi : i = r
    · simpa [hi] using hr
    · simpa [hi, hr] using hh
  · intro hv i
    rw [pivot_row_eval]
    simp [hv]

theorem pivot_preserves_objective {m n} (T : Tableau m n) (r : Fin m) (c : Col m n)
    (v : Col m n → ℚ) (hr : rowEval T v r = 0) :
    (∑ j, (pivot T r c).obj j * v j) = ∑ j, T.obj j * v j := by
  simp only [pivot, memo_apply]
  simp_rw [sub_mul, mul_assoc, div_mul_eq_mul_div]
  rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.sum_div]
  unfold rowEval at hr
  rw [hr]
  simp

/-- The ratio test keeps the represented basic RHS nonnegative. -/
theorem pivot_preserves_rhs {m n} (T : Tableau m n) (r : Fin m) (c : Col m n)
    (hb : ∀ i, 0 ≤ T.row i (rhsCol m n)) (hp : 0 < T.row r c)
    (hmin : ∀ i, 0 < T.row i c →
      T.row r (rhsCol m n) / T.row r c ≤ T.row i (rhsCol m n) / T.row i c) :
    ∀ i, 0 ≤ (pivot T r c).row i (rhsCol m n) := by
  intro i
  by_cases hi : i = r
  · simp [pivot, hi, div_nonneg (hb r) hp.le]
  · simp only [pivot, vector_get_ofFn, hi, ↓reduceIte]
    by_cases hc : 0 < T.row i c
    · have hh := (le_div_iff₀ hc).mp (hmin i hc)
      nlinarith
    · have hh := mul_nonpos_of_nonpos_of_nonneg (le_of_not_gt hc) (div_nonneg (hb r) hp.le)
      linarith [hb i]

def entering {m n} (T : Tableau m n) : Option (Fin n) :=
  (List.finRange n).find? (fun j => T.obj (orig j) < 0)

theorem entering_none_iff {m n} (T : Tableau m n) :
    entering T = none ↔ ∀ j : Fin n, 0 ≤ T.obj (orig j) := by
  simp [entering, List.find?_eq_none]

theorem entering_negative {m n} (T : Tableau m n) (j : Fin n)
    (h : entering T = some j) : T.obj (orig j) < 0 := by
  have hh := List.find?_some (p := fun k : Fin n => decide (T.obj (orig k) < 0)) h
  exact of_decide_eq_true hh

def leaving {m n} (T : Tableau m n) (j : Fin n) : Option (Fin m) :=
  match T.active.filter (fun i => 0 < T.row i (orig j)) with
  | [] => none
  | i :: is => some (is.foldl (fun best k =>
      if T.row k (rhsCol m n) / T.row k (orig j) <
         T.row best (rhsCol m n) / T.row best (orig j) ∨
         (T.row k (rhsCol m n) / T.row k (orig j) =
          T.row best (rhsCol m n) / T.row best (orig j) ∧ T.basis k < T.basis best)
      then k else best) i)

inductive Refusal where
  | budget | infeasible | unbounded | certificate
  deriving DecidableEq, Repr

structure Run (m n : ℕ) where
  table : Tableau m n
  remaining : ℕ
  trace : List (Fin m × Col m n)

def simplex {m n} : ℕ → Tableau m n → Except Refusal (Run m n)
  | fuel, T => match entering T with
    | none => .ok ⟨T, fuel, []⟩
    | some j => match leaving T j with
      | none => .error .unbounded
      | some i => match fuel with
        | 0 => .error .budget
        | k + 1 => match simplex k (pivot T i (orig j)) with
          | .error e => .error e
          | .ok R => .ok { R with trace := (i, orig j) :: R.trace }

theorem simplex_budget_exact {m n} (fuel : ℕ) (T : Tableau m n) (R : Run m n)
    (h : simplex fuel T = .ok R) : R.trace.length + R.remaining = fuel := by
  induction fuel generalizing T R with
  | zero =>
    rw [simplex] at h
    split at h
    · cases h; rfl
    · split at h <;> contradiction
  | succ k ih =>
    rw [simplex] at h
    split at h
    · cases h; simp
    · split at h
      · contradiction
      · dsimp only at h
        split at h
        · contradiction
        · cases h
          simp only [List.length_cons]
          have hh := ih _ _ (by assumption)
          omega

def cleanup {m n} : List (Fin m) → ℕ → Tableau m n → Except Refusal (Run m n)
  | [], fuel, T => .ok ⟨T, fuel, []⟩
  | i :: is, fuel, T =>
    let j := if n ≤ T.basis i then
      (List.finRange n).find? (fun j => T.row i (orig j) ≠ 0) else none
    match j with
    | none => cleanup is fuel T
    | some c => match fuel with
      | 0 => .error .budget
      | k + 1 => match cleanup is k (pivot T i (orig c)) with
        | .error e => .error e
        | .ok R => .ok { R with trace := (i, orig c) :: R.trace }

theorem cleanup_budget_exact {m n} (is : List (Fin m)) (fuel : ℕ)
    (T : Tableau m n) (R : Run m n) (h : cleanup is fuel T = .ok R) :
    R.trace.length + R.remaining = fuel := by
  induction is generalizing fuel T R with
  | nil => cases h; simp
  | cons i is ih =>
    simp only [cleanup] at h
    split at h
    · exact ih _ _ _ h
    · split at h
      · contradiction
      · split at h
        · contradiction
        · cases h
          simp only [List.length_cons]
          have hh := ih _ _ _ (by assumption)
          omega

def sign {m n} (P : Problem m n) (i : Fin m) : ℚ := if P.b i < 0 then -1 else 1

def initial {m n} (P : Problem m n) : Tableau m n :=
  let rows : Fin m → Col m n → ℚ := fun i j => if hj : j.val < n then sign P i * P.A i ⟨j, hj⟩
    else if j = rhsCol m n then sign P i * P.b i else if j.val = n + i.val then 1 else 0
  { row := rows
    basis := fun i => n + i.val
    active := List.finRange m
    obj := fun j => if j.val < n ∨ j = rhsCol m n then -(∑ i, rows i j) else 0 }

theorem initial_rhs_nonnegative {m n} (P : Problem m n) :
    ∀ i, 0 ≤ (initial P).row i (rhsCol m n) := by
  intro i
  simp only [initial, rhsCol, show ¬ n + m < n by omega, ↓reduceDIte,
    ↓reduceIte]
  unfold sign
  split <;> simp_all <;> linarith

def phaseTwo {m n} (P : Problem m n) (T : Tableau m n) : Tableau m n :=
  let active := T.active.filter (fun i => T.basis i < n)
  let obj : Vector ℚ (n + m + 1) := memo (fun j => if hj : j.val < n then P.c ⟨j, hj⟩ else 0)
  let obj := active.foldl (fun o i => memo (fun j =>
    o[j.val] - (if hi : T.basis i < n + m + 1 then o[T.basis i] else 0) * T.row i j)) obj
  { T with obj := fun j => obj[j.val], active := active }

def execute {m n} (P : Problem m n) (budget : ℕ) : Except Refusal (Run m n) := do
  let one ← simplex budget (initial P)
  if one.table.obj (rhsCol m n) ≠ 0 then throw .infeasible
  let clean ← cleanup (List.finRange m) one.remaining one.table
  let two ← simplex clean.remaining (phaseTwo P clean.table)
  return { two with trace := one.trace ++ clean.trace ++ two.trace }

theorem execute_budget_exact {m n} (P : Problem m n) (budget : ℕ) (R : Run m n)
    (h : execute P budget = .ok R) : R.trace.length + R.remaining = budget := by
  unfold execute at h
  simp only [bind, Except.bind] at h
  split at h
  · contradiction
  · rename_i one hone
    split at h
    · contradiction
    · simp only [pure, Except.pure] at h
      split at h
      · contradiction
      · rename_i clean hclean
        split at h
        · contradiction
        · rename_i two htwo
          cases h
          have h1 := simplex_budget_exact budget (initial P) one hone
          have hc := cleanup_budget_exact (List.finRange m) one.remaining one.table clean hclean
          have h2 := simplex_budget_exact clean.remaining (phaseTwo P clean.table) two htwo
          simp only [List.length_append]
          omega

def extract {m n} (P : Problem m n) (budget : ℕ) (R : Run m n) : Certificate m n :=
  { x := R.table.active.foldl (fun x i => fun j =>
      if j.val = R.table.basis i then R.table.row i (rhsCol m n) else x j) (fun _ => 0)
    y := fun i => -sign P i * R.table.obj (art i)
    value := -R.table.obj (rhsCol m n)
    pivots := budget - R.remaining }

def solve {m n} (P : Problem m n) (budget : ℕ) : Except Refusal (Certificate m n) := do
  let R ← execute P budget
  let C := extract P budget R
  if valid P C then return C else throw .certificate

/-- Every successful return from the complete budgeted two-phase program is
    feasible and globally optimal. The independent final replay is essential. -/
theorem solve_correct {m n} (P : Problem m n) (budget : ℕ) (C : Certificate m n)
    (h : solve P budget = .ok C) : valid P C := by
  unfold solve at h
  simp only [bind, Except.bind] at h
  split at h
  · contradiction
  · split at h
    · simp only [pure, Except.pure, Except.ok.injEq] at h
      subst C
      assumption
    · contradiction

theorem solve_optimal {m n} (P : Problem m n) (budget : ℕ) (C : Certificate m n)
    (h : solve P budget = .ok C) :
    ∀ x : Fin n → ℚ, (∀ j, 0 ≤ x j) → (∀ i, ∑ j, P.A i j * x j = P.b i) →
      C.value ≤ ∑ j, P.c j * x j := valid_is_optimal P C (solve_correct P budget C h)

theorem solve_pivot_bound {m n} (P : Problem m n) (budget : ℕ) (C : Certificate m n)
    (h : solve P budget = .ok C) : C.pivots ≤ budget := by
  unfold solve at h
  simp only [bind, Except.bind] at h
  split at h
  · contradiction
  · split at h
    · cases h
      exact Nat.sub_le _ _
    · contradiction

theorem accepted_pivots_match_trace {m n} (P : Problem m n) (budget : ℕ) (R : Run m n)
    (h : execute P budget = .ok R) : (extract P budget R).pivots = R.trace.length := by
  have hh := execute_budget_exact P budget R h
  simp only [extract]
  omega

theorem valid_is_real_optimal {m n} (P : Problem m n) (C : Certificate m n)
    (h : valid P C) (x : Fin n → ℝ) (hx : ∀ j, 0 ≤ x j)
    (hAx : ∀ i, ∑ j, (P.A i j : ℝ) * x j = (P.b i : ℝ)) :
    (C.value : ℝ) ≤ ∑ j, (P.c j : ℝ) * x j := by
  have hy : ∀ j, ∑ i, (P.A i j : ℝ) * (C.y i : ℝ) ≤ (P.c j : ℝ) := by
    intro j
    exact_mod_cast h.2.2.1 j
  have hval : (∑ i, (P.b i : ℝ) * (C.y i : ℝ)) = (C.value : ℝ) := by
    exact_mod_cast h.2.2.2.2
  rw [← hval]
  calc
    ∑ i, (P.b i : ℝ) * (C.y i : ℝ) =
        ∑ j, (∑ i, (P.A i j : ℝ) * (C.y i : ℝ)) * x j := by
      simp_rw [← hAx, Finset.sum_mul]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro j _
      apply Finset.sum_congr rfl
      intro i _
      ring
    _ ≤ _ := Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_right (hy j) (hx j))

end EpistemicNoGo.Simplex
