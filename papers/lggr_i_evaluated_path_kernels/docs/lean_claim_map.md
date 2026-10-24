# Lean claim map

Version 1.2.4 — 2026-10-15

The nested Lake project formally mechanizes finite Boolean and integer-weight statements.
It does not formalize the real exponential path weight or a differentiable
activation model. The paper root module is
lean4/lggr_i_evaluated_path_kernels.lean.

Status meanings:

- **MECHANIZED:** the named Lean declaration formally mechanizes the finite paper claim.
- **MECHANIZED-PARTIAL:** Lean formally mechanizes an algebraic or discrete specialization,
  while part of the displayed prose claim remains outside Lean.
- **PROSE:** no Lean theorem is claimed.
- **N/A:** executable or publication fact, not a Lean proposition.

## Root declarations

| Ledger ID | Root declaration | Status | Scope |
|---|---|---|---|
| B1 | B1_local_green_global_red_witness | MECHANIZED | explicit Boolean counterexample |
| B2 | B2_phone_identity; B2b–B2e | MECHANIZED | exact five-trace integer counts |
| B3 | — | PROSE | classical finite modeling scope |
| B4 | — | PROSE | real weighted-kernel definition |
| C1 | C1_kernel_composition_under_G1_G2_G3; C1b; C1c; C1d | MECHANIZED-PARTIAL | finite integer weights and supplied G1 data; no real exponential |
| C2 | C1c_g1_set_isomorphism | MECHANIZED-PARTIAL | G1 is an explicit equivalence between global paths and the dependent disjoint union of compatible pairs; G2–G3 remain supplied hypotheses |
| D1 | D1_delta_trichotomy | MECHANIZED | Boolean defect range |
| D2 | D2_defect_corrected_kernel_identity | MECHANIZED-PARTIAL | integer-weight residual identity |
| D3 | D3_fully_corrected_kernel_identity | MECHANIZED-PARTIAL | abstract additive two-channel expansion |
| D4 | D4_cancellation_not_pointwise_zero | MECHANIZED | finite signed cancellation witness |
| E1 | E1_ngd_pgd_zdr_partition | MECHANIZED | class-count partition |
| E2 | E2_count_gap_eq_delta_sum | MECHANIZED | count identity |
| E3 | E3_local_pass_count_does_not_determine_global | MECHANIZED | explicit indistinguishable local summaries |
| E4 | E4_local_dashboard_does_not_carry_global_or_delta | MECHANIZED | quotient non-factorization |
| E5 | E5_defect_class_semantic_normal_forms | MECHANIZED | Boolean normal forms |
| E6 | E6_egd_zero_iff_all_zdr | MECHANIZED | zero absolute defect iff all ZDR |
| E7 | E7_egd_decomposition | MECHANIZED | EGD and ZDR partition |
| E8 | E8_signed_defect_balance | MECHANIZED | signed count balance |
| E9 | E9_pass_rates_do_not_determine_egd | MECHANIZED | matched-rate counterexample |
| E10 | E10_defect_moment_reconstruction | MECHANIZED | oriented count reconstruction |
| E11 | E11_ngd_bounded_by_local_pass_count | MECHANIZED | exposure bound |
| E12 | E12_diagnostic_dashboard_factors | MECHANIZED | defect packet factors through diagnostic quotient |
| E13 | E13_defect_packet_non_sufficiency | MECHANIZED | packet loses absolute verdicts |
| E14 | E14_defect_packet_plus_local_determines_global | MECHANIZED | one-bit reconstruction; dual in source module |
| E15 | E15_defect_packet_eq_iff_defect_kind_eq | MECHANIZED | kind is packet normal form |
| E16 | E16_bool_dashboard_cannot_be_exact | MECHANIZED | finite three-class argument |
| E17 | E17_carrier_collision_induces_zero_relation | MECHANIZED | carrier collision |
| E18 | E18_global_failure_decomposition | MECHANIZED | failure partition |
| F1 | — | PROSE | empirical hypothesis |
| F2 | activation_derivative_formula; activation_first_order_condition | MECHANIZED-PARTIAL | integer algebraic shadow, not real differentiation |
| F3 | SingleCrossing; sign_positive_before_single_crossing; sign_negative_after_single_crossing | MECHANIZED-PARTIAL | implication from an assumed integer sign pattern |
| F4–F5 | — | PROSE | expert-model algebra and interpretation |
| P1–P4 | — | PROSE | empirical program, implementation, and scope; P1–P4 are distinct from structural hypotheses G1–G4 |
| P5 | P5_proposal_weighted_composition_under_G1_G2_G3_G4 | MECHANIZED-PARTIAL | integer factorization theorem |
| P6 | — | PROSE | related-work positioning |
| H1 | false_red_two_record_counts; cancellation_sample_zero_delta_but_positive_egd | MECHANIZED-PARTIAL | selected finite collapse examples; no adequacy certificate |
| H2a | H2_structural_guard_implies_ngd_strictly_below_global_failure | MECHANIZED | implication from every explicit structural-guard premise |
| H2b | H2b_one_minus_gpr_eq_ngd_add_lrgr | MECHANIZED | global-failure count partition |
| H2c | — | PROSE | vacuous-local specialization, replayed in Python |
| H3–H6 | — | PROSE | publication and modeling boundaries |
| H7 | — | N/A | summary of this map and a current build receipt |
| I1 | I1_verdict_ceiling | MECHANIZED | target mixed on a carrier fiber cannot factor |
| I2 | witness_fabrication_indistinguishable | MECHANIZED | source declaration in 21_carrier_kernel_quotient.lean |
| I3 | I3_local_product_invariant | MECHANIZED | local-product fiber invariance |
| I4 | I4_green_mixed_forces_negative_defect | MECHANIZED | mixed green fiber yields NGD |
| I5 | I5_green_mixed_strict_pass_gap | MECHANIZED | finite two-record gap |
| I6 | I6_no_downstream_refinement | MECHANIZED | equality preserved by post-composition |
| I7a | I7a_diagnostic_pair_factors_when_Eg_invariant | MECHANIZED | the diagnostic pair factors under global-evaluator invariance |
| I7b | I7b_Eg_no_factor_through_packet_quotient_of_mixed | MECHANIZED | the global evaluator alone cannot factor across a mixed fiber |

## Source modules

The root declarations import the supporting modules 01 through 22, including
03b_product_of_sums.lean and 03c_g1_set_isomorphism.lean. Each supporting theorem
is visible through the nested default target. The release check is:

    lake build

The source files contain print-axioms commands for the load-bearing
declarations. A release receipt must record their live output; this map does
not substitute a historical count.
