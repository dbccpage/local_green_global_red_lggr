# Swarm laboratory: review revision v2

This runnable source revision repairs auxiliary-query admission and deterministic replay. It is derived from the [published v1 archive](../dist/lggr-swarm-lab-2026-10-24.zip), whose bytes and historical results are unchanged (SHA-256 `fd233b5e24a388c996a0fc4a63a53175efce6dad89c412a169b487b68da26a9a`). The original archive contains the complete original source, protocol, receipts, results and reproduction commands.

From this directory, using Python 3.10 or newer, run:

```sh
python -m lggr_swarm_lab tests
python -m lggr_swarm_lab demo --output demo-results
python -m lggr_swarm_lab benchmark --split development --output development-results
python -m lggr_swarm_lab benchmark --split evaluation --output evaluation-results
python -m lggr_swarm_lab replay evaluation-results/runs/evaluation.branch_join.00.C.json
```

Output directories must be fresh. All operations are offline SQLite computations; no model API requests are made. The vendored LGGR modules retain their original bytes.

Required auxiliary declarations accept a query ID or a dictionary with `query_id`, optional `scope`, and optional `baseline`. Every requirement needs matching known evidence before final admission. Endpoint samples must be terminal. Missing/unknown evidence defers; retained negative evidence blocks. The independent judge implements these checks independently of the controller.

New interactive and fixed-trace receipts use v2 schemas. Replay regenerates decisions, verdict labels, and deterministic counters. Wall-clock timings remain measurements, not replay-certified facts. v1 receipts are historical evidence: use the unchanged ZIP for original reproduction, or rerun their inputs through v2 for revised verification. The `evidence/native/` files are copied original proposals and historical runs, not newly collected agent output.

This revision is a post-review regression exercise on already published fixtures, not a new blinded experiment. The original B/C agreement and costs are finite integration evidence, not proof of a reliability or cost advantage. The revised protocol and source freeze identify this run separately.

The [v2 regression results](evidence/review-v2-results.json) contain 144 interactive runs and 48 fixed-evidence comparisons, with no replay failures. B and C each produce 33 correct commits, six blocks and nine deferrals; B consumes 309 attempts and C consumes 310. All 48 saved fixed traces also pass the v2 file replayer. These unchanged aggregate outcomes do not erase the extra adversarial cases in `tests/test_review_regressions.py`.

The [complete v2 run archive](evidence/review-v2-evaluation.zip) retains every interactive trace, fixed trace, replay receipt and command log. Extract it into a fresh directory and pass a saved run or fixed-trace path to the v2 `replay` command above. Archive SHA-256: `d27bd923fed1d6df1bce0071e58f5d5df3bd98c71bf55e385f761667c0e82028`.
