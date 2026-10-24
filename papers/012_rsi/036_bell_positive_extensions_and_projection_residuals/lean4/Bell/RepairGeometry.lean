import Bell.Repair
import Bell.TangentCone
import Bell.PolyhedralProjection

noncomputable section
open scoped BigOperators Topology
open Set Metric Filter
namespace Bell.RepairGeometry
attribute [local instance] Classical.propDecidable
open Bell.LinearProgramming Bell.Repair Bell.Separable Bell.Polyhedral Bell.PolyhedralProjection
variable {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
abbrev V (X Y A B : Type) := Vec (Coordinate X Y A B)

def embed (π : X × Y → ℝ) : Bell.Behavior X Y A B →ₗ[ℝ] V X Y A B := by
  let L : Bell.Behavior X Y A B →ₗ[ℝ] (Coordinate X Y A B → ℝ) :=
    { toFun := fun p i => π i.1 / 2 * flatten p i
      map_add' := by intros; funext i; simp [flatten, mul_add]
      map_smul' := by
        intro t p
        funext i
        change π i.1 / 2 * (t * p i.1.1 i.1.2 i.2.1 i.2.2) =
          t * (π i.1 / 2 * p i.1.1 i.1.2 i.2.1 i.2.2)
        ring }
  exact (WithLp.linearEquiv 1 ℝ (Coordinate X Y A B → ℝ)).symm.toLinearMap.comp L

omit [Fintype X] [Fintype Y] [Fintype A] [Fintype B] in
theorem embed_apply (π : X × Y → ℝ) (p : Bell.Behavior X Y A B) (i : Coordinate X Y A B) :
    embed π p i = π i.1 / 2 * flatten p i := rfl

def localSet (π : X × Y → ℝ) : Set (V X Y A B) :=
  mixtureMap (fun ω i => π i.1 / 2 * vertex ω i) '' simplex (Bell.Assignment X Y A B)

theorem mixture_embed (π : X × Y → ℝ) (q : Bell.Assignment X Y A B → ℝ) :
    mixtureMap (fun ω i => π i.1 / 2 * vertex ω i) q = embed π (Bell.marginal q) := by
  ext i
  rw [mixtureMap_apply, scaled_mix, embed_apply, marginal_eq_mix]

theorem localSet_eq (π : X × Y → ℝ) :
    localSet (A := A) (B := B) π = embed π '' {p | Bell.PositiveExtension p} := by
  ext z
  constructor
  · rintro ⟨q,hq,rfl⟩
    exact ⟨Bell.marginal q, ⟨q, ⟨hq.1,hq.2⟩,rfl⟩, (mixture_embed π q).symm⟩
  · rintro ⟨p,⟨q,hq,rfl⟩,rfl⟩
    exact ⟨q,⟨hq.nonneg,hq.total⟩,mixture_embed π q⟩

theorem dist_embed (π : X × Y → ℝ) (hπ : Bell.Probability π)
    (p q : Bell.Behavior X Y A B) : dist (embed π p) (embed π q) = weightedTV π p q := by
  simp only [dist_eq_norm, PiLp.norm_eq_of_L1, PiLp.sub_apply, embed_apply, Real.norm_eq_abs,
    ← mul_sub, abs_mul]
  have habs (i : Coordinate X Y A B) : |π i.1 / 2| = π i.1 / 2 :=
    abs_of_nonneg (div_nonneg (hπ.nonneg i.1) (by norm_num))
  simp_rw [habs]
  simp only [weightedTV, flatten, Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro x _
  apply Finset.sum_congr rfl
  intro y _
  simp only [← Finset.mul_sum]
  ring

theorem repair_eq_distance [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p : Bell.Behavior X Y A B) :
    behaviorRepair π p = infDist (embed π p) (localSet π) := by
  obtain ⟨q,c,z,hq,hc,hz,he,hmin,hd⟩ := bell_strong_duality π hπ p
  have hlocal : embed π (Bell.marginal q) ∈ localSet π := by
    rw [localSet_eq]; exact ⟨_,⟨q,hq,rfl⟩,rfl⟩
  apply le_antisymm
  · apply (le_infDist ⟨_,hlocal⟩).2
    intro y hy
    rw [localSet_eq] at hy
    obtain ⟨l,hl,rfl⟩ := hy
    rw [dist_embed π hπ]
    exact behaviorRepair_le π hπ p l hl
  · calc
      _ ≤ dist (embed π p) (embed π (Bell.marginal q)) := infDist_le_dist_of_mem hlocal
      _ = _ := (dist_embed π hπ p _).trans hmin

/-- An actual finite inequality presentation of the weighted Bell local polytope. -/
theorem local_polyhedral (π : X × Y → ℝ) :
    IsPolyhedron (localSet (A := A) (B := B) π) := by
  let e := WithLp.linearEquiv 1 ℝ (Coordinate X Y A B → ℝ)
  let T := mixtureMap (fun ω i => π i.1 / 2 * vertex (X := X) (Y := Y) (A := A) (B := B) ω i)
  have hh := preimage (linear_image (simplex_polyhedral (Bell.Assignment X Y A B))
    (e.toLinearMap.comp T.toLinearMap)) e.toLinearMap
  convert hh using 1
  ext x
  constructor
  · rintro ⟨q,hq,rfl⟩; exact ⟨q,hq,rfl⟩
  · rintro ⟨q,hq,he⟩
    exact ⟨q,hq,e.injective he⟩

structure Presentation (π : X × Y → ℝ) where
  count : ℕ
  normal : Fin count → V X Y A B →L[ℝ] ℝ
  bound : Fin count → ℝ
  represents : localSet π = Bell.TangentCone.feasible normal bound

theorem presentation_exists (π : X × Y → ℝ) :
    Nonempty (Presentation (A := A) (B := B) π) := by
  obtain ⟨n,a,b,he⟩ := local_polyhedral (A := A) (B := B) π
  exact ⟨⟨n, fun i => (a i).toContinuousLinearMap, b, he⟩⟩

def presentation (π : X × Y → ℝ) : Presentation (A := A) (B := B) π :=
  Classical.choice (presentation_exists π)

def localTangent (π : X × Y → ℝ) (p : Bell.Behavior X Y A B) : Set (V X Y A B) :=
  Bell.TangentCone.tangent (presentation π).normal (presentation π).bound (embed π p)

theorem bell_ray_distance [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p v : Bell.Behavior X Y A B)
    (hp : Bell.PositiveExtension p) :
    ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t →
      behaviorRepair π (p+t•v) = t * infDist (embed π v) (localTangent π p) := by
  have hp' : embed π p ∈ Bell.TangentCone.feasible (presentation π).normal (presentation π).bound := by
    rw [← (presentation π).represents, localSet_eq]; exact ⟨p,hp,rfl⟩
  have hr := Bell.TangentCone.ray_distance (presentation π).normal (presentation π).bound
    (embed π p) (embed π v) hp'
  filter_upwards [hr] with t ht hnon
  rw [repair_eq_distance π hπ, map_add, map_smul, (presentation π).represents]
  exact ht hnon

/-- Proposition 4 with an explicit quadratic remainder and the same constant. -/
theorem bell_quadratic_remainder [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p v : Bell.Behavior X Y A B)
    (hp : Bell.PositiveExtension p) (path : ℝ → Bell.Behavior X Y A B) (C : ℝ)
    (hrem : ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t → weightedTV π (path t) (p+t•v) ≤ C*t^2) :
    ∀ᶠ t : ℝ in 𝓝 0, 0 ≤ t →
      |behaviorRepair π (path t) - t * infDist (embed π v) (localTangent π p)| ≤ C*t^2 := by
  filter_upwards [bell_ray_distance π hπ p v hp, hrem] with t ht hr hnon
  rw [← ht hnon, repair_eq_distance π hπ, repair_eq_distance π hπ]
  have hd := (lipschitz_infDist_pt (localSet π)).dist_le_mul (embed π (path t)) (embed π (p+t•v))
  have hd' : |infDist (embed π (path t)) (localSet π) - infDist (embed π (p+t•v)) (localSet π)| ≤
      weightedTV π (path t) (p+t•v) := by
    simpa only [Real.dist_eq, NNReal.coe_one, one_mul, dist_embed π hπ] using hd
  exact hd'.trans (hr hnon)

omit [Fintype X] [Fintype Y] [Fintype A] [Fintype B] in
theorem embed_injective (π : X × Y → ℝ) (hπ : ∀ k, 0 < π k) :
    Function.Injective (embed (A := A) (B := B) π) := by
  intro p q he
  funext x y a b
  have hh := congrArg (fun z : V X Y A B => z ((x,y),(a,b))) he
  simp only [embed_apply, flatten] at hh
  exact mul_left_cancel₀ (ne_of_gt (div_pos (hπ (x,y)) (by norm_num))) hh

theorem local_compact (π : X × Y → ℝ) : IsCompact (localSet (A := A) (B := B) π) :=
  (simplex_compact _).image (mixtureMap _).continuous

theorem local_nonempty [Nonempty A] [Nonempty B] (π : X × Y → ℝ) :
    (localSet (A := A) (B := B) π).Nonempty := by
  classical
  exact ⟨_, Pi.single (Classical.arbitrary (Bell.Assignment X Y A B)) 1,
    simplex_single _, rfl⟩

theorem repair_zero_iff [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (hpos : ∀ k, 0 < π k)
    (p : Bell.Behavior X Y A B) : behaviorRepair π p = 0 ↔ Bell.PositiveExtension p := by
  rw [repair_eq_distance π hπ, ← (local_compact π).isClosed.mem_iff_infDist_zero (local_nonempty π),
    localSet_eq]
  constructor
  · rintro ⟨q,hq,he⟩
    exact (embed_injective π hpos he) ▸ hq
  · intro hp; exact ⟨p,hp,rfl⟩

theorem repair_lipschitz [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p q : Bell.Behavior X Y A B) :
    |behaviorRepair π p - behaviorRepair π q| ≤ weightedTV π p q := by
  rw [repair_eq_distance π hπ, repair_eq_distance π hπ]
  simpa only [Real.dist_eq, NNReal.coe_one, one_mul, dist_embed π hπ] using
    (lipschitz_infDist_pt (localSet π)).dist_le_mul (embed π p) (embed π q)

/-- The constructed constraint description yields the intrinsic closed radial cone. -/
theorem localTangent_intrinsic (π : X × Y → ℝ) (p : Bell.Behavior X Y A B)
    (hp : Bell.PositiveExtension p) :
    localTangent π p = closure {u | ∃ t : ℝ, 0 < t ∧ embed π p + t • u ∈ localSet π} := by
  have hp' : embed π p ∈ Bell.TangentCone.feasible (presentation π).normal (presentation π).bound := by
    rw [← (presentation π).represents, localSet_eq]; exact ⟨p,hp,rfl⟩
  simpa only [localTangent, ← (presentation π).represents] using
    Bell.TangentCone.tangent_eq_closed_radial (presentation π).normal (presentation π).bound (embed π p) hp'

theorem bell_explicit_ray_window [Nonempty A] [Nonempty B]
    (π : X × Y → ℝ) (hπ : Bell.Probability π) (p v : Bell.Behavior X Y A B)
    (hp : Bell.PositiveExtension p) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ t, 0 ≤ t → t ≤ δ →
      behaviorRepair π (p+t•v) = t * infDist (embed π v) (localTangent π p) :=
  Bell.TangentCone.positive_window (bell_ray_distance π hπ p v hp)

end Bell.RepairGeometry
