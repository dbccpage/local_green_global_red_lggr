# Claim Ledger: Constraint-Level Regulation via Multi-Channel Obstruction Diagnostics (Paper 018)

**Package:** `018_constraint_level_regulation_via_multi_channel_obstruction_diagnostics`  
**Monograph:** `constraint_level_regulation_via_multi_channel_obstruction_diagnostics_monograph.md`  
**Version:** 2.0.2  
**Date:** 2026-10-08  

| Claim ID | Formal Claim | Status | Verification Mechanism | Scope Fence |
|---|---|---|---|---|
| C01 | A rational channel tuple with $\Phi_{\mathrm{geom}} = 0$ and either $\Phi_{\mathrm{curv}} > 0$ or $\Xi > 0$ is rejected. The tuple $(0, 3, 0, 0, 0)$ is accepted. | `[PROVED]` | `zero_geom_rejects_curvature`, `zero_geom_rejects_xi`, and `separated_sat_accepts`. Proposition 2.1's operator-norm bound stays classical. | `test_proved_finite_integer_and_rational_claims` calls `exact_signature_ok`. The chain-complex inequality is not a Lean theorem in this deposit. |
| C02 | For $R_{\max} > 0$, the guard rejects $\Phi_{\mathrm{geom}} = 0 < \Phi_{\mathrm{curv}}$, accepts the collapsed pair $(0, 0)$, and for $\Phi_{\mathrm{geom}} > 0$ accepts exactly when $\Phi_{\mathrm{curv}} \le R_{\max} \Phi_{\mathrm{geom}}$. | `[PROVED]` | `ratio_infinite_rejects`, `collapsed_pair_passes`, `ratio_positive_rejects`, `ratio_positive_admits`, and `deletion_shaped_passes`. | `test_proved_finite_integer_and_rational_claims` calls `exact_ratio_admits` and `exact_select` on a deletion-shaped collapse. The collapsed pair passing is why the ratio does not reject edge deletion. |
| C03 | Descent rejects a geometric increase. A ratio failure still rejects after descent passes. Outside the $\varepsilon$ band the higher score loses. Inside a score tie the lower $\Xi$ wins, and equal score and $\Xi$ follow the earlier name. | `[PROVED]` | `descent_rejects`, `tearing_after_descent`, `outside_eps_loses`, `lower_xi_in_score_tie`, and `name_orders_exact_tie`. | `test_proved_finite_integer_and_rational_claims` calls `exact_select` on an outside-band pair, an inside-band $\Xi$ tie, each weighted channel, and a name tie. Asymptotic convergence is not claimed. |
| C04 | A lift is admitted exactly when the penalty is strictly below $\Delta\Phi_{\mathrm{geom}} + \tfrac{1}{2}\Delta\Phi_{\mathrm{sat}}$. | `[PROVED]` | `lift_rejects` and `lift_accepts`. | `test_proved_finite_integer_and_rational_claims` calls `exact_lift_admitted` and `exact_select` on a failing penalty and a passing penalty. |
| C05 | The empty tag list is `RefusedStalled`. A nonempty list of one refusal tag returns that tag for invalid input, tearing, and descent. A mixed tearing and descent list is `RefusedStalled`. | `[PROVED]` | `empty_is_stalled`, `classify_all_invalid`, `classify_all_tearing`, `classify_all_descent`, and `mixed_stalls`. | `test_proved_finite_integer_and_rational_claims` calls `exact_select` on an empty list, a descent, a tear, an invalid signature, and a mixed pair. |

