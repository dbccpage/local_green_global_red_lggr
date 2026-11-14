# Local Green, Global Red: manuscript and implementation index

**Author:** Jeremy H. Carroll  
**Date:** 2026-10-24  
**Series:** Local Green, Global Red (Volumes I–VIII)

| Volume | Package | Title | Version | Date |
| --- | --- | --- | --- | --- |
| I | [`lggr_i_evaluated_path_kernels`](lggr_i_evaluated_path_kernels/lggr_i_evaluated_path_kernels.md) | Evaluated Path Kernels for Composed Agent Reliability | 1.2.4 | 2026-10-15 |
| II | [`lggr_ii_organizational_gluing`](lggr_ii_organizational_gluing/lggr_ii_organizational_gluing.md) | Organizational Evaluator Gluing | 1.3.1 | 2026-10-15 |
| III | [`lggr_iii_epk_gtla_overlay`](lggr_iii_epk_gtla_overlay/lggr_iii_epk_gtla_overlay.md) | A Finite Evaluator Overlay Across Six System Roles | 1.5.2 | 2026-10-15 |
| IV | [`lggr_iv_finite_presentations_completion_relative`](lggr_iv_finite_presentations_completion_relative/lggr_iv_finite_presentations_completion_relative.md) | Finite Presentations and Completion-Relative Obstruction | 0.1.1 | 2026-10-15 |
| V | [`lggr_v_local_green_global_red`](lggr_v_local_green_global_red/lggr_v_local_green_global_red.md) | Local Green, Global Red: When Local Evaluators Cannot Certify Global Exactness | 1.3.2 | 2026-10-15 |
| VI | [`lggr_vi_nonlinear_aggregation_and_adjoint_probing`](lggr_vi_nonlinear_aggregation_and_adjoint_probing/lggr_vi_nonlinear_aggregation_and_adjoint_probing.md) | Nonlinear Aggregation, Gram Kernels, and Centered Adjoint Probing | 0.1.1 | 2026-10-15 |
| VII | [`lggr_vii_projection_residuals_and_witness_composition`](lggr_vii_projection_residuals_and_witness_composition/lggr_vii_projection_residuals_and_witness_composition.md) | Positive-Extension Projection Residuals, Observer-Fiber Minimax Floors, and Witnessed Composition | 0.1.0 | 2026-10-23 |
| VIII | [`lggr_viii_online_streaming_discovery_and_runtime_gluing`](lggr_viii_online_streaming_discovery_and_runtime_gluing/lggr_viii_online_streaming_discovery_and_runtime_gluing.md) | Online Streaming LGGG vs. LGGR Discovery for Agentic Swarms | 0.1.0 | 2026-10-24 |


This repository index describes the eight current manuscripts and selected proof
sources. A source pointer records a declaration and its scope; it is not a fresh
compiler result, a full paper verification, or an empirical reliability claim.
See the [series guide](README.md) for entry points and focused replay commands.

The shared question is whether local reports retain enough information to answer
a specified global question. The volumes use different mathematical models; a
Boolean evaluator defect, a failure of descent, a raw cochain defect, and a repair
class must not be identified without a map and its hypotheses.

## I. Evaluated path kernels

[Manuscript](lggr_i_evaluated_path_kernels/lggr_i_evaluated_path_kernels.md),
[Python](lggr_i_evaluated_path_kernels/code/epk_core.py).

- The Boolean defect is $\Delta_E=E_g-E_1E_2\in\{-1,0,1\}$.
  Zero means evaluator agreement, including the case where both reject.
- Kernel composition requires a bijection between admitted composed paths and
  compatible pairs, multiplicative weights, and pointwise evaluator
  factorization (G1–G3). Proposal-weighted composition also needs G4.
- Signed defects can cancel in an aggregate. Zero aggregate defect does not
  establish pointwise agreement.
- A carrier collision with different global verdicts prevents a carrier-only
  evaluator from recovering both. The diagnostic pair $(E_1E_2,E_g)$ retains
  more information than the defect alone.

Selected Lean declarations:

| Source | Declaration | Scope |
| --- | --- | --- |
| [Boolean partition](lggr_i_evaluated_path_kernels/lean4/02_delta_partition.lean) | `PaperAE004.exactly_one_defect_class` | Boolean inputs and integer defect classes. |
| [Composition](lggr_i_evaluated_path_kernels/lean4/03c_g1_set_isomorphism.lean) | `PaperAE004.raw_kernel_composition_under_G1_G2_G3` | Finite lists and integer weights under explicit factorization hypotheses. |
| [Carrier quotient](lggr_i_evaluated_path_kernels/lean4/21_carrier_kernel_quotient.lean) | `PaperAE004.carrier_bounded_iff_invariant`, `PaperAE004.verdict_ceiling` | Fiber constancy and a two-trace impossibility witness; no real exponential-weight construction. |

## II. Organizational evaluator gluing

[Manuscript](lggr_ii_organizational_gluing/lggr_ii_organizational_gluing.md),
[Python](lggr_ii_organizational_gluing/code/organizational_gluing_core.py).

The organizational defect compares $E_G$ with the product of the local Boolean
verdicts. A report can determine $E_G$ without making it equal to that product.
A mixed carrier fiber defeats quotient factorization; an additional local-green
premise produces an LGGR witness in that fiber.

Representational, ownership, temporal, and agreement requirements are declared
closure conditions. Conjoining flags does not establish operational authority.
The Boolean model does not construct a presheaf or prove a general sheaf-gluing
theorem; those require actual restriction maps and compatibility laws.

| Source | Declaration | Scope |
| --- | --- | --- |
| [Boundary sufficiency](lggr_ii_organizational_gluing/lean4/02_boundary_sufficiency.lean) | `PaperAE005.weak_boundary_sufficiency_does_not_force_factorization` | Explicit Boolean counterexample. |
| [Carrier obstruction](lggr_ii_organizational_gluing/lean4/04_carrier_boundary_obstruction.lean) | `PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization`, `PaperAE005.boundary_carrier_mixing_forces_lggr` | Declared carrier projections; the second theorem also requires local green. |

## III. A finite evaluator overlay across six system roles

[Manuscript](lggr_iii_epk_gtla_overlay/lggr_iii_epk_gtla_overlay.md),
[Python](lggr_iii_epk_gtla_overlay/code/epk_gtla_overlay_core.py),
[Lean source](lggr_iii_epk_gtla_overlay/lean4/Core.lean).

The six roles are **finite obstruction, foundations, representation, observer,
continuum shadow, and action alignment**. They are profiles for recording the
same finite evaluator calculus. They are not planner/worker governance seats.
The manuscript supplies no payoff matrix, anti-collusion theorem, or proof that
truth-telling dominates under a penalty contract.

`LGGR3.factorized_integer_kernel_has_zero_residual` proves a finite integer
factorization identity. `LGGR3.fixed_observation_preserves_defect` says unchanged
verdicts give unchanged defect. `LGGR3.quotient_evaluator_obstruction` addresses
the explicitly defined carrier setoid; it is not a theorem about every possible
organizational quotient. `LGGR3.six_roles` counts the declared list.

## IV. Finite presentations and completion-relative obstruction

[Manuscript](lggr_iv_finite_presentations_completion_relative/lggr_iv_finite_presentations_completion_relative.md),
[Python](lggr_iv_finite_presentations_completion_relative/code/lggr_iv_core.py),
[Lean source](lggr_iv_finite_presentations_completion_relative/lean4/core.lean).

- At a fixed presentation, descent of a question means constancy on every
  realized fiber. Failure at every stage can require different witness pairs.
- The compatible congruences $3x+1\equiv0\pmod{2^n}$ have finite-stage integer
  solutions but no single integer solution at every stage. Their compatible
  limit is $-1/3$ in the separately admitted $2$-adic completion.
- A valid completed witness descends only if it belongs to the reflection image;
  relating validity in the two carriers requires the stated validity condition.
- General cofiltered compactness, derived limits, and Mittag-Leffler results are
  classical mathematical inputs. Failure of Mittag-Leffler is not by itself a
  proof of a nonzero derived-limit obstruction.

| Declaration | Actual formal scope |
| --- | --- |
| `LggrIV.finite_stage_collision_iff` | Enumerated finite carrier and declared question. |
| `LggrIV.finite_stage_identity`, `LggrIV.no_integral_global_solution` | Exact integer congruence construction and impossibility. |
| `LggrIV.reflection_descent_criterion` | Unfolds the definition into validity plus image membership. |
| `LggrIV.finite_chain_limit_nonempty` | A supplied top element pulled back along a finite list of transitions. |

The last theorem is not the general cofiltered theorem in Stacks Tag 086J.
This Lean package does not formalize the general Mittag-Leffler or derived-limit
claims. There are no declarations named `stacks_tag_086j_thread` or
`stacks_tag_07kv_mittag_leffler` in the indexed proof sources.

## V. Finite no-recovery and repair distance

[Manuscript](lggr_v_local_green_global_red/lggr_v_local_green_global_red.md),
[exact rational replay](lggr_v_local_green_global_red/code/lgr_replay.py),
[exact cochain checker](lggr_v_local_green_global_red/code/code_exact_obstruction.py).

Let $D$ be the section-defect map and $Q$ the combined linear observation map.
All-green means **zero observed scores**. Soundness on realizable defects is
$\mathrm{im}(D)\cap\ker(Q)=\{0\}$. Triviality of the entire ambient joint
kernel is sufficient but not necessary.

The six-site, three-patch family has raw mass $6|\lambda|$ and all observed scores
zero. With unrestricted real $\lambda$, no finite bound from those scores alone
controls raw mass. This concerns a finite incidence system with unbounded state
values, not a finite state space or a bounded-state impossibility theorem.

Keep its two examples separate:

- A section defect $Ds$ is in the repair image, so its distance to that image is
  zero even when its raw mass is large.
- The separate cochain $\omega=(1,-1)$ has $\ell^1$ distance **2** from the
  diagonal repair image. This is a norm distance, not Hamming distance.

[ObserverVisibility Lean](lggr_v_local_green_global_red/lean4/observer_visibility.lean)
contains `ObserverVisibility.master_soundness_iff` with an explicit norm-zero
hypothesis, and `ObserverVisibility.ThreePatch.no_recovery_modulus` for the
scaling family. The [PO000 companion](lggr_v_local_green_global_red/lean4/po000_l004_observer_visibility.lean)
contains `PO000.ObserverVisibility.QuotientWitness.repair_mass_ge_two` and
`PO000.ObserverVisibility.QuotientWitness.repair_mass_attained`.
These do not formalize every graph-incidence construction or every norm formula
in the manuscript. The additional `minkowski_repair.lean` file is not a default
Lake root in this package.

## VI. Nonlinear aggregation and adjoint probing

[Manuscript](lggr_vi_nonlinear_aggregation_and_adjoint_probing/lggr_vi_nonlinear_aggregation_and_adjoint_probing.md),
[Python](lggr_vi_nonlinear_aggregation_and_adjoint_probing/code/lggr_vi_core.py),
[Lean source](lggr_vi_nonlinear_aggregation_and_adjoint_probing/lean4/Core.lean).

Deterministic postprocessing cannot distinguish states with the same observation.
For rational matrices, $H=Q^TQ$ satisfies $\ker H=\ker Q$; forming the Gram
operator therefore does not recover hidden components. Centered energy probes
recover directional pairings with $Hx$, and a full sign-cube average recovers
$Hx$. Neither operation reconstructs a component in $\ker Q$.

| Declaration | Actual formal scope |
| --- | --- |
| `LGGRVI.postprocessing_invariance` | Arbitrary functions and equal observations. |
| `LGGRVI.gram_kernel_iff` | Actual finite rational matrices, rather than an assumed Gram-kernel identity. |
| `LGGRVI.centered_directional_identity` | Exact rational two-query identity with nonzero step. |
| `LGGRVI.sign_cube_recovers` | Full finite sign-cube average; no random-prefix convergence guarantee. |

The real singular-value cylinder estimate remains classical supporting analysis
and a numerical helper, explicitly outside this deposit's theorem boundary.
The manuscript's 25-step programme is deferred research, not 25 completed
verification steps or a global optimization theorem.

## VII. Positive-extension projection residuals, observer-fiber minimax floors, and witnessed composition

[Manuscript](lggr_vii_projection_residuals_and_witness_composition/lggr_vii_projection_residuals_and_witness_composition.md),
[Python](lggr_vii_projection_residuals_and_witness_composition/code/lggr_vii_core.py),
[Lean source](lggr_vii_projection_residuals_and_witness_composition/lean4/LggrVII.lean).

Unifies the finite report-fiber and cochain repair checks of Volumes I–VI with
positive-extension projection residuals, signed-extension negative mass
($N_{\min}$), contextual fraction ($CF$), and observer-fiber scalar minimax
bounds under evidence-preserving recursion (`Lean 4.35.0`, zero custom axioms).

| Declaration | Actual formal scope |
| --- | --- |
| `LggrVII.collision_blocks_factorization`, `LggrVII.postprocessing_preserves_collision`, `LggrVII.verdict_ceiling_on_collision` | Arbitrary carrier types; explicit colliding pair refutes decoding, survives deterministic postprocessing, and forces report-only evaluator disagreement on at least one member. |
| `LggrVII.evalDefect_partition` | Boolean triples $(E_1, E_2, E_g)$ and integer defect $\Delta_E = E_g - E_1 E_2 \in \{-1, 0, 1\}$. |
| `LggrVII.local_steps_do_not_imply_endpoint_bound`, `LggrVII.every_prefix_strictly_stronger_than_endpoint`, `LggrVII.unsigned_report_collision_good_vs_bad` | Integer step-history telescoping, separation on $(0, 1, 2)$ and $(0, 1, 2, 1)$, and unsigned step-magnitude collision between $(0, 1, 0)$ and $(0, 1, 2)$. |
| `LggrVII.triangle_l1_primal_dual_optimality`, `LggrVII.filled_triangle_closure_vs_budget_exactness`, `LggrVII.retraction_reflects_repair_and_obstruction` | Exact integer-scaled 3-cycle $\ell^1$ optimum $\Phi(1,1,1)=1$, filled-triangle closure failure vs. exact budget coboundary $(1,1,2)=D_0(0,1,2)$, and left-inverse chain-retraction repair reflection. |
| `LggrVII.observer_fiber_two_point_minimax` | Integer two-point fiber error bound $|a - z| + |b - z| \ge b - a$ and midpoint attainment. |
| `LggrVII.contextual_fraction_packing_mass_identity`, `LggrVII.ghz_rnd2_cf_gt_two_neg_mass_and_order_reversal` | Scaled $m$-context mass identity $U - R = S - (mN - N)$ and exact denominator-$768$ certification of $CF(p_*) = 19/64 > 2 N_{\min}(p_*) = 25/128$ and order reversal against $Q_{5/8}$. |

<!-- ## viii -->
## VIII. Online streaming LGGG vs. LGGR discovery for agentic swarms

[Manuscript](lggr_viii_online_streaming_discovery_and_runtime_gluing/lggr_viii_online_streaming_discovery_and_runtime_gluing.md),
[Python](lggr_viii_online_streaming_discovery_and_runtime_gluing/code/lggr_viii_core.py),
[Lean source](lggr_viii_online_streaming_discovery_and_runtime_gluing/lean4/LggrVIII.lean),
[Claim Ledger](lggr_viii_online_streaming_discovery_and_runtime_gluing/lggr_viii_online_streaming_discovery_and_runtime_gluing_claim_ledger.md).

Extends the Local Green, Global Red framework from post-hoc batch evaluation to
online streaming discovery during live agentic swarm execution. Evaluates finite
step witnesses, report-fiber collisions, prefix-by-prefix signed budget drift,
and 1-cochain cycle closure incrementally as steps arrive (`Lean 4.35.0`, zero
custom axioms).

- **Incremental fiber collision:** Monotonicity under streaming trace extension
  ($T \subseteq T' \implies \mathrm{HasCollision}(p, q, T) \implies \mathrm{HasCollision}(p, q, T')$)
  and deterministic postprocessing invariance ($f \circ p$ preserves collision).
- **Streaming defect tracking:** Defect trichotomy $\Delta_E = E_{g,k} - L_k \in \{-1, 0, 1\}$,
  with $\Delta_E = -1$ uniquely identifying Local Green, Global Red (`NGD`).
- **Prefix vs. endpoint drift:** Exact signed step difference telescoping
  $\sum_{i=1}^n (x_i - x_{i-1}) = x_n - x_0$; strict separation of online
  `every_prefix` admissibility from endpoint admissibility on excursion trace
  $[0, 1, 2, 1]$ with budget $B = 1$; monotonic early stopping.
- **Incremental 1-cochain cycle closure:** Directed graph edge addition with
  active spanning forest maintenance; cycle closure defect $(D_1 h)_C$, exact
  rational weighted $\ell^1$ repair distance $\Phi(h)$, and dual witness $z$
  with $D_0^\top z = 0$ and $\|z\|_{\infty,w^{-1}} \le 1$.
- **Boundary sufficiency:** Certification of composable LGGG ($\Delta_E = 0$)
  when boundary reports preserve fiber constancy on declared queries; proof that
  colliding fibers force defect $\Delta_E = -1$ on at least one branch.
- **Empirical benchmarks & live swarm receipts:** Live OpenRouter completions
  ($N = 8$, $\mathrm{LPR} = 1$, $\mathrm{GPR} = 1$, $\mathrm{NGD} = 0$, $\mathrm{ZDR} = 1$,
  $\mathrm{PGD} = 0$) and structured replay receipts across Tests 1–4.

| Declaration | Actual formal scope |
| --- | --- |
| `LggrVIII.collision_monotonicity`, `LggrVIII.postprocessing_preserves_streaming_collision`, `LggrVIII.streaming_verdict_ceiling` | Arbitrary finite trace carrier; trace extension monotonicity and report-only verdict ceiling on colliding fibers. |
| `LggrVIII.streaming_evalDefect_partition`, `LggrVIII.streaming_chain_telescoping` | Boolean local/global pairs, defect trichotomy $\Delta_E \in \{-1, 0, 1\}$, and signed step-history telescoping identity. |
| `LggrVIII.online_prefix_strictly_stronger_than_endpoint`, `LggrVIII.prefix_violation_monotonicity`, `LggrVIII.streaming_unsigned_report_collision` | Excursion trace separation, monotonic early stopping under prefix violation, and unsigned report collision between $[0, 1, 0]$ and $[0, 1, 2]$. |
| `LggrVIII.open_chain_exactness`, `LggrVIII.incremental_cycle_closure_obstruction` | Acyclic spanning forest exactness ($D_1 = 0$, $\ell^1 = 0$) vs. closing edge circulation failure with dual witness $z = (1, 1, -1)$. |
| `LggrVIII.boundary_sufficient_gluing_certifies_lggg`, `LggrVIII.boundary_insufficiency_forces_defect` | Composable LGGG ($\Delta_E = 0$) under boundary sufficiency vs. forced LGGR ($\Delta_E = -1$) under colliding boundary fibers. |

### Artifact Summary — Volume VIII

1. **What it supports:** Exact finite theorems for streaming collision monotonicity, prefix budget early stopping, incremental 1-cochain cycle closure, dual witness certification, and empirical benchmark defect rate calculations.
2. **What it does not support:** Does not establish that unobserved agent behaviors satisfy safety invariants, nor does it replace full end-to-end integration testing with local checks.
3. **Narrowest defensible claim:** Online monitoring of realized report fibers, prefix sums, and spanning cycle defects detects composability obstructions at the exact step of occurrence and emits verified machine-readable receipts.
4. **Next test needed:** Continuous multi-agent swarm deployment with dynamic task graphs and online automated boundary schema adaptation.

## Connections to WDP and the Engine

The [WDP manuscript](../000_witnessed_difference_programme/witnessed_difference_programme.md)
makes several connections explicit:

| WDP location | LGGR connection | Required distinction |
| --- | --- | --- |
| §§10.6, 14.4 and Appendix T | V: realizable defect spaces, invisible kernels, observer completion. | Detecting raw defects and detecting nonzero repair classes are different tasks; realization and repair images may differ. |
| §§11, 16.7 and Appendix J | II–IV: descent and local/global compatibility. | A presheaf needs actual restriction maps and functor laws; Boolean disagreement supplies neither. |
| §14.3 and §17.8 | I–III, VI: report fibers, postprocessing, Gram radical. | Recoverability is relative to declared questions; a small symmetry stabilizer does not guarantee separation. |
| §17.1 | I, III: finite path sums and composition. | Full admitted paths or a faithful augmented carrier are needed before matrix multiplication represents composition. |
| §19.1 | II–IV: compatible local empirical models versus a global distribution. | Bell adds specific measurement, compatibility and positivity assumptions; LGGR alone does not distinguish quantum from classical systems. |

The native package is
[`omega_epk`](../../../../../omega_engine/crates_rs/omega_local_green_global_red_lggr/Cargo.toml),
in `omega_engine/crates_rs/omega_local_green_global_red_lggr`.
[`omega_wdp`](../../../../../omega_engine/crates_rs/omega_wdp/src/lib.rs)
provides WDP adapters; reusable finite report mathematics belongs to
[`omega_category_theory`](../../../../../omega_engine/crates_rs/omega_category_theory/src/lib.rs).
A directory or import is not proof that an application uses these checks.

## Evidence boundary

This index is a source map, not a certification of all six releases. Mathematical
proof, Lean theorem scope, compiler reproduction, exact finite computation,
numerical estimation, and production integration need separate evidence.
No test coverage percentage or publication-ready verdict is asserted here.
Preserved package manifests and historical archives retain their own provenance.
