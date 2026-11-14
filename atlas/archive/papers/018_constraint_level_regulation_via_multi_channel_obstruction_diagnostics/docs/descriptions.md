# Candidate selection with residual and constraint diagnostics

Subtitle: A finite mathematical construction with explicit evidence boundaries

## Abstract

We specify a finite candidate-selection rule using a quotient residual,
constraint violations, a closure residual, interface discrepancies and a
secondary alignment statistic. The quotient and closure residuals satisfy an
operator-norm inequality, so these channels are not algebraically independent.
Candidates must satisfy literal non-increase of the quotient residual and an
exact ratio ceiling before entering a two-stage tolerance ranking. A separate
inequality can screen representation-expanding proposals. We establish the
residual bound, explain the ranking rule and give counterexamples to stronger
interpretations: a ratio ceiling does not preserve constraints against deletion,
and greedy candidate selection does not establish convergence. The implementation
provides exact rational decision routines alongside a numerical interface.

## Why This Matters

The paper distinguishes what its diagnostic inequalities measure from stronger
claims that do not follow. Explicit definitions and counterexamples make the
selection policy and its limits inspectable.

## Core Theorems

The numbered propositions and proofs in the manuscript state their domains and
hypotheses. The revision separates quotient residuals, input norms, discrete
formal lemmas and numerical evaluations rather than treating them as equivalent.

## Formal Verification and Computational Artifacts

The package includes source code, tests, a pinned standalone Lean project, an
explicit declaration census and source-bound rendered files. The quick start
gives commands for replay. Each formal result retains the scope described in the
manuscript; test outcomes do not supply a theorem beyond that scope.

## Scope Boundaries and Non-Claims

Selection does not establish feasibility, constraint preservation or convergence. The ratio test does not detect deletion. Lean verifies discrete comparisons; the general cochain inequality has a separate prose proof.

## Reproduction

See [quick_start.md](quick_start.md) for installation, tests, the Lean census,
rendering and independent archive checks. The manuscript and documentation use
CC-BY-4.0; reference software and tests use MIT. The renderer, Lua filter and path helper
retain Apache-2.0; see the component table in README.md.

## Related Identifiers and Citations

Verified scholarly sources are listed in [references.md](references.md).
The new revision has no assigned DOI. The previous record is [10.5281/zenodo.20214310](https://doi.org/10.5281/zenodo.20214310); its verified parent is [10.5281/zenodo.19322638](https://doi.org/10.5281/zenodo.19322638). The metadata records these version relationships.
