# Complete quantum CF/N comparison

The canonical construction and proof are Theorem 22 in Section 8.6 of the main manuscript, 036_bell_positive_extensions_and_projection_residuals.md.

For k >= 2, the family retains every one of the k^4 contexts of a k^2-by-k^2 binary Bell experiment. Its certified comparison is CF/N_min >= 3k - 4 + 3/(k+1). These are bounds, not claims of exact optima.

The proof uses a smoothed cyclic profile, its normalized Gram matrix, a constructive local model minus white noise, and a chained failure-count witness. The primary-source quantum bridge and the precise Lean boundary are stated in the manuscript. See formalization.md and claim_code_map.yaml for declarations and assumptions.

Replay code/smoothed_gram.py for the six exact finite complete-table checks and code/smoothed_quantum.py for the separate finite Clifford/Born matrix check. Neither finite replay substitutes for the all-size written proof.
