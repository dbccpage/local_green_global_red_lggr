> Current API/reproduction edition: see [the v1.8.3 review response](review_response_2026_10_23.md) and [source verification](source_verification_v1_8_3.json). The dated evidence below retains its original edition and scope.

# Reproduction record — version 1.6.0, 2026-10-21

The records below describe their dated earlier editions. The current version 1.7.0 integration and paired version 1.1.0 companion are mapped in [embedded_research.md](embedded_research.md); current replay evidence is [embedded_verification.json](embedded_verification.json). Historical hashes and test counts are not reassigned.


The Lean 4.35.0 migration uses Python 3.12.10 and pytest 8.3.5. `verification_run_v160_lean435.json` records the existing checks replayed for that toolchain, including commands, exit codes and output. `verification_run_v160.json` remains the original pre-migration record using Python 3.12.14, pytest 9.1.1 and Lean 4.33.1; its bytes and runtime identity are not rewritten. Earlier reports under versioned filenames remain historical.

- **143 pytest executions passed**, zero failures, errors or skips: the previous 112 plus 31 certificate tests, including original-input binding, strict signs, feasible bases, nullspace directions, malformed types and forced final-checker rejection.
- **113 named Lean theorems replayed**: 25 axiom-free, 88 using subsets of propext, Quot.sound and Classical.choice. No custom axiom or proof placeholder is admitted.
- **796 package-local declarations across 13 modules replayed**, including private/generated declarations, in the Lean 4.35.0 full environment census. The pre-migration count was 800: three generated decidability names change from `_aux_1` to `_proof_1`, and four generated `toCtorIdx` declarations disappear. All 113 explicitly named theorems remain present.
- **95 complete Python/Lean execution comparisons passed**: optimum coordinates, Farkas vectors, feasible bases, ray coordinates, exact objectives, pivot counts and inconclusive refusal kinds. Finite agreement is not universal refinement.
- The five exact contextuality fixtures retain their prior numerical data and Lean proofs against real competitors.
- Six source-pinned mind-expansion illustration groups and 19 standard-library assertions replayed. Optional NumPy/SymPy checks are not claimed. The source script mixes exact examples and floating illustrations; these are not empirical cognition tests or exact LP certificates.
- The preserved review's three mathematical groups and the noisy observation example replayed. Raw defect and radius remain 1/50, with guaranteed adjusted margin zero. The original 86-pass/four-missing-file review and its lack of a fresh Lean build remain preserved as supplied evidence.

## New formal scope

`CertifiedOutcomes` proves Farkas exclusion of every real feasible vector, real-ray feasibility/objective identities, and existence of a real feasible vector below every real objective floor. The total extended program reuses the deposited exact pivot, row-sign initialization and cleanup operations. Original-input replay guards each accepted outcome. Named theorems specialize these soundness results to actual accepted optimal, infeasible and unbounded returns. Search is structural on the remaining budget; its exact accounting theorem covers optimal and ray terminal tables.

`MindContracts` proves greatest sound report-only acceptance, per-score error regret and strict-gap optimality, and an upper-bound/actual-error counterexample. The continuous hybrid error ledger is a conditional mathematical argument, not a new Lean ODE theorem. The implemented memory-and-action safety refinement remains open. No consciousness threshold, human diagnosis, phenomenal identity or empirical cognition claim is derived.

Budget and certificate-mismatch refusals are inconclusive. Checked mathematical outcomes do not imply that every budget is sufficient, that unbudgeted Bland completeness is mechanized, or that Python and Lean are universally equivalent. Pivot accounting supplies no wall-clock or rational-bit-complexity bound. The independent Python checkers share exact arithmetic utilities with the solver but read only original LP inputs and witness records; institutional or hardware independence is not claimed.

## Source and dependency custody

The preserved v1.5.1 release digest is 2fc69a12e546b2ee5b62f36ca8ecbd6d82d9f87b74cec3f2a902abe0cb3b6c8d. The inherited theorem statements remain, while the root imports and JSON driver change and two modules are added. `source_lineage.json` preserves the unchanged precursor inventory and exact companion release identity. `mind_expansion_sources.json` pins all six supplied files after checking the four-entry source SHA256 inventory. The supplied optional 21-assertion report remains distinct from the current 19-assertion replay and is never overwritten.

The Lean 4.35.0 offline bundle contains 559,752,326 bytes, pinned by SHA256 9e3aeb94d4d2b0992e6485a3c8ea79c5f2bee49006913c43ff141f2d1b9ec3f5 and official Mathlib v4.35.0 commit 56a005855ea17e0b0958f73ec801ae140b0a1679. Its 2,426 dependency/build-support modules, matching sources, compiled artifacts and upstream licenses are included. No sibling paper, ambient Mathlib checkout, monorepo import or remote Lake dependency is needed. Lean, Python, pytest and tar are installed prerequisites; document-binding verification requires Pandoc, and PDF rebuilding additionally requires XeLaTeX and pdftotext. Repository clones additionally need `git lfs pull` to materialize the two large archives; a downloaded standalone ZIP does not require Git or Git LFS.

## Release procedure and final validation

The canonical rebuild regenerates the named census, checks the persistent equation registry, builds all manuscript formats, preserves actual compiler log/auxiliary evidence and rejects missing glyphs or overfull boxes. Both manifests and the deterministic ZIP are regenerated and byte-checked. Root compiler outputs and sealed text copies under `render_build` are preserved; a table-of-contents file is retained only if generated.

The original pre-migration clean-extraction and mutation checks remain recorded in `verification_run_v160.json`; they are not relabeled as Lean 4.35.0 checks. Migration validation rebuilds all package-local proof modules using the newly materialized offline cache, reruns both axiom censuses and all 95 execution comparisons, runs all five named Python test files, and rebuilds the manuscript formats. The existing deposit verifier and deterministic-archive checker then check the resealed package. Any fresh post-migration extraction receipt is retained outside the package and keyed to its ZIP digest to avoid self-reference. These are local checks, not an external reviewer's approval.
