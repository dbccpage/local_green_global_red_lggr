# Break-and-recover mutation matrix — LGGR III

**Date:** 2026-10-15\
**Harness:** code/tests/test_invasive_injections.py

Each case first injects a malformed or misleading state and then checks the
corresponding lawful recovery path.

| # | injected fault | required interception | recovery |
|---:|---|---|---|
| 1 | non-binary verdict | InvalidVerdictError | binary triple accepted |
| 2 | one compatible segment pair omitted | G1 missing-pair report | restore the omitted composite |
| 3 | two composites name the same compatible pair | G1 duplicate-pair report | retain one composite per pair |
| 4 | composite names an unknown segment | G1 report and downstream hypotheses false | declare the referenced segment |
| 5 | segment endpoints do not share a boundary | G1 incompatibility report | restore the common boundary |
| 6 | composite cost differs from segment-cost sum | computed G2 false | restore the additive cost |
| 7 | composite verdict differs from the local product | computed G3 false | restore the product verdict |
| 8 | composite proposal mass differs from the segment product | computed G4 false | restore the product mass |
| 9 | $+1$ and $-1$ hidden by aggregate zero | cancellation flag | retain and inspect the pointwise list |
| 10 | evaluator varies inside one computed quotient class | QuotientDescentError | refine partition by verdict (descent on refined quotient) |
| 11 | constant evaluator output sample | DetectorAdequacyError | supply a sample that witnesses both outputs |
| 12 | post-integration verdict triple changed | ObservationChangedError | compare an actually fixed triple |

*Note on mutation 10:* Splitting an equivalence class according to verdict alters the equivalence relation, producing a finer partition and a refined quotient. This demonstrates descent through the refined quotient projection $\bar{E} \colon X/{\sim'} \to \{0,1\}$, not repair while preserving the original equivalence relation $\sim$.

The matrix is an executable falsifier, not a detector-adequacy proof. Every
row performs both the break and the recovery in the same test. Final pass
counts and coverage are reported only after source and manifest bytes are
fixed.

