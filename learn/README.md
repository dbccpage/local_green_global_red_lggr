# Instrument your own harness

**AuthorityEffect: None.**

This course shows a harness author how to use the LGGR and RSI checks on events their own loop already has. The checks live in the stdlib package `lggr`. The papers stay the proof record. Nothing here calls a model, admits an authority, or clears an obligation.

Run it from the repository root with Python 3.10 or newer. Installing the package is unnecessary.

```console
python learn/check.py
python learn/lessons/01_same_summary_different_job.py
python -m unittest tests/test_learn_path.py -v
```

`learn/check.py` replays the prepared half of all ten lessons and prints one line each: lesson id, receipt schema, status. Exit 0 means those statuses match. Each script also has a your-turn dict. Edit that dict to point the same monitor at your own field names. The test suite does not read the your-turn dict.

## How long

| Time | Lessons | You leave able to |
| --- | --- | --- |
| 20 minutes | 00, 01, 07 | Name the query, catch a report collision, and see a fiber-width ceiling |
| One afternoon | 00–09 | Wire a tool loop, a handoff, and a review cycle |
| After that | Papers listed in each lesson | Read the scoped proof that matches the receipt you just held |

The four scripts in `cookbooks/` are short demos of the same monitors. Start here when you need to know which object in your harness is the report and which is the query.

## The ten lessons

| Lesson | Question the receipt answers |
| --- | --- |
| 00 Name the question | Is there a declared scope, report, and query yet? |
| 01 Same summary, different job | Do two states share a report and differ on the query? |
| 02 Local green is not the global question | What is `Delta_E` when the global sample is supplied from outside? |
| 03 A prefix is not an endpoint | Does the bound have to hold on the way, or only at the end? |
| 04 The review cycle | Does the cycle close, and what is the exact repair distance? |
| 05 Moving the ledger | Does the new encoding preserve repairs, and does it reflect nonrepairability? |
| 06 A boundary that holds | On this supplied table, is the report constant on the query and are the steps glued? |
| 07 Another generation on the same report | Does a new predictor that still sees only the coarse report undercut the half-spread? |
| 08 Three ways a loop stops | Which receipt is a report collision, a budget stop, or a gluing refusal? |
| 09 The pass comes from outside | Who supplied the global sample, and which obligations are still open? |

Copy `HARNESS_CONTRACT.md` if your harness is not Python. `harness_adapter.py` is one reference wiring of that contract.

## After the course

These monitors are in `lggr.streaming` and are not on the core path. Each line is the class docstring's subject, so you can open the class when a receipt from the course is too coarse for the question you actually have.

| Monitor | Subject |
| --- | --- |
| `StreamingPositiveExtensionMonitor` | Observer-fiber minimax floor and positive-extension order |
| `StreamingTransportMonitor` | Streaming chain retraction and coarse-graining |
| `StreamingPathKernelMonitor` | LGGR I / III evaluated path kernels |
| `StreamingOrganizationalGluingMonitor` | LGGR II organizational gluing and carrier mixing |
| `StreamingCoalitionalAttributionMonitor` | LGGR II Shapley attribution against a raw defect |
| `StreamingSixRoleOverlayMonitor` | LGGR III six accounting roles |
| `StreamingDefectSoundnessMonitor` | LGGR V realizable-defect soundness |
| `StreamingGramProbeMonitor` | LGGR VI Gram nullspace and adjoint probes |
| `StreamingProductRetractionMonitor` | LGGR VII product-state retraction versus a separable extension |
| `StreamingBellPolytopeMonitor` | CHSH behavior tables, visibility, negative mass |
| `StreamingDashboardAdequacyMonitor` | Dashboard collapse of a detector |
| `StreamingBaselineComparator` | Ordinary baseline arithmetic beside the audit |
| `StreamingWindowedDriftMonitor` | Sliding-window budget versus the full horizon |
| `StreamingReplayOrderMonitor` | Prefix budget when step order is permuted |
| `StreamingThresholdGovernanceMonitor` | k-of-n quorum versus a strict product |
| `StreamingCPTPTraceMonitor` | Rational channel trace residual on a supplied matrix |
| `StreamingDFAGrammarGluingMonitor` | Finite-automaton tape concatenation |
| `StreamingMayerVietorisMonitor` | A declared cover and its connecting defect |
| `StreamingSimplicialCupMonitor` | Cup product on a supplied simplex |
| `StreamingHodgeDecompositionMonitor` | Orthogonal decomposition over the rationals |

Paper 000 (*Relational Reasoning, Memory, and Embedded Knowledge*) is the reading for lesson 07 and lesson 08. Its current edition keeps scoped finite-carrier bounds and constructive memory results. This course uses that wording. Paper 002's four-role council protocol remains proposed. The glossary says where that sentence sits.
