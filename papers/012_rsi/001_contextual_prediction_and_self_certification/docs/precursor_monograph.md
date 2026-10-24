<div align="center"># Conditional Limits on Global Prediction, Self-Knowledge and Self-Certification for Physical Reasoners (CODA-FOC / CODA-GTLA)</div>
<div align="center">Four separately quantified no-go statements for finite, boundary-mediated, effectively enumerable reasoners in contextual worlds, with the self-knowing limits of the Witnessed Difference Programme and an exact-rational mechanization</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">2026-10-17</div>
<div align="center">Version 1.2.0</div>

## Abstract

Version 1.0.0 of this manuscript stated one theorem with four clauses under four substrate-blind postulates and called it a demarcation of physical cognition. An outside review of that version found the central implications false as stated, the postulates under-specified, and the inline floating-point kernel unsound as a decision procedure. This version replaces the single theorem by four separately quantified statements, each tagged by its evidential status, and replaces the inline kernel by the exact-rational observer merged on the repository trunk.

The four statements are these. (I) For a no-signalling empirical model on a finite cover, either a joint distribution over global assignments marginalises to every context, or the exact ℓ¹ distance to the noncontextual polytope is positive and a dual witness of sup-norm at most one certifies it; the alternative is decided by linear-programming duality over the rationals and the certificate is replayed before it is reported. (II) If the observer's boundary map has a nonzero kernel, two states share one report, so no function of the report returns both of their answers; this is an instance of a fiber lemma that needs no vector space, and it is a statement about one step, not about privacy over time, which remains open. (III) A system's evaluation of its own claim carries no authority by definition; a ledger of self-evaluations cannot establish its own completeness except against a tip pinned outside it; the Tarski and Löb forms of self-grounding hold only for a specified effective theory, which is a hypothesis to be established per system; and relabeling blindness bounds relabeling-invariant verdicts only. (IV) A provenance packet in which the proposer or the evaluator is the authorizer, or whose root is not admitted, is refused before any mathematics is consulted; authority delegated from an admitted root is valid, and competence does not supply the delegation.

Between the statements and their applications sits the self-knowledge boundary of the Witnessed Difference Programme, copied here with its identifiers: the presentation blind spot, the refuted implication ladder and its repaired predicates, the injectivity and recovery bounds for linear presentations, the awareness firewall, the three-axis regress at its declared scope, the authority packet and its four invalid implications, and the falsifier that a self-knowledge completeness claim fails whenever the presentation map has a displayed nontrivial fiber.

**Why this matters.** The distinction the first version was reaching for survives: predictive competence inside a context is unbounded by anything here, and the standing to admit one's own claims is a license from outside, not a capability. What does not survive is every inference from the first to limits on the second that skipped a hypothesis. This version names each hypothesis, says who establishes it, and gives the reader a fixture table and a command list with which every computed sentence can be re-run.

**Status and scope.** Status: WORKING_DRAFT. It is not deposited, carries no DOI, and supersedes version 1.1.0, which in turn superseded version 1.0.0 (an outside review found that version not publishable in its theorem form). The text is licensed CC-BY-4.0; the code under `code/`, `scripts/`, `tools/` and `lean4/` carries the code license in `LICENSE-CODE`. Authority status: None. This monograph assigns no authorization and changes no jurisdiction. It carries no operational authority or institutional standing.

**CODA architecture and operational layers.** Of the nine components of the Calculus of Obstruction, Descent, and Authority (CODA), this monograph uses two. Its contextuality verdicts (exact ℓ¹ defect, dual witness, support descent) are Finite Obstruction Calculus (FOC) objects. Its authority statements (three-role packet, admitted root, refusals, delegated standing) are General Theory of Layered Authority (GTLA) objects. It constructs nothing on the other seven layers (FDA, OR, A, Q, CS-Q, CS, MUR).

**No automatic upgrade.** A verdict of this monograph is not a capability ceiling, not a statement about any particular system, and not a standing.

## 1. Introduction

### 1.1 What changed from version 1.0.0

Version 1.0.0 carried the title "The Universal Epistemic No-Go Theorem for Physical Cognition". That title is withdrawn. The word it rested on named a quantifier the proofs did not discharge: the statements below hold for every system that satisfies their hypotheses, and whether a given brain, language model or proof assistant satisfies them is an empirical claim about that system that this monograph does not make.

The outside review of version 1.0.0 (summarised in the change log) found, in order: that the privacy proposition fails under dynamics; that the inference-device section defined weak inference and invoked strong-inference theorems; that the inline kernel returned a glued global section for a CHSH value of 2 + 4·10⁻⁸; that the abstract conflated noncommutativity, contextuality and nonzero Čech cohomology; that two self-grounding arguments were invalid as written; that the authority and thermodynamic conclusions exceeded their premises; that several precursor identifiers had changed meaning in transit; and that the ledger named symbols the code did not define. Every one of those findings is accepted. Section 7 answers them one by one.

The repository's own note on the merged kernel (WDP-DOC-EPIS-NOGO-001, in the documentation folder of the Witnessed Difference Programme package) reached the same corrections independently on 2026-10-16 and is the source of the status tags used here.

### 1.2 Status tags

Every statement in this monograph carries one of six tags.

- PROVED HERE: a written proof in this monograph, over the stated hypotheses.
- COMPUTED: a value or verdict produced by the cited kernel on a cited fixture and replayable by the commands of section 6.
- IMPORTED: a result of the literature or of the Witnessed Difference Programme, cited and used at its declared scope, not re-proved.
- DEFINITIONAL: a consequence of a definition adopted here or in the programme.
- OPEN: a statement the author wants and this monograph does not establish; a falsifier or a witness of the gap is given.
- FALSE: a statement of version 1.0.0 withdrawn, with the counterexample.

### 1.3 Reading guide

Section 2 fixes the primitives and the four hypotheses. Section 3 copies the self-knowing limits of the Witnessed Difference Programme, identifier by identifier, and says what each contributes here. Section 4 states the four results. Section 5 gives the worked examples and their fixture values. Section 6 names the mechanization and lists the commands. Section 7 records the corrections. Section 8 lists non-claims and open problems. Section 9 is the bibliography; section 10 the claim index.

## 2. Primitives and hypotheses

### 2.1 Empirical models

A **scenario** is a finite set of questions $X$, a finite outcome set $O_x$ for each question, and a cover $\mathcal M$ of $X$ by maximal contexts, the sets of questions that one evaluation can answer together. An **empirical model** $e$ assigns to each context $C \in \mathcal M$ a probability distribution $e_C$ on $\prod_{x \in C} O_x$ with rational entries. It is **no-signalling** when $e_C$ and $e_{C'}$ have the same marginal on $C \cap C'$ for all $C, C'$. IMPORTED as a definition (Abramsky and Brandenburger 2011, [REF-1]).

A **global section** of $e$ is a probability distribution $p$ on the global assignments $\prod_{x \in X} O_x$ whose marginal on every context equals $e_C$. The **ℓ¹ defect** of $e$ is

$$d(e) = \min_{p} \lVert A p - e \rVert_1$$

over probability vectors $p$ on global assignments, where $A$ is the marginalisation matrix. A **dual witness** is a vector $y$ with $\lVert y \rVert_\infty \le 1$ and $\langle y, e \rangle - \max_{g} \langle y, A \delta_g \rangle = d(e)$; it is a Bell functional with the classical bound subtracted.

A **support presheaf** records, per context, which joint outcomes have positive probability. A model is **strongly contextual** when no global assignment lies in every context's support, and **logically contextual** when some supported local section has no supported global extension. For a parity-shaped support the **parity cut** is a set of contexts whose $\mathbb F_2$ constraints sum to the contradiction $0 = 1$.

The **nerve** of the cover is the simplicial complex of nonempty intersections of contexts; its rational first cohomology $H^1$ depends on the cover alone.

### 2.2 Observers, presentations, fibers

An **observer packet** (the programme's chapter 10) carries a state space, a presentation map $q: X_{\mathcal O} \to P_{\mathcal O}$ from accessible states to reports, and the maps needed to evaluate reports. The **fiber** of $q$ over a report is the set of states with that report. A **boundary projection** is a linear presentation $\pi: K \to B$ on a finite-dimensional state space $K$; its **private fiber dimension** is $\dim K - \dim B$ when $\pi$ is surjective, which is the only case the kernel declares.

### 2.3 Authority packets and receipts

An **authority packet** is $\mathfrak A = (R, J, \mathsf{Perm}, \mathsf{Proc}, \mathsf{Appeal})$: roles, a jurisdiction, a typed permission relation, a procedure, and an appeal mechanism (WDP-CH15-D01, copied in section 3.8). A **provenance packet** for a claim names a proposer $P$, an evaluator $E$ and an authorizer $A$, and a root of trust from which $A$'s standing descends. An **executable machine receipt** is $(c, \Delta, \varphi^*, \mathrm{status})$ with $\mathrm{status} \in \{\mathsf{PASS}, \mathsf{FAIL}, \mathsf{REFUSE}\}$ (WDP-CH15-D02).

### 2.4 The four hypotheses

None of the four is derived. Each names where it comes from and who must establish it for a given system.

- **H1 (co-evaluable contexts, finite data).** The world the reasoner predicts presents a scenario with a finite cover and a no-signalling empirical model with rational entries. IMPORTED as a definition. The kernel checks no-signalling exactly and refuses a signalling table with a typed error. Version 1.0.0 derived finiteness of the data from finite entropy and from the Bekenstein bound; neither inference holds (a distribution with $p_n = 2^{-n}$ has finite entropy and infinite support, and the bound concerns a region, not a data set). Finite support is declared here, not derived.
- **H2 (private fiber).** The observer reports through a boundary map $\pi: K \to B$ with $\ker \pi \ne 0$. Declared per observer. The kernel refuses an observer whose boundary dimension equals its state dimension. Whether a given physical system has such a map is an empirical claim about that system. The physical readings offered for H2 in version 1.0.0 (Bekenstein, Landauer, Holevo) are IMPORTED as motivation and are used in no proof.
- **H3 (self-reference bridge).** When a statement of section 4.3 invokes Tarski or Löb, the reasoner is assumed to carry a specified consistent, effectively axiomatised theory $T$ extending a base arithmetic, with a Gödel numbering of its own sentences and a provability predicate for $T$. IMPORTED. The hypothesis is about the reasoner's declared theory, not about the token stream it emits; a generator and its realised stream are different objects, and H3 is a claim about the first.
- **H4 (three roles).** A claim is admitted for authorization only through a provenance packet naming a proposer, an evaluator and an authorizer whose standing descends from an admitted root external to the packet. DEFINITIONAL: WDP-CH15-D01 and the authority packet of the programme's chapter 15. The separation is a policy a jurisdiction adopts; the code enforces it; nothing in physics imposes it.

## 3. The self-knowing limits of the Witnessed Difference Programme

This section copies, with identifiers, the statements of the programme's chapters 14, 15 and 21 that bound what a reasoner can know and certify about itself. Each item ends with its use here. Where the wording is the programme's, it is quoted; where it is paraphrased, the identifier is the authority. Nothing in this section is proved here; everything is IMPORTED or DEFINITIONAL.

### 3.1 Self-presentation and self-witnessing (WDP 14.1)

"An observer can receive as input a representation of some of its own state." With $\sigma: \mathcal O \to X_{\mathcal O}$ encoding the accessible self-state, a self-report is the ordinary report $q_{\mathcal O}\sigma$ with a reflexive provenance path.

WDP-CH14-D01 (self-witnessing event). "A self-witnessing event is a validated observation whose target proposition concerns a typed component of the same observer packet and whose provenance/re-access record exhibits that reflexive target." The programme adds: "A program checking its own version hash is a simple instance. It witnesses a proposition about an accessible representation, not every fact about itself."

Use here: the object of section 4.3 is a self-witnessing event in this sense. The restriction "an accessible representation, not every fact" is the whole of what the fiber arguments add.

### 3.2 The refuted implication ladder and its repair (WDP 14.2)

An earlier draft of the programme printed a hierarchy $O_3 \Rightarrow O_2 \Rightarrow O_1 \Rightarrow O_0$ of self-knowledge levels. "As stated, the levels mixed incompatible context actions and made $O_0$ and $O_1$ contrary in some models. The full carrier ladder is therefore a `RefutedDraft`, not a theorem." The repair replaces the ladder by independent predicates with explicit bridges:

- $R_1$: a self-report is linked to an accessible self-state;
- $R_2$: the report remains stable under a declared context transport;
- $R_3$: an evaluator can compare the report with later behavior or state.

"Comparison availability and calibration success are separate predicates; partial maps cannot be completed by defaults."

Use here: version 1.0.0's Proposition 2.4 asserted an implication of the refuted kind, from an instantaneous kernel to privacy under every later observation. Section 4.2 keeps only $R_1$-level content and marks the rest open.

### 3.3 The presentation blind spot (WDP 14.3)

WDP-CH14-P01 (presentation blind spot). "If $x \ne y$ but $q_{\mathcal O}(x) = q_{\mathcal O}(y)$, then every function $F: P_{\mathcal O} \to Z$ assigns the same output to the presentations of $x$ and $y$." The programme's gloss: "This trivial factorization fact is a precise limit on self-knowledge in the model. It is not the philosophical hard problem and does not imply that a human or machine lacks awareness."

Use here: this is the fiber lemma of section 4.2 in the programme's notation. The second sentence of the gloss is adopted as a non-claim.

### 3.4 Capacity, diagonal questions and the Gödelian preconditions (WDP 14.4)

"A finite observer with a finite report alphabet cannot injectively encode an arbitrarily large state space. Pigeonhole arguments yield blind spots relative to the selected encoding. Stronger diagonal or self-reference results require a language capable of naming its own reports, an interpretation map, and a logic. Those structures must be listed before invoking Gödelian language."

Frauchiger–Renner scenarios "can serve as adversarial tests for context mixing in a quantum host [REF-OBS-009]. They are not evidence for a general awareness theorem, and no protocol or proof from that work is imported here."

WDP-CH14-P02 (injectivity on a declared subspace). A linear presentation map $q$ on a finite-dimensional space is injective on a declared subspace $Y$ exactly when $Y \cap \ker q = 0$. This requires at least $\dim Y$ report coordinates, and with fewer, exact elimination over the coefficient field exhibits a nonzero $y \in Y$ with $q(y) = 0$. Proof in the programme by rank–nullity.

WDP-CH14-P03 (recovery bound). If $q$ is injective on $Y$ and norms are declared, some $c > 0$ satisfies $\lVert y \rVert \le c \lVert q(y) \rVert$ on $Y$, and a report perturbed by $\eta$ with $\lVert \eta \rVert \le \varepsilon$ still gives $\lVert y \rVert \le c(\lVert q(y) + \eta \rVert + \varepsilon)$. The hypothesis is needed: over $\mathbb Q$ with the report norm $|r_1 + \sqrt 2\, r_2|$ no constant exists.

WDP-CH14-N02 (nonclaim). "Injectivity of a presentation map on a declared subspace does not detect inputs outside that subspace, does not certify detection of unmodeled or adversarial behavior, and does not select, price, or authorize a sensor suite."

Use here: the three listed structures (a language naming its own reports, an interpretation map, a logic) are hypothesis H3. Version 1.0.0 invoked Tarski and Löb without listing them; section 4.3 lists them. P02 and P03 are the exact-linear content behind H2; version 1.0.0 cited them for a thermodynamic inequality they do not state, and that citation is withdrawn. N02 is adopted: the private fiber of H2 says nothing about what lies outside the declared state space.

### 3.5 The awareness firewall (WDP 14.5)

WDP-CH14-N01 (nonclaim). "Self-witnessing, self-modeling, evaluator closure, or report integration does not establish phenomenal consciousness."

WDP-CH14-O01 (declared functional bridges). For independently declared finite presentation, report, context and calibration maps, factorization and stability have the complete implication classification of the programme's Appendix J; "later-target and successful linked-report existence are exact fiber-constancy questions. No phenomenology premise occurs."

The programme's interpretive remark distinguishes adjectival reports ("the apple appears red"), which have external anchors, from adverbial reports ("I am remembering vividly"), whose anchors are temporal profile, salience and later reports by the same subject. "Neither report is nothing, and neither governs a shared verdict by being felt."

Use here: adopted as non-claims. Nothing in sections 4 to 8 is a statement about experience.

### 3.6 The three-axis regress at its declared scope (WDP 14.8)

WDP-CH14-T01 (three-axis self-grounding regress), for an autonomous computational process $S$ without external observer grounding: Axis 1, every rule admission depends on `AdmitInst`, and without an empirical base instance admission collapses (`collapsed_of_no_insts`); Axis 2, verifying the truth predicate of carrier $K_n$ requires ascent to $K_{n+1}$, and self-endorsement within $K_n$ carries no authority (`ENC-0195`); Axis 3, syntactic transformations with zero passage charge cannot distinguish defect repairs from coordinate changes.

WDP-CH14-C01 (demarcation of ungrounded synthetic models) and WDP-CH14-N03 (nonclaim): the theorem "applies to self-evaluating syntactic generative models lacking external grounding; it does not restrict systems coupled to physical actuators or external formal oracle verifiers."

Use here, with two reservations recorded in the programme's own note. Axis 1 rests on an admitted result and is used. Axis 2 as printed cites a "Lemma D" that could not be sourced, and Axis 3 as printed cites NB-9, which the programme's notebook review refuted; neither axis is used as a proved step. Axis 2 is replaced by the Tarski and Löb forms under H3 (section 4.3), and Axis 3 is restated with its hypothesis made explicit (section 4.3, claims (1) and (2)), following the companion note FOC-035 which derives it from NS-14 and CL-13 alone.

### 3.7 Self-model calibration and the repaired hierarchy (WDP 15.9)

"A self-report can be calibrated against externally accessible behavior without being exhaustive." With reports $r \in R$, behaviors $b \in B$ and a calibration relation $K \subseteq R \times B$, repeated tests reveal systematic mismatches; "the result concerns $K$ and the sampled behavior family, not the total internal state." The repaired hierarchy:

- self-presentation: a report is generated from an encoded self-state;
- self-retention: the report is available later;
- self-comparison: a later procedure compares it with a typed target;
- self-calibration: the comparison satisfies a declared relation on a test family;
- cross-context robustness: the relation is preserved under named context transports.

"No implication should be asserted in reverse, and forward implications require the adapter laws. A stable report can be consistently wrong; a calibrated report can cover only a narrow test family; a broad functional self-model still does not settle phenomenology."

Use here: the ledger statement of section 4.3 is a self-retention and self-comparison statement and no more. The sentence "a stable report can be consistently wrong" is the reason section 4.3 refuses to let a consistent ledger certify soundness.

### 3.8 Authority as a separate layer (WDP 15.1 to 15.3, 15.13)

WDP-CH15-D01 (authority packet). $\mathfrak A = (R, J, \mathsf{Perm}, \mathsf{Proc}, \mathsf{Appeal})$, "where $R$ is a set of roles, $J$ a jurisdiction, $\mathsf{Perm}$ a typed permission relation, $\mathsf{Proc}$ a procedure for exercising permissions, and $\mathsf{Appeal}$ any review or revocation mechanism. The packet is external to the layered observer. A bridge from measurement or proof status into an authority procedure is a policy choice in a jurisdiction, not a theorem of obstruction calculus."

Four separations (WDP 15.2), invalid without explicit bridge rules:

$$\text{witness exists} \not\Rightarrow \text{observer accepts} \not\Rightarrow \text{measurement valid} \not\Rightarrow \text{authority standing} \not\Rightarrow \text{claim true}.$$

"An authorized role can make an incorrect statement; a correct measurement can be outside a role's jurisdiction; an evaluator can accept an internally valid record that lacks metrological fields; and a residual can exist without being registered."

WDP 15.3 (repository status): "A green test run says that specified commands returned expected results in a specified environment. A formal proof says that a term inhabits a proposition under the proof assistant's logic and imports. A release tag identifies bytes. None of these confers institutional, scientific, or moral authority." WDP-CH15-N01 is the nonclaim this monograph's authority status line repeats.

WDP-CH15-D02 (executable machine receipt) and WDP-CH15-P04 (prose authority impotence): prose declarations and cited rules carry no authority; "compliance is established solely by the generation of a passing machine receipt." WDP-CH15-N02: this "defines repository verification governance; it does not model legal or social authority structures."

Use here: H4 and the whole of section 4.4. The four separations are the reason no verdict of sections 4.1 to 4.3 changes a packet's standing. N02 fixes the scope: section 4.4 is about a verification regime, not about law.

### 3.9 The falsifier (WDP 21.5)

"A self-knowledge completeness claim fails whenever the presentation map has a displayed nontrivial fiber." Also from the same list: "Any implication from evaluator acceptance to authority is ill typed unless an authority bridge is declared."

Use here: these are the two falsifiers of sections 4.2 and 4.4. A reader who exhibits a nontrivial fiber refutes a completeness claim; a reader who finds a passage from a verdict to a standing without a declared bridge has found a type error in this monograph.

## 4. The four results

### 4.1 Result I: exact dichotomy for context-free prediction

**Theorem I (PROVED HERE; decided by the kernel with a replayable certificate).** Let $e$ be a no-signalling empirical model with rational entries on a finite cover. Exactly one of the following holds.

1. A probability distribution $p$ on global assignments marginalises to every context of $e$. The kernel returns `GlobalSection` carrying $p$, after re-marginalising $p$ exactly and comparing it with $e$ entry by entry (`verify_joint`).
2. No such $p$ exists; then $d(e) > 0$ is attained, and a dual witness $y$ with $\lVert y \rVert_\infty \le 1$ certifies $d(e)$, so that every distribution on global assignments mispredicts $e$ by at least $d(e)$ in ℓ¹. The kernel returns `Obstructed` carrying $d(e)$ and $y$, after replaying the witness exactly (`verify_l1_defect`).

*Proof.* The primal is a linear programme over $\mathbb Q$ with a bounded feasible region (probability vectors), so the minimum is attained at a rational vertex. Strong duality for linear programmes over an ordered field gives a dual optimum with equal value; normalising the dual variable of the ℓ¹ norm gives $\lVert y \rVert_\infty \le 1$. If the minimum is $0$ the optimal $p$ is a global section; if positive, the dual value is the lower bound on the mismatch of every $p$. The kernel solves both programmes in exact rational arithmetic with a pivot budget; exhausting the budget returns a typed refusal, never a verdict. $\square$

**Refinements (COMPUTED by support enumeration).** When obstructed, the kernel enumerates the support presheaf and classifies the obstruction as `Strong` (no global assignment lies in every context's support; carries the parity cut when the support is parity-shaped and a descent classification), `Logical` (a supported local section with no supported global extension; carries that section), or `Probabilistic` (the defect is positive with full support). The enumeration is bounded by a declared cap on global assignments and refuses beyond it.

**Scope of Result I.** The theorem obstructs noncontextual predictors: those that answer every question from one joint distribution regardless of which questions are asked alongside. A predictor that carries the context, as a quantum state with a setting does, reproduces the table. Contextuality excludes one global representation, a joint distribution reproducing the contextual statistics; a system can hold the whole specification of a contextual model, obstruction included, without holding a global assignment that does not exist, and Abramsky and Brandenburger make that distinction explicit [REF-1]. Version 1.0.0's reading "no world-model exists" is FALSE at that width.

**What Čech cohomology does and does not do.** The rational $H^1$ of the nerve is a cover invariant: on the Bell cover it is 1 for every model, including the two global sections in the fixture table (COMPUTED). The Abramsky–Brandenburger–Mansfield cohomological obstruction [REF-2] lives in the support presheaf, is sufficient for contextuality and not necessary (IMPORTED), which is why the kernel decides by the linear programme and reports the nerve number as a cover invariant only. Version 1.0.0's claim that nonzero $H^1$ of the cover obstructs a global world-model is FALSE.

### 4.2 Result II: the fiber lemma and the one-step boundary

**Lemma II (fiber lemma; PROVED HERE).** Let $E: W \to K$ be everything available to a system for one decision and $q: W \to A$ the answer sought. If $E(w) = E(w')$ and $q(w) \ne q(w')$, then no $f: K \to A$ satisfies $f \circ E = q$.

*Proof.* $f(E(w)) = f(E(w'))$ and $q(w) \ne q(w')$. $\square$

This is WDP-CH14-P01 with the programme's $q_{\mathcal O}$ as $E$. Internal computation of any depth is a choice of $f$ and leaves the obstruction where it is while $E$ is fixed. What the lemma does not supply is its premise: that two worlds with the same $E$-image and different answers exist is the substantive obligation of each application.

**Corollary II (no perfect peer prediction from the boundary; PROVED HERE under H2).** If $\ker \pi \ne 0$ for the peer's boundary map, there are two peer states with the same boundary report, so any predictor of the peer that reads only the boundary returns one prediction for two states and is wrong on at least one of them. The content of the corollary is H2.

**Proposition II-open (privacy over time; OPEN).** The kernel of $\pi$ is an instantaneous statement. With $K = \mathbb F_2^2$, $\pi(a, b) = a$ and dynamics $F(a, b) = (b, a)$, the hidden coordinate $b$ is the next report. Permanent privacy is indistinguishability under every allowed observation history and intervention, and version 1.0.0's Proposition 2.4 asserted it from the instantaneous kernel alone; that assertion is FALSE as stated (the review's witness, and the harness test on swap dynamics). What would establish privacy over time is either a fixed report map with trivial dynamics, or an intertwining condition $\pi \circ F_u = \bar F_u \circ \pi$ for every allowed intervention $u$, giving a transcript-fiber statement; neither is proved here.

**Wolpert (IMPORTED, unused).** Wolpert's inference-device theorem [REF-3], that no device in a world can strongly infer every other device in it, is background for Corollary II and is used in no proof. Version 1.0.0's section 2.2 defined weak inference and invoked the strong-inference theorems; the review's four-world counterexample shows the gap, and the "pullback apex" corollary that rested on it is withdrawn.

### 4.3 Result III: no self-grounding, in four separately quantified parts

**III.a (DEFINITIONAL; `ENC-0195`).** An observer's own evaluation of its own claim carries no authority. This is a typing rule of the receipt, enforced by the receipt types of the kernel; it is not a theorem about the observer.

**III.b (ledger completeness; PROVED HERE and COMPUTED).** A ledger of self-evaluations cannot establish its own completeness. *Proof.* Any prefix of a hash-chained ledger is itself a well-formed chained ledger, so a truncated tail passes every internal check; completeness is decidable only by comparison with a tip pinned outside the ledger. $\square$ The kernel's `verify_ledger` accepts every consistent prefix and `complete_against` decides completeness against an external tip; the integration test truncates and tampers.

**III.c (Tarski and Löb forms; IMPORTED under H3).** For a consistent, effectively axiomatised $T$ extending a base arithmetic with its own provability predicate: no formula of $T$ defines truth for $T$'s own sentences (Tarski [REF-5]); and if $T \vdash \mathrm{Prov}_T(\ulcorner\varphi\urcorner) \to \varphi$ then $T \vdash \varphi$ (Löb [REF-6]). So a reasoner that is such a $T$ does not derive its own soundness schema for undecided sentences. Both hold only when H3 is established for the reasoner; a level counter, a token stream, or the ability to use the words "I" or "ASI" does not establish it. Version 1.0.0's rendering of Löb was misstated and the claim that "verification of a carrier needs a larger carrier" in general is withdrawn; what is retained is the pair of theorems at their own scope.

**III.d (relabeling blindness, restated with its hypothesis; PROVED HERE).** Let $G$ be the group of presentation relabelings of a carrier $K$ (bijections on tokens, extended to carriers). A verdict $V$ on carriers cannot separate $K$ from $gK$ when $V$ is $G$-invariant, or factors through a $G$-invariant export $V = \bar V \circ \mathrm{Exp}$ with $\mathrm{Exp}(\sigma H) = \mathrm{Exp}(H)$. *Proof.* $V(gK) = V(K)$ by hypothesis. $\square$ Without the hypothesis the statement is FALSE: the verdict "the first token is `a`" separates a carrier from its relabeling. Two claims are kept apart, both of which hold: (1) an invariant defect is detected by internal computation whenever the supplied data determine it (the kernel computes the defect of Result I from the table alone); (2) a relabeling cannot change that defect (it permutes the polytope onto itself). Version 1.0.0's inference from (2) to the denial of (1) ("token manipulation cannot detect quotient defects") is FALSE for defects the data determine. What relabeling blindness adds is an instance of Lemma II: $H$ and $\sigma H$ have the same export, and the question whether the tokens of one denote what the tokens of the other denote is answered differently by a nontrivial $\sigma$ on grounded tokens. So a drop in an internal defect is certified as a drop, and what no export-reading verdict decides is whether the drop is a repair or a reinterpretation; that question lives in the grounding map, which is a declared observer outside the system.

**Well-foundedness (withdrawn).** Version 1.0.0's section 3.2 argued that an admission order on carriers must be well founded; the review's two-element counterexample ($K = \{a, b\}$, $a \prec b$) shows that the argument as written establishes nothing. Axis 1 of WDP-CH14-T01 (`collapsed_of_no_insts`) is retained as IMPORTED at its own scope and is not re-derived.

### 4.4 Result IV: no self-granted authority, and delegated standing

**Proposition IV (DEFINITIONAL; enforced).** Under H4, a provenance packet is refused before any verdict of Results I to III is read when: the proposer is the authorizer; the evaluator is the authorizer; the authorizer's standing is prose rather than a certificate; the root is not admitted; or the root is the proposer or the evaluator. The contract `verify_three_role_authority` returns a typed refusal and never a receipt in those cases, and under a regime policy that admits self-authorization the receipt it issues still marks the evaluation as carrying no authority.

**What Proposition IV does not say.** A system may authorize when the standing it acts under was delegated to it earlier by an admitted root; the contract models that case and issues the receipt. What a system cannot supply from its own competence is the delegation. Authority is a license granted from an admitted root; no verdict of Results I to III changes a packet's standing; distinct principal strings in a packet do not by themselves establish independent controllers, which is a fact about the jurisdiction's procedure, not about the packet. The premise is the regime: as WDP 15.1 has it, the bridge from a proof or a measurement to a permission is a jurisdictional choice. Version 1.0.0's Theorem 5.1 clause 4 and its "sovereign kernel" language treated this policy as physics; that treatment is withdrawn.

### 4.5 The demarcation, as a reading of the four results

Combinatorial competence is what a system does inside a context: answer, compose, search, prove, predict, compress. It is measured by witnesses and costs and nothing here caps it. Self-grounding standing is being, for one's own claims, proposer, evaluator and authorizer at once. Results I to IV say that no amount of the first buys the second, because the second is a license issued from a root outside the licensee. The cut is between a verdict and a standing.

In the author's words, adopted as the one-sentence reading: "A unified self-presentation supplies neither a guarantee of complete knowledge nor an independent source of authority. Each claim still requires sufficient evidence; each permission still requires standing under the applicable authority regime."

**Substrate indifference (PROVED HERE, by inspection of the hypotheses; and no more).** H1 to H4 mention a cover, a boundary map, a theory, a ledger and a packet. None names neurons, weights or proof terms. So the results apply to a brain, a language model, a proof assistant or a hypothetical superhuman system exactly when that system is described by the hypotheses, and the description is the empirical step this monograph does not take. Version 1.0.0's Theorem 5.3 ("competence envelope") and its substrate table are reduced to this paragraph.

## 5. Worked examples

All values are COMPUTED by the kernel on the fixture file named in section 6 and checked by the Python harness independently where stated. Every rational is exact.

| fixture | verdict | ℓ¹ defect | parity cut | nerve $H^1$ | supported global assignments | note |
| --- | --- | --- | --- | --- | --- | --- |
| `pr_box` | `Strong` | 2 | {0, 1, 2, 3} | 1 | 0 | CHSH value 4 |
| `classical_mixture` | `GlobalSection` | 0 | none | 1 | 2 | joint re-marginalised exactly |
| `deterministic_zero` | `GlobalSection` | 0 | none | 1 | 1 | |
| `near_tsirelson` | `Probabilistic` | 4/5 | none | 1 | 16 | CHSH value 14/5 > 2 |
| `wdp_15_5_triangle` | `Strong` | 2 | {0, 1, 2} | 1 | 0 | the programme's section 15.5 counterexample |
| `hardy_type` | `Logical` | 1/3 | none | 1 | 5 | carries the unextendable section |

Two refusals are pinned: `signalling_family` (marginals disagree on an overlap; typed error before any LP) and `oversized_singletons` ($2^{21}$ global assignments against a cap of $2^{20}$; typed refusal of the enumeration).

**The near-Tsirelson table.** On the Bell cover with contexts $(x, y) \in \{0,1\}^2$, each context's distribution puts $17/40$ on each equal-outcome pair and $3/40$ on each unequal pair, except the context $(1,1)$, where the weights are exchanged. The harness re-derives the classical CHSH bound 2 by enumerating the sixteen deterministic strategies and checks that the table attains $14/5$, which certifies a positive defect independently of the linear programme. The exact defect $4/5$ and its dual witness come from the kernel and are replayed before being reported.

**Why the boundary value matters.** The review's probe for version 1.0.0 was a table at CHSH value $2 + 4 \cdot 10^{-8}$, which the floating-point solver of that version glued. In the present kernel the same table is a rational input; its defect is a rational number decided by exact pivoting, and a positive defect, however small, is returned as `Obstructed` with its witness. No tolerance exists in the code path.

**The swap-dynamics witness.** The harness fixes $K = \mathbb F_2^2$, $\pi(a, b) = a$, $F(a, b) = (b, a)$, and records that the coordinate hidden at time 0 is the report at time 1. This is the recorded falsifier of version 1.0.0's Proposition 2.4.

## 6. Mechanization and verification

Three artifacts carry the computed and checked statements. They overlap in some places and not in others; the last paragraph of this section says which statement rests on which.

**The Rust kernel (not in this deposit).** The exact-rational observer is the module `epistemic_observer` of the crate `omega_sheaf_theory`, with the three-role contract `three_role_authority` in the crate `omega_contracts`, their JSON fixtures and Rust integration tests, all merged on the repository trunk at commit b8a84409f (pull request 1083, 2026-10-16). These crates depend on the repository workspace and are not copied here. Rationals are `num_rational` big rationals; every rational in JSON is a canonical string `p/q`. The verdict type is `GlobalSection { joint, nerve_h1_dim }` or `Obstructed(Strong | Logical | Probabilistic)`, each obstruction carrying the ℓ¹ defect and its dual witness. The entry point `evaluate_epistemic_contextuality(model, pivots)` checks no-signalling, computes the nerve $H^1$, solves the defect programme within the pivot budget, replays the witness (`verify_l1_defect`), enumerates the global support, classifies the obstruction, and re-marginalises any joint (`verify_joint`). The observer carries a declared `BoundaryProjection { state_dim, boundary_dim }` whose `private_fiber_dim` is the difference of declared dimensions; there is no numerical rank. The only budget is the LP pivot budget, whose exhaustion is a typed refusal. The exact ℓ¹ defects, the dual witnesses and the classification in the table of section 5 are COMPUTED by this kernel and cannot be re-run from this deposit.

**The Python checks (in this deposit).** `code/epistemic_kernel.py` uses only the standard library and `fractions.Fraction`. It reproduces the finite statements that need no linear-programming solver: the three Bell-cover tables, supported global assignments, exact marginalisation of a joint, the CHSH value and the classical bound 2 by enumerating sixteen deterministic strategies, the fiber lemma and the swap-dynamics witness by exhausting every function on $\mathbb F_2^2$, a hash-chain ledger with truncation and tamper cases, relabeling, and the three-role gate with its refusals. `code/tests/test_epistemic_kernel.py` holds 26 tests. It does not compute an ℓ¹ defect.

**The Lean package (in this deposit).** `lean4/` is a Lean 4.34.0 package without Mathlib. It contains 29 declarations in four modules, each stated on a finite model:

- `ResultI`: the PR-box four-cycle has no global assignment, and no supported one; a positive-weight joint over assignments cannot marginalise into the PR supports; a classical mixture of two deterministic assignments has a global section.
- `ResultII`: the fiber lemma for arbitrary types; a private fiber blocks full prediction; on $\mathbb F_2^2$ with $\pi(a,b)=a$ no function recovers the state from the report, and under the swap map $\pi\circ F$ does not factor through $\pi$.
- `ResultIII`: hash-chain prefixes verify, so truncation is invisible and completeness needs a tip pinned outside the ledger; a tampered entry fails; relabeling-invariant verdicts and exports are blind to a bijective relabeling, and one non-invariant verdict separates a carrier from its relabeling.
- `ResultIV`: a Lean model of the gate `verify_three_role_authority` with the refusals for self-authorization, self-evaluation, prose standing, a root that is not admitted or equals the proposer or evaluator, and malformed packets; a receipt carries no authority; one refused link poisons a composition.

`lean4/axiom_report.txt` lists `#print axioms` for each of the 29 declarations. Eighteen depend on no axiom. Eleven depend on `propext`, `Quot.sound` or `Classical.choice`; `Classical.choice` enters through the `simp` proofs of the `ResultIV` theorems. All three are on the whitelist of the programme's deposit rules.

**What the Lean package does not do.** It is not linked to the Rust kernel: the model of `verify_three_role_authority` is a re-statement whose simplifications are listed in the docstring of `ResultIV.lean`, and nothing machine-checks that the two agree. It has no linear programme, so the ℓ¹ defect, the dual witness and the strong, logical and probabilistic classification of Result I are not Lean theorems; the Lean statements are the support-level facts. Result III.c (Tarski, Löb) is IMPORTED and not mechanised. Result III.a is a policy invariant by construction. Proposition II-open stays OPEN. In `ResultIV`, distinct identifier strings pass even when they name one agent (`distinct_strings_pass`): identity binding is outside the model.

**Which artifact supports which statement.** Result I at support level: Lean and Python; the ℓ¹ defect and dual witness: Rust only. Result II: Lean and Python. Result III.b and III.d: Lean and Python. Result IV: the Rust gate, a Lean model of it, and a Python model of it, three separate implementations of one policy. The table in section 5 is from the Rust kernel; the CHSH values in it are re-derived in Python.

**Reproduction machinery and receipts.** The commands below are reproduction machinery. A receipt is a dated run recorded here; running a command again produces a new receipt and is not the old one.

| command | tool version | exit | scope |
| --- | --- | --- | --- |
| `python3 -m pytest code/tests -q` | pytest 9.1.1, Python 3.13.16 | 0 | 26 tests, `code/` |
| `lake build` in `lean4/` | Lean 4.34.0, Lake 5.0.0 | 0 | modules `Core`, `ResultI` to `ResultIV` |
| `lake env lean Census.lean` in `lean4/` | Lean 4.34.0 | 0 | 29 declarations; output equals `axiom_report.txt` |
| `python3 tools/replay_lean_axiom_census.py --replay .` | Python 3.13.16, Lean 4.34.0 | 0 | census replay |
| `python3 verify_deposit.py --lean` | Python 3.13.16 | 0 | manifest two-way sweep, Lean build and census, axiom whitelist |

The receipts are from 2026-10-17 on Linux x86_64. The Rust commands of the 2026-10-16 trunk receipts (`cargo test -j 1 -p omega_sheaf_theory`, `-p omega_contracts`) are not repeated here and are not part of this table. The repository holds a 22-test Python harness for the Rust fixtures at `omega_engine_pfp/tests/normal_forms/test_epistemic_no_go_harness.py`; it imports repository modules and is not packaged.

**Version 1.0.0's inline listings.** The Rust and Python listings printed in version 1.0.0 are preserved verbatim, with the review's findings against them, in `docs/legacy_float_kernel_listings.md`. They are not part of this manuscript and are not maintained.

## 7. Corrections from version 1.0.0

Each row names the review finding, the status of the version 1.0.0 statement, and what this version says instead.

| finding of the review | v1.0.0 statement | status | this version |
| --- | --- | --- | --- |
| 1. Privacy fails under dynamics | Prop 2.4 | FALSE | Proposition II-open, with the swap witness recorded (sections 4.2, 5) |
| 2. Weak inference stated, strong-inference theorems used | §2.2, Cor 2.3 | FALSE | Wolpert IMPORTED and unused; pullback apex withdrawn (4.2) |
| 3. Float solver glues CHSH 2 + 4·10⁻⁸; support truncation; numerical rank; non-bijective relabel; budgets | §7, §8 listings | superseded | exact-rational kernel with replayed witnesses, declared dimensions, no relabel routine, typed pivot refusal (6); listings moved to `docs/` |
| 4. Abstract conflates noncommutativity, contextuality, nonzero $H^1$ | Abstract, §1.3 | FALSE | nerve $H^1$ a cover invariant; cohomological obstruction sufficient not necessary; LP decides (4.1) |
| 5. Well-foundedness argument; invariance read as undetectability | §3.2, §3.3 | FALSE | well-foundedness withdrawn; III.d with claims (1) and (2) (4.3) |
| 6. Tarski/Löb without a specified theory; level counter; generator vs stream | §3.1 | under-specified | H3 names the theory; III.c at its scope (2.4, 4.3) |
| 7. Finite entropy ⇏ finite support; Landauer is about erasure; Lemma 2.1 is pigeonhole | §2.1, Lemma 2.1 | FALSE as derivations | H1 declares finite data; physical imports are motivation only (2.4) |
| 8. Authority is policy; Thm 5.1 hypothesis accounting; distinct strings ≠ controllers | §4, Thm 5.1 | overclaimed | H4 and Proposition IV as policy, with delegated standing (2.4, 4.4) |
| 9. Precursor anchors changed meaning | §0, ledger | miscited | section 3 copies each identifier with its source meaning |
| 10. Code broken as printed; absent ledger symbols; f64 and SipHash against a rational/HMAC ledger | §7, §8, ledger | superseded | ledger rewritten against the merged kernel's real symbols |
| 11. Rebuild around four conditional statements; retitle | Thm 5.1, title | accepted | this version's structure and title |
| 12. Scaffolding ("Obligation A", "Knife with One Cut", "sovereign kernel"), duplicate §0, broken delimiters, no bibliography | throughout | accepted | removed; section 9 added |

Two further corrections come from the programme's own note rather than the review: the companion branch's cover-gluing `NoGlobalExtension` is a restatement of "no supported global assignment" and not an independent witness (FOC-035, L035-B6 and L035-B7), and the former Axis 3 citation of NB-9 is dropped because the programme's notebook review refuted NB-9.

## 8. Non-claims and open problems

- Nothing here bounds competence: no capability ceiling is stated or implied.
- Nothing here is a statement about any particular brain, model or prover; the hypotheses must be checked per system, and that check is empirical.
- The physical imports (Bekenstein, Landauer, Holevo, Bell violations, Wolpert) motivate H1 and H2; no proof uses them.
- Self-witnessing, self-modeling, evaluator closure or report integration does not establish phenomenal consciousness (WDP-CH14-N01), and nothing here is a statement about experience.
- Injectivity of a presentation on a declared subspace does not detect inputs outside it (WDP-CH14-N02).
- Result III.d is stated for relabeling-invariant verdicts only; nothing here bounds a verdict that reads the presentation.
- Result IV defines a verification regime; it does not model legal or social authority (WDP-CH15-N02).
- Nothing here says a system cannot know something about itself, or cannot exercise authority delegated to it. The fiber lemma obstructs only answers the available data do not determine; the contract refuses only standing the packet does not carry.
- OPEN: privacy over time (Proposition II-open). A proof needs an intertwining condition on the allowed interventions or a transcript-fiber statement.
- OPEN: whether the claims a self-presenting reasoner makes about its own states form an empirical model on a cover in the sense of section 2.1, and whether their demanded combination fails as in Result I. Result I is established for question contexts; the transfer to self-reports is a research task named and not discharged.
- OPEN: repair versus reinterpretation (section 4.3, III.d) is decided only by a grounding map outside the system; no internal criterion is offered.
- Not mechanised in Lean: the ℓ¹ defect, its dual witness and the strong, logical and probabilistic classification of Result I (Rust only, section 6); the Tarski and Löb forms (IMPORTED); Axis 1 of WDP-CH14-T01 (IMPORTED); Proposition II-open (OPEN); relabeling beyond the permutations of the finite models in `ResultIII`. Result III.a is a policy invariant by construction, and `ResultIV` is a re-statement of the Rust gate with no machine-checked link to it.

## 9. References

Programme monographs.

- [REF-0] Carroll, J. H. (2026). *The Witnessed Difference Programme: A Finite Calculus of Obstruction, Observation, and Quantum Foundations.* Research monograph series 001_finite_obstruction_calculus, paper 000. Chapters 10, 14, 15 and 21 are cited by identifier.
- [REF-0a] Carroll, J. H. (2026). *Note WDP-DOC-EPIS-NOGO-001: the epistemic no-go theorem, corrected, with its kernel.* Documentation folder of paper 000.

Literature. Entries marked with an asterisk are copied from the programme's verified bibliography; the others are to be checked against the publisher record before deposit.

- [REF-1]* Abramsky, S. and Brandenburger, A. (2011). The sheaf-theoretic structure of non-locality and contextuality. *New Journal of Physics* 13, 113036. [arXiv:1102.0264](https://arxiv.org/abs/1102.0264); [DOI 10.1088/1367-2630/13/11/113036](https://doi.org/10.1088/1367-2630/13/11/113036).
- [REF-2] Abramsky, S., Mansfield, S. and Barbosa, R. S. (2012). The cohomology of non-locality and contextuality. *Electronic Proceedings in Theoretical Computer Science* 95, 1–14. [arXiv:1111.3620](https://arxiv.org/abs/1111.3620).
- [REF-3] Wolpert, D. H. (2008). Physical limits of inference. *Physica D* 237, 1257–1281. [arXiv:0708.1362](https://arxiv.org/abs/0708.1362).
- [REF-4] Fine, A. (1982). Hidden variables, joint probability, and the Bell inequalities. *Physical Review Letters* 48, 291–295.
- [REF-5] Tarski, A. (1936). Der Wahrheitsbegriff in den formalisierten Sprachen. *Studia Philosophica* 1, 261–405.
- [REF-6] Löb, M. H. (1955). Solution of a problem of Leon Henkin. *Journal of Symbolic Logic* 20, 115–118.
- [REF-7]* Popescu, S. and Rohrlich, D. (1994). Quantum nonlocality as an axiom. *Foundations of Physics* 24, 379–385. [DOI 10.1007/BF02058098](https://doi.org/10.1007/BF02058098).
- [REF-8]* Frauchiger, D. and Renner, R. (2018). Quantum theory cannot consistently describe the use of itself. *Nature Communications* 9, 3711. [arXiv:1604.07422](https://arxiv.org/abs/1604.07422); [DOI 10.1038/s41467-018-05739-8](https://doi.org/10.1038/s41467-018-05739-8). Cited only through WDP 14.4 as an adversarial test; nothing is imported from it.

## 10. Claim index

`docs/mechanization_map.md` maps each statement of section 4 to its tag, its programme anchor, the Rust symbol or test, the Lean declaration, and the Python test. The programme's packaging rules retire separate claim ledgers from deposits, so the map is a documentation file and not a ledger.
