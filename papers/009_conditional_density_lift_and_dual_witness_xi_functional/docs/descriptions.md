# Conditional density lifts and a primal–dual alignment statistic

Subtitle: A finite mathematical construction with explicit evidence boundaries

## Abstract

A nonzero real vector can be mapped to a unit vector by taking signed square
roots of its normalized absolute coordinates. The associated rank-one projector
retains relative magnitudes and signs while forgetting total mass and common
sign. We apply this construction to an optimal residual and an optimal dual
witness for a finite-dimensional minimum-distance problem in the sum norm.
Their trace distance defines an alignment statistic. Complementary slackness
gives a strict upper bound below one for every optimal pair, and characterizes
the zero-distance case. Successive coordinate minimization selects a unique
pair once a coordinate order is fixed. The construction is undefined at a zero
residual; a separate convention assigns the statistic the value zero there.
We give proofs, an explicit example, and a selection policy that uses the
statistic only after primary residual comparisons. The accompanying numerical
implementation and discrete Lean results have distinct, stated scopes.

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

The real projector construction and strict primal-dual distance bound have prose proofs. Lean checks discrete integer and rational statements. Numerical vector evaluation does not establish optimality or compute the canonical selector.

## Reproduction

See [quick_start.md](quick_start.md) for installation, tests, the Lean census,
rendering and independent archive checks. The manuscript and documentation use
CC-BY-4.0; reference software and tests use MIT. The renderer, Lua filter and path helper
retain Apache-2.0; see the component table in README.md.

## Related Identifiers and Citations

Verified scholarly sources are listed in [references.md](references.md).
The version DOI is [10.5281/zenodo.23604860](https://doi.org/10.5281/zenodo.23604860); its verified concept DOI is [10.5281/zenodo.20192296](https://doi.org/10.5281/zenodo.20192296). Zenodo and DataCite identify this as the published October 23, 2026 edition. The earlier record 10.5281/zenodo.20192297 belongs to the same concept DOI; the existing lineage is preserved.
