# Blind Spots Under Nonlinear Aggregation and Adjoint Probing

**Author:** Jeremy H. Carroll

**Date:** 2026-10-15

**Version:** 0.1.1

**Paper ID:** LGGR VI

**DOI:** Not assigned

This package studies a finite observation map `Q`. If two states have the same
observation, no deterministic rule applied only to that observation can tell
them apart. The Gram operator `Q.T @ Q` is nonzero exactly when the state has a
component outside `ker(Q)`.

This package is the v0.1.1 preprint release. Earlier preliminary exploratory
prototypes are excluded; they are not paper evidence. Future extensions are
governed by the 25 independently checkable steps in
`docs/research_program_25_steps.md`.

## Package map

- `lggr_vi_nonlinear_aggregation_and_adjoint_probing.md` — manuscript.
- `lggr_vi_nonlinear_aggregation_and_adjoint_probing_claim_ledger.md` — claims and evidence.
- `code/` — self-contained Python implementation and tests.
- `lean4/` — Lean theorems for postprocessing, the rational Gram kernel, and the two probe identities, plus a source-bound axiom report.
- `jupyter_notebooks/` — two executable lessons, from geometric intuition to research-level probes.
- `figures/` — generated visual explanations.
- `docs/` — descriptions, evidence maps, mutation record, and the deferred research program.

## Reproduce the executable evidence

Install [uv](https://docs.astral.sh/uv/) and run from this directory:

```text
uv run --isolated --frozen --extra dev python -m pytest -n 8 \
  --cov=lggr_vi_core --cov=generate_figures \
  --cov-branch --cov-report=term-missing --cov-fail-under=95
uv run --isolated --frozen --extra dev python verify_deposit.py --lean
```

`verify_deposit.py --lean` checks the pinned file set, reruns the complete
Python suite, copies the exact Lean sources to a short temporary path, builds
them, recaptures every theorem-level axiom result, and compares the normalized
result with `lean4/AXIOM_REPORT.txt`. It also requires at least 95% line and 95%
branch coverage independently for each production module. The short copy
avoids the Windows path limit without changing a proof input.

To rebuild the checked-in paper artifacts and deterministic archive:

```text
uv run --isolated --frozen --extra dev python scripts/capture_axiom_report.py
uv run --isolated --frozen --extra dev python scripts/build_paper_artifacts.py
uv run --isolated --frozen --extra dev python scripts/regen_sha256sums.py
uv run --isolated --frozen --extra dev python scripts/build_deposit_zip.py
```

The paper producer hash-checks the live shared preamble at
`coda_university/_kits/obstruction_paper_kit/obstruction_preamble.tex`, bundles
those exact bytes for extracted-archive replay, and runs pdfLaTeX exactly twice.
It does not enable section numbering and does not use XeLaTeX or LuaLaTeX. The
archive is written as
`lggr_vi_nonlinear_aggregation_and_adjoint_probing_2026-10-15.zip`.
`docs/descriptions.md` is the sole source for the Primary and Secondary deposit
descriptions; `zenodo_metadata.json.description` must equal its Primary block.

## Licences

The manuscript, documentation, notebooks, and figures are released under
CC BY 4.0 (`LICENSE`). Python, Lean 4, and release tooling are released under
Apache 2.0 (`LICENSE-CODE`). No DOI is claimed before a deposit is minted.
