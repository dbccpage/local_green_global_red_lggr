---
paper: "Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction"
version: "0.1.1"
date: "2026-10-15"
---

# Claim Ledger — LGGR IV

This ledger separates mathematical statements, definitions, implementation contracts, and interpretation. The structured `Mechanization` column identifies which rows have Lean 4 formalization support. A Lean theorem supports only the statement in its row; it does not mechanize organizational or physical readings.

| ID | Statement | Type | Mechanization | Lean evidence | Python evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | Moving-witness collision criterion on a finite complete state list: with one default output value extending each stage map off its image, $\neg\operatorname{FinDesc}(D)$ if and only if every stage has a colliding pair. An arbitrary non-enumerated carrier is not a separate Lean theorem. | theorem | LEAN | `LggrIV.finite_notFinDesc_iff_collisions` | `test_finite_descent_moving_witnesses` | checked |
| M2 | Finite-chain thread: one element of the last stage, pulled back along a finite list of transition maps, yields a nonempty compatible thread whose last entry is that element. Finiteness of the fibers is not used. The cofiltered nonemptiness statement is cited from Stacks Tag 086J and is outside this row. | theorem | LEAN | `LggrIV.finite_chain_limit_nonempty` | `test_finite_chain_thread` | checked |
| M3 | Explicit finite-stage solution: For $x_n = -\sum_{k=0}^{n-1} (-2)^k$, the identity $3x_n + 1 = (-2)^n$ holds for all $n \ge 1$; in particular $2^n \mid (3x_n + 1)$ (Local Green). | theorem | LEAN | `LggrIV.finite_stage_identity`, `LggrIV.finite_stage_divisibility` | `test_finite_stage_identity_and_divisibility` | checked |
| M4 | Sequence compatibility: $x_{n+1} - x_n = -(-2)^n$, so $x_{n+1} \equiv x_n \pmod{2^n}$, forming a compatible thread in $\varprojlim \mathbb{Z}/2^n\mathbb{Z}$. | theorem | LEAN | `LggrIV.thread_compatibility` | `test_stage_compatibility` | checked |
| M5 | Absence of integral global lift: There exists no integer $x \in \mathbb{Z}$ satisfying $2^n \mid (3x+1)$ for all $n \ge 1$ (Global Red in original carrier). | theorem | LEAN | `LggrIV.no_integral_global_solution` | `test_integral_global_red` | checked |
| M6 | Completion solution and convergence: In $\mathbb{Z}_2$, $3$ is a unit and $3x+1=0$ has unique solution $x_\infty = -1/3 \in \mathbb{Z}_2$; the thread $(x_n \bmod 2^n)$ converges $2$-adically to $x_\infty$ (Completion Green). | classical theorem | PROSE / MATH | Standard 2-adic analysis (Koblitz). Classical result, reproduced in prose, not mechanized here. | `test_p_adic_valuation_and_distance` | checked |
| M7 | Reflection descent criterion: For completed solution $\hat{r} \in R_{\widehat{X}}$, $\hat{r}$ descends to original carrier iff $\hat{r} \in \operatorname{im}(\eta)$. Primitive residual is $\hat{r} \notin \operatorname{im}(\eta)$. | theorem | MECHANIZED DEFINITION | `LggrIV.reflection_descent_criterion` (definition unfolding via `rfl`) | `test_reflection_descent_classification` | checked |
| M8 | Finite probability-simplex overlap identity: for a finite carrier $U$ and finite nonempty list of nonempty subsets $T_1, \dots, T_B \subseteq U$, with $B$ the family count and $k^* = \max_{u \in U} \#\{b : u \in T_b\}$, the primal defect on $\Delta(U)$ is $J = 2(B - k^*)$. That defect equals the exact rational dual lower bound $\mu - \sum \alpha_i$, where $\mu = B - 2k^*$ and each $\alpha_i = -1$ when $k^* < B$, and both are $0$ when $k^*=B$. A nonempty list with $k^*=B$ has an element common to every family. Stacks Tag 07KV is a citation and is outside this row. | theorem | LEAN | `LggrIV.overlap_dual_residual` | `test_overlap_certificate` | checked |
| D1 | Finite descent definition: $\operatorname{FinDesc}(D) :\iff \exists i \in I, \exists d_i: X_i \to Y, D = d_i \circ \pi_i$. | definition | LEAN | `LggrIV.FinDesc` | `lggr_iv_core.try_stage_factor` | implemented |
| D2 | Cofiltered inverse system, compatible thread, and projective limit definitions. | definition | PROSE | Standard category theory | `lggr_iv_core.CompatibleThread` | implemented |
| D3 | Completed repair set $R_{\widehat{X}}$, canonical reflection embedding $\eta: X \hookrightarrow \widehat{X}$, and completion residual $\hat{r} \notin \operatorname{im}(\eta)$. | definition | LEAN | `LggrIV.ReflectionDescent` | `lggr_iv_core.classify_witness` | implemented |
| D4 | Mittag–Leffler condition for inverse systems of abelian groups. | definition | PROSE | Stacks Tag 07KV | not duplicated in Python | definition |
| P1 | Principle of No Completion Laundering: Local-stage solvability or completion solvability does not establish original-carrier solvability. | operational rule | PROSE | none | none | binding |
| S1 | Diagnostic geometry fence: The arithmetic example is diagnostic mathematics of projective limits; it does not model physical spacetime quantization or quantum emergence. | scope fence | PROSE | none | none | binding |
| S2 | Representation limit fence: Moving-witness collisions under $\neg\operatorname{FinDesc}(D)$ reflect finite stage lossiness, not an ontological defect. | scope fence | PROSE | none | none | binding |
| S3 | No continuum extrapolation fence: Passing a countable tower of finite tests provides evidence only for those tests, not continuous limits. | scope fence | PROSE | none | none | binding |

## Formal Scope

The Lean formalization in `lean4/core.lean` mechanizes the core arithmetic claims M3, M4, M5, the structural definition D1, the reflection descent definition D3 and its unfolding M7, the finite complete-list form of M1 (`finite_notFinDesc_iff_collisions`), the finite-chain thread M2 (`finite_chain_limit_nonempty`), and the finite overlap identity M8 (`overlap_dual_residual`). `stage_collision_witness` establishes that a collision blocks factorization on an arbitrary carrier, and `not_FinDesc_iff` is the factorization form of descent failure. The arbitrary non-enumerated carrier is not a separate Lean theorem. Stacks Tag 086J and Stacks Tag 07KV remain citations. The axiom census (`lean4/check_axioms.lean`) verifies that dependencies remain strictly within standard kernel axioms (`Quot.sound`, `propext`), with zero `sorry` or `admit`.

## Interpretation Scope

The arithmetic model over $\mathbb{Z} \to \mathbb{Z}/2^n\mathbb{Z}$ and its completion $\mathbb{Z}_2$ is a deterministic diagnostic tool demonstrating the mathematical decoupling of finite-stage solvability from original-carrier solvability. It does not license claims regarding physical quantum mechanics, spacetime ontology, or continuous evaluation systems.
