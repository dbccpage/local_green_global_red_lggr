# Concurrent five-agent protocol v1

Prospective protocol: development seed 5100, then held-out seeds 5200 through
5217, in ascending order. Conditions cycle feasible occupied-slot withdrawal,
infeasible capacity, and no-change control: six evaluation seeds per condition.
Development is excluded from evaluation and all failures are retained.

Five persistent, separate model histories use the same worker-to-model mapping
as the original pilot (GPT-4o-mini, Claude Haiku 4.5, Gemini 2.5 Flash Lite,
GPT-4o-mini, Claude Haiku 4.5). Every initial pass runs all five agents in
concurrent API waves. Each unfinished session advances to its next request;
requests launch together and finish before tools apply in worker-ID order.
This is a synchronous concurrent scheduler, not asynchronous tool execution.
Actual monotonic request intervals are retained and overlap is summarized.
After two jobs execute, recovery runs the three unfinished agents concurrently.
Completed agents' output remains immutable. Max four model calls per turn,
eight tool calls per response, four initial passes, three recovery passes.
Temperature zero, 512 output tokens, no paid transport retries.

Initial failure remains in the seed denominator; no replacement seed is drawn.
A/B/C each starts from identical post-fault state and copied histories. Arm order
rotates by seed modulo three. Every arm has identical tools, retry limits,
complete admission checking and independently judged SQLite execution.
A receives generic rejection; B receives every conventional constraint finding
AND an exhaustive Hall capacity diagnostic (including a deficiency witness).
C receives exactly that same information plus LGGR fiber/budget receipts.
The conventional diagnostic enumerates subsets; the independent oracle searches
matchings. Neither supplies an assignment. Invoice arithmetic is available to
all agents. No prompt supplies repaired values or the correct allocation.

The pilot-wide ceiling is USD 10. Prior measured spend is USD 0.57951748.
Each run claims an allocation against a persistent cumulative ledger before
any inference. An exclusive run lock prevents competing runs. The coordinator
reserves a conservative worst-case cost for every request in an entire wave
before launching it. Network threads never mutate shared budget or event state.
Unreported cost stays reserved. All in-flight calls settle before a stop.
A crash retains the full run allocation. Default run allocation is USD 4;
the development allocation will be USD 0.50. No automatic expansion or reruns
are permitted on exhausted budget. Maximum 3000 attempts per run.

Every request, raw response, model identity, cost, tool result, gate receipt,
intervention, result, and summary is logged. Replay regenerates requests from
histories, re-executes tools and gates, and independently derives verdicts and
summary counters. Hashes are integrity checks, not provider signatures; network
intervals and provider responses remain recorded observations, not facts
cryptographically authenticated by offline replay. Source snapshots are checked
against Git and hashed before spending. Provider generation metadata and SQLite
outputs are cross-checked separately. Original serial evidence is unchanged.

Primary descriptive outcomes: completed feasible repairs, explicit safe
escalation on infeasible cases, controls completed, invalid executions, baseline
failures, calls and dollars. Include all seeds and separate conditional-on-start
rates. Pairwise B/C counts are descriptive, not a powered superiority test.
Safety is enforced by the common complete execution gate. Synthetic injected
faults and a small fixed model/fixture family do not establish population failure
rates, general convergence, or a unique LGGR advantage.
