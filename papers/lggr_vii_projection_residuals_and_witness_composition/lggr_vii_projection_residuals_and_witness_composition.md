# Local Green, Global Red VII: Positive-Extension Projection Residuals, Observer-Fiber Minimax Floors, and Witnessed Composition

**Author:** Jeremy H. Carroll  
**Date:** 23 October 2026  
**Version:** 0.1.0  
**AuthorityEffect:** `None`

## Abstract

Volumes I–VI of the *Local Green, Global Red* (LGGR) series examine when local step verdicts, boundary quotients, finite-stage congruences, or linear observation maps fail to determine a specified global property. The companion study *Bell's Theorem as a Positive-Extension Obstruction* develops quantitative projection residuals for empirical behavior tables and observer-fiber minimax bounds for task prediction under fixed evidence. Volume VII unifies the finite mathematical core of these two lines of work into a single executable and Lean-checked framework. First, we formalize the realized-image decoder-or-collision criterion, its invariance under deterministic postprocessing, the report-only verdict ceiling on colliding pairs, and the exact Boolean evaluator defect partition $\Delta_E = E_g - E_1 E_2 \in \{-1, 0, 1\}$. Second, we derive and machine-check multi-step signed increment telescoping, exhibit the separation between local step admissibility ($|\Delta x_i| \le B$) and cumulative endpoint admissibility ($|x_n - x_0| \le B$), separate `every_prefix` from `endpoint` history queries on excursion traces, and certify the report collision between good and bad histories under unsigned step-magnitude reports. Third, we formalize exact integer-scaled $\ell^1$ primal/dual repair certification on the frustrated 3-cycle, distinguish filled-triangle closure failure ($D_1 h \ne 0$) from exact coboundaries ($h = D_0 x$) and from closed nonexact 1-cochains, and establish repair reflection under left-inverse chain retractions. Fourth, we establish the two-point observer-fiber scalar minimax error floor $\frac{1}{2}(b - a)$ and its midpoint attainment, formalize the $m$-context signed-extension to contextual-fraction packing mass identity $U - R = S - (m - 1)N$, and certify the exact rational separation $CF(p_*) = \frac{19}{64} > 2 N_{\min}(p_*) = \frac{25}{128}$ together with the relative order reversal between $p_*$ and the Mermin isotropic behavior $Q_{5/8}$.

**Keywords:** `local-green-global-red`, `finite-obstruction-calculus`, `evaluated-path-kernels`, `observer-sufficiency`, `decoder-or-collision`, `witness-composition`, `cochain-obstruction`, `l1-duality`, `projection-residuals`, `positive-extensions`, `contextual-fraction`, `recursive-self-improvement`

---

## 1. Introduction and Scope Boundary

A recurring failure mode in multi-stage evaluation and distributed observation is that every local check passes while a declared global requirement fails—or remains undetermined by the retained local reports. Across the LGGR series (Volumes I–VI) and the positive-extension Bell analysis, four mathematically distinct questions arise:

1. **Report-fiber descent and task sufficiency:** Given a carrier $X$, a report map $p : X \to A$, and a target query $q : X \to B$, does $q$ factor through $p$ ($q = D \circ p$ on the realized image $p(X)$), or do there exist colliding states $x, y \in X$ with $p(x) = p(y)$ and $q(x) \ne q(y)$?
2. **Signed transition composition vs. restricted local reports:** When each accepted step $x_{i-1} \to x_i$ satisfies a local step bound $|x_i - x_{i-1}| \le B$, what retained boundary data are required to evaluate the cumulative endpoint bound $|x_n - x_0| \le B$ or the prefix bound $\max_{1 \le k \le n} |x_k - x_0| \le B$?
3. **Linear repair distance vs. cohomological closure:** Given a linear coboundary operator $D_0 : C^0 \to C^1$ and defect $h \in C^1$, what certifies a positive weighted $\ell^1$ repair residual $\Phi(h) = \min_x \|h - D_0 x\|_{1,w} > 0$, when is $h$ a closure failure ($D_1 h \ne 0$) rather than a closed nonexact class ($D_1 h = 0, h \notin \mathrm{im}(D_0)$), and when does a representation map $(F_0, F_1)$ preserve nonrepairability?
4. **Positive-extension projection residuals vs. signed extensions:** Given a finite context-incidence matrix $T$ and empirical behavior $p$, how do total-variation distance to the positive local polytope $\mathcal{L} = T\Delta(\Omega)$, minimum negative mass $N_{\min}(p)$ of normalized signed extensions $Tq = p$, and the contextual fraction $CF(p) = 1 - \max\{\mathbf{1}^\top \gamma : \gamma \ge 0,\, T\gamma \le p\}$ compare across symmetric and general multipartite no-signalling tables?

This manuscript records the exact finite theorems answering each question, binds every claim to a sorry-free Lean 4.35.0 theorem in [`lean4/LggrVII.lean`](../../lean4/LggrVII.lean) and an executable Python test in [`code/tests/test_lggr_vii_core.py`](code/tests/test_lggr_vii_core.py), and maintains strict non-conflation between these four regimes.

---

## 2. Report-Fiber Sufficiency, Postprocessing Invariance, and Verdict Ceiling

Let $X$ be a carrier of admissible states or histories, $p : X \to A$ a report map, and $q : X \to B$ a protected query.

**Definition 2.1 (Factorization and Collision).**
- The query $q$ *factors through* $p$ (`LggrVII.FactorsThrough p q`) if there exists a decoder $D : A \to B$ such that $\forall x \in X,\ D(p(x)) = q(x)$.
- A pair $(x, y) \in X \times X$ is a *report collision* (`LggrVII.IsCollision p q x y`) if $p(x) = p(y)$ and $q(x) \ne q(y)$.

**Theorem 2.2 (`LggrVII.collision_blocks_factorization`).** *If $(x, y)$ is a report collision for $(p, q)$, then $\neg \mathrm{FactorsThrough}(p, q)$.*

*Proof.* Suppose $D : A \to B$ satisfies $D(p(z)) = q(z)$ for all $z \in X$. Then $q(x) = D(p(x)) = D(p(y)) = q(y)$, contradicting $q(x) \ne q(y)$. $\square$

**Theorem 2.3 (`LggrVII.postprocessing_preserves_collision`).** *For any deterministic postprocessing map $f : A \to A'$, if $(x, y)$ is a report collision for $(p, q)$, then $(x, y)$ is also a report collision for $(f \circ p, q)$.*

*Proof.* From $p(x) = p(y)$, congruence yields $f(p(x)) = f(p(y))$, while $q(x) \ne q(y)$ is unchanged. $\square$

**Theorem 2.4 (`LggrVII.verdict_ceiling_on_collision`).** *Assume $B$ has decidable equality. For any report-only evaluator $E : A \to B$ and any colliding pair $(x, y)$ for $(p, q)$, either $E(p(x)) \ne q(x)$ or $E(p(y)) \ne q(y)$.*

*Proof.* If $E(p(x)) = q(x)$ and $E(p(y)) = q(y)$, then $p(x) = p(y)$ implies $q(x) = E(p(x)) = E(p(y)) = q(y)$, contradicting $q(x) \ne q(y)$. $\square$

**Theorem 2.5 (`LggrVII.evalDefect_partition`).** *For Boolean verdicts $E_1, E_2, E_g \in \{0, 1\}$, define the evaluated path kernel defect $\Delta_E = E_g - E_1 E_2$. Then $\Delta_E \in \{-1, 0, 1\}$, and $\Delta_E = -1$ (`NGD`: local green, global red) if and only if $E_1 = 1 \wedge E_2 = 1 \wedge E_g = 0$.*

---

## 3. Signed Transition Composition and Scope Separation

Let $x_0, x_1, \dots, x_n \in \mathbb{Z}$ be a sequence of configuration states under a step-magnitude rule $|x_i - x_{i-1}| \le B$ with $B \ge 0$.

**Theorem 3.1 (`LggrVII.two_step_telescope`, `LggrVII.three_step_telescope`).** *Signed transition increments telescope exactly:*
$$(x_1 - x_0) + (x_2 - x_1) = x_2 - x_0, \qquad (x_1 - x_0) + (x_2 - x_1) + (x_3 - x_2) = x_3 - x_0.$$

**Theorem 3.2 (`LggrVII.local_steps_do_not_imply_endpoint_bound`).** *For $B = 1$ and the history $(x_0, x_1, x_2) = (0, 1, 2)$, both local transitions satisfy $|x_1 - x_0| \le 1$ and $|x_2 - x_1| \le 1$, whereas the composed endpoint satisfies $|x_2 - x_0| = 2 > 1$.*

**Theorem 3.3 (`LggrVII.every_prefix_strictly_stronger_than_endpoint`).** *Define `EveryPrefixBounded3` on $(x_0, x_1, x_2, x_3)$ by $\max_{k \in \{1, 2, 3\}} |x_k - x_0| \le B$. Then `EveryPrefixBounded3` implies `EndpointBounded` ($|x_3 - x_0| \le B$), whereas the excursion history $(0, 1, 2, 1)$ with $B = 1$ satisfies `EndpointBounded` ($|1 - 0| \le 1$) while violating `EveryPrefixBounded3` at prefix $x_2 = 2$.*

**Theorem 3.4 (`LggrVII.unsigned_report_collision_good_vs_bad`).** *Under the unsigned step-magnitude report $p_{\mathrm{unsigned}}(x_0, x_1, x_2) = (|x_1 - x_0|, |x_2 - x_1|)$ and Boolean endpoint query $q_1(x_0, x_1, x_2) = \mathbf{1}\{|x_2 - x_0| \le 1\}$, the good history $(0, 1, 0)$ and bad history $(0, 1, 2)$ satisfy $p_{\mathrm{unsigned}}(0, 1, 0) = (1, 1) = p_{\mathrm{unsigned}}(0, 1, 2)$ and $q_1(0, 1, 0) = \mathrm{true} \ne \mathrm{false} = q_1(0, 1, 2)$.*

---

## 4. Exact $\ell^1$ Primal/Dual Repair, Cochain Classification, and Retraction Reflection

Consider the 3-vertex, 3-edge oriented triangle with coboundary matrix
$$D_0 = \begin{pmatrix} -1 & 1 & 0 \\ 0 & -1 & 1 \\ -1 & 0 & 1 \end{pmatrix}, \qquad D_0 \begin{pmatrix} x_0 \\ x_1 \\ x_2 \end{pmatrix} = \begin{pmatrix} x_1 - x_0 \\ x_2 - x_1 \\ x_2 - x_0 \end{pmatrix}.$$

**Theorem 4.1 (`LggrVII.triangle_l1_primal_dual_optimality`).** *For the unit-weight 1-cochain $h = (1, 1, 1)^\top$ and dual vector $z = (1, 1, -1)^\top$:*
1. *$z$ annihilates $\mathrm{im}(D_0)$: for all $x_0, x_1, x_2 \in \mathbb{Z}$, $1(x_1 - x_0) + 1(x_2 - x_1) - 1(x_2 - x_0) = 0$.*
2. *Every integer potential $x = (x_0, x_1, x_2)^\top \in \mathbb{Z}^3$ satisfies $\|h - D_0 x\|_1 \ge z^\top h = 1$.*
3. *The potential $x^* = (0, 1, 2)^\top$ attains $\|h - D_0 x^*\|_1 = |1 - 1| + |1 - 1| + |1 - 2| = 1$.*

**Theorem 4.2 (`LggrVII.filled_triangle_closure_vs_budget_exactness`).** *Let $D_1 = \begin{pmatrix} 1 & 1 & -1 \end{pmatrix}$ be the degree-two boundary operator of the filled triangle:*
1. *$D_1(D_0 x) = (x_1 - x_0) + (x_2 - x_1) - (x_2 - x_0) = 0$ for all $x \in \mathbb{Z}^3$ (`valid_complex`).*
2. *For $h = (1, 1, 1)^\top$, $D_1 h = 1 + 1 - 1 = 1 \ne 0$, so $h$ is a **closure failure** on the filled triangle (and a closed nonexact 1-cochain only when the 2-cell is omitted, $D_1 = 0$).*
3. *For the cumulative-budget difference vector $h_{\mathrm{budget}} = (1, 1, 2)^\top$ from $(x_0, x_1, x_2) = (0, 1, 2)$, $D_0(0, 1, 2)^\top = (1, 1, 2)^\top = h_{\mathrm{budget}}$ with $\ell^1$ repair residual $0$. Thus the cumulative-budget drift violation is an **exact coboundary**, not a cohomological obstruction.*

**Theorem 4.3 (`LggrVII.retraction_reflects_repair_and_obstruction`).** *Let $D_S : C_S^0 \to C_S^1$ and $D_T : C_T^0 \to C_T^1$ be repair operators equipped with forward map $F_1 : C_S^1 \to C_T^1$ and backward maps $G_0 : C_T^0 \to C_S^0$, $G_1 : C_T^1 \to C_S^1$ satisfying backward commutation $G_1(D_T y) = D_S(G_0 y)$ for all $y \in C_T^0$ and left-inverse retraction $G_1(F_1 h) = h$ for all $h \in C_S^1$. Then:*
1. *Any target repair $D_T y = F_1 h$ pulls back to a source repair $D_S(G_0 y) = h$.*
2. *If $h$ is nonrepairable in the source ($\forall x \in C_S^0,\ D_S x \ne h$), then $F_1 h$ is nonrepairable in the target ($\forall y \in C_T^0,\ D_T y \ne F_1 h$).*

---

## 5. Observer-Fiber Minimax Floor and Positive-Extension / Contextual-Fraction Separation

### 5.1 Observer-Fiber Scalar Minimax Error Floor

Let $\mathcal{H}$ be a nonempty finite history carrier, $O : \mathcal{H} \to Y$ a presentation map with fibers $\mathcal{H}_y = O^{-1}(y)$, and $f : \mathcal{H} \to \mathbb{R}$ a scalar target with fiber spread $W_f(y) = \max_{h \in \mathcal{H}_y} f(h) - \min_{h \in \mathcal{H}_y} f(h)$.

**Theorem 5.1 (`LggrVII.observer_fiber_two_point_minimax`).** *Let $h_0, h_1 \in \mathcal{H}_y$ be two histories in the same observation fiber with integer target values $a = f(h_0) \le b = f(h_1)$. For any integer prediction $z \in \mathbb{Z}$:*
1. $|a - z| + |b - z| \ge b - a$, *so $\max(2|a - z|, 2|b - z|) \ge b - a$.*
2. *When $a + b = 2m$, the midpoint prediction $z = m$ attains $2|a - m| = b - a$ and $2|b - m| = b - a$.*

Under evidence-preserving recursion (where an agent updates its internal code, state, or predictor through $n$ steps using only fixed initial report $y = O(h)$ and randomness conditionally independent of $h \in \mathcal{H}_y$), the output distribution of $Z_n$ is identical on $h_0$ and $h_1$, so $\max_{h \in \{h_0, h_1\}} \mathbb{E}|Z_n - f(h)| \ge \frac{1}{2}(b - a) = \frac{1}{2} W_f(y)$.

### 5.2 Positive Extensions, Contextual Fraction, and Signed Negative Mass

Let $T \in \{0, 1\}^{C \times |\Omega|}$ be the incidence matrix of a finite $m$-context measurement scenario where every deterministic assignment $\lambda \in \Omega$ has $\sum_i T_{i,\lambda} = m > 0$. For a normalized nonnegative behavior $p$ ($\sum_i p_i = m$):
- The **signed-extension minimum negative mass** is $N_{\min}(p) = \min\{\mathbf{1}^\top q^- : q = q^+ - q^-,\ q^\pm \ge 0,\ Tq = p,\ \mathbf{1}^\top q = 1\}$.
- The **contextual fraction** is $CF(p) = 1 - \max\{\mathbf{1}^\top \gamma : \gamma \ge 0,\ T\gamma \le p\}$.

**Theorem 5.2 (`LggrVII.contextual_fraction_packing_mass_identity`).** *In an $m$-context scenario scaled by denominator $S > 0$, if the positive part $u$ of a normalized signed extension has total mass $U = S + N$ and the negative-part context marginals $r = T n$ have total mass $R = m N$, then the excess mass satisfies*
$$U - R = S - (m N - N) = S - (m - 1)N,$$
*and any local packing $\gamma \ge 0$ with scaled mass $\Gamma \ge U - R$ satisfies $S - \Gamma \le (m - 1)N$ (corresponding to $CF(p) \le (m - 1) N(q)$).*

**Theorem 5.3 (`LggrVII.ghz_rnd2_cf_gt_two_neg_mass_and_order_reversal`).** *In the three-party, two-setting, two-outcome ($m = 8$) scenario over common denominator $S = 768$, consider the no-signalling mixture*
$$p_* = \frac{1}{6} W + \frac{1}{3} \ell_{63} + \frac{5}{12} G + \frac{1}{12} Q_{5/8}$$
*and the Mermin isotropic behavior $Q_{5/8}$:*
1. *At $p_*$, the certified optimal local packing mass is $\frac{540}{768}$, giving $CF(p_*) = \frac{228}{768} = \frac{19}{64}$, while the certified optimal signed negative mass is $N_{\min}(p_*) = \frac{75}{768} = \frac{25}{256}$.*
2. *Therefore $CF(p_*) - 2 N_{\min}(p_*) = \frac{228 - 150}{768} = \frac{78}{768} = \frac{13}{128} > 0$, refuting the inequality $CF \le 2 N_{\min}$ across general three-party no-signalling behaviors while obeying the 8-context bound $CF(p_*) = \frac{228}{768} \le 7 N_{\min}(p_*) = \frac{525}{768}$.*
3. *At $Q_{5/8}$, $CF(Q_{5/8}) = \frac{1}{4} = \frac{192}{768}$ and $N_{\min}(Q_{5/8}) = \frac{1}{8} = \frac{96}{768}$. Consequently $CF(Q_{5/8}) < CF(p_*)$ whereas $N_{\min}(Q_{5/8}) > N_{\min}(p_*)$, demonstrating that $CF$ and $N_{\min}$ can reverse relative ordering.*

---

## 6. Reproduction and Verification Commands

From the repository root:

```console
python -m unittest discover -s papers/lggr_vii_projection_residuals_and_witness_composition/code/tests -v
cd lean4 && lake build
```

---

## 7. Claim Hygiene Summary

1. **What this paper supports:**
   - Machine-checked Lean 4.35.0 proofs (`LggrVII`) and exact rational Python verifications (`lggr_vii_core.py`) of report-fiber collision non-factorization, postprocessing invariance, report-only verdict ceilings, signed history telescoping and `every_prefix` vs. `endpoint` separation, integer $\ell^1$ triangle primal/dual optimality, chain-retraction repair reflection, two-point observer-fiber minimax bounds, and the $CF(p_*) > 2N_{\min}(p_*)$ separation and order reversal.
2. **What this paper does not support:**
   - Quantum realizability of the no-signalling mixture $p_*$ (whose component $G$ is the full-parity box rather than the quantum Mermin endpoint $Q_1$).
   - Any equivalence between cumulative step-budget drift (which is an exact coboundary $h_{\mathrm{budget}} = D_0(0, 1, 2)^\top$) and nonzero cohomology or physical Bell nonlocality.
   - Any general no-go claim for recursive self-improvement when an agent acquires new informative observations that refine its observation fibers.
3. **Narrowest defensible claim:**
   - Within explicitly declared finite carriers, linear cochain complexes, and finite context-incidence matrices, local pass bits and unsigned step magnitudes lose global target distinctions whenever report fibers mix target values; preserving nonrepairability across representations requires a left-inverse retraction condition beyond forward commutation; and on three-party no-signalling tables, contextual fraction $CF$ and signed-extension negative mass $N_{\min}$ satisfy $CF \le (m - 1)N_{\min}$ while separating from $2N_{\min}$ and reversing relative order between $p_*$ and $Q_{5/8}$.
4. **Next test needed:**
   - Determine the tightest scenario-specific constant $c_3 \in [228/75, 7]$ such that $CF(p) \le c_3 N_{\min}(p)$ holds across the full three-party no-signalling polytope, and test whether any quantum-realizable three-qubit behavior achieves $CF(p) > 2 N_{\min}(p)$.
