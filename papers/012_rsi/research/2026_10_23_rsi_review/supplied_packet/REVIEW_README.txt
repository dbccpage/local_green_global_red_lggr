RSI REVIEW REPRODUCTION PACKET — 2026-10-23

Read rsi_review_2026-10-23.txt first.

Reviewed commit: e15a9d4ac6298524ce370cae679314aa0fef7585
Repository directory: omega_engine_atlas/coda_atlas/F004_papers/012_rsi/000_relational_reasoning_and_rsi_impossibility

The original repository was not changed. Source identities are recorded in source_receipt.json.

Python negative controls:
  python reproduce_findings.py "/path/to/000_relational_reasoning_and_rsi_impossibility"

Requirements:
  Python 3.10+ (review used 3.12.14), NumPy, SciPy, and rustc on PATH.
  The missing NumPy/SciPy declarations are themselves one of the reviewed defects.
  The script imports the reviewed source without editing it.
  A confirmed finding means that a defect or scope counterexample was reproduced.

Lean negative controls:
  In the original paper's lean4 directory, using its pinned Lean 4.35.0:
    lake build
    lake env lean "/path/to/ReviewCountermodels.lean"

Repository verification:
  In the paper directory:
    python -X utf8 -m pytest code/tests/test_rsi_impossible_lean_verification.py code/tests/test_architecture_and_value_objects.py -q
    python -X utf8 verify_deposit.py --test --lean

Observed:
  Canonical 79 tests + 5 architecture tests: 84 passed.
  Lean build and 40-entry census: pass.
  Four reviewer Lean checks: pass (one propext dependency, three axiom-free).
  Deposit verification: fail on three stale hashes and archive mismatch.
  Eight reviewer Python/native negative controls: defects/scope counterexamples reproduced.

The Lean runtime on this execution host could not use its numeric /proc/PID/exe lookup.
proc_path_shim.c records the small runtime adapter used here; a normal host should not need it.
No compiler binary or proof source was patched.

