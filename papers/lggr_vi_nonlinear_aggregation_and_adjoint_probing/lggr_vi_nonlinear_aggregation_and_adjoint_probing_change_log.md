# Change Log: LGGR VI (Nonlinear Aggregation and Adjoint Probing)

**Paper ID:** `lggr_vi_nonlinear_aggregation_and_adjoint_probing`  
**Title:** Blind Spots Under Nonlinear Aggregation and Adjoint Probing  
**Series:** `001_finite_obstruction_calculus / 012_local_green_global_red_foundational_series / lggr_vi_nonlinear_aggregation_and_adjoint_probing`  
**Anchor Tag:** `sealed-derivation-v1` (`3100c4e`)  

---

## [v0.1.0] - 2026-09-21

- **Initial Publication:** First formal public preprint release of LGGR VI studying finite observation blind spots, the Gram response, and adjoint probing.
- **Mathematical Scope:** Exact formulation of observation-only postprocessing invariance, zero-preserving aggregation acceptance of hidden states, metric cylinder distance bound under singular values, Gram kernel identity, two-query centered directional derivative, and full sign-cube recovery.
- **Formal Verification:** Four core theorems formalized in Lean 4 (`lean4/Core.lean`) with clean Lake compilation and zero unproved `sorry` axioms.
- **Self-Contained Executable Artifacts:** Portable Python test suite with line and branch coverage gates, break-detect-restore watcher mutation falsifier, two interactive Jupyter notebooks, reproducible figure generators, and verified pdfLaTeX compilation.
- **Internal Development Note:** Earlier preliminary drafts and exploratory prototypes from internal working iterations are permanently retired from the public surface and catalogued under the deferred research roadmap (`docs/research_program_25_steps.md`).

## [v0.1.0] - 2026-10-09 repair

- **No version bump and no DOI.** The release date string remains 2026-09-21.
- **LGGRVI-C03 recorded** as classical Euclidean background. The Euclidean cylinder argument stays visible in Theorem 2 and is not mechanized.
- **LGGRVI-C04 proved** for finite rational matrices by `gram_kernel_iff` and `gram_detectable_iff`. The orthogonal-range statement is outside the rational Lean formalization.
- **LGGRVI-C05 and LGGRVI-C06 proved** by `centered_directional_identity` and `sign_cube_recovers`, with exact `Fraction` checks that call the shipped Python functions. The float probes remain numerical checks.
- **Preamble pin:** the bundled obstruction preamble now matches the live kit. The added commands are subscript 4, subscript 5, and cdots. The shared kit file was not edited.

## [v0.1.1] - 2026-10-15

- **Metadata and Artifact Synchronization:** Updated release version to `0.1.1` and publication date to `2026-10-15` across manuscript, `README.md`, `zenodo_metadata.json`, `pyproject.toml`, claim ledger, and release builders.
- **Canonical Artifact Naming:** Standardized PDF output name to `lggr_vi_nonlinear_aggregation_and_adjoint_probing.pdf` and deterministic archive name to `lggr_vi_nonlinear_aggregation_and_adjoint_probing_2026-10-15.zip`.
- **Prose Hygiene:** Replaced defensive deposit-withdrawal phrasing with standard mathematical scope statements and added explicit citation `[3]` in the manuscript body.
