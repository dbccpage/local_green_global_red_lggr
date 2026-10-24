<div align="center">

# Local Green, Global Red III

## A finite evaluator overlay across six system roles

**Author:** Jeremy H. Carroll  
**Date:** 2026-10-15  
**Version:** 1.5.2  
**License:** CC-BY-4.0  

</div>

## Abstract

Two checks can pass separately while their composition fails. For binary local
verdicts $e_1,e_2$ and a binary verdict $e_g$ on the composite, the signed
evaluator defect

$$
\Delta_E=e_g-e_1e_2
$$

is $-1$ precisely in the local-green/global-red case
$(e_1,e_2,e_g)=(1,1,0)$. This paper shows how the same finite diagnostic can be
used across six distinct system roles without treating it as a new layer or
changing its mathematics. The main results are elementary but useful:
the defect has a three-way sign classification; finite sums obey an exact
global-minus-local identity; cancellation of a total defect does not imply
pointwise agreement; and an evaluator cannot descend to a quotient if it
assigns different verdicts to equivalent carrier elements. A tested Python
implementation, seven teaching and verification notebooks, and a Lean 4 library
accompany the paper. The Lean library checks the finite integer statements and
the quotient obstruction. The real-valued weighted-kernel theorem remains
conditional on the explicit hypotheses inherited from LGGR I [8].

## 1. Why this matters

A composed system is often inspected by several specialists: one checks the
mathematical carrier, another checks representation transport, another fixes
the observation scale, and another evaluates an integrated run. Their jobs are
different, but each can ask the same concrete question:

> Did the verdict on the composite agree with the product of the verdicts on
> its two parts?

Writing that discrepancy down prevents a locally successful pipeline from
being summarized by a single misleading green status. The overlay is small
enough to replay and strict enough to reject malformed inputs.

## 2. Scope

The results concern finite binary evaluations and declared integer or real
weights. They do not establish reliability for an arbitrary agent,
organization, software stack, or physical system. A zero observed defect is
sample-relative and can also be produced by an empty sample or an
uninformative evaluator. The real exponential kernel is proved here only
conditionally in prose, not fully mechanized in Lean. The six-role
interpretation is a recording convention, not an empirical adequacy result,
and the related-work comparisons do not identify this model with another
theory. These are the standing caveats for every result below.

## 3. Finite evaluator calculus

### 3.1 Verdict triples

An evaluated boundary consists of a triple

$$
v=(e_1,e_2,e_g)\in\{0,1\}^3,
$$

where $e_1$ and $e_2$ are local verdicts and $e_g$ is the verdict after
composition. Define

$$
\Delta_E(v)=e_g-e_1e_2.
$$

Because $e_1e_2,e_g\in\{0,1\}$, the defect lies in
$\{-1,0,1\}$.

### 3.2 Sign classification

**Proposition 1.** Every verdict triple has defect in
$\{-1,0,1\}$:

$$
\begin{array}{ccl}
\Delta_E=-1 &:& \text{local green, global red},\\
\Delta_E=0  &:& \text{the composite verdict equals the local product},\\
\Delta_E=1  &:& \text{local product red, global verdict green}.
\end{array}
$$

**Proof.** Both $e_g$ and $e_1e_2$ are binary, so their difference has one of
the three displayed values. $\square$

The signs are retained. Replacing $\Delta_E$ by $|\Delta_E|$ is useful for
magnitude summaries but loses the direction of disagreement.

### 3.3 A one-trace counterexample

**Proposition 2.** Local success does not imply composite success.

**Proof.** Choose $(e_1,e_2,e_g)=(1,1,0)$. Then both local verdicts pass, the
composite verdict fails, and

$$
\Delta_E=0-(1)(1)=-1.
\qquad\square
$$

This is an existence result. It says that compositional success needs
additional hypotheses; it does not estimate how often the failure occurs.

## 4. From one trace to a finite sample

Let $v_i=(e_{1i},e_{2i},e_{gi})$ for $i=1,\ldots,n$ and define

$$
G=\sum_{i=1}^n e_{gi},\qquad
L=\sum_{i=1}^n e_{1i}e_{2i},\qquad
D=\sum_{i=1}^n\Delta_E(v_i).
$$

**Theorem 1.** For every finite sample,

$$
G-L=D.
$$

**Proof.** Substitute the definition of $\Delta_E$ and use finite
distributivity:

$$
\sum_i(e_{gi}-e_{1i}e_{2i})
=\sum_i e_{gi}-\sum_i e_{1i}e_{2i}.
\qquad\square
$$

### 4.1 Cancellation and disagreement count

**Proposition 3.** $D=0$ does not imply
$\Delta_E(v_i)=0$ for every $i$.

**Proof.** The two triples $(0,1,1)$ and $(1,1,0)$ have defects $1$ and $-1$.
Their sum is zero although neither defect is zero. $\square$

To distinguish signed cancellation from total agreement, define the positive and negative defect counts:

$$
N_+ = \#\{i : \Delta_E(v_i) = 1\}, \qquad N_- = \#\{i : \Delta_E(v_i) = -1\}.
$$

Then the total signed defect and the total disagreement count satisfy:

$$
D = N_+ - N_-, \qquad M = N_+ + N_- = \sum_{i=1}^n |\Delta_E(v_i)|.
$$

While $D=0$ allows interior cancellations ($N_+ = N_- > 0$), $M=0$ is strictly equivalent to pointwise agreement $\Delta_E(v_i)=0$ on every item of the observed sample. For nonnegative weights $w_i \ge 0$, the weighted sum $\sum_i w_i |\Delta_E(v_i)| = 0$ certifies agreement on the positive-weight support. This is why the implementation reports both the signed defect sum $D$ and the disagreement count $M$, alongside the pointwise defect list.


### 4.2 Worked five-trace example

Consider:

| trace | $e_1$ | $e_2$ | $e_g$ | $\Delta_E$ |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 0 |
| 2 | 1 | 1 | 0 | -1 |
| 3 | 1 | 1 | 0 | -1 |
| 4 | 0 | 1 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 |

The totals are $G=1$, $L=3$, and $D=-2$, hence $1-3=-2$. The companion
Python test and Lean theorem compute these same integers.

## 5. Evaluated path kernels

Let $A,B,C$ be finite state sets. For a role profile $r$, let
$\Gamma_r(b,a)$ be the finite set of admitted paths from $a$ to $b$, with
cost $C_r(\gamma)$ and evaluator $E_r(\gamma)\in\{0,1\}$. For
$\lambda\ge 0$, define

$$
Z_r(b\mid a)
=\sum_{\gamma\in\Gamma_r(b,a)}
E_r(\gamma)\exp[-\lambda C_r(\gamma)].
$$

For proposal-weighted paths, an additional nonnegative proposal mass is
multiplied into each summand.

The composition hypotheses are:

- **G1:** composition is a bijection
  $$
  \bigsqcup_{b\in B}\Gamma_r(c,b)\times\Gamma_r(b,a)
  \longrightarrow \Gamma_r(c,a).
  $$
  Thus every admitted composite has one compatible segment pair, and every
  compatible pair produces exactly one admitted composite;
- **G2:** cost is additive across that decomposition;
- **G3:** the evaluator factorizes across the boundary;
- **G4:** proposal mass factorizes across the boundary when proposal weights
  are used.

\medskip

**Theorem 2 (conditional on G1--G4).** Under G1--G3, and also G4 in
the proposal-weighted case,

$$
Z_r(c\mid a)=\sum_{b\in B}Z_r(c\mid b)Z_r(b\mid a).
$$

**Proof.** Reindex the finite sum over $\Gamma_r(c,a)$ along the G1 bijection.
It becomes a sum over the displayed disjoint union of all compatible segment
pairs. G2 replaces each composite cost by the sum of its segment costs, so the
exponential is a product. G3 replaces each composite verdict by the product
of its segment verdicts, and G4 does the same for proposal mass when present.
Finite distributivity then turns, for each $b$, the sum over the Cartesian
product into $Z_r(c\mid b)Z_r(b\mid a)$. Summing those products over $b$ gives
the displayed identity. $\square$

When G3 is not assumed, the composite summand retains $E_r(\gamma_2\circ\gamma_1)$
while the product of segment partition functions produces $E_r(\gamma_2)E_r(\gamma_1)$.
Under G1, G2, and G4 when proposal weights are used, the same reindexing argument
yields the exact discrepancy identity:

$$
Z_r(c\mid a)-\sum_{b\in B} Z_r(c\mid b)Z_r(b\mid a) = \sum_{\text{compatible pairs}} w_r(\gamma_2,\gamma_1) \left[ E_r(\gamma_2\circ\gamma_1) - E_r(\gamma_2)E_r(\gamma_1) \right],
$$

where $w_r(\gamma_2,\gamma_1)=\exp[-\lambda(C_r(\gamma_2)+C_r(\gamma_1))]$ (multiplied
by proposal masses when applicable). The evaluated partition-function discrepancy is
thus directly the weighted sum of local evaluator defects $\Delta_E(\gamma_2,\gamma_1)$.

The Lean companion formally mechanizes the integer reindexing. If the composite weight list
equals the flattened products of the boundary weight lists, the composite sum
equals the sum over boundaries of left-sum times right-sum, and the residual
is zero. The Python implementation computes the G1 bijection and G2--G4 from
concrete finite path records and checks that integer identity on integer
lists. Real exponentials remain outside both mechanizations.

## 6. Quotient descent and carrier mixing

Let $X$ be a finite carrier with equivalence relation $\sim$, quotient map
$q:X\to X/{\sim}$, and evaluator $E:X\to\{0,1\}$.

**Theorem 3.** A function
$\bar E:X/{\sim}\to\{0,1\}$ satisfying $\bar E(q(x))=E(x)$ for every $x\in X$
exists if and only if

$$
x\sim y\Longrightarrow E(x)=E(y).
$$

Moreover, when such $\bar E$ exists, it is unique.

**Proof.** ($\Longrightarrow$) If $x\sim y$, then $q(x)=q(y)$. Applying $\bar E$ gives
$E(x)=\bar E(q(x))=\bar E(q(y))=E(y)$.
($\Longleftarrow$) Define $\bar E([x])=E(x)$ for each equivalence class $[x]\in X/{\sim}$.
The condition $x\sim y\implies E(x)=E(y)$ ensures $\bar E$ is well-defined.
By construction, $\bar E(q(x))=E(x)$ for all $x\in X$.
Uniqueness follows from the surjectivity of the quotient projection $q$:
if $\bar E'$ also satisfies $\bar E'(q(x))=E(x)$ for all $x$, then for every $[x]\in X/{\sim}$, $\bar E'([x])=\bar E'(q(x))=E(x)=\bar E([x])$. $\square$

**Corollary 3.1.** If equivalent elements receive different
verdicts, the evaluator does not descend to the quotient.


The Lean companion formally mechanizes this obstruction and includes an explicit inhabited
witness, so the hypotheses are not vacuous.

## 7. The six-role overlay

The overlay attaches the same record

$$
(r,\;e_1,\;e_2,\;e_g,\;\Delta_E,\;\text{context})
$$

to six role profiles. The role changes the context fields that must be
declared; it does not change the defect formula.

| role profile | question asked before comparing verdicts |
|---|---|
| finite obstruction | Are carrier, degree, comparison map, quotient gauge, and replay data declared? |
| foundations | Is this a diagnostic record rather than a decision record? |
| representation | Do the operation and transport witness match? |
| observer | Were both scores computed in the same observation envelope? |
| continuum shadow | Is a finite calculation being kept distinct from a limit statement? |
| action and alignment | Is residual feedback routed as feedback rather than relabeled as success? |

These questions specify what context must be recorded. They do not add a
seventh role and do not turn a declared field into evidence that a real
evaluator is adequate.

### 7.1 Observation envelope

**Proposition 4.** For the declared score
$S_w(R)=wR$, changing $w$ can change the score of the same residual.

**Proof.** Take $R=1$, $w=1$, and $w'=2$. Then
$S_w(R)=1\ne2=S_{w'}(R)$. $\square$

Scores from different envelopes should therefore not be compared without an
explicit transport rule.

### 7.2 Integration does not erase a defect

**Proposition 5 (fixed observation).** If integration
leaves $(e_1,e_2,e_g)$ unchanged, it leaves $\Delta_E$ unchanged.

**Proof.** $\Delta_E$ is a function of that triple. Substituting the same
arguments gives the same value. $\square$

## 8. What is recorded

For each finite observation the package records the two local verdicts, the
composite verdict, their signed difference, the role in which the comparison
was made, and enough context to tell whether the compared quantities share a
carrier, transport rule, and observation scale. A zero says only that the
composite verdict equals the product of the local verdicts for that record.
When pointwise defects cancel, the pointwise list is retained. When an
evaluator varies inside a declared equivalence class, quotient evaluation is
refused. This paper defines no repair procedure or cochain complex.

## 9. Reproducible implementation

The package contains:

- a Python reference implementation of the finite records and guards;
- tests for valid inputs, invalid inputs, and twelve break-and-recover
  mutations;
- seven teaching and verification notebooks, each with plots and optional
  interactive exploration;
- a Lean 4 library for the integer identities and quotient
  statements, plus a current theorem-level axiom report;
- deterministic scripts for figures, the manuscript build, checksums, and the
  release archive.

An earlier omnibus snapshot is retained outside the public deposit for
provenance. It is excluded from the archive and from current claim evidence.

## 10. Falsifiability

The model is directly testable. Any of the following would refute a stated
result or expose an implementation mismatch:

1. a binary verdict triple produces a defect outside $\{-1,0,1\}$;
2. a finite sample violates $G-L=D$;
3. the implementation accepts a non-binary verdict;
4. a quotient evaluator is produced despite two equivalent elements receiving
   different verdicts;
5. the implementation reports G1, G2, G3, or G4 as satisfied although the
   concrete path records violate the corresponding condition; or
6. a notebook result cannot be reproduced from the archived environment.

A failed hypothesis places the record outside the theorem’s applicable case; it
does not refute the conditional theorem. Mathematical counterexamples,
implementation discrepancies, and environmental reproducibility failures are
distinct outcomes.

The executable constant-output check is only a basic falsifier; the stronger
task-specific adequacy obligation stated in Section 2 remains open.

## 11. Related work

Weighted automata provide the standard algebraic setting for finite paths with
semiring-valued weights. Kleisli's construction and Moggi's computational use
of monads explain why effectful composition is naturally expressed through
Kleisli arrows. The sheaf-theoretic account of contextuality by Abramsky and
Brandenburger is a nearby local-to-global obstruction language, but this paper
does not identify its binary evaluator defect with contextuality or sheaf
cohomology. Contract-based design supplies a neighboring language for
assumption-sensitive composition. Recent cellular-sheaf work on distributed
multi-agent coordination and system identification studies richer dynamical
and topological settings; the present contribution is only a finite,
replayable evaluator overlay.

## 12. Conclusion

The useful object is the signed discrepancy
$\Delta_E=e_g-e_1e_2$. It survives changes of role name, exposes
local-green/global-red traces, adds linearly over finite samples, and refuses
quotient descent when an evaluator varies inside an equivalence class.
Everything else in the overlay is context: which carrier, transport,
observation envelope, and replay data make a comparison meaningful.

## References

1. H. Kleisli, “Every standard construction is induced by a pair of adjoint
   functors,” *Proceedings of the American Mathematical Society* 16(3),
   544--546 (1965).
   [doi:10.1090/S0002-9939-1965-0177024-4](https://doi.org/10.1090/S0002-9939-1965-0177024-4)
2. E. Moggi, “Notions of computation and monads,” *Information and
   Computation* 93(1), 55--92 (1991).
   [doi:10.1016/0890-5401(91)90052-4](https://doi.org/10.1016/0890-5401(91)90052-4)
3. M. Droste, W. Kuich, and H. Vogler, eds., *Handbook of Weighted
   Automata*, Springer (2009).
   [doi:10.1007/978-3-642-01492-5](https://doi.org/10.1007/978-3-642-01492-5)
4. S. Abramsky and A. Brandenburger, “The sheaf-theoretic structure of
   non-locality and contextuality,” *New Journal of Physics* 13, 113036
   (2011). [doi:10.1088/1367-2630/13/11/113036](https://doi.org/10.1088/1367-2630/13/11/113036)
5. A. Benveniste et al., “Contracts for system design,” *Foundations and
   Trends in Electronic Design Automation* 12(2--3), 124--400 (2018).
   [doi:10.1561/1000000053](https://doi.org/10.1561/1000000053)
6. T. Hanks et al., “Distributed Multi-agent Coordination over Cellular
   Sheaves” (2025). [arXiv:2504.02049](https://arxiv.org/abs/2504.02049)
7. N. Anwer, H. Riess, and M. Hale, “Multi-Agent System Identification with
   Nonlinear Sheaf Diffusion” (2026). [arXiv:2605.11204](https://arxiv.org/abs/2605.11204)
8. J. H. Carroll, “Local Green, Global Red I: Evaluated Path Kernels for
   Composed Agent Reliability,” preprint (2026).
   [doi:10.5281/zenodo.20675803](https://doi.org/10.5281/zenodo.20675803)
