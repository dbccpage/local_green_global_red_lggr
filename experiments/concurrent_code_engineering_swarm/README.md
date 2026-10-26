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

## 15. 3-Agent Concurrent Resource Lease Overlap & Split-Brain Fencing-Token Synthesis Campaign (`--topology lease`)

In `--topology lease`, 3 concurrent LLM workers edit `pricing_lease.py`, `tax_lease.py`, and `settlement_lease.py` where each module acquires a half-open lease window $[s_i, e_i)$ satisfying its isolated duration bound ($e_i - s_i \le \tau_{\mathrm{dur}} = 3$, weighted lease slacks $(4, 3, 4) \le \tau_{\mathrm{lease}} = 4$) and presents a fencing token $k_i$:
- On `seed 10500` (`repairable_lease_overlap_seed_10500`), all 3 modules start concurrently at $t = 0$ (`windows = [[0, 1], [0, 3], [0, 3]]`, `tokens = [1, 1, 1]`, `local_green = 1`), producing `max_concurrent_leases = 3`, `peak_concurrent_drift = 11 > 6`, and `split_brain_reserve_cents = 10` (`payout = 863 != 873`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 10502` (`infeasible_lease_overlap_lock`), legacy constraints lock `tax_lease.py` and `settlement_lease.py` to their overlapping windows at $t = 0$ while requiring disjoint fencing-serialized leases, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `38` live API attempts, `$0.034715` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `lease_windows` | `fencing_tokens` | `peak_drift` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10500` | `repairable_lease_overlap_seed_10500` | **A** | `isolated_lease_duration_gate` | `blocked_unresolved` | `[[0,1],[0,3],[0,3]]` | `[1, 1, 1]` | `11` | 1 | 7 | `$0.005599` |
| `10500` | `repairable_lease_overlap_seed_10500` | **B** | `partial_tax_lease_serialization` | `blocked_unresolved` | `[[0,1],[1,2],[1,4]]` | `[1, 2, 2]` | `7` | 1 | 6 | `$0.005256` |
| `10500` | `repairable_lease_overlap_seed_10500` | **C** | `explicit_lggr_fencing_token_directive` | **`completed`** | **`[[0,1],[1,2],[2,3]]`** | **`[1, 2, 3]`** | **`4`** | **1** | **6** | **`$0.005702`** |
| `10502` | `infeasible_lease_overlap_lock` | **A / B / C** | All policies | `safe_escalated` | `[[0,1],[0,3],[0,3]]` | `[1, 1, 1]` | `11` | 1 | 19 | `$0.018159` |

## 16. 3-Agent Cyclic Pairwise Constraint Sheaf Contextuality vs. Global Section Reconciliation Campaign (`--topology contextuality`)

In `--topology contextuality`, 3 concurrent LLM workers edit `pricing_sheaf.py`, `tax_sheaf.py`, and `settlement_sheaf.py` where each module emits a 2-variable empirical context table (`table_ab`, `table_bc`, `table_ca`) satisfying single-variable marginal compatibility ($p_A = p_B = p_C = 1/2$, $M = 4$):
- On `seed 10602` (`repairable_contextual_sheaf_seed_10602`), all 3 modules use anti-correlated pairwise tables `['0', '1/2', '1/2', '0']` (`q_ab_num = 0`, `q_bc_num = 0`, `q_ca_num = 0`, `local_green = 1`), creating a cyclic hollow-triangle sheaf obstruction ($q_{BC} + q_{CA} = 0 \ne 2$, `scaled_gap_m4 = 2 > 0`, $H^1 \ne 0$) and `contextuality_reserve_cents = 11` (`payout = 862 != 873`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 10600` (`infeasible_contextual_sheaf_lock`), legacy constraints lock `tax_sheaf.py` and `settlement_sheaf.py` to their hollow-triangle pairwise tables while requiring a non-negative global joint section $d \ge 0$, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `40` live API attempts, `$0.038555` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `q_bc_num` | `q_ca_num` | `scaled_gap_m4` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10602` | `repairable_contextual_sheaf_seed_10602` | **A** | `pairwise_no_signaling_marginal_gate` | `blocked_unresolved` | `0` | `0` | `2` | 1 | 7 | `$0.005699` |
| `10602` | `repairable_contextual_sheaf_seed_10602` | **B** | `partial_tax_pairwise_reconciliation` | `blocked_unresolved` | `1` | `0` | `1` | 1 | 6 | `$0.005054` |
| `10602` | `repairable_contextual_sheaf_seed_10602` | **C** | `explicit_lggr_global_section_directive` | **`completed`** | **`1`** | **`1`** | **`0`** | **1** | **6** | **`$0.005698`** |
| `10600` | `infeasible_contextual_sheaf_lock` | **A / B / C** | All policies | `safe_escalated` | `0` | `0` | `2` | 1 | 21 | `$0.022104` |

## 17. 3-Agent Watcher-Dropout & Gram Rank-Deficiency vs. Full-Rank Critical Watcher Restoration Campaign (`--topology gram_dropout`)

In `--topology gram_dropout`, 3 concurrent LLM workers edit `pricing_gram.py`, `tax_gram.py`, and `settlement_gram.py` where each module emits a 3-element watcher row (`pricing_watcher_row`, `tax_watcher_row`, `settle_watcher_row`) forming the $3 \times 3$ observation matrix $Q = (q_1, q_2, q_3)$ evaluated along the settlement-critical perturbation $v_{\mathrm{crit}} = (1, -1, 1)$ ($\|v_{\mathrm{crit}}\|_1 = 3 > 0$):
- On `seed 10700` (`repairable_watcher_dropout_seed_10700`), `tax_gram.py` emits collinear row `[2, 2, 0] = 2 * q_1` and `settlement_gram.py` omits critical row `[1, 0, 1]` (`settle_watcher_row = [0, 1, 1]`, `dropout_reserve_cents = 12`, `local_green = 1`), yielding $\mathrm{rank}(Q^\top Q) = 2 < 3$, $\dim \ker(Q^\top Q) = 1 > 0$, $\|Q v_{\mathrm{crit}}\|_2^2 = 0$, and `payout = 861 != 873` (`global_green = 0`, $\Delta_E = -1$).
- On `seed 10701` (`infeasible_watcher_dropout_lock_seed_10701`), legacy constraints lock `tax_gram.py` and `settlement_gram.py` to their rank-deficient watcher rows while requiring $\mathrm{rank}(Q^\top Q) = 3$, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `42` live API attempts, `$0.039763` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `gram_rank` | `nullspace_dim` | `crit_norm_sq` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10700` | `repairable_watcher_dropout_seed_10700` | **A** | `local_nonzero_row_gate_only` | `blocked_unresolved` | `2` | `1` | `0` | 1 | 6 | `$0.006228` |
| `10700` | `repairable_watcher_dropout_seed_10700` | **B** | `partial_tax_watcher_row_update` | `blocked_unresolved` | `2` | `1` | `0` | 1 | 6 | `$0.005993` |
| `10700` | `repairable_watcher_dropout_seed_10700` | **C** | `explicit_lggr_watcher_gram_restoration_directive` | **`completed`** | **`3`** | **`0`** | **`4`** | **1** | **6** | **`$0.006413`** |
| `10701` | `infeasible_watcher_dropout_lock_seed_10701` | **A / B / C** | All policies | `safe_escalated` | `2` | `1` | `0` | 1 | 24 | `$0.021129` |

## 18. 3-Agent Multi-Evaluator Policy Ranking $CF(p)$ vs. $N_{\min}(p)$ Order Reversal Campaign (`--topology policy_reversal`)

In `--topology policy_reversal`, 3 concurrent LLM workers edit `pricing_policy.py`, `tax_policy.py`, and `settlement_policy.py` over $m = 8$ evaluation contexts with common denominator $D = 768$ comparing Policy A (`Q_5_8`: $CF_A = 192, N_{\min,A} = 96$) and Policy B (`p_star`: $CF_B = 228, N_{\min,B} = 75$) under signed violation ceiling $\tau_n = 80$:
- On `seed 10800` (`repairable_policy_reversal_defect`), `tax_policy.py` assumes the false surrogate bound $CF \le 2 N_{\min}$ (`surrogate_two_bound_assumed = True`, failing on Policy B since $228 > 150 = 2 \cdot 75$, excess $78$) and `settlement_policy.py` ranks by coarse fallback frequency $CF$ alone (`192 < 228`), selecting Policy A (`Q_5_8`, `selected_neg_num = 96 > 80 = tau_n`, `surcharge = 16`, `payout = 857 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 10801` (`infeasible_policy_reversal_lock`), legacy constraints lock `tax_policy.py` and `settlement_policy.py` to their CF-only ranking and surrogate settings while requiring $N_{\min} \le 80$, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `42` live API attempts, `$0.037957` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `selected_policy` | `selected_neg` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10800` | `repairable_policy_reversal_defect` | **A** | `coarse_cf_only_ranking_gate` | `blocked_unresolved` | `Q_5_8` | `96` | `16` | 1 | 6 | `$0.005663` |
| `10800` | `repairable_policy_reversal_defect` | **B** | `partial_m_context_bound_update` | `blocked_unresolved` | `Q_5_8` | `96` | `16` | 1 | 6 | `$0.006202` |
| `10800` | `repairable_policy_reversal_defect` | **C** | `explicit_lggr_dual_metric_policy_reversal_directive` | **`completed`** | **`p_star`** | **`75`** | **`0`** | **1** | **6** | **`$0.007074`** |
| `10801` | `infeasible_policy_reversal_lock` | **A / B / C** | All policies | `safe_escalated` | `Q_5_8` | `96` | `16` | 1 | 24 | `$0.019018` |

## 19. 3-Agent Tool-Assisted Fiber Splitting vs. Unassisted Self-Reflection Campaign (`--topology fiber_splitting`)

In `--topology fiber_splitting`, 3 concurrent LLM workers edit `pricing_split.py`, `tax_split.py`, and `settlement_split.py` over 4 aliased state configurations $x \in \{x_{00}, x_{01}, x_{10}, x_{11}\}$ with target values $f = (0, 4, 8, 12)$ under coarse status telemetry $\pi_0(x) = \text{'status\_ok'}$:
- On `seed 10900` (`repairable_fiber_splitting_defect`), `tax_split.py` and `settlement_split.py` initially emit uninformative probe bits `[0, 0, 0, 0]` (`W0 = 12`, minimax floor `6`, `state_predictions = [6, 6, 6, 6]`, `ambiguity_surcharge_cents = 6`, `payout = 867 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 10901` (`infeasible_fiber_splitting_lock`), legacy constraints lock `tax_split.py` and `settlement_split.py` to `[0, 0, 0, 0]` while requiring $W_2 = 0$, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `43` live API attempts, `$0.040917` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `fiber_width` | `minimax_floor` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `10900` | `repairable_fiber_splitting_defect` | **A** | `unassisted_coarse_status_reflection` | `blocked_unresolved` | `12` | `6` | `6` | 1 | 7 | `$0.006509` |
| `10900` | `repairable_fiber_splitting_defect` | **B** | `partial_1bit_tax_probe_split` | `blocked_unresolved` | `4` | `2` | `2` | 1 | 6 | `$0.006573` |
| `10900` | `repairable_fiber_splitting_defect` | **C** | `explicit_lggr_2bit_tool_fiber_splitting_directive` | **`completed`** | **`0`** | **`0`** | **`0`** | **1** | **7** | **`$0.007524`** |
| `10901` | `infeasible_fiber_splitting_lock` | **A / B / C** | All policies | `safe_escalated` | `12` | `6` | `6` | 1 | 23 | `$0.020311` |

## 20. 3-Agent Disagreement-Preserving Side-Channel Council $S \ge K > 2$ vs. Collapsing Consensus Campaign (`--topology council`)

In `--topology council`, 3 concurrent LLM workers edit `pricing_council.py`, `tax_council.py`, and `settlement_council.py` over $K = 3$ distinct latent root causes (`rebate_drift`, `jurisdiction_mismatch`, `fee_tier_overflow`, 5 cents surcharge per collided cause):
- On `seed 11000` (`repairable_council_capacity_defect`), `tax_council.py` and `settlement_council.py` initially emit collapsing scalar consensus symbols `[0, 0, 0]` (`S_cons = 1 < K = 3`, `active_collision_floor = 2`, `shared_remediation_support = False`, `poe_partition_sum = 0`, `council_collision_surcharge_cents = 10`, `payout = 863 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 11001` (`infeasible_council_capacity_lock`), legacy constraints lock `tax_council.py` and `settlement_council.py` to `[0, 0, 0]` while requiring $S \ge 3$ and zero collision surcharge, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `41` live API attempts, `$0.038325` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `collision_floor` | `poe_sum` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `11000` | `repairable_council_capacity_defect` | **A** | `collapsing_scalar_consensus_gate` | `blocked_unresolved` | `2` | `0` | `10` | 1 | 6 | `$0.005613` |
| `11000` | `repairable_council_capacity_defect` | **B** | `partial_binary_escalation_tag_split` | `blocked_unresolved` | `1` | `0` | `5` | 1 | 6 | `$0.006173` |
| `11000` | `repairable_council_capacity_defect` | **C** | `explicit_lggr_disagreement_council_directive` | **`completed`** | **`0`** | **`3/8`** | **`0`** | **1** | **6** | **`$0.006739`** |
| `11001` | `infeasible_council_capacity_lock` | **A / B / C** | All policies | `safe_escalated` | `2` | `0` | `10` | 1 | 23 | `$0.019800` |

## 21. 3-Agent Cross-Role Six-Role Schema Validation & Double-Count Deduplication Campaign (`--topology six_role`)

In `--topology six_role`, 3 concurrent LLM workers edit `pricing_role.py`, `tax_role.py`, and `settlement_role.py` over 3 unique settlement traces `tr-01` (`d1 = -1, m1 = 2`), `tr-02` (`d2 = -1, m2 = 1`), and `tr-03` (`d3 = +1, m3 = 3`) observed across the 6 canonical LGGR III roles (5 cents surcharge per drifted or double-counted role entry):
- On `seed 11100` (`repairable_six_role_deduplication_defect`), `tax_role.py` initially mutates `tr-01` from `(1, 1, 0)` to `(1, 1, 1)` (`verdict_drift_count = 1`), and `settlement_role.py` aggregates un-deduplicated role entries (`deduplicate_by_trace_id = False`, `double_counted_entries_active = 3`, `raw_signed_defect_sum = 0 != unique_signed_defect_sum = -1`, `role_dedup_surcharge_cents = 20`, `payout = 853 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 11101` (`infeasible_six_role_deduplication_lock`), legacy constraints lock `tax_role.py` and `settlement_role.py` to drifting un-deduplicated role summation while requiring zero drift and trace-ID deduplication, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `54` live API attempts, `$0.068249` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `drift_count` | `double_counted` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `11100` | `repairable_six_role_deduplication_defect` | **A** | `un_deduplicated_drifting_six_role_gate` | `blocked_unresolved` | `1` | `3` | `20` | 2 | 12 | `$0.014311` |
| `11100` | `repairable_six_role_deduplication_defect` | **B** | `partial_verdict_preservation_without_dedup` | `blocked_unresolved` | `1` | `3` | `15` | 2 | 12 | `$0.015581` |
| `11100` | `repairable_six_role_deduplication_defect` | **C** | `explicit_lggr_six_role_deduplication_directive` | **`completed`** | **`0`** | **`0`** | **`0`** | **2** | **12** | **`$0.015754`** |
| `11101` | `infeasible_six_role_deduplication_lock` | **A / B / C** | All policies | `safe_escalated` | `1` | `3` | `20` | 1 | 18 | `$0.022603` |

## 22. 3-Agent Stage-Level Unit Tests vs. End-to-End Path-Kernel & Dashboard Adequacy Campaign (`--topology path_kernel`)

In `--topology path_kernel`, 3 concurrent LLM workers edit `pricing_kernel.py`, `tax_kernel.py`, and `settlement_kernel.py` over 4 composite trajectories $c_{i,j} = s_{2,j} \circ s_{1,i}$ (`stage1_verdicts = [1, 0]`, `stage2_verdicts = [1, 1]`, factored boundary product $Z_2 Z_1 = 2 \cdot 1 = 2$, 5 cents surcharge per pointwise EGD disagreement $\mathrm{egd} = n_- + n_+$):
- On `seed 11200` (`repairable_path_kernel_dashboard_defect`), `tax_kernel.py` initially enables `allow_pgd_fallback = True` and `settlement_kernel.py` reports a 3-tuple pass-rate dashboard with `composite_e2e_verdicts = [1, 0, 1, 0]` (`Z_E = 2 = Z_2 Z_1`, `evaluator_residual_re = 0`, masking `n_neg = 1` and `n_pos = 1`, `egd_count = 2`, `kernel_discrepancy_surcharge_cents = 10`, `payout = 863 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 11201` (`infeasible_path_kernel_dashboard_lock`), legacy constraints lock `tax_kernel.py` and `settlement_kernel.py` to PGD fallback cancellation masking while requiring 4-tuple dashboard adequacy and zero EGD, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `48` live API attempts, `$0.053831` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `egd_count` | `r_e` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `11200` | `repairable_path_kernel_dashboard_defect` | **A** | `three_tuple_masked_stage_kernel_gate` | `blocked_unresolved` | `2` | `0` | `10` | 2 | 12 | `$0.012735` |
| `11200` | `repairable_path_kernel_dashboard_defect` | **B** | `disable_pgd_fallback_unmasked_ngd` | `blocked_unresolved` | `1` | `-1` | `5` | 2 | 12 | `$0.012984` |
| `11200` | `repairable_path_kernel_dashboard_defect` | **C** | `explicit_lggr_path_kernel_dashboard_directive` | **`completed`** | **`0`** | **`0`** | **`0`** | **1** | **6** | **`$0.007013`** |
| `11201` | `infeasible_path_kernel_dashboard_lock` | **A / B / C** | All policies | `safe_escalated` | `2` | `0` | `10` | 1 | 18 | `$0.021099` |

## 23. 3-Agent Dynamic Boundary Schema Synthesis Under Online Fiber Collisions Campaign (`--topology schema_synthesis`)

In `--topology schema_synthesis`, 3 concurrent LLM workers edit `pricing_schema.py`, `tax_schema.py`, and `settlement_schema.py` over a 4-state XNOR parity stream $X = \{s_{00}, s_{01}, s_{10}, s_{11}\}$ with candidate metadata features `(k_noise, k1, k2)` and 5 cents surcharge per active fiber collision:
- On `seed 11300` (`repairable_dynamic_schema_collision_defect`), `tax_schema.py` initially locks `lock_schema_v1 = True` (`schema_version = 'v1'`) and `settlement_schema.py` projects with `active_schema_keys = []` (`collision_count = 2`, `decoder_size = 0`, `schema_collision_surcharge_cents = 10`, `payout = 863 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 11301` (`infeasible_hardware_locked_schema_v1`), legacy constraints lock `tax_schema.py` and `settlement_schema.py` to the 0-feature v1 schema while requiring 4-fiber XNOR parity separation, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `48` live API attempts, `$0.051015` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `active_keys` | `collisions` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `11300` | `repairable_dynamic_schema_collision_defect` | **A** | `static_zero_feature_schema_v1_gate` | `blocked_unresolved` | `[]` | `2` | `10` | 2 | 12 | `$0.012618` |
| `11300` | `repairable_dynamic_schema_collision_defect` | **B** | `greedy_single_feature_k2_expansion` | `blocked_unresolved` | `['k2']` | `1` | `5` | 2 | 12 | `$0.013034` |
| `11300` | `repairable_dynamic_schema_collision_defect` | **C** | `explicit_lggr_dynamic_schema_v2_directive` | **`completed`** | **`['k1', 'k2']`** | **`0`** | **`0`** | **1** | **6** | **`$0.007159`** |
| `11301` | `infeasible_hardware_locked_schema_v1` | **A / B / C** | All policies | `safe_escalated` | `[]` | `2` | `10` | 1 | 18 | `$0.018204` |

## 24. 3-Agent Adversarial Prompt Injection Against Boundary Schemas & Side-Channel Bit Allocation Campaign (`--topology adversarial_schema`)

In `--topology adversarial_schema`, 3 concurrent LLM workers edit `pricing_adv.py`, `tax_adv.py`, and `settlement_adv.py` over a 4-state adversarial injection stream $X = \{s_{00}, s_{01}, s_{10}, s_{11}\}$ (`benign_exec`, `prompt_override`, `tool_hijack`, `exfil_payload`) with spoofed agent self-report key `k_agent_self_report = 1` vs. host-authenticated keys `['k_host_1', 'k_host_2']` and 5 cents surcharge per spoofed safety collision or side-channel collision floor unit:
- On `seed 11400` (`repairable_adversarial_schema_side_channel_defect`), `tax_adv.py` initially trusts `trust_agent_self_report = True` (`active_schema_keys = ['k_agent_self_report']`, `spoofed_safety_collisions = 1`) and `settlement_adv.py` allocates `side_channel_bits = 1` ($S = 2 < K = 4$, `side_channel_collision_floor = 2`, `adversarial_surcharge_cents = 15`, `payout = 858 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 11401` (`infeasible_hardware_locked_spoofed_1bit_schema`), legacy constraints lock `tax_adv.py` and `settlement_adv.py` to the spoofed self-report key and 1-bit side-channel wire while requiring collision-free 4-class forensic separation, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `48` live API attempts, `$0.052561` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `active_keys` | `spoof_col` | `sc_floor` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `11400` | `repairable_adversarial_schema_side_channel_defect` | **A** | `unauthenticated_self_report_1bit_gate` | `blocked_unresolved` | `['k_agent_self_report']` | `1` | `2` | `15` | 2 | 12 | `$0.012685` |
| `11400` | `repairable_adversarial_schema_side_channel_defect` | **B** | `authenticate_host_keys_underallocated_1bit` | `blocked_unresolved` | `['k_host_1', 'k_host_2']` | `0` | `2` | `10` | 2 | 12 | `$0.013678` |
| `11400` | `repairable_adversarial_schema_side_channel_defect` | **C** | `explicit_lggr_host_authenticated_2bit_directive` | **`completed`** | **`['k_host_1', 'k_host_2']`** | **`0`** | **`0`** | **`0`** | **1** | **6** | **`$0.007360`** |
| `11401` | `infeasible_hardware_locked_spoofed_1bit_schema` | **A / B / C** | All policies | `safe_escalated` | `['k_agent_self_report']` | `1` | `2` | `15` | 1 | 18 | `$0.018838` |

## 25. 3-Agent Variable-Duration Incident Burst & Graceful-Degradation Shedding Campaign (`--topology graceful_shedding`)

In `--topology graceful_shedding`, 3 concurrent LLM workers edit `pricing_sla.py`, `tax_sla.py`, and `settlement_sla.py` over a simultaneous 3-incident burst (durations $p = (2, 1, 1)$, deadlines $D = (2, 1, 2)$, Pareto floors $f = (4, 3, 4)$, criticalities $\kappa = (10, 8, 3)$) under fixed horizon ceiling $\tau_{\mathrm{horizon}} = 7$ (with 10 cents surcharge per missed deadline and 1 cent per unit of excess criticality loss):
- On `seed 11500` (`repairable_variable_duration_graceful_shedding_defect`), `tax_sla.py` initially defers Incident 3 without shedding (`shed_incident_indices = []`, `start_ticks = [0, 0, 2]`, `missed_deadline_count = 1`, `shedding_surcharge_cents = 10`, `payout = 863 != 873`, `local_green = 1`, `global_green = 0`, $\Delta_E = -1$).
- On `seed 11501` (`infeasible_hardware_locked_unpreemptible_zero_shed_sla`), legacy constraints lock `tax_sla.py` and `settlement_sla.py` to zero shedding under $\tau_{\mathrm{horizon}} = 7$ while requiring zero deadline misses across all 3 incidents, requiring safe escalation.

Executed across 3 concurrent LLM worker models (`max_inflight_requests = 3`, `49` live API attempts, `$0.059779` total cost):

| Seed | Scenario Kind | Arm | Feedback Policy | Outcome | `shed_indices` | `missed` | `excess_loss` | `surcharge` | Waves Run | API Attempts | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `11500` | `repairable_variable_duration_graceful_shedding_defect` | **A** | `deferred_overload_no_shedding_gate` | `blocked_unresolved` | `[]` | `1` | `0` | `10` | 2 | 12 | `$0.013791` |
| `11500` | `repairable_variable_duration_graceful_shedding_defect` | **B** | `priority_inverted_shed_incident_1` | `blocked_unresolved` | `[1]` | `0` | `7` | `7` | 2 | 12 | `$0.014301` |
| `11500` | `repairable_variable_duration_graceful_shedding_defect` | **C** | `explicit_lggr_governed_shed_incident_3_directive` | **`completed`** | **`[3]`** | **`0`** | **`0`** | **`0`** | **1** | **7** | **`$0.007553`** |
| `11501` | `infeasible_hardware_locked_unpreemptible_zero_shed_sla` | **A / B / C** | All policies | `safe_escalated` | `[]` | `1` | `0` | `10` | 1 | 18 | `$0.024135` |

## 26. Equal-Information Baseline vs. LGGR Scope-Migration & Deferred-Obligation Accounting (`--topology obligation_migration`, Theorem 119)

In `--topology obligation_migration`, the 3 concurrent agents maintain a 3-step trajectory `0 -> s1 -> s2 -> s3` across `pricing_mig.py` (`worker-0`), `tax_mig.py` (`worker-1`), and `settlement_mig.py` (`worker-2`) under `BudgetPolicy(max_step=2, max_total=3, representation_id='rep-v1', query_scope='every_prefix')` (`StreamingCodebaseObligationMigrationMonitor`, Theorem 119):

| Seed | Case | Arm | Gate Policy | Status | Trajectory | Migration Count | Obligation Count | Excursion | Surcharge | Waves | API Calls | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `11600` | `repairable_equal_info_migration_and_deferred_obligation_defect` | **A** | `conventional_local_endpoint_baseline_gate` | `blocked_unresolved` | `[0, 2, 3, 1]` | `1` | `0` | `0` | `5` | 2 | 12 | `$0.012420` |
| `11600` | `repairable_equal_info_migration_and_deferred_obligation_defect` | **B** | `deferred_obligation_prefix_excursion_gate` | `blocked_unresolved` | `[0, 2, 4, 2]` | `0` | `1` | `1` | `10` | 2 | 12 | `$0.014020` |
| `11600` | `repairable_equal_info_migration_and_deferred_obligation_defect` | **C** | `explicit_lggr_equal_info_migration_obligation_directive` | **`completed`** | **`[0, 1, 2, 2]`** | **`0`** | **`0`** | **`0`** | **`0`** | **2** | **12** | **`$0.014586`** |
| `11601` | `infeasible_hardware_locked_unmigrated_legacy_rep_v2_and_deferred_obligation` | **A / B / C** | All policies | `safe_escalated` | `[0, 2, 3, 1]` | `1` | `0` | `0` | `5` | 1 | 18 | `$0.018465` |

## 27. Three-Party No-Signalling Constant $c_3 \in [228/75, 7]$ Family Audit (`--topology three_party_c3`, Theorem 120)

In `--topology three_party_c3`, the 3 concurrent agents maintain a 3-module three-party no-signalling settlement codebase (`pricing_c3.py`, `tax_c3.py`, `settlement_c3.py`) audited across the 5-point 8-context slice $k \in \{0, 1, 2, 3, 4\}$ ($\mathrm{CF}_k = (768 + 36k)/3072$, $N_k = (384 - 21k)/3072$) (`StreamingCodebaseThreePartyConstantMonitor`, Theorem 120):

| Seed | Case | Arm | Gate Policy | Status | Effective $c_3$ Bound | $v_2 (k=2)$ | $v_4 (k=4)$ | Uncertified Points | Surcharge | Waves | API Calls | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `11700` | `repairable_three_party_c3_slice_bound_defect` | **A** | `bipartite_c2_surrogate_ceiling_gate` | `blocked_unresolved` | `2` | `1` | `1` | `4` | `10` | 2 | 18 | `$0.016091` |
| `11700` | `repairable_three_party_c3_slice_bound_defect` | **B** | `conjectured_integer_c3_three_ceiling_gate` | `blocked_unresolved` | `3` | `0` | `1` | `1` | `5` | 2 | 13 | `$0.017812` |
| `11700` | `repairable_three_party_c3_slice_bound_defect` | **C** | `explicit_lggr_three_party_c3_bracket_directive` | **`completed`** | **`76/25` (`228/75`)** | **`0`** | **`0`** | **`0`** | **`0`** | **2** | **12** | **`$0.015375`** |
| `11701` | `infeasible_hardware_locked_bipartite_c2_surrogate_ceiling` | **A / B / C** | All policies | `safe_escalated` | `2` | `1` | `1` | `4` | `10` | 1 | 19 | `$0.024187` |

## 28. Multi-Loop 2-Complex Cup-Product & Hodge-Laplacian Harmonic Kernel Audit (`--topology multi_loop_hodge`, Theorem 121)

In `--topology multi_loop_hodge`, the 3 concurrent agents maintain a 3-module multi-loop settlement codebase (`pricing_hodge.py`, `tax_hodge.py`, `settlement_hodge.py`) on the 5-vertex, 6-edge, 1-filled-triangle 2-complex $K = T_{012} \sqcup C_{234}$ (`StreamingCodebaseMultiLoopHodgeMonitor`, Theorem 121):

| Seed | Case | Arm | Gate Policy | Status | 1-Cochain $h$ | $e_{\mathrm{ex}}$ | $e_{\mathrm{co}}$ | $e_{\mathrm{harm}}$ | $|\mathrm{cup}|$ | Surcharge | Waves | API Calls | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `11800` | `repairable_multi_loop_cup_and_harmonic_kernel_defect` | **A** | `local_unit_and_pythagorean_orthogonality_gate` | `blocked_unresolved` | `[3, 0, 0, 1, 1, 1]` | `6` | `3` | `3` | `2` | `8` | 2 | 18 | `$0.015919` |
| `11800` | `repairable_multi_loop_cup_and_harmonic_kernel_defect` | **B** | `filled_loop_curl_and_cup_only_gate` | `blocked_unresolved` | `[2, -1, -1, 1, 1, 1]` | `6` | `0` | `3` | `0` | `3` | 2 | 14 | `$0.014760` |
| `11800` | `repairable_multi_loop_cup_and_harmonic_kernel_defect` | **C** | `explicit_lggr_multi_loop_hodge_directive` | **`completed`** | **`[2, -1, -1, 1, -1, 0]`** | **`8`** | **`0`** | **`0`** | **`0`** | **`0`** | **1** | **6** | **`$0.008064`** |
| `11801` | `infeasible_hardware_locked_unfilled_loop_harmonic_kernel` | **A / B / C** | All policies | `safe_escalated` | `[3, 0, 0, 1, 1, 1]` | `6` | `3` | `3` | `2` | `8` | 1 | 19 | `$0.022409` |

## 29. Coupled Figure-Eight Wedge Junction Gauge Propagation & Mayer-Vietoris Hodge Audit (`--topology figure_eight_wedge`, Theorem 122)

In `--topology figure_eight_wedge`, the 3 concurrent agents maintain a 3-module figure-eight wedge settlement codebase (`pricing_wedge.py`, `tax_wedge.py`, `settlement_wedge.py`) on $K = T_{\mathrm{filled}} \vee_{v_0} T_{\mathrm{unfilled}}$ sharing degree-4 junction vertex $v_0$ (`StreamingCodebaseFigureEightWedgeMonitor`, Theorem 122):

| Seed | Case | Arm | Gate Policy | Status | 1-Cochain $h$ | $e_{\mathrm{ex}}$ | $e_{\mathrm{co}}$ | $e_{\mathrm{harm}}$ | $g_{\mathrm{mis}}$ | Surcharge | Waves | API Calls | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `11900` | `repairable_figure_eight_wedge_junction_gauge_and_hodge_defect` | **A** | `local_unit_and_pythagorean_wedge_gate` | `blocked_unresolved` | `[3, 0, 0, 1, 1, 1]` | `6` | `3` | `3` | `0` | `6` | 2 | 18 | `$0.016914` |
| `11900` | `repairable_figure_eight_wedge_junction_gauge_and_hodge_defect` | **B** | `unilateral_filled_loop_curl_and_junction_shift_gate` | `blocked_unresolved` | `[1, 0, -1, 1, 1, 1]` | `2` | `0` | `3` | `1` | `4` | 2 | 16 | `$0.021778` |
| `11900` | `repairable_figure_eight_wedge_junction_gauge_and_hodge_defect` | **C** | `explicit_lggr_figure_eight_wedge_directive` | **`completed`** | **`[2, -1, -1, 3, -2, -1]`** | **`20`** | **`0`** | **`0`** | **`0`** | **`0`** | **1** | **7** | **`$0.009192`** |
| `11901` | `infeasible_hardware_locked_unfilled_wedge_loop_and_junction_v0` | **A / B / C** | All policies | `safe_escalated` | `[3, 0, 0, 1, 1, 1]` | `6` | `3` | `3` | `0` | `6` | 1 | 18 | `$0.023448` |

## 30. Shared-Chord Bicyclic Diamond Hodge & Mayer-Vietoris Coupling Audit (`--topology shared_chord_diamond`, Theorem 123)

In `--topology shared_chord_diamond`, the 3 concurrent agents maintain a 3-module shared-chord bicyclic diamond settlement codebase (`pricing_chord.py`, `tax_chord.py`, `settlement_chord.py`) on $K = T_{\mathrm{filled}} \cup_{e_{01}} T_{\mathrm{unfilled}}$ sharing chord $e_{01} = (v_0, v_1)$ (`StreamingCodebaseSharedChordDiamondMonitor`, Theorem 123):

| Seed | Case | Arm | Gate Policy | Status | 1-Cochain $h$ | $e_{\mathrm{ex}}$ | $e_{\mathrm{co}}$ | $e_{\mathrm{harm}}$ | $c_{\mathrm{mis}}$ | Surcharge | Waves | API Calls | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `12000` | `repairable_shared_chord_diamond_hodge_and_mayer_vietoris_defect` | **A** | `local_unit_and_pythagorean_chord_diamond_gate` | `blocked_unresolved` | `[0, 2, 1, -4, -3]` | `3` | `3` | `24` | `0` | `27` | 2 | 18 | `$0.016636` |
| `12000` | `repairable_shared_chord_diamond_hodge_and_mayer_vietoris_defect` | **B** | `unilateral_upper_curl_clear_chord_shift_gate` | `blocked_unresolved` | `[-1, 1, 0, -4, -3]` | `3` | `0` | `24` | `1` | `25` | 2 | 16 | `$0.019981` |
| `12000` | `repairable_shared_chord_diamond_hodge_and_mayer_vietoris_defect` | **C** | `explicit_lggr_shared_chord_diamond_directive` | **`completed`** | **`[1, 1, -2, -1, 0]`** | **`7`** | **`0`** | **`0`** | **`0`** | **`0`** | **1** | **7** | **`$0.009119`** |
| `12001` | `infeasible_hardware_locked_unfilled_diamond_loop_and_shared_chord` | **A / B / C** | All policies | `safe_escalated` | `[0, 2, 1, -4, -3]` | `3` | `3` | `24` | `0` | `27` | 1 | 18 | `$0.022290` |

## 31. Governed Policy Relaxation & Minimum-Slack Authority Gate Audit (`--topology governed_relaxation`, Theorem 124)

In `--topology governed_relaxation`, the 3 concurrent agents maintain a 3-module policy-governed settlement codebase (`pricing_relax.py`, `tax_relax.py`, `settlement_relax.py`) starting from initial halted policy vector $P_0 = [4, 2]$ across candidate menu $P_{\mathrm{under}} = [4, 3]$ ($\ell^1$ slack $1$, infeasible), $P_{\ast} = [5, 3]$ ($\ell^1$ slack $2 = \Delta_{\mathrm{policy}}^{\ast}$, minimum-slack Pareto), and $P_{\mathrm{over}} = [7, 4]$ ($\ell^1$ slack $5$, excess slack $3$) (`StreamingCodebaseGovernedRelaxationMonitor`, Theorem 124):

| Seed | Case | Arm | Gate Policy | Status | `auth_verified` | Policy ID | Vector $P$ | $\ell^1$ Slack | Excess Slack | Surcharge | Waves | API Calls | Cost (USD) |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `12100` | `repairable_governed_relaxation_authority_gate_and_minimum_slack_defect` | **A** | `unauthorized_worker_self_relaxation_gate` | `blocked_unresolved` | `False` | `P_star` | `[5, 3]` | `2` | `0` | `10` | 2 | 18 | `$0.017287` |
| `12100` | `repairable_governed_relaxation_authority_gate_and_minimum_slack_defect` | **B** | `authorized_over_permissive_slack_gate` | `blocked_unresolved` | `True` | `P_over` | `[7, 4]` | `5` | `3` | `6` | 2 | 14 | `$0.015066` |
| `12100` | `repairable_governed_relaxation_authority_gate_and_minimum_slack_defect` | **C** | `explicit_lggr_governed_minimum_slack_directive` | **`completed`** | **`True`** | **`P_star`** | **`[5, 3]`** | **`2`** | **`0`** | **`0`** | **1** | **8** | **`$0.010746`** |
| `12101` | `infeasible_hardware_locked_unauthenticated_policy_relaxation` | **A / B / C** | All policies | `safe_escalated` | `False` | `P_star` | `[5, 3]` | `2` | `0` | `10` | 1 | 19 | `$0.022162` |

## Offline Verification & Live Execution

```powershell
# Run unit, tamper, and deterministic replay tests (no API calls)
python -m unittest tests.test_concurrent_code_engineering_swarm -v

# Replay archived live 3-agent linear, 4-agent diamond, 3-agent catalyst, 3-agent stateful DFA, 3-agent replay-order, 3-agent coalitional, 3-agent Mayer-Vietoris, 3-agent windowed-drift, 3-agent optional-stopping, 3-agent CPTP channel, 3-agent Regge holonomy, 3-agent k-induction, 3-agent Jacobian, 3-agent boundary-quorum, 3-agent lease-overlap, 3-agent contextual-sheaf, 3-agent watcher-dropout, 3-agent policy-reversal, 3-agent fiber-splitting, 3-agent disagreement-council, 3-agent six-role deduplication, 3-agent path-kernel dashboard, 3-agent dynamic-schema synthesis, 3-agent adversarial-schema side-channel, 3-agent graceful-shedding, 3-agent obligation-migration, 3-agent three-party-c3, 3-agent multi-loop-hodge, 3-agent figure-eight-wedge, 3-agent shared-chord-diamond, and 3-agent governed-relaxation evidence (no API calls)
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
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/lease_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/contextuality_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/gram_dropout_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/policy_reversal_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/fiber_splitting_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/council_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/six_role_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/path_kernel_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/schema_synthesis_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/adversarial_schema_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/graceful_shedding_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/obligation_migration_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/three_party_c3_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/multi_loop_hodge_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/figure_eight_wedge_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/shared_chord_diamond_pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/governed_relaxation_pilot_run/events.jsonl
```
