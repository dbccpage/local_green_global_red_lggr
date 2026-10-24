---
title: "Minds Under Partial Observation"
subtitle: "Retained differences, causal continuation, and accountable self-modification in humans and AI"
author: "Conceptual and mathematical expansion prepared for Jeremy H. Carroll"
date: "21 October 2026"
---

# Abstract

A mind can be studied as a situated organization that retains distinctions and makes them consequential for subsequent perception, inference, and action. This working description does not identify subjective experience with an error term or turn every stateful controller into a conscious subject. Building on the supplied projection-obstruction, adaptive-dynamics, contextual-prediction, and RSI materials, we distinguish informational sufficiency, usable knowledge, future-preserving memory, self-description, and physical or computational self-modification. The most important expansion is from static retained information to **preservation of consequential distinctions through changing actions, representations, and evaluators**. We develop nested observation boundaries, distributed knowledge, action-relative memory, nonlinear composition defects, adaptive error accounting, and robust action conditions. For consciousness, differentiated causal continuation is formulated as a testable candidate supporting condition, not an established necessary-and-sufficient criterion. For LLMs and possible ASI, the same mathematics supplies system-level requirements without assuming human mechanisms or phenomenology. The central risk is not unlimited intelligence as such, but a growing mismatch between what a system can change and what its evidence and checks justify.

**Status:** research expansion and proposed definitions. Generic mathematical implications are proved where used; applications to actual cognition require empirical models. This is not a novelty claim, a clinical assessment method, or a proof that current AI is conscious or incapable of consciousness. AuthorityEffect: None.

# 1. The stronger thesis

The strongest extension of the supplied argument is:

> A cognitive organization does not merely contain differences. It preserves selected differences long enough, and in usable enough form, for them to change what happens next.

This shifts attention from how much information a system stores to what its retained distinctions can do. A notebook, a latent vector, a neural response, a learned skill, a proof, and a memory of an unresolved question are different carriers. Their significance depends on access, decoding, future use, and the reliability of the operations connecting them.

Three layers should remain separate:

1. **A formal account of cognition:** which distinctions support which predictions and decisions under which transformations?
2. **An empirical account of humans and machines:** which actual mechanisms implement those operations and with what reliability?
3. **An account of experience:** which organizations, if any, support felt experience, and why?

Success at the first layer can organize experiments at the second and third. It does not automatically settle either. Conversely, explaining when an experiential capacity disappears need not be identical to explaining what the experience is.

Your updated manuscripts already improve the separation considerably. *Contextual Prediction and Self-Certification* v1.5.1 distinguishes global-distribution obstruction, observation-fiber loss, ledger integrity, provenance, and action safety. The RSI change log records v1.4.0 contracts across changing representations. This expansion uses those distinctions rather than treating the older universal-no-go rhetoric as the current position. Formalization counts in the supplied files remain their reported status; the Lean packages were not supplied and rerun in this task.

# 2. Being, representation, and error

Under your premise that reality is identical to being, a mistaken belief is real as an event without its content being true. A map drawn with the wrong road exists; the road it depicts may not. An illusion is not outside nature, and a correction is another event within nature.

The mathematical consequence is modest but helpful: no external observer is needed to formulate a relation between a representation, a task, and an observation protocol. A state space is a declared model of relevant possibilities, not a claim to possess an exhaustive inventory of being. Its adequacy remains open to testing.

This avoids two opposite mistakes:

- Treating a representation as unreal because it omits information.
- Treating a representation as complete because it is a real physical occurrence.

The same applies to a person's self-description and an LLM's explanation. Both are events with causal consequences. Neither becomes an exhaustive description of its generating process merely by using the first person.

Sequential presentation, linear algebra, and linear dynamics must also remain distinct. Experience may be reported as a sequence without its supporting dynamics being linear. A system may employ a vector representation without its state transitions being linear. Your product-of-marginals retraction is explicitly nonlinear.

# 3. A working vocabulary, with boundaries

**Cognitive organization:** a process that retains distinctions, uses them to represent or discriminate possible continuations, and lets those representations regulate subsequent observation or action.

**Mind:** provisionally, a sufficiently organized, persistent instance of such cognition, including self-regulation where appropriate. This is a working research description, not a necessary-and-sufficient definition. Minimal memory and control occur in simple devices; those properties alone do not establish a mind in the rich human sense.

**Knowing:** having justified, usable access to distinctions sufficient for a specified question or action within an established domain. Information sufficiency, implementation of the decoder, and justification are separate requirements.

**Intelligence:** resource-bounded competence at organizing evidence, memory, inference, and action across a declared range of situations, including recognizing when the current representation is inadequate.

**Learning:** experience-dependent change in representations or operations. Successful learning improves specified future performance under a comparison that does not quietly replace the task with an easier one.

**Conscious experience:** the phenomenal matter under investigation. It is not defined here as prediction error, residual magnitude, reportability, integration, or computational capability.

**Self-maintenance:** preserving the operations and distinctions required for continuing a declared cognitive or functional organization. This is not assumed to entail a desire for survival or permission to resist shutdown.

This vocabulary lets human and artificial systems be compared on explicit properties without declaring them identical.

# 4. A mind is not its report: nested boundaries

Let a modeled situation $x$ produce an available embodied or implemented state $e=E(x)$, and let a report map produce $n=N(e)$:

$$X\xrightarrow{E}\mathcal E\xrightarrow{N}\mathcal N.$$

The phrase "available state" includes every variable accessible to the system for the task, not merely its verbal description. For a human, that might include sensorimotor capacities and nonverbal discriminations. For an AI system, it may include activations, memory, retrieved data, and tool state, subject to the actual architecture.

For any map $q$, let $\sim_q$ mean equality of reports. Then

$$x\sim_E x'\quad\Longrightarrow\quad x\sim_{NE}x'.$$

Reporting may erase distinctions that remain available to other operations. The reverse implication need not hold.

**Example.** Let $e=(a,b)$, report $N(e)=a$, and a permitted action depend on $b$. Two states can produce identical narratives while producing different actions. Report-only failure to recover $b$ is not whole-system failure to retain $b$.

Conversely, if $E(x)=E(x')$ and every subsequent operation has access only to $E$ and the same state-independent randomness, those operations cannot reliably distinguish $x$ from $x'$. Positing an unmodeled channel may change the premise; it is not a conclusion of the original model.

This yields a practical three-way distinction:

1. **Retained and usable, but not reportable through the chosen channel.**
2. **Retained somewhere, but not accessible to the required decoder or action.**
3. **Not retained by any available task-relevant channel.**

Human speech loss, human memory-access failure, and loss of a relevant distinction are therefore different hypotheses. An LLM's failure to verbalize a feature likewise does not establish that no internal computation carries it. But successful verbalization alone does not establish a privileged, accurate introspective readout.

## 4.1 Why "qualia are the residual" is too strong as a conclusion

Your pasted argument ultimately asks for conditions sustaining experience, not an identity between experience and a number. That is the better formulation.

If $N$ is linear and $s$ is a linear section, a residual $e-sN(e)$ identifies what that chosen reconstruction omits. Change $s$, the task, or the representation and the residual can change. Random nuisance data can generate a large residual; an excellent representation can generate a small one. Neither fact determines the presence or richness of experience.

A defensible proposal is narrower: **some experiential distinctions may not survive a particular narrative projection, even when their supporting organization persists.** Whether a particular unreported distinction is experienced rather than unconsciously processed is an empirical and theoretical question, not something the projection theorem decides.

The theorem protects the distinction between a failed reporting channel and a failed underlying process. It does not fill the gap with an automatic consciousness attribution.

# 5. Knowing is a relation, not a stored object

For report $q:X\to Y$ and task $f:X\to A$, exact recoverability means $f=gq$. Thus every distinction erased by $q$ must be irrelevant to $f$.

But the existence of $g$ is not enough to establish usable knowledge. A large integer determines its prime factors; that does not mean a bounded agent can obtain them on demand. A person's access to an archive is not identical to remembering its contents. An AI deployment that can retrieve an answer is not the same object as its bare parameter array.

It is useful to record a knowledge claim as a tuple:

$$\mathcal K=(\text{task},\text{domain},\text{evidence},\text{decoder},\text{warrant},\text{resources}).$$

This is an engineering specification, not a claim to settle epistemology. In empirical applications, certainty is often replaced by calibrated risk and a domain of validity. In mathematics, the warrant may be a proof relative to definitions and axioms. In action, a correct prediction may still be insufficient to authorize the act.

A fixed-evidence reasoner can improve dramatically by finding a better decoder. Research on computationally usable information formalizes why processing can improve accessibility without increasing Shannon information about an unknown variable. [Xu et al.](https://openreview.net/pdf?id=r1eBeyHFDH).

## 5.1 Distributed knowing is real but not magical

Suppose two agents have reports $q_1$ and $q_2$. Their joint evidence partitions states by

$$x\sim_{(q_1,q_2)}x'\iff x\sim_{q_1}x'\text{ and }x\sim_{q_2}x'.$$

Pooling can therefore resolve a task that neither agent can solve alone. If one holds bit $a$ and another bit $b$, neither can determine $a\mathbin{\mathrm{xor}}b$ on all four states, but their joint report can. Duplicating the same bit across a hundred agents does not solve it.

The ability to pool evidence also requires actual communication, trustworthy identification of records, and an implemented decoder. A social group can collectively contain the needed facts without any member or protocol being able to bring them together.

For humans this motivates distinguishing personal recall from supported, distributed competence. For LLM systems it motivates evaluating the model, retrieval system, tools, and memory as a specified whole. Evidence from Internet-search experiments shows that people can overestimate their internal knowledge after using external information; this is one concrete reason to label the boundary. [Fisher, Goddu, and Keil](https://bpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/c/259/files/2020/05/fisher2015.pdf).

# 6. Memory preserves possible futures, not just past descriptions

Let $M$ be a finite state set, $r$ a readout, and $u_a$ the allowed actions. Define future equivalence by agreement of readouts after every finite permitted action word. A memory summary is sufficient for this contract only if it never merges states that a permitted continuation can distinguish.

The supplied papers already develop this criterion and its finite refinement. The expansion for humans and AI is that **a memory contract is indexed by the actions the system may later perform**.

## 6.1 Capability expansion can invalidate memory

Let $\mathcal A\subseteq\mathcal B$ be two action sets. Then

$$m\equiv_{\mathcal B}m'\quad\Longrightarrow\quad m\equiv_{\mathcal A}m'.$$

**Proof.** Every word over $\mathcal A$ is also a word over $\mathcal B$. Agreement for the larger collection implies agreement for the smaller one.

The reverse can fail. If the only action is identity and the report is the first bit of $(a,b)$, retaining $a$ suffices. Add a swap action; the previously discarded $b$ becomes the next first-bit report. The old summary was adequate under the old contract and inadequate under the new one.

For a person, a newly learned skill can make a formerly ignored distinction consequential. For an LLM system, adding a database-write tool, a new retrieval source, or persistent memory can change which historical distinctions matter. For ASI, a capability upgrade is therefore not just "more of the same intelligence": it can change the equivalence relation under which old memory was considered safe.

**Engineering rule:** revalidate memory, evaluation, and safety assumptions when the action interface expands. If the old summary has already discarded a newly necessary distinction, reconstruction may require fresh evidence or an older retained record; renaming the summary does not restore it.

## 6.2 Restoration is behavioral, not necessarily microscopic

A restored state need not reproduce every microscopic detail if it preserves every future distinction in the declared task/action family. Conversely, the same current answer or storage address does not prove restoration.

This gives precise interpretations of recovery from a corrupted memory, migration to a new model representation, or resumption after an interrupted task. The certificate must say what continuity it preserves. Functional equivalence under a test family does not establish sameness of personal identity or continuity of experience.

# 7. Nonlinear compression changes future composition

Your Paper 034 supplies a stronger statement than the linear projection-memory analogy. Let $\Pi$ be a $C^2$ retraction, $m=\Pi(m)$, and $A$ a linear ambient generator. Set

$$P=D\Pi_m,\quad a=Am,\quad v=Pa,\quad n=a-v.$$

For $F_t=\Pi e^{tA}$ restricted to the retraction image, the mixed coefficient of $F_{s+t}(m)-F_s(F_t(m))$ is

$$\mathcal K_{\Pi,A}(m)=PAn+D^2\Pi_m(a,n).\qquad (1)$$

The first term represents discarded motion returning to retained directions. The second is a curvature contribution from the changing compression geometry. It cannot generally be dropped. In your particular marginal-product setting, the relevant Hessian term vanishes on the declared normal directions; that special simplification is not universal.

**Explicit curved example.** Let $u=x+y-x^2$ and $\Pi(x,y)=(u,u^2)$. This fixes every point of the parabola and is a smooth retraction. At $m=(1,1)$ with $A=I$, one has $v=0$, $n=m$, and $PAn=0$, but

$$D^2\Pi_m(a,n)=(-2,-4).$$

Thus a composition defect remains even though the linear return term vanishes. Repeatedly compressing between updates can change later outputs.

For human reasoning, this is a model of how changing conceptual representation can affect composition of inferences, not a derivation of a neural law. For LLMs, it suggests testing whether summarize-then-reason agrees with reason-then-summarize over the declared task family. It does not establish that an arbitrary language summary is a smooth retraction. A discrete commutative-square test may be the appropriate version there.

Nor is this dynamical defect automatically the same as a cochain square defect or a contextuality witness. Your Paper 034 explicitly keeps those constructions separate; a bridge requires specified maps.

## 7.1 Extension to nonlinear ambient dynamics

For a $C^2$ vector field $f$ with local flow $\Phi_t$, replace $Am$ by $f(m)$. With $a=f(m)$ and the same definitions of $P,v,n$, the mixed coefficient becomes

$$\mathcal K(m)=P\,Df_m[n]+D^2\Pi_m[a,n].\qquad (2)$$

**Proof.** The direct-flow mixed derivative is $P Df_m[a]+D^2\Pi_m[a,a]$. The compressed composition has derivative $P Df_m[v]+D^2\Pi_m[v,a]$. Their difference is (2). This is a local calculus consequence, not a new empirical law.

Two counterexamples clarify the interpretation. For $\Pi(x,y)=(x,0)$ and $f=(0,1)$, discarded motion is nonzero but the retained dynamics close exactly: the hidden variable never returns. For $f=(y^2,1)$, starting on the retained axis gives $x(t)=x(0)+t^3/3$. The mixed quadratic coefficient vanishes, but the composition defect is $st(s+t)$ in the first coordinate. Neither positive leakage nor zero leading defect alone settles the memory question.

The correct question is whether discarded distinctions can become consequential under the allowed continuations.

# 8. Learning changes a representation; it must not erase the bill

Your adaptive quantum paper offers a useful architectural lesson: enriching the representation can reduce future error production without deleting accumulated past uncertainty. A state-preserving cluster merge preserves the current approximate state; it does not make that state equal to the unknown exact one.

For a human, learning a new vocabulary does not automatically correct an old mistaken recollection. For a machine, migrating a memory into a richer schema does not validate unsupported facts already stored there. A new explanation can make an error more articulate.

Successful learning therefore needs both:

- A mechanism for improving future inference, retention, observation, or action.
- An evaluation that preserves the question being answered and the evidence against which success is judged.

Deleting troublesome observations can reduce an internal inconsistency score while worsening knowledge. Changing the benchmark can increase a reported score without improving the original capability. These are not inevitable consequences of learning; they are identifiable failure modes.

## 8.1 A hybrid error ledger for changing representations

Here is a precise conditional extension of your error-accounting programme. Let a reference trajectory satisfy $\dot x=f(t,x)$ in a common finite-dimensional Euclidean comparison space. Assume the relevant trajectories remain in a region where

$$\langle x-y,f(t,x)-f(t,y)\rangle\le\lambda(t)\|x-y\|^2.$$

Let $\widehat x$ be an approximation, absolutely continuous between finitely many representation switches $\tau_j$. Assume integrable stability and defect bounds, finite switch costs, and existence of the trajectories throughout the stated interval. Suppose verified bounds cover its initial error $e_0$, actual differential defect $\eta(t)$, and switch jumps $\epsilon_j$:

$$\|x(0)-\widehat x(0)\|\le e_0,$$

$$\|\dot{\widehat x}-f(t,\widehat x)\|\le\eta(t),\qquad
\|\widehat x(\tau_j^+)-\widehat x(\tau_j^-)\|\le\epsilon_j.$$

Write $\Lambda(t,s)=\int_s^t\lambda(u)\,du$. Then

$$\|x(t)-\widehat x(t)\|\le E(t),$$

where

$$E(t)=e^{\Lambda(t,0)}e_0+\int_0^t e^{\Lambda(t,s)}\eta(s)\,ds
+\sum_{\tau_j\le t}e^{\Lambda(t,\tau_j)}\epsilon_j.\qquad (3)$$

**Proof.** Between switches, differentiating the error norm gives the upper derivative bound $D^+\|x-\widehat x\|\le\lambda\|x-\widehat x\|+\eta$. At a switch, the triangle inequality adds at most $\epsilon_j$. Integrating the scalar comparison inequality and iterating over switches gives (3). Negative $\lambda$ is allowed and represents contraction.

The common comparison space is essential. If successive memories have different latent coordinates, first supply decoders $D_j$ into that space. The adapter cost is the difference between decoded states, not subtraction of incomparable embeddings.

If a decoder $D(z,\theta)$ changes while the state changes, its derivative includes both

$$\dot{\widehat x}=\partial_zD\,\dot z+\partial_\theta D\,\dot\theta.$$

Ignoring the second term can understate the actual defect. Numerical error, interpolation error, and mismatch between the nominal world model and the reference dynamics must also be included. A small sampled ideal residual alone is insufficient.

Equation (3) covers representation changes while the reference state stays continuous. If an intervention resets the actual system, a separate reset condition is needed, for example

$$\|R_j(x)-\widehat R_j(y)\|\le L_j\|x-y\|+\delta_j,$$

which gives $E^+\le L_jE^-+\delta_j$. If a new policy changes the environment's trajectory, either compare under the same realized actions or establish a closed-loop simulation/stability result. An old open-loop forecast is not a certificate for arbitrary new actions.

This is a rigorous model-level contract. Actual human or LLM cognition does not currently come with the verified full-state models needed to apply it wholesale. Finite software subsystems and controlled tasks are realistic first targets.

## 8.2 Decision confidence can be weaker than state accuracy

Suppose each action value $V_a$ is $K$-Lipschitz and a computed score $s_a$ has evaluation error at most $\zeta$ at $\widehat x$. Then score error at the true state is at most $b=KE+\zeta$. Choosing the largest score incurs regret at most $2b$. A score gap greater than $2b$ guarantees the chosen action is uniquely optimal in that declared value model.

**Proof.** If $a^*$ is truly best and $\widehat a$ maximizes the scores, then $V_{a^*}(x)\le s_{a^*}+b\le s_{\widehat a}+b\le V_{\widehat a}(x)+2b$.

A model can therefore be inaccurate in irrelevant details yet support a robust decision. But the theorem does not establish that the value function captures the right human interests or that the action is permitted. Prediction, value specification, and authority remain separate.

## 8.3 Three failures that must not be confused

1. **The certificate fails:** the available upper bound no longer proves a tolerance.
2. **The task performance fails:** the actual error or regret exceeds the tolerance.
3. **The experiential process fails:** experience ceases.

The first does not imply the second, and neither establishes the third. An upper error bound can grow while the actual error remains zero. A valid lower bound or observed violation is needed to establish actual task failure. A theory and evidence connecting task or dynamical conditions to experience are additionally needed for the third claim.

This distinction is central to your proposed "conditions sustaining experience" programme. A correction window is a window for a stated guarantee, not a universal countdown to the disappearance of a mind.

# 9. Self-knowledge and self-certification

A system's own report can carry genuine information without being a complete audit of the process producing it. An external observer can also lack decisive information. The issue is not simply inside versus outside; it is what each accessible channel discriminates and what checks it can support.

Let $c:X\to\{0,1\}$ mean that a candidate satisfies a declared correctness condition. A report-only certificate $a:Y\to\{0,1\}$ is sound when $a(q(x))=1$ implies $c(x)=1$.

The maximally permissive sound certificate accepts precisely those reports whose entire fiber is correct:

$$a(y)=1\quad\Longleftrightarrow\quad q^{-1}(y)\subseteq c^{-1}(1).\qquad (4)$$

**Proof.** If a fiber contains an incorrect state, accepting its common report is unsound there. If all states in the fiber are correct, acceptance is sound. This characterizes possibility, not efficient computability of the fiber condition.

A proof-carrying solver can perform useful self-checks because its checker has a mathematically specified relation to the candidate and statement. That does not prove its sensors, specification, hardware, or evidence inventory are complete. Distinct checker identities may reduce some shared risks but do not themselves establish independence. A self-check is neither automatically worthless nor automatically sufficient.

The human parallel is not that introspection is always false. It is that reasons offered after an action, remembered evidence, and the full causal process are different objects. The machine parallel is not that every generated explanation is deceptive. It is that an explanation must not be treated as a verified execution trace without evidence of that connection.

## 9.1 Contextual prediction is not forbidden by contextuality

Your current contextuality theorem asks whether several context-indexed distributions can arise as marginals of one nonnegative global distribution over fixed outcome labels. Failure of that construction does not prevent a predictor from storing and using the context-specific distributions themselves.

For humans and LLMs, changing a question can change the state, incentives, interpretation, and report channel. These are ordinary candidate explanations for context dependence. A Bell-style or sheaf contextuality application needs explicit contexts, shared measurement identities, compatible marginals, and a justified comparison class. It cannot be inferred from inconsistent answers alone.

The useful architectural lesson is broader and safer: **local success certificates need composition assumptions**. A truthful data source, correct parser, and compliant permission packet can still fail jointly if they refer to different versions, assumptions, or objects. The obstruction can reside in their interfaces rather than in any one component.

# 10. Differentiated causal continuation and human experience

Your candidate condition can now be sharpened:

> Experience may require an organization in which registered distinctions remain differentiated, enter causally relevant relations, and sustain further organized distinctions over an appropriate timescale.

This remains a necessary-condition hypothesis. Writing $C\Rightarrow K$ makes $\neg K\Rightarrow\neg C$ a valid inference only after the substantive premise is established. A failed measurement $\widehat K$ is not automatically a failed capacity $K$.

The proposal distinguishes three possible interruptions:

- **Isolation:** a local difference cannot influence the relevant wider organization.
- **Stereotypy:** activity propagates, but different perturbations collapse into the same response pattern.
- **Interrupted continuation:** a difference initially matters but loses its organized causal influence across the relevant interval.

These are distinct properties of a model. None by itself is an established universal consciousness switch.

## 10.1 The empirical foothold is real

Sarasso and colleagues studied unresponsiveness induced by propofol, xenon, and ketamine. Propofol produced localized low-complexity responses; xenon produced widespread but stereotyped low-complexity responses; ketamine preserved complex responses despite unresponsiveness, with later reports of vivid experiences. The study directly motivates separating response spread, complexity, and overt responsiveness. Retrospective reports remain imperfect temporal evidence. [Sarasso et al., 2015](https://pubmed.ncbi.nlm.nih.gov/26752078/).

Pigorini and colleagues found that during NREM sleep in eight epilepsy patients, an OFF-period interrupted the phase-locked response to intracerebral stimulation even though activity subsequently resumed. This is relevant to continuation rather than mere activity, but does not show that all NREM sleep is experience-free. [Pigorini et al., 2015](https://pubmed.ncbi.nlm.nih.gov/25747918/).

The importance of separating cognition from outward response is reinforced by task-based EEG/fMRI findings of cognitive motor dissociation: a six-center study detected command-related responses in 60 of 241 adults without observable command responses. This was a convenience sample, not a universal prevalence estimate; negative task results also have several possible explanations. [Bodien et al., 2024](https://www.nejm.org/doi/10.1056/NEJMoa2400645).

These studies support careful measurement of hidden capacities. They do not establish the proposed condition as necessary for every experience, nor supply a consciousness threshold applicable to AI.

## 10.2 A quantitative candidate, not an experience meter

For a local linearized model $\delta x_{k+1}=A\delta x_k$, perturbation $\delta x_0=Bu$, and recorded output $y_k=C\delta x_k$, define the stacked continuation map

$$\mathcal O_Hu=(CABu,CA^2Bu,\ldots,CA^HBu).$$

Its Gram matrix is

$$W_H=\sum_{k=1}^H B^T(A^k)^TC^TCA^kB,$$

and

$$\|\mathcal O_Hu\|^2=u^TW_Hu.\qquad (5)$$

**Proof.** Expand the squared norm of the stacked response; $W_H=\mathcal O_H^T\mathcal O_H$.

The kernel identifies perturbation differences that the declared output channel cannot distinguish over that horizon. Singular values quantify sensitivity and conditioning after units, normalization, and noise floors are specified. A late-window version tests sustained rather than immediate influence; a remote-output channel tests spread beyond the perturbation site.

Yet an array of uncoupled memory registers can have full observability rank. A noisy signal can have high raw complexity. Neither establishes integration or experience. Measuring the narrative channel and measuring internal continuations are also different choices of $C$.

The matrix supplies a candidate assay of an operational property. The hypothesis connecting that property to consciousness is separate. For strongly nonlinear systems, the local model needs a validated perturbation range and horizon, or should be replaced by an explicitly estimated intervention-response distribution.

## 10.3 What would make the conjecture scientific?

Choose a restricted population and state family, define the continuation measure before examining outcomes, and test whether independently supported experience can occur when that measured capacity is absent. Keep separate labels for overt responsiveness, reported experience, inaccessible content, and uncertain status.

Compare differentiation, persistence, and propagation against simpler predictors such as response amplitude. Control recording quality, stimulation effectiveness, and report demands. Hold out people and a state or intervention class. A measure that merely tracks the ability to answer the question has not solved the report-boundary problem.

Repeated positive evidence of experience despite a validated absence of the proposed operational condition would challenge the preregistered necessary-condition hypothesis. A low score plus no later recollection would not uniquely confirm it. Preserved capacity without experience would challenge a sufficiency claim, not a necessity-only claim.

Human perturbation or anesthesia research belongs in qualified, ethically approved studies; the framework is not an individual diagnostic procedure. The broader need for explicit competing predictions is underscored by the 2025 adversarial test of global neuronal workspace and integrated information theories, which challenged predictions of both rather than establishing a single universally accepted theory. [Cogitate Consortium](https://www.nature.com/articles/s41586-025-08888-1).

# 11. What changes for LLMs and possible ASI?

## 11.1 Specify the object before making a claim

Distinguish at least four objects:

1. **A trained model:** parameters and architecture defining a conditional computation.
2. **A running inference process:** activations, context, sampling state, and any implemented caches.
3. **A persistent tool-using system:** the model plus memory, retrieval, tools, update rules, and execution controls.
4. **A deployed capability:** that whole system acting under particular tasks, permissions, environments, and resource limits.

A fixed parameter array is not by itself an ongoing self-maintaining process. A running model can perform substantial computation without updating its weights. A scaffold can preserve state across calls even when the model alone does not. Online training, prompt changes, memory updates, and code changes are different forms of adaptation.

This distinction should also be applied to humans: an isolated verbal answer, a person across time, and a person supported by tools and other people are different analytical boundaries. The framework gains explanatory power by declaring the boundary, not by calling everything a mind.

## 11.2 Three levels of self-modeling

- **Descriptive self-model:** produces statements about its own properties.
- **Predictive self-model:** predicts how specified interventions change its performance or behavior.
- **Intervention-validated self-model:** those predictions survive controlled changes and independently evaluated outcomes.

A system can be fluent at the first and poor at the second. A system can be strong at the second within a domain without possessing a complete account of itself. The third is the useful engineering target: test memory removal, tool unavailability, representation migration, and evaluator changes against predictions made in advance.

These tests establish functional capacities. They do not by themselves decide experience. Indicator-based AI-consciousness research similarly distinguishes theoretical indicators from definitive proof; applying it requires substantive assumptions about which theories and properties generalize across substrates. [Butlin et al.](https://arxiv.org/abs/2308.08708).

## 11.3 Intelligence and consciousness are separate axes

A possible ASI could be highly capable while uncertain about some facts, unable to verify some self-modifications, and subject to hidden-state obstructions. None of those limits makes superhuman capability impossible. Nor would superhuman capability establish subjective experience.

The converse separation matters too: difficulties with language, calculation, memory, or outward response do not justify dismissing a human's possible experience. The research programme should not use task competence as a proxy for moral status or consciousness.

## 11.4 What must be managed

The most actionable danger is **capability growth without corresponding preservation of justified control**. A system may gain new action channels faster than its memory, forecasts, evaluation, and permissions are revalidated.

For finite nonempty admissible state and action sets, and a report $y$ in the observation image, let $\operatorname{Safe}(x)$ be the actions safe in admissible state $x$. Uniformly safe report-based action requires choosing from

$$\bigcap_{x\in q^{-1}(y)}\operatorname{Safe}(x).\qquad (6)$$

If that intersection is empty, no deterministic action based only on $y$ can guarantee safety across the modeled alternatives. For these finite action sets, randomization cannot give almost-sure safety in every admissible state unless every action assigned positive probability belongs to the intersection. This follows directly from the same-report premise. If a safe no-op exists, it may preserve safety while failing the task: safety is not liveness.

The constructive options are to acquire a separating observation, restrict the action scope, improve the model, adopt a separately justified fallback, or retain uncertainty. Declaring confidence cannot make an empty intersection nonempty. The actual safety sets are assumptions to validate, not something supplied automatically by notation.

For humans, institutions distribute some of these burdens among expertise, records, review, and authority. For AI systems, the burdens should be explicit at the interface: what can be proposed, what can be checked, and what can be executed. A permission packet can be well formed while its action is unsafe; a correct theorem can be irrelevant to the actual decision.

This is not a recipe for making systems fearsome. It identifies where powerful systems require more careful control: expanding permissions, changing objectives, manipulating evidence channels, or modifying the very evaluators used to declare success.

# 12. A concrete programme spanning humans and machines

## Study A: retained difference versus narrative report

Use a task with two separable channels: an explicit report and a later nonverbal or operational choice. Vary which distinctions reach the report while preserving or disrupting the underlying task memory. For machine experiments, use controlled synthetic states and separate output heads or tools. For human research, use established behavioral paradigms rather than assuming an exact hidden-state model.

Test whether report-equivalent states remain behaviorally distinguishable. This demonstrates a report boundary, not consciousness. A failure of both channels is also inconclusive about every possible retained mechanism unless the model covers them.

## Study B: action expansion and summary sufficiency

Build a finite action system with a computable future-equivalence quotient. Test summaries under the original action family, then add a new permitted action. Compare no migration, migration using full retained records, and acquisition of a targeted new observation.

Prediction: a previously sufficient summary may fail specifically on the new action-dependent tasks. A valid migration must restore the newly required distinction or explicitly narrow its claim. In an LLM implementation, distinguish summarization loss from retrieval failure and decoding error.

## Study C: honest adaptive error accounting

In a known small dynamical system, compare representation enrichment, lossy compression, and decoder changes. Include a treatment that dishonestly resets accumulated uncertainty to zero after each upgrade. Compare the declared bound with the reference trajectory and task decisions.

The honest ledger should enclose error under its assumptions; the reset treatment admits counterexamples. This tests a mathematical contract, not a theory of human neural learning. For LLM agents, initially apply it only to components with known state transitions or verifiable task semantics.

## Study D: self-model prediction under intervention

Ask a system to predict its performance when a memory segment, tool, or context distinction is withheld. Freeze those predictions, perform the specified ablation, and score externally. Compare descriptive self-reports against intervention-tested prediction.

Control for information leaks and prompt-induced changes in the task. Similar human and machine protocols can compare functional calibration while allowing different underlying mechanisms.

## Study E: differentiated continuation in human research

Use the preregistered profile in Section 10, with separate responsiveness and experience-status measures. Seek dissociations that defeat simplistic accounts based only on activity, spread, or reportability. Do not transfer human thresholds to token streams or transformer activations.

Across all studies, publish failures, negative controls, resource costs, and uncertainty. A theory earns explanatory value by distinguishing failure mechanisms that previous methods conflated.

# 13. The resulting account of mind

The proposed picture can now be stated without overstating it:

- A mind is not outside the world it models. Its representations, errors, and corrections are processes within its situation.
- Knowledge is not a complete inner replica. It is justified usable discrimination for particular questions and actions.
- Memory is not just a record of the past. It preserves distinctions that may matter under future operations.
- Learning changes what is retained, accessible, inferable, and actionable. Successful learning must not be defined solely by a reduction in the learner's own residual.
- Self-knowledge is partial but can be genuine. Its scope depends on channels, tests, and inference, not merely on whether the description originates inside or outside the system.
- Experience may depend on an organization sustaining differentiated causal continuations, but that necessary-condition proposal remains empirically open. A mathematical residual is not thereby the experience itself.
- More intelligence can reduce computational limitations without eliminating information, model, or verification limits. More capability may create new memory and control obligations.

**The constructive goal is a reasoner that notices when its current distinctions no longer support what it is about to claim or do, and can acquire, preserve, or reorganize the needed distinctions without pretending that a change of description has settled the world.**

That is a programme for human learning, collective knowing, LLM engineering, and the management of possible ASI. Its force comes from explicit, testable relations, not from declaring any of those systems omniscient, unreal, or impossible.


# Appendix: source scope and executed illustrations

## Supplied material used

This expansion is based on the pasted mind/obstruction and experience-support argument; *Projection Obstruction for Factorized States* v6.9.18; Paper 033, *Certified Adaptive Quantum Dynamics from Projection Residuals*; Paper 034, *Higher-Cell Product Retractions, Simplicial Cochains, and Finite Retraction Dynamics*; *Contextual Prediction and Self-Certification* v1.5.1 and its math spine; and the supplied relational-RSI v1.4.0 change log and math spine.

The source-specific focus was on the observation/report distinction, actual-defect error bounds, nonlinear retraction geometry, context-indexed prediction, and contracts for changing memory and actions. This is an expansion of those results, not an exhaustive republication audit of the long projection monograph. The RSI manuscript body itself was not among these eight attachments; claims about that revision are attributed to its supplied change log and mathematical spine. Historical proof counts, named Lean declarations, and repository test reports were not independently rerun here. None of the source files was edited.

## New illustrations executed

The accompanying mind_extension_tests.py passed six deterministic test groups with 21 assertions in the available environment. It checks:

1. Complementary distributed observations solve XOR while duplicated observations do not.
2. Report-only insufficiency can coexist with a sufficient retained state.
3. Adding a swap action invalidates a first-bit summary previously adequate under identity-only updates.
4. A nonlinear retraction has mixed composition-defect coefficient (-2, -4), including a curvature contribution when the linear return term vanishes. Exact polynomial and optional symbolic calculations agree; a finite-difference check has maximum error about 5.12e-7.
5. A sufficient error certificate can expire while actual error remains zero; decision margins and representation/reset costs require separate accounting.
6. Independent memory registers can be fully observable without cross-coordinate coupling, demonstrating that observability rank alone is not integration or consciousness.

Python's standard library is sufficient for the core suite; NumPy and SymPy enable two additional checks when available. The standard-library-only path has 19 assertions. The script writes a same-directory JSON result file. No network, model API, credentials, human experiment, or live LLM trial is involved. These examples illustrate mathematics; they do not formally verify the full propositions or empirically establish the cognitive applications.

## Recommended next paper boundary

A focused follow-up paper could present three clearly labeled parts: generic preservation theorems; controlled artificial-agent tests; and the separately testable human continuation-capacity hypothesis. Keep claims of phenomenal identity out of the theorem layer. Keep successful runtime checks distinct from proofs of their specifications. Keep permission to act distinct from evidence that an action is safe.

The strongest single question is: which distinctions must survive a particular self-change so that the system's subsequent claims and actions remain warranted?
