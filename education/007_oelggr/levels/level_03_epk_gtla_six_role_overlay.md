---
documentation_contract: symbol-game-documentation/v1
title: "LGGR Level 03: EPK-GTLA Six-Role System Overlay"
kind: grammar-reference
level: 3
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
  row: LGGR-4
  relation: declared_research_successor
  lift_status: unlicensed
source_provenance: coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_iii_epk_gtla_overlay
authority_effect: "None"
source_paths:
  - omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_iii_epk_gtla_overlay/code/epk_gtla_overlay_core.py
  - omega_engine_education/documentation/16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md
---

# LGGR Level 03: EPK-GTLA Six-Role System Overlay

AuthorityEffect: None.

**Level:** Level 03 (Six-Role Game-Theoretic Overlay)  
**Carrier:** Six-Role Evaluation Profile $\mathbf{R} = (P, \Pi, G, W, A, \Omega)$  
**Runtime Pipeline:** `Evaluator::RoleOverlayAuditor` | Primary Error: `ERR_ROLE_COLLUSION`  
**Atlas Capabilities:** `game_theoretic_overlay`, `role_decoupling`, `audit_triangulation`

---

## 1. Schematic & Conceptual Architecture

```
   [ Planner ] --------> Decomposes Task Contract
        |
        v
   [ Proposer ] -------> Synthesizes Candidate Patch / Action
        |
        v
   [ Governor ] -------> Validates Pre-Execution Fences & Budget
        |
        v
   [ Worker ] ---------> Executes Step in Container Sandbox
        |
        v
   [ Arbiter ] --------> Emits Local Verdict E_local in {0, 1}
        |
   ===========================================================
   [ Auditor ] --------> Independent Replay -> Global Verdict E_g in {0, 1}
                         Computes: Delta_E = E_g - E_local
```

Level 03 introduces the **Game-Theoretic Learning Architecture (GTLA)** overlay. When multiple AI subagents collaborate, relying on the implementing agent or a friendly local reviewer to grade the work leads to systemic self-grading inflation. Level 03 decouples evaluation into six distinct, non-overlapping roles.

---

## 2. Mathematical Spine & Exact Invariants

### The Six-Role Separation Invariant
The six system roles are strictly orthogonal:
1. **Planner ($P$):** Decomposes parent goals into typed sub-contracts. Must NOT evaluate code.
2. **Proposer ($\Pi$):** Synthesizes creative solutions. Must NOT have merge or sign-off authority.
3. **Governor ($G$):** Enforces static type and boundary fences. Must NOT generate content.
4. **Worker ($W$):** Executes isolated tasks. Must NOT self-evaluate.
5. **Arbiter ($A$):** Computes local acceptance verdicts ($e_1, e_2$). Must be separate from Worker.
6. **Auditor ($\Omega$):** Read-only independent examiner that recomputes ground truth from first principles to issue $e_g$.

### The Anti-Collusion Payoff Functional
Let $u_W$ and $u_A$ be the payoff utilities of Worker and Arbiter. If Arbiter colludes with Worker to award an unearned green ($e_{\text{local}} = 1$), but Auditor detects a global defect ($e_g = 0$):
$$\Delta_E = 0 - 1 = -1$$
The payoff assigns a severe penalty:
$$u_A(\Delta_E = -1) = -\infty \quad (\text{Immediate Demotion / License Revocation})$$
This penalty strictly enforces truth-telling as a dominant game-theoretic equilibrium.

---

## 3. Omega Engine Crate Implementation & Code References

In [`omega_engine/crates_rs/omega_local_green_global_red_lggr/`](../../16_the_omega_engine/omega_engine_operations/_design_docs/omega_engine_components.md#L1868):
- `epk_overlay.py`: Formalizes the six-role dispatch interfaces.
- `evaluation_harness.py`: Orchestrates multi-agent execution rounds and recomputes $\Delta_E$.

```python
class SystemRole(Enum):
    PLANNER = "planner"
    PROPOSER = "proposer"
    GOVERNOR = "governor"
    WORKER = "worker"
    ARBITER = "arbiter"
    AUDITOR = "auditor"

def evaluate_gtla_round(worker_output, arbiter_verdict: int, auditor_evaluator: callable) -> dict:
    eg = auditor_evaluator(worker_output)
    delta = eg - arbiter_verdict
    return {
        "arbiter_verdict": arbiter_verdict,
        "auditor_verdict": eg,
        "delta": delta,
        "collusion_detected": (delta == -1)
    }
```

---

## 4. Target Checkers, Adversarial Falsifiers & Replay Verification

In `coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_iii_epk_gtla_overlay/`:
- `code/tests/`: Tests mutation scenarios where Worker and Arbiter attempt to whitewash boundary violations.
- `lean4/`: shows in this model that under the GTLA penalty contract, any strategy profile where Arbiter rubber-stamps invalid worker outputs is strictly dominated.

---

## 5. Scope & Claim Boundary

| CAN Show in this Level | CANNOT Show in this Level |
| :--- | :--- |
| Formal game-theoretic role separation preventing local self-certification in finite multi-agent networks. | Guarantee that real-world LLMs adhere to incentives without host-enforced boundary execution. |
| Elimination of unearned local-green via independent Auditor triangulation. | Convergence under unconstrained adversary collusion without sandboxing. |
