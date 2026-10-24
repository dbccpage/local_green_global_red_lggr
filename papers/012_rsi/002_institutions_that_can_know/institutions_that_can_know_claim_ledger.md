# Claim ledger

Version 0.1.0. Formal and executable evidence applies only to the assumptions recorded here.

| ID | Claim and manuscript location | Evidence | Boundary |
|---|---|---|---|
| IK-01 | Relative non-identification (section 3.1.2) | LEAN4_PROOF | An admitted relation preserves J; endpoint J values differ. invariant_separates is a Boolean-premise fixture, not an invariant verifier. |
| IK-02 | Exact question recovery (section 3.2.1) | LEAN4_PROOF | Functions C and q on a declared source domain; decoder on the image. Python checked on finite domains; no universal implementation refinement. |
| IK-03 | Question-profile preservation (section 3.2.1) | LEAN4_PROOF | Declared indexed family of questions; equality of answer profiles. Not preservation of every possible future question. |
| IK-04 | Recovery with a side record (section 3.2.2) | LEAN4_PROOF | Decoder from the pair of summary and side code. Formalized separation step; not the full cardinality bound. |
| IK-05 | Exact fixed-length side-bit bound (section 3.2.2) | PROSE_PROOF | Finite nonempty domain; deterministic unrestricted encoder; shared codebook; fixed length. Counting proof and 216 exhaustive cases; codebook, specification and verification costs excluded; general bound not Lean-formalized. |
| IK-06 | Matching local projections need not admit a global assignment (section 4.1) | WORKED_EXAMPLE | Binary variables with a=b, b=c, c!=a. Lean proves the contradiction; Python establishes nonempty locals and pairwise consistency. |
| IK-07 | Joint acceptability respects every participant constraint (section 4.2) | LEAN4_PROOF | Membership in the intersection of declared predicates. Does not grant execution authority or merge explanations. |
| IK-08 | Evidence-access cuts can remove answerability (section 4.3) | CODE_DEMO_PYTHON | Fixed graph, evidence corpus and admitted procedures. Reachability examples only; no claim about actual institutional collapse. |
| IK-09 | Variance and effective sample size (section 4.4) | PROSE_PROOF | Equal unbiased variances, feasible common correlation, positive denominator for finite effective count. Conditional variance expansion; no measured council correlation; no Lean proof. |
| IK-10 | Five institutional capacities (section 2.1) | PROPOSED_FRAMEWORK | Declared task, constituency and resources. Requires construct validation and empirical case studies. |
| IK-11 | Belonging and failed mediation (section 6.1) | EMPIRICAL_HYPOTHESIS | Measured dependencies, sanctions and correction routes. No motive diagnosis or universal collapse law. |
| IK-12 | Existing Anomalon design provides integration points (section 6.2.1) | SOURCE_SUPPORTED_OBSERVATION | Two design documents at the pinned commit. Document claims are not a current runtime audit or replay of their tests. |
| IK-13 | Proposed council protocol improves recovery and coordination (section 6.4) | EMPIRICAL_HYPOTHESIS | Matched budgets, baselines, negative controls and ablations for H1-H3. No live-model, human, deployment or superiority experiment. |
| IK-14 | Proposal does not authorize execution in the finite example (section 5.1) | CODE_DEMO_PYTHON | Explicit mandate fixture and example YAML. Externally verified Boolean is assumed; no authentication or enforced runtime gate. |
| IK-15 | Prior work motivates distributed and socially organized knowing (section 1.2) | IMPORTED_BACKGROUND | References and per-source inspection scope. Not a systematic review or global novelty claim. |
| IK-16 | RSI crosswalk and embedded evaluation (section 1.3) | PROPOSED_FRAMEWORK | Agents, records and evaluators are parts of one world; questions and budgets are declared. No outside observer; no claim that the existing runtime implements this protocol. |

The source-level declarations and exact names are in [the formalization map](docs/lean_claim_map.md). Imported sources and their inspection limits are recorded separately. No overall correctness percentage is assigned.
