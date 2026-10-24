# Claim ledger — Local Green, Global Red III

**Paper:** A finite evaluator overlay across six system roles\
**Date:** 2026-10-15 (evidence-capture baseline: 2026-10-15)\
**Version:** 1.5.2\
**Primary manuscript:** lggr_iii_epk_gtla_overlay.md\
**Evidence boundary:** paper-local Python, notebooks, Lean 4, and build scripts

This ledger records the claims retained by the thin synthesis paper. Earlier
omnibus releases contained many interface-schema claims. Version 1.5.0 removes
those claims from the paper rather than silently treating their Boolean
declaration checks as semantic theorems.

## 1. Claim inventory

| ID | paper location | exact claim | type | evidence |
|---|---|---|---|---|
| LGGR3-C01 | §3.1 | For binary $e_1,e_2,e_g$, define $\Delta_E=e_g-e_1e_2$. | [DEFINITION] | Python EvaluatorVerdictTriple; Lean LGGR3.defect |
| LGGR3-C02 | Proposition 1 | $\Delta_E\in\{-1,0,1\}$. | [PROVEN] | finite case split; Lean LGGR3.defect_range; Python classify_defect in test_classify_defect |
| LGGR3-C03 | Proposition 2 | $(1,1,0)$ is a local-green/global-red witness with defect $-1$. | [PROVEN] | displayed substitution; Python and Lean witnesses |
| LGGR3-C04 | Theorem 1 | On every finite sample, $\sum e_g-\sum e_1e_2=\sum\Delta_E$. | [PROVEN] | finite distributivity; Python audit_sample; Lean LGGR3.global_sub_local_eq_defect_sum |
| LGGR3-C05 | Proposition 3 | Zero aggregate defect need not mean zero pointwise defects. | [PROVEN] | binary triples $(0,1,1)$ and $(1,1,0)$; Lean LGGR3.binary_defect_cancellation; Python AggregateAudit.has_aggregate_cancellation in test_mutation_09_aggregate_cancellation_then_pointwise_recovery |
| LGGR3-C06 | §4.2 | The five archived triples have totals $(G,L,D)=(1,3,-2)$. | [WORKED EXAMPLE] | Python phone_test; Lean LGGR3.phone_totals |
| LGGR3-C07 | Theorem 2 | If the composite integer weights are the flattened products of the boundary weight lists, the composite sum equals the sum over boundaries of left-sum times right-sum, and the residual is zero. | [PROVEN] | Lean LGGR3.factorized_integer_kernel_has_zero_residual; Python integer_kernel_residual_is_zero in test_integer_kernel_reindexes; Python audit_kernel_composition in test_explicit_boundary_bijection_and_unweighted_kernel. Real exponentials remain PL-025-8. |
| LGGR3-C08 | Theorem 3 | If $E$ factors through $X/{\sim}$, it is constant on each equivalence class. | [PROVEN] | quotient equality proof; Lean LGGR3.quotient_evaluator_constant; Python quotient_class_violations in test_actual_quotient_classes_construct_descended_evaluator |
| LGGR3-C09 | Corollary 3.1 | Equivalent carrier elements with different verdicts obstruct evaluator descent. | [PROVEN] | Lean LGGR3.quotient_evaluator_obstruction; Python descend_evaluator in test_actual_mixed_class_blocks_descent |
| LGGR3-C10 | §7 | The six-role overlay is one common defect record with role-specific context fields. | [DEFINITION] | Python data model |
| LGGR3-C11 | Proposition 4 | For $S_w(R)=wR$, changing $w$ can change the score of fixed $R$. | [PROVEN] | witness $(R,w,w')=(1,1,2)$; Lean LGGR3.observer_weights_can_change_a_score; Python observer_score in test_observer_score_and_fixed_observation |
| LGGR3-C12 | Proposition 5 | A map that preserves $(e_1,e_2,e_g)$ preserves $\Delta_E$. | [PROVEN, CONDITIONAL + fixed observation] | substitution; Python fixed_observation_preserves_defect; Lean LGGR3.fixed_observation_preserves_defect |
| LGGR3-C13 | §8 | The paper uses a signed comparison defect, not a claimed $C^0\to C^1\to C^2$ cochain complex. | [SCOPE FENCE] | ordinary-language scope statement in the manuscript |
| LGGR3-C14 | §10 | Constant-output rejection is not a general detector-adequacy certificate. | [OPEN] | PL-025-6 |
| LGGR3-C15 | §11 | Sheaf, contract, weighted-automata, and monadic formalisms are related languages, not identified theories. | [INTERPRETIVE] | cited primary literature |

## 2. Paper-to-Lean boundary

The nested Lake library is LGGR3. Its exported theorem names are stable
republication handles. A MECHANIZED row means Lean checks the displayed finite
statement; it does not upgrade a stronger prose claim.

| claim | exported declaration | status | exact limitation |
|---|---|---|---|
| C01 | LGGR3.defect | MECHANIZED | Lean integer definition only. Python test_all_binary_triples |
| C02 | LGGR3.defect_range | MECHANIZED | assumes each input is 0 or 1. Python test_classify_defect |
| C03 | LGGR3.local_green_global_red | MECHANIZED | finite integer witness only. Python test_all_binary_triples |
| C04 | LGGR3.global_sub_local_eq_defect_sum | MECHANIZED | finite lists of integer triples. Python test_finite_sample_identity_and_empty_sample |
| C05 | LGGR3.binary_defect_cancellation | MECHANIZED | two explicit binary verdict triples with nonzero cancelling defects. Python test_mutation_09_aggregate_cancellation_then_pointwise_recovery |
| C06 | LGGR3.phone_totals | MECHANIZED | fixed five-trace fixture. Python test_phone_test_exact_totals |
| C07 | LGGR3.factorized_integer_kernel_has_zero_residual | MECHANIZED | Lean integer reindexing of factorized weights. Python test_integer_kernel_reindexes. Real exponential kernel remains PL-025-8 |
| C08 | LGGR3.quotient_evaluator_constant | MECHANIZED | general constancy consequence for a descended Boolean evaluator. Python test_actual_quotient_classes_construct_descended_evaluator |
| C09 | LGGR3.quotient_evaluator_obstruction | MECHANIZED | obstruction for any equivalent pair with mixed Boolean verdicts. Python test_actual_mixed_class_blocks_descent |
| C10 | LGGR3.six_roles | MECHANIZED-PARTIAL | length of the declared six-item role list only |
| C11 | LGGR3.observer_weights_can_change_a_score | MECHANIZED | integer weighted score. Python test_observer_score_and_fixed_observation |
| C12 | LGGR3.fixed_observation_preserves_defect | MECHANIZED | fixed input verdicts. Python test_observer_score_and_fixed_observation |
| C14 | — | PROSE / OPEN | no detector-adequacy theorem |

The public file exports only definitions and finite statements used by this
map. The older schema-oriented modules are research history, not current
claim evidence.

## 3. Python binding

| claim | production symbol | decisive tests |
|---|---|---|
| C01--C03 | EvaluatorVerdictTriple; classify_defect | test_all_binary_triples; test_invalid_verdicts_are_rejected |
| C04--C06 | audit_sample; phone_test | test_finite_sample_identity_and_empty_sample; test_phone_test_exact_totals; test_mutation_09_aggregate_cancellation_then_pointwise_recovery |
| C07 | integer_kernel_residual_is_zero; compatible_segment_pairs; boundary_bijection_report; audit_kernel_composition | test_integer_kernel_reindexes; test_explicit_boundary_bijection_and_unweighted_kernel; test_proposal_weighted_kernel_uses_computed_g4; mutation tests 02--08 |
| C08--C09 | quotient_class_violations; descend_evaluator | test_actual_quotient_classes_construct_descended_evaluator; test_actual_mixed_class_blocks_descent; mutation test 10 |
| C10 | RoleOverlay; ROLE_NAMES | test_role_overlay_has_exact_six_roles_and_context |
| C11 | observer_score | test_observer_score_and_fixed_observation |
| C12 | fixed_observation_preserves_defect | test_observer_score_and_fixed_observation; mutation test 12 |
| C14 | require_non_collapsing | test_collapsing_samples_are_rejected; mutation test 11 |

The invasive suite contains twelve paired mutations. Each test first injects
an invalid state or deceptive summary and then exercises the corresponding
recovery path.

## 4. Open obligations

Open obligations are retained even when they do not gate the honesty of the
current finite claims.

| ID | exact obligation | effect on this release |
|---|---|---|
| PL-025-6 | Construct a task-specific evaluator-adequacy result excluding constant evaluators, empty trace sets, trivial boundary slices, and nominally declared fields. | Blocks any claim that a green reading establishes real-system reliability; does not block the finite defect identities. |
| PL-025-7 | Define and justify a probabilistic adapter for expectation notation, conditional proposal laws, and log-space proposal defects. | The thin paper uses finite sums and makes no distributional-rate claim. |
| PL-025-8 | Mechanize the nonnegative-real exponential kernel or prove a transport from the integer theorem to the stated weighted carrier. | The integer reindexing is mechanized. Real weights stay open. |
| PL-025-9 | If role-readiness fields are used in future work, bind them to trace-level semantics. | The current thin implementation does not use declaration fields as theorem evidence. |

## 5. Closed historical obligations

PL-025-1 through PL-025-5 are retained as closed historical rows:

| ID | disposition |
|---|---|
| PL-025-1 | Closed for the declared integer difference $\Delta_P=p_{\rm composed}-p_{\rm product}$; the probabilistic/log-space extension remains PL-025-7. |
| PL-025-2 | Closed only as a type-discipline record; no empirical claim follows. |
| PL-025-3 | Closed as local type separation. |
| PL-025-4 | Closed partially for the fixed six-role count; semantic attachment remains under PL-025-9. |
| PL-025-5 | Closed as a feedback-record field theorem. |

## 6. Release rule

No open row may be rewritten as proved because tests, a PDF build, or a
checksum succeeds. The release is ready only when manuscript, this ledger,
Lean map, code tests, notebook executions, metadata, and final archive hashes
refer to the same bytes.
