/- Finite content of the operator-lift identities.

The monograph's Mazur square root, real punctured line, and trace-norm
triangle inequality stay classical. These theorems use integer and rational
arithmetic only.
-/

def nsum : List Nat → Nat
  | [] => 0
  | x :: xs => x + nsum xs

def mass : List Int → Nat
  | [] => 0
  | x :: xs => x.natAbs + mass xs

def sumSq : List Int → Int
  | [] => 0
  | x :: xs => x * x + sumSq xs

def dotp : List Int → List Int → Int
  | [], [] => 0
  | x :: xs, y :: ys => x * y + dotp xs ys
  | _, _ => 0

def subL : List Int → List Int → List Int
  | [], [] => []
  | x :: xs, y :: ys => (x - y) :: subL xs ys
  | _, _ => []

def addL : List Int → List Int → List Int
  | [], [] => []
  | x :: xs, y :: ys => (x + y) :: addL xs ys
  | _, _ => []

structure Gate where
  phi : Rat
  gamma : Rat
  finiteRatio : Bool
  rcl : Rat
  xi : Rat

def admits (rMax eps : Rat) (cur cand : Gate) : Bool :=
  if cand.finiteRatio = false then
    false
  else if rMax < cand.rcl then
    false
  else if cand.phi < cur.phi - eps then
    true
  else if cur.phi < cand.phi then
    false
  else if cand.gamma < cur.gamma - eps then
    true
  else if cur.gamma < cand.gamma then
    false
  else if cand.xi < cur.xi - eps then
    true
  else
    false

def feasible (rMax : Rat) (g : Gate) : Bool :=
  g.finiteRatio && decide (g.rcl ≤ rMax)

def compareGates (rMax : Rat) (a b : Gate) : Int :=
  if feasible rMax a && !(feasible rMax b) then
    -1
  else if feasible rMax b && !(feasible rMax a) then
    1
  else if !(feasible rMax a) && !(feasible rMax b) then
    0
  else if a.phi < b.phi then
    -1
  else if b.phi < a.phi then
    1
  else if a.gamma < b.gamma then
    -1
  else if b.gamma < a.gamma then
    1
  else if a.xi < b.xi then
    -1
  else if b.xi < a.xi then
    1
  else
    0

theorem mass_eq_nsum (v : List Int) : mass v = nsum (v.map Int.natAbs) := by
  induction v with
  | nil => rfl
  | cons x xs ih =>
    simp [mass, nsum, ih]

theorem trace_norm_eq_mass (v : List Int) : mass v = nsum (v.map Int.natAbs) :=
  mass_eq_nsum v

theorem natAbs_neg (x : Int) : (-x).natAbs = x.natAbs := by
  cases x with
  | ofNat n =>
    cases n with
    | zero => rfl
    | succ n =>
      have h : -Int.ofNat (n + 1) = Int.negSucc n := by simp [Int.negSucc_eq]
      rw [h]
      rfl
  | negSucc n =>
    rfl

theorem mass_neg (v : List Int) : mass (v.map Neg.neg) = mass v := by
  induction v with
  | nil => rfl
  | cons x xs ih =>
    simp [mass]
    exact ih

theorem weight_sign_cross (x : Int) (v : List Int) :
    (-x).natAbs * mass v = x.natAbs * mass (v.map Neg.neg) := by
  rw [mass_neg, natAbs_neg]

theorem mass_scale_int (c : Int) (v : List Int) :
    mass (v.map fun x => c * x) = c.natAbs * mass v := by
  induction v with
  | nil => simp [mass]
  | cons x xs ih =>
    simp only [List.map_cons, mass]
    rw [Int.natAbs_mul, ih, Nat.mul_add]

theorem weight_scale_cross (c x : Int) (v : List Int) :
    (c * x).natAbs * mass v = x.natAbs * mass (v.map fun y => c * y) := by
  rw [Int.natAbs_mul, mass_scale_int]
  calc
    c.natAbs * x.natAbs * mass v = c.natAbs * (x.natAbs * mass v) := by rw [Nat.mul_assoc]
    _ = x.natAbs * (c.natAbs * mass v) := by rw [Nat.mul_left_comm]

theorem scale_increases_mass (c : Int) (v : List Int)
    (hc : 1 < c.natAbs) (hv : 0 < mass v) :
    mass v < mass (v.map fun x => c * x) := by
  rw [mass_scale_int]
  have hsplit : c.natAbs = (c.natAbs - 1) + 1 := by omega
  rw [hsplit, Nat.add_mul, Nat.one_mul]
  have hrest : 0 < (c.natAbs - 1) * mass v := by
    have hpos : 0 < c.natAbs - 1 := by omega
    exact Nat.mul_pos hpos hv
  omega

theorem ratio_cross (c : Int) (n d : Nat) :
    (c.natAbs * n) * d = n * (c.natAbs * d) := by
  calc
    (c.natAbs * n) * d = c.natAbs * (n * d) := by rw [Nat.mul_assoc]
    _ = n * (c.natAbs * d) := by rw [Nat.mul_left_comm]

theorem sq_sub (x y : Int) :
    (x - y) * (x - y) = x * x + y * y - 2 * (x * y) := by
  grind

theorem sq_add (x y : Int) :
    (x + y) * (x + y) = x * x + y * y + 2 * (x * y) := by
  grind

theorem sumSq_sub (xs ys : List Int) (hlen : xs.length = ys.length) :
    sumSq (subL xs ys) = sumSq xs + sumSq ys - 2 * dotp xs ys := by
  induction xs generalizing ys with
  | nil =>
    cases ys with
    | nil => simp [subL, sumSq, dotp]
    | cons => simp at hlen
  | cons x xs ih =>
    cases ys with
    | nil => simp at hlen
    | cons y ys =>
      simp only [List.length_cons, Nat.succ.injEq] at hlen
      have ih' := ih ys hlen
      simp only [subL, sumSq, dotp]
      rw [sq_sub, ih']
      omega

theorem sumSq_add (xs ys : List Int) (hlen : xs.length = ys.length) :
    sumSq (addL xs ys) = sumSq xs + sumSq ys + 2 * dotp xs ys := by
  induction xs generalizing ys with
  | nil =>
    cases ys with
    | nil => simp [addL, sumSq, dotp]
    | cons => simp at hlen
  | cons x xs ih =>
    cases ys with
    | nil => simp at hlen
    | cons y ys =>
      simp only [List.length_cons, Nat.succ.injEq] at hlen
      have ih' := ih ys hlen
      simp only [addL, sumSq, dotp]
      rw [sq_add, ih']
      omega

theorem diff_of_squares (s d : Int) :
    (s - 2 * d) * (s + 2 * d) = s * s - 4 * (d * d) := by
  grind

theorem equal_norm_square (a : Int) :
    (a + a) * (a + a) = 4 * (a * a) := by
  grind

theorem trace_gap_identity (xs ys : List Int) (hlen : xs.length = ys.length)
    (hq : sumSq xs = sumSq ys) :
    sumSq (subL xs ys) * sumSq (addL xs ys)
      = 4 * (sumSq xs * sumSq ys - dotp xs ys * dotp xs ys) := by
  rw [sumSq_sub xs ys hlen, sumSq_add xs ys hlen]
  have hprod := diff_of_squares (sumSq xs + sumSq ys) (dotp xs ys)
  rw [hprod, hq]
  have hsq := equal_norm_square (sumSq ys)
  rw [hsq]
  grind

theorem not_lt_of_gt (a b e : Rat) (he : 0 ≤ e) (h : a < b) : ¬ b < a - e := by
  grind

theorem guardrail_rejects_before_primary
    (rMax eps : Rat) (cur cand : Gate)
    (_hdown : cand.phi < cur.phi - eps)
    (hbad : cand.finiteRatio = false ∨ rMax < cand.rcl) :
    admits rMax eps cur cand = false := by
  cases hbad with
  | inl hf => simp [admits, hf]
  | inr hgate =>
    cases hfin : cand.finiteRatio with
    | false => simp [admits, hfin]
    | true => simp [admits, hfin, hgate]

theorem primary_decrease_accepts
    (rMax eps : Rat) (cur cand : Gate)
    (hf : cand.finiteRatio = true) (hgate : ¬ rMax < cand.rcl)
    (hdown : cand.phi < cur.phi - eps) :
    admits rMax eps cur cand = true := by
  simp [admits, hf, hgate, hdown]

theorem primary_increase_rejects
    (rMax eps : Rat) (cur cand : Gate)
    (hf : cand.finiteRatio = true) (hgate : cand.rcl ≤ rMax)
    (heps : 0 ≤ eps) (hphi : cur.phi < cand.phi) :
    admits rMax eps cur cand = false := by
  have hnotGate : ¬ rMax < cand.rcl := by grind
  have hnotDown : ¬ cand.phi < cur.phi - eps := not_lt_of_gt cur.phi cand.phi eps heps hphi
  simp [admits, hf, hnotGate, hnotDown, hphi]

theorem secondary_increase_rejects
    (rMax eps : Rat) (cur cand : Gate)
    (hf : cand.finiteRatio = true) (hgate : ¬ rMax < cand.rcl)
    (heps : 0 ≤ eps)
    (hlo : cur.phi - eps ≤ cand.phi) (hhi : cand.phi ≤ cur.phi)
    (hgamma : cur.gamma < cand.gamma) :
    admits rMax eps cur cand = false := by
  have hnotDown : ¬ cand.phi < cur.phi - eps := by grind
  have hnotInc : ¬ cur.phi < cand.phi := by grind
  have hnotGamma : ¬ cand.gamma < cur.gamma - eps := not_lt_of_gt cur.gamma cand.gamma eps heps hgamma
  simp [admits, hf, hgate, hnotDown, hnotInc, hnotGamma, hgamma]

theorem feasible_dominates (rMax : Rat) (a b : Gate)
    (ha : feasible rMax a = true) (hb : feasible rMax b = false) :
    compareGates rMax a b = -1 := by
  simp [compareGates, ha, hb]

theorem lower_phi_preferred (rMax : Rat) (a b : Gate)
    (ha : feasible rMax a = true) (hb : feasible rMax b = true)
    (hphi : a.phi < b.phi) :
    compareGates rMax a b = -1 := by
  simp [compareGates, ha, hb, hphi]
