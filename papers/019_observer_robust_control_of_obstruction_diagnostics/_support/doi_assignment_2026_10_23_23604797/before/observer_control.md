<div align="center"># Observer-relative control of cochain residuals</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">2026-10-23</div>
<div align="center">Version 2.1.3</div>

## Abstract

We study finite candidate-selection policies constrained by several coordinate
observers. Each observer specifies a projection, positive weights, a space of
removable differences and a closure map. The policy bounds the observer-relative
quotient residual, the closure residual and their ratio. We distinguish two
coordinate estimates: a weighted norm bounds the coordinates of its input,
whereas a quotient seminorm bounds coordinates only of a selected minimizing
residual. Complete coordinate coverage does not remove this distinction.
A one-edge example has zero quotient residual and arbitrarily large raw
coordinates, even with complete observation. We give the corrected estimates,
counterexamples to stronger transfer claims and a finite ranking rule. The
supplied Lean development treats integer weighted norms; a numerical reference
implementation additionally evaluates projected quotient problems.

## 1. Introduction

Several observation maps can impose simultaneous constraints on a proposed
repair. Such constraints are relative to the declared maps: they do not establish
stability under all possible measurements or transformations. The mathematical
question is what these inequalities actually control.

Finite-dimensional quotient norms and linear-program duality are standard [1].
The cochain condition used for closure residuals is standard as well [2]. Our
purpose is to specify a policy and identify the distinction between coordinate
coverage, residual bounds and bounds on the original field. In particular, a
bound on distance to a subspace is not a bound on the vector itself.

## 2. Observer data and diagnostics

Let $\omega\in\mathbb R^m$ and let $\mathcal O$ be a finite nonempty family
of observers. Observer $o$ selects a coordinate set $I_o$, with coordinate
restriction $\pi_o$, positive weights $w_{o,k}$ on those coordinates, a linear
map $B_o$ into the observed coordinate space, and a linear closure map $D_o$.
Assume $D_oB_o=0$. Choose positive face weights $v_{o,j}$ when that space is nonzero.

Define

$$
\Phi_o(\omega)=\min_a\sum_{k\in I_o}w_{o,k}
 |(\pi_o\omega-B_oa)_k|,
\qquad
\Gamma_o(\omega)=\sum_jv_{o,j}|(D_o\pi_o\omega)_j|.
$$

The first minimum is attained because the image of $B_o$ is a closed subspace
of a finite-dimensional normed space. Write $r_o(\omega)=\pi_o\omega-B_oa_o^*$
for a selected minimizing residual. The closure residual is unchanged by
subtracting $B_oa_o^*$.

The family has complete coordinate coverage if $\bigcup_o I_o=\{1,\ldots,m\}$.
This is a condition on the coordinate restrictions. For arbitrary linear
projections, a positivity statement about coordinate weights is not a substitute
for checking the common kernel of the observation maps.

## 3. A finite-observer policy

Fix nonnegative tolerances $\epsilon_o$, positive ceilings $M$ and $R$, and
nonnegative closure limits $G$ and $\delta$. For a candidate $\omega'$ require,
for every observer,

$$
\Phi_o(\omega')\le\Phi_o(\omega)+\epsilon_o,\qquad
\Phi_o(\omega')\le M,
$$

$$
\Gamma_o(\omega')\le\Gamma_o(\omega)+\delta,\qquad
\Gamma_o(\omega')\le G.
$$

We also specify a resolution-dependent ratio

$$
R_o(\omega')=
\begin{cases}
\Gamma_o(\omega')/\Phi_o(\omega'),&\Phi_o(\omega')>\epsilon_o,\\
0,&\Phi_o(\omega')\le\epsilon_o\ \text{and}\ \Gamma_o(\omega')\le\epsilon_o,\\
+\infty,&\Phi_o(\omega')\le\epsilon_o<\Gamma_o(\omega'),
\end{cases}
$$

and require $R_o(\omega')\le R$. This is a policy definition. Its middle
branch can differ from the exact positive-denominator ratio: for
$\Phi=1/4000$, $\Gamma=1/2000$ and $\epsilon=1/1000$, it is zero although
$\Gamma/\Phi=2$. Thus this test alone does not establish an exact ratio ceiling.

After $T$ transitions satisfying the first inequality,

$$
\Phi_o(\omega_T)\le\Phi_o(\omega_0)+
\sum_{t=0}^{T-1}\epsilon_{o,t}.
$$

This follows by summing the step inequalities. A fixed positive tolerance gives
a possible increase proportional to $T$, rather than a uniform infinite-time
bound. A uniform bound requires the explicit ceiling or a bounded cumulative
tolerance. Strict non-increase is obtained by setting each tolerance to zero.

## 4. Coordinate estimates and their limits

**Proposition 4.1: minimizing residuals.** If the quotient-residual comparison
in Section 3 holds, then for each observer and each of its observed coordinates,

$$
w_{o,k}|r_o(\omega')_k|
\le\Phi_o(\omega')\le\Phi_o(\omega)+\epsilon_o.
$$

**Proof.** The first term is one nonnegative summand in the weighted norm of
the minimizing residual. The second inequality is the assumed policy comparison.

The conclusion concerns $r_o(\omega')$, not $\pi_o\omega'$. Different observers
can select different minimizing residuals. Coordinate coverage alone does not
turn these observer-relative residuals into a single raw-coordinate bound.

**Counterexample 4.2: complete coverage with unbounded raw coordinates.**
Take one directed edge with $B=(-1,1)$, identity coordinate observation and
weight one. Every scalar field $\omega_t=(t)$ is $B(0,t)^T$, so

$$
\Phi(\omega_t)=0,\qquad \Gamma(\omega_t)=0
$$

when there are no faces. The observer covers the only coordinate. A transition
from zero to $\omega_t$ passes the residual comparisons and zero-ratio convention
for every $t$, while $|\omega_t|=|t|$ is arbitrarily large. The statement
$|\omega'_k|\le\Phi_o(\omega)+\epsilon_o$ is therefore false for quotient
residuals, even with complete coordinate coverage.

There is a valid raw-coordinate theorem for weighted norms. Define

$$
N_o(c)=\sum_{k\in I_o}w_{o,k}|c_k|.
$$

**Proposition 4.3: weighted input norms.** Suppose coverage is complete and
$N_o(c')\le N_o(c)+\epsilon_o$ for every observer. For every coordinate $k$
choose an observer with $k\in I_o$. Then

$$
w_{o,k}|c'_k|\le N_o(c)+\epsilon_o.
$$

**Proof.** The coordinate term is at most the full weighted input norm, which
is bounded by the assumed comparison. If $w_{o,k}\ge1$, the same budget bounds
$|c'_k|$. More generally divide by the specified positive weight.

This applies when no quotient minimization is performed, or when the supplied
vectors are explicitly the residuals to which the weighted norms apply. It does
not justify replacing $N_o$ by a quotient seminorm on arbitrary raw fields.

## 5. Transfer examples and candidate ranking

Complete coverage does not prohibit transfer between observed components. On
two disjoint cycle coordinates with weights $(2,1)$, changing $(1,0)$ to
$(0,1)$ reduces the weighted norm from two to one. Both coordinates are observed,
yet the defect changes location. To forbid that transfer, a policy must include
appropriate componentwise or partition constraints.

Coverage also matters for input norms. Observers that see only the first two
of three coordinates assign zero observed norm to $(0,0,K)$ for every $K$.
No bound on the third coordinate follows from those observations.

For a finite set of candidates that passed the specified tests, one possible
ranking score is

$$
L(o)=\max_{a\in\mathcal O}\Phi_a(\omega'_o)+
\frac{\lambda}{|\mathcal O|}\sum_{a\in\mathcal O}
 \bigl(S_{a,o}+R_a(\omega'_o)\bigr)+c_o,
$$

where $\lambda\ge0$, $c_o\ge0$ is a supplied cost, and $S_{a,o}\ge0$ is a
supplied constraint penalty. An implementation without a clause evaluator may
use $S_{a,o}=\min(\Phi_a(\omega'_o),1)$ as a surrogate; that surrogate is not
a count of violated clauses. Select a least-score candidate. An empty surviving
set produces no selection. These choices specify one algorithm, not an optimal
controller over an unspecified future trajectory.

## 6. Numerical and formal evidence

`code/mod_observer_robust_control_core.py` implements finite-observer comparisons
and a floating-point linear program when a matrix $B_o$ is supplied. This linear
program is a numerical computation, not an exact rational solver. The numerical
observer object checks matrix shapes but does not independently certify
$D_oB_o=0$; that identity is a hypothesis of the cochain interpretation and must
be checked separately for supplied matrices. The numerical
controller also permits its configured comparison margin on ratio and absolute
ceilings. To interpret those checks mathematically, use the corresponding
inflated ceilings or set the comparison margin to zero; the observer's residual
tolerance remains a separate parameter.

`lean4/ObserverRobustControlCore.lean` and `lean4/JointDetectorAdequacy.lean`
verify statements about integer vectors, natural-number weights and weighted
input norms. Their coordinate estimate instantiates Proposition 4.3, not a
raw-coordinate theorem for a quotient linear program. The zero-weight entries
in their finite examples represent omitted coordinates. The supplied census
records the actual declaration set and admitted kernel axioms.

The tests include the quotient/raw-coordinate counterexample and distinguish
numerical LP observations from exact arithmetic identities. A successful
finite test run does not establish statements about undeclared observers.

## 7. Discussion

The policy controls precisely the diagnostics it compares. Quotient residuals
ignore removable components; raw weighted norms do not. Complete coordinate
coverage helps obtain coordinate estimates for raw input norms, but it cannot
bound arbitrary components removed by quotient minimization. Neither condition
prevents all transfers, constraint deletion or divergence under an unbounded
cumulative tolerance. Those properties require additional hypotheses and checks.

## References

1. S. Boyd and L. Vandenberghe, *Convex Optimization*, Cambridge University Press,
   2004. [Author-hosted book](https://web.stanford.edu/~boyd/cvxbook/).
2. A. Hatcher, *Algebraic Topology*, Cambridge University Press, 2002, Section 3.1.
   [Author-hosted book](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html).
