import Bell.QuantumTrace

/-! Finite separable states, partial traces, and the full state-to-behavior bound. -/
noncomputable section
open scoped BigOperators ComplexOrder MatrixOrder Matrix.Norms.L2Operator
open Matrix Bell.QuantumState Bell.QuantumTrace
namespace Bell.Separable
variable {n m : Type} [Fintype n] [DecidableEq n] [Fintype m] [DecidableEq m]

structure POVM {a : Type} [Fintype a] (E : a → Operator n) : Prop where
  positive : ∀ j, (E j).PosSemidef
  total : ∑ j, E j = 1

omit [Fintype n] [DecidableEq n] in
theorem positive_sum {i : Type} [Fintype i] (T : i → Operator n)
    (h : ∀ j, (T j).PosSemidef) : (∑ j, T j).PosSemidef := by
  exact (Finset.sum_nonneg fun j _ => (h j).nonneg).posSemidef

omit [DecidableEq n] [DecidableEq m] in
theorem product_density (A : Operator n) (B : Operator m)
    (hA : Density A) (hB : Density B) : Density (Matrix.kronecker A B) := by
  refine ⟨hA.positive.kronecker hB.positive, ?_⟩
  simp only [Matrix.kronecker, Matrix.trace_kronecker, hA.trace_one, hB.trace_one, one_mul]

/-- An actual finite convex mixture, with local density matrices at every component. -/
structure Ensemble (n m : Type) [Fintype n] [DecidableEq n] [Fintype m] [DecidableEq m] where
  count : ℕ
  weight : Fin count → ℝ
  probability : Bell.Probability weight
  alice : Fin count → Operator n
  bob : Fin count → Operator m
  alice_density : ∀ i, Density (alice i)
  bob_density : ∀ i, Density (bob i)

def mixture (e : Ensemble n m) : Operator (n × m) :=
  ∑ i, (e.weight i : ℂ) • Matrix.kronecker (e.alice i) (e.bob i)

def IsSeparable (ρ : Operator (n × m)) : Prop := ∃ e : Ensemble n m, ρ = mixture e

theorem mixture_density (e : Ensemble n m) : Density (mixture e) := by
  refine ⟨positive_sum _ (fun i => ?_), ?_⟩
  · exact ((e.alice_density i).positive.kronecker (e.bob_density i).positive).smul
      (show (0 : ℂ) ≤ (e.weight i : ℂ) by exact_mod_cast e.probability.nonneg i)
  · simp only [mixture, Matrix.trace_sum, Matrix.trace_smul]
    simp_rw [(product_density _ _ (e.alice_density _) (e.bob_density _)).trace_one,
      smul_eq_mul, mul_one]
    exact_mod_cast e.probability.total

theorem separable_density (ρ : Operator (n × m)) (hρ : IsSeparable ρ) : Density ρ := by
  obtain ⟨e, rfl⟩ := hρ
  exact mixture_density e

def productEnsemble (A : Operator n) (B : Operator m) (hA : Density A) (hB : Density B) :
    Ensemble n m where
  count := 1
  weight := fun _ => 1
  probability := ⟨fun _ => by norm_num, by simp⟩
  alice := fun _ => A
  bob := fun _ => B
  alice_density := fun _ => hA
  bob_density := fun _ => hB

theorem product_separable (A : Operator n) (B : Operator m)
    (hA : Density A) (hB : Density B) : IsSeparable (Matrix.kronecker A B) := by
  refine ⟨productEnsemble A B hA hB, ?_⟩
  change Matrix.kronecker A B = ∑ _i : Fin 1, (1 : ℂ) • Matrix.kronecker A B
  simp

def leftMarginal (ρ : Operator (n × m)) : Operator n :=
  ∑ b, ρ.submatrix (fun i => (i, b)) (fun j => (j, b))

def rightMarginal (ρ : Operator (n × m)) : Operator m :=
  ∑ a, ρ.submatrix (fun i => (a, i)) (fun j => (a, j))

omit [Fintype n] [DecidableEq n] [DecidableEq m] in
theorem leftMarginal_apply (ρ : Operator (n × m)) (i j : n) :
    leftMarginal ρ i j = ∑ b, ρ (i, b) (j, b) := by
  simp [leftMarginal, Matrix.sum_apply, Matrix.submatrix]

omit [DecidableEq n] [Fintype m] [DecidableEq m] in
theorem rightMarginal_apply (ρ : Operator (n × m)) (i j : m) :
    rightMarginal ρ i j = ∑ a, ρ (a, i) (a, j) := by
  simp [rightMarginal, Matrix.sum_apply, Matrix.submatrix]

omit [DecidableEq n] [DecidableEq m] in
theorem leftMarginal_density (ρ : Operator (n × m)) (hρ : Density ρ) :
    Density (leftMarginal ρ) := by
  refine ⟨positive_sum _ (fun b => hρ.positive.submatrix (fun i => (i, b))), ?_⟩
  simpa only [Matrix.trace, Matrix.diag, leftMarginal_apply, Fintype.sum_prod_type]
    using hρ.trace_one

omit [DecidableEq n] [DecidableEq m] in
theorem rightMarginal_density (ρ : Operator (n × m)) (hρ : Density ρ) :
    Density (rightMarginal ρ) := by
  refine ⟨positive_sum _ (fun a => hρ.positive.submatrix (fun i => (a, i))), ?_⟩
  simp only [Matrix.trace, Matrix.diag, rightMarginal_apply]
  rw [Finset.sum_comm]
  simpa only [Matrix.trace, Matrix.diag, Fintype.sum_prod_type] using hρ.trace_one

def productMarginals (ρ : Operator (n × m)) : Operator (n × m) :=
  Matrix.kronecker (leftMarginal ρ) (rightMarginal ρ)

omit [DecidableEq n] [DecidableEq m] in
theorem productMarginals_density (ρ : Operator (n × m)) (hρ : Density ρ) :
    Density (productMarginals ρ) :=
  product_density _ _ (leftMarginal_density ρ hρ) (rightMarginal_density ρ hρ)

theorem productMarginals_separable (ρ : Operator (n × m)) (hρ : Density ρ) :
    IsSeparable (productMarginals ρ) :=
  product_separable _ _ (leftMarginal_density ρ hρ) (rightMarginal_density ρ hρ)

omit [DecidableEq n] in
theorem mean_sum_left {i : Type} [Fintype i] (ρ : i → Operator n) (T : Operator n) :
    mean (∑ j, ρ j) T = ∑ j, mean (ρ j) T := by
  simp [mean, Finset.sum_mul, Matrix.trace_sum]

omit [DecidableEq n] in
theorem mean_sum_right {i : Type} [Fintype i] (ρ : Operator n) (E : i → Operator n) :
    mean ρ (∑ j, E j) = ∑ j, mean ρ (E j) := by
  simp [mean, Finset.mul_sum, Matrix.trace_sum]

theorem povm_probability {a : Type} [Fintype a] (ρ : Operator n) (hρ : Density ρ)
    (E : a → Operator n) (hE : POVM E) : Bell.Probability (fun j => mean ρ (E j)) := by
  refine ⟨fun j => density_mean_nonneg ρ (E j) hρ (hE.positive j), ?_⟩
  rw [← mean_sum_right, hE.total, mean_one ρ hρ]

omit [DecidableEq n] [DecidableEq m] in
theorem product_mean (A : Operator n) (B : Operator m) (hA : Density A) (hB : Density B)
    (E : Operator n) (F : Operator m) (hE : E.PosSemidef) (hF : F.PosSemidef) :
    mean (Matrix.kronecker A B) (Matrix.kronecker E F) = mean A E * mean B F := by
  unfold mean
  simp only [Matrix.kronecker, ← Matrix.mul_kronecker_mul, Matrix.trace_kronecker,
    Complex.mul_re, density_trace_real A E hA hE.isHermitian,
    density_trace_real B F hB hF.isHermitian,
    zero_mul, sub_zero]

variable {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]

def born (ρ : Operator (n × m)) (M : X → A → Operator n) (N : Y → B → Operator m) :
    Bell.Behavior X Y A B := fun x y a b => mean ρ (Matrix.kronecker (M x a) (N y b))

omit [Fintype X] [Fintype Y] in
theorem mixture_born (e : Ensemble n m) (M : X → A → Operator n)
    (N : Y → B → Operator m) (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y))
    (x : X) (y : Y) (a : A) (b : B) :
    born (mixture e) M N x y a b = ∑ i, e.weight i *
      (mean (e.alice i) (M x a) * mean (e.bob i) (N y b)) := by
  simp only [born, mixture, mean_sum_left, mean_real_smul]
  congr 1
  funext i
  rw [product_mean _ _ (e.alice_density i) (e.bob_density i) _ _
    ((hM x).positive a) ((hN y).positive b)]

def mixtureLocalModel (e : Ensemble n m) (M : X → A → Operator n)
    (N : Y → B → Operator m) (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y)) :
    Bell.LocalModel (born (mixture e) M N) where
  Hidden := Fin e.count
  finiteHidden := inferInstance
  weight := e.weight
  probability := e.probability
  alice := fun i x a => mean (e.alice i) (M x a)
  bob := fun i y b => mean (e.bob i) (N y b)
  alice_probability := fun i x => povm_probability _ (e.alice_density i) _ (hM x)
  bob_probability := fun i y => povm_probability _ (e.bob_density i) _ (hN y)
  reproduces := mixture_born e M N hM hN

theorem separable_positive_extension (ρ : Operator (n × m)) (hρ : IsSeparable ρ)
    (M : X → A → Operator n) (N : Y → B → Operator m)
    (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y)) :
    Bell.PositiveExtension (born ρ M N) := by
  obtain ⟨e, rfl⟩ := hρ
  exact Bell.local_positive_extension (mixtureLocalModel e M N hM hN)

omit [Fintype n] [Fintype m] in
theorem tensor_effect_total (E : A → Operator n) (F : B → Operator m)
    (hE : POVM E) (hF : POVM F) :
    ∑ r : A × B, Matrix.kronecker (E r.1) (F r.2) = 1 := by
  have h : (∑ r : A × B, Matrix.kronecker (E r.1) (F r.2)) =
      Matrix.kronecker (∑ a, E a) (∑ b, F b) := by
    ext ⟨i, b⟩ ⟨j, c⟩
    simp only [Matrix.sum_apply, Fintype.sum_prod_type, Matrix.kronecker,
      Matrix.kronecker_apply, Finset.mul_sum, Finset.sum_mul]
    exact Finset.sum_comm
  rw [h, hE.total, hF.total]
  exact Matrix.one_kronecker_one

def weightedTV (π : X × Y → ℝ) (p q : Bell.Behavior X Y A B) : ℝ :=
  ∑ k, π k * ((∑ r : A × B, |p k.1 k.2 r.1 r.2 - q k.1 k.2 r.1 r.2|) / 2)

theorem weightedTV_nonneg (π : X × Y → ℝ) (hπ : Bell.Probability π)
    (p q : Bell.Behavior X Y A B) : 0 ≤ weightedTV π p q := by
  exact Finset.sum_nonneg fun k _ => mul_nonneg (hπ.nonneg k)
    (div_nonneg (Finset.sum_nonneg fun _ _ => abs_nonneg _) (by norm_num))

theorem born_weightedTV_bound (ρ σ : Operator (n × m)) (hρ : Density ρ) (hσ : Density σ)
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (M : X → A → Operator n)
    (N : Y → B → Operator m) (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y)) :
    weightedTV π (born ρ M N) (born σ M N) ≤
      traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian) / 2 :=
  weighted_measurement_tv_bound ρ σ hρ hσ π hπ
    (fun (k : X × Y) (r : A × B) => Matrix.kronecker (M k.1 r.1) (N k.2 r.2))
    (fun k r => ((hM k.1).positive r.1).kronecker ((hN k.2).positive r.2))
    (fun k => tensor_effect_total _ _ (hM k.1) (hN k.2))

def behaviorRepair (π : X × Y → ℝ) (p : Bell.Behavior X Y A B) : ℝ :=
  sInf {r | ∃ l, Bell.PositiveExtension l ∧ r = weightedTV π p l}

theorem behaviorRepair_le (π : X × Y → ℝ) (hπ : Bell.Probability π)
    (p l : Bell.Behavior X Y A B) (hl : Bell.PositiveExtension l) :
    behaviorRepair π p ≤ weightedTV π p l := by
  apply csInf_le
  · refine ⟨0, ?_⟩
    rintro r ⟨q, _, rfl⟩
    exact weightedTV_nonneg π hπ p q
  · exact ⟨l, hl, rfl⟩

def separableDistances (ρ : Operator (n × m)) (hρ : Density ρ) : Set ℝ :=
  {r | ∃ σ : Operator (n × m), ∃ hσ : Density σ, IsSeparable σ ∧
    r = traceNorm (ρ - σ) (hρ.positive.isHermitian.sub hσ.positive.isHermitian)}

def separableDistance (ρ : Operator (n × m)) (hρ : Density ρ) : ℝ :=
  sInf (separableDistances ρ hρ)

def productResidual (ρ : Operator (n × m)) (hρ : Density ρ) : ℝ :=
  traceNorm (ρ - productMarginals ρ)
    (hρ.positive.isHermitian.sub (productMarginals_density ρ hρ).positive.isHermitian)

theorem productResidual_mem (ρ : Operator (n × m)) (hρ : Density ρ) :
    productResidual ρ hρ ∈ separableDistances ρ hρ :=
  ⟨productMarginals ρ, productMarginals_density ρ hρ, productMarginals_separable ρ hρ, rfl⟩

theorem separableDistances_bddBelow (ρ : Operator (n × m)) (hρ : Density ρ) :
    BddBelow (separableDistances ρ hρ) := by
  refine ⟨0, ?_⟩
  rintro r ⟨σ, hσ, _, rfl⟩
  exact traceNorm_nonneg _ _

theorem separableDistance_le_productResidual (ρ : Operator (n × m)) (hρ : Density ρ) :
    separableDistance ρ hρ ≤ productResidual ρ hρ :=
  csInf_le (separableDistances_bddBelow ρ hρ) (productResidual_mem ρ hρ)

theorem separableDistance_nonneg (ρ : Operator (n × m)) (hρ : Density ρ) :
    0 ≤ separableDistance ρ hρ := by
  apply le_csInf ⟨_, productResidual_mem ρ hρ⟩
  rintro r ⟨σ, hσ, _, rfl⟩
  exact traceNorm_nonneg _ _

theorem full_state_to_behavior_bound (ρ : Operator (n × m)) (hρ : Density ρ)
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (M : X → A → Operator n)
    (N : Y → B → Operator m) (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y)) :
    behaviorRepair π (born ρ M N) ≤ separableDistance ρ hρ / 2 ∧
      separableDistance ρ hρ / 2 ≤ productResidual ρ hρ / 2 := by
  constructor
  · suffices h : 2 * behaviorRepair π (born ρ M N) ≤ separableDistance ρ hρ by linarith
    apply le_csInf ⟨_, productResidual_mem ρ hρ⟩
    rintro r ⟨σ, hσ, hsep, rfl⟩
    have h1 := behaviorRepair_le π hπ (born ρ M N) (born σ M N)
      (separable_positive_extension σ hsep M N hM hN)
    have h2 := born_weightedTV_bound ρ σ hρ hσ π hπ M N hM hN
    linarith
  · exact div_le_div_of_nonneg_right (separableDistance_le_productResidual ρ hρ) (by norm_num)

omit [Fintype X] [Fintype Y] in
theorem born_probability (ρ : Operator (n × m)) (hρ : Density ρ)
    (M : X → A → Operator n) (N : Y → B → Operator m)
    (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y)) (x : X) (y : Y) :
    Bell.Probability (fun r : A × B => born ρ M N x y r.1 r.2) :=
  povm_probability ρ hρ _
    ⟨fun r => ((hM x).positive r.1).kronecker ((hN y).positive r.2),
      tensor_effect_total _ _ (hM x) (hN y)⟩

omit [Fintype X] [Fintype Y] in
theorem born_complex_trace (ρ : Operator (n × m)) (hρ : Density ρ)
    (M : X → A → Operator n) (N : Y → B → Operator m)
    (hM : ∀ x, POVM (M x)) (hN : ∀ y, POVM (N y)) (x : X) (y : Y) (a : A) (b : B) :
    (born ρ M N x y a b : ℂ) = Matrix.trace (ρ * Matrix.kronecker (M x a) (N y b)) := by
  apply Complex.ext
  · rfl
  · simpa using (density_trace_real ρ _ hρ
      (((hM x).positive a).kronecker ((hN y).positive b)).isHermitian).symm

omit [Fintype n] in
theorem binary_povm (E : Bool → Operator n) (hE : BinaryPOVM E) : POVM E := by
  refine ⟨hE.positive, ?_⟩
  simpa only [Fintype.sum_bool, add_comm] using hE.total

theorem separable_chsh_bound (ρ : Operator (n × m)) (hρ : IsSeparable ρ)
    (M : Bool → Bool → Operator n) (N : Bool → Bool → Operator m)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) :
    |Bell.CHSH.score (Bell.QuantumMeasurement.tensorBehavior ρ M N)| ≤ 2 :=
  Bell.CHSH.positive_extension_chsh _
    (separable_positive_extension ρ hρ M N (fun x => binary_povm _ (hM x))
      (fun y => binary_povm _ (hN y)))

theorem chsh_full_state_to_behavior_bound (ρ : Operator (n × m)) (hρ : Density ρ)
    (M : Bool → Bool → Operator n) (N : Bool → Bool → Operator m)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) :
    repair (Bell.QuantumMeasurement.tensorBehavior ρ M N) ≤ separableDistance ρ hρ / 2 ∧
      separableDistance ρ hρ / 2 ≤ productResidual ρ hρ / 2 := by
  constructor
  · suffices h : 2 * repair (Bell.QuantumMeasurement.tensorBehavior ρ M N) ≤
        separableDistance ρ hρ by linarith
    apply le_csInf ⟨_, productResidual_mem ρ hρ⟩
    rintro r ⟨σ, hσ, hsep, rfl⟩
    have h1 := repair_le_comparison (Bell.QuantumMeasurement.tensorBehavior ρ M N) _
      (separable_positive_extension σ hsep M N (fun x => binary_povm _ (hM x))
        (fun y => binary_povm _ (hN y)))
    have h2 := tensor_tv_bound ρ σ hρ hσ M N hM hN
    change repair (Bell.QuantumMeasurement.tensorBehavior ρ M N) ≤
      Bell.CHSH.tv (Bell.QuantumMeasurement.tensorBehavior ρ M N)
        (Bell.QuantumMeasurement.tensorBehavior σ M N) at h1
    linarith
  · exact div_le_div_of_nonneg_right (separableDistance_le_productResidual ρ hρ) (by norm_num)

omit [Fintype n] [DecidableEq n] [DecidableEq m] in
theorem leftMarginal_product (A : Operator n) (B : Operator m) (hB : Density B) :
    leftMarginal (Matrix.kronecker A B) = A := by
  ext i j
  simp only [leftMarginal_apply, Matrix.kronecker, Matrix.kronecker_apply, ← Finset.mul_sum]
  change A i j * B.trace = A i j
  rw [hB.trace_one, mul_one]

omit [DecidableEq n] [Fintype m] [DecidableEq m] in
theorem rightMarginal_product (A : Operator n) (B : Operator m) (hA : Density A) :
    rightMarginal (Matrix.kronecker A B) = B := by
  ext i j
  simp only [rightMarginal_apply, Matrix.kronecker, Matrix.kronecker_apply, ← Finset.sum_mul]
  change A.trace * B i j = B i j
  rw [hA.trace_one, one_mul]

omit [DecidableEq n] [DecidableEq m] in
theorem productMarginals_idempotent (ρ : Operator (n × m)) (hρ : Density ρ) :
    productMarginals (productMarginals ρ) = productMarginals ρ := by
  unfold productMarginals
  rw [leftMarginal_product _ _ (rightMarginal_density ρ hρ),
    rightMarginal_product _ _ (leftMarginal_density ρ hρ)]

end Bell.Separable
