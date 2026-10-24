<div align="center">

# Bell's Theorem as a Positive-Extension Obstruction

### Projection residuals, uncertainty, and embedded knowledge

**Author:** Jeremy H. Carroll

**Date:** 24 October 2026

**Version:** 0.13.0, research draft for author review

</div>

## Abstract

Bell's theorem gives a precise instance of a general representational problem: locally compatible observations need not admit a realization in a declared global model class. For finite Bell experiments, that class consists of positive distributions over local response assignments with setting-independent weights. We derive witness bounds for the distance to this class, an exactly solvable CHSH family, and uncertainty-adjusted conclusions. Product-state residuals, overlap inconsistency, and positive-extension failure remain distinct. A separate finite observer-fiber theorem characterizes the error caused by retained evidence that identifies histories with different task values. Computation and self-modification preserving that evidence cannot remove the ambiguity; additional informative observations can. The carrier is a mathematical family of possibilities consistent with a declared experiment, not a privileged external observer. Lean proofs verify the positive-extension equivalence for actual probability integrals, classical CHSH witness bounds, the quantum operator and state ceiling with an exact two-qubit realization, finite separable-state construction and the full state-to-behavior bound, attained finite LP duality and tangent-cone onset bounds, conditional dynamical witness bounds, real-parameter CHSH/Mermin negative-mass and contextual-fraction formulas, a certified separation of those measures, a finite-context comparison bound, quantum-restricted family ceilings, an explicit GHZ unitary orbit with exact and uncertainty-delayed exit windows, a full nine-context two-qubit counterexample to the proposed universal quantum bound $CF\le2N_{\min}$, a full 25-context rational quantum counterexample to $CF\le4N_{\min}$, arbitrary-size cycle-parity optimization and its quantum visibility, continuous complete-chain bounds, and the exact finite scalar minimax result. A smoothed Gram construction proves that $CF/N_{\min}$ is unbounded even across complete finite quantum Bell scenarios, including a constructed finite Clifford realization and an end-to-end Lean existence theorem. These results impose task-specific limits on certification without asserting a general impossibility of learning or intelligence.

**Keywords:** Bell inequalities; recursive self-improvement; artificial superintelligence; projection residual; positive extension; observer sufficiency; cochains; embedded knowledge.

# 1 Introduction

Bell's theorem identifies quantum measurement statistics that cannot be reproduced by a locally causal hidden-variable model with a setting-independent hidden-variable distribution [1, 2]. Its geometric content is especially clear in a finite experiment: the admissible local models form a convex polytope, and a violating behavior lies outside that polytope. A Bell inequality is a separating linear functional.

The two source papers [P1, P2] provide a complementary language. A declared reduction retains some structure and discards other structure; the difference between the original object and its reduced representation is a residual. A specified observation map determines which part of that residual is visible. The present paper applies this language to Bell experiments and to the RSI/ASI questions motivating this research. Here RSI means recursive self-improvement: a system uses its current capabilities to modify its later computation or design. ASI means artificial capability exceeding human performance across a declared range of tasks; it is not defined as omniscience. We begin by preserving the distinction between four different questions:

1. Is a quantum state a product of its own marginals?
2. Are the observed distributions compatible on overlapping measurement contexts?
3. Do those distributions admit one positive global distribution over local response assignments?
4. Does a specified cochain construction produce a nonzero cohomology class?

These questions have different answers even in small finite examples. In particular, a classically correlated separable state fails the first condition while satisfying the third for every choice of local measurements. Conversely, quantum Bell violations satisfy overlap consistency but fail positive global extension.

Our central statement is therefore precise: **a Bell violation witnesses an unavoidable residual when an observed behavior is approximated by the complete convex class of Bell-local behaviors.** Calling this a projection residual identifies the failed representation and the distance used to quantify its failure. It does not introduce a physical projection process or supply a local hidden-variable explanation of the violating data.

The positive-extension characterization is closely related to Fine's theorem [3] and the sheaf-theoretic formulation of Abramsky and Brandenburger [4]. Distance to the local polytope is already an established nonlocality measure [5]. We do not claim those constructions as new. Our purpose is to connect them explicitly to the state residuals, observation maps, and dynamical estimates in [P1, P2]. The finite calculations below establish this connection without importing the source papers' broader foundational programme or assuming that every residual is cohomological. Sections 9 and 10 extend the analysis to task sufficiency and self-improvement. Section 11 explains exact reproduction and statistical uncertainty.

Bell infeasibility and prediction ambiguity require different witnesses: the former is an empty positive-local feasible set, while the latter is variation of a task across an existing observation fiber. This distinction is maintained when the paper turns to embedded knowledge and RSI.

# 2 What the product retraction measures

For a bipartite density matrix on a finite-dimensional Hilbert space, define
$$
\Pi_{\rm prod}(\rho)=\rho_A\otimes\rho_B,\qquad
F_\rho=\rho-\Pi_{\rm prod}(\rho),\qquad
D_{\rm prod}(\rho)=\|F_\rho\|_1.
$$
The trace norm here has no factor of one half. Both partial traces of $F_\rho$ vanish. At a product reference $m=m_A\otimes m_B$, the derivative on traceless Hermitian variations is
$$
P_m Z=(\operatorname{Tr}_B Z)\otimes m_B
       +m_A\otimes(\operatorname{Tr}_A Z),\qquad Q_m=I-P_m.
$$
The identities $P_m^2=P_m$ and $Q_m^2=Q_m$ follow from normalization of the factors. In general $P_m$ is oblique. At rank-deficient references its image is the tangent space of the affine product extension, not the full cone of physically feasible velocities. These are the conventions of [P1, Sections 2 and 3.4] and [P2, Sections 2 and 3].

Consider the separable state
$$
\rho_{\rm cl}=\tfrac12|00\rangle\langle00|
                    +\tfrac12|11\rangle\langle11|.
$$
Its product retraction is $I_4/4$, so $D_{\rm prod}(\rho_{\rm cl})=1$. Nevertheless, for arbitrary local POVMs $M_{a|x}$ and $N_{b|y}$,
$$
\operatorname{Tr}[\rho_{\rm cl}(M_{a|x}\otimes N_{b|y})]
=\tfrac12\sum_{j=0}^1
\langle j|M_{a|x}|j\rangle\langle j|N_{b|y}|j\rangle.
$$
This is a local hidden-variable model with shared variable $j$. A product residual detects failure of unconditional independence; Bell locality permits correlations produced by conditioning on a shared variable. Taking the convex closure of local product response behaviors is consequently essential.

There are also two distinct meanings of projection. The map $\Pi_{\rm prod}$ is a particular marginal-preserving retraction and need not give a nearest product state in trace norm [P2, Section 4.1]. Projection onto the Bell-local polytope below is a metric approximation problem in probability space. Its Euclidean minimizer is unique, while its total-variation minimizer need not be.

# 3 Bell locality as positive global extension

## 3.1 The finite experimental model

Alice chooses $x\in X$, Bob chooses $y\in Y$, and their outcomes lie in finite sets $A$ and $B$. A behavior is the table
$$
p=(p(a,b|x,y)),\qquad p(a,b|x,y)\ge0,\qquad
\sum_{a,b}p(a,b|x,y)=1.
$$
The no-signalling conditions require Alice's marginal to be independent of $y$ and Bob's marginal to be independent of $x$. Quantum behaviors
$$
\mathcal M(\rho)(a,b|x,y)
=\operatorname{Tr}[\rho(M_{a|x}\otimes N_{b|y})]
$$
satisfy these conditions, since summing a local POVM gives the identity operator.

A Bell-local behavior has the form
$$
p(a,b|x,y)=\int \mu(d\lambda)\,
p_A(a|x,\lambda)p_B(b|y,\lambda).
\tag{1}
$$
Here $\mu$ is a probability measure on a measurable latent space. Every response coordinate is measurable, nonnegative, and normalized pointwise over its finite outcome set. These assumptions bound each response between zero and one and make the products integrable. The measure $\mu$ is independent of the chosen settings. Equation (1) declares both setting independence and local factorization. Stochastic responses are allowed. No extra assumption that the responses were initially deterministic is required. Conditioning on selected detection events would define a different statistical model and requires its own justification.

Let
$$
\Omega=A^X\times B^Y
$$
be the finite set of complete local response assignments $\lambda=(\alpha,\beta)$. Define the marginalization matrix
$$
T_{(a,b,x,y),(\alpha,\beta)}
=\mathbf1\{\alpha(x)=a,\ \beta(y)=b\}.
$$
Write $\Delta(\Omega)$ for the probability simplex. The local polytope is
$$
\mathcal L=T\Delta(\Omega).
\tag{2}
$$
The assignments are a mathematical representation of the local model; this definition does not assert that incompatible quantum measurements can be jointly performed.

**Theorem 1 (Positive extension).** A behavior satisfies (1) if and only if there is a vector $q\ge0$, with $\sum_\lambda q_\lambda=1$, such that $Tq=p$.

**Proof.** A positive $q$ yields (1) using deterministic responses $\alpha(x)$ and $\beta(y)$. Conversely, from (1) define
$$
q(\alpha,\beta)=\int\mu(d\lambda)
\prod_{x\in X}p_A(\alpha(x)|x,\lambda)
\prod_{y\in Y}p_B(\beta(y)|y,\lambda).
$$
Summing over all assignments gives one. Summing over every assignment coordinate except $\alpha(x)=a$ and $\beta(y)=b$ gives (1). Thus $Tq=p$. $\square$

**Formalization.** The probability-integral equivalence in `Bell.Integral` proves Theorem 1 with Mathlib's Bochner integral. The construction forms the algebra of bounded measurable real functions, proves integrability on the probability space, and derives linearity, positivity and normalization of the integral. Response boundedness follows from nonnegativity and finite normalization. The converse constructs the measure $\sum_\omega q_\omega\delta_\omega$ and proves its normalization and finite-sum integration formula. Thus the integral laws are proved for the declared measure. The algebraic averaging equivalence and the finite stochastic equivalence remain available as separate theorems.

The word *positive* is indispensable. Solving $Tq=p$ over signed real vectors is a weaker problem. Also, increasing the number of values of $\lambda$ cannot circumvent Theorem 1: all stochastic local models already reduce to mixtures of the finitely many deterministic assignments in $\Omega$.

## 3.2 CHSH as a separating witness

Take $X=Y=\{0,1\}$ and $A=B=\{-1,+1\}$. Define
$$
E_{xy}(p)=\sum_{a,b}ab\,p(a,b|x,y),\qquad
S(p)=E_{00}+E_{01}+E_{10}-E_{11}.
$$
For a deterministic assignment,
$$
K(\lambda)=a_0(b_0+b_1)+a_1(b_0-b_1)\in\{-2,2\}.
$$
Every positive mixture therefore satisfies $|S(p)|\le2$. This is the CHSH inequality [2]. Lean proves the deterministic values, the marginal-score identity, and the resulting stochastic-local bound in `Bell.CHSH`; positivity and normalization are explicit premises. Other output and setting relabelings give the remaining CHSH inequalities. Fine's theorem connects the complete family, under the requisite consistency of the specified marginals, to a joint distribution in this scenario [3]. Our general arguments below use the full polytope (2), not just one inequality.

For an explicit quantum violation, use $|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2$ and
$$
A_0=Z,\quad A_1=X,\quad
B_0=(Z+X)/\sqrt2,\quad B_1=(Z-X)/\sqrt2.
$$
The four correlators are $(1,1,1,-1)/\sqrt2$, so $S=2\sqrt2>2$. The associated outcome distributions are positive and no-signalling but have no positive extension over $\Omega$. `Bell.QuantumExample` constructs these complex matrices and the Bell state, checks Hermiticity, squared-observable identities and commutation between Alice and Bob, and computes the Born table exactly as $p_{1/\sqrt2}$. Its CHSH score is exactly $2\sqrt2$, and the local-bound theorem excludes a positive extension.

# 4 Projection residuals and their dual witnesses

## 4.1 Total-variation repair cost

Fix a setting distribution $\pi_{xy}>0$ with $\sum_{xy}\pi_{xy}=1$. For a table difference $z$, define
$$
\|z\|_\pi=\frac12\sum_{xy}\pi_{xy}\sum_{ab}|z(a,b|x,y)|.
$$
This equals total variation between the joint distributions $\pi_{xy}p(a,b|x,y)$ and $\pi_{xy}\ell(a,b|x,y)$ when $z=p-\ell$. Define
$$
R_\pi(p)=\min_{\ell\in\mathcal L}\|p-\ell\|_\pi
=\min_{q\in\Delta(\Omega)}\|p-Tq\|_\pi.
\tag{3}
$$
For uniform settings this is the trace-distance nonlocality measure studied in [5]. The weights are declared experimental or analytical choices, not a consequence of retraction geometry.

**Theorem 2 (Vanishing and stability).** The minimum in (3) exists. Moreover,
$$
R_\pi(p)=0\iff p\in\mathcal L,
\qquad
|R_\pi(p)-R_\pi(p')|\le\|p-p'\|_\pi.
\tag{4}
$$

**Proof.** The simplex is compact and its linear image $\mathcal L$ is compact. Continuity gives an attained minimum; strict positivity of all weights makes $\|\cdot\|_\pi$ a norm. The zero criterion follows. The triangle inequality applied to any $\ell\in\mathcal L$, followed by minimization and exchange of $p,p'$, proves stability. $\square$

If $\ell_*$ minimizes (3), the table $e_\pi=p-\ell_*$ is a projection residual. Different minimizers can produce different residual vectors with the same norm. There is no preferred linear complementary projector $I-P$ here.

## 4.2 Bell functionals as dual residual measurements

For coefficients $c$, put
$$
B_c(p)=\langle c,p\rangle,\qquad
\beta_c=\max_{\ell\in\mathcal L}\langle c,\ell\rangle,
\qquad
L_\pi(c)=2\max_{a,b,x,y}\frac{|c_{abxy}|}{\pi_{xy}}.
$$
Then $|\langle c,z\rangle|\le L_\pi(c)\|z\|_\pi$.

**Theorem 3 (Dual bounds and completeness).** If $L_\pi(c)>0$, then
$$
R_\pi(p)\ge
\frac{[B_c(p)-\beta_c]_+}{L_\pi(c)},
\qquad [u]_+=\max\{u,0\}.
\tag{5}
$$
In fact,
$$
R_\pi(p)=\max_{L_\pi(c)\le1}
\left(\langle c,p\rangle-\max_{\ell\in\mathcal L}\langle c,\ell\rangle\right).
\tag{6}
$$

**Proof.** For every local $\ell$, $B_c(p)-\beta_c\le\langle c,p-\ell\rangle\le L_\pi(c)\|p-\ell\|_\pi$, proving (5). For (6), choose a nearest local behavior. If its distance is zero, the zero witness attains the dual value. Otherwise separate the open ball of that radius centered at $p$ from the compact convex local polytope. Continuity extends the separation to the closed ball; normalization of the separating functional gives a dual-unit-ball witness attaining the distance. Its maximum over the polytope equals its maximum over the deterministic vertices. $\square$

Equation (6) identifies the optimized residual with a normalized separating witness. Coefficients constant within a context pair to zero with normalized behavior differences, so shifting such constants can improve the bound (5). The displayed $L_\pi$ is the full-space dual norm and is always valid.

For uniform settings in CHSH, $\pi_{xy}=1/4$ and $c_{abxy}=ab(-1)^{xy}$, giving $L_\pi(c)=8$. Applying both signs yields
$$
R_\pi(p)\ge\frac{[|S(p)|-2]_+}{8}.
\tag{7}
$$

The Lean result `Bell.Repair.bell_strong_duality` constructs both optima. Its support-function form `bell_support_duality` uses the coordinate form of the dual unit ball, $|c_{abxy}|\le\pi_{xy}/2$. The declarations `bell_witness_bound` and `bell_slack_primal` prove (5) from a positive coordinate norm bound and the explicit slack-variable formulation (29). These results use the actual marginal map and the weighted-TV infimum, without a supplied optimality certificate.

## 4.3 A literal Euclidean projection

Let $\Pi_{\mathcal L}^{(2)}p=\ell_2$ minimize $\|p-\ell\|_2$ over $\mathcal L$ and put $r_2=p-\ell_2$. Strict convexity gives a unique minimizer. For any $\ell\in\mathcal L$, differentiation along the feasible segment from $\ell_2$ to $\ell$ gives
$$
\langle r_2,\ell-\ell_2\rangle\le0.
$$
Thus, when $r_2\ne0$, the residual itself supplies a separating functional:
$$
\max_{\ell\in\mathcal L}\langle r_2,\ell\rangle
=\langle r_2,\ell_2\rangle,
\qquad
\langle r_2,p\rangle-\langle r_2,\ell_2\rangle=\|r_2\|_2^2.
\tag{8}
$$
This is an exact projection-and-witness identity. The metric is additional structure, and (8) is not a trace-norm identity for quantum density matrices.

## 4.4 Onset is governed by a feasible tangent cone

Let $p_0\in\mathcal L$, and let $\mathcal T_{\mathcal L}(p_0)$ be the polyhedral tangent cone, including the affine-hull constraints of $\mathcal L$.

**Proposition 4 (First-order Bell residual).** If
$$
p(t)=p_0+t v+O(t^2),\qquad t\downarrow0,
$$
in the norm $\|\cdot\|_\pi$, then
$$
R_\pi(p(t))=
t\,\operatorname{dist}_\pi\bigl(v,\mathcal T_{\mathcal L}(p_0)\bigr)+O(t^2).
\tag{9}
$$

**Proof.** Every feasible displacement $\ell-p_0$ lies in the tangent cone. Hence the distance of $p_0+tv$ from $\mathcal L$ is at least $t\operatorname{dist}_\pi(v,\mathcal T_{\mathcal L}(p_0))$. Choose a nearest cone vector $u$. Active inequalities hold along $p_0+tu$ by the definition of the cone. Each inactive inequality has strictly positive slack at $p_0$, and there are finitely many; consequently $p_0+tu\in\mathcal L$ for all sufficiently small $t\ge0$. This gives the reverse inequality on the ray. Apply (4) to the $O(t^2)$ remainder. $\square$

`Bell.Polyhedral` proves finite one-variable elimination, and `Bell.PolyhedralProjection` iterates it to prove that finite linear images of polyhedra remain polyhedral. Applied to the probability simplex and Bell marginal map, this constructs the required finite inequality presentation. Paired inequalities retain affine-hull equalities. `Bell.RepairGeometry.localTangent_intrinsic` identifies its active-constraint cone with the closed radial feasible cone, so the result does not depend on a chosen facet list. `bell_explicit_ray_window` proves existence of a positive interval of exact ray scaling. `bell_quadratic_remainder` proves (9) in the explicit form $|R_\pi(p(t))-t\operatorname{dist}_\pi(v,\mathcal T_{\mathcal L}(p_0))|\le Ct^2$ whenever the trajectory remainder is at most $Ct^2$, for all sufficiently small nonnegative $t$. The window is an existence theorem, not a computed runtime bound.

The Bell analogue of normal leakage is therefore distance of a behavior velocity from a feasible cone. A nonzero quantum $Q_m\dot\rho(0)$ need not produce a velocity outside this cone. If $p_0$ is in the relative interior of $\mathcal L$, every sufficiently nearby no-signalling behavior remains local. At a boundary, tangent-cone escape and higher-order curvature must be distinguished.

# 5 An exactly solvable CHSH family

## 5.1 Positive repair and metric projection

For $0\le v\le1$, define
$$
p_v(a,b|x,y)=\frac14\left[1+v\,ab(-1)^{xy}\right].
\tag{10}
$$
Every context distribution is positive, all one-party marginals are uniform, and $S(p_v)=4v$. Let $c_{abxy}=ab(-1)^{xy}$ as above. On the sixteen assignments define
$$
q_v(\lambda)=\frac{1+vK(\lambda)}{16}.
\tag{11}
$$
Summing over the two unobserved assignment coordinates shows $Tq_v=p_v$: all irrelevant sign monomials cancel. Exactly eight assignments have $K=2$ and eight have $K=-2$. Therefore $q_v$ is positive for $v\le1/2$, with total mass one. At $v=1/2$ it places mass $1/8$ on each $K=2$ assignment.

**Theorem 5 (Exact repair costs).** For uniform settings,
$$
R_\pi(p_v)=\frac{[2v-1]_+}{4},\qquad
\operatorname{dist}_2(p_v,\mathcal L)=[v-\tfrac12]_+.
\tag{12}
$$
For $v>1/2$, $p_{1/2}$ is a total-variation minimizer and the unique Euclidean projection.

**Proof.** The case $v\le1/2$ follows from (11). For $v>1/2$, equation (7) gives $(4v-2)/8=(v-1/2)/2$. On the other hand,
$$
p_v-p_{1/2}=\frac{v-1/2}{4}c,
$$
so direct summation gives $\|p_v-p_{1/2}\|_\pi=(v-1/2)/2$. For the Euclidean norm, $\|c\|_2=4$ gives the separating lower bound $(4v-2)/4=v-1/2$, attained by the same difference. Uniqueness follows from strict convexity. $\square$

At $v=1/\sqrt2$, (10) is precisely the quantum example in Section 3.2. For $v>1/\sqrt2$ this family is not quantum in the CHSH scenario. To see the upper bound, for dichotomic projective observables define
$$
\mathcal B=A_0\otimes(B_0+B_1)+A_1\otimes(B_0-B_1).
$$
**Proposition 5a (Quantum CHSH bound).** The following is the Tsirelson ceiling [11], proved here through Hilbert-space geometry. More generally, let $A_0,A_1,B_0,B_1$ be bounded complex-linear contractions on one Hilbert space, with the local tensor factors already included. Then
$$
\|A_0(B_0+B_1)+A_1(B_0-B_1)\|\le2\sqrt2.
$$
Every unit-vector expectation and every finite positive normalized mixture of such expectations has absolute value at most $2\sqrt2$.

**Proof.** For a vector $\psi$, put $u=B_0\psi$ and $v=B_1\psi$. Contractivity and the triangle inequality give
$$
\|\mathcal B\psi\|\le\|u+v\|+\|u-v\|.
$$
The parallelogram identity and $(a+b)^2\le2(a^2+b^2)$ imply
$$
(\|u+v\|+\|u-v\|)^2
\le4(\|u\|^2+\|v\|^2)\le8\|\psi\|^2.
$$
Taking square roots proves the operator bound. Cauchy--Schwarz bounds a unit-vector expectation; positivity and normalization extend it to finite mixtures. Hermitian involutions preserve norms, as follows from $\langle A\psi,A\psi\rangle=\langle\psi,A^2\psi\rangle$, and therefore satisfy the contraction premise. $\square$

`Bell.Quantum` proves these steps, including the implication from Hermitian dichotomic observables to contraction. The norm inequality itself needs no commutation assumption. The following finite-dimensional conversion supplies the measurement and state hypotheses directly.

**Proposition 5b (Density matrices and binary POVMs).** Let $\rho$ be any positive semidefinite complex matrix with $\operatorname{Tr}\rho=1$. For each setting, let $M_{-|x},M_{+|x}$ and $N_{-|y},N_{+|y}$ be positive semidefinite effects summing to the identity on their respective finite-dimensional spaces. Put
$$
A_x=M_{+|x}-M_{-|x},\qquad B_y=N_{+|y}-N_{-|y}.
$$
These are Hermitian contractions. For a density matrix on the tensor-product space, the actual Born probabilities
$$
p(a,b|x,y)=\operatorname{Tr}\!\left[\rho(M_{a|x}\otimes N_{b|y})\right]
$$
are real, nonnegative, normalized and no-signalling, and their CHSH score obeys $|S(p)|\le2\sqrt2$. The same statement holds for effects on one finite-dimensional space when all effects from opposite parties commute.

**Proof.** For a unit eigenvector $v$ of $A_x$, positivity gives $\langle v,M_{\pm|x}v\rangle\ge0$, while normalization makes these two numbers sum to one. Their difference is the eigenvalue of $A_x$, which therefore lies in $[-1,1]$. Unitary diagonalization gives $\|A_x\|\le1$ in the Hilbert operator norm; likewise for $B_y$.

The spectral theorem gives the explicit decomposition
$$
\rho=\sum_i\lambda_i|v_i\rangle\langle v_i|,
\qquad \lambda_i\ge0,\quad \sum_i\lambda_i=1,\quad \|v_i\|=1.
$$
For every matrix $T$, including non-Hermitian $T$, trace cyclicity yields
$$
\operatorname{Re}\operatorname{Tr}(\rho T)
=\sum_i\lambda_i\operatorname{Re}\langle v_i,Tv_i\rangle.
$$
For Hermitian $T$ the trace is real. Thus Proposition 5a applies to the density expectation without an assumed ensemble decomposition. Singular density matrices and zero eigenvalues are included.

Commuting positive effects have a positive product. Its density expectation is nonnegative; summing either party's effects produces the identity, proving normalization and marginals independent of the opposite setting. Expanding the four binary correlators proves the exact identity $S(p)=\operatorname{Tr}(\rho\mathcal B)$. Tensor lifting preserves positivity and normalization and proves cross-party commutation, so it discharges that premise for local tensor-product POVMs. $\square$

`Bell.QuantumState` proves the effect-to-contraction conversion, normalized spectral weights, explicit rank-one decomposition and trace-to-mixture identity. `Bell.QuantumMeasurement` proves reality, positivity, normalization, both marginal identities, the exact score identity and the tensor-product specialization. None of these conversions assumes contractivity or a supplied mixture. The generic score bound does not use commutation; the probability interpretation does. These conversions cover arbitrary finite matrix dimensions. Infinite-dimensional trace-class density operators are outside this formalization.

 Mixing the displayed maximally entangled state with white noise realizes every $0\le v\le1/\sqrt2$. The endpoint $v=1$ is a PR behavior, useful here as a no-signalling comparison, not a quantum state.

## 5.2 Signed extension and its negative mass

For any normalized signed extension define
$$
N(q)=\sum_\lambda[-q_\lambda]_+
=\frac{\|q\|_1-1}{2},\qquad
N_{\min}(p)=\min_{Tq=p,\ \sum q=1}N(q).
$$
This optimization is considered when signed extensions exist. In CHSH every no-signalling behavior has one: if its one-party means are $\alpha_x,\beta_y$ and correlators are $E_{xy}$, then
$$
q(a_0,a_1,b_0,b_1)=\frac1{16}
\left(1+\sum_x\alpha_x a_x+\sum_y\beta_y b_y
                  +\sum_{xy}E_{xy}a_xb_y\right)
\tag{13}
$$
has the required marginals. This is an explicit instance of the signed-extension/no-signalling connection in [4]. Negative-probability representations and the isotropic family are also studied in [12]. Higher unobserved moments may be added; the displayed extension is not generally the one of least negative mass.

**Proposition 6 (Negativity bound and isotropic optimum).** Every normalized signed CHSH extension satisfies
$$
N(q)\ge\frac{[|S(p)|-2]_+}{4}.
$$
For (10),
$$
N_{\min}(p_v)=\frac{[2v-1]_+}{2}=2R_\pi(p_v).
\tag{14}
$$

**Proof.** Since $|K(\lambda)|=2$,
$$
|S(p)|=\left|\sum_\lambda q_\lambda K(\lambda)\right|
\le2\|q\|_1=2+4N(q).
$$
For $v>1/2$, the eight negative entries of (11) each equal $(1-2v)/16$, giving $N(q_v)=(2v-1)/2$ and attaining the bound. For $v\le1/2$, (11) is positive. $\square$

| Behavior | $S$ | $R_\pi$ | $N_{\min}$ |
|:--|--:|--:|--:|
| White noise, $v=0$ | $0$ | $0$ | $0$ |
| Local boundary, $v=1/2$ | $2$ | $0$ | $0$ |
| Quantum endpoint, $v=1/\sqrt2$ | $2\sqrt2$ | $(\sqrt2-1)/4$ | $(\sqrt2-1)/2$ |
| PR endpoint, $v=1$ | $4$ | $1/4$ | $1/2$ |

At the quantum endpoint, the repair cost is approximately $0.104063$, and the minimum negative mass is approximately $0.207107$. Equation (14) is a family-specific identity; it is not asserted for general scenarios. Contextual fraction is a separate convex-decomposition measure [7]; Section 8 gives exact comparisons, including a counterexample to a universal identification.

# 6 Connecting state residuals to Bell residuals

## 6.1 Measurement contraction and convexification

Let $\mathrm{Sep}$ be the convex set of separable density matrices on the declared finite-dimensional bipartite Hilbert space. For fixed local POVMs, $\mathcal M(\mathrm{Sep})\subseteq\mathcal L$: apply the local response construction of Section 2 to each product term of a separable mixture. Equality need not hold for fixed observables and dimensions.

Related comparisons between state distance and behavior distance appear in [13]. Here the measurement map, the weighted-TV normalization, and the separable comparison class are explicit.

**Theorem 7 (State-to-behavior bound).** For every state $\rho$,
$$
R_\pi(\mathcal M(\rho))
\le\frac12\inf_{\sigma\in\mathrm{Sep}}\|\rho-\sigma\|_1
\le\frac12D_{\rm prod}(\rho).
\tag{15}
$$

**Proof.** For any fixed setting pair, a POVM maps states to probability distributions with total-variation distance at most half their trace-norm distance. Explicitly, for Hermitian $Z$, write $Z=Z_+-Z_-$. Positivity of the POVM effects bounds the sum of absolute outcome traces by $\operatorname{Tr}(Z_++Z_-)=\|Z\|_1$. Averaging over $\pi$ preserves this bound. For each separable $\sigma$, $\mathcal M(\sigma)$ is an admissible local comparison behavior. Minimize over $\sigma$, then choose $\sigma=\rho_A\otimes\rho_B$. $\square$

**Formal instance.** `Bell.QuantumTrace` defines the finite Hermitian trace norm by $\|Z\|_1=\sum_i|\lambda_i(Z)|$. The signed spectral trace expansion proves
$$
\sum_a|\operatorname{Re}\operatorname{Tr}(ZE_a)|\le\|Z\|_1,
\qquad E_a\succeq0,\quad\sum_aE_a=I.
$$
The finite-dimensional construction of $\mathrm{Sep}$ and both inequalities in (15) are now proved in Lean. A separable state is represented by an actual finite ensemble
$$
\sigma=\sum_{i=1}^{k} w_i\,\alpha_i\otimes\beta_i,
\qquad w_i\ge0,\quad\sum_iw_i=1,
$$
where each local matrix is positive semidefinite with trace one. Lean derives positivity and trace one of the mixture. It proves product Born factorization and constructs normalized local responses $\operatorname{Tr}(\alpha_iM_{a|x})$ and $\operatorname{Tr}(\beta_iN_{b|y})$, then constructs a positive global extension through Theorem 1. Locality of the comparison behavior is therefore a conclusion of the construction.

The reduced states are the actual partial traces,
$$
(\rho_A)_{ij}=\sum_b\rho_{(i,b),(j,b)},
\qquad (\rho_B)_{bc}=\sum_i\rho_{(i,b),(i,c)}.
$$
Their positivity and unit trace are proved, as are separability of $\rho_A\otimes\rho_B$ and idempotence of the product-marginal map. Both infima in (15) range over explicitly defined sets. The product of the marginals supplies a separable comparison, so the state-distance set is nonempty; nonnegativity supplies its lower bound. No closest separable state or optimizer is assumed.

The result permits arbitrary finite local dimensions, setting and outcome types, and nonnegative normalized context weights, including zero weights. The general tensor Born table is proved real, nonnegative and normalized. A separate specialization uses the manuscript's existing uniform CHSH repair definition and derives the classical CHSH bound for every separable state. No contraction premise is hidden in the definition of a POVM.

Thus a nonzero Bell residual requires a nonzero state product residual, while the converse fails. The inequalities are upper bounds on Bell residual, not lower bounds. A lower bound on $D_{\rm prod}$ from [P1] or [P2] cannot be substituted into (15) to conclude a Bell violation.

For a fixed CHSH Bell operator $\mathcal B$, there is also the exact observation identity
$$
S(\mathcal M(\rho))
=\operatorname{Tr}(\mathcal B\Pi_{\rm prod}\rho)
 +\operatorname{Tr}(\mathcal B F_\rho).
\tag{16}
$$
The first term is a local baseline. The second is a declared linear observation of the product residual. It must exceed the baseline's remaining slack to cross the Bell bound. Norm magnitude alone does not determine its sign or its alignment with $\mathcal B$.

## 6.2 A conditional dynamical witness

Suppose a trajectory starts at a product state and obeys
$$
F(t)=t n+E(t),\qquad \|E(t)\|_1\le\kappa t^2,
\qquad n=Q_m\dot\rho(0).
\tag{17}
$$
The finite closed-system proof in [P2, Theorem 4.3] supplies $\kappa=2(1+k^2)g^2$ for a $k$-factor system with $g\ge\|H\|_\infty$. For a two-site reduced state in the one- and two-local lattice setting of [P1], its local Taylor estimate supplies $\kappa=24g_{\rm inc}^2$, where $g_{\rm inc}$ is the full incident interaction norm. These constants have different hypotheses and are not interchangeable.

For a fixed CHSH operator put
$$
b=\operatorname{Tr}(\mathcal B n),\qquad
\delta(t)=2-\operatorname{Tr}(\mathcal B\Pi_{\rm prod}\rho(t))\ge0.
$$
Equations (16), (17), and trace/operator norm duality give
$$
S(t)-2\ge t b-\|\mathcal B\|_\infty\kappa t^2-\delta(t).
\tag{18}
$$
Whenever the right side is positive, (7) converts it into a lower bound on the behavior residual. Equation (18) requires the oriented observation $b$ and the product-baseline slack, not merely $\|n\|_1$. An experimental certificate additionally requires certified bounds for every quantity used.

**Finite-time consequence.** The same proof applies to any declared decomposition $\rho(t)=\sigma(t)+t n+E(t)$, with baseline slack $\delta(t)=2-\operatorname{Re}\operatorname{Tr}(\sigma(t)\mathcal B)$. Write $c=\|\mathcal B\|_\infty\kappa$. On a baseline face with $\delta(t)=0$, $b>0$ and $c\ge0$, the conditions $t>0$ and $ct<b$ certify a crossing. If $ct\le b/2$, every local approximation is at distance at least $tb/16$. For $c=0$ the positive-time witness remains positive without division by $c$. Away from the face, the baseline slack must still be subtracted. An additional behavior uncertainty enclosure of radius $\varepsilon$ subtracts $8\varepsilon$ from a certified score excess before taking its positive part and dividing by eight.

`Bell.Dynamics` proves these implications from the actual matrix identity and the spectral trace/operator inequality. The Taylor enclosure (17), the product-reference identification, and the constants imported from [P1, P2] remain explicit premises. For a supporting functional on the local tangent cone the cone support is zero, not the value of the functional at the base behavior. The finite-time estimates require no general tangent-cone theorem.

**Fixed witnesses at a saturating product start.** If Hermitian contractions define a fixed CHSH operator $\mathcal B$ and a product density $\sigma=\alpha\otimes\beta$ satisfies $\operatorname{Tr}(\mathcal B\sigma)=2$, saturation of the scalar CHSH bound forces the relevant local expectations to be extremal. Each corresponding contraction acts as $+1$ or $-1$ on the local state's support, giving $\mathcal B\sigma=\sigma\mathcal B=2\sigma$. Thus a differentiable closed unitary trajectory from $\sigma$ has $\frac{d}{dt}\operatorname{Tr}(\mathcal B\rho(t))|_{t=0}=-i\operatorname{Tr}(\mathcal B[H,\sigma])=0$. A smooth product-marginal baseline also has zero derivative there, since its CHSH value has a two-sided local maximum. Consequently the first-order coefficient in (18) cannot certify quadratic onset from such a start. This written support argument is separate from the Lean trajectory-enclosure implications; a second-order witness construction remains a research target.

## 6.3 Linear correlation growth and quadratic Bell growth

Take $H=gX\otimes X$, $g>0$, and $|\psi(0)\rangle=|00\rangle$. Then
$$
|\psi(t)\rangle=\cos(gt)|00\rangle-i\sin(gt)|11\rangle.
$$
Write $c=|\sin(2gt)|$. Direct diagonalization of $F(t)$ gives
$$
D_{\rm prod}(t)=c+\frac{c^2}{2}.
\tag{19}
$$
Indeed, with $u=\cos(gt)$ and $w=\sin(gt)$, the $00,11$ block of $F$ has diagonal entries $u^2w^2$ and off-diagonal magnitude $|uw|$, while the $01,10$ entries are $-u^2w^2$. Its eigenvalues yield (19).

A fixed local phase change puts the state in Schmidt form. Its $3\times3$ Pauli correlation matrix then has singular values $1,c,c$. The maximum projective CHSH expectation is
$$
S_{\max}(t)=2\sqrt{1+c^2}.
\tag{20}
$$
For completeness, write Bob's two unit Bloch vectors as $b_0+b_1=2\cos\theta\,u$ and $b_0-b_1=2\sin\theta\,v$, where $u\perp v$. Maximizing Alice's directions gives $2(\cos\theta\|Tu\|+\sin\theta\|Tv\|)$; maximizing $\theta$ and the orthonormal pair selects the two largest squared singular values. This proves (20).

As $t\downarrow0$,
$$
D_{\rm prod}(t)=2gt+2g^2t^2+O(t^3),\qquad
S_{\max}(t)-2=4g^2t^2+O(t^4).
\tag{21}
$$
Thus the initial product normal rate is $2g$, but the optimized Bell excess has zero first derivative. The optimal measurement directions in (20) are chosen separately for each $t$; this is not a claim about one fixed experimental setting table. It demonstrates directly why a product-residual onset theorem is not itself a Bell-onset theorem.

# 7 Cochains and the positivity obstruction

## 7.1 Overlap consistency survives Bell violation

The CHSH measurement labels are $\{A_0,A_1,B_0,B_1\}$, with jointly accessible contexts $C_{xy}=\{A_x,B_y\}$. A section on a context is its outcome distribution; restrictions to overlaps are ordinary marginalizations. The overlap defect compares two context distributions after restriction to their common measurement labels.

For every $p_v$ in (10), all these overlap defects vanish because all singleton marginals are uniform. Yet for $v>1/2$, Theorem 5 gives $R_\pi(p_v)>0$. Consequently, the Bell obstruction cannot be identified with the norm of that ordinary linear overlap defect.

The underlying reason is visible in (13). In the CHSH no-signalling affine space, real signed gluing succeeds. Positive gluing can fail:
$$
\{q:Tq=p,\ \textstyle\sum q=1\}\ne\varnothing,
\qquad
\{q:Tq=p,\ q\ge0,\ \textstyle\sum q=1\}=\varnothing.
\tag{22}
$$
This is a convex feasibility obstruction. Its exact witnesses are separating Bell functionals. Merely adjoining a putative global context to a diagram does not create a positive distribution on it.

## 7.2 A genuine parity class at the PR endpoint

At $v=1$, the support constraints are $ab=(-1)^{xy}$. Write $a_x=(-1)^{u_x}$ and $b_y=(-1)^{v_y}$ with values in $\mathbb F_2$. They become
$$
u_x+v_y=xy\pmod2.
\tag{23}
$$
Use the graph with vertices $A_0,A_1,B_0,B_1$ and all four context edges, namely $K_{2,2}$. Define the edge cochain $h(C_{xy})=xy$. If a global assignment existed, then $h=d_0 f$ for the vertex cochain $f=(u_0,u_1,v_0,v_1)$. But the sum of a coboundary around the four-cycle is zero, whereas $\sum_{xy}h(C_{xy})=1$. Since the graph has no 2-cells, $h$ is a cocycle and represents the nonzero class in $H^1(K_{2,2};\mathbb F_2)$.

This is an explicit cohomological obstruction with declared carrier, coefficients, and observation rule. Its mathematical content is the inconsistent parity equations, not the use of the word cohomology. It is a support-level example of the broader programme in [6].

## 7.3 Why this class does not cover the quantum family

For $1/2<v<1$, every outcome pair in every context of (10) has strictly positive probability. Every deterministic assignment is therefore compatible with the support. No support-only invariant can distinguish this family from full-support local white noise. In particular, at $v=1/\sqrt2$ the Bell residual is positive although the support admits every global assignment.

This establishes the limit of the parity construction without diminishing its endpoint result. Probability weights, not forbidden events, obstruct positive gluing in this full-support quantum example. The support-derived cohomological obstruction of [6] is not a complete detector of probabilistic Bell nonlocality.

The scalar Hodge decomposition in [P2, Section 5] concerns a declared linear cochain complex. Its harmonic component depends on that complex and the chosen inner product. Equating its norm with (3) would require an additional theorem incorporating positivity. No such equivalence is assumed here. Similarly, the temporal semigroup defect of [P2, Section 6.2] concerns repeated retraction of dynamics, not the existence of a setting-independent positive extension.

# 8 A higher-order Bell observation

The distinction between the fully factorized residual projector $Q$ and the highest-order projector $R_k$ in [P2] matters for multipartite Bell tests. For $k$ factors, $Q$ retains intermediate-order correlations. A two-site interaction inside a three-site cell can produce $Q\dot\rho\ne0$ without any genuine three-party correlation. Neither the size of the cell nor a nonzero $Q$ supplies a multipartite Bell witness.

An explicit three-party observation is available. Let
$$
|\mathrm{GHZ}_+\rangle=(|000\rangle+|111\rangle)/\sqrt2,
\qquad
\mathcal B_3=XXX-XYY-YXY-YYX,
$$
where juxtaposition denotes tensor product. For deterministic local $X,Y$ outcomes, put $r_A=y_A/x_A$ and likewise for $B,C$. The Bell polynomial becomes
$$
x_Ax_Bx_C\,[1-r_Br_C-r_Ar_C-r_Ar_B].
$$
The three pair products in brackets multiply to one, so their sum is either $3$ or $-1$. Hence the polynomial is always $\pm2$. Every local mixture has $|\langle\mathcal B_3\rangle|\le2$, the three-party Mermin bound [8]. Direct Pauli action gives $\langle\mathrm{GHZ}_+|\mathcal B_3|\mathrm{GHZ}_+\rangle=4$.

Each one-party density matrix is $I_2/2$, so the product baseline is $I_8/8$ and
$$
\operatorname{Tr}\!\left[\mathcal B_3
\left(|\mathrm{GHZ}_+\rangle\langle\mathrm{GHZ}_+|-I_8/8\right)\right]=4.
\tag{24}
$$
Thus $Z\mapsto\operatorname{Tr}(\mathcal B_3Z)$ is the declared linear observation of the state residual. With reference factors $I_2/2$, each term of $\mathcal B_3$ is traceless at every site, so it pairs only with the highest-order component $R_3Z$. This supplies a concrete observation bridge of the kind required by [P2], without identifying $R_3$ with a universal entanglement test.

By contrast, the dephased state
$$
\rho_{\rm GHZ,cl}=\tfrac12|000\rangle\langle000|
                         +\tfrac12|111\rangle\langle111|
$$
has $D_{\rm prod}=3/2$ but $\operatorname{Tr}(\mathcal B_3\rho_{\rm GHZ,cl})=0$. The pure GHZ state has $D_{\rm prod}=7/4$. Their different Bell observations cannot be inferred merely from the fact that both product residuals are nonzero.

For the four displayed $X/Y$ contexts of the GHZ state, all proper-party outcome marginals are uniform while the triple parities produce the violation. This statement concerns those measurement outcomes: the full two-qubit reduced density matrices are classically correlated, not maximally mixed. With uniform weight on these four contexts, the same dual-norm calculation as (7) gives a behavior repair cost of at least $1/4$.

## 8.1 Contextual fraction and signed mass

Contextual fraction [7] uses the largest nonnegative local subdistribution dominated by the observed table. For the incidence matrix $T$ of a finite scenario, define
$$
CF(p)=1-\max\{\mathbf1^\top\gamma:\gamma\ge0,\ T\gamma\le p\}.
\tag{31}
$$
Each deterministic column has one unit in each context. For a normalized nonnegative table the feasible masses lie in $[0,1]$, and the maximum exists. On no-signalling tables this is the usual decomposition into a local behavior and a no-signalling remainder. Its dual minimizes $p^\top y$ subject to $y\ge0$ and $T^\top y\ge\mathbf1$. A feasible primal/dual pair with equal objectives proves the optimum. This is different from the signed-extension dual, whose vertex scores lie in an interval of width one.

**Theorem 11 (Real-parameter CHSH and Mermin families).** For the CHSH family (10) and the eight-context three-party family
$$
Q_v(a,b,c|x,y,z)=\frac{1+v\,\chi(x,y,z)abc}{8},
\quad
\chi(000)=-1,\quad
\chi(011)=\chi(101)=\chi(110)=1,
$$
with $\chi=0$ on the other settings and outcomes $a,b,c\in\{-1,1\}$, every real $0\le v\le1$ satisfies
$$
N_{\min}=\max(0,v-\tfrac12),\qquad
CF=\max(0,2v-1)=2N_{\min}.
\tag{32}
$$

**Proof.** In CHSH put $K=K_{\rm CHSH}$, $D=16$, $d=4$; in the Mermin scenario put
$$
K=-a_0b_0c_0+a_0b_1c_1+a_1b_0c_1+a_1b_1c_0,
\qquad D=64,\quad d=8.
$$
In both cases $K$ takes only the values $\pm2$, equally often. The normalized real weights $q_v(g)=(1+vK(g))/D$ project to the stated behavior. Their negative mass is $\max(0,v-\tfrac12)$. The witness with coefficients $c_i/4$ and normalization offset $-1/2$, where $p_v(i)=(1+vc_i)/d$, has vertex scores in $[-1,0]$ and objective $v-1/2$. Weak duality therefore excludes every smaller negative mass, including among arbitrary real signed extensions.

For $v\le1/2$, $q_v$ is positive and proves $CF=0$. For $v\ge1/2$, the local subdistribution $(2-2v)q_{1/2}$ is dominated by $p_v$, giving $CF\le2v-1$. The nonnegative dual vector $y_i=(|c_i|-c_i)/2$ has every vertex score at least one and objective $2-2v$, proving the reverse inequality. $\square$

The module Bell.BinaryScenarios instantiates these identities with the actual deterministic incidence matrices; Bell.NegativeMassFamilies proves the formulas for real parameters and all real competitors. This extends the supplied integer-scaled rational-grid Lean fragment; it does not merely repackage its finite evaluations.

The Mermin endpoint $Q_1$ is the Pauli $X/Y$ behavior of $(|000\rangle-|111\rangle)/\sqrt2$. White-noise mixing realizes every $Q_v$ in the displayed interval. Thus its quantum endpoint is $v=1$, unlike the CHSH isotropic endpoint $1/\sqrt2$. Section 8.3 now constructs an alternative pure-state realization of every such visibility and formalizes its Born table in Lean. There are eight settings here; a uniform average over only the four nonzero Mermin contexts has a different repair normalization.

With uniform weight on all eight contexts, the exact repair is $R_\pi(Q_v)=\max(0,2v-1)/8$. For $v\ge1/2$, the Mermin witness gives this lower bound and comparison with the local table $Q_{1/2}$ attains it: only four contexts change, each by L1 distance $v-1/2$. For $v\le1/2$, $Q_v$ is already local. Thus $CF=2N_{\min}=8R_\pi$ on this line, compared with $4R_\pi$ on the CHSH line. This repair sharpness argument remains written and numerically checked; it is not included in the new Lean family theorem.

## 8.2 Comparison beyond the symmetric families

**Theorem 12 (Separation and reversed ordering).** There is a normalized, nonnegative, no-signalling behavior $p_*$ in the three-party, two-setting, two-outcome scenario with
$$
CF(p_*)=\frac{19}{64},\qquad
N_{\min}(p_*)=\frac{25}{256},\qquad
CF(p_*)-2N_{\min}(p_*)=\frac{13}{128}>0.
\tag{33}
$$
Moreover $CF(Q_{5/8})=1/4<CF(p_*)$, whereas $N_{\min}(Q_{5/8})=1/8>N_{\min}(p_*)$.

**Proof.** The full rational table and four primal/dual certificate vectors are supplied in the data file contextual_fraction_certificates.json, case GHZ rnd2 (k=4, den=12). Equivalently,
$$
p_*=\tfrac16W+\tfrac13\ell_{63}+\tfrac5{12}G+\tfrac1{12}Q_{5/8},
$$
where $W$ is uniform on the four even-parity output triples in every context, $\ell_{63}$ always outputs the bit triple $(1,1,1)$, and $G$ is uniform on the four odd-parity triples at setting $(0,0,0)$ and on the four even-parity triples at every other setting. These four tables are normalized and no-signalling, so their convex mixture is too.

With the scale used in Bell.ComparisonData, the integer local weights sum to $540$, the integer signed weights sum to $768$ and have negative mass $75$, and the table entries have denominator $768$. The CF dual objective is $540/768$; the signed-mass dual objective is $150/1536$. Kernel-checked integer incidence identities establish all domination, projection and dual-feasibility constraints. The real certificate theorems then give (33) and exclude every better real competitor. Equation (32) at $v=5/8$ gives the reversed ordering. $\square$

This disproves the universal inequality $CF\le2N_{\min}$ and a universal equality of the two measures. It does not show that no scenario-dependent comparison constant exists. Quantum realizability of $p_*$ is not established here. In particular, the full-parity box $G$ is distinct from the quantum Mermin endpoint $Q_1$.

**Theorem 13 (Finite-context comparison).** Let $T$ be a finite zero-one incidence matrix with exactly $m>0$ ones in every deterministic column. Suppose $p\ge0$, $\mathbf1^\top p=m$, and $Tq=p$, $\mathbf1^\top q=1$. Then
$$
0\le CF(p)\le1,\qquad CF(p)\le(m-1)N(q).
\tag{34}
$$
Consequently, when the minimum is attained, $CF(p)\le(m-1)N_{\min}(p)$.

**Proof.** Write $u=q^+$, $n=q^-$, $s=Tu$, $r=Tn$, and $N=\mathbf1^\top n$. Then $p=s-r\ge0$, $\mathbf1^\top u=1+N$, and $\mathbf1^\top r=mN$. Set $d_i=r_i/s_i$ when $s_i>0$ and zero otherwise; $0\le d_i\le1$. For each assignment define
$$
L_g=u_g\sum_iT_{ig}d_i,\qquad
\gamma_g=\max(u_g-L_g,0).
$$
For every incident cell $i$, $\gamma_g\le u_g(1-d_i)$, so $(T\gamma)_i\le s_i-r_i=p_i$. Thus $\gamma$ is a feasible local subdistribution. Also $\sum_g L_g=\sum_i r_i=mN$, whence $\sum_g\gamma_g\ge1-(m-1)N$. Substitution into (31) proves the comparison. The zero packing and the common column mass prove the range $[0,1]$. $\square$

The theorem Bell.ContextualFraction.fraction_le_negative_mass proves this construction directly from the stated incidence and normalization hypotheses. It assumes neither the desired inequality nor an optimal CF dual witness. No optimality or sharpness of the constant $m-1$ is claimed. For eight contexts the bound is $CF\le7N_{\min}$, compatible with (33).

The positive and negative parts of a normalized signed extension have the same masses $1+N$ and $N$ in every context. The obstruction to turning this into a contextual-fraction decomposition is the signed affine combination $p=(1+N)\ell_+-N\ell_-$, not a variation of those masses between contexts. Likewise, a separating negative-mass dual functional is a Bell inequality witness; its origin in a different optimization does not remove that status.

## 8.3 Quantum-restricted comparisons and an explicit evolution

The word *quantum* restricts the admissible behaviors, but it does not supply one scenario-independent ceiling for contextual fraction. The two families below provide exact, attained comparisons with different quantum ranges.

**Theorem 14 (Quantum CHSH-line comparison).** On the isotropic CHSH line $p_v$, restrict to $v\ge0$ and a quantum realization by normalized states and local binary observables. Then
$$
\mathrm{CF}(p_v)=2N_{\min}(p_v),\qquad
N_{\min}(p_v)\le\frac{\sqrt2-1}{2},\qquad
\mathrm{CF}(p_v)\le\sqrt2-1.
\tag{35}
$$
Both upper bounds are attained by the two-qubit realization in Section 6.

**Proof.** The quantum CHSH bound gives $4v\le2\sqrt2$. Substitute into Theorem 11. At $v=1/\sqrt2$, the existing complex Born-table construction attains the cap. All smaller nonnegative visibilities can also be obtained by mixing that state with the maximally mixed state while retaining the measurements. The Lean comparison theorem derives the ceiling from Hilbert-space contractions and a matching CHSH expectation; the endpoint's Born realization was already formalized. The mixed-state interpolation argument is written. These are bounds on the declared line, not a classification of arbitrary quantum behaviors. $\square$

**Theorem 15 (Quantum GHZ-line realization and comparison).** Let
$$
|\psi(t)\rangle=\cos t\,|000\rangle-\sin t\,|111\rangle,
\qquad 0\le t\le\pi/4.
$$
Measure $X$ or $Y$ at each of three sites, with bit $a$ denoting eigenvalue $(-1)^a$. The complete eight-context Born behavior is exactly $Q_{\sin(2t)}$ from Theorem 11. Consequently
$$
\begin{aligned}
N_{\min}(Q_{\sin(2t)})&=\max\{0,\sin(2t)-1/2\},\\
\mathrm{CF}(Q_{\sin(2t)})&=2N_{\min}(Q_{\sin(2t)})\le1.
\end{aligned}
\tag{36}
$$
Every $Q_v$ with $0\le v\le1$ is quantum: take $t=\arcsin(v)/2$. At $t=\pi/4$, the two optima are $1/2$ and $1$, respectively. In particular, the CHSH-line ceilings in (35) cannot be imposed on all quantum Bell scenarios.

**Proof.** The two nonzero amplitudes have squared norm one. In the tensor product of local outcome projectors, only four matrix entries contribute to the expectation. Their sum is $(1+2\cos t\sin t\,\chi(x,y,z)(-1)^{a+b+c})/8$. Since $2\cos t\sin t=\sin(2t)$, this is the exact table used in Theorem 11. Lean proves the local Pauli identities, projector identities, all Born entries for arbitrary real amplitudes of norm one, and the real-parameter optimization conclusions. No quantum-realizability assumption is supplied for this family: the state and measurements are constructed. $\square$

This is an actual evolution. In the ordered subspace $|000\rangle,|111\rangle$, set
$$
G=\begin{pmatrix}0&1\\-1&0\end{pmatrix},\quad
H=iG,\quad
U(t)=\begin{pmatrix}\cos t&\sin t\\-\sin t&\cos t\end{pmatrix}.
$$
Extend $H$ by zero and $U$ by the identity on the six remaining basis vectors. Then $H$ is Hermitian, $U(t)=e^{-itH}$, and $U(t)|000\rangle=|\psi(t)\rangle$. Lean checks the active block's Hermiticity, unitarity, identity at zero, and composition law $U(t+u)=U(t)U(u)$, together with the three-qubit state and Born table. The identification with the matrix exponential follows by the elementary two-dimensional calculation and is independently replayed numerically on the full eight-dimensional matrix; no general Lean matrix-exponential or differential-equation theorem is claimed. The interaction is a preparation operation before the separated local measurements, not a locality-preserving resource operation.

**Theorem 16 (Exact and uncertainty-delayed exit windows).** On $0\le t\le\pi/4$, this measured behavior has no positive local extension exactly when $t>\pi/12$. At the boundary $t=\pi/12$, both optima in (36) are zero. For any actual behavior $p$ with Mermin score $M(p)$, suppose
$$
|M(p)-4\sin(2t)|\le\eta,\qquad 0\le\eta<2.
$$
Then the sufficient window certifying that $p$ is nonlocal is
$$
\frac12\arcsin\!\left(\frac{2+\eta}{4}\right)<t\le\frac\pi4.
\tag{37}
$$
If $p$ is nonnegative and normalized in each context, its contextual fraction obeys
$$
\mathrm{CF}(p)\ge 2\sin(2t)-1-\eta/2.
$$
Every normalized signed extension $q$ of $p$ obeys
$$
N(q)\ge \sin(2t)-1/2-\eta/4.
$$
Nonnegativity of these measures allows clipping the lower bounds at zero. Under uniform weighting of eight contexts, an observed-table total-variation error at most $\varepsilon$ supplies $\eta=16\varepsilon$. Thus a nonempty worst-case certification window requires $\varepsilon<1/8$ with this witness. This is a sufficient certificate; failure of its threshold does not prove locality.

**Proof.** The local Mermin bound is $M\le2$, while the constructed table has $M=4\sin(2t)$. Before the threshold, Theorem 11 supplies an actual nonnegative normalized extension. Sine is strictly increasing on the stated interval and $\sin(\pi/6)=1/2$, giving the exact onset. Subtracting the score-error bound gives (37). The CF dual witness $(|c|-c)/2$ has value $2-M(p)/2$, using normalization of the four active contexts. The signed dual witness $c/4$ with offset $-1/2$ gives $N(q)\ge(M(p)-2)/4$. Finally, $|c_i|\le1$ bounds the score error by the cellwise $\ell^1$ error, which equals sixteen times uniform-context TV. All these inequalities and the inverse-sine window are formalized. $\square$

For physical coupling $g>0$, replace $t$ by $g\tau$: the onset time is $\pi/(12g)$ and the noisy sufficient start is $\arcsin((2+\eta)/4)/(2g)$. At $g=0$ the initial behavior never exits. The window refers to the first rising interval; later evolution is periodic and can re-enter the local region. A nonzero interaction, a nonzero state residual, or entanglement alone does not imply a violation at every positive time.

The comparisons proved here are sharp on two explicitly identified quantum families. These family results alone do not settle a universal quantum inequality; Section 8.4 now disproves the proposed factor-two bound with a different quantum experiment. In particular, the earlier no-signalling counterexample remains without an established quantum realization. Neither the elementary trigonometric window nor the family formulas are claimed as discoveries over the contextuality literature; the contribution is their explicit, checked connection to this package's optimization and uncertainty semantics.


## 8.4 A quantum counterexample in the full three-setting Bell scenario

The restriction to quantum behaviors does **not** rescue the universal inequality $CF\le2N_{\min}$. It already fails for one maximally entangled pair of qubits with three binary settings at each site. The experiment below includes **all nine setting pairs**, not only the six appearing in the chained witness. This answers the question across finite quantum Bell scenarios; it does not settle a restriction to the earlier three-party, two-setting scenario.

**Theorem 17 (exact three-setting line).** For outcomes $a,b\in\{-1,1\}$ and settings $x,y\in\{0,1,2\}$, put
$$
C=\begin{pmatrix}1&0&-1\\1&1&0\\0&1&1\end{pmatrix},
\qquad
p_v(a,b\mid x,y)=\frac{1+ab\,v C_{xy}}4.
$$
Let the local model contain all $64$ assignments of the six local response values. For every real $2/3\le v\le1$,
$$
CF(p_v)=3v-2,\qquad N_{\min}(p_v)=\frac{3v-2}{4},
\qquad CF(p_v)=4N_{\min}(p_v).
\tag{38}
$$

**Proof.** For an assignment $\lambda$, write $K_\lambda=\sum_{xy}C_{xy}A_xB_y$. Its possible values are $-4,0,4$, with $12$ assignments at each nonzero extreme and $40$ at zero. Uniform distributions on the positive and negative extremes have correlations $\pm(2/3)C$, including the three zero entries, and unbiased marginals. Consequently
$$
q_v(\lambda)=
\begin{cases}
(2+3v)/48&K_\lambda=4,\\
(2-3v)/48&K_\lambda=-4,\\
0&K_\lambda=0
\end{cases}
$$
is a normalized signed extension of the entire table, with negative mass $(3v-2)/4$. The signed dual has cell coefficients $\alpha_{xyab}=abC_{xy}/8$ and normalization offset $\beta=-1/2$. Each deterministic value lies in $[-1,0]$, while $\langle\alpha,p_v\rangle+\beta=(3v-2)/4$. Weak duality proves minimality against every real signed extension.

For CF, use $\gamma_v(\lambda)=(1-v)/4$ when $K_\lambda=4$, and zero otherwise. This is a nonnegative local subdistribution of mass $3(1-v)$ dominated cellwise by $p_v$. Indeed, its remainder is $(3v-2)p_1$, a nonnegative table. The nonnegative covering dual
$$
y_{xyab}=\frac{|C_{xy}|-abC_{xy}}2
$$
takes value $(6-K_\lambda)/2\ge1$ on each assignment and has expectation $3(1-v)$. Matching packing and covering values give $CF=3v-2$. The Lean proof checks the finite identities in the kernel and transports them to real optimization statements; it does not substitute a finite visibility grid for the real parameter. $\square$

**Theorem 18 (two-qubit quantum separation).** Let $u=\sqrt3/2$ and use the normalized state $|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2$. With Pauli matrices $X,Z$, choose
$$
(A_0,A_1,A_2)=(Z,\tfrac12Z+uX,-\tfrac12Z+uX),
$$
$$
(B_0,B_1,B_2)=(uZ+\tfrac12X,X,-uZ+\tfrac12X).
$$
These are Hermitian involutions. Their local effects $(I+aA_x)/2$ and $(I+bB_y)/2$ are positive complete projective measurements. Their tensor-product Born table is exactly $p_u$, and
$$
CF(p_u)=\frac{3\sqrt3-4}{2}\simeq0.598076,
\qquad
N_{\min}(p_u)=\frac{3\sqrt3-4}{8}\simeq0.149519.
\tag{39}
$$
Thus $CF(p_u)=4N_{\min}(p_u)>2N_{\min}(p_u)$.

**Proof.** The state has zero local $X,Z$ means and correlations $\langle X\otimes X\rangle=\langle Z\otimes Z\rangle=1$, with the cross terms zero. Taking the inner products of the displayed planar axes gives the full correlation matrix $uC$. Since $u^2=3/4$ and $2/3<u<1$, the effects are projectors and Theorem 17 applies. Lean proves the actual complex state normalization, effect positivity/completeness, all Born cells, the strict inequality and the optimality of the signed extension. $\square$

The witness is the three-setting member of the established chained Bell family [20]. Its role here is to close our quantum-realizability gap by an explicit experiment and checked certificates, not to claim discovery of chained nonlocality. An independent Python implementation enumerates the model, verifies the Born matrices and both primal/dual pairs exactly in $\mathbb Q(\sqrt3)$, and checks two floating-point LP answers separately.

Any constant $k$ asserted in $CF\le kN_{\min}$ for **every** finite quantum Bell behavior must therefore satisfy $k\ge4$. We have not proved that $4$ works universally, or that any scenario-independent finite constant works. The established finite-context bound remains $CF\le\min\{1,(m-1)N_{\min}\}$ under Theorem 13's assumptions. The exact factor $4$ here applies to this line; the exact factor $2$ on the CHSH and GHZ lines remains correct. The earlier no-signalling table $p_*$ still has no established quantum realization.

Normalization and model space matter when comparing to contextuality literature. The cyclic-system relation in [18] uses its declared quasi-coupling space and $CNT3$ convention. Our optimization uses one signed weight per global deterministic assignment of the six measurements. We do not identify those optimization variables or transplant a proportionality coefficient without a proof. All values in (38)–(39) are independently derived for the explicitly stated nine-context model.



## 8.5 The factor-four conjecture and the measurement cover

The inequality $CF\le4N_{\min}$ also fails for complete quantum Bell behaviors. The possibility of an unbounded ratio depends on which contexts are retained. Write $N_{\min}$ for the minimum *total negative weight*, not the excess $\ell_1$ norm $2N_{\min}$.

**Theorem 19 (A complete rational quantum counterexample to factor four).** On $|\Phi^+\rangle$, take five binary projective measurements per party. Write a planar observable as $zZ+xX$. The respective pairs $(z,x)$ are

$$
\begin{aligned}
A&=\frac1{185}\big((185,0),(148,111),(57,176),(-57,176),(-148,111)\big),\\
B&=\frac1{185}\big((175,60),(111,148),(0,185),(-111,148),(-175,60)\big).
\end{aligned}
$$

Every pair has squared norm one. Include **all 25** setting pairs and all four outcome cells at each pair. The Born probabilities are $p(a,b\mid x,y)=(1+ab\,A_x\cdot B_y)/4$, with $a,b\in\{-1,1\}$. Then

$$
CF(p)=\frac{698}{925},\qquad N_{\min}(p)=\frac{167}{925},\qquad
CF(p)-4N_{\min}(p)=\frac6{185}>0.\tag{40}
$$

Thus any coefficient valid for every complete quantum Bell behavior must be at least $698/167\simeq4.17964$. These rational directions approximate the usual five-setting chained directions; exact trigonometric values are unnecessary for the counterexample.

*Certificates.* `data/five_setting_certificates.json` lists a signed extension supported on 31 of the 1,024 local response assignments, a local packing supported on 20 assignments, a nonnegative covering witness, and a signed-mass dual witness. Their objectives are respectively $167/925$, $227/925$, $227/925$, and $167/925$. The incidence matrix includes all 100 cells. The only negative signed weights are $-1/20$ and $-483/3700$, whose sum in absolute value is $167/925$. Independent exact arithmetic checks every incidence constraint and both zero duality gaps. The Lean proofs lift integer identities to real optimization over the complete assignment space; the minimum is not restricted to rational weights. The local effects are positive complete projectors, and their tensor Born table is explicitly verified.

**Theorem 20 (Unbounded ratios on the restricted chained cover).** For $n\ge2$, retain the $2n$ edges of the usual chained experiment, with one frustrated sign, and unbiased outcomes. Set $v=\cos(\pi/(2n))$. On this *cycle cover*, rather than the full $n^2$-context cover,

$$
CF_{\mathrm{cycle}}=nv-n+1,\qquad
N_{\mathrm{cycle}}=\frac{nv-n+1}{2n-2},\qquad
\frac{CF_{\mathrm{cycle}}}{N_{\mathrm{cycle}}}=2n-2.\tag{41}
$$

In particular, no finite coefficient works over all quantum empirical models when their allowed context covers vary. Quantum realizability follows from $|\Phi^+\rangle$ and planar angles $\alpha_j=j\pi/n$, $\beta_j=(j+1/2)\pi/n$. Adjacent edges have correlation $v$; the closing edge has correlation $-v$. The coefficient grows because the admissible global class must satisfy the cycle parity constraint even though each observed edge is almost perfectly correlated with its designated sign.

*Proof and normalization.* A deterministic assignment fails an odd number $d\in\{1,3,\ldots,2n-1\}$ of the signed edge constraints. Conversely, every odd failure pattern is realized: choose the first vertex outcome and propagate success or failure around the cycle; odd parity is exactly the closing consistency condition. The two choices of initial outcome differ by a global sign. Averaging them gives unbiased marginals.

Let $L_+$ be the uniform distribution on the $4n$ assignments obtained by choosing one failed edge and the initial sign. Its signed edge correlations are $r=1-1/n$. Flipping every Bob response gives $L_-$, with correlations $-r$. For any $r\le v\le1$,

$$
q_v=\frac{1+v/r}{2}L_++\frac{1-v/r}{2}L_-
$$

is a normalized signed extension with negative mass $(v/r-1)/2$. The affine dual value $(1-d)/(2n-2)\in[-1,0]$ proves optimality. Giving every one-failure assignment weight $(1-v)/4$ supplies a feasible local packing of total mass $n(1-v)$; the witness counting failed edges has the same objective. These matching certificates establish (41) for real weights.

For precision about the quotient: map each deterministic response assignment to its failure pattern, and each observed outcome pair to success or failure. Pushing signed weights forward cannot increase negative mass. Lifting each pattern equally to its two global-sign assignments cannot increase negative mass either, and reproduces the unbiased four-cell table. The same pushforward and lift preserve feasible packing weights. Hence both optima agree with the parity-quotient formulation. The arbitrary-size parity optimization and quantum edge formulas are mechanized. `CycleLifting` now proves path reconstruction and its inverse, odd closing parity, the two-fold assignment equivalence, global-sign propagation, the four-cell outcome recoding, equality of feasible packing weights, and equivalence at every signed-mass budget. Its cycle corollaries instantiate the previous parity incidence matrix; the list and finite-index presentations differ only by their enumeration. Independent finite reconstruction replay remains in `code/chain_comparisons.py`.

For all sufficiently large $n$, the elementary bound $\cos t\ge1-t^2$ at $t=\pi/(2n)$ already proves $v>1-1/n$. Therefore the numerator in (41) is positive, $CF_{\mathrm{cycle}}\to1$, $N_{\mathrm{cycle}}\to0$, and the ratio is unbounded. The Lean theorem quantifies over every proposed finite coefficient; it is not an extrapolation from the finite checks. The cycle-cover qualification is essential.

**Theorem 21 (Complete equally spaced chains have a bounded tail).** Now retain every setting pair of those same equally spaced measurements. For $n\ge4$, every normalized signed extension of the full correlation table satisfies

$$
N\ \ge\ \frac{2\sqrt2-2-6\pi/n}{4}.\tag{42}
$$

For $n\ge64$, this implies $N\ge17/160$ and

$$
CF_{\mathrm{full}}\le\frac{160}{17}N_{\min,\mathrm{full}}.
\tag{43}
$$

More sharply, (42) gives
$\limsup_{n\to\infty}CF_{\mathrm{full}}/N_{\min,\mathrm{full}}\le2(\sqrt2+1)\simeq4.82843$.
This is an asymptotic upper bound, not an asserted exact limit. Consequently increasing the number of settings in this standard **complete-table** family does not make the ratio unbounded. Theorem 22 below proves that no such finite coefficient works across all complete quantum Bell behaviors; it uses a different family.

*Proof.* Choose Alice settings $0$ and $\lfloor n/2\rfloor$ and Bob settings $\lfloor n/4\rfloor$ and $\lfloor3n/4\rfloor$. Their angles approximate $0,\pi/2,\pi/4,3\pi/4$ within $\pi/(2n)$. A local trigonometric estimate bounds the CHSH score below by $2\sqrt2-6\pi/n$. Every signed normalized assignment model has CHSH score at most $2(1+2N)$, giving (42). Combine $CF\le1$ with $\pi\le4$ and $\sqrt2\ge7/5$ to obtain (43). The asymptotic statement follows as $1/n\to0$. Lean additionally proves the equivalent quantified tail estimate: for every $k>2(\sqrt2+1)$ there is a cutoff beyond which $CF\le kN$ for all signed models obeying the indicated CHSH bound. The formal lower bound is stated for all signed models reproducing these four correlations, so it applies in particular to every extension reproducing the complete probability table.

The distinction is visible in a bounded numerical exploration (solver values only):

| Settings per party | Complete-table CF | Complete-table N | Complete-table CF/N | Cycle-cover CF/N |
|---:|---:|---:|---:|---:|
| 3 | 0.598076 | 0.149519 | 4.000000 | 4 |
| 4 | 0.695518 | 0.175699 | 3.958588 | 6 |
| 5 | 0.755283 | 0.178603 | 4.228833 | 8 |
| 6 | 0.795555 | 0.207107 | 3.841279 | 10 |
| 7 | 0.824495 | 0.199141 | 4.140252 | 12 |

The rational example in Theorem 19 has different directions from this numerical table and has its own exact certificates. No exact optimality or quantum-realization claim rests on the floating-point exploration.

The chained construction and the vanishing local fraction of maximally entangled correlations are established literature [20,21]. The present development makes the optimization conventions, omitted contexts, and formal verification boundaries explicit. Relations in Contextuality-by-Default [17,18] use their own coupling space; their coefficients must not be transplanted without proving the identification.


## 8.6 Unbounded comparison on complete quantum Bell scenarios

**Theorem 22 (No uniform complete-quantum comparison constant).** For every
integer $k\ge2$, there is a finite-dimensional bipartite quantum behavior $P_k$
with two outcomes and $n=k^2$ settings per party, retaining all $n^2$ contexts,
such that, with

$$
s_k=1-\frac{k^2-1}{3k^3},\qquad
\beta_k=\frac{1-s_k}{s_k},\qquad
\alpha_k=1-\frac{1}{ks_k},
$$

$$
0<N_{\min}(P_k)\le\beta_k,\qquad
CF(P_k)\ge\alpha_k>0,\qquad
\frac{CF(P_k)}{N_{\min}(P_k)}\ge
3k-4+\frac{3}{k+1}.\tag{44}
$$

Thus $CF/N_{\min}$ is unbounded across complete quantum Bell scenarios.
In fact this sequence has $CF(P_k)\to1$ and $N_{\min}(P_k)\to0$.
The settings and a sufficient local Hilbert-space dimension grow with $k$;
no fixed-scenario or fixed-dimension unboundedness is asserted.

*Construction and proof.* Put $D=4n$ and define a real cyclic profile on
$\mathbb Z_D$. On its first half let

$$
f(t)=\begin{cases}-1+2t/k&0\le t<k,\\1&k\le t<2n,\end{cases}
\qquad f(t+2n)=-f(t).
\tag{45}
$$

Every entry lies in $[-1,1]$. Summing the ramp squares gives

$$
\sum_{t=0}^{k-1}(-1+2t/k)^2=\frac{k^2+2}{3k},
\quad \frac1D\sum_t f(t)^2=s_k,
\quad \sum_t\bigl(f(t+1)-f(t)\bigr)^2=\frac8k.
\tag{46}
$$

The last identity counts two ramps, each with $k$ increments of magnitude
$2/k$; all other increments, including the two flat joins, vanish. Indices
are cyclic. Let $r_j(t)=f(t+j)$ and $u_j=r_j/\sqrt{Ds_k}$. These are unit
real vectors. For every $0\le x,y<n$ define

$$
C_{xy}=\langle u_{2x},u_{2y+1}\rangle,\qquad
P_k(a,b\mid x,y)=\frac{1+abC_{xy}}4,
\quad a,b\in\{-1,1\}.
\tag{47}
$$

This defines the whole table. Cauchy--Schwarz ensures nonnegative cells,
and the marginals are uniformly $1/2$.

For quantum realization, use the finite unit-vector characterization of
bipartite correlations due to Tsirelson [22,23]. Explicitly, choose traceless
Hermitian Clifford matrices $\Gamma_1,\ldots,\Gamma_D$ with
$\Gamma_i\Gamma_j+\Gamma_j\Gamma_i=2\delta_{ij}I$ and
$\operatorname{tr}(\Gamma_i\Gamma_j)/d=\delta_{ij}$.
Standard Pauli strings supply dimension $d=2^{D/2}$. The formal construction uses a simpler sufficient real-symmetric recursion in dimension $d=2^D$: start with no generators on a one-dimensional space, adjoin $X\otimes I$, and replace each old generator by $Z\otimes\Gamma_i$. Anticommutation, trace orthogonality, and Hermiticity are proved for every finite $D$. Neither dimension statement claims minimality. Set
$A_x=\sum_tu_{2x}(t)\Gamma_t$ and
$B_y=(\sum_tu_{2y+1}(t)\Gamma_t)^\mathsf T$.
They are Hermitian involutions. Their binary projectors on
$|\Phi_d\rangle=d^{-1/2}\sum_i|ii\rangle$ have unbiased marginals and
correlation $d^{-1}\operatorname{tr}(A_xB_y^\mathsf T)=C_{xy}$,
proving (47). This sufficient dimension is not an optimal dimension claim.

Now construct a local behavior $L_k$: share a uniformly sampled coordinate
$t\in\mathbb Z_D$ and a fair sign $r\in\{-1,1\}$. Alice and Bob use the
stochastic responses

$$
\Pr(a\mid x,t,r)=\frac{1+ar f(t+2x)}2,\qquad
\Pr(b\mid y,t,r)=\frac{1+br f(t+2y+1)}2.
$$

Averaging gives $L_k(a,b\mid x,y)=(1+ab s_k C_{xy})/4$.
Let $W(a,b\mid x,y)=1/4$. Both $L_k$ and $W$ have positive normalized
extensions over all $2^{2n}$ deterministic assignments by Theorem 1.
If these extensions are $q_L,q_W$, then

$$
q=\frac{q_L}{s_k}-\frac{1-s_k}{s_k}q_W,
\qquad Tq=P_k,\quad \sum_gq_g=1,\quad N(q)\le\beta_k.
\tag{48}
$$

The last inequality follows pointwise from
$[-q_g]_+\le\beta_k(q_W)_g$. This certifies an upper bound for the minimum
over the full assignment space; it does not discard off-chain contexts.

For the lower CF witness, the $2n-1$ adjacent edges of the alternating
Alice--Bob chain have correlation

$$
v_k=1-\frac{1}{nk s_k}.
$$

Indeed the energy identity (46) says
$2Ds_k(1-v_k)=8/k$. The final edge has correlation $-v_k$ by
anti-periodicity. Every deterministic assignment fails at least one of
these $2n$ constraints, while the expected number of failed constraints
under $P_k$ is $n(1-v_k)=1/(ks_k)$. The nonnegative failure-count witness
therefore bounds every feasible local packing mass by $1/(ks_k)$,
giving $CF(P_k)\ge\alpha_k$. Equivalently, restriction to the cycle
cannot increase the available local packing mass. The witness is supported
on the cycle, but the packing being bounded must fit the full table.

For $k\ge2$, $1/2<s_k<1$ and $\alpha_k>0$. The finite-context bound
of Theorem 13, applied to an attained signed minimum, then excludes
$N_{\min}=0$. Finally direct algebra yields

$$
\frac{\alpha_k}{\beta_k}
=\frac{3k^3-4k^2+1}{k^2-1}
=3k-4+\frac{3}{k+1},
$$

which tends to infinity. The same formulas and $CF\le1$ give the two
claimed limits. $\square$

| $k$ | Complete contexts $k^4$ | Certified CF lower bound | Certified N upper bound | Certified CF/N lower bound |
|---:|---:|---:|---:|---:|
| 2 | 16 | $3/7$ | $1/7$ | $3$ |
| 3 | 81 | $46/73$ | $8/73$ | $23/4$ |
| 4 | 256 | $43/59$ | $5/59$ | $43/5$ |
| 5 | 625 | $92/117$ | $8/117$ | $23/2$ |
| 8 | 4096 | $427/491$ | $21/491$ | $61/3$ |
| 12 | 20736 | $4609/5041$ | $143/5041$ | $419/13$ |

Theorem 21 remains valid for the complete equally spaced planar
single-Bell-pair family. Theorem 22 changes the family: its normalized
smoothed profiles have a local model at visibility $s_k\to1$ while the
number of chained constraints grows. Weight of contextual content and
cost of signed cancellation consequently have no uniform conversion
factor as the scenario varies. This is a resource-measure separation,
not an impossibility of learning or a claim of an external observer.

**Formalization scope.** Theorem 22 is now an end-to-end Lean theorem.
Bell.CompleteQuantumUnbounded.quantum_unbounded constructs a complete
behavior, a finite quantum realization, and a normalized signed extension
that minimizes negative mass against every real competitor. It proves
strictly positive minimum mass and a ratio exceeding any proposed
nonnegative constant. Quantum realization and the certificate envelopes
are conclusions, not premises.

CyclicProfile proves the modular ramp, antiperiodicity, norm, cyclic
energy, and shifted inner products. Clifford, CliffordObservables,
MaximallyEntangled, and GramQuantum construct the arbitrary finite
matrix model, including positive complete POVMs and every Born cell.
ChainWitness bounds full-table packings using the chained failures.
SmoothedFamily connects those constructions to (44)--(48).
The cycle reconstruction and two-fold optimization equivalences remain
separately proved. The numerical Clifford replay uses the smaller
standard representation; it does not execute the enormous general
formal matrices. No novelty or priority claim is made for the
resource-measure separation.

## 8.7 Finite constructions and selected continuum shadows

The tables in Theorem 22 are rational at every finite $k$. Their vector
normalization uses square roots that cancel from the final probabilities.
The all-size assertion $\forall C\,\exists k$ requires neither an infinite
experiment nor a differential equation. A continuum shadow is a further
choice of presentation, metric, and query, rather than a claim that the
world itself performs real-number calculus.

To make that choice explicit, set $h=1/k$ and use the usual Archimedean
real metric. The certificate functions become
\[
s(h)=1-\frac h3+\frac{h^3}3,\quad
\alpha(h)=1-\frac h{s(h)},\quad
\beta(h)=\frac{1-s(h)}{s(h)}.
\]
The pair has the endpoint $(1,0)$ at $h=0$. Its ratio
\[
\frac{\alpha(h)}{\beta(h)}
 =\frac3h-4+\frac{3h}{1+h}
\]
has no finite real endpoint.

**Theorem 23 (A declared scalar shadow and its error cutoff).** For the
complete behaviors of Theorem 22, every $\varepsilon>0$ and integer
$k\ge2$ with $k>2/\varepsilon$ satisfy
\[
|CF(P_k)-1|<\varepsilon,\qquad
|N_{\min}(P_k)|<\varepsilon.
\]
Moreover the ratio envelope $3k-4+3/(k+1)$ has no finite real limit.
*Proof.* Direct algebra gives
$0<1-\alpha_k<2/k$ and $0<\beta_k<2/(3k)$.
Use $\alpha_k\le CF(P_k)\le1$ and
$0<N_{\min}(P_k)\le\beta_k$. The ratio exceeds $3k-4$.
Lean proves the actual-optimum cutoff in
CompleteQuantumUnbounded.finite_shadow_error and the absence of a finite
endpoint in ContinuumShadows.no_finite_ratio_endpoint. $\square$

This is a limit of scalar summaries across growing scenarios. It does
not supply a common limiting density operator, a fixed-scenario limit,
or a continuum of actual measurement settings. Those require their own
presentation and convergence hypotheses.

The WDP CODA-CS-Q bridge separates exact factorization on presentation
fibers from stable extension to a completion [24]. Its presentation
criterion requires arbitrarily close presentations to force arbitrarily
close query values, uniformly on the actual image. CODA-CS is the finite
descended shadow; CODA-Q supplies the selected completion. The endpoint
above is a concrete scalar example of this route, with the chosen
metric and discarded information stated.

There is also a useful failure of uniform control. The constructed local
table is $L_k=s_kP_k+(1-s_k)W_k$. Thus each cell differs by at most
$(1-s_k)/4$ and each context's total-variation distance is at most
$(1-s_k)/2$, both tending to zero. Nevertheless $CF(L_k)=0$ while
$CF(P_k)\to1$. No modulus independent of scenario size can recover
contextual fraction from that cellwise accuracy alone: the witness
aggregates a growing number of constraints. This written consequence
does not claim that tables on different setting sets already share one
metric space. See the continuum shadow note in the package for the
exact boundary and preserved historical WDP sources.

# 9 Presentation families and task relevant projection loss

## 9.1 A carrier need not be an ontological background

The finite inference results do not require a brain, a body, or a Hilbert space to be treated as an observer-independent starting point. Declare a set $\mathcal H$ of admissible histories or candidate situations and a family of presentations
$$
O_\alpha:\mathcal H\longrightarrow Y_\alpha.
$$
The elements of $\mathcal H$ index possibilities admitted by the model. They need not be asserted to be ultimate physical states. Their interpretation, admissibility, and relation to observations remain part of the model's assumptions. Choosing this carrier does not derive it from an absence of primitives.

Given observed presentations, write $O(h)=(O_\alpha(h))_\alpha$. The equivalence relation
$$
h\sim_O h'\iff O(h)=O(h')
$$
defines what the observer cannot presently distinguish. Its fiber at report $y$ is $\mathcal H_y=O^{-1}(y)$. For a nonlinear observation map this fiber relation, rather than a linear kernel, is the appropriate language.

An observation map is not automatically a retraction. If a decoder chooses a representative $s(y)\in\mathcal H_y$, then $\Pi=s\circ O$ satisfies $\Pi^2=\Pi$. However, a difference $h-\Pi(h)$ is defined only if an appropriate vector representation has also been supplied. The inference theory below needs neither vector subtraction nor a product manifold.

## 9.2 The exact observer fiber error floor

Let $f:\mathcal H\to\mathbb R$ be a declared target, such as a future readout, the performance of a proposed modification, or a quantity to be certified. Assume $\mathcal H$ is finite and nonempty. On a nonempty fiber define
$$
W_f(y)=\max_{h\in\mathcal H_y}f(h)-\min_{h\in\mathcal H_y}f(h).
$$

**Theorem 8 (Task sufficiency and scalar minimax residual).** There exists a predictor $g$ satisfying $f=g\circ O$ exactly if and only if $f$ is constant on every observer fiber. More generally,
$$
\inf_g\max_{h\in\mathcal H}|f(h)-g(O(h))|
=\frac12\max_{y\in O(\mathcal H)}W_f(y).
\tag{25}
$$

**Proof.** Equal reports necessarily give equal values of $g$. If $f$ is constant on fibers, define $g(y)$ to be that common value. For the quantitative statement, let $a_y$ and $b_y$ be the smallest and largest target values in a fiber. Any scalar prediction $z$ obeys
$$
b_y-a_y\le|b_y-z|+|z-a_y|,
$$
so its maximum error is at least $(b_y-a_y)/2$. Choosing the midpoint $g(y)=(a_y+b_y)/2$ attains that error for every member of the fiber. Maximize over fibers. $\square$

**Formalization.** `Bell.Observer.scalar_minimax` proves (25) as an infimum over actual predictor risks, and `midpoint_optimal` proves attainment. The formal maximum ranges over histories through their reports, which is equivalent to maximizing over the image of the observation map. The qualitative factorization theorem also holds without finiteness.

An observer can therefore discard extensive information while remaining sufficient for a particular task. Non-injectivity alone is not a prediction obstruction. The obstruction is variation of the target along an unresolved fiber. Equation (25) is a finite scalar minimax statement; vector-valued targets require their actual feasible prediction sets and metric radii, not independent scalar midpoints.

This is the discrete counterpart of the phase-fiber prediction analysis in [P1, Sections 7.5 and 7.6]. As an exact two-state example, take
$$
|+\rangle=(|0\rangle+|1\rangle)/\sqrt2,\qquad
|-\rangle=(|0\rangle-|1\rangle)/\sqrt2.
$$
The observation retaining only computational-basis populations reports $(1/2,1/2)$ for both. After a Hadamard transformation, the probability of output $0$ is respectively $1$ and $0$. The best scalar predictor from those populations alone has worst-case error $1/2$. This is a prediction ambiguity, not a Bell violation. An independently available $X$-expectation report separates the two states. An actual quantum measurement protocol must still specify state preparation and available copies; formal statistics are not automatically simultaneous single-shot measurements.

## 9.3 Why serial language is not intrinsically low dimensional

A finite graph, a finitely specified matrix, or a finitely specified collection of noncommuting operator rules can be encoded injectively as a finite string. Ordering the symbols does not force the encoded objects to commute, erase graph cycles, or factorize the represented distribution. A transcript's one-dimensional order is not the dimension of its semantic state space. Shannon's communication model distinguishes the message set from its encoding and channel [9].

A concrete capacity obstruction requires a budget. If a message uses at most $b$ binary digits in a fixed-length code, it has at most $2^b$ values. Exact reconstruction of $N>2^b$ distinguishable states is then impossible by the pigeonhole principle. For task prediction, the relevant number is the number of task distinctions that must survive. Even when state reconstruction is impossible, exact prediction of a constant or otherwise sufficiently compressed target can remain possible.

Thus the relevant language argument is conditional: a particular encoding, finite context, measurement interface, or summary may merge histories that matter for the task. Increasing the length, using a more suitable code, or retaining additional data can change those fibers. The mere fact that a model emits successive tokens establishes none of the required losses.

## 9.4 Several presentations can remove an ambiguity

For reports $O_1,O_2$, the joint fiber is
$$
\mathcal H_{y_1,y_2}
=O_1^{-1}(y_1)\cap O_2^{-1}(y_2).
$$
Adding an informative report can only shrink the fiber and cannot increase its target width. In a linear vector model, the corresponding invisible subspace is $\ker O_1\cap\ker O_2$. For example, observations $O_1(u,v)=u$ and $O_2(u,v)=v$ are each non-injective but jointly recover $(u,v)$ exactly. There is no general theorem that every finite observer family has a surviving blind direction.

If instead $O_2=\varphi\circ O_1$, the second presentation leaves the fibers unchanged. Rephrasing an existing report can aid computation or interpretation without supplying a new distinguishing observation. Translation, poetic restatement, or alternative reasoning is informative about an external target only insofar as it brings in additional warranted information or reveals consequences already implicit in the report.

When overlapping presentations are compared, declare what their common reports mean and supply the restriction maps. For linear data the familiar defect is
$$
\Delta_{\alpha\beta}
=r_{\alpha\to\alpha\beta}(y_\alpha)
 -r_{\beta\to\alpha\beta}(y_\beta).
$$
A nonzero value witnesses disagreement under those maps. It does not uniquely identify the lost state, establish that the higher-dimensional model is correct, or act as a certificate of truth. Noise, faulty adapters, and an incorrect model can also produce disagreement. Conversely, zero disagreement can coexist with a positive Bell residual or a nonzero task-fiber width.

## 9.5 When local reports can bound a global defect

The strongest scaling example in [P1, Section 7.4] can be situated in a general finite linear statement. Let $V,Y,Z$ be finite-dimensional normed spaces, let $O:V\to Y$ collect the local reports, and let $G:V\to Z$ be the defect one seeks to control.

**Proposition 9 (Linear visibility criterion).** Let $O:V\to Y$ and $G:V\to Z$ be linear maps between finite-dimensional real normed vector spaces. There is a finite constant $C$ such that $\|Gv\|\le C\|Ov\|$ for every $v\in V$ if and only if $\ker O\subseteq\ker G$.

**Proof.** The inequality forces $Gv=0$ whenever $Ov=0$. Conversely, that kernel inclusion makes $B(Ov)=Gv$ a well-defined linear map on $\operatorname{im}O$. It is bounded in finite dimensions, so $C=\|B\|$ gives the inequality. $\square$

If the kernel inclusion fails, choose $v_0$ with $Ov_0=0$ and $Gv_0\ne0$. On the unrestricted vector carrier, $\|G(tv_0)\|=|t|\|Gv_0\|$ is unbounded although every observed report remains zero. Therefore no finite-valued function $F$ can bound $\|Gv\|$ solely by $F(\|Ov\|)$ on that carrier. This is the mechanism of the source paper's local-zero/global-nonzero scaling construction.

On a bounded physical carrier, an arbitrary-size scaling argument is unavailable. A constant global bound may exist. The surviving claim is a positive uncertainty floor or failure of a modulus with $F(0)=0$, when equal reports conceal distinct target values. In particular, the trace-norm distance of two density matrices is at most two. One cannot transfer an unbounded cochain counterexample to a normalized-state or bounded-score problem without checking the carrier and normalization.

# 10 Recursive self improvement and the observer boundary

## 10.1 An evidence preserving recursion theorem

Suppose an agent's initial information is $y=O(h)$, including all relevant training information, weights, inputs, accessible tools' fixed contents, and other side information. Fix the same initial information across the candidate histories being compared. Let the agent recursively update its internal state, code, or predictor using only this information and internal computation. Any world-dependent feedback received later must be added to the observation; it is not silently covered by this hypothesis.

**Theorem 10 (No recovery by evidence preserving recursion).** Let $Z_n$ be the scalar prediction after any finite number $n$ of such updates. If the updates use randomness, assume its distribution conditional on $y$ is independent of which $h\in\mathcal H_y$ is actual. Then
$$
\max_{h\in\mathcal H_y}\mathbb E|Z_n-f(h)|
\ge\frac12W_f(y).
\tag{26}
$$
The same lower bound holds for any well-defined limiting output whose distribution still depends only on $y$. Arbitrary changes to internal representation or code do not alter it.

**Proof.** Induction over the updates shows that the conditional distribution of $Z_n$ is the same for all histories in a fiber. Choose histories attaining target values $a_y$ and $b_y$. For each possible output $z$, $|z-a_y|+|z-b_y|\ge b_y-a_y$. Take expectations under the common output distribution. At least one of the two expected errors is at least half the width. The proof uses only equality of output laws, so also applies to a limiting output satisfying that condition. $\square$

This includes self-modification: rewriting the update procedure from unchanged evidence still gives the same procedure and output law on indistinguishable histories. A training or evaluation loop that obtains new observations is outside this fixed-evidence condition and must be analyzed with its enlarged observation map. The argument is elementary indistinguishability, not a new undecidability theorem; it does not depend on a particular programming language, neural architecture, or claim of logical incompleteness.

**A finite counterexample to guaranteed self-certification.** Let $\mathcal H=\{h_0,h_1\}$, let $O(h_0)=O(h_1)$, and let $f(h_0)=-1$, $f(h_1)=1$ denote the true performance change caused by a proposed modification. Every evidence-preserving recursion faces error at least one. It cannot truthfully certify that the modification improves performance in every history consistent with its report. It can correctly report the uncertainty, abstain, or seek a discriminating evaluation. If the task is instead to distinguish the two histories, randomized success under equal prior weights is at most $1/2$.

An evaluator computed solely from the same report can nevertheless assign a perfect score to the proposal. That score establishes performance under the evaluator's rule; it does not establish the sign of $f$ on the unresolved fiber. The problem is the missing relation between the evaluation and the target, not the numerical value of the score.

## 10.2 What the theorem permits

Theorem 10 imposes an informational lower bound on a declared task and carrier. It does not imply that additional computation is useless. Computation can discover a consequence already determined by the input, improve an initially poor estimator toward the minimax optimum, find a proof, reduce costs, or design a discriminating experiment. An unresolved computational problem can have a unique correct answer throughout the fiber; then (25) has zero information-theoretic floor even though finding the answer remains difficult.

Nor does the theorem forbid general RSI or ASI. A system may gain sensors, retrieve previously inaccessible records, run external experiments, modify its environment and observe the result, or acquire reliable feedback. Its evidence changes. It may also surpass human performance on a broad task family while retaining unavoidable uncertainty elsewhere. No premise here supplies a universal rate bound on improvement, a maximum level of intelligence, or a proof that all feasible agents are confined to one immutable presentation.

More parameters can also embody additional training evidence or a better inductive bias. The theorem compares histories with identical *total available information*; it cannot be applied by ignoring information stored in model weights. Frozen weights do not imply the absence of present-time input, state, or interaction.

The resulting no-go statement is exact and limited: **a recursion cannot guarantee recovery of a task distinction that its total evidence does not distinguish, unless an additional justified assumption removes that distinction from the admitted carrier.** Assuming such a restriction can improve prediction, but the resulting guarantee is conditional on its validity.

## 10.3 Active observation and predictive closure

Allow actions $a$ and world-dependent responses. For a realized action-observation transcript $\tau_n$, let $\mathcal H(\tau_n)$ contain the histories still compatible with it. In a deterministic finite model, each new response refines the current set. A natural certificate for a scalar target is
$$
\varepsilon_f(\tau_n)
=\frac12\left(\max_{h\in\mathcal H(\tau_n)}f(h)
                   -\min_{h\in\mathcal H(\tau_n)}f(h)\right).
\tag{27}
$$
Here the target is fixed; if the action changes what is being evaluated, the target function must be updated explicitly. In a noisy model, hard compatibility sets require replacement by an appropriate statistical analysis.

If every permitted adaptive experiment gives the same transcript distribution under two candidate histories, internal recursion cannot distinguish them either. Conversely, an allowed query with different deterministic answers separates them. In the two-history example above, one query returning the hidden bit reduces the error floor from one to zero. The obstruction is therefore relative to the allowed observation and intervention family.

To avoid assuming a privileged present state, define two histories to be predictively equivalent when all allowed continuations have the same future observation distributions. This relational quotient is sufficient for those predictions by construction. Predictive state representations are an established approach to describing dynamical systems through future tests rather than an assumed hidden-state description [10]. Construction of the quotient does not establish that it is finite, efficiently learnable, or known to the agent.

For a deterministic evolution $T_t$ and summary $O$, exact autonomous summary dynamics exists precisely when
$$
O(h)=O(h')\ \Longrightarrow\ O(T_t h)=O(T_t h')
\quad\text{for every allowed }t.
\tag{28}
$$
Then $\overline T_t(O(h))=O(T_t h)$ is well-defined, and if the original $T_t$ form a semigroup, so do the induced maps. This follows directly from well-defined composition. Failure of (28) identifies a predictive insufficiency that can be addressed by memory or richer observations; it does not imply consciousness. It also clarifies why [P2]'s retracted family may fail the semigroup law while a sufficient quotient would preserve it.

## 10.4 The precise relation to Bell's theorem

Bell and RSI share the requirement to declare the admissible representations and the maps connecting them to observations. Their principal failures have different logical forms:

| Question | Mathematical test | Failure witness |
|:--|:--|:--|
| Bell-local realizability | Does $T^{-1}(p)\cap\Delta(\Omega)$ contain a point? | A separating Bell inequality |
| Exact prediction from a report | Is $f$ constant on $O^{-1}(y)$? | Two equal-report histories with different target values |
| Overlap consistency | Do restricted reports agree? | A nonzero adapter defect |
| Autonomous reduced dynamics | Does every future report descend through $O$? | Equal present reports with unequal future reports |

Bell nonlocality is nonexistence of a realization in a specified positive local model class. Prediction insufficiency is multiplicity of allowed realizations with incompatible answers. These are not the same theorem. In particular, an ordinary context-sensitive language system has not violated Bell merely because its responses change across prompts; Bell's experimental factorization and setting assumptions must first be defined and justified.

The useful common research programme is to retain both kinds of witness. A reasoning engine should test whether its observations admit the declared model at all, and, when they do, whether the requested answer is determined across the surviving possibilities. An empty feasible set calls for model or data review. A wide feasible fiber calls for uncertainty, stronger evidence, or a narrower task. Neither problem is solved by fluency alone.

# 11 Finite verification and empirical use

The distance in (3) is computed by the following linear program. Introduce nonnegative variables $q_\lambda,u_{abxy}$ and solve
$$
\begin{aligned}
\text{minimize}\quad &\frac12\sum_{xy}\pi_{xy}\sum_{ab}u_{abxy},\\
\text{subject to}\quad &-u\le p-Tq\le u,\qquad
q\ge0,\qquad \sum_\lambda q_\lambda=1.
\end{aligned}
\tag{29}
$$
The negative-mass problem is also linear: write $q=q^+-q^-$, impose $q^\pm\ge0$, $T(q^+-q^-)=p$, $\sum(q^+-q^-)=1$, and minimize $\sum q^-$. Enumeration grows exponentially with the number of local measurements; finite formulation does not imply scalability to arbitrary scenarios.

For the CHSH scenario, the signed normalized fiber exists precisely on the normalized no-signalling affine space, allowing signed table entries in this affine statement. The supplied exact checker gives marginalization rank nine, ambient no-signalling constraint rank seven, and normalized affine dimension eight. Positivity is an additional constraint. The negative-mass dual uses $-1\le\alpha\cdot\ell_\lambda+\beta\le0$ for every deterministic vertex. Eliminating $\beta$ gives a vertex-spread bound of one and objective $\alpha\cdot p-\max_\lambda\alpha\cdot\ell_\lambda$. The general signed LP duality is formalized in `Bell.SignedDuality.bell_negative_mass_duality`; `bell_signed_spread_duality` eliminates the normalization offset and proves attainment of the vertex-spread witness. Feasibility of the normalized signed fiber is an explicit premise. The CHSH rank and affine-dimension calculations remain exact finite checks.

The reproducible code in `code/reproduce_examples.py` checks the sixteen-assignment CHSH calculation using exact rational arithmetic, verifies the positive boundary extension, and independently solves the two linear programs for selected values of $v$. It checks the observer-fiber and recursion examples and also checks the two-qubit trace norms and CHSH values and the three-party Mermin witness by floating-point matrix calculations. Exact rational checks establish the specified finite identities. Floating-point optimization and matrix checks are consistency tests, not substitutes for the proofs or certified interval computations. The Lean scope and replay protocol are given below. These calculations do not constitute an experimental Bell test.

For empirical data $\widehat p$, if a statistical procedure supplies the confidence statement $\|p-\widehat p\|_\pi\le\varepsilon$, then (4) gives
$$
R_\pi(p)\ge[R_\pi(\widehat p)-\varepsilon]_+.
\tag{30}
$$
The confidence level and assumptions belong to that statistical procedure. Finite samples can show apparent signalling; a distance from $\widehat p$ to $\mathcal L$ may then include both sampling inconsistency and Bell nonlocality. The four-context probability model, trial selection, and setting assumptions must be stated before interpreting a numerical residual. Equation (30) is a stability statement, not a complete experimental analysis.

## 11.1 Lean proof coverage and axiom census

Version 0.13.0 contains 656 named Lean theorems, compiled with Lean 4.35.0. The fresh census records only the standard dependencies `propext`, `Quot.sound`, and `Classical.choice`; it contains no custom axioms or admitted proofs. Every named theorem is included in the census, including the intermediate normalization and marginalization results used by Theorem 1.

The CHSH module proves the local bound, the bound (7) against every local approximation, the normalized signed-extension negative-mass bound, and the isotropic score and nonlocality threshold. It also proves the uncertainty-adjusted bound
$$
\|p-\ell\|_\pi\ge\frac{[|S(\widehat p)|-2-8\varepsilon]_+}{8}
\quad\text{for all }\ell\in\mathcal L,
\qquad \|\widehat p-p\|_\pi\le\varepsilon,
$$
for uniform CHSH settings. The statistical enclosure is a supplied premise.

The observer module proves task sufficiency, the exact finite scalar minimax equality and midpoint attainment, monotonicity under report refinement, and the unchanged error floor after any number of report-preserving updates. Its randomized theorem permits a different finite conditional output law for each report, provided histories with that report share the law. It bounds worst-case expected absolute error; arbitrary-measure randomization is not instantiated in this release.

The probability-integral instance, Tsirelson operator and pure/finite-mixture state bounds, exact two-qubit saturation, and the finite-dimensional POVM and density-matrix conversions of Proposition 5b are included in the census. The separable-state results construct separable density mixtures and their local models, derive partial-trace density matrices and the product-marginal retraction, and prove the full state-to-behavior bound (15) for finite local POVMs, with a uniform CHSH specialization. The census also proves attained weighted repair and signed-negative-mass LP duality, finite polyhedral projection, and the intrinsic tangent-cone ray and remainder results. The complete isotropic repair-cost sharpness calculation, infinite-dimensional trace-class conversions, and Mermin cohomology results remain outside it. The real-parameter CHSH/Mermin negative-mass and contextual-fraction optima, the explicit comparison counterexample and reversed ordering, and the constructive finite-context comparison are now included. Prior Isabelle/HOL formalization of classical and separable CHSH bounds, the quantum ceiling, and saturation is given in [14]. `docs/formalization.md` maps each claim to its declarations and exact assumptions.

The standalone archive includes pinned offline dependency sources and compiled libraries, their licenses and hash manifest, all Bell proof sources, the raw axiom report and the census. With Lean 4.35.0 and the listed Python dependencies installed, `python verify_deposit.py` checks the archive payload, compiles all Bell proofs in a new build directory, regenerates and compares the axiom census, runs the 60 tests in small batches, finite reproduction, supplied 39-check review script and 15 separately validated primal/dual certificates, and executes the notebook cells. It needs neither a sibling paper nor a network fetch.

The three added chained-Bell modules prove assignment completeness, real-parameter optimization, local projective effects, the exact two-qubit Born table, and the strict quantum counterexample of Theorems 17–18. The exact radical checker covers all 36 cells and both optimization certificates; its separate numerical LP comparison is consistency evidence rather than the proof.

## 11.2 Computational evidence and independence

The exact checker `code/bell_certificates.py` independently enumerates the deterministic CHSH model. `code/review_certificates.py` validates the solver's returned feasibility constraints and objective equalities, while reusing the supplied solver's model helpers. The latter is an independent check of answers, not an independently encoded experimental model. The mathematical LP duality theorems do not certify the supplied Python simplex implementation. The verifier imposes finite subprocess timeouts; a timeout is a verification failure.

The new checker independently enumerates both deterministic models and verifies all normalization, no-signalling, primal and dual constraints using Python Fraction arithmetic. Across 78 supplied cases (62 CHSH, 16 three-party), 74 have CF=2N, three have CF<2N, and one has CF>2N. These finite observations do not prove a universal CHSH identity. SciPy is used only for candidate search in the optional regeneration script; every accepted answer is checked exactly. A read-only generator binds the explicit Lean integer fixture to the stored rational certificate. Seven mutation controls test rejection of altered certificates and malformed inputs.

The unchanged supplied inputs, their hashes, and the detailed assessment of the reviews are recorded in `docs/source_custody.json` and `docs/review_assimilation.md`.

# 12 Interpretation and scope

The projection viewpoint gives a precise answer to what remains after a local classical explanation has been made as accurate as possible: a signed residual table, and a dual Bell functional that detects its unavoidable part. Every positive local hidden-variable model lies in the target polytope. A nonzero residual therefore records failure of that entire model class, rather than failure of one insufficiently expressive choice of hidden variable.

This formulation connects naturally to [P1, P2], but the targets of reduction must remain explicit. State product retraction removes even shared classical correlations. Bell-local convex repair retains them. Overlap coboundaries test marginal agreement. Support cohomology can detect parity contradictions. Positive-extension feasibility tests the probability weights as well. These are related constructions with distinct kernels and distinct witnesses.

No-signalling survives the quantum example, so the residual does not by itself describe a controllable superluminal signal. It also does not select a unique ontology, derive the Born rule, or show that an inaccessible higher-dimensional local classical distribution restores Bell locality. Such a distribution, if it obeyed (1), would still induce a positive extension and would still satisfy CHSH. What the paper establishes is a representation theorem and quantitative obstruction, conditional on the explicitly stated Bell assumptions and the quantum measurement model used in its examples.

The Bell-specific next mathematical problem is to study when the measured state velocity exits the local tangent cone, and how higher-order state dynamics control that exit. Equations (9), (15), and (18) identify the ingredients: the measurement map, the feasible local cone, an oriented witness, and a controlled remainder. They make the connection to projection dynamics concrete while leaving the positive-extension content of Bell's theorem intact.

For RSI, the corresponding problem is to design updates that expose and reduce task-relevant fiber width. A system can improve its computation within its existing evidence, and it can improve the evidence through informative interaction. Those are distinct sources of progress. Theorem 10 rules out guaranteed recovery across an unresolved distinction; it does not rule out progress, powerful artificial intelligence, or empirically successful self-improvement. Future work should specify the retained observations, the admissible alternatives, and the task before asserting that a memory or learning update reduces an obstruction.

# 13 Research programme and evidence map

Bell belongs to the classical marginal-extension problem: compatible distributions on overlapping contexts may fail to be marginals of one positive global distribution. In the sheaf formulation, this is an obstruction to global sections [4]; Bell nonlocality is a special case of contextuality. In the present programme's local-green/global-red (LGGR) terminology, local green means normalized nonnegative tables with consistent overlaps, and global red means no positive extension in the declared setting-independent local model. Support consistency, signed extension and positive extension must remain distinct.

This foundational classification is established mathematics. Proportionality results relating contextual fraction and negative-probability measures for cyclic systems, a class containing CHSH, are also established [17, 18]; their coupling and normalization conventions must be respected when comparing formulas. The present Lean comparisons and dynamical bridges are a concrete contribution to reproducibility; this paper makes no priority claim for the family formulas or the finite-context comparison constant. Recent work develops simplicial resource transformations [15], while a 2026 preprint reports formal CHSH rigidity in Lean [16]. The latter concerns recovering a near-canonical quantum realization from a near-optimal score, which is stronger than merely proving the score ceiling. Its reported formalization has not been independently replayed here.

The research frontier relevant to this package is therefore specific: sharp scenario-dependent CF/negative-mass/repair comparisons, comparisons restricted to quantum-realizable behaviors, resource transformations preserving those bounds, and dynamical cone-exit certificates with remainders derived from an implemented evolution. The current counterexample is no-signalling but is not proved quantum-realizable; the constant in (34) is not proved sharp; general dynamical remainder bounds remain premises. Section 8.3 now resolves a concrete unitary orbit and its certification window, while sharp comparisons over the full quantum set and general evolution-derived remainder bounds remain research targets.


The common mathematical object is an observation map restricted to a declared admissible class. Bell asks whether its inverse image of an observed table contains a positive local model. Embedded prediction asks whether a task is constant on an existing inverse image. The first may have an empty feasible set; the second may have several task-distinct elements. They require different certificates.

For Bell dynamics, the next target is a checked witness of exit from the local tangent cone together with a remainder enclosure. For memory, the target is a measured reduction of task-relevant fiber width after an evidence-bearing update. The PO correction-window bound can limit how long a fixed enclosure remains valid, but cannot manufacture a Bell witness or establish that a memory learned new information.

| Result | Evidence in this package | Remaining premise or boundary |
|---|---|---|
| Positive extension and classical CHSH | Lean probability-integral and finite equivalences; witness bounds | Setting-independent probability measure and measurable normalized local responses |
| Quantum CHSH ceiling, conversions and saturation | Lean operator/state bounds, finite density/POVM conversions and exact two-qubit Born table | Positive unit-trace finite matrices; normalized binary effects; cross-party commutation for joint probabilities, proved for tensor lifts |
| CHSH/Mermin signed negativity and contextual fraction | Lean real-parameter optima; exact rational primal/dual replay | Stated families; Mermin quantum realization now includes an explicit Lean Born table |
| CF versus signed mass | Lean explicit counterexample, reversed ordering and finite-context upper bound | Three-party example quantum status unknown; complete quantum examples disprove factors two and four; cycle-cover ratios are unbounded, while complete regular chains have a bounded tail. Theorem 22 has an end-to-end Lean construction, including the full quantum model and attained signed minimum; Theorem 23 gives selected real-metric scalar shadows. No fixed dimension, physical continuum, or infinite-dimensional limiting state is asserted |
| General LP duality and tangent cone | Lean attained repair and signed duals; finite polyhedral projection; intrinsic cone, exact short rays and quadratic remainder | Finite scenario, nonempty outcomes, inhabited normalized signed fiber for signed duality, normalized nonnegative context weights; zero-repair equivalence uses strictly positive weights; a trajectory remainder is supplied |
| State-to-behavior and dynamical witness | Lean finite separable construction, full bound (15), and conditional witness; written trajectory examples | Positive complete finite POVMs, normalized context weights; dynamics requires an exact decomposition and trace-norm remainder enclosure |
| Fiber-width and recursive evidence limit | Lean exact minimax, midpoint attainment, refinement and recursion bounds | Finite nonempty histories; finite randomized conditional output laws |

## 13.1 Side note: contextuality theory and research level

A context is a collection of jointly performable measurements. Contextuality asks whether their probability tables can all be restrictions of one distribution over context-independent outcome assignments. Bell nonlocality is the separated-site case [4]. Locally compatible data can fail this positive extension without any inconsistency in nature or any observer outside it. Kochen–Specker, Bell, and generalized operational contextuality have different assumptions [19]; ordinary dependence on surrounding information is not automatically a violation.

The elementary CHSH and small Hamiltonian calculations are advanced undergraduate or introductory graduate material. Convex duality, quantum measurement theory, and resource-theoretic comparisons are graduate topics. The reusable Lean proofs and reproducible certificate package constitute substantial formal-methods work. That assessment does not establish new mathematical priority. This release is a checked synthesis, concrete dynamical extension, and exact quantum counterexample to the factor-two conjecture. The counterexample uses established chained Bell measurements; no priority claim follows. Section 8.5 further disproves factor four and separates unbounded cycle-cover ratios from complete-table comparisons. The longer reader's note, `docs/contextuality_side_note.md`, explains the measures, the literature, and what would constitute a stronger research advance. Current nearby work includes simplicial resource transformations [15] and reported Lean CHSH rigidity [16], neither of which is reproduced by merely deriving CHSH again.

# References

**[P1]** J. H. Carroll. *Projection Obstruction for Factorized States*. PO-000, version 6.9.20 (2026). Companion manuscript; its supplemental Lean census checks real uncertainty and correction bounds under declared analytic premises.

**[P2]** J. H. Carroll. *Higher-Cell Product Retractions, Simplicial Cochains, and Finite Retraction Dynamics*. PO-034, version 0.3.0 (2026). Companion manuscript; its supplemental Lean census checks the normed-carrier product-residual bound from explicit factor-replacement estimates.

**[1]** J. S. Bell. On the Einstein Podolsky Rosen paradox. *Physics Physique Fizika* **1**, 195-200 (1964). [doi:10.1103/PhysicsPhysiqueFizika.1.195](https://doi.org/10.1103/PhysicsPhysiqueFizika.1.195).

**[2]** J. F. Clauser, M. A. Horne, A. Shimony, and R. A. Holt. Proposed experiment to test local hidden-variable theories. *Physical Review Letters* **23**, 880-884 (1969). [doi:10.1103/PhysRevLett.23.880](https://doi.org/10.1103/PhysRevLett.23.880).

**[3]** A. Fine. Hidden variables, joint probability, and the Bell inequalities. *Physical Review Letters* **48**, 291-295 (1982). [doi:10.1103/PhysRevLett.48.291](https://doi.org/10.1103/PhysRevLett.48.291).

**[4]** S. Abramsky and A. Brandenburger. The sheaf-theoretic structure of non-locality and contextuality. *New Journal of Physics* **13**, 113036 (2011). [doi:10.1088/1367-2630/13/11/113036](https://doi.org/10.1088/1367-2630/13/11/113036); [arXiv:1102.0264](https://arxiv.org/abs/1102.0264).

**[5]** S. G. A. Brito, B. Amaral, and R. Chaves. Quantifying Bell nonlocality with the trace distance. *Physical Review A* **97**, 022111 (2018). [doi:10.1103/PhysRevA.97.022111](https://doi.org/10.1103/PhysRevA.97.022111); [arXiv:1709.04260](https://arxiv.org/abs/1709.04260).

**[6]** S. Abramsky, S. Mansfield, and R. Soares Barbosa. The cohomology of non-locality and contextuality. *Electronic Proceedings in Theoretical Computer Science* **95**, 1-14 (2012). [doi:10.4204/EPTCS.95.1](https://doi.org/10.4204/EPTCS.95.1); [arXiv:1111.3620](https://arxiv.org/abs/1111.3620).

**[7]** S. Abramsky, R. Soares Barbosa, and S. Mansfield. Contextual fraction as a measure of contextuality. *Physical Review Letters* **119**, 050504 (2017). [doi:10.1103/PhysRevLett.119.050504](https://doi.org/10.1103/PhysRevLett.119.050504); [arXiv:1705.07918](https://arxiv.org/abs/1705.07918).

**[8]** N. D. Mermin. Extreme quantum entanglement in a superposition of macroscopically distinct states. *Physical Review Letters* **65**, 1838-1840 (1990). [doi:10.1103/PhysRevLett.65.1838](https://doi.org/10.1103/PhysRevLett.65.1838).

**[9]** C. E. Shannon. A mathematical theory of communication. *Bell System Technical Journal* **27**, 379-423 and 623-656 (1948). [Primary paper, corrected reprint](https://www.princeton.edu/~wbialek/rome/refs/shannon_48.pdf).

**[10]** M. Thon and H. Jaeger. Links between multiplicity automata, observable operator models and predictive state representations: a unified learning framework. *Journal of Machine Learning Research* **16**, 103-147 (2015). [Primary publication](https://www.jmlr.org/papers/v16/thon15a.html).

**[11]** B. S. Cirel'son (Tsirelson). Quantum generalizations of Bell's inequality. *Letters in Mathematical Physics* **4**, 93-100 (1980). [doi:10.1007/BF00417500](https://doi.org/10.1007/BF00417500).

**[12]** G. Oas, J. A. de Barros, and C. Carvalhaes. *Exploring non-signalling polytopes with negative probability*. arXiv:1404.3831v2 (2014). [Primary preprint](https://arxiv.org/html/1404.3831v2).

**[13]** L.-L. Sun, X. Zhou, Z.-P. Xu, and S. Yu. *Lower-Bounding Entanglement in a general Bell scenario*. arXiv:2312.02588v2. [Primary preprint](https://arxiv.org/html/2312.02588v2).

**[14]** M. Echenim, M. Mhalla, and C. Mori. *The CHSH inequality: Tsirelson's upper-bound and other results*. Archive of Formal Proofs (2023). [Formal development](https://isa-afp.org/entries/TsirelsonBound.html).

**[15]** A. Kharoof and C. Okay. *Simplicial methods in the resource theory of contextuality*. arXiv:2505.24010 (2025). [Primary preprint](https://arxiv.org/abs/2505.24010).

**[16]** T. Zhao and N. Yu. *Formalizing CHSH Rigidity in Lean 4*. arXiv:2604.03884 (2026). [Primary preprint](https://arxiv.org/abs/2604.03884). Reported external formalization; not independently replayed in this package.

**[17]** V. H. Cervantes. *A note on the relation between the Contextual Fraction and CNT2*. arXiv:2110.07113v3 (2022). [Primary preprint](https://arxiv.org/abs/2110.07113).

**[18]** G. Camillo and V. H. Cervantes. *Measures of contextuality in cyclic systems and the negative probabilities measure CNT3*. arXiv:2305.16574 (2023). [Primary preprint](https://arxiv.org/abs/2305.16574).

**[19]** C. Budroni, A. Cabello, O. Gühne, M. Kleinmann, and J.-Å. Larsson. *Kochen–Specker contextuality*. Reviews of Modern Physics **94**, 045007 (2022), revised preprint 2023. [Primary review](https://arxiv.org/abs/2102.13036).

**[20]** S. L. Braunstein and C. M. Caves. *Wringing out better Bell inequalities*. Annals of Physics **202**, 22–56 (1990). [Author-hosted primary paper](https://www-users.york.ac.uk/~sb54/papers/90/bcB90.pdf).

**[21]** J. Barrett, A. Kent and S. Pironio. *Maximally Non-Local and Monogamous Quantum Correlations*. Physical Review Letters **97**, 170409 (2006). [Primary preprint](https://arxiv.org/abs/quant-ph/0605182).

**[22]** B. S. Tsirelson. *Quantum analogues of the Bell inequalities. The case of two spatially separated domains*. Journal of Soviet Mathematics **36**, 557–570 (1987); Russian original (1985). [Primary journal record](https://www.mathnet.ru/php/archive.phtml?jrnid=znsl&option_lang=eng&paperid=4332&wshow=paper).

**[23]** A. Prakash and A. Varvitsiotis. *Correlation matrices, Clifford algebras, and completely positive semidefinite rank*. arXiv:1702.06305v2 (2018). [Primary author preprint, Theorem 4.1 and constructive proof](https://arxiv.org/html/1702.06305v2).

**[24]** J. H. Carroll. *Witnessed Difference Programme*, Appendix O and
*Presentation closure from CODA-CS to CODA-Q and the circle dual*;
*Finite Profile Factorization and Sampling Limits (CODA-CS-Q)*;
*Continuum Shadow (CODA-CS)*. Historical sources at Git commit
762671d8cd1d61fbd30212d2bebb869aadc95850, preserved with byte hashes in
docs/wdp_continuum_sources.json. Used for presentation and completion
definitions; their historical validation is separate from this Bell census.

**Preparation note.** Prepared with AI assistance from the user-supplied Bell draft and the cited sources. The finite arguments are research claims offered for review. The formalized subset, ordinary theorem premises, and remaining written/numerical results are identified in Section 11.1 and the claim ledger.
