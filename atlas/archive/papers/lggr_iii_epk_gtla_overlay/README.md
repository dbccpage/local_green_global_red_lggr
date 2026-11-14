# Local Green, Global Red III

This archive accompanies “A finite evaluator overlay across six system
roles,” version 1.5.2 (2026-10-15).

The package studies the signed discrepancy

$$
\Delta_E=e_g-e_1e_2
$$

between a verdict on a composite and the product of two local verdicts. It
contains the paper, a concise Python implementation, mutation tests, seven
teaching and verification notebooks, two generated figures, and a Lean 4 library.

## Quick verification

Install the development dependencies and run the full Python suite:

    uv sync --frozen --extra dev
    uv run --frozen --extra dev python -m pytest -n 8 code/tests --cov=epk_gtla_overlay_core \
      --cov=generate_figures --cov=run_notebook --cov-branch \
      --cov-report=term-missing --cov-fail-under=95

Build and audit the nested Lean library:

    (cd lean4 && lake build && lake env lean check_axioms.lean)

The archived `lean4/AXIOM_REPORT.txt` is regenerated from those current
theorem declarations and compared byte-for-byte by the verifier.

Verify the final deposit tree:

    uv run --frozen --extra dev python verify_deposit.py --lean

Build the deterministic dated archive:

    uv run --frozen --extra dev python scripts/build_deposit_zip.py

The release verifier checks the manuscript companions, per-module branch
coverage, notebooks, Lean handles, metadata, PDF identity, checksum manifests,
deterministic figures, and public archive selection. It does not upload
anything.

The review files under `docs/rt/` bind an earlier archive hash. They remain
historical review records; the archive rebuilt from this repair has not been
separately re-reviewed under that historical snapshot.

## Teaching notebooks

The public package has seven ordered notebooks following dedicated reading routes:

- `00_start_here.ipynb` orientation, glossary, and reading routes;
- `01_two_passes_one_failure.ipynb` introduces all eight binary cases and elementary defect;
- `02_why_zero_can_mislead.ipynb` examines finite sums, agreement vs success, and cancellation;
- `03_when_paths_compose.ipynb` attacks boundary bijection multiplicity and factorization hypotheses;
- `04_when_grouping_loses_information.ipynb` analyzes equivalence classes and quotient descent;
- `05_one_record_six_roles.ipynb` examines a concrete byte-order failure across all six roles;
- `06_reviewer_verification.ipynb` audits formal claims, production core, and fixtures.

Novice route: 00 -> 01 -> 02 -> 04 -> 05.  
Professional route: 00 -> 03 -> 04 -> 05 -> 06.

They contain no machine-specific or unavailable repository paths. The sole
documented launcher family is the package-local Python command below.

Run the public sequence headlessly:

    uv run --frozen --extra dev python code/run_notebook.py

## Package map

| item | purpose |
|---|---|
| lggr_iii_epk_gtla_overlay.md | primary manuscript |
| lggr_iii_epk_gtla_overlay_claim_ledger.md | typed claims and open obligations |
| lggr_iii_epk_gtla_overlay_change_log.md | version lineage |
| code | current finite implementation, figure generator, launcher, and tests |
| lean4 | local formalization and axiom audit |
| jupyter_notebooks | seven teaching and verification notebooks |
| docs | public descriptions, references, and claim maps |
| public_export | generated publication figures |
| zenodo_metadata.json | deposit metadata draft |
| MANIFEST.sha256 and SHA256SUMS | final byte inventory |
| scripts/obstruction-preamble.tex | exact shared pdfLaTeX preamble bundled for replay |

## Evidence scope

The verified results are finite identities and computed finite-data guards. In
particular, a zero observed defect is not a general reliability guarantee; a
task-specific evaluator-adequacy result remains open. See PL-025-6 through
PL-025-9 in the claim ledger.

An earlier omnibus snapshot is retained outside the public deposit for
provenance. Its eight notebooks and four figures are byte-preserved in
`research/legacy_omnibus/`. It is excluded from release evidence and is not
current claim evidence.

## License

See LICENSE for the manuscript and LICENSE-CODE for the software.
