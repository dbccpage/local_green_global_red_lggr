# LGGR SQLite handoff laboratory

This small local experiment reconciles synthetic orders, customers and refunds
into an integer-cent ledger. A planner artifact controls two independently
scheduled SQLite worker branches, an integrator consumes their actual outputs,
and a bounded host admits, repairs, blocks or defers the result. An independent
Python reference scores the task only after the host records its final decision.

The primary comparison is complete conventional checking **B** against the same
contract plus LGGR certificates **C**. **A** checks local artifact reports only.
B and C have the same information, probes, capabilities and shared attempt limit.
The experiment allows a null B/C result. The offline proposals are deterministic
fault fixtures, not unreported model generations. Any native-agent demonstration
and raw responses are separate evidence, with model usage marked unmeasured when
the runtime does not expose it.

The executed 48-case evaluation found identical B/C outcomes: each committed
33 correct ledgers, blocked six and deferred nine, with no invalid commits.
A committed 17 invalid outputs. C used 310 tool attempts versus B's 309;
identical-evidence findings agreed 48/48. See [REPORT.md](REPORT.md) for the
six-part report, limitations and per-family results, and
[results.json](evidence/evaluation/results.json) for exact measurements.

## Run

Use Python 3.10 or newer. Everything needed for the offline experiment is in the
standard library; the pinned LGGR runtime is included in `vendor/`. No API key,
network access, model download or package installation is needed. Run from this
directory:

```text
python -m lggr_swarm_lab demo --output demo-results
python -m unittest discover -s tests -v
python -m lggr_swarm_lab benchmark --protocol protocol.json --output dev-results --split development
python -m lggr_swarm_lab benchmark --protocol protocol.json --output results --split evaluation
python -m lggr_swarm_lab replay demo-results/repaired.json
python -m lggr_swarm_lab replay results/fixed-traces/evaluation.equal_reports.00.json
```

The recorded environment used Python 3.14.2 and SQLite as listed in
`evidence/environment.json`; other Python versions were not executed here.
To inspect the already preserved outcomes without generating new ones:

```text
python -m lggr_swarm_lab replay evidence/demo-release/repaired.json
python -m lggr_swarm_lab replay evidence/demo-release/unresolved.json
python -m lggr_swarm_lab replay evidence/native/run.json
```

`supplemental_branch_join.py` is a separate, executed cross-branch compatibility
diagnostic with an additional nonnegative-net contract. Its evidence is excluded
from the frozen 72-case comparison. `native_session.py` is the recorded native
proposal harness; its responses came from actual Codex collaboration turns.
Offline replay reuses those bytes and makes no new model call.

`python -m lggr_swarm_lab tests` is equivalent to the unittest command. Output
directories must be new or empty, so reruns do not overwrite original evidence.
Use another output name for a repeat. Interactive traces and their individual
replay results are written under `runs/` and `replays/`; complete and partial
identical-evidence comparisons are under `fixed-traces/`. `results.json` contains
exact counts, denominators, per-family results, resource costs, findings and
runtime measurements. `command-log.json` records the invocation, runtime and exit
status. A replay mismatch makes the benchmark command fail while preserving its
outputs.

## Worked development example

The first two development executions use identical raw source rows and the same
proposed operations. Both coarse reports say there are four orders and two
refunds. In one fixture an order amount means cents; in the other it means
dollars. The default proposed SQL transformation assumes cents in both cases.
Both branches locally succeed, while the independent ledger answer differs.

`build_development()` executes both transformations and integrations before asking
the independent oracle for labels. It preserves the original inputs, outputs,
labels and provenance in `evidence/development.json`. `analyze_descent` certifies
the explicit equal-report/different-query pair, and the certificate is replayed.
`StreamingFiberMonitor.synthesize_minimal_refinement` searches only the three
predeclared monetary metadata fields. Adding the observed order scale separates
this pair. This is a two-example result; identifiers and content hashes are never
used as a substantive semantic refinement.

In the repaired demo, C consumes the collision certificate and asks the host for
the permitted `semantics` observation. SQLite supplies the unit/sign metadata.
The controller changes the concrete proposal, the workers consume that updated
planner artifact, and the integrator receives their actual outputs. The oracle
then measures the final ledger independently. The `coarse-ablation.json` trace
retains A's behavior on the same fixture. `unresolved.json` uses an ambiguity whose
resolving probe is unavailable: it must terminate with a residual rather than
invent an answer. The command reports the actual observed outcomes and replay
status for all four demonstrations.

## Boundaries and evidence

The host's public controller view contains the declared contract, actual
proposals, acquired observations, state, obligations and merge facts. It excludes
fixture family, variant, seeds and oracle answers. Original monetary semantics
are available only through an allowed named observation. This is inspectable
data-flow separation inside a trusted local process, not an operating-system
security boundary or a claim that role names establish independent knowledge.

The frozen protocol contains 24 development and 48 evaluation cases, with two and
four variants respectively for each of twelve families. The independent judge,
generator and split hashes were frozen before evaluation in
`evidence/protocol-freeze.json`. The benchmark binds all production Python files,
the vendored runtime, protocol and development evidence in
`evidence/controller-freeze.json` before its first held-out run. Subsequent source
changes cause a failure; evaluation outcomes must not be used to tune this
experiment silently. Repeated fixture variants are not independent discoveries
or a population estimate.

The native harness is also bound in the production freeze. Final artifact
checksums cover all included source, tests, scripts and evidence. Historical
pre-freeze traces and the retained failed test setup are described in
`evidence/HISTORY.md`; final replay targets are the release demo, development
release, evaluation and final native files named in REPORT.md.

Fixed-trace comparison feeds B and C an identical public view. Its separate
offline collector reuses A's preserved worker artifacts and obtains permitted
observations through actual SQLite queries. Any supplemental worker/integration
effects, transient failed probes and successful observations have their own
cost ledger. These diagnostic effects are excluded from interactive costs and
do not imply that an originally stopped host could legally continue. A missing
allowed probe remains unknown. Records with incomplete state evidence are kept
and excluded from the complete-trace denominator.

Task correctness and evidence admissibility are separate fields. A correct
candidate can be inadmissible. When there is no committed output,
`task_correct` is null; an unknown result never becomes an observed passing label. NGD/ZDR/PGD calculations
use only completed outputs with independently measured global truth and include
the corresponding local verdicts. Zero defect can include joint rejection.

Endpoint scope permits a recorded intermediate excursion followed by a valid
terminal recovery. Every-prefix scope stops before the next tool effect. Signed
state changes are distinct from irreversible attempt consumption. Retries,
repairs, probes and both branches use the same atomic shared issuance limit.
Identical delivered event/attempt IDs deduplicate once; actual retries have new
IDs. Merges retain original query scope, negative samples, costs and obligations.

Hashes establish byte custody. Certificates carry `authority_effect="None"`;
the host separately authorizes only synthetic local laboratory actions. A
successfully replayed negative or deferred receipt remains negative or deferred.
The compact oracle checks arithmetic and declared admission facts; full event
hash, parent and restart integrity is the responsibility of the separate replay
verifier and adversarial tests.

See `SOURCE_MAP.md` for the exact upstream commit, reused symbols, dependency
findings and claim-to-code map; `protocol.json` for the frozen hypotheses and
scoring definitions; and the accompanying report for executed outcomes and
remaining limitations.
