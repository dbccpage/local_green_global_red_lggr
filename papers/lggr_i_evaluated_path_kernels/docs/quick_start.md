# Quick start

Version 1.2.4 — 2026-10-15

From the paper directory:

    uv run --isolated --frozen --extra dev python -m pytest -n 8 \
      code/tests --cov=epk_core \
      --cov=generate_figures --cov=run_notebook --cov-branch \
      --cov-report=term-missing

`verify_deposit.py` enforces the 95% statement and branch floors separately
for every production module and for their aggregate.

Compute the five-trace example:

    from epk_core import EPKMetrics, make_five_trace_phone_test
    report = EPKMetrics.compute(make_five_trace_phone_test())
    print(report.lpr, report.gpr, report.mean_delta_e)

The output is 0.60, 0.20, and -0.40.

Generate the figures:

    python code/generate_figures.py

Execute the public entry and falsification notebooks:

    python code/run_notebook.py

Execute all eight supplemental lessons through the tested harness:

    python -m pytest -n 8 code/tests/test_notebooks.py

Build the finite Lean development:

    cd lean4
    lake build

Create the dated archive only after all files are final:

    python scripts/capture_axiom_report.py
    python scripts/build_paper_artifacts.py
    python scripts/regen_sha256sums.py
    uv run --isolated --frozen --extra dev python verify_deposit.py --lean
    python scripts/build_deposit_zip.py

The final path is
`dist/lggr_i_evaluated_path_kernels_2026-10-15.zip`.
