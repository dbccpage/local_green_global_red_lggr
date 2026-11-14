# Scientific Description: The Authority Firewall

This deposit contains the complete research package for The Authority Firewall: A Machine-Checked Separation of Evidence from Authority in Finite Systems, authored by Jeremy H. Carroll.

Series: 001_finite_obstruction_calculus  
Paper ID: 001_finite_obstruction_calculus/027_the_authority_firewall_a_machine_checked_separation_of_evidence_from_authority_in_finite_systems  
Version: 2.1.1 (2026-10-23)  

---

## 1. Context and Problem Statement

Automated reasoning and verification systems face a structural hazard: the trust-bootstrap failure mode, in which the evidence of having evaluated or filtered candidate outputs is circularly interpreted as normative certification that the candidate is correct. In self-certifying architectures, candidates that survive local syntactic filters are promoted to certified solutions without independent evaluation. This monograph establishes the Authority Firewall, demonstrating how type-theoretic constructor disjointness strictly separates diagnostic evidence from operational authority in finite verification architectures.

---

## 2. Core Mathematical Contributions

1. Coproduct Summand Decomposition: Formalization of the terminal type as a binary coproduct T = T_auth + (T_res + F_res), isolating authority terminals in the left injection (Sum.inl) and all residual/defect outcomes in the right injection (Sum.inr).
2. Pointwise Separation Theorem: Axiom-free machine-checked verification in Lean 4 proving that no residual terminal inhabits the authority summand: not IsAuth(residualTerminal(r)). The proof relies solely on constructor disjointness (Sum.noConfusion).
3. Dependent Family Emptiness: Derivation that the authority-extracting dependent family Pi_r IsAuth(residualTerminal(r)) is uninhabited whenever any residual outcome exists.
4. Seven-Guard Operational Specification: Formulation of the seven-guard authority predicate (IsAuthGuards) requiring verified replay hash, matching replay, terminalizer presence, exhaustive search (kappa = 0), zero defect (delta = 0), descent witness, and replay freshness.
5. Worked Negative Instance: Analysis of an audited solver showing how missing Pareto-optimal truth tables and unseparated evaluator boundaries trigger firewall refusal, confining solver output to diagnostic residuals.
6. Mechanization of Seven Operational Guards: Machine-checked verification in Lean 4 proving that operational authority IsAuth_S factors through structural coproduct authority (is_auth_s_factors_through_is_auth).
7. Typed Component Bridge: Formalization of the discrete diagnostic cochain complex (C⁰, C¹, d⁰) and proof that non-repairable obstruction classes map to diagnostic terminals strictly disjoint from authority terminals and falsify truthful delta guards.

---

## 3. Mathematical Framework

- Two-Lane Architecture: The verification topology divides into an Obstruction Evidence Lane (defect detection, transition reindexing, and diagnostic composition) and a Descent Authority Lane (finite descent verification, finite-shadow evaluation, and residual closure).
- Constructor Disjointness: Enforcement of [q] in Q^1 does not imply Auth via the structural impossibility of Sum.inr = Sum.inl.
- Scoped Authority Boundaries: Explicit demarcation between ContractAuthority (schema fulfillment), VerifierScopedAuthority (rule satisfaction under a declared verifier), and SemanticAuthority (real-world truth, declared unavailable without a semantic adapter).

---

## 4. Computational Implementation and Conformance

The package includes an audited Python reference implementation under `code/mod_authority_firewall_core.py` and a unit test suite under `code/tests/`:
- Exact Rational Arithmetic: Exact representation of defect mass using `fractions.Fraction`.
- Strict Coproduct Sum Type: Strict runtime enforcement of binary coproduct contract requiring exactly one non-null tag-consistent payload of valid class (`AuthEvidence`, `ResidualClass`, or `ResidualFailure`), rejecting empty payloads, mismatched classes, and invalid tags.
- Seven-Guard Conjunction Validator: Strict runtime evaluation requiring actual boolean values for all seven certification flags (verified replay hash, matching replay, terminalizer presence, exhaustive search $\kappa = 0$, zero defect $\delta = 0$, descent witness, replay freshness), rejecting string-encoded flags or blank evidence IDs. The boolean flags represent externally verified certificate attributes rather than an in-band re-execution engine.
- Solver Audit Simulation: Simulation of the Section 4 adversarial audit scenario demonstrating fail-closed rejection of self-certification for stipulated inputs.

---

## 5. Evaluator Soundness and Non-Claims

This monograph assigns no authorization, changes no jurisdiction, and confers no institutional standing. It does not establish semantic truth or empirical realism. The Lean 4 theorem establishes structural coproduct disjointness within a declared type discipline; it does not claim to eliminate the irreducible trust root (C4: external verifier audit).

---

## 6. Scope Boundaries and Falsifiability

- Bounded Discrete Complexes: Formal results apply to finite type systems and discrete verification complexes.
- Categorical Conditional: The categorical form Nat(Omega_LambdaOmega, Auth) = empty remains conditional on a prose reduction and component bridge.
- Falsifiability: The framework is falsified if any valid term of type IsAuth(residualTerminal(r)) can be constructed, or if residual diagnostic evidence can directly trigger an authority gate without external descent evidence.

---

## 7. Deposit Contents

- `authority_firewall_monograph.md`: Canonical monograph manuscript.
- `authority_firewall_claim_ledger.md`: Claim status register.
- `the_authority_firewall_a_machine_checked_separation_of_evidence_from_authority_in_finite_systems_change_log.md`: Package version log.
- `code/mod_authority_firewall_core.py`: Python reference implementation.
- `code/tests/test_authority_firewall.py`: Unit test suite (11 tests).
- `docs/descriptions.md`: Scientific description register.
- `docs/references.md`: Bibliography and citation register.
- `lean4/ResidualNonCreation.lean`: Self-contained bundled Lean 4 verification kernel.
- `pyproject.toml`, `zenodo_metadata.json`, `LICENSE`, `LICENSE-CODE`: Metadata and packaging.
- `verify_deposit.py`, `scripts/regen_sha256sums.py`, `tools/rebuild_release.py`: Deterministic verification and release tooling.

---

## 8. Citation and Verification Notice

To verify the deposit:
```bash
py -3.12 -m pytest code/tests/test_authority_firewall.py
py -3.12 verify_deposit.py --test code/tests/test_authority_firewall.py
```
