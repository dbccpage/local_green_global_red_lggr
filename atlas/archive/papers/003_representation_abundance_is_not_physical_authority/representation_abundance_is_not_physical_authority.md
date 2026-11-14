<div align="center"># Representation Abundance Is Not Physical Authority: Finite Selectors, Witnessed Differences, and the Local-Green Boundary</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">2026-10-16</div>
<div align="center">Version 2.2.0</div>

## Abstract

A large family of representations need not distinguish its members observationally. For a finite candidate family, we characterize the properties recoverable from an observation map and show that adding candidates without adding observable profiles increases the average fiber size. A rational graph example separates local tolerance checks from global integrability and gives a sharp cycle-holonomy bound. A finite selector then distinguishes candidate survival from unique selection relative to declared alternatives and measurements. The results do not authenticate the measurements or establish that the candidate family is exhaustive. Written proofs, finite Python checks, and supporting Lean lemmas are identified separately.

**Why a researcher should care.** Observational indistinguishability concerns what evidence can recover. It need not prevent identification of a property shared by all surviving models. Keeping those questions separate makes both mathematical claims and empirical selection more precise.

## 1. Introduction and the Representation-Authority Gap

### 1.1 Generative Plenitude vs. Empirical Selection

A central feature of modern theoretical physics is the discovery of theories that permit a vast cardinality of internal solutions:

- **String Theory Compactifications:** Flux compactifications on Calabi-Yau manifolds yield an estimated $10^{500}$ or more metastable vacua, each corresponding to distinct low-energy effective field theories with differing gauge groups, particle spectra, and cosmological constants.

- **Multiverse Cosmologies:** Eternal inflation scenarios generate infinite ensembles of causally disconnected pocket universes exhibiting varied physical parameters.

- **Maximal Computational Plenitude:** Generative systems exploring the totality of computational rules, evolutions, or discrete hypergraphs contain, by construction, representations of computable histories under a specified encoding and rule class. No universality claim is proved here.

Such programs possess undeniable mathematical richness. They generate intricate geometric structures, provide deep dualities between seemingly disparate areas of mathematics, and model complex systems. However, a persistent conceptual confusion deadlocks methodological debates:

- Critics characterize such frameworks as "unfalsifiable" or "vacuous" because they can accommodate nearly any observed datum after the fact.

- Defenders respond that the framework is "mathematically fertile" and possesses "broad representational capacity."

This paper supplies a finite, executable presentation of the distinction between representational availability, observational discrimination, and family-relative selection. This contribution does not assert that the surrounding literature lacks such distinctions; Douglas (2003), for example, explicitly studies ensembles in relation to predictive power.

### 1.2 The Core Principle: Plenitude Is Proposal Generation

We formulate the core principle of this monograph:

$$\boxed{\begin{array}{c}
\text{Membership in an abundant representation space alone} \\
\text{does not establish unique selection within a declared family and evidence record.}
\end{array}}$$

Vast representational plenitude does not defeat a theory mathematically. Instead, it places the theory in a specific epistemic category: it is an abundant reservoir of candidate descriptions. But membership of a specific candidate $x$ within a representation space $\mathcal{S}$ does not confer physical authority upon $x$. Unique model selection requires discrimination among declared alternatives. Identification of a target property is a different question: several surviving models may agree on that property. Proposition 2.3 below states when a property can be recovered from observations.

### 1.3 Scope

The results concern declared finite families, observation maps, and rational graph data. A family-relative selection is conditional on the supplied alternatives, measurements, and tolerances. Measurement authenticity and adequacy of the model family are separate questions.

---

## 2. Witnessed Difference Quotients and Observer Equivalence

Following the foundational framework of the *Witnessed Difference Programme* (Paper 000), we model candidate models and physical observers without presupposing continuous manifolds, background spacetimes, or unexamined state vectors.

### 2.1 Candidate Spaces and Observable Projections

Let $\mathcal{S}$ denote a finite set of candidate models (e.g., discrete vacua, rule configurations, or parameters):

$$\mathcal{S} = \{s_1, s_2, \ldots, s_N\}.$$

Let $\mathcal{O}$ denote an **observer evaluation operator** that maps each candidate $s \in \mathcal{S}$ to a tuple of observable predictions in an observable space $\mathcal{E}$:

$$\mathcal{O}: \mathcal{S} \to \mathcal{E}.$$

For an observer equipped with $m$ discrete observables $\{o_1, o_2, \ldots, o_m\}$, the evaluation map is given by:

$$\mathcal{O}(s) = \big(o_1(s), o_2(s), \ldots, o_m(s)\big) \in \mathbb{Q}^m.$$

### 2.2 The Observed Difference Quotient and Blind Kernels

Two candidates $s_1, s_2 \in \mathcal{S}$ are said to be **indistinguishable to observer $\mathcal{O}$** if their predicted observable profiles coincide:

$$s_1 \sim_{\mathcal{O}} s_2 \iff \mathcal{O}(s_1) = \mathcal{O}(s_2).$$

The equivalence relation $\sim_{\mathcal{O}}$ defines the **observer kernel**:

$$\ker(\mathcal{O}) = \{(s_1, s_2) \in \mathcal{S} \times \mathcal{S} \mid \mathcal{O}(s_1) = \mathcal{O}(s_2)\}.$$

The space of distinguishable configurations accessible to observer $\mathcal{O}$ is the quotient set:

$$\mathcal{S} / \ker(\mathcal{O}) = \{[s]_{\mathcal{O}} \mid s \in \mathcal{S}\}.$$

**Mathematical proof:** the argument below. **Mechanized statement:** observation_decision_agrees establishes the same function-composition equality for arbitrary types. The Python helper checks finite instances.

**Proposition 2.1 (Observer Blindness).** *Let $\mathcal{O}$ be an observer evaluation map. If candidates $s_1, s_2 \in \mathcal{S}$ satisfy $s_1 \sim_{\mathcal{O}} s_2$ with $s_1 \ne s_2$, then no computation or decision procedure utilizing solely the outputs of $\mathcal{O}$ can distinguish $s_1$ from $s_2$.*

*Proof.* Any decision procedure $D$ acting on observation data is a function of the form $D: \mathcal{E} \to \mathbb{T}$. For any $s_1, s_2$ with $\mathcal{O}(s_1) = \mathcal{O}(s_2) = e \in \mathcal{E}$, we have:

$$D(\mathcal{O}(s_1)) = D(e) = D(\mathcal{O}(s_2)).$$

Thus the outputs of $D$ on $s_1$ and $s_2$ are identical. $\blacksquare$

### 2.3 The Underdetermination Metric

For any finite nonempty candidate family $F \subset \mathcal{S}$ and observer evaluation map $\mathcal{O}: F \to \mathcal{E}$, we define the **Underdetermination Ratio** $U(F, \mathcal{O})$ as the average fiber size:

$$U(F, \mathcal{O}) = \frac{|F|}{|F / \ker(\mathcal{O})|}.$$

This numerical ratio requires finite nonempty candidate sets; division by infinite cardinals is not treated as an exact rational statistic.

- If $U(F, \mathcal{O}) = 1$, the observer's observables fully separate the candidate family: every candidate possesses a distinct observable profile.

- If $U(F, \mathcal{O}) > 1$, multiple internal candidates map to identical observable profiles.

**Mathematical proof:** the finite-family argument below. **Supporting mechanized component:** plenitude_inflation is a natural-number multiplication inequality with positive denominator. **Not yet mechanized:** finite families, observation-preserving inclusion, quotient cardinalities, and rational ratios. Python checks unchanged retained model content, identical profile sets, and exact ratios.

**Theorem 2.2 (Plenitude Inflation).** *Let $F$ and $F'$ be finite nonempty sets of candidates with $F \subsetneq F'$, and let $\mathcal{O}': F' \to \mathcal{E}$ be an extended observer evaluation map whose restriction to $F$ equals $\mathcal{O}$. If the extension introduces no new observable profiles, $\mathcal{O}'(F') = \mathcal{O}(F)$, then:*

$$U(F', \mathcal{O}') > U(F, \mathcal{O}).$$

*Proof.* Because $\mathcal{O}'(F') = \mathcal{O}(F)$, the number of distinguishable equivalence classes in the denominator is unchanged:

$$|F' / \ker(\mathcal{O}')| = |\mathcal{O}'(F')| = |\mathcal{O}(F)| = |F / \ker(\mathcal{O})|.$$

Meanwhile, the numerator strictly increases because $F \subsetneq F'$: $|F'| > |F|$. Therefore:

$$U(F', \mathcal{O}') = \frac{|F'|}{|F' / \ker(\mathcal{O}')|} = \frac{|F'|}{|\mathcal{O}(F)|} > \frac{|F|}{|\mathcal{O}(F)|} = U(F, \mathcal{O}). \quad \blacksquare$$

It is essential to emphasize that keeping the observer or its list of observable coordinates fixed is not sufficient by itself for strict inflation. A fixed list of rational observables can take arbitrarily many distinct values on new candidates; if an added candidate introduces a new observable profile in $\mathcal{E}$, the denominator increases and the average fiber size can decrease. For example, if $F$ contains 100 candidates all predicting $x = 0$, $U(F, \mathcal{O}) = 100/1 = 100$. If a 101st candidate is added predicting $x = 1$ under the same observable, $U(F', \mathcal{O}') = 101/2 = 50.5$. Strict inflation holds under the precise hypothesis of Theorem 2.2: the expanded family introduces no new distinguishing observable profiles ($\mathcal{O}'(F') = \mathcal{O}(F)$).

In string theory and multiverse discussions, the astronomical figure of $10^{500}$ vacua serves as motivational context for vast generative plenitude; it is not an input mathematically validated by this finite theorem, since a fixed list of observables does not guarantee that new vacua produce no new observable signatures.

### 2.4 Identifying a Property Without Selecting a Model

**Proposition 2.3 (Observation Factorization).** Let F be a declared family, $\mathcal O:F\to E$ an observation map, and $P:F\to T$ a target property. There exists $D:\mathcal O(F)\to T$ with $P=D\circ\mathcal O$ if and only if

$$\mathcal O(s)=\mathcal O(t)\ \Longrightarrow\ P(s)=P(t)\qquad(s,t\in F).$$

*Proof.* If $P=D\circ\mathcal O$, equality of observations implies equality of property values by substitution. Conversely, for each $e\in\mathcal O(F)$ define $D(e)$ as the common value of $P$ on the nonempty fiber $\mathcal O^{-1}(e)$. Fiber constancy makes this value well-defined, and $D(\mathcal O(s))=P(s)$. $\blacksquare$

**Proof status:** written proof; not mechanized in Lean. Recoverability is relative to the declared family and observation map. It does not certify the family as exhaustive or the measurements as authentic.

In Scenario A of Section 5.1, both survivors have three generations, so that property is identified within the survivor family even though the model is not uniquely selected. In Section 3, retaining only local acceptance flags identifies neither the exact holonomy nor its vanishing: the zero cochain and an edge-simple false-green witness have the same all-green profile but different holonomies. Holonomy is not constant on that observation fiber, so Proposition 2.3 rules out its recovery from those flags alone.

---

## 3. The Local-Green Global-Red Boundary

Local tolerance checks need not determine whether edge data integrate to vertex values. The following graph calculation gives a finite counterexample. Its application to a physical theory requires a separately justified encoding.

### 3.1 Discrete Cochain Complexes of Local Evaluations

Consider a finite loop-free graph $G = (V, E)$ with one chosen stored orientation per undirected edge and no duplicate edges. The graph may represent local observation patches or theoretical sectors only when that correspondence is separately supplied.

A signed traversal $(u,v,s)$, $s\in\{-1,+1\}$, is normalized to the stored edge and its orientation sign before reading its cochain value or tolerance. Thus $(u,v,+1)$ and $(v,u,-1)$ describe the same step. Cochains and tolerances are functions on exactly the stored-edge domain; extra reverse entries are rejected. A closed walk may repeat edges. An edge-simple closed cycle visits each stored edge at most once. Evaluator soundness and the per-traversal upper bound hold on closed walks; the false-green and sharpness constructions below use edge-simple closed cycles.

- $C^0(V, \mathbb{Q})$ is the space of 0-cochains: global candidate field assignments $f: V \to \mathbb{Q}$.

- $C^1(E, \mathbb{Q})$ is the space of 1-cochains: edge transitions or local comparative discrepancies $\omega: E \to \mathbb{Q}$.

For this graph regarded as a one-dimensional cell complex, $C^2=0$ and $Z^1=C^1$. The standard coboundary operator $d_0: C^0(V, \mathbb{Q}) \to C^1(E, \mathbb{Q})$ is defined on directed edges $e = (u, v) \in E$ by:

$$(d_0 f)(u, v) = f(v) - f(u).$$

Each edge $e \in E$ is equipped with a local acceptance interval (or tolerance set) $K_e = [-\tau_e, \tau_e] \cap \mathbb{Q}$, where $\tau_e \ge 0$. Note that for $\tau_e > 0$, $K_e$ is a bounded interval, not a linear subspace (it is not closed under scalar multiplication).

A 1-cochain $\omega \in C^1(E, \mathbb{Q})$ is defined as **Local-Green** if every local edge evaluation satisfies the local tolerance:

$$\text{Local-Green}(\omega) \iff \forall e \in E,\quad \omega(e) \in K_e.$$

### 3.2 Evaluator Soundness Theorem

**Mathematical proof:** rational graph telescoping below. **Supporting mechanized component:** cycle_coboundary_holonomy_zero telescopes a closed list of integer values. **Not yet mechanized:** rational graph cochains, signed traversal correspondence, or the quotient group H¹.

**Theorem 3.1 (Evaluator Soundness).** *Let $G = (V, E)$ be a finite graph and let $C = (e_1, e_2, \ldots, e_k)$ be any closed directed cycle in $G$. For any 0-cochain $f \in C^0(V, \mathbb{Q})$, the cycle holonomy of the exact coboundary $d_0 f$ is identically zero:*

$$\oint_C d_0 f = \sum_{i=1}^k (d_0 f)(e_i) = 0.$$

*Consequently, every exact coboundary represents the trivial cohomology class in the first cohomology quotient space $H^1(G, \mathbb{Q}) = Z^1(G, \mathbb{Q}) / \operatorname{im}(d_0)$:*

$$[d_0 f] = 0 \in H^1(G, \mathbb{Q}).$$

*Proof.* Let the cycle vertices be $(v_1, v_2, \ldots, v_k, v_{k+1} = v_1)$ with edges $e_i = (v_i, v_{i+1})$. Then:

$$\oint_C d_0 f = \sum_{i=1}^k (f(v_{i+1}) - f(v_i)) = (f(v_2) - f(v_1)) + (f(v_3) - f(v_2)) + \cdots + (f(v_1) - f(v_k)) = 0.$$

The telescoping sum vanishes identically. $\blacksquare$

### 3.3 The False-Green Theorem

The next result concerns edge tolerances and global integrability on a finite graph. It does not establish that any particular physical framework exhibits this obstruction.

**Mathematical proof:** the rational edge-simple-cycle construction below. **Supporting mechanized components:** false_green_holonomy and false_green_local establish integer positivity and local absolute-value inequalities. **Not yet mechanized:** the rational half-minimum witness or its embedding in a graph. Python constructs and checks that witness.

**Theorem 3.2 (False-Green Obstruction).** *Let $G = (V, E)$ contain at least one edge-simple closed oriented cycle $C = ((e_1, s_1), (e_2, s_2), \ldots, (e_k, s_k))$ of length $k \ge 3$, where each $e_i \in E$ and $s_i \in \{-1, +1\}$. Suppose each edge in $C$ has a strictly positive local tolerance $\tau_{e_i} \in \mathbb{Q}_{> 0}$. Then there exists a rational-valued 1-cochain $\omega \in C^1(E, \mathbb{Q})$ such that:*

1. *$\omega$ is Local-Green on every edge: $|\omega(e)| \le \tau_e$ for all $e \in E$ (specifically, $|\omega(e)| < \tau_e$ for all $e \in C$).*

2. *$\omega$ is Global-Red: the global cycle holonomy is strictly non-zero:*

$$\oint_C \omega = \Phi \ne 0.$$

*Therefore, $\omega \notin \operatorname{im}(d_0)$; no global 0-cochain assignment $f \in C^0(V, \mathbb{Q})$ can generate $\omega$.*

*Proof.* Since each $\tau_{e_i}$ is a strictly positive rational number, their finite minimum $\tau_{\min} = \min_{1 \le i \le k} \tau_{e_i}$ is strictly positive and rational: $\tau_{\min} \in \mathbb{Q}_{> 0}$. Choose an explicitly rational constant:

$$\epsilon = \frac{1}{2} \tau_{\min} \in \mathbb{Q}_{> 0},$$

so that $0 < \epsilon < \min_{e \in C} \tau_e$. Define the 1-cochain $\omega \in C^1(E, \mathbb{Q})$ by assigning signed values according to the cycle traversal orientation:

- For each edge $e \in E$ traversed in $C$ with sign $s(e) \in \{-1, +1\}$, set $\omega(e) = s(e) \epsilon$.

- For any edge $e \notin C$, set $\omega(e) = 0$.

By construction, for every edge $e \in C$:
$$|\omega(e)| = |s(e) \epsilon| = \epsilon < \tau_{\min} \le \tau_e.$$
For every edge $e \notin C$:
$$|\omega(e)| = 0 \le \tau_e.$$
Thus Condition 1 (Local-Green) is satisfied across all of $E$.

However, the global cycle holonomy evaluates to:

$$\oint_C \omega = \sum_{i=1}^k s_i \omega(e_i) = \sum_{i=1}^k s_i (s_i \epsilon) = \sum_{i=1}^k s_i^2 \epsilon = \sum_{i=1}^k \epsilon = k \epsilon.$$

Because $k \ge 3$ and $\epsilon \in \mathbb{Q}_{> 0}$, the accumulated holonomy is strictly positive and rational: $\Phi = k\epsilon \in \mathbb{Q}_{> 0}$, so $\Phi \ne 0$. By Theorem 3.1, any exact coboundary $d_0 f$ must have zero cycle holonomy. Because $\oint_C \omega \ne 0$, $\omega$ cannot be the coboundary of any global assignment $f$. The field is globally obstructed (Global-Red). $\blacksquare$

*Remark (Finite Counterexample Scope).* Theorem 3.2 provides a finite discrete counterexample to local-to-global inference: local satisfaction of tolerances across every edge does not imply the existence of a global potential $f$. Applying this principle to gauge anomalies, supersymmetry, or a particular physical theory requires a declared correspondence mapping field configurations to cochains, which this discrete graph model does not construct.

### 3.4 Cycle Defect Bound

While local-green evaluations on edge acceptance intervals $K_e = [-\tau_e, \tau_e] \cap \mathbb{Q}$ do not certify vanishing holonomy (since both the zero cochain and nonzero holonomy cochains pass local tolerances), they do impose an explicit, computable upper bound on the accumulated cycle defect. On a declared oriented cycle $C$, the global holonomy is bounded by the sum of local edge tolerances:

**Mathematical proof:** the rational graph argument below. **Supporting mechanized components:** cycle_defect_bound bounds a signed integer list with natural-number tolerances; sharp_cycle_attains uses an all-positive-sign list. **Not yet mechanized:** the graph-to-list correspondence, rational tolerances, or arbitrary graph orientations.

**Corollary 3.3 (Cycle Defect Bound).** *Let $G = (V, E)$ be a finite graph, and let $C = (e_1, e_2, \ldots, e_k)$ be an edge-simple closed oriented cycle with local edge tolerances $\tau_e \ge 0$. Any Local-Green 1-cochain $\omega \in C^1(E, \mathbb{Q})$ satisfies:*

$$\left|\oint_C \omega\right| \le \sum_{e \in C} \tau_e.$$

*Furthermore, this signed tolerance-sum bound is sharp on the declared cycle: assigning $\omega(e) = \operatorname{sgn}(e) \tau_e$ for each oriented edge $e \in C$ attains the upper bound $\sum_{e \in C} \tau_e$.*

*Proof.* By definition of Local-Green, $|\omega(e)| \le \tau_e$ for all $e \in E$. Applying the triangle inequality to the cycle sum:

$$\left|\oint_C \omega\right| = \left|\sum_{i=1}^k \operatorname{sgn}(e_i) \omega(e_i)\right| \le \sum_{i=1}^k |\omega(e_i)| \le \sum_{e \in C} \tau_e.$$

Setting $\omega(e_i) = \operatorname{sgn}(e_i) \tau_{e_i}$ yields $\oint_C \omega = \sum_{e \in C} \tau_e$, demonstrating sharpness, including when every tolerance is zero. $\blacksquare$

The same triangle inequality bounds any closed walk by its per-traversal tolerance sum, counting repeated edges. Sharpness of that sum is not asserted for general walks: a backtracking walk has zero holonomy for every cochain.

*Remark (Information Loss vs. Defect Bounding).* Local consistency fails to certify vanishing holonomy ($\oint_C \omega = 0$): both the zero field $\omega = 0$ (exact) and non-zero drift fields (such as $\omega(e) = 1/10$ with $\tau_e = 1/5$ on the hexagon, yielding $\oint_C \omega = 3/5$) pass every local check. This constitutes the valid information-loss statement. However, local data explicitly bounds the global defect by $\sum_{e \in C} \tau_e$ (which equals $6 \times (1/5) = 6/5$ for the hexagon). A measured global cycle witness is required not to bound the defect, but to certify whether or not the defect vanishes.

---

## 4. The Finite Terminal Selector

Having established that representation abundance inflates underdetermination and that local consistency does not guarantee global realizability, we now formulate the operational mechanism required to establish empirical selection.

### 4.1 The Operational Quadruple $(F, e, V, \tau)$

Physical authority is not an inherent property of a candidate model, Lagrangian, or vacuum state. In operational terms, selection is a property of a declared candidate family evaluated against certified empirical evidence.

We define a **Finite Terminal Selector** as a quadruple:

$$\mathcal{T} = (F, e, V, \tau),$$

where:

1. **$F \subset \mathcal{S}$ (Declared Finite Family):** A finite, nonempty set of candidate models with unique candidate identifiers: $F = \{s_1, s_2, \ldots, s_n\}$.

2. **$e \in \mathcal{E}_{\text{finite}}$ (Finite Evidence Record):** A finite set of certified observational measurements:

$$e = \{(o_j, v_j, \delta_j)\}_{j=1}^m,$$

where $o_j$ is the observable name, $v_j \in \mathbb{Q}$ is the measured central value, and $\delta_j \in \mathbb{Q}_{\ge 0}$ is the explicit measurement tolerance.

*Explicit Premise Note (External Certification):* The operational selector takes certified evidence as an explicit input premise. The computational selector $\mathcal{T}$ verifies candidate predictions against declared values and tolerances in $e$, but does not independently verify laboratory calibration, detector provenance, or external certification certificates. The designation of $e$ as "certified evidence" is an upstream boundary condition; if the evidence record itself is unverified, corrupt, or fabricated, downstream selection inherits that defect without detection.

3. **$V: \mathcal{E}_{\text{finite}} \times \mathcal{S} \to \mathcal{R}$ (Deterministic Candidate Verifier):** A computable procedure that evaluates candidate $s \in F$ against evidence record $e$, producing an evaluation receipt $R(s) = V(e, s)$. The receipt records candidate identity, the supplied evidence-record identifier, completeness (whether $s$ provides a prediction for every required observable $o_j$ in $e$), discrepancies $\Delta_j(s) = |o_j(s) - v_j|$, maximum discrepancy, and candidate-level consistency: $\Delta_j(s) \le \delta_j$ for every required $j$. Candidate receipts take candidate-level statuses:

$$\mathbb{T}_{\text{candidate}} = \{\mathsf{Survivor}, \mathsf{Refuted}, \mathsf{Refused}\}.$$

- $\mathsf{Refused}$: Incomplete input (empty evidence record $e$, or missing prediction for any required observable $o_j$).

- $\mathsf{Refuted}$: Complete predictions, but $\exists j \in \{1, \ldots, m\}: \Delta_j(s) > \delta_j$.

- $\mathsf{Survivor}$: Complete predictions and $\forall j \in \{1, \ldots, m\}: \Delta_j(s) \le \delta_j$.

4. **$\tau: \mathcal{E}_{\text{finite}} \times \mathcal{P}_{\text{fin}}(\mathcal{S}) \times \mathcal{R}^{|F|} \to \mathbb{T}_{\text{family}}$ (Family Terminalizer):** A decision mapping that evaluates the evidence record, declared family, and candidate receipts to produce a family-level outcome:

$$\tau\bigl(e, F, (V(e, s))_{s \in F}\bigr) \in \mathbb{T}_{\text{family}} = \{\mathsf{Accepted}, \mathsf{Underdetermined}, \mathsf{Refuted}, \mathsf{Refused}\}.$$

### 4.2 The Survivor Set and Terminal Taxonomy

For complete inputs, we define the **survivor set** $A_{F,e} \subseteq F$:

$$A_{F,e} = \{s \in F \mid \Delta_j(s) \le \delta_j \text{ for every required } j \in \{1, \ldots, m\}\}.$$

The family terminalizer $\tau\bigl(e, F, (V(e,s))_{s\in F}\bigr)$ produces four mutually exclusive family-level outcomes:

- **$\mathsf{Refused}$:** If the evidence record is empty ($e = \emptyset$), the declared family is empty ($F = \emptyset$), duplicate candidate identifiers exist within $F$, or any candidate $s \in F$ has an incomplete receipt (missing a prediction for a required observable). In the reference implementation, duplicate candidate identifiers in a declared family raise `ValueError`, rejecting execution before evaluation. Incomplete inputs are neither refutations nor acceptances.

- **$\mathsf{Refuted}$:** If all candidates have complete predictions, but none satisfies the tolerances:

$$A_{F,e} = \emptyset \implies \tau(e, F, \cdot) = \mathsf{Refuted}.$$

- **$\mathsf{Accepted}$ (Family-Relative Selection):** If all candidates have complete predictions and exactly one candidate survives:

$$A_{F,e} = \{s^*\} \implies \tau(e, F, \cdot) = \mathsf{Accepted}.$$

In this case, candidate $s^*$ is uniquely selected relative to $(F,e)$; its candidate receipt remains $\mathsf{Survivor}$. The Python FamilySelectionResult records the evidence-record identifier, ordered declared candidate identifiers, family verdict, selected candidate identifier when unique, and candidate receipts. Evidence identifiers are labels, not cryptographic certification. Callers use result.verdict and result.receipts; the previous tuple-unpacking return is replaced.

- **$\mathsf{Underdetermined}$:** If all candidates have complete predictions and multiple distinct candidates survive:

$$|A_{F,e}| > 1 \implies \tau(e, F, \cdot) = \mathsf{Underdetermined}.$$

In the underdetermined state, every survivor candidate $s \in A_{F,e}$ remains an uneliminated proposal within $F$. None is selected over any other by evidence $e$.

### 4.3 The Non-Promotion Principle and Scope of Acceptance

**Mathematical argument:** extending a complete family with one further survivor changes its survivor count from one to two. **Supporting mechanized component:** unique_acceptance_breaks establishes this count identity for Boolean lists. **Not yet mechanized:** candidate models, evidence semantics, or family terminalization. Python checks the declared family extension.

We summarize this operational boundary in the **Non-Promotion Principle**:

$$\boxed{
s \in \mathcal{S} \quad\not\Longrightarrow\quad A_{F,e} = \{s\}.
}$$

Membership of a candidate $s$ within a vast representation space $\mathcal{S}$ does not imply that $s$ is uniquely selected relative to any declared family $F$ and evidence record $e$.

Furthermore, unique acceptance is an explicitly family-relative and evidence-relative outcome: $A_{F,e} = \{s\}$. It means that candidate $s$ is the sole survivor among the declared alternatives in $F$ that satisfies evidence record $e$ within tolerances $\delta$.

Crucially, if the family $F$ can be chosen arbitrarily, each of two empirically indistinguishable survivors $s_1 \sim_{\mathcal{O}} s_2$ could be made uniquely accepted solely by declaring a singleton family $F_1 = \{s_1\}$ or $F_2 = \{s_2\}$. Deleting competing candidates supplies no new empirical information. The stated selection rule therefore cannot establish exclusive physical authority between them.

Selection is strictly relative to a declared candidate family $F$ and evidence record $e$. It does not establish that $F$ exhausts physical alternatives, that all representation differences between candidates correspond to physically realized distinctions, or that the author-defined label 'accepted' constitutes general empirical validity. We therefore separate the finite membership/selection non-implication ($s \in \mathcal{S} \not\Longrightarrow A_{F,e} = \{s\}$) from author-defined policy terminology such as 'authority'.

---

## 5. Concrete Computational Realizations and Worked Examples

All models and examples discussed below are implemented in Python in `code/mod_representation_abundance_core.py` and validated on the stated examples across 33 core unit and regression tests in `code/tests/test_representation_abundance.py`.

### 5.1 Worked Example 1: Toy Landscape Vacua

Consider a toy landscape containing 5 distinct vacua $\mathcal{S} = \{V_1, V_2, V_3, V_4, V_5\}$ characterized by 4 exact rational observables:

1. $\Lambda$: cosmological constant analogue.

2. $G_{\text{rank}}$: rank of the low-energy gauge group.

3. $N_{\text{gen}}$: number of fermion generations.

4. $M_H^2$: scalar Higgs mass squared parameter.

The predicted values for each vacuum are tabulated below:

| Vacuum | $\Lambda$ | $G_{\text{rank}}$ | $N_{\text{gen}}$ | $M_H^2$ |
| :--- | :---: | :---: | :---: | :---: |
| **$V_1$** | $1/100$ | $4$ | $3$ | $125$ |
| **$V_2$** | $1/100$ | $4$ | $3$ | $250$ |
| **$V_3$** | $-1/100$ | $4$ | $3$ | $125$ |
| **$V_4$** | $1/100$ | $5$ | $3$ | $125$ |
| **$V_5$** | $1/100$ | $4$ | $2$ | $125$ |

#### Scenario A: Partial Evidence Packet (Underdetermination)
Suppose an observer possesses an evidence record $e_A$ measuring only the first three observables:

- $\Lambda = 1/100 \ (\delta = 0)$

- $G_{\text{rank}} = 4 \ (\delta = 0)$

- $N_{\text{gen}} = 3 \ (\delta = 0)$

Running the deterministic verifier $V(e_A, \cdot)$ yields:

- $V_3$ is $\mathsf{Refuted}$ because $\Lambda = -1/100 \ne 1/100$.

- $V_4$ is $\mathsf{Refuted}$ because $G_{\text{rank}} = 5 \ne 4$.

- $V_5$ is $\mathsf{Refuted}$ because $N_{\text{gen}} = 2 \ne 3$.

- Both $V_1$ and $V_2$ satisfy all three measurements: $A_{F,e_A} = \{V_1, V_2\}$.

Because $|A_{F,e_A}| = 2 > 1$, the family terminalizer outputs:

$$\tau(e_A, F, \cdot) = \mathsf{Underdetermined}.$$

Neither $V_1$ nor $V_2$ is uniquely selected. Both survivors share the measured cosmological-constant analogue and three generations. Those properties are identified within the surviving alternatives; the individual model remains unselected.

#### Scenario B: Complete Evidence Packet (Unique Family Selection)
Now extend the evidence record to $e_B$ by measuring the fourth observable:

- $M_H^2 = 125 \ (\delta = 0)$.

Running the verifier against $e_B$:

- $V_2$ is now $\mathsf{Refuted}$ because $M_H^2 = 250 \ne 125$.

- $V_1$ is the sole survivor: $A_{F,e_B} = \{V_1\}$.

The family terminalizer outputs:

$$\tau(e_B, F, \cdot) = \mathsf{Accepted}.$$

Only now is $V_1$ uniquely selected within family $F$ relative to evidence $e_B$. The transition from $\mathsf{Underdetermined}$ to $\mathsf{Accepted}$ was accomplished not by generating more vacua, but by declaring a discriminating observable $M_H^2$ that separated the fiber.

### 5.2 Worked Example 2: Hexagonal Cycle Complex (False-Green Condition)

To demonstrate the Local-Green Global-Red boundary in code, we construct a 6-vertex directed graph $G = (V, E)$ forming a hexagon:

$$V = \{0, 1, 2, 3, 4, 5\}, \quad E = \{(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)\}.$$

Let the cycle $C$ be the complete perimeter.

1. **Evaluator Soundness Check:** We assign an arbitrary rational 0-cochain $f \in C^0(V, \mathbb{Q})$:
   $$f(0) = 1/2, \ f(1) = 7/3, \ f(2) = -4/5, \ f(3) = 11/7, \ f(4) = 0, \ f(5) = 3/4.$$
   Computing $d_0 f$ on each edge and summing around $C$ yields:
   $$\oint_C d_0 f = 0.$$
   Evaluator Soundness is verified exactly.

2. **False-Green Demonstration:** We construct a 1-cochain $\omega$ with a constant drift of $\epsilon = 1/10$ on each edge:
   $$\omega(0, 1) = \omega(1, 2) = \omega(2, 3) = \omega(3, 4) = \omega(4, 5) = \omega(5, 0) = 1/10.$$
   We set the local edge tolerance to $\tau_e = 1/5$ for all edges.
   - For every edge, $|\omega(e)| = 1/10 \le 1/5$. Thus, the system is **Local-Green** on every edge.
   - Computing the global cycle holonomy:
     $$\oint_C \omega = 6 \times \frac{1}{10} = \frac{3}{5} \ne 0.$$
   The global defect is strictly positive: $\Phi = 3/5$.

This confirms that local evaluation acceptance intervals can be fully satisfied everywhere, while a global topological obstruction remains completely unresolved.

### 5.3 Stress Test: Generating 100 Vacua Without Discriminating Evidence

In `TestRepresentationPlenitudeVsAuthority` of the test suite, we instantiate an ensemble of 100 candidate vacua $\{W_0, W_1, \ldots, W_{99}\}$, each assigned identical values for $(\Lambda, G_{\text{rank}}, N_{\text{gen}})$ but parameterized by an internal hidden modulus $\mu_i = i$.

When evaluated against the standard evidence packet:

- All 100 vacua are consistent with the evidence within tolerance: $|A_{F,e}| = 100$.

- The family verdict is $\mathsf{Underdetermined}$.

- The underdetermination ratio evaluated by `WitnessedDifferenceQuotient` is:

$$U(F, \mathcal{O}) = \frac{100}{1} = 100.$$

Relative to a singleton family with this observable profile, the 100-candidate family has an average fiber size 100 times larger. The unchanged evidence selects none of its members uniquely.

---

## 6. Scope Boundaries, Claim Discipline, and Non-Claims

In compliance with the claim hygiene discipline of this project, we explicitly state the scope boundaries and four-point summary of this monograph:

### 6.1 What This Monograph Supports

1. **Definite Separation of Categories:** It supports a strict mathematical distinction between proposal generation and family-relative empirical selection.

2. **Quotient Space Bounds:** It provides exact rational formulas for observer underdetermination ratios $U(F, \mathcal{O})$ on finite nonempty candidate families.

3. **Discrete False-Green Invariant:** It demonstrates in this discrete setting that local patch consistency in discrete cochain complexes does not imply global cycle triviality when local tolerances are non-zero.

4. **Sharp Cycle Holonomy Bound:** It establishes that local edge tolerances impose a sharp upper bound $|\oint_C \omega| \le \sum_{e \in C} \tau_e$ on cycle defects.

5. **Constructive Operational Framework:** It provides a reproducible Python implementation (`code/mod_representation_abundance_core.py`) checking stated finite examples and regressions in 33 core tests, with 23 separate release-integrity cases. Tests check implementations; general statements rely on the written proofs and only the explicitly scoped Lean components.

### 6.2 What This Monograph Does Not Support

1. **No Refutation of Physics Frameworks:** It does not claim that string theory, cosmological multiverse models, or cellular automata are mathematically false, physically unviable, or without scientific value.

2. **No Claim of Continuum Realization:** It does not construct continuous physical spacetime, smooth manifolds, or continuous gauge fields.

3. **No Empirical Predictions:** It does not predict the numerical value of the cosmological constant, the Higgs mass, or any physical constant of nature.

4. **No Global Unconditional Authority:** This monograph does not assign unconditional physical authority to any specific model; acceptance is strictly relative to a declared candidate family and evidence record.

### 6.3 The Narrowest Defensible Claim

The narrowest defensible claim established by this monograph is:

> *Within any finite observer evaluation system or discrete cochain complex, membership of a candidate model in a representation space does not imply that the candidate is selected by a finite terminal selector, and local consistency across all evaluation patches does not imply that the global cycle obstruction vanishes.*

### 6.4 Next Tests Needed

1. **Empirical Parameter Fencing:** Construction of explicit finite selectors for realistic cosmological and particle physics parameter datasets with certified experimental error bars.

2. **Higher-Degree Cochain Solvers:** Mechanization of higher-dimensional cochain complexes ($C^1 \xrightarrow{d_1} C^2 \xrightarrow{d_2} C^3$) to evaluate 2-cycle and 3-cycle cocycle obstructions.

3. **Interactive Replay Demonstrations (future work):** Develop pedagogical walkthroughs illustrating the quotient space collapse and selector terminalization in educational settings.

---

## References

1. Carroll, J. H. (2026). *The Witnessed Difference Programme: From Finite Distinction to Witnessed Measurement*. Research Monograph Series 001_finite_obstruction_calculus, Paper 000.

2. Carroll, J. H. (2026). *Local Green, Global Red: Evaluated Path Kernels, Organizational Gluing, and Finite Presentation Obstructions*. Research Monograph Series 001_finite_obstruction_calculus, Paper 001.

3. Carroll, J. H. (2026). *An L1 Obstruction Framework for Coboundary Defects: Lp Solvers, Schatten Presheaves, and Primal-Dual Iterators*. Research Monograph Series 001_finite_obstruction_calculus, Paper 003.

4. Cartwright, N. (1983). *How the Laws of Physics Lie*. Oxford University Press.

5. Douglas, M. R. (2003). *The statistics of string / M theory vacua*. Journal of High Energy Physics, 2003(05), 046.

6. Duhem, P. (1906). *La théorie physique: son objet, sa structure*. Chevalier & Rivière.

7. Popper, K. R. (1959). *The Logic of Scientific Discovery*. Hutchinson & Co.

8. Smolin, L. (2006). *The Trouble with Physics: The Rise of String Theory, the Fall of a Science, and What Comes Next*. Houghton Mifflin.

9. Susskind, L. (2003). *The anthropic landscape of string theory*. arXiv:hep-th/0302219.

10. Wolfram, S. (2002). *A New Kind of Science*. Wolfram Media.
