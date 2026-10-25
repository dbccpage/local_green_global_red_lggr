# Concurrent five-agent break-and-recover experiment

See [PROTOCOL.md](PROTOCOL.md) for the prospective design and [REPORT.md](REPORT.md)
for measured results. [RESULTS.json](RESULTS.json) is derived from verified evidence.
The original serial pilot remains in `../live_five_agent_swarm/`.

Five separate live model histories run through concurrent API waves. Tools apply
in deterministic worker order after each wave, permitting exact offline replay.
Two jobs execute in SQLite before a fault; the three unfinished agents then try
to repair their own proposals. No satisfying assignment is provided by the host.

The complete conventional baseline B includes every constraint finding and an
exact finite Hall capacity diagnostic. C gets identical information, tools,
models, and retry limits, plus LGGR receipts. All arms use the same execution gate
and a separate matching/output judge. The experiment measures whether receipts
help recovery beyond a strong conventional baseline, not whether global checks
outperform an intentionally incomplete safety gate.

Offline verification (no API calls):

```powershell
python -m unittest tests.test_concurrent_five_agent_swarm -v
python -m experiments.concurrent_five_agent_swarm.verify experiments/concurrent_five_agent_swarm/evidence/development experiments/concurrent_five_agent_swarm/evidence/evaluation experiments/concurrent_five_agent_swarm/evidence/continuation
python -m experiments.concurrent_five_agent_swarm.tools.summarize
```

The verifier hashes source_snapshot.zip against the recorded source hashes, then
compares those bytes with the recorded Git commit when that commit is in the
clone. A missing commit does not fail the replay: the hashed snapshot is the
source. A present commit whose blob differs still fails. The verifier then
executes each run's frozen source, regenerates all prompts, tools, gates,
verdicts, and summaries, and checks actual SQLite rows. Use it for archived
evidence: directly replaying with newer source appropriately rejects a
source-hash mismatch. Hashes are not provider signatures. Timing overlap is a
recorded client observation.

Provider-side verification is read-only and requires the same OpenRouter account:

```powershell
python experiments/live_five_agent_swarm/tools/verify_provider.py experiments/concurrent_five_agent_swarm/evidence/development experiments/concurrent_five_agent_swarm/evidence/evaluation experiments/concurrent_five_agent_swarm/evidence/continuation
```

A new paid run requires committed source, an unused direct child of `evidence/`,
and an allocation fitting the cumulative USD 10 pilot ledger. Credentials are
loaded through the existing OpenRouter credential loader and are never logged.
Both prior serial spending and every concurrent run count against the ceiling.
`budget.lock` prevents competing runs. An interrupted run retains its allocation;
reconcile provider/evidence costs before releasing that reservation. Do not
remove reservations merely to rerun a failed case. Evaluation failures are part
of the evidence, not invitations to replace seeds.

```powershell
python -m experiments.concurrent_five_agent_swarm.runner live experiments/concurrent_five_agent_swarm/evidence/new-run --phase development --budget 0.50
```

This is a small synthetic experiment across three model families. It does not
establish a general failure rate, general convergence theorem, or LGGR superiority.
The absence of invalid execution is attributable to the common complete gate.
