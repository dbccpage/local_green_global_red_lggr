# Harness contract

**AuthorityEffect: None.**

This is the piece to copy into a harness that is not this repository. The field names match `learn/harness_adapter.py`. That file is a Python reference. A Go loop, a TypeScript graph, or a shell pipeline can emit the same events and compare receipts on the fixtures in `learn/traces/`.

The adapter calls the existing `lggr` monitors. It does not call a model. It does not clear obligations. It does not treat a receipt as permission to merge, deploy, or spend.

## Run declaration

Send one declaration before any event.

| Field | Required | Meaning |
| --- | --- | --- |
| `scope_id` | yes | Name of this finite run. Nonempty string. |
| `query_scope` | yes | `endpoint` or `every_prefix`. |
| `bound` | yes | Integer `max_total` for the signed budget. |
| `global_sample_source` | yes | The only value this course accepts is `external`. |
| `authority_id` | yes | Supplied identity. Not an authentication. |
| `evaluator_id` | yes | Supplied identity of the local rule. |
| `policy_id` | yes | Supplied policy name. The monitor also hashes the policy body. |
| `spec_id` | no | Defaults to `learn-harness/v1` in the reference adapter. |
| `representation_id` | no | Defaults to `learn-declared/v1`. A change of representation is a transport problem, not a silent reinterpretation. |
| `allowed_states` | no | Integer domain. Default `[0, 1, 2]`. |
| `max_step` | no | Integer local step bound. Default `1`. |

`global_sample_source` other than `external` produces a receipt with `status` `GLOBAL_SAMPLE_REJECTED` and `monitor_receipt` null. The reference adapter does not call a monitor for that run.

An event may repeat `global_sample_source`. If that copy is not `external`, that event is rejected the same way, even when the declaration said `external`.

## Events

### `handoff`

| Field | Required | Meaning |
| --- | --- | --- |
| `state_id` | yes | Identity of this observed state. |
| `report` | yes | What the next stage may see. JSON value. |
| `query` | yes | Protected downstream question. JSON value. |
| `metadata` | no | Extra labels. Not part of the fiber key. |

The reference calls `StreamingFiberMonitor.observe`.

### `step`

| Field | Required | Meaning |
| --- | --- | --- |
| `before` | yes | `{"state_id", "value"}`. `value` is an integer. |
| `after` | yes | Same shape. |
| `signed_delta` | no | If present, it must equal `after.value - before.value`. |
| `global_sample` | no | Integer or Boolean `0` or `1`, from outside the proposer. |
| `obligations` | no | Strings the host must retain. |
| `witness_id` | no | Default `w001`, `w002`, ... |
| `step_cost` | no | Nonnegative integer. Default `0`. |

The reference calls `make_witness` and `StreamingAuditMonitor.step`. After the steps, `summary()` returns `get_receipt()`. Read `unresolved_obligations` on that summary. The batch audit `audit_history` promotes a nonempty obligation list to status `WITNESS_INCOMPLETE`. The streaming summary lists the same strings and may keep another primary status. The host reads the list either way.

### `review_edge`

| Field | Required | Meaning |
| --- | --- | --- |
| `src` | yes | Source vertex. |
| `dst` | yes | Target vertex. |
| `value` | yes | Exact integer or rational string. |
| `weight` | no | Positive rational. Default `1`. |

The reference calls `StreamingCochainMonitor.add_edge`.

### `generation`

| Field | Required | Meaning |
| --- | --- | --- |
| `state_id` | yes | History identity. |
| `coarse_report` | yes | The report a later predictor is allowed to see. |
| `target` | yes | Rational target `f` on this state. |
| `refined_report` | no | A finer observation, when you have one. |
| `prediction` | no | Predictor value for this event's report. |
| `use_refined_report` | no | When true, `prediction` is keyed by the refined report. |
| `evaluate` | no | When true, score the predictions stored on this guard. |
| `generation_id` | no | Name of this generation. |

The reference calls `StreamingRSIFiberCeilingMonitor.observe_state` and, when `evaluate` is true, `evaluate_generation`. Predictions are matched by the canonical JSON of the report.

## Envelope

Every reference receipt has this shape:

```json
{
  "lesson_schema": "learn.harness_event.v1",
  "authority_effect": "None",
  "status": "<monitor status, or GLOBAL_SAMPLE_REJECTED>",
  "monitor_receipt": {}
}
```

`monitor_receipt` is the monitor's own object, or null when the adapter refuses the event before calling one. The three wiring functions are `wire_tool_loop`, `wire_handoff`, and `wire_review_cycle`.

## Host duties

These stay with the host. The library will not do them.

- Retain the original history.
- Supply the global sample from outside the proposing stage.
- Treat every receipt as evidence about the supplied rows.
- Read `unresolved_obligations` and keep them until a separate, external admission clears them.
- Refuse to treat a receipt as permission to merge, deploy, or spend.

## Three shapes

**Tool loop.** One agent, many steps. Declaration plus a list of `step` events. Use `every_prefix` when the bound has to hold after every accepted update.

**Handoff.** Specifier, implementer, verifier. A list of `handoff` events. The report is the message. The query is the requirement the message is being asked to determine. Enrich the report when you need a decoder on that table. The enrichment is schema work for the query you declared.

**Review cycle.** Agents passing numeric judgments around a loop. A list of `review_edge` events. The closing edge returns the cycle defect and, when the defect is nonzero, an exact rational repair distance and a dual witness.
