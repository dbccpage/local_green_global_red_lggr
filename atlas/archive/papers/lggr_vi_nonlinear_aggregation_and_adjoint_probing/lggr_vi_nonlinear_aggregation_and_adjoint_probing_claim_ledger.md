# Claim ledger: nonlinear aggregation and adjoint probing

- **Paper:** `lggr_vi_nonlinear_aggregation_and_adjoint_probing`
- **Version:** 0.1.1
- **Date:** 2026-10-15

| ID | Type | Mechanization | Claim | Manuscript | Support | Scope |
|---|---|---|---|---|---|---|
| `LGGRVI-C01` | `[PROVED] theorem` | `LEAN_FULL` | Equal observations remain equal after every deterministic observation-only postprocessor. | Theorem 1 | `lean4/Core.lean::postprocessing_invariance`; Python postprocessor test | Arbitrary types and deterministic functions. |
| `LGGRVI-C02` | `[PROVED] theorem` | `LEAN_FULL` | A zero-preserving postprocessor accepts every state observationally equivalent to the zero state. | Corollary 1 | `lean4/Core.lean::zero_preserving_accepts_hidden`; Python unanimous and k-of-n tests | The verdict sees only `Qx`. |
| `LGGRVI-C03` | `[CLASSICAL] classical background` | `N/A` | The Euclidean cylinder bound stays visible as classical SVD background. It is not mechanized here. | Theorem 2 | SVD paragraph remains in the manuscript. `cylinder_radius` is a float helper, not the proof. | Real singular values are outside the rational Lean development. |
| `LGGRVI-C04` | `[PROVED] theorem` | `LEAN_FULL` | For every finite rational matrix, `Hx = 0` exactly when `Qx = 0`. | Theorem 3 | `lean4/Core.lean::gram_kernel_iff` and `gram_detectable_iff`; `test_exact_rational_identities_call_shipped_checkers` | Finite rational matrices. `range(H) = (ker Q)` orthogonal complement is outside the rational Lean formalization. |
| `LGGRVI-C05` | `[PROVED] theorem` | `LEAN_FULL` | The centered two-query derivative of one-half the squared observation equals the Gram pairing for every nonzero rational step. | Theorem 4 | `lean4/Core.lean::centered_directional_identity`; `test_exact_rational_identities_call_shipped_checkers` | Exact rational identity. The float step `1e-5` check is numerical only. |
| `LGGRVI-C06` | `[PROVED] theorem` | `LEAN_FULL` | Averaging the centered sign probe over the full cube recovers each coordinate of `Hx`. | Theorem 5 | `lean4/Core.lean::sign_cube_recovers`; `test_exact_rational_identities_call_shipped_checkers` | Full finite sign cube. A random subsample is not this theorem. |
| `LGGRVI-C07` | `[COMPUTED] computation` | `PYTHON` | The reference hidden vector is accepted, becomes visible after one watcher-coefficient mutation, and is hidden again after restoration. | §5 | `test_mutation_breaks_and_restoration_recovers_kernel_claim` | One declared finite fixture; not a general mutation-detection rate. |

No claim in this ledger depends on a live language-model response, a cached
provider receipt, a distributed protocol, a Byzantine bound, a transformer
model, or a topological construction.
