<div align="center"># Conditional density lifts and a primal–dual alignment statistic</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">2026-10-23</div>
<div align="center">Version 2.0.5</div>

## Abstract

A nonzero real vector can be mapped to a unit vector by taking signed square
roots of its normalized absolute coordinates. The associated rank-one projector
retains relative magnitudes and signs while forgetting total mass and common
sign. We apply this construction to an optimal residual and an optimal dual
witness for a finite-dimensional minimum-distance problem in the sum norm.
Their trace distance defines an alignment statistic. Complementary slackness
gives a strict upper bound below one for every optimal pair, and characterizes
the zero-distance case. Successive coordinate minimization selects a unique
pair once a coordinate order is fixed. The construction is undefined at a zero
residual; a separate convention assigns the statistic the value zero there.
We give proofs, an explicit example, and a selection policy that uses the
statistic only after primary residual comparisons. The accompanying numerical
implementation and discrete Lean results have distinct, stated scopes.

## 1. Problem and relation to existing methods

Let $B:\mathbb R^n\to\mathbb R^m$ be a fixed linear map, with $m\ge1$, and
let $\omega\in\mathbb R^m$. Define

$$
\Phi(\omega)=\min_{a\in\mathbb R^n}\|\omega-Ba\|_1.
$$

For a graph, $B$ may be its vertex-to-edge incidence map. The minimum is a norm
on the quotient by $\operatorname{im}B$ and a seminorm on the original vector
space. Linear programming supplies optimality and duality statements [1].
The finite-dimensional projector distance used below is standard [2]. The
contribution here is the specified combination of these constructions and its
primal–dual bound, rather than a new duality or trace-distance theorem.

## 2. The signed square-root map

For $v\ne0$, put $M(v)=\sum_i|v_i|$ and

$$
\psi(v)_i=\operatorname{sgn}(v_i)\sqrt{|v_i|/M(v)},\qquad
\rho(v)=\psi(v)\psi(v)^T.
$$

The sign at zero is immaterial because that coordinate of $\psi$ is zero.
We use $\operatorname{sgn}(0)=1$ in the implementation.

**Proposition 2.1.** The matrix $\rho(v)$ is positive semidefinite, has trace
one and rank one, and satisfies $\rho(v)^2=\rho(v)$. For $c>0$,
$\rho(cv)=\rho(v)=\rho(-v)$.

**Proof.** The squared Euclidean norm of $\psi(v)$ is
$\sum_i|v_i|/M(v)=1$. Thus $x^T\rho(v)x=(x^T\psi(v))^2\ge0$,
the trace is one, and multiplication of the two outer products gives
$\rho(v)^2=\psi(v)(\psi(v)^T\psi(v))\psi(v)^T=\rho(v)$.
Positive scaling cancels in the normalized weights; negation changes the unit
vector's common sign and leaves its outer product unchanged.

For real unit vectors $u,v$, the trace norm gives

$$
\frac12\|uu^T-vv^T\|_{\mathrm{tr}}
 =\sqrt{1-|u^Tv|^2}.
$$

Indeed, outside their span the difference is zero. On their span it has trace
zero and eigenvalues $\pm\sqrt{1-|u^Tv|^2}$, with the coincident-ray case
obtained directly. This is a finite matrix identity, with no physical
interpretation assumed.

## 3. Selecting an optimal pair

The residual and dual optimal sets are

$$
H^*(\omega)=\{h\in\omega-\operatorname{im}B:\|h\|_1=\Phi(\omega)\},
$$

$$
W^*(\omega)=\{\varphi:\|\varphi\|_\infty\le1,\ B^T\varphi=0,
\ \varphi^T\omega=\Phi(\omega)\}.
$$

Both sets are nonempty and compact. For the primal, the affine residual space
is closed and its intersection with any sufficiently large norm ball is
compact; a continuous norm attains its minimum there. The dual feasible set is
compact, and finite-dimensional norm duality gives the stated equality of
optimal values [1]. An optimal potential need not be unique, but its residual
belongs to $H^*$.

Fix a coordinate order $1,\ldots,m$. On either optimal set, minimize the first
coordinate, then the second on the remaining minimizers, and continue. Each
stage is nonempty and compact. At the last stage all coordinates are fixed,
so the remaining set contains exactly one vector. Denote the resulting pair
by $(h^*,\varphi^*)$. It is unique relative to the declared coordinate order;
it is not invariant under an arbitrary change of that convention.

Support-first minimization is not a substitute for this construction. On two
disjoint directed triangles, a residual class can have optimal set

$$
\{h\ge0:h_1+h_2+h_3=1,\ h_4+h_5+h_6=1\}.
$$

Its lexicographically first possible sorted support is $(1,2,3,4)$. Within
that support, the first coordinate has infimum zero without attaining it:
$h=(t,(1-t)/2,(1-t)/2,1,0,0)$ for $0<t<1$. The stratum is not closed.

## 4. Alignment and its bounds

When $\Phi(\omega)>0$, define

$$
\Xi(\omega)=\frac12\|\rho(h^*)-\rho(\varphi^*)\|_{\mathrm{tr}}.
$$

When $\Phi(\omega)=0$, define $\Xi(\omega)=0$ separately. This value is a
convention: the density lift of the zero residual does not exist.

**Theorem 4.1.** For any optimal primal–dual pair $(h,\varphi)$ with
$\Phi>0$ and $N=\|\varphi\|_1$,

$$
1\le N\le m,\qquad
0\le\frac12\|\rho(h)-\rho(\varphi)\|_{\mathrm{tr}}
\le\sqrt{1-1/N}\le\sqrt{1-1/m}<1.
$$

**Proof.** Dual feasibility and optimality imply
$\varphi^Th=\varphi^T\omega=\|h\|_1$. Each summand
$|h_i|-\varphi_i h_i$ is nonnegative, so it is zero. Thus
$\varphi_i=\operatorname{sgn}(h_i)$ whenever $h_i\ne0$. In particular
$\|\varphi\|_\infty=1$, whence $1\le N\le m$. Consequently

$$
\langle\psi(h),\psi(\varphi)\rangle
=\frac{\sum_{h_i\ne0}\sqrt{|h_i|}}{\sqrt{\Phi N}}
\ge\frac{\sqrt{\sum_i|h_i|}}{\sqrt{\Phi N}}
=\frac1{\sqrt N}.
$$

The trace-distance identity gives the result.

**Corollary 4.2.** The distance is zero exactly when the two supports coincide
and $|h_i|=\Phi/N$ on that support. Their signs then agree automatically.

**Proof.** Zero distance means equal rank-one projectors, hence equal unit
vectors up to a common sign. Their overlap is positive by Theorem 4.1, so the
common sign is positive. Comparing their squared coordinates gives
$|h_i|/\Phi=|\varphi_i|/N$. On the primal support, $|\varphi_i|=1$;
outside it equality requires $\varphi_i=0$. The converse follows by substitution.

## 5. Worked example and a selection policy

On a directed triangle take $h=(2,1,1)$ and $\varphi=(1,1,1)$.
Their pairing and primal mass are both four, and the circulation constraint
$B^T\varphi=0$ holds. These are an optimal pair for the class of $h$.
Here $N=3$ and

$$
\langle\psi(h),\psi(\varphi)\rangle=\frac{1+\sqrt2}{\sqrt6},\qquad
\Xi=\sqrt{\frac{3-2\sqrt2}{6}}>0.
$$

This pair illustrates why sign and support agreement alone do not imply zero
distance. It need not be the pair selected by coordinate minimization.

One possible decision policy compares tuples $(\Phi,\Gamma,R,\Xi)$ with a
resolution $\epsilon>0$. It accepts a candidate if one of these conditions holds:

1. $\Phi'<\Phi-\epsilon$.
2. $\Phi-\epsilon\le\Phi'\le\Phi$ and $\Gamma'<\Gamma-\epsilon$.
3. $\Phi-\epsilon\le\Phi'\le\Phi$, $\Gamma-\epsilon\le\Gamma'\le\Gamma$,
   $R'\le R_{\max}$ and $\Xi'<\Xi-\epsilon$.

This policy never increases the primary coordinate. The ratio condition is
applied only in the third branch; primary or secondary improvement can be
accepted without it. This is the specified behavior, rather than a general
feasibility or convergence result. All tuple entries must be computed or
validated for their stated mathematical roles before interpreting a decision.

## 6. Implementation and formal scope

The Python module `code/mod_conditional_density_lift_core.py` implements the
numerical square-root lift and trace distance. Its numerical function accepts
supplied vectors; it does not certify their optimality or perform the successive
coordinate selector. The linear-program examples use floating-point optimization
and cannot serve as exact certificates merely because a solver reports success.
The explicit unverified-override option is outside the mathematical definition.

An optional zero-obstruction certificate is bound to the supplied cochain and
checks its coboundary equality over the exact rational values represented by
the finite binary inputs. A numerical near-equality does not certify an exact
zero class. The numerical lift refuses inputs whose total mass cannot be stored
as a finite floating-point number, rather than returning a clipped mass.

The module also contains exact integer/rational checks for normalized absolute
weights, the Cauchy inequality, complementary slackness and rational decision
comparisons. `lean4/Xi.lean` formalizes corresponding discrete statements.
The real rank-one matrix construction, compactness argument and square-root
bound above are prose proofs, not results of the discrete Lean development.
The supplied census lists the declarations audited by the pinned compiler.

## 7. Limitations

The statistic depends on a selected optimal pair and a coordinate convention.
It discards total residual mass and cannot replace the quotient residual as a
measure of that mass. Its definition at zero is separate from the density formula.
A small statistic does not imply feasibility, convergence, or preservation of
constraints. The finite matrix encoding does not derive quantum mechanics or
any law of physical measurement.

## References

1. S. Boyd and L. Vandenberghe, *Convex Optimization*, Cambridge University Press,
   2004, Chapters 4–5. [Author-hosted book](https://web.stanford.edu/~boyd/cvxbook/).
2. J. Watrous, *The Theory of Quantum Information*, Cambridge University Press,
   2018, Chapter 3. [Author-hosted text and chapters](https://cs.uwaterloo.ca/~watrous/TQI/).
