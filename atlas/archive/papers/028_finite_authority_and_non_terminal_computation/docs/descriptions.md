# Scientific Description: Finite Authority and Non-Terminal Computation

This deposit contains the complete research package for Finite Authority and Non-Terminal Computation, authored by Jeremy H. Carroll.

Series: 001_finite_obstruction_calculus  
Paper ID: 001_finite_obstruction_calculus/028_finite_authority_and_non_terminal_computation  
Version: 2.0.3 (2026-10-23)  
DOI: not assigned for this prepared edition.  

---

## 1. Context and Problem Statement

Automated reasoning systems, generative language models, and formal program executions generate symbolic traces (proof sketches, token sequences, code edits, simulation results). A widespread category error conflates trace generation or syntactic program halting with normative epistemic or operational authority. Fluency or execution survival is treated as proof of correctness. This monograph formalizes the boundary between non-terminal computation (proposals) and terminalized operational authority, establishing the necessary finite descent machinery required for verifiable certification.

---

## 2. Core Mathematical Contributions

1. Proposal Law Formulation: Precise characterization of model emissions as proposal laws P_theta(gamma | x) that do not imply operational authority without finite descent.
2. Evaluated Path Kernel (EPK): Formalization of accepted proposal mass Z_theta(y | x) across traces under a declared evaluator with exact rational cost and residual suppression.
3. Primitive-Difference LGGR Theorem: Proof that local dashboards can factor through zero-difference quotient spaces while the paired local/global dashboard provably fails to factor due to global cycle obstructions (Local Green != Global Red).
4. C1–C8 Conjunctive Gate Stack: Complete specification of eight operational gates (schema validity, evaluator projection, verifier sovereignty, trust root audit, exhaustive bounds, replay determinism, boundary sufficiency, and terminalization) whose conjunction is required for authority certification.
5. Halting-Authority Non-Implication: Formal demonstration that Turing halting provides a syntactic terminal but does not by itself constitute an evidence terminal.
6. Counterfeit Descent Refusal: Structural criteria for detecting and rejecting counterfeit descent packets where surface signs imitate authority despite non-zero residual obstruction.

---

## 3. Mathematical Framework

- Finite Descent Packets: Formal tuple D = (K, E, V, tau, Lambda) encompassing representation carrier, evaluator, verifier, terminalizer, and lift/repair discipline.
- Scoped Authority Taxonomy: Demarcation of ContractAuthority (schema fulfillment), VerifierScopedAuthority (verifier-relative descent), and the unavailability of SemanticAuthority without a declared semantic adapter.
- Typed Refusal Terminals: Complete catalog of typed failure terminals (NoRepresentation, VerifierRejected, ReplayHashMismatch, BoundaryInsufficient, CounterfeitPacket, etc.) ensuring fail-closed operation.

---

## 4. Computational Implementation and Conformance

The package includes an audited Python reference implementation under `code/mod_finite_authority_core.py` and a unit test suite under `code/tests/`:
- Exact Rational Arithmetic: Evaluated Path Kernel mass and defect fractions computed using fractions.Fraction.
- Gate Stack Validator: Evaluates conjunction across all eight gates and returns typed refusal reasons upon defect detection.
- Halting Non-Implication Tester: Demonstrates that halted execution without verifier gates yields NonAuthorityTerminal.
- Counterfeit Detector: Identifies surface signs (citations, JSON tags, confidence markers) paired with non-zero residual defects.
- LGGR Quotient Obstruction: Validates factorization of local dashboard alongside failure of joint local/global dashboard.

---

## 5. Evaluator Soundness and Non-Claims

This monograph assigns no authorization, changes no jurisdiction, and confers no institutional standing. It does not establish semantic truth or empirical realism. Verifier satisfaction reflects compliance with declared finite checks, not universal truth. The external verifier remains the irreducible trust root.

---

## 6. Scope Boundaries and Falsifiability

- Bounded Discrete Complexes: Formal models apply to finite state systems and discrete computational traces.
- Model Passivity: Evaluator decisions remain independent of generative model parameters or internal chain-of-thought structures.
- Falsifiability: The framework is falsified if any proposal generation process can be shown to establish operational authority without independent verifier descent, or if a local dashboard factorization ensures global section existence across non-trivial cycles.

---

## 7. Deposit Contents

- `finite_authority_and_non_terminal_computation_monograph.md`: Canonical monograph manuscript.
- `finite_authority_and_non_terminal_computation_claim_ledger.md`: Claim status register.
- `finite_authority_and_non_terminal_computation_change_log.md`: Package version log.
- `code/mod_finite_authority_core.py`: Python reference implementation.
- `code/tests/test_finite_authority.py`: Unit test suite.
- `lean4/FiniteAuthority.lean`: Finite proofs checked by `verify_deposit.py --lean`.
- `docs/descriptions.md`: Scientific description register.
- `docs/references.md`: Bibliography and citation register.
- `pyproject.toml`, `zenodo_metadata.json`, `LICENSE`, `LICENSE-CODE`: Metadata and packaging.
- `verify_deposit.py`, `scripts/regen_sha256sums.py`, `tools/rebuild_release.py`: Deterministic verification and release tooling.

---

## 8. Citation and Verification Notice

To verify the deposit:
```bash
py -3.12 -m pytest code/tests/test_finite_authority.py
py -3.12 verify_deposit.py --test code/tests/test_finite_authority.py --lean
```
