# Operator Dynamics and Structural Constraints in L1 Obstruction Systems

## Proposal Without Authority, Evaluator Supremacy Firewalls, and Discrete Cohomological Diagnostics

**Author:** Jeremy H. Carroll  
**Date:** 2026-10-08  
**Version:** 2.0.3  
**DOI:** [10.5281/zenodo.20213064](https://doi.org/10.5281/zenodo.20213064)  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)  
**Subject:** Applied Mathematics / Algebraic Topology / Multi-Agent Systems & AI Safety  

> **Authority Nonclaim:**
> This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing.

## Abstract

This paper operationalizes the "Evaluator Discipline" required for high-fidelity automated reasoning by formalizing the Operator Proposal Layer. In complex search and transport systems, proposal mechanisms often inadvertently contaminate the evaluation process by importing implicit heuristics or structure-as-truth. This work strictly separates proposal generation (search) from gate evaluation (judgment under a declared policy). Operators propose candidate field evolutions $\omega \mapsto \omega'$ but carry zero acceptance authority: every accept/reject decision is a function only of the evaluator-computed obstruction tuple $(\Phi_1, \Gamma_2, R_{cl}, \Xi)$, the evaluator policy, and declared solver conventions—never of an operator's internal structure, parameters, or intent. We establish discrete coboundary defect foundations on finite connected directed graphs, cycle consistency equivalence, second-order closure defects $\Gamma_2 = \|d_1 h_1\|_1$ on 2-complexes, and local-green/global-red atlas gates. The framework enforces operator passivity, ensuring search systems can generate high-fidelity candidates while remaining structurally incapable of promoting their own authority.

**Keywords:** operator proposal layer, finite obstruction calculus, L1 coboundary defects, evaluator supremacy, operator passivity, local-green global-red, cycle consistency, closure defect, discrete cochain complexes, exact rational arithmetic.

---

## Motivation: Why This Matters

In complex automated reasoning systems, proposal mechanisms (search/transport) often inadvertently contaminate the evaluation process by importing implicit heuristics or "structure-as-truth." This paper operationalizes evaluator discipline by strictly separating **proposal generation** (search) from **gate evaluation** (judgment under a declared policy). By formalizing operator passivity, we ensure that search systems can generate high-fidelity candidates while remaining structurally incapable of promoting their own authority.

The discipline this enforces establishes a rigorous separation of roles: the operator proposes candidate field evolutions; the evaluator computes obstruction diagnostics and evaluates gate conditions under a declared policy; and any promotion to authority remains an accountable institutional responsibility. Neither the operator nor the evaluator creates free-standing institutional authority.

Scope

This paper specifies the mechanics of the operator layer:

* **Operational Discipline:** Permitted proposal of candidate field evolutions.
* **Operator Passivity:** Structural inability to define or override acceptance criteria.
* **Residual structure under non-commutative proposals.** **[INTERPRETIVE — possibility claim; see §5]** Distinct proposal orders *may* yield distinct evaluated tuples. This bullet is **not** a claim that measurable residuals are generated: per §5, non-commutativity alone does not force an evaluator-visible difference, since the difference must survive repair minimization and diagnostic projection.

**Terminology fence — "evolution" / "dynamics".** Throughout this paper, "candidate field evolution" names a **single discrete proposal step** $\omega \mapsto T(\omega)$ (§5), and "dynamics" names composition of such steps in a declared finite step index (§6b). Neither imports continuum time, $\exp(tH)$, a flow, or physical dynamics; none of these is constructed at this paper's declared degree. The containing directory's legacy "Operator Dynamics" label is not a scope claim of this paper.

**Axiom (Non-Authority).** The operator layer possesses zero authority. It is structurally isolated from acceptance logic and cannot influence, redefine, or shortcut the independent evaluator's descent criteria.

## 1. Evaluator Supremacy

**Specification (Operator structure cannot promote authority).** **[DEFINITION / ARCHITECTURAL AXIOM — interface contract, not a derived theorem]**
Let $T$ be an operator and $\omega' = T(\omega)$ be a candidate field. Let $\mathcal{E}$ be a finite evaluator whose certification is **imported as a declared specification hypothesis**; this paper does not certify $\mathcal{E}$ and exhibits no descent packet for it. The acceptance state $A(\omega \to \omega')$ is *defined* to be a function of the obstruction tuples $(\Phi_1, \Gamma_2, R_{cl}, \Xi)$, the evaluator policy $\mathcal{P}$, and the **declared solver convention** that selects $f^*$ and hence $h_1$ (§2, §3b) — and of nothing else. The internal structure, parameters, or intent of $T$ are non-informative to $\mathcal{E}$ and are strictly excluded from the decision boundary. (This restates the Non-Authority Axiom as the evaluator's interface signature; conformance of an implementation to this signature is a mechanical audit obligation, not a mathematical theorem.)

**Scope of the evaluator's verdict.** $\mathcal{E}$'s accept/reject output is a **routing terminal** under the declared policy — at most a `VerifierScopedAuthority` relative to that policy, gauge, and solver convention. It is not an authority terminal, not a semantic verdict, and not a promotion. The operator proposes; the evaluator judges its declared lane; **promotion to authority is a separate verified descent step that neither the operator nor the evaluator performs.**

\[
\boxed{
\text{Operator structure cannot promote authority.}
}
\]

## 2. Obstruction System (Foundation)

Let $P = (V, E)$ be a finite connected directed graph.

**Definition (discrete coboundary).** Define $d_0 : C^0(P) \to C^1(P)$ by:
$$
(d_0 f)(e_{ij}) = f(j) - f(i)
$$

**Definition (primary obstruction).** The topological obstruction scalar is:
$$
\Phi_1(\omega) = \inf_{f \in C^0(P)} |\omega - d_0 f|_1
$$

Let $f^*$ denote an optimal scalar achieving the infimum. The infimum is attained on a finite connected graph after fixing the additive gauge, e.g. by setting one vertex potential to zero; the resulting finite-dimensional convex $\ell^1$ program has a minimizer, though it need not be unique. Define the irreducible residual:
$$
h_1 = \omega - d_0 f^*
$$

**Structural facts:**

* $h_1$ is irreducible with respect to $d_0$ ($\ell^1$-optimal residual). When a 2-complex $(P,\sigma_2)$ is specified and $d_1h_1=0$, the residual determines a representative of a class in $H^1(P;\mathbb{R})$.
* If $f^*$ is a true $\ell^1$-optimal section, then $\Phi_1 = |h_1|_1$.
* For finite connected graphs without 2-cells, nonzero $\Phi_1$ is supported by nontrivial cycle-space content. If the underlying undirected graph is a tree, equivalently $\beta_1(P)=0$, then $C^1(P)=\operatorname{im}(d_0)$, hence $\Phi_1=0$ for every edge field.

## 3. Diagnostic Hierarchy

3a. Cycle consistency

For any cycle $C$ in the underlying graph, with signs determined by agreement or disagreement with the chosen edge orientation,
$$
\Delta(C)=\sum_{e\in C}\epsilon_e\omega(e),\qquad \epsilon_e\in\{\pm1\}.
$$

**Theorem (cycle–obstruction equivalence).** **[STANDARD + corpus citation [1]; proof = exactness characterization]**
For a finite connected graph with no additional 2-cell constraints,
$$
\Phi_1 = 0 \iff \Delta(C)=0 \;\forall\; \text{cycles } C \in Z_1(P;\mathbb{R}),
$$
where $\Delta(C)$ uses the signed edge sum of §3a; it suffices to check a cycle basis.
*(Proof sketch: $\Phi_1=0$ iff $\omega\in\operatorname{im}(d_0)$. Attainment follows from the finite graph LP after gauge fixing. An edge field is exact iff its signed sum vanishes on every cycle in the cycle space $Z_1(P;\mathbb{R})$, the standard cycle-space characterization [6, §2.1]; see the quotient-norm companion paper for the LP formulation.)*

3b. Second-order obstruction

**Prerequisite.** Let $(P, \sigma_2)$ be a 2-cell complex.

**Declared regime data.** **[DECLARED AXIOM — assumption of the 2-complex, not proved here]** This section's obstruction regime is the degree-1 window of the finite cochain complex
$$
C^0(P) \xrightarrow{\;d_0\;} C^1(P) \xrightarrow{\;d_1\;} C^2(P,\sigma_2),
\qquad d_1 \circ d_0 = 0 .
$$
The complex condition $d_1 \circ d_0 = 0$ is **assumed as part of the declared 2-cell structure** $\sigma_2$; it is what makes $\Gamma_2$ readable as a *closure* defect rather than an arbitrary functional of $h_1$. It is a declared property of the admitted regime, not a theorem of this paper. Where no 2-complex is declared, $\Gamma_2$ is undefined and only $\Phi_1$ is available (cf. §2, which requires no 2-cells).

**Definition.** The closure defect is:
$$
\Gamma_2 = \|d_1 h_1\|_1
$$
Because $d_1 \circ d_0 = 0$ on any declared 2-complex, $d_1 h_1 = d_1(\omega - d_0 f^*) = d_1 \omega$. Consequently, $\Gamma_2 = \|d_1 \omega\|_1$ is an invariant of the cochain field $\omega$ and does not depend on which optimal potential $f^*$ is selected by the $\ell^1$ solver.

**Proposition.** **[PROVED on the oriented triangle]** For the all-ones face, the coboundary $(f_1-f_0,f_2-f_1,f_0-f_2)$ sums to $0$, so $\lvert\sum(\omega-d_0 f)\rvert=\lvert\sum\omega\rvert$, and $\Phi_1(\omega)=0$ implies $\Gamma_2(\omega)=0$. The field $(2,-1,-1)$ has both equal to $0$. The general step on an arbitrary declared complex still uses the declared identity $d_1\circ d_0=0$; that identity is not a theorem of this paper. The converse remains false.

**Closure ratio and routing statuses.**

**[IMPLEMENTATION CONVENTION]** In exact mathematics, the algebraic closure ratio $R_{\mathrm{exact}} = \Gamma_2 / \Phi_1$ is defined whenever $\Phi_1 > 0$. On any fixed finite 2-complex, the operator norm inequality yields the finite bound:
$$
\Gamma_2 = \|d_1 \omega\|_1 = \|d_1 h_1\|_1 \le \|d_1\|_{1 \to 1} \|h_1\|_1 = \|d_1\|_{1 \to 1} \Phi_1,
$$
which implies that $R_{\mathrm{exact}} \le \|d_1\|_{1 \to 1} < +\infty$ is strictly bounded on the complex whenever $\Phi_1 > 0$. The sentinel value $+\infty$ is not literal infinite topological curvature; it is an implementation guard signaling that the boundary defect exceeds the resolution threshold while the residual remains below it.

For numerical and finite-evaluation robustness, the evaluator computes both $R_{\mathrm{exact}}$ and the $\varepsilon$-based piecewise ratio $R_\varepsilon$ alongside an explicit named routing status:
$$
R_\varepsilon = \begin{cases}
\Gamma_2 / \Phi_1 & \text{if } \Phi_1 > \varepsilon \quad (\text{status: } \texttt{REGULAR}) \\
0 & \text{if } \Phi_1 \le \varepsilon \text{ and } \Gamma_2 \le \varepsilon \quad (\text{status: } \texttt{SUB\_EPSILON\_FLAT}) \\
+\infty & \text{if } \Phi_1 \le \varepsilon \text{ and } \Gamma_2 > \varepsilon \quad (\text{status: } \texttt{UNBOUNDED\_CURVATURE\_SENTINEL})
\end{cases}
$$
In exact arithmetic, when $0 < \Phi_1 \le \varepsilon$ while $\Gamma_2 \le \varepsilon$, the sub-epsilon flat branch assigns $R_\varepsilon = 0$ even if $R_{\mathrm{exact}} > 1$ (for instance, with $\Phi_1 = 1/4000$, $\Gamma_2 = 1/2000$, and $\varepsilon = 1/1000$, the exact ratio is $R_{\mathrm{exact}} = 2$, but both are $\le \varepsilon$, routing to $R_\varepsilon = 0$). An evaluator accepting under $R_\varepsilon \le 1$ when $\Phi_1$ strictly descends is faithful to this piecewise convention, but must not be inferred as establishing an exact ratio ceiling $R_{\mathrm{exact}} \le 1$. Transition evaluation enforces the hard gate on $R_\varepsilon$, rejecting transitions in the $\texttt{UNBOUNDED\_CURVATURE\_SENTINEL}$ status unconditionally.

## 4. Multi-Channel Obstruction Fields

**Status:** Modeling extension

4a. Multi-channel $\Phi_1$

Let $P = (V, E)$ be a finite directed graph and let each edge carry a $k$-channel obstruction vector:
$$
\omega \in C^1(P, \mathbb{R}^k)
$$

Let $f \in C^0(P, \mathbb{R}^k)$ assign a $k$-vector to each node. Define:
$$
(d_0 f)(e_{ij}) = f(j) - f(i) \in \mathbb{R}^k
$$

Choose a local channel gauge $g : \mathbb{R}^k \to \mathbb{R}_{\ge 0}$. The multi-channel obstruction is:
$$
\boxed{
\Phi_{1,g}(\omega) = \inf_{f \in C^0(P, \mathbb{R}^k)} \sum_{e \in E} g\bigl(\omega(e) - (d_0 f)(e)\bigr)
}
$$

and the optimal residual is $h_{1,g} = \omega - d_0 f^*$.

**Required assumptions on $g$.** For $\Phi_{1,g}$ to be valid, $g$ must be a norm on $\mathbb{R}^k$:

1. Positive definite: $g(x) = 0 \iff x = 0$
2. Absolutely homogeneous: $g(\lambda x) = |\lambda| g(x)$
3. Subadditive: $g(x+y) \le g(x) + g(y)$

**Important special cases:**

| Observer | Local gauge $g$ | Global form | Separability |
|---|---|---|---|
| Coordinate-separable ($\ell^1$) | $g(x) = \|x\|_1$ | $\sum_e \sum_a |\omega_a(e) - (d_0 f_a)(e)|$ | Fully separable by channel |
| Rotational / SO($k$) | $g(x) = \|x\|_2$ | $\sum_e \|\omega(e) - (d_0 f)(e)\|_2$ | $\ell^1(E; \ell^2(\mathbb{R}^k))$ |
| Trace / quantum **[IMPORTED — Q-gated; see fence below]** | $g(X) = \|X\|_{\mathrm{tr}}$ | $\sum_e \|\omega(e) - (d_0 f)(e)\|_{\mathrm{tr}}$ | $\ell^1(E; \mathcal{T}_1(\mathcal{H}))$ |

The trace gauge convention must be declared: unhalved Schatten-1 norm $\|X\|_1$, or half-normalized trace distance $\frac12\|X\|_1$. The dual bounds change accordingly.

> **SCOPE FENCE — the trace/quantum row is an import, not a construction.** The Hilbert space $\mathcal{H}$ and the trace-class ideal $\mathcal{T}_1(\mathcal{H})$ in the third row are **imported representation structures**. They are not constructed at this paper's declared finite degree, and $\mathcal{T}_1(\mathcal{H})$ is not finite-dimensional for general $\mathcal{H}$ — so that row alone leaves the finite regime named in this paper's title. It is listed to record how a declared local gauge would be read *if* such a carrier were separately admitted; this paper admits no such carrier and derives nothing from it. Any use of that row is **Q-gated**: it requires a separate admission of $\mathcal{H}$, a declared trace-norm convention, and — for any quantum reading — the Born firewall of §6a. Nothing in §4a derives Hilbert space, density operators, the Born rule, or a quantum realization; the first two rows ($\ell^1$, $\ell^2$) are the finite cases actually used in this paper.

**Imported Result — Replica extensivity fixes outer $\ell^1$.** **[IMPORTED FROM COMPANION — not re-proved here]** Under independent graph replica additivity, disjoint edge support additivity, and a fixed local observer gauge $g$, the canonical admissible global obstruction form under these assumptions is $\Phi_{1,g}$. Replica extensivity fixes the **outer edge aggregation** to be $\ell^1$, while observer symmetry determines the **inner local gauge** $g$. *(The outer-$\ell^1$ selection is the coordinate-wise additivity classification and its Banach-presheaf extension, proven in the companion classification paper "$\ell^1$-Native Cohomology of Defect Fields" (record 20186523, listed in [4]); this paper imports, and does not re-prove, that result.)*

For multi-channel fields, $\ell^1$ does not necessarily mean coordinate-wise $\ell^1$ over channels. The canonical multi-channel obstruction is $\ell^1(E; g)$, where $g$ is the local observer gauge on channel space.

4b. Channel operator family

**Channel operator family (modeling choice).** Introduce:
$$
T_a : \mathbb{R}^k \to \mathbb{R}^k
$$

**Lie algebra closure (assumed class, not $\ell^1$-derived).** For real channel operators $T_a : \mathbb{R}^k \to \mathbb{R}^k$, skew-adjoint generators satisfying $T_a^T = -T_a$ (real skew-symmetric matrices) close to the Lie algebra $\mathfrak{so}(k)$. If channel space is generalized to complex carriers $\mathbb{C}^k$, skew-Hermitian generators satisfying $T_a^\dagger = -T_a$ close to $\mathfrak{u}(k)$.

> **Critical statement.** This follows from the skew-adjoint assumption. It is not a consequence of $\ell^1$ obstruction theory. Operators may be parameterized by Lie algebra generators, but this has no effect on evaluation. The evaluator sees only $(\Phi_1, \Gamma_2, R_{cl}, \Xi)$.

## 5. Transport Operators

**Status:** Experimental module

**Definition.** A transport operator is a map $T : C^1(P) \to C^1(P)$ that proposes a candidate evolution $\omega \mapsto \omega' = T(\omega)$. Per the terminology fence in §Scope, "evolution" here names **one discrete proposal step** — the application of a map to a declared edge field. $T$ carries no time parameter, generates no flow, and is not $\exp(tH)$ for any $H$; no continuum time or physical dynamics is constructed at this degree.

$T$ must preserve edge cardinality and indexing of $P$ unless explicitly declared as a structural operator (e.g., $\Pi_{12}$ lift) evaluated separately.

Operational Constraints

Proposal generation is strictly passive. Operators propose candidate fields ($\omega \mapsto \omega'$) but are structurally excluded from evaluation and decision-making.

**Specification (operator compatibility).** **[DEFINITION / ARCHITECTURAL — interface contract]** Given operator $T$ and candidate $\omega' = T(\omega)$, correctness of the transition is determined exclusively by the evaluator via $(\Phi_1, \Gamma_2, R_{cl}, \Xi)$. The operator itself cannot define, override, or influence the acceptance decision.

**Observation — Non-commutativity may become evaluator-visible** **[INTERPRETIVE / POSSIBILITY WARNING]**
For operators $T_1,T_2$, if
$$
T_1T_2(\omega)\ne T_2T_1(\omega),
$$
then the two proposal orders may produce distinct evaluated obstruction tuples:
$$
(\Phi_1,\Gamma_2,R_{cl},\Xi)(T_1T_2\omega) \ne (\Phi_1,\Gamma_2,R_{cl},\Xi)(T_2T_1\omega).
$$
Non-commutativity alone does not force evaluator-visible difference; the difference must survive repair minimization and diagnostic projection.

**Reference operator class:** `CyclicShift` — cyclic permutation of edge weights with configurable scale. Period-3 on $C_3$ graphs when unscaled. **[SPECIFICATION — not a verified implementation claim]** As of this snapshot no `CyclicShift` symbol resolves in the Omega Rust workspace; the class is specified here and exercised by the self-contained Python replay below, which is the only executable artifact this section relies on. See the Appendix registry caveat.

### Worked Replay — `CyclicShift` Preserves $\Phi_1$ on $C_3$

On $C_3$ with $\omega=(1,0,0)$ the cycle obstruction is $\Phi_1=1$. Unscaled `CyclicShift` cyclically permutes edge weights, $\omega\mapsto(0,1,0)\mapsto(0,0,1)$. **[PROVED as equality of the three cycle sums; the Python replay calls `compute_phi1_cycle_graph`]** Because it only relabels the edges of a symmetric cycle, it preserves the cycle sum, so the evaluator computes

$$
\Phi_1(\omega)=\Phi_1(\mathrm{shift}\,\omega)=\Phi_1(\mathrm{shift}^2\,\omega)=1.
$$

The proposal therefore generates a period-3 orbit that the guarded descent law rejects at every step — no strict $\Phi_1$ decrease, and no $\Gamma_2$ or $\Xi$ tiebreak applies. This illustrates the core discipline: operator activity, however structured, yields no acceptance without an evaluator-visible obstruction decrease.

```python
import numpy as np
from scipy.optimize import linprog
def phi1(B, w):
    E, V = B.shape
    A = np.vstack([np.hstack([B, -np.eye(E)]), np.hstack([-B, -np.eye(E)])])
    return linprog(np.r_[np.zeros(V), np.ones(E)], A_ub=A, b_ub=np.r_[w, -w],
                   bounds=[(None, None)]*V + [(0, None)]*E, method="highs").fun
B3 = np.array([[-1,1,0],[0,-1,1],[1,0,-1]], float); w = np.array([1.,0,0])
print([round(phi1(B3, np.roll(w, k)), 3) for k in range(3)])   # [1.0, 1.0, 1.0]
```

Expected output: `[1.0, 1.0, 1.0]`.

## 6. Evaluator Pipeline

```text
graph P
   ↓
ω (possibly multi-channel)
   ↓
transport T proposes ω'
   ↓
solver \to h_1
   ↓
Φ_1, Γ₂, R_cl, Ξ
   ↓
evaluator \to accept / reject
```

**$\Xi$ (external distortion functional) and trust boundary.** $\Xi$ is a representative distortion scalar defined in Paper 009 and treated here as an opaque scalar input to the evaluator. It measures representative distortion between the selected primal residual and selected optimal dual witness. Its internal structure is not specified in this paper. Because $\Xi$ is imported across an external boundary, independent field certification from 1-cochains alone computes $(\Phi_1, \Gamma_2, R_{cl})$ and sets $\Xi$ to the declared neutral convention (0) unless an evaluator-bound functional or verified receipt is provided. Caller-supplied $\Xi$ values cannot manufacture a third-order tiebreak descent on an unchanged field without an evaluator-bound verifier.

**Guarded Descent Law.** **[DEFINITION / ARCHITECTURAL — evaluator policy, not a derived theorem]** The evaluator evaluates a proposed transition from before-state $S$ to after-state $S'$ by imposing a strict lexicographic descent on $(\Phi_1, \Gamma_2, \Xi)$ subject to an unconditional hard guard on $R_{cl}(S')$. For multi-channel fields, $\Phi_1$ means $\Phi_{1,g}$ for the declared observer gauge $g$ of §4a, reducing to the scalar $\Phi_1$ of §2 when $k=1$.

0. **Gate:** $R_{cl}(S') \le R_{cl,\max}$ must hold (and $R_{cl}(S') < +\infty$). If violated, reject unconditionally.
1. $\Phi_1(S') < \Phi_1(S)$ \to **accept** (primary descent),
2. $\Phi_1(S') = \Phi_1(S)$ **and** $\Gamma_2(S') < \Gamma_2(S)$ \to **accept** (second-order tiebreak),
3. $\Phi_1(S') = \Phi_1(S)$ **and** $\Gamma_2(S') = \Gamma_2(S)$ **and** $\Xi(S') < \Xi(S)$ \to **accept** (third-order tiebreak).
4. Otherwise (including unchanged tuples and worsening proposals) \to **reject**.

No other acceptance path exists. The lexicographic priority is strict: $\Phi_1$ dominates $\Gamma_2$ dominates $\Xi$. Unchanged tuples and worsening proposals are rejected.

**Specification consequence (guarded evaluator non-interference).** **[SPECIFICATION / EXTERNAL UNVERIFIED IMPORT — see scope note]** If two operator proposals have the same before/after evaluator tuples and the same $R_{cl}$ gate truth value, then their accept/reject states are identical regardless of operator identity, source state, target state, or operator metadata. Moreover, acceptance implies both the $R_{cl}$ gate and strict lexicographic descent; a failed $R_{cl}$ gate, an unchanged tuple, a $\Phi_1$ increase, or a $\Gamma_2$ increase under a $\Phi_1$ tie is rejected.

> **Scope note on external formalization (read before citing).** This is a *consequence of the interface definition*, not a discovered property of any system. Earlier design sketches in Lean (`PaperAF000.L011_01_GuardedEvaluator`) stipulated non-interference by definition (`OperatorAccepted` binds `_op`, `_source`, `_target` and ignores them). Those external sketches are not bundled or verified in this deposit. Conformance of any evaluator to this specification is certified by the sovereign Python verification suite and exact rational test suite (`test_evaluator_supremacy_and_operator_passivity`). The names listed below remain external. The bundled Lean file `lean4/Proposal.lean` mechanizes only the finite sentences of ledger rows C5, C13, C14, and C19.

The Lean theorem inventory is:

* `PaperAF000.operator_identity_nonpromotion`
* `PaperAF000.accept_requires_rcl_gate`
* `PaperAF000.accept_requires_strict_lex_descent`
* `PaperAF000.reject_without_rcl_gate`
* `PaperAF000.reject_without_strict_descent`
* `PaperAF000.unchanged_tuple_rejected`
* `PaperAF000.phi_increase_rejected`
* `PaperAF000.gamma_increase_with_phi_tie_rejected`
* `PaperAF000.equal_diagnostics_same_acceptance`

> **Dependency caveat.** That repeated $\Phi_1$-descent acceptance drives the system to the $\ell^1$/LP optimum depends on the open descent-convergence conjecture (Conjecture 4.3 of [2]); live code is a 1-step subgradient method — see 007 code-status note / 899 backlog.

6a. LGGR Operator Atlas and Sheaf Gluing Constraint

**Theorem (operator-atlas LGGR non-promotion).** **[PROVED for the triangle witness below; the general cover statement is the surrounding explanation and is not a separate Lean theorem]**
Let $\{U_i\}_{i\in I}$ be a finite declared cover of an obstruction carrier (concretely: each $U_i$ is a subgraph of $P$, restriction is edge-weight restriction $\omega\mapsto\omega|_{U_i}$, and overlap $U_i\cap U_j$ is the induced subgraph on shared edges) and let $T_i$ be operator proposals on the corresponding local edge-field charts. Suppose each local proposal is *locally green*: its local diagnostic projection either descends through the local quotient or satisfies the local guarded-descent test. This does not imply global acceptance. A global accept state is reachable only if the assembled candidate satisfies the declared overlap/gluing compatibility **and** the independently computed global tuple $(\Phi_1,\Gamma_2,R_{cl},\Xi)$ passes the evaluator policy. These are **necessary conditions for a routing accept, and they license nothing**: passing them yields a policy outcome, not a lift, a certificate, or an authority terminal (a lift additionally requires an obstruction witness, a preservation witness, a non-destruction check, a budget/authority boundary, and a terminalizer route — none supplied here). If an overlap residual, cocycle defect, or augmented global diagnostic fails to vanish/pass, the atlas remains globally red even though every local chart is green.

Equivalently: local chart consistency is a presheaf matching condition. Compatible local edge data glue into a global cochain section purely by presheaf overlap agreement, independently of policy acceptance. However, existence of a glued global section does not imply that the resulting global proposal is accepted: an assembled global section constitutes an *accepted global proposal* only if its independently computed global obstruction tuple (\Phi_1, \Gamma_2, R_{cl}, \Xi) additionally satisfies the guarded evaluator policy. The operator atlas may propose compatible local sections, but it cannot promote them to an accepted global proposal, licensed lift, repair certificate, or authority terminal.

**Proof.** The Non-Authority Axiom fixes the acceptance signature: acceptance is a function only of the evaluator-computed tuple and policy, not of operator internals. Therefore local operator success can enter the evaluator only as candidate data. By the primitive-difference/factorization reading, a local-green quotient may identify candidates that an augmented global diagnostic separates; any global diagnostic must factor through the chosen quotient before a local certificate can be reused globally. If it does not factor, this is exactly the Local-Green/Global-Red obstruction.

In sheaf language, chartwise agreement is presheaf matching data. Compatible local edge data glue into a global cochain section purely by presheaf overlap agreement, independently of policy acceptance. However, an assembled global section constitutes an accepted global proposal only if restriction maps, overlap residuals, cocycle checks, and the global evaluator terminal all pass in the declared quotient. Lift evidence, repair-boundary evidence, repair witnesses, repair certificates, terminal packets, and raw-score classifiers are separate gates in the same firewall. Missing gate evidence leaves the proposal in the data/non-authority lane. Thus local green cannot promote itself to global authority. $\square$

**External Lean specifications (unverified in this deposit).** Earlier design explorations referenced external Lean specifications under `PaperAF000`. However, the repository certificates indicate that source proofs are absent from this release (`source_exists: false`). Consequently, this deposit does not bundle or support independent replay of those Lean scripts; they are retained as external design references only. The finite sentences of C5, C13, C14, and C19 are elaborated in `lean4/Proposal.lean` and checked by the Python suite. The primitive-difference theorem is parameterized by arbitrary state type, chart index type, local diagnostic type, global diagnostic type, and primitive zero relation. This is the current maximal EPK generalization in the declared interface: a local family factors through the primitive quotient exactly when every local coordinate is invariant; the paired local/global dashboard factors exactly when the global diagnostic is invariant too. The overlap-payload criterion strengthens the atlas audit: once local charts and their pairwise overlap payloads are quotient-compatible, augmented atlas/global descent is equivalent to global diagnostic quotient-compatibility. The concrete overlap layer splits the abstract gluing gate into pairwise residual predicates, triple cocycle residual predicates, and the terminal guarded evaluator predicate. The restriction-map layer computes those pair and triple residual predicates from declared local sections and restriction maps. The finite edge-cover layer lists charts and edges explicitly and establishes that pairwise-compatible local edge values glue to a global edge section; the declared subgraph-cover layer instantiates that result for obstruction-graph subgraphs and establishes the pair-compatibility/global-section equivalence for edge values. The declared subgraph-cover cochain layer names the `d0` residual as equality of local edge values on shared graph incidence, names the `d1` residual as the triple-overlap compatibility forced by those pair residuals, and wires both predicates into the guarded evaluator terminal. The signed incidence layer computes integer `d0` differences, integer `d1` cycle sums, and finite L1 residual totals, and feeds them to the evaluator tuple as its `Phi`/`Gamma`/`Xi` fields. These gluing constructions use `Classical.choice` to choose a covering chart for each edge.

> **SCOPE FENCE — the Lean `Phi` is not the $\Phi_1$ of §2.** The Lean `Phi` field is a finite sum of declared cell residuals, $\sum |{\rm left}-{\rm right}|$ over `Int` cells, taken with `natAbs`. It contains **no infimum over $f \in C^0(P)$, no gauge fixing, and no dual witness** — it is the norm of a *declared* residual list, not the gauge-optimized residual of §2's convex program $\Phi_1(\omega)=\inf_f|\omega - d_0f|_1$. Likewise the Lean `Gamma` is a declared triple-cycle sum rather than $|d_1h_1|_1$ for an optimal $h_1$, and the Lean `Xi` is a declared `Nat` debt field, not the Paper 009 distortion functional. **No theorem in `PaperAF000` links any of these to their §2/§3b/§6 namesakes**, and the names in the Lean source should not be read as asserting such a link. By the standard applied elsewhere in the Omega kernel — where a raw representative norm is explicitly *not* $\Phi_1$ and cannot be promoted to a verified quotient-distance result without a certified primal/dual pair — the Lean `Phi` is a raw representative norm. Supplying the extraction that would earn the identification, and its parity with the Rust `phi1`/`gamma2` certificates, is the open obligation recorded below; it is not done here. Lean also verifies that missing pair compatibility, missing `d0`/`d1` residuals, missing local evidence, missing `R_cl`, or missing evaluator descent rejects acceptance even when local evidence is green. If a zero-related witness pair disagrees globally, local green remains globally red.

Core theorem names:

* `PaperAF000.local_green_does_not_close_overlap`
* `PaperAF000.local_green_does_not_force_global_tuple`
* `PaperAF000.exists_local_green_global_red_atlas`
* `PaperAF000.evaluated_atlas_rejects_without_overlap`
* `PaperAF000.evaluated_atlas_rejects_without_evaluator_descent`
* `PaperAF000.local_family_factor_exists_iff`
* `PaperAF000.joint_local_global_factor_exists_iff`
* `PaperAF000.primitive_difference_operator_atlas_lggr_nonpromotion`
* `PaperAF000.overlap_payload_global_lggr_nonpromotion`
* `PaperAF000.overlap_payload_global_factor_exists_iff`
* `PaperAF000.overlap_payload_global_factor_iff_global_invariant`
* `PaperAF000.overlap_payload_global_no_factor_of_global_not_invariant`
* `PaperAF000.primitive_difference_pair_lggr_nonpromotion`
* `PaperAF000.concrete_overlap_accept_requires_overlap_residual`
* `PaperAF000.concrete_overlap_accept_requires_cocycle_residual`
* `PaperAF000.concrete_evaluated_overlap_rejects_without_overlap_residual`
* `PaperAF000.concrete_evaluated_overlap_rejects_without_cocycle_residual`
* `PaperAF000.concrete_evaluated_overlap_rejects_without_evaluator_descent`
* `PaperAF000.concrete_evaluated_overlap_rejects_without_strict_descent`
* `PaperAF000.exists_concrete_overlap_local_green_global_red`
* `PaperAF000.exists_concrete_cocycle_local_green_global_red`
* `PaperAF000.restriction_accept_requires_pair_compatibility`
* `PaperAF000.restriction_accept_requires_triple_cocycle`
* `PaperAF000.restriction_evaluated_rejects_without_pair_compatibility`
* `PaperAF000.restriction_evaluated_rejects_without_triple_cocycle`
* `PaperAF000.restriction_evaluated_rejects_without_evaluator_descent`
* `PaperAF000.exists_restriction_pair_local_green_global_red`
* `PaperAF000.exists_restriction_triple_local_green_global_red`
* `PaperAF000.edge_pair_compatibility_glues_global_section`
* `PaperAF000.edge_cover_accept_glues_global_section`
* `PaperAF000.edge_cover_evaluated_accept_glues_global_section`
* `PaperAF000.edge_cover_evaluated_rejects_without_pair_compatibility`
* `PaperAF000.edge_cover_evaluated_rejects_without_evaluator_descent`
* `PaperAF000.exists_edge_cover_local_green_global_red`
* `PaperAF000.subgraph_pair_compatibility_glues_global_section`
* `PaperAF000.subgraph_global_section_implies_pair_compatibility`
* `PaperAF000.subgraph_global_section_iff_pair_compatible`
* `PaperAF000.subgraph_cover_accept_glues_global_section`
* `PaperAF000.subgraph_cover_accept_requires_pair_compatibility`
* `PaperAF000.subgraph_cover_rejects_without_pair_compatibility`
* `PaperAF000.subgraph_cover_evaluated_accept_glues_global_section`
* `PaperAF000.subgraph_cover_evaluated_rejects_without_pair_compatibility`
* `PaperAF000.subgraph_cover_evaluated_rejects_without_evaluator_descent`
* `PaperAF000.exists_subgraph_cover_local_green_global_red`
* `PaperAF000.subgraph_d0_residual_iff_pair_compatible`
* `PaperAF000.subgraph_d1_residual_iff_triple_compatible`
* `PaperAF000.subgraph_cochain_accept_iff_cover_accept`
* `PaperAF000.subgraph_cochain_accept_requires_d0_residual`
* `PaperAF000.subgraph_cochain_accept_requires_d1_residual`
* `PaperAF000.subgraph_cochain_accept_requires_global_tuple`
* `PaperAF000.subgraph_cochain_rejects_without_d0_residual`
* `PaperAF000.subgraph_cochain_rejects_without_d1_residual`
* `PaperAF000.subgraph_cochain_accept_glues_global_section`
* `PaperAF000.subgraph_cochain_evaluated_accept_glues_global_section`
* `PaperAF000.subgraph_cochain_evaluated_rejects_without_d0_residual`
* `PaperAF000.subgraph_cochain_evaluated_rejects_without_d1_residual`
* `PaperAF000.subgraph_cochain_evaluated_rejects_without_evaluator_descent`
* `PaperAF000.exists_subgraph_cochain_local_green_global_red`
* `PaperAF000.signed_d0_residuals_cons`
* `PaperAF000.signed_d1_residuals_cons`
* `PaperAF000.signed_d0_l1_cons`
* `PaperAF000.signed_d1_l1_cons`
* `PaperAF000.signed_incidence_eval_phi_eq_d0_l1`
* `PaperAF000.signed_incidence_eval_gamma_eq_d1_l1`
* `PaperAF000.signed_incidence_eval_xi_eq_debt`
* `PaperAF000.signed_incidence_accept_requires_local_green`
* `PaperAF000.signed_incidence_accept_requires_rcl_gate`
* `PaperAF000.signed_incidence_accept_requires_tuple_descent`
* `PaperAF000.signed_incidence_rejects_without_local_green`
* `PaperAF000.signed_incidence_rejects_without_rcl_gate`
* `PaperAF000.signed_incidence_rejects_without_tuple_descent`
* `PaperAF000.signed_incidence_unchanged_tuple_rejected`
* `PaperAF000.exists_signed_incidence_local_green_global_red`

The remaining unmechanized target is not another quotient theorem, edge-section gluing theorem, Boolean residual-gate theorem, or signed residual-tuple theorem of the same form. It is the extraction/binding layer: deriving the signed incidence cells from an oriented obstruction graph and declared subgraph cover, proving that this extraction matches the Rust `phi1`/`gamma2` residual implementation, and then replaying the same evaluator tuple against finite certificates. The current Lean layer verifies the required gate shape, parametric restriction-map discipline, finite edge-cover gluing theorem, declared subgraph-cover edge-section equivalence, declared subgraph-cover cochain residual evaluator, and signed incidence residual tuple without claiming Rust-certifier equivalence.

**Boundary imported from the SO($k$) sweeper review.** The Paper 003 review discipline applies here: local gauge selection and outer aggregation are separate layers. Full local SO($k$) symmetry can select the local $\ell^2$ stalk gauge, but it does not by itself select an unweighted global $\ell^1(E;\ell^2)$ diagnostic; edge decomposability, disjoint additivity, positive weights, and normalization/single-orbit assumptions remain explicit. The same separation controls operator atlases: chart-local symmetry does not supply global aggregation, gluing, or authority.

**Born firewall carry-over.** If an operator chart carries normalized sector weights or a Hilbert-style density encoding, Paper 010's redundancy result may be used only as local normalization bookkeeping. It must not be cited as a Born-rule derivation. Born uniqueness remains imported/conditional (ENC-0317), and no operator-atlas argument in this paper changes that status. Paper 010 and ENC-0317 are internal corpus identifiers; see the companion corpus [4] for the public portion.

6b. EPK Path Erasure Boundary

**Theorem (EPK path operator erasure).** **[SPECIFICATION / EXTERNAL UNVERIFIED IMPORT]**
> **Scope note on external formalization.** The Lean theorems cited below represent external design specifications not bundled or certified in this release. All executable properties are validated locally by the test suite.
Let an evaluated path kernel be any finite list of proposal steps. Each step may carry arbitrary operator metadata and arbitrary source/target state data, but its acceptance predicate is the guarded evaluator predicate on its before/after tuples and $R_{cl}$ gate. Lean now packages this as a trace factorization: step acceptance is equivalent to acceptance of the evaluator trace `(before, after, rclOk)`, and path acceptance is equivalent to acceptance of the list of evaluator traces. Replacing every operator label, source state, and target state in the path with arbitrary replacement metadata preserves path acceptance. Path composition is also exact: a concatenated EPK path is accepted exactly when its left and right segments are accepted, and the same componentwise rule holds for concatenated evaluator-trace paths. Therefore an accepted concatenation projects to accepted prefix/suffix segments, and a rejected segment rejects the whole concatenation. If a path is accepted, every member step has a true $R_{cl}$ gate and strict lexicographic tuple descent; if any member step is rejected, the path is rejected.

Lean verifies this under the theorem names:

* `PaperAF000.step_accepted_iff_trace_accepted`
* `PaperAF000.step_acceptance_ignores_metadata_replacement`
* `PaperAF000.step_acceptance_ignores_operator_replacement`
* `PaperAF000.path_acceptance_append_iff`
* `PaperAF000.trace_path_acceptance_append_iff`
* `PaperAF000.path_acceptance_of_append_left`
* `PaperAF000.path_acceptance_of_append_right`
* `PaperAF000.path_append_rejects_of_left_rejects`
* `PaperAF000.path_append_rejects_of_right_rejects`
* `PaperAF000.trace_path_acceptance_of_append_left`
* `PaperAF000.trace_path_acceptance_of_append_right`
* `PaperAF000.trace_path_append_rejects_of_left_rejects`
* `PaperAF000.trace_path_append_rejects_of_right_rejects`
* `PaperAF000.path_acceptance_iff_trace_path_acceptance`
* `PaperAF000.path_acceptance_ignores_metadata_replacement`
* `PaperAF000.path_acceptance_ignores_operator_replacement`
* `PaperAF000.path_acceptance_requires_step_gate`
* `PaperAF000.path_acceptance_requires_step_descent`
* `PaperAF000.path_rejects_if_member_rejects`
* `PaperAF000.unchanged_step_rejected`

This is the operative EPK boundary for the proposal layer. Operator metadata, source states, and target states can be generalized arbitrarily and then erased without changing acceptance, provided the evaluator trace is unchanged. To make any new operator feature matter, the feature must be declared as part of the evaluator tuple, the overlap/gluing gate, or the primitive quotient kernel. Otherwise it is proposal data only.

**Continuation-stable state erasure extension.** While single-step metadata erasure preserves one-step acceptance, reusing a compressed state description across sequential continuations requires stability under the admitted operator family. The accompanying derivation in `docs/mathematical_extension.md` establishes in this setting that the maximal equivalence relation contained in $\ker(D)$ that is stable under an admitted operator family $\mathcal{T}$ is $x \sim_T y \iff \forall W \in \mathcal{T}^*,\, D(W(x)) = D(W(y))$. The quotient $X / {\sim_T}$ is the coarsest state quotient that preserves diagnostics under all finite continuations and supports induced operator actions. Furthermore, executable path concatenation requires verified endpoint continuity ($S_k^{\mathrm{target}} = S_{k+1}^{\mathrm{source}}$), separating list-level step predicates from composed executable trajectories.

**QM residual-density specialization.** Lean also exposes the same boundary in `QM.PaperAF000OperatorTraceBridge`: a QM-facing density proposal step carries an operator label plus density-like source and target payloads, but acceptance factors through the same PaperAF000 evaluator trace. Theorems `QM.PaperAF000OperatorTraceBridge.density_step_acceptance_iff_trace_accepted` and `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_iff_trace_path_acceptance` state the trace factorization; `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_append_iff` and `QM.PaperAF000OperatorTraceBridge.density_trace_path_acceptance_append_iff` state componentwise acceptance under path concatenation; `QM.PaperAF000OperatorTraceBridge.density_path_append_rejects_of_left_rejects`, `QM.PaperAF000OperatorTraceBridge.density_path_append_rejects_of_right_rejects`, `QM.PaperAF000OperatorTraceBridge.density_trace_path_append_rejects_of_left_rejects`, and `QM.PaperAF000OperatorTraceBridge.density_trace_path_append_rejects_of_right_rejects` state that a rejected density segment still rejects the concatenation; `QM.PaperAF000OperatorTraceBridge.density_step_acceptance_ignores_metadata_replacement` and `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_ignores_metadata_replacement` state that changing operator/density proposal metadata cannot change acceptance when the evaluator trace is fixed. The member-step consequences are now QM-facing too: `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_requires_step_gate` and `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_requires_step_descent` prove that every accepted density-path member has the `R_cl` gate and strict evaluator descent; `QM.PaperAF000OperatorTraceBridge.density_path_rejects_if_member_rejects` establishes that any rejected member rejects the path; and `QM.PaperAF000OperatorTraceBridge.density_unchanged_step_rejected` establishes that unchanged evaluator tuples reject. The same bridge ties the trace interface to the Q admission firewall: `QM.PaperAF000OperatorTraceBridge.density_trace_acceptance_admission_gap_blocks_qheld` and `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_admission_gap_blocks_qheld` state that an accepted evaluator trace cannot bypass incomplete Q admission debt; `QM.PaperAF000OperatorTraceBridge.density_trace_acceptance_without_witness_blocks_terminal` and `QM.PaperAF000OperatorTraceBridge.density_path_acceptance_without_witness_blocks_terminal` state that accepted traces still cannot produce `TerminalWithinScope` without separate witness support. This is a QM-interface firewall only; it does not derive the Born rule, quantum dynamics, continuum behavior, LQG, QHeld status, TerminalWithinScope status, or authority.

## 7. Final Statement

$$
\boxed{
\text{Operators generate candidate field evolutions. Acceptance is determined by a lexicographic descent in } (\Phi_1, \Gamma_2, \Xi), \text{ gated by } R_{cl} \le R_{cl,\max}, \text{ evaluated under the declared policy, gauge, and solver convention, independently of operator structure.}
}
$$

This paper should be cited for the operator non-authority interface: transport operators may generate candidate field evolutions, but acceptance is computed only from evaluator diagnostics and policy. Operator internals, parameterization, Lie-algebra structure, and non-commutativity do not themselves carry authority.

**What this statement is not.** "Acceptance" here is a **routing outcome under a declared policy**, not an authority terminal, not a certificate, and not a claim that the accepted proposal is correct. It is scoped to the declared detector: a proposal invisible to $(\Phi_1,\Gamma_2,R_{cl},\Xi)$ is accepted or rejected on that tuple alone, and no `DetectorAdequacy` certificate is offered here (see the Detector adequacy warning). The tuple is additionally relative to the declared solver convention wherever the $\ell^1$ minimizer is non-unique (§2, §3b). This paper must not be cited for: authority; certification; semantic truth; convergence of repeated descent to the $\ell^1$/LP optimum (open conjecture); or conformance of any implementation to the §1 signature.

Falsifiability

The evaluator-supremacy claim is falsified by any accepted transition whose acceptance depends on operator internal structure rather than on $(\Phi_1,\Gamma_2,R_{cl},\Xi)$ and the declared policy. The guarded-descent law is falsified by an accepted transition that violates the lexicographic order (e.g. $\Phi_1$ strictly increases yet the transition is accepted) or that has $R_{cl}>R_{cl,\max}$. The non-commutativity proposition is falsified only by reading it as an *inevitable* evaluator-visible difference; the paper asserts only possibility.

Related Work and Positioning

1. **Actor/critic and proposer–evaluator separation** in search and reinforcement learning [5]: this layer enforces the separation *structurally* — the proposer is incapable of computing acceptance.
2. **Lie-algebra / skew-Hermitian generators** [2]: the channel operator family is parameterized by $\mathfrak u(k)$ generators as an assumed class, explicitly **not** derived from $\ell^1$ structure.
3. **Lexicographic / constrained multi-objective acceptance** [3]: the guarded descent law is a lexicographic order on $(\Phi_1,\Gamma_2,\Xi)$ with $R_{cl}$ as a hard gate.
4. **Companion corpus papers** 006 ($\Phi_1$ / duality), 009 ($\Xi$), 012 (degree-wise DSL) [4].

References

1. Carroll, J. H. (2026). *Primitive Axiomatics of Finite Obstruction Calculus.* Zenodo. <https://zenodo.org/records/20651224>

2. B. C. Hall, *Lie Groups, Lie Algebras, and Representations*, 2nd ed., Springer, 2015.

3. M. Ehrgott, *Multicriteria Optimization*, 2nd ed., Springer, 2005.

4. J. H. Carroll, "$\ell^1$-Native Cohomology of Defect Fields" (<https://zenodo.org/uploads/20186523>); "Conditional Density Lift and Dual-Witness Ξ Functional" (<https://zenodo.org/records/20192297>); "Degree-Wise Obstruction Calculus and Symbolic DSL" (<https://zenodo.org/uploads/20213227>). Zenodo, 2026.

5. R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press, 2018.

6. A. Hatcher, *Algebraic Topology*, Cambridge University Press, 2002.

---
*End of Monograph.*
