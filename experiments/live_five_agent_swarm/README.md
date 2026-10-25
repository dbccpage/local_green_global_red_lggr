# Live five-agent dispatch and recovery pilot

Five independent model sessions inspect a shared board, compute invoice totals,
and use tools to propose resource allocations. The host executes admitted work
in SQLite, withdraws resources after two jobs execute, and lets unfinished agents
recover or escalate. Agents see source data and observations, not a solver's answer.

Read [the prospective protocol](PROTOCOL.md) before interpreting results. A/B/C
fork the same live baseline and histories: generic retry, a complete conventional
checker, and that same checker plus LGGR receipts. The independent judge checks
actual execution rows. A successful safe gate alone is not counted as recovery.

From the repository root:

```sh
python -m unittest discover -s tests -p test_live_five_agent_swarm.py -v
python -m experiments.live_five_agent_swarm.runner live experiments/live_five_agent_swarm/evidence/development --development --budget 10
# Deduct development charges from the $10 ceiling before the evaluation run.
python -m experiments.live_five_agent_swarm.runner live experiments/live_five_agent_swarm/evidence/evaluation --budget REMAINING_DOLLARS
python experiments/live_five_agent_swarm/tools/verify_run.py experiments/live_five_agent_swarm/evidence/evaluation
```

Live output directories must be new. Credentials come from the existing OpenRouter
credential resolver; no credentials are written into logs. Live commands consume
paid API usage. Unit tests and replay make no network calls. All prompts, provider
responses and usage, tool effects, gate decisions, independent verdicts, and final
SQLite rows are retained. Source hashes freeze the implementation used by each run.
Provider timings and billing are recorded observations, not independently
recreated measurements. Hashes establish internal consistency, not authenticity.

The pilot uses synthetic tasks and injected failures. It can demonstrate concrete
breakage, detection and recovery on those runs; it cannot establish a general swarm
failure rate, general recovery guarantee, or LGGR superiority. See the run report
for failed cases and the distinction between host blocking and agent recovery.

The [measured results and limitations](REPORT.md) and [machine-readable tables](RESULTS.json)
include all 343 live calls across two development runs and the six-case evaluation.
`tools/verify_run.py` requires a Git checkout containing the recorded source commits;
it extracts the frozen source, verifies its Git blobs, replays the complete event
log, and checks the actual SQLite files. The current replay CLI is for runs made
with the current source hash; use the frozen-source verifier for retained runs.
Agents run under a serial scheduler with separate persistent histories and shared
tool state. This pilot does not exercise simultaneous races or distributed failures.
