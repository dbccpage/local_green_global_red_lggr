# Observer-relative control of cochain residuals

Subtitle: A finite mathematical construction with explicit evidence boundaries

## Abstract

We study finite candidate-selection policies constrained by several coordinate
observers. Each observer specifies a projection, positive weights, a space of
removable differences and a closure map. The policy bounds the observer-relative
quotient residual, the closure residual and their ratio. We distinguish two
coordinate estimates: a weighted norm bounds the coordinates of its input,
whereas a quotient seminorm bounds coordinates only of a selected minimizing
residual. Complete coordinate coverage does not remove this distinction.
A one-edge example has zero quotient residual and arbitrarily large raw
coordinates, even with complete observation. We give the corrected estimates,
counterexamples to stronger transfer claims and a finite ranking rule. The
supplied Lean development treats integer weighted norms; a numerical reference
implementation additionally evaluates projected quotient problems.

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

Coordinate coverage does not bound raw cochains by a quotient residual. The corrected theorem bounds selected residuals, or raw vectors under an explicit weighted-input-norm assumption. The reference linear program uses floating-point arithmetic.

## Reproduction

See [quick_start.md](quick_start.md) for installation, tests, the Lean census,
rendering and independent archive checks. The manuscript and documentation use
CC-BY-4.0; software and tests use Apache-2.0.

## Related Identifiers and Citations

Verified scholarly sources are listed in [references.md](references.md).
The version DOI is [10.5281/zenodo.23604797](https://doi.org/10.5281/zenodo.23604797); its verified concept DOI is [10.5281/zenodo.20652483](https://doi.org/10.5281/zenodo.20652483). Zenodo and DataCite identify this as the published October 23, 2026 edition. Earlier package identifiers remain historical and are not asserted as the current concept lineage.
