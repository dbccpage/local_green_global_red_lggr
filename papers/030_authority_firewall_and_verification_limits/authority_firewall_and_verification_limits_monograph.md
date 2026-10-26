# The Authority Firewall and Verification Limits: Structural Verification, Detector Adequacy, and Capability Non-Constructibility

**Monograph Series:** Monograph 030 (Finite Obstruction Calculus Program)  
**Author:** Jeremy H. Carroll  
**Series:** `001_finite_obstruction_calculus`  
**Paper Key:** `001_finite_obstruction_calculus/030_authority_firewall_and_verification_limits`  
**Date:** 2026-10-08  
**Version:** 2.2.0  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0) / MIT (Code)  
**Status:** WORKING_SPECIFICATION_AND_REFERENCE_IMPLEMENTATION  
**Authority Notice:** *This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing.*

---

## Abstract

Automated verification architectures and autonomous evaluation agents face a systemic failure mode: conflating fluent text completion or syntactic halting with structural authority. We investigate the operational boundaries of verification systems, focusing on three structural hazards:
1. **Detector Collapse and False-Green Gating:** A coarse or constant detector can mark every candidate as an exact repair. We analyze the four-case calibration suite (positive, negative, collision, metamorphic), showing that while it forms a necessary **minimum calibration record** to reject collapsing detectors, four examples cannot establish detector adequacy over an unbounded claim class without a domain coverage certificate. We prove the **Finite Calibration Completeness Theorem** and establish a sharp partition coverage bound.
2. **Capability Non-Constructibility under Object-Capability Security:** We formalize capability isolation, showing that within an untrusted evaluation environment with access only to runtime execution results, no computable program can construct or forge an unsealed authority capability. We tie this to production Rust capability patterns (`HostPromotionCapabilityV1`).
3. **Defense Against Fabricated Evidence:** We examine how authority gates can be deceived by unverified witness tokens. We specify a fail-closed sovereign descent gate that validates cryptographic witness signatures and binds tokens directly to result payloads, rejecting fabricated or unbound evidence.

All computational claims are accompanied by an audited reference implementation in Python 3.12 utilizing exact rational arithmetic (`fractions.Fraction`).

---

## 1. Epistemic Posture and Core Separations

Classical generative systems treat generation termination as a proxy for task success. That proxy fails for authority-sensitive claims. The fundamental premise of this monograph is the strict separation between three distinct categories:

$$\boxed{D(x) = \text{pass} \;\neq\; \text{Adequate}(D, \mathcal{C}, P) \;\neq\; \text{operational authority}}$$

$$\boxed{\text{fluent halt} \;\neq\; \text{structural authority}}$$

$$\boxed{\text{routing terminal} \;\neq\; \text{authority terminal}}$$

- **Detector Passage ($D(x) = \text{pass}$):** Indicates that an evaluated candidate satisfies the immediate predicates of a local detector $D$.
- **Detector Adequacy ($\text{Adequate}(D, \mathcal{C}, P)$):** Signifies that detector $D$ has been certified adequate with respect to a claim class $\mathcal{C}$ and observer profile $P$.
- **Operational Authority:** A sovereign, non-transferable entitlement to execute actions or alter institutional estate state. Authority cannot be minted by runtime evaluators or language model self-certification.

---

## 2. Detector Adequacy vs. Minimum Calibration Records

### 2.1 The Hazard of Collapsing Detectors

Consider a residual carrier $W = \{r_0, r_1\}$ where $r_0$ represents a non-zero obstruction that must refuse promotion, and $r_1$ represents a validly closed boundary. Define the constant terminalizer:

$$T_{\mathrm{collapse}}(r) := \mathsf{ExactRepair} \quad \forall r \in W$$

$T_{\mathrm{collapse}}$ satisfies totality and emits a positive terminal for every input. If an evaluation architecture promotes candidates whenever $T(r) = \mathsf{ExactRepair}$, it admits false-green verifications across defective inputs.

### 2.2 The Four-Case Minimum Calibration Record

To prevent trivial or constant collapse, an evaluation gate must require a calibration record comprising at least four distinct cases:

1. **Positive Case ($x_{\mathrm{pos}}$):** A valid, known-sound input where $D(x_{\mathrm{pos}}) = \text{pass}$ is required.
2. **Negative Case ($x_{\mathrm{neg}}$):** An invalid or defective input where $D(x_{\mathrm{neg}}) = \text{refuse}$ is required.
3. **Collision Pair ($x_{\mathrm{col}, 1}, x_{\mathrm{col}, 2}$):** Distinct protected defect states that must not be collapsed into identical passing terminals.
4. **Metamorphic Pair ($x, x'$):** An invariant-preserving transformation (e.g. gauge rewrite or coordinate permutation) where $D(x) = D(x')$ must hold.

### 2.3 The Calibration Boundary: Necessary vs. Sufficient

A critical mathematical boundary must be explicitly stated:

> **Boundary Condition:** A four-case calibration suite constitutes a **minimum calibration record**, not a proof of detector adequacy over an arbitrary claim class $\mathcal{C}$.

A detector can behave correctly on all four calibration cases and fail on an untested fifth case. Therefore, adequacy over a claim class cannot be inferred from four test cases alone. True adequacy requires:
1. An exhaustive enumeration over a finite, closed domain $\mathcal{C}$, or
2. A formal partition coverage theorem certifying that all equivalence classes of $\mathcal{C}$ are bounded by the calibration suite, or
3. An explicitly declared and bounded claim scope.

When an evaluation gate operates without a verified adequacy proof, positive routes must fail-close to `DetectorInadequate` rather than assuming adequacy.

### 2.4 Finite Calibration Completeness with Sharp Coverage Bound

To provide a mathematically precise criterion for when calibration evidence covers a declared claim space, consider a finite carrier $X$, a ground-truth specification $A: X \to \{0,1\}$, and a candidate detector $D: X \to \{0,1\}$.

Let $\sim$ be an equivalence relation on $X$ generated by declared invariant-preserving rewrites (e.g., coordinate permutations or sign flips). Suppose $A$ and $D$ are independently established to be class-constant on the quotient partition $X / \sim$:

$$\forall x_1, x_2 \in X, \quad x_1 \sim x_2 \implies A(x_1) = A(x_2) \;\land\; D(x_1) = D(x_2)$$

Let $R \subseteq X$ be a set of calibration representatives containing at least one element from every equivalence class of $X / \sim$.

> **Theorem (Finite Calibration Completeness):** Under the assumption that $A$ and $D$ are class-constant on $X / \sim$, the detector agrees with the specification globally on $X$ if and only if it agrees on the representative set $R$:
> $$D = A \iff \forall r \in R, \; D(r) = A(r)$$

*Proof.* The forward implication ($\implies$) is immediate since $R \subseteq X$. For the converse ($\impliedby$), let $x \in X$ be arbitrary. Because $R$ contains a representative from every equivalence class, there exists $r \in R$ such that $x \sim r$. By class-constancy of $D$ and $A$, $D(x) = D(r)$ and $A(x) = A(r)$. By assumption, $D(r) = A(r)$, whence $D(x) = A(x)$. Since $x$ was arbitrary, $D = A$ on $X$. $\square$

> **Proposition (Sharpness of Representative Coverage):** The coverage requirement $|R \cap [x]| \ge 1$ for all $[x] \in X / \sim$ is sharp. If any equivalence class $C_k \in X / \sim$ is omitted from $R$, there exists a class-constant detector $D_{\mathrm{counter}}$ that agrees with $A$ on all tested representatives $r \in R$, yet fails precisely on $C_k$:
> $$\forall r \in R, \; D_{\mathrm{counter}}(r) = A(r), \quad \text{yet} \quad \exists x \in C_k, \; D_{\mathrm{counter}}(x) \neq A(x)$$

*Proof.* Define $D_{\mathrm{counter}}$ by setting $D_{\mathrm{counter}}(x) := A(x)$ for all $x \notin C_k$, and $D_{\mathrm{counter}}(x) := 1 - A(x)$ for all $x \in C_k$. Because $A$ is constant on $C_k$, $1 - A(x)$ is constant on $C_k$, so $D_{\mathrm{counter}}$ is class-constant on $X / \sim$. Since $C_k \cap R = \emptyset$, $D_{\mathrm{counter}}(r) = A(r)$ for all $r \in R$. However, for any $x \in C_k$, $D_{\mathrm{counter}}(x) = 1 - A(x) \neq A(x)$, demonstrating $D_{\mathrm{counter}} \neq A$. $\square$

This theorem provides an operational test for calibration coverage: calibration evidence covers the claim space exactly when the test suite covers all equivalence classes of a declared invariant partition. Omitting even one class admits a class-constant counterexample detector.

---

## 3. Capability Non-Constructibility under Object-Capability Security

### 3.1 Restricted Construction vs. Set-Theoretic Functions

In mathematical discourse, the proposition:

$$\neg\exists f\colon \mathsf{RuntimeResult} \to \mathsf{AuthorityCapability}$$

is false if stated over all set-theoretic functions whenever $\mathsf{AuthorityCapability}$ is non-empty, because a constant function $f(r) = c$ already exists for any chosen $c \in \mathsf{AuthorityCapability}$.

The intended claim is **computational non-constructibility within an unprivileged programming context under object-capability security**:

> **Theorem (Capability Non-Constructibility):** Given an unprivileged programming context $\mathcal{E}$ possessing only the public runtime interface $\mathcal{I}_{\mathrm{untrusted}}$ and access to a `RuntimeResult` $r$, there exists no computable program in $\mathcal{E}$ that can construct, mint, or forge an `AuthorityCapability`.

This scoped property is realized in production systems via private encapsulation fences:
- In the Python reference engine, `AuthorityCapability` and `AuthorityWitness` require a private `_token: _CapabilityToken` held exclusively by `_SOVEREIGN_TOKEN`, raising `CapabilityViolationError` on direct instantiation.
- In sovereign Rust kernels (`omega_contracts::certificate_promotion`), the host authority surface [`HostPromotionCapabilityV1`](../../../../../omega_engine/crates_rs/omega_contracts/src/certificate_promotion.rs#L341-L362) has private fields (`_seal: HostPromotionSeal`), possesses no public constructor, and cannot be cloned or deserialized, enforced by a compile-fail contract (`compile_fail`).

### 3.2 Trust Assumptions and Protected Interface

The capability firewall rests upon three explicit trust assumptions:
1. **Unforgeable Token Protection:** The `AuthorityCapability` and `AuthorityWitness` types possess sealed, private constructors that require an unforgeable sovereign token $\kappa_{\mathrm{sovereign}}$.
2. **Private Capability Minting:** $\kappa_{\mathrm{sovereign}}$ is held exclusively by an out-of-band `SovereignDescentVerifier` and is inaccessible to untrusted worker processes.
3. **Sandbox Memory Integrity:** The runtime execution sandbox cannot read verifier memory, intercept verifier secret keys, or forge cryptographic signatures.

If an untrusted caller attempts to invoke `result.to_authority_capability()` or instantiate `AuthorityCapability` directly, the system raises a typed `CapabilityViolationError`.

---

## 4. Defense Against Fabricated Evidence and Sovereign Descent Gating

### 4.1 Vulnerability to Fabricated Witnesses

A critical defect in naive authority firewalls is accepting unverified witness data. If a gate accepts:

$$\mathsf{AuthorityWitness}(\text{verifier\_id} = \text{"invented"}, \text{token\_hash} = \text{"not-a-hash"})$$

and emits `AuthorityCertified`, the firewall has failed: anyone can forge authority by providing synthetic strings.

### 4.2 The Sovereign Descent Verification Gate

To prevent counterfeit authority, the `StructuralVerificationGate` enforces a multi-stage fail-closed evaluation pipeline:

```text
Runtime Candidate Output
  │
  ├── 1. Syntactic Halt Check ────────── [Not Halted] ──> FluentHaltNonAuthority
  │
  ├── 2. Primary Detector Pass Check ──── [Failed] ──────> RefusalDefect
  │
  ├── 3. Minimum Calibration Check ────── [Inadequate] ──> DetectorInadequate
  │
  └── 4. Sovereign Witness Validation
          ├── Verifier registered? ───── [No] ───────────> RefusalDefect
          ├── Result ID bound? ────────── [No] ───────────> RefusalDefect
          ├── Content hash matches? ──── [No] ───────────> RefusalDefect
          ├── Signature authentic? ───── [No] ───────────> RefusalDefect
          ├── [Witness Valid & Bound] ───────────────────> AuthorityCertified
          └── [No Witness Provided] ─────────────────────> FluentHaltNonAuthority
```

Under this discipline:
- Fabricated or synthetic verifier IDs are rejected immediately.
- Passing arbitrary untyped objects (e.g. `object()`) or empty witnesses returns `RefusalDefect` fail-closed.
- `AuthorityWitness` requires an internal sovereign capability token (`_SOVEREIGN_TOKEN`), preventing direct instantiation by untrusted callers.
- Witnesses generated for a different candidate result cannot be reused (unbound witness rejection).
- Post-hoc tampering with candidate output invalidates the content hash and signature.
- Only authentic witnesses issued by a registered `SovereignDescentVerifier` over an exact zero residual can yield `AuthorityCertified`.

---

## 5. The Six-Axis Evidence Lattice

Verification claims in the Omega framework are structured across six orthogonal axes:

| Axis | Meaning | Governing Artifact |
|---|---|---|
| **Mathematical** | Analytical proof under declared hypotheses | Monograph definitions and theorems |
| **Mechanization** | Machine-checked proof in Lean 4 | Lake build receipt + axiom audit |
| **Implementation** | Tested executable code in Rust or Python | Crate tests, sealed constructors |
| **Empirical** | Replayable benchmarks and numerical runs | Test receipts, execution logs |
| **Security** | Tamper-resistance and capability boundaries | Sandbox policies, private tokens |
| **Authority** | Sovereign finite descent verification | Sealed cryptographic witness |

> **Independence Invariant:** Status across the six axes is strictly non-transitive. Green status on one axis never implies or permits auto-greening of another axis:
> $$\text{can\_auto\_promote}(A_i, A_j) = \text{False} \quad \forall i \neq j$$

A system with complete mathematical and mechanization proofs remains unverified on the implementation axis until executable tests pass.

---

## 6. Structural Verification vs. Classical Halting

The contrast between classical halting and structural verification is summarized below:

| Dimension | Classical Generative System | Omega Structural Architecture |
|---|---|---|
| **Stop Condition** | EOS token / fluent completion | Typed routing terminal after declared checks |
| **Success Proxy** | Syntactic fluency / length / self-report | Exact residual check + sovereign descent witness |
| **Authority** | Implicit ("audit complete") | Explicit `AuthorityStatus: None` by default |
| **Missing Checks** | Silent acceptance | `DetectorInadequate` / `NoRule` / `RefusalDefect` |
| **Residual State** | Invisible | `DiscreteResidual` with exact rational coordinates |
| **Multi-Agent Consensus** | Voting / averaging | Observer comparison envelope + support sieve |

---

## 7. Reference Implementation and Exact Rational Arithmetic

### 7.1 Exact Rational Discrete Residuals

To ensure that numerical evaluations do not suffer from floating-point imprecision or false convergence, all discrete obstruction residuals are modeled in exact rational arithmetic:

```python
from fractions import Fraction

@dataclass(frozen=True)
class DiscreteResidual:
    coordinates: tuple[Fraction, ...]
    
    @property
    def norm1(self) -> Fraction:
        return sum(abs(c) for c in self.coordinates) if self.coordinates else Fraction(0, 1)

    @property
    def is_exact_zero(self) -> bool:
        return self.norm1 == Fraction(0, 1)
```

### 7.2 Tested Code and Test Suite

The package includes an audited Python 3.12 reference implementation in [`code/mod_verification_limits_core.py`](code/mod_verification_limits_core.py) and a 11-case unit test suite in [`code/tests/test_verification_limits.py`](code/tests/test_verification_limits.py):

1. `test_exact_rational_obstruction_properties`: Validates exact fraction arithmetic and $\ell_1$ norm calculation.
2. `test_minimum_calibration_record_execution`: Verifies that sound detectors pass calibration while collapsing detectors ($T_{\mathrm{collapse}}$) fail-close to `DetectorInadequate`.
3. `test_fabricated_witness_rejection`: Reproduces the peer review exploit, ensuring that invented witness tokens evaluate to `RefusalDefect`.
4. `test_witness_forgery_defenses_and_object_bypass`: Validates that `object()`, empty witnesses, and non-zero residual witnesses return `RefusalDefect`.
5. `test_unbound_and_tampered_witness_rejection`: Confirms that reusing witnesses across different result IDs or tampering with output data triggers refusal.
6. `test_genuine_sovereign_descent_witness_admission`: Validates that authentic descent witnesses over exact zero residuals yield `AuthorityCertified`.
7. `test_capability_firewall_non_constructibility`: Verifies that direct instantiation of `AuthorityCapability` or calling `result.to_authority_capability()` raises `CapabilityViolationError`.
8. `test_fluent_halt_non_authority`: Confirms that fluent completion without a descent witness routes to `FluentHaltNonAuthority`.
9. `test_six_axis_evidence_lattice_independence`: Verifies that cross-axis promotion is rejected across all six axes.
10. `test_finite_calibration_completeness_and_sharp_coverage_bound`: Validates the Finite Calibration Completeness Theorem and tests sharpness via counterexample detector construction.
11. `test_master_demo_seven_scenarios`: Executes the full 7-scenario classical vs. Omega benchmark (`run_master_demo_scenarios`).

### 7.3 Master Demo Seven-Scenario Benchmark

The package bundles a self-contained, replayable master demo runner in `mod_verification_limits_core.py` (`run_master_demo_scenarios()`) covering all historical scenarios:
- **C1 (Classical Fluent Halting):** Model emits fluent SOC2 compliance paragraph without structural descent witness $\to$ `FluentHaltNonAuthority`.
- **O1 (Missing Descent Packet):** Claim submitted without calibration record $\to$ `DetectorInadequate`.
- **O2 (Open Residual Conflict):** Partial residual declared open with non-zero boundary defect $\to$ `RefusalDefect`.
- **O3 (Budget Exhaustion):** Resource ceiling reached before closure $\to$ `RefusalDefect`.
- **O4 (Continuum Claim Debt):** Infinite continuum claim without finite shadow projection $\to$ `DetectorInadequate`.
- **O5 (Uncertified Transport):** Representation shift lacking certified transport $\chi_F$ $\to$ `RefusalDefect`.
- **O6 (Consensus Laundering):** Multi-model majority voting lacking component descent $\to$ `RefusalDefect`.
- **O7 (Certified Baseline):** Verified exact zero residual with sovereign cryptographic witness $\to$ `AuthorityCertified`.

### 7.4 Reproducibility Commands

To verify the implementation locally:

```bash
# Execute unit test suite
py -3.12 -m pytest code/tests/test_verification_limits.py -v

# Execute deposit verification runner
py -3.12 verify_deposit.py --test
```

---

## 8. Conclusion and Nonclaims

1. **What this package supports:**
   - Demonstrates that a four-case calibration suite serves as a necessary minimum filter against collapsing detectors in a finite discrete setting.
   - Demonstrates the Finite Calibration Completeness Theorem, showing $D = A$ on a finite carrier under invariant-preserving partitions, and demonstrates sharpness via explicit counterexample detector construction.
   - Shows that capability-protected interfaces prevent untrusted runtime results from constructing authority capabilities or witnesses.
   - Demonstrates that binding authority witnesses to result payloads and verifier keys prevents fabricated evidence from obtaining certification.
   - Verifies all seven master demo scenarios in a deterministic, replayable test suite without broken external links.
   - Shows exact rational evaluation of obstruction residuals without floating-point errors.

2. **What this package does not support:**
   - Does not establish detector adequacy across an arbitrary, infinite, or unconstrained prompt/claim class.
   - Does not prove capability non-constructibility for arbitrary mathematical functions outside an object-capability security model.
   - Does not assert continuum dynamics, physical authority, or general security against out-of-process memory corruption.

---

## References

1. Carroll, J. H. (2026). *The Authority Firewall: A Machine-Checked Separation of Evidence from Authority in Finite Systems*. Monograph 027, Finite Obstruction Calculus Series.
2. Carroll, J. H. (2026). *Witnessed Difference, Finite Distinction Carriers, and History Escape*. Monograph 032, Finite Obstruction Calculus Series.
3. Miller, M. S. (2006). *Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control*. Johns Hopkins University Dissertation.
4. Saltzer, J. H., & Schroeder, M. D. (1975). *The protection of information in computer systems*. Proceedings of the IEEE, 63(9), 1278-1308.
