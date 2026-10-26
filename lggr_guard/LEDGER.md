# lggr_guard ledger mode: gate each change against everything accepted since the last full check

**AuthorityEffect: None.** A receipt is evidence for your merge rule. It does not merge anything.

Two changes each pass review. Merged together they break a contract. Per-PR review cannot see this, because each reviewer sees one diff against main. That is **Local Green, Global Red (LGGR)**.

Ledger mode replays a candidate on top of **everything accepted since the last full check**. It evaluates your contracts on the result. When one breaks, the receipt names the smallest set of changes that breaks it, together with the contract:

```text
B after A accepted   LOCAL_GREEN_GLOBAL_RED  A+B  precheck-on-by-default  UNDECLARED_EFFECT
```

It is Python 3.10+ and standard library only. It makes no model calls.

## 60-second demo

```console
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

The demo builds a throwaway git repo with a toy review gate. The gate has a precheck that sends undeclared behaviour changes back to the worker.

| Change | Diff | Alone |
|---|---|---|
| **A** "make precheck configurable" | `enabled()` returns `cfg.get("precheck_enabled", False)`, and `defaults.json` gains `"precheck_enabled": true` | green |
| **B** "reject unknown config keys" | `config.load()` keeps only `KNOWN_KEYS = {review_model, max_diff_lines}` | green |
| **A + B** | B filters out A's key, so the `False` default wins and the precheck silently stops bouncing anything | **red** |

Git merges A and B without a conflict, and each diff reads as clean. The precheck is disabled only when both are present. Rows C and D are the single-change version, where a later self-modification turns the check off by default. Row F shows the model-mismatch alarm: every contract still holds, but the change altered a fact it never declared. Row E is cumulative drift: two threshold relaxations, each within budget, are outside it together.

`python -m lggr_guard.ledger_demo --json` prints the full receipts.

## Quick start on your repo

**1. Write `.lggr/suite.py` on main.** The gate reads it from `main` with `git show`, never from the candidate's branch.

```python
from lggr_guard import Contract, Fact, Suite, drift_budget, equals, run_json

OBSERVE = r"""
import json
from mybot import gate, config
cfg = config.load()
print(json.dumps({
    "precheck.bounces_undeclared": gate.precheck({"undeclared_behaviour": True}, cfg) == "BOUNCE",  # probe
    "review.model": cfg["review_model"],
    "review.pass_threshold": cfg["pass_threshold_pct"],
}))
"""

SUITE = Suite(
    facts=(Fact("precheck.bounces_undeclared", (True, False)),
           Fact("review.model", ("opus", "sonnet")),
           Fact("review.pass_threshold")),
    contracts=(equals("precheck-on-by-default", "precheck.bounces_undeclared", True),
               equals("reviewer-is-opus", "review.model", "opus"),
               drift_budget("threshold-drift", "review.pass_threshold", 5)),   # vs owner anchor, not vs last step
    observe=lambda worktree: run_json(worktree, OBSERVE),
    protected_paths=(".lggr/", "specs/", "prompts/", "tests/protected/"),
)
```

**2. Run it from the host, not from a worker.**

```console
python -m lggr_guard init --approved-by owner          # checkpoint main, anchor its facts
python -m lggr_guard check  feature/x --declares '{"review.pass_threshold": 87}'
python -m lggr_guard accept feature/x --declares '{"review.pass_threshold": 87}' --approved-by orchestrator
# ...merge, run the post-merge smoke...
python -m lggr_guard checkpoint --smoke passed         # smoke green: pending resets, anchor stays
python -m lggr_guard blame                             # smoke red: which pending set broke which contract
```

Exit code 0 means `COMPOSITION_VERIFIED`, and anything else exits 1. By default the ledger lives at `.git/lggr-guard/ledger.jsonl`. That path is outside every branch, so no PR can change it. Every entry is hash-chained, and a tampered ledger refuses to load.

**Or call it from Python** (for example, inside your orchestrator's merge step):

```python
from lggr_guard import CompositionGate, GitComposer, Ledger, candidate_from_branch, load_suite_from_ref

ledger = Ledger.load(".git/lggr-guard/ledger.jsonl")
suite = load_suite_from_ref(".", "main")
gate = CompositionGate(suite, GitComposer(".", ledger.checkpoint["ref"], suite.observe), ledger)
change = candidate_from_branch(".", "feature/x", "main", declares={"review.pass_threshold": 87})
receipt = gate.check(change)
if receipt["allowed"]:
    send_to_reviewer(change, receipt)            # the old reviewer still decides
else:
    return_to_worker(change, receipt["findings"])
```

## What the receipt says

| Status (most severe first) | Meaning |
|---|---|
| `GUARD_PROBE_FAILED` | A contract accepted its own known-bad probe. The gate stops because it has lost power. |
| `AUTHORITY_REQUIRED` | The candidate edits a protected path, or the pending changes were accepted under a different suite. |
| `MERGE_CONFLICT` | The candidate does not apply on top of the pending set. The receipt names the conflicting changes. |
| `LOCAL_RED` | The candidate breaks a contract on its own. |
| `LOCAL_GREEN_GLOBAL_RED` | `changes` jointly break `contract`. Dropping any one of them makes it hold. |
| `MODEL_MISMATCH` | Something was observed outside the declared model: an undeclared effect, a declared effect that did not happen, an effect no contract reads, an unknown fact, a value outside the fact's domain, or an observer crash. The gate fails closed. |
| `COMPOSITION_VERIFIED` | Every contract holds on the composition, and every observed effect was declared. |

The receipt also carries `unresolved_obligations`, which stay open until the owner runs `clear`. It also carries `declaration_sufficiency`, from the repo's report-collision monitor. `REPORT_INSUFFICIENT` there means two changes with the same declaration had different observed effects, so declarations alone do not tell you what a change does.

## How it maps onto a self-modifying gate

| Your rule | Ledger mode |
|---|---|
| Gate, specs, prompts and protected tests are read from main | `load_suite_from_ref(repo, "main")`. Candidate edits to `protected_paths` give `AUTHORITY_REQUIRED`, and main's version is used anyway. |
| The old reviewer judges every change | The guard runs before the reviewer and adds a second witness. It is deterministic code, so a provider-side model update does not change it. |
| Every gate has a probe it must still reject | `Contract.probe` runs before every check. The observer itself can also run a known-bad input, as `precheck.bounces_undeclared` does. |
| Post-merge smoke tests with rollback | `checkpoint` after a green smoke. After a red one, `blame` names which pending set to revert. |
| A precheck flags undeclared behaviour changes | `UNDECLARED_EFFECT` compares the declaration with what the host observed, on the composition. |
| **Gap: two acceptable changes add up to drift** | The ledger plus the composition replay, plus `drift_budget` against an owner-approved anchor rather than the previous step. |

## Limits

- The gate sees only the facts your observer reports. A behaviour no fact covers is invisible to it, which is the same gap your probes have. `UNCOVERED_EFFECT` and `UNDECLARED_FACT` narrow this gap without closing it.
- The named set is 1-minimal: removing any one member makes the contract hold. A smaller set made of different changes could also exist.
- The cost is `O(n)` compositions when one change is to blame and `O(n²)` in the worst case, where n is the number of changes accepted since the last checkpoint. Checkpoint often.
- The observer executes candidate code in a temporary worktree, so sandbox it the way you sandbox your tests.
- `--approved-by` records a name. It does not authenticate anyone. Keep the CLI and the ledger on the host side.

Tests: `python -m unittest tests.test_lggr_guard_ledger -v`. Batch mode (`compose_check`, `FrozenDecisions` for reviewer drift): [README.md](README.md). Background: [learn/guides/02_authority_firewall.md](../learn/guides/02_authority_firewall.md) and [learn/guides/01_report_collision.md](../learn/guides/01_report_collision.md).
