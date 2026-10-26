---
documentation_contract: symbol-game-documentation/v1
title: "LGGR Level 07: Omega Engine Crate Architecture"
kind: grammar-reference
level: 7
status: active
maturity: production
atlas_status: specified
evidence_grades:
  named: true
  syntax: true
  computed: true
  Lean: true
  gated: true
successor:
  row: LGGR-8
  relation: declared_research_successor
  lift_status: unlicensed
source_provenance: omega_engine/crates/omega_local_green_global_red_lggr
authority_effect: "None"
source_paths:
  - omega_engine_education/documentation/16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md
  - omega_engine_pfp/domain/ast_cochain/models.py
---

# LGGR Level 07: Omega Engine Crate Architecture

AuthorityEffect: None.

**Level:** Level 07 (Production Crate & Clean Architecture Integration)  
**Carrier:** Software Package `omega_engine.crates.omega_local_green_global_red_lggr`  
**Runtime Pipeline:** `Evaluator::CrateKernelPipeline` | Primary Error: `ERR_CRATE_BOUNDARY_LEAK`  
**Atlas Capabilities:** `crate_architecture`, `clean_architecture_inward_purity`, `ast_cochain_binding`

---

## 1. Schematic & Conceptual Architecture

```
   +-------------------------------------------------------------------------------+
   |                             OUTER CONSUMERS                                   |
   |   - omega_engine_pfp (AST Cochain Arbiter)                            |
   |   - omega_engine_operations (Release Gate Receipt CLI)                        |
   |   - omega_research (Empirical Verification Swarms)                            |
   +---------------------------------------+---------------------------------------+
                                           | calls / imports
                                           v
   +-------------------------------------------------------------------------------+
   |       CRATE: omega_local_green_global_red_lggr                    |
   |                                                                               |
   |   [ Public Interface ]:  core.py, epk.py, composition.py, defects.py         |
   |   [ Role Overlay ]:      epk_overlay.py, lggr_overlay.py                      |
   |   [ Measurement ]:       bound_measurement.py, metrics.py                     |
   |   [ Audit Ledger ]:      ledger.py, evaluation_harness.py                     |
   +---------------------------------------+---------------------------------------+
                                           | strict inward dependencies only
                                           v
   +-------------------------------------------------------------------------------+
   |                           FOUNDATIONAL CRATES                                 |
   |   - contract_core (Immutable protocols)                                       |
   |   - category_theory (Functors & monoids)                                      |
   |   - sheaf_theory (Restriction maps)                                           |
   |   - type (Exact rational arithmetic)                                          |
   +-------------------------------------------------------------------------------+
```

Level 07 specifies the physical software implementation of the Local Green, Global Red theory as built within the Omega Engine sovereign crate architecture.

---

## 2. Directory & Module Inventory

As documented in [`omega_engine_education/documentation/16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md`](../../16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md#L1868), the crate contains 44 files organized into clear functional boundaries:

1. **Core Kernel Models:**
   - `core.py`: Abstract protocols, dataclasses, and immutable value objects.
   - `base/epk_base.py`: Low-level base classes for evaluated path structures.
   - `epk.py`: Canonical implementation of path-ordered evaluation kernels.
   - `evaluated_path.py`: Concrete path sequences and state trajectory loggers.

2. **Defect & Composition Calculus:**
   - `defects.py`: Exact rational computation of $\Delta_E = E_g - \prod E_i$.
   - `composition.py`: Associative path concatenation and kernel tensor products.
   - `bound_measurement.py`: Exact rational interval bounds for observation maps.
   - `metrics.py`: Duality gaps, coboundary norms, and spectral leakage metrics.

3. **Overlays & Harnesses:**
   - `epk_overlay.py`: Six-role GTLA protocol interfaces (Planner, Proposer, Governor, Worker, Arbiter, Auditor).
   - `lggr_overlay.py`: Clean Architecture interceptor preventing silent promotion of local-green proposals.
   - `evaluation_harness.py`: Multi-agent test runner detecting local-green/global-red discrepancies.
   - `ledger.py`: Append-only, SHA-256 hash-chained evaluation receipts.

---

## 3. Clean Architecture Inward Dependency Invariant

The crate strictly adheres to the repository's Clean Architecture Inward Dependency Directive:
- **Zero Outward Leaks:** The crate does NOT depend on operations, controllers, frontend CLIs, or third-party web frameworks.
- **Foundational Ports:** It imports exclusively from internal core crates:
  - `omega_engine.crates.contract_core`
  - `omega_engine.crates.category_theory`
  - `omega_engine.crates.sheaf_theory`
  - `omega_engine.crates.type`
- **Zero-Float Law:** All internal calculations use `fractions.Fraction` or exact integers. Floating-point arithmetic is strictly banned.

---

## 4. Integration into the Symbol Game

In [`omega_engine_pfp/domain/ast_cochain/models.py`](../../../../omega_engine_pfp/domain/ast_cochain/models.py#L20), the crate's defect calculus is wired directly into the AST cochain referee:

```python
class LggrVerdict(str, Enum):
    PASS = "PASS"
    REFUSED_LOCAL_GREEN_GLOBAL_RED = "REFUSED_LOCAL_GREEN_GLOBAL_RED"
    LOCAL_RED = "LOCAL_RED"
```

When an AST proposal exhibits non-zero boundary leakage ($\Phi_1 > 0$) or cycle obstruction ($\Gamma_2 > 0$) despite passing local module syntax checks, the arbiter returns:
$$\text{verdict} = \boxed{\text{LggrVerdict.REFUSED\_LOCAL\_GREEN\_GLOBAL\_RED}}$$

---

## 5. Scope & Claim Boundary

| CAN Show in this Level | CANNOT Show in this Level |
| :--- | :--- |
| Exact module layout and dependency graph of the production `omega_local_green_global_red_lggr` crate. | general software reliability across arbitrary untrusted third-party code without crate execution. |
| Deterministic fail-closed rejection of $\Phi_1 > 0$ AST cochains under `LggrVerdict`. | Claim of formal Lean 4 kernel compilation outside the verified Lake toolchain. |
