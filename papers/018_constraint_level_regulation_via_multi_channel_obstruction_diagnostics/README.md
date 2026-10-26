# Candidate selection with residual and constraint diagnostics

Jeremy H. Carroll. Version 2.0.4, 2026-10-23.

Read [constraint_regulation.md](constraint_regulation.md) or `constraint_regulation.pdf`. The archive is `constraint_regulation.zip` and its
checksum sidecar is `constraint_regulation.zip.sha256`. This is a prepared revision; no new
publication or DOI is claimed.

Selection does not establish feasibility, constraint preservation or convergence. The ratio test does not detect deletion. Lean verifies discrete comparisons; the general cochain inequality has a separate prose proof.

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

The previous record is [10.5281/zenodo.20214310](https://doi.org/10.5281/zenodo.20214310), under concept
DOI [10.5281/zenodo.19322638](https://doi.org/10.5281/zenodo.19322638). These identifiers were checked
against DataCite on 2026-10-23. The prepared revision has no assigned version DOI.

For an extracted download whose ZIP remains in its parent directory, use
`python verify_deposit.py --lean --archive ../constraint_regulation.zip`.
