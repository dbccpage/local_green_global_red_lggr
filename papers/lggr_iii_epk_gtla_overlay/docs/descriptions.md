# Zenodo descriptions

## Primary description

```html
<p><strong>Abstract.</strong> Local checks can pass while their composition fails. For binary local verdicts e<sub>1</sub>, e<sub>2</sub> and a binary composite verdict e<sub>g</sub>, this package studies the signed evaluator defect Δ<sub>E</sub> = e<sub>g</sub> − e<sub>1</sub>e<sub>2</sub>. The paper derives that the defect lies in {−1, 0, 1}, an exact finite-sample sum identity, a binary-triple cancellation counterexample, and a quotient-descent obstruction.</p>
<p><strong>Why it matters.</strong> The same small diagnostic can be attached to six system roles while keeping carrier, transport, and observation assumptions explicit. This exposes an integration mismatch without turning a local pass into a claim about an entire system.</p>
<p><strong>Contents.</strong> The archive includes matching Markdown, TeX, and PDF; a finite Python implementation; twelve paired break-detect-recover mutation tests; seven teaching and verification notebooks with generated plots and optional widgets; two publication figures; a Lean 4 library with a current theorem-level axiom report; typed claim maps; metadata; and deterministic checksum and archive scripts.</p>
<p><strong>Reproduction.</strong> Install the locked development environment, run <code>python verify_deposit.py --lean</code>, and build the dated archive with <code>python scripts/build_deposit_zip.py</code>.</p>
<p><strong>Scope.</strong> The checked results are finite identities and finite-data guards. A zero observed defect is not a general reliability guarantee, and the real exponential-kernel theorem remains conditional and is not fully mechanized in Lean.</p>
```

## Secondary description

```text
Local checks can pass while their composition fails. For binary local verdicts e1, e2 and a binary composite verdict eg, this package studies the signed evaluator defect Delta_E = eg - e1e2. It derives that the defect lies in {-1, 0, 1}, an exact finite-sample sum identity, a binary-triple cancellation counterexample, and a quotient-descent obstruction.

The archive includes matching Markdown, TeX, and PDF; a finite Python implementation; twelve paired mutation tests; seven teaching and verification notebooks with generated plots and optional widgets; two publication figures; and a Lean 4 library with a current theorem-level axiom report.

The checked results are finite identities and finite-data guards. A zero observed defect is not a general reliability guarantee, and the real exponential-kernel theorem remains conditional and is not fully mechanized in Lean.
```

The Primary block is the canonical Zenodo description. The `description`
field in `zenodo_metadata.json` must match its contents byte-for-byte.
