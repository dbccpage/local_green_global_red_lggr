# Lean claim map

| Claim | Declaration | What Lean checks | Boundary |
|---|---|---|---|
| `LGGRVI-C01` | `LGGRVI.postprocessing_invariance` | Function congruence after equal observations. | No matrix or probability structure. |
| `LGGRVI-C02` | `LGGRVI.zero_preserving_accepts_hidden` | Substitution of the zero observation into a declared green verdict. | The postprocessor is deterministic and observation-only. |
| `LGGRVI-C04` (assumed system) | `LGGRVI.gram_zero_iff_hidden` | The declared `GramSystem.gramKernel` field is exposed through `gram`. | This declaration does not derive the matrix identity. |
| `LGGRVI-C04` (assumed system) | `LGGRVI.detectable_has_nonzero_gram` | Contrapositive use of the same declared identity. | No inner-product-space construction is mechanized. |
| `LGGRVI-C04` | `LGGRVI.gram_kernel_iff` | For every finite rational matrix, `Hx = 0` if and only if `Qx = 0`. | Rational entries only. |
| `LGGRVI-C04` | `LGGRVI.gram_detectable_iff` | The Gram response is nonzero exactly when the observation is nonzero. | Same rational matrices. The orthogonal range sentence is not this theorem. |
| `LGGRVI-C05` | `LGGRVI.centered_directional_identity` | The centered energy quotient equals the Gram pairing when the step is nonzero. | Rational step, not a float limit. |
| `LGGRVI-C06` | `LGGRVI.sign_cube_recovers` | The full sign-cube average recovers each coordinate of `Hx`. | The cube is finite and exhaustive. |

`lean4/check_axioms.lean` prints the dependency report for this exact list.
`lean4/AXIOM_REPORT.txt` is the deterministic normalized output of a fresh
short-path build and census, bound to the SHA-256 hashes of `Core.lean` and
`check_axioms.lean`; the verifier recaptures it rather than trusting the stored
text alone. The Euclidean SVD bound and the orthogonal-range statement are
classical real-matrix results outside the rational Lean formalization.
`SHA256SUMS` pins every Lean input and the bundled report.
