# Change log: paper 002 (epistemic no-go)

Paper key: `001_finite_obstruction_calculus/002_asi_no_go_theorem_epistemic_contextuality`\
Current version: 1.2.0 (2026-10-17), WORKING_DRAFT\
License: CC-BY-4.0\
Authority status: None.

## Version 1.2.0 (2026-10-17)

Packaging release. No theorem statement of version 1.1.0 changes. The package gains a Lean model and a standard-library check suite, and loses its claim ledger.

- Lean 4.34.0 package `lean4/` added, without Mathlib: 29 declarations in `ResultI` to `ResultIV`, built with `lake build` (exit 0) and censused with `Census.lean`; the axiom report lists `propext`, `Quot.sound` and `Classical.choice` only. `Classical.choice` enters through the `simp` proofs in `ResultIV`.
- Lean scope is the support-level and finite-model statements. The ℓ¹ defect, the dual witness and the strong, logical and probabilistic classification of Result I remain Rust-only; Result III.c is imported; Proposition II-open stays open; the gate model is not linked to the Rust gate.
- `code/epistemic_kernel.py` and 26 tests added. They use the standard library and `fractions.Fraction`, and reproduce the finite statements that need no linear-programming solver.
- Claim ledger retired from the package, following the programme's packaging rules. Its rows moved to `docs/mechanization_map.md`, which maps each statement to its Lean declaration and Python test.
- Manuscript section 6 rewritten for the three artifacts and a dated receipts table; section 8 non-claims and section 10 updated. Header brought to the strict centered four-line form with an abstract status paragraph; Status: WORKING_DRAFT.
- Deposit kit tooling added: `verify_deposit.py`, `scripts/`, `tools/`, `code/deposit_paths.py`, `pyproject.toml`, `README.md`, `zenodo_metadata.json` (no DOI), `docs/descriptions.md`, `docs/keywords.md`, `docs/references.md`, `docs/quick_start.md`, the two license files, and checksum manifests.
- Not done in this version: no PDF, TeX or notebook was built (no XeLaTeX in the build environment); the unmarked bibliography entries are still to be checked against the publisher record; no upload and no DOI.
- Housekeeping from 1.1.0 done: the manuscript and change log carry concise-stem names (`epistemic_no_go_monograph.md`, `epistemic_no_go_change_log.md`), which keeps every path under the 250-character ceiling.

## Version 1.1.0 (2026-10-16)

Rewrite after an outside review of version 1.0.0 returned the verdict "no-go for publication in its current theorem form". The review's findings, numbered 1 to 12 in the manuscript's section 7, are all accepted.

- Title changed. The former title, "The Universal Epistemic No-Go Theorem for Physical Cognition", is withdrawn; the new title names conditional limits and the hypotheses they depend on.
- One four-clause theorem replaced by four separately quantified results (manuscript section 4), each tagged PROVED HERE, COMPUTED, IMPORTED, DEFINITIONAL, OPEN or FALSE.
- The self-knowing limits of the Witnessed Difference Programme copied in with their identifiers (section 3): WDP-CH14-D01, the refuted ladder of 14.2 with $R_1$ to $R_3$, WDP-CH14-P01, 14.4 with WDP-CH14-P02, P03 and N02, WDP-CH14-N01 and O01, WDP-CH14-T01, C01 and N03 at their declared scope, the hierarchy of 15.9, WDP-CH15-D01, the four separations of 15.2, 15.3, WDP-CH15-D02, P04 and N02, and the falsifiers of 21.5. Each item says what it contributes here.
- Postulates restated as hypotheses H1 to H4 with the party that must establish each. Finite data is declared, not derived from entropy or the Bekenstein bound. H3 names a specified effective theory.
- Privacy over time (v1.0.0 Proposition 2.4) marked OPEN with the swap-dynamics witness; the instantaneous fiber statement kept as Corollary II.
- Wolpert marked IMPORTED and unused; the pullback-apex corollary withdrawn.
- Čech $H^1$ of the nerve reported as a cover invariant; the cohomological obstruction stated as sufficient, not necessary; the dichotomy decided by the exact linear programme.
- Relabeling blindness restated for invariant verdicts with claims (1) and (2) kept apart, following FOC-035 §3.1; NB-9 dropped; "Lemma D" not used.
- Löb restated correctly; the well-foundedness argument of v1.0.0 §3.2 withdrawn.
- Authority stated as policy under H4 with delegated standing admitted; "sovereign" language removed.
- The inline floating-point Rust and Python listings (v1.0.0 sections 7 and 8) moved verbatim to `docs/legacy_float_kernel_listings.md` with the review's findings against them. The manuscript now cites the exact-rational kernel merged on the repository trunk at commit b8a84409f (pull request 1083): crate `omega_sheaf_theory` module `epistemic_observer`, crate `omega_contracts` module `three_role_authority`, their fixtures, 17 Rust tests and a 22-test Python harness.
- Claim ledger rewritten against symbols that exist in the merged code; the v1.0.0 rows and their absent symbols listed in the ledger's section 3. The ledger is kept as a draft index only, since the programme's packaging rules retire claim ledgers from deposits.
- Bibliography added (section 9). Entries copied from the programme's bibliography are marked; the rest await a check against the publisher record before deposit.
- Formatting brought to the programme's Markdown rules: no horizontal rules, ATX headings, dash list markers, no bare URLs, no governance tokens in reader-facing prose.
- Known housekeeping not done in this version, left for the author: the package still carries byte-identical duplicates (`paper.md` beside the slug-named manuscript, two copies each of the ledger and the change log, and a misspelled `paper_cjange_log.md`), a root copy of `wdp_precursor_to_no_go_theorem.md` beside the `docs/` copy, and dated prompt-output filenames under `docs/`, which the filename rules forbid. The package also lacks the deposit quartet (`README.md`, `docs/descriptions.md`, `docs/references.md`, `docs/keywords.md`, `code/`, manifests).

## Version 1.0.0 (2026-10-16)

Initial draft and package release. Superseded in every theorem statement by version 1.1.0; recorded here as written.

- Foundational lineage from the Witnessed Difference Programme (paper 000): sheaf-theoretic contextuality and missing global tables (WDP-CH19-P05, WDP-CH11-O01); the three-axis self-grounding regress (WDP-CH14-T01, C01, N03); observer presentation blind spots and the awareness firewall (WDP-CH14-P01, N01); the operational authority firewall (WDP-CH15-D01, D02, P04). The precursor text preserved in `wdp_precursor_to_no_go_theorem.md` and `docs/wdp_precursor_to_no_go_theorem.md`.
- Consolidation of fifteen multi-turn model outputs under prompt 04 (`docs/prompt_04_asi_no_go_theorem_epistemic_contextuality.md`), with the raw turns archived in `docs/`.
- A single theorem under four postulates (finitude; boundary mediation; effective enumerability; contextual world) with four refutations (context-free world model; peer-prediction dominance; internal self-soundness certification; self-authorization), five derivation obligations, and a "bounded coexistence" paradigm.
- An inline Rust kernel (about 1,970 lines) and a Python harness (25 tests), both floating-point, both now superseded and preserved under `docs/`.
- A claim ledger CLM-001 to CLM-012, now replaced.
