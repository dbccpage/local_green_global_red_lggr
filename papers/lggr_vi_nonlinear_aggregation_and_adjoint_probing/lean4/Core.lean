import Init.Data.Rat.Lemmas
import Init.Grind.Ordered.Ring

/- Finite observation invariance, rational Gram kernel, and sign-cube probes. -/

namespace LGGRVI

/-- Equal observations remain equal after any deterministic post-processing. -/
theorem postprocessing_invariance
    {State Observation Verdict : Type}
    (observe : State → Observation)
    (postprocess : Observation → Verdict)
    {left right : State}
    (h : observe left = observe right) :
    postprocess (observe left) = postprocess (observe right) := by
  exact congrArg postprocess h

/-- A zero-preserving verdict map accepts every state observationally
    equivalent to the declared zero state. -/
theorem zero_preserving_accepts_hidden
    {State Observation Verdict : Type}
    (observe : State → Observation)
    (postprocess : Observation → Verdict)
    (zeroState : State)
    (green : Verdict)
    {state : State}
    (hzero : postprocess (observe zeroState) = green)
    (hhidden : observe state = observe zeroState) :
    postprocess (observe state) = green := by
  rw [hhidden]
  exact hzero

/-- An abstract measurement/adjoint pair with the one identity required by
    the probing argument. The identity is an explicit hypothesis, not a
    theorem about arbitrary functions. -/
structure GramSystem (V W : Type) [Zero V] [Zero W] where
  measure : V → W
  adjoint : W → V
  gramKernel : ∀ v, adjoint (measure v) = 0 ↔ measure v = 0

variable {V W : Type} [Zero V] [Zero W]

def GramSystem.gram (system : GramSystem V W) (v : V) : V :=
  system.adjoint (system.measure v)

/-- Under `gramKernel`, the Gram response vanishes exactly on hidden states. -/
theorem gram_zero_iff_hidden (system : GramSystem V W) (v : V) :
    system.gram v = 0 ↔ system.measure v = 0 := by
  exact system.gramKernel v

/-- A detectable state has a nonzero Gram response. -/
theorem detectable_has_nonzero_gram
    (system : GramSystem V W)
    (v : V)
    (hvisible : system.measure v ≠ 0) :
    system.gram v ≠ 0 := by
  intro hzero
  exact hvisible ((gram_zero_iff_hidden system v).mp hzero)

/- Rational matrices. Square roots and singular values are not used. -/

abbrev Vec (n : Nat) := Fin n → Rat
abbrev Mat (r c : Nat) := Fin r → Fin c → Rat

def vsum : {n : Nat} → (Fin n → Rat) → Rat
  | 0, _ => 0
  | n + 1, f => f (Fin.last n) + vsum (fun i : Fin n => f i.castSucc)

@[simp] theorem vsum_succ {n : Nat} (f : Fin (n + 1) → Rat) :
    vsum f = f (Fin.last n) + vsum (fun i => f i.castSucc) := rfl

theorem vsum_congr : ∀ {n : Nat} {f g : Fin n → Rat}, (∀ i, f i = g i) → vsum f = vsum g
  | 0, _, _, _ => rfl
  | n + 1, f, g, h => by
    rw [vsum_succ, vsum_succ, h (Fin.last n), vsum_congr (fun i => h i.castSucc)]

theorem vsum_zeros : ∀ {n : Nat}, vsum (fun _ : Fin n => (0 : Rat)) = 0
  | 0 => rfl
  | n + 1 => by
    rw [vsum_succ, vsum_zeros, Rat.add_zero]

theorem vsum_add :
    ∀ {n : Nat} (f g : Fin n → Rat), vsum (fun i => f i + g i) = vsum f + vsum g
  | 0, _, _ => (Rat.zero_add (0 : Rat)).symm
  | n + 1, f, g => by
    rw [vsum_succ, vsum_succ, vsum_succ,
      vsum_add (fun i => f i.castSucc) (fun i => g i.castSucc)]
    grind

theorem vsum_mul_left :
    ∀ {n : Nat} (c : Rat) (f : Fin n → Rat), vsum (fun i => c * f i) = c * vsum f
  | 0, c, _ => by
    change (0 : Rat) = c * 0
    exact (Rat.mul_zero c).symm
  | n + 1, c, f => by
    rw [vsum_succ, vsum_succ, vsum_mul_left c (fun i => f i.castSucc)]
    grind

theorem vsum_mul_right :
    ∀ {n : Nat} (f : Fin n → Rat) (c : Rat), vsum (fun i => f i * c) = vsum f * c
  | 0, _, c => by
    change (0 : Rat) = 0 * c
    exact (Rat.zero_mul c).symm
  | n + 1, f, c => by
    rw [vsum_succ, vsum_succ, vsum_mul_right (fun i => f i.castSucc) c]
    grind

theorem vsum_swap :
    ∀ {m n : Nat} (f : Fin m → Fin n → Rat),
      vsum (fun i => vsum (fun j => f i j)) = vsum (fun j => vsum (fun i => f i j))
  | 0, _, f => by
    change (0 : Rat) = vsum (fun j => vsum (fun i : Fin 0 => f i j))
    have hinner : ∀ j, vsum (fun i : Fin 0 => f i j) = 0 := fun _ => rfl
    rw [vsum_congr hinner, vsum_zeros]
  | m + 1, _, f => by
    rw [vsum_succ]
    rw [vsum_swap (fun i j => f i.castSucc j)]
    rw [← vsum_add]
    exact vsum_congr (fun j => (vsum_succ (fun i => f i j)).symm)

def dot {n : Nat} (x y : Vec n) : Rat := vsum (fun i => x i * y i)

def mulVec {r c : Nat} (matrix : Mat r c) (x : Vec c) : Vec r :=
  fun i => dot (matrix i) x

def gram {r c : Nat} (matrix : Mat r c) : Mat c c :=
  fun i j => vsum (fun k => matrix k i * matrix k j)

def applyGram {r c : Nat} (matrix : Mat r c) (x : Vec c) : Vec c :=
  fun i => dot (gram matrix i) x

def addVec {n : Nat} (x y : Vec n) : Vec n := fun i => x i + y i

def smulVec {n : Nat} (c : Rat) (x : Vec n) : Vec n := fun i => c * x i

def subVec {n : Nat} (x y : Vec n) : Vec n := fun i => x i - y i

theorem nonneg_neg_of_nonpos {a : Rat} (ha : a ≤ 0) : 0 ≤ -a := by
  rw [← Rat.neg_zero] at ha
  exact (Rat.le_neg_iff).mp ha

theorem rat_sq_nonneg (a : Rat) : 0 ≤ a * a := by
  by_cases h : 0 ≤ a
  · exact Rat.mul_nonneg h h
  · have ha : a ≤ 0 := Rat.le_of_lt (Rat.not_le.mp h)
    have heq : a * a = (-a) * (-a) := by grind
    rw [heq]
    exact Rat.mul_nonneg (nonneg_neg_of_nonpos ha) (nonneg_neg_of_nonpos ha)

theorem mul_self_eq_zero {a : Rat} (h : a * a = 0) : a = 0 :=
  (Rat.mul_eq_zero.mp h).elim id id

theorem add_nonneg_eq_zero {a b : Rat} (ha : 0 ≤ a) (hb : 0 ≤ b) (h : a + b = 0) :
    a = 0 ∧ b = 0 := by
  have hb' : b = -a := by
    calc
      b = 0 + b := (Rat.zero_add b).symm
      _ = (-a + a) + b := by rw [Rat.neg_add_cancel]
      _ = -a + (a + b) := by grind
      _ = -a + 0 := by rw [h]
      _ = -a := Rat.add_zero _
  have ha0 : a ≤ 0 := by
    have hnb : -(0 : Rat) ≤ -a := by simpa [Rat.neg_zero, hb'] using hb
    exact (Rat.neg_le_neg_iff).mp hnb
  have ha0' : a = 0 := Rat.le_antisymm ha0 ha
  exact ⟨ha0', by simpa [ha0', Rat.neg_zero] using hb'⟩

theorem vsum_nonneg :
    ∀ {n : Nat} (f : Fin n → Rat), (∀ i, 0 ≤ f i) → 0 ≤ vsum f
  | 0, _, _ => Rat.le_refl
  | n + 1, f, hf => by
    rw [vsum_succ]
    exact Rat.add_nonneg (hf _) (vsum_nonneg _ (fun i => hf i.castSucc))

theorem vsum_sq_nonneg {n : Nat} (f : Fin n → Rat) : 0 ≤ vsum (fun i => f i * f i) :=
  vsum_nonneg _ (fun i => rat_sq_nonneg (f i))

theorem vsum_sq_eq_zero :
    ∀ {n : Nat} (f : Fin n → Rat), vsum (fun i => f i * f i) = 0 → ∀ i, f i = 0
  | 0, _, _ => fun i => Fin.elim0 i
  | n + 1, f, h => by
    have hsplit :
        f (Fin.last n) * f (Fin.last n) +
          vsum (fun i : Fin n => f i.castSucc * f i.castSucc) = 0 := by
      simpa [vsum_succ] using h
    have hparts :=
      add_nonneg_eq_zero (rat_sq_nonneg _) (vsum_sq_nonneg _) hsplit
    have hprefix := vsum_sq_eq_zero _ hparts.2
    intro i
    rcases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ i.isLt) with hlt | heq
    · have i_eq : i = (Fin.castLT i hlt).castSucc := (Fin.castSucc_castLT i hlt).symm
      rw [i_eq]
      exact hprefix _
    · have i_eq : i = Fin.last n := Fin.eq_of_val_eq (by simp [Fin.val_last, heq])
      rw [i_eq]
      exact mul_self_eq_zero hparts.1

theorem dot_zero_right {n : Nat} (x : Vec n) : dot x (fun _ => 0) = 0 := by
  unfold dot
  have hterm : ∀ i, x i * (0 : Rat) = 0 := fun i => Rat.mul_zero (x i)
  rw [vsum_congr hterm, vsum_zeros]

theorem dot_add_left {n : Nat} (x y z : Vec n) :
    dot (addVec x y) z = dot x z + dot y z := by
  unfold dot addVec
  have hterm : ∀ i, (x i + y i) * z i = x i * z i + y i * z i := fun _ => by grind
  rw [vsum_congr hterm, vsum_add]

theorem dot_add_right {n : Nat} (x y z : Vec n) :
    dot x (addVec y z) = dot x y + dot x z := by
  unfold dot addVec
  have hterm : ∀ i, x i * (y i + z i) = x i * y i + x i * z i := fun _ => by grind
  rw [vsum_congr hterm, vsum_add]

theorem dot_smul_right {n : Nat} (c : Rat) (x y : Vec n) :
    dot x (smulVec c y) = c * dot x y := by
  unfold dot smulVec
  have hterm : ∀ i, x i * (c * y i) = c * (x i * y i) := fun _ => by grind
  rw [vsum_congr hterm, vsum_mul_left]

theorem dot_smul_left {n : Nat} (c : Rat) (x y : Vec n) :
    dot (smulVec c x) y = c * dot x y := by
  unfold dot smulVec
  have hterm : ∀ i, c * x i * y i = c * (x i * y i) := fun _ => by grind
  rw [vsum_congr hterm, vsum_mul_left]

theorem gram_comm {r c : Nat} (matrix : Mat r c) (i j : Fin c) :
    gram matrix i j = gram matrix j i := by
  unfold gram
  refine vsum_congr ?_
  intro k
  grind

theorem applyGram_coord {r c : Nat} (matrix : Mat r c) (x : Vec c) (i : Fin c) :
    applyGram matrix x i = vsum (fun k => matrix k i * mulVec matrix x k) := by
  unfold applyGram dot gram mulVec
  have hpull :
      vsum (fun j => (vsum (fun k => matrix k i * matrix k j)) * x j) =
        vsum (fun j => vsum (fun k => (matrix k i * matrix k j) * x j)) := by
    refine vsum_congr ?_
    intro j
    exact (vsum_mul_right (fun k => matrix k i * matrix k j) (x j)).symm
  rw [hpull, vsum_swap]
  refine vsum_congr ?_
  intro k
  unfold dot
  rw [← vsum_mul_left]
  refine vsum_congr ?_
  intro j
  exact Rat.mul_assoc (matrix k i) (matrix k j) (x j)

theorem dot_apply_eq_obs {r c : Nat} (matrix : Mat r c) (x : Vec c) :
    dot x (applyGram matrix x) = dot (mulVec matrix x) (mulVec matrix x) := by
  unfold dot
  have hcoord : ∀ i, x i * applyGram matrix x i =
      x i * vsum (fun k => matrix k i * mulVec matrix x k) := by
    intro i
    exact congrArg (fun t => x i * t) (applyGram_coord matrix x i)
  rw [vsum_congr hcoord]
  have hpull :
      vsum (fun i => x i * vsum (fun k => matrix k i * mulVec matrix x k)) =
        vsum (fun i => vsum (fun k => x i * (matrix k i * mulVec matrix x k))) := by
    refine vsum_congr ?_
    intro i
    exact (vsum_mul_left (x i) _).symm
  rw [hpull, vsum_swap]
  refine vsum_congr ?_
  intro k
  unfold mulVec dot
  rw [← vsum_mul_right]
  refine vsum_congr ?_
  intro i
  exact calc
    x i * (matrix k i * mulVec matrix x k)
        = (x i * matrix k i) * mulVec matrix x k := (Rat.mul_assoc (x i) (matrix k i) _).symm
    _ = (matrix k i * x i) * mulVec matrix x k := by rw [Rat.mul_comm (x i) (matrix k i)]

theorem gram_kernel_iff {r c : Nat} (matrix : Mat r c) (x : Vec c) :
    applyGram matrix x = (fun _ => (0 : Rat)) ↔ mulVec matrix x = (fun _ => (0 : Rat)) := by
  constructor
  · intro hhidden
    have hsq : dot (mulVec matrix x) (mulVec matrix x) = 0 := by
      rw [← dot_apply_eq_obs, hhidden, dot_zero_right]
    have hcoords := vsum_sq_eq_zero (mulVec matrix x) (by
      unfold dot at hsq
      exact hsq)
    funext i
    exact hcoords i
  · intro hhidden
    funext i
    rw [applyGram_coord]
    have hterm : ∀ k, matrix k i * mulVec matrix x k = 0 := by
      intro k
      rw [congrFun hhidden k, Rat.mul_zero]
    rw [vsum_congr hterm, vsum_zeros]

theorem gram_detectable_iff {r c : Nat} (matrix : Mat r c) (x : Vec c) :
    applyGram matrix x ≠ (fun _ => (0 : Rat)) ↔ mulVec matrix x ≠ (fun _ => (0 : Rat)) := by
  constructor
  · intro hseen hhidden
    exact hseen ((gram_kernel_iff matrix x).mpr hhidden)
  · intro hseen hhidden
    exact hseen ((gram_kernel_iff matrix x).mp hhidden)

def quad {n : Nat} (rows : Mat n n) (x : Vec n) : Rat :=
  dot x (fun i => dot (rows i) x)

theorem dot_sym_comm {n : Nat} (rows : Mat n n)
    (hsym : ∀ i j, rows i j = rows j i) (x s : Vec n) :
    dot x (fun i => dot (rows i) s) = dot s (fun i => dot (rows i) x) := by
  unfold dot
  have hpull :
      vsum (fun i => x i * vsum (fun j => rows i j * s j)) =
        vsum (fun i => vsum (fun j => x i * (rows i j * s j))) := by
    refine vsum_congr ?_
    intro i
    exact (vsum_mul_left (x i) (fun j => rows i j * s j)).symm
  rw [hpull, vsum_swap]
  refine vsum_congr ?_
  intro j
  change vsum (fun i => x i * (rows i j * s j)) = s j * vsum (fun i => rows j i * x i)
  have hterm : ∀ i, x i * (rows i j * s j) = s j * (rows j i * x i) := by
    intro i
    have hrow : rows i j = rows j i := hsym i j
    grind
  rw [vsum_congr hterm, vsum_mul_left]

theorem quad_expand {n : Nat} (rows : Mat n n)
    (hsym : ∀ i j, rows i j = rows j i) (x s : Vec n) :
    quad rows (addVec x s) =
      quad rows x + dot x (fun i => dot (rows i) s) +
        dot s (fun i => dot (rows i) x) + quad rows s := by
  unfold quad
  have hmul : (fun i => dot (rows i) (addVec x s)) =
      addVec (fun i => dot (rows i) x) (fun i => dot (rows i) s) := by
    funext i
    exact dot_add_right (rows i) x s
  have hcross := dot_sym_comm rows hsym x s
  rw [hmul, dot_add_left, dot_add_right, dot_add_right, hcross]
  grind

def energy {r c : Nat} (matrix : Mat r c) (x : Vec c) : Rat :=
  (1 / 2) * quad (gram matrix) (x)

theorem energy_centered_cleared {r c : Nat} (matrix : Mat r c) (x d : Vec c) (step : Rat) :
    quad (gram matrix) (addVec x (smulVec step d)) -
        quad (gram matrix) (subVec x (smulVec step d)) =
      (4 * step) * dot d (applyGram matrix x) := by
  have hsym : ∀ i j, gram matrix i j = gram matrix j i := fun i j => gram_comm matrix i j
  have hadd := quad_expand (gram matrix) hsym x (smulVec step d)
  have hsubvec : subVec x (smulVec step d) = addVec x (smulVec (-step) d) := by
    funext i
    unfold subVec addVec smulVec
    grind
  have hsub := quad_expand (gram matrix) hsym x (smulVec (-step) d)
  have hsmul_quad : ∀ c, quad (gram matrix) (smulVec c d) = (c * c) * quad (gram matrix) d := by
    intro c
    unfold quad
    rw [dot_smul_left]
    have hrow : (fun i => dot (gram matrix i) (smulVec c d)) =
        smulVec c (fun i => dot (gram matrix i) d) := by
      funext i
      exact dot_smul_right c (gram matrix i) d
    rw [hrow, dot_smul_right]
    grind
  have hcross : dot (smulVec step d) (fun i => dot (gram matrix i) x) =
      step * dot d (applyGram matrix x) := by
    rw [dot_smul_left]
    rfl
  have hcross_neg : dot (smulVec (-step) d) (fun i => dot (gram matrix i) x) =
      (-step) * dot d (applyGram matrix x) := by
    rw [dot_smul_left]
    rfl
  have hx_cross : dot x (fun i => dot (gram matrix i) (smulVec step d)) =
      step * dot d (applyGram matrix x) := by
    have hfun : (fun i => dot (gram matrix i) (smulVec step d)) =
        smulVec step (applyGram matrix d) := by
      funext i
      unfold applyGram
      exact dot_smul_right step (gram matrix i) d
    rw [hfun, dot_smul_right]
    unfold applyGram
    rw [dot_sym_comm (gram matrix) hsym x d]
  have hx_cross_neg : dot x (fun i => dot (gram matrix i) (smulVec (-step) d)) =
      (-step) * dot d (applyGram matrix x) := by
    have hfun : (fun i => dot (gram matrix i) (smulVec (-step) d)) =
        smulVec (-step) (applyGram matrix d) := by
      funext i
      unfold applyGram
      exact dot_smul_right (-step) (gram matrix i) d
    rw [hfun, dot_smul_right]
    unfold applyGram
    rw [dot_sym_comm (gram matrix) hsym x d]
  rw [hadd, hsubvec, hsub, hsmul_quad, hsmul_quad, hcross, hcross_neg, hx_cross, hx_cross_neg]
  grind

theorem centered_directional_identity
    {r c : Nat} (matrix : Mat r c) (x d : Vec c) {step : Rat} (hstep : step ≠ 0) :
    (energy matrix (addVec x (smulVec step d)) -
        energy matrix (subVec x (smulVec step d))) / (2 * step) =
      dot d (applyGram matrix x) := by
  unfold energy
  have htwo : (2 : Rat) ≠ 0 := by decide
  have hden : 2 * step ≠ 0 := by
    intro h
    rcases (Rat.mul_eq_zero.mp h) with h2 | hs
    · exact htwo h2
    · exact hstep hs
  have hdiff :
      (1 / 2) * quad (gram matrix) (addVec x (smulVec step d)) -
          (1 / 2) * quad (gram matrix) (subVec x (smulVec step d)) =
        (1 / 2) * (quad (gram matrix) (addVec x (smulVec step d)) -
          quad (gram matrix) (subVec x (smulVec step d))) := by
    grind
  rw [hdiff, energy_centered_cleared]
  have hscale :
      (1 / 2) * ((4 * step) * dot d (applyGram matrix x)) =
        (2 * step) * dot d (applyGram matrix x) := by
    grind
  rw [hscale, Rat.div_def, Rat.mul_comm (2 * step) (dot d (applyGram matrix x)),
    Rat.mul_assoc, Rat.mul_inv_cancel _ hden, Rat.mul_one]

def extendSign {n : Nat} (prefixSign : Vec n) (bit : Rat) : Vec (n + 1) :=
  fun i => Fin.lastCases bit prefixSign i

def signSum : {n : Nat} → (Vec n → Rat) → Rat
  | 0, g => g (fun i => Fin.elim0 i)
  | _ + 1, g =>
      signSum (fun prefixSign => g (extendSign prefixSign 1)) +
        signSum (fun prefixSign => g (extendSign prefixSign (-1)))

def twoPow : Nat → Rat
  | 0 => 1
  | n + 1 => twoPow n + twoPow n

theorem twoPow_nonneg : ∀ n : Nat, 0 ≤ twoPow n
  | 0 => Rat.le_refl
  | n + 1 => by
    rw [twoPow]
    exact Rat.add_nonneg (twoPow_nonneg n) (twoPow_nonneg n)

theorem twoPow_ne_zero : ∀ n : Nat, twoPow n ≠ 0
  | 0 => by decide
  | n + 1 => by
    intro h
    rw [twoPow] at h
    exact twoPow_ne_zero n (add_nonneg_eq_zero (twoPow_nonneg n) (twoPow_nonneg n) h).1

theorem signSum_zero : ∀ {n : Nat}, signSum (fun _ : Vec n => (0 : Rat)) = 0
  | 0 => rfl
  | _ + 1 => by
    rw [signSum, signSum_zero]
    exact Rat.add_zero (0 : Rat)

theorem signSum_congr :
    ∀ {n : Nat} {g h : Vec n → Rat}, (∀ sign, g sign = h sign) → signSum g = signSum h
  | 0, _, _, h => h _
  | n + 1, _, _, heq => by
    rw [signSum, signSum]
    rw [signSum_congr (fun prefixSign => heq (extendSign prefixSign 1))]
    rw [signSum_congr (fun prefixSign => heq (extendSign prefixSign (-1)))]

theorem signSum_add :
    ∀ {n : Nat} (g h : Vec n → Rat),
      signSum (fun sign => g sign + h sign) = signSum g + signSum h
  | 0, g, h => by
    change g (fun i => Fin.elim0 i) + h (fun i => Fin.elim0 i) =
      g (fun i => Fin.elim0 i) + h (fun i => Fin.elim0 i)
    rfl
  | n + 1, g, h => by
    rw [signSum, signSum, signSum]
    rw [signSum_add (fun prefixSign => g (extendSign prefixSign 1))
      (fun prefixSign => h (extendSign prefixSign 1))]
    rw [signSum_add (fun prefixSign => g (extendSign prefixSign (-1)))
      (fun prefixSign => h (extendSign prefixSign (-1)))]
    grind

theorem signSum_mul_left :
    ∀ {n : Nat} (c : Rat) (g : Vec n → Rat), signSum (fun δ => c * g δ) = c * signSum g
  | 0, _, _ => rfl
  | n + 1, c, g => by
    rw [signSum, signSum]
    rw [signSum_mul_left c (fun prefixSign => g (extendSign prefixSign 1))]
    rw [signSum_mul_left c (fun prefixSign => g (extendSign prefixSign (-1)))]
    grind

theorem signSum_const : ∀ {n : Nat}, signSum (fun _ : Vec n => (1 : Rat)) = twoPow n
  | 0 => rfl
  | n + 1 => by
    rw [signSum, twoPow, signSum_const]

theorem signSum_coordinate : ∀ {n : Nat} (i : Fin n), signSum (fun sign : Vec n => sign i) = 0
  | n + 1, i => by
    rw [signSum]
    rcases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ i.isLt) with hlt | heq
    · have i_eq : i = (Fin.castLT i hlt).castSucc := (Fin.castSucc_castLT i hlt).symm
      rw [i_eq]
      simp only [extendSign, Fin.lastCases_castSucc]
      rw [signSum_coordinate]
      exact Rat.add_zero (0 : Rat)
    · have i_eq : i = Fin.last n := Fin.eq_of_val_eq (by simp [Fin.val_last, heq])
      rw [i_eq]
      simp only [extendSign, Fin.lastCases_last]
      have hneg : signSum (fun _ : Vec n => (-1 : Rat)) = (-1) * twoPow n := by
        have hfun : (fun _ : Vec n => (-1 : Rat)) = (fun _ => (-1) * (1 : Rat)) := by
          funext
          grind
        rw [hfun, signSum_mul_left, signSum_const]
      rw [signSum_const, hneg]
      grind

theorem castSucc_ne_last {n : Nat} (j : Fin n) : j.castSucc ≠ Fin.last n := by
  intro hsame
  have hval : (j : Nat) = n := by
    simpa [Fin.val_castSucc, Fin.val_last] using congrArg Fin.val hsame
  exact absurd hval (Nat.ne_of_lt j.isLt)

theorem signSum_product :
    ∀ {n : Nat} (i j : Fin n),
      signSum (fun δ : Vec n => δ i * δ j) = if i = j then twoPow n else 0
  | n + 1, i, j => by
    rw [signSum]
    rcases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ i.isLt) with hi | hi
    · rcases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ j.isLt) with hj | hj
      · have i_eq : i = (Fin.castLT i hi).castSucc := (Fin.castSucc_castLT i hi).symm
        have j_eq : j = (Fin.castLT j hj).castSucc := (Fin.castSucc_castLT j hj).symm
        rw [i_eq, j_eq]
        simp only [extendSign, Fin.lastCases_castSucc]
        rw [signSum_product]
        by_cases hidx : Fin.castLT i hi = Fin.castLT j hj
        · have hij : i = j := by
            rw [i_eq, j_eq, hidx]
          simp [hij, twoPow]
        · have hcast : (Fin.castLT i hi).castSucc ≠ (Fin.castLT j hj).castSucc := by
            intro hsame
            exact hidx (Fin.castSucc_inj.mp hsame)
          rw [ite_eq_right hcast, ite_eq_right hidx]
          exact Rat.add_zero (0 : Rat)
      · have i_eq : i = (Fin.castLT i hi).castSucc := (Fin.castSucc_castLT i hi).symm
        have j_eq : j = Fin.last n := Fin.eq_of_val_eq (by simp [Fin.val_last, hj])
        have hne : (Fin.castLT i hi).castSucc ≠ Fin.last n :=
          castSucc_ne_last (Fin.castLT i hi)
        rw [i_eq, j_eq, ite_eq_right hne]
        simp only [extendSign, Fin.lastCases_castSucc, Fin.lastCases_last]
        have hone : signSum (fun prefixSign => prefixSign (Fin.castLT i hi) * (1 : Rat)) =
            signSum (fun prefixSign => prefixSign (Fin.castLT i hi)) := by
          refine signSum_congr ?_
          intro prefixSign
          grind
        have hneg : signSum (fun prefixSign => prefixSign (Fin.castLT i hi) * (-1)) =
            (-1) * signSum (fun prefixSign => prefixSign (Fin.castLT i hi)) := by
          have hfun : (fun prefixSign : Vec n => prefixSign (Fin.castLT i hi) * (-1)) =
              (fun prefixSign => (-1) * prefixSign (Fin.castLT i hi)) := by
            funext prefixSign
            grind
          rw [hfun, signSum_mul_left]
        rw [hone, hneg, signSum_coordinate]
        grind
    · have i_eq : i = Fin.last n := Fin.eq_of_val_eq (by simp [Fin.val_last, hi])
      rw [i_eq]
      rcases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ j.isLt) with hj | hj
      · have j_eq : j = (Fin.castLT j hj).castSucc := (Fin.castSucc_castLT j hj).symm
        have hne : Fin.last n ≠ (Fin.castLT j hj).castSucc :=
          (castSucc_ne_last (Fin.castLT j hj)).symm
        rw [j_eq, ite_eq_right hne]
        simp only [extendSign, Fin.lastCases_last, Fin.lastCases_castSucc]
        have hone : signSum (fun prefixSign => (1 : Rat) * prefixSign (Fin.castLT j hj)) =
            signSum (fun prefixSign => prefixSign (Fin.castLT j hj)) := by
          refine signSum_congr ?_
          intro prefixSign
          grind
        rw [hone, signSum_mul_left, signSum_coordinate]
        grind
      · have j_eq : j = Fin.last n := Fin.eq_of_val_eq (by simp [Fin.val_last, hj])
        rw [j_eq]
        simp only [extendSign, Fin.lastCases_last]
        rw [ite_true, twoPow]
        have hone : signSum (fun _ : Vec n => (1 : Rat) * 1) = twoPow n := by
          have hfun : (fun _ : Vec n => (1 : Rat) * (1 : Rat)) = (fun _ => (1 : Rat)) := by
            funext
            grind
          rw [hfun, signSum_const]
        have hneg : signSum (fun _ : Vec n => (-1 : Rat) * (-1)) = twoPow n := by
          have hfun : (fun _ : Vec n => (-1 : Rat) * (-1)) = (fun _ => (1 : Rat)) := by
            funext
            grind
          rw [hfun, signSum_const]
        rw [hone, hneg]

theorem signSum_vsum :
    ∀ {n m : Nat} (f : Vec n → Fin m → Rat),
      signSum (fun sign => vsum (fun j => f sign j)) =
        vsum (fun j => signSum (fun sign => f sign j))
  | _, 0, f => by
    have hzero : (fun sign => vsum (fun j : Fin 0 => f sign j)) = (fun _ => (0 : Rat)) := by
      funext sign
      rfl
    rw [hzero, signSum_zero]
    rfl
  | _, m + 1, f => by
    have hsplit : ∀ sign, vsum (fun j => f sign j) =
        f sign (Fin.last m) + vsum (fun j : Fin m => f sign j.castSucc) := fun sign => vsum_succ _
    rw [signSum_congr hsplit, signSum_add, signSum_vsum, vsum_succ]

theorem vsum_slot :
    ∀ {n : Nat} (v : Vec n) (i : Fin n) (c : Rat),
      vsum (fun j => v j * (if j = i then c else 0)) = v i * c
  | 0, _, i, _ => Fin.elim0 i
  | n + 1, v, i, c => by
    rw [vsum_succ]
    rcases Nat.lt_or_eq_of_le (Nat.le_of_lt_succ i.isLt) with hlt | heq
    · have i_eq : i = (Fin.castLT i hlt).castSucc := (Fin.castSucc_castLT i hlt).symm
      have hne : Fin.last n ≠ i := by
        rw [i_eq]
        exact (castSucc_ne_last (Fin.castLT i hlt)).symm
      rw [ite_eq_right hne, Rat.mul_zero, Rat.zero_add]
      have hprefix : vsum (fun j : Fin n =>
          v j.castSucc * (if j.castSucc = i then c else 0)) =
          vsum (fun j : Fin n => v j.castSucc * (if j = Fin.castLT i hlt then c else 0)) := by
        refine vsum_congr ?_
        intro j
        by_cases hj : j = Fin.castLT i hlt
        · rw [hj, ite_eq_left i_eq.symm, ite_eq_left rfl]
        · have hjs : j.castSucc ≠ i := by
            intro hsame
            apply hj
            apply Fin.castSucc_inj.mp
            rw [i_eq] at hsame
            exact hsame
          rw [ite_eq_right hjs, ite_eq_right hj, Rat.mul_zero]
      rw [hprefix, vsum_slot (fun j => v j.castSucc) (Fin.castLT i hlt) c]
      exact congrArg (fun t => v t * c) i_eq.symm
    · have i_eq : i = Fin.last n := Fin.eq_of_val_eq (by simp [Fin.val_last, heq])
      rw [i_eq]
      have hprefix : vsum (fun j : Fin n =>
          v j.castSucc * (if j.castSucc = Fin.last n then c else 0)) = 0 := by
        refine (vsum_congr ?_).trans vsum_zeros
        intro j
        rw [ite_eq_right (castSucc_ne_last j), Rat.mul_zero]
      rw [hprefix, Rat.add_zero, ite_eq_left rfl]

theorem sign_average_coordinate {n : Nat} (v : Vec n) (i : Fin n) :
    signSum (fun sign => dot sign v * sign i) = twoPow n * v i := by
  unfold dot
  have hterm : ∀ sign : Vec n, vsum (fun j => sign j * v j) * sign i =
      vsum (fun j => v j * (sign j * sign i)) := by
    intro sign
    rw [← vsum_mul_right]
    refine vsum_congr ?_
    intro j
    grind
  rw [signSum_congr hterm, signSum_vsum]
  have hcol : ∀ j, signSum (fun sign : Vec n => v j * (sign j * sign i)) =
      v j * (if j = i then twoPow n else 0) := by
    intro j
    rw [signSum_mul_left, signSum_product]
  rw [vsum_congr hcol, vsum_slot, Rat.mul_comm]

theorem sign_cube_recovers
    {r c : Nat} (matrix : Mat r c) (x : Vec c) {step : Rat} (hstep : step ≠ 0) (i : Fin c) :
    signSum (fun sign =>
      ((energy matrix (addVec x (smulVec step sign)) -
          energy matrix (subVec x (smulVec step sign))) / (2 * step)) * sign i) /
      twoPow c =
    applyGram matrix x i := by
  have hterm : ∀ sign : Vec c,
      ((energy matrix (addVec x (smulVec step sign)) -
          energy matrix (subVec x (smulVec step sign))) / (2 * step)) * sign i =
        dot sign (applyGram matrix x) * sign i := by
    intro sign
    rw [centered_directional_identity matrix x sign hstep]
  rw [signSum_congr hterm, sign_average_coordinate, Rat.div_def,
    Rat.mul_comm (twoPow c) (applyGram matrix x i), Rat.mul_assoc,
    Rat.mul_inv_cancel _ (twoPow_ne_zero c), Rat.mul_one]

end LGGRVI

