# Institutions That Can Know

**Jeremy H. Carroll — version 0.1.0, 2026-10-23**

Preserving Difference, Coordinating Action, and the Risks of Epistemic Collapse.

This third RSI paper studies how institutions preserve distinctions, compare accounts, correct records and coordinate bounded action. The world is one world; participants and evaluators are embedded within it. A common record format need not force a common explanation.

Read the [manuscript](institutions_that_can_know_monograph.md), [PDF](institutions_that_can_know_monograph.pdf), [DOCX](institutions_that_can_know_monograph.docx), or [claim ledger](institutions_that_can_know_claim_ledger.md). The proposed [Anomalon comparison packet](contracts/anomalon_institutional_reasoning.contract.yaml) is an example without an execution mandate. The [source custody record](docs/source_custody.json) identifies the unchanged supplied kernel and tests. Historical inputs live separately in the repository's RSI research directory; the active package needs no files from that directory.

## What is established

- Written recovery and finite side-information proofs, with their cost assumptions explicit.
- Eight Lean theorems covering invariant separation, recovery, question profiles, side-code separation, the global contradiction and joint constraints.
- Seventeen supplied Python tests, including two independent exhaustive checks of 216 cases each.
- A proposed four-role council protocol and falsifiable evaluation plan. No live council, human study or performance gain is reported.

The full side-bit cardinality theorem is not Lean-formalized here. The [formalization map](docs/lean_claim_map.md) records the exact boundary. The Boolean mandate fixture is not an authentication implementation.

## Reproduce from a fresh extraction

Use Python 3.10 or later. The finite kernel, tests, hash checks and archive tooling need only the standard library. Commands are run from this package root; `python` means your selected interpreter.

```sh
python tools/run_checks.py
python verify_deposit.py --test
```

Fresh Lean replay needs the installed toolchain `leanprover/lean4:v4.35.0` and its `lake` on PATH. There are no remote Lake dependencies or vendored math libraries. An absent toolchain fails; a stored report is not substituted for a requested build.

```sh
python verify_deposit.py --lean
```

This performs `lake build`, the source-covered named census replay, and the full declaration census. Check mode never rewrites the sealed census files. Explicit regeneration after proof edits uses:

```sh
python tools/replay_lean_axiom_census.py --write
python tools/replay_full_axiom_census.py --write
```

Optional dependency profiles are declared in `pyproject.toml`. Install them in your environment before selecting their checks:

```sh
python -m pip install ".[contract,notebook,documents]"
python verify_deposit.py --contract --notebook
```

The notebook executes assertions in memory without modifying the deposited file. YAML inspection uses PyYAML; notebook replay uses nbclient, nbformat and ipykernel. No repository-wide Python import path or native build directory is required.

## Documents and release

Document generation additionally needs Pandoc, XeLaTeX, `pdftotext`, the fonts in `scripts/obstruction-preamble.tex`, and PyMuPDF for PDF equation destinations. These are external build dependencies, not bundled executables.

```sh
python scripts/build_pdf.py
python tools/build_docx.py
python verify_deposit.py --documents
```

The equation registry already exists. Explicit equation changes must be reconciled with the canonical math spine before `python scripts/paper_spine.py sync`; the builder fails on drift. DOCX is generated from the same body and checked for an ordered math round-trip through Pandoc under the limited typesetting normalizations listed in its receipt. The receipt records every differing TeX serialization and binds the document bytes and source; it does not assert glyph equivalence or mathematical truth.

```sh
python tools/rebuild_release.py
python tools/rebuild_release.py --check
python verify_deposit.py --test --lean --contract --notebook --documents --archive
```

Rebuilding the release uses the publication date pinned in metadata, validates a staged replacement, then replaces the ZIP and manifests. It does not regenerate documents or empirical evidence. New edition identity requires deliberate metadata changes and `--new-release`. The archive is deterministic for the same payload and compression runtime. The extracted folder normally contains no nested ZIP; omit `--archive` there. Checks revalidate sealed bytes after execution.

Text is CC BY 4.0 (`LICENSE`); code and Lean source use PolyForm Noncommercial 1.0.0 (`LICENSE-CODE`). Prepared deposit metadata does not assert publication or a DOI.
