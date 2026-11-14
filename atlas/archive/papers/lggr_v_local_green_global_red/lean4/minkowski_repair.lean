import Init.Data.Rat.Lemmas
import Init.Grind.Ordered.Ring

/-!
Rational repair distances for LGGR V lemmas LGR-R2, LGR-R3, and LGR-R4.

The Euclidean statements are identities of squares. The positive square root of a
proved nonnegative rational is not a separate declaration. This file is not a
Lake root: elaborate it with the toolchain `lean` binary, not `lake build`.
-/

namespace MinkowskiRepair

theorem two_nonneg : (0 : Rat) ≤ 2 := Rat.natCast_nonneg

theorem two_ne_zero : (2 : Rat) ≠ 0 := by
  intro h
  have hn := congrArg Rat.num h
  simp at hn

theorem two_pos : (0 : Rat) < 2 :=
  Rat.lt_of_le_of_ne two_nonneg (fun h => two_ne_zero h.symm)

theorem nonneg_neg_of_nonpos {a : Rat} (ha : a ≤ 0) : 0 ≤ -a := by
  rw [← Rat.neg_zero] at ha
  exact (Rat.le_neg_iff).mp ha

theorem add_nonpos {a b : Rat} (ha : a ≤ 0) (hb : b ≤ 0) : a + b ≤ 0 := by
  have hsum : 0 ≤ -a + -b :=
    Rat.add_nonneg (nonneg_neg_of_nonpos ha) (nonneg_neg_of_nonpos hb)
  have heq : -a + -b = -(a + b) := by grind
  rw [heq] at hsum
  have hle : a + b ≤ -0 := (Rat.le_neg_iff (a := 0) (b := a + b)).mp hsum
  rw [Rat.neg_zero] at hle
  exact hle

theorem sub_nonneg_of_le {a b : Rat} (h : a ≤ b) : 0 ≤ b - a := by
  have h' := (Rat.add_le_add_right (c := -a)).mpr h
  rw [Rat.add_neg_cancel] at h'
  rw [Rat.sub_eq_add_neg]
  exact h'

theorem le_abs_self (x : Rat) : x ≤ x.abs := by
  by_cases hx : 0 ≤ x
  · rw [Rat.abs_of_nonneg hx]
    exact Rat.le_refl
  · rw [Rat.abs_of_nonpos (Rat.le_of_lt (Rat.not_le.mp hx))]
    grind

theorem neg_abs_le_self (x : Rat) : -x.abs ≤ x := by
  by_cases hx : 0 ≤ x
  · rw [Rat.abs_of_nonneg hx]
    grind
  · rw [Rat.abs_of_nonpos (Rat.le_of_lt (Rat.not_le.mp hx)), Rat.neg_neg]
    exact Rat.le_refl

theorem abs_le_of_bounds (z b : Rat) (hlo : -b ≤ z) (hhi : z ≤ b) : z.abs ≤ b := by
  by_cases hz : 0 ≤ z
  · rw [Rat.abs_of_nonneg hz]
    exact hhi
  · rw [Rat.abs_of_nonpos (Rat.le_of_lt (Rat.not_le.mp hz))]
    exact (Rat.neg_le_iff).mpr hlo

theorem abs_add_le (x y : Rat) : (x + y).abs ≤ x.abs + y.abs := by
  have hlo : -(x.abs + y.abs) ≤ x + y := by
    have hx := neg_abs_le_self x
    have hy := neg_abs_le_self y
    grind
  have hhi : x + y ≤ x.abs + y.abs := by
    have hx := le_abs_self x
    have hy := le_abs_self y
    grind
  exact abs_le_of_bounds (x + y) (x.abs + y.abs) hlo hhi

theorem abs_two_mul (x : Rat) : (2 * x).abs = 2 * x.abs := by
  by_cases hx : 0 ≤ x
  · have h2x : 0 ≤ 2 * x := Rat.mul_nonneg two_nonneg hx
    rw [Rat.abs_of_nonneg hx, Rat.abs_of_nonneg h2x]
  · have hx0 : x ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hx)
    have h2x : 2 * x ≤ 0 := by
      have hpos : 0 ≤ 2 * -x := Rat.mul_nonneg two_nonneg (nonneg_neg_of_nonpos hx0)
      have heq : 2 * -x = -(2 * x) := by grind
      rw [heq] at hpos
      have hle : 2 * x ≤ -0 := (Rat.le_neg_iff (a := 0) (b := 2 * x)).mp hpos
      rw [Rat.neg_zero] at hle
      exact hle
    rw [Rat.abs_of_nonpos hx0, Rat.abs_of_nonpos h2x]
    grind

theorem nat_inv_nonneg (n : Nat) : (0 : Rat) ≤ (n : Rat)⁻¹ := by
  rw [Rat.inv_def]
  simp only [Rat.den_natCast, Rat.num_natCast]
  exact Rat.divInt_nonneg (Int.natCast_nonneg 1) (Int.natCast_nonneg n)

theorem inv_two_nonneg : (0 : Rat) ≤ (2 : Rat)⁻¹ := nat_inv_nonneg 2

theorem div_two_nonneg {x : Rat} (hx : 0 ≤ x) : 0 ≤ x / 2 := by
  rw [Rat.div_def]
  exact Rat.mul_nonneg hx inv_two_nonneg

theorem div_ofNat_nonneg {x : Rat} {n : Nat} (hx : 0 ≤ x) : 0 ≤ x / (n : Rat) := by
  rw [Rat.div_def]
  exact Rat.mul_nonneg hx (nat_inv_nonneg n)

theorem abs_div_ofNat (x : Rat) {n : Nat} (_hn : 0 < n) :
    (x / (n : Rat)).abs = x.abs / (n : Rat) := by
  by_cases hx : 0 ≤ x
  · rw [Rat.abs_of_nonneg hx, Rat.abs_of_nonneg (div_ofNat_nonneg hx)]
  · have hx0 : x ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hx)
    have hdiv : x / (n : Rat) ≤ 0 := by
      have hy : 0 ≤ (-x) / (n : Rat) := div_ofNat_nonneg (nonneg_neg_of_nonpos hx0)
      have heq : x / (n : Rat) = -((-x) / (n : Rat)) := by grind
      rw [heq]
      have hle : -((-x) / (n : Rat)) ≤ -0 := (Rat.neg_le_neg_iff).mpr hy
      rw [Rat.neg_zero] at hle
      exact hle
    rw [Rat.abs_of_nonpos hx0, Rat.abs_of_nonpos hdiv]
    grind

theorem abs_div_two (x : Rat) : (x / 2).abs = x.abs / 2 :=
  abs_div_ofNat x (by decide)

theorem max_eq_right {a b : Rat} (h : a ≤ b) : max a b = b := by
  rw [Rat.max_def, ite_eq_left h]

theorem max_eq_left {a b : Rat} (h : b ≤ a) : max a b = a := by
  rw [Rat.max_def]
  by_cases hab : a ≤ b
  · have heq : a = b := Rat.le_antisymm hab h
    rw [ite_eq_left hab]
    exact heq.symm
  · rw [ite_eq_right hab]

theorem min_eq_left {a b : Rat} (h : a ≤ b) : min a b = a := by
  rw [Rat.min_def, ite_eq_left h]

theorem min_eq_right {a b : Rat} (h : b ≤ a) : min a b = b := by
  rw [Rat.min_def]
  by_cases hab : a ≤ b
  · have heq : a = b := Rat.le_antisymm hab h
    rw [ite_eq_left hab]
    exact heq
  · rw [ite_eq_right hab]

theorem le_max_left (a b : Rat) : a ≤ max a b := by
  by_cases h : a ≤ b
  · rw [max_eq_right h]
    exact h
  · rw [max_eq_left (Rat.le_of_lt (Rat.not_le.mp h))]
    exact Rat.le_refl

theorem le_max_right (a b : Rat) : b ≤ max a b := by
  by_cases h : a ≤ b
  · rw [max_eq_right h]
    exact Rat.le_refl
  · rw [max_eq_left (Rat.le_of_lt (Rat.not_le.mp h))]
    exact Rat.le_of_lt (Rat.not_le.mp h)

theorem min_le_left (a b : Rat) : min a b ≤ a := by
  by_cases h : a ≤ b
  · rw [min_eq_left h]
    exact Rat.le_refl
  · rw [min_eq_right (Rat.le_of_lt (Rat.not_le.mp h))]
    exact Rat.le_of_lt (Rat.not_le.mp h)

theorem min_le_right (a b : Rat) : min a b ≤ b := by
  by_cases h : a ≤ b
  · rw [min_eq_left h]
    exact h
  · rw [min_eq_right (Rat.le_of_lt (Rat.not_le.mp h))]
    exact Rat.le_refl

theorem max_self (a : Rat) : max a a = a := max_eq_right Rat.le_refl

theorem max_add_min (a b : Rat) : max a b + min a b = a + b := by
  by_cases hab : a ≤ b
  · rw [max_eq_right hab, min_eq_left hab]
    exact Rat.add_comm b a
  · have hba : b ≤ a := Rat.le_of_lt (Rat.not_le.mp hab)
    rw [max_eq_left hba, min_eq_right hba]

theorem max_sub_min (a b : Rat) : max a b - min a b = (a - b).abs := by
  by_cases hab : a ≤ b
  · have hsub : a - b ≤ 0 := by
      have h' := (Rat.add_le_add_right (c := -b)).mpr hab
      rw [Rat.add_neg_cancel] at h'
      rw [Rat.sub_eq_add_neg]
      exact h'
    rw [max_eq_right hab, min_eq_left hab, Rat.abs_of_nonpos hsub]
    grind
  · have hba : b ≤ a := Rat.le_of_lt (Rat.not_le.mp hab)
    have hsub : 0 ≤ a - b := sub_nonneg_of_le hba
    rw [max_eq_left hba, min_eq_right hba, Rat.abs_of_nonneg hsub]

theorem sq_eq_zero_iff (a : Rat) : a ^ 2 = 0 ↔ a = 0 := by
  grind

theorem diag_l2_cleared (a b α : Rat) :
    2 * ((a + α) ^ 2 + (b + α) ^ 2) = (2 * α + a + b) ^ 2 + (a - b) ^ 2 := by
  grind

theorem skew_l2_cleared (a b α : Rat) :
    5 * ((a + α) ^ 2 + (b + 2 * α) ^ 2) = (5 * α + a + 2 * b) ^ 2 + (2 * a - b) ^ 2 := by
  grind

theorem diag_l1_ge (a b α : Rat) :
    (a - b).abs ≤ (a + α).abs + (b + α).abs := by
  have h := abs_add_le (a + α) (-(b + α))
  rw [Rat.abs_neg] at h
  have heq : (a + α) + -(b + α) = a - b := by grind
  rw [heq] at h
  exact h

theorem diag_l1_not_above (a b α : Rat)
    (heq : (a + α).abs + (b + α).abs = (a - b).abs)
    (hhi : ¬ α ≤ -min a b) : False := by
  have hltmin : -min a b < α := (Rat.not_le).mp hhi
  have hpos : 0 < min a b + α := by
    have hlt := (Rat.add_lt_add_left (c := min a b)).mpr hltmin
    rw [Rat.add_neg_cancel] at hlt
    exact hlt
  have ha : 0 ≤ a + α :=
    Rat.le_trans (Rat.le_of_lt hpos)
      ((Rat.add_le_add_right (c := α)).mpr (min_le_left a b))
  have hb : 0 ≤ b + α :=
    Rat.le_trans (Rat.le_of_lt hpos)
      ((Rat.add_le_add_right (c := α)).mpr (min_le_right a b))
  rw [Rat.abs_of_nonneg ha, Rat.abs_of_nonneg hb] at heq
  have hexcess : a + α + (b + α) - (max a b - min a b) = 2 * (α + min a b) := by
    have hadd := max_add_min a b
    grind
  have hdiff0 : a + α + (b + α) - (a - b).abs = 0 := by
    rw [heq, Rat.sub_self]
  rw [max_sub_min a b] at hexcess
  have hzero : 2 * (α + min a b) = 0 := hexcess.symm.trans hdiff0
  have hpos2 : 0 < α + min a b := by
    rw [Rat.add_comm] at hpos
    exact hpos
  exact absurd hzero (Rat.ne_of_gt (Rat.mul_pos two_pos hpos2))

theorem diag_l1_not_below (a b α : Rat)
    (heq : (a + α).abs + (b + α).abs = (a - b).abs)
    (hlo : ¬ -max a b ≤ α) : False := by
  have hα : α < -max a b := (Rat.not_le).mp hlo
  have hsumneg : max a b + α < 0 := by
    have hlt := (Rat.add_lt_add_left (c := max a b)).mpr hα
    rw [Rat.add_neg_cancel] at hlt
    exact hlt
  have hsumle : max a b + α ≤ 0 := Rat.le_of_lt hsumneg
  have ha : a + α ≤ 0 :=
    Rat.le_trans ((Rat.add_le_add_right (c := α)).mpr (le_max_left a b)) hsumle
  have hb : b + α ≤ 0 :=
    Rat.le_trans ((Rat.add_le_add_right (c := α)).mpr (le_max_right a b)) hsumle
  rw [Rat.abs_of_nonpos ha, Rat.abs_of_nonpos hb] at heq
  have hexcess : -(a + α) + -(b + α) - (max a b - min a b) = 2 * (-max a b - α) := by
    have hadd := max_add_min a b
    grind
  have hdiff0 : -(a + α) + -(b + α) - (a - b).abs = 0 := by
    rw [heq, Rat.sub_self]
  rw [max_sub_min a b] at hexcess
  have hzero : 2 * (-max a b - α) = 0 := hexcess.symm.trans hdiff0
  have hpos : 0 < -max a b - α := by
    have hlt := (Rat.add_lt_add_right (c := -α)).mpr hα
    rw [Rat.add_neg_cancel] at hlt
    rw [Rat.sub_eq_add_neg]
    exact hlt
  exact absurd hzero (Rat.ne_of_gt (Rat.mul_pos two_pos hpos))

/-- LGR-R3, ell-one: the residual sum equals `|a-b|` exactly on the closed interval. -/
theorem diag_l1_iff (a b α : Rat) :
    (a + α).abs + (b + α).abs = (a - b).abs ↔ -max a b ≤ α ∧ α ≤ -min a b := by
  constructor
  · intro heq
    refine ⟨?_, ?_⟩
    · by_cases hlo : -max a b ≤ α
      · exact hlo
      · exact absurd heq (fun h => diag_l1_not_below a b α h hlo)
    · by_cases hhi : α ≤ -min a b
      · exact hhi
      · exact absurd heq (fun h => diag_l1_not_above a b α h hhi)
  · intro h
    rcases h with ⟨hlo, hhi⟩
    by_cases hab : a ≤ b
    · rw [max_eq_right hab] at hlo
      rw [min_eq_left hab] at hhi
      have ha0 : a + α ≤ 0 := by
        have h' := (Rat.add_le_add_left (c := a)).mpr hhi
        rw [Rat.add_neg_cancel] at h'
        exact h'
      have hb0 : 0 ≤ b + α := by
        have h' := (Rat.add_le_add_left (c := b)).mpr hlo
        rw [Rat.add_neg_cancel] at h'
        exact h'
      rw [Rat.abs_of_nonpos ha0, Rat.abs_of_nonneg hb0]
      have hsub : a - b ≤ 0 := by
        have h' := (Rat.add_le_add_right (c := -b)).mpr hab
        rw [Rat.add_neg_cancel] at h'
        rw [Rat.sub_eq_add_neg]
        exact h'
      rw [Rat.abs_of_nonpos hsub]
      grind
    · have hba : b ≤ a := Rat.le_of_lt (Rat.not_le.mp hab)
      rw [max_eq_left hba] at hlo
      rw [min_eq_right hba] at hhi
      have hb0 : b + α ≤ 0 := by
        have h' := (Rat.add_le_add_left (c := b)).mpr hhi
        rw [Rat.add_neg_cancel] at h'
        exact h'
      have ha0 : 0 ≤ a + α := by
        have h' := (Rat.add_le_add_left (c := a)).mpr hlo
        rw [Rat.add_neg_cancel] at h'
        exact h'
      rw [Rat.abs_of_nonpos hb0, Rat.abs_of_nonneg ha0]
      have hsub : 0 ≤ a - b := sub_nonneg_of_le hba
      rw [Rat.abs_of_nonneg hsub]
      grind

/-- LGR-R3, squared Euclidean norm. Equality holds only at the midpoint. -/
theorem diag_l2_sq_iff (a b α : Rat) :
    2 * ((a + α) ^ 2 + (b + α) ^ 2) = (a - b) ^ 2 ↔ α = -(a + b) / 2 := by
  constructor
  · intro h
    have hclear := diag_l2_cleared a b α
    have hsq : (2 * α + a + b) ^ 2 = 0 := by grind
    have hlin : 2 * α + a + b = 0 := (sq_eq_zero_iff _).mp hsq
    grind
  · intro h
    have hclear := diag_l2_cleared a b α
    grind

theorem sq_nonneg (a : Rat) : 0 ≤ a ^ 2 := by
  have hpow : a ^ 2 = a * a := by
    have h2 : (2 : Nat) = 1 + 1 := by decide
    rw [h2, Rat.pow_succ, Rat.pow_one]
  rw [hpow]
  by_cases h : 0 ≤ a
  · exact Rat.mul_nonneg h h
  · have ha : a ≤ 0 := Rat.le_of_lt (Rat.not_le.mp h)
    have heq : a * a = (-a) * (-a) := by grind
    rw [heq]
    exact Rat.mul_nonneg (nonneg_neg_of_nonpos ha) (nonneg_neg_of_nonpos ha)

theorem diag_l2_sq_ge (a b α : Rat) :
    (a - b) ^ 2 ≤ 2 * ((a + α) ^ 2 + (b + α) ^ 2) := by
  have hclear := diag_l2_cleared a b α
  have hsq : 0 ≤ (2 * α + a + b) ^ 2 := sq_nonneg _
  rw [hclear]
  have hle :=
    (Rat.add_le_add_right (a := 0) (b := (2 * α + a + b) ^ 2) (c := (a - b) ^ 2)).mpr hsq
  rw [Rat.zero_add] at hle
  exact hle

/-- LGR-R3, supremum norm. -/
theorem diag_linf_iff (a b α : Rat) :
    max (a + α).abs (b + α).abs = (a - b).abs / 2 ↔ α = -(a + b) / 2 := by
  constructor
  · intro h
    have h1 : (a + α).abs ≤ (a - b).abs / 2 := by
      have hmax := le_max_left (a + α).abs (b + α).abs
      rw [h] at hmax
      exact hmax
    have h2 : (b + α).abs ≤ (a - b).abs / 2 := by
      have hmax := le_max_right (a + α).abs (b + α).abs
      rw [h] at hmax
      exact hmax
    have hsumle : (a + α).abs + (b + α).abs ≤ (a - b).abs := by
      have s1 := (Rat.add_le_add_right (c := (b + α).abs)).mpr h1
      have s2 := (Rat.add_le_add_left (c := (a - b).abs / 2)).mpr h2
      have htrans := Rat.le_trans s1 s2
      have hhalf : (a - b).abs / 2 + (a - b).abs / 2 = (a - b).abs := by grind
      rw [hhalf] at htrans
      exact htrans
    have htri := diag_l1_ge a b α
    have hsum : (a + α).abs + (b + α).abs = (a - b).abs :=
      Rat.le_antisymm hsumle htri
    have hbetween := (diag_l1_iff a b α).mp hsum
    have hA : (a + α).abs = (a - b).abs / 2 := by
      have hAge : (a - b).abs / 2 ≤ (a + α).abs := by
        have hB : 0 ≤ (a - b).abs / 2 - (b + α).abs := sub_nonneg_of_le h2
        have hid : (a - b).abs - (b + α).abs =
            (a - b).abs / 2 + ((a - b).abs / 2 - (b + α).abs) := by grind
        have hAeq : (a + α).abs = (a - b).abs - (b + α).abs := by grind
        rw [hAeq, hid]
        have hle := (Rat.add_le_add_left (c := (a - b).abs / 2)).mpr hB
        rw [Rat.add_zero] at hle
        exact hle
      exact Rat.le_antisymm h1 hAge
    have hB : (b + α).abs = (a - b).abs / 2 := by
      have hsum' : (a + α).abs + (b + α).abs = (a - b).abs := hsum
      grind
    rcases hbetween with ⟨hlo, hhi⟩
    by_cases hab : a ≤ b
    · rw [max_eq_right hab] at hlo
      rw [min_eq_left hab] at hhi
      have ha0 : a + α ≤ 0 := by
        have h' := (Rat.add_le_add_left (c := a)).mpr hhi
        rw [Rat.add_neg_cancel] at h'
        exact h'
      have hb0 : 0 ≤ b + α := by
        have h' := (Rat.add_le_add_left (c := b)).mpr hlo
        rw [Rat.add_neg_cancel] at h'
        exact h'
      rw [Rat.abs_of_nonpos ha0] at hA
      rw [Rat.abs_of_nonneg hb0] at hB
      have hopp : a + α + (b + α) = 0 := by grind
      grind
    · have hba : b ≤ a := Rat.le_of_lt (Rat.not_le.mp hab)
      rw [max_eq_left hba] at hlo
      rw [min_eq_right hba] at hhi
      have hb0 : b + α ≤ 0 := by
        have h' := (Rat.add_le_add_left (c := b)).mpr hhi
        rw [Rat.add_neg_cancel] at h'
        exact h'
      have ha0 : 0 ≤ a + α := by
        have h' := (Rat.add_le_add_left (c := a)).mpr hlo
        rw [Rat.add_neg_cancel] at h'
        exact h'
      rw [Rat.abs_of_nonpos hb0] at hB
      rw [Rat.abs_of_nonneg ha0] at hA
      have hopp : a + α + (b + α) = 0 := by grind
      grind
  · intro h
    rw [h]
    have hleft : a + -(a + b) / 2 = (a - b) / 2 := by grind
    have hright : b + -(a + b) / 2 = -((a - b) / 2) := by grind
    rw [hleft, hright, Rat.abs_neg, max_self, abs_div_two]

theorem abs_align_iff (u v : Rat) : (u + v).abs = u.abs + v.abs ↔ 0 ≤ u * v := by
  constructor
  · intro h
    by_cases hu : 0 ≤ u <;> by_cases hv : 0 ≤ v
    · exact Rat.mul_nonneg hu hv
    · have hv0 : v ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hv)
      by_cases huv : 0 ≤ u + v
      · rw [Rat.abs_of_nonneg hu, Rat.abs_of_nonpos hv0, Rat.abs_of_nonneg huv] at h
        have hvz : v = 0 := by grind
        exact absurd (show 0 ≤ v from hvz.symm ▸ (Rat.le_refl : (0 : Rat) ≤ 0)) hv
      · rw [Rat.abs_of_nonneg hu, Rat.abs_of_nonpos hv0,
          Rat.abs_of_nonpos (Rat.le_of_lt (Rat.not_le.mp huv))] at h
        have huz : u = 0 := by grind
        rw [huz, Rat.zero_mul]
        exact Rat.le_refl
    · have hu0 : u ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hu)
      by_cases huv : 0 ≤ u + v
      · rw [Rat.abs_of_nonpos hu0, Rat.abs_of_nonneg hv, Rat.abs_of_nonneg huv] at h
        have huz : u = 0 := by grind
        exact absurd (show 0 ≤ u from huz.symm ▸ (Rat.le_refl : (0 : Rat) ≤ 0)) hu
      · rw [Rat.abs_of_nonpos hu0, Rat.abs_of_nonneg hv,
          Rat.abs_of_nonpos (Rat.le_of_lt (Rat.not_le.mp huv))] at h
        have hvz : v = 0 := by grind
        rw [hvz, Rat.mul_zero]
        exact Rat.le_refl
    · have hu0 : u ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hu)
      have hv0 : v ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hv)
      have heq : u * v = (-u) * (-v) := by grind
      rw [heq]
      exact Rat.mul_nonneg (nonneg_neg_of_nonpos hu0) (nonneg_neg_of_nonpos hv0)
  · intro h
    by_cases hu : 0 ≤ u <;> by_cases hv : 0 ≤ v
    · rw [Rat.abs_of_nonneg hu, Rat.abs_of_nonneg hv, Rat.abs_of_nonneg (Rat.add_nonneg hu hv)]
    · have hv0 : v ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hv)
      have hle : u * v ≤ 0 := by
        have hnn : 0 ≤ u * -v := Rat.mul_nonneg hu (nonneg_neg_of_nonpos hv0)
        have heq : u * -v = -(u * v) := Rat.mul_neg u v
        rw [heq] at hnn
        have hstep : u * v ≤ -0 := (Rat.le_neg_iff (a := 0) (b := u * v)).mp hnn
        rw [Rat.neg_zero] at hstep
        exact hstep
      have h0 : u * v = 0 := Rat.le_antisymm hle h
      rcases (Rat.mul_eq_zero).mp h0 with hu0 | hvz
      · rw [hu0, Rat.zero_add, Rat.abs_zero, Rat.zero_add]
      · rw [hvz, Rat.add_zero, Rat.abs_zero, Rat.add_zero]
    · have hu0 : u ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hu)
      have hle : u * v ≤ 0 := by
        have hnn : 0 ≤ -u * v := Rat.mul_nonneg (nonneg_neg_of_nonpos hu0) hv
        have heq : -u * v = -(u * v) := Rat.neg_mul u v
        rw [heq] at hnn
        have hstep : u * v ≤ -0 := (Rat.le_neg_iff (a := 0) (b := u * v)).mp hnn
        rw [Rat.neg_zero] at hstep
        exact hstep
      have h0 : u * v = 0 := Rat.le_antisymm hle h
      rcases (Rat.mul_eq_zero).mp h0 with hu0' | hvz
      · rw [hu0', Rat.zero_add, Rat.abs_zero, Rat.zero_add]
      · rw [hvz, Rat.add_zero, Rat.abs_zero, Rat.add_zero]
    · have hu0 : u ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hu)
      have hv0 : v ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hv)
      rw [Rat.abs_of_nonpos hu0, Rat.abs_of_nonpos hv0, Rat.abs_of_nonpos (add_nonpos hu0 hv0)]
      grind

theorem diag_zero_l1_iff (a b : Rat) :
    a.abs + b.abs = (a - b).abs ↔ a * b ≤ 0 := by
  have h := abs_align_iff a (-b)
  rw [Rat.abs_neg] at h
  have hsum : a + -b = a - b := by grind
  rw [hsum] at h
  rw [Rat.mul_neg] at h
  constructor
  · intro heq
    have hnn : 0 ≤ -(a * b) := h.mp heq.symm
    have hle : a * b ≤ -0 := (Rat.le_neg_iff (a := 0) (b := a * b)).mp hnn
    rw [Rat.neg_zero] at hle
    exact hle
  · intro hle
    have hnn : 0 ≤ -(a * b) := by
      rw [← Rat.neg_zero] at hle
      exact (Rat.le_neg_iff).mpr hle
    exact (h.mpr hnn).symm

theorem diag_zero_l2_iff (a b : Rat) :
    a ^ 2 + b ^ 2 = (a - b) ^ 2 / 2 ↔ a + b = 0 := by
  have h := diag_l2_sq_iff a b 0
  constructor
  · intro heq
    have hclear : 2 * (a ^ 2 + b ^ 2) = (a - b) ^ 2 := by
      have hmul := congrArg (fun z : Rat => 2 * z) heq
      grind
    have hmid := h.mp (by grind)
    grind
  · intro hsum
    have hmid := h.mpr (by grind)
    grind

theorem diag_zero_linf_iff (a b : Rat) :
    max a.abs b.abs = (a - b).abs / 2 ↔ a + b = 0 := by
  have h := diag_linf_iff a b 0
  constructor
  · intro heq
    have hmid := h.mp (by
      rw [Rat.add_zero, Rat.add_zero]
      exact heq)
    grind
  · intro hsum
    have heq := h.mpr (by grind)
    rw [Rat.add_zero, Rat.add_zero] at heq
    exact heq

theorem diag_vanish_iff (a b : Rat) :
    (a - b).abs = 0 ∧ (a - b) ^ 2 / 2 = 0 ∧ (a - b).abs / 2 = 0 ↔ a = b := by
  constructor
  · intro h
    have hz : a - b = 0 := (Rat.abs_eq_zero_iff).mp h.1
    grind
  · intro h
    have hz : a - b = 0 := by grind
    refine ⟨?_, ?_, ?_⟩
    · rw [hz, Rat.abs_zero]
    · rw [hz]
      grind
    · rw [hz, Rat.abs_zero]
      grind

/-- LGR-R2 is the pair `(1, -1)` on the diagonal image. -/
theorem r2_l1_iff (α : Rat) :
    ((1 : Rat) + α).abs + (α - 1).abs = 2 ↔ -1 ≤ α ∧ α ≤ 1 := by
  have h := diag_l1_iff (1 : Rat) (-1) α
  have hord : (-1 : Rat) ≤ 1 := by decide
  have hmax : max (1 : Rat) (-1) = 1 := max_eq_left hord
  have hmin : min (1 : Rat) (-1) = -1 := min_eq_right hord
  have habs : (α - 1).abs = ((-1 : Rat) + α).abs := by
    have heq : α - 1 = (-1 : Rat) + α := by grind
    rw [heq]
  have hgap : ((1 : Rat) - (-1)).abs = 2 := by
    have heq : (1 : Rat) - (-1) = 2 := by grind
    rw [heq, Rat.abs_of_nonneg two_nonneg]
  rw [← habs] at h
  rw [hgap] at h
  rw [hmax] at h
  rw [hmin] at h
  rw [Rat.neg_neg] at h
  exact h

theorem r2_l2_sq (α : Rat) : ((1 : Rat) + α) ^ 2 + (α - 1) ^ 2 = 2 * α ^ 2 + 2 := by
  grind

theorem r2_l2_sq_iff (α : Rat) :
    ((1 : Rat) + α) ^ 2 + (α - 1) ^ 2 = 2 ↔ α = 0 := by
  have hid := r2_l2_sq α
  constructor
  · intro h
    have hsq : α ^ 2 = 0 := by grind
    exact (sq_eq_zero_iff α).mp hsq
  · intro h
    rw [h]
    grind

theorem r2_linf_iff (α : Rat) :
    max ((1 : Rat) + α).abs (α - 1).abs = 1 ↔ α = 0 := by
  have h := diag_linf_iff (1 : Rat) (-1) α
  have habs : (α - 1).abs = ((-1 : Rat) + α).abs := by
    have heq : α - 1 = (-1 : Rat) + α := by grind
    rw [heq]
  have hgap : ((1 : Rat) - (-1)).abs / 2 = 1 := by
    have heq : (1 : Rat) - (-1) = 2 := by grind
    rw [heq, Rat.abs_of_nonneg two_nonneg]
    grind
  have hmid : -((1 : Rat) + -1) / 2 = 0 := by grind
  rw [← habs] at h
  rw [hgap] at h
  rw [hmid] at h
  exact h

theorem skew_l1_ge (a b α : Rat) :
    (2 * a - b).abs ≤ 2 * (a + α).abs + (b + 2 * α).abs := by
  have h := abs_add_le (2 * (a + α)) (-(b + 2 * α))
  rw [Rat.abs_neg] at h
  rw [abs_two_mul (a + α)] at h
  have heq : 2 * (a + α) + -(b + 2 * α) = 2 * a - b := by grind
  rw [heq] at h
  exact h

theorem skew_loose (x y : Rat) : 2 * x.abs + y.abs ≤ 2 * (x.abs + y.abs) := by
  have hy : y.abs ≤ 2 * y.abs := by
    have hle := (Rat.add_le_add_left (c := y.abs)).mpr (Rat.abs_nonneg (x := y))
    rw [Rat.add_zero] at hle
    have heq : y.abs + y.abs = 2 * y.abs := by grind
    rw [← heq]
    exact hle
  have hstep := (Rat.add_le_add_left (c := 2 * x.abs)).mpr hy
  have heq : 2 * x.abs + 2 * y.abs = 2 * (x.abs + y.abs) := by grind
  rw [heq] at hstep
  exact hstep

theorem skew_l1_iff (a b α : Rat) :
    2 * ((a + α).abs + (b + 2 * α).abs) = (2 * a - b).abs ↔ α = -b / 2 := by
  constructor
  · intro h
    let x := a + α
    have hx : x = a + α := rfl
    let y := b + 2 * α
    have hy : y = b + 2 * α := rfl
    have htight : (2 * a - b).abs ≤ 2 * x.abs + y.abs := by
      rw [hx, hy]
      exact skew_l1_ge a b α
    have hloose : 2 * x.abs + y.abs ≤ 2 * (x.abs + y.abs) := skew_loose x y
    have hscaled : 2 * (x.abs + y.abs) = (2 * a - b).abs := by
      rw [hx, hy]
      exact h
    have hle : 2 * (x.abs + y.abs) ≤ 2 * x.abs + y.abs := by
      rw [hscaled]
      exact htight
    have heqsum : 2 * x.abs + y.abs = 2 * (x.abs + y.abs) := Rat.le_antisymm hloose hle
    have hy0 : y.abs = 0 := by grind
    have hyz : y = 0 := (Rat.abs_eq_zero_iff).mp hy0
    have : b + 2 * α = 0 := by rw [← hy, hyz]
    grind
  · intro h
    rw [h]
    have hy : b + 2 * (-b / 2) = 0 := by grind
    have hx : 2 * (a + -b / 2) = 2 * a - b := by grind
    rw [hy, Rat.abs_zero, Rat.add_zero, ← hx, abs_two_mul]

theorem skew_l2_sq_iff (a b α : Rat) :
    5 * ((a + α) ^ 2 + (b + 2 * α) ^ 2) = (2 * a - b) ^ 2 ↔ α = -(a + 2 * b) / 5 := by
  constructor
  · intro h
    have hclear := skew_l2_cleared a b α
    have hsq : (5 * α + a + 2 * b) ^ 2 = 0 := by grind
    have hlin : 5 * α + a + 2 * b = 0 := (sq_eq_zero_iff _).mp hsq
    grind
  · intro h
    have hclear := skew_l2_cleared a b α
    grind

theorem skew_l2_sq_ge (a b α : Rat) :
    (2 * a - b) ^ 2 ≤ 5 * ((a + α) ^ 2 + (b + 2 * α) ^ 2) := by
  have hclear := skew_l2_cleared a b α
  have hsq : 0 ≤ (5 * α + a + 2 * b) ^ 2 := sq_nonneg _
  rw [hclear]
  have hle :=
    (Rat.add_le_add_right (a := 0) (b := (5 * α + a + 2 * b) ^ 2) (c := (2 * a - b) ^ 2)).mpr hsq
  rw [Rat.zero_add] at hle
  exact hle

theorem two_mul_add_nonneg_eq_zero {p q : Rat} (hp : 0 ≤ p) (hq : 0 ≤ q)
    (h : 2 * p + q = 0) : p = 0 ∧ q = 0 := by
  have h2p : 0 ≤ 2 * p := Rat.mul_nonneg two_nonneg hp
  have h2p_le : 2 * p ≤ 0 := by
    have hneg : 2 * p = -q := by grind
    rw [hneg]
    have hnq : -q ≤ -0 := (Rat.neg_le_neg_iff).mpr hq
    rw [Rat.neg_zero] at hnq
    exact hnq
  have h2p0 : 2 * p = 0 := Rat.le_antisymm h2p_le h2p
  have hp0 : p = 0 := (Rat.mul_eq_zero.mp h2p0).resolve_left two_ne_zero
  have hq0 : q = 0 := by
    rw [hp0, Rat.mul_zero, Rat.zero_add] at h
    exact h
  exact ⟨hp0, hq0⟩

theorem mul_le_zero_of_neg_two_mul_nonneg {z : Rat} (h : 0 ≤ -(2 * z)) : z ≤ 0 := by
  have h2 : 2 * z ≤ 0 := by
    have hle : 2 * z ≤ -0 := (Rat.le_neg_iff (a := 0) (b := 2 * z)).mp h
    rw [Rat.neg_zero] at hle
    exact hle
  have hstep := Rat.mul_le_mul_of_nonneg_left h2 inv_two_nonneg
  rw [Rat.mul_zero, ← Rat.mul_assoc, Rat.inv_mul_cancel _ two_ne_zero, Rat.one_mul] at hstep
  exact hstep

theorem neg_of_abs_eq_and_mul_nonpos {x y : Rat}
    (habs : x.abs = y.abs) (hprod : x * y ≤ 0) : y = -x := by
  by_cases hx : 0 ≤ x
  · by_cases hy : 0 ≤ y
    · have h0 : x * y = 0 := Rat.le_antisymm hprod (Rat.mul_nonneg hx hy)
      rcases (Rat.mul_eq_zero).mp h0 with hx0 | hy0
      · rw [hx0, Rat.neg_zero]
        have hz : y.abs = 0 := by rw [← habs, hx0, Rat.abs_zero]
        exact (Rat.abs_eq_zero_iff).mp hz
      · rw [hy0]
        have hz : x = 0 := by
          have habs0 : x.abs = 0 := by rw [habs, hy0, Rat.abs_zero]
          exact (Rat.abs_eq_zero_iff).mp habs0
        rw [hz, Rat.neg_zero]
    · have hy0 : y ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hy)
      rw [Rat.abs_of_nonneg hx, Rat.abs_of_nonpos hy0] at habs
      grind
  · have hx0 : x ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hx)
    by_cases hy : 0 ≤ y
    · rw [Rat.abs_of_nonpos hx0, Rat.abs_of_nonneg hy] at habs
      grind
    · have hy0 : y ≤ 0 := Rat.le_of_lt (Rat.not_le.mp hy)
      have hnn : 0 ≤ x * y := by
        have heq : x * y = (-x) * (-y) := by grind
        rw [heq]
        exact Rat.mul_nonneg (nonneg_neg_of_nonpos hx0) (nonneg_neg_of_nonpos hy0)
      have h0 : x * y = 0 := Rat.le_antisymm hprod hnn
      rcases (Rat.mul_eq_zero).mp h0 with hx0' | hy0'
      · rw [hx0', Rat.neg_zero]
        have hz : y.abs = 0 := by rw [← habs, hx0', Rat.abs_zero]
        exact (Rat.abs_eq_zero_iff).mp hz
      · have hz : x = 0 := by
          have habs0 : x.abs = 0 := by rw [habs, hy0', Rat.abs_zero]
          exact (Rat.abs_eq_zero_iff).mp habs0
        rw [hy0', hz, Rat.neg_zero]

/-- LGR-R4, supremum norm on the line `(-α, -2α)`. -/
theorem skew_linf_iff (a b α : Rat) :
    max (a + α).abs (b + 2 * α).abs = (2 * a - b).abs / 3 ↔ α = -(a + b) / 3 := by
  constructor
  · intro h
    let x := a + α
    have hx : x = a + α := rfl
    let y := b + 2 * α
    have hy : y = b + 2 * α := rfl
    let H := (2 * a - b).abs / 3
    have hH : H = (2 * a - b).abs / 3 := rfl
    have hmax : max x.abs y.abs = H := by
      rw [hx, hy, hH]
      exact h
    have hxle : x.abs ≤ H := by
      have hmaxl := le_max_left x.abs y.abs
      rw [hmax] at hmaxl
      exact hmaxl
    have hyle : y.abs ≤ H := by
      have hmaxr := le_max_right x.abs y.abs
      rw [hmax] at hmaxr
      exact hmaxr
    have htri : (2 * x - y).abs ≤ 2 * x.abs + y.abs := by
      have hadd := abs_add_le (2 * x) (-y)
      rw [Rat.abs_neg] at hadd
      rw [abs_two_mul x] at hadd
      have heq : 2 * x + -y = 2 * x - y := by grind
      rw [heq] at hadd
      exact hadd
    have hconst : 2 * x - y = 2 * a - b := by
      rw [hx, hy]
      grind
    have hloose : 2 * x.abs + y.abs ≤ (2 * a - b).abs := by
      have s1 := (Rat.add_le_add_right (c := y.abs)).mpr
        (Rat.mul_le_mul_of_nonneg_left hxle two_nonneg)
      have s2 := (Rat.add_le_add_left (c := 2 * H)).mpr hyle
      have htrans := Rat.le_trans s1 s2
      have hthree : 2 * H + H = 3 * H := by grind
      have hclear : 3 * H = (2 * a - b).abs := by
        rw [hH]
        grind
      rw [hthree, hclear] at htrans
      exact htrans
    have htight : (2 * a - b).abs ≤ 2 * x.abs + y.abs := by
      rw [← hconst]
      exact htri
    have heqsum : 2 * x.abs + y.abs = (2 * a - b).abs := Rat.le_antisymm hloose htight
    have hslack : 2 * (H - x.abs) + (H - y.abs) = 0 := by
      have hthree : (2 * a - b).abs = 3 * H := by
        rw [hH]
        grind
      grind
    have hslacks := two_mul_add_nonneg_eq_zero (sub_nonneg_of_le hxle) (sub_nonneg_of_le hyle) hslack
    have hxH : x.abs = H := by
      have : H - x.abs = 0 := hslacks.1
      grind
    have hyH : y.abs = H := by
      have : H - y.abs = 0 := hslacks.2
      grind
    have habs : x.abs = y.abs := by rw [hxH, hyH]
    have halign : (2 * x + -y).abs = (2 * x).abs + (-y).abs := by
      rw [Rat.abs_neg, abs_two_mul x]
      have heq : 2 * x + -y = 2 * x - y := by grind
      rw [heq, hconst]
      exact heqsum.symm
    have hprod2 : 0 ≤ (2 * x) * (-y) := (abs_align_iff (2 * x) (-y)).mp halign
    have hprod : x * y ≤ 0 := by
      have heq : (2 * x) * (-y) = -(2 * (x * y)) := by grind
      rw [heq] at hprod2
      exact mul_le_zero_of_neg_two_mul_nonneg hprod2
    have hopp : y = -x := neg_of_abs_eq_and_mul_nonpos habs hprod
    rw [hy, hx] at hopp
    grind
  · intro h
    rw [h]
    have hx : a + -(a + b) / 3 = (2 * a - b) / 3 := by grind
    have hy : b + 2 * (-(a + b) / 3) = -((2 * a - b) / 3) := by grind
    rw [hx, hy, Rat.abs_neg, max_self]
    exact abs_div_ofNat (2 * a - b) (n := 3) (by decide)

theorem skew_vanish_iff (a b : Rat) :
    (2 * a - b).abs / 2 = 0 ∧ (2 * a - b) ^ 2 / 5 = 0 ∧ (2 * a - b).abs / 3 = 0 ↔ b = 2 * a := by
  constructor
  · intro h
    have hz : (2 * a - b).abs = 0 := by
      have hmul := congrArg (fun z : Rat => 2 * z) h.1
      grind
    have hlin : 2 * a - b = 0 := (Rat.abs_eq_zero_iff).mp hz
    grind
  · intro h
    have hz : 2 * a - b = 0 := by grind
    refine ⟨?_, ?_, ?_⟩
    · rw [hz, Rat.abs_zero]
      grind
    · rw [hz]
      grind
    · rw [hz, Rat.abs_zero]
      grind

theorem skew_points_coincide_iff (a b : Rat) :
    -b / 2 = -(a + 2 * b) / 5 ∧ -b / 2 = -(a + b) / 3 ↔ b = 2 * a := by
  grind

theorem skew_pair_values :
    (2 * (1 : Rat) - (-1)).abs / 2 = 3 / 2 ∧
      (2 * (1 : Rat) - (-1)) ^ 2 / 5 = 9 / 5 ∧
      (2 * (1 : Rat) - (-1)).abs / 3 = 1 ∧
      -(-1 : Rat) / 2 = 1 / 2 ∧
      -((1 : Rat) + 2 * (-1)) / 5 = 1 / 5 ∧
      -((1 : Rat) + (-1)) / 3 = 0 := by
  have hlin : 2 * (1 : Rat) - (-1) = 3 := by grind
  have habs : (2 * (1 : Rat) - (-1)).abs = 3 := by
    rw [hlin]
    exact Rat.abs_of_nonneg (Rat.natCast_nonneg (a := 3))
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · rw [habs]
  · rw [hlin]; grind
  · rw [habs]; grind
  · grind
  · grind
  · grind

theorem skew_zero_l1_iff (a b : Rat) :
    a.abs + b.abs = (2 * a - b).abs / 2 ↔ b = 0 := by
  constructor
  · intro h
    have hclear : 2 * (a.abs + b.abs) = (2 * a - b).abs := by
      have hmul := congrArg (fun z : Rat => 2 * z) h
      grind
    have hα := (skew_l1_iff a b 0).mp (by
      rw [Rat.add_zero, show (2 : Rat) * 0 = 0 from Rat.mul_zero 2, Rat.add_zero]
      exact hclear)
    grind
  · intro hb
    rw [hb, Rat.abs_zero, Rat.add_zero]
    have heq : (2 * a - 0).abs = (2 * a).abs := by grind
    rw [heq, abs_two_mul]
    grind

theorem skew_zero_l2_iff (a b : Rat) :
    a ^ 2 + b ^ 2 = (2 * a - b) ^ 2 / 5 ↔ a + 2 * b = 0 := by
  have h := skew_l2_sq_iff a b 0
  constructor
  · intro heq
    have hclear : 5 * (a ^ 2 + b ^ 2) = (2 * a - b) ^ 2 := by
      have hmul := congrArg (fun z : Rat => 5 * z) heq
      grind
    have hmid := h.mp (by grind)
    grind
  · intro hsum
    have hmid := h.mpr (by grind)
    grind

theorem skew_zero_linf_iff (a b : Rat) :
    max a.abs b.abs = (2 * a - b).abs / 3 ↔ a + b = 0 := by
  have h := skew_linf_iff a b 0
  constructor
  · intro heq
    have hmid := h.mp (by
      rw [Rat.add_zero, show (2 : Rat) * 0 = 0 from Rat.mul_zero 2, Rat.add_zero]
      exact heq)
    grind
  · intro hsum
    have heq := h.mpr (by grind)
    rw [show (2 : Rat) * 0 = 0 from Rat.mul_zero 2, Rat.add_zero, Rat.add_zero] at heq
    exact heq

end MinkowskiRepair

#print axioms MinkowskiRepair.diag_l1_iff
#print axioms MinkowskiRepair.diag_l2_sq_iff
#print axioms MinkowskiRepair.diag_linf_iff
#print axioms MinkowskiRepair.diag_zero_l1_iff
#print axioms MinkowskiRepair.diag_zero_l2_iff
#print axioms MinkowskiRepair.diag_zero_linf_iff
#print axioms MinkowskiRepair.diag_vanish_iff
#print axioms MinkowskiRepair.r2_l1_iff
#print axioms MinkowskiRepair.r2_l2_sq_iff
#print axioms MinkowskiRepair.r2_linf_iff
#print axioms MinkowskiRepair.skew_l1_iff
#print axioms MinkowskiRepair.skew_l2_sq_iff
#print axioms MinkowskiRepair.skew_linf_iff
#print axioms MinkowskiRepair.skew_vanish_iff
#print axioms MinkowskiRepair.skew_points_coincide_iff
#print axioms MinkowskiRepair.skew_pair_values
#print axioms MinkowskiRepair.skew_zero_l1_iff
#print axioms MinkowskiRepair.skew_zero_l2_iff
#print axioms MinkowskiRepair.skew_zero_linf_iff
