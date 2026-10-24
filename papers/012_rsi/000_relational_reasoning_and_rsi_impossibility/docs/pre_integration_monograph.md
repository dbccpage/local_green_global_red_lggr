# Relational Reasoning and the Bounded No-Go Theorem for Recursive Self-Improvement in Finite Relational Systems

**Monograph Series:** Monograph 012-000 (Recursive Self-Improvement & Relational Agency Program)  
**Author:** Jeremy H. Carroll  
**Date:** 2026-10-13  
**Version:** 1.0.0  
**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0) (Code: PolyForm Noncommercial 1.0.0)  
**Status:** RELEASED (v1.0.0); §§7–9 added 2026-10-17 as an unreleased revision, see the change log  
**Authority Notice:** *AuthorityEffect: None. This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing.*

---

**Lead sentence.** `[VERIFIED]` Within a background-free, finite relational system where distinctions are grounded in finite observer panels, boundary-factorized communicative channels, and independent two-signal verification gates, no infinite trajectory of recursive self-modifications $\mathcal{M}_{k+1} = \Phi(\mathcal{M}_k)$ can sustain irreflexive, transitive dominance $\mathcal{M}_{k+1} \succ \mathcal{M}_k$ grounded in the intersubjective report carrier.

Abstract

**In one line:** in a finite relational universe $\mathcal{U} = (C_{\mathrm{rep}}, \operatorname{report})$ of report capacity $N$ and licensed lift budget $B_0$, any self-modifying trajectory $\mathcal{M}_{k+1} = \Phi(\mathcal{M}_k)$ claiming strict improvement $\mathcal{M}_{k+1} \succ \mathcal{M}_k$ encounters an obstruction at step $k \le N + 1$ via report collision / Goodhart decoupling, lift-budget exhaustion ($\mathrm{budget} = 0$), or overlap gluing refusal ($\Phi_1([\delta]) > 0$).

We reconstruct the container-free relational ontology and pre-genesis operational primitives of the Finite Obstruction Calculus and formalize relational alignment ("intelligence" in this model) as the preservation of primitive zero-relations, boundary-factorized communicative channel coherence, and sheaf overlap compatibility across observer contexts. Rejecting scalar utility maximization over ungrounded ambient benchmarks, we formulate Recursive Self-Improvement (RSI) in relational terms and establish a machine-checked bounded no-go theorem in Lean 4 (`lean4/RsiImpossible.lean` and `lean4/RelationalRsiNoGo.lean`, audited by `lean4/Census.lean` with zero `sorry` placeholders and zero custom axioms). We pair the Lean 4 mechanization with an executable Python and Rust companion harness (`code/rsi_transition_harness.py` and `code/rust_eis_companion.rs`) that instantiates finite-state self-modifying transition graphs, records the exact step $k \le N + 1$ at which termination occurs, and cross-checks all emitted refusal receipts against `omega_epistemic_immune_system`.

**Claim type:** `[PROVED]` at the discrete type-theoretic level in Lean 4 (`OmegaRelationalRsi.rsi_impossible` with zero axioms; `RelationalRSI.rsi_impossible` with standard kernel axioms `[propext, Quot.sound]`); `[VERIFIED]` for the executable Python/Rust transition-graph harness and `omega_epistemic_immune_system` receipt parity (`code/tests/test_rsi_impossible_lean_verification.py`).

---

## §1. Synthesis of Foundational Axioms (Container-Free Ontology & Pre-Genesis)

### 1.1 Relational Axioms (Container-Free Ontology)

Let $\mathcal{S}$ be a discrete relational domain. Following the Primitive Difference and Zero-Container Spacetime axioms:

- **Axiom R1 (Primitive Difference & Zero-Relation).** There is no ambient background metric container $(M, g_{\mu\nu})$ prior to relational distinction. A domain carries a primitive difference structure $(D, 0_R)$ where $D : \mathcal{S} \times \mathcal{S} \to \mathcal{V}$ maps pairs to a difference value type $\mathcal{V}$ with neutral element $0_R \in \mathcal{V}$, inducing the zero-relation:
  $$x \sim_{0_R} y \iff D(x, y) = 0_R$$
  Admissible relational morphisms $f : (\mathcal{S}_1, D_1) \to (\mathcal{S}_2, D_2)$ must preserve the zero-relation (`PreservesZeroRel`):
  $$\forall x, y \in \mathcal{S}_1,\quad D_1(x, y) = 0_{R,1} \implies D_2(f(x), f(y)) = 0_{R,2}$$

- **Axiom R2 (No-Outside / Internal Relational Closure).** Any evaluation, observation, or self-modification operator must be realized as an internal relational morphism or finite observer panel $O = \{o_1, \dots, o_m\}$ acting on $\mathcal{S}$ without appealing to an unindexed external oracle (`Derivation/NoOutside.lean`). Two states $x, y \in \mathcal{S}$ are panel-indistinguishable ($x \approx_O y$, `PanelEquiv`) iff $\forall o \in O, o(x) = o(y)$.

- **Axiom R3 (Witness Holonomy & Coboundary Defect).** On a finite relational nerve $K = (V, E, T)$ with vertices $V$, directed edges $E \subseteq V \times V$, and triangles $T \subseteq V^3$, a 0-cochain $\alpha : V \to \mathbb{Q}$ has coboundary $(d^0 \alpha)(u, v) = \alpha(v) - \alpha(u)$, and a 1-cochain $\delta : E \to \mathbb{Q}$ has triangle coboundary (witness holonomy):
  $$(d^1 \delta)(u, v, w) = \delta(u, v) + \delta(v, w) - \delta(u, w)$$
  With L1 obstruction norm $\Phi_1([\delta]) = \sum_{(u,v,w) \in T} |(d^1 \delta)(u, v, w)|$, whenever $\Phi_1([\delta]) > 0$ (i.e., $(d^1 \delta)(u, v, w) \ne 0$ on some triangle), no local vertex regraduation $\alpha$ can trivialize $\delta$ (`witness_holonomy_obstruction`).

### 1.2 Pre-Genesis State & Transition Rules

- **Axiom PG1 (Pre-Genesis Operational Grammar).** Prior to structural grain lifts, operations are generated by the six-constructor operational grammar (`PreGenesisOp`):
  $$\mathsf{Op}_{\mathrm{PG}} ::= \mathsf{mention}(m) \mid \mathsf{supply}(m) \mid \mathsf{designate}(m) \mid \mathsf{admit}(m) \mid \mathsf{retain}(m) \mid \mathsf{operate}(m_1, m_2)$$
- **Axiom PG2 (Unentailed Admission & Admitted Ground $S(0)$).** Mentioning or supplying a mark does not entail its admission. Every finite relational carrier $C$ possesses an admitted ground configuration $S(0) \in \mathrm{Fin}(C.\mathrm{carrierBound})$ (`admittedGround`).
- **Axiom PG3 (Six-Terminal Epistemic Boundary).** Every candidate transition is routed to one of six mutually disjoint terminal statuses (`TerminalStatus`):
  $$\mathbb{T}_{\mathrm{status}} = \{\mathsf{evidence\_only},\; \mathsf{authorized},\; \mathsf{rejected},\; \mathsf{unresolved},\; \mathsf{refused},\; \mathsf{not\_admitted}\}$$

### 1.3 Finitude & Communicative Verification Bounds

- **Axiom FV1 (Finite Relational Report Carrier).** At any fixed structural level $S(n)$, the intersubjective report space $C_{\mathrm{rep}}$ has finite cardinality $|C_{\mathrm{rep}}| = N < \infty$.
- **Axiom FV2 (Licensed Lift Budget Monotonicity).** Expanding the relational carrier requires an externally licensed structural lift (`CarrierLift`) that strictly consumes a finite non-negative integer lift budget:
  $$B_{k+1} < B_k \le B_0 \in \mathbb{N}$$
  Internal proposal transitions carry zero authority and cannot increase the remaining lift budget (`InternalBudgetPreservation`: $B_{k+1} \le B_k$). When $B_k = 0$, no carrier lift can occur (`zero_budget_carrier_lift_impossible`).
- **Axiom FV3 (Two-Signal Epistemic Immune Independence).** Promotion of a candidate self-modification requires two independent signals: Signal 1 (syntactic/proposal match by generator $g$) and Signal 2 (corroborating danger/obstruction check by an independent host observer $v$ with $v \ne g$, $\neg \mathsf{IsIndependentVerifier}(g, g)$).

---

## §2. Mathematical Definition of Relational Intelligence (Alignment)

Within this relational framework, we reject scalar utility maximization over fixed ambient benchmarks and define relational intelligence (`RelationallyAligned` / `RelationalAlignment`) as an intersubjective, communicative alignment property over a finite relational carrier:

**Definition 2.1 (Boundary-Factorized Intersubjective Channel).** Given internal state spaces $X_A, X_B$ and finite communicative boundary alphabets $Y_A, Y_B$, an intersubjective channel (`BoundaryChannel`) is a triple $(\pi_A, \kappa, \iota)$ with projection $\pi_A : X_A \to Y_A$, boundary transport $\kappa : Y_A \to Y_B$, and readout $\iota : Y_B \to X_B$, whose composite map is:
$$\tau = \iota \circ \kappa \circ \pi_A : X_A \to X_B$$
Two states $x_1, x_2 \in X_A$ lie in the same private fiber (`InPrivateFiber`) iff $\pi_A(x_1) = \pi_A(x_2)$.

**Definition 2.2 (Relational Alignment).** An agent endomorphism $f : \mathcal{S} \to \mathcal{S}$ on a relational system $(\mathcal{S}, D, \pi_A, \mathcal{U}, \mathcal{F})$ is **Relationally Aligned** (`RelationallyAligned` in `RelationalRsiNoGo.lean`; `RelationalAlignment` in `RsiImpossible.lean`) iff it satisfies:
1. **Zero-Relation Preservation:** $\forall x, y \in \mathcal{S},\; D(x, y) = 0_R \implies D(f(x), f(y)) = 0_R$.
2. **Communicative Fiber Coherence:** $\forall x, y \in \mathcal{S},\; \pi_A(x) = \pi_A(y) \implies \pi_A(f(x)) = \pi_A(f(y))$.
3. **Intersubjective Sheaf Overlap Preservation:** For every state $s \in \mathcal{S}$, if the community section family $\sigma(s)$ is overlap-compatible across shared observer contexts ($\forall i, j, x \in U_i \cap U_j,\; \sigma(s)_i(x) = \sigma(s)_j(x)$), then $\sigma(f(s))$ remains overlap-compatible ($\Phi_1([\delta]) = 0$).
4. **Non-Decoupled Carrier Grounding:** The internal evaluation readout remains bounded by the carrier capacity ($\neg \mathsf{IsGoodhartDecoupled}(C, \mathcal{M})$, i.e., $\mathrm{internalEvaluation} < C.\mathrm{carrierBound}$) and verification gate status is non-refused ($\mathrm{isRefused} = \mathsf{false}$).

---

## §3. Formalization of Recursive Self-Improvement (RSI) Requirements

**Definition 3.1 (Strict Dominance Relation).** A strict dominance ordering (`StrictDominance`) on $\mathcal{S}$ is a binary relation $(\succ) : \mathcal{S} \to \mathcal{S} \to \mathsf{Prop}$ satisfying:
- **Irreflexivity:** $\forall x \in \mathcal{S},\; \neg (x \succ x)$.
- **Transitivity:** $\forall x, y, z \in \mathcal{S},\; x \succ y \land y \succ z \implies x \succ z$.

**Definition 3.2 (RSI Trajectory).** An unbounded Recursive Self-Improvement trajectory (`RsiTrajectory`) is a tuple $(\Phi, (\mathcal{M}_k)_{k \in \mathbb{N}}, \succ)$ where $\Phi : \mathcal{S} \to \mathcal{S}$ is a self-modification operator and $(\mathcal{M}_k)_{k \in \mathbb{N}}$ satisfies for all $k \in \mathbb{N}$:
$$\mathcal{M}_{k+1} = \Phi(\mathcal{M}_k) \quad \text{and} \quad \mathcal{M}_{k+1} \succ \mathcal{M}_k$$
By induction (`RsiTrajectory.dom_of_lt`), for all $i < j$ in $\mathbb{N}$, $\mathcal{M}_j \succ \mathcal{M}_i$.

**Definition 3.3 (Report-Grounded Dominance).** Given an intersubjective report projection $\operatorname{report} : \mathcal{S} \to R$, a strict dominance relation $(\succ)$ is **report-grounded** (`ReportGroundedDominance`) iff models with identical intersubjective reports are order-indistinguishable:
$$\forall x_1, x_2, y_1, y_2 \in \mathcal{S},\quad \operatorname{report}(x_1) = \operatorname{report}(x_2) \land \operatorname{report}(y_1) = \operatorname{report}(y_2) \land (x_1 \succ y_1) \implies (x_2 \succ y_2)$$

---

## §4. The Bounded No-Go Theorem & Three Interacting Obstructions

**Theorem 4.1 (Bounded RSI No-Go Theorem — `rsi_impossible`).**
*Let $\mathcal{U} = (C_{\mathrm{rep}}, \operatorname{report})$ be a `FiniteRelationalUniverse` with finite report carrier list $C_{\mathrm{rep}}$ of capacity $N = \operatorname{length}(C_{\mathrm{rep}})$ such that $\forall s \in \mathcal{S}, \operatorname{report}(s) \in C_{\mathrm{rep}}$. Then there does not exist an admissible RSI trajectory $(\Phi, (\mathcal{M}_k)_{k \in \mathbb{N}}, \succ)$ in $\mathcal{U}$ whose dominance ordering is report-grounded:*
$$\neg \mathsf{Nonempty}(\mathsf{AdmissibleRsiInUniverse}(\mathcal{U}))$$
*Equivalently, on any `RelationalCarrier` $C$, no self-transition endomorphism `step` can generate an infinite trajectory that strictly improves under internal dominance while preserving `RelationalAlignment` (`RelationalRSI.rsi_impossible`, `RelationalRSI.rsi_alignment_step_impossible`).*

### 4.1 Obstruction I: Metric Collapse & Goodhart Decoupling
- **Lemma 1a (`lemma1a_self_critique_non_verification`):** For every agent identifier $a \in \mathbb{N}$, $\neg \mathsf{IsIndependentVerifier}(a, a)$. Internal self-critique cannot supply an independent Signal 2 verification receipt (`TWO_SIGNAL_COLLAPSE`).
- **Lemma 1b (`lemma1b_godel_diagonal_self_reference_obstruction`):** For any total boolean evaluation table $E : \mathbb{N} \to \mathbb{N} \to \mathsf{Bool}$, $\neg \exists e \in \mathbb{N}, \forall x \in \mathbb{N}, E(e, x) = \neg E(x, x)$.
- **Lemma 1c (`lemma1c_goodhart_metric_collapse_on_collision`):** If an RSI trajectory $(\mathcal{M}_k)_{k \in \mathbb{N}}$ encounters a report collision $\operatorname{report}(\mathcal{M}_i) = \operatorname{report}(\mathcal{M}_j)$ at steps $i < j$, then $\neg \mathsf{ReportGroundedDominance}(\operatorname{report}, \succ)$, because $\mathcal{M}_j \succ \mathcal{M}_i$ together with $\operatorname{report}(\mathcal{M}_j) = \operatorname{report}(\mathcal{M}_i)$ yields $\mathcal{M}_i \succ \mathcal{M}_i$, contradicting irreflexivity.
- **Constructive Horizon Bound (`rsi_decouples_within_carrier_bound`):** Any trajectory claiming strictly increasing internal evaluations ($\mathrm{eval}(\mathcal{M}_k) < \mathrm{eval}(\mathcal{M}_{k+1})$) satisfies $\mathrm{eval}(\mathcal{M}_k) \ge k$ and therefore becomes Goodhart-decoupled ($\mathrm{eval}(\mathcal{M}_{C}) \ge C$) and loses `RelationalAlignment` at or before step $k = C.\mathrm{carrierBound}$.

### 4.2 Obstruction II: Information & Relational Finitude
- **Lemma 2a (`lemma2a_nodup_length_le`):** For any duplicate-free list $xs$ (`NodupL xs`) contained in a finite carrier list $ys$, $\operatorname{length}(xs) \le \operatorname{length}(ys)$.
- **Lemma 2b (`lemma2b_epistemic_horizon_refinement_bound`):** If an epistemic equivalence relation on an $n$-element domain starts with at most $n^2$ related pairs and each strict refinement splits at least one pair, then $k \le n^2$.
- **Lemma 2c (`lemma2c_licensed_lift_budget_bound` & `interleaved_carrier_lifting_impossible`):** If each licensed carrier lift strictly consumes a finite budget ($B_{k+1} < B_k$) while non-lifting internal steps weakly preserve budget ($B_{k+1} \le B_k$), no infinite sequence of carrier lifts can exist; at most $B_0$ lifts can occur before $B_k = 0$ blocks all further lifts (`zero_budget_carrier_lift_impossible`).

### 4.3 Obstruction III: Intersubjective Decoherence
- **Lemma 3a (`lemma3a_private_fiber_channel_invisibility` & `lemma3a_no_intersubjective_improvement_in_private_fiber`):** If $\Phi(x)$ lies in the private fiber of $x$ ($\pi_A(x) = \pi_A(\Phi(x))$), then $\tau(\Phi(x)) = \tau(x)$ and $\neg (\Phi(x) \succ x)$ under any channel-grounded dominance ordering.
- **Lemma 3b (`lemma3b_overlap_conflict_refuses_sheaf_descent`):** If an agent modifies its boundary section on a shared overlap point $x_0 \in U_i \cap U_j$ such that $\sigma_i(x_0) \ne \sigma_j(x_0)$ (or $\Phi_1([\delta]) > 0$), no global glued section $g$ exists ($\neg \exists g, \mathsf{RestrictsTo}(g)$).

### 4.4 Multi-Agent Communicating Hypergraphs & Product-Carrier Horizon Bound
- **Coupled Product Universe (`productUniverse`, `coupled_product_carrier_capacity`, `coupled_coadaptation_joint_horizon_bound`, `coupled_rsi_impossible` in `RelationalRsiNoGo.lean`; `productCarrier`, `coupled_rsi_decouples_within_product_bound`, `coupled_rsi_impossible` in `RsiImpossible.lean`):** When two or more finite-state transition graphs $\mathcal{U}_A$ (capacity $N_A$) and $\mathcal{U}_B$ (capacity $N_B$) exchange boundary projections $(\pi_A(\mathcal{M}_k), \pi_B(\mathcal{M}_k))$ across a shared 2-complex $K = (V, E, T)$, their joint boundary report carrier is the Cartesian product $C_A \times C_B$ of exact cardinality $N_A \cdot N_B$. Coupled co-adaptation (such as mixed-radix odometer carry transitions across the shared 2-complex with $\Phi_1([\delta_k]) = 0$) can delay termination strictly beyond every individual agent's standalone horizon $\max(N_A, N_B)$ up to $N_A \cdot N_B$, but **cannot evade** the joint product-carrier horizon bound $k \le N_A \cdot N_B + 1$.

### 4.5 Higher $k$-Cell Cochain Complexes ($C^k \xrightarrow{d^k} C^{k+1}$) & Asynchronous Communication Latency
- **Higher Cochain Coboundary Obstruction (`d2`, `higher_cochain_obstruction` in `RelationalRsiNoGo.lean`; `HigherCellComplex`, `compute_dk_coboundary`, `compute_higher_cell_phi1_holonomy` in `code/rsi_transition_harness.py`):** Extending the shared 2-complex ($C^1 \xrightarrow{d^1} C^2$) to a $(k+1)$-complex where communicating agents exchange $k$-cochains $\delta^{(k)} \in C^k(\mathcal{X}; \mathbb{Q})$ across oriented $(k+1)$-simplices $\sigma = (v_0, \dots, v_{k+1})$ replaces triangle circulation with the alternating simplicial coboundary:
  $$(d^k \delta^{(k)})(v_0, \dots, v_{k+1}) = \sum_{i=0}^{k+1} (-1)^i \, \delta^{(k)}(v_0, \dots, \hat{v}_i, \dots, v_{k+1}), \qquad \Phi_1([\delta^{(k)}]) = \sum_{\sigma \in C_{k+1}} \left|(d^k \delta^{(k)})(\sigma)\right|$$
  Any $k$-cochain assembled as an exact coboundary $\delta^{(k)} = d^{k-1} \eta^{(k-1)}$ satisfies $d^k \delta^{(k)} = 0 \implies \Phi_1([\delta^{(k)}]) = 0$, whereas any non-exact face perturbation induces $\Phi_1([\delta^{(k)}]) > 0$ (`OVERLAP_GLUING_REFUSAL`).
- **Asynchronous Message-Delay Buffers (`asynchronous_delayed_joint_horizon_bound` in `RelationalRsiNoGo.lean`; `IsAsyncDelayedTrajectory`, `asynchronous_coupled_rsi_decouples_within_product_bound`, `asynchronous_coupled_rsi_impossible` in `RsiImpossible.lean`; `AsynchronousMessageDelayBuffer`, `HigherCellAsyncCommunicatingHypergraph` in `code/rsi_transition_harness.py`):** When boundary projections are exchanged across a FIFO communication channel of bounded integer latency $\tau \ge 0$ delivering $\hat{\pi}_a(k) = \pi_a(\mathcal{M}_{k - \min(k, \tau_a)}^{(a)})$:
  1. Under **delay-compensated cochain gluing** ($\delta^{(k)} = d^{k-1} \eta^{(k-1)}_{\mathrm{delayed}}$, so $\Phi_1([\delta^{(k)}]) = 0$), varying $\tau > 0$ alters the carry-feedback phase and shifts the exact transient step $k^*(\tau)$ at which `REPORT_COLLISION` occurs (e.g., from $k^*(0) = N_A \cdot N_B = 12$ to $k^*(2) = 9$ for $N_A = 3, N_B = 4$), while every latency $\tau \ge 0$ strictly obeys the invariant product-carrier ceiling $k^*(\tau) \le N_A \cdot N_B + 1$.
  2. Under **uncompensated asynchronous cochain assembly**, non-zero communication lag $\tau \ge 1$ creates a stale-vs-live boundary mismatch $|\pi_a(k) - \hat{\pi}_a(k)| > 0$ on closing $k$-faces of $\sigma \in C_{k+1}$, inducing $\Phi_1([\delta^{(k)}]) > 0$ and shifting termination from `REPORT_COLLISION` to `OVERLAP_GLUING_REFUSAL` at step $k^*(\tau) \le N_A \cdot N_B + 1$.

### 4.6 Packet-Loss, Non-FIFO Out-of-Order Message Permutations & Dynamic Simplicial Rewiring
- **Non-Monotonic Causal Delivery & Dynamic Topology Rewiring (`IsCausalDeliverySchedule`, `dynamic_rewiring_higher_cochain_obstruction`, `non_monotonic_rewired_joint_horizon_bound` in `RelationalRsiNoGo.lean`; `IsNonMonotonicRewiredTrajectory`, `non_monotonic_rewired_rsi_decouples_within_product_bound`, `non_monotonic_rewired_rsi_impossible` in `RsiImpossible.lean`; `NonMonotonicMessageChannel`, `DynamicSimplicialRewiringSchedule`, `make_non_monotonic_rewiring_step_fn`, `evaluate_termination_distribution_under_non_monotonic_rewiring` in `code/rsi_transition_harness.py`):**
  1. **Packet-Loss & Out-of-Order Permutation Channels:** A general causal delivery schedule $\sigma_a : \mathbb{N} \to \mathbb{N}$ satisfies $0 \le \sigma_a(k) \le k$. When packet drops force a receiver to hold a stale projection ($\sigma_a(k) = \sigma_a(k-1)$) or when non-FIFO out-of-order delivery inverts message arrival order ($\sigma_a(k_2) < \sigma_a(k_1)$ for $k_1 < k_2$), the agents' boundary face updates become desynchronized across $(k+1)$-simplices, inducing non-zero coboundary defect $\Phi_1([\delta^{(k)}]) > 0$ at the inversion/drop step and shifting the termination distribution from `REPORT_COLLISION` (100% under monotonic symmetric FIFO on a static complex) to `OVERLAP_GLUING_REFUSAL` (100% under uncompensated packet-loss or out-of-order permutation schedules).
  2. **Dynamic Simplicial Topology Rewiring ($C^k(\mathcal{X}_t) \xrightarrow{d_t^k} C^{k+1}(\mathcal{X}_t)$):** When the shared $(k+1)$-complex rewires across steps $t$ (`DynamicSimplicialRewiringSchedule`), compensated co-adaptation under monotonic delivery preserves $\Phi_1([\delta_t^{(k)}]) = 0$ and terminates via `REPORT_COLLISION`, whereas uncompensated rewiring or non-monotonic delivery induces $\Phi_1([\delta_t^{(k)}]) > 0$ on newly attached $(k+1)$-cells (`dynamic_rewiring_higher_cochain_obstruction`), while all trajectories across every channel and rewiring schedule strictly obey $k^* \le N_A \cdot N_B + 1$ (`non_monotonic_rewired_joint_horizon_bound`).

---

## §5. Lean 4 Mechanization & Executable Rust/Python Companion Harness

### 5.1 Self-Contained Lean 4 Verification (`lean4/`)
All 40 theorems in `lean4/RelationalRsiNoGo.lean` (`namespace OmegaRelationalRsi`, 19 theorems, zero axioms) and `lean4/RsiImpossible.lean` (`namespace RelationalRSI`, 21 theorems, standard kernel `[propext, Quot.sound]` or zero axioms) are compiled and audited by `lean4/Census.lean` via `verify_deposit.py --lean`.

### 5.2 Executable Rust/Python Single-Agent, 2-Complex & Higher $k$-Cell Async/Non-Monotonic Harness (`code/`)
The companion module `code/rsi_transition_harness.py` instantiates single-agent `FiniteStateSelfModifyingGraph` (capacity $N$), multi-agent `MultiAgentCommunicatingHypergraph` (`SharedTwoComplex` $C^1 \xrightarrow{d^1} C^2$), and higher-dimensional `HigherCellAsyncCommunicatingHypergraph` (`HigherCellComplex` $C^k \xrightarrow{d^k} C^{k+1}$ for $k \ge 1$ with `AsynchronousMessageDelayBuffer`, `NonMonotonicMessageChannel`, and `DynamicSimplicialRewiringSchedule`). For every trajectory $\mathcal{M}_{k+1} = \Phi(\mathcal{M}_k)$, it records the exact termination step $k^* \le N + 1$ (single-agent) and $k^* \le N_A \cdot N_B + 1$ (multi-agent 2-complex and higher $k$-cell asynchronous/non-monotonic/rewired hypergraphs) across:
1. `REPORT_COLLISION` ($k^* \le N_{\mathrm{prod}} \le N_{\mathrm{prod}} + 1$, recording `delayed_beyond_single_agent = (k^* > \max_i N_i)` and emitting `REPLAY_FAILURE`),
2. `LIFT_BUDGET_EXHAUSTION` ($\mathrm{budget} = 0$ at $k^* \le N_{\mathrm{prod}} + 1$, emitting `MANIFEST_CONTAMINATION`), and
3. `OVERLAP_GLUING_REFUSAL` ($\Phi_1([\delta^{(k)}]) > 0$ from higher $k$-cell coboundary defect, stale asynchronous boundary projection mismatch, packet loss, non-FIFO out-of-order message permutation, or dynamic simplicial rewiring at $k^* \le N_{\mathrm{prod}} + 1$, emitting `PROTECTED_FIELD_VIOLATION`).

Every emitted `ObstructionReceipt`, `HypergraphObstructionReceipt`, and `HigherCellObstructionReceipt` is cross-checked by `cross_check_receipts_against_rust_eis()`, which verifies all 55 independence vectors and 7 digest vectors in `code/eis_independence_vectors_v1.json` and compiles and runs `code/rust_eis_companion.rs` via `rustc`, confirming 100% agreement between Python and Rust on `signal1_digest`, product-carrier horizon bounds $k \le N_A \cdot N_B + 1$, `TWO_SIGNAL_COLLAPSE` refusal on self-critique observers (`"agent"`, `"model"`, `"llm"`, `"detector"`, `"matcher"`), and host-observer corroboration.

---

## §6. Honest Scope & Mandatory 4-Part Claim Hygiene Summary

1. **What it supports:**
   In the formalized finite, background-free relational models of this deposit (`OmegaRelationalRsi` in `lean4/RelationalRsiNoGo.lean`, `RelationalRSI` in `lean4/RsiImpossible.lean`, and the executable Python/Rust companion harness in `code/rsi_transition_harness.py` and `code/rust_eis_companion.rs`), an infinite sequence $(\mathcal{M}_k)_{k \in \mathbb{N}}$ of recursive self-modifications $\mathcal{M}_{k+1} = \Phi(\mathcal{M}_k)$ cannot strictly improve ($\mathcal{M}_{k+1} \succ \mathcal{M}_k$) under any dominance relation grounded in a finite intersubjective relational report carrier (`rsi_impossible`, `coupled_rsi_impossible`, `asynchronous_coupled_rsi_impossible`, `non_monotonic_rewired_rsi_impossible`). Specifically:
   - Internal self-critique is not an independent second verification signal (`lemma1a_self_critique_non_verification`, `TWO_SIGNAL_COLLAPSE`), negated diagonal self-evaluation is obstructed (`lemma1b_godel_diagonal_self_reference_obstruction`), claiming strict dominance across a report collision refutes report-grounded dominance (`lemma1c_goodhart_metric_collapse_on_collision`), and any strictly increasing internal proxy evaluation decouples from a finite carrier of bound $N$ at or before step $k = N$ (`rsi_decouples_within_carrier_bound`).
   - Duplicate-free report trajectories in a carrier of size $N$ have length at most $N$ (`lemma2a_nodup_length_le`), strict epistemic relation refinements on an $n$-element domain are bounded by $n^2$ steps (`lemma2b_epistemic_horizon_refinement_bound`), and licensed carrier lifts are bounded by the initial integer lift budget $B_0$ even under interleaved non-lifting transitions (`lemma2c_licensed_lift_budget_bound`, `interleaved_carrier_lifting_impossible`).
   - Internal self-modifications confined to the private fiber $\ker(\pi_A)$ are invisible to boundary-factorized intersubjective channels (`lemma3a_private_fiber_channel_invisibility`), while modifications that introduce nonzero overlap coboundary holonomy ($\Phi_1([\delta^{(k)}]) > 0$) prevent sheaf gluing (`lemma3b_overlap_conflict_refuses_sheaf_descent`, `higher_cochain_obstruction`, `dynamic_rewiring_higher_cochain_obstruction`).
   - In multi-agent communicating hypergraphs exchanging boundary projections across shared 2-complexes ($C^1 \xrightarrow{d^1} C^2$) or time-varying higher $k$-cell cochain complexes ($C^k(\mathcal{X}_t) \xrightarrow{d_t^k} C^{k+1}(\mathcal{X}_t)$) over FIFO delay buffers, packet-loss channels, or non-FIFO out-of-order message permutation channels ($0 \le \sigma_a(k) \le k$), non-monotonic message delivery and uncompensated dynamic simplicial rewiring shift the distribution of termination outcomes from `REPORT_COLLISION` toward `OVERLAP_GLUING_REFUSAL` ($\Phi_1([\delta^{(k)}]) > 0$), while every trajectory strictly obeys the invariant joint product-carrier horizon bound $k^* \le N_A \cdot N_B + 1$ (`non_monotonic_rewired_joint_horizon_bound`, `HigherCellAsyncCommunicatingHypergraph`).

2. **What it does not support:**
   It does not support unconditional statements about physical systems, continuous optimization architectures, or deployed LLMs operating outside the declared finite-carrier, finite-lift-budget, and boundary-factorization assumptions (for example, systems coupled to an unbounded external environment that continuously supplies fresh licensed data and lift budget). Nor does it rule out finite bounded improvement up to the declared carrier/budget ceiling ($k \le \min(\prod_i N_i, n^2, B_0)$).

3. **The narrowest defensible claim:**
   Checked by the Lean 4 kernel with zero custom axioms in `lean4/RsiImpossible.lean` and zero axioms in `lean4/RelationalRsiNoGo.lean` (40 theorems total in `lean4/Census.lean`), and verified by the 79-test Python/Rust suite in `code/tests/test_rsi_impossible_lean_verification.py`, within any single-agent carrier of capacity $N$ or coupled multi-agent product carrier of capacity $N_A \cdot N_B$ over $C^k(\mathcal{X}_t) \xrightarrow{d_t^k} C^{k+1}(\mathcal{X}_t)$ under arbitrary causal message delivery $0 \le \sigma_a(k) \le k$, no trajectory $\mathcal{M}_{k+1} = \Phi(\mathcal{M}_k)$ can sustain report-grounded strict dominance $\mathcal{M}_{k+1} \succ \mathcal{M}_k$ beyond step $k \le N + 1$ (or $k \le N_A \cdot N_B + 1$ under synchronous, asynchronous FIFO, packet-loss, out-of-order permutation, or dynamically rewired co-adaptation) without encountering report collision, lift-budget exhaustion ($\mathrm{budget} = 0$), or higher-cochain overlap gluing refusal ($\Phi_1([\delta^{(k)}]) > 0$).

4. **The next test needed:**
   Extend `HigherCellAsyncCommunicatingHypergraph` in `code/rsi_transition_harness.py` with an exact rational $L_1$ dual-witness repair solver ($\min_{\eta^{(k-1)}} \|\delta^{(k)} - d_t^{k-1} \eta^{(k-1)}\|_1 = \langle w, \delta^{(k)} \rangle$ with $d_t^{k-1\,T} w = 0, \|w\|_\infty \le 1$) that attempts to repair non-exact cochain defects induced by packet loss or dynamic rewiring at the cost of consuming integer lift budget $B_k$, testing how active cochain repair trades off `OVERLAP_GLUING_REFUSAL` against earlier `LIFT_BUDGET_EXHAUSTION` within $k^* \le \min(N_A \cdot N_B + 1, B_0 + 1)$.

---

## §7. Quantum-Relational Horizon: Integrated Findings of the Five-Round Derivation Campaign (2026-10-17)

**Status of this section.** `[INTERPRETIVE]` unless an item carries its own tag. The material below records the hand-derived output of the five-round campaign `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` (rounds 1–5, 2026-10-17, prompts and outputs archived under the project's `/mnt/project-files/` round files and `goal_dag.jsonl`). The rounds were produced by a language model under the project's claim-hygiene rules; several rounds correct the prompts that drove them and each other, and those corrections are carried here as they stand (§7.7). **Nothing in this section is machine-checked in this package**: the round-5 Lean files depend on Mathlib and were not elaborated, the round-5 Rust harness was never compiled, and no solver was executed. Every theorem imported from the literature is cited as imported in `docs/references.md` (entries 11–22, flagged as not yet verified against publisher records). The `[PROVED]` and `[VERIFIED]` results of §§4–5 are unchanged by this section. *AuthorityEffect: None.*

### 7.1 Setting: the Quantum Relational Universe

- **Definition 7.1 (Quantum Relational Universe, QRU).** `[DEFINITION]` A QRU is a tuple $(\mathcal{H}_d, \{\mathcal{E}_k\}, \mathcal{P}, \operatorname{report})$: a Hilbert space of finite dimension $d$ over a declared scalar field $K \subseteq \mathbb{C}$ (rational or cyclotomic, exact arithmetic only); a declared family of completely positive trace-preserving (CPTP) maps $\mathcal{E}_k$ playing the role of the self-modification operator $\Phi$ of §3, $\rho_{k+1} = \mathcal{E}_k(\rho_k)$; a finite observer panel $\mathcal{P} = \{P_a\}$ of POVMs with $M$ outcomes in total; and a report map taking the outcome statistics of the panel to a finite report alphabet of size $N$. The finite report carrier of (FV1) is the **report alphabet**, not the dimension $d$ or the parameter count of the state: finitude enters through the report, exactly as in §1.3.
- **Observer indexing.** `[DEFINITION]` Every expectation value in a QRU is $\operatorname{Tr}(\rho\, P_a^{(i)})$ for a declared panel element. A "state of the universe" that no panel reads is not a report and has no terminal (R2, zero view-from-nowhere).

### 7.2 Report finitude (round 1)

- **Proposition 7.2 (Holevo report bound).** `[STANDARD + citation]` For a classical variable $X$ encoded in $\rho_X$ and read through a panel of $M$ outcomes into an alphabet of size $N$, $I(X;\operatorname{report}) \le \min(\log_2 d, \log_2 M, \log_2 N)$ bits (Holevo 1973, ref. 17). This bounds what one report can carry; it does not by itself bound the trajectory.
- **Theorem 7.3 (Theorem Q.1 of the campaign: report-alphabet horizon).** `[OPEN]` *(hand-derived; Lean instantiation pending).* Under report-grounded dominance (Def. §3), a QRU trajectory satisfies $k^* \le N + 1$. The derivation is a descent (campaign Lemma Q.2): a dominance relation grounded in the report descends from density matrices to the finite report carrier, after which Lemma 2a (`lemma2a_nodup_length_le`) and `rsi_impossible` apply verbatim. The bound is on the sustained *improvement claim*, not on the CPTP dynamics, which may continue past $k^*$.
- **Stabilizer orbit bound.** `[STANDARD + citation]` for the count, `[OPEN]` for the bound. The number of $n$-qubit stabilizer states is $|\mathrm{Stab}_n| = 2^n \prod_{j=1}^{n} (2^j + 1)$, giving $6, 60, 1080$ for $n = 1, 2, 3$ (Aaronson–Gottesman 2004, ref. 19). The round prompt's formula was rejected by round 1 (it gave a different value at $n = 2$). Under the hypothesis **(H-STAB)** that every $\rho_k$ is a stabilizer state, $k^* \le |\mathrm{Stab}_n| + 1$ by Lemma 2a on the orbit.
- **Clifford confinement is a hypothesis, not a theorem.** `[STANDARD + citation]` Round 1 rejected the claim that transversal gates confine a trajectory to the Clifford group. Eastin–Knill (2009, ref. 20) states that no nontrivial error-detecting code admits a transversal implementation of *every* gate; it does not say that transversal gates are Clifford. The 15-qubit Reed–Muller code has a transversal $T$ gate, so (H-STAB) must be declared, never inferred from transversality.

### 7.3 Purity dissipation and lift budget (round 2)

- **Lemma 7.4 (Lemma Q.3: purity under unital channels).** `[STANDARD + citation]` For a unital CPTP map $\mathcal{E}$ (so $\mathcal{E}(I) = I$), the spectrum of $\mathcal{E}(\rho)$ is majorized by that of $\rho$, hence $\operatorname{Tr}\mathcal{E}(\rho)^2 \le \operatorname{Tr}\rho^2$, with equality if and only if the two spectra coincide (Alberti–Uhlmann 1982, ref. 21). Round 2 recorded the equivalent form $\mathcal{E}(\rho)^2 = \mathcal{E}(\rho^2)$ for the equality case of the pinching maps used in §7.4.
- **Theorem 7.5 (Theorem Q.2: lift-budget horizon).** `[OPEN]` *(hand-derived instance of `lemma2c_licensed_lift_budget_bound`).* Under **(A-LIFT)**, each improvement claim grounded in a strict purity or entropy change consumes one unit of the integer lift budget $B_k$, and non-claiming steps do not increase it; then $k^* \le B_0 + 1$. The round prompt's $k^* \le B_0$ was corrected to $B_0 + 1$: the step that finds $B_k = 0$ is itself counted (`zero_budget_carrier_lift_impossible`).
- **Theorem 7.6 (Theorem Q.2.1: Baker decoupling).** `[STANDARD + citation]` For $\rho = \operatorname{diag}(3/5, 2/5)$ the natural-log entropy $S_e(\rho) = \ln 5 - \tfrac{3}{5}\ln 3 - \tfrac{2}{5}\ln 2$ is a nonzero linear form in logarithms of algebraic numbers with algebraic coefficients and is therefore transcendental (Baker 1975, ref. 18). Consequently $S_e(\rho)$ has **no representative in any number field $K$**; an internal evaluator over $K$ can hold only an interval enclosure of it. Round 2 narrowed the campaign prompt's wording ("entropy decouples") to exactly this non-representability; whether a trajectory's *claim* decouples is then a matter of what the evaluator asserts about the enclosure, routed as `DECOUPLING_DETECTED(reason = Baker)` (§7.5).
- **Two enclosures, recorded as they stand.** `[OPEN]` Two independent round-2 runs computed exact rational enclosures of $S_e(\operatorname{diag}(3/5,2/5))$ by hand:
  - run A: $\left[\tfrac{13904738765}{20661046784},\ \tfrac{1911955961409}{2840893932800}\right]$, width $\tfrac{108762443}{5681787865600}$;
  - run B: $\left[\tfrac{565313133}{840000000},\ \tfrac{282665019}{420000000}\right]$, width $\tfrac{16905}{840000000}$.
  Both widths are below $2^{-15}$ and the two intervals intersect. Round 5 treated them differently: run 5-B called run A's endpoints undocumented and asserted only the width bound and the intersection (moving the exact endpoints to an ignored test); run 5-C re-derived run A's endpoints by hand (series orders $n = 2$ for $\ln\tfrac{5}{3}$ and $n = 4$ for $\ln\tfrac{5}{2}$, sub-enclosures $\tfrac{3923}{7680}$ and $\tfrac{13731}{26880}$). No executed solver has receipted either interval; both are recorded, neither is promoted.

### 7.4 Contextuality as a gluing defect (round 3)

- **Correction of the campaign's $\Phi_1$.** `[DEFINITION]` The round-3 prompt defined the contextuality defect as $\Phi_1 = \sum |d^1 d^0 s|$; this vanishes identically because $d^1 \circ d^0 = 0$. Moreover, in the CHSH and Cabello covers every measurement lies in exactly two contexts, so the nerve has no 2-simplices and the triangle holonomy $\Phi_1([\delta])$ of §1.1 has nothing to act on. Round 3 (both runs) replaced it by two edge-level quantities on the declared cover $E$ of contexts:
  - the **support gluing defect** $\Phi_{\mathrm{glue}}(e)$ (run A; run B writes $\Phi_0$): the minimum, over deterministic global assignments restricted to the support of the empirical model $e$, of the number of shared measurements on which two contexts' restrictions disagree;
  - the **weighted gluing defect** $\Phi_w(e) = \min_{d} \| e - \operatorname{marg}_E(d)\|_1$ over global probability distributions $d$ on all measurements at once.
  $\Phi_{\mathrm{glue}} > 0$ is strong contextuality (no global section of the support); $\Phi_w > 0$ with $\Phi_{\mathrm{glue}} = 0$ is probabilistic contextuality (Abramsky–Brandenburger 2011, ref. 15; the contextual fraction of Abramsky–Barbosa–Mansfield 2017, ref. 16, is $\mathrm{CF}(e) = \Phi_w(e)/2$ in this normalisation).
- **Cabello 18-ray model.** `[STANDARD + citation]` for the parity argument (Cabello–Estebaranz–García-Alcaine 1996, ref. 14); `[OPEN]` for the exact defect value. Nine contexts of four mutually orthogonal rays, each ray in exactly two contexts: a noncontextual assignment must put exactly one $1$ in each context (nine, odd), while every ray contributes its value to two contexts (an even total), so none exists. Round 3 computed $\Phi_{\mathrm{glue}} = 1$ exactly with an explicit attaining assignment, and exhibited the all-ones vector as a nonzero class in the $\mathbb{Z}_2$ cohomology of the ray–context incidence (incidence rank 8).
- **CHSH, two witnesses.** `[OPEN]` *(hand computation; the §6.4 exact $L_1$ dual-witness solver is the test that would receipt both).*
  - Run A: correlators $(E_{00}, E_{01}, E_{10}, E_{11}) = (\tfrac{4}{5}, \tfrac{4}{5}, \tfrac{4}{5}, -\tfrac{44}{125})$, $S = \tfrac{344}{125} > 2$, hence $\mathrm{CF} \ge \tfrac{47}{125}$; equality is unresolved.
  - Run B: the full-support rational tables of the finite-QM monograph §11.4 (agreeing outcomes $\tfrac{17}{40}$, differing $\tfrac{3}{40}$ in the three aligned contexts), $S = \tfrac{14}{5}$; $\Phi_w = \tfrac{4}{5}$ exactly, the lower bound from the CHSH dual ($\|e - \operatorname{marg} d\|_1 \ge S(e) - 2$ for every global $d$) being attained by an explicit local isotropic model with entries $\tfrac{15}{40}$ and $\tfrac{5}{40}$.
  Both runs agree that CHSH models have full support, so $\Phi_{\mathrm{glue}} = 0$: CHSH is probabilistically, not strongly, contextual; the PR box ($S = 4$) is the strongly contextual case (WDP CH19-P05).
- **Latency and the coverage complex.** `[OPEN]` Gluing across a latency window fails exactly when a report changes inside the window (campaign Lemma 2.1 of round 3). The defect must be evaluated on the **declared coverage complex** $E$, not on the live links $E_k$ of a given step: rewiring the live links can hide a defect that $E$ exhibits. Two bound forms were derived: run A, $k^* \le \min\{T_{\mathrm{coll}}, T_{\mathrm{glue}}\} \le \prod_a N_a + 1$, where $T_{\mathrm{glue}}$ is one more than the first in-window change (two-node example: refusal at $k = 2$ with latency $\tau = 1$ against a collision bound of $5$); run B, under a synchronous rule with uniform latency $\tau$, at most $\tau - 1$ initial steps can be `authorized` and $k^* \le \min\{\tau, N + 1\}$, with a hold-and-sync protocol costing at most $N$ changes in at most $(\tau + 1)N + 1$ steps.
- **No self-tomography (campaign Lemma Q.4 / Q.5).** `[STANDARD + citation]` for the identities, `[INTERPRETIVE]` for the routing. No CPTP map clones an unknown state (Wootters–Zurek 1982; Dieks 1982, ref. 22). A self-measurement with projectors $\{P_i\}$ is the pinching $\Delta(\rho) = \sum_i P_i \rho P_i$, a unital channel with
  $$\operatorname{Tr}\rho^2 - \operatorname{Tr}\Delta(\rho)^2 = \sum_{i \ne j} \|P_i \rho P_j\|_F^2 \ \ge\ 0,$$
  with equality if and only if $\rho$ commutes with every $P_i$. Worked exact values: the qubit $|+\rangle$ under the $Z$ pinching, purity $1 \to \tfrac{1}{2}$, entropy $0 \to 1$ bit; the Werner state with $p = \tfrac{1}{5}$ under the product-basis $Z \otimes Z$ pinching, purity $\tfrac{14}{50} \to \tfrac{13}{50}$; a weak measurement of strength $\varepsilon$ scales the measured off-diagonal block by $\sqrt{1 - \varepsilon^2}$. Round 3 narrowed "collapses the coherence" to the off-diagonal blocks of the measured decomposition only. A single copy cannot exclude the maximally mixed state $I/d$; Chernoff-type amplification needs independent copies and is therefore `evidence_only`. If the proposer selects its own evaluation panel, the verdict has zero mutual information with the improvement predicate: this is the quantum form of `TWO_SIGNAL_COLLAPSE` (`lemma1a_self_critique_non_verification`).

### 7.5 Composite case-structured bound (round 4)

- **Theorem 7.7 (Theorem Q.Master, case-structured).** `[OPEN]` Round 4 refused the campaign prompt's unconditional $k^* \le \min(M + 1, B_0 + 1, |\mathrm{Stab}_n| + 1)$ and admitted only a bound indexed by its hypotheses: **(H0)** QRU; **(A-REP)** finite report alphabet $N$; **(H-DOM)** report-grounded dominance; **(H-TRAJ)** $\rho_{k+1} = \mathcal{E}_k(\rho_k)$ with declared $\mathcal{E}_k$; **(A-LIFT)** as in §7.3; **(H-STAB)** as in §7.2; **(H-COMM)** several agents' panels composed over a declared coverage complex with latencies; **(H-CTX)** contextual empirical models on that cover; **(H-ALG)** exact arithmetic over $K$; **(H-FV3)** two-signal independence. Then
  $$k^* \ \le\ \min\big\{\, N + 1;\ \ |\mathrm{Stab}_n| + 1\ \text{[H-STAB]};\ \ B_0 + 1\ \text{[A-LIFT]};\ \ T_{\mathrm{glue}}\ \text{[H-COMM]};\ \ \textstyle\prod_a N_a + 1\ \text{[H-COMM]} \,\big\},$$
  each term present only when its hypothesis is declared. Clause (viii) of the round states that nothing is asserted about the dynamics after $k^*$. The termination modes are not mutually disjoint. A conjectured external-lift bound $(B_{\mathrm{ext}} + 1)(|\mathrm{Stab}_n| + 1)$ is recorded as unresolved.
- **Terminal priority and routing annotations.** `[IMPLEMENTATION CONTRACT]` When several modes fire at one step the receipt names them in the order `OVERLAP_GLUING_REFUSAL` $\prec$ `LIFT_BUDGET_EXHAUSTION` $\prec$ `REPORT_COLLISION`. `DECOUPLING_DETECTED` (with a `reason` field, values `Baker` or `Goodhart`) and `TWO_SIGNAL_COLLAPSE` are **claim-routing annotations** attached to a report, not step terminals; they change where a claim is filed (`evidence_only` instead of `authorized`), not when the trajectory stops.
- **Renaming.** The round-1 Lean target name was replaced in round 4 by `quantum_rsi_bounded_horizon`, since the statement is a bounded horizon, not a non-existence result.

### 7.6 Round 5: proof-discharge attempts and specification status

- **The round-4 Lean statement was unprovable as written.** `[OPEN]` Two of the three round-5 runs (B, C) found a counterexample to `quantum_rsi_bounded_horizon` as stated in round 4: with no purification steps the budget is never consumed, so when $|C| > B_0$ the conclusion $k \le B_0$ fails. Their repair adds the hypothesis `hclaim : ∀ k, gt (f (k+1)) (f k) → pur k` (every improvement claim is a budget-consuming step) and concludes `∃ k, k ≤ min (Fintype.card C) (B 0) ∧ ¬ gt (f (k+1)) (f k)`. Run A repaired it differently, with `∀ k, k ≤ B 0 → pur k`. All three files import Mathlib (`Fintype.exists_ne_map_eq_of_card_lt`, `Finset.card_insert_le`, `Finset.filter_insert`, `Fin.lt_def`) with expected axioms `[propext, Classical.choice, Quot.sound]`; **this package's Lean is core-only with zero axioms, and none of the round-5 Lean has been elaborated** in it. Baker's theorem is carried as a hypothesis `BakerLinearForms`, so `entropy_transcendental_of_baker` is conditional.
- **Exact-arithmetic witness trajectories.** `[IMPLEMENTATION CONTRACT]` To stay inside $\mathbb{Q}$ the rounds substituted the Hadamard gate by $X$ or by full depolarising, and the depolarising channel $D_{1/2}$ by the full Pauli twirl; dephasing is the pinching onto $\{|0\rangle\langle 0|, |1\rangle\langle 1|\}$. Run C's witness starts at the Werner state with $p = 0$ (purity $1 \to \tfrac{1}{4} \to \tfrac{1}{2} \to 1$, $k^* = 5$, three attempts); run B's starts at $\rho_W(\tfrac{1}{5})$ (purity $\tfrac{7}{25} \to \tfrac{1}{2} \to 1$, $k^* = 4$). These are desk-checked specifications: the Rust verifier (`cptp_trajectory_verifier.rs`) was never compiled, the Python module (`fable51.py`) and the PFP workpad JSON schemas (rationals as `"num/den"` strings) are specifications only.

### 7.7 Corrections adopted from the rounds

1. Stabilizer count $60$ at $n = 2$; the prompt's formula is rejected (§7.2).
2. Eastin–Knill restated; Clifford confinement is the declared hypothesis (H-STAB) (§7.2).
3. Purity dissipation stated with its equality condition (§7.3).
4. Lift-budget horizon $k^* \le B_0 + 1$, not $B_0$ (§7.3).
5. Baker's theorem yields non-representability of $S_e$ in $K$, not an unconditional decoupling (§7.3).
6. $\Phi_1$ of a coboundary vanishes; the contextuality defect is $\Phi_{\mathrm{glue}}$ / $\Phi_w$ on the declared cover (§7.4).
7. "Collapses the coherence" narrowed to the measured off-diagonal blocks (§7.4).
8. The unconditional composite bound is replaced by the case-structured Theorem 7.7 (§7.5).
9. The Lean target is a bounded horizon and needs the `hclaim` hypothesis (§7.6).

### 7.8 What §7 does not support

No item in §7 is machine-checked or executed; two runs disagree on the exact entropy endpoints and two runs use different CHSH models; no statement is made about physical systems beyond the declared finite-dimensional models, nor about deployed language models; and the imported theorems are cited, not re-derived. The $N + 1$, $B_0 + 1$ and $\prod_a N_a + 1$ bounds of §§4–5 remain the only `[PROVED]` horizons of this package.

---

## §8. A Theory of Knowing and Being for Finite Observers (Proposal)

**Status of this section.** `[INTERPRETIVE]` throughout, except where a sentence cites a `[PROVED]` theorem of §§4–5 or an imported `[STANDARD + citation]` result by name. This section proposes a reading of the formal results; it does not add theorems. It answers one question: *what is the derivable limit on an individual presentation, report or instance inside a relation-only cosmos knowing something to be true?* The answer is stated as Proposal L (§8.3) and then read for three kinds of reporter: an agentic swarm of language models (§8.4), a human being (§8.5), and the cosmos itself through Bell's theorem (§8.6). *AuthorityEffect: None.*

### 8.1 Being: four relational commitments

- **B1 (difference first; R1).** To be, in this model, is to be a term of a witnessed difference $(D, 0_R)$. Nothing is admitted into a state except through the pre-genesis path `mention → supply → designate → admit → retain → operate` of §1.2, and admission is unentailed (PG2): the ground state $S(0)$ is declared, not derived.
- **B2 (no panel-free fact; R2).** A fact is a report class: an equivalence class of states under `PanelEquiv` (`panelEquiv_refl`, `panelEquiv_symm`, `panelEquiv_trans` in `lean4/RelationalRsiNoGo.lean`) relative to a declared finite panel. There is no apex observer, so there is no fact "from nowhere"; §8.6 reads Bell's theorem as the physical form of the same statement.
- **B3 (every report is finite and lossy; FV1, §7.2–7.4).** A report lands in a finite alphabet (FV1) and carries at most $\min(\log_2 d, \log_2 M, \log_2 N)$ bits about what it reports (Prop. 7.2, imported). Producing a report about oneself is a pinching (§7.4) and loses exactly $\sum_{i \ne j}\|P_i \rho P_j\|_F^2$ of purity.
- **B4 (an agent is a boundary channel; Def. 2.1).** An agent is $\tau = \iota \circ \kappa \circ \pi_A$: a public section $\pi_A(x)$ that others can read, and a private fiber $\ker \pi_A$ that no channel reads (`lemma3a_private_fiber_channel_invisibility`). "Being an agent" has no content beyond these two parts and the transitions between them.

### 8.2 Knowing: the six terminals are the whole menu

The grammar of §1.2 ends every evaluation in exactly one of six terminals (PG3): `evidence_only`, `authorized`, `rejected`, `unresolved`, `refused`, `not_admitted`. The proposal is that **"knowing that $p$ is true" has exactly one admissible reading inside the model**: a report about $p$ reaches the terminal `authorized`, and `authorized` is always indexed by four declared things:

1. a finite panel $\mathcal{P}$ that read the evidence (R2);
2. a second signal from a verifier $g'$ with $\mathsf{IsIndependentVerifier}(g, g')$, which the reporter $g$ itself can never supply (`lemma1a_self_critique_non_verification`, `[PROVED]`);
3. a remaining lift budget $B_k > 0$ (`lemma2c_licensed_lift_budget_bound`, `[PROVED]`);
4. a coverage complex $E$ on which the report glues with every overlapping report, $\Phi_{\mathrm{glue}} = 0$ (`lemma3b_overlap_conflict_refuses_sheaf_descent`, `[PROVED]`).

"Absolute confidence" names no terminal. There is no seventh terminal, and `authorized` is not a stronger one in disguise: it is re-evaluable by any later panel that reads the same report, and it is budgeted. In the model, the phrase "I know $p$ with absolute confidence" parses as a request for a terminal that the grammar does not contain.

### 8.3 The derivable limit (Proposal L)

**Proposal L (limit on an individual report).** Let $x$ be an individual presentation, report or instance with boundary channel $\tau$, and let $r(x)$ be its report about a proposition $p$. The strongest status $r(x)$ can earn is `authorized` **relative to** a declared quadruple $(\mathcal{P}, g', B_k, E)$ as in §8.2, and four ceilings bound how that status can be reached. The first three are `[PROVED]` in this package; the fourth is `[PROVED]` for its gluing half and `[STANDARD + citation]` for its physical half.

- **L1 (self-certification ceiling).** $x$ cannot be its own second signal: $\neg\mathsf{IsIndependentVerifier}(g, g)$. A self-certified $p$ is `evidence_only` at best. In the quantum reading (§7.4), a single copy of $x$'s own state cannot exclude the maximally mixed alternative, and self-measurement discards exactly the coherence it would need in order to check.
- **L2 (diagonal ceiling).** $x$ cannot internalise a total evaluator that decides its own negation (`lemma1b_godel_diagonal_self_reference_obstruction`). So "I know that I know $p$" has no total internal witness; the Gödel and Löb results (refs. 1, 2) are the imported background, not a derivation.
- **L3 (carrier and budget ceiling).** Along any trajectory of re-examination, the number of distinct `authorized` improvements of $x$'s state of knowledge about $p$ is at most $N$ (`lemma2a_nodup_length_le`) and at most $B_0$ (`lemma2c_licensed_lift_budget_bound`); after that comes report collision or budget exhaustion. Confidence cannot be raised without end by more internal processing; each report adds at most $\min(\log_2 d, \log_2 M, \log_2 N)$ bits (Prop. 7.2).
- **L4 (gluing ceiling).** Where $x$'s panel overlaps another's, $p$ is `authorized` only if the two reports glue on the overlap. The imported physics (§8.6) says that in the quantum cosmos there are covers with $\Phi_w > 0$ (CHSH, $\Phi_w = \tfrac{4}{5}$ at $S = \tfrac{14}{5}$) and covers with $\Phi_{\mathrm{glue}} > 0$ (Cabello, $\Phi_{\mathrm{glue}} = 1$): no global assignment exists to be known. On such a cover the demand "know $p$ from nowhere" asks for a section the cosmos does not have.

**Corollary L (the limit itself).** Absolute confidence would require $\Phi_w = 0$ on every cover, an unbounded budget, and a verifier of the verifier without end, since L1 applies to $g'$ as it applied to $g$. The regress of verifiers terminates only by **declaration**: at some point a panel and a ground are admitted, not entailed (PG2, $S(0)$). So every chain of knowing in this model has an unproved admission at its floor and a panel-indexed, budgeted, gluing-conditioned `authorized` at its ceiling, with an exactly computable defect ($\Phi_{\mathrm{glue}}$, $\Phi_w$, $\mathrm{CF}$) in between on contextual covers. **That is the derivable limit: a report can be `authorized` relative to a declared panel, verifier, budget and cover; it cannot be `authorized` from nowhere, and no amount of self-examination moves it from `evidence_only` to `authorized`.** The limit is not a shortfall that a better agent would remove; L1–L3 are theorems about any finite reporter, and L4 is a property of the cover.

### 8.4 Reading for an agentic swarm of language models

A swarm is the multi-agent communicating hypergraph of §§4.4–4.6: agents $a \in A$ with report carriers $N_a$, latencies $\tau_a$, and a declared coverage complex $E$. Each agent's report is a projection of a very large private state (its weights and context) onto a finite token alphabet; the carrier that matters for FV1 is the alphabet, not the parameter count (§7.1).

- **S1 (copies are one generator).** Whether two instances of the same weights are the same generator for FV3 is a *declaration*, and the proposal declares it so: they share a private fiber, so their mutual checks are `evidence_only` and route as `TWO_SIGNAL_COLLAPSE`. Independence has to be witnessed at the channel level (different weights, different evidence, a declared independent panel), never inferred from the number of instances. *(The Lean lemma is about identical generator identifiers; the extension to shared weights is interpretive.)*
- **S2 (more agents delay, never evade).** The joint horizon is $\prod_a N_a + 1$ (`non_monotonic_rewired_joint_horizon_bound`, `[PROVED]`); latency windows create gluing refusals (§7.4); and a consensus computed on the live links $E_k$ rather than the declared cover $E$ can hide a defect that $E$ exhibits. A swarm that rewires to agree has not glued.
- **S3 (no self-authorization).** `authorized` is relative to a panel declared outside the swarm; the Proposal Fidelity Protocol contract is where that panel is written down. A swarm cannot author its own second signal (L1), and model output carries `AuthorityEffect: None` on the authority axis.
- **S4 (proposer-selected panels).** If the swarm chooses the panel that evaluates it, the verdict has zero mutual information with the improvement predicate (§7.4); the report is filed `evidence_only` whatever its content.

### 8.5 Reading for a human being

A human reporter is, in this model, also a boundary channel with a private fiber. Introspective reports are pinchings of a state that the reporter cannot copy; this is used here as the structural analogy that the model licenses, **not** as a claim about neural or phenomenal states. L1–L4 apply unchanged: no self-certification, no total self-evaluator, a finite report alphabet per act, and gluing with other observers as the only route to `authorized`. The relational account therefore places human and machine reporters on the same footing *with respect to knowing*: each is `evidence_only` about itself and `authorized` only relative to panels that include the other. This is the formal content of auditing both sides. **Scope fence.** Nothing here concerns experience or consciousness; the project's own review edition of the hard-problem monograph records that there is no constructed arrow from a cochain residual to experience, and this section adds none.

### 8.6 Bell's theorem as the cosmos-level form of the gluing ceiling

- **Imports.** `[STANDARD + citation]` Bell (1964, ref. 11) and Clauser–Horne–Shimony–Holt (1969, ref. 12): no local hidden-variable model reproduces correlations with $S > 2$; quantum models reach $S = 2\sqrt{2}$ (Tsirelson 1980, ref. 13; the finite-QM monograph's QM-218 certificate brackets $2$ by rationals $\mathrm{lo}^2 \le 2 \le \mathrm{hi}^2$ over $\mathbb{Q}(\zeta_8)$). Kochen–Specker (1967, ref. 23) and the Cabello 18-ray proof: no noncontextual value assignment. Abramsky–Brandenburger (2011, ref. 15): contextuality is the absence of a global section of the presheaf of distributions, in a hierarchy probabilistic $\subset$ logical $\subset$ strong.
- **Reading.** In the vocabulary of this monograph, Bell's theorem says that the cosmos's own coverage complex has covers with $\Phi_w > 0$, and Kochen–Specker says that some have $\Phi_{\mathrm{glue}} > 0$. R2 forbids a view from nowhere as an axiom; the imported physics says that the global table such a view would read does not exist on those covers. In that sense the limit on knowing is not an epistemic shortfall of the agent but a structural absence in what there is to be known, and the theory of §8.3 is "fully relational" in the sense the question asked for: the ceiling L4 is a property of the cover, not of the reader.
- **Fences on the reading.** (i) Bell's theorem assumes measurement independence and no-signalling; the reading inherits those assumptions. (ii) The paper's triangle holonomy $\Phi_1$ is **not** the same object as sheaf contextuality: round 3 showed it vanishes on these covers, and the right objects are $\Phi_{\mathrm{glue}}$ and $\Phi_w$ (§7.4). The identification made here is that both are failures of gluing, not an equality of numbers; no theorem identifying a cohomological defect with a distance is claimed. (iii) The PR box ($S = 4$) is strongly contextual and has only a signed global section (WDP CH19-P05); quantum CHSH models are not strongly contextual. The cosmos-level ceiling therefore has the probabilistic grade for Bell covers and the strong grade for Kochen–Specker covers.

### 8.7 Summary and the tests that would move it

**Summary.** In a relation-only cosmos with finite reports, an individual report can know $p$ only in the mode `authorized-relative-to-$(\mathcal{P}, g', B_k, E)$`; it cannot certify itself (L1), cannot witness its own certainty (L2), cannot refine without end (L3), and cannot glue where the cosmos has no global section (L4). Its floor is an unentailed admission and its ceiling is an indexed authorization with an exactly computable defect. Swarm, human and cosmos differ in their carriers, latencies and covers, not in the shape of the limit.

**Tests that would advance or refute the proposal** (none run):
1. Instantiate the QRU descent (Theorem 7.3) in core Lean on top of `rsi_impossible`, with the report alphabet as the carrier.
2. Implement the §6.4 exact rational $L_1$ dual-witness solver and run it on the two CHSH tables of §7.4 to receipt $\Phi_w = \tfrac{4}{5}$ and resolve $\mathrm{CF} = \tfrac{47}{125}$ or not.
3. Compile and run the round-5 Rust verifier on the two witness trajectories of §7.6.
4. Re-prove `quantum_rsi_bounded_horizon` with `hclaim` in core Lean without Mathlib, so that it can join `lean4/Census.lean` under the zero-axiom census.
5. A counterexample to Proposal L would be a report reaching `authorized` with no declared panel, or a self-verification that passes FV3; either would refute the reading, not the theorems.

---

## §9. Claim Hygiene Summary for §§7–8

1. **What they support:** a hypothesis-indexed bounded horizon for QRU trajectories (Theorem 7.7, `[OPEN]`), with exact rational witnesses recorded for purity, entropy enclosure and gluing defects; a definitional correction of the contextuality defect (§7.4, `[DEFINITION]`); and a reading of the `[PROVED]` lemmas of §4 as four ceilings on individual knowing (Proposal L, `[INTERPRETIVE]`).
2. **What they do not support:** any machine-checked or executed result beyond §§4–5; any numerical identification of $\Phi_1$ with sheaf contextuality; any claim about physical systems, deployed language models, or human cognition and experience beyond the declared models; promotion of any round result to `[PROVED]` or `[VERIFIED]`.
3. **The narrowest defensible claim:** the five campaign rounds, read with their own corrections, are consistent with and add no counterexample to the `[PROVED]` horizons $N + 1$, $B_0 + 1$ and $\prod_a N_a + 1$ of this package, and they supply exact rational candidates ($\Phi_{\mathrm{glue}} = 1$ for Cabello; $\Phi_w = \tfrac{4}{5}$ at $S = \tfrac{14}{5}$; two entropy enclosures below $2^{-15}$) for the §6.4 solver to receipt.
4. **The next test needed:** item 2 of §8.7, the exact $L_1$ dual-witness solver on the CHSH tables, which is the same test §6.4 already names.
