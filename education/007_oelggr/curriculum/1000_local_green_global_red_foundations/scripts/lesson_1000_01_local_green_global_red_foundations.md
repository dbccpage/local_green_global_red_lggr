# LGGR first calculation: narration and storyboard

AuthorityEffect: None. Source companion:
[first calculation](../concepts/lesson_1000_01_local_green_global_red_foundations.md).
Source revision: `f2d5e5f9a5babf4cdfe2265c1fbd1434d4d3caf3`.

**Production status:** written transcript and storyboard only. No audio or video
has been rendered or reviewed for this revised lesson. Timings below are planning
estimates. They are not measured recording lengths or synchronized captions.
The [video slot](../videos/) contains a placeholder at the inspected revision.

## Spoken transcript with pause points

"Two steps exchange an identifier. The first sends alpha. The second expects
beta. Each local check asks only whether its own word is nonempty. Both checks
pass. The global check asks whether the words agree. It fails. Pause: should two
local passes be enough to certify that handoff?

"Write the defect as global verdict minus the product of the local verdicts.
Here that is zero minus one times one, which equals minus one. Minus one means
local green, global red. The sign reports a disagreement. It does not repair the
handoff. A zero defect means agreement, which can include all checks failing.

"Try a different triple: local verdicts one and zero, global verdict one. Pause
and calculate before continuing. Multiply the local values first. Compare your
answer with feedback A on the separate answer page.

"Now use a second, rational model. The state change is the ordered pair one,
one. The identity map leaves it unchanged. The observer takes first coordinate
minus second coordinate. It reports zero. The state changed, but the observer
cannot see that direction. Both conditions matter: the state change is nonzero,
and its observation is zero.

"The all-zero state change is a wrong witness: it is invisible but is no change.
The pair one, zero is another wrong witness for this observer: it changes the
state, but its observation is one. Pause and name which condition each failed.

"For independent practice change the observer to first coordinate plus second
coordinate. Test the state change one, minus one. Then replace the observer by
the identity. Which state changes can the new observer miss? Find feedback B
only after your attempt.

"We calculated finite examples using supplied checks and matrices. The source
owner computes the signed Boolean defect and exact rational witness predicates.
The companion notebook is a separate Boolean teaching model whose exact source
completed nine code cells under Python three point twelve point ten. That run
does not invoke the Rust owner or execute the rational example. This is no
physical quantum derivation or terminal recording. Two existing rational Rust
owner cases were separately replayed; that record does not compare this Boolean
notebook with native output. Retain the actual inputs,
your calculation and the narrow conclusion."

## Visual and accessible production plan

| Segment, suggested time | Visual action and on-screen labels | Text alternative and production check |
| --- | --- | --- |
| Problem, 0:00–0:40 | Two boxes: output `alpha`, expected input `beta`; show the three check definitions. | Read both words and each predicate. Do not rely on box position or colour to explain mismatch. |
| Defect, 0:40–1:20 | Hold the input; reveal `E1=1`, `E2=1`, `Eg=0`, then `0-1*1=-1`. | Say "global minus local product." Keep signs visible and spell out minus one in captions. |
| Faded practice, 1:20–1:50 | Show `(1,0,1)` with the product and defect blank. | Give an explicit pause cue; do not reveal the answer in the same shot. Link the separate feedback page. |
| Blind spot, 1:50–2:40 | Show ordered pair `(1,1)`, identity `D`, observer row `[1,-1]`, output `0`. | Say "first coordinate minus second coordinate." Label state nonzero and observation zero separately. |
| Wrong controls, 2:40–3:20 | Show `(0,0)` and `(1,0)` in separate rows with both predicates. | Indicate each failed condition in words; no red/green-only verdicts. |
| Transfer and scope, 3:20–4:00 | Keep new observer `[1,1]` and candidate `(1,-1)` unresolved; end with actual evidence and open work. | Read the new sign aloud. Provide a text-only route to the exercise and feedback; avoid a success badge. |

Pronunciation: `Delta_E` is "delta E"; `Dv` is "D applied to v"; `Q(Dv)` is
"Q applied to the state difference"; `rank` is the number of independent
directions. Say the meaning before introducing each symbol.

## Before a recording can be marked delivered

Reconcile every spoken number with the source lesson. Record with learner pause
time; then create captions from that timed recording, describe the displayed
equations, and review playback with captions and without the visual. Link the
actual asset and record its review date only after it exists. This storyboard
does not supply a rendered lesson, synchronized captions or a usability trial.
