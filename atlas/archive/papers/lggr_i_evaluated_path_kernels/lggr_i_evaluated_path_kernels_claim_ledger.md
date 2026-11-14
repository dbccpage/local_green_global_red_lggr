# Claim ledger

**Paper:** Local Green, Global Red I: Evaluated Path Kernels for Composed Agent Reliability

**Version:** 1.2.4

**Republication date:** 2026-10-15

This ledger records the strongest supported reading of each substantive
claim. The canonical manuscript is lggr_i_evaluated_path_kernels.md.

## Status vocabulary

- **Definition:** notation or a declared model.
- **Finite theorem:** proved for the stated finite Boolean/integer setting.
- **Conditional theorem:** proved only under the listed hypotheses.
- **Computed fixture:** exact output for explicitly supplied data.
- **Model consequence:** algebra inside an explicitly chosen engineering
  model.
- **Empirical hypothesis:** a falsifiable claim not tested by this package.
- **Positioning:** comparison with prior work; not an equivalence theorem.
- **Scope:** a boundary on interpretation.

Python tests check executable counterparts but are not proofs of claims about
deployed systems. Lean declarations prove only their typed statements.

## Core calculus

| ID | Status | Statement | Evidence and conditions |
|---|---|---|---|
| B1 | Finite theorem by counterexample | Local passes do not imply a global pass. | The tuple \((1,1,0)\) has \(\Delta_E=-1\). Lean root declaration B1_local_green_global_red_witness; Python five-trace tests. |
| B2 | Computed fixture | The five traces have LPR \(3/5\), GPR \(1/5\), mean defect \(-2/5\), and NGD \(2/5\). | Lean declarations B2_phone_identity and B2b–B2e; make_five_trace_phone_test and EPKMetrics.compute. |
| B3 | Scope | Trajectories and weights are finite symbolic records with classical non-negative weights. | Model definition. No wavefunction, complex amplitude, or Born rule is used. |
| B4 | Definition | \(Z_E(b\mid a)=\sum_\gamma E(\gamma)w(\gamma)\). | Manuscript Section 1 and EvaluatedPathKernel. The real exponential instance is prose/Python, not Lean real analysis. |
| C1 | Conditional theorem | Under G1–G3, evaluated path kernels compose over the boundary slice. | Manuscript Theorem 1; Lean root declarations C1_kernel_composition_under_G1_G2_G3, C1b, C1c, and C1d. Lean formally mechanizes finite integer-weight forms. Python `test_kernel_composition_theorem_under_g1_g3`. |
| C2 | Definition | G1 is a bijection between global paths and the dependent disjoint union of all compatible segment pairs; G2 is multiplicative weight; G3 is evaluator factorization. | Manuscript Section 3; Lean G1_BoundarySliceDecomposition and C1c_g1_set_isomorphism; Python BoundarySlice.validate_unique_decomposition, including the empty-global/nonempty-segments countermodel. |
| D1 | Definition plus finite range theorem | \(\Delta_E=E_g-E_1E_2\in\{-1,0,1\}\). | Lean D1_delta_trichotomy; calculate_evaluator_defect. |
| D2 | Conditional theorem | Under G1 and G2, \(Z_E=\sum ZZ+R_E\). | Manuscript Section 4; Lean D2_defect_corrected_kernel_identity; Python action residual tests. |
| D3 | Conditional theorem | With weight defect \(\Delta_w\), the contribution has the four-term expansion in Section 4. | Lean D3_fully_corrected_kernel_identity checks the abstract integer expansion. The displayed real exponential specialization is outside this integer theorem. Python `test_four_term_contribution_expansion`. |
| D4 | Finite theorem | Zero signed residual does not imply pointwise zero defect. | One NGD and one PGD cancel. Lean D4_cancellation_not_pointwise_zero; Python cancellation mutation. |

## Finite diagnostic identities

For this table, all claims concern a finite list of binary verdict triples.
Count identities become rate identities after division by a nonzero sample
size.

| ID | Status | Statement | Lean root declaration |
|---|---|---|---|
| E1 | Definition | LPR, GPR, NGD, PGD, ZDR, EGD, RKE, and nRKE are the statistics defined in Section 2 and the code. | E1_ngd_pgd_zdr_partition formally verifies the class partition. |
| E2 | Finite theorem | Global-pass count minus local-pass count equals the signed defect sum. | E2_count_gap_eq_delta_sum. Python `test_e2_count_gap_equals_signed_defect_sum` calls `EPKMetrics.verify_identities`. |
| E3 | Finite theorem | Local-pass count does not determine global passes, NGD, or signed defect. | E3_local_pass_count_does_not_determine_global. Python `test_e3_same_local_count_different_global`. |
| E4 | Finite theorem | The local-only quotient cannot carry \(E_g\) or \(\Delta_E\). | E4_local_dashboard_does_not_carry_global_or_delta. Python `test_e4_same_local_product_different_global`. |
| E5 | Finite theorem | NGD, PGD, and ZDR have the Boolean normal forms shown in Section 2. | E5_defect_class_semantic_normal_forms. Python `test_e5_defect_kind_matches_boolean_classes`. |
| E6 | Finite theorem | EGD count is zero iff every trace is ZDR. | E6_egd_zero_iff_all_zdr. Python `test_e6_egd_zero_iff_all_zdr`. |
| E7 | Finite theorem | EGD count equals NGD plus PGD and complements ZDR. | E7_egd_decomposition. Python `EPKMetrics.verify_identities`. |
| E8 | Finite theorem | Signed defect equals PGD count minus NGD count. | E8_signed_defect_balance. Python `EPKMetrics.verify_identities`. |
| E9 | Finite theorem | LPR and GPR do not determine EGD or the defect partition. | E9_pass_rates_do_not_determine_egd. Python `test_e9_same_pass_counts_different_partition`. |
| E10 | Finite theorem | EGD and signed defect reconstruct NGD and PGD counts. | E10_defect_moment_reconstruction. Python `EPKMetrics.verify_identities`. |
| E11 | Finite theorem | NGD count is bounded by local-pass count. | E11_ngd_bounded_by_local_pass_count. Python `test_e11_ngd_count_is_bounded_by_local_passes`. |
| E12 | Finite theorem | The diagnostic pair \((L,E_g)\) carries the defect packet. | E12_diagnostic_dashboard_factors. Python `test_e12_same_dashboard_same_defect`. |
| E13 | Finite theorem | The defect packet alone does not determine either absolute verdict. | E13_defect_packet_non_sufficiency. Python `test_e13_same_defect_different_verdicts`. |
| E14 | Finite theorem | The packet plus either absolute verdict determines the other. | E14_defect_packet_plus_local_determines_global and source-file dual theorem. Python `test_e14_defect_plus_local_determines_global`. |
| E15 | Finite theorem | Defect-packet equality is equivalent to defect-kind equality. | E15_defect_packet_eq_iff_defect_kind_eq. Python `test_e15_defect_kind_agrees_with_defect_value`. |
| E16 | Finite theorem | No Boolean key exactly represents the three-class diagnostic quotient. | E16_bool_dashboard_cannot_be_exact. Python `test_e16_one_boolean_key_collides`. |
| E17 | Finite theorem | A carrier collision is a zero-relation in the induced carrier quotient. | E17_carrier_collision_induces_zero_relation. Python `test_e17_carrier_collision_agrees` calls `carrier_verdicts_agree`. |
| E18 | Finite theorem | Global failures partition into NGD and local-red/global-red cases. | E18_global_failure_decomposition. Python `test_e18_h2_failure_partition` calls `EPKMetrics.failure_partition_holds`. |

## Conditional engineering models

| ID | Status | Statement | Evidence and limit |
|---|---|---|---|
| F1 | Empirical hypothesis | Pre-terminal historical defect features may improve held-out global-failure prediction over local-pass features alone. | Section 9 protocol. No benchmark run is included. Same-trace NGD is excluded as a predictor because it contains the terminal verdict. |
| F2 | Model consequence | If \(C,D\) are differentiable, \(S=C(1-D)\) has derivative \(S'=C'(1-D)-CD'\); an interior optimum satisfies \(C'(1-D)=CD'\). | Ordinary product rule in prose. Lean activation_derivative_formula checks an integer algebraic shadow, not differentiation over the reals. Python `test_activation_density_first_order_condition`. |
| F3 | Conditional theorem | A strict positive-to-negative single crossing of \(S'\) yields the stated reversal around the crossing. | Assumes the sign pattern. Lean SingleCrossing declarations check the implication in an integer model. The paper does not derive the sign pattern. Python `test_activation_density_curve`. |
| F4 | Computed fixture | On a nonempty finite candidate set, Product-of-Experts energies add under the declared Gibbs/product form. Normalization requires a strictly positive denominator, equivalently a candidate in every expert's positive support. Under that condition, a zero hard factor forces that candidate's normalized probability to zero. | Checked on the declared finite instances by Python ReliabilityModels.normalized_product_of_experts, including the disjoint-support refusal test. Not a Lean theorem. |
| F5 | Positioning | Product and mixture aggregation expose different false-accept/false-reject pressures. | Engineering interpretation, not a dominance theorem; Jacobs et al. (1991) and Hinton (2002). |

## Experiment and implementation

| ID | Status | Statement | Evidence and limit |
|---|---|---|---|
| P1 | Empirical program | Multi-step agent benchmarks can be instrumented with a declared local/global evaluator split. | Section 9. The cited benchmarks do not supply that split automatically. The P prefix avoids collision with structural hypotheses G1–G4. |
| P2 | Computed fixture | Synthetic tables and plots satisfy the finite identities. | generate_figures.py and Python tests. Not sampled deployment data. |
| P3 | Implementation fact | The reference engine implements states, paths, boundaries, defects, metrics, weights, and observed degeneracy warnings. | code/epk_core.py and code/tests. |
| P4 | Scope | Design implications and falsification criteria do not establish deployment reliability. | Sections 5, 9, and 10. |
| P5 | Conditional theorem | Proposal-weighted kernels compose under G1–G4. | Lean P5_proposal_weighted_composition_under_G1_G2_G3_G4; Python proposal/hybrid tests. |
| P6 | Positioning | Cellular-sheaf gluing is adjacent language, not an identification with this defect. | Hansen and Ghrist (2019). No sheaf or cohomology class is constructed here. |

## Evaluator adequacy and modeling boundary

| ID | Status | Statement | Evidence and limit |
|---|---|---|---|
| H1 | Finite counterexamples | Constant or tautological evaluator configurations can force an uninformative zero defect. | DetectorAdequacyGuard warnings and finite Lean examples. Python `test_r5_guard_detects_constant_degeneracies`. A warning is not a certificate of adequacy. |
| H2a | Conditional finite theorem | Under the declared structural detector guard, NGD count is strictly below global-failure count. | Lean H2_structural_guard_implies_ngd_strictly_below_global_failure. The theorem assumes every field of DetectorStructuralGuard. Python `ngd_below_failure_given_both_witnesses` checks the count gap once both witnesses are present. |
| H2b | Finite theorem | Global failures partition into NGD and local-red/global-red cases. | Lean H2b_one_minus_gpr_eq_ngd_add_lrgr and E18_global_failure_decomposition. Python `failure_partition_holds`. |
| H2c | Finite model consequence | If every local product equals one, local-red/global-red and PGD cannot occur, so NGD = EGD = one minus GPR. | Direct specialization of H2b; Python test_vacuous_local_accepts_collapse_defect_counts. This is not an adequacy certificate. |
| H3 | Scope | This package is a research artifact, not operational authorization. | Publication status; not a mathematical theorem. |
| H4 | Scope | Sample proportions and proposal weights have classical finite semantics. | Sections 1 and 6. |
| H5 | Definition | The model begins with declared finite recorded states and paths. | State and TrajectorySegment; no continuous latent state space is inferred. |
| H6 | Positioning | The residual is a finite gluing mismatch, not a cohomology class. | No cochain complex or topological invariant occurs in the construction. |
| H7 | Mechanization status | Lean covers the finite Boolean and integer-weight claims named in docs/lean_claim_map.md. | A current build and axiom report are release checks. Real exponential weights and differentiable activation are outside Lean scope. |

## Carrier quotient

Let \(\pi:\Omega\to P\) be a finite observation carrier and let
\(\Pi\) be the product carrier for a composed pair.

| ID | Status | Statement | Evidence and conditions |
|---|---|---|---|
| I1 | Conditional finite theorem | A target verdict that varies within a \(\pi\)-fiber cannot factor through \(\pi\). | Lean I1_verdict_ceiling. Python `verdict_ceiling_witness` on the collapsing carrier. |
| I2 | Conditional finite theorem | Two realized traces in the same carrier fiber are indistinguishable to every carrier-bounded evaluator. | carrier_kernel_quotient.lean, witness_fabrication_indistinguishable. Python `carrier_verdicts_agree`. The names “witness” and “fabrication” denote supplied predicates, not an automatic semantic classifier. |
| I3 | Finite theorem | The local product is invariant on joint-carrier fibers. | Lean I3_local_product_invariant. Python `composed_local_product` on the demo pair. |
| I4 | Conditional finite theorem | A locally green fiber with mixed global verdicts contains an NGD trace. | Lean I4_green_mixed_forces_negative_defect. Python `negative_defect_trace`. |
| I5 | Conditional finite theorem | For a locally green mixed pair, global-pass count is strictly below local-pass count. | Lean I5_green_mixed_strict_pass_gap. Python `strict_pass_gap`. |
| I6 | Finite theorem | Post-composition cannot separate two already collided carrier records. | Lean I6_no_downstream_refinement. Python `downstream_verdicts_agree`. |
| I7a | Conditional finite theorem | If \(E_g\) is fiber-invariant, the diagnostic pair \((L,E_g)\) descends to the packet quotient. | Lean I7a_diagnostic_pair_factors_when_Eg_invariant. Python `class_factor` on a constant global verdict. |
| I7b | Conditional finite theorem | If \(E_g\) differs on two members of one packet fiber, \(E_g\) itself cannot factor through the packet quotient. | Lean I7b_Eg_no_factor_through_packet_quotient_of_mixed. Python `class_factor` on the mixed demo. This row does not assert non-factorization of every diagnostic component. |

## Open work

1. Mechanize the displayed real-valued exponential specialization.
2. Mechanize the differentiable activation model rather than its integer
   algebraic shadow.
3. Run the prospective held-out benchmark protocol with independently
   justified, non-constant evaluators.
4. Report uncertainty and evaluator-sensitivity analyses for those empirical
   measurements.

No item in this list is presented as completed by the current package.
