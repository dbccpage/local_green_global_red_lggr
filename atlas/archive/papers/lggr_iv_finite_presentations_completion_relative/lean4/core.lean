/-!
# Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction
Formalization of the core mathematical claims:
1. Finite descent definition and moving-witness collision criterion
2. Finite-stage arithmetic identity: 3 * x_n + 1 = (-2)^n
3. Finite-stage divisibility: 2^n | (3 * x_n + 1)
4. Successive stage compatibility: 2^n | (x_{n+1} - x_n)
5. Impossibility of an integral global solution: ¬ ∃ z : Int, ∀ n : Nat, 2^n | (3 * z + 1)
6. Reflection descent criterion for completion witnesses
7. Finite-chain pullback: one top element and a finite list of transitions yield a nonempty compatible thread
8. Finite overlap identity: primal defect 2*(B-k) equals the dual value, and k=B yields a common element
-/

namespace LggrIV

/-- Definition 2.1: A defect D has finite descent through {proj_i} if it factors through some stage i. -/
def FinDesc {X Y : Type} (proj : Nat → X → Nat) (D : X → Y) : Prop :=
  ∃ (i : Nat) (d : Nat → Y), ∀ (x : X), D x = d (proj i x)

/-- Theorem 2.1: Failure of finite descent is equivalent to non-factorization at every stage. -/
theorem not_FinDesc_iff {X Y : Type} (proj : Nat → X → Nat) (D : X → Y) :
  (¬ FinDesc proj D) ↔ (∀ (i : Nat), ¬ ∃ (d : Nat → Y), ∀ (x : X), D x = d (proj i x)) := by
  constructor
  · intro h i ⟨d, hd⟩
    exact h ⟨i, d, hd⟩
  · intro h ⟨i, d, hd⟩
    exact h i ⟨d, hd⟩

/-- Moving-witness collision: A pair (x, y) with proj i x = proj i y but D x ≠ D y prevents stage factorization. -/
theorem stage_collision_witness {X Y : Type} (pi : X → Nat) (D : X → Y) :
  (∃ (x y : X), pi x = pi y ∧ D x ≠ D y) →
  (¬ ∃ (d : Nat → Y), ∀ (z : X), D z = d (pi z)) := by
  intro ⟨x, y, hpi, hD⟩ ⟨d, hd⟩
  have hx := hd x
  have hy := hd y
  have heq : D x = D y := by
    rw [hx, hy, hpi]
  exact hD heq

def collisionBool {X Y : Type} [DecidableEq Y] (pi : X → Nat) (D : X → Y) (x y : X) : Bool :=
  decide (pi x = pi y) && decide (D x ≠ D y)

/-- A colliding pair in a finite state list, scanning earlier states against later ones. -/
def firstCollision {X Y : Type} [DecidableEq Y] (pi : X → Nat) (D : X → Y) :
    List X → Option (X × X)
  | [] => none
  | x :: rest =>
    match rest.find? (collisionBool pi D x) with
    | some y => some (x, y)
    | none => firstCollision pi D rest

theorem firstCollision_some {X Y : Type} [DecidableEq Y]
    (pi : X → Nat) (D : X → Y) (xs : List X) (x y : X)
    (h : firstCollision pi D xs = some (x, y)) :
    x ∈ xs ∧ y ∈ xs ∧ pi x = pi y ∧ D x ≠ D y := by
  induction xs with
  | nil => simp [firstCollision] at h
  | cons head tail ih =>
    unfold firstCollision at h
    cases hfind : tail.find? (collisionBool pi D head) with
    | some z =>
      rw [hfind] at h
      simp at h
      rcases h with ⟨rfl, rfl⟩
      have hp := List.find?_some hfind
      unfold collisionBool at hp
      have hparts := Bool.and_eq_true_iff.mp hp
      exact ⟨List.mem_cons_self, List.mem_cons_of_mem head (List.mem_of_find?_eq_some hfind),
        of_decide_eq_true hparts.1, of_decide_eq_true hparts.2⟩
    | none =>
      rw [hfind] at h
      simp at h
      have ⟨hx, hy, hpi, hD⟩ := ih h
      exact ⟨List.mem_cons_of_mem head hx, List.mem_cons_of_mem head hy, hpi, hD⟩

theorem firstCollision_none {X Y : Type} [DecidableEq Y]
    (pi : X → Nat) (D : X → Y) (xs : List X)
    (h : firstCollision pi D xs = none) :
    ∀ x y, x ∈ xs → y ∈ xs → pi x = pi y → D x = D y := by
  induction xs with
  | nil =>
    intro x y hx
    cases hx
  | cons head tail ih =>
    unfold firstCollision at h
    cases hfind : tail.find? (collisionBool pi D head) with
    | some z =>
      rw [hfind] at h
      simp at h
    | none =>
      rw [hfind] at h
      simp at h
      have ih' := ih h
      have noHit := List.find?_eq_none.mp hfind
      have head_agrees : ∀ a, a ∈ tail → pi head = pi a → D head = D a := by
        intro a hmem hpi
        have hnot : ¬ collisionBool pi D head a := noHit a hmem
        have hpiB : decide (pi head = pi a) = true := decide_eq_true hpi
        have hDnot : decide (D head ≠ D a) ≠ true := by
          intro hDtrue
          apply hnot
          unfold collisionBool
          exact Bool.and_eq_true_iff.mpr ⟨hpiB, hDtrue⟩
        exact Decidable.of_not_not (of_decide_eq_false (Bool.eq_false_iff.mpr hDnot))
      intro x y hx hy hpi
      cases hx with
      | head =>
        cases hy with
        | head => rfl
        | tail _ hmem => exact head_agrees y hmem hpi
      | tail _ hxmem =>
        cases hy with
        | head => exact (head_agrees x hxmem hpi.symm).symm
        | tail _ hymem => exact ih' x y hxmem hymem hpi

/-- The missing direction uses one default value on stage labels outside the image. -/
def factorFrom {X Y : Type} (pi : X → Nat) (D : X → Y) (xs : List X) (y0 : Y) (n : Nat) : Y :=
  match xs.find? (fun z => pi z == n) with
  | some z => D z
  | none => y0

theorem factorFrom_agrees {X Y : Type} [DecidableEq Y]
    (pi : X → Nat) (D : X → Y) (xs : List X) (y0 : Y) (x : X)
    (hnone : firstCollision pi D xs = none) (hx : x ∈ xs) :
    D x = factorFrom pi D xs y0 (pi x) := by
  have hself : (pi x == pi x) = true := beq_iff_eq.mpr rfl
  have hsome : (xs.find? (fun z => pi z == pi x)).isSome :=
    List.find?_isSome.mpr ⟨x, hx, hself⟩
  cases hfind : xs.find? (fun z => pi z == pi x) with
  | none => simp [hfind] at hsome
  | some z =>
    have hpred := List.find?_some (p := fun (w : X) => pi w == pi x) (a := z) hfind
    have hpi : pi z = pi x := beq_iff_eq.mp hpred
    have hD : D z = D x :=
      firstCollision_none pi D xs hnone z x (List.mem_of_find?_eq_some hfind) hx hpi
    unfold factorFrom
    rw [hfind]
    exact hD.symm

/-- Finite complete carriers: non-factorization at one stage is a colliding pair. -/
theorem finite_stage_collision_iff {X Y : Type} [DecidableEq Y]
    (xs : List X) (y0 : Y) (pi : X → Nat) (D : X → Y)
    (complete : ∀ x : X, x ∈ xs) :
    (¬ ∃ d : Nat → Y, ∀ x : X, D x = d (pi x)) ↔
      ∃ x y : X, x ∈ xs ∧ y ∈ xs ∧ pi x = pi y ∧ D x ≠ D y := by
  constructor
  · intro hnot
    match hcol : firstCollision pi D xs with
    | some (x, y) =>
      exact ⟨x, y, firstCollision_some pi D xs x y hcol⟩
    | none =>
      exact False.elim <| hnot ⟨factorFrom pi D xs y0, fun x =>
        factorFrom_agrees pi D xs y0 x hcol (complete x)⟩
  · intro ⟨x, y, _, _, hpi, hD⟩ ⟨d, hd⟩
    exact hD <| by rw [hd x, hd y, hpi]

/-- Theorem M1 on a finite complete state list. One default value extends each stage off its image. -/
theorem finite_notFinDesc_iff_collisions {X Y : Type} [DecidableEq Y]
    (proj : Nat → X → Nat) (D : X → Y) (xs : List X) (y0 : Y)
    (complete : ∀ x : X, x ∈ xs) :
    (¬ FinDesc proj D) ↔
      ∀ i : Nat, ∃ x y : X, x ∈ xs ∧ y ∈ xs ∧ proj i x = proj i y ∧ D x ≠ D y := by
  rw [not_FinDesc_iff]
  constructor
  · intro h i
    exact (finite_stage_collision_iff xs y0 (proj i) D complete).mp (h i)
  · intro h i
    exact (finite_stage_collision_iff xs y0 (proj i) D complete).mpr (h i)

/-- Section 4.2: The finite-stage candidate x_n = -sum_{k=0}^{n-1} (-2)^k. -/
def x : Nat → Int
  | 0 => 0
  | n + 1 => x n - (-2 : Int)^n

/-- Alternating sign sequence representing (-1)^n. -/
def alt_sign : Nat → Int
  | 0 => 1
  | n + 1 => - alt_sign n

/-- Proposition 4.1: Exact arithmetic identity 3 * x_n + 1 = (-2)^n. -/
theorem finite_stage_identity (n : Nat) : 3 * x n + 1 = (-2 : Int)^n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [x]
    rw [Int.pow_succ]
    omega

/-- Representation of (-2)^n as 2^n * alt_sign n. -/
theorem neg_two_pow_eq (n : Nat) : (-2 : Int)^n = (2 : Int)^n * alt_sign n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [Int.pow_succ, Int.pow_succ]
    simp only [alt_sign]
    rw [ih]
    have h1 : (2 : Int)^n * alt_sign n * -2 = (2 : Int)^n * (alt_sign n * -2) := by rw [Int.mul_assoc]
    have h2 : alt_sign n * -2 = 2 * -alt_sign n := by omega
    have h3 : (2 : Int)^n * (2 * -alt_sign n) = ((2 : Int)^n * 2) * -alt_sign n := by rw [Int.mul_assoc]
    rw [h1, h2, h3]

/-- Proposition 4.1 (Local Green): 2^n divides 3 * x_n + 1 for all n. -/
theorem finite_stage_divisibility (n : Nat) : (2 : Int)^n ∣ (3 * x n + 1) := by
  rw [finite_stage_identity n]
  exact ⟨alt_sign n, neg_two_pow_eq n⟩

/-- Proposition 4.2: Transition compatibility x_{n+1} - x_n = -(-2)^n, divisible by 2^n. -/
theorem thread_compatibility (n : Nat) : (2 : Int)^n ∣ (x (n + 1) - x n) := by
  have hdiff : x (n + 1) - x n = - ((-2 : Int)^n) := by
    simp only [x]
    omega
  rw [hdiff]
  have hneg : -((-2 : Int)^n) = (2 : Int)^n * -alt_sign n := by
    rw [neg_two_pow_eq n, Int.neg_mul_eq_mul_neg]
  exact ⟨-alt_sign n, hneg⟩

/-- Auxiliary lemma: Absolute value of (2 : Int)^n is 2^n. -/
theorem int_two_pow_natAbs (n : Nat) : ((2 : Int)^n).natAbs = 2^n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [Int.pow_succ, Nat.pow_succ]
    show (((2 : Int)^n) * 2).natAbs = 2^n * 2
    rw [Int.natAbs_mul]
    rw [ih]
    rfl

/-- Theorem 4.1 (Global Red): No integer satisfies 2^n | (3 * z + 1) for all n >= 1. -/
theorem no_integral_global_solution : ¬ ∃ (z : Int), ∀ (n : Nat), (2 : Int)^n ∣ (3 * z + 1) := by
  intro ⟨z, hz⟩
  have hnz : 3 * z + 1 ≠ 0 := by omega
  have hm_pos : 0 < (3 * z + 1).natAbs := by
    cases h : (3 * z + 1).natAbs with
    | zero =>
      have hz0 : 3 * z + 1 = 0 := Int.natAbs_eq_zero.mp h
      contradiction
    | succ k => exact Nat.succ_pos k
  have h_dvd (n : Nat) : 2^n ∣ (3 * z + 1).natAbs := by
    have h1 := hz n
    have h2 : ((2 : Int)^n).natAbs ∣ (3 * z + 1).natAbs := Int.natAbs_dvd_natAbs.mpr h1
    rwa [int_two_pow_natAbs n] at h2
  have h_le (n : Nat) : 2^n ≤ (3 * z + 1).natAbs := Nat.le_of_dvd hm_pos (h_dvd n)
  have h_contra : (3 * z + 1).natAbs < 2^(3 * z + 1).natAbs := Nat.lt_pow_self (by decide)
  have h_le_m := h_le (3 * z + 1).natAbs
  omega

/-- Criterion 5.1: Reflection descent of a completed witness into the original carrier. -/
def ReflectionDescent {X X_hat : Type} (eta : X → X_hat) (R_hat : X_hat → Prop) (r_hat : X_hat) : Prop :=
  R_hat r_hat ∧ ∃ (x : X), eta x = r_hat

/-- Criterion 5.1: A completed witness descends to the original carrier iff it is in the image of eta. -/
theorem reflection_descent_criterion {X X_hat : Type} (eta : X → X_hat) (R_hat : X_hat → Prop) (r_hat : X_hat) :
  ReflectionDescent eta R_hat r_hat ↔ (R_hat r_hat ∧ ∃ (x : X), eta x = r_hat) := by
  rfl

/-- Pull `top` back along transitions from later stages to earlier ones.
`steps[i]` maps stage `i+1` to stage `i`. The result ends with `top`. -/
def pullThread {α : Type} (top : α) : List (α → α) → List α
  | [] => [top]
  | f :: rest =>
    let later := pullThread top rest
    f (later.headD top) :: later

/-- Consecutive entries agree with the transition list. The catch-all is the incompatible shape. -/
def consecutiveOk {α : Type} : List (α → α) → List α → Prop
  | [], _ :: [] => True
  | f :: fs, x :: y :: rest => x = f y ∧ consecutiveOk fs (y :: rest)
  | _, _ => False

private theorem length_pos_ne_nil {α : Type} {l : List α} {n : Nat}
    (hlen : l.length = n + 1) (hempty : l = []) : False := by
  rw [hempty, List.length_nil] at hlen
  exact Nat.succ_ne_zero n hlen.symm

private theorem pullThread_length {α : Type} (top : α) (steps : List (α → α)) :
    (pullThread top steps).length = steps.length + 1 := by
  induction steps with
  | nil => rfl
  | cons f rest ih =>
    unfold pullThread
    simp only [List.length_cons, ih]

private theorem pullThread_getLast? {α : Type} (top : α) (steps : List (α → α)) :
    (pullThread top steps).getLast? = some top := by
  induction steps with
  | nil =>
    unfold pullThread
    rfl
  | cons f rest ih =>
    cases h : pullThread top rest with
    | nil =>
      exact False.elim (length_pos_ne_nil (pullThread_length top rest) h)
    | cons s tail =>
      rw [h] at ih
      unfold pullThread
      rw [h, List.getLast?_cons_cons]
      exact ih

private theorem pullThread_consecutive {α : Type} (top : α) (steps : List (α → α)) :
    consecutiveOk steps (pullThread top steps) := by
  induction steps with
  | nil =>
    unfold pullThread consecutiveOk
    trivial
  | cons f rest ih =>
    cases h : pullThread top rest with
    | nil =>
      exact False.elim (length_pos_ne_nil (pullThread_length top rest) h)
    | cons s tail =>
      have ih' : consecutiveOk rest (s :: tail) := by
        rw [h] at ih
        exact ih
      unfold pullThread
      rw [h]
      exact ⟨rfl, ih'⟩

/-- Finite-index inverse limit along a chain. One top element pulls back to a nonempty
compatible thread. This is not the cofiltered statement of Stacks Tag 086J. -/
theorem finite_chain_limit_nonempty {α : Type} (top : α) (steps : List (α → α)) :
    consecutiveOk steps (pullThread top steps) ∧
    (pullThread top steps).getLast? = some top ∧
    (pullThread top steps) ≠ [] := by
  refine ⟨pullThread_consecutive top steps, pullThread_getLast? top steps, ?_⟩
  intro h
  exact length_pos_ne_nil (pullThread_length top steps) h

def listMax : List Nat → Nat
  | [] => 0
  | a :: as => max a (listMax as)

def countMem {α : Type} [DecidableEq α] (a : α) : List (List α) → Nat
  | [] => 0
  | fam :: rest => (if a ∈ fam then 1 else 0) + countMem a rest

/-- Greatest number of families that contain one common element. Empty support gives `0`. -/
def maxOverlap {α : Type} [DecidableEq α] (families : List (List α)) : Nat :=
  listMax ((families.flatMap id).map fun a => countMem a families)

def overlapPrimal (B k : Nat) : Int :=
  if k = B then 0 else 2 * ((B : Int) - (k : Int))

def overlapMu (B k : Nat) : Int :=
  if k = B then 0 else (B : Int) - 2 * (k : Int)

/-- Sum of the dual multipliers. Each multiplier is `-1` when `k < B`, and the sum is `0` when `k = B`. -/
def alphasSum (B k : Nat) : Int :=
  if k = B then 0 else - (B : Int)

private theorem countMem_le_length {α : Type} [DecidableEq α] (a : α) (families : List (List α)) :
    countMem a families ≤ families.length := by
  induction families with
  | nil => simp [countMem]
  | cons fam rest ih =>
    simp only [countMem, List.length_cons]
    match (inferInstance : Decidable (a ∈ fam)) with
    | .isTrue h =>
      simp [h]
      omega
    | .isFalse h =>
      simp [h]
      omega

private theorem countMem_eq_length_mem {α : Type} [DecidableEq α] (a : α) (families : List (List α))
    (h : countMem a families = families.length) :
    ∀ fam, fam ∈ families → a ∈ fam := by
  induction families with
  | nil =>
    intro fam hf
    cases hf
  | cons fam rest ih =>
    intro fam' hf
    simp only [countMem, List.length_cons] at h
    match (inferInstance : Decidable (a ∈ fam)) with
    | .isTrue ha =>
      have hrest : countMem a rest = rest.length := by
        simp [ha] at h
        omega
      simp only [List.mem_cons] at hf
      rcases hf with rfl | hmem
      · exact ha
      · exact ih hrest fam' hmem
    | .isFalse ha =>
      simp [ha] at h
      have hle := countMem_le_length a rest
      omega

private theorem listMax_le_of_all {l : List Nat} {B : Nat} (h : ∀ n, n ∈ l → n ≤ B) :
    listMax l ≤ B := by
  induction l with
  | nil => simp [listMax]
  | cons a as ih =>
    have ha : a ≤ B := h a List.mem_cons_self
    have has : listMax as ≤ B := ih (fun n hn => h n (List.mem_cons_of_mem a hn))
    simp only [listMax]
    omega

private theorem maxOverlap_le_length {α : Type} [DecidableEq α] (families : List (List α)) :
    maxOverlap families ≤ families.length := by
  unfold maxOverlap
  refine listMax_le_of_all ?_
  intro n hn
  simp only [List.mem_map] at hn
  rcases hn with ⟨a, _, rfl⟩
  exact countMem_le_length a families

private theorem listMax_mem (l : List Nat) (hne : l ≠ []) : listMax l ∈ l := by
  induction l with
  | nil => contradiction
  | cons a as ih =>
    cases as with
    | nil =>
      simp [listMax]
    | cons b bs =>
      have ih' : listMax (b :: bs) ∈ b :: bs := ih (List.cons_ne_nil b bs)
      have goal : max a (listMax (b :: bs)) ∈ a :: b :: bs := by
        match Nat.decLe a (listMax (b :: bs)) with
        | .isTrue hle =>
          have hmax : max a (listMax (b :: bs)) = listMax (b :: bs) := by
            show (if a ≤ listMax (b :: bs) then listMax (b :: bs) else a) = listMax (b :: bs)
            simp [hle]
          rw [hmax]
          exact List.mem_cons_of_mem a ih'
        | .isFalse hle =>
          have hmax : max a (listMax (b :: bs)) = a := by
            show (if a ≤ listMax (b :: bs) then listMax (b :: bs) else a) = a
            simp [hle]
          rw [hmax]
          exact List.mem_cons_self
      exact goal

private theorem exists_max_count {α : Type} [DecidableEq α]
    (families : List (List α)) (elems : List α) (hne : elems ≠ []) :
    ∃ a, a ∈ elems ∧ countMem a families = listMax (elems.map fun x => countMem x families) := by
  have hcounts : elems.map (fun x => countMem x families) ≠ [] := by
    intro hempty
    cases elems with
    | nil => exact hne rfl
    | cons head tail =>
      rw [List.map_cons] at hempty
      exact List.cons_ne_nil (countMem head families) (tail.map fun x => countMem x families) hempty
  have hmem := listMax_mem (elems.map fun x => countMem x families) hcounts
  rw [List.mem_map] at hmem
  rcases hmem with ⟨a, ha, hf⟩
  exact ⟨a, ha, hf⟩

private theorem exists_common_of_full {α : Type} [DecidableEq α]
    (families : List (List α)) (hne : families ≠ [])
    (hk : maxOverlap families = families.length) :
    ∃ a, ∀ fam, fam ∈ families → a ∈ fam := by
  have helems : families.flatMap id ≠ [] := by
    intro hempty
    cases families with
    | nil => exact False.elim (hne rfl)
    | cons fam rest =>
      unfold maxOverlap at hk
      rw [hempty, List.map_nil, listMax, List.length_cons] at hk
      exact Nat.succ_ne_zero rest.length hk.symm
  obtain ⟨a, _, hc⟩ := exists_max_count families (families.flatMap id) helems
  have hc' : countMem a families = families.length := by
    unfold maxOverlap at hk
    rwa [hk] at hc
  exact ⟨a, countMem_eq_length_mem a families hc'⟩

private theorem overlap_arith (B k : Nat) :
    overlapPrimal B k = overlapMu B k - alphasSum B k := by
  unfold overlapPrimal overlapMu alphasSum
  match decEq k B with
  | .isTrue h =>
    simp [h]
  | .isFalse h =>
    simp [h]
    omega

private theorem overlap_pos (B k : Nat) (hlt : k < B) :
    overlapPrimal B k = 2 * ((B : Int) - (k : Int)) ∧ (0 : Int) < overlapPrimal B k := by
  have hne : ¬ k = B := Nat.ne_of_lt hlt
  unfold overlapPrimal
  simp [hne]
  omega

/-- Finite overlap identity computed by the rational dual certificate.
`k = maxOverlap families` and `B = families.length`. The primal defect equals
`mu - sum alpha`, with each alpha equal to `-1` when `k < B`. A nonempty list with
`k = B` has an element common to every family. This is not Stacks Tag 07KV. -/
theorem overlap_dual_residual {α : Type} [DecidableEq α] (families : List (List α)) :
    maxOverlap families ≤ families.length ∧
    overlapPrimal families.length (maxOverlap families) =
      overlapMu families.length (maxOverlap families) - alphasSum families.length (maxOverlap families) ∧
    (families ≠ [] ∧ maxOverlap families = families.length →
      ∃ a, ∀ fam, fam ∈ families → a ∈ fam) ∧
    (maxOverlap families < families.length →
      overlapPrimal families.length (maxOverlap families) =
        2 * ((families.length : Int) - (maxOverlap families : Int)) ∧
      (0 : Int) < overlapPrimal families.length (maxOverlap families)) := by
  refine ⟨maxOverlap_le_length families, overlap_arith _ _, ?_, ?_⟩
  · intro h
    exact exists_common_of_full families h.1 h.2
  · intro hlt
    exact overlap_pos _ _ hlt

end LggrIV
