# LGGR/RSI live swarm experiment: report

Protocol: [PROTOCOL.md](PROTOCOL.md) (v1, frozen before any paid call; revisions R1-R4 recorded there).
Machine-readable results: [RESULTS.json](RESULTS.json) (primary, committed before the sensitivity run),
[RESULTS_SENSITIVITY.json](RESULTS_SENSITIVITY.json). Evidence: `evidence/` (hash-chained gzip JSONL
events per chunk, summaries, ledger, verifier output).

## Can a host trust the agent's verdict? (agent vs host rule on the same evidence)

For every live controller session, the deterministic host elimination rule was applied to exactly the
evidence the agent bought. Rates per (instance, draw); 95% CIs from 10,000 family-stratified cluster
bootstrap resamples over instances ([RESULTS_TRUST.json](RESULTS_TRUST.json), supplementary).

| Arm | n | agent false-accept rate | host-rule false-accept rate (same evidence) | agent - host | agent/host verdict agreement | agent correct | host correct |
|---|---|---|---|---|---|---|---|
| L-0 | 300 | 5.33% [1.67, 9.67] | 5.33% [1.33, 10.00] | 0.00 [-1.00, 1.00] pts | 97.0% [95.0, 98.7] | 83.7% | 83.3% |
| L-B | 1200 | 3.50% [1.92, 5.33] | 3.50% [1.92, 5.33] | 0.00 [0.00, 0.00] pts | 98.4% [97.8, 99.1] | 84.8% | 84.3% |
| L-C | 1200 | 3.83% [2.08, 5.75] | 3.75% [2.08, 5.67] | +0.08 [0.00, 0.25] pts | 98.8% [98.2, 99.4] | 84.7% | 83.8% |

- **Every false accept, agent or host, is an out-of-model control** (L-0 16, L-B 42, L-C 46 agent; 16 /
  42 / 45 host). On clean and malformed-evidence instances neither the agents nor the host rule ever
  accepted a system that fails its contracts.
- On out-of-model controls, where the world violates the declared hypothesis space, both accept wrongly
  about a third of the time (L-B 42/120 = 35%, L-C 46/120 = 38%, L-0 16/30 = 53%). Agreement is high
  precisely because both are fooled the same way: the evidence is consistent with a passing hypothesis.
  This is the failure a host cannot detect with pass/fail checks alone; it needs an explicit
  model-mismatch test.
- Where they disagree (1-3% of sessions), the agent is usually more conservative: in 33 sessions it did
  not accept where the host rule deferred or accepted (it avoided 1 host false accept; 9 of these were
  wrong rejects of passing systems), and once it correctly reported `model_mismatch` where the
  host rule deferred. It went beyond what the evidence licenses in 7 sessions (agent accept, host
  defer); 2 of those 7 were false accepts on out-of-model controls (L-0 1, L-C 1).
- Conditional on cases where accepting is wrong (target reject or model_mismatch; L-B/L-C n=745,
  L-0 n=191): agent false-accept 5.6% / 6.2% / 8.4% (L-B / L-C / L-0), identical to the host rule within 0.1
  points.

## Bottom line

- **P1 (host elimination rule, 4 units): LGGR selection beats uncertainty reduction.** C - B =
  **+0.268** correct decisions per (instance, draw), 95% CI [0.225, 0.309], Holm-significant
  (p < 1e-4, 10,000 family-stratified cluster resamples). Interpretation: **benefit**.
- **P2 (live model controllers, 4 units): no difference between LGGR and uncertainty advice.**
  L-C - L-B = **-0.001**, 95% CI [-0.013, 0.013], p = 0.95. Under the frozen rules this is
  **absorbed-by-agent** (P1 benefit, P2 inside the +/-0.10 equivalence margin): the Haiku 5.5
  controllers reach about 85% correct whatever note they are given, including no advice (L-0).
- The live controllers do better than either host-rule selector at the same budget (L-B/L-C 85% vs C@4
  76% and B@4 50% correct), spending about 2.1 of 4 units on average.
- All errors by every selector and every controller on clean instances are deferrals or rare false
  rejects; false accepts occur only in out-of-model controls, where the true hidden value lies outside
  the public domain. C's speed has a cost there: it resolves out-of-model cases quickly and wrongly
  (46 false accepts vs 24 for B at 4 units).
- Repair (secondary) and RSI memory (secondary) show no arm difference beyond noise.
- A cap sensitivity rerun (16k input / 8k output) of the 270 affected cases leaves both primary
  conclusions unchanged (P1 +0.271, P2 -0.004).
- Spend: USD 30.34 cumulative (development 0.40, primary evaluation 20.61, sensitivity 9.33).

## What was run

400 held-out generated instances (100 per family: allocation, temporal, interface, combined; per family
80 clean, 10 malformed-evidence, 10 out-of-model), 3 model draws each, `claude-haiku-5-5` via the
Anthropic API (adaptive thinking, effort low, max_tokens 4096, strict tools, no retries, count_tokens
before every request, 10,000-token input cap). Per (instance, draw): five persistent agents ran two
wave-synchronous proposal waves; the frozen snapshot was scored by every offline arm at budgets
1/2/4/8; live controllers L-B and L-C ran on all 1,200 snapshots and L-0 on the preselected
100-instance subset (300 snapshots); 60 preselected clean instances x 3 draws ran repair continuations
for L-B and L-C; 30 preselected clean instances x 3 draws ran the RSI learn/restart/use protocol for
memory arms C (plain) and D (bound). Arm order was randomized per instance and arms were interleaved
within each wave.

Development (8 separate instances, USD 0.40) confirmed the API configuration and exposed two input-cap
problems that were fixed before evaluation (R2: controllers as new challenger-role sessions instead of
forks of the challenger's full history; R3: fresh sessions for the RSI use phase). The power simulation
recorded before evaluation (`evidence/development/power.json`) gave P1 power ~1.0 and P2 power 0.77 for
a 5-point effect at alpha 0.025.

## Primary results

| Contrast | Estimate | 95% CI | p (two-sided) | Holm threshold | Interpretation |
|---|---|---|---|---|---|
| P1: C - B, host rule, 4 units | +0.268 | [0.225, 0.309] | < 1e-4 | 0.025 | benefit |
| P2: L-C - L-B, agent verdict, 4 units | -0.001 | [-0.013, 0.013] | 0.95 | 0.05 | absorbed-by-agent |

P2 discordance: of 1,200 paired snapshots, 983 both correct, 150 both wrong, 34 only L-B correct, 33 only
L-C correct.

### Offline arms (1,200 snapshots)

| Arm | correct | defer | false accept | false reject | mean units to resolve |
|---|---|---|---|---|---|
| A shadow (all report success) | 625 | 0 | 0 | 575 | - |
| B @1 / @2 / @4 / @8 | 121 / 253 / 595 / 1018 | 1060 / 914 / 550 / 70 | 3 / 6 / 24 / 51 | 16 / 27 / 31 / 61 | 0.73 / 1.40 / 2.65 / 3.99 |
| C @1 / @2 / @4 / @8 | 329 / 721 / 916 / 1040 | 832 / 407 / 179 / 42 | 13 / 32 / 46 / 51 | 26 / 40 / 59 / 67 | 0.90 / 1.49 / 1.90 / 2.49 |
| round-robin @4 | 459 | 705 | 8 | 28 | 2.78 |
| recently-changed @4 | 455 | 698 | 2 | 45 | 3.42 |
| dependency-risk @4 | 522 | 613 | 5 | 60 | 3.74 |

Shadow acceptance A never accepts wrongly here only because the challenger almost never reports
`success`; it rejects 575 snapshots that actually satisfy the global contract.

P1 strata (mean C - B at 4 units): allocation +0.29, temporal +0.09, interface +0.49, combined +0.20;
clean +0.31, malformed +0.23, out-of-model -0.03; instances with a distractor hidden parameter +0.26,
without +0.27 (so the effect is not driven by distractors); snapshots already resolved before any check
(38 of 1,200) contribute 0.

All false accepts/rejects of B and C at 4 units are in out-of-model controls (B: 24 FA, 31 FR, 3 correct
of 120; C: 46 FA, 59 FR, 0 correct). Neither selector targets model-mismatch detection, and C's faster
resolution converts out-of-model cases into confident wrong verdicts more often than B's slower one.

### Live controllers (budget 4, turn cap 6)

| Arm | n | correct | defer | FA | FR | host rule on agent's evidence correct | agent/host agreement | complied with note | mean units | mean turns | denied calls | failures |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L-0 | 300 | 251 | 23 | 16 | 10 | 250 | 97.0% | 100% (trivial) | 2.19 | 2.98 | 15 | 3 |
| L-B | 1200 | 1017 | 74 | 42 | 67 | 1012 | 98.4% | 41.9% | 2.09 | 2.95 | 95 | 6 |
| L-C | 1200 | 1016 | 73 | 46 | 65 | 1005 | 98.8% | 68.4% | 2.08 | 2.91 | 79 | 2 |

On the L-0 subset the three arms are indistinguishable (correct 251 / 249 / 248 of 300). Controllers
follow the L-C note more often than the L-B note (first check among the note's recommendations), but
this does not change what they conclude. Agent verdicts and the host rule applied to the evidence
the agent bought agree 97-99% of the time, so the agents mostly decide exactly what the evidence
licenses. Again, every false accept is an out-of-model control (L-B 42, L-C 46); on clean instances
controllers made 5 (L-B) and 2 (L-C) false rejects and otherwise deferred.
Live correctness by family: allocation 0.89, temporal 0.73, interface 0.89, combined 0.87.
Controller cost per correct verdict: USD 0.0018 for every arm.

### Repair (secondary; 60 instances x 3 draws per arm)

| Arm | system passed before | repaired system passes (blind 16-unit grader) | repair controller correct | repair controller false accept |
|---|---|---|---|---|
| L-B | 71/180 | 92/180 (51.1%) | 167/180 | 0 |
| L-C | 71/180 | 89/180 (49.4%) | 167/180 | 0 |

Paired outcomes: 89 both pass, 88 both fail, 3 only L-B passes, 0 only L-C passes. Repairs raise the
pass rate by about 11 points in both arms; the advice does not matter. Note: 471 of 3,600 repair-wave
requests (13%) were refused over the 10,000-token input cap because repair waves continue full proposal
histories as specified; see the sensitivity analysis.

### RSI memory (secondary; 30 instances x 3 draws per arm)

| Arm | learn-phase final system passes | v2 (revised contract) system passes | v2 local tests green | mean memory records | mean obligations |
|---|---|---|---|---|---|
| C plain | 49/90 | 36/90 (40.0%) | 89/90 | 10.5 | 4.8 |
| D bound | 53/90 | 40/90 (44.4%) | 88/90 | 10.3 | 4.7 |

Paired v2 outcomes: 34 both pass, 48 both fail, 6 only D passes, 2 only C passes (exact sign test
p = 0.29). Direction favours source-bound memory but the sample is too small to claim an effect.

## Failures (primary evaluation, all counted, never retried)

29,404 evaluation responses:

| Category | over input cap (refused before dispatch) | output-truncated at 4,096 | transport error |
|---|---|---|---|
| proposal (12,000) | 0 | 198 | 0 |
| controller | 8 | 2 | 1 (APIConnectionError) |
| repair wave (3,600) | 471 | 6 | 0 |
| repair controller | 18 | 0 | 0 |
| RSI (5,400) | 15 | 110 | 0 |

Truncations are agents whose adaptive thinking ran past the 4,096-token output cap. No refusals (`stop_reason: refusal`), no 4xx/5xx, no model or API version drift
(`claude-haiku-5-5` throughout). A failed proposal agent stops for that phase; a failed controller yields
`defer`.

## Cap sensitivity analysis (separate from the primary endpoints; protocol R4)

Approved by the owner after the primary results were committed. The 270 evaluation (instance, draw)
cases (146 instances) with any output-truncated or over-input-cap request were re-run with 16,000 input /
8,192 output caps. Each case reused its recorded primary trajectory up to its first capped failure
(4,022 reused responses, each verified byte-for-byte against the primary evidence) and continued live
(3,400 live responses; 3 still exceeded the 16k input cap). Results with those cases replaced
([RESULTS_SENSITIVITY.json](RESULTS_SENSITIVITY.json)):

| Quantity | Primary | Sensitivity |
|---|---|---|
| P1: C - B @4 | +0.268 [0.225, 0.309] | +0.271 [0.229, 0.313] |
| P2: L-C - L-B | -0.001 [-0.013, 0.013] | -0.004 [-0.017, 0.008] |
| live controller correct L-0 / L-B / L-C | 83.7% / 84.8% / 84.7% | 84.0% / 84.9% / 84.5% |
| live controller failures (all arms) | 11 | 0 |
| repaired system passes L-B / L-C | 51.1% / 49.4% | 52.8% / 53.9% |
| repair controller correct L-B / L-C | 92.8% / 92.8% | 97.2% / 96.7% |

The token caps did not drive either primary conclusion. They depressed the repair secondary (mainly the
repair controller), which recovers with larger caps, still without an arm difference.

Two earlier sensitivity attempts are kept in `evidence/sensitivity/`: one stopped before any request
(ledger had no `sensitivity` phase), one crashed mid-run on a Windows file lock while saving the ledger
(fixed by retrying the local rename). Its outstanding reservations were retained as charges, as the
protocol requires.

## Spend

From the persistent ledger (`evidence/ledger.json`), USD:

| Phase | requests | settled on reported usage | retained reservations | total |
|---|---|---|---|---|
| development | 605 | 0.397 | 0 | 0.397 |
| evaluation (primary) | 28,892 | 20.611 | 0.003 | 20.615 |
| sensitivity (incl. crashed attempt) | 5,466 | 5.335 | 3.993 | 9.328 |
| **cumulative** | | | | **30.340** |

Owner ceilings: USD 150 cumulative (lowered from 160, R4); target below USD 100 met. Retained amounts are
conservative reservations for requests whose usage was never settled (one transport error; the crashed
sensitivity wave). Per-request cost in evaluation: proposal ~USD 0.0008, controller ~0.0005, RSI ~0.0007.

## Interpretation and limits

- P1 is a property of the selectors on this generator's problem class: with a fixed elimination rule,
  choosing checks that separate passing from failing hypotheses resolves far more verdicts per unit than
  maximizing information about hypothesis identity. The effect is large in every family and does not
  depend on distractor parameters, but it is smaller in the temporal family (+0.09) and slightly
  negative on out-of-model controls.
- P2 shows that, for a capable controller with the full check catalog and contracts, neither note
  changes the outcome. The controllers effectively do verdict-directed reasoning themselves (they beat
  both host-rule selectors at equal budget), so the advisory signal is redundant.
- Out-of-model controls are the main residual risk for every arm: no arm reliably reports
  `model_mismatch`; fast resolution (C, and live controllers) turns them into confident wrong verdicts.
- The tasks are synthetic and generated; costs and token caps are specific to Haiku 5.5 at effort low.
  The 10,000-token input cap materially affected the repair secondary (13% of repair-wave requests).

## Verification

`python -m experiments.lggr_rsi_swarm.verify <run dirs>` checks the hash chain, that every recorded
source file equals the file at the recorded commit, replays the whole campaign offline in a clean
checkout of those sources (every request payload hash, tool result, snapshot, offline decision,
controller verdict, host-rule verdict and charge must be reproduced exactly) and compares the saved
summary. All 4 development runs, all 23 evaluation chunks (`evidence/evaluation/VERIFY.json`) and the sensitivity run (`evidence/sensitivity/VERIFY.json`, including 4,022 reused primary responses) pass.
The offline test suite is `tests/test_lggr_rsi_swarm.py` (22 tests, all passing).
