# Deposit descriptions

## Primary Description

This HTML block is the sole canonical source for
`zenodo_metadata.json.description`.

```html
<p><strong>Abstract.</strong> A finite evaluator is represented by a real observation matrix Q. If two states produce the same observation, every deterministic rule that sees only that observation gives them the same verdict. Thresholds, voting, ranking, and other nonlinear post-processing therefore preserve every direction in ker Q. The Gram response Q-transpose Qx vanishes exactly on ker Q. Its orthogonal-range description is classical real-matrix language and is outside the rational Lean formalization.</p>
<p><strong>Results.</strong> The paper establishes observation-only post-processing invariance, the rational Gram-kernel identity, a centered two-query directional identity, and exact recovery of the Gram response by averaging over the full finite sign cube. The Euclidean singular-value cylinder bound remains visible as classical background and is cited from classical matrix analysis.</p>
<p><strong>Artifacts.</strong> The deposit contains a self-contained Python implementation with branch-aware tests and a break-detect-restore mutation, Lean theorems for those rational identities with an axiom report, two executable teaching notebooks, and generated figures. Earlier live-model and distributed or topological prototypes are retained as research history but excluded from the evidentiary surface.</p>
<p><strong>Reproduction.</strong></p>
<pre><code>uv run --isolated --frozen --extra dev python verify_deposit.py --lean</code></pre>
<p><strong>Scope.</strong> The work establishes finite real-matrix statements and reports deterministic fixtures. It does not evaluate a language model, certify an operational system, establish stochastic-optimization convergence, or demonstrate the deferred distributed and geometric extensions.</p>
```

## Secondary Description

This plain-text block is the canonical secondary rendering for catalogues that
do not accept HTML.

```text
Abstract. A finite evaluator is represented by a real observation matrix Q. If two states produce the same observation, every deterministic rule that sees only that observation gives them the same verdict. Thresholds, voting, ranking, and other nonlinear post-processing therefore preserve every direction in ker Q. The Gram response Q-transpose Qx vanishes exactly on ker Q. Its orthogonal-range description is classical real-matrix language and is outside the rational Lean formalization.

Results. The paper establishes observation-only post-processing invariance, the rational Gram-kernel identity, a centered two-query directional identity, and exact recovery of the Gram response by averaging over the full finite sign cube. The Euclidean singular-value cylinder bound remains visible as classical background and is cited from classical matrix analysis.

Artifacts. The deposit contains a self-contained Python implementation with branch-aware tests and a break-detect-restore mutation, Lean theorems for those rational identities with an axiom report, two executable teaching notebooks, and generated figures. Earlier live-model and distributed or topological prototypes are retained as research history but excluded from the evidentiary surface.

Reproduction.

    uv run --isolated --frozen --extra dev python verify_deposit.py --lean

Scope. The work establishes finite real-matrix statements and reports deterministic fixtures. It does not evaluate a language model, certify an operational system, establish stochastic-optimization convergence, or demonstrate the deferred distributed and geometric extensions.
```
