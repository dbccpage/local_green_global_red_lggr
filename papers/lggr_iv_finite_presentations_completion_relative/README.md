# Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction

**Author:** Jeremy H. Carroll  
**Date:** 2026-10-15  
**Version:** 0.1.1  
**DOI:** Not assigned  

Evaluator agreements across finite stages of an inverse system need not imply the existence of a solution in the original carrier. On a finite chain, one element of the last stage pulls back along the transition maps to a nonempty compatible thread. The general statement that a cofiltered inverse limit of nonempty finite sets is nonempty is cited from Stacks Tag 086J. Thread existence does not imply realization by an element of the original carrier: in an explicit $2$-adic arithmetic family, the congruence $3x+1 \equiv 0 \pmod{2^n}$ admits an exact solution $x_n = -\sum_{k=0}^{n-1}(-2)^k$ at every stage $n$ and forms a compatible thread, yet no integer satisfies all stages simultaneously because $2^n \mid 3x+1$ for all $n \ge 1$ forces $x = -1/3 \notin \mathbb{Z}$. The unique solution lives in the completion $\mathbb{Z}_2$. We formulate a general reflection image criterion: completed solutions descend to original-carrier solutions if and only if they belong to the image of the canonical reflection map $\eta$. For a finite list of families, the overlap defect $2(B-k^*)$ equals the dual value used by the rational certificate, and it vanishes when a common element exists. The general statement that the Mittag–Leffler condition implies $R^1 \varprojlim A_n = 0$ is cited from Stacks Tag 07KV.

## Core Structure

```text
├── code/
│   ├── lggr_iv_core.py                  # Exact integer/rational arithmetic, reflection classification
│   ├── generate_figures.py              # Figure 1 publication generator
│   └── tests/
│       ├── test_finite_chain_and_overlap.py  # Finite-chain thread (M2) and overlap identity (M8)
│       ├── test_lggr_iv_core.py         # Unit tests covering M1-M7
│       ├── test_derived_limits.py       # Non-abelian derived limits & ML obstruction tests (M8)
│       ├── test_rational_duality.py     # Exact rational LP/SDP duality certifier on Q[G] (M8)
│       └── test_notebook.py             # Headless notebook execution test
├── docs/
│   ├── descriptions.md                  # Public release descriptions
│   ├── keywords.md                      # Keyword taxonomy
│   ├── lean_claim_map.md                # Mechanized declaration mapping
│   ├── nonclaims.md                     # Claim hygiene fences
│   ├── quick_start.md                   # Reproduction instructions
│   └── references.md                    # Primary bibliographic sources
├── jupyter_notebooks/
│   └── 001_finite_presentations.ipynb
├── lean4/
│   ├── core.lean                        # Pure Lean 4 proofs of M1, the finite-chain M2, M3, M4, M5, M7, and the overlap M8
│   ├── check_axioms.lean                # Axiom census (#print axioms)
│   ├── lakefile.lean                    # Package configuration
│   ├── lean-toolchain                   # Toolchain pin (v4.33.1)
│   └── axiom_report.txt                 # Recorded axiom dependencies
├── public_export/
│   ├── figure_1_refinement_tower_and_completion.png
│   └── figure_1_refinement_tower_and_completion.pdf
├── scripts/
│   ├── build_deposit_zip.py             # Builds publishable release zip from pinned manifest
│   ├── build_paper_artifacts.py         # Builds TeX, PDF, and axiom report
│   ├── obstruction-preamble.tex         # Canonical LaTeX preamble
│   └── regen_sha256sums.py              # Checksum manifest generator
├── lggr_iv_finite_presentations_completion_relative.md
├── lggr_iv_finite_presentations_completion_relative.tex
├── lggr_iv_finite_presentations_completion_relative.pdf
├── lggr_iv_finite_presentations_completion_relative_claim_ledger.md
├── lggr_iv_finite_presentations_completion_relative_change_log.md
├── pyproject.toml
├── verify_deposit.py                    # Independent deposit verification harness
├── LICENSE                              # CC BY 4.0
└── LICENSE-CODE                         # Apache-2.0
```

## Quick Reproduction

1. **Run Python tests:**

   ```bash
   python -m pytest -n 8 code/tests --cov=lggr_iv_core --cov-branch --cov-report=term-missing
   ```

2. **Verify Lean formalization:**

   ```bash
   cd lean4
   lake build
   lake env lean check_axioms.lean
   cd ..
   ```

3. **Verify Deposit:**

   ```bash
   python verify_deposit.py --lean
   ```
