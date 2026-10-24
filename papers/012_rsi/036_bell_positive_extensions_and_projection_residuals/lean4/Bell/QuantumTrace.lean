import Bell.QuantumMeasurement

/-! Finite Hermitian Schatten 1 norm and measurement contractivity. -/
noncomputable section
open scoped BigOperators ComplexOrder Matrix.Norms.L2Operator
open Matrix Bell.QuantumState
namespace Bell.QuantumTrace
variable {n : Type} [Fintype n] [DecidableEq n]

/-- For a Hermitian matrix the singular values are the absolute eigenvalues.
This spectral formula is the finite Hermitian trace norm; no norm instance
or infinite-dimensional trace-class assertion is introduced. -/
def traceNorm (Z : Operator n) (hZ : Z.IsHermitian) : ℝ :=
  ∑ i, |hZ.eigenvalues i|

theorem traceNorm_nonneg (Z : Operator n) (hZ : Z.IsHermitian) :
    0 ≤ traceNorm Z hZ := Finset.sum_nonneg fun _ _ => abs_nonneg _

theorem hermitian_trace_mixture (Z T : Operator n) (hZ : Z.IsHermitian) :
    mean Z T = ∑ i, hZ.eigenvalues i *
      Bell.Quantum.expectation (hZ.eigenvectorBasis i) (asOperator T) := by
  have ht := LinearMap.trace_eq_sum_inner (asOperator (T * Z)).toLinearMap
    hZ.eigenvectorBasis
  rw [trace_asOperator, Matrix.trace_mul_comm] at ht
  have hm : asOperator (T * Z) = (asOperator T).comp (asOperator Z) :=
    map_mul (Matrix.toEuclideanCLM (n := n) (𝕜 := ℂ)) T Z
  rw [hm] at ht
  simp only [ContinuousLinearMap.coe_coe, ContinuousLinearMap.comp_apply,
    eigenvector_apply, map_smul, inner_smul_right] at ht
  have hr := congrArg Complex.re ht
  simpa [mean, Bell.Quantum.expectation, Complex.mul_re] using hr

omit [DecidableEq n] in
theorem mean_sub_left (ρ σ T : Operator n) :
    mean (ρ - σ) T = mean ρ T - mean σ T := by
  simp [mean, sub_mul, Matrix.trace_sub]

theorem mean_add_left (ρ σ T : Operator n) :
    mean (ρ + σ) T = mean ρ T + mean σ T := by
  simp [mean, add_mul, Matrix.trace_add]

theorem mean_real_smul (t : ℝ) (Z T : Operator n) :
    mean ((t : ℂ) • Z) T = t * mean Z T := by
  simp [mean, Matrix.trace_smul, Complex.mul_re]

theorem pure_sum {a : Type} [Fintype a] (E : a → Operator n) (v : Space n) :
    Bell.Quantum.expectation v (asOperator (∑ j, E j)) =
      ∑ j, Bell.Quantum.expectation v (asOperator (E j)) := by
  simp [Bell.Quantum.expectation, asOperator, inner_sum]

theorem measurement_l1_bound {a : Type} [Fintype a]
    (Z : Operator n) (hZ : Z.IsHermitian) (E : a → Operator n)
    (hp : ∀ j, (E j).PosSemidef) (hs : ∑ j, E j = 1) :
    ∑ j, |mean Z (E j)| ≤ traceNorm Z hZ := by
  calc
    _ ≤ ∑ j, ∑ i, |hZ.eigenvalues i| *
        Bell.Quantum.expectation (hZ.eigenvectorBasis i) (asOperator (E j)) := by
      apply Finset.sum_le_sum
      intro j _
      rw [hermitian_trace_mixture Z (E j) hZ]
      calc
        _ ≤ ∑ i, |hZ.eigenvalues i *
            Bell.Quantum.expectation (hZ.eigenvectorBasis i) (asOperator (E j))| :=
          Finset.abs_sum_le_sum_abs _ _
        _ = _ := by simp_rw [abs_mul, abs_of_nonneg (pure_nonneg _ (hp j) _)]
    _ = traceNorm Z hZ := by
      rw [Finset.sum_comm]
      simp_rw [← Finset.mul_sum, ← pure_sum, hs, pure_one,
        hZ.eigenvectorBasis.orthonormal.1, one_pow, mul_one]
      rfl

theorem measurement_tv_bound {a : Type} [Fintype a]
    (ρ σ : Operator n) (hρ : Density ρ) (hσ : Density σ)
    (E : a → Operator n) (hp : ∀ j, (E j).PosSemidef) (hs : ∑ j, E j = 1) :
    (∑ j, |mean ρ (E j) - mean σ (E j)|) / 2 ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2 := by
  simp_rw [← mean_sub_left]
  exact div_le_div_of_nonneg_right (measurement_l1_bound _ _ E hp hs) (by norm_num)

theorem pure_operator_bound (T : Operator n) (v : Space n) (hv : ‖v‖ = 1) :
    |Bell.Quantum.expectation v (asOperator T)| ≤ ‖asOperator T‖ := by
  calc
    _ ≤ ‖inner ℂ v (asOperator T v)‖ := Complex.abs_re_le_norm _
    _ ≤ ‖v‖ * ‖asOperator T v‖ := norm_inner_le_norm _ _
    _ ≤ ‖v‖ * (‖asOperator T‖ * ‖v‖) :=
      mul_le_mul_of_nonneg_left ((asOperator T).le_opNorm v) (norm_nonneg _)
    _ = _ := by rw [hv]; ring

theorem trace_operator_bound (Z T : Operator n) (hZ : Z.IsHermitian) :
    |mean Z T| ≤ ‖asOperator T‖ * traceNorm Z hZ := by
  rw [hermitian_trace_mixture Z T hZ]
  calc
    _ ≤ ∑ i, |hZ.eigenvalues i *
        Bell.Quantum.expectation (hZ.eigenvectorBasis i) (asOperator T)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, |hZ.eigenvalues i| * ‖asOperator T‖ := by
      apply Finset.sum_le_sum
      intro i _
      rw [abs_mul]
      exact mul_le_mul_of_nonneg_left
        (pure_operator_bound T _ (hZ.eigenvectorBasis.orthonormal.1 i)) (abs_nonneg _)
    _ = _ := by rw [← Finset.sum_mul]; exact mul_comm _ _

theorem joint_effect_total (M N : Bool → Operator n)
    (hM : BinaryPOVM M) (hN : BinaryPOVM N) :
    ∑ r : Bool × Bool, M r.1 * N r.2 = 1 := by
  simp only [Fintype.sum_prod_type, ← Finset.mul_sum, ← Finset.sum_mul,
    Fintype.sum_bool]
  rw [add_comm (M true), add_comm (N true), hM.total, hN.total, one_mul]

theorem born_tv_bound (ρ σ : Operator n) (hρ : Density ρ) (hσ : Density σ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : Bell.QuantumMeasurement.CrossCommute M N) :
    Bell.CHSH.tv (Bell.QuantumMeasurement.behavior ρ M N)
      (Bell.QuantumMeasurement.behavior σ M N) ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2 := by
  have h (x y : Bool) := measurement_l1_bound (ρ - σ)
    (hρ.positive.isHermitian.sub hσ.positive.isHermitian)
    (fun r : Bool × Bool => M x r.1 * N y r.2)
    (fun r => Bell.QuantumMeasurement.joint_effect_positive M N hM hN hc x y r.1 r.2)
    (joint_effect_total (M x) (N y) (hM x) (hN y))
  simp only [mean_sub_left, Fintype.sum_prod_type, Fintype.sum_bool] at h
  unfold Bell.CHSH.tv Bell.QuantumMeasurement.behavior
  simp only [Fintype.sum_prod_type, Fintype.sum_bool]
  linarith [h false false, h false true, h true false, h true true]


theorem weighted_measurement_tv_bound {c a : Type} [Fintype c] [Fintype a]
    (ρ σ : Operator n) (hρ : Density ρ) (hσ : Density σ)
    (π : c → ℝ) (hπ : Bell.Probability π) (E : c → a → Operator n)
    (hp : ∀ k j, (E k j).PosSemidef) (hs : ∀ k, ∑ j, E k j = 1) :
    (∑ k, π k * ((∑ j, |mean ρ (E k j) - mean σ (E k j)|) / 2)) ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2 := by
  calc
    _ ≤ ∑ k, π k * (traceNorm (ρ - σ)
        (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2) := by
      apply Finset.sum_le_sum
      intro k _
      exact mul_le_mul_of_nonneg_left
        (measurement_tv_bound ρ σ hρ hσ (E k) (hp k) (hs k)) (hπ.nonneg k)
    _ = _ := by rw [← Finset.sum_mul, hπ.total, one_mul]

def repair (p : Bell.CHSH.Table) : ℝ :=
  sInf {r | ∃ l, Bell.PositiveExtension l ∧ r = Bell.CHSH.tv p l}

theorem repair_le_comparison (p l : Bell.CHSH.Table) (hl : Bell.PositiveExtension l) :
    repair p ≤ Bell.CHSH.tv p l := by
  apply csInf_le
  · refine ⟨0, ?_⟩
    rintro r ⟨q, _, rfl⟩
    exact Bell.CHSH.tv_nonnegative p q
  · exact ⟨l, hl, rfl⟩

theorem born_repair_bound (ρ σ : Operator n) (hρ : Density ρ) (hσ : Density σ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : Bell.QuantumMeasurement.CrossCommute M N)
    (hl : Bell.PositiveExtension (Bell.QuantumMeasurement.behavior σ M N)) :
    repair (Bell.QuantumMeasurement.behavior ρ M N) ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2 :=
  (repair_le_comparison _ _ hl).trans (born_tv_bound ρ σ hρ hσ M N hM hN hc)

theorem state_distance_witness (ρ σ : Operator n) (hρ : Density ρ) (hσ : Density σ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y))
    (hc : Bell.QuantumMeasurement.CrossCommute M N)
    (hl : Bell.PositiveExtension (Bell.QuantumMeasurement.behavior σ M N)) :
    max 0 (|Bell.CHSH.score (Bell.QuantumMeasurement.behavior ρ M N)| - 2) / 4 ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) := by
  have h1 := Bell.CHSH.chsh_repair_lower_bound (Bell.QuantumMeasurement.behavior ρ M N) _ hl
  have h2 := born_tv_bound ρ σ hρ hσ M N hM hN hc
  linarith


theorem density_traceNorm (ρ : Operator n) (hρ : Density ρ) :
    traceNorm ρ hρ.positive.isHermitian = 1 := by
  unfold traceNorm
  simp_rw [abs_of_nonneg (hρ.positive.eigenvalues_nonneg _)]
  exact (density_weights ρ hρ).total

theorem tensor_tv_bound {m : Type} [Fintype m] [DecidableEq m]
    (ρ σ : Operator (n × m)) (hρ : Density ρ) (hσ : Density σ)
    (M : Bool → Bool → Operator n) (N : Bool → Bool → Operator m)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) :
    Bell.CHSH.tv (Bell.QuantumMeasurement.tensorBehavior ρ M N)
      (Bell.QuantumMeasurement.tensorBehavior σ M N) ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2 := by
  rw [Bell.QuantumMeasurement.tensor_behavior_eq,
    Bell.QuantumMeasurement.tensor_behavior_eq]
  exact born_tv_bound ρ σ hρ hσ _ _
    (fun x => Bell.QuantumMeasurement.leftLift_povm _ (hM x))
    (fun y => Bell.QuantumMeasurement.rightLift_povm _ (hN y))
    (Bell.QuantumMeasurement.tensor_cross_commute M N)

end Bell.QuantumTrace
