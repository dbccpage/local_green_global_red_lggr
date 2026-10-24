# Bell trace-norm and dynamical-witness release, 23 October 2026

Version **0.5.0** adds **28 named Lean theorems**, bringing the exhaustive census to **147**. The new modules prove finite Hermitian trace/operator bounds, POVM outcome-L1 contraction, weighted total variation and actual tensor Born-table comparison, local-repair and state-distance witnesses, and conditional dynamical CHSH bounds with uncertainty and finite-time exit rates.

A fresh source build and a second build from a clean ZIP extraction both passed under Lean 4.35.0. All theorem dependencies are among `propext`, `Quot.sound`, and `Classical.choice`; no custom axioms or admitted proofs occur. The unchanged pinned offline closure contains 2948 modules and 20672 individually hashed files.

Clean-extraction verification passed **26 tests**, the supplied **39/39 checks**, independent feasibility/objective verification of **8 repair and 7 negative-mass certificates**, 14 numerical LP solves, finite quantum/observer/Mermin checks, and direct notebook-cell replay. Before/after manifests confirm no packaged payload mutation. The source-bound PDF has **20 pages, zero overfull boxes**; pages 1, 8, 9, 17, 18 and 20 were visually reviewed.

The supplied notes and script are preserved unchanged. `docs/review_assimilation.md` records corrections to the dual-ball argument, tangent-cone support value, worked residual factor, invalid CHSH cross-term cancellation, minimax uniqueness and claimed improvement trichotomy. The independently checked returned certificates do not certify the supplied simplex implementation or its mathematical termination; subprocess timeouts enforce bounded replay.

Archive: `../036_bell_positive_extensions_and_projection_residuals/dist/bell_positive_extensions_v0.5.0.zip`  
Bytes: `707484561`  
SHA-256: `31dde3edb65ee9b56346aa505836dde9b03fa80493ef66cabd20aa97d012e45f`

The companion JSON and raw logs record exact commands, durations, all new theorem names, source/ZIP hashes, the clean extraction and PDF bindings. The final replay reused the dependency cache extracted from the identical bundled archive during the preliminary clean replay, and rechecked every dependency digest. All Bell sources were freshly compiled again. The only candidate difference was the completed review assessment; the JSON binds this comparison. Earlier release ZIPs and historical receipts are preserved. The disposable v0.4 and preliminary v0.5 extractions were removed to recover disk space after retaining receipts and relocating the verified dependency cache; they are not release artifacts.

The trace norm is the actual finite Hermitian spectral formula, without a factor one half. The dynamical witness derives its error from the supplied matrix remainder enclosure; it does not derive an equation of motion or that enclosure. The separable-set construction in equation (15), general LP and tangent-cone theorems, and infinite-dimensional trace-class results remain written rather than newly mechanized. No publication or Git commit was performed.
