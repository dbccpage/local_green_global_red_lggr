# Five-agent live recovery pilot, protocol v3 (runtime maintenance; measured pilot remains v2)

This prospective pilot tests whether five real tool-using model sessions can
complete a shared synthetic dispatch task, experience an injected disruption,
and recover without receiving a solution. It does not prove a general advantage
of LGGR, a natural swarm failure rate, or general convergence.

Five workers own one invoice-dispatch job each. Each job has six integer-priced
items and a set of permitted dispatch slots. A worker must compute its invoice
total and reserve a slot; only that worker can alter its proposal. Model tool
calls inspect the shared board, calculate supplied integer line-item totals,
propose a plan, or escalate. Separate conversation
histories persist across the intervention. Model output is never executed as code.
The host executes validated proposals as SQLite transactions. Two jobs execute
before an intervention; their outputs must remain immutable through recovery.

The generator is fixed before live calls. Evaluation seeds 4101 and 4102 withdraw
one occupied unfinished-job slot while preserving feasibility; 4103 and 4104
withdraw all but two slots for the three unfinished jobs, making recovery
impossible; 4105 and 4106 are no-fault controls. Seed 3101 is development only.
An exhaustive matching oracle establishes feasibility independently and never
sends a satisfying assignment to agents. All initial failures remain in results.

For each seed, the five live sessions first create a shared pre-intervention
snapshot. Three arms fork that identical snapshot and those exact histories:

- A: generic failure/retry feedback; agents can inspect the current board.
- B: ordinary complete-contract validation with explicit violated predicates.
- C: the same B feedback plus LGGR fiber and per-resource budget receipts.

All arms use the same admission gate, models, tools, maximum two recovery passes,
and four API calls per agent turn. The safe gate may reject invalid proposals in
any arm; that is recorded as a blocked attempt, never counted as agent recovery.
Both B and C have the complete conventional checker. Equality or a worse C result
is a valid outcome. Arm execution order rotates by seed. After two initial jobs
execute, only the three unfinished workers propose repairs. The two completed
workers remain part of the preserved five-agent system; their work is not rerun.

Requested model assignments are fixed: workers 0/3 use OpenAI GPT-4o-mini,
workers 1/4 use Anthropic Claude Haiku 4.5, and worker 2 uses Gemini 2.5 Flash Lite,
all through OpenRouter. They are five independent agent sessions across three
model families, not five different model families. Temperature is zero; provider
nondeterminism remains. No external browsing, arbitrary shell execution, or
human-authored repaired allocation is available to the agents.

Primary outcomes: valid completion after disruption, invalid execution count,
correct escalation on independently infeasible tasks, and controls completed.
Also report local-green/global-red observations, blocked attempts, agent turns,
API attempts, tokens, cost, and latency by arm. Paired descriptive outcomes only;
six seeds are too small for superiority or population-rate claims. Injected
faults are reported separately from spontaneous model mistakes. No retries or
failed seeds may be omitted from the denominator.

Append-only JSONL events retain request bodies, provider response bodies and IDs,
tool requests/results, snapshots, injected faults, checker/certificate outputs,
and final SQLite rows. Hash chaining and offline deterministic replay detect
inconsistency, not external authenticity. Replay reconstructs tool state from
recorded model responses and compares complete derived events and summaries.
Source and protocol hashes are frozen in each run. An independently implemented
judge checks database rows against source invoice items, allowed slots, uniqueness,
resource availability, and preservation of completed work.

The default first-pilot spending ceiling is USD 10, with no more than 600 API
attempts. Each request reserves a conservative maximum charge before sending;
provider price caps and output/context limits bound consumption. Missing cost or
transport uncertainty retains the reservation; no automatic paid retries. API
keys remain in process memory and are not copied into evidence. Only generated
synthetic task data and model histories are sent to the provider.

Development may uncover implementation defects. Changes must be committed and
recorded before evaluation starts; development evidence remains separate. Any
post-evaluation fix requires a new version and the old evidence stays retained.

## Development revision before evaluation

The v1 development run (seed 3101, source commit 16af298) made 32 live API calls
and cost USD 0.04562550. It failed to establish the initial shared plan because
GPT-4o-mini workers repeatedly submitted incorrect invoice totals. No fault
intervention occurred. That complete failed run and its frozen source remain in
`evidence/development/`; it is not counted as evaluation evidence. Protocol v2
adds a calculator tool operating only on model-supplied line items, equally in
all arms. It does not reveal an allocation, feasible matching, or repair. A second
development run precedes the still-unseen evaluation seeds.

## Post-evaluation maintenance

The measured six-case evaluation used protocol v2 and source commit af69e3e.
Its frozen source bundle and all original evidence remain unchanged. Version 3
repairs the replay CLI's display of a budget-stopped run (which has no
completed-case summary) and closes SQLite handles on interruption, with an
offline regression test. No agent prompt, tool,
gate, intervention, or outcome calculation changed, and no additional live calls
were made for this maintenance. Use each run's frozen source for exact replay.
