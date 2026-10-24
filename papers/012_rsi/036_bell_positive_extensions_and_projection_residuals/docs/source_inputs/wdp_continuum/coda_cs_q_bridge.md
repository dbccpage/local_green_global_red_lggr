<div align="center">

# Finite Profile Factorization and Sampling Limits (CODA-CS-Q)

**Subtitle:** Image factors, decoder bounds, and missing-value obstructions

**Author:** Jeremy H. Carroll

**Date:** 2026-09-28

**Version:** 3.0.1

**Status:** first public preprint

**License:** Creative Commons Attribution 4.0 International

</div>

## CODA Architecture & Layers

CODA stands for the Calculus of Obstruction, Descent, and Authority. Its eight research components are FOC, MUR, CS, CS_Q, Q, A, OR, and FDA; GTLA is the overarching authority architecture, not a ninth mathematical component. The order below is the application's runtime order and does not assert that this paper's image-factor theorem is implemented by the application.

| Runtime stage | Abbreviation | Component or architecture |
| :---: | :--- | :--- |
| 1 | **FOC** | Finite Obstruction Calculus |
| 2 | **MUR** | Meta & Universal Re-Presentation (what presentations exist) |
| 3 | **CS** | Continuum Shadow (what continuum presentation may descend to a finite calculus system) |
| 4 | **CS_Q** | Continuum Shadow to Continuum Bridge (how continuum presentations descend) |
| 5 | **Q** | The Continuum (continuum presentations via completion and enclosure) |
| 6 | **A** | Anomalon (global residuals not removed and typed instead) |
| 7 | **OR** | Omniversal Re-Presentation (what presentations can transport) |
| 8 | **FDA** | Finite Descent Authority (what presentation may descend to evaluation and authorization) |
| 9 | **GTLA** | Layered Authority Architecture for CODA |

## Abstract

A query factors through a sample profile on the image of that profile if
and only if it is constant on the fibres. The honest reverse is a map out
of the image: a value together with a witnessing state. A total factor on
the whole observation space needs a section of the profile, or a choice
on the unused labels. If a decoder is everywhere within $\varepsilon$ of
the query, two states with the same profile have query values at most
$2\varepsilon$ apart. A Lipschitz query cannot change faster than its
constant times the input gap. Sampling a real function at $0$ and at $1$
does not determine its value at $1/2$: the zero function and
$t(1-t)$ agree at the endpoints and disagree in the middle. Named maps in
the package agree when they are the query and the factored composite.
General authority terminalizers are not proved. Authorized glue of
overlapping shadows is not proved here.

## Introduction

It is easy to treat a short sample list as a curve. You write down
$f(0)$ and $f(1)$, or a blurry decoder that almost recovers a query, and
talk as if the missing values had been filled in. Two numbers are two
numbers. An approximate decoder is an approximate decoder. Neither object
is an arbitrary function of the state.

A picture. Look at real functions only at the endpoints $0$ and $1$. The
zero function and the hump $t(1-t)$ both sample to $(0,0)$. At the
midpoint the first is $0$ and the second is $1/4$. The two-dot profile
does not determine the midpoint query.

A second picture. Suppose a decoder $g$, reading only the profile, stays
within $\varepsilon$ of the true query at every state. On a fibre the
profile does not move, so the two query values are each within
$\varepsilon$ of the same decoded number. The triangle inequality puts
them at most $2\varepsilon$ apart. At $\varepsilon=0$, the query values
have distance zero; equality of values additionally requires metric separation.

A third picture. If the query itself is Lipschitz with constant $K$, then
states at distance at most $\varepsilon$ have query values at most
$K\varepsilon$ apart. Nearby inputs give a bounded change of answer. That
bound is not an identification of the two answers.

The theory is refuted by any of: a query that factors through a profile
while splitting a fibre; a well-defined image factor whose values depend
on the choice of witness in a fibre; a decoder within $\varepsilon$ whose
fibre collision exceeds $2\varepsilon$; a Lipschitz query that outruns
its constant; a rule that reads $f(1/2)$ off the pair $(f(0),f(1))$ for
every real function $f$; or a total factor on unused observation labels
constructed from fibre constancy alone.

This note does not derive quantum mechanics.

## Notation

Throughout, the types are ordinary.

- $X$ is a type of states. $P$ is a type of observations. $Y$ is a type
  of answers.
- $p:X\to P$ is a *profile*: a sample map, a coarse look, a list of
  coordinates you actually hold.
- $q:X\to Y$ is a *query*: the function of the state whose value you
  want.
- $q$ is *fibre-constant* for $p$ when $p(x)=p(y)$ implies $q(x)=q(y)$.
- $q$ *factors through* $p$ when there is $g:P\to Y$ with $g(p(x))=q(x)$
  for every $x$.
- The *image* of $p$ is the subtype of those $z\in P$ for which some
  $x\in X$ has $p(x)=z$. A point of the image may be written as a pair
  $(z,x)$ with $p(x)=z$.
- When $Y$ carries a pseudometric, $\mathrm{dist}$ denotes its distance.
- When $X$ and $Y$ both carry pseudometrics, $q$ is *Lipschitz with
  constant* $K\ge 0$ when $\mathrm{dist}(q(x),q(a))\le K\cdot\mathrm{dist}(x,a)$
  for all $x,a$.

A **decoder** of $q$ through $p$ is a map $g:P\to Y$. It is an
*$\varepsilon$-decoder* when $\mathrm{dist}(q(x),g(p(x)))\le\varepsilon$
for every $x$. Exact factorization is the case $\varepsilon=0$ with
equality of values rather than a distance bound.

## 1. Factorization on the image is fibre constancy

Fibre constancy is the statement that equal observations give equal
answers. Factorization through the whole of $P$ is stronger: it supplies
an answer even at observation labels that no state produces. Through the
image, the two statements match.

### Theorem CSQ-T1 — exact on the image

Let $p:X\to P$ and $q:X\to Y$. The following are equivalent.

1. There is a map $g$ from the image of $p$ to $Y$ such that
   $g(p(x))=q(x)$ for every $x$.
2. $q$ is fibre-constant for $p$.

**Proof.** From (1) to (2): if $p(x)=p(y)$, then $p(x)$ and $p(y)$ are
the same image point, so $q(x)=g(p(x))=g(p(y))=q(y)$.

From (2) to (1): given an image point $z=p(x)$, set $g(z)=q(x)$. If
$z=p(x)=p(y)$, fibre constancy gives $q(x)=q(y)$, so the value does not
depend on which preimage was used. Lean `Coda.CSQ.ImagePoint` bundles the
observed value, an explicit witness, and a proof of the profile equality.
`Coda.CSQ.ImageFactor` requires both recovery and invariance under equal
profile values. This direct witness proof uses no choice of a range preimage.

This is Lean `Coda.CSQ.exact_on_image`.
The package form is `CodaCsQ.factorization_iff_fiber_constancy_on_image`.
$\square$

A total factorization $q=g\circ p$ with $g$ defined on all of $P$ still
implies fibre constancy: if $p(x)=p(y)$, then
$q(x)=g(p(x))=g(p(y))=q(y)$. That direction does not use the image. Lean
name: `CodaCsQ.factorization_implies_fiber_constancy`.

Two image factors that both recover $q$ are equal. Every image point is
$p(x)$ for some $x$, so both maps send it to $q(x)$. That is Lean
`Coda.CSQ.image_factor_unique`.

## 2. A blurry decoder still bounds collisions

Exact factorization has zero error; the converse needs metric separation. An approximate decoder does
not make the query constant on fibres. It does bound how far the query
can move.

### Theorem CSQ-T2 — collision distance is at most $2\varepsilon$

Let $Y$ be a pseudometric space, let $g:P\to Y$, and suppose

$$
\mathrm{dist}\bigl(q(x),g(p(x))\bigr)\le\varepsilon
\quad\text{for every }x\in X.
$$

If $p(x)=p(y)$, then

$$
\mathrm{dist}\bigl(q(x),q(y)\bigr)\le 2\varepsilon.
$$

**Proof.** The triangle inequality through the decoded value at $p(x)$
gives

$$
\mathrm{dist}(q(x),q(y))
\le
\mathrm{dist}(q(x),g(p(x)))
+
\mathrm{dist}(g(p(x)),q(y)).
$$

The first summand is at most $\varepsilon$ by hypothesis. For the second,
$p(x)=p(y)$ and symmetry of distance turn
$\mathrm{dist}(g(p(x)),q(y))$ into $\mathrm{dist}(g(p(y)),q(y))$, which
is at most $\varepsilon$ again. This is Lean
`Coda.CSQ.approximate_collision_bound`. $\square$

When $\varepsilon=0$, the collision distance bound yields $\mathrm{dist}(q(x), q(y)) \le 0$, hence $\mathrm{dist}(q(x), q(y)) = 0$ by nonnegativity of pseudometrics. In a general pseudometric space where distinct answers can sit at distance zero (for instance, an indiscrete pseudometric where $\mathrm{dist}(a,b)=0$ for all $a, b$), zero decoder error does not imply that $q(x)$ and $q(y)$ are equal as elements. Value equality $q(x) = q(y)$ strictly requires the target space to satisfy the metric separation axiom ($\mathrm{dist}(a, b) = 0 \implies a = b$). When metric separation holds and $\varepsilon=0$, zero error implies that $q$ is constant on every fibre, and Theorem CSQ-T1 supplies a well-defined image factor. Lean formalizes this separation in `Coda.CSQ.metric_zero_error_implies_equality` and exhibits the indiscrete separation failure in `Coda.CSQ.pseudometric_zero_error_does_not_imply_equality`. A positive $\varepsilon$ is not that factor. The two query values may still differ; they just cannot differ by more than twice the decoder error.

A finite replay. Let $p$ be parity on the integers $\{2,4\}$, let
$q$ be the identity, and let $g$ send evenness to $3$. Then
$|2-3|=1$ and $|4-3|=1$, so $\varepsilon=1$ works, and
$|4-2|=2\le 2\varepsilon$. The decoder is blurry. The fibre still
collides.

## 3. Nearby inputs, nearby answers

The collision bound of Theorem CSQ-T2 controls the query on a fibre of
$p$. A Lipschitz hypothesis on $q$ itself controls the query when the
*inputs* are close, whether or not they share a profile.

### Theorem CSQ-T3 — Lipschitz access

Let $X$ and $Y$ be pseudometric spaces, and let $q:X\to Y$ be Lipschitz
with constant $K\ge 0$. If $\mathrm{dist}(x,a)\le\varepsilon$, then

$$
\mathrm{dist}\bigl(q(x),q(a)\bigr)\le K\varepsilon.
$$

**Proof.** Lipschitz says
$\mathrm{dist}(q(x),q(a))\le K\cdot\mathrm{dist}(x,a)$. The right-hand
side is at most $K\varepsilon$ because $K$ and $\varepsilon$ are
nonnegative. Lean `Coda.CSQ.lipschitz_access` proves the more abstract
ordered-carrier implication for a monotone scale function. Taking the scale
to be multiplication by $K\ge0$ gives the displayed mathematical argument;
the package does not instantiate that abstract structure with real metrics. $\square$

Take $q(t)=2t$ on $\mathbb{Q}$ with the usual metric, and $K=2$. The
points $1/2$ and $2/5$ are $1/10$ apart, and the query values $1$ and
$4/5$ are $1/5$ apart, which is exactly $K$ times the input gap. The
bound is sharp on this pair. It still does not say that $q(1/2)$ equals
$q(2/5)$.

Lipschitz access is not fibre constancy. The integer states $2$ and $4$
share the parity profile and have usual distance $2$. CSQ-T3 bounds the
change of a Lipschitz query on these states; it does not force equality.
Theorem CSQ-T2, or exact factorization, is the fibre statement.

## 4. Two dots do not make a curve

Let the state space be the type of functions $\mathbb{R}\to\mathbb{R}$.
The *two-dot profile* is

$$
p(f)=\bigl(f(0),f(1)\bigr).
$$

The *midpoint query* is $q(f)=f(1/2)$.

### Theorem CSQ-T4 — endpoint samples do not determine the midpoint

The midpoint query does not factor through the two-dot profile:

$$
\neg\,\mathsf{Factors}\bigl(f\mapsto(f(0),f(1)),\ f\mapsto f(1/2)\bigr).
$$

**Proof.** Let $f$ be the zero function, and let $g(t)=t(1-t)$. Then

$$
f(0)=f(1)=0=g(0)=g(1),
$$

so $p(f)=p(g)$, while $f(1/2)=0$ and $g(1/2)=(1/2)(1/2)=1/4$. A factor
through $p$ would have made the midpoint values agree. $\square$

**Formal scope.** `Coda.CSQ.samples_not_query` proves the Boolean analogue
for functions `Point3 → Bool`: two observed coordinates do not determine a
third coordinate. The real-function quadratic argument above is a prose
proof, with exact rational midpoint checks in the companion tests; it is
not the statement of that Lean declaration.

Two dots, one missing height. The sample pair $(0,0)$ is honest. It is
shared by more than one curve. Reading $f(1/2)$ off that pair is a guess,
not a factor.

The same obstruction, in a discrete costume, is Theorem CS-T3 of the CS
companion: four Boolean pairs, first-coordinate projection, second
coordinate not a function of the first. Family observations still agree
pointwise and only pointwise (CS-T2). Metric completion and midpoint
enclosure, in the Q companion, supply completed points and interval
bounds; they do not cancel Theorem CSQ-T4.

A finite quadrature that uses only the listed nodes *does* factor through
those nodes, because it is a function of the samples. On the grid
$\{0,1/4,1/2,3/4\}$ with $X(t)=2t$ at those nodes, the energy

$$
0^2\cdot\frac14
+
\bigl(\tfrac12\bigr)^2\cdot\frac14
+
1^2\cdot\frac14
+
\bigl(\tfrac32\bigr)^2\cdot\frac14
=
\frac78
$$

is constant on the fibre of that four-dot profile. Replacing the grid
function by another function with the same four samples does not change
the number. Replacing the query by “value at $1/8$”, a node the profile
does not hold, returns the obstruction of Theorem CSQ-T4.

## 5. A total factor needs an extension

Theorem CSQ-T1 gives a factor on the image. The unused part of $P$ is not
the image. Assigning answers there is extra data.

### Theorem CSQ-T5 — fibre constancy need not extend to the whole codomain

There exist $p$ and $q$ such that $q$ is fibre-constant for $p$, and $q$
does not factor through $p$ as a map out of the whole observation type.

**Proof.** Take the empty type as $X$ and as $Y$, and take the unit type
as $P$. There is a unique $p$ and a unique $q$. Fibre constancy holds
vacuously: there are no states to compare. A total factor would be a map
from the unit type to the empty type, sending the unused label to an
answer that does not exist. This is Lean
`Coda.CSQ.whole_codomain_needs_extension`. $\square$

The empty example is extreme on purpose. A inhabited companion is the
same point with more room to write. Let $X$ be a singleton $\{a\}$, let
$P=\{0,1\}$, let $p(a)=0$, and let $q(a)=7$. Fibre constancy holds — there
is only one state — and the image factor is $g(0)=7$. Nothing in that data
selects $g(1)$. A section of $p$ would pick, for every label, a state
mapping to it; here $1$ has no preimage. A choice of a default answer in
$Y$ would fill the complement. Either piece of extra data produces a
total $g:P\to Y$. Neither piece is fibre constancy.

If $Y$ is nonempty, classical choice does fill the complement: use the
image factor on the range, and pick any element of $Y$ off the range.
That is Lean `Coda.CSQ.total_factor_of_inhabited`. It is a total factor
from a nonempty-target hypothesis and choice, not from fibre constancy
alone. The image reverse remains the reverse that does not invent answers
at unused labels.

## 6. Named maps, not a general terminal theorem

The package Lean records two named maps of the same type, written
$\tau_Q$ and $\tau_{\mathrm{CS}}$, and the pointwise statement that they
agree. If those maps are chosen to be the query $q$ and the composite
$\bar{q}\circ p$, then factorization $q=\bar{q}\circ p$ is exactly their
agreement.

Agreement is not automatic from other flags. The identity on the Booleans
and the constant-true map disagree at `false`, even if three surrounding
propositions are true. The two package theorems are named in
`lean4/T03NamedTerminalizers.lean`.

General authority terminalizers are not proved.

## 7. Computational companion

The companion module `code/coda_cs_q_bridge_core.py` records a finite
sample profile, checks fibre constancy on a listed domain, and, when that
check passes, builds an image lookup for the query. Asking the lookup at
a profile that never occurred raises an error: that is the total-reverse
refusal of Section 5, on a finite list. Exact arithmetic routines use rational scalars;
floats and booleans in scalar position raise `TypeError`.
Each solve copies the finite domain and records each profile/query pair once.
Its factor is defined only on that observed `Prof(D)`, returns detached values,
and raises `KeyError` on an unobserved profile. It assumes deterministic,
non-mutating callables and hashable profiles with stable equality; it does
not certify future changes to state or callable behavior. Admission flags
require actual booleans. `ImagePoint` requires a profile binding, rechecks its
witness, and reads a supplied factor; constructing a point alone proves no
fibre constancy.

On the four-node quadrature of Section 4 the calculator returns $7/8$
and reports fibre constancy. On the two-dot domain
$\{\,t\mapsto 0,\ t\mapsto t(1-t)\,\}$ it refuses a midpoint factor. On
the parity domain of Section 1 a query that depends only on evenness
acquires an image factor; the identity query does not.

The same module stores a finite checklist of named hypotheses: the sample
list is nonempty, declared transitions agree on the listed states, a
completion flag is set, a Boolean flag declares the continuum debts paid, the query is constant on realized fibres, two routes are declared
to agree, a reflection flag is set, and two named maps are compared
pointwise. That checklist is a record of hypotheses. It is not a proof
that each hypothesis holds in analysis.

Lean files in `lean4/`:

- `Algebra.lean` — exact image equivalence and uniqueness, abstract
  distance bounds, the Boolean CSQ-T4 analogue, and extension results;
- `T01FactorizationFiberConstancy.lean` — image reverse as
  `ImagePoint`;
- `T02BridgeAdmissibility.lean` — 14-schema and 8-step admission audit;
- `T03NamedTerminalizers.lean` — named maps of Section 6;
- `Core.lean` — re-exports the files above.

There are no `sorry` stubs in those reconstruction theorems. The
statements use the ordinary Lean kernel.

Adversarial tests include: a query that splits a fibre; a decoder treated
as exact factorization; two named maps that disagree; a midpoint read off
endpoint samples; float rejection.

## 8. Limitations

The reconstruction theorems are an image-restricted equivalence of
factorization with fibre constancy; a $2\varepsilon$ collision bound for
an $\varepsilon$-decoder; a Lipschitz bound for nearby inputs; an
explicit two-function collision at the midpoint; and a witness that fibre
constancy need not extend off the image. They hold for ordinary functions
of types, and for pseudometric targets where a distance is used.

Authorized glue of overlapping shadows — the H3'' lemma — is not proved
here.

Translation semigroups, action semigroups, and Hamilton–Jacobi generators
are not theorems of this note.

The Python companion checks finite domains and exact rationals. It does
not construct a factor for an arbitrary map of types, and it does not
decide equality of arbitrary reals.

A Lipschitz constant is extra data. Theorem CSQ-T3 uses it. An arbitrary
query $\mathbb{R}\to\mathbb{R}$ need not be Lipschitz, and Theorem CSQ-T4
is then the obstruction that remains.

## References

1. S. Mac Lane, *Categories for the Working Mathematician*, 2nd ed.,
   Springer, 1998. <https://doi.org/10.1007/978-1-4757-4721-8>
2. W. Rudin, *Principles of Mathematical Analysis*, 3rd ed., McGraw-Hill,
   1976.
3. J. H. Carroll, *The Continuum Shadow: Continuum Re-presentations that
   Descend to the Finite Calculus (CODA-CS)*, 2026.
4. J. H. Carroll, *The Continuum: Continuum Representations via Completion
   and Enclosure (CODA-Q)*, 2026.
5. A. Grothendieck, “Technique de descente et théorèmes d'existence en
   géométrie algébrique,” Séminaire Bourbaki, 1959.
