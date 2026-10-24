# Bell LP and tangent-cone release, 23 October 2026

Version **0.7.0** adds **75 named Lean theorems** in eight modules, giving an exhaustive census of **256** in twenty modules. The finite LP results construct attained primal and dual optima for weighted Bell repair, prove its support-witness and slack-variable formulations, and construct optimal normalized signed extensions with their negative-mass and vertex-spread duals. Signed duality explicitly requires an inhabited normalized signed fiber.

Finite real-variable elimination and linear-image closure construct an inequality presentation of the actual Bell simplex image. The active-constraint tangent cone is proved equal to the intrinsic closed radial cone. For a local starting behavior, repair along a sufficiently short ray equals time times distance of its velocity to that cone. A trajectory remainder bounded by C t^2 gives the same C t^2 error in repair. The positive time window is an existence theorem; the trajectory remainder is a premise. Positive weights are required for zero repair to characterize the unweighted local behavior. Nonnegative weights are handled through the weighted image.

Fresh source compilation and the complete verifier from a clean ZIP extraction passed under Lean 4.35.0. The exhaustive census uses only `propext`, `Quot.sound`, and `Classical.choice`; it has no custom axioms or admitted proofs. All twelve previous modules and all 181 previous axiom entries are unchanged. Recomputing the dependency closure confirmed the existing pinned bundle already includes every required module: 2948 modules and 20672 individually hashed files. Clean replay unpacked those dependencies itself and matched the complete final census.

The clean package passed **26 tests**, the supplied **39/39 checks**, separate checks of **8 repair and 7 negative-mass certificates**, 14 numerical LP solves, finite matrix/observer/Mermin checks, and direct notebook-cell replay. All **65 payload files** retained their hashes throughout verification. All **12 numbered claims** are mapped to their actual evidence, and five malformed-map mutations were rejected. The source-bound **21-page PDF** has zero overfull boxes; pages 1, 5, 6, 10, 18, 20 and 21 were visually reviewed.

The supplied review is preserved byte-for-byte and assessed in the package. Its encoding, linear-map, signed-table, reference, and evidence-independence corrections are incorporated. The fixed-witness limitation at a saturating product start is included as a written argument, explicitly outside the Lean census. The Python simplex implementation is not certified by the mathematical LP duality proofs.

Archive: `../036_bell_positive_extensions_and_projection_residuals/dist/bell_positive_extensions_v0.7.0.zip`  
Bytes: `707663004`  
SHA-256: `2aaf41b188c78bfe7a9474eae7cef8552f166f6b405eda8174b9b0317edf4314`

The companion JSON and raw logs bind commands, durations, theorem names, source and archive digests, clean extraction, and PDF inspection. Historical archives and receipts are retained. Infinite-dimensional trace-class conversions, full isotropic repair-cost sharpness, Mermin/cohomology results, and general trajectory remainder derivations remain outside the census. No Git commit or publication was performed.
