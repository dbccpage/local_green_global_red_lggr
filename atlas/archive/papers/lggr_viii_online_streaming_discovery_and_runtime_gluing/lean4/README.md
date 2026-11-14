# LGGR Lean 4 Formalizations (`LGGR` / Volume VIII)

**AuthorityEffect: None.**

Standalone Lean 4 (`v4.35.0`) formalization package for Volume VIII of the *Local Green, Global Red* series: *Online Streaming Discovery, Prefix Admissibility, and Runtime Gluing*.

## Build and Verify

```console
cd lean4
lake build
```

Building `CheckAxioms` runs `#print axioms` on all 12 theorems in [`LggrVIII.lean`](LggrVIII.lean), verifying zero `sorry` declarations and zero custom axioms.

## Theorem Inventory

| Section | Theorem | Scope |
|---|---|---|
| 1 | `LggrVIII.collision_monotonicity` | Trace extension preserves existing report-fiber collisions; any collision present in trace $T$ persists in extended trace $T'$. |
| 1 | `LggrVIII.postprocessing_preserves_streaming_collision` | Deterministic postprocessing $f : A \to A'$ of streaming reports preserves all collisions and cannot restore sufficiency. |
| 1 | `LggrVIII.streaming_verdict_ceiling` | Any report-only streaming evaluator $E : A \to B$ disagrees with target query $q$ on at least one observed state in colliding trace $T$. |
| 1 | `LggrVIII.streaming_evalDefect_partition` | Evaluator defect $\Delta_E = E_g - L_k \in \{-1, 0, 1\}$, with $\Delta_E = -1$ (NGD: local green, global red) if and only if $L_k = \mathrm{true} \wedge E_g = \mathrm{false}$. |
| 2 | `LggrVIII.streaming_chain_telescoping` | Exact telescoping of signed step differences $\sum_{i=1}^n (x_i - x_{i-1}) = x_n - x_0$ over arbitrary-length streaming chains. |
| 2 | `LggrVIII.online_prefix_strictly_stronger_than_endpoint` | Online prefix boundedness implies endpoint boundedness, while excursion history $[0, 1, 2, 1]$ separates the converse for budget $B = 1$. |
| 2 | `LggrVIII.prefix_violation_monotonicity` | Once a prefix violation occurs, no extension $H ++ H'$ can restore prefix admissibility, establishing sound early stopping. |
| 2 | `LggrVIII.streaming_unsigned_report_collision` | Safe history $[0, 1, 0]$ and excursion history $[0, 1, 2]$ produce identical streaming unsigned magnitude reports $[1, 1]$ while diverging on endpoint query. |
| 3 | `LggrVIII.open_chain_exactness` | Any acyclic streaming tree of 1-cochains $(h_1, h_2)$ has zero circulation, exact potential $(0, h_1, h_1 + h_2)$, and zero $\ell^1$ repair cost. |
| 3 | `LggrVIII.incremental_cycle_closure_obstruction` | Closing open chain with edge $h_3$ yields circulation $D_1 h = h_1 + h_2 - h_3$; if $h_1 + h_2 \ne h_3$, dual witness $z = (1, 1, -1)$ certifies $\ell^1$ repair residual $\ge 1$. |
| 3 | `LggrVIII.boundary_sufficient_gluing_certifies_lggg` | When boundary summaries satisfy conditional gluing hypotheses G1–G4 and local checks pass, global integration passes with zero defect ($\Delta_E = 0$). |
| 3 | `LggrVIII.boundary_insufficiency_forces_defect` | If a realized report fiber contains an explicit collision between local passes with divergent global outcomes, at least one branch incurs defect $\Delta_E = -1$ (LGGR). |
