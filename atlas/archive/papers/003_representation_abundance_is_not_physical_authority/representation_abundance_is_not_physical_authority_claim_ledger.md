# Claim Ledger: Representation Abundance Is Not Physical Authority

**Author:** Jeremy H. Carroll
**Series:** 001_finite_obstruction_calculus
**Paper Key:** 001_finite_obstruction_calculus/003_representation_abundance_is_not_physical_authority
**Version:** 2.2.0 (2026-10-16)
**License:** CC-BY-4.0

## Verification scope

Written mathematical proofs, supporting Lean statements, and Python regressions have distinct scopes. The core has 33 unit and regression tests; the release verifier has 23 synthetic integrity cases. Passing finite tests is not a general proof or evidence of physical completeness. This package has no assigned version DOI and has not been deposited by this revision.

## Claim register

| ID | Manuscript claim | Written status | Lean support and boundary | Python scope |
| :--- | :--- | :--- | :--- | :--- |
| C1 | §1.2 Membership alone does not select a candidate in a declared family. | Definition and finite non-implication. | No physical-authority theorem. | Finite family examples. |
| C2 | Proposition 2.1 Observer blindness. | Proof in §2.2. | observation_decision_agrees: function-composition equality on arbitrary types. | Equal-profile examples. |
| C3 | Theorem 2.2 Plenitude inflation under an observation-preserving proper extension with no new profiles. | Proof in §2.3. | plenitude_inflation: natural-number multiplication inequality only. Families, quotient cardinalities, and rational ratios are not mechanized. | Retained immutable model content, proper identifier inclusion, profile-set equality, exact ratios. |
| C14 | Proposition 2.3 A property factors through observations exactly when constant on their fibers. | Proof in §2.4. | Not mechanized. | Shared-property example; no general executable proof claimed. |
| C4 | Theorem 3.1 Rational graph coboundaries have zero holonomy on closed walks. | Telescoping proof in §3.2. | cycle_coboundary_holonomy_zero: closed integer-value list. Rational graph correspondence and H¹ quotient are not mechanized. | Canonical stored cochains and equivalent signed traversals. |
| C5 | Theorem 3.2 Positive cycle tolerances admit a rational local-green field with nonzero holonomy on an edge-simple cycle of length at least three. | Half-minimum construction in §3.3. | false_green_holonomy and false_green_local: integer positivity and local inequalities. Rational witness and graph embedding are not mechanized. | Rational construction on declared edge-simple cycles; repeated edges refused. |
| C6 | Corollary 3.3 Tolerance-sum bound, sharp on edge-simple cycles including zero tolerances. | Triangle inequality and sign-aligned assignment in §3.4. General closed-walk bound need not be sharp. | cycle_defect_bound: signed integer list with natural tolerances. sharp_cycle_attains: all-positive-sign list. Rational graph correspondence is not mechanized. | Bound on closed walks; sharpness on edge-simple cycles. |
| C7 | Definition 4.1 Selector quadruple with externally certified evidence as a premise. | Definition. | Not mechanized. | Exact per-observable discrepancies; upstream provenance is not authenticated. |
| C8 | §4.2 Candidate and family terminal taxonomies differ. | Definition. | Not mechanized. | Candidate receipt remains SURVIVOR, REFUTED, or REFUSED. Context-bound family result carries ACCEPTED, UNDERDETERMINED, REFUTED, or REFUSED. |
| C9 | §4.3 Adding a survivor to a uniquely selected complete family removes uniqueness. | Finite counting argument. | unique_acceptance_breaks: Boolean survivor count one to two. Candidate, evidence, and selector semantics are not mechanized. | Same evidence, retained family, new survivor. |
| C10 | §5.1 Five toy vacua. | Worked example. | No claim of physical applicability. | Exact finite refutation and family selection. |
| C11 | §5.2 Hexagon holonomy 3/5 within local tolerances 1/5. | Worked example. | No graph-to-physics bridge. | Exact rational computation. |
| C12 | §5.3 One hundred indistinguishable vacua. | Worked example. | No asymptotic or physical completeness claim. | Underdetermination ratio 100. |
| C13 | §6 Scope boundaries. | Explicit nonclaims. | Lean components do not establish empirical validity. | No full repository, Rust, or external physics verification. |

## Reproduction

The README gives named Python checks, the standalone Lean build/census, and a separate check of the selected ZIP. The census expects eight declarations from lean4/Census.lean and only the standard kernel axioms propext, Quot.sound, and Classical.choice. The complete rational graph and selector statements remain written proofs with finite Python checks.

## Named regression entry points

These executable checks have the finite scopes described above; they do not establish whole-paper truth.

- `code/tests/test_release_integrity.py::test_rebuild_is_byte_identical_and_inventory_complete`
- `code/tests/test_release_integrity.py::test_subprocess_payload_mutation_is_fatal`
