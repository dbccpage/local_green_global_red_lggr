# Current statement-to-proof map

This map, its embedded-research extension below, and the root version 1.7.0 manuscript describe current scope. The version 1.6.1 consolidation preserved the earlier statements; version 1.7.0 adds the new proof modules mapped below. `precursor_mechanization_map.md` is verbatim historical source. Lean declarations below have the prefix `EpistemicNoGo.`. Python tests live in `code/tests/`.

| Current statement | Lean module and declarations | Executable scope |
| --- | --- | --- |
| Primal and dual attainment for every finite real contextuality LP | `ContextualDuality.compact_convex_distance_duality`, `contextuality_strong_duality` | Constructs an attaining dual by geometric separation; zero gap is a conclusion |
| Canonical maximum over deterministic columns | `ContextualDuality.dual_offset_is_negative_max`, `canonical_dual_attainment` | Exhibits a column attaining the finite maximum; offset is its negative |
| Exhaustive joint-or-positive-defect alternative, and exclusion | `ContextualDuality.joint_or_positive_dual`, `positive_dual_excludes_joint`, `cost_zero_iff` | Arbitrary finite real tables, not only Bell fixtures |
| Ordered-field weak duality and certificate optimality | `ContextualDuality.weak_duality`, `zero_gap_certificate_optimal`, `dual_solution_optimal` | Includes exact rational arithmetic |
| Literal standard-form LP with nonnegative residual variables | `ContextualDuality.slacks_l1_lower_bound`, `exact_slacks_exist`, `contextuality_standard_form_strong_duality` | Same constraints and objective as the standalone solver |
| Rational certificate bounds against all real competitors | `ContextualDuality.rational_certificate_real_optimal`, `rational_simplex_cast` | Scalar embedding preserves primal feasibility and the certified lower bound |
| Five actual exact-rational solver outputs | All ten theorems in `RationalCertificates` | Classical (0), PR (2), near (4/5), triangle (2), boundary (1/25000000); numerical feasibility and zero gap checked by Lean |
| Executable two-phase solver success is feasible and optimal | `Simplex.solve_correct`, `solve_optimal`, `valid_is_real_optimal`, `standard_weak_duality`, `valid_is_optimal` | Arbitrary finite rational standard-form input; includes the mandatory independent final checker |
| Exact pivot semantics and feasible RHS | `Simplex.pivot_column`, `pivot_row_eval`, `pivot_preserves_equations`, `pivot_preserves_objective`, `pivot_preserves_rhs`, `initial_rhs_nonnegative` | Actual materialized pivot definition; nonzero pivot and ratio-test premises are explicit |
| Entering selector | `Simplex.entering_none_iff`, `entering_negative` | Finite original columns and exact reduced-cost signs |
| Shared finite-budget termination and accounting | `Simplex.simplex_budget_exact`, `cleanup_budget_exact`, `execute_budget_exact`, `accepted_pivots_match_trace`, `solve_pivot_bound` | Structural recursion on remaining budget and cleanup row list; no unbudgeted completeness or wall-clock bound |
| Materialized exact vector implementation | `Simplex.vector_get_ofFn`, `memo_apply` | Lookup in cached finite rows agrees with the mathematical function |
| State enclosure to observation uncertainty | `ErrorBudget.observation_radius`, `nearest_distance_lipschitz`, `uncertainty_adjusted_witness` | Declared bounded linear observations, attained nearest points, and feasible contextuality witness |
| Actual-trajectory propagation and correction windows | `ErrorBudget.trajectory_error_bound`, `constant_residual_envelope`, `nonexpansive_envelope`, `correction_window` | Explicit Lipschitz dynamics and actual one-step defect caps; no initial-speed substitution |
| Continuous enclosure consequence and correction-capacity obstruction | `ErrorBudget.duhamel_waiting_window`, `correction_capacity_lower_bound`, `threshold_missed` | Conditional scalar implications; continuous ODE enclosure and physical rate/capacity hypotheses are supplied |
| PR support contradiction | `ResultI.pr_box_no_global_assignment`, `pr_box_no_supported_assignment` | Finite binary Bell support, exhaustive Boolean proof |
| Positive-weight joint cannot live in PR support | `ResultI.no_positive_joint_into_pr`, `mass_zero_into_pr` | Finitely supported natural-weight measures; general probability-vector extension in prose |
| Classical global section | `ResultI.classical_joint_is_global_section` | Exact context marginal weights |
| CHSH bounds and near-boundary incompatibility | None | Python exact `Fraction` calculations and all sixteen deterministic assignments |
| Observation collision blocks recovery | `ResultII.fiber_lemma`, `no_perfect_peer_prediction`, `private_fiber_blocks_prediction` | Arbitrary types with explicit collision premises |
| Instantaneous loss need not persist | `ResultII.hidden_at_zero_is_report_at_one`, `swap_not_intertwined`, `kernel_does_not_give_privacy_over_time` | Bit-pair swap counterexample |
| One-step fiber preservation iff preservation for all finite words | `Bridge.report_eq_after_word`, `fibers_preserved_iff_all_words` | Arbitrary state, report and update types; no finite cardinality restriction |
| Intertwining supplies fiber preservation | `Bridge.intertwining_preserves_fibers` | Explicit family of reduced updates |
| A future task collision blocks current-report prediction | `Bridge.future_task_collision_blocks_prediction` | Arbitrary task and a specified finite word |
| Every verified ledger prefix verifies | `ResultIII.verifyFrom_append_left`, `prefix_verifies` | Arbitrary digest function; no cryptographic assumption |
| Concrete truncation, pin, and tamper witnesses | `ResultIII.ledger_verifies`, `truncation_is_invisible`, `pinned_tip_separates`, `tamper_detected`, `internal_verification_is_not_completeness` | Toy arithmetic digest in Lean; SHA-256 examples in Python |
| A tip pin alone need not identify a history | `Bridge.pinned_tip_can_collide` | Constant-digest counterexample, empty and nonempty ledgers |
| Relabeling blindness requires invariance | `ResultIII.invariant_verdict_blind`, `invariant_export_blind`, `noninvariant_verdict_separates` | Factorization statement and a concrete non-invariant counterexample |
| Provenance refusals and pass conditions | All named theorems in `ResultIV` | Independent Lean policy model; no identity authentication or Rust refinement proof |
| A successful provenance packet can accompany an unsafe action | `Bridge.provenance_pass_can_be_unsafe` | Concrete successful packet plus action 1 when only 0 is safe |
| Tarski, Löb, cryptographic integrity, real-system authority | None | Imported background or application premises, not package theorems |

The named census covers every explicit theorem, including helper theorems in the source modules that the precursor's 29-entry selection omitted. The full census checks all package-local environment declarations, including definitions, private declarations, and generated auxiliaries. These are different counts. Audit commands re-execute Lean and compare the current outputs with stored reports.

The 26 inherited and 13 bridge test executions are supplemented by the contextuality LP tests and generated-data custody checks. The update-map enumeration is bounded to four states; it supplements the general Lean induction. The complete Lean solver is an executable certified program: the final replay guards every successful return. The Python implementation is separately compared on 95 full outputs, including refusals and pivot counts. This is finite agreement evidence. Finite-budget Lean termination and successful-return correctness are formalized; universal different-language equivalence and unbudgeted Bland completeness are not asserted.

## Version 1.5.1 API and presentation correction

The 98 named theorem statements and all eleven proof module bytes are unchanged. The continuous waiting-window prose now explicitly requires positive residual rate and positive observable norm; its zero-rate case follows directly from the supplied constant enclosure. No new continuous propagator theorem is asserted.

`evaluate_observed` and `verify_observed` implement the already stated uncertainty-adjusted witness formula for unchanged exact row frequencies, including signalling samples. Their Python tests and source-bound exact example are executable evidence. They do not constitute a universal Python-to-Lean refinement or a proof of statistical coverage.


## Version 1.6.0 checked outcomes and partial-observation integration

| Statement | Lean declaration in `EpistemicNoGo` | Scope |
| --- | --- | --- |
| Farkas witness excludes every real feasible vector | `CertifiedOutcomes.infeasible_excludes_real` | Original rational equality constraints and nonnegative real variables |
| Feasible ray, objective identity and arbitrary real floor | `CertifiedOutcomes.ray_real_feasible`, `ray_real_objective`, `unbounded_below_real` | Checked rational base and direction; nonnegative real ray parameter |
| All accepted outcome constructors satisfy their checks | `CertifiedOutcomes.accept_correct`, `solve_certified_correct` | Actual total extended program with mandatory original-input replay |
| Accepted infeasible, unbounded and optimal outcomes have real semantics | `CertifiedOutcomes.solve_infeasible_correct`, `solve_unbounded_correct`, `solve_optimal_correct` | No assumptions about unverified candidate correctness |
| Terminal-tableau search consumes exactly its budget | `CertifiedOutcomes.search_budget_exact` | Optimal and ray terminals; shared cleanup uses existing accounting |
| Greatest sound report-only acceptance set | `MindContracts.whole_fiber_sound`, `whole_fiber_maximal` | Arbitrary types/predicates; no efficient decidability claim |
| Regret and uniquely optimal action from score error | `MindContracts.score_regret`, `score_gap_unique` | Explicit per-action error and score dominance/gap premises |
| Upper-bound exhaustion does not entail actual failure | `MindContracts.upper_bound_does_not_force_failure` | Zero-error witness for every nonnegative tolerance |
| Continuous hybrid representation-change enclosure | No new Lean theorem | Written conditional comparison argument; trajectory/stability/defect/jump premises required |
| Human/AI consciousness and phenomenal continuity | No theorem | Source hypotheses, not verified cognition claims |

The v1.5.1 paragraph above describes that historical patch: the new edition adds two modules and changes the driver, while retaining the prior theorem statements and updating the root imports and driver. `Simplex.solve` retains its optimal-only semantics; the release driver invokes `CertifiedOutcomes.solveCertified`. The Python solver is compared on all 95 complete outputs, including new Farkas and ray coordinates. Six source illustration groups with 19 standard-library assertions are separately replayed; floating illustrations do not enter LP checkers or Lean premises.

## Version 1.7.0: embedded knowledge and observation budgets

The complete new result mapping is in [embedded_research.md](embedded_research.md). `EmbeddedLimits`, `EmbeddedQuantitative` and `QueryBudget` are included in both the explicit-theorem and full-declaration censuses. The shared module has the same source hash in both standalone packages.

## Version 1.8.0: persistent memory

Eight source-supported update, recall, refusal and exact-reload statements in `LiveMemory` are added to both censuses. Full mappings, executable restart tests and live model-use limits are in [live_memory.md](live_memory.md).

## Version 1.8.3: API and release integrity

No theorem statements change. The named audit also binds the API/release regression source, packager and deposit verifier. Full-census check mode preserves sealed source bytes; explicit write mode regenerates them. These Python integrity properties are tested, not newly proved in Lean. See [review response](review_response_2026_10_23.md).
