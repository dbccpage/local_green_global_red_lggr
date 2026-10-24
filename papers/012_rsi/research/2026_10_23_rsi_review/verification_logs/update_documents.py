from pathlib import Path
import json

root=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\000_relational_reasoning_and_rsi_impossibility')
for name in ('README.md','pyproject.toml','zenodo_metadata.json','docs/descriptions.md',
             'lean4/lakefile.lean','relational_reasoning_and_rsi_impossibility_monograph.md'):
    p=root/name
    p.write_text(p.read_text(encoding='utf-8').replace('1.2.2','1.2.3'),encoding='utf-8',newline='\n')
p=root/'README.md'
s=p.read_text(encoding='utf-8').replace('Python kernels use the standard library, tests need pytest, and the older parity checks additionally need rustc.',
    'Memory and finite-limit kernels use the standard library. The cochain solver requires NumPy and SciPy (declared wheel dependencies); tests need pytest. Native metadata parity requires rustc.')
s=s.replace('```text\npython -m pytest', '```text\npython -m pip install .\npython -m pytest',1)
s+='''
The independent October 23 review is reconciled in
[the finding-by-finding response](docs/review_response_2026_10_23.md).
The cochain solver reconstructs and independently checks exact rational
certificates; closure alone never licenses an exactness claim. The transition
CLI delegates to the same modules as the tests. Its numeric threshold policy
checks `internal_eval >= N` before report collision, so score units are part of
the declared model. The reported `N+1` transition ceiling is loose; a fixed
N-report interface forces a repeated report by transition index N.

`rsi-transitions --json` (or `python -m rsi_transition_harness --json`) runs the
packaged examples. `rsi-memory` provides the local persistent-memory interface.
Rust results are explicitly EIS metadata/digest parity, not obstruction replay
or authenticated verifier independence. The identifier policy rejects Unicode
and unsupported wire inputs. The asynchronous distribution uses controlled
synthetic defect injection, including an age penalty for equal content.

To test the installed wheel in a fresh virtual environment outside the source
tree, run `python tools/verify_installed_wheel.py`. This builds with local
setuptools and installs declared dependencies from the configured package index;
`--wheelhouse PATH` instead uses a supplied directory of NumPy/SciPy wheels.
The standalone archive includes source, tests and resources but not Python,
NumPy/SciPy binaries, rustc, Lean 4.35.0 or rendering tools. Clean extraction
checks use these declared installed prerequisites, no sibling repository source.
The prior 712/57/24 Rust results above are preserved earlier evidence, not new
executions in version 1.2.3.
'''
p.write_text(s,encoding='utf-8',newline='\n')
p=root/'relational_reasoning_and_rsi_impossibility_monograph.md'
s=p.read_text(encoding='utf-8')
s=s.replace('The original `RsiImpossible.lean` and `RelationalRsiNoGo.lean` remain unchanged. A duplicate-free list contained in a carrier of size N has length at most N. `OmegaRelationalRsi.rsi_impossible` applies this directly to a stipulated list of N+1 distinct reports. Separately, `lemma1c_goodhart_metric_collapse_on_collision` shows that strict, transitive, irreflexive dominance cannot remain grounded in a report map across a repeated report. Both premises must be checked before using the collision as evidence about improvement.',
'''The original `RsiImpossible.lean` and `RelationalRsiNoGo.lean` retain their definitions and theorem statements. A duplicate-free list contained in a carrier of size N has length at most N. `OmegaRelationalRsi.rsi_impossible` rules out an infinite strictly improving trajectory whose transitive, irreflexive dominance is invariant under report equality in both arguments and whose report image lies in that fixed finite carrier. It derives distinct reports from those hypotheses using `lemma1c_goodhart_metric_collapse_on_collision`, then applies the finite-list bound. The underlying state space can be infinite. Neither a particular self-modification mechanism nor statistical independence, primitive difference or a sheaf premise occurs in this theorem's signature.

N reports allow at most N−1 report-grounded strict transitions. An arbitrary sequence of N+1 observations repeats by transition index N; this says nothing about the magnitude of a jump or elapsed time. Transcripts, verifier state, timestamps and rolling context must be included in the declared report interface whenever dominance uses them.

Structural `RelationallyAligned` transformations and the numeric-rank `RelationalAlignment` predicate are different definitions, not equivalent encodings. The latter explicitly uses an internal score below N. Relabeling scores can change that policy. The compiled `ReviewCountermodels` exhibit a structurally aligned successor and an infinite increasing trajectory with one constant report; the dominance is not report-grounded. This is a scope control consistent with the finite-report theorem.''')
s=s.replace('A finite alphabet does not bound', '''`PrefixBounds.spending_prefix_invariant` bounds cumulative natural-valued charges plus remaining budget by initial budget, assuming the budget inequality only at indices below a declared finite horizon L. `refinement_prefix_bound` and `lift_prefix_bound` give the corresponding finite-prefix bounds. `interleaved_lift_event_bound` counts actual charged lift events and permits uncharged intervening ticks. The older total strictly decreasing sequences are impossible infinite-descent hypotheses, not certificates of existing finite executions. The retained asynchronous and rewiring corollaries are cardinality statements on fixed report products; they do not formalize buffers, evolving incidence or terminal-reason distributions.

A finite alphabet does not bound''')
s=s.replace('Persistence across process restarts, injection into a live agent request, and measurement of actual model use are not established by this edition.',
    'This abstract theorem alone does not establish persistence, agent-request injection or actual model use; section 8 supplies separate finite evidence for those implementation questions.')
s=s.replace('The original transition-graph and Rust/Python receipt checks remain finite implementation evidence for their declared policy.',
'''The transition CLI imports the tested modular implementation. The Rust companion checks EIS metadata, role-label separation, digests and reported horizon arithmetic; it neither replays obstruction predicates nor authenticates host identities. Distinct labels alone do not establish statistical independence or evidential soundness. The ASCII identifier contract is checked in both languages. The asynchronous fixtures deliberately inject residuals from lag/skew/rewiring flags, including a positive age penalty when report contents agree. Their distribution shift is a property of that synthetic policy, not a derived transport law.

The cochain repair kernel minimizes an L1 residual over unrestricted potentials. Every successful certificate must reconstruct the repaired cochain from its potential, reproduce the residual/cost, annihilate the transposed incidence with a dual vector of infinity norm at most one, and close the exact rational duality gap. Closedness alone is insufficient: the review's closed annulus has optimal repair cost 9. HiGHS supplies a numerical candidate; the exact checker can refuse it. Active repair replays the certificate and admits only an exact integer price, strictly positive for a nonzero repair, even with Python assertions disabled.

This cochain LP is separate from the companion's probability-marginal LP, which requires nonnegative normalized global distributions. There is no declared reduction and no general identification of contextual fraction with half the unweighted concatenated-context L1 distance. Two disjoint PR scenarios give contextual fraction 1 but distance 4. A support-gluing test ranges over families of supported local sections; restrictions of a single preselected global assignment already agree. Strong contextuality implies logical contextuality, which implies probabilistic contextuality. The review response links the original contextual-fraction definition.''')
s=s.replace('Source hashes, current census results and verification details are supplied under `lean4/` and `docs/live_memory_verification.json`.',
    'Source hashes and current censuses are supplied under `lean4/`; the review corrections are detailed in `docs/review_response_2026_10_23.md`. The live-memory and numerical verification files retain their earlier experiment dates and scopes.')
s=s.replace('The repaired quantum library passes all 712 tests', 'The preceding numerical verification recorded all 712 quantum-library tests passing')
s=s.replace('These are scoped current-source checks.', 'These are scoped checks of the earlier recorded source snapshot, not fresh native reruns in this edition.')
s=s.replace('Their exact scalar witnesses check supplied-bound arithmetic. The continuous statements are written proofs with declared premises, not new Lean results or automatic error certificates for recalled memories.',
    'The preceding numerical-release report records their exact scalar witnesses and then-written continuous bounds. Later projection-paper mechanization is a separate release; these transferred observations do not supply automatic error certificates for recalled memories.')
p.write_text(s,encoding='utf-8',newline='\n')
p=root/'relational_reasoning_and_rsi_impossibility_claim_ledger.md'
s=p.read_text(encoding='utf-8').replace('version 1.1.0','version 1.2.3')
s+='''

## Version 1.2.3 review corrections

| Claim | Evidence | Scope |
|---|---|---|
| Finite-prefix charge conservation | `PrefixBounds.spending_prefix_invariant`, `unit_spending` | Natural-valued costs and budgets; inequality assumed only below L. |
| Finite refinement/lift bound | `refinement_prefix_bound`, `lift_prefix_bound` | Every counted step consumes at least one unit. |
| Interleaved lift-event bound | `interleaved_lift_event_bound` | Counts events, not elapsed uncharged ticks. |
| Structural alignment scope control | Four `ReviewCountermodels` theorems | Infinite trajectory lacks report-grounded dominance; total natural descent is impossible. |
| Exact cochain optimality | `verify_exact_l1_repair`, review regression tests | Rational certificate replay after numerical candidate search; no universal solver-completeness or Lean/Python refinement claim. |
| Repair admission | Active-repair gate and optimized-Python regression | Certificate replay and exact positive price for nonzero repair. |
| Native metadata parity | `cross_check_eis_metadata_against_rust`, native regression | ASCII role policy, digest, reported capacity arithmetic only; no obstruction replay or identity authentication. |

The [review response](docs/review_response_2026_10_23.md) maps all fourteen findings
to current definitions, code, negative controls or withdrawn historical claims.
The separate named and full censuses enumerate the actual proof estate.
'''
p.write_text(s,encoding='utf-8',newline='\n')
p=root/'relational_reasoning_and_rsi_impossibility_change_log.md'
p.write_text(p.read_text(encoding='utf-8')+'''

## Version 1.2.3 (2026-10-23)

Reconciled all fourteen findings of the independent pinned-source review against
the integrated manuscript. Replayed its eight negative controls before editing.
Removed the false closedness certificate, added an independent exact checker,
made repair admission survive optimized Python, unified CLI and module code,
declared scientific dependencies and packaged native/JSON resources. Introduced
the shared ASCII identifier contract and explicit metadata-only native results.
Added five finite-prefix Lean results and four compiled reviewer scope controls
to both censuses. Clarified rank alignment, report counting, synthetic defect
injection and separation of cochain/probability/contextual-fraction LPs. Rebuilt
the paper and standalone package, preserving previous evidence outside the
active deposit. Earlier native and live-provider trials were not rerun.
''',encoding='utf-8',newline='\n')
p=root/'lean4/RelationalRsiNoGo.lean'
s=p.read_text(encoding='utf-8')
s=s.replace('   Under the declared axioms of a background-free, finite relational system with\n   intersubjective fact verification, an unbounded strictly improving RSI trajectory\n   `(M_k)_{k ∈ ℕ}` with `M_{k+1} = Φ(M_k)` and `M_{k+1} ≻ M_k` does not exist.',
    '   A fixed finite report image excludes an infinite strict trajectory when\n   dominance is invariant under report equality. The state type can be infinite.\n   The theorem does not require the other interpretive structures in this file.')
s=s.replace('/-- Lemma 2b (Epistemic Horizon Pair Budget,', '/-- Historical total-descent contradiction; for an existing finite prefix use\n    `PrefixBounds.refinement_prefix_bound`. Lemma 2b (Epistemic Horizon Pair Budget,')
s=s.replace('/-- Lemma 2c (Licensed Structural Lift Budget Bound,', '/-- Historical total-descent contradiction; for finite prefixes and interleaved\n    events use `PrefixBounds`. Lemma 2c (Licensed Structural Lift Budget Bound,')
s=s.replace('/-- A background-free, finite relational universe with intersubjective verification:',
    '/-- A finite report interface; no authentication or finiteness of State is encoded:')
s=s.replace('finite intersubjective relational report type','report type with decidable equality')
s=s.replace('community-validated / boundary-factorized relational report','declared report map')
p.write_text(s,encoding='utf-8',newline='\n')
print('Updated manuscript, claim map and active version to 1.2.3')
