# Reproduction guide

**Date:** 2026-10-15\
**Version:** 1.3.1

Run every command from the package root unless the command changes directory.

## Python

The project supports Python 3.11 or later; this release lock was resolved and
verified with Python 3.12. Use the checked-in `uv.lock` without re-resolving it:

```bash
uv run --isolated --frozen --python <python-3.12> --extra dev \
  python -m pytest -n 8 code/tests \
  --cov=organizational_gluing_core --cov=generate_figures --cov-branch \
  --cov-report=term-missing --cov-report=json:<external-temp>/coverage.json
```

The suite includes unit tests, twelve break-and-recover injections, figure
generation, and a clean headless execution of the public notebook.
The release verifier independently rejects line/statement coverage below 95
percent or branch coverage below 95 percent for the two production modules.

## Figures

```bash
uv run --isolated --frozen --python <python-3.12> --extra dev \
  python code/generate_figures.py
```

This writes PNG and PDF versions of two figures to `public_export/`.

## Lean 4

The pinned toolchain is recorded in `lean4/lean-toolchain`.

```bash
cd lean4
lake build LGGR2
lake env lean check_axioms.lean
cd ..
```

Then scan only source files:

```bash
rg -n "\b(sorry|admit)\b" lean4 -g "*.lean"
```

No match is expected. Build output is intentionally excluded from the archive.

## Paper artifacts

The builder verifies the Lean target, refreshes `lean4/axiom_report.txt`, and
uses Pandoc with the byte-pinned shared obstruction preamble. It then runs
pdfLaTeX twice and writes the TeX and PDF beside the Markdown source.

```bash
python scripts/build_paper_artifacts.py
```

## Deposit

Only after the final source, notebook, figures, TeX, and PDF checks pass:

```bash
python scripts/regen_sha256sums.py
uv run --isolated --frozen --python <python-3.12> --extra dev \
  python verify_deposit.py --lean
python scripts/build_deposit_zip.py
```

For an independent check, unpack the resulting archive into a new directory,
then repeat the frozen verifier command there. No script in this package
uploads an archive or mints a DOI.
The default archive is
`lggr_ii_organizational_gluing_2026-10-15.zip`.
