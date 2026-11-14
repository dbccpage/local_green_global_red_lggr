<div align="center"># Candidate selection with residual and constraint diagnostics</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">2026-10-23</div>
<div align="center">Version 2.0.4</div>

## Abstract

We specify a finite candidate-selection rule using a quotient residual,
constraint violations, a closure residual, interface discrepancies and a
secondary alignment statistic. The quotient and closure residuals satisfy an
operator-norm inequality, so these channels are not algebraically independent.
Candidates must satisfy literal non-increase of the quotient residual and an
exact ratio ceiling before entering a two-stage tolerance ranking. A separate
inequality can screen representation-expanding proposals. We establish the
residual bound, explain the ranking rule and give counterexamples to stronger
interpretations: a ratio ceiling does not preserve constraints against deletion,
and greedy candidate selection does not establish convergence. The implementation
provides exact rational decision routines alongside a numerical interface.

## 1. Introduction

A repair proposal can improve one diagnostic while worsening another. A
selection rule must therefore state which comparisons are mandatory and which
are permitted trade-offs. The rule studied here is a finite filtering and
ranking procedure. Its acceptance conditions are definitions of a policy;
they are not theorems that selected proposals solve the underlying problem.
The geometric setup uses a finite cochain complex, while the optimization
ingredients are finite-dimensional norm minimization and ordered comparisons [1,2].

## 2. State variables and the residual inequality

Let $C^0\xrightarrow{B}C^1\xrightarrow{D}C^2$ be finite-dimensional real
coordinate spaces with $DB=0$. For a field $\omega\in C^1$, define

$$
\Phi(\omega)=\min_a\|\omega-Ba\|_1,\qquad
\Gamma(\omega)=\|D\omega\|_1.
$$

Additional channels are a nonnegative clause-violation count $S$, an interface
discrepancy

$$
J=\sum_{(i,j)}\|r_{ij}(\omega_i)-r_{ji}(\omega_j)\|_1,
$$

and a supplied alignment statistic $X\in[0,1]$. If $X$ is obtained by a
normalized residual construction, we use the separate convention $X=0$ when
$\Phi=0$. A tuple $(\Phi,S,\Gamma,J,X)$ does not by itself establish that its
entries are realized by a particular field or constraint system.

**Proposition 2.1.** For the induced sum-norm operator bound $L=\|D\|_{1\to1}$,

$$
\Gamma(\omega)\le L\Phi(\omega).
$$

**Proof.** For every $a$, $D(\omega-Ba)=D\omega$, and hence
$\|D\omega\|_1\le L\|\omega-Ba\|_1$. Minimization gives the result.
In finite dimensions $\operatorname{im}B$ is closed and the residual minimum
is attained. In particular $\Phi=0$ implies $\Gamma=0$.

Different channels can nevertheless distinguish different defects. A logical
assignment can violate a clause even when the cochain is exact. A directed cycle
without faces has $\Gamma=0$ for every field but can have $\Phi>0$. On a filled
directed triangle,

$$
\Phi(\omega)=|\omega_1+\omega_2+\omega_3|=\Gamma(\omega).
$$

The lower bound is the triangle inequality for every representative; a potential
can move the whole cycle sum onto a single edge, attaining it. These examples
show distinct diagnostic roles, rather than complete independence.

## 3. Admissible candidates

For abstract nonnegative diagnostic pairs define

$$
R(\Phi,\Gamma)=
\begin{cases}
\Gamma/\Phi,&\Phi>0,\\
0,&\Phi=\Gamma=0,\\
+\infty,&\Phi=0<\Gamma.
\end{cases}
$$

The last case is incompatible with a realized field in the fixed complex above.
It is retained to reject inconsistent supplied data. Likewise $\Phi=0<X$ is
rejected under the stated alignment convention.

Fix $R_{\max}>0$. A candidate with primed diagnostics must satisfy

$$
\Phi'\le\Phi,\qquad R(\Phi',\Gamma')\le R_{\max}.
$$

These are literal comparisons. The ranking tolerance introduced below does not
relax them. For positive $\Phi'$ the ratio comparison can be evaluated exactly
as $\Gamma'\le R_{\max}\Phi'$ without division.

**Counterexample 3.1: deletion.** Removing one edge and the incident face of a
filled triangle leaves a path. Every field on that path is exact and there are
no face residuals. Both diagnostics become zero and the ratio test passes.
Consequently this ratio condition does not detect constraint deletion. Any
required preservation of the carrier, clauses or interfaces is a separate
condition on the proposed transformation.

For a candidate that expands a representation, an optional additional condition is

$$
(\Phi-\Phi')+\frac12(S-S')>c_{\mathrm{dim}},
$$

where $c_{\mathrm{dim}}\ge0$ is a specified dimension penalty. This is another
policy condition, not a consequence of the residual inequality.

## 4. Global tolerance ranking

Let $A$ be a finite, nonempty set of candidates that passed the required checks.
For candidate $o$, let its nonnegative execution cost be $c_o$ and define

$$
F_o=\Phi_o+\tfrac12S_o+\tfrac15\Gamma_o+\tfrac1{10}J_o+c_o.
$$

The coefficients are specified choices. No mathematical optimality of these
particular weights is asserted. For a tolerance $\epsilon>0$ form

$$
F_{\min}=\min_{o\in A}F_o,\qquad
C=\{o\in A:F_o\le F_{\min}+\epsilon\},
$$

$$
X_{\min}=\min_{o\in C}X_o,\qquad
T=\{o\in C:X_o\le X_{\min}+\epsilon\}.
$$

Select the lexicographically smallest $(F_o,X_o,\operatorname{name}(o))$
among candidates in $T$, using a fixed ordering of names. This is a global
set-based rule. Pairwise approximate equality is not used as a comparator.
Identical records can share a name; distinct selected transformations require
distinct names or another declared final ordering.

**Proposition 4.1.** The selected candidate has $F_o\le F_{\min}+\epsilon$
and $X_o\le X_{\min}+\epsilon$. It need not minimize either coordinate exactly.

**Proof.** Both bands contain a minimizer and are nonempty. The final choice is
made within $T\subseteq C$, so both inequalities follow from membership.

For example, with $\epsilon=1/10$, scores and alignment values $(0,1/2)$ and
$(1/20,0)$ both enter the score band, but only the second enters the alignment
band. It is selected although its score is larger. This is the intended
tolerance rule. It does not permit the primary residual to increase, because
the admission comparison was applied before ranking.

## 5. Implementation and formal verification

The exact rational methods of `code/mod_constraint_regulation_core.py` implement
signature validation, the cross-multiplied ratio comparison, the expansion
condition and the global ranking rule. They reject malformed rational inputs.
The numerical interface uses floating-point diagnostics and rejects nonfinite
states or scores. Numerical evaluations are not exact proofs about the field
from which those diagnostics are said to originate.

`lean4/Regulate.lean` verifies rational comparison statements, selected ranking
cases and classifications of rejected candidates. It does not construct a
general cochain complex or prove Proposition 2.1; that proposition has the prose
proof in Section 2. The bundled census records the checked declaration set.
Tests exercise the reference implementation, including invalid inputs and the
constraint-deletion limitation.

## 6. Limitations and discussion

Selection uses a finite supplied candidate set. It does not establish that this
set contains a feasible repair. The policy does not certify the diagnostic
computation, preserve constraints against deletion or guarantee termination.
Even literal non-increase of a real residual allows repeated equal-score steps
and does not imply finite termination. Applications needing an absolute closure
bound must specify one separately from the ratio ceiling.

## References

1. S. Boyd and L. Vandenberghe, *Convex Optimization*, Cambridge University Press,
   2004. [Author-hosted book](https://web.stanford.edu/~boyd/cvxbook/).
2. A. Hatcher, *Algebraic Topology*, Cambridge University Press, 2002, Sections
   2.1 and 3.1. [Author-hosted book](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html).
