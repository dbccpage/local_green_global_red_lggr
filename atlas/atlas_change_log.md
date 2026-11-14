# Atlas change log

**AuthorityEffect: None.**

## 2026-11-14: consolidation

- Moved `papers/` to `atlas/archive/papers/` and `source/` to `atlas/archive/source/` with `git mv`
  (history kept). The originals are gone.
- Renamed `experiments/` to `workflows/`. Python imports, test paths, `MANIFEST.sha256`,
  `.gitattributes`, docs and the in-repo `wiki/` copy now use the new paths.
- Replay verifiers (`concurrent_five_agent_swarm/verify.py`, `live_five_agent_swarm/tools/verify_run.py`,
  `lggr_rsi_swarm/verify.py`) import the package name recorded in each run's source snapshot. Runs
  recorded before the rename replay as `experiments.*`, and later runs as `workflows.*`.
- Left unchanged on purpose: the frozen `PROTOCOL.md` files, recorded evidence (`evidence/`, `*.jsonl`,
  `RESULTS*.json`), `receipts/`, and the sealed `workflows/grok_swarm_lab/` distribution. Paths inside
  them are historical records.
- `MANIFEST.sha256`: paths renamed. A hash was refreshed only where the old entry matched the old file
  and this change edited that file (11 entries). Entries that were already stale stay stale.
- Added `atlas/reproduce.md`: current commands for archived READMEs that still name `papers/` (review
  finding 5). The archive itself is not rewritten.
- Created `atlas/`, `dag/` and `code/rust/`, matching the Omega Codex layout. `lean4/` already existed
  and is unchanged.

## 2026-11-14: first-pass claim ledger and derivation DAG

- Added `dag/derivations/derivation_dag.json` and `atlas/atlas_claim_ledger.md`: 170 nodes
  (36 core claims, 7 empirical workflow results, 5 open items, 122 further Lean theorems recorded one
  per node, and one support-module node for `PrimitiveDifference.lean`). Counts: 148 `PROVED_LEAN`,
  10 `TESTED_RUST`, 7 `EMPIRICAL`, 5 `OPEN`.
- Sources for this pass: `examples/`, `cookbooks/`, `code/`, `lean4/`, `workflows/`. Nothing was
  extracted from `atlas/archive/papers/` yet.
- Added the Rust crate `code/rust` (`lggr_derivations`). It re-derives all 13 examples and the 11
  matching receipts, the cookbook instances and three recorded workflow event chains, and checks that
  the DAG and ledger agree.
- Replayed `lake build` in `lean4/` with Lean 4.35.0: success, zero `sorry`. `#print axioms` on all 160
  theorems in `LggrVII`, `LggrVIII` and `WorldLGGRWitness`: 47 depend on `Classical.choice`, recorded per
  module in `lean_inventory` (open item LGGR-O03).
- No status was raised beyond its replayed evidence. Where Lean proves only an instance, or only the
  arithmetic step, the claim's `scope` says so.
- Observation, not changed here: `wiki/Home.md` counts 65 theorems in `LggrVIII.lean`; the file has 142.

## 2026-11-14: fixes from the joint review of #156/#157

- `code/rust/src/linear.rs`: `matvec`, `matmul`, `sub`, `solve_exact` and `classify_cochain` now check
  every shape and return an error instead of truncating with `zip`. `classify_cochain` requires
  `len(h) = rows(D0)` and `cols(D1) = rows(D0)`. Added exact `rank`.
- `code/rust/src/transport.rs`: all six shapes are checked before any product; ill-typed input is
  `InvalidTransport`. `zero_map_admits_left_inverse` is replaced by `admits_left_inverse`
  (rank = column count), which rejects nonzero non-injective maps such as `[[1, 0]]`.
- `code/rust/tests/boundary.rs`: the reviewer's fixtures as regressions.
- LGGR-C21 rescoped to what the Lean theorem proves (lower bound; attainment only when a + b = 2m).
  New LGGR-C37 (`TESTED_RUST`): the integer two-point optimum is ceil((b - a)/2). LGGR-C22 now says the
  midpoint attainment is over rational predictors.
- DAG: new `claim_correspondence` field separates proof existence from claim correspondence
  (`AUTHOR_MATCHED` for core claims, `DOCSTRING_ONLY` for the Lean inventory; none `REVIEWED` yet).
- CI: `.github/workflows/derivations.yml` runs `cargo test`, `lake build`, the Lean axiom census
  (`lean_census`, which fails if any cited theorem gains or loses `Classical.choice` or uses another
  axiom such as `sorryAx`) and the Python app tests.
- Counts: 171 nodes; 148 `PROVED_LEAN`, 11 `TESTED_RUST`, 7 `EMPIRICAL`, 5 `OPEN`.
