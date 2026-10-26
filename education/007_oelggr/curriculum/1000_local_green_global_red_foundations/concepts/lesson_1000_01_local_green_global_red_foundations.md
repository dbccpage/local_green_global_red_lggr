---
documentation_contract: symbol-game-documentation/v1
title: "First LGGR calculation: local checks, global failure and a blind spot"
kind: pedagogical-lesson
track: 1000_local_green_global_red_foundations
status: active
maturity: instructional
claim_status: finite-worked-example
authority_effect: "None"
source_revision: f2d5e5f9a5babf4cdfe2265c1fbd1434d4d3caf3
source_paths:
  - omega_engine/crates_rs/omega_local_green_global_red_lggr/src/lggr_engine.rs
  - omega_engine/crates_rs/omega_local_green_global_red_lggr/src/lggr_v.rs
verification_scope: nine exact-source Boolean teaching cells under Python 3.12.10 and two existing rational Rust unit cases; no Boolean-native parity or general proof
media_status: narration and storyboard only; no recording
---

# First LGGR calculation: when every local check passes

AuthorityEffect: None.

You will calculate a signed evaluator defect, find a concrete counterexample to
"all local checks pass, so the global check passes," and check one exact blind-spot
witness. You need signed arithmetic, Boolean values (0 means fail, 1 means pass)
and multiplication of a two-entry row by a two-entry column. Allow 20–30 minutes;
this is a study estimate, not a measured completion time.

Beginner route: work sections 1–3, attempt the faded exercise, then read the
matching answer. Expert route: inspect the two source owners in section 5,
complete the rational witness and explain the difference between a false witness
and an unavailable evaluation. Both routes end with the independent task.

## 1. State the checks before reading their verdicts

[Declared] A two-step pipeline exchanges an identifier. The first step outputs
`alpha`; the second step expects `beta`. Define three checks for this illustrative
pipeline:

- `E1`: the first identifier is nonempty.
- `E2`: the second identifier is nonempty.
- `Eg`: the identifiers agree, so the handoff can be joined.

These are deliberately different predicates. Each local check sees one identifier;
the global check compares both. Text alternative to a pipeline diagram: a first
box sends the word alpha to a second box whose input contract says beta. Both
words exist, but their equality check fails.

**Predict before calculating:** What are `E1`, `E2` and `Eg`? Would checking that
each word is nonempty establish that the two words are equal?

For this example they are `1`, `1` and `0`. The combined local verdict is the
product `E1*E2=1`. The signed evaluator defect is:

```text
Delta_E = Eg - E1*E2 = 0 - 1*1 = -1
```

The defect `-1` means local green, global red. It identifies disagreement between
the supplied verdicts; the arithmetic alone does not discover the cause. Here we
can name the cause because the example supplied the unequal identifiers.

## 2. Calculate every possible verdict combination

The next table enumerates the eight Boolean triples. They are abstract verdict
combinations, not eight states of the nonempty-identifier example: under that
example's particular predicates, equality of two empty words gives one specific
triple. Do not confuse a truth-table carrier with one application's reachable
states.

| E1 | E2 | Eg | E1*E2 | Delta_E | Read the result |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 | Local product and global verdict agree on failure. |
| 0 | 0 | 1 | 0 | +1 | A local failure accompanies global success. |
| 0 | 1 | 0 | 0 | 0 | Local product and global verdict agree on failure. |
| 0 | 1 | 1 | 0 | +1 | A local failure accompanies global success. |
| 1 | 0 | 0 | 0 | 0 | Local product and global verdict agree on failure. |
| 1 | 0 | 1 | 0 | +1 | A local failure accompanies global success. |
| 1 | 1 | 0 | 1 | -1 | Every local check passes; the global check fails. |
| 1 | 1 | 1 | 1 | 0 | All three checks pass. |

Only one triple has defect `-1`. Three have `+1`; four have `0`. A zero defect
means agreement, which includes agreement on failure. It is not a success badge.
The sign convention matters: reversing the subtraction reverses the meanings.

**Faded exercise:** A new run has verdicts `(1,0,1)`. Complete the local product
`__`, defect `__` and classification `__`. A second run has `(0,1,0)`. Is its
zero defect enough to call the pipeline successful? Write an answer before opening
[feedback A](lesson_1000_01_feedback.md#feedback-a-verdict-arithmetic).

## 3. A rational blind spot you can check directly

[Declared] This second model supplies rational matrices. `D` maps a candidate
change `v` to a state difference `Dv`. `Q` maps that state difference to an
observation. A nonzero difference that produces a zero observation is invisible
to this observer.

```text
D = [[1,0], [0,1]]      Q = [[1,-1]]      v = (1,1)
Dv = (1,1)             Q(Dv) = 1-1 = 0
```

Check **both** conditions: `Dv` is nonzero, and `Q(Dv)` is zero. The observer
cannot distinguish this change from no change, even though the state changed.
The two independent columns of `D` give `rank(D)=2`. `QD=[1,-1]` has one
independent row and gives `rank(QD)=1`. The observer has lost one state direction.

The actual LGGR V owner uses the exact condition
`im(D) intersect ker(Q) = {0}` for soundness, equivalently
`rank(QD)=rank(D)`. Here `im` means the state differences reachable through `D`;
`ker` means the inputs sent to zero. This example violates that condition.

**Wrong-witness control:** Taking `v=(0,0)` also gives `Q(Dv)=0`. It is not an
unsoundness witness because `Dv=0`. Taking `v=(1,0)` gives a nonzero `Dv`, but
`Q(Dv)=1`, so the observer detects it. Neither single condition is sufficient.

These rational equations and the Boolean evaluator defect answer different
questions. No automatic identification with the PFP quantities `phi1` or `gamma2`
is supplied here. For a finite-QM cochain certificate with its own equations, use
the [C4 certificate lesson](../../../../004_oepfp/levels/level_finite_qm_certificate_walkthrough.md).
Neither supplied finite example establishes a Born rule or physical QM bridge.

## 4. Independent task: change the check, then change the observer

Attempt these without reading the answer page. Keep your calculations.

1. In the identifier example replace `beta` with `alpha`. Compute all three
   verdicts, the local product and the defect. Explain what changed.
2. Keep `D` as the identity, replace `Q` with `[1,1]`, and try `v=(1,-1)`.
   Compute `Dv` and `Q(Dv)`. State whether it is a valid unsoundness witness.
3. Replace `Q` with the two-by-two identity. Can any nonzero `Dv` have zero
   observation? Justify your answer directly from the coordinates.
4. A learner says, "The observer returned zero, so the state difference is zero."
   Use one concrete pair above to refute the inference. State what extra property
   of the observer would license it on the reachable state differences.

Use [feedback B](lesson_1000_01_feedback.md#feedback-b-independent-transfer) only
after attempting all four. Completion requires correct signs, both witness
equations, and an explanation of why zero defect can include failure. If a sign
is wrong, revisit section 2; if a witness fails, recompute its two conditions
separately. Repeating a definition without diagnosing a changed input is not
completion of the transfer task.

## 5. Follow the actual owner and keep execution status visible

The inspected source revision is
`f2d5e5f9a5babf4cdfe2265c1fbd1434d4d3caf3`. These source paths exist at that
revision:

- [lggr_engine.rs](../../../../../../omega_engine/crates_rs/omega_local_green_global_red_lggr/src/lggr_engine.rs):
  `CompositionRecord::local_product` uses Boolean conjunction;
  `evaluator_gluing_defect` subtracts it from the supplied global verdict.
  `TraceLedger::resolve_boundary` independently compares the linked trace hashes.
  The defect function itself does not execute that boundary comparison.
- [lggr_v.rs](../../../../../../omega_engine/crates_rs/omega_local_green_global_red_lggr/src/lggr_v.rs):
  `check_soundness` returns exact ranks and, when unsound, a witness;
  `verify_unsoundness_witness` checks both equations on an admitted matrix profile.
- [Cargo.toml](../../../../../../omega_engine/crates_rs/omega_local_green_global_red_lggr/Cargo.toml):
  the directory is named `omega_local_green_global_red_lggr`, but its Cargo
  package is **`omega_epk`**. Use the actual package name in commands.

The following replay completed against the unchanged owner source. The
[native record](../../../../../../omega_engine_product_planning_office/plans/review_remediation/evidence/batch_11/native_owner_checks.json)
binds actual source hashes, command, cache settings and output. From the repository
root with Rust/Cargo and the locked dependencies available, the same selection is:

```powershell
cargo test -j 1 --manifest-path omega_engine/crates_rs/Cargo.toml -p omega_epk --lib lggr_v::tests::exact_soundness_ --offline --locked -- --test-threads=1
```

The completed result is **two passed**, zero failed, and **74 filtered out**.
These are the existing sound identity case and the unsound `[1,-1]` observer case.
The latter checks the witness equations using exact rational arithmetic. This
does not execute every transfer example or compare the Boolean teaching model
with native output. The run reused a build cache; its short duration is not a
cold-build estimate. A new replay can need substantial disk and time. A missing
dependency, compile failure or zero matching cases is not the recorded result.
Keep the source pin and recorded scope visible when comparing another revision.

The [companion notebook](../notebooks/lesson_1000_01_local_green_global_red_foundations.ipynb)
now contains a limited Boolean teaching model: a prediction before evaluation,
the identifier mismatch, all eight verdict triples, wrong-sign and malformed-input
controls, and transfer with separate feedback. An isolated replay under Python
3.12.10 completed all nine code cells with no error outputs on these exact source
bytes (SHA-256):

```text
b11276be8e5c43f7347d24c2e43cb52d3a0a44047281882ca2d759bf6c5b130f
```

The source notebook keeps outputs clear so you can commit your own predictions.
The [execution receipt](../../../../../../omega_engine_product_planning_office/plans/review_remediation/evidence/batch_11/execution_receipt.json)
links the actual executed output and runner log. The final-source replay explicitly
shut down its pinned kernel. Windows kernel compatibility and local TCP transport
warnings were reported; no warning-free claim is made. The notebook invokes no
Rust owner and does not compute the rational example. It establishes neither
native parity nor learner acquisition.

[Open] Boolean-native parity, runtime checks for the transfer examples and an
independent learner trial remain separate work. The [narration and storyboard](../scripts/lesson_1000_01_local_green_global_red_foundations.md)
are production inputs; this unit has no reviewed recording or timed captions.

A request outside the cell profile may return `BudgetUnknown` in the Rust
API (the host uses `BUDGET_UNKNOWN`). That is an unresolved evaluation under the
declared budget, not a mathematical sound or unsound verdict. The 4096-cell
profile does not bound rational bit size, upstream parsing or total runtime.

This page records source inspection, finite displayed arithmetic and the isolated
nine-cell Boolean notebook replay at the exact digest above. It records no new
provider run, host-route execution, Lean proof, media playback or learning outcome.
The separate two-case Rust replay supports only the recorded unit selection.
The dated architecture grade and documentation baseline remain unchanged.
