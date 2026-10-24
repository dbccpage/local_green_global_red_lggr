# Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction

**Author:** Jeremy H. Carroll

**Date:** 2026-10-15

**Version:** 0.1.1

## Abstract

Evaluator agreements across finite stages of an inverse system need not imply the existence of a solution in the original carrier. On a finite chain, one element of the last stage pulls back along the transition maps to a nonempty compatible thread. The general statement that a cofiltered inverse limit of nonempty finite sets is nonempty is cited from Stacks Tag 086J. Thread existence does not imply realization by an element of the original carrier: in an explicit $2$-adic arithmetic family, the congruence $3x+1 \equiv 0 \pmod{2^n}$ admits an exact solution $x_n = -\sum_{k=0}^{n-1}(-2)^k$ at every stage $n$ and forms a compatible thread, yet no integer satisfies all stages simultaneously because $2^n \mid 3x+1$ for all $n \ge 1$ forces $x = -1/3 \notin \mathbb{Z}$. The unique solution lives in the completion $\mathbb{Z}_2$. We formulate a general reflection image criterion: completed solutions descend to original-carrier solutions if and only if they belong to the image of the canonical reflection map $\eta$. For a finite list of families, the overlap defect $2(B-k^*)$ equals the dual value used by the rational certificate, and it vanishes when a common element exists. The general statement that the Mittag–Leffler condition implies $R^1 \varprojlim A_n = 0$ is cited from Stacks Tag 07KV.

---

## 1. Problem and Relation to the LGGR Series

The foundational papers in this series address evaluator composition over a fixed finite observation presentation:

- **LGGR I** [1] examines sample identities, weighted path-kernel composition, and carrier collisions under binary evaluator defects.
- **LGGR II** [2] establishes the organizational composition of boundary owners, distinguishing definitional sufficiency from true factorization and identifying quotient-level boundary defects.
- **LGGR III** [3] layers this defect across six explicit system roles under finite sums and quotient descent.
- **LGGR V** [4] characterizes linear observation blind spots, showing that full interface coverage can leave an undetected subspace $\ker Q$ whenever $\operatorname{im} D \cap \ker Q \neq \{0\}$.
- **LGGR VI** [5] establishes that downstream nonlinear post-processing cannot recover directions already erased by an observation operator $Q$.

Each of those results operates on a single, fixed stage of observation. **LGGR IV** addresses an orthogonal mathematical question:

> *Can a system appear solvable across an unbounded tower of finite observation stages, while admitting no solution in the original carrier—even though a valid solution emerges after completion?*

When an engineered system or formal evaluator is subjected to progressively refined testing stages $\pi_n: X \to X_n$, one observed outcome is that every finite stage passes: for every $n$, there exists a state $x_n$ satisfying the $n$-th requirement. If these requirements are mutually compatible, one might hope that a global state $x \in X$ exists satisfying the requirements across all stages simultaneously.

This paper establishes that such an inference is invalid in general:

1. **Local Green**: Every finite refinement stage $n$ admits a valid witness.
2. **Global Red in the Original Carrier**: No element in the original carrier $X$ satisfies all stages.
3. **Completion Green**: A valid global witness exists in a completion $\widehat{X}$.

We show that solving a problem in the completion does not retroactively solve the problem in the original carrier. We formalize this distinction through a reflection image criterion and clarify the homological boundary where lifting obstructions vanish.

---

## 2. Finite-Stage Descent and the Moving-Witness Criterion

Let $X$ denote a state space, and let $I$ be a directed index set. Consider an inverse system of quotient or observation projections:

\[
\{\pi_i: X \longrightarrow X_i\}_{i \in I}.
\]

We formalize what it means for a defect or property to factor through a finite stage.

### Definition 2.1 (Finite Descent)

Let $D: X \to Y$ be an evaluation or defect function. We say that $D$ has **finite descent** through the family $\{\pi_i\}_{i \in I}$, denoted $\operatorname{FinDesc}(D)$, if there exists an index $i \in I$ and a function $d_i: X_i \to Y$ such that

\[
D = d_i \circ \pi_i.
\]

When $D = d_i \circ \pi_i$, any two states $x, y \in X$ that agree at stage $i$ (that is, $\pi_i(x) = \pi_i(y)$) must satisfy $D(x) = D(y)$. The failure of finite descent is characterized by the following criterion.

### Theorem 2.1 (Moving-Witness Collision Criterion)

Let $X$ and $Y$ be sets with $Y$ nonempty, and let $\{\pi_i: X \to X_i\}_{i \in I}$ be a family of surjective observation maps. A defect $D: X \to Y$ fails to have finite descent through $\{\pi_i\}_{i \in I}$ if and only if for every stage $i \in I$, there exists a pair of states $x_i, y_i \in X$ such that

\[
\pi_i(x_i) = \pi_i(y_i) \quad \text{and} \quad D(x_i) \neq D(y_i).
\]

*Proof.*

- $(\implies)$ If $\operatorname{FinDesc}(D)$ fails, then for every $i \in I$, no function $d_i: X_i \to Y$ satisfies $D = d_i \circ \pi_i$. Because each $\pi_i$ is surjective, a function $d_i: X_i \to Y$ satisfying $D = d_i \circ \pi_i$ exists if and only if $D$ is constant on the fibers of $\pi_i$ (that is, $\pi_i(x) = \pi_i(y) \implies D(x) = D(y)$ for all $x, y \in X$). Without surjectivity, fiber constancy only defines $d_i$ on the image $\operatorname{im} \pi_i \subseteq X_i$, requiring an extension to $X_i \setminus \operatorname{im} \pi_i$ using $Y \neq \emptyset$. Under surjectivity (or extension), the failure of factorization implies that for every $i \in I$, some fiber contains at least two points on which $D$ takes different values: that is, states $x_i, y_i \in X$ with $\pi_i(x_i) = \pi_i(y_i)$ and $D(x_i) \neq D(y_i)$.
- $(\impliedby)$ Conversely, if such a pair $(x_i, y_i)$ exists for every $i \in I$, then no function $d_i: X_i \to Y$ can satisfy both $d_i(\pi_i(x_i)) = D(x_i)$ and $d_i(\pi_i(y_i)) = D(y_i)$, since $\pi_i(x_i) = \pi_i(y_i)$ forces $d_i(\pi_i(x_i)) = d_i(\pi_i(y_i))$ whereas $D(x_i) \neq D(y_i)$. Hence no stage $i$ factors $D$, and $\operatorname{FinDesc}(D)$ is false. $\square$

The Lean development formalizes this equivalence for a finite complete state list, using one default output value to extend a stage map off its image (`LggrIV.finite_notFinDesc_iff_collisions`). It does not treat an arbitrary non-enumerated carrier as a separate theorem.

### Remark 2.1 (Moving Witnesses vs. Fixed Collisions)

The pairs $(x_i, y_i)$ depend on the stage $i$. If the projective family $\{\pi_i\}_{i \in I}$ is **jointly separating**—meaning that for every pair $x \neq y$ in $X$, there exists some index $j \in I$ such that $\pi_j(x) \neq \pi_j(y)$—then no *fixed* pair $(x, y)$ can satisfy $\pi_i(x) = \pi_i(y)$ for all $i \in I$. Thus, failure of finite descent in a separating system is necessarily driven by moving witnesses: as the stage $i$ deepens, the colliding pair $(x_i, y_i)$ must shift.

---

## 3. A Non-Obstruction Theorem for Finite Repair Fibers

Before demonstrating how global solvability can fail, we establish a structural regime where failure does not arise: namely, when the repair sets at each finite stage are finite and nonempty.

Let $(I, \le)$ be a directed partially ordered set. An inverse system of sets over $I$ consists of sets $\{S_i\}_{i \in I}$ together with transition maps $f_{ij}: S_j \to S_i$ for all $i \le j$, satisfying $f_{ii} = \operatorname{id}_{S_i}$ and $f_{ik} = f_{ij} \circ f_{jk}$ for all $i \le j \le k$.

The inverse limit is the set of compatible threads:

\[
\varprojlim_{i \in I} S_i = \left\{ (s_i)_{i \in I} \in \prod_{i \in I} S_i \;\middle|\; \forall i \le j,\; s_i = f_{ij}(s_j) \right\}.
\]

### Theorem 3.1 (Finite Fiber Coherence; Stacks Tag 086J)

Let $(I, \le)$ be a directed partially ordered set, and let $\{S_i, f_{ij}\}$ be an inverse system of sets. If each $S_i$ is **finite and nonempty**, then the inverse limit is nonempty:

\[
\varprojlim_{i \in I} S_i \neq \emptyset.
\]

*Proof.*
Equip each finite set $S_i$ with the discrete topology. Because $S_i$ is finite, it is compact and Hausdorff. By Tychonoff's theorem, the product $\prod_{i \in I} S_i$ is compact and Hausdorff. For each pair $i \le j$, the condition $E_{ij} = \{(s_k) \in \prod S_k \mid s_i = f_{ij}(s_j)\}$ is a closed subset.

For any finite subset of indices $J \subseteq I$, choose an upper bound $m \in I$ such that $j \le m$ for all $j \in J$. Since $S_m$ is nonempty, choose $s_m \in S_m$ and set $s_j = f_{jm}(s_m)$ for $j \in J$. This shows that any finite intersection $\bigcap_{i \le j \in J} E_{ij}$ is nonempty. By the finite intersection property of compact spaces,

\[
\varprojlim_{i \in I} S_i = \bigcap_{i \le j} E_{ij} \neq \emptyset. \quad \square
\]

The Lean companion formalizes only the finite-chain case (`LggrIV.finite_chain_limit_nonempty`): one element of the last stage, pulled back along a finite list of transition functions, yields a nonempty compatible thread. Tag 086J remains a classical citation, and the topological compactness argument above is cited from the classical literature.

### Corollary 3.1 (Non-Obstruction for Finite Diagnostic Repair)

Suppose an evaluator pipeline defines for each stage $i$ a set of valid repairs $R_i \subseteq X_i$. If each $R_i$ is finite and nonempty, and transition maps preserve validity ($f_{ij}(R_j) \subseteq R_i$), then there exists a coherent global repair sequence $(r_i)_{i \in I} \in \varprojlim R_i$.

Consequently, an obstruction between finite-stage solvability and global thread existence requires infinite fibers at the finite stages, whereas an obstruction between thread existence and original-carrier descent persists even when all finite repair sets are singletons.
---

## 4. The Explicit $3x+1 \equiv 0 \pmod{2^n}$ Arithmetic Counterexample

We now construct an elementary arithmetic inverse system that illustrates the triple phenomenon:
$$\boxed{ \text{finite-stage green} \;+\; \text{original-carrier red} \;+\; \text{completion green} }$$

### 4.1 System Definition

Let the original carrier be the ring of integers:

\[
X = \mathbb{Z}.
\]

For each integer $n \ge 1$, let the $n$-th observation stage be the residue ring:

\[
X_n = \mathbb{Z}/2^n\mathbb{Z},
\]

with canonical projection $\pi_n: \mathbb{Z} \to \mathbb{Z}/2^n\mathbb{Z}$ given by $\pi_n(x) = x \bmod 2^n$. The transition maps $f_{nm}: \mathbb{Z}/2^m\mathbb{Z} \to \mathbb{Z}/2^n\mathbb{Z}$ for $m \ge n$ are the standard quotient projections.

The goal at each stage $n$ is to satisfy the linear affine congruence:

\[
3x + 1 \equiv 0 \pmod{2^n}.
\]

### 4.2 Finite-Stage Solvability (Local Green)

For each $n \ge 1$, define the integer:

\[
x_n = -\sum_{k=0}^{n-1} (-2)^k.
\]

### Proposition 4.1 (Exact Finite-Stage Solution)

For every $n \ge 1$, the integer $x_n$ satisfies:

\[
3x_n + 1 = (-2)^n.
\]

In particular, $2^n \mid (3x_n + 1)$, so $\pi_n(x_n)$ is an exact solution in $\mathbb{Z}/2^n\mathbb{Z}$.

*Proof.*
Recall the geometric series identity for any real or algebraic variable $t$:
\[
(1 - t)\sum_{k=0}^{n-1} t^k = 1 - t^n.
\]
Setting $t = -2$, we obtain $1 - t = 1 - (-2) = 3$. Therefore:
\[
3 \sum_{k=0}^{n-1} (-2)^k = 1 - (-2)^n.
\]
Multiplying through by $-1$:
\[
3 \left( -\sum_{k=0}^{n-1} (-2)^k \right) = (-2)^n - 1.
\]
Substituting the definition $x_n = -\sum_{k=0}^{n-1} (-2)^k$:
\[
3x_n = (-2)^n - 1 \iff 3x_n + 1 = (-2)^n.
\]
Because $(-2)^n = (-1)^n 2^n$, the term $3x_n + 1$ is an exact multiple of $2^n$:
\[
3x_n + 1 \equiv 0 \pmod{2^n}. \quad \square
\]

### Proposition 4.2 (Compatibility Across Stages)

The sequence of residues $(\pi_n(x_n))_{n \ge 1}$ forms a compatible thread in $\varprojlim \mathbb{Z}/2^n\mathbb{Z}$.

*Proof.*
For any $n \ge 1$:
\[
x_{n+1} - x_n = -\sum_{k=0}^n (-2)^k - \left( -\sum_{k=0}^{n-1} (-2)^k \right) = -(-2)^n.
\]
Since $-(-2)^n = (-1)^{n+1} 2^n$, we have $x_{n+1} \equiv x_n \pmod{2^n}$. Thus, under the projection $f_{n,n+1}: \mathbb{Z}/2^{n+1}\mathbb{Z} \to \mathbb{Z}/2^n\mathbb{Z}$,
\[
f_{n,n+1}(\pi_{n+1}(x_{n+1})) = \pi_n(x_n). \quad \square
\]

The first four terms of this sequence illustrate the progression:

- $n = 1$: $x_1 = -1 \implies 3(-1) + 1 = -2 \equiv 0 \pmod 2$.
- $n = 2$: $x_2 = -(1 - 2) = 1 \implies 3(1) + 1 = 4 \equiv 0 \pmod 4$.
- $n = 3$: $x_3 = -(1 - 2 + 4) = -3 \implies 3(-3) + 1 = -8 \equiv 0 \pmod 8$.
- $n = 4$: $x_4 = -(1 - 2 + 4 - 8) = 5 \implies 3(5) + 1 = 16 \equiv 0 \pmod{16}$.

Every finite observation stage evaluates to zero defect (Local Green).

### 4.3 Original-Carrier Failure (Global Red)

### Theorem 4.1 (Impossibility of an Integral Global Solution)

There exists no integer $x \in \mathbb{Z}$ such that

\[
3x + 1 \equiv 0 \pmod{2^n} \quad \text{for all } n \ge 1.
\]

*Proof.*
Suppose there exists $x \in \mathbb{Z}$ satisfying $3x + 1 \equiv 0 \pmod{2^n}$ for all $n \ge 1$. This implies that $2^n$ divides the fixed integer $3x + 1$ for every positive integer $n$:

\[
\forall n \ge 1, \quad 2^n \mid (3x + 1).
\]

In the integers, the only element divisible by $2^n$ for all $n \ge 1$ is $0$. Therefore:

\[
3x + 1 = 0 \implies x = -\frac{1}{3}.
\]

However, $-1/3 \notin \mathbb{Z}$. Thus no such integer exists. $\square$

### 4.4 Completion Solvability (Completion Green)

The inverse limit of the finite residue rings $\mathbb{Z}/2^n\mathbb{Z}$ defines the ring of $2$-adic integers:

\[
\mathbb{Z}_2 = \varprojlim_{n \ge 1} \mathbb{Z}/2^n\mathbb{Z}.
\]

There is a canonical injective ring homomorphism $\eta: \mathbb{Z} \to \mathbb{Z}_2$ mapping an integer to its coherent sequence of residues $(\pi_n(x))_{n \ge 1}$.

### Classical record 4.3 (existence and uniqueness in the 2-adic completion)

This argument is cited from standard $2$-adic analysis [9].

In $\mathbb{Z}_2$, the equation $3x + 1 = 0$ has a unique solution:

\[
x_\infty = -\frac{1}{3} \in \mathbb{Z}_2.
\]

Moreover, the thread $(\pi_n(x_n))_{n \ge 1}$ converges $2$-adically to $x_\infty$.

*Proof.*
The prime $2$ does not divide $3$. In the ring $\mathbb{Z}_2$, an element is a unit if and only if its residue modulo $2$ is nonzero. Since $3 \equiv 1 \pmod 2$, $3$ is a unit in $\mathbb{Z}_2$. Hence the linear equation $3x + 1 = 0$ has the unique solution $x = -3^{-1} = -1/3$.

The sequence of partial sums $x_n = -\sum_{k=0}^{n-1} (-2)^k$ satisfies:
\[
|x_n - x_\infty|_2 = \left| -\frac{1 - (-2)^n}{3} - \left(-\frac{1}{3}\right) \right|_2 = \left| \frac{(-2)^n}{3} \right|_2 = \frac{1}{2^n} \xrightarrow{n \to \infty} 0.
\]
Thus $x_n \to -1/3$ in $\mathbb{Z}_2$. $\square$

---

## 5. Completion-Relative Versus Original-Carrier Repair

The arithmetic example illustrates the structural hazard of completion laundering: an evaluator observing passing checks at every stage $n$ concludes that the system is locally valid everywhere, and a solver operating on the completion finds an exact limit point $-1/3 \in \mathbb{Z}_2$. However, if the operational system requires a solution in $\mathbb{Z}$, the system remains red.

### 5.1 The Reflection Image Criterion

Let $X$ be an arbitrary carrier space, and let $\eta: X \to \widehat{X}$ denote its completion or limit embedding with respect to an inverse family of projections.

Let $R_X \subseteq X$ denote the predicate of valid states in the original carrier, and let $R_{\widehat{X}} \subseteq \widehat{X}$ denote the extended predicate in the completion. We require that the extension is faithful on the image of $X$:

\[
\eta(R_X) = R_{\widehat{X}} \cap \operatorname{im}(\eta).
\]

### Criterion 5.1 (Reflection Descent Criterion)

Let $\hat{r} \in R_{\widehat{X}}$ be a valid solution in the completion. Then $\hat{r}$ descends to a valid solution in the original carrier $X$ if and only if

\[
\hat{r} \in \operatorname{im}(\eta).
\]

When $\hat{r} \notin \operatorname{im}(\eta)$, the element $\hat{r}$ constitutes a **completion-only witness**.

### 5.2 The Completion Residual

For a general completion, the primitive residual witnessing original-carrier obstruction is given by the set membership failure:

\[
\operatorname{Res}_{\text{refl}}(\hat{r}) = \hat{r} \notin \operatorname{im}(\eta).
\]

When $X$ and $\widehat{X}$ possess abelian group structures and $\eta: X \hookrightarrow \widehat{X}$ is an injective homomorphism, the obstruction can be packaged additively as a non-trivial coset in the quotient group:

\[
[\hat{r}] \in \widehat{X} / \operatorname{im}(X).
\]

In our $2$-adic example, the element $-1/3 \in \mathbb{Z}_2$ defines a nonzero residual class in the quotient group $\mathbb{Z}_2 / \mathbb{Z}$.

### 5.3 Operational Rule: No Completion Laundering

We state the operational discipline required to prevent invalid claim promotion:

> **Principle of No Completion Laundering**: Demonstrating that every finite refinement stage $n$ admits a witness, or demonstrating that a coherent witness exists in a completion $\widehat{X}$, does not establish the existence of a solution in the original carrier $X$. A completed witness cannot be promoted to an operational certificate unless its reflection descent $\hat{r} \in \operatorname{im}(\eta)$ is explicitly verified.

---

## 6. Scope and Non-Claims

To ensure claim hygiene, we explicitly fence the interpretive boundaries of this paper:

1. **Diagnostic Geometry, Not Physics or Ontology**: The divergence between $\mathbb{Z}$ and $\mathbb{Z}_2$ is a property of projective limits and metric completions. It does not model physical spacetime quantization, ontological emergence, or quantum measurement.
2. **Representation Limits**: The existence of moving-witness collisions under $\neg \operatorname{FinDesc}(D)$ reflects the lossiness of finite stages, not an inherent defect in the underlying mathematical reality.
3. **No Continuum Extrapolation**: Passing a countable sequence of finite tests provides evidence only for those tests. It does not authorize unverified assertions about continuous limits.

---

## Appendix: Derived Limits and the Mittag–Leffler Vanishing Theorem

In this appendix, we place the lifting obstruction into the standard framework of homological algebra. We clarify the role of the Mittag–Leffler condition, correcting a common misconception regarding the derived inverse limit $R^1 \varprojlim$.

### A.1 The Inverse System Exact Sequence

Let $0 \to A_n \xrightarrow{\iota_n} B_n \xrightarrow{p_n} C_n \to 0$ be a sequence of short exact sequences of abelian groups, compatible with transition maps:

```text
0 ---> A_{n+1} ---> B_{n+1} ---> C_{n+1} ---> 0
         |              |              |
         v              v              v
0 --->   A_n   --->   B_n   --->   C_n   ---> 0
```

Applying the left-exact inverse limit functor $\varprojlim$ yields the standard six-term exact sequence:

\[
0 \longrightarrow \varprojlim A_n \longrightarrow \varprojlim B_n \longrightarrow \varprojlim C_n \xrightarrow{\;\delta\;} R^1 \varprojlim A_n \longrightarrow R^1 \varprojlim B_n \longrightarrow R^1 \varprojlim C_n \longrightarrow 0.
\]

Here, $R^1 \varprojlim A_n$ denotes the first derived limit of the inverse system $\{A_n\}$.

### A.2 The Lifting Obstruction Class

Suppose we are given a compatible sequence of target requirements $(c_n) \in \varprojlim C_n$.

- At each finite stage $n$, surjectivity of $p_n$ ensures that there exists some $b_n \in B_n$ lifting $c_n$ (Finite-Stage Green).
- However, the choices of $b_n$ may not be compatible under transition maps: $f_{n,n+1}(b_{n+1})$ need not equal $b_n$.
- The connecting homomorphism $\delta: \varprojlim C_n \to R^1 \varprojlim A_n$ maps the compatible family $(c_n)$ to an obstruction class:

\[
\omega = \delta((c_n)) \in R^1 \varprojlim A_n.
\]

By exactness of the sequence, the compatible family $(c_n)$ lifts to a global coherent element $(b_n) \in \varprojlim B_n$ if and only if $\omega = 0$.

### A.3 The Mittag–Leffler Condition (Stacks Tag 07KV, Tag 0597)

### Definition A.1 (Mittag–Leffler Condition)

An inverse system of abelian groups $\{A_n, f_{nm}\}$ satisfies the **Mittag–Leffler (ML) condition** if for every $n$, the descending chain of images

\[
\operatorname{im}(f_{n, n+k}) \subseteq A_n \quad (k \ge 0)
\]

eventually stabilizes: that is, there exists $k_0$ such that for all $k \ge k_0$, $\operatorname{im}(f_{n, n+k}) = \operatorname{im}(f_{n, n+k_0})$.

### Theorem A.1 (Mittag–Leffler Vanishing; Stacks Tag 07KV)

If $\{A_n\}$ is an inverse system of abelian groups indexed by the natural numbers that satisfies the Mittag–Leffler condition, then:

\[
R^1 \varprojlim A_n = 0.
\]

*Proof.* See Stacks Project, Tag 07KV. $\square$

The Lean companion formalizes only the finite overlap identity (`LggrIV.overlap_dual_residual`): for a finite list of families the primal defect $2(B-k^*)$ equals the dual value $\mu - \sum \alpha_i$, and a nonempty list with $k^*=B$ has a common element. Tag 07KV remains a classical citation.

### Corollary A.1 (Vanishing of the Lifting Obstruction)

If the kernel system $\{A_n\}$ satisfies the Mittag–Leffler condition, then every compatible family $(c_n) \in \varprojlim C_n$ lifts to a compatible family $(b_n) \in \varprojlim B_n$.

### Remark A.1 (Correction to the Role of Mittag–Leffler)

The Mittag–Leffler condition does *not* create an obstruction; rather, it ensures the *absence* of a lifting obstruction ($R^1 \varprojlim A_n = 0$). Consequently, coherent lifting failure (Local Green, Global Red in an abelian tower) can occur only when the kernel transition system $\{A_n\}$ fails the Mittag–Leffler condition.

### A.4 The Direct Arithmetic Bridge: $R^1 \varprojlim (2^n \mathbb{Z}) \cong \mathbb{Z}_2 / \mathbb{Z}$

The derived-limit exact sequence of Section A.1 applies directly to the paper's primary arithmetic system. For each $n \ge 1$, consider the short exact sequence of abelian groups:

\[
0 \longrightarrow 2^n \mathbb{Z} \longrightarrow \mathbb{Z} \longrightarrow \mathbb{Z}/2^n \mathbb{Z} \longrightarrow 0,
\]

equipped with standard inclusion homomorphisms on the submodules $2^n \mathbb{Z}$, identity transitions on the constant tower $\mathbb{Z}$, and modular reductions on the residue rings $\mathbb{Z}/2^n \mathbb{Z}$.

Evaluating the projective limits:
1. $\varprojlim 2^n \mathbb{Z} = \bigcap_{n \ge 1} 2^n \mathbb{Z} = \{0\}$.
2. The constant tower $\{\mathbb{Z}, \operatorname{id}\}$ satisfies the Mittag–Leffler condition (its transition images are identically $\mathbb{Z}$), hence $\varprojlim \mathbb{Z} = \mathbb{Z}$ and $R^1 \varprojlim \mathbb{Z} = 0$.
3. $\varprojlim \mathbb{Z}/2^n \mathbb{Z} = \mathbb{Z}_2$ (the ring of $2$-adic integers).

Substituting these evaluations into the six-term derived limit exact sequence yields:

\[
0 \longrightarrow 0 \longrightarrow \mathbb{Z} \xrightarrow{\;\eta\;} \mathbb{Z}_2 \xrightarrow{\;\delta\;} R^1 \varprojlim (2^n \mathbb{Z}) \longrightarrow 0.
\]

Consequently, as abelian groups:

\[
R^1 \varprojlim (2^n \mathbb{Z}) \cong \mathbb{Z}_2 / \mathbb{Z}.
\]

The connecting homomorphism $\delta: \mathbb{Z}_2 \to R^1 \varprojlim (2^n \mathbb{Z})$ is the canonical quotient projection modulo the embedded integers $\eta(\mathbb{Z})$.

In our arithmetic system, the unique $2$-adic solution $x_\infty = -1/3 \in \mathbb{Z}_2$ does not lie in the image of $\mathbb{Z}$. Therefore:

\[
\delta(x_\infty) = [-1/3] \neq 0 \in R^1 \varprojlim (2^n \mathbb{Z}).
\]

Thus, the completion residual $\hat{r} \notin \operatorname{im}(\eta)$ and the non-vanishing derived limit lifting obstruction $\delta(x_\infty) \neq 0$ coincide on the paper's primary system.

At the level of finite representatives, the chosen stage solutions $(x_n)_{n \ge 1}$ satisfy the step discrepancies:
\[
x_n - x_{n+1} = (-2)^n \in 2^n \mathbb{Z}.
\]
If these step discrepancies were trivialized by compatible kernel corrections $k_n \in 2^n \mathbb{Z}$, the corrected sequence $x_n' = x_n - k_n$ would stabilize to a single integer $x \in \mathbb{Z}$ satisfying $3x + 1 \equiv 0 \pmod{2^n}$ for all $n \ge 1$, which is ruled out by Theorem 4.1.

*Note on quotient topology:* The isomorphism $R^1 \varprojlim (2^n \mathbb{Z}) \cong \mathbb{Z}_2 / \mathbb{Z}$ is an algebraic group isomorphism. Because $\mathbb{Z}$ is dense in $\mathbb{Z}_2$ under the $2$-adic metric, the quotient does not carry a Hausdorff metric; non-zero cosets admit representatives arbitrarily close to $0$ in metric distance. This separation reinforces Criterion 5.1: finite-stage or metric proximity cannot substitute for exact reflection descent into the original operational carrier.

---

## References

1. Carroll, J. H. *Local Green, Global Red I: Evaluated Path Kernels for Composed Agent Reliability.* Zenodo preprint, 2026. DOI: <https://doi.org/10.5281/zenodo.22881911>.
2. Carroll, J. H. *Local Green, Global Red II: Organizational Evaluator Gluing.* Zenodo preprint, 2026. DOI: <https://doi.org/10.5281/zenodo.22882042>.
3. Carroll, J. H. *Local Green, Global Red III: A finite evaluator overlay across six system roles.* Zenodo preprint, 2026.
4. Carroll, J. H. *Local Green, Global Red V: Linear Observation Blind Spots and Kernel Intersections.* Zenodo preprint, 2026.
5. Carroll, J. H. *Local Green, Global Red VI: Nonlinear Aggregation and Adjoint Probing.* Zenodo preprint, 2026.
6. The Stacks Project Authors. *Tag 086J: Inverse limits of finite nonempty sets.* <https://stacks.math.columbia.edu/tag/086J>.
7. The Stacks Project Authors. *Tag 07KV: Derived inverse limits and the Mittag–Leffler condition.* <https://stacks.math.columbia.edu/tag/07KV>.
8. The Stacks Project Authors. *Tag 0597: Mittag–Leffler systems of sets.* <https://stacks.math.columbia.edu/tag/0597>.
9. Koblitz, N. *p-adic Numbers, p-adic Analysis, and Zeta-Functions.* Graduate Texts in Mathematics, vol. 58, Springer, 1984.
10. Weibel, C. A. *An Introduction to Homological Algebra.* Cambridge Studies in Advanced Mathematics, vol. 38, Cambridge University Press, 1994.
