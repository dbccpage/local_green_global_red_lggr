# Constraint-Level Regulation via Multi-Channel Obstruction Diagnostics

**Monograph Series:** Monograph 018 (Finite Obstruction Calculus Program)  
**Author:** Jeremy H. Carroll  
**Date:** 2026-10-08  
**Version:** 2.0.2  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)  

---

## Abstract

This paper defines a repair-selection controller for discrete constraint-system evolution. The system monitors five obstruction channels—geometric quotient residual ($\Phi_{\mathrm{geom}}$), logical inconsistency ($\Phi_{\mathrm{sat}}$), structural closure defect ($\Phi_{\mathrm{curv}}$), representative distortion ($\Xi$), and relational interface drift ($\Phi_{\mathrm{rel}}$)—to evaluate and rank candidate repair operator proposals under explicit guardrails, including the piecewise closure ratio ($R_{cl}$) and guarded descent bounds. Candidate selection is separated from state transition verification, ensuring that exploratory operator proposals are screened prior to state commitment. Tested unit fixtures demonstrate the distinct activation of these diagnostic channels and show that the controller correctly filters and ranks candidate proposals under declared rules. Key Technical Definitions Included: The Multi-Channel State Vector; Differential Bound and Realized Channel Separability ($\Gamma_2 \le \|d_1\|_{1 \to 1} \Phi_1$); Piecewise Closure Ratio ($R_{cl}$) as an exact boundary stability filter; Global $\varepsilon$-Optimal Candidate Ranking with $\Xi$ Tie-Breaking; and the Cost-Sensitive Lift Law ($\Delta_\Lambda$).

---

## 1. Introduction and Architectural Motivation

Complex constraint-satisfaction and discrete optimization settings frequently exhibit multidimensional failure modes that cannot be captured by a single scalar error metric. A candidate state transition may lower a numeric residual while violating discrete logical invariants, or resolve local edge discrepancies by worsening boundary curvature.

This paper establishes the architecture of a **repair-selection controller** that evaluates candidate constraint system transitions. Rather than collapsing distinct diagnostics into an unweighted scalar loss that allows trade-offs against boundary constraints, the controller evaluates five diagnostic channels and screens candidate repair operators under declared topological guardrails.

```
       +--------------------------------------------------------------+
       |                  Multi-Channel State Vector                  |
       |  (Phi_geom,  Phi_sat,  Phi_curv,  Phi_rel,  Xi)              |
       +--------------------------------------------------------------+
                                      |
                                      v
       +--------------------------------------------------------------+
       |               Topological Guardrail Evaluation               |
       |     - Guarded Descent: Phi_geom(S') <= Phi_geom(S) + eps     |
       |     - Boundary Stability: R_cl(S') <= R_max                  |
       +--------------------------------------------------------------+
                         /                          \
             Pass Guardrails                      Fail Guardrails
                       /                              \
                      v                                v
       +-------------------------------+    +-------------------------+
       |  Candidate Ranking by         |    |  Refusal / Rollback     |
       |  Discrete Score & Strict Xi   |    |  (Halt with Diagnostics)|
       +-------------------------------+    +-------------------------+
```

### Separation of Candidate Selection and State Transition Verification

The controller functions as a candidate screening and ranking filter:
$$\boxed{\text{Candidate selection by the controller does not certify state transition validity or constraint preservation.}}$$
Selection of an operator proposal indicates only that its supplied diagnostic values satisfy declared admission criteria; committing the resulting state requires verification by separate, deterministic verification checks.

---

## 2. The Five-Channel Diagnostic State Vector

At any discrete time step $t$, the system state $S_t$ produces a five-dimensional diagnostic signature:
$$\vec{\Phi}(S_t) = \left( \Phi_{\mathrm{geom}}(S_t), \; \Phi_{\mathrm{sat}}(S_t), \; \Phi_{\mathrm{curv}}(S_t), \; \Phi_{\mathrm{rel}}(S_t), \; \Xi(S_t) \right) \in \mathbb{R}_{\ge 0}^5.$$

1. **Geometric Quotient Residual ($\Phi_{\mathrm{geom}} = \Phi_1$):**
   $$\Phi_1([\omega_1]) = \min_{\alpha \in C^0} \|\omega_1 - d_0 \alpha\|_1.$$
   Measures the irreducible coboundary defect in the 1-cochain space.
2. **Logical Inconsistency ($\Phi_{\mathrm{sat}}$):**
   $$\Phi_{\mathrm{sat}} = \sum_{c \in \mathcal{C}} \mathbf{1}_{\{\text{clause } c \text{ violated}\}}.$$
   Counts violated discrete propositional clauses in declared SAT constraints.
3. **Closure Defect / Curvature ($\Phi_{\mathrm{curv}} = \Gamma_2$):**
   $$\Gamma_2(\omega_1) = \|d_1 \omega_1\|_1.$$
   Measures non-closure of the defect field at the 2-boundary.
4. **Relational Interface Drift ($\Phi_{\mathrm{rel}}$):**
   For sub-carriers with boundary interface operators $\rho_{ij}$:
   $$\Phi_{\mathrm{rel}}(S) = \sum_{(i,j)} \|\rho_{ij}(\omega_i) - \rho_{ji}(\omega_j)\|_1.$$
   Measures boundary discrepancy across sub-system interfaces.
5. **Representative Distortion ($\Xi$):**
   Normalized trace distance between primal residual and dual witness density lifts.
   *Zero-Obstruction Convention:* When $\Phi_1 = 0$ (exact cochain), $\Xi = 0$ by definition.

### Proposition 2.1 (Differential Bound and Channel Separability)

Let $C^0 \xrightarrow{d_0} C^1 \xrightarrow{d_1} C^2$ be a finite cochain complex ($d_1 d_0 = 0$). For every cochain $\omega_1 \in C^1$ and potential $\alpha \in C^0$:
$$d_1 \omega_1 = d_1(\omega_1 - d_0 \alpha).$$
Consequently, taking the $\ell^1$ operator norm $\|d_1\|_{1 \to 1} = \sup_{v \ne 0} \|d_1 v\|_1 / \|v\|_1$:
$$\|d_1 \omega_1\|_1 \le \|d_1\|_{1 \to 1} \|\omega_1 - d_0 \alpha\|_1.$$
Minimizing over $\alpha \in C^0$ yields:
$$\boxed{\Gamma_2(\omega_1) \le \|d_1\|_{1 \to 1} \Phi_1([\omega_1]).}$$
In particular, $\Phi_1([\omega_1]) = 0 \implies \Gamma_2(\omega_1) = 0$. The channels are therefore not completely algebraically independent.

However, the channels exhibit distinct activation patterns across finite constraint configurations:
- **Exact cochain with logical violation:** $\Phi_1 = 0$ and $\Gamma_2 = 0$, while $\Phi_{\mathrm{sat}} > 0$.
- **Closed non-exact cochain:** On a complex with non-trivial 1-cohomology (such as an uncontractible cycle), a closed cochain satisfies $\Gamma_2 = 0$ while $\Phi_1 > 0$.
- **Unclosed cochain on a filled cell:** On a single filled triangle with cyclic orientation, $\Phi_1([\omega]) = \Gamma_2(\omega) = |\omega_1 + \omega_2 + \omega_3|$.

Deposit status. The mechanized statement is the rational signature fence: $\Phi_{\mathrm{geom}} = 0$ with positive curvature or positive $\Xi$ is rejected, and $(0, 3, 0, 0, 0)$ is accepted. The operator-norm bound remains the classical reading.

---

## 3. Boundary Stability: The Piecewise Closure Ratio $R_{cl}$

In candidate repair evaluation, an operator proposal might attempt to reduce the 1-defect $\Phi_1$ while inflating boundary curvature $\Gamma_2$.

### Definition 3.1 (Piecewise Closure Ratio)
The closure ratio $R_{cl}(S)$ is defined piecewise by:
$$R_{cl}(S) = \begin{cases} 0 & \text{if } \Phi_1(S) = 0 \text{ and } \Gamma_2(S) = 0, \\[6pt] \frac{\Gamma_2(S)}{\Phi_1(S)} & \text{if } \Phi_1(S) > 0, \\[6pt] +\infty & \text{if } \Phi_1(S) = 0 \text{ and } \Gamma_2(S) > 0. \end{cases}$$

On any valid finite cochain complex with $d_1 d_0 = 0$, Proposition 2.1 establishes $\Gamma_2 \le \|d_1\|_{1 \to 1} \Phi_1$, ensuring that exact cochains ($\Phi_1 = 0$) force $\Gamma_2 = 0$. Signatures with $\Phi_1 = 0$ and $\Gamma_2 > 0$ (or $\Xi > 0$, violating the declared zero-obstruction convention) cannot arise from any cochain in the declared complex and are rejected fail-closed during state validation.

### Invariant 3.1 (The Exact $R_{cl}$ Guardrail)
No candidate proposal $o$ is admitted if its resulting closure ratio exceeds the declared threshold:
$$R_{cl}(o(S_t)) \le R_{\max},$$
where $R_{\max} \in (0, \infty)$ is an exact hard boundary with no tolerance relaxation.

### Scope Fence: Constraint Deletion
The ratio $R_{cl}$ is a scalar filter evaluated on candidate states within a fixed or declared constraint complex. It does not detect or prevent constraint or edge deletion where both $\Phi_1$ and $\Gamma_2$ collapse to zero. For example, deleting an edge and incident face from a filled triangle leaves a 2-edge path with $\Phi_1' = 0$ and $\Gamma_2' = 0$, yielding $R_{cl}' = 0 \le R_{\max}$. The ratio accepts this outcome. Constraint preservation and carrier support invariants must therefore be verified by a separate verification check.

Deposit status. For a positive ceiling, the exact guard rejects a zero geometric coordinate with positive curvature, accepts the collapsed pair $(0,0)$, and for positive geometry accepts exactly the cross-multiplied inequality $\Phi_{\mathrm{curv}} \le R_{\max}\Phi_{\mathrm{geom}}$. Acceptance of the collapsed pair is the proved form of the deletion fence.

---

## 4. Repair Selection Controller Architecture

Let $\mathfrak{O}$ be a declared catalog of candidate repair operators:
$$\mathfrak{O} = \{ \Pi_{21} \text{ (numeric projection)}, \; \Pi_{12} \text{ (structural lift)}, \; \text{SAT repair}, \; \text{rollback}, \; \text{wait} \}.$$

### Definition 4.1 (Candidate Scoring and Global $\varepsilon$-Optimal Ranking)
The controller evaluates admissible operator proposals that satisfy:
1. **Guarded Descent:** $\Phi_{\mathrm{geom}}(o(S_t)) \le \Phi_{\mathrm{geom}}(S_t)$ (literal non-increase relative to current state, composing with Paper 009).
2. **Boundary Stability:** $R_{cl}(o(S_t)) \le R_{\max}$ (exact hard boundary).

Admissible candidates are scored by the discrete objective:
$$F_{\mathrm{discrete}}(o(S_t)) = \Phi_{\mathrm{geom}}' + \lambda_{\mathrm{sat}} \Phi_{\mathrm{sat}}' + \lambda_{\mathrm{curv}} \Gamma_2' + \lambda_{\mathrm{rel}} \Phi_{\mathrm{rel}}' + \operatorname{Cost}(o),$$
with declared default weights $(\lambda_{\mathrm{sat}} = 0.5, \lambda_{\mathrm{curv}} = 0.2, \lambda_{\mathrm{rel}} = 0.1)$. Proposals whose discrete score overflows to non-finite values are rejected fail-closed.

**Global Ranking Policy:** To eliminate pairwise cyclic preferences and proposal-order dependencies, selection follows a global set-based policy:
1. Identify the minimal discrete score: $F_{\min} = \min_{o \in \text{Admissible}} F_{\mathrm{discrete}}(o)$.
2. Form the $\varepsilon$-optimal candidate set:
   $$\mathcal{C}_\varepsilon = \{ o \in \text{Admissible} : F_{\mathrm{discrete}}(o) \le F_{\min} + \varepsilon \}.$$
3. Identify the minimal trace distance within $\mathcal{C}_\varepsilon$: $\Xi_{\min} = \min_{o \in \mathcal{C}_\varepsilon} \Xi(o)$.
4. Form the tie-break set:
   $$\mathcal{T}_\varepsilon = \{ o \in \mathcal{C}_\varepsilon : \Xi(o) \le \Xi_{\min} + \varepsilon \}.$$
5. Apply deterministic final tie-breaking on $\mathcal{T}_\varepsilon$: prefer strictly smaller $F_{\mathrm{discrete}}$, then strictly smaller $\Xi$, then declared catalog order (operator name).

**Score Priority Fencing:** Within the declared numerical tolerance $\varepsilon$, discrete scores satisfying $F_{\mathrm{discrete}}(o) \le F_{\min} + \varepsilon$ are treated as numerically tied (indistinguishable within measurement resolution). Within this $\varepsilon$-optimal set, $\Xi$ minimizes the trace distance to break the tie, which may select a candidate whose discrete score is up to $\varepsilon$ higher than $F_{\min}$. Outside this $\varepsilon$-band ($F_{\mathrm{discrete}}(o) > F_{\min} + \varepsilon$), no reduction in $\Xi$ can override a worse discrete score. Furthermore, guarded descent enforces strict literal non-increase relative to the current state ($\Phi_{\mathrm{geom}}(o(S_t)) \le \Phi_{\mathrm{geom}}(S_t)$), supporting compatibility with the literal non-increase invariant of Paper 009.

Deposit status. Lean verifies that a geometric increase is rejected, that a ratio failure is still rejected after descent passes, that a score outside the $\varepsilon$ band loses to the minimum, that the lower $\Xi$ wins inside a score tie, and that equal score and $\Xi$ follow the earlier name. No convergence theorem is mechanized.

### Definition 4.2 (Cost-Sensitive Lift Law $\Delta_\Lambda$)
A representation-expanding lift $\Pi_{12}$ (which increases model dimension or introduces new auxiliary vertices) is admitted only if its structural reduction exceeds its dimensional parameter penalty:
$$\Delta_\Lambda(\Pi_{12}) = \Delta\Phi_{\mathrm{geom}} + \lambda_{\mathrm{sat}} \Delta\Phi_{\mathrm{sat}} - \operatorname{Cost}_{\mathrm{dim}}(\Pi_{12}) > 0,$$
where $\Delta\Phi_{\mathrm{geom}} = \Phi_{\mathrm{geom}}(S_t) - \Phi_{\mathrm{geom}}(S')$, $\Delta\Phi_{\mathrm{sat}} = \Phi_{\mathrm{sat}}(S_t) - \Phi_{\mathrm{sat}}(S')$, and $\operatorname{Cost}_{\mathrm{dim}}$ is distinct from the operator execution cost $\operatorname{Cost}(o)$.

Deposit status. The proved comparison is $\operatorname{Cost}_{\mathrm{dim}} < \Delta\Phi_{\mathrm{geom}} + \tfrac{1}{2}\Delta\Phi_{\mathrm{sat}}$.

### Definition 4.3 (Typed Refusal Taxonomy and Audit Diagnostics)
When no candidate proposal can be admitted, the controller emits an explicit typed refusal:
- `RefusedTearing`: Candidates violated boundary stability ($R_{cl} > R_{\max}$).
- `RefusedDescentViolation`: Candidates increased geometric residual ($\Phi_{\mathrm{geom}}(S') > \Phi_{\mathrm{geom}}(S_t)$).
- `RefusedInvalidInput`: Proposals contained non-finite, negative, or contradictory diagnostic signatures.
- `RefusedStalled`: Proposals were empty or contained mixed unviable violations.
Each proposal's specific failure reason is recorded in `diagnostics["rejections"]` and aggregated in `diagnostics["rejection_counts"]`.

Deposit status. The empty tag list is a stall. A nonempty uniform list of invalid, tearing, or descent tags returns that tag. A mixed tearing and descent list stalls.

---

## 5. Scope Fences and Nonclaims

1. **No Cognition or Agency:** The controller is an explicit numerical and discrete routing algorithm. It possesses no self-awareness, cognitive capabilities, or subjective evaluation.
2. **No Terminal Transition Verification:** An operator chosen by the controller is an exploratory candidate transition. It becomes committed only upon passing hard, sovereign verifier gates.
3. **No General Convergence Theorem:** The controller implements a greedy single-step filtering policy. Non-worsening under tolerance $\varepsilon$ does not establish asymptotic convergence, termination, or cycle avoidance on general non-convex discrete constraint systems.
4. **No Unassisted Constraint Preservation:** $R_{cl}$ bounds the ratio of curvature to quotient residual on a given complex; it does not certify that constraints or edges have not been deleted.

---

## 6. Conclusion

Multi-channel obstruction regulation provides a structured candidate screening policy for discrete constraint systems. By decomposing errors into geometric, logical, curvature, relational, and distortion channels, the repair-selection controller filters and ranks operator proposals while enforcing fail-closed boundary stability and strict tie-breaking guardrails.

