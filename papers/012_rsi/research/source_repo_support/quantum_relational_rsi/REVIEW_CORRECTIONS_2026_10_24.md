# Corrections to archived quantum relational RSI outputs (24 October 2026)

These model outputs are historical drafts, not current RSI package proofs.
The following corrections override their claim-status tables and summaries.

1. Round 3 Lemma 2.1: Phi1 = 0 iff each compared report agrees at the two latency endpoints. Constancy throughout the window is sufficient but unnecessary: A,B,A has equal endpoints and an interior change.
2. Round 3 Theorem Q.3.2(c), and Round 4 step C: withdraw the bound T_glue <= k0+1 inferred merely from an in-window change. With lag two, an alternating A,B,A,B sequence has endpoint agreement at every comparison. A refusal requires an actual endpoint mismatch on a covered edge.
3. Round 1 Theorem Q.1 proof step 5: withdraw the assertion that the transition into the first repeated report cannot improve. A,B,A with A strictly preferred to B refutes that step. A strictly improving prefix at every transition still cannot repeat a report under a fixed strict transitive order; apply transitivity along the entire prefix to obtain irreflexivity's contradiction.
4. Round 3 Theorem Q.4(c): withdraw the T-1 authorized-step bound from staleness at most T. The T=3 counterexample admits three steps. A lag-only bound needs an explicit indexing convention and endpoint mismatch hypothesis; it is not established by this draft.
5. OmegaQuantumRelationalRsi/Core.lean: the executable predicate checks endpoints; its docstring now states that scope. No stronger in-window constancy theorem is inferred.

The original output bodies remain below their notices for provenance.
