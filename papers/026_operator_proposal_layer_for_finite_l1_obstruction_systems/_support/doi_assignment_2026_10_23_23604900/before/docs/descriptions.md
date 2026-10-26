# Proposal selection and continuation-stable diagnostics on finite graphs

Subtitle: A finite mathematical construction with explicit evidence boundaries

## Abstract

We separate the generation of candidate edge fields from a decision rule based
on independently computed diagnostics. On a finite connected graph, distance
to the image of the incidence map measures failure of exactness. A declared
face map supplies a closure residual. A lexicographic comparison of diagnostics,
subject to a ratio condition, defines one proposal-selection policy. Equal
diagnostic traces have equal decisions by construction, but equal current
diagnostics need not remain equal after further proposals. For a declared
family of transformations, we characterize the largest equivalence relation
inside diagnostic equality that is preserved by every finite continuation.
We give explicit cycle examples distinguishing local exactness from global
exactness, and one-step decisions from continuation-stable state compression.
Executable paths additionally require agreement of adjacent endpoint states.
The accompanying exact rational checks and Lean results are scoped to their
stated finite and abstract objects.

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

The scalar graph solver uses exact rational witnesses. The vector-valued extension is mathematical, not a generic numerical implementation. Label erasure for one-step decisions does not imply stable state compression under arbitrary continuations.

## Reproduction

See [quick_start.md](quick_start.md) for installation, tests, the Lean census,
rendering and independent archive checks. The manuscript and documentation use
CC-BY-4.0; software and tests use Apache-2.0.

## Related Identifiers and Citations

Verified scholarly sources are listed in [references.md](references.md).
The new revision has no assigned DOI. The previous record is [10.5281/zenodo.20213064](https://doi.org/10.5281/zenodo.20213064); its verified parent is [10.5281/zenodo.20213063](https://doi.org/10.5281/zenodo.20213063). The metadata records these version relationships.
