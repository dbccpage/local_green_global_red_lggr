# Change Log: Finite Authority and Non-Terminal Computation (Paper 028)

## Version 2.0.3 — 2026-10-23

- Prepared republication metadata and reader-facing artifacts for this date.
- Retained mathematical claims, proof scope and the Lean 4.35.0 pin.
- Preserved the pre-preparation package outside the new deposit. No upload or new DOI is asserted.

All notable changes to this research package are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

---

## Repair record (2026-10-09)

Marked D1, D5, D6, and the class-increase identity D16 `[PROVED]` on theorems in `lean4/FiniteAuthority.lean`, with the existing Python tests calling `mod_finite_authority_core.py`. Those four rows name `test_lggr_quotient_obstruction_exhaustive_carrier_and_counterexample`, `test_minimal_verdict_refinement_derivation`, `test_halting_does_not_imply_authority_and_checklist_scoping`, and `test_counterfeit_descent_detection_and_missing_evidence_safeguards`. Marked C1, C1a, C2, the detection-completeness half of C3, D2, D7, and D8 `[NEGATIVE BOUNDARY]`: the cited prose and `PaperAF003` names are not in this deposit. Halt and counterfeit theorems are finite status equalities, not theorems about Turing machines and not $\mathsf{Authority}_D$. Version 2.0.2 and publication date 2026-10-08 are unchanged.

## [2.0.2] - 2026-10-08

### Added
- **Constructive Minimal Verdict-Preserving Refinement (§4.4):**
  - Proved that $X/{\sim_*}$ (where $x \sim_* y \iff q(x)=q(y) \land G(x)=G(y)$) is the coarsest quotient refinement preserving $Q$ through which $G$ descends.
  - Implemented exact class increase formula $|X/{\sim_*}| - |Q| = \sum_{u \in Q} (|G(q^{-1}(u))| - 1)$ and explicit split witness generation in `compute_minimal_verdict_refinement`.
- **Evaluated Path Kernel (EPK) Dual Formulations (§4):**
  - Implemented canonical continuous exponential discount kernel ($e^{-\lambda C - \mu R}$) alongside exact rational Pade surrogate ($1 / (1 + \lambda C + \mu R)$ in $\mathbb{Q}$), matching reviewer fixture probes.
  - Added strict non-negativity and exact rational type checking for cost, residual risk, and proposal probabilities.
- **Evidence-Bearing Authority vs Scoped Checklist (§6):**
  - Added `TerminalStatus.CHECKLIST_CERTIFIED` and `TerminalWitness` dataclass.
  - Passing C1–C8 checklist yields `CHECKLIST_CERTIFIED`, refusing sufficiency to operational `AUTHORITY` without a verified terminal object and $IsAuth$ witness.
  - `detect_counterfeit_descent(trace, 0)` now fail-closes to `PROPOSAL_ONLY` on unhalted traces and `NON_AUTHORITY_HALT` without verified gates.

### Changed
- **Reconciled Gate Stack Schema & Boolean Enforcement (§6):**
  - Reconciled `GateStack` fields with Section 6 Table (C1: proposal, C2: parseable output, C3: canonicalization, C4: verifier, C5: unique answer fiber, C6: replay, C7: leakage/provenance, C8: terminal gate).
  - Enforced strict boolean validation in `GateStack.__post_init__`, rejecting string truthiness (`GateStack(*["False"]*8)` raises `TypeError`).
- **Exhaustive Carrier LGGR Verification (§4.3):**
  - Updated `LGGRObstruction` to evaluate equivalence classes over declared finite carriers, preventing false-positive factorization from sampled pairs when equivalent states exhibit conflicting local values.
- **Licensing & Mathematical Typography Alignment:**
  - Replaced PolyForm Noncommercial with standard Apache-2.0 in `LICENSE-CODE`, harmonizing with README and pyproject.toml.
  - Corrected literal `##` artifacts in EPK equation (§4) and evaluator gluing defect equation (§11).
  - Explicitly scoped earlier Lean formalization sketches (`PaperAF003`) as unbundled external design sketches; standalone package verification certified locally by Python suite.

---

## [2.0.1] - 2026-10-07

### Changed
- `detect_counterfeit_descent` refuses every trace with non-zero residual defect mass before looking at surface signs or the gate stack (`VERIFIER_REJECTED` without surface signs, `COUNTERFEIT_PACKET` with them), and rejects inexact or negative residual mass; `code/tests` gains the corresponding checks.
- `verify_deposit.py` no longer requires a `*_claim_ledger.md` (aligned with the paper template); `scripts/regen_sha256sums.py` is the template version and shares the deposit walker and exclusion sets with `verify_deposit.py` and `tools/rebuild_release.py`; `tools/rebuild_release.py` registers `deposit_paths` in `sys.modules` before executing it.
- Import blocks sorted and unused imports removed (ruff F401/F841/I).

## [2.0.0] - 2026-10-07

### Added
- Standardized academic research package layout conforming to local local-first verification standards.
- Sovereign reference implementation `code/mod_finite_authority_core.py` modeling proposal laws, Evaluated Path Kernel (EPK), C1–C8 gate stack, typed refusals, and LGGR obstruction in exact rational arithmetic.
- Full unit test suite `code/tests/test_finite_authority.py` covering gate stack evaluation, halting vs authority, counterfeit descent rejection, and quotient non-factorization.
- Comprehensive 8-section Unicode documentation standard `docs/descriptions.md`.
- Formatted bibliography in `docs/references.md`.
- Automated manifest generator `scripts/regen_sha256sums.py`, release builder `tools/rebuild_release.py`, and fail-closed deposit verifier `verify_deposit.py`.

### Changed
- Promoted manuscript to publication-grade monograph `finite_authority_and_non_terminal_computation_monograph.md`.
- Purged internal house jargon and replaced with canonical terminology (Layered Authority Framework, Finite Descent Verification, Obstruction Evidence Lane).
- Enforced strict claim hygiene (`RULE[user_global]`): eliminated forbidden promotional language.
- Clarified distinction between syntactic halting / token generation and terminalized operational authority.

## [1.0.0] - 2026-07-24

### Added
- Initial pre-print registration and Lean 4 kernel verification for LGGR quotient obstruction and finite authority gates.
