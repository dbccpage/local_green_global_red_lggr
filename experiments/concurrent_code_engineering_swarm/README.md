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

## Offline Verification & Live Execution

```powershell
# Run unit, tamper, and deterministic replay tests (no API calls)
python -m unittest tests.test_concurrent_code_engineering_swarm -v

# Replay archived live 3-agent linear and 4-agent diamond evidence (no API calls)
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/pilot_run/events.jsonl
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/diamond_pilot_run/events.jsonl
```
