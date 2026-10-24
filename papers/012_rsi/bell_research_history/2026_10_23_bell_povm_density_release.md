# Bell POVM and density-operator release, 23 October 2026

Version **0.4.0** adds **39 named Lean theorems**, taking the Bell census to **119**. Binary positive effects summing to identity are proved to give Hermitian contractions. Positive unit-trace matrices yield normalized spectral weights, unit eigenvectors, an explicit rank-one reconstruction and the trace-mixture identity. Joint Born traces are proved real, nonnegative and normalized under cross-party commutation, with both no-signalling marginals and the exact CHSH score identity. Local tensor lifts discharge the measurement premises and give the finite-dimensional density/POVM CHSH bound.

A fresh package build and a second build from a clean ZIP extraction passed under Lean 4.35.0. Every named theorem uses only the standard axioms `propext`, `Quot.sound` and/or `Classical.choice`; there are no custom axioms or admitted proofs. The expanded offline bundle contains 2948 pinned dependency modules and 20672 individually hashed files.

The full clean-extraction verifier passed **21 exact tests**, 14 numerical LP solves, the finite quantum/observer checks and direct notebook-cell replay, and confirmed that verification left all packaged payload bytes unchanged. The source-bound PDF has **19 pages and zero overfull boxes**; pages 1, 6, 7, 17 and 19 were visually reviewed.

Archive: `../036_bell_positive_extensions_and_projection_residuals/dist/bell_positive_extensions_v0.4.0.zip`  
Bytes: `707256271`  
SHA-256: `e7fe2f2edda3acbfea49ae793d5382e3a4e85d65913f6aa0aff836faae1eb63d`

The companion JSON records the exact commands, durations, archive/census hashes, extracted directory and raw-log hashes. The original supplied source, earlier release archives and historical verification reports are preserved. This is a locally verified research package; no commit or publication was performed.

The conversions cover arbitrary finite matrix dimensions, including singular densities and zero effects. They do not assume contractivity or a supplied ensemble decomposition. Infinite-dimensional trace-class conversions, general LP/tangent-cone results and Mermin/cohomology theorems remain outside this Lean census.
