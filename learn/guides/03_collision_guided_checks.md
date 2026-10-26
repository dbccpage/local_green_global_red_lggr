# 03 Collision-guided check selection

**AuthorityEffect: None.** Recipe: [`recipes/check_selector.py`](../recipes/check_selector.py).

> **Measured, with a split result** ([swarm report](../../experiments/lggr_rsi_swarm/REPORT.md)). This recipe is a simplified form of selection policy C. The full policy was run on 400 generated instances, with 3 Claude Haiku 5.5 draws each and a budget of 4 of 16 units:
>
> - **As the host's own selector it helps.** C resolved **+26.8 points** more cases correctly than expected-uncertainty-reduction selection (B), with 95% CI [22.5, 30.9]. That is 76% versus 50% correct.
> - **As advice to a live agent it adds nothing.** Controllers given C's collision witness or B's ranking both reached about 85% correct, and so did controllers given no advice at all. The difference was −0.1 points, CI [−1.3, 1.3]. The agent already does what the advice suggests.
>
> The recipe's own numbers were not measured; the demo below is a four-row illustration.

**The bug.** A verifier can afford 4 of 16 check units. It buys cheap checks that pass in every plausible world, runs out of budget, and either defers or accepts on hope.

![Hypotheses by checks, with the two checks the selector buys](../img/check_selection.svg)

## The idea in one line

While a pass hypothesis and a fail hypothesis agree on everything you have observed, your verdict is undetermined. `StreamingFiberMonitor` names such a pair. Buy a check that tells them apart.

## Wire it in

1. Enumerate a finite hypothesis set from public contracts. Each hypothesis lists the outcome of every check and the global verdict:

   ```python
   {"id": "H2-key-mismatch", "verdict": "fail",
    "outcomes": {"unit_a": True, "unit_b": True, "lint": True, "schema": False, "fee_e2e": True}}
   ```

2. Price each check: `costs = {"unit_a": 1, "unit_b": 1, "lint": 1, "schema": 2, "fee_e2e": 2}`.
3. Let the host run the loop. `run_check` executes a real check outside the proposing agents:

   ```python
   from learn.recipes.check_selector import run
   result = run(hypotheses, costs, budget=4, run_check=execute_check)
   ```

4. Act on `result["decision"]`. The shared host rule never accepts while a fail hypothesis survives:

   | Survivors | Decision |
   | --- | --- |
   | all pass | `accept` |
   | all fail | `reject` |
   | both remain when budget runs out | `defer` |
   | none | `model_mismatch`: your hypothesis set is wrong |

5. Use the selector where the host decides without a model in the loop. That is the setting where it measured +26.8 points. If a live agent buys the checks, the advice did not change its accuracy in the experiment. Apply the host rule to what the agent bought anyway: agent and host verdicts agreed on 97–99% of sessions.

## What you will see

In the demo the clean world is H1. The selector buys `schema`, then `fee_e2e`, spends 4 units, and returns `accept`. In every other world it returns `reject` within budget. A cheapest-first toy policy spends 3 units on checks that are ✓ in every hypothesis and must defer. That is an illustration on four hand-made rows, not evidence.

```console
python learn/recipes/check_selector.py
```

## What it does not prove

The rule is only as good as the hypothesis set. A world you did not enumerate shows up as `model_mismatch` at best, and at worst survives as one you did enumerate.

The experiment hit exactly this. Every false accept by B or C at 4 units, and by every live agent, was on an out-of-model control, where the true world lay outside the declared hypotheses. Speed made it worse: at 4 units C made 46 false accepts against B's 24, because it resolved those cases faster and wrongly. Pass/fail checks alone cannot catch this, so add an explicit model-mismatch test before you trust an `accept`.

## Go deeper

[Lesson 07](../lessons/07_recursion_on_a_fixed_report.py) shows why another generation on the same report cannot beat the fiber ceiling, while a check that splits the fiber can. `StreamingToolAssistedFiberSplittingMonitor` in `lggr.streaming` is the monitor form of that claim.
