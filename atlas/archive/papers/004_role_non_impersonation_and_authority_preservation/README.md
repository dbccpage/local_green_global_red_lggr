# The Omega Tower: Role Non-Impersonation and Authority Preservation in Agentic AI

Jeremy H. Carroll · Prepared edition 1.3.0 · 2026-10-16

This monograph presents a contract model for separation of proposal, evaluation, and authorization in agentic systems. It verifies several algebraic components and records explicit failure modes when a declared contract is not honored.

We formalize the foundational boundary: proposal is not authority ((see manuscript notation)). Generating a fluent candidate action, regardless of heuristic confidence or internal self-critique, does not constitute execution authority. Authority is an inhabited dependent type requiring an explicit terminal certificate produced by an independent, replayable verification pipeline.

The six roles are a proposed contract: detect defects, gate authorization, track representation changes, compare candidates, check finite evidence, and retain unresolved outcomes. The mathematical results concern constructor distinctions, exception propagation, and predicate transport through a quotient. They do not prove that this six-role decomposition is necessary for every secure architecture.

## This revision

Restricted universal-descent authorization to inhabited observation fibers; clarified that universal quantification alone accepts empty fibers vacuously. Scoped the six-role correspondence to its constructor convention, refusal propagation to the pure bind operation, and finite evidence transport to an explicit factorization. Removed unsupported cofinality and repeated policy claims.

This is a prepared republication package, not a record of a new public deposit. The repository contains October 2026 revisions and earlier release archives; public publication history has not been independently established. Existing DOI references identify prior records or repository-declared lineage. No new version DOI is assigned here.

## Contents

- `role_non_impersonation_and_authority_preservation.md`: canonical manuscript; matching `.tex`, `.pdf`, and `.txt` files are generated.
- `role_non_impersonation_and_authority_preservation_math_spine.md`: canonical expressions with persistent equation UUIDs.
- `role_non_impersonation_and_authority_preservation_math_spine.json`: ordered occurrence bindings, including repeated formulas.
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
