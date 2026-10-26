# Observer-Robust Control of Obstruction Diagnostics

**Monograph Series:** Monograph 019 (Finite Obstruction Calculus Program)  
**Author:** Jeremy H. Carroll  
**Date:** 2026-10-08  
**Version:** 2.1.1  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)  
**Status:** RELEASED  
**DOI:** 10.5281/zenodo.20214468  
**Authority Notice:** *This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing.*

---

## Abstract

This paper establishes a formal architecture for the observer-robust control of discrete constraint systems. Shifting from a single-metric view of system error, the work defines a repair-policy layer that operates over a bundle of observer-induced geometries. A control policy ($\operatorname{Ctrl}$) is defined as 'observer-robust' if its performance—measured by descent adherence, structural stability, and diagnostic responsiveness—remains bounded across a declared class of admissible observers ($\mathfrak{O}$). The core contribution is the operationalization of the Observer-Robust Control Criterion, which evaluates policies based on their ability to stabilize obstruction diagnostics ($\Phi_1$, $\Gamma_2$, $R_{cl}$, $\Xi$) without assuming a universally privileged metric. This framework incorporates a committed-state descent law, an absolute curvature stability fence, and a piecewise closure-ratio guardrail to prevent unmonitored residual surges and enforce bounded coordinate diagnostics under joint detector adequacy. This is a technical contribution to the theory of finite control and discrete geometry; it is not a theory of intelligence, cognition, learning, or consciousness. Verification suite and test fixtures demonstrate in finite discrete test systems that diagnostic channels can activate separately, supporting the requirement for multi-channel, diagnostic-responsive repair routing. Key Technical Contributions: Observer-Robust Control Criterion: A formal property for evaluating policy admissibility across varying observer assumptions. Hierarchical Control Model: From primitive observer selection to induced obstruction geometry and state-dependent repair routing. Committed-State Descent Law: Bounded quotient residuals ($\Phi_1$) under per-observer tolerances while allowing exploratory operator proposals. Diagnostic-Separation Evidence: Test validation that geometric, logical, and relational channels provide separable signals for structural repair.

---

## 1. Introduction: From Privileged Geometries to Observer Bundles

Traditional control theory and automated optimization assume a privileged coordinate system or a globally canonical metric. In complex distributed systems, heterogeneous verification pipelines, or multi-agent environments, such assumptions fail: different observation agents, measurement projections, or evaluation regimes measure structural errors differently.

A repair policy optimized exclusively for one specific observer is often fragile under another, creating hidden topological tearing or unmonitored residual buildup.

This paper formulates **Observer-Robust Control**:
- Rather than optimizing against a single observer $\mathcal{O}$, the controller operates over a declared **observer bundle** $\mathfrak{O}$.
- A transition is admissible if and only if it maintains bounded residuals and structural stability across **all** observers $\mathcal{O} \in \mathfrak{O}$.

```
                      +---------------------------------------+
                      |      Declared Observer Bundle O       |
                      |     { O_1,   O_2,   ...,   O_k }      |
                      +---------------------------------------+
                                          |
                      +-------------------+-------------------+
                      |                   |                   |
                      v                   v                   v
              +---------------+   +---------------+   +---------------+
              | Diagnostics   |   | Diagnostics   |   | Diagnostics   |
              | under O_1     |   | under O_2     |   | under O_k     |
              +---------------+   +---------------+   +---------------+
                      \                   |                   /
                       \                  |                  /
                        v                 v                 v
       +--------------------------------------------------------------+
       |             Observer-Robust Control Criterion                |
       |  - Committed Descent: Phi_1(S_{t+1}) <= Phi_1(S_t) + eps_O   |
       |  - Stability Guardrail: R_cl(S_{t+1}) <= R_max (for all O)   |
       |  - Absolute Curvature: Gamma_2(S_{t+1}) <= Gamma_2 + delta_G |
       |  - Worst-Case Residual Boundedness: sup_O Phi_1^O <= M_max   |
       +--------------------------------------------------------------+
```

---

## 2. Observer Models and Induced Geometries

Let $S$ be a discrete constraint state over a carrier complex $P = (V, E, F)$.

### Definition 2.1 (Observer Model)
An observer $\mathcal{O} \in \mathfrak{O}$ is a tuple $\mathcal{O} = (\pi_{\mathcal{O}}, \, d_0^{\mathcal{O}}, \, d_1^{\mathcal{O}}, \, \mathcal{W}_{1, \mathcal{O}}, \, \mathcal{W}_{2, \mathcal{O}}, \, \varepsilon_{\mathcal{O}})$ where:
1. $\pi_{\mathcal{O}}: C^1(P) \to C^1(P_{\mathcal{O}})$ is a linear projection or coordinate restriction map onto an observed 1-cochain subcomplex.
2. $d_0^{\mathcal{O}}: C^0(P_{\mathcal{O}}) \to C^1(P_{\mathcal{O}})$ and $d_1^{\mathcal{O}}: C^1(P_{\mathcal{O}}) \to C^2(P_{\mathcal{O}})$ are discrete coboundary operators on the observed complex.
3. $\mathcal{W}_{1, \mathcal{O}} = \{w_e\}_{e \in E_{\mathcal{O}}}$ with strictly positive, finite edge weights $w_e > 0$ defines the observed 1-cochain weighted $\ell^1$ norm:
   $$\|v\|_{1, \mathcal{W}_{1, \mathcal{O}}} = \sum_{e \in E_{\mathcal{O}}} w_e |v_e|.$$
4. $\mathcal{W}_{2, \mathcal{O}} = \{w_f\}_{f \in F_{\mathcal{O}}}$ with strictly positive, finite face weights $w_f > 0$ defines the observed 2-cochain weighted $\ell^1$ norm:
   $$\|u\|_{1, \mathcal{W}_{2, \mathcal{O}}} = \sum_{f \in F_{\mathcal{O}}} w_f |u_f|.$$
5. $\varepsilon_{\mathcal{O}} \ge 0$ is the finite observer resolution limit.

Each observer $\mathcal{O}$ induces its own quotient obstruction magnitude via coboundary $\ell^1$ quotient minimization:
$$\Phi_1^{\mathcal{O}}(S) = \min_{\alpha \in C^0(P_{\mathcal{O}})} \|\pi_{\mathcal{O}}(\omega_1) - d_0^{\mathcal{O}} \alpha\|_{1, \mathcal{W}_{1, \mathcal{O}}},$$
and boundary curvature:
$$\Gamma_2^{\mathcal{O}}(S) = \|d_1^{\mathcal{O}} \pi_{\mathcal{O}}(\omega_1)\|_{1, \mathcal{W}_{2, \mathcal{O}}}.$$

*Remark on Quotient Evaluation:* When discrete coboundary $d_0^{\mathcal{O}}$ is explicitly declared, $\Phi_1^{\mathcal{O}}$ is solved via exact $\ell^1$ linear programming minimization. When $d_0^{\mathcal{O}}$ is absent, $\Phi_1^{\mathcal{O}}$ evaluates the weighted $\ell^1$ norm of an externally certified optimal residual representative.

### Definition 2.2 (Joint Detector Adequacy)
An observer bundle $\mathfrak{O}$ satisfies *Joint Detector Adequacy* over carrier coordinates $k \in \{0, \dots, m-1\}$ if, for every coordinate $k < m$, there exists at least one observer $\mathcal{O} \in \mathfrak{O}$ whose weight on coordinate $k$ is strictly positive:
$$\forall k < m, \quad \exists \mathcal{O} \in \mathfrak{O} \quad \text{such that} \quad w_k^{\mathcal{O}} > 0.$$
If a carrier coordinate $k$ has $w_k^{\mathcal{O}} = 0$ for all $\mathcal{O} \in \mathfrak{O}$, it lies in the shared blind subspace $\mathcal{B}_{\mathfrak{O}} = \bigcap_{\mathcal{O} \in \mathfrak{O}} \ker(\pi_{\mathcal{O}})$, and bundle-relative descent cannot detect defect accumulation or transfers into coordinate $k$.

---

## 3. The Observer-Robust Control Criterion

### Definition 3.1 (Observer-Robust Policy)
A repair policy $\operatorname{Ctrl}: \operatorname{State} \times \mathfrak{O} \times \operatorname{History} \to \mathcal{O}_{\mathrm{ops}}$ is *observer-robust relative to $\mathfrak{O}$* with parameters $(M_{\max}, R_{\max}, \delta_{\Gamma}, \Gamma_{\max}, \Delta_{\max})$ if, for every transition $S_t \to S_{t+1}$ admitted by the controller, the following conditions hold uniformly across all $\mathcal{O} \in \mathfrak{O}$:

1. **Committed-State Descent Law:**
   $$\Phi_1^{\mathcal{O}}(S_{t+1}) \le \Phi_1^{\mathcal{O}}(S_t) + \varepsilon_{\mathcal{O}}.$$
   Exploratory proposals may produce localized fluctuations within resolution limit $\varepsilon_{\mathcal{O}}$. For long-run descent across $T$ steps, cumulative upward drift is bounded by $\sum_{t=1}^T \varepsilon_{\mathcal{O}} \le \Delta_{\max}$; strict monotonic descent requires $\varepsilon_{\mathcal{O}} = 0$.
2. **Topological Stability Guardrails (Ratio and Absolute Curvature):**
   The piecewise closure ratio is defined by:
   $$R_{cl}^{\mathcal{O}}(S_{t+1}) = \begin{cases} \frac{\Gamma_2^{\mathcal{O}}(S_{t+1})}{\Phi_1^{\mathcal{O}}(S_{t+1})} & \text{if } \Phi_1^{\mathcal{O}}(S_{t+1}) > \varepsilon_{\mathcal{O}}, \\ 0 & \text{if } \Phi_1^{\mathcal{O}}(S_{t+1}) \le \varepsilon_{\mathcal{O}} \text{ and } \Gamma_2^{\mathcal{O}}(S_{t+1}) \le \varepsilon_{\mathcal{O}}, \\ \infty & \text{if } \Phi_1^{\mathcal{O}}(S_{t+1}) \le \varepsilon_{\mathcal{O}} \text{ and } \Gamma_2^{\mathcal{O}}(S_{t+1}) > \varepsilon_{\mathcal{O}}, \end{cases}$$
   and must satisfy $R_{cl}^{\mathcal{O}}(S_{t+1}) \le R_{\max}$ across all $\mathcal{O} \in \mathfrak{O}$.
   Absolute curvature stability requires:
   $$\Gamma_2^{\mathcal{O}}(S_{t+1}) \le \Gamma_2^{\mathcal{O}}(S_t) + \delta_{\Gamma}, \quad \text{and} \quad \Gamma_2^{\mathcal{O}}(S_{t+1}) \le \Gamma_{\max}.$$
   *Remark on Curvature Stability:* Bounding the ratio $R_{cl} = \Gamma_2 / \Phi_1$ alone is insufficient to prevent tearing, because a transition that sharply reduces $\Phi_1$ (e.g. from 100 to 50) while increasing $\Gamma_2$ (e.g. from 1 to 50) can maintain $R_{cl} \le 1$ despite severe boundary disruption. The absolute limits $\delta_{\Gamma}$ and $\Gamma_{\max}$ rule out such false repairs.
3. **Worst-Case Residual Boundedness:**
   $$\sup_{\mathcal{O} \in \mathfrak{O}} \Phi_1^{\mathcal{O}}(S_{t+1}) \le M_{\max}.$$

The proved finite form of this ceiling is the natural-number predicate `CeilingAdmitted`: the transition is bundle-admissible and `worstPhi` of the image is at most $M$. Every observer's weighted norm of the image is then at most $M$, and any observer that exceeds $M$ keeps the transition out of the ceiling. The ratio and absolute curvature guards remain controller checks beside that theorem.

### Proposition 3.1 (Bounded Coordinate and Aggregate Diagnostics Under Joint Adequacy)
Assume the observer bundle $\mathfrak{O}$ satisfies Joint Detector Adequacy (Definition 2.2) over carrier coordinates $k < m$. If a candidate transition $c \to c'$ satisfies the Observer-Robust Control Criterion (Bundle Admissibility, Definition 3.1) on $\mathfrak{O}$ with parameters $(M_{\max}, R_{\max}, \delta_{\Gamma}, \Gamma_{\max})$, then:
1. **Aggregate Quotient Residual Descent:** For every observer $\mathcal{O} \in \mathfrak{O}$, the aggregate quotient residual satisfies:
   $$\Phi_1^{\mathcal{O}}(c') \le \Phi_1^{\mathcal{O}}(c) + \varepsilon_{\mathcal{O}}.$$
2. **Uniform Coordinate Defect Bounding:** For every carrier coordinate $k < m$, there exists an observer $\mathcal{O} \in \mathfrak{O}$ with $w_k^{\mathcal{O}} > 0$ such that the post-transition defect is bounded by the observer's initial budget:
   $$w_k^{\mathcal{O}} \cdot |c'_k| \le \Phi_1^{\mathcal{O}}(c) + \varepsilon_{\mathcal{O}}.$$
   In particular, when observer weights satisfy $w_k^{\mathcal{O}} \ge 1$, the post-transition absolute defect satisfies:
   $$|c'_k| \le \Phi_1^{\mathcal{O}}(c) + \varepsilon_{\mathcal{O}}.$$
3. **Fail-Closed Rejection of Excessive Injections:** Any candidate transition attempting to inject defect into coordinate $k$ such that $w_k^{\mathcal{O}} |c'_k| > \Phi_1^{\mathcal{O}}(c) + \varepsilon_{\mathcal{O}}$ violates observer descent and is strictly rejected fail-closed.

The mechanized bound is that integer statement. The quotient linear program is the Python evaluation used when a coboundary $d_0$ is supplied. It is not the Lean theorem. The empty bundle is not jointly adequate for any positive coordinate count, and the Python constructor rejects it.

*Remark on Monitored Defect Transfer:* Joint detector adequacy bounds post-transition coordinate defects by the initial observer budget; it does *not* claim that defect cannot transfer between monitored subcomplexes when such transfer reduces or preserves the observer's weighted norm. For instance, on two disjoint cycle classes where an observer assigns weight 2 to cycle 1 and weight 1 to cycle 2, moving a unit defect from cycle 1 to cycle 2 reduces $\Phi_1: 2 \to 1$ with $\Gamma_2 = 0$. Because every guardrail passes, this transfer is admitted. Prohibiting transfer between specific monitored subcomplexes requires explicit protected-mode partition guardrails rather than aggregate descent alone.

*Remark on Unmonitored Defect Modes:* If an operator transfers defect into a blind cycle coordinate unmonitored by $\mathfrak{O}$ (as demonstrated in the three-cycle disjoint class counterexample), bundle-relative descent cannot detect this transfer. Without joint detector adequacy across all cycle modes of the underlying complex, the controller ensures under the declared assumptions that *observed* residual increases and curvature surges are rejected across $\mathfrak{O}$; it cannot prevent hidden defect accumulation in unmonitored blind modes.

---

## 4. Multi-Observer Routing Architecture

To select an operator proposal, the controller computes the worst-case residual and average-case diagnostic penalty across the bundle:
$$\mathcal{L}(o, S_t) = \sup_{\mathcal{O} \in \mathfrak{O}} \Phi_1^{\mathcal{O}}(o(S_t)) + \lambda \frac{1}{|\mathfrak{O}|} \sum_{\mathcal{O} \in \mathfrak{O}} \left( \Phi_{\mathrm{sat}}^{\mathcal{O}}(o) + R_{cl}^{\mathcal{O}}(o(S_t)) \right) + \operatorname{Cost}(o).$$
Here, $\pi_{\mathcal{O}}$ restricts the carrier cochain to the observer's monitored coordinates (`projection_indices`), while $\Phi_{\mathrm{sat}}^{\mathcal{O}} \in [0, 1]$ represents the optional satisfaction/logical obstruction channel (which defaults to the saturated residual surrogate $\min(\Phi_1^{\mathcal{O}}, 1.0)$ in the absence of an external SAT oracle).

### Algorithm 1 (Observer-Robust Repair Step)
1. Verify non-empty bundle $\mathfrak{O} \ne \emptyset$; if empty, emit typed refusal `ObserverRefusalStalled`.
2. Generate candidate operator set $\{o_1, \dots, o_m\}$.
3. For each candidate $o$:
   - For each observer $\mathcal{O} \in \mathfrak{O}$:
     - Compute $\Phi_1^{\mathcal{O}}(o(S_t))$, $\Gamma_2^{\mathcal{O}}(o(S_t))$, and $R_{cl}^{\mathcal{O}}(o(S_t))$.
     - If $\Phi_1^{\mathcal{O}}(o(S_t)) > \Phi_1^{\mathcal{O}}(S_t) + \varepsilon_{\mathcal{O}}$, prune $o$.
     - If $\Gamma_2^{\mathcal{O}}(o(S_t)) > \Gamma_2^{\mathcal{O}}(S_t) + \delta_{\Gamma}$ or $\Gamma_2^{\mathcal{O}}(o(S_t)) > \Gamma_{\max}$, prune $o$.
     - If $R_{cl}^{\mathcal{O}}(o(S_t)) > R_{\max}$, prune $o$.
     - If $\Phi_1^{\mathcal{O}}(o(S_t)) > M_{\max}$, prune $o$.
4. If no candidate survives, emit typed refusal `ObserverRefusalStalled`.
5. Otherwise, commit $o^* = \arg\min_o \mathcal{L}(o, S_t)$.

---

## 5. Scope Fences and Nonclaims

1. **No Claims on Cognition or Intelligence:** This work contributes to finite robust control and discrete topological optimization. It makes no claims regarding general intelligence, cognitive architectures, or conscious perception.
2. **Bundle-Relative Scope:** Observer robustness holds strictly relative to the declared class $\mathfrak{O}$. No claim is made for unadmitted observers outside $\mathfrak{O}$.
3. **Coverage and Transfer Scope:** Claims regarding defect bounding hold only under Joint Detector Adequacy across monitored coordinates. Defect in shared blind modes ($\bigcap_{\mathcal{O}} \ker(\pi_{\mathcal{O}})$) cannot be bounded without expanding $\mathfrak{O}$. Furthermore, joint adequacy bounds coordinate defects under the declared assumptions by the initial observer budget; it does not forbid norm-reducing or norm-preserving defect transfers between monitored subcomplexes without explicit partition guardrails.
4. **No Operational Authority:** The controller routes repair operations within an algebraic constraint framework; it mints no external authority or institutional authorization.

---

## 6. Conclusion

Observer-robust control bridges discrete obstruction calculus and multi-observer reality. By enforcing uniform descent, bounded boundary ratios, absolute curvature stability, and diagnostic responsiveness across an entire observer bundle, the architecture prevents unmonitored residual explosions, localized metric gaming, and topological tearing in complex constraint systems.
