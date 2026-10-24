# Reproduction record — version 1.5.0, 2026-10-21

The current rooted Lean build and Python checks establish:

- 90 pytest executions, covering inherited finite checks, future-observation bridge, exact LP objectives, 60 one-dimensional hull comparisons, certificate tampering, resource/input refusals, source custody, axiom-report parsing and the review's context-validation regressions.
- All eleven deposited Lean modules build with Lean 4.33.1 and the pinned offline dependency bundle.
- All 98 explicitly named theorems are in the current census: 23 axiom-free and 75 using only approved foundational axioms. This includes 20 simplex and 10 error/correction results added in this edition.
- Every package-local environment declaration, including private/generated declarations, is checked by the full census. Its exact current count is in `lean4/full_axiom_report.txt`.
- The general finite real contextuality LP has attained primal and dual solutions. The standard-form equivalence, canonical maximum, contextuality alternative, ordered-field weak duality, and rational certificate bounds against all real competitors are formalized.
- Five exact outputs of the Python solver are checked numerically in Lean: classical 0, PR 2, near 4/5, triangle 2, and boundary 1/25000000. Generated-data check mode binds the solver, fixture data, and Lean source.

Approved axioms are exactly `propext`, `Quot.sound`, and `Classical.choice`. No custom axiom or unfinished proof is accepted. The named audit binds proof sources, certificate data, and build/dependency configuration to `lean4/source_hashes.json`; post-audit mutations are refused. The offline vendor manifest binds 2,318 dependency modules and 16,258 source/artifact files, including matching private/server/IR artifacts and upstream licenses.

The canonical paper rebuild regenerates the PDF from the explicit equation registry, checks ordered Markdown/TeX/UTF-8 formulas and rendering diagnostics, reseals both manifests and the deterministic ZIP, and verifies their agreement. Current artifact hashes and formula counts are in `render_receipt.json`. Conversion checks do not prove mathematical truth; the named Lean declarations carry the formal statements.

Standalone replay starts by extracting the release ZIP into an empty directory with no Lean cache, then supplies that same release ZIP beside its payload and runs `verify_deposit.py --lean` with all three test files. That command checks the archive/tree bijection, current document bindings, generated certificates, both current axiom reports, the vendor archive, and every extracted dependency file. Sensitivity probes omit a census entry and modify an audited proof, an extracted dependency, a payload file, and the bound manuscript; each must be refused. Temporary execution receipts stay outside the public package.

The executable Lean two-phase solver is structurally total for every finite typed input and pivot budget. Every accepted result is feasible and globally optimal; its exact shared-budget trace accounting and algebraic pivot invariants are formalized. Seventy-one complete Lean/Python execution comparisons agree on all primal/dual coordinates, exact values, pivot counts and refusal kinds, including budgets at completion boundaries, degenerate/redundant constraints, negative RHS, empty problems and the classical cycling example under Bland selection. Finite agreement is not universal refinement.

The error development proves an observation-radius bridge, nearest-distance Lipschitz comparison, uncertainty-adjusted witness, actual-trajectory recurrence, constant-residual enclosure, sufficient waiting windows and correction-capacity threshold implications. A continuous Duhamel enclosure is a supplied hypothesis of its scalar consequence; no validated ODE or quadrature theorem is asserted. Exact source snapshots and review limitations are recorded in `correction_review_sources.json`.

This release was checked using the repository's explicit Python 3.13.11 environment. The installed Windows Python 3.12 launcher could not start its registered Store executable; no Python 3.12 execution is claimed. The exact kernels use the standard library; pytest is needed for tests.

Universal Python-to-Lean refinement, unbudgeted Bland completeness, mathematical certification of infeasible/unbounded refusal labels, and a wall-clock or rational-bit-complexity bound remain open. The final checker is part of the certified successful-return path. A resource refusal is never a contextuality verdict. General rational-vertex existence, cryptographic integrity assumptions, imported logical metatheorems, and general Rust/Python equivalence are not formalized.
