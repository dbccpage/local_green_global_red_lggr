# Local Green, Global Red I: Evaluated Path Kernels for Composed Agent Reliability (LGGR-001)

Subtitle: Boundary Sufficiency, Defect Mass, and Proposal-Weighted Trajectories

## Abstract

Local Green, Global Red I develops a finite, auditable calculus for a recurring failure mode in composed agent systems: each stage can pass a local evaluator while the completed trajectory fails a global evaluator. For binary stage and global verdicts, the paper defines the evaluator defect Δ_E = E_g − E_1 E_2 ∈ {−1, 0, 1} and introduces evaluated path kernels whose exact composition is proved under explicit boundary-slice, weight-factorization, and evaluator-factorization hypotheses.

The analysis derives a residual-corrected composition identity, separates evaluator mismatch from weight mismatch, characterizes cancellation and information loss in aggregate dashboards, and gives conditional treatments of proposal-weighted paths and Product-of-Experts versus Mixture-of-Experts aggregation. A prospective falsification protocol explains how the framework could be tested on multi-step agent benchmarks.

The contribution is deliberately scoped: the theorems are finite or conditional, the examples are finite synthetic fixtures, and no benchmark-performance or deployment-reliability result is claimed. Version 1.2.4 is a corrected and expanded republication in the existing Zenodo version lineage. Reproducibility materials and the authoritative file inventory are documented in the accompanying README and manifest.

## Why This Matters

In composed agentic workflows, multi-stage language-model pipelines, and distributed verification systems, pipelines frequently execute local validator or unit checks at intermediate boundaries. A common implicit assumption is that local validation ensures global correctness (E₁ = 1 ∧ E₂ = 1 ⇒ E_g = 1). This paper shows that this assumption fails on finite discrete systems and provides exact algebraic identities and residual terms measuring the failure of evaluators to compose.

By isolating the evaluator gluing defect Δ_E and demonstrating that aggregate pass rates (LPR, GPR) conflate and cancel pointwise discrepancies, this work provides a rigorous foundation for trajectory-level process supervision and boundary sufficiency without relying on unvalidated heuristic claims.

## Core Theorems

- Theorem 1 (Evaluated Path-Kernel Composition): Under boundary-slice decomposition (G1), multiplicative weights (G2), and evaluator factorization (G3), evaluated path kernels compose exactly over intermediate boundary slices: Z_E(c | a) = ∑_{b ∈ B} Z_{E₂}(c | b) Z_{E₁}(b | a).
- Theorem D2 (Residual Decomposition): When evaluator factorization fails, the exact difference is captured by a signed residual: Z_E(c | a) = ∑_{b ∈ B} Z_{E₂}(c | b) Z_{E₁}(b | a) + R_E(c, a), where R_E(c, a) = ∑_{b, γ₂, γ₁} Δ_E(γ₂, γ₁) w₂(γ₂) w₁(γ₁).
- Theorem D3 (Fully Corrected Two-Channel Expansion): When both evaluator and weight factorization fail (w_g = w₁ w₂ + Δ_w), each global contribution expands into four exact terms: E_g w_g = E₁ E₂ w₁ w₂ + Δ_E w₁ w₂ + E₁ E₂ Δ_w + Δ_E Δ_w.
- Theorems E2–E8 (Finite Defect Identities and Trichotomy): Binary local and global verdicts partition every trace into exactly one of three defect classes: Negative Gluing Defect (NGD, Δ_E = −1), Zero Defect Residual (ZDR, Δ_E = 0), or Positive Gluing Defect (PGD, Δ_E = +1). The signed defect sum equals PGD count minus NGD count, and GPR − LPR = mean(Δ_E).
- Theorem E9 (Pass Rates Do Not Determine Gluing Defects): Local pass rate (LPR) and global pass rate (GPR) determine the signed balance n₊ − n₋, but do not determine the absolute gluing defect EGD = (n₋ + n₊) / N.
- Theorem E12–E16 (Diagnostic Quotient Information): The pair (L, E_g) carries the defect packet (Δ_E, kind). Three diagnostic classes exist, so no single Boolean key can encode the exact diagnostic quotient.
- Theorems I1–I7 (Carrier Collision Obstruction): A target verdict varying within a packet fiber cannot factor through packet-bounded evaluators (e ∘ π). In particular, a locally green fiber containing mixed global verdicts forces the presence of an NGD trace, and post-composition cannot separate collided observations.

## Formal Verification and Computational Artifacts

- Lean 4 Mechanization: Standalone package in lean4/ compiling all modules with zero sorry placeholders and zero errors. Formally verifies finite Boolean trichotomy, count identities, integer-weight kernel composition, residual identities, and carrier quotient collision theorems against standard kernel axioms {propext, Quot.sound}.
- Python Reference Engine: Self-contained reference implementation in code/epk_core.py with 134 passing tests achieving >95% statement and branch coverage. Implements exact trajectory segments, boundary slices, evaluator defect calculations, metric reports, and detector adequacy guards.
- Jupyter Review Notebooks: Eight replayable notebooks in jupyter_notebooks/ (including 00_how_to_read_this_series.ipynb and 06_reviewer_reference_verification.ipynb) executing headlessly via nbclient.
- Standalone Solvers & Bundled Dependencies: Pinned Python environment via uv.lock, deterministic hash verification, and reproducible document builders.

## Scope Boundaries and Non-Claims

- Finite Discrete Trajectories: All theorems are proved for finite symbolic path spaces with non-negative weights; continuous path integrals, complex quantum amplitudes, and measure-theoretic continuous state spaces are not considered.
- Synthetic Fixtures: Numerical examples and figures are illustrative synthetic fixtures; they do not establish empirical failure rates for deployed LLMs.
- Mechanization Boundary: Real exponential weights and differentiable active support curves are derived in prose and tested in Python; formal Lean proofs cover the Boolean and integer algebraic models.
- No Operational Authorization: The framework provides diagnostic measurement of composition failure; it does not confer operational deployment authorization.

## Reproduction

Execute verification suite and tests directly:

    uv run --isolated --frozen --extra dev python -m pytest -n 8 code/tests --cov=epk_core --cov-branch

Replay companion notebooks:

    python code/run_notebook.py

Build Lean 4 formal proofs:

    cd lean4 && lake build

## Related Identifiers & Citations

- Zenodo DOI: 10.5281/zenodo.22881911
- Zenodo Record: https://zenodo.org/records/22881911
- Lineage DOI: 10.5281/zenodo.20675803 (previous version record v0.2)
- Canonical Paper: Local Green, Global Red I: Evaluated Path Kernels for Composed Agent Reliability (Version 1.2.4, 2026-10-15)
