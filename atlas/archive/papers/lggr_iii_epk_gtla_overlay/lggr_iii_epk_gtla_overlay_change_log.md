# Change log — Local Green, Global Red III

## Version 1.5.2 — 2026-10-15

- Synchronized release date (`2026-10-15`) and version (`1.5.2`) across manuscript, metadata, claim ledger, notebooks, and release scripts.
- Removed numbered duplicate PDF/archive files and standardized the canonical archive output name to `lggr_iii_epk_gtla_overlay_2026-10-15.zip`.

## Version 1.5.1 — 2026-10-10

- Remediated external repair-and-republish review findings across exactness, numerical status, claim binding, and artifact binding.
- Exactness: Replaced float tolerance (`math.isclose`) in G2 cost additivity and G4 proposal mass factorization with exact rational arithmetic (`_to_exact_rational` using `fractions.Fraction`), preserving exact decimal representations for test fixtures while rejecting exact discrepancies.
- Numerical status: Implemented `NumericalRefusalError` and explicit `numerical_status` classification (`finite`, `overflow`, `nan_residual`), ensuring nonfinite compositions cannot produce a successful numerical identity verdict.
- Claim binding: Generalized Lean 4 quotient declarations (`LGGR3.quotient_evaluator_obstruction` and `LGGR3.quotient_evaluator_constant`) to quantify over arbitrary carrier types and setoids `{X : Type u} (s : Setoid X)`.
- Artifact binding: Bound canonical release artifacts (`lggr_iii_epk_gtla_overlay.pdf` and `lggr_iii_epk_gtla_overlay_2026-10-15.zip`) by byte-equality check and archive extraction verification against `MANIFEST.sha256`.
- Separated signed defect sum $D = N_+ - N_-$ from disagreement count $M = N_+ + N_- = \sum_i |\Delta_i|$ in manuscript, core, and test suites.
- Stated quotient descent (Theorem 3) as a necessary and sufficient equivalence with uniqueness by projection surjectivity.
- Clarified mutation test 10 annotation: partitioning by verdict demonstrates descent on a refined quotient, not repair under the original relation.
- Added 5 regression tests reproducing review findings and 3 independent bounded controls (4,681 binary samples, 200 deterministic integer kernel cases, 1,955 partition/evaluator combinations), maintaining 100% statement and branch coverage on the core.

## 2026-10-09 — Integer kernel reindexing

This does not mint a DOI or change version 1.5.0.

- `LGGR3.factorized_integer_kernel_has_zero_residual` mechanizes the finite integer reindexing: flattened boundary products sum to the grouped convolution, so the residual is zero.
- Python `integer_kernel_residual_is_zero` checks that statement. The existing path audit still checks the finite float kernel.
- Real exponentials stay open under PL-025-8.

## 2026-10-09 — Local checksum refresh

This does not mint a DOI or change version 1.5.0.

- The pinned digests for `jupyter_notebooks/00_start_here.ipynb`, `jupyter_notebooks/02_why_zero_can_mislead.ipynb`, and `uv.lock` did not match the bytes already in the package.
- `scripts/regen_sha256sums.py` rewrote `MANIFEST.sha256` and `SHA256SUMS` from those bytes. No claim text was changed.
- The reproduction entry disables the unrelated asyncio plugin. This package has no async tests, and that plugin's deprecation text was being read as a failed suite.

## Version 1.5.0 — 2026-09-18

- Publication date: 2026-09-18 (evidence-capture baseline: 2026-09-15).
- Resource type: Preprint. Standardized version identity string to `1.5.0`.
- Expanded and reconciled the public surface to seven teaching and verification notebooks (`00_start_here.ipynb` through `06_reviewer_verification.ipynb`).
- Rebuilt reviewer verification matrix in `06_reviewer_verification.ipynb` directly from the 15-row claim IR, public `Core.lean` declarations, and exact axiom census.
- Reconciled notebook wording: neutralized "global-only pass" in Notebook 01; clarified G1–G4 as sufficient hypotheses in Notebook 03; fixed claim citation to C08–C09 in Notebook 04; replaced "adjoint transport" with "invertible byte-swap transport" in Notebook 05.
- Removed the table of contents from the short synthesis note to eliminate the empty TOC header.
- Added explicit spacing before Theorem 2 following the G4 list and removed the duplicated author/date header block.
- Rebuilt matching Markdown, TeX, and PDF from the single authoritative source.
- Eliminated internal repository fields and placeholder DOI from public manuscript headers pending formal minting.
- Recorded the existing DOI lineage `10.5281/zenodo.20675954` while keeping upload of the repaired archive explicitly pending through **New version**.
- Made the verifier and archive builder reject absolute, escaping, non-canonical, symlink, and case-colliding manifest paths.
- Restored all eight earlier notebooks and four figures byte-for-byte under `research/legacy_omnibus/` before reducing the former sibling package to a redirect.
- Classified the existing prior review report as a historical review of earlier bytes, not a review of the rebuilt archive.
- Reclassified the 2,200-line archive omnibus as a thin synthesis paper.
- Retained five load-bearing results: defect trichotomy, the one-trace local-green/global-red witness, the finite sum identity, aggregate cancellation, and quotient-descent obstruction.
- Removed the embedded change log and claim table from the manuscript.
- Replaced repeated internal workflow language with one ordinary-language scope paragraph.
- Reduced the live claim ledger while preserving PL-025-6 through PL-025-9.
- Rechecked the nearest-neighbor bibliography against DOI and arXiv records.
- Added honest coverage for the figure generator and declared the notebook runtime dependencies.
- Strengthened G1 to the explicit bijection between admitted composites and the disjoint union of compatible segment pairs, with a matching proof and executable falsifiers.
- Replaced declaration booleans and caller-supplied quotient truth values with computations over concrete finite paths and quotient classes.
- Moved the older omnibus Python, tests, eight supplemental notebooks, Lean modules, and wrapper scripts under `research/legacy_omnibus`, with their relocation hashes preserved.
- Bound all claim handles to public `Core.lean`, added a fifteen-row claim IR, and made the Lean verifier resolve every documented handle.
- Preserved every identity field in Markdown, TeX, PDF text, PDF metadata, and Zenodo metadata; fixed the checklist/tag-scope mismatch.
- Fixed figure and archive metadata and added two-run byte-hash checks.
- Bound the public build to the shared pdfLaTeX preamble, added a current theorem-level axiom report, and made the release archive date-explicit.
- Corrected the cancellation and quotient Lean mappings to match the exact paper statements and typed every claim for the live review plan.

## Version 1.4.0 — 2026-09-13

- Consolidated the package under its current unnumbered paper slug.
- Reconciled documentation and local references after the move.

## Version 1.3.1 — 2026-09-13

- Added the eight-notebook teaching sequence.
- Selected the orientation and reviewer notebooks as the public pair.
- Added the paper-local Lean claim map.

## Version 1.3.0 — 2026-09-11

- Aligned the six role names with the accompanying system-role vocabulary.
- Added modern Python aliases without changing the original API.
- Built the local Lean project and audited exported theorem axioms.

## Version 1.2.0 — 2026-09-09

- Corrected the aggregate residual sign.
- Added the clean-locus-to-zero-residual Lean bridge.
- Added an inhabited carrier-mixing quotient obstruction.
- Added strict Python quotient routing and invariance errors.

## Version 0.3.0 — 2026-09-04

- Introduced the paper-local Python, Lean, notebook, figure, and metadata
  package.
- Added twelve break-and-recover mutation checks.

## Versions 0.1–0.2.37 — 2026-06-10 to 2026-07-23

The original synthesis grew through a sequence of finite gate and interface
lemmas. Those historical declarations remain buildable in the legacy repository
snapshot (`research/legacy_omnibus`), whereas the shipped public Lean target
(`lean4/Core.lean`) focuses on the twelve paper-level mathematical claims.
PL-025 identifiers are never renumbered; their current dispositions are in the
companion claim ledger.
