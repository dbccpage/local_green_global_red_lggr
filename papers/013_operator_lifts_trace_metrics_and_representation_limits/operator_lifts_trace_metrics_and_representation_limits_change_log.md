# Change Log: Operator Lifts Trace Metrics and Representation Limits (Paper 013)

## Version 2.1.1 — 2026-10-23

- Prepared republication metadata and reader-facing artifacts for this date.
- Retained mathematical claims, proof scope and the Lean 4.35.0 pin.
- Preserved the pre-preparation package outside the new deposit. No upload or new DOI is asserted.

## 2.1.0 — 2026-10-16 (prepared edition)

Completed the fixed-mass sign-selection proof, including continuity of the sign coefficient and restriction to a two-dimensional subspace. Scoped numerical stability claims to floating-point limitations. Added a bibliography and removed the inherited Ricard citation whose arXiv identifier resolves to an unrelated work.

Revised mathematical scope and presentation; introduced the canonical Markdown math spine with persistent equation IDs and occurrence bindings; regenerated TeX, math-preserving text, and PDF through ordered formula checks. The build records file digests and does not assign mathematical truth. Existing public deposit identifiers are retained as prior-record references, not asserted as identifiers for this prepared edition.


All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

---

## Repair record (2026-10-09)

Narrowed C01–C04 and C06–C07 to the finite integer and rational statements mechanized in `lean4/Lifts.lean` and checked by `OperatorLifts.integer_trace_norm`, `normalized_abs_weights`, `cleared_homogeneous_pair`, `squared_trace_gap`, `GuardedDescentEvaluator.exact_admits`, and `exact_compare`. The Mazur square root, the real punctured line, the chain-complex bound, and the square-root metric triangle inequality stay classical readings. C05 is a negative boundary. Version and publication date are unchanged.

## [2.0.3] - 2026-10-08

### Added
- Specific attribution of the signed square-root coordinate map $v \mapsto \psi(v)$ to the classical Mazur map $M_{1,2}$ (Mazur 1929, Ricard 2013) in monograph §4, code docstrings, and bibliography (`docs/references.md`).
- Monograph Proposition 4.2 proving that the density quotient preserves normalized homogeneous diagnostics $N(v)/\|v\|_1$ for all absolutely homogeneous seminorms $N$, including $\Phi_1(v)/\|v\|_1$, $\Gamma_2(v)/\|v\|_1$, and the ratio $\Gamma_2(v)/\Phi_1(v)$, as well as exactness and closedness.
- Monograph Theorem 4.3 establishing local reconstruction charts $U_\ell = \{\rho : \ell(v) \ne 0\}$ and proving the topological obstruction to a globally continuous antipodal sign selection map in dimension $m \ge 2$.
- Monograph Proposition 2.2 establishing the chain complex compatibility bound $\Gamma_2(v) \le \|d_1\|_{1\to 1} \Phi_1(v)$ for complexes with $d_1 d_0 = 0$, proving exact $\Phi_1(v) = 0 \implies \Gamma_2(v) = 0$, and clarifying the numerical-threshold nature of infinite curvature fixtures.
- Regression unit tests in `code/tests/test_operator_lifts.py`:
  - `test_quotient_equality_and_hash_consistency_with_zero_coordinates`: verifies that antipodal inputs with zero coordinates compare equal, hash identically, and deduplicate to a single element in sets.
  - `test_trace_distance_preserves_triangle_inequality_without_near_identity_clipping`: verifies the metric triangle inequality on the $v(t) = (\cos^2 t, \sin^2 t)$ family at scale $\theta = 10^{-7}$.
  - `test_reconstruction_rejects_mixed_states_outside_rank1_image`: verifies strict rejection of mixed states ($\frac{1}{2} I_2$), asymmetric matrices, and non-unit trace inputs.
  - `test_reconstruction_rejects_orthogonal_and_nonfinite_anchors`: verifies that orientation anchors must satisfy $\ell(v) \ne 0$ and strictly rejects orthogonal vectors and non-finite values.
- Regression integration tests in `code/tests/test_guarded_descent_integration.py`:
  - `test_comparator_transitivity_no_preference_cycles`: verifies strictly transitive candidate comparison without preference cycles on the reviewer's theta complex reproduction case.
  - `test_ratio_guard_consistent_between_transition_and_comparison`: verifies consistent enforcement of the hard ratio ceiling $R_{\mathrm{cl}} \le r_{\max}$ across transition evaluation and pairwise comparison.
  - `test_zero_cochain_clean_closure_integration`: verifies native handling of zero cochains and clean-closure termination before density diagnostics.
  - `test_chain_complex_compatibility_bound_and_exact_closure`: verifies $d_1 d_0 = 0$ and $\Gamma_2 \le \|d_1\|_{1\to 1} \Phi_1$ on cell complexes.

### Changed
- `GuardedDescentEvaluator.compare_candidates`: implemented strictly transitive lexicographical total ordering on stored finite values, eliminating cyclic epsilon-tie defects.
- `GuardedDescentEvaluator.rank_candidates`: implemented true priority sorting of candidates (admissible candidates first, ordered by selection priority), and added `evaluate_candidates` to preserve original input order for annotated evaluations.
- `GuardedDescentEvaluator.evaluate_transition`: aligned with `compare_candidates` by evaluating the hard ratio ceiling $R_{\mathrm{cl}} \le r_{\max}$ prior to descent acceptance.
- `DiagnosticState`: added consistency validation between $\Phi_1$, $\Gamma_2$, and $R_{\mathrm{cl}}$, preventing contradictory diagnostic tuples.
- `OperatorLifts.trace_distance`: replaced near-identity clipping cutoff with the equivalent stable expression $\Xi(a, b) = \frac{1}{2} \|a - b\|_2 \|a + b\|_2$, eliminating cancellation error near identity without violating the triangle inequality.
- `DensityOperator.__init__`: normalized accepted near-unit state vectors to exact unit norm, and canonicalized signed zeros (`-0.0` -> `+0.0`) strictly after representative gauge fixing to ensure byte-hash consistency with numerical equality.
- `OperatorLifts.attempt_reconstruction`: enforced real rank-1 orthogonal projector domain verification ($\rho^\top = \rho, \rho^2 = \rho, \operatorname{Tr}\rho = 1$, finite entries) and postcondition verification (admitted mass recovery and re-lift agreement).
- `DiscreteComplex.evaluate_state`: added native exact branch for zero cochains, preventing undefined density lift exceptions on clean closure.
- Updated claim ledger (added C06 and C07, expanded C03 and C04) and package documentation.

## [2.0.2] - 2026-10-08

### Added
- Reference `GuardedDescentEvaluator` and `DiagnosticState` in `code/mod_operator_lifts_core.py`, implementing the declared selection priority ($\Phi_1 \succ \Gamma_2 \succ \Xi$), piecewise $R_{cl}$ boundary guardrails, strict non-increase fences, and multi-candidate comparison and ranking.
- Integration test suite `code/tests/test_guarded_descent_integration.py` (8 test cases) validating evaluator orderings on discrete graph instances:
  - Primary dominance of $\Phi_1$ over $\Xi$ on discrete Theta graph $\Theta$.
  - Secondary dominance of $\Gamma_2$ over $\Xi$ on tied $\Phi_1$ states.
  - Tertiary decisiveness of $\Xi$ on tied $(\Phi_1, \Gamma_2)$ states.
  - Guardrail refusal when $R_{cl} > r_{\max}$ despite favorable $\Xi$.
  - Infinite curvature branch rejection when $R_{cl} = +\infty$.
  - Fail-closed non-increase fence rejecting sub-epsilon creep in $\Phi_1$.
  - Antipodal blindness ($\Xi(v, -v) = 0$) proving that continuous spectral metrics cannot replace combinatorial orientation.
  - Multi-candidate ranking across competing cochain proposals on a cell complex.
- Regression unit tests in `code/tests/test_operator_lifts.py` covering:
  - Large finite inputs near float64 limits (`[1e308, 1e308]`) without overflow.
  - Rejection of invalid, nonfinite, or nonpositive admitted mass (`nan`, `inf`, `-1.0`, `0.0`).
  - Trace distance numerical stability on identical states and antipodal pairs ($\Xi = 0.0$ exactly).
  - Reconstruction directly from raw 2D density matrices without wrapper classes.
  - Antipodal collision ($\Xi(v, -v) = 0$), candidate pair reconstruction $\{v, -v\}$ with admitted mass, resolution with orientation anchors, rejection of unnormalized state vectors in direct `DensityOperator` construction, and small-mass cochains ($10^{-13}$).
- Complete Apache-2.0 and MIT license texts in `LICENSE-CODE`, aligned with `zenodo_metadata.json` dual licensing.

### Changed
- Monograph §2 and claim ledger updated to verify the declared selection priority (Claim C04) via the reference `GuardedDescentEvaluator` and discrete graph integration tests.
- Monograph §4 and §5 amended to state the full punctured 1D line fiber $F_{\mathrm{den}}^{-1}(\rho(v)) = \{c \cdot v : c \in \mathbb{R} \setminus \{0\}\}$, antipodal reconstruction barrier $\{v, -v\}$ under admitted mass, and characterization of $\Xi$ as a pseudometric on nonzero cochains and metric on the real projective quotient space $\mathbb{P}(C^1(P; \mathbb{R}))$.
- Introductory diagram line 45 corrected to include factor $1/2$ ($\Xi = \frac{1}{2} \operatorname{Tr}|\rho_1 - \rho_2|$).
- Replaced promotional vocabulary throughout the package ("Combinatorial Primary Doctrine", "primary authority", "sovereign feasibility boundaries", "Hilbert-Lift Quarantine", "No Reverse Teleology") with direct mathematical and methodological phrasing ("the declared selection priority", "scope of the operator construction", "combinatorial feasibility boundaries").
- Narrowed abstract to clarify that $F_{\mathrm{lin}}$ is an isometric and injective embedding in the canonical edge basis (no information loss), while $F_{\mathrm{den}}$ is the source of intentional scale and orientation abstraction.
- `DensityOperator` enforces unit $L^2$ norm ($\text{trace} = 1 \pm 10^{-7}$) on direct construction and canonicalizes representative gauge; `@property` methods return read-only defensive copies to prevent post-construction hash mutation.
- `OperatorLifts.density_lift` normalized by `max_abs` to prevent overflow on inputs up to float limits, and accepts small-mass cochains down to float underflow limits.
- `OperatorLifts.attempt_reconstruction` validates finite positive mass and operates directly on density matrix entries, returning candidate pair `(v_pos, v_neg)` or resolving with orientation anchors.
- `OperatorLifts.trace_distance` uses stable calculation $(1 - |\text{overlap}|)(1 + |\text{overlap}|)$ and exact short-circuit for identical operators to avoid cancellation error.
- Harmonized release version 2.0.2 across all package manifests, metadata, documentation, and source headers.

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local-first verification standards.
- Reference implementation `code/mod_operator_lifts_core.py` modeling linear trace embeddings $F_{\mathrm{lin}}$, nonlinear density lifts $F_{\mathrm{den}}$, the Lossy Collision Principle, and reconstruction obstruction.
- Initial unit test suite `code/tests/test_operator_lifts.py`.
- Documentation in `docs/descriptions.md` and bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `operator_lifts_trace_metrics_and_representation_limits_monograph.md`.
- Harmonized title with Zenodo record 20213629 (*Operator Lifts Trace Metrics and Representation Limits*).

## [1.0.0] - 2026-06-09

### Added
- Initial pre-print definition of operator lifts and spectral representation geometry.
