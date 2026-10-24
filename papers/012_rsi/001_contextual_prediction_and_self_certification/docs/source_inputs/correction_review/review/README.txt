CONTEXTUAL PREDICTION: REVIEW AND QUANTITATIVE EXTENSIONS
21 October 2026

Read contextual_prediction_review.pdf for findings, assumptions, proofs,
prior-art attribution, and the limits of the fresh verification.

Run from this directory:
    python3 run_review_checks.py

Python 3, standard library only. The runner writes verification.json.
No API keys, external services, or installed LP package are required.
This is research reference code, not a production input boundary or a
formally verified implementation.

originals/ contains unchanged copies of the 19 supplied revision files.
proposed/contextuality_lp.py is a separate copy with the proposed validation
repair. contextuality_lp_validation.patch applies to the original module.
Neither the original uploads nor the user's manuscript were overwritten.

The proposed input contract accepts ordinary list/tuple Scenario fields,
canonicalizes context lists, and refuses malformed containers and indices
before sorting or hashing. Other low-level APIs retain their typed-input
preconditions. This patch is not a universal hostile-object deserializer.

quantitative_prediction.py adds:
  1. A replayed witness bound for an l1 uncertainty ball.
  2. Exact convex-hull separation for polytope uncertainty sets, using the
     original distance LP on pair differences, plus independent replay.
  3. Finite transition-kernel leakage bounds, transcript enumeration for a
     pure history-based policy, and the sharp four-state reveal example.

The transcript function expects the same policy in each world. The policy
must depend only on its history and return an exact action distribution.
It must not query hidden state or mutate external state. A finite enumeration
is a check of that instance, not a proof of the general coupling theorem.

Fresh checks: five exact fixture values; 130 independent dual-vertex LP
comparisons; 30 defect-certificate mutations; nine input-boundary cases;
256 deterministic update cases; 30 uncertainty-ball cases and 30 rejected
hull-certificate mutations; 360 stochastic pair/horizon checks; 28 sharp
reveal examples. Seed: 20261021. See verification.json for exact results.

Lean source was reviewed but NOT freshly compiled. Lean/lake and the full
pinned build/audit package are absent. General arguments for the extensions
are prose proofs. No new Lean formalization or upstream release audit is
claimed. The originals directory is an attachment snapshot, not a complete
reproducible upstream release.

To rebuild the PDF (requires LaTeX packages listed in the TeX file):
    pdflatex -interaction=nonstopmode -halt-on-error contextual_prediction_review.tex

source_manifest.json binds the attachment snapshot. SHA256SUMS binds this
packet's files except itself. These are provenance checks, not proofs of
mathematical validity or authority.
