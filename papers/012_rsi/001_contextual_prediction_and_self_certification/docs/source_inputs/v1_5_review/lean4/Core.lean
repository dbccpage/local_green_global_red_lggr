import ResultI
import ResultII
import ResultIII
import ResultIV
import Bridge
import ContextualDuality
import RationalCertificates
import Simplex
import ErrorBudget

/-!
# Epistemic no-go: root module

Imports the four inherited result modules, the RSI bridge, full finite
contextuality LP duality, and generated exact rational certificates.
Mathlib dependencies, sources, licenses and compiled modules are vendored
offline and pinned to Lean 4.33.1. A build needs no network access.

Scope in one line each:

* `ResultI`   support-level strong contextuality of the 4-cycle (PR box) and a
              classical global section. This historical module is supplemented
              by general duality and exact numerical certificates below.
* `ResultII`  the fiber lemma, its corollary for a boundary map with a
              nontrivial fiber, and the swap-dynamics witness.
* `ResultIII` hash-chain prefixes verify (completeness needs an external tip)
              and relabeling blindness of invariant verdicts.
* `ResultIV`  a Lean model of the three-role gate and its refusal and
              soundness statements.

`ContextualDuality` proves finite real primal/dual attainment, the canonical
maximum form, the contextuality alternative, standard-form residual bounds,
and exact rational certificate soundness against all real competitors.
`RationalCertificates` checks five concrete outputs of the standalone solver.
`Simplex` is an executable two-phase rational solver with structural finite-
budget termination, pivot invariants, exact budget accounting and successful-
return optimality. `SimplexDriver` exposes exact execution separately.
`ErrorBudget` proves conditional trajectory, observation and correction bounds.
Not mechanised: unbudgeted Bland completeness, universal Python refinement,
Tarski and Löb, privacy without a dynamics premise, or Rust/Python equivalence.
-/
