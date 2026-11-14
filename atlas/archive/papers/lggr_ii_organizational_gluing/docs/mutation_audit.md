# Mutation audit

**Package:** *Local Green, Global Red II: Organizational Evaluator Gluing*

**Version:** 1.3.1

**Date:** 2026-10-15

The executable tests include deliberate break-and-recover checks. Each row names
an admissible input mutation, the failure it must expose, and the recovery
witness checked by the suite.

| Fault injection | Required response | Recovery or control witness |
|---|---|---|
| Local validator returns `0`, `1`, `0.0`, `1.0`, text, or `None` | reject every non-exact-`bool` verdict | return `False` or `True` explicitly |
| Global evaluator returns an integer, float, text, or `None` | reject every non-exact-`bool` verdict | return `False` or `True` explicitly |
| Owner prerequisite is absent | refuse the declared closure | supply authority and accountability |
| Authority lacks accountability | refuse the declared closure | bind both owner properties |
| Accountability lacks authority | refuse the declared closure | bind both owner properties |
| Boundary name or token is empty | reject the malformed cut | supply nonempty fields |
| One validator copies the global evaluator while a peer fails | compare the complete local product with `E_G` and refuse a false collapse result | require product alignment on every sampled trace |
| Passing agreement lacks adequacy support | keep the result non-certifying | even declared adequacy remains diagnostic |
| Three defects are added to obtain -3 | flag departure from the defect range | use Shapley attribution for a declared value function |
| Weak representation is offered as factorization | exhibit the finite counterexample | require product sufficiency |
| Temporal coherence is false | make the prerequisite conjunction false | restore temporal coherence |
| A caller requests an elevated evidence level | cap or reject the request | retain the boundary-checked level |

These tests establish robustness of the finite implementation boundary only.
They do not turn the organizational interpretation into an empirical claim.

## Reference verification run

The release-candidate run completed with **49 passed in 12.81 s**. Production
line/statement coverage was **99.22%** (384/387), and production branch
coverage was **98.72%** (77/78). The terminal report rounded the two modules to
100% for `organizational_gluing_core.py` and 97% for `generate_figures.py`.
There were no skips or test warnings. The command was:

```powershell
uv run --isolated --frozen --project . --python <python-3.12> --extra dev `
  python -m pytest -n 8 code/tests --basetemp <external-temp> `
  -p no:debugging -p no:cacheprovider `
  --cov=organizational_gluing_core --cov=generate_figures --cov-branch `
  --cov-report=term-missing --cov-report=json:<external-temp>/coverage.json
```

The deposit verifier reads that JSON and applies separate 95 percent floors to
line/statement coverage and branch coverage.
