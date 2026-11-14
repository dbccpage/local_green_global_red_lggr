<div align="center"># Proposal selection and continuation-stable diagnostics on finite graphs</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">2026-10-23</div>
<div align="center">Version 2.0.5</div>

## Abstract

We separate the generation of candidate edge fields from a decision rule based
on independently computed diagnostics. On a finite connected graph, distance
to the image of the incidence map measures failure of exactness. A declared
face map supplies a closure residual. A lexicographic comparison of diagnostics,
subject to a ratio condition, defines one proposal-selection policy. Equal
diagnostic traces have equal decisions by construction, but equal current
diagnostics need not remain equal after further proposals. For a declared
family of transformations, we characterize the largest equivalence relation
inside diagnostic equality that is preserved by every finite continuation.
We give explicit cycle examples distinguishing local exactness from global
exactness, and one-step decisions from continuation-stable state compression.
Executable paths additionally require agreement of adjacent endpoint states.
The accompanying exact rational checks and Lean results are scoped to their
stated finite and abstract objects.

## 1. Setting and purpose

Let $P=(V,E)$ be a finite directed graph whose underlying undirected graph is
connected. A field $\omega\in\mathbb R^E$ assigns a real value to each directed
edge. Reversing the orientation of an edge reverses the sign used in a path sum.
The incidence map is

$$
(Bf)_{ij}=f(j)-f(i).
$$

A proposal is a specified map $T$ taking a field to a candidate field. The
selection rule studied here evaluates the candidate field rather than the
proposal's name or description. This separation is an interface definition;
it does not establish that an arbitrary software system follows that definition.
The graph and convex-optimization foundations are standard [1,2].

## 2. Quotient residuals and cycle consistency

Define

$$
\Phi(\omega)=\min_f\|\omega-Bf\|_1.
$$

The minimum is attained: the residual space is affine and closed, and its
intersection with a sufficiently large norm ball is compact. Potentials need
not be unique; fixing one vertex removes the additive constant but does not
in general remove all minimizer nonuniqueness.

For a signed graph cycle $C$, write
$\Delta_C(\omega)=\sum_{e\in C}\epsilon_e\omega_e$, where the sign records
agreement with the traversal orientation.

**Theorem 2.1.** The following are equivalent:

1. $\Phi(\omega)=0$.
2. $\omega=Bf$ for some potential $f$.
3. $\Delta_C(\omega)=0$ for every cycle $C$.

**Proof.** Attainment makes the first two equivalent. If $\omega=Bf$, summing
around a cycle telescopes to zero. Conversely choose a root and define $f(v)$
as the signed sum along a path from that root to $v$. Two such paths differ
by a cycle-space element; the zero-cycle condition makes the sum independent
of the path. Applying this to the endpoints of an edge gives $Bf=\omega$.
Checking a cycle basis suffices by linearity.

On a tree every field is exact. On a cyclically oriented triangle,

$$
\Phi(\omega)=|\omega_1+\omega_2+\omega_3|.
$$

Every residual has this same signed sum, giving the lower bound by the triangle
inequality. A potential can set two residual coordinates to zero, attaining it.

For rational data, an exact primal–dual witness consists of a potential $f$,
residual $h=\omega-Bf$ and vector $\varphi$ such that

$$
B^T\varphi=0,\qquad \|\varphi\|_\infty\le1,\qquad
\varphi^T\omega=\|h\|_1.
$$

For any other potential $a$, dual feasibility gives
$\varphi^T\omega=\varphi^T(\omega-Ba)\le\|\omega-Ba\|_1$.
Thus the equality certifies optimality without trusting the solver that supplied
the witness. Existence of a witness for every arbitrary numerical input is a
separate solver question.

## 3. Closure residuals and ratio conventions

When faces are specified, let $D$ be their signed edge-to-face map and require
$DB=0$. For any minimizing residual $h=\omega-Bf^*$,

$$
\Gamma(\omega)=\|Dh\|_1=\|D\omega\|_1
\le\|D\|_{1\to1}\Phi(\omega).
$$

The equality follows from $DB=0$; the inequality is the induced norm bound.
Closure is therefore independent of the chosen minimizer. Without faces one
may use a zero-dimensional target and $D=0$, giving $\Gamma=0$ by explicit
convention; no additional face information is thereby recovered.

For $\Phi>0$ the exact ratio is $\Gamma/\Phi$. A numerical policy can instead
define, for $\epsilon\ge0$,

$$
R_\epsilon=
\begin{cases}
\Gamma/\Phi,&\Phi>\epsilon,\\
0,&\Phi\le\epsilon\ \text{and}\ \Gamma\le\epsilon,\\
+\infty,&\Phi\le\epsilon<\Gamma.
\end{cases}
$$

The infinity value marks rejection under the policy; it is not an infinite
geometric curvature. With $\Phi=1/4000$, $\Gamma=1/2000$ and
$\epsilon=1/1000$, the policy ratio is zero while the exact ratio is two.
Passing a ceiling on $R_\epsilon$ consequently does not establish the same
ceiling on the exact ratio.

## 4. Decisions based on diagnostic traces

Let $d(\omega)=(\Phi(\omega),\Gamma(\omega),X(\omega))$, where $X$ is a
declared auxiliary function. If it depends on a selected minimizing residual,
the selection convention is part of the definition of $d$. If no such function
has been independently specified, setting $X=0$ supplies no extra information.

One exact policy accepts $\omega\to\omega'$ when $R_\epsilon(\omega')\le R_{\max}$
is finite and the triple $d(\omega')$ is strictly lexicographically smaller than
$d(\omega)$. This means a decrease of the first coordinate, or a tie there and
a decrease of the second, or ties in both and a decrease of the third.

**Proposition 4.1.** Two proposals with the same before/after diagnostics and
the same ratio-test value receive the same decision under this policy.

**Proof.** The decision is the stated function of those values. The proposal
label is not an argument of that function.

This is a property of the specified interface, not a claim that identical labels
have identical effects. An implementation must compute or verify the diagnostic
values from the candidate fields. Caller-supplied numbers alone do not certify
the connection to those fields. Strict real-valued descent also need not
terminate: the sequence $1,1/2,1/3,\ldots$ strictly decreases indefinitely.

## 5. Examples of information lost by a diagnostic

### Local exactness does not imply global exactness

On a directed triangle take $\omega=(1,0,0)$. Restrict it to each of the two-edge
path subgraphs. Each path is a tree, so each restriction has zero quotient
residual. The restrictions agree on shared edges and assemble into the given
global field, whose residual is one. Compatible local edge values can therefore
form a global field without making that field exact. This example distinguishes
gluing of data from the additional cycle condition for gluing potentials.

### A periodic proposal need not be selected

Cyclically shifting the three coordinates of $(1,0,0)$ produces a period-three
orbit. Every field in that orbit has cycle sum one and the same quotient
residual. With $D=0$ and $X=0$, none of those steps meets the strict selection
rule. Noncommuting transformations likewise need not be distinguished by a
diagnostic: their different outputs may be mapped to the same diagnostic value.

### Equal current diagnostics can separate after a continuation

Let $x=(1,0,0)$ and $y=(-1,0,0)$ on the triangle, again with $D=0$ and $X=0$.
Both have $d=(1,0,0)$. For the translation $T(w)=w+(1,0,0)$,

$$
\Phi(Tx)=2,\qquad \Phi(Ty)=0.
$$

Thus equality of current diagnostics does not permit identification of the two
states if subsequent translations must be represented correctly.

## 6. Continuation-stable equivalence

Let $X$ be any state set, $d:X\to Y$ an observation map and $\mathcal T$ a
declared family of total maps $X\to X$. Write $\mathcal T^*$ for finite
compositions, including the identity. Define

$$
x\sim y\quad\Longleftrightarrow\quad
d(Wx)=d(Wy)\text{ for every }W\in\mathcal T^*.
$$

**Theorem 6.1.** This is the largest equivalence relation contained in
$\ker d$ that is preserved by each map in $\mathcal T$.

**Proof.** Reflexivity, symmetry and transitivity hold pointwise after every
continuation. The identity continuation gives $\sim\,\subseteq\ker d$.
If $x\sim y$ and $T\in\mathcal T$, then every $W\circ T$ is another finite
continuation, so $d(WTx)=d(WTy)$; hence $Tx\sim Ty$.

Let $R\subseteq\ker d$ be an equivalence relation preserved by all admitted
maps. Induction on word length gives $Wx\,R\,Wy$ whenever $x\,R\,y$.
Containment in $\ker d$ gives $d(Wx)=d(Wy)$ for each word, so $R\subseteq\sim$.
This establishes maximality.

The quotient supports well-defined maps $[T]([x])=[Tx]$ and
$\bar d([x])=d(x)$. It is the coarsest state quotient preserving all the
specified finite observations and transformations. If $\ker d$ is already
preserved by every admitted map, it equals $\sim$. At the other extreme, if
$d$ is nonconstant and all total maps are admitted, $\sim$ is equality: any two
distinct states can be sent to two states distinguished by $d$.

These statements are relative to the specified family. They do not provide an
algorithm for computing this relation on an arbitrary infinite state space.

## 7. Finite vector-valued fields

The residual definition extends to a fixed norm $g$ on $\mathbb R^k$:

$$
\Phi_g(\omega)=\min_{f:V\to\mathbb R^k}
\sum_{e\in E}g\bigl(\omega_e-(Bf)_e\bigr).
$$

Finite-dimensionality again gives attainment. Coordinatewise application of
the path-sum argument shows that this residual is zero exactly when the
vector-valued field is exact. Choosing $g=\|\cdot\|_1$ separates the problem
into scalar channels; choosing $g=\|\cdot\|_2$ couples them within each edge.
Neither choice is selected by the scalar quotient construction alone.
The bundled reference solver is scalar; this formula is a mathematical extension,
not a claim that the solver implements every vector-valued norm problem.

Matrix-based proposals need no privileged role in selection. For example, if
$A^T=-A$ and $B^T=-B$, then $[A,B]^T=-[A,B]$. Commutators therefore stay in
the space of real skew-symmetric matrices. A particular generating family
need not generate that entire Lie algebra, and this closure observation imposes
no residual decrease on a proposed field.

## 8. Paths, implementation and formal scope

A list of individually accepted steps need not be an executable trajectory.
Adjacent steps must also satisfy equality of the preceding target state and
following source state. Diagnostic equality at the boundary does not imply
state equality, as the translation example demonstrates.

`code/mod_operator_proposal_core.py` implements exact rational witness checks,
the diagnostic comparison and endpoint checks. Its general graph solver uses
a two-phase simplex over rational numbers and independently checks the resulting
primal–dual equality. The existence of the mathematical optimum does not imply
that every possible input representation or solver implementation is correct;
the witness checker supplies a separate condition on each returned result.

`lean4/Proposal.lean` verifies integer triangle identities, preservation of a
finite path predicate under label erasure, and the continuation-equivalence
properties for arbitrary state and observation types. Its finite path example
uses natural-number before/after values; it is not a mechanization of every
real-valued graph diagnostic or numerical solver. No external formal theorem
names or absent source files are needed for the results cited here.

## 9. Discussion

Diagnostic equality has several distinct uses: defining equal one-step decisions,
assembling compatible edge data, and identifying states under future transformations.
The first does not imply the other two. A selected proposal satisfies the stated
comparison policy; further properties such as feasibility, constraint preservation
and convergence require their own evidence. The continuation relation gives an
exact criterion for state identification relative to a declared transformation
family, without turning that criterion into an unrestricted compression claim.

## References

1. A. Hatcher, *Algebraic Topology*, Cambridge University Press, 2002, Sections
   2.1 and 3.1. [Author-hosted book](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html).
2. S. Boyd and L. Vandenberghe, *Convex Optimization*, Cambridge University Press,
   2004, Chapters 4–5. [Author-hosted book](https://web.stanford.edu/~boyd/cvxbook/).
