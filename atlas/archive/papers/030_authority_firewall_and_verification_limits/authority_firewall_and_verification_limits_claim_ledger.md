# Claim Ledger: The Authority Firewall and Verification Limits (Paper 030)

**Paper Key:** `001_finite_obstruction_calculus/030_authority_firewall_and_verification_limits`  
**Paper:** `authority_firewall_and_verification_limits_monograph.md`  
**Series:** `001_finite_obstruction_calculus`  
**Date:** 2026-10-08  
**Version:** v2.2.0  
**Status:** RECONCILED_AND_TYPED  

---

## 1. Claim Discipline Summary

1. **What this package supports:**
   - Demonstrates in a finite discrete setting that a four-case calibration suite (positive, negative, collision, metamorphic) acts as a necessary minimum filter to falsify collapsing detectors ($T_{\mathrm{collapse}}$).
   - Demonstrates the Finite Calibration Completeness Theorem: under class-constancy of ground-truth specification $A$ and candidate detector $D$ on an equivalence partition $X / \sim$, global agreement $D = A$ holds if and only if $D(r) = A(r)$ for all representatives $r \in R$.
   - Demonstrates that representative coverage is sharp: omitting any equivalence class admits a class-constant counterexample detector that passes all tested representatives yet fails on the omitted class.
   - Demonstrates that under an object-capability security discipline, untrusted runtime results cannot construct or forge authority capabilities.
   - Shows that fabricated, empty, unbound, or tampered authority witnesses (including arbitrary mocks such as `object()`) are rejected fail-closed to `RefusalDefect`, preventing counterfeit authority certification.
   - Confirms that syntactic completion (fluent halt) routes to `FluentHaltNonAuthority` in the absence of a sovereign descent witness.
   - Validates that six verification axes remain strictly independent with zero cross-axis auto-greening.
   - Bundles a pinned, self-contained master demo runner covering 7 distinct operational scenarios (C1, O1–O7) with 100% deterministic assertion agreement.
   - Demonstrates exact rational arithmetic over discrete obstruction residuals with no floating-point rounding errors.

2. **What this package does not support:**
   - Does not establish detector adequacy across an arbitrary, infinite, or unconstrained prompt/claim class without a verified partition coverage certificate.
   - Does not prove capability non-constructibility against unconstrained set-theoretic constant functions in the absence of an object-capability protected programming model.
   - Does not claim physical realization, continuum mechanics, or general security against out-of-process memory corruption or hostile host kernels.
   - Does not claim that live LLM generative endpoints are governed by these gates without a host proxy integration.

3. **Narrowest defensible claim:**
   - Under declared class-constancy of $A$ and $D$ over a finite partition $X / \sim$, calibration suite $R$ verifies global agreement $D = A$ if and only if $R$ covers every partition class; and within an unprivileged programming context, the `StructuralVerificationGate` enforces fail-closed witness verification and capability encapsulation.

4. **Next test needed:**
   - The Finite Calibration Completeness Theorem is checked in `lean4/Calibration.lean` and by `FinitePartitionCoverage` in `code/proved_rows.py`.
   - Implement asymmetric public-key signature validation (e.g. Ed25519) alongside HMAC in sovereign descent verifier.

---

## 2. Reconciled Claim Register

| Claim ID | Type | Status | Statement | Binding |
|---|---|---|---|---|
| `AVF-030-C01` | `DEFINITION` | `BOUNDED_SPECIFICATION` | Epistemic Separation: $D(x) = \text{pass} \neq \text{Adequate}(D, \mathcal{C}, P) \neq \text{operational authority}$. | Monograph §1; `code/mod_verification_limits_core.py:TerminalVerdict` |
| `AVF-030-C02` | `MINIMUM_CALIBRATION` | `TESTED` | Calibration Requirement: A minimum calibration record requires positive, negative, collision, and metamorphic cases to reject collapsing detectors. | Monograph §2; `code/mod_verification_limits_core.py:MinimumCalibrationRecord`; `test_verification_limits.py:test_minimum_calibration_record_execution` |
| `AVF-030-C03` | `SCOPE_FENCE` | `BOUNDED_SPECIFICATION` | Calibration Inadequacy Boundary: Four calibration examples do not establish adequacy over an unbounded claim class; adequacy requires finite domain exhaustion, an explicit coverage theorem, or a declared bounded domain. | Monograph §2.3; `code/mod_verification_limits_core.py:MinimumCalibrationRecord` |
| `AVF-030-C04` | `IMPLEMENTATION_CONTRACT` | `TESTED` | Capability Non-Constructibility: Under object-capability security, untrusted runtime results cannot construct or forge an `AuthorityCapability`. | Monograph §3; `code/mod_verification_limits_core.py:AuthorityCapability`, `RuntimeResult.to_authority_capability`; `test_verification_limits.py:test_capability_firewall_non_constructibility` |
| `AVF-030-C05` | `IMPLEMENTATION_CONTRACT` | `TESTED` | Sovereign Descent Witnessing: Authority certification requires a cryptographically bound descent witness issued by an authorized sovereign descent verifier. | Monograph §4; `code/mod_verification_limits_core.py:SovereignDescentVerifier`, `AuthorityWitness`; `test_verification_limits.py:test_genuine_sovereign_descent_witness_admission` |
| `AVF-030-C06` | `FALSIFIABILITY` | `TESTED` | Fabricated Witness Rejection: Witnesses with unrecognized verifier IDs, invalid signatures, or mismatched result bindings fail-closed to `RefusalDefect`. | Monograph §4; `code/mod_verification_limits_core.py:StructuralVerificationGate.evaluate_result`; `test_verification_limits.py:test_fabricated_witness_rejection`, `test_unbound_and_tampered_witness_rejection` |
| `AVF-030-C07` | `NEGATIVE_RESULT` | `TESTED` | Collapsing Detector Vulnerability: Constant terminalizers $T_{\text{collapse}}(x) = \text{ExactRepair}$ fail negative and collision calibration checks. | Monograph §2.1; `test_verification_limits.py:test_minimum_calibration_record_execution` |
| `AVF-030-C08` | `DEFINITION` | `TESTED` | Six-Axis Evidence Lattice: Status across Mathematical, Mechanization, Implementation, Empirical, Security, and Authority axes is non-transitive. | Monograph §5; `code/mod_verification_limits_core.py:SixAxisEvidenceLattice`; `test_verification_limits.py:test_six_axis_evidence_lattice_independence` |
| `AVF-030-C09` | `DEFINITION` | `TESTED` | Fluent Halting Non-Authority: Syntactic completion without an authentic sovereign descent witness evaluates to `FluentHaltNonAuthority`. | Monograph §6; `code/mod_verification_limits_core.py:StructuralVerificationGate`; `test_verification_limits.py:test_fluent_halt_non_authority` |
| `AVF-030-C10` | `SCOPE_FENCE` | `TESTED` | Exact Rational Arithmetic: Discrete obstruction calculations and calibration norms are computed over exact rational coordinates (`fractions.Fraction`). | Monograph §7.1; `code/mod_verification_limits_core.py:DiscreteResidual`; `test_verification_limits.py:test_exact_rational_obstruction_properties` |
| `AVF-030-C11` | `THEOREM` | `PROVEN_AND_TESTED` | Finite Calibration Completeness: Under class-constancy of $A$ and $D$ on $X / \sim$, $D = A \iff \forall r \in R, D(r) = A(r)$, with a sharp counterexample construction for any omitted partition class. | Monograph §2.4; `lean4/Calibration.lean`; `code/mod_verification_limits_core.py:FinitePartitionCoverage`; `code/proved_rows.py`; `test_verification_limits.py:test_finite_calibration_completeness_and_sharp_coverage_bound` |
| `AVF-030-C12` | `IMPLEMENTATION_CONTRACT` | `TESTED` | Sealed Authority Witness Protection: Direct untrusted instantiation of `AuthorityWitness`, empty witnesses, and arbitrary object bypasses (`object()`) are rejected fail-closed to `RefusalDefect`. | Monograph §3.1, §4.2; `code/mod_verification_limits_core.py:AuthorityWitness`, `StructuralVerificationGate.evaluate_result`; `test_verification_limits.py:test_witness_forgery_defenses_and_object_bypass` |
| `AVF-030-C13` | `FIXTURE_SUITE` | `TESTED` | Master Demo Benchmark Parity: Pinned self-contained execution across 7 distinct operational scenarios (C1, O1–O7) verifying deterministic routing and failure-closed terminal states. | Monograph §7.4; `code/mod_verification_limits_core.py:run_master_demo_scenarios`; `test_verification_limits.py:test_master_demo_seven_scenarios` |

---

## 3. Open Obligations

| ID | Obligation | Type | Status |
|---|---|---|---|
| `OBL-AVF-01` | Machine-checked Lean 4 proof of Finite Calibration Completeness and the omitted-class counterexample | Lean 4 / Math | DISCHARGED in `lean4/Calibration.lean` |
| `OBL-AVF-02` | Implement asymmetric public-key signature validation (e.g. Ed25519) alongside HMAC in sovereign verifier | Implementation | OPEN |
| `OBL-AVF-03` | Bind Proposal Fidelity Protocol (PFP) prompt pilots to the `StructuralVerificationGate` | System Integration | OPEN |
