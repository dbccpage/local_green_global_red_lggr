# Composition Gate (`lggr_guard`)

**AuthorityEffect: None.** The gate returns evidence and a verdict, and your owner rules still decide what merges.

## The problem

Change **A** makes the pre-review check configurable, with the default left on. Change **B** hardens the config loader to reject unknown keys. Each one passes review alone. Git merges them without a conflict. Together, B drops A's key, the default falls back to `False`, and the precheck silently stops bouncing anything.

Each reviewer saw one clean diff. The failure exists only in the composition. That is **Local Green, Global Red (LGGR)**.

## Try it (no install, no API calls)

```console
git clone https://github.com/dbccpage/local_green_global_red_lggr.git && cd local_green_global_red_lggr
python -m lggr_guard.ledger_demo
```

```text
A alone on main                COMPOSITION_VERIFIED    A
B alone on main                COMPOSITION_VERIFIED    B
B after A accepted             LOCAL_GREEN_GLOBAL_RED  A+B      precheck-on-by-default   UNDECLARED_EFFECT
C disables precheck default    LOCAL_RED               C        precheck-on-by-default   UNDECLARED_EFFECT
D also edits the suite         AUTHORITY_REQUIRED      D        PROTECTED_PATH           LOCAL_RED, UNDECLARED_EFFECT
F undeclared, contracts green  MODEL_MISMATCH          F        UNDECLARED_EFFECT
F' same diff, declared         COMPOSITION_VERIFIED    F'
E2 after E1 (drift)            LOCAL_GREEN_GLOBAL_RED  E1+E2    threshold-drift
```

`python -m lggr_guard.demo` shows batch mode, which also covers **reviewer drift**: frozen past decisions are replayed against the hosted reviewer.

## What it does

| Gap | Mechanism |
|---|---|
| Two acceptable changes add up to a broken system | Each candidate is replayed on the last checkpoint plus **everything accepted since**, in a temporary git worktree. On failure the receipt names the 1-minimal set of changes and the contract they jointly break. |
| Small steps add up to drift | `drift_budget` measures against the **owner-approved anchor**, not the previous step. |
| A change does something it did not declare | **Model-mismatch alarm**. It compares the declared effects with what the host observed, and it fails closed on unknown facts, out-of-domain values and observer crashes. In our 3,600-session swarm experiment, every false accept came from out-of-model cases. |
| A branch weakens the checks that judge it | Contracts, observer and protected paths are read from `main` with `git show`. A candidate that edits them gets `AUTHORITY_REQUIRED`, and main's version is used anyway. |
| A gate quietly loses power | Every contract has a known-bad **probe** that runs before every check. |
| A red post-merge smoke test | `blame` names which pending set to revert. |
| The hosted reviewer changes under you | `FrozenDecisions` replays owner-confirmed cases and raises an alarm on disagreement. |
| "How do we know what happened?" | A hash-chained, append-only ledger stored in `.git/`. A tampered ledger refuses to load. |

## Wire it in

```console
python -m lggr_guard init --approved-by owner
python -m lggr_guard check  feature/x --declares '{"review.pass_threshold": 87}'   # exit 0 = verified
python -m lggr_guard accept feature/x --declares '{"review.pass_threshold": 87}' --approved-by orchestrator
python -m lggr_guard checkpoint --smoke passed     # after a green post-merge smoke
python -m lggr_guard blame                         # after a red one
```

You write one file on main, `.lggr/suite.py`, which declares facts, contracts and an observer. See [LEDGER.md](https://github.com/dbccpage/local_green_global_red_lggr/blob/main/lggr_guard/LEDGER.md) for the quick start, the Python API and the full status table. See [README.md](https://github.com/dbccpage/local_green_global_red_lggr/blob/main/lggr_guard/README.md) for batch mode.

## Limits

- The gate sees only the facts your observer reports, so a behaviour no fact covers stays invisible. `UNCOVERED_EFFECT` narrows this gap without closing it.
- The named set is 1-minimal: removing any one member makes the contract hold. A different, smaller set could also exist.
- The cost is O(n) to O(n²) compositions, where n is the number of changes since the last checkpoint. Checkpoint often.
- The observer runs candidate code, so sandbox it the way you sandbox your tests.
