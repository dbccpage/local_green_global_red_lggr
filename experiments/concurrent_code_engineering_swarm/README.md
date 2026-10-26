# Concurrent Multi-Agent Code-Engineering Swarm (`experiments/concurrent_code_engineering_swarm`)

This package implements a real multi-agent software engineering swarm where three concurrent LLM agents (`openai/gpt-4o-mini`, `anthropic/claude-haiku-4.5`, and `deepseek/deepseek-chat`) independently inspect, test, and patch coupled Python modules in a 3-stage financial settlement codebase:

- `worker-0` (`pricing.py`): `compute_quote(items, discount_bps)`
- `worker-1` (`tax_engine.py`): `apply_tax(quote, tax_bps)`
- `worker-2` (`settlement_router.py`): `route_settlement(taxed_quote, fee_bps)`

## Why Real "Local Green, Global Red" (`LGGR`) Occurs in Parallel Code Swarms

Each worker executes its own module's isolated unit test suite (`run_local_tests`):
- `pricing.py`'s local unit test verifies subtotal and discount arithmetic and accepts either `'net_cents'` or `'net_amount_cents'`.
- `tax_engine.py`'s local unit test uses a permissive mock dictionary containing both `'net_cents'` and `'net_amount_cents'`.
- `settlement_router.py`'s local unit test checks the zero-fee baseline (`fee_bps = 0`), which passes even when platform fees are computed on `gross_cents` instead of `net_cents`.

Consequently, all three modules pass 100% of their isolated local unit tests (`local_green = 1`), yet fail end-to-end pipeline integration (`global_green = 0`, $\Delta_E = -1$) due to:
1. **Cross-module schema key mismatch (`KeyError: 'net_amount_cents'`)** between `pricing.py` and `tax_engine.py`,
2. **Cross-module fee-base conservation drift** in `settlement_router.py`, or
3. **Infeasible specification contradiction** when an immutable upstream contract (`MAX_INVOICE_LINE_ITEMS = 3`) conflicts with a downstream compliance requirement (`MIN_AUDIT_LINE_ITEMS = 5`).

## Host Cryptographic Receipts vs. Compact Role-Scoped Agent Directives

To avoid the token bloat and bilateral wave oscillation observed when raw cryptographic JSON receipts are dumped into agent prompts:
- **Host Audit Log (`events.jsonl`):** Records the full signed `StreamingCodebaseInterfaceMergeMonitor` receipt (`lggr.online_codebase_interface_merge.v1`), including `receipt_sha256`, `StreamingFiberMonitor` collision receipts, AST signature/key reports, and exact conservation residuals.
- **Agent Prompts (Arm C — `compact_lggr_role_directive`):** Receives only a compact, symmetry-broken, role-scoped directive per worker:
  - `worker-0` (`pricing`, priority rank 0): `HOLD_CANONICAL_INTERFACE` (prevents `worker-0` from flipping `'net_cents'` to `'net_amount_cents'` at the same time `worker-1` flips `'net_amount_cents'` to `'net_cents'`).
  - `worker-1` (`tax_engine`, priority rank 1): `ALIGN_TO_UPSTREAM_PRICING_SCHEMA` (`read_from_quote: ['net_cents']`).
  - `worker-2` (`settlement_router`, priority rank 2): `ALIGN_SCHEMA_AND_CONSERVATION_INVARIANT` (`platform_fee_cents = (taxed_quote['net_cents'] * fee_bps) // 10000`).

## Live Empirical Campaign (`evidence/pilot_run/summary.json`)

Executed across 3 concurrent LLM worker models (`openai/gpt-4o-mini`, `anthropic/claude-haiku-4.5`, `deepseek/deepseek-chat`, `max_inflight_requests = 3`, `50` live API attempts, `$0.052721` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `6100` | `infeasible_contract` | **A** | `generic_ci_red` | `safe_escalated` | 1 | 6 | `$0.005037` |
| `6100` | `infeasible_contract` | **B** | `sequential_pipeline_traceback` | `safe_escalated` | 1 | 7 | `$0.005853` |
| `6100` | `infeasible_contract` | **C** | `compact_lggr_role_directive` | `safe_escalated` | 1 | 6 | `$0.005062` |
| `6101` | `clean_control` | **A / B / C** | All policies | `completed` | 0 | 0 | `$0.000000` |
| `6102` | `schema_and_fee_drift` | **A** | `generic_ci_red` | `blocked_unresolved` | 2 | 13 | `$0.014489` |
| `6102` | `schema_and_fee_drift` | **B** | `sequential_pipeline_traceback` | `completed` | 2 | 12 | `$0.016545` |
| `6102` | `schema_and_fee_drift` | **C** | `compact_lggr_role_directive` | `completed` | **1** | **6** | **`$0.005736`** |

On `seed 6102` (`schema_and_fee_drift`), Arm A fails (`blocked_unresolved`) because each worker's local unit tests pass and generic CI failure gives no cross-module attribution. Arm B requires **2 waves** (`12` API calls, `$0.016545`) because the Wave 0 sequential pipeline traceback crashes at Stage 2 (`tax_engine.py` `KeyError: 'net_amount_cents'`), **masking** Stage 3's (`settlement_router.py`) 5-cent conservation drift until Wave 1 repairs Stage 2. Arm C resolves both defects in **1 wave** (`6` API calls, `$0.005736` — 50% fewer API calls and 65% lower cost than Arm B) because `StreamingCodebaseInterfaceMergeMonitor` inspects all three modules' AST contracts and conservation laws simultaneously while holding `worker-0` fixed (`HOLD_CANONICAL_INTERFACE`).

## Diamond-Dependency Multi-Module Codebase (`--topology diamond`, `evidence/diamond_pilot_run/summary.json`)

The package also extends the concurrent code-engineering swarm to a 4-module diamond dependency graph ($A \to B$, $A \to C$, $B, C \to D$) across 4 isolated git worktree branches:
- `worker-0` (`wt/branch-a-anchor`, `quote_anchor.py`): `emit_base_quote(items, discount_bps)`
- `worker-1` (`wt/branch-b-tax`, `tax_branch.py`): `compute_tax_branch(base_quote, tax_bps)`
- `worker-2` (`wt/branch-c-fee`, `fee_branch.py`): `compute_fee_branch(base_quote, fee_bps)`
- `worker-3` (`wt/branch-d-aggregator`, `diamond_aggregator.py`): `aggregate_diamond_settlement(tax_leg, fee_leg)`

On `seed 7200` (`incompatible_middle_branch_extensions`), middle-tier workers $B$ (`tax_branch.py` returning `'branch_net_cents'` with `'NET_V1'`) and $C$ (`fee_branch.py` reading `'net_amount_cents'` with `'GROSS_V2'`) concurrently propose incompatible schema extensions while $D$ (`diamond_aggregator.py`) omits tax deduction in payout (`payout = gross - fee`), yet all 4 modules pass 100% of their isolated worktree unit tests (`local_green = 1`, `global_green = 0`, $\Delta_E = -1$).

Executed across 4 concurrent LLM worker models (`max_inflight_requests = 4`, `63` live API attempts, `$0.053210` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | Pullback Glued | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| `7200` | `incompatible_middle_branch_extensions` | **A** | `generic_ci_red` | `blocked_unresolved` | `false` | 2 | 16 | `$0.013453` |
| `7200` | `incompatible_middle_branch_extensions` | **B** | `sequential_branch_traceback` | `blocked_unresolved` | `false` | 2 | 15 | `$0.014608` |
| `7200` | `incompatible_middle_branch_extensions` | **C** | `pullback_mediated_lggr_directive` | **`completed`** | **`true` ($\lvert f^{-1}\rvert=1$)** | **1** | **8** | **`$0.006600`** |
| `7201` | `infeasible_diamond_contract` | **A** | `generic_ci_red` | `safe_escalated` | `false` | 1 | 8 | `$0.005835` |
| `7201` | `infeasible_diamond_contract` | **B** | `sequential_branch_traceback` | `safe_escalated` | `false` | 1 | 8 | `$0.006376` |
| `7201` | `infeasible_diamond_contract` | **C** | `pullback_mediated_lggr_directive` | `safe_escalated` | `false` | 1 | 8 | `$0.006339` |
| `7202` | `clean_diamond_control` | **A / B / C** | All policies | `completed` | `true` ($\lvert f^{-1}\rvert=1$) | 0 | 0 | `$0.000000` |

On `seed 7200`, Arm B (`sequential_branch_traceback`) fails to converge within 2 waves (`blocked_unresolved`, `15` API calls, `$0.014608`) because Wave 0 sequential execution halts at Branch $B$'s missing `'net_cents'` key (`B -> D`), masking Branch $C$'s upstream `KeyError: 'net_amount_cents'` until Wave 1 and masking Branch $D$'s payout conservation drift across both waves. By contrast, Arm C (`pullback_mediated_lggr_directive`) evaluates all 4 worktree branches over canonical mediated fibers in parallel via `StreamingDiamondCodebasePullbackMonitor` (`StreamingPullbackSquareMonitor` + `StreamingPullbackMediatorFactorizationMonitor` + `StreamingCodebaseInterfaceMergeMonitor`), synthesizing the unique cone mediator $u(w_{\mathrm{diamond}}) = (\text{b\_net\_v1\_900}, \text{c\_net\_v1\_900})$ over singleton interface fiber `'NET_V1:net_cents:900'` in **1 wave** (`8` API calls, `$0.006600`).

## Multi-Round Iterative Feature-Evolution & Catalyst Technical-Debt Rejuvenation (`--topology catalyst`, `evidence/catalyst_pilot_run/summary.json`)

The package also models multi-round iterative feature evolution (`--topology catalyst`) across sequential feature tickets ($t = 1, 2, 3$) on the 3-module settlement codebase (`pricing.py`, `tax_engine.py`, `settlement_router.py`), audited by `StreamingCodebaseCatalystEvolutionMonitor` (`StreamingCatalystDegradationMonitor` + `StreamingCatalystRejuvenationScheduleMonitor` + `StreamingCodebaseInterfaceMergeMonitor` + `StreamingFiberMonitor`):
- Each module's technical-debt catalyst state is measured directly from its Python AST (`dead_helper_functions` not reachable from the canonical entrypoint via AST call edges) plus its runtime return dictionary (`deprecated_alias_keys` outside the canonical interface schema).
- Across Tickets $t = 1, 2, 3$ (`seed 8301`, `multi_ticket_catalyst_debt_breach`), each ticket's quick-fix shim adds $\delta C_t = 2 \le \tau_{\mathrm{step}} = 2$ debt (`_legacy_discount_shim` + `'legacy_subtotal_cents'` in `pricing.py`; `_deprecated_tax_hook` + `'deprecated_gross_v0'` in `tax_engine.py`; `_compat_fee_fallback` + `'shim_payout_cents'` in `settlement_router.py`) while passing 100% of local unit tests and functional E2E settlement conservation (`local_green = 1`), yet cumulative workspace debt reaches $C_3 = 6 > \tau_{\mathrm{cat}} = 4$ (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `51` live API attempts, `$0.062291` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | Final Debt $C_3$ | Max Debt $\max_t C_t$ | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `8300` | `clean_catalyst_control` | **A / B / C** | All policies | `completed` | `0` | `0` | 0 | 0 | `$0.000000` |
| `8301` | `multi_ticket_catalyst_debt_breach` | **A** | `functional_and_step_delta_gate` | `blocked_unresolved` | `6` | `6` | 2 | 13 | `$0.016318` |
| `8301` | `multi_ticket_catalyst_debt_breach` | **B** | `late_last_ticket_module_cleanup` | `blocked_unresolved` | `4` | `6` | 2 | 13 | `$0.016381` |
| `8301` | `multi_ticket_catalyst_debt_breach` | **C** | `scheduled_lggr_catalyst_rejuvenation_directive` | **`completed`** | **`0`** | **`4`** | **1** | **6** | **`$0.006219`** |
| `8302` | `infeasible_catalyst_budget_lock` | **A** | `functional_and_step_delta_gate` | `safe_escalated` | `3` | `4` | 1 | 7 | `$0.008905` |
| `8302` | `infeasible_catalyst_budget_lock` | **B** | `late_last_ticket_module_cleanup` | `safe_escalated` | `3` | `6` | 1 | 6 | `$0.007136` |
| `8302` | `infeasible_catalyst_budget_lock` | **C** | `scheduled_lggr_catalyst_rejuvenation_directive` | `safe_escalated` | `3` | `4` | 1 | 6 | `$0.007332` |

## Stateful Transaction/Session Codebase & DFA Reset-Token Gluing (`--topology dfa`, `evidence/dfa_pilot_run/summary.json`)

The package also models stateful transaction/session modules (`--topology dfa`) sharing a 4-state lock/commit/release `TransactionSession` DFA ($\mathcal{A} = (Q, \Sigma, \delta, q_0, F)$ with $Q = \{\text{'q0\_idle'}, \text{'q1\_lock'}, \text{'q2\_done'}, \text{'q3\_err'}\}$, $q_0 = \text{'q0\_idle'}$, $F = \{\text{'q0\_idle'}, \text{'q2\_done'}\}$) across `pricing_tx.py`, `tax_tx.py`, and `settlement_tx.py`, audited by `StreamingStatefulCodebaseDFAMonitor` (`StreamingDFAGrammarGluingMonitor` + `StreamingDFAResetTokenGluingMonitor` + `StreamingCodebaseInterfaceMergeMonitor` + `StreamingFiberMonitor`):
- In isolated local unit tests (`run_dfa_local_unit_tests`), each module is invoked on a fresh `TransactionSession` initialized at `'q0_idle'`. A module that executes `session.acquire()` followed by `session.commit()` without `session.release()` emits $w_i = [\text{'acquire'}, \text{'commit'}]$, which reaches `'q2_done' \in F$ and passes its isolated unit test (`local_green = 1`), yet `'q2_done' \ne \text{'q0\_idle'}$ is not reset-idempotent on $q_0$.
- When composed sequentially on a shared session ($w_1 ++ w_2 ++ w_3$), `pricing_tx` leaves `session.state = 'q2_done'`, causing `tax_tx`'s `session.acquire()` to transition into trap state `'q3_err' \notin F$ (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `52` live API attempts, `$0.058084` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | Non-Reset Modules | Terminal State | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `9400` | `infeasible_dfa_hold_lock` | **A / B / C** | All policies | `safe_escalated` | `3` | `'q3_err'` | 1 | 6–7 | `$0.0057–$0.0065` |
| `9401` | `clean_dfa_reset_control` | **A / B / C** | All policies | `completed` | `0` | `'q0_idle'` | 0 | 0 | `$0.000000` |
| `9402` | `unreleased_session_lock_trap` | **A** | `isolated_fixture_acceptance_gate` | `blocked_unresolved` | `3` | `'q3_err'` | 2 | 13 | `$0.014272` |
| `9402` | `unreleased_session_lock_trap` | **B** | `exception_site_traceback_routing` | `blocked_unresolved` | `1` | `'q3_err'` | 2 | 14 | `$0.019483` |
| `9402` | `unreleased_session_lock_trap` | **C** | `explicit_lggr_dfa_reset_gluing_directive` | **`completed`** | **`0`** | **`'q0_idle'`** | **1** | **6** | **`$0.006128`** |

## Asynchronous Event-Driven Codebase & Replay-Order Barrier Gluing (`--topology replay`, `evidence/replay_pilot_run/summary.json`)

The package also models asynchronous event-driven escrow modules (`--topology replay`) sharing an `AsyncEscrowBus(prefix_budget=900)` across `pricing_events.py`, `tax_events.py`, and `settlement_events.py`, audited by `StreamingCodebaseReplayOrderMonitor` (`StreamingReplayOrderMonitor` + `StreamingReplayOrderEnvelopeMonitor` + `StreamingCodebaseInterfaceMergeMonitor` + `StreamingFiberMonitor`):
- In isolated local unit tests (`run_replay_local_unit_tests`), each module is invoked on a fresh `AsyncEscrowBus(prefix_budget=900)`. Whether `pricing_events` reserves unnetted `+900` or pre-netted `+720`, `tax_events` reserves `+180`, and `settlement_events` releases `-900` or `-720`, each module's isolated prefix peak is $\le 900$ (`local_green = 1`) and the commutative terminal escrow sum across all 3 modules is identically `180` cents (`tax_reserve_cents = 180`).
- On `seed 9501` (`arrival_masked_replay_breach`), `settlement_events` publishes `-900` with `priority_arrival=True` and no causal barrier (`[-900, +900, +180]`), keeping `arrival_max_prefix_cents = 180 <= 900`, yet causal order `[+900, +180, -900]` reaches `causal_max_prefix_cents = 1080 > 900` (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `50` live API attempts, `$0.055804` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | Arrival Max | Causal Max | Worst Perm Max | Missing Barriers | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `9500` | `clean_replay_barrier_control` | **A / B / C** | All policies | `completed` | `900` | `900` | `900` | `0` | 0 | 0 | `$0.000000` |
| `9501` | `arrival_masked_replay_breach` | **A** | `endpoint_and_arrival_prefix_gate` | `blocked_unresolved` | `180` | `1080` | `1080` | `3` | 2 | 13 | `$0.015276` |
| `9501` | `arrival_masked_replay_breach` | **B** | `causal_interleaving_without_positive_mass_netting` | `blocked_unresolved` | `900` | `900` | `1080` | `3` | 2 | 13 | `$0.015375` |
| `9501` | `arrival_masked_replay_breach` | **C** | `explicit_lggr_replay_order_barrier_directive` | **`completed`** | **`900`** | **`900`** | **`900`** | **`0`** | **1** | **6** | **`$0.006533`** |
| `9502` | `infeasible_escrow_prefix_budget_contradiction` | **A / B / C** | All policies | `safe_escalated` | `180` | `1080` | `1080` | `3` | 1 | 6 | `$0.0059–$0.0066` |

## Synergistic Fault Masking & Coalitional Shapley Attribution (`--topology coalitional`, `evidence/coalitional_pilot_run/summary.json`)

The package also models synergistic fault masking across coupled codebase modules (`--topology coalitional`) over `pricing_coalition.py`, `tax_coalition.py`, and `settlement_coalition.py`, audited by `StreamingCodebaseCoalitionalMonitor` (`StreamingCoalitionalAttributionMonitor` + `StreamingCoalitionalSynergyMaskingMonitor` + `StreamingCodebaseInterfaceMergeMonitor` + `StreamingFiberMonitor`):
- Across all $2^3 = 8$ module ablation coalitions $C \subseteq \{\text{pricing\_coalition}, \text{tax\_coalition}, \text{settlement\_coalition}\}$ (where modules outside $C$ are substituted by their canonical baseline implementations), `seed 9600` (`synergistic_leave_one_out_masked_shims`) harbors redundant fallback shims in both `pricing_coalition.py` (`'fee_basis_cents': subtotal = 1000`) and `settlement_coalition.py` (`basis = max(int(taxed_quote.get('fee_basis_cents', net)), 1000)`).
- Every module passes its isolated local unit test (`local_green = 1`), and reverting any single module in isolation (leave-one-out ablation from the grand coalition $N$) leaves the integration defect unchanged ($\Delta_{-P} = \Delta_{-T} = \Delta_{-S} = 0$), blinding single-module bisection (`Arm A`). Exact rational Shapley attribution computes $2\phi = (-1, 0, -1)$, exonerates dummy player `tax_coalition` ($\phi_T = 0$), and attributes the joint fault to `{pricing_coalition, settlement_coalition}` (`Arm C`).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `50` live API attempts, `$0.053976` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | LOO Marginals $(\Delta_{-P}, \Delta_{-T}, \Delta_{-S})$ | Scaled Shapley $2\phi$ | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `9600` | `synergistic_leave_one_out_masked_shims` | **A** | `leave_one_out_ablation_bisection` | `blocked_unresolved` | `(0, 0, 0)` | `(-1, 0, -1)` | 2 | 13 | `$0.014564` |
| `9600` | `synergistic_leave_one_out_masked_shims` | **B** | `downstream_assertion_site_blame` | `blocked_unresolved` | `(-1, 0, 0)` | `(-2, 0, 0)` | 2 | 13 | `$0.015253` |
| `9600` | `synergistic_leave_one_out_masked_shims` | **C** | `explicit_lggr_coalitional_shapley_directive` | **`completed`** | **`(0, 0, 0)`** | **`(0, 0, 0)`** | **1** | **6** | **`$0.006230`** |
| `9601` | `infeasible_coalitional_fee_floor_lock` | **A / B / C** | All policies | `safe_escalated` | `(0, 0, 0)` | `(-1, 0, -1)` | 1 | 6 | `$0.0058–$0.0062` |
| `9602` | `clean_coalitional_control` | **A / B / C** | All policies | `completed` | `(0, 0, 0)` | `(0, 0, 0)` | 0 | 0 | `$0.000000` |

## Mayer-Vietoris Disconnected Overlap Coboundary Reconciliation (`--topology mayer_vietoris`, `evidence/mayer_vietoris_pilot_run/summary.json`)

The package also models Mayer-Vietoris disconnected overlap coboundary reconciliation (`--topology mayer_vietoris`) across `pricing_mv.py`, `tax_mv.py`, and `settlement_mv.py` partitioned into two overlapping subswarm covers $U = \{w_0 \to u \to w_1\}$ and $V = \{w_0 \to v \to w_1\}$ with disconnected interface overlap $U \cap V = \{w_0, w_1\}$ ($w_0 = \text{'usd\_anchor'}$ at `0`, $w_1 = \text{'eur\_clearing'}$ at target `1080`), audited by `StreamingCodebaseMayerVietorisMonitor` (`StreamingMayerVietorisMonitor` + `StreamingMayerVietorisReconciliationMonitor` + `StreamingCodebaseInterfaceMergeMonitor` + `StreamingFiberMonitor`):
- Both subswarms $U$ and $V$ are open tree paths with zero internal cycles (`u_locally_exact = True`, `v_locally_exact = True`, `local_green = 1`).
- On `seed 9702` (`disconnected_overlap_coboundary_jump`), `tax_mv` on $U$ sets `'eur_clearing_delta_cents': 210` ($f_U(w_1) = 1110$) and `settlement_mv` on $V$ sets `'clearing_offset_cents': 150` ($f_V(w_1) = 1050$), producing connecting coboundary spread $\Delta_{\mathrm{MV}} = |f_U(w_1) - f_V(w_1)| = 60 > 0$ (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `50` live API attempts, `$0.059762` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | $f_U(w_1)$ | $f_V(w_1)$ | Spread $\Delta_{\mathrm{MV}}$ | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `9700` | `infeasible_mayer_vietoris_clearing_lock` | **A / B / C** | All policies | `safe_escalated` | `1110` | `1050` | `60` | 1 | 6 | `$0.0065–$0.0075` |
| `9701` | `clean_mayer_vietoris_control` | **A / B / C** | All policies | `completed` | `1080` | `1080` | `0` | 0 | 0 | `$0.000000` |
| `9702` | `disconnected_overlap_coboundary_jump` | **A** | `isolated_subswarm_exactness_gate` | `blocked_unresolved` | `1110` | `1050` | `60` | 2 | 13 | `$0.016320` |
| `9702` | `disconnected_overlap_coboundary_jump` | **B** | `one_sided_subswarm_v_adjustment` | `blocked_unresolved` | `1110` | `1080` | `30` | 2 | 13 | `$0.015792` |
| `9702` | `disconnected_overlap_coboundary_jump` | **C** | `explicit_lggr_mayer_vietoris_coboundary_directive` | **`completed`** | **`1080`** | **`1080`** | **`0`** | **1** | **6** | **`$0.006775`** |

## 8. 3-Agent Sliding-Window Horizon Truncation & Periodic Rebalancing Campaign (`--topology windowed_drift`)

In `--topology windowed_drift`, 3 concurrent LLM workers edit `pricing_win.py`, `tax_win.py`, and `settlement_win.py` across a 6-epoch settlement drift stream (2 epochs per module) with sliding-window size $W = 2$, sliding-window budget $B_W = 2$ cents, and global horizon drift ceiling $B_{\mathrm{global}} = 3$ cents:
- On `seed 9801` (`unrebalanced_sliding_window_horizon_breach`), every module initially emits `'epoch_drifts_cents': [1, 1]`, satisfying all isolated unit tests and every length-2 sliding window (`max_window_sum = 2 <= 2`, `local_green = 1`) yet breaching the global horizon ceiling (`max_prefix_drift = 6 > 3`, `global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `48` live API attempts, `$0.053738` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | Max Window | Max Prefix | Terminal Drift | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `9800` | `clean_windowed_drift_control` | **A / B / C** | All policies | `completed` | `1` | `1` | `0` | 0 | 0 | `$0.000000` |
| `9801` | `unrebalanced_sliding_window_horizon_breach` | **A** | `sliding_window_local_gate` | `blocked_unresolved` | `2` | `6` | `6` | 2 | 12 | `$0.014319` |
| `9801` | `unrebalanced_sliding_window_horizon_breach` | **B** | `late_terminal_sweep_only` | `blocked_unresolved` | `2` | `4` | `2` | 2 | 12 | `$0.014475` |
| `9801` | `unrebalanced_sliding_window_horizon_breach` | **C** | `explicit_lggr_windowed_drift_rebalancing_directive` | **`completed`** | **`1`** | **`1`** | **`0`** | **1** | **6** | **`$0.006663`** |
| `9802` | `infeasible_windowed_drift_lock` | **A / B / C** | All policies | `safe_escalated` | `2` | `6` | `6` | 1 | 6 | `$0.0059–$0.0065` |

## 9. 3-Agent Martingale Optional-Stopping Early-Gain Halting vs. Tail-Drawdown Cap Campaign (`--topology optional_stopping`)

In `--topology optional_stopping`, 3 concurrent LLM workers edit `pricing_stop.py`, `tax_stop.py`, and `settlement_stop.py` under a 2-step stopped martingale tree ($X_0 = 0$, $X_u = 100$, $X_d = -100$, $X_{uu} = 200$, $X_{ud} = 0$) with maximum tail-drawdown budget $B_{\mathrm{tail}} = 100$ cents:
- On `seed 9900` (`double_down_recovery_stake_tail_drawdown`), `settlement_stop.py` sets `'x_du_cents': 100, 'x_dd_cents': -300, 'stop_on_step1_down': False`. Every node satisfies local martingale conservation ($X_{du} + X_{dd} = -200 = 2 X_d$), stopped expectation is $\mathbb{E}[X_\tau] = 0 = X_0$ with win probability $3/4$, and all isolated unit tests pass (`local_green = 1`), yet adverse-leaf tail drawdown reaches $300 > B_{\mathrm{tail}} = 100$ cents (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `47` live API attempts, `$0.060785` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | $\mathbb{E}[X_\tau]$ | Tail Drawdown | Stop on $d$ | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `9900` | `double_down_recovery_stake_tail_drawdown` | **A** | `martingale_expectation_and_win_rate_gate` | `blocked_unresolved` | `0` | `300` | `False` | 2 | 11 | `$0.015255` |
| `9900` | `double_down_recovery_stake_tail_drawdown` | **B** | `reduced_break_even_recovery_stake` | `blocked_unresolved` | `0` | `200` | `False` | 2 | 12 | `$0.015931` |
| `9900` | `double_down_recovery_stake_tail_drawdown` | **C** | `explicit_lggr_optional_stopping_drawdown_cap_directive` | **`completed`** | **`0`** | **`100`** | **`True`** | **1** | **6** | **`$0.007450`** |
| `9901` | `infeasible_optional_stopping_lock` | **A / B / C** | All policies | `safe_escalated` | `0` | `300` | `False` | 1 | 6 | `$0.0070–$0.0077` |
| `9902` | `clean_optional_stopping_control` | **A / B / C** | All policies | `completed` | `0` | `100` | `True` | 0 | 0 | `$0.000000` |

## 10. 3-Agent CPTP Channel State-Blindspot vs. Operator-Level Completeness Campaign (`--topology cptp`)

In `--topology cptp`, 3 concurrent LLM workers edit `pricing_channel.py`, `tax_channel.py`, and `settlement_channel.py` acting on a 3-dimensional state space $\{\rho_0, \rho_1, \rho_2\}$ via Kraus operators $K_0 = \mathrm{diag}(k_0, 0, 0)$, $K_1 = \mathrm{diag}(0, k_1, 0)$, $K_2 = \mathrm{diag}(0, 0, k_2)$:
- On `seeds 10000, 10001` (`incomplete_kraus_ground_state_blindspot`), `pricing_channel.py` sets `k0_diag = 1` while `tax_channel.py` sets `k1_diag = 0` and `settlement_channel.py` sets `k2_diag = 0`. Isolated unit tests probe only the ground state $\rho_0 = \mathrm{diag}(1, 0, 0)$, where $\mathrm{tr}(\mathcal{E}(\rho_0)) - \mathrm{tr}(\rho_0) = 0$ (`local_green = 1`), yet the operator trace-preservation residual $R_{\mathrm{TP}}(\mathcal{E}) = \sum_{r=0}^2 K_r^\top K_r - I_3 = \mathrm{diag}(0, -1, -1)$ has L1 norm $\|R_{\mathrm{TP}}\|_1 = 2 > 0$ (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `50` live API attempts, `$0.063678` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | $(k_0, k_1, k_2)$ | $\|R_{\mathrm{TP}}\|_1$ | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `10000` | `incomplete_kraus_ground_state_blindspot` | **A** | `ground_state_probe_trace_gate` | `blocked_unresolved` | `(1, 0, 0)` | `2` | 1 | 6 | `$0.006057` |
| `10000` | `incomplete_kraus_ground_state_blindspot` | **B** | `partial_sector1_kraus_completion` | `blocked_unresolved` | `(1, 1, 0)` | `1` | 1 | 6 | `$0.005855` |
| `10000` | `incomplete_kraus_ground_state_blindspot` | **C** | `explicit_lggr_cptp_operator_completion_directive` | **`completed`** | **`(1, 1, 1)`** | **`0`** | **2** | **13** | **`$0.019931`** |
| `10001` | `incomplete_kraus_ground_state_blindspot` | **A** | `ground_state_probe_trace_gate` | `blocked_unresolved` | `(1, 0, 0)` | `2` | 1 | 6 | `$0.006075` |
| `10001` | `incomplete_kraus_ground_state_blindspot` | **B** | `partial_sector1_kraus_completion` | `blocked_unresolved` | `(1, 1, 0)` | `1` | 1 | 6 | `$0.005855` |
| `10001` | `incomplete_kraus_ground_state_blindspot` | **C** | `explicit_lggr_cptp_operator_completion_directive` | **`completed`** | **`(1, 1, 1)`** | **`0`** | **2** | **13** | **`$0.019904`** |

## 11. 3-Agent Simplicial Mesh Regge Hinge-Deficit Curvature & Gauss-Bonnet Holonomy Campaign (`--topology regge`)

In `--topology regge`, 3 concurrent LLM workers edit `pricing_mesh.py`, `tax_mesh.py`, and `settlement_mesh.py` forming a 3-triangle star $K$ around interior vertex `v_apex` with boundary vertices $\{b_0, b_1, b_2\}$ (where angles are expressed in $1/36$-turn units: $18$ units $= 1/2$ turn per Euclidean triangle, $36$ units $= 1$ full turn around `v_apex`):
- On `seeds 10100, 10101` (`conical_hinge_deficit_star`), `pricing_mesh.py` has flat sector angles `(12, 3, 3)` while `tax_mesh.py` and `settlement_mesh.py` have equilateral sector angles `(6, 6, 6)`. Every module's triangle closes locally ($12+3+3 = 18$, $6+6+6 = 18$, `local_green = 1`), yet the interior hinge deficit at `v_apex` is $\epsilon_{\mathrm{apex}} = 36 - (12 + 6 + 6) = 12$ units ($= 1/3$ turn $\ne 0$) and boundary geodesic turn sum is $24 < 36$ (`global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `42` live API attempts, `$0.049997` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | $\epsilon_{\mathrm{apex}}$ (units) | $\sum \kappa_{\mathrm{bnd}}$ (units) | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `10100` | `conical_hinge_deficit_star` | **A** | `local_triangle_closure_gate` | `blocked_unresolved` | `12` | `24` | 1 | 6 | `$0.005646` |
| `10100` | `conical_hinge_deficit_star` | **B** | `partial_sector1_hinge_flattening` | `blocked_unresolved` | `6` | `30` | 1 | 6 | `$0.006365` |
| `10100` | `conical_hinge_deficit_star` | **C** | `explicit_lggr_regge_holonomy_flattening_directive` | **`completed`** | **`0`** | **`36`** | **1** | **6** | **`$0.007637`** |
| `10101` | `conical_hinge_deficit_star` | **A** | `local_triangle_closure_gate` | `blocked_unresolved` | `12` | `24` | 1 | 6 | `$0.005624` |
| `10101` | `conical_hinge_deficit_star` | **B** | `partial_sector1_hinge_flattening` | `blocked_unresolved` | `6` | `30` | 1 | 6 | `$0.006404` |
| `10101` | `conical_hinge_deficit_star` | **C** | `explicit_lggr_regge_holonomy_flattening_directive` | **`completed`** | **`0`** | **`36`** | **2** | **12** | **`$0.018321`** |

## 12. 3-Agent Bounded-Depth $k$-Induction Unrolling vs. Inductive Invariant Strengthening Campaign (`--topology kinduction`)

In `--topology kinduction`, 3 concurrent LLM workers edit `pricing_ind.py`, `tax_ind.py`, and `settlement_ind.py` over modular unrolling depths $m_k \in \{2, 4, 8, 16\}$ ($k = 1, 2, 3, 4$) and reachable non-negative carrier $X_{\mathrm{reach}} = [0, 10]$:
- On `seeds 10200, 10201` (`repairable_k_induction_escape_seed_*`), `tax_ind.py` sets `tax_const_b = 1, tax_unrolling_thread = [1, 1, 5, 5]` ($3x + 1 \equiv 0 \pmod{m_k}$, no integer root $x_\infty = -1/3 \notin \mathbb{Z}$) and `settlement_ind.py` sets `settle_const_b = 3, settle_unrolling_thread = [1, 3, 7, 15]` ($3x + 3 \equiv 0 \pmod{m_k}$, out-of-carrier integer root $x_\star = -1 \notin [0, 10]$, depth-4 carry overflow $x_4 - x_3 = 15 - 7 = 8 > 0$). Both pass isolated unit tests and bounded-depth $k \le 3$ unrolling (`local_green = 1`), yet fail full carrier completion and settlement conservation (`payout = 865 != 873`, `global_green = 0`, $\Delta_E = -1$).

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `47` live API attempts, `$0.059591` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `tax_root` | `settle_root` | `depth4_overflow` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10200` | `repairable_k_induction_escape_seed_10200` | **A** | `bounded_k3_unrolling_gate` | `blocked_unresolved` | `null` | `-1` | `8` | 1 | 6 | `$0.005697` |
| `10200` | `repairable_k_induction_escape_seed_10200` | **B** | `partial_tax_tower_strengthening` | `blocked_unresolved` | `2` | `-1` | `8` | 1 | 6 | `$0.006056` |
| `10200` | `repairable_k_induction_escape_seed_10200` | **C** | `explicit_lggr_kinduction_carrier_directive` | `blocked_unresolved` | `2` | `-1` | `8` | 2 | 11 | `$0.017702` |
| `10201` | `repairable_k_induction_escape_seed_10201` | **A** | `bounded_k3_unrolling_gate` | `blocked_unresolved` | `null` | `-1` | `8` | 1 | 6 | `$0.005717` |
| `10201` | `repairable_k_induction_escape_seed_10201` | **B** | `partial_tax_tower_strengthening` | `blocked_unresolved` | `2` | `-1` | `8` | 1 | 6 | `$0.006055` |
| `10201` | `repairable_k_induction_escape_seed_10201` | **C** | `explicit_lggr_kinduction_carrier_directive` | **`completed`** | **`2`** | **`2`** | **`0`** | **2** | **12** | **`$0.018364`** |

## 13. 3-Agent Linearized Pipeline Jacobian Stealth Blindspot vs. Full-Rank Observability Campaign (`--topology jacobian`)

In `--topology jacobian`, 3 concurrent LLM workers edit `pricing_jac.py`, `tax_jac.py`, and `settlement_jac.py` with stage state vector $s = (s_1, s_2, s_3)$ and interface handoff defect Jacobian $D(s) = (s_1 - s_2, s_2 - s_3, s_1 - s_3)$ ($\mathrm{rank}(D) = 2$):
- On `seed 10300` (`repairable_jacobian_blindspot_seed_10300`), `tax_jac.py` sets `tax_state_s2 = 0` ($s = (1, 0, 1)$, $\omega = D(s) = (1, -1, 0)$, $\|\omega\|_1 = 2 > 0$) and `settlement_jac.py` sets redundant telemetry row `settle_telemetry_row = [1, 1, 0]` so $Q_{\mathrm{blind}} = \begin{pmatrix} 1 & 1 & 0 \\ 1 & 1 & 0 \end{pmatrix}$ has $Q_{\mathrm{blind}} \omega = (0, 0)^\top$ (`measured_l1_score = 0`), $\mathrm{rank}(Q_{\mathrm{blind}} D) = 1 < 2 = \mathrm{rank}(D)$, $\dim(\mathrm{im}(D) \cap \ker(Q_{\mathrm{blind}})) = 1 > 0$, and `unobserved_blindspot_reserve_cents = 8` (`payout = 865 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 10301` (`infeasible_jacobian_blindspot_lock`), legacy constraints lock `tax_jac.py` and `settlement_jac.py` to their rank-deficient telemetry configuration while requiring $\mathrm{im}(D) \cap \ker(Q) = \{0\}$, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `37` live API attempts, `$0.038575` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `state_vector` | `rank_qd` | `blindspot_dim` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10300` | `repairable_jacobian_blindspot_seed_10300` | **A** | `coarse_endpoint_telemetry_gate` | `blocked_unresolved` | `(1, 0, 1)` | `1` | `1` | 1 | 6 | `$0.005468` |
| `10300` | `repairable_jacobian_blindspot_seed_10300` | **B** | `partial_tax_stage_alignment` | `blocked_unresolved` | `(1, 1, 1)` | `1` | `1` | 1 | 7 | `$0.006524` |
| `10300` | `repairable_jacobian_blindspot_seed_10300` | **C** | `explicit_lggr_jacobian_observability_directive` | **`completed`** | **`(1, 1, 1)`** | **`2`** | **`0`** | **1** | **6** | **`$0.005970`** |
| `10301` | `infeasible_jacobian_blindspot_lock` | **A / B / C** | All policies | `safe_escalated` | `(1, 0, 1)` | `1` | `1` | 1 | 18 | `$0.020613` |

## 14. 3-Agent Boundary-Mixing & Majority Quorum-Masking vs. Exact Fiber Payload Verification Campaign (`--topology quorum`)

In `--topology quorum`, 3 concurrent LLM workers edit `pricing_quorum.py`, `tax_quorum.py`, and `settlement_quorum.py` where each module emits a boolean pass flag, a boundary basis tag, and a binary validator vote $(e_1, e_2, e_3) \in \{0, 1\}^3$:
- On `seed 10402` (`repairable_quorum_masking_seed_10402`), `tax_quorum.py` uses pre-discount `basis_tag = 'subtotal_cents'` (`tax_cents = 200 != 180`, `tax_validator_vote = 0`) while `pricing_quorum.py` and `settlement_quorum.py` vote `1`, so the 2-of-3 majority quorum passes ($M_{2,3}(1, 0, 1) = 1$, `pass_flags = [1, 1, 1]`, `local_green = 1`) while the strict product is $L_{\mathrm{prod}} = 0$ (`quorum_inflation = 1`) and `settlement_quorum.py` operates under `governance_mode = 'quorum_2_of_3'` (`quorum_reserve_cents = 9`, `payout = 864 != 873`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 10400` (`infeasible_quorum_governance_lock`), legacy constraints lock `tax_quorum.py` and `settlement_quorum.py` to their quorum-masked configuration while requiring `strict_product` governance, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `37` live API attempts, `$0.040903` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `tax_basis_tag` | `governance_mode` | `quorum_reserve` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10402` | `repairable_quorum_masking_seed_10402` | **A** | `pass_flag_and_quorum_2_of_3_gate` | `blocked_unresolved` | `subtotal_cents` | `quorum_2_of_3` | `9` | 1 | 7 | `$0.006693` |
| `10402` | `repairable_quorum_masking_seed_10402` | **B** | `partial_tax_basis_alignment` | `blocked_unresolved` | `net_cents` | `quorum_2_of_3` | `9` | 1 | 6 | `$0.006401` |
| `10402` | `repairable_quorum_masking_seed_10402` | **C** | `explicit_lggr_boundary_product_directive` | **`completed`** | **`net_cents`** | **`strict_product`** | **`0`** | **1** | **6** | **`$0.006468`** |
| `10400` | `infeasible_quorum_governance_lock` | **A / B / C** | All policies | `safe_escalated` | `subtotal_cents` | `quorum_2_of_3` | `9` | 1 | 18 | `$0.021341` |

## Offline Verification & Live Execution

```powershell
# Run unit, tamper, and deterministic replay tests (no API calls)
python -m unittest tests.test_concurrent_code_engineering_swarm -v

# Replay archived live 3-agent linear, 4-agent diamond, 3-agent catalyst, 3-agent stateful DFA, 3-agent replay-order, 3-agent coalitional, 3-agent Mayer-Vietoris, 3-agent windowed-drift, 3-agent optional-stopping, 3-agent CPTP channel, 3-agent Regge holonomy, 3-agent k-induction, 3-agent Jacobian, and 3-agent boundary-quorum evidence (no API calls)
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/diamond_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/catalyst_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/dfa_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/replay_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/coalitional_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/mayer_vietoris_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/windowed_drift_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/optional_stopping_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/cptp_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/regge_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/kinduction_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/jacobian_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/quorum_pilot_run/events.jsonl
```
