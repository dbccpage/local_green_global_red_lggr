# Local Green, Global Red Foundational Series: From Evaluator Defect Calculus to Omega Engine Crate Architecture

AuthorityEffect: None.

> "A modular interface can pass every local check and still fail its global check. This monograph details the mathematical theory, Lean 4 proofs, and software crate implementation of Evaluated Path Kernels and the Local Green, Global Red foundational series."

---

## 1. Introduction & The Core Problem

In modern autonomous computing, distributed multi-agent systems, and formal verification frameworks, complex tasks are decomposed into discrete, modular subtasks. Each subtask is assigned a local evaluator $E_i: X_i \to \{0, 1\}$, while an end-to-end composite evaluator $E_g: X \to \{0, 1\}$ monitors the global outcome.

Under naive compositional assumptions, engineers expect that if every component passes its local acceptance gate ($E_1 = 1, E_2 = 1, \dots, E_k = 1$), the combined system must succeed ($E_g = 1$).

The **Local Green, Global Red (LGGR)** research programme demonstrates that this assumption is mathematically false whenever the global property relies on joint state constraints not fully projected onto individual local boundaries.

### The Evaluator Defect Functional

Let $X$ be the composite state space, and let $\pi_i: X \to X_i$ be local projection operators. Given local evaluators $E_i: X_i \to \{0, 1\}$ and a global evaluator $E_g: X \to \{0, 1\}$, the **signed evaluator defect** is defined as:

$$\Delta_E(x) = E_g(x) - \prod_{i=1}^k E_i(\pi_i(x)) \in \{-1, 0, 1\}$$

Three distinct operational regimes emerge:
1. **$\Delta_E = 0$ (Sound Agreement):** The global outcome matches the product of local outcomes ($1 - 1 = 0$ or $0 - 0 = 0$).
2. **$\Delta_E = +1$ (Local Red, Global Green):** At least one local evaluator failed, yet the global evaluator succeeded. This occurs when local contracts are overly conservative.
3. **$\Delta_E = -1$ (Local Green, Global Red):** Every local evaluator reports success ($E_i = 1$ for all $i$), but the global evaluator fails ($E_g = 0$).

The state $\Delta_E = -1$ is a **catastrophic blind spot**. Local monitoring dashboards illuminate green across all subsystems, yet the composed pipeline fails closed.

---

## 2. The Six Foundational Papers

The foundational theory was authored and archived across six monographs in [`coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/`](../../../omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series):

```
+---------------------------------------------------------------------------------------------------+
|                     001_local_green_global_red_foundational_series                                |
+---------------------------------------------------------------------------------------------------+
|  Volume I: Evaluated Path Kernels (EPK) for Composed Agent Reliability                            |
|    - Non-commutative path composition; trace validation; Delta_E in {-1, 0, 1}                    |
+---------------------------------------------------------------------------------------------------+
|  Volume II: Organizational Evaluator Gluing and Sheaf Obstructions                                |
|    - Local checks on covers U_i vs global section agreement; quotient obstructions               |
+---------------------------------------------------------------------------------------------------+
|  Volume III: EPK-GTLA Overlay Across Six System Roles                                             |
|    - Game-Theoretic Learning Architecture: Planner, Proposer, Governor, Worker, Arbiter, Auditor  |
+---------------------------------------------------------------------------------------------------+
|  Volume IV: Finite Presentations & Completion-Relative Obstruction                                |
|    - 2-adic inverse systems, thread existence (Stacks 086J), reflection map eta, derived R^1 lim  |
+---------------------------------------------------------------------------------------------------+
|  Volume V: Local Green, Global Red: A Finite No-Recovery Theorem                                  |
|    - Blind spots, 6-site graph realization, unrecoverable defect at distance 2                    |
+---------------------------------------------------------------------------------------------------+
|  Volume VI: Blind Spots Under Nonlinear Aggregation and Adjoint Probing                           |
|    - Observation map Q, Gram operator Q^T Q, adjoint reconstruction of ker(Q)                     |
+---------------------------------------------------------------------------------------------------+
```

### Volume I: Evaluated Path Kernels (EPK) for Composed Agent Reliability
- **Core Result:** Defines the evaluated path kernel (EPK) over discrete transitions. An agent trace $\tau = (s_0 \xrightarrow{a_1} s_1 \xrightarrow{a_2} \dots \xrightarrow{a_n} s_n)$ has an associated evaluation functional.
- **Compositionality Theorem:** shows in this model that kernel composition $K_2 \circ K_1$ preserves soundness if and only if intermediate state interfaces satisfy exact boundary conditions.
- **Reference Code:** `code/epk_core.py`.
- **Lean 4 Mechanization:** shows in this model algebraic properties of path-ordered evaluation.

### Volume II: Organizational Evaluator Gluing
- **Core Result:** Formulates local-to-global evaluation in the language of sheaf theory on open coverings $\{U_i\}$. A global section exists if and only if pairwise restrictions agree on intersections $U_i \cap U_j$.
- **Quotient Obstruction:** shows in this model that when an organization or multi-agent team groups disparate states into a single equivalence class, the global evaluator may vary within that class, generating a non-trivial quotient obstruction.
- **Four Governance Requirements:**
  1. *Representational Sufficiency*: The local boundary must encode all variables checked by the global validator.
  2. *Accountable Ownership*: Every boundary must have an identified agent with authority to modify it.
  3. *Temporal Coherence*: Evaluation must occur at synchronous logical timestamps.
  4. *Evaluator Agreement*: Local and global predicates must be calibrated against a common domain model.

### Volume III: EPK-GTLA Overlay Across Six System Roles
- **Core Result:** Integrates EPKs with the Game-Theoretic Learning Architecture (GTLA), defining six mutually adversarial system roles:
  1. **Planner:** Decomposes global tasks into directed sub-contracts.
  2. **Proposer:** Synthesizes candidate transformations and code patches.
  3. **Governor:** Enforces immutable boundary invariants.
  4. **Worker:** Executes isolated steps within sandbox containers.
  5. **Arbiter:** Renders binary verdicts over local contract completions.
  6. **Auditor:** Recomputes independent end-to-end evidence receipts.
- **Payoff Matrix:** Structures payoff incentives such that collusive agreements between Worker and Arbiter are penalized whenever the independent Auditor detects $\Delta_E = -1$.

### Volume IV: Finite Presentations & Completion-Relative Obstruction
- **Core Result:** Studies inverse systems of finite presentations $(X_n, f_n)_{n \in \mathbb{N}}$. By Stacks Project Tag 086J, any inverse system of non-empty finite sets has a non-empty inverse limit:
  $$\varprojlim X_n \ne \emptyset$$
  However, having a solution at every finite stage $n$ does **not** imply that a solution exists in the base carrier!
- **The $2$-Adic Countermodel:**
  Consider the congruence $3x + 1 \equiv 0 \pmod{2^n}$.
  For every finite $n \ge 1$, an exact integer solution exists:
  $$x_n = -\sum_{k=0}^{n-1} (-2)^k \in \mathbb{Z}$$
  These solutions form a compatible thread. Yet no integer $x \in \mathbb{Z}$ solves the equation globally, because $3x + 1 = 0 \implies x = -1/3 \notin \mathbb{Z}$. The thread converges only in the completion $\mathbb{Z}_2$.
- **Reflection Criterion:** A thread descends to an original carrier solution if and only if it lies in the image of the canonical reflection map $\eta: X \to \widehat{X}$.
- **Derived Inverse Limits ($R^1 \varprojlim$):** shows in this model that lifting obstructions in abelian towers vanish if and only if transition kernels satisfy the Mittag-Leffler condition (Stacks Tag 07KV).

### Volume V: Local Green, Global Red: The Finite No-Recovery Theorem
- **Core Result:** Establishes the No-Recovery Theorem: **No finite-valued function of local evaluator scores can bound true global inconsistency.**
- **Blind-Spot Geometry:** If an unobserved degree of freedom $\xi$ exists such that $\pi_i(x + \xi) = \pi_i(x)$ for all $i$, then local evaluators are completely invariant under translations by $\xi$.
- **Distance-2 Defect Pattern:** In a concrete six-site graph realization, constructs an explicit defect pattern that lies at exact Hamming distance 2 from every possible valid repair, proving that localized greedy repairs cannot close the defect.

### Volume VI: Blind Spots Under Nonlinear Aggregation and Adjoint Probing
- **Core Result:** Investigates nonlinear observation operators $Q: V \to W$.
- **Gram Operator ($Q^T Q$):** Demonstrates that defects residing in $\ker(Q)$ remain undetectable by any feed-forward evaluation.
- **Adjoint Probing:** Develops an adjoint test: by applying dual witnesses $w \in W^*$ and pulling back via $Q^T$, the host detects whether hidden state variations perturb global invariants, effectively illuminating the blind spot.

---

## 3. Omega Engine Crate Architecture

Inside the Omega Engine monorepo, these mathematical principles are codified into a sovereign production crate:
[`omega_engine/crates_rs/omega_local_green_global_red_lggr/`](../16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md#L1868)

### Crate File & Module Inventory

```text
omega_engine/crates_rs/omega_local_green_global_red_lggr/
├── core.py                   # EvaluatedPathKernel base protocols & dataclasses
├── defects.py                # Exact rational evaluator defect calculation (Delta_E)
├── composition.py            # Path-ordered tensor product and composition operators
├── epk.py                    # Concrete Evaluated Path Kernel implementation
├── epk_overlay.py            # Six-role GTLA overlay interfaces
├── evaluation_harness.py     # Multi-agent test runner detecting local-green/global-red
├── ledger.py                 # Append-only hash chain of evaluator receipts
├── lggr_overlay.py           # Clean Architecture adapter injecting LGGR guards
├── metrics.py                # Duality gap and coboundary leakage metrics
├── bound_measurement.py      # Exact rational interval bounds for observation maps
└── examples/
    ├── activation_density.py # Density matrix test cases
    ├── poe_vs_moe.py         # Product-of-experts vs Mixture-of-experts defects
    └── swe_patch.py          # Software engineering patch regression harness
```

### Inward Dependency Flow

The crate strictly respects Clean Architecture:
- Depends inward on:
  - `omega_engine.crates.contract_core`: Immutable contracts and type definitions.
  - `omega_engine.crates.category_theory`: Functorial maps and monoidal composition.
  - `omega_engine.crates.sheaf_theory`: Restriction maps and overlap gluing.
  - `omega_engine.crates.type`: Exact rational types and setoids.
- Emits to:
  - `omega_engine_pfp/domain/ast_cochain/models.py`: Defines enum `LggrVerdict.REFUSED_LOCAL_GREEN_GLOBAL_RED`.

---

## 4. Integration with the Symbol Game

In the Symbol Game runtime (`omega_engine_pfp`), the evaluator defect is linked directly to AST cohomology:

$$\Phi_1(h) = \|d_0 h\|_1 \quad (\text{Boundary Leakage})$$
$$\Gamma_2(h) = \|d_1 h\|_1 \quad (\text{Cycle Obstruction})$$

When an external model or subagent proposes a code patch or geometric triangulation:
1. Local linters and unit tests may report green ($E_{\text{lint}} = 1, E_{\text{unit}} = 1$).
2. The Symbol Game host evaluates the global AST coboundary matrix $d_0$.
3. If $\Phi_1 > 0$ or $\Gamma_2 > 0$, the composite evaluator sets $E_g = 0$.
4. The defect functional yields:
   $$\Delta_E = 0 - (1 \times 1) = -1$$
5. The host referee triggers a fail-closed refusal:
   $$\text{verdict} = \boxed{\text{REFUSED\_LOCAL\_GREEN\_GLOBAL\_RED}}$$

---

## 5. Claim Hygiene Summary

1. **What this document supports:**
   - Formal mathematical specification of the signed evaluator defect $\Delta_E \in \{-1, 0, 1\}$.
   - Structural mapping of the 6-volume foundational paper series to the Omega Engine crate implementation.
   - Demonstration that passing local tests does not guarantee global composite validity under incomplete projection boundaries.

2. **What this document does not support:**
   - It does not support a general claim that all software bugs are caused by sheaf obstructions.
   - It does not assert that finite-stage solvability ensures under the declared assumptions infinite-stage convergence without verifying Stacks Tag 07KV (Mittag-Leffler) conditions.

3. **Narrowest defensible claim:**
   - On any discrete system where the global evaluation predicate depends on joint state coordinates outside the span of local projections, there exist inputs where all local evaluators return $1$ while the global evaluator returns $0$, which the Omega Engine detects and refuses with typed status `REFUSED_LOCAL_GREEN_GLOBAL_RED`.

4. **Next test needed:**
   - Run targeted unit tests `test_tier5_adversarial_m4_m5.py` and verify that mutant arbiters correctly emit `REFUSED_LOCAL_GREEN_GLOBAL_RED` whenever $\Phi_1 > 0$.
