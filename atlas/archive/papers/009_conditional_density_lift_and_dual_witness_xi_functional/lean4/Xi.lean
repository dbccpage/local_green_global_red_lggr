/- Finite content of the conditional density lift.

The monograph's square-root trace distance is the classical name of the
normalized Cauchy gap. These theorems stay inside integer and rational arithmetic.
-/

def nsum : List Nat → Nat
  | [] => 0
  | x :: xs => x + nsum xs

def weightSum : List Nat → Rat → Rat
  | [], _ => 0
  | n :: ns, m => (n : Rat) / m + weightSum ns m

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

def term (p x : Int) : Int := (x.natAbs : Int) - p * x

def slack : List Int → List Int → Int
  | [], [] => 0
  | p :: ps, x :: xs => term p x + slack ps xs
  | _, _ => 0

def linfOk : List Int → Prop
  | [] => True
  | p :: ps => p.natAbs ≤ 1 ∧ linfOk ps

def xiIfZero (massValue : Nat) (positive : Rat) : Rat :=
  if massValue = 0 then 0 else positive

def admissible
    (phi gamma _rcl xi phi' gamma' rcl' xi' rMax eps : Rat) : Bool :=
  if phi' < phi - eps then
    true
  else if phi < phi' then
    false
  else if gamma' < gamma - eps then
    true
  else if gamma < gamma' then
    false
  else if rMax < rcl' then
    false
  else
    xi' < xi - eps

theorem natCast_mul (a b : Nat) : (a : Int) * (b : Int) = ((a * b : Nat) : Int) := by
  induction a with
  | zero => simp
  | succ a ih =>
    rw [Nat.succ_mul]
    have hcast : ((a + 1 : Nat) : Int) = (a : Int) + 1 := by simp
    rw [hcast, Int.add_mul, Int.one_mul, ih]
    simp

theorem sq_nonneg (x : Int) : 0 ≤ x * x := by
  cases x with
  | ofNat n =>
    rw [show Int.ofNat n * Int.ofNat n = (n : Int) * (n : Int) from rfl, natCast_mul]
    exact Int.natCast_nonneg _
  | negSucc n =>
    rw [Int.negSucc_eq, Int.neg_mul_neg]
    have hsum : (n : Int) + 1 = ((n + 1 : Nat) : Int) := by simp
    rw [hsum, natCast_mul]
    exact Int.natCast_nonneg _

theorem add_nonneg_pair {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) (h : a + b = 0) :
    a = 0 ∧ b = 0 := by
  omega

theorem add_div_same (a b c : Rat) (_hc : c ≠ 0) : a / c + b / c = (a + b) / c := by
  grind

theorem cast_ne_zero (m : Nat) (hm : m ≠ 0) : (m : Rat) ≠ 0 := by
  intro h
  have hnum : Rat.num ((m : Rat)) = (m : Int) := by
    cases m with
    | zero => rfl
    | succ _ => rfl
  have : (m : Int) = 0 := by
    have := congrArg Rat.num h
    rwa [hnum] at this
  omega

theorem div_self (c : Rat) (_hc : c ≠ 0) : c / c = 1 := by
  grind

theorem mass_eq_nsum (v : List Int) : mass v = nsum (v.map Int.natAbs) := by
  induction v with
  | nil => rfl
  | cons x xs ih =>
    simp [mass, nsum, ih]

theorem weight_div (xs : List Nat) (m : Nat) (hm : m ≠ 0) :
    weightSum xs (m : Rat) = ((nsum xs : Nat) : Rat) / (m : Rat) := by
  induction xs with
  | nil =>
    simp [weightSum, nsum]
    grind
  | cons n xs ih =>
    simp [weightSum, nsum, ih]
    rw [add_div_same (n : Rat) ((nsum xs : Nat) : Rat) (m : Rat) (cast_ne_zero m hm)]

theorem weights_sum_to_one (v : List Int) (hv : mass v ≠ 0) :
    weightSum (v.map Int.natAbs) (mass v : Rat) = 1 := by
  rw [weight_div (v.map Int.natAbs) (mass v) hv]
  have hsum : nsum (v.map Int.natAbs) = mass v := (mass_eq_nsum v).symm
  rw [hsum]
  exact div_self _ (cast_ne_zero _ hv)

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

theorem natAbs_nsmul (c : Nat) (x : Int) : ((c : Int) * x).natAbs = c * x.natAbs := by
  rw [Int.natAbs_mul, Int.natAbs_natCast]

theorem mass_scale (c : Nat) (v : List Int) :
    mass (v.map fun x => (c : Int) * x) = c * mass v := by
  induction v with
  | nil => simp [mass]
  | cons x xs ih =>
    simp [mass, natAbs_nsmul, ih, Nat.mul_add]

theorem weight_scale_cross (c : Nat) (x : Int) (v : List Int) :
    (c * x.natAbs) * mass v = x.natAbs * mass (v.map fun y => (c : Int) * y) := by
  rw [mass_scale]
  grind

theorem expand_gap (a b s t d : Int) :
    (a * a + s) * (b * b + t) - (a * b + d) * (a * b + d)
      = (s * t - d * d) + (a * a * t - 2 * a * b * d + s * b * b) := by
  grind

theorem cross_id (a b s t d : Int) :
    t * (a * a * t - 2 * a * b * d + s * b * b)
      = (a * t - b * d) * (a * t - b * d) + b * b * (s * t - d * d) := by
  grind

theorem sq_eq_zero {d : Int} (h : d * d = 0) : d = 0 := by
  cases d with
  | ofNat n =>
    have hcast : (n : Int) * (n : Int) = 0 := by simpa using h
    rw [natCast_mul] at hcast
    have hz : n * n = 0 := Int.ofNat.inj hcast
    cases n with
    | zero => rfl
    | succ n =>
      exact absurd hz (Nat.mul_ne_zero (Nat.succ_ne_zero n) (Nat.succ_ne_zero n))
  | negSucc n =>
    exfalso
    rw [Int.negSucc_eq, Int.neg_mul_neg] at h
    have hsum : (n : Int) + 1 = ((n + 1 : Nat) : Int) := by simp
    rw [hsum, natCast_mul] at h
    exact absurd (Int.ofNat.inj h) (Nat.mul_ne_zero (Nat.succ_ne_zero n) (Nat.succ_ne_zero n))

theorem nonneg_of_mul_pos_left {t z : Int} (ht : 0 < t) (hz : 0 ≤ t * z) : 0 ≤ z := by
  cases z with
  | ofNat n =>
    exact Int.natCast_nonneg n
  | negSucc n =>
    exfalso
    rw [Int.negSucc_eq, Int.mul_neg] at hz
    have hsum : (n : Int) + 1 = ((n + 1 : Nat) : Int) := by simp
    rw [hsum] at hz
    have h1 : 0 < ((n + 1 : Nat) : Int) := by omega
    have hpos : 0 < t * ((n + 1 : Nat) : Int) := Int.mul_pos ht h1
    omega

theorem cross_nonneg (a b s t d : Int) (hs : 0 ≤ s) (ht : 0 ≤ t)
    (hcs : 0 ≤ s * t - d * d) :
    0 ≤ (a * a + s) * (b * b + t) - (a * b + d) * (a * b + d) := by
  have hexpand := expand_gap a b s t d
  have hcross : 0 ≤ a * a * t - 2 * a * b * d + s * b * b := by
    by_cases ht0 : t = 0
    · subst ht0
      have hdnn : 0 ≤ d * d := sq_nonneg d
      have hd2 : d * d ≤ 0 := by simpa using hcs
      have hd0 : d * d = 0 := by omega
      have hd : d = 0 := sq_eq_zero hd0
      subst hd
      simp
      have hmul : 0 ≤ s * (b * b) := Int.mul_nonneg hs (sq_nonneg b)
      simpa [Int.mul_assoc] using hmul
    · have htpos : 0 < t := by omega
      have hid := cross_id a b s t d
      have hsq : 0 ≤ (a * t - b * d) * (a * t - b * d) := sq_nonneg _
      have hrest : 0 ≤ b * b * (s * t - d * d) := Int.mul_nonneg (sq_nonneg b) hcs
      have hmul : 0 ≤ t * (a * a * t - 2 * a * b * d + s * b * b) := by
        have hsum := Int.add_nonneg hsq hrest
        simpa [hid] using hsum
      exact nonneg_of_mul_pos_left htpos hmul
  rw [hexpand]
  exact Int.add_nonneg hcs hcross

theorem sumSq_nonneg : ∀ xs : List Int, 0 ≤ sumSq xs
  | [] => by decide
  | x :: xs => Int.add_nonneg (sq_nonneg x) (sumSq_nonneg xs)

theorem cauchy_gap_nonneg (xs ys : List Int) (hlen : xs.length = ys.length) :
    0 ≤ sumSq xs * sumSq ys - dotp xs ys * dotp xs ys := by
  induction xs generalizing ys with
  | nil =>
    cases ys with
    | nil =>
      simp [sumSq, dotp]
    | cons _ _ =>
      simp at hlen
  | cons x xs ih =>
    cases ys with
    | nil =>
      simp at hlen
    | cons y ys =>
      have hlen' : xs.length = ys.length := by
        simp at hlen
        exact hlen
      exact cross_nonneg x y (sumSq xs) (sumSq ys) (dotp xs ys)
        (sumSq_nonneg xs) (sumSq_nonneg ys) (ih ys hlen')

theorem trichotomy_unit (p : Int) (hp : p.natAbs ≤ 1) : p = -1 ∨ p = 0 ∨ p = 1 := by
  cases p with
  | ofNat n =>
    cases n with
    | zero => exact Or.inr (Or.inl rfl)
    | succ n =>
      cases n with
      | zero => exact Or.inr (Or.inr rfl)
      | succ n =>
        simp [Int.natAbs] at hp
  | negSucc n =>
    cases n with
    | zero =>
      exact Or.inl rfl
    | succ n =>
      simp [Int.natAbs] at hp

theorem term_nonneg (p x : Int) (hp : p.natAbs ≤ 1) : 0 ≤ term p x := by
  rcases trichotomy_unit p hp with rfl | rfl | rfl
  · cases x with
    | ofNat n =>
      simp [term, Int.natAbs]
      exact Int.add_nonneg (Int.natCast_nonneg n) (Int.natCast_nonneg n)
    | negSucc n =>
      simp [term, Int.natAbs, Int.negSucc_eq]
  · simp [term]
  · cases x with
    | ofNat n =>
      simp [term, Int.natAbs]
    | negSucc n =>
      simp [term, Int.natAbs, Int.negSucc_eq]
      exact Int.add_nonneg
        (Int.add_nonneg (Int.natCast_nonneg n) (Int.natCast_nonneg 1))
        (Int.add_nonneg (Int.natCast_nonneg n) (Int.natCast_nonneg 1))

theorem slack_nonneg : ∀ phi h : List Int, phi.length = h.length → linfOk phi → 0 ≤ slack phi h
  | [], [], _, _ => by decide
  | p :: ps, x :: xs, hlen, hlinf => by
    have hlen' : ps.length = xs.length := by
      simp at hlen
      exact hlen
    have hterm : 0 ≤ term p x := term_nonneg p x hlinf.1
    have htail : 0 ≤ slack ps xs := slack_nonneg ps xs hlen' hlinf.2
    exact Int.add_nonneg hterm htail
  | [], _ :: _, hlen, _ => by simp at hlen
  | _ :: _, [], hlen, _ => by simp at hlen

theorem forced_sign (p x : Int) (hp : p.natAbs ≤ 1) (hterm : term p x = 0) (hx : x ≠ 0) :
    p = (if x < 0 then -1 else 1) := by
  rcases trichotomy_unit p hp with hp | hp | hp
  · subst hp
    cases x with
    | ofNat n =>
      cases n with
      | zero =>
        exact absurd rfl hx
      | succ n =>
        simp [term, Int.natAbs] at hterm
        omega
    | negSucc n =>
      have hxlt : Int.negSucc n < 0 := by
        rw [Int.negSucc_eq]
        omega
      simp [hxlt]
  · subst hp
    cases x with
    | ofNat n =>
      have hz : n = 0 := by simpa [term, Int.natAbs] using hterm
      cases n with
      | zero =>
        exact absurd rfl hx
      | succ n =>
        simp at hz
    | negSucc n =>
      have hz : (n : Int) + 1 = 0 := by simpa [term, Int.natAbs] using hterm
      have hcast : ((n + 1 : Nat) : Int) = (n : Int) + 1 := by simp
      rw [← hcast] at hz
      exact absurd (Int.ofNat.inj hz) (Nat.succ_ne_zero n)
  · subst hp
    cases x with
    | ofNat n =>
      cases n with
      | zero =>
        exact absurd rfl hx
      | succ n =>
        rfl
    | negSucc n =>
      simp [term, Int.natAbs, Int.negSucc_eq] at hterm
      omega

theorem dual_mass_at_least_one (phi h : List Int) (hlen : phi.length = h.length)
    (hlinf : linfOk phi) (hslack : slack phi h = 0) (hpos : 0 < mass h) :
    1 ≤ mass phi := by
  induction h generalizing phi with
  | nil =>
    simp [mass] at hpos
  | cons x xs ih =>
    cases phi with
    | nil =>
      simp at hlen
    | cons p ps =>
      have hlen' : ps.length = xs.length := by
        simp at hlen
        exact hlen
      have hlinf' : linfOk ps := hlinf.2
      have hterm : 0 ≤ term p x := term_nonneg p x hlinf.1
      have htail : 0 ≤ slack ps xs := slack_nonneg ps xs hlen' hlinf'
      have hzero : term p x = 0 ∧ slack ps xs = 0 := by
        have : term p x + slack ps xs = 0 := by simpa [slack] using hslack
        exact add_nonneg_pair hterm htail this
      have hmass : mass (x :: xs) = x.natAbs + mass xs := by simp [mass]
      by_cases hx : x = 0
      · subst hx
        have hpos' : 0 < mass xs := by
          simp [mass] at hpos
          exact hpos
        have htailMass : 1 ≤ mass ps := ih ps hlen' hlinf' hzero.2 hpos'
        have : mass (p :: ps) = p.natAbs + mass ps := by simp [mass]
        omega
      · have hsign := forced_sign p x hlinf.1 hzero.1 hx
        have habs : p.natAbs = 1 := by
          by_cases hneg : x < 0
          · simp [hneg] at hsign
            simp [hsign]
          · simp [hneg] at hsign
            simp [hsign]
        simp [mass, habs]

theorem zero_mass_convention (positive : Rat) : xiIfZero 0 positive = 0 := by
  simp [xiIfZero]

theorem not_lt_of_gt (a b e : Rat) (he : 0 ≤ e) (h : a < b) : ¬ b < a - e := by
  grind

theorem primary_decrease_accepts
    (phi gamma rcl xi phi' gamma' rcl' xi' rMax eps : Rat)
    (h : phi' < phi - eps) :
    admissible phi gamma rcl xi phi' gamma' rcl' xi' rMax eps = true := by
  simp [admissible, h]

theorem primary_increase_rejects
    (phi gamma rcl xi phi' gamma' rcl' xi' rMax eps : Rat)
    (heps : 0 ≤ eps) (hphi : phi < phi') :
    admissible phi gamma rcl xi phi' gamma' rcl' xi' rMax eps = false := by
  have hnot : ¬ phi' < phi - eps := not_lt_of_gt phi phi' eps heps hphi
  simp [admissible, hnot, hphi]

theorem secondary_increase_rejects
    (phi gamma rcl xi phi' gamma' rcl' xi' rMax eps : Rat)
    (heps : 0 ≤ eps) (hlo : phi - eps ≤ phi') (hhi : phi' ≤ phi) (hgamma : gamma < gamma') :
    admissible phi gamma rcl xi phi' gamma' rcl' xi' rMax eps = false := by
  have hnotPhi : ¬ phi' < phi - eps := by grind
  have hnotInc : ¬ phi < phi' := by grind
  have hnotGamma : ¬ gamma' < gamma - eps := not_lt_of_gt gamma gamma' eps heps hgamma
  simp [admissible, hnotPhi, hnotInc, hnotGamma, hgamma]

theorem guardrail_rejects
    (phi gamma rcl xi phi' gamma' rcl' xi' rMax eps : Rat)
    (_heps : 0 ≤ eps) (hlo : phi - eps ≤ phi') (hhi : phi' ≤ phi)
    (hglo : gamma - eps ≤ gamma') (hghi : gamma' ≤ gamma) (hgate : rMax < rcl') :
    admissible phi gamma rcl xi phi' gamma' rcl' xi' rMax eps = false := by
  have hnotPhi : ¬ phi' < phi - eps := by grind
  have hnotInc : ¬ phi < phi' := by grind
  have hnotGamma : ¬ gamma' < gamma - eps := by grind
  have hnotGinc : ¬ gamma < gamma' := by grind
  simp [admissible, hnotPhi, hnotInc, hnotGamma, hnotGinc, hgate]
