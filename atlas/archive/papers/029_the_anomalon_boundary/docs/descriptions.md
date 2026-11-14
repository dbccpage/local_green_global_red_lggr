# Scientific Description: The Anomalon Boundary

This deposit contains the complete research package for The Anomalon Boundary: Primitive Difference, Structure, and the Authority Boundary of Meaning, authored by Jeremy H. Carroll.

Series: 001_finite_obstruction_calculus  
Paper ID: 001_finite_obstruction_calculus/029_the_anomalon_boundary  
Version: 2.1.1 (2026-10-23)  

---

## 1. Context and Problem Statement

Theoretical modeling and representation systems often permit inherited structures (spacetime metrics, Hilbert spaces, continuum coordinates, probability measures) to speak as primitive or fundamental truths without witnessed descent. This monograph establishes the root authority boundary: every authoritative claim must descend to Primitive Difference, Structure, or a typed refusal. Rather than proposing a metaphysical origin, the paper establishes the Anomalon as a recursion and restart boundary produced when a finite verification system exhausts its admitted repairs while retaining typed obstruction.

---

## 2. Core Mathematical Contributions

1. Root Authority Boundary: Formulation of Real_0 = Primitive Difference union Structure, asserting that claims acquire operational authority only after witnessed descent.
2. Surviving Primitive Difference Trichotomy: Cohomological classification of 1-cochain discrepancies into exact gauge artifacts (VanishesAsGauge, [h] = 0 in H^1), unclosed active closure defects (ActiveIncoherence, Gamma_2 > 0), and closed non-exact survivors (SurvivingPrimitiveDifference, [h] != 0 in H^1, Gamma_2 = 0).
3. The Anomalon Boundary Specification: Characterization of the Anomalon as an unresolvable terminal residual permitting strictly three continuations: typed refusal, licensed lift request, or next-iteration restart seed.
4. Anomalon Non-Promotion and Active Restart Firewall: Firewall establishing that an Anomalon seed grants recursion permission, not operational authority. A lift request is distinguished from an authorized lift, which requires a validated LiftPreservationWitness with strictly positive preservation metric Delta_Lambda > 0.
5. Minimal Knowable System (MKS): Proposed interface specification of the ten-role complete package (carrier, state, gauge, coboundary, comparison, quotient residual, closure defect, observer norm, terminal rule, continuation rule) required for any system to be terminalizable under this calculus.

---

## 3. Mathematical Framework

- Finite Obstruction Complex: Discrete cochains C^0 -> C^1 -> C^2 with coboundaries d^0, d^1 satisfying d^1 o d^0 = 0.
- First Cohomology Survivor: Non-trivial cohomology class [h] in H^1 = ker d^1 / im d^0 representing persistent obstruction.
- Law of Non-Vanishing Obstruction: Invariant requiring that obstruction cannot vanish without an explicit coboundary repair or quotient operation.

---

## 4. Computational Implementation and Conformance

The package includes an audited Python reference implementation under `code/mod_anomalon_boundary_core.py` and a unit test suite under `code/tests/`:
- Cochain Defect Classification: Exact rational evaluation of defect mass, exactness, and closure defect from explicit boundary matrices d^0, d^1 with verified d^1 o d^0 = 0 via exact Gaussian elimination.
- Fail-Closed Input Validation: Rejection of mathematically inconsistent defects (such as exact cochains with non-zero curvature or negative norms).
- Anomalon Boundary Engine: Handles continuation requests, enforces the active firewall, and requires LiftPreservationWitness before granting lift authorization.
- MKS Validator: Validates role completeness across all ten essential system dimensions under declared scope boundaries.

---

## 5. Evaluator Soundness and Non-Claims

This monograph assigns no authorization, changes no jurisdiction, and confers no institutional standing. It does not assert a metaphysical cosmology, physical spacetime, or exhaustive repair. The Anomalon boundary is a recursion barrier, not an empirical assertion about the origin of reality.

---

## 6. Scope Boundaries and Falsifiability

- Bounded Discrete Complexes: Formal models apply to discrete cochain complexes and finite verification architectures.
- Falsifiability: The framework is falsified if an authoritative claim can be exhibited that descends to neither Primitive Difference, Structure, nor a typed refusal, or if an Anomalon seed is demonstrated to grant operational certification without external descent.

---

## 7. Deposit Contents

- `the_anomalon_boundary_monograph.md`: Canonical monograph manuscript.
- `the_anomalon_boundary_claim_ledger.md`: Claim status register.
- `the_anomalon_boundary_change_log.md`: Package version log.
- `code/mod_anomalon_boundary_core.py`: Python reference implementation.
- `code/tests/test_anomalon_boundary.py`: Unit test suite (8 tests).
- `lean4/`: Self-contained Lean 4 formalization package (`OntologyBasic.lean`, `Census.lean`, `lakefile.lean`, `lean-toolchain`).
- `docs/descriptions.md`: Scientific description register.
- `docs/references.md`: Bibliography and citation register.
- `pyproject.toml`, `zenodo_metadata.json`, `LICENSE`, `LICENSE-CODE`: Metadata and packaging.
- `verify_deposit.py`, `scripts/regen_sha256sums.py`, `tools/rebuild_release.py`: Deterministic verification and release tooling.

---

## 8. Citation and Verification Notice

To verify the deposit:
```bash
py -3.12 -m pytest code/tests/test_anomalon_boundary.py
py -3.12 verify_deposit.py --lean --test code/tests/test_anomalon_boundary.py
```
