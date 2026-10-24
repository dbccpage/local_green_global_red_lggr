# Relational Reasoning, Memory, and Embedded Knowledge

Jeremy H. Carroll. Version 1.2.3, 2026-10-23.

The [manuscript](relational_reasoning_and_rsi_impossibility_monograph.md) characterizes task-relative knowledge, exact recovery, future-preserving memory and bounded recursive improvement. Agents, instruments, memories and evaluators are modeled within the world. The earlier finite-carrier proofs are retained with their exact scope; constructive memory results replace blanket interpretations of impossibility.

New Lean modules prove record-relative factivity and introspection, recovery through fibers, maximal future equivalence, concrete encoded-memory updates, checked append and recall, and invariant preservation by an enforced gate. The finite Python experiment is in [code/memory_machine.py](code/memory_machine.py). The source-bound persistent implementation and live agent experiment are documented in [docs/live_memory.md](docs/live_memory.md). Exact scalar and finite query experiments are in [code/finite_limits.py](code/finite_limits.py). The [companion paper 001](../001_contextual_prediction_and_self_certification/README.md), version 1.8.2, supplies quantitative minimax, loss-transfer and query-budget theorems as well as contextuality and simplex certificates.

Lean 4.35.0 is pinned; this package needs no Mathlib or sibling source. Memory and finite-limit kernels use the standard library. The cochain solver requires NumPy and SciPy (declared wheel dependencies); tests need pytest. Native metadata parity requires rustc. Rendering requires Pandoc, XeLaTeX and pdftotext. Documentation uses CC BY 4.0; code retains PolyForm Noncommercial 1.0.0.

```text
python -m pip install .
python -m pytest code/tests -q
python tools/replay_lean_axiom_census.py --replay
python tools/replay_full_axiom_census.py --check
python scripts/paper_spine.py verify
python verify_deposit.py --lean
python tools/rebuild_release.py --check
```

After editing source, explicitly reconcile equations in the math spine, rebuild the proof modules, regenerate the named and full censuses, then run the canonical repository command:

```text
python -m omega_engine_research_papers.use_cases.paper_edition.cli rebuild --paper-path omega_engine_atlas/coda_atlas/F004_papers/012_rsi/000_relational_reasoning_and_rsi_impossibility --verbose
```

The standalone equivalents are `python tools/replay_lean_axiom_census.py --write`, `python tools/replay_full_axiom_census.py`, `python scripts/build_pdf.py`, and `python tools/rebuild_release.py`. The release ZIP includes the rendered manuscript, proofs, checkers, source catalog, censuses and manifests. Current source mappings are in [docs/embedded_research.md](docs/embedded_research.md) and preceding-edition replay evidence in [docs/embedded_verification.json](docs/embedded_verification.json). Historical manuscript and ledger bytes are retained as `docs/pre_integration_*`; their extrapolations are superseded by this edition. No DOI or public deposit is asserted.

Persistent memory, restart evidence and its eight Lean statements are described in [docs/live_memory.md](docs/live_memory.md). Current edition checks are in [docs/live_memory_verification.json](docs/live_memory_verification.json); `embedded_verification.json` records the preceding edition.

The preceding numerical verification recorded all 712 quantum-library tests passing in release mode, with no failures, ignored cases or filtered cases. This includes the three prior numerical failures, all ten previously unfinished MUB tests, and three new admission-boundary regressions. Exact PSD of the supplied binary Choi matrix replaces a rounded eigenvalue-sign decision. Floating-point Hamiltonian evolution uses a separate tolerance-checked numerical propagator; exact admission remains strict, and numerical evolution retains norm drift. The rebuilt native budget host passes all 24 gateway-and-memory tests, including both previously blocked cases; five quantum integration binaries pass 57 tests. These are scoped checks of the earlier recorded source snapshot, not fresh native reruns in this edition. The earlier multi-crate audit remains historical, and these synthetic gateway tests add no new live model trial or universal implementation-refinement proof.

See [completed numerical and gateway verification](docs/numerical_verification.md).

The independent October 23 review is reconciled in
[the finding-by-finding response](docs/review_response_2026_10_23.md).
The cochain solver reconstructs and independently checks exact rational
certificates; closure alone never licenses an exactness claim. The transition
CLI delegates to the same modules as the tests. Its numeric threshold policy
checks `internal_eval >= N` before report collision, so score units are part of
the declared model. The reported `N+1` transition ceiling is loose; a fixed
N-report interface forces a repeated report by transition index N.

`rsi-transitions --json` (or `python -m rsi_transition_harness --json`) runs the
packaged examples. `rsi-memory` provides the local persistent-memory interface.
Rust results are explicitly EIS metadata/digest parity, not obstruction replay
or authenticated verifier independence. The identifier policy rejects Unicode
and unsupported wire inputs. The asynchronous distribution uses controlled
synthetic defect injection, including an age penalty for equal content.

To test the installed wheel in a fresh virtual environment outside the source
tree, run `python tools/verify_installed_wheel.py`. This builds with isolated
build dependencies and installs declared dependencies from the configured package index;
`--wheelhouse PATH` instead uses supplied setuptools/wheel and NumPy/SciPy wheels.
The standalone archive includes source, tests and resources but not Python,
NumPy/SciPy binaries, rustc, Lean 4.35.0 or rendering tools. Clean extraction
checks use these declared installed prerequisites, no sibling repository source.
The prior 712/57/24 Rust results above are preserved earlier evidence, not new
executions in version 1.2.3.
