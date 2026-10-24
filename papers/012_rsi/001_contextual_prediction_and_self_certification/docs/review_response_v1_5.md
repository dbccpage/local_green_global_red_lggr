# Response to the v1.5.0 source review — correction release 1.5.1

The supplied review recommends proceeding after minor corrections. Its evidence was source review, 86 passing Python tests, four missing-file failures and exact comparisons of five Python certificates with literal Lean definitions. It performed no Lean elaboration, no 71-case executable comparison replay and no PDF review. This limitation is retained literally; the fresh local release checks are a separate record in verification.md.

## Corrections

| Finding | Resolution |
|:--|:--|
| Missing positive residual-rate premise in Section 3.2 | The divided window now states both positive rate and positive observable norm. The zero-rate case uses the original enclosure directly and applies only while that enclosure holds. A zero observable norm is handled separately. The Lean theorem already had the positive premises and remains unchanged. |
| Sampling noise can violate exact overlap compatibility | `evaluate` keeps its exact-model domain and signalling refusal. New `observed_matrix` builds columns from the declared measurements while retaining normalized observed rows with their discrepancies. `evaluate_observed` returns a conditional radius-adjusted bound; `verify_observed` checks it against the original observations and radius. |
| Raw defect 1/50 entirely explained by radius 1/50 | The exact example and regression tests reproduce a raw optimum of 1/50 and an adjusted guaranteed margin of zero. No contextuality classification of the unknown true table is returned. Zero adjusted margin is not a noncontextuality certificate. |
| Obsolete Rust LP pointer | The inherited module description marks the old Rust implementation as historical and points to the current Python solver and separate Lean implementation. |
| Tip-check helper overstates completeness | `complete_against` now states that it checks internal consistency and equality to a supplied tip, with no unconditional history-completeness or uniqueness guarantee. |
| Bland attribution | Added the primary 1977 publisher citation. Using the rule remains distinct from a Lean proof of its unbudgeted finiteness. |

The radius is the total raw l1 error over all context/outcome entries. Its statistical or model-based coverage is a caller premise, not supplied by exact arithmetic. The uncertain route does not force compatibility or alter the input. If a caller preprocesses observations, the resulting change must be included in a justified uncertainty enclosure.

## Four missing-file failures

These failures belong to the attachment subset reconstructed by the reviewer. All four files are present in the complete local v1.5.0 release, and remain included in this correction:

| Missing in reviewed subset | Present in complete standalone ZIP |
|:--|:--|
| Source lineage | `docs/source_lineage.json` |
| Fixture generator | `tools/generate_lp_certificates.py` |
| Solver provenance | `docs/solver_provenance.json` |
| Axiom parser/auditor | `tools/replay_lean_axiom_census.py` |

The full ZIP also includes the pinned toolchain declaration, local Lake build configuration, source/artifact dependency bundle and licenses, `SimplexDriver.lean`, `docs/simplex_execution_cases.json`, the comparison replay tool, named/full census reports, audited source hashes, conversion tools, rendered manuscript, compiler logs and both manifests. Extract that complete archive for the commands in Section 6. Selected source attachments cannot replace it. Lean, Python, pytest, tar and the documented document tools remain installed prerequisites.

The original 86-pass/four-failure output, checker, outputs and all attached sources are preserved unchanged under source_inputs/v1_5_review and enumerated in v1_5_review_sources.json. The new replay tool reruns the review's three exact mathematical groups and the current API example. Those literal-source comparisons do not elaborate Lean. The full build/census and 71 executable comparisons are separate commands.

## Scope retained

No theorem or proof module is changed by this patch. The named census still contains 98 theorems and the package-local environment census contains 660 declarations. The simplex is finite-budget total and correct on successful checked return. Universal Python refinement, unbudgeted Bland completeness and mathematical evidence for infeasible/unbounded labels remain unimplemented. Resource exhaustion remains a distinct refusal.

Checked infeasibility witnesses and unbounded rays are recorded as the next solver extension, rather than being presented as completed work. The broader refinement from an implemented memory transformation and enforced action gate to a safety invariant remains open; neither additional arithmetic nor role identifiers discharge it.

Fresh local replay establishes the recorded properties of this release under its stated prerequisites. It does not convert the supplied source review into an independent external release approval.
