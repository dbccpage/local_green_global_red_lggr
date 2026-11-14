# Quick Start and Reproduction Guide — LGGR IV

**Date:** 2026-10-15  
**Version:** 0.1.1  

All commands should be executed from the package root.

## 1. Python Environment and Tests

Run the full test suite with parallel execution and branch coverage:

```bash
python -m pytest -n 8 code/tests --cov=lggr_iv_core --cov=generate_figures --cov-branch --cov-report=term-missing
```

The test suite covers:

- Exact finite-stage identity $3x_n + 1 = (-2)^n$ and local divisibility for $n = 1..50$;
- Transition compatibility $x_{n+1} \equiv x_n \pmod{2^n}$;
- Exhaustive integral failure search across range $[-1000, 1000]$;
- 2-adic valuation and metric distance convergence $|x_n - (-1/3)|_2 = 2^{-n}$;
- Reflection descent classification of completion witnesses;
- Moving-witness collision detection for non-finitary defects;
- Clean headless execution of the interactive companion notebook.

## 2. Publication Figures

Generate the publication figures in `public_export/`:

```bash
python code/generate_figures.py
```

Outputs:

- `public_export/figure_1_refinement_tower_and_completion.png`
- `public_export/figure_1_refinement_tower_and_completion.pdf`

## 3. Lean 4 Formalization

Verify the Lean 4 package and axiom census:

```bash
cd lean4
lake build
lake env lean check_axioms.lean
cd ..
```

Verify that no unapproved axioms or placeholder proof tokens exist:

```bash
git grep -E "\b(sorry|admit)\b" -- lean4
```

## 4. Manuscript Build

Rebuild the TeX and PDF artifacts from Markdown source using the shared obstruction preamble:

```bash
python scripts/build_paper_artifacts.py
```

## 5. Deposit Verification

Verify bit-level manifest consistency:

```bash
python verify_deposit.py --lean
```
