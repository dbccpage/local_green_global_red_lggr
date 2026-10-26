---
documentation_contract: symbol-game-documentation/v1
title: "LGGR Level 01: Evaluated Path Kernels (EPK)"
kind: grammar-reference
level: 1
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
  row: LGGR-2
  relation: declared_research_successor
  lift_status: unlicensed
source_provenance: coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_i_evaluated_path_kernels
authority_effect: "None"
source_paths:
  - omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_i_evaluated_path_kernels/code/epk_core.py
  - omega_engine_education/documentation/16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md
---

# LGGR Level 01: Evaluated Path Kernels (EPK)

AuthorityEffect: None.

**Level:** Level 01 (Path Trajectory & Kernel Composition)  
**Carrier:** Evaluated Path Kernel Tuple $\mathcal{K} = (S, T, E, \mu)$  
**Runtime Pipeline:** `Evaluator::PathKernelComposer` | Primary Error: `ERR_COMPOSITION_MISMATCH`  
**Atlas Capabilities:** `path_kernel_composition`, `trace_evaluation`

---

## 1. Schematic & Conceptual Architecture

```
   State s_0 ---[ a_1 ]---> State s_1 ---[ a_2 ]---> State s_2
      |                        |                        |
   Kernel K_1: (s_0 -> s_1)    |                        |
   Verdict E_1 in {0, 1}       |                        |
                               Kernel K_2: (s_1 -> s_2) |
                               Verdict E_2 in {0, 1}    |
   ======================================================
   Composite Kernel K_2 o K_1: (s_0 -> s_2)
   Global Verdict E_g in {0, 1}
   Defect: Delta_E = E_g - E_1 E_2
```

In Level 01, we advance from static scalar checks to **dynamic execution paths**. An Evaluated Path Kernel (EPK) formalizes the evaluation of an agent or process executing a sequence of actions over a state transition graph.

---

## 2. Mathematical Spine & Exact Invariants

### Evaluated Path Kernel Definition
An Evaluated Path Kernel on a directed graph $G = (V, E_G)$ is a structure:
$$\mathcal{K} = (X, \mathcal{P}, E)$$
where:
- $X$ is a finite discrete state space.
- $\mathcal{P} \subseteq X \times X$ is the set of admissible execution paths.
- $E: \mathcal{P} \to \{0, 1\}$ is a deterministic path evaluator.

### Non-Commutative Path Composition
Let $\gamma_1 = (s_0 \to s_1)$ and $\gamma_2 = (s_1 \to s_2)$ be composable paths. The concatenated path is:
$$\gamma = \gamma_2 \circ \gamma_1 = (s_0 \to s_1 \to s_2)$$

Because path concatenation is sensitive to traversal sequence, evaluation is non-commutative:
$$E(\gamma_2 \circ \gamma_1) \ne E(\gamma_1 \circ \gamma_2)$$

### Conditional Kernel Composition Theorem
Let $K_1$ and $K_2$ be two EPKs with evaluators $E_1, E_2$. Global evaluation $E_g$ factorizes into $E_1 E_2$ ($E_g = E_1 E_2$) if and only if the global acceptance predicate does not depend on correlations across the intermediate boundary state $s_1$. If the global specification enforces an end-to-end invariant $I(s_0, s_2)$ that is not a conjunction of local invariants $I_1(s_0, s_1) \land I_2(s_1, s_2)$, then $\Delta_E = -1$ is realizable.

---

## 3. Omega Engine Crate Implementation & Code References

In [`omega_engine/crates_rs/omega_local_green_global_red_lggr/`](../../16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md#L1868):
- `epk_core.py`: Defines `EvaluatedPath` and `KernelComposition`.
- `composition.py`: Computes path products and tracks path-ordered history.
- `defects.py`: Implements exact rational defect checks on path steps.

```python
class EvaluatedPath:
    def __init__(self, steps: list[tuple[int, int]], evaluator: callable):
        self.steps = steps
        self.evaluator = evaluator

    def evaluate(self) -> int:
        return self.evaluator(self.steps)

def compose_kernels(k1: EvaluatedPath, k2: EvaluatedPath, global_eval: callable) -> dict:
    e1 = k1.evaluate()
    e2 = k2.evaluate()
    composite_steps = k1.steps + k2.steps
    eg = global_eval(composite_steps)
    delta = eg - (e1 * e2)
    return {"e1": e1, "e2": e2, "eg": eg, "delta_e": delta}
```

---

## 4. Target Checkers, Adversarial Falsifiers & Replay Verification

In `coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_i_evaluated_path_kernels/`:
- `code/tests/`: Executes unit and mutation tests asserting that path composition correctly flags $\Delta_E = -1$ when intermediate boundary invariants are decoupled.
- `lean4/`: Lake build elaborates formal theorems stating that $E_g = E_1 E_2$ requires conditional independence over boundary cuts.

---

## 5. Scope & Claim Boundary

| CAN Show in this Level | CANNOT Show in this Level |
| :--- | :--- |
| Exact discrete path composition and defect calculation over finite state graphs. | Distributed multi-agent sheaf overlap obstructions (addressed in Level 02). |
| Constructive demonstration that non-separable end-to-end predicates cause $\Delta_E = -1$. | Continuous diffusion or unbounded Markov chain dynamics. |
