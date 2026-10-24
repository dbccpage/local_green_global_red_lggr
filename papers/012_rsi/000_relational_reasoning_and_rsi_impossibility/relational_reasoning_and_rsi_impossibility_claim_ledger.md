# Historical ledger pointer

The pre-integration ledger is preserved verbatim in [docs/pre_integration_claim_ledger.md](docs/pre_integration_claim_ledger.md). It describes the earlier manuscript and is not the claim inventory for version 1.2.3. Current statements and hypotheses are in the manuscript and [docs/embedded_research.md](docs/embedded_research.md); the generated axiom censuses cover actual declarations.


## Version 1.2.3 review corrections

| Claim | Evidence | Scope |
|---|---|---|
| Finite-prefix charge conservation | `PrefixBounds.spending_prefix_invariant`, `unit_spending` | Natural-valued costs and budgets; inequality assumed only below L. |
| Finite refinement/lift bound | `refinement_prefix_bound`, `lift_prefix_bound` | Every counted step consumes at least one unit. |
| Interleaved lift-event bound | `interleaved_lift_event_bound` | Counts events, not elapsed uncharged ticks. |
| Structural alignment scope control | Four `ReviewCountermodels` theorems | Infinite trajectory lacks report-grounded dominance; total natural descent is impossible. |
| Exact cochain optimality | `verify_exact_l1_repair`, review regression tests | Rational certificate replay after numerical candidate search; no universal solver-completeness or Lean/Python refinement claim. |
| Repair admission | Active-repair gate and optimized-Python regression | Certificate replay and exact positive price for nonzero repair. |
| Native metadata parity | `cross_check_eis_metadata_against_rust`, native regression | ASCII role policy, digest, reported capacity arithmetic only; no obstruction replay or identity authentication. |

The [review response](docs/review_response_2026_10_23.md) maps all fourteen findings
to current definitions, code, negative controls or withdrawn historical claims.
The separate named and full censuses enumerate the actual proof estate.
