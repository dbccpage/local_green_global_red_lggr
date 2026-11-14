# Claim Ledger: Operator Lifts Trace Metrics and Representation Limits (Paper 013)

**Package:** `013_operator_lifts_trace_metrics_and_representation_limits`  
**Monograph:** `operator_lifts_trace_metrics_and_representation_limits_monograph.md`  
**Version:** 2.1.1 (2026-10-23)
**Date:** 2026-10-23

| Claim ID | Formal Claim | Status | Analytical Proof / Specification | Numerical Example / Regression Check | Scope Fence & Boundary Conditions |
|---|---|---|---|---|---|
| C01 | For every finite integer list $v$, the integer trace norm equals $\sum_i |v_i|$. | `[PROVED]` | `trace_norm_eq_mass`: the diagonal list's absolute-coordinate sum is the finite trace norm. Proposition 3.1's Banach-space embedding is the classical reading of that identity. | `test_proved_finite_integer_and_rational_claims` calls `integer_trace_norm` and `linear_embedding`; `test_linear_trace_embedding_isometry` checks the floating-point diagonal. | The real operator $T(v)$ and its injectivity as a map of Banach spaces are not constructed in Lean. |
| C02 | For an integer $c \neq 0$, normalized absolute coordinate weights of $c \cdot v$ and $v$ agree. If $|c| > 1$ and the mass is positive, the mass strictly increases. | `[PROVED]` | `weight_scale_cross` and `scale_increases_mass`. Theorem 4.1's real punctured line and Mazur square root remain the monograph's classical reading. | `test_proved_finite_integer_and_rational_claims` calls `normalized_abs_weights` on a vector, its positive scale, and its global sign flip. `test_lossy_collision_principle_positive_and_negative` checks the floating-point density lift. | The real fiber $F_{\mathrm{den}}^{-1}(\rho(v))$ is not a Lean theorem in this deposit. |
| C03 | Reconstruction without an admitted mass returns failure. Negation preserves integer mass and absolute weights. | `[PROVED]` | `mass_neg` and `weight_sign_cross`. The shipped `attempt_reconstruction` returns failure when mass is absent. Theorem 4.3's continuous selection obstruction remains classical. | `test_proved_finite_integer_and_rational_claims` calls `attempt_reconstruction` with no mass and compares antipodal integer weights. The existing reconstruction tests cover the floating-point rank-1 domain. | Mixed-state rejection and the circle argument are not Lean theorems here. |
| C04 | The exact rational fence tests the ratio ceiling before a primary decrease, rejects a primary increase and a secondary increase after the guardrail passes, prefers a feasible candidate to an infeasible one, and prefers the lower primary value. | `[PROVED]` | `guardrail_rejects_before_primary`, `primary_decrease_accepts`, `primary_increase_rejects`, `secondary_increase_rejects`, `feasible_dominates`, and `lower_phi_preferred`. Proposition 2.2's chain-complex bound stays classical. | `test_proved_finite_integer_and_rational_claims` calls `exact_admits` and `exact_compare`. `test_guarded_descent_integration.py` checks finite rankings of the floating-point evaluator. | A general transitivity theorem for every ranking is not the Lean statement. |
| C05 | Mathematical trace embedding carries no physical state or quantum emergence claims. | `[NEGATIVE BOUNDARY]` | Monograph §6: declarative scope and interpretive demarcation. | None (declarative nonclaim) | Epistemic boundary. This row is not a theorem. |
| C06 | For an integer scale $c$ and natural numbers $n, d$, $(|c| n) d = n (|c| d)$. | `[PROVED]` | `ratio_cross`. Proposition 4.2's factorisation through the operator $\rho$ is the classical reading. | `test_proved_finite_integer_and_rational_claims` calls `cleared_homogeneous_pair` and checks the cleared pair and the reduced ratio. | The identity does not construct $\Phi_1$, $\Gamma_2$, or $\rho$. |
| C07 | If two integer vectors have equal sums of squares and equal length, then $\|a-b\|_2^2 \|a+b\|_2^2 = 4(\|a\|_2^2 \|b\|_2^2 - \langle a, b \rangle^2)$. | `[PROVED]` | `trace_gap_identity`. Section 5's square-root distance and its triangle inequality remain the classical reading. | `test_proved_finite_integer_and_rational_claims` calls `squared_trace_gap` on $(1,0),(0,1)$ and on $(3,4),(4,-3)$. The floating-point triangle inequality remains in `test_trace_distance_preserves_triangle_inequality_without_near_identity_clipping`. | The square-root metric is not a Lean theorem in this deposit. |


## Named regression entry points

These executable checks have the finite scopes described above; they do not establish whole-paper truth.

- `code/tests/test_operator_lifts.py::test_linear_trace_embedding_isometry`
- `code/tests/test_operator_lifts.py::test_lossy_collision_principle_positive_and_negative`
