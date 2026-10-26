# Operator-Relative Continuation-Stable Erasure

**Document ID:** `docs/mathematical_extension.md`  
**Parent Monograph:** `026_operator_proposal_layer_for_finite_l1_obstruction_systems`  
**Version:** 2.0.3  
**Status:** Derivation supplied with review; formal extension of FOC-026 path erasure boundaries. No novelty claim is made for the general equivalence construction.

---

### Claim Hygiene Summary

1. **What this derivation supports:**
   - Formal characterization of the coarsest state quotient $X / {\sim_T}$ compatible with both an observation map $D : X \to Y$ and an admitted family of transition operators $\mathcal{T}$.
   - Proof that $x \sim_T y \iff \forall W \in \mathcal{T}^*,\, D(W(x)) = D(W(y))$ is the maximal congruence contained in $\ker(D)$.
   - Demonstrating via explicit counterexample on directed cycles why single-step diagnostic agreement $D(x) = D(y)$ is insufficient to license state erasure under arbitrary subsequent operator continuations.
   - Clarifying that path concatenation requires explicit endpoint state transport (bridge admissibility) in addition to step acceptance.

2. **What this derivation does not support:**
   - Universal or unrestricted state erasure without declaring the candidate operator family $\mathcal{T}$.
   - Equivalence of single-step evaluator non-interference with infinite-horizon continuation equivalence.
   - Proof that real-world LLMs or physical systems exhibit continuation-stable quotients.

3. **Narrowest defensible claim:**
   - A compressed state description can be safely reused across future proposal steps without altering subsequent diagnostic evaluations if and only if the identified states belong to the same equivalence class under the continuation closure $\sim_T$ for the declared operator family $\mathcal{T}$.

4. **Next test needed:**
   - Algorithmic construction of finite generators for $\sim_T$ on bounded finite graph complexes under Lie-algebra generated edge perturbation families.

---

## 1. Mathematical Formulation

Let $X$ be a state space (e.g. the space of 1-cochains $C^1(P)$ on a finite graph $P$), $D : X \to Y$ an evaluator diagnostic map (such as $D(\omega) = (\Phi_1, \Gamma_2, R_{cl}, \Xi)$), and $\mathcal{T}$ a declared family of total proposal maps $T : X \to X$.

Write $\mathcal{T}^*$ for the monoid of all finite compositions of maps in $\mathcal{T}$, including the identity map $\operatorname{id}_X$.

**Definition (Continuation-Stable Equivalence).**  
Define the relation $\sim_T$ on $X$ by:
$$
x \sim_T y \iff D(W(x)) = D(W(y)) \quad \text{for every } W \in \mathcal{T}^*.
$$

---

## 2. Main Theorem & Proof

**Theorem.**  
The relation $\sim_T$ is the largest equivalence relation $R$ contained in $\ker(D)$ that is stable under $\mathcal{T}$, i.e.,
$$
x \, R \, y \implies T(x) \, R \, T(y) \quad \text{for every } T \in \mathcal{T}.
$$
Consequently, the quotient space $X / {\sim_T}$ is the coarsest state quotient that simultaneously retains the diagnostic observations of every admitted finite continuation and supports well-defined induced actions of every admitted operator in $\mathcal{T}$.

**Proof.**

1. **Equivalence Relation:**  
   Reflexivity ($D(W(x)) = D(W(x))$), symmetry ($D(W(x)) = D(W(y)) \implies D(W(y)) = D(W(x))$), and transitivity hold pointwise for each observation $D$ following each continuation $W \in \mathcal{T}^*$. Thus $\sim_T$ is an equivalence relation.

2. **Subjection to Kernel:**  
   Choosing the empty continuation $W = \operatorname{id}_X \in \mathcal{T}^*$, we have $D(x) = D(y)$ whenever $x \sim_T y$. Hence $\sim_T \subseteq \ker(D)$.

3. **Stability under $\mathcal{T}$:**  
   Assume $x \sim_T y$, and let $T \in \mathcal{T}$. For any continuation $W \in \mathcal{T}^*$, the composition $W \circ T$ is an element of $\mathcal{T}^*$. By definition of $\sim_T$,
   $$
   D(W(T(x))) = D((W \circ T)(x)) = D((W \circ T)(y)) = D(W(T(y))).
   $$
   Since this holds for every $W \in \mathcal{T}^*$, it follows that $T(x) \sim_T T(y)$. Thus $\sim_T$ is stable under $\mathcal{T}$.

4. **Maximality:**  
   Let $R$ be any equivalence relation satisfying $R \subseteq \ker(D)$ and stable under $\mathcal{T}$. Suppose $x \, R \, y$. By induction on the word length of $W \in \mathcal{T}^*$, stability implies $W(x) \, R \, W(y)$. Since $R \subseteq \ker(D)$, we have $D(W(x)) = D(W(y))$ for every $W \in \mathcal{T}^*$. Therefore, $x \sim_T y$, establishing $R \subseteq {\sim_T}$.

5. **Quotient Factorization:**  
   Because $\sim_T$ is stable under $\mathcal{T}$, the induced operator $[T] : X/{\sim_T} \to X/{\sim_T}$ given by $[T]([x]) = [T(x)]$ is well-defined. Because $\sim_T \subseteq \ker(D)$, the diagnostic map descends uniquely to the quotient via $[D]([x]) = D(x)$. Every quotient permitting this diagnostic factorization and induced operator action has a kernel contained in $\sim_T$, and therefore retains at least the distinctions retained by $X/{\sim_T}$. $\blacksquare$

---

## 3. Why the Present Single-Step Tuple Alone is Insufficient

In FOC-026 Section 6b, single-step metadata erasure establishes that the evaluator's accept/reject verdict depends exclusively on the verified before/after diagnostic tuples $(D(\omega), D(\omega'))$ and policy $\mathcal{P}$. However, identifying two states solely because they have identical current diagnostics ($D(x) = D(y)$) is insufficient to ensure under the declared assumptions that future proposal steps evaluate identically.

**Counterexample.**  
Consider a directed 3-cycle $C_3$ with no declared 2-cells and constant external $\Xi = 0$. Let:
$$
x = (1, 0, 0), \quad y = (-1, 0, 0), \quad T(w) = w + (1, 0, 0).
$$
Initially, the diagnostic tuples coincide:
$$
\Phi_1(x) = |1 + 0 + 0| = 1, \quad \Phi_1(y) = |-1 + 0 + 0| = 1,
$$
so $D(x) = D(y) = (1, 0, 0, 0)$.

Now apply the permitted translation operator $T$:
$$
T(x) = (2, 0, 0) \implies \Phi_1(T(x)) = 2,
$$
$$
T(y) = (0, 0, 0) \implies \Phi_1(T(y)) = 0.
$$
The future evaluated tuples differ: $D(T(x)) = (2, 0, 0, 0) \ne (0, 0, 0, 0) = D(T(y))$.

Therefore, $\ker(D)$ is not stable under the admitted translation operator family. Erasing the underlying sign or coordinate distinction is sound for a single-step gate decision, but unsound for multi-step compositional state caching without continuation closure.

This observation does not contradict FOC-026's single-step non-interference theorem: the future evaluated tuples differ precisely because the underlying cochains differ. It formalizes the exact mathematical requirement needed to reuse a compressed state description across sequential workflows.

---

## 4. Two Sharp Extremes

The quotient $X / {\sim_T}$ exhibits two boundary regimes depending on the richness of $\mathcal{T}$:

1. **Kernel-Preserving Family:**  
   If every admitted operator $T \in \mathcal{T}$ preserves $\ker(D)$ (i.e. $D(x) = D(y) \implies D(T(x)) = D(T(y))$), then $\sim_T = \ker(D)$. In this regime, the static diagnostic quotient $X / \ker(D)$ is already fully stable under continuation.

2. **Unrestricted Operator Family:**  
   If the admitted operator family $\mathcal{T}$ contains all functions $X \to X$ and $D$ is non-constant, then $\sim_T$ collapses to identity (equality).  
   *Proof:* For any distinct $x \ne y \in X$, choose two states $a, b \in X$ distinguished by $D$ ($D(a) \ne D(b)$). Define $T : X \to X$ by $T(x) = a$, $T(y) = b$, and $T(w) = a$ otherwise. Then $D(T(x)) = D(a) \ne D(b) = D(T(y))$, so $x \not\sim_T y$.  
   Thus, no non-trivial state compression is valid under completely unrestricted future proposals.

---

## 5. Path Binding is Separate from Diagnostic Equality

Equality of endpoint diagnostics ($D(x_k) = D(y_k)$) does not imply equality or composability of the actual endpoint states ($x_k = y_k$).

For an executable trajectory $(S_0 \xrightarrow{T_1} S_1 \xrightarrow{T_2} \dots \xrightarrow{T_n} S_n)$, path concatenation requires an explicit bridge verifying that the target state of the preceding segment matches the source state of the succeeding segment:
$$
S_k^{\mathrm{target}} = S_{k+1}^{\mathrm{source}}.
$$
A conjunction of accepted step predicates $\bigwedge_k \operatorname{Accepted}(S_k \to S_k')$ establishes only a list-level property unless this continuity condition is explicitly enforced. In `mod_operator_proposal_core.py`, `evaluate_path_acceptance` verifies both the individual guarded descent steps and this mandatory endpoint continuity.
