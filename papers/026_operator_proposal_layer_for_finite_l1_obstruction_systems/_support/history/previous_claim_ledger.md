# Claim Ledger: Operator Dynamics and Structural Constraints in L1 Obstruction Systems
## Proposal Without Authority, Evaluator Supremacy Firewalls, and Discrete Cohomological Diagnostics

**Author:** Jeremy H. Carroll  
**Date:** 2026-10-08  
**Version:** 2.0.3  
**DOI:** [10.5281/zenodo.20213064](https://doi.org/10.5281/zenodo.20213064)  
**License:** CC-BY-4.0  
**Authority Nonclaim:** This ledger records claim boundaries, dependencies, and verification limits. It carries no operational authority or institutional standing.

---

### Claim Hygiene Summary

1. **What this work supports:**
   - Formal specification of the Operator Proposal Layer separating candidate generation from gate evaluation.
   - Evaluator supremacy: accept/reject verdicts depend solely on the evaluator-computed obstruction tuple $(\Phi_1, \Gamma_2, R_{cl}, \Xi)$ and declared policy, strictly ignoring operator metadata.
   - Evaluator-owned evidence binding: all gate inputs ($R_{cl}$, $\Gamma_2$, $\Phi_1$, $\Xi$) are bound to certified evaluator calculations, refuting spoofed or altered caller tuples.
   - Carrier and field dimension binding: ordinary proposals must preserve carrier dimensions; structural operators require explicit carrier maps.
   - General graph discrete coboundary defect calculations, tree exactness ($\Phi_1 = 0$), and exact primal/dual witness verification with zero duality gap.
   - Second-order closure defects $\Gamma_2 = \|d_1 \omega\|_1 = \|d_1 h_1\|_1$ on admitted 2-complexes verifying $d_1 \circ d_0 = 0$.
   - Realizable second-order tiebreak on theta-graph complexes with equal certified $\Phi_1$ and strict $\Gamma_2$ decrease.
   - Piecewise closure ratio $R_{cl}$ and exact algebraic ratio $R_{\mathrm{exact}}$ separation, with $+\infty$ sentinel curvature rejection.
   - Strict lexicographic descent law on $(\Phi_1, \Gamma_2, \Xi)$ rejecting unchanged, spoofed, and worsening transitions.
   - Operator passivity and Local-Green / Global-Red non-promotion across chart atlases.
   - Continuation-stable state erasure equivalence $\sim_T$ for declared operator families.

2. **What this work does not support:**
   - Free-standing institutional authority minted by either the operator or the evaluator.
   - Replay of the external `PaperAF000` Lean sketches. Those sketches stay outside this deposit. The bundled Lean development is only the four finite sentences in C5, C13, C14, and C19.
   - Unconditional convergence of repeated greedy $\Phi_1$-descent to the global $\ell^1$/LP optimum without global LP solving.
   - Independent 4-tuple field certification of $\Xi$ without an evaluator-bound functional (external-Xi trust boundary).
   - Non-commutativity forcing an evaluator-visible difference in every projection.

3. **Narrowest defensible claim:**
   - Operator proposal mechanisms can generate discrete field candidates while remaining structurally isolated from evaluation criteria, ensuring that candidate generation does not bias or self-certify acceptance decisions under guarded lexicographic descent.

4. **Next test needed:**
   - Quantitative evaluation of multi-operator search trajectories on large sparse graph benchmarks measuring empirical closure ratios and convergence rates.

---

### Formal Claim Registry

| ID | Claim Statement | Status | Hypotheses | Verification & Scope |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | **Non-Authority Axiom:** The operator layer possesses zero acceptance authority and cannot influence evaluator criteria. | `[DECLARED AXIOM]` | Defining constraint of the proposal layer | Architectural invariant verified by interface signature. |
| **C2** | **Evaluator Supremacy:** Acceptance is strictly a function of $(\Phi_1, \Gamma_2, R_{cl}, \Xi)$ and policy, excluding operator metadata. | `[DEFINITION]` | Finite evaluator $\mathcal{E}$, declared policy $\mathcal{P}$, declared solver convention | Implemented in `GuardedEvaluator` and `evaluate_tuple_acceptance` in `mod_operator_proposal_core.py`. |
| **C3** | **Discrete Coboundary Setup:** $d_0 f(e_{ij}) = f(j) - f(i)$, $\Phi_1(\omega) = \inf_{f} \|\omega - d_0 f\|_1$, irreducible residual $h_1$. | `[DEFINITION]` | Finite connected directed graph $P = (V, E)$, additive gauge fixed | Exact rational calculation, tree exactness, and exact primal/dual witness verification in reference module; general LP optimization certified via primal/dual witnesses or exact rational simplex. |
| **C4** | **Cycle-Obstruction Equivalence:** For finite connected graphs without 2-cells, $\Phi_1 = 0 \iff \Delta(C) = 0$ for all cycles $C$. | `[STANDARD]` | Finite connected graph, cycle basis | Proved via exactness characterization; verified in unit tests. |
| **C5** | **Second-Order Closure on the Oriented Triangle:** The coboundary $(f_1-f_0, f_2-f_1, f_0-f_2)$ sums to $0$. For the all-ones face, $\lvert\sum(\omega-d_0 f)\rvert = \lvert\sum\omega\rvert$. Thus $\Phi_1(\omega)=0$ implies $\Gamma_2(\omega)=0$. The field $(2,-1,-1)$ has both equal to $0$. | `[PROVED]` | Oriented triangle, all-ones face row | Lean `triangle_coboundary_sums_zero`, `gamma_independent_of_potential`, `phi_zero_implies_gamma_zero`, `exact_field_gamma_zero`. Python `test_gamma2_independent_of_potential`, `test_r7_phi1_zero_implies_gamma2_zero_on_complex`. |
| **C6** | **Multi-Channel Norm Setup:** Multi-channel $\Phi_1$ evaluation with local gauge $g$ on $\mathbb{R}^k$. | `[DEFINITION]` | $g$ a valid norm on $\mathbb{R}^k$ | Generalizes single-channel obstruction. |
| **C7** | **Replica Extensivity:** Disjoint edge support additivity forces outer $\ell^1$ metric structure. | `[STANDARD]` | Independent replica additivity | Standard result in defect norm classification. |
| **C8** | **Lie Generator Parameterization:** Real skew-symmetric $\mathfrak{so}(k)$ generators on $\mathbb{R}^k$ (or skew-Hermitian $\mathfrak{u}(k)$ on $\mathbb{C}^k$) parameterize candidate channel transitions. | `[STANDARD]` | $T_a^T = -T_a$ on $\mathbb{R}^k$ (or $T_a^\dagger = -T_a$ on $\mathbb{C}^k$) | Standard Lie algebra modeling class. |
| **C9** | **Operator Compatibility Contract:** Operators declare signatures matching graph complex carrier. | `[DEFINITION]` | Declared complex carrier | Interface contract for proposal generation; ordinary proposals enforce dimension invariance. |
| **C10** | **Non-Commutative Proposal Possibility:** Distinct proposal sequences may yield distinct evaluated obstruction tuples. | `[INTERPRETIVE]` | Non-commuting operators | Possibility claim bounded by diagnostic projection. |
| **C11** | **Guarded Descent Law:** Strict lexicographic descent on $(\Phi_1, \Gamma_2, \Xi)$ with hard piecewise $R_{cl}$ gate and verified field binding. | `[POLICY RULE]` | Declared policy thresholds and epsilon guard | Implemented in `GuardedEvaluator` and `evaluate_tuple_acceptance`; verified by 29 unit tests enforcing field binding, ratio validation, domain checks, and carrier dimension preservation. |
| **C12** | **Worked Replay Example:** On the directed 3-cycle the fields $(1,0,0)$, $(0,1,0)$, and $(0,0,1)$ each have cycle obstruction $1$. | `[PROVED]` | Directed 3-cycle, absolute cycle sum | Lean `cyclic_shift_preserves_cycle_sum`. Python `test_r6_cyclic_shift_operator_holonomy_invariance` calls `compute_phi1_cycle_graph`. |
| **C13** | **Operator-Atlas LGGR Non-Promotion:** On the triangle, $(1,0)$ is a coboundary of the path $0\to 1\to 2$ and $(0,0)$ is a coboundary of the path $1\to 2\to 0$, while the cycle field $(1,0,0)$ has obstruction $1$. The step from $(0,0,0)$ to $(1,0,0)$ is not a descent. | `[PROVED]` | One oriented triangle and two spanning paths | Lean `chart1_is_coboundary`, `chart2_is_coboundary`, `global_cycle_obstructed`, `global_step_not_descent`. Python `test_r6_operator_atlas_lggr_non_promotion`. |
| **C14** | **Path Operator Erasure:** Path acceptance on integer primary residuals reads the before/after values and the endpoint bridge, and ignores the operator name. Replacing every name by `Dummy` preserves the Boolean. The trajectory $3\to 2\to 1$ is accepted under both the original names and the erased names. | `[PROVED]` | Finite path of integer primary residuals with matching endpoints | Lean `pathOk_erase`, `both_paths_accept`. Python `test_r6_path_operator_metadata_erasure` calls `evaluate_path_acceptance`. |
| **C15** | **Complex Structure Invariant:** Cochain complex condition $d_1 \circ d_0 = 0$ holds on declared 2-complex. | `[DECLARED AXIOM]` | Declared 2-cell boundary structure | Structural complex prerequisite; checked fail-closed in `AdmittedComplex`. |
| **C16** | **Trace / Quantum Scope Fence:** Hilbert space and trace-class ideal are external imported structures. | `[SCOPE FENCE]` | Separate admission of Hilbert space | Bounded finite cochain scope. |
| **C17** | **Reference Implementation Scope:** Core algorithmic primitives implemented in pure Python / exact rationals. | `[SCOPE FENCE]` | Python 3.10+ standard library | Validated by pytest suite (29 tests passing). |
| **C18** | **Detector Adequacy Bounds:** Bounded four-diagnostic tuple can exhibit blind spots under non-injective projections. | `[OPEN]` | Declared observer tuple | Open obligation for full domain certification. |
| **C19** | **Continuation-Stable State Erasure:** For a diagnostic $D$ and a declared family $\mathcal{T}$, $x\sim_T y$ means $D$ agrees on every finite word from $\mathcal{T}$. That relation is an equivalence, sits in $\ker(D)$, is stable under $\mathcal{T}$, and contains every equivalence with those two properties. On the 3-cycle, $\Phi_1(1,0,0)=\Phi_1(-1,0,0)=1$, but translation by $(1,0,0)$ sends them to obstructions $2$ and $0$. | `[PROVED]` | Total maps and a diagnostic; the witness is the oriented 3-cycle | Lean `contEq_refl`, `contEq_symm`, `contEq_trans`, `contEq_in_kernel`, `contEq_stable`, `contEq_maximal`, `translation_splits_kernel`. Python `test_continuation_stable_erasure_counterexample`. |
