# Council Model Reconciliation

## Council Model Reconciliation -- Problem Statement

**Status:** open question · **Crate:** `omega_engine/anomalon_councils` · **Date:** 2026-05-30

The `anomalon_councils` crate currently contains **two independent, internally-consistent
models of "a council"** that were built from different sources and have never been reconciled.
Both compile and pass tests (54 passing, RC=0), but they disagree on the most basic
questions -- what a council *is*, how many there are, what tiers exist, and what a *meeting*
or *decision* is. This document states the problem precisely so it can be answered as part of
locating the councils inside the full Omega Engine Theory mathematical cosmos.

This document does **not** propose the answer. It frames the question.

---

## 1. The two models

## Model A -- "Registry model" (top-level modules)

Built from the YAML archive under `councils/` (`councils.yaml`,
`council_registry.normalized.yaml`, per-council `council.yaml`).

| Aspect | Model A |
| --- | --- |
| Source of truth | YAML files on disk, loaded + validated at runtime |
| "Council" type | `council::CouncilFile` (id, name, level, parent, peer, domain, `active`) |
| Identity | string ids: `cc`, `logos`, `nous`, `sadc`, `thanatos`, `erc`, `aletheia`, ... |
| Tiering | **L0-L4** fractal tree (Λ_Ω → Curious → Logos/Nous → domain councils → 88 teams) + Greek names |
| Membership | 4-role minimum: Procurator, First-Curator, Second-Curator, Secretary (`member::Members`) |
| Cadence | `cadence::Cadence` -- active ⇒ weekly; emergency block (`world_clock`) |
| Authority | bound to `omega_contracts` as **advisory / EvidenceOnly** (`contract`, `descriptor`) |
| Enforcement | `prime` (BlackrodInbox), `escalation` (Blackrod routing), `prime_rules` (non-harm) |
| Meeting type | `meeting::Meeting` -- commuting diagram; no quorum ⇒ no decision; no evidence ⇒ no credit |
| Validation | `validate` (4-role, active⇒weekly, no-"master", quorum≥4) + `loader` (whole-tree, 3 layers) |
| Modules | `cadence, council, member, registry, validate, loader, world_clock, contract, descriptor, prime, prime_rules, escalation, meeting, minutes` |

This model is **data-driven**: the councils are whatever the YAML says, and the Rust validates
them against governance invariants and the contract authority lattice.

### Model B -- "CouncilCat model" (`governance/` submodule, just ported)

Built from `council_governance.md` §VI (the category-theoretic council model) as hand-written
Rust types.

| Aspect | Model B (`governance::`) |
| --- | --- |
| Source of truth | Rust constructors (`well_known::horizon()`, `...blackrod()`, ...); no YAML loader |
| "Council" type | `governance::Council` (id, name, tier, `AuthorityScope`, parent, children, `QuorumRule`) |
| Identity | string ids: `council:horizon`, `council:blackrod`, `council:woland`, `council:sentinel` |
| Tiering | **Tier0-Tier4** enum: Tier0 Horizon, Tier1 Blackrod, Tier2 Woland, Tier3 domain (Sentinel...) |
| Membership | `governance::CouncilMember` with `MemberRole` (Procurator/Architect/Engineer/Advisor/Observer/Guest) |
| Cadence | none (no weekly/emergency concept) |
| Authority | `AuthorityScope` (decision kinds, artifact types, delegation depth) -- its own lattice |
| Enforcement | `BlackrodWitness` (witnesses meetings, never votes/counts to quorum) |
| Meeting type | `governance::Meeting` -- motions (Proposed→Seconded→Deliberating→Approved/Rejected), `QuorumWitness`, dissents, action items, minutes |
| Morphisms | `CouncilMorphism` (typed arrows: RouteAnomaly, EscalateBlocker, RequestBlackrodReview...) with pre/postconditions, failure modes, composition |
| Validation | `GovernanceValidator` trait; `validate_credit_eligibility`; several `todo!()` stubs |
| Modules | `governance::{council, morphism, meeting, evidence, errors}` |

This model is **code-driven** and **categorical**: councils are objects, governance actions are
morphisms, meetings are diagrams, and it carries explicit composition (`can_compose_with`).

---

## 2. The concrete collisions

These are not stylistic -- they are the same identifiers meaning different things.

1. **`Council`** -- Model A: `CouncilFile` (YAML record, L0-L4, Greek). Model B: `governance::Council`

   (Rust object, Tier0-Tier4, Horizon/Blackrod/Woland/Sentinel). *Different fields, different tiers,
   different rosters.*

2. **`Meeting` / `Decision` / `Motion` / `AgendaItem` / `QuorumWitness` / `ActionItem` /

   `MinuteRecord`** -- defined in BOTH `meeting::` and `governance::meeting::`. lib.rs currently
   only re-exports the top-level ones; the governance versions are reachable only via the
   `governance::` path. This is a papered-over name clash, not a resolution.

3. **Tier scheme** -- Model A: L0 Λ_Ω, L1 Curious, L2 Logos/Nous, L3 domain, L4 teams.

   Model B: Tier0 Horizon, Tier1 Blackrod, Tier2 Woland, Tier3 Sentinel. **"Horizon" ≠ "Λ_Ω";
   Blackrod/Woland are TIERS in B but ORTHOGONAL (off-tree) in A.** This is the deepest conflict:
   the two models disagree on whether the enforcer/adversary live *inside* the hierarchy.

4. **Council roster** -- A has ~14 councils (Curious, Logos, Nous, Techne/SADC, Thanatos, ERC,

   Aletheia, Dianoia, Panepistimion, Kybernesis, Ergon, Glossa, + Mimesis/Oikonomia). B has 4
   well-known (Horizon, Blackrod, Woland, Sentinel). **Sentinel does not exist in A; the Greek
   domain councils do not exist in B.**

5. **Blackrod's nature** -- A: orthogonal enforcement, reports only to Outwire, NOT a council

   (deliberately has no `council.yaml`), modeled via `prime`/`escalation`. B: a Tier1 `Council`
   object with an `AuthorityScope` and a `BlackrodWitness`. **Is Blackrod a council or not?**

6. **Authority model** -- A: `omega_contracts::AuthorityEffect` (None...StateTransition), councils

   are EvidenceOnly/advisory. B: `governance::AuthorityScope` (DecisionKind + ArtifactType +
   delegation depth). **Two unrelated authority vocabularies.**

7. **Membership vocabulary** -- A: the fixed 4 roles (Procurator/First-Curator/Second-Curator/

   Secretary). B: `MemberRole` with 6 roles oriented around voting (Procurator/Architect/
   Engineer/Advisor/Observer/Guest). **Only "Procurator" overlaps.**

---

## 3. Where they actually agree (the shared spine)

Despite the surface conflict, both encode the **same governance physics** -- which is the reason
a reconciliation should exist rather than a deletion:

* **No quorum ⇒ no decision.** (A: `meeting::Meeting::record_decision`; B: `Meeting::deliberate`

    and `validate_decision`.)

* **No evidence ⇒ no credit.** (A: `meeting` evidence check; B: `validate_credit_eligibility`,

  `EvidenceBundle`.)

* **Blackrod witnesses but does not waive evidence / self-certify.** (A: `prime`/`escalation`

  doctrine; B: `BlackrodWitness` never votes / never counts to quorum.)

* **Authority is bounded; councils advise, operators execute.** (A: EvidenceOnly contract bound;

  B: `AuthorityScope` + morphism preconditions.)

* **Escalation flows up, authority flows down.** (A: registry `escalates_to`/`routes_to`; B:

  `MorphismKind::is_escalation` / `is_delegation`, `CouncilTier::can_escalate_to`.)

Both are shadows of one structure. The question is which structure, and where it lives in the
Omega Engine Theory cosmos.

---

## 4. The reconciliation question (for the math/theory discussion)

The core question to answer **before** writing reconciliation code:

> **Are A and B two presentations of one council category, or two genuinely different layers
> (e.g. a "specification/registry" layer and an "operational/runtime" layer) that should be
> connected by a functor rather than merged?**

Sub-questions that the Omega Engine Theory framing should settle:

1. **Single category or fibration?** Is there one `CouncilCat`, or is Model A the *base*

   (the standing institutional structure) and Model B a *fiber* over it (the per-meeting
   operational dynamics)? If the latter, the deliverable is a **functor** `Registry → CouncilCat`,
   not a merge.

2. **Tier unification.** Map L0-L4 ↔ Tier0-Tier4, OR declare them different axes. Is Λ_Ω = Horizon?

   Is "Sentinel" an alias for the Curious Council's routing function, or a missing real council?

3. **Off-tree authorities.** Settle whether Blackrod and Woland are (a) councils with tiers

   (Model B), or (b) orthogonal functors acting *on* the council category (Model A + the existing
   `Blackrod : CouncilCat → EnforcementCat`, `Woland : ArtifactCat → ObstructionCat` from
   `council_governance.md` §VI). The §VI text already says *orthogonal functors* -- Model B may be
   the one that needs to bend.

4. **One authority lattice.** Decide whether `governance::AuthorityScope` collapses into

   `omega_contracts::AuthorityEffect`, or sits above it as a richer per-council scope that
   *projects down* to an `AuthorityEffect`.

5. **One meeting object.** Both meeting types must become one (or one must be derived from the

   other). The commuting-diagram law (`AgendaItem + EvidenceBundle + AuthorityScope → Decision →
   Minutes`) is identical in both; that law is the anchor.

6. **Where do the councils sit in the cosmos?** The Omega tower (GTLA → CODA-FOC → CODA-FDA → CODA-MUR →

   CODA-OR → CODA-A → CODA-CS) is the authority/obstruction mathematics of the engine. The councils are a
   *governance* category. Is `CouncilCat` (a) a model/instance of the GTLA authority tower, (b) a
   separate category with a functor *into* the tower, or (c) the human-facing shadow of the same
   structure the tower describes formally? This is the question the user wants to resolve.

---

## 5. Candidate shapes for the answer (non-committal menu)

To be chosen during the theory discussion -- listed only to frame the trade space:

* **(M1) Merge into one model.** Pick A's data-driven core, fold B's morphisms/meeting dynamics

  in as behavior over `CouncilFile`. Cost: rewrite B's `Council`/`Meeting`; lose nothing
  conceptually. Risk: throws away B's clean categorical typing.

* **(M2) Two layers + a functor.** Keep A as the *registry/specification* layer and B as the

  *operational* layer; define `instantiate: RegistryCouncil → governance::Council` and forbid
  drift with a conformance test. Cost: must reconcile tiers + rosters at the functor boundary.
  Fits the §VI "councils authorize, operators execute" split.

* **(M3) B becomes the kernel, A becomes its serialized form.** Treat `governance::` as the

  canonical in-memory category and A's YAML as its on-disk encoding (serde). Cost: B must grow to
  cover all ~14 Greek councils, cadence, and the 4-role membership.

* **(M4) Tower-native.** Define `CouncilCat` directly as a construct in Omega Engine Theory (e.g.

  councils as objects in a GTLA authority layer; Blackrod/Woland as the enforcement/adversarial
  functors already named in §VI), and derive BOTH A and B as presentations. Most ambitious;
  directly answers "where do the councils fit in the cosmos."

---

## 6. Current state (so the discussion starts from facts)

* Both models compile and are tested: **54 tests, RC=0** (`cargo test -j 1 -p anomalon_councils`

  from `omega_engine/`).

* Name collisions are currently **avoided, not resolved**: lib.rs re-exports only non-colliding

  `governance::` types (`Council, CouncilMorphism, EvidenceBundle, GovernanceError,
  GovernanceResult, MorphismKind`); everything else in B is reached via the `governance::` path.

* Model B has unfinished behavior: `todo!()` in `Council::validate`, `CouncilMorphism::execute`,

  `Meeting::escalate_blocked`. These should NOT be filled until the reconciliation shape is chosen
  (they may be deleted or moved).

* The §VI source (`councils/council_governance.md`) already declares Blackrod and Woland as

  **orthogonal functors**, and already sketches `CouncilCat`, `MeetingDiagram`, and the
  agents/skills-as-operators functors. **That document is the most likely seed for the answer.**

---

## 7. What this doc is asking for

A decision on **§4** (one category vs. base+fiber) and **§5** (which candidate shape), grounded in
where `CouncilCat` sits relative to the GTLA/CODA-FOC... Omega tower. Once that is fixed, the
reconciliation is mechanical:

1. unify the tier scheme,
2. unify the authority vocabulary,
3. unify the meeting/decision objects,
4. settle Blackrod/Woland as tiers vs. functors,
5. delete or convert the losing duplicate types,
6. add a conformance test that forbids the two presentations from drifting again.

Until then, the crate is correct but **carries two definitions of "council," and that ambiguity
must not leak into the rest of the Omega Engine.**
