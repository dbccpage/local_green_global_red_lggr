# LGGR VIII: Online Streaming Discovery, Prefix Admissibility, and Runtime Gluing

**AuthorityEffect: None.**

Volume VIII of the *Local Green, Global Red* series addresses online, streaming LGGG (Local Green, Global Green) versus LGGR (Local Green, Global Red) discovery during multi-agent swarm execution. It formalizes report-fiber collision monotonicity, streaming prefix-by-prefix drift telescoping, online every-prefix versus endpoint admissibility separation, incremental 1-cochain cycle closure with exact rational $\ell^1$ dual witnesses, and boundary-sufficient runtime gluing certification.

This package unifies Lean 4.35.0 formalizations, reproducible exact rational Python monitors, live OpenRouter model benchmark receipts resolving Volume I §9 ($N = 8, \mathrm{LPR}=1, \mathrm{GPR}=1, \mathrm{NGD}=0, \mathrm{ZDR}=1, \mathrm{PGD}=0$), and deterministic offline replay verification for Tests 1–4.

## Contents

- [`lggr_viii_online_streaming_discovery_and_runtime_gluing.md`](lggr_viii_online_streaming_discovery_and_runtime_gluing.md) — Main manuscript.
- [`lggr_viii_online_streaming_discovery_and_runtime_gluing_claim_ledger.md`](lggr_viii_online_streaming_discovery_and_runtime_gluing_claim_ledger.md) — Typed claim ledger (`C-01` through `C-14`).
- [`CHANGELOG.md`](CHANGELOG.md) & [`lggr_viii_online_streaming_discovery_and_runtime_gluing_change_log.md`](lggr_viii_online_streaming_discovery_and_runtime_gluing_change_log.md) — Release change log.
- [`code/lggr_viii_core.py`](code/lggr_viii_core.py) & [`code/tests/test_lggr_viii_core.py`](code/tests/test_lggr_viii_core.py) — Standalone reproducible Python module and unit tests.
- [`lean4/LggrVIII.lean`](lean4/LggrVIII.lean) & [`lean4/CheckAxioms.lean`](lean4/CheckAxioms.lean) — Mirrored Lean 4 (`v4.35.0`) formalization and axiom audit.
- [`receipts/`](receipts/) — Live OpenRouter benchmark receipts and deterministic offline replay traces.

## Reproduction and Verification

```console
# 1. Run companion Python unit tests
python -m unittest papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/code/tests/test_lggr_viii_core.py -v

# 2. Build and audit mirrored Lean 4 package
cd papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/lean4 && lake build
```
