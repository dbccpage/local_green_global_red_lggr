import Bell.SignedDuality

/-! Packing contextual fraction and constructive comparison with signed mass.
The comparison constructs a feasible local subdistribution; it does not assume LP duality. -/
noncomputable section
open scoped BigOperators
open Set
namespace Bell.ContextualFraction
open Bell.LinearProgramming
variable {I G : Type} [Fintype I] [Fintype G]

def Packing (A : G → I → ℝ) (p : I → ℝ) (q : G → ℝ) : Prop :=
  (∀ g, 0 ≤ q g) ∧ ∀ i, mix A q i ≤ p i

def weights (A : G → I → ℝ) (p : I → ℝ) : Set ℝ :=
  {w | ∃ q, Packing A p q ∧ ∑ g, q g = w}

def fraction (A : G → I → ℝ) (p : I → ℝ) : ℝ :=
  1 - sSup (weights A p)

theorem sum_mix (A : G → I → ℝ) (q : G → ℝ) :
    ∑ i, mix A q i = ∑ g, q g * ∑ i, A g i := by
  simp only [mix, Finset.mul_sum]
  exact Finset.sum_comm

theorem pairing_mix (A : G → I → ℝ) (q : G → ℝ) (y : I → ℝ) :
    pairing y (mix A q) = ∑ g, q g * pairing y (A g) := by
  simp only [pairing, mix, Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro g _
  apply Finset.sum_congr rfl
  intro i _
  ring

theorem packing_mass_le (A : G → I → ℝ) (p : I → ℝ) (m : ℝ)
    (hm : 0 < m) (hcol : ∀ g, ∑ i, A g i = m) (hnorm : ∑ i, p i = m)
    {q : G → ℝ} (hq : Packing A p q) : ∑ g, q g ≤ 1 := by
  have h := Finset.sum_le_sum (fun i (_ : i ∈ Finset.univ) => hq.2 i)
  rw [sum_mix] at h
  simp_rw [hcol] at h
  rw [← Finset.sum_mul, hnorm] at h
  nlinarith

theorem weights_bounded (A : G → I → ℝ) (p : I → ℝ) (m : ℝ)
    (hm : 0 < m) (hcol : ∀ g, ∑ i, A g i = m) (hnorm : ∑ i, p i = m) :
    BddAbove (weights A p) :=
  ⟨1, fun _ ⟨_q,hq,he⟩ => he ▸ packing_mass_le A p m hm hcol hnorm hq⟩

omit [Fintype I] in
theorem zero_packing (A : G → I → ℝ) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    Packing A p (fun _ => 0) := by
  constructor
  · simp
  · simpa [mix] using hp

omit [Fintype I] in
theorem weights_nonempty (A : G → I → ℝ) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    (weights A p).Nonempty :=
  ⟨0, fun _ => 0, zero_packing A p hp, by simp⟩

omit [Fintype I] in
theorem upper_of_packing (A : G → I → ℝ) (p : I → ℝ)
    (hb : BddAbove (weights A p)) {q : G → ℝ} (hq : Packing A p q) :
    fraction A p ≤ 1 - ∑ g, q g := by
  have h := le_csSup hb (show (∑ g, q g) ∈ weights A p from ⟨q,hq,rfl⟩)
  unfold fraction
  linarith

theorem packing_weak_duality (A : G → I → ℝ) (p y : I → ℝ)
    (hy : ∀ i, 0 ≤ y i) (hdual : ∀ g, 1 ≤ pairing y (A g))
    {q : G → ℝ} (hq : Packing A p q) : ∑ g, q g ≤ pairing y p := by
  calc
    ∑ g, q g ≤ ∑ g, q g * pairing y (A g) := by
      apply Finset.sum_le_sum
      intro g _
      simpa using mul_le_mul_of_nonneg_left (hdual g) (hq.1 g)
    _ = pairing y (mix A q) := (pairing_mix A q y).symm
    _ ≤ pairing y p := by
      exact Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (hq.2 i) (hy i))

theorem lower_of_dual (A : G → I → ℝ) (p y : I → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hy : ∀ i, 0 ≤ y i)
    (hdual : ∀ g, 1 ≤ pairing y (A g)) :
    1 - pairing y p ≤ fraction A p := by
  have h := csSup_le (weights_nonempty A p hp) (fun w ⟨q,hq,he⟩ =>
    he ▸ packing_weak_duality A p y hy hdual hq)
  unfold fraction
  linarith

theorem certificate_exact (A : G → I → ℝ) (p y : I → ℝ) (q : G → ℝ)
    (hb : BddAbove (weights A p)) (hp : ∀ i, 0 ≤ p i)
    (hq : Packing A p q) (hy : ∀ i, 0 ≤ y i)
    (hd : ∀ g, 1 ≤ pairing y (A g)) (hgap : pairing y p = ∑ g, q g) :
    fraction A p = 1 - ∑ g, q g := by
  apply le_antisymm (upper_of_packing A p hb hq)
  rw [← hgap]
  exact lower_of_dual A p y hp hy hd

theorem fraction_nonnegative (A : G → I → ℝ) (p : I → ℝ) (m : ℝ)
    (hm : 0 < m) (hcol : ∀ g, ∑ i, A g i = m)
    (hnorm : ∑ i, p i = m) (hp : ∀ i, 0 ≤ p i) : 0 ≤ fraction A p := by
  have h := csSup_le (weights_nonempty A p hp) (fun w ⟨q,hq,he⟩ =>
    he ▸ packing_mass_le A p m hm hcol hnorm hq)
  unfold fraction
  linarith

omit [Fintype I] in
theorem fraction_le_one (A : G → I → ℝ) (p : I → ℝ)
    (hb : BddAbove (weights A p)) (hp : ∀ i, 0 ≤ p i) : fraction A p ≤ 1 := by
  simpa using upper_of_packing A p hb (zero_packing A p hp)

theorem positive_parts (q : G → ℝ) (hn : ∑ g, q g = 1) :
    ∑ g, max (q g) 0 = 1 + Bell.SignedDuality.negativeMass q := by
  have h (x : ℝ) : max x 0 = x + max (-x) 0 := by
    rcases le_total 0 x with hx | hx
    · rw [max_eq_left hx, max_eq_right (by linarith)]; ring
    · rw [max_eq_right hx, max_eq_left (by linarith)]; ring
  have he : (∑ g, max (q g) 0) = ∑ g, (q g + max (-q g) 0) :=
    Finset.sum_congr rfl (fun g _ => h (q g))
  rw [he, Finset.sum_add_distrib, hn]
  rfl

/-- Remove enough positive assignment mass, row by row, to dominate all cancellations. -/
theorem packing_from_signed (A : G → I → ℝ) (p : I → ℝ) (m : ℝ)
    (hA : ∀ g i, A g i = 0 ∨ A g i = 1)
    (hcol : ∀ g, ∑ i, A g i = m) (hp : ∀ i, 0 ≤ p i)
    (q : G → ℝ) (hq : mix A q = p) (hn : ∑ g, q g = 1) :
    ∃ γ, Packing A p γ ∧
      1 - (m-1) * Bell.SignedDuality.negativeMass q ≤ ∑ g, γ g := by
  classical
  let u : G → ℝ := fun g => max (q g) 0
  let n : G → ℝ := fun g => max (-q g) 0
  let s := mix A u
  let r := mix A n
  have hnon : ∀ g i, 0 ≤ A g i := by
    intro g i; rcases hA g i with h | h <;> simp [h]
  have hs : ∀ i, 0 ≤ s i := fun i =>
    Finset.sum_nonneg (fun g _ => mul_nonneg (le_max_right _ _) (hnon g i))
  have hr : ∀ i, 0 ≤ r i := fun i =>
    Finset.sum_nonneg (fun g _ => mul_nonneg (le_max_right _ _) (hnon g i))
  have hdiff : ∀ i, s i - r i = p i := by
    intro i
    have he : ∀ g, u g - n g = q g := by
      intro g; dsimp [u,n]
      rcases le_total 0 (q g) with h | h
      · rw [max_eq_left h, max_eq_right (by linarith)]; ring
      · rw [max_eq_right h, max_eq_left (by linarith)]; ring
    calc
      s i - r i = ∑ g, (u g - n g) * A g i := by
        simp [s,r,mix, sub_mul, Finset.sum_sub_distrib]
      _ = p i := by simp_rw [he]; exact congrFun hq i
  let d : I → ℝ := fun i => if s i = 0 then 0 else r i / s i
  have hd : ∀ i, 0 ≤ d i ∧ d i ≤ 1 := by
    intro i
    dsimp [d]
    split_ifs with hz
    · norm_num
    · have hsp : 0 < s i := lt_of_le_of_ne (hs i) (Ne.symm hz)
      constructor
      · exact div_nonneg (hr i) (hs i)
      · apply (div_le_one hsp).2; have := hdiff i; have := hp i; linarith
  have hsd : ∀ i, s i * d i = r i := by
    intro i
    dsimp [d]
    split_ifs with hz
    · have := hdiff i; have := hp i; have := hr i; nlinarith
    · field_simp
  let loss : G → ℝ := fun g => ∑ i, u g * A g i * d i
  let γ : G → ℝ := fun g => max (u g - loss g) 0
  have hg : ∀ g i, γ g * A g i ≤ u g * A g i * (1-d i) := by
    intro g i
    rcases hA g i with ha | ha
    · simp [ha]
    · rw [ha, mul_one, mul_one]
      have hsingle : u g * d i ≤ loss g := by
        have hh := Finset.single_le_sum
          (s := Finset.univ) (f := fun j => u g * A g j * d j)
          (fun j _ => mul_nonneg (mul_nonneg (le_max_right _ _) (hnon g j)) (hd j).1)
          (Finset.mem_univ i)
        simpa [ha,loss] using hh
      apply max_le
      · nlinarith
      · exact mul_nonneg (le_max_right _ _) (sub_nonneg.mpr (hd i).2)
  refine ⟨γ, ⟨fun g => le_max_right _ _, ?_⟩, ?_⟩
  · intro i
    calc
      mix A γ i ≤ ∑ g, u g * A g i * (1-d i) :=
        Finset.sum_le_sum (fun g _ => hg g i)
      _ = s i - r i := by rw [← Finset.sum_mul]; change s i * (1-d i) = _; rw [mul_sub,mul_one,hsd]
      _ = p i := hdiff i
  · have hloss : ∑ g, loss g = m * Bell.SignedDuality.negativeMass q := by
      dsimp [loss]
      rw [Finset.sum_comm]
      simp_rw [← Finset.sum_mul]
      change (∑ i, s i * d i) = _
      simp_rw [hsd]
      rw [sum_mix]
      simp_rw [hcol]
      rw [← Finset.sum_mul]
      change (Bell.SignedDuality.negativeMass q) * m = _
      ring
    have hγ : (∑ g, u g) - ∑ g, loss g ≤ ∑ g, γ g := by
      rw [← Finset.sum_sub_distrib]
      exact Finset.sum_le_sum (fun g _ => le_max_left _ _)
    have hu : ∑ g, u g = 1 + Bell.SignedDuality.negativeMass q := positive_parts q hn
    rw [hu, hloss] at hγ
    nlinarith

/-- For m contexts, contextual fraction is at most (m-1) times any signed extension's
negative mass. The feasible local subdistribution is constructed explicitly. -/
theorem fraction_le_negative_mass (A : G → I → ℝ) (p : I → ℝ) (m : ℝ)
    (hm : 0 < m) (hA : ∀ g i, A g i = 0 ∨ A g i = 1)
    (hcol : ∀ g, ∑ i, A g i = m) (hnorm : ∑ i, p i = m)
    (hp : ∀ i, 0 ≤ p i) (q : G → ℝ)
    (hq : mix A q = p) (hn : ∑ g, q g = 1) :
    fraction A p ≤ (m-1) * Bell.SignedDuality.negativeMass q := by
  obtain ⟨γ,hγ,hbound⟩ := packing_from_signed A p m hA hcol hp q hq hn
  have hu := upper_of_packing A p (weights_bounded A p m hm hcol hnorm) hγ
  linarith

end Bell.ContextualFraction

