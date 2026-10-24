# Test Infrastructure: LGGR Volume VIII Advancement

**Status:** Published  
**Track:** Independent Opaque-Box E2E Testing  
**Framework:** Python Standard Library (`unittest`, `subprocess`, `json`, `fractions`, `pathlib`)  
**AuthorityEffect:** None  

---

## 1. Executive Summary & Purpose

This document defines the test architecture, methodology, and verification protocols for the Local Green, Global Red (LGGR) Volume VIII advancement. 

The objective of this test infrastructure is to provide an independent, opaque-box, requirement-driven verification harness covering:
1. Online, streaming detection of composability obstructions (report-fiber collisions, evaluator defects $\Delta_E \in \{-1, 0, 1\}$, and cycle closure $\ell^1$ repair distances) in `lggr`.
2. Standalone CLI and zipapp execution (`lggr_witness_audit.pyz selftest`, `stream`).
3. Multi-agent swarm benchmark schemas, empirical defect rates, and offline deterministic replay.
4. Practitioner cookbooks, documentation synchronization, manifest integrity, and repository hygiene.

Strict adherence to the Claim Hygiene Rule is maintained across all test specifications, assertions, and docstrings.

---

## 2. Test Architecture & Directory Layout

The testing track operates with zero external dependencies, utilizing exclusively the standard Python distribution:

```text
lggr/
├── tests/
│   ├── test_cli.py              # Unit tests for legacy CLI subcommands
│   ├── test_descent.py          # Unit tests for batch descent analysis
│   ├── test_linear.py           # Unit tests for exact rational LP and cochains
│   ├── test_transport.py        # Unit tests for chain maps and transport
│   ├── test_witnesses.py        # Unit tests for step witnesses and budget drift
│   ├── test_streaming.py        # M1 unit tests for streaming runtime monitors
│   ├── test_live_benchmarks.py  # M2 unit tests for offline benchmark replay
│   └── test_e2e_suite.py        # Comprehensive 4-tier independent E2E test suite
├── receipts/                    # Machine-readable JSON receipts and replay traces
│   └── live_benchmarks/         # Recorded deterministic replay artifacts
├── TEST_INFRA.md                # This specification
└── TEST_READY.md                # Test execution readiness report and checklist
```

### Execution Protocol
The entire test suite is executable via standard Python tooling:
```bash
python -m unittest tests/test_e2e_suite.py -v
```

---

## 3. Feature Inventory & Interface Contracts

The testing harness covers nineteen features (F01–F14, F20–F24) specified in `PROJECT.md § Feature Inventory`:

| Feature ID | Feature Name | Target Scope | Milestone | Interface Contract / Expected Behavior |
|---|---|---|---|---|
| **F01** | `StreamingFiberMonitor` | `lggr.streaming` | M1 | Incremental state observation; returns `{"status": "OK" \| "REPORT_INSUFFICIENT", "colliding_pair": ...}`. |
| **F02** | `StreamingAuditMonitor` | `lggr.streaming` | M1 | Prefix-by-prefix $G_1$–$G_4$ gluing; computes running $\Delta_E \in \{-1, 0, 1\}$ (`NGD`, `ZDR`, `PGD`) and `every_prefix` alerts. |
| **F03** | `StreamingCochainMonitor` | `lggr.streaming` | M1 | Incremental directed edges; cycle closure $(D_1 h)_C \ne 0$ detection and rational $\ell^1$ repair witness $z$. |
| **F04** | Zipapp `selftest` subcommand | CLI & `.pyz` | M1 | `python lggr_witness_audit.pyz selftest` exits code 0 and emits `schema: "lggr.selftest.v1"`. |
| **F05** | Zipapp `stream` subcommand | CLI & `.pyz` | M1 | `python -m lggr stream --monitor {fiber,audit,cochain}` processes line-delimited JSON events. |
| **F06** | Rebuilt `lggr_witness_audit.pyz` | Root package | M1 | Executable zip archive containing valid `__main__.py` and packaged `lggr/` modules. |
| **F07** | Streaming Unit Tests | `tests/` | M1 | `test_streaming.py` and `test_cli.py` pass 100% under `unittest discover`. |
| **F08** | Zero-dep OpenRouter loader | Benchmarks | M2 | Resolves API key and model from environment or sibling `.env` without secret leaks. |
| **F09** | Empirical NGD/ZDR/PGD rates | Benchmarks | M2 | Calculates empirical LPR, GPR, NGD rate, ZDR rate, PGD rate, mean defect, and EGD. |
| **F10** | Live Test 1: Fiber collision | Benchmarks | M2 | Online detection of boundary-insufficient summary collision across multi-stage agent handoffs. |
| **F11** | Live Test 2: Prefix threshold breach | Benchmarks | M2 | Online early-stopping triggered on `every_prefix` budget breach before endpoint. |
| **F12** | Live Test 3: Incremental 1-cochain | Benchmarks | M2 | Online detection of cyclic inconsistency in 3-agent review topology with rational $\ell^1$ distance. |
| **F13** | Live Test 4: Composable LGGG | Benchmarks | M2 | Certification of composable LGGG ($\Delta_E = 0$) under boundary-sufficient schema. |
| **F14** | Offline deterministic replay | `receipts/` | M2 | Offline replay of recorded trace artifacts without external network requests. |
| **F20** | Practitioner Cookbooks | `cookbooks/` | M5 | Four standalone runnable Python scripts (`01_` through `04_`) covering streaming integration. |
| **F21** | Monograph Index update | `papers/` | M5 | `papers/local_green_global_red_monograph_index.md` indexed with Volume VIII entry. |
| **F22** | Cloned Wiki sync | Wiki repo | M5 | Wiki pages created without `\operatorname` macros, matching repository documentation. |
| **F23** | Git commit & push | VCS | M5 | Working tree clean and properly tracked in git. |
| **F24** | Manifest verification | Root | M5 | `MANIFEST.sha256` checksums validate against all tracked distribution files. |

---

## 4. Four-Tier Systematic Testing Methodology

The test suite is structured into four distinct, progressive tiers:

```text
┌─────────────────────────────────────────────────────────────────┐
│ Tier 4: Real-World Swarm Application Scenarios (>= 5 Scenarios) │
├─────────────────────────────────────────────────────────────────┤
│ Tier 3: Cross-Feature Interactions (Pairwise Combinations)      │
├─────────────────────────────────────────────────────────────────┤
│ Tier 2: Boundary & Corner Cases (>= 5 Cases per Feature)        │
├─────────────────────────────────────────────────────────────────┤
│ Tier 1: Feature Coverage (>= 5 Cases per Feature)               │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 Tier 1: Feature Coverage (>= 5 Test Cases per Feature)

For each feature F01–F14 and F20–F24, at least 5 targeted unit/functional test cases verify primary functional behavior:

- **F01 (`StreamingFiberMonitor`)**:
  - `test_f01_01_initial_state`: Verify initialization with scope ID and empty state index.
  - `test_f01_02_single_observation_ok`: Observe single state; verify status `OK` / `COMPOSABLE_LGGG`.
  - `test_f01_03_distinct_reports_ok`: Observe multiple states with distinct reports; verify no collision.
  - `test_f01_04_identical_report_and_query_ok`: Observe repeated report with matching query; verify no collision.
  - `test_f01_05_collision_detected`: Observe identical report with differing query; verify immediate `REPORT_INSUFFICIENT` transition and colliding pair emission.

- **F02 (`StreamingAuditMonitor`)**:
  - `test_f02_01_initialization`: Initialize with `BudgetPolicy` and baseline state; verify initial counters.
  - `test_f02_02_valid_step_g1_gluing`: Step with valid chained source/target; verify $G_1$ gluing holds.
  - `test_f02_03_running_evaluator_defect_zdr`: Step with concordant local/global checks; verify $\Delta_E = 0$ (`ZDR`).
  - `test_f02_04_running_evaluator_defect_ngd`: Step where local check is green but global sample is red; verify $\Delta_E = -1$ (`NGD`).
  - `test_f02_05_running_evaluator_defect_pgd`: Step where local check is red but global sample is green; verify $\Delta_E = +1$ (`PGD`).

- **F03 (`StreamingCochainMonitor`)**:
  - `test_f03_01_initialization`: Verify empty graph and components on initialization.
  - `test_f03_02_tree_edge_open`: Add tree edges without cycle; verify status `OPEN_TREE` with no cycle.
  - `test_f03_03_cycle_closure_consistent`: Add chord closing a zero-defect cycle; verify $(D_1 h)_C = 0$ and repair distance 0.
  - `test_f03_04_cycle_closure_inconsistent`: Add chord closing an inconsistent cycle; verify $(D_1 h)_C \ne 0$ and nonzero $\ell^1$ repair distance.
  - `test_f03_05_dual_witness_certification`: Verify dual witness $z$ satisfies annihilator constraint and matches primal repair value.

- **F04 (Zipapp `selftest` Subcommand)**:
  - `test_f04_01_cli_selftest_exit_zero`: Run `python -m lggr selftest`; verify returncode is 0.
  - `test_f04_02_cli_selftest_schema`: Verify output contains `schema: "lggr.selftest.v1"`.
  - `test_f04_03_cli_selftest_status`: Verify output status indicates `PASS`.
  - `test_f04_04_cli_selftest_modules_listed`: Verify output lists core modules checked.
  - `test_f04_05_cli_selftest_json_validity`: Verify stdout is strictly parseable canonical JSON.

- **F05 (Zipapp `stream` Subcommand)**:
  - `test_f05_01_stream_help`: Verify `--help` displays usage for stream subcommand.
  - `test_f05_02_stream_fiber_mode`: Pipe observations into `stream --monitor fiber`; verify receipt output.
  - `test_f05_03_stream_audit_mode`: Pipe step witnesses into `stream --monitor audit`; verify receipt output.
  - `test_f05_04_stream_cochain_mode`: Pipe edges into `stream --monitor cochain`; verify receipt output.
  - `test_f05_05_stream_invalid_monitor_rejected`: Pass invalid monitor name; verify exit code 2 and input error receipt.

- **F06 (Rebuilt `lggr_witness_audit.pyz`)**:
  - `test_f06_01_zipapp_exists`: Verify `lggr_witness_audit.pyz` exists as a file.
  - `test_f06_02_zipapp_executable_demo`: Run `python lggr_witness_audit.pyz demo`; verify returncode 0.
  - `test_f06_03_zipapp_executable_selftest`: Run `python lggr_witness_audit.pyz selftest`; verify returncode 0.
  - `test_f06_04_zipapp_internal_main`: Inspect zip archive; verify root `__main__.py` exists.
  - `test_f06_05_zipapp_module_contents`: Inspect zip archive; verify `lggr/__init__.py`, `lggr/streaming.py`, etc., exist.

- **F07 (Streaming Unit Tests)**:
  - `test_f07_01_test_streaming_file_present`: Verify `tests/test_streaming.py` exists.
  - `test_f07_02_test_streaming_discovery`: Run discovery for `tests/test_streaming.py`; verify clean execution.
  - `test_f07_03_test_cli_streaming_cases`: Verify `tests/test_cli.py` includes tests for `selftest` and `stream`.
  - `test_f07_04_unit_test_suite_all_pass`: Verify full suite `python -m unittest discover -s tests` passes.
  - `test_f07_05_optimized_execution`: Verify test suite passes under `python -O`.

- **F08 (Zero-dep OpenRouter Loader)**:
  - `test_f08_01_env_resolver_present`: Verify standard library credential loader function exists.
  - `test_f08_02_dotenv_parser_standard_library`: Parse mock `.env` format without third-party `python-dotenv`.
  - `test_f08_03_key_stripping_and_quotes`: Verify quoted and raw values parsed correctly.
  - `test_f08_04_missing_key_graceful_handling`: Verify clear refusal or sentinel return when `.env` is absent.
  - `test_f08_05_zero_leakage_in_exceptions`: Verify error handling suppresses API key strings from exception logs.

- **F09 (Empirical NGD/ZDR/PGD Rates)**:
  - `test_f09_01_rate_calculator_zero_traces`: Verify handling of empty trace collections.
  - `test_f09_02_all_zdr_rate_computation`: Ingest traces where all $\Delta_E = 0$; verify ZDR = 1.0, NGD = 0.0, PGD = 0.0.
  - `test_f09_03_all_ngd_rate_computation`: Ingest traces where all $\Delta_E = -1$; verify NGD = 1.0, mean defect = -1.0.
  - `test_f09_04_mixed_distribution_rates`: Ingest balanced traces; verify exact rational rate proportions.
  - `test_f09_05_empirical_goodness_differential`: Verify EGD metric calculation ($EGD = \text{GPR} - \text{LPR}$).

- **F10 (Live Test 1: Fiber Collision Detection)**:
  - `test_f10_01_test1_trace_schema`: Verify Test 1 trace schema adherence (`lggr.trace_replay.v1`).
  - `test_f10_02_test1_online_step_arrival`: Ingest Test 1 steps sequentially into `StreamingFiberMonitor`.
  - `test_f10_03_test1_collision_detection_step`: Confirm collision fires at the declared step index.
  - `test_f10_04_test1_receipt_structure`: Verify colliding pair and report content in receipt.
  - `test_f10_05_test1_transition_to_obstructed`: Confirm monitor status transitions to `OBSTRUCTED_LGGR`.

- **F11 (Live Test 2: Prefix Threshold Breach)**:
  - `test_f11_01_test2_trace_schema`: Verify Test 2 trace schema adherence.
  - `test_f11_02_test2_every_prefix_monitoring`: Feed multi-step trajectory under `every_prefix` policy.
  - `test_f11_03_test2_midflight_early_stop`: Verify alert fires on prefix drift exceedance before trajectory end.
  - `test_f11_04_test2_endpoint_contrast`: Contrast with `endpoint` scope where the same trajectory would be unflagged.
  - `test_f11_05_test2_alert_receipt_payload`: Verify step index, cumulative delta, and threshold in alert receipt.

- **F12 (Live Test 3: Incremental 1-Cochain)**:
  - `test_f12_01_test3_trace_schema`: Verify Test 3 trace schema adherence.
  - `test_f12_02_test3_three_agent_edges`: Add edges A->B, B->C, C->A incrementally.
  - `test_f12_03_test3_cycle_detection`: Verify cycle closure identified exactly upon edge 3 arrival.
  - `test_f12_04_test3_closure_defect`: Verify $(D_1 h)_C$ defect calculated exactly.
  - `test_f12_05_test3_repair_distance_and_dual`: Verify primal $\ell^1$ repair cost and dual witness match.

- **F13 (Live Test 4: Composable LGGG)**:
  - `test_f13_01_test4_trace_schema`: Verify Test 4 trace schema adherence.
  - `test_f13_02_test4_boundary_sufficient_schema`: Verify typed schema prevents report-fiber collision.
  - `test_f13_03_test4_streaming_execution`: Feed all steps into `StreamingFiberMonitor` and `StreamingAuditMonitor`.
  - `test_f13_04_test4_zero_defect_throughout`: Verify $\Delta_E = 0$ (`ZDR`) at every step.
  - `test_f13_05_test4_composable_certification`: Verify final contract status is `COMPOSABLE_LGGG`.

- **F14 (Offline Deterministic Replay)**:
  - `test_f14_01_receipts_directory_exists`: Verify `receipts/live_benchmarks/` exists.
  - `test_f14_02_replay_without_network`: Ingest replay artifacts with network sockets disabled; verify success.
  - `test_f14_03_replay_hash_determinism`: Recompute receipt digests from replayed inputs; verify exact match.
  - `test_f14_04_tampered_replay_detection`: Introduce modification into replay trace; verify mismatch detection.
  - `test_f14_05_replay_cli_command`: Verify `python -m lggr replay` verifies replay receipts.

- **F20 (4 Practitioner Cookbooks)**:
  - `test_f20_01_cookbook_01_exists_and_runs`: Execute `cookbooks/01_online_fiber_monitoring.py`; returncode 0.
  - `test_f20_02_cookbook_02_exists_and_runs`: Execute `cookbooks/02_streaming_budget_audit.py`; returncode 0.
  - `test_f20_03_cookbook_03_cochain_cycle_repair.py`: Execute `cookbooks/03_cochain_cycle_repair.py`; returncode 0.
  - `test_f20_04_cookbook_04_swarm_runtime_guard.py`: Execute `cookbooks/04_swarm_runtime_guard.py`; returncode 0.
  - `test_f20_05_cookbooks_claim_hygiene`: Scan all cookbook scripts for Claim Hygiene Rule compliance.

- **F21 (Monograph Index Update)**:
  - `test_f21_01_monograph_index_exists`: Verify `papers/local_green_global_red_monograph_index.md` exists.
  - `test_f21_02_volume_viii_entry_present`: Verify Volume VIII section heading and description are present.
  - `test_f21_03_claim_ledger_reference`: Verify Volume VIII entry references claim ledger and companion code.
  - `test_f21_04_monograph_index_claim_hygiene`: Scan monograph index for forbidden words.
  - `test_f21_05_monograph_index_mathjax`: Scan monograph index for disallowed `\operatorname` macros.

- **F22 (Cloned Wiki Sync)**:
  - `test_f22_01_wiki_volume_viii_page`: Verify Volume VIII wiki page markdown exists in wiki workspace.
  - `test_f22_02_wiki_practitioner_page`: Verify Practitioner Guide markdown exists in wiki workspace.
  - `test_f22_03_wiki_mathjax_compliance`: Verify zero occurrences of `\operatorname` in all wiki pages.
  - `test_f22_04_wiki_sidebar_updated`: Verify `_Sidebar.md` links Volume VIII and practitioner guide.
  - `test_f22_05_wiki_claim_hygiene`: Scan wiki markdown files for Claim Hygiene Rule compliance.

- **F23 (Git Commit & Push Readiness)**:
  - `test_f23_01_git_status_clean`: Check `git status --porcelain` is clean or tracks expected changes.
  - `test_f23_02_gitignore_secrets`: Verify `.gitignore` contains `.env`, `*.env`, and cache entries.
  - `test_f23_03_zero_api_keys_in_repo`: Scan repository tree for potential leaked API key patterns.
  - `test_f23_04_wiki_git_clean`: Verify wiki repository git workspace is in a valid tracked state.
  - `test_f23_05_no_untracked_temp_files`: Verify absence of temporary scratch files (`temp.md`, `run_rip_*`).

- **F24 (Manifest Verification)**:
  - `test_f24_01_manifest_file_exists`: Verify `MANIFEST.sha256` exists at repository root.
  - `test_f24_02_manifest_format_valid`: Verify each line has valid hex SHA-256 and relative path.
  - `test_f24_03_manifest_files_exist`: Verify every file listed in `MANIFEST.sha256` exists on disk.
  - `test_f24_04_manifest_hashes_match`: Recompute SHA-256 for all listed files; verify 100% checksum match.
  - `test_f24_05_no_missing_tracked_files`: Verify all core distribution files are covered by manifest.

---

### 4.2 Tier 2: Boundary & Corner Cases (>= 5 Test Cases per Feature)

Tier 2 exercises extreme edge conditions, input anomalies, type boundaries, and structural limits:

- **F01 (Fiber Boundaries)**:
  - `test_f01_b01_empty_string_keys`: State ID, report, and query as empty strings `""`.
  - `test_f01_b02_nested_data_structures`: Complex nested JSON dictionaries and lists as reports.
  - `test_f01_b03_unicode_special_chars`: Control characters, non-ASCII Unicode, and escaped delimiters.
  - `test_f01_b04_rapid_repeated_collisions`: Multiple colliding states arriving sequentially after initial collision.
  - `test_f01_b05_large_fiber_volume`: 1,000 distinct states indexed with constant query without memory explosion.

- **F02 (Audit Boundaries)**:
  - `test_f02_b01_zero_step_transition`: Step witness where source and target are identical with 0 delta.
  - `test_f02_b02_exact_boundary_threshold`: Cumulative delta exactly equal to `max_total` (verifying $\le$ vs $<$ boundary).
  - `test_f02_b03_single_step_exceeds_max_step`: Step magnitude strictly exceeding `max_step`.
  - `test_f02_b04_alternating_cancelling_drift`: Fluctuating $+k, -k$ steps testing prefix breach vs endpoint cancellation.
  - `test_f02_b05_disconnected_source_fracture`: Step witness whose source differs from prior target ($G_1$ fracture).

- **F03 (Cochain Boundaries)**:
  - `test_f03_b01_self_loop_edge`: Directed edge from $u$ to $u$.
  - `test_f03_b02_parallel_multiedges`: Multiple edges between same pair with differing values/weights.
  - `test_f03_b03_fractional_extreme_denominators`: Fractions with large numerators/denominators (e.g. $10^{18}$).
  - `test_f03_b04_disconnected_components`: Edges arriving across disjoint subgraphs before cross-link.
  - `test_f03_b05_zero_and_negative_weights_rejected`: Weights $\le 0$ rejected at input boundary.

- **F04 (Selftest Boundaries)**:
  - `test_f04_b01_selftest_with_excess_args`: Passing spurious arguments to `selftest`.
  - `test_f04_b02_selftest_stdout_purity`: Verify no diagnostic warnings contaminate stdout.
  - `test_f04_b03_selftest_determinism`: Run selftest multiple times; verify identical receipt structure.
  - `test_f04_b04_selftest_fast_execution`: Verify execution completes under 5 seconds.
  - `test_f04_b05_selftest_isolated_environment`: Run with restricted environment variables.

- **F05 (Stream Boundaries)**:
  - `test_f05_b01_empty_stream`: Empty input stream (0 lines) terminates cleanly with exit code 0.
  - `test_f05_b02_malformed_json_lines`: Input containing truncated or unparseable JSON line; exits 2 with error receipt.
  - `test_f05_b03_mixed_empty_lines`: Stream containing blank lines and comments.
  - `test_f05_b04_streaming_buffer_flush`: Verify line-buffered flushing without unbounded memory buffering.
  - `test_f05_b05_duplicate_keys_in_stream_line`: JSON line with duplicate keys rejected per `loads_strict`.

- **F06 (Zipapp Boundaries)**:
  - `test_f06_b01_zipapp_file_permissions`: Readability and execution permissions.
  - `test_f06_b02_zipapp_corrupted_archive`: Handling of truncated archive file.
  - `test_f06_b03_zipapp_unknown_subcommand`: Calling non-existent subcommand returns exit code 2.
  - `test_f06_b04_zipapp_stdin_piping`: Piping data into zipapp via stdin (`-`).
  - `test_f06_b05_zipapp_zero_external_sys_path`: Verify zipapp runs cleanly with empty `PYTHONPATH`.

- **F07 (Test Suite Boundaries)**:
  - `test_f07_b01_no_third_party_imports`: Scan all test files for non-standard library imports.
  - `test_f07_b02_test_case_isolation`: Verify tests do not rely on execution order or side effects.
  - `test_f07_b03_clean_tempdir_cleanup`: Verify all temporary files/directories removed upon test exit.
  - `test_f07_b04_timeout_protection`: Verify subprocess commands enforce strict timeouts.
  - `test_f07_b05_no_network_access_in_unit_tests`: Ensure unit tests execute without external network connections.

- **F08 (OpenRouter Loader Boundaries)**:
  - `test_f08_b01_empty_env_file`: `.env` file exists but is 0 bytes.
  - `test_f08_b02_comment_only_env_file`: `.env` containing only `#` comments and whitespace.
  - `test_f08_b03_malformed_env_lines`: Lines missing `=` or containing duplicate equals signs.
  - `test_f08_b04_multiline_and_export_prefix`: Lines prefixed with `export ` or trailing carriage returns (`\r\n`).
  - `test_f08_b05_env_override_priority`: System environment variables take precedence over `.env` file.

- **F09 (Rate Metric Boundaries)**:
  - `test_f09_b01_single_sample_rates`: Exact rate calculation with $N=1$.
  - `test_f09_b02_extreme_imbalance`: 999 ZDR and 1 NGD; verify precision without float rounding errors.
  - `test_f09_b03_all_local_red_zero_lpr`: Local Pass Rate exactly 0.
  - `test_f09_b04_all_global_red_zero_gpr`: Global Pass Rate exactly 0.
  - `test_f09_b05_negative_egd_bound`: Extreme case where $LPR=1.0$ and $GPR=0.0$ yielding $EGD = -1.0$.

- **F10 (Test 1 Boundaries)**:
  - `test_f10_b01_test1_two_step_collision`: Collision occurring on immediate second step ($k=2$).
  - `test_f10_b02_test1_collision_with_boolean_reports`: Report is boolean `True` while query is boolean `False`.
  - `test_f10_b03_test1_collision_with_nested_reports`: Complex nested JSON dictionaries sharing representation.
  - `test_f10_b04_test1_post_collision_streaming`: Ingesting further steps after collision maintains `OBSTRUCTED_LGGR`.
  - `test_f10_b05_test1_receipt_hash_stability`: SHA-256 of collision receipt is deterministic.

- **F11 (Test 2 Boundaries)**:
  - `test_f11_b01_test2_immediate_first_step_breach`: First step delta exceeds budget.
  - `test_f11_b02_test2_boundary_reversal`: Step $k$ breaches budget, step $k+1$ cancels it; verify $k$ alert retained.
  - `test_f11_b03_test2_negative_drift_breach`: Negative drift exceeds $- \text{max\_total}$.
  - `test_f11_b04_test2_zero_tolerance_budget`: `max_total = 0`; any nonzero delta triggers alert.
  - `test_f11_b05_test2_multiple_alerts_accumulated`: Continued breaches emit cumulative alert records.

- **F12 (Test 3 Boundaries)**:
  - `test_f12_b01_test3_chordless_large_cycle`: 10-node cycle closing on step 10.
  - `test_f12_b02_test3_figure_eight_two_cycles`: Graph forming two adjacent cycles sharing a node.
  - `test_f12_b03_test3_unit_weight_simplification`: All weights exactly 1; exact $\ell^1$ norm.
  - `test_f12_b04_test3_asymmetric_edge_weights`: Highly skewed weights (e.g. 1 vs 100).
  - `test_f12_b05_test3_zero_cost_optimal_potential`: Cycle values summing to zero; potential exists with zero repair.

- **F13 (Test 4 Boundaries)**:
  - `test_f13_b01_test4_minimal_two_stage_lggg`: Minimal 2-agent pipeline satisfying boundary sufficiency.
  - `test_f13_b02_test4_ten_stage_pipeline`: 10-agent sequential pipeline maintaining composable LGGG.
  - `test_f13_b03_test4_redundant_query_fields`: Schema with extra discriminating fields preserving injectivity.
  - `test_f13_b04_test4_empty_payload_boundary`: Valid minimal empty payload schema.
  - `test_f13_b05_test4_large_step_history`: 50 steps maintaining $\Delta_E = 0$ throughout.

- **F14 (Replay Boundaries)**:
  - `test_f14_b01_replay_missing_file`: Replaying non-existent trace file returns error exit code.
  - `test_f14_b02_replay_truncated_trace`: Incomplete trace file with missing closing JSON bracket.
  - `test_f14_b03_replay_schema_version_mismatch`: Trace with unsupported `schema` version string.
  - `test_f14_b04_replay_reordered_events`: Events reordered out of chronological sequence detected.
  - `test_f14_b05_replay_extra_unknown_fields`: Unknown top-level fields rejected per strict parser.

- **F20 (Cookbook Boundaries)**:
  - `test_f20_b01_cookbooks_executable_directly`: Can be invoked as `python cookbooks/01_...`.
  - `test_f20_b02_cookbooks_no_side_effects`: Do not write persistent files outside temporary locations.
  - `test_f20_b03_cookbooks_syntax_compilation`: Verify `py_compile.compile` succeeds with zero errors.
  - `test_f20_b04_cookbooks_stdout_clean`: Emit valid demonstration receipts without uncaught tracebacks.
  - `test_f20_b05_cookbooks_quick_completion`: Each cookbook completes execution in under 5 seconds.

- **F21 (Monograph Index Boundaries)**:
  - `test_f21_b01_markdown_heading_structure`: Proper markdown syntax and link structure.
  - `test_f21_b02_relative_paths_valid`: All relative links in index resolve to existing files.
  - `test_f21_b03_utf8_encoding_clean`: Index file is valid UTF-8 without BOM or invalid bytes.
  - `test_f21_b04_consistent_table_columns`: Tables have matching column counts across all rows.
  - `test_f21_b05_chronological_ordering`: Volumes I through VIII appear in strict sequential order.

- **F22 (Wiki Boundaries)**:
  - `test_f22_b01_mathjax_double_dollar_delimiters`: Block math uses `$$` and inline math uses `$`.
  - `test_f22_b02_no_latex_packages`: No `\usepackage` or environment definitions in wiki markdown.
  - `test_f22_b03_wiki_links_format`: Wiki links use relative paths or standard GitHub Wiki syntax.
  - `test_f22_b04_no_html_tags`: Clean markdown without unescaped raw HTML formatting.
  - `test_f22_b05_sidebar_all_links_resolve`: Every page referenced in `_Sidebar.md` exists.

- **F23 (Git Boundaries)**:
  - `test_f23_b01_no_stray_pyc_files`: Git status contains zero untracked `.pyc` or `__pycache__`.
  - `test_f23_b02_no_merge_conflict_markers`: Zero occurrences of `<<<<<<<`, `=======`, `>>>>>>>`.
  - `test_f23_b03_crlf_lf_safety`: Text files have consistent newline conventions without corruption.
  - `test_f23_b04_file_size_limits`: No tracked file exceeds 50 MB.
  - `test_f23_b05_branch_head_valid`: Working branch is valid and cleanly rebased.

- **F24 (Manifest Boundaries)**:
  - `test_f24_b01_manifest_sorted_order`: Entries in `MANIFEST.sha256` are sorted alphabetically.
  - `test_f24_b02_manifest_double_space_separator`: Standard sha256sum format `<hash>  <path>`.
  - `test_f24_b03_manifest_forward_slashes`: Paths in manifest use forward slashes `/`.
  - `test_f24_b04_manifest_covers_cookbooks`: All new cookbook scripts listed in manifest.
  - `test_f24_b05_manifest_covers_paper_viii`: All Volume VIII paper files listed in manifest.

---

### 4.3 Tier 3: Cross-Feature Interactions (Pairwise Combinations)

Tier 3 verifies seamless interoperation across feature boundaries:

1. **X01 (F01 Fiber + F02 Audit)**: Streaming fiber collision occurs during multi-step audit; verifies that fiber collision receipt integrates into audit history status.
2. **X02 (F01 Fiber + F05 CLI Stream)**: JSON state observations piped to `python -m lggr stream --monitor fiber` emit formatted `lggr.online_collision.v1` receipts.
3. **X03 (F02 Audit + F05 CLI Stream)**: JSON step witnesses piped to `python -m lggr stream --monitor audit` emit formatted `lggr.online_alert.v1` receipts.
4. **X04 (F03 Cochain + F05 CLI Stream)**: JSON edges piped to `python -m lggr stream --monitor cochain` detect cycle closure and emit rational repair receipts.
5. **X05 (F04 Selftest + F06 Zipapp)**: Standalone `lggr_witness_audit.pyz` executes `selftest` subcommand and exits with code 0.
6. **X06 (F08 Loader + F14 Replay)**: Benchmark trace replay mechanisms parse environment configurations and verify traces without making live API calls.
7. **X07 (F09 Rates + F10-F13 Benchmark Traces)**: Aggregation of replayed Tests 1–4 computes exact empirical defect distribution (LPR, GPR, NGD, ZDR, PGD).
8. **X08 (F14 Replay + F02 Audit)**: Recorded live benchmark traces replayed through `StreamingAuditMonitor` verify exact defect classification reproducibility.
9. **X09 (F20 Cookbooks + F01/F02/F03 Streaming API)**: Cookbooks import and drive streaming monitors through their public API contracts.
10. **X10 (F21 Monograph + F24 Manifest)**: Volume VIII paper additions in monograph index are fully validated by `MANIFEST.sha256`.

---

### 4.4 Tier 4: Real-World Swarm Application Scenarios (>= 5 Scenarios)

Tier 4 exercises complete end-to-end multi-agent swarm workflows reflecting practical production use cases:

#### Scenario 1: Multi-Agent Software Engineering Swarm with Boundary Insufficiency (F10)
- **Context**: A 3-agent software engineering swarm (Specification Agent $\to$ Code Generator $\to$ Unit Tester).
- **Failure Mode**: The Unit Tester verifies that all generated tests pass on mock inputs ($E_1 = 1, E_2 = 1$), emitting summary report `{"unit_tests": "PASS", "coverage": 95}`. However, an independent integration test oracle $E_g$ against real environment states fails ($E_g = 0$) due to an unmodeled network timeout invariant.
- **Workflow**:
  1. The swarm streams state transitions and boundary summaries to `StreamingFiberMonitor`.
  2. A previous passing run had identical report `{"unit_tests": "PASS", "coverage": 95}` with passing integration query ($q = 1$).
  3. The monitor detects that the same local report now maps to $q = 0$.
  4. Immediate transition from `COMPOSABLE_LGGG` to `OBSTRUCTED_LGGR` is signaled with receipt `lggr.online_collision.v1`.
- **Authoritative Oracle**: Batch `analyze_descent` on identical table rows yields matching `REPORT_INSUFFICIENT` status and identical colliding pair.

#### Scenario 2: Recursive Autonomous Tool-Use Chain with Prefix Budget Exhaustion (F11)
- **Context**: An autonomous agent performing iterative data retrieval and transformation over a 5-step tool execution plan.
- **Failure Mode**: Intermediate query exploration consumes excessive token/call budget (+8, +7, +6) before converging to a lower net endpoint (+3). Under an `every_prefix` policy with `max_total = 15`, step 3 breaches the ceiling ($8+7+6 = 21 > 15$).
- **Workflow**:
  1. Steps are streamed into `StreamingAuditMonitor` with `query_scope = "every_prefix"`.
  2. At step 3, cumulative signed delta reaches 21.
  3. The monitor immediately triggers an early-stopping alert receipt `lggr.online_alert.v1` at step 3, halting the swarm prior to completing steps 4 and 5.
- **Authoritative Oracle**: Batch `audit_history` on the 3-step prefix yields `BUDGET_EXCEEDED` under `every_prefix`.

#### Scenario 3: Cyclic Multi-Agent Peer Review and Consensus Obstruction (F12)
- **Context**: A 3-agent peer review loop where Agent 1 reviews Agent 2, Agent 2 reviews Agent 3, and Agent 3 reviews Agent 1 on code security claims.
- **Failure Mode**: Inconsistent relative risk scores: Agent 1 rates Agent 2 as $+1/2$, Agent 2 rates Agent 3 as $+1/3$, but Agent 3 rates Agent 1 as $+1/2$. The sum around the directed cycle is $1/2 + 1/3 + 1/2 = 4/3 \ne 0$, creating a topological obstruction.
- **Workflow**:
  1. Directed edges $(A_1, A_2, 1/2)$, $(A_2, A_3, 1/3)$, $(A_3, A_1, 1/2)$ arrive sequentially at `StreamingCochainMonitor`.
  2. Edges 1 and 2 form an open tree.
  3. Edge 3 closes the cycle $C$.
  4. The monitor detects closure failure $(D_1 h)_C = 4/3$ and computes exact rational $\ell^1$ repair distance $\Phi_1(h) = 4/3$ and dual witness $z = (1, 1, 1)$.
- **Authoritative Oracle**: Exact rational LP via `classify_cochain` and `verify_l1_certificate` in `lggr.linear` produces matching defect $4/3$ and dual certificates.

#### Scenario 4: Boundary-Sufficient Composable Swarm (LGGG Certification) (F13)
- **Context**: A multi-stage document translation and verification swarm adhering to a strongly typed schema that includes full context digests in local boundary reports.
- **Workflow**:
  1. Swarm stages pass state handoffs where local report includes input hash, output hash, and invariant token.
  2. Observations stream to `StreamingFiberMonitor` and `StreamingAuditMonitor`.
  3. Throughout all stages, no report collisions occur.
  4. Local evaluators pass ($E_i = 1$) and global oracle passes ($E_g = 1$), maintaining $\Delta_E = 0$ (`ZDR`).
  5. The monitors certify the run as `COMPOSABLE_LGGG` with receipt `lggr.composable_lggg.v1`.
- **Authoritative Oracle**: Exhaustive descent table decoder verification confirms `DECODER_VERIFIED` with zero collisions.

#### Scenario 5: Live Swarm Telemetry Pipeline via Unix Pipe to CLI Stream (F05)
- **Context**: Production monitoring pipeline where agent runner processes pipe JSON telemetry directly to `python -m lggr stream --monitor audit`.
- **Workflow**:
  1. Subprocess executes a simulated telemetry stream generated via standard library Python.
  2. The stream pipes into `lggr` CLI without temporary disk files.
  3. JSON receipts stream to stdout and are captured and validated against schema.
  4. Replay verification executes against the captured receipt stream using `python -m lggr replay`.
- **Authoritative Oracle**: Direct comparison of streaming receipt output against batch `audit_document` output on the equivalent history object.

---

## 5. Authoritative Expected Output Derivation

To guarantee test integrity without facade testing:
1. **Mathematical Oracles**:
   - Defect algebra: $\Delta_E = E_g - \prod_{i=1}^k E_i \in \{-1, 0, 1\}$.
   - Coboundary cycle defect: $(D_1 h)_C = \sum_{e \in C} \text{sign}(e) h(e)$.
   - $\ell^1$ primal/dual certificate: $\Phi(h) = \min_x \|h - D_0 x\|_{1,w} = z^T h$ where $D_0^T z = 0$ and $|z_e| \le w_e$.
2. **Reference Implementation Equivalences**:
   - Every streaming monitor result is checked against the equivalent batch oracle in `lggr.descent`, `lggr.witnesses`, and `lggr.linear`.
   - Streaming state arrival must produce identical final verdicts to batch evaluation over the realized sequence.
3. **Receipt Schemas**:
   - Receipts are checked against canonical schemas:
     - `lggr.selftest.v1`
     - `lggr.online_collision.v1`
     - `lggr.online_alert.v1`
     - `lggr.online_cochain.v1`
     - `lggr.trace_replay.v1`
     - `lggr.replay.v1`

---

## 6. Progressive Testability & Execution Strategy

In accordance with progressive testability principles:
- Tests verify features progressively as milestones complete:
  - If Milestone M1 is in progress or completed, F01–F07 tests execute against the implemented code.
  - If Milestone M2 is in progress, F08–F14 replay tests execute against pre-recorded or fixture artifacts.
  - If Milestone M5 is in progress, F20–F24 documentation and cookbook tests execute against repository files.
- Tests do not assume or require features from higher milestones to verify lower-milestone functionality.
- Pure Python standard library is used exclusively; no network access is attempted during test execution.

---

## 7. Claim Hygiene & Artifact Assessment

In strict accordance with the Claim Hygiene Rule:

1. **What this infrastructure supports:**
   - Formal test architecture and systematic 4-tier methodology for LGGR Volume VIII.
   - Comprehensive enumeration and contract specification for nineteen features (F01–F14, F20–F24).
   - Verifiable test cases across Feature Coverage, Boundary Cases, Pairwise Interactions, and Real-World Swarm Applications.
   - Exact mathematical derivation of expected test outcomes using standard library oracles.

2. **What this infrastructure does not support:**
   - Does not establish that real-world LLM swarms are immune to composability failures under unmodeled invariants.
   - Does not assert that passing synthetic test suites constitutes empirical proof of general multi-agent safety.

3. **Narrowest defensible claim:**
   - The test infrastructure establishes an opaque-box verification harness that checks whether the Python implementation in `lggr` adheres to its declared mathematical contracts for online report-fiber collision detection, prefix budget drift tracking, exact rational cycle repair, and standalone CLI receipt generation.

4. **Next test needed:**
   - Implement the test cases in `tests/test_e2e_suite.py` and run `python -m unittest tests/test_e2e_suite.py -v`.
