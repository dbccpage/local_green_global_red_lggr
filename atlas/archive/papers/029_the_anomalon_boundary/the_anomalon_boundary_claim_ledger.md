000c — The Anomalon Boundary — Claim Ledger
===========================================

**Paper Key:** `001_finite_obstruction_calculus/029_the_anomalon_boundary`  
**Retired Paper Identity:** `FOC-002`  <!-- Retired 2026-08-18. Stamped from lean_identity_map.yaml, which describes the pre-rename tree, and restamped to the Paper Key above. Kept so an old citation to this code meets an explanation rather than nothing. -->

Per-paper claim ledger (Part B/C of `paper_hygiene_standard.md`). Companion to
`the_anomalon_boundary_monograph.md`.
Prepared edition: 2.1.1, 2026-10-23. Earlier review judgments remain historical; current replay checks the bundled finite statements only.

Part B — Typed Claims
---------------------

| # | Claim (where) | Type | Support / note |
|---|---|---|---|
| C1 | `Real_0 = Primitive Difference ⊔ Structure` is the root boundary, a typed coproduct of two independently posited channels (§0, §2.1). | `[DEFINITION]` | `OmegaCosmology.Ontology.Real0` in [OntologyBasic](lean4/OntologyBasic.lean). `Ontology.Anomalon.Real0Strat` is not in this deposit |
| C2 | NoAuthorityWithoutDescent: `HasAuthority` implies `DescendsToReal0` (§6). | `[POLICY RULE]` | `OmegaCosmology.Ontology.no_authority_without_descent` is the first conjunct of the definition of `HasAuthority`. It is not an executed certificate check. The Python suite does not evaluate `ClaimPacket` |
| C3 | "Structure" stratifies into carrier-Structure and residual-Structure (§2.1). | `[DEFINITION]` + `[NEGATIVE BOUNDARY]` | The prose distinction is in §2.1. `Ontology.Anomalon` (`CarrierStructure`, `PrimitiveDifferenceOver`, `ResidualStructure`, `DescentLadder`) is not in this deposit |
| C4 | Represented difference is carrier-typed (§2.1, §2.2, §9). | `[NEGATIVE BOUNDARY]` | `Ontology.Anomalon.PrimitiveDifferenceOver` and `FOC.RedTeamDischarge.carrierOfDifference` are not in this deposit |
| C5 | The boundary mints no authority: `Q¹ ≠ 0 ⇏ Auth`, channel-membership `⇏ Auth` (§2.1, §10). | `[NEGATIVE BOUNDARY]` | `Ontology.Anomalon.channel_membership_is_not_authority` is not in this deposit |
| C6 | Red-team Tests 3 and 4 are discharged carrier-first (§9). | `[NEGATIVE BOUNDARY]` | `FOC.RedTeamDischarge` is not in this deposit. The difference-first route stays OPEN (C7) |
| C7 | Working hypothesis: "Structure is residual from failed, stabilized, or transformed obstruction removal" — equivalently, Primitive Difference is ontologically prior (§9). | `[CONJECTURE / OPEN]` | PL-000c-1. Explicitly not promoted to a theorem; must be earned carrier-first. |
| C8 | Compact axiom set, Axioms 0–4 (§3); carried as explicit Lean data, not kernel axioms; quantifiers restricted to ValidatedClaimPacket with exhibited default inhabitant. | `[DEFINITION]` | `OmegaCosmology.Ontology.AnomalonAxiomSet` and `defaultAnomalonAxioms` in [OntologyBasic](lean4/OntologyBasic.lean). The census reports no axiom dependencies for that definition |
| C9 | Derived vocabulary (time, space, object, identity, truth, meaning, …) of §4 are audit hooks, not derivations. | `[DEFINITION]` | Paper §4 explicitly states they are audit hooks, not licenses. |
| C10 | Terminal statuses (certified/repaired/lifted/stabilized/refused/noRule/budgetUnknown); positive statuses authority-bearing only when descent is witnessed (§5). | `[DEFINITION]` | `OmegaCosmology.Ontology.TerminalStatus` in [OntologyBasic](lean4/OntologyBasic.lean) |
| C11 | Intelligence / AGI / ASI definitions (§8); the potato descent example. | `[INTERPRETIVE]` + `[WORKED EXAMPLE]` | Reading laid over the math; the potato example is the worked instance. |
| C12 | Finite descent is an access discipline, not root ontology (§7). | `[INTERPRETIVE / SCOPE FENCE]` | Consistent with the corpus's finite-window doctrine. |
| C13 | Carrier is not yet root/fundamental (§2.2). | `[NEGATIVE BOUNDARY]` | `Ontology.Anomalon.CarrierOriginStatus` and the cited origin lemmas are not in this deposit |
| C14 | Functional and binary addressability collapse into a carrier skeleton; unary markability remains open (§2.3). | `[NEGATIVE BOUNDARY]` + `[OPEN]` | `Ontology.AddressabilityThreshold` is not in this deposit. PL-SPK-COSMO-003-4 stays open |
| C15 | A boundary continuation is refusal, lift request, or restart; a lift is authorized only for a positive metric; the boundary flag does not promote to authority (§2.4). | `[PROVED]` + `[SCOPE FENCE]` | Lean `request_refusal`, `request_lift`, `request_restart`, `authorize_positive`, `authorize_zero`, `anomalon_does_not_promote`. Python `AnomalonBoundary.request_continuation`, `authorize_lift`, and `assert_no_authority_promotion` in `test_anomalon_boundary.py`. `Ontology.Anomalon.AnomalonSeed` is not in this deposit. A preservation identity beyond the sign of the metric stays open |
| C16 | Ten Boolean roles are jointly complete exactly when each role flag is true (§2.5). | `[PROVED]` + `[SCOPE FENCE]` | Lean `full_roles_complete`, `broken_roles_incomplete`. Python `MinimalKnowableSystem.check_completeness` in `test_minimal_knowable_system_completeness`. This is not a theorem of metaphysical necessity. The `no_*_blocks_*` names are not in this deposit. PL-000c-9 stays open |
| C17 | On the declared flags, exact-and-closed vanishes, unclosed is active, and closed non-exact survives. On the integer cycle, `d1 = 0` composes to zero, `(-2,1,1)` is `d0(2,0,1)`, and `(1,1,1)` is closed and not a coboundary. On the filled triangle, `d1 d0 = 0` and `d1(1,0,0) = 1` (§2.6). | `[PROVED]` | Lean `exact_closed_vanishes`, `unclosed_is_active`, `closed_nonexact_survives`, `c3_zero_coboundary`, `c3_exact_witness`, `c3_cycle_closed`, `c3_cycle_not_exact`, `filled_triangle_comp`, `filled_triangle_curvature`, `bad_square_not_complex`. Python `CochainDefect.classify` and `CochainComplex.analyze_defect` in `test_defect_classification_trichotomy` and `test_cochain_complex_explicit_matrix_computation`. `Ontology.SurvivingPrimitiveDifference` is not in this deposit. This is not a general theorem that `H¹ = 0`. PL-000c-11 stays open |

Part C — Support Ledger (upgrade engine)
----------------------------------------

Candidate results that would upgrade a conditional/conjecture:

1. **SL-1 (would upgrade C7 toward [PROVEN] or [REFUTED]).** *Statement:* every Structure
   in the corpus's instantiated domains is exhibited as residual-Structure of some
   prior primitive difference (no carrier-Structure that is not itself the residual of
   an earlier difference). *Strengthens:* removes the OPEN tag on the §9 hypothesis /
   the PD-priority reading. *Difficulty:* looks hard — its closing edge is red-team
   Test 3, currently resolved only carrier-first; a counterexample hunt (a carrier
   that is demonstrably not a residual) should run first. *Checkable:* Lean + prose.

2. **SL-2 (would close the dual-`Real₀` gap, hardening C1/C3).** *Statement:* a
   refinement map `Real0Strat → Real0` exhibiting `carrierStructure` and
   `residualStructure` as the `Structure` channel and `primitiveDifference` as the
   `PrimitiveDifference` channel, with the canonical descent lemmas preserved.
   *Strengthens:* makes the stratified and canonical roots provably one object.
   *Difficulty:* looks standard. *Checkable:* Lean. (PL-000c-3.)

3. **SL-3 (historical note, 2026-06-19; not a build of this deposit).** An earlier
   draft recorded that `OmegaCosmology` would import the FOC layer and
   `Ontology.Anomalon`. Those modules are not in this deposit, and
   `lake build OmegaCosmology` is not a target here. (PL-000c-4 stays a note, not a
   theorem of this package.)

4. **SL-4 (new carrier-origin audit).** Audit whether Support, Boundary, Address,
   Orientation, Comparison, Multiplicity, Persistence, Witnessability, Zero/nonzero,
   Inside/outside, Mark/trace, and Repeatability derive from Primitive Difference +
   Structure, must be named candidate primitives, or remain unknown Matryoshka layers.
   *Strengthens:* C13 and the §2.2 carrier-origin boundary. *Checkable:* prose +
   Lean status ledger (`PreCarrierAuditQuestion`).

5. **SL-5 (new unary/non-binary markability audit).** Test whether `UnaryAddressability` or any modal operator that does not expose an `Address → Mark → Prop` relation can support represented difference without reconstructing a carrier skeleton. *Strengthens:* C14 and §2.3. *Checkable:* Lean + prose. (PL-SPK-COSMO-003-4.)
6. **SL-6 (new Anomalon lift-preservation audit).** Specify the preservation witness required before a terminal residual can license an actual lift rather than only a lift request. *Strengthens:* C15 and §2.4. *Checkable:* Lean + prose. (PL-000c-7.)
7. **SL-7 (new MKS translation audit).** Exhibit equivalent translations into `MinimalKnowableSystem` for concrete Omega packets/domains, or identify which role fails. *Strengthens:* C16 and §2.5. *Checkable:* Lean + Rust/prose fixtures. (PL-000c-9.)
8. **SL-8 (new quantitative survivor bridge).** Connect `SurvivesLocalGlobalDescent` to the concrete finite diagnostics `Φ₁ > 0` and `Γ₂ = 0` in the active finite-window certificate layer. *Strengthens:* C17 and §2.6. *Checkable:* Lean + finite certificate fixtures. (PL-000c-11.)

Lineage
-------

- v0.1 (June 2026) initial pre-print → v0.1.1 (2026-06-19) hygiene pass → v0.1.2 (2026-06-19) carrier-origin boundary pass → v0.1.3 (2026-06-20) addressability threshold + Anomalon restart-boundary pass → v0.1.4 (2026-06-20) Minimal Knowable System pass → v0.1.5 (2026-06-20) Surviving Primitive Difference pass. Header
  `status` is canonical; the §Changelog records the lineage.

<!-- claim-id-body-only-sync:begin -->

Body-only ID sync (packaging)
-----------------------------

**AuthorityEffect:** None. Packaging hygiene; no OPEN→PROVED.

| ID | Claim | Type | Status |
|---|---|---|---|
| COSMO-002 | Body claim-shaped ID registered for bijection packaging only; OPEN; not upgraded | OPEN | packaging |

<!-- claim-id-body-only-sync:end -->

## Named regression entry points

These checks exercise the bundled finite models; they do not close the ledger's OPEN or external obligations.

- `code/tests/test_anomalon_boundary.py::test_minimal_knowable_system_completeness`
- `code/tests/test_anomalon_boundary.py::test_cochain_complex_explicit_matrix_computation`
