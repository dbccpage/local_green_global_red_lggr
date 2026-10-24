# Institutions v0.1.0 verification

Archive: `002_institutions_that_can_know_2026-10-23.zip` (342,437 bytes).

SHA-256: `75b1833972778afc72b000830ba4afdf9ec45da01aee4f361a13195201e0ab0c`.

Source and clean extracted package both passed 17 Python tests, two exhaustive 216-case checks, the four-cell notebook, the proposed contract inspection, fresh Lean build, eight named theorem checks, all 13 local declaration checks, and document-source binding. The extracted Lean directory initially contained no `.lake` cache. Ambient repository Python and Cargo paths were cleared.

All sealed bytes remained unchanged during verification. Cold rebuilding produced the identical archive. A simulated 2031 wall clock also produced identical bytes using the pinned 2026-10-23 publication date. Modified proof bytes and an unexpected payload file were rejected; the restored package passed again.

The full side-bit cardinality formula remains a written counting proof with finite checks. The council protocol remains proposed; no live-model, human, deployed-authorization or superiority result is asserted. See `verification.json` and the recorded command logs for the exact execution scope.
