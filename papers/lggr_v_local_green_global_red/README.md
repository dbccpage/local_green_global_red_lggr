# Local Green, Global Red

**Detection and Recovery in Finite Linear Evaluation Models** — Jeremy H. Carroll · v1.3.2 Pre-Print ·
**Date:** 2026-10-15 · **Version:** 1.3.2 · CC-BY-4.0

The note gives mathematical proofs of its stated results, with accompanying
Lean 4 declarations for the abstract observer statements and explicit defect
calculations. The six-site graph realization is established by the assignment
and calculation in §3. Exact Python replays check the resulting finite-instance
arithmetic. The declaration map specifies the extent of formalization for each
result. The finite-dimensional quantitative recovery result is proved in prose by compactness on the realizable defect space, with a separate zero-space branch; it is not Lean-mechanized.
Evaluators cannot create inconsistency; All-Green is exactly
defect-inside-every-blind-spot; false green can occur at any severity with
full coverage, so **no finite-valued function of evaluator scores bounds true
inconsistency**; per-interface joint-kernel triviality restores soundness
— sufficient, and provably **not** necessary (an explicit coupled system
shows why); and on the scalar variant of that coupled system an explicit defect
pattern is at exact distance 2 from every possible repair. Witness constants
have exact-arithmetic Python replays, pinned by tests.

Written without programme vocabulary, for readers who think about AI
oversight and composed evaluation.

## Contents

This deposit is the honest union of two parallel builds of the same paper
(see the change log): a self-contained Zenodo deposit (the note, the exact
replays, the verifier) and a full computational package (a typed
object-model harness with its own pytest suite, whose claims and declaration
maps are unified into this README, lggr_v_local_green_global_red_claim_ledger.md, and
manifest.json). Neither build saw the other; both are kept, with one canonical
manifest and pyproject. Manuscript completed 2026-09-09; Zenodo release package
assembled, audited, and verified 2026-09-10.

| Path | What it is |
| --- | --- |
| `lggr_v_local_green_global_red.md` | The paper (v1.3.2, manuscript dated 2026-10-15) |
| `lggr_v_local_green_global_red.tex` | The standalone LaTeX source for the paper |
| `lggr_v_local_green_global_red.pdf` | The rendered paper (compiled via pdfLaTeX without line overflows) |
| `lggr_v_local_green_global_red_claim_ledger.md` | Claim-by-claim evidence map (Lean + Python) |
| `lggr_v_local_green_global_red_change_log.md` | Version history, through v1.3.2 |
| `LICENSE` | CC BY 4.0 for manuscript, figures, and documentation |
| `LICENSE-CODE` | Apache 2.0 for source code, Lean files, notebooks, and release tooling |
| `code/lgr_replay.py`, `code/test_lgr_replay.py` | Exact-arithmetic replays and pinned tests (pure stdlib) |
| `code/code_*.py`, `code/test_*.py`, `code/run_tests.py` | The computational harness (numpy/scipy) and its pytest suite and 100% coverage gate |
| `jupyter_notebooks/` | Interactive Jupyter notebooks demonstrating the model, false-green scaling, and quotient geometry |
| `lean4/` | Three mathematical sources: current observer results plus supplementary developments in `observer_visibility.lean` (67 recorded reports); the byte-identical anchor snapshot (14 recorded reports); and mathlib-free `minkowski_repair.lean` (19 rational reports). `Census.lean` and `lakefile.lean` are infrastructure. Historical receipts are in `PROVENANCE.md`. |
| `manifest.json` | The one canonical machine-readable manifest (declarations + Lean file inventory) |
| `SHA256SUMS`, `verify_deposit.py` | Integrity manifest (covers every shipped file) and the one-command verifier |

`manifest.json` is the canonical release identity and publication description. `tools/sync_metadata.py` generates both `.zenodo.json` and `zenodo_metadata.json`, checks manuscript/README/Python identity and license parity, and writes `docs/descriptions.md`. Use `python tools/sync_metadata.py --check` to detect drift.

## Verify the package

    python verify_deposit.py

This checks every file against `SHA256SUMS` (both directions: nothing
listed may be missing or altered, nothing unlisted may be present), then
runs the exact replay test suite and elaborates `lean4/minkowski_repair.lean`
with the pinned Lean binary. That file is not a Lake root. Pure standard
library for the Python half, Python >= 3.10. Expected tail includes the
receipt values `r2-l1=2`, `r2-l2sq=2`, `r2-linf=1`, `r4-l1=3/2`,
`r4-l2sq=9/5`, `r4-linf=1`, then:

    Ran 18 tests ...
    OK
    OK: minkowski_repair.lean elaborated with no sorry.

To run the pieces separately:

    python -m unittest discover -s code -p "test_lgr_replay.py"   # the pinned tests
    python code/lgr_replay.py                   # prints the deterministic receipt:
                                                # I=6 J=[0, 0, 0] coverage=full
                                                # 6lam-checks=pass coupled=forced phi=2
                                                # r2-l1=2 r2-l2sq=2 r2-linf=1
                                                # r4-l1=3/2 r4-l2sq=9/5 r4-linf=1

The computational harness has its own suite (requires numpy, scipy,
pytest, pytest-cov — the `harness` extra in `pyproject.toml`):

    python code/run_tests.py                    # complete package harness; 100% coverage gate

## Recompiling the Lean proofs (optional)

The deposit includes a reproducible Lake project (`lean4/lakefile.lean`,
`lean4/lean-toolchain`, `lean4/lake-manifest.json`) pinned to
`leanprover/lean4:v4.34.0-rc1` with Mathlib. See `lean4/README.md` and
`lean4/PROVENANCE.md` for build commands, SHA-256 digests, and compile
receipts (both files exit 0; all `#print axioms` reports — 67 for
`observer_visibility.lean` (pinned `lake build` replay of 2026-10-05), 14 for the `po000_l004_observer_visibility.lean`
snapshot — within `{propext, Classical.choice, Quot.sound}`; no `sorry`).
`lean4/minkowski_repair.lean` is a separate mathlib-free file for LGR-R2,
LGR-R3, and LGR-R4. The default verifier elaborates it with the toolchain
`lean` binary. It is not a Lake root, and `python verify_deposit.py --lean`
additionally runs the Mathlib build and named census. Both routes reject a compiler whose reported version differs from `lean4/lean-toolchain`; neither installs a toolchain. Historical build receipts do not establish a fresh successful replay.

Named tests use the actual flat layout, for example:

    python verify_deposit.py --test code/test_core.py

The default verifier does not run the numerical harness, notebooks, or archive checker. For the final archive, run:

    python tools/sync_metadata.py --check
    python tools/rebuild_release.py --check

After intentional source/artifact changes, `python tools/sync_metadata.py` and `python tools/rebuild_release.py` regenerate metadata and the deterministic archive. Archive naming and member timestamps use the canonical publication date, so the same release can be rebuilt on a later day. A passing archive check establishes member and envelope identity, not mathematical validity or a Zenodo publication.

## Provenance in one line

This note extracts §7.4 of the anchor paper *Projection Obstruction for
Factorized States* (Zenodo concept DOI 10.5281/zenodo.18896776); the Lean
module is snapshotted here because the anchor's published record (v6.3)
predates it. Details: paper §7 and `lean4/PROVENANCE.md`.
