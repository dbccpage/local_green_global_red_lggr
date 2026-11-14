Paper 027 Claim Ledger
======================

**Paper Key:** `001_finite_obstruction_calculus/027_the_authority_firewall_a_machine_checked_separation_of_evidence_from_authority_in_finite_systems`  
**Retired Paper Identity:** `AF-001`  <!-- Retired 2026-08-18. Historical AF/PL identifiers remain as stable tracking codes. -->

Paper: `authority_firewall_monograph.md`

Date: 2026-10-23  
Public status: prepared edition 2.1.1 (2026-10-23); no new public deposit is asserted.

Source spine used for status: the frozen v002 canonical spine. **Path correction (2026-07-17):** the path previously recorded here, `omega_engine/research/omega_engine_theory/math_spines_v002`, **does not resolve**; neither does `omega_engine/research/archive/math_spines_v002/`. The cited document survives at `omega_engine/.omega_engine_official_archive/canonical_omega_math_spine.md` (4797 lines), with the v002 set frozen in `omega_engine/.omega_engine_official_archive/math_spines_v002.zip`. Per CLAUDE.md the canonical math system is now the **encyclopedia** (`omega_engine/research/encyclopedia/`); the spine citations below are therefore citations into a **superseded, archived** source and are retained only as historical provenance for statuses set at authoring time. Re-anchoring this paper's canonical citations to encyclopedia entries is **PL-024-9**.

Allowed claim tags: `[DEFINITION]`, `[VERIFIED]`, `[PROVEN, CONDITIONAL + H1...Hn]`, `[STANDARD + citation]`, `[MECHANIZED]`, `[MECHANIZED-PARTIAL]`, `[WORKED EXAMPLE]`, `[IMPLEMENTATION CONTRACT]`, `[SCOPE FENCE]`, `[CONJECTURE]`, `[INTERPRETIVE]`, `[OPEN]`, `[OBSTRUCTION]`, `[REFUSED]`, `[FRAMEWORK]`, `[POLICY RULE]`, `[DECLARED AXIOM]`.

**Canonical citation audit (2026-07-17), spot-checked against the archived spine:**

| Paper cites | Verdict |
|---|---|
| L932 — firewall invariant | **accurate**; also confirms `IsAuth` is canonically the **seven-guard** predicate (see AF-20) |
| L1560 — §II.2 Authority Σ-gate | **accurate** (`\mathsf{Authority}_S(x)`) |
| L1714-1716 — C4 irreducibility | **accurate**; supports AF-09 verbatim in substance |
| L3498-3499 — H3 | **WRONG — corrected in this pass.** Those lines are QM qubit proof obligations (PO-D14/PO-D19). Theorem V.2 and its three bullets are at **L3478-3492** (bullets L3482-3484). Both occurrences in the paper (§3.7, §5.2.1) repointed. |

Load-Bearing Claims
-------------------

| ID | Claim | Tag | Basis | Remaining action |
|---|---|---|---|---|
| AF-01 | For every residual outcome `r`, `not IsAuth (residualTerminal r)` — where `IsAuth` is **authority-summand membership**, NOT Def 2.2's seven-guard `IsAuth_S` (see AF-20). | `[PROVED]` | Lean `residual_not_auth` in [ResidualNonCreation](lean4/ResidualNonCreation.lean). | Python `test_pointwise_separation_theorem` calls `residual_not_auth`. |
| AF-02 | The dependent authority extractor `(forall r, IsAuth (residualTerminal r)) -> False` is empty when the residual layer is inhabited. | `[PROVED]` | Lean kernel `nat_residual_auth_empty` (L80-82); **H-inhab**: at least one residual outcome exists. Discharged concretely in-file by `authExtractor_empty` (L93-95) via `residualWitness`, which is unconditional. | Pytest `test_af02_witness_blocks_total_auth_extractor` calls `residual_not_auth` and `is_auth` on the residual witness `q42`. |
| AF-03 | No `FormalStructure -> AuthorityTerminal` exists under the declared no-terminalizer-evidence hypothesis **H-noEv**. | `[NEGATIVE BOUNDARY]` | The cited `AuthorityNonPromotion` is not in this deposit. The stated hypothesis is vacuous, so this row is not a proved firewall. Lean kernel `AuthorityNonPromotion` (**path corrected**), `no_formal_to_authority_when_no_terminalizer` (L77-82). **H-noEv := `TerminalizerEvidence -> False` is UNSATISFIABLE**: `TerminalizerEvidence` is the raw record `{packetId : String, terminalizerId : String, replayable : Bool}`, freely inhabited by `⟨"", "", false⟩`. The lemma is therefore vacuously true and carries **no firewall force**. The kernel's own header concedes the record is "raw and easily inhabited". The file's `VerifiedTerminalizerEvidence` lane is **also** vacuous (its `Prop`-valued fields are inhabitable by `True`). | **Downgraded in substance this pass** (tag unchanged; the vacuity is now disclosed rather than the status inflated). Do NOT cite as a "Descent Authority Lane firewall". Retain only as a type-design statement. Non-vacuous restatement = **PL-024-6**. |
| AF-04 | Obstruction Evidence Lane terminals are separated at the checked **exact-repair boundary only** (`exactRepair` vs each of `stabilizedSurvivor`, `openObstruction`, `refusal`); the remaining pairs are **not** proven. | `[NEGATIVE BOUNDARY]` | `TerminalDisjointness` is not in this deposit, so the exact-repair separation is not a proved row here. Lean kernel `TerminalDisjointness` (**path corrected**), `terminal_disjoint_*` (L14-16). Companion `classify_unique` (L18-20) is the **trivial** single-valuedness of a function (`rfl` + `symm`), not substantive classification uniqueness. | Re-verified axiom-free at HEAD 2026-07-17. Do not describe `classify_unique` as classification uniqueness. `refusal`/NoRule is a **routing** terminal, not a fourth cohomology class — the cohomological part is three-way. |
| AF-05 | The compression theorem imports a five-primitive tower spine. | `[NEGATIVE BOUNDARY]` | Imported canonical spine dependency; not re-proven in Paper 024. | Cite the versioned canonical spine and keep the dependency explicit. |
| AF-06 | `Nat(Omega_LambdaOmega, Auth) = empty` follows from the Lean pointwise theorem plus H3 and the dependent-family-to-natural-transformation bridge. | `[NEGATIVE BOUNDARY]` | Math spine `firewall_separation_attack.md` reports pointwise witness proven and categorical form conditional on H3/bridge. | PL-024-1. |
| AF-07 | Four separately declared encodings (with no verified common adapter) factor through one Section II.2 Authority Sigma-gate. | `[OPEN]` | Current paper states per-type separation; federation is not mechanized. The two string/string/bool records and two singletons are separately declared types without a common adapter. | PL-024-2. |
| AF-08 | MAJOR-3 lossy chi coherence is bounded and orthogonal to the authority firewall. | `[OPEN]` | Math spine identifies missing comparison-cell well-definedness, pentagon, unit triangles, and naturality. | PL-024-3. |
| AF-09 | C4 replay/verifier soundness is the irreducible external trust root. | `[OPEN]` | Spine status says C4 cannot be derived from finite replay determinism plus totality; it can only be audited and shrunk. **Citation verified 2026-07-17** against archived spine L1714-1716, which states exactly this and adds the engineering directive to shrink C4 to a small audited replay-checker kernel. | PL-024-5. |

Authority-Scope and Mechanization-Scope Claims (added 2026-07-17, Finite Obstruction Calculus/Layered Authority Framework pass)
---------------------------------------------------------------------------------

| ID | Claim | Tag | Basis | Remaining action |
|---|---|---|---|---|
| AF-20 | Definition 2.2's seven operational guards ($\mathsf{IsAuth}_S$) and the structural authority predicate `IsAuth` are mechanized; `is_auth_s_factors_through_is_auth` shows that operational authority factors through coproduct summand authority. | `[PROVED]` | Lean `is_auth_s_factors_through_is_auth` in [ResidualNonCreation](lean4/ResidualNonCreation.lean). | Python `test_seven_guards_predicate` calls `IsAuthGuards.all_guards_met`. |
| AF-21 | Authority scoping: **ContractAuthority** and **VerifierScopedAuthority** are in scope; **SemanticAuthority is NOT AVAILABLE** — no semantic adapter is declared in this paper. | `[SCOPE FENCE]` | Layered Authority Framework doctrine: SemanticAuthority requires a declared semantic adapter. §2.5 of the paper. The self-authorization failure mode of §1.1 is precisely the unlicensed slide from VerifierScoped to Semantic. | Keep §2.5 attached to any reuse of the firewall. Never read a green verifier as a true claim. |
| AF-22 | Authority-bearing use requires `SpecificationIdentity`, `DetectorAdequacy`, `ExhaustionWitness`, `EvidenceCeiling`, `ReplayWitness`, `Terminalizer`, `IsAuth`. This paper supplies a coproduct model, Boolean guard predicates and a conditional cochain bridge. Boolean flags do not construct an actual replay or search-exhaustion witness. It supplies **no operational certificate** for specification identity, detector adequacy, exhaustion, evidence ceiling or replay soundness. | `[OPEN]` | Paper §4 demonstrates two stages. Pre-adversarial review: the guards **passed** on asserted inputs (`search_exhaustive = True` hardcoded) while the answer was wrong — a fully replayable but **inadequate** detector. Post-adversarial review: after correcting inputs to reflect unverified search exhaustion, the authority route refused promotion. Replay caught nothing; out-of-band review did. | **PL-024-8**. Detector adequacy is prior to, and not implied by, replayability. |
| AF-23 | Lean path resolution: historical paths cited in earlier drafts are replaced by the self-contained bundled proof file at [ResidualNonCreation](lean4/ResidualNonCreation.lean). | `[IMPLEMENTATION CONTRACT]` | Bundled self-contained within deposit at [ResidualNonCreation](lean4/ResidualNonCreation.lean) under `OmegaCore.ResidualClosureLayer`. Verified axiom-free. | Self-contained in deposit; verifiable via [ResidualNonCreation](lean4/ResidualNonCreation.lean). |
| AF-24 | The two "attached" audit companions are **not attached**. | `[OPEN]` | `final_synthesis.md` exists at `omega_engine/research/omega_sweeper/04_model_runs/run_024_authority_firewall/final_synthesis.md` (link repointed). `001_review_verdict.md` is **absent from disk and from the restore source `449500d31`**; deleted by unrelated commit `fabfd650c` (2026-06-15 `.planning` cleanup); recoverable from `a6cf93ff0`. | Restoring `001_review_verdict.md` is outside this pass's write boundary — **human action required**. |

Empirical and Interpretive Claims
---------------------------------

| ID | Claim | Tag | Basis | Remaining action |
|---|---|---|---|---|
| AF-10 | Kaggle Clause 4 is refuted: the supposed independent evaluator delegates to the same enumerator. | `[OPEN]` | Internal audit claim in the paper; artifact not yet attached. | PL-024-4. |
| AF-11 | Kaggle Clause 1 is refuted: Pareto-complete enumeration finds 233 in-bound missing truth tables, 213 shift-realizable. | `[OPEN]` | Internal audit claim in the paper; artifact not yet attached. | PL-024-4. |
| AF-12 | Query determinacy is not correctness. | `[INTERPRETIVE]` | Operational interpretation of determinate-but-wrong failure mode. | Keep examples attached if promoted. |
| AF-13 | The firewall blocks self-authorization in practice. | `[INTERPRETIVE]` | Derived from zero authority promotion in audited Kaggle conditions; artifact-dependent. | Keep scoped to demonstrated cases. |
| AF-14 | Autonomous AI verification pipelines need structural separation, not only policy. | `[INTERPRETIVE]` | Implication drawn from the theorem and failure mode. | Avoid broad safety claims. |

Standard Background and Citations
---------------------------------

| ID | Claim | Tag | Citation status |
|---|---|---|---|
| AF-15 | Proof-carrying code is a nearest neighbor for machine-checkable evidence. | `[STANDARD + citation]` | Necula 1997. |
| AF-16 | Certified compilation is a nearest neighbor for semantic preservation proofs. | `[STANDARD + citation]` | CompCert, CakeML. |
| AF-17 | Byzantine fault tolerance is a nearest neighbor for distributed trust under faulty participants. | `[STANDARD + citation]` | Lamport 1982; Castro and Liskov 1999. |
| AF-18 | Self-verification limits are a nearest neighbor for verifier bootstrapping. | `[STANDARD + citation]` | Godel/Lob; tiling agents / Vingean reflection references. |
| AF-19 | AI alignment verification proposals are a nearest neighbor for delegated/amplified checking. | `[STANDARD + citation]` | Christiano et al. 2018; Irving et al. 2018. |

Definition Audit
----------------

These are definitions, not theorem claims:

| Item | Location | Note |
|---|---|---|
| Five primitives: Difference, Repair, Quotient, Closure, Authority | Paper 027, Definition 2.1 | Definitions imported from the tower vocabulary. Repair quotient $Q^1 = C^1 / \operatorname{im} d^0$ distinguished from first cohomology $H^1 = \ker d^1 / \operatorname{im} d^0$. |
| Authority Sigma-record and seven guards | Paper 024, Definition 2.2 | A well-formed record definition; realization soundness remains C4-scoped. |
| `IsAuth` | Paper 024, Section 3.1 | Predicate defining membership in the authority summand. |
| `residualTerminal` | Paper 024, Section 3.1 | Function mapping residual outcomes into the residual summand. |
| `authority_only_via_evidence` | Paper 024, Section 3.4 | Lean-proven record unpacking; useful but not independently load-bearing. |

Proof Ledger Cross-References
-----------------------------

| Proof ID | Needed for |
|---|---|
| PL-024-1 | **Typed component bridge relating diagnostic cochain complex to authority route.** Mechanized in [ResidualNonCreation](lean4/ResidualNonCreation.lean) (`bridge_mutual_exclusion`, `bridge_diagnostic_carries_no_authority`, `obstruction_cannot_pass_truthful_guards`, `cochain_bridge_obstruction_disjoint`, `cochain_bridge_obstruction_not_auth_s`). |
| PL-024-2 | Four-authority-type federation through a single Section II.2 Authority Sigma-gate. |
| PL-024-3 | MAJOR-3 lossy chi coherence and naturality. |
| PL-024-4 | Public reproducibility artifacts for Kaggle CC1 claims. |
| PL-024-5 | C4 replay-checker kernel audit contract. |
| PL-024-6 | **Non-vacuous Descent Authority Lane lane.** Replace `TerminalizerEvidence` (freely inhabited `String × String × Bool`) with a terminalizer-evidence type whose inhabitation is itself gated by verified replay/descent, so that `no_formal_to_authority_when_no_terminalizer` stops being vacuously true. Applies equally to `VerifiedTerminalizerEvidence`, whose `Prop`-valued fields are inhabitable by `True`. (AF-03) |
| PL-024-7 | **Mechanize `IsAuth_S`'s seven guards and guard factorization theorem.** [RESOLVED / MECHANIZED in [ResidualNonCreation](lean4/ResidualNonCreation.lean)]. |
| PL-024-8 | **`SpecificationIdentity`, `DetectorAdequacy`, `EvidenceCeiling`** for authority-bearing use. Detector adequacy must name protected distinctions, adversarial cases, and blind spots; §4 shows replayability alone does not supply it. (AF-22) |
| PL-024-9 | **Re-anchor canonical citations** from the superseded archived spine (`.omega_engine_official_archive/canonical_omega_math_spine.md`) to encyclopedia entries, per CLAUDE.md's canonical-source ruling. |

## Named regression entry points

These checks exercise the bundled finite models; they do not close the ledger's OPEN or external obligations.

- `code/tests/test_authority_firewall.py::test_pointwise_separation_theorem`
- `code/tests/test_authority_firewall.py::test_seven_guards_predicate`
- `code/tests/test_authority_firewall.py::test_auth_evidence_validation_and_unreplayable_rejection`
