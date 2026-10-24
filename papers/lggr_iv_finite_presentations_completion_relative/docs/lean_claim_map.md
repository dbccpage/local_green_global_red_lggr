# Lean Claim Map — LGGR IV

**Paper:** Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction  
**Version:** 0.1.1  
**Date:** 2026-10-15  
**Default build target:** `LGGR4`  
**Lean version:** `4.33.1`  
**Build result:** 4 jobs completed successfully  
**Axiom result:** 11 reports; 3 axiom-free; 1 uses only `{propext}`; 7 use only `{Quot.sound, propext}`  
**Source scan:** no `sorry` or `admit` token in any `lean4/*.lean` source  

## Declaration Ledger

| Ledger ID | Declaration | Source | Status | Description |
|---|---|---|---|---|
| `M1` | `LggrIV.finite_notFinDesc_iff_collisions` | `lean4/core.lean` | `MECHANIZED` | Finite complete state list: descent failure iff a collision at every stage, using one default output |
| `M1` | `LggrIV.not_FinDesc_iff` | `lean4/core.lean` | `MECHANIZED` | Failure of finite descent iff non-factorization at every stage |
| `M1` | `LggrIV.stage_collision_witness` | `lean4/core.lean` | `MECHANIZED` | A collision blocks stage factorization |
| `M2` | `LggrIV.finite_chain_limit_nonempty` | `lean4/core.lean` | `MECHANIZED` | Finite chain: one top element pulls back to a nonempty compatible thread |
| `M8` | `LggrIV.overlap_dual_residual` | `lean4/core.lean` | `MECHANIZED` | Finite overlap: primal defect equals the dual value, and $k^*=B$ yields a common element |
| `M3` | `LggrIV.finite_stage_identity` | `lean4/core.lean` | `MECHANIZED` | Exact arithmetic identity $3x_n + 1 = (-2)^n$ |
| `M3` | `LggrIV.neg_two_pow_eq` | `lean4/core.lean` | `MECHANIZED` | Representation $(-2)^n = 2^n \cdot (-1)^n$ |
| `M3` | `LggrIV.finite_stage_divisibility` | `lean4/core.lean` | `MECHANIZED` | Divisibility $2^n \mid (3x_n + 1)$ (Local Green) |
| `M4` | `LggrIV.thread_compatibility` | `lean4/core.lean` | `MECHANIZED` | Successive compatibility $2^n \mid (x_{n+1} - x_n)$ |
| `M5` | `LggrIV.no_integral_global_solution` | `lean4/core.lean` | `MECHANIZED` | Impossibility of integral global lift (Global Red) |
| `M7` | `LggrIV.reflection_descent_criterion` | `lean4/core.lean` | `MECHANIZED-DEFINITION` | Definition unfolding (via `rfl`): completed witness descends iff in $\operatorname{im}(\eta)$ |
| `D1` | `LggrIV.FinDesc` | `lean4/core.lean` | `MECHANIZED-DEFINITION` | Finite descent definition |
| `D3` | `LggrIV.ReflectionDescent` | `lean4/core.lean` | `MECHANIZED-DEFINITION` | Reflection descent definition |

## Axiom Censuses

From `lean4/axiom_report.txt`:

- `LggrIV.not_FinDesc_iff`: no axioms
- `LggrIV.stage_collision_witness`: no axioms
- `LggrIV.finite_notFinDesc_iff_collisions`: `[Quot.sound, propext]`
- `LggrIV.reflection_descent_criterion`: no axioms
- `LggrIV.finite_chain_limit_nonempty`: `[propext]`
- `LggrIV.overlap_dual_residual`: `[Quot.sound, propext]`
- `LggrIV.finite_stage_identity`: `[Quot.sound, propext]`
- `LggrIV.neg_two_pow_eq`: `[Quot.sound, propext]`
- `LggrIV.finite_stage_divisibility`: `[Quot.sound, propext]`
- `LggrIV.thread_compatibility`: `[Quot.sound, propext]`
- `LggrIV.no_integral_global_solution`: `[Quot.sound, propext]`

All declarations adhere strictly to the declared whitelist (`Quot.sound`, `propext`).
