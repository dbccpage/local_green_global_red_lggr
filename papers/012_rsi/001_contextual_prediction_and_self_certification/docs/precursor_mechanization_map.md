# Mechanization map: statement to Lean declaration and Python test

This file maps the statements of section 4 of `epistemic_no_go_monograph.md` to the checks that cover them. It is documentation. It is not a claim ledger and it confers no status: the tag column repeats the monograph's tag. Lean declarations are in `lean4/` under the namespace `EpistemicNoGo`. Python tests are in `code/tests/test_epistemic_kernel.py`. Rust symbols are on the programme repository trunk (commit b8a84409f) and are not in this deposit.

| statement | tag | Rust symbol (trunk) | Lean declaration | Python test |
| --- | --- | --- | --- | --- |
| Result I dichotomy: joint or positive ℓ¹ defect | COMPUTED (ℓ¹ part), PROVED HERE (support part) | `evaluate_epistemic_contextuality`, `verify_l1_defect` | `ResultI.pr_box_no_global_assignment`, `pr_box_no_supported_assignment`, `no_positive_joint_into_pr`, `mass_zero_into_pr`, `classical_joint_is_global_section` (support level only) | `test_tables_are_distributions`, `test_pr_box_has_no_supported_global_assignment`, `test_pr_box_support_is_the_xor_rule_in_every_context`, `test_no_positive_joint_marginalises_to_pr_box`, `test_classical_mixture_has_global_section_with_exact_marginals` |
| Result I refinements and parity cut | COMPUTED | `parity_analysis` | none | none |
| Result I nerve H¹ as a cover invariant | COMPUTED | nerve H¹ routine in `epistemic_observer` | none | none |
| Result I no-signalling check | COMPUTED | no-signalling check in `epistemic_observer` | none | none |
| CHSH values and the classical bound 2 | COMPUTED | fixtures in `epistemic_observer` | none | `test_chsh_values_and_classical_bound`, `test_near_tsirelson_is_not_in_the_classical_polytope_by_chsh`, `test_exact_boundary_value_is_not_glued_by_tolerance` |
| Fiber lemma | PROVED HERE | none | `ResultII.fiber_lemma` | `test_fiber_lemma_exhaustive_on_f2_squared` |
| Corollary II: a private fiber blocks prediction | PROVED HERE | `BoundaryProjection.private_fiber_dim` | `ResultII.private_fiber_blocks_prediction`, `proj_has_private_fiber`, `proj_no_perfect_prediction`, `no_perfect_peer_prediction` | `test_private_fiber_blocks_prediction_of_the_state` |
| Proposition II-open: privacy over time | OPEN | none | witnesses only: `ResultII.hidden_at_zero_is_report_at_one`, `swap_not_intertwined`, `kernel_does_not_give_privacy_over_time` | `test_swap_dynamics_witness` |
| Wolpert's inference-device results | IMPORTED, unused | none | none | none |
| III.a: a receipt carries no authority | DEFINITIONAL (policy invariant by construction) | `ThreeRoleReceipt` | `ResultIV.receipt_carries_no_authority` | `test_distinct_roles_with_admitted_root_pass_with_no_authority` |
| III.b: a ledger cannot establish its own completeness | PROVED HERE and COMPUTED | none | `ResultIII.prefix_verifies`, `truncation_is_invisible`, `pinned_tip_separates`, `tamper_detected`, `internal_verification_is_not_completeness` | `test_truncated_ledger_still_verifies`, `test_pinned_tip_separates_complete_from_truncated`, `test_tampered_payload_is_detected` |
| III.c: Tarski and Löb forms | IMPORTED | none | none | none |
| III.d: relabeling-invariant verdicts are blind | PROVED HERE | none | `ResultIII.invariant_verdict_blind`, `invariant_export_blind`, `noninvariant_verdict_separates` | `test_invariant_verdict_is_blind_and_noninvariant_verdict_separates` |
| Axis 1 of WDP-CH14-T01 | IMPORTED | none | none | none |
| Proposition IV: the three-role gate | PROVED HERE (model) and COMPUTED | `verify_three_role_authority`, `compose_attempts` | `ResultIV.proposer_cannot_authorize`, `evaluator_cannot_authorize`, `prose_standing_refused`, `pass_implies_policy`, `delegated_standing_admitted`, `compose_refused_link`, `distinct_strings_pass` | `test_gate_refusals`, `test_a_refused_link_poisons_the_composition`, `test_distinct_identifiers_naming_one_agent_pass` |
| Substrate indifference | PROVED HERE by inspection of the hypotheses | none | none | none |
| Terminal disjointness | DEFINITIONAL | `Terminal` | none | none |

Rows with "none" in the Lean and Python columns are covered only by the Rust kernel on the trunk, or are not mechanised. Rows tagged IMPORTED are used at their stated scope and not re-proved.

The Lean declarations are statements about finite models. In particular, `ResultIV` is a re-statement of `verify_three_role_authority` with the simplifications listed in the docstring of `lean4/ResultIV.lean`; no check ties it to the Rust source. Its `simp` proofs depend on `Classical.choice`, which is on the programme's axiom whitelist; `lean4/axiom_report.txt` lists the dependency of every declaration.
