# The Authority Firewall: A Machine-Checked Separation of Evidence from Authority in Finite Systems

Prepared republication edition 2.1.1 · 2026-10-23. No new public deposit or DOI is asserted.

PDF regeneration: `py -3.12 scripts/build_pdf.py`. This uses the canonical math-spine renderer and requires Pandoc, XeLaTeX, PyMuPDF, and the Times New Roman, Cascadia Mono, Cambria Math and Latin Modern Math fonts. The shipped PDF is already rendered. The standalone proofs remain pinned to Lean 4.35.0.

**Live status:** The F004 floor status for family 001 is Open. "Machine-checked" in this title is not that floor status.

**Pointwise Coproduct Separation, Zero-Guard Summand Disjointness, and Fail-Closed Verification Gates**

Author: Jeremy H. Carroll  
Series: `001_finite_obstruction_calculus`  
Paper Key: `001_finite_obstruction_calculus/027_the_authority_firewall_a_machine_checked_separation_of_evidence_from_authority_in_finite_systems`  
Version: 2.1.1 (2026-10-23)  
License: Creative Commons Attribution 4.0 International (CC-BY-4.0) / PolyForm Noncommercial 1.0.0 (Code)  

---

## Nonclaims and Scope

This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing. All computational claims are demonstrated over finite discrete complexes with exact rational arithmetic. No claim of continuum dynamics or empirical realism is asserted.

---

## Overview

This research package formalizes the Authority Firewall:
1. **Coproduct Summand Separation**: The terminal type decomposes into a disjoint binary coproduct $\mathbb{T} = \mathbb{T}_{\mathsf{auth}} \oplus (\mathbb{T}_{\mathrm{res}} + \mathbb{F}_{\mathrm{res}})$. Residual evidence occupies the right injection (`Sum.inr`), while authority certificates occupy the left injection (`Sum.inl`).
2. **Pointwise Separation Theorem**: Lean 4 machine-checked verification that no residual outcome can inhabit the authority terminal summand: $\neg\,\mathsf{IsAuth}(\mathrm{residualTerminal}(r))$.
3. **Constructor Disjointness**: Relies solely on type-theoretic constructor disjointness (`Sum.noConfusion`) without extra axioms.
4. **Seven-Guard Authority Predicate**: Operational requirements (verified replay hash, matching replay, terminalizer present, exhaustive search $\kappa = 0$, zero defect $\delta = 0$, descent witness, replay freshness) necessary for operational certification.
5. **Audited Solver Case Study**: Demonstration on an adversarial solver audit showing how incomplete search and non-independent evaluation fail authority promotion and are structurally confined to diagnostic residuals.

---

## Directory Structure

```text
.
├── README.md                                          # Package overview
├── LICENSE                                            # Creative Commons Attribution 4.0
├── LICENSE-CODE                                       # PolyForm Noncommercial 1.0.0
├── MANIFEST.sha256                                    # Release checksum manifest
├── SHA256SUMS                                         # Full tree cryptographic checksums
├── pyproject.toml                                     # Python configuration
├── zenodo_metadata.json                               # Zenodo deposit metadata
├── verify_deposit.py                                  # Deterministic verification runner
├── authority_firewall_monograph.md                    # Canonical monograph
├── the_authority_firewall_a_machine_checked_separation_of_evidence_from_authority_in_finite_systems_change_log.md # Revision history
├── authority_firewall_claim_ledger.md                 # Claim registry
├── code/
│   ├── deposit_paths.py                               # Safe path traversal
│   ├── mod_authority_firewall_core.py                 # Core exact rational model and evaluator
│   └── tests/
│       └── test_authority_firewall.py                 # Pytest test suite (10 unit tests)
├── docs/
│   ├── descriptions.md                                # Single-Version Unicode Word documentation
│   └── references.md                                  # Bibliography & citation register
├── lean4/
│   └── ResidualNonCreation.lean                       # Self-contained bundled Lean 4 verification
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
py -3.12 -m pytest code/tests/test_authority_firewall.py

# 2. Run deposit verifier
py -3.12 verify_deposit.py --test code/tests/test_authority_firewall.py --lean

# 3. Verify bundled Lean 4 proof (if lean is installed)
lean lean4/ResidualNonCreation.lean
```
