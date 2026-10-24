import Bell.CliffordObservables
import Bell.MaximallyEntangled
import Bell.LocalGram

/-! Every finite real unit-vector Gram table has a constructed finite quantum
realization, including a density matrix, both local POVMs and every Born cell. -/
noncomputable section
open scoped BigOperators ComplexOrder
namespace Bell.GramQuantum
open Bell.Clifford Bell.CliffordObservables Bell.QuantumState

theorem effect_trace_product (d : ℕ) (u v : Fin d → ℝ) (a b : Bool) :
    Matrix.trace (effect d u a * effect d v b) =
      (Fintype.card (Carrier d) : ℂ)/4 *
        (1+(Bell.CHSH.sign a:ℂ)*(Bell.CHSH.sign b:ℂ)*∑ i, (u i:ℂ)*(v i:ℂ)) := by
  unfold effect
  simp only [mul_add,add_mul,one_mul,mul_one,smul_mul_assoc,
    mul_smul_comm,Matrix.trace_smul,Matrix.trace_add,linear_trace,linear_trace_product,
    Matrix.trace_one,smul_eq_mul]
  ring

theorem born_formula (d : ℕ) (u v : Fin d → ℝ) (a b : Bool) :
    mean (Bell.MaximallyEntangled.density (I:=Carrier d))
      (kron (effect d u a) (effect d v b).transpose) =
      (1+Bell.LocalGram.sign a*Bell.LocalGram.sign b*(∑ i, u i*v i))/4 := by
  rw [Bell.MaximallyEntangled.born_trace,effect_trace_product]
  have hc : (Fintype.card (Carrier d) : ℂ) ≠ 0 := by
    exact_mod_cast (Fintype.card_ne_zero (α:=Carrier d))
  have he : (Fintype.card (Carrier d):ℂ)/4 *
      (1+(Bell.CHSH.sign a:ℂ)*(Bell.CHSH.sign b:ℂ)*∑ i, (u i:ℂ)*(v i:ℂ)) /
      (Fintype.card (Carrier d):ℂ) =
      ((1+Bell.CHSH.sign a*Bell.CHSH.sign b*(∑ i, u i*v i))/4:ℝ) := by
    push_cast
    field_simp
  rw [he]
  simp only [Complex.ofReal_re]
  cases a <;> cases b <;> simp [Bell.CHSH.sign,Bell.LocalGram.sign]

structure Model {X Y : Type} (p : Bell.Behavior X Y Bool Bool) where
  dimension : ℕ
  state : Operator (Carrier dimension × Carrier dimension)
  alice : X → Bool → Operator (Carrier dimension)
  bob : Y → Bool → Operator (Carrier dimension)
  density : Density state
  alice_povm : ∀ x, BinaryPOVM (alice x)
  bob_povm : ∀ y, BinaryPOVM (bob y)
  reproduces : ∀ x y a b, mean state (kron (alice x a) (bob y b)) = p x y a b

def model {X Y : Type} (d : ℕ) (u : X → Fin d → ℝ) (v : Y → Fin d → ℝ)
    (hu : ∀ x, ∑ i, u x i^2=1) (hv : ∀ y, ∑ i, v y i^2=1) :
    Model (Bell.LocalGram.table (fun x y => ∑ i, u x i*v y i)) where
  dimension := d
  state := Bell.MaximallyEntangled.density
  alice := fun x => effect d (u x)
  bob := fun y b => (effect d (v y) b).transpose
  density := Bell.MaximallyEntangled.density_valid
  alice_povm := fun x => local_povm d (u x) (hu x)
  bob_povm := fun y => Bell.MaximallyEntangled.transpose_povm _ (local_povm d (v y) (hv y))
  reproduces := fun x y a b => born_formula d (u x) (v y) a b

theorem realization {X Y : Type} (d : ℕ) (u : X → Fin d → ℝ) (v : Y → Fin d → ℝ)
    (hu : ∀ x, ∑ i, u x i^2=1) (hv : ∀ y, ∑ i, v y i^2=1) :
    Nonempty (Model (Bell.LocalGram.table (fun x y => ∑ i, u x i*v y i))) :=
  ⟨model d u v hu hv⟩

theorem model_nonnegative {X Y : Type} {p : Bell.Behavior X Y Bool Bool}
    (M : Model p) (x : X) (y : Y) (a b : Bool) : 0 ≤ p x y a b := by
  rw [← M.reproduces]
  apply density_mean_nonneg _ _ M.density
  simpa only [Matrix.kronecker] using (M.alice_povm x).positive a |>.kronecker ((M.bob_povm y).positive b)

end Bell.GramQuantum
