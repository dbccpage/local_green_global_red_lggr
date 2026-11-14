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
