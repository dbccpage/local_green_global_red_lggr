# Change Log: Relational Reasoning and the Bounded RSI No-Go Theorem (Paper 012-000)

## 1.1.0 — 2026-10-23

Integrated the memory and embedded-knowledge dossier. Added source-covered Lean proofs and exact finite checks, corrected the companion lineage and scoped impossibility claims, refreshed axiom censuses, rendered formats and standalone release. Historical source inventories remain historical. See [docs/embedded_research.md](docs/embedded_research.md).

All notable changes to this research paper package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

---

## [Unreleased] - 2026-10-17 (proposed 1.1.0; version bump, `zenodo_metadata.json` and release are the author's step)

### Added
- Monograph §7 "Quantum-Relational Horizon: Integrated Findings of the Five-Round Derivation Campaign (2026-10-17)": the Quantum Relational Universe definition, the Holevo report bound and report-alphabet horizon $k^* \le N + 1$, the stabilizer orbit bound under (H-STAB) with the corrected count $2^n\prod_{j=1}^n(2^j+1)$, purity dissipation under unital channels with its equality condition and the lift-budget horizon $k^* \le B_0 + 1$, Baker non-representability of $S_e(\operatorname{diag}(3/5,2/5))$ with two hand enclosures recorded as they stand, the edge-level and weighted gluing defects $\Phi_{\mathrm{glue}}$ and $\Phi_w$ replacing the vanishing $\sum|d^1 d^0 s|$, the Cabello and CHSH witnesses, latency and coverage-complex lemmas, no-self-tomography, the case-structured composite bound (Theorem Q.Master), terminal priority and routing annotations, and the round-5 proof-discharge status (`hclaim` repair; Mathlib-dependent Lean not elaborated here; Rust never compiled).
- Monograph §8 "A Theory of Knowing and Being for Finite Observers (Proposal)": four relational commitments B1–B4, the six terminals as the whole menu of knowing, Proposal L with ceilings L1–L4 and its corollary (the derivable limit), readings for an agentic swarm, a human being, and Bell's theorem as the cosmos-level gluing ceiling, with fences and the tests that would move it.
- Monograph §9 claim-hygiene summary for §§7–8.
- Claim ledger rows RSI-16 through RSI-37 (tags `[DEFINITION]`, `[STANDARD + citation]`, `[OPEN]`, `[IMPLEMENTATION CONTRACT]`, `[INTERPRETIVE]`, `[SCOPE FENCE]`; no new `[PROVED]` or `[VERIFIED]` rows).
- `docs/references.md` entries 11–23 for the imported theorems (Bell, CHSH, Tsirelson, Cabello et al., Abramsky–Brandenburger, Abramsky–Barbosa–Mansfield, Holevo, Baker, Aaronson–Gottesman, Eastin–Knill, Alberti–Uhlmann, Wootters–Zurek / Dieks, Kochen–Specker), each flagged as not yet verified against its publisher record.

### Changed
- Monograph header status line notes the unreleased revision; `README.md` and `docs/descriptions.md` ledger range updated to RSI-01 to RSI-37.
- `MANIFEST.sha256` and `SHA256SUMS` regenerated with `scripts/regen_sha256sums.py` for the edited text files. The dated release zip is untouched.

### Unchanged
- `lean4/` (40 theorems, zero custom axioms), `code/`, the 79-test suite, and every `[PROVED]` / `[VERIFIED]` claim RSI-01 through RSI-15.

### Provenance note
- The campaign rounds and this integration were drafted with language-model assistance under the project's claim-hygiene rules (`AuthorityEffect: None`); whether and how to disclose this in the released deposit is the author's decision.

---

## [1.0.0] - 2026-10-13

### Added
- Canonical monograph `relational_reasoning_and_rsi_impossibility_monograph.md` formalizing container-free relational ontology, pre-genesis operational transitions, relational alignment ("intelligence" in this model), Recursive Self-Improvement (RSI) dominance requirements, the Bounded No-Go Theorem, multi-agent communicating hypergraph product-carrier bounds, and higher $k$-cell cochain complexes ($C^k \xrightarrow{d^k} C^{k+1}$) with asynchronous message-delay buffers, packet-loss / non-FIFO out-of-order message permutation channels, and dynamic simplicial topology rewiring.
- Self-contained Lean 4 package under `lean4/` (`RsiImpossible.lean`, `RelationalRsiNoGo.lean`, `Census.lean`, `lakefile.lean`) providing 40 machine-checked theorems (including `coupled_product_carrier_capacity`, `coupled_coadaptation_joint_horizon_bound`, `higher_cochain_obstruction`, `asynchronous_delayed_joint_horizon_bound`, `dynamic_rewiring_higher_cochain_obstruction`, `non_monotonic_rewired_joint_horizon_bound`, `coupled_rsi_decouples_within_product_bound`, `coupled_rsi_impossible`, `asynchronous_coupled_rsi_decouples_within_product_bound`, `asynchronous_coupled_rsi_impossible`, `non_monotonic_rewired_rsi_decouples_within_product_bound`, and `non_monotonic_rewired_rsi_impossible`) with zero `sorry` placeholders and zero custom axioms.
- Executable Python and Rust companion harness (`code/rsi_transition_harness.py`, `code/rust_eis_companion.rs`, `code/eis_independence_vectors_v1.json`) instantiating single-agent `FiniteStateSelfModifyingGraph` ($k \le N + 1$), multi-agent `MultiAgentCommunicatingHypergraph` ($k \le N_A \cdot N_B + 1$) over `SharedTwoComplex` ($C^1 \xrightarrow{d^1} C^2$), and higher-dimensional `HigherCellAsyncCommunicatingHypergraph` over `HigherCellComplex` ($C^k \xrightarrow{d^k} C^{k+1}$) with `AsynchronousMessageDelayBuffer` ($\tau \ge 0$), `NonMonotonicMessageChannel` (packet loss and out-of-order permutations), and `DynamicSimplicialRewiringSchedule` (time-varying $(k+1)$-complexes), recording exact termination steps across `REPORT_COLLISION`, `LIFT_BUDGET_EXHAUSTION` (`budget = 0`), and `OVERLAP_GLUING_REFUSAL` ($\Phi_1([\delta^{(k)}]) > 0$), and cross-checking emitted refusal receipts against `omega_epistemic_immune_system`.
- Automated pytest verification suite `code/tests/test_rsi_impossible_lean_verification.py` (79 tests) and deterministic deposit verifier `verify_deposit.py`.
- Claim ledger `relational_reasoning_and_rsi_impossibility_claim_ledger.md` (Claims `RSI-01` through `RSI-15`), pure-Unicode scientific description `docs/descriptions.md`, and bibliography `docs/references.md`.

## Version 1.2.0 (2026-10-23)

Persistent source-checked memory, agent-context integration, restart and corruption tests, eight LiveMemory theorems, full axiom recensus and standalone rebuild. Both successful exact-use and failed arithmetic live trials are retained.

## Version 1.2.1 (2026-10-23)

The native budget host now builds offline from the repaired Rust sources. Both previously blocked gateway tests pass, and the full gateway-and-memory selection passes all 24 tests with no exclusions. The additional Rust library audit records 3687 passing, 3 failing, 13 ignored and 10 unfinished tests; five solver and five quantum integration binaries pass 89 tests. The three failures are floating-point quantum admission checks: the Choi identity example and two Hamiltonian propagator tests; they remain unresolved. Ten long-running MUB tests were stopped after about nine minutes and have no completed verdict in this run. The broad library audit also precedes concurrent edits in the shared checkout; the final host build and gateway rerun use the later checkout. These gateway checks use synthetic provider transports and the real native budget host. They do not add a new live model trial or establish universal implementation refinement. Refreshed both axiom censuses without changing theorem statements; rebuilt the rendered manuscript and standalone archive. The preceding verification report is retained under `docs/history/`.

## Version 1.2.2 (2026-10-23)

The repaired quantum library passes all 712 tests in release mode, with no failures, ignored cases or filtered cases. This includes the three prior numerical failures, all ten previously unfinished MUB tests, and three new admission-boundary regressions. Exact PSD of the supplied binary Choi matrix replaces a rounded eigenvalue-sign decision. Floating-point Hamiltonian evolution uses a separate tolerance-checked numerical propagator; exact admission remains strict, and numerical evolution retains norm drift. The rebuilt native budget host passes all 24 gateway-and-memory tests, including both previously blocked cases; five quantum integration binaries pass 57 tests. These are scoped current-source checks. The earlier multi-crate audit remains historical, and these synthetic gateway tests add no new live model trial or universal implementation-refinement proof.

Refreshed the existing named and full axiom censuses without changing theorem statements, rebuilt the manuscript, and rebuilt and verified the standalone archive. Detailed evidence: `docs/numerical_verification.json`.


## Version 1.2.3 (2026-10-23)

Reconciled all fourteen findings of the independent pinned-source review against
the integrated manuscript. Replayed its eight negative controls before editing.
Removed the false closedness certificate, added an independent exact checker,
made repair admission survive optimized Python, unified CLI and module code,
declared scientific dependencies and packaged native/JSON resources. Introduced
the shared ASCII identifier contract and explicit metadata-only native results.
Added five finite-prefix Lean results and four compiled reviewer scope controls
to both censuses. Clarified rank alignment, report counting, synthetic defect
injection and separation of cochain/probability/contextual-fraction LPs. Rebuilt
the paper and standalone package, preserving previous evidence outside the
active deposit. Earlier native and live-provider trials were not rerun.
