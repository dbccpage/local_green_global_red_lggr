import Mathlib.Analysis.LocallyConvex.Separation
import Mathlib.Analysis.Convex.Topology
import Mathlib.Analysis.Normed.Module.Convex
import Mathlib.Analysis.Normed.Lp.PiLp
import Mathlib.Topology.MetricSpace.HausdorffDistance
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

noncomputable section
open scoped BigOperators
open Set Metric
namespace Bell.ConvexDistance
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

def DualFeasible (f : E →L[ℝ] ℝ) : Prop := ∀ z, |f z| ≤ ‖z‖

theorem weak_duality {K : Set E} (hne : K.Nonempty) (p : E)
    (f : E →L[ℝ] ℝ) (hf : DualFeasible f) (b : ℝ)
    (hb : ∀ l ∈ K, f l ≤ b) : f p - b ≤ infDist p K := by
  apply (le_infDist hne).2
  intro l hl
  calc
    f p - b ≤ f p - f l := sub_le_sub_left (hb l hl) _
    _ = f (p - l) := (map_sub f p l).symm
    _ ≤ |f (p - l)| := le_abs_self _
    _ ≤ ‖p - l‖ := hf _
    _ = dist p l := (dist_eq_norm _ _).symm

/-- A compact convex repair set has an attained primal and an attained norm-dual witness. -/
theorem attained_duality_of_nearest {K : Set E}
    (hconv : Convex ℝ K) (p l : E) (hl : l ∈ K)
    (hdist : infDist p K = dist p l) :
    ∃ l ∈ K, ∃ f : E →L[ℝ] ℝ, DualFeasible f ∧
      (∀ y ∈ K, f y ≤ f l) ∧ f p - f l = infDist p K ∧
      dist p l = infDist p K := by
  by_cases hd : infDist p K = 0
  · exact ⟨l, hl, 0, by simp [DualFeasible], by simp, by simp [hd], hdist.symm⟩
  have hdpos : 0 < infDist p K := lt_of_le_of_ne infDist_nonneg (Ne.symm hd)
  obtain ⟨f, b, hball, hlocal⟩ := geometric_hahn_banach_open
    (convex_ball p (infDist p K)) isOpen_ball hconv disjoint_ball_infDist
  have hpb : f p < b := hball p (mem_ball_self hdpos)
  have hclosed : ∀ x ∈ closedBall p (infDist p K), f x ≤ b := by
    have hh : closure (ball p (infDist p K)) ⊆ {x | f x ≤ b} :=
      closure_minimal (fun x hx => (hball x hx).le) (isClosed_le f.continuous continuous_const)
    intro x hx
    exact hh (by simpa only [closure_ball _ hd] using hx)
  have hlball : l ∈ closedBall p (infDist p K) := by
    simpa only [mem_closedBall, dist_comm] using hdist.ge
  have hfl : f l = b := le_antisymm (hclosed l hlball) (hlocal l hl)
  have hgap : 0 < b - f p := sub_pos.mpr hpb
  let g : E →L[ℝ] ℝ := (-(infDist p K / (b - f p))) • f
  have hbound : DualFeasible g := by
    intro x
    by_cases hx : x = 0
    · simp [hx, g]
    have hn : 0 < ‖x‖ := norm_pos_iff.mpr hx
    have hp : p + (infDist p K / ‖x‖) • x ∈ closedBall p (infDist p K) := by
      simp only [mem_closedBall, dist_eq_norm, add_sub_cancel_left, norm_smul,
        Real.norm_eq_abs, abs_of_pos (div_pos hdpos hn)]
      exact (div_mul_cancel₀ _ hn.ne').le
    have hm : p - (infDist p K / ‖x‖) • x ∈ closedBall p (infDist p K) := by
      simp only [mem_closedBall, dist_eq_norm, sub_sub_cancel_left, norm_neg, norm_smul,
        Real.norm_eq_abs, abs_of_pos (div_pos hdpos hn)]
      exact (div_mul_cancel₀ _ hn.ne').le
    have hp' := hclosed _ hp
    have hm' := hclosed _ hm
    simp only [map_add, map_sub, map_smul, smul_eq_mul] at hp' hm'
    have habs : |(infDist p K / ‖x‖) * f x| ≤ b - f p :=
      abs_le.mpr ⟨by linarith, by linarith⟩
    rw [abs_mul, abs_of_pos (div_pos hdpos hn)] at habs
    have hmul : infDist p K * |f x| ≤ (b - f p) * ‖x‖ := by
      apply (div_le_iff₀ hn).mp
      simpa only [div_mul_eq_mul_div] using habs
    simp only [g, smul_apply, smul_eq_mul, abs_mul, abs_neg,
      abs_of_pos (div_pos hdpos hgap)]
    rw [div_mul_eq_mul_div]
    exact (div_le_iff₀ hgap).mpr (by simpa only [mul_comm] using hmul)
  refine ⟨l, hl, g, hbound, ?_, ?_, hdist.symm⟩
  · intro y hy
    have hy' : b ≤ f y := hlocal y hy
    simp only [g, smul_apply, smul_eq_mul, hfl]
    exact mul_le_mul_of_nonpos_left hy' (neg_nonpos.mpr (div_nonneg hdpos.le hgap.le))
  · simp only [g, smul_apply, smul_eq_mul, hfl]
    calc
      _ = (infDist p K / (b - f p)) * (b - f p) := by ring
      _ = _ := div_mul_cancel₀ _ hgap.ne'

theorem attained_duality {K : Set E} (hK : IsCompact K) (hne : K.Nonempty)
    (hconv : Convex ℝ K) (p : E) :
    ∃ l ∈ K, ∃ f : E →L[ℝ] ℝ, DualFeasible f ∧
      (∀ y ∈ K, f y ≤ f l) ∧ f p - f l = infDist p K ∧
      dist p l = infDist p K := by
  obtain ⟨l, hl, hd⟩ := hK.exists_infDist_eq_dist hne p
  exact attained_duality_of_nearest hconv p l hl hd

theorem attained_duality_closed [ProperSpace E] {K : Set E} (hK : IsClosed K)
    (hne : K.Nonempty) (hconv : Convex ℝ K) (p : E) :
    ∃ l ∈ K, ∃ f : E →L[ℝ] ℝ, DualFeasible f ∧
      (∀ y ∈ K, f y ≤ f l) ∧ f p - f l = infDist p K ∧
      dist p l = infDist p K := by
  obtain ⟨l, hl, hd⟩ := hK.exists_infDist_eq_dist hne p
  exact attained_duality_of_nearest hconv p l hl hd

end Bell.ConvexDistance

