# Lean claim map — LGGR III

**Checked:** 2026-10-15\
**Project:** lean4, package LGGR3\
**Default build target:** LGGR3 (`Core.lean`)\
**Statement SHA-256:** `d6029a1e8406a085a4b5c0214b53ce1252888c9de853137f4140e11a747c60a1`\
**Census source SHA-256:** `d54b8887ce723be11a169a803668c38c15d23a3abd635db87231c95bb04558ad`\
**Toolchain/import receipt:** `leanprover/lean4:v4.33.1`; `lake-manifest.json` SHA-256 `f4f0b390203ca8bd6ab43e4397ba7132777218275771e315639a1fa3695a41a4`

The public Lean companion contains only the finite statements used by the thin
paper. It mechanizes the integer reindexing of factorized weights. It does not
formalize real exponentials or detector adequacy.

| paper claim | declaration | status | exact scope |
|---|---|---|---|
| C01 | LGGR3.defect | MECHANIZED | integer definition e_g - e_1 e_2 |
| C02 | LGGR3.defect_range | MECHANIZED | range membership under binary-input hypotheses |
| C03 | LGGR3.local_green_global_red | MECHANIZED | explicit triple (1,1,0) |
| C04 | LGGR3.global_sub_local_eq_defect_sum | MECHANIZED | finite lists of integer triples |
| C05 | LGGR3.binary_defect_cancellation | MECHANIZED | actual binary triples (0,1,1) and (1,1,0) have nonzero defects 1 and -1 with zero sum |
| C06 | LGGR3.phone_totals | MECHANIZED | fixed five-trace sample |
| C07 | LGGR3.factorized_integer_kernel_has_zero_residual | MECHANIZED | flattened integer boundary products have zero residual; real exponential kernel remains open |
| C08 | LGGR3.quotient_evaluator_constant | MECHANIZED | any descended Boolean evaluator on arbitrary Setoid X is constant on each class |
| C09 | LGGR3.quotient_evaluator_obstruction | MECHANIZED | universally quantified mixed-verdict pair on arbitrary Setoid X rules out every descended evaluator |
| C10 | LGGR3.six_roles | MECHANIZED-PARTIAL | checks the declared list has six entries; no semantics of the roles |
| C11 | LGGR3.observer_weights_can_change_a_score | MECHANIZED | integer witness for S_w(R)=wR |
| C12 | LGGR3.fixed_observation_preserves_defect | MECHANIZED | unchanged integer triple |
| C13 | — | PROSE | no cochain complex is introduced |
| C14 / PL-025-6 | — | PROSE / OPEN | no task-specific detector-adequacy theorem |
| C15 | — | N/A | related-work comparison only |
| PL-025-8 | — | PROSE / OPEN | real nonnegative exponential kernel is not mechanized |

## Current replay

The source files were copied byte-for-byte to a short temporary directory to
avoid the Windows path-length limit of the repository checkout, then checked
with:

    lake build
    lake env lean check_axioms.lean

The build completed successfully. The census produced twelve theorem reports. Every
report was axiom-free or used only propext and Quot.sound. No theorem uses a
custom axiom, sorry, or admit.

The checked report is archived as `lean4/AXIOM_REPORT.txt` with SHA-256
`1445edf452eb719a6a55d7c6c69c163851f125570e7d00dab228a037a8745f8a`.

The verifier also extracts every `LGGR3.*` handle from this map, the claim
ledger, and the machine-readable claim map, then asks Lean to resolve all of
them against `Core.lean`. Older omnibus modules are retained outside the
public deposit for study. They are not imported by `Core.lean`, compiled by
the default target, or included in the deposit.
