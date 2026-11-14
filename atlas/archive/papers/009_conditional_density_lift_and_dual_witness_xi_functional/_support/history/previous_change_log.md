# Change Log: Conditional Density Lift and Dual-Witness Xi Functional (Paper 009)

All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## Repair record (2026-10-09)

- Mechanized the finite integer and rational content of C01–C05 in Lean 4 (`lean4/Xi.lean`) and in exact methods on the shipped Python classes. The square-root trace norm and the compactness argument for successive minimization remain classical readings in the monograph.
- Marked C06 as a negative boundary. It is a non-claim.
- Version 2.0.3 and publication date 2026-10-08 are unchanged.
- The proved rows name `weights_sum_to_one`, `weight_scale_cross`, `cauchy_gap_nonneg`, `dual_mass_at_least_one`, `forced_sign`, `zero_mass_convention`, and the four admissibility gates.
- C03 names `test_proved_finite_integer_and_rational_claims`, which calls `integer_cauchy_gap`.

## [2.0.3] - 2026-10-08

### Fixed
- **LP Solver Integration and Certification Boundary:** Replaced unverified labeling of near-exact LP results with `certify_canonical_primal_dual_pair`, explicitly verifying primal feasibility ($\|r_{\text{primal}}\|_\infty / \text{scale} \le 10^{-6}$), dual feasibility ($\|B^T \phi^*\|_\infty \le 10^{-6}$, $\|\phi^*\|_\infty \le 1 + 10^{-6}$), and certified duality gap ($|P - D| \le \text{tol}_{\text{abs}} + \text{tol}_{\text{rel}} \max(P, D)$). Added test verifying that tolerance-level defects ($5\times 10^{-8}$ defect on oriented triangle) are flagged as numerically uncertain rather than erroneously labeled canonical when primal and dual objectives diverge.
- **Safe Finite-Input Normalization:** Scaled inputs by maximum absolute coordinate before summing in `ConditionalDensityLift.lift`, preventing float64 overflow on large inputs (e.g. `lift([1e308, 1e308])`). Added strict input rejection for nonfinite (`NaN`, `Inf`) and empty vectors. Added explicit unit 2-norm and positive finite mass validations in `DensityLift.__post_init__`.
- **Zero-Obstruction Certificate Separation:** Separated verified zero obstructions from caller assertions by introducing `ZeroObstructionCertificate` requiring an explicit boundary certificate $B \alpha = \omega$ with checked residual $\|B \alpha - \omega\|_\infty \le \text{tol}$. Replaced caller parameter `certified_zero` with `zero_certificate: ZeroObstructionCertificate | None` and explicit `unverified_override: bool = False`, strictly enforcing the paper's $\Xi = 0.0$ operational convention.
- **Evaluator State Validation:** Added explicit pre-validation of all state diagnostics (checking finite, non-negative, and $\Xi \le 1.0$) and thresholds ($r_{\max} > 0$, $\epsilon \ge 0$) in `GuardedEvaluator.is_admissible_transition` before branching, immediately rejecting invalid candidates such as `(0, NaN, NaN, NaN)`.
- **Licensing and Metadata Harmonization:** Included full legal text for Creative Commons Attribution 4.0 International (`LICENSE`) and MIT License (`LICENSE-CODE`). Reconciled `zenodo_metadata.json` code license to "MIT".

## [2.0.2] - 2026-10-08

### Fixed
- **Domain Inequality in Definition 4.1:** Replaced false domain comparison $\|\varphi^*\|_1 \ge \Phi_1$ with exact bound $\|\varphi^*\|_1 \ge 1 > 0$, proved via $\|\varphi^*\|_\infty = 1$ under LP strong duality ($\Phi_1 = \langle \varphi^*, h^* \rangle \le \|\varphi^*\|_\infty \|h^*\|_1 = \|\varphi^*\|_\infty \Phi_1 \implies \|\varphi^*\|_1 \ge \|\varphi^*\|_\infty = 1 > 0$).
- **Strict Non-Increase Fences in Evaluator:** Corrected `GuardedEvaluator.is_admissible_transition` and Monograph §5 to enforce literal non-increase: candidate transitions with $\Phi_1(S') > \Phi_1(S)$ or $\Gamma_2(S') > \Gamma_2(S)$ on tie-break are strictly rejected, preventing sub-epsilon creep ($\Phi_1(S') = \Phi_1(S) + 5 \cdot 10^{-10}$) from being accepted on favorable $\Xi$.
- **Zero-Obstruction Threshold Erasure & Uncertainty Handling:** Updated `ConditionalDensityLift.compute_xi` so that small positive obstructions are not falsely collapsed to $\Xi = 0$. Required exact zero cochain (`mass == 0.0`) or explicit `certified_zero=True` to invoke the operational zero-obstruction convention. Defaulted `tolerance=0.0` in `lift` and `compute_xi` to preserve scale invariance down to IEEE 754 underflow limits. Explicit positive tolerances without zero certification raise `ValueError` to treat numerical uncertainty as an explicit condition.
- **LP Integration Relative Scaling:** Updated `solve_canonical_primal_dual_pair` in `test_lp_solver_integration.py` with relative scale normalization ($\|\omega\|_\infty$), ensuring well-conditioned LP solutions and preserving scale invariance for small positive scalings (e.g. $\omega = (0, 0, 10^{-13})$ on oriented triangle yields $\Phi_1 = 10^{-13}$ and $\Xi = \sqrt{2/3}$) while distinguishing exact coboundaries.

### Changed
- **Claim Ledger Disambiguation:** Restructured `conditional_density_lift_and_dual_witness_xi_functional_claim_ledger.md` to cleanly separate exact analytical propositions from float64 implementation checks across all claims (C01–C06).
- **Test Suite Enhancements:** Added test cases in `code/tests/test_conditional_density_lift.py` and `code/tests/test_lp_solver_integration.py` covering sub-epsilon creep rejection, small positive obstruction preservation ($\Xi = \sqrt{2/3}$ on triangle with $h^* = (0, 0, 10^{-13})$), scale invariance across small positive scalings, and explicit numerical uncertainty exceptions.
- Synchronized version 2.0.2 across monograph, claim ledger, README, metadata, pyproject.toml, and descriptions.

## [2.0.1] - 2026-10-07

### Added
- Explicit zero-obstruction domain specification in Definition 4.1 and `compute_xi`: for unobstructed classes ($\Phi_1 = 0$), density lift is undefined and $\Xi = 0.0$ by declared operational convention.
- Canonical representative selection in Section 3 via successive coordinate minimization over compact optimal faces $\mathcal{H}^*$ and $\mathcal{W}^*$ relative to declared edge ordering $e_1 < \dots < e_m$, addressing non-attainment failure of support-first lexicographic ordering.
- Analytical optimal-pair bounds in Proposition 4.2: proved $\Xi \le \sqrt{1 - 1/\|\varphi^*\|_1} \le \sqrt{1 - 1/m} < 1$, precluding orthogonality ($\Xi = 1$) for optimal pairs; characterized exact zero-distance condition $\Xi = 0$ as requiring magnitude uniformity across matching support in addition to sign agreement.
- Unit test `test_zero_obstruction_domain_and_convention` verifying $\Phi_1 = 0$ handling.
- Unit test `test_optimal_pair_bounds_and_strictly_sub_unitary` verifying strictly sub-unitary optimal-pair bounds and the cyclic triangle magnitude-non-uniformity example ($\Xi \approx 0.16910198 > 0$).
- Unit tests validating full tiered priority admission policy and tolerance gating in `GuardedEvaluator`.
- End-to-end integration test suite `code/tests/test_lp_solver_integration.py` pairing an external LP solver (successive coordinate minimization) with `compute_xi` across non-trivial connected cycle topologies (Figure-Eight, Theta, Dumbbell, Complete $K_4$, and disjoint triangles).

### Changed
- Aligned Section 5 prose and `GuardedEvaluator` implementation to tiered priority admission with threshold gating ($\Phi_1 \to \Gamma_2 \to (R_{cl} \text{ gate}, \Xi \text{ tie-breaker})$), explicitly documenting that $R_{cl} \le R_{\max}$ gates candidate admission at the $\Xi$ stage rather than forming a 4-coordinate lexicographical ordering.
- State vector canonicalization in `DensityLift` (float64, contiguous, read-only, +0.0) with exact-type equality and byte-level hash.
- Corrected representation terminology: replaced "mass-preserving embedding" with normalized square-root map into rank-1 density matrices that preserves normalized absolute coordinate weights and real amplitudes without independent phases; noted total mass and common global sign are discarded.
- Purged institutional and sovereign vocabulary ("sovereign", "foundational doctrine", "supremacy", "authority notice") across manuscript, docstrings, ledger, descriptions, and metadata.
- Updated Claim Ledger C04, C05, and C06: distinguished prose proofs from numerical tests, replaced unattainable optimal-pair endpoint claim, and clarified `verify_deposit.py` structural checks.
- Synchronized release version 2.0.1 across monograph, claim ledger, README, metadata, pyproject.toml, and descriptions.
- `verify_deposit.py` aligned with paper template; `tools/rebuild_release.py` registers `deposit_paths` in `sys.modules`.

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local-first verification standards.
- Reference implementation `code/mod_conditional_density_lift_core.py` modeling the conditional density lift, pure-state trace distance, and secondary $\Xi$ tie-breaker in NumPy float64 floating-point arithmetic.
- Unit test suite `code/tests/test_conditional_density_lift.py` validating unit trace, scale invariance, pure-state trace distance, $\Xi$ boundary conditions, and evaluator subordination.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `conditional_density_lift_and_dual_witness_xi_functional_monograph.md`.
- Harmonized title with Zenodo record 20192297 (*Conditional Density Lift and Dual-Witness Xi Functional*).
- Purged internal house acronyms and promotional vocabulary.
- Enforced strict claim hygiene (`RULE[user_global]`).

## [1.0.0] - 2026-06-09

### Added
- Initial pre-print extraction of density lift and $\Xi$ tie-breaking functional.

