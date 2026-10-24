import Bell.Repair
import Mathlib.LinearAlgebra.Isomorphisms
import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.Analysis.Normed.Module.FiniteDimension

noncomputable section
open scoped BigOperators
open Set Metric
namespace Bell.SignedDuality
attribute [local instance] Classical.propDecidable
open Bell.LinearProgramming Bell.ConvexDistance

/-- A kernel-annihilating functional factors through a finite linear observation map. -/
theorem factor_functional {E F : Type} [AddCommGroup E] [Module ℝ E]
    [AddCommGroup F] [Module ℝ F] (T : E →ₗ[ℝ] F) (g : E →ₗ[ℝ] ℝ)
    (hg : T.ker ≤ g.ker) : ∃ y : F →ₗ[ℝ] ℝ, ∀ q, y (T q) = g q := by
  let r := (T.ker.liftQ g hg).comp T.quotKerEquivRange.symm.toLinearMap
  obtain ⟨y,hy⟩ := r.exists_extend
  refine ⟨y, fun q => ?_⟩
  have hh := LinearMap.congr_fun hy ⟨T q, T.mem_range_self q⟩
  change y (T q) = (T.ker.liftQ g hg) (T.quotKerEquivRange.symm ⟨T q, _⟩) at hh
  rw [T.quotKerEquivRange_symm_apply_image q _] at hh
  change y (T q) = g q at hh
  exact hh

/-- An inhabited affine fiber has an attained l1 minimum and an attained dual functional. -/
theorem affine_norm_duality {G F : Type} [Fintype G]
    [NormedAddCommGroup F] [NormedSpace ℝ F]
    (T : Vec G →L[ℝ] F) (p : F) (hne : ∃ q, T q = p) :
    ∃ q : Vec G, ∃ y : F →ₗ[ℝ] ℝ, T q = p ∧
      (∀ u, |y (T u)| ≤ ‖u‖) ∧ y p = ‖q‖ ∧
      (∀ u, T u = p → ‖q‖ ≤ ‖u‖) := by
  let K : Set (Vec G) := {q | T q = p}
  have hc : IsClosed K := isClosed_eq T.continuous continuous_const
  have hconv : Convex ℝ K := (convex_singleton p).linear_preimage T.toLinearMap
  obtain ⟨q,hq,f,hf,hs,he,hd⟩ := attained_duality_closed hc hne hconv 0
  change T q = p at hq
  have hker : T.toLinearMap.ker ≤ (-f).toLinearMap.ker := by
    intro u hu
    have hu' : T u = 0 := hu
    have hp : q + u ∈ K := by simp [K, map_add, hu', hq]
    have hm : q - u ∈ K := by simp [K, map_sub, hu', hq]
    have h1 := hs (q+u) hp
    have h2 := hs (q-u) hm
    simp only [map_add, map_sub] at h1 h2
    change -f u = 0
    linarith
  obtain ⟨y,hy⟩ := factor_functional T.toLinearMap (-f).toLinearMap hker
  change ∀ u, y (T u) = -f u at hy
  have hyq : y p = ‖q‖ := by
    rw [← hq, hy]
    have hh := he.trans hd.symm
    simpa using hh
  refine ⟨q,y,hq,?_,hyq,?_⟩
  · intro u; rw [hy]; simpa using hf u
  · intro u hu
    rw [← hyq, ← hu]
    exact (le_abs_self _).trans (by rw [hy]; simpa using hf u)

variable {I G : Type} [Fintype I] [Fintype G]

def negativeMass (q : G → ℝ) : ℝ := ∑ g, max (-q g) 0

theorem signed_norm_identity (q : G → ℝ) (hq : ∑ g, q g = 1) :
    ∑ g, |q g| = 1 + 2 * negativeMass q := by
  have hp (r : ℝ) : |r| = r + 2 * max (-r) 0 := by
    rcases le_total 0 r with h | h
    · rw [abs_of_nonneg h, max_eq_right (neg_nonpos.mpr h)]; ring
    · rw [abs_of_nonpos h, max_eq_left (neg_nonneg.mpr h)]; ring
  simp_rw [hp, Finset.sum_add_distrib, ← Finset.mul_sum, hq, negativeMass]

def augmentedMap (A : G → I → ℝ) : Vec G →L[ℝ] ((I → ℝ) × ℝ) :=
  (((∑ g, (LinearMap.proj (R := ℝ) g).smulRight (A g)).prod
    (∑ g, LinearMap.proj (R := ℝ) g)).comp
      (WithLp.linearEquiv 1 ℝ (G → ℝ)).toLinearMap).toContinuousLinearMap

omit [Fintype I] in
theorem augmentedMap_apply (A : G → I → ℝ) (q : Vec G) :
    augmentedMap A q = (mix A (fun g => q g), ∑ g, q g) := by
  apply Prod.ext
  · funext i
    simp [augmentedMap, mix, Finset.sum_apply]
  · simp [augmentedMap]

/-- Signed normalized extensions: attained minimum negative mass and the full LP dual. -/
theorem negative_mass_duality (A : G → I → ℝ) (p : I → ℝ)
    (hne : ∃ q : G → ℝ, mix A q = p ∧ ∑ g, q g = 1) :
    ∃ (q : G → ℝ) (α : I → ℝ) (β : ℝ), mix A q = p ∧ (∑ g, q g = 1) ∧
      (∀ g, -1 ≤ pairing α (A g) + β ∧ pairing α (A g) + β ≤ 0) ∧
      pairing α p + β = negativeMass q ∧
      (∀ q', mix A q' = p → (∑ g, q' g = 1) → negativeMass q ≤ negativeMass q') := by
  classical
  have hne' : ∃ q : Vec G, augmentedMap A q = (p,1) := by
    obtain ⟨q,hq,hs⟩ := hne
    exact ⟨WithLp.toLp 1 q, by simp [augmentedMap_apply, hq, hs]⟩
  obtain ⟨q,y,hq,hy,he,hopt⟩ := affine_norm_duality (augmentedMap A) (p,1) hne'
  have hq' : mix A (fun g => q g) = p ∧ ∑ g, q g = 1 := by
    simpa only [augmentedMap_apply, Prod.mk.injEq] using hq
  let α : I → ℝ := fun i => y (Pi.single i 1, 0) / 2
  let β : ℝ := (y (0,1) - 1) / 2
  have hcoord (v : I → ℝ) : y (v,1) = 2 * (pairing α v + β) + 1 := by
    have hv : (v, (1 : ℝ)) = (∑ i, v i • (Pi.single i 1, (0 : ℝ))) + (0,1) := by
      apply Prod.ext
      · ext i; simp [Prod.fst_sum, Pi.single_apply, Finset.sum_apply]
      · simp [Prod.snd_sum]
    rw [hv, map_add, map_sum]
    simp only [map_smul, smul_eq_mul, pairing, α, β]
    rw [mul_add, Finset.mul_sum]
    have hh : (∑ x, 2 * (y (Pi.single x 1, 0) / 2 * v x)) =
        ∑ x, v x * y (Pi.single x 1,0) := by
      apply Finset.sum_congr rfl
      intro i _; ring
    rw [hh]
    ring
  have hb (g : G) : -1 ≤ pairing α (A g) + β ∧ pairing α (A g) + β ≤ 0 := by
    have hh := hy (PiLp.single 1 g 1)
    have hv : augmentedMap A (PiLp.single 1 g 1) = (A g,1) := by
      ext i <;> simp [augmentedMap_apply, mix, PiLp.single_apply]
    rw [hv, PiLp.norm_single] at hh
    have hh' : |y (A g,1)| ≤ 1 := by simpa using hh
    rw [hcoord] at hh'
    obtain ⟨h1,h2⟩ := abs_le.mp hh'
    constructor <;> linarith
  have hnorm : ‖q‖ = 1 + 2 * negativeMass (fun g => q g) := by
    simpa only [PiLp.norm_eq_of_L1, Real.norm_eq_abs] using signed_norm_identity (fun g => q g) hq'.2
  refine ⟨fun g => q g, α, β, hq'.1, hq'.2, hb, ?_, ?_⟩
  · rw [hcoord, hnorm] at he
    linarith
  · intro q' hmix hsum
    have hh := hopt (WithLp.toLp 1 q') (by simp [augmentedMap_apply, hmix, hsum])
    rw [hnorm] at hh
    have hs : ‖WithLp.toLp 1 q'‖ = 1 + 2 * negativeMass q' := by
      simpa only [PiLp.norm_eq_of_L1, Real.norm_eq_abs, PiLp.toLp_apply] using signed_norm_identity q' hsum
    rw [hs] at hh
    linarith

theorem negative_mass_weak_duality (A : G → I → ℝ) (p α : I → ℝ)
    (q : G → ℝ) (β : ℝ) (hmix : mix A q = p) (hs : ∑ g, q g = 1)
    (hdual : ∀ g, -1 ≤ pairing α (A g) + β ∧ pairing α (A g) + β ≤ 0) :
    pairing α p + β ≤ negativeMass q := by
  have he : pairing α p + β = ∑ g, q g * (pairing α (A g) + β) := by
    rw [← hmix]
    simp only [pairing, mix, Finset.mul_sum, mul_add, Finset.sum_add_distrib,
      ← Finset.sum_mul, hs, one_mul]
    congr 1
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro g _
    apply Finset.sum_congr rfl
    intro i _; ring
  rw [he]
  apply Finset.sum_le_sum
  intro g _
  by_cases hq : 0 ≤ q g
  · exact (mul_nonpos_of_nonneg_of_nonpos hq (hdual g).2).trans (le_max_right _ _)
  · have hn : q g ≤ 0 := (lt_of_not_ge hq).le
    have hh := mul_le_mul_of_nonpos_left (hdual g).1 hn
    calc
      q g * (pairing α (A g) + β) ≤ -q g := by simpa using hh
      _ ≤ max (-q g) 0 := le_max_left _ _

theorem negative_mass_dual_optimal (A : G → I → ℝ) (p α : I → ℝ)
    (q : G → ℝ) (β : ℝ) (hmix : mix A q = p) (hs : ∑ g, q g = 1)
    (he : pairing α p + β = negativeMass q) :
    ∀ α' β', (∀ g, -1 ≤ pairing α' (A g) + β' ∧ pairing α' (A g) + β' ≤ 0) →
      pairing α' p + β' ≤ pairing α p + β := by
  intro α' β' hdual
  rw [he]
  exact negative_mass_weak_duality A p α' q β' hmix hs hdual

/-- The signed LP theorem instantiated with Bell's actual deterministic marginal map. -/
theorem bell_negative_mass_duality {X Y A B : Type}
    [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
    (p : Bell.Behavior X Y A B)
    (hne : ∃ q : Bell.Assignment X Y A B → ℝ, Bell.marginal q = p ∧ ∑ g, q g = 1) :
    ∃ (q : Bell.Assignment X Y A B → ℝ) (α : Bell.Repair.Coordinate X Y A B → ℝ) (β : ℝ),
      Bell.marginal q = p ∧ (∑ g, q g = 1) ∧
      (∀ g, -1 ≤ pairing α (Bell.Repair.vertex g) + β ∧ pairing α (Bell.Repair.vertex g) + β ≤ 0) ∧
      pairing α (Bell.Repair.flatten p) + β = negativeMass q ∧
      (∀ q', Bell.marginal q' = p → (∑ g, q' g = 1) → negativeMass q ≤ negativeMass q') := by
  classical
  have hne' : ∃ q, mix Bell.Repair.vertex q = Bell.Repair.flatten p ∧ ∑ g, q g = 1 := by
    obtain ⟨q,hq,hs⟩ := hne
    exact ⟨q, by rw [← Bell.Repair.marginal_eq_mix, hq], hs⟩
  obtain ⟨q,α,β,hq,hs,hdual,he,hopt⟩ := negative_mass_duality Bell.Repair.vertex (Bell.Repair.flatten p) hne'
  have hm : Bell.marginal q = p := by
    rw [← Bell.Repair.marginal_eq_mix] at hq
    funext x y a b
    exact congrFun hq ((x,y),(a,b))
  refine ⟨q,α,β,hm,hs,hdual,he,?_⟩
  intro q' hq' hs'
  exact hopt q' (by rw [← Bell.Repair.marginal_eq_mix, hq']) hs'

/-- Eliminate the normalization offset: the optimal signed witness has vertex spread at most one. -/
theorem bell_signed_spread_duality {X Y A B : Type}
    [Fintype X] [Fintype Y] [Fintype A] [Fintype B] [Nonempty A] [Nonempty B]
    (p : Bell.Behavior X Y A B)
    (hne : ∃ q : Bell.Assignment X Y A B → ℝ, Bell.marginal q = p ∧ ∑ g, q g = 1) :
    ∃ (q : Bell.Assignment X Y A B → ℝ) (α : Bell.Repair.Coordinate X Y A B → ℝ),
      Bell.marginal q = p ∧ (∑ g, q g = 1) ∧
      (∀ g, Bell.Repair.vertexSupport α - pairing α (Bell.Repair.vertex g) ≤ 1) ∧
      pairing α (Bell.Repair.flatten p) - Bell.Repair.vertexSupport α = negativeMass q ∧
      (∀ q', Bell.marginal q' = p → (∑ g, q' g = 1) → negativeMass q ≤ negativeMass q') := by
  obtain ⟨q,α,β,hq,hs,hdual,he,hopt⟩ := bell_negative_mass_duality p hne
  have hmax : Bell.Repair.vertexSupport α ≤ -β := by
    apply Finset.sup'_le
    intro g _
    have hh := (hdual g).2
    linarith
  have hspread : ∀ g, Bell.Repair.vertexSupport α - pairing α (Bell.Repair.vertex g) ≤ 1 := by
    intro g
    have hh := (hdual g).1
    linarith
  have hnew : ∀ g, -1 ≤ pairing α (Bell.Repair.vertex g) + -Bell.Repair.vertexSupport α ∧
      pairing α (Bell.Repair.vertex g) + -Bell.Repair.vertexSupport α ≤ 0 := by
    intro g
    have h1 := hspread g
    have h2 := Bell.Repair.vertex_le_support α g
    constructor <;> linarith
  have hweak := negative_mass_weak_duality Bell.Repair.vertex (Bell.Repair.flatten p) α q
    (-Bell.Repair.vertexSupport α) (by rw [← Bell.Repair.marginal_eq_mix, hq]) hs hnew
  exact ⟨q,α,hq,hs,hspread,by linarith,hopt⟩

end Bell.SignedDuality
