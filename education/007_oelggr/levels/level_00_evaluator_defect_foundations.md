---
documentation_contract: symbol-game-documentation/v1
title: "LGGR Level 00: Evaluator Defect Foundations"
kind: grammar-reference
level: 0
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
  row: LGGR-1
  relation: declared_research_successor
  lift_status: unlicensed
source_provenance: coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_i_evaluated_path_kernels
authority_effect: "None"
source_paths:
  - omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_i_evaluated_path_kernels/code/epk_core.py
  - omega_engine_operations/tests/release/test_release_models_and_lggr.py
---

# LGGR Level 00: Evaluator Defect Foundations

AuthorityEffect: None.

**Level:** Level 00 (Foundational Discrete Defect Carrier)  
**Carrier:** Signed Integer Defect $\Delta_E \in \{-1, 0, 1\}$  
**Runtime Pipeline:** `Evaluator::DefectCalculator` | Primary Error: `ERR_LOCAL_GREEN_GLOBAL_RED`  
**Atlas Capabilities:** `defect_computation`, `boolean_lattice_comparison`

---

## 1. Schematic & Conceptual Architecture

```
   [ Local Component 1 ] ---> E_1 in {0, 1}
                                    \
                                     [ Product ] ---> Prod E_i in {0, 1}
                                    /                         \
   [ Local Component 2 ] ---> E_2 in {0, 1}                    v
                                                          [ Difference ] ---> Delta_E in {-1, 0, 1}
                                                               ^
   [ End-to-End System ] -------------------> E_g in {0, 1} --/
```

Level 00 establishes the simplest discrete carrier capable of witnessing compositional evaluation divergence. Given two local evaluators $E_1, E_2 \in \{0, 1\}$ and a global evaluator $E_g \in \{0, 1\}$, the composite evaluation functional evaluates the signed defect:

$$\Delta_E = E_g - E_1 E_2$$

The state space of this carrier is strictly ternary: $\Delta_E \in \{-1, 0, 1\}$.

---

## 2. Mathematical Spine & Exact Invariants

### The Boolean Truth Table

Evaluating all $2^3 = 8$ possible configurations of $(E_1, E_2, E_g)$:

| $E_1$ | $E_2$ | $E_1 E_2$ | $E_g$ | $\Delta_E = E_g - E_1 E_2$ | Classification |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | 0 | 0 | 0 | $0$ | Concordant Red |
| 0 | 0 | 0 | 1 | $+1$ | Local Red, Global Green |
| 0 | 1 | 0 | 0 | $0$ | Concordant Red |
| 0 | 1 | 0 | 1 | $+1$ | Local Red, Global Green |
| 1 | 0 | 0 | 0 | $0$ | Concordant Red |
| 1 | 0 | 0 | 1 | $+1$ | Local Red, Global Green |
| 1 | 1 | 1 | 1 | $0$ | Concordant Green |
| **1** | **1** | **1** | **0** | **-1** | **Local Green, Global Red (Blind Spot)** |

### Structural Invariant
The failure mode $\Delta_E = -1$ occurs if and only if:
$$\prod_{i=1}^k E_i = 1 \quad \land \quad E_g = 0$$

Under this condition, every local monitor asserts success, while the composite system fails.

---

## 3. Omega Engine Crate Implementation & Code References

In the Omega Engine release and defect models:
- [`omega_engine_operations/tests/release/test_release_models_and_lggr.py`](../../../../omega_engine_operations/tests/release/test_release_models_and_lggr.py#L69-L97):
  ```python
  def compute_evaluator_defect(e1: int, e2: int, eg: int) -> dict:
      prod_local = e1 * e2
      delta = eg - prod_local
      has_lggr = (delta == -1)
      return {
          "delta": delta,
          "has_local_green_global_red": has_lggr,
          "classification": "LGGR_BLIND_SPOT" if has_lggr else "CONCORDANT"
      }
  ```

---

## 4. Target Checkers, Adversarial Falsifiers & Replay Verification

In `test_release_models_and_lggr.py`, the test suite parameterizes all eight rows of the truth table:
- Asserts that exactly one row produces `has_local_green_global_red == True` with $\Delta_E = -1$.
- Asserts that three rows produce $+1$ and four rows produce $0$.
- Verifies that no float conversion or rounding is permitted during defect computation.

---

## 5. Scope & Claim Boundary

| CAN Show in this Level | CANNOT Show in this Level |
| :--- | :--- |
| Exact ternary defect arithmetic over integers: $\Delta_E \in \{-1, 0, 1\}$. | Root causes of why $E_g$ failed when $E_1, E_2$ passed (requires Levels 01–06). |
| Deterministic classification of the $(1, 1, 0)$ state as the unique LGGR witness. | general claim about real-world software without evaluating concrete state projections. |
