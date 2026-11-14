# Change Log: Operator Dynamics and Structural Constraints in L1 Obstruction Systems
## 026_operator_proposal_layer_for_finite_l1_obstruction_systems (Zenodo Record 20213064)

**Authority Nonclaim:** This change log records structural, theoretical, and editorial revisions. It carries no operational authority or institutional standing.

### Repair record (2026-10-09)

Narrowed the four rows that were labeled proved to the finite sentences elaborated in `lean4/Proposal.lean`, and pointed each row at the Python test that calls the shipped checker. External `PaperAF000` sketches stay outside the deposit. Version 2.0.3 and publication date 2026-10-08 are unchanged.

### Version 2.0.3 (2026-10-08)

* **R1 — Evaluator-Owned Evidence & Ratio Verification (§6):**
  * Updated `GuardedEvaluator.evaluate_acceptance` to independently compute and verify the target ratio $R_{cl}$, rejecting altered or spoofed caller ratios fail-closed.
  * Enforced that when no 2-complex ($d_1$ differential) is declared, $\Gamma_2$ defaults strictly to the neutral convention ($0$), refuting arbitrary caller-injected $\Gamma_2$ values from manufacturing secondary tiebreak descent.
  * Split the pure diagnostic tuple predicate `evaluate_tuple_acceptance` from the public field-bound evaluator, ensuring hypothetical tuple tests cannot establish a public verification bypass.
  * Added domain validation in `EvaluatorPolicy` and `ObstructionTuple` enforcing non-negative parameters.
* **R2 — Carrier and Field Dimension Binding (§5, §6):**
  * Bound proposal endpoints to admitted complex edge carrier dimensions; ordinary proposals changing carrier dimensions (e.g. $(2,0,0) \to (1,)$ or $(2,0,0) \to ()$) are rejected before diagnostics.
  * Introduced `StructuralOperatorProposal` requiring explicit source/target `AdmittedComplex` carriers and carrier mapping.
  * Removed field truthiness switches: empty carriers compute actual diagnostics $(0,0,0,0)$ and verify them fail-closed.
* **R3 — General Graph Solver & Primal/Dual Witnesses (§2, §3a):**
  * Distinguished cycle specialization from general graph solvers; implemented `ExactPrimalDualWitness` and `verify_primal_dual_witness` checking residual $r = \omega - B f$, divergence-free dual flow $B^T z = 0$, bound $\|z\|_\infty \le 1$, and zero duality gap $\|r\|_1 = \langle z, \omega \rangle$.
  * Implemented exact tree solver `solve_tree_witness` verifying tree exactness ($\Phi_1 = 0$ on paths/trees such as $(1, 1) = d_0(0, 1, 2)$).
  * Enforced 2-complex condition $d_1 \circ d_0 = 0$ on `AdmittedComplex` initialization, rejecting malformed boundary matrices.
* **R4 — Realizable Secondary Tie-Break on Theta-Graph (§3b, §6):**
  * Added realizable graph-bound theta-graph example (vertices 0, 1, 2, 3; edges 01, 12, 02, 03, 32; faces $(1, 1, -1, 0, 0)$ and $(0, 0, -1, 1, 1)$).
  * Verified transition $(0, 0, -1, 0, 0) \to (1, 0, 0, 0, 0)$ with equal independently certified $\Phi_1 = 1$, strict $\Gamma_2$ decrease $2 \to 1$, and target $R_{cl} = 1 \le 1$ accepted on second-order tiebreak under full complex binding.
* **R5 — External-Xi Trust Boundary (§6):**
  * Formalized the external trust boundary for the imported $\Xi$ functional; added `xi_evaluator` interface to `GuardedEvaluator`.
  * Rejects caller attempts to forge $\Xi$ descent on unchanged fields without an evaluator-bound verifier.
* **R6 — Corrected Claim-to-Artifact Mappings (§5, §6a, §6b):**
  * Added executable unit tests in `test_operator_proposal.py` directly exercising `CyclicShift` holonomy invariance on $C_3$ (C12), Local-Green / Global-Red non-promotion on covering atlases (C13), and path operator metadata erasure with endpoint continuity bridges (C14).
  * Updated claim ledger C3, C11, C12, C13, C14 to align with implemented and verified artifacts.
* **R7 — Exact Ratio vs Threshold-Routing Policy Separation (§3b):**
  * Implemented `compute_r_exact` returning exact algebraic ratio $\Gamma_2 / \Phi_1$, alongside `compute_r_epsilon` with named routing statuses (`REGULAR`, `SUB_EPSILON_FLAT`, `UNBOUNDED_CURVATURE_SENTINEL`).
  * Tested sub-epsilon regime ($\Phi_1 = 1/4000, \Gamma_2 = 1/2000, \varepsilon = 1/1000 \implies R_{\mathrm{exact}} = 2, R_\varepsilon = 0$, status `SUB_EPSILON_FLAT`).
* **R8 — Release Portability & Manifest Canonicalization:**
  * Pinned release byte format to canonical LF (`\n`), harmonizing working tree files, Git blob representations, and SHA-256 manifests.
* **Mathematical Extension — Continuation-Stable Erasure:**
  * Authored `docs/mathematical_extension.md` deriving the coarsest state quotient $X / {\sim_T}$ for admitted operator families $\mathcal{T}$, establishing maximality in $\ker(D)$, and providing the translation counterexample on $C_3$.
* **Expanded Verification Suite:**
  * Expanded unit test suite from 14 to 29 tests in `code/tests/test_operator_proposal.py` covering all R1–R8 invariants and the continuation-stable extension.

---

### Version 2.0.2 (2026-10-08)

* **Lie Algebra Identification (§4b):**
  * Corrected Lie algebra classification for channel operators: real skew-symmetric operators $T_a : \mathbb{R}^k \to \mathbb{R}^k$ with $T_a^T = -T_a$ close to $\mathfrak{so}(k)$.
  * Explicitly scoped $\mathfrak{u}(k)$ to complexified carrier spaces $\mathbb{C}^k$ under skew-Hermitian operators $T_a^\dagger = -T_a$.
* **Mandatory Transition & Strict Descent Gate (§6):**
  * Updated `GuardedEvaluator.evaluate_acceptance` to require both before and after diagnostic tuples; reject single-state queries fail-closed.
  * Enforced strict lexicographic decrease on $(\Phi_1, \Gamma_2, \Xi)$; rejects any transition where $\Phi_1$ increases (e.g. $1 \to 2$ under ceiling 10), even when within static ceilings.
* **Host Field Diagnostic Binding (§6):**
  * Added certified field binding in `evaluate_acceptance` and `evaluate_proposal_step`: host independently evaluates field diagnostics from `initial_field` and `proposed_field`, rejecting spoofed or decoupled caller diagnostic tuples.
* **Piecewise $R_{cl}$ Guard Enforcement (§3b):**
  * Confirmed and tested piecewise guard: returns `None` ($+\infty$) whenever $\Phi_1 \le \varepsilon < \Gamma_2$, triggering unconditional rejection of unbounded curvature transitions (tested with $\varepsilon = 1/1000$, $\Phi_1 = 1/2000$, $\Gamma_2 = 1/500$).
* **Matrix Row Dimension Validation:**
  * Updated `compute_gamma2_simple` to raise `ValueError` on mismatched matrix row widths, eliminating silent truncation via `zip`.
* **Expanded Verification Suite:**
  * Expanded unit tests from 10 to 14 in `code/tests/test_operator_proposal.py` directly probing row dimension errors, single-state rejection, spoofed diagnostic detection, and infinite curvature gates.
* **Ledger Harmonization:**
  * Updated Claim Ledger `C8` and `C11` with exact mathematical classifications and verified field binding scopes.

---

### Version 2.0.1 (2026-10-07)

* **Guarded Descent Enforcement (§6):**
  * Updated `GuardedEvaluator.evaluate_acceptance` to enforce the strict lexicographic descent law on $(\Phi_1, \Gamma_2, \Xi)$ across transitions.
  * Rejects unchanged obstruction tuples, worsening proposals (e.g. $1 \to 2$), and transitions failing the $R_{cl}$ gate.
  * Evaluates third-order tiebreak on $\Xi$ functional.
* **Direct Field Diagnostics Binding:**
  * Added `evaluate_proposal_step` and `evaluate_field_diagnostics` to `GuardedEvaluator`, computing diagnostics directly from initial and proposed 1-cochains, preventing caller-supplied disconnected tuples.
* **Piecewise Closure Ratio ($R_{cl}$) Alignment (§3b):**
  * Aligned code and manuscript to the exact piecewise definition: $\Gamma_2 / \Phi_1$ for $\Phi_1 > \varepsilon$, $0$ for $\Phi_1, \Gamma_2 \le \varepsilon$, and $+\infty$ for $\Phi_1 \le \varepsilon$ while $\Gamma_2 > \varepsilon$.
  * Removed false claim that $+\infty$ is unreachable in exact arithmetic; documented and tested the $\omega=(3/4000, 0, 0)$ counterexample yielding $+ \infty$ curvature and immediate gate rejection.
* **Mathematical Invariance of $\Gamma_2$ (§3b):**
  * Corrected text to establish that because $d_1 \circ d_0 = 0$, $\Gamma_2 = \|d_1 \omega\|_1 = \|d_1 h_1\|_1$ is an exact invariant of the cochain field $\omega$ independent of the $\ell^1$ potential solver convention.
* **Sheaf Gluing vs Policy Acceptance Distinction (§6a):**
  * Clarified that compatible local edge data glue into a global section by presheaf agreement, reserving evaluator policy gates for acceptance of an assembled global proposal.
* **External Lean Import Scoping (§6, §6a, §6b):**
  * Explicitly relabeled external Lean formalizations (`PaperAF000`) as external unverified design imports not bundled or verified in this deposit.
* **Code License Harmonization:**
  * Replaced PolyForm Noncommercial License with standard Apache-2.0 in `LICENSE-CODE`, harmonizing README, pyproject.toml, and Zenodo metadata.
* **Extended Test Suite:**
  * Expanded unit tests from 4 to 10 in `code/tests/test_operator_proposal.py` validating strict descent, tiebreak chains, worsening rejection, $+\infty$ curvature rejection, field diagnostics binding, and potential invariance.
* `verify_deposit.py` shared exclusions aligned with paper template; `scripts/regen_sha256sums.py` and `tools/rebuild_release.py` aligned.

---

### Version 2.0.0 (2026-10-07)

* **Repository Canonicalization & Clean Architecture:**
  * Canonicalized under `001_finite_obstruction_calculus/026_operator_proposal_layer_for_finite_l1_obstruction_systems`.
  * Harmonized with Zenodo Record `20213064` (DOI: `10.5281/zenodo.20213064`).
* **Jargon & House Language Eradication:**
  * Removed internal esoteric terminology, compliance notes, and Mechanism Inventory tables.
  * Replaced internal governance headers with standard academic frontmatter and explicit nonclaims.
  * Truncated developmental revision notes and obsolete crate registry entries from the public monograph text.
  * Established clean separation: public monograph ends after references, while detailed formal claim statuses reside in `operator_proposal_layer_for_finite_l1_obstruction_systems_claim_ledger.md`.
* **Claim Hygiene & Hype Prohibition:**
  * Screened entire manuscript against claim hygiene rules, replacing promotional verbs with defensible, scoped descriptions.
* **Executable Verification Code:**
  * Added reference Python package under `code/mod_operator_proposal_core.py` modeling discrete coboundaries ($d_0$), $\ell^1$ cycle obstructions ($\Phi_1$), second-order closure defects ($\Gamma_2$), closure ratios ($R_{cl}$), and the `GuardedEvaluator` enforcing Evaluator Supremacy using exact rational arithmetic (`fractions.Fraction`).
  * Added comprehensive test suite under `code/tests/test_operator_proposal.py` (all tests passing).
* **Package Deposit Standards:**
  * Added `pyproject.toml`, `zenodo_metadata.json`, `docs/descriptions.md`, `docs/references.md`, `README.md`, `LICENSE`, `LICENSE-CODE`, and `verify_deposit.py`.

---

### Version 1.1 (2026-06-13)

* Initial pre-print release of the Operator Proposal Layer framework on Zenodo (Record 20213064).
