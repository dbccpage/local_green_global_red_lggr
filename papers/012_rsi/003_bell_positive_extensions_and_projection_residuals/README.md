# Bell's Theorem as a Positive-Extension Obstruction

Version 0.13.0, 24 October 2026. A separate research draft under Projection Obstruction.

The manuscript develops Bell nonlocality as failure of a positive local extension, with a distinct comparison to task ambiguity under retained evidence. It preserves setting independence, the distinction from product-state correlation, and the direction of all norm bounds.

Install the dependencies in `requirements.txt` and Lean 4.35.0, and set `ELAN_HOME` to the Lean installation. Run `python verify_deposit.py` from this directory. The verifier checks all payload bytes, freshly compiles the Bell Lean sources, compares the complete axiom census, runs exact certificate tests, reruns the finite LP/matrix reproduction, and directly executes the notebook's Python cells. It does not require sibling packages or a network connection after these prerequisites are installed. Python 3.12 was used for this release.

The 656 named Lean theorems cover the finite stochastic positive-extension equivalence, arbitrary-carrier positive averaging and probability-integral models, quantum operator and pure/finite-mixture state bounds, arbitrary finite-dimensional density-matrix and binary-POVM conversions with actual Born tables and tensor lifts, finite Hermitian trace-norm measurement contraction, explicit separable mixtures and local models, partial traces and the full state-to-behavior bound, and conditional dynamical witness bounds, an exact complex two-qubit saturation example, classical CHSH bounds and uncertainty-adjusted witnesses, attained repair and signed-negative-mass LP duality, finite polyhedral elimination, intrinsic tangent-cone and quadratic remainder bounds, exact finite scalar minimax, and evidence-preserving recursion. Their exact assumptions and the remaining unformalized results are listed in `docs/formalization.md`.

- `code/bell_certificates.py`: exact uniform-setting CHSH primal/dual certificate checker.
- `code/tests/`: 60 tests, including forged witnesses, invalid extensions, and uncertainty that removes the margin.
- `code/reproduce_examples.py`: supplied finite calculation, including 14 numerical LP solves.
- `docs/source_inputs/`: exact original user draft and the earlier reviews and six additional GLM inputs.
- `docs/source_custody.json`: input hash, editorial changes, and primary sources checked.
- `lean4/Bell/`: 55 proof modules; `lean4/Census.lean` requests all 656 named theorems.
- `axiom_census.json`: fresh theorem dependencies and source hashes; no custom axioms.
- `lean4/vendor/`: pinned offline Mathlib closure, sources, licenses, and file manifest.
- `tools/replay_lean.py`: fresh proof build and census replay; dependency cache is excluded from the archive.
- `claim_ledger.json`, `docs/claim_code_map.yaml`, and `docs/formalization.md`: mathematical claims, proof mappings, and boundaries.

Build PDF/TeX with `python scripts/build_paper_artifacts.py` (Pandoc, XeLaTeX and the named fonts required). Build or check the deterministic archive with `python tools/package.py --build` or `python tools/package.py`. Packaging is not publication or an experimental Bell test.

The supplied review and exact simplex are assessed in `docs/review_assimilation.md`. The verifier also replays its 39 checks and separately validates 15 returned primal/dual certificates. The simplex itself is not claimed Lean-verified.

Version 0.8.0 added the real-parameter CHSH/Mermin signed-mass optima, contextual-fraction packing semantics, exact family comparisons, an explicit CF>2N counterexample and reversed ordering, and the constructive bound CF <= (m-1)N. All real competing extensions are covered.

- Run python code/contextual_fraction.py for 78 exactly checked certificates.
- Run python tools/generate_comparison_fixture.py for read-only Lean/Python fixture binding.
- Optional: python code/generate_contextual_fraction_certificates.py reruns SciPy candidate search followed by exact checks. Only --write regenerates stored data.
- Original GLM inputs remain byte-preserved under docs/source_inputs/glm_2026_10_23. Their historical solver/log assertions are not release verification.

The earlier three-party counterexample is no-signalling; quantum realizability is not established. The Mermin quantum endpoint is v=1, distinct from the full-parity G box. The original Python simplex is not claimed Lean-verified.

Version 0.9.0 adds quantum-restricted CHSH/GHZ family comparisons and an explicit GHZ evolution with exact and uncertainty-delayed exit windows. Run `python code/quantum_evolution.py` for the independent matrix-exponential/LP replay. Read `docs/contextuality_side_note.md` for an introduction and assessment of the research level. The census now covers 656 named theorems in 55 modules.

Version 0.10.0 resolves the quantum factor-two question negatively: the full 3x3 Bell experiment on one entangled qubit pair has CF=4N_min>2N_min. Run python code/chained_quantum.py for exact Q(sqrt(3)) Born and optimality certificates. This does not prove a universal coefficient-four upper bound.

Version 0.11.0 disproves the factor-four conjecture with a complete rational 5x5 quantum example: CF=698/925 and N_min=167/925. Arbitrary-size cycle parity quotients have ratio 2n-2, whereas complete equally spaced chains obey a bounded-tail CHSH estimate. Version 0.12.0 resolves that question with a different, smoothed Gram family. Run `python code/chain_comparisons.py` for the exact certificate and cycle reconstruction checks. Cycle reconstruction and lifting are now formalized; their exact coverage is in docs/formalization.md.

Optional: `python tools/explore_complete_chains.py` reproduces the floating-point complete-table comparison in Section 8.5 for two through seven settings. Those solver values are exploratory and separate from the exact rational certificate.

`python tools/verify_five_fixture.py` independently checks the exact binding between the JSON certificate vectors and Lean's integer data without rewriting either file; it is included in the default verifier.

Version 0.12.0 constructs complete quantum tables with CF/N_min >= 3k-4+3/(k+1), for k^2 settings per party. Run `python code/smoothed_gram.py` for exact complete-table certificates and `python code/smoothed_quantum.py` for the independent Clifford/Born check. Version 0.13.0 closes the end-to-end Lean construction: cyclic profiles, general Clifford matrices, density/POVM Born tables, actual CF witness and attained positive N_min. Section 8.7 and docs/continuum_shadow_note.md distinguish finite tables from selected Archimedean scalar shadows. The title, subtitle, author, date and version are centered, with version last.
