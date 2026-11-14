# Atlas claim ledger

**AuthorityEffect: None.**

First pass, 2026-11-14. Claims derived from `examples/`, `cookbooks/`, `code/`, `lean4/` and `workflows/`. The machine-readable copy, with dependency edges, is [`dag/derivations/derivation_dag.json`](../dag/derivations/derivation_dag.json); `cargo test` in `code/rust` checks that the two agree and that every cited Lean theorem and Rust test exists. Statuses are defined in [`atlas.md`](atlas.md). Claims from `atlas/archive/papers/` are the next phase.

| Status | Count |
|---|---|
| `EMPIRICAL` | 7 |
| `OPEN` | 5 |
| `PROVED_LEAN` | 148 |
| `TESTED_RUST` | 10 |

## Descent: decoders, collisions, evaluator defect

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C01 | **A collision refutes every decoder.** If p(x) = p(y) and q(x) != q(y), no map D with D(p(z)) = q(z) for all z exists. | `PROVED_LEAN` | general | Lean `collision_blocks_factorization`; Rust `c01_collision_refutes_every_decoder` | - |
| LGGR-C02 | **Decoder-or-collision dichotomy on a finite table.** On a supplied finite table, exactly one holds: q is constant on every realized fiber of p (and the fiberwise decoder replays on every row), or an explicit colliding pair exists. _Note: The decoder direction is proved in Lean only as the classical pair-level alternative in WorldLGGRWitness (uses Classical.choice, no executable search). The general finite-table dichotomy is checked by exhaustive Rust census, not proved for all finite carriers._ | `TESTED_RUST` | finite tables; exhaustive census of all 216 maps p:{3}->{3}, q:{3}->{2} | Lean `exactPairFactorOrLGGRWitness`; Rust `c02_decoder_or_collision_exhaustive_census` | LGGR-C01, LGGR-L-PrimitiveDifference |
| LGGR-C03 | **Postprocessing preserves collisions.** For any deterministic f : A -> A', a collision of (p, q) is a collision of (f o p, q); postprocessing cannot restore a decoder. | `PROVED_LEAN` | general | Lean `postprocessing_preserves_collision`; Lean `postprocessing_preserves_streaming_collision`; Rust `c03_postprocessing_preserves_collision` | LGGR-C01 |
| LGGR-C04 | **Verdict ceiling on a colliding pair.** Any report-only evaluator E : A -> B disagrees with q on at least one member of a colliding pair. | `PROVED_LEAN` | general | Lean `verdict_ceiling_on_collision`; Lean `streaming_verdict_ceiling`; Lean `single_colliding_pair_error_lower_bound`; Rust `c04_verdict_ceiling_on_collision` | LGGR-C01 |
| LGGR-C05 | **Boolean evaluator defect partition.** Delta_E = E_g - E_1 E_2 takes values in {-1, 0, 1}, and Delta_E = -1 (NGD, local green / global red) exactly at (E_1, E_2, E_g) = (1, 1, 0). | `PROVED_LEAN` | general (all 8 Boolean triples) | Lean `evalDefect_partition`; Lean `streaming_evalDefect_partition`; Rust `c05_evaluator_defect_partition` | - |
| LGGR-C31 | **Metadata refinement removes a collision.** If x, y collide under p and a feature m has m(x) != m(y), then x, y do not collide under z -> (p(z), m(z)). | `PROVED_LEAN` | general | Lean `minimal_metadata_refinement_eliminates_collision`; Rust `c31_metadata_refinement_eliminates_collision`; Rust `c09_report_examples_collision_and_refinement` | LGGR-C01 |
| LGGR-C11 | **Online collision monotonicity.** A report-fiber collision present in a trace persists in every extension of the trace; an online monitor's collision verdict never retracts. | `PROVED_LEAN` | general | Lean `collision_monotonicity`; Rust `c11_online_collision_monotonicity`; Rust `cookbook01_online_fiber_collision` | LGGR-C01 |
| LGGR-C29 | **Boundary-sufficient gluing gives zero defect (composable LGGG).** If the boundary summaries are sufficient (E_g = E_1 and E_2) and every local stage passes, the global check passes and Delta_E = 0. | `PROVED_LEAN` | general | Lean `boundary_sufficient_gluing_certifies_lggg`; Rust `c29_boundary_sufficient_gluing_zero_defect`; Rust `cookbook04_boundary_sufficient_lggg` | LGGR-C05 |
| LGGR-C30 | **Boundary insufficiency forces NGD.** If two locally passing traces share a report but disagree on the global oracle, at least one branch has Delta_E = -1. | `PROVED_LEAN` | general | Lean `boundary_insufficiency_forces_defect`; Rust `c30_boundary_insufficiency_forces_ngd` | LGGR-C04, LGGR-C05 |

## Histories and witness composition

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C06 | **Signed increments telescope.** For any history x_0, ..., x_n, the sum of signed steps equals x_n - x_0. | `PROVED_LEAN` | general (Lean: streaming_chain_telescoping over lists) | Lean `two_step_telescope`; Lean `three_step_telescope`; Lean `streaming_chain_telescoping`; Rust `c06_telescoping_all_short_histories` | - |
| LGGR-C07 | **Local step bounds do not imply the endpoint bound.** With B = 1, the history (0, 1, 2) has every \|dx_i\| <= 1 but \|x_2 - x_0\| = 2 > 1. | `PROVED_LEAN` | instance (0,1,2), B = 1 | Lean `local_steps_do_not_imply_endpoint_bound`; Rust `c07_local_steps_do_not_imply_endpoint_bound` | LGGR-C06 |
| LGGR-C08 | **Every-prefix boundedness is strictly stronger than endpoint boundedness.** Every-prefix boundedness implies endpoint boundedness; (0, 1, 2, 1) with B = 1 is endpoint-bounded but not prefix-bounded. | `PROVED_LEAN` | implication general; separation on the instance (0,1,2,1) | Lean `every_prefix_strictly_stronger_than_endpoint`; Lean `prefix_implies_endpoint`; Lean `online_prefix_strictly_stronger_than_endpoint`; Rust `c08_every_prefix_strictly_stronger_than_endpoint` | LGGR-C06 |
| LGGR-C09 | **Unsigned step reports collide; signed reports separate.** (0, 1, 0) and (0, 1, 2) have the same unsigned step report (1, 1) but different endpoint verdicts; the signed report separates them. | `PROVED_LEAN` | instance | Lean `unsigned_report_collision_good_vs_bad`; Lean `streaming_unsigned_report_collision`; Rust `c09_unsigned_reports_collide_signed_reports_separate`; Rust `c09_report_examples_collision_and_refinement` | LGGR-C01, LGGR-C07 |
| LGGR-C10 | **Prefix violations latch (online early stopping is sound).** Once a prefix exceeds the bound, no extension restores prefix admissibility, so stopping at the first excursion loses nothing. | `PROVED_LEAN` | general | Lean `prefix_violation_monotonicity`; Rust `c10_prefix_violation_latches`; Rust `cookbook02_prefix_excursion_alert` | LGGR-C08 |
| LGGR-C12 | **The audit keeps five outcomes separate.** On the example histories the audit returns COMPOSITION_VERIFIED (good), OBSTRUCTION_DETECTED (bad: signed total 2 > 1), WITNESS_INCOMPLETE (reports only: missing endpoints), WITNESS_INCOMPLETE (open obligation retained) and AUTHORITY_REQUIRED (changed authority id). _Note: A replay of the finite budget model on supplied data; not runtime or merge authorization._ | `TESTED_RUST` | the five supplied example documents | Rust `c12_history_examples_audit_outcomes` | LGGR-C06, LGGR-C07 |
| LGGR-C13 | **Recorded policy digests replay.** Every witness's policy_sha256 equals SHA-256 of the canonical JSON of the example policy. _Note: A digest binds data; it does not establish truth or grant authority._ | `TESTED_RUST` | the five supplied example documents | Rust `c13_policy_digest_replays` | - |

## Linear repair and 1-cochains

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C14 | **Weighted-l1 weak duality certificate.** If D^T z = 0 and \|z_e\| <= w_e, then z.h <= sum_e w_e \|h_e - (Dx)_e\| for every x; equality certifies the optimum, and z.h > 0 certifies that h is not repairable. _Note: Weak duality holds in general (one-line triangle inequality); no general Lean theorem in this repository yet._ | `TESTED_RUST` | checked on the triangle over a grid of potentials; general statement is prose | Rust `c14_l1_weak_duality_on_triangle` | - |
| LGGR-C15 | **Triangle l1 primal/dual optimality.** For D_0 the triangle coboundary and h = (1, 1, 1), z = (1, 1, -1) and x = (0, 1, 2) certify min_x \|\|h - D_0 x\|\|_1 = 1. | `PROVED_LEAN` | instance | Lean `triangle_l1_primal_dual_optimality`; Rust `c15_triangle_l1_optimality_example` | LGGR-C14 |
| LGGR-C16 | **Filled triangle: closure failure vs budget exactness.** D_1 D_0 = 0; D_1 (1, 1, 1) = 1 != 0 (closure failure); (1, 1, 2) = D_0 (0, 1, 2) is exact. | `PROVED_LEAN` | instance | Lean `filled_triangle_closure_vs_budget_exactness`; Rust `c16_filled_triangle_closure_vs_exactness_examples`; Rust `c16_triangle_budget_differences_exact` | - |
| LGGR-C17 | **Cycle closure: nonzero circulation is an obstruction, certified by a cycle-flow dual.** When a streamed edge closes a cycle with defect d = h_e - (x_v - x_u) != 0, the cochain is not exact; on the unfilled triangle (1, 1, 1) is closed but not exact (nonzero H^1). For one fundamental cycle the weighted-l1 repair distance is \|d\| times the minimum weight on the cycle. _Note: The weighted min-weight formula is checked in Rust on instances; Lean covers the unit-weight residual bound._ | `PROVED_LEAN` | Lean: integer circulation instance (residual >= 1) and the 4-vertex complex; Rust: monitor instances incl. cookbook 03 (defect 3, distance 3) | Lean `incremental_cycle_closure_obstruction`; Lean `streaming_closed_nonexact_cohomology`; Rust `c17_incremental_cycle_closure_certificate`; Rust `c17_unfilled_triangle_nonzero_h1_example` | LGGR-C14 |
| LGGR-C18 | **Open chains are exact.** A streamed acyclic (tree) family of 1-cochains has zero circulation and is a coboundary. | `PROVED_LEAN` | Lean: two-edge chain; Rust: tree instance | Lean `open_chain_exactness`; Rust `c18_open_chain_exactness` | - |

## Transport

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C19 | **A chain retraction reflects repair and obstruction.** If F commutes with the coboundaries and G is a left-inverse chain map (G_1 D_T = D_S G_0, G F = I), target repairs pull back and source nonrepairability is reflected. | `PROVED_LEAN` | general | Lean `retraction_reflects_repair_and_obstruction`; Rust `c19_transport_examples` | LGGR-C16 |
| LGGR-C20 | **A lossy projection cannot reflect nonrepairability.** A non-injective projection admits no left inverse; dropping the chord sends the exact (1,1,2) and the frustrated (1,1,1) to the same repairable image (1,1). | `PROVED_LEAN` | general (non-injectivity) plus the chord-drop instance | Lean `non_injective_projection_blocks_retraction`; Lean `streaming_transport_projection_vs_retraction`; Rust `c20_non_injective_projection_blocks_retraction`; Rust `c19_transport_examples` | LGGR-C19, LGGR-C16 |

## Observer-fiber floor

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C21 | **Two-point fiber minimax floor.** On a fiber with target values a <= b, every integer prediction z has 2 max(\|a - z\|, \|b - z\|) >= b - a, with equality at the midpoint. | `PROVED_LEAN` | two-point fibers, integers | Lean `observer_fiber_two_point_minimax`; Lean `streaming_observer_fiber_minimax_monotonicity`; Rust `c21_two_point_fiber_minimax` | LGGR-C04 |
| LGGR-C22 | **General fiber minimax floor on a finite table.** For O : H -> Y and f : H -> Z, inf_g max_h \|f(h) - g(O(h))\| = (1/2) max_y W_f(y), attained by the fiber midpoint. _Note: General multi-point statement is not yet in Lean._ | `TESTED_RUST` | exhaustive over all 3-history tables with binary observations and targets in {-2..2} | Rust `c22_general_fiber_minimax_floor` | LGGR-C21 |
| LGGR-C23 | **Evidence-preserving recursion keeps the floor.** Any finite chain of self-updates that sees only the fixed evidence y = O(h) yields one output per fiber, so its worst-case error stays >= W_f(y)/2. _Note: Deterministic updates only in the Rust check; the randomized statement in the README is prose._ | `PROVED_LEAN` | Lean: two update operators on a colliding pair; Rust: composed update instances | Lean `evidence_preserving_rsi_invariance_bound`; Rust `c23_evidence_preserving_recursion_keeps_floor` | LGGR-C21, LGGR-C03 |

## Contextuality and Bell

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C24 | **CHSH local bound and PR-box violation.** Every deterministic local strategy has \|S\| = 2, so every local behaviour has \|S\| <= 2; the PR box has S = 4. | `PROVED_LEAN` | general for the 16 deterministic vertices | Lean `chsh_local_polytope_bound_and_negative_mass`; Rust `c24_chsh_local_bound_and_pr_box` | - |
| LGGR-C25 | **Pairwise-compatible odd cycle has no global section.** Constraints x_i != x_{i+1} around an odd cycle are satisfiable on every edge and every proper path, yet no global assignment exists (local green, global red); even cycles glue. | `PROVED_LEAN` | Lean: 3-cycle marginal invariant; Rust: n = 3, 5, 7 | Lean `pairwise_compatible_three_cycle_contextual_obstruction`; Rust `c25_odd_cycle_local_green_global_red` | - |
| LGGR-C26 | **Mermin-Peres parity obstruction.** Every row and column context of the magic square is satisfiable, but no global +/-1 assignment meets row products (1,1,1) and column products (1,1,-1). | `PROVED_LEAN` | general (finite) | Lean `mermin_peres_magic_square_parity_obstruction`; Rust `c26_mermin_peres_parity_obstruction` | LGGR-C25 |
| LGGR-C27 | **Contextual-fraction packing bound (scaled arithmetic).** With constant context weight m, U = S + N and R = mN give U - R = S - (m - 1)N, so any packing Gamma >= U - R has S - Gamma <= (m - 1)N, the scaled form of CF <= (m - 1) N_min. _Note: The Lean theorem assumes the mass identities U = S + N and R = mN; their derivation from an LP signed extension is not formalized here._ | `PROVED_LEAN` | the arithmetic step; the LP reading CF <= (m-1) N_min is prose | Lean `contextual_fraction_packing_mass_identity`; Rust `c27_contextual_fraction_packing_identity` | - |
| LGGR-C28 | **Three-party separation CF(p*) > 2 N_min(p*) (arithmetic on supplied optima).** Given optimal packing mass 540/768 and negative mass 75/768 at p* (GHZ rnd2), CF(p*) = 19/64 and N_min(p*) = 25/256, so CF - 2 N_min = 13/128 > 0, and the order reverses against Q_{5/8}. _Note: Optimality of 540/768 and 75/768 (the LP primal/dual certificates) is not checked in Lean or Rust in this repository; see LGGR-O04._ | `PROVED_LEAN` | arithmetic over denominator 768 on supplied optima | Lean `ghz_rnd2_cf_gt_two_neg_mass_and_order_reversal`; Rust `c28_ghz_rnd2_cf_vs_neg_mass_arithmetic` | LGGR-C27 |

## Host rule and evidence (code/)

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-C32 | **Host elimination rule: no false accept in model.** If the true hypothesis is in the declared space and every observation is faithful, the host rule (accept iff every surviving hypothesis passes) never accepts a failing system and never rejects a passing one. | `TESTED_RUST` | exhaustive over 3-hypothesis, 2-check spaces; general proof is one line (the truth survives elimination) | Rust `c32_host_rule_no_false_accept_in_model` | - |
| LGGR-C33 | **Out of model, the host rule can false-accept.** If the true world lies outside the hypothesis space, evidence consistent with only passing hypotheses makes the host accept a failing system. | `TESTED_RUST` | explicit counterexample | Rust `c33_host_rule_false_accept_out_of_model` | LGGR-C32 |
| LGGR-C34 | **The LGGR selector quantity vanishes exactly at resolution.** The number of surviving accept/reject hypothesis pairs is zero if and only if the host rule is resolved (all survivors agree). | `TESTED_RUST` | exhaustive over 4-hypothesis spaces | Rust `c34_zero_verdict_pairs_iff_resolved` | LGGR-C32 |
| LGGR-C35 | **Every recorded example receipt is re-derived in Rust.** For the 11 receipts in receipts/ that have a matching example, the Rust kernels reproduce the recorded status. | `TESTED_RUST` | the 11 supplied receipts | Rust `c35_receipts_rederived` | LGGR-C02, LGGR-C12, LGGR-C15, LGGR-C16, LGGR-C17, LGGR-C19 |
| LGGR-C36 | **Workflow event logs are intact hash chains.** Each record's sha256 is the digest of its canonical body and links to the previous record; the recorded logs verify, and editing one field breaks the chain at that record. _Note: Tamper evidence only; a hash chain does not authenticate who wrote it._ | `TESTED_RUST` | three recorded event logs (live five-agent evaluation and development, concurrent five-agent development) | Rust `c36_workflow_event_chains_verify` | - |

## Workflows (empirical)

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-E01 | **P1: LGGR evidence selection beats uncertainty reduction under the host rule.** At 4 verification units, C - B = +0.268 correct decisions per (instance, draw), 95% CI [0.225, 0.309], p < 1e-4 (cap-sensitivity rerun: +0.271). _Note: A property of the selectors on this generator's problem class._ | `EMPIRICAL` | 400 generated multi-module tasks from one generator; host elimination rule | `workflows/lggr_rsi_swarm/REPORT.md`; `workflows/lggr_rsi_swarm/RESULTS.json` | LGGR-C32, LGGR-C34 |
| LGGR-E02 | **P2: no difference with live model controllers.** With Haiku 5.5 controllers, L-C - L-B = -0.001, 95% CI [-0.013, 0.013], p = 0.95 (absorbed by the agent); about 85% correct whatever note is given. | `EMPIRICAL` | same task set; live controllers, budget 4, turn cap 6 | `workflows/lggr_rsi_swarm/REPORT.md` | LGGR-E01 |
| LGGR-E03 | **Every false accept came from an out-of-model control.** Agent false accepts: L-0 16, L-B 42, L-C 46; host-rule false accepts on the same evidence: 16 / 42 / 45; none on clean or malformed-evidence instances. _Note: Consistent with LGGR-C32/C33: in-model soundness, out-of-model failure._ | `EMPIRICAL` | same task set | `workflows/lggr_rsi_swarm/REPORT.md`; `workflows/lggr_rsi_swarm/RESULTS_TRUST.json` | LGGR-C32, LGGR-C33 |
| LGGR-E04 | **RSI memory: no significant effect.** v2 system passes: source-bound memory 40/90 (44.4%) vs plain 36/90 (40.0%); paired sign test p = 0.29. _Note: Direction only; sample too small to claim an effect._ | `EMPIRICAL` | 30 instances x 3 draws per arm | `workflows/lggr_rsi_swarm/REPORT.md` | LGGR-C23 |
| LGGR-E05 | **Concurrent five-agent pilot: no LGGR advantage.** Of three completed paired feasible-fault trials, conventional feedback recovered 3 and LGGR feedback 2; no invalid SQLite executions in any arm (a property of the shared gate). | `EMPIRICAL` | pilot, 13 finished seeds, 8 fully paired | `workflows/concurrent_five_agent_swarm/REPORT.md` | - |
| LGGR-E06 | **Live five-agent pilot: no LGGR advantage.** The serial live pilot produced real failures and recoveries but did not show an LGGR advantage over complete-contract checking. | `EMPIRICAL` | pilot | `workflows/live_five_agent_swarm/REPORT.md` | - |
| LGGR-E07 | **Code-engineering swarm scenarios exhibit local green / global red.** In constructed 3- and 4-module codebases every module passes its own unit tests while integration fails (Delta_E = -1); on several single seeds the LGGR directive arm resolved in fewer waves (e.g. seed 6102: 1 wave vs 2). | `EMPIRICAL` | single-seed exploratory pilots; no statistical claim | `workflows/concurrent_code_engineering_swarm/README.md` | LGGR-C05, LGGR-C30 |

## Open

| ID | Claim | Status | Scope | Evidence | Depends on |
|---|---|---|---|---|---|
| LGGR-O01 | **General finite decoder-or-collision theorem in Lean.** Prove the finite-table dichotomy (LGGR-C02) constructively in Lean for every finite carrier, not only as the classical pair alternative. | `OPEN` | goal | - | LGGR-C02 |
| LGGR-O02 | **General weak duality and multi-point minimax in Lean.** Formalize LGGR-C14 and LGGR-C22 for arbitrary finite rational data. | `OPEN` | goal | - | LGGR-C14, LGGR-C22 |
| LGGR-O03 | **Constructive Lean core.** 47 Lean theorems here depend on Classical.choice (see lean_inventory). Omega Codex admits only propext and Quot.sound; removing Classical.choice is open. | `OPEN` | goal | - | - |
| LGGR-O04 | **LP certificates for CF and N_min in Rust.** Port the exact rational primal/dual LP certificates behind LGGR-C28 (and the isotropic CHSH/Mermin families) from the archived paper code to Rust. | `OPEN` | goal (phase 2) | - | LGGR-C27, LGGR-C28 |
| LGGR-O05 | **Rust ports for the code-swarm monitors.** The streaming codebase monitors in lggr/streaming.py used by workflows/ have Lean instance audits (LggrVIII) but no Rust re-derivation yet. | `OPEN` | goal | - | LGGR-E07 |

## Lean inventory not yet curated

121 further Lean theorems (from `LggrVIII.lean`, `LggrVII.lean`, `WorldLGGRWitness.lean`) are recorded as `PROVED_LEAN` nodes `LGGR-L-<module>-<theorem>` in the DAG, with their docstring as the statement. Most `LggrVIII` `*_audit` theorems are concrete finite codebase audits, so their scope is the stated instance. `PrimitiveDifference.lean` (75 lemmas) is one support node. Curating these into core claims is part of the next pass.

| ID | Scope | Classical.choice |
|---|---|---|
| LGGR-L-LggrVIII-historyEndpoint_mem | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-cross_branch_audit_splice_budget_breach | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-multi_stage_gluing_associativity_and_defect_bound | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-coarsened_macro_stage_masks_internal_prefix_breach | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-deferred_obligation_and_scope_migration_separation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-l1_dual_witness_subgradient_weight_sensitivity | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-cycle_bottleneck_weight_pivot_threshold | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-six_role_sample_defect_and_cancellation_masking | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-completion_relative_obstruction_on_carrier_extension | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-disjoint_colliding_pairs_additive_error_lower_bound | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-centered_gram_kernel_nullspace_obstruction | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-path_kernel_composition_discrepancy_identity | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-boundary_sufficiency_without_quotient_factorization | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-realizable_defect_soundness_kernel_intersection | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-dashboard_summary_reconstruction_and_collapsing_detector | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-product_retraction_residual_vs_local_extension | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-two_player_shapley_efficiency_and_symmetry | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-quorum_threshold_vs_product_defect_separation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-kraus_trace_preservation_and_blindspot_residual | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-sliding_window_green_vs_horizon_drift_breach | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-arrival_order_endpoint_invariance_vs_prefix_divergence | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-simplicial_cup_product_and_leibniz_cocycle_identity | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-mayer_vietoris_local_exactness_gluing_obstruction | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-discrete_hodge_harmonic_orthogonality_and_decomposition | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-dfa_concatenation_state_mismatch_obstruction | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-catalyst_residual_accumulation_and_cycle_ceiling | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-hodge_laplacian_energy_sum_of_squares_kernel | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-discrete_regge_hinge_deficit_and_gauss_bonnet | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-fibered_pullback_compatibility_and_mediator_uniqueness | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-optional_stopping_expectation_conservation_vs_skew | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-derived_limit_projective_tower_lifting_obstruction | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-skew_repair_norm_attainment_divergence_and_obstruction | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-side_information_channel_capacity_and_fiber_error_floor | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-product_of_experts_disjoint_support_collapse_vs_mixture | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-closed_loop_receipt_feedback_repair_convergence_vs_uninformed_retry | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-coupled_multi_monitor_joint_repair_whack_a_mole_vs_pareto_convergence | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-infeasible_coupled_multi_monitor_empty_intersection_oscillation_vs_escalation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-governed_policy_relaxation_handoff_restores_pareto_vs_self_relaxation | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-minimum_slack_pareto_policy_relaxation_vs_over_permissive_grant | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-asymmetric_weighted_policy_relaxation_tie_breaking_vs_unweighted_slack | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-cumulative_policy_ratchet_drift_vs_lease_revocation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-concurrent_lease_overlap_horizon_breach_vs_overlap_accounting | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-non_preemptible_simultaneous_budget_split_vs_priority_queueing | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-deadline_constrained_priority_queue_static_inversion_vs_edf | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-overloaded_deadline_burst_serial_edf_vs_bin_packing_and_escalation | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-variable_duration_burst_and_graceful_degradation_shedding | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-linearized_pipeline_jacobian_soundness_vs_stealth_blindspot | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-watcher_dropout_gram_rank_deficiency_and_critical_blindspot | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-multi_evaluator_policy_ranking_cf_vs_neg_mass_order_reversal | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-rsi_unassisted_self_reflection_vs_tool_assisted_fiber_splitting | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-multi_turn_pairwise_transcript_contextuality_and_reconciliation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-disagreement_preserving_side_channel_council_vs_collapsing_consensus | as stated in the Lean theorem | yes |
| LGGR-L-LggrVIII-bounded_depth_k_induction_tower_and_carrier_completion | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-boundary_mixing_and_quorum_masking_interface_schema_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-cross_role_schema_validation_and_double_count_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-stage_unit_vs_e2e_integration_kernel_and_dashboard_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-three_party_no_signalling_c3_interval_family_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-dynamic_boundary_schema_synthesis_under_online_collisions | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-adversarial_prompt_injection_schema_and_side_channel_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-equal_info_baseline_vs_lggr_migration_and_obligation_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-multi_cycle_catalyst_wear_vs_periodic_rejuvenation_schedule | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-dfa_non_resetting_concatenation_vs_explicit_reset_gluing | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-cptp_state_blindspot_vs_operator_residual_and_completion | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-mayer_vietoris_disconnected_overlap_and_coboundary_reconciliation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-asynchronous_replay_order_prefix_peak_envelope_and_robustness | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-sliding_window_truncation_vs_horizon_rebalancing_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-optional_stopping_early_gain_skew_vs_tail_drawdown_cap | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-regge_hinge_deficit_curvature_and_boundary_gauss_bonnet_holonomy | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-coalitional_shapley_attribution_under_synergistic_fault_masking | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-pullback_square_mediator_uniqueness_and_interface_factorization_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-multi_loop_two_complex_cup_product_and_hodge_harmonic_kernel_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-figure_eight_wedge_junction_gauge_shift_and_mayer_vietoris_hodge_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-shared_chord_bicyclic_diamond_hodge_and_mayer_vietoris_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-concurrent_code_swarm_symmetry_broken_directive_vs_bilateral_oscillation | as stated in the Lean theorem | no |
| LGGR-L-LggrVIII-diamond_codebase_pullback_mediator_contract_synthesis_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-iterative_codebase_feature_evolution_catalyst_debt_and_rejuvenation_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-stateful_codebase_transaction_dfa_reset_gluing_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-async_codebase_replay_order_prefix_envelope_and_barrier_gluing_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-coalitional_codebase_synergistic_fault_masking_and_shapley_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-mayer_vietoris_codebase_disconnected_overlap_and_coboundary_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-windowed_drift_codebase_horizon_truncation_and_rebalancing_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-optional_stopping_codebase_early_gain_skew_and_drawdown_cap_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-cptp_codebase_state_blindspot_and_operator_completion_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-regge_codebase_hinge_deficit_and_gauss_bonnet_holonomy_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-kinduction_codebase_bounded_unrolling_and_invariant_strengthening_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-jacobian_codebase_stealth_blindspot_and_observability_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-boundary_quorum_codebase_mixing_and_quorum_masking_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-lease_overlap_codebase_split_brain_and_fencing_token_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-contextual_sheaf_codebase_hollow_triangle_and_reconciliation_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-watcher_dropout_codebase_gram_rank_deficiency_and_restoration_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-policy_reversal_codebase_cf_vs_neg_mass_ranking_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-fiber_splitting_codebase_unassisted_reflection_and_tool_probe_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-disagreement_council_codebase_collapsing_consensus_and_side_channel_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-six_role_codebase_schema_validation_and_double_count_deduplication_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-path_kernel_codebase_stage_vs_e2e_and_dashboard_adequacy_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-dynamic_schema_codebase_online_collision_and_refinement_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-adversarial_schema_codebase_spoofed_metadata_and_side_channel_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-graceful_shedding_codebase_variable_duration_burst_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-obligation_migration_codebase_equal_info_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-three_party_c3_codebase_constant_bound_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-multi_loop_hodge_codebase_cup_and_harmonic_kernel_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-figure_eight_wedge_codebase_junction_gauge_and_hodge_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-shared_chord_diamond_codebase_hodge_and_mayer_vietoris_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-governed_relaxation_codebase_authority_gate_and_minimum_slack_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-non_abelian_braid_codebase_word_ordering_and_yang_baxter_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-subgradient_pivot_codebase_weight_sensitivity_and_bottleneck_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-policy_ratchet_codebase_cumulative_drift_and_sunset_revocation_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-skew_repair_codebase_norm_attainment_divergence_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-poe_veto_codebase_zero_collapse_and_compromise_mass_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-simultaneous_split_codebase_budget_starvation_and_joint_guard_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-mermin_peres_codebase_parity_obstruction_and_noncontextual_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-side_info_capacity_codebase_ambiguity_and_bit_budget_audit | as stated in the Lean theorem (concrete finite codebase audit) | yes |
| LGGR-L-LggrVIII-deadline_bin_packing_codebase_edf_and_overload_admission_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-projective_tower_codebase_r1_limit_and_integral_lift_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-bell_polytope_codebase_chsh_violation_and_lhv_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-weighted_relaxation_codebase_pareto_tie_and_minimum_weighted_slack_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-threshold_governance_codebase_prefix_excursion_and_endpoint_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-closed_loop_repair_codebase_open_loop_residual_and_witness_convergence_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-LggrVIII-product_retraction_codebase_non_injective_projection_and_section_lift_audit | as stated in the Lean theorem (concrete finite codebase audit) | no |
| LGGR-L-WorldLGGRWitness-setoidPairFactorOrLGGRWitness | as stated in the Lean theorem | yes |
| LGGR-L-WorldLGGRWitness-scope_boundary_snapshot | as stated in the Lean theorem | no |
| LGGR-L-PrimitiveDifference | support library | no |
