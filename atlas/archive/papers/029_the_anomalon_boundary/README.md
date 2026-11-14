# The Anomalon Boundary: Primitive Difference, Structure, and the Authority Boundary of Meaning

Prepared republication edition 2.1.1 · 2026-10-23. No new public deposit or DOI is asserted.

PDF regeneration: `py -3.12 scripts/build_pdf.py`. This uses the canonical math-spine renderer and requires Pandoc, XeLaTeX, PyMuPDF, and the Times New Roman, Cascadia Mono, Cambria Math and Latin Modern Math fonts. The shipped PDF is already rendered. The standalone proofs remain pinned to Lean 4.35.0.

**Surviving Primitive Differences, Minimal Knowability Closures, and Restart Boundaries**

Author: Jeremy H. Carroll  
Series: `001_finite_obstruction_calculus`  
Paper Key: `001_finite_obstruction_calculus/029_the_anomalon_boundary`  
Version: 2.1.1 (2026-10-23)  
License: Creative Commons Attribution 4.0 International (CC-BY-4.0) / Apache-2.0 (Code)  

---

## Nonclaims and Scope

This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing. All computational claims are demonstrated over finite discrete complexes with exact rational arithmetic. No claim of metaphysical cosmology, total repair, or continuum physics is asserted.

---

## Overview

This research package formalizes the root authority boundary of finite obstruction systems:
1. **Root Authority Boundary**: Every authoritative claim must descend to Primitive Difference, Structure, or a typed refusal: $\text{Real}_0 = \text{Primitive Difference} \cup \text{Structure}$.
2. **Surviving Primitive Difference**: Cohomological trichotomy classifying 1-cochain discrepancies $h$ over an explicit finite boundary complex with verified $d^1 d^0 = 0$:
   - Exact ($h \in \text{im}(d^0)$): Vanishes as gauge ($[h] = 0$ in $H^1$).
   - Unclosed ($d^1 h \neq 0$): Active closure failure ($\Gamma_2 > 0$).
   - Closed non-exact ($d^1 h = 0$ and $h \notin \text{im}(d^0)$): Survives local-to-global descent as stable structure ($[h] \neq 0$ in $H^1$, $\Gamma_2 = 0$).
3. **The Anomalon Boundary**: Defined strictly as a recursion and restart boundary produced when a finite system exhausts admitted repairs with strictly positive residual obstruction. Permits only three lawful continuations: typed refusal, lift request, or restart seed.
4. **Anomalon Non-Promotion & Active Restart Firewall**: An Anomalon seed provides restart permission; it does not grant authority. A lift request is distinguished from an authorized lift, which requires an explicit `LiftPreservationWitness` with strictly positive preservation metric $\Delta_\Lambda > 0$.
5. **Minimal Knowable System (MKS)**: Proposed ten-role interface specification (carrier, state, gauge, coboundary, comparison, quotient residual, closure defect, observer norm, terminal rule, continuation rule) required for any system to be terminalizable under this calculus.

---

## Directory Structure

```text
.
├── README.md                                          # Package overview
├── LICENSE                                            # Creative Commons Attribution 4.0
├── LICENSE-CODE                                       # Apache 2.0 / MIT
├── MANIFEST.sha256                                    # Release checksum manifest
├── SHA256SUMS                                         # Full tree cryptographic checksums
├── pyproject.toml                                     # Python configuration
├── zenodo_metadata.json                               # Zenodo deposit metadata
├── verify_deposit.py                                  # Deterministic verification runner
├── the_anomalon_boundary_monograph.md                 # Canonical monograph
├── the_anomalon_boundary_change_log.md                # Revision history
├── the_anomalon_boundary_claim_ledger.md              # Claim registry
├── code/
│   ├── deposit_paths.py                               # Safe path traversal
│   ├── mod_anomalon_boundary_core.py                  # Core exact rational model and evaluator
│   └── tests/
│       └── test_anomalon_boundary.py                  # Pytest test suite (8 unit tests)
├── lean4/
│   ├── Census.lean                                    # Axiom dependency census
│   ├── lakefile.lean                                  # Lake package configuration
│   ├── lean-toolchain                                 # Lean 4 toolchain specification
│   ├── OntologyBasic.lean                             # Authority-boundary policy
│   └── FiniteBoundary.lean                            # Finite trichotomy, cycle, and firewall proofs
├── docs/
│   ├── descriptions.md                                # Single-Version Unicode Word documentation
│   └── references.md                                  # Bibliography & citation register
├── scripts/
│   └── regen_sha256sums.py                            # Checksum generator
└── tools/
    └── rebuild_release.py                             # Deterministic zip builder
```

---

## Verification

To verify this package locally:

```bash
# 1. Run unit test suite
py -3.12 -m pytest code/tests/test_anomalon_boundary.py

# 2. Run deposit verifier (including Lean 4 axiom audit and unit tests)
py -3.12 verify_deposit.py --lean --test code/tests/test_anomalon_boundary.py
```
