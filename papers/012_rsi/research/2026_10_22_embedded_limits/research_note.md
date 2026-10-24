# Knowing and learning from inside the world

Research extension for the RSI series, 22 October 2026. This is a research dossier with a checked formal core, not a replacement release of papers 000 or 001.

## 1. The working rule and the scientific question

**The world is what it is. There is no outside or observer from nowhere.**

An agent, its instruments, its records, its memory, its computations, its evaluator and its interventions all belong to the world. An evaluator implemented by another machine is another physical subsystem, not an exception to this rule. This program introduces no phenomenal variable. Its objects are records, distinctions, dynamics, prediction, action, error and resources.

The productive question is: which distinctions can a particular subsystem preserve or establish, about which tasks, through which interactions, with which resources? An exact limit specifies those objects. It does not infer universal ignorance from finite access or universal stagnation from a bounded example.

An ambient set in a mathematical model does not posit a physically available omniscient observer. It supplies semantics for comparing candidate histories. The agent has access only to its modeled record. A theorem quantified over modeled histories does not grant the agent the ability to enumerate them, nor establish that the model covers reality.

The governing distinction is between what is true, what a record determines, what an implementation can compute, and what a policy permits. Conflating these makes an impossibility claim stronger in prose than in mathematics.

## 2. Exact knowledge from a record

Let X be a declared class of admissible histories containing the agent and its interactions. Let r map histories to the agent's current record. At history x, define the compatibility class

$$
C_r(x)=\{y\in X:r(y)=r(x)\}.
$$

A proposition p is determined by that record when it holds throughout this class:

$$
K_r p(x)\quad\Longleftrightarrow\quad\forall y\in C_r(x),\ p(y).
$$

The actual-history premise x in X makes this factive: determination implies p(x). It is a semantic criterion, not an algorithm that endows the agent with logical omniscience. Correctness also depends on not excluding the actual history through an incorrect model.

For an exact task f, recovery from the record is possible precisely when equal records imply equal task values:

$$
r(x)=r(y)\ \Longrightarrow\ f(x)=f(y).
$$

For a nonempty finite model, select a representative of each reached record class and define the decoder by evaluating f on the representative. Constancy makes the choice irrelevant. Conversely, any decoder must give the same answer to equal records. The Lean theorem `recoverable_iff_fiber_constant` supplies this equivalence given an explicit representative function satisfying its stated reachable-record condition; it does not hide a physical oracle in that function.

For finite rational-valued f under absolute loss, the exact error floor is

$$
\inf_d\max_{x\in X}|d(r(x))-f(x)|
=\frac12\max_{r(x)=r(y)}|f(x)-f(y)|.
$$

Proof: within each fiber, the two extreme values force any proposed answer to incur at least half their gap; their midpoint attains that error for every value between them. Taking the largest fiber gap gives the result. The code implements the finite extrema calculation and a separate pair-based checker. This dossier does not assert a Lean proof of this scalar minimax equality; its generic formal core concerns factorization and dynamics.

The obstruction is task-relative. Two histories can differ in their microstates while agreeing on every question the agent needs to answer. Such compression is sufficient. A finite report is not automatically inadequate, and an invisible distinction is not automatically an important distinction.

Postprocessing a fixed record cannot split an existing record class. Nevertheless, better computation can find a correct decoder that a weaker program failed to compute. Information loss and computational difficulty are different limitations.

The statistical extension replaces deterministic collisions with indistinguishable or nearby observation laws. Fano's inequality bounds identification error using information about a finite hidden index; its binary case requires care because the coarse multiway bound can be vacuous. Adaptive sampling needs conditional information accounting, not an IID formula applied after arbitrary selection. See Scarlett and Cevher, Theorem 1 and the adaptive-sampling sections. [Primary text](https://arxiv.org/pdf/1901.00555).

## 3. Remembering means preserving declared future distinctions

A memory should preserve what future use requires, rather than retain every historical byte or every linguistic detail. Declare an action family A, an update rule T and a readout f. Define

$$
x\equiv_{A,f}y\quad\Longleftrightarrow\quad
\forall w\in A^*,\ f(T_w x)=f(T_w y).
$$

This is the largest action-stable relation preserving the readout. The Lean file proves equivalence properties, stability under an action, and maximality relative to every supplied stable relation. In a finite deterministic model, partition refinement computes its classes. A separate product-state search returns an action word witnessing inequivalence.

An implemented memory m, update u and decoder d preserve the readout for every finite permitted action word when their diagrams commute:

$$
d(m(x))=f(x),\qquad m(T_a x)=u_a(m(x)).
$$

This implication is checked in `implemented_memory_preserves_future`. It exposes a useful implementation obligation: prove or independently check what the updater actually does. Merely defining a favorable quotient is insufficient.

If there are k future-equivalence classes, every exact deterministic memory needs at least k distinguishable reached states; the quotient attains k. A fixed-length binary encoding therefore needs at least ceiling(log2 k) bits. This is a cardinality argument, not a statement about variable-length expected code length or the entire universe's storage capacity.

The four-state example has readout (0,0,1,1). With only identity permitted, two memory classes suffice. Adding the action (0,2,1,3), which exchanges the two middle states, requires four classes. States 0 and 1 share the old record but differ after that action. More future tasks can require finer memory. They do not retroactively make the old memory incorrect for the old task.

For stationary stochastic processes, Shalizi and Crutchfield identify histories with the same predictive future distribution and establish predictive sufficiency and minimality, with almost-sure qualifications. This is the appropriate stochastic counterpart, not a claim that every finite archive estimates the true causal states. [Primary text, causal-state and minimality results](https://arxiv.org/pdf/cond-mat/9907176).

For controlled processes, Littman, Sutton and Singh represent state by action-conditional predictions of future tests. Their finite-rank representation result motivates storing operational predictions rather than assuming privileged access to hidden state. Learning the necessary tests and obtaining reliable data remain additional obligations. [Primary text](https://proceedings.neurips.cc/paper_files/paper/2001/file/1e4d36177d71bbb3558e43af9577d70e-Paper.pdf).

Tishby, Pereira and Bialek's information bottleneck makes relevance an explicit compression objective for a declared joint distribution; Strouse and Schwab distinguish objectives that favor deterministic compression. These optimize specified information criteria. Neither objective alone certifies every future task or protects against a changed distribution. [Information bottleneck](https://arxiv.org/pdf/physics/0004057), [deterministic information bottleneck](https://arxiv.org/pdf/1604.00268).

## 4. All-task memory has a stronger price

A representation that preserves one task can discard distinctions irrelevant to that task. A representation required to preserve every downstream decision problem has a much stronger obligation.

Use two experiments E and F indexed by the same parameter theta. Define directed deficiency with the conventional half-L1 total variation norm:

$$
\delta(E,F)=\inf_K\sup_\theta
\frac12\lVert K E_\theta-F_\theta\rVert_1.
$$

Here K is a stochastic postprocessing kernel from E's outcomes to F's outcomes. Direction matters: this measures how well E can simulate F. On finite alphabets it is a linear program. Zero deficiency gives exact simulation. An attaining kernel with deficiency at most epsilon transfers any F decision rule to E with at most epsilon additional expected loss when loss lies in [0,1]. Compose the rule with K and use the total-variation expectation bound. This is a mathematical argument here; no LP implementation or Lean proof of deficiency is claimed in this dossier.

Van Rooyen and Williamson connect decision-risk differences, deficiency and generic features, and characterize universal feature quality through reconstruction. Their variational divergence is L1, twice the total variation used above. That normalization must be translated before importing numerical constants. Their prior-weighted formulation must also be distinguished from the supremum-over-parameters definition above. [Primary text, Theorems 1 and 3 and Appendix 7.5](https://arxiv.org/pdf/1402.4884).

The extension to paper 001 is concrete: encode this finite deficiency LP using its exact simplex, independently check original-input kernels and residual bounds, then prove the corresponding bounded-loss transfer theorem. This would provide a meaningful residual for memory transformations across a declared family of decisions. A feature reconstruction score or embedding distance is not automatically that certificate.

For quantum memory, the simulation kernel must satisfy the required quantum physical admissibility conditions. Buscemi develops a quantum comparison theory; comparisons based on restricted classical tests must not be silently promoted to existence of a completely positive channel. Ancillary tests and the theorem's exact conditions matter. [Primary text](https://arxiv.org/pdf/1004.3794).

## 5. Learning can change the information boundary

An observation that splits a problematic class changes what the record determines. This is ordinary acquisition of information by an embedded subsystem. It does not require an outside observer.

For a finite class S, deterministic non-destructive tests Q, scalar task f and required error epsilon, define the optimal worst-case number of queries:

$$
D_\epsilon(S)=0\quad\text{if}\quad
\max_{x\in S}f(x)-\min_{x\in S}f(x)\leq2\epsilon;
$$

otherwise,

$$
D_\epsilon(S)=1+\min_{q\in Q}\max_{z:q^{-1}(z)\cap S\ne\varnothing}
D_\epsilon(S\cap q^{-1}(z)).
$$

Only strictly splitting tests are eligible. A missing feasible continuation has infinite cost. This follows by induction on the finite class size: every decision tree chooses a first test and must solve all possible branches; conversely, combine an optimal first test with optimal child trees. A successful leaf supplies its midpoint decoder.

The implementation limits this exact search to twelve worlds and sixteen tests. It independently replays every branch and searches for any strategy one query shallower. No Lean refinement proof for that Python search is asserted.

Example: four possible task values 0,1,2,3 and tests

```text
q0 = (0,0,1,1)
q1 = (0,1,0,0)
q2 = (0,0,0,1)
```

Ask q0 first, then q1 on its first branch or q2 on its second. Two adaptive queries suffice. Every fixed selection of two tests leaves a task collision; all three fixed tests suffice. Restricting the available test panel can make identification impossible, even with arbitrarily much computation. This supplies both an exact limit and a constructive way to improve it.

These tests do not change the unknown state. Destructive measurements, experiments with side effects and policy-dependent transitions require a controlled belief-state model. A separating query is not necessarily safe or available. Permissions, costs and admissibility must constrain Q before solving the planning problem.

Angluin's exact learning result is a valuable constructive comparison: regular sets can be learned with membership and equivalence queries under a minimally adequate teacher. The teacher is a specified resource. A practical system without equivalence-query access does not inherit the guarantee. [Primary text](https://homepages.math.uic.edu/~lreyzin/papers/angluin87.pdf).

## 6. Self-knowing is possible without universal self-prediction

The distinction between a self-readout and a universal evaluator is essential. An agent can read a stored version, inspect an accessible register, validate a bounded computation, or maintain a certificate about a specified subsystem. Such tasks have the same fiber criterion as any other task.

Within the record semantics above, the proposition that the record equals its present value is determined. Determination also has positive introspection:

$$
K_r p(x)\ \Longrightarrow\ K_r(K_rp)(x).
$$

Every history sharing x's record has the same compatibility class, so it determines the same p. Both statements have constructive Lean proofs here. This semantic result does not guarantee an arbitrary bounded agent can calculate or express all such propositions.

A Boolean predictor confronted with the response opposite its announced bit cannot predict that response correctly. The formal contradiction requires that adversarial response coupling. It does not apply to every private state variable or prohibit every iterated knowledge statement. Our Boolean theorem isolates exactly this obstruction.

Wolpert's physical inference devices organize prediction and recollection as relations over world histories. His mutual-inference impossibility requires setup distinguishability; the paper explicitly says the condition is essential. Its existence results permit devices that infer particular functions. The correct import is a quantified boundary, not that no subsystem can know itself. [Physical inference](https://arxiv.org/pdf/0708.1362), [extended knowledge formalization](https://arxiv.org/pdf/1711.03499).

Logical Induction supplies a constructive counterweight: its computable belief process has introspection, paradox-resistance and qualified future-self-trust theorems. These are asymptotic or sequence-indexed guarantees under a deductive process and efficient-trader criterion, not a deployable efficient universal truth procedure. [Primary text, Theorems 4.11.1, 4.11.2 and 4.12.4](https://arxiv.org/html/1609.03543).

Reflective oracles avoid certain diagonal contradictions by permitting random answers at specified boundaries. Their existence theorem does not give an implementable external oracle; they are idealized mathematical models of mutually embedded reasoners. [Primary text, Theorem 2.1](https://arxiv.org/pdf/1508.04145).

## 7. Intelligence and learning need explicit resource contracts

A useful capability statement specifies an environment class, observations, permitted actions, objectives, prior or worst-case criterion, and resource limits. Different choices induce different orderings of agents. A claim that an agent is intelligent without those indices may be useful colloquially, but supplies no exact mathematical bound.

Legg and Hutter define a general intelligence measure through weighted performance across environments. Leike and Hutter show substantial dependence on the chosen universal prior. This does not make concrete capability comparisons meaningless. It means that the weighting and coding choices belong in the statement. [Definition](https://arxiv.org/pdf/0712.3329), [prior-dependence results](https://arxiv.org/pdf/1510.04931).

More explicitly, fix evidence, prior and loss. If a bounded executable rule class is contained in the full rule class, its best achievable risk is the evidence-limited Bayes risk plus a nonnegative computational excess. Better computation can reduce the excess without supplying new observations. New observations can reduce the evidence floor. More memory can preserve additional future distinctions. The three operations are not interchangeable.

Chen, Papadimitriou and Peng prove worst-case continual-learning memory requirements growing with the number of tasks, including improper learners in their model. They also give a multi-pass construction with substantially different resource use. The hard-class and data-access assumptions matter; a repeated trivial task does not require linearly growing storage. [Primary text, Theorems 1.1–1.3](https://arxiv.org/html/2204.10830).

Brown, Bun and Smith give one-pass streaming lower bounds for specified natural learning families, including near-minimal-sample regimes where working storage is much larger than the final classifier description. This distinguishes training workspace from inference-time memory. Their results are not lower bounds for every learning problem or every number of passes. [Primary text](https://proceedings.mlr.press/v178/brown22a/brown22a.pdf).

Schmidhuber's Gödel machines make some self-rewrites conditional on a proof about the declared utility and formalized machine/environment assumptions. That is a positive conditional framework, not a guarantee that useful proofs are available or that the adopted model is true. [Primary text](https://arxiv.org/pdf/cs/0309048).

Demski and Garrabrant's Embedded Agency is a useful problem map for systems that are smaller than, and physically included in, their environment. It is an informal research survey, not an impossibility theorem that blocks implementation. [Primary text](https://arxiv.org/pdf/1902.09469).

## 8. A learning memory must preserve the validity of its evidence

Retaining a successful old verdict is not equivalent to retaining a valid argument for a new claim. A persistent record should bind the source bytes, task definition, observation model, updater version, evaluated candidate, test policy and time of observation. Recall must distinguish an archived report from current executed evidence.

For a finite exact task, an update can be committed only after checking the complete prospective comparison class. If a new observation introduces an unhandled task collision, refuse the update under that contract or explicitly enrich the retained view. Recompute on recall. Keep the earlier evidence; repair changes the current observation rather than deleting the old residual. The reference code demonstrates this gate on immutable finite archives; it is not currently connected to the repository's live provider composition.

For empirical improvement claims, selection and repeated testing enter the mathematics. Howard and colleagues develop time-uniform confidence sequences under stated process assumptions. Dwork and colleagues show how adaptive use of a holdout requires mechanisms that preserve statistical validity; a second program name does not create an independent sample. [Confidence sequences](https://arxiv.org/pdf/1810.08240), [adaptive holdout reuse](https://arxiv.org/pdf/1506.02629).

The September 2026 revision of Statistical Gödel Machines is directly relevant. Its trajectory-level false-commit result assumes conditionally valid confirmation tests and predictable, pathwise summable error allocation. The index includes opened failed confirmations, not just successful commits. A summable schedule such as delta/[k(k+1)] is valid; a bare infinite harmonic schedule is not. The bound concerns erroneous adoption under the defined null and objective. It is not a general action-safety theorem. [Primary text, v2, Theorem 1 and Section 4](https://arxiv.org/html/2510.10232v2).

The engineering extension is an append-only evidence ledger with exact task contracts and a separately justified sequential confirmation rule. Content integrity, semantic sufficiency and statistical validity are three checks. Passing any one does not imply the other two.

## 9. Contextuality belongs at its actual boundary

Abramsky and Brandenburger characterize contextuality using measurement covers and the nonexistence of appropriate global sections. This supports a precise obstruction for specified empirical models. It does not equate every incomplete observation with contextuality or show that reality lacks every observer-independent fact. [Primary text](https://arxiv.org/pdf/1102.0264).

Rovelli's relational quantum mechanics treats observers as physical systems and offers a relevant interpretive precedent. It does not prove the author's full working rule, and that rule need not wait for one preferred quantum interpretation. The operational research program above is already available classically. [Primary text](https://arxiv.org/pdf/quant-ph/9609002).

Our world-internal framing therefore does not depend on promoting Bell inequalities into a theorem about all truth. Contextual empirical statistics remain usable and learnable. Failure of one global classical representation specifies which representation to replace.

## 10. Corrections to carry into the existing monographs

The current paper-000 source, especially Section 8, needs these changes before its claims are extended:

| Current assertion or inference | Required replacement |
|:--|:--|
| Knowing has exactly the `authorized` reading | Separate factivity, record-relative determination, executable evidence and policy permission. |
| A finite token alphabet supplies a fixed report-carrier horizon | Bound the whole message/history length or actual memory states; arbitrary binary strings already defeat the inference. |
| Every finite report is lossy | State the task collision that witnesses loss; a finite sufficient statistic can be exact. |
| A diagonal obstruction prohibits iterated self-knowledge | State the adversarial coupling or formal truth/provability assumptions; preserve ordinary self-readout and qualified introspection. |
| Choosing one's evaluator makes its verdict have zero mutual information with improvement | Supply a probabilistic model and prove the independence; evaluator selection alone does not imply zero information. |
| Self-report is necessarily a destructive quantum pinching | Specify the physical measurement channel and state assumptions; ordinary classical logging is not that channel. |
| Bell/contextuality proves there is no fact from nowhere | Keep the world-internal rule as framing and state the exact local/noncontextual representation excluded. |
| Different verifier identifiers establish independent evidence | Separate declared roles from statistical and causal dependence. |

Paper 001 already separates permission, contextuality and several observation limits more carefully. Its introduction nevertheless describes a v1.4 companion whose recovery modules are absent from the currently checked-out paper 000. Reconcile that source lineage before claiming those proofs are in the current pair. Do not repair the mismatch by assigning historical proof counts to present files.

## 11. What is established now and what comes next

This dossier adds a constructive Lean core for semantic determination, exact decoder factorization, admissible future-memory preservation, the scoped Boolean obstruction, and maximal sound report-only acceptance. It also adds independent finite checking of fiber residuals, memory extension, future distinctions and optimal active query trees. These are neither a universal intelligence bound nor a proof that an arbitrary learned summarizer implements the model.

The most valuable next results are: finite deficiency LP certificates and bounded-loss transfer; action-indexed predictive memory with witness-guided refinement; controlled safe observation planning; and statistically valid evidence retention through repeated adaptive learning. Each pairs an exact obstruction with an explicit resource or interaction that can change it. The detailed integration sequence is in [extension_plan.md](extension_plan.md).
