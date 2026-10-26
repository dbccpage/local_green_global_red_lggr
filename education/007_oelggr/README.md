---
documentation_contract: symbol-game-documentation/v1
title: "007_oelggr: Local Green, Global Red (OELGGR)"
kind: grammar-reference
audience:
  - researchers
  - engineers
  - coding-agents
status: active
maturity: production
atlas_status: specified
syntax_status: verified
checker_status: verified
mathematical_status: computed
successor_status: declared
lift_status: unlicensed
source_provenance: coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series
authority_effect: "None"
source_paths:
  - omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series
  - omega_engine_education/documentation/007_oelggr/README.md
source_revision: 44aff3782
prerequisites: []
verification: py -3.12 -m unittest omega_engine_education.tests.test_curriculum_estate
aliases:
  - oelggr
  - LGGR
  - EPK
  - 100_local_green_global_red
related:
  - omega_engine_education/documentation/006_oewdp
  - omega_engine_education/documentation/003_oemssn
  - omega_engine_education/documentation/002_oesn
last_verified: 2026-10-10
---

# 007_oelggr: Local Green, Global Red (OELGGR)

AuthorityEffect: None.

> "An interface can pass every local check and still fail its global check. This package studies that fact in finite mathematical, sheaf-theoretic, and computational models."

This documentation context specifies the complete **Local Green, Global Red (LGGR)** architecture: its mathematical foundation across the 6-volume foundational paper series (`coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/`), its implementation in the Omega Engine crate (`omega_local_green_global_red_lggr`), its Lean 4 interactive proof kernels, and its operational enforcement via runtime target checkers.

---

## A first calculation before the monograph

Start with the [finite LGGR lesson](curriculum/1000_local_green_global_red_foundations/concepts/lesson_1000_01_local_green_global_red_foundations.md)
for a worked local/global counterexample, a rational blind-spot witness and an
unseen task with separate feedback. The companion track states which assets are
text, gives the limited Boolean notebook's execution scope, and identifies which
recordings are still absent.
This is a source-bound follow-up; it does not re-certify every historical
implementation or mechanization claim in the reference map below.

## 1. Master Documentation Index

- [`local_green_global_red_foundational_series.md`](local_green_global_red_foundational_series.md): The comprehensive monograph detailing the six-volume foundational series, the evaluated path kernel algebra, the finite no-recovery theorem, and the Omega Engine crate architecture.
- [`levels/`](levels/): **Decomposed Stage Specifications & Verification Records (Levels 00 through 09)**:
  - [`level_00_evaluator_defect_foundations.md`](levels/level_00_evaluator_defect_foundations.md): Level 00 — The Signed Evaluator Defect Carrier $\Delta_E = E_g - E_1 E_2 \in \{-1, 0, 1\}$.
  - [`level_01_evaluated_path_kernels.md`](levels/level_01_evaluated_path_kernels.md): Level 01 — Evaluated Path Kernels (EPK) and Composite Trajectories (Paper I).
  - [`level_02_organizational_gluing_sheaf_obstructions.md`](levels/level_02_organizational_gluing_sheaf_obstructions.md): Level 02 — Organizational Evaluator Gluing and Sheaf Obstructions (Paper II).
  - [`level_03_epk_gtla_six_role_overlay.md`](levels/level_03_epk_gtla_six_role_overlay.md): Level 03 — The Six-Role Game-Theoretic Learning Architecture (EPK-GTLA) (Paper III).
  - [`level_04_completion_relative_obstructions.md`](levels/level_04_completion_relative_obstructions.md): Level 04 — Finite Presentations, Inverse Systems, and Completion-Relative Obstructions (Paper IV).
  - [`level_05_finite_no_recovery_theorem.md`](levels/level_05_finite_no_recovery_theorem.md): Level 05 — The Finite No-Recovery Theorem and Blind-Spot Geometry (Paper V).
  - [`level_06_nonlinear_aggregation_adjoint_probing.md`](levels/level_06_nonlinear_aggregation_adjoint_probing.md): Level 06 — Nonlinear Aggregation and Adjoint Probing ($Q^T Q$) (Paper VI).
  - [`level_07_omega_engine_crate_architecture.md`](levels/level_07_omega_engine_crate_architecture.md): Level 07 — The `omega_local_green_global_red_lggr` Crate Architecture.
  - [`level_08_lean4_mechanization_and_target_checkers.md`](levels/level_08_lean4_mechanization_and_target_checkers.md): Level 08 — Formal Lean 4 Kernel Proofs and Runtime Target Checkers (`stage_021.py`).
  - [`level_09_runtime_guardrails_and_protocol_synthesis.md`](levels/level_09_runtime_guardrails_and_protocol_synthesis.md): Level 09 — The Seven Runtime Guardrails Against Evaluator Blind Spots.

---

## 2. The Core Phenomenon: The Evaluator Defect

In modular software, distributed multi-agent systems, and multi-simplex geometric complexes, a system is partitioned into components with local evaluators $E_1, E_2, \dots, E_k$. Each local evaluator checks an isolated boundary or projection, returning a Boolean verdict $E_i \in \{0, 1\}$. A global evaluator $E_g \in \{0, 1\}$ checks end-to-end composite correctness.

The **evaluator defect** is defined as:

$$\Delta_E = E_g - \prod_{i=1}^k E_i \in \{-1, 0, 1\}$$

| Defect $\Delta_E$ | Meaning | System State |
| :---: | :--- | :--- |
| **$0$** | **Evaluator Agreement**: Global verdict matches product of local verdicts. | Normal ($1-1=0$ or $0-0=0$) |
| **$+1$** | **Local Red, Global Green**: A local check failed, but global check passed. | Benign or over-constrained local fence |
| **$-1$** | **Local Green, Global Red**: Every local check passed, yet the global check failed! | **Critical Failure Mode** (`REFUSED_LOCAL_GREEN_GLOBAL_RED`) |

The state $\Delta_E = -1$ is the canonical **Local-Green / Global-Red witness**: each local subsystem reports success, creating a false impression of health, while the composed composite fails.

---

## 3. Mapping to the Six Foundational Papers

The foundational paper series lives under [`omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/`](../../../omega_engine_atlas/coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series):

| Volume | Title | Core Focus | Lean 4 Mechanization |
| :--- | :--- | :--- | :--- |
| **LGGR I** | *Evaluated Path Kernels for Composed Agent Reliability* | Non-commutative path composition, path kernels over transitions | `epk_composition.lean` |
| **LGGR II** | *Organizational Evaluator Gluing* | Sheaf obstructions on overlapping sub-domains, quotient obstructions | `gluing_obstruction.lean` |
| **LGGR III** | *EPK-GTLA Overlay Across Six System Roles* | Six-role game-theoretic architecture (Planner, Proposer, Governor, Worker, Arbiter, Auditor) | `gtla_roles.lean` |
| **LGGR IV** | *Finite Presentations & Completion-Relative Obstruction* | 2-adic inverse systems, thread existence (Stacks 086J), non-realization in $\mathbb{Z}$, Mittag-Leffler (Stacks 07KV) | `derived_limits.lean` |
| **LGGR V** | *Local Green, Global Red: Finite No-Recovery Theorem* | Blind-spot geometry, unrecoverable defect at distance 2, per-interface kernel triviality | `no_recovery_theorem.lean` |
| **LGGR VI** | *Nonlinear Aggregation & Adjoint Probing* | Observation map $Q$, Gram operator $Q^T Q$, adjoint detection of $\ker(Q)$ | `adjoint_probing.lean` |

---

## 4. Mapping to Omega Engine Crates

In our repository and monorepo design, the implementation resides in:
[`omega_engine/crates_rs/omega_local_green_global_red_lggr/`](../../../omega_engine/crates_rs/omega_local_green_global_red_lggr/)

Key components include:
- `core.py`: Abstract evaluated path kernel data structures.
- `defects.py`: Exact rational and Boolean defect calculations ($\Delta_E$).
- `composition.py`: Associative path composition and kernel tensor products.
- `epk_overlay.py`: Six-role GTLA overlay interfaces.
- `evaluation_harness.py`: Automated multi-agent harness verifying end-to-end composites.
- `ledger.py`: Append-only cryptographic trace of local vs global verdicts.
- `omega_engine_pfp/domain/ast_cochain/models.py`: Declares `LggrVerdict.REFUSED_LOCAL_GREEN_GLOBAL_RED` and binds to AST coboundary leakage ($\Phi_1 > 0$) and cycle obstructions ($\Gamma_2 > 0$).

---

## 5. Claim Hygiene Summary

1. **What this documentation supports:**
   - Formal mathematical modeling of composed evaluator defects $\Delta_E \in \{-1, 0, 1\}$ over finite Boolean and exact rational lattices.
   - Exact mapping between the 6-volume foundational paper series, Lean 4 proofs, and the `omega_local_green_global_red_lggr` crate.
   - Demonstration in finite toy settings that passing all local checks does not imply passing global checks.

2. **What this documentation does not support:**
   - It does not support an empirical claim that all real-world AI agent swarms suffer from a fixed percentage failure rate.
   - It does not assert that finite-stage solvability extends to continuous infinities without checking topological completion conditions.

3. **Narrowest defensible claim:**
   - In any discrete system where the global evaluator depends on joint state coordinates not captured by the product of local projections, there exist configurations where all local evaluators return $1$ while the global evaluator returns $0$, producing the typed defect $\Delta_E = -1$.

4. **Next test needed:**
   - Run cross-crate integration tests between `omega_local_green_global_red_lggr` and `omega_engine_pfp/domain/ast_cochain/`.


## Curriculum Tracks & Interactive Laboratories

- [**Curriculum Master Index**](curriculum/README.md): Interactive laboratory notebooks, concept lessons, narration scripts, and media assets.
