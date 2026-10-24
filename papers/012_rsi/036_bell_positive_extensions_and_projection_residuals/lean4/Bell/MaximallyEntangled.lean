import Bell.Clifford

/-! An explicit normalized maximally entangled density and its trace identity.
The density uses 1/d directly, so no square root is required for its entries. -/
noncomputable section
open scoped BigOperators ComplexOrder ComplexConjugate
namespace Bell.MaximallyEntangled
open Bell.QuantumState
variable {I : Type} [Fintype I] [DecidableEq I] [Nonempty I]

def vector (i : I × I) : ℂ := if i.1=i.2 then 1 else 0
def density : Operator (I × I) :=
  (1/(Fintype.card I : ℂ)) • Matrix.vecMulVec vector (star vector)

theorem density_positive : (density (I:=I)).PosSemidef := by
  apply (Matrix.posSemidef_vecMulVec_self_star (vector (I:=I))).smul
  have h : (0:ℝ) ≤ 1/(Fintype.card I:ℝ) := by positivity
  have hc : (0:ℂ) ≤ ((1/(Fintype.card I:ℝ):ℝ):ℂ) := by exact_mod_cast h
  simpa only [Complex.ofReal_div,Complex.ofReal_one,Complex.ofReal_natCast] using hc

theorem density_trace : Matrix.trace (density (I:=I)) = 1 := by
  have hc : (Fintype.card I : ℂ) ≠ 0 := by exact_mod_cast (Fintype.card_ne_zero (α:=I))
  simp [density,Matrix.trace,Matrix.diag,Matrix.vecMulVec,
    vector,Fintype.sum_prod_type,hc]

theorem density_valid : Density (density (I:=I)) := ⟨density_positive,density_trace⟩

omit [Nonempty I] in
theorem density_apply (i j : I × I) : density (I:=I) i j =
    (1/(Fintype.card I:ℂ))*(if i.1=i.2 then 1 else 0)*(if j.1=j.2 then 1 else 0) := by
  simp [density,Matrix.smul_apply,smul_eq_mul,Matrix.vecMulVec_apply,vector]

omit [Nonempty I] in
theorem born_trace (A B : Operator I) :
    mean (density (I:=I)) (Bell.Clifford.kron A B.transpose) =
      ((Matrix.trace (A*B))/(Fintype.card I : ℂ)).re := by
  unfold mean
  congr 1
  simp only [Matrix.trace,Matrix.diag,Matrix.mul_apply,Fintype.sum_prod_type,density_apply,
    Bell.Clifford.kron,Matrix.kroneckerMap_apply,Matrix.transpose_apply]
  simp only [ite_mul,mul_ite,zero_mul,mul_one,mul_zero,
    Finset.sum_ite_eq,Finset.mem_univ,ite_true]
  simp only [Finset.sum_ite_irrel,Finset.sum_const_zero,Finset.sum_ite_eq,Finset.mem_univ,ite_true]
  simp only [← Finset.mul_sum]
  rw [Finset.sum_comm]
  ring

omit [Fintype I] [Nonempty I] in
theorem transpose_povm (M : Bool → Operator I) (hM : BinaryPOVM M) :
    BinaryPOVM (fun a => (M a).transpose) := by
  refine ⟨fun a => (hM.positive a).transpose,?_⟩
  rw [← Matrix.transpose_add,hM.total,Matrix.transpose_one]

end Bell.MaximallyEntangled
