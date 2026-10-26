# Conditional density lifts and a primal–dual alignment statistic

Jeremy H. Carroll. Version 2.0.5, 2026-10-23.

Read [density_lift.md](density_lift.md) or `density_lift.pdf`. The archive is `density_lift.zip` and its
checksum sidecar is `density_lift.zip.sha256`. Published version DOI: [10.5281/zenodo.23604860](https://doi.org/10.5281/zenodo.23604860). The local package now records the DOI and confirmed concept lineage; these refreshed files have not been uploaded to replace the deposited files.

The real projector construction and strict primal-dual distance bound have prose proofs. Lean checks discrete integer and rational statements. Numerical vector evaluation does not establish optimality or compute the canonical selector.

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
| Reference module, mathematical tests and Lean sources | MIT, see LICENSE-CODE |
| Renderer, Lua filter and code/deposit_paths.py | Apache-2.0, see LICENSE-TOOLS |

Previous sources and identifiers are retained under `_support/history/` in the
research checkout. That directory is excluded from the new public archive.
It is not a dependency of the extracted package.

## Version lineage

The current record is [10.5281/zenodo.23604860](https://doi.org/10.5281/zenodo.23604860), under concept DOI
[10.5281/zenodo.20192296](https://doi.org/10.5281/zenodo.20192296). Both were verified against Zenodo and DataCite on 2026-10-23. The registry labels this edition `v2.0.5 Pre-Print`; the package uses semantic version `2.0.5`.

The earlier record `10.5281/zenodo.20192297` belongs to the same concept DOI. The existing concept lineage is preserved. The [publication record](docs/publication_record.json) binds the downloaded published PDF and ZIP, which matched the local files before this DOI refresh.

For an extracted download whose ZIP remains in its parent directory, use
`python verify_deposit.py --lean --archive ../density_lift.zip`.
