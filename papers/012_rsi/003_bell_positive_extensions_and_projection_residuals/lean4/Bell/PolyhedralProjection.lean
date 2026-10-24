import Bell.Polyhedral
import Bell.LinearProgramming

noncomputable section
open Set
namespace Bell.PolyhedralProjection
open Bell.Polyhedral
variable {E : Type} [AddCommGroup E] [Module ℝ E]

theorem intersection {S T : Set E} (hS : IsPolyhedron S) (hT : IsPolyhedron T) :
    IsPolyhedron (S ∩ T) := by
  obtain ⟨n,a,b,rfl⟩ := hS
  obtain ⟨m,c,d,rfl⟩ := hT
  convert of_finite_system (Sum.elim a c) (Sum.elim b d) using 1
  ext x; simp

theorem equalities {I : Type} [Fintype I] (a : I → E →ₗ[ℝ] ℝ) :
    IsPolyhedron {x | ∀ i, a i x = 0} := by
  convert of_finite_system (fun k : I × Bool => if k.2 then a k.1 else -a k.1)
    (fun _ => (0 : ℝ)) using 1
  ext x
  simp only [mem_ofPred_eq, Prod.forall, Bool.forall_bool, Bool.false_eq_true,
    ite_false, ite_true, LinearMap.neg_apply, neg_nonpos]
  constructor
  · intro hx i; simp [hx i]
  · intro hx i; exact le_antisymm (hx i).2 (hx i).1

theorem projection_fin (n : ℕ) {S : Set (E × (Fin n → ℝ))} (hS : IsPolyhedron S) :
    IsPolyhedron {x | ∃ q : Fin n → ℝ, (x,q) ∈ S} := by
  induction n with
  | zero =>
      let L : E →ₗ[ℝ] E × (Fin 0 → ℝ) :=
        (LinearMap.id : E →ₗ[ℝ] E).prod 0
      have he : {x | ∃ q : Fin 0 → ℝ, (x,q) ∈ S} = L ⁻¹' S := by
        ext x
        constructor
        · rintro ⟨q,hq⟩
          have hq0 : q = 0 := Subsingleton.elim _ _
          simpa [L, hq0] using hq
        · intro hx; exact ⟨0,hx⟩
      rw [he]
      exact preimage hS L
  | succ n ih =>
      let L : ((E × (Fin n → ℝ)) × ℝ) →ₗ[ℝ] E × (Fin (n+1) → ℝ) :=
        { toFun := fun z => (z.1.1, Fin.cons z.2 z.1.2)
          map_add' := by
            intro x y
            refine Prod.ext rfl ?_
            funext i
            exact Fin.cases rfl (fun _ => rfl) i
          map_smul' := by
            intro t x
            refine Prod.ext rfl ?_
            funext i
            exact Fin.cases rfl (fun _ => rfl) i }
      have hp := ih (projection_one (preimage hS L))
      convert hp using 1
      ext x
      simp only [mem_ofPred_eq, mem_preimage, L]
      constructor
      · rintro ⟨q,hq⟩
        refine ⟨fun i => q i.succ, q 0, ?_⟩
        change (x, Fin.cons (q 0) (Fin.tail q)) ∈ S
        simpa only [Fin.cons_self_tail] using hq
      · rintro ⟨q,t,hq⟩
        exact ⟨Fin.cons t q,hq⟩

theorem projection_finite {I : Type} [Fintype I] {S : Set (E × (I → ℝ))}
    (hS : IsPolyhedron S) : IsPolyhedron {x | ∃ q : I → ℝ, (x,q) ∈ S} := by
  classical
  let L : (E × (Fin (Fintype.card I) → ℝ)) →ₗ[ℝ] E × (I → ℝ) :=
    { toFun := fun z => (z.1, fun i => z.2 (Fintype.equivFin I i))
      map_add' := by intros; rfl
      map_smul' := by intros; rfl }
  have hp := projection_fin (Fintype.card I) (preimage hS L)
  convert hp using 1
  ext x
  constructor
  · rintro ⟨q,hq⟩
    refine ⟨fun i => q ((Fintype.equivFin I).symm i), ?_⟩
    simpa [L] using hq
  · rintro ⟨q,hq⟩
    exact ⟨fun i => q (Fintype.equivFin I i), hq⟩

/-- Finite linear images preserve polyhedrality; the proof eliminates each source coordinate. -/
theorem linear_image {I J : Type} [Fintype I] [Fintype J]
    {S : Set (I → ℝ)} (hS : IsPolyhedron S) (T : (I → ℝ) →ₗ[ℝ] (J → ℝ)) :
    IsPolyhedron (T '' S) := by
  let a : J → ((J → ℝ) × (I → ℝ)) →ₗ[ℝ] ℝ := fun j =>
    (LinearMap.proj j).comp ((LinearMap.fst ℝ (J → ℝ) (I → ℝ)) -
      T.comp (LinearMap.snd ℝ (J → ℝ) (I → ℝ)))
  have hp := projection_finite (intersection
    (preimage hS (LinearMap.snd ℝ (J → ℝ) (I → ℝ))) (equalities a))
  convert hp using 1
  ext x
  constructor
  · rintro ⟨q,hq,rfl⟩
    exact ⟨q,hq,fun j => by simp [a]⟩
  · rintro ⟨q,hq,he⟩
    refine ⟨q,hq,?_⟩
    funext j
    have hh := he j
    change x j - T q j = 0 at hh
    exact (sub_eq_zero.mp hh).symm

theorem simplex_polyhedral (I : Type) [Fintype I] :
    IsPolyhedron (Bell.LinearProgramming.simplex I) := by
  classical
  let total : (I → ℝ) →ₗ[ℝ] ℝ := ∑ i, LinearMap.proj i
  let a : I ⊕ Bool → (I → ℝ) →ₗ[ℝ] ℝ :=
    Sum.elim (fun i => -LinearMap.proj i) (fun b => if b then total else -total)
  let b : I ⊕ Bool → ℝ := Sum.elim (fun _ => 0) (fun b => if b then 1 else -1)
  convert of_finite_system a b using 1
  ext q
  simp only [Bell.LinearProgramming.simplex, mem_ofPred_eq, Sum.forall, Bool.forall_bool,
    a,b,Sum.elim_inl,Sum.elim_inr,LinearMap.neg_apply,LinearMap.proj_apply,neg_nonpos,
    Bool.false_eq_true,ite_false,ite_true,total,LinearMap.sum_apply]
  constructor
  · rintro ⟨hn,hs⟩; exact ⟨hn, by simp [hs], by simp [hs]⟩
  · rintro ⟨hn,hlo,hhi⟩; exact ⟨hn, by linarith⟩

end Bell.PolyhedralProjection
