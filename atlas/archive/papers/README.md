# Local Green, Global Red foundational series

AuthorityEffect: None.

The seven volumes study when local observations or verdicts fail to determine a
specified global question. Start with the
[manuscript and implementation index](local_green_global_red_monograph_index.md)
for theorem names, assumptions, WDP connections, and formalization limits.

## Reading order

| Volume | Main result and scope |
| --- | --- |
| [I: Evaluated path kernels](lggr_i_evaluated_path_kernels/lggr_i_evaluated_path_kernels.md) | Boolean evaluator defects, conditional composition, and carrier collisions. |
| [II: Organizational gluing](lggr_ii_organizational_gluing/lggr_ii_organizational_gluing.md) | Boundary sufficiency, quotient obstructions, and separately declared closure conditions. |
| [III: Six-role overlay](lggr_iii_epk_gtla_overlay/lggr_iii_epk_gtla_overlay.md) | The same finite evaluator calculus across six mathematical role profiles. |
| [IV: Completion-relative obstruction](lggr_iv_finite_presentations_completion_relative/lggr_iv_finite_presentations_completion_relative.md) | Finite-stage solutions, compatible threads, and the extra obligation of descent to the original carrier. |
| [V: Finite no-recovery](lggr_v_local_green_global_red/lggr_v_local_green_global_red.md) | Hidden raw defects, soundness on realizable defects, and separate distance-to-repair examples. |
| [VI: Aggregation and probing](lggr_vi_nonlinear_aggregation_and_adjoint_probing/lggr_vi_nonlinear_aggregation_and_adjoint_probing.md) | Postprocessing preserves blind spots; rational Gram and full sign-cube identities. |
| [VII: Projection residuals and witness composition](lggr_vii_projection_residuals_and_witness_composition/lggr_vii_projection_residuals_and_witness_composition.md) | Positive-extension projection residuals, observer-fiber minimax error floors, $CF$ vs. $N_{\min}$ separation, and witnessed transition composition. |

In I–III, $\Delta_E=E_g-\prod_iE_i$ lies in $\{-1,0,1\}$.
The value $-1$ means local green/global red; zero means agreement and can include
joint rejection. In V–VI, all-green instead means zero observed defect scores.
These conventions should not be interchanged.

III's roles are finite obstruction, foundations, representation, observer,
continuum shadow, and action alignment. Its proofs do not establish
anti-collusion or truth-telling payoff dominance. IV separates classical
completion theorems from its finite Lean results. V separates raw inconsistency
from repair distance. VI's Gram operator remains blind on the original kernel.

## WDP and native owners

[WDP](../000_witnessed_difference_programme/witnessed_difference_programme.md)
§10.6 directly connects LGGR V to observer completion; Appendix T allows
realization and repair images to differ. §§14.3–14.4 connect report sufficiency
to the kernel results, and §17.1 connects finite path sums to conditional
composition. The index states the premises of these connections.

The Rust package is
[`omega_epk`](../../../../../omega_engine/crates_rs/omega_local_green_global_red_lggr/Cargo.toml).
Its source directory is `omega_engine/crates_rs/omega_local_green_global_red_lggr`.
[`omega_wdp`](../../../../../omega_engine/crates_rs/omega_wdp/src/lib.rs)
and [`omega_category_theory`](../../../../../omega_engine/crates_rs/omega_category_theory/src/lib.rs)
are related owners. Application integration must be checked at the actual call
site; the existence of a crate does not establish that connection.

## Focused local reproduction

Use Python 3.12 with each volume's declared dependencies. Run one row at a time,
from that volume's directory. These are selected regressions, not a full release
verification or a proof of all manuscript claims.

| Volume | Command |
| --- | --- |
| I | `python -m pytest -o addopts='' code/tests/test_finite_theorem_witnesses.py code/tests/test_carrier_kernel_census.py` |
| II | `python -m pytest -o addopts='' code/tests/test_organizational_gluing_core.py` |
| III | `python -m pytest -o addopts='' code/tests/test_epk_gtla_overlay_core.py` |
| IV | `python -m pytest -o addopts='' code/tests/test_finite_chain_and_overlap.py code/tests/test_lggr_iv_core.py` |
| V | `python -m pytest -o addopts='' code/test_lgr_replay.py code/test_exact_obstruction.py` |
| VI | `python -m pytest -o addopts='' code/tests/test_lggr_vi_core.py` |
| VII | `python -m unittest discover -s code/tests -v` |

Lean reproduction requires the toolchain in each `lean4/lean-toolchain`, its
`lakefile.lean` targets, and any pinned dependencies. I–IV currently pin Lean
4.33.1; V–VI pin 4.34.0-rc1. A run on another compiler must be reported separately.
A declaration's presence is not a successful build receipt. General cofiltered
compactness and Mittag-Leffler results in IV are not proved by its finite-chain
Lean module.

Each volume owns its package verification script and manifests. Check that
script's actual options and execution scope before a release replay; this guide
does not instruct simultaneous or unbounded test sweeps. The series index and
this guide sit outside the six individual deposit directories. Updating these
navigation files does not regenerate or recertify their historical archives.
