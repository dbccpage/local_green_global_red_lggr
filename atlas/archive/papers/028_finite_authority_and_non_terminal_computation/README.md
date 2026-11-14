# Finite Authority and Non-Terminal Computation

Prepared republication edition 2.0.3 · 2026-10-23. No new public deposit or DOI is asserted.

PDF regeneration: `py -3.12 scripts/build_pdf.py`. This uses the canonical math-spine renderer and requires Pandoc, XeLaTeX, PyMuPDF, and the Times New Roman, Cascadia Mono, Cambria Math and Latin Modern Math fonts. The shipped PDF is already rendered. The standalone proofs remain pinned to Lean 4.35.0.

**Proposal Systems, Evaluated Path Kernels, Local Green != Global Red Obstructions, and Structural Firewalls**

Author: Jeremy H. Carroll  
Series: `001_finite_obstruction_calculus`  
Paper Key: `001_finite_obstruction_calculus/028_finite_authority_and_non_terminal_computation`  
Version: 2.0.3 (2026-10-23)  
License: Creative Commons Attribution 4.0 International (CC-BY-4.0) / Apache-2.0 (Code)  
DOI: not assigned for this prepared edition.

---

## Nonclaims and Scope

This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing. All computational claims are demonstrated over finite discrete complexes with exact rational arithmetic. No claim of continuum dynamics or empirical realism is asserted.

---

## Overview

This research package formalizes the boundary between non-terminal computation (traces, proposals, token sequences, and halting states) and terminalized operational authority:
1. **Proposal Systems vs Authority**: Generative models, search engines, and Turing machines generate traces with probability $P_\theta(\gamma \mid x) > 0$. High proposal mass is not authority.
2. **Evaluated Path Kernel (EPK)**: Traces are integrated into an accepted mass $Z_\theta^{\lambda, \mu}(y \mid x)$ under declared evaluators, with exact rational costs and residual penalties.
3. **C1–C8 Gate Stack**: Operational authority requires the conjunction of eight gates (schema validity, evaluator projection, verifier sovereignty, trust root audit, exhaustive bounds, replay determinism, boundary sufficiency, and terminalization). Any failure yields a typed refusal.
4. **Halting is not Authority**: Formal program termination represents syntactic halting; operational authority requires an independent, replayable evidence terminal.
5. **Local Green != Global Red (LGGR)**: A local dashboard can factor through zero-difference equivalence classes while the joint local/global dashboard provably fails to factor due to global cycle obstructions.
6. **Counterfeit Descent Detection**: Structural defenses against systems that imitate authority surface signs (citations, JSON tags, confidence markers) without valid descent witnesses.

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
├── finite_authority_and_non_terminal_computation_monograph.md # Canonical monograph
├── finite_authority_and_non_terminal_computation_change_log.md # Revision history
├── finite_authority_and_non_terminal_computation_claim_ledger.md # Claim registry
├── code/
│   ├── deposit_paths.py                               # Safe path traversal
│   ├── mod_finite_authority_core.py                   # Core exact rational model and evaluator
│   └── tests/
│       └── test_finite_authority.py                   # Pytest suite
├── lean4/
│   ├── FiniteAuthority.lean                           # Finite LGGR, halt, counterfeit, and class-increase proofs
│   ├── Census.lean                                    # Axiom census
│   ├── lakefile.lean
│   ├── lake-manifest.json
│   └── lean-toolchain                                 # leanprover/lean4:v4.33.1
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
py -3.12 -m pytest code/tests/test_finite_authority.py

# 2. Run deposit verifier
py -3.12 verify_deposit.py --test code/tests/test_finite_authority.py --lean
```
