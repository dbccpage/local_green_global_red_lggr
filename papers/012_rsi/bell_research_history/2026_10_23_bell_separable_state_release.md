# Bell separable-state release, 23 October 2026

Version **0.6.0** adds **34 named Lean theorems**, for an exhaustive census of **181** in twelve modules. `Bell.Separable` constructs actual finite mixtures of product density matrices, proves positivity and trace one, derives their normalized local Born responses, and builds positive global extensions. It constructs both partial traces, proves density and separability of their product, and proves the product map idempotent.

The complete finite-dimensional inequality (15) is mechanized: weighted behavior repair is at most half the infimum of the Hermitian trace norm over separable states, which is at most half the product-marginal residual. Settings, outcomes and local dimensions are arbitrary finite types; context weights are nonnegative and normalized. The comparison sets are explicitly defined and nonemptiness is proved. No closest separable state is supplied. A separate specialization uses the existing uniform CHSH repair, and every separable state satisfies the classical CHSH ceiling.

Fresh source compilation and the full verifier from a clean ZIP extraction both passed under Lean 4.35.0. The exhaustive census has only `propext`, `Quot.sound`, and `Classical.choice`; no custom axioms or admitted proofs. All eleven previous Lean modules and all 147 previous axiom entries are unchanged. The existing pinned dependency archive suffices: 2948 modules and 20672 individually hashed files. The clean replay unpacked these dependencies itself and matched the full final census, including the updated descriptive scope.

The clean package passed **26 tests**, the supplied **39/39 checks**, independent checks of **8 repair and 7 negative-mass certificates**, 14 numerical LP solves, finite matrix/observer/Mermin checks, and direct notebook-cell replay. Its payload hashes were unchanged before and after verification. All **12 numbered claims** are mapped to their actual evidence, with written-only results explicit; five malformed-map mutations were rejected. The source-bound **20-page PDF** has zero overfull boxes, and pages 1, 8, 9, 17, 18 and 20 were visually reviewed.

Archive: `../036_bell_positive_extensions_and_projection_residuals/dist/bell_positive_extensions_v0.6.0.zip`  
Bytes: `707525079`  
SHA-256: `2d5ec2ca6f6f38ddbfcc1ed57b33cb3beba61406e473997a95e1bae2c4909aad`

The companion JSON and raw logs bind the commands, durations, new theorem names, source and archive digests, clean extraction, and PDF. Only regenerable verification caches were removed for disk space; historical release archives and receipts remain. General LP/tangent-cone theorems, infinite-dimensional separability and unspecified dynamical remainder derivations remain outside this census. No Git commit or publication was performed.
