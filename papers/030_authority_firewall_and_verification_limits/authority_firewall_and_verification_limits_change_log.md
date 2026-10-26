# Change Log: The Authority Firewall and Verification Limits (Paper 030)

All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## 2026-10-09 — Finite calibration completeness checked

AVF-030-C11 remains the proved theorem. `lean4/Calibration.lean` verifies agreement on a hitting set of representatives if and only if the class-constant specification and detector agree on the carrier, and establishes that flipping one missed block is a class-constant counterexample. `code/proved_rows.py` calls `FinitePartitionCoverage` on the five-point, three-class residual. OBL-AVF-01 is discharged. OBL-AVF-02 and OBL-AVF-03 stay open. This is not a new Zenodo deposit.

## [2.2.0] - 2026-10-08

### Added
- **Finite Calibration Completeness Theorem (§2.4):** Formalized and proved the theorem stating that under declared class-constancy of ground-truth specification $A$ and detector $D$ on equivalence partition $X / \sim$, global agreement $D = A$ holds if and only if $D(r) = A(r)$ for all representatives $r \in R$.
- **Sharp Coverage Bound & Counterexample Generator:** Proved that partition coverage is sharp, and implemented `FinitePartitionCoverage.construct_omitted_class_counterexample` which deterministically constructs a class-constant counterexample detector whenever any partition class is omitted.
- **Sealed Authority Witness Defense (§4.2):** Sealed `AuthorityWitness` with private capability token `_SOVEREIGN_TOKEN`, preventing direct untrusted construction, empty witnesses, arbitrary mocks (`object()`), and uncertified payloads from bypassing verification gates.
- **Bundled Master Demo Runner (§7.4):** Implemented `run_master_demo_scenarios()` in `code/mod_verification_limits_core.py`, providing a pinned, self-contained runner for 7 distinct operational scenarios (C1, O1–O7) without relying on external or dead repository paths.
- **Unit Test Suite Expansion:** Expanded `code/tests/test_verification_limits.py` to 11 unit tests, adding `test_witness_forgery_defenses_and_object_bypass`, `test_finite_calibration_completeness_and_sharp_coverage_bound`, and `test_master_demo_seven_scenarios`.

### Changed
- **Capability Non-Constructibility Scoping (§3.1):** Clarified the mathematical distinction between set-theoretic constant functions and unprivileged programming capability boundaries, scoping non-constructibility to unprivileged execution contexts under object-capability security, citing Rust `HostPromotionCapabilityV1`.
- **Claim Register Reconciliation:** Updated `authority_firewall_and_verification_limits_claim_ledger.md` to v2.2.0, adding claims `AVF-030-C11`, `AVF-030-C12`, and `AVF-030-C13`, and updating open obligations.
- **Metadata and Package Alignment:** Bumped package version to 2.2.0 across `pyproject.toml`, `zenodo_metadata.json`, `README.md`, and `docs/descriptions.md`.

## [2.1.0] - 2026-10-08

### Changed
- **Detector Calibration vs. Adequacy:** Clarified mathematically that four calibration cases (positive, negative, collision, metamorphic) constitute a necessary Minimum Calibration Record to falsify collapsing detectors, but cannot establish detector adequacy over an unbounded claim class. Refactored `MinimumCalibrationRecord` in `code/mod_verification_limits_core.py` to execute actual calibration cases against detectors, catching collapsing detectors $T_{\text{collapse}}$ fail-closed.
- **Capability Non-Constructibility:** Replaced the unconstrained function non-existence formulation with an explicit object-capability security specification: within an untrusted runtime environment possessing only public runtime interfaces, untrusted code cannot instantiate or forge an `AuthorityCapability`. Implemented sealed private constructor tokens in `AuthorityCapability`.
- **Fabricated Witness Defense:** Remediated the authority gate exploit identified in peer review. In `StructuralVerificationGate.evaluate_result`, authority witnesses are cryptographically verified against registered sovereign verifiers and bound to the candidate's exact `result_id` and payload hash. Fabricated, unbound, or tampered witnesses fail-closed to `RefusalDefect`.
- **Exact Rational Arithmetic:** Implemented discrete obstruction residual calculations using `fractions.Fraction` coordinates and exact $\ell_1$ norm metrics in `DiscreteResidual`.
- **Licensing & Metadata Alignment:** Aligned `LICENSE-CODE` to standard MIT License matching `README.md` and `zenodo_metadata.json`. Updated `zenodo_metadata.json` notes and provisional DOI status.
- **Monograph Harmonization:** Replaced fragmented extraction headers and phantom demo references (`_demos/runtime/`) with a unified, publication-grade academic monograph bound directly to the in-deposit reference implementation and test suite.
- **Claim Ledger Reconciliation:** Replaced the unfinished extraction stub in `authority_firewall_and_verification_limits_claim_ledger.md` with a complete, typed, dated claim ledger (`AVF-030-C01` through `AVF-030-C10`).
- **Test Suite Expansion:** Expanded `code/tests/test_verification_limits.py` from 4 to 8 comprehensive unit tests covering exact rational arithmetic, calibration execution, fabricated witness rejection, unbound witness rejection, genuine sovereign witness admission, capability isolation, fluent halting, and 6-axis lattice independence.

## [2.0.1] - 2026-10-07

### Changed
- `verify_deposit.py` no longer requires a `*_claim_ledger.md` (aligned with the paper template); `scripts/regen_sha256sums.py` is the template version and shares the deposit walker and exclusion sets with `verify_deposit.py` and `tools/rebuild_release.py`; `tools/rebuild_release.py` registers `deposit_paths` in `sys.modules` before executing it.
- Import blocks sorted and unused imports removed (ruff F401/F841/I).

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local local-first verification standards.
- Sovereign reference implementation `code/mod_verification_limits_core.py` modeling detector adequacy calibration suites (positive, negative, collision, metamorphic), capability non-constructibility, 6-axis evidence lattice, and halting vs structural authority in exact rational arithmetic.
- Unit test suite `code/tests/test_verification_limits.py` validating detector adequacy gating, capability isolation, and evidence lattice independence.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `authority_firewall_and_verification_limits_monograph.md`.
- Purged internal omnibus references, mechanism inventories, and house acronyms.
- Enforced strict claim hygiene (`RULE[user_global]`).

## [1.0.0] - 2026-07-28

### Added
- Initial pre-print specification of red-team P0 interfaces, detector adequacy, and capability non-constructibility.
