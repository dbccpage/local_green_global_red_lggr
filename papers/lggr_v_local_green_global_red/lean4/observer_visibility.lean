/-
  Observer visibility mechanization: observer visibility.

  This module mechanizes the finite observer-visibility layer of PO-000:

  * Proposition 7.4.3 (green propagation / passivity direction): every observed
    local tally is bounded by the raw represented defect norm, so Global Green
    propagates to Local Green.
  * Proposition 7.4.4 (kernel-cover mechanism): the family is All-Green at a
    defect family exactly when every watched edge defect lies in every watcher's
    kernel.
  * Proposition 7.4.5 (three-patch witness): the explicit three-patch family
    with full edge coverage is All-Green while the raw defect norm is 6.
  * Corollary 7.4.6 (unbounded gap): the scaled witnesses defeat every candidate
    recovery modulus.
  * Corollary 7.4.7 (sufficient condition): full coverage plus edgewise
    joint-kernel triviality carries All-Green to raw defect zero.
  * S13 settlement (necessity fails): a coupled two-edge carrier has full
    coverage and a nontrivial joint kernel on every edge, yet All-Green at any
    section-realized defect forces the raw defect norm to zero.  Edgewise
    joint-kernel triviality is therefore sufficient but NOT necessary over
    coupled carriers.
  * S14 witness: on the same coupled carrier the cochain (1, -1) has exact
    quotient obstruction 2 > 0: every gauge repair leaves l1 mass at least 2,
    and the bound is attained.
  * Supplementary cycle development (historically Theorem 7; namespace `CycleBlindSpot`, added 2026-10-05): on an
    identity-translation directed cycle with one-dimensional blind spots
    `K ∙ v i`, a nonzero realizable All-Green defect exists iff the generators
    `v` are linearly dependent; hence more edges than `finrank` forces one.
    The transverse three-cycle in `ℝ²` is mechanized as an instance.
  * Supplementary invertible-translation extension (same namespace, added 2026-10-05): invertible edge
    translations.  With trivial holonomy the criterion becomes linear
    dependence of the generators transported back to `u_0`; if `w ↦ w - H w`
    is surjective for the holonomy `H` (finite dimension: `H` fixes no
    nonzero vector), every cochain is realizable and every choice of nonzero
    one-dimensional blind spots admits a nonzero All-Green defect.
  * Supplementary redundancy corollary (namespace `Redundancy`, added
    2026-10-05): All-Green depends on observers only through edgewise joint
    blind spots; adjoining observers whose kernels contain them (e.g.
    duplicating every check) leaves All-Green unchanged.

  Scope honesty: the abstract layer works over arbitrary seminormed edge fibers
  with contractive observation maps into normed value spaces, exactly matching
  the display hypotheses of §7.4.1-§7.4.2 evaluated on a defect family (the
  sections and restriction maps enter only through the defect family they
  induce; the witnesses below realize their defect families from explicit
  sections of explicit finite diagrams).  Nothing here mechanizes the quantum
  results of §5, supplies an adapter in the sense of §7.2, or mints authority.
  AuthorityEffect: None.
-/
import Mathlib

namespace ObserverVisibility

open scoped BigOperators

variable {E : Type*} [Fintype E]
variable {A : Type*}
variable {F : E → Type*} [∀ e, SeminormedAddCommGroup (F e)]
variable {V : A → E → Type*} [∀ a e, NormedAddCommGroup (V a e)]

/-- A local observer carrier family over the edge fibers `F`: each observer
`a` watches a finite edge set and observes each fiber through a contractive
map into a normed value space (§7.4.1).  The maps are recorded as plain
functions with a contraction bound; linearity is not needed for the abstract
propositions. -/
structure Carrier (A : Type*) (F : E → Type*)
    [∀ e, SeminormedAddCommGroup (F e)] (V : A → E → Type*)
    [∀ a e, NormedAddCommGroup (V a e)] where
  watched : A → Finset E
  obs : ∀ a e, F e → V a e
  contractive : ∀ a e v, ‖obs a e v‖ ≤ ‖v‖

/-- The raw represented defect norm `I(Δ) = ∑_e ‖Δ_e‖` of §2.2, evaluated on
a defect family. -/
def rawNorm (Δ : ∀ e, F e) : ℝ := ∑ e, ‖Δ e‖

/-- The observed local tally `J^a(Δ) = ∑_{e ∈ E^a} ‖q_e^a(Δ_e)‖` of §7.4.2. -/
def tally (C : Carrier A F V) (a : A) (Δ : ∀ e, F e) : ℝ :=
  ∑ e ∈ C.watched a, ‖C.obs a e (Δ e)‖

/-- All-Green at a defect family: every observer's tally vanishes (§7.4.2). -/
def AllGreen (C : Carrier A F V) (Δ : ∀ e, F e) : Prop :=
  ∀ a, tally C a Δ = 0

theorem rawNorm_nonneg (Δ : ∀ e, F e) : 0 ≤ rawNorm Δ :=
  Finset.sum_nonneg fun _ _ => norm_nonneg _

omit [Fintype E] in
theorem tally_nonneg (C : Carrier A F V) (a : A) (Δ : ∀ e, F e) :
    0 ≤ tally C a Δ :=
  Finset.sum_nonneg fun _ _ => norm_nonneg _

/-- Proposition 7.4.3, first inequality chain: each observed tally is bounded
by the raw represented defect norm.  Contractivity termwise, then enlarging
the (nonnegative) sum from the watched set to all edges. -/
theorem tally_le_rawNorm (C : Carrier A F V) (a : A) (Δ : ∀ e, F e) :
    tally C a Δ ≤ rawNorm Δ := by
  calc
    tally C a Δ ≤ ∑ e ∈ C.watched a, ‖Δ e‖ :=
      Finset.sum_le_sum fun e _ => C.contractive a e (Δ e)
    _ ≤ ∑ e, ‖Δ e‖ :=
      Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ _)
        (fun e _ _ => norm_nonneg _)

/-- Proposition 7.4.3, consequence: Global Green propagates to Local Green. -/
theorem localGreen_of_globalGreen (C : Carrier A F V) (Δ : ∀ e, F e)
    (h : rawNorm Δ = 0) (a : A) : tally C a Δ = 0 :=
  le_antisymm (h ▸ tally_le_rawNorm C a Δ) (tally_nonneg C a Δ)

omit [Fintype E] in
/-- Proposition 7.4.4 (kernel-cover mechanism): All-Green holds exactly when
every watched edge defect is annihilated by every one of its watchers.  For
watched edges this is membership in the joint watcher kernel; for unwatched
edges the condition is vacuous, matching `K_e = F(a_e)`. -/
theorem allGreen_iff_kernel (C : Carrier A F V) (Δ : ∀ e, F e) :
    AllGreen C Δ ↔ ∀ e a, e ∈ C.watched a → C.obs a e (Δ e) = 0 := by
  constructor
  · intro h e a hea
    have hterm :=
      (Finset.sum_eq_zero_iff_of_nonneg
        (fun e _ => norm_nonneg (C.obs a e (Δ e)))).1 (h a) e hea
    exact norm_eq_zero.1 hterm
  · intro h a
    exact Finset.sum_eq_zero fun e he => by rw [h e a he, norm_zero]

/-- Corollary 7.4.7 (sufficient condition for local-to-global soundness):
full edge coverage together with edgewise joint-kernel triviality carries
All-Green to raw defect zero.  The joint-triviality hypothesis quantifies
over each edge's watchers exactly as the combined watcher map's injectivity
does in the paper. -/
theorem rawNorm_eq_zero_of_allGreen
    (C : Carrier A F V) (Δ : ∀ e, F e)
    (htrivial : ∀ e (v : F e), (∀ a, e ∈ C.watched a → C.obs a e v = 0) → v = 0)
    (hgreen : AllGreen C Δ) : rawNorm Δ = 0 := by
  have h := (allGreen_iff_kernel C Δ).1 hgreen
  have hz : ∀ e, Δ e = 0 := fun e => htrivial e (Δ e) fun a hea => h e a hea
  unfold rawNorm
  exact Finset.sum_eq_zero fun e _ => by rw [hz e, norm_zero]

omit [Fintype E] in
/-- Joint-kernel triviality silently contains full edge coverage on every edge
whose fiber has a nonzero vector: an unwatched edge makes the kernel premise
vacuous, so triviality would force the whole fiber to zero.  Recorded so the
coverage hypothesis of Corollary 7.4.7 is visibly not lost in the encoding. -/
theorem coverage_of_jointTrivial (C : Carrier A F V)
    (htrivial : ∀ e (v : F e), (∀ a, e ∈ C.watched a → C.obs a e v = 0) → v = 0)
    (e : E) (v : F e) (hv : v ≠ 0) : ∃ a, e ∈ C.watched a := by
  by_contra hnone
  exact hv (htrivial e v fun a hea => absurd ⟨a, hea⟩ hnone)


/-- The joint blind-spot kernel K: defect cochains annihilated on all watched edges. -/
def jointKernel (C : Carrier A F V) : Set (∀ e, F e) :=
  {Δ | ∀ e a, e ∈ C.watched a → C.obs a e (Δ e) = 0}

/-- The Master Soundness Criterion (Theorem 5 generalized iff form):
    for any subspace/subset of cochains S (such as im(D)), All-Green forces
    raw defect zero on S if and only if S has trivial intersection with the
    joint blind-spot kernel K in the sense that every member of S ∩ K is zero
    (i.e. S ∩ K ⊆ {0}; when 0 ∈ S, such as for S = im(D), this is S ∩ K = {0}). -/
theorem master_soundness_iff (C : Carrier A F V) (S : Set (∀ e, F e))
    (hnorm_zero : ∀ Δ ∈ S, rawNorm Δ = 0 ↔ Δ = 0) :
    (∀ Δ ∈ S, AllGreen C Δ → rawNorm Δ = 0) ↔ (∀ Δ ∈ S, Δ ∈ jointKernel C → Δ = 0) := by
  constructor
  · intro hsound Δ hS hK
    have hgreen : AllGreen C Δ := (allGreen_iff_kernel C Δ).2 hK
    have hzero := hsound Δ hS hgreen
    exact (hnorm_zero Δ hS).1 hzero
  · intro htriv Δ hS hgreen
    have hK : Δ ∈ jointKernel C := (allGreen_iff_kernel C Δ).1 hgreen
    have hz : Δ = 0 := htriv Δ hS hK
    rw [hz]
    unfold rawNorm
    exact Finset.sum_eq_zero fun e _ => by simp

end ObserverVisibility

/-
  The three-patch witness of Proposition 7.4.5 and the scaling family of
  Corollary 7.4.6, with fibers `ℝ³` under the `ℓ¹` norm.  Edges are encoded as
  pairs `(i, k) : Fin 3 × Bool`: patch `u_i` has exactly two covering edges,
  from its two overlaps, selected by `k`; the watcher of `(i, k)` is observer
  `i`, matching `W((x_{ij}, u_i)) = {i}` in the paper.  Restrictions are
  identities and the section vanishes on overlaps, so the defect on `(i, k)`
  is `s(u_i)`.
-/
namespace ObserverVisibility.ThreePatch

open scoped BigOperators

/-- The edge fiber: `ℝ³` with the `ℓ¹` norm. -/
abbrev Fib : Type := PiLp 1 fun _ : Fin 3 => ℝ

/-- The observer value space: `ℝ²` with the `ℓ¹` norm. -/
abbrev Val : Type := PiLp 1 fun _ : Fin 2 => ℝ

theorem fib_norm (v : Fib) : ‖v‖ = ∑ j, |v j| := by
  rw [PiLp.norm_eq_sum (p := 1) (by simp)]
  simp [Real.norm_eq_abs]

theorem val_norm (v : Val) : ‖v‖ = ∑ j, |v j| := by
  rw [PiLp.norm_eq_sum (p := 1) (by simp)]
  simp [Real.norm_eq_abs]

/-- Observer `a` deletes coordinate `a` (the fiber projection `π_a` of
Proposition 7.4.5, kernel `ℝ e_a`). -/
def deleteCoord (a : Fin 3) (v : Fib) : Val :=
  WithLp.toLp 1 fun i : Fin 2 => v (a.succAbove i)

theorem deleteCoord_contractive (a : Fin 3) (v : Fib) :
    ‖deleteCoord a v‖ ≤ ‖v‖ := by
  rw [fib_norm, val_norm, Fin.sum_univ_succAbove (fun j => |v j|) a]
  have hsum : ∑ i, |deleteCoord a v i| = ∑ i : Fin 2, |v (a.succAbove i)| := by
    simp [deleteCoord]
  rw [hsum]
  linarith [abs_nonneg (v a)]

/-- The three-patch observer carrier family: observer `a` watches exactly its
own two edges `(a, false)` and `(a, true)`, through `π_a`. -/
def carrier : Carrier (Fin 3) (fun _ : Fin 3 × Bool => Fib)
    (fun _ _ => Val) where
  watched a := {(a, false), (a, true)}
  obs a _ v := deleteCoord a v
  contractive a _ v := deleteCoord_contractive a v

/-- The section of Proposition 7.4.5, scaled by `lam` as in Corollary 7.4.6:
`s(u_i) = lam · e_i` on patches (the overlap values are zero and the
restrictions are identities, so each edge defect is the patch value). -/
def scaledDefect (lam : ℝ) : Fin 3 × Bool → Fib :=
  fun ek => WithLp.toLp 1 (Pi.single ek.1 lam)

/-- Realization cochain identity: the defect family is induced by subtracting zero
overlap values from patch values (`lam · e_i - 0`), witnessing the cochain form
of section defects. (Note: this verifies the edge-indexed cochain difference directly;
it is distinguished from an encoded six-site incidence operator and assignment graph). -/
theorem scaledDefect_is_section_defect (lam : ℝ) :
    scaledDefect lam =
      fun ek : Fin 3 × Bool =>
        WithLp.toLp 1 (Pi.single ek.1 lam) - (0 : Fib) := by
  funext ek
  simp [scaledDefect]

theorem obs_scaledDefect (a : Fin 3) (e : Fin 3 × Bool) (lam : ℝ)
    (hfst : e.1 = a) : carrier.obs a e (scaledDefect lam e) = 0 := by
  show deleteCoord a (WithLp.toLp 1 (Pi.single e.1 lam)) = 0
  rw [hfst]
  ext i
  simp [deleteCoord]

/-- Proposition 7.4.5 / Corollary 7.4.6, All-Green half: every observer
reports Local Green at every scale. -/
theorem allGreen_scaled (lam : ℝ) : AllGreen carrier (scaledDefect lam) := by
  intro a
  apply Finset.sum_eq_zero
  intro e he
  have hfst : e.1 = a := by
    rcases Finset.mem_insert.1 he with h | h
    · rw [h]
    · rw [Finset.mem_singleton.1 h]
  rw [obs_scaledDefect a e lam hfst, norm_zero]

theorem norm_single (i : Fin 3) (lam : ℝ) :
    ‖(WithLp.toLp 1 (Pi.single i lam) : Fib)‖ = |lam| := by
  rw [fib_norm, Fin.sum_univ_succAbove
    (fun j => |(WithLp.toLp 1 (Pi.single i lam) : Fib) j|) i]
  simp

/-- Proposition 7.4.5 / Corollary 7.4.6, Global Red half: the raw represented
defect norm is `6 |lam|`; at `lam = 1` it is `6`. -/
theorem rawNorm_scaled (lam : ℝ) :
    rawNorm (scaledDefect lam) = 6 * |lam| := by
  unfold rawNorm scaledDefect
  rw [Finset.sum_congr rfl fun (e : Fin 3 × Bool) _ => norm_single e.1 lam,
    Finset.sum_const, Finset.card_univ]
  simp only [Fintype.card_prod, Fintype.card_fin, Fintype.card_bool,
    nsmul_eq_mul]
  norm_num

/-- Proposition 7.4.5 (three-patch witness), assembled: full edge coverage,
All-Green, raw defect norm `6`. -/
theorem three_patch_witness :
    (∀ e : Fin 3 × Bool, ∃ a, e ∈ carrier.watched a) ∧
      AllGreen carrier (scaledDefect 1) ∧
      rawNorm (scaledDefect 1) = 6 := by
  refine ⟨fun e => ⟨e.1, ?_⟩, allGreen_scaled 1, by rw [rawNorm_scaled]; norm_num⟩
  rcases e with ⟨i, k⟩
  cases k
  · exact Finset.mem_insert_self _ _
  · exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _)

/-- Corollary 7.4.6 (no recovery modulus): every candidate modulus `f` is
defeated by a section-realized All-Green defect family whose raw norm
exceeds `f 0` — and `0` is exactly the family's best (indeed every)
observer tally at that defect. -/
theorem no_recovery_modulus (f : ℝ → ℝ) :
    ∃ lam : ℝ, AllGreen carrier (scaledDefect lam) ∧
      (∀ a, tally carrier a (scaledDefect lam) = 0) ∧
      f 0 < rawNorm (scaledDefect lam) := by
  refine ⟨(|f 0| + 1) / 6, allGreen_scaled _, allGreen_scaled _, ?_⟩
  rw [rawNorm_scaled, abs_of_pos (by positivity)]
  have h2 : f 0 ≤ |f 0| := le_abs_self _
  have h3 : 6 * ((|f 0| + 1) / 6) = |f 0| + 1 := by ring
  linarith


/-- Vector score function: the tuple of all observers' observed tallies. -/
noncomputable def scoreVector (Δ : Fin 3 × Bool → Fib) : Fin 3 → ℝ :=
  fun a => tally carrier a Δ

/-- Corollary 7.4.6, Score-Vector version: no vector recovery function
    `f : (Fin 3 → ℝ) → ℝ` can upper-bound the raw defect norm from the
    vector of all local observer tallies. -/
theorem vector_no_recovery_modulus (f : (Fin 3 → ℝ) → ℝ) :
    ∃ lam : ℝ, AllGreen carrier (scaledDefect lam) ∧
      f (scoreVector (scaledDefect lam)) < rawNorm (scaledDefect lam) := by
  have hz : scoreVector (scaledDefect ((|f 0| + 1) / 6)) = 0 := by
    ext a
    exact allGreen_scaled ((|f 0| + 1) / 6) a
  refine ⟨(|f 0| + 1) / 6, allGreen_scaled _, ?_⟩
  rw [hz, rawNorm_scaled, abs_of_pos (by positivity)]
  have h2 : f 0 ≤ |f 0| := le_abs_self _
  have h3 : 6 * ((|f 0| + 1) / 6) = |f 0| + 1 := by ring
  linarith

end ObserverVisibility.ThreePatch

/-
  The coupled two-edge carrier: one overlap `x` under two patches `u_0, u_1`,
  both restriction maps the zero map (contractive), fibers `ℝ²` with the `ℓ¹`
  norm.  Both edge defects then equal `-s(x)`, so the realizable defect
  families form the diagonal.  Observer `a ∈ Fin 2` watches edge `a` alone and
  reads the OTHER coordinate, so each edge's joint watcher kernel is a full
  coordinate line — nontrivial.  Yet All-Green at any section-realized defect
  forces both coordinates of `s(x)` to zero, hence raw defect zero.

  This settles obligation S13 in the negative: edgewise joint-kernel
  triviality (Corollary 7.4.7) is sufficient but NOT necessary for
  local-to-global soundness over coupled carriers.
-/
namespace ObserverVisibility.Coupled

open scoped BigOperators

/-- The edge fiber: `ℝ²` with the `ℓ¹` norm. -/
abbrev Fib2 : Type := PiLp 1 fun _ : Fin 2 => ℝ

theorem fib2_norm (v : Fib2) : ‖v‖ = ∑ j, |v j| := by
  rw [PiLp.norm_eq_sum (p := 1) (by simp)]
  simp [Real.norm_eq_abs]

/-- The other coordinate: `0 ↦ 1`, `1 ↦ 0`. -/
def other : Fin 2 → Fin 2 := ![1, 0]

theorem other_ne (a : Fin 2) : other a ≠ a := by fin_cases a <;> decide

theorem coord_abs_le (v : Fib2) (i : Fin 2) : |v i| ≤ ‖v‖ := by
  rw [fib2_norm]
  exact Finset.single_le_sum (f := fun j => |v j|)
    (fun j _ => abs_nonneg _) (Finset.mem_univ i)

/-- Observer `a` watches edge `a` alone and reads the other coordinate; its
kernel on that edge is the coordinate line `ℝ e_a`, which is nontrivial. -/
def carrier : Carrier (Fin 2) (fun _ : Fin 2 => Fib2) (fun _ _ => ℝ) where
  watched a := {a}
  obs a _ v := v (other a)
  contractive a _ v := by
    rw [Real.norm_eq_abs]
    exact coord_abs_le v (other a)

/-- The defect family realized by the section with overlap value `sx` (both
patch values are erased by the zero restrictions): both edges carry `-sx`. -/
def coupledDefect (sx : Fib2) : Fin 2 → Fib2 := fun _ => -sx

/-- Full edge coverage holds: edge `e` is watched by observer `e`. -/
theorem full_coverage : ∀ e : Fin 2, ∃ a, e ∈ carrier.watched a :=
  fun e => ⟨e, Finset.mem_singleton_self e⟩

/-- Each edge's joint watcher kernel is nontrivial: the basis vector `e_a`
is nonzero and is annihilated by edge `a`'s only watcher. -/
theorem joint_kernel_nontrivial (e : Fin 2) :
    ∃ v : Fib2, v ≠ 0 ∧ ∀ a, e ∈ carrier.watched a → carrier.obs a e v = 0 := by
  refine ⟨WithLp.toLp 1 (Pi.single e 1), ?_, ?_⟩
  · intro h
    have h1 : (WithLp.toLp 1 (Pi.single e 1) : Fib2) e = (0 : Fib2) e :=
      congrFun (congrArg WithLp.ofLp h) e
    simp at h1
  · intro a hae
    have ha : e = a := Finset.mem_singleton.1 hae
    subst ha
    show (WithLp.toLp 1 (Pi.single e (1 : ℝ)) : Fib2) (other e) = 0
    simp [Pi.single_eq_of_ne (other_ne e)]

/-- S13 settled in the negative: on the coupled carrier, All-Green at any
section-realized defect family forces the raw defect norm to zero, although
every edge's joint watcher kernel is nontrivial and coverage is full.
Edgewise joint-kernel triviality is sufficient (Corollary 7.4.7) but not
necessary. -/
theorem allGreen_forces_zero (sx : Fib2)
    (hgreen : AllGreen carrier (coupledDefect sx)) :
    rawNorm (coupledDefect sx) = 0 := by
  have h := (allGreen_iff_kernel carrier (coupledDefect sx)).1 hgreen
  have h1 : sx 1 = 0 := by
    have h0 := h 0 0 (Finset.mem_singleton_self 0)
    have hval : (-sx : Fib2) (other 0) = 0 := h0
    have : -(sx 1) = 0 := by simpa [other] using hval
    linarith
  have h0 : sx 0 = 0 := by
    have hx := h 1 1 (Finset.mem_singleton_self 1)
    have hval : (-sx : Fib2) (other 1) = 0 := hx
    have : -(sx 0) = 0 := by simpa [other] using hval
    linarith
  have hnorm : ‖-sx‖ = 0 := by
    rw [norm_neg, fib2_norm, Fin.sum_univ_two, h0, h1]
    simp
  unfold rawNorm coupledDefect
  simp [hnorm]

end ObserverVisibility.Coupled

/-
  The S14 quotient witness, on the scalar coupled diagram: fibers `ℝ`, two
  edges from the shared overlap with zero restrictions, so `im(d_0)` is the
  diagonal `{(-α, -α)}`.  The cochain `ω = (1, -1)` has exact `ℓ¹` quotient
  distance `2` from `im(d_0)`: the triangle inequality gives the lower bound
  on every repair, and `α = 0` attains it.  In particular `ω` is not exact,
  and `Φ([ω]) = 2 > 0` for this declared finite gauge.
-/
namespace ObserverVisibility.QuotientWitness

/-- The coboundary of the scalar coupled diagram: both edges read `-α` where
`α` is the repair's overlap value (the zero restrictions erase the patch
values). -/
def d0 (alpha : ℝ) : Fin 2 → ℝ := fun _ => -alpha

/-- The witness cochain `ω = (1, -1)`. -/
def omega : Fin 2 → ℝ := ![1, -1]

/-- The `ℓ¹` mass of a scalar 2-cochain. -/
def massL1 (w : Fin 2 → ℝ) : ℝ := |w 0| + |w 1|

/-- Every gauge repair leaves `ℓ¹` mass at least `2`. -/
theorem repair_mass_ge_two (alpha : ℝ) :
    2 ≤ massL1 (fun i => omega i - d0 alpha i) := by
  unfold massL1 omega d0
  simp only [Matrix.cons_val_zero, Matrix.cons_val_one]
  have hA : (1 : ℝ) - -alpha = 1 + alpha := by ring
  have hB : (-1 : ℝ) - -alpha = alpha - 1 := by ring
  rw [hA, hB]
  have h1 : (1 : ℝ) + alpha ≤ |1 + alpha| := le_abs_self _
  have h2 : (1 : ℝ) - alpha ≤ |alpha - 1| := by
    rw [abs_sub_comm]
    exact le_abs_self _
  linarith

/-- The bound is attained at the zero repair. -/
theorem repair_mass_attained :
    massL1 (fun i => omega i - d0 0 i) = 2 := by
  unfold massL1 omega d0
  norm_num

/-- `ω` is not exact: no repair reaches it. -/
theorem omega_not_exact (alpha : ℝ) : d0 alpha ≠ omega := by
  intro h
  have h0 := congrFun h 0
  have h1 := congrFun h 1
  unfold d0 omega at h0 h1
  simp at h0 h1
  linarith

end ObserverVisibility.QuotientWitness

/-
  Minkowski norm inequality chain on quotient spaces and finite cochains:
  For any 2-cochain w, the Chebyshev (ℓ^∞), Euclidean (ℓ²), and Taxicab (ℓ¹)
  norms satisfy:
      ‖w‖_∞ ≤ ‖w‖_2 ≤ ‖w‖_1
  Consequently, on any cochain w and coboundary subspace im(d_0), the quotient
  residuals for every repair α satisfy the pointwise chain, and the exact
  infimal quotient distances satisfy:
      dist_∞(ω, im(d_0)) ≤ dist_2(ω, im(d_0)) ≤ dist_1(ω, im(d_0))
  with exact attained values 1 ≤ √2 ≤ 2.
-/
namespace ObserverVisibility.MinkowskiQuotient

/-- The ℓ^∞ (Chebyshev / uniform) norm on a 2-cochain. -/
def normLinf (w : Fin 2 → ℝ) : ℝ := max |w 0| |w 1|

/-- The ℓ² (Euclidean / Hilbert) norm on a 2-cochain. -/
noncomputable def normL2 (w : Fin 2 → ℝ) : ℝ := Real.sqrt ((w 0)^2 + (w 1)^2)

/-- The ℓ¹ (Taxicab / Minkowski-1) norm on a 2-cochain. -/
def normL1 (w : Fin 2 → ℝ) : ℝ := |w 0| + |w 1|

/-- Vector-level inequality: ‖w‖_∞ ≤ ‖w‖_2 on `Fin 2 → ℝ`. -/
theorem normLinf_le_normL2 (w : Fin 2 → ℝ) : normLinf w ≤ normL2 w := by
  unfold normLinf normL2
  apply max_le
  · have h0 : (|w 0|)^2 ≤ (w 0)^2 + (w 1)^2 := by
      have : (|w 0|)^2 = (w 0)^2 := sq_abs (w 0)
      rw [this]
      have : 0 ≤ (w 1)^2 := sq_nonneg (w 1)
      linarith
    have hsqrt := Real.sqrt_le_sqrt h0
    rw [Real.sqrt_sq (abs_nonneg (w 0))] at hsqrt
    exact hsqrt
  · have h1 : (|w 1|)^2 ≤ (w 0)^2 + (w 1)^2 := by
      have : (|w 1|)^2 = (w 1)^2 := sq_abs (w 1)
      rw [this]
      have : 0 ≤ (w 0)^2 := sq_nonneg (w 0)
      linarith
    have hsqrt := Real.sqrt_le_sqrt h1
    rw [Real.sqrt_sq (abs_nonneg (w 1))] at hsqrt
    exact hsqrt

/-- Vector-level inequality: ‖w‖_2 ≤ ‖w‖_1 on `Fin 2 → ℝ`. -/
theorem normL2_le_normL1 (w : Fin 2 → ℝ) : normL2 w ≤ normL1 w := by
  unfold normL2 normL1
  have hnonneg2 : 0 ≤ (w 0)^2 + (w 1)^2 := by positivity
  have hnonneg1 : 0 ≤ |w 0| + |w 1| := by positivity
  rw [← Real.sqrt_sq hnonneg1]
  have hsq1 : (|w 0| + |w 1|)^2 = (|w 0|)^2 + 2 * |w 0| * |w 1| + (|w 1|)^2 := by ring
  rw [sq_abs, sq_abs] at hsq1
  have hcross : 0 ≤ 2 * |w 0| * |w 1| := by positivity
  have hsq_le : (w 0)^2 + (w 1)^2 ≤ (|w 0| + |w 1|)^2 := by
    rw [hsq1]
    linarith
  exact Real.sqrt_le_sqrt hsq_le

/-- Vector-level combined chain: ‖w‖_∞ ≤ ‖w‖_2 ≤ ‖w‖_1. -/
theorem norm_minkowski_chain (w : Fin 2 → ℝ) :
    normLinf w ≤ normL2 w ∧ normL2 w ≤ normL1 w :=
  ⟨normLinf_le_normL2 w, normL2_le_normL1 w⟩

/-- Pointwise quotient residual bound: for every gauge repair α, the quotient residuals
satisfy the Minkowski chain ‖ω - d₀(α)‖_∞ ≤ ‖ω - d₀(α)‖_2 ≤ ‖ω - d₀(α)‖_1. -/
theorem quotient_residual_minkowski_chain (alpha : ℝ) :
    normLinf (fun i => QuotientWitness.omega i - QuotientWitness.d0 alpha i) ≤
      normL2 (fun i => QuotientWitness.omega i - QuotientWitness.d0 alpha i) ∧
    normL2 (fun i => QuotientWitness.omega i - QuotientWitness.d0 alpha i) ≤
      normL1 (fun i => QuotientWitness.omega i - QuotientWitness.d0 alpha i) :=
  norm_minkowski_chain (fun i => QuotientWitness.omega i - QuotientWitness.d0 alpha i)

/-- Residual values at the zero repair α = 0 satisfy ‖ω - d₀(0)‖_∞ = 1 ≤ ‖ω - d₀(0)‖_2 = √2 ≤ ‖ω - d₀(0)‖_1 = 2.
    (Note: This evaluates the residual norms at candidate repair α = 0; the infimal lower bound for L1 is proved separately in repair_mass_ge_two). -/
theorem quotient_attained_minkowski_chain :
    normLinf (fun i => QuotientWitness.omega i - QuotientWitness.d0 0 i) = 1 ∧
    normL2 (fun i => QuotientWitness.omega i - QuotientWitness.d0 0 i) = Real.sqrt 2 ∧
    normL1 (fun i => QuotientWitness.omega i - QuotientWitness.d0 0 i) = 2 ∧
    (1 : ℝ) ≤ Real.sqrt 2 ∧ Real.sqrt 2 ≤ (2 : ℝ) := by
  unfold normLinf normL2 normL1 QuotientWitness.omega QuotientWitness.d0
  simp only [Matrix.cons_val_zero, Matrix.cons_val_one, neg_zero, sub_zero]
  have h1 : max |(1 : ℝ)| |(-1 : ℝ)| = 1 := by norm_num
  have h2 : Real.sqrt ((1 : ℝ)^2 + (-1 : ℝ)^2) = Real.sqrt 2 := by
    have : (1 : ℝ)^2 + (-1 : ℝ)^2 = 2 := by norm_num
    rw [this]
  have h3 : |(1 : ℝ)| + |(-1 : ℝ)| = 2 := by norm_num
  have h4 : (1 : ℝ) ≤ Real.sqrt 2 := by
    rw [← Real.sqrt_sq (by positivity : 0 ≤ (1 : ℝ))]
    exact Real.sqrt_le_sqrt (by norm_num)
  have h5 : Real.sqrt 2 ≤ (2 : ℝ) := by
    rw [← Real.sqrt_sq (by positivity : 0 ≤ (2 : ℝ))]
    exact Real.sqrt_le_sqrt (by norm_num)
  exact ⟨h1, h2, h3, h4, h5⟩

/-- The generalized ℓ^∞ (Chebyshev / uniform) norm on an arbitrary finite coordinate space `ι → ℝ`. -/
def generalNormLinf {ι : Type*} [Fintype ι] [Nonempty ι] (v : ι → ℝ) : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty (fun i => |v i|)

/-- The generalized ℓ² (Euclidean / Hilbert) norm on an arbitrary finite coordinate space `ι → ℝ`. -/
noncomputable def generalNormL2 {ι : Type*} [Fintype ι] (v : ι → ℝ) : ℝ :=
  Real.sqrt (∑ i, (v i)^2)

/-- The generalized ℓ¹ (Taxicab / Minkowski-1) norm on an arbitrary finite coordinate space `ι → ℝ`. -/
def generalNormL1 {ι : Type*} [Fintype ι] (v : ι → ℝ) : ℝ :=
  ∑ i, |v i|

/-- General vector-level inequality: ‖v‖_∞ ≤ ‖v‖_2 on any finite index type `ι`. -/
theorem general_normLinf_le_general_normL2 {ι : Type*} [Fintype ι] [Nonempty ι] (v : ι → ℝ) :
    generalNormLinf v ≤ generalNormL2 v := by
  unfold generalNormLinf generalNormL2
  apply Finset.sup'_le
  intro j _
  have hsq : (|v j|)^2 ≤ ∑ i, (v i)^2 := by
    have : (|v j|)^2 = (v j)^2 := sq_abs (v j)
    rw [this]
    exact Finset.single_le_sum (fun i _ => sq_nonneg (v i)) (Finset.mem_univ j)
  have hsqrt := Real.sqrt_le_sqrt hsq
  rw [Real.sqrt_sq (abs_nonneg (v j))] at hsqrt
  exact hsqrt

/-- General vector-level inequality: ‖v‖_2 ≤ ‖v‖_1 on any finite index type `ι`. -/
theorem general_normL2_le_general_normL1 {ι : Type*} [Fintype ι] (v : ι → ℝ) :
    generalNormL2 v ≤ generalNormL1 v := by
  unfold generalNormL2 generalNormL1
  have hnonneg1 : 0 ≤ ∑ i, |v i| := Finset.sum_nonneg fun i _ => abs_nonneg (v i)
  rw [← Real.sqrt_sq hnonneg1]
  have h_single : ∀ i, (v i)^2 ≤ |v i| * ∑ j, |v j| := by
    intro i
    have heq : (v i)^2 = |v i| * |v i| := by rw [← sq_abs, sq]
    rw [heq]
    have hle : |v i| ≤ ∑ j, |v j| :=
      Finset.single_le_sum (fun j _ => abs_nonneg (v j)) (Finset.mem_univ i)
    exact mul_le_mul_of_nonneg_left hle (abs_nonneg (v i))
  have hsq_le : ∑ i, (v i)^2 ≤ (∑ i, |v i|)^2 := by
    rw [sq]
    calc
      ∑ i, (v i)^2 ≤ ∑ i, (|v i| * ∑ j, |v j|) := Finset.sum_le_sum fun i _ => h_single i
      _ = (∑ i, |v i|) * (∑ j, |v j|) := by rw [← Finset.sum_mul]
  exact Real.sqrt_le_sqrt hsq_le

/-- Cauchy-Schwarz bound: ‖v‖_1 ≤ √(card ι) · ‖v‖_2 on any finite index type `ι`. -/
theorem general_normL1_le_sqrt_card_mul_general_normL2 {ι : Type*} [Fintype ι] (v : ι → ℝ) :
    generalNormL1 v ≤ Real.sqrt (Fintype.card ι : ℝ) * generalNormL2 v := by
  unfold generalNormL1 generalNormL2
  have h_cs : (∑ i, |v i|)^2 ≤ (Fintype.card ι : ℝ) * ∑ i, (v i)^2 := by
    have h1 : (∑ i, |v i|)^2 = (∑ i, (1 : ℝ) * |v i|)^2 := by
      congr 1
      refine Finset.sum_congr rfl fun i _ => by ring
    rw [h1]
    have h_cauchy := Finset.sum_mul_sq_le_sq_mul_sq (Finset.univ : Finset ι) (fun _ => (1 : ℝ)) (fun i => |v i|)
    have h_ones : ∑ i : ι, (1 : ℝ)^2 = (Fintype.card ι : ℝ) := by simp
    have h_abs_sq : ∑ i, (|v i|)^2 = ∑ i, (v i)^2 := by
      refine Finset.sum_congr rfl fun i _ => sq_abs (v i)
    rw [h_ones, h_abs_sq] at h_cauchy
    exact h_cauchy
  have hnonneg1 : 0 ≤ ∑ i, |v i| := Finset.sum_nonneg fun i _ => abs_nonneg (v i)
  have hnonneg_prod : 0 ≤ (Fintype.card ι : ℝ) * ∑ i, (v i)^2 := by positivity
  rw [← Real.sqrt_sq hnonneg1]
  have h_sqrt := Real.sqrt_le_sqrt h_cs
  rw [Real.sqrt_mul (Nat.cast_nonneg _)] at h_sqrt
  exact h_sqrt

/-- Generalized Minkowski norm chain: ‖v‖_∞ ≤ ‖v‖_2 ≤ ‖v‖_1 ≤ √(card ι) · ‖v‖_2 on any `[Fintype ι] [Nonempty ι]`. -/
theorem general_norm_minkowski_chain {ι : Type*} [Fintype ι] [Nonempty ι] (v : ι → ℝ) :
    generalNormLinf v ≤ generalNormL2 v ∧
    generalNormL2 v ≤ generalNormL1 v ∧
    generalNormL1 v ≤ Real.sqrt (Fintype.card ι : ℝ) * generalNormL2 v :=
  ⟨general_normLinf_le_general_normL2 v,
   general_normL2_le_general_normL1 v,
   general_normL1_le_sqrt_card_mul_general_normL2 v⟩

/-- Reverse Chebyshev bound: ‖v‖_1 ≤ (card ι) · ‖v‖_∞ on any finite index type `ι`. -/
theorem general_normL1_le_card_mul_general_normLinf {ι : Type*} [Fintype ι] [Nonempty ι] (v : ι → ℝ) :
    generalNormL1 v ≤ (Fintype.card ι : ℝ) * generalNormLinf v := by
  unfold generalNormL1 generalNormLinf
  have h_le : ∀ i : ι, |v i| ≤ Finset.univ.sup' Finset.univ_nonempty (fun j => |v j|) := by
    intro i
    exact Finset.le_sup' (fun j => |v j|) (Finset.mem_univ i)
  calc
    ∑ i, |v i| ≤ ∑ i : ι, Finset.univ.sup' Finset.univ_nonempty (fun j => |v j|) :=
      Finset.sum_le_sum fun i _ => h_le i
    _ = (Fintype.card ι : ℝ) * Finset.univ.sup' Finset.univ_nonempty (fun j => |v j|) := by
      rw [Finset.sum_const, nsmul_eq_mul, Finset.card_univ]


/-- Invariance of ℓ¹ norm under coordinate permutation. -/
theorem generalNormL1_equiv_comp {ι : Type*} [Fintype ι] (e : ι ≃ ι) (v : ι → ℝ) :
    generalNormL1 (v ∘ e) = generalNormL1 v := by
  unfold generalNormL1
  exact Equiv.sum_comp e (fun i => |v i|)

/-- Invariance of ℓ² norm under coordinate permutation. -/
theorem generalNormL2_equiv_comp {ι : Type*} [Fintype ι] (e : ι ≃ ι) (v : ι → ℝ) :
    generalNormL2 (v ∘ e) = generalNormL2 v := by
  unfold generalNormL2
  congr 1
  exact Equiv.sum_comp e (fun i => (v i)^2)

/-- Invariance of ℓ¹ norm under coordinate sign flips. -/
theorem generalNormL1_sign_flip {ι : Type*} [Fintype ι] (s : ι → ℝ) (hs : ∀ i, |s i| = 1) (v : ι → ℝ) :
    generalNormL1 (fun i => s i * v i) = generalNormL1 v := by
  unfold generalNormL1
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [abs_mul, hs i, one_mul]

/-- Invariance of ℓ² norm under coordinate sign flips. -/
theorem generalNormL2_sign_flip {ι : Type*} [Fintype ι] (s : ι → ℝ) (hs : ∀ i, (s i)^2 = 1) (v : ι → ℝ) :
    generalNormL2 (fun i => s i * v i) = generalNormL2 v := by
  unfold generalNormL2
  congr 1
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [mul_pow, hs i, one_mul]

/-- Invariance of ℓ^∞ norm under coordinate sign flips. -/
theorem generalNormLinf_sign_flip {ι : Type*} [Fintype ι] [Nonempty ι] (s : ι → ℝ) (hs : ∀ i, |s i| = 1) (v : ι → ℝ) :
    generalNormLinf (fun i => s i * v i) = generalNormLinf v := by
  unfold generalNormLinf
  refine Finset.sup'_congr Finset.univ_nonempty rfl fun i _ => ?_
  rw [abs_mul, hs i, one_mul]

/-- Quotient residual ℓ¹ isometry under signed coordinate permutations: ‖U(ω - Dα)‖₁ = ‖ω - Dα‖₁. -/
theorem quotient_residual_l1_isometry {ι : Type*} [Fintype ι]
    (e : ι ≃ ι) (s : ι → ℝ) (hs : ∀ i, |s i| = 1) (r : ι → ℝ) :
    generalNormL1 (fun i => s i * (r (e i))) = generalNormL1 r := by
  have h1 : (fun i => s i * (r (e i))) = (fun i => s i * ((r ∘ e) i)) := rfl
  rw [h1, generalNormL1_sign_flip s hs, generalNormL1_equiv_comp e]

/-- Quotient residual ℓ² isometry under signed coordinate permutations: ‖U(ω - Dα)‖₂ = ‖ω - Dα‖₂. -/
theorem quotient_residual_l2_isometry {ι : Type*} [Fintype ι]
    (e : ι ≃ ι) (s : ι → ℝ) (hs : ∀ i, (s i)^2 = 1) (r : ι → ℝ) :
    generalNormL2 (fun i => s i * (r (e i))) = generalNormL2 r := by
  have h1 : (fun i => s i * (r (e i))) = (fun i => s i * ((r ∘ e) i)) := rfl
  rw [h1, generalNormL2_sign_flip s hs, generalNormL2_equiv_comp e]


/-- Triangle inequality for the generalized ℓ¹ norm: ‖u + v‖₁ ≤ ‖u‖₁ + ‖v‖₁. -/
theorem generalNormL1_triangle {ι : Type*} [Fintype ι] (u v : ι → ℝ) :
    generalNormL1 (u + v) ≤ generalNormL1 u + generalNormL1 v := by
  unfold generalNormL1
  rw [← Finset.sum_add_distrib]
  exact Finset.sum_le_sum fun i _ => abs_add_le (u i) (v i)

/-- Triangle inequality for the generalized ℓ^∞ norm: ‖u + v‖_∞ ≤ ‖u‖_∞ + ‖v‖_∞. -/
theorem generalNormLinf_triangle {ι : Type*} [Fintype ι] [Nonempty ι] (u v : ι → ℝ) :
    generalNormLinf (u + v) ≤ generalNormLinf u + generalNormLinf v := by
  unfold generalNormLinf
  apply Finset.sup'_le
  intro j _
  have h_le : |(u + v) j| ≤ |u j| + |v j| := by
    dsimp
    exact abs_add_le (u j) (v j)
  have hu : |u j| ≤ Finset.univ.sup' Finset.univ_nonempty (fun i => |u i|) :=
    Finset.le_sup' (fun i => |u i|) (Finset.mem_univ j)
  have hv : |v j| ≤ Finset.univ.sup' Finset.univ_nonempty (fun i => |v i|) :=
    Finset.le_sup' (fun i => |v i|) (Finset.mem_univ j)
  exact h_le.trans (add_le_add hu hv)

/-- Quotient gauge residual subadditivity for ℓ¹:
    ‖(ω₁ + ω₂) - (d₁ + d₂)‖₁ ≤ ‖ω₁ - d₁‖₁ + ‖ω₂ - d₂‖₁. -/
theorem quotient_residual_l1_subadditive {ι : Type*} [Fintype ι] (w1 w2 d1 d2 : ι → ℝ) :
    generalNormL1 ((w1 + w2) - (d1 + d2)) ≤ generalNormL1 (w1 - d1) + generalNormL1 (w2 - d2) := by
  have h_eq : (w1 + w2) - (d1 + d2) = (w1 - d1) + (w2 - d2) := by
    ext i
    dsimp
    ring
  rw [h_eq]
  exact generalNormL1_triangle (w1 - d1) (w2 - d2)

/-- Quotient gauge residual subadditivity for ℓ^∞:
    ‖(ω₁ + ω₂) - (d₁ + d₂)‖_∞ ≤ ‖ω₁ - d₁‖_∞ + ‖ω₂ - d₂‖_∞. -/
theorem quotient_residual_linf_subadditive {ι : Type*} [Fintype ι] [Nonempty ι] (w1 w2 d1 d2 : ι → ℝ) :
    generalNormLinf ((w1 + w2) - (d1 + d2)) ≤ generalNormLinf (w1 - d1) + generalNormLinf (w2 - d2) := by
  have h_eq : (w1 + w2) - (d1 + d2) = (w1 - d1) + (w2 - d2) := by
    ext i
    dsimp
    ring
  rw [h_eq]
  exact generalNormLinf_triangle (w1 - d1) (w2 - d2)

end ObserverVisibility.MinkowskiQuotient

#print axioms ObserverVisibility.tally_le_rawNorm
#print axioms ObserverVisibility.localGreen_of_globalGreen
#print axioms ObserverVisibility.allGreen_iff_kernel
#print axioms ObserverVisibility.rawNorm_eq_zero_of_allGreen
#print axioms ObserverVisibility.coverage_of_jointTrivial
#print axioms ObserverVisibility.ThreePatch.three_patch_witness
#print axioms ObserverVisibility.ThreePatch.rawNorm_scaled
#print axioms ObserverVisibility.ThreePatch.no_recovery_modulus
#print axioms ObserverVisibility.Coupled.full_coverage
#print axioms ObserverVisibility.Coupled.joint_kernel_nontrivial
#print axioms ObserverVisibility.Coupled.allGreen_forces_zero
#print axioms ObserverVisibility.QuotientWitness.repair_mass_ge_two
#print axioms ObserverVisibility.QuotientWitness.repair_mass_attained
#print axioms ObserverVisibility.QuotientWitness.omega_not_exact
#print axioms ObserverVisibility.MinkowskiQuotient.normLinf_le_normL2
#print axioms ObserverVisibility.MinkowskiQuotient.normL2_le_normL1
#print axioms ObserverVisibility.MinkowskiQuotient.norm_minkowski_chain
#print axioms ObserverVisibility.MinkowskiQuotient.quotient_residual_minkowski_chain
#print axioms ObserverVisibility.MinkowskiQuotient.quotient_attained_minkowski_chain
#print axioms ObserverVisibility.MinkowskiQuotient.general_normLinf_le_general_normL2
#print axioms ObserverVisibility.MinkowskiQuotient.general_normL2_le_general_normL1
#print axioms ObserverVisibility.MinkowskiQuotient.general_normL1_le_sqrt_card_mul_general_normL2
#print axioms ObserverVisibility.MinkowskiQuotient.general_norm_minkowski_chain
#print axioms ObserverVisibility.MinkowskiQuotient.general_normL1_le_card_mul_general_normLinf
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormL1_equiv_comp
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormL2_equiv_comp
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormL1_sign_flip
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormL2_sign_flip
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormLinf_sign_flip
#print axioms ObserverVisibility.MinkowskiQuotient.quotient_residual_l1_isometry
#print axioms ObserverVisibility.MinkowskiQuotient.quotient_residual_l2_isometry
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormL1_triangle
#print axioms ObserverVisibility.MinkowskiQuotient.generalNormLinf_triangle
#print axioms ObserverVisibility.MinkowskiQuotient.quotient_residual_l1_subadditive
#print axioms ObserverVisibility.MinkowskiQuotient.quotient_residual_linf_subadditive

#print axioms ObserverVisibility.master_soundness_iff
#print axioms ObserverVisibility.ThreePatch.scaledDefect_is_section_defect
#print axioms ObserverVisibility.ThreePatch.vector_no_recovery_modulus

/-
  Non-linear evaluation maps and quotient distance bounds.
-/
namespace ObserverVisibility.NonlinearEvaluation

variable {E V : Type*} [SeminormedAddCommGroup E] [SeminormedAddCommGroup V]

/-- Non-linear contractive evaluation bound:
    if Ψ : E → V is non-linear and contractive (‖Ψ u - Ψ v‖ ≤ ‖u - v‖),
    then for any cochain ω and any repair m, ‖Ψ ω - Ψ m‖ ≤ ‖ω - m‖. -/
theorem nonlinear_obs_contractive_bound (Ψ : E → V)
    (h_contr : ∀ u v : E, ‖Ψ u - Ψ v‖ ≤ ‖u - v‖)
    (omega m : E) :
    ‖Ψ omega - Ψ m‖ ≤ ‖omega - m‖ :=
  h_contr omega m

/-- Non-linear Lipschitz evaluation bound:
    if Ψ : E → V is L-Lipschitz (‖Ψ u - Ψ v‖ ≤ L * ‖u - v‖),
    then for any cochain ω and any repair m, ‖Ψ ω - Ψ m‖ ≤ L * ‖omega - m‖. -/
theorem nonlinear_lipschitz_obs_bound (Ψ : E → V) (L : ℝ)
    (h_lip : ∀ u v : E, ‖Ψ u - Ψ v‖ ≤ L * ‖u - v‖)
    (omega m : E) :
    ‖Ψ omega - Ψ m‖ ≤ L * ‖omega - m‖ :=
  h_lip omega m

/-- Pointwise non-linear lower expansion bound:
    given any map Φ : E → V and real constant c satisfying c * ‖u - v‖ ≤ ‖Φ u - Φ v‖ for all u, v,
    specializes this inequality to the pair (ω, m).
    (Note: This is a pointwise lower bound on the residual pair (ω, m); it does not quantify over a repair set or take an infimum, nor does it require c > 0 as a hypothesis). -/
theorem nonlinear_bilipschitz_quotient_lower_bound (Φ : E → V) (c : ℝ)
    (h_lower : ∀ u v : E, c * ‖u - v‖ ≤ ‖Φ u - Φ v‖)
    (omega m : E) :
    c * ‖omega - m‖ ≤ ‖Φ omega - Φ m‖ :=
  h_lower omega m

/-- Non-linear perturbed repair residual upper bound:
    ‖ω - (m + δ)‖ ≤ ‖ω - m‖ + ‖δ‖. -/
theorem nonlinear_perturbed_residual_upper_bound (omega m delta : E) :
    ‖omega - (m + delta)‖ ≤ ‖omega - m‖ + ‖delta‖ := by
  have h_eq : omega - (m + delta) = (omega - m) - delta := by
    abel
  rw [h_eq]
  exact norm_sub_le (omega - m) delta

/-- Non-linear perturbed repair residual lower bound:
    ‖ω - m‖ ≤ ‖ω - (m + δ)‖ + ‖δ‖. -/
theorem nonlinear_perturbed_residual_lower_bound (omega m delta : E) :
    ‖omega - m‖ ≤ ‖omega - (m + delta)‖ + ‖delta‖ := by
  have h_eq : omega - m = (omega - (m + delta)) + delta := by
    abel
  rw [h_eq]
  exact norm_add_le (omega - (m + delta)) delta

end ObserverVisibility.NonlinearEvaluation

#print axioms ObserverVisibility.NonlinearEvaluation.nonlinear_obs_contractive_bound
#print axioms ObserverVisibility.NonlinearEvaluation.nonlinear_lipschitz_obs_bound
#print axioms ObserverVisibility.NonlinearEvaluation.nonlinear_bilipschitz_quotient_lower_bound
#print axioms ObserverVisibility.NonlinearEvaluation.nonlinear_perturbed_residual_upper_bound
#print axioms ObserverVisibility.NonlinearEvaluation.nonlinear_perturbed_residual_lower_bound

/-
  Supplementary cycle blind-spot dependence (historically Theorem 7), mechanized 2026-10-05.
  Directed cycle on m + 1 sites, identity translations, one-dimensional blind
  spots K ∙ v i with v i ≠ 0.  Telescoping gives im D = {Δ | ∑ Δ = 0}; a nonzero
  realizable defect inside every blind spot exists iff v is linearly dependent.
  Scope: identity translations in this block; invertible translations are
  treated in the extension block below (trivial holonomy, and holonomy with
  `w ↦ w - H w` surjective).  AuthorityEffect: None.
-/
namespace ObserverVisibility.CycleBlindSpot

open scoped BigOperators

section Core

variable {K : Type*} [Field K] {W : Type*} [AddCommGroup W] [Module K W] {m : ℕ}

/-- Defect operator of the identity-translation directed cycle on `m + 1`
sites: edge `i` runs from `u_i` to `u_{i+1}`, so `(D s)_i = s (i + 1) - s i`. -/
def cycleDefect (s : Fin (m + 1) → W) : Fin (m + 1) → W :=
  fun i => s (i + 1) - s i

/-- Telescoping: every realizable cycle cochain sums to zero. -/
theorem cycleDefect_sum (s : Fin (m + 1) → W) : ∑ i, cycleDefect s i = 0 := by
  unfold cycleDefect
  rw [Finset.sum_sub_distrib, sub_eq_zero]
  exact Fintype.sum_equiv (Equiv.addRight (1 : Fin (m + 1))) _ _ (fun _ => rfl)

/-- Extension of a cycle cochain to a natural-number-indexed sequence. -/
def extend (Δ : Fin (m + 1) → W) (j : ℕ) : W :=
  if h : j < m + 1 then Δ ⟨j, h⟩ else 0

theorem extend_coe (Δ : Fin (m + 1) → W) (i : Fin (m + 1)) :
    extend Δ (i : ℕ) = Δ i := by
  unfold extend
  split
  · rfl
  · exact absurd i.isLt ‹_›

/-- Potential (partial-sum) assignment `s(u_k) = ∑_{j < k} Δ_j`. -/
def potential (Δ : Fin (m + 1) → W) (k : Fin (m + 1)) : W :=
  ∑ j ∈ Finset.range (k : ℕ), extend Δ j

/-- Converse of telescoping: a cochain with zero sum is the defect of its
potential. -/
theorem cycleDefect_potential (Δ : Fin (m + 1) → W) (h : ∑ i, Δ i = 0) :
    cycleDefect (potential Δ) = Δ := by
  funext i
  unfold cycleDefect potential
  by_cases hi : i = Fin.last m
  · subst hi
    have hsum : ∑ j ∈ Finset.range m, extend Δ j + Δ (Fin.last m) = 0 := by
      have hlast : extend Δ m = Δ (Fin.last m) := extend_coe Δ (Fin.last m)
      rw [← hlast, ← Finset.sum_range_succ, ← h, ← Fin.sum_univ_eq_sum_range]
      exact Finset.sum_congr rfl fun i _ => extend_coe Δ i
    rw [Fin.last_add_one, Fin.val_zero, Finset.sum_range_zero, Fin.val_last,
      eq_neg_of_add_eq_zero_left hsum, zero_sub, neg_neg]
  · have hlt : i < Fin.last m := lt_of_le_of_ne (Fin.le_last i) hi
    rw [Fin.val_add_one_of_lt hlt, Finset.sum_range_succ, extend_coe,
      add_sub_cancel_left]

/-- Realizability on the identity-translation cycle: `Δ ∈ im D ↔ ∑ Δ = 0`. -/
theorem realizable_iff_sum_eq_zero (Δ : Fin (m + 1) → W) :
    (∃ s, cycleDefect s = Δ) ↔ ∑ i, Δ i = 0 := by
  constructor
  · rintro ⟨s, rfl⟩
    exact cycleDefect_sum s
  · intro h
    exact ⟨potential Δ, cycleDefect_potential Δ h⟩

/-- **Theorem 7 (cycle blind-spot dependence).**  With identity translations
and one-dimensional blind spots `K ∙ v i` (`v i ≠ 0`), a nonzero realizable
defect lying in every blind spot exists iff the generators are linearly
dependent. -/
theorem cycle_blind_spot_dependence (v : Fin (m + 1) → W) (hv : ∀ i, v i ≠ 0) :
    (∃ s : Fin (m + 1) → W, cycleDefect s ≠ 0 ∧ ∀ i, cycleDefect s i ∈ K ∙ v i) ↔
      ¬ LinearIndependent K v := by
  rw [Fintype.not_linearIndependent_iff]
  constructor
  · rintro ⟨s, hne, hmem⟩
    choose c hc using fun i => Submodule.mem_span_singleton.1 (hmem i)
    refine ⟨c, ?_, ?_⟩
    · rw [← cycleDefect_sum s]
      exact Finset.sum_congr rfl fun i _ => hc i
    · by_contra hall
      have hzero : ∀ i, c i = 0 := fun i => not_not.mp (not_exists.mp hall i)
      apply hne
      funext i
      simp only [Pi.zero_apply]
      rw [← hc i, hzero i, zero_smul]
  · rintro ⟨c, hsum, i₀, hi₀⟩
    obtain ⟨s, hs⟩ := (realizable_iff_sum_eq_zero (fun i => c i • v i)).2 hsum
    refine ⟨s, ?_, ?_⟩
    · intro h0
      have h1 : c i₀ • v i₀ = 0 := by
        have := congrFun hs i₀
        rw [h0] at this
        exact this.symm
      exact smul_ne_zero hi₀ (hv i₀) h1
    · intro i
      rw [hs]
      exact Submodule.mem_span_singleton.2 ⟨c i, rfl⟩

/-- Consequence 1: a cycle with more edges than `finrank K W` admits a nonzero
realizable defect inside every one-dimensional blind spot, for every choice of
nonzero generators. -/
theorem cycle_unsound_of_finrank_lt [FiniteDimensional K W]
    (v : Fin (m + 1) → W) (hv : ∀ i, v i ≠ 0)
    (hdim : Module.finrank K W < m + 1) :
    ∃ s : Fin (m + 1) → W, cycleDefect s ≠ 0 ∧ ∀ i, cycleDefect s i ∈ K ∙ v i := by
  refine (cycle_blind_spot_dependence v hv).2 ?_
  intro hli
  have hcard := hli.fintype_card_le_finrank
  rw [Fintype.card_fin] at hcard
  omega

end Core

section Bridge

variable {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W] {m : ℕ}
variable {A : Type*} {V : A → Fin (m + 1) → Type*} [∀ a e, NormedAddCommGroup (V a e)]

/-- Theorem 7 through the observer layer: if the joint watcher kernel on each
cycle edge is exactly `ℝ ∙ v i`, then some nonzero realizable defect is
All-Green iff the generators are linearly dependent. -/
theorem cycle_allGreen_iff_dependent
    (C : Carrier A (fun _ : Fin (m + 1) => W) V) (v : Fin (m + 1) → W)
    (hv : ∀ i, v i ≠ 0)
    (hK : ∀ i (w : W), (∀ a, i ∈ C.watched a → C.obs a i w = 0) ↔ w ∈ ℝ ∙ v i) :
    (∃ s : Fin (m + 1) → W, cycleDefect s ≠ 0 ∧ AllGreen C (cycleDefect s)) ↔
      ¬ LinearIndependent ℝ v := by
  rw [← cycle_blind_spot_dependence v hv]
  refine exists_congr fun s => and_congr Iff.rfl ?_
  rw [allGreen_iff_kernel]
  constructor
  · intro h i
    exact (hK i _).1 fun a ha => h i a ha
  · intro h i a ha
    exact (hK i _).2 (h i) a ha

end Bridge

/- The transverse three-cycle instance of Theorem 7 in `ℝ²`. -/
namespace C3

/-- Blind-spot generators `v₀ = (1, 0)`, `v₁ = (0, 1)`, `v₂ = (-1, -1)`. -/
def gen : Fin 3 → (Fin 2 → ℝ) := ![![1, 0], ![0, 1], ![-1, -1]]

theorem gen_ne_zero (i : Fin 3) : gen i ≠ 0 := by
  intro h
  fin_cases i
  · have := congrFun h 0
    simp [gen] at this
  · have := congrFun h 1
    simp [gen] at this
  · have := congrFun h 0
    simp [gen] at this

theorem gen_sum : ∑ i, gen i = 0 := by
  funext j
  fin_cases j <;> simp [gen, Fin.sum_univ_three]

/-- Pairwise transversality: any two distinct generators are linearly
independent, i.e. any two blind spots meet only in `0`. -/
theorem gen_pairwise_independent (i j : Fin 3) (hij : i ≠ j) :
    LinearIndependent ℝ ![gen i, gen j] := by
  rw [LinearIndependent.pair_iff]
  intro a b hab
  have h0 := congrFun hab 0
  have h1 := congrFun hab 1
  fin_cases i <;> fin_cases j <;> simp [gen] at h0 h1 hij ⊢ <;>
    constructor <;> linarith

/-- The three generators are dependent (`v₀ + v₁ + v₂ = 0`). -/
theorem gen_dependent : ¬ LinearIndependent ℝ gen := by
  rw [Fintype.not_linearIndependent_iff]
  exact ⟨fun _ => 1, by simpa using gen_sum, 0, one_ne_zero⟩

/-- False Green on the transverse three-cycle: a nonzero realizable defect
lies in every blind spot. -/
theorem false_green :
    ∃ s : Fin 3 → (Fin 2 → ℝ),
      cycleDefect s ≠ 0 ∧ ∀ i, cycleDefect s i ∈ ℝ ∙ gen i :=
  (cycle_blind_spot_dependence gen gen_ne_zero).2 gen_dependent

/-- Every severity: for each scale `t`, the potential assignment has defect
exactly `t • gen i` on edge `i`. -/
theorem scaled_defect (t : ℝ) :
    cycleDefect (potential fun i => t • gen i) = fun i => t • gen i := by
  apply cycleDefect_potential
  rw [← Finset.smul_sum, gen_sum, smul_zero]

end C3

end ObserverVisibility.CycleBlindSpot

#print axioms ObserverVisibility.CycleBlindSpot.cycleDefect_sum
#print axioms ObserverVisibility.CycleBlindSpot.cycleDefect_potential
#print axioms ObserverVisibility.CycleBlindSpot.realizable_iff_sum_eq_zero
#print axioms ObserverVisibility.CycleBlindSpot.cycle_blind_spot_dependence
#print axioms ObserverVisibility.CycleBlindSpot.cycle_unsound_of_finrank_lt
#print axioms ObserverVisibility.CycleBlindSpot.cycle_allGreen_iff_dependent
#print axioms ObserverVisibility.CycleBlindSpot.C3.gen_pairwise_independent
#print axioms ObserverVisibility.CycleBlindSpot.C3.gen_dependent
#print axioms ObserverVisibility.CycleBlindSpot.C3.false_green
#print axioms ObserverVisibility.CycleBlindSpot.C3.scaled_defect

/-
  Theorem 7 extension to invertible translations, mechanized 2026-10-05.
  Edge `i` of the directed cycle on m + 1 sites carries an invertible linear
  translation `r i`; the defect is `(D s)_i = s (i + 1) - r i (s i)`.  The
  transport frames `frame r k = r (k-1) ∘ ⋯ ∘ r 0` and the holonomy
  `frame r (m + 1)` govern the cycle constraint:
  * trivial holonomy: a nonzero realizable defect inside every blind spot
    `K ∙ v i` exists iff the transported generators
    `(frame r (i + 1))⁻¹ (v i)` are linearly dependent;
  * holonomy `H` with `w ↦ w - H w` surjective (in finite dimension: `H` fixes
    no nonzero vector): every cochain is realizable, so every choice of
    nonzero one-dimensional blind spots admits a nonzero All-Green defect.
  Holonomies with nonzero fixed vectors other than the identity are not
  covered.  The statements are linear-algebraic; contractivity of the
  translations is not used.  AuthorityEffect: None.
-/
namespace ObserverVisibility.CycleBlindSpot

open scoped BigOperators

section Transport

variable {K : Type*} [Field K] {W : Type*} [AddCommGroup W] [Module K W] {m : ℕ}

/-- Defect operator of a directed cycle whose edge `i` (from `u_i` to
`u_{i+1}`) carries the invertible translation `r i`. -/
def transDefect (r : Fin (m + 1) → W ≃ₗ[K] W) (s : Fin (m + 1) → W) :
    Fin (m + 1) → W :=
  fun i => s (i + 1) - r i (s i)

/-- With identity translations the defect is the one of Theorem 7. -/
theorem transDefect_refl (s : Fin (m + 1) → W) :
    transDefect (fun _ => LinearEquiv.refl K W) s = cycleDefect s := rfl

/-- Gauge translations `r i = g (i + 1) ∘ (g i)⁻¹` built from site frames. -/
def gaugeTrans (g : Fin (m + 1) → W ≃ₗ[K] W) (i : Fin (m + 1)) : W ≃ₗ[K] W :=
  (g i).symm.trans (g (i + 1))

/-- A gauge change turns the gauge-translation defect into the
identity-translation defect, edgewise conjugated by `g (i + 1)`. -/
theorem transDefect_gauge (g : Fin (m + 1) → W ≃ₗ[K] W) (s : Fin (m + 1) → W)
    (i : Fin (m + 1)) :
    transDefect (gaugeTrans g) s i =
      g (i + 1) (cycleDefect (fun j => (g j).symm (s j)) i) := by
  simp [transDefect, gaugeTrans, cycleDefect, map_sub]

/-- Theorem 7 for gauge translations: a nonzero realizable defect inside
every blind spot exists iff the pulled-back generators are dependent. -/
theorem gauge_blind_spot_dependence (g : Fin (m + 1) → W ≃ₗ[K] W)
    (v : Fin (m + 1) → W) (hv : ∀ i, v i ≠ 0) :
    (∃ s : Fin (m + 1) → W, transDefect (gaugeTrans g) s ≠ 0 ∧
        ∀ i, transDefect (gaugeTrans g) s i ∈ K ∙ v i) ↔
      ¬ LinearIndependent K (fun i => (g (i + 1)).symm (v i)) := by
  rw [← cycle_blind_spot_dependence _
    (fun i => (LinearEquiv.map_ne_zero_iff _).2 (hv i))]
  constructor
  · rintro ⟨s, hne, hmem⟩
    refine ⟨fun j => (g j).symm (s j), ?_, fun i => ?_⟩
    · intro h0
      apply hne
      funext i
      rw [transDefect_gauge, h0]
      simp
    · obtain ⟨a, ha⟩ := Submodule.mem_span_singleton.1 (hmem i)
      refine Submodule.mem_span_singleton.2 ⟨a, ?_⟩
      rw [← map_smul, ha, transDefect_gauge, LinearEquiv.symm_apply_apply]
  · rintro ⟨t, hne, hmem⟩
    refine ⟨fun j => g j (t j), ?_, fun i => ?_⟩
    · intro h0
      apply hne
      funext i
      have h := congrFun h0 i
      rw [transDefect_gauge] at h
      simpa using h
    · obtain ⟨a, ha⟩ := Submodule.mem_span_singleton.1 (hmem i)
      refine Submodule.mem_span_singleton.2 ⟨a, ?_⟩
      rw [transDefect_gauge]
      simp only [LinearEquiv.symm_apply_apply]
      rw [← ha, map_smul, LinearEquiv.apply_symm_apply]

/-- Edge index of the `k`-th step along the cycle (`k mod (m + 1)`). -/
def idx (m k : ℕ) : Fin (m + 1) := ⟨k % (m + 1), Nat.mod_lt _ m.succ_pos⟩

theorem idx_coe (i : Fin (m + 1)) : idx m (i : ℕ) = i :=
  Fin.ext (Nat.mod_eq_of_lt i.isLt)

/-- Transport frames along the path `u_0 → u_1 → ⋯`:
`frame r k = r (k - 1) ∘ ⋯ ∘ r 0`; `frame r (m + 1)` is the holonomy. -/
def frame (r : Fin (m + 1) → W ≃ₗ[K] W) : ℕ → W ≃ₗ[K] W
  | 0 => LinearEquiv.refl K W
  | k + 1 => (frame r k).trans (r (idx m k))

theorem frame_zero_apply (r : Fin (m + 1) → W ≃ₗ[K] W) (y : W) : frame r 0 y = y := rfl

theorem frame_succ_apply (r : Fin (m + 1) → W ≃ₗ[K] W) (i : Fin (m + 1)) (y : W) :
    r i (frame r i y) = frame r ((i : ℕ) + 1) y := by
  rw [show frame r ((i : ℕ) + 1) = (frame r i).trans (r (idx m i)) from rfl,
    LinearEquiv.trans_apply, idx_coe]

/-- With trivial holonomy the translations are the gauge translations of
their own transport frames. -/
theorem gaugeTrans_frame (r : Fin (m + 1) → W ≃ₗ[K] W)
    (hol : frame r (m + 1) = LinearEquiv.refl K W) :
    gaugeTrans (fun i : Fin (m + 1) => frame r i) = r := by
  funext i
  apply LinearEquiv.ext
  intro x
  simp only [gaugeTrans, LinearEquiv.trans_apply]
  by_cases hi : i = Fin.last m
  · subst hi
    have hz := frame_succ_apply r (Fin.last m) ((frame r m).symm x)
    rw [Fin.val_last, hol, LinearEquiv.apply_symm_apply] at hz
    rw [Fin.last_add_one, Fin.val_zero, Fin.val_last]
    exact hz.symm
  · have hlt : i < Fin.last m := lt_of_le_of_ne (Fin.le_last i) hi
    rw [Fin.val_add_one_of_lt hlt, ← frame_succ_apply, LinearEquiv.apply_symm_apply]

/-- **Theorem 7, invertible translations with trivial holonomy.**  A nonzero
realizable defect inside every blind spot `K ∙ v i` exists iff the generators
transported back to `u_0`, `(frame r (i + 1))⁻¹ (v i)`, are linearly
dependent. -/
theorem holonomy_blind_spot_dependence (r : Fin (m + 1) → W ≃ₗ[K] W)
    (hol : frame r (m + 1) = LinearEquiv.refl K W)
    (v : Fin (m + 1) → W) (hv : ∀ i, v i ≠ 0) :
    (∃ s : Fin (m + 1) → W, transDefect r s ≠ 0 ∧
        ∀ i, transDefect r s i ∈ K ∙ v i) ↔
      ¬ LinearIndependent K
        (fun i : Fin (m + 1) => (frame r ((i + 1 : Fin (m + 1)) : ℕ)).symm (v i)) := by
  have h := gauge_blind_spot_dependence (fun i : Fin (m + 1) => frame r i) v hv
  rwa [gaugeTrans_frame r hol] at h

/-- Transported partial sums used to realize an arbitrary cochain. -/
def transPotential (r : Fin (m + 1) → W ≃ₗ[K] W) (Δ : Fin (m + 1) → W) (t₀ : W)
    (i : Fin (m + 1)) : W :=
  frame r i (t₀ + ∑ j ∈ Finset.range (i : ℕ), (frame r (j + 1)).symm (extend Δ j))

/-- **Nontrivial holonomy.**  If `w ↦ w - H w` is surjective for the holonomy
`H = frame r (m + 1)`, every cochain on the cycle is realizable. -/
theorem realizable_of_holonomy_surjective (r : Fin (m + 1) → W ≃ₗ[K] W)
    (hH : Function.Surjective fun w => w - frame r (m + 1) w)
    (Δ : Fin (m + 1) → W) :
    ∃ s : Fin (m + 1) → W, transDefect r s = Δ := by
  set S := ∑ j ∈ Finset.range m, (frame r (j + 1)).symm (extend Δ j) with hS
  obtain ⟨t₀, ht₀⟩ := hH (Δ (Fin.last m) + frame r (m + 1) S)
  simp only at ht₀
  refine ⟨transPotential r Δ t₀, ?_⟩
  funext i
  unfold transDefect transPotential
  by_cases hi : i = Fin.last m
  · subst hi
    rw [Fin.last_add_one, Fin.val_zero, Finset.sum_range_zero, add_zero, frame_succ_apply,
      Fin.val_last, ← hS, map_add, frame_zero_apply, ← sub_sub, ht₀, add_sub_cancel_right]
  · have hlt : i < Fin.last m := lt_of_le_of_ne (Fin.le_last i) hi
    rw [Fin.val_add_one_of_lt hlt, frame_succ_apply, Finset.sum_range_succ, ← add_assoc,
      map_add, add_sub_cancel_left, extend_coe, LinearEquiv.apply_symm_apply]

/-- Consequence: under a surjective `w ↦ w - H w`, every choice of nonzero
one-dimensional blind spots admits a nonzero realizable All-Green defect
(already on a single edge), as on a tree. -/
theorem unsound_of_holonomy_surjective (r : Fin (m + 1) → W ≃ₗ[K] W)
    (hH : Function.Surjective fun w => w - frame r (m + 1) w)
    (v : Fin (m + 1) → W) (hv : ∀ i, v i ≠ 0) :
    ∃ s : Fin (m + 1) → W, transDefect r s ≠ 0 ∧ ∀ i, transDefect r s i ∈ K ∙ v i := by
  obtain ⟨s, hs⟩ := realizable_of_holonomy_surjective r hH (Pi.single 0 (v 0))
  refine ⟨s, ?_, fun i => ?_⟩
  · rw [hs]
    intro h
    exact hv 0 (by simpa using congrFun h 0)
  · rw [hs]
    by_cases hi : i = 0
    · subst hi
      rw [Pi.single_eq_same]
      exact Submodule.mem_span_singleton_self (v 0)
    · rw [Pi.single_eq_of_ne hi]
      exact Submodule.zero_mem _

/-- Finite-dimensional form: if the holonomy fixes no nonzero vector, every
choice of nonzero one-dimensional blind spots admits a nonzero realizable
All-Green defect. -/
theorem unsound_of_holonomy_fixed_point_free [FiniteDimensional K W]
    (r : Fin (m + 1) → W ≃ₗ[K] W)
    (hfix : ∀ w, frame r (m + 1) w = w → w = 0)
    (v : Fin (m + 1) → W) (hv : ∀ i, v i ≠ 0) :
    ∃ s : Fin (m + 1) → W, transDefect r s ≠ 0 ∧ ∀ i, transDefect r s i ∈ K ∙ v i := by
  let f : W →ₗ[K] W := LinearMap.id - (frame r (m + 1) : W →ₗ[K] W)
  have hf : ∀ w, f w = w - frame r (m + 1) w := fun w => rfl
  have hinj : Function.Injective f := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro w hw
    rw [hf, sub_eq_zero] at hw
    exact hfix w hw.symm
  have hsurj := LinearMap.injective_iff_surjective.mp hinj
  refine unsound_of_holonomy_surjective r (fun y => ?_) v hv
  obtain ⟨w, hw⟩ := hsurj y
  exact ⟨w, by rw [← hw, hf]⟩

end Transport

/- Sign-flipping handoffs on the three-cycle: holonomy `-id`. -/
namespace SignFlip

variable {W : Type*} [AddCommGroup W] [Module ℝ W]

theorem frame_three (w : W) :
    frame (fun _ : Fin 3 => LinearEquiv.neg ℝ (M := W)) 3 w = -w := by
  simp [frame]

/-- On a three-cycle whose handoffs all flip sign, every choice of nonzero
one-dimensional blind spots admits a nonzero realizable All-Green defect. -/
theorem unsound (v : Fin 3 → W) (hv : ∀ i, v i ≠ 0) :
    ∃ s : Fin 3 → W,
      transDefect (fun _ => LinearEquiv.neg ℝ (M := W)) s ≠ 0 ∧
        ∀ i, transDefect (fun _ => LinearEquiv.neg ℝ (M := W)) s i ∈ ℝ ∙ v i := by
  refine unsound_of_holonomy_surjective _ (fun y => ⟨(2 : ℝ)⁻¹ • y, ?_⟩) v hv
  show (2 : ℝ)⁻¹ • y - frame _ 3 ((2 : ℝ)⁻¹ • y) = y
  rw [frame_three, sub_neg_eq_add, ← two_smul ℝ, smul_smul,
    mul_inv_cancel₀ (two_ne_zero : (2 : ℝ) ≠ 0), one_smul]

end SignFlip

end ObserverVisibility.CycleBlindSpot

/-
  Redundancy Corollary of the note (Boxed Theorem, §4), mechanized
  2026-10-05.  All-Green, and hence soundness on any set of realizable
  defects, depends on an observer family only through its edgewise joint
  blind spots.  Adjoining observers whose edge kernels contain the existing
  joint blind spots (in particular, duplicating the existing observers)
  leaves All-Green unchanged and therefore cannot remove a false green.
  The measurement-dimension count `k` of the Boxed Theorem is not formalized
  here.  AuthorityEffect: None.
-/
namespace ObserverVisibility.Redundancy

universe u

variable {E : Type*} {F : E → Type*} [∀ e, SeminormedAddCommGroup (F e)]
variable {A A₂ : Type*} {V : A → E → Type u} [∀ a e, NormedAddCommGroup (V a e)]
variable {V₂ : A₂ → E → Type u} [∀ b e, NormedAddCommGroup (V₂ b e)]

/-- Joint blind spot of the carrier `C` on edge `e`. -/
def EdgeKernel (C : Carrier A F V) (e : E) (w : F e) : Prop :=
  ∀ a, e ∈ C.watched a → C.obs a e w = 0

/-- Kernel monotonicity: if every joint blind spot of `C` lies in the
corresponding joint blind spot of `C₂`, All-Green for `C` implies All-Green
for `C₂`. -/
theorem allGreen_of_kernel_le (C : Carrier A F V) (C₂ : Carrier A₂ F V₂)
    (hle : ∀ e w, EdgeKernel C e w → EdgeKernel C₂ e w) (Δ : ∀ e, F e)
    (h : AllGreen C Δ) : AllGreen C₂ Δ := by
  rw [allGreen_iff_kernel] at h ⊢
  exact fun e => hle e (Δ e) (h e)

/-- Soundness on any defect set depends only on the joint blind spots. -/
theorem sound_iff_of_kernel_eq (C : Carrier A F V) (C₂ : Carrier A₂ F V₂)
    (heq : ∀ e w, EdgeKernel C e w ↔ EdgeKernel C₂ e w) (S : Set (∀ e, F e)) :
    (∀ Δ ∈ S, AllGreen C Δ → Δ = 0) ↔ (∀ Δ ∈ S, AllGreen C₂ Δ → Δ = 0) := by
  constructor
  · intro h Δ hS hg
    exact h Δ hS (allGreen_of_kernel_le C₂ C (fun e w => (heq e w).2) Δ hg)
  · intro h Δ hS hg
    exact h Δ hS (allGreen_of_kernel_le C C₂ (fun e w => (heq e w).1) Δ hg)

/-- Value spaces of the augmented observer family `A ⊕ A₂`. -/
def sumV (V : A → E → Type u) (V₂ : A₂ → E → Type u) : A ⊕ A₂ → E → Type u
  | Sum.inl a => V a
  | Sum.inr b => V₂ b

instance sumV.instNormed : ∀ (x : A ⊕ A₂) (e : E), NormedAddCommGroup (sumV V V₂ x e)
  | Sum.inl a, e => inferInstanceAs (NormedAddCommGroup (V a e))
  | Sum.inr b, e => inferInstanceAs (NormedAddCommGroup (V₂ b e))

/-- Adjoin the observers of `C₂` to those of `C`. -/
def augment (C : Carrier A F V) (C₂ : Carrier A₂ F V₂) :
    Carrier (A ⊕ A₂) F (sumV V V₂) where
  watched := Sum.elim C.watched C₂.watched
  obs
    | Sum.inl a, e, w => C.obs a e w
    | Sum.inr b, e, w => C₂.obs b e w
  contractive
    | Sum.inl a, e, w => C.contractive a e w
    | Sum.inr b, e, w => C₂.contractive b e w

/-- **Redundancy Corollary.**  Adjoining observers whose edge kernels contain
the existing joint blind spots leaves All-Green unchanged. -/
theorem augment_allGreen_iff (C : Carrier A F V) (C₂ : Carrier A₂ F V₂)
    (hsub : ∀ e w, EdgeKernel C e w → EdgeKernel C₂ e w) (Δ : ∀ e, F e) :
    AllGreen (augment C C₂) Δ ↔ AllGreen C Δ := by
  rw [allGreen_iff_kernel, allGreen_iff_kernel]
  constructor
  · intro h e a ha
    exact h e (Sum.inl a) ha
  · intro h e x hx
    cases x with
    | inl a => exact h e a hx
    | inr b => exact hsub e (Δ e) (fun a ha => h e a ha) b hx

/-- Duplicating every observer leaves All-Green unchanged. -/
theorem duplicate_allGreen_iff (C : Carrier A F V) (Δ : ∀ e, F e) :
    AllGreen (augment C C) Δ ↔ AllGreen C Δ :=
  augment_allGreen_iff C C (fun _ _ h => h) Δ

/-- Redundant observers cannot remove a false green: a nonzero All-Green
defect in `S` for `C` stays All-Green after the augmentation. -/
theorem augment_preserves_false_green (C : Carrier A F V) (C₂ : Carrier A₂ F V₂)
    (hsub : ∀ e w, EdgeKernel C e w → EdgeKernel C₂ e w) (S : Set (∀ e, F e))
    (h : ∃ Δ ∈ S, Δ ≠ 0 ∧ AllGreen C Δ) :
    ∃ Δ ∈ S, Δ ≠ 0 ∧ AllGreen (augment C C₂) Δ := by
  obtain ⟨Δ, hS, hne, hg⟩ := h
  exact ⟨Δ, hS, hne, (augment_allGreen_iff C C₂ hsub Δ).2 hg⟩

/-- Regime 3 on cycles: augmenting a Theorem 7 carrier with redundant
observers leaves the dependence criterion unchanged (e.g. the transverse
three-cycle with every check duplicated stays unsound). -/
theorem augment_cycle_allGreen_iff_dependent {W : Type*} [NormedAddCommGroup W]
    [NormedSpace ℝ W] {m : ℕ} {V : A → Fin (m + 1) → Type u}
    [∀ a e, NormedAddCommGroup (V a e)] {V₂ : A₂ → Fin (m + 1) → Type u}
    [∀ b e, NormedAddCommGroup (V₂ b e)]
    (C : Carrier A (fun _ : Fin (m + 1) => W) V)
    (C₂ : Carrier A₂ (fun _ : Fin (m + 1) => W) V₂) (v : Fin (m + 1) → W)
    (hv : ∀ i, v i ≠ 0)
    (hK : ∀ i (w : W), (∀ a, i ∈ C.watched a → C.obs a i w = 0) ↔ w ∈ ℝ ∙ v i)
    (hsub : ∀ e w, EdgeKernel C e w → EdgeKernel C₂ e w) :
    (∃ s : Fin (m + 1) → W, CycleBlindSpot.cycleDefect s ≠ 0 ∧
        AllGreen (augment C C₂) (CycleBlindSpot.cycleDefect s)) ↔
      ¬ LinearIndependent ℝ v := by
  simp_rw [augment_allGreen_iff C C₂ hsub]
  exact CycleBlindSpot.cycle_allGreen_iff_dependent C v hv hK

end ObserverVisibility.Redundancy

#print axioms ObserverVisibility.CycleBlindSpot.transDefect_gauge
#print axioms ObserverVisibility.CycleBlindSpot.gauge_blind_spot_dependence
#print axioms ObserverVisibility.CycleBlindSpot.gaugeTrans_frame
#print axioms ObserverVisibility.CycleBlindSpot.holonomy_blind_spot_dependence
#print axioms ObserverVisibility.CycleBlindSpot.realizable_of_holonomy_surjective
#print axioms ObserverVisibility.CycleBlindSpot.unsound_of_holonomy_surjective
#print axioms ObserverVisibility.CycleBlindSpot.unsound_of_holonomy_fixed_point_free
#print axioms ObserverVisibility.CycleBlindSpot.SignFlip.unsound
#print axioms ObserverVisibility.Redundancy.allGreen_of_kernel_le
#print axioms ObserverVisibility.Redundancy.sound_iff_of_kernel_eq
#print axioms ObserverVisibility.Redundancy.augment_allGreen_iff
#print axioms ObserverVisibility.Redundancy.duplicate_allGreen_iff
#print axioms ObserverVisibility.Redundancy.augment_preserves_false_green
#print axioms ObserverVisibility.Redundancy.augment_cycle_allGreen_iff_dependent
