# Local Green, Global Red — Lean 4 sources

This package ships three mathematical sources. `Census.lean` and `lakefile.lean` are infrastructure.

| Source | Role | Axiom reports |
| --- | --- | --- |
| `observer_visibility.lean` | Current manuscript observer results and explicit edge-level calculations in `ObserverVisibility`; also supplementary cycle, holonomy, redundancy, non-linear, and zero-repair norm-chain developments | 67 in the historical 2026-10-05 receipt |
| `po000_l004_observer_visibility.lean` | Byte-identical anchor v6.3 snapshot in `PO000.ObserverVisibility` | 14 in the historical packaging receipt |
| `minkowski_repair.lean` | Rational repair/minimizer identities for LGR-R2–R4 in `MinkowskiRepair`; squared Euclidean quantities | 19 standalone reports |

The current manuscript has Theorems 1–6, the Master Soundness Criterion, a prose finite-dimensional recovery proposition, and repair lemmas. Its §6 and the claim ledger give the current declaration map. Historical “Theorem 7”, “Theorem 7′”, and “Redundancy Corollary” labels refer to supplementary developments, not numbered results in this manuscript.

The rational repair source works over `Rat`. Its Euclidean identities concern squares. Written proofs establish real infima and square-root conclusions. The compactness recovery proposition has no Lean declaration here. The six-site graph realization is established in prose; the observer source formalizes the stated edge-level calculations. Supplementary non-linear bounds and norm-chain evaluations retain the narrower scopes documented in the claim ledger.

The two observer sources are Lake roots and use Mathlib pinned in `lake-manifest.json`. `python ../verify_deposit.py --lean` (from this directory) validates the compiler pin, builds them, and compares the 81 named reports with `axiom_report.txt` via the generated `Census.lean`. The standalone rational module is not a Lake root; the default verifier elaborates it separately and requires all 19 named reports.

All compilation uses `leanprover/lean4:v4.34.0-rc1`. A different compiler or absent local Lake dependencies must be reported as a failed replay, not replaced by a new pin. Historical receipts in `PROVENANCE.md` retain their dates and scope; they are not fresh release verification. The axiom whitelist is `propext`, `Classical.choice`, and `Quot.sound`. Source files and tooling are Apache 2.0 under `../LICENSE-CODE`.
