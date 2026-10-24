# Bell probability-integral and quantum release, 23 October 2026

Version **0.3.0** adds **32 named Lean theorems**, taking the Bell census to **80**. The actual probability-integral equivalence includes proved measurability/boundedness consequences, integrability, averaging laws and an atomic-measure converse. Quantum proofs cover the Tsirelson operator ceiling, pure and finite-mixture state bounds, the Hermitian-involution contraction bridge, and an exact complex two-qubit Born table attaining the ceiling and violating the local bound.

The fresh census and a second build from a clean ZIP extraction passed under Lean 4.35.0. Every theorem depends only on `propext`, `Quot.sound`, and/or `Classical.choice`; no custom axioms or admitted proofs occur. The package includes 2634 pinned dependency modules and 18474 individually hashed dependency files.

The full clean-extraction verifier passed all 21 exact tests, 14 numerical LP solves, the finite quantum/observer checks and direct notebook-cell replay. It confirmed that verification did not modify the packaged payload. The source-bound PDF has 18 pages and zero overfull boxes; pages 1, 3, 6, 7, 16 and 18 were visually reviewed.

Archive: `../036_bell_positive_extensions_and_projection_residuals/dist/bell_positive_extensions_v0.3.0.zip`  
Bytes: `613351824`  
SHA-256: `0164dfe963c6f68ee09d217191e6c64a3a37d54efce5da9be01dc2ef61413029`

The accompanying JSON binds the archive, census, exact commands, durations, clean-extraction directory and full raw logs. The original supplied manuscript is preserved unchanged. Earlier release archives and verification reports remain available. This is a locally verified research package, with no commit or publication performed.

General LP duality and tangent-cone theorems, arbitrary POVM/density-operator conversions, other quantum state/dynamical calculations and Mermin/cohomology results remain outside this Lean census.
