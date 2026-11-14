# Change Log: The Authority Firewall (Paper 027)

## Version 2.1.1 — 2026-10-23

- Prepared republication metadata and reader-facing artifacts for this date.
- Retained mathematical claims, proof scope and the Lean 4.35.0 pin.
- Preserved the pre-preparation package outside the new deposit. No upload or new DOI is asserted.

All notable changes to this research paper package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

---

## Repair record (2026-10-09)

Marked AF-01, AF-02, and AF-20 `[PROVED]` on the theorems in `lean4/ResidualNonCreation.lean`, and added a Lake package so `verify_deposit.py --lean` elaborates them. The Lake trace path inside this package is 260 characters, so the verifier copies those same sources to a short directory before `lake build`. Marked AF-03, AF-04, AF-05, and AF-06 `[NEGATIVE BOUNDARY]`: their cited kernels are not in this deposit, or the stated hypothesis is vacuous. Version 2.1.0 and publication date 2026-10-08 are unchanged. `test_af02_witness_blocks_total_auth_extractor` calls `residual_not_auth` on the residual witness.

## [2.1.0] - 2026-10-08

### Added
- Bundled self-contained Lean 4 proof file `lean4/ResidualNonCreation.lean` under namespace `OmegaCore.ResidualClosureLayer` providing an immediately reproducible, zero-axiom verification trail.
- Strict runtime contract enforcement in `code/mod_authority_firewall_core.py` rejecting malformed coproducts (empty payloads, mismatched classes, non-boolean guard truth values, blank identifiers, unreplayable evidence).
- Conformance regression tests in `code/tests/test_authority_firewall.py` verifying strict runtime contract enforcement.

### Changed
- Standardized release identity to Version 2.1.0 (2026-10-08) across monograph, ledgers, metadata, and packaging.
- Aligned software license declarations to PolyForm Noncommercial 1.0.0; removed placeholder `10.5281/zenodo.pending` DOI.
- Scoped constructor disjointness claims: constructor disjointness prevents an existing residual terminal from being identified with an authority certificate, but does not prohibit external functions from constructing new authority records; removed overbroad self-authorization claims.
- Reconciled audit narrative into explicit pre-adversarial review (asserted flags passed inadequate detector) and post-adversarial review (corrected inputs refused promotion) stages; downgraded Clause 2 to internal audit claim.
- Corrected mathematical formulations: injection image intersection $\operatorname{im}(\mathsf{inl}) \cap \operatorname{im}(\mathsf{inr}) = \varnothing$, distinguished repair quotient $Q^1 = C^1 / \operatorname{im} d^0$ from first cohomology $H^1 = \ker d^1 / \operatorname{im} d^0$, and characterized authority types as four separately declared encodings without a common adapter.
- Corrected Layer 6 routing in the architecture diagram to terminalize into $\mathbb{T}_{\mathrm{res}} + \mathbb{F}_{\mathrm{res}}$.
- Updated claim ledger heading from Paper 024 to Paper 027 and repaired body index links.

## [2.0.1] - 2026-10-07

### Changed
- `verify_deposit.py` no longer requires a `*_claim_ledger.md` (aligned with the paper template); `scripts/regen_sha256sums.py` is the template version and shares the deposit walker and exclusion sets with `verify_deposit.py` and `tools/rebuild_release.py`; `tools/rebuild_release.py` registers `deposit_paths` in `sys.modules` before executing it.
- Import blocks sorted and unused imports removed (ruff F401/F841/I).

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local local-first verification standards.
- Sovereign reference implementation `code/mod_authority_firewall_core.py` modeling the coproduct separation $\mathbb{T} = \mathbb{T}_{\mathsf{auth}} \oplus (\mathbb{T}_{\mathrm{res}} + \mathbb{F}_{\mathrm{res}})$, 7-guard verification, and solver audit simulation in exact rational arithmetic.
- Full test suite `code/tests/test_authority_firewall.py` covering constructor disjointness, promotion refusal, and adversarial audit scenarios.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted pre-print manuscript to publication-grade monograph `authority_firewall_monograph.md`.
- Purged internal house jargon and replaced with canonical mathematical terminology (Obstruction Evidence Lane, Descent Authority Lane, Layered Authority Framework).
- Enforced strict claim hygiene (`RULE[user_global]`): eliminated forbidden promotional language.
- Clarified distinction between zero-guard type-level summand separation and semantic truth certification.

## [1.0.0] - 2026-07-24

### Added
- Initial pre-print registration and Lean 4 kernel verification for coproduct constructor disjointness.
