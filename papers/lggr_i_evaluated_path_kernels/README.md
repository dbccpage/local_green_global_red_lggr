# Local Green, Global Red I

## Evaluated Path Kernels for Composed Agent Reliability

Jeremy H. Carroll

Republication version 1.2.4 — 2026-10-15
Zenodo DOI: [10.5281/zenodo.22881911](https://zenodo.org/records/22881911) (lineage / previous version: [10.5281/zenodo.20675803](https://doi.org/10.5281/zenodo.20675803)).

This package studies a finite and directly testable failure mode in composed
systems: two local validators can pass while the end-to-end validator fails.
For binary verdicts, the evaluator defect is

\[
\Delta_E = E_g - E_1E_2 \in \{-1,0,1\}.
\]

The paper derives finite identities for this defect, gives a conditional kernel
composition theorem, and supplies matching Lean 4 and Python artifacts. The
included examples are synthetic. They do not establish a field-wide failure
rate for language-model agents.

## Read and run

- lggr_i_evaluated_path_kernels.md — canonical manuscript.
- lggr_i_evaluated_path_kernels_claim_ledger.md — claim status and evidence.
- docs/lean_claim_map.md — declarations in the nested Lean project.
- code/epk_core.py — reference implementation.
- code/tests/ — unit, falsifier, mutation, and notebook tests.
- jupyter_notebooks/ — eight lessons from first example to reviewer replay.
- public_export/ — generated figures and notebook launchers.

Run the pinned Python checks from this directory:

    uv run --isolated --frozen --extra dev python -m pytest -n 8 \
      code/tests --cov=epk_core --cov=generate_figures \
      --cov=run_notebook --cov-branch --cov-report=term-missing

The pytest configuration keeps notebook kernels in one xdist group to avoid
Windows port-allocation races; the remaining tests still use eight workers.
The deposit verifier checks statement and branch coverage separately, both in
aggregate and for each production module, at a 95% floor.

Run the two public notebooks:

    python code/run_notebook.py

The public archive contains only the entry notebook
00_how_to_read_this_series.ipynb and the falsification notebook
06_reviewer_reference_verification.ipynb. The other six notebooks remain
supplemental lessons in the repository and are exercised by the test suite.

Build the Lean project:

    cd lean4
    lake build

After all source changes are final, refresh the theorem-level Lean report,
build the Markdown-derived TeX/PDF with exactly two pdfLaTeX passes and the
hash-bound shared preamble, then regenerate and verify the deposit:

    python scripts/capture_axiom_report.py
    python scripts/build_paper_artifacts.py
    python scripts/regen_sha256sums.py
    uv run --isolated --frozen --extra dev python verify_deposit.py --lean
    python scripts/build_deposit_zip.py

The default archive is written to
`lggr_i_evaluated_path_kernels_2026-10-15.zip` (pass `--out` for `dist/`).

The verifier checks the pinned file set in both directions, reruns the Python
suite, checks the fresh axiom report, and reproduces the TeX, PDF, and archive
twice. Passing it confirms reproducible package bytes and executable checks;
it is not independent evidence for the empirical hypotheses.

Historical review records under `docs/rt/` bind an earlier archive hash and do
not review the rebuilt archive.

## Mechanization boundary

The Lean development formally mechanizes the finite Boolean and integer-weight theorems
named in docs/lean_claim_map.md. The real exponential specialization of the
path weights and the differentiable activation model are stated and derived
in prose, not mechanized as real analysis.


## Licence

The paper, figures, and documentation are CC BY 4.0 (LICENSE). Python, Lean,
and release tooling are Apache 2.0 (LICENSE-CODE).

## Citation

    @article{carroll2026lggr1,
      author  = {Jeremy H. Carroll},
      title   = {Local Green, Global Red I: Evaluated Path Kernels for
                 Composed Agent Reliability},
      year    = {2026},
      version = {1.2.4},
      doi     = {10.5281/zenodo.22881911},
      url     = {https://zenodo.org/records/22881911},
      note    = {Zenodo version lineage 10.5281/zenodo.20675803}
    }
