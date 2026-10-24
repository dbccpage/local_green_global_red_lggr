import Mathlib.Analysis.LocallyConvex.Separation
import Mathlib.Analysis.Normed.Lp.PiLp
import Mathlib.Analysis.Convex.StdSimplex
import Mathlib.Analysis.Convex.Topology
import Mathlib.Analysis.Normed.Operator.NNNorm
import Mathlib.Analysis.Normed.Operator.NormedSpace
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

noncomputable section
open Set Metric
open scoped BigOperators
namespace EpistemicNoGo.ContextualDuality

theorem separating_ball_bound {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (f : E →L[ℝ] ℝ) (e x : E) (d : ℝ) (hd : 0 < d)
    (hB : ∀ z ∈ closedBall e d, f z ≤ f x) :
    ‖f‖ * d ≤ f x - f e := by
  have hgap : 0 ≤ f x - f e := sub_nonneg.mpr (hB e (mem_closedBall_self hd.le))
  have hop : ‖f‖ ≤ (f x - f e) / d := by
    apply ContinuousLinearMap.opNorm_le_of_unit_norm (div_nonneg hgap hd.le)
    intro v hv
    have hp : e + d • v ∈ closedBall e d := by
      rw [mem_closedBall_iff_norm]
      simp [norm_smul, hv, abs_of_pos hd]
    have hn : e - d • v ∈ closedBall e d := by
      rw [mem_closedBall_iff_norm]
      simp [sub_eq_add_neg, norm_smul, hv, abs_of_pos hd]
    have hpos := hB (e + d • v) hp
    have hneg := hB (e - d • v) hn
    simp only [map_add, map_sub, map_smul, smul_eq_mul] at hpos hneg
    rw [Real.norm_eq_abs, abs_le]
    constructor
    · have hh : -f v ≤ (f x - f e) / d := (le_div_iff₀ hd).mpr (by nlinarith)
      linarith
    · apply (le_div_iff₀ hd).mpr
      nlinarith
  exact (le_div_iff₀ hd).mp hop

/-- Attainment of primal distance and a supporting dual functional. The dual
is constructed by separation, not supplied as a zero-gap premise. -/
theorem compact_convex_distance_duality {E : Type*}
    [NormedAddCommGroup E] [NormedSpace ℝ E]
    (K : Set E) (hK : IsCompact K) (hne : K.Nonempty) (hc : Convex ℝ K) (e : E) :
    ∃ x ∈ K, ∃ f : E →L[ℝ] ℝ,
      ‖f‖ ≤ 1 ∧ (∀ z ∈ K, f z ≤ f x) ∧
      f e - f x = ‖e - x‖ ∧ (∀ z ∈ K, ‖e - x‖ ≤ ‖e - z‖) := by
  obtain ⟨x, hx, hmin⟩ := hK.exists_isMinOn hne (continuous_const.sub continuous_id).norm.continuousOn
  by_cases he : e = x
  · refine ⟨x, hx, 0, by simp, by simp, ?_, ?_⟩
    · simp [he]
    · intro z hz; simp [he]
  let d := ‖e - x‖
  have hd : 0 < d := norm_pos_iff.mpr (sub_ne_zero.mpr he)
  have hdisj : Disjoint (ball e d) K := by
    apply Set.disjoint_left.mpr
    intro z hz hzK
    have hlow := hmin hzK
    have hhigh : ‖e - z‖ < d := by
      simpa [dist_eq_norm, norm_sub_rev] using hz
    exact (not_lt_of_ge hlow) hhigh
  obtain ⟨g, u, hgB, hgK⟩ := geometric_hahn_banach_open (convex_ball e d) isOpen_ball hc hdisj
  have hge : g e < g x := (hgB e (mem_ball_self hd)).trans_le (hgK x hx)
  have hg0 : g ≠ 0 := by intro h; simp [h] at hge
  have hgn : 0 < ‖g‖ := norm_pos_iff.mpr hg0
  have hclosedAll : ∀ z ∈ K, ∀ v ∈ closedBall e d, g v ≤ g z := by
    intro z hz
    have hsub : ball e d ⊆ {v | g v ≤ g z} := fun v hv => (hgB v hv).le.trans (hgK z hz)
    have hh := closure_minimal hsub (isClosed_le g.continuous continuous_const)
    rw [closure_ball e hd.ne'] at hh
    exact fun v hv => hh hv
  have hbound := separating_ball_bound g e x d hd (hclosedAll x hx)
  have hupper : g x - g e ≤ ‖g‖ * d := by
    calc
      g x - g e = g (x - e) := (map_sub g x e).symm
      _ ≤ ‖g (x - e)‖ := le_abs_self _
      _ ≤ ‖g‖ * ‖x - e‖ := g.le_opNorm _
      _ = ‖g‖ * d := by rw [norm_sub_rev]
  have hgap : g x - g e = ‖g‖ * d := le_antisymm hupper hbound
  let f : E →L[ℝ] ℝ := (-‖g‖⁻¹) • g
  refine ⟨x, hx, f, ?_, ?_, ?_, hmin⟩
  · simp [f, norm_smul, norm_inv, norm_neg, inv_mul_cancel₀ hgn.ne']
  · intro z hz
    change -‖g‖⁻¹ * g z ≤ -‖g‖⁻¹ * g x
    have hlower := separating_ball_bound g e z d hd (hclosedAll z hz)
    have hsupport : g x ≤ g z := by linarith [hgap]
    apply mul_le_mul_of_nonpos_left hsupport
    exact neg_nonpos.mpr (inv_nonneg.mpr hgn.le)
  · change -‖g‖⁻¹ * g e - -‖g‖⁻¹ * g x = d
    calc
      _ = ‖g‖⁻¹ * (g x - g e) := by ring
      _ = d := by rw [hgap, ← mul_assoc, inv_mul_cancel₀ hgn.ne', one_mul]

abbrev Vec (I : Type*) := PiLp 1 (fun _ : I => ℝ)

def pairing {R I : Type*} [Semiring R] [Fintype I] (y v : I → R) : R := ∑ i, y i * v i

def mix {R I G : Type*} [Semiring R] [Fintype G] (A : G → I → R) (p : G → R) : I → R :=
  fun i => ∑ g, p g * A g i

def cost {R I G : Type*} [Ring R] [LinearOrder R] [Fintype I] [Fintype G]
    (A : G → I → R) (e : I → R) (p : G → R) : R := ∑ i, |e i - mix A p i|

/-- Weak duality over any ordered field, in particular the exact rational
field used by certificate replay. No attainment hypothesis is needed. -/
theorem weak_duality {R I G : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]
    [Fintype I] [Fintype G] (A : G → I → R) (e y : I → R) (p : G → R) (z : R)
    (hp : ∀ g, 0 ≤ p g) (hsum : ∑ g, p g = 1)
    (hy : ∀ i, |y i| ≤ 1) (hz : ∀ g, pairing y (A g) + z ≤ 0) :
    pairing y e + z ≤ cost A e p := by
  have hm : pairing y (mix A p) + z ≤ 0 := by
    have heq : pairing y (mix A p) = ∑ g, p g * pairing y (A g) := by
      simp only [pairing, mix, Finset.mul_sum]
      rw [Finset.sum_comm]
      congr 1; funext g; congr 1; funext i; ring
    rw [heq]
    have hh := Finset.sum_nonpos (s := Finset.univ) (fun g _ =>
      mul_nonpos_of_nonneg_of_nonpos (hp g) (hz g))
    simp_rw [mul_add] at hh
    simpa only [Finset.sum_add_distrib, ← Finset.sum_mul, hsum, one_mul] using hh
  have hres : pairing y e - pairing y (mix A p) ≤ cost A e p := by
    simp only [pairing, cost, ← Finset.sum_sub_distrib, ← mul_sub]
    apply Finset.sum_le_sum
    intro i _
    calc
      y i * (e i - mix A p i) ≤ |y i * (e i - mix A p i)| := le_abs_self _
      _ = |y i| * |e i - mix A p i| := abs_mul _ _
      _ ≤ 1 * |e i - mix A p i| := mul_le_mul_of_nonneg_right (hy i) (abs_nonneg _)
      _ = _ := one_mul _
  linarith

theorem zero_gap_certificate_optimal {R I G : Type*} [Field R] [LinearOrder R]
    [IsStrictOrderedRing R] [Fintype I] [Fintype G]
    (A : G → I → R) (e y : I → R) (p : G → R) (z : R)
    (hy : ∀ i, |y i| ≤ 1) (hz : ∀ g, pairing y (A g) + z ≤ 0)
    (hgap : pairing y e + z = cost A e p) :
    ∀ q, (∀ g, 0 ≤ q g) → (∑ g, q g = 1) → cost A e p ≤ cost A e q := by
  intro q hq hs
  rw [← hgap]
  exact weak_duality A e y q z hq hs hy hz

theorem linear_form_coordinates {I : Type*} [Fintype I] [DecidableEq I]
    (f : Vec I →L[ℝ] ℝ) (v : Vec I) :
    f v = pairing (fun i => f (PiLp.single 1 i 1)) (fun i => v i) := by
  have h := congrArg f ((PiLp.basisFun 1 ℝ I).sum_repr v)
  simpa [pairing, map_sum, map_smul, mul_comm] using h.symm

theorem dual_coordinates_bounded {I : Type*} [Fintype I] [DecidableEq I]
    (f : Vec I →L[ℝ] ℝ) (hf : ‖f‖ ≤ 1) :
    ∀ i, |f (PiLp.single 1 i 1)| ≤ 1 := by
  intro i
  have hh := f.le_opNorm (PiLp.single 1 i 1)
  rw [PiLp.norm_single] at hh
  have hh' : |f (PiLp.single 1 i 1)| ≤ ‖f‖ := by simpa using hh
  exact hh'.trans hf

def mixtureMap {I G : Type*} [Fintype I] [Fintype G] (A : G → I → ℝ) :
    (G → ℝ) →L[ℝ] Vec I :=
  ((WithLp.linearEquiv 1 ℝ (I → ℝ)).symm.toLinearMap.comp
    (∑ g, (LinearMap.proj (R := ℝ) g).smulRight (A g))).toContinuousLinearMap

theorem mixtureMap_apply {I G : Type*} [Fintype I] [Fintype G]
    (A : G → I → ℝ) (p : G → ℝ) (i : I) : mixtureMap A p i = mix A p i := by
  simp [mixtureMap, mix, Finset.sum_apply]

theorem cost_eq_norm {I G : Type*} [Fintype I] [Fintype G]
    (A : G → I → ℝ) (e : I → ℝ) (p : G → ℝ) :
    cost A e p = ‖WithLp.toLp 1 e - mixtureMap A p‖ := by
  simp [PiLp.norm_eq_of_L1, cost, PiLp.sub_apply, mixtureMap_apply, Real.norm_eq_abs]

/-- Finite contextuality LP strong duality: primal simplex weights and a
bounded dual vector/offset are both attained, with zero gap and optimality. -/
theorem contextuality_strong_duality {I G : Type*} [Fintype I] [Fintype G]
    [Nonempty G] [DecidableEq I] [DecidableEq G] (A : G → I → ℝ) (e : I → ℝ) :
    ∃ (p : G → ℝ) (y : I → ℝ) (z : ℝ),
      (∀ g, 0 ≤ p g) ∧ (∑ g, p g = 1) ∧
      (∀ i, |y i| ≤ 1) ∧ (∀ g, pairing y (A g) + z ≤ 0) ∧
      pairing y e + z = cost A e p ∧
      (∀ q, (∀ g, 0 ≤ q g) → (∑ g, q g = 1) → cost A e p ≤ cost A e q) := by
  classical
  let L := mixtureMap A
  let K := L '' stdSimplex ℝ G
  have hK : IsCompact K := (isCompact_stdSimplex ℝ G).image L.continuous
  have hc : Convex ℝ K := (convex_stdSimplex ℝ G).linear_image L.toLinearMap
  have hne : K.Nonempty := ⟨L (Pi.single (Classical.arbitrary G) 1),
    ⟨_, single_mem_stdSimplex ℝ _, rfl⟩⟩
  obtain ⟨x, ⟨p, hp, hpx⟩, f, hfn, hsupport, hgap, hmin⟩ :=
    compact_convex_distance_duality K hK hne hc (WithLp.toLp 1 e)
  let y := fun i => f (PiLp.single 1 i 1)
  let z := -f x
  have hy : ∀ i, |y i| ≤ 1 := dual_coordinates_bounded f hfn
  have hcol : ∀ g, pairing y (A g) + z ≤ 0 := by
    intro g
    have hh := hsupport (L (Pi.single g 1)) ⟨_, single_mem_stdSimplex ℝ g, rfl⟩
    have heq : L (Pi.single g 1) = WithLp.toLp 1 (A g) := by
      ext i
      simp [L, mixtureMap_apply, mix, Pi.single_apply]
    rw [heq, linear_form_coordinates] at hh
    change pairing y (A g) + -f x ≤ 0
    linarith
  have hvalue : pairing y e + z = cost A e p := by
    rw [cost_eq_norm, hpx]
    have heval : f (WithLp.toLp 1 e) = pairing y e := linear_form_coordinates f _
    rw [← heval]
    exact hgap
  exact ⟨p, y, z, hp.1, hp.2, hy, hcol, hvalue,
    zero_gap_certificate_optimal A e y p z hy hcol hvalue⟩

theorem cost_zero_iff {I G : Type*} [Fintype I] [Fintype G]
    (A : G → I → ℝ) (e : I → ℝ) (p : G → ℝ) :
    cost A e p = 0 ↔ mix A p = e := by
  rw [cost_eq_norm, norm_eq_zero]
  constructor
  · intro h
    have heq := sub_eq_zero.mp h
    funext i
    have hh := congrArg (fun v : Vec I => v i) heq
    simpa only [PiLp.toLp_apply, mixtureMap_apply] using hh.symm
  · intro h
    apply sub_eq_zero.mpr
    ext i
    simpa only [PiLp.toLp_apply, mixtureMap_apply] using congrFun h.symm i

/-- The contextuality alternative is proved from attained duality. -/
theorem joint_or_positive_dual {I G : Type*} [Fintype I] [Fintype G]
    [Nonempty G] [DecidableEq I] [DecidableEq G] (A : G → I → ℝ) (e : I → ℝ) :
    (∃ p, (∀ g, 0 ≤ p g) ∧ (∑ g, p g = 1) ∧ mix A p = e) ∨
    (∃ (p : G → ℝ) (y : I → ℝ) (z : ℝ),
      (∀ g, 0 ≤ p g) ∧ (∑ g, p g = 1) ∧
      (∀ i, |y i| ≤ 1) ∧ (∀ g, pairing y (A g) + z ≤ 0) ∧
      0 < cost A e p ∧ pairing y e + z = cost A e p ∧
      ∀ q, (∀ g, 0 ≤ q g) → (∑ g, q g = 1) → cost A e p ≤ cost A e q) := by
  obtain ⟨p, y, z, hp, hs, hy, hz, hval, hmin⟩ := contextuality_strong_duality A e
  by_cases hzero : cost A e p = 0
  · exact Or.inl ⟨p, hp, hs, (cost_zero_iff A e p).mp hzero⟩
  · exact Or.inr ⟨p, y, z, hp, hs, hy, hz,
      lt_of_le_of_ne (by rw [cost_eq_norm]; exact norm_nonneg _) (Ne.symm hzero), hval, hmin⟩

theorem positive_dual_excludes_joint {I G : Type*} [Fintype I] [Fintype G]
    (A : G → I → ℝ) (e y : I → ℝ) (z : ℝ)
    (hy : ∀ i, |y i| ≤ 1) (hz : ∀ g, pairing y (A g) + z ≤ 0)
    (hpos : 0 < pairing y e + z) :
    ¬ ∃ p, (∀ g, 0 ≤ p g) ∧ (∑ g, p g = 1) ∧ mix A p = e := by
  rintro ⟨p, hp, hs, heq⟩
  have hh := weak_duality A e y p z hp hs hy hz
  rw [(cost_zero_iff A e p).mpr heq] at hh
  exact (not_lt_of_ge hh) hpos

theorem slacks_l1_lower_bound {R I G : Type*} [Field R] [LinearOrder R]
    [IsStrictOrderedRing R] [Fintype I] [Fintype G]
    (A : G → I → R) (e : I → R) (p : G → R) (u v : I → R)
    (hu : ∀ i, 0 ≤ u i) (hv : ∀ i, 0 ≤ v i)
    (heq : ∀ i, mix A p i - u i + v i = e i) :
    cost A e p ≤ ∑ i, (u i + v i) := by
  apply Finset.sum_le_sum
  intro i _
  apply abs_le.mpr
  constructor <;> linarith [hu i, hv i, heq i]

theorem exact_slacks_exist {R I G : Type*} [Field R] [LinearOrder R]
    [IsStrictOrderedRing R] [Fintype I] [Fintype G]
    (A : G → I → R) (e : I → R) (p : G → R) :
    ∃ u v : I → R, (∀ i, 0 ≤ u i) ∧ (∀ i, 0 ≤ v i) ∧
      (∀ i, mix A p i - u i + v i = e i) ∧ cost A e p = ∑ i, (u i + v i) := by
  refine ⟨fun i => max (mix A p i - e i) 0, fun i => max (e i - mix A p i) 0,
    fun i => le_max_right _ _, fun i => le_max_right _ _, ?_, ?_⟩
  · intro i
    dsimp only
    by_cases h : e i ≤ mix A p i
    · rw [max_eq_left (by linarith : 0 ≤ mix A p i - e i),
        max_eq_right (by linarith : e i - mix A p i ≤ 0)]; ring
    · rw [max_eq_right (by linarith : mix A p i - e i ≤ 0),
        max_eq_left (by linarith : 0 ≤ e i - mix A p i)]; ring
  · apply Finset.sum_congr rfl
    intro i _
    dsimp only
    by_cases h : e i ≤ mix A p i
    · rw [abs_of_nonpos (by linarith : e i - mix A p i ≤ 0),
        max_eq_left (by linarith : 0 ≤ mix A p i - e i),
        max_eq_right (by linarith : e i - mix A p i ≤ 0)]; ring
    · rw [abs_of_nonneg (by linarith : 0 ≤ e i - mix A p i),
        max_eq_right (by linarith : mix A p i - e i ≤ 0),
        max_eq_left (by linarith : 0 ≤ e i - mix A p i)]; ring

/-- A checked rational certificate also certifies the optimum against every
real probability vector, not only against rational competitors. -/
theorem rational_certificate_real_optimal {I G : Type*} [Fintype I] [Fintype G]
    (A : G → I → ℚ) (e y : I → ℚ) (p : G → ℚ) (z : ℚ)
    (hy : ∀ i, |y i| ≤ 1) (hz : ∀ g, pairing y (A g) + z ≤ 0)
    (hgap : pairing y e + z = cost A e p) :
    ∀ q : G → ℝ, (∀ g, 0 ≤ q g) → (∑ g, q g = 1) →
      ((cost A e p : ℚ) : ℝ) ≤ cost (fun g i => (A g i : ℝ)) (fun i => (e i : ℝ)) q := by
  intro q hq hs
  have hyr : ∀ i, |(y i : ℝ)| ≤ 1 := by intro i; exact_mod_cast hy i
  have hzr : ∀ g, pairing (fun i => (y i : ℝ)) (fun i => (A g i : ℝ)) + (z : ℝ) ≤ 0 := by
    intro g
    have hh := hz g
    unfold pairing at *
    dsimp only at *
    exact_mod_cast hh
  have hh := weak_duality (fun g i => (A g i : ℝ)) (fun i => (e i : ℝ))
    (fun i => (y i : ℝ)) q (z : ℝ) hq hs hyr hzr
  have hcast : pairing (fun i => (y i : ℝ)) (fun i => (e i : ℝ)) + (z : ℝ) = ((cost A e p : ℚ) : ℝ) := by
    unfold pairing cost mix at *
    dsimp only at *
    exact_mod_cast hgap
  rwa [hcast] at hh

theorem dual_offset_is_negative_max {R I G : Type*} [Field R] [LinearOrder R]
    [IsStrictOrderedRing R] [Fintype I] [Fintype G] [Nonempty G]
    (A : G → I → R) (e y : I → R) (p : G → R) (z : R)
    (hp : ∀ g, 0 ≤ p g) (hs : ∑ g, p g = 1)
    (hy : ∀ i, |y i| ≤ 1) (hz : ∀ g, pairing y (A g) + z ≤ 0)
    (hgap : pairing y e + z = cost A e p) :
    ∃ g, (∀ j, pairing y (A j) ≤ pairing y (A g)) ∧ z = -pairing y (A g) := by
  classical
  obtain ⟨g, _, hmax⟩ := Finset.exists_max_image Finset.univ (fun j => pairing y (A j)) Finset.univ_nonempty
  have hmax' : ∀ j, pairing y (A j) ≤ pairing y (A g) := fun j => hmax j (Finset.mem_univ j)
  have hnew : ∀ j, pairing y (A j) + -pairing y (A g) ≤ 0 := by
    intro j; linarith [hmax' j]
  have hh := weak_duality A e y p (-pairing y (A g)) hp hs hy hnew
  exact ⟨g, hmax', by linarith [hz g]⟩

/-- Canonical form with the actual finite maximum over deterministic columns. -/
theorem canonical_dual_attainment {I G : Type*} [Fintype I] [Fintype G]
    [Nonempty G] [DecidableEq I] [DecidableEq G] (A : G → I → ℝ) (e : I → ℝ) :
    ∃ (p : G → ℝ) (y : I → ℝ) (g : G),
      (∀ j, 0 ≤ p j) ∧ (∑ j, p j = 1) ∧ (∀ i, |y i| ≤ 1) ∧
      (∀ j, pairing y (A j) ≤ pairing y (A g)) ∧
      pairing y e - pairing y (A g) = cost A e p ∧
      ∀ q, (∀ j, 0 ≤ q j) → (∑ j, q j = 1) → cost A e p ≤ cost A e q := by
  obtain ⟨p, y, z, hp, hs, hy, hz, hgap, hmin⟩ := contextuality_strong_duality A e
  obtain ⟨g, hmax, heq⟩ := dual_offset_is_negative_max A e y p z hp hs hy hz hgap
  exact ⟨p, y, g, hp, hs, hy, hmax, by simpa [heq, sub_eq_add_neg] using hgap, hmin⟩

theorem dual_solution_optimal {R I G : Type*} [Field R] [LinearOrder R]
    [IsStrictOrderedRing R] [Fintype I] [Fintype G]
    (A : G → I → R) (e y : I → R) (p : G → R) (z : R)
    (hp : ∀ g, 0 ≤ p g) (hs : ∑ g, p g = 1)
    (hgap : pairing y e + z = cost A e p) :
    ∀ y' z', (∀ i, |y' i| ≤ 1) → (∀ g, pairing y' (A g) + z' ≤ 0) →
      pairing y' e + z' ≤ pairing y e + z := by
  intro y' z' hy' hz'
  rw [hgap]
  exact weak_duality A e y' p z' hp hs hy' hz'

theorem rational_simplex_cast {G : Type*} [Fintype G] (p : G → ℚ)
    (hp : ∀ g, 0 ≤ p g) (hs : ∑ g, p g = 1) :
    (∀ g, (0 : ℝ) ≤ (p g : ℝ)) ∧ (∑ g, (p g : ℝ)) = 1 := by
  constructor
  · intro g; exact_mod_cast hp g
  · exact_mod_cast hs

/-- The literal standard-form LP used by the standalone rational solver. -/
theorem contextuality_standard_form_strong_duality {I G : Type*} [Fintype I] [Fintype G]
    [Nonempty G] [DecidableEq I] [DecidableEq G] (A : G → I → ℝ) (e : I → ℝ) :
    ∃ (p : G → ℝ) (u v y : I → ℝ) (z : ℝ),
      (∀ g, 0 ≤ p g) ∧ (∑ g, p g = 1) ∧
      (∀ i, 0 ≤ u i) ∧ (∀ i, 0 ≤ v i) ∧
      (∀ i, mix A p i - u i + v i = e i) ∧
      (∀ i, |y i| ≤ 1) ∧ (∀ g, pairing y (A g) + z ≤ 0) ∧
      pairing y e + z = ∑ i, (u i + v i) := by
  obtain ⟨p, y, z, hp, hs, hy, hz, hgap, _⟩ := contextuality_strong_duality A e
  obtain ⟨u, v, hu, hv, heq, hcost⟩ := exact_slacks_exist A e p
  exact ⟨p, u, v, y, z, hp, hs, hu, hv, heq, hy, hz, hgap.trans hcost⟩

end EpistemicNoGo.ContextualDuality
