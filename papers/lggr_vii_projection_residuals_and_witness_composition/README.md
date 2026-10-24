# LGGR VII: Positive-Extension Projection Residuals, Observer-Fiber Minimax Floors, and Witnessed Composition

**AuthorityEffect: None.**

Volume VII of the *Local Green, Global Red* series synthesizes finite report-fiber descent, signed witness composition, exact $\ell^1$ cochain repair and retraction reflection, observer-fiber scalar minimax error floors under evidence-preserving recursion, and positive-extension / contextual-fraction projection residuals.

## Contents

- [`lggr_vii_projection_residuals_and_witness_composition.md`](lggr_vii_projection_residuals_and_witness_composition.md) — Main manuscript.
- [`lggr_vii_projection_residuals_and_witness_composition_claim_ledger.md`](lggr_vii_projection_residuals_and_witness_composition_claim_ledger.md) — Typed claim ledger (`C-01` through `C-14`).
- [`lggr_vii_projection_residuals_and_witness_composition_change_log.md`](lggr_vii_projection_residuals_and_witness_composition_change_log.md) — Release change log.
- [`code/lggr_vii_core.py`](code/lggr_vii_core.py) & [`code/tests/test_lggr_vii_core.py`](code/tests/test_lggr_vii_core.py) — Exact rational Python derivations and unit tests.
- [`lean4/LggrVII.lean`](lean4/LggrVII.lean) & [`lean4/CheckAxioms.lean`](lean4/CheckAxioms.lean) — Lean 4 (`v4.35.0`) formalization and axiom audit.

## Reproduction

```console
python -m unittest discover -s code/tests -v
cd lean4 && lake build
```
