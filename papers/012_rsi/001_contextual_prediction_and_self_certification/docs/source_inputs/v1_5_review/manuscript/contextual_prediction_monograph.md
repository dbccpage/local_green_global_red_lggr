<div align="center"># Contextual Prediction and Self-Certification</div>
<div align="center">Jeremy H. Carroll</div>
<div align="center">Conditional limits and their role in safe recursive self-modification</div>
<div align="center">2026-10-21</div>
<div align="center">Version 1.5.0</div>

## Abstract

A reasoner can represent contextual statistics without possessing a single joint distribution that reproduces them. It can check a ledger without establishing that no entries have been withheld. It can satisfy a provenance policy without establishing that a proposed action is safe. These are different limitations, with different hypotheses. This paper organizes them as a companion to *Projection Loss and Self-Maintaining Reasoning*, rather than treating them as one impossibility theorem for artificial superintelligence. We carry forward the finite support, observation-fiber, ledger, relabeling, and three-role results of the epistemic-contextuality precursor, with their executable checks. We add a Lean proof that preservation of observation fibers by every permitted update is equivalent to preservation under every finite update word. This supplies a precise sufficient condition for the precursor's unresolved temporal-privacy claim. We also exhibit why a pinned ledger tip needs an integrity assumption and why a passing provenance packet supplies no action-safety guarantee. The finite contextuality LP now has a Lean proof of primal and dual attainment, including the canonical maximum over deterministic columns and the joint-or-positive-defect alternative. A standalone exact-rational two-phase simplex solver returns independently replayed certificates. Five solver outputs are checked numerically inside Lean, and rational certificates are proved sound against all real probability vectors. This edition adds an executable Lean two-phase simplex with exact pivots, a shared finite pivot budget, and an independently checked return path. Its successful results are feasible and globally optimal; its recursion is total with budget exhaustion represented as a refusal. Conditional trajectory-error and correction-window results connect a declared residual enclosure to an observation uncertainty margin.

## 1. Two papers, two questions

The RSI companion asks what task information an observation retains, what memory must preserve through updates, how accurately missing information can be recovered, and when an enforced action gate preserves safety. Its version 1.3.0 includes analytic minimax, finite quantum recovery, and safe-delegation formalizations. This paper asks whether contextual tables admit a global joint representation, what internal checks establish about a ledger, and what follows from a specified authorization policy.

The distinction matters mathematically. A fiber collision concerns two states with the same observation and different task answers. A contextuality obstruction concerns the nonexistence of a probability distribution whose marginals equal several context-indexed distributions. Neither is the first cohomology of a cover alone. Likewise, a proof of recovery error does not issue a permission, and a permission does not supply a proof of safety.

This edition succeeds *Conditional Limits on Global Prediction, Self-Knowledge and Self-Certification for Physical Reasoners*, version 1.2.0, formerly filed under `001_finite_obstruction_calculus/002_asi_no_go_theorem_epistemic_contextuality`. The original package remains a historical source. Its monograph, README, mechanization map, and references are retained verbatim as archival documents under `docs/precursor_*`; they are not the current manuscript. The source inventory and the exact RSI companion release digest are in `docs/source_lineage.json`. The inherited Lean namespace is retained to make source comparison straightforward.

### 1.1 Status of the claims

**Formal** means a named declaration checked by the deposited Lean package. **Exact check** means a specified finite computation using integers or rational arithmetic. **Mathematical argument** means a proof in the text without a complete Lean formalization. **Imported** means a cited theorem not proved here. **Policy** means behavior follows from the adopted gate definition. **Open application** means the needed premise about a real system has not been established.

No result here bounds arbitrary intelligence, arbitrary computation, or the possibility of recursive improvement. No result turns an observation boundary into permanent privacy without a dynamics premise. No result derives the chosen authority policy from physical law.

## 2. Contextual prediction

Let $X$ be a finite set of measurements, each with a finite nonempty outcome set. A context is a jointly permitted subset of measurements. For each context $C$, an empirical model supplies a normalized nonnegative rational distribution $e_C$ on its outcome assignments. Assume compatible marginals on context overlaps. This assumption is often called no-signalling; it is a property of the supplied tables, not a consequence of finiteness.

Let $G$ be the finite nonempty set of global outcome assignments. A probability vector $p$ on $G$ induces all context marginals by a linear map $A$. A noncontextual representation is a probability vector satisfying

$$
Ap=e,\qquad p_g\geq 0,\qquad \sum_{g\in G}p_g=1.
$$

Here $e$ is the concatenation of the context tables. An assignment and a distribution over assignments are different objects: absence of a supported assignment implies absence of a representing probability distribution, but a supported assignment alone does not establish agreement with all probabilities.

### 2.1 The finite rational dichotomy

**Theorem 1 (formal over the reals, including rational data by scalar embedding).** Exactly one of the following holds: a representing joint probability vector exists, or the minimum mismatch is strictly positive:

$$
d(e)=\min_{p\in\Delta(G)}\lVert Ap-e\rVert_1>0.
$$

The deposited proof constructs both an attaining probability vector and an attaining dual pair. It does not assume a zero-gap certificate to establish existence. The probability simplex is nonempty and compact; its image under the marginal map is compact and convex. The proof first obtains a nearest point. If the empirical model belongs to that image, the zero functional supplies the dual optimum. Otherwise, geometric Hahn–Banach separation of the image from the open ball at the minimum distance yields a supporting functional. Its operator norm supplies the normalization. In the finite $\ell^1$ space, its values on coordinate basis vectors give the bounded dual coefficients.

The canonical dual certificate is

$$
\lVert y\rVert_\infty\leq 1,\qquad
\langle y,e\rangle-\max_{g\in G}\langle y,A\delta_g\rangle=d(e).
$$

The formal theorem `canonical_dual_attainment` exhibits a deterministic column attaining that finite maximum. The offset version returns a scalar satisfying

$$
\langle y,A\delta_g\rangle+z\leq0\quad(g\in G),\qquad
\langle y,e\rangle+z=d(e).
$$

Weak duality holds over any ordered field, including the rationals: a feasible dual value is no larger than the mismatch of any probability vector. Equality therefore proves optimality. `dual_solution_optimal` also proves that no feasible dual pair has a larger objective. `joint_or_positive_dual` and `positive_dual_excludes_joint` give the exhaustive and mutually exclusive contextuality alternative.

### 2.2 The exact-rational standard-form solver

The standalone solver uses variables for probability weights and positive and negative residuals:

$$
Ap-u+v=e,\qquad p,u,v\geq0,\qquad \sum_g p_g=1,
\qquad\min\sum_i(u_i+v_i).
$$

`slacks_l1_lower_bound` proves that every feasible residual split upper-bounds the $\ell^1$ cost. `exact_slacks_exist` constructs a split attaining that cost. Thus the standard-form problem implemented by the solver has exactly the same optimum, and `contextuality_standard_form_strong_duality` supplies attaining primal and dual solutions for that literal formulation.

The Python implementation adapts the repository's two-phase Bland simplex, using only integers and `Fraction`. Phase one introduces artificial variables and detects infeasibility; phase two optimizes the original objective. One declared pivot budget covers both phases and removal of artificial basic variables. The contextuality reduction is always feasible and bounded for nonempty finite columns; general standard-form inputs can also receive infeasible or unbounded refusals. Exhaustion of a resource budget is a refusal, never a contextuality verdict. No floating approximation or rational reconstruction is used.

A separate checker rebuilds the standard-form constraints and checks primal nonnegativity, every equality, every dual inequality, equality of objectives, the residual vector, the witness norm, the offset, and their binding to the displayed result. The pivot count is diagnostic and is not a premise of the mathematical certificate. Input validation checks normalization and overlap marginals before the contextuality LP; enumeration and dense-matrix caps are checked before allocation.

Rational zero-gap certificates are proved sound over the rationals and, by scalar embedding, against all real probability vectors. Five concrete solver outputs are translated into `RationalCertificates.lean`; Lean checks all their numerical constraints and the claimed defects, then applies that general result. These are the classical mixture (0), PR box (2), near-Tsirelson table (4/5), an odd-parity triangle (2), and a Bell table just above the classical boundary (1/25000000). `docs/lp_certificates.json` contains the exact data, with source bindings; its generator has a refusing check mode.

### 2.2.1 Executable simplex correctness and finite-budget termination

`Simplex.lean` implements the two phases, negative-right-hand-side normalization, artificial-variable initialization, least-index entering selection, ratio selection with least-basic-index tie breaking, exact row elimination, artificial-basis cleanup, removal of redundant active rows, phase-two objective reconstruction, primal and dual extraction, and independent final replay. `SimplexDriver.lean` runs this program on exact JSON inputs. Table rows are materialized as finite vectors after each pivot, avoiding exponential reevaluation of earlier functional updates.

**Theorem 1a (formal, successful-return correctness).** For every finite rational standard-form problem and every natural pivot budget, a successful Lean `solve` return satisfies primal nonnegativity, every equality, dual feasibility, and equality of both objectives to the returned value. Every feasible rational competitor has objective at least this value. `valid_is_real_optimal` also proves that a rational certificate lower-bounds every feasible real competitor for the same rational data. The final checker is part of the algorithm; the proof does not assume that the unverified extracted tableau is correct.

The pivot development separately proves normalization of the entering column, equivalence of the represented linear equations before and after a nonzero pivot, preservation of the objective on those equations, and nonnegative right-hand sides under the ratio-test hypotheses. Initialization gives nonnegative right-hand sides. These are algebraic invariants for the actual pivot definition, including degenerate zero right-hand sides.

**Theorem 1b (formal, shared-budget accounting).** Both simplex recursions are structural on the remaining pivot budget; cleanup is structural on the finite original row list. Every pivot consumes exactly one unit. `simplex_budget_exact`, `cleanup_budget_exact`, and `execute_budget_exact` prove that the successful execution trace length plus the remaining budget equals the original budget. `accepted_pivots_match_trace` identifies the displayed count with the actual trace; `solve_pivot_bound` bounds it by the supplied budget. Thus the deposited Lean program terminates with an accepted optimum or a refusal for every finite typed input and budget. This is a finite-pivot termination guarantee, not a wall-clock bound on rational bit complexity or operating-system resources.

The Python algorithm and the executable Lean algorithm are compared on complete outputs: every primal coordinate, every dual coordinate, exact value, pivot count, and refusal kind. Cases include all five contextuality fixtures at budgets just below and at completion, redundant rows, negative right-hand sides, empty problems, degeneracy, and the classical cycling example under Bland selection. These finite comparisons do not prove universal Python-to-Lean refinement. Neither budget exhaustion nor the other refusal labels is a checked mathematical certificate of infeasibility or unboundedness. A proof that unbudgeted Bland execution always finds an optimum, a complete phase-invariant proof removing the final checker, and universal cross-language refinement remain outside this edition.

The supplied review's input-boundary repair is implemented: ordinary list/tuple containers and integer context indices are checked before sorting or hashing. The inherited `is_distribution` and `marginalises` helpers are partial checks of supplied rows and marginal equalities respectively; they are not complete probability-model validators. Current public contextuality evaluation checks positivity, normalization, coverage and overlap compatibility.

### 2.3 The PR support obstruction

For binary settings and outcomes, the PR support requires

$$
a_x\mathbin{\mathrm{xor}} b_y=x\mathbin{\mathrm{and}} y.
$$

The three contexts other than the final one require equal outcomes. Together they imply equality in the final context, whose rule instead requires unequal outcomes. Thus no global assignment satisfies every context. Any positive-weight entry of a nonnegative joint representing the PR tables would have to satisfy every support constraint: otherwise it would contribute positive mass to a zero-probability outcome. This is impossible.

`ResultI` proves the support contradiction and its consequence for finitely supported natural-weight measures. Its natural weights are a support model, not a Lean construction of arbitrary real probability measures. The positive-weight argument above extends to finite probability vectors in prose. The same module verifies exact marginal weights for the equal mixture of the all-zero and all-one assignments, supplying a classical global section.

The Python checks use `Fraction` to verify the PR table, the classical mixture, and a full-support table with weights 17/40 and 3/40, exchanged in the final context. They enumerate all sixteen deterministic assignments and obtain the classical CHSH upper bound 2. The full-support table has CHSH value 14/5, so it cannot be a convex combination of those deterministic assignments. It nevertheless has supported global assignments. This separates probability incompatibility from absence of global support. A further rational probe lies just above the classical boundary; no floating tolerance is used.

A context-aware predictor may store the whole empirical model and answer from the selected context. Theorem 1 excludes a particular joint representation. It does not exclude storage of contextual statistics or a world-model containing them. The first cohomology of the context-cover nerve is a property of the cover; it cannot distinguish two empirical models on the same cover. A support-presheaf obstruction is a different construction and is not implemented here.

## 3. Observation fibers and future privacy

Let $\pi:S\to B$ be the information supplied to a predictor and let $q:S\to Q$ be its task. If two states have the same report and different task answers, no report-reading function recovers the task on both states:

$$
\pi(s)=\pi(t),\quad q(s)\ne q(t)
\quad\Longrightarrow\quad
\neg\exists f\;\forall z,\ f(\pi(z))=q(z).
$$

`ResultII.fiber_lemma` proves this for arbitrary types. Its finite witness observes the first coordinate of a pair of bits. Full-state prediction fails because the hidden coordinate can vary. With swap dynamics, however, the hidden coordinate becomes the next report. The source's inference from instantaneous information loss to indefinite privacy is therefore false. The witness is preserved in both Lean and Python.

### 3.1 The missing dynamics premise

Let $U$ be a type of permitted updates and let $F_u:S\to S$ be the update indexed by $u$. Apply a word from left to right, with the empty word acting as identity. Define fiber preservation by

$$
\forall u,s,t,\quad \pi(s)=\pi(t)\Longrightarrow
\pi(F_u(s))=\pi(F_u(t)).
$$

**Theorem 2 (formal).** Every permitted update preserves observation fibers if and only if, for every pair in the same initial fiber and every finite update word, the final reports agree.

*Proof.* For the forward direction, induct on the word. The empty case is the initial equality. For a nonempty word, the first update preserves equality, and the induction hypothesis applies to the remaining word. For the reverse direction use a word of length one. `Bridge.fibers_preserved_iff_all_words` checks both directions in Lean without Mathlib.

An intertwining family supplies this premise:

$$
\pi\circ F_u=\overline F_u\circ\pi.
$$

Theorem 2 therefore gives a precise sufficient condition for privacy of distinctions within a report fiber under the declared updates. It also covers adaptive selection of updates by a deterministic policy reading only the common transcript: equal transcripts select the same next update, preserving the induction. The adaptive extension is a prose argument, not a separate Lean theorem. Controllers with additional private observations, unmodeled interventions, or changed report maps need additional premises.

The RSI companion treats the more general task of preserving every future task readout, defines its greatest update-stable observational equivalence, and studies finite memory refinements and recovery. The theorem here is the report-fiber specialization that connects the precursor's counterexample to that construction. It does not import the companion's 161 declarations into this package, and the two packages build independently.

### 3.2 Projection Obstruction: error propagation and correction windows

The supplied review and a fresh reading of Projection Obstruction supply useful conditional boundaries. They do not identify contextuality defect with a quantum product-retraction residual. The former is distance to a convex probability polytope; the latter is the residual of a specified nonlinear marginal-product retraction. PO-034 section 4.1 shows explicitly that this retraction need not be a nearest-product projection. PO-000 also exhibits vanishing pairwise defects with a positive global obstruction, so a locally zero diagnostic is not a global error certificate.

For an actual exact update and an implemented trajectory, suppose the update is Lipschitz with factor L, the initial error is bounded by E0, and every actual one-step implementation defect is bounded by r_k. Then:

$$
E_{k+1}\le L E_k+r_k,
\qquad
E_n\le L^n E_0+\sum_{k=0}^{n-1}L^{n-1-k}r_k.
$$

`ErrorBudget.trajectory_error_bound` proves the recursive enclosure for arbitrary normed additive groups. `constant_residual_envelope` proves its geometric finite-sum form for a constant defect cap. With nonexpansive propagation and a positive constant cap, a sufficient waiting window is:

$$
E_n\le E_0+n\eta,\qquad
n\le\frac{\varepsilon-E_0}{\eta}\Longrightarrow E_n\le\varepsilon.
$$

`nonexpansive_envelope` and `correction_window` establish the displayed arithmetic. Apply the trajectory theorem to a constant cap that bounds every actual defect before using this window. A correction resets E0 only if its post-correction error is independently bounded. A finite pivot budget says nothing about whether computation finishes inside this physical window.

PO-033 section 3.1 and PO-034 section 4.2 give the conditional continuous-time Duhamel estimate, including initial mismatch in PO-033:

$$
|\Delta O(t)|\le\lVert O\rVert_\infty
\left(E_0+\int_0^t\lVert\mathcal R(s)\rVert_1\,ds\right).
$$

The residual here is the actual dynamical defect of the implemented interpolated trajectory. With a proved uniform residual cap r and positive observable norm, a sufficient waiting window is:

$$
t\le\frac{\varepsilon/\lVert O\rVert_\infty-E_0}{r}.
$$

`duhamel_waiting_window` formalizes the scalar implication from a supplied enclosure and cap. The CPTP/unitary propagator theorem, continuous integral enclosure, and validated numerical quadrature are not newly mechanized here. PO-033's sampled trapezoidal estimates explicitly remain uncertified; initial normal velocity alone cannot replace a uniform cap. PO-000 Theorem 5.10.A can sharpen observable bounds through certified edge residuals and Lieb--Robinson weights, provided its locality and trajectory hypotheses hold. Those spatial weights do not automatically apply to a reasoning state or arbitrary self-modification.

To connect a state enclosure to contextual data, declare the observation maps. `observation_radius` proves:

$$
\sum_i|O_i(x)-O_i(y)|\le
\left(\sum_i\lVert O_i\rVert\right)\lVert x-y\rVert.
$$

`nearest_distance_lipschitz` proves the 1-Lipschitz comparison for attained distances. `uncertainty_adjusted_witness` then proves, for every feasible probability vector p and any feasible bounded witness:

$$
\sum_i|e_i-\widehat e_i|\le\rho
\Longrightarrow
\lVert Ap-e\rVert_1\ge
\max\{0,\langle y,\widehat e\rangle+z-\rho\}.
$$

The radius needs a justified observation/error or statistical coverage argument. The exact near-boundary fixture has margin 1/25000000; a radius at least that large erases this guaranteed positive margin. Exact arithmetic alone supplies no empirical confidence region. The review's sharper witness-norm factor, exact ball erosion, two-polytope certificates, and stochastic adaptive-transcript extensions remain separate prose/reference-code results in the supplied review, not newly claimed formal theorems in this edition.

Finally, a short-time leakage lower bound becomes a correction-capacity obstruction only after bounding what correction can remove in the same metric:

$$
D(t)\ge\nu t-Kt^2,\quad
C(t)\le ct,\quad R(t)\ge D(t)-C(t)
\Longrightarrow R(t)\ge(\nu-c)t-Kt^2.
$$

`correction_capacity_lower_bound` and `threshold_missed` prove this implication and its strict-threshold consequence. PO-000 supplies a local correlation lower bound with K equal to 24 times the squared full incident interaction norm; PO-034 supplies different finite-carrier coefficients under its own Hamiltonian, jump, and dilation hypotheses. These quantities and domains must not be interchanged. A lower bound gives a forbidden window when it exceeds tolerance; it does not certify safety at other times, monotonic error growth, or a universal deadline for correcting reasoning.

## 4. Internal checks and self-certification

### 4.1 Ledger validity and completeness

A linked ledger contains payloads and stored digests. A verifier checks that every digest agrees with the previous digest and the payload. Every prefix of a verified ledger still verifies. `ResultIII.prefix_verifies` proves this for an arbitrary digest function. Consequently an internal validity check alone cannot distinguish the whole ledger from a withheld suffix.

An externally expected length and tip can distinguish a particular full ledger from its proper prefixes when the data and integrity assumptions support that comparison. In the finite source example the full two-entry ledger passes against its expected tip and its one-entry prefix fails. This is a formal example, not a proof that any hash tip uniquely identifies any history.

**Proposition 3 (formal counterexample).** For a constant digest function, both the empty ledger and a nonempty valid ledger have the same tip and pass the same tip check. `Bridge.pinned_tip_can_collide` exhibits them. An external pin is useful evidence relative to a trusted commitment, expected extent, and suitable integrity assumptions. It is not an unconditional uniqueness theorem about arbitrary digest functions or a way to know whether the external source withheld records. Python uses SHA-256; Lean's illustrative digest is arithmetic. Neither implementation proves cryptographic collision resistance.

### 4.2 Relabeling

If an export is invariant under a relabeling, every verdict computed solely from that export is also invariant. `ResultIII.invariant_export_blind` proves the factorization statement. A verdict sensitive to the first token separates a concrete list from its relabeling, so dropping invariance makes the assertion false.

An internally detectable invariant defect remains detectable. Relabeling invariance does not imply that token computation cannot detect any quotient defect. Questions about what a token denotes require a supplied grounding map. This is another observation-fiber issue, with the missing information named rather than inferred from a general claim about semantics.

### 4.3 Logical self-reference

Tarski's undefinability and Löb's theorem concern specified formal languages and provability predicates. Their application to an agent requires hypotheses about its effective theory, arithmetic, coding, and derivability conditions. They are imported background, not Lean results in this package. A token stream, self-report, or level counter does not establish those hypotheses. The present finite examples do not prove a general incompleteness theorem for physical cognition, awareness, or arbitrary self-modification.

## 5. Provenance, permission, and safe delegation

The adopted strict policy uses proposer, evaluator, and authorizer identifiers. It requires distinct role identifiers, certificate rather than prose standing, and an admitted root distinct from proposer and evaluator. It refuses malformed identifiers and unadmitted roots. `ResultIV.pass_implies_policy` proves the corresponding conditions from a successful Lean-model evaluation; `delegated_standing_admitted` proves the converse existence of a receipt under its stated premises.

This is a policy theorem. The receipt's effect type contains only `none`; saying that it carries no authority is a fact about this type. Delegated standing is an input supplied under a regime, not a consequence of predictive competence. Distinct strings can name one controller; the deposited alias witness passes. The model does not authenticate identities, verify a cryptographic delegation chain, or establish institutional independence.

### 5.1 A gate can pass an unsafe action

The three-role function has no action-safety predicate. Attach the action 1 to a valid packet in a system where only action 0 is safe. The packet still passes. `Bridge.provenance_pass_can_be_unsafe` proves this concrete counterexample; the Python suite checks the same separation. No contradiction arises, because provenance and safety answer different questions.

The safe-delegation results in the RSI companion instead require a sound model of possible states, an enforced gate admitting only actions safe in every compatible state, and an invariant preserved by admitted actions. Their induction can cover recursively changing proposers while those premises remain fixed. A provenance certificate may be one input to that engineering contract. It cannot replace its semantic safety premise.

Conversely, contextuality alone is not an action veto. To obtain a decision impossibility one must specify the action set, the loss or safety relation, and which states remain compatible with the available report. If every compatible state has a common safe action, refusal is not forced by an inability to reconstruct the whole state. The common-action criterion and conflict witnesses belong to the RSI companion.

## 6. Executable scope and reproduction

The standalone Python modules use the standard library and exact fractions. The inherited and bridge tests cover contextual supports, marginals, CHSH, observation maps and words, ledgers, relabeling, and the three-role policy. The LP tests check exact objectives, randomized one-dimensional hulls against their closed form, certificate component mutations, degenerate constraints, negative right-hand sides, signalling input, malformed data, and resource refusals. The Lean generator independently checks five exact solver outputs; finite fixture checks supplement the general duality proof.

The Lean package pins Lean 4.33.1 and a source-pinned offline Mathlib bundle. The four original result modules remain byte-for-byte identical to the precursor. `Bridge` supplies the RSI connections, `ContextualDuality` proves the general LP results, and `RationalCertificates` checks the generated rational data. `Simplex` implements the total budgeted solver and proves its pivot, return and accounting results; `SimplexDriver` exposes exact execution. `ErrorBudget` proves the conditional propagation, observation and correction-window statements. Each package-local theorem enters the named census; the full environment census additionally checks generated and private package declarations. Only `propext`, `Quot.sound`, and `Classical.choice` are admitted. Source hashes bind the audited modules and build configuration; changes after audit are refused. Vendored dependencies have their own source, license, module and artifact inventory.

The Lean, Python, and external Rust gate implementations remain separate models. No compiler or refinement proof ties their semantics together. The new Python boundary check refuses unknown basis strings; Lean's basis type already admits only its two constructors. Tests bind that documented boundary behavior, without claiming general cross-language equivalence.

Reproduction commands, from this package root, are:

```text
python -m pytest code/tests -q
python tools/generate_lp_certificates.py --check
python tools/replay_simplex_implementation.py --replay
python verify_deposit.py --lean
python tools/replay_lean_axiom_census.py --replay
python tools/replay_full_axiom_census.py --check
python scripts/paper_spine.py verify
python tools/rebuild_release.py --check
```

The mathematical text, generated TeX, and UTF-8 text share an explicit equation registry. The PDF is freshly compiled from that source; byte bindings and rendering checks are conversion checks, not proofs of mathematical truth. The release ZIP and both manifests are checked against the package tree. No source from the sibling paper is needed to run this package.

## 7. Limits and research directions

General finite contextuality LP duality and an exact solver are now included. The source's additional support classifications and nerve computations remain historical external results unless independently represented in the deposited checks. The budgeted Lean simplex is total and success-sound; unbudgeted Bland completeness and universal Python refinement remain unformalized. General probabilistic privacy, stochastic interventions, real-system identity binding, cryptographic commitments, and verification of a self-modifying model remain application obligations. The Tarski and Löb results remain imported.

The constructive target is safe delegation under declared observations and updates. A useful next result would connect an implemented memory transformation and an authenticated action gate to the companion's invariant-preservation hypotheses. Such a refinement must show preservation of the relevant future tasks and the action-safety relation. Descriptive self-reports and successful provenance checks alone supply neither proof.

## References

The precursor's full bibliography and verification markers are preserved in `docs/precursor_references.md`. Bibliographic identifiers below are carried from that supplied source; publisher records were not re-audited for this reorganization.

1. Carroll, J. H. (2026). *Projection Loss and Self-Maintaining Reasoning*. Version 1.3.0. RSI paper 000; exact release identity in `docs/source_lineage.json`.
2. Carroll, J. H. (2026). *Conditional Limits on Global Prediction, Self-Knowledge and Self-Certification for Physical Reasoners*. Version 1.2.0. Precursor manuscript retained as `docs/precursor_monograph.md`.
3. Abramsky, S. and Brandenburger, A. (2011). *The sheaf-theoretic structure of non-locality and contextuality*. New Journal of Physics 13, 113036. doi:10.1088/1367-2630/13/11/113036.
4. Popescu, S. and Rohrlich, D. (1994). *Quantum nonlocality as an axiom*. Foundations of Physics 24, 379–385. doi:10.1007/BF02058098.
5. Tarski, A. (1936). *Der Wahrheitsbegriff in den formalisierten Sprachen*. Imported background at the scope stated in section 4.3.
6. Löb, M. H. (1955). *Solution of a problem of Leon Henkin*. Journal of Symbolic Logic 20, 115–118. Imported background at the scope stated in section 4.3.
