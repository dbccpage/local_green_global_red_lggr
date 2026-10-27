# LGGR Lean 4 Formalizations (`LGGR` / Volume VII)

**AuthorityEffect: None.**

Standalone Lean 4 (`v4.35.0`) formalization package for Volume VII of the *Local Green, Global Red* series: *Positive-Extension Projection Residuals, Observer-Fiber Minimax Floors, and Witnessed Composition*.

## Build and Verify

```console
cd lean4
lake build
```

Building `CheckAxioms` runs `#print axioms` on all 15 theorems in [`LggrVII.lean`](LggrVII.lean), verifying zero `sorry` declarations and zero custom axioms.

## Theorem Inventory

| Section | Theorem | Scope |
|---|---|---|
| 1 | `LggrVII.collision_blocks_factorization` | Explicit colliding pair $(x, y)$ with $p(x)=p(y)$ and $q(x) \ne q(y)$ refutes any decoder $D \circ p = q$. |
| 1 | `LggrVII.postprocessing_preserves_collision` | Any deterministic postprocessing $f : A \to A'$ preserves report collisions. |
| 1 | `LggrVII.verdict_ceiling_on_collision` | Any report-only evaluator $E : A \to B$ disagrees with $q$ on at least one member of a colliding pair. |
| 1 | `LggrVII.evalDefect_partition` | Boolean defect $\Delta_E = E_g - E_1 E_2 \in \{-1, 0, 1\}$, with $\Delta_E = -1 \iff (E_1, E_2, E_g) = (1, 1, 0)$. |
| 2 | `LggrVII.two_step_telescope`, `LggrVII.three_step_telescope` | Exact telescoping of signed step increments across two and three transitions. |
| 2 | `LggrVII.local_steps_do_not_imply_endpoint_bound` | Witnessed on $(0, 1, 2)$ with $B = 1$: both local steps satisfy $|\Delta x_i| \le 1$ while $|x_2 - x_0| = 2 > 1$. |
| 2 | `LggrVII.every_prefix_strictly_stronger_than_endpoint` | Every-prefix boundedness implies endpoint boundedness, while $(0, 1, 2, 1)$ separates the converse. |
| 2 | `LggrVII.unsigned_report_collision_good_vs_bad` | $(0, 1, 0)$ and $(0, 1, 2)$ collide under unsigned step-magnitude reports $(|\Delta x_1|, |\Delta x_2|) = (1, 1)$. |
| 3 | `LggrVII.triangle_l1_primal_dual_optimality` | Dual annihilator $z = (1, 1, -1)$ and primal potential $(0, 1, 2)$ certify $\min_{x \in \mathbb{Z}^3} \|(1,1,1) - D_0 x\|_1 = 1$. |
| 3 | `LggrVII.filled_triangle_closure_vs_budget_exactness` | $D_1 D_0 = 0$; $D_1(1, 1, 1) = 1 \ne 0$ (closure failure on filled triangle); budget differences $(1, 1, 2) = D_0(0, 1, 2)$ are exact. |
| 3 | `LggrVII.retraction_reflects_repair_and_obstruction` | Left-inverse chain retraction $(G_1 F_1 = I, G_1 D_T = D_S G_0)$ pulls back target repairs and reflects source nonrepairability. |
| 4 | `LggrVII.observer_fiber_two_point_minimax` | On a two-point fiber with target values $a \le b$, any integer prediction $z$ has $2 \max(|a-z|, |b-z|) \ge b - a$, attained at midpoint $m$. |
| 4 | `LggrVII.contextual_fraction_packing_mass_identity` | Scaled $m$-context mass identity $U - R = S - (mN - N)$ and packing bound $S - \Gamma \le (m - 1) N$. |
| 4 | `LggrVII.ghz_rnd2_cf_gt_two_neg_mass_and_order_reversal` | Exact rational-scaled certification (denominator $768$) of $CF(p_*) = 19/64 > 2 N_{\min}(p_*) = 25/128$ and order reversal against $Q_{5/8}$. |

## Imported LGGR witness classes

`WorldLGGRWitness.lean` and its only import, `PrimitiveDifference.lean`, were copied byte for byte on 2026-10-27 from `dbccpage/the_symbol_game` at `ad9dc4eb5bed958a9b18c951b44ce6acc06d9725`. They come from `lean4/quantum_mechanics/`, where no paper cited them. AuthorityEffect: None. They build with core Lean 4.35.0 and import nothing else.

| File | SHA-256 | Graded |
|---|---|---|
| `PrimitiveDifference.lean` | `3b292fc7544be02d7e7afaae62c70e6ed20a1d152644f0897ba8dfe5db596e1b` | L3D |
| `WorldLGGRWitness.lean` | `480f36d099bd082b4fd04d0af0dbae65d36a25337876df21416d08eb116e9819` | L3D |

`OmegaWorld.LGGRWitness` wraps the primitive-difference pair obstruction in two type classes. `ExactLGGRWitness` compares observer outputs by equality; `SetoidLGGRWitness` compares them modulo supplied setoids. An instance must already supply the two source points, their `ZeroRel` proof, local congruence and global separation. The module has no generic instance and does no search; its only instances are the Bool regressions. `CheckAxioms` prints the axioms of its seven declarations, which use at most `propext`, `Classical.choice` and `Quot.sound`.

The grades follow the_symbol_game `SCORING.md` v2.0.0. The re-homing report is `reports/lean4_rehoming_2026-10-27/report.md` in the project files. FQM `lean4/WorldLGGRWitness.lean` holds the same code, with the namespace renamed to `ObserverWorld` and the docs stripped.
