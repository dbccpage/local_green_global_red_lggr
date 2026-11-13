# Proposal: a rounding witness from angle-word presentations

**AuthorityEffect:** None
**Status:** proposal, 2026-11-13. Nothing here is admitted into LGGR, and no claim status changes.
**Data:** none. No contest data, fitted factorization or derived tensor is stored here. The table in §4 repeats published scores only.

## 1. Question

LGGR already has the linear case. `papers/003_representation_abundance_is_not_physical_authority/lean4/Representation.lean` gives `cycle_defect_bound` (a signed sum of edge defects is at most the sum of tolerances) and `sharp_cycle_attains` (equality for the sign-aligned list), recorded as C6 in that paper's claim ledger.

This proposal adds a non-linear witness in which every coordinate is locally green and the aggregate score is globally red, and asks how the local errors combine when the per-coordinate directions are orthogonal vectors instead of collinear scalars.

## 2. Setting

- A unit vector u in R^n is built from n−1 angles by a fixed tree of Givens rotations. Step k splits parent p_k into child c_k.
- Each angle is an integer word on a grid, θ/π = word / 2^(b−1). Grid step π/2^(b−1); nearest rounding error |ε_k| ≤ τ = π/2^b.
- Local test: each word is within half a step (green by construction).
- Global test: a Frobenius-type score of the rebuilt object against a target, gated at a fixed threshold.

## 3. Proved on paper, checked exactly here

Let J_k = ∂u/∂θ_k and a_k = v_{k−1}[p_k], the parent's mass just before step k. Under the freshness rule (c_k carries no mass when split off):

1. ⟨J_j, J_k⟩ = 0 for j ≠ k.
2. |J_k|² = a_k².
3. ⟨J_k, u⟩ = 0.

Sketch: G_k′ v_{k−1} = a_k(−sin θ_k e_p + cos θ_k e_c) has norm |a_k| and is orthogonal to v_k. Later rotations are isometries, so inner products are fixed at level k. For j < k, the propagated J_j has no c_k component (c_k is untouched before step k), and G_kᵀ J_k at level k is a multiple of e_{c_k}. Hence claim 1. A non-fresh child breaks the last step.

**Fixture:** `tests/test_rounding_witness_tree_jacobian.py`. Standard library only, `Fraction` throughout, rational half-angle parametrization so u and every J_k are exact. 300 seeded random admissible trees with n ≤ 9. Asserts |u| = 1, claims 1 to 3, the linearized quadrature identity |Σ ε_k J_k|² = Σ a_k² ε_k², the equality case, and a negative control (re-splitting into a child that already carries mass breaks claim 1; one fixed witness plus 50 random ones). Reimplemented from the stated claims; it is not a copy of the source script.

## 4. OPEN target: quadrature sharpness corollary

**Lean status:** not written. **Status:** candidate, not a theorem of LGGR.

**Statement (first order only).** For one vector,

    |u(θ+ε) − u(θ)|² = Σ_k a_k² ε_k² + O(|ε|³),

so to first order the defect is at most √(Σ a_k² τ_k²) ≤ Σ |a_k| τ_k. The second inequality is exact, and equality holds iff at most one a_k τ_k is nonzero. With k equal weighted errors, the ratio is √k.

**Relation to C6.** C6 is sharp because its sharp witness makes every signed edge term point the same way (collinear). Here the J_k are pairwise orthogonal, so the same triangle-inequality bound is loose by √k at first order. Collinear means the linear bound is attained. Orthogonal means it is loose. The corollary is the orthogonal analogue of C6, not a restriction of it: C6's own bound is still attained with many nonzero terms.

**Review caveats, to settle before any Lean work:**

- *Not a finite-ε bound.* The a_k are taken at the base point θ. In a float probe (20,000 seeded random trees, n ≤ 9, |ε_k| ≤ 0.3), the exact chord exceeded √(Σ a_k² ε_k²) by up to 11%. A Lean statement must either be about the linearization or carry an explicit remainder. At 12-bit words (τ ≈ 7.7×10⁻⁴) the excess is O(τ) relative and negligible in practice, but it is not zero.
- *A finite-ε linear bound does hold.* Telescoping one angle at a time, each rotation moves the vector by at most |ε_k| times the current mass, which is at most 1, so |Δu| ≤ Σ τ_k exactly. This is the honest analogue of `cycle_defect_bound` and is a better first Lean target than the quadrature form.
- *One vector only.* The corollary says nothing about the aggregate score in §5, which couples many vectors through weights and a nonzero fit residual (see §5).

## 5. Worked example: projection after optimization

**Pattern.** A move that is green in one presentation (continuous angles) becomes red after the forced projection to the admitted presentation (the integer word grid). Each coordinate's snap is within half a step. The aggregate is not.

Source: the Google VQCC dfthcsos verifier formula, run by the proposer. Rows marked † are measured on the public sample submission with pinned hashes. Other rows are measured on Syed Asad Ali's public Apache-2.0 entry (H200 runs, 2026-11-13). Scores are float64 from the verifier's own functions, not exact arithmetic. Gate: error_2 ≤ 20 mHa.

| Case | Each word | error_2 | Verdict |
|---|---|---|---|
| Fit before rounding (sample) † | none | 16.133 mHa | green |
| Nearest rounding, 12-bit words † | ≤ ½ step | 18.640 mHa | green |
| Nearest rounding, 11-bit words † | ≤ ½ step | 25.035 mHa | **red** |
| Nearest rounding, 10-bit words † | ≤ ½ step | 40.015 mHa | **red** |
| 8-bit entry rounded to 7 bits | ≤ ½ step | 425.1 mHa (error_1 2137) | **red** |
| Free-float refit of that entry | none | 15.12 mHa | green |
| That refit snapped back to the 8-bit grid | ≤ ½ step | 145.30 mHa | **red** |

The last two rows are the witness: better in the continuous presentation (20.0 to 15.1 mHa), about 7× worse once projected back.

**Why the aggregate is red even though one vector's errors add in quadrature.** error_2 couples 1,220 vectors through their weights and a nonzero fit residual r. Its expansion has a linear term 2⟨r, dH·ε⟩ and cross terms between words, and the orthogonality claims remove none of them. Letting each word pick its other neighbour (joint lifts) moved 11-bit error_2 only from 19.14 to 18.85 mHa. That expansion is open.

**Local tightness (measured, scoped).** At the 8-bit point, no single ±1 move among the 8,000 words with the largest gradient improved the objective under the error gate. Single moves lowered error_1 (19.61 to 18.75 mHa) but error_2 stayed at 20.0 mHa. This is a finite check on that ranked neighbourhood only.

## 6. Limits

- No physical claim. This is a finite rounding map and a score.
- The table is float64 and comes from the proposer's runs; this repository does not reproduce it.
- Contest data and derived factorizations stay out of this repository. Only the data-free fixture and published numbers are here.
