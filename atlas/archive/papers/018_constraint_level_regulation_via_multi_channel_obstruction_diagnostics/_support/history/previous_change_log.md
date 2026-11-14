# Change Log: Constraint-Level Regulation via Multi-Channel Obstruction Diagnostics (Paper 018)

All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

---

## Repair record (2026-10-09)

Narrowed C01–C05 to the rational signature fence, the piecewise ratio, the $\varepsilon$-band selection clauses, the lift inequality, and the refusal tags mechanized in `lean4/Regulate.lean` and checked by `RepairSelectionController.exact_signature_ok`, `exact_ratio_admits`, `exact_lift_admitted`, `exact_discrete_score`, and `exact_select`. The operator-norm bound and asymptotic convergence stay classical. Version and publication date are unchanged.

## [2.0.2] - 2026-10-08

### Fixed
- **Global $\varepsilon$-Optimal Ranking Policy (Elimination of Pairwise Cycles):** Replaced pairwise comparison sort with global set-based selection ($F_{\min} \to \mathcal{C}_\varepsilon \to \Xi_{\min} \to \mathcal{T}_\varepsilon \to \text{deterministic tie-break}$). Eliminated cyclic preference loops ($A \prec B \prec C \prec A$) and proposal-order permutation dependencies across all input orderings.
- **Literal Non-Increase Guarded Descent & Score Priority Reconciliation:** Enforced strict non-increase relative to current state ($\Phi_{\mathrm{geom}}(S') \le \Phi_{\mathrm{geom}}(S_t)$), reconciling controller composition with Paper 009. Clarified in monograph and ledger that within the measurement resolution band $\varepsilon$, discrete scores are treated as numerically tied, allowing $\Xi$ to break ties, while candidates outside this band ($F_{\mathrm{discrete}} > F_{\min} + \varepsilon$) can never be selected by favorable $\Xi$.
- **Exact Hard Boundary for $R_{\max}$:** Removed tolerance relaxation from boundary stability gate ($R_{cl} \le R_{\max}$), strictly aligning implementation with Invariant 3.1.
- **Fail-Closed Contradictory Signature Rejection & Overflow Defense:** Validated cochain signatures to reject mathematically unrealizable configurations ($\Phi_1 = 0$ with $\Gamma_2 > 0$, violating $\Gamma_2 \le \|d_1\|\Phi_1$) and convention violations ($\Phi_1 = 0$ with $\Xi > 0$). Added fail-closed checks against discrete score floating-point overflows to infinity.
- **Completed Typed Refusal Taxonomy:** Emitted explicit typed refusals (`RefusedTearing`, `RefusedDescentViolation`, `RefusedInvalidInput`, `RefusedStalled`) and recorded individual operator failure reasons in `diagnostics["rejections"]` and `diagnostics["rejection_counts"]`.
- **Licensing and Metadata Harmonization:** Included full legal text for Creative Commons Attribution 4.0 International (`LICENSE`) and MIT License (`LICENSE-CODE`). Reconciled `zenodo_metadata.json` code license note to "MIT".

## [2.0.1] - 2026-10-07

### Mathematical Corrections
- Corrected Proposition 2.1: replaced blanket channel independence with the proven cochain bound $\Gamma_2(\omega) \le \|d_1\|_{1 \to 1} \Phi_1([\omega])$, proving $\Phi_1 = 0 \implies \Gamma_2 = 0$. Replaced unrealizable test fixture ($\Phi_1=0, \Gamma_2=2$) with realized finite cochain configurations.
- Narrowed the closure ratio claim: documented that $R_{cl}$ is a scalar filter that does not detect or prevent constraint/edge deletion (e.g. triangle-to-path collapse); explicitly stated that constraint preservation requires a separate verification check.
- Resolved $\Xi$ selection rule: replaced weighted objective term with strict lexicographic tie-breaking ($F_{\mathrm{discrete}}$ dominates; $\Xi$ breaks ties only when discrete scores match within $\varepsilon$), eliminating the failure mode where a candidate with larger geometric residual is chosen due to lower trace metric.
- Completed definitions: added explicit formula for relational interface drift $\Phi_{\mathrm{rel}}$, declared the $\Xi = 0$ convention for exact cochains ($\Phi_1 = 0$), and defined the parameterization of the lift law $\Delta_\Lambda$.
- Removed unsupported outcome claims: excised diagnostic entropy, certified convergence claims, and broad empirical assertions.
- Replaced promotional prose with concrete technical descriptions (e.g. "repair-selection controller", separate candidate selection from transition verification).

### Implementation Fixes
- Fixed tolerance bug: controller's configured $\varepsilon$ is now uniformly used for candidate $R_{cl}$ calculation and admission filtering, rather than being overridden by the state property's hardcoded $10^{-9}$.
- Fixed non-finite input validation: added fail-closed checks rejecting `NaN`, infinite, negative, or out-of-range diagnostic inputs and invalid controller policy parameters.
- Renamed controller to `RepairSelectionController` with backward-compatible alias `SecondOrderRepairController`.
- Synchronized version designation across all package files to `2.0.1`.


## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local local-first verification standards.
- Sovereign reference implementation `code/mod_constraint_regulation_core.py` modeling the 5-channel diagnostic vector, piecewise closure ratio $R_{cl}$, second-order repair controller, cost-sensitive lift law $\Delta_\Lambda$, and typed refusal emission.
- Unit test suite `code/tests/test_constraint_regulation.py` validating channel separability, $R_{cl}$ tearing rejection, cost-sensitive selection, and fail-closed refusal safety.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `constraint_level_regulation_via_multi_channel_obstruction_diagnostics_monograph.md`.
- Harmonized title with Zenodo record 20214310 (*Constraint-Level Regulation via Multi-Channel Obstruction Diagnostics*).
- Purged internal house acronyms and promotional vocabulary.
- Enforced strict claim hygiene (`RULE[user_global]`).

## [1.0.0] - 2026-06-09

### Added
- Initial pre-print definition of multi-channel state vector and second-order repair controller.
