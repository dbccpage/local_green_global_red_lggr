# Mutation and falsifier audit

Version 1.2.4 — 2026-10-15

The tests do more than replay successful examples. They first inject an invalid
or misleading case, assert that the implementation catches or exposes it, and
then rerun the corrected case.

| Fault family | Injected break | Expected observation | Recovery |
|---|---|---|---|
| evaluator input | verdict outside \(\{0,1\}\) | ValueError | binary verdict accepted |
| segment input | negative cost, risk, or action | ValueError | non-negative value accepted |
| proposal input | zero, negative, non-finite, or above-one probability | ValueError | probability in \((0,1]\) accepted |
| composition | segment endpoints do not match | ValueError | matching boundary composes |
| boundary slice | missing or undeclared Cartesian segment | G1 validation fails with a diagnostic | complete declared slice validates |
| cancellation | one NGD and one PGD | signed residual is zero while EGD is positive | pointwise counts expose both defects |
| mode selection | unknown kernel or residual mode | ValueError | one of the three documented modes runs |
| sample identity | tampered rate or count | invariant assertion fails | recomputed metric passes |
| expert model | mismatched dimensions or empty joint support | ValueError | normalized compatible input runs |
| detector warning | constant, vacuous, or sample-agreeing evaluators | warning status is present | non-degenerate observed sample avoids the listed warning |

The relevant tests are:

- code/tests/test_invasive_injections.py
- code/tests/test_epk_core.py
- code/tests/test_epk_v121_regressions.py
- code/tests/test_notebooks.py

Release command:

    python -m pytest -n 8 code/tests --cov=epk_core \
      --cov=generate_figures --cov=run_notebook --cov-branch \
      --cov-report=term-missing --cov-fail-under=95

A passing mutation test establishes that a named injected fault is caught. It
does not estimate the frequency of that fault outside the test fixture.
