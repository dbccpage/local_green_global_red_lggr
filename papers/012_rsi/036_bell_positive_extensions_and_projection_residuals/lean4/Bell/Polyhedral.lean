import Bell.ConvexDistance
import Mathlib.LinearAlgebra.Pi

noncomputable section
open scoped BigOperators
open Set
namespace Bell.Polyhedral

/-- Eliminate one real variable from a finite system of weak inequalities. -/
theorem exists_scalar_iff {I : Type} [Fintype I] (c d : I → ℝ) :
    (∃ t : ℝ, ∀ i, c i * t ≤ d i) ↔
    (∀ i, c i = 0 → 0 ≤ d i) ∧
      (∀ i j, c i < 0 → 0 < c j → d i / c i ≤ d j / c j) := by
  classical
  constructor
  · rintro ⟨t, ht⟩
    refine ⟨fun i hi => by simpa [hi] using ht i, ?_⟩
    intro i j hi hj
    exact ((div_le_iff_of_neg hi).2 (by simpa [mul_comm] using ht i)).trans
      ((le_div_iff₀ hj).2 (by simpa [mul_comm] using ht j))
  · rintro ⟨hz, hpair⟩
    let lower := Finset.univ.filter (fun i => c i < 0)
    by_cases hn : lower.Nonempty
    · obtain ⟨k, hk, hmax⟩ := lower.exists_max_image (fun i => d i / c i) hn
      refine ⟨d k / c k, fun i => ?_⟩
      rcases lt_trichotomy (c i) 0 with hi | hi | hi
      · simpa only [mul_comm] using (div_le_iff_of_neg hi).mp
          (hmax i (by simp [lower, hi]))
      · simpa [hi] using hz i hi
      · simpa only [mul_comm] using (le_div_iff₀ hi).mp
          (hpair k i (by simpa [lower] using hk) hi)
    · let upper := Finset.univ.filter (fun i => 0 < c i)
      by_cases hp : upper.Nonempty
      · obtain ⟨k, hk, hmin⟩ := upper.exists_min_image (fun i => d i / c i) hp
        refine ⟨d k / c k, fun i => ?_⟩
        have hci : 0 ≤ c i := by
          by_contra h
          exact hn ⟨i, by simp [lower, lt_of_not_ge h]⟩
        rcases hci.eq_or_lt with hi | hi
        · simpa [← hi] using hz i hi.symm
        · simpa only [mul_comm] using (le_div_iff₀ hi).mp
            (hmin i (by simp [upper, hi]))
      · refine ⟨0, fun i => ?_⟩
        have hi : c i = 0 := by
          rcases lt_trichotomy (c i) 0 with h | h | h
          · exact False.elim (hn ⟨i, by simp [lower, h]⟩)
          · exact h
          · exact False.elim (hp ⟨i, by simp [upper, h]⟩)
        simpa using hz i hi

variable {E : Type} [AddCommGroup E] [Module ℝ E]

def IsPolyhedron (S : Set E) : Prop :=
  ∃ n : ℕ, ∃ a : Fin n → E →ₗ[ℝ] ℝ, ∃ b : Fin n → ℝ,
    S = {x | ∀ i, a i x ≤ b i}

theorem of_finite_system {I : Type} [Fintype I] (a : I → E →ₗ[ℝ] ℝ) (b : I → ℝ) :
    IsPolyhedron {x | ∀ i, a i x ≤ b i} := by
  classical
  refine ⟨Fintype.card I, fun i => a ((Fintype.equivFin I).symm i),
    fun i => b ((Fintype.equivFin I).symm i), ?_⟩
  ext x
  simp only [mem_ofPred_eq]
  exact (Fintype.equivFin I).symm.surjective.forall

theorem preimage {F : Type} [AddCommGroup F] [Module ℝ F]
    {S : Set E} (hS : IsPolyhedron S) (L : F →ₗ[ℝ] E) : IsPolyhedron (L ⁻¹' S) := by
  obtain ⟨n, a, b, rfl⟩ := hS
  exact ⟨n, fun i => (a i).comp L, b, rfl⟩

theorem projection_one {S : Set (E × ℝ)} (hS : IsPolyhedron S) :
    IsPolyhedron {x | ∃ t : ℝ, (x,t) ∈ S} := by
  classical
  obtain ⟨n, a, b, rfl⟩ := hS
  let c : Fin n → ℝ := fun i => a i (0,1)
  let L : Fin n → E →ₗ[ℝ] ℝ := fun i => (a i).comp (LinearMap.inl ℝ E ℝ)
  let A : Fin n ⊕ (Fin n × Fin n) → E →ₗ[ℝ] ℝ := Sum.elim
    (fun i => if c i = 0 then L i else 0)
    (fun ij => if c ij.1 < 0 ∧ 0 < c ij.2 then
      (c ij.2)⁻¹ • L ij.2 - (c ij.1)⁻¹ • L ij.1 else 0)
  let B : Fin n ⊕ (Fin n × Fin n) → ℝ := Sum.elim
    (fun i => if c i = 0 then b i else 0)
    (fun ij => if c ij.1 < 0 ∧ 0 < c ij.2 then
      b ij.2 / c ij.2 - b ij.1 / c ij.1 else 0)
  have he (x : E) (t : ℝ) (i : Fin n) : a i (x,t) = L i x + c i * t := by
    have hv : (x,t) = (x,0) + t • (0,1) := by simp
    rw [hv, map_add, map_smul]
    simp [L, c, mul_comm]
  have hset : {x | ∃ t : ℝ, ∀ i, a i (x,t) ≤ b i} = {x | ∀ k, A k x ≤ B k} := by
    ext x
    simp only [mem_ofPred_eq]
    have hred : (∃ t : ℝ, ∀ i, a i (x,t) ≤ b i) ↔
        ∃ t : ℝ, ∀ i, c i * t ≤ b i - L i x := by
      simp_rw [he, le_sub_iff_add_le, add_comm (L _ x)]
    rw [hred, exists_scalar_iff]
    simp only [Sum.forall, Prod.forall, A, B, Sum.elim_inl, Sum.elim_inr]
    constructor
    · rintro ⟨hz, hp⟩
      constructor
      · intro i; split_ifs with hi
        · exact sub_nonneg.mp (hz i hi)
        · simp
      · intro i j; split_ifs with hij
        · have hh := hp i j hij.1 hij.2
          simp only [LinearMap.sub_apply, LinearMap.smul_apply, smul_eq_mul, div_eq_mul_inv]
          simp only [div_eq_mul_inv] at hh
          nlinarith
        · simp
    · rintro ⟨hz, hp⟩
      constructor
      · intro i hi
        have hh := hz i
        simp only [hi, ite_true] at hh
        exact sub_nonneg.mpr hh
      · intro i j hi hj
        have hh := hp i j
        simp only [hi, hj, and_self, ite_true, LinearMap.sub_apply, LinearMap.smul_apply, smul_eq_mul, div_eq_mul_inv] at hh
        simp only [div_eq_mul_inv]
        nlinarith
  rw [show {x | ∃ t : ℝ, (x,t) ∈ {x | ∀ i, a i x ≤ b i}} =
    {x | ∃ t : ℝ, ∀ i, a i (x,t) ≤ b i} from rfl, hset]
  exact of_finite_system A B

end Bell.Polyhedral
