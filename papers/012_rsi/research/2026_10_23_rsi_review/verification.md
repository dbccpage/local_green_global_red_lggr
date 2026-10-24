# RSI independent-review remediation and release

Version **1.2.3**, verified 2026-10-23. All fourteen supplied findings have a
[current response](../../000_relational_reasoning_and_rsi_impossibility/docs/review_response_2026_10_23.md).
Eight supplied negative controls reproduced their described behavior before
repair. The earlier claim that the shipped cochain solver had been repaired was
not supported by that fresh baseline. The actual deposited implementation now
reconstructs and independently checks exact rational certificates.

| Verification layer | Result |
|---|---|
| Source pytest suite | 221 passed; 17 new review regressions |
| Fresh extracted pytest suite | 221 passed, including fresh Lean compilation |
| Named Lean census, source and extracted | 118 theorems; 90 axiom-free; only standard foundations |
| Full Lean census, source and extracted | 609 declarations across eight local modules |
| New formal results | Five finite-prefix/charge theorems and four reviewer scope controls |
| Installed wheel from extraction | PASS: 15 module/resource imports, exact annulus optimum 9, native metadata parity and full CLI |
| Native policy boundary | Eight adversarial/control identity records agree across Python/Rust |
| Active repair | Independent certificate replay and positive integer price; negative-price refusal also tested under Python -O |
| Canonical PDF rebuild | Seven pages, zero missing glyphs/overfull boxes; pages 1, 4 and 6 visually inspected |
| Manifests and deterministic ZIP | Two-way membership/hash checks and canonical byte equality pass |

The pytest total counts collected executions, including legacy aggregate
reexports. Original theorem code in `RelationalRsiNoGo.lean` and
`RsiImpossible.lean` is unchanged apart from comments; comparison with the
preserved previous archive confirms this. No new custom axioms or unfinished
proofs were introduced. The cold extraction started without a Lean build cache.

[Standalone package](../../000_relational_reasoning_and_rsi_impossibility/000_relational_reasoning_and_rsi_impossibility_2026-10-23.zip)
contains the manuscript/PDF, proofs/censuses, tests, native source/resources and
isolated wheel verifier. SHA-256:
`74855c151bcf8ee873fa30aa49de62fbcb5a93d7c1c8d5dcffa8f093a7a58b9f` (754,871 bytes).

[Machine-readable receipt](verification.json) binds the archive, PDF, original
review inputs, previous archive, source/wheel payloads and individual command
logs. [Supplied packet](supplied_packet/REVIEW_README.txt) and
[baseline replay](baseline_review.txt) are preserved unchanged. Failed initial
Lean and local-setuptools attempts remain in the verification logs alongside the
successful retries. The complete reviewer provenance is a supplied claim; the
fresh working-tree and release hashes here are independently computed.

The standalone prerequisites are Python 3.12 for this replay, NumPy/SciPy,
pytest, rustc, Lean 4.35.0 and the declared rendering inspection tools. The
isolated wheel test installed NumPy 2.5.4 and
SciPy 1.18.1 into a fresh venv with no system site
packages or checkout PYTHONPATH. Wheel payload bytes match the final source.

Native EIS results now explicitly say **metadata only**. They do not certify an
obstruction predicate, authenticate a host or establish statistical independence.
The asynchronous shift remains an explicitly controlled synthetic defect model.
The current run adds no live-provider or broad native-host experiment and no
universal implementation-refinement proof. Paper 001 remains unchanged at
version 1.8.2. No commit, push, DOI or public deposit was made.
