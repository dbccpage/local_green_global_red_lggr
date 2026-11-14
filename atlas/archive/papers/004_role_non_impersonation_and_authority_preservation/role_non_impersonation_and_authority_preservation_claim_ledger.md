# Claim Ledger: The Omega Tower — Role Non-Impersonation and Authority Preservation

**Author:** Jeremy H. Carroll
**Series:** 001_finite_obstruction_calculus
**Paper Key:** `001_finite_obstruction_calculus/004_role_non_impersonation_and_authority_preservation`
**Version:** 1.3.0 (2026-10-16)
**Prior record identifier:** [10.5281/zenodo.20710065](https://doi.org/10.5281/zenodo.20710065)
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

---

## 1. Governance & Verification Scope

This ledger records all formal claims, theorems, definitions, and verification receipts for the monograph *The Omega Tower: Role Non-Impersonation and Authority Preservation in Agentic AI*.

- **Nonclaims:** This monograph establishes an architectural separation of privilege model and formal verification criteria; it assigns no operational authority or institutional standing, and does not claim unconstrained AI safety.
- **Machine Verification:**
  - All formal algebraic theorems, constructor bijections, refusal monad laws, quotient boundaries, and descent adjunctions are mechanized in Lean 4 (`lean4/`), compiling under toolchain `v4.34.0` with zero `sorry` placeholders and strictly whitelisted standard axioms (`Quot.sound`, `propext`).
  - All operational pipelines, $\mathbb{F}_2^3$ cochain examples, audit detectors, finite-shadow evaluators, and residual classifiers are implemented in Python (`code/`) and verified by 47 unit tests in `code/tests/`.
- **Claim Types:** `[DEFINITION]`, `[PROVEN]`, `[CONTRACT RULE]`, `[WORKED EXAMPLE]`, `[IMPLEMENTATION CONTRACT]`, `[FIXTURE CONTRACT]`, `[FIXTURE SUITE]`, `[SCOPE FENCE]`.

---

## 2. Master Claim Register

| ID | Location | Claim Summary | Type | Verification / Proof |
| :---: | :--- | :--- | :---: | :--- |
| **C1** | Sec. 2.1 | **Proposal/Authority Boundary:** $p \in \mathcal{P} \not\Rightarrow \mathsf{Auth}(p)$. Authority is a dependent type requiring an explicit terminal token from an independent verification pipeline. | `[DEFINITION]` | Formal definition in §2.1; verified in `AuthorityResidual.lean` and `code/pipeline.py`. |
| **C2** | Sec. 3 | **Conserved Obligations:** Six distinct governance roles ($\Omega_\partial, \Omega_\mathbb{A}, \Omega_\chi, \Omega_\mathfrak{O}, \Omega_\kappa, \Omega_{\Lambda\Omega}$) with explicit governing prohibitions. | `[DEFINITION]` | Formal definitions in Table 1; implemented in `code/models.py`. |
| **C3** | Sec. 4 | **Theorem 1 (Constructor Invertibility & Role Distinction):** The mapping from the six roles to the six failure modes is bijective, injective, and invertible. | `[PROVEN]` | Proved in Lean 4 (`RoleFailure.roleToFailure_injective`, `failureToRole_roleToFailure`); tested in `test_role_collapse.py` and `code/proved_rows.py`. |
| **C4** | Sec. 6.1 | **Proposition 1 (Left-Zero Absorption):** The refusal monad satisfies $\mathsf{bind}(\mathsf{Refusal}(err), f) = \mathsf{Refusal}(err)$, a property of the declared pure bind operation. | `[PROVEN]` | Proved in Lean 4 (`ExceptionPipeline.bindR_refusal_left_zero`); tested in `test_pipeline.py` and `code/proved_rows.py`. |
| **C5** | Sec. 6.2 | **Theorem 2 (Refusal Propagation and Anti-Cheat):** The five-stage Kleisli pipeline short-circuits on any stage refusal, halting execution without minting authority under the declared premise that preterminal stages lack token-issuance capabilities. | `[PROVEN]` | Proved in Lean 4 (`ExceptionPipeline.pipeline5_*_refusal_propagates`); tested in `test_pipeline.py` and `code/proved_rows.py`. |
| **C6** | Sec. 6.2 | **Contract Rule 3:** the declared model routes role removal to its mapped failure label unless a reviewed equivalent obligation is supplied. | `[CONTRACT RULE]` | Lean verifies the constructor mapping only; it is not an architecture-necessity theorem. |
| **C7** | Sec. 2.1 | **Terminal Constructor Disjointness:** Authority, Residual, and Refusal constructors are mutually disjoint; residual/refusal output cannot inhabit $\mathsf{Auth}(p)$. | `[PROVEN]` | Proved in Lean 4 (`AuthorityResidual.authority_not_residual`, `authority_not_refusal`); tested in `test_pipeline.py` and `code/proved_rows.py`. |
| **C8** | Sec. 6.2 | **Quotient Boundary Theorem:** Role-failure classification cannot factor through a role-erasing payload quotient; factoring is equivalent to fiber invariance; equal payloads may carry different role failure labels. | `[PROVEN]` | Proved in Lean 4 (`QuotientBoundary.role_failure_no_quotient_factor`, `payload_classifier_factors_iff`, `role_failure_not_factor_through_payload_quotient`, `payload_green_role_failure_red`); finite witness in `code/proved_rows.py`. |
| **C9** | Sec. 5 | **Worked Example ($\mathbb{F}_2^3$ Configuration Merge):** Conflict cochain $r = (0, 1, 0)$ with $\bar{d}_1(r) = 0$ is housed as `ClosedResidual` in full-stack run, while collapsed run exposes counterfeit closure. Carrier requires exactly 3 coordinates in $\mathbb{F}_2$. | `[WORKED EXAMPLE]` | Analytical derivation in §5; verified in Python by `test_cochain_worked_example.py` and `test_reviewer_authority_regressions.py`. |
| **C10** | Sec. 7 | **Query-relative finite checks:** declared coverage and complete transport entries produce `CoherentUpTo(N)`, not authority. | `[FIXTURE CONTRACT]` | Verified in Python by `test_finite_shadow.py`; no cofinality theorem is claimed. |
| **C11** | Sec. 8 | **Residual Honesty Taxonomy:** Four-condition linear defect classification; separates exactness from nonzero mass; unchecked or malformed numerical inputs reject authority issuance; unverified repair witnesses withhold authority; label modification fails closed; budget exhaustion triggers honest refusal. | `[IMPLEMENTATION CONTRACT]` | Formalized in Table 3; verified in Python by `test_residual_honesty.py` and `test_reviewer_authority_regressions.py`. |
| **C12** | Sec. 11 | **Scope Boundaries & Non-Claims:** Explicit demarcation of claim limits, compression admissibility, and implementation falsifiability challenge. | `[SCOPE FENCE]` | Declared in §11; verified against negative assertions. |
| **C13** | Sec. 10 | **Deterministic fixture suite:** the fixed rules classify 16 labelled adversarial and 4 labelled benign fixtures as expected. | `[FIXTURE SUITE]` | `code/adversarial_benchmark.py`; no LLM is evaluated and the baseline is hard-coded. |
| **C14** | Sec. 5.4 | **Theorem 3 (Maximal Sound Authority Descent Adjunction):** Transporting authority along $q$ via universal quantification $\forall_q A$ is the right adjoint to inverse image ($q^{-1}(B) \subseteq A \iff B \subseteq \forall_q A$); exact descent holds iff authority is constant on fibers; finite conjunctions distribute. | `[PROVEN]` | Proved in Lean 4 (`AuthorityDescent.lawvere_adjunction`, `exact_preservation_iff_fiber_constant`, `mixed_fiber_obstruction`, `descent_composition`, `descent_conjunction`); finite witness in `code/proved_rows.py`. |

---


## Clarifications in edition 1.3.0

C14 is a predicate theorem. Outside the image of the transport map, universal quantification is vacuously true; operational authorization additionally requires a preimage witness. C10 checks supplied finite coherence, not an infinite cofinality claim. The constructor table is not a causal classifier for arbitrary failures.

## Named regression entry points

These executable checks have the finite scopes described above; they do not establish whole-paper truth.

- `code/tests/test_role_collapse.py::test_role_failure_bijection_completeness`
- `code/tests/test_pipeline.py::test_refusal_left_zero_absorption`
- `code/tests/test_proved_rows.py::test_proved_rows_call_shipped_checker`
