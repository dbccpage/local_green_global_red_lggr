# Contextual Prediction and Self-Certification

Version 1.8.3, 2026-10-23.

Finite contextuality duality and exact-rational simplex with checked optimal, infeasible and unbounded outcomes, extended with embedded knowledge, attained scalar minimax certificates, future-memory capacity, total-variation loss transfer and correct finite-budget binary observation planning. Includes standalone sources, exact checkers, complete axiom censuses and offline Lean dependencies.

Source and theorem mapping: [embedded_research.md](embedded_research.md).


The retained v1.8.2 verification records that the repaired quantum library passed all 712 tests in release mode, with no failures, ignored cases or filtered cases. This includes the three prior numerical failures, all ten previously unfinished MUB tests, and three new admission-boundary regressions. Exact PSD of the supplied binary Choi matrix replaces a rounded eigenvalue-sign decision. Floating-point Hamiltonian evolution uses a separate tolerance-checked numerical propagator; exact admission remains strict, and numerical evolution retains norm drift. The rebuilt native budget host passes all 24 gateway-and-memory tests, including both previously blocked cases; five quantum integration binaries pass 57 tests. These are scoped checks of the recorded v1.8.2 sources, not new v1.8.3 executions. The earlier multi-crate audit remains historical, and these synthetic gateway tests add no new live model trial or universal implementation-refinement proof.
