# LGGR/RSI live swarm experiment

Live five-agent `claude-haiku-5-5` swarms on 400 generated multi-module tasks, comparing LGGR
(verdict-directed) evidence selection against uncertainty reduction under a fixed verification budget,
with live model controllers, repair continuations and an RSI memory study.

- [PROTOCOL.md](PROTOCOL.md): frozen protocol and recorded revisions
- [REPORT.md](REPORT.md): results; [RESULTS.json](RESULTS.json) (primary), [RESULTS_TRUST.json](RESULTS_TRUST.json),
  [RESULTS_SENSITIVITY.json](RESULTS_SENSITIVITY.json)
- Shared machinery: `code/operations/swarm/`; tests: `tests/test_lggr_rsi_swarm.py`

```bash
python -m experiments.lggr_rsi_swarm.generate                    # rewrite instances.json, print digest
python -m unittest tests.test_lggr_rsi_swarm                     # offline tests (no network)
python -m experiments.lggr_rsi_swarm.verify experiments/lggr_rsi_swarm/evidence/evaluation/*/
python -m experiments.lggr_rsi_swarm.analyze results experiments/lggr_rsi_swarm/evidence/evaluation
```

Live runs need `ANTHROPIC_API_KEY` (environment or the git-ignored repository `.env`) and the
`anthropic` SDK (2.3.0 was used); `numpy` for analysis. `python -m experiments.lggr_rsi_swarm.drive`
runs the evaluation chunks with a cumulative spend gate.
