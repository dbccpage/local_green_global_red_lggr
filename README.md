# LGGR Witness Audit

**AuthorityEffect: None.** Working Python reference implementation of the finite mechanisms in the supplied report, *Local Green, Global Red: cumulative drift under protected local evaluation*.

This is a standalone, tested adapter. It does **not** modify the Omega Engine or finite-QM repositories, execute a hosted model, authenticate an owner, or authorize a merge. The source report supplies the mathematics; this package implements scoped checks on explicit finite data.

## Run without installing anything

Python **3.10 or newer**; standard-library runtime only. Tested here with Python 3.13.5 on Linux; other platforms/interpreters were not executed here. No API calls, tokens, Git checkout, NumPy, Lean, solver, or GPU are required.

Unzip the source archive, enter its directory, then run:

```console
python -m lggr demo
python -m unittest discover -s tests -v
```

A separately supplied single-file archive can run directly:

```console
python lggr_witness_audit.pyz demo
python lggr_witness_audit.pyz --help
```

The `.pyz` contains the same library code, not a native executable or model. The source ZIP also includes JSON examples, tests, documentation and execution receipts.

Optional installation from the extracted directory:

```console
python -m pip install --no-build-isolation .
lggr-audit demo
```

Installation requires a compatible local setuptools installation. It is unnecessary for either run method above; there are no third-party runtime dependencies.

## What is implemented

| Mechanism | Executable behavior | Boundary |
|---|---|---|
| Decoder-or-collision | Groups finite observations by report, constructs a decoder on the realized image or exhibits a colliding pair, and replays either certificate. | A decoder is certified only on the supplied table. A collision proves report insufficiency, not which history occurred. |
| Witness composition | Checks endpoint identity, signed differences, local verdicts, smoke observations, baseline, policy manifest, evaluator/spec/representation/authority identity, and open obligations. | Its global query is the declared integer budget requirement, not arbitrary software semantics. |
| Evaluator defect | Computes `Eg - E1*E2` and labels NGD/ZDR/PGD. | Requires an independently supplied global verdict. It does not manufacture one from local passes. |
| Exact L1 certificate | Checks `D.T z = 0`, `abs(z) <= w`, the primal residual and equality of bounds. | Verifies supplied rational certificates; does not optimize an arbitrary repair problem for you. |
| Cochain classification | Exact rational elimination separates repairability, closure failure and closed/nonexact classes. | A degree-two differential must be supplied before any H1 classification. |
| Witness transport | Checks commuting squares and optional chain retractions. | Forward commutation preserves repairs; it does not alone preserve nonrepairability. |
| Retained obligations | Unions unresolved obligations across every supplied witness and prior obligation list. | The host must retain the original history/ledger. This package cannot prevent deletion outside its process. |

The added schema/version checks, exact finite elimination, JSON CLI and optional every-prefix query are **implementation extensions**, not claims that these exact Python APIs or statuses already exist as native OE/QM contracts.

## Reproduce the report

```console
python -m lggr audit examples/bad_history.json
python -m lggr audit examples/good_history.json
python -m lggr audit examples/reports_only.json
python -m lggr descent examples/report_collision.json
python -m lggr descent examples/refined_reports.json
python -m lggr linear examples/triangle_l1.json
python -m lggr cochain examples/triangle_filled.json
python -m lggr cochain examples/triangle_unfilled.json
python -m lggr cochain examples/budget_exact_cochain.json
python -m lggr transport examples/faithful_transport.json
python -m lggr transport examples/lossy_transport.json
```

Some commands intentionally return exit **1**: they found a counterexample or did not establish the requested claim. That is expected, not a crash.

### Expected results

| Input | Result |
|---|---|
| `0 -> 1 -> 2` | Both local gates pass; `OBSTRUCTION_DETECTED` because cumulative change is 2 and the bound is 1. |
| `0 -> 1 -> 0` | `COMPOSITION_VERIFIED` for the declared cumulative requirement. |
| Same local reports, endpoints unavailable | `WITNESS_INCOMPLETE`; no realized global failure is inferred. |
| Restricted reports for both histories | `REPORT_INSUFFICIENT`, with an explicit equal-report/different-query pair. |
| Signed-increment refinement | `DECODER_VERIFIED` on the supplied finite carrier. |
| A changed owner/evaluator/specification or policy manifest | `AUTHORITY_REQUIRED`; no self-approval fallback. |
| An untranslated representation | `UNSUPPORTED`; no automatic reinterpretation of its values. |
| An unresolved earlier obligation | `WITNESS_INCOMPLETE`, even if the endpoint budget holds. |
| Triangle `h=(1,1,1)`, `z=(1,1,-1)` | `OPTIMALITY_VERIFIED`, with exact `Phi=1`. |
| Same triangle, filled by a face | `CLOSURE_FAILURE`, **not** an H1 class. |
| Same triangle, no degree-two cells | `CLOSED_NONEXACT`. |
| Budget differences `h=(1,1,2)` | `EXACT`; the drift example is not a cohomological obstruction. |
| Edge-permutation chain retraction | `RETRACTION_VERIFIED`; repair reflection is certified. |
| Zero/lossy map | Forward commutation holds, but reflection is not certified. |

A fixed-baseline arithmetic check detects the same budget failure. **No greater detection power than that baseline is claimed.** The extra artifacts expose the scope, report loss, transport assumptions and unresolved obligations.

## Python API

### 1. Compose witnessed transitions

```python
from lggr import BudgetPolicy, StateRef, audit_history, make_witness

policy = BudgetPolicy()
s0 = StateRef("commit-0", 0)
s1 = StateRef("commit-1", 1)
s2 = StateRef("commit-2", 2)

w01 = make_witness(policy, s0, s1, witness_id="review-01")
w12 = make_witness(policy, s1, s2, witness_id="review-12")
receipt = audit_history(policy, s0, [w01, w12])

print(receipt["status"])                         # OBSTRUCTION_DETECTED
print(receipt["arithmetic"]["signed_total"])     # 2
print(receipt["arithmetic"]["global_verdict"])   # False
print(receipt["authority_effect"])               # None (the string)
```

`make_witness` evaluates the supplied finite model. It does not turn arbitrary code, an LLM's approval, or a commit hash into behavioral evidence.

`policy.sha256` binds the actual policy contents, not just its name. Each witness records this manifest digest and the evaluator, specification, representation and authority identities. These are **supplied identities**, not authentication or a guarantee that a hosted provider has remained unchanged.

The audit recomputes local verdicts instead of trusting the recorded flags. It rejects disconnected boundaries and conflicting observations for one state identity. All findings remain in the receipt even when a more conservative primary status takes precedence.

### Endpoint scope versus every-prefix scope

The source report's query is `abs(final - baseline) <= bound`. That is the default `query_scope="endpoint"`.

Under this query, `0 -> 1 -> 2 -> 1` has a valid final endpoint despite an earlier violation. The receipt exposes both the endpoint and every-prefix answers; it does not pretend they are the same proposition.

For a requirement that must hold after **every** accepted update, explicitly use:

```python
policy = BudgetPolicy(query_scope="every_prefix")
```

That policy rejects the excursion even after a return within bounds. Its different manifest must not be silently substituted into existing witnesses. Retain earlier decisions and obligations in protected storage.

### 2. Audit whether reports retain enough information

```python
from lggr import analyze_descent, verify_descent_certificate

rows = [
    {"state_id": "0,1,0", "report": [[1, True, True], [1, True, True]], "query": True},
    {"state_id": "0,1,2", "report": [[1, True, True], [1, True, True]], "query": False},
]
certificate = analyze_descent(rows, scope_id="two-explicit-budget-histories")
print(certificate["status"])  # REPORT_INSUFFICIENT
print(verify_descent_certificate(rows, certificate))  # True
```

To certify a finite carrier exhaustively, **you must supply the full declared carrier**. Passing a sample does not establish adequacy on unseen histories. A collision within a sample nevertheless refutes sufficiency for any larger declared carrier containing that pair under the same report and query maps.

Reports and query values use canonical JSON equality. In particular, JSON `true`, integer `1`, and string `"1"` remain distinct. Object key order is irrelevant. Repeated state IDs, unknown schema fields and floats are rejected.

`decode(certificate, report)` is a lookup convenience for a previously verified certificate. It raises `KeyError` outside the certified realized image; it never extrapolates. Replay an untrusted certificate against its source table before using it.

### 3. Verify a genuine nonrepairability certificate

```python
from lggr import verify_l1_certificate

receipt = verify_l1_certificate(
    D=[[-1, 1, 0], [0, -1, 1], [-1, 0, 1]],
    h=[1, 1, 1],
    weights=[1, 1, 1],
    potential=[0, 1, 2],
    dual=[1, 1, -1],
)
print(receipt["status"])             # OPTIMALITY_VERIFIED
print(receipt["optimum"])            # "1", an exact rational string
print(receipt["repair_impossible"])  # True
```

Acceptable coefficients are integers, rational strings such as `"1/3"`, or Python `Fraction` objects. No tolerance or approximate equality is used. The routines support nonempty finite rational repair matrices with positive weights. `classify_cochain(..., D1=[])` explicitly declares a zero-dimensional degree-two space; omitting `D1` makes no cohomology claim.

### 4. Check transport before reusing an obstruction

`verify_transport` accepts `D_source`, `D_target`, `F0`, `F1`, and optionally `G0`, `G1`.

It checks:

```text
F1 D_source = D_target F0          forward repair transport
G1 D_target = D_source G0          backward repair transport
G0 F0 = identity on source C0     left inverse
G1 F1 = identity on source C1     left inverse
```

The full verified chain retraction is a sufficient repair-reflection certificate. Failure to provide one does not prove that every conceivable reflection method fails. It means this checker has not certified reflection by this route.

This finite rational check is **not automatically connected to runtime representation migration** in the budget adapter. That connection needs an independently admitted interpretation of the maps and states. The adapter refuses unprovided transport instead of assuming it.

## Replay, receipts and exit codes

```console
python -m lggr audit examples/bad_history.json --output receipts/bad.json
python -m lggr replay examples/bad_history.json receipts/bad.json

python -m lggr descent examples/report_collision.json --output receipts/collision.json
python -m lggr replay examples/report_collision.json receipts/collision.json
```

A negative receipt can replay successfully. **Exit 0 from `replay` means the certificate was verified, not that its negative finding became an admission.** The full audit input is recomputed; a receipt hash alone is not accepted as proof.

| Command | Exit 0 means |
|---|---|
| `demo` | The demonstration and exhaustive finite census completed. Expected counterexamples are included. |
| `audit` | `COMPOSITION_VERIFIED` for the declared query and supplied evidence. No merge grant. |
| `descent` | A decoder exists on the supplied finite table. |
| `linear` | A supplied lower-bound or matching-optimum certificate verified; inspect `status`. |
| `cochain` | An exact repair exists in the supplied rational model. |
| `transport` | Forward transport verified, and reflection too when `require_reflection` is true. |
| `replay` | The receipt's mathematical check replays against the supplied input, including valid negative findings. |

Exit **1** means a negative or uncertified result. Exit **2** means malformed input, unsupported CLI usage, or an input/output error. JSON errors go to stderr. Unexpected internal implementation errors are not converted into successful results.

`--output` writes a JSON receipt. Input `-` reads JSON from stdin. Verification does not depend on Python `assert`, so `python -O` does not remove the checks.

## Host integration boundary

A host should read the policy, baseline and retained obligations from protected accepted state; obtain candidate evidence from a separate execution/replay mechanism; then call this checker. Do not read the governing policy from a worker-controlled branch and assume its digest makes it trustworthy.

For the audit command, only exit 0 is a candidate **certificate success**. The owner's external admission rule still decides whether any change may merge. Do not treat successful CLI execution, a verified collision, a positive L1 obstruction, or successful receipt replay as permission to merge.

The current package deliberately has no `approve=True`, owner-signature bypass, mutable reviewer, obligation-clearing endpoint, GitHub write action, or autonomous gate-installation feature. It is a verification library and experiment, not a production security boundary. Untrusted JSON still requires normal host resource limits and sandboxing.

## Validation and source custody

`receipts/tests.txt` records the actual unit-test run. `receipts/validation.json` records execution details and limitations. The tests include the 216 finite report/query combinations, all eight Boolean verdict triples, all 363 histories of length one through five over the three-state domain, independent certificate replay, tampering and scope-change cases, exact arithmetic, and CLI exit behavior.

`SOURCE_NOTES.md` separates the uploaded report from this new implementation. `source/research_response.txt` preserves the supplied input. `provenance.json` records its SHA-256 and the repository pins **reported by that input**. Those repositories and Lean proofs were not independently fetched or rerun for this implementation.

The produced status names are adapter vocabulary. NGD/ZDR/PGD reproduce the report's mathematical sign convention; the original `epk_core.py` was not imported. There is no claim of native integration, universal self-modification safety, quantum advantage, or stronger detection than a complete fixed-invariant checker.
