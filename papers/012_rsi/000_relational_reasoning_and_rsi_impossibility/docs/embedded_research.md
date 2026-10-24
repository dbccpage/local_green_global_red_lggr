# Embedded research: source and theorem map

Integrated for the 2026-10-23 editions from the October 22 research dossier. `embedded_integration.json` binds the verbatim shared Lean module, finite Python algorithms, thirteen-test suite and 23-source primary-literature catalog. The original dossier and its pre-integration baseline are unchanged. The current paired editions are paper 000 version 1.1.0 and paper 001 version 1.7.0.

| Result | Mechanization or executable evidence | Boundary |
| --- | --- | --- |
| Factivity, positive introspection, own-record determination | `EmbeddedLimits.lean`, twenty shared constructive theorems | Record-relative semantics in a declared model; no algorithmic omniscience |
| Exact decoder iff fiber constancy | Explicit representative construction in `EmbeddedLimits.lean` | Representative premise is explicit |
| Greatest stable future-readout equivalence | `future_eq_*`, `stable_relation_refines_future_eq` | Fixed readout and action family, every finite word |
| Memory update correspondence | Paper 000 `MemoryImplementation.run_updates_commute`, concrete pair encoding | Actual specified Lean updater; no universal Python refinement |
| Checked append and recall | Paper 000 `accepted_append_*`, `accepted_recall_sound`; `memory_machine.py` | Whole supplied archive; unstored possibilities need their own model |
| Enforced invariant preservation | Paper 000 `gated_run_preserves`, `concrete_gate_preserves_every_word` | Safe initial state and declared decidable invariant; runtime bypass excluded by definition |
| Attained scalar minimax | Paper 001 `EmbeddedQuantitative.attained_fiber_minimax`; `verify_fibers` | Explicit real bounds and attaining pair; finite scalar generator |
| Memory-state capacity | Paper 001 `future_classes_require_memory`; `memory_capacity` | Finite representative family and memory state space |
| Half-L1 bounded-loss transfer | Paper 001 `bounded_loss_tv`, `simulation_loss_transfer` | Equal mass, losses in [0,1], supplied simulation kernel/error |
| Correct binary budget recurrence | Paper 001 `QueryBudget.possible_iff_bounded_plan`, `checked_leaf_error` | Deterministic nondestructive binary queries; supplied sound leaf checker |
| Strict refinement termination | Paper 001 `informative_branch_card_lt`; finite Python search | Branch excludes a witnessed alternative; computation is not elapsed physical time |
| Adaptive two versus fixed three | Exact finite query fixture and independent optimality checker | Four declared worlds and three permitted queries |

The finite algorithms retain the scalar 31/2 witness, the one-to-two-bit action-extension example, 65,536 partition-versus-pair-search cases, 16,384 semantic determination cases, and adversarial certificate mutations. The Lean and Python programs remain separately scoped models. The preceding edition made no live model calls. The current persistent-memory experiment and its limits are documented in live_memory.md.

## Imported literature and remaining extensions

The inspected primary sources below inform the scope and constructive directions; their complete theorems are not imported into Lean merely by citation. Source URLs, versions and inspected locators remain in `embedded_literature.json`. A deficiency LP optimizer, a converse decision-comparison theorem, quantum channel recovery, statistical adaptive-confirmation guarantees, physical intervention safety remain separate work. A bounded live-agent persistence and injection experiment is now in live_memory.md.

- **wolpert2008** — [Physical limits of inference](https://arxiv.org/abs/0708.1362v2). Setup-distinguishable devices cannot mutually weakly infer one another. Particular tasks can remain inferable. Scope: The setup-distinguishability quantifier is essential; this is not a blanket ban on self-knowledge.

- **wolpert2018** — [Constraints on physical reality arising from a formalization of knowledge](https://arxiv.org/abs/1711.03499v3). Extends the physical inference framework to epistemic structures with observation, prediction and retrodiction. Scope: Imported framework; its defined devices must be related explicitly to an implemented agent.

- **shalizi2001** — [Computational Mechanics: Pattern and Prediction, Structure and Simplicity](https://arxiv.org/abs/cond-mat/9907176v2). Predictive causal states group pasts with the same future law and provide minimal predictive representations. Scope: Stationary-process and almost-sure qualifications; finite-data identification is an additional problem.

- **littman2001** — [Predictive Representations of State](https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html). Controlled predictive state can be represented through future-test probabilities. Scope: Representation existence is not an efficient learning guarantee or access to an unobserved physical state.

- **vanrooyen2014** — [Le Cam meets LeCun: Deficiency and Generic Feature Learning](https://arxiv.org/abs/1402.4884). Relates feature quality across decision problems to deficiency and reconstruction. Scope: Uses L1 variational divergence, twice half-L1 total variation; prior-weighted and uniform formulations differ.

- **tishby1999** — [The information bottleneck method](https://arxiv.org/abs/physics/0004057v1). Makes relevance-sensitive compression an explicit information-theoretic objective. Scope: A declared joint distribution and relevance variable are required; no automatic future-task guarantee.

- **strouse2016** — [The deterministic information bottleneck](https://arxiv.org/abs/1604.00268). Distinguishes deterministic compression objectives from standard information bottleneck optimization. Scope: An objective is not an independent semantic-sufficiency certificate.

- **scarlett2019** — [An Introductory Guide to Fano’s Inequality with Applications in Statistical Estimation](https://arxiv.org/abs/1901.00555). Converts information bounds into estimation lower bounds, including adaptive observations. Scope: Specify prior, hidden-index family and observation process; the coarse multiway bound can be vacuous for binary tests.

- **chen2022** — [Memory Bounds for Continual Learning](https://arxiv.org/abs/2204.10830). Worst-case continual-learning storage can grow with task count; revisiting tasks changes the attainable tradeoff. Scope: Hard-class, PAC and access assumptions matter; the result does not say every additional task needs new memory.

- **brown2022** — [Strong Memory Lower Bounds for Learning Natural Models](https://proceedings.mlr.press/v178/brown22a.html). Some sample-efficient one-pass learners need much more workspace than the final predictor description. Scope: Specified learning families and sample regimes; not a universal architecture-independent storage constant.

- **garrabrant2020** — [Logical Induction](https://arxiv.org/abs/1609.03543v5). A computable belief process satisfies qualified introspection, paradox resistance and future-self-trust guarantees. Scope: Sequence/asymptotic results under the deductive-process and efficient-trader framework; no efficient universal truth procedure.

- **fallenstein2015** — [Reflective Oracles: A Foundation for Classical Game Theory](https://arxiv.org/abs/1508.04145v1). Randomization at specified boundaries permits reflective oracle models without the corresponding deterministic diagonal contradiction. Scope: Oracle existence does not supply a physically implemented omniscient observer.

- **schmidhuber2006** — [Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements](https://arxiv.org/abs/cs/0309048v5). Describes self-rewrites justified relative to encoded machine, environment and utility assumptions. Scope: A useful proof need not be available; proof-system soundness and world-model adequacy remain premises.

- **demski2020** — [Embedded Agency](https://arxiv.org/abs/1902.09469). Maps problems for agents physically included in, and smaller than, their environment. Scope: Informal problem survey rather than a general no-go theorem.

- **legg2007** — [Universal Intelligence: A Definition of Machine Intelligence](https://arxiv.org/abs/0712.3329v1). Defines intelligence through performance weighted across an environment class. Scope: The environment prior, coding and value normalization are part of the definition.

- **leike2015** — [Bad Universal Priors and Notions of Optimality](https://arxiv.org/abs/1510.04931v1). Shows strong prior-dependence of proposed universal intelligence and optimality criteria. Scope: Does not invalidate concrete comparisons under a declared environment weighting.

- **howard2021** — [Time-uniform, nonparametric, nonasymptotic confidence sequences](https://arxiv.org/abs/1810.08240). Constructs confidence sequences valid uniformly over time under explicit observation-process conditions. Scope: Optional-stopping validity is not automatically preserved under arbitrary candidate selection or sample reuse.

- **dwork2015** — [Generalization in Adaptive Data Analysis and Holdout Reuse](https://arxiv.org/abs/1506.02629). Gives mechanisms for controlling generalization when analyses adapt to earlier data-dependent answers. Scope: A second evaluator identifier is not a substitute for the required statistical mechanism.

- **wu2026** — [Statistical Gödel Machines: From Formal Proofs to Risk-Controlled Self-Improvement](https://arxiv.org/abs/2510.10232v2). Conditionally valid confirmations with predictable summable allocations control trajectory-level false commitment. Scope: Read the September 2026 revision; opened failed confirmations count. Non-improvement control is not general action safety.

- **abramsky2011** — [The Sheaf-Theoretic Structure Of Non-Locality and Contextuality](https://arxiv.org/abs/1102.0264v7). Characterizes specified contextual empirical models through obstructions to suitable global sections. Scope: Do not identify every observation collision or triangle-cochain residual with contextuality.

- **rovelli1996** — [Relational Quantum Mechanics](https://arxiv.org/abs/quant-ph/9609002v2). An interpretive precedent for treating observers as physical systems. Scope: Interpretive context, not a proof of the complete working ontology or a premise needed for the classical results.

- **angluin1987** — [Learning Regular Sets from Queries and Counterexamples](https://doi.org/10.1016/0890-5401(87)90052-6). Exact learning becomes possible with specified membership and equivalence-query access. Scope: A practical agent must implement or justify the teacher resource before importing the guarantee.

- **buscemi2011** — [Comparison of quantum statistical models: equivalent conditions for sufficiency](https://arxiv.org/abs/1004.3794v4). Provides quantum statistical-model comparison conditions relevant to physically admissible memory recovery. Scope: Restricted classical decision tests must not be conflated with complete positivity; retain the exact ancillary/completeness conditions.
