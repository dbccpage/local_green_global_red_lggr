---
supplement_for: lesson_1000_01_local_green_global_red_foundations
---

# LGGR first calculation: feedback after your attempt

AuthorityEffect: None. Companion to the
[first calculation](lesson_1000_01_local_green_global_red_foundations.md).
These are finite worked answers, not a learner-outcome report or runtime receipt.

## Feedback A: verdict arithmetic

For `(E1,E2,Eg)=(1,0,1)`, the local product is `1*0=0` and the defect is
`1-0=+1`. A local check fails while the global check passes. Calling this `-1`
reverses the subtraction in the definition.

For `(0,1,0)`, the local product is zero and `Delta_E=0-0=0`. The global check
still fails. The word "agreement" describes the relationship between verdicts;
it does not convert failure into success.

Diagnostic step: write `global minus local product` in words before inserting
numbers. If you interpreted zero as universal success, compare the all-zero row
with the all-one row: both have zero defect and different global verdicts.

## Feedback B: independent transfer

1. The identifiers now agree and are nonempty, so `(E1,E2,Eg)=(1,1,1)`,
   local product `1` and defect `1-1=0`. The handoff input changed. Computing the
   defect did not itself repair the original unequal identifiers.
2. For `D=I`, `Q=[1,1]` and `v=(1,-1)`, `Dv=(1,-1)` is nonzero and
   `Q(Dv)=1-1=0`. Both required conditions hold. Reusing `(1,1)` from the worked
   example would give observation `2`, so a changed observer needs a fresh check.
3. The identity observer returns the same two coordinates it receives. If its
   output is zero, both coordinates of `Dv` are zero. Thus no nonzero reachable
   difference is invisible, and `rank(QD)=rank(D)=2` in this example.
4. In the original example, state difference `(1,1)` is nonzero while observer
   `[1,-1]` returns zero. To infer zero state difference from zero observation,
   the observer must have no nonzero kernel element among the reachable
   differences: `im(D) intersect ker(Q)={0}`. This is the declared soundness
   condition. An observer can have a kernel outside `im(D)` without violating it.

Suggested rubric: one point each for correct Boolean arithmetic, correct changed
observer multiplication, an explicit nonzero-state check, and the scope of the
inference in answer 4. Request a correction only for the failed subskill. This
rubric is instructional guidance; it has not been calibrated in a learner study.
