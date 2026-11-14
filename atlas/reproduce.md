# Reproducing the archived papers

**AuthorityEffect: None.**

The paper packages moved from `papers/` to `atlas/archive/papers/` on 2026-11-14. Their READMEs and
manuscripts are kept byte for byte as historical records, so some still give commands that start with
`papers/`. Use the current paths below instead. Run every command from the repository root.

## Rule

Wherever an archived file writes `papers/<package>/...`, use `atlas/archive/papers/<package>/...`.
Commands that a package README gives relative to its own folder (`cd` into the package first) work
unchanged once you `cd atlas/archive/papers/<package>`.

## Commands that name the old root path

| Package | Archived command | Current command |
|---|---|---|
| LGGR VII | `python -m unittest discover -s papers/lggr_vii_projection_residuals_and_witness_composition/code/tests` | `python -m unittest discover -s atlas/archive/papers/lggr_vii_projection_residuals_and_witness_composition/code/tests` |
| LGGR VIII | `python -m unittest papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/code/tests/test_lggr_viii_core.py` | `python -m unittest atlas/archive/papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/code/tests/test_lggr_viii_core.py` |
| LGGR VIII | `cd papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/lean4 && lake build` | `cd atlas/archive/papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/lean4 && lake build` |

All three current commands were run on 2026-11-14 and pass (Python 3.13, Lean 4.35.0).

These are the only commands in the archived Markdown files that name the old root `papers/` path.
They appear in `README.md` and the manuscript of each package.

## Not covered

The archived Python is historical. It is not on the derivation path, which uses only `code/rust` and
`lean4/` (see [`atlas.md`](atlas.md)). The repository-level `atlas/archive/papers/run_cross_deposit_verification.py`
already failed before the move (recorded 2026-10-26) and is not repaired here.
