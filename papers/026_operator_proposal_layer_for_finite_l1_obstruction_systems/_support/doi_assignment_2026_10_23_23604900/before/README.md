# Proposal selection and continuation-stable diagnostics on finite graphs

Jeremy H. Carroll. Version 2.0.5, 2026-10-23.

Read [operator_proposals.md](operator_proposals.md) or `operator_proposals.pdf`. The archive is `operator_proposals.zip` and its
checksum sidecar is `operator_proposals.zip.sha256`. This is a prepared revision; no new
publication or DOI is claimed.

The scalar graph solver uses exact rational witnesses. The vector-valued extension is mathematical, not a generic numerical implementation. Label erasure for one-step decisions does not imply stable state compression under arbitrary continuations.

## Reproduction

```text
python -m pip install ".[dev]"
python -m pytest code/tests -p no:cacheprovider --runxfail
python verify_deposit.py --lean --require-archive
```

See [the quick start](docs/quick_start.md), [description](docs/descriptions.md)
and [references](docs/references.md). The two checksum manifests cover the
complete payload. Archive verification checks the complete deterministic ZIP,
its member bytes and its external SHA-256 sidecar.

## Licenses

| Material | License |
| --- | --- |
| Manuscript, renders and documentation | CC-BY-4.0, see LICENSE |
| Software, tests and Lean sources | Apache-2.0, see LICENSE-CODE |

Previous sources and identifiers are retained under `_support/history/` in the
research checkout. That directory is excluded from the new public archive.
It is not a dependency of the extracted package.

## Version lineage

The previous record is [10.5281/zenodo.20213064](https://doi.org/10.5281/zenodo.20213064), under concept
DOI [10.5281/zenodo.20213063](https://doi.org/10.5281/zenodo.20213063). These identifiers were checked
against DataCite on 2026-10-23. The prepared revision has no assigned version DOI.

For an extracted download whose ZIP remains in its parent directory, use
`python verify_deposit.py --lean --archive ../operator_proposals.zip`.
