# Quick start — LGGR III

**Version:** 1.5.2\
**Date:** 2026-10-15

## Prerequisites

- Python 3.11 or newer
- Lean 4.33.1 through Elan/Lake
- a TeX/Pandoc toolchain only when rebuilding the PDF

## Python

From the package root:

    uv sync --frozen --extra dev
    uv run --frozen --extra dev python -m pytest -n 8 code/tests \
      --cov=epk_gtla_overlay_core \
      --cov=generate_figures \
      --cov=run_notebook \
      --cov-branch \
      --cov-report=term-missing \
      --cov-fail-under=95

The suite includes unit checks, twelve paired break-detect-recover mutations,
two-run figure hashing, notebook structure checks, and headless notebook
execution. `verify_deposit.py` additionally enforces at least 95% branch-aware
coverage for each production module separately.

## Notebooks

Run the public sequence (`00_start_here.ipynb` through `06_reviewer_verification.ipynb`):

    uv run --frozen --extra dev python code/run_notebook.py

This is the one documented public launcher. The notebooks support both novice and professional
reading routes; interactive widgets are optional during headless execution.

## Lean

From the package root:

    cd lean4
    lake build
    lake env lean check_axioms.lean

On Windows, a checkout whose full path exceeds the toolchain's file-creation
limit can be copied byte-for-byte to a short temporary directory for the build.
That workaround changes no source and must be reported as environmental.

## Figures and paper

Generate both figures:

    uv run --frozen --extra dev python code/generate_figures.py

Build the TeX and PDF when Pandoc and pdfLaTeX are available. The script uses
the bundled shared preamble and runs pdfLaTeX until auxiliary state converges:

    python scripts/build_paper_artifacts.py

## Deposit verification

After every intended file is final:

    uv run --frozen --extra dev python scripts/regen_sha256sums.py
    uv run --frozen --extra dev python verify_deposit.py --lean

The verifier does not upload or mint a DOI. The archive builder creates the
byte-reproducible dated archive
`lggr_iii_epk_gtla_overlay_2026-10-15.zip` only after verification succeeds:

    uv run --frozen --extra dev python scripts/build_deposit_zip.py
