# Notebook curriculum

Version 1.2.4 — 2026-10-15

The notebooks take a reader from a concrete five-row table to the finite
composition theorem and its falsification protocol. Each lesson contains:

- a plain-language intuition;
- one hand calculation before automation;
- production-code replay;
- a plot or an interactive control;
- an exercise with a solution;
- links to the manuscript, claim ledger, Python test, and Lean declaration;
- a short statement of what the example cannot establish.

## Learning path

| Order | Notebook | Purpose |
|---:|---|---|
| 0 | 00_how_to_read_this_series.ipynb | orient the reader and select a route |
| 1 | 01_the_five_trace_phone_test.ipynb | compute the basic defect by hand |
| 2 | 02_the_evaluator_defect_trichotomy.ipynb | visualize negative, positive, and zero defects |
| 3 | 03_boundary_slices_and_composition.ipynb | explore G1–G3 and the residual |
| 4 | 04_why_green_evaluators_can_lie.ipynb | break degenerate evaluator configurations |
| 5 | 05_cancellation_and_poe_vs_moe.ipynb | expose signed cancellation and model tradeoffs |
| 6 | 06_reviewer_reference_verification.ipynb | rerun and falsify the main finite claims |
| 7 | 07_llm_and_agentic_pipelines.ipynb | map the model to multi-step agent traces |

The sequence is supplemental; a reader can complete 00 and 06 for a compact
entry/falsification route. Those two notebooks are the only notebook members
of the public archive.

## Execution

The notebooks import the shipped code through epk_nb.py and use no
machine-local paths. Interactive controls are optional; EPK_HEADLESS=1 selects
deterministic non-interactive execution.

    python code/run_notebook.py
    python -m pytest -n 8 code/tests/test_notebooks.py
