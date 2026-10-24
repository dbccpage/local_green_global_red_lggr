# Standalone reproduction

Use Python 3.10 or later with pytest and the pinned Lean 4.35.0 toolchain. The mathematical kernels, including the exact simplex solver, use only Python's standard library. Lean's source-pinned Mathlib dependencies are included in the offline bundle. Lake extracts the bundle locally; no remote dependency is fetched.

From the package root:

```text
python -m pytest code/tests -q
python tools/generate_lp_certificates.py --check
python tools/replay_simplex_implementation.py --replay
python tools/replay_review_corrections.py
python tools/replay_mind_expansion.py
python code/uncertain_observation_example.py
python verify_deposit.py --lean
python tools/replay_lean_axiom_census.py --replay
python tools/replay_full_axiom_census.py --check
python scripts/paper_spine.py verify
python tools/rebuild_release.py --check
```

Document-binding verification requires Pandoc. PDF rebuilding additionally requires XeLaTeX and pdftotext. Run `python scripts/build_pdf.py`; it refuses formula drift against the explicit math spine. A cold Lean build can take several minutes; the census runner permits ten minutes for that step. After an intentional source edit, update the affected equations in the spine, run `python scripts/paper_spine.py sync`, rebuild the PDF, regenerate the named census with `--write`, regenerate the full census, run tests, and refresh the release with `python tools/rebuild_release.py`.

After an intentional solver edit, run `python tools/generate_lp_certificates.py` to regenerate the exact certificate data and Lean source before building. Its check mode refuses drift. The Lean proof checks those numerical certificates and proves their bounds against arbitrary real probability vectors.

The report-replay modes verify current results and the audited source hashes. The dependency checker validates the vendor archive and extracted cache. No command runs the external Rust crate or imports a companion package. The archived precursor text is historical source, not an additional current manuscript.

After intentionally changing either simplex implementation or its execution driver, run `python tools/replay_simplex_implementation.py --write` before collecting the censuses. `--check` recomputes and binds the 95 full-output cases; `--replay` also runs Lean and compares all outputs, including every Farkas/ray coordinate, pivot count and refusal kind. Source binding refuses stale fixtures. `verify_deposit.py --lean` performs this replay automatically.

`solve_standard` returns the existing `LPCertificate` at an optimum. Catch `CertifiedInfeasible` or `CertifiedUnbounded` and check their `.certificate` fields with `verify_infeasible(costs, matrix, rhs, cert)` or `verify_unbounded(costs, matrix, rhs, cert)`. These checkers require exact original inputs and exact typed witnesses, and read no tableau state. Ordinary `Refusal` carries no checked mathematical outcome. A zero pivot budget can still yield a checked outcome when no pivot is needed; a budget refusal is inconclusive.

The Lean JSON driver runs `CertifiedOutcomes.solveCertified`. Its checked constructors are optimal, infeasible and unbounded; `Simplex.solve` remains the prior optimal-only compatibility entry point. The source packet integration and its empirical limits are documented in `mind_expansion_integration.md`.

For the correction release, Python 3.12.14 is the recorded verification runtime. Extract the full dated ZIP, install pytest, and use its complete tree. The original source-only attachment review could not run release-dependent tests; its four failures remain preserved. For uncertain normalized frequencies, use evaluate_observed with an explicit justified raw l1 radius, then verify_observed against the same original inputs. No signalling fit or data renormalization is performed.
