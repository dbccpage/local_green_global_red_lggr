# The Authority Firewall and Verification Limits: Structural Verification, Detector Adequacy, and Capability Non-Constructibility

**Detector Calibration Suites, Capability Fences, Six-Axis Evidence Lattices, and Halting Contrasts**

Author: Jeremy H. Carroll  
Series: `001_finite_obstruction_calculus`  
Paper Key: `001_finite_obstruction_calculus/030_authority_firewall_and_verification_limits`  
Version: 2.2.0 (2026-10-08)  
License: Creative Commons Attribution 4.0 International (CC-BY-4.0) / MIT (Code)  
Concept DOI: [10.5281/zenodo.pending](https://zenodo.org/records/pending) *(Provisional pre-deposit identifier)*

---

## Nonclaims and Scope

This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing. All computational claims are demonstrated over finite discrete complexes with exact rational arithmetic (`fractions.Fraction`). No claim of continuum dynamics, unbounded prompt coverage, or empirical realism is asserted.

---

## Overview

This research package formalizes the structural boundaries and verification limits of autonomous reasoning systems:
1. **Detector Calibration vs. Adequacy**: $D(x) = \text{pass} \neq \text{Adequate}(D, \mathcal{C}, P) \neq \text{operational authority}$. A collapsing detector produces false-green verifications. The 4-case suite (positive, negative, collision, metamorphic) forms a necessary *minimum calibration record* to falsify constant/collapsing detectors. True adequacy over an arbitrary claim class requires finite domain exhaustion, an explicit coverage theorem, or a strictly bounded claim domain. Incomplete calibration fail-closes to `DetectorInadequate`.
2. **Finite Calibration Completeness Theorem & Sharp Coverage Bound**: Under declared class-constancy of ground-truth specification $A$ and detector $D$ on equivalence partition $X / \sim$, global agreement $D = A$ holds if and only if $D(r) = A(r)$ for all representatives $r \in R$. The bound is sharp: omitting any partition class admits a class-constant counterexample detector that passes all tested representatives while failing on the omitted class.
3. **Capability Non-Constructibility under Object-Capability Security**: Enforces protected interface separation: within an unprivileged execution context, an untrusted runtime result cannot construct or forge an `AuthorityCapability`. Direct instantiation attempts raise `CapabilityViolationError`.
4. **Cryptographically Bound Descent Witnessing & Defense Against Mocks**: Authority certification requires an authentic, cryptographically bound descent witness issued by an authorized sovereign descent verifier. Sealed constructor tokens prevent unauthorized instantiation. Direct mock injections (such as `object()`), empty witnesses, or tampered payloads fail-closed to `RefusalDefect`.
5. **Six-Axis Evidence Lattice**: Independent axes (Mathematical, Mechanization, Implementation, Empirical, Security, Authority) with strict prohibition on cross-axis greening.
6. **Halting vs Structural Authority**: Fluent task completion or syntactic halting does not confer authority without an independent, adequate structural descent verifier.
7. **Bundled Master Demo Runner**: Pinned, self-contained reference execution across 7 distinct operational scenarios (C1, O1–O7) verifying deterministic routing and failure-closed terminal states.

---

## Directory Structure

```text
.
├── README.md                                          # Package overview
├── LICENSE                                            # Creative Commons Attribution 4.0
├── LICENSE-CODE                                       # MIT License
├── MANIFEST.sha256                                    # Release checksum manifest
├── SHA256SUMS                                         # Full tree cryptographic checksums
├── pyproject.toml                                     # Python configuration
├── zenodo_metadata.json                               # Zenodo deposit metadata
├── verify_deposit.py                                  # Deterministic verification runner
├── authority_firewall_and_verification_limits_monograph.md # Canonical monograph
├── authority_firewall_and_verification_limits_change_log.md # Revision history
├── authority_firewall_and_verification_limits_claim_ledger.md # Claim registry
├── code/
│   ├── deposit_paths.py                               # Safe path traversal
│   ├── mod_verification_limits_core.py               # Core exact rational model and evaluator
│   └── tests/
│       └── test_verification_limits.py               # Pytest test suite (11 unit tests)
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
# 1. Run unit test suite (11 tests)
py -3.12 -m pytest code/tests/test_verification_limits.py

# 2. Run deposit verifier
py -3.12 verify_deposit.py --test
```
