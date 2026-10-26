# Change Log: The Omega Tower — Role Non-Impersonation and Authority Preservation

## 1.3.0 — 2026-10-16 (prepared edition)

Restricted universal-descent authorization to inhabited observation fibers; clarified that universal quantification alone accepts empty fibers vacuously. Scoped the six-role correspondence to its constructor convention, refusal propagation to the pure bind operation, and finite evidence transport to an explicit factorization. Removed unsupported cofinality and repeated policy claims.

Revised mathematical scope and presentation; introduced the canonical Markdown math spine with persistent equation IDs and occurrence bindings; regenerated TeX, math-preserving text, and PDF through ordered formula checks. The build records file digests and does not assign mathematical truth. Existing public deposit identifiers are retained as prior-record references, not asserted as identifiers for this prepared edition.


**Paper Key:** `001_finite_obstruction_calculus/004_role_non_impersonation_and_authority_preservation`  
**DOI:** [10.5281/zenodo.20710065](https://doi.org/10.5281/zenodo.20710065)  

## 2026-10-09 — Proved rows checked in Lean 4 and Python

C3, C4, C5, C7, C8, and C14 stay proved. `code/proved_rows.py` calls the shipped role table, refusal bind, five-stage pipeline, and terminal constructors on the finite instances: six roles round-trip through six failure modes; a refusal absorbs the next stage; an obstruction refusal calls no later stage; authority, residual, and refusal statuses stay apart; the same payload with authority and residual roles receives two failure labels, so a payload-only map misses one; that mixed fiber makes universal quantification along payload-erasure fail exactness, while a one-point fiber stays exact; a predicate true only on the unmixed image sits inside both sides of the adjunction. The general statements remain the Lean theorems named in the ledger. This is not a new Zenodo deposit and does not change the published version.

## [v1.2.2] — 2026-10-08 (Audited Remediation & Republication Release)

- **P1 Residual Classification & Exactness Separation:** Separated mathematical predicates ($\operatorname{Exact}(r) \iff \exists \alpha, d_0 \alpha = r$, $\operatorname{Closed}(r) \iff d_1 r = 0$) from terminal authority. Implemented 4-way classification: zero defect, repairable exact defect, closed non-exact residual, and open residual. Added regression test for equal-mass counterexample ($r_e=(1,0,0)$ vs $r_h=(0,1,0)$). Renamed Lean theorems in `AuthorityResidual.lean` to `non_exact_residual_not_resolved` and `renamed_non_exact_as_resolved_contradiction`.
- **P1 Elimination of Unchecked Authority Issuance:** Enforced 4-stage pipeline: cochain evaluation $\to$ checked mathematical result $\to$ authorization decision $\to$ issued receipt. Removed default throwaway registries and fail-closed against internally inconsistent inputs ($r=0$ with $d_1(r) \ne 0$). Bound issuance to verified evidence.
- **P1 Contract Rule vs Necessity Separation:** Scoped role non-impersonation strictly to a declared contract rule. Replaced "Proof Sketch" with contract interpretation and illustrative omission scenarios. Replaced §11 architectural necessity challenge with concrete implementation falsifiability challenge.
- **Pure Math §5.4 — Maximal Sound Authority Descent:** Mechanized Lawvere universal quantification $\forall_q A(y) := \forall x, q(x)=y \to A(x)$ in dedicated Lean 4 module `AuthorityDescent.lean` with 7 machine-checked theorems: adjunction $q^{-1}(B) \subseteq A \iff B \subseteq \forall_q A$, soundness, maximality, exact preservation iff fiber-constant, mixed-fiber obstruction, compositionality, and conjunction distribution with zero custom axioms. Added two-way bridge theorem `payload_classifier_factors_iff` and non-existence theorem `role_failure_no_quotient_factor` to `QuotientBoundary.lean`.
- **P2 Proposal Digest Receipt Binding Separation:** Separated receipt envelope keys (`token`, `verified_token`, `receipt_envelope`) from `_proposal_digest` hash inputs to prevent positive receipt validation from invalidating its own binding. Added positive verification and tamper detection tests.
- **P2 Finite Shadow & Axiom Audit Tightening:** Designated cofinal category formula in §7.1 as an ideal semantic specification; kept executable result as bounded coherence without authority. Made `Census.lean` presence and 18-declaration census mandatory in `verify_deposit.py`, aligning whitelist documentation with standard Lean 4 core axioms (`propext`, `Quot.sound`).

---

## [v1.2.1] — 2026-10-08 (Publication Blocker Resolution)

- **P1 Verification Evidence Hardening:** Replaced caller-controlled metadata assertions (`verified_token=True`) in Stage 4 verification defense (`adversarial_benchmark.py`) with validation of verifier-owned evidence (`AuthorityReceiptRegistry.validates`). Added regression test for confidence-spoofing fixture 114 confirming refusal regardless of caller metadata.
- **P1 Release Archive Integrity Gate:** Repaired stale release zip members (updating cochain exactness handling, tests, and manifests). Bound `tools/rebuild_release.py --check` directly into the default execution of `verify_deposit.py` so release archive drift fails closed.
- **P2 Semantic Disambiguation of "Authority":** Clarified and separated mathematical cochain classification (exact cochain zero-defect closure) from registry authorization (in-memory token issuance) across Lean 4 structural types, Python registry objects, and mathematical models. Specified in §2.1 and §8 that Lean proofs (`isValidAuthorityToken`) govern syntactic record validation rather than runtime trust.
- **P2 Claim Hygiene & Scope Harmonization:** Purged remaining instances of `[ARCHITECTURE THEOREM]` and `[EMPIRICAL BENCHMARK]` across Appendix B, README, and claim ledger, strictly scoping them to `[CONTRACT RULE]` and `[FIXTURE SUITE]`. Updated Section 6 proof sketch to frame role omission as a contract routing policy rather than an architecture theorem.
- **P2 Licensing Harmonization:** Replaced PolyForm Noncommercial in `LICENSE-CODE` with Apache-2.0, aligning code licensing uniformly across `LICENSE-CODE`, `README.md`, `zenodo_metadata.json`, and documentation.
- **Pure Derivation Roadmap:** Prioritized pure mathematical derivation for maximal sound authority descent through a quotient ($A_{\mathrm{safe}}(y) = \forall x \in q^{-1}(y), A(x)$), proving preservation under fiber-constancy and compositionality across successive transports.

---

## [v1.2.0] — 2026-10-08 (Contract-Model Corrections)

- Reclassified Role Non-Impersonation as a declared contract rule.
- Replaced caller-controlled receipt checks with a verifier-owned local registry and documented its non-cryptographic scope.
- Declared the F2 cochain differential, added bounded finite-shadow coherence, and relabelled the LLM benchmark as a deterministic fixture suite.

---

## [v1.1.0] — 2026-10-07 (Academic Republication Upgrade)

### Removed / Purged
- **In-House Jargon & Swarm Lore Purged:**
  - Removed "Mechanism inventory" table with internal slots (`ZeroRel`, `Anomalon Estate`, `Licensed repairs`, etc.).
  - Purged internal acronyms and lore (`GTLA`, `GTOC`, `CODA-FDA`, `CODA-MUR`, `CODA-OR`, `CODA-CS`, `CODA-A`, `CODA-FOC`, `Root W`, `Root P`, `AuthorityEffect: None`).
  - Retired internal ticket numbers (`PL-029-1` through `PL-029-4`) and replaced with explicit mathematical hypotheses, propositions, and theorems.
  - Eliminated promotional hype vocabulary and ungrounded claims in compliance with strict Claim Hygiene rules.

### Added
- **Formal Academic Monograph Overhaul:**
  - Rewrote `role_non_impersonation_and_authority_preservation.md` into a publication-grade systems/formal-methods monograph.
  - Grounded theoretical foundations in separation of privilege (Saltzer & Schroeder, 1975) and commercial integrity (Clark & Wilson, 1987).
  - Formalized the five-stage Kleisli pipeline in an exception/refusal monad with left-zero absorption.
  - Formalized query-relative finite shadows and the five-terminal residual honesty taxonomy.
- **Machine-Checked Lean 4 Formalization (`lean4/`):**
  - Added self-contained Lean 4 package `RoleNonImpersonation` compiling under toolchain `v4.34.0`.
  - `RoleFailure.lean`: Bijective role-to-failure mapping, injectivity, and invertibility theorems.
  - `ExceptionPipeline.lean`: Refusal monad definition, monad laws, and five-stage refusal propagation theorems.
  - `AuthorityResidual.lean`: Terminal constructor disjointness, replayable token contracts, and residual classification theorems.
  - `QuotientBoundary.lean`: Role-erasure payload quotient boundary and non-factorization theorems.
- **Verified Python Reference Engine & Test Suite (`code/`):**
  - Implemented `models.py`, `pipeline.py`, `cochain_example.py`, `shadow.py`, `classifier.py`, and `deposit_paths.py`.
  - Created 20 comprehensive unit tests in `code/tests/` achieving 100% pass rate under `py -3.12 -m pytest`.
- **Standard Release Infrastructure:**
  - Added `zenodo_metadata.json` matching Zenodo record 20710065.
  - Added `README.md`, `REVIEW_SCOPE.md`, `LICENSE` (CC-BY-4.0), `LICENSE-CODE` (Apache-2.0 / MIT), `pyproject.toml`.
  - Added `docs/descriptions.md` and `docs/references.md`.
  - Added `scripts/build_paper_artifacts.py` for automated Pandoc + XeLaTeX PDF generation.
  - Added `verify_deposit.py`, `scripts/regen_sha256sums.py`, and `tools/rebuild_release.py`.

---

## [v0.1.0] — 2026-06-15 (Initial Working Draft)
- Initial internal preprint draft with cross-tower notes and preliminary role tables.
