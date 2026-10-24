import Bell.Quantum
import Mathlib.Analysis.Matrix.PosDef
import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.CStarAlgebra.Basic
import Mathlib.Analysis.InnerProductSpace.Trace

/-! Finite-dimensional density matrices and binary POVMs, with no spectral
or contraction premises hidden in their definitions. -/
noncomputable section
open scoped BigOperators ComplexOrder Matrix.Norms.L2Operator
open Matrix
namespace Bell.QuantumState

variable {n : Type} [Fintype n] [DecidableEq n]
abbrev Operator (n : Type) := Matrix n n ℂ
abbrev Space (n : Type) := EuclideanSpace ℂ n

def asOperator (T : Operator n) : Space n →L[ℂ] Space n := Matrix.toEuclideanCLM (n := n) (𝕜 := ℂ) T

def mean (ρ T : Operator n) : ℝ := (Matrix.trace (ρ * T)).re

structure Density (ρ : Operator n) : Prop where
  positive : ρ.PosSemidef
  trace_one : ρ.trace = 1

structure BinaryPOVM (M : Bool → Operator n) : Prop where
  positive : ∀ a, (M a).PosSemidef
  total : M false + M true = 1

def observable (M : Bool → Operator n) : Operator n := M true - M false

theorem asOperator_apply (T : Operator n) (v : Space n) :
    asOperator T v = Matrix.toEuclideanLin T v := rfl

theorem trace_asOperator (T : Operator n) :
    LinearMap.trace ℂ (Space n) (asOperator T).toLinearMap = T.trace := by
  change LinearMap.trace ℂ (Space n) (Matrix.toEuclideanLin T) = _
  rw [Matrix.toEuclideanLin_eq_toLin_orthonormal, Matrix.trace_toLin_eq]

theorem eigenvector_apply (ρ : Operator n) (hρ : ρ.IsHermitian) (i : n) :
    asOperator ρ (hρ.eigenvectorBasis i) =
      (hρ.eigenvalues i : ℂ) • hρ.eigenvectorBasis i := by
  apply WithLp.ofLp_injective
  simpa [asOperator, RCLike.real_smul_eq_coe_smul] using hρ.mulVec_eigenvectorBasis i

theorem density_weights (ρ : Operator n) (hρ : Density ρ) :
    Bell.Probability hρ.positive.isHermitian.eigenvalues := by
  refine ⟨hρ.positive.eigenvalues_nonneg, ?_⟩
  have h := congrArg Complex.re hρ.positive.isHermitian.trace_eq_sum_eigenvalues
  simpa [hρ.trace_one] using h.symm

theorem density_vectors_unit (ρ : Operator n) (hρ : Density ρ) (i : n) :
    ‖hρ.positive.isHermitian.eigenvectorBasis i‖ = 1 :=
  hρ.positive.isHermitian.eigenvectorBasis.orthonormal.1 i

theorem density_trace_mixture (ρ T : Operator n) (hρ : Density ρ) :
    mean ρ T = ∑ i, hρ.positive.isHermitian.eigenvalues i *
      Bell.Quantum.expectation (hρ.positive.isHermitian.eigenvectorBasis i) (asOperator T) := by
  have ht := LinearMap.trace_eq_sum_inner (asOperator (T * ρ)).toLinearMap
    hρ.positive.isHermitian.eigenvectorBasis
  rw [trace_asOperator] at ht
  rw [Matrix.trace_mul_comm] at ht
  have hm : asOperator (T * ρ) = (asOperator T).comp (asOperator ρ) := by
    exact map_mul (Matrix.toEuclideanCLM (n := n) (𝕜 := ℂ)) T ρ
  rw [hm] at ht
  simp only [ContinuousLinearMap.coe_coe, ContinuousLinearMap.comp_apply,
    eigenvector_apply, map_smul, inner_smul_right] at ht
  have hr := congrArg Complex.re ht
  simpa [mean, Bell.Quantum.expectation, Complex.mul_re] using hr


theorem pure_eq_dot (T : Operator n) (v : Space n) :
    Bell.Quantum.expectation v (asOperator T) =
      (star (⇑v) ⬝ᵥ (T *ᵥ ⇑v)).re := by
  simp only [Bell.Quantum.expectation, asOperator_apply,
    EuclideanSpace.inner_eq_star_dotProduct, Matrix.toLpLin_apply]
  rw [dotProduct_comm]

theorem pure_nonneg (T : Operator n) (hT : T.PosSemidef) (v : Space n) :
    0 ≤ Bell.Quantum.expectation v (asOperator T) := by
  rw [pure_eq_dot]
  exact hT.re_dotProduct_nonneg _

theorem pure_add (S T : Operator n) (v : Space n) :
    Bell.Quantum.expectation v (asOperator (S + T)) =
      Bell.Quantum.expectation v (asOperator S) +
      Bell.Quantum.expectation v (asOperator T) := by
  simp [Bell.Quantum.expectation, asOperator, inner_add_right]

theorem pure_sub (S T : Operator n) (v : Space n) :
    Bell.Quantum.expectation v (asOperator (S - T)) =
      Bell.Quantum.expectation v (asOperator S) -
      Bell.Quantum.expectation v (asOperator T) := by
  simp [Bell.Quantum.expectation, asOperator, inner_sub_right]

theorem pure_one (v : Space n) :
    Bell.Quantum.expectation v (asOperator (1 : Operator n)) = ‖v‖ ^ 2 := by
  simp only [Bell.Quantum.expectation, asOperator, map_one, one_apply_eq_self]
  exact inner_self_eq_norm_sq (𝕜 := ℂ) v

omit [Fintype n] in
theorem povm_observable_hermitian (M : Bool → Operator n) (hM : BinaryPOVM M) :
    (observable M).IsHermitian :=
  (hM.positive true).isHermitian.sub (hM.positive false).isHermitian

theorem povm_eigenvalues_bound (M : Bool → Operator n) (hM : BinaryPOVM M) (i : n) :
    |(povm_observable_hermitian M hM).eigenvalues i| ≤ 1 := by
  let h := povm_observable_hermitian M hM
  let v := h.eigenvectorBasis i
  have hp := pure_nonneg (M true) (hM.positive true) v
  have hn := pure_nonneg (M false) (hM.positive false) v
  have hv : ‖v‖ = 1 := h.eigenvectorBasis.orthonormal.1 i
  have ht : Bell.Quantum.expectation v (asOperator (M false)) +
      Bell.Quantum.expectation v (asOperator (M true)) = 1 := by
    rw [← pure_add, hM.total, pure_one, hv, one_pow]
  have he : h.eigenvalues i = Bell.Quantum.expectation v (asOperator (observable M)) := by
    rw [pure_eq_dot]
    exact h.eigenvalues_eq i
  change |h.eigenvalues i| ≤ 1
  rw [he, observable, pure_sub, abs_le]
  constructor <;> linarith

theorem hermitian_contraction_of_eigenvalues (T : Operator n) (hT : T.IsHermitian)
    (h : ∀ i, |hT.eigenvalues i| ≤ 1) : ‖asOperator T‖ ≤ 1 := by
  rw [asOperator, Matrix.l2_opNorm_toEuclideanCLM]
  conv_lhs => rw [hT.spectral_theorem]
  rw [Unitary.conjStarAlgAut_apply, ← Unitary.coe_star,
    CStarRing.norm_mul_coe_unitary, CStarRing.norm_coe_unitary_mul,
    Matrix.l2_opNorm_diagonal]
  exact (pi_norm_le_iff_of_nonneg zero_le_one).2 fun i => by simpa using h i

theorem povm_observable_contraction (M : Bool → Operator n) (hM : BinaryPOVM M) :
    ‖asOperator (observable M)‖ ≤ 1 :=
  hermitian_contraction_of_eigenvalues _ (povm_observable_hermitian M hM)
    (povm_eigenvalues_bound M hM)


theorem mean_add (ρ S T : Operator n) : mean ρ (S + T) = mean ρ S + mean ρ T := by
  simp [mean, mul_add, Matrix.trace_add]

omit [DecidableEq n] in
theorem mean_sub (ρ S T : Operator n) : mean ρ (S - T) = mean ρ S - mean ρ T := by
  simp [mean, mul_sub, Matrix.trace_sub]

theorem mean_one (ρ : Operator n) (hρ : Density ρ) : mean ρ 1 = 1 := by
  simp [mean, hρ.trace_one]

theorem density_mean_nonneg (ρ T : Operator n) (hρ : Density ρ) (hT : T.PosSemidef) :
    0 ≤ mean ρ T := by
  rw [density_trace_mixture ρ T hρ]
  exact Finset.sum_nonneg fun i _ => mul_nonneg (hρ.positive.eigenvalues_nonneg i)
    (pure_nonneg T hT _)

def chshMatrix (A₀ A₁ B₀ B₁ : Operator n) : Operator n := A₀ * (B₀ + B₁) + A₁ * (B₀ - B₁)

theorem asOperator_chsh (A₀ A₁ B₀ B₁ : Operator n) :
    asOperator (chshMatrix A₀ A₁ B₀ B₁) =
      Bell.Quantum.chsh (asOperator A₀) (asOperator A₁) (asOperator B₀) (asOperator B₁) := by
  simp [asOperator, chshMatrix, Bell.Quantum.chsh, ContinuousLinearMap.mul_def]

theorem density_chsh_bound (ρ A₀ A₁ B₀ B₁ : Operator n) (hρ : Density ρ)
    (hA₀ : ‖asOperator A₀‖ ≤ 1) (hA₁ : ‖asOperator A₁‖ ≤ 1)
    (hB₀ : ‖asOperator B₀‖ ≤ 1) (hB₁ : ‖asOperator B₁‖ ≤ 1) :
    |mean ρ (chshMatrix A₀ A₁ B₀ B₁)| ≤ 2 * Real.sqrt 2 := by
  rw [density_trace_mixture ρ _ hρ, asOperator_chsh]
  exact Bell.Quantum.tsirelson_mixed_state_bound _ (density_weights ρ hρ) _ _ _ _
    hA₀ hA₁ hB₀ hB₁ _ (density_vectors_unit ρ hρ)

theorem density_povm_chsh_bound (ρ : Operator n) (hρ : Density ρ)
    (M N : Bool → Bool → Operator n)
    (hM : ∀ x, BinaryPOVM (M x)) (hN : ∀ y, BinaryPOVM (N y)) :
    |mean ρ (chshMatrix (observable (M false)) (observable (M true))
      (observable (N false)) (observable (N true)))| ≤ 2 * Real.sqrt 2 :=
  density_chsh_bound _ _ _ _ _ hρ (povm_observable_contraction _ (hM false))
    (povm_observable_contraction _ (hM true)) (povm_observable_contraction _ (hN false))
    (povm_observable_contraction _ (hN true))


theorem density_spectral_decomposition (ρ : Operator n) (hρ : Density ρ) :
    ρ = ∑ i, (hρ.positive.isHermitian.eigenvalues i : ℂ) •
      Matrix.vecMulVec (⇑(hρ.positive.isHermitian.eigenvectorBasis i))
        (star (⇑(hρ.positive.isHermitian.eigenvectorBasis i))) := by
  conv_lhs => rw [hρ.positive.isHermitian.spectral_theorem]
  rw [Unitary.conjStarAlgAut_apply]
  ext a b
  rw [Matrix.mul_apply]
  simp only [Matrix.mul_diagonal, Matrix.sum_apply, Matrix.smul_apply, smul_eq_mul,
    Matrix.vecMulVec_apply, Matrix.star_eq_conjTranspose, Matrix.conjTranspose_apply,
    Matrix.IsHermitian.eigenvectorUnitary_apply, Function.comp_apply, Pi.star_apply]
  apply Finset.sum_congr rfl
  intro i _
  change ((hρ.positive.isHermitian.eigenvectorBasis i) a *
    (hρ.positive.isHermitian.eigenvalues i : ℂ)) *
    star ((hρ.positive.isHermitian.eigenvectorBasis i) b) =
    (hρ.positive.isHermitian.eigenvalues i : ℂ) *
    ((hρ.positive.isHermitian.eigenvectorBasis i) a *
      star ((hρ.positive.isHermitian.eigenvectorBasis i) b))
  ring

omit [DecidableEq n] in
theorem density_trace_real (ρ T : Operator n) (hρ : Density ρ) (hT : T.IsHermitian) :
    (ρ * T).trace.im = 0 := by
  have h : star ((ρ * T).trace) = (ρ * T).trace := by
    rw [← Matrix.trace_conjTranspose, Matrix.conjTranspose_mul,
      hT.eq, hρ.positive.isHermitian.eq, Matrix.trace_mul_comm]
  have hi := congrArg Complex.im h
  simp only [Complex.star_def, Complex.conj_im] at hi
  linarith

end Bell.QuantumState



