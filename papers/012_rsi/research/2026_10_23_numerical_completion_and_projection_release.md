# Completed numerical repair and projection extensions

Verification date: 2026-10-23. Both RSI editions and all three projection packages were rebuilt and checked from clean extractions.

The repaired quantum library passed **712 tests**, including all three earlier failures, all ten previously unfinished cases, and three new admission-boundary regressions. Five quantum integration binaries passed **57 tests**. The rebuilt native budget host passed all **24 gateway and memory tests**.

Choi admission now checks exact PSD after losslessly lifting finite binary entries. Hamiltonian floating-point evolution has its own tolerance-checked numerical propagator; zero-defect admission remains strict and norm drift is retained.

| Package | Edition | Python tests (source / extracted) | Fresh Lean scope |
|---|---|---|---|
| RSI A | 1.2.2 | 204 / 204 | 109 named theorems; 577 package declarations |
| RSI B | 1.8.2 | 170 / 170 | 161 named theorems; 941 package declarations |
| PO-000 | 6.9.19 | 1075 / 1075 | Source scan only |
| PO-033 | 1.1.0 | 161 / 161 | 11 conditional abstract declarations |
| PO-034 | 0.2.0 | 155 / 155 | 7 conditional abstract declarations |

All reported tests passed with no failures. PO-000 excludes eleven native-integration tests under its declared standalone profile. The 95 complete Lean/Python simplex comparisons also passed. RSI censuses retain the same theorem statements and permit only standard Lean foundations.

PO-000 §5.18 adds uncertainty-aware onset and correction windows. PO-033 §3.5 accounts for piecewise trajectories, integration defects and finite correction jumps. PO-034 §4.3 proves a product-defect perturbation bound of (k+1) times density-state trace-norm uncertainty and transfers it through a declared observation map. Exact scalar witnesses include accepted and rejected boundary examples. These new continuous results are written proofs, not new Lean declarations.

## Rebuilt archives

- [000_relational_reasoning_and_rsi_impossibility_2026-10-23.zip](C:/Users/a343o/source/repos/the_symbol_game/omega_engine_atlas/coda_atlas/F004_papers/012_rsi/000_relational_reasoning_and_rsi_impossibility/000_relational_reasoning_and_rsi_impossibility_2026-10-23.zip) — version 1.2.2; SHA-256 `1698d7b0c72a8328dec46f3f334e4a2147e0de7de49fba26287813a7a66c83d8`.
- [001_contextual_prediction_and_self_certification_2026-10-23.zip](C:/Users/a343o/source/repos/the_symbol_game/omega_engine_atlas/coda_atlas/F004_papers/012_rsi/001_contextual_prediction_and_self_certification/001_contextual_prediction_and_self_certification_2026-10-23.zip) — version 1.8.2; SHA-256 `5766c177f3cb489e2a8d011f29790ee637a5fa321b7d31337765d2fd2ec0906d`.
- [projection_obstruction_v6.9.19.zip](C:/Users/a343o/source/repos/the_symbol_game/omega_engine_atlas/coda_atlas/F004_papers/002_projection_obstruction/000_projection_obstruction/dist/projection_obstruction_v6.9.19.zip) — version 6.9.19; SHA-256 `566a5580223fa1abc4ccff50ba101a739a753d89d70f81dfaed9ac72ae9be13a`.
- [certified_adaptive_quantum_dynamics_2026-10-23.zip](C:/Users/a343o/source/repos/the_symbol_game/omega_engine_atlas/coda_atlas/F004_papers/002_projection_obstruction/033_certified_adaptive_quantum_dynamics/certified_adaptive_quantum_dynamics_2026-10-23.zip) — version 1.1.0; SHA-256 `b02d71d2082d7ee508cc38f989ed716ac957c826e6867771af2c898ec54dcebe`.
- [034_higher_cell_cochain_projection_and_retraction_dynamics_2026-10-23.zip](C:/Users/a343o/source/repos/the_symbol_game/omega_engine_atlas/coda_atlas/F004_papers/002_projection_obstruction/034_higher_cell_cochain_projection_and_retraction_dynamics/034_higher_cell_cochain_projection_and_retraction_dynamics_2026-10-23.zip) — version 0.2.0; SHA-256 `f4c986188ad12b4501f05e131b942270231c393a3f8af9008443fef23fef8c11`.

## Evidence and limits

The adjacent JSON binds archives, commands, source hashes, native executable, named case completion, and extraction checks. Each RSI archive includes current numerical verification, task-relative Rust patches, repaired source snapshots, command logs, package XML, gateway XML and refreshed axiom reports. Historical failures and incomplete runs remain preserved.

The fresh full Rust library run covers omega_quantum_physics, not every crate in the monorepo. Gateway transport is synthetic; no new live-provider trial was run. Source Lean replay for both RSI papers is fresh; a second cold Lean rebuild from the RSI extractions is not claimed. Projection packages PO-033/034 passed fresh Lean and notebook replay after extraction; PO-000 did not compile Lean in this extension.
