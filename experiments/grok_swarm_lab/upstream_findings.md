# Reproduced upstream findings

The dependency remains pinned to
`6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85`. Run the offline reproductions from
the laboratory directory:

```console
python evidence/upstream/reproduce_upstream.py
```

The command verifies all vendored SHA-256 values before importing them. The
saved [regressions.json](evidence/upstream/regressions.json) is the measured
output, with full receipts. No network request or real API key was used. The
retry client receives a dummy key directly and `urlopen` and sleeping are
mocked.

| Review observation | Reproduced result | Lab treatment |
|---|---|---|
| `StreamingAuditMonitor.merge` loses downstream negative sample and costs | Source receipt `OBSTRUCTION_DETECTED`; merged receipt `COMPOSITION_VERIFIED`; running cost 3 instead of unique-attempt total 10 | Bypass merge. Union original evidence with its query, scope and baseline; retain negative samples without claiming they answer a changed proposition; deduplicate attempt IDs exactly once. |
| Endpoint trajectory 0→2→1 emits transient alert despite valid terminal endpoint | First endpoint step `ALERT/ENDPOINT_BUDGET_EXCEEDED`; final summary and batch `COMPOSITION_VERIFIED`; stream CLI exits 1 and calls stream obstructed | Treat intermediate endpoint observations as provisional. Only terminal endpoint bound decides that query. Every-prefix breach blocks future tool actions. |
| Upstream conventional comparator omits relevant checks | Three disagreements on prefix excursion, representation change and retained obligation; all three faults localized online | Full contract checker B is implemented separately with the same evidence and capabilities as C. No accuracy claim is inferred from the upstream comparator's terminology. |
| Retry loop checks cap only before the loop | Cap 2, repeated mocked HTTP503: three issued mock attempts, counter 3, two mocked sleeps | Shared host permit reservation occurs at the issue point. Retries, branch actions, probes and repair operations consume the declared shared allowance. No OpenRouter runtime is used by the offline lab. |

The four reproduction predicates are all true. Reproducing a bug is not a
passing application-correctness result. The vendored functions retain their
original behavior.

The original root runtime suite, including the original test source at the
reviewed pin and excluding only metadata-dependent `test_e2e_suite.py`, ran
**179 tests: 177 passed, 2 failed, 0 errors, 0 skips**. The failures are:

- `TestStreamingAuditMonitor.test_every_prefix_vs_endpoint_scope`: expects
  first endpoint step `OK`, actual `ALERT`.
- `TestStreamingBaselineComparator.test_comparative_evaluation_across_excursions_migrations_and_obligations`:
  expects two localized faults, actual three (the retained obligation now also
  raises an online alert).

No expectations were changed. [pinned-root-tests.json](evidence/upstream/pinned-root-tests.json)
contains source hashes and result IDs; [pinned-root-tests.txt](evidence/upstream/pinned-root-tests.txt)
contains the full original output. Tests/library were loaded from pinned bytes
with resource paths resolving in the complete checkout. CLI subprocesses use
the complete checkout's root package. The selected runtime class ASTs and
unchanged CLI/core blobs were separately compared; the supplemental additions
are unused by those tests. This is not a claim to have checked out and rebuilt
the entire historical repository at the pin.

The **separate Volume VIII companion passed 15/15 tests**, with no errors or
skips. These tests inspect/replay historical stored receipts. They do not
re-execute live models or prove independence of the original prompt roles.
[companion.txt](evidence/upstream/companion.txt) preserves the run. The root
CLI selftest (six internal groups), demo, and cookbook 04 also completed with
exit 0; their outputs are separate evidence files, not substitutes for tests.

A supplementary full current-checkout run executed **386 tests: 382 passed,
4 failed**. The failures were the empty audit-stream success expectation, the
nested streaming test's endpoint expectation, the optional wiki Git check
(exit 128), and the root endpoint expectation. The checkout changed
concurrently during this run, so this is an honestly retained diagnostic run,
**not exact-head acceptance evidence**. It was not used to certify the pinned
dependency. See [current-root-all.txt](evidence/upstream/current-root-all.txt).
No incomplete checkout or missing historical source failure is attributed to
the lab's implementation.

Both **root and paper-local Lean source sets compiled separately** with
installed Lean 4.35.0, commit
`eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, including their original
`CheckAxioms.lean` files. These are byte-exact pinned source exports under
`evidence/upstream/lean/`. The logs list the usual `propext`, `Classical.choice`
and `Quot.sound` dependencies where applicable. No extra theorem was added,
no Mathlib download occurred, and no general agent-correctness claim follows.

Additional source limitations retained in our interpretation:

- The historical empirical benchmark records eight tasks and 16 completions,
  all local and global verdicts true. Coding receives the original task text;
  it does not consume the generated specification. It measures no failures
  caused by that handoff.
- The sorting collision demonstration assigns its target outcomes explicitly.
  The enriched-schema demonstration supplies `{"valid":1}` twice and records
  zero defect directly. They demonstrate finite monitor behavior, not
  independently executed sorting success or naturally occurring model errors.
- Root and paper-local C10 Lean declarations use different edge orientations;
  the manuscript's description mixes the forward cycle with chord notation.
  The lab makes no cochain claim about the ledger and does not import the
  simplified companion implementation.
- `boundary_sufficient_gluing_certifies_lggg` assumes `eg = (e1 && e2)`.
  `minimal_metadata_refinement_eliminates_collision` proves pair separation
  when metadata differs, not existence of a deployable minimal schema.
- The root streaming fiber receipt uses schema label `lggr.descent.v1` but a
  different field structure from `descent.analyze_descent`; it is not
  interchangeable with that function's replay certificate. The lab uses the
  batch certificate and verifier together.

The complete-checkout helper commands are optional for source archaeology:

```console
python evidence/upstream/verify_upstream.py --suite pinned-root
python evidence/upstream/verify_upstream.py --suite companion
python evidence/upstream/verify_upstream.py --suite current-root-all
python evidence/upstream/verify_lean.py
```

The first and third commands preserve nonzero exits when original tests fail.
The application demo, benchmark, tests and replay need only the bundled
dependency and Python; they do not require Git, Lean, network access or API
credentials.
