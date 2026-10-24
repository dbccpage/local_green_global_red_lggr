import Bell.ConvexDistance
import Mathlib.Analysis.Normed.Module.FiniteDimension

noncomputable section
open scoped Topology
open Set Metric Filter
namespace Bell.TangentCone
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable {I : Type*} [Fintype I]

def feasible (a : I → E →L[ℝ] ℝ) (b : I → ℝ) : Set E :=
  {x | ∀ i, a i x ≤ b i}

def tangent (a : I → E →L[ℝ] ℝ) (b : I → ℝ) (p : E) : Set E :=
  {u | ∀ i, a i p = b i → a i u ≤ 0}

omit [Fintype I] in
theorem tangent_closed (a : I → E →L[ℝ] ℝ) (b : I → ℝ) (p : E) :
    IsClosed (tangent a b p) := by
  have he : tangent a b p = ⋂ i, ⋂ (_ : a i p = b i), {u | a i u ≤ 0} := by
    ext u; simp [tangent]
  rw [he]
  exact isClosed_iInter fun i => isClosed_iInter fun _ =>
    isClosed_le (a i).continuous continuous_const

omit [Fintype I] in
theorem tangent_zero (a : I → E →L[ℝ] ℝ) (b : I → ℝ) (p : E) :
    (0 : E) ∈ tangent a b p := by simp [tangent]

omit [Fintype I] in
theorem displacement_mem_tangent (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p y : E) (hy : y ∈ feasible a b) : y - p ∈ tangent a b p := by
  intro i hi
  simp only [map_sub, hi]
  exact sub_nonpos.mpr (hy i)

omit [Fintype I] in
theorem tangent_smul (a : I → E →L[ℝ] ℝ) (b : I → ℝ) (p u : E)
    (hu : u ∈ tangent a b p) (t : ℝ) (ht : 0 ≤ t) : t • u ∈ tangent a b p := by
  intro i hi
  simpa only [map_smul, smul_eq_mul] using mul_nonpos_of_nonneg_of_nonpos ht (hu i hi)

/-- Finite inactive constraints have a common positive slack window. -/
theorem tangent_ray_feasible (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p u : E) (hp : p ∈ feasible a b) (hu : u ∈ tangent a b p) :
    ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t → p + t • u ∈ feasible a b := by
  have hi : ∀ i, ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t → a i (p + t • u) ≤ b i := by
    intro i
    by_cases he : a i p = b i
    · exact Filter.Eventually.of_forall fun t ht => by
        simp only [map_add, map_smul, smul_eq_mul, he]
        exact add_le_of_nonpos_right (mul_nonpos_of_nonneg_of_nonpos ht (hu i he))
    · have hs : a i p < b i := lt_of_le_of_ne (hp i) he
      have hc : Continuous (fun t : ℝ => a i (p + t • u)) :=
        (a i).continuous.comp (continuous_const.add (continuous_id.smul continuous_const))
      have hh : ∀ᶠ t : ℝ in 𝓝 0, a i (p + t • u) < b i :=
        (isOpen_Iio.preimage hc).mem_nhds (by simpa using hs)
      exact hh.mono fun _ h _ => h.le
  exact (Filter.eventually_all.mpr hi).mono fun _ ht hnon i => ht i hnon

omit [Fintype I] in
theorem ray_lower (a : I → E →L[ℝ] ℝ) (b : I → ℝ) (p v : E)
    (hp : p ∈ feasible a b) (t : ℝ) (ht : 0 ≤ t) :
    t * infDist v (tangent a b p) ≤ infDist (p + t • v) (feasible a b) := by
  by_cases hz : t = 0
  · simp [hz, infDist_nonneg]
  have htpos : 0 < t := lt_of_le_of_ne ht (Ne.symm hz)
  apply (le_infDist ⟨p, hp⟩).2
  intro y hy
  have hu := tangent_smul a b p (y-p) (displacement_mem_tangent a b p y hy)
    t⁻¹ (inv_nonneg.mpr ht)
  have hdist := mul_le_mul_of_nonneg_left (infDist_le_dist_of_mem hu (x := v)) ht
  have he : p + t • v - y = t • (v - t⁻¹ • (y-p)) := by
    rw [smul_sub, smul_smul, mul_inv_cancel₀ hz, one_smul]
    abel
  simpa only [dist_eq_norm, he, norm_smul, Real.norm_eq_abs, abs_of_nonneg ht] using hdist

/-- Exact distance on a short ray, with a nearest tangent vector constructed from closedness. -/
theorem ray_distance [ProperSpace E] (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p v : E) (hp : p ∈ feasible a b) :
    ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t →
      infDist (p + t • v) (feasible a b) = t * infDist v (tangent a b p) := by
  obtain ⟨u, hu, hd⟩ := (tangent_closed a b p).exists_infDist_eq_dist
    ⟨0, tangent_zero a b p⟩ v
  filter_upwards [tangent_ray_feasible a b p u hp hu] with t ht hnon
  apply le_antisymm _ (ray_lower a b p v hp t hnon)
  calc
    infDist (p + t • v) (feasible a b) ≤ dist (p + t • v) (p + t • u) :=
      infDist_le_dist_of_mem (ht hnon)
    _ = t * infDist v (tangent a b p) := by
      rw [hd, dist_eq_norm, dist_eq_norm]
      have he : p + t • v - (p + t • u) = t • (v-u) := by rw [smul_sub]; abel
      rw [he, norm_smul, Real.norm_eq_abs, abs_of_nonneg hnon]

/-- The exact ray formula transports any explicit trajectory remainder without weakening it. -/
theorem remainder_bound [ProperSpace E] (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p v : E) (hp : p ∈ feasible a b) :
    ∀ᶠ t : ℝ in 𝓝 0, ∀ z : E, 0 ≤ t →
      |infDist z (feasible a b) - t * infDist v (tangent a b p)| ≤ ‖z - (p+t•v)‖ := by
  filter_upwards [ray_distance a b p v hp] with t ht z hnon
  rw [← ht hnon, ← dist_eq_norm]
  simpa only [Real.dist_eq, NNReal.coe_one, one_mul] using
    (lipschitz_infDist_pt (s := feasible a b)).dist_le_mul z (p+t•v)

/-- A quadratic Taylor enclosure gives the paper's first-order formula with the same constant. -/
theorem quadratic_remainder [ProperSpace E] (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p v : E) (hp : p ∈ feasible a b) (path : ℝ → E) (C : ℝ)
    (hrem : ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t → ‖path t - (p+t•v)‖ ≤ C*t^2) :
    ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t →
      |infDist (path t) (feasible a b) - t * infDist v (tangent a b p)| ≤ C*t^2 := by
  filter_upwards [remainder_bound a b p v hp, hrem] with t ht hr hnon
  exact (ht (path t) hnon).trans (hr hnon)

theorem positive_window {P : ℝ → Prop} (h : ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t → P t) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ t, 0 ≤ t → t ≤ δ → P t := by
  obtain ⟨ε,hε,he⟩ := Metric.eventually_nhds_iff.mp h
  refine ⟨ε/2, by linarith, fun t ht hle => he ?_ ht⟩
  rw [Real.dist_eq, sub_zero, abs_of_nonneg ht]
  linarith

/-- The active-constraint cone equals the radial feasible cone, independent of a chosen presentation. -/
theorem tangent_eq_radial (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p : E) (hp : p ∈ feasible a b) :
    tangent a b p = {u | ∃ t : ℝ, 0 < t ∧ p + t • u ∈ feasible a b} := by
  ext u
  constructor
  · intro hu
    obtain ⟨δ,hδ,hwin⟩ := positive_window (tangent_ray_feasible a b p u hp hu)
    exact ⟨δ,hδ,hwin δ hδ.le le_rfl⟩
  · rintro ⟨t,ht,hu⟩
    have hh := tangent_smul a b p (p+t•u-p)
      (displacement_mem_tangent a b p (p+t•u) hu) t⁻¹ (inv_nonneg.mpr ht.le)
    simpa only [add_sub_cancel_left, smul_smul, inv_mul_cancel₀ ht.ne', one_smul] using hh

theorem tangent_eq_closed_radial (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p : E) (hp : p ∈ feasible a b) :
    tangent a b p = closure {u | ∃ t : ℝ, 0 < t ∧ p + t • u ∈ feasible a b} := by
  rw [← tangent_eq_radial a b p hp, (tangent_closed a b p).closure_eq]

theorem explicit_ray_window [ProperSpace E] (a : I → E →L[ℝ] ℝ) (b : I → ℝ)
    (p v : E) (hp : p ∈ feasible a b) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ t, 0 ≤ t → t ≤ δ →
      infDist (p+t•v) (feasible a b) = t * infDist v (tangent a b p) :=
  positive_window (ray_distance a b p v hp)

end Bell.TangentCone
