/-!
# BellNegMass.lean — certificate form of Theorems 24 and 27

Lean 4 (core only, no Mathlib; tested on toolchain v4.35.0).  Companion to
`math_notes.md` Part V and the exact-rational scripts `verify_obstruction.py`,
`verify_headroom.py`, `verify_cf2n.py`.

## What is formalized

The two "negative mass" theorems of the notes, in scaled-integer certificate
form (the script's arithmetic IS the proof trace; every quantity is an integer
with an explicit denominator recorded in the comments):

* **Theorem 27** (isotropic CHSH line).  Write `v = m/8` with `m : Nat`.
  The isotropic box has entries `p_v(a,b|x,y) = (8 + m·c(x,y)·s(a)s(b))/32`
  (denominator 32 per cell) and the canonical signed extension has weights
  `q^v_λ = (8 + m·K(λ))/128` over the 16 deterministic assignments.  Then,
  with `N` the minimal total negative mass of a normalized signed extension:
  - `q^v` is normalized (`Σ q = 128`), projects to the table
    (`T(q)(cell) = 32 + 4·m·coef = 128·p_v(cell)`), and has negative mass
    exactly `16·max(0, m-4) = 128·max(0, v-1/2)`;   **[upper bound]**
  - EVERY normalized signed extension of the table has negative mass
    `≥ 16·max(0, m-4)`.                              **[lower bound]**
  Hence `N(p_v) = max(0, v - 1/2)` — Theorem 27, all v.

* **Theorem 24** (Mermin/GHZ line).  Identical structure with 64 assignments,
  64 cells, the Mermin functional `M` in place of `K`, weights
  `q^v_λ = (8 + m·M(λ))/512`, cells `Q_v(cell) = (8 + m·χ·s_as_bs_c)/64`,
  and the same value `max(0, v - 1/2)`.

## Method (no LP duality is developed)

The lower bound is the certificate-checking form of Propositions 4/20:
`Σ_cells coef·T(w) = Σ_λ w_λ·K(λ)` by a double-sum swap (`fubini_chsh`), the
deterministic bound `K(λ) ∈ {±2}` (a 16-case kernel `decide`), and the
pointwise step `w_λ·K(λ) ≤ 2·|w_λ|` give `S(p_v) ≤ 2·(1 + 2N)`; with
`S(p_v) = 4v` this is exactly `N ≥ v - 1/2`.  All finite sums run through a
tiny exact-sum library `qsum` proven from scratch by induction; every closed
finite identity (deterministic ranges, parity sums, match-sums) is a
`decide`-checked kernel computation over `Fin 16` / `Fin 64` — the Lean twin
of Python checks C12–C21.
-/

set_option maxRecDepth 10000

/-! ## §0  An exact sum library over ℤ -/

/-- Exact sum of an `Nat → Int` function over `0, ..., n-1`. -/
def qsum (f : Nat → Int) : Nat → Int
  | 0 => 0
  | n + 1 => qsum f n + f n

theorem qsum_succ (f : Nat → Int) (n : Nat) : qsum f (n + 1) = qsum f n + f n := rfl

theorem qsum_ext {f g : Nat → Int} {n : Nat} (h : ∀ j, j < n → f j = g j) :
    qsum f n = qsum g n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [qsum_succ, qsum_succ, ih (fun j hj => h j (Nat.lt_succ_of_lt hj))]
    exact congrArg (fun t => qsum g n + t) (h n (Nat.lt_succ_self n))

theorem qsum_add (f g : Nat → Int) (n : Nat) :
    qsum (fun j => f j + g j) n = qsum f n + qsum g n := by
  induction n with
  | zero => rfl
  | succ n ih => rw [qsum_succ, qsum_succ, qsum_succ, ih]; omega

theorem qsum_one (n : Nat) : qsum (fun _ => (1 : Int)) n = (n : Int) := by
  induction n with
  | zero => rfl
  | succ n ih => rw [qsum_succ, ih]; omega

theorem qsum_const (c : Int) (n : Nat) : qsum (fun _ => c) n = (n : Int) * c := by
  induction n with
  | zero => simp [qsum]
  | succ n ih =>
    rw [qsum_succ, ih]
    have hcast : ((n + 1 : Nat) : Int) = (n : Int) + 1 := by omega
    rw [hcast, Int.add_mul]
    omega

theorem qsum_mul_left (c : Int) (f : Nat → Int) (n : Nat) :
    qsum (fun j => c * f j) n = c * qsum f n := by
  induction n with
  | zero => simp [qsum]
  | succ n ih => rw [qsum_succ, qsum_succ, ih, Int.mul_add]

theorem qsum_mul_right (f : Nat → Int) (c : Int) (n : Nat) :
    qsum (fun j => f j * c) n = qsum f n * c := by
  induction n with
  | zero => simp [qsum]
  | succ n ih => rw [qsum_succ, qsum_succ, ih, Int.add_mul]

theorem qsum_le {f g : Nat → Int} {n : Nat} (h : ∀ j, j < n → f j ≤ g j) :
    qsum f n ≤ qsum g n := by
  induction n with
  | zero => simp [qsum]
  | succ n ih =>
    have h1 := ih (fun j hj => h j (Nat.lt_succ_of_lt hj))
    have h2 := h n (Nat.lt_succ_self n)
    rw [qsum_succ, qsum_succ]; omega

theorem qsum_nonneg {f : Nat → Int} {n : Nat} (h : ∀ j, j < n → 0 ≤ f j) :
    0 ≤ qsum f n := by
  have h1 : qsum (fun _ => (0 : Int)) n ≤ qsum f n := qsum_le h
  rw [qsum_const] at h1
  omega

theorem qsum_comm (f : Nat → Nat → Int) (n m : Nat) :
    qsum (fun i => qsum (fun j => f i j) m) n = qsum (fun j => qsum (fun i => f i j) n) m := by
  induction n with
  | zero =>
    have hr : qsum (fun j => qsum (fun i => f i j) 0) m = qsum (fun j => (0 : Int)) m :=
      qsum_ext (fun j _ => rfl)
    rw [hr, qsum_const, Int.mul_zero]
    rfl
  | succ n ih =>
    have h1 : ∀ j, qsum (fun i => f i j) (n + 1) = qsum (fun i => f i j) n + f n j :=
      fun j => qsum_succ _ _
    rw [qsum_succ, qsum_ext (fun j _ => h1 j), qsum_add, ih]

/-- Pointwise helper: pull a scalar through a `Bool` conditional. -/
theorem ite_as_mul (b : Bool) (c : Int) : (if b then c else 0) = c * (if b then 1 else 0) := by
  cases b <;> simp

/-- Pointwise helper: swap a scalar with a `Bool` conditional. -/
theorem mul_ite_swap (w c : Int) (b : Bool) :
    w * (if b then c else 0) = c * (if b then w else 0) := by
  cases b <;> simp [Int.mul_comm]

/-- Pointwise helper: split a conditional summand. -/
theorem ite_add_mul (b : Bool) (c : Int) (m : Int) (h : Int) :
    (if b then c + m * h else 0) = (if b then c else 0) + m * (if b then h else 0) := by
  cases b <;> simp

/-- Pointwise helper for the negative-part split. -/
theorem max_split (x : Int) : max 0 x = x + max 0 (-x) := by omega

/-! ## §1  Scenario encoding -/

/-- bit `k` of index `i` (little-endian). -/
def bit (i k : Nat) : Nat := (i / 2 ^ k) % 2

/-- spin of a bit: bit 0 ↦ +1, bit 1 ↦ -1. -/
def sp (b : Nat) : Int := 1 - 2 * b

/-! ## §2  CHSH (2,2,2): 16 cells, 16 deterministic assignments

Cell `i`: `x = i/8`, `y = (i/4)%2`, outcome bits `a = (i/2)%2`, `b = i%2`.
Assignment `j`: bits `(α₀,α₁,β₀,β₁) = (bit j 0, bit j 1, bit j 2, bit j 3)`.
`matchC i j` says assignment j realizes cell i. -/
def matchC (i j : Nat) : Bool :=
  (bit j (i / 8) == (i / 2) % 2) && (bit j (2 + (i / 4) % 2) == i % 2)

/-- CHSH functional coefficients: `c(x,y)·s(a)·s(b)` with `c = (+,+,+,-)`. -/
def coefC (i : Nat) : Int :=
  (if i / 8 == 1 && (i / 4) % 2 == 1 then (-1 : Int) else 1)
    * sp ((i / 2) % 2) * sp (i % 2)

/-- The CHSH value of an assignment, defined as the sum of `coefC` over the
cells it realizes — definitionally the moment-duality partner of `T`. -/
def Kdef (j : Nat) : Int := qsum (fun i => if matchC i j then coefC i else 0) 16

/-- Projection `T`: the table produced by (possibly signed) weights `w`. -/
def Tchsh (w : Nat → Int) (i : Nat) : Int := qsum (fun j => if matchC i j then w j else 0) 16

-- Closed facts (kernel-checked; the Lean twins of Python checks C12-C19)
theorem K_pm1 : ∀ j : Fin 16, Kdef j.val = 2 ∨ Kdef j.val = -2 := by decide
theorem sumK_zero : qsum (fun j => Kdef j) 16 = 0 := by decide
theorem cntK_neg : qsum (fun j => if Kdef j = -2 then (1 : Int) else 0) 16 = 8 := by decide
theorem cardC : ∀ i : Fin 16,
    qsum (fun j => if matchC i.val j then (1 : Int) else 0) 16 = 4 := by decide
theorem matchK : ∀ i : Fin 16,
    qsum (fun j => if matchC i.val j then Kdef j else 0) 16 = 4 * coefC i.val := by decide
theorem sumCoef_zero : qsum (fun i => coefC i) 16 = 0 := by decide
theorem sumCoefSq : qsum (fun i => coefC i * coefC i) 16 = 16 := by decide
theorem coefC_pm1 : ∀ i : Fin 16, coefC i.val = 1 ∨ coefC i.val = -1 := by decide

/-- Moment duality: `Σ_cells coefC·T(w) = Σ_λ w_λ·K(λ)`. -/
theorem fubini_chsh (w : Nat → Int) :
    qsum (fun j => w j * Kdef j) 16 = qsum (fun i => coefC i * Tchsh w i) 16 := by
  have step1 : qsum (fun j => w j * Kdef j) 16
      = qsum (fun j => qsum (fun i => w j * (if matchC i j then coefC i else 0)) 16) 16 := by
    simp only [Kdef]
    exact qsum_ext
      (fun j _ => (qsum_mul_left (w j) (fun i => if matchC i j then coefC i else 0) 16).symm)
  have step2 : qsum (fun j => qsum (fun i => w j * (if matchC i j then coefC i else 0)) 16) 16
      = qsum (fun i => qsum (fun j => w j * (if matchC i j then coefC i else 0)) 16) 16 :=
    qsum_comm (fun a b => w a * (if matchC b a then coefC b else 0)) 16 16
  have step3 : qsum (fun i => qsum (fun j => w j * (if matchC i j then coefC i else 0)) 16) 16
      = qsum (fun i => coefC i * Tchsh w i) 16 := by
    have ptw : ∀ i, qsum (fun j => w j * (if matchC i j then coefC i else 0)) 16
        = coefC i * Tchsh w i := by
      intro i
      rw [qsum_ext (fun j _ => mul_ite_swap (w j) (coefC i) (matchC i j)),
        qsum_mul_left (coefC i) (fun j => if matchC i j then w j else 0) 16]
      rfl
    exact qsum_ext (fun i _ => ptw i)
  rw [step1, step2, step3]

/-! ### Theorem 27 (certificate form) -/

/-- Upper bound, part 1: the canonical extension is normalized. -/
theorem thm27_normalization (m : Nat) :
    qsum (fun j => 8 + (m : Int) * Kdef j) 16 = 128 := by
  rw [qsum_add, qsum_const, qsum_mul_left, sumK_zero]
  omega

/-- Upper bound, part 2: it projects to the isotropic table
(`32 + 4·m·coefC i = 128 · p_v(cell i)`). -/
theorem thm27_table (m : Nat) (i : Nat) (hi : i < 16) :
    Tchsh (fun j => 8 + (m : Int) * Kdef j) i = 32 + 4 * (m : Int) * coefC i := by
  simp only [Tchsh]
  have h1 : coefC i = 1 ∨ coefC i = -1 := coefC_pm1 ⟨i, hi⟩
  rw [qsum_ext (fun j _ => ite_add_mul (matchC i j) 8 (m : Int) (Kdef j)), qsum_add,
    qsum_ext (fun j _ => ite_as_mul (matchC i j) (8 : Int))]
  rw [qsum_mul_left 8 (fun j => if matchC i j then (1 : Int) else 0) 16, cardC ⟨i, hi⟩]
  rw [qsum_mul_left (m : Int) (fun j => if matchC i j then Kdef j else 0) 16, matchK ⟨i, hi⟩]
  rcases h1 with h | h <;> rw [h] <;> omega

/-- Upper bound, part 3: its negative mass is exactly `16·max(0, m-4)`. -/
theorem thm27_mass (m : Nat) :
    qsum (fun j => max 0 (-(8 + (m : Int) * Kdef j))) 16 = 16 * max 0 ((m : Int) - 4) := by
  have pt : ∀ j, j < 16 → max 0 (-(8 + (m : Int) * Kdef j))
      = (2 * max 0 ((m : Int) - 4)) * (if Kdef j = -2 then (1 : Int) else 0) := by
    intro j hj
    have h1 : Kdef j = 2 ∨ Kdef j = -2 := K_pm1 ⟨j, hj⟩
    rcases h1 with h | h
    · rw [h, if_neg (by decide : ¬((2 : Int) = -2))]
      omega
    · rw [h, if_pos (by decide : ((-2 : Int) = -2))]
      omega
  rw [qsum_ext pt, qsum_mul_left, cntK_neg]
  omega

/-- Lower bound: EVERY normalized signed extension of the isotropic table has
negative mass `≥ 16·max(0, m-4)`. -/
theorem thm27_lower (m : Nat) (w : Nat → Int)
    (hnorm : qsum w 16 = 128)
    (htab : ∀ i, i < 16 → Tchsh w i = 32 + 4 * (m : Int) * coefC i) :
    qsum (fun j => max 0 (- w j)) 16 ≥ 16 * max 0 ((m : Int) - 4) := by
  have hpos : 0 ≤ qsum (fun j => max 0 (- w j)) 16 :=
    qsum_nonneg (fun j _ => by omega)
  have hfub : qsum (fun j => w j * Kdef j) 16 = 64 * (m : Int) := by
    rw [fubini_chsh]
    have ptw : ∀ i, i < 16 → coefC i * Tchsh w i
        = coefC i * (32 + 4 * (m : Int) * coefC i) := fun i hi => by rw [htab i hi]
    rw [qsum_ext ptw]
    have key : ∀ i, i < 16 → coefC i * (32 + 4 * (m : Int) * coefC i)
        = 32 * coefC i + 4 * (m : Int) := by
      intro i hi
      have h1 : coefC i = 1 ∨ coefC i = -1 := coefC_pm1 ⟨i, hi⟩
      rcases h1 with h | h <;> rw [h] <;> omega
    rw [qsum_ext key, qsum_add, qsum_mul_left, sumCoef_zero, qsum_const]
    omega
  have pt2 : ∀ j, j < 16 → w j * Kdef j ≤ 2 * max 0 (w j) + 2 * max 0 (-(w j)) := by
    intro j hj
    have h1 : Kdef j = 2 ∨ Kdef j = -2 := K_pm1 ⟨j, hj⟩
    rcases h1 with h | h <;> rw [h] <;> omega
  have h2 : qsum (fun j => w j * Kdef j) 16
      ≤ qsum (fun j => 2 * max 0 (w j) + 2 * max 0 (-(w j))) 16 := qsum_le pt2
  rw [qsum_add, qsum_mul_left, qsum_mul_left] at h2
  have h3 : qsum (fun j => max 0 (w j)) 16 = 128 + qsum (fun j => max 0 (- w j)) 16 := by
    rw [qsum_ext (fun j _ => max_split (w j)), qsum_add, hnorm]
  rw [hfub] at h2
  omega

/-- **Theorem 27, certificate form.**  For every `m : Nat` (i.e. every
`v = m/8 ∈ [0,1]`): the canonical signed extension `q^v_λ = (8 + m·K(λ))/128`
is normalized, projects to the isotropic table, and has negative mass exactly
`16·max(0, m-4)` — and no normalized signed extension has smaller negative
mass.  Dividing by 128: `N(p_v) = max(0, m-4)/8 = max(0, v - 1/2)`. -/
theorem theorem27 (m : Nat) :
    (∃ q : Nat → Int,
      qsum q 16 = 128
        ∧ (∀ i, i < 16 → Tchsh q i = 32 + 4 * (m : Int) * coefC i)
        ∧ qsum (fun j => max 0 (-(q j))) 16 = 16 * max 0 ((m : Int) - 4))
      ∧ ∀ w : Nat → Int,
          qsum w 16 = 128 →
          (∀ i, i < 16 → Tchsh w i = 32 + 4 * (m : Int) * coefC i) →
          qsum (fun j => max 0 (-(w j))) 16 ≥ 16 * max 0 ((m : Int) - 4) := by
  refine ⟨⟨fun j => 8 + (m : Int) * Kdef j, thm27_normalization m,
    fun i hi => thm27_table m i hi, thm27_mass m⟩, fun w h1 h2 => thm27_lower m w h1 h2⟩

/-! ## §3  GHZ (3,2,2): 64 cells, 64 deterministic assignments, the Mermin line

Cell `i`: `x = i/32`, `y = (i/16)%2`, `z = (i/8)%2`, outcome bits
`a = (i/4)%2, b = (i/2)%2, c = i%2`.  Assignment `j`: bits
`(α₀,α₁,β₀,β₁,γ₀,γ₁)`. -/
def matchG (i j : Nat) : Bool :=
  (bit j (i / 32) == (i / 4) % 2) && (bit j (2 + (i / 16) % 2) == (i / 2) % 2)
    && (bit j (4 + (i / 8) % 2) == i % 2)

/-- Mermin coefficient pattern: `χ = -1` at (0,0,0), `+1` at the three
contexts with exactly two 1-settings, `0` elsewhere; times the outcome spins. -/
def chi (x y z : Nat) : Int :=
  if x + y + z == 0 then -1 else if x + y + z == 2 then 1 else 0

def chiCell (i : Nat) : Int :=
  chi (i / 32) ((i / 16) % 2) ((i / 8) % 2)
    * sp ((i / 4) % 2) * sp ((i / 2) % 2) * sp (i % 2)

/-- The Mermin value of an assignment (sum of `chiCell` over realized cells). -/
def Mdef (j : Nat) : Int := qsum (fun i => if matchG i j then chiCell i else 0) 64

/-- Projection `T` for the GHZ scenario. -/
def Tghz (w : Nat → Int) (i : Nat) : Int := qsum (fun j => if matchG i j then w j else 0) 64

-- Closed facts (kernel-checked; the Lean twins of Python checks C12-C16)
theorem M_pm1 : ∀ j : Fin 64, Mdef j.val = 2 ∨ Mdef j.val = -2 := by decide
theorem sumM_zero : qsum (fun j => Mdef j) 64 = 0 := by decide
theorem cntM_neg : qsum (fun j => if Mdef j = -2 then (1 : Int) else 0) 64 = 32 := by decide
theorem cardG : ∀ i : Fin 64,
    qsum (fun j => if matchG i.val j then (1 : Int) else 0) 64 = 8 := by decide
theorem matchM : ∀ i : Fin 64,
    qsum (fun j => if matchG i.val j then Mdef j else 0) 64 = 8 * chiCell i.val := by decide
theorem sumChi_zero : qsum (fun i => chiCell i) 64 = 0 := by decide
theorem sumChiSq : qsum (fun i => chiCell i * chiCell i) 64 = 32 := by decide
theorem chiCell_pm1 : ∀ i : Fin 64,
    chiCell i.val = 1 ∨ chiCell i.val = -1 ∨ chiCell i.val = 0 := by decide

/-- Moment duality for the Mermin functional:
`Σ_cells chiCell · T(w) = Σ_λ w_λ · M(λ)`. -/
theorem fubini_ghz (w : Nat → Int) :
    qsum (fun j => w j * Mdef j) 64 = qsum (fun i => chiCell i * Tghz w i) 64 := by
  have step1 : qsum (fun j => w j * Mdef j) 64
      = qsum (fun j => qsum (fun i => w j * (if matchG i j then chiCell i else 0)) 64) 64 := by
    simp only [Mdef]
    exact qsum_ext
      (fun j _ => (qsum_mul_left (w j) (fun i => if matchG i j then chiCell i else 0) 64).symm)
  have step2 : qsum (fun j => qsum (fun i => w j * (if matchG i j then chiCell i else 0)) 64) 64
      = qsum (fun i => qsum (fun j => w j * (if matchG i j then chiCell i else 0)) 64) 64 :=
    qsum_comm (fun a b => w a * (if matchG b a then chiCell b else 0)) 64 64
  have step3 : qsum (fun i => qsum (fun j => w j * (if matchG i j then chiCell i else 0)) 64) 64
      = qsum (fun i => chiCell i * Tghz w i) 64 := by
    have ptw : ∀ i, qsum (fun j => w j * (if matchG i j then chiCell i else 0)) 64
        = chiCell i * Tghz w i := by
      intro i
      rw [qsum_ext (fun j _ => mul_ite_swap (w j) (chiCell i) (matchG i j)),
        qsum_mul_left (chiCell i) (fun j => if matchG i j then w j else 0) 64]
      rfl
    exact qsum_ext (fun i _ => ptw i)
  rw [step1, step2, step3]

/-! ### Theorem 24 (certificate form) -/

theorem thm24_normalization (m : Nat) :
    qsum (fun j => 8 + (m : Int) * Mdef j) 64 = 512 := by
  rw [qsum_add, qsum_const, qsum_mul_left, sumM_zero]
  omega

theorem thm24_table (m : Nat) (i : Nat) (hi : i < 64) :
    Tghz (fun j => 8 + (m : Int) * Mdef j) i = 64 + 8 * (m : Int) * chiCell i := by
  simp only [Tghz]
  have h1 : chiCell i = 1 ∨ chiCell i = -1 ∨ chiCell i = 0 := chiCell_pm1 ⟨i, hi⟩
  rw [qsum_ext (fun j _ => ite_add_mul (matchG i j) 8 (m : Int) (Mdef j)), qsum_add,
    qsum_ext (fun j _ => ite_as_mul (matchG i j) (8 : Int))]
  rw [qsum_mul_left 8 (fun j => if matchG i j then (1 : Int) else 0) 64, cardG ⟨i, hi⟩]
  rw [qsum_mul_left (m : Int) (fun j => if matchG i j then Mdef j else 0) 64, matchM ⟨i, hi⟩]
  rcases h1 with h | h | h <;> rw [h] <;> omega

theorem thm24_mass (m : Nat) :
    qsum (fun j => max 0 (-(8 + (m : Int) * Mdef j))) 64 = 64 * max 0 ((m : Int) - 4) := by
  have pt : ∀ j, j < 64 → max 0 (-(8 + (m : Int) * Mdef j))
      = (2 * max 0 ((m : Int) - 4)) * (if Mdef j = -2 then (1 : Int) else 0) := by
    intro j hj
    have h1 : Mdef j = 2 ∨ Mdef j = -2 := M_pm1 ⟨j, hj⟩
    rcases h1 with h | h
    · rw [h, if_neg (by decide : ¬((2 : Int) = -2))]
      omega
    · rw [h, if_pos (by decide : ((-2 : Int) = -2))]
      omega
  rw [qsum_ext pt, qsum_mul_left, cntM_neg]
  omega

theorem thm24_lower (m : Nat) (w : Nat → Int)
    (hnorm : qsum w 64 = 512)
    (htab : ∀ i, i < 64 → Tghz w i = 64 + 8 * (m : Int) * chiCell i) :
    qsum (fun j => max 0 (- w j)) 64 ≥ 64 * max 0 ((m : Int) - 4) := by
  have hpos : 0 ≤ qsum (fun j => max 0 (- w j)) 64 :=
    qsum_nonneg (fun j _ => by omega)
  have hfub : qsum (fun j => w j * Mdef j) 64 = 256 * (m : Int) := by
    rw [fubini_ghz]
    have ptw : ∀ i, i < 64 → chiCell i * Tghz w i
        = chiCell i * (64 + 8 * (m : Int) * chiCell i) := fun i hi => by rw [htab i hi]
    rw [qsum_ext ptw]
    have key : ∀ i, i < 64 → chiCell i * (64 + 8 * (m : Int) * chiCell i)
        = 64 * chiCell i + 8 * (m : Int) * (chiCell i * chiCell i) := by
      intro i hi
      have h1 : chiCell i = 1 ∨ chiCell i = -1 ∨ chiCell i = 0 := chiCell_pm1 ⟨i, hi⟩
      rcases h1 with h | h | h <;> rw [h] <;> omega
    rw [qsum_ext key, qsum_add, qsum_mul_left, sumChi_zero, qsum_mul_left, sumChiSq]
    omega
  have pt2 : ∀ j, j < 64 → w j * Mdef j ≤ 2 * max 0 (w j) + 2 * max 0 (-(w j)) := by
    intro j hj
    have h1 : Mdef j = 2 ∨ Mdef j = -2 := M_pm1 ⟨j, hj⟩
    rcases h1 with h | h <;> rw [h] <;> omega
  have h2 : qsum (fun j => w j * Mdef j) 64
      ≤ qsum (fun j => 2 * max 0 (w j) + 2 * max 0 (-(w j))) 64 := qsum_le pt2
  rw [qsum_add, qsum_mul_left, qsum_mul_left] at h2
  have h3 : qsum (fun j => max 0 (w j)) 64 = 512 + qsum (fun j => max 0 (- w j)) 64 := by
    rw [qsum_ext (fun j _ => max_split (w j)), qsum_add, hnorm]
  rw [hfub] at h2
  omega

/-- **Theorem 24, certificate form.**  For every `m : Nat` (i.e. every
`v = m/8 ∈ [0,1]`): the canonical signed extension `q^v_λ = (8 + m·M(λ))/512`
is normalized (`Σ = 512`), projects to the Mermin-line table
(`T(q)(cell) = 512 · Q_v(cell)`), and has negative mass exactly
`64·max(0, m-4) = 512·max(0, v-1/2)` — and no normalized signed extension of
the table has smaller negative mass.  Dividing by 512:
`N(Q_v) = max(0, v - 1/2)` — Theorem 24. -/
theorem theorem24 (m : Nat) :
    (∃ q : Nat → Int,
      qsum q 64 = 512
        ∧ (∀ i, i < 64 → Tghz q i = 64 + 8 * (m : Int) * chiCell i)
        ∧ qsum (fun j => max 0 (-(q j))) 64 = 64 * max 0 ((m : Int) - 4))
      ∧ ∀ w : Nat → Int,
          qsum w 64 = 512 →
          (∀ i, i < 64 → Tghz w i = 64 + 8 * (m : Int) * chiCell i) →
          qsum (fun j => max 0 (-(w j))) 64 ≥ 64 * max 0 ((m : Int) - 4) := by
  refine ⟨⟨fun j => 8 + (m : Int) * Mdef j, thm24_normalization m,
    fun i hi => thm24_table m i hi, thm24_mass m⟩, fun w h1 h2 => thm24_lower m w h1 h2⟩

-- Axiom census: both packaging theorems must be axiom-free beyond Lean's
-- three standard axioms (propext, Quot.sound, Classical.choice via simp/omega).
#print axioms theorem27
#print axioms theorem24