# Institutions That Can Know

**Jeremy H. Carroll · Working Paper 1 · Version 0.1 · October 23, 2026**

*Preserving Difference, Coordinating Action, and the Risks of Epistemic Collapse*

## Manuscript

`institutions_that_can_know.pdf` is the reading edition. The editable Word manuscript is `institutions_that_can_know.docx`; the repository-ready text is `institutions_that_can_know.md`.

The paper develops institutions as maintained capacities for memory, comparison, correction, bounded coordination, and succession. It proposes a comparison-and-recovery protocol for Anomalon Councils. Synthesis is an optional supported result rather than the compulsory endpoint of deliberation. The paper includes three elementary propositions with proofs, a local-to-global counterexample, an empirical evaluation design, and a claim-status register.

## Finite companion

Requires Python 3.10 or later; no third-party dependencies are needed for the tests.

From this directory, run:

```sh
python -m unittest -v test_institutional_reasoning.py
```

`institutional_reasoning.py` implements the finite examples. `test_institutional_reasoning.py` contains 17 tests, including two exhaustive checks of 216 cases each. `test_run.txt` and `execution_receipt.json` record an actual local run and hashes of the tested files.

The examples do not validate the performance of an AI council or a human institution. The mandate object is a sandbox fixture, not an authentication or security implementation. A Boolean named `externally_verified` is not a real authorization process.

## Proposed contract

`anomalon_institutional_reasoning.contract.yaml` is an illustrative research contract and synthetic packet, not a deployed Omega Engine schema. It retains two explanations, demonstrates a common proposed action, records missing evidence, and withholds execution authority.

## Sources and integrity

The manuscript contains 16 references. `source_register.json` records the scope of source inspection and the two repository document paths at the inspected commit. These were read as design documents; the full current codebase was not audited and its tests were not rerun.

`manifest.sha256` identifies all included deliverables other than itself. Hashes establish file identity, not the truth of their contents. No existing repository was modified and nothing was published.

**Status:** prepared for author review; conceptual paper and proposed architecture.

**AuthorityEffect:** None.
