# Provenance of the two Lean sources in this deposit

This deposit ships **two** Lean files, from the two parallel builds this
deposit unions (see the change log):

* `observer_visibility.lean` — **this deposit's own mechanization**
  (namespace `ObserverVisibility`): the note's seven core results plus the
  vector no-recovery theorem, the master soundness criterion, the Minkowski
  quotient chains, and the non-linear evaluation bounds. Its compile
  receipt is in the final section of this file.
* `po000_l004_observer_visibility.lean` — the **anchor snapshot**
  (namespace `PO000.ObserverVisibility`), whose provenance and receipt are
  the sections immediately below (unchanged from packaging time).

An earlier revision of this file described only the snapshot while
`lean4/README.md` named `observer_visibility.lean` as "Source"; the two
documents contradicted each other because neither parallel build saw the
other's files. Both are now described, accurately, in both places.

## Part 1 — the anchor snapshot `po000_l004_observer_visibility.lean`

## Where the canonical file lives, and why a snapshot ships here

The canonical copy of this file lives in the anchor estate of the paper
*Projection Obstruction for Factorized States* (PO-000), at

    002_projection_obstruction/000_projection_obstruction/lean4/po000_l004_observer_visibility.lean

This is a **byte-identical deposit snapshot taken at anchor version v6.3
(2026-08-31)**. The estate is not publicly readable, and this note needs the
observer-visibility Lean source to be self-contained rather than depending on a
private repository path. A Zenodo deposit must be self-contained — nothing
required to reproduce a claim may live only in a private repository — which is
why the snapshot is included here.

The file is not edited in any way. Its header comments reference PO-000
section numbers (§7.4.x, S13, S14); those are provenance markers into the
anchor paper, and the note's §6 table is the reader-facing map from this
note's theorem numbers to the Lean declarations.

## Snapshot identity

SHA-256 of `po000_l004_observer_visibility.lean` (must match the
`SHA256SUMS` line at the deposit root, and matched the estate original at
packaging time):

    aa34acc95bf399ac085ee4fcc379f6490e691e4bcb557d4ebe24200b6230f295

## Toolchain and compile command

Toolchain: `leanprover/lean4:v4.34.0-rc1` with Mathlib (community
toolchain). To recompile, run from any Lake project pinned to that
toolchain with Mathlib as a dependency:

    lake env lean <absolute path to>/po000_l004_observer_visibility.lean

The file imports only `Mathlib` and compiles standalone (it is not tied to
the estate's build tree).

## Compile receipt (actual output, packaging-time run of 2026-08-31)

Exit code: **0**. The two warnings are Mathlib's unused-simp-argument
linter (cosmetic; no proof content). The fourteen `#print axioms` lines
below are the complete axiom report — every declaration is within
`{propext, Classical.choice, Quot.sound}` (Lean's three standard axioms),
and there is no `sorry`.

```text
<PATH>/po000_l004_observer_visibility.lean:209:21: warning: This simp argument is unused:
  Pi.single_eq_of_ne (Fin.succAbove_ne a i)

Hint: Omit it from the simp argument list.
  [apply] simp [deleteCoord]

Note: This linter can be disabled with `set_option linter.unusedSimpArgs false`
<PATH>/po000_l004_observer_visibility.lean:227:8: warning: This simp argument is unused:
  Pi.single_eq_of_ne (Fin.succAbove_ne i _)

Hint: Omit it from the simp argument list.
  [apply] simp

Note: This linter can be disabled with `set_option linter.unusedSimpArgs false`
'PO000.ObserverVisibility.tally_le_rawNorm' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.localGreen_of_globalGreen' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.allGreen_iff_kernel' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.rawNorm_eq_zero_of_allGreen' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.coverage_of_jointTrivial' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.ThreePatch.three_patch_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.ThreePatch.rawNorm_scaled' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.ThreePatch.no_recovery_modulus' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.Coupled.full_coverage' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.Coupled.joint_kernel_nontrivial' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.Coupled.allGreen_forces_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.QuotientWitness.repair_mass_ge_two' depends on axioms: [propext, Classical.choice, Quot.sound]
'PO000.ObserverVisibility.QuotientWitness.repair_mass_attained' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'PO000.ObserverVisibility.QuotientWitness.omega_not_exact' depends on axioms: [propext, Classical.choice, Quot.sound]
```

(`<PATH>` abbreviates the absolute path of the compiled snapshot on the
packaging machine; the warning line/column numbers `209:21` and `227:8`
are positions in this byte-identical file.)

## Declaration inventory

The fourteen public declarations behind the `#print axioms` block, each
mapped to its claim-ledger row (see
`../local_green_global_red_claim_ledger.md`):

| Lean declaration (`PO000.ObserverVisibility.` prefix omitted) | Ledger row |
| --- | --- |
| `tally_le_rawNorm` | LGR-T1 |
| `localGreen_of_globalGreen` | LGR-T1 |
| `allGreen_iff_kernel` | LGR-T2 |
| `rawNorm_eq_zero_of_allGreen` | LGR-T5 |
| `coverage_of_jointTrivial` | LGR-T5 |
| `ThreePatch.three_patch_witness` | LGR-T3 |
| `ThreePatch.rawNorm_scaled` | LGR-T3, LGR-T4 |
| `ThreePatch.no_recovery_modulus` | LGR-T4 |
| `Coupled.full_coverage` | LGR-T6 |
| `Coupled.joint_kernel_nontrivial` | LGR-T6 |
| `Coupled.allGreen_forces_zero` | LGR-T6 |
| `QuotientWitness.repair_mass_ge_two` | LGR-R1 |
| `QuotientWitness.repair_mass_attained` | LGR-R1 |
| `QuotientWitness.omega_not_exact` | LGR-R1 |

(`ThreePatch.scaledDefect_is_section_defect`, cited by the note's §6 table
for Theorem 3's section-realization, is a supporting theorem inside the
same file; the fourteen above are the ones with committed `#print axioms`
reports.)

## Part 2 — this deposit's own `observer_visibility.lean`

Not a snapshot: this file was produced for this deposit by the parallel
full-package build and is a strict extension of the snapshot's mathematics
(same seven core results, without the `PO000.` namespace prefix, plus the
vector no-recovery theorem `ThreePatch.vector_no_recovery_modulus`, the
master soundness criterion `master_soundness_iff`, the
`MinkowskiQuotient.*` norm chains, and the `NonlinearEvaluation.*` bounds).

SHA-256 of `observer_visibility.lean` at the 2026-09-09 receipt below
(historical; superseded by the 2026-10-05 extension in Part 3, whose SHA
is the one that must match the `SHA256SUMS` line at the deposit root):

    9585ff8f40d0c2f5fa45c3086bd1199fe4a65c37d94ba4af3643e7261000efec

### Compile receipt (actual output, verification run of 2026-09-09)

Toolchain: `leanprover/lean4:v4.34.0-rc1` with Mathlib (community
toolchain), same as Part 1; the file imports only `Mathlib` and compiles
standalone via

    lake env lean <absolute path to>/observer_visibility.lean

Exit code: **0**. The **43** `#print axioms` lines below are the complete
axiom report — every declaration is within `{propext, Classical.choice,
Quot.sound}`, and there is no `sorry`.

``` text
'ObserverVisibility.tally_le_rawNorm' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.localGreen_of_globalGreen' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.allGreen_iff_kernel' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.rawNorm_eq_zero_of_allGreen' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.coverage_of_jointTrivial' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.ThreePatch.three_patch_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.ThreePatch.rawNorm_scaled' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.ThreePatch.no_recovery_modulus' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.Coupled.full_coverage' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.Coupled.joint_kernel_nontrivial' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.Coupled.allGreen_forces_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.QuotientWitness.repair_mass_ge_two' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.QuotientWitness.repair_mass_attained' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.QuotientWitness.omega_not_exact' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.MinkowskiQuotient.normLinf_le_normL2' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.MinkowskiQuotient.normL2_le_normL1' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.MinkowskiQuotient.norm_minkowski_chain' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.MinkowskiQuotient.quotient_residual_minkowski_chain' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.quotient_attained_minkowski_chain' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.general_normLinf_le_general_normL2' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.general_normL2_le_general_normL1' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.general_normL1_le_sqrt_card_mul_general_normL2' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.general_norm_minkowski_chain' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.general_normL1_le_card_mul_general_normLinf' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormL1_equiv_comp' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormL2_equiv_comp' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormL1_sign_flip' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormL2_sign_flip' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormLinf_sign_flip' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.quotient_residual_l1_isometry' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.quotient_residual_l2_isometry' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormL1_triangle' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.MinkowskiQuotient.generalNormLinf_triangle' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.quotient_residual_l1_subadditive' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.MinkowskiQuotient.quotient_residual_linf_subadditive' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.master_soundness_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.ThreePatch.scaledDefect_is_section_defect' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.ThreePatch.vector_no_recovery_modulus' depends on axioms: [propext, Classical.choice, Quot.sound]
'ObserverVisibility.NonlinearEvaluation.nonlinear_obs_contractive_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.NonlinearEvaluation.nonlinear_lipschitz_obs_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.NonlinearEvaluation.nonlinear_bilipschitz_quotient_lower_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.NonlinearEvaluation.nonlinear_perturbed_residual_upper_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'ObserverVisibility.NonlinearEvaluation.nonlinear_perturbed_residual_lower_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```

(`<PATH>` abbreviates the absolute path of the compiled file on the
verification machine, as in Part 1.)

## Publication replay note (2026-09-09)

For the final first-publication readiness pass, the exact shipped Lean files
were copied to a short temporary Lake project on Windows to avoid path-length
failures under the repository checkout. The shipped `lake-manifest.json`
pinned the Mathlib and transitive dependency revisions.

Commands replayed:

    lake exe cache get! observer_visibility.lean po000_l004_observer_visibility.lean
    lake build ObserverVisibility

Results: the cache command exited 0 after decompressing 8691 files. The final
Lake build exited 0 with `Build completed successfully (8709 jobs)`. The
deposit-owned `observer_visibility.lean` replay emitted no warnings; the
byte-identical anchor snapshot retained its two documented unused-simp-argument
warnings. All reported axioms remained within
`{propext, Classical.choice, Quot.sound}`.

## Part 3 — 2026-10-05 Theorem 7 extension replay

`observer_visibility.lean` was extended by appending the namespace
`ObserverVisibility.CycleBlindSpot` (paper Theorem 7: cycle telescoping and
kernel dependence under identity translations with 1-D blind spots, plus the
C₃ instance). No earlier declaration was changed. The anchor snapshot
`po000_l004_observer_visibility.lean` is unchanged (SHA in Part 1).

SHA-256 of the extended `observer_visibility.lean` at this receipt (1049
lines, 53 `#print axioms` commands; historical, superseded by Part 4, whose
SHA is the one that must match the `SHA256SUMS` line at the deposit root):

    c676229d5f31b20c8512bdf689eae336e8f441a2b091d757263de3b400a3ba3e

Toolchain: `leanprover/lean4:v4.34.0-rc1` (from the shipped
`lean-toolchain`), Mathlib revision pinned by the shipped
`lake-manifest.json`. The shipped lakefile, toolchain file, manifest, and
both `.lean` files were copied to a short-path Lake project `<PATH>` on
Windows (path-length workaround, as in the 2026-09-09 replay).

Commands replayed:

    lake exe cache get
    lake build ObserverVisibility -v

Result: exit 0, `Build completed successfully (8709 jobs).` The only
warnings are the two documented unused-simp-argument warnings of the anchor
snapshot (`po000_l004_observer_visibility.lean:209:21` and `:227:8`). All 53
`ObserverVisibility` axiom reports are within
`{propext, Classical.choice, Quot.sound}`; no `sorry`. The 43 reports listed
in Part 2 recur unchanged; the 10 new reports are (verbatim, `info:`
prefix and file position retained):

```text
info: observer_visibility.lean:1040:0: 'ObserverVisibility.CycleBlindSpot.cycleDefect_sum' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1041:0: 'ObserverVisibility.CycleBlindSpot.cycleDefect_potential' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1042:0: 'ObserverVisibility.CycleBlindSpot.realizable_iff_sum_eq_zero' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1043:0: 'ObserverVisibility.CycleBlindSpot.cycle_blind_spot_dependence' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1044:0: 'ObserverVisibility.CycleBlindSpot.cycle_unsound_of_finrank_lt' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1045:0: 'ObserverVisibility.CycleBlindSpot.cycle_allGreen_iff_dependent' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1046:0: 'ObserverVisibility.CycleBlindSpot.C3.gen_pairwise_independent' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1047:0: 'ObserverVisibility.CycleBlindSpot.C3.gen_dependent' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1048:0: 'ObserverVisibility.CycleBlindSpot.C3.false_green' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1049:0: 'ObserverVisibility.CycleBlindSpot.C3.scaled_defect' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Scope of what this receipt supports: the Lean kernel accepted the stated
Theorem 7 declarations under the three standard axioms. It does not check
the paper's prose wording, the ℓ¹ mass `4|t|` of the C₃ witness, or any
result listed in the paper's §11 as prose-only.

## Part 4 — 2026-10-05 Theorem 7′ and Redundancy Corollary replay

`observer_visibility.lean` was extended again by appending (a) an
invertible-translation block in `ObserverVisibility.CycleBlindSpot`
(Theorem 7′: gauge reduction, trivial holonomy, holonomy with
`w ↦ w - H w` surjective, sign-flip 3-cycle) and (b) the namespace
`ObserverVisibility.Redundancy` (structural Redundancy Corollary). The only
edits to earlier text are two header-comment additions and one scope
comment in the Theorem 7 block; no earlier declaration changed. The anchor
snapshot is unchanged.

SHA-256 of the extended `observer_visibility.lean` (1406 lines, 67
`#print axioms` commands; must match the `SHA256SUMS` line at the deposit
root):

    c8ec2366e2cbc28b55f9c9eff53009459316f52021a9265d339f4090b2921476

Toolchain, short-path procedure, and commands as in Part 3 (`lake build
ObserverVisibility -v` against the shipped `lean-toolchain` and
`lake-manifest.json`). Before the pinned replay the draft was also
elaborated against a separate local Mathlib build on Lean v4.33.1 with no
errors or warnings; that run is not the receipt.

Result: exit 0, `Build completed successfully (8709 jobs).` The only
warnings are the two documented anchor-snapshot warnings. All 67
`ObserverVisibility` axiom reports are within
`{propext, Classical.choice, Quot.sound}` (`gaugeTrans_frame` uses the
subset `{propext, Quot.sound}`); no `sorry`. The 53 reports of Part 3 recur;
the 14 new reports are (verbatim):

```text
info: observer_visibility.lean:1393:0: 'ObserverVisibility.CycleBlindSpot.transDefect_gauge' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1394:0: 'ObserverVisibility.CycleBlindSpot.gauge_blind_spot_dependence' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1395:0: 'ObserverVisibility.CycleBlindSpot.gaugeTrans_frame' depends on axioms: [propext, Quot.sound]
info: observer_visibility.lean:1396:0: 'ObserverVisibility.CycleBlindSpot.holonomy_blind_spot_dependence' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1397:0: 'ObserverVisibility.CycleBlindSpot.realizable_of_holonomy_surjective' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1398:0: 'ObserverVisibility.CycleBlindSpot.unsound_of_holonomy_surjective' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1399:0: 'ObserverVisibility.CycleBlindSpot.unsound_of_holonomy_fixed_point_free' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
info: observer_visibility.lean:1400:0: 'ObserverVisibility.CycleBlindSpot.SignFlip.unsound' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1401:0: 'ObserverVisibility.Redundancy.allGreen_of_kernel_le' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1402:0: 'ObserverVisibility.Redundancy.sound_iff_of_kernel_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1403:0: 'ObserverVisibility.Redundancy.augment_allGreen_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1404:0: 'ObserverVisibility.Redundancy.duplicate_allGreen_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1405:0: 'ObserverVisibility.Redundancy.augment_preserves_false_green' depends on axioms: [propext, Classical.choice, Quot.sound]
info: observer_visibility.lean:1406:0: 'ObserverVisibility.Redundancy.augment_cycle_allGreen_iff_dependent' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```

Scope of what this receipt supports: the Lean kernel accepted the stated
Theorem 7′ and Redundancy declarations under the standard axioms. It does
not cover holonomies `H ≠ I` with nonzero fixed vectors, non-invertible
translations, or the measurement count `k` of the Boxed Theorem.

## Part 5 — standalone rational repair replay, 2026-10-10

Release candidate: v1.3.1. The installed compiler's reported version was
checked against `lean4/lean-toolchain` before this replay:
`leanprover/lean4:v4.34.0-rc1`.

Source SHA-256 (`minkowski_repair.lean`): `911b88b30f2938ccc85f08e26da85793c341666b8a7b9028aa538f10bd54c091`.
The standalone compiler elaborated that source with its output in a unique
temporary directory, exit 0. All 19 named axiom reports were required:

```text
'MinkowskiRepair.diag_l1_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.diag_l2_sq_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.diag_linf_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.diag_zero_l1_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.diag_zero_l2_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.diag_zero_linf_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.diag_vanish_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.r2_l1_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.r2_l2_sq_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.r2_linf_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_l1_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_l2_sq_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_linf_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_vanish_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_points_coincide_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_pair_values' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_zero_l1_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_zero_l2_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'MinkowskiRepair.skew_zero_linf_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
```

This receipt covers rational identities and squared Euclidean quantities only.
It does not formalize the real infima, square roots, graph incidence realization,
or compactness recovery argument. Those written proofs retain their stated scopes.

The full Lake route was attempted and refused before compilation:
`Missing local Lake dependency: mathlib; refusing to download`.
The pinned Mathlib revision is `de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11`.
The available local Mathlib cache belongs to Lean v4.33.1 and was not substituted.
Consequently the 81-report Lake census remains historical evidence for this
release candidate; no fresh full Lake success or external publication is claimed.
