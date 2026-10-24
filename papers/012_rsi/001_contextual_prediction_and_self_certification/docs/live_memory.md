# Persistent memory in the agent request path

The current experiment connects `ResidualMemory` to the repository's
`LlmGateway.complete` before PFP prompt binding and provider dispatch. Configure
the facade with `memory=ResidualMemory(database, contract)` and `memory_keys`.
Use `facade.learn(candidate_rows)` to submit learning proposals. Every call
reopens the database and replays the checks. Existing callers without an explicit
memory configuration retain their prior behavior. This does not install a global
memory hook in the Codex desktop application or change model weights.

## Contract and residual

The contract binds task, model, allowed operations, exact key/value encoding,
append rule and a zero residual cap. For this categorical task, the residual is
one exactly when equal keys have unequal values, and zero otherwise. Thus it is
the discrete diameter of the recorded task fibers. Source hashes and exact
membership in the declared source JSON are checked separately. These checks
establish consistency and source custody, conditional on source adequacy.
They do not prove the source true, cover unseen worlds or certify action safety.

Both recall and prospective append validate the whole archive. Missing or changed
sources, changed contracts, unsupported facts, corrupted bytes and contradictory
values cause explicit refusals. Recall additionally requires every queried key,
the bound model and the context size limit. There is no silent truncation or
automatic database recreation. Facts are inserted as user data, never privileged
instructions; source paths stay local. Textual labeling is not a proof of
resistance to prompt injection.

SQLite serializes writes with `BEGIN IMMEDIATE` and commits with FULL synchronous
durability. A rejected candidate leaves the archive unchanged. An interrupted
uncommitted transaction was tested by terminating a separate process. The caller
must retain the database and its pinned sources across restarts. Checks bind the
source snapshot read during validation; they do not lock an external file against
later edits. The next operation rechecks it. Hashes detect accidental corruption,
not a malicious writer able to rewrite both records and digests. The archive is
bounded to 256 rows, sources to one MiB and inserted context to 16 KiB.

## Reproduction

The standalone package includes the identical stdlib memory implementation and
local CLI. A contract can be created with `exact_contract(task, model)` from
`code/residual_memory.py`. Sources are JSON objects containing a `facts` array of
objects with string `key` and `value` fields. From the package directory:

```text
python code/memory_cli.py memory.sqlite3 contract.json init
python code/memory_cli.py memory.sqlite3 contract.json learn source.json
python code/memory_cli.py memory.sqlite3 contract.json recall calibration
python code/memory_cli.py memory.sqlite3 contract.json prepare model "Use calibration" calibration
python -m pytest code/tests/test_residual_memory.py -q
python tools/replay_live_memory_evidence.py
```

The local CLI has no network path. The repository entry point
`python -m omega_engine_woland.entrypoints.synthetic_memory_experiment NEW_DIRECTORY`
performs the separately scoped live experiment through the existing accounted
OpenRouter gateway. Its outbound checker permits only reconstructed synthetic
calibration prompts. It uses at most four calls, 700 output tokens per call and
a 50,000 micro-USD estimated run allowance; this is not a vendor-enforced maximum
bill. Credentials are resolved by the existing provider adapter and never enter
the paper. The provider adapter snapshot is source evidence, not a standalone
copy of the monorepo provider stack. Offline tests require no credentials.

## Captured experiment and limits

On 23 October 2026 the exact-use trial used `openai/gpt-4o-mini` through OpenRouter
in four separate Python processes. The baseline returned `UNKNOWN`. The learning
process extracted the generated fact, and the update checker accepted it. Two
fresh processes then returned the exact learned value with `/ready` and `/checked`
suffixes. No conversational history was carried between these calls. The retained
database was the path by which the learned observation reached later prompts.

An earlier arithmetic trial is also retained: baseline and learning passed, but
the restarted model returned 10104857 instead of 10108497 for twice 5054245 plus
7, despite correct memory injection. This is a failed task-use result, not a
memory consistency failure. The later exact-use protocol was selected after this
failure and is not a preregistered statistical estimate. The initial transport
guard trial refused locally because its expected PFP envelope omitted the empty
context field; it produced no model response. All three trial records remain in
`docs/live_memory_trials`. Offline replay checks the captured raw replies, prompt
bindings, source pins and expected answers; it is not a fresh provider call or
independent provider attestation. No claim about long-term retention, model
comprehension, general intelligence or arbitrary tasks follows from these trials.

## Lean mapping

`LiveMemory.update_sound` proves consistency and source support of accepted
extensions. `update_retains` preserves old entries. `refused_update_preserves`
states the rejection branch leaves the old state. `recall_sound` supplies the
declared binding, source support and agreement of all recorded matches.
`changed_binding_refuses`, `missing_support_refuses` and `conflict_refused` cover
negative cases. `exact_reload_preserves_recall` explicitly assumes equality of
the reloaded rows. These eight statements are audited in both named and full
axiom censuses. The source predicate and binding check are abstract premises;
the proofs do not establish SHA-256 collision resistance, SQLite durability,
universal Python refinement or model obedience. Those implementation properties
have the executable evidence and limitations stated above.

The native budget host now builds offline from the repaired Rust sources. Both previously blocked gateway tests pass, and the full gateway-and-memory selection passes all 24 tests with no exclusions. The additional Rust library audit records 3687 passing, 3 failing, 13 ignored and 10 unfinished tests; five solver and five quantum integration binaries pass 89 tests. The three failures are floating-point quantum admission checks: the Choi identity example and two Hamiltonian propagator tests; they remain unresolved. Ten long-running MUB tests were stopped after about nine minutes and have no completed verdict in this run. The broad library audit also precedes concurrent edits in the shared checkout; the final host build and gateway rerun use the later checkout. These gateway checks use synthetic provider transports and the real native budget host. They do not add a new live model trial or establish universal implementation refinement.

See [native gateway verification](native_gateway_verification.md).
