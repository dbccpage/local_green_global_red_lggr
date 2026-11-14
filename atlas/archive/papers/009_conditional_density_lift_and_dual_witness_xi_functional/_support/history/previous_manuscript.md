# Conditional Density Lift and Dual-Witness Xi Functional

**Monograph Series:** Monograph 009 (Finite Obstruction Calculus Program)  
**Author:** Jeremy H. Carroll  
**Date:** 2026-10-08  
**Version:** 2.0.3  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)  
**Status:** RELEASED  
**DOI:** 10.5281/zenodo.20192297  

---

## Abstract

This paper defines a secondary diagnostic functional, $\Xi$, for an $\ell^1$-primary finite obstruction framework. The construction begins with the quotient obstruction magnitude $\Phi_1$, inherited from the finite cochain complex $C^0(P) \to C^1(P)$, and introduces a conditional $\ell^1$-to-density lift using a normalized square-root map that preserves normalized absolute coordinate weights and real amplitudes without independent phases. The real vector retains coordinate signs, while the rank-1 density operator discards total cochain mass and the common global sign. For obstructed classes ($\Phi_1 > 0$), canonical primal and dual representatives are selected via successive coordinate minimization on the compact optimal face relative to a declared edge ordering. $\Xi$ is then defined as the trace-norm distance between the density of the selected primal residual $h_1^*$ and the density of the optimal dual witness $\phi^*$. On unobstructed classes ($\Phi_1 = 0$), the lift is undefined and $\Xi = 0$ by declared convention. For any genuine optimal primal-dual pair with $\Phi_1 > 0$, linear programming complementary slackness forces $\Xi \le \sqrt{1 - 1/\|\varphi^*\|_1} \le \sqrt{1 - 1/m} < 1$, precluding orthogonality ($\Xi = 1$), while $\Xi = 0$ requires magnitude uniformity across the common support in addition to sign agreement. The evaluator integrates $\Xi$ via a tiered priority admission policy with threshold gating: $\Xi$ is evaluated only when $\Phi_1$ and $\Gamma_2$ are tied within tolerance, subject to the boundary guardrail $R_{cl} \le R_{\max}$.

---

## 1. Introduction and Architectural Motivation

In discrete constraint systems and combinatorial optimization, error detection typically terminates in scalar norms or boundary residual metrics. Earlier work in this programme established the quotient obstruction magnitude $\Phi_1([\omega_1]) = \min_{\alpha} \|\omega_1 - d_0 \alpha\|_1$ as the primary quotient norm of unsolvable cycle defects. However, when evaluating competing operator proposals or parameter adjustments, multiple candidate configurations frequently produce identical primary obstruction signatures $(\Phi_1, \Gamma_2)$, where $\Gamma_2$ denotes an externally supplied secondary curvature / closure residual diagnostic from the cochain complex.

Relying solely on $\Phi_1$ leaves an optimization or repair policy blind to finer geometric distinctions among candidate solutions having equal quotient norm. To address this degeneracy without corrupting primary quotient properties, this paper introduces the **Conditional Density Lift** and the secondary **Dual-Witness $\Xi$ Functional**, alongside an externally supplied boundary ratio diagnostic $R_{cl}$ evaluated against a threshold $R_{\max}$.

```
                +-----------------------------------------+
                |   Combinatorial Cochain Space C^1(P)    |
                +-----------------------------------------+
                     |                               |
        Primal Residual h*                     Dual Witness phi*
        ||h*||_1 = Phi_1 > 0                   ||phi*||_inf <= 1, div=0
                     |                               |
                     v                               v
             +---------------+               +---------------+
             |  Density Lift |               |  Density Lift |
             |   rho(h*)     |               |   rho(phi*)   |
             +---------------+               +---------------+
                     \                               /
                      \                             /
                       v                           v
                +-----------------------------------------+
                |        Trace Distance Diagnostic        |
                |  Xi = Tr|rho(h*) - rho(phi*)| / 2      |
                |       (Secondary Tie-Breaker)          |
                +-----------------------------------------+
```

### The Architectural Subordination Principle
The architectural principle governing this construction is strict subordination:
$$\boxed{\text{The primary quotient norm } \Phi_1 \text{ is primary. The secondary statistic } \Xi \text{ is strictly secondary.}}$$
Under no circumstances may a favorable $\Xi$ value accept a proposal that increases $\Phi_1$, nor may $\Xi$ be applied when the boundary closure guardrail ($R_{cl} \le R_{\max}$) is violated.

---

## 2. The Conditional $\ell^1$-to-Density Lift

Let $P = (V, E)$ be a finite carrier graph with edge coordinate space $C^1(P) \cong \mathbb{R}^E$ of dimension $m = |E|$. For any non-zero vector $v \in C^1(P)$, let its total $\ell^1$ mass be:
$$M(v) = \|v\|_1 = \sum_{e \in E} |v_e| > 0.$$

### Definition 2.1 (Pure-State Density Lift)
For a non-zero cochain $v \in C^1(P)$, the conditional state vector $\psi(v) \in \mathbb{R}^E$ is defined coordinate-wise by:
$$\psi(v)_e = \operatorname{sgn}(v_e) \sqrt{\frac{|v_e|}{M(v)}},$$
where $\operatorname{sgn}(x) = 1$ for $x \ge 0$ and $-1$ for $x < 0$. The associated rank-1 density operator $\rho(v)$ is given by the outer product:
$$\rho(v) = |\psi(v)\rangle \langle \psi(v)| \in \mathcal{S}(\mathcal{H}_E),$$
where $\mathcal{H}_E \cong \mathbb{R}^m$.

### Proposition 2.1 (Properties of the Density Lift)

**Deposit status.** Lean formally mechanizes that the rational absolute weights of a nonzero integer cochain sum to 1, and that nonnegative integer scaling and global sign leave the cleared weight identity unchanged. The rank-1 operator is not constructed in Lean.
1. **Normalized Coordinate Weights and Unit Trace:**
   $$\operatorname{Tr}(\rho(v)) = \langle \psi(v) | \psi(v) \rangle = \sum_{e \in E} \frac{|v_e|}{M(v)} = 1, \quad \psi(v)_e^2 = \frac{|v_e|}{M(v)}.$$
   The map preserves normalized absolute coordinate weights; total cochain mass $M(v)$ is discarded in the projection $\rho(v)$.
2. **Positive Semi-Definiteness and Purity:** $\rho(v) \ge 0$ and $\rho(v)^2 = \rho(v)$ (rank-1 pure state).
3. **Scale Invariance:** For any scalar $c > 0$,
   $$M(c \cdot v) = c \cdot M(v), \quad \psi(c \cdot v) = \psi(v), \quad \rho(c \cdot v) = \rho(v).$$
4. **Coordinate Signs and Global Sign Loss:** The real state vector $\psi(v)$ preserves the coordinate signs $\operatorname{sgn}(v_e)$ of $v$. The density matrix $\rho(v) = \rho(-v)$ is invariant under global sign negation, discarding the common global sign.
5. **Real Amplitudes:** $\psi(v)$ consists of real amplitudes with no independently chosen phases.

---

## 3. Primal-Dual Representative Selection

To define a deterministic functional, non-uniqueness in the optimal primal and dual sets must be resolved.
Let $[\omega_1] \in Q^1 = C^1 / \operatorname{im}(d_0)$ be the quotient class, with quotient norm $\Phi_1([\omega_1]) = \min_{h \in [\omega_1]} \|h\|_1$.

1. **Optimal Primal Residual Set:**
   $$\mathcal{H}^*([\omega_1]) = \arg\min_{h \in [\omega_1]} \|h\|_1 = \left\{ h \in [\omega_1] : \|h\|_1 = \Phi_1([\omega_1]) \right\}.$$
2. **Optimal Dual Witness Set:**
   $$\mathcal{W}^*([\omega_1]) = \left\{ \varphi \in C^1(P) : \|\varphi\|_\infty \le 1, \; d_0^* \varphi = 0, \; \langle \varphi, \omega_1 \rangle = \Phi_1([\omega_1]) \right\}.$$

### Failure of Support-First Lexicographic Selection
A naive rule that sorts non-zero supports and then minimizes coordinates within the minimal support stratum can fail to attain a minimum. Consider two disjoint cyclically oriented triangles on edges $1, 2, 3$ and $4, 5, 6$, with cochain $\omega = (1, 0, 0, 1, 0, 0)$. The optimal primal residual set is:
$$\mathcal{H}^* = \{ h \ge 0 : h_1 + h_2 + h_3 = 1, \; h_4 + h_5 + h_6 = 1 \},$$
with quotient norm $\Phi_1 = 2$, certified by dual circulation $\varphi = (1, 1, 1, 1, 1, 1)$.
Under standard lexicographic ordering of sorted support index lists, the minimal candidate support is $(1, 2, 3, 4)$. On that support, the family
$$h(t) = \left( t, \; \frac{1-t}{2}, \; \frac{1-t}{2}, \; 1, \; 0, \; 0 \right), \quad 0 < t < 1,$$
has an infimum first coordinate $t \to 0$, but the infimum is not attained on that support stratum because at $t = 0$ the support drops to $(2, 3, 4)$. Hence support-first selection does not define a valid minimizer.

### Canonical Successive Coordinate Minimization

**Deposit status.** Existence of the successive minimizer is a classical compactness argument. This deposit does not mechanize that argument.
To ensure existence and uniqueness, fix an arbitrary but declared total ordering on the edges: $e_1 < e_2 < \dots < e_m$.
The set $\mathcal{H}^*([\omega_1])$ is non-empty, closed, and bounded (compact) in $\mathbb{R}^E$, as the intersection of an affine subspace with an $\ell^1$-ball. Define the sequence of nested sets:
$$K_0 = \mathcal{H}^*([\omega_1]), \quad K_k = \arg\min_{h \in K_{k-1}} h_{e_k} \quad (k = 1, \dots, m).$$
Since each coordinate projection $h \mapsto h_{e_k}$ is continuous and each $K_{k-1}$ is non-empty and compact, the Weierstrass extreme value theorem ensures under the declared assumptions that each minimum is attained, so each $K_k$ is non-empty and compact. For any $u, v \in K_m$, $u_{e_k} = v_{e_k}$ for all $k \in \{1, \dots, m\}$, so $K_m = \{ h^* \}$ is a unique singleton.

Similarly, the optimal dual witness set $\mathcal{W}^*([\omega_1])$ is non-empty, closed, and bounded (compact) in $\mathbb{R}^E$. Define:
$$L_0 = \mathcal{W}^*([\omega_1]), \quad L_k = \arg\min_{\varphi \in L_{k-1}} \varphi_{e_k} \quad (k = 1, \dots, m).$$
By identical compactness and continuity arguments, $L_m = \{ \varphi^* \}$ is a unique singleton.

The resulting vectors $h^*$ and $\varphi^*$ are canonical relative to the declared edge ordering. The reference implementation takes externally supplied vectors (for example, from an upstream linear programming solver implementing this selector) and evaluates the functional on those inputs.

---

## 4. The $\Xi$ Diagnostic Functional

### Definition 4.1 (Domain of $\Xi$ and Zero-Obstruction Convention)
1. **Obstructed Domain ($\Phi_1([\omega_1]) > 0$):**
   When $\Phi_1([\omega_1]) > 0$, the canonical primal residual satisfies $\|h^*\|_1 = \Phi_1 > 0$ and the canonical dual witness satisfies $\|\varphi^*\|_1 \ge 1 > 0$. The lower bound $\|\varphi^*\|_1 \ge 1$ holds because linear programming strong duality gives $\Phi_1 = \langle \varphi^*, h^* \rangle \le \|\varphi^*\|_\infty \|h^*\|_1 = \|\varphi^*\|_\infty \Phi_1$, forcing $\|\varphi^*\|_\infty = 1$, and therefore $\|\varphi^*\|_1 \ge \|\varphi^*\|_\infty = 1 > 0$. The density lifts $\rho(h^*)$ and $\rho(\varphi^*)$ are well-defined, and $\Xi$ is given by the normalized trace distance:
   $$\Xi([\omega_1]) = \frac{1}{2} \operatorname{Tr}\left| \rho(h^*) - \rho(\varphi^*) \right|.$$
2. **Zero-Obstruction Convention ($\Phi_1([\omega_1]) = 0$):**
   When $\Phi_1([\omega_1]) = 0$ (including exact cochains and all cochains on trees), every minimizing residual is $h^* = 0$, having zero mass, so $\rho(h^*)$ is undefined. By declared operational convention:
   $$\Xi([\omega_1]) = 0 \quad \text{when } \Phi_1([\omega_1]) = 0.$$
   This declared convention reflects the complete absence of residual defect distortion and is an operational definition, not an evaluation of the trace distance formula. The convention applies strictly to unobstructed cochains ($\Phi_1 = 0$); any positive obstruction ($\Phi_1 > 0$), regardless of its scale, has non-zero mass and evaluates under the density lift without threshold erasure.

### Proposition 4.1 (Generic Pure-State Trace Distance Formula)

**Deposit status.** Lean formally mechanizes the integer Cauchy gap $(\sum a_i^2)(\sum b_i^2)-(\sum a_i b_i)^2 \ge 0$. The square-root trace-distance formula is the classical name of the normalized gap.
For normalized pure-state vectors $\psi_1, \psi_2 \in \mathbb{R}^m$ and their projectors $\rho_1 = |\psi_1\rangle\langle\psi_1|$ and $\rho_2 = |\psi_2\rangle\langle\psi_2|$, the trace distance is:
$$D(\rho_1, \rho_2) = \frac{1}{2}\operatorname{Tr}|\rho_1 - \rho_2| = \sqrt{1 - |\langle \psi_1 | \psi_2 \rangle|^2}.$$
For arbitrary pure states, $0 \le D \le 1$, with $D = 0$ if and only if $\psi_1 = \pm \psi_2$, and $D = 1$ if and only if $\langle \psi_1 | \psi_2 \rangle = 0$.

### Proof
Let $F = |\langle \psi_1 | \psi_2 \rangle| \in [0, 1]$. The non-zero eigenvalues of $\rho_1 - \rho_2$ are $\pm \sqrt{1 - F^2}$. Summing their absolute values gives $\operatorname{Tr}|\rho_1 - \rho_2| = 2\sqrt{1 - F^2}$, so $\frac{1}{2}\operatorname{Tr}|\rho_1 - \rho_2| = \sqrt{1 - F^2}$. $\blacksquare$

### Proposition 4.2 (Optimal Primal-Dual Pair Bounds and Equality Conditions)

**Deposit status.** Lean formally mechanizes that a unit-infinity integer dual with vanishing slack on a positive-mass primal has dual mass at least 1 and matches the primal signs. Zero primal mass uses the declared value 0. The square-root upper bound is not constructed in Lean.
Let $\Phi_1([\omega_1]) > 0$, and let $(h^*, \varphi^*)$ be any optimal primal-dual pair.
1. **Strictly Sub-Unitary Bound ($\Xi < 1$):**
   By linear programming strong duality, $\langle \varphi^*, h^* \rangle = \Phi_1 = \|h^*\|_1$. Because $\|\varphi^*\|_\infty \le 1$, Hölder's inequality holds with equality only if $\varphi^*_e = \operatorname{sgn}(h^*_e)$ and $|\varphi^*_e| = 1$ whenever $h^*_e \ne 0$.
   In particular, $\operatorname{supp}(h^*) \subseteq \operatorname{supp}(\varphi^*)$.
   The state overlap satisfies:
   $$\langle \psi(h^*), \psi(\varphi^*) \rangle = \frac{\sum_{e \in \operatorname{supp}(h^*)} \sqrt{|h^*_e|}}{\sqrt{\Phi_1 \|\varphi^*\|_1}} \ge \frac{\sqrt{\Phi_1}}{\sqrt{\Phi_1 \|\varphi^*\|_1}} = \frac{1}{\sqrt{\|\varphi^*\|_1}} \ge \frac{1}{\sqrt{m}} > 0.$$
   Consequently, $\Xi$ satisfies the strict bound:
   $$\Xi(h^*, \varphi^*) \le \sqrt{1 - \frac{1}{\|\varphi^*\|_1}} \le \sqrt{1 - \frac{1}{m}} < 1.$$
   The orthogonality boundary $\Xi = 1$ is never attained for an optimal primal-dual pair.
2. **Zero-Distance Condition ($\Xi = 0$):**
   $\Xi(h^*, \varphi^*) = 0$ if and only if $\psi(h^*) = \psi(\varphi^*)$.
   This holds if and only if:
   - $\operatorname{supp}(h^*) = \operatorname{supp}(\varphi^*)$ and $\operatorname{sgn}(h^*_e) = \operatorname{sgn}(\varphi^*_e)$ for all $e \in \operatorname{supp}(h^*)$; AND
   - $h^*$ has uniform coordinate magnitude across its support: $|h^*_e| = \Phi_1 / \|\varphi^*\|_1$ for all $e \in \operatorname{supp}(h^*)$.
   Matching support and signs alone is insufficient: for example, on a cyclic triangle with $h^* = (2, 1, 1)$ and $\varphi^* = (1, 1, 1)$, $\Phi_1 = 4$ and $\|\varphi^*\|_1 = 3$, giving overlap $(1 + \sqrt{2})/\sqrt{6} \approx 0.98559856$ and $\Xi \approx 0.16910198 > 0$.

---

## 5. Subordination and Evaluator Integration

**Deposit status.** Lean formally mechanizes the exact rational admission fences: a larger primary coordinate is rejected, a tied primary with a larger secondary coordinate is rejected, a double tie that breaks the guardrail is rejected, and a sufficient primary decrease is accepted.

The guarded evaluator implements a tiered priority admission policy with threshold gating and strict non-increase fences:

$$\text{State Diagnostic: } S = (\Phi_1(S), \; \Gamma_2(S), \; R_{cl}(S), \; \Xi(S)).$$

Here, $\Phi_1$ is the primary quotient norm, $\Gamma_2$ is the secondary curvature diagnostic, $R_{cl}$ is the boundary ratio diagnostic, and $\Xi$ is the tertiary tie-breaker. The policy operates with a declared numerical resolution $\epsilon = 10^{-9}$ for registering meaningful decreases, while enforcing literal non-increase on primary and secondary metrics.

A candidate transition $S \to S'$ is admitted if and only if:
1. **Primary Improvement:** $\Phi_1(S') < \Phi_1(S) - \epsilon$; OR
2. **Secondary Improvement:** $\Phi_1(S) - \epsilon \le \Phi_1(S') \le \Phi_1(S)$ AND $\Gamma_2(S') < \Gamma_2(S) - \epsilon$; OR
3. **Tertiary Tie-Break with Guardrail Gating:** $\Phi_1(S) - \epsilon \le \Phi_1(S') \le \Phi_1(S)$ AND $\Gamma_2(S) - \epsilon \le \Gamma_2(S') \le \Gamma_2(S)$ AND $R_{cl}(S') \le R_{\max}$ AND $\Xi(S') < \Xi(S) - \epsilon$.

### Strict Non-Increase Fences
Under no circumstances may a favorable $\Xi$ accept a proposal that increases the primary obstruction $\Phi_1$. Specifically:
- **Literal Non-Increase of $\Phi_1$:** Any candidate with $\Phi_1(S') > \Phi_1(S)$ is strictly rejected—even when the increase is smaller than $\epsilon$ (e.g. $\Phi_1(S') = \Phi_1(S) + 5 \cdot 10^{-10}$).
- **Literal Non-Increase of $\Gamma_2$ on Tie-Break:** When $\Phi_1$ is tied within $[\Phi_1(S) - \epsilon, \Phi_1(S)]$, any candidate with $\Gamma_2(S') > \Gamma_2(S)$ is strictly rejected.
- **Strict Guardrail Gating:** At the tertiary tie-break stage, if the boundary guardrail is violated ($R_{cl}(S') > R_{\max}$), the candidate is rejected regardless of $\Xi$.

This structure is a tiered priority decision policy with threshold gating and strict non-increase fences, not a lexicographical ordering across four coordinates: $R_{cl}$ is not minimized, but acts as a feasibility gate at the $\Xi$ stage, and is not checked on the primary or secondary improvement branches.

---

## 6. Scope Fences and Nonclaims

1. **No Physical Quantum Claims:** The density lift $\rho(v)$ is a mathematical mapping from normalized $\ell^1$ cochains to trace-class operators. It does not suggest or establish physical quantum mechanics, quantum states, or a derivation of the Born rule.
2. **Diagnostic Scope:** Calculating $\Xi$ produces a secondary diagnostic scalar for tie-breaking; it does not constitute an independent objective or feasibility certificate.
3. **Loss of Total Mass and Global Sign:** The mapping $v \mapsto \rho(v)$ discards total scalar magnitude $M(v) = \|v\|_1$ and the common global sign ($\rho(-v) = \rho(v)$). $\Xi$ evaluates normalized structural alignment between primal residual and dual witness, not absolute defect mass.

---

## 7. Conclusion

The Conditional Density Lift and Dual-Witness $\Xi$ Functional extend finite obstruction calculus with an additional scalar for the declared tie-breaking policy while strictly subordinating it to the primary quotient norm $\Phi_1$. By mapping normalized $\ell^1$ cochains to rank-1 density matrices, $\Xi$ computes geometric alignment between canonical primal residuals and dual witnesses without introducing ungrounded representation metaphysics.

