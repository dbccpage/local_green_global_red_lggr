# Representation Abundance Is Not Physical Authority: Finite Selectors, Witnessed Differences, and the Local-Green Boundary

Jeremy H. Carroll · Prepared edition 2.2.0 · 2026-10-16

A large family of representations need not distinguish its members observationally. For a finite candidate family, we characterize the properties recoverable from an observation map and show that adding candidates without adding observable profiles increases the average fiber size. A rational graph example separates local tolerance checks from global integrability and gives a sharp cycle-holonomy bound. A finite selector then distinguishes candidate survival from unique selection relative to declared alternatives and measurements. The results do not authenticate the measurements or establish that the candidate family is exhaustive. Written proofs, finite Python checks, and supporting Lean lemmas are identified separately.

## This revision

Clarified rational-valued cochains versus algebraically exact cochains, finite candidate domains, and the strict local-check hypothesis. Separated observable properties from unique candidate identification and stated the limits of the supporting Lean lemmas.

This is a prepared republication package, not a record of a new public deposit. The repository contains October 2026 revisions and earlier release archives; public publication history has not been independently established. Existing DOI references identify prior records or repository-declared lineage. No new version DOI is assigned here.

## Contents

- `representation_abundance_is_not_physical_authority.md`: canonical manuscript; matching `.tex`, `.pdf`, and `.txt` files are generated.
- `representation_abundance_is_not_physical_authority_math_spine.md`: canonical expressions with persistent equation UUIDs.
- `representation_abundance_is_not_physical_authority_math_spine.json`: ordered occurrence bindings, including repeated formulas.
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
