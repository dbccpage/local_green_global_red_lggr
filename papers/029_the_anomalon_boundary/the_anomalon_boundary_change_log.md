# Change Log: The Anomalon Boundary (Paper 029)

## Version 2.1.1 — 2026-10-23

- Prepared republication metadata and reader-facing artifacts for this date.
- Retained mathematical claims, proof scope and the Lean 4.35.0 pin.
- Preserved the pre-preparation package outside the new deposit. No upload or new DOI is asserted.

All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## Repair record (2026-10-09)

Marked the finite trichotomy, the integer cycle and filled-triangle calculations, the continuation statuses, the positive-metric lift gate, the non-promotion flag, and the ten-role completeness check `[PROVED]` in `lean4/FiniteBoundary.lean`. The Python tests call `mod_anomalon_boundary_core.py` on those cases. Marked C4, C5, C6, C13, and C14 `[NEGATIVE BOUNDARY]`: the cited `Ontology.Anomalon`, `FOC.RedTeamDischarge`, `AddressabilityThreshold`, and `SurvivingPrimitiveDifference` names are not in this deposit. C2 stays a policy rule because `no_authority_without_descent` is the first conjunct of `HasAuthority`. Version 2.1.0 and publication date 2026-10-08 are unchanged.

## [2.1.0] - 2026-10-08

### Added
- Bundled self-contained Lean 4 package `lean4/` containing `lakefile.lean`, `lean-toolchain`, `OntologyBasic.lean`, and `Census.lean`.
- `ValidatedClaimPacket` in Lean 4 formalization, restricting quantifiers in `AnomalonAxiomSet` and exhibiting a concrete verified inhabitant `defaultAnomalonAxioms`.
- Explicit finite `CochainComplex` in Python reference implementation verifying coboundary composition $d^1 d^0 = 0$ over $\mathbb{Q}$ and classifying cochain discrepancies via exact Gaussian elimination.
- `LiftPreservationWitness` dataclass gating lift transitions (`authorize_lift`) with strictly positive preservation metric $\Delta_\Lambda > 0$.
- Comprehensive unit tests covering explicit boundary matrix classification, fail-closed input validation, and rejection of mathematically inconsistent cochain defects.

### Changed
- Relabeled `no_authority_without_descent` as a policy invariant by construction (definitional from `HasAuthority`), reserving "verified descent" for executed certificate checks against concrete packet data.
- Upgraded `AnomalonBoundary.request_continuation` to an active firewall that validates inputs fail-closed and distinguishes requested lifts (`LIFT_REQUESTED`) from authorized lifts (`LIFT_AUTHORIZED`).
- Replaced boolean `is_closed` and `is_exact` assumptions in `CochainDefect` with mathematical consistency checks, rejecting exact discrepancies with non-zero curvature or negative norms.
- Updated Zenodo release metadata: removed pending DOI, corrected parenthetical equating exact discrepancies with $H^1 = 0$ to quotient residual $[h] = 0$ in $H^1$, and set version to 2.1.0.
- Synchronized companion file references across `the_anomalon_boundary_claim_ledger.md` and clarified MKS scope fences in `the_anomalon_boundary_monograph.md`.

## [2.0.1] - 2026-10-07

### Changed
- `verify_deposit.py` no longer requires a `*_claim_ledger.md` (aligned with the paper template); `scripts/regen_sha256sums.py` is the template version and shares the deposit walker and exclusion sets with `verify_deposit.py` and `tools/rebuild_release.py`; `tools/rebuild_release.py` registers `deposit_paths` in `sys.modules` before executing it.
- Import blocks sorted and unused imports removed (ruff F401/F841/I).

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local local-first verification standards.
- Sovereign reference implementation `code/mod_anomalon_boundary_core.py` modeling surviving primitive differences, the Anomalon restart boundary, continuation laws, and Minimal Knowable System (MKS) role completeness in exact rational arithmetic.
- Unit test suite `code/tests/test_anomalon_boundary.py` validating defect trichotomy, continuation routing, Anomalon non-promotion, and MKS role checking.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `the_anomalon_boundary_monograph.md`.
- Purged internal house slang and informal prose while establishing "Anomalon" strictly as the formal concept name for an unresolvable terminal residual.
- Enforced strict claim hygiene (`RULE[user_global]`).

## [1.0.0] - 2026-07-24

### Added
- Initial pre-print registration and Lean 4 kernel verification for surviving primitive differences and minimal knowable systems.
