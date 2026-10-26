---
documentation_contract: symbol-game-documentation/v1
title: "LGGR Levels Index: Levels 00 through 09"
kind: grammar-reference
status: active
maturity: production
atlas_status: specified
evidence_grades:
  named: true
  syntax: true
  computed: true
  Lean: true
  gated: true
source_provenance: coda_atlas/F004_papers/001_finite_obstruction_calculus/001_local_green_global_red_foundational_series
authority_effect: "None"
---

# Local Green, Global Red Levels Index (Levels 00 through 09)

AuthorityEffect: None.

This directory contains the decomposed stage specifications and verification records for the **Local Green, Global Red (LGGR)** foundational series:

| Level | Document | Core Focus | Paper / Crate Anchor |
| :---: | :--- | :--- | :--- |
| **00** | [`level_00_evaluator_defect_foundations.md`](level_00_evaluator_defect_foundations.md) | Signed defect carrier $\Delta_E = E_g - E_1 E_2 \in \{-1, 0, 1\}$ | Truth table, `defects.py` |
| **01** | [`level_01_evaluated_path_kernels.md`](level_01_evaluated_path_kernels.md) | Evaluated path kernels, trajectories, non-commutative composition | Paper I (`lggr_i`), `epk_core.py` |
| **02** | [`level_02_organizational_gluing_sheaf_obstructions.md`](level_02_organizational_gluing_sheaf_obstructions.md) | Sheaf overlap conditions, quotient obstructions, four governance laws | Paper II (`lggr_ii`), `organizational_gluing_core.py` |
| **03** | [`level_03_epk_gtla_six_role_overlay.md`](level_03_epk_gtla_six_role_overlay.md) | Six-role GTLA overlay: Planner, Proposer, Governor, Worker, Arbiter, Auditor | Paper III (`lggr_iii`), `epk_overlay.py` |
| **04** | [`level_04_completion_relative_obstructions.md`](level_04_completion_relative_obstructions.md) | 2-adic inverse systems, thread existence (Stacks 086J), reflection $\eta$, $R^1 \varprojlim$ | Paper IV (`lggr_iv`), `lggr_iv_core.py` |
| **05** | [`level_05_finite_no_recovery_theorem.md`](level_05_finite_no_recovery_theorem.md) | No-Recovery Theorem, blind-spot geometry, 6-site distance-2 defect | Paper V (`lggr_v`), Lean 4 proofs |
| **06** | [`level_06_nonlinear_aggregation_adjoint_probing.md`](level_06_nonlinear_aggregation_adjoint_probing.md) | Observation map $Q$, Gram operator $Q^T Q$, adjoint illumination of $\ker(Q)$ | Paper VI (`lggr_vi`), `bound_measurement.py` |
| **07** | [`level_07_omega_engine_crate_architecture.md`](level_07_omega_engine_crate_architecture.md) | `omega_local_green_global_red_lggr` crate architecture | Monorepo components, 44 files |
| **08** | [`level_08_lean4_mechanization_and_target_checkers.md`](level_08_lean4_mechanization_and_target_checkers.md) | Formal Lean 4 Lake proofs, Python target checkers (`stage_021.py`) | Adversarial test suites |
| **09** | [`level_09_runtime_guardrails_and_protocol_synthesis.md`](level_09_runtime_guardrails_and_protocol_synthesis.md) | Synthesis: The Seven Runtime Guardrails against evaluator blind spots | Operational runbook |
