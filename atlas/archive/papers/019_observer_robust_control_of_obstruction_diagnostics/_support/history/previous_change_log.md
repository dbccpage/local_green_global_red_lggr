# Change Log: Observer-Robust Control of Obstruction Diagnostics (Paper 019)

All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## Repair record (2026-10-09)

Narrowed C01–C06 from `[VERIFIED]` to `[PROVED]` on the finite sentences that Lean 4 elaborates and the Python controller checks. Added `worstPhi`, `CeilingAdmitted`, `ceiling_bounds_each`, `excess_not_ceiling`, and `empty_not_jointly_adequate`. The closure ratio, absolute curvature, quotient linear program, and non-finite parameter checks stay controller fences. Version 2.1.1 and publication date 2026-10-08 are unchanged.

## [2.1.1] - 2026-10-08

### Added
- **Parameter and Shape Validation:** Added strict fail-closed validation in `ObserverModel` enforcing finite, strictly positive edge and boundary weights, finite non-negative resolution tolerances ($\varepsilon_{\mathcal{O}}$), matching $d_0$ row and $d_1$ column shapes, and non-negative projection indices.
- **Controller Bound Validation:** Validated `ObserverRobustController` parameters requiring positive non-NaN $R_{\max}$ and $M_{\max}$, non-negative non-NaN $\Gamma_{\max}$ and $\delta_{\Gamma}$, and finite non-negative $\lambda$ and $\epsilon$.
- **Subcomplex Projection Map:** Added `projection_indices` ($\pi_{\mathcal{O}}$) to `ObserverModel`, enabling observers to restrict evaluation to declared subcomplex coordinates.
- **SAT Channel Routing Support:** Extended `ObserverRobustController.evaluate_transition` to accept candidate transitions with explicit satisfaction channel obstruction $\Phi_{\mathrm{sat}}$, falling back to saturated residual $\min(\Phi_1^{\mathcal{O}}, 1.0)$ when omitted.
- **Expanded Test Suite:** Added 5 new unit tests (20 total) validating invalid observer parameter rejection, controller parameter validation, subcomplex coordinate projection, SAT channel routing selection, and bounded inter-subcomplex defect transfer under the initial budget.

### Changed
- **Narrowed Proposition 3.1 & Definition 2.2 Alignment:** Aligned monograph Definition 2.2 with Lean 4 coordinate coverage (`JointlyAdequate`); narrowed Proposition 3.1 to bounded coordinate diagnostics ($w_k |c'_k| \le \Phi_1(c) + \varepsilon_{\mathcal{O}}$) and aggregate descent, documenting that norm-reducing transfers between monitored subcomplexes are admitted without dedicated partition guardrails.
- **Claim Ledger Harmonization:** Synchronized claim ledger C01–C06 with the mechanized coordinate bounds in `JointDetectorAdequacy.lean`.
- **Full License Text:** Replaced 1-line stub with the full Creative Commons Attribution 4.0 International Public License in `LICENSE`.
- **Deposit Integrity:** Synchronized version 2.1.1 across all project files (`README.md`, `pyproject.toml`, `zenodo_metadata.json`, `docs/descriptions.md`, monograph, and claim ledger), regenerated checksums, and rebuilt release bundle.

## [2.1.0] - 2026-10-08

### Added
- **Joint Detector Adequacy:** Formalized Definition 2.2 requiring $\sum_{\mathcal{O}} (|\Delta \Phi_1^{\mathcal{O}}| + |\Delta \Gamma_2^{\mathcal{O}}|) > 0$ for non-trivial defect modifications; revised Proposition 3.1 to state that transfer prevention strictly requires joint detector adequacy, demonstrating the three-cycle unmonitored transfer counterexample.
- **Fail-Closed Validation of Finite Inputs:** Rejects candidates with `NaN` or infinite boundary/residual diagnostics or cost fail-closed in `ObserverRobustController.evaluate_transition`.
- **Empty Observer Bundle Protection:** `ObserverBundle` now strictly requires at least one observer model; controller refuses stalled if bundle is empty.
- **Piecewise Closure Ratio Boundary:** Formalized piecewise definition of $R_{cl}$: $\Gamma_2/\Phi_1$ for $\Phi_1 > \varepsilon_{\mathcal{O}}$, $0.0$ for $\Phi_1 \le \varepsilon_{\mathcal{O}}$ and $\Gamma_2 \le \varepsilon_{\mathcal{O}}$, and $\infty$ for $\Phi_1 \le \varepsilon_{\mathcal{O}}$ with $\Gamma_2 > \varepsilon_{\mathcal{O}}$.
- **Degree-Two Channel Typing:** Ensured that observers with 2-complex coboundary $d_1$ default to unit face weights matching $C^2$ dimension when face weights are omitted, supporting genuine one-face 2-cochains.
- **Extended Test Suite:** Added 5 new regression tests (15 total) validating empty bundle rejection, NaN candidate fail-closed refusal, genuine degree-two face curvature, piecewise $R_{cl}$ boundary handling, and joint detector adequacy counterexample.

### Changed
- Clarified that `evaluate_phi_1` solves the $\ell^1$ quotient linear program when coboundary $d_0$ is provided, and evaluates certified optimal residuals when $d_0$ is omitted.
- Synchronized version 2.1.0 across monograph, metadata, descriptions, change log, and claim ledger.

## [2.0.1] - 2026-10-07

### Added
- **Joint Observer Coverage:** Formalized Definition 2.2 requiring $\bigcap_{\mathcal{O} \in \mathfrak{O}} \ker(\pi_{\mathcal{O}}) \cap U = \{0\}$; narrowed Proposition 3.1 non-tearing property to monitored defect support and documented shared blind subspace limits.
- **Absolute Curvature Stability:** Added $\Gamma_2^{\mathcal{O}}(S_{t+1}) \le \Gamma_2^{\mathcal{O}}(S_t) + \delta_{\Gamma}$ and $\Gamma_2^{\mathcal{O}}(S_{t+1}) \le \Gamma_{\max}$ to Definition 3.1 and controller, preventing topological tearing where $\Phi_1$ drops while $\Gamma_2$ spikes.
- **Cochain Quotient Minimization:** Implemented exact $\ell^1$ coboundary quotient minimization $\min_{\alpha} \|\pi_{\mathcal{O}}(\omega_1) - d_0 \alpha\|_{1, \mathcal{W}}$ using HiGHS LP (`scipy.optimize.linprog(method='highs')`) in `ObserverModel.evaluate_phi_1`.
- **Dimension Separation:** Separated 1-cochain edge weights ($C^1$) from 2-cochain face boundary weights ($C^2$) with $d_1$ mapping, preventing shape errors on 2-complexes.
- **Worst-Case Ceiling ($M_{\max}$):** Added `m_max` guardrail to `ObserverRobustController` enforcing $\sup_{\mathcal{O}} \Phi_1^{\mathcal{O}} \le M_{\max}$.
- **Per-Observer Tolerances:** Transition checks evaluate per-observer `obs.tolerance` ($\varepsilon_{\mathcal{O}}$) rather than a global scalar.
- **Full Routing Objective:** Implemented $\mathcal{L}(o, S_t) = \sup \Phi_1 + \lambda \operatorname{avg}(\Phi_{\mathrm{sat}} + R_{cl}) + \operatorname{Cost}(o)$, favoring lower closure ratios under equal residual.
- **Extended Test Suite:** Added unit tests verifying exact cochain minimization ($\Phi_1=0$ on exact 1-cochains), $C^1 \neq C^2$ dimension separation, $M_{\max}$ ceiling enforcement, absolute curvature guardrail rejecting $(99,1) \to (0,50)$ tearing, and routing preference for lower $R_{cl}$.

### Changed
- Strictly positive weight enforcement in `ObserverModel` ($w_e > 0, w_f > 0$).
- Replaced zero weights in spoofing test fixture with strictly positive weights.
- Standardized `LICENSE-CODE` to complete Apache-2.0 license.
- Claim-disciplined abstract ("Verification suite and test fixtures demonstrate...") and claim ledger.
- Synchronized version 2.0.1 across monograph, metadata, pyproject.toml, README, descriptions, and claim ledger.
- `ObserverModel.evaluate_phi_1` and `evaluate_gamma_2` refuse vector length mismatches with `ValueError`.
- `verify_deposit.py` shared exclusions aligned with paper template; `scripts/regen_sha256sums.py` and `tools/rebuild_release.py` aligned.

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local local-first verification standards.
- Sovereign reference implementation `code/mod_observer_robust_control_core.py` modeling the observer bundle $\mathfrak{O}$, multi-observer residual evaluation, single-observer spoofing detection, minimax robust routing, and typed bundle refusals.
- Unit test suite `code/tests/test_observer_robust_control.py` validating the observer-robust control criterion, spoofing rejection, uniform descent, and bundle-wide refusal safety.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `observer_robust_control_of_obstruction_diagnostics_monograph.md`.
- Harmonized title with Zenodo record 20214468 (*Observer-Robust Control of Obstruction Diagnostics*).
- Purged internal house acronyms and promotional vocabulary.
- Enforced strict claim hygiene (`RULE[user_global]`).

## [1.0.0] - 2026-06-09

### Added
- Initial pre-print definition of observer bundles and robust control criteria.
