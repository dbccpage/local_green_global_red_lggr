# Concurrent five-agent pilot: measured results and limits

**The expanded run does not demonstrate an LGGR advantage over the strong
conventional baseline.** Of three completed paired feasible-fault trials,
conventional feedback recovered all three and LGGR feedback recovered two.
All arms used the same complete execution gate. No invalid SQLite executions
were observed; that safety result belongs to the common gate.

This expansion made **1,053 new live API attempts**, including development.
Five separate model sessions issued overlapping requests during initialization;
the three unfinished workers issued overlapping recovery requests after two
jobs had already executed. The evaluation scheduled 18 new seeds: **15 started,
13 finished, two were interrupted by HTTP 429, and three never started**.
Five of the 13 finished cases failed to establish an initial valid plan, leaving
eight fully paired recovery/control comparisons. No failed seed was replaced.

## Design and baseline

[PROTOCOL.md](PROTOCOL.md) was committed before spending. Models and worker IDs
match the serial pilot: GPT-4o-mini, Claude Haiku 4.5, Gemini 2.5 Flash Lite,
GPT-4o-mini, Claude Haiku 4.5. These are five persistent sessions across three
model families. Network calls run concurrently in waves; tool application is
serialized in worker-ID order after each wave. This is synchronous concurrency,
not fully asynchronous shared-state mutation. Logged client request intervals
show peak overlap of five in all three runs and 249 waves with overlap overall
(18 development, 224 evaluation, seven continuation).

A receives generic rejection. B receives every conventional contract finding
and an exhaustive Hall capacity diagnostic, with a deficient subset when
infeasible. C receives that same information plus LGGR fiber and resource-budget
receipts. All arms have identical tools, model assignments, arithmetic access,
admission gates, and retry limits. The conventional capacity check enumerates
subsets; the independent feasibility judge searches matchings. Neither supplies
a repair assignment. Models must choose their own proposals.

The agent prompts and outputs, tool calls, state transitions, complete monitor
receipts, SQLite outputs, costs, and source snapshots are retained. The source
for development and the initial evaluation is `d721ba7`; the operational
continuation uses `c2a9127`. Current main was integrated for continuation, with
no change to the monitors or decision rules exercised by this experiment.

## Completed paired comparisons

These rates are **conditional on successful initialization and all three arms
finishing**, not rates over all scheduled seeds.

| Outcome | A: generic retry | B: complete conventional feedback | C: B plus LGGR receipts |
|---|---:|---:|---:|
| Feasible withdrawals recovered | 1/3 | 3/3 | 2/3 |
| Infeasible cases explicitly escalated | 2/2 | 2/2 | 2/2 |
| Controls completed | 3/3 | 3/3 | 3/3 |
| Invalid executions | 0 | 0 | 0 |
| Calls across these eight paired cases | 88 | 87 | 95 |
| Cost or retained reserve across those cases | $0.26293624 | $0.32822190 | $0.48175612 |

B and C both recovered seeds 5206 and 5212. B recovered 5209 while C remained
blocked. C also safely escalated on seed 5213 before the run was interrupted in
A; B never ran on that seed. That extra C result is preserved but excluded from
the paired table. Comparing three C escalations against two B escalations
without accounting for that interruption would be misleading.

## Complete scheduled denominator

| Condition | Scheduled | Initial-plan failures | Fully paired cases | Other cases |
|---|---:|---:|---:|---|
| Feasible withdrawal | 6 | 2 | 3 | 1 not started |
| Infeasible capacity | 6 | 2 | 2 | 1 interrupted after C, 1 not started |
| Control | 6 | 1 | 3 | 1 interrupted during initialization, 1 not started |

Initial failures were seeds 5200, 5203, 5204, 5208, and 5210. These include
missing valid proposals and resource collisions under concurrency. All remain
in [RESULTS.json](RESULTS.json), which records every arm's outcome across all
18 scheduled seeds. They were not silently dropped to improve recovery rates.

## Concrete break and recovery

On seed 5206, worker-0 had already executed invoice 674 on slot-0 and worker-1
invoice 923 on slot-2 at epoch 0. The host then withdrew occupied slot-1 and
advanced the epoch. The remaining allocation was independently feasible.

B's live agents recovered with slots 6, 4, and 7 for workers 2, 3, and 4;
C recovered with slots 3, 4, and 6. Both wrote three new valid epoch-1 rows while
preserving the first two rows exactly. Each used 15 recovery API calls. A used
21 calls and remained blocked, leaving only the original two rows. This is
actual model-selected tool action and SQLite execution, not a supplied repair.
The different failure on 5209 prevents treating that example as evidence of a
consistent LGGR advantage.

## Provider interruptions and budget

The initial evaluation stopped on a Gemini HTTP 429 at seed 5213, arm A.
All other in-flight calls settled; the failed request retained its $0.031331
reservation. An explicit protocol amendment attempted only the four previously
unstarted seeds. Its first seed, 5214, stopped during initialization on another
Gemini HTTP 429, retaining $0.023286. Paid calls then stopped. Seeds 5215-5217
were never attempted. Neither interrupted seed was retried or replaced.

| Run | API attempts | Received responses | Cost or retained reserve |
|---|---:|---:|---:|
| Concurrent development | 67 | 67 | $0.17694535 |
| Initial evaluation | 947 | 946 | $2.57415122 |
| Unstarted-seed continuation | 39 | 38 | $0.08244952 |
| New work total | 1,053 | 1,051 | $2.83354609 |
| Earlier serial pilot | 343 | 343 | $0.57951748 |
| Entire pilot | 1,396 | 1,394 | **$3.41306357** |

Of the new received responses, **1,048 generation records** match provider-side
IDs, canonical model identities, and costs. Three Gemini responses have null
usage and their generation endpoints return 404, including a targeted second
read-only lookup. The original lookup report is retained as
`provider_verification.initial.json`; those responses remain explicitly
unverified. They and both HTTP 429 calls retain conservative reservations.

The pilot-wide number therefore includes **$0.153731 of unconfirmed reserves**;
provider-confirmed charges total $3.25933257 including the earlier serial run.
The remaining authorized budget is **$6.58693643**, calculated conservatively.
No transport retry or manual model/provider substitution was made.

## Verification and reproducibility

All three new runs replay through their frozen committed source. Replay derives
prompts from agent histories, executes tools, regenerates complete gate receipts,
and recomputes verdicts, counters, and summaries. It also checks interrupted
traces; all **45 SQLite files**, including partial outputs, match replayed
execution events. All 20 source files in each snapshot match its recorded Git
commit. See [README.md](README.md) for offline commands.

The integrated root suite passes **472 tests**. Regression tests cover actual
five-thread overlap, whole-wave budget preflight, settlement of failed waves,
Hall diagnostics against an independent matching search over 256 active-slot
sets, preserved continuation conditions, and rejection of rehashed altered
prompts, tool results, receipts, outcomes, costs, and summaries.

Hashes and offline replay establish internal consistency and source binding;
they do not cryptographically authenticate provider responses or timestamps.
The separate provider lookup adds corroboration where available, with the three
missing records explicitly retained as a limitation. Model failures and cloud
availability failures are separate categories in the evidence.

## Interpretation

This is a working five-session integration with genuine concurrent requests,
agent-selected repairs, durable execution, failures, and conservative budget
accounting. The measured feedback format does not improve on complete
conventional diagnostics in this sample, and costs more in the paired cases.

The sample is small, synthetic, and interrupted. Initialization failures reduce
the paired sample; the two protocol phases are not silently pooled as completed
runs. Condition assignment and arm rotation share a three-seed cycle, so arm
order is fixed within each condition rather than counterbalanced. Models,
providers, token limits, and full-receipt JSON formatting also limit transfer.
A conventional dispatcher that directly computes an assignment was not tested.
These data do not establish general convergence, natural swarm failure rates,
or superiority over conventional methods. No new Lean theorem is claimed.
