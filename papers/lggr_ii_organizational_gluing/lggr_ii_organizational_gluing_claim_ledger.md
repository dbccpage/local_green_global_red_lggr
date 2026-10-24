---
paper: "Local Green, Global Red II: Organizational Evaluator Gluing"
version: "1.3.1"
date: "2026-10-15"
---

# Claim ledger

This ledger separates mathematical statements, definitions, implementation
contracts, and interpretation. The structured `Mechanization` column identifies
which rows have Lean support. A Lean theorem supports only the statement in its
row; it does not mechanize the organizational reading.

| ID | Statement | Type | Mechanization | Lean evidence | Python evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | For Boolean global verdict `E_G` and local product `L`, `Δ_E = E_G - L` lies in `{-1,0,1}`. | theorem | LEAN | `PaperAE005.orgDelta_range` | `TestEvaluatorGluingDefect.test_defect_trichotomy_and_invariants` | checked |
| M2 | `Δ_E=-1` iff `E_G=false` and `L=true`. | theorem | LEAN | `PaperAE005.orgDelta_is_negative_one_iff` | `TestOrganizationalEvaluatorSystem.test_system_evaluation_success` | checked |
| M3 | Weak recovery of `E_G`, together with `gAuth=true` and `gTime=true`, does not imply `E_G=E1∧E2`. | finite counterexample | LEAN | `PaperAE005.weak_boundary_sufficiency_does_not_force_factorization` | `TestWeakSufficiencyAuditor.test_weak_sufficiency_counterexample` | checked |
| M4 | Given weak recovery of `E_G`, product sufficiency is equivalent to evaluator factorization. | theorem | LEAN | `PaperAE005.product_sufficiency_iff_evaluator_factorization` | `FiniteTheoremCensus.product_sufficiency_iff_factorization_census` | checked |
| M5 | Three legal defect values can have a sum outside `{-1,0,1}`. | finite counterexample | LEAN | `PaperAE005.three_binary_defects_sum_can_leave_binary_range` | `TestNonAdditivityAuditor.test_direct_scalar_sum_range_violation` | checked |
| M6 | `Δ_E=0` does not imply that both global and local-product verdicts pass. | finite counterexample | LEAN | `PaperAE005.zero_defect_does_not_imply_all_pass` | `TestDetectorAdequacyGuard.test_audit_verdict_asymmetry_and_diagnostics` | checked |
| M7 | Setting the complete local product equal to the global evaluator forces zero defect. If one local validator copies `E_G`, passing peer validators are a sufficient specialization; a copied validator plus a failing peer need not collapse. | theorem and finite countermodel | LEAN | `PaperAE005.aligned_validator_forces_zero_defect`; `PaperAE005.aligned_validator_proxy_collapsing_detector` | `TestDetectorAdequacyGuard.test_aligned_collapsing_detector`; `TestDetectorAdequacyGuard.test_copied_global_validator_with_failing_peer_is_not_collapsing` | checked |
| M8 | If the global evaluator differs on two traces in one joint-carrier class, it cannot factor through the carrier quotient. | theorem | LEAN | `PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization` | `FiniteTheoremCensus.quotient_factor_table` | checked |
| M9 | Under carrier-local evaluators, if two traces have the same joint carrier, their global verdicts differ, and one trace is locally green, then one of the two traces has `Δ_E = -1`. | theorem | LEAN | `PaperAE005.boundary_carrier_mixing_forces_lggr` | `FiniteTheoremCensus.negative_defect_witness` | checked |
| D1 | Governance readiness is `gRep ∧ gAuth ∧ gTime`; therefore readiness implies `gAuth`. | definition and conjunction elimination | LEAN | `PaperAE005.governancePrerequisitesSatisfied`; `PaperAE005.governance_prerequisites_require_auth` | `OrganizationalClosureConditions.governance_prerequisites_satisfied` | implemented and checked |
| D2 | Checked-closure eligibility is zero defect together with governance readiness. | definition | PYTHON | no Lean declaration | `OrganizationalClosureConditions.is_checked_closure_eligible` | implemented |
| D3 | `gAuth` is true only when the declared owner has authority and accountability. | definition | PYTHON | Boolean field only | `BoundaryOwner.is_complete` | implemented |
| I1 | Local evaluators can model unit checks and `E_G` an end-to-end check. | interpretation | PROSE | none | generic and named example constructors | illustrative |
| I2 | A Shapley value can describe contributions for a user-supplied coalitional value function. | implementation contract | PYTHON | none | `TestNonAdditivityAuditor.test_shapley_attribution` | checked in Python |
| R1 | Evaluator callbacks reject every value whose exact Python type is not `bool`, including integer and float stand-ins; valid verdicts produce integer `0/1` records. Inconsistent records, malformed cuts, empty detector samples, and evidence-level escalation attempts are also rejected. | computational robustness contract | PYTHON | none | `test_invasive_injections.py` and constructor tests | checked |
| R2 | The public notebook executes from start to finish without a pre-existing kernel state. | computational reproducibility contract | PYTHON | none | `test_notebook_executes_headlessly` | checked when suite passes |

## Formal scope

`check_axioms.lean` requests an axiom report for every declaration cited above.
The expected report is empty except for the standard `Quot.sound` dependency
in the quotient theorem. A clean build also requires a source scan with no
`sorry` or `admit` token.

## Interpretation scope

Named scenarios in the Python module are fixed Boolean examples. They do not
establish historical causation, organizational fault, risk estimates, or
predictions. No empirical claim in an earlier draft is load-bearing for M1–M9.

## Release evidence

The release is ready to pin only after all of the following are rerun on the
final bytes:

1. frozen `uv.lock` replay with branch-aware Python coverage at or above 95 percent;
2. headless notebook execution;
3. Lean build, source scan, axiom census, and `docs/lean_claim_map.md` hash check;
4. figure and paper-artifact regeneration;
5. visual PDF inspection; and
6. two-way deposit-manifest verification.
