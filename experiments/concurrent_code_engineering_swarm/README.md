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

## Offline Verification & Live Execution

```powershell
# Run unit, tamper, and deterministic replay tests (no API calls)
python -m unittest tests.test_concurrent_code_engineering_swarm -v

# Replay archived live evidence (no API calls)
python -m experiments.concurrent_code_engineering_swarm.runner replay experiments/concurrent_code_engineering_swarm/evidence/pilot_run/events.jsonl
```
