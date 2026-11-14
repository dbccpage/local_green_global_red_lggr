# Observer-relative control of cochain residuals

Jeremy H. Carroll. Version 2.1.3, 2026-10-23.

Read [observer_control.md](observer_control.md) or `observer_control.pdf`. The archive is `observer_control.zip` and its
checksum sidecar is `observer_control.zip.sha256`. Published version DOI: [10.5281/zenodo.23604797](https://doi.org/10.5281/zenodo.23604797). The local package now records the DOI and corrected concept lineage; these refreshed files have not been uploaded to replace the deposited files.

Coordinate coverage does not bound raw cochains by a quotient residual. The corrected theorem bounds selected residuals, or raw vectors under an explicit weighted-input-norm assumption. The reference linear program uses floating-point arithmetic.

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

The current record is [10.5281/zenodo.23604797](https://doi.org/10.5281/zenodo.23604797), under concept DOI
[10.5281/zenodo.20652483](https://doi.org/10.5281/zenodo.20652483). Both were verified against Zenodo and DataCite on 2026-10-23. The registry labels this edition `v2.1.3 Pre-Print`; the package uses semantic version `2.1.3`.

The earlier package cited record `10.5281/zenodo.20214468` and concept `10.5281/zenodo.20214467`. Those remain historical identifiers, not the current record's concept lineage. The [publication record](docs/publication_record.json) binds the downloaded published PDF and ZIP, which matched the local files before this DOI refresh.

For an extracted download whose ZIP remains in its parent directory, use
`python verify_deposit.py --lean --archive ../observer_control.zip`.
