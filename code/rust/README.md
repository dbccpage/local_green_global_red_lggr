# `code/rust`: LGGR derivation kernels

**AuthorityEffect: None.**

Exact integer and rational kernels that re-derive every `TESTED_RUST` claim in the
[claim ledger](../../atlas/atlas_claim_ledger.md) and check the
[derivation DAG](../../dag/derivations/derivation_dag.json). The derivation path depends only on
this crate and the Lean package in `lean4/`. It does not call or import the Python `lggr` app,
which stays as it is.

```console
cd code/rust
cargo test                       # 52 tests: claims, examples, receipts, event chains, boundary regressions, DAG integrity
cargo run --bin lggr_derive      # re-derive the verdict of every file in examples/
```

| Module | Re-derives (Python origin, not imported) |
|---|---|
| `descent` | decoder-or-collision, evaluator defect (`lggr/descent.py`) |
| `history` | telescoping, endpoint vs every-prefix, witness audit (`lggr/witnesses.py`) |
| `linear` | exact Gaussian elimination, weighted-l1 certificates, cochain classes (`lggr/linear.py`) |
| `transport` | commuting squares and chain retractions (`lggr/transport.py`) |
| `streaming` | online fiber, prefix and cycle-closure monitors (`lggr/streaming.py`, cookbooks 01–04) |
| `minimax` | observer-fiber floor |
| `bell` | CHSH, odd cycles, Mermin–Peres by exhaustive enumeration |
| `selectors` | host elimination rule (`code/operations/swarm/selectors.py`) |
| `chain`, `canon` | canonical JSON, SHA-256 and hash-chained event logs (`code/operations/swarm/hashing.py`) |

| Test file | Checks |
|---|---|
| `tests/derivations.rs` | one test per claim (`cNN_*`, cited by name in the DAG) |
| `tests/examples.rs` | all 13 `examples/`, 11 `receipts/`, cookbook instances, three recorded `workflows/` event chains |
| `tests/boundary.rs` | malformed or ill-typed input is rejected, never truncated into evidence |
| `tests/dag.rs` | DAG ids, edges, acyclicity, status evidence, cited Lean theorems and Rust tests exist, ledger agreement |

`cargo run --bin lean_census -- emit|check` runs the Lean axiom census used in CI (see `.github/workflows/derivations.yml`).

No floats, solver or tolerance. A passing test describes the supplied finite instances only.
