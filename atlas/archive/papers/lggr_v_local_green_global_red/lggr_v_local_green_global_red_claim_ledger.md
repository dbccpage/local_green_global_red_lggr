# Claim ledger — Local Green, Global Red (Part V)

**Paper key:** `001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_v_local_green_global_red`  
**Paper ID:** `lggr_v_local_green_global_red` (formerly `029_local_green_global_red` / `PO-029`)  
**Paper:** `lggr_v_local_green_global_red.md`  
Identity: LGR · Canonical version: 1.3.2 (2026-10-15) · License: CC-BY-4.0  
Author: Jeremy H. Carroll  
Scope: This ledger classifies claims and maps each statement to its formal or computational evidence.

Claim types used here, in plain words: **PROVEN-MECHANIZED** means the
statement, at the stated generality, is a Lean 4 theorem whose axiom report
is within `{propext, Classical.choice, Quot.sound}`; **FINITE COMPUTATION**
means an exact finite-instance arithmetic replay exists in `code/` and is
pinned by exact rational equality in `code/test_lgr_replay.py`.

**Python evidence ceiling.** We distinguish two Python suites in `code/`:
(1) The exact finite-instance replays (`code/lgr_replay.py` and
`code/test_lgr_replay.py`), which compute strictly with standard-library
`fractions.Fraction` and integers (zero floats, zero numerical tolerances) to pin
every constant the note names.
(2) The numerical verification harness (`code/code_*.py` and `code/test_*.py`),
which implements linear programming and duality certification in floating-point
arithmetic under declared tolerances.
Neither suite establishes for-all quantified theorems — no finite run can. The
note gives mathematical proofs of its stated results, with accompanying Lean 4
declarations for the abstract observer statements and explicit defect
calculations. The six-site graph realization is established by the assignment
and calculation in §3. Exact Python replays check the resulting finite-instance
arithmetic. The declaration map specifies the extent of formalization for each
result. The finite-dimensional quantitative recovery bound is proved in prose by compactness, under finite-dimensionality of the realizable defect space; it is not Lean-mechanized.

**Lean bindings.** The canonical copy of
`po000_l004_observer_visibility.lean` lives in the anchor estate of the
paper *Projection Obstruction for Factorized States* (published on Zenodo
as v6.3 Pre-Print, 2026-09-04, version DOI 10.5281/zenodo.22289548; concept DOI 10.5281/zenodo.18896776).
`lean4/po000_l004_observer_visibility.lean` in this deposit is a
**byte-identical snapshot at anchor v6.3**
(SHA-256 in `lean4/PROVENANCE.md` and `SHA256SUMS`). It compiles standalone
against `leanprover/lean4:v4.34.0-rc1` with Mathlib; the packaging-time
compile exited 0, every one of the fourteen `#print axioms` reports is
within `{propext, Classical.choice, Quot.sound}`, and there is no `sorry`.
The verbatim receipt is in `lean4/PROVENANCE.md`.

*Second Lean source (2026-08-31 union).* The deposit also ships
`lean4/observer_visibility.lean`, this deposit's own mechanization from the
parallel full-package build: the same core declarations without the
`PO000.` prefix, **plus** the joint (score-vector) form of LGR-T4
(`ObserverVisibility.ThreePatch.vector_no_recovery_modulus`), the master
soundness criterion (`master_soundness_iff`), the Minkowski quotient
chains, and the non-linear evaluation bounds. Verified by compilation on
2026-08-31: exit 0, 43 `#print axioms` reports, all within
`{propext, Classical.choice, Quot.sound}`, no `sorry`; receipt in
`lean4/PROVENANCE.md` (Part 2), machine-readable declaration inventory in
`manifest.json`. On 2026-10-05 the file was extended with the supplementary cycle
namespace `ObserverVisibility.CycleBlindSpot` and rebuilt with `lake build`
against the pinned toolchain: exit 0, 53 reports, all within the same three
axioms, no `sorry` (receipt in `lean4/PROVENANCE.md`, Part 3). Later on
2026-10-05 it was extended again with the invertible-translation extension
of that supplementary development and the `ObserverVisibility.Redundancy` namespace and rebuilt
the same way: exit 0, 67 reports, same three axioms, no `sorry` (receipt in
`lean4/PROVENANCE.md`, Part 4).

## Claim matrix

Lean names below are fully qualified in `ObserverVisibility` or `MinkowskiRepair`. The latter source reports 19 rational declarations independently of the two Lake roots. Cycle, holonomy, redundancy, non-linear, and zero-repair norm-chain developments in the observer source are supplementary, not additional numbered theorems in the current manuscript.
Python names refer to `code/lgr_replay.py`, `code/test_lgr_replay.py`,
and the numerical suite under `code/`.

| ID | Claim | Type | Hypotheses / scope | Lean source file | Lean declaration | Python replay |
| --- | --- | --- | --- | --- | --- | --- |
| LGR-T1 | Every evaluator score is bounded by the global inconsistency, `J^a(s) <= I(s)`; hence global consistency forces every evaluator green | PROVEN-MECHANIZED | Arbitrary finite interface set, seminormed fibers, contractive measurements | `lean4/observer_visibility.lean`, `lean4/po000_l004_observer_visibility.lean` | `ObserverVisibility.tally_le_rawNorm`, `ObserverVisibility.localGreen_of_globalGreen` | None needed: an inequality over arbitrary carriers is not a finite computation. Recorded as *mechanized general statement, no finite replay applicable*. |
| LGR-T2 | The family is All-Green iff every interface defect lies in that interface's blind spot (joint watcher kernel) | PROVEN-MECHANIZED | Same generality as LGR-T1 | `lean4/observer_visibility.lean`, `lean4/po000_l004_observer_visibility.lean` | `ObserverVisibility.allGreen_iff_kernel` | `test_lgr_replay.py::test_coupled_blind_spots_nontrivial` exercises the kernel-membership direction on a finite instance (a nonzero blind-spot vector measured as 0). |
| LGR-MSC | Master Soundness Criterion: All-Green forces `I = 0` iff `im(D) ∩ prod_e K_e = {0}` | PROVEN-MECHANIZED, CONDITIONAL | Explicit `hnorm_zero` on the supplied realizable set; the displayed equality also uses `0 ∈ im(D)`. Not arbitrary seminormed fibers without separation. | `lean4/observer_visibility.lean` | `ObserverVisibility.master_soundness_iff` | No finite replay of the general iff is claimed; the sufficient condition and coupled example are separate instances. |
| LGR-T3 | Three-patch witness: 6 sites (3 component, 3 overlap), 6 interfaces, every one watched, All-Green, yet `I = 6` (at scale 1) | PROVEN-MECHANIZED (Edge) + PROSE-REALIZED (Graph) + FINITE COMPUTATION | The explicit six-site system ($s(u_i) = \lambda e_i, s(x_{ij}) = 0$, identity translations); per-edge cochain scaling mechanized; six-site graph realization established in prose; resulting edge-cochain arithmetic checked by exact rational replay | `lean4/observer_visibility.lean`, `lean4/po000_l004_observer_visibility.lean` | `ObserverVisibility.ThreePatch.three_patch_witness`, `ObserverVisibility.ThreePatch.rawNorm_scaled`, `ObserverVisibility.ThreePatch.scaledDefect_is_section_defect` | `three_patch_*` in `lgr_replay.py`; tests pin `I == Fraction(6)` exactly and `J == (0, 0, 0)` exactly (`test_lgr_replay.py::test_three_patch_I_is_exactly_6`, `test_lgr_replay.py::test_three_patch_all_green`, `test_lgr_replay.py::test_three_patch_every_interface_watched`). |
| LGR-T4 | Scaling: `I(s_lam) = 6\|lam\|` exactly; **no finite-valued function** `f` satisfies `I(s) <= f(max_a J^a(s))` over this family | PROVEN-MECHANIZED + FINITE COMPUTATION | The fixed witness family of LGR-T3; the no-recovery statement quantifies over all finite-valued functions `f` | `lean4/observer_visibility.lean` (both), `lean4/po000_l004_observer_visibility.lean` (max only) | `ObserverVisibility.ThreePatch.no_recovery_modulus`, `ObserverVisibility.ThreePatch.vector_no_recovery_modulus` | `test_lgr_replay.py::test_scaling_is_six_lambda` pins `6*\|lam\|` at exact Fraction scales including a negative one; `test_lgr_replay.py::test_no_recovery_witness_defeats_f` replays the Lean witness `lam = (\|f0\|+1)/6`: All-Green and `I > f0`. |
| LGR-T5 | Full coverage + trivial joint kernel on every interface => All-Green implies `I(s) = 0`; and joint triviality implies coverage given a non-zero vector on each fiber | PROVEN-MECHANIZED | Arbitrary carriers, as LGR-T1; for the coverage consequence (`coverage_of_jointTrivial`), requires a non-trivial fiber ($v \ne 0$) | `lean4/observer_visibility.lean`, `lean4/po000_l004_observer_visibility.lean` | `ObserverVisibility.rawNorm_eq_zero_of_allGreen`, `ObserverVisibility.coverage_of_jointTrivial` | No finite replay applicable (general statement); noted as such. |
| LGR-T5B | Finite-dimensional quantitative recovery: soundness implies a finite $C>0$ with $I(s)\le C\max_\alpha J^\alpha(s)$. For nonzero $Y=\operatorname{im}D$, $c=\min_{\omega\in Y,\|\omega\|_{1,E}=1}p(\omega)>0$ and $C=c^{-1}$ | PROVED IN PROSE — FINITE-DIMENSIONAL — NOT LEAN-MECHANIZED | Fixed finite-dimensional realizable defect space $Y$, normed fibers, continuous linear measurements, soundness. If $Y=\{0\}$ use $C=1$; the normalized infimum over $I(s)=1$ is asserted only for nonzero $Y$ | None | None; written compactness proof in §4 | `compute_recovery_constant` is an ambient edgewise-injectivity SVD sufficient-condition helper, not this optimum; it may return infinity when recovery holds through coupling. |
| LGR-T6 | Coupled two-edge witness: full coverage, nontrivial blind spot on **every** interface, yet All-Green forces `I = 0` — so the LGR-T5 condition is sufficient but **not** necessary | PROVEN-MECHANIZED + FINITE COMPUTATION | The explicit coupled system (zero restrictions through one shared site; section-realized defects) | `lean4/observer_visibility.lean`, `lean4/po000_l004_observer_visibility.lean` | `ObserverVisibility.Coupled.full_coverage`, `ObserverVisibility.Coupled.joint_kernel_nontrivial`, `ObserverVisibility.Coupled.allGreen_forces_zero` | Tests pin: both edge defects equal `-s(x)` (`test_coupled_defects_are_coupled`), tallies $(\lvert s(x)_1\rvert, \lvert s(x)_0\rvert)$ under the replay convention where watcher 0 reads coordinate 1 and watcher 1 reads coordinate 0 (transposing the two evaluators from the manuscript convention $(\lvert s(x)_0\rvert, \lvert s(x)_1\rvert)$; pinned by `test_coupled_tallies_read_the_other_coordinate`), zero tallies force `s(x) = 0` hence `I = 0` plus the contrapositive (`test_coupled_all_green_forces_zero`), and a nonzero blind-spot vector measured as 0 (`test_coupled_blind_spots_nontrivial`). |
| LGR-R1 | Irreparability remark: on the scalar coupled system, `omega = (1, -1)` is outside `im(D)`, with quotient projection `Phi(omega) = inf_t | | omega - Dt | | _1 = 2` attained at `alpha = 0`; distinct from section defects where`Phi(Delta(s)) = 0` | PROVEN-MECHANIZED + FINITE COMPUTATION | The scalar coupled diagram; repairs range over all overlap values | `lean4/observer_visibility.lean`, `lean4/po000_l004_observer_visibility.lean` | `ObserverVisibility.QuotientWitness.repair_mass_ge_two`, `ObserverVisibility.QuotientWitness.repair_mass_attained`, `ObserverVisibility.QuotientWitness.omega_not_exact` | `test_repair_mass_min_is_exactly_2` pins mass `>= 2` on sampled exact alphas, mass `== 2` at `alpha = 0`, and `phi_lower_bound() == Fraction(2)`; `test_omega_not_exact` pins non-exactness. |
| LGR-R2 | Infimal Minkowski repair distances: for `omega = (1, -1)` and residual `r(alpha) = (1+alpha, alpha-1)`, `Phi_1 = 2`, the squared Euclidean infimum is `2` (named `Phi_2 = sqrt(2)`), and `Phi_infinity = 1`. The value 2 is attained on `[-1, 1]`; the squared value `2` and the value `1` are attained only at `alpha = 0` | PROVED IN PROSE (REAL) + MECHANIZED RATIONAL IDENTITIES + FINITE COMPUTATION | Real repairs in the prose proof; rational repairs in Lean and Fraction replay. One cochain and the diagonal repair line `{(-alpha, -alpha)}`. Not a general norm or a non-diagonal image. `sqrt(2)` names the positive square root of the proved square `2`; the real square-root conclusion is proved in prose and not mechanized here. `quotient_attained_minkowski_chain` evaluates only at `alpha = 0` and is not this infimum. Every scalar pair on this image is LGR-R3 | `lean4/minkowski_repair.lean` | `MinkowskiRepair.r2_l1_iff`, `MinkowskiRepair.r2_l2_sq_iff`, `MinkowskiRepair.r2_linf_iff` | `diag_closed(1, -1)` and `diag_residual` in `lgr_replay.py`; `test_r2_recovers_from_diagonal_closed_form` and `test_diagonal_off_image_is_strict` |
| LGR-R3 | Minkowski distances of a stated scalar cochain: on the same diagonal image `{(-alpha, -alpha)}`, for `omega = (a, b)` with residual `r(alpha) = (a+alpha, b+alpha)`, `Phi_1 = |a-b|` attained for every `alpha` in `[-max(a,b), -min(a,b)]`, the squared Euclidean infimum is `(a-b)^2/2` (named `Phi_2 = |a-b|/sqrt(2)`), and `Phi_infinity = |a-b|/2` attained only at `alpha = -(a+b)/2`. The three distances vanish if and only if `a = b`. The pair `(1, -1)` recovers LGR-R2. Zero-repair equality: `p = 1` iff `ab <= 0`, and the squared `p = 2` norm and `p = infinity` iff `b = -a` | PROVED IN PROSE (REAL) + MECHANIZED RATIONAL IDENTITIES + FINITE COMPUTATION | Every real pair in the prose proof; rational pairs in Lean and Fraction replay, on that one diagonal repair line. Not a norm outside `{1, 2, infinity}`, not a non-diagonal image, not a third component, and not a vector-valued fiber. `sqrt(2)` names the positive square root of the proved square. Outside the sign conditions, the zero-repair evaluation remains only an upper bound | `lean4/minkowski_repair.lean` | `MinkowskiRepair.diag_l1_iff`, `MinkowskiRepair.diag_l2_sq_iff`, `MinkowskiRepair.diag_linf_iff`, `MinkowskiRepair.diag_zero_l1_iff`, `MinkowskiRepair.diag_zero_l2_iff`, `MinkowskiRepair.diag_zero_linf_iff`, `MinkowskiRepair.diag_vanish_iff` | `diag_closed`, `diag_residual`, and `zero_repair_norm` in `lgr_replay.py`; `test_diagonal_vanishes_only_when_coordinates_agree` and `test_zero_repair_matches_diagonal_only_on_the_stated_signs` |
| LGR-R4 | Minkowski distances on one non-diagonal line: on `{(-alpha, -2alpha)}`, for `omega = (a, b)` with residual `r(alpha) = (a+alpha, b+2alpha)`, `Phi_1 = |2a-b|/2` attained only at `alpha = -b/2`, the squared Euclidean infimum is `(2a-b)^2/5` (named `Phi_2 = |2a-b|/sqrt(5)`) attained only at `alpha = -(a+2b)/5`, and `Phi_infinity = |2a-b|/3` attained only at `alpha = -(a+b)/3`. The three distances vanish, and the three attainment sets coincide, if and only if `b = 2a`. The pair `(1, -1)` gives `3/2`, squared value `9/5`, and `1`. Zero-repair equality: `p = 1` iff `b = 0`, squared `p = 2` iff `a + 2b = 0`, and `p = infinity` iff `a + b = 0` | PROVED IN PROSE (REAL) + MECHANIZED RATIONAL IDENTITIES + FINITE COMPUTATION | Every real pair in the prose proof; rational pairs in Lean and Fraction replay, on that one line through the origin in the direction `(-1, -2)`. Not the scalar coupled diagonal image, not a second direction, not a norm outside `{1, 2, infinity}`, not a third component, and not a vector-valued fiber. `sqrt(5)` names the positive square root of the proved square. Outside the three linear conditions, the zero-repair evaluation remains only an upper bound | `lean4/minkowski_repair.lean` | `MinkowskiRepair.skew_l1_iff`, `MinkowskiRepair.skew_l2_sq_iff`, `MinkowskiRepair.skew_linf_iff`, `MinkowskiRepair.skew_vanish_iff`, `MinkowskiRepair.skew_points_coincide_iff`, `MinkowskiRepair.skew_pair_values`, `MinkowskiRepair.skew_zero_l1_iff`, `MinkowskiRepair.skew_zero_l2_iff`, `MinkowskiRepair.skew_zero_linf_iff` | `skew_closed`, `skew_residual`, and `zero_repair_norm` in `lgr_replay.py`; `test_skew_pair_attains_the_three_closed_values`, `test_skew_vanishes_only_on_the_double_line`, and `test_zero_repair_matches_skew_only_on_the_stated_lines` |

## Scope, exactly

Mirroring the note's §6: **LGR-T1, LGR-T2, LGR-T5** are proved over
*arbitrary* finite interface sets, seminormed state spaces, and contractive
measurements — not only the witnesses. **LGR-T5B** is proved in prose by compactness on the finite-dimensional realizable defect space, including a separate zero-space branch; it is not Lean-mechanized. **LGR-T3, LGR-T4,
LGR-T6, LGR-R1, LGR-R2, LGR-R3, LGR-R4** are the explicit finite systems described, with their exact
constants. **LGR-R2**, **LGR-R3**, and **LGR-R4** have written proofs over the reals and rational identities in `lean4/minkowski_repair.lean`, with Fraction replays. Their real infima and square-root formulas are not Lean-mechanized here. The symbols $\sqrt{2}$ and $\sqrt{5}$ name positive square roots of proved squares. **LGR-R3** covers every real pair in prose and every rational pair in Lean on the diagonal image of **LGR-R2**; it is not a non-diagonal image. **LGR-R4** covers every real pair in prose and every rational pair in Lean on the one line through the origin in the direction `(-1, -2)`. It is not a second direction.

**LGR-MSC** additionally requires `hnorm_zero`: zero raw norm detects the
zero cochain on the supplied set. For arbitrary cochain subsets $S$, the formal
statement establishes that every member of $S$ in the joint kernel is zero ($S \cap K \subseteq \{0\}$);
its set-equality specialization $S \cap K = \{0\}$ requires that zero belongs to that set ($0 \in S$),
which holds for linear subspaces such as $S = \operatorname{im}(D)$. The earlier claim of the same unconditional
seminormed generality as LGR-T1 is withdrawn.

The load-bearing words each point at the Lean declaration that earns them:

* "**no finite-valued function**" (LGR-T4) — `ThreePatch.no_recovery_modulus` quantifies
  over every `f : ℝ → ℝ` and produces, for each, an All-Green
  section-realized defect family with `f 0 < I`. The joint strengthening —
  no `F` of the full score vector either — is
  `ObserverVisibility.ThreePatch.vector_no_recovery_modulus` in the second
  source, quantifying over every `F : (Fin 3 → ℝ) → ℝ`. The earlier claim that
  metric rescaling escapes this theorem is withdrawn. The finite-valued
  restriction excludes the vacuous extended-real upper bound `+∞`.
* "**sufficient but not necessary**" (LGR-T5/T6) — sufficiency is
  `rawNorm_eq_zero_of_allGreen`; failure of necessity is the conjunction
  `Coupled.full_coverage` + `Coupled.joint_kernel_nontrivial` +
  `Coupled.allGreen_forces_zero`, unified by `master_soundness_iff`.
* "**nontrivial fiber for coverage**" (LGR-T5) — `coverage_of_jointTrivial` requires
  the explicit hypothesis `hv : v ≠ 0`. If an interface fiber is zero-dimensional ($F(e)=\{0\}$),
  any defect on that interface is trivially zero even if completely unwatched; nontriviality
  ensures the existence of a non-zero witness vector to detect the presence of a watcher.
* "**exactly 2**" (LGR-R1) — lower bound `repair_mass_ge_two` for every
  repair, attainment `repair_mass_attained` at the zero repair. The test cochain
  $\omega = (1, -1) \notin \operatorname{im} D$ has $\Phi(\omega) = 2 > 0$, whereas
  every valid section defect satisfies $\Phi(\Delta(s)) = 0$.
* "**section defect mechanization**" (LGR-T3) — `scaledDefect_is_section_defect`
  formalizes the per-edge algebraic cochain identity $v = v - 0$ directly on edge-indexed vectors;
  it is distinguished from a formalization of an incidence boundary operator on a full six-site assignment graph.
* "**Minkowski chain at zero repair**" — `MinkowskiQuotient.quotient_attained_minkowski_chain`
  evaluates the residual norms at the zero repair candidate $\alpha = 0$ (yielding $1, \sqrt{2}, 2$ and their chain order).
  That declaration does not establish those values are infima. **LGR-R2** is the rational triple
  $\Phi_1=2$ on $[-1,1]$, squared Euclidean infimum $2$, and $\Phi_\infty=1$ only at $\alpha=0$, in `MinkowskiRepair.r2_l1_iff`, `r2_l2_sq_iff`, and `r2_linf_iff`.
  The $\ell^1$ lower bound $\ge 2$ remains `repair_mass_ge_two`. The symbol $\sqrt{2}$ names the positive square root of the proved square.
  **LGR-R3** extends the same three norms from $\omega=(1,-1)$ to every rational pair on that diagonal image, with formulas $|a-b|$, squared value $(a-b)^2/2$, and $|a-b|/2$. For a general pair, the zero-repair numbers $\|(a,b)\|_p$ remain upper bounds unless $ab\le 0$ (for $p=1$) or $b=-a$ (for the squared $p=2$ norm and for $p=\infty$).
  **LGR-R4** computes the same three norms on the different line $\{(-\alpha,-2\alpha)\}$, with formulas $|2a-b|/2$, squared value $(2a-b)^2/5$, and $|2a-b|/3$, attained only on the singletons $\{-b/2\}$, $\{-(a+2b)/5\}$, and $\{-(a+b)/3\}$. It does not identify that line with the scalar coupled image. For a general pair, the zero-repair numbers $\|(a,b)\|_p$ remain upper bounds unless $b=0$ (for $p=1$), $a+2b=0$ (for the squared $p=2$ norm), or $a+b=0$ (for $p=\infty$).
* "**Pointwise non-linear lower bound**" — `NonlinearEvaluation.nonlinear_bilipschitz_quotient_lower_bound`
  specializes an assumed global lower bound to a single pair $(\omega, m)$ pointwise; it does not quantify over a repair set
  or take an infimum, nor does it require $c > 0$ as a formal hypothesis.
* The note's §5 use of "**forced**" (about the additive form of `I`)
  carries its conditional scope — "the axioms under which" — and is the
  anchor paper's claim (version DOI 10.5281/zenodo.22289548; concept DOI 10.5281/zenodo.18896776), not this note's.

## Packaging-time evidence receipts (actual output)

Test run (2026-08-31, deposit root, Python 3.x standard library only):

```text
$ python -m unittest discover -s code -p "test_lgr_replay.py"
...........
----------------------------------------------------------------------
Ran 11 tests in 0.001s

OK
```

Replay receipt (`python code/lgr_replay.py`):

```text
I=6 J=[0, 0, 0] coverage=full 6lam-checks=pass coupled=forced phi=2
```

Lean compile receipts: the anchor snapshot — exit 0, fourteen
`#print axioms` reports; this deposit's own `observer_visibility.lean`
(2026-08-31 verification compile) — exit 0, forty-three reports. All
within `{propext, Classical.choice, Quot.sound}`; verbatim output for both
in `lean4/PROVENANCE.md`.
