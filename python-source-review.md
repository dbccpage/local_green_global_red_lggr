# Python source review

Revision: `2b3f102084a4e494c14d6e1d8df2c6de7094ae24`.

Focused review of shared linear algebra, homology, quantum-state and normalization boundaries in `code/python/src/`. The directory contains 883 Python files, including 400 named `test_*.py`. This is not an exhaustive audit of every module or mathematical claim. No repository files were changed.

## Findings, ordered by priority

### 1. High — DensityOperator accepts states with negative probabilities

Location: [qm/__init__.py:15](/home/vercel-sandbox/workspace/repos/github.com/dbccpage/theory_of_finite_quantum_mechanics/code/python/src/qm/__init__.py:15).

The constructor checks squareness, Hermiticity and trace one, but omits positive semidefiniteness. `DensityOperator(diag(2, -1))` is accepted. Its expectation against the valid projector `diag(0, 1)` is **−1**, and its purity is **5**. Neither is a valid density-state result. Existing positive-state coverage in `test_isomorphic_src_core.py` does not exercise this case.

**Suggested upgrade:** validate positive semidefiniteness over the exact rational/Gaussian field before admitting the state. Preserve singular positive semidefinite matrices, including pure states. The exact Schur-complement approach in `linear_algebra/cyclo_density.py::validate_psd` is a useful reference, but its cyclotomic representation needs adaptation; do not substitute floating-point eigenvalue thresholds. Protect the validated matrix from later mutation as part of the ownership design.

### 2. Medium — Equal GaussianRational values have incompatible hashes

Location: [scalars.py:151](/home/vercel-sandbox/workspace/repos/github.com/dbccpage/theory_of_finite_quantum_mechanics/code/python/src/linear_algebra/scalars.py:151).

`GaussianRational(1, 0) == 1 == Fraction(1)` is true, but the Gaussian value hashes as a tuple. Consequently, `{GaussianRational(1, 0): "one"}.get(1)` returns `None`, and a set retains both equal values. This violates Python's equality/hash contract and makes mixed exact-scalar keys unreliable.

**Suggested upgrade:** when the imaginary part is zero, return `hash(self.real)`; otherwise use a hash consistent with the supported equality domain. Keep the existing equality with integers and fractions. Also resolve mutable fields on this hashable type: use immutable storage or explicitly make instances unhashable if that API change is acceptable. Add dictionary/set interoperability coverage.

### 3. Medium — Negative matrix dimensions pass admission

Location: [matrix.py:76](/home/vercel-sandbox/workspace/repos/github.com/dbccpage/theory_of_finite_quantum_mechanics/code/python/src/linear_algebra/matrix.py:76).

`_dimension` accepts negative integers. The product-based length check then admits `ExactMatrix(-1, -1, [Fraction(1)])` and `ExactMatrix.zeros(-1, 0)`. The former fails later in `rank()`, after the invalid shape has already entered the API. Zero-area shapes also bypass the intended dimension boundary.

**Suggested upgrade:** reject dimensions below zero in the shared dimension validator, preserving valid zero-dimensional matrices and the existing float/bool refusals. The neighboring `bareiss_det._require_dimension` already rejects negatives. Do not introduce eager scalar validation as part of this fix: `ExactMatrix` deliberately retains entries for downstream scanners, as its module contract explains.

### 4. Medium — Caller mutation breaks the Carrier chain invariant

Locations: [carrier.py:134](/home/vercel-sandbox/workspace/repos/github.com/dbccpage/theory_of_finite_quantum_mechanics/code/python/src/homology/carrier.py:134), [carrier.py:150](/home/vercel-sandbox/workspace/repos/github.com/dbccpage/theory_of_finite_quantum_mechanics/code/python/src/homology/carrier.py:150).

The class promises `d1 ∘ d0 = 0` and verifies it at construction, but retains the caller's mutable matrix objects. Constructing a one-dimensional carrier with `d0=[0]`, `d1=[1]` succeeds. Calling `d0.set(0, 0, Fraction(1))` on the original input subsequently makes the composition nonzero and `carrier.dim_h1()` returns **−1**.

**Suggested upgrade:** define ownership explicitly. Store immutable matrix snapshots and prevent unrestricted replacement of invariant-bearing fields, or revalidate dimensions and the chain condition whenever computing derived results. A shallow copy alone does not prevent direct mutation through `carrier.d0`. Review similar matrix ownership in `ChainComplex` and `DensityOperator` when selecting the shared design.

**Boundary:** this reproduces invalid direct Carrier results. It does not establish a witness-verification bypass; the homology witness code rechecks the carrier.

### 5. Medium — Numerical Born lift returns invalid amplitudes for unchecked inputs and overflow

Location: [born_normalization.py:38](/home/vercel-sandbox/workspace/repos/github.com/dbccpage/theory_of_finite_quantum_mechanics/code/python/src/qm/born_normalization.py:38).

NaN weights pass the negative/positive-sum checks, infinite weights produce invalid divisions, and NaN phases pass the shape check. All return amplitudes that fail `verify_born_normalization`. Even finite positive weights `[1e308, 1e308]` overflow their sum and return zero amplitudes rather than a unit vector. Thus the issue also affects inputs that satisfy finiteness and nonnegativity.

**Suggested upgrade:** require finite weights and phases; normalize finite nonnegative weights using scaling by the largest weight before summation, with explicit empty/all-zero handling. Validate the result or raise an informative exception. Extend the property tests to cover extreme magnitudes and refusal cases; current generated weights exclude NaN/Inf and cap magnitudes well below overflow.

## Further upgrades

- **Make test discovery explicit.** Root `pyproject.toml` limits default collection to `code/python/tests`. The 400 source-local `test_*.py` files are not collected directly by that default. Inventory which are exercised through other suites before adding source paths or a separate CI job; adding everything blindly can introduce import-name collisions. This is a discovery gap, not a claim that all those behaviors lack coverage.
- **Declare reproducible test dependencies.** The root project has no default dependencies. The documented test collection needed pytest, PyYAML, SymPy, NumPy, SciPy and Hypothesis in this environment. Declare a test/development extra or environment and verify it from a fresh install. Pytest also warned that `asyncio_mode` is unknown because pytest-asyncio was absent; decide whether to declare that plugin or remove unused configuration.
- **Reduce eager imports.** Importing shared source APIs pulls in `qm` campaigns and numerical dependencies through package initializers. Consider lazy loading optional campaign modules so exact arithmetic can be used without importing the entire numerical stack. Preserve documented exports and alias behavior when changing initialization.

## Verification

Environment: Python 3.14.4; pytest 9.1.1; NumPy 2.5.4; SciPy 1.18.1; SymPy 1.14.0; PyYAML 6.0.3; Hypothesis 6.170.8. Real source imports were used, with no stubs or services.

- **54 existing tests passed** across `test_scalars.py`, `test_matrix.py`, `test_isomorphic_src_core.py`, `test_carrier.py`, `test_carrier_contract.py`, `test_chain_complex.py`, `test_witness.py`, `test_exact_carrier.py`, and `test_born_normalization_lift.py`.
- **Five independent probes passed**, confirming the defective outcomes above and positive controls. Passing these probes means the defects were reproduced; it does not mean the implementation is correct.
- **2,663 tests collected successfully** from `code/python/tests` after installing missing dependencies. Collection is not execution. The full suite and source-local suites were not run.
- Collection and the selected test run each emitted the unknown `asyncio_mode` configuration warning.

Reproduction, from the repository root:

```bash
.venv/bin/python /path/to/python-review-probes.py .
.venv/bin/python -I -X utf8 -m pytest -q code/python/tests/test_scalars.py code/python/tests/test_matrix.py code/python/tests/test_isomorphic_src_core.py code/python/tests/test_carrier.py code/python/tests/test_carrier_contract.py code/python/tests/test_chain_complex.py code/python/tests/test_witness.py code/python/tests/test_exact_carrier.py code/python/tests/test_born_normalization_lift.py
```

The accompanying `python-review-probes.py` preserves the executable reproductions. No fixes were applied.
