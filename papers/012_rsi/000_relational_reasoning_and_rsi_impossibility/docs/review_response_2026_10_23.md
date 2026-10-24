# Response to the independent RSI review

Version 1.2.3, 2026-10-23. The supplied review audits commit
`e15a9d4ac6298524ce370cae679314aa0fef7585`, not the later integrated manuscript.
Its eight executable probes nevertheless reproduced their reported behavior on
the pre-repair 1.2.2 working tree. The source-bound baseline, complete supplied
packet, original Unicode fixture and release verification are retained in the
adjacent research dossier `../research/2026_10_23_rsi_review/` (from the paper root).
The earlier numerical-completion report did not establish that the shipped
cochain solver had the claimed exactness correction; the fresh baseline exposed
that gap. This edition repairs the actual deposited implementation.

| Finding | Current disposition and evidence |
|---|---|
| R01: closed versus exact | Removed the zero-closure shortcut. `verify_exact_l1_repair` independently checks signed-incidence reconstruction, exact residual/cost, dual annihilation, infinity bound and equal objectives. A nonzero exact triangle reconstructs; the closed annulus has certified optimum 9, not 0. Component mutations fail. Search remains floating-point HiGHS with exact rational checking; a failed reconstruction is not a certificate. |
| R02: identity parity | Both languages enforce `ascii-identifiers-v2`: ASCII letters, digits, space, dot, underscore, colon and hyphen; trim and lowercase for comparison. Unicode identities are refused. Eight native adversarial/control records cover sharp-s, sigma, dotted I, invisible/nonbreaking space and ASCII case. The local v2 fixture is distinct from the retained upstream v1 Unicode policy. |
| R03: native verification scope | Renamed the primary API `cross_check_eis_metadata_against_rust`. Results state `EIS_METADATA_ONLY`, `obstruction_predicates_checked=false`, and `metadata_record_count`. The old function name is a compatibility alias. A forged obstruction still passes the metadata layer, which now explicitly makes no obstruction claim. Host authenticity and independence remain external premises. Unsupported wire shapes/delimiters are refused. |
| R04: implementation divergence | The former monolith now imports the tested modules and supplies only a CLI. At N=4, an increasing counter reaches the declared capacity threshold at step 4 in both APIs. A cyclic bounded counter instead reaches report collision. This numeric-rank policy is not invariant under arbitrary score relabeling. |
| R05: installed wheel | Declared NumPy/SciPy; explicitly listed public modules; bundled JSON/Rust under `rsi_eis_resources`, accessed via `importlib.resources`. The deposited wheel verifier installs into a fresh venv, checks import origins, replays the annulus and native metadata checker, then executes the advertised CLI outside the source tree. Rust, Lean and rendering binaries remain declared external prerequisites. |
| R06: release identity | Version 1.2.3 aligns active metadata, manuscript and source package. The release is rebuilt with two-way checksum/membership checks and deterministic byte equality; the previous ZIP is retained outside the active deposit. Historical logs keep their original versions. |
| R07: epistemic overclaim | The integrated manuscript already withdrew the zero-mutual-information inference and distinguishes an anti-announced-bit protocol from positive introspection. This edition also explicitly treats distinct verifier labels as a role policy, not authenticated or statistical independence. |
| R08: finite vocabulary | The manuscript already requires a complete-report resource bound, rather than finite alphabet alone. It now explicitly includes transcript, verifier state, timestamps and rolling context if used by dominance. N reports allow at most N−1 strict transitions; N+1 observations force a repeat by transition index N. |
| R09: conflated optimization problems | Cochain repair uses unrestricted potentials. The companion's separate probability-marginal LP includes nonnegativity and normalization. No reduction or general CF=distance/2 equality is claimed. The supplied two-disjoint-PR counterexample has contextual fraction 1 and unweighted distance 4. Supported local sections, not restrictions of a preselected global section, are the domain of a support-gluing test. |
| R10: alignment definitions | Structural preservation and the numeric-rank predicate are separate models. No equivalence is asserted. The four supplied `ReviewCountermodels` declarations are compiled and included in both censuses; the aligned successor with one constant report violates report-grounded dominance. |
| R11: dynamical corollaries | The retained Lean corollaries express cardinality facts about fixed report products and compatibility equations. They do not model channel buffers or prove a terminal-reason distribution. Self-equality of a topology argument supplies no mechanistic evidence. |
| R12: finite prefixes | `PrefixBounds` adds finite-horizon spending, unit-cost, refinement, lift and interleaved-event results. Decrease is required only below L. Interleaved lift counts are bounded, not uncharged clock ticks. The older total-descent statements remain termination contradictions, as the compiled countermodels show. |
| R13: budget creation | Active repair independently rechecks the certificate. Price must be an exact nonnegative integer, excluding bool, float and Fraction; a nonzero repair requires a strictly positive license price. Invalid certificates/prices raise explicit errors even under `python -O`. |
| R14: synthetic defects | The experiment labels its outcome distribution `CONTROLLED_SYNTHETIC_DEFECT_INJECTION`. The age penalty for equal content is retained as an explicit policy, not a consequence of transport. Constant/equal-content, compensated and mismatched controls expose that distinction. |

The contextual-fraction distinction follows the separate LP definition and
normalized Bell-violation characterization in [Abramsky, Barbosa and Mansfield
(2017)](https://arxiv.org/abs/1705.07918). Strong contextuality implies logical
contextuality, which implies probabilistic contextuality; none is inferred from
an arbitrary cochain residual alone.

## Verification boundaries

`code/tests/test_review_regressions.py` supplies 17 regression cases, including
real rustc execution and a separate optimized Python process. The named census
includes all 118 explicit package theorems: five new prefix theorems and the four
reviewer scope controls, plus the prior 109. The full census also covers generated
and private declarations. Only standard Lean foundations are permitted.

This edition does not establish a universal refinement theorem from Python/Rust
execution to Lean. It does not implement authenticated host identity or full
obstruction-receipt replay. The native gateway/quantum and live-provider evidence
from the preceding edition is historical; these runs are not repeated or
promoted by the present code repair. Fresh source, clean extraction and installed
wheel results are recorded separately in the accompanying verification receipt.
