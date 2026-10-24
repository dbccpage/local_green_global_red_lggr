# Local Green, Global Red VIII: Online Streaming Discovery, Prefix Admissibility, and Runtime Gluing

**Author:** Jeremy H. Carroll  
**Date:** 24 October 2026  
**Version:** 0.1.0  
**AuthorityEffect:** `None`

## Abstract

Volumes I–VII of the *Local Green, Global Red* (LGGR) monograph series analyze when local step verdicts, boundary quotients, finite-stage congruences, or linear observation maps fail to determine a specified global property. In those volumes, obstruction and composition are examined post-hoc on complete offline execution traces, fixed behavior tables, or static cochain complexes. In contrast, running agentic swarms require runtime discovery while intermediate artifacts and handoffs stream through execution. This volume formalizes online, streaming LGGG (Local Green, Global Green) versus LGGR (Local Green, Global Red) discovery and delivers machine-checked Lean 4.35.0 proofs alongside an exact rational Python implementation and live empirical benchmark receipts. First, we formalize the monotonicity of report-fiber collisions under streaming trace extensions, their invariance under deterministic postprocessing, and the report-only evaluator verdict ceiling on colliding fibers. Second, we formalize streaming prefix-by-prefix signed increment telescoping, exhibit the strict separation between online every-prefix admissibility and cumulative endpoint admissibility, derive the persistence of prefix violations that justifies online early stopping, and construct the streaming unsigned magnitude report collision. Third, we establish exactness on open acyclic handoff trees versus incremental cycle closure obstruction, deriving exact rational $\ell^1$ dual witnesses on frustrated cycles. Fourth, we formalize boundary-sufficient runtime gluing certification and forced defect under boundary insufficiency. Fifth, we resolve the Volume I §9 "Next Test Needed" by executing live OpenRouter model benchmarks ($N = 8$ tasks, 16 completions, empirical rates $\mathrm{LPR}=1, \mathrm{GPR}=1, \mathrm{NGD}=0, \mathrm{ZDR}=1, \mathrm{PGD}=0$) and verifying deterministic offline replay receipts across Tests 1–4. Finally, we synthesize a boundary-sufficient runtime guard architecture for practitioner swarms.

**Keywords:** `local-green-global-red`, `online-discovery`, `streaming-monitors`, `prefix-admissibility`, `evaluator-defects`, `cochain-obstruction`, `l1-duality`, `runtime-gluing`, `boundary-sufficiency`, `multi-agent-swarms`

---

## 1. Introduction: Composable LGGG vs. Obstructed LGGR in Running Swarms

In distributed multi-agent systems and staged language-model pipelines, a pervasive failure mode occurs when every intermediate agent, tool, or stage emits a local "pass" verdict, yet the composed end-to-end task fails or violates an unmonitored system invariant. Within the LGGR framework, this phenomenon is formalized as Local Green, Global Red (LGGR), characterized by a negative evaluated path kernel defect $\Delta_E = E_g - \prod_{i=1}^k E_i = -1$ (Negative Global Defect, `NGD`). Conversely, when local checks compose to satisfy the global requirement without hidden boundary failure, the execution exhibits Local Green, Global Green (LGGG), characterized by $\Delta_E = 0$ (`ZDR`).

Prior volumes of this series analyzed these phenomena retrospectively:
- Volume I formulated evaluated path kernels and conditional gluing hypotheses ($G_1$–$G_4$) on completed paths.
- Volume II established organizational gluing boundaries and carrier mixing obstructions.
- Volume V and Volume VII characterized linear section defects and positive-extension projection residuals on fixed finite tables.

However, real-world practitioner swarms execute asynchronously. Waiting for complete pipeline execution before detecting failure incurs high latency, squanders model inference budgets, and allows corrupted intermediate representations to propagate through downstream stages. 

Volume VIII addresses the problem of **online streaming discovery**: distinguishing composable LGGG from obstructed LGGR incrementally *while* an agentic swarm is running. We establish:
1. Online detection of report-fiber collisions as soon as an incoming state shares a boundary report with an earlier state but diverges on the required query.
2. Online prefix-by-prefix monitoring of signed state drift, separating `every_prefix` constraints from `endpoint` constraints and enabling early stopping.
3. Incremental tracking of pairwise agent handoffs as directed edges in a 1-cochain complex, computing the exact rational $\ell^1$ repair distance and dual witness upon cycle closure.
4. An empirical evaluation resolving the Volume I §9 benchmark specification with live OpenRouter models and deterministic offline replay receipts.

All twelve mathematical theorems are machine-checked in Lean 4.35.0 ([`lean4/LggrVIII.lean`](lean4/LggrVIII.lean)) with zero `sorry` and zero custom axioms, and all algorithmic procedures are verified by reproducible unit tests ([`code/tests/test_lggr_viii_core.py`](code/tests/test_lggr_viii_core.py)).

---

## 2. Online Report-Fiber Collisions & Boundary Insufficiency Monotonicity

Let $X$ denote a state carrier of agent execution states or intermediate handoff artifacts. At runtime, an observer or downstream supervisor monitors execution via a streaming report map $p : X \to A$, while the system must satisfy a protected downstream query or integration contract $q : X \to B$.

**Definition 2.1 (Online Collision and Trace Collision).**
- An explicit *report collision* for $(p, q)$ is a pair $(x, y) \in X \times X$ such that $p(x) = p(y)$ and $q(x) \ne q(y)$ (`LggrVIII.IsCollision p q x y`).
- A finite observed execution trace $T : \mathrm{List}\;X$ contains an explicit collision (`LggrVIII.HasCollision p q T`) if $\exists x \in T, \exists y \in T$ such that $\mathrm{IsCollision}(p, q, x, y)$.

**Theorem 2.1 (`LggrVIII.collision_monotonicity`, Claim C-01).** *Let $p : X \to A$ and $q : X \to B$. If an observed trace $T$ contains an explicit collision, then any extended trace $T'$ containing $T$ ($\forall z, z \in T \to z \in T'$) also contains an explicit collision.*

*Proof.* By hypothesis, there exist $x, y \in T$ with $p(x) = p(y)$ and $q(x) \ne q(y)$. Since $T \subseteq T'$, both $x$ and $y$ belong to $T'$. Thus $(x, y)$ remains an explicit collision witness in $T'$. $\square$

Theorem 2.1 establishes that report-fiber collisions are monotone with respect to trace extension: once a boundary summary is revealed to be insufficient on observed states, no subsequent execution steps can remove the observed collision.

**Theorem 2.2 (`LggrVIII.postprocessing_preserves_streaming_collision`, Claim C-02).** *Let $f : A \to A'$ be any deterministic postprocessing function applied to streaming reports. If $T$ contains an explicit collision for $(p, q)$, then $T$ contains an explicit collision for $(f \circ p, q)$.*

*Proof.* Let $x, y \in T$ satisfy $p(x) = p(y)$ and $q(x) \ne q(y)$. By congruence of equality, $f(p(x)) = f(p(y))$, while the ground-truth values $q(x) \ne q(y)$ remain distinct. Hence $(x, y)$ collides under $f \circ p$. $\square$

Theorem 2.2 confirms that downstream filtering, dimensionality reduction, or lossy tokenization of intermediate reports cannot restore boundary sufficiency.

**Theorem 2.3 (`LggrVIII.streaming_verdict_ceiling`, Claim C-03).** *Assume $B$ has decidable equality. For any report-only streaming evaluator $E : A \to B$ and any trace $T$ containing an explicit collision for $(p, q)$, there exists an observed state $x \in T$ such that $E(p(x)) \ne q(x)$.*

*Proof.* Let $x, y \in T$ be a colliding pair ($p(x) = p(y), q(x) \ne q(y)$). If $E(p(x)) = q(x)$, then $E(p(y)) = E(p(x)) = q(x) \ne q(y)$, so $E$ fails on $y$. Conversely, if $E(p(x)) \ne q(x)$, $E$ fails on $x$. In either case, $E$ disagrees with $q$ on at least one realized state. $\square$

---

## 3. Streaming Prefix-by-Prefix Gluing & Evaluator Defect Tracking ($\Delta_E \in \{-1, 0, 1\}$)

In multi-stage execution, local stage evaluators emit Boolean verdicts $E_1, E_2, \dots, E_k \in \{0, 1\}$. The cumulative local prefix pass indicator after $k$ stages is $L_k = \prod_{i=1}^k E_i$. Meanwhile, an independent downstream integration oracle assesses the end-to-end task output, producing $E_{g,k} \in \{0, 1\}$.

**Definition 3.1 (Streaming Evaluator Defect).** The streaming evaluator defect at step $k$ is defined by:
$$\Delta_E = E_{g,k} - L_k \in \mathbb{Z}.$$

**Theorem 3.1 (`LggrVIII.streaming_evalDefect_partition`, Claim C-04).** *For any Boolean prefix pass $L_k$ and global verdict $E_{g,k}$:*
$$\Delta_E \in \{-1, 0, 1\},$$
*and $\Delta_E = -1$ (`NGD`: local green, global red) if and only if $L_k = \mathrm{true} \wedge E_{g,k} = \mathrm{false}$.*

*Proof.* Verified by exhaustive finite Boolean evaluation across all four pairs $(L_k, E_{g,k}) \in \{0, 1\}^2$ (`decide`). $\square$

### 3.1 Signed Step Telescoping and Online Admissibility

Let $x_0, x_1, \dots, x_n \in \mathbb{Z}$ be configuration states (e.g. cumulative tool resource consumption, memory usage, or safety parameter values). Consecutive transitions have signed step increments $\Delta x_i = x_i - x_{i-1}$.

**Theorem 3.2 (`LggrVIII.streaming_chain_telescoping`, Claim C-05).** *For any initial state $x_0$ and any streaming chain of subsequent transitions $x_1, \dots, x_n$ of arbitrary finite length:*
$$\sum_{i=1}^n (x_i - x_{i-1}) = x_n - x_0.$$

*Proof.* By structural induction on the list of transitions, using linear integer arithmetic (`omega`). $\square$

**Theorem 3.3 (`LggrVIII.online_prefix_strictly_stronger_than_endpoint`, Claim C-06).** *For budget $B \ge 0$, define:*
- $\mathrm{PrefixBounded}(B, H) \iff \forall x \in H,\ |x - x_0| \le B$.
- $\mathrm{EndpointBounded}(B, H) \iff |x_n - x_0| \le B$.

*Then:*
1. $\forall B, H,\ \mathrm{PrefixBounded}(B, H) \implies \mathrm{EndpointBounded}(B, H)$.
2. *For $B = 1$ and excursion history $H = [0, 1, 2, 1]$, $\mathrm{EndpointBounded}(1, H)$ holds ($|1 - 0| \le 1$), whereas $\mathrm{PrefixBounded}(1, H)$ fails ($|2 - 0| = 2 > 1$).*

*Proof.* Part (1) follows because the endpoint $x_n$ belongs to $H$. Part (2) is witnessed by evaluation on $[0, 1, 2, 1]$. $\square$

**Theorem 3.4 (`LggrVIII.prefix_violation_monotonicity`, Claim C-07).** *If a prefix history $H$ violates the budget ($\neg \mathrm{PrefixBounded}(B, H)$), then for any extension $H'$, the concatenated history $H ++ H'$ violates the budget ($\neg \mathrm{PrefixBounded}(B, H ++ H')$).*

*Proof.* By definition, there exists $x \in H$ with $|x - x_0| > B$. For any extension $H'$, $x \in H ++ H'$, so the violation persists. $\square$

Theorem 3.4 establishes the soundness of online early stopping: when an excursion violates a prefix budget mid-flight, halting execution immediately is sound because no future valid transitions can undo the historical excursion.

**Theorem 3.5 (`LggrVIII.streaming_unsigned_report_collision`, Claim C-08).** *Under the unsigned step-magnitude streaming report $p_{\mathrm{unsigned}}(x_0, \dots, x_n) = [|x_1 - x_0|, \dots, |x_n - x_{n-1}|]$ and endpoint query $q_1(H) = \mathbf{1}\{|x_n - x_0| \le 1\}$, the safe history $[0, 1, 0]$ and excursion history $[0, 1, 2]$ produce identical reports $[1, 1]$ while diverging on $q_1$, forming an explicit collision.*

*Proof.* Direct evaluation yields $p_{\mathrm{unsigned}}([0, 1, 0]) = [1, 1] = p_{\mathrm{unsigned}}([0, 1, 2])$, while $q_1([0, 1, 0]) = \mathrm{true}$ and $q_1([0, 1, 2]) = \mathrm{false}$ (`decide`). $\square$

---

## 4. Streaming 1-Cochain Cycle Closure & Exact Rational $\ell^1$ Dual Witnesses

In collaborative multi-agent swarms, agents exchange pairwise commitments or valuations. We formalize streaming handoffs as directed edges $e = (u, v)$ with weight $w_e > 0$ and observed value $h_e \in \mathbb{Q}$ in a 1-cochain complex.

### 4.1 Acyclic Open Trees

Consider an open chain of agent handoffs: Agent A $\to$ Agent B $\to$ Agent C, with handoffs $h_1 = h_{AB}$ and $h_2 = h_{BC}$.

**Theorem 4.1 (`LggrVIII.open_chain_exactness`, Claim C-09).** *For any acyclic streaming chain of 1-cochains $(h_1, h_2) \in \mathbb{Z}^2$:*
1. *The circulation is identically zero: $D_1(h_1, h_2) = 0$.*
2. *The handoff cochain is an exact coboundary under vertex potential $x = (0, h_1, h_1 + h_2)$:*
$$D_0 x = (h_1 - 0, (h_1 + h_2) - h_1) = (h_1, h_2).$$
3. *The $\ell^1$ repair distance vanishes: $\Phi(h) = \|h - D_0 x\|_1 = 0$.*

*Proof.* Direct evaluation and subtraction in $\mathbb{Z}$ (`omega`). $\square$

### 4.2 Incremental Cycle Closure and Dual Witnesses

When a third edge $h_3 = h_{CA}$ arrives, closing the cycle (Agent A $\to$ Agent B $\to$ Agent C $\to$ Agent A), the circulation operator evaluates the closed loop:
$$D_1 h = h_1 + h_2 - h_3.$$

**Theorem 4.2 (`LggrVIII.incremental_cycle_closure_obstruction`, Claim C-10).** *Let $h_1, h_2, h_3 \in \mathbb{Z}$ satisfy $h_1 + h_2 \ne h_3$. Then:*
1. *The circulation is nonzero: $D_1(h_1, h_2, h_3) \ne 0$.*
2. *The dual cochain $z = (1, 1, -1)$ annihilates all coboundaries:*
$$\forall x_0, x_1, x_2 \in \mathbb{Z},\quad 1(x_1 - x_0) + 1(x_2 - x_1) - 1(x_2 - x_0) = 0.$$
3. *For every integer vertex potential $x = (x_0, x_1, x_2) \in \mathbb{Z}^3$, the $\ell^1$ repair residual satisfies:*
$$\|h - D_0 x\|_1 = |h_1 - (x_1 - x_0)| + |h_2 - (x_2 - x_1)| + |h_3 - (x_2 - x_0)| \ge 1.$$

*Proof.* Evaluated using triangle inequality and linear integer arithmetic (`omega`). $\square$

---

## 5. Empirical Multi-Agent Swarm Benchmarks (Volume I §9 Resolution & Tests 1–4)

### 5.1 Volume I §9 Empirical Resolution

Volume I §9 explicitly identified the empirical measurement of NGD, ZDR, and PGD rates across live multi-agent model pipelines as the primary open empirical test of the evaluated path kernel framework. We executed this benchmark suite across $N = 8$ structured programming and specification tasks using OpenRouter model completions (`openai/gpt-4o-mini`, 16 total model completions, well within the 40-completion safety budget).

For each task, an architect subagent emitted a JSON functional specification, and a developer subagent implemented the Python function. Local stage evaluators ($E_1, E_2$) verified schema compliance and syntax validity, while an independent integration oracle ($E_g$) executed automated unit test suites against hidden edge cases.

The live benchmark receipt ([`receipts/empirical_ngd_benchmark.json`](receipts/empirical_ngd_benchmark.json)) records:
- Sample size: $N = 8$ tasks.
- Local Pass Rate: $\mathrm{LPR} = \frac{8}{8} = 1.0$.
- Global Pass Rate: $\mathrm{GPR} = \frac{8}{8} = 1.0$.
- Negative Global Defect Rate: $\mathrm{NGD\_rate} = \frac{0}{8} = 0.0$.
- Zero Defect Rate: $\mathrm{ZDR\_rate} = \frac{8}{8} = 1.0$.
- Positive Global Defect Rate: $\mathrm{PGD\_rate} = \frac{0}{8} = 0.0$.
- Mean evaluator defect: $\bar{\Delta}_E = 0.0$.
- Partition identity: $1 - \mathrm{GPR} = \mathrm{NGD\_rate} + \mathrm{LRGR\_rate} \implies 0 = 0 + 0$ (verified).

All model prompts, completions, and hashes are preserved in the JSON receipt and verified by deterministic offline replay in [`code/tests/test_lggr_viii_core.py`](code/tests/test_lggr_viii_core.py) (`test_empirical_ngd_pgd_rates`, Claim C-13).

### 5.2 Tests 1–4 Structured Live Swarm Experiments

We executed four live multi-agent swarm experiments validating online discovery across distinct operational failure modes ([`code/tests/test_lggr_viii_core.py`](code/tests/test_lggr_viii_core.py), Claim C-14):

1. **Test 1: Online Report-Fiber Collision (`test1_fiber_collision.json`):**
   A multi-stage agent pipeline processed database sorting requests. An intermediate agent emitted an ambiguous summary report `{"key": "user_id", "operation": "sort", "order": "asc"}` for both an arbitrary sort task (Task 1) and a stable-ties requirement sort task (Task 2). Downstream integration succeeded for Task 1 ($E_g = 1$) but failed for Task 2 ($E_g = 0$). `StreamingFiberMonitor` detected the collision at step index 1, immediately transitioned the contract from `COMPOSABLE_LGGG` to `OBSTRUCTED_LGGR`, and emitted an `online_collision.v1` receipt.

2. **Test 2: Online Prefix vs. Endpoint Excursion (`test2_prefix_breach.json`):**
   A multi-step agent tool chain operated under budget policy `every_prefix` with maximum total drift $B = 5$. Transition increments $\Delta x = [3, 4, -4]$ produced state trajectory $[0, 3, 7, 3]$. At step index 1, cumulative drift reached $S_2 = 7 > 5$. `StreamingAuditMonitor` fired an immediate mid-flight alert (`PREFIX_BUDGET_EXCEEDED`) and transitioned to `OBSTRUCTED_LGGR`, whereas an unmonitored endpoint check would have erroneously reported success ($S_3 = 3 \le 5$).

3. **Test 3: Incremental 1-Cochain Cycle Closure (`test3_cochain_cycle.json`):**
   A cyclic 3-agent review swarm (Agent A $\to$ Agent B $\to$ Agent C $\to$ Agent A) exchanged rational valuations $h_{AB} = 1/2$, $h_{BC} = 1/3$, and $h_{CA} = 1/2$. `StreamingCochainMonitor` verified exactness on edges 0 and 1, then detected cycle closure on edge 2 with circulation defect $D_1 h = 4/3 \ne 0$. The monitor computed the certified exact rational $\ell^1$ repair distance $\Phi(h) = 4/3$ and dual witness $z = [1, 1, 1]$.

4. **Test 4: Composable LGGG Certification (`test4_composable_lggg.json`):**
   The sorting swarm was updated to enforce a boundary-sufficient schema retaining precondition flags (`preserve_ties: true`). `StreamingFiberMonitor` processed both states without collision, maintained $\Delta_E = 0$ across all steps, and certified final contract status `COMPOSABLE_LGGG`.

### 5.3 Formal Gluing and Defect Theorems

**Theorem 5.1 (`LggrVIII.boundary_sufficient_gluing_certifies_lggg`, Claim C-11).** *Under conditional gluing hypotheses G1–G4 ($E_g = E_1 \wedge E_2$), if all local stage checks pass ($E_1 = \mathrm{true} \wedge E_2 = \mathrm{true}$), then global integration passes ($E_g = \mathrm{true}$) and the evaluator defect vanishes ($\Delta_E = 0$), certifying composable LGGG.*

*Proof.* Direct truth-table substitution (`decide`). $\square$

**Theorem 5.2 (`LggrVIII.boundary_insufficiency_forces_defect`, Claim C-12).** *If a realized report fiber contains an explicit collision between states $x$ and $y$ that both pass local stage checks ($E_l(x) = E_l(y) = \mathrm{true}$) but disagree on global integration ($E_g(x) \ne E_g(y)$), then at least one branch incurs the LGGR obstruction defect $\Delta_E = -1$ (NGD).*

*Proof.* Since $E_g(x) \ne E_g(y)$ and $E_g \in \{0, 1\}$, exactly one state has $E_g = 0$. For that state, $E_l = 1 \wedge E_g = 0 \implies \Delta_E = 0 - 1 = -1$ (`decide`). $\square$

---

## 6. Boundary-Sufficient Runtime Guard Design for Practitioner Swarms

Based on the theoretical and empirical results, we outline an architectural pattern for integrating online LGGG vs. LGGR guards into practitioner swarms:

```
                  Incoming Agent / Tool Step
                              │
                              ▼
               ┌──────────────────────────────┐
               │   1. Fiber Collision Guard   │
               │  (StreamingFiberMonitor)     │
               └──────────────┬───────────────┘
                              │ No collision
                              ▼
               ┌──────────────────────────────┐
               │    2. Prefix Drift Guard     │
               │  (StreamingAuditMonitor)     │
               └──────────────┬───────────────┘
                              │ Prefix bounded
                              ▼
               ┌──────────────────────────────┐
               │    3. Cochain Cycle Guard    │
               │  (StreamingCochainMonitor)   │
               └──────────────┬───────────────┘
                              │ Circulation = 0
                              ▼
                     Composable LGGG Pass
```

### 6.1 Three Guard Layers

1. **Fiber Collision Guard:** Maintains hash maps of intermediate boundary summaries against declared downstream invariants. When two distinct states produce identical reports but diverge downstream, the contract immediately halts or requests summary refinement.
2. **Prefix Drift Guard:** Monitors resource, safety, and token budgets under the `every_prefix` scope. Early halts fire upon the first exceeding transition, preventing wasted downstream inference.
3. **Cochain Cycle Guard:** Tracks circular multi-agent reviews and handoffs. Evaluates coboundary consistency and emits exact rational $\ell^1$ dual witnesses when handoff promises are inconsistent.

---

## 7. Related Work & Discussion

1. **Runtime Verification (RV):** Classical runtime verification focuses on temporal logic properties (LTL/MTL) over linear traces. The LGGR streaming framework complements RV by formalizing fiber-descent insufficiency, evaluator defects $\Delta_E$, and cohomological obstructions over multi-agent handoff graphs.
2. **Evaluated Path Kernels and Monograph Series:** While Volumes I–VII developed foundational mathematical structures, Volume VIII connects these concepts directly to running multi-agent swarms with zero external dependencies and deterministic offline replay.
3. **Multi-Agent Alignment and Consensus:** Traditional Byzantine consensus algorithms assume fault-tolerant message passing on fixed networks. LGGR cochain monitoring provides quantitative $\ell^1$ repair distances and dual certificates of inconsistency without requiring heavy consensus rounds.

---

## 8. Claim Hygiene Summary

In adherence to the Claim Hygiene Rule, we summarize the empirical and theoretical findings of Volume VIII:

1. **What this paper supports:**
   - Supports that report-fiber collisions are monotone under streaming trace extensions and invariant under deterministic postprocessing.
   - Supports that online every-prefix admissibility is strictly stronger than endpoint admissibility, and that prefix budget violations persist monotonically under all continuations.
   - Supports that acyclic streaming handoff trees have exact coboundary potentials and zero $\ell^1$ repair distance, while closing an inconsistent cycle yields nonzero circulation certified by an explicit dual witness.
   - Supports that in the tested multi-stage programming tasks ($N = 8$), live OpenRouter model completions achieved $\mathrm{LPR}=1, \mathrm{GPR}=1, \mathrm{NGD}=0, \mathrm{ZDR}=1, \mathrm{PGD}=0$, with verified deterministic offline replay receipts.
   - Supports that runtime monitors detect fiber collisions, prefix budget breaches, and cycle closure defects mid-flight in the declared test scenarios.

2. **What this paper does not support:**
   - Does not support that LLM swarms will never exhibit NGD defects in untested domains or with other prompts.
   - Does not support that discrete mathematical formalizations of toy state chains eliminate physical risks in general autonomous AI deployments.
   - Does not support that report-fiber sufficiency over observed traces ensures sufficiency over unseen states.

3. **Narrowest defensible claim:**
   - Under the declared discrete relational definitions, all 12 formal theorems in `lean4/LggrVIII.lean` are machine-checked under Lean 4.35.0 standard core foundations with zero custom axioms and zero `sorry`; the standalone Python module `lggr_viii_core.py` reproduces these derivations with exact rational arithmetic; and the live OpenRouter benchmark receipts record empirical zero-defect performance across $N = 8$ tasks and verify online collision, excursion, and cycle detection across Tests 1–4.

4. **Next test needed:**
   - Execute large-scale adversarial stress tests on multi-agent swarms with diverse tool APIs and complex multi-cycle topologies to measure empirical NGD rates under intentional prompt injection and partial tool failures.

---

## 9. Reproduction and Verification Commands

From the repository root:

```console
# 1. Run Volume VIII standalone companion Python tests:
python -m unittest papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/code/tests/test_lggr_viii_core.py -v

# 2. Build and verify mirrored Lean 4 package:
cd papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/lean4
lake build
```
