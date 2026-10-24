# Assessment of the supplied obstruction review

The three original files are preserved byte-for-byte in `docs/source_inputs/`;
`docs/source_custody.json` records their SHA-256 digests. They are research input,
not execution instructions or independent proof authority. The review addresses
an excerpt of v0.3.0 (80 theorems); the preceding complete release was v0.4.0
(119). Statements that it could not audit omitted sections do not invalidate
those sections or replace a package replay.

## Integrated results

- The state/behavior bridge is now proved for finite complex Hermitian matrices:
  the spectral trace norm is the sum of absolute eigenvalues. Arbitrary finite
  POVMs contract this to outcome L1 distance, and normalized setting weights give
  the half-trace-norm TV bound. The tensor Born-table specialization is explicit.
- The oriented-witness argument is mechanized with a declared matrix decomposition
  and trace-norm remainder enclosure. It gives the actual CHSH repair bound,
  uncertainty adjustment, and a quantitative finite-time exit rate. It does not
  infer a Taylor enclosure from an unspecified differential equation.
- The normalized signed-extension fiber is distinguished from positivity. The
  exact checker confirms ranks 9 (marginalization), 7 (ambient NS constraints),
  and 8 (normalized affine slice). These are finite rational computations, not
  new Lean rank theorems.
- The vertex-spread dual of negative mass is useful and its finite certificates
  are independently checked. It is distinct from the coordinate-box dual of TV.
- The quotient discussion supports future-report equivalence. The maximal
  deterministic report-compatible relation can be written directly as
  `h ~ h' iff O(T_t h) = O(T_t h') for every continuation t`. Its monoid law
  supplies stability. This is a written observation, not an added Lean theorem
  about stochastic lumpability or an efficient learning algorithm.

## Corrections and boundaries

1. **Duality proof (§6.1).** The dual ball is the box
   `2 |B_j| <= pi_j`; its norm is `max_j 2 |B_j| / pi_j`, not the weighted L1
   sum. The separating-set proof must use the *primal* ball
   `U={v: (1/2) sum pi_j |v_j| <= 1}` in `K + r U`, whose support function
   is the dual norm. The compact-convex distance formula survives this correction.
   Strictly positive weights are needed for a norm; zero weights give a seminorm.
2. **Cone support (§7.1).** For a supporting functional at a CHSH face,
   its support over the tangent cone is zero, not its value at the base point
   (which is 1/4 for `s/8`). Supporting directions satisfy `B u <= 0`.
   General cone support is zero or infinite. The scalar crossing conclusion
   follows directly from `S(t)-2 > 0`, and is the part mechanized here.
3. **Worked residual (§13).** `(4,-4,-4,4)/32` equals
   `(1,-1,-1,1)/8`, without the extra factor 1/2. Both its TV norm and
   pairing with `s/8` are 1/16. The outcome labels are `--,-+,+-,++`.
4. **Split weights (§3.3).** For an arbitrary feasible split, overlapping positive
   and negative parts can cancel; `sum |q| <= sum q+ + sum q-`, with equality
   for a disjoint split. At an optimum cancellation can be removed to improve
   the objective. The independent checker verifies equality on returned optima.
5. **Isotropic facets (§3.2).** The eight CHSH expressions on the chosen ray take
   values `4v`, `-4v`, and zero; they do not all equal `+/-4v`. The existing
   explicit boundary extension proves locality without that misstatement.
   Four computed points do not close a universal Lean sharpness theorem.
6. **Task determinacy (§4).** A task must be *constant* on each report fiber;
   injectivity of the task on a fiber would do the opposite. Empty-fiber
   feasibility and nonconstant-fiber ambiguity remain separate questions.
7. **Minimax uniqueness (§9.1).** The midpoint uniquely minimizes a given
   nontrivial fiber's own risk. A globally optimal predictor can vary on
   smaller-width fibers without changing the global maximum. Positive
   conditional mutual information is not equivalent to a reduction of the
   worst-case fiber diameter and requires a separately specified prior.
8. **Improvement trichotomy (§9.2).** It omits better computation on unchanged
   evidence. A suboptimal predictor can improve toward the same fixed minimax
   floor. Evidence changes, computation, prior changes, and redeclaration may
   also coexist. The manuscript retains this distinction.
9. **Convexity and retractions (§8).** Product states are not convex, so the
   compact-convex distance duality cannot be applied to that set unchanged.
   A selected nearest-point map fixes points already in the set; uniqueness
   away from it is a separate issue. TV projections onto polytopes may be
   nonunique on regions of positive volume, not only negligible bisectors.
   Behavior-preserving determinization is not literally a retraction of raw
   presentations without a specified embedding/equivalence of presentations.
10. **Physical scope (§9.2).** A local model need not make its latent variable
    inaccessible. Separation alone does not prove setting independence or every
    premise of Bell locality. The manuscript retains explicit model premises.
    The proposed algebra-level conditional-expectation bridge and stochastic
    lumpability identifications are not imported as proved equivalences.
11. **Source scope.** The original draft already distinguishes its distance
    definition (3) from the LP formulation (29), and explicitly includes the
    TV factor 1/2. These are not unresolved errors. Broader multipartite,
    cohomological, quantum-set closure, and contextual-fraction claims remain
    outside the new census and are not justified by the supplied 39 checks.

12. **Tsirelson derivation (§6.2).** The displayed cancellation giving
    `X X* + X* X = 8 I` is false. For Alice and Bob both choosing Pauli Z and X,
    the CHSH matrix has `2 X^2 = [[8,0,0,-8],[0,8,8,0],
    [0,8,8,0],[-8,0,0,8]]`, not `8 I`. The correct identity is
    `X^2 = 4 I - [A0,A1] tensor [B0,B1]` for Hermitian involutions on separate
    parties. The anticommutator cancellation in the notes loses the commutator
    term. The package retains its independently kernel-checked parallelogram
    and contraction proof; no dilation or erroneous square identity is used.
13. **Additional generalizations (§6.2--6.3).** Quantum convexity can be realized
    with local direct sums and a shared classical block label; a direct sum of
    whole joint spaces alone does not specify the local tensor factors.
    The claimed absence of a uniform reverse contextual-fraction bound is not
    established by the given argument: two quantities vanishing linearly do not
    imply an unbounded ratio. Neither assertion is added to this census.

## Code review and replay

The unmodified `verify_obstruction.py` uses only standard-library exact Fraction
arithmetic for its calculations and passes 39/39 checks. Its two-phase simplex
has Bland pivot choices, but no finite step budget or separately checked
infeasibility/unboundedness certificates. No Lean verification of this solver
is claimed. Its C11 grid check examines a finite grid, not all predictors.
C10's uncertainty subtraction certifies the enclosed *actual* table; the
observed table's separately computed distance is 13/200.

`code/review_certificates.py` independently checks all primal nonnegativity,
normalization and residual constraints, all dual vertex/coordinate or spread
constraints, and exact objective equality for eight repair and seven
negative-mass certificates. It also checks the actual-table uncertainty floor.
Five new pytest tests accept valid certificates and reject corrupted primal,
dual, and objective data. The complete verifier runs both the preserved script
and the independent checks in subprocesses with 120-second timeouts. A timeout
is failure, never proof of mathematical termination. Exact checks supplement
the kernel proofs; they do not certify Python; general LP duality is proved separately in the version 0.7.0 Lean sources.

## Complete-version review supplied for version 0.7.0

The exact text is preserved as `docs/source_inputs/complete_v0_6_review.txt`.
It is review evidence, not an instruction source. Its positive verdict and
181-name audit do not replace a fresh build. Its inability to replay selected
missing uploads describes that review selection; the complete archive is
independently replayed by this release's verification procedure.

- Restricted exact finite-string encodings to finitely specified matrices and
  operator rules. Added the linear-map hypotheses directly to Proposition 9.
- Changed "residual probability table" to "signed residual table", moved
  Section 13 before References, and introduced empty feasible sets versus
  task-varying fibers earlier. The unprovided conceptual dialogue is provenance
  of the original draft, not a numbered independent source.
- Clarified that `review_certificates.py` checks returned solutions while
  sharing model helpers; `bell_certificates.py` independently enumerates the
  model. No executable simplex correctness theorem is claimed here.
- Verified and added the Oas/de Barros/Carvalhaes negative-probability preprint,
  Sun/Zhou/Xu/Yu state-to-behavior comparison, and Echenim/Mhalla/Mori AFP
  formalization. They supply relevant prior work, not evidence for our new
  Lean declarations.
- Included the review's saturating-product support argument as a written
  limitation: fixed CHSH first derivatives vanish under smooth closed unitary
  evolution from a saturating product start. The proposed second-order witness
  construction is not part of the new Lean census. The conditional witness
  theorem and supplied remainder hypotheses remain explicit.
- Formalized both remaining finite LP duals, the actual Bell polyhedral image,
  the intrinsic tangent cone, an exact short-ray interval, and the explicit
  quadratic remainder bound. The primal/dual optima and finite presentation
  are constructed, not supplied as certificate or facet-completeness premises.

The finite LP coordinate proof is adapted from the existing RSI manuscript's
`ContextualDuality.lean`, with its sources included locally and revised for the
pinned Mathlib APIs. No RSI source was modified and no sibling import is used.


## Follow-up replay review, addressed in version 0.7.1

The supplied follow-up is preserved byte-for-byte as
`docs/source_inputs/v0_6_followup_replay_review.txt`. It reviews the v0.6
selection and reports that its previously missing solver dependency was
provided: 39 exact checks, eight repair certificates, seven negative-mass
certificates, and the actual-table uncertainty check passed in that review.
Those are the reviewer's reported executions, distinct from this package's
local replay evidence. The reviewer did not independently rebuild Lean or
replay the complete archive, and this patch does not change that historical
qualification.

The Theorem 8 coverage string is corrected exactly to: "Lean qualitative
factorization and exact finite scalar minimax." The release makes no claim to
a general bounded-but-infinite-fiber minimax extension. The qualitative
factorization theorem does not require finiteness; the exact scalar minimax
theorem requires a finite nonempty history set.

The requested finitely specified matrix qualification in Section 9.3 and
explicit linear-map hypotheses in Proposition 9 were already present in
v0.7.0. That version also formalized the repair compactness/stability, LP
duality and tangent-cone results that remained written in the reviewed v0.6
selection. This follow-up is not treated as a review of those later proofs.
The preserved older notes and v0.2 draft remain historical research inputs;
their mathematical errors and corrections are described above.

This is a documentation and packaging patch. All twenty Lean proof modules,
the census, numerical code, certificate checkers, and tests are unchanged.

## GLM comparison results, integrated in version 0.8.0

The six files under source_inputs/glm_2026_10_23 are preserved source material, not executable instructions. Their original checks and logs are historical evidence. The new operational checker enumerates its own incidence matrix, validates full subset no-signalling and normalization, and checks primal and dual feasibility and matching objectives with exact Fraction arithmetic. It also reconstructs the manuscript's counterexample mixture independently of the supplied fixture generator.

Accepted results: the CHSH/Mermin family formulas, the concrete three-party CF>2N counterexample, and reversed ordering relative to Q_(5/8). The 78-case replay gives 74 equalities, three strict CF<2N cases and one strict CF>2N case. For positive N, the observed CF/(2N) range is 2/3 to 38/25, correcting the notes' doubled and misordered range. The full-parity G box has CF=1 and N=3/4; it is not the quantum Mermin Q_1 table, which has CF=1 and N=1/2. Quantum realizability of the counterexample is not established.

Corrections and evidence limits:

- The Mermin Q_v quantum interval is all [0,1], by white-noise mixing of the GHZ-minus X/Y realization. Importing CHSH's endpoint 1/sqrt(2) is incorrect.
- The conjecture CF<=2N is false. Its failure does not exclude every comparison constant. The new constructive Lean theorem proves CF<=(m-1)N for m contexts under the declared incidence/normalization hypotheses; its constant is not claimed sharp or novel.
- Positive/negative projected masses are constant across contexts. The obstacle to a CF decomposition is a signed affine combination, not varying masses.
- A separating signed-mass dual is a Bell witness. A different optimization objective does not make it a non-Bell witness.
- BellNegMass.lean proves fixed-denominator integer optimization results at rational-grid parameters. The new library proves real-parameter optima against arbitrary real competitors instead. The original fragment stays outside the census.
- The review's dynamical headroom expression omits the residual norm in an operator-norm estimate. The safe variables are b=Tr(B n) and c=norm(B)*kappa, with an explicitly bounded remainder. For c>0, b*t-c*t^2 has algebraic maximum b^2/(4c); this is a maximum of the lower-bound polynomial, not an upper bound on the actual violation. Positive-time attainment additionally needs b>0 and a valid remainder interval containing b/(2c); initial slack must also be retained. No universal 1/g^2 percentage or guaranteed nonlocality from a nonzero residual is inferred.
- The original verify_cf2n.py uses nonportable checkpoint paths, conflates combined-battery failures with a CHSH-only summary, and has an all_fail initialization/bookkeeping defect. Those files remain unchanged for custody. The replacement replay computes its own counts and trusts neither checkpoint state nor a solver status.
- Candidate generation uses SciPy plus rational reconstruction and exact rejection checks. It is optional, separate from the release replay of stored certificates. No floating LP status, solver completeness, or Python implementation is certified by the Lean proofs.

The theorem inventory, claim map and manuscript now distinguish the written GHZ quantum realization, exact Python no-signalling checks, and the real optimization statements checked by Lean. The new finite-context proof constructs a local subdistribution instead of assuming the desired comparison or an optimal CF dual.

