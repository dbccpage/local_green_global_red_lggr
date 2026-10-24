# Projection Residuals in Bell's Theorem and Recursive Self-Improvement

## Positive extensions, observer sufficiency, and limits on ASI self-certification

**Author:** Jeremy H. Carroll  
**Date:** 21 October 2026  
**Version:** 0.2, draft for author review  
**Source basis:** Two supplied projection-obstruction manuscripts and a supplied conceptual dialogue  
**Scope:** Finite mathematics with a separately marked interpretive discussion

## Abstract

Bell's theorem and limits on recursive self-improvement concern different kinds of representational failure. In a Bell experiment, a compatible family of measurement distributions may have no positive extension over local response assignments. In inference, multiple admissible histories may produce the same retained evidence but require different predictions. We formulate both using declared observation maps and residuals, without identifying nonexistence of a local realization with nonuniqueness of an inferred state. Drawing on product-retraction geometry and higher-cell observation maps, we prove quantitative Bell repair bounds, exact CHSH examples, and a state-to-behavior inequality. We then prove a finite observer-fiber minimax theorem and show that arbitrary recursive computation, self-modification, or randomization based on unchanged evidence cannot beat its worst-case error floor. The obstruction can be reduced by informative observations, justified restrictions of the admissible carrier, or changes to the task; it does not prohibit recursive self-improvement or artificial superintelligence in general. A finite phase example links the two parts through quantum prediction. We also examine narrative compression, memory, and the proposed interpretation of qualia as residual registration. Those interpretations remain hypotheses: neither serial language nor a nonzero cohomology class establishes a theory of consciousness. The paper distinguishes proved finite statements, standard results, and proposed applications throughout.

**Keywords:** Bell inequalities; recursive self-improvement; artificial superintelligence; projection residual; positive extension; observer sufficiency; cochains; narrative compression.

# 1 Introduction

Bell's theorem identifies quantum measurement statistics that cannot be reproduced by a locally causal hidden-variable model with a setting-independent hidden-variable distribution [1, 2]. Its geometric content is especially clear in a finite experiment: the admissible local models form a convex polytope, and a violating behavior lies outside that polytope. A Bell inequality is a separating linear functional.

The two source papers [P1, P2] provide a complementary language. A declared reduction retains some structure and discards other structure; the difference between the original object and its reduced representation is a residual. A specified observation map determines which part of that residual is visible. The present paper applies this language to Bell experiments and to the RSI/ASI questions in the supplied dialogue [P3]. Here RSI means recursive self-improvement: a system uses its current capabilities to modify its later computation or design. ASI means artificial capability exceeding human performance across a declared range of tasks; it is not defined as omniscience. We begin by preserving the distinction between four different questions:

1. Is a quantum state a product of its own marginals?
2. Are the observed distributions compatible on overlapping measurement contexts?
3. Do those distributions admit one positive global distribution over local response assignments?
4. Does a specified cochain construction produce a nonzero cohomology class?

These questions have different answers even in small finite examples. In particular, a classically correlated separable state fails the first condition while satisfying the third for every choice of local measurements. Conversely, quantum Bell violations satisfy overlap consistency but fail positive global extension.

Our central statement is therefore precise: **a Bell violation witnesses an unavoidable residual when an observed behavior is approximated by the complete convex class of Bell-local behaviors.** Calling this a projection residual identifies the failed representation and the distance used to quantify its failure. It does not introduce a physical projection process or supply a local hidden-variable explanation of the violating data.

The positive-extension characterization is closely related to Fine's theorem [3] and the sheaf-theoretic formulation of Abramsky and Brandenburger [4]. Distance to the local polytope is already an established nonlocality measure [5]. We do not claim those constructions as new. Our purpose is to connect them explicitly to the state residuals, observation maps, and dynamical estimates in [P1, P2]. The finite calculations below establish this connection without importing the source papers' broader foundational programme or assuming that every residual is cohomological. Sections 9 and 10 extend the analysis to task sufficiency and self-improvement. Section 11 examines the dialogue's philosophical interpretation and the additional evidence it would require.

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
The measure $\mu$ is independent of the chosen settings. Equation (1) declares both setting independence and local factorization. Stochastic responses are allowed. No extra assumption that the responses were initially deterministic is required. Conditioning on selected detection events would define a different statistical model and requires its own justification.

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
Every positive mixture therefore satisfies $|S(p)|\le2$. This is the CHSH inequality [2]. Other output and setting relabelings give the remaining CHSH inequalities. Fine's theorem connects the complete family, under the requisite consistency of the specified marginals, to a joint distribution in this scenario [3]. Our general arguments below use the full polytope (2), not just one inequality.

For an explicit quantum violation, use $|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2$ and
$$
A_0=Z,\quad A_1=X,\quad
B_0=(Z+X)/\sqrt2,\quad B_1=(Z-X)/\sqrt2.
$$
The four correlators are $(1,1,1,-1)/\sqrt2$, so $S=2\sqrt2>2$. The associated outcome distributions are positive and no-signalling but have no positive extension over $\Omega$.

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
\left(\langle c,p\rangle-max_{\ell\in\mathcal L}\langle c,\ell\rangle\right).
\tag{6}
$$

**Proof.** For every local $\ell$, $B_c(p)-\beta_c\le\langle c,p-\ell\rangle\le L_\pi(c)\|p-\ell\|_\pi$, proving (5). For (6), norm duality expresses $\|p-\ell\|_\pi$ as $\max_{L_\pi(c)\le1}\langle c,p-\ell\rangle$. The two feasible sets are compact convex sets in finite dimensions and the pairing is bilinear, so the finite-dimensional minimax theorem interchanges minimum and maximum. $\square$

Equation (6) identifies the optimized residual with a normalized separating witness. Coefficients constant within a context pair to zero with normalized behavior differences, so shifting such constants can improve the bound (5). The displayed $L_\pi$ is the full-space dual norm and is always valid.

For uniform settings in CHSH, $\pi_{xy}=1/4$ and $c_{abxy}=ab(-1)^{xy}$, giving $L_\pi(c)=8$. Applying both signs yields
$$
R_\pi(p)\ge\frac{[|S(p)|-2]_+}{8}.
\tag{7}
$$

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
Then $\mathcal B^2=4I-[A_0,A_1]\otimes[B_0,B_1]$, and each commutator has operator norm at most two. Thus $\|\mathcal B\|_\infty\le2\sqrt2$. The same bound holds for dichotomic POVMs by local dilation. Mixing the displayed maximally entangled state with white noise realizes every $0\le v\le1/\sqrt2$. The endpoint $v=1$ is a PR behavior, useful here as a no-signalling comparison, not a quantum state.

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
has the required marginals. This is an explicit instance of the signed-extension/no-signalling connection in [4]. Higher unobserved moments may be added; the displayed extension is not generally the one of least negative mass.

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

At the quantum endpoint, the repair cost is approximately $0.103553$, and the minimum negative mass is approximately $0.207107$. Equation (14) is a family-specific identity; it is not asserted for general scenarios. Neither quantity is defined here as the contextual fraction, which is a separate convex-decomposition measure [7].

# 6 Connecting state residuals to Bell residuals

## 6.1 Measurement contraction and convexification

Let $\mathrm{Sep}$ be the convex set of separable density matrices on the declared bipartite Hilbert space. For fixed local POVMs, $\mathcal M(\mathrm{Sep})\subseteq\mathcal L$: apply the local response construction of Section 2 to each product term of a separable mixture. Equality need not hold for fixed observables and dimensions.

**Theorem 7 (State-to-behavior bound).** For every state $\rho$,
$$
R_\pi(\mathcal M(\rho))
\le\frac12\inf_{\sigma\in\mathrm{Sep}}\|\rho-\sigma\|_1
\le\frac12D_{\rm prod}(\rho).
\tag{15}
$$

**Proof.** For any fixed setting pair, a POVM maps states to probability distributions with total-variation distance at most half their trace-norm distance. Explicitly, for Hermitian $Z$, write $Z=Z_+-Z_-$. Positivity of the POVM effects bounds the sum of absolute outcome traces by $\operatorname{Tr}(Z_++Z_-)=\|Z\|_1$. Averaging over $\pi$ preserves this bound. For each separable $\sigma$, $\mathcal M(\sigma)$ is an admissible local comparison behavior. Minimize over $\sigma$, then choose $\sigma=\rho_A\otimes\rho_B$. $\square$

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

# 9 Presentation families and task relevant projection loss

## 9.1 A carrier need not be an ontological background

The dialogue [P3] asks whether the same mathematics can be used without treating a brain, a body, or a Hilbert space as an observer-independent starting point. For the finite inference results, it can. Declare a set $\mathcal H$ of admissible histories or candidate situations and a family of presentations
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

An observer can therefore discard extensive information while remaining sufficient for a particular task. Non-injectivity alone is not a prediction obstruction. The obstruction is variation of the target along an unresolved fiber. Equation (25) is a finite scalar minimax statement; vector-valued targets require their actual feasible prediction sets and metric radii, not independent scalar midpoints.

This is the discrete counterpart of the phase-fiber prediction analysis in [P1, Sections 7.5 and 7.6]. As an exact two-state example, take
$$
|+\rangle=(|0\rangle+|1\rangle)/\sqrt2,\qquad
|-\rangle=(|0\rangle-|1\rangle)/\sqrt2.
$$
The observation retaining only computational-basis populations reports $(1/2,1/2)$ for both. After a Hadamard transformation, the probability of output $0$ is respectively $1$ and $0$. The best scalar predictor from those populations alone has worst-case error $1/2$. This is a prediction ambiguity, not a Bell violation. An independently available $X$-expectation report separates the two states. An actual quantum measurement protocol must still specify state preparation and available copies; formal statistics are not automatically simultaneous single-shot measurements.

## 9.3 Why serial language is not intrinsically low dimensional

A finite graph, a matrix, or a collection of noncommuting operator rules can be encoded injectively as a finite string. Ordering the symbols does not force the encoded objects to commute, erase graph cycles, or factorize the represented distribution. A transcript's one-dimensional order is not the dimension of its semantic state space. Shannon's communication model distinguishes the message set from its encoding and channel [9].

A concrete capacity obstruction requires a budget. If a message uses at most $b$ binary digits in a fixed-length code, it has at most $2^b$ values. Exact reconstruction of $N>2^b$ distinguishable states is then impossible by the pigeonhole principle. For task prediction, the relevant number is the number of task distinctions that must survive. Even when state reconstruction is impossible, exact prediction of a constant or otherwise sufficiently compressed target can remain possible.

Thus the strongest defensible version of the dialogue's language argument is conditional: a particular encoding, finite context, measurement interface, or summary may merge histories that matter for the task. Increasing the length, using a more suitable code, or retaining additional data can change those fibers. The mere fact that a model emits successive tokens establishes none of the required losses.

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

**Proposition 9 (Linear visibility criterion).** There is a finite constant $C$ such that $\|Gv\|\le C\|Ov\|$ for every $v\in V$ if and only if $\ker O\subseteq\ker G$.

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

# 11 Narrative and experience as proposed applications

## 11.1 Narrative as a task dependent presentation

The dialogue [P3] proposes that a first-person account such as a description of breakfast selects a manageable trajectory from a much richer relational situation. As a modelling hypothesis, this can be expressed by a narrative report $O_{\rm nar}(h)$ and a family of nonverbal readouts or later responses. The mathematically testable question is whether those targets are constant on narrative fibers.

It is unnecessary to assume at the outset that an anatomical brain is the uniquely privileged carrier. One can begin with relations among reports, interventions, and later observations. A neural, bodily, or environmental model can then be an explicitly proposed realization of those relations. This respects the dialogue's presentation-relative intent while leaving empirical adjudication possible.

However, grammatical categories such as subject, object, and time do not define tensor factors, and a sentence is not thereby a product density matrix. To use $\Pi_{\rm prod}$ rather than a generic observation map requires an actual factorization model and evidence that the proposed retraction captures the relevant reduction. The loss of an unchosen alternative is a possible property of a report, not a theorem about all language.

## 11.2 Residual registration is not yet an account of qualia

The proposal that qualia are the internally registered part of a projection residual can guide a research question, but the equations in [P1, P2] do not establish that identity. Many elementary physical and computational systems have nonzero projection residuals. The existence of such a residual does not by itself identify which systems have experience or what that experience is like.

A proposed model would need a declared presentation map, independently specified targets or indicators, and predictions that distinguish it from alternative explanations. For instance, one could test whether a particular summary is insufficient to predict later reports or actions and whether an additional relational statistic reduces that error. Such a result would support a claim about predictive information. Identifying the statistic with subjective experience would remain a further theoretical step.

If a person can notice that their verbal account omits something, that noticing is itself an additional report. In the present formalism it may refine the observer family; it is not proof that the original kernel has been inverted. Similarly, humor, metaphor, and shifts of perspective may reveal distinctions or reorganize known information, but contradictions between descriptions do not uniquely reconstruct a hidden higher-dimensional object.

## 11.3 No consciousness threshold follows from the quoted dynamics

The dialogue suggests transferring connected-cumulant onset, graph disconnection, and dephasing formulas to consciousness. Several mathematical qualifications are necessary even before any biological identification is attempted.

First, a Taylor onset order $j\ge\tau_G(S)$ is not a strictly positive waiting time. A nonzero leading term $a t^j$ is nonzero at arbitrarily small positive $t$. Second, setting an edge coupling to zero can split a specified interaction tree and suppress the connected cumulants spanning its components under the stated product-initialization and dynamical assumptions. That conclusion is about the model, not a general diagnostic for loss of experience. Third, an exponential factor $e^{-2\gamma t}$ is strictly positive for finite $\gamma,t$; its decay supplies no exact finite phase-transition threshold. A practical detection threshold must be declared separately.

The supplied papers do not provide a validated mapping from these operators to anaesthesia, sleep, trauma, or subjective awareness. No clinical claim or consciousness biomarker is inferred here. The productive proposal is to specify and test a presentation-dependent predictive model, rather than labeling a mathematical residual as an established mechanism of consciousness.

## 11.4 Higher cells and existential closure

The dialogue's interpretation of religion as an attempt to close an unresolved cycle is a philosophical analogy. It can express the search for a wider account of otherwise incompatible commitments without serving as proof of a theological or anti-theological conclusion.

There is also a precise algebraic correction. Attaching a 2-cell to a cycle can make the first cohomology group of the enlarged complex vanish, but it does not change a fixed edge assignment into a vertex coboundary. The map $d_0$ and its image remain unchanged if the vertices and edges are unchanged. A former cycle cochain with nonzero circulation instead has $d_1\omega\ne0$ on the new face and ceases to be closed. Its obstruction has not been erased from the data; its location in the description has changed. This is the same distinction illustrated by the filled-triangle calculation in [P2].

Nor does the existence of a graph cycle force a particular cochain to have a nonzero class: the zero cochain and every coboundary remain exact. A higher presentation earns explanatory value by preserving observations, accounting for additional structure, and supporting successful tests. Neither a richer diagram nor a residual by itself supplies that validation.

# 12 Finite verification and empirical use

Equation (3) is a linear program. Introduce nonnegative variables $q_\lambda,u_{abxy}$ and solve
$$
\begin{aligned}
\text{minimize}\quad &\frac12\sum_{xy}\pi_{xy}\sum_{ab}u_{abxy},\\
\text{subject to}\quad &-u\le p-Tq\le u,\qquad
q\ge0,\qquad \sum_\lambda q_\lambda=1.
\end{aligned}
\tag{29}
$$
The negative-mass problem is also linear: write $q=q^+-q^-$, impose $q^\pm\ge0$, $T(q^+-q^-)=p$, $\sum(q^+-q^-)=1$, and minimize $\sum q^-$. Enumeration grows exponentially with the number of local measurements; finite formulation does not imply scalability to arbitrary scenarios.

The reproducible code in Appendix A checks the sixteen-assignment CHSH calculation using exact rational arithmetic, verifies the positive boundary extension, and independently solves the two linear programs for selected values of $v$. It checks the observer-fiber and recursion examples and also checks the two-qubit trace norms and CHSH values and the three-party Mermin witness by floating-point matrix calculations. Exact rational checks establish the specified finite identities. Floating-point optimization and matrix checks are consistency tests, not substitutes for the proofs or certified interval computations. No Lean formalization or experimental Bell test is claimed for this draft.

For empirical data $\widehat p$, if a statistical procedure supplies the confidence statement $\|p-\widehat p\|_\pi\le\varepsilon$, then (4) gives
$$
R_\pi(p)\ge[R_\pi(\widehat p)-\varepsilon]_+.
\tag{30}
$$
The confidence level and assumptions belong to that statistical procedure. Finite samples can show apparent signalling; a distance from $\widehat p$ to $\mathcal L$ may then include both sampling inconsistency and Bell nonlocality. The four-context probability model, trial selection, and setting assumptions must be stated before interpreting a numerical residual. Equation (30) is a stability statement, not a complete experimental analysis.

# 13 Interpretation and scope

The projection viewpoint gives a precise answer to what remains after a local classical explanation has been made as accurate as possible: a residual probability table, and a dual Bell functional that detects its unavoidable part. Every positive local hidden-variable model lies in the target polytope. A nonzero residual therefore records failure of that entire model class, rather than failure of one insufficiently expressive choice of hidden variable.

This formulation connects naturally to [P1, P2], but the targets of reduction must remain explicit. State product retraction removes even shared classical correlations. Bell-local convex repair retains them. Overlap coboundaries test marginal agreement. Support cohomology can detect parity contradictions. Positive-extension feasibility tests the probability weights as well. These are related constructions with distinct kernels and distinct witnesses.

No-signalling survives the quantum example, so the residual does not by itself describe a controllable superluminal signal. It also does not select a unique ontology, derive the Born rule, or show that an inaccessible higher-dimensional local classical distribution restores Bell locality. Such a distribution, if it obeyed (1), would still induce a positive extension and would still satisfy CHSH. What the paper establishes is a representation theorem and quantitative obstruction, conditional on the explicitly stated Bell assumptions and the quantum measurement model used in its examples.

The Bell-specific next mathematical problem is to study when the measured state velocity exits the local tangent cone, and how higher-order state dynamics control that exit. Equations (9), (15), and (18) identify the ingredients: the measurement map, the feasible local cone, an oriented witness, and a controlled remainder. They make the connection to projection dynamics concrete while leaving the positive-extension content of Bell's theorem intact.

For RSI, the corresponding problem is to design updates that expose and reduce task-relevant fiber width. A system can improve its computation within its existing evidence, and it can improve the evidence through informative interaction. Those are distinct sources of progress. Theorem 10 rules out guaranteed recovery across an unresolved distinction; it does not rule out progress, powerful artificial intelligence, or empirically successful self-improvement. The conceptual extension to narrative and experience remains an invitation to construct and test presentation maps, not an established identification of qualia with a norm or a cohomology class.

# References

**[P1]** J. H. Carroll. *Projection Obstruction for Factorized States: Nonlinear Dynamics, Conditional $\ell^1$ Diagnostics, and Exact Short-Time Defect Bounds*. Supplied manuscript, version 6.9.18, dated 14 October 2026. Source file: `projection_obstruction(20261021-095018).md`. The present paper uses its product-retraction definitions, distinction between compatible marginal sections and correlation residuals, two-site Taylor estimate, and residual/cochain taxonomy. Referenced companion packages were not supplied and are not treated as verified dependencies.

**[P2]** J. H. Carroll. *Higher-Cell Product Retractions, Simplicial Cochains, and Finite Retraction Dynamics*. Supplied manuscript, version 0.1.0, dated 10 October 2026. Source file: `034_higher_cell_cochain_projection_and_retraction_dynamics(1).md`. The present paper uses its affine derivative, $Q$ versus $R_k$ distinction, finite-Hamiltonian remainder estimate, and requirement for an explicit observation map. Its own software and formalization status are not inherited by this draft.

**[P3]** Supplied conceptual dialogue on projection loss, first-person narrative, consciousness, RSI/ASI, and higher-cell closure. Source file: `Pasted text(20261021-095549).txt`, provided 21 October 2026. Used as the source of the interpretive questions developed in Sections 9-11, not as evidence that its proposed physical or cognitive identifications have been established.

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

**Preparation note.** This draft was prepared with AI assistance from the two supplied manuscripts, the supplied conceptual dialogue, and the cited primary literature. Its self-contained arguments and accompanying calculations are offered for author and independent review. No publication, external peer review, or formal proof-assistant certification is asserted.


# Appendix A Reproducible finite checks

The following Python code is included directly so that this Markdown file is a self-contained manuscript and verification record. It uses the standard library plus NumPy and SciPy. Run the code block as a Python script. The checks were executed during preparation on 21 October 2026 with NumPy 2.3.5 and SciPy 1.17.0.

Five rational CHSH parameters were checked exactly. Fourteen floating-point linear programs, covering seven parameters and two objectives, agreed with the closed forms to a maximum absolute difference of approximately $1.12\times10^{-16}$. The two-qubit calculations agreed to approximately $8.89\times10^{-16}$. All 64 deterministic Mermin assignments and the stated finite prediction checks passed. These are finite checks of the displayed examples; the general statements rely on their proofs above.

```python
from fractions import Fraction as F
from itertools import product
import json
import numpy as np
from scipy.optimize import linprog

# CHSH row order: x, y, a, b. Assignment order: a0, a1, b0, b1.
signs = (-1, 1)
assignments = list(product(signs, repeat=4))
rows = list(product(range(2), range(2), signs, signs))
K = [a0*(b0+b1)+a1*(b0-b1) for a0,a1,b0,b1 in assignments]
assert K.count(2) == K.count(-2) == 8
T = np.array([[int(l[x] == a and l[2+y] == b) for l in assignments]
              for x,y,a,b in rows], dtype=float)
coeff = np.array([a*b*(-1)**(x*y) for x,y,a,b in rows], dtype=float)
exact_rows = []
for v in (F(0), F(1,4), F(1,2), F(3,4), F(1)):
    q = [(1+v*k)/16 for k in K]
    p = [(1+v*a*b*(-1)**(x*y))/4 for x,y,a,b in rows]
    assert sum(q) == 1
    for i, (x,y,a,b) in enumerate(rows):
        assert sum(w for l,w in zip(assignments,q)
                   if l[x] == a and l[2+y] == b) == p[i]
    assert sum(F(int(c))*u for c,u in zip(coeff,p)) == 4*v
    assert sum(-w for w in q if w < 0) == max(F(0), v-F(1,2))
    if v <= F(1,2):
        assert all(w >= 0 for w in q)
    else:
        boundary = [(1+F(1,2)*a*b*(-1)**(x*y))/4 for x,y,a,b in rows]
        cost = sum(abs(u-w) for u,w in zip(p,boundary))/8
        assert cost == (2*v-1)/4
    exact_rows.append(str(v))

# Independent linear programs for behavioral distance and negative mass.
I = np.eye(16)
Aub = np.block([[-T,-I],[T,-I]])
Aeq = np.r_[np.ones(16), np.zeros(16)][None,:]
errors = []
for v in (0., .25, .5, .6, 1/np.sqrt(2), .75, 1.):
    p = (1+v*coeff)/4
    res = linprog(np.r_[np.zeros(16),np.ones(16)/8],
                  A_ub=Aub, b_ub=np.r_[-p,p],
                  A_eq=Aeq, b_eq=[1], bounds=(0,None), method='highs')
    assert res.success
    err = abs(res.fun-max(0.,(2*v-1)/4))
    errors.append(err)
    assert err < 1e-9
    Aneg = np.vstack([np.c_[T,-T],np.r_[np.ones(16),-np.ones(16)]])
    neg = linprog(np.r_[np.zeros(16),np.ones(16)],
                  A_eq=Aneg, b_eq=np.r_[p,1.],
                  bounds=(0,None), method='highs')
    assert neg.success
    err = abs(neg.fun-max(0.,v-.5))
    errors.append(err)
    assert err < 1e-9

X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.diag([1.,-1.]).astype(complex)
H = np.array([[1,1],[1,-1]], dtype=complex)/np.sqrt(2)
def trace_norm(a):
    return float(np.abs(np.linalg.eigvalsh(a)).sum())
def density(v):
    return np.outer(v, v.conj())
def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

# Independently evaluate state residuals and chosen optimal CHSH observables.
state_errors = []
for t in (.001, .07, .2, np.pi/8, np.pi/4):
    u,w = np.cos(t),np.sin(t)
    psi = np.array([u,0,0,-1j*w])
    rho = density(psi)
    reduced = np.diag([u*u,w*w])
    c = abs(np.sin(2*t))
    err = abs(trace_norm(rho-np.kron(reduced,reduced))-(c+c*c/2))
    state_errors.append(err)
    assert err < 1e-12
    schmidt = density(np.array([u,0,0,w], dtype=complex))
    b0,b1 = (Z+c*X)/np.sqrt(1+c*c),(Z-c*X)/np.sqrt(1+c*c)
    B = np.kron(Z,b0+b1)+np.kron(X,b0-b1)
    err = abs(np.trace(B@schmidt).real-2*np.sqrt(1+c*c))
    state_errors.append(err)
    assert err < 1e-12

# Three-party witness and classical control.
mermin_values = []
for xa,ya,xb,yb,xc,yc in product(signs,repeat=6):
    mermin_values.append(xa*xb*xc-xa*yb*yc-ya*xb*yc-ya*yb*xc)
assert set(mermin_values) == {-2,2}
ghz = np.zeros(8, dtype=complex)
ghz[0] = ghz[7] = 1/np.sqrt(2)
Bg = kron3(X,X,X)-kron3(X,Y,Y)-kron3(Y,X,Y)-kron3(Y,Y,X)
rhog = density(ghz)
classical = np.diag([.5,0,0,0,0,0,0,.5])
assert np.isclose(np.trace(Bg@rhog),4)
assert np.isclose(np.trace(Bg@classical),0)
assert np.isclose(trace_norm(rhog-np.eye(8)/8),7/4)
assert np.isclose(trace_norm(classical-np.eye(8)/8),3/2)

# Equal-population states with opposite future output probabilities.
plus = np.array([1,1],dtype=complex)/np.sqrt(2)
minus = np.array([1,-1],dtype=complex)/np.sqrt(2)
assert np.allclose(abs(plus)**2,abs(minus)**2)
assert np.isclose(abs((H@plus)[0])**2,1)
assert np.isclose(abs((H@minus)[0])**2,0)

# Exact fiber widths and a finite version of the recursion lower bound.
histories = list(product((0,1),repeat=2))
f = lambda h: F(h[0]+2*h[1])
for report in (0,1):
    values = [f(h) for h in histories if h[0] == report]
    lo,hi = min(values),max(values)
    assert (hi-lo)/2 == 1
    midpoint = (hi+lo)/2
    assert max(abs(z-midpoint) for z in values) == 1
    for guess in (F(k,4) for k in range(-8,21)):
        assert abs(guess-lo)+abs(guess-hi) >= hi-lo
# Observing both coordinates makes every fiber a singleton.
assert len(set(histories)) == len(histories)

print(json.dumps({
    'status':'passed',
    'exact_CHSH_parameters':exact_rows,
    'floating_LP_parameters':7,
    'max_LP_absolute_error':max(errors),
    'two_qubit_times_checked':5,
    'max_state_absolute_error':max(state_errors),
    'Mermin_assignments_checked':len(mermin_values),
    'phase_fiber_and_finite_inference_checks':'passed'
},indent=2))
```
