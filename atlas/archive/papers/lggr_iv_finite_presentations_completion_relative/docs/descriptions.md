# Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction (LGGR IV)

Subtitle: Finite Presentations, Projective Limits, and Original-Carrier Lifting Failures

## Abstract

Local Green, Global Red IV is an expository technical preprint examining the distinction among solvability at every finite stage, existence of a compatible inverse-limit thread, and realization of that thread by an element of the original carrier. Its central arithmetic example considers the congruences 3x + 1 ≡ 0 (mod 2^n). Explicit finite-stage solutions form a compatible thread converging to the unique solution -1/3 in the 2-adic integers, while no ordinary integer satisfies every stage simultaneously. The paper develops finite-descent and reflection-image criteria, reviews the nonemptiness theorem for inverse limits of finite nonempty sets, and summarizes the R¹ lim← lifting obstruction for countable towers of abelian groups together with its vanishing under the Mittag–Leffler condition. Companion materials include Python tests, a Jupyter notebook, reproducible figures, and Lean 4 proofs of the arithmetic core. The work is intended as a mathematical foundation for staged evaluation and governance architectures; completion-level solvability is not treated as evidence of validity in the original operational carrier.

## Why This Matters

Systems engineering, formal verification, and multi-stage evaluation pipelines frequently assume that passing all finite approximation stages or boundary tests ensures the existence of a global solution in the intended execution environment. This monograph formalizes the boundary where this heuristic fails. By providing exact arithmetic counterexamples and categorical criteria, it establishes that local stage green verdicts and completion green solutions cannot be laundered into original-carrier validity without explicit reflection descent certification.

## Core Theorems

- Theorem LGGR4-M1 (Moving-Witness Collision Criterion): Under surjective observation maps, a defect predicate D fails to have finite descent if and only if at every finite stage there exist distinct elements sharing the same stage presentation but differing under D. Lean formalizes this equivalence for a finite complete state list with one default output (`LggrIV.finite_notFinDesc_iff_collisions`). An arbitrary non-enumerated carrier is not a separate Lean theorem.
- Theorem LGGR4-M2 (Finite-Chain Thread): One element of the last stage, pulled back along a finite list of transition maps, yields a nonempty compatible thread (`LggrIV.finite_chain_limit_nonempty`). The cofiltered nonemptiness statement remains the classical citation Stacks Tag 086J. It does not ensure descent to the original carrier.
- Theorem LGGR4-M3 (Explicit Finite-Stage Solution): For x_n = −∑_{k=0}^{n−1} (−2)^k, the identity 3x_n + 1 = (−2)^n holds for all n ≥ 1, yielding local divisibility 2^n | (3x_n + 1) at every stage (Local Green).
- Theorem LGGR4-M4 (Sequence Compatibility): The sequence satisfies x_{n+1} − x_n = −(−2)^n ≡ 0 (mod 2^n), forming a coherent thread in the projective limit.
- Theorem LGGR4-M5 (Absence of Integral Global Lift): There exists no integer x ∈ ℤ satisfying 2^n | (3x + 1) for all n ≥ 1 (Global Red in original carrier).
- LGGR4-M6 (Completion Solution and Metric Convergence) is cited from classical 2-adic analysis. In the 2-adic integers ℤ_2, 3 is a unit and 3x + 1 = 0 admits the unique solution x_∞ = −1/3; the compatible thread converges 2-adically with distance |x_n − (−1/3)|_2 = 2^{−n} (Completion Green).
- Theorem LGGR4-M7 (Reflection Descent Criterion): A completed solution descends to the original carrier if and only if it belongs to the image of the canonical reflection embedding η (formalized in Lean via definition unfolding `rfl`).
- Theorem LGGR4-M8 (Finite Overlap Identity): For a finite list of families, the primal defect is 0 when k* equals the family count and 2(B-k*) otherwise, and that value equals the dual μ − ∑α_i (`LggrIV.overlap_dual_residual`). A nonempty list with k*=B has a common element. Stacks Tag 07KV remains a citation.

## Formal Verification and Computational Artifacts

- Lean 4 Mechanization: Formalization of core arithmetic claims M3, M4, M5, reflection descent definition D3/M7, the finite complete-list moving-witness equivalence M1, the finite-chain thread M2, and the finite overlap identity M8 in `lean4/core.lean` under Lake v4.33.1. All proofs pass the kernel axiom audit (`lean4/check_axioms.lean`) restricted strictly to standard kernel axioms (`propext`, `Quot.sound`), with zero `sorry` or `admit` tokens. Stacks Tag 086J and Stacks Tag 07KV are citations.
- Python Reference Engine: Exact rational and integer arithmetic reference implementation in `code/lggr_iv_core.py`, backed by comprehensive pytest test suites in `code/tests/` achieving 100% line and branch coverage.
- Publication Figures: Vector figure generation in `code/generate_figures.py` rendering the refinement tower and 2-adic completion embedding in `public_export/figure_1_refinement_tower_and_completion.pdf`.
- Jupyter Companion Notebook: Headless-verified interactive walkthrough in `jupyter_notebooks/001_finite_presentations.ipynb` demonstrating thread construction, 2-adic metric convergence, and reflection descent classification.

## Scope Boundaries and Non-Claims

- Pure Mathematics Scope: The results establish mathematical and categorical boundaries for projective limits and completion descent. They do not claim physical spacetime discreteness or quantum mechanics emergence.
- No Completion Laundering: Solvability in a completion space or passing a countable tower of finite tests does not prove original-carrier existence.
- Non-Authority Invariant: Computational test passes and mechanical verification receipts document local consistency and do not mint unconditioned authority certificates.

## Reproduction

1. Environment Setup: Ensure Python 3.10+ and Lean 4 toolchain v4.33.1 are installed.
2. Run Test Suite: `python -m pytest -n 8 code/tests --cov=lggr_iv_core --cov=generate_figures --cov-branch`
3. Verify Lean Proofs: `cd lean4 && lake build && lake env lean check_axioms.lean && cd ..`
4. Compile Manuscript: `python scripts/build_paper_artifacts.py`
5. Verify Deposit Envelope: `python verify_deposit.py --lean`

## Related Identifiers & Citations

- Stacks Project: Tag 086J (Limits of finite sets) and Tag 07KV (Derived inverse limits and Mittag–Leffler).
- Series Predecessors: Local Green, Global Red I (Evaluated Path Kernels), II (Organizational Gluing), and III (A Finite Evaluator Overlay Across Six System Roles).
