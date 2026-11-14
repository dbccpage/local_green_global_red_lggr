import core

/-!
# lggr_i_evaluated_path_kernels

Paper Key: `001_finite_obstruction_calculus/012_local_green_global_red_foundational_series/parts/lggr_i_evaluated_path_kernels`

AuthorityEffect: None.
Anchoring: `sealed-derivation-v1` (`3100c4e`).

This module connects the claim ledger IDs to the verified Lean 4 kernel theorems
implemented in `core_l020_01` through `core_l020_22`.
Every declaration is fully proven and checked without placeholder proofs or custom axioms.
All proofs depend solely on the standard Lean 4 kernel (`propext`, `Classical.choice`, `Quot.sound`).
-/

namespace n_001_finite_obstruction_calculus_012_lggr_i_evaluated_path_kernels

open PaperAE004

/- ===================================================================== -/
/-  Section B: Non-Compositionality and the Five-Trace Phone Test        -/
/- ===================================================================== -/

/-- B1: Canonical counterexample: local validators both pass while composed evaluator fails (§1.2, §1.6). -/
theorem B1_local_green_global_red_witness :
    deltaEval true true false = -1 :=
  local_green_global_red_counterexample

/-- B1b: DeltaEval ternary range: deltaEval in {-1, 0, 1}. -/
theorem B1b_delta_range (e1 e2 eg : Bool) :
    deltaEval e1 e2 eg = -1 ∨ deltaEval e1 e2 eg = 0 ∨ deltaEval e1 e2 eg = 1 :=
  deltaEval_range e1 e2 eg

/-- B2: Five-Trace Phone Test identity: global passes minus local passes equals delta sum (§1.5, §1.6). -/
theorem B2_phone_identity :
    phoneGlobalSum - phoneLocalSum = phoneDeltaSum :=
  phone_identity_global_minus_local

/-- B2b: Five-Trace Phone Test local pass count is 3. -/
theorem B2b_phone_local_passes :
    phoneLocalSum = 3 :=
  phone_local_sum

/-- B2c: Five-Trace Phone Test global pass count is 1. -/
theorem B2c_phone_global_passes :
    phoneGlobalSum = 1 :=
  phone_global_sum

/-- B2d: Five-Trace Phone Test delta sum is -2. -/
theorem B2d_phone_delta_sum :
    phoneDeltaSum = -2 :=
  phone_delta_sum

/-- B2e: Five-Trace Phone Test negative defect count equals 2 (computed from trace values by testing deltaEval == -1). -/
theorem B2e_phone_ngd_count :
    phoneNegativeDefectCount = 2 :=
  phone_negative_defect_count

/- ===================================================================== -/
/-  Section C: Kernel Composition under G1–G3 (§3)                        -/
/- ===================================================================== -/

/-- C1: Int-weight Cartesian product-of-sums bridge over supplied boundary rows,
    assuming pointwise contribution factorization. (Full G1 bijection from an independent
    path corpus and real exponential specialization remain open under PL-020-4). -/
theorem C1_kernel_composition_under_G1_G2_G3
    {Boundary Left Right : Type}
    (rows : List (BoundaryRow Boundary Left Right))
    (wLeft : Left → Int) (wRight : Right → Int)
    (globalEval globalWeight : SegmentPair Boundary Left Right → Int)
    (hContribution :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalContribution globalEval globalWeight p =
          pairProductContribution (Boundary := Boundary) wLeft wRight p) :
    flatKernel (rows.map BoundaryRow.pairs)
        (globalContribution globalEval globalWeight) =
      matrixKernel rows wLeft wRight :=
  kernel_composition_under_G1_G2_G3 rows wLeft wRight globalEval globalWeight hContribution

/-- C1b: Finite boundary pair-sum reindexing under G1–G3 pointwise factorization. -/
theorem C1b_kernel_pair_sum_reindexing_under_G1_G2_G3
    {Boundary Left Right : Type}
    (rows : List (List (SegmentPair Boundary Left Right)))
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (weightLeft : Left → Int) (weightRight : Right → Int)
    (globalEval globalWeight : SegmentPair Boundary Left Right → Int)
    (hEval :
      ∀ p, p ∈ flatten rows → globalEval p = evalRight p.right * evalLeft p.left)
    (hWeight :
      ∀ p, p ∈ flatten rows → globalWeight p = weightRight p.right * weightLeft p.left) :
    flatKernel rows (globalContribution globalEval globalWeight) =
      boundaryKernel rows
        (factoredContribution evalLeft evalRight weightLeft weightRight) :=
  kernel_pair_sum_reindexing_under_G1_G2_G3 rows evalLeft evalRight weightLeft weightRight
    globalEval globalWeight hEval hWeight

/-- C1c: Theorem G1 set-isomorphism: certified type equivalence between full paths and the disjoint union
    of boundary-anchored segment Cartesian products, without pre-decomposed row lists. -/
def C1c_g1_set_isomorphism
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (g1 : G1_BoundarySliceDecomposition State Boundary toState a c Path) :
    Path a c ≃ ((b : Boundary) × (Path (toState b) c × Path a (toState b))) :=
  g1_set_isomorphism g1

/-- C1d: Kernel composition on raw flat paths under G1–G3.
    Evaluates global contribution over raw full paths without pre-decomposed row lists. -/
theorem C1d_raw_kernel_composition_under_G1_G2_G3
    {State Boundary : Type} {toState : Boundary → State} {a c : State} {Path : State → State → Type}
    (concat : ∀ {b : Boundary}, Path (toState b) c → Path a (toState b) → Path a c)
    (boundaries : List Boundary)
    (rights : (b : Boundary) → List (Path (toState b) c))
    (lefts : (b : Boundary) → List (Path a (toState b)))
    (w : Path a c → Int)
    (wLeft : ∀ {b : Boundary}, Path a (toState b) → Int)
    (wRight : ∀ {b : Boundary}, Path (toState b) c → Int)
    (hFact : ∀ (b : Boundary) (r : Path (toState b) c) (l : Path a (toState b)),
      w (concat r l) = wRight r * wLeft l) :
    ((rawFullPaths concat boundaries rights lefts).map w).sum =
      (boundaries.map fun b => ((rights b).map wRight).sum * ((lefts b).map wLeft).sum).sum :=
  raw_kernel_composition_under_G1_G2_G3 concat boundaries rights lefts w wLeft wRight hFact

/- ===================================================================== -/
/-  Section D: Evaluator Gluing Defect and Residual Bookkeeping (§4)     -/
/- ===================================================================== -/

/-- D1: Evaluator defect ternary range trichotomy. -/
theorem D1_delta_trichotomy (e1 e2 eg : Bool) :
    deltaEval e1 e2 eg = -1 ∨ deltaEval e1 e2 eg = 0 ∨ deltaEval e1 e2 eg = 1 :=
  deltaEval_range e1 e2 eg

/-- D2: Defect-corrected kernel identity: composite weighted kernel equals uncorrected product kernel
    plus the evaluator residual sum. -/
theorem D2_defect_corrected_kernel_identity {α : Type}
    (rows : List (List α)) (localEval delta weight : α → Int) :
    weightedKernel rows (fun p => localEval p + delta p) weight =
      weightedKernel rows localEval weight + evaluatorResidual rows delta weight :=
  defect_corrected_kernel_identity rows localEval delta weight

/-- D3: Abstract additive two-channel defect expansion underlying the fully-corrected kernel identity;
    formalizes the algebraic expansion over abstract integer weights (does not construct the
    real exponential Δ_A specialization). -/
theorem D3_fully_corrected_kernel_identity {α : Type}
    (rows : List (List α))
    (localEval deltaEval localWeight deltaWeight : α → Int) :
    flatKernel rows
        (correctedCompositeContribution localEval deltaEval localWeight deltaWeight) =
      flatKernel rows
        (fullyCorrectedExpansion localEval deltaEval localWeight deltaWeight) :=
  fully_corrected_kernel_identity rows localEval deltaEval localWeight deltaWeight

/-- D4: Net zero cancellation does not imply pointwise zero defect. -/
theorem D4_cancellation_not_pointwise_zero :
    cancellationDeltaNeg + cancellationDeltaPos = 0 ∧
    (cancellationDeltaNeg ≠ 0 ∧ cancellationDeltaPos ≠ 0) :=
  ⟨cancellation_net_zero, cancellation_not_pointwise_zero⟩

/- ===================================================================== -/
/-  Section E: Metrics, Dashboards, and Normal Forms (§5)                 -/
/- ===================================================================== -/

/-- D1 / E1: Exhaustive partition of traces into NGD, PGD, ZDR. -/
theorem E1_ngd_pgd_zdr_partition (samples : List EvalTriple) :
    classCount isNGDTriple samples +
      classCount isPGDTriple samples +
      classCount isZDRTriple samples =
    samples.length :=
  defect_class_count_partition samples

/-- E2: Global count minus local count equals delta sum. -/
theorem E2_count_gap_eq_delta_sum (samples : List EvalTriple) :
    (globalPassCount samples : Int) - (localPassCount samples : Int) = deltaSum samples :=
  global_minus_local_count_eq_delta_sum samples

/-- E3: Local pass count alone does not determine GPR, NGD count, or delta sum. -/
theorem E3_local_pass_count_does_not_determine_global :
    localPassCount singletonAllGreen = localPassCount singletonLocalGreenGlobalRed ∧
    singletonAllGreen.length = singletonLocalGreenGlobalRed.length ∧
    globalPassCount singletonAllGreen ≠ globalPassCount singletonLocalGreenGlobalRed ∧
    classCount isNGDTriple singletonAllGreen ≠ classCount isNGDTriple singletonLocalGreenGlobalRed ∧
    deltaSum singletonAllGreen ≠ deltaSum singletonLocalGreenGlobalRed :=
  same_local_pass_count_different_global_ngd_and_delta

/-- E4: Local-dashboard primitive-difference quotient does not carry Eg or Delta_E. -/
theorem E4_local_dashboard_does_not_carry_global_or_delta :
    localDashboardPrimitiveDifference.ZeroRel allGreenTriple lggrTriple ∧
    (¬ OmegaCore.PrimitiveDifference.InvariantCongruent
        localDashboardPrimitiveDifference isGlobalGreenTriple) ∧
    (¬ OmegaCore.PrimitiveDifference.InvariantCongruent
        localDashboardPrimitiveDifference tripleEvaluatorDefect) :=
  ⟨local_dashboard_zero_identifies_all_green_and_lggr,
   global_classifier_not_invariant_on_local_dashboard_zero,
   evaluator_defect_not_invariant_on_local_dashboard_zero⟩

/-- E5: Defect classes have Boolean semantic normal forms. -/
theorem E5_defect_class_semantic_normal_forms (e1 e2 eg : Bool) :
    (isNGD e1 e2 eg = true ↔ localProduct e1 e2 = 1 ∧ b2i eg = 0) ∧
    (isPGD e1 e2 eg = true ↔ localProduct e1 e2 = 0 ∧ b2i eg = 1) ∧
    (isZDR e1 e2 eg = true ↔ b2i eg = localProduct e1 e2) :=
  defect_class_semantic_normal_forms e1 e2 eg

/-- E6: EGD count is zero iff every sampled trace is ZDR. -/
theorem E6_egd_zero_iff_all_zdr (samples : List EvalTriple) :
    egdCount samples = 0 ↔ allZDR samples :=
  egd_count_zero_iff_all_zdr samples

/-- E7: EGD decomposes as NGD + PGD and complements ZDR. -/
theorem E7_egd_decomposition (samples : List EvalTriple) :
    egdCount samples = classCount isNGDTriple samples + classCount isPGDTriple samples ∧
    egdCount samples + classCount isZDRTriple samples = samples.length :=
  ⟨egd_count_eq_ngd_plus_pgd samples, egd_zdr_count_partition samples⟩

/-- E8: Signed defect balance: delta_sum = PGD_count - NGD_count. -/
theorem E8_signed_defect_balance (samples : List EvalTriple) :
    deltaSum samples = (classCount isPGDTriple samples : Int) - (classCount isNGDTriple samples : Int) :=
  delta_sum_eq_pgd_count_minus_ngd_count samples

/-- E9: LPR and GPR do not determine EGD or the defect partition. -/
theorem E9_pass_rates_do_not_determine_egd :
    rateMatchedCleanSamples.length = rateMatchedCancellingSamples.length ∧
    localPassCount rateMatchedCleanSamples = localPassCount rateMatchedCancellingSamples ∧
    globalPassCount rateMatchedCleanSamples = globalPassCount rateMatchedCancellingSamples ∧
    deltaSum rateMatchedCleanSamples = deltaSum rateMatchedCancellingSamples ∧
    egdCount rateMatchedCleanSamples ≠ egdCount rateMatchedCancellingSamples ∧
    classCount isNGDTriple rateMatchedCleanSamples ≠ classCount isNGDTriple rateMatchedCancellingSamples ∧
    classCount isPGDTriple rateMatchedCleanSamples ≠ classCount isPGDTriple rateMatchedCancellingSamples ∧
    classCount isZDRTriple rateMatchedCleanSamples ≠ classCount isZDRTriple rateMatchedCancellingSamples :=
  same_lpr_gpr_and_delta_sum_different_egd

/-- E10: EGD count and delta sum reconstruct NGD and PGD counts. -/
theorem E10_defect_moment_reconstruction (samples : List EvalTriple) :
    (classCount isEGDTriple samples : Int) + deltaSum samples = 2 * (classCount isPGDTriple samples : Int) ∧
    (classCount isEGDTriple samples : Int) - deltaSum samples = 2 * (classCount isNGDTriple samples : Int) :=
  ⟨egd_plus_delta_eq_twice_pgd_count samples, egd_minus_delta_eq_twice_ngd_count samples⟩

/-- E11: NGD count is bounded by local pass count. -/
theorem E11_ngd_bounded_by_local_pass_count (samples : List EvalTriple) :
    classCount isNGDTriple samples ≤ localPassCount samples :=
  ngd_count_le_local_pass_count samples

/-- E12: Diagnostic dashboard carries the full defect packet. -/
theorem E12_diagnostic_dashboard_factors :
    ∃ F : diagnosticDashboardPrimitiveDifference.ResidualQuotient → DefectPacket,
      ∀ t : EvalTriple, F (diagnosticDashboardPrimitiveDifference.classOf t) = defectPacket t :=
  defect_packet_factors_through_diagnostic_dashboard_quotient

/-- E13: Defect packet alone does not determine local or global verdicts. -/
theorem E13_defect_packet_non_sufficiency :
    defectPacket allGreenTriple = defectPacket localRedGlobalRedTriple ∧
    isLocalGreenTriple allGreenTriple ≠ isLocalGreenTriple localRedGlobalRedTriple ∧
    isGlobalGreenTriple allGreenTriple ≠ isGlobalGreenTriple localRedGlobalRedTriple :=
  same_defect_packet_can_have_different_local_and_global_verdicts

/-- E14: Defect packet plus local verdict determines global verdict. -/
theorem E14_defect_packet_plus_local_determines_global {x y : EvalTriple}
    (hPacket : defectPacket x = defectPacket y)
    (hLocal : isLocalGreenTriple x = isLocalGreenTriple y) :
    isGlobalGreenTriple x = isGlobalGreenTriple y :=
  defect_packet_plus_local_determines_global hPacket hLocal

/-- E15: Defect packet equality is equivalent to canonical defect kind equality. -/
theorem E15_defect_packet_eq_iff_defect_kind_eq (x y : EvalTriple) :
    defectPacket x = defectPacket y ↔ defectKind x = defectKind y :=
  defect_packet_eq_iff_defect_kind_eq x y

/-- E16: No single Bool-valued dashboard key is exact for the diagnostic quotient. -/
theorem E16_bool_dashboard_cannot_be_exact :
    ¬ ∃ key : EvalTriple → Bool,
      ∀ x y : EvalTriple, key x = key y ↔ diagnosticDashboardPrimitiveDifference.ZeroRel x y :=
  bool_dashboard_cannot_be_exact_diagnostic_dashboard

/-- E17: Carrier collision induces a zero-relation in the carrier-kernel quotient. -/
theorem E17_carrier_collision_induces_zero_relation {Ω P : Type} (π : Ω → P) (x y : Ω) (hFiber : π x = π y) :
    (carrierKernelPD π).ZeroRel x y :=
  (carrierKernelPD_zeroRel π x y).mpr hFiber

/-- E17_carrier_cannot_separate_witness: Backward-compatible alias for E17_carrier_collision_induces_zero_relation.
    (Note: the separate verdict impossibility theorem is mechanized in I1 / verdict_ceiling). -/
theorem E17_carrier_cannot_separate_witness {Ω P : Type} (π : Ω → P) (x y : Ω) (hFiber : π x = π y) :
    (carrierKernelPD π).ZeroRel x y :=
  E17_carrier_collision_induces_zero_relation π x y hFiber

/-- E18: Global failure decomposes into NGD plus local-red/global-red (LRGR). -/
theorem E18_global_failure_decomposition (samples : List EvalTriple) :
    globalFailureCount samples =
      classCount isNGDTriple samples + lrgrCount samples :=
  global_failure_count_eq_ngd_add_lrgr samples

/- ===================================================================== -/
/-  Section G: POCv2 Proposal-Weighted Composition (§11)                 -/
/- ===================================================================== -/

/-- P5: Proposal-weighted composition bridge over supplied Cartesian boundary rows,
    assuming separate evaluator, proposal, and action-weight factorizations over integer weights. -/
theorem P5_proposal_weighted_composition_under_G1_G2_G3_G4
    {Boundary Left Right : Type}
    (rows : List (BoundaryRow Boundary Left Right))
    (evalLeft : Left → Int) (evalRight : Right → Int)
    (proposalLeft actionLeft : Left → Int)
    (proposalRight actionRight : Right → Int)
    (globalEval globalProposal globalAction :
      SegmentPair Boundary Left Right → Int)
    (hEval :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalEval p = evalRight p.right * evalLeft p.left)
    (hProposal :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalProposal p = proposalRight p.right * proposalLeft p.left)
    (hAction :
      ∀ p, p ∈ flatten (rows.map BoundaryRow.pairs) →
        globalAction p = actionRight p.right * actionLeft p.left) :
    flatKernel (rows.map BoundaryRow.pairs)
        (proposalWeightedContribution globalEval globalProposal globalAction) =
      matrixKernel rows
        (fun left => evalLeft left *
          proposalActionWeight proposalLeft actionLeft left)
        (fun right => evalRight right *
          proposalActionWeight proposalRight actionRight right) :=
  proposal_weighted_composition_under_G1_G2_G3_G4 rows
    evalLeft evalRight proposalLeft actionLeft proposalRight actionRight
    globalEval globalProposal globalAction hEval hProposal hAction

/- ===================================================================== -/
/-  Section H: Detector Adequacy & Non-Vacuous Guard Theorems (§12)       -/
/- ===================================================================== -/

/-- H2: Structural guard implies NGD is strictly below global failure count. -/
theorem H2_structural_guard_implies_ngd_strictly_below_global_failure
    {samples : List EvalTriple}
    {claims : DetectorStructuralClaims}
    (guard : DetectorStructuralGuard samples claims) :
    classCount isNGDTriple samples < globalFailureCount samples :=
  structural_guard_implies_ngd_strictly_below_global_failure guard

/-- H2b: Global failure count equals NGD count plus LRGR count (finite complement identity). -/
theorem H2b_one_minus_gpr_eq_ngd_add_lrgr (samples : List EvalTriple) :
    samples.length - globalPassCount samples =
      classCount isNGDTriple samples + lrgrCount samples :=
  one_minus_gpr_eq_ngd_add_lrgr samples

/- ===================================================================== -/
/-  Section I: Bounded Observer Carriers and Epistemic Ceiling (OB-2)    -/
/- ===================================================================== -/

/-- I1: Finite verdict ceiling: an evaluator non-constant on a carrier-kernel fiber cannot factor. -/
theorem I1_verdict_ceiling {Ω P : Type} (π : Ω → P) (e : P → Bool) (T : Ω → Bool)
    {γ γ' : Ω} (hpi : π γ = π γ') (hT : T γ ≠ T γ') :
    ∃ ω : Ω, inducedEvaluator π e ω ≠ T ω :=
  verdict_ceiling π e T hpi hT

/-- I3: Local product is invariant on joint carrier fibers. -/
theorem I3_local_product_invariant {Ω₁ Ω₂ P₁ P₂ : Type}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool) :
    (jointCarrierPD π₁ π₂).InvariantCongruent
      (localProductComposed π₁ π₂ e₁ e₂) :=
  local_product_invariant π₁ π₂ e₁ e₂

/-- I4: Kernel-mixing forces the local-green/global-red discrepancy (Delta_Eval = -1 witness). -/
theorem I4_green_mixed_forces_negative_defect
    {Ω₁ Ω₂ P₁ P₂ : Type}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hgreen : LocallyGreen π₁ π₂ e₁ e₂ c)
    (hmix : Eg c ≠ Eg c') :
    ∃ d : Composed Ω₁ Ω₂,
      (d = c ∨ d = c') ∧
      jointCarrier π₁ π₂ d = jointCarrier π₁ π₂ c ∧
      deltaComposed π₁ π₂ e₁ e₂ Eg d = -1 :=
  green_mixed_forces_negative_defect π₁ π₂ e₁ e₂ Eg hclass hgreen hmix

/-- I5: Finite hidden-failure gap: among a green mixed pair, global pass count is strictly below local pass count. -/
theorem I5_green_mixed_strict_pass_gap
    {Ω₁ Ω₂ P₁ P₂ : Type}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hgreen : LocallyGreen π₁ π₂ e₁ e₂ c)
    (hmix : Eg c ≠ Eg c') :
    b2i (Eg c) + b2i (Eg c')
      < localProductComposed π₁ π₂ e₁ e₂ c + localProductComposed π₁ π₂ e₁ e₂ c' :=
  green_mixed_strict_pass_gap π₁ π₂ e₁ e₂ Eg hclass hgreen hmix

/-- I6: No downstream refinement: post-composition cannot separate a carrier collision. -/
theorem I6_no_downstream_refinement {Ω P R : Type}
    (π : Ω → P) (chain : P → R) {γ γ' : Ω} (h : π γ = π γ') :
    chain (π γ) = chain (π γ') :=
  no_downstream_refinement π chain h

/-- I7a: Diagnostic pair factors through the packet quotient when Eg is Pi-invariant. -/
theorem I7a_diagnostic_pair_factors_when_Eg_invariant
    {Ω₁ Ω₂ P₁ P₂ : Type}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (e₁ : P₁ → Bool) (e₂ : P₂ → Bool)
    (Eg : Composed Ω₁ Ω₂ → Bool)
    (hEg : (jointCarrierPD π₁ π₂).InvariantCongruent Eg) :
    ∃ F : (jointCarrierPD π₁ π₂).ResidualQuotient → Int × Bool,
      ∀ c : Composed Ω₁ Ω₂,
        F ((jointCarrierPD π₁ π₂).classOf c)
          = (localProductComposed π₁ π₂ e₁ e₂ c, Eg c) :=
  diagnostic_pair_factors_when_Eg_invariant π₁ π₂ e₁ e₂ Eg hEg

/-- I7b: Packet quotient loses the global evaluator when Eg is mixed across a carrier class. -/
theorem I7b_Eg_no_factor_through_packet_quotient_of_mixed
    {Ω₁ Ω₂ P₁ P₂ : Type}
    (π₁ : Ω₁ → P₁) (π₂ : Ω₂ → P₂) (Eg : Composed Ω₁ Ω₂ → Bool)
    {c c' : Composed Ω₁ Ω₂}
    (hclass : jointCarrier π₁ π₂ c = jointCarrier π₁ π₂ c')
    (hmix : Eg c ≠ Eg c') :
    ¬ (∃ F : (jointCarrierPD π₁ π₂).ResidualQuotient → Bool,
        ∀ x : Composed Ω₁ Ω₂,
          F ((jointCarrierPD π₁ π₂).classOf x) = Eg x) :=
  Eg_no_factor_through_packet_quotient_of_mixed π₁ π₂ Eg hclass hmix

/- ===================================================================== -/
/-  Axiom Audits for All Public Ledger Theorems                          -/
/- ===================================================================== -/

#print axioms B1_local_green_global_red_witness
#print axioms B1b_delta_range
#print axioms B2_phone_identity
#print axioms B2b_phone_local_passes
#print axioms B2c_phone_global_passes
#print axioms B2d_phone_delta_sum
#print axioms B2e_phone_ngd_count
#print axioms C1_kernel_composition_under_G1_G2_G3
#print axioms C1b_kernel_pair_sum_reindexing_under_G1_G2_G3
#print axioms C1c_g1_set_isomorphism
#print axioms C1d_raw_kernel_composition_under_G1_G2_G3
#print axioms D1_delta_trichotomy
#print axioms D2_defect_corrected_kernel_identity
#print axioms D3_fully_corrected_kernel_identity
#print axioms D4_cancellation_not_pointwise_zero
#print axioms E1_ngd_pgd_zdr_partition
#print axioms E2_count_gap_eq_delta_sum
#print axioms E3_local_pass_count_does_not_determine_global
#print axioms E4_local_dashboard_does_not_carry_global_or_delta
#print axioms E5_defect_class_semantic_normal_forms
#print axioms E6_egd_zero_iff_all_zdr
#print axioms E7_egd_decomposition
#print axioms E8_signed_defect_balance
#print axioms E9_pass_rates_do_not_determine_egd
#print axioms E10_defect_moment_reconstruction
#print axioms E11_ngd_bounded_by_local_pass_count
#print axioms E12_diagnostic_dashboard_factors
#print axioms E13_defect_packet_non_sufficiency
#print axioms E14_defect_packet_plus_local_determines_global
#print axioms E15_defect_packet_eq_iff_defect_kind_eq
#print axioms E16_bool_dashboard_cannot_be_exact
#print axioms E17_carrier_collision_induces_zero_relation
#print axioms E17_carrier_cannot_separate_witness
#print axioms E18_global_failure_decomposition
#print axioms P5_proposal_weighted_composition_under_G1_G2_G3_G4
#print axioms H2_structural_guard_implies_ngd_strictly_below_global_failure
#print axioms H2b_one_minus_gpr_eq_ngd_add_lrgr
#print axioms I1_verdict_ceiling
#print axioms I3_local_product_invariant
#print axioms I4_green_mixed_forces_negative_defect
#print axioms I5_green_mixed_strict_pass_gap
#print axioms I6_no_downstream_refinement
#print axioms I7a_diagnostic_pair_factors_when_Eg_invariant
#print axioms I7b_Eg_no_factor_through_packet_quotient_of_mixed

end n_001_finite_obstruction_calculus_012_lggr_i_evaluated_path_kernels
