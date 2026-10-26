# Observer-relative control of cochain residuals

Jeremy H. Carroll. Version 2.1.3, 2026-10-23.

Read [observer_control.md](observer_control.md) or `observer_control.pdf`. The archive is `observer_control.zip` and its
checksum sidecar is `observer_control.zip.sha256`. This is a prepared revision; no new
publication or DOI is claimed.

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

The previous record is [10.5281/zenodo.20214468](https://doi.org/10.5281/zenodo.20214468), under concept
DOI [10.5281/zenodo.20214467](https://doi.org/10.5281/zenodo.20214467). These identifiers were checked
against DataCite on 2026-10-23. The prepared revision has no assigned version DOI.

For an extracted download whose ZIP remains in its parent directory, use
`python verify_deposit.py --lean --archive ../observer_control.zip`.
