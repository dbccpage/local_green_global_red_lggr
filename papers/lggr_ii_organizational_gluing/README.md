# Local Green, Global Red II

## Organizational evaluator gluing

**Author:** Jeremy H. Carroll\
**Date:** 2026-10-15\
**Version:** 1.3.1\
**DOI:** [10.5281/zenodo.22882042](https://zenodo.org/records/22882042) (lineage / previous version: [10.5281/zenodo.20674787](https://doi.org/10.5281/zenodo.20674787))

An interface can pass every local check and still fail its global check. This
package studies that fact in a finite Boolean model. For local evaluators
`E_i` and a global evaluator `E_G`, the defect is

\[
\Delta_E = E_G-\prod_i E_i\in\{-1,0,1\}.
\]

`Δ_E = -1` is the local-green/global-red witness. The paper derives its exact
Boolean characterization, gives a counterexample showing that a weak boundary
representation does not imply evaluator factorization, and derives a quotient
obstruction when the global evaluator varies inside one local carrier class.

The governance interpretation is deliberately small. A checked boundary must
have representational sufficiency, an accountable owner with power to change
the interface, temporal coherence, and evaluator agreement. These are defined
requirements; the Lean proofs establish the finite Boolean statements, not an
empirical theorem about organizations.

## Read and reproduce

- `lggr_ii_organizational_gluing.md` — source manuscript.
- `lggr_ii_organizational_gluing.tex` and `.pdf` — generated publication forms.
- `lggr_ii_organizational_gluing_claim_ledger.md` — claim-to-evidence table.
- `docs/lean_claim_map.md` — declaration, statement-hash, import-hash, and
  current Lean replay map.
- `code/organizational_gluing_core.py` — executable finite model.
- `code/tests/` — unit, mutation, figure, and notebook checks.
- `pyproject.toml` and `uv.lock` — Python package definition and locked environment.
- `lean4/` — self-contained Lean project and axiom census.
- `jupyter_notebooks/lggr_ii_organizational_gluing.ipynb` — one public
  companion, from first intuition to the quotient obstruction.
- `public_export/` — generated figures used by the paper and notebook.
- `docs/descriptions.md` — canonical Primary and Secondary public descriptions.

From this directory, use Python 3.12 and the pinned environment to run the
Python gate:

```bash
uv run --isolated --frozen --python <python-3.12> --extra dev \
  python -m pytest -n 8 code/tests \
  --cov=organizational_gluing_core --cov=generate_figures --cov-branch \
  --cov-report=term-missing --cov-report=json:<external-temp>/coverage.json
```

`verify_deposit.py` reads the coverage JSON produced by its own isolated test
run and independently requires at least 95 percent line/statement coverage and
at least 95 percent branch coverage over those two production modules.

Regenerate the figures:

```bash
uv run --isolated --frozen --python <python-3.12> --extra dev \
  python code/generate_figures.py
```

Build and audit Lean:

```bash
cd lean4
lake build LGGR2
lake env lean check_axioms.lean
```

Regenerate the paper and then the deposit manifests:

```bash
python scripts/build_paper_artifacts.py
python scripts/regen_sha256sums.py
uv run --isolated --frozen --python <python-3.12> --extra dev \
  python verify_deposit.py --lean
python scripts/build_deposit_zip.py
```

The final command creates
`lggr_ii_organizational_gluing_2026-10-15.zip` deterministically from the
pinned file set.
The scripts do not upload that archive or mint a DOI.

The review files under `docs/rt/` examine earlier archive bytes. They are
historical records, not a review pass for the archive rebuilt from this repair.

## Mathematical map

| Result | Lean declaration | Python witness |
| --- | --- | --- |
| Defect trichotomy | `PaperAE005.orgDelta_range` | `EvaluatorGluingDefect` |
| `Δ_E=-1` characterization | `PaperAE005.orgDelta_is_negative_one_iff` | `OrganizationalEvaluatorSystem.evaluate` |
| Weak sufficiency counterexample | `PaperAE005.weak_boundary_sufficiency_does_not_force_factorization` | `WeakSufficiencyAuditor` |
| Product sufficiency equivalence | `PaperAE005.product_sufficiency_iff_evaluator_factorization` | `FiniteTheoremCensus.product_sufficiency_iff_factorization_census` |
| Owner necessity in the declared conjunction | `PaperAE005.governance_prerequisites_require_auth` | `DefinitionalNecessityGuard` |
| Zero defect is not a passing certificate | `PaperAE005.zero_defect_does_not_imply_all_pass` | `DetectorAdequacyGuard` |
| Product-aligned detector collapse | `PaperAE005.aligned_validator_forces_zero_defect` | `DetectorAdequacyGuard.is_aligned_validator_collapsing` |
| Carrier-class quotient obstruction | `PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization` | `FiniteTheoremCensus.quotient_factor_table` |
| Local-green mixing forces defect `-1` | `PaperAE005.boundary_carrier_mixing_forces_lggr` | `FiniteTheoremCensus.negative_defect_witness` |

## Citation

```bibtex
@article{carroll2026lggr2,
  author  = {Jeremy H. Carroll},
  title   = {Local Green, Global Red II: Organizational Evaluator Gluing},
  year    = {2026},
  version = {1.3.1},
  doi     = {10.5281/zenodo.22882042},
  url     = {https://zenodo.org/records/22882042},
  note    = {Zenodo version lineage 10.5281/zenodo.20674787}
}
```

Paper, figures, and documentation are CC BY 4.0. Code and Lean sources are
Apache 2.0.
