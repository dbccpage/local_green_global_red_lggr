# Reproduction

This is version 2.0.5, dated 2026-10-23, associated with DOI [10.5281/zenodo.23604860](https://doi.org/10.5281/zenodo.23604860). This local metadata refresh has not replaced the deposited files. Keep `density_lift.zip` and its `.sha256` sidecar in the same download
directory, extract the ZIP there, and enter the extracted package folder.

Use Python 3.12 or later with the dependencies in `pyproject.toml`:

```text
python -m pip install ".[dev]"
python -m pytest code/tests -p no:cacheprovider --runxfail
python verify_deposit.py --lean --archive ../density_lift.zip
```

Lean is pinned in `lean4/lean-toolchain` and has no external package dependency.
Run `python tools/replay_lean_axiom_census.py --check` to replay the declaration
census. The checker compares the requested names, allowed axioms and source
hashes; it does not turn discrete lemmas into unproved real-valued statements.

Rendering requires Pandoc, XeLaTeX, Times New Roman, Consolas and Latin Modern
Math. Run `python scripts/build_pdf.py` from the package root. A source edit
invalidates its render binding and checksum manifests. After all validation,
`python tools/rebuild_release.py` refreshes the archive; use `--check` for
read-only envelope verification. Tests and builds write only excluded caches
and scratch outputs. Checksum agreement establishes byte identity.
