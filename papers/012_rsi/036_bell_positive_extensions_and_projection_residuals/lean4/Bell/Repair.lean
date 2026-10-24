import Bell.LinearProgramming
import Bell.Separable

noncomputable section
open scoped BigOperators
namespace Bell.Repair
attribute [local instance] Classical.propDecidable
open Bell.LinearProgramming Bell.Separable

variable {I G : Type} [Fintype I] [Fintype G]

def weightedCost (w : I → ℝ) (A : G → I → ℝ) (p : I → ℝ) (q : G → ℝ) : ℝ :=
  ∑ i, w i * |p i - mix A q i|

omit [Fintype I] in
theorem scaled_mix (w : I → ℝ) (A : G → I → ℝ) (q : G → ℝ) (i : I) :
    mix (fun g i => w i * A g i) q i = w i * mix A q i := by
  simp only [mix, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro g _; ring

theorem scaled_cost (w : I → ℝ) (hw : ∀ i, 0 ≤ w i) (A : G → I → ℝ)
    (p : I → ℝ) (q : G → ℝ) :
    cost (fun g i => w i * A g i) (fun i => w i * p i) q = weightedCost w A p q := by
  simp only [cost, weightedCost, scaled_mix, ← mul_sub, abs_mul, abs_of_nonneg (hw _)]

theorem scaled_pairing (w y p : I → ℝ) :
    pairing y (fun i => w i * p i) = pairing (fun i => w i * y i) p := by
  unfold pairing
  apply Finset.sum_congr rfl
  intro i _; ring

theorem weighted_weak_duality (w : I → ℝ) (A : G → I → ℝ) (p y : I → ℝ)
    (q : G → ℝ) (z : ℝ) (hq : Bell.Probability q)
    (hy : ∀ i, |y i| ≤ w i) (hz : ∀ g, pairing y (A g) + z ≤ 0) :
    pairing y p + z ≤ weightedCost w A p q := by
  have hm : pairing y (mix A q) + z ≤ 0 := by
    have he : pairing y (mix A q) = ∑ g, q g * pairing y (A g) := by
      simp only [pairing, mix, Finset.mul_sum]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro g _
      apply Finset.sum_congr rfl
      intro i _; ring
    rw [he]
    have hh := Finset.sum_nonpos (s := Finset.univ) (fun g _ =>
      mul_nonpos_of_nonneg_of_nonpos (hq.nonneg g) (hz g))
    simpa only [mul_add, Finset.sum_add_distrib, ← Finset.sum_mul, hq.total, one_mul] using hh
  have hr : pairing y p - pairing y (mix A q) ≤ weightedCost w A p q := by
    simp only [pairing, weightedCost, ← Finset.sum_sub_distrib, ← mul_sub]
    exact Finset.sum_le_sum fun i _ => (le_abs_self _).trans (by
      rw [abs_mul]; exact mul_le_mul_of_nonneg_right (hy i) (abs_nonneg _))
  linarith

theorem weighted_strong_duality [Nonempty G] (w : I → ℝ) (hw : ∀ i, 0 ≤ w i)
    (A : G → I → ℝ) (p : I → ℝ) :
    ∃ (q : G → ℝ) (y : I → ℝ) (z : ℝ), Bell.Probability q ∧
      (∀ i, |y i| ≤ w i) ∧ (∀ g, pairing y (A g) + z ≤ 0) ∧
      pairing y p + z = weightedCost w A p q ∧
      (∀ q', Bell.Probability q' → weightedCost w A p q ≤ weightedCost w A p q') ∧
      (∀ y' z', (∀ i, |y' i| ≤ w i) → (∀ g, pairing y' (A g) + z' ≤ 0) →
        pairing y' p + z' ≤ pairing y p + z) := by
  classical
  obtain ⟨q, y, z, hq, hs, hy, hz, he, hopt⟩ := contextuality_strong_duality
    (fun g i => w i * A g i) (fun i => w i * p i)
  simp_rw [scaled_pairing] at hz he
  rw [scaled_cost w hw] at he
  have hwb : ∀ i, |w i * y i| ≤ w i := by
    intro i
    rw [abs_mul, abs_of_nonneg (hw i)]
    simpa using mul_le_mul_of_nonneg_left (hy i) (hw i)
  refine ⟨q, fun i => w i * y i, z, ⟨hq, hs⟩, hwb, hz, he, ?_, ?_⟩
  · intro q' hq'
    rw [← he]
    exact weighted_weak_duality w A p _ q' z hq' hwb hz
  · intro y' z' hy' hz'
    rw [he]
    exact weighted_weak_duality w A p y' q z' ⟨hq, hs⟩ hy' hz'

variable {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
abbrev Coordinate (X Y A B : Type) := (X × Y) × (A × B)

def flatten (p : Bell.Behavior X Y A B) : Coordinate X Y A B → ℝ :=
  fun i => p i.1.1 i.1.2 i.2.1 i.2.2

def vertex (ω : Bell.Assignment X Y A B) : Coordinate X Y A B → ℝ := by
  classical
  exact fun i => if ω.1 i.1.1 = i.2.1 ∧ ω.2 i.1.2 = i.2.2 then 1 else 0

theorem marginal_eq_mix (q : Bell.Assignment X Y A B → ℝ) :
    flatten (Bell.marginal q) = mix vertex q := by
  classical
  funext i
  simp [flatten, Bell.marginal, mix, vertex, mul_ite]

theorem weighted_cost_eq_tv (π : X × Y → ℝ) (p : Bell.Behavior X Y A B)
    (q : Bell.Assignment X Y A B → ℝ) :
    weightedCost (fun i : Coordinate X Y A B => π i.1 / 2) vertex (flatten p) q =
      weightedTV π p (Bell.marginal q) := by
  unfold weightedCost
  rw [← marginal_eq_mix]
  simp only [ weightedTV, flatten, Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro x _
  apply Finset.sum_congr rfl
  intro y _
  simp only [← Finset.mul_sum]
  ring

/-- The Bell repair LP has both optimizers, in the paper's actual coordinates and TV convention. -/
theorem bell_strong_duality [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p : Bell.Behavior X Y A B) :
    ∃ (q : Bell.Assignment X Y A B → ℝ) (c : Coordinate X Y A B → ℝ) (z : ℝ),
      Bell.Probability q ∧ (∀ i, |c i| ≤ π i.1 / 2) ∧
      (∀ ω, pairing c (vertex ω) + z ≤ 0) ∧
      pairing c (flatten p) + z = behaviorRepair π p ∧
      weightedTV π p (Bell.marginal q) = behaviorRepair π p ∧
      (∀ c' z', (∀ i, |c' i| ≤ π i.1 / 2) →
        (∀ ω, pairing c' (vertex ω) + z' ≤ 0) →
        pairing c' (flatten p) + z' ≤ behaviorRepair π p) := by
  obtain ⟨q, c, z, hq, hc, hz, he, hopt, hd⟩ := weighted_strong_duality
    (fun i : Coordinate X Y A B => π i.1 / 2)
    (fun i => div_nonneg (hπ.nonneg i.1) (by norm_num)) vertex (flatten p)
  simp_rw [weighted_cost_eq_tv] at he hopt
  have hlocal : Bell.PositiveExtension (Bell.marginal q) := ⟨q, hq, rfl⟩
  have hr : behaviorRepair π p = weightedTV π p (Bell.marginal q) := by
    apply le_antisymm (behaviorRepair_le π hπ p _ hlocal)
    unfold behaviorRepair
    refine le_csInf ?_ ?_
    · exact ⟨weightedTV π p (Bell.marginal q), Bell.marginal q, hlocal, rfl⟩
    · rintro r ⟨l, ⟨q', hq', rfl⟩, rfl⟩
      exact hopt q' hq'
  refine ⟨q, c, z, hq, hc, hz, he.trans hr.symm, hr.symm, ?_⟩
  intro c' z' hc' hz'
  rw [← he.trans hr.symm]
  exact hd c' z' hc' hz'

def vertexSupport (c : Coordinate X Y A B → ℝ) [Nonempty A] [Nonempty B] : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty (fun ω => pairing c (vertex ω))

theorem vertex_le_support [Nonempty A] [Nonempty B]
    (c : Coordinate X Y A B → ℝ) (ω : Bell.Assignment X Y A B) :
    pairing c (vertex ω) ≤ vertexSupport c := by
  unfold vertexSupport
  exact Finset.le_sup' (fun ω => pairing c (vertex ω)) (Finset.mem_univ ω)

/-- Equation (6), including attainment, with the maximum over deterministic vertices. -/
theorem bell_support_duality [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p : Bell.Behavior X Y A B) :
    ∃ c : Coordinate X Y A B → ℝ, (∀ i, |c i| ≤ π i.1 / 2) ∧
      pairing c (flatten p) - vertexSupport c = behaviorRepair π p ∧
      (∀ c', (∀ i, |c' i| ≤ π i.1 / 2) →
        pairing c' (flatten p) - vertexSupport c' ≤ behaviorRepair π p) := by
  obtain ⟨q,c,z,hq,hc,hz,he,hmin,hmax⟩ := bell_strong_duality π hπ p
  have hcol (c' : Coordinate X Y A B → ℝ) (ω : Bell.Assignment X Y A B) :
      pairing c' (vertex ω) + -vertexSupport c' ≤ 0 := by
    have hh := vertex_le_support c' ω
    linarith
  have hall : ∀ c', (∀ i, |c' i| ≤ π i.1 / 2) →
      pairing c' (flatten p) - vertexSupport c' ≤ behaviorRepair π p := by
    intro c' hc'
    exact hmax c' (-vertexSupport c') hc' (hcol c')
  refine ⟨c,hc,?_,hall⟩
  have hs : vertexSupport c ≤ -z := by
    apply Finset.sup'_le
    intro ω _
    have hh := hz ω
    linarith
  exact le_antisymm (hall c hc) (by linarith)

/-- A positive dual norm bound yields the normalized Bell witness lower bound (5). -/
theorem bell_witness_bound [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p : Bell.Behavior X Y A B)
    (c : Coordinate X Y A B → ℝ) (β L : ℝ) (hL : 0 < L)
    (hc : ∀ i, |c i| ≤ L * (π i.1 / 2))
    (hβ : ∀ ω, pairing c (vertex ω) ≤ β) :
    max 0 (pairing c (flatten p) - β) / L ≤ behaviorRepair π p := by
  obtain ⟨q,_,_,hq,_,_,_,hmin,hmax⟩ := bell_strong_duality π hπ p
  have hpair (v : Coordinate X Y A B → ℝ) :
      pairing (fun i => c i / L) v = pairing c v / L := by
    simp only [pairing, div_mul_eq_mul_div, Finset.sum_div]
  have hc' : ∀ i, |c i / L| ≤ π i.1 / 2 := by
    intro i
    rw [abs_div, abs_of_pos hL]
    exact (div_le_iff₀ hL).mpr (by simpa only [mul_comm] using hc i)
  have hcol : ∀ ω, pairing (fun i => c i / L) (vertex ω) + -β/L ≤ 0 := by
    intro ω
    rw [hpair]
    rw [← add_div]
    exact div_nonpos_of_nonpos_of_nonneg (by linarith [hβ ω]) hL.le
  have hb := hmax (fun i => c i / L) (-β/L) hc' hcol
  rw [hpair] at hb
  have hn : 0 ≤ behaviorRepair π p := by
    rw [← hmin]
    exact weightedTV_nonneg π hπ p _
  by_cases hgap : 0 ≤ pairing c (flatten p) - β
  · rw [max_eq_right hgap]
    calc
      _ = pairing c (flatten p) / L + -β / L := by ring
      _ ≤ _ := hb
  · rw [max_eq_left (le_of_not_ge hgap), zero_div]
    exact hn

theorem weighted_slack_bound (w : I → ℝ) (hw : ∀ i, 0 ≤ w i)
    (A : G → I → ℝ) (p : I → ℝ) (q : G → ℝ) (u : I → ℝ)
    (hu : ∀ i, -u i ≤ p i - mix A q i ∧ p i - mix A q i ≤ u i) :
    weightedCost w A p q ≤ ∑ i, w i * u i := by
  apply Finset.sum_le_sum
  intro i _
  exact mul_le_mul_of_nonneg_left (abs_le.mpr (hu i)) (hw i)

/-- The minimizer also solves the explicit slack-variable linear program (29). -/
theorem bell_slack_primal [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p : Bell.Behavior X Y A B) :
    ∃ (q : Bell.Assignment X Y A B → ℝ) (u : Coordinate X Y A B → ℝ),
      Bell.Probability q ∧ (∀ i, 0 ≤ u i) ∧
      (∀ i, -u i ≤ flatten p i - mix vertex q i ∧ flatten p i - mix vertex q i ≤ u i) ∧
      (∑ i, (π i.1 / 2) * u i) = behaviorRepair π p ∧
      (∀ (q' : Bell.Assignment X Y A B → ℝ) (u' : Coordinate X Y A B → ℝ), Bell.Probability q' →
        (∀ i, -u' i ≤ flatten p i - mix vertex q' i ∧ flatten p i - mix vertex q' i ≤ u' i) →
        behaviorRepair π p ≤ ∑ i, (π i.1 / 2) * u' i) := by
  obtain ⟨q,c,z,hq,hc,hz,he,hmin,hd⟩ := bell_strong_duality π hπ p
  refine ⟨q, fun i => |flatten p i - mix vertex q i|, hq, fun i => abs_nonneg _,
    fun i => ⟨neg_abs_le _,le_abs_self _⟩, ?_, ?_⟩
  · exact (weighted_cost_eq_tv π p q).trans hmin
  · intro q' u' hq' hu'
    have hl := weighted_weak_duality (fun i : Coordinate X Y A B => π i.1 / 2)
      vertex (flatten p) c q' z hq' hc hz
    rw [he] at hl
    exact hl.trans (weighted_slack_bound _ (fun i => div_nonneg (hπ.nonneg _) (by norm_num))
      vertex (flatten p) q' u' hu')

end Bell.Repair
