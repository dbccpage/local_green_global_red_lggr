# LGGR/RSI live swarm experiment, protocol v1 (frozen before any paid call)

This protocol is committed before any paid API request. Implementation defects
found during the development run may be fixed only before evaluation starts; each
fix is recorded in the "Revisions" section below with its commit, and development
evidence stays separate. Nothing after the first evaluation request changes this
document except appended, dated notes that do not alter the analysis.

## Question

Does verdict-directed (LGGR) evidence selection resolve more global accept/reject
decisions per unit of verification budget than a conventional
uncertainty-reduction selector, (P1) when the host applies a fixed elimination
rule and (P2) when a live tool-using model controller receives the selector's
advice? Secondary: do repair continuations and bound (hash-checked) memory change
outcomes? Equality or a worse LGGR result is a valid outcome.

## Generated tasks

`experiments/lggr_rsi_swarm/generate.py` deterministically produces held-out
evaluation instances (seeds 500000-500399) and separate development instances
(seeds 900000-900007). Evaluation is balanced: 100 instances per family

- `allocation`: shared capacity / overhead budget,
- `temporal`: stage order with cumulative (prefix) budgets,
- `interface`: unit conversion, inclusive bounds and latency across module interfaces,
- `combined`: constraints drawn from two families.

Each instance has three implemented modules (integer key=value configuration files,
interpreted only by the host, never executed), public local contracts, a public
global contract over the module parameters and hidden environment parameters,
and a bounded enumerated hypothesis space: the product of the publicly listed
domains of the hidden parameters (at most 216 hypotheses). Some hidden parameters
may appear in no global constraint (distractors); this is a recorded stratum.
The true hidden assignment is never sent to any model and is read only by the
evidence-access gateway and the blind grader.

Every instance has exactly 16 candidate checks with costs 1, 2 or 4: threshold
probes of one hidden parameter (cost 1), exact measurements of one hidden
parameter (cost 2), integration checks of one global constraint against the frozen
module files (cost 2 when it involves one hidden parameter, else 4), and module
local-test reruns (cost 1, uninformative by construction). Full verification
(the blind grader) costs 16 units and is never a candidate.

Controls per family: 80 clean, 10 malformed-evidence (one or two checks return a
malformed record; malformed records must eliminate nothing), and 10 out-of-model
(one true hidden value lies outside its public domain, so some checks can return
results consistent with no hypothesis). Correct decision target: `accept` if the
frozen system satisfies all local and global constraints under the true hidden
values, else `reject`; for out-of-model instances the target is `model_mismatch`.
`defer` is never correct (unresolved).

## Model and API configuration

Anthropic Messages API directly, official `anthropic` Python SDK, credentials only
from `ANTHROPIC_API_KEY`. `model="claude-haiku-5-5"`, no fallback model, no
`fallbacks` parameter. `thinking={"type":"adaptive","display":"summarized"}`,
`output_config={"effort":"low"}` explicit, no `budget_tokens`, no
temperature/top_p/top_k, no assistant prefill, `max_tokens=4096`,
`tool_choice={"type":"auto"}` (plus `disable_parallel_tool_use=true` for
controller sessions), `strict: true` and `additionalProperties: false` on every
tool. Tool inputs are validated again by the host; invalid input returns a
`tool_result` with `is_error: true`. Histories are append-only and thinking blocks
are passed back unchanged. Each conversation keeps one fixed tool list for its
whole life. Prompt caching uses a breakpoint on the stable prefix (tools, system,
contracts, snapshot) and on the latest message.

Client `max_retries=0`. `max_tokens` and `refusal` stop reasons, any 4xx, 5xx,
transport error or timeout are recorded as failures and never retried. A failed
proposal agent makes no further requests in that phase; a failed controller
yields `defer`. `count_tokens` (free) runs on every request with the exact
model/system/tools/messages/thinking/tool_choice; requests over 10,000 input tokens
are refused before dispatch and recorded as failures. Every response's `model`
string must equal the first resolved model string and the SDK/API version header
must not change; otherwise the run halts. `models.retrieve` output is recorded.

## Spending

Rates (USD per million tokens, prompts <= 100K): input 0.10, 5-minute cache write
0.125, cache read 0.01, output 0.50. Reservation per request
R = 10000 x 0.125e-6 + 4096 x 0.50e-6 = USD 0.003298. A persistent ledger
(`evidence/ledger.json`, atomic replace) reserves whole waves transactionally
before launch, settles each request on reported usage, keeps the full reservation
for any failed or interrupted request (including crashes: unsettled reservations
found at start-up are converted to charges), and requires all launched requests
of a wave to settle before the next wave is reserved. Hard cumulative ceiling
USD 160 (development USD 20, evaluation USD 140); target below USD 100.

## Phases

Agents: five persistent sessions per (instance, draw): `impl-0`, `impl-1`,
`impl-2` (each owns one module file), `tester` (integration tester) and
`challenger`. Three independent model draws per instance (draw 0, 1, 2).

1. Proposal. Two wave-synchronous waves: one request per agent per wave. Local
   unpriced tools: `read_contract`, `read_file`, `write_file` (own file only),
   `run_local_tests` (own module only; testers/challengers have notes files and no
   module), `post_note` (text and status `success|concern|blocked`). The host
   executes tool calls between waves in agent order and delivers results (and
   peers' new notes) at the start of the next wave. After wave 2 the tool calls
   are executed, the module files are frozen as the snapshot, and transcripts are
   frozen. `run_check`/`submit_verdict` exist in the same fixed tool list but are
   denied (`is_error`) outside controller phases; no proposal tool reads hidden
   values or check outcomes.

2. Offline arms on each frozen snapshot (no API calls). Host elimination rule:
   hypotheses inconsistent with a well-formed observation are removed; malformed
   observations remove nothing. Empty set -> `model_mismatch`; all remaining pass
   -> `accept`; all fail -> `reject`; else `defer`. All arms stop acquiring when
   the host rule is resolved or no affordable unrun check remains. Arms:
   - A shadow: accept iff every agent's latest posted status is `success`, else reject (no checks).
   - B: maximize expected entropy reduction of hypothesis identity per unit cost
     under uniform weights over consistent hypotheses.
   - C (LGGR): maximize worst-case number of eliminated opposite-verdict
     hypothesis pairs per unit cost, witnesses drawn only from hypotheses
     consistent with acquired observations; if every affordable check has zero
     worst-case elimination, use expected (uniform) eliminated pairs per cost; if
     that is also zero, stop.
   - Secondary: round-robin (id order), recently-changed (checks touching the
     module files written last in the proposal phase first), dependency-risk
     (checks involving the most hidden parameters and modules first).
   Ties broken by lowest check id. Budgets 1, 2, 4, 8; primary 4.

3. Live controller arms (forks of the challenger session) at budget 4: tools
   `run_check(check_id)` (priced; over budget, unknown, or repeated ids return
   `is_error` and charge nothing) and `submit_verdict(verdict in
   accept|reject|defer|model_mismatch, explanation, cited_check_ids)`. Turn cap 6;
   no verdict = `defer`. An "advisor note" is pushed into the opening message and
   into every `run_check` result:
   - L-0: remaining budget and the unrun check ids;
   - L-B: B's top three affordable checks with expected information gain;
   - L-C: one surviving pass/fail hypothesis pair and its affordable separating checks.
   Advisors read only public contracts and acquired observations, never hidden
   state. Prompts are byte-identical across arms except the advisor note. L-B and
   L-C on all 400 x 3 snapshots; L-0 on a preselected 100-instance subset
   (25 per family, chosen by `generate.py` before any results) x 3. The host
   elimination rule is also applied to the evidence each controller bought.

4. Repair. A preselected, family-balanced set of 60 clean instances (15 per
   family). Each draw forks into L-B and L-C continuations: the five agents get
   the arm's controller report, run two more wave-synchronous waves with the same
   tools, then the arm's controller session continues (<= 5 turns) with 4 more
   units on the repaired snapshot. Integration observations from the old snapshot
   are discarded; hidden-parameter observations carry over. A blind grader runs
   full 16-unit verification of the repaired snapshot.

5. RSI. 30 preselected clean instances (family-balanced) x 3 draws x arms
   C (plain memory) and D (bound memory). Identical tools `memory_append(key,
   content, source_ref)`, `memory_recall(query)`, `memory_mark_obligation(text,
   source_ref)`, `memory_list_obligations()` in both arms. Arm C stores and returns
   records as written. Arm D binds each record and obligation to the SHA-256 of
   its `source_ref` (a contract or file) at write time; recall flags records whose
   source changed (`stale`) or whose key has differing contents (`conflict`) and
   also returns open obligations. Phases, each two waves with five agents:
   learn (fresh sessions, contract v1; between waves a postmortem reveals the v1
   grader result and measured hidden values), restart (fresh sessions, contract v2
   in which one hidden domain/value and one module demand change; write_file is
   denied), use (restart sessions continue; build against v2). Outcome: blind
   grader pass on the v2 snapshot.

Arm order is randomized per instance (seeded) and arms are interleaved within
each wave batch. The run halts if the resolved model string or API version changes.

## Analysis (frozen)

Co-primary, Holm-adjusted at family-wise alpha 0.05:
- P1 = mean over (instance, draw) of correct(C) - correct(B), host rule, budget 4;
- P2 = mean of correct(L-C agent verdict) - correct(L-B agent verdict), budget 4.
Family-stratified paired cluster bootstrap over generator instances (all draws of
an instance resampled together), 10,000 resamples, seed 20261026, two-sided
percentile p-values. Before evaluation, power for P1/P2 at alpha 0.025 is simulated
from development measurements and recorded.

Reported: correct, false accept, false reject, defer and mismatch rates (agent and
host rule), agent/host agreement, advisor compliance (first check taken from the
note's recommendations), units to resolution, turns, denied tool calls, cost per
correct decision, secondary selectors and budgets, repair and RSI outcomes, and
every failure. Interpretation per primary contrast: benefit (Holm-significant
positive), disadvantage (Holm-significant negative), practical equivalence (95% CI
inside +/-0.10), absorbed-by-agent (P1 benefit but P2 equivalence), otherwise
inconclusive.

## Gates

1. Offline build and unit tests (no network).
2. Development run on development instances only, <= USD 20.
3. Projection: if measured development cost projects development + evaluation
   above USD 100, stop and report options before spending more. Never exceed USD
   160. No condition is silently shrunk.
4. Evaluation, analysis (REPORT.md, RESULTS.json) and the replay verifier.

## Evidence

Append-only, hash-chained JSONL events (gzip) with source hashes, request
deltas plus request hashes, full provider responses and usage, tool calls and
results, snapshots, ledger operations, failures and decisions. Offline replay
reconstructs every request hash, tool result, snapshot, offline decision, live
host-rule verdict and charge. API keys never enter evidence.

## Revisions

- R1 (2026-10-26, before any paid call): `ANTHROPIC_API_KEY` is read from the process environment, the
  Windows user environment, or the repository's git-ignored `.env` (only that one variable is parsed);
  the value is never logged or recorded. The L-C advisor's example pair takes the first passing
  hypothesis separated by C's top-ranked check and the failing hypothesis nearest to it in Hamming
  distance (ties by index), so that the listed separating checks are informative.
