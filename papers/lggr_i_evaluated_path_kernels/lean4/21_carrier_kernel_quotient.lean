/-
Paper 020, §11.6: Bounded Evaluator Carriers over Prompt-Packet Projections.

This file discharges the Lean obligation **OB-2** of the Epoch-19 extension
"Bounded Evaluators, Prompt-Packet Projections, and the Epistemic Ceiling of LLM
Evaluation" (`PKT-20260722-RES-EPOCH19`): the transport of the Lemma 1.5.2 /
Lemma 1.5.10 dashboard arguments to the packet (carrier-kernel) quotient, and the
mechanization of the §11.6 propositions that derive the §1.2 local-green /
global-red discrepancy from *carrier-kernel coverage*.

Scope and firewall (matches the paper's own `[MECHANIZED-PARTIAL]` ceiling):
  * Everything here is finite, `Bool`/`Int`-valued, and constructed from declared
    projections.  The real weight `e^{-β𝒜}` of §2 is NOT constructed; Corollary
    11.6.9.1's strict evaluated-mass inequality `Z^Q_g < Z^Q_ℓ` is mechanized only
    in its finite counting form (globally-passing count `<` class size).  The
    real-weighted reading remains a declared reading, located not eliminated
    (PL-020-4 discipline).
  * This is diagnostic.  Nothing here mints authority: the theorems classify and
    price a gluing obstruction; they do not authorize.  "Observers reveal or
    erase; they do not create" — the carrier does not create the obstruction, it
    erases the distinctions that would have exposed it locally.
  * Proposition 11.6.5's cardinality bound `≤ 2^{|π_K(Ω)|}` is the immediate
    finite-image corollary of the fiber-invariance characterization proved here
    (`carrier_bounded_iff_invariant`); the load-bearing content is that
    characterization together with the disagreement lemma `verdict_ceiling`.

Substrate: `OmegaCore.PrimitiveDifference` (the ZeroRel / quotient / invariance
kernel; the "third declared zero relation" `∼_K` of Definition 11.6.2) and the
§1–§4 `Int`-valued defect arithmetic of `L020_01`.  Mathlib-free (Lean core only).
-/

import «01_local_green_counterexample»
import primitive_difference

namespace PaperAE004

open OmegaCore

universe u v w z

/- ---- Bool arithmetic helpers (cased on genuine variables) ---- -/

private theorem bool_cases (b : Bool) : b = false ∨ b = true := by
  cases b
  · exact Or.inl rfl
  · exact Or.inr rfl

private theorem b2i_ne_of_ne {x y : Bool} (h : x ≠ y) : b2i x ≠ b2i y := by
  cases x with
  | false =>
    cases y with
    | false => exact absurd rfl h
    | true => decide
  | true =>
    cases y with
    | false => decide
    | true => exact absurd rfl h

private theorem bool_neq_pass_sum {x y : Bool} (h : x ≠ y) :
    b2i x + b2i y < (2 : Int) := by
  cases x with
  | false =>
    cases y with
    | false => exact absurd rfl h
    | true => decide
  | true =>
    cases y with
    | false => decide
    | true => exact absurd rfl h

private theorem ne_true_eq_false {x y : Bool} (hx : x = true) (hne : x ≠ y) :
    y = false := by
  cases y with
  | false => rfl
  | true => rw [hx] at hne; exact absurd rfl hne

/- ===================================================================== -/
/-  §11.6.1–11.6.2 — Bounded observer carrier and carrier kernel          -/
/- ===================================================================== -/

/-- Definition 11.6.2 (carrier kernel `∼_K`), as an `OmegaCore.PrimitiveDifference`.
The zero relation is fiber-equality of the declared projection `π`: it depends
only on `π`, not on any verdict map.  This is the "third declared zero relation"
of §11.6, alongside the local-dashboard relation (Lemma 1.5.2) and the diagnostic
relation (Lemma 1.5.10). -/
def carrierKernelPD {Ω : Type u} {P : Type v} (π : Ω → P) :
    OmegaCore.PrimitiveDifference Ω Prop where
  δ := fun a b => π a = π b
  Zero := fun h => h
  zero_refl := fun _ => rfl
  zero_symm := fun _ _ h => h.symm
  zero_trans := fun _ _ _ hxy hyz => hxy.trans hyz

theorem carrierKernelPD_zeroRel {Ω : Type u} {P : Type v} (π : Ω → P) (a b : Ω) :
    (carrierKernelPD π).ZeroRel a b ↔ π a = π b :=
  Iff.rfl

/-- The evaluator induced by a bounded observer carrier: `E_{C_K} = e_K ∘ π_K`. -/
def inducedEvaluator {Ω : Type u} {P : Type v} (π : Ω → P) (e : P → Bool) : Ω → Bool :=
  fun γ => e (π γ)

/-- An evaluator `E` is `C_K`-bounded when it factors through the carrier as
`e ∘ π_K` for some verdict map `e`. -/
def CarrierBounded {Ω : Type u} {P : Type v} (π : Ω → P) (E : Ω → Bool) : Prop :=
  ∃ e : P → Bool, E = inducedEvaluator π e

/- ---- §11.6.2 Kernel constancy and the finite verdict ceiling ---- -/

/-- Proposition 11.6.4 (Kernel constancy), pointwise: a carrier-bounded evaluator
takes equal values on carrier-kernel-related traces. -/
theorem kernel_constancy {Ω : Type u} {P : Type v} (π : Ω → P) (e : P → Bool)
    {γ γ' : Ω} (h : π γ = π γ') :
    inducedEvaluator π e γ = inducedEvaluator π e γ' := by
  unfold inducedEvaluator
  rw [h]

/-- Proposition 11.6.4, as fiber-invariance on the carrier-kernel quotient:
every induced evaluator is `InvariantCongruent` for `∼_K`. -/
theorem induced_evaluator_invariant {Ω : Type u} {P : Type v}
    (π : Ω → P) (e : P → Bool) :
    (carrierKernelPD π).InvariantCongruent (inducedEvaluator π e) := by
  intro a b hab
  have hpi : π a = π b := hab
  exact kernel_constancy π e hpi

/-- Proposition 11.6.4, packaged for an arbitrary `C_K`-bounded evaluator. -/
theorem carrier_bounded_invariant {Ω : Type u} {P : Type v}
    (π : Ω → P) (E : Ω → Bool) (hE : CarrierBounded π E) :
    (carrierKernelPD π).InvariantCongruent E := by
  obtain ⟨e, rfl⟩ := hE
  exact induced_evaluator_invariant π e

/-- Converse of Proposition 11.6.4/11.6.5: an evaluator invariant on the
carrier-kernel classes is exactly a `C_K`-bounded evaluator (the indicator of a
`π`-saturated set).  Uses classical choice to pick a verdict on each realized
class. -/
theorem invariant_implies_carrier_bounded {Ω : Type u} {P : Type v}
    (π : Ω → P) (E : Ω → Bool)
    (hInv : (carrierKernelPD π).InvariantCongruent E) :
    CarrierBounded π E := by
  classical
  refine ⟨fun p => if h : ∃ ω : Ω, π ω = p then E (Classical.choose h) else false, ?_⟩
  funext γ
  have hex : ∃ ω : Ω, π ω = π γ := ⟨γ, rfl⟩
  have hspec : (carrierKernelPD π).ZeroRel (Classical.choose hex) γ :=
    Classical.choose_spec hex
  simp only [inducedEvaluator, dif_pos hex]
  exact (hInv (Classical.choose hex) γ hspec).symm

/-- Proposition 11.6.5 (characterization half): the `C_K`-bounded evaluators are
exactly the carrier-kernel-invariant predicates.  (The count `≤ 2^{|π(Ω)|}` is the
immediate finite-image corollary of this bijection with `π(Ω) → Bool`.) -/
theorem carrier_bounded_iff_invariant {Ω : Type u} {P : Type v}
    (π : Ω → P) (E : Ω → Bool) :
    CarrierBounded π E ↔ (carrierKernelPD π).InvariantCongruent E := by
  constructor
  · exact carrier_bounded_invariant π E
  · exact invariant_implies_carrier_bounded π E

/-- Proposition 11.6.5 (verdict ceiling): if a declared target predicate `T` is
non-constant on some realized carrier-kernel class, then *every* carrier-bounded
evaluator disagrees with `T` on at least one recorded trace.  No amount of
verdict-map tuning can recover a distinction the carrier already erased. -/
theorem verdict_ceiling {Ω : Type u} {P : Type v}
    (π : Ω → P) (e : P → Bool) (T : Ω → Bool)
    {γ γ' : Ω} (hpi : π γ = π γ') (hT : T γ ≠ T γ') :
    ∃ ω : Ω, inducedEvaluator π e ω ≠ T ω := by
  rcases Classical.em (inducedEvaluator π e γ = T γ) with hγ | hγ
  · -- if the evaluator agrees with `T` at `γ`, it must disagree at `γ'`.
    refine ⟨γ', ?_⟩
    intro hγ'
    apply hT
    rw [← hγ, kernel_constancy π e hpi, hγ']
  · exact ⟨γ, hγ⟩

/-- Corollary 11.6.6 (witness/fabrication indistinguishability inside the kernel):
on a realized `π`-collision `γ_w ∼_K γ_f`, every `C_K`-bounded evaluator assigns
the two traces equal verdicts.  A green packet verdict is a statement about the
packet image, not about the witness predicate `W`. -/
theorem witness_fabrication_indistinguishable {Ω : Type u} {P : Type v}
    (π : Ω → P) (e : P → Bool) {γw γf : Ω} (h : π γw = π γf) :
    inducedEvaluator π e γw = inducedEvaluator π e γf :=
  kernel_constancy π e h

/-- Corollary 11.6.6 (contrapositive form): if the witness predicate `W` separates
a `π`-collided pair, then no `C_K`-bounded evaluator can equal `W` on the corpus. -/
theorem carrier_cannot_separate_witness {Ω : Type u} {P : Type v}
    (π : Ω → P) (e : P → Bool) (W : Ω → Bool)
    {γw γf : Ω} (hcollide : π γw = π γf) (hW : W γw ≠ W γf) :
    ∃ ω : Ω, inducedEvaluator π e ω ≠ W ω :=
  verdict_ceiling π e W hcollide hW

/- Concrete witness that Corollary 11.6.6's hypotheses are realizable (anti-vacuity):
the collapsing carrier `Bool → Unit` collides `true`/`false`, and the identity
witness predicate separates them. -/
def collapseUnit : Bool → Unit := fun _ => ()

theorem collapse_unit_collides : collapseUnit true = collapseUnit false := rfl

theorem witness_fabrication_instance :
    ∃ ω : Bool, inducedEvaluator collapseUnit (fun _ => true) ω ≠ id ω :=
  carrier_cannot_separate_witness collapseUnit (fun _ => true) id
    collapse_unit_collides (by decide)

/- ===================================================================== -/
/-  §11.6.3 — Composed evaluator networks and the joint carrier          -/
/- ===================================================================== -/

/-- A composed trace carrying its declared G1 decomposition `(γ₁, γ₂)`.  Modelling
the decomposition as primitive is the paper's "declared decomposition record"
reading of G1 (Definition 11.6.7). -/
structure Composed (Ω₁ : Type u) (Ω₂ : Type v) where
  g1 : Ω₁
  g2 : Ω₂

/-- Definition 11.6.7 (joint local carrier) `Π(γ) = (π_{K₁}(γ₁), π_{K₂}(γ₂))`. -/
def jointCarrier {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) : Composed Ω₁ Ω₂ → P₁ × P₂ :=
  fun c => (π₁ c.g1, π₂ c.g2)

/-- The joint carrier kernel `∼_Π` as a primitive-difference zero relation. -/
def jointCarrierPD {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) :
    OmegaCore.PrimitiveDifference (Composed Ω₁ Ω₂) Prop :=
  carrierKernelPD (jointCarrier π₁ π₂)

/-- The local product `E₁E₂` on composed traces, as the `Int` value
`localProduct (e₁ (π₁ γ₁)) (e₂ (π₂ γ₂))` of §1. -/
def localProductComposed {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool) :
    Composed Ω₁ Ω₂ → Int :=
  fun c => localProduct (e₁ (π₁ c.g1)) (e₂ (π₂ c.g2))

/-- A composed trace is locally green when both carrier-bounded local evaluators
pass. -/
def LocallyGreen {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (c : Composed Ω₁ Ω₂) : Prop :=
  e₁ (π₁ c.g1) = true ∧ e₂ (π₂ c.g2) = true

/-- The evaluator gluing defect `Δ_Eval` on composed traces (§4), with a global
evaluator `E_g`. -/
def deltaComposed {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool) : Composed Ω₁ Ω₂ → Int :=
  fun c => deltaEval (e₁ (π₁ c.g1)) (e₂ (π₂ c.g2)) (Eg c)

/-- Proposition 11.6.8 (the local product is carrier-measurable): `E₁E₂` is
constant on realized `Π`-classes, i.e. each `Π`-class is locally green as a whole
or locally red as a whole. -/
theorem local_product_invariant {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool) :
    (jointCarrierPD π₁ π₂).InvariantCongruent
      (localProductComposed π₁ π₂ e₁ e₂) := by
  intro a b hab
  have hpi : jointCarrier π₁ π₂ a = jointCarrier π₁ π₂ b := hab
  have h1 : π₁ a.g1 = π₁ b.g1 := congrArg Prod.fst hpi
  have h2 : π₂ a.g2 = π₂ b.g2 := congrArg Prod.snd hpi
  unfold localProductComposed
  rw [h1, h2]

/-- Local-greenness is a property of the `Π`-class. -/
theorem locally_green_class_transport {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hgreen : LocallyGreen π₁ π₂ e₁ e₂ c) :
    LocallyGreen π₁ π₂ e₁ e₂ c' := by
  obtain ⟨hg1, hg2⟩ := hgreen
  have h1 : π₁ c.g1 = π₁ c'.g1 := congrArg Prod.fst hclass
  have h2 : π₂ c.g2 = π₂ c'.g2 := congrArg Prod.snd hclass
  refine ⟨?_, ?_⟩
  · rw [← h1]; exact hg1
  · rw [← h2]; exact hg2

/-- **Proposition 11.6.9 (Kernel-mixing forces the local-green / global-red
discrepancy).**  If a `Π`-class is locally green and *mixed* (the global evaluator
is non-constant on it), it contains a trace with `Δ_Eval = -1`.  This is the
carrier-kernel-coverage source of the §1.2 pattern: the defect (where `E_g`
varies) lives inside a fiber the local carriers cannot see. -/
theorem green_mixed_forces_negative_defect
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hgreen : LocallyGreen π₁ π₂ e₁ e₂ c)
    (hmix : Eg c ≠ Eg c') :
    ∃ d : Composed Ω₁ Ω₂,
      (d = c ∨ d = c') ∧
      jointCarrier π₁ π₂ d = jointCarrier π₁ π₂ c ∧
      deltaComposed π₁ π₂ e₁ e₂ Eg d = -1 := by
  obtain ⟨hg1, hg2⟩ := hgreen
  obtain ⟨hg1', hg2'⟩ :=
    locally_green_class_transport π₁ π₂ e₁ e₂ hclass ⟨hg1, hg2⟩
  rcases bool_cases (Eg c) with hEc | hEc
  · -- Eg c = false: the trace c itself is locally green, globally red.
    refine ⟨c, Or.inl rfl, rfl, ?_⟩
    show deltaEval (e₁ (π₁ c.g1)) (e₂ (π₂ c.g2)) (Eg c) = -1
    rw [hg1, hg2, hEc]
    exact local_green_global_red_counterexample
  · -- Eg c = true: mixedness forces Eg c' = false; the trace c' witnesses.
    have hEc' : Eg c' = false := ne_true_eq_false hEc hmix
    refine ⟨c', Or.inr rfl, hclass.symm, ?_⟩
    show deltaEval (e₁ (π₁ c'.g1)) (e₂ (π₂ c'.g2)) (Eg c') = -1
    rw [hg1', hg2', hEc']
    exact local_green_global_red_counterexample

/-- Proposition 11.6.9 (sample form): a recorded corpus containing a locally green
mixed pair contains a recorded trace with `Δ_Eval = -1`; hence G3 fails on the
sample and `EGD > 0`.  (The aggregate `NGD_count ≥ #{green mixed classes}` is the
elementary summation of this per-class bound over disjoint classes.) -/
theorem sample_green_mixed_forces_ngd
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    (sample : List (Composed Ω₁ Ω₂))
    {c c' : Composed Ω₁ Ω₂}
    (hc : c ∈ sample) (hc' : c' ∈ sample)
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hgreen : LocallyGreen π₁ π₂ e₁ e₂ c)
    (hmix : Eg c ≠ Eg c') :
    ∃ d : Composed Ω₁ Ω₂, d ∈ sample ∧ deltaComposed π₁ π₂ e₁ e₂ Eg d = -1 := by
  obtain ⟨d, hd, _, hdelta⟩ :=
    green_mixed_forces_negative_defect π₁ π₂ e₁ e₂ Eg hclass hgreen hmix
  refine ⟨d, ?_, hdelta⟩
  cases hd with
  | inl h => rw [h]; exact hc
  | inr h => rw [h]; exact hc'

private theorem localProduct_true_true : localProduct true true = 1 := rfl

/-- Corollary 11.6.9.1 (finite hidden-failure gap, no real weights).  On a locally
green mixed `Π`-pair, the count of globally-passing traces is strictly below the
**local-product-passing count** — and the latter is derived to be full (`= 2`) from
local greenness, not assumed: `Z^Q_g < Z^Q_ℓ` in its finite counting form.  The
`e^{-β𝒜}`-weighted strict inequality is the declared reading; no real weight is
constructed here. -/
theorem green_mixed_strict_pass_gap
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hgreen : LocallyGreen π₁ π₂ e₁ e₂ c)
    (hmix : Eg c ≠ Eg c') :
    b2i (Eg c) + b2i (Eg c')
      < localProductComposed π₁ π₂ e₁ e₂ c + localProductComposed π₁ π₂ e₁ e₂ c' := by
  obtain ⟨hg1, hg2⟩ := hgreen
  obtain ⟨hg1', hg2'⟩ :=
    locally_green_class_transport π₁ π₂ e₁ e₂ hclass ⟨hg1, hg2⟩
  have hlpc : localProductComposed π₁ π₂ e₁ e₂ c = 1 := by
    show localProduct (e₁ (π₁ c.g1)) (e₂ (π₂ c.g2)) = 1
    rw [hg1, hg2, localProduct_true_true]
  have hlpc' : localProductComposed π₁ π₂ e₁ e₂ c' = 1 := by
    show localProduct (e₁ (π₁ c'.g1)) (e₂ (π₂ c'.g2)) = 1
    rw [hg1', hg2', localProduct_true_true]
  have hb := bool_neq_pass_sum hmix
  omega

/-- Proposition 11.6.10 (No downstream refinement in judge chains): the carrier
kernel coarsens under any post-composition — a pair collided at the carrier stays
collided under every downstream computable map and every aggregation of the
emissions. -/
theorem no_downstream_refinement {Ω : Type u} {P : Type v} {R : Type w}
    (π : Ω → P) (chain : P → R) {γ γ' : Ω} (h : π γ = π γ') :
    chain (π γ) = chain (π γ') := by
  rw [h]

/-- Proposition 11.6.10, kernel form: `∼_K ⊆ ∼_{ρ∘π}` for every post-composition
`ρ`. -/
theorem kernel_coarsens_under_post {Ω : Type u} {P : Type v} {R : Type w}
    (π : Ω → P) (ρ : P → R) {γ γ' : Ω}
    (h : (carrierKernelPD π).ZeroRel γ γ') :
    (carrierKernelPD (fun x => ρ (π x))).ZeroRel γ γ' := by
  have hpi : π γ = π γ' := h
  show ρ (π γ) = ρ (π γ')
  rw [hpi]

/-- Proposition 11.6.10, verdict form: an appended bounded judge `v ∘ chain` cannot
separate a carrier-collided pair (including the witness/fabrication pair of
Corollary 11.6.6). -/
theorem downstream_cannot_separate_collided_pair
    {Ω : Type u} {P : Type v} {R : Type w}
    (π : Ω → P) (chain : P → R) (v : R → Bool)
    {γw γf : Ω} (h : π γw = π γf) :
    v (chain (π γw)) = v (chain (π γf)) := by
  rw [h]

/- ===================================================================== -/
/-  §11.6.3 — Proposition 11.6.11: the packet-auditability dichotomy      -/
/- ===================================================================== -/

/-- The composed evaluator gluing defect is `Π`-invariant whenever the global
evaluator is (needed for case (a)). -/
theorem delta_invariant_of_Eg_invariant
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    (hEg : (jointCarrierPD π₁ π₂).InvariantCongruent Eg) :
    (jointCarrierPD π₁ π₂).InvariantCongruent (deltaComposed π₁ π₂ e₁ e₂ Eg) := by
  intro a b hab
  have hEgab : Eg a = Eg b := hEg a b hab
  have hpi : jointCarrier π₁ π₂ a = jointCarrier π₁ π₂ b := hab
  have h1 : π₁ a.g1 = π₁ b.g1 := congrArg Prod.fst hpi
  have h2 : π₂ a.g2 = π₂ b.g2 := congrArg Prod.snd hpi
  show deltaEval (e₁ (π₁ a.g1)) (e₂ (π₂ a.g2)) (Eg a)
      = deltaEval (e₁ (π₁ b.g1)) (e₂ (π₂ b.g2)) (Eg b)
  rw [h1, h2, hEgab]

/-- **Proposition 11.6.11(a).**  If the global evaluator is constant on every
realized `Π`-class, the diagnostic pair `(E₁E₂, E_g)` factors through the packet
quotient (the Lemma 1.5.10 quotient-sufficiency argument, at packet granularity). -/
theorem diagnostic_pair_factors_when_Eg_invariant
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    (hEg : (jointCarrierPD π₁ π₂).InvariantCongruent Eg) :
    ∃ F : (jointCarrierPD π₁ π₂).ResidualQuotient → Int × Bool,
      ∀ c : Composed Ω₁ Ω₂,
        F ((jointCarrierPD π₁ π₂).classOf c)
          = (localProductComposed π₁ π₂ e₁ e₂ c, Eg c) := by
  have hInv :
      (jointCarrierPD π₁ π₂).InvariantCongruent
        (fun c => (localProductComposed π₁ π₂ e₁ e₂ c, Eg c)) :=
    (OmegaCore.PrimitiveDifference.invariantCongruent_pair_iff
        (jointCarrierPD π₁ π₂) (localProductComposed π₁ π₂ e₁ e₂) Eg).mpr
      ⟨local_product_invariant π₁ π₂ e₁ e₂, hEg⟩
  exact (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
    (jointCarrierPD π₁ π₂) (fun c => (localProductComposed π₁ π₂ e₁ e₂ c, Eg c))).mpr hInv

/-- Proposition 11.6.11(a), packet form: the defect `Δ_E` itself factors through
the packet quotient when `E_g` is `Π`-invariant — the full defect packet is then
computable from packet-level records alone. -/
theorem delta_factors_when_Eg_invariant
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    (hEg : (jointCarrierPD π₁ π₂).InvariantCongruent Eg) :
    ∃ F : (jointCarrierPD π₁ π₂).ResidualQuotient → Int,
      ∀ c : Composed Ω₁ Ω₂,
        F ((jointCarrierPD π₁ π₂).classOf c) = deltaComposed π₁ π₂ e₁ e₂ Eg c :=
  (OmegaCore.PrimitiveDifference.invariantFactor_exists_iff_invariantCongruent
      (jointCarrierPD π₁ π₂) (deltaComposed π₁ π₂ e₁ e₂ Eg)).mpr
    (delta_invariant_of_Eg_invariant π₁ π₂ e₁ e₂ Eg hEg)

/-- **Proposition 11.6.11(b).**  If the global evaluator is non-constant on some
realized `Π`-class, it is not `Π`-invariant (the Lemma 1.5.2 two-trace
non-invariance argument, transported to packet granularity). -/
theorem Eg_not_invariant_of_mixed
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hmix : Eg c ≠ Eg c') :
    ¬ (jointCarrierPD π₁ π₂).InvariantCongruent Eg := by
  have hz : (jointCarrierPD π₁ π₂).ZeroRel c c' := hclass
  exact OmegaCore.PrimitiveDifference.not_invariantCongruent_of_zeroRel_ne
    (jointCarrierPD π₁ π₂) Eg hz hmix

/-- Proposition 11.6.11(b): a mixed `Π`-class blocks `E_g` from factoring through
the packet quotient — every packet-only dashboard loses the global evaluator. -/
theorem Eg_no_factor_through_packet_quotient_of_mixed
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hmix : Eg c ≠ Eg c') :
    ¬ (∃ F : (jointCarrierPD π₁ π₂).ResidualQuotient → Bool,
        ∀ x : Composed Ω₁ Ω₂,
          F ((jointCarrierPD π₁ π₂).classOf x) = Eg x) := by
  have hz : (jointCarrierPD π₁ π₂).ZeroRel c c' := hclass
  exact OmegaCore.PrimitiveDifference.invariantFactor_no_factor_of_zeroRel_ne
    (jointCarrierPD π₁ π₂) Eg hz hmix

/-- The evaluator gluing defect differs across a mixed `Π`-class: since the local
product is class-constant (Prop 11.6.8), `Δ_E` inherits `E_g`'s variation. -/
theorem delta_differs_on_mixed_class
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hmix : Eg c ≠ Eg c') :
    deltaComposed π₁ π₂ e₁ e₂ Eg c ≠ deltaComposed π₁ π₂ e₁ e₂ Eg c' := by
  have hz : (jointCarrierPD π₁ π₂).ZeroRel c c' := hclass
  have hlp : localProductComposed π₁ π₂ e₁ e₂ c
      = localProductComposed π₁ π₂ e₁ e₂ c' :=
    local_product_invariant π₁ π₂ e₁ e₂ c c' hz
  have hb : b2i (Eg c) ≠ b2i (Eg c') := b2i_ne_of_ne hmix
  show b2i (Eg c) - localProductComposed π₁ π₂ e₁ e₂ c
      ≠ b2i (Eg c') - localProductComposed π₁ π₂ e₁ e₂ c'
  rw [hlp]
  intro hEq
  exact hb (by omega)

/-- Proposition 11.6.11(b): a mixed `Π`-class blocks the defect `Δ_E` from
factoring through the packet quotient. -/
theorem delta_no_factor_through_packet_quotient_of_mixed
    {Ω₁ : Type u} {Ω₂ : Type v} {P₁ : Type w} {P₂ : Type z}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hmix : Eg c ≠ Eg c') :
    ¬ (∃ F : (jointCarrierPD π₁ π₂).ResidualQuotient → Int,
        ∀ x : Composed Ω₁ Ω₂,
          F ((jointCarrierPD π₁ π₂).classOf x)
            = deltaComposed π₁ π₂ e₁ e₂ Eg x) := by
  have hz : (jointCarrierPD π₁ π₂).ZeroRel c c' := hclass
  exact OmegaCore.PrimitiveDifference.invariantFactor_no_factor_of_zeroRel_ne
    (jointCarrierPD π₁ π₂) (deltaComposed π₁ π₂ e₁ e₂ Eg) hz
    (delta_differs_on_mixed_class π₁ π₂ e₁ e₂ Eg hclass hmix)

/- ===================================================================== -/
/-  Concrete realizability of §11.6.9 / §11.6.11(b) (anti-vacuity)        -/
/- ===================================================================== -/

/- A carrier-closed network where both stages collapse to a point (`Bool → Unit`),
both local evaluators are constant-green, and the global evaluator depends on the
erased first-stage byte.  Both composed traces share the single `Π`-class, are
locally green, and disagree globally — a locally green mixed class. -/

def demoPi : Bool → Unit := fun _ => ()

def demoLocalGreen : Unit → Bool := fun _ => true

def demoGlobal : Composed Bool Bool → Bool := fun c => c.g1

def demoTraceGreen : Composed Bool Bool := ⟨true, true⟩

def demoTraceRed : Composed Bool Bool := ⟨false, true⟩

theorem demo_same_joint_class :
    jointCarrier demoPi demoPi demoTraceGreen = jointCarrier demoPi demoPi demoTraceRed :=
  rfl

theorem demo_locally_green :
    LocallyGreen demoPi demoPi demoLocalGreen demoLocalGreen demoTraceGreen :=
  ⟨rfl, rfl⟩

theorem demo_mixed :
    demoGlobal demoTraceGreen ≠ demoGlobal demoTraceRed := by decide

/-- Anti-vacuity for Proposition 11.6.9: the hypotheses (a locally green, mixed,
realized `Π`-class) are satisfiable, and the forced `Δ_Eval = -1` trace exists. -/
theorem demo_green_mixed_forces_negative_defect :
    ∃ d : Composed Bool Bool,
      (d = demoTraceGreen ∨ d = demoTraceRed) ∧
      jointCarrier demoPi demoPi d = jointCarrier demoPi demoPi demoTraceGreen ∧
      deltaComposed demoPi demoPi demoLocalGreen demoLocalGreen demoGlobal d = -1 :=
  green_mixed_forces_negative_defect demoPi demoPi demoLocalGreen demoLocalGreen
    demoGlobal demo_same_joint_class demo_locally_green demo_mixed

/-- Anti-vacuity for Proposition 11.6.11(b): the packet quotient loses the global
evaluator on this carrier-closed network. -/
theorem demo_Eg_no_factor_through_packet_quotient :
    ¬ (∃ F : (jointCarrierPD demoPi demoPi).ResidualQuotient → Bool,
        ∀ x : Composed Bool Bool,
          F ((jointCarrierPD demoPi demoPi).classOf x) = demoGlobal x) :=
  Eg_no_factor_through_packet_quotient_of_mixed demoPi demoPi demoGlobal
    demo_same_joint_class demo_mixed

/- ===================================================================== -/
/-  Axiom audit                                                          -/
/- ===================================================================== -/

#print axioms carrier_bounded_iff_invariant
#print axioms verdict_ceiling
#print axioms carrier_cannot_separate_witness
#print axioms local_product_invariant
#print axioms green_mixed_forces_negative_defect
#print axioms sample_green_mixed_forces_ngd
#print axioms green_mixed_strict_pass_gap
#print axioms no_downstream_refinement
#print axioms diagnostic_pair_factors_when_Eg_invariant
#print axioms delta_factors_when_Eg_invariant
#print axioms Eg_no_factor_through_packet_quotient_of_mixed
#print axioms delta_no_factor_through_packet_quotient_of_mixed
#print axioms demo_green_mixed_forces_negative_defect
#print axioms demo_Eg_no_factor_through_packet_quotient

end PaperAE004
