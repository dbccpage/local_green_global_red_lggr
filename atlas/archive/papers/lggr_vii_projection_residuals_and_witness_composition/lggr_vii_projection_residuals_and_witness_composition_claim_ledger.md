# Claim Ledger — LGGR Volume VII (`lggr_vii_projection_residuals_and_witness_composition`)

**AuthorityEffect:** `None`  
**Date:** 2026-10-23  
**Lean 4 Toolchain:** `leanprover/lean4:v4.35.0`

| Claim ID | Section | Claim Summary | Claim Type | Lean 4 Binding (`lean4/LggrVII.lean`) | Python Binding (`code/tests/test_lggr_vii_core.py`) | Status |
|---|---|---|---|---|---|---|
| `C-01` | §2 | Report collision $(x, y)$ with $p(x)=p(y)$ and $q(x)\ne q(y)$ refutes any decoder $D \circ p = q$. | `LEAN4_PROOF` | `LggrVII.collision_blocks_factorization` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-02` | §2 | Deterministic postprocessing $f : A \to A'$ preserves report collisions. | `LEAN4_PROOF` | `LggrVII.postprocessing_preserves_collision` | `test_observer_minimax_and_evidence_preserving_predictor` | Verified |
| `C-03` | §2 | Any report-only evaluator $E : A \to B$ disagrees with $q$ on at least one member of a colliding pair. | `LEAN4_PROOF` | `LggrVII.verdict_ceiling_on_collision` | `test_observer_minimax_and_evidence_preserving_predictor` | Verified |
| `C-04` | §2 | Boolean evaluator defect $\Delta_E = E_g - E_1 E_2$ lies in $\{-1, 0, 1\}$ and equals $-1$ iff $(E_1, E_2, E_g) = (1, 1, 0)$. | `LEAN4_PROOF` | `LggrVII.evalDefect_partition` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-05` | §3 | Two-step and three-step signed state increments telescope to $x_n - x_0$. | `LEAN4_PROOF` | `LggrVII.two_step_telescope`, `LggrVII.three_step_telescope` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-06` | §3 | Local step bounds ($|\Delta x_i| \le 1$) do not imply cumulative endpoint bound ($|x_2 - x_0| \le 1$) on $(0, 1, 2)$. | `LEAN4_PROOF` | `LggrVII.local_steps_do_not_imply_endpoint_bound` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-07` | §3 | `EveryPrefixBounded3` implies `EndpointBounded`, and the excursion history $(0, 1, 2, 1)$ separates the converse. | `LEAN4_PROOF` | `LggrVII.every_prefix_strictly_stronger_than_endpoint` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-08` | §3 | Good history $(0, 1, 0)$ and bad history $(0, 1, 2)$ collide under unsigned step-magnitude reports $(1, 1)$. | `LEAN4_PROOF` | `LggrVII.unsigned_report_collision_good_vs_bad` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-09` | §4 | Dual annihilator $z = (1, 1, -1)$ and primal potential $(0, 1, 2)$ certify $\min_{x \in \mathbb{Z}^3} \|(1,1,1) - D_0 x\|_1 = 1$. | `LEAN4_PROOF` | `LggrVII.triangle_l1_primal_dual_optimality` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-10` | §4 | $D_1 D_0 = 0$; $D_1(1, 1, 1) = 1 \ne 0$ (closure failure on filled triangle); budget vector $(1, 1, 2) = D_0(0, 1, 2)$ is exact. | `LEAN4_PROOF` | `LggrVII.filled_triangle_closure_vs_budget_exactness` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-11` | §4 | Left-inverse chain retraction ($G_1 D_T = D_S G_0$, $G_1 F_1 = I$) pulls back repairs and reflects source nonrepairability. | `LEAN4_PROOF` | `LggrVII.retraction_reflects_repair_and_obstruction` | `test_bridge_to_root_lggr_modules` | Verified |
| `C-12` | §5.1 | On a two-point fiber with target values $a \le b$, any prediction $z$ incurs $2\max(|a-z|, |b-z|) \ge b - a$, attained at midpoint $m$. | `LEAN4_PROOF` | `LggrVII.observer_fiber_two_point_minimax` | `test_observer_minimax_and_evidence_preserving_predictor` | Verified |
| `C-13` | §5.2 | Scaled $m$-context packing identity $U - R = S - (mN - N)$ and constructive bound $CF(p) \le (m - 1) N(q)$. | `LEAN4_PROOF` + `CODE_DEMO_PYTHON` | `LggrVII.contextual_fraction_packing_mass_identity` | `test_constructive_m_context_packing_bound` | Verified |
| `C-14` | §5.2 | Three-party no-signalling table $p_*$ satisfies $CF(p_*) = 19/64 > 2N_{\min}(p_*) = 25/128$ and reverses order against $Q_{5/8}$. | `LEAN4_PROOF` + `CODE_DEMO_PYTHON` | `LggrVII.ghz_rnd2_cf_gt_two_neg_mass_and_order_reversal` | `test_pstar_no_signalling_and_cf_gt_2n_separation` | Verified |
