/-
  PO-000 §7.4 mechanization: observer visibility.

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

namespace PO000.ObserverVisibility

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

end PO000.ObserverVisibility

/-
  The three-patch witness of Proposition 7.4.5 and the scaling family of
  Corollary 7.4.6, with fibers `ℝ³` under the `ℓ¹` norm.  Edges are encoded as
  pairs `(i, k) : Fin 3 × Bool`: patch `u_i` has exactly two covering edges,
  from its two overlaps, selected by `k`; the watcher of `(i, k)` is observer
  `i`, matching `W((x_{ij}, u_i)) = {i}` in the paper.  Restrictions are
  identities and the section vanishes on overlaps, so the defect on `(i, k)`
  is `s(u_i)`.
-/
namespace PO000.ObserverVisibility.ThreePatch

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

/-- Realization: the defect family is induced by an explicit section of the
three-patch diagram (patch values `lam · e_i`, overlap values `0`, identity
restrictions), witnessing that these are section defects and the raw defect
cochain is exact by construction (§7.4.8, remark 1). -/
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
  simp [deleteCoord, Pi.single_eq_of_ne (Fin.succAbove_ne a i)]

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
  simp [Pi.single_eq_of_ne (Fin.succAbove_ne i _)]

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

end PO000.ObserverVisibility.ThreePatch

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
namespace PO000.ObserverVisibility.Coupled

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

end PO000.ObserverVisibility.Coupled

/-
  The S14 quotient witness, on the scalar coupled diagram: fibers `ℝ`, two
  edges from the shared overlap with zero restrictions, so `im(d_0)` is the
  diagonal `{(-α, -α)}`.  The cochain `ω = (1, -1)` has exact `ℓ¹` quotient
  distance `2` from `im(d_0)`: the triangle inequality gives the lower bound
  on every repair, and `α = 0` attains it.  In particular `ω` is not exact,
  and `Φ([ω]) = 2 > 0` for this declared finite gauge.
-/
namespace PO000.ObserverVisibility.QuotientWitness

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

end PO000.ObserverVisibility.QuotientWitness

#print axioms PO000.ObserverVisibility.tally_le_rawNorm
#print axioms PO000.ObserverVisibility.localGreen_of_globalGreen
#print axioms PO000.ObserverVisibility.allGreen_iff_kernel
#print axioms PO000.ObserverVisibility.rawNorm_eq_zero_of_allGreen
#print axioms PO000.ObserverVisibility.coverage_of_jointTrivial
#print axioms PO000.ObserverVisibility.ThreePatch.three_patch_witness
#print axioms PO000.ObserverVisibility.ThreePatch.rawNorm_scaled
#print axioms PO000.ObserverVisibility.ThreePatch.no_recovery_modulus
#print axioms PO000.ObserverVisibility.Coupled.full_coverage
#print axioms PO000.ObserverVisibility.Coupled.joint_kernel_nontrivial
#print axioms PO000.ObserverVisibility.Coupled.allGreen_forces_zero
#print axioms PO000.ObserverVisibility.QuotientWitness.repair_mass_ge_two
#print axioms PO000.ObserverVisibility.QuotientWitness.repair_mass_attained
#print axioms PO000.ObserverVisibility.QuotientWitness.omega_not_exact
