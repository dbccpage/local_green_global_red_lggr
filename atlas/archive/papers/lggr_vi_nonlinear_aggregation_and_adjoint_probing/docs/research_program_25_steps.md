# Deferred research program: 25 gated steps

**Date fixed:** 2026-09-15  
**Status:** all steps open  
**Rule:** a cached artifact may motivate a step but cannot satisfy its acceptance gate.

The earlier omnibus is split into three prospective papers: black-box cyclic
evaluation (steps 1–15), distributed probing (steps 16–20), and geometric or
sheaf extensions (steps 21–24). Step 25 releases them separately. No step is a
claim of the present paper.

| Step | Deliverable | Acceptance gate |
|---:|---|---|
| 1 | Question registry for every proposed live-model experiment | Each question has a measurable response variable, null hypothesis, and failure condition. |
| 2 | Provider-independent request and response schema | Schema validation rejects missing model IDs, timestamps, sampling parameters, and raw response hashes. |
| 3 | Immutable raw-transcript store | Every transcript is content-addressed; a replay audit recomputes every digest. |
| 4 | Model-identity snapshot | Provider documentation, exact model identifier, access date, and retirement policy are archived together. |
| 5 | Cost and retry protocol | Prices are dated; timeouts, retries, rate limits, and partial failures have prespecified treatment. |
| 6 | Cycle-task semantics | Each task defines state, edge maps, observation, loop order, and residual before any model call. |
| 7 | Negative controls | Tasks with zero residual are generated independently and must not trigger the detector above the preregistered rate. |
| 8 | Positive controls | Injected nonzero residuals span prespecified magnitudes and must be detected above the preregistered rate. |
| 9 | Blinded annotation guide | At least two annotators label outputs without seeing condition; disagreements and adjudication are retained. |
| 10 | Leakage audit | Prompts are checked mechanically and manually for words or values that reveal the expected answer. |
| 11 | Sampling plan | Power or precision calculation fixes task count, repetitions, model strata, and exclusion rules before collection. |
| 12 | Randomization plan | Seeds, task ordering, model ordering, and temperature assignments are fixed and replayable. |
| 13 | Live pilot | A small current run exercises the full pipeline; pilot outcomes are excluded from confirmatory estimates. |
| 14 | Confirmatory live run | The preregistered pipeline runs without mixing cached, simulated, surrogate, and live observations. |
| 15 | Independent empirical audit | A second operator reproduces tables from raw transcripts and signs a hash-bound discrepancy report. |
| 16 | Quantized-message model | State spaces, quantizer, bit budget, norm, and reconstruction error are defined; edge cases have executable tests. |
| 17 | Loss and delay model | Delivery, loss, reorder, and delay assumptions are explicit; deterministic schedules and randomized schedules are separated. |
| 18 | Asynchronous convergence statement | A theorem states every boundedness, fairness, and step-size hypothesis; proof or counterexample is machine checked. |
| 19 | Byzantine threat model | Fault budget, trust boundary, collusion rule, and aggregation rule are fixed before any robustness bound is stated. |
| 20 | Distributed replication | Simulations and formal statements agree on the same protocol; adversarial mutations violate the claimed bound and recovery restores it. |
| 21 | Lie-group example | Group, action, connection or transport rule, and loop are defined so that telescoping identities and gauge choices are explicit. |
| 22 | Multi-cycle chain model | Boundary matrices are generated from a declared cell complex and verified by dimension and boundary-square checks. |
| 23 | Sheaf model | Stalks, restriction maps, cochains, and the obstruction class are defined; a nonzero class is proved rather than inferred from a plot. |
| 24 | Cross-check of algebra and numerics | Exact small examples are checked in Lean or another proof kernel and independently recomputed in Python. |
| 25 | Separate releases | Each prospective paper has its own ledger, tests, proof map, notebooks, PDF review, archive manifest, and current external-reference audit. |

## Preserved starting material

`research/legacy_omnibus/code/` contains prototypes and historical receipts
related to several steps. They remain in the source repository but are
deliberately outside the public archive and test surface. A later result must
meet the corresponding acceptance gate above; file existence or a historical
passing test is not enough.
