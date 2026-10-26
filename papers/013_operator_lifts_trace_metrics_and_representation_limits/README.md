# Operator Lifts Trace Metrics and Representation Limits

Jeremy H. Carroll · Prepared edition 2.1.1 · 2026-10-23

We compare two representations of a finite real cochain: its diagonal operator and the rank-one projector obtained from its normalized signed square-root coordinates. The diagonal map is injective and preserves the sum-of-absolute-values norm as trace norm. The projector identifies precisely the nonzero scalar multiples of a cochain, losing mass and global orientation while retaining every diagnostic constant on those fibers. Trace distance defines a pseudometric on nonzero cochains and a metric on their real projective quotient. We prove a chain-complex residual bound, describe local reconstruction using an orientation anchor, and show that a continuous global sign choice is impossible in dimension at least two. A guarded evaluator uses these representations under an explicit selection policy. The real-vector arguments are written proofs; the Lean package verifies narrower integer and rational identities. No physical quantum interpretation is asserted.

## This revision

Completed the fixed-mass sign-selection proof, including continuity of the sign coefficient and restriction to a two-dimensional subspace. Scoped numerical stability claims to floating-point limitations. Added a bibliography and removed the inherited Ricard citation whose arXiv identifier resolves to an unrelated work.

This is a prepared republication package, not a record of a new public deposit. The repository contains October 2026 revisions and earlier release archives; public publication history has not been independently established. Existing DOI references identify prior records or repository-declared lineage. No new version DOI is assigned here.

## Contents

- `operator_lifts_trace_metrics_and_representation_limits_monograph.md`: canonical manuscript; matching `.tex`, `.pdf`, and `.txt` files are generated.
- `operator_lifts_trace_metrics_and_representation_limits_math_spine.md`: canonical expressions with persistent equation UUIDs.
- `operator_lifts_trace_metrics_and_representation_limits_math_spine.json`: ordered occurrence bindings, including repeated formulas.
- `*_claim_ledger.md`: claim scope, evidence, and formalization limits; expressions and claims are distinct.
- `docs/paper_inventory.json`: parsed document nodes, byte-addressed source lines, and formula occurrences.
- `docs/render_receipt.json` and `docs/equation_locations.json`: source/build/file digests and PDF destination points.
- `code/`, `code/tests/`, and `lean4/`: finite reference implementation, regressions, and scoped formal proofs.
- `MANIFEST.sha256`, `SHA256SUMS`, and the dated ZIP: reproducible release inventory and standalone verification.

## Build and verify

Use Python 3.12 with the package's test dependencies, Pandoc, XeLaTeX, Poppler (`pdftotext`), and PyMuPDF for PDF occurrence locations. Use the Lean version in `lean4/lean-toolchain`. From this package directory:

```sh
python scripts/paper_spine.py check
python scripts/build_pdf.py
python scripts/paper_spine.py verify
python scripts/paper_spine.py inventory --output docs/paper_inventory.json
python -m pytest -q --confcutdir=. code/tests
python tools/rebuild_release.py .
python tools/rebuild_release.py . --check
python verify_deposit.py --lean
```

A mathematical edit must update the manuscript and its spine entry deliberately, retaining the equation UUID. Run `python scripts/paper_spine.py sync` to rebind occurrences after that edit. New equations require new explicit spine entries. The build never silently adopts changed mathematics.

The text export retains literal LaTeX equations. PDF-extracted prose is in `docs/rendered_text.txt`. Ordered MD/TeX/text checks preserve signs, grouping, commands, and repeated occurrences. PDF checks bind a fresh compilation to exact bytes and locate every occurrence; they do not prove independent symbolic equivalence of rendered glyphs. Written and Lean proof review remain separate. No overall correctness percentage is assigned.

Paper: CC-BY-4.0. Code: see LICENSE-CODE; the existing code license is unchanged.

`python code/verify_witnesses.py` checks the two rational cycle certificates in `docs/witnesses/`. They witness zero and positive repair residuals for those examples only.
