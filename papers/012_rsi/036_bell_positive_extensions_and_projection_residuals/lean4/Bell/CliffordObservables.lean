import Bell.Clifford

/-! The linear Clifford map and binary projective measurements. -/
noncomputable section
open scoped BigOperators ComplexConjugate ComplexOrder
namespace Bell.CliffordObservables
open Bell.Clifford

def linear (n : ℕ) (u : Fin n → ℝ) : Matrix (Carrier n) (Carrier n) ℂ :=
  ∑ i, (u i : ℂ) • gamma n i

theorem gamma_anticommutator (n : ℕ) (i j : Fin n) :
    gamma n i * gamma n j + gamma n j * gamma n i =
      if i=j then (2:ℂ) • (1 : Matrix (Carrier n) (Carrier n) ℂ) else 0 := by
  split_ifs with h
  · subst j; rw [gamma_square,two_smul]
  · rw [gamma_anticommute n i j h]; simp

theorem linear_hermitian (n : ℕ) (u : Fin n → ℝ) :
    (linear n u).conjTranspose = linear n u := by
  simp [linear,Matrix.conjTranspose_sum,Matrix.conjTranspose_smul,gamma_hermitian]

theorem linear_trace (n : ℕ) (u : Fin n → ℝ) : Matrix.trace (linear n u) = 0 := by
  simp only [linear,Matrix.trace_sum,Matrix.trace_smul,gamma_trace,smul_zero,Finset.sum_const_zero]

theorem linear_product (n : ℕ) (u v : Fin n → ℝ) :
    linear n u * linear n v =
      ∑ i, ∑ j, ((u i : ℂ)*(v j : ℂ)) • (gamma n i * gamma n j) := by
  simp only [linear,Finset.sum_mul,Finset.mul_sum,smul_mul_smul]
  rw [Finset.sum_comm]

theorem linear_anticommutator (n : ℕ) (u v : Fin n → ℝ) :
    linear n u * linear n v + linear n v * linear n u =
      (2*(∑ i, (u i : ℂ)*(v i : ℂ))) • (1 : Matrix (Carrier n) (Carrier n) ℂ) := by
  rw [linear_product,linear_product]
  have hs : (∑ i, ∑ j, ((v i : ℂ)*(u j : ℂ)) • (gamma n i * gamma n j)) =
      ∑ i, ∑ j, ((u i : ℂ)*(v j : ℂ)) • (gamma n j * gamma n i) := by
    rw [Finset.sum_comm]
    simp only [mul_comm (v _ : ℂ)]
  rw [hs,← Finset.sum_add_distrib]
  simp_rw [← Finset.sum_add_distrib,← smul_add,gamma_anticommutator]
  simp only [smul_ite,smul_smul,smul_zero,Finset.sum_ite_eq,Finset.mem_univ,ite_true]
  rw [← Finset.sum_smul,← Finset.sum_mul]
  congr 1
  ring

theorem linear_square (n : ℕ) (u : Fin n → ℝ) (hu : ∑ i, u i^2 = 1) :
    linear n u * linear n u = 1 := by
  have h := linear_anticommutator n u u
  have he : (∑ i, (u i : ℂ)*(u i : ℂ)) = 1 := by
    exact_mod_cast (show (∑ i, u i*u i)=1 by simpa only [← pow_two] using hu)
  rw [he,mul_one,two_smul] at h
  ext i j
  have he := congrFun (congrFun h i) j
  simp only [Matrix.add_apply] at he
  linear_combination (1/2:ℂ) * he

theorem linear_trace_product (n : ℕ) (u v : Fin n → ℝ) :
    Matrix.trace (linear n u * linear n v) =
      (Fintype.card (Carrier n) : ℂ) * ∑ i, (u i : ℂ)*(v i : ℂ) := by
  rw [linear_product]
  simp only [Matrix.trace_sum,Matrix.trace_smul,gamma_trace_pair,smul_eq_mul,
    mul_ite,mul_zero,Finset.sum_ite_eq,Finset.mem_univ,ite_true]
  rw [← Finset.sum_mul,mul_comm]

def effect (n : ℕ) (u : Fin n → ℝ) (a : Bool) : Matrix (Carrier n) (Carrier n) ℂ :=
  (1/2:ℂ) • (1+(Bell.CHSH.sign a:ℂ) • linear n u)

theorem effect_hermitian (n : ℕ) (u : Fin n → ℝ) (a : Bool) :
    (effect n u a).conjTranspose = effect n u a := by
  simp [effect,Matrix.conjTranspose_smul,linear_hermitian]

theorem effect_projector (n : ℕ) (u : Fin n → ℝ) (hu : ∑ i, u i^2=1) (a : Bool) :
    effect n u a * effect n u a = effect n u a := by
  have hs := linear_square n u hu
  cases a <;> dsimp [effect,Bell.CHSH.sign]
  all_goals
    simp only [mul_add,add_mul,one_mul,mul_one,
      smul_mul_assoc,mul_smul_comm,smul_smul,hs]
    ext i j
    simp only [neg_one_smul,Matrix.smul_apply,Matrix.add_apply,Matrix.neg_apply,
      smul_eq_mul]
    ring

theorem effects_total (n : ℕ) (u : Fin n → ℝ) :
    effect n u false + effect n u true = 1 := by
  ext i j
  norm_num [effect,Bell.CHSH.sign,Matrix.smul_apply,smul_eq_mul]
  ring

theorem local_povm (n : ℕ) (u : Fin n → ℝ) (hu : ∑ i, u i^2=1) :
    Bell.QuantumState.BinaryPOVM (effect n u) := by
  refine ⟨fun a => ?_,effects_total n u⟩
  have h := Matrix.posSemidef_conjTranspose_mul_self (effect n u a)
  rw [effect_hermitian,effect_projector n u hu] at h
  exact h

end Bell.CliffordObservables
