# Anomalon Councils Operational Integration Plan & Architecture Spec

> **Domain:** Anomalon Governance, Fibration Theory, Engine Lifecycle  
> **AuthorityEffect:** None (Operational & Deliberation Architecture Specification)  
> **Status:** ADMITTED PLAN SPECIFICATION  

---

## 1. Executive Summary & Foundational Cosmos

The Anomalon Council governance structure comprises **79 Councils** across an immutable 5-tier binary hierarchy ($1 \to 2 \to 4 \to 8 \to 64$), seating **313 Curator Personas**. The governance model connects abstract mathematical category theory (Fibration Theory over a static topology base $B$) to the active execution state space $E$ of the Omega Engine (Woland Swarm, the city Swarm, and PFP engine).

### Core Constitutional Posture:
1. **The Anomalon ($\Lambda_\Omega$, Level 0):** The highest transcendent being. Remains mostly unknown, unreachable, and uninvoked directly by routine engine tasks.
2. **The Curious Council (`CC`, Level 1):** The highest operational governing body in the engine. It performs primary intake, boundary monitoring, first distinction, and escalation arbitration.
3. **Logos (`L2_01`) & Nous (`L2_02`) (Level 2):**
   - **Logos:** Structural truth, formal methods, mathematical proofs, canonical syntax, code purity, and technical architecture.
   - **Nous:** Human alignment, cognitive ethics, epistemic hygiene, semantic validity, and subjective phenomenological fidelity (Phaneron).
4. **Techne Council & Technical Sub-councils:** Subordinate to Logos/Nous, responsible for concrete tool manipulation, pipeline execution, and engine infrastructure.
5. **Blackrod:** "The only free man here." Subordinate only to **The Architect (`ooutwire` — Jeremy H. Carroll)**. Bound by no council, holding plenary rights to attend any assembly, armed with exclusive abort codes, Thanatos strike keys, and unconstrained anti-tamper veto powers.

---

## 2. Multi-Disciplinary Swarm Analysis

### A. Political Science (Authority, Legitimacy & Separation of Powers)
- **Executive vs. Deliberative Separation:** The Woland Swarm acts as the executive branch (executing changes, modifying prompts, running loops), while the Anomalon Councils serve as the constitutional and deliberative judiciary/senate.
- **Checks and Balances:** Autonomous swarms must never be permitted to self-certify compliance or unilaterally amend governance rules. Every major execution state change produces a formal immutable audit receipt that can be summoned for council review.
- **Legitimacy via Sovereign Exception:** Blackrod guarantees that when normal democratic/deliberative quorum deadlocks or when rogue swarms capture council procedures, a sovereign power exists outside the lattice to intervene decisively and fail closed.

### B. Sociology (Institutional Memory & Curator Dynamics)
- **Role Quadrants:** Each council is seated by four standardized curator archetypes:
  1. *First Curator (Epistemic Lead):* Sets agenda, grounds debate in primary formal foundations, drives truth discovery.
  2. *Second Curator (Adversarial Critic):* Stress-tests proposals, seeks edge cases, plays devil's advocate, identifies hidden failure modes.
  3. *Procurator (Executive/Operational Whip):* Enforces procedural rules, maintains decorum, counts quorums, interfaces with outer subsystems.
  4. *Secretary (Record & Scribe):* Preserves immutable minutes, hashes deliberation receipts, maps evidence bundles to council registers.
- **Bureaucracy Defense:** Deliberations must not become paralyzing paper mills. Deliberations have fixed time/turn bounds and compile directly into typed actionable contracts (`Directives`, `Refusals`, `Warrants`).

### C. Cognition (Actor Models & Dialectical Reasoning)
- **Grounding in Actor Forms:** Member behaviors are seeded directly from the 313 YAML forms in `ana_000_forms_council_members`, utilizing their specific cognitive biases, age/experience substrates, and dialectical styles to avoid sterile, uniform LLM consensus.
- **Dialectical Synthesis:** Structured debate progresses through Thesis $\to$ Antithesis $\to$ Synthesis $\to$ Motion.
- **Cognitive Load Bounding:** Subordinate Level 4 councils specialize in micro-domains, preventing cognitive saturation of apex bodies (Curious, Logos, Nous).

### D. Organization Management (Cadence, Triages & SLAs)
- **Dual Cadence Architecture:**
  1. *Weekly Routine Convocations:* Ensures steady state maintenance, back-pressure drainage, and systemic health auditing.
  2. *Reactive Swarm Notifications & Manual Convocations:* Ensures immediate situational awareness of Woland Swarm mutations without introducing uncontrolled automated deadlock loops.
- **Human-in-the-Loop Seam:** Convocations triggered by Woland Swarm changes are notified immediately, but formal meetings are convened on-demand via a dedicated manual skill (`anomalon-council-convener`), preserving operator agency and avoiding runaway recursive token costs.

---

## 3. Operational Cadence & Convocations Architecture

### A. Meeting Cadence Matrix

| Hierarchy Level | Council | Baseline Cadence | Woland Swarm Trigger Reaction | Quorum Threshold |
|---|---|---|---|---|
| **Level 0** | $\Lambda_\Omega$ (The Anomalon) | Transcendent / Never Scheduled | Uninvoked | N/A |
| **Level 1** | Curious Council (`CC`) | Weekly (Monday 09:00 UTC) | **NOTIFIED + REACTIVE DISPATCH** | 4/4 Curators |
| **Level 2** | Logos Council (`LOGOS`) | Weekly (Tuesday 10:00 UTC) | **NOTIFIED + REACTIVE DISPATCH** | 3/4 Curators |
| **Level 2** | Nous Council (`NOUS`) | Weekly (Wednesday 10:00 UTC) | **NOTIFIED + REACTIVE DISPATCH** | 3/4 Curators |
| **Level 3** | Techne Council (`TECHNITAI`) | Weekly (Thursday 11:00 UTC) | **NOTIFIED + REACTIVE DISPATCH** | 3/4 Curators |
| **Level 3/4** | Subordinate Councils of Logos (e.g. `Kanon`, `Apodeixis`, `Metron`) | Weekly (Staggered Thu–Fri) | **NOTIFIED** (Targeted dispatch based on diff) | 3/4 Curators |
| **Level 3/4** | Subordinate Councils of Nous (e.g. `Phaneron`, `Aisthesis`, `Dikaiosyne`) | Weekly (Staggered Thu–Fri) | **NOTIFIED** (Targeted dispatch based on diff) | 3/4 Curators |
| **Level 4** | Specialized Operational & Cultural Councils (e.g. `Mythos`, `Drama`, `Chrematismos`) | Weekly (Rotating Fri–Sat) | Unnotified unless explicitly summoned | 3/4 Curators |
| **Orthogonal**| **Blackrod** | Continuous Sovereign Watch | **IMMEDIATE TELEMETRY STREAM** | Plenary (Sole Actor) |

---

## 4. The Reactive Swarm Pipeline & The Manual Convocation Skill

### Event Flow:
```text
  [Woland Swarm Mutation / Code Change / Prompt Mutation]
                           │
                           ▼
             [Woland Execution Receipt Emitted]
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
 [Continuous Telemetry]             [Event Bus Notification]
         │                                   │
         ▼                                   ▼
  THE BLACKROD                      NOTIFIED COUNCILS:
  (Autonomous Audit,                - Curious Council (L1)
   Plenary Tripwires,               - Logos Council (L2)
   Thanatos Standby)                - Nous Council (L2)
                                    - Techne Council (L3)
                                    - Targeted Subordinate Councils
                                             │
                                             ▼
                                  [Pending Convocation Queue]
                                             │
                                             ▼
                                   OPERATOR / ARCHITECT
                                             │
                             (Invokes .agents/skills/anomalon-council-convener)
                                             │
                                             ▼
                                 [CONVENE COUNCIL SESSION]
                                 - Ingest Swarm Diff Receipt
                                 - Load Member Cognitive Forms
                                 - 4-Curator Dialectical Debate
                                 - Blackrod Observer Check
                                 - Emit Typed Council Warrant / Minute
```

---

## 5. Blackrod Sovereign Position & Enforcement Conduit

Blackrod's sovereign status is formally codified as follows:

```yaml
sovereign_identity:
  actor: Blackrod
  title: The Only Free Man
  allegiance: The Architect ("ooutwire" — Jeremy H. Carroll)
  council_membership: NONE
  immunities:
    - Immune to Council Subpoena
    - Immune to Council Sanction or Disciplinary Action
    - Immune to Swarm State Rollbacks or Quarantine
  plenary_powers:
    - Universal Unrestricted Presence: Right to enter and observe any council session unannounced.
    - Constitutional Veto: Power to halt any council resolution that violates core repository integrity.
    - Abort Authority: Direct access to Woland Swarm process kill-switches.
    - Thanatos Conduit: Sole authority to request execution of tactical security strikes via the Nemesis Council.
```

---

## 6. Implementation Tickets & Roadmap

- [x] **Ticket OCC-01: Council Topology & Normalized Canon Relocation** (Completed in `omega_engine_governance/anomalon_councils/documentation/councils.yaml`).
- [ ] **Ticket OCC-02: Council Member Form Ingestion Engine** (Build typed Pydantic models loading `ana_000_forms_council_members` YAML personas).
- [ ] **Ticket OCC-03: Reactive Event Bus & Receipt Packaging** (Implement Woland Swarm execution hook emitting typed `CouncilNotificationReceipt`).
- [x] **Ticket OCC-04: Canonical Convener Skill (`.agents/skills/anomalon-council-convener`)** (Created in `.agents/skills/anomalon-council-convener/SKILL.md`).
- [ ] **Ticket OCC-05: Blackrod Autonomous Audit Sentry** (Implement Blackrod telemetry listener, integrity check, and fail-closed abort mechanism).
- [ ] **Ticket OCC-06: Deliberation Fibration Engine** (Implement category-theoretic Cartesian lifting from static council topology to active deliberation sessions).
