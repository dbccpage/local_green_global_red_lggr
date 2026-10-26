# lggr_guard: catch "Local Green, Global Red" before it merges

Two self-modifications can each pass your gate and still break the system together. A check
gets silently disabled, or a threshold drifts a little at a time until it no longer means
anything. This package makes that failure explicit **before merge** and names the culprits.

Pure Python standard library, no dependencies. Copy the `lggr_guard/` folder into your project,
or install this repository (`pip install -e .`).

## What it checks

| Your problem | What `lggr_guard` does |
|---|---|
| Two individually acceptable changes add up to a broken system | `compose_check` judges every change **alone** and **together** against the last accepted state. When each is green and the composition is red, it reports defect class **NGD** (local green, global red) and every **minimal failing subset**: the exact pair or triple that breaks it. |
| A change silently alters behaviour nobody declared | You expose observable behaviour (enabled checks, defaults, thresholds) with `observe(state) -> dict`. Each change declares which behaviours it may change. Any other difference in the composition is reported. It is marked **emergent** when no single change caused it, so it only exists in combination. |
| Many small steps add up to drift | `Metric(budget=...)` is measured against the **anchor**, the last owner-approved state, not the previous step. The report names the first change after which the total leaves the budget, even when every step was small. |
| A branch weakens the tests that judge it | Git mode resets the paths you `--protect` (probes, acceptance tests, gate config, spec) to `main` before running checks. Main judges the branch; the branch never judges itself. |
| The hosted reviewer changes under you | `FrozenDecisions` replays owner-confirmed past decisions and raises an alarm when the reviewer no longer agrees. Its verdicts are then treated as out-of-model until a human re-anchors. |
| "How do we know what happened?" | `DecisionLog` is an append-only, hash-chained JSONL record. Editing any past decision breaks the chain, and `verify()` says where. |

Nothing here approves anything: the gate returns evidence and a verdict, and your owner rules
still decide.

## 60-second demo

```bash
python -m lggr_guard.demo
```

It reproduces a real incident pattern. Change A makes the pre-review check configurable (default
stays on). Change B adopts a "fast" settings profile. Each passes the gate alone. Together, the
fast profile switches the check off:

```
verdict: reject   defect: NGD
minimal failing set: [make-precheck-configurable, adopt-fast-profile]
undeclared: precheck_enabled true -> false (emergent: no single change did it)
```

It then shows three 0.03 threshold relaxations, each fine alone, leaving a 0.05 budget after
the second one. Finally a reviewer update that stops flagging weakened tests is caught by
frozen-decision replay (agreement 0.90, alarm).

## In a pipeline (git branches)

Run it before merging the batch, for example in your orchestrator or merge queue:

```bash
python -m lggr_guard compose --base main \
    --branch feat-a --branch feat-b \
    --check "python -m pytest -q tests/probes tests/acceptance" \
    --protect tests/probes --protect tests/acceptance --protect gate_config.yaml \
    --observe "python tools/observe_behaviour.py" \
    --declare feat-a=parallelism --declare feat-b=review_threshold \
    --log decisions.jsonl
```

The exit status is 0 to accept and 1 to reject, with a JSON report. For up to 4 branches every
subset is checked (15 combinations). Beyond that it checks each branch alone plus all together. Each
run uses a temporary `git worktree`; nothing is merged or pushed.

`observe_behaviour.py` is yours. It prints JSON describing what the system will actually do,
for example `{"precheck_enabled": true, "review_threshold": 0.8, "gates": ["spec", "tests"]}`.
That is where emergent changes become visible.

## In code

```python
from lggr_guard import Change, Check, Metric, compose_check

report = compose_check(
    main_state,
    [Change("feat-a", apply_a, frozenset({"parallelism"})), Change("feat-b", apply_b)],
    [Check("gate rejects known-bad input", probe)],
    observe=observe,
    metrics=[Metric("review_threshold", lambda s: s["review_threshold"], budget=0.05)],
    anchor=last_approved_state,
)
if report["verdict"] == "reject":
    send_back(report["minimal_failing_sets"], report["undeclared"], report["reasons"])
```

## Why these pieces (evidence)

This repository includes a 3,600-session live experiment with Claude agent swarms
([report](https://github.com/dbccpage/local_green_global_red_lggr/blob/lggr-rsi-swarm-live/experiments/lggr_rsi_swarm/REPORT.md), PR #143). Two findings shaped this package:

1. **The deterministic host check carries the weight.** Applied to the same evidence, agents'
   verdicts and a fixed elimination rule had the same false-accept rate (3.5% vs 3.5%) and
   agreed 98-99% of the time. Better prompting or advice did not change agent outcomes. A
   mechanical gate that runs regardless of agent quality is what you can rely on.
2. **The failures that got through were all "out of model".** Every false accept, by agents
   and by the host rule, happened where reality had moved outside what the contracts
   declared. Pass/fail checks were fooled the same way. That is why `lggr_guard` adds explicit
   undeclared-behaviour detection and frozen-decision replay rather than only more checks.

## Limits

- Composition checking is exhaustive only for small batches (default up to 5 in-memory
  changes, 4 git branches). Larger batches get singletons plus the full composition; failures
  inside them are still caught, but the minimal witness may not be named.
- Probes and observed behaviours only see what you expose. A behaviour you do not observe can
  still drift. Frozen decisions only detect reviewer drift on the kinds of cases you froze.
- Drift budgets need a sensible anchor. Re-anchor deliberately, with an owner decision logged,
  not automatically.

AuthorityEffect: None.
