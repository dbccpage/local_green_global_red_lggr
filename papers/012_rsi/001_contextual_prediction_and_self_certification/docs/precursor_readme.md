# Conditional Limits on Global Prediction, Self-Knowledge and Self-Certification for Physical Reasoners (CODA-FOC / CODA-GTLA)

**Author:** Jeremy H. Carroll  
**Date:** 2026-10-17  
**Version:** 1.2.0  
**Status:** WORKING_DRAFT. Not deposited; no DOI.  
**License:** Creative Commons Attribution 4.0 International for the manuscript and documentation (`LICENSE`). PolyForm Noncommercial 1.0.0 for source code, Lean files and release tooling (`LICENSE-CODE`).  
**Authority status:** None.

This package holds the monograph `epistemic_no_go_monograph.md`, a Lean 4.34.0 model of the support-level statements (`lean4/`), a standard-library Python check suite (`code/`), and the deposit tooling. It is isolated: nothing outside the package directory is needed, and there is no Mathlib or network dependency.

## What the package covers

- Lean: 29 declarations in `lean4/ResultI.lean` to `ResultIV.lean`, finite models only. `lean4/axiom_report.txt` lists the axioms of each.
- Python: 26 tests of the finite statements, using the standard library and exact fractions.
- Not here: the exact-rational linear-programming kernel that computes the ℓ¹ defects and dual witnesses of Result I. It is on the programme repository trunk (commit b8a84409f) and is not reproducible from this package. The Lean model of the three-role gate is a re-statement and is not machine-checked against the Rust gate.

`docs/mechanization_map.md` maps each statement to its Lean declaration and Python test.

## Reproduction machinery

These commands are reproduction machinery, not verification reports. The dated receipts are in section 6 of the monograph.

```bash
python3 -m pytest code/tests -q
cd lean4 && lake build && lake env lean Census.lean && cd ..
python3 tools/replay_lean_axiom_census.py --replay .
python3 verify_deposit.py --lean
python3 scripts/regen_sha256sums.py --check
```

Python 3.10 or later is needed. `verify_deposit.py` runs each test file under `code/tests` with the package root as the working directory and sweeps `MANIFEST.sha256` in both directions.

## Layout

- `epistemic_no_go_monograph.md`, `epistemic_no_go_change_log.md`: manuscript and dated version history.
- `docs/`: `descriptions.md`, `keywords.md`, `references.md`, `quick_start.md`, `mechanization_map.md`, and `legacy_float_kernel_listings.md` (the superseded version 1.0.0 floating-point listings, kept as a defect archive).
- `code/`, `lean4/`, `scripts/`, `tools/`, `verify_deposit.py`: checks, Lean model and tooling.
- `MANIFEST.sha256`, `SHA256SUMS`: checksums in ordinal byte order.

## Not done

No PDF, TeX or notebook has been built for this version. No upload has been made and no DOI exists. Bibliography entries without an asterisk in `docs/references.md` are unverified against the publisher record.
