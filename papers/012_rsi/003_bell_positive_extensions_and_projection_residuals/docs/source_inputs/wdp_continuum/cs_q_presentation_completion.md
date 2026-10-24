# Presentation closure from CODA-CS to CODA-Q and the circle dual

AuthorityEffect: None. The metric presentation criterion and commuting
completion routes are now mechanized in Lean. The character and Haar
arguments remain written conditional proofs with exact finite examples.
A general physical field theory and GEN-WDP-O01–O05 remain open.

A selected continuum is possible here. The useful bridge combines the
image-factor theorem of [CODA-CS/Q](source_archive/coda_component_packages/cs_q/coda_cs_q_bridge.md)
with the uniform-extension theorem of [CODA-Q](source_archive/coda_component_packages/q/coda_q.md).
The missing condition is stability **in the presentation metric**. Equality
of presentation values controls exact descent; closeness of presentation
values must additionally control closeness of the protected answers.

## 1. The presentation-completion criterion

Let X be a set, P a metric space, p:X→P a presentation, and Y a complete
metric space. Put S=p(X), with its inherited metric, and let q:X→Y be the
protected query. The following condition is relative to p:

$$
\forall\varepsilon>0\ \exists\delta>0\ \forall x,x'\in X:
\quad d_P(p(x),p(x'))<\delta
\ \Longrightarrow\ d_Y(q(x),q(x'))<\varepsilon.\tag{PC}
$$

**Proposition PC-1.** Condition PC is equivalent to the existence of a
uniformly continuous g:S→Y with q=g∘p. Under PC there is a unique uniformly
continuous extension ĝ:Ŝ→Y, where Ŝ is the metric completion of the actual
image. Conversely any such extension recovering q implies PC.

**Proof.** If p(x)=p(x'), their presentation distance is zero. PC bounds
their answer distance by every positive ε, so it is zero; metric separation
gives q(x)=q(x'). The image-factor theorem CSQ-T1 therefore defines
g(p(x))=q(x), independently of the witness. Applying PC to witnesses for any
two points of S proves uniform continuity of g. Q-T3 gives the unique
uniformly continuous extension into complete Y. In the reverse direction,
restrict the modulus of ĝ to S and compose with p. This is exactly PC. □

This theorem is on Ŝ, **not on all of P or its completion**. Unused labels
are still outside the factor's source. No surjectivity, chosen section, or
default value is silently supplied. For a pseudometric answer space, the
same proof yields a factor only into its separated quotient; literal answer
equality requires separation. A constructive evaluator additionally needs an
effective modulus and effective names for the chosen inputs and outputs.

The quantitative specialization

$$
d_Y(q(x),q(x'))\le K\,d_P(p(x),p(x')),\qquad K\ge0,
$$

gives a K-Lipschitz image factor and a K-Lipschitz completion extension.
This follows first on S; approximating two completed points by points of S
and taking limits preserves the displayed inequality.

If X is also metric and p:X→S is uniformly continuous, extend p to
p̂:X̂→Ŝ. The composite ĝ∘p̂ agrees with q on X. Uniform continuity and
uniqueness give q̂=ĝ∘p̂. Thus the presentation route and the query route
commute at the completion. Without this extra hypothesis on p, PC-1 still
closes the image-query route but supplies no completed source transport.

### Mechanized metric scope

[PresentationCompletion.lean](../lean4/WitnessedDifference/PresentationCompletion.lean)
proves PC-1 for arbitrary source types and actual metric spaces. In particular,
`relativeControl_iff_unique_completion` gives the equivalence with the unique
uniformly continuous recovery map on Mathlib's metric completion of `Set.range p`.
`completion_routes_commute` proves the stated equality of completed routes when
the source is metric and p is uniformly continuous. Completeness of Y is an
explicit typeclass hypothesis for the recovery and uniqueness results.

The [separate axiom report](../lean4/WitnessedDifference/PresentationCompletionAxiomReport.lean)
selects fifteen metric declarations, including fibre constancy, image agreement,
uniform continuity, extension recovery and uniqueness, and the commuting square.
The [dated 2026-10-08 verification record](lane_e_character_duality_completion.md#8-local-verification-record)
reports a scoped Lake build and census on Lean 4.33.1 with Mathlib pin
`0df444a360eaa60ab8c11dca51a86af692955474`. A separate 2026-10-13 compatibility
replay compiled the unchanged `PresentationCompletion.lean` and its report
using Lean 4.34.0 and Mathlib `5ed2965256430c3649e86755f9576b54eca72435`.
The fifteen selected declarations reported the axiom union `propext`,
`Quot.sound` and `Classical.choice`, with no `sorryAx` or custom axiom.
This was not a fresh full-package build at the pinned versions: the available
4.33.1 cache had no compiled Mathlib completion module. The mathematical
result is a classical existence proof, not an effective decoder.
It is separate from the historical 202-theorem report and the 29-module,
408-declaration core-only finite spine. Neither historical census is rewritten.

Mathlib's `Completion.extension` is a total construction. Its uniform-continuity
theorem alone supplies no recovery certificate: agreement with q in this module
requires `RelativeControl`. The mechanized scope does not include the Lipschitz
specialization, circle/torus character classification, Haar integration, scalar
field operations, Meron ensembles or an authorization rule. Those statements
retain their separately stated assumptions and evidence.

Replay these two targets from the package at a short path, using local vendors
and cached dependencies at its exact manifest revisions:

```text
lake build +WitnessedDifference.PresentationCompletion +WitnessedDifference.PresentationCompletionAxiomReport
lake env lean WitnessedDifference/PresentationCompletionAxiomReport.lean
```

## 2. Exact descent alone does not give PC

Give X={0,1,2,…} the discrete metric. Define p(0)=0, p(n)=1/n for n>0;
define q(0)=0, q(n)=1 for n>0. The map p is injective, so q is exactly
fibre-constant. The query is 1-Lipschitz on X. Yet p(n)→p(0) while
|q(n)−q(0)|=1. Taking ε=1/2 disproves PC for every δ>0.

Every finite restriction has an image factor; none proves the missing
all-level modulus. This is the distinction between a native finite
factorization replay and an analytic completion theorem. It also explains
why CSQ-T3's Lipschitz control on source states is insufficient after a
presentation compresses their distances.

An approximate finite decoder only bounds each same-profile collision by
2ε, as in CSQ-T2. To obtain a completed query from improving decoders, one
must additionally bind them to one target query and prove a vanishing error
law and the needed compatibility or Cauchy control. Unrelated values inside
shrinking intervals do not meet that condition.

## 3. The dyadic presentation closes to the circle under its circle topology

The [dyadic supplement](dyadic_refinement_and_duality.md) already proves
that C_n=Z/(2^n), with inclusions k↦2k, has algebraic direct limit
D=Z[1/2]/Z. It distinguishes D with the discrete topology from D embedded
densely in T=R/Z with the circle metric. The latter completion is T.

**Proposition PC-2.** Give D the circle-subspace topology. Its continuous
character group, with the compact-open topology, is Z with the discrete
topology. Its character bidual is T, and the evaluation map D→T is its
usual dense circle embedding.

**Proof.** A continuous homomorphism D→T is uniformly continuous:
continuity at zero controls every difference because the metrics are
translation invariant. PC-1/Q-T3 extends it uniquely to T. Taking limits
in the homomorphism identity proves that the extension is a homomorphism.
The circle characters are χ_j(x)=exp(2πijx), j∈Z, as proved in the dyadic
supplement. Restriction and extension therefore identify the character
groups algebraically.

To check the dual topology, consider the compact subset
K={0}∪{1/2^n:n≥1} of D. It is a convergent sequence together with its limit.
For each nonzero j, write j=2^v u with u odd. At the point 1/2^(v+1)∈K,
χ_j has value −1. Hence the compact-open neighborhood consisting of
characters sending K into the open circle arc of radius 1/4 about 1
contains only χ_0. Translations give a discrete character group.
The conventional dual of discrete Z is T: a character is fixed by its
arbitrary value at 1. The compact-open topology is the circle topology
because compact sets in Z are finite and evaluation at 1 determines all
other evaluations. Evaluation of d∈D sends j to exp(2πijd), giving precisely
the displayed dense embedding. □

D with this subspace topology is not locally compact. If it had a compact
neighborhood K of zero, an ambient open arc U would have U∩D⊂K. The image
of K in the Hausdorff circle is closed; density then forces U⊂K⊂D, which
is impossible for this countable subgroup. Thus PC-2 uses the direct
extension and topology proofs above; it does **not** invoke general
locally compact Pontryagin reflexivity on D itself.

With the **discrete** topology on D, every character is continuous and its
dual is Z_2. General locally compact duality applies to that discrete group
and returns D as its bidual. The same algebraic tower consequently has
different character/completion outcomes under different topologies.

| Declared topology on D | Continuous character group | Character bidual | Circle route |
| --- | --- | --- | --- |
| Discrete | Z_2, compact | Discrete D | Additional topology is required. |
| Circle subspace | Z, discrete | T | Evaluation is the dense completion embedding. |

This closes a specific presentation/character route. It does not select the
topology from the initial mark or recover arbitrary functions and dynamics.
The standard locally compact theorem and T/Z examples are background in
[Elkies's notes](https://abel.math.harvard.edu/~elkies/M55b.02/pontrjagin.html);
finite-character background is in
[Conrad's notes](https://kconrad.math.uconn.edu/blurbs/grouptheory/charthy.pdf).

## 4. Continuity selects which coherent finite characters survive

All coherent finite indices a_n mod 2^n give a character of discrete D.
The circle-continuous ones are exactly a_n=j mod 2^n for a single integer j.
No finite prefix distinguishes an integer extension from all other 2-adic
extensions.

For a concrete excluded family, take a_n=Σ_(2r<n)2^(2r) modulo 2^n.
Restriction commutes at every level. At n=2m,

$$
\frac{a_{2m}}{2^{2m}}=\frac13-\frac{1}{3\,4^m}.
$$

The inputs 1/4^m tend to zero in D, but their character turns tend to 1/3,
not zero modulo one. Thus this coherent 2-adic character, representing
−1/3∈Z_2, is discontinuous for the circle topology. The geometric-series
identity proves this at all m; the companion checks five exact prefixes.
This is a useful positive obstruction: reject a tower character that has no
required continuity rather than calling every compatible family a circle
mode.

### Fixed finite products reach the torus branch

For any supplied finite positive dimension d, D^d is dense in T^d under the
product circle metric. A character of D^d splits into the sum of its d
coordinate characters. Each extends to T, so the continuous characters are
indexed by Z^d. The finite union of the coordinate copies of K from PC-2 is
compact and detects every nonzero integer tuple; the compact-open character
topology is discrete. Its character bidual is T^d, and evaluation is the
dense coordinatewise completion embedding. This proves the same selected
presentation closure for the 2-, 3- and 4-torus.

With normalized product length measure and coordinatewise Lipschitz
constants L_i, a product-grid average has error at most
Σ_i L_i/(2N_i). Within each cell, telescope the coordinate differences and
integrate L_i times its coordinate displacement; sum the cells. The
companion samples an actual four-coordinate piecewise-linear function on
16 nodes. This extends the geometric/observable profile, not a dynamical
field theory or an infinite-dimensional operator limit.

## 5. Haar observables give exact and approximate query closures

Supply the circle, normalized length measure and circle characters. For a
trigonometric polynomial F(x)=Σ c_j exp(2πijx), the N-point average is
Σ_(N divides j)c_j. The finite geometric-series proof is in the dyadic
supplement. If N exceeds every absolute nonzero frequency, the average is
exactly c_0=∫F. This is an exact finite query factor on the declared
band-limited function class. The samples need not reconstruct F itself.

For all L-Lipschitz real functions the integral does not factor exactly
through one finite grid. Both F=0 and
H_N(x)=L·dist(x,(1/N)Z), periodically continued, vanish at every grid node.
The second is L-Lipschitz. Each cell is a triangle of base 1/N and height
L/(2N), so its total integral is L/(4N)>0. The identical profiles have
different protected answers. The companion calls the actual CS-Q solver
on the N=4 collision, with answers 0 and 1/16 for L=1.

Nevertheless, the cellwise sampling estimate gives

$$
\left|\frac1N\sum_{k=0}^{N-1}F(k/N)-\int_0^1F(x)\,dx\right|
\le\frac{L}{2N}.
$$

Therefore the averages of this single observable recover its integral,
with an effective error modulus if L is supplied effectively. On C(T) with
the sup metric, the integral query is 1-Lipschitz. A dyadic restriction
p:F↦F|_D, whose image has the sup metric over D, is an isometry: density
and continuity give sup_D|F−G|=sup_T|F−G|. The integral thus satisfies PC-1
on the actual restriction image. That image is already complete because
C(T) is complete; this closes its query transport rather than constructing
C(T) from a finite list. A finite list of samples alone is a different
presentation.

Continuity matters. Zero and the indicator of irrational circle coordinates
agree at all dyadic nodes but have Haar integrals 0 and 1. Arbitrary
measurable functions are not recovered by this sampling argument; point
evaluation is also not a well-defined map on L^1 equivalence classes.

The finite uniform measures are not pushforward-compatible along doubling
inclusions: the pushed lower measure occupies only the even-index points
of the higher group. The circle integral is their weak sampling limit after
the circle embedding, not an algebraic direct-limit invariant probability.
Reduction maps in the inverse system instead support the compact Z_2 Haar
construction. Those two measure constructions must stay distinct.

## 6. What the incoming Haar implementation actually checks

This section binds the original functions at the source checkpoint
[`ee274924111e1cbb4c4c7601cebeee05e569ecbb`](https://github.com/dbccpage/the_symbol_game/tree/ee274924111e1cbb4c4c7601cebeee05e569ecbb/omega_engine_projects/finite_to_continuum).
They are called unchanged by the companion.

- `HaarLimitCharacterPair.discrete_sum_at_level` returns the divisibility
  formula. The companion independently sums all powers in
  Q[z]/Φ_N(z), using exact SymPy polynomial arithmetic, and compares 78
  character averages across levels 0–5. This is finite replay, separate from
  the all-N geometric-series proof.
- `TrigPolynomial({4:1}).verify_haar_recovery(max_level=0)` reports recovery
  true although its sole observed average is 1 and its declared integral is
  0. Its claimed stabilization level is 3; the post-threshold check range is
  empty. The flag therefore does not establish *observed* recovery on this
  prefix. The written theorem still proves recovery at all later levels.
- Direct `ContinuumEnclosure` accepts [-1,1], [1/2,3/2], [5/4,7/4] as
  contractive. Their widths halve and neighbors overlap, but the total
  intersection is empty. The separate `constructive_cauchy_completion`
  wrapper accumulates intersections and returns a false contraction flag
  for the corresponding supplied sums. The wrapper catches this example;
  the direct flag does not.
- `LipschitzContinuumEnclosure` accepts supplied L and average values. It
  does not prove that they came from one observable with that Lipschitz
  constant or that its intervals contain one particular integral. A
  positive example here computes the actual dyadic samples of
  F(x)=dist(x,Z), with integral 1/4 proved by its triangular areas.

No source flag supplies PC, a common physical target, or an infinite law.
A finite nested prefix also needs its generator's global containment and
shrinking-width proof before it names or bounds a continuum observable.

## 7. Completing scalars and operators is an additional, explicit profile

The existing Gaussian-rational instruments provide another practical
starting point: give Q(i) the metric |Δa|+|Δb| on its rational coordinates.
Its completion is R² by coordinatewise rational completion, conventionally
identified with C. Addition extends uniformly. Multiplication is uniformly
continuous on bounded sets, and every Cauchy sequence is bounded, so its
product passes to Cauchy equivalence classes. Reciprocal requires a nonzero
bound and extends on regions bounded away from zero. These arguments construct the selected
field operations; a name for a metric completion alone does not do so.

At a **fixed finite matrix dimension**, entrywise completion and finite sums
and products consequently preserve matrix algebra and trace pairing. This
does not handle growing Hilbert dimensions, unbounded operators, spectral
limits, quantum state selection or a physical continuum by itself. Those
require their own topology, domains and bounds. The Archimedean metric is an
admission; the primitive mark does not select it over other completions.

## 8. Numeric closure preserves no automatic authority decision

The sequence φ_n=2^-n is strictly positive and tends to zero. The Boolean
query φ↦[φ>0] therefore changes at the limit and is not continuous there.
PC-1 cannot extend that decision merely because the numeric values converge.
Indeed a continuous map from the connected circle into a discrete decision
space is constant. A useful discrete verdict needs a proved margin, an
appropriate restricted domain, or an explicit unresolved boundary.

Proposal, mathematical evaluation and authorization consequently retain
different meanings after completion. Exact numeric replay supplies no
external grant, jurisdiction, institutional standing or physical model.

## 9. The bounded next target

The [actual U=t chain derivation](meron_time_and_volume_refinement.md) now
supplies Hamiltonian binding and common-target time/volume errors for its
corrected full partition log density. Its Lipschitz scalar target closes to
the supplied real parameter line. The remaining targets below concern other
models, nonpartition numerators, spatial-mesh fields and operator transport.

For one chosen Meron/CODA model, bind the actual ensemble and observable to
its finite presentations and refinement maps; prove the sign/weight and observable-numerator
identities; select the topology; and give model-specific sampling, time-mesh
and volume remainders against a common target. Then apply PC-1 or the
coherent-decoder bound to the protected observable. Specify the order of
limits and prove any interchange actually used. The regularity/error law
must hold across the refinement family; separate bounds whose constants
grow with the mesh do not automatically give a vanishing remainder.

The circle presentation/character closure above is a real conditional
completion. It narrows the remaining continuum problem to regularity,
model binding and quantitative transport; it does not discharge those
obligations through duality alone.

Replay the finite illustrations from the repository root:

```sh
py -3.12 -B omega_engine_projects/finite_to_continuum/code/presentation_closure_examples.py
py -3.12 -B -m pytest -q omega_engine_projects/finite_to_continuum/tests/test_presentation_closure_examples.py
```

The [companion](../../../../../../omega_engine_projects/finite_to_continuum/code/presentation_closure_examples.py)
and [tests](../../../../../../omega_engine_projects/finite_to_continuum/tests/test_presentation_closure_examples.py)
exercise finite values and actual source functions. They are distinct from
the Lean metric proof and do not mechanize infinite character classification
or Haar measure.

## 10. Keep the physical scaling question explicit

The [actual source observable](meron_spin_and_observable_transport.md) now has
a fixed-volume time limit. To take its staggered susceptibility further, first
choose its intensive normalization, common temperature and growing-volume
target. A bound whose constant grows exponentially with L does not itself
close that target. Partition log-density convergence also cannot simply be
differentiated twice to obtain convergence of susceptibilities.

A spatial field profile must additionally declare lattice spacing, coupling
and temperature scaling, test/smeared observables, retained sectors and the
topology of correlation convergence. In critical finite-size scaling, theta
may grow with L; the earlier theta/L boundary bound need not vanish. Retain
the odd-periodic/even-twisted sectors rather than discarding them by a fixed-
temperature bulk-density argument. Pontryagin closure supplies the selected
character geometry; it supplies neither that correlation estimate nor the
physical dynamics. A successful endpoint needs compatible observable maps
and a common-target error tending to zero in the declared scaling regime.

## 11. A response with retained resolution now closes

The [actual source-field proof](meron_source_field_response.md) supplies
a Lipschitz common pressure on the admitted theta/lambda parameter domain,
with field-uniform volume and joint time/volume errors. It derives weak
response convergence and a triangularly averaged response at every fixed
field resolution. This supplies a further actual observable to PC-1, with
the resolution retained as part of the query. Letting resolution vanish
requires pressure errors o(epsilon^2) and a justified pointwise identification.
The full periodic Kubo susceptibility and spatial field profile therefore
retain their explicit derivative, sector and scaling obligations.

## 12. The actual intensive response closes in an analytic region

The [uniform-source theorem](meron_analytic_response.md) now proves the
pointwise intensive Kubo limit for theta<=1/192. Even-CAR factorization
handles the periodic bond directly; a uniform polymer margin supplies the
complex-source bound and Cauchy estimates. AR-9 closes the actual query
<Q^2>/((2M)^2L) under polynomial joint refinement at a common admitted
temperature. Thus the previously missing derivative witness is supplied
in this region, rather than assumed from pressure convergence.

The circle/Pontryagin branch establishes selected geometric completion;
this theorem adds one actual dynamical response limit at fixed spatial
lattice. Passing to a field theory still requires a spatial mesh and
coupling/temperature/observable scaling profile with convergence estimates.
The theorem makes no statement about the q=3,M=2 fixture or other
temperatures outside its analytic domain.

## 13. Circle completion now carries a static spatial source limit

The [spatial-source theorem](meron_spatial_gaussian_source.md) takes the
selected completed circle seriously as a test-function domain. It retains
one Lipschitz profile across meshes, derives actual local response decay,
and proves a Gaussian limit of the original Meron source functional under
declared fluctuation scaling. Integer circle characters then construct the
limiting Gaussian random distribution and its quadratic pairing.

This is a concrete common-target spatial closure with its own error law.
It does not select the circle topology or scaling from a primitive mark,
promote finite signed source sums into probability measures, or identify
an interacting spacetime quantum field. Those require distinct additional
semantics and estimates; software evaluation still grants no authorization.
