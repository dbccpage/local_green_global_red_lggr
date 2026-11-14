# LGGR Atlas

**AuthorityEffect: None.**

The atlas is the single index of what this repository claims, how each claim is derived, and how strongly
it is checked. It follows the `atlas/`, `dag/`, `lean4/` and `code/rust/` layout used in the Omega Codex
repository.

## Layout

| Path | Role |
|---|---|
| [`atlas/atlas.md`](atlas.md) | This index. |
| [`atlas/atlas_claim_ledger.md`](atlas_claim_ledger.md) | Human-readable claim ledger: one row per claim, with status and evidence. |
| [`atlas/atlas_change_log.md`](atlas_change_log.md) | Dated record of structural and ledger changes. |
| [`atlas/archive/papers/`](archive/papers/README.md) | The research papers (LGGR I–VIII and companions), moved from `papers/`. Read-only source material. |
| [`atlas/reproduce.md`](reproduce.md) | Current commands for archived papers whose READMEs still name the old `papers/` path. |
| [`atlas/archive/source/`](archive/source/) | The originally supplied report, moved from `source/`. |
| [`dag/derivations/derivation_dag.json`](../dag/derivations/derivation_dag.json) | Machine-readable derivation DAG: the same claims as the ledger, with dependency edges. |
| [`lean4/`](../lean4/README.md) | Lean 4 proofs (existing package, unchanged). |
| [`code/rust/`](../code/rust/README.md) | Rust derivation kernels and tests. The derivation path depends only on Rust and Lean. |
| [`workflows/`](../workflows/) | Live and offline swarm experiments, renamed from `experiments/`. Their measured results enter the ledger as empirical claims. |

## Claim statuses

Every claim carries exactly one status. A status is only raised when the stronger evidence exists and has
been replayed.

| Status | Meaning |
|---|---|
| `PROVED_LEAN` | A named Lean 4 theorem states the claim and the package builds with zero `sorry`. |
| `TESTED_RUST` | Checked by a Rust test on the stated finite instance; no general proof in this repository. |
| `EMPIRICAL` | Measured in a recorded workflow run, with the interval or count reported; not a theorem. |
| `PROSE_ONLY` | Stated in documentation only; no Lean theorem or Rust test yet. |
| `OPEN` | Stated as a goal or conjecture; neither proved nor tested. |

`PROVED_LEAN` records proof existence. Whether the theorem says exactly what the ledger row says is tracked
separately as `claim_correspondence` in the DAG (`AUTHOR_MATCHED`, `DOCSTRING_ONLY`, `REVIEWED`).
Each cited theorem's statement is pinned in `dag/derivations/lean_signatures.json`; CI fails if a statement
changes, so the correspondence must be re-reviewed before the pin is updated.

## Phases

1. **Done (this pass):** consolidate folders; first-pass claims from `examples/`, `cookbooks/`, `code/`,
   `lean4/` and `workflows/`, recorded in both the ledger and the DAG.
2. **Next:** extract every claim and derivation from `atlas/archive/papers/` into the ledger and DAG.
3. **Then:** complete each derivation in prose, Lean and Rust.

The `lggr/` Python package (the app) and `lggr_guard/` are not part of the derivation path and are left as they are.
