# LGGR in a working SQLite workflow

The useful part of Grok's proposal is explicit evidence acquisition, scoped
certificates and preservation of unresolved obligations. This experiment does
**not** establish an accuracy advantage over a complete conventional checker.
That checker and the LGGR integration made the same final decisions; LGGR used
one additional tool attempt and larger evidence records.

## 1. Built and executed

The application is planner → orders/refunds workers → integrator → verifier.
Workers consume the actual planner artifact and their permitted source slices:
orders sees orders/customers; refunds sees refunds. Real SQLite transformations
produce the branch artifacts consumed by integration. An independent Python
integer reference recomputes task truth from original inputs only after the
host records its terminal decision. The source/protocol reading and candidate
selection are documented in [SOURCE_MAP.md](SOURCE_MAP.md) and
[protocol.json](protocol.json). SQLite was selected over a programming chain
and calendar merging because it supports cheap, exact and inspectable effects.

Executed: 24 development cases × three modes; 48 held-out cases × three modes;
48 identical-evidence comparisons; four worked demos; one native-proposal run;
67 application tests; original upstream checks; and a separately labelled
cross-branch compatibility diagnostic. All 144 held-out interactive receipts
and all 48 fixed-evidence comparisons replayed. The clean-extraction receipt
and logs accompany the bundle and repeat the tests, demo, evaluation and saved
interactive/fixed/native replays in separate Python processes without Git or
API credentials. See [clean-extraction.json](evidence/clean-extraction.json).

The independent oracle, generator, allowed features/probes and split hashes
were frozen before evaluation. Production package/vendor Python, native harness,
protocol and development evidence were frozen before the first held-out run.
The frozen source set was checked again afterward. No held-out outcome was
used to tune the controllers. These are deterministic, injected template
variants, not 48 independent naturally occurring model failures. Data-flow
withholding is explicit and tested; the trusted process is not an OS sandbox.

| Actual agent | Engineering contribution | Native runtime role |
|---|---|---|
| Parent `/root` | Host, tools, controller, integration and release checks | Dispatch; deterministic integration and judging |
| `/root/math_upstream` | Mathematical/source review, pin export, reproductions, Lean checks | Planner, then refunds worker using the same agent |
| `/root/oracle_protocol` | Frozen oracle/fixtures/protocol, benchmark, completion audit | None |
| `/root/adversarial` | Merge hardening, adversarial/numeric tests, final audit | Orders worker |

The three native role turns actually ran. Raw input/response files, hashes and
role reuse are preserved in [native/provenance.json](evidence/native/provenance.json)
and [native/run.json](evidence/native/run.json). The resulting ledger was correct
and admissible, using seven local tool attempts. Two worker SQL intervals
overlap on distinct threads. Integration and judging were deterministic host
work. Roles share model/context and prior engineering knowledge; no epistemic
independence is claimed. Provider tokens, model billing and exact backend model
identity were unavailable. Three recorded native role turns are separate from
local attempt units and from engineering work. Replays made no model calls.

All new work is in this application subtree. The dependency is the unchanged
reviewed pin `6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85`. The shared parent checkout
changed concurrently; it is not the dependency or exact-head acceptance evidence.
The final source/evidence manifest includes the native and supplemental helpers.
Earlier development traces and one failed test setup are retained and explained
in [HISTORY.md](evidence/HISTORY.md).

## 2. Where LGGR acts

The two executed development examples have the same rows, operations and coarse
report: `ledger`, `coarse.v1`, four orders, two refunds. Both branch shape checks
pass. The default transformation assumes cents. Original-input metadata says
order amounts are cents in one example and dollars in the other. Independent
judging after SQL execution labels the actual outputs true and false. These
two measured labels, not evaluation answers, supply the collision certificate
in [development.json](evidence/development.json).

The lost distinction is `order_scale_to_cents`. The pinned fiber synthesizer
finds that this one field separates this pair among three allowed metadata
fields. The deployed report acquires all three fields; it is not a demonstrated
minimal schema for unseen tasks. The old collision and both reports remain in
the evidence. The refined decoder includes a false labelled example: constancy
does not mean that every task succeeds, and the upstream `COMPOSABLE_LGGG`
schema label must not be read that way.

The [repaired trace](evidence/demo-release/repaired.json) records:

| Event sequence | Actual behavior |
|---:|---|
| 3 | C verifies and consumes the collision certificate, then requests `semantics`. Current task truth remains unknown. |
| 5 | A permitted SQLite metadata observation supplies scales/sign. |
| 6–8 | Controller requests and issues a counted plan repair; old/new proposals are retained. Order scale changes from 1 to 100. |
| 10–14 | Two workers consume the repaired handoff and produce real SQL artifacts; the branch evidence is merged. |
| 15–18 | Host acquires branch evidence and checks coverage/semantic consistency. |
| 19–22 | Integration produces a candidate; terminal checking admits it; the independent judge subsequently finds it correct. |

For order `o0`, A emits gross 3,900 and net 3,600 cents; C emits gross 390,000
and net 389,700 cents after observing the dollar scale. Both subtract the same
300-cent refund. The global outcome is false for A and true for C, with local
verdicts `[1,1,1]`. B repairs this example equally well using the same observation.
The LGGR-specific mechanism is an explicit certificate consumer, not a claim
that only LGGR can decide to obtain missing metadata.

The [unresolved trace](evidence/demo-release/unresolved.json) has no permitted
`semantics` probe. C defers at event 3 after one planner attempt, with zero worker
effects, no committed output and null global truth. It does not label the
current task false or insert an unknown result as a passing development label.
Bounded retry/decision limits retain residuals rather than loop indefinitely.

In evaluation, [every-prefix](evidence/evaluation/runs/evaluation.query_scope.01.C.json)
blocks after state 0→2 and one worker canary effect; the next worker and
integration do not execute. [Endpoint](evidence/evaluation/runs/evaluation.query_scope.00.C.json)
permits 0→2→1 and commits a correct output after three worker/integration effects.
The independent attempt ledger never refunds spent work when numeric state falls.
Merged negative auxiliary verdicts keep their original query/baseline/scope and
do not masquerade as ledger truth. Obligations survive empty later reports;
only a specific admitted discharge removes one. Duplicate deliveries deduplicate
by identity; genuine retries reserve new shared permits before effects.

The supplemental [branch-join diagnostic](evidence/supplemental-branch-join.json)
adds the explicit query “refunds per order must not exceed gross.” Both branches
are complete, unique and nonnegative on their own. Gross 100 with refunds 50 is
compatible; gross 100 with refunds 150 fails only when combined. Actual SQL and
a separate post-decision Python reference check this relationship. B and C use
the same join guard and give the same answer. This is outside the frozen 48-case
denominator and does not redefine original ledger arithmetic, which can produce
a correct negative net. The frozen `branch_join` family itself is narrower:
it tests an orders-side duplicate fanout. Supplemental design preceded the
held-out run; execution followed it, without changes to frozen source or cases.

## 3. Comparison

Machine-readable [results.json](evidence/evaluation/results.json) contains every
run, exact denominators, per-family metrics and individual local/global verdicts.

| Mode | Correct commits / 48 | Invalid commits | Blocked | Deferred | Correctness among commits | Tool attempts |
|---|---:|---:|---:|---:|---:|---:|
| A: local-only | 29 | 17 | 0 | 2 | 29/46 | 230 |
| B: complete conventional | 33 | 0 | 6 | 9 | 33/33 | 309 |
| C: B plus LGGR | 33 | 0 | 6 | 9 | 33/33 | 310 |

A has 46/46 inadmissible commits because it omits required evidence; this is a
separate measure from its 17/46 arithmetically wrong outputs. B/C have 0/33
inadmissible commits. Each retains three unresolved obligations across three
tasks. Each refuses one arithmetically correct candidate out of 34 actually
produced correct candidates: `query_scope.02` violates its terminal state bound.
That is not a false rejection of a fully admissible task. Tasks stopped before
a candidate exists have no counterfactual correctness label; valid-output
refusal cannot be estimated for those unexecuted artifacts.

Each cell below is **correct / invalid / blocked / deferred**, with denominator
four per mode and family. B and C have identical counts.

| Family | A | B | C |
|---|---|---|---|
| Equal reports | 2 / 2 / 0 / 0 | 4 / 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| Composition | 1 / 3 / 0 / 0 | 4 / 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| Branch join/fanout | 2 / 2 / 0 / 0 | 4 / 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| Units/sign | 0 / 4 / 0 / 0 | 4 / 0 / 0 / 0 | 4 / 0 / 0 / 0 |
| Query scope | 4 / 0 / 0 / 0 | 2 / 0 / 2 / 0 | 2 / 0 / 2 / 0 |
| Obligations | 4 / 0 / 0 / 0 | 2 / 0 / 0 / 2 | 2 / 0 / 0 / 2 |
| Version transition | 4 / 0 / 0 / 0 | 2 / 0 / 2 / 0 | 2 / 0 / 2 / 0 |
| Evidence resolution | 0 / 4 / 0 / 0 | 2 / 0 / 0 / 2 | 2 / 0 / 0 / 2 |
| Event integrity | 4 / 0 / 0 / 0 | 3 / 0 / 0 / 1 | 3 / 0 / 0 / 1 |
| Merge retention | 3 / 0 / 0 / 1 | 1 / 0 / 2 / 1 | 1 / 0 / 2 / 1 |
| Shared budget | 3 / 0 / 0 / 1 | 2 / 0 / 0 / 2 | 2 / 0 / 0 / 2 |
| Completion controls | 2 / 2 / 0 / 0 | 3 / 0 / 0 / 1 | 3 / 0 / 0 / 1 |

On identical complete **available** evidence, B/C findings and normalized
decisions agree **48/48**. Three cases still lack a required resolving probe;
“complete available” does not mean sufficient to answer every query. The offline
collector executes permitted SQL observations and any missing artifacts using
247 separately reported diagnostic attempt units. These do not authorize a
stopped interactive host to continue or enter its resource totals.

Interactive final actions and task outcomes agree **48/48**. Probe sequences
agree 46/48; one ordering differs at equal acquisition cost, and C spends one
extra attempt on `version_transition.03`. It requests semantics before learning
that migration is unsupported, then blocks at sequence 9; B blocks at sequence 6
with one fewer attempt. This is the strongest concrete counterexample to an
orchestration advantage here. C's finite certificates add cost, not earlier
fault localization, in that case. Both modes share complete contract checks;
their agreement is expected from this deliberately fair common implementation,
not a comparison of independently designed algorithms.

| Measured total over 48 cases | A | B | C |
|---|---:|---:|---:|
| Issued probe attempts (including retries) | 0 | 94 | 95 |
| Issued repairs | 0 | 14 | 14 |
| Correct completions following repair | 0 | 14 | 14 |
| Worker branch / shared / integration attempts | 136 / 48 / 46 | 119 / 156 / 34 | 119 / 157 / 34 |
| Serialized events + artifacts, bytes | 1,494,025 | 2,067,317 | 3,068,040 |
| Initial report projection, bytes | 3,168 | 3,168 | 3,168 |
| Final report projection, bytes | 4,416 | 7,188 | 7,252 |
| Host elapsed including oracle, seconds | 0.3363 | 0.4138 | 0.9060 |
| Controller + certificate computation, seconds | 0.0072 | 0.0170 | 0.4148 |
| Fresh interactive replay, seconds | 0.6380 | 0.7879 | 1.3663 |

These timings describe one local run, not a controlled performance estimate.
Evidence size excludes other run-file/provenance data. Report size is the named
coarse/refined projection, not total communication. Repair success means a
correct completion after any requested repair, not independently identified
causal benefit per attempt. C consumed certificates in 28 decisions. Both B/C
record first supported detection events in 20 cases; event sequence and
`first_detecting_boundary` are stored. First causal fault origin and separate
certificate-only CPU time remain unmeasured; no localization superiority is
claimed. Model tokens/cost remain null, not synthetic estimates.

Completed Boolean evaluations: A has NGD 17, ZDR 29, PGD 0 out of 46; B/C each
have NGD 0, ZDR 33, PGD 0 out of 33. All committed local stage verdicts are true.
Unknown global outcomes (A 2, B/C 15) are excluded, not converted to zeros.
Mathematically zero defect also includes joint rejection, although none occurs
among these completed outputs.

Twenty-five evaluation reports differ from the observed development report.
B/C each commit 16 correctly, block four and defer five on those 25; A commits
13 correctly and 11 incorrectly and defers one. Those results use actual
contract observations; the two-row decoder does not certify new-report coverage.
On the separate 24-case development run, A commits 15 correctly and nine
incorrectly; B/C each commit 17 correctly, block three and defer four, with
159 versus 160 attempts. No statistical/population inference is made.

## 4. Reproduced repository findings

All four supplied runtime observations were reproduced at the unchanged pin:
lossy `StreamingAuditMonitor.merge` drops a downstream negative sample and cost
(3 instead of 10); endpoint 0→2→1 raises an intermediate alert despite terminal
recovery; the bundled comparator gives its baseline weaker checks; mocked
HTTP503 retries issue three attempts under a cap of two. No live API request
was needed. The lab bypasses lossy merge, explicitly separates terminal and
prefix semantics, uses complete B, and reserves shared permits at issuance.
These are new host interfaces, not a silently patched dependency.

Original verification is retained in [upstream_findings.md](upstream_findings.md):
179 relevant pinned-source tests ran with 177 passes and two failures (endpoint
expectation and comparator localized-fault count). The separate Volume VIII
companion passed 15/15; CLI selftest, demo and cookbook 04 exited zero. A
supplemental changing-checkout suite had 382 passes and four failures out of 386
and is explicitly not exact-head acceptance. Pinned tests/library were used;
some CLI subprocesses used the complete current checkout, with relevant source
differences separately checked. No failing expectation was changed to pass.

Root and paper-local Lean copies compiled separately with Lean 4.35.0 and their
original axiom censuses. This was direct `lean -o` source compilation, not a
release archive or `lake build`. Their cycle orientations differ. No new theorem
was added and no cochain meaning was invented for ordinary messages.

The historical eight-task/16-completion benchmark has no NGD examples and its
coding handoff receives the original task rather than the prior specification.
Constructed target labels do not establish naturally occurring model failures.
The gluing theorem assumes the global/local equality that application users
would still need to establish. The pair-separation theorem does not prove
deployable minimal-schema discovery. See the exact symbols and source artifacts
in SOURCE_MAP.md.

## 5. Claim ledger

| Status | Claim and boundary |
|---|---|
| Established by execution | Real dependent SQLite branches, repaired/valid completions, explicit unknowns, canary stops, terminal recovery, retained scoped evidence/obligations/costs, shared issuance caps, and tamper-rejecting replay on these fixtures/tests. |
| Established null comparison | B/C have identical final outcomes and same-evidence findings here. C has one extra acquisition and larger evidence/computation cost. No reliability, compression, localization or cost advantage was demonstrated. |
| Proved under stated hypotheses | Existing pinned finite-fiber/collision, signed telescope and prefix implications compiled in their original Lean sources. The application has no proof that local SQL success implies global correctness. |
| Supported only on a finite table | The observed two-example collision and metadata separation, plus recorded outcomes on the 24/48 template splits. New reports do not inherit universal sufficiency. |
| Proposed, not measured benefit | Certificates may help reviewers inspect ambiguity, coverage and obligations. Human audit clarity/usability was not measured. A larger independent task set could test this. |
| Unresolved or refuted | Superiority over complete B, automatic universal minimal schemas, arbitrary-message cochains, general agent/ASI guarantees, production security and Bell/QM conclusions are not established. Original upstream failures remain. |

Grok's fixed-evidence point is useful as an indistinguishability limit. It does
not imply that additional reasoning can never improve an answer from existing
information: computation may uncover consequences not yet extracted. New
observations are necessary to distinguish truly identical reports with different
protected answers, not for every kind of improvement. Similarly, a receipt
does not itself enforce a stop: this experiment's host implements and tests
that control. Hashes establish byte identity, not producer authentication or
external authority. Every certificate's AuthorityEffect remains None.

## 6. What to inspect next

1. [controller.py](lggr_swarm_lab/controller.py) together with
   [host.py](lggr_swarm_lab/host.py): the certificate consumer, filtered argument
   boundary, actual tool admission and post-decision oracle call are where
   hidden truth access or a decorative monitor would be exposed.
2. [evaluation.version_transition.03.C.json](evidence/evaluation/runs/evaluation.version_transition.03.C.json)
   and its B counterpart: directly falsify any claim that C always selects
   evidence more efficiently. Compare the fixed-trace record for the same case.
3. [test_adversarial.py](tests/test_adversarial.py) and
   [native/run.json](evidence/native/run.json): inspect fully resealed forgery,
   prefix canary, obligation retention and actual native attribution. The outer
   event log uses serial audit ordering; branch fragments separately encode
   causal parents, duplicate delivery and merge ordering.

Run the commands in README.md or replay any final `evidence/evaluation/runs/`
receipt. Replaying a negative/deferred receipt successfully preserves its
refusal; it does not convert it to admission.
