# Reproduction record — correction release 1.5.1, 2026-10-21

The supplied matching v1.5.0 source review produced 86 passing tests and four missing-file failures, compared five certificates with literal Lean constants, and explicitly performed no Lean build, full release audit, executable comparison replay or PDF review. Those statements describe its attachment subset. They remain preserved in `source_inputs/v1_5_review` and are not rewritten as successful release verification.

## Fresh local checks

This correction was checked with **Python 3.12.14**, **pytest 9.1.1** and the actual **Lean 4.33.1** executable. `verification_run_v151.json` records the commands, exit codes, stdout and runtime identities.

- **112 pytest executions passed**, with zero failures, errors or skips: the original 90 plus 22 uncertainty, mutation and release-file tests.
- **98 explicitly named theorems replayed**, with complete source coverage: 23 axiom-free and 75 with approved foundational axioms only.
- **660 package-local declarations across 11 modules replayed**, including private and generated declarations.
- **71 complete Lean/Python execution comparisons passed**, including every primal/dual coordinate, value, pivot count and refusal label. This finite agreement is not universal refinement.
- The five generated rational certificates remain numerically identical to v1.5.0 and are checked inside Lean against arbitrary real competitors.
- The review's three exact mathematical groups were replayed from preserved source copies. They read Lean constants as data and do not elaborate Lean. Its separate path/symlink results remain supplied review evidence.
- The new API example retains signalling observations with raw defect 1/50, known raw uncertainty radius 1/50 and guaranteed adjusted margin zero. Model inputs, radius, witness and resulting margin are checked independently of the solver's candidate generation.

All eleven proof-module files remain byte-for-byte identical to the preserved v1.5.0 archive. No new theorem or axiom is introduced. The named source audit was refreshed after the deliberate Python/API and build-version changes; both source and execution fixtures bind the updated implementation.

## Files and dependency custody

The four files absent from the review subset are included in the complete release: `docs/source_lineage.json`, `docs/solver_provenance.json`, `tools/generate_lp_certificates.py` and `tools/replay_lean_axiom_census.py`. The JSON execution fixtures, replay tool, driver, audit tools/reports, source hashes, manuscript builder and complete manifests are included as well.

An initial local 112-test attempt found that the working copy lacked `lean4/vendor/dependencies.tar.gz`, with 111 other tests passing. The original v1.5.0 ZIP contained it. Its exact 541,112,932 bytes were restored from that preserved archive and verified against vendor SHA-256 `af6fd2173a60c1a98a934ee678d94bad6a66837b436dcf0af8adc0b52183ce3d`. The full 112-test suite then passed. The initial result is retained in `initial_worktree_pytest_v151.xml` with its explanation in the execution record. This was a working-tree repair, not fabrication of replacement provenance.

The offline bundle pins Mathlib commit `0df444a360eaa60ab8c11dca51a86af692955474`, with 2,318 dependency modules and matching source, compiled artifacts and licenses. The standalone Lean gate checks the archive and every extracted source/artifact byte. It needs no ambient Mathlib checkout or monorepo import. Lean, Python, pytest and tar remain installed prerequisites.

All 36 review artifacts are preserved verbatim and source-bound. Review inputs and newly executed results are separate. `uncertain_observation_replay.json` contains the current exact example and mathematical review replay; `review_corrections_source_hashes.json` binds that record to the current source files.

## Document and final archive

The canonical rebuild checks every formula against the persistent equation registry, recompiles the PDF, checks ordered Markdown/TeX/UTF-8 formula structure, and rejects missing glyphs or overfull boxes. `render_receipt.json` contains actual artifact hashes and formula counts. The compiler's actual log and auxiliary outputs are preserved in sealed text copies under `render_build`; generated root compiler files are retained as well. A table-of-contents file is retained only when one is actually generated.

Both manifests and the deterministic ZIP are resealed and checked by the canonical rebuild. Final validation extracts that exact ZIP into an empty directory, confirms no Lean package cache is present, blocks monorepo imports, checks the actual compiler version, and runs `verify_deposit.py --lean`. It repeats the complete Python suite and checks refusal of changed proof sources, missing census entries, altered executable fixtures, modified uncertainty records and dependency bytes. Restored extracted files must match every archive member.

The final clean-replay receipt is stored outside the package and keyed to the release ZIP SHA-256, avoiding a self-referential archive digest. These are fresh local release checks; no independent external rebuild approval is inferred from the supplied review.

## Boundaries retained

The simplex is total for finite typed input and a finite shared pivot budget, and every successful checked return is feasible and globally optimal. Budget accounting is not elapsed-time, bit-complexity or operating-system resource accounting. Infeasible/unbounded labels do not yet carry mathematical certificates. Universal Python refinement and unbudgeted Bland completeness are not formalized.

The waiting-window theorem assumes a supplied continuous Duhamel enclosure and positive rate before division. A zero rate uses its constant enclosure directly. No propagator, validated quadrature, statistical coverage or physical model adequacy is proved by that scalar implication. The uncertain API's margin is conditional on the supplied observation radius; zero margin is not a true-model classification. Implemented memory transformation and enforced action-safety refinement remain open applications.
