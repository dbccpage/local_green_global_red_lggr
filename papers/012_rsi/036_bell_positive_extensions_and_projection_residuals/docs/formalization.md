# Bell formalization, version 0.10.0

The package contains 656 named Lean theorems. `axiom_census.json` binds every proof
source, compiler configuration, and offline dependency archive to a fresh build.
`lean4/Census.lean` requests every named theorem; `tools/replay_lean.py` checks that
this inventory is exhaustive and rejects axiom dependencies other than
`propext`, `Quot.sound`, and `Classical.choice`.

## Claim-to-proof map

| Manuscript result | Lean declarations | Exact scope |
|---|---|---|
| Theorem 2, actual repair infimum | `Bell.Repair.bell_strong_duality`, `Bell.RepairGeometry.repair_eq_distance`, `repair_zero_iff`, `repair_lipschitz` | Finite scenario with nonempty outcome types and normalized nonnegative context weights. Strictly positive weights are required for zero repair iff positive extension. Both minimization and the Lipschitz bound use the existing weighted-TV definition. |
| Theorem 3 and (29), attained LP duality | `Bell.ConvexDistance.attained_duality`, `Bell.LinearProgramming.contextuality_strong_duality`, `Bell.Repair.bell_support_duality`, `bell_witness_bound`, `bell_slack_primal` | Separation constructs a dual witness, including zero-distance handling. The Bell bridge proves marginal/mixture and weighted-cost identities. Dual coefficients satisfy abs(c_i) <= pi_i/2. The general lower bound requires L>0 and abs(c_i)<=L*pi_i/2. Both optima and slack LP optimality are proved. |
| Proposition 4, intrinsic tangent cone | `Bell.Polyhedral.exists_scalar_iff`, `projection_one`, `Bell.PolyhedralProjection.linear_image`, `Bell.RepairGeometry.local_polyhedral`, `localTangent_intrinsic`, `bell_explicit_ray_window`, `bell_quadratic_remainder` | Finite elimination constructs an inequality description from the simplex image. Equality constraints are preserved as opposite inequalities. A closed cone has a nearest vector; finite slack supplies a positive ray window. A supplied weighted-TV remainder <= C*t^2 yields the same constant in the repair error bound. No derivative, enclosure, or numerical time window is assumed proved. |
| Section 11, signed LP duality | `Bell.SignedDuality.affine_norm_duality`, `negative_mass_weak_duality`, `negative_mass_dual_optimal`, `bell_negative_mass_duality`, `bell_signed_spread_duality` | An inhabited normalized signed fiber is explicit. Closed affine-fiber l1 minimization constructs an optimizer and a kernel-annihilating functional; quotient factorization gives the LP dual. The norm/negative-mass identity and vertex-spread reduction are proved. |
| Theorem 1, finite stochastic locality iff positive extension | `Bell.positive_extension_iff_local`, `response_total`, `response_marginal`, `extension_nonnegative`, `extension_total`, `extension_marginal` | Arbitrary finite setting and outcome types, real nonnegative normalized latent weights, normalized local response distributions. The forward proof constructs the product response distribution over all deterministic assignments. The reverse proof constructs indicator responses. |
| Theorem 1, arbitrary latent carriers | `Bell.positive_extension_iff_averaged`, `averaged_extension_nonnegative`, `averaged_extension_total`, `averaged_extension_marginal` | A declared subalgebra of real functions on any latent type and a positive normalized real-linear averaging map. Response functions lie in that algebra. No finite latent carrier is required. |
| Theorem 1, actual probability integrals | `Bell.Integral.positive_extension_iff_probability_integral`, `functions_integrable`, `response_bounded`, `atomicMeasure_probability`, `atomicMeasure_integral` | Arbitrary measurable latent space with a setting-independent probability measure; measurable, nonnegative, pointwise-normalized finite response families. Boundedness, integrability, integral linearity/positivity/normalization, and the atomic-measure converse are proved. |
| Proposition 5a, quantum CHSH ceiling | `Bell.Quantum.tsirelson_operator_bound`, `tsirelson_pure_state_bound`, `tsirelson_mixed_state_bound`, `tsirelson_dichotomic_bound` | Complex inner-product space; bounded linear contractions. Hermitian involutions are proved to preserve norms and hence be contractions. State results use unit vectors or finite nonnegative normalized mixtures. The bound itself does not require commutation. |
| Proposition 5b, binary effects to contractions | `Bell.QuantumState.povm_observable_hermitian`, `povm_eigenvalues_bound`, `povm_observable_contraction` | Arbitrary finite complex matrices; each effect is positive semidefinite and the pair sums to identity. Hermiticity and Hilbert operator-norm contractivity are derived. |
| Proposition 5b, density matrices to mixtures | `Bell.QuantumState.density_weights`, `density_vectors_unit`, `density_spectral_decomposition`, `density_trace_mixture`, `density_trace_real`, `density_povm_chsh_bound` | Positive semidefinite unit-trace finite matrix. Actual eigenweights and orthonormal eigenvectors are constructed, with an explicit sum of rank-one matrices and equality for every real trace expectation. No full-rank or supplied-mixture premise. |
| Proposition 5b, actual joint Born tables | `Bell.QuantumMeasurement.born_complex_trace`, `born_nonnegative`, `born_probability`, `born_alice_marginal`, `born_bob_marginal`, `born_score_trace`, `born_chsh_bound` | Reality and positivity use cross-party commutation of effects. Normalization and marginal/score identities are algebraic. The score bound alone needs no commutation, but an arbitrary noncommuting product table is not asserted to be a probability model. |
| Proposition 5b, local tensor specialization | `Bell.QuantumMeasurement.leftLift_povm`, `rightLift_povm`, `tensor_cross_commute`, `tensor_behavior_eq`, `tensor_born_probability`, `tensor_born_chsh_bound` | Independent arbitrary finite Alice/Bob dimensions; Kronecker lifts preserve positivity/normalization and prove commutation. The actual table is `Re Tr(rho (M tensor N))`, with the generic real-trace theorem supplying equality to the complex Born trace. |
| Sections 3.2 and 5.1, quantum saturation | `Bell.QuantumExample.mean_eq_inner`, `alice_hermitian`, `bob_hermitian`, `alice_square`, `bob_square`, `local_commutation`, `born_formula`, `bell_state_unit`, `tsirelson_attained`, `bell_behavior_no_positive_extension` | Explicit complex two-qubit matrices and Born projectors on the normalized Bell vector; the outcome table equals `isotropic (1/sqrt 2)` and has score `2 sqrt 2`. The parties' observables commute. |
| Section 3.2, CHSH | `Bell.CHSH.deterministic_values`, `marginal_score`, `mixture_bound`, `positive_extension_chsh`, `stochastic_local_chsh`, `violation_no_extension` | Canonical CHSH orientation; Boolean outcomes encode -1 and +1. The marginal-score identity is proved, rather than assumed. |
| Equation (7), uniform-setting witness | `Bell.CHSH.score_lipschitz`, `chsh_repair_lower_bound` | For every positive local extension, its distance from a table is at least `max(0, abs(S)-2)/8`; total variation is the sixteen-entry absolute difference sum divided by eight. This is a universal bound over every local approximation, not a definition of the approximation error. |
| Section 5, signed-extension obstruction | `Bell.CHSH.signed_total_variation`, `signed_chsh_bound`, `signed_negativity_lower_bound` | A normalized signed extension has `abs(S) <= 2(1+2N)`, hence `N >= max(0,abs(S)-2)/4`. Positivity is not silently imposed on signed weights. |
| Section 5, isotropic CHSH threshold | `Bell.CHSH.isotropic_score`, `isotropic_nonlocal` | `S(p_v)=4v`; `v>1/2` rules out a positive extension. The exact attained repair cost and quantum-realizability interval remain separate results. |
| Section 11, uncertainty-adjusted witness | `Bell.CHSH.uncertain_repair_lower_bound`, `uncertainty_excludes_extension` | A supplied uniform total-variation enclosure of radius epsilon reduces the CHSH excess by `8 epsilon`. The theorem does not construct a confidence interval or certify an experiment. |
| Theorem 7, measurement contraction | `Bell.QuantumTrace.hermitian_trace_mixture`, `measurement_l1_bound`, `measurement_tv_bound`, `weighted_measurement_tv_bound`, `density_traceNorm` | Arbitrary finite complex Hermitian matrices; trace norm is the sum of absolute eigenvalues. Every finite positive POVM summing to identity contracts the outcome L1 distance. Nonnegative normalized context weights, including zero weights, give the half-trace-norm TV estimate. |
| Theorem 7, actual Born comparison | `Bell.QuantumTrace.born_tv_bound`, `tensor_tv_bound`, `repair_le_comparison`, `born_repair_bound`, `state_distance_witness` | Arbitrary finite party dimensions. Joint commuting effects, or tensor lifts with commutation derived. The repair is an actual infimum over positive-extension behaviors; the chosen comparison state must have a positive-extension Born table. The supplied-comparison interface remains available; the new separable construction below derives that premise for every finite separable density. |
| Theorem 7, separable-state construction | `Bell.Separable.mixture_density`, `product_mean`, `povm_probability`, `mixture_born`, `separable_positive_extension`, `separable_chsh_bound` | Actual finite mixtures of product density matrices, nonnegative normalized weights, and arbitrary finite local POVMs. Constructs a `LocalModel` and then a positive global extension. No local-image assumption. |
| Theorem 7, partial traces and product reference | `Bell.Separable.leftMarginal_density`, `rightMarginal_density`, `productMarginals_density`, `productMarginals_separable`, `leftMarginal_product`, `rightMarginal_product`, `productMarginals_idempotent` | Entrywise partial traces of the given bipartite density; positivity and trace one derived. The product map is proved idempotent. |
| Theorem 7, full inequality (15) | `Bell.Separable.born_probability`, `born_complex_trace`, `born_weightedTV_bound`, `separableDistances_bddBelow`, `separableDistance_nonneg`, `full_state_to_behavior_bound`, `chsh_full_state_to_behavior_bound` | Infimum over all positive-extension behaviors is bounded by half the infimum of the finite Hermitian trace norm over all finite separable mixtures, then by half the product-marginal residual. Arbitrary finite dimensions/settings/outcomes; nonnegative normalized context weights, including zeros. Nonemptiness is constructed; no optimizer or compactness premise. |
| Equations (16)--(18), matrix witness dynamics | `Bell.QuantumTrace.trace_operator_bound`, `Bell.Dynamics.trace_decomposition`, `dynamical_witness`, `dynamical_born_repair` | Actual real trace expectations and the Hilbert operator norm. A Hermitian remainder, the exact decomposition `rho = sigma + t v + E`, and `traceNorm E <= kappa t^2` are supplied. No equation of motion, derivative, or remainder enclosure is inferred. The algebraic result applies even without density/POVM premises; those premises give its physical Born interpretation. |
| Section 6.2, finite-time and uncertain exit | `Bell.Dynamics.oriented_repair_bound`, `uncertain_oriented_repair`, `oriented_exit`, `quadratic_exit_window`, `quadratic_linear_rate`, `zero_remainder_window`, `face_exit_rate` | Canonical oriented CHSH witness; every positive local extension. Positive-time condition `c*t < b` avoids division by a possibly zero coefficient. The half-rate interval gives repair at least `t*b/16`; zero remainder is handled separately. Supplied TV uncertainty subtracts `8 epsilon`. |
| Theorem 8, task sufficiency | `Bell.Observer.factors_iff_constant_on_fibers` | Scalar targets factor through the report exactly iff they are constant on its fibers. This qualitative theorem does not require finiteness. |
| Theorem 8, exact scalar minimax | `Bell.Observer.fiber_extrema`, `minimax_lower`, `midpoint_optimal`, `scalar_minimax` | Finite nonempty history set; arbitrary report type; real scalar target and absolute error. Actual extrema and a midpoint predictor are constructed, and the infimum over all predictors is proved equal to half the maximum fiber width. |
| Section 9.4, additional information | `Bell.Observer.refinement_cannot_increase_minimax` | The old report must be a deterministic function of the new report. |
| Theorem 10, deterministic recursion | `Bell.Observer.recursion_preserves_fibers`, `recursion_error_floor` | Any number of updates using only the unchanged report and a common initial state, followed by an arbitrary readout. No restriction on the state type or update complexity. |
| Theorem 10, randomized predictions | `Bell.Observer.randomized_error_floor` | Finite output/seed type with a nonnegative normalized conditional distribution for each report. The law may depend on the report but is shared by histories in that fiber. The bound concerns worst-case expected absolute error. |

## Averaging and integration

The integral proof in Theorem 1 uses only positivity, normalization and linearity
of averaging on the algebra generated by the bounded measurable response
functions. `AveragedModel` exposes these laws as ordinary theorem hypotheses,
and Lean proves the construction and its converse under them. It also proves
that every finite stochastic model supplies such an averaging model.

`Bell.Integral` instantiates that interface using Mathlib's Bochner integral on
bounded measurable real functions. Every response coordinate is bounded by one,
so products in the algebra are integrable on the probability space. Integral
linearity, positivity and normalization are derived. Conversely, normalized
finite weights induce a sum of scaled Dirac measures; Lean proves both its
probability normalization and its finite-sum integration formula. The resulting
`positive_extension_iff_probability_integral` is the full probability-integral
equivalence. Its assumptions are ordinary measure/model hypotheses, not custom
kernel axioms. `probability_integral_chsh` gives the classical bound directly.

## Quantum conventions

`Bell.Quantum.chsh` is the bounded complex-linear operator
`A0.comp (B0+B1) + A1.comp (B0-B1)`. The parallelogram identity and contraction
bounds give its operator norm ceiling. Cauchy--Schwarz gives the unit-vector
expectation bound; positive normalized finite mixtures preserve that ceiling.
The `Dichotomic` interface states inner-product symmetry and an involution;
Lean derives norm preservation and contractivity from those two properties.

The explicit example uses Pauli X and Z matrices, Kronecker products, the Bell
vector in complex Euclidean space, and outcome projectors `(I + a A)/2`.
`mean_eq_inner` identifies the finite sum with the Hilbert inner product.
Hermiticity, the squared-observable identities, cross-party commutation and
normalization are checked, and the actual Born table is computed exactly.
No floating-point value of the square root enters these proofs.

`Bell.QuantumState` uses Mathlib positive semidefiniteness and trace one as the
complete density interface. The eigenvalues give probability weights and the
orthonormal eigenbasis gives unit vectors, including when some eigenvalues vanish.
The explicit rank-one reconstruction and trace-mixture identity are proved.
For each binary POVM, the two positive quadratic forms sum to one on a unit
eigenvector; their difference lies in [-1,1], giving operator contractivity by
unitary diagonalization. `asOperator` uses `Matrix.toEuclideanCLM`; the norm is
explicitly the L2 operator norm, not an entrywise or Frobenius matrix norm.

`Bell.QuantumMeasurement` proves the joint probabilities are actual real Born
traces, nonnegative and normalized, with marginal identities that imply
no-signalling. Cross-party commutation is explicit at this probability boundary.
The score-to-trace identity is proved algebraically. Kronecker lifts establish
all local measurement premises for independent finite party dimensions.

## Trace-norm and dynamical conventions

`Bell.QuantumTrace.traceNorm Z hZ` is `sum_i abs(lambda_i(Z))` for a
Hermitian finite matrix, the spectral formula for its Schatten 1 norm.
It has no factor one half. It does not install a norm on arbitrary matrices or
claim an infinite-dimensional trace-class construction. The eigenvalues and
orthonormal eigenvectors come from Mathlib's actual matrix spectral theorem.
The trace-mixture identity is proved for signed eigenvalues, then positivity
and completeness of POVM effects prove the L1 contraction. Density trace norm
one is also derived. Cauchy--Schwarz and the operator norm yield
`abs(Re Tr(Z B)) <= norm(asOperator B) * traceNorm Z` for every matrix B.

The dynamical results use these matrix inequalities, rather than taking the
witness error bound as a hypothesis. Taylor control and the identification of
sigma with a product reference remain model premises. Positive excess gives
nonlocality and a repair lower bound. A nonzero state residual alone supplies
neither an oriented witness nor a positive excess.

## Separable-state and infimum conventions

`Bell.Separable.Ensemble` carries a finite index count, a probability vector,
and a pair of genuine local density matrices for each index. `mixture` forms
their weighted Kronecker sum; `IsSeparable` asserts existence of such an
ensemble. This is finite-dimensional separability by finite convex mixtures;
it does not assert an infinite-dimensional closure or provide an algorithm
for deciding separability.

`leftMarginal` and `rightMarginal` sum principal submatrices. Positive
semidefiniteness survives those sums and trace one follows by exchanging
finite sums. Product Born factorization is proved from tensor multiplication
and trace identities, with the imaginary trace parts proved zero. The local
responses are actual Born probabilities, not additional supplied data.

`behaviorRepair` is the real infimum over positive-extension behaviors in
the weighted total-variation pseudometric. `separableDistance` is the real
infimum of trace norms over `IsSeparable` density matrices; `productResidual`
uses the given state's two partial traces. The product-marginal state proves
that the distance set is inhabited and all its values are nonnegative.
The proof bounds the behavior repair for every separable comparison before
taking the infimum, without assuming attainment. The CHSH specialization uses
the pre-existing `Bell.QuantumTrace.repair` and `Bell.CHSH.tv` directly.

## Observer conventions

Empty report fibers receive predictor value zero and never enter the risk.
`maxWidth` takes the maximum of the width at `O(h)` over histories. This equals
the manuscript's maximum over the image of `O`, because duplicate reports do
not change a maximum. `scalar_minimax` uses the infimum of the range of the
actual worst-case-error function. The companion `midpoint_optimal` proves
attainment, so the result is not only an unattained lower bound.

## LP and tangent conventions

The eight added modules contain 75 named theorems. `ConvexDistance` supplies
attained compact/closed convex distance duality. `LinearProgramming` adapts the
finite coordinate argument from the RSI contextuality paper; its proof is
included here, with no sibling import. `Repair` connects it to the Bell model.
`SignedDuality` handles the normalized signed fiber, rather than assuming its
feasibility for arbitrary signalling data.

`Polyhedral` and `PolyhedralProjection` prove finite real-variable elimination
and linear-image closure. `TangentCone` proves the geometric result for finite
linear inequalities, including identification with the closed radial cone.
`RepairGeometry` constructs the Bell presentation and transports the result
through the weighted l1 embedding. Strictly positive weights identify the
paper's norm; with zero weights the repair results use its weighted image and
pseudometric. The chosen inequality presentation carries a proved equality to
the actual Bell simplex image, not an extra facet-completeness hypothesis.

The time result is one-sided near zero. It supplies a positive existence
window and retains the trajectory remainder bound as a premise. A positive
state residual alone still does not prove a Bell-cone escape.

## Results outside this census

The full isotropic repair-cost
sharpness calculation, infinite-dimensional trace-class density/POVM conversions,
other explicit quantum trajectories, Mermin cohomology statements, and arbitrary-measure random-output
expectations retain their written proofs and existing finite checks. The new written saturating-product support argument is also outside the census. The census
does not certify the Python interpreter, SciPy, experimental assumptions, or the
behavior of a deployed agent.

## Replay

Install Lean 4.35.0 and set `ELAN_HOME` to its installation. The packaged
`lean4/vendor/dependencies.tar.gz` contains the required pinned Mathlib closure,
sources and licenses; its manifest records the upstream revisions and every
file digest. No sibling paper or network fetch is used by the proof replay.

Run `python verify_deposit.py` for the complete verification, or
`python tools/replay_lean.py` for the fresh Lean build and census alone.
Each replay creates a new proof build directory. The dependency cache under
`lean4/.lake/vendor` is checked against its manifest and is excluded from the
release archive. `--record` regenerates the census for an intentional source
revision; normal verification never rewrites the declared evidence.

## Contextual fraction and real signed-mass comparison

The five added modules are ContextualFraction, NegativeMassFamilies, BinaryScenarios, ComparisonData and Comparison. Contextual fraction is defined as one minus the supremum of actual feasible local-subdistribution masses. Nonemptiness, boundedness, primal upper bounds, dual lower bounds, and exactness of matching certificates are proved. General CF dual attainment is not required or claimed by this module.

The theorem negative_mass_exact constructs a real extension and proves its minimal negative mass against every real competitor. The BinaryScenarios family theorems instantiate actual zero-one incidence matrices. The parameter ranges over all real v in [0,1] for the probability/CF assertions, not just eighths; the algebraic signed-mass theorem covers v>=0. The chsh_behavior_bridge theorem identifies the new finite-cell encoding with the existing CHSH isotropic behavior. Finite incidence identities are checked by kernel decide, not native_decide.

Comparison.contextual_fraction, signed_mass, negative_mass_optimal, cf_gt_twice_negative_mass and ranking_reversal establish the explicit real optimization conclusions. Integer certificate vectors are bound to Python JSON by the read-only generator. The full no-signalling and context-normalization checks are replayed in exact Python; their mathematical interpretation also follows from the written convex-mixture construction. The Lean theorems assert the exact concrete real table and optimization values, without claiming a generic no-signalling or quantum-realizability proof for it.

ContextualFraction.packing_from_signed constructs dominated nonnegative local weights from any normalized signed extension. The fraction_le_negative_mass theorem proves CF <= (m-1)N(q) for finite zero-one matrices with common positive column sum m, nonnegative p of total m, and a normalized real signed preimage. It does not assume a desired comparison or supplied optimal dual. Taking an attained minimizing extension gives the N_min corollary. No sharpness claim is made.

The imported GLM BellNegMass.lean is historical source material, outside the library and census. Its fixed-scale integer optimization statements are not substituted for the real statements above. No Python-to-Lean equivalence or solver search-completeness theorem is asserted.

## Quantum-restricted comparisons and explicit evolution (0.9.0)

QuantumComparisons derives isotropic CHSH caps from an actual Hilbert-space expectation and contraction bounds. Its scalar nCHSH is the minimum established by BinaryScenarios.chsh_negative_mass, not a new optimization definition. It does not classify all quantum behaviors.

GHZEvolution constructs the three-qubit pure state and tensor-product X/Y measurement effects. QuantumWindows.local_povm proves positivity and completeness of the local effects. The arbitrary-real-amplitude Born formula is instantiated by cos/sin, and all_visibilities_quantum constructs a normalized state for each real v in [0,1]. The optimization conclusions cover every real signed competitor. Rotation unitarity, the group law, identity, and Hermitian active Hamiltonian are proved; the identification with the full eight-dimensional matrix exponential is written and independently numerically checked. No general ODE or matrix exponential theorem is claimed.

QuantumWindows.Local is an actual nonnegative normalized extension over 64 assignments. Exact_exit proves both directions on 0 <= t <= pi/4. Before and at the onset, an explicit extension exists. Noisy_exit accepts an arbitrary actual table and a score-error budget. Noisy_cf_lower additionally requires nonnegativity and active-context normalization (pairing abs(c) p = 4). Noisy_negative_mass_lower applies to every normalized signed extension of the actual table. Noisy_tv_exit converts uniform eight-context total variation into a score budget of 16 epsilon. The first-interval restriction, strict exit inequality, and loss of this certificate at large uncertainty are explicit. Physical coupling rescaling is written.

No quantum realization of Comparison.point, sharp universal quantum comparison, or general dynamical remainder theorem is added. See contextuality_side_note.md for a reader-level literature assessment.

## Full three-setting quantum counterexample (0.10.0)

ChainedData enumerates all 64 deterministic response assignments for all nine setting pairs, with a completeness theorem for arbitrary pairs of three-setting Boolean response functions. The integer identities use kernel decide. ChainedComparison proves exact CF and minimum negative mass for every real 2/3 <= v <= 1, with constructed packing/signed extensions and matching dual witnesses against all real competitors.

ChainedQuantum constructs local complex projective effects on each qubit and uses the normalized Phi-plus state. The Born formula covers every cell of the full 36-cell behavior. Quantum_realization proves positivity/completeness and normalization; quantum_counterexample supplies the strict CF > 2N inequality and the attained signed minimum. Universal_coefficient_at_least_four is a necessary constraint on any bound applied to this quantum example, not a universal coefficient-four upper bound.

The earlier three-party no-signalling example remains without an established quantum realization. The new example changes the scenario to two parties with three binary settings each. Exact Python arithmetic in Q(sqrt(3)) checks the Born matrix and primal/dual certificates independently; no universal Python-to-Lean equivalence or solver search-completeness claim is made.

## Larger chains and measurement covers (0.11.0)

PlanarQuantum proves arbitrary real planar projective effects and their Bell-pair Born formula, including angular parametrization. SparseCertificates embeds sparse witnesses into the full assignment space and bounds their negative mass. FiveData checks integer certificates over all 1,024 responses and all 100 cells, with a constructive bit-vector completeness proof; decide +kernel uses trusted kernel reduction, not native_decide. FiveComparison proves both exact real optima, and FiveQuantum proves the complete two-qubit realization and strict CF>4N.

CycleParity retains every odd failure pattern of an arbitrary even cycle, constructs signed and positive packings and proves both real optima. CycleLimits quantifies over every proposed finite coefficient and proves a counterexample in that parity quotient at the quantum cosine visibility. Its edge Born formulas and closing sign are explicit. Version 0.12.0 adds the reconstruction, global-sign and optimization equivalences in CycleLifting, described below.

ChainAnalysis proves the trigonometric error bound, integer grid rounding, CHSH score floor, negative-mass floor and explicit 160/17 bounded-tail coefficient for n>=64. FullChainBounds proves the signed CHSH bound and pulls it back to any finite signed model reproducing the four declared correlations. The complete table necessarily reproduces those correlations; no bound over all quantum measurement families is asserted. ChainAsymptotic.eventual_coefficient proves the quantified tail statement for every k>2(sqrt(2)+1). The limsup notation is the manuscript formulation of that bound, rather than a separate Filter.limsup declaration.

## Complete smoothed Gram family and cycle equivalence (0.12.0)

CycleLifting proves inverse path reconstruction, closing parity, a literal equivalence between odd cycle patterns with a root sign and vertex assignments, and propagation of a global sign flip. Encode/decode are inverse recodings of actual binary outcome pairs into failure and left outcome. For the two-fold incidence, lift/down preserve total weight; lift preserves negative mass, and down cannot increase it. Feasible packing-weight sets are equal, hence contextual fractions are equal; signed_budget_iff gives equality of the achievable negative-mass budgets. The cycle-specific corollaries use CycleParity.A and point. List versus Fin enumeration is presentation glue; there is no assumed lifting identity among the theorem premises.

LocalGram constructs the shared-coordinate/shared-sign stochastic local model and its positive deterministic extension. It constructs a white-noise extension and proves the normalized complete-table signed extension with mass at most (1-s)/s. Real-vector normalization and inner-product bounds are proved. RampSums proves the finite linear/square sums, ramp square sum, flat-plus-ramp norm identity, active-edge energy and the algebraic visibility conversion. ScenarioRestriction proves packing and signed projection and monotonicity of contextual fraction under restriction.

SmoothedComparison proves the exact scalar envelopes and ratio identity, their positivity and a quantified no_uniform_coefficient theorem for sequences satisfying these envelopes. This theorem has explicit envelope premises: it does not manufacture a quantum behavior from them. Theorem 22 has a complete written construction using modular translates and the standard Tsirelson/Clifford representation. Version 0.13.0 closes those two steps with the additional modules below; neither is inserted as a new axiom. The exact Python replay covers six finite members (25,810 complete contexts); a separate 256-dimensional Clifford replay checks 64 Born cells for k=2. Neither finite replay proves the all-size statement.

## Complete quantum construction and selected shadows (0.13.0)

CyclicProfile constructs the modular piecewise ramp and proves its bounds,
antiperiodicity, squared norm, cyclic energy and translated adjacent products.
Clifford constructs D anticommuting real-symmetric complex matrices on
Carrier D of cardinality 2^D. This nonminimal representation suffices;
the separate numerical replay uses the smaller standard representation.

CliffordObservables derives Hermitian involutions, orthogonal trace products
and positive binary projectors. MaximallyEntangled constructs the trace-one
positive density using entries 1/d and proves its tensor trace identity.
GramQuantum.Model contains actual matrices and POVMs with every Born cell
equal to the requested table. Its realization theorem covers arbitrary
finite families of real unit vectors.

ChainWitness proves the parity failure bound directly on all assignments,
linearity of the witness, its packing bound and CF upper bound. SmoothedFamily
constructs the complete table, quantum model, local visibility model, signed
certificate, adjacent and closing correlations, and CF lower bound.
The two integer parameters satisfy n+1=k*k because Fin(n+1) simplifies the
path induction; no setting is removed.

CompleteQuantumUnbounded constructs an attained signed optimizer from the
existing LP theorem. Its minimumMass is the mass of that optimizer, proved
minimal against every real normalized signed preimage. It is strictly
positive. quantum_unbounded has only C>=0 as a mathematical premise: actual
quantum realization and CF/N_min>C are conclusions. No supplied envelope,
quantum predicate, search-completeness or Python-equivalence premise remains.

ContinuumShadows proves the reciprocal presentation identity, strict finite
error estimates, a cutoff for values inside the envelopes, and the absence
of a finite real endpoint for the ratio envelope. CompleteQuantumUnbounded
instantiates the cutoff with actual CF and minimumMass. These are explicit
epsilon statements in the usual real metric, not a separately declared
Filter.Tendsto theorem or a physical continuum claim. The written local-shadow
cellwise/TV observation and historical WDP completion theorem remain separate
from this package's named-theorem census.
