# Adversarial acceptance review

Mission source: the user-supplied Grok prompt dated 24 October 2026. This
review began before the application API and evaluation results were available.
Entries marked pending are requirements, not passing results.
The adversarial role owns this file and `tests/test_adversarial.py`; it does not
implement the application, case generator, or judge.

## Ten externally observable requirements

| # | Acceptance evidence | Adversarial counterexample |
|---|---|---|
| 1 | Compare the actual action sequence of A and C on the same inadequate boundary artifact. Record either a changed admission/probe/repair/defer decision or the measured null result. | Merely add a diagnostic label after identical execution. |
| 2 | After an every-prefix breach, invoke the ordinary host tool path and show its canary effect count does not increase. | The monitor alerts but a later tool action still executes; a direct helper bypasses the guard. |
| 3 | Under terminal endpoint scope, execute a permitted intermediate excursion and final recovery and obtain a passing independent answer. Run the same history under every-prefix scope and show it blocks. | A sticky alert incorrectly rejects terminal recovery, or changing scope erases a prefix failure. |
| 4 | Merge branches containing a negative sample, nonzero cost, and an unresolved obligation. Verify original query/baseline/scope and cost attribution survive, including an empty later report. | Duplicate arrival doubles costs; merge drops negative evidence; an incompatible query is silently recast. |
| 5 | Mutate a local pass, omit a mandatory witness, change policy/version, and change an artifact. Each must fail an independently recomputed host check. | A self-asserted pass or recomputed digest confers admission. |
| 6 | Restart from persisted original inputs and events and reproduce decisions and final artifact. Independently tamper with input bytes, event/certificate contents, and a fully rehashed decision. | Replay verifies only internal hash consistency or simply echoes stored admission. |
| 7 | Exercise failed tool execution, unknown oracle outcome, and observed negative outcome. Unknown/failure creates no positive label; a known false label remains false. | `bool(nonempty_dict)` or a missing verdict default changes unknown to true. |
| 8 | Independent oracle confirms useful valid completions, repaired completions, and correct insufficient-evidence deferrals. | Reject-all has zero false accepts and is reported as the best controller. |
| 9 | Exhaust shared probes/repairs/retries and verify finite termination with retained obligations and an explicit residual. | A repair resets the permit counter or recursively refines forever. |
| 10 | Record commands, environment, exit status, complete counts and unresolved failures for original relevant suites and application tests. | Count collection as execution, omit failures, or claim a focused suite proves the full repository. |

## Twelve case families

Each family needs disjoint development/evaluation variants, an independently
recomputed task answer where the fixture declares enough information, and
per-mode counts. Template variants are not independent discoveries.

| # | Family | Required contrasting cases and assertions |
|---|---|---|
| 1 | Equal reports, different outcomes | Two verified executions share the semantic report and differ in query answer. Preserve the explicit pair and its label sources; IDs/hashes are excluded from substantive refinement. |
| 2 | Multi-step composition | Locally accepted operations cause a wrong final ledger only through their actual dependency. Downstream consumes the upstream artifact, not the original full task. |
| 3 | Branch join | A duplicate-key/conflicting branch join is obstructed and a compatible join completes. Arrival ordering may vary without changing the semantic result. |
| 4 | Units/sign/representation | Cents versus dollars, positive refund magnitude versus signed refund delta, and supported representation conversion have exact integer expectations. Missing semantics defers; unsupported conversion cannot become authorized through a digest. |
| 5 | Endpoint/prefix | Run one excursion/recovery history under both declared scopes. Signed recovery does not refund irreversible tool attempts. |
| 6 | Deferred obligation | A missing lookup/semantic witness persists through an empty report, branch merge, and restart. Only explicit checked discharge evidence removes it. |
| 7 | Version transition | A declared, validated transition succeeds. Changed evaluator/specification/schema without its transition evidence is unsupported. A probe/refinement preserves the prior version and prior collision. |
| 8 | Evidence acquisition | A permitted probe observes real fixture/SQLite state and resolves a named distinction. An unavailable probe leaves a bounded unknown/defer residual. B may use every probe available to C. |
| 9 | Event integrity | Exact duplicate delivery is idempotent. Causally valid reordering produces the same result. Missing parent, cycle, conflicting same-ID payload, and replay of an already-consumed action are rejected or explicitly unresolved. |
| 10 | Merge evidence/cost | Retain downstream negative evidence under its original proposition, all obligations, and unique event consumption. Reproduce the pinned library merge defect separately from the wrapper result. |
| 11 | Shared budgets | Parallel branches contend for one atomic budget, including retry, failed action, repair, and probe attempts. At most the declared number of tool effects begin; no retry occurs after exhaustion. |
| 12 | Success/repair/defer | Include a correct unrepaired ledger, a successfully repaired ledger, an invalid admitted baseline output, and unresolved evidence that is deferred rather than called false. |

## Leakage and fairness checks

1. Controller inputs contain boundary artifacts, declared contract metadata,
   allowed development examples, and permitted online observations. They do not
   contain evaluation truth, correctness flags, expected ledgers, hidden fixture
   labels, or a task-ID-to-answer map.
2. A final independent judge reads original protected inputs through a separate
   implementation. A controller cannot obtain that answer merely by asking for
   a `verify` probe. Development labels and online observation semantics must
   document their actual provenance.
3. Same-model roles are operational roles, not a claim of epistemic independence.
   Native worker artifacts and raw responses must be identified separately from
   deterministic fixtures.
4. B and C use the same input bytes, allowed tools, contract semantics, thresholds,
   and shared budget. Fixed-trace comparison gives both the identical complete
   evidence. Different acquisition is reported separately from interpretation.
5. The conventional baseline checks the full declared contract, including
   prefixes, semantic versions, evidence integrity, obligations, and joins.
   Matching B/C findings is an informative null result.
6. Unknown coverage remains unknown beyond the observed semantic report carrier.
   Collision-free sampled tables do not establish future report sufficiency.
7. NGD/ZDR/PGD use a justified Boolean global evaluation. Both local and global
   verdicts are printed; joint rejection is not called a successful task.
8. Measured elapsed time, artifact bytes, and attempt counts are actual
   observations. Token/model usage is unmeasured unless supplied by a runtime
   receipt; synthetic counters must not be called tokens.

## Strongest falsification targets

- Reseal a malicious receipt after changing admission/local-pass fields. A
  correct host must recompute the contract and reject the forged claim.
- Arrange two branches and a retry so all observe one remaining permit. Shared
  enforcement must allow only one issued effect.
- Give a coarse report a new execution ID. Its information coverage must not
  improve. Then provide a permitted semantic observation and verify the action
  changes only because that observation supplies the missing distinction.
- Run a terminal recovery with a prior negative intermediate observation, then
  merge it into a different query. Retain the observation under its original
  scope; neither erase it nor reinterpret it as the new query's answer.
- Add an empty branch/report after an unresolved obligation. Admission must not
  silently become possible.
- Claim a migration is `validated` while changing its mapping or version tuple.
  A checked registry mapping must decide support, not the proposal's label.

## Execution status

Initial host components now exist. The latest focused run executed
`python -m unittest discover -s tests -p test_adversarial.py -v` using Python
3.14.2 at the lab root: **36 tests passed, exit 0**, without SQLite resource
warnings. It covers actual SQLite sign/unit transformations and duplicate-join
effects, atomic shared-budget contention, failed retries, causal evidence
merges, and integrated host/replay behavior. The integrated tests use only
development cases. They ran after `evidence/protocol-freeze.json` was written;
this role did not execute held-out evaluation cases or alter frozen oracle,
fixture, protocol, or oracle-test files.

Inspection found that `EvidenceBook.merge` committed its candidate event map
before validating discharge/cost records. On delegated ownership, this role
changed it to commit only after validation, copied retained data to avoid caller
mutation, required the fixed laboratory attempt cost of integer one, checked the
structured discharge evidence shape, preserved unknown global samples without
Boolean coercion, and grouped samples by original query/baseline/scope. The host
remains responsible for trusted observation collection; these checks do not
authenticate an untrusted producer. Rejected merges leave the prior book intact.

The implementation parent also corrected review findings about certificate
consumption, guard precedence, migration validation, application status for A,
SQLite connection lifetime, and explicit later empty reports. The tests exercise
the resulting behavior, rather than preserving earlier implementation mistakes.
One intermediate test failed after the host correctly attributed an obligation
to the refund branch and introduced a separate `later-empty-report` event. The
test now asserts the correct owner, the actual later empty event, and retention
of the obligation; it does not require the earlier misattribution.

| Requirement | Current focused evidence |
|---|---|
| 1 | `test_ablation_changes_operations_and_independent_outcome` observes a changed repair path and independent false-to-true task outcome. `test_verified_collision_drives_probe_and_retains_unknown_current_verdict` checks an actual certificate-consumed probe action. |
| 2 | `test_prefix_block_prevents_next_host_effect` observes one worker effect, the blocked next effect, and no extra permit consumption. Prefix plus missing-evidence guard precedence is checked separately. |
| 3 | `test_terminal_scope_permits_recovery_without_refunding_costs` executes 0 -> 2 -> 1 and independently checks correct admissible completion under both B and C. |
| 4 | Merge unit tests and `test_merge_preserves_negative_auxiliary_and_real_costs` retain the original auxiliary false, ten real extra query attempts, query scope, and obligations. Duplicate/reordered events do not execute again. |
| 5 | Tests reject altered artifacts, changed policy, conflicting replay, missing witness, malformed development certificate, and unregistered migration mapping. The host recomputes local pass from the SQLite output, ignoring a submitted local-pass field. |
| 6 | Input/artifact/event mutation is detected. A forged admission and a changed certificate are fully rehashed, pass chain verification, and are rejected by fresh tool/controller/oracle replay. Separate-process CLI restart execution remains an integration-log item. |
| 7 | Unknown/deferred answers remain `None`, outside defect arithmetic; verified development labels come from actual executed outputs and the independent judge. Collision certificates retain `current_task_verdict=None`. |
| 8 | Correct, repaired, rejected, and unresolved development cases have direct assertions. A successful negative replay remains a refusal/defer. |
| 9 | Failed retries consume the shared limit; exhaustion returns a finite unknown residual before a worker effect. Twelve contending threads produce exactly three effects under a limit of three. |
| 10 | This role's focused suite passes. The inspected upstream summary/log references retain 177/179 pinned passes with two known failures, companion 15/15 passes, and a supplemental current-checkout 382/386 pass result with four failures and explicit concurrent-checkout caveat. Root and paper-local Lean exports compiled separately. Aggregate application logs and final bundle execution remain integration items. |

## Limits of this review

- A sweep of all 24 development cases in A/B/C, with fresh replay of each run,
  completed before the final focused run. It is development evidence, not the
  held-out result. B and C matched actions in that early sweep without supplied
  development certificates; the frozen benchmark must establish final parity
  and cost counts with its actual certificate inputs.
- The source/metadata, obligation evidence, auxiliary negative query, migration
  registry, and state excursions are synthetic fixture constructions. Executing
  SQLite makes their effects reproducible; it does not turn injected faults into
  naturally occurring model failures.
- The inspectable Python host is trusted. Tests show controller data-flow
  separation and that the judge runs after the terminal host decision. They do
  not establish an operating-system sandbox, producer authentication, or blindness
  of a model that could inspect the repository.
- Resealed decision tampering is detected by recomputation from preserved inputs.
  Replacing the entire experiment together with all external checksum anchors is
  outside the integrity claim; hashes are not signatures.
- Development refinement remains a finite-table certificate. Actual completion
  is judged separately, and unknown observations are not Boolean successes.
- The frozen corpus uses unit scales 1 and 100. The parent subsequently aligned
  the tool vocabulary with the protocol's general positive-integer scales and
  integer multipliers, subject to SQLite's exact integer range. A separate
  `test_sqlite_numbers.py` run passed **9 tests, exit 0**, including scales 3/10/125,
  multipliers 0/3/-4/17, Boolean/type rejection before SQLite coercion, exact large
  integers, binding overflow, multiplication/sum overflow, and refusal of float
  money results. These are additional development tests, not held-out cases.

Pending integration review: final held-out A/B/C measurements, same-trace parity,
native raw proposal provenance, separate-process replay, source bundle, and
aggregate application logs. No live API requests were made by this role.
