# Source and implementation boundary

## Requested basis

The user supplied *Local Green, Global Red: cumulative drift under protected local evaluation*, dated 23 October 2026. The preserved input is `source/research_response.txt`.

The input reports two pinned repositories:

- Omega Engine / `the_symbol_game`: `e7420ae75737df9dbb0785cc102e8179fa6feb8c`.
- `theory_of_finite_quantum_mechanics`: `5b22322289839eaa308c91b01500225aa31ddaba`.

These are **reported source identities**, not independently fetched or verified source snapshots in this implementation session. In particular, the input's claims of Lean checks and prior EPK execution are not presented as new checks performed here.

## Mapping from the report to this implementation

| Report location | Implemented component | Scope |
|---|---|---|
| A, decoder-or-collision criterion; E1/E2 | `lggr/descent.py` | Finite table algorithm and independent certificate replay. |
| B, three-state drift model | `lggr/witnesses.py`, `lggr/examples.py` | Exact endpoint arithmetic, bounded-step rule, smoke domain check and protected probes. |
| A/B, evaluator defect; E19 | `evaluator_defect` | Small independent reimplementation of `Eg - E1*E2`, not a native EPK import. |
| A/B, primal/dual repair certificate; E5 | `verify_l1_certificate` | Exact rational checking of a supplied annihilator, dual bound and matching primal. |
| A/B, distinction between closure and exactness | `classify_cochain` | Rational elimination; cohomology claims only after validating the declared complex. |
| A, repair transport and retraction; E6/E12 | `verify_transport` | Supplied rational commuting maps and left-inverse chain maps. |
| Smallest proposed extension and candidate certificate | Identity/version fields, policy hashes, obligations and JSON replay | New engineering implementation. Not an existing native contract or formally verified adapter. |

The original hardcoded Windows checkout, dynamic `git show`/`exec`, NumPy import and Python `assert`-based harness are not used. The portable implementation performs explicit runtime checks and uses only standard-library modules.

## Deliberate nonclaims

1. No arbitrary code-to-mathematics extraction, complete AI verifier, or automatic semantic witness generation.
2. No provider-drift detector or proof of real-world agent independence.
3. No new theorem identifying software drift with quantum contextuality.
4. No claim that the cumulative budget violation is nonzero cohomology.
5. No universal adequacy claim from a finite sample or finite census.
6. No stronger budget detector than ordinary fixed-baseline arithmetic.
7. No proof that a digest authenticates observations, protects files, or legitimizes a grantor.
8. No actual repository modifications, production deployments, fresh Lean build, or external service calls.

## Explicit implementation extensions

- Strict JSON schemas and duplicate-key rejection.
- Scope-bound policy manifests and typed finite state/witness objects.
- Separate diagnostic outcomes, with all simultaneous findings retained.
- Aggregation of unresolved obligations; no unverified clearing API.
- Optional `every_prefix` query, distinct from the source's default endpoint query.
- Reproducible JSON receipts, CLI exit semantics and tamper-replay tests.
- A standalone `.pyz` archive using the same implementation.

Every guarantee refers to the supplied finite model and artifacts. The host must supply and retain trustworthy observations, protected specifications and authority boundaries.
