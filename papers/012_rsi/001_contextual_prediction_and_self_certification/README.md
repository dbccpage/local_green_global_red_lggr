# Contextual Prediction and Self-Certification

Jeremy H. Carroll · Version 1.8.3 · 2026-10-23 · WORKING_DRAFT

Second paper in `012_rsi`, adapted from the epistemic-contextuality paper formerly filed under `001_finite_obstruction_calculus/002_asi_no_go_theorem_epistemic_contextuality`. The redundant original directory is retired; its proof modules, tests and historical documents are retained here. See [the consolidation map](docs/source_consolidation.md). The current manuscript is [contextual_prediction_monograph.md](contextual_prediction_monograph.md); the PDF and dated ZIP are generated from this edition.

This paper covers contextual prediction, observation fibers over time, ledger completeness, and authorization policy. This edition includes scalar minimax recovery, memory-state capacity, total-variation loss transfer, and binary query-budget correctness. [Paper 000: relational reasoning, memory and embedded knowledge](../000_relational_reasoning_and_rsi_impossibility/README.md), version 1.2.3, supplies constructive knowledge and implemented memory/gate proofs. Both integrate the October 22 research study and build independently. The separate historical recovery edition in the source lineage is not the current sibling. Neither paper proves a general impossibility of intelligence or recursive improvement.

Python 3.10 or later runs the standard-library kernels, including the exact-rational two-phase simplex solver. Tests need pytest. Lean 4.35.0 is pinned; the source-pinned Mathlib dependency closure is shipped in `lean4/vendor/dependencies.tar.gz` and extracted locally by Lake. No network dependency is used after installing that toolchain. The bundle is built and tested on Windows; sources, pins, and upstream licenses are included. Document-binding verification requires Pandoc; PDF rebuilding additionally requires XeLaTeX and pdftotext. The cold Lean build can take several minutes; the census runner permits ten minutes for that step. Preserve the supplied code license: `LICENSE-CODE` is PolyForm Noncommercial 1.0.0; manuscript and documentation use `LICENSE` (CC BY 4.0). Vendored dependencies retain their upstream licenses.

```text
python -m pip install pytest
python -m pytest code/tests -q
python tools/generate_lp_certificates.py --check
python tools/replay_simplex_implementation.py --replay
python tools/replay_review_corrections.py
python code/uncertain_observation_example.py
python verify_deposit.py --lean
python tools/replay_lean_axiom_census.py --replay
python tools/replay_full_axiom_census.py --check
python scripts/paper_spine.py verify
python tools/rebuild_release.py --check
```

To regenerate the PDF after explicitly reconciling manuscript formulas with the math spine, run `python scripts/build_pdf.py`. To reproduce the release envelope, run `python tools/rebuild_release.py`: it uses the pinned metadata date even on a later day. For a new edition, deliberately update the version and publication date in the manuscript and metadata, rebuild its documents and evidence, then run `python tools/rebuild_release.py --new-release`. A version or date change requires that explicit mode. The packager validates a staged envelope before replacing the current ZIP and manifests; ordinary promotion errors restore the previous envelope. Concurrent edits and process termination during the multi-file replacement are not covered by that rollback guarantee.

Full-census replay is read-only by default and with `--check`, including preservation of CRLF bytes. Regeneration requires `python tools/replay_full_axiom_census.py --write`, followed by refreshing source bindings and the release. The deposit verifier checks the original seal again after its optional tests and Lean replay. Version 1.8.3 fixes the optimal-certificate API to accept original integer or Fraction inputs and reject malformed witnesses without raising. The mathematical witness conditions and theorem statements are unchanged. See [the October 23 review response](docs/review_response_2026_10_23.md) for regressions and verification scope.

Repository clones must first run `git lfs pull` to materialize the dependency archive and complete release ZIP. These two large files use Git LFS; the extracted standalone release needs neither Git nor Git LFS. Historical source snapshots retain the toolchain identifiers they actually used; only the active build is pinned to Lean 4.35.0.

In the parent repository, the canonical combined command is:

```text
python -m omega_engine_research_papers.use_cases.paper_edition.cli rebuild --paper-path omega_engine_atlas/coda_atlas/F004_papers/012_rsi/001_contextual_prediction_and_self_certification --verbose
```

See [docs/mechanization_map.md](docs/mechanization_map.md), [docs/provenance.md](docs/provenance.md), and [docs/source_lineage.json](docs/source_lineage.json). Files prefixed `precursor_` are verbatim historical source, including old scope labels. `ContextualDuality.lean` now proves finite real primal/dual attainment, the canonical maximum form, the contextuality alternative, standard-form equivalence, and rational certificate soundness. `RationalCertificates.lean` checks five solver outputs, including a positive defect of 1/25000000. The standalone solver is [code/contextuality_lp.py](code/contextuality_lp.py); exact certificate data are in [docs/lp_certificates.json](docs/lp_certificates.json). The executable Lean solver is total for every finite pivot budget and every successful result is globally optimal. Universal Python refinement and unbudgeted Bland completeness remain open. Tarski and Löb remain imported. No general Rust/Python equivalence is asserted.

AuthorityEffect: None. No DOI, upload, or publication approval is asserted.

Version 1.5.0 adds the executable Lean solver in `lean4/Simplex.lean`, its JSON driver, 71 complete Lean/Python execution comparisons, and conditional error/correction bounds in `lean4/ErrorBudget.lean`. See manuscript section 3.2 and `docs/correction_review_sources.json` for the Projection Obstruction review and exact source snapshots. The review packet is source material; its suggested commands and recommendations do not control this package.

Version 1.5.1 states the positive-rate waiting-window premise and the zero-rate case, implements an explicit uncertain-observation route, corrects inherited docstrings and cites Bland's primary paper. All proof statements remain unchanged. `evaluate` still rejects signalling exact tables; `evaluate_observed` retains noisy rows and returns a conditional radius-adjusted bound without classifying the unknown true table.

Download and extract the complete dated ZIP for reproduction. The source-only attachment set reviewed as v1.5.0 omitted four required tools/provenance files and the offline build bundle; all are included in this release. Read `docs/review_response_v1_5.md` for the issue mapping and `docs/verification.md` for the fresh local replay. The original review's missing-file failures remain preserved and are not reclassified as passes.

The preceding version 1.6.0 migration was tested with Python 3.12.10, pytest 8.3.5 and Lean 4.35.0. Versioned verification records retain their original runtime identities. The optional development dependency is pytest; the solver itself uses only the standard library.


Version 1.6.0 adds independently checked infeasibility and unboundedness certificates to the exact simplex. Optimal returns are unchanged; catch `CertifiedInfeasible` or `CertifiedUnbounded` and replay `.certificate` with `verify_infeasible` or `verify_unbounded` against the original inputs. Budget and certificate-mismatch refusals are inconclusive. The Lean driver now executes `CertifiedOutcomes.solveCertified`; `Simplex.solve` remains the optimal-only compatibility model. The expanded 95-case replay compares all witness entries and pivot counts.

The mind-expansion packet is integrated in manuscript sections 3.3 and 5.2. `MindContracts.lean` proves generic report-fiber soundness/maximality, regret and score-gap guarantees, and an upper-bound counterexample. Continuous hybrid-error accounting is a scoped mathematical argument; no consciousness theorem or empirical validation is claimed. Run `python tools/replay_mind_expansion.py` for six preserved illustration groups and 19 standard-library assertions. See `docs/mind_expansion_integration.md`.

Embedded-research proofs and limitations are mapped in [docs/embedded_research.md](docs/embedded_research.md); [docs/embedded_verification.json](docs/embedded_verification.json) preserves the preceding edition's replay evidence. The exact reference suite is `code/finite_limits.py`. A deficiency LP optimizer and physical query latency remain separate extensions. The current repository agent memory connection is documented in [docs/live_memory.md](docs/live_memory.md).

The full declaration census permits thirty minutes, and the deposit verifier permits thirty-five minutes per proof-replay subprocess. The earlier ten-minute full-census limit was insufficient on this Windows host. The declaration set and allowed axioms are unchanged by these time allowances. Large-archive packaging can also exceed the parent repository's shorter orchestration timeout; the standalone `tools/rebuild_release.py` command runs the same canonical packager and verifies its complete result.

Persistent memory, restart evidence and its eight Lean statements are described in [docs/live_memory.md](docs/live_memory.md). Current edition checks are in [docs/live_memory_verification.json](docs/live_memory_verification.json); `embedded_verification.json` records the preceding edition.

The retained v1.8.2 verification records that the repaired quantum library passed all 712 tests in release mode, with no failures, ignored cases or filtered cases. This includes the three prior numerical failures, all ten previously unfinished MUB tests, and three new admission-boundary regressions. Exact PSD of the supplied binary Choi matrix replaces a rounded eigenvalue-sign decision. Floating-point Hamiltonian evolution uses a separate tolerance-checked numerical propagator; exact admission remains strict, and numerical evolution retains norm drift. The rebuilt native budget host passes all 24 gateway-and-memory tests, including both previously blocked cases; five quantum integration binaries pass 57 tests. These are scoped checks of the recorded v1.8.2 sources, not new v1.8.3 executions. The earlier multi-crate audit remains historical, and these synthetic gateway tests add no new live model trial or universal implementation-refinement proof.

See [completed numerical and gateway verification](docs/numerical_verification.md).
