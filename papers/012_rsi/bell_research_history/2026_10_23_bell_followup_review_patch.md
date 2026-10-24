# Bell follow-up review patch, 23 October 2026

Version **0.7.1** applies the requested Theorem 8 claim-map correction exactly:

> Lean qualitative factorization and exact finite scalar minimax.

The unsupported reference to a general bounded-but-infinite-fiber minimax extension is removed. Qualitative factorization has broader scope; the minimax result requires a finite nonempty history set. The review's matrix-encoding and linear-map edits were already in v0.7.0.

The follow-up review is preserved byte-for-byte, hashed in source custody, and assessed as a review of the v0.6 selection. Its reported 39 exact checks, eight repair certificates and seven negative-mass certificates are distinguished from our local replay. It did not independently rebuild Lean or review the later v0.7 LP/tangent proofs. Historical drafts and erroneous older notes remain labeled research inputs with their corrections recorded.

All **20 Lean modules**, the complete **256-theorem census**, numerical code, certificate checkers, notebook and tests are byte-identical to v0.7.0. The updated archive passed a fresh clean-extraction Lean build and full census comparison, **26 tests**, **39/39 supplied checks**, **8 repair and 7 negative-mass certificate checks**, numerical examples and direct notebook-cell replay. The fresh run verified all 20,672 bundled dependency file hashes and left all 68 payload file hashes unchanged. There are no new theorems or custom axioms.

The rebuilt **21-page PDF** is bound to its Markdown, TeX, compilation log and auxiliary record. It has zero missing glyphs or overfull boxes. Pages 1 and 18 were visually reviewed; sampled pages 5, 6, 10, 20 and 21 are pixel-identical to the previously reviewed v0.7.0 renderings. The manuscript does not generate a table of contents.

The archive's second build was byte-identical. All 12 numbered claims are mapped, and five malformed-map mutations were rejected.

Archive: `../036_bell_positive_extensions_and_projection_residuals/dist/bell_positive_extensions_v0.7.1.zip`  
Bytes: `707758864`  
SHA-256: `8253c95ab7aaa8b12bcb47578eee58961c570ae0ebbdf37e5c0fcc1490357073`

The initial clean attempt stopped during dependency extraction with a disk-space error. Its failed log is preserved separately. Only obsolete task-owned verification extractions and a duplicate scratch dependency bundle were removed; the successful run restarted from a new extraction. The companion JSON and raw logs bind both attempts, commands, durations, source/archive digests and the clean extraction. The previous release archive and receipt are retained. No Git commit or publication was performed.
