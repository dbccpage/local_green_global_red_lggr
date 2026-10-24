# Lean formalization map

The dependency-free core uses Lean 4.35.0. All names below have prefix `InstitutionalReasoning.` and are defined in `lean4/Core.lean`.

| Claim | Theorem | Exact scope |
|---|---|---|
| IK-01 | `relative_non_identification` | An admitted relation preserves J; endpoint J values differ. invariant_separates is a Boolean-premise fixture, not an invariant verifier. |
| IK-02 | `recoverable_iff_fiber_constant` | Functions C and q on a declared source domain; decoder on the image. Python checked on finite domains; no universal implementation refinement. |
| IK-03 | `profile_fiber_constant_iff` | Declared indexed family of questions; equality of answer profiles. Not preservation of every possible future question. |
| IK-03 | `profile_recoverable_iff` | Declared indexed family of questions; equality of answer profiles. Not preservation of every possible future question. |
| IK-04 | `side_recovery_iff` | Decoder from the pair of summary and side code. Formalized separation step; not the full cardinality bound. |
| IK-04 | `distinct_answers_require_distinct_side_codes` | Decoder from the pair of summary and side code. Formalized separation step; not the full cardinality bound. |
| IK-06 | `joint_constraint_obstruction` | Binary variables with a=b, b=c, c!=a. Lean proves the contradiction; Python establishes nonempty locals and pairwise consistency. |
| IK-07 | `joint_action_respects_each_constraint` | Membership in the intersection of declared predicates. Does not grant execution authority or merge explanations. |

Eight explicitly named theorems are covered by `Census.lean` and the named report. `FullCensus.lean` enumerates all declarations whose defining module is Core, including generated declarations if any. Imported Lean declarations are outside this package census. Source hashes bind the local proof module, Lake files, pinned toolchain and census tools. The reports allow only `propext`, `Classical.choice`, and `Quot.sound`; a custom axiom or incomplete proof fails the checks.

The image-based theorem also applies to empty domains and does not require a nonempty ambient answer type; it therefore includes the manuscript's finite nonempty case. Its existential decoder uses classical choice and asserts no efficient algorithm. The profile theorem permits an arbitrary indexed family of questions. The paper's finite family is an instance.

The full fixed-bit cardinality formula, statistical variance identity, general graph theorem, Python refinement, program termination and institutional hypotheses remain outside the Lean proof scope. The joint-action theorem is elementary intersection elimination and carries no authorization semantics.
