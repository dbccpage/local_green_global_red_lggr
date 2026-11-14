---
title: "Claim Ledger — Paper 028"
subtitle: "Finite Authority and Non-Terminal Computation"
author: "Jeremy H. Carroll"
date: "2026-10-23"
---

**Paper Key:** `001_finite_obstruction_calculus/028_finite_authority_and_non_terminal_computation`  
**Retired Paper Identity:** `AF-003`  <!-- Retired 2026-08-18. Stamped from lean_identity_map.yaml, which describes the pre-rename tree, and restamped to the Paper Key above. Kept so an old citation to this code meets an explanation rather than nothing. -->

Prepared edition 2.0.3 (2026-10-23). Companion to this paper's inline Appendix D Claim-Type Ledger. Where this file and the paper differ, the paper is canonical.

Claim types (Finite Obstruction Calculus/Layered Authority Framework permitted set): `[DEFINITION]`, `[DECLARED AXIOM]`, `[IMPLEMENTATION CONTRACT]`, `[POLICY RULE]`, `[VERIFIED]`, `[PROVEN, CONDITIONAL + H1…Hn]`, `[STANDARD + citation]`, `[MECHANIZED]`, `[MECHANIZED-PARTIAL]`, `[WORKED EXAMPLE]`, `[INTERPRETIVE]`, `[CONJECTURE]`, `[OPEN]`, `[OBSTRUCTION]`, `[SCOPE FENCE]`, `[REFUSED]`, `[FRAMEWORK]`. A Finite Obstruction Calculus/Layered Authority Framework compliance pass (2026-07-17) mapped this ledger's previously free-form values (`[MECHANIZED WITNESS]`, `[DEFINITION + MECHANIZED BOOLEAN KERNEL]`, `[DEFINITION / OPERATIONAL RULE]`, `[EMPIRICAL / OPERATIONAL EVIDENCE]`) onto this set.

**Public status:** prepared republication edition 2.0.3; consolidation/companion paper, not a new public deposit. Drafted against Layered Authority Framework v1.2; controlling preprint now `999_Layered Authority Framework/v1.3_preprint.md` (see paper §0 lineage note). The Lean in this deposit is [FiniteAuthority](lean4/FiniteAuthority.lean). `omega_engine/lean4/PaperAF003` is not in this deposit.

**Authority status:** **This paper mints no authority.** It is an authority-*theory* paper, not an authority *source*. Scoped per paper §0.2: `ContractAuthority` and `VerifierScopedAuthority` available only relative to a declared packet $D$ and named verifier $V$; **`SemanticAuthority` UNAVAILABLE** — no semantic adapter is declared. Ownership (paper §0): **Finite Descent Verification** owns the Authority type and $\mathsf{IsAuth}$; **Layered Authority Framework** owns terminalization discipline and non-promotion rules; **Finite Obstruction Calculus** mints nothing. This paper owns none of the three.

**Verification Grounding & Mechanization Scope:** Rows marked `[PROVED]` are the finite statements in [FiniteAuthority](lean4/FiniteAuthority.lean) (Lean 4.35.0, no `sorry`) together with the Python checks that call `code/mod_finite_authority_core.py`. A 2026-07-17 receipt for `lake build PaperAF003` names files that are not in this deposit. Those names are `[NEGATIVE BOUNDARY]`, not proofs of this package. The proved Lean statements are flag and fiber facts. They are not $\mathsf{Authority}_D$, and they are not theorems about Turing machines.

---

Canonical FA-prefixed IDs are additive publication identifiers; every legacy label is retained unchanged for existing cross-references.

A. Framing and fences
---------------------

| Claim ID | Legacy label | Claim (location) | Type | Basis |
|---|---|---|---|---|
| FA-A1 | A1 | Claim discipline list 1–6 (§1) | `[SCOPE FENCE]` + `[DEFINITION]` | The paper's theses, scoped; each is grounded in an imported object or inherited theorem below |
| FA-A2 | A2 | Proposal-system framing of LLMs/programs/institutions (§2) | `[INTERPRETIVE]` — explicitly "structural analogy, not an ontological equivalence" (§2) | Honest as stated |
| FA-A3 | A3 | Verifier soundness is the trust root (§0.1) | `[SCOPE FENCE]` | Load-bearing assumption, declared |
| FA-A4 | A4 | Non-claims 1–12 (§20); consciousness fence (§19) | `[SCOPE FENCE]` | Cross-checked; no section asserts a fenced item |

B. Imported formal machinery
----------------------------

| Claim ID | Legacy label | Claim | Type | Home |
|---|---|---|---|---|
| FA-B1 | B1 | Authority object $\mathsf{Authority}_S(x)$ / $\mathsf{Authority}_D(x,a)$ and the $\mathsf{IsAuth}$ guard (§0) | `[DEFINITION]` | **Finite Descent Verification** — corrected 2026-07-17. Under the tower ownership split the Authority type, `IsAuth`, and descent-packet data are Finite Descent Verification-owned; this row previously named Layered Authority Framework, which owns terminalization discipline and non-promotion rules but not the type |
| FA-B1A | B1a | Kernel chain $\text{Difference}\to\text{Repair}\to\text{Quotient}\to\text{Closure}\to\text{Authority}$; packet $D=(K,E,V,\tau,\Lambda)$ (§0, §3) | `[DEFINITION]` | Layered Authority Framework (`999_Layered Authority Framework/v1.3_preprint.md`, `math_spine.md`). Root fence added at paper §0: the chain is a pipeline of declared packet stages, **not** a genesis order; `Difference` = the non-sameness aspect of an admitted cut, co-admitted with exhibited-retention Structure, neither prior to the other |
| FA-B2 | B2 | EPK $Z_\theta^{\lambda,\mu}(y\mid x)$ (§4) | `[DEFINITION]` | Papers 020/025; §4.2 fences what it is not |
| FA-B3 | B3 | $\Delta_E$ gluing defect; local-green/global-red (§11) | `[DEFINITION]` + non-composition inherited. The finite split proved here is D1 | Paper 020 (G1–G4 locus), Paper 023 (organizational case). `PaperAF003.LGGR` is not in this deposit |
| FA-B4 | B4 | $\mathsf{Computation}_{Layered Authority Framework}$ refinement table (§13) | `[DEFINITION]` | Layered Authority Framework refinement; no claim against computability theory |

C. Inherited theorems (LLM spine T1–T15)
----------------------------------------

| Claim ID | Legacy label | Claim | Type | Home + status note |
|---|---|---|---|---|
| FA-C1 | C1 | §5 compressed theorem map T1–T15; the consequences used in §§2.1, 7, 8, 9, 10 | `[NEGATIVE BOUNDARY]` | The cited homes are encyclopedia prose outside this deposit (`Status: PROVED-PROSE`). They are not theorems of [FiniteAuthority](lean4/FiniteAuthority.lean). **PL-027-2 stays OPEN** |
| FA-C1A | C1a | T1 Proposal Non-Authority (§2.1) — the paper's central claim | `[NEGATIVE BOUNDARY]` | Home file `08` is prose, not a proof in this deposit. H1 and H2 are not discharged here |
| FA-C2 | C2 | Dominance $\epsilon_T < \epsilon_G$ (§18, T15) | `[NEGATIVE BOUNDARY]` | Home file `37` is prose. **FFC** is a modelling assumption, not a theorem of this deposit. §18 already says the comparison is conditional and empirical |
| FA-C3 | C3 | Counterfeit contradiction test (§14) | `[DEFINITION]` (typed contradiction). Detection-completeness is `[NEGATIVE BOUNDARY]` | The $\Phi$ separation used for detection-completeness is an open gate at its home. It is not checked by this deposit |

D. Own claims of this paper
---------------------------

| Claim ID | Legacy label | Claim | Type | Basis |
|---|---|---|---|---|
| FA-D1 | D1 | On a finite index set, if the local color is constant on the declared relation and the joint local/global color is not, then some related pair shares a local color and differs in verdict (§4.3) | `[PROVED]` | Lean `lggr_has_global_split`, `two_point_lggr`, `three_point_not_lggr`. Python `LGGRObstruction.verify_lggr_obstruction` in `test_lggr_quotient_obstruction_exhaustive_carrier_and_counterexample`. `PaperAF003` is not in this deposit |
| FA-D2 | D2 | Quotient-modulo LGGR generalization (§4.3) | `[NEGATIVE BOUNDARY]` | The congruence-modulo statement is not a theorem of this deposit. `PaperAF003.lggr_mod_nonpromotion` is absent |
| FA-D3 | D3 | $\mathsf{CertifiedAuthority}_D \iff \bigwedge_{i=1}^{8} C_i$ (§6) | `[DEFINITION]` | Definitional, as §6 states. `PaperAF003.certified_iff_all_gates_true` is not in this deposit (see D3a). The prior label `[DEFINITION + MECHANIZED BOOLEAN KERNEL]` is withdrawn |
| FA-D3A | D3a | **Gate-vector correspondence** (§6) | `[OPEN]` | **Found 2026-07-17.** The paper's C1–C8 (proposal, parse, canonicalization, verifier, answer fiber, replay, leakage, terminal) and Lean's `DescentGateVector` (`hasRepresentation`, `hasEvaluator`, `hasVerifier`, `hasReplay`, `hasLeakageBoundary`, `hasResidualLedger`, `hasTerminalizer`, `terminalAccepts`) are **different eight-tuples**; only 4 of 8 correspond. Both have arity 8, which hid the mismatch. §6's $\bigwedge_{i=1}^{8} C_i$ is therefore **not mechanized**; §6 and Appendix E now say so. Reconciling the two vectors is an open obligation |
| FA-D3B | D3b | $\mathsf{Authority}_D \Rightarrow \bigwedge_i C_i$ (gate necessity, §6) | `[POLICY RULE]` | **Declared, not proved.** What a compliant packet $D$ is required to enforce. Earlier revisions wrote $\neg C_i \Rightarrow \neg\mathsf{Authority}_D$ as though it followed from the definitional $\iff$, which is stated for $\mathsf{CertifiedAuthority}_D$ — a different predicate. Corrected this pass |
| FA-D3C | D3c | $\bigwedge_i C_i \Rightarrow \mathsf{Authority}_D$ (gate sufficiency, §6) | `[REFUSED]` | **Refused this pass.** $\mathsf{Authority}_D$ is the Finite Descent Verification dependent object: a terminal $t$ with $\Pi_D^\sharp(x,a)=\mathsf{inl}(t)$ *and* a proof of $\mathsf{IsAuth}_D(t)$. A conjunction of eight Booleans does not construct that pair, and nothing in the paper or its Lean module does. Granting to a conjunction of predicates what §§2.1/7/8/13 deny to generation, self-critique, scaling and halting is the category error this paper exists to refuse. Recorded as an `OBSTRUCTION` block at §6 |
| FA-D4 | D4 | Gate minimality: removing any $C_i$ admits a known counterfeit/failure mode (§6) | `[OPEN]` | Failure terminals are named per gate, but no per-gate removal-witness catalog exists in this paper — **PL-027-1** |
| FA-D5 | D5 | A halted flag with no gate stack is `nonAuthorityHalt`; gates without a witness are `checklistCertified`; both flags true is `authority` (§2.2, §13) | `[PROVED]` + `[SCOPE FENCE]` | Lean `halt_alone_not_authority`, `gates_without_witness_not_authority`, `gates_and_witness_authority`, `witness_mismatch_refuses`, `unhalted_is_proposal`. Python `evaluate_halted_trace` in `test_halting_does_not_imply_authority_and_checklist_scoping`. These are equalities of `HaltStatus`. They are not a theorem about Turing machines, and `HaltStatus.authority` is not $\mathsf{Authority}_D$ |
| FA-D6 | D6 | Positive residual with surface signs is `counterfeitRefusal`; positive residual without them is `verifierRefusal`; zero residual and no gates is `nonAuthorityHalt` (§14) | `[PROVED]` + `[SCOPE FENCE]` | Lean `residual_surface_counterfeit`, `residual_plain_refuses`, `zero_residual_no_gates`, `zero_residual_gates_checklist`, `zero_residual_witness_authority`, `unhalted_counterfeit_is_proposal`. Python `detect_counterfeit_descent` in `test_counterfeit_descent_detection_and_missing_evidence_safeguards`. This is a flag machine, not a theorem that surface signs never imply $\mathsf{Authority}_D$ |
| FA-D7 | D7 | Evaluator sovereignty witness (§15) | `[NEGATIVE BOUNDARY]` | `PaperAF003.self_owned_evaluator_boundary_witness` is not in this deposit. No checker here verifies that witness |
| FA-D8 | D8 | EPK lift candidates require evidence fields (§4.3, Appendix E) | `[NEGATIVE BOUNDARY]` | `PaperAF003.licensed_epk_lift_requires_all_fields` and `PaperAF003.carrier_change_alone_refuses_epk_lift` are not in this deposit |
| FA-D9 | D9 | Benchmark transfer schema $\chi$, $s_T \ge s_B - \delta(\chi)$ (§9) | `[POLICY RULE]` | Declares what a transfer claim must supply; no transfer theorem is asserted. The `SpecificationIdentity` it would require is unsupplied (paper §0.3) |
| FA-D10 | D10 | $r_G > r_V \Rightarrow$ unresolved backlog grows (§14.1) | `[INTERPRETIVE]` | Elementary rate comparison; no queueing model claimed. Paper already hedges: "a pressure model, not a full queueing theorem" |
| FA-D11 | D11 | Worked example (§6.1) | `[WORKED EXAMPLE]` | Concrete packet; gate vectors; geometric retry-decay numbers. **Import note added this pass:** the decay numbers import probability semantics + retry independence; no probability adapter is declared |
| FA-D12 | D12 | Kaggle/sweeper evidence reading (§18.1) | `[INTERPRETIVE]` | A reading of evidence review files under `omega_engine/products/omega_engine_kaggle/evidence`; local green firewall/replay state does not imply global deployability. Not a result |
| FA-D13 | D13 | Engineering protocol / runtime logs (§17, §18, Appendix B) | `[IMPLEMENTATION CONTRACT]` | Interface contracts, not theorems |
| FA-D14 | D14 | Probability semantics (§6.1, §8, §18) | `[SCOPE FENCE]` — **IMPORTED** | Recorded this pass. A probability measure over samples, independence across retries, a limit over a model sequence (§8), and measured error rates (§18) are **imported representation structure**, not constructed at this paper's degree. **No probability adapter is declared.** The structural conclusions do not depend on the probabilistic reading; the numbers do. Paper §4's gloss of $P_\theta(\gamma\mid x)$ as "proposal mass" is the correct doctrinal reading and is now applied consistently |
| FA-D16 | D16 | For nonempty verdict fibers, the refined count equals the fiber count plus $\sum(|G(q^{-1}(u))|-1)$ (§4.4) | `[PROVED]` | Lean `increase_formula`, `demo_increase`, `demo_refined`, `demo_formula`, `demo_split_verdicts`. Python `compute_minimal_verdict_refinement` in `test_minimal_verdict_refinement_derivation`. The coarsest refinement sentence in §4.4 is argued in prose and is not a theorem of [FiniteAuthority](lean4/FiniteAuthority.lean) |
| FA-D15 | D15 | Authority scope typing (§0.2) | `[DEFINITION]` + `[SCOPE FENCE]` | Added this pass. `ContractAuthority` / `VerifierScopedAuthority` available relative to declared $D$ and $V$; **`SemanticAuthority` UNAVAILABLE** — no semantic adapter declared. The paper previously described verifier-relativity in prose (§0.1, §16) without ever typing it |

E. Open / obligations (cross-ref global proof ledger)
-----------------------------------------------------

| Obligation | Strengthens | Status | Global ledger ID |
|---|---|---|---|
| Per-gate minimality witness catalog: for each $C_i$, a concrete counterfeit or failure mode admitted when only $C_i$ is removed | Upgrades **D4** from `[OPEN]` to `[VERIFIED]` (by witness exhibition). *(This row previously read "D2", which is the quotient-modulo LGGR row — cross-reference corrected 2026-07-17.)* | OPEN | **PL-027-1** |
| Verify and migrate the LLM-spine T1–T15 home files into the **indexed** canonical encyclopedia with statuses | Grounds every inherited typing in section C | OPEN | **PL-027-2** — *reframed 2026-07-17.* The cited source path `archive/encyclopedia_anomalon/` does not exist; the files are at `encyclopedia/archived_research/encyclopedia_anomalon/`. The obligation survives the correction: `archived_research/` is a harvest folder, not the indexed spine, and every home reads `Status: PROVED-PROSE` |

**Opened by the Finite Obstruction Calculus/Layered Authority Framework compliance pass (2026-07-17). Not yet registered with global ledger IDs** — these are recorded here so they are not lost, and require a global-ledger entry to become tracked obligations:

| Obligation | Strengthens | Status |
|---|---|---|
| Reconcile the §6 C1–C8 gate stack with Lean's `DescentGateVector`, or mechanize C1–C8 as stated | Closes **D3a**; would make §6's $\bigwedge_{i=1}^{8}C_i$ genuinely mechanized rather than arity-coincident | OPEN |
| `DetectorAdequacy` certificate for each gate detector (protected distinctions, adversarial cases, blind spots) | Closes the §0.3 gap. Live, not theoretical: §16 books "Parser insufficiency" and "Canonicalizer collapse" as serious, and `minimal_lggr_witness` is itself a maximally collapsed detector ($\delta \equiv$ `true`, constant local verdict) | OPEN |
| `ExhaustionWitness` for gate C5, or a declared $V$-uniqueness property | Makes C5 finitely checkable. $A_x$ quantifies over **all** traces, so $\lvert A_x \rvert = 1$ cannot be read off a run (§12.1) | OPEN |
| Probability adapter for §6.1 / §8 / §18, or restatement as unit-sum weight profiles | Discharges the D14 import | OPEN |
| `SpecificationIdentity` object for the §9 transport map $\chi$ | Turns D9 from a `[POLICY RULE]` into a usable transfer route | OPEN |
| Establish $\mathsf{Authority}_D \Rightarrow \bigwedge_i C_i$ at its Finite Descent Verification/Layered Authority Framework home, or keep it a declared packet rule | Closes **D3b**; currently the only thing making a failed gate refuse the §0 authority object rather than solely this paper's certificate | OPEN |

Inherited conditionals tracked at home, not re-registered: Layered Authority Framework v1.3 Known Gate / Open Check #1 (Φ positive-definiteness); G1–G4 (Paper 020); organizational closure (Paper 023).

**Out of this pass's write boundary — reported, not fixed.** [index:index:FiniteAuthority.lean](omega_engine/research/_indexes/_master_index.yaml):18` carries the docstring "The eight gate fields named in Paper 027's finite descent stack". That is false of the paper's C1–C8 stack (see D3a); the structure's fields are the §3 packet vector. Recorded for the Lean owner.

F. Lean in this deposit
-----------------------

[FiniteAuthority](lean4/FiniteAuthority.lean) elaborates with Lean 4.35.0. The census axioms on the proved theorems are only `propext` and `Quot.sound`. There is no `sorry`. The names `PaperAF003.*` are not files in this deposit, so each of those names is `[NEGATIVE BOUNDARY]`.

| Theme | Lean theorem(s) in this deposit | Status |
|---|---|---|
| finite LGGR split | `lggr_has_global_split`, `two_point_lggr`, `three_point_not_lggr`. Pytest `test_lggr_quotient_obstruction_exhaustive_carrier_and_counterexample` calls `LGGRObstruction`. | `[PROVED]` (D1) |
| class-increase identity | `increase_formula`, `demo_increase`, `demo_refined`, `demo_formula`, `demo_split_verdicts`. Pytest `test_minimal_verdict_refinement_derivation` calls `compute_minimal_verdict_refinement`. | `[PROVED]` (D16). Not the coarsest refinement quantifier |
| halt-status separation | `halt_alone_not_authority`, `gates_without_witness_not_authority`, `gates_and_witness_authority`, `witness_mismatch_refuses`, `unhalted_is_proposal`. Pytest `test_halting_does_not_imply_authority_and_checklist_scoping` calls `evaluate_halted_trace`. | `[PROVED]` (D5). Not a Turing theorem |
| counterfeit-status separation | `residual_surface_counterfeit`, `residual_plain_refuses`, `zero_residual_no_gates`, `zero_residual_gates_checklist`, `zero_residual_witness_authority`, `unhalted_counterfeit_is_proposal`. Pytest `test_counterfeit_descent_detection_and_missing_evidence_safeguards` calls `detect_counterfeit_descent`. | `[PROVED]` (D6). Not $\mathsf{Authority}_D$ |
| quotient-modulo LGGR, gate-vector `Iff.rfl`, evaluator sovereignty, EPK lift lemmas | absent `PaperAF003` names | `[NEGATIVE BOUNDARY]` |

**Standing caveat.** `HaltStatus.authority` and `CounterfeitStatus.authority` are constructors of finite enumerations. They are not $\mathsf{Authority}_D$. The module contains no `IsAuth` and no descent packet. It discharges no Finite Descent Verification obligation.

<!-- claim-id-body-only-sync:begin -->

Body-only ID sync (packaging)
-----------------------------

**AuthorityEffect:** None. Packaging hygiene; no OPEN→PROVED.

| ID | Claim | Type | Status |
|---|---|---|---|
| Layered Authority Framework-T15 | Body claim-shaped ID registered for bijection packaging only; OPEN; not upgraded | OPEN | packaging |

<!-- claim-id-body-only-sync:end -->

## Named regression entry points

These checks exercise the bundled finite models; they do not close the ledger's OPEN or external obligations.

- `code/tests/test_finite_authority.py::test_lggr_quotient_obstruction_exhaustive_carrier_and_counterexample`
- `code/tests/test_finite_authority.py::test_minimal_verdict_refinement_derivation`
