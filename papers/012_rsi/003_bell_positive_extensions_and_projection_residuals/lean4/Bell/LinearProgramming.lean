import Bell.ConvexDistance
import Mathlib.Analysis.Convex.Combination

/-! Finite norm-repair linear programming, adapted from the RSI contextuality proof. -/
noncomputable section
open Set Metric
open scoped BigOperators
namespace Bell.LinearProgramming

def simplex (G : Type*) [Fintype G] : Set (G → ℝ) :=
  {q | (∀ g, 0 ≤ q g) ∧ ∑ g, q g = 1}

theorem simplex_single {G : Type*} [Fintype G] [DecidableEq G] (g : G) :
    Pi.single g (1 : ℝ) ∈ simplex G := by
  constructor
  · intro i; simp [Pi.single_apply]; split_ifs <;> norm_num
  · simp

theorem simplex_convex (G : Type*) [Fintype G] : Convex ℝ (simplex G) := by
  intro x hx y hy a b ha hb hab
  constructor
  · intro i; exact add_nonneg (mul_nonneg ha (hx.1 i)) (mul_nonneg hb (hy.1 i))
  · simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul, Finset.sum_add_distrib,
      ← Finset.mul_sum, hx.2, hy.2, mul_one, hab]

theorem simplex_compact (G : Type*) [Fintype G] : IsCompact (simplex G) := by
  have hc : IsClosed (simplex G) := by
    have he : simplex G = (⋂ i, {q : G → ℝ | 0 ≤ q i}) ∩ {q | ∑ i, q i = 1} := by
      ext q; simp [simplex]
    rw [he]
    exact (isClosed_iInter fun i => isClosed_le continuous_const (continuous_apply i)).inter
      (isClosed_eq (continuous_finsetSum _ fun i _ => continuous_apply i) continuous_const)
  apply (isCompact_Icc (a := (0 : G → ℝ)) (b := 1)).of_isClosed_subset hc
  intro q hq
  constructor
  · exact hq.1
  · intro i
    change q i ≤ (1 : ℝ)
    rw [← hq.2]
    exact Finset.single_le_sum (fun j _ => hq.1 j) (Finset.mem_univ i)

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
    (f : Vec I →L[ℝ] ℝ) (hf : Bell.ConvexDistance.DualFeasible f) :
    ∀ i, |f (PiLp.single 1 i 1)| ≤ 1 := by
  intro i
  simpa only [PiLp.norm_single, Real.norm_eq_abs, abs_one] using hf (PiLp.single 1 i 1)

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
  let K := L '' simplex G
  have hK : IsCompact K := (simplex_compact G).image L.continuous
  have hc : Convex ℝ K := (simplex_convex G).linear_image L.toLinearMap
  have hne : K.Nonempty := ⟨L (Pi.single (Classical.arbitrary G) 1),
    ⟨_, simplex_single _, rfl⟩⟩
  obtain ⟨x, ⟨p, hp, hpx⟩, f, hfn, hsupport, hgap, hmin⟩ :=
    Bell.ConvexDistance.attained_duality hK hne hc (WithLp.toLp 1 e)
  let y := fun i => f (PiLp.single 1 i 1)
  let z := -f x
  have hy : ∀ i, |y i| ≤ 1 := dual_coordinates_bounded f hfn
  have hcol : ∀ g, pairing y (A g) + z ≤ 0 := by
    intro g
    have hh := hsupport (L (Pi.single g 1)) ⟨_, simplex_single g, rfl⟩
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
    change f (WithLp.toLp 1 e) - f x = _
    simpa only [dist_eq_norm] using hgap.trans hmin.symm
  exact ⟨p, y, z, hp.1, hp.2, hy, hcol, hvalue,
    zero_gap_certificate_optimal A e y p z hy hcol hvalue⟩


end Bell.LinearProgramming
