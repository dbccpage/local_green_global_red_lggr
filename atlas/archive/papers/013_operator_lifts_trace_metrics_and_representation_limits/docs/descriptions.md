# Scientific description

Operator Lifts Trace Metrics and Representation Limits

Jeremy H. Carroll. Prepared edition 2.1.1, 2026-10-23.

## Abstract

We compare two representations of a finite real cochain: its diagonal operator and the rank-one projector obtained from its normalized signed square-root coordinates. The diagonal map is injective and preserves the sum-of-absolute-values norm as trace norm. The projector identifies precisely the nonzero scalar multiples of a cochain, losing mass and global orientation while retaining every diagnostic constant on those fibers. Trace distance defines a pseudometric on nonzero cochains and a metric on their real projective quotient. We prove a chain-complex residual bound, describe local reconstruction using an orientation anchor, and show that a continuous global sign choice is impossible in dimension at least two. A guarded evaluator uses these representations under an explicit selection policy. The real-vector arguments are written proofs; the Lean package verifies narrower integer and rational identities. No physical quantum interpretation is asserted.

## What changed

Completed the fixed-mass sign-selection proof, including continuity of the sign coefficient and restriction to a two-dimensional subspace. Scoped numerical stability claims to floating-point limitations. Added a bibliography and removed the inherited Ricard citation whose arXiv identifier resolves to an unrelated work.

## What the package establishes

The manuscript states its domains and assumptions. Written arguments, finite regression checks, and Lean statements have separate scopes recorded in the claim ledger. The mathematical spine binds each formula occurrence to a persistent expression identity. A successful conversion check establishes the defined source-form comparison, not mathematical truth.

## Replication and limitations

The README gives standalone build and verification commands. The archive includes the manuscript in four formats, canonical spine, claim ledger, typed source inventory, render receipt, reference implementation, tests, Lean sources, and manifests. Named PDF destinations locate equations for inspection; independent glyph-to-symbol equivalence remains unresolved. This edition is prepared for republication; no new public deposit or DOI is asserted.
