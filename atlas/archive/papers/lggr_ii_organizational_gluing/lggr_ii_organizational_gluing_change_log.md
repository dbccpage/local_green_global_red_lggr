# Change log — lggr_ii_organizational_gluing

**File:** `lggr_ii_organizational_gluing_change_log.md`  
**Package:** `parts/lggr_ii_organizational_gluing`  
**Status:** Active  
**Date:** 2026-10-15

## Version 1.3.1 (2026-10-15) — Zenodo release synchronization

- Synchronized release date (`2026-10-15`) and version (`1.3.1`) across manuscript, metadata, claim ledger, and release tooling.
- Removed numbered duplicate PDF/archive files and standardized the canonical archive output name to `lggr_ii_organizational_gluing_2026-10-15.zip`.

## 2026-10-10 — Review remediation and release consistency audit

- Corrected the abstract wording in `lggr_ii_organizational_gluing.md` to state product sufficiency ($R_3 = E_1 E_2 \iff E_G = E_1 E_2$) and formalize the carrier obstruction as the standard requirement that functions descending to equivalence classes respect their identifications.
- Hardened `EvaluatorGluingDefect` by materializing `local_evaluator_passes` as an immutable tuple upon initialization before validation, preventing post-validation mutation and avoiding duplicate iterator consumption.
- Hardened `negative_defect_witness` to fail closed if local product fails to transport or if the returned witness defect is not `-1`.
- Eliminated platform-dependent compiler triple embedding (`x86_64-w64-windows-gnu`) from `lean4/axiom_report.txt`, normalized compiler toolchain checks, and separated declaration/axiom validation to verify all 18 declarations uniquely without accepting duplicate reports.
- Hardened coverage computation in `verify_deposit.py` so that zero statements or zero branches evaluate to 0.0% coverage rate and fail the gate.
- Hardened manifest path validation in `verify_deposit.py` and `scripts/build_deposit_zip.py` to reject directory-component case collisions and file-directory clashes.
- Synchronized companion notebook outputs and non-null execution counts in `jupyter_notebooks/lggr_ii_organizational_gluing.ipynb` with headless and in-process execution fallback in `code/tests/test_notebook.py`.
- Retired claim ledgers from blocking verification gates in `verify_deposit.py` in accordance with repository publication rules while retaining files for provenance custody.
- Aligned `scripts/build_deposit_zip.py` default archive target to `{ROOT.name}_{RELEASE_DATE}.zip` and added release candidate archive consistency checks to `verify_deposit.py` to establish source-to-release agreement.

## 2026-10-09 — Finite Python checks for M4, M8, and M9

- The Boolean boundary cube is evaluated by `FiniteTheoremCensus.product_sufficiency_iff_factorization_census`. Under weak recovery the two sides of the product-sufficiency equivalence agree on all 128 recovered assignments. The other 128 assignments are the cases where the two sides disagree.
- `quotient_factor_table` returns a factor only when every joint-carrier class has one global verdict. A shared class with both verdicts is reported as blocked.
- `negative_defect_witness` selects the trace whose computed defect is `-1`. Local evaluators receive only the carrier coordinates, so a shared joint carrier transports the local product.
- The deposit verifier reads the pytest line that reports how many tests passed. A plugin warning on standard error is no longer able to hide that line.
- This note does not mint a DOI and does not change published version 1.3.0.

## Version 1.3.0 (2026-09-15) — concise republication

- Recorded Zenodo publication DOI `10.5281/zenodo.22882042` (record `22882042`)
  in the existing lineage `10.5281/zenodo.20674787`.
- Made the verifier and archive builder reject absolute, escaping,
  non-canonical, symlink, and case-colliding manifest paths.
- Classified the existing prior review report as a historical review of earlier bytes,
  not a review of the rebuilt archive.
- Rewrote the manuscript around the finite defect, weak-sufficiency
  counterexample, governance conjunction, and carrier-quotient obstruction.
- Replaced the earlier claim inventory with a direct claim-to-evidence ledger
  and synchronized the machine-readable claim-to-code map.
- Added `docs/lean_claim_map.md`, which records the exact paper declarations,
  statement hashes, import-block hashes, build target, and current Lean check.
- Corrected the detector-collapse implementation to compare the complete local
  product with the global evaluator. A regression now shows that one copied
  global validator plus a failing peer does not satisfy the collapse premise.
- Required evaluator callbacks to return exact Python `bool` values. Integer,
  floating-point, textual, and null stand-ins are rejected, while valid
  verdicts continue to produce integer `0/1` defect records.
- Reconciled the Shapley chapter pagination with the publisher record.
- Replaced implementation-process vocabulary in reader-facing history with
  ordinary mathematical and software language.
- Removed company-specific assertions from the public figures; retained named
  code constructors only as labelled illustrative assignments.
- Rebuilt the public notebook as one novice-to-research progression with a
  truth-table visualization, interactive controls, exact counterexamples, and
  a break-and-recover exercise; added headless execution to pytest.
- Reduced the Lean quotient support module to the definitions and theorem used
  by this paper. No paper-facing theorem was removed.
- Added deterministic Markdown-to-TeX/PDF tooling through the byte-pinned shared
  obstruction preamble and two pdfLaTeX passes. The build also captures the
  current Lean axiom report and writes a reproducibly dated archive.
- Enforced separate 95 percent floors for production line/statement and branch
  coverage, including a regression that rejects a sub-threshold branch rate.
- Made the Primary description in `docs/descriptions.md` the exact source for
  the Zenodo description, with a separate concise Secondary description.
- Added a locked Python environment and two-way checksum checks.
- Made the Boolean cases a portable vertical list and replaced long in-text
  Lean identifiers with claim-ledger labels for clean typesetting.
- Updated the public date and version metadata to 2026-09-15 / 1.3.0.

## Monograph consolidation and prefix removal (2026-09-13)

- Moved the package under
  `012_local_green_global_red_foundational_series/parts/lggr_ii_organizational_gluing/`.
- Removed the former numerical prefixes from the folder, paper, claim ledger,
  change log, and companion notebook names.
- Reconciled documentation, tests, and local references after the move. The
  suite then contained 43 passing tests.

## Version 1.2.1 (September 2026) — clarification pass

- Reconciled historical paper-number aliases and local references.
- Replaced “certifiably closed” with “checked for closure eligibility” and
  separated zero defect from a passing outcome.
- Distinguished paper-facing Lean declarations from auxiliary finite
  counterexamples and corrected the claim ledger.
- Updated the then-current test count to 31 unit tests and 12 fault-injection
  tests.
- Softened the Shapley wording from a required attribution method to an
  optional analysis of a user-supplied coalitional game.
- Corrected the Abramsky–Brandenburger title and refreshed source links.
- Repaired the notebook after an API rename and regenerated its clean source.
- Improved figure labels, line wrapping, and panel spacing.

## Version 1.2.0 (2026-09-09) — republication pass

- Removed the false implication
  \(G_{\mathrm{rep}}\wedge G_{\mathrm{auth}}\wedge G_{\mathrm{time}}
  \Rightarrow E_G=\prod_i E_i\) and retained the three Boolean values only as
  declared governance prerequisites.
- Made every `DetectorAdequacyGuard.audit_verdict` branch non-certifying and
  distinguished passing agreement from joint failure.
- Separated evaluator agreement, declared governance prerequisites, checked
  closure eligibility, and any later empirical assessment.
- Added strict Boolean validation to trace and record constructors, validated
  defect arithmetic, and prevented unsupported evidence-level elevation.
- Relabelled the named examples and figures as illustrative model assignments.
- Synchronized version 1.2.0 across the public package surfaces.
- Narrowed the non-additivity result to unrestricted scalar summation and added
  duplicate-player validation to the optional Shapley implementation.
- Added the nonempty-sample condition to the finite detector check.
- Expanded the suite to 43 tests, with full coverage of the core model and
  99 percent aggregate statement coverage in that run.

## Version 0.3.3 (2026-09-04) — finite Lean package and executable model

- Added the finite Lean package for the Boolean audits, counterexamples, and
  quotient obstruction, together with a local axiom census.
- Added the Python organizational evaluator model, publication figure
  generator, and 37-test suite.
- Added the interactive notebook, reproduction documentation, package metadata,
  and licensing files.
- Added explicit scope language: the organizational examples are illustrative
  assignments rather than empirical findings.

## Initial version (2026-07-24)

- Created the package change log and initial finite-model description.
