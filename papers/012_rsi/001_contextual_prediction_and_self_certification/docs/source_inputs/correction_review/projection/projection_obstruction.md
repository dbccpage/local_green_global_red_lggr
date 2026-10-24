<div align="center">

# Projection Obstruction for Factorized States

### Nonlinear Dynamics, Conditional ℓ¹ Diagnostics, and Exact Short-Time Defect Bounds

**Author:** Jeremy H. Carroll

**Date:** 2026-10-14

**Version:** 6.9.18

**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

</div>

## Abstract

For finite one- and two-local quantum lattice dynamics starting from a product state, we establish the exact short-time two-site correlation-defect lower bound
$D_e(t)=\lVert\rho_e(t)-\rho_a(t)\otimes\rho_b(t)\rVert_1\geq\nu_e t-24g^2t^2$, where $\nu_e$ is the initial normal product-retraction rate on edge $e$ and $g$ is the full incident interaction norm. All-order commutator bounds yield explicit Taylor coefficients, finite-horizon remainders, and a volume-uniform Lindbladian open-system extension. Lifting expectations to polynomials over cyclic operator subspaces gives a finite onset-or-invariance criterion; for $k$-body connected cumulants, this combines with a Steiner-tree onset bound $\tau_G(S)$, an algebraic cancellation stratification, an incidence-qubit tree construction attaining $\tau_T(S)$, and a boundary-checked local persistent-zero certificate.

Geometrically, we compare the canonical marginal-product retraction against nearest-product trace-norm approximation, derive a dual tangent-space distance formula and a pure-state Pythagorean rate identity $\nu_{\mathrm{global}}^2=\sum_e\nu_e^2$ (together with its cut-edge cluster extension and an intra-cluster entanglement counterexample), and construct explicit state families showing that global and edgewise trace-norm defects are not uniformly equivalent. Along time-dependent variational principle (TDVP) product trajectories, we prove an edge-decomposed Duhamel error bound weighted by Lieb--Robinson light-cone factors.

At the observer and cochain level, we quantify the physical visibility gap between projection-limited local observers and global section defects. On an $n$-qubit Ising ring ($n\ge 5$) and on higher-degree graphs of girth at least $4$ and minimum degree at least $2$, we construct a three-body cycle-cochain adapter on the ring and degree-dependent stabilizer observers on regular graphs. At the exact graph-state time $t_*=\pi/(4|J|)$, every two-body edge defect vanishes identically ($D_e(t_*)=0$, Local Green), yet the ring cycle class is nonzero and the product-state minimax defects remain strictly positive ($r_2\approx0.6823278038$ on the ring, and $r_d^{\mathrm{Q}} > 0$ on $d$-regular graphs, Global Red). These results isolate the physical and geometric core of projection obstruction on quantum lattices, while companion investigations across this series examine higher presheaves, gauge classifications, adaptive numerical prototypes, and operational foundations (§1.2).

---

## 1. Introduction

Projection-based approximations are central to many-body quantum physics and numerical simulation. Methods such as mean-field theory, Hartree--Fock, and product-state variational ansätze replace a correlated many-body state with a factorized product of local states, reducing an exponentially large state space to a tractable product family. Mathematically, this replacement is implemented by a nonlinear retraction $\Pi$. For density matrices, its smooth product extension lives in the affine space of trace-one Hermitian operators; the positive subset has rank boundaries, where a linear tangent space and a feasible tangent cone must be distinguished (§§5.10.2 and 5.11.1). While the computational utility of such retractions is well established, a quantitative mathematical theory of the error they introduce requires answering three foundational questions: how the nonlinear geometry of $\Pi$ shapes the projected vector field and its normal leakage; how local edge residuals aggregate into global diagnostics under explicit observer axioms; and how fast two-body and $k$-body correlation defects grow at short and intermediate times.

In this work, we focus on the core quantum lattice dynamics and the physical gap between local and global observation:

1. **Exact Short-Time Local Defect Bounds, TDVP Duhamel Enclosures, and Connected Cumulant Onset (§5 and §6):** For any finite one- and two-local Hamiltonian with incident interaction norm $g$ evolving from a product state, Theorem 5.1 establishes the exact two-site correlation-defect lower bound $D_e(t)\ge\nu_e t-24g^2t^2$ (extended to open Lindblad dynamics in §5.4.1), where $\nu_e=\lVert Q_e\dot\rho_e(0)\rVert_1$ isolates the normal component of the initial two-site velocity after projecting out one-local tangent motion (Lemma 5.3). Sections 5.8--5.10 extend this estimate to all Taylor orders, establish all-time local dynamical limits under a uniform incident bound and spatial density limits under the additional translation-invariance hypotheses, without invoking Lieb--Robinson bounds, and derive an edge-decomposed Duhamel observable error bound along TDVP trajectories weighted by Lieb--Robinson light-cone factors (Theorem 5.10.A) together with a cut-edge Pythagorean cluster rate law (Theorem 5.10.B). Sections 5.11--5.17 compare the marginal retraction $\Pi$ with nearest-product trace distance, establish pure-state Pythagorean rate identities, establish the Steiner-tree onset bound $m_{\mathrm{onset}}\ge\tau_G(S)$ for $k$-body connected cumulants $\kappa_S(t)$, and classify algebraic cancellation strata and local persistent-zero certificates.
2. **Local Marginal Geometry and 0-Cochain Representations (§2--§4):** In §2 and §3, we establish the smooth product retraction geometry on the affine space of trace-one Hermitian operators, isolating tangent and normal projectors $P_e$ and $Q_e=I-P_e$. In §4, Theorem 4.3.A represents the two-site correlation defect $D_e(t)=\lVert\rho_{uv}(t)-\rho_u(t)\otimes\rho_v(t)\rVert_1$ as the fiber norm of the 0-cochain difference $s_{\mathrm{true}}-s_{\mathrm{prod}}$ of two closed marginal sections, whose unweighted $\ell^1$ summation $C(t)=\sum_e D_e(t)$ is characterized by replica additivity (RE3) and singleton calibration (RE5).
3. **Physical Visibility Gaps and Graph-State Minimax Separation (§7):** Section 7 separates raw projection residuals, induced 1-cochains, and quotient cohomology classes $\Phi([\omega])=\inf_\alpha\lVert\omega-d_0\alpha\rVert_1$. In §7.4, we formalize projection-limited local observer families and exhibit a three-patch carrier with full edge coverage where every local observer reports zero defect ("Local Green") while the global compatibility defect norm is $I(s)=6>0$ ("Global Red"). In §7.8, we construct an explicit three-site stabilizer cochain adapter on an $n$-qubit Ising ring ($n\ge 5$) and establish the Higher-Degree Graph-State Minimax Theorem (Theorem 7.12) on $d$-regular graphs ($d \ge 2$, girth $\ge 4$): at the exact graph-state formation time $t_*=\pi/(4|J|)$, every two-body edge defect $D_e(t_*)$ vanishes identically because $\rho_{uv}(t_*)=I_4/4$, yet the ring cycle quotient class $\Phi(\omega(t_*))=1$ and the product-state minimax defect ($r_2\approx0.6823278038$ on the ring, and $r_d^{\mathrm{Q}} > 0$ on $d$-regular graphs) remain strictly positive.

**Conventions.** Norms are denoted $\lVert \cdot \rVert$ with appropriate subscripts ($\lVert\cdot\rVert_1$ for trace norm on trace-class operators or $\ell^1$ norm on cochains, $\lVert\cdot\rVert_\infty$ for operator/supremum norm, and $\lVert\cdot\rVert_2$ or $\lVert\cdot\rVert_{\mathrm{HS}}$ for Euclidean/Hilbert--Schmidt norm); scalar absolute values are denoted $|\cdot|$.

### Notation

| Symbol | Meaning |
|---|---|
| $X$ | ambient trace-class or Banach state space of Hermitian operators |
| $\mathcal{M}$ | declared smooth product family; for density states, its positive subset has rank boundaries |
| $\Pi$ | $C^2$ product-state retraction |
| $T_t$ | ambient unitary or Lindblad dynamics semigroup |
| $S_t$ | projected dynamics family $\Pi T_t\rvert_{\mathcal{M}}$ |
| $\bar B(m)$ | projected tangent vector field $D\Pi(m)Am$ |
| $D_e(t)$ | two-site trace-norm correlation defect $\lVert\rho_e(t)-\rho_a(t)\otimes\rho_b(t)\rVert_1$ |
| $\widehat D_e(t)$ | dimension-normalized defect $D_e(t)/d^2$ (for equal endpoint dimensions $d$) |
| $C(t)$ | edgewise correlation defect sum $\sum_{e\in E}D_e(t)$ |
| $P_e, Q_e$ | tangent and normal projectors at a product state ($Q_e = I-P_e$) |
| $n_e$ | initial normal velocity residual $Q_e\dot\rho_e(0)$ |
| $\nu_e$ | local normal leakage rate $\lVert n_e\rVert_1$ |
| $\gamma_e$ | dimension-normalized rate $\nu_e/d^2$ (for equal endpoint dimensions $d$) |
| $g$ | full local incident interaction norm $\max_{v\in V}\sum_{X\ni v}\lVert h_X\rVert_\infty$ |

### 1.1 Related Work and Positioning

This paper connects to six main lines of research:

1. **Mean-field, Hartree--Fock, and product-state variational methods.** Product-state ansätze make many-body quantum evolution computationally tractable by restricting states to $\mathcal{M}$. Rather than proposing a new variational ansatz, we quantify the normal leakage rate $\nu_e$, the short-time trace-norm defect $D_e(t)$, and cohomological diagnostics obtained through separately declared observation adapters and cycle repairs.
2. **Time-dependent variational principle (TDVP) and projected dynamics.** TDVP projects the Schrödinger or Lindblad vector field onto the tangent bundle $T\mathcal{M}$ of a variational manifold (Haegeman et al. [14]). While global and local error bounds for variational quantum dynamics via standard Duhamel variation of constants are studied in Martinazzo and Burghardt [10] and Zoufal, Sutter, and Woerner [11], our focus in §5.10.2 is the exact local decomposition of the generator residual into partial-trace-annihilating edge normal operators ($\operatorname{Tr}_u n_e = \operatorname{Tr}_w n_e = 0$) and their coupling with incident Lieb--Robinson spatial suppression weights.
3. **Projection-operator (Nakajima--Zwanzig) methods.** Classical projection-operator formalisms eliminate unresolved degrees of freedom at the cost of a non-Markovian memory kernel. Our short-time bounds in §5 analyze the instantaneous normal velocity $n_e=(I-P_e)\dot\rho_e(0)$ and the moving retraction residual $F_e(t)=\rho_e(t)-\rho_a(t)\otimes\rho_b(t)$, while §2.2 explains why the projected family $S_t=\Pi T_t|_{\mathcal{M}}$ need not be a semigroup. An exact memory-kernel closure is not derived here.
4. **Lieb--Robinson locality bounds.** Whereas Lieb--Robinson bounds [1, 3, 4, 9, 25] control spatial light-cone propagation across lattice distance, our short-time lower bounds (Theorems 5.1 and 5.5) and infinite-volume dynamical limits (Theorem 5.7) rely on direct finite-support commutator combinatorics without causal-cone truncation. When bounding errors of spatially localized observables along a TDVP trajectory, Theorem 5.10.A incorporates Lieb--Robinson light-cone weights $w_{O,e}(\tau)$ to exponentially suppress distant edge leakage.
5. **Presheaf and cohomological obstructions in quantum information.** Sheaf-theoretic and cohomological methods have been widely used to study contextuality and local-to-global consistency. Here we work with observer visibility kernels (§7.4), and an explicit 1D cycle cochain adapter (§7.8) that detects graph-state multipartite correlations invisible to all two-site marginals.
6. **Entanglement timescales and correlation distance.** The pure-state normal rate identity $\nu_e=2\lVert\chi\rVert$ in §5.3.1 connects directly to the correlated uncertainty governing Yang's entanglement timescale [15] and Cresswell's Rényi-entropy rate [16], while $D_e=\lVert\rho_e-\rho_a\otimes\rho_b\rVert_1$ is Hall's trace-norm correlation distance [13], whose relationship to minimum product distance [17] is quantified in §5.11.

### 1.2 Research Series and Sibling Packages

To keep the present paper focused on quantum lattice dynamics, local correlation bounds, and physical visibility gaps, specialized and background developments are coordinated with companion packages in the `002_projection_obstruction` series and `coda_atlas`:

| Sibling Paper / Package | Formal Title & Version / Commit | Source | Key Anchors | Results used & Scope |
|---|---|---|---|---|
| **PO-001** | *From Covering-Edge Descent Complexes to Functorial Presheaves and Coherence Defects* (v2.0.0) | `002_projection_obstruction/001_from_covering_edge_descent...` | Theorem 2.1, §3 | Saturated-chain presheaves, degree-2 composition curvature cochains $K_{c,b,a}$, and operator cocycle coboundaries. |
| **PO-006 (GS-003)** | *Vector and Quantum Observer Geometries: Gauge Relativity and Trace Metric Bounds* (v0.4.0) | `002_projection_obstruction/006_vector_and_quantum_observer_geometries` | §§2–4 | Non-scalar observer geometries, Schatten-norm operator bounds, dual witness certificates, and phase metrics. |
| **PO-007 (GS-001)** | *M-Compatible Gauge Classification for Banach Presheaf Coboundaries: The $\ell^1$ Maximal-Symmetry Endpoint* (v4.7.0) | `002_projection_obstruction/007_m_compatible_gauge_classification` | Theorem 2.2, §3 | $M$-compatible gauge classification for Banach presheaves; maximal linear symmetry selecting weighted $\ell^1$. |
| **PO-008 (GS-002)** | *SO(k)-Invariant Gauge Rigidity for Declared Euclidean Stalks: Local $\ell^2$ Selection and Outer $\ell^1$ Aggregation* (v2.0.0) | `002_projection_obstruction/008_so_k_invariant_gauge_classification` | Theorem 1.1, §§2–3 | $SO(k)$-invariant gauge rigidity on Euclidean stalks; local $\ell^2$ selection with outer $\ell^1$ aggregation. |
| **PO-009 (GS-000)** | *Coordinate-Wise Additivity and Local $\ell^1$ Gauge Selection* (v6.1.1) | `002_projection_obstruction/009_coordinate_wise_additivity` | Theorems 1–3, §2 | Coordinate-wise additivity and local $\ell^1$ gauge selection on finite graph cochains. |
| **PO-033** | *Certified Adaptive Quantum Dynamics from Projection Residuals* (v1.0.1) | `002_projection_obstruction/033_certified_adaptive_quantum_dynamics` | §3, §4, Claims PO033-C1–C6 | Conditional analytic bounds and uncertified adaptive cluster prototype (`HEURISTIC_UNCERTIFIED`); Lean scope is conditional finite-sum inequalities over an abstract carrier (`Nat`/`Int`). Validated continuous-time ODE integration and conservative quadrature remain open work. |
| **PO-034** | *Higher-Cell Product Retractions, Simplicial Cochains, and Finite Retraction Dynamics* (v0.1.0) | `002_projection_obstruction/034_higher_cell_cochain_projection...` | §2, §3, Theorems 4.1–4.3 | Higher-cell product retractions, oblique projectors, simplicial cochain dynamics, and finite-dilation Taylor estimates. |
| **PO-035** | *Zero-Container Relational Spacetime, Emergent Lorentz Causality, and Witness Holonomy* (v0.1.0) | `002_projection_obstruction/035_zero_container_relational_spacetime...` | §§2–7, Claims RC-01–RC-10 | Defect 4-current conservation ($\partial_\mu J^\mu=0$), discrete relational spacetime, and witness holonomy. |
| **Finite QM** | *Finite Quantum Mechanics: Operational Jordan--Lie Foundations, Canonical Traces, and Central Purification* (v0.55.0) | `F004_papers/006_finite_qm` | §§13.5–13.8, Claim FQM-13.8 | Operational Jordan--Lie foundations, character cancellation on the sign cube, positive Bell cone extensions, and central-sector purification obstructions (former Appendix E). |
| *Archived Monograph Material* | *Projection Obstruction for Factorized States* (pre-streamlining monograph) | Commits `90e6231546` / `d44f760555`; code: `code/retraction_geometry.py` | Former §§3.4–3.14, Appendix D | Banach graph charts, shear retractions, parameter-chart transitions, bounded-left-inverse failure lemmas, and conditional extension reductions (omitted from the 69-page edition). |

Every theorem in §§5--7 of the present paper is self-contained under its declared Hilbert-space and interaction-graph premises.

### 1.3 Conceptual Pipeline

The progression from full many-body dynamics to local and cohomological diagnostics follows six explicit steps:

1. **Ambient state space** $X$: the affine space $\mathcal{A}_1$ of trace-one Hermitian operators, with parallel subspace of Hermitian trace-zero variations $\mathcal{A}_0$.
2. **Smooth product extension** $\mathcal{M}\subset X$: selected via a $C^2$ retraction $\Pi$ on a stated neighborhood. Positivity and boundary feasibility are additional constraints, not consequences of smoothness.
3. **Projected dynamics and normal residual:** tangent projection $\bar B(m)=D\Pi(m)Am$, projected family $S_t=\Pi\circ T_t|_{\mathcal{M}}$, and normal velocity $(I-D\Pi(m))Am$.
4. **Induced 1-cochains:**
   - *Rate diagnostic:* instantaneous local leakage $\omega_e^{\mathrm{rate}} = q_e(n_e) \in V_e$ induced by linear observation maps $q_e$ on normal velocity $n_e$. For identity observation maps, this yields the normal leakage rate $\nu_e = \lVert n_e\rVert_1$.
   - *State diagnostic:* finite-time correlation defect $\omega_e^{\mathrm{state}}(t) = \rho_e(t) - \rho_a(t)\otimes\rho_b(t)$, whose trace-norm magnitude is $D_e(t) = \lVert\omega_e^{\mathrm{state}}(t)\rVert_1$.
5. **Quotient obstruction vs. coboundary:** given a coboundary differential $d_0:C^0\to C^1$, the repair-minimized quotient seminorm $\Phi([\omega])=\inf_{\alpha\in C^0}\lVert\omega-d_0\alpha\rVert_1$ vanishes if and only if $\omega=d_0\alpha$ is exact (in finite dimensions).
6. **Global edge aggregation and short-time connection:** under replica additivity (RE3) and singleton calibration (RE5), local edge diagnostics aggregate via unweighted $\ell^1$ summation:
   - the total instantaneous rate tally is $\sum_{e\in E} \nu_e$;
   - the total finite-time state correlation defect is $C(t) = \sum_{e\in E} D_e(t)$;
   these two diagnostics are physically distinct and connected by the short-time expansion of Theorem 5.5: $|D_e(t) - t\nu_e| \le 24 g^2 t^2$.

---

## 2. Structural Framework

We consider quantum spin lattices and general Banach state spaces under nonlinear factorization retractions.

### 2.1 State Space and Product Retraction

Let $X$ denote the real Banach space of Hermitian trace-class operators on a composite Hilbert space $\mathcal{H}_V = \bigotimes_{v\in V}\mathcal{H}_v$ equipped with the trace norm $\lVert\cdot\rVert_1$. Let $\mathcal{A}_1 = \{\rho \in X : \operatorname{Tr}\rho = 1\}$ denote the affine hyperplane of trace-one Hermitian operators, with parallel subspace of trace-zero Hermitian variations $\mathcal{A}_0 = \{\Delta \in X : \operatorname{Tr}\Delta = 0\}$. The convex physical state space is $\mathcal{S}(\mathcal{H}_V) = \{\rho \in \mathcal{A}_1 : \rho \ge 0\}$.

The **physical product state manifold** $\mathcal{M} = \{\bigotimes_{v\in V}\rho_v : \rho_v \in \mathcal{S}(\mathcal{H}_v)\}$ forms a smooth submanifold on the interior of the state space (where states have full local rank), with rank boundaries on singular strata (§§5.10.2 and 5.11.1), embedded in the smooth affine product variety $\mathcal{M}_{\mathrm{aff}} = \{\bigotimes_{v\in V}\sigma_v : \sigma_v \in \mathcal{A}_1(\mathcal{H}_v)\}$. On physical density states, the canonical **product retraction**
$$
\Pi: \mathcal{S}(\mathcal{H}_V) \longrightarrow \mathcal{M}, \qquad \Pi(\rho) = \bigotimes_{v\in V}\operatorname{Tr}_{V\setminus\{v\}}(\rho),
$$
restricts to a well-defined projection onto $\mathcal{M}$. More generally, $\Pi$ admits a smooth $C^\infty$ extension $\Pi: \mathcal{A}_1 \to \mathcal{M}_{\mathrm{aff}}$ on the trace-one Hermitian affine slice, with tangent derivatives $D\Pi(\rho): \mathcal{A}_0 \to T_{\Pi(\rho)}\mathcal{M}_{\mathrm{aff}}$ acting on trace-zero variations. On each two-site subsystem $e=\{u,w\}$, the local marginal product retraction $\Pi_e(\rho_{uw}) = \rho_u \otimes \rho_w$ induces an instantaneous tangent projector $P_e = D\Pi_e(m)$ at any product state $m=\rho_u\otimes\rho_w$, and a complementary **normal projector**
$$
Q_e = I - P_e.
$$
For general covering-edge Banach diagrams and saturated-chain descent complexes over abstract posets (Mac Lane [2]), we refer to companion package **PO-001** (*From Covering-Edge Descent Complexes to Functorial Presheaves and Coherence Defects*).

### 2.2 Linear Semigroups and Projected Dynamics Families

Let $\{T_t\}_{t \ge 0}$ be a $C_0$ contraction semigroup on $X$ with generator $(A, \mathcal{D}(A))$ (for closed quantum systems, $A\rho = -i[H,\rho]$; for open Markovian systems, $A$ is a Lindbladian generator). Whenever $\{T_t\}$ does not leave $\mathcal{M}$ invariant, the **projected dynamics family**
$$
S_t = \Pi \circ T_t\rvert_{\mathcal{M}}
$$
maps $\mathcal{M} \to \mathcal{M}$ locally for small $t\ge 0$, but need not satisfy the semigroup law:
$$
S_{t+s}=\Pi T_{t+s}|_{\mathcal{M}}
\quad\text{need not equal}\quad
S_tS_s=\Pi T_t\Pi T_s|_{\mathcal{M}}.
$$

---

## 3. Affine-Chart Criterion for Projected Vector Fields

### 3.1 Statement and Decomposition

**Theorem 3.1 (Affine Chart Criterion).** Let $X$ be a Banach space, $\{T_t\}$ a $C_0$ contraction semigroup with generator $(A,\mathcal D(A))$, and $\Pi:W\to M\subset X$ a $C^2$ retraction onto a $C^2$ submanifold $M$. Assume either that $A$ is bounded on $X$, or that $M$ is a $C^2$ submanifold of the graph-norm domain of $A$ such that $m\mapsto Am$ is $C^1$ along $M$. Let $\phi:U\subset M\to Y$ be a chart in a flat affine atlas on $M$, and define the coordinate vector field
$$
b(y)=D\phi_{\phi^{-1}(y)}\left[D\Pi_{\phi^{-1}(y)}A\phi^{-1}(y)\right].
$$
If $y\mapsto Db(y)$ is nonconstant on a connected chart domain $\phi(U)$, then $b$ is not affine-linear in that chart. Consequently, the projected dynamics family $S_t=\Pi\circ T_t|_M$ cannot have $b$ as an exact affine-linear semigroup generator in the chart $\phi$. (This is a coordinate statement in the chosen affine chart and does not rule out nonlinear $C^2$ coordinate conjugacies.)

Theorem 3.1 rests on two elementary observations:

**Lemma 3.A (Affine Criterion).** In any flat affine coordinate chart, an affine-linear vector field $b(y)=Ly+c$ has a constant Fréchet derivative $y\mapsto Db(y)=L$. Therefore, if $y\mapsto Db(y)$ is nonconstant, $b$ is not affine-linear in those coordinates.

**Proposition 3.B (Non-Invariance versus Projected Motion).** For an orbit point $T_tm\in W\setminus M$, the retraction $\Pi$ changes that point because its image lies in $M$. This does not imply that the projected map $S_t=\Pi\circ T_t|_M$, wherever defined, moves its initial point: nontrivial projected motion requires an explicit pair $(m,t)$ with $T_tm\in W$ and $\Pi(T_tm)\ne m$.

### 3.2 Parallel Tensor Fields on Flat Affine Manifolds

**Lemma 3.2 (Parallel fields on flat affine connections).** Let $(M, \nabla)$ be a connected Banach manifold equipped with a torsion-free flat affine connection. If a $(1,1)$-tensor field $S$ on $M$ satisfies $\nabla S = 0$, then $S$ has constant operator components in every connected affine coordinate chart.

*Proof.* In an affine coordinate chart where Christoffel symbols vanish, $\nabla S = 0$ reduces to $\partial_v S = 0$ in all coordinate directions, so $S$ is locally constant and hence constant on any connected chart domain. Affine transition maps preserve constancy across the affine atlas. $\square$

### 3.3 Proof of Theorem 3.1 and the Ambient-to-Chart Bridge

*Proof of Theorem 3.1.* In an affine chart, any affine-linear vector field has the form $b(y)=Ly+c$ with constant derivative $Db(y)=L$; nonconstancy of $y\mapsto Db(y)$ immediately rules out this form. $\square$

**Lemma 3.3 (tangent-restricted affine-subspace transfer).** Let $L\subset X$ be a closed affine subspace with direction space $L_0$, and let $M\subset L$ be relatively open, so $T_mM=L_0$ for every $m\in M$. Let $\Pi:W\to M$ be a $C^2$ retraction and let $A$ satisfy the bounded-generator or graph-norm hypothesis of Theorem 3.1, so that $\bar B(m)=D\Pi(m)Am$ is $C^1$ on $M$. Let $\tilde\phi:L\to Y$ be a continuous affine isomorphism, set $\phi=\tilde\phi|_M$, and write $S=(D\tilde\phi)^{-1}:Y\to L_0$. Then, under the identification $T_mM=L_0$,
$$
Db(y) = D\tilde\phi \circ D_M\bar B(\phi^{-1}(y)) \circ S.
$$
Consequently, on this chart, $y\mapsto Db(y)$ is nonconstant if and only if $m\mapsto D_M\bar B(m)$ is nonconstant.

*Proof.* Because $\tilde\phi$ is affine, $D\phi_m=D\tilde\phi:L_0\to Y$ is independent of $m\in M$, so $b(y)=D\tilde\phi(\bar B(\phi^{-1}(y)))$ and the chain rule gives $Db(y)[\xi]=D\tilde\phi(D_M\bar B(m)[S\xi])$ for $m=\phi^{-1}(y)$. $\square$

**Example 3.3 (Projection curvature inducing chart nonlinearity on a flat subspace).** On $X=\mathbb R^2$, $M=\mathbb R\times\{0\}$, $\Pi(x,y)=(x(1+y),0)$, and $A(x,y)=(-x,x-y)$ (a contraction generator on Euclidean $\mathbb R^2$), direct calculation gives $\bar B(x,0)=(x^2-x,0)$, so $b(x)=x^2-x$ and $Db(x)=2x-1$ ($Db(0)=-1\ne Db(1)=1$), where nonlinearity arises directly from the projection-curvature term $D^2\Pi(m)(Am,(1,0))=(x,0)$.

**Proposition 3.C (Ambient nonconstancy without flat hypotheses).** Ambient nonconstancy of $D_X\bar B(m)$ and a nonzero projection-curvature term $D^2\Pi(m)(Am,\cdot)$ do not by themselves force $y\mapsto Db(y)$ to be nonconstant on a curved submanifold $M$.

*Proof.* On Euclidean $X=\mathbb R^2$, take the parabola $M=\{(s,s^2):s\in\mathbb R\}$, vertical retraction $\Pi(x,y)=(x,x^2)$, contraction generator $A(x,y)=(-x,0)$, and global chart $\phi(s,s^2)=s$. Then $\bar B(s,s^2)=(-s)(1,2s)$, so $b(s)=-s$ and $Db(s)=-1$ (constant), even though $D_X\bar B$ and the contracted projection-curvature term $D^2\Pi_m[Am, h] = (0, -2s h_x)$ for $m=(s,s^2)$ and $h=(h_x, 2s h_x)$ are nonconstant along $M$. (Note that while the uncontracted second Fréchet derivative $D^2\Pi_{(x,y)}[h,k] = (0, 2h_x k_x)$ is constant on $\mathbb R^2$, its contraction with the generator field $Am=(-s,0)$ depends nontrivially on the base point $m$.) $\square$

*Omitted chart hierarchy and archived results.* The detailed hierarchy of chart-derivative formulas for vertical, sheared, and fiber-nonlinear graph submanifolds over Banach splittings, along with bounded left-inverse failure criteria (former Lemmas 3.4–3.14 in the pre-streamlining monograph), is omitted from this 69-page edition. Readers seeking those full functional-analytic proofs are referred to the archived reviewed monograph revision `90e6231546` (and `d44f760555`), with exact symbolic verification fixtures preserved in `code/retraction_geometry.py`. Sibling package **PO-034** develops higher-cell product retractions and simplicial dynamics, while **PO-001** and **PO-006** develop covering-edge descent complexes and non-scalar observer geometries respectively (see the authoritative sibling reference table in §1.2).

### 3.4 Residual Taxonomy and Retraction Geometry

Throughout the paper we distinguish three residual objects associated with $(X, \mathcal{M}, \Pi, T_t)$:

1. **Instantaneous normal leakage:**
   $$\Delta_\Pi(m) = (I - D\Pi_m)Am,$$
   which is the first-order normal velocity vector leaving the tangent space $T_m \mathcal{M}$.

2. **Finite-time retraction residual:**
   - Under $C^1$ orbit differentiability:
     $$R(t, m) = T_t m - \Pi(T_t m) = t(I - D\Pi_m)Am + o(t).$$
   - For bounded generators $A$ and smooth retractions $\Pi \in C^3(\mathcal{A}_1)$ (as in finite-dimensional quantum spin lattices):
     $$R(t, m) = t(I - D\Pi_m)Am + \frac{t^2}{2}\left(A^2 m - D\Pi_mA^2 m - D^2\Pi_m(Am, Am)\right) + \mathcal{O}(t^3).$$

3. **Projected-family semigroup defect:**
   $$S_{t+s}(m) - S_t(S_s(m)),$$
   which measures the failure of the projected family $S_t = \Pi \circ T_t|_{\mathcal{M}}$ to form an exact semigroup on $\mathcal{M}$ (delegated to companion study **PO-034**).

The short-time quantum correlation bounds of §5 analyze objects 1 and 2 directly on each two-site subsystem.

---

## 4. Conditional Additive $\ell^1$ Diagnostic

Theorem 3.1 supplies a chart-level affine-nonlinearity criterion for a declared coordinate vector field. The next question is how to measure projection residuals once a diagnostic has been declared. Theorem 4.2 establishes that, given RE1--RE5, the $\ell^1$ norm is the selected diagnostic. The conclusion is conditional on these axioms; relaxing them admits other norms.

### 4.1 Primitive Axioms for Replica-Extensive Diagnostics

Let $E$ be a finite edge set. For each $e\in E$, let $V_e$ be a finite-dimensional vector space equipped with a faithful local gauge
$$ j_e:V_e\to \mathbb R_{\ge 0}. $$

A diagnostic is a family
$$ J_E:\prod_{e\in E}V_e\to \mathbb R_{\ge 0}. $$

We do **not** assume an additive form.

#### Axiom RE1 — Global gauge

Each $J_E$ is a faithful convex gauge:
$$ J_E(x)=0\iff x=0, $$
$$ J_E(\lambda x)=\lambda J_E(x),\qquad \lambda\ge0, $$
$$ J_E(x+y)\le J_E(x)+J_E(y). $$

#### Axiom RE2 — Local magnitude sufficiency

There exists a function
$$ A_E:\mathbb R_{\ge0}^E\to\mathbb R_{\ge0} $$
such that
$$ J_E(x)=A_E\bigl((j_e(x_e))_{e\in E}\bigr). $$
Thus the observer sees only independent local magnitudes, not directions or cross-edge phases.

#### Axiom RE3 — Disjoint replica additivity

For disjoint finite edge sets $E,F$:
$$ J_{E\sqcup F}(x\sqcup y)=J_E(x)+J_F(y). $$
Equivalently,
$$ A_{E\sqcup F}(u\sqcup v)=A_E(u)+A_F(v). $$

#### Axiom RE4 — Edge-exchange symmetry

If $\sigma:E\to F$ is a bijection preserving local gauge type, and for each $e\in E$ a gauge-preserving fiber identification map $\tau_e:V_e\to V_{\sigma(e)}$ is declared, then for $x=(x_e)_{e\in E}$ and $(\sigma x)_{\sigma(e)} = \tau_e(x_e)$:
$$ J_F(\sigma x)=J_E(x). $$

#### Axiom RE5 — One-edge normalization

For every singleton $E=\{e\}$:
$$ J_{\{e\}}(x_e)=j_e(x_e). $$

---

### 4.2 Replica-Extensivity Hierarchy

**Theorem 4.2 (Measurement Hierarchy and Observer Selection).** Let $E$ be finite and let the diagnostic family $J_E$ be defined on every finite disjoint union of labelled edge types across the observer class.

1. **RE3 alone gives singleton separability:**
   $$
   J_E(x)=\sum_{e\in E}J_{\{e\}}(x_e).
   $$
2. **RE1+RE2+RE3 give weighted $\ell^1$ relative to the declared local gauges:** if each $V_e\ne0$, then
   $$
   J_E(x)=\sum_{e\in E}c_ej_e(x_e),\qquad c_e>0.
   $$
3. **RE4 controls symmetry:** $c_e$ is constant on every declared edge-type orbit.
4. **RE3+RE5 give the edgewise sum of declared local gauges:**
   $$
   J_E(x)=\sum_{e\in E}j_e(x_e).
   $$
   RE1, RE2, and RE4 are unnecessary for this last implication.

*Observer Selection Framing.* RE3 supplies separability across disjoint replicas, while RE5 calibrates singleton terms; together, RE3+RE5 force the edgewise sum of the declared singleton gauges $j_e(x_e)$. The theorem identifies the exact observer axioms under which an $\ell^1$ edge tally is selected, rather than deriving a fiber norm from graph topology alone. In Lean 4, item 4 is mechanized as `ReplicaHierarchy.unweighted_sum_of_replicaAdditive_of_singleton_calibration` in `lean4/po000_l001_replica_hierarchy.lean`, and the singleton algebraic cores of items 2 and 3 are mechanized in `lean4/po000_l005_weighted_hierarchy.lean` (`PO000.WeightedHierarchy.singleton_aggregator_linear`, `singleton_weight_pos`, and `orbit_weights_equal`).

*Proof.* Because
$$
E=\bigsqcup_{e\in E}\{e\},
$$
finite induction using RE3 gives
$$
J_E(x)=\sum_{e\in E}J_{\{e\}}(x_e),
$$
establishing item 1.

Assume RE1 and RE2 as well. On a singleton, write
$$
J_{\{e\}}(x)=A_{\{e\}}(j_e(x)).
$$
The local gauge has full nonnegative range: choose $v\ne0$; faithfulness gives $j_e(v)>0$, and positive homogeneity gives
$$
j_e\!\left(\frac{u}{j_e(v)}v\right)=u
\qquad (u\ge0).
$$
Positive homogeneity of the singleton diagnostic from RE1 therefore forces
$$
A_{\{e\}}(u)=c_eu,
\qquad
c_e=A_{\{e\}}(1).
$$
Faithfulness gives $c_e>0$. Substitution into the RE3 decomposition establishes item 2. RE4 identifies coefficients on declared type-preserving edge orbits, establishing item 3.

Finally, under RE5,
$$
J_{\{e\}}(x_e)=j_e(x_e).
$$
Substitution into the RE3 decomposition establishes item 4 directly. No transitivity assumption is needed. $\square$

A direct logical consequence is that RE3+RE5 also imply RE1, RE2, and RE4 whenever the $j_e$ are faithful convex gauges and RE4 ranges over bijections preserving local gauge type.

---

### 4.3 Coboundary and Induced-Cochain Specializations

For a covering-edge Banach diagram over a poset (formalized in §7.3.3; see also companion package **PO-001**), the edge data
$$
\delta_e(s)=r_{b,a}s(b)-s(a)
$$
are a coboundary by construction: $\delta=d_0s$. With $j_e(v)=\lVert v\rVert_{F(a)}$, Theorem 4.2 gives
$$
J_P(s)=\sum_{e\in E_{\mathrm{cov}}}\lVert\delta_e(s)\rVert_{F(a)}
$$
under RE3+RE5, or a weighted sum under RE1+RE2+RE3.

The physical projection residual in §5 is a distinct object. If bounded linear observation maps
$$
\mathcal O_{e,m}:\ker D\Pi_m\longrightarrow V_e
$$
map the normal leakage
$$
\mathcal N_\Pi(m)=(I-D\Pi_m)Am
$$
to
$$
\omega_e(m)=\mathcal O_{e,m}(\mathcal N_\Pi(m)),
$$
then $\omega(m)\in\prod_eV_e$ is an induced 1-cochain relative to the chosen observation family. It becomes a coboundary only when a 0-cochain space $C^0$, a differential $d_0:C^0\to C^1$, and a section $s\in C^0$ with $\omega=d_0s$ are supplied.

### 4.3.1 Exact Dependencies in the Implication Lattice

The implication lattice of Theorem 4.2 is:
$$
\boxed{\mathrm{RE3}\Rightarrow\text{singleton separability}},
\qquad
\boxed{\mathrm{RE1+RE2+RE3}\Rightarrow\text{weighted }\ell^1},
$$
$$
\boxed{\mathrm{RE1+RE2+RE3+RE4}\Rightarrow
\text{orbit-constant weights}},
\qquad
\boxed{\mathrm{RE3+RE5}\Rightarrow\text{unweighted }\ell^1}.
$$

The first and fourth implications are finite disjoint-union identities. The weighted implication uses only the singleton clauses of RE1 and RE2: singleton homogeneity, singleton faithfulness, and dependence on the local gauge magnitude. In `lean4/po000_l005_weighted_hierarchy.lean`, `PO000.WeightedHierarchy.singleton_aggregator_linear` derives $A_{\{e\}}(u)=A_{\{e\}}(1)\,u$ from homogeneity, magnitude sufficiency, and full nonnegative range; `singleton_weight_pos` derives $c_e>0$ from faithfulness; and `orbit_weights_equal` derives orbit weight equality under gauge-preserving fiber bijections. Companion works [5,8] study broader gauge classifications under transformation-monoid and coordinate-additivity hypotheses.

Note that Theorem 4.2 characterizes the raw edge tally $I$ on a declared 1-cochain, which is distinct from the quotient obstruction seminorm $\Phi([\omega])=\inf_{\alpha\in C^0}\lVert\omega-d_0\alpha\rVert_1$: a positive raw tally $I>0$ does not imply $\Phi>0$, and $\Phi=0$ does not imply $I=0$.

### 4.3.2 Quantum Partial-Trace Poset and Two-Site Correlation Cochains

**Theorem 4.3.A (Quantum Partial-Trace Poset and Correlation Defect Representation).** Let $V$ be a finite set of quantum sites with local Hilbert spaces $\mathcal{H}_v$ ($v\in V$), and let $\mathcal{P} = (\mathcal{P}(V), \subseteq)$ be the finite poset of site subsets ordered by inclusion.
For each subset $A \subseteq V$, let $\mathcal{H}_A = \bigotimes_{v\in A} \mathcal{H}_v$ and let $\mathcal{F}(A) = \mathfrak{T}_1(\mathcal{H}_A)$ be the real Banach space of Hermitian trace-class operators on $\mathcal{H}_A$ equipped with the trace norm $\lVert\cdot\rVert_1$.
For every inclusion $A \subseteq B$, define the restriction map $r_{B,A}: \mathcal{F}(B) \to \mathcal{F}(A)$ by the partial trace:
$$
r_{B,A}(\sigma_B) = \operatorname{Tr}_{B\setminus A}(\sigma_B).
$$
Then:
1. *Banach Diagram Functoriality:* For any chain $A \subseteq B \subseteq C$, $r_{B,A} \circ r_{C,B} = r_{C,A}$ and $r_{A,A} = \mathrm{id}_{\mathcal{F}(A)}$. Each restriction map $r_{B,A}$ is a positive, trace-preserving linear contraction with $\lVert r_{B,A}\rVert_{1\to 1} = 1$.
2. *Covering-Edge Poset Coboundary and Marginal Compatibility:* The covering relations in $\mathcal{P}$ are pairs $e = (A, A \cup \{v\})$ with $v \notin A$. For any 0-cochain $s \in C^0(\mathcal{P}; \mathcal{F}) = \prod_{A\subseteq V} \mathcal{F}(A)$, the coboundary operator $\delta = d_0 s \in C^1(E_{\mathrm{cov}}; \mathcal{F})$ evaluates along each covering edge $e = (A, B)$ to
$$
\delta_e(s) = r_{B,A}(s(B)) - s(A) = \operatorname{Tr}_{B\setminus A}(s(B)) - s(A).
$$
Consequently, a 0-cochain $s$ is closed ($d_0 s = 0$) if and only if the family $\{s(A)\}_{A\subseteq V}$ is a partial-trace-compatible marginal hierarchy ($\operatorname{Tr}_{B\setminus A}(s(B)) = s(A)$ for all $A \subseteq B$). In particular, for any global state $\rho_V \in \mathcal{S}(\mathcal{H}_V)$ with single-site marginals $\rho_v = \operatorname{Tr}_{V\setminus\{v\}}(\rho_V)$, both the true marginal section $s_{\mathrm{true}}(A) := \rho_A = \operatorname{Tr}_{V\setminus A}(\rho_V)$ and the factorized marginal section $s_{\mathrm{prod}}(A) := \bigotimes_{v\in A} \rho_v$ are individually closed 0-cochains ($d_0 s_{\mathrm{true}} = 0$ and $d_0 s_{\mathrm{prod}} = 0$).
3. *0-Cochain Difference and Two-Level Induced Defect Cochain:* Because both $s_{\mathrm{true}}$ and $s_{\mathrm{prod}}$ are closed under linear partial trace—and because on any singleton-to-pair covering edge $(\{u\},\{u,v\})$ one has $\operatorname{Tr}_v(\rho_{uv}) - \rho_u = 0$, while for $|V|\ge 3$ any subset $X$ with $2\le |X| < |V|$ serves simultaneously as an upper vertex of $(X\setminus\{x\}, X)$ and a lower vertex of $(X, X\cup\{y\})$—the subset correlation defect
$$
D_A(\rho_V) := \left\lVert \rho_A - \bigotimes_{v\in A}\rho_v\right\rVert_1 = \bigl\lVert (s_{\mathrm{true}} - s_{\mathrm{prod}})(A)\bigr\rVert_1
$$
is the fiber norm at $A$ of the **0-cochain difference** $s_{\mathrm{true}} - s_{\mathrm{prod}} \in \ker d_0$ rather than the linear partial-trace coboundary of a single section on $\mathcal{P}(V)$. Restricted to the two-site edge family $E \subseteq \binom{V}{2}$, the nonlinear product-retraction residual $\omega_e(\rho_V) := (I - \Pi_e)(\rho_e) = \rho_e - \rho_u\otimes\rho_v = (s_{\mathrm{true}} - s_{\mathrm{prod}})(e)$ defines an induced 1-cochain $\omega(\rho_V) \in \prod_{e\in E}\mathcal{F}(e)$ whose RE3+RE5 $\ell^1$ evaluation is the edgewise correlation tally:
$$
J_E\bigl(\omega(\rho_V)\bigr) = \sum_{e=\{u,v\}\in E} \lVert \omega_e(\rho_V)\rVert_1 = \sum_{e=\{u,v\}\in E} \lVert \rho_{uv} - \rho_u\otimes\rho_v\rVert_1 = \sum_{e\in E} D_e(\rho_V).
$$

*Proof.* For item 1, Fubini's theorem for partial traces on $\mathcal{H}_C = \mathcal{H}_A \otimes \mathcal{H}_{B\setminus A} \otimes \mathcal{H}_{C\setminus B}$ gives $\operatorname{Tr}_{B\setminus A}(\operatorname{Tr}_{C\setminus B}(\sigma_C)) = \operatorname{Tr}_{C\setminus A}(\sigma_C)$, and trace-norm contractivity $\lVert\operatorname{Tr}_{B\setminus A}(\sigma_B)\rVert_1 \le \lVert\sigma_B\rVert_1$ holds with equality on positive states ($\lVert r_{B,A}\rVert_{1\to 1}=1$). For item 2, $d_0 s = 0$ means $\operatorname{Tr}_{B\setminus A}(s(B)) = s(A)$ on every covering pair $B = A\cup\{v\}$, which by induction along inclusion chains holds if and only if $\operatorname{Tr}_{B\setminus A}(s(B)) = s(A)$ for all $A\subseteq B$; both $s_{\mathrm{true}}(A)=\operatorname{Tr}_{V\setminus A}(\rho_V)$ and $s_{\mathrm{prod}}(A)=\bigotimes_{v\in A}\rho_v$ satisfy this identity since $\operatorname{Tr}_v(\rho_v)=1$. Item 3 follows immediately by evaluating $(s_{\mathrm{true}} - s_{\mathrm{prod}})(A) = \rho_A - \bigotimes_{v\in A}\rho_v$ and applying Theorem 4.2(4) to $\omega_e(\rho_V) = \rho_e - \rho_u\otimes\rho_v$ with local gauge $j_e = \lVert\cdot\rVert_1$. $\square$

---

**Classical control.** For
$$
\rho_{uv}=\tfrac12|00\rangle\langle00|+\tfrac12|11\rangle\langle11|,
\qquad \rho_u=\rho_v=I_2/2,
$$
both sections above are closed, while $D_{\{u,v\}}=1$: the difference
from $I_4/4$ is diagonal with entries $(1,-1,-1,1)/4$. This separable
state distinguishes marginal consistency from product independence.
Bell extension imposes a further requirement across measurement contexts
(§7.10); neither this positive product defect nor a closed marginal
section settles it.

### 4.4 Scope of the Characterization and Related Frameworks

Theorem 4.2 does not assert that every useful diagnostic on a graph must be an $\ell^1$ sum, nor that the trace norm is uniquely selected by completely positive trace-preserving (CPTP) monotonicity alone. Rather, it shows that finite replica additivity (RE3) decomposes a global diagnostic into singleton contributions, and singleton calibration (RE5) identifies each singleton contribution with the chosen local gauge.

*Related framework connections.* The complete transformation-monoid gauge classification, the $SO(k)$-invariance rigidity on Euclidean stalks, and the one-axiom-drop independence countermodels (including `l2_combination_not_additive` and `doubled_sum_not_calibrated` in `lean4/po000_l005_weighted_hierarchy.lean`) are established in companion packages **PO-007** (`007_m_compatible_gauge_classification`), **PO-008** (`008_so_k_invariant_gauge_classification`), and **PO-009** (`009_coordinate_wise_additivity`). Linear measurement dimension counting on repair subspaces is established in the finite obstruction calculus of **PO-001**.

---

## 5. Exact Short-Time Density Production

### 5.1 Setup and Normalization

Let $\Lambda=(V,E)$ be a finite simple graph, and attach to each vertex $v\in V$ a finite-dimensional Hilbert space $\mathcal H_v$. On the tensor-product Hilbert space $\mathcal H_V = \bigotimes_{v\in V}\mathcal H_v$, let
$$
H=\sum_{1\le |X|\le2}h_X
$$
be a Hamiltonian with one- and two-site Hermitian interaction terms. Define the full local interaction norm
$$
g:=\max_{v\in V}\sum_{X\ni v}\lVert h_X\rVert_\infty.
$$
This quantity includes one-local fields. If every edge term and the single one-local term at each vertex have norm at most $J$ on a graph of maximum degree $\Delta$, then
$$
g\le(\Delta+1)J.
$$
For the transverse-field Ising chain,
$$
g\le2|J|+|h|.
$$
The first-order normal rate in §6.2 is independent of $h$, whereas the uniform second-order remainder and certified time window depend on $g$.

Let the initial state be a product state,
$$
\rho(0)=\bigotimes_{v\in V}\rho_v,
\qquad
\rho(t)=e^{-itH}\rho(0)e^{itH}.
$$
For $e=\{a,b\}$, write $\rho_e(t)$ for the exact two-site reduced state and $\rho_a(t),\rho_b(t)$ for its one-site marginals. The raw trace-norm defect and trace distance are defined for arbitrary endpoint dimensions, while the dimension-normalized score $\widehat D_e(t)$ is defined when both endpoints have local Hilbert dimension $d$:
$$
D_e(t):=\lVert\rho_e(t)-\rho_a(t)\otimes\rho_b(t)\rVert_1,
\qquad
T_e(t):=\frac12D_e(t),
\qquad
\widehat D_e(t):=\frac{1}{d^2}D_e(t).
$$
Here $D_e$ is the raw trace-norm correlation defect (cf. Hall [13]), $T_e$ is the trace distance, and $\widehat D_e$ is the dimension-normalized score. Throughout the theorems below we work with $D_e$.

At the product state $\rho_a\otimes\rho_b$, differentiating the product-of-marginals retraction $\Pi_e(\sigma_{ab})=\operatorname{Tr}_b(\sigma_{ab})\otimes\operatorname{Tr}_a(\sigma_{ab})$ on the trace-zero tangent space yields
$$
P_e Z
=
(\operatorname{Tr}_b Z)\otimes\rho_b
+
\rho_a\otimes(\operatorname{Tr}_a Z).
$$
Because $L_e = \dot\rho_e(0)$ has trace zero ($\operatorname{Tr} L_e = 0$), $P_e L_e$ is the product-tangent component. We write
$$
L_e:=\dot\rho_e(0),
\qquad
Q_e:=I-P_e,
\qquad
n_e:=Q_eL_e,
\qquad
\nu_e:=\lVert n_e\rVert_1,
\qquad
\gamma_e:=\frac{\nu_e}{d^2}.
$$
An edge is called *active* when $\nu_e>0$; this is strictly stronger than having a nonzero commutator $[h_e,\rho_a\otimes\rho_b]\neq 0$, because $Q_e = I - P_e$ projects out all local product-tangent motion.

### 5.2 Uniform Double-Commutator Bounds

**Lemma 5.2 (local derivative bounds).** If $A_S$ is supported on a site set $S$ with $\lVert A_S\rVert_\infty\le1$, then
$$
\lVert[H,[H,A_S]]\rVert_\infty
\le
\begin{cases}
8g^2,&|S|=1,\\
24g^2,&|S|=2.
\end{cases}
$$
For $|S|=1$, one also has $\lVert[H,A_S]\rVert_\infty\le2g$.

*Proof.* Only terms $h_X$ with $X\cap S\ne\varnothing$ contribute to the first commutator $[H,A_S]$, and their operator norms sum to at most $|S|g$. For each such $X$, the union $S\cup X$ has size at most $2$ when $|S|=1$ and at most $3$ when $|S|=2$. Only terms $h_Y$ meeting $S\cup X$ contribute to the outer commutator. Applying $\lVert[A,B]\rVert_\infty\le2\lVert A\rVert_\infty\lVert B\rVert_\infty$ twice yields $4(g)(2g)=8g^2$ for $|S|=1$ and $4(2g)(3g)=24g^2$ for $|S|=2$. $\square$

By trace-norm/operator-norm duality and unitary invariance, for all $t\in\mathbb R$,
$$
\lVert\ddot\rho_e(t)\rVert_1\le24g^2,
\qquad
\lVert\ddot\rho_a(t)\rVert_1,
\lVert\ddot\rho_b(t)\rVert_1\le8g^2,
\qquad
\lVert\dot\rho_a(t)\rVert_1,
\lVert\dot\rho_b(t)\rVert_1\le2g.
$$

### 5.3 One-Local and Incident Terms Are Tangent

**Lemma 5.3 (local normal-rate isolation).** For a product initial state $\rho(0)=\bigotimes_{v\in V}\rho_v$ and a one- and two-local Hamiltonian $H$, every term $h_X$ supported on at most one endpoint of $e=\{a,b\}$ contributes a purely product-tangent operator to $L_e = \dot\rho_e(0)$. Consequently, the normal rate $n_e = Q_e L_e$ receives contributions only from interaction terms $h_X$ whose support equals $\{a,b\}$.

*Proof.* A one-local term on $a$, or a two-local term on $\{a,c\}$ ($c\ne b$), contributes after tracing out $V\setminus\{a,b\}$ an operator of the form $M_a\otimes\rho_b$ with $\operatorname{Tr}M_a=0$, since $\operatorname{Tr}_c[h_{ac},\rho_a\otimes\rho_c] = [\operatorname{Tr}_c(h_{ac}(I_a\otimes\rho_c)),\rho_a]$ acts only on $a$ and has zero trace. The tangent projection $P_e$ fixes $M_a\otimes\rho_b$:
$$
P_e(M_a\otimes\rho_b)=(\operatorname{Tr}_b(M_a\otimes\rho_b))\otimes\rho_b + \rho_a\otimes(\operatorname{Tr}_a(M_a\otimes\rho_b)) = M_a\otimes\rho_b.
$$
By symmetry the same holds for terms meeting $e$ only at $b$, and terms disjoint from $e$ have zero partial trace over $V\setminus e$. Thus $Q_e = I - P_e$ annihilates all such contributions. $\square$

In particular, one-local field terms (such as transverse or longitudinal fields in Ising models) never contribute to the first-order normal rate $n_e$, even when the initial single-site states are not field eigenstates; they enter the short-time bound only through the second-order remainder constant $g$.

### 5.3.1 Centered Interactions and the Pure-State Rate

Let $h_{ab}$ denote the sum of the terms supported on both endpoints.
Lemma 5.3 gives the explicit formula
$$
 n_e=-i(I-P_e)[h_{ab},\rho_a\otimes\rho_b].
$$
Choose a Hermitian product decomposition
$h_{ab}=\sum_\alpha A_\alpha\otimes B_\alpha$, and put
$A_\alpha^\circ=A_\alpha-\operatorname{Tr}(\rho_aA_\alpha)I$ and
$B_\alpha^\circ=B_\alpha-\operatorname{Tr}(\rho_bB_\alpha)I$. Then
$$
 n_e=-i\left[\sum_\alpha A_\alpha^\circ\otimes B_\alpha^\circ,
                   \rho_a\otimes\rho_b\right].
$$
Indeed, tracing the uncentered commutator over either endpoint gives
the corresponding mean-field commutator; subtracting the two product
tangents gives exactly the centered expression. Both partial traces of
the centered expression vanish. Raw commutators do not generally have
that property. For example, $h_{ab}=Z\otimes Z$ and the state
$|0+\rangle$ have a nonzero commutator but $n_e=0$.

For pure endpoint states, write
$$
 u=\alpha\otimes\beta,\quad
 \chi=(I-|\alpha\rangle\langle\alpha|)
       \otimes(I-|\beta\rangle\langle\beta|)\,h_{ab}u.
$$
The centered Hamiltonian applied to $u$ is $\chi$, which is
orthogonal to $u$. Consequently
$$
 n_e=-i(|\chi\rangle\langle u|-|u\rangle\langle\chi|),
 \qquad
 \boxed{\ \nu_e=2\lVert \chi\rVert.\ }
$$
The two possible nonzero eigenvalues are $\pm\lVert \chi\rVert$.
In the notation of the product decomposition,
$$
 \frac{\nu_e^2}{4}
 =\sum_{\alpha,\beta}
 \bigl(\langle A_\alpha A_\beta\rangle
       -\langle A_\alpha\rangle\langle A_\beta\rangle\bigr)
 \bigl(\langle B_\alpha B_\beta\rangle
       -\langle B_\alpha\rangle\langle B_\beta\rangle\bigr).
$$
This is the correlated uncertainty in Yang's entanglement timescale
[15], so $\nu_e=2/T_{\mathrm{ent}}$ for the isolated pure bipartite
interaction, with $T_{\mathrm{ent}}=\infty$ when the rate vanishes.
Cresswell [16] relates the same quantity to Rényi entropy growth.
Here the quantity gives a trace-norm rate with an explicit finite-time
remainder, and the general theorem also permits mixed product states.

### 5.4 Exact Short-Time Local Defect Bound

**Theorem 5.1 (Exact Finite-System Short-Time Lower Bound).** Let $G=(V,E)$ be a finite graph and set $\hbar = 1$. Let $H=\sum_{1\le |X|\le2}h_X$ be a one- and two-local Hamiltonian whose two-site terms are supported on edges of $G$, with full incident interaction norm
$$
g:=\max_{v\in V}\sum_{X\ni v}\lVert h_X\rVert_\infty<\infty.
$$
Let $\Pi_e(\sigma_{ab}) := \operatorname{Tr}_b(\sigma_{ab}) \otimes \operatorname{Tr}_a(\sigma_{ab})$ be the product retraction, with $P_e := D\Pi_e|_{\rho_a\otimes\rho_b}$, $Q_e:=I-P_e$, and $n_e:=Q_e\dot\rho_{ab}(0)$. For every edge $e=\{a,b\}$ and every $t\ge0$, under a global pure or mixed product initial state $\rho(0)=\bigotimes_{v\in V}\rho_v$, the two-site correlation defect $D_e(t) := \lVert \rho_{ab}(t) - \rho_a(t) \otimes \rho_b(t)\rVert_1$ satisfies
$$
\boxed{
D_e(t)\ge\nu_e t-24g^2t^2,
}
$$
where $\nu_e = \lVert n_e\rVert_1$. In particular, if $\nu_e\ge\nu_{\min}>0$, then
$$
D_e(t)\ge\frac{\nu_{\min}}{2}t
\qquad
\text{for }
0<t\le\frac{\nu_{\min}}{48g^2}.
$$

*Proof.* Define the operator-valued correlation residual
$$
F_e(t):=\rho_e(t)-\rho_a(t)\otimes\rho_b(t).
$$
The product initial condition gives $F_e(0)=0$, and differentiation of the product map gives
$$
F_e'(0)=Q_eL_e=n_e.
$$
Moreover,
$$
F_e''(t)
=
\ddot\rho_e(t)
-
\ddot\rho_a(t)\otimes\rho_b(t)
-
2\dot\rho_a(t)\otimes\dot\rho_b(t)
-
\rho_a(t)\otimes\ddot\rho_b(t).
$$
Trace-norm multiplicativity on tensor products, unit trace of the density matrices, and the bounds of Lemma 5.2 imply
$$
\lVert F_e''(t)\rVert_1
\le
24g^2+8g^2+2(2g)(2g)+8g^2
=
48g^2.
$$
Taylor's formula with integral remainder gives
$$
F_e(t)
=
tn_e+\int_0^t(t-u)F_e''(u)\,du.
$$
Therefore
$$
D_e(t)=\lVert F_e(t)\rVert_1
\ge
t\lVert n_e\rVert_1
-
\frac{t^2}{2}\sup_{0\le u\le t}\lVert F_e''(u)\rVert_1
\ge
\nu_e t-24g^2t^2.
$$
The half-slope interval follows immediately. $\square$

**Corollary 5.1.A (System-Size-Independent Family Bound).** Consider a sequence of finite quantum lattice systems indexed by size $N$, with $H_N=\sum_{1\le |X|\le2}h_{N,X}$, edge sets $E_N$, active edge subsets $A_N \subseteq E_N$, and full incident norms $g_N:=\max_{v}\sum_{X\ni v}\lVert h_{N,X}\rVert_\infty$. Suppose there exist system-size-independent constants $0<g_*<\infty$, $\eta_* > 0$, $\nu_* > 0$, and $a_* > 0$ such that
$$
\sup_N g_N \le g_*, \qquad \inf_N \frac{|A_N|}{|E_N|} \ge \eta_* > 0, \qquad \inf_{N, e \in A_N} \nu_{N,e} \ge \nu_* > 0, \qquad \inf_N \frac{|E_N|}{N} \ge a_* > 0.
$$
Then on the uniform near-zero time interval
$$
0 < t \le \frac{\nu_*}{48 g_*^2},
$$
the total edge-tally defect sum $C(t) = \sum_{e \in E_N} D_e(t)$ satisfies uniform site-density and edge-density bounds independent of $N$:
$$
\frac{C(t)}{N} \ge a_* \eta_* (\nu_* t - 24 g_*^2 t^2) \ge \frac{a_* \eta_* \nu_*}{2} t, \qquad \frac{C(t)}{|E_N|} \ge \eta_* (\nu_* t - 24 g_*^2 t^2).
$$

**Remark 5.1.1 (Schatten norm conversion).** On a two-site Hilbert space of dimension $D = d_a d_b$, converting from the trace norm $\lVert \cdot\rVert_1$ to a Schatten $p$-norm $\lVert \cdot\rVert_p$ ($p > 1$) via Hölder's inequality introduces a dimension factor $D^{-(1 - 1/p)}$ (for $d_a = d_b = d$, a factor of $d^{-2(1 - 1/p)}$, i.e., $d^{-1}$ for the Hilbert--Schmidt norm $p=2$ and $d^{-2}$ for the operator norm $p=\infty$).

### 5.4.1 Open-system Lindbladian generators, parameter uncertainty, and 3-axis separation

Theorem 5.1 extends directly to open quantum systems governed by Markovian Lindblad master equations:
$$
\dot\rho = \mathcal L(\rho) = -i[H, \rho] + \sum_a \gamma_a \mathcal{D}_{L_a}(\rho), \qquad \mathcal{D}_{L_a}(\rho) := L_a \rho L_a^\dagger - \frac{1}{2} \{L_a^\dagger L_a, \rho\}.
$$
In the Heisenberg picture, the adjoint dissipator acts on any operator $A_S$ supported on $S\subseteq V$ via the commutator identity
$$
\mathcal{D}_{L_a}^\dagger(A_S) = L_a^\dagger A_S L_a - \frac{1}{2}\{L_a^\dagger L_a, A_S\} = \frac{1}{2}L_a^\dagger[A_S, L_a] + \frac{1}{2}[L_a^\dagger, A_S]L_a.
$$
Consequently, $\mathcal{D}_{L_a}^\dagger(A_S) = 0$ whenever $\operatorname{supp}(L_a)\cap S = \emptyset$, and $\lVert\mathcal{D}_{L_a}^\dagger(A_S)\rVert_\infty \le 2\lVert L_a\rVert_\infty^2 \lVert A_S\rVert_\infty$ whenever $\operatorname{supp}(L_a)\cap S \ne \emptyset$. For local interaction supports $X\subset V$ with $|X|\le 2$, define the local Lindblad generator strength
$$
\ell_X := 2\lVert h_X\rVert_\infty + 2\sum_{a: \operatorname{supp}(L_a) = X} \gamma_a \lVert L_a\rVert_\infty^2, \qquad \Lambda_* := \max_{v\in V} \sum_{X\ni v} \ell_X.
$$
When all Hamiltonian terms and Lindblad jump operators are at most 2-local ($\lvert\operatorname{supp}(L_a)\rvert \le 2$), with nonnegative rates $\gamma_a$, replacing $2g$ by $\Lambda_*$ in the support-counting argument of Lemma 5.2 yields, for $\lVert A_S\rVert_\infty\le1$, $\lVert\mathcal{L}^\dagger(A_S)\rVert_\infty \le |S|\Lambda_*$ and $\lVert(\mathcal{L}^\dagger)^2(A_S)\rVert_\infty \le 2\Lambda_*^2$ for $|S|=1$ and $6\Lambda_*^2$ for $|S|=2$. Thus $\lVert F_{ab}''(t)\rVert_1 \le (6 + 2 + 2 + 2)\Lambda_*^2 = 12\Lambda_*^2$, and for each edge $e=\{a,b\}$ with initial normal rate $\nu_{ab} = \lVert Q_{ab}\mathcal{L}(\rho(0))_{ab}\rVert_1$, Taylor's theorem gives the volume-uniform open-system lower bound
$$
D_{ab}(t) \ge \nu_{ab} t - 6\Lambda_*^2 t^2.
$$
Under interval uncertainty $\nu_{ab} \in [\nu_{ab}^-, \nu_{ab}^+]$ and $\Lambda_* \in [\Lambda_*^-, \Lambda_*^+]$, monotonicity on $\mathbb{R}_{\ge 0}$ yields the worst-case enclosure
$$
D_{ab}(t) \ge \nu_{ab}^- t - 6(\Lambda_*^+)^2 t^2.
$$
This formulation distinguishes three physical mechanisms affecting two-site marginals:
1. *Coherent Hamiltonian dynamics:* reversible unitary evolution under $-i[H, \cdot]$, which generates first-order normal leakage $\nu_{ab}$ solely from two-site edge interactions;
2. *Dissipative Lindbladian dynamics:* completely positive trace-preserving semigroup evolution under jump operators $L_a$ and rates $\gamma_a$, which can either damp correlations (via single-site decoherence) or drive dissipative state preparation and purification (for instance, single-qubit amplitude damping reduces the von Neumann entropy of $I/2$ from $1$ bit to $0.68862$ bits at $\gamma t = 1$);
3. *Classical statistical mixing:* convex combinations of density matrices or measurement-induced conditioning, which are static operations distinct from generator-driven evolution.

### 5.5 Edge-Normalized and Site-Normalized Density Corollaries

Define the active edge subset $A_{\nu_{\min}}:=\{e\in E:\nu_e\ge\nu_{\min}\}$ with active fraction $|A_{\nu_{\min}}|\ge\eta|E|$, and let $C(t):=\sum_{e\in E}D_e(t)$ be the total edgewise correlation tally.

1. **Edge-Normalized Defect Density:**
   $$
   \frac{C(t)}{|E|} \ge \eta\bigl(\nu_{\min}t-24g^2t^2\bigr).
   $$
   For $0 < t \le \frac{\nu_{\min}}{48g^2}$, this yields $\frac{C(t)}{|E|} \ge \frac{\eta \nu_{\min}}{2} t$.

2. **Site-Normalized Defect Density:**
   If the graph family satisfies $|E|\ge aN$, then
   $$
   \boxed{
   \frac{C(t)}{N} \ge a\eta\bigl(\nu_{\min}t-24g^2t^2\bigr) \ge \frac{a\eta\nu_{\min}}{2}t
   }
   $$
   for $0<t\le\frac{\nu_{\min}}{48g^2}$.

**Remark 5.5.1 (Pairwise scope of the edge tally).** The quantity $C(t)=\sum_{e\in E}D_e(t)$ is an overlapping sum of two-site product-retraction residuals. It is distinct from the global trace norm $\lVert\rho(t)-\bigotimes_{v\in V}\rho_v(t)\rVert_1$, from entanglement measures (as separable correlated states can have $D_e > 0$), from Bell nonlocality (§7.10), and from the cohomological quotient seminorm $\Phi$.

### 5.6 Lipschitz Transfer Bound

When comparing two states $\rho$ and $\sigma$ under a retraction or projection map $P$ that is $L$-Lipschitz with respect to a norm $\lVert\cdot\rVert$, the reverse triangle inequality gives the elementary transfer estimate
$$
\lVert\rho - P(\rho)\rVert \ge \lVert\sigma - P(\sigma)\rVert - (1+L)\lVert\rho-\sigma\rVert.
$$
This abstract inequality is mechanized as `ProjectionTransfer.transfer` in `lean4/po000_l001_projection_transfer.lean` (along with its $K_\Pi = 1+L = 3$ specialization `ProjectionTransfer.transfer_product_KPi_three` for the two-site product retraction, which has Lipschitz constant $L=2$ on density operators by telescoping $\rho_a\otimes\rho_b - \sigma_a\otimes\sigma_b = (\rho_a-\sigma_a)\otimes\rho_b + \sigma_a\otimes(\rho_b-\sigma_b)$). Notice that Theorem 5.1 above differentiates the moving product residual $F_e(t)=\rho_e(t)-\rho_a(t)\otimes\rho_b(t)$ directly and therefore does not need this Lipschitz transfer step.

### 5.7 Non-Firing and Boundary Cases

We record seven boundary regimes where the first-order lower bound of Theorem 5.1 vanishes or becomes uninformative:

1. **Tangent Initial Directions ($\nu_e = 0$):** If $n_e=Q_eL_e=0$, the first-order normal rate vanishes. The defect starts at $\mathcal{O}(t^2)$ and Theorem 5.1 gives the trivial bound $D_e(t) \ge -24g^2 t^2$.
2. **Commutative or Product-Preserving Dynamics:** If $[h_{\{a,b\}}, \rho_a \otimes \rho_b] = 0$, no normal product defect is generated at first order on edge $\{a,b\}$.
3. **Sparse Active Edges:** If $|A_N|/|E_N| \to 0$, the active-set sum yields no positive uniform edge-normalized bound; if $|A_N|/N \to 0$, it yields no positive uniform site-normalized bound.
4. **Vanishing Rate-to-Curvature Ratio:** The guaranteed half-slope window shrinks to zero when $\nu_{\min}/g^2\to0$, including $\nu_{\min}\to0$ at fixed $g>0$. A vanishing rate alone does not decide this if the interactions also weaken.
5. **Growing Incident Strength:** If the full incident norm $g$ grows while $\nu_{\min}$ stays bounded, the guaranteed window shrinks. Unbounded degree alone does not imply this: edge strengths can decrease so that their incident sums remain bounded.
6. **Higher-Order Defect Onset:** When $\nu_e=0$ because of initial-state alignment, correlation production begins at order $t^2$ or higher; Section 5.8 provides higher-order Taylor bounds and §6.3 gives explicit quadratic and cubic onset examples.
7. **Purely Multipartite Correlations:** Because $C(t)$ sums two-site defects $D_e(t)$, it vanishes on states whose two-site marginals are all factorized even when $k$-body connected cumulants ($k\ge 3$) are nonzero (§5.12–§5.17).

---

### 5.8 Higher-Order Short-Time Bounds

The first-order estimate can be sharpened without changing the hypotheses of
Theorem 5.1. Put $F_e(t)=\rho_e(t)-\rho_a(t)\otimes\rho_b(t)$, as above.
All derivatives below are derivatives of this full residual, including both
moving marginals.

**Lemma 5.4 (uniform derivative bounds).** For a nonempty set $S$ of $k$
sites and any integer $j\geq0$,
$$
 \lVert \rho_S^{(j)}(t)\rVert_1
 \leq (2g)^j k(k+1)\cdots(k+j-1)
$$
for all real $t$, with empty product one. In particular,
$$
 \boxed{\ \lVert F_e^{(j)}(t)\rVert_1\leq 2^{j+1}(j+1)!\,g^j.\ }
$$

*Proof.* Expand $\operatorname{ad}_H^j(A_S)$ as a sum of nested
commutators. At step $r+1$, a surviving term has support on at most
$k+r$ sites, so the sum of norms of Hamiltonian terms meeting that
support is at most $(k+r)g$. Each commutator contributes a factor two.
This bound is applied to each branch of the expansion before summing;
the full commutator need not have a single small support. The identity
$$
 \operatorname{Tr}\bigl(A_S\rho_S^{(j)}(t)\bigr)
 =i^j\operatorname{Tr}\bigl(\operatorname{ad}_H^j(A_S)\rho(t)\bigr)
$$
and trace-norm/operator-norm duality give the first assertion.
For the product of the two one-site marginals, the Leibniz rule gives
$$
 \begin{aligned}
 \left\lVert\frac{d^j}{dt^j}(\rho_a\otimes\rho_b)\right\rVert_1
 &\leq\sum_{m=0}^j {j\choose m}
       (2g)^m m!\,(2g)^{j-m}(j-m)!\\
 &=(2g)^j(j+1)!.
 \end{aligned}
$$
Adding the two-site bound gives the stated estimate. $\square$

**Theorem 5.5 (finite Taylor approximation).** Define
$$
 P_{e,J}(t)=\sum_{j=1}^{J}\frac{t^j}{j!}F_e^{(j)}(0),
 \qquad
 R_J(t)=2^{J+2}(J+2)g^{J+1}t^{J+1}.
$$
For every integer $J\geq1$ and every $t\geq0$,
$$
 \lVert F_e(t)-P_{e,J}(t)\rVert_1\leq R_J(t),\qquad
 \boxed{\ \bigl|D_e(t)-\lVert P_{e,J}(t)\rVert_1\bigr|\leq R_J(t).\ }
$$
Consequently, for any Hermitian $W$ with $\lVert W\rVert_\infty\leq1$,
$$
 D_e(t)\geq
 \sum_{j=1}^{J}\frac{t^j}{j!}\operatorname{Tr}
       \bigl(WF_e^{(j)}(0)\bigr)-R_J(t).
$$

*Proof.* Taylor's integral remainder and Lemma 5.4 give
$$
 \lVert F_e(t)-P_{e,J}(t)\rVert_1
 \leq\frac{t^{J+1}}{(J+1)!}
       2^{J+2}(J+2)!\,g^{J+1}=R_J(t).
$$
Apply the reverse triangle inequality for the second conclusion and
trace-norm duality for the witness inequality. $\square$

Taking $J=1$ gives the two-sided refinement of Theorem 5.1:
$$
 |D_e(t)-\nu_e t|\leq24g^2t^2,\qquad
 \lim_{t\downarrow0}\frac{D_e(t)}t=\nu_e.
$$
In particular, $\nu_e=0$ implies $D_e(t)\leq24g^2t^2$.

More generally, if $m\geq1$ is the first index with
$A_m:=F_e^{(m)}(0)\ne0$, then
$$
 \left|D_e(t)-\frac{\lVert A_m\rVert_1}{m!}t^m\right|
 \leq2^{m+2}(m+2)g^{m+1}t^{m+1},
 \qquad
 \lim_{t\downarrow0}\frac{D_e(t)}{t^m}=\frac{\lVert A_m\rVert_1}{m!}.
$$
For $g>0$, a half-leading-term bound holds on
$$
 0<t\leq
 \frac{\lVert A_m\rVert_1}{2^{m+3}(m+2)m!\,g^{m+1}}.
$$
For example, if $F_e'(0)=0$ and $\mu_e=\lVert F_e''(0)\rVert_1>0$,
$$
 D_e(t)\geq\frac{\mu_e}{2}t^2-64g^3t^3
 \geq\frac{\mu_e}{4}t^2
 \quad\text{when}\quad
 0<t\leq\frac{\mu_e}{256g^3}.
$$
The $g=0$ case has constant product evolution and zero defect.
A family version follows by replacing $g$ by a uniform upper bound and
$\lVert A_m\rVert_1/m!$ by a positive uniform lower bound on a declared positive
density of edges, all with the same first nonzero order $m$.

These are bounds on the polynomial as a whole; different coefficients can
cancel. Computing more derivatives does not by itself promise a longer
interval on which the lower bound is positive. The constants also show
convergence: the remainder is $2(J+2)(2gt)^{J+1}$, which tends to zero
when $2g|t|<1$. Each fixed finite system actually has an entire
matrix-valued residual, since matrix exponentials and products are entire.
Thus vanishing of every derivative at zero is equivalent to
$F_e(t)=0$ for all real $t$. The norm $D_e$ itself need not be analytic.
Section 5.16 replaces the all-derivatives test by a finite certificate for each fixed polynomial model. Neither assertion establishes an infinite-volume limit.

**Schatten norms.** For $1\leq p\leq\infty$, the same remainder satisfies
$$
 \bigl|\lVert F_e(t)\rVert_p-\lVert P_{e,J}(t)\rVert_p\bigr|
 \leq\lVert F_e(t)-P_{e,J}(t)\rVert_p\leq R_J(t).
$$
The first-order rate is then $\lVert n_e\rVert_p$. No dimension factor is needed
when this rate is computed in the chosen norm. Converting only a known
trace-norm rate to another norm still incurs the dimension factor stated
in §5.4.

**Proposition 5.6 (locality of the Taylor coefficients).** Under the product
initial condition and two-site interaction assumption, $F_e^{(j)}(0)$,
for $j\geq1$, is unchanged when the system is restricted to the induced
subgraph on sites at graph distance at most $j-1$ from $\{a,b\}$.
The restricted Hamiltonian keeps exactly those terms supported there,
and the initial state is the corresponding product.

*Proof.* Give each Hamiltonian term its own scalar parameter. The
$j$-th derivative of the residual is a homogeneous polynomial of degree
$j$ in these parameters. Consider one of its monomials and set all
parameters absent from that monomial to zero. If its interaction supports
do not connect $a$ to $b$, the reduced state remains a product and
that monomial's coefficient vanishes. If an interaction component does
not meet $a$ or $b$, its evolution disappears under the partial trace;
the residual is independent of its parameters, so a monomial containing
such a parameter also has zero coefficient. Hence every surviving
monomial uses a connected interaction graph containing both endpoints,
with at most $j$ edges (one-site terms add no edges). Any vertex in such
a graph is at distance at most $j-1$ from the endpoint set: connecting
both endpoints requires at least one edge in addition to a shortest path
from that vertex to the nearer endpoint. Every contributing term and
initial factor therefore lies in the declared neighborhood. $\square$

This gives a finite local computation for each fixed order. Its cost can
grow exponentially with the neighborhood size; it is not a polynomial-time
algorithm in unrestricted order, degree or local dimension.

### 5.9 Finite Regions and Larger Interaction Supports

The second-order estimate also extends to an explicitly changed interaction
assumption. Let every Hamiltonian term have support of size at most $r$,
let $g=\max_v\sum_{X\ni v}\lVert h_X\rVert_\infty$, and let $S$ contain $k\geq1$
sites. For a global product initial state, define
$$
 F_S(t)=\rho_S(t)-\bigotimes_{v\in S}\rho_v(t),\qquad
 \nu_S=\lVert F_S'(0)\rVert_1.
$$
Then, for $t\geq0$,
$$
 \boxed{\ \bigl|\lVert F_S(t)\rVert_1-\nu_S t\bigr|
 \leq4k(k+r-1)g^2t^2.\ }
$$

*Proof.* The first commutator has incident norm sum at most $kg$;
each branch then has at most $k+r-1$ sites. Thus
$\lVert \rho_S''(t)\rVert_1\leq4k(k+r-1)g^2$.
Each one-site second derivative is bounded by $4rg^2$, while each
one-site first derivative is bounded by $2g$. The second derivative of
the product has $k$ second-derivative terms and $k(k-1)$ ordered
cross terms, giving
$$
 4krg^2+4k(k-1)g^2=4k(k+r-1)g^2.
$$
The sum of the two bounds, followed by the integral remainder factor
$1/2$, gives the result. $\square$

Only Hamiltonian terms meeting $S$ in at least two sites can contribute
to $F_S'(0)$; terms meeting a single site give a product tangent.
For $r=2$ these are internal edges. For $r>2$ a contributing term can
also meet the complement, so its contribution may depend on initial
states outside $S$. For $k=1$, the residual is identically zero.

### 5.10 The Infinite-Volume Dynamics and a Defect-Density Limit

Here a thermodynamic limit means convergence of finite-volume evolution
on every fixed local observable, uniformly on compact time intervals.
It does not mean convergence of a global density matrix in trace norm.
The construction below uses standard quantum-spin dynamics on the
norm-completed algebra of local observables; existence results in this
setting are established in the literature, including [9, Theorem 2.2].
The purpose here is to connect the elementary derivative estimate to
an all-time limit and to the particular defect studied in this paper.

Assume a fixed countable, locally finite graph $G$, a finite-dimensional
Hilbert space at each vertex, fixed Hermitian one-site and edge terms,
and
$$
 g_*:=\sup_v\sum_{X\ni v}\lVert h_X\rVert_\infty<\infty.
$$
Let $\mathcal A$ be the operator-norm completion of the union of the
finite tensor-product observable algebras, embedded by tensoring with
identities. For finite $\Lambda\subset G$, put
$$
 H_\Lambda=\sum_{X\subseteq\Lambda}h_X,\qquad
 \alpha_t^\Lambda(A)=e^{itH_\Lambda}Ae^{-itH_\Lambda}.
$$
These are isometric automorphisms of the same algebra $\mathcal A$,
including when $A$ is not supported inside $\Lambda$.

**Theorem 5.7 (all-time local thermodynamic limit).** There is a strongly
continuous one-parameter group of isometric $*$-automorphisms
$\alpha_t$ of $\mathcal A$ such that, for every $A\in\mathcal A$
and $T<\infty$,
$$
 \lim_{\Lambda\uparrow G}\ \sup_{|t|\leq T}
 \lVert \alpha_t^\Lambda(A)-\alpha_t(A)\rVert_\infty=0.
$$
The limit is independent of the finite exhaustion. Every initial state
$\omega$ on $\mathcal A$ therefore has a limiting evolution
$\omega_t=\omega\circ\alpha_t$; its finite-region density matrices are
the trace-norm limits of those obtained by evolving
$\omega|_{\mathcal A_\Lambda}$. These local limits are uniform for
$|t|\leq T$. No product-state assumption is needed for existence.

*Proof.* The case $g_*=0$ is constant evolution. Suppose $g_*>0$.
For a local $A$ supported on $k\geq1$ vertices, the branchwise
commutator count of Lemma 5.4 gives
$$
 \lVert (\operatorname{ad}_{H_\Lambda})^j A\rVert_\infty
 \leq \lVert A\rVert_\infty(2g_*)^j k(k+1)\cdots(k+j-1).
$$
Each nonzero branch adds at most one vertex at each commutator.
Consequently, the order-$j$ coefficient is independent of
$\Lambda$ once it contains the radius-$j$ neighborhood of
$\operatorname{supp}A$. That neighborhood is finite by local
finiteness. Unitary conjugation preserves the norm of every derivative,
so Taylor's integral remainder gives, for $0\leq\tau<1/(2g_*)$,
$$
 \sup_{|t|\leq\tau}
 \left\lVert\alpha_t^\Lambda(A)-
 \sum_{j=0}^{J}\frac{(it)^j}{j!}
       (\operatorname{ad}_{H_\Lambda})^j A\right\rVert_\infty
 \leq \lVert A\rVert_\infty {k+J\choose J+1}(2g_*\tau)^{J+1}.                 \tag{5.10a}
$$
For fixed $k$ the right side tends to zero. Coefficient stabilization
therefore makes the finite-volume evolutions uniformly Cauchy on this
interval, with the same limit for every exhaustion. In fact the
Cauchy estimate holds for all finite volumes containing a sufficiently
large fixed neighborhood, not only for a selected sequence.

For $|t|<1/(2g_*)$, take this limit on local observables. The limits
preserve norms, products, adjoints and the identity, so they extend to
isometric unital $*$-endomorphisms on $\mathcal A$.
Approximating any $B\in\mathcal A$ by a local observable extends the
uniform-in-$t$ convergence to $B$: the two approximation errors
are at most $2\lVert B-A\rVert_\infty$. It also gives norm continuity in $t$
for each $B$.

For $s,t,s+t$ in this short interval, finite-volume composition passes
to the limit because
$$
 \begin{aligned}
 \lVert \alpha_s^\Lambda(\alpha_t^\Lambda B)-\alpha_s(\alpha_t B)\rVert_\infty
 &\leq\lVert \alpha_t^\Lambda B-\alpha_t B\rVert_\infty\\
 &\quad+\lVert \alpha_s^\Lambda(\alpha_t B)-\alpha_s(\alpha_t B)\rVert_\infty
 \longrightarrow0 .
 \end{aligned}
$$
Thus $\alpha_s\alpha_t=\alpha_{s+t}$ there. Taking $s=-t$
shows that these maps are automorphisms.

For an arbitrary real $t$, choose an integer $n$ with
$|t|/n<1/(2g_*)$ and define
$\alpha_t=(\alpha_{t/n})^n$. A common integer refinement of two
subdivisions and the short-interval composition law show that this
definition is independent of $n$. For $s,t\in\mathbb R$, choose
$n$ so that $s/n,t/n,(s+t)/n$ lie in the short interval. Their
short-time maps commute and multiply to $\alpha_{(s+t)/n}$;
taking $n$-th powers gives the group law. Continuity near zero
and the group law give strong continuity for every real time.

It remains to show convergence of the original finite-volume evolution,
rather than just to define a candidate extension. Fix $T<\infty$ and
$n$ with $\tau=T/n<1/(2g_*)$. A telescoping identity and isometry give,
with $u=t/n$,
$$
 \lVert \alpha_t^\Lambda B-\alpha_t B\rVert_\infty
 \leq\sum_{\ell=0}^{n-1}
 \lVert (\alpha_u^\Lambda-\alpha_u)(\alpha_u^\ell B)\rVert_\infty.          \tag{5.10b}
$$
The set
$\{\alpha_u^\ell B:|u|\leq\tau,\ 0\leq\ell<n\}$ is compact,
by norm continuity. Short-time convergence is uniform on this compact
set: take a finite norm net and use the operator-norm bound
$\lVert \alpha_u^\Lambda-\alpha_u\rVert\leq2$.
The right side of (5.10b) therefore tends to zero uniformly for
$|t|\leq T$, for all sufficiently large finite volumes.

For a state $\omega$, applying it to the observable convergence
gives convergence of each matrix coefficient of every finite-region
density matrix. All norms on that fixed finite-dimensional matrix
space are equivalent, yielding uniform trace-norm convergence.
Positivity, unit trace and consistency under partial trace pass to
the limit. $\square$

**Product-state defect estimates in the limit.** For fixed compatible
product initial data and an edge $e=\{a,b\}$, put
$$
 F_e^\infty(t)=\rho_e^\infty(t)
             -\rho_a^\infty(t)\otimes\rho_b^\infty(t).
$$
Every finite-order estimate in §5.8 passes to the limit. In particular,
for $J\geq1$ and every real $t$,
$$
 \lVert F_e^\infty(t)-P_{e,J}(t)\rVert_1
 \leq2(J+2)(2g_*|t|)^{J+1}.                                    \tag{5.10c}
$$
The coefficients are the stabilized finite-volume derivatives.
For $2g_*|t|<1$ the remainder tends to zero with $J$, so the
identification with the derivatives of $F_e^\infty$ at zero follows
from its convergent power series. For any finite $\Lambda$
containing the radius-$(J-1)$ neighborhood of $e$,
$$
 \lVert F_e^\Lambda(t)-F_e^\infty(t)\rVert_1
 \leq4(J+2)(2g_*|t|)^{J+1}.                                    \tag{5.10d}
$$
This explicit estimate is useful near zero; all-time convergence comes
from (5.10b), not from extending the convergence radius of (5.10a).

An actual limit of the spatially averaged diagnostic needs additional
spatial assumptions. The following elementary case complements the
uniform family lower bounds in §5.5.

**Corollary 5.8 (translation-invariant defect density).** Suppose
$G=\mathbb Z^d$ with nearest-neighbor edges, the on-site spaces,
interactions and product initial state are translation invariant, and
$\Lambda_L=\{-L,\ldots,L\}^d$ has open boundaries. Write $E_L$
for its internal nearest-neighbor edges and
$$
 d_L(t)=\frac1{|E_L|}\sum_{e\in E_L}D_e^{\Lambda_L}(t),\qquad
 D_r^\infty(t)=\lVert F_{\{0,\mathbf e_r\}}^\infty(t)\rVert_1 .
$$
Then, uniformly on every compact time interval,
$$
 d_L(t)\longrightarrow d_\infty(t):=
 \frac1d\sum_{r=1}^dD_r^\infty(t).
$$
If $\bar\nu=d^{-1}\sum_{r=1}^d\nu_{\{0,\mathbf e_r\}}$, then
$$
 d_\infty(t)\geq\bar\nu\,t-24g_*^2t^2\qquad(t\geq0).
$$
In particular $\bar\nu>0$ gives a strictly positive limiting
defect density for $0<t<\bar\nu/(24g_*^2)$.

*Proof.* Translating finite volumes and using exhaustion independence
shows that the limiting dynamics, and hence the product-state
evolution, is translation invariant. Given $T$ and $\varepsilon>0$,
Theorem 5.7 gives a radius $R$ such that every edge whose
radius-$R$ neighborhood is contained in $\Lambda_L$ has defect
within $\varepsilon$ of the corresponding $D_r^\infty$, uniformly
for $|t|\leq T$. To obtain one $R$, use a finite matrix basis for
each of the $d$ edge orientations and the net convergence proved
above; tensor-product continuity transfers the estimate to $F_e$.
The fraction of remaining edges tends to zero as $L\to\infty$,
and both finite and limiting defects lie in $[0,2]$. Each
orientation has exactly the same number of internal edges in the
cube. Averaging establishes the limit. Averaging the limiting version of
Theorem 5.1 establishes the lower bound. $\square$

Theorem 5.7 supplies the all-time dynamical thermodynamic limit under
the stated bounded-interaction assumptions. Corollary 5.8 additionally
supplies a spatial density limit under translation invariance.
Neither establishes an equilibrium free-energy limit, selection or
uniqueness of a thermodynamic phase, a continuum scaling limit, or
nonzero defect at arbitrarily late times.

### 5.10.1 Locality-controlled Duhamel bounds and numerical enclosures

To turn defect diagnostics into certified predictive bounds for physical observables, consider the expectation $\langle O\rangle_{\rho(t)}$ of an observable $O$ along the true trajectory $\rho(t)$ compared with a reduced or model trajectory $\widetilde\rho(t)$.
The variation-of-constants formula rigorously distinguishes three separate diagnostic quantities:
1. *Equation residual:* $R(s) := \dot{\widetilde\rho}(s) - \mathcal L\widetilde\rho(s)$, which measures the failure of the model trajectory to satisfy the true physical master equation;
2. *Normal velocity defect:* $\nu_m := \operatorname{dist}_1(\mathcal L m, T_m\mathcal M)$, the instantaneous rate of escaping the model manifold $\mathcal M$;
3. *State defect:* $D(m) := \operatorname{dist}_1(m, \mathcal M)$, the instantaneous trace-norm distance to the model manifold.

Integrating the Heisenberg operator evolution or the Schrödinger equation residual yields the unweighted global Duhamel bound:
$$
|\langle O\rangle_{\rho(t)} - \langle O\rangle_{\widetilde\rho(t)}| \le \lVert O\rVert_\infty \int_0^t \lVert \mathcal L\widetilde\rho(s) - \dot{\widetilde\rho}(s)\rVert_1\,ds + E_{\mathrm{initial}} + E_{\mathrm{numerical}}.
$$
By trace-operator norm Hölder duality, $|\operatorname{Tr}(O \Delta\rho)| \le \lVert O\rVert_\infty \lVert\Delta\rho\rVert_1$. The factor of 2 in conventional literature appears only when converting raw trace norm $\lVert\cdot\rVert_1$ to trace distance $T = \frac{1}{2}\lVert\cdot\rVert_1$, since $|\operatorname{Tr}(O \Delta\rho)| \le 2 \lVert O\rVert_\infty T(\rho, \widetilde{\rho}) = \lVert O\rVert_\infty \lVert\Delta\rho\rVert_1$.

For a local observable $O$ supported on a region $X$, the spatial influence of an interaction term on edge $e$ is controlled by the locality weights:
$$
w_{O,e}(\tau) \le \min\left(\lVert O\rVert_\infty,\; C_0 \lVert O\rVert_\infty e^{v_{\mathrm{LR}}\tau - \mu d(e, X)}\right),
$$
where $v_{\mathrm{LR}}$ is the Lieb–Robinson velocity and $\mu > 0$ is the spatial decay rate.
Notice that the operator-norm upper cap is $\lVert O\rVert_\infty$; omitting a redundant factor of $\lVert h_e\rVert_\infty$ is essential to prevent underestimating physical prediction errors in weakly coupled systems.
Indeed, in a two-qubit entangling pair with $H = \varepsilon X\otimes X$ ($\varepsilon = 0.1$) starting from $\rho(0) = |00\rangle\langle 00|$ over duration $t = 0.1$, the exact physical prediction error for $O = Y\otimes X$ is $|\sin(2\varepsilon t)| = |\sin(0.02)| \approx 0.01999866... \le 0.02$. The equation residual has trace norm $\lVert\mathcal L\widetilde\rho(s)\rVert_1 = 2\varepsilon = 0.2$, so $\int_0^t \lVert\mathcal L\widetilde\rho(s)\rVert_1\,ds = 2\varepsilon t = 0.02$, which is enclosed by the corrected unweighted bound $\lVert O\rVert_\infty (2\varepsilon t) = 0.02$.

In computational simulations, initial state uncertainty $\delta\rho_0$ and time-integration discretization errors $\delta_{\mathrm{step}, k}$ are enclosed by:
$$
E_{\mathrm{model}}=\lVert O\rVert_\infty\int_0^t
 \lVert\mathcal L\widetilde\rho(s)-\dot{\widetilde\rho}(s)\rVert_1\,ds,
\qquad
E_{\mathrm{total}}=E_{\mathrm{model}}+E_{\mathrm{initial}}+E_{\mathrm{numerical}},
$$
where $E_{\mathrm{initial}}=\lVert O\rVert_\infty\lVert\delta\rho_0\rVert_1$
and $E_{\mathrm{numerical}}$ must bound the propagated integration, quadrature
and rounding errors in the prediction and residual integral. Certified upper
bounds for these three terms enclose the exact physical expectation in
$[y_{\mathrm{pred}}-E_{\mathrm{total}},y_{\mathrm{pred}}+E_{\mathrm{total}}]$.
The model term cannot be dropped even with exact initialization and integration:
the stationary weak-coupling example above has nonzero error. Sampled trapezoidal
quadrature without a proved remainder and freely chosen light-cone constants
produce numerical estimates, not certified enclosures.

### 5.10.2 The Edge-Decomposed TDVP Duhamel Master Theorem

Global and local-in-time error bounds for variational quantum dynamics via standard Duhamel variation of constants are established in Martinazzo and Burghardt [10] and Zoufal, Sutter, and Woerner [11]. Theorem 5.10.A contributes the exact local decomposition of the generator residual into partial-trace-annihilating edge normal operators and couples them with incident Lieb--Robinson spatial suppression weights.

**Theorem 5.10.A (Edge-Decomposed TDVP Duhamel Master Theorem).** Let $G=(V,E)$ be a finite graph with finite-dimensional local Hilbert spaces $\mathcal{H}_v$ ($v\in V$) and Hamiltonian $H = \sum_{v\in V} h_v + \sum_{e=\{u,w\}\in E} h_e$, where each $h_v$ is 1-local and each $h_e$ is 2-local on edge $e$. Work in the real affine space $\mathcal A_1=\{X=X^\dagger:\operatorname{Tr}X=1\}$ with variation space $\mathcal A_0=\{Z=Z^\dagger:\operatorname{Tr}Z=0\}$. The map $\Pi(X)=\bigotimes_v\operatorname{Tr}_{V\setminus v}X$ retracts $\mathcal A_1$ smoothly onto the products of Hermitian trace-one factors. Write $\mathcal M$ for the positive product subset and $T_m^{\mathrm{aff}}\mathcal M$ for the tangent of this smooth affine product extension. On $\mathcal A_0$, its derivative
$$
P_m Z=\sum_v\rho_{<v}\otimes\operatorname{Tr}_{V\setminus v}Z\otimes\rho_{>v}
$$
is a projection onto $T_m^{\mathrm{aff}}\mathcal M$; set $Q_m=I-P_m$ and $N_m=\ker P_m$. At full rank this is the physical product-manifold tangent. At rank boundaries it is a linear extension, not the feasible tangent cone of §5.11.1. These domain restrictions matter: differentiating the same unnormalized marginal-product formula on all operators gives $D\Pi_m(m)=|V|m$, which is not an idempotent tangent projection for $|V|>1$.
Let $\widetilde{\rho}(t) = \bigotimes_{v\in V} \rho_v(t) \in \mathcal{M}$ be a product trajectory evolving under the projected (time-dependent variational principle / mean-field) generator:
$$
\dot{\widetilde{\rho}}(s) = P_{\widetilde{\rho}(s)}\bigl(\mathcal{L}\widetilde{\rho}(s)\bigr) = -i P_{\widetilde{\rho}(s)}\bigl([H, \widetilde{\rho}(s)]\bigr).
$$
Then:
1. *Residual Locality & Single-Site Vanishing:* The Schrödinger equation residual $R(s) := \mathcal{L}\widetilde{\rho}(s) - \dot{\widetilde{\rho}}(s) = Q_{\widetilde{\rho}(s)}\bigl(\mathcal{L}\widetilde{\rho}(s)\bigr)$ vanishes identically on all 1-local Hamiltonian terms $\sum_v h_v$, and decomposes into an exact sum of partial-trace-free 2-site edge normal contributions:
$$
R(s) = \sum_{e=\{u,w\}\in E} n_e(s) \otimes \widetilde{\rho}_{V\setminus e}(s),
$$
where each edge normal defect operator
$$
n_e(s) = Q_{e, \widetilde{\rho}_e(s)}\bigl(-i[h_e, \widetilde{\rho}_e(s)]\bigr)
$$
is supported strictly on edge $e$ and satisfies the partial-trace annihilation identities
$$
\operatorname{Tr}_u n_e(s) = 0, \qquad \operatorname{Tr}_w n_e(s) = 0.
$$
(In particular, when $\widetilde{\rho}(s)$ is full-rank, distinct edge summands $n_e(s)\otimes\widetilde{\rho}_{V\setminus e}(s)$ are orthogonal with respect to the $\widetilde{\rho}(s)^{-1}$-weighted inner product $\langle A,B\rangle_{\widetilde{\rho}(s)^{-1}}=\operatorname{Tr}(A\widetilde{\rho}(s)^{-1}B)$, and for pure product states they are Hilbert--Schmidt orthogonal as in Proposition 5.11.)
2. *Edgewise Weighted Duhamel Bound:* Suppose the Heisenberg evolution $\tau_\tau(O) = e^{i\tau H}Oe^{-i\tau H}$ of a local observable $O$ supported on $X \subset V$ has a certified nonnegative residual bound $b_{O,e}(\tau)$ satisfying
$$
\bigl\lVert \tau_\tau(O) - \mathbb{E}_{V\setminus e}\bigl(\tau_\tau(O)\bigr)\otimes I_e\bigr\rVert_\infty \le b_{O,e}(\tau),
\qquad w_{O,e}(\tau)=\min\{\lVert O\rVert_\infty,b_{O,e}(\tau)\},
$$
where $\mathbb{E}_{V\setminus e}: \mathfrak{B}(\mathcal{H}_V) \to \mathfrak{B}(\mathcal{H}_{V\setminus e})$ is the normalized partial trace over $e=\{u,w\}$.
A proved Lieb--Robinson estimate may supply
$b_{O,e}(\tau)=C_0\lVert O\rVert_\infty e^{v_{\mathrm{LR}}\tau-\mu d(e,X)}$;
the constants must apply to the specified Hamiltonian and geometry.
The residual norm itself need not be at most $\lVert O\rVert_\infty$:
for $O=\operatorname{diag}(1,1,1,-1)$ and $e=V$, its normalized-trace
residual at time zero has norm $3/2$, whereas $\lVert O\rVert_\infty=1$.
The minimum bounds the trace pairing, as proved below. Then the expectation
error between $\rho(t)=e^{t\mathcal L}\rho(0)$ and the TDVP trajectory satisfies:
$$
\bigl|\langle O\rangle_{\rho(t)} - \langle O\rangle_{\widetilde{\rho}(t)}\bigr| \le \lVert O\rVert_\infty \lVert \delta\rho_0\rVert_1 + \sum_{e\in E} \int_0^t w_{O,e}(t-s) \nu_e(s)\,ds,
$$
where $\nu_e(s) = \lVert n_e(s)\rVert_1$ is the instantaneous edge normal leakage rate.

*Proof.* First, let $H_1 = \sum_{v\in V} h_v$. Then $-i[H_1, \widetilde{\rho}(s)] = \sum_{v\in V} \widetilde{\rho}_{<v} \otimes (-i[h_v, \rho_v(s)]) \otimes \widetilde{\rho}_{>v}$.
Each $-i[h_v,\rho_v(s)]$ is Hermitian and traceless and is the velocity of a local unitary orbit, including at rank boundaries. Thus $-i[H_1,\widetilde\rho(s)]\in T^{\mathrm{aff}}_{\widetilde\rho(s)}\mathcal M$, and $Q_{\widetilde\rho(s)}(-i[H_1,\widetilde\rho(s)])=0$.

Next, for each 2-local term $h_e = h_{\{u,w\}}$, $-i[h_e, \widetilde{\rho}(s)] = (-i[h_e, \widetilde{\rho}_e(s)]) \otimes \widetilde{\rho}_{V\setminus e}(s)$.
For this traceless edge operator $L=-i[h_e,\widetilde\rho_e(s)]$, the sites outside $e$ have zero marginal velocity. Consequently
$$
P_{\widetilde\rho(s)}(L\otimes\widetilde\rho_{V\setminus e}(s))
=\bigl(\operatorname{Tr}_wL\otimes\rho_w+\rho_u\otimes\operatorname{Tr}_uL\bigr)\otimes\widetilde\rho_{V\setminus e}(s).
$$
The parentheses are $P_{e,\widetilde\rho_e(s)}L$ on the Hermitian trace-zero edge space. This is an identity on the displayed edge-supported variations, not an operator factorization of the full projector on arbitrary variations.
Consequently, $Q_{\widetilde{\rho}(s)}(-i[h_e, \widetilde{\rho}(s)]) = n_e(s) \otimes \widetilde{\rho}_{V\setminus e}(s)$ with $n_e(s) = (I - P_{e, \widetilde{\rho}_e})(-i[h_e, \widetilde{\rho}_e(s)])$.
Since $\operatorname{Tr}_w(P_{e, \widetilde{\rho}_e} L) = \operatorname{Tr}_w L$, the normal operator satisfies $\operatorname{Tr}_w n_e(s) = \operatorname{Tr}_w(I - P_{e, \widetilde{\rho}_e})L = 0$ and similarly $\operatorname{Tr}_u n_e(s) = 0$. Summing over all edges $e\in E$ gives $R(s) = \sum_{e\in E} n_e(s) \otimes \widetilde{\rho}_{V\setminus e}(s)$.

Finally, substituting this decomposition into the variation-of-constants formula
$$
\rho(t) - \widetilde{\rho}(t) = e^{t\mathcal{L}}(\rho_0 - \widetilde{\rho}_0) + \int_0^t e^{(t-s)\mathcal{L}} R(s)\,ds
$$
and taking the trace pairing with $O$ gives, for each edge $e$ and lag $\tau = t-s$, the Heisenberg pairing $\operatorname{Tr}(\tau_\tau(O)(n_e(s) \otimes \widetilde{\rho}_{V\setminus e}(s)))$. Because $\operatorname{Tr}_e n_e(s) = \operatorname{Tr}_u(\operatorname{Tr}_w n_e(s)) = 0$, any operator of the form $B_{V\setminus e}\otimes I_e$ has zero trace against $n_e(s)\otimes\widetilde{\rho}_{V\setminus e}(s)$:
$$
\operatorname{Tr}\bigl((B_{V\setminus e}\otimes I_e)(n_e(s)\otimes\widetilde{\rho}_{V\setminus e}(s))\bigr) = \operatorname{Tr}_{V\setminus e}\bigl(B_{V\setminus e}\widetilde{\rho}_{V\setminus e}(s)\bigr)\operatorname{Tr}_e\bigl(n_e(s)\bigr) = 0.
$$
Choosing $B_{V\setminus e} = \mathbb{E}_{V\setminus e}(\tau_\tau(O))$ and applying trace--operator Hölder duality yields
$$
\begin{aligned}
\bigl|\operatorname{Tr}\bigl(\tau_\tau(O)(n_e(s)\otimes\widetilde{\rho}_{V\setminus e}(s))\bigr)\bigr|
&= \bigl|\operatorname{Tr}\bigl(\bigl(\tau_\tau(O) - \mathbb{E}_{V\setminus e}(\tau_\tau(O))\otimes I_e\bigr)(n_e(s)\otimes\widetilde{\rho}_{V\setminus e}(s))\bigr)\bigr| \\
&\le \bigl\lVert \tau_\tau(O) - \mathbb{E}_{V\setminus e}(\tau_\tau(O))\otimes I_e\bigr\rVert_\infty \lVert n_e(s)\rVert_1 \lVert\widetilde{\rho}_{V\setminus e}(s)\rVert_1 \\
&\le b_{O,e}(\tau)\,\nu_e(s).
\end{aligned}
$$
Direct Hölder duality also bounds the same pairing by
$\lVert\tau_\tau(O)\rVert_\infty\nu_e(s)=\lVert O\rVert_\infty\nu_e(s)$.
Taking the minimum of these two bounds gives $w_{O,e}(\tau)\nu_e(s)$.
Integrating over $s\in[0,t]$ and summing over $e\in E$ yields the claim. $\square$

**Numerical comparison on the declared eight-site cluster.**
Theorem 5.10.A is compared with floating-point Krylov evolution (`scipy.sparse.linalg.expm_multiply`) on an 8-qubit cluster of a hexagon with an attached square in `code/tests/test_honeycomb_tdvp_duhamel_integration.py`:
1. For the central bond observable $O=Z_2Z_3$, the test compares the
   numerically evolved expectation with the mean-field prediction and a
   sampled unweighted residual integral on its declared time grid.
2. For the boundary observable $O=Z_0$ with longitudinal field $h_z=0.2$,
   the test evaluates an exponentially weighted integral and compares it with
   the numerical expectation error at the sampled times.

These sampled comparisons illustrate the bound on a finite cluster. Companion package **PO-033** (*Certified Adaptive Quantum Dynamics from Projection Residuals*, v1.0.1) analyzes conditional analytic bounds and supplies an adaptive cluster prototype. However, as documented in its release manifest, that prototype is uncertified (heuristic_uncertified / `HEURISTIC_UNCERTIFIED`): it samples ideal tangent residuals at recorded times without bounding continuous-time integration, numerical quadrature, or floating-point error, and its formal Lean 4 mechanization formalizes conditional finite-sum inequalities over an abstract discrete carrier (`Nat`/`Int`), not continuous-time density-matrix dynamics. Validated continuous-time ODE integration and conservative quadrature enclosures on honeycomb lattices or general graphs remain open work.

### 5.10.3 Cut-Edge Pythagorean Cluster Rate Law

**Theorem 5.10.B (Cut-Edge Pythagorean Cluster Rate Law for Site-Factorized Pure States).** Let $G=(V,E)$ be a finite graph with 2-local Hamiltonian $H = \sum_{e\in E} h_e$. Let $\mathcal{C} = \{V_1, V_2, \dots, V_K\}$ be a partition of $V$ into disjoint clusters ($V = \bigsqcup_{k=1}^K V_k$). Let $\mathcal{M}_{\mathcal{C}} = \{\bigotimes_{k=1}^K \rho_{V_k} : \rho_{V_k} \in \mathcal{S}(\bigotimes_{v\in V_k} \mathcal{H}_v)\}$ be the cluster-product state family, using the affine product-extension tangent of §5.10.2, and let $E_{\mathrm{cut}}(\mathcal{C}) = \{\{u,w\} \in E : u \in V_k, w \in V_l, k \ne l\}$ be the set of cut edges crossing between distinct clusters.
Then for any **fully site-factorized pure state** $m = \bigotimes_{v\in V} \lvert u_v\rangle\langle u_v\rvert \in \mathcal{M} \subseteq \mathcal{M}_{\mathcal{C}}$ (with cluster factors $\lvert u_{V_k}\rangle := \bigotimes_{v\in V_k}\lvert u_v\rangle$):
1. Every internal edge $e \in E(V_k)$ within a cluster $V_k$ generates a purely tangential direction in $T_m\mathcal{M}_{\mathcal{C}}$:
$$
-i[h_e, m] \in T_m \mathcal{M}_{\mathcal{C}}, \qquad Q_{m,\mathcal{C}}\bigl(-i[h_e, m]\bigr) = 0.
$$
2. The global cluster normal leakage rate $\nu_{\mathrm{global},\mathcal{C}}(m) = \lVert Q_{m,\mathcal{C}}(-i[H, m])\rVert_1$ satisfies the exact Pythagorean cut-edge sum:
$$
\nu_{\mathrm{global},\mathcal{C}}^2(m) = \sum_{e\in E_{\mathrm{cut}}(\mathcal{C})} \nu_e^2(m),
$$
where $\nu_e(m) = \lVert Q_{e, m_e}(-i[h_e, m_e])\rVert_1$ is the two-site normal rate on edge $e$. Consequently, at any site-factorized pure state $m\in\mathcal{M}$, selecting a $K$-cluster partition $\mathcal{C}$ that minimizes instantaneous cluster normal leakage $\nu_{\mathrm{global},\mathcal{C}}(m)$ is equivalent to the weighted minimum $K$-cut problem on $G$ with edge capacities $c(e)=\nu_e^2(m)$, with the same declared nonempty-cluster, connectivity or balance constraints, if any. For $K=2$ without extra constraints this is the usual minimum cut.

*Proof.* Decompose each single-site Hilbert space as $\mathcal{H}_v = \mathbb{C}\lvert u_v\rangle \oplus \lvert u_v\rangle^\perp$ and each cluster Hilbert space as $\mathcal{H}_{V_k} = \mathbb{C}\lvert u_{V_k}\rangle \oplus \lvert u_{V_k}\rangle^\perp$.
An internal edge $e=\{u,w\} \subset V_k$ acts solely within $\mathcal{H}_{V_k}$, so $-i[h_e, m] = (-i[h_e, \lvert u_{V_k}\rangle\langle u_{V_k}\rvert]) \otimes \bigotimes_{j\ne k} \lvert u_{V_j}\rangle\langle u_{V_j}\rvert \in T_m \mathcal{M}_{\mathcal{C}}$ and $Q_{m,\mathcal{C}}(-i[h_e, m]) = 0$.

Now let $e = \{u,w\} \in E_{\mathrm{cut}}(\mathcal{C})$ be a cut edge with $u \in V_k$ and $w \in V_l$ ($k\ne l$). Because $m = \bigotimes_{v\in V}\lvert u_v\rangle\langle u_v\rvert$ is site-factorized and $h_e$ acts as the identity on $(V_k\setminus\{u\})\cup(V_l\setminus\{w\})$, the cluster normal projection on $V_k\cup V_l$ acts strictly on the two endpoint factors $\{u,w\}$:
$$
\begin{aligned}
&(I_{V_k} - \lvert u_{V_k}\rangle\langle u_{V_k}\rvert)\otimes (I_{V_l} - \lvert u_{V_l}\rangle\langle u_{V_l}\rvert)\bigl(h_e\lvert u_{V_k}u_{V_l}\rangle\bigr)\\
&\quad = \bigl((I_u - \lvert u_u\rangle\langle u_u\rvert)\otimes(I_w - \lvert u_w\rangle\langle u_w\rvert)h_e\lvert u_u u_w\rangle\bigr)\otimes \lvert u_{(V_k\cup V_l)\setminus\{u,w\}}\rangle.
\end{aligned}
$$
Embedding into the full Hilbert space $\mathcal{H}_V$, the excitation vector $\chi_e = \widetilde{\chi}_e \otimes \lvert u_{V\setminus\{u,w\}}\rangle$ has both endpoints $u,w$ in their orthogonal complements $\lvert u_u\rangle^\perp \otimes \lvert u_w\rangle^\perp$ and every other site $v \notin \{u,w\}$ in its unexcited state $\lvert u_v\rangle$, with $2\lVert\chi_e\rVert = 2\lVert\widetilde{\chi}_e\rVert = \nu_e(m)$.
For any two distinct cut edges $e \ne e'$ in $E_{\mathrm{cut}}(\mathcal{C})$—including two cut edges that cross between the *same* pair of clusters $(V_k, V_l)$—the two-element endpoint sets $e=\{u,w\}$ and $e'=\{u',w'\}$ are distinct, so there is at least one site $v \in e\triangle e'$ at which one excitation vector lies in $\lvert u_v\rangle^\perp$ while the other lies in $\mathbb{C}\lvert u_v\rangle$. Hence $\langle \chi_e, \chi_{e'}\rangle = 0$ for all $e \ne e' \in E_{\mathrm{cut}}(\mathcal{C})$.
By the rank-2 pure-state normal decomposition of Proposition 5.11, $Q_{m,\mathcal{C}}(-i[H,m]) = -i(\lvert\chi_{\mathrm{global}}\rangle\langle u_V\rvert - \lvert u_V\rangle\langle\chi_{\mathrm{global}}\rvert)$ where $\chi_{\mathrm{global}} = \sum_{e\in E_{\mathrm{cut}}(\mathcal{C})} \chi_e$, so $\nu_{\mathrm{global},\mathcal{C}}^2(m) = 4\lVert\chi_{\mathrm{global}}\rVert^2 = 4\sum_{e\in E_{\mathrm{cut}}(\mathcal{C})}\lVert\chi_e\rVert^2 = \sum_{e\in E_{\mathrm{cut}}(\mathcal{C})}\nu_e^2(m)$. $\square$

**Remark 5.10.B.1 (Counterexample for intra-cluster entangled states).** The hypothesis that $m$ is site-factorized ($m\in\mathcal{M}$) cannot be weakened to arbitrary pure cluster-product states $m = \bigotimes_{k=1}^K \lvert u_{V_k}\rangle\langle u_{V_k}\rvert \in \mathcal{M}_{\mathcal{C}}$ when two or more cut edges connect the same pair of clusters. Indeed, take four qubits partitioned into two clusters $V_1=\{1,2\}$ and $V_2=\{3,4\}$ in the intra-cluster Bell state $\lvert u_{V_1}\rangle = \lvert\Phi^+\rangle_{12} = \frac{\lvert 00\rangle+\lvert 11\rangle}{\sqrt{2}}$ and $\lvert u_{V_2}\rangle = \lvert\Phi^+\rangle_{34} = \frac{\lvert 00\rangle+\lvert 11\rangle}{\sqrt{2}}$, with two cut edges $e_1=\{1,3\}$ ($h_{e_1}=Z_1\otimes Z_3$) and $e_2=\{2,4\}$ ($h_{e_2}=Z_2\otimes Z_4$). Because $Z_1\lvert\Phi^+\rangle_{12} = Z_2\lvert\Phi^+\rangle_{12} = \lvert\Phi^-\rangle_{12} \in \lvert u_{V_1}\rangle^\perp$ and $Z_3\lvert\Phi^+\rangle_{34} = Z_4\lvert\Phi^+\rangle_{34} = \lvert\Phi^-\rangle_{34} \in \lvert u_{V_2}\rangle^\perp$, the two distinct cut edges produce the **exact same** cluster excitation vector:
$$
\chi_{e_1} = \chi_{e_2} = \lvert\Phi^-\rangle_{12}\otimes\lvert\Phi^-\rangle_{34}.
$$
Thus $\chi_{\mathrm{global}} = \chi_{e_1} + \chi_{e_2} = 2\lvert\Phi^-\rangle_{12}\otimes\lvert\Phi^-\rangle_{34}$, yielding $\nu_{\mathrm{global},\mathcal{C}}^2 = 4\lVert\chi_{\mathrm{global}}\rVert^2 = 16$, whereas $4(\lVert\chi_{e_1}\rVert^2 + \lVert\chi_{e_2}\rVert^2) = 8$ (and if $h_{e_2} = -Z_2\otimes Z_4$, the two cut edges destructively interfere to give $\nu_{\mathrm{global},\mathcal{C}}^2 = 0 \ne 8$; moreover, on the maximally mixed two-site marginals $\rho_{13}=\rho_{24}=I_4/4$, the two-site rates $\nu_{e_i}(\rho_{e_i})$ vanish). Site factorization eliminates this intra-cluster entanglement transfer channel and ensures that distinct cut edges excite orthogonal two-site subspaces.

### 5.11 Retraction residual and distance to the nearest product

The product of the marginals is a canonical retraction, but need not be a
nearest product in trace norm. On a finite tensor product of $k$ local Hilbert
spaces let $\mathcal M$ be the compact set of product density matrices and set
$$
d_{\mathcal M}(\rho)=\min_{\sigma\in\mathcal M}\lVert \rho-\sigma\rVert_1,
\qquad D_\Pi(\rho)=\lVert \rho-\Pi\rho\rVert_1.
$$
All distances here use the raw trace norm; divide both by two for trace distance.
The following comparison does not assert a sharp constant.

**Theorem 5.9 (metric comparison and first-order optimality).** For every density
matrix on $k$ factors,
$$
d_{\mathcal M}(\rho)\le D_\Pi(\rho)\le(k+1)d_{\mathcal M}(\rho).
$$
At a full-rank product $m=\bigotimes_jm_j$, suppose
$\rho(t)=m+tL+O(t^2)$ in trace norm, with $L$ Hermitian and traceless and
$t\downarrow0$. Define the real tangent space and its retraction projection by
$$
\begin{aligned}
T_m&=\left\{\sum_jm_{<j}\otimes v_j\otimes m_{>j}:
                 v_j=v_j^*,\ \operatorname{Tr}v_j=0\right\},\\
PL&=\sum_jm_{<j}\otimes\operatorname{Tr}_{\ne j}L\otimes m_{>j},
\qquad Q=I-P.
\end{aligned}
$$
Then
$$
\begin{aligned}
d_{\mathcal M}(\rho(t))&=t\mu+O(t^2),
&\mu&=\inf_{v\in T_m}\lVert L-v\rVert_1,\\
D_\Pi(\rho(t))&=t\nu+O(t^2),
&\nu&=\lVert QL\rVert_1,\\
\mu&\le\nu\le\lVert Q\rVert_{1\to1}\mu.
\end{aligned}
$$
The induced norm of $Q$ is taken on the Hermitian trace-zero space. The optimal
coefficient has the dual certificate
$$
\mu=\max\left\{\operatorname{Tr}(WL): W=W^*,\ \lVert W\rVert_\infty\le1,
                  \ \operatorname{Tr}(Wv)=0\ \text{for every }v\in T_m\right\}.
$$

*Proof.* For any product $\sigma=\bigotimes_j\sigma_j$, telescoping the tensor
product and using marginal contraction gives
$$
\lVert \Pi\rho-\sigma\rVert_1\le\sum_j\lVert \rho_j-\sigma_j\rVert_1
                    \le k\lVert \rho-\sigma\rVert_1.
$$
The triangle inequality and minimization establish the finite comparison; the other
direction uses $\Pi\rho\in\mathcal M$.

A minimizer $\sigma(t)=\bigotimes_j\sigma_j(t)$ exists by compactness. Since
$m$ is an admissible competitor, $\lVert \sigma(t)-m\rVert_1=O(t)$. Thus every
$\Delta_j(t)=\sigma_j(t)-m_j$ is $O(t)$, and the finite product expansion is
$$
\sigma(t)=m+\sum_jm_{<j}\otimes\Delta_j(t)\otimes m_{>j}+O(t^2).
$$
The linear term lies in $T_m$, uniformly giving
$d_{\mathcal M}(\rho(t))\ge t\mu-O(t^2)$. This lower argument works at
boundary products too. At full rank, for any fixed $v\in T_m$ represented by
$v_j$, all $m_j+tv_j$ are densities for sufficiently small $t$. Their product
is $m+tv+O(t^2)$. A minimizing tangent vector exists in this finite-dimensional
closed subspace, yielding the matching upper bound. Expanding $\Pi\rho(t)$
gives the formula for $\nu$. Since $PL\in T_m$ and $Qv=0$ on $T_m$,
$\mu\le\nu$ and $\lVert QL\rVert_1\le\lVert Q\rVert\lVert L-v\rVert_1$. Finally, the
finite-dimensional Hahn--Banach distance formula and Hermitian trace/operator
norm duality give the displayed maximum. $\square$

Full rank is used for the physical upper tangent curve. An arbitrary
rank-deficient mixed product requires its feasible tangent cone; the theorem
must not be transferred to that boundary by dropping this premise. The pure
Hamiltonian case has a separate certificate below.

**Proposition 5.10 (a strict mixed-state distortion family).** Put
$r_p=\operatorname{diag}(p,1-p)$, $r_q=\operatorname{diag}(q,1-q)$, with
$0<p,q<1$, and evolve $r_p\otimes r_q$ under $H=X\otimes Z$. With
$a=1-2p$ and $b=2q-1$,
$$
L=aY\otimes Zr_q,\quad PL=abY\otimes r_q,\quad
QL=2aq(1-q)Y\otimes Z.
$$
Consequently
$$
\mu=4|a|\min(q,1-q),\qquad \nu=8|a|q(1-q).
$$
For $p\ne1/2$ their ratio is $2\max(q,1-q)$, approaching $2$ within the
full-rank family. This is an example family, not a sharp bound over all states.

*Proof.* For $q\ge1/2$ take the primal tangent vector
$v=aY\otimes r_q$ and the dual witness
$$
W=\operatorname{sign}(a)Y\otimes
       \operatorname{diag}\bigl((1-q)/q,-1\bigr).
$$
It has operator norm at most one. It annihilates $v_A\otimes r_q$ because
the second-factor pairing is zero, and $r_p\otimes v_B$ because
$\operatorname{Tr}(Yr_p)=0$. Direct calculation gives
$\lVert L-v\rVert_1=\operatorname{Tr}(WL)=4|a|(1-q)$. For $q<1/2$ use
$v=-aY\otimes r_q$ and
$W=\operatorname{sign}(a)Y\otimes\operatorname{diag}(1,-q/(1-q))$.
Theorem 5.9 and the spectrum of $Y\otimes Z$ establish the assertion. If
$p=1/2$ both rates vanish and the ratio is undefined. At $p=q=3/4$ the
certificate gives $\mu=1/2$ but $\nu=3/4$. $\square$

### 5.11.1 Feasible tangent cones at rank-deficient boundaries and cluster refinement monotonicity

When analyzing rank-deficient quantum states at the boundary of the state space, two distinct tangent cones must be carefully distinguished:
1. *Ambient state-space tangent cone $T_{\mathcal D}^{\mathrm{feas}}(m)$:*
   For an arbitrary rank-deficient mixed state $m$ on the boundary of the ambient state space $\mathcal D := \mathcal S(\mathcal H) = \{\rho \ge 0, \operatorname{Tr}\rho = 1\}$, the cone of first-order variations preserving positivity is
   $$
   T_{\mathcal D}^{\mathrm{feas}}(m) = \left\{ v = v^\dagger, \; \operatorname{Tr} v = 0 : P_0 v P_0 \ge 0 \right\},
   $$
   where $P_0=I-\operatorname{supp}(m)$ projects onto $\ker(m)$.
   This is the closed first-order (Bouligand) tangent cone: a direction may
   require a curve with a second-order correction, not the straight ray
   $m+tv$.
   For an arbitrary traceless Hermitian variation $L$, its trace-norm distance to $T_{\mathcal D}^{\mathrm{feas}}(m)$ is given by the exact spectral formula:
   $$
   \operatorname{dist}_1(L, T_{\mathcal D}^{\mathrm{feas}}(m)) = 2 \left\lVert (P_0 L P_0)^- \right\rVert_1,
   $$
   where $(A)^- = \frac{|A| - A}{2}$ denotes the negative part of self-adjoint operator $A$.
   To prove the distance, put $N=(P_0LP_0)^-$ and $\beta=\operatorname{Tr}N$.
   Then $v=L+N-\beta m$ lies in the cone, and
   $\|L-v\|_1=2\beta$ because $N$ and $m$ have orthogonal supports.
   If $P_-$ is the negative spectral projection of $P_0LP_0$, the contraction
   $W=I-2P_-$ has $\operatorname{Tr}(Wv')\le0$ for every cone element $v'$
   and $\operatorname{Tr}(WL)=2\beta$, proving the matching lower bound.
   This is first-order positivity feasibility in the ambient state space;
   it does *not* measure preservation of factorization.

2. *Product manifold tangent cone $T_{\mathcal M}^{\mathrm{feas}}(m)$:*
   On the product manifold $\mathcal M$, first-order variations are constrained to local product tangent directions:
   $$
   T_{\mathcal M}^{\mathrm{feas}}(m) = \left\{ v = \sum_j m_{<j}\otimes v_j \otimes m_{>j} : v_j = v_j^\dagger, \; \operatorname{Tr} v_j = 0, \; P_0^{(j)} v_j P_0^{(j)} \ge 0 \right\}.
   $$
   In particular, $\operatorname{dist}_1(L, T_{\mathcal M}^{\mathrm{feas}}(m))$ *cannot* be evaluated by summing local marginal projections $P_0^{(j)} \operatorname{Tr}_{\ne j}(L) P_0^{(j)}$. A marginal-sum formula examines only local partial traces and entirely misses emerging correlations.

**Exact two-qubit entangling counterexample.**
Consider the pure product state $m = |00\rangle\langle 00|$, entangling Hamiltonian $H = X \otimes X$, and dynamical velocity $L = -i[H, m] = -i(|11\rangle\langle 00| - |00\rangle\langle 11|)$.
Both local partial traces vanish identically: $\operatorname{Tr}_A(L) = 0$ and $\operatorname{Tr}_B(L) = 0$.
The ambient cone distance is $\operatorname{dist}_1(L, T_{\mathcal D}^{\mathrm{feas}}(m)) = 0$ because $P_0 = I - |00\rangle\langle 00|$ gives $P_0 L P_0 = 0$ ($L$ connects $\operatorname{supp}(m)$ exclusively to the orthogonal subspace $|11\rangle$).
However, every product tangent has the form $v = v_A \otimes |0\rangle\langle 0| + |0\rangle\langle 0| \otimes v_B$, for which the matrix element $\langle 11| v |00\rangle = 0$.
The actual distance to the product tangent cone is $\operatorname{dist}_1(L, T_{\mathcal M}^{\mathrm{feas}}(m)) = 2$.
This distance is certified with zero duality gap by the dual witness $W = L$, which satisfies $\lVert W\rVert_\infty = 1$, $\operatorname{Tr}(W v) = 0$ for all $v \in T_{\mathcal M}$, and $\operatorname{Tr}(W L) = \operatorname{Tr}(L^2) = 2$.
The finite instance above has an exact written primal/dual certificate.
While numerical algorithms (such as the optimization routines in `code/feasible_tangent_cone.py`) compute candidate product-cone projections, exact lower and upper bounds are certified through independent primal and dual feasibility verifiers.

**Cluster product manifolds and refinement monotonicity.** Let $V = \bigsqcup_{k=1}^K V_k$ be a partition $\mathcal C$ of the lattice vertices into disjoint clusters, and define the cluster product manifold:
$$
\mathcal M_{\mathcal C} = \left\{ \bigotimes_{k=1}^K \rho_{V_k} : \rho_{V_k} \in \mathcal S(\mathcal H_{V_k}) \right\}.
$$
If partition $\mathcal C_2$ is a refinement of partition $\mathcal C_1$ (denoted $\mathcal C_1 \preceq \mathcal C_2$, meaning every cluster in $\mathcal C_2$ is contained within a cluster in $\mathcal C_1$), then $\mathcal M_{\mathcal C_2} \subseteq \mathcal M_{\mathcal C_1}$.
Consequently, the feasible trace-norm distance satisfies refinement monotonicity:
$$
\operatorname{dist}_1(L, T_{\mathcal M_{\mathcal C_1}}^{\mathrm{feas}}(m)) \le \operatorname{dist}_1(L, T_{\mathcal M_{\mathcal C_2}}^{\mathrm{feas}}(m)).
$$
Cluster merging cannot increase the distance, by inclusion of the admissible
tangent cones. Absorbing an interaction does not imply a strict decrease:
for $m=|00\rangle\langle00|$ and $H=Z\otimes Z$, the velocity and both
distances are zero before and after merging. Strictness requires an actual
distance gap. For the site-factorized pure-state rate in Theorem 5.10.B,
strictness is equivalent to a positive sum of squared rates on the absorbed
cut edges; this criterion is not a theorem for arbitrary mixed-state cones.

### 5.12 Pure excitation sectors, optimality, and declared Born weights

Let $u=\bigotimes_vu_v$ be a normalized pure product, $m=|u\rangle\langle u|$,
and $H$ a finite one-/two-local Hermitian Hamiltonian. Combine all terms on the
same unordered pair into $h_e$ before defining any sector mass. For
$e=\{a,b\}$, let $\chi_e$ be the vector obtained by applying
$$
\bigl((I-|u_a\rangle\langle u_a|)\otimes
      (I-|u_b\rangle\langle u_b|)\bigr)h_e
$$
to $u_a\otimes u_b$ and tensoring back the unchanged factors. Put
$\chi=\sum_e\chi_e$.

**Theorem 5.11 (orthogonal sectors and pure metric optimality).** Distinct pairs
have orthogonal $\chi_e$, even when the pairs share a vertex. The global
product-retraction normal vector and rates satisfy
$$
\begin{aligned}
n_{\mathrm{global}}&=-i\bigl(|\chi\rangle\langle u|
                         -|u\rangle\langle\chi|\bigr),\\
\nu_{\mathrm{global}}&=2\lVert \chi\rVert,\qquad
\nu_e=2\lVert \chi_e\rVert,\qquad
\nu_{\mathrm{global}}^2=\sum_e\nu_e^2.
\end{aligned}
$$
For this Hamiltonian curve,
$$
d_{\mathcal M}(\rho(t))=D_\Pi(\rho(t))+O(t^2)
                     =t\nu_{\mathrm{global}}+O(t^2),\qquad t\downarrow0.
$$
These global $O(t^2)$ constants are for a fixed finite volume; no uniform
in-volume time window follows from this identity.

*Proof.* Decompose each factor as $\mathbb Cu_v\oplus u_v^\perp$. The tensor
space is an orthogonal direct sum labeled by its excited-site subset. A
one-/two-local $Hu$ has only empty, singleton and pair sectors. The empty
sector cancels in $-i[H,m]$, and $P$ removes exactly its singleton terms.
Different pair labels give orthogonal sectors: a site in the symmetric
difference supplies an orthogonal tensor factor. Only $h_e$ reaches the
pair-$e$ sector, also establishing the edge rate using §5.3.1. On
$\operatorname{span}\{u,\chi\}$ the normal vector has eigenvalues
$\pm\lVert \chi\rVert$ and it is zero on the orthogonal complement.

If $\chi\ne0$, put $\eta=\chi/\lVert \chi\rVert$ and
$W=-i(|\eta\rangle\langle u|-|u\rangle\langle\eta|)$. Then
$\lVert W\rVert_\infty=1$, $\operatorname{Tr}(WL)=2\lVert \chi\rVert$, and $W$
annihilates every product tangent direction: such a direction changes at most
one factor, whereas $W$ couples the empty sector to pair sectors. The lower
minimizer argument of Theorem 5.9 is valid at this boundary and yields
$d_{\mathcal M}\ge t\nu_{\mathrm{global}}-O(t^2)$. The physical product
$\Pi\rho(t)$ supplies the upper bound. If $\chi=0$, that upper bound is
$O(t^2)$ and the same conclusion follows. $\square$

There is an exact arithmetic certificate for the squared rates without taking
square roots. When the initial pure projectors and interactions have entries
in $\mathbb Q(i)$, put $r_{ab}=|u_au_b\rangle\langle u_au_b|$ and
$R_{ab}=(I-r_a)\otimes(I-r_b)$. Then
$$
w_e=\lVert \chi_e\rVert^2=\operatorname{Tr}(r_{ab}h_eR_{ab}h_e)\in\mathbb Q_{\ge0},
\qquad \nu_e^2=4w_e,\quad \nu_{\mathrm{global}}^2=4\sum_ew_e.
$$
Hermiticity and positivity identify the rational trace as a nonnegative squared
norm. A negative value in such a replay is a failed input or calculation, not
a physical rate. Terms on the same edge can interfere and cancel, so their
individual squared masses cannot be summed before their operators are combined.
For $|000\rangle$ and
$H=X_1X_2+2X_1X_3+3X_2X_3$, the sector Gram matrix is
$\operatorname{diag}(1,4,9)$, local rates are $(2,4,6)$ and the global squared
rate is $56$.

To connect this result to the supplied normalization construction [18], the
weight assignment must be declared: use $w_e=\nu_e^2/4$, and when
$W_0=\sum_ew_e>0$ set
$$
p_e=\frac{w_e}{W_0}=\frac{\nu_e^2}{\sum_f\nu_f^2}.
$$
This is a normalized profile of the orthogonal excitation masses in the
already imported Hilbert space. It need not be the profile obtained by normalizing
the original additive tally: $C'(0+)=\sum_e\nu_e=2\sum_e\sqrt{w_e}$.
The two profiles coincide when all nonzero rates are equal.
The triangle example gives $p=(1/14,2/7,9/14)$ and additive slope $12$.
When $W_0=0$, the rate identity still holds but the profile is undefined.
Normalization alone neither selects these weights nor establishes Born uniqueness,
a Hilbert lift, a measurement interpretation, or a Gleason premise. This is
consistent with the normalization nonselection result of the witnessed
difference programme [12].

Nor do the masses determine the normal vector. For fixed $u$ and vectors
$\chi,\chi'\perp u$,
$$
\lVert n(\chi)-n(\chi')\rVert_1=2\lVert \chi-\chi'\rVert.
$$
Changing a sector's physical relative phase can preserve every $w_e$ while
changing the normal direction. Rephasing a basis vector together with its
coordinate is only a representation change and does not supply such a witness.

### 5.13 Limits of a global trace-norm versus edge-sum comparison

Write $D_{\mathrm{global}}=\lVert \rho-\bigotimes_v\rho_v\rVert_1$ and
$C=\sum_{e\in E}D_e$. Marginal contraction always gives
$$
\max_eD_e\le D_{\mathrm{global}}\le2,
\qquad C\le |E|D_{\mathrm{global}}.
$$
The size factor cannot be removed without additional assumptions, and even vanishing pair defects can
miss the global defect.

**Proposition 5.12 (two failures of unrestricted equivalence).** There is no
positive size-independent $c$ with $D_{\mathrm{global}}\ge cC$ for all finite
product-state one-/two-local evolutions, even with $g=1$ and a fixed arbitrarily
small positive time. There is also no finite $K$ with
$D_{\mathrm{global}}\le KC$ at unrestricted times in that class.

*Proof.* Take $M$ disjoint qubit pairs, initial state $|00\rangle$ per pair,
and $H=\sum_eX_aX_b$. For $0<t<\pi/4$, the exact two-qubit computation of
§6.1 gives
$$
D_e(t)=\sin(2t)+\tfrac12\sin^2(2t)>0.
$$
Thus $C=MD_e(t)$ while $D_{\mathrm{global}}\le2$. This establishes the first
failure at any such fixed time. At zero the corresponding slopes are $2M$
and $2\sqrt M$, by Theorem 5.11.

For the second, take the five-cycle, $H=\sum_{j\bmod5}Z_jZ_{j+1}$, initial
state $|+\rangle^{\otimes5}$ and $t=\pi/4$. Up to a common phase the state is
$$
|\psi\rangle=2^{-5/2}\sum_{b\in\{0,1\}^5}
       (-1)^{\sum_jb_j+\sum_jb_jb_{j+1}}|b\rangle.
$$
Every two-site marginal is $I_4/4$. Here is a direct cancellation check:
for two distinct retained strings let $d$ be their binary difference,
supported on at most two sites. In the partial-trace sum the phase difference
has, at each discarded vertex $v$, linear coefficient
$d_{v-1}+d_{v+1}$ modulo two. A single changed vertex in a five-cycle has a
neighbor outside the retained pair with coefficient one; two changed vertices,
whether adjacent or nonadjacent, also have an outside neighbor adjacent to
exactly one of them. Summing that bit cancels the off-diagonal entry. Diagonal
entries are $1/4$. One-site marginals are therefore $I_2/2$, and
$$
C=0,\qquad D_{\mathrm{global}}
 =\bigl\lVert |\psi\rangle\langle\psi|-I_{32}/32\bigr\rVert_1=31/16.
$$
The last spectrum consists of $31/32$ once and $-1/32$ thirty-one times.
All entries of this density and its marginals are rational. $\square$

This settles the unrestricted equivalence question between $D_{\mathrm{global}}$ and $C$ negatively.
The cycle time is outside the certified small-time window of Theorem 5.1;
it does not refute every additional near-zero upper bound, nor the matching
and total-correlation density result of [5]. An intensive edge
average and a bounded global distinguishability are different quantities.

### 5.14 Support components and connected cumulants

Fix reference densities $r_j$ and let $E_j$ trace out site $j$ and reinsert
$r_j$ in its position. These are commuting idempotent linear maps. Define
$$
T_S=\prod_{j\in S}(I-E_j)\prod_{j\notin S}E_j.
$$

**Proposition 5.13 (reference-support decomposition).** The $T_S$ are
idempotents, $T_ST_R=0$ for $S\ne R$, and $\sum_ST_S=I$. On Hermitian
trace-zero directions at $m=\bigotimes_jr_j$,
$$
P=\sum_{|S|=1}T_S,\qquad Q=\sum_{|S|\ge2}T_S.
$$
If $r_j=\rho_j$, then
$$
\rho-\Pi\rho=\sum_{|S|\ge2}T_S\rho.
$$

*Proof.* Expand $\prod_j(E_j+(I-E_j))$; unequal subsets have a factor
$E_j(I-E_j)=0$. Moreover $T_\varnothing Z=\operatorname{Tr}(Z)m$, and
$T_{\{j\}}Z$ inserts
$\operatorname{Tr}_{\ne j}Z-\operatorname{Tr}(Z)r_j$ into factor $j$.
These formulas give every assertion. The references remain fixed when
composing the projectors. $\square$

These projectors are algebraically complementary; they need not be orthogonal
or make the trace norm additive. Their highest component need not represent a
connected correlation. For independent Bell pairs
$\rho=B_{12}\otimes B_{34}$,
$$
T_{\{1,2,3,4\}}\rho=(B_{12}-I_4/4)\otimes(B_{34}-I_4/4)\ne0,
\qquad \lVert T_{\{1,2,3,4\}}\rho\rVert_1=9/4.
$$
The connected four-site cumulant instead vanishes.

For a nonempty site set $S$ define the operator cumulant
$$
\kappa_S(\rho)=\sum_{\pi\in\operatorname{Part}(S)}
       (-1)^{|\pi|-1}(|\pi|-1)!\bigotimes_{B\in\pi}\rho_B,
$$
where tensors are always restored to the original site order. For a pair
this is $F_{ab}$; for three sites it is
$$
\rho_{abc}-\rho_{ab}\otimes\rho_c-\rho_{ac}\otimes\rho_b
-\rho_{bc}\otimes\rho_a+2\rho_a\otimes\rho_b\otimes\rho_c.
$$
It measures connected correlation, including classical correlation; nonzero
cumulant is not by itself an entanglement witness.

To establish cancellation under independent splitting without assuming commuting
matrices, introduce a square-free support algebra. Its coefficients on $A$
are operators on $A$; multiply coefficients by their reordered tensor product
if supports are disjoint and by zero if supports overlap. This is a commutative
algebra because actual products use disjoint factors. Its positive-support
ideal is nilpotent. In
$M=\sum_{A\subseteq S}\rho_Az_A$, $\rho_\varnothing=1$, the coefficient
of $z_S$ in the finite series $\log M$ is precisely $\kappa_S$: a partition
with $\ell$ blocks occurs $\ell!$ times in the $\ell$th logarithm term.
If $\rho_S$ splits across a nontrivial partition, $M$ factors into the
component series. The logarithm is their sum and has no term crossing those
components. Thus $\kappa_S=0$ whenever $S$ crosses independent components.

Let $G$ be the graph of allowed two-site interactions, and let
$\tau_G(S)$ be the minimum number of edges in a connected subgraph containing
$S$, allowing Steiner vertices. Set $\tau_G(S)=\infty$ if no such subgraph
exists. Let $(k)_j=k(k+1)\cdots(k+j-1)$, with $(k)_0=1$, and set
$$
a_k=\sum_{\pi\in\operatorname{Part}(k)}(|\pi|-1)!,\qquad
b_k=\sum_{\pi\in\operatorname{Part}(k)}|\pi|!.
$$
For $k=1,\ldots,6$ these are respectively
$(1,2,6,26,150,1082)$ and $(1,3,13,75,541,4683)$.

**Theorem 5.14 (connected onset, locality and all-order remainder).** For a
finite one-/two-local Hamiltonian, a product initial state, and $|S|=k\ge2$,
$$
\kappa_S^{(j)}(0)=0\quad(j<\tau_G(S)),\qquad \tau_G(S)\ge k-1.
$$
If $j\ge k-1$, its $j$th derivative depends only on the initial factors and
Hamiltonian terms in the induced radius-$(j-k+1)$ neighborhood of $S$.
At every real time,
$$
\lVert \kappa_S^{(j)}(t)\rVert_1\le a_k(2g)^j(k)_j.
$$
Writing $P_{S,J}(t)=\sum_{j=0}^Jt^j\kappa_S^{(j)}(0)/j!$, for $J\ge0$,
$$
\lVert \kappa_S(t)-P_{S,J}(t)\rVert_1
 \le a_k\binom{k+J}{J+1}(2g|t|)^{J+1}.
$$
The same bound controls the difference of their trace norms. In particular,
for finite $\tau=\tau_G(S)$,
$$
\lVert \kappa_S(t)\rVert_1\le a_k\binom{k+\tau-1}{\tau}(2g|t|)^\tau.
$$
If $\tau=\infty$, the cumulant is identically zero at every time.

*Proof.* Give each Hamiltonian term its own real parameter. The $j$th state
jet, and hence the $j$th cumulant jet, is a homogeneous degree-$j$ polynomial
in those parameters. For a particular monomial set every absent parameter to
zero; its coefficient is unchanged. If the remaining interaction graph splits
$S$, the corresponding evolution factorizes and the cumulant vanishes for all
parameter choices. Its monomial coefficient is therefore zero. If $S$ is in
one component but the monomial also uses a parameter in another component,
the state reduced to $S$ is independent of that parameter, again giving zero.
Thus any surviving monomial uses one connected component containing all of
$S$, with at most $j$ distinct two-site edges. This establishes onset. That component
has at most $j+1$ vertices. A vertex at distance $r$ from $S$ in it requires
$r$ distinct vertices outside the $k$ sites of $S$, so $k+r\le j+1$.
The ambient distance is no larger. This establishes the stated induced-neighborhood
locality, including one-local terms, which consume degree without adding edges.
Connectivity is necessary, not sufficient: commutation or cancellation can
postpone onset further.

For any partition $\pi$, Lemma 5.4 and the multinomial product rule bound its
$j$th derivative by
$$
(2g)^j\sum_{\sum_Bj_B=j}\frac{j!}{\prod_Bj_B!}
                   \prod_{B\in\pi}(|B|)_{j_B}=(2g)^j(k)_j.
$$
The equality is coefficient extraction from
$\prod_B(1-z)^{-|B|}=(1-z)^{-k}$. Sum the absolute partition coefficients
to obtain $a_k$. Integral Taylor remainder gives the displayed estimate.
Set $J=\tau-1$ and use the zero jets for the onset bound. Disconnected graph
components factorize at every time, establishing the infinite-$\tau$ case.
$\square$

At $k=2$, $a_2=2$ and the remainder is exactly the coefficient in Theorem 5.5.
For the three-site chain
$H=X_1X_2+Y_2X_3$ and $|000\rangle$, the pair and triple first jets vanish,
whereas
$$
\kappa_{13}''(0)=2i|01\rangle\langle10|-2i|10\rangle\langle01|,
\qquad \lVert \kappa_{13}''(0)\rVert_1=4,\quad
\lVert \kappa_{123}''(0)\rVert_1=8.
$$
Both have Steiner length two and attain the permitted quadratic onset.

For fixed $k$ the onset estimate supplies short-time spatial decay: if
$q=2g|t|<r<1$, the generating-function bound gives
$$
\lVert \kappa_S(t)\rVert_1\le a_k(1-q/r)^{-k}r^{\tau_G(S)}.
$$
Indeed $\binom{k+\tau-1}{\tau}(q/r)^\tau\le(1-q/r)^{-k}$.
One can replace $\tau_G(S)$ by a smaller distance in this exponential
bound, but not automatically in the preceding polynomial-times-power bound,
which need not be monotone at small $\tau$. This is a short-time propagation
bound. Subdividing time does not extend its zero-jet proof to arbitrary times:
the state after the first interval is generally no longer product.

### 5.15 Fixed-support limits and connected-cumulant densities

For two densities on $S$, telescoping each partition product and contracting
marginals establishes the useful global Lipschitz estimate
$$
\lVert \kappa_S(\rho)-\kappa_S(\sigma)\rVert_1\le b_k\lVert \rho-\sigma\rVert_1,
\qquad \lVert \kappa_S(\rho)\rVert_1\le a_k.
$$
For a partition with $\ell$ blocks, the product difference has norm at most
$\ell\lVert \rho-\sigma\rVert_1$; multiplying by $(\ell-1)!$ and summing gives
$b_k$. The second inequality uses norm one for each density factor.
Consequently the fixed-support local thermodynamic limit of Theorem 5.7
immediately yields a cumulant limit uniformly on compact real-time intervals.
For $J\ge k-1$ and a finite volume $\Lambda$ containing the induced
radius-$(J-k+1)$ neighborhood of $S$, locality and the two Taylor remainders
also give the explicit estimate
$$
\lVert \kappa_S^\Lambda(t)-\kappa_S^\infty(t)\rVert_1
 \le2a_k\binom{k+J}{J+1}(2g_*|t|)^{J+1}.
$$
The stabilized coefficients pass to the limit. For $2g_*|t|<1$ the remainders
tend to zero and identify these coefficients as derivatives of the limit.
At arbitrary times convergence instead uses Theorem 5.7 and the Lipschitz
estimate, not extrapolation of the series beyond its useful radius.

**Theorem 5.15 (density for finitely many fixed shapes).** Assume a
translation-invariant locally finite graph on $\mathbb Z^d$, finite local
dimensions identified by translation, translation-covariant one-/two-site
interactions with $g_*<\infty$, and a translation-invariant product initial
state. Use compatible open-boundary cubes $\Lambda_L=\{-L,\ldots,L\}^d$.
Fix finitely many finite shapes $S_\alpha$, each of size at least two, and
nonnegative fixed weights $w_\alpha$. Then, uniformly on every $|t|\le T$,
$$
\begin{aligned}
\mathcal C_L(t)&=\frac1{|\Lambda_L|}\sum_\alpha w_\alpha
   \sum_{x:x+S_\alpha\subseteq\Lambda_L}
                  \lVert \kappa_{x+S_\alpha}^{\Lambda_L}(t)\rVert_1\\
&\longrightarrow \sum_\alpha w_\alpha\lVert \kappa_{S_\alpha}^\infty(t)\rVert_1.
\end{aligned}
$$

*Proof.* Exhaustion independence in Theorem 5.7 makes the limiting dynamics
translation covariant. Given an error tolerance and a compact time interval,
choose a finite neighborhood of each shape so that every volume containing
that neighborhood approximates its limit within the tolerance. The preceding
Lipschitz estimate transfers this to cumulant norms. Translation gives the
same bound for all translates whose chosen neighborhoods lie inside
$\Lambda_L$. Local finiteness and translation invariance give finitely many
edge displacements, and these neighborhoods are fixed finite sets. The
fraction of their translates crossing the cubic boundary tends to zero, while
the number of retained translates of each shape divided by $|\Lambda_L|$
tends to one. On the exceptional boundary translates use the uniform bound
$a_{|S_\alpha|}$. Sum the finitely many weighted errors. $\square$

This completes a fixed-shape density extension of §5.10 and a short-time
connected propagation estimate. An all-time spatial propagation estimate,
densities summing over unbounded support orders, and observer budgets growing
with volume require additional arguments and are not consequences of this
finite-shape theorem.

### 5.16 Finite onset or persistent zero for polynomial defects

The all-derivatives criterion in §5.8 has a finite replacement for each fixed
finite system. The object differentiated is the vector-valued residual, not
its norm, which need not be differentiable at zero.

**Theorem 5.16 (finite polynomial onset-or-invariance certificate).** Let $V$
and $W$ be finite-dimensional real or complex vector spaces, $\dim V=n$, let
$A:V\to V$ be linear, and let $f:V\to W$ be a polynomial of degree at most
$p\geq0$. Fix $m\in V$ with $f(m)=0$. Define
$$
 R(t)=f(e^{tA}m),\qquad
 \mathcal W_p=\bigoplus_{r=0}^{p}\operatorname{Sym}^{r}V,
 \qquad z_m=(1,m,m^{\odot2},\ldots,m^{\odot p}).
$$
On degree zero put $\mathcal L_0=0$, and on degree $r\geq1$ put
$$
 \mathcal L_r(v_1\odot\cdots\odot v_r)
 =\sum_{i=1}^{r}v_1\odot\cdots\odot Av_i\odot\cdots\odot v_r,
 \qquad \mathcal L=\bigoplus_{r=0}^{p}\mathcal L_r.
$$
There is a linear readout $O:\mathcal W_p\to W$ such that
$R(t)=Oe^{t\mathcal L}z_m$. Let
$$
 \mathcal C_m=\operatorname{span}\{\mathcal L^jz_m:j\geq0\},
 \qquad q(s)=s^\kappa+\sum_{i=0}^{\kappa-1}q_i s^i
$$
be the minimal polynomial of $\mathcal L|_{\mathcal C_m}$. Then
$$
 1\leq\kappa=\dim\mathcal C_m
 \leq\dim\mathcal W_p={n+p\choose p},
 \qquad
 \boxed{\quad R(t)\equiv0\ \Longleftrightarrow\
          R^{(j)}(0)=0\quad(0\leq j<\kappa).\quad}
$$
If $R$ is not identically zero, its first nonzero derivative has order
$$
 \boxed{\quad 1\leq m_{\mathrm{onset}}\leq\kappa-1.\quad}
$$
In particular, $\kappa=1$ and $f(m)=0$ force persistent zero.

*Proof.* Decompose $f=\sum_{r=0}^{p}f_r$ into homogeneous terms. In
characteristic zero, polarization gives linear maps
$O_r:\operatorname{Sym}^rV\to W$ with $f_r(v)=O_r(v^{\odot r})$.
The tensor product rule gives
$(e^{tA}m)^{\odot r}=e^{t\mathcal L_r}m^{\odot r}$; summing these
readouts gives $O$ and the displayed representation of $R$.

Write $z=z_m$. Its degree-zero coordinate is one, so $z\ne0$. The first
linear dependence in the Krylov sequence $z,\mathcal Lz,\ldots$ has the
form $q(\mathcal L)z=0$, with all earlier vectors independent. Multiplying
this relation by every power of $\mathcal L$ shows that these earlier
vectors span an invariant space containing the whole sequence. Thus their
number is $\dim\mathcal C_m=\kappa$. A polynomial annihilates $z$ if and
only if it annihilates $\mathcal C_m$, since $z$ is cyclic, establishing the
stated minimal-polynomial interpretation and dimension bound.

Put $b_j=R^{(j)}(0)=O\mathcal L^jz$. The full vector relation gives, for
every $j\geq0$,
$$
 b_{j+\kappa}=-\sum_{i=0}^{\kappa-1}q_i b_{j+i}.
$$
If $b_0,\ldots,b_{\kappa-1}$ vanish, induction makes every $b_j$ vanish.
The finite matrix exponential is entire, so
$R(t)=\sum_{j\geq0}b_jt^j/j!$ then vanishes for all real $t$ (and for all
complex $t$ after complexification). The converse follows by differentiation.
If $R$ is nonzero, one of these first $\kappa$ derivatives must be nonzero;
$f(m)=0$ excludes index zero. $\square$

**Certificate form and sharpness.** Minimality is useful for the shortest
state-space cutoff, but is not necessary for a valid finite test. Any supplied
monic polynomial $a$ of degree $K\geq1$ with $a(\mathcal L)z_m=0$ gives
the sufficient-and-necessary zero test on $0\leq j<K$ and, for nonzero $R$,
the upper bound $K-1$. Checking only a recurrence among reported zero outputs
does not establish that vector relation. An exact certificate contains the
model, polynomial readout, annihilator coefficients, and the jets
$O\mathcal L^jz_m$; the checker reconstructs the lift and replays the
relation and jets. To claim $K=\kappa$, it also checks independence of the
first $K$ cyclic vectors. The cutoff may exceed the minimal recurrence degree
of the output because $O$ can annihilate part of the cyclic space.

The upper bound is attained: with $V=\mathbb R$, $A=1$, $m=1$ and
$f(x)=(x-1)^p$ for $p\geq1$, $R(t)=(e^t-1)^p$ has onset $p$ and
$\kappa=p+1$. The unlifted generator has minimal polynomial of degree one,
so substituting that degree would give a false zero certificate. Even for
fixed degree $p=1$, nilpotent chains of growing dimension, observed at the
last coordinate, give arbitrarily late onset. No size-independent cutoff
follows from polynomial degree alone.

**Corollary 5.17 (pair defects and connected cumulants).** For a fixed finite
quantum system, use the real vector space of Hermitian matrices, of dimension
$n=d^2$ for global Hilbert dimension $d$, and the linear Liouvillian
$A(X)=-i[H,X]$. The pair readout
$$
 f_e(X)=\operatorname{Tr}_{e^c}X
       -(\operatorname{Tr}_{a^c}X)\otimes(\operatorname{Tr}_{b^c}X)
$$
is a polynomial of degree at most two on that vector space. For product
initial density $m$, $f_e(m)=0$. Consequently its residual $F_e(t)$ is either
identically zero or has onset at most $\kappa_e-1$, where
$\kappa_e\leq {d^2+2\choose2}$. Under the one-/two-local interaction
hypotheses of §5.8, a first nonzero jet supplied by this finite test can be
inserted directly into that section's remainder and leading-rate bounds.

For a fixed set $S$ of $k\geq2$ sites, the connected cumulant of §5.14 is
$$
 f_S(X)=\sum_{\pi\in\operatorname{Part}(S)}
          (-1)^{|\pi|-1}(|\pi|-1)!
          \bigotimes_{B\in\pi}\operatorname{Tr}_{B^c}X.
$$
Tensor factors are placed in the fixed site order. Each reduced operator is
linear in $X$, so this is a polynomial of degree at most $k$, and it vanishes
on the normalized product initial state. Theorem 5.16 applies with
$\kappa_S\leq {d^2+k\choose k}$. Under the additional product and one-/two-local
interaction hypotheses of Theorem 5.14, every nonzero cumulant therefore has
$$
 \boxed{\quad \tau_G(S)\leq m_{\mathrm{onset}}
                         \leq\kappa_S-1.\quad}
$$
Here $\tau_G(S)$ is the minimum number of edges of a connected interaction
subgraph spanning $S$. If no such subgraph exists, the independent-component
cancellation gives persistent zero. If finite $\tau_G(S)\geq\kappa_S$, the
lower-order vanishing already covers the entire cyclic cutoff and again
forces persistent zero. These conclusions concern the finite residual
operator; a norm or incomplete observer report cannot replace its jets.

*Proof.* The polynomial degree and initial-zero facts just established allow
Theorem 5.16. The lower bound and disconnected case are precisely the
cancellation statement of Theorem 5.14; combining the two bounds gives the
remaining assertions. $\square$

The cutoff depends on the declared finite model and can grow with global
Hilbert dimension. Finite coefficient locality in §5.14 does not supply an
annihilator uniform across growing systems, and the local limits of §§5.10
and 5.15 do not change this restriction. The exact rational implementation
`code/polynomial_onset.py` checks finite instances and rejects inexact scalars,
invalid annihilators and forged jets. It has a declared lift-dimension budget;
its execution is separate from this general written proof, which is not newly
mechanized in Lean.

**Prior art, positioning, and non-claim of lifting priority.** Polynomial lifting
and finite linear observability have established antecedents across dynamical systems
and mathematical control theory:
1. Classical Carleman linearization embeddings embed finite-dimensional polynomial
   differential equations into infinite-dimensional or truncated linear operator
   systems (Carleman [22]).
2. In data-driven dynamical systems and Koopman operator theory, exact finite linear
   representations and Koopman invariant subspaces are constructed via dictionary
   and polynomial lifting functions (Brunton et al. [21]).
3. Differential algebraic observability and Lie-derivative rank tests for polynomial
   and rational differential systems similarly provide finite criteria for state
   reconstructibility (e.g., Sedoglavic [23]; Villaverde et al. [24]).

*Non-claim of priority:* This monograph does not claim priority for the general
algebraic mechanism of symmetric-power / polynomial lifting or the finite
Krylov/cyclic observability of linear representations.

*Specific contribution:* The contribution of Theorem 5.16 and Corollary 5.17
consists in:
1. The application to non-product projection defects, non-equilibrium defect
   fields, and reduced state retractions under Hamiltonian and Liouvillian dynamics.
2. Reconstructible, machine-checkable certificates: Theorem 5.16 requires an
   annihilator of the full lifted state $z_m$ under $\mathcal L$, and derives the
   residual recurrence from this state-space identity. This distinction separates
   a vanishing truncated jet (which may vanish through order $\kappa-2$ before
   exhibiting nonzero onset) from persistent zero.
3. Integration with interaction locality: Corollary 5.17 binds the finite upper
   cyclic cutoff ($\kappa_S - 1$) to the graph-theoretic Steiner-tree lower bound
   ($\tau_G(S)$), keeping the finite state-space dimension limit separate from
   interaction locality.
4. Explicit finite model-specific bounds, rational test verification, and
   fail-closed certificate refusal contracts.

**Roadmap: Minimal observer for future defect prediction.** A direct consequence
of the lifted cyclic structure in §5.16 is the characterization of the smallest
observer sufficient to predict the future defect trajectory.

Using §5.16’s lifted cyclic space $\mathcal C_m = \operatorname{span}\{\mathcal L^j z_m : j \ge 0\}$,
define the unobservable subspace on $\mathcal C_m$:
$$
 N = \bigcap_{j=0}^{\kappa-1} \ker\left(O\mathcal L^j|_{\mathcal C_m}\right).
$$
For a linear report $Q$ on $\mathcal C_m$, the criterion is uniform over
**all** $z,z'\in\mathcal C_m$: for every such pair,
$$
 Qz=Qz'\ \Longrightarrow\ Oe^{t\mathcal L}z=Oe^{t\mathcal L}z'
 \quad\text{for every }t
$$
if and only if $\ker(Q|_{\mathcal C_m})\subseteq N$. For a fixed, known
$z_m$, its trajectory is already determined by the model; the criterion
concerns distinguishing possible lifted initial states.

On the full linear carrier $\mathcal C_m$, the minimum number of additional
unrestricted linear measurements needed is
$$
 \dim\ker Q-\dim(\ker Q\cap N),
$$
with both kernels taken on $\mathcal C_m$. The annihilator recurrence of
Theorem 5.16 identifies the common kernel of all future readouts with $N$;
Proposition 4.7's rank-nullity argument gives the measurement count.

For a restricted admitted subset $Z\subseteq\mathcal C_m$, the exact
criterion instead is
$$
 (Z-Z)\cap\ker Q\subseteq N.
$$
The ambient kernel inclusion is sufficient but need not be necessary on $Z$;
the unrestricted linear-carrier measurement count is not asserted to be
minimal there. Conditioning constants for imperfect reports require the
singular values of the relevant restricted observability map.

### 5.17 Sharp onset, algebraic cancellation, and local zero certificates

Fix the finite tensor factors, a normalized product initial density $m$, and
an affine real family of one-/two-local Hermitian Hamiltonians
$H(\lambda)=H_0+\sum_{a=1}^r\lambda_a H_a$. Fix $S$, $|S|=k\ge2$.
The allowed graph includes every edge occurring in this family; it is not
recomputed after setting a coupling to zero. Write $d$ for the global Hilbert
dimension and use $K={d^2+k\choose k}$ as a common, possibly large cutoff.
In a fixed real Hermitian basis define the vector polynomials
$$
 b_j(\lambda)=\kappa_S^{(j)}(0;\lambda),\qquad
 E_j=\{\lambda:b_0(\lambda)=\cdots=b_j(\lambda)=0\}.
$$
Each coordinate of $b_j$ has degree at most $j$. A parameter-dependent initial
state is not included in this declaration.

**Theorem 5.18 (finite cancellation stratification).** If the allowed graph
connects $S$, put $\tau=\tau_G(S)$. The onset-$j$ stratum is exactly
$E_{j-1}\setminus E_j$ for $\tau\le j<K$; the persistent-zero stratum is
exactly $E_{K-1}$. All $E_j$ are real algebraic sets. If $b_\tau$ is not the
zero polynomial on the declared parameter space, then onset equals $\tau$
outside the proper algebraic exceptional set $E_\tau$. This complement is
open, dense and of full Lebesgue measure. If $b_\tau$ vanishes identically,
no such generic-equality conclusion is licensed. Disconnected $S$ gives
persistent zero throughout the family.

*Proof.* Nested commutators give polynomial state jets of degree at most $j$.
The partition/product formula for cumulants preserves that degree, since
the derivative orders in every product sum to $j$. Theorem 5.14 makes all
orders below $\tau$ zero. For each fixed parameter, Corollary 5.17 bounds
its cyclic dimension by $K$, so vanishing of orders $0,\ldots,K-1$ is
equivalent to persistent zero. The first nonzero vector polynomial value
therefore gives precisely the displayed stratum. A nonzero coordinate of
$b_\tau$ has a zero set of empty interior and Lebesgue measure zero; $E_\tau$
is contained in it and is closed. Disconnected components factorize. $\square$

This is a finite algebraic classification for a *specified* family, not an
efficient algorithm in global volume. Different edge monomials can cancel
at a particular parameter value. Exhibiting one nonzero monomial coefficient
establishes that the polynomial is nonzero, not that every nonzero-coupling
Hamiltonian attains the graph bound. The locality radius in Theorem 5.14
applies to each $b_j$, but not to the common global cutoff $K$.

**Proposition 5.19 (a constructive sharp family for every finite tree).**
Let $T$ be any finite tree with $k\ge2$ vertices, put $S=V(T)$ and
$r=k-1$. At vertex $v$ take one qubit for each incident edge, so
$\mathcal H_v=(\mathbb C^2)^{\otimes\deg(v)}$. Initialize all qubits in
$|0\rangle$. Orient each edge $e=(u,v)$ once and set
$$
 H=\sum_{e=(u,v)}\lambda_e X_{u,e}X_{v,e}.
$$
Define $W_v$ as the product of $Y$ on outgoing incidence qubits and $X$ on
incoming incidence qubits. Then the connected scalar readout is exactly
$$
 \chi_T(t):=\operatorname{Tr}\!\left[
       \left(\bigotimes_vW_v\right)\kappa_S(t)\right]
   =(-1)^r\prod_{e\in T}\sin(2\lambda_e t).
$$
Consequently
$$
 \chi_T^{(r)}(0)=r!(-2)^r\prod_e\lambda_e,
 \qquad m_{\mathrm{onset}}=r=\tau_T(S)
 \quad\hbox{if every }\lambda_e\ne0.
$$
If any coupling is zero the tree splits and the full cumulant stays zero.
Thus this family's exceptions are exactly the coordinate hyperplanes.

*Proof.* Edge terms act on disjoint incidence qubits. On each edge the state
is $\cos(\lambda_e t)|00\rangle-i\sin(\lambda_e t)|11\rangle$;
its single-qubit $X,Y$ means vanish and its $Y\otimes X$ mean is
$-\sin(2\lambda_e t)$. Every nonempty proper vertex subset has a cut edge,
so the moment of its $W_v$ product contains a zero single-qubit factor.
All proper-partition terms in the scalar cumulant vanish. The full moment
is the product of the edge moments. Its nonzero order-$r$ derivative,
together with Theorem 5.14, establishes the full operator's onset. $\square$

This supplies a nonzero point for every admitted tree in the full affine
space of Hermitian edge interactions on these local dimensions, with this
fixed initial state. Theorem 5.18 therefore gives generic equality there.
Bounded tree degree keeps local dimension bounded. It does **not** establish
generic equality for every qubit-only tree or every proper terminal subset
with Steiner vertices: those families require their own nonzero coefficient.
The three-qubit chain in §5.14 already supplies a sharp proper-terminal
example. No uniform lower rate follows as a coupling tends to zero or as
the number of tree edges grows.

**A genuine delay with the same graph bound.** For two qubits set
$H=aX_1+bZ_1X_2$ and $m=|00\rangle\langle00|$. Direct differentiation gives
$$
 \kappa_{12}'(0)=0,\qquad
 \kappa_{12}''(0)=ab(X\otimes X-Y\otimes Y).
$$
Thus $ab\ne0$ has onset two although $\tau=1$. If $a=0$, the first spin
stays a $Z$ eigenstate and the evolution is product; if $b=0$ the evolution
is local. These are all persistent-zero cases in this family. In particular,
the order-one polynomial can vanish on an entire admitted family without
forcing persistent zero.

**Symmetry-protected exceptions, with an exact scope.** Specify a finite
unitary symmetry group $\Gamma$, require $U_gmU_g^*=m$ and
$[U_g,H(\lambda)]=0$, and suppose the chosen vector readout is equivariant
into a real representation $D_g$. Its trajectory lies in
$\operatorname{Fix}(D)$. If the projector
$P_\Gamma=|\Gamma|^{-1}\sum_gD_g$ is zero, that readout stays zero.
Indeed the evolved density remains invariant, and equivariance gives
$R(t)=D_gR(t)$; averaging gives $R(t)=P_\Gamma R(t)$.
For a nonzero fixed subspace this selection rule alone decides nothing.
Parameterize the symmetry-allowed affine Hamiltonian space and restrict the
polynomials $b_j$ to it. Theorem 5.18 still gives its exact onset strata;
the entire family has persistent zero if and only if every restricted
$b_j$, $0\le j<K$, is the zero polynomial. Necessity follows from vanishing
at every real parameter; sufficiency follows pointwise from the cutoff.
This classifies exceptions relative to the declared symmetry family, not
all possible symmetry groups. An odd scalar observable can be zero while
the full cumulant is nonzero; its selection rule must not be promoted to
an operator-zero certificate.

**Proposition 5.20 (boundary-checked local persistent-zero certificate).**
Let $R\supseteq S$ be a finite region. Supply a finite-dimensional real
space $\mathcal A_R$ of Hermitian operators, containing identity, with an
explicit basis such that
$$
 i[H_R,\mathcal A_R]\subseteq\mathcal A_R,
 \qquad [h_Z,X]=0.
$$
The second identity is required for every boundary-crossing term $h_Z$
and every basis vector $X$.
Suppose the desired readout is a polynomial of degree at most $p$ in the
expectations of this basis. If $n_R=\dim\mathcal A_R$, vanishing of its
first ${n_R+p\choose p}$ jets, including order zero, certifies persistent
zero in every finite ambient volume with the same local and boundary data.
A smaller verified cyclic annihilator is sufficient as in Theorem 5.16.

*Proof.* Terms outside $R$ commute with supported operators. The boundary
test removes every crossing contribution. Invariance under $i[H_R,\cdot]$
makes the expectation vector solve a closed finite linear ODE with initial
values computed from $m$. Apply Theorem 5.16 to that vector and the declared
polynomial. Its equality with the ambient expectations follows from
uniqueness of the linear ODE. To certify the full $\kappa_S$, include a
complete Hermitian operator basis on $S$ and use its component polynomials,
not only one measured contraction. $\square$

The invariant region and crossing-commutator tests are substantive premises;
a radius sufficient for a few jets is not a substitute. For example, a
missing symmetry or one noncommuting boundary term invalidates this local
certificate, even when several initial jets happen to vanish.

The finite checker in `code/local_persistent_zero.py` verifies the supplied
Hermitian basis, identity containment, independence, local generator, every
declared crossing commutator, initial density, polynomial degree and full
cyclic annihilator. The certificate is bound to the entire declared model,
including all Hamiltonian terms. The negative control changes a commuting
$Z\otimes X$ boundary to $X\otimes X$: its first jet vanishes but its second
is nonzero, and the certificate is rejected. These are finite model checks;
completeness of a laboratory's Hamiltonian description is not inferred.

**A measurement protocol for the leading coefficient.** Fix Hermitian
contractions $M_i$ on $S$ and measure the $2^k-1$ subset moments
$\langle\prod_{i\in B}M_i\rangle$. Their partition polynomial gives
$\chi_S(t)=\operatorname{Tr}[(\bigotimes_iM_i)\kappa_S(t)]$. These
measurements are supported on $S$; for Pauli $M_i$, one joint local basis
setting supplies all subset moments. If every moment estimate, clipped to
$[-1,1]$, has error at most $\epsilon$, telescoping partition products
gives error at most $b_k\epsilon$, with $b_k$ as in §5.14.
Given verified zero lower jets and $a=\chi_S^{(m)}(0)/m!$, Theorem 5.14 gives
$$
 \begin{aligned}
 \left|\frac{\widehat\chi_S(t)}{t^m}-a\right|
 &\le B_{k,m}|t|+\frac{b_k\epsilon}{|t|^m},\\
 B_{k,m}&=a_k\binom{k+m}{m+1}(2g)^{m+1}.
 \end{aligned}
$$
It also gives $|\chi_S(t)|\ge |a||t|^m-B_{k,m}|t|^{m+1}$.
Independent repetitions of bounded outcomes suffice: Hoeffding's inequality
and a union bound give simultaneous moment error $\epsilon$ with probability
at least $1-\delta$ after
$N\ge2\epsilon^{-2}\log(2(2^k-1)/\delta)$ shots of that setting.
This does not assume independence between moments extracted from the same
shot. Resolving higher onset orders costs precision; the error amplified by
$|t|^{-m}$ is not suppressed by taking arbitrarily small times. Measuring
one contraction certifies nonzero onset when it is nonzero, not persistent
zero of the operator. Fixed-support tomography is an alternative, not global
tomography. Bounds uniform in volume require fixed $k,m$, bounded $g$, and
a positive lower bound on $|a|$.

The role of these results differs from Lieb--Robinson propagation bounds
[1,3,4,9]: they identify exact initial cancellations and finite-model zero
certificates, whereas those bounds constrain propagation. No priority for
connected expansions, symmetry selection rules, or polynomial observability
is claimed.

**Finite-horizon observation trade-offs and marginal-indistinguishable state pairs.**
In experimental observation protocols with a finite total shot budget $M_{\mathrm{total}}$ distributed across $M_{\mathrm{settings}}$ measurement settings ($M_s = M_{\mathrm{total}} / M_{\mathrm{settings}}$ shots per setting), two distinct estimation targets can be compared:
1. *Leading Taylor/jet coefficient estimation:* For a $k$-site cumulant with verified zero jets below order $m$, the preceding estimate controls $\chi_S^{(m)}(0)/m!$ using a sampled cumulant, the analytic remainder, and measurement error amplified by $|t|^{-m}$. The ordered-Bell constant $b_k$ controls conversion of subset moments into a support-$k$ cumulant at each fixed time. It does not control the separate finite-difference or interpolation problem in time; that conditioning depends on the sampling times, derivative order and remainder assumptions. Finitely many samples alone do not determine an exact derivative.
2. *Future trajectory prediction:* Predicting the trajectory $\langle O\rangle_{\rho(t)}$ across a finite horizon $t \in [0, T]$ via the Duhamel convolution bound.

For one declared $[-1,1]$-valued observable per setting and independent repetitions, Hoeffding's inequality and a union bound give simultaneous absolute estimation errors at most the following value with probability at least $1-\delta$:
$$
\epsilon_{\mathrm{shot}} = \sqrt{\frac{2\ln(2M_{\mathrm{settings}}/\delta)}{M_s}} = \sqrt{\frac{2M_{\mathrm{settings}}\ln(2M_{\mathrm{settings}}/\delta)}{M_{\mathrm{total}}}},
$$
On that probability event, a bound $\epsilon_{\mathrm{pred}}$ for the same observable combines as $\epsilon_{\mathrm{total}}\le\epsilon_{\mathrm{pred}}+\epsilon_{\mathrm{shot}}$. If each setting supplies multiple reported observables, the union bound counts those observables; a nonlinear cumulant requires its additional $b_k$ error factor.

To illustrate how all lower-order marginals can agree identically while the $k$-body connected cumulant differs macroscopically, consider for $k=6$ the opposite-parity six-qubit GHZ states
$$
\lvert\mathrm{GHZ}_6^\pm\rangle = \frac{1}{\sqrt{2}}\bigl(\lvert 0\rangle^{\otimes 6} \pm \lvert 1\rangle^{\otimes 6}\bigr), \qquad \rho_\pm = \lvert\mathrm{GHZ}_6^\pm\rangle\langle\mathrm{GHZ}_6^\pm\rvert,
$$
and the interpolated family $\rho(\epsilon) = \rho_{\mathrm{cl}} + \frac{\epsilon}{2}\bigl(\lvert 0\rangle^{\otimes 6}\langle 1\rvert^{\otimes 6} + \lvert 1\rangle^{\otimes 6}\langle 0\rvert^{\otimes 6}\bigr)$ for $\epsilon\in[-1,1]$, where $\rho_{\mathrm{cl}} = \frac{1}{2}(\lvert 0\rangle^{\otimes 6}\langle 0\rvert^{\otimes 6} + \lvert 1\rangle^{\otimes 6}\langle 1\rvert^{\otimes 6})$ is the decohered classical mixture ($\rho(1)=\rho_+$ and $\rho(-1)=\rho_-$). For every proper subset $A \subsetneq \{1,\dots,6\}$ ($1 \le |A| \le 5$), tracing out the complement $V\setminus A$ annihilates the six-site off-diagonal coherence, so all proper reduced states coincide identically:
$$
\operatorname{Tr}_{V\setminus A}\rho(\epsilon) = \operatorname{Tr}_{V\setminus A}\rho_{\mathrm{cl}} = \frac{1}{2}\bigl(\lvert 0\rangle^{\otimes |A|}\langle 0\rvert^{\otimes |A|} + \lvert 1\rangle^{\otimes |A|}\langle 1\rvert^{\otimes |A|}\bigr) \qquad (1 \le |A| \le 5).
$$
Because every proper marginal of order $\le 5$ is independent of $\epsilon$, all lower-order marginal differences and all lower-order connected-cumulant differences vanish identically between $\rho(\epsilon)$ and $\rho_{\mathrm{cl}}$, while the 6-site connected cumulant difference is exact:
$$
\kappa_6(\rho(\epsilon)) - \kappa_6(\rho_{\mathrm{cl}}) = \rho(\epsilon) - \rho_{\mathrm{cl}} = \frac{\epsilon}{2}\bigl(\lvert 0\rangle^{\otimes 6}\langle 1\rvert^{\otimes 6} + \lvert 1\rangle^{\otimes 6}\langle 0\rvert^{\otimes 6}\bigr),
$$
with trace norm $\lVert\kappa_6(\rho(\epsilon)) - \kappa_6(\rho_{\mathrm{cl}})\rVert_1 = |\epsilon|$ and $\lVert\kappa_6(\rho_+) - \kappa_6(\rho_-)\rVert_1 = 2$ (witnessed by the 6-body Pauli observable $X^{\otimes 6}$, for which $\langle X^{\otimes 6}\rangle_{\rho_+} - \langle X^{\otimes 6}\rangle_{\rho_-} = 2$).
These results complement multipartite Lieb--Robinson bounds (Tran et al. [25]): whereas power-law Lieb--Robinson bounds constrain spatial propagation velocity in long-range architectures, the algebraic cancellation strata and parity constructions above identify exact structural blind spots where few-body marginals carry zero signal despite order-unity $k$-body connected correlations.

## 6. Worked Examples

### 6.1 Example 1: Two Qubits with Exact Trace-Norm Defect

Consider two qubits with Hamiltonian and initial state
$$H = J(X \otimes X), \qquad \rho(0) = |00\rangle\langle 00|.$$
The evolved state is $|\psi(t)\rangle = \cos(Jt)|00\rangle - i\sin(Jt)|11\rangle$. Write $c=\cos(Jt)$ and $s=\sin(Jt)$. The product retraction is the product of single-site marginals $\Pi\rho(t)=\rho_A(t)\otimes\rho_B(t)$ with $\rho_A(t)=\rho_B(t)=c^2|0\rangle\langle0|+s^2|1\rangle\langle1|$. In the ordered basis $(|00\rangle,|01\rangle,|10\rangle,|11\rangle)$,
$$\rho(t)-\Pi\rho(t)=\begin{pmatrix} c^2s^2 & 0 & 0 & i\,cs\\ 0 & -c^2s^2 & 0 & 0\\ 0 & 0 & -c^2s^2 & 0\\ -i\,cs & 0 & 0 & c^2s^2 \end{pmatrix}.$$
This Hermitian matrix has eigenvalues $\{c^2s^2+cs,\ c^2s^2-cs,\ -c^2s^2,\ -c^2s^2\}$, so for $|Jt|\le\pi/4$ (where $|cs|\ge c^2s^2$) its trace norm is
$$D_{12}(t)=\lVert\rho(t)-\Pi\rho(t)\rVert_1 = 2|cs|+2c^2s^2.$$
The absolute value covers both signs of $J$: for $J<0$ we have $s=\sin(Jt)<0$, so $cs<0$ and the two eigenvalues $c^2s^2\pm cs$ exchange roles, leaving $|c^2s^2+cs|+|c^2s^2-cs|=2|cs|$ unchanged whenever $|cs|\ge c^2s^2$. At $t=\pi/(8|J|)$ we get $|Jt|=\pi/8$, so $|cs|=\tfrac{1}{2\sqrt2}$ and $c^2s^2=\tfrac18$, hence
$$D_{12}\!\left(\tfrac{\pi}{8|J|}\right)=\tfrac{1}{\sqrt2}+\tfrac14\approx 0.9571.$$

The calculation is verified by the following script:

```python
import numpy as np
for theta in (np.pi / 8, -np.pi / 8):  # Jt > 0 and Jt < 0
    c, s = np.cos(theta), np.sin(theta)
    a, b = c * c * s * s, c * s
    Delta = np.array(
        [
            [a, 0, 0, 1j * b],
            [0, -a, 0, 0],
            [0, 0, -a, 0],
            [-1j * b, 0, 0, a],
        ],
        dtype=complex,
    )
    # both signs: 0.9571067811865476
    print(np.sum(np.abs(np.linalg.eigvalsh(Delta))))
    print(2 * abs(b) + 2 * a)
```

The defect is positive and computed in closed form, witnessing non-product structure that the marginal retraction cannot represent.

### 6.2 Example 2: Transverse-Field Ising Model

Consider the 1D transverse-field Ising model $H = -J\sum_i Z_i Z_{i+1} - h\sum_i X_i$ with initial state $|{+}\rangle^{\otimes N}$ and bond term $H_e = -J\,Z_a Z_b$. We compute both the raw rate $\nu_e$ and the dimension-normalized rate $\gamma_e$ in closed form. Because $|{+}\rangle$ is an eigenstate of $X$, the transverse field commutes with the initial one-site state and contributes nothing to the first-order normal rate. With $\rho_a=\rho_b=|{+}\rangle\langle{+}|$ and $(Z\otimes Z)|{++}\rangle=|{--}\rangle$,
$$-i[H_e,\rho_a\otimes\rho_b] = iJ\bigl(|{--}\rangle\langle{++}| - |{++}\rangle\langle{--}|\bigr).$$
Both one-site marginals of this operator vanish (each term carries a factor $\langle{+}|{-}\rangle=0$), so $P_e$ annihilates it and $Q_e$ acts as the identity: $n_e = -i[H_e,\rho_a\otimes\rho_b]$. In the two-dimensional span of $\{|{++}\rangle,|{--}\rangle\}$ this is $J$ times a Pauli-$Y$, with eigenvalues $\pm J$, hence
$$\nu_e=\lVert n_e\rVert_1 = 2|J|,\qquad \gamma_e = \frac{\nu_e}{d^2} = \frac{|J|}{2}.$$
For $J\ne0$ this holds on every bond, for every field strength $h$, independently of $N$. Thus the active-edge hypothesis holds with $\eta=1$ and raw $\nu_{\min}=2|J|$. Lemma 5.3 covers the one-local field terms, and with $g\le2|J|+|h|$, Theorem 5.1 gives the half-slope window
$$0<t\le\frac{|J|}{24(2|J|+|h|)^2}.$$

The calculation is verified by the following script:

```python
import numpy as np
plus = np.array([1, 1]) / np.sqrt(2)
rp = np.outer(plus, plus)  # |+><+|
Z = np.array([[1, 0], [0, -1]])
He = -np.kron(Z, Z)  # J = 1 bond term
rab = np.kron(rp, rp)
rhodot = -1j * (He @ rab - rab @ He)

def ptr(M, keep):
    # partial trace of a 2-qubit operator
    M = M.reshape(2, 2, 2, 2)
    if keep == 0:
        return np.einsum("ijkj->ik", M)
    return np.einsum("ijil->jl", M)

Ne = (
    rhodot
    - np.kron(ptr(rhodot, 0), rp)
    - np.kron(rp, ptr(rhodot, 1))
)
# 2.0 => nu_e = 2, gamma_e = 1/2
print(np.sum(np.abs(np.linalg.eigvalsh(Ne))))
```

The rate is positive and computed in closed form on every bond, so the active-edge density hypothesis holds with $\eta=1$.

---

### 6.3 Quadratic and Cubic Onset

A zero first-order rate does not determine the first nonzero order.
Two small systems illustrate what the Taylor bounds add.

For $H=Z\otimes Z+X\otimes I$ and initial state $|0+\rangle$,
direct differentiation gives
$$
 F'(0)=0,\qquad
 F''(0)=
 \begin{pmatrix}
 0&0&1&-1\\
 0&0&1&-1\\
 1&1&0&0\\
 -1&-1&0&0
 \end{pmatrix}.
$$
Its eigenvalues are $2,-2,0,0$, so
$D(t)=2t^2+O(t^3)$. Here $g=2$, and Theorem 5.5 gives the explicit
bound $D(t)\ge 2t^2-512t^3\,$.

For the two-qubit Ising Hamiltonian
$$
 H=-JZ\otimes Z-h(X\otimes I+I\otimes X),\qquad
 \rho(0)=|00\rangle\langle00|,
$$
the first *two* residual derivatives vanish:
$$
 F'(0)=F''(0)=0,\qquad
 F'''(0)=8iJh^2
       (|00\rangle\langle11|-|11\rangle\langle00|).
$$
Thus, when $Jh\ne0$,
$$
 \lVert F'''(0)\rVert_1=16|J|h^2,\qquad
 D(t)=\frac{8}{3}|J|h^2t^3+O(t^4).
$$
With $g=|J|+|h|$, the quantitative bound is
$$
 D(t)\geq\frac{8}{3}|J|h^2t^3-160g^4t^4.
$$
It retains half the leading term for
$0<t\leq |J|h^2/(120g^4)$.

These derivatives can be checked by expanding the state amplitudes:
$$
 \begin{aligned}
 c_{00}(t)&=1+iJt-\tfrac12(J^2+2h^2)t^2
              -\tfrac{i}{6}J(J^2+2h^2)t^3+O(t^4),\\
 c_{01}(t)=c_{10}(t)&=iht-\tfrac{i}{6}h(J^2+4h^2)t^3+O(t^4),\\
 c_{11}(t)&=-h^2t^2-\tfrac{i}{3}Jh^2t^3+O(t^4).
 \end{aligned}
$$
Forming $|\psi(t)\rangle\langle\psi(t)|$, tracing its marginals and
subtracting their product gives the displayed residual derivatives.
In particular, the isolated term
$-2\dot\rho_a(0)\otimes\dot\rho_b(0)=-2h^2Y\otimes Y$ is canceled
by the other terms in $F''(0)$. Keeping it alone would incorrectly
predict correlation under independent local fields even at $J=0$.

The exact symbolic implementation in `code/short_time_jets.py` and its
tests compare nested-commutator derivatives with this separate amplitude
expansion. They also retain the tangent-commutator example, independent
local evolution, mixed-state centering, the pure-state rate identity and
a four-site locality example. The Lean file
`lean4/po000_short_time_jets.lean` checks the support-factor and
factorial-normalization arithmetic, including the constants 24, 64 and
160. The analytic and matrix-norm arguments remain written proofs.

---

## 7. Observer Visibility and the Local Green / Global Red Gap

This section separates three distinct mathematical objects: a direction-valued projection residual, a declared 1-cochain obtained by applying linear observation maps to that residual, and a coboundary obtained only when an explicit 0-cochain potential is supplied. The finite quantum lower bounds in §5 concern the raw trace norm of the first object, whereas the characterization in §4 governs global aggregation once a local gauge family has been specified.

### 7.1 Relation to Hilbert extensions

The conditional $\ell^1$ characterization of §4 does not require every downstream statistic to remain an $\ell^1$ sum. Passing to an $L^2_{\mathrm{RMS}}$ or Hilbert-space envelope is an additional representation step that introduces inner-product structure and phase-symmetry assumptions not used in Theorems 3.1, 4.2, or 5.1.

### 7.2 Projection residual, induced cochain, and coboundary

Let $R_e$ be a local residual space on edge $e$ and let
$$
q_e:R_e\longrightarrow V_e
$$
be a bounded linear observation map into a normed vector space $V_e$. For a local normal residual $n_e \in R_e$, define
$$
\omega_e:=q_e(n_e).
$$
The family $\omega=(\omega_e)_e$ is an **induced 1-cochain** in $C^1=\prod_eV_e$. Forming $\omega$ does not by itself make $\omega$ a coboundary.

It is useful to distinguish three structural levels:

1. **Induced cochain:** the observation maps $q_e$ are specified and $\omega_e=q_e(n_e)$ is evaluated edgewise.
2. **Quotient obstruction:** a coboundary differential $d_0:C^0\to C^1$ and norm gauge are specified, so the quotient seminorm
   $$
   \Phi([\omega])=\inf_{\alpha\in C^0}\lVert\omega-d_0\alpha\rVert_1
   $$
   is well defined.
3. **Coboundary (exactness):** an explicit 0-cochain $\alpha\in C^0$ is exhibited with $\omega=d_0\alpha$.

In finite-dimensional spaces, $\operatorname{im}(d_0)$ is automatically closed, so $\Phi([\omega])=0$ if and only if $\omega\in\operatorname{im}(d_0)$. In an infinite-dimensional Banach presentation, closedness of $\operatorname{im}(d_0)$ must be verified separately; otherwise $\Phi([\omega])$ measures only the distance to $\overline{\operatorname{im}(d_0)}$.

Identifying a physical residual with a coboundary requires level 3. The companion paper [6] develops the finite cochain-adapter schema and higher-cell extensions when a second differential $d_1:C^1\to C^2$ satisfying $d_1d_0=0$ is present. At the covering-edge level of the present paper, $C^2$, $d_1$, and any descended curvature map $\overline d_1:Q^1\to C^2$ are not needed until §7.7–§7.9; even when $d_1d_0=0$ holds, the cocycle condition $d_1\omega=0$ is an independent closure property that does not follow solely from $\omega$ being induced by a projection residual.

### 7.3 Relation to higher-cell and representation extensions

Within the finite obstruction framework [8], a nonvanishing local residual or quotient class diagnoses an incompatibility of the chosen reduced representation; passing to a richer representation space or higher-order cell complex is an explicit modeling step with its own compatibility conditions. The companion work [7] studies the analogous projection-residual diagnostics in compressed evaluation pipelines.

#### 7.3.3 Covering-Edge Diagrams and Poset Coboundaries

Before analyzing observer visibility, we fix the compact algebraic setup for covering-edge descent complexes on posets (companion package **PO-001** develops the full saturated-chain presheaf theory; see also Mac Lane [2]). Let $(P, \le)$ be a finite partially ordered set, and let $E_{\mathrm{cov}} = \{(a,b) \in P \times P : a \lessdot b\}$ denote its set of covering edges ($b$ covers $a$). A **covering-edge Banach diagram** assigns to each element $a \in P$ a real or complex normed fiber space $(F(a), \lVert\cdot\rVert_{F(a)})$, and to each covering edge $(a,b) \in E_{\mathrm{cov}}$ a contractive linear transition map $r_{b,a}: F(b) \to F(a)$ ($\lVert r_{b,a}\rVert \le 1$).

The corresponding 0-cochain space (space of global sections) and 1-cochain space are the direct product/sum spaces
$$
C^0 = \bigoplus_{a\in P} F(a), \qquad C^1 = \bigoplus_{e=(a,b)\in E_{\mathrm{cov}}} F(a),
$$
equipped with their $\ell^1$ fiber sums. The **canonical covering-edge coboundary operator** $d_0: C^0 \to C^1$ assigns to each section $s = (s(a))_{a\in P} \in C^0$ the edgewise compatibility defect
$$
(d_0 s)_e = \Delta(s)_e := r_{b,a}s(b) - s(a) \;\in\; F(a) \qquad \text{for } e=(a,b)\in E_{\mathrm{cov}}.
$$
A section $s \in C^0$ is a global section (or compatible) if and only if $d_0 s = 0$; the global compatibility defect norm is $I(s) := \lVert d_0 s\rVert_1 = \sum_{e\in E_{\mathrm{cov}}} \lVert\Delta(s)_e\rVert_{F(a)}$.

---

### 7.4 Best-Single-Observer Visibility Gap and the Local Green / Global Red Bound

While §7.2 distinguishes an induced cochain from a quotient class and a coboundary, a further distinction arises when a glued section is monitored by a *family of projection-limited local observers*. Each observer inspects only a subset of covering edges through contractive linear observation maps. When the kernels of these observation maps jointly cover the subspace supporting the edgewise compatibility defect, every individual observer reports zero local defect ("Local Green") even though the global compatibility defect norm is strictly positive ("Global Red").

Here “local” specifies which coordinates an observer can inspect. Bell
local causality instead constrains conditional response probabilities,
and local tomography (Finite QM [20, §13.8]) constrains determination of composite
states by product effects. Section 7.10 separates these conditions.

#### 7.4.1 Definition (local observer carrier family)

Let $F$ be a covering-edge Banach diagram over the finite poset $(P,\leq)$ as defined in §7.3.3, and for an edge $e=(a,b)\in E_{\mathrm{cov}}$ write $a_e:=a$ for its lower endpoint. A **local observer carrier** is a pair
$$
\mathcal C^\alpha \;=\; \bigl(E^\alpha,\ (q_e^\alpha)_{e\in E^\alpha}\bigr),
$$
where $E^\alpha\subseteq E_{\mathrm{cov}}$ is the observer's edge domain and each
$$
q_e^\alpha : F(a_e)\longrightarrow V_e^\alpha
$$
is a contractive linear observation map into a normed space $V_e^\alpha$. A **local observer carrier family** is a finite, nonempty collection $\{\mathcal C^\alpha\}_{\alpha\in A}$ ($A\neq\varnothing$). For an edge $e$, its **watcher set** is $W(e):=\{\alpha\in A : e\in E^\alpha\}$, and its **joint watcher kernel** is
$$
K_e \;:=\;
\begin{cases}
\bigcap_{\alpha\in W(e)}\ker q_e^\alpha, & W(e)\neq\varnothing,\\[2pt]
F(a_e), & W(e)=\varnothing .
\end{cases}
$$
The family has **full edge coverage** when $\bigcup_{\alpha\in A}E^\alpha=E_{\mathrm{cov}}$, i.e., $W(e)\neq\varnothing$ for every edge $e\in E_{\mathrm{cov}}$.

#### 7.4.2 Definition (local tallies, Local Green, Global Red, visibility gap)

For a section $s\in C^0$, with edgewise compatibility defect $\Delta(s)_e = (d_0 s)_e = r_{b,a}(s(b))-s(a)$ as in §7.3.3, define the **observed local tally** of observer $\alpha$:
$$
J^\alpha(s)\;:=\;\sum_{e\in E^\alpha}\bigl\lVert q_e^\alpha\bigl(\Delta(s)_e\bigr)\bigr\rVert_{V_e^\alpha}.
$$
We say that observer $\alpha$ reports **Local Green** at $s$ when $J^\alpha(s)=0$, and that the family is **All-Green** at $s$ when $J^\alpha(s)=0$ for every $\alpha\in A$. We say that $s$ is **Global Red** when $I(s)=\sum_{e\in E_{\mathrm{cov}}}\lVert\Delta(s)_e\rVert>0$. The **best-single-observer visibility gap** of the family at $s$ is
$$
\Lambda_{\max}(s)\;:=\;I(s)\;-\;\max_{\alpha\in A}J^\alpha(s)\;\ge\;0
\qquad\text{(nonnegativity by Proposition 7.4.3).}
$$
When no ambiguity can arise, we write $\Lambda$ for $\Lambda_{\max}$.

**Remark 7.4.2.1 (Unfaithfulness of observed local gauges).** Each observer's induced local gauge $j_e^\alpha(v):=\lVert q_e^\alpha v\rVert_{V_e^\alpha}$ is a seminorm, so it is convex and positively homogeneous, but it is not faithful whenever $\ker q_e^\alpha\neq\{0\}$: the implication $J_{\{e\}}(x)=0\Rightarrow x=0$ of Axiom RE1 (§4.1) fails on $\ker q_e^\alpha$. Defining $p_e:=\max_{\alpha\in W(e)}\lVert q_e^\alpha\Delta(s)_e\rVert$ (with $p_e:=0$ if $W(e)=\varnothing$) decomposes the visibility gap into two nonnegative contributions:
$$
\Lambda_{\max}(s)
=\underbrace{\sum_e\bigl(\lVert\Delta(s)_e\rVert-p_e\bigr)}_{\text{edgewise observation/contraction loss}}
+\underbrace{\left(\sum_e p_e-\max_\alpha J^\alpha(s)\right)}_{\text{single-observer domain fragmentation}}.
$$
Thus a positive visibility gap $\Lambda_{\max}(s)>0$ can arise either from nontrivial observer kernels, from no single observer watching all edges carrying visible defect, or from both mechanisms simultaneously.

#### 7.4.3 Proposition (passivity and Green propagation)

For every section $s\in C^0$ and every observer $\alpha\in A$,
$$
J^\alpha(s)\;\le\;\sum_{e\in E^\alpha}\lVert\Delta(s)_e\rVert\;\le\;I(s).
$$
In particular, $I(s)=0$ implies $J^\alpha(s)=0$ for every $\alpha\in A$: global compatibility implies Local Green for every observer.

*Proof.* Each $q_e^\alpha$ is contractive, so $\lVert q_e^\alpha(\Delta(s)_e)\rVert_{V_e^\alpha}\le\lVert\Delta(s)_e\rVert_{F(a_e)}$ termwise. Summing over $E^\alpha\subseteq E_{\mathrm{cov}}$ and enlarging the domain of summation to $E_{\mathrm{cov}}$ (all summands being nonnegative) yields both inequalities. $\square$

Contractivity ensures that passive linear observations can attenuate or annihilate defect norm, but cannot manufacture it. The converse fails whenever the defect lies inside the joint watcher kernels.

#### 7.4.4 Proposition (kernel-cover characterization of All-Green)

Fix a section $s\in C^0$. The observer family is All-Green at $s$ **if and only if**
$$
\Delta(s)_e\in K_e
\qquad\text{for every } e\in E_{\mathrm{cov}} .
$$
Consequently:

1. *(Local Green / Global Red coexistence.)* If $I(s)>0$ and $\Delta(s)_e\in\ker q_e^\alpha$ for every edge $e$ and every watcher $\alpha\in W(e)$, then every observer reports Local Green while $s$ is Global Red, and $\Lambda(s)=I(s)$.
2. *(Sufficiency versus necessity.)* All-Green implies $I(s)=0$ under the joint-kernel triviality hypothesis of Corollary 7.4.7; without that hypothesis the implication can fail even under full edge coverage (Proposition 7.4.5). Conversely, edgewise joint-kernel triviality is not necessary for local-to-global soundness on coupled carriers, because coboundary coupling across shared fibers can force invisible edge defects to vanish (Proposition 7.4.7-B).

*Proof.* Because $J^\alpha(s)$ is a finite sum of nonnegative norms, $J^\alpha(s)=0$ if and only if $q_e^\alpha(\Delta(s)_e)=0$, i.e., $\Delta(s)_e\in\ker q_e^\alpha$, for all $e\in E^\alpha$. Quantifying over all $\alpha\in A$ shows that All-Green holds if and only if $\Delta(s)_e\in\bigcap_{\alpha\in W(e)}\ker q_e^\alpha=K_e$ for every watched edge $e$, while for unwatched edges ($W(e)=\varnothing$) the condition $\Delta(s)_e\in F(a_e)=K_e$ is vacuous. Claim 1 and Claim 2 follow immediately. $\square$

#### 7.4.5 Proposition (three-patch Local Green / Global Red witness)

There exists a covering-edge Banach diagram, a section $s$, and a local observer carrier family with **full edge coverage** such that the family is All-Green at $s$ while $I(s)=6>0$.

*Construction and proof.* Take the finite poset
$$
P=\{x_{12},x_{23},x_{31},\,u_1,u_2,u_3\},
\qquad
x_{ij}<u_i,\quad x_{ij}<u_j,
$$
consisting of three patches $u_1,u_2,u_3$ and three pairwise overlaps $x_{ij}$; every displayed relation is a covering relation, so
$$
E_{\mathrm{cov}}=\bigl\{(x_{ij},u_i),\,(x_{ij},u_j)\ :\ \{i,j\}\subset\{1,2,3\}\bigr\},
\qquad |E_{\mathrm{cov}}|=6 .
$$
Assign to every element the fiber $F(x)=(\mathbb R^3,\lVert\cdot\rVert_1)$, and let every restriction map $r_{u,x}$ be the identity map. Let $(e_1,e_2,e_3)$ be the standard basis of $\mathbb R^3$ and define the section
$$
s(u_i)=e_i\ \ (i=1,2,3),
\qquad
s(x_{ij})=0 .
$$
Then on each covering edge $(x_{ij},u_i)$,
$$
\Delta(s)_{(x_{ij},u_i)}
= r_{u_i,x_{ij}}\bigl(s(u_i)\bigr)-s(x_{ij})
= e_i ,
$$
so each of the six edge defects is a standard basis vector of $\ell^1$ norm $1$, giving
$$
I(s)=\sum_{e\in E_{\mathrm{cov}}}\lVert\Delta(s)_e\rVert_1 = 6 > 0 .
$$
Define three observers $\mathcal C^1,\mathcal C^2,\mathcal C^3$, where observer $\alpha$ watches the two edges whose upper element is $u_\alpha$,
$$
E^\alpha=\bigl\{(x_{\alpha\beta},u_\alpha)\ :\ \beta\neq\alpha\bigr\},
$$
through the coordinate-deletion projection
$$
q_e^\alpha=\pi_\alpha:\mathbb R^3\to\mathbb R^2,
\qquad
\pi_\alpha \text{ deletes coordinate } \alpha,
\qquad
\ker\pi_\alpha=\mathbb R\,e_\alpha ,
$$
which is $\ell^1$-contractive. Every edge $(x_{ij},u_i)$ belongs to $E^i$, so $\bigcup_\alpha E^\alpha=E_{\mathrm{cov}}$ (full edge coverage) with $W((x_{ij},u_i))=\{i\}$ and $K_{(x_{ij},u_i)}=\mathbb R\,e_i$. On each edge watched by $\alpha$, the defect is $e_\alpha\in\ker\pi_\alpha$, so
$$
J^\alpha(s)=\sum_{e\in E^\alpha}\lVert\pi_\alpha(\Delta(s)_e)\rVert_1=0
\qquad(\alpha=1,2,3).
$$
Thus the family is All-Green while $\Lambda(s)=I(s)=6$. $\square$

The construction is directly verified by the following script:

```python
import numpy as np

e = np.eye(3)
s = {
    "u1": e[0],
    "u2": e[1],
    "u3": e[2],
    "x12": np.zeros(3),
    "x23": np.zeros(3),
    "x31": np.zeros(3),
}
edges = [
    ("x12", "u1"),
    ("x12", "u2"),
    ("x23", "u2"),
    ("x23", "u3"),
    ("x31", "u3"),
    ("x31", "u1"),
]
watcher = {
    ("x12", "u1"): 0,
    ("x12", "u2"): 1,
    ("x23", "u2"): 1,
    ("x23", "u3"): 2,
    ("x31", "u3"): 2,
    ("x31", "u1"): 0,
}
# identity restrictions
d = {ed: s[ed[1]] - s[ed[0]] for ed in edges}
I = sum(np.abs(v).sum() for v in d.values())
J = [
    sum(
        np.abs(np.delete(d[ed], a)).sum()
        for ed in edges
        if watcher[ed] == a
    )
    for a in range(3)
]
print(I, J)  # 6.0 [0.0, 0.0, 0.0]
```

#### 7.4.6 Corollary (unbounded visibility gap; absence of a recovery modulus)

With the diagram and observers of Proposition 7.4.5 held fixed, the scaled sections $s_\lambda$ ($s_\lambda(u_i)=\lambda e_i$, $s_\lambda(x_{ij})=0$, $\lambda>0$) satisfy $J^\alpha(s_\lambda)=0$ for all $\alpha$ and $I(s_\lambda)=6\lambda$. Consequently, for every $R>0$ there exists an All-Green section with $I(s)=R$, and there is **no** function $f:\mathbb R_{\ge0}\to\mathbb R_{\ge0}$ satisfying
$$
I(s)\ \le\ f\Bigl(\max_{\alpha\in A}J^\alpha(s)\Bigr)
\qquad\text{for all sections } s\in C^0.
$$

*Proof.* By linearity of $\Delta$ (§2.2) and positive homogeneity of the norms, $I(s_\lambda)=\lambda I(s_1)=6\lambda$ and $J^\alpha(s_\lambda)=\lambda J^\alpha(s_1)=0$. Any such function $f$ would have to satisfy $f(0)\ge 6\lambda$ for all $\lambda>0$, which contradicts that $f(0)$ is a fixed non-negative real scalar. $\square$

#### 7.4.7 Corollary (sufficient condition for local-to-global soundness)

Suppose the observer family has full edge coverage and edgewise joint-kernel triviality: $K_e=\{0\}$ for every $e\in E_{\mathrm{cov}}$, so that the combined watcher map $\mathcal Q_e: v \longmapsto (q_e^\alpha v)_{\alpha \in W(e)}$ is injective on every edge fiber. Then All-Green at $s$ implies $I(s)=0$.

*Proof.* By Proposition 7.4.4, All-Green implies $\Delta(s)_e\in K_e=\{0\}$ for every $e\in E_{\mathrm{cov}}$, so $\Delta(s)_e=0$ for all $e$ and $I(s)=0$. $\square$

Proposition 7.4.5 shows that full edge coverage alone does not suffice when $K_e\neq\{0\}$. Injectivity of the combined watcher map $\mathcal Q_e$ does not require any single watcher $q_e^\alpha$ to be faithful on its own. Moreover, as the next proposition shows, edgewise joint-kernel triviality is a sufficient condition on arbitrary 1-cochains, but is not necessary for section-realized defects $\Delta(s)$, because shared lower fibers couple the defects across adjacent covering edges.

#### 7.4.7-B Proposition (non-necessity of joint-kernel triviality on coupled carriers)

There exists a covering-edge Banach diagram and a local observer carrier family with **full edge coverage** and a **nontrivial** joint watcher kernel $K_e\neq\{0\}$ on *every* edge, such that All-Green at any section $s\in C^0$ nevertheless forces $I(s)=0$.

*Construction and proof.* Take the poset $P=\{x,\,u_1,\,u_2\}$ with covering relations $x<u_1$ and $x<u_2$, fibers $F(\cdot)=(\mathbb R^2,\lVert\cdot\rVert_1)$, and zero restriction maps $r_{u_i,x}:=0$ ($i=1,2$). Then for every section $s\in C^0$,
$$
\Delta(s)_{(x,u_i)} = r_{u_i,x}\bigl(s(u_i)\bigr)-s(x) = -s(x)
\qquad(i=1,2).
$$
Thus the realizable defect cochains lie on the diagonal of $C^1$. Define two observers: observer $i\in\{1,2\}$ watches only the edge $(x,u_i)$ through the contractive coordinate functional $q^i(v_1,v_2):=v_{3-i}$. Edge coverage is full, each edge has the single watcher $i$, and the joint watcher kernels are nontrivial on both edges:
$$
K_{(x,u_1)}=\mathbb R\,e_1\neq\{0\},
\qquad
K_{(x,u_2)}=\mathbb R\,e_2\neq\{0\}.
$$
If the family is All-Green at $s$, Proposition 7.4.4 gives $\Delta(s)_{(x,u_i)}=-s(x)\in K_{(x,u_i)}$ for $i=1,2$, so $-s(x)\in\mathbb R e_1\cap\mathbb R e_2=\{0\}$. Hence $s(x)=0$, both edge defects vanish, and $I(s)=0$. $\square$

```python
# coupled two-edge carrier: both restrictions are the zero map, so both
# edge defects equal -s(x); observer i sees the OTHER coordinate.
for sx in ((0.0, 0.0), (1.0, 0.0), (0.0, -2.0), (3.0, 4.0)):
    d = (-sx[0], -sx[1])            # both edges carry this defect
    J1, J2 = abs(d[1]), abs(d[0])   # observer 1 reads coord 2, and vice versa
    I = 2 * (abs(d[0]) + abs(d[1]))
    all_green = J1 == 0 and J2 == 0
    print(sx, all_green, I)         # all_green is True only when I == 0
```

#### 7.4.8 Remarks on represented defect norms versus quotient cohomology

1. **Represented defect norm versus quotient obstruction.** Every quantity $I(s)$ in §7.4 is the $\ell^1$ compatibility defect norm of a declared section $s\in C^0$ (§2.2). Because $\Delta(s)=d_0 s$ is a coboundary by definition (level 3 of §7.2), its quotient semi-norm vanishes identically: $\Phi([\Delta(s)])=0$. Thus the three-patch example of Proposition 7.4.5 exhibits a section with $I(s)>0$ and $\Phi([\Delta(s)])=0$. Section 7.4.10 below complements this by exhibiting an explicit non-exact 1-cochain $\omega\in C^1$ on the two-edge carrier with strictly positive quotient norm $\Phi([\omega])=2>0$.
2. **Notation for sheaf Laplacians.** Whenever a Hilbert-space completion is introduced on a finite carrier, we write $L_0 := d_0^{*} d_0$ for the 0-cochain Hodge Laplacian so as not to collide with the covering-edge coboundary operator $\Delta$ of §2.2.

#### 7.4.9 Lean 4 formalization of the visibility-gap propositions

The results of §7.4 are mechanized in `lean4/po000_l004_observer_visibility.lean`:

- Proposition 7.4.3: `PO000.ObserverVisibility.tally_le_rawNorm` and `localGreen_of_globalGreen`.
- Proposition 7.4.4: `PO000.ObserverVisibility.allGreen_iff_kernel`.
- Proposition 7.4.5: `PO000.ObserverVisibility.ThreePatch.three_patch_witness` and `ThreePatch.scaledDefect_is_section_defect`.
- Corollary 7.4.6: `PO000.ObserverVisibility.ThreePatch.rawNorm_scaled` and `ThreePatch.no_recovery_modulus`.
- Corollary 7.4.7: `PO000.ObserverVisibility.rawNorm_eq_zero_of_allGreen` and `coverage_of_jointTrivial`.
- Proposition 7.4.7-B: `PO000.ObserverVisibility.Coupled.full_coverage`, `Coupled.joint_kernel_nontrivial`, and `Coupled.allGreen_forces_zero`.
- §7.4.10: `PO000.ObserverVisibility.QuotientWitness.repair_mass_ge_two`, `QuotientWitness.repair_mass_attained`, and `QuotientWitness.omega_not_exact`.

#### 7.4.10 A fiber-level quotient witness with $\Phi([\omega]) > 0$

On the two-edge carrier of Proposition 7.4.7-B with scalar fibers $F(\cdot)=\mathbb R$ and zero restriction maps $r_{u_i,x}=0$, the coboundary image is the diagonal
$$
\operatorname{im}(d_0)=\{(-\alpha,-\alpha):\alpha\in\mathbb R\} \subset \mathbb R^2.
$$
For the 1-cochain $\omega=(1,-1)\in C^1$, the quotient obstruction norm is
$$
\Phi([\omega])=\inf_{\alpha\in C^0}\lVert\omega-d_0\alpha\rVert_1
=\inf_{\alpha\in\mathbb R}\bigl(|1+\alpha|+|\alpha-1|\bigr)=2>0,
$$
where the lower bound $|1+\alpha|+|1-\alpha|\ge 2$ follows from the triangle inequality and is attained at $\alpha=0$. In particular, $\omega\notin\operatorname{im}(d_0)$.

```python
# quotient mass of omega = (1, -1) against the diagonal im(d0)
masses = [
    abs(1 + a / 8) + abs(a / 8 - 1)
    for a in range(-64, 65)  # alpha = -8 .. 8 in steps of 1/8
]
print(min(masses))  # 2.0, attained at alpha = 0; never below 2
```

---

### 7.5 Phase information discarded by normalized weights

The excitation profile in §5.12 forgets relative directions. A second, finite
Hilbert-space question makes that loss quantitative. Fix weights $p_j\ge0$,
$\sum_jp_j=1$, and declare the **full complex phase fiber**
$$
\mathcal F_p=\{c:c_j=\sqrt{p_j}e^{i\theta_j},\ \theta_j\in\mathbb R\}.
$$
These are hypotheses about the admitted carrier. A finite sign carrier,
a list of Gaussian vectors, or an independently phase-complete Hilbert carrier
need not have the same attainable outputs. None is selected by normalization.

**Theorem 7.5 (phase interval and scalar minimax).** For a fixed complex row
$a$, put $r_j=|a_j|\sqrt{p_j}$, $R=\sum_jr_j$, and
$\ell=\max(0,2\max_jr_j-R)$. Then
$$
\{|ac|^2:c\in\mathcal F_p\}=[\ell^2,R^2].
$$
The best deterministic scalar prediction from $p$ alone, under worst absolute
error on this fiber, is
$$
m_a(p)=\tfrac12(R^2+\ell^2),\qquad
\varepsilon_a(p)=\tfrac12(R^2-\ell^2).
$$
When $\lVert a\rVert_2\le1$, $a^*a$ is an effect and the interval lies in $[0,1]$.
For a general row the interval formula remains algebraic but is not necessarily
a probability interval.

*Proof.* Absorb the arguments of $a_j$ into the independent phases. The
triangle and reverse-triangle inequalities give the proposed endpoints. To
establish that all moduli between them are attainable, induct on the lengths. Suppose
previous resultants have moduli $[L,U]$. Adding a vector of length $s$ gives
moduli $[|x-s|,x+s]$ for $x\in[L,U]$. The total image is compact and connected,
as the continuous image of $[L,U]\times S^1$. Its maximum is $U+s$ and its
minimum is $\max(0,L-s,s-U)$. Induction gives exactly $[\ell,R]$, including
zero lengths. Squaring preserves this interval. Any prediction $z$ has
worst error at least half the endpoint separation, since
$R^2-\ell^2\le|R^2-z|+|z-\ell^2|$. The midpoint attains that bound.
Cauchy--Schwarz gives $R\le\lVert a\rVert_2$. $\square$

The minimax midpoint argument applies to any nonempty finite attained set,
using its actual minimum and maximum; the interval assertion requires the
full phase fiber. Supremum and infimum give the same minimax value on a dense
phase subgroup, but the endpoints need not be attained there.

Independent uniform phases, signs, or quarter turns have vanishing cross-term
means, so the ensemble mean is $\bar f=\sum_jr_j^2$. This imports a probability
law on phase choices. It does not define a deterministic answer on the fiber.
In fact, on the full fiber,
$$
\bar f\le m_a(p),
\qquad \bar f=m_a(p)\ \Longleftrightarrow\
              \text{at most two of the }r_j\text{ are positive}.
$$
To see this, let $r=\max_jr_j$ and let $S$ be the sum of the others. If
$r\ge S$, the midpoint is $r^2+S^2$; subtracting
$r^2+\sum_{j\ne j_*}r_j^2$ leaves the nonnegative cross products among the
other lengths, zero exactly when at most one other is positive. If $r\le S$,
$\ell=0$ and
$\bar f\le rR\le R^2/2=m_a(p)$. Equality requires exactly two equal positive
lengths, apart from the zero case. Thus the phase-mean predictor has worst
error $R^2-\bar f$, exceeding minimax by $m_a(p)-\bar f$ whenever three
lengths are active. For $p_j=1/n$, $a_j=1/\sqrt n$ and $n\ge2$, the full
range is $[0,1]$, mean $1/n$, minimax radius $1/2$, and mean worst error
$1-1/n$.

A finite sign example makes the carrier distinction exact. With three equal
input weights and the uniform normalized row, the attained sign values are
$\{1/9,1\}$, whose midpoint and radius are $5/9$ and $4/9$. Full complex
phases attain $[0,1]$. A different, explicitly specified sign fixture is
$$
z=(2s_1,s_2,s_3),\quad s_j\in\{-1,1\},\quad
 a=(1/2,1/4,1/8),\quad \lVert z\rVert^2=6.
$$
It gives
$$
\frac{|az|^2}{6}=\frac{(8s_1+2s_2+s_3)^2}{384}
 \in\frac{\{25,49,81,121\}}{384}.
$$
The mean is $23/128$, midpoint $73/384$, radius $1/8$, and mean worst error
$13/96$. Each value occurs twice among the eight sign choices. This is a
reconstructed fixture for the supplied fractions, not a claim to have recovered
unsupplied original input data. Here the largest length dominates, so the full
phase endpoints happen to agree with the sign endpoints. The preceding equal
length example supplies the strict endpoint gap. The phrase “Gaussian host”
alone specifies neither example: Gaussian-integer modulus fibers can contain
more than four phases, and Gaussian-rational unit phases form an infinite dense
subgroup. An exact finite-host claim must provide its actual admitted list or
group and its arithmetic comparison rule.

**Proposition 7.6 (effect-specific descent and resolution).** For a Hermitian
effect $E$, the readout $c^*Ec$ is constant on $\mathcal F_p$ if and only if
$E_{ij}=0$ for distinct active coordinates $i,j$ with $p_ip_j>0$. It descends
to weights on every profile if and only if $E$ is diagonal.

*Proof.* Its phase expansion is
$$
\sum_jp_jE_{jj}+\sum_{i\ne j}\sqrt{p_ip_j}E_{ij}
                               e^{i(\theta_j-\theta_i)}.
$$
The nontrivial characters are distinct on the full independent torus.
Integrating against each character shows that constancy forces exactly the
stated coefficients to vanish. The converse is direct. $\square$

For an orthogonal block decomposition, the observer
$\mathcal D(\rho)=\sum_bP_b\rho P_b$ retains each entire diagonal block.
On all density matrices a Hermitian readout descends through $\mathcal D$
if and only if $E=\mathcal D(E)$. Indeed equality of the readouts on
$\rho$ and $\mathcal D(\rho)$ is equivalent to
$\operatorname{Tr}((E-\mathcal D(E))\rho)=0$ for every density.
An observer retaining only block populations $\operatorname{Tr}(P_b\rho)$
is coarser: its criterion is $E\in\operatorname{span}_{\mathbb R}\{P_b\}$,
so $E$ must be scalar on each block. For blocks $\{1,2\}\mid\{3\}$,
$E=\operatorname{diag}(1,0,0)$ is block diagonal, yet $|1\rangle$ and
$|2\rangle$ have equal block populations and readouts one and zero.

A smaller phase host changes even the necessity direction. On independent
real-sign lifts, constancy only forces $\operatorname{Re}E_{ij}=0$ on active
pairs. The effect $E=(I+Y)/2$ has readout $1/2$ on every
$(\pm1,\pm1)/\sqrt2$, but gives one and zero on $(1,\pm i)/\sqrt2$.
Independent quarter turns expose both off-diagonal components. For a correlated
finite diagonal group, coefficients sharing the same character must first be
summed; they may cancel. Similarly, coarse measurement outcomes can cancel
phase sensitivity: two Hadamard rank-one effects are individually sensitive,
whereas their sum $I$ is constant. Every descent statement must therefore
name both the phase carrier and the resolved readout.

### 7.6 Prediction under dynamics and completed linear observers

Let $H=H^*$, $U(t)=e^{-itH}$, and let the initial observer retain only the
weights $p$. For one fixed output $i$,
$$
\dot p_i(0)=2\operatorname{Im}\left(\overline c_i\sum_jH_{ij}c_j\right).
$$
On the full complex phase fiber this has the exact range
$$
[-B_i(p),B_i(p)],\qquad
 B_i(p)=2\sqrt{p_i}\sum_{j\ne i}|H_{ij}|\sqrt{p_j}.
$$
The diagonal term is real; align each off-diagonal summand to the positive or
negative imaginary axis to attain either endpoint. Connectedness supplies the
intermediate values. The scalar derivative minimax radius is $B_i(p)$.
This aligns one output at a time. Conservation of total probability prevents
independent simultaneous endpoint choices for every coordinate.

**Theorem 7.7 (exact all-time scalar prediction and a short-time floor).** At
any fixed real time, set
$$
r_j(t)=|U(t)_{ij}|\sqrt{p_j},\quad R_i(t)=\sum_jr_j(t),\quad
\ell_i(t)=\max(0,2\max_jr_j(t)-R_i(t)).
$$
The possible $i$th populations are exactly
$[\ell_i(t)^2,R_i(t)^2]$, with minimax radius
$$
\varepsilon_i(p,t)=\tfrac12(R_i(t)^2-\ell_i(t)^2)
$$
and midpoint half the sum of those endpoints. If
$h=\inf_{c\in\mathbb R}\lVert H-cI\rVert_\infty$
(the half spectral diameter), then for $t\ge0$
$$
\varepsilon_i(p,t)\ge\max\{0,tB_i(p)-2h^2t^2\}.
$$
If $p_i>0$, $\varepsilon_i(p,t)=tB_i(p)+O(t^2)$ as $t\downarrow0$.

*Proof.* Apply Theorem 7.5 to row $i$ of $U(t)$. For the lower bound, the
second derivative of the $P_i$ expectation is bounded by
$\lVert [H,[H,P_i]]\rVert_\infty\le4h^2$. Each of the two derivative-endpoint
lifts therefore has Taylor remainder at most $2h^2t^2$, giving a separation
at least $2tB_i-4h^2t^2$. Half this separation is a prediction lower bound.
For the asymptotic statement, $r_i(t)=\sqrt{p_i}+O(t^2)$ and
$\sum_{j\ne i}r_j(t)=t\sum_{j\ne i}|H_{ij}|\sqrt{p_j}+O(t^2)$.
The $i$th length dominates for small positive time, and half the difference
of the squared sum and squared difference equals twice their product.
$\square$

If $p_i=0$, every first derivative vanishes, but future ambiguity can start at
second order. For
$$
H=\begin{pmatrix}0&1&1\\1&0&0\\1&0&0\end{pmatrix},\qquad
p=(0,1/2,1/2),
$$
the bright lift $(0,1,1)/\sqrt2$ and dark lift $(0,1,-1)/\sqrt2$ give output
zero populations $\sin^2(\sqrt2t)$ and $0$. The full-phase range is
$[0,\sin^2(\sqrt2t)]$ and radius half its upper endpoint. A vanishing
first-order coefficient therefore does not establish future descent. For
$H=X$, $p=(1/2,1/2)$ the full-phase radius is $|\sin(2t)|/2$, but the
real-sign lifts are eigenrays and have constant weights at every time.

All these midpoint assertions concern one scalar output. Componentwise scalar
midpoints need not be a probability vector. For the three-dimensional Fourier
unitary and uniform input weights, every output has interval $[0,1]$, so their
midpoints sum to $3/2$. The fiber contains every output simplex vertex. If a
predictor must itself be a probability vector, those vertices force worst
$\ell^\infty$ error at least $1-\min_iq_i\ge2/3$; the uniform predictor
attains $2/3$. The scalar radius $1/2$ is not a joint distribution certificate under general couplings.

The finite-QM observer-completion results [19] suggest a second, exactly
soluble carrier. Here admit **all density matrices** on $\mathbb C^d$ and
linear statistics $q_j(\rho)=\operatorname{Tr}(A_j\rho)$, with Hermitian
$A_j$. Include the known trace coordinate by setting
$\mathcal S=\operatorname{span}_{\mathbb R}\{I,A_1,\ldots,A_m\}$.

**Theorem 7.8 (linear sufficiency and norm-distance minimax).** A Hermitian
readout $\operatorname{Tr}(E\rho)$ factors through $q$ on the full density
carrier if and only if $E\in\mathcal S$. More generally its global worst-case
scalar prediction error is
$$
\inf_f\sup_{\rho}\bigl|\operatorname{Tr}(E\rho)-f(q(\rho))\bigr|
                 =\inf_{B\in\mathcal S}\lVert E-B\rVert_\infty.
$$
The supremum is over density matrices, and arbitrary deterministic scalar
functions are admitted. An affine estimator already attains this global
optimum. This formula does not compute the radius of each restricted pure
phase fiber separately.

*Proof.* Membership gives an affine formula using the trace. If $E\notin \mathcal S$,
let $D\ne0$ be its Hilbert--Schmidt projection onto
$\mathcal S^\perp$. Then $D$ is Hermitian, traceless, and orthogonal to each
$A_j$, while $\operatorname{Tr}(ED)=\lVert D\rVert_{\mathrm{HS}}^2>0$.
For sufficiently small $\epsilon>0$, the densities $I/d\pm\epsilon D$
have equal reports and distinct readouts. This establishes necessity using actual
physical states.

Write $\delta=\operatorname{dist}_\infty(E,\mathcal S)$. Finite-dimensional
norm duality yields
$$
\delta=\max\{\operatorname{Tr}(ED):D=D^*\in\mathcal S^\perp,
                                         \ \lVert D\rVert_1\le1\}.
$$
Because $I\in\mathcal S$, all these $D$ are traceless. Every Hermitian
traceless $D$ with $\lVert D\rVert_1\le2$ is the difference of two densities: in its
Jordan decomposition $D=D_+-D_-$ the two traces equal some $a\le1$; add
$(1-a)\tau$ to both parts for any density $\tau$. If $D\perp\mathcal S$,
the resulting densities have equal reports. Conversely every equal-report
difference is in $\mathcal S^\perp$ and has trace norm at most two.
Thus the maximum readout width of an observer fiber is exactly $2\delta$.
Each fiber is compact; its midpoint attains half its width and its endpoints
force that error. A best $B\in\mathcal S$ exists and gives the affine
estimator $\operatorname{Tr}(B\rho)$ with error at most $\delta$, establishing
attainment also in the affine class. $\square$

A chosen retraction of $E$ need not minimize the operator norm either. For
$E=J_3/3$ and the diagonal observer, dephasing gives $I/3$ with error $2/3$,
whereas $I/2$ gives error $1/2$. The uniform-weight phase fiber attains both
zero and one, so Theorem 7.8 or its endpoint lower bound establishes $1/2$ optimal.

At time $t$, sufficiency replaces $E$ by its Heisenberg evolution
$U(t)^*EU(t)$. The smallest invariant real observation space containing
$I,A_1,\ldots,A_m$ is the span of
$$
I,\quad (\mathcal L^*)^rA_j\quad(0\le r<d^2),\qquad
\mathcal L^*(A)=i[H,A].
$$
Cayley--Hamilton gives invariance, and every invariant containing space contains
all these iterates. This is the finite row-space completion principle of [19]
on the admitted density carrier. It counts linear statistics, not samples,
bits, or simultaneously measurable sharp observables. For example observing
$Z$ under $H=X$ requires $Y$ for closure, and $Y$ does not commute with $Z$.
On a restricted carrier ambient span membership remains sufficient, but need
not be necessary.

The same sufficiency question can be posed before choosing a Hilbert carrier:
which admitted histories have equal answers after every available continuation?
Section 7.10 relates this protected-history quotient to the linear completion
above. The quantum calculation assumes density states and Hamiltonian dynamics;
the native finite construction supplies neither assumption by itself.

### 7.7 Curvature together with retained cohomology

Return to a specified finite real cochain complex
$C^0\xrightarrow{d_0}C^1\xrightarrow{d_1}C^2$, with $d_1d_0=0$,
$B=\operatorname{im}d_0$, and quotient norm
$\Phi(\omega)=\operatorname{dist}(\omega,B)$. Let
$\ell:C^1\to Y$ be a linear report into a finite-dimensional normed space,
and require $\ell B=0$. This requirement makes it a report on repair classes.

**Theorem 7.9 (augmented quotient observability).** The map
$$
[\omega]\longmapsto(d_1\omega,\ell\omega)
$$
is injective on $C^1/B$ if and only if the induced $\ell$ is injective on
$H^1=\ker d_1/B$. These conditions are equivalent to the existence of a finite
constant $K$ such that
$$
\Phi(\omega)\le K\bigl(\lVert d_1\omega\rVert+\lVert \ell\omega\rVert\bigr)
\quad\text{for every }\omega\in C^1.
$$

*Proof.* The kernel consists exactly of classes represented in
$\ker d_1\cap\ker\ell$. It is zero precisely when $\ell$ separates
$H^1$. An injective linear map from the finite-dimensional quotient has a
bounded inverse on its image, which gives the estimate for the sum norm.
Conversely the estimate forces every zero-report class to have zero quotient
norm and hence to be zero. $\square$

For an explicit constant, it suffices to exhibit linear lifts $R:C^2\to C^1$
and $S:Y\to C^1$ satisfying
$$
\omega-Rd_1\omega-S\ell\omega\in B.
$$
Then $\Phi(\omega)\le\lVert R\rVert\lVert d_1\omega\rVert+\lVert S\rVert\lVert \ell\omega\rVert$.
Such lifts exist in finite dimensions when the augmented map is injective:
extend its inverse from its image and lift a basis of the quotient.
Their norms, however, need not be uniform across a family.

For example, take coordinates $(b,x,y)$ with $\ell^1$ norm, repair line
$B=\mathbb R(1,0,0)$, $d_{1,n}(b,x,y)=x/n$ and $\ell(b,x,y)=y$.
Then $\Phi=|x|+|y|$, the augmented map is injective for every $n$, and
$H^1$ retains the $y$ coordinate, but its best $K$ is $n$. Fixed dimension
and algebraic observability alone give no uniform lower singular bound.
There is also a positive uniform example retaining nonzero cohomology:
take direct sums of $N$ fixed blocks with $d_1(b,x,y)=x$ and $\ell(b,x,y)=y$,
using sum norms. Then
$\Phi=\lVert d_1\omega\rVert_1+\lVert \ell\omega\rVert_1$ with $K=1$ for every $N$,
and $\dim H^1=N$. This is an explicit linear-complex family; it does not
supply a geometric projection-to-cochain adapter.

### 7.8 A physical cycle adapter and a measurable product-distance bound

We now construct an explicit cochain adapter on a quantum spin ring, providing concrete application data for the abstract framework of §7.2. Number $n\ge5$ qubits cyclically and orient comparison edges $j\to j+1$. Consider the real cellular cochain complex of the unfilled cycle:
$$
 C^0=\mathbb R^n,\quad C^1=\mathbb R^n,\quad C^2=0,\qquad
 (d_0\alpha)_j=\alpha_{j+1}-\alpha_j,\quad d_1=0.
$$
The coboundary space $\operatorname{im} d_0$ consists of discrete cycle gradients, which model local additive calibration shifts across adjacent sites. Because the cycle is unfilled ($C^2=0$), the condition $d_1d_0=0$ holds trivially.

Equip $C^1$ with the intensive $\ell^1$ norm $\lVert \omega\rVert_{1,n}=n^{-1}\sum_j|\omega_j|$ and define the circulation report $\ell\omega=n^{-1}\sum_j\omega_j$. The coboundary space and first cohomology are
$$
 B=\operatorname{im}d_0=\ker\ell,\qquad
 H^1=C^1/B\simeq\mathbb R,\qquad
 \Phi(\omega)=\min_\alpha\lVert \omega-d_0\alpha\rVert_{1,n}
             =|\ell\omega|.
$$
Indeed, telescoping around the cycle gives $B\subseteq\ker\ell$, and any zero-sum vector integrates around the cycle to a periodic potential in $C^0$. For an arbitrary 1-cochain $\omega$, subtracting its mean $\ell\omega$ yields a zero-sum coboundary whose constant residual attains the triangle-inequality lower bound $|\ell\omega|$. Consequently, $\ker\ell = B$ and the quotient conditioning constant in Theorem 7.9 is $K=1$ for every ring size $n\ge 5$.

Fix the norm-one observables
$$
 K_j=Z_{j-1}X_jZ_{j+1},\qquad
 \mathcal O_n=\{K_j,X_j,Z_j:0\le j<n\},\qquad
 d_{\mathcal O_n}(\rho,\sigma)
    =\max_{O\in\mathcal O_n}|\operatorname{Tr}O(\rho-\sigma)|.
$$
Let $\mathcal P_n=\{\bigotimes_j\sigma_j\}$ denote the set of $n$-qubit product states, $\Pi\rho=\bigotimes_j\rho_j$ the marginal product retraction, and define the linear evaluation map $A_n(X)_j=\operatorname{Tr}(K_jX)$ together with the induced 1-cochain
$$
 \omega(\rho)=A_n(\rho-\Pi\rho),\qquad
 \omega_j(\rho)=\langle K_j\rangle_\rho
       -\langle Z_{j-1}\rangle_\rho
        \langle X_j\rangle_\rho\langle Z_{j+1}\rangle_\rho.
$$
Each coordinate $\omega_j(\rho)$ depends only on the three-site marginal on $\{j-1,j,j+1\}$, and cyclic site translations intertwine $A_n$, $\Pi$, and the shift operators on $C^0$ and $C^1$.

**Theorem 7.10 (physical obstruction and measurement error).** For every $n$-qubit density matrix $\rho$,
$$
 \boxed{\quad
 \inf_{\sigma\in\mathcal P_n}d_{\mathcal O_n}(\rho,\sigma)
       \ge\tfrac14\Phi\bigl(A_n(\rho-\Pi\rho)\bigr).
 \quad}
$$
If all displayed moment estimates have simultaneous absolute error at most $\epsilon$ and are clipped to $[-1,1]$, let $\widehat\omega$ denote the resulting empirical cochain. Then
$$
 \inf_{\sigma\in\mathcal P_n}d_{\mathcal O_n}(\rho,\sigma)
 \ge \max\{0,\tfrac14|\ell\widehat\omega|-\epsilon\}.
$$
Adding any cycle gradient $d_0\alpha$ to $\omega$ or $\widehat\omega$ leaves both lower bounds invariant.

*Proof.* For any product state $\sigma \in \mathcal P_n$, the expectation $\langle K_j\rangle_\sigma$ factorizes into the product of the three single-site expectations. Setting $d=d_{\mathcal O_n}(\rho,\sigma)$ and telescoping the three-factor product difference inside $[-1,1]^3$ gives $|\omega_j(\rho)|\le d+3d=4d$. Averaging over $j$, applying $|\ell\omega|\le\lVert \omega\rVert_{1,n}$, and taking the infimum over $\sigma\in\mathcal P_n$ yields the first inequality. The same telescoping bound gives $\lVert \widehat\omega-\omega\rVert_{1,n}\le4\epsilon$ and hence $|\ell\widehat\omega|\le\Phi(\omega)+4\epsilon$. Finally, $\omega(\sigma)=0$ for every $\sigma\in\mathcal P_n$ and $\ell d_0=0$. $\square$

Note that Theorem 7.10 bounds distance to the product manifold $\mathcal P_n$ rather than to the convex hull of separable states; classically correlated mixtures can also carry a nonzero certificate (Hein, Eisert, and Briegel [20]). For product observables of maximum arity $k$, the telescoping constant $4$ generalizes to $k+1$.

**Corollary 7.11 (Ising rings, a uniform onset window, and pair blindness).**
Let
$$
 H_n=J\sum_{j\bmod n}Z_jZ_{j+1},\qquad J\ne0,\qquad
 \rho_n(0)=|+\rangle\langle+|^{\otimes n}.
$$
For every $n\ge5$ and every real time $t$,
$$
 \omega_j(\rho_n(t))=-\sin^2(2Jt),\qquad
 \Phi(\omega(\rho_n(t)))=\sin^2(2Jt),
$$
and therefore
$$
 \begin{aligned}
 \inf_{\sigma\in\mathcal P_n}d_{\mathcal O_n}(\rho_n(t),\sigma)
 &\ge\tfrac14\sin^2(2Jt),\\
 \tfrac14\sin^2(2Jt)&\ge J^2t^2-\tfrac43J^4t^4
 \ge\tfrac23J^2t^2
 \quad (|t|\le(2|J|)^{-1}).
 \end{aligned}
$$
Both the onset window and the prefactors are independent of the ring size $n$. For inhomogeneous bond couplings $J_j$, the exact coordinate is $-\sin(2J_{j-1}t)\sin(2J_jt)$, whose sign-alternating terms can cancel in the cycle average $\ell\omega$.

*Proof.* All bond terms commute. In the Heisenberg evolution of $K_j$, only the two incident bond terms $Z_{j-1}Z_j$ and $Z_jZ_{j+1}$ anticommute with $X_j$. Expanding each conjugation via $e^{i\theta P}Qe^{-i\theta P}=Q\cos(2\theta)+iPQ\sin(2\theta)$ for $P^2=I$ and $\{P,Q\}=0$ leaves $-X_j\sin^2(2Jt)$ as the unique term with nonzero expectation in $|+\rangle^{\otimes n}$. All single-site $Z$ expectations vanish identically, so the product correction is zero and Theorem 7.10 yields the distance bound. On $0\le x\le1$, $\sin x\ge x-x^3/6\ge0$ implies $\sin^2x\ge x^2-x^4/3$; substituting $x=2|Jt|$ completes the proof. $\square$

Along this trajectory, all nonempty $Z$-only moments vanish, so every proper-partition product in the three-site connected scalar cumulant of $(Z_{j-1},X_j,Z_{j+1})$ vanishes and the connected cumulant coincides with $\omega_j(\rho_n(t))$, with leading coefficient $-4J^2$ and Steiner length $\tau=2$.

At the graph-state time $t_* =\pi/(4|J|)$, all pairwise product defects vanish while the three-body cochain obstruction attains its maximum $\Phi(\omega(\rho_n(t_*))) = 1$. This phenomenon extends to general higher-degree interaction graphs as follows.

**Theorem 7.12 (Higher-Degree Graph-State Minimax Theorem).** Let $G=(V,E)$ be a finite simple graph with minimum degree $d_{\min} \ge 2$. Evolve the initial product state $|+\rangle^{\otimes |V|}$ under the Ising Hamiltonian $H = J \sum_{\{u,v\}\in E} Z_u Z_v$ ($J \ne 0$) to the graph-state time $t_* = \pi/(4|J|)$, with unitary $U(t_*) = e^{-it_* H}$.
Then:
1. *Complete Two-Body Marginal Blindness:*
   - If $G$ has girth at least $4$ (triangle-free), then for every edge $e=\{u,v\}\in E$ the two-site reduced density matrix is maximally mixed,
     $$
     \rho_{uv}(t_*) = \frac{I_4}{4},
     $$
     and the pairwise product defect vanishes identically across $E$:
     $$
     D_e(t_*) = \lVert \rho_e(t_*) - \rho_u(t_*)\otimes\rho_v(t_*)\rVert_1 = 0, \qquad C(t_*) = \sum_{e\in E} D_e(t_*) = 0.
     $$
   - If $G$ has girth at least $5$, then $\rho_{uv}(t_*) = I_4/4$ holds for *every* pair of distinct vertices $\{u,v\} \subset V$, whether adjacent or non-adjacent.
2. *Degree-Parity Stabilizers and Minimax Product Separation:* Under $U(t_*)$, the Heisenberg evolution of $X_v$ at a vertex $v$ of degree $d_v$ is
   $$
   U(t_*)^\dagger X_v U(t_*) = \bigl(i\operatorname{sign}(J) Z_v\bigr)^{d_v} X_v \prod_{w\in N(v)} Z_w.
   $$
   Define the local transverse Pauli operator $O_v := X_v$ when $d_v$ is even and $O_v := Y_v$ when $d_v$ is odd, and set $K_v := O_v \prod_{w\in N(v)} Z_w$, so that $\lvert\langle K_v\rangle_{\rho(t_*)}\rvert = 1$ for every $v\in V$. (Equivalently, applying the single-qubit $Z$-rotation gauge $V_{\mathrm{loc}} = \prod_{v\in V} \exp(i\frac{\pi}{4}\operatorname{sign}(J)d_v Z_v)$, which preserves the product manifold $\mathcal{P}_V$ and all computational-basis marginals, transforms $\rho(t_*)$ into the standard graph state $|G\rangle\langle G|$ with $O_v = X_v$ and $K_v = X_v\prod_{w\in N(v)}Z_w$ for all $d_v$ [20].)
   Let $\mathcal{O}_G = \{K_v, O_v, Z_v : v\in V\}$. For any $d$-regular graph $G$ ($d \ge 2$) of girth at least $4$, every product state $\tau = \bigotimes_{v\in V} \tau_v \in \mathcal{P}_V$ satisfies the universal product lower bound
   $$
   d_{\mathcal{O}_G}(\rho(t_*), \tau) = \max_{A\in\mathcal{O}_G} \lvert\operatorname{Tr}(A\rho(t_*)) - \operatorname{Tr}(A\tau)\rvert \ge r_d,
   $$
   where $r_d \in (0,1)$ is the unique positive real root of the polynomial master equation
   $$
   r_d^{d+1} + r_d - 1 = 0.
   $$
   Moreover, $r_d$ is the exact minimax value over the relaxed box $(\langle O_v\rangle, \langle Z_v\rangle) \in [-1,1]^{2|V|}$. On the true quantum product manifold $\mathcal{P}_V$, where each single-qubit factor obeys the Bloch-disk positivity constraint $\langle O_v\rangle_{\tau_v}^2 + \langle Z_v\rangle_{\tau_v}^2 \le 1$, the exact minimax distance is
   $$
   \inf_{\tau\in\mathcal{P}_V} d_{\mathcal{O}_G}(\rho(t_*), \tau) = r_d^{\mathrm{Q}} := \min_{\substack{x, z \in [0, 1] \\ x^2 + z^2 \le 1}} \max\bigl\{1 - x z^d,\; x,\; z\bigr\}.
   $$
   For $d \in \{1,2\}$, $r_d\sqrt{2} < 1$ so the Bloch constraint is inactive and $r_d^{\mathrm{Q}} = r_d$ (attained in the interior at $x = z = r_d$); for $d \ge 3$, $r_d > 1/\sqrt{2}$ so the Bloch boundary $x^2+z^2=1$ is active and $r_d^{\mathrm{Q}} > r_d$ is the unique root $z \in (1/\sqrt{2}, 1)$ of $1 - z^d\sqrt{1-z^2} = z$.
3. *Closed-Form and Numerical Minimax Constants:* Both $r_d$ and $r_d^{\mathrm{Q}}$ increase strictly with degree $d$:
   - For $d=1$ (scalar optimization reference, outside this theorem’s $d_{\min}\ge2$ premise): $r_1 = r_1^{\mathrm{Q}} = \frac{\sqrt{5}-1}{2} \approx 0.6180339887$;
   - For $d=2$ (1D cycle graph, $n\ge 5$): $r_2 = r_2^{\mathrm{Q}} = \frac{(108+12\sqrt{93})^{1/3}}{6} - \frac{2}{(108+12\sqrt{93})^{1/3}} \approx 0.6823278038$;
   - For $d=3$ (2D honeycomb lattice): polynomial lower bound $r_3 \approx 0.7244919590$, exact quantum minimax $r_3^{\mathrm{Q}} \approx 0.7324640561$;
   - For $d=4$ (2D square lattice): polynomial lower bound $r_4 \approx 0.7548776662$, exact quantum minimax $r_4^{\mathrm{Q}} \approx 0.7732827496$;
   - For $d\ge3$, $1 - \frac{\ln(d+1)}{d+1} \le r_d < r_d^{\mathrm{Q}} < 1$, so both tend to $1$ as $d\to\infty$.
4. *Bounded Measurement Settings:* All observables in $\mathcal{O}_G$ can be measured in at most
   $$
   M_{\mathrm{settings}} \le \chi(G^2) + 1 \le \Delta(G)^2 + 2
   $$
   joint product Pauli measurement settings, independent of $|V|$, where $\chi(G^2)$ is the chromatic number of the distance-$2$ square graph $G^2$.

*Proof.* 1. *Two-Body Marginal Blindness:* Expand $\rho_{uv}(t_*) = \operatorname{Tr}_{V\setminus\{u,v\}}\rho(t_*)$ in the computational basis $\{|x\rangle : x\in\{0,1\}^V\}$. Since $|+\rangle^{\otimes |V|} = 2^{-|V|/2}\sum_x |x\rangle$ and $Z_a|x\rangle = (-1)^{x_a}|x\rangle$, the matrix element $\langle x_u x_v|\rho_{uv}(t_*)|y_u y_v\rangle$ is $2^{-|V|}$ times the sum over $z \in \{0,1\}^{V\setminus\{u,v\}}$ of the phase
$$
\exp\!\left(-i\frac{\pi}{4}\operatorname{sign}(J)\sum_{\{a,b\}\in E}
\bigl((-1)^{\tilde x_a+\tilde x_b}-(-1)^{\tilde y_a+\tilde y_b}\bigr)\right),
$$
where $\tilde x, \tilde y$ agree with $z$ on $V\setminus\{u,v\}$ and take the values $(x_u,x_v)$ and $(y_u,y_v)$ on $\{u,v\}$. Terms in $E$ disjoint from $\{u,v\}$ cancel identically between $\tilde x$ and $\tilde y$. For each $w \in V\setminus\{u,v\}$, write $s_w = (-1)^{z_w} \in \{\pm 1\}$; the factor depending on $z_w$ is $(-i\operatorname{sign}(J))^{\alpha_w s_w}$ where
$$
\alpha_w = \mathbf{1}_{\{u,w\}\in E}\bigl((-1)^{x_u} - (-1)^{y_u}\bigr)/2 + \mathbf{1}_{\{v,w\}\in E}\bigl((-1)^{x_v} - (-1)^{y_v}\bigr)/2 \in \{-2,-1,0,1,2\}.
$$
Whenever $\alpha_w = \pm 1$, summing over $s_w \in \{+1,-1\}$ gives $(-i\operatorname{sign}(J)) + (i\operatorname{sign}(J)) = 0$.
If $e=\{u,v\}\in E$ and $G$ has girth $\ge 4$, then $N(u)\cap N(v) = \emptyset$. Since $d_{\min} \ge 2$, if $x_u \ne y_u$ there exists $w \in N(u)\setminus\{v\}$, and because $w \notin N(v)$ one has $\alpha_w = \pm 1$, so the sum over $z_w$ vanishes; symmetrically, if $x_v \ne y_v$ there exists $w' \in N(v)\setminus\{u\}$ with $\alpha_{w'} = \pm 1$. (Note that $d_{\min}\ge 2$ is sharp: if $u$ were a leaf with $N(u)=\{v\}$, then $U(t_*)^\dagger(Y_u Z_v)U(t_*) = \pm X_u$ would give $\langle Y_u Z_v\rangle_{\rho(t_*)} = \pm 1 \ne 0$ and $\rho_{uv}(t_*)\ne I_4/4$.) If $G$ has girth $\ge 5$, any two non-adjacent vertices $u \ne v$ share at most one common neighbor, and since $d_u, d_v \ge 2$, each has at least one neighbor not adjacent to the other, again giving a vertex $w$ with $\alpha_w = \pm 1$ whenever $(x_u,x_v) \ne (y_u,y_v)$. The diagonal entries ($x_u=y_u, x_v=y_v$) equal $1/4$, so $\rho_{uv}(t_*) = I_4/4$ and $D_e(t_*) = 0$.

2. *Degree-Parity Stabilizers and Minimax Separation:* Since $Z_u Z_w$ commutes with $X_v$ unless $v\in\{u,w\}$ and $e^{i(\pi/4)\operatorname{sign}(J)Z_v Z_w} X_v e^{-i(\pi/4)\operatorname{sign}(J)Z_v Z_w} = (i\operatorname{sign}(J)Z_v)X_v Z_w$, multiplying over the $d_v$ incident edges $w\in N(v)$ yields the displayed Heisenberg formula. Using $Z_v X_v = iY_v$, the factor $(i\operatorname{sign}(J)Z_v)^{d_v}X_v$ equals $(\operatorname{sign}(J))^{d_v}(-1)^{\lceil d_v/2\rceil} O_v = \pm O_v$, so $U(t_*)^\dagger K_v U(t_*) = \pm X_v$ has expectation $s_v := \langle K_v\rangle_{\rho(t_*)} \in \{+1,-1\}$, while $\langle O_v\rangle_{\rho(t_*)} = \langle Z_v\rangle_{\rho(t_*)} = 0$ because $d_v \ge 2$ and girth $\ge 4$ make $\rho_v(t_*) = I_2/2$.

Now let $\tau = \bigotimes_{v\in V}\tau_v \in \mathcal{P}_V$ and put $\delta = d_{\mathcal{O}_G}(\rho(t_*),\tau)$, $x_v = \langle O_v\rangle_{\tau_v}$, and $z_v = \langle Z_v\rangle_{\tau_v}$. Then $|x_v| \le \delta$ and $|z_w| \le \delta$ for all $w\in N(v)$. Because $K_v = O_v \prod_{w\in N(v)} Z_w$ acts on distinct vertices $\{v\}\cup N(v)$, its expectation in $\tau$ factorizes:
$$
\lvert\langle K_v\rangle_\tau\rvert = |x_v| \prod_{w\in N(v)} |z_w| \le \delta \cdot \delta^d = \delta^{d+1}.
$$
By the triangle inequality, $1 = |s_v| \le |s_v - \langle K_v\rangle_\tau| + |\langle K_v\rangle_\tau| \le \delta + \delta^{d+1}$. Since $f_d(\delta) = \delta^{d+1} + \delta$ is strictly increasing on $[0,\infty)$ with $f_d(r_d) = 1$, we obtain $\delta \ge r_d$. Over the relaxed box $(x_v,z_v)\in[-1,1]^{2|V|}$, setting $x_v = s_v r_d$ and $z_v = r_d$ attains $\delta = r_d$.

On the quantum product manifold $\mathcal{P}_V$, positivity of each single-qubit state $\tau_v$ requires $x_v^2 + z_v^2 \le 1$. Choose a vertex $v_* \in V$ attaining $z := \max_{w\in V}|z_w| = |z_{v_*}| \in [0,1]$, and put $x := |x_{v_*}| \in [0,1]$. Then $x^2 + z^2 \le 1$, every neighbor $w\in N(v_*)$ satisfies $|z_w| \le z$, and thus $\lvert\langle K_{v_*}\rangle_\tau\rvert \le x z^d$, which forces
$$
\delta \ge \max\bigl\{1 - x z^d,\; x,\; z\bigr\} \ge r_d^{\mathrm{Q}}.
$$
Conversely, for any $(x,z)\in[0,1]^2$ with $x^2+z^2\le 1$, the site-homogeneous product state $\tau(x,z) = \bigotimes_{v\in V}\frac{1}{2}(I + s_v x\,O_v + z\,Z_v) \in \mathcal{P}_V$ attains $d_{\mathcal{O}_G}(\rho(t_*),\tau(x,z)) = \max\{1 - x z^d, x, z\}$. For $d\in\{1,2\}$, $2r_d^2 < 1$, so $(x,z)=(r_d,r_d)$ lies strictly inside the Bloch disk and attains $r_d^{\mathrm{Q}} = r_d$. For $d\ge3$, $2r_d^2>1$. To establish the constrained optimum, the equation $1-z^d\sqrt{1-z^2}=z$ is equivalent on $(0,1)$ to
$$
\frac{1-z}{1+z}=z^{2d}.
$$
Its left side decreases and its right side increases, giving exactly one root $r$; at $z=1/\sqrt2$ the left side is greater for $d\ge3$, so $r>1/\sqrt2$. Put $z_0=\sqrt{d/(d+1)}$. Bernoulli's inequality gives $z_0^{2d}\ge1/(d+1)$ and hence $z_0^d\sqrt{1-z_0^2}\ge1/(d+1)>1-z_0$, so $r<z_0$. For a proposed error $\delta\in[1/\sqrt2,r)$, maximizing $xz^d$ subject to $x,z\le\delta$ and the disk gives $\delta^d\sqrt{1-\delta^2}$: the circle function $z^d\sqrt{1-z^2}$ increases up to $z_0$, and the remaining box segment increases up to that circle. This maximum is less than $1-\delta$, precluding such an error value. Errors below $1/\sqrt2$ are already excluded by the box lower bound $r_d>1/\sqrt2$. At $z=r$, $x=\sqrt{1-r^2}\le r$ attains error $r$. Thus $r_d^{\mathrm Q}=r>r_d$. The defining root equations show strict increase with $d$.

3. *Measurement Settings:* Two star stabilizers $K_u, K_v$ have disjoint supports whenever $d_G(u,v) \ge 3$. Thus any proper vertex coloring of the distance-$2$ square graph $G^2$ partitions $V$ into at most $\chi(G^2) \le \Delta(G^2)+1 \le \Delta(G)^2+1$ color classes, each of which can be measured in a single product Pauli setting (measuring $O_u$ on the color class and $Z_w$ on all other vertices, which also supplies all single-site $O_u$ expectations). Adding one all-$Z$ setting for $\{Z_v\}_{v\in V}$ gives at most $\chi(G^2)+1 \le \Delta(G)^2+2$ product settings. $\square$

Under observational perturbation or finite-sample estimation error bounded by $\eta$, the distance obeys the stability floor
$$
\inf_{\tau\in\mathcal P_V} d_{\mathcal O_G}(\rho, \tau) \ge \max\{0, r_d^{\mathrm{Q}} - \eta\} \ge \max\{0, r_d - \eta\}.
$$

**Operational measurement procedure and nuisance parameter models.**
Under local additive calibration drift, the reported cochain transforms as $\tilde\omega = \omega + d_0\alpha + \xi$, where $d_0\alpha\in\operatorname{im}(d_0)$ represents localized gradient shifts and $\xi$ represents zero-mean measurement noise with $\lVert \xi\rVert_{1,n}\le\eta$. Because $\ell d_0 = 0$, the quotient functional satisfies
$$
\Phi([\tilde\omega]) = |\ell(\omega + d_0\alpha + \xi)| = |\ell(\omega + \xi)|,
$$
exhibiting exact gauge invariance under additive potential coboundaries $d_0\alpha$.
In contrast, multiplicative detector gain drift $\omega' = g_{\mathrm{det}}^3 \omega$ scales the three-point correlator outside $\operatorname{im}(d_0)$ and satisfies
$$
|\Phi(\omega') - \Phi(\omega)| \le |g_{\mathrm{det}}^3 - 1| \Phi(\omega),
$$
preserving a strictly positive quotient whenever $|g_{\mathrm{det}}^3 - 1| < 1$.
On the 1D cycle ($d=2$), properly coloring $G^2$ requires at most $\chi(C_n^2) \le 5$ colors (and on $C_n$ itself, coloring vertices at distance $\ge 3$ requires at most $5$ settings, or $3$ settings when $3 \mid n$ by grouping non-overlapping three-site supports, plus $1$ all-$Z$ setting). With $N$ independent shots per setting, Hoeffding's inequality and a union bound over the $3n$ single-site and three-site observables certify simultaneous estimation error at most $\epsilon$ with probability at least $1-\delta$ whenever $N\ge 2\epsilon^{-2}\log(6n/\delta)$.

---

### 7.9 Selected finite calculations and their scope

The following calculations complement §§5–7, separating written finite identities from numerical demonstrations.

1. **Rational repair quotients and cumulant constants.** For a finite rational
   differential $d:C^{k-1}\to C^k$, finite linear-programming duality gives
   $$
   \min_\alpha\|\omega-d\alpha\|_1
   =\max_{\|y\|_\infty\le1,\ d^Ty=0}\langle y,\omega\rangle.
   $$
   Rational data admit rational optimal witnesses; any proposed witness must
   still satisfy its constraints and matching objectives. The exact cycle
   certificates in `code/physical_obstruction.py` instantiate this argument,
   not every higher-dimensional complex. Partition enumeration gives
   $a_k=(1,2,6,26,150,1082)$ and $b_k=(1,3,13,75,541,4683)$ for $1\le k\le6$
   under the definitions of §5.14. These support-size constants do not measure
   finite-difference conditioning in time.

2. **Marginal derivative versus residual.** On Hermitian trace-zero two-site
   variations at a density product, partial-trace contraction and tensor norm
   multiplicativity give $\|D\Pi_m Z\|_1\le2\|Z\|_1$. The constant $2$ is sharp:
   at $m=|00\rangle\langle00|$, take
   $Z=|11\rangle\langle11|-|00\rangle\langle00|$. Then
   $D\Pi_m Z=\operatorname{diag}(-2,1,1,0)$, of norm $4$, while $\|Z\|_1=2$.
   The triangle inequality gives $\|(I-D\Pi_m)Z\|_1\le3\|Z\|_1$;
   it does not establish sharpness of $3$. Likewise the product retraction
   is $2$-Lipschitz on density states and its residual is at most
   $3$-Lipschitz. Neither statement says $\|D\Pi_m\|=3$.

3. **Commuting next-nearest-neighbor perturbation.** For
   $H=J_1\sum_jZ_jZ_{j+1}+J_2\sum_jZ_jZ_{j+2}$ on $C_n$, $n\ge5$, all terms
   commute. At $t_*=\pi/(4|J_1|)$, $J_1\ne0$, conjugating the cycle stabilizer
   by the two additional incident $ZZ$ rotations gives
   $$
   \Phi(\omega(t_*))=\cos^2(2J_2t_*)
   =1-\frac{\pi^2}{4}(J_2/J_1)^2+O((J_2/J_1)^4).
   $$
   Terms with an extra nonempty $Z$ string have zero expectation in the
   unperturbed graph state. The quotient is positive precisely when this
   cosine is nonzero; $|J_2/J_1|<1$ suffices, whereas $J_2=J_1$ gives zero.
   This is a commuting perturbation, not evidence of integrability breaking.
   A transverse $X$ field is noncommuting and requires a separate Duhamel
   bound or an explicit evolution calculation.

4. **Plaquettes and retained cohomology.** On $C_4$, the opposite-site
   marginal at graph-state time is $(I+X\otimes X)/4$, with product defect
   $1$, while every edge marginal is $I_4/4$. Filling plaquettes does not
   imply that every non-exact 1-cochain has nonzero curvature: on a square
   torus, the cochain equal to $1$ on positively oriented horizontal edges
   and $0$ on vertical edges is closed and has a nonzero horizontal period.
   Curvature detects nonclosedness. It detects every non-exact class only
   when $H^1=0$; otherwise §7.7 requires the additional cohomology report.

5. **Boundary tangents.** The written two-qubit witness in §5.11.1 separates
   the ambient positivity cone from the product tangent cone. Floating-point
   rank thresholds and unverified polar candidates in
   `code/feasible_tangent_cone.py` remain numerical diagnostics. They do not
   certify either the exact rank stratum or an optimum.

6. **Local noise with an explicit convention.** Use
   $\mathcal L=-i[H,\cdot]+\gamma_z\sum_j\mathcal D_{Z_j}$,
   $\gamma_z\ge0$, with the dissipator convention of §5.4.1. Since
   $\mathcal D_Z^\dagger(X)=-2X$ and $Z$ dephasing commutes with the Ising
   evolution, the ring observable $K_j=Z_{j-1}X_jZ_{j+1}$ obeys
   $$
   \Phi_{\gamma_z}(t_*)=e^{-2\gamma_z t_*}\Phi_0(t_*).
   $$
   A rate defined as transverse attenuation instead would put
   $\gamma_z/2$ in the generator. For $X$ dephasing, the two endpoint $Z$
   factors are damped and the central $X$ is fixed; the dissipator does not
   commute with the Ising generator. An exponential for the initial Pauli
   operator alone therefore does not supply the time-evolved quotient or
   a uniform noise threshold. The general local Lindblad bounds remain
   those of §5.4.1.

7. **Discretization and observer replication.** For fixed bounded generators,
   symmetric Strang splitting has one-step error $O(\Delta t^3)$ and
   accumulated error $O(T\Delta t^2)$ over fixed time $T$, with constants
   depending on the relevant commutators and stability bounds. These are
   approximation orders, not validated numerical error bars. For the
   visibility construction, take upper patches $u_i$ and lower overlaps
   $x_i<u_i,u_{i+1}$ on a $K$-cycle, $K\ge3$, with fibers $\mathbb R^K$,
   identity restrictions, $s(u_i)=e_i$ and $s(x_i)=0$. Its $2K$ covering
   edges each have residual norm $1$, hence $I(s_K)=2K$. Observer $i$
   watches the two edges into $u_i$ and deletes coordinate $i$, so every
   local tally is zero.
   Trace-norm growth for a noncontractive evolution shows why a
   contractivity premise cannot arbitrarily be dropped from its proof; it does
   not make complete positivity or Hermiticity necessary for every bound.
   Transpose, for example, is positive and trace preserving, not completely
   positive in dimension at least two, and is trace-norm isometric.

`code/tests/test_physical_obstruction.py` checks the declared cycle adapter
and finite graph-state examples; `code/tests/test_connected_cumulants.py`
checks specified cumulant calculations. `code/tests/test_po000_e2e_extension.py`
contains selected algebraic and floating-point controls, including the
cluster interference and GHZ examples. Its numerical Duhamel and tangent
outputs have the non-certifying scope stated in §§5.10–5.11. Passing these
files does not prove unrestricted topological, dynamical or reconstruction
claims.

---

### 7.10 Related Foundational Frameworks: Protected Histories and Bell Extensions

Discrete protected history carriers, partition refinement quotients, joint future sufficiency, and positive Bell extensions are developed in companion packages:

- **Finite QM** (`F004_papers/006_finite_qm`, §13.8) develops the operational quantum realization, character cancellation on the sign cube, and the separation between linear gluing, support gluing, and positive Bell cone extensions.
- **PO-035** (`002_projection_obstruction/035_zero_container_relational_spacetime...`) establishes defect 4-current conservation and relational spacetime holonomy.

## Appendix A: Modular Architecture & Sibling Directory

To maintain focus on quantum lattice dynamics, local correlation bounds, and observer visibility, foundational manifold chart constructions and companion developments are coordinated across the research series:

1. **Decoupled Banach Chart Formulations:** The full hierarchy of Banach-manifold chart-derivative formulas, vertical shear retractions, parameter-chart transitions, and bounded left-inverse failure criteria (formerly Lemmas 3.4–3.14 and Examples 3.4–3.14) is omitted from this 69-page edition. These results are preserved in archived monograph revisions `90e6231546` / `d44f760555` and verified by symbolics in `code/retraction_geometry.py`.
2. **Operational Quantum Foundations:** The operational Jordan--Lie reconstruction, positive cone characterizations, canonical trace witnesses, and central-sector purification obstructions (formerly Appendix E) are imported from companion package `Finite QM` (`F004_papers/006_finite_qm`, §13.8) and formalized in `lean4/Po000JordanLie.lean` and `lean4/Po000JordanTrace.lean`.
3. **Coordinated Sibling Packages:** Sibling packages in the `002_projection_obstruction` series and `coda_atlas` are listed in the Authoritative Sibling Reference Table in §1.2.

---

## Appendix B: Exact Constant Ledger for Theorem 5.1

For an observable supported on $k\in\{1,2\}$ sites, support counting gives
$$
\lVert[H,A]\rVert_\infty\le2kg\lVert A\rVert_\infty,
\qquad
\lVert[H,[H,A]]\rVert_\infty
\le4k(k+1)g^2\lVert A\rVert_\infty.
$$
Thus the one-site and two-site reduced-state second derivatives are bounded by $8g^2$ and $24g^2$, respectively, while each one-site first derivative is bounded by $2g$.

For
$$
F_e(t)=\rho_e(t)-\rho_a(t)\otimes\rho_b(t),
$$
the product rule and trace-norm tensor multiplicativity give
$$
\begin{aligned}
\lVert F_e''(t)\rVert_1
&\le
\lVert\ddot\rho_e(t)\rVert_1
+\lVert\ddot\rho_a(t)\rVert_1
+2\lVert\dot\rho_a(t)\rVert_1\lVert\dot\rho_b(t)\rVert_1
+\lVert\ddot\rho_b(t)\rVert_1\\
&\le24g^2+8g^2+8g^2+8g^2\\
&=48g^2.
\end{aligned}
$$
Since $F_e(0)=0$ and $F_e'(0)=n_e$, the integral Taylor formula and reverse triangle inequality yield
$$
D_e(t)=\lVert F_e(t)\rVert_1
\ge t\lVert n_e\rVert_1-\frac{t^2}{2}(48g^2)
=\nu_et-24g^2t^2.
$$
Consequently, on $0<t\le\nu_{\min}/(48g^2)$,
$$
D_e(t)\ge\frac{\nu_{\min}}2t
$$
for every declared active edge with $\nu_e\ge\nu_{\min}$. If at least $\eta\lvert E\rvert$ edges are active and $\lvert E\rvert\ge aN$, then
$$
\frac1N\sum_{e\in E}D_e(t)
\ge
a\eta\bigl(\nu_{\min}t-24g^2t^2\bigr)
\ge
\frac{a\eta\nu_{\min}}2t.
$$
There is no causal-cone radius, Lieb--Robinson error, regular-stratum hypothesis, or positive lower time endpoint in this derivation.

## Appendix C: Extension Map

The research series coordinates specialized geometric, cohomological, and foundational analyses across distinct packages. Sibling packages, titles, anchors, and scopes are specified authoritatively in §1.2:

- **PO-001** (*From Covering-Edge Descent Complexes to Functorial Presheaves and Coherence Defects*, v2.0.0): Saturated-chain presheaves, degree-2 composition curvature cochains $K_{c,b,a}$, and operator cocycle coboundaries.
- **PO-006 (GS-003)** (*Vector and Quantum Observer Geometries: Gauge Relativity and Trace Metric Bounds*, v0.4.0): Non-scalar observer geometries, Schatten-norm operator bounds, dual witness certificates, and phase metrics.
- **PO-007 (GS-001)** (*M-Compatible Gauge Classification for Banach Presheaf Coboundaries: The $\ell^1$ Maximal-Symmetry Endpoint*, v4.7.0): $M$-compatible gauge classification for Banach presheaves; maximal linear symmetry selecting weighted $\ell^1$.
- **PO-008 (GS-002)** (*SO(k)-Invariant Gauge Rigidity for Declared Euclidean Stalks: Local $\ell^2$ Selection and Outer $\ell^1$ Aggregation*, v2.0.0): $SO(k)$-invariant gauge rigidity on Euclidean stalks; local $\ell^2$ selection with outer $\ell^1$ aggregation.
- **PO-009 (GS-000)** (*Coordinate-Wise Additivity and Local $\ell^1$ Gauge Selection*, v6.1.1): Coordinate-wise additivity and local $\ell^1$ gauge selection on finite graph cochains.
- **PO-033** (*Certified Adaptive Quantum Dynamics from Projection Residuals*, v1.0.1): Conditional analytic bounds and uncertified adaptive cluster prototype (heuristic_uncertified / `HEURISTIC_UNCERTIFIED`); Lean scope is conditional finite-sum inequalities over an abstract carrier (`Nat`/`Int`). Validated continuous-time ODE integration and conservative quadrature enclosures on general graphs remain open work.
- **PO-034** (*Higher-Cell Product Retractions, Simplicial Cochains, and Finite Retraction Dynamics*, v0.1.0): Higher-cell product retractions, oblique projectors, simplicial cochain dynamics, and finite-dilation Taylor estimates.
- **PO-035** (*Zero-Container Relational Spacetime, Emergent Lorentz Causality, and Witness Holonomy*, v0.1.0): Defect 4-current conservation ($\partial_\mu J^\mu=0$), discrete relational spacetime, and witness holonomy.
- **Finite QM** (*Finite Quantum Mechanics*, §§13.5–13.8): Operational Jordan--Lie foundations, character cancellation on the sign cube, positive Bell cone extensions, and central-sector purification obstructions.
- **Archived Monograph Material** (Commits `90e6231546` / `d44f760555`; symbolics in `code/retraction_geometry.py`): Banach graph charts, shear retractions, parameter-chart transitions, bounded-left-inverse failure lemmas, and conditional extension reductions (omitted from the 69-page edition).

These companion extensions close distinct gaps exposed by the correction audit. Earlier series labels are historical only. None silently upgrades another paper's imports, mechanization status, or authority.

---

## Data and Code Availability

The v6.9.16 revision connects existing results in §7.10 and operational quantum foundations without adding a primitive-to-quantum reconstruction. The external repository sources in [26] implement native history quotients, joint refinement and exact Bell extensions in the Rust category, WDP and quantum owners. The external Lean modules `GenesisContinuation.lean` and `GenesisJointOperations.lean` prove abstract future/operation laws and integer-weight CHSH bounds; they do not verify the Rust algorithms or the quantum realization. These external sources are pinned navigation references, not additional bundled or newly mechanized proofs of this manuscript. Finite QM [19, §13.8] states the separate scope of `CarrierTests.lean` and its Rust/Python carrier-test interfaces.

The companion software and formalization archive (`PO-000`, release `6.9.18`, Python code `6.9.6`) accompanies this manuscript and is covered by the deterministic checksum manifest `SHA256SUMS` at the package root. Authority status: none; the software, finite replay receipts, and mechanized modules are mathematical and numerical verification artifacts only and confer no operational authority.

The package consists of the following components:

- **Manuscript and Claim Ledgers:** `projection_obstruction.md`, together with the structured claim ledgers `projection_obstruction_claim_ledger.md`, `projection_obstruction_claim_ledger.yaml`, `docs/claim_dependencies.json`, and `projection_obstruction_change_log.md`.
- **Lean 4 Formalization Suite (19 files in `lean4/`):**
  - *Scoped Lake build modules (Lean 4.34.0 / Mathlib v4.34.0):* `lean4/Po000JordanLie.lean` and `lean4/Po000JordanLieImage.lean` (formalizing the complexified associative $C^*$-algebra construction and positive cone of the operational Jordan--Lie algebra), and `lean4/Po000JordanTrace.lean` (formalizing the canonical trace witness, idempotent polynomial projections, and positive definiteness of the central trace).
  - *Arithmetic jet constants:* `lean4/po000_short_time_jets.lean` (checking support-factor and factorial-normalization arithmetic, including the constants $24$, $64$, and $160$ in §§5.8 and 6.3).
  - *Foundational hierarchy and observer-visibility modules:* Fifteen `po000_*.lean` modules, including `po000_l001_replica_hierarchy.lean` (`ReplicaHierarchy`, mechanizing the RE3 singleton decomposition and RE3+RE5 unweighted sum of Theorem 4.2), `po000_l005_weighted_hierarchy.lean` (`PO000.WeightedHierarchy`, mechanizing the weighted and orbit singleton cores of Theorem 4.2 items 2–3 and the former counterexample arithmetic for the withdrawn five-way independence claim), `po000_l004_observer_visibility.lean` (`PO000.ObserverVisibility`, mechanizing Propositions 7.4.3–7.4.5, Corollaries 7.4.6–7.4.7, Proposition 7.4.7-B, and §7.4.10), and `po000_l001_projection_transfer.lean` (`ProjectionTransfer`). The scoped Jordan--Lie and trace build and the historical per-file checks have separate dated records in `lean4/README.md` and `lean4/manifest.json`. Their recorded axiom reports lie within $\{\texttt{propext},\texttt{Classical.choice},\texttt{Quot.sound}\}$; no whole-suite or fresh historical-file elaboration is implied. Parked and package-context-only sources are explicitly labelled there.
- **Python Verification and Exact Replay Suite (`code/` and `code/tests/`):**
  - *TDVP Duhamel and Open-System Bounds (§§5.4.1, 5.10.1–5.10.3):* `code/observable_duhamel.py`, `code/open_system_jets.py`, and `code/tests/test_honeycomb_tdvp_duhamel_integration.py`. The latter compares a sampled Duhamel estimate with floating-point Krylov evolution on an eight-site hexagon-plus-square graph. It supplies neither a honeycomb-lattice example nor a validated continuous-time enclosure; §5.10.A remains a written conditional theorem.
  - *Short-Time Jets, Metric Optimality, Connected Cumulants, and Polynomial Onset (§§5.8, 5.11–5.17, 6.3, 7.5–7.7):* `code/short_time_jets.py`, `code/feasible_tangent_cone.py`, `code/derivation_replays.py`, `code/polynomial_onset.py`, `code/local_persistent_zero.py`, and their corresponding pytest suites in `code/tests/`.
  - *Physical Cycle Adapter, Higher-Degree Graph-State Minimax, and Finite Witnesses (§§7.8–7.9):* `code/physical_obstruction.py`, `code/verify_finite_certificates.py`, `code/verify_certificate.py`, `code/replay.py`, and test suites `code/tests/test_physical_obstruction.py`, `code/tests/test_sharp_onset.py`, and `code/tests/test_po000_e2e_extension.py` (checking selected finite instances related to Theorems 4.3.A, 5.10.B and 7.12, along with the explicitly non-certifying numerical demonstrations described above; no twenty-witness unconstrained certificate is claimed).

To execute the verification suite from the package root:

```bash
python -m pip install ".[jets]"
python -m pytest -q code/tests/test_metric_phase_derivations.py code/tests/test_connected_cumulants.py
python -m pytest -q code/tests/test_short_time_jets.py code/tests/test_polynomial_onset.py
python -m pytest -q code/tests/test_physical_obstruction.py code/tests/test_sharp_onset.py
python -m pytest -q code/tests/test_honeycomb_tdvp_duhamel_integration.py code/tests/test_po000_e2e_extension.py
python code/replay.py --output build/verification/current_run.json
python code/verify_certificate.py build/verification/current_run.json
python scripts/regen_sha256sums.py --check
```

**Scope and evidence boundaries.** Each Lean module or Python test supports only the specific algebraic identity or finite instance it encodes; finite numerical or symbolic replays are not a proof of the general Banach-manifold or infinite-volume theorems. Theorem 3.1 rules out affine-coordinate linearization in a declared affine chart, not arbitrary nonlinear smooth conjugacies. In §5, the raw edge sum $C(t)$ is an overlapping two-site correlation tally, not the global trace norm $\lVert\rho(t)-\bigotimes_v\rho_v(t)\rVert_1$, and Theorems 5.1, 5.5, and 5.7 use direct local commutator estimates rather than Lieb--Robinson bounds (whereas Theorem 5.10.A incorporates Lieb--Robinson light-cone weights for spatially localized observables). Quantum Hilbert spaces and dynamical generators enter §§5–7 as declared host assumptions rather than derivations from obstruction data, and repairable mass $R$ is not defined in this paper. Companion extensions (such as PO-034 and PO-035) address higher-cell adapters and spacetime holonomy separately.

Version provenance: concept DOI `10.5281/zenodo.18896776`; preceding version DOI `10.5281/zenodo.21752743`; license CC-BY-4.0.

---

## Acknowledgments

No external funding. No conflicts of interest.

---

## References

1. E. H. Lieb and D. W. Robinson, "The Finite Group Velocity of Quantum Spin Systems," *Commun. Math. Phys.* **28** (1972), 251--257.
2. S. Mac Lane, *Categories for the Working Mathematician*, Springer, 1971.
3. B. Nachtergaele and R. Sims, "Lieb--Robinson Bounds and the Exponential Clustering Theorem," *Commun. Math. Phys.* **265** (2006), 119--130.
4. S. Bravyi, M. B. Hastings, and F. Verstraete, "Lieb--Robinson Bounds and the Generation of Correlations and Topological Quantum Order," *Phys. Rev. Lett.* **97** (2006), 050401.
5. J. H. Carroll, "M-Compatible Gauge Classification for Banach Presheaf Coboundaries: The $\ell^1$ Maximal-Symmetry Endpoint," Zenodo, 2026. <https://zenodo.org/records/20564214>
6. J. H. Carroll, "L1-Native Cohomology of Defect Fields: Quotient Norms, Dual Circulations, and Hodge Inflation," companion note, 2026 (contextual background only; no result in this paper depends on it).
7. J. H. Carroll, "Coordinate-Wise Additivity and the L1 Norm on Finite Graph Cochains," companion note, 2026 (contextual background only; all additivity and calibration statements used here are proved in Theorem 4.2 and mechanized in `ReplicaHierarchy` and `PO000.WeightedHierarchy`).
8. J. H. Carroll, "General Theory of Finite Obstruction Calculus," companion note, 2026 (contextual background only; the covering-edge passivity inequality used here is proved in Proposition 7.4.3).
9. B. Nachtergaele, Y. Ogata, and R. Sims, "Propagation of Correlations in Quantum Lattice Systems," *J. Stat. Phys.* **124** (2006), 1--13.
10. R. Martinazzo and I. Burghardt, "A local-in-time, minimum-error approach to non-Markovian quantum dynamics," *Phys. Rev. Lett.* **124** (2020), 150601. [doi:10.1103/PhysRevLett.124.150601](https://doi.org/10.1103/PhysRevLett.124.150601).
11. C. Zoufal, D. Sutter, and S. Woerner, "Error bounds for variational quantum time evolution," *Phys. Rev. Applied* **19** (2023), 034057. [doi:10.1103/PhysRevApplied.19.034057](https://doi.org/10.1103/PhysRevApplied.19.034057).
12. J. H. Carroll, "Witnessed Difference Programme," companion note, 2026 (historical series context only).
13. M. J. W. Hall, "Correlation Distance and Bounds for Mutual Information," *Entropy* **15** (2013), 3698--3713. [arXiv:1307.2697](https://arxiv.org/abs/1307.2697); [doi:10.3390/e15093698](https://doi.org/10.3390/e15093698).
14. J. Haegeman, C. Lubich, I. Oseledets, B. Vandereycken, and F. Verstraete, "Unifying time evolution and optimization with matrix product states," *Phys. Rev. B* **94** (2016), 165116. [arXiv:1408.5056](https://arxiv.org/abs/1408.5056); [doi:10.1103/PhysRevB.94.165116](https://doi.org/10.1103/PhysRevB.94.165116).
15. I.-S. Yang, "The Entanglement Timescale," *Phys. Rev. D* **97** (2018), 066008. [arXiv:1707.05792](https://arxiv.org/abs/1707.05792); [doi:10.1103/PhysRevD.97.066008](https://doi.org/10.1103/PhysRevD.97.066008).
16. J. C. Cresswell, "Universal entanglement timescale for Rényi entropies," *Phys. Rev. A* **97** (2018), 022317. [arXiv:1709.10064](https://arxiv.org/abs/1709.10064); [doi:10.1103/PhysRevA.97.022317](https://doi.org/10.1103/PhysRevA.97.022317).
17. B. Aaronson, R. Lo Franco, G. Compagno, and G. Adesso, "Hierarchy and dynamics of trace distance correlations," *New J. Phys.* **15** (2013), 093022. [arXiv:1307.3953](https://arxiv.org/abs/1307.3953); [doi:10.1088/1367-2630/15/9/093022](https://doi.org/10.1088/1367-2630/15/9/093022).
18. J. H. Carroll, "Conditional Hilbert Lifts of $\ell^1$ Sector Weights and Born Normalization Redundancy," companion note, 2026 (restated in §5.12).
19. J. H. Carroll, *Finite Quantum Mechanics*, 2026, §§13.5–13.8. [Manuscript](https://github.com/dbccpage/the_symbol_game/blob/4a4fd192f/omega_engine_atlas/coda_atlas/F004_papers/006_finite_qm/finite_quantum_mechanics.md). The finite linear-observer arguments used here are proved self-containedly in §7.6.
20. M. Hein, J. Eisert, and H. J. Briegel, "Multiparty entanglement in graph states," *Phys. Rev. A* **69** (2004), 062311. [doi:10.1103/PhysRevA.69.062311](https://doi.org/10.1103/PhysRevA.69.062311).
21. S. L. Brunton, B. W. Brunton, J. L. Proctor, and J. N. Kutz, "Koopman Invariant Subspaces and Finite Linear Representations of Nonlinear Dynamical Systems for Control," *PLOS ONE* **11**(2) (2016), e0150171. [doi:10.1371/journal.pone.0150171](https://doi.org/10.1371/journal.pone.0150171).
22. T. Carleman, "Application de la théorie des équations intégrales linéaires aux systèmes d'équations différentielles non linéaires," *Acta Math.* **59** (1932), 63--87.
23. A. Sedoglavic, "A probabilistic algorithm to test local algebraic observability in polynomial time," *J. Symb. Comput.* **33** (2002), 735--755. [doi:10.1006/jsco.2002.0532](https://doi.org/10.1006/jsco.2002.0532).
24. A. F. Villaverde, A. Barreiro, and A. Papachristodoulou, "Structural Identifiability of Dynamic Systems Biology Models," *PLOS Comput. Biol.* **12**(10) (2016), e1005153. [doi:10.1371/journal.pcbi.1005153](https://doi.org/10.1371/journal.pcbi.1005153).
25. M. C. Tran, C.-F. Chen, A. Ehrenberg, A. Y. Guo, A. Deshpande, Y. Hong, Z.-X. Gong, A. V. Gorshkov, and A. Lucas, "Hierarchy of Linear Light Cones with Long-Range Interactions," *Phys. Rev. X* **11** (2021), 011016. [doi:10.1103/PhysRevX.11.011016](https://doi.org/10.1103/PhysRevX.11.011016).
26. *Native joint operations and a Genesis-to-Bell experiment*, The Symbol Game repository, revision `4bdf074a1b18cdeb710d991336e35f8f62979542`, 2026. [Joint experiment](https://github.com/dbccpage/the_symbol_game/blob/4bdf074a1b18cdeb710d991336e35f8f62979542/omega_engine/documentation/rust_crates/omega_wdp/docs/genesis_bell_experiment.md); [stable history carrier](https://github.com/dbccpage/the_symbol_game/blob/4bdf074a1b18cdeb710d991336e35f8f62979542/omega_engine/documentation/rust_crates/omega_wdp/docs/stable_genesis_carrier.md). External source descriptions; their proof and execution scopes are stated separately.
