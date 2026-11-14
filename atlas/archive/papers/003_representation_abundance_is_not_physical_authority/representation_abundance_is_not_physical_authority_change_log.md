# Change Log — Representation Abundance Is Not Physical Authority

## 2.2.0 — 2026-10-16 (prepared edition)

Clarified rational-valued cochains versus algebraically exact cochains, finite candidate domains, and the strict local-check hypothesis. Separated observable properties from unique candidate identification and stated the limits of the supporting Lean lemmas.

Revised mathematical scope and presentation; introduced the canonical Markdown math spine with persistent equation IDs and occurrence bindings; regenerated TeX, math-preserving text, and PDF through ordered formula checks. The build records file digests and does not assign mathematical truth. Existing public deposit identifiers are retained as prior-record references, not asserted as identifiers for this prepared edition.


Paper Key: `001_finite_obstruction_calculus/003_representation_abundance_is_not_physical_authority`  
Current Version: 2.1.2 (2026-10-10)
License: CC-BY-4.0  

---

## Version 2.1.2 (2026-10-10)

- Limit the manuscript title block to Author, Date, and Version. Other publication metadata remains in the README and metadata file.

- Normalize signed traversals to one stored cochain domain; reject extra and ambiguous orientations.
- Restrict false-green and sharpness constructions to edge-simple cycles and include zero-tolerance sharpness; retain the closed-walk upper bound.
- Check retained model content in plenitude extensions and freeze candidate/evidence mappings.
- Keep candidate receipts as SURVIVOR, REFUTED, or REFUSED. FamilySelectionResult carries evidence and family context; tuple unpacking is replaced by explicit fields.
- Distinguish written rational graph/family proofs from the eight narrower Lean components. Add the written observation-factorization criterion and distinguish property identification from model uniqueness.
- Synchronize current documentation at 33 core regressions and 23 release-integrity cases. Require canonical ZIP verification and recheck custody after test/compiler subprocesses.
- Prepare version 2.1.2 metadata with concept lineage and no assigned version DOI. No Zenodo deposit is performed. The dated historical repair record below is retained; its proof-status shorthand and DOI wording are superseded by this revision.

## Repair record (2026-10-09)

Version and publication date stay 2.1.1 and 2026-10-08. No new DOI.

- The six proved rows are the finite Lean theorems `observation_decision_agrees`, `plenitude_inflation`, `cycle_coboundary_holonomy_zero`, `false_green_holonomy`, `false_green_local`, `cycle_defect_bound`, `sharp_cycle_attains`, and `unique_acceptance_breaks`.
- Python evaluates those statements by calling `observation_decision_agrees`, `plenitude_inflates`, `check_evaluator_soundness`, `false_green_witness`, `cycle_defect_within_tolerance_sum`, `sharp_cycle_attains_tolerance_sum`, and `acceptance_relaxes_when_another_survivor_joins`.
- The cohomology sentence in Theorem 3.1 is the closed-walk vanishing. This deposit does not construct the quotient group $H^1$.

## Version 2.1.1 (2026-10-08)

Publication remediation addressing formal republication review findings:
- Enforced exact rational inputs across public evidence and candidate constructors (`ObservableDatum`, `EvidenceRecord`, `CandidateModel`), rejecting Python floats via `TypeError` to prevent precision drift, and parsing explicit decimal strings (e.g. `'0.1'`) into exact `Fraction`.
- Specified and validated `LocalGreenGlobalRedGate` input contracts: refused incomplete edge evaluations by default (`allow_sparse_default=False`), and validated that submitted signed cycles are non-empty, use valid graph edges, and form strictly closed loops before computing holonomy or checking evaluator soundness.
- Kept certified evidence an explicit premise: added premise notes in `EvidenceRecord`, monograph Section 4.1, abstract, and scientific description, qualifying that instrumental calibration and provenance occur upstream of the computational selector, and preserved that unique acceptance is strictly relative to the supplied candidate family $F$.
- Closed domain and proof gaps: rejected empty families and duplicate candidate identifiers in `WitnessedDifferenceQuotient`, chose an explicitly rational constant $\epsilon = \frac{1}{2} \tau_{\min} \in \mathbb{Q}_{> 0}$ satisfying $0 < \epsilon < \min_{e \in C} \tau_e$ in Theorem 3.2, and assigned signed values according to the cycle orientation.
- Added comprehensive unit and regression tests covering all 4 priority repair tasks, bringing the test suite to 20 tests.
- Rebuilt LaTeX, PDF, release checksums, and deterministic release archive.

---

## Version 2.1.0 (2026-10-08)

- Refused incomplete evidence, missing predictions, empty families, and duplicate identifiers rather than manufacturing discrepancies or acceptance.
- Made explicit zero tolerances authoritative and stated the finite nonempty no-new-profile hypotheses for plenitude inflation.
- Corrected the cycle-defect statement to the signed tolerance-sum bound and rebuilt the rendered artifacts.

---

## Version 2.0.0 (2026-10-07)

Comprehensive monograph upgrade and mathematical foundation enhancement:
- Upgraded theoretical framework synthesizing advancements from Paper 000 (*Witnessed Difference Programme*) and Paper 001 (*Local-Green Global-Red Foundational Series*).
- Formalized candidate spaces modulo observer evaluation equivalence $\mathcal{S} / \ker(\mathcal{O})$ and established the Observer Blindness Proposition and Plenitude Inflation Theorem.
- Proved the Local-Green Global-Red Boundary: Evaluator Soundness Theorem ($\operatorname{im}(d_0) \cap H^1 = \{0\}$), False-Green Obstruction Theorem, and Non-Recovery Theorem over discrete 1-cochain complexes.
- Formalized the Finite Terminal Selector operational tuple $(e, V, \tau)$ and established the 4-state terminal taxonomy (`ACCEPTED`, `SURVIVOR`, `REFUTED`, `UNDERDETERMINED`).
- Built sovereign Python verification engine (`code/mod_representation_abundance_core.py`) with exact rational arithmetic (`fractions.Fraction`) and 12 unit tests (`code/tests/test_representation_abundance.py`).
- Added complete deposit tooling: `verify_deposit.py`, `scripts/regen_sha256sums.py`, `tools/rebuild_release.py`, `zenodo_metadata.json`, and single-version Unicode documentation `docs/descriptions.md`.
- Completely eradicated internal esoteric house jargon and replaced governance token text with standard academic nonclaim statements.

---

## Version 1.0.0 (2026-07-29)

Initial preprint release (Concept DOI: 10.5281/zenodo.20725629):
- Preliminary conceptual framing of the representation-authority non-implication.
- Initial three-vacua worked example and checklist formulation.
