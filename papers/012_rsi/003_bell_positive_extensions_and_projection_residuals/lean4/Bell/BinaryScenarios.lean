import Bell.NegativeMassFamilies

/-! Explicit deterministic models. Cell order is settings first, then outcomes;
assignment bits give each party's two local response values. -/
noncomputable section
open scoped BigOperators
namespace Bell.BinaryScenarios
open Bell.LinearProgramming Bell.NegativeMassFamilies
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def bit (j k : ℕ) : ℕ := j / 2^k % 2
def spin (b : ℕ) : ℤ := 1-2*(b:ℤ)

def chshAI (g i : Fin 16) : ℤ :=
  if bit g (i.val/8) == i.val/2%2 && bit g (2+i.val/4%2) == i.val%2 then 1 else 0
def chshCI (i : Fin 16) : ℤ :=
  (if i.val/8 == 1 && i.val/4%2 == 1 then -1 else 1) *
    spin (i.val/2%2) * spin (i.val%2)
def chshKI (g : Fin 16) : ℤ :=
  spin (bit g 0) * (spin (bit g 2)+spin (bit g 3)) +
    spin (bit g 1) * (spin (bit g 2)-spin (bit g 3))

def merminAI (g i : Fin 64) : ℤ :=
  if bit g (i.val/32) == i.val/4%2 &&
      bit g (2+i.val/16%2) == i.val/2%2 &&
      bit g (4+i.val/8%2) == i.val%2 then 1 else 0
def merminCI (i : Fin 64) : ℤ :=
  (if i.val/32+i.val/16%2+i.val/8%2 == 0 then -1
   else if i.val/32+i.val/16%2+i.val/8%2 == 2 then 1 else 0) *
    spin (i.val/4%2) * spin (i.val/2%2) * spin (i.val%2)
def merminKI (g : Fin 64) : ℤ :=
  -spin (bit g 0)*spin (bit g 2)*spin (bit g 4) +
  spin (bit g 0)*spin (bit g 3)*spin (bit g 5) +
  spin (bit g 1)*spin (bit g 2)*spin (bit g 5) +
  spin (bit g 1)*spin (bit g 3)*spin (bit g 4)

def chsh : Line (Fin 16) (Fin 16) where
  A := fun g i => (chshAI g i : ℝ)
  c := fun i => (chshCI i : ℝ)
  K := fun g => (chshKI g : ℝ)
  D := 16
  d := 4
  m := 4
  D_pos := by norm_num
  d_pos := by norm_num
  m_pos := by norm_num
  binary := by exact_mod_cast (show ∀ g i, chshAI g i = 0 ∨ chshAI g i = 1 by decide)
  column := by exact_mod_cast (show ∀ g, (∑ i, chshAI g i) = 4 by decide)
  card := by norm_num
  sumK := by exact_mod_cast (show (∑ g, chshKI g) = 0 by decide)
  negative_count := by
    norm_num only
    exact_mod_cast (show (∑ g, if chshKI g = -2 then (1:ℤ) else 0) = 8 by decide)
  K_values := by exact_mod_cast (show ∀ g, chshKI g = -2 ∨ chshKI g = 2 by decide)
  c_values := by exact_mod_cast (show ∀ i, chshCI i = -1 ∨ chshCI i = 0 ∨ chshCI i = 1 by decide)
  fiber_count := by
    norm_num only
    exact_mod_cast (show ∀ i, (∑ g, chshAI g i) = 4 by decide)
  fiber_K := by
    norm_num only
    exact_mod_cast (show ∀ i, (∑ g, chshKI g * chshAI g i) = 4 * chshCI i by decide)
  score_column := by
    dsimp only [pairing]
    exact_mod_cast (show ∀ g, (∑ i, chshCI i * chshAI g i) = chshKI g by decide)
  active_column := by
    dsimp only [pairing]
    exact_mod_cast (show ∀ g, (∑ i, |chshCI i| * chshAI g i) = 4 by decide)
  sumc := by exact_mod_cast (show (∑ i, chshCI i) = 0 by decide)
  sumc2 := by
    norm_num only
    exact_mod_cast (show (∑ i, chshCI i * chshCI i) = 16 by decide)

theorem chsh_negative_mass (v : ℝ) (hv : 0 ≤ v) :
    (∑ g, extension chsh v g = 1) ∧
    mix chsh.A (extension chsh v) = behavior chsh v ∧
    Bell.SignedDuality.negativeMass (extension chsh v) = max 0 (v-1/2) ∧
    ∀ q, mix chsh.A q = behavior chsh v → (∑ g, q g = 1) →
      max 0 (v-1/2) ≤ Bell.SignedDuality.negativeMass q :=
  negative_mass_exact chsh v hv

theorem chsh_contextual_fraction (v : ℝ) (hv : 0 ≤ v) (hv1 : v ≤ 1) :
    Bell.ContextualFraction.fraction chsh.A (behavior chsh v) = max 0 (2*v-1) :=
  contextual_fraction_exact chsh v hv hv1

def mermin : Line (Fin 64) (Fin 64) where
  A := fun g i => (merminAI g i : ℝ)
  c := fun i => (merminCI i : ℝ)
  K := fun g => (merminKI g : ℝ)
  D := 64
  d := 8
  m := 8
  D_pos := by norm_num
  d_pos := by norm_num
  m_pos := by norm_num
  binary := by exact_mod_cast (show ∀ g i, merminAI g i = 0 ∨ merminAI g i = 1 by decide)
  column := by exact_mod_cast (show ∀ g, (∑ i, merminAI g i) = 8 by decide)
  card := by norm_num
  sumK := by exact_mod_cast (show (∑ g, merminKI g) = 0 by decide)
  negative_count := by
    norm_num only
    exact_mod_cast (show (∑ g, if merminKI g = -2 then (1:ℤ) else 0) = 32 by decide)
  K_values := by exact_mod_cast (show ∀ g, merminKI g = -2 ∨ merminKI g = 2 by decide)
  c_values := by exact_mod_cast (show ∀ i, merminCI i = -1 ∨ merminCI i = 0 ∨ merminCI i = 1 by decide)
  fiber_count := by
    norm_num only
    exact_mod_cast (show ∀ i, (∑ g, merminAI g i) = 8 by decide)
  fiber_K := by
    norm_num only
    exact_mod_cast (show ∀ i, (∑ g, merminKI g * merminAI g i) = 8 * merminCI i by decide)
  score_column := by
    dsimp only [pairing]
    exact_mod_cast (show ∀ g, (∑ i, merminCI i * merminAI g i) = merminKI g by decide)
  active_column := by
    dsimp only [pairing]
    exact_mod_cast (show ∀ g, (∑ i, |merminCI i| * merminAI g i) = 4 by decide)
  sumc := by exact_mod_cast (show (∑ i, merminCI i) = 0 by decide)
  sumc2 := by
    norm_num only
    exact_mod_cast (show (∑ i, merminCI i * merminCI i) = 32 by decide)

theorem mermin_negative_mass (v : ℝ) (hv : 0 ≤ v) :
    (∑ g, extension mermin v g = 1) ∧
    mix mermin.A (extension mermin v) = behavior mermin v ∧
    Bell.SignedDuality.negativeMass (extension mermin v) = max 0 (v-1/2) ∧
    ∀ q, mix mermin.A q = behavior mermin v → (∑ g, q g = 1) →
      max 0 (v-1/2) ≤ Bell.SignedDuality.negativeMass q :=
  negative_mass_exact mermin v hv

theorem mermin_contextual_fraction (v : ℝ) (hv : 0 ≤ v) (hv1 : v ≤ 1) :
    Bell.ContextualFraction.fraction mermin.A (behavior mermin v) = max 0 (2*v-1) :=
  contextual_fraction_exact mermin v hv hv1

def chshCell (x y a b : Bool) : Fin 16 :=
  ⟨(if x then 8 else 0) + (if y then 4 else 0) +
    (if a then 2 else 0) + (if b then 1 else 0), by
      cases x <;> cases y <;> cases a <;> cases b <;> decide⟩

/-- The finite certificate's table is precisely the manuscript's existing CHSH isotropic table. -/
theorem chsh_behavior_bridge (v : ℝ) (x y a b : Bool) :
    behavior chsh v (chshCell x y a b) = Bell.CHSH.isotropic v x y a b := by
  cases x <;> cases y <;> cases a <;> cases b <;>
    norm_num [behavior, chsh, chshCell, chshCI, spin, Bell.CHSH.isotropic,
      Bell.CHSH.coefficient, Bell.CHSH.sign]

end Bell.BinaryScenarios

