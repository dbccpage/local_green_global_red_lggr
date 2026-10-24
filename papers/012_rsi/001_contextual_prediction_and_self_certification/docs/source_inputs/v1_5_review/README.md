# Contextual Prediction v1.5.0 — review evidence

Read `contextual_prediction_v1_5_review.md` for the verdict and its scope.

This is a review packet assembled from the attachments, not the author's complete
release. Sources under `code/`, `lean4/`, and `manuscript/` are copied unchanged;
filenames with upload suffixes are mapped back to their module names. The five
precursor Lean modules came from earlier attachments in this conversation.
`source_manifest.json` identifies each original filename, its source group, and
its hash. Original uploads were not edited.

Run the independent standard-library checks from this directory:

```bash
python3 independent_review.py
```

The script parses only literal integer/rational/list data from Lean fixture
definitions; it does not run Lean. Recorded results are in
`independent_results.json`.

To rerun the supplied Python tests, with pytest installed:

```bash
python3 -m pytest code/tests -q
```

The attached subset produced 86 passes and four FileNotFoundError failures for
missing release evidence/tools. Those failures are preserved in
`pytest_output.txt` and `pytest_results.xml`. They are not silently excluded.
The reported full-release audit and 71 Lean/Python execution comparisons require
additional files absent from this packet. No Lean build was performed here.

The source/formula checks in `review_results.json` are static checks, not a
replacement for the absent author release verifier, Lean elaboration, or PDF QA.
