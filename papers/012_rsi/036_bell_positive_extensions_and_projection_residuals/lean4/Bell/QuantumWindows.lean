import Bell.GHZEvolution
import Bell.QuantumState

/-! Exact exit and uncertainty-delayed certification for the explicit GHZ orbit.
The uncertainty budget is a bound on the Mermin score error, not an assumed
equation of motion or an assertion that the true state is on the orbit. -/
noncomputable section
open scoped BigOperators ComplexOrder
namespace Bell.QuantumWindows
open Bell.LinearProgramming Bell.NegativeMassFamilies Bell.BinaryScenarios Bell.GHZEvolution

def Local (p : Fin 64 → ℝ) : Prop :=
  ∃ q, (∀ g, 0 ≤ q g) ∧ (∑ g, q g = 1) ∧ mix mermin.A q = p

theorem rotation_column (t : ℝ) :
    (rotation t).mulVec (fun b => if b then 0 else 1) =
      (fun b => if b then (-Real.sin t : ℂ) else (Real.cos t : ℂ)) := by
  funext b
  cases b <;> simp [Matrix.mulVec, dotProduct, rotation]

theorem effect_hermitian (x a : Bool) : (effect x a).conjTranspose = effect x a := by
  ext r k
  cases x <;> cases a <;> cases r <;> cases k <;>
    simp [effect, pauli, Bell.CHSH.sign, Matrix.conjTranspose_apply]

theorem effect_positive (x a : Bool) : (effect x a).PosSemidef := by
  have h := Matrix.posSemidef_conjTranspose_mul_self (effect x a)
  rw [effect_hermitian, effect_projector] at h
  exact h

theorem local_povm (x : Bool) : Bell.QuantumState.BinaryPOVM (effect x) :=
  ⟨effect_positive x, effects_total x⟩

theorem all_visibilities_quantum (v : ℝ) (hv : 0 ≤ v) (hv1 : v ≤ 1) :
    ∃ t, 0 ≤ t ∧ t ≤ Real.pi/4 ∧ ‖state (Real.cos t) (Real.sin t)‖ = 1 ∧
      born (Real.cos t) (Real.sin t) = behavior mermin v := by
  refine ⟨Real.arcsin v/2, div_nonneg (Real.arcsin_nonneg.mpr hv) (by norm_num),
    ?_, orbit_unit _, ?_⟩
  · have := Real.arcsin_le_pi_div_two v
    linarith
  · rw [orbit_born, show 2*(Real.arcsin v/2)=Real.arcsin v by ring,
      Real.sin_arcsin (by linarith) hv1]

theorem local_score (p : Fin 64 → ℝ) (hp : Local p) : pairing mermin.c p ≤ 2 := by
  obtain ⟨q,hq,hn,he⟩ := hp
  rw [← he, Bell.ContextualFraction.pairing_mix]
  calc
    _ ≤ ∑ g, q g * 2 := by
      apply Finset.sum_le_sum
      intro g _
      rw [mermin.score_column]
      apply mul_le_mul_of_nonneg_left _ (hq g)
      rcases mermin.K_values g with h | h <;> linarith
    _ = 2 := by rw [← Finset.sum_mul, hn]; ring

theorem visibility_threshold (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4) :
    1/2 < visibility t ↔ Real.pi/12 < t := by
  have h := Real.strictMonoOn_sin.lt_iff_lt
    (show Real.pi/6 ∈ Set.Icc (-(Real.pi/2)) (Real.pi/2) by
      constructor <;> linarith [Real.pi_pos])
    (show 2*t ∈ Set.Icc (-(Real.pi/2)) (Real.pi/2) by
      constructor <;> linarith [Real.pi_pos])
  rw [Real.sin_pi_div_six] at h
  change 1/2 < Real.sin (2*t) ↔ _
  exact h.trans (by constructor <;> intro h <;> linarith)

theorem exact_exit (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4) :
    ¬ Local (born (Real.cos t) (Real.sin t)) ↔ Real.pi/12 < t := by
  rw [← visibility_threshold t ht ht1, orbit_born]
  constructor
  · intro h
    by_contra hn
    have hv := visibility_range t ht ht1
    exact h ⟨extension mermin (visibility t),
      Bell.NegativeMassFamilies.extension_nonnegative mermin _ hv.1 (le_of_not_gt hn),
      Bell.NegativeMassFamilies.extension_total mermin _, extension_projects mermin _⟩
  · intro h hl
    have hs := local_score _ hl
    rw [behavior_score] at hs
    change 4*visibility t ≤ 2 at hs
    linarith

theorem onset_zero : cf (Real.pi/12) = 0 ∧ mass (Real.pi/12) = 0 := by
  have h : visibility (Real.pi/12) = 1/2 := by
    unfold visibility
    rw [show 2*(Real.pi/12)=Real.pi/6 by ring, Real.sin_pi_div_six]
  simp [cf, mass, h]

theorem quantum_endpoint : cf (Real.pi/4) = 1 ∧ mass (Real.pi/4) = 1/2 := by
  have h : visibility (Real.pi/4) = 1 := by
    unfold visibility
    rw [show 2*(Real.pi/4)=Real.pi/2 by ring, Real.sin_pi_div_two]
  norm_num [cf, mass, h]

def certifiedStart (η : ℝ) : ℝ := Real.arcsin ((2+η)/4)/2

theorem noisy_threshold (t η : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4)
    (hη : 0 ≤ η) (hη1 : η ≤ 2) :
    2+η < 4*visibility t ↔ certifiedStart η < t := by
  have h := Real.strictMonoOn_sin.lt_iff_lt (Real.arcsin_mem_Icc ((2+η)/4))
    (show 2*t ∈ Set.Icc (-(Real.pi/2)) (Real.pi/2) by
      constructor <;> linarith [Real.pi_pos])
  rw [Real.sin_arcsin (by linarith : -1 ≤ (2+η)/4) (by linarith)] at h
  dsimp [visibility, certifiedStart]
  constructor
  · intro he
    have := h.mp (by linarith)
    linarith
  · intro he
    have := h.mpr (by linarith)
    linarith

theorem noisy_exit (t η : ℝ) (p : Fin 64 → ℝ)
    (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4) (hη : 0 ≤ η) (hη1 : η ≤ 2)
    (hwindow : certifiedStart η < t)
    (herror : |pairing mermin.c p - 4*visibility t| ≤ η) : ¬ Local p := by
  intro hp
  have he := (abs_le.mp herror).1
  have hs := local_score p hp
  have hw := (noisy_threshold t η ht ht1 hη hη1).mpr hwindow
  linarith

theorem no_score_guarantee_at_large_error (t η : ℝ) (hη : 2 ≤ η) :
    4*visibility t-η ≤ 2 := by
  have h := Real.sin_le_one (2*t)
  dsimp [visibility]
  linarith

theorem contextual_fraction_witness (p : Fin 64 → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hactive : pairing (fun i => |mermin.c i|) p = 4) :
    (pairing mermin.c p - 2)/2 ≤ Bell.ContextualFraction.fraction mermin.A p := by
  have h := Bell.ContextualFraction.lower_of_dual mermin.A p (cfWitness mermin) hp
    (cf_witness_feasible mermin).1 (cf_witness_feasible mermin).2
  have he : pairing (cfWitness mermin) p = (4-pairing mermin.c p)/2 := by
    simp only [pairing, cfWitness, div_mul_eq_mul_div, sub_mul,
      ← Finset.sum_div, Finset.sum_sub_distrib]
    change ((pairing (fun i => |mermin.c i|) p)-pairing mermin.c p)/2 = _
    rw [hactive]
    rfl
  rw [he] at h
  linarith

theorem noisy_cf_lower (t η : ℝ) (p : Fin 64 → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hactive : pairing (fun i => |mermin.c i|) p = 4)
    (herror : |pairing mermin.c p - 4*visibility t| ≤ η) :
    2*visibility t-1-η/2 ≤ Bell.ContextualFraction.fraction mermin.A p := by
  have h := contextual_fraction_witness p hp hactive
  have he := (abs_le.mp herror).1
  linarith

theorem negative_mass_witness (p : Fin 64 → ℝ) (q : Fin 64 → ℝ)
    (hq : mix mermin.A q = p) (hn : ∑ g, q g = 1) :
    (pairing mermin.c p-2)/4 ≤ Bell.SignedDuality.negativeMass q := by
  have hscale (u : Fin 64 → ℝ) :
      pairing (fun i => mermin.c i/4) u = pairing mermin.c u/4 := by
    simp only [pairing, div_mul_eq_mul_div, ← Finset.sum_div]
  have hd : ∀ g, -1 ≤ pairing (fun i => mermin.c i/4) (mermin.A g) + (-1/2) ∧
      pairing (fun i => mermin.c i/4) (mermin.A g) + (-1/2) ≤ 0 := by
    intro g
    rw [hscale, mermin.score_column]
    rcases mermin.K_values g with h | h <;> rw [h] <;> norm_num
  have h := Bell.SignedDuality.negative_mass_weak_duality mermin.A p
    (fun i => mermin.c i/4) q (-1/2) hq hn hd
  rw [hscale] at h
  linarith

theorem noisy_negative_mass_lower (t η : ℝ) (p : Fin 64 → ℝ) (q : Fin 64 → ℝ)
    (hq : mix mermin.A q = p) (hn : ∑ g, q g = 1)
    (herror : |pairing mermin.c p - 4*visibility t| ≤ η) :
    visibility t-1/2-η/4 ≤ Bell.SignedDuality.negativeMass q := by
  have h := negative_mass_witness p q hq hn
  have he := (abs_le.mp herror).1
  linarith

theorem score_error_l1 (p r : Fin 64 → ℝ) :
    |pairing mermin.c p - pairing mermin.c r| ≤ ∑ i, |p i-r i| := by
  have he : pairing mermin.c p - pairing mermin.c r =
      ∑ i, mermin.c i*(p i-r i) := by
    simp only [pairing, mul_sub, Finset.sum_sub_distrib]
  rw [he]
  apply (Finset.abs_sum_le_sum_abs _ _).trans
  apply Finset.sum_le_sum
  intro i _
  rw [abs_mul]
  have hc : |mermin.c i| ≤ 1 := by
    rcases mermin.c_values i with h | h | h <;> rw [h] <;> norm_num
  simpa using mul_le_mul_of_nonneg_right hc (abs_nonneg (p i-r i))

theorem noisy_tv_exit (t ε : ℝ) (p : Fin 64 → ℝ)
    (ht : 0 ≤ t) (ht1 : t ≤ Real.pi/4) (hε : 0 ≤ ε) (hε1 : ε ≤ 1/8)
    (hwindow : certifiedStart (16*ε) < t)
    (herror : (∑ i, |p i-born (Real.cos t) (Real.sin t) i|)/16 ≤ ε) : ¬ Local p := by
  apply noisy_exit t (16*ε) p ht ht1 (by positivity) (by linarith) hwindow
  have he := score_error_l1 p (born (Real.cos t) (Real.sin t))
  rw [orbit_born] at herror
  rw [orbit_born, behavior_score] at he
  change |pairing mermin.c p-4*visibility t| ≤ _ at he
  linarith

end Bell.QuantumWindows
