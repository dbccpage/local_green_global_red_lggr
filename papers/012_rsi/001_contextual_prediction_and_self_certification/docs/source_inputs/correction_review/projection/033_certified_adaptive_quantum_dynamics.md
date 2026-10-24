# Certified Adaptive Quantum Dynamics from Projection Residuals

**Subtitle:** Conditional analytic bounds and a cluster-product numerical prototype  
**Authors:** Jeremy H. Carroll & CODA Research Consortium  
**Date:** 2026-10-11  
**Version:** 1.0.1 (reviewed research preprint)  
**License:** CC-BY-4.0 (text and figures) / Apache-2.0 (code and Lean sources)

## Abstract

For a finite-dimensional quantum system with a completely positive, trace-preserving (CPTP) propagator, the error of a differentiable approximate density trajectory is bounded by the time integral of its actual dynamical defect, multiplied by the observable operator norm. We give a classical derivation including the initial-state mismatch term. For ideal product or cluster-product mean-field dynamics under a two-local Hamiltonian, that defect decomposes into boundary residuals computed on the full cluster factors. The product-marginal map has an idempotent differential on the trace-one slice; its normalized ambient extension preserves both partial traces. A polar witness certifies the trace norm of a residual, but does not in general certify a best tangent approximation.

The accompanying Python implementation samples these ideal tangent residuals while integrating approximate cluster dynamics and using a heuristic merge policy. It does not bound numerical integration or quadrature error, and it does not certify the requested tolerance. Reproduced comparisons cover open TFIM and XXZ chains with four or six qubits. The Lean sources establish conditional finite-sum inequalities over an abstract carrier with natural-number norm fields and integer pairings. They do not mechanize density matrices, continuous-time Duhamel analysis, or the numerical solver. The historical title is retained; the software status is `HEURISTIC_UNCERTIFIED`.

## 1. Introduction and relation to prior work

Variational dynamics replaces a large dynamical state space with a tractable family of approximate states. Product mean field, tensor networks, and parameterized circuits use different state families and tangent constructions. Their accuracy depends on how much of the exact generator lies outside the chosen tangent space, and on how accurately the projected equations are integrated.

A posteriori error analysis for variational quantum dynamics already exists. Martinazzo and Burghardt [1] study the local-in-time variational error and adaptive manifold enlargement; Zoufal, Sutter, and Woerner [2] derive error bounds for variational quantum time evolution. This work does not claim to introduce residual-based error control in general. Its contribution is a finite product/cluster-product formulation, an explicit distinction between marginal preservation and trace-norm optimality, and a small executable research package.

We use units with $\hbar=1$. Every Hilbert space is finite dimensional. $\|X\|_1$ denotes the Schatten trace norm and $\|O\|_\infty$ the operator norm. An analytic bound, a sampled numerical estimate, and a numerical reference comparison have different evidential roles throughout.

## 2. Product retractions and their differential

### 2.1 Domain and normalized ambient extension (PO033-C2)

For unit-trace density matrices on $A\otimes B$, define
$$
\Pi(\sigma)=\operatorname{Tr}_B(\sigma)\otimes\operatorname{Tr}_A(\sigma).
$$
On the trace-one affine slice, admissible first variations $Z$ are traceless. To discuss arbitrary ambient variations, use the extension
$$
\widehat\Pi(\sigma)=
\frac{\operatorname{Tr}_B(\sigma)\otimes\operatorname{Tr}_A(\sigma)}
{\operatorname{Tr}(\sigma)},\qquad \operatorname{Tr}(\sigma)\ne0.
$$
At $\rho=\rho_A\otimes\rho_B$, with both factors of unit trace, its differential is
$$
P_\rho Z=(\operatorname{Tr}_B Z)\otimes\rho_B
+\rho_A\otimes(\operatorname{Tr}_A Z)
-\operatorname{Tr}(Z)\rho.
$$
The unnormalized ambient map has a two-term differential instead. The three-term formula above agrees with that differential only on trace-zero inputs.

**Proposition 2.1.** $P_\rho$ preserves both partial traces, is idempotent, and has kernel
$$
\ker P_\rho=\{Z:\operatorname{Tr}_A Z=0,\ \operatorname{Tr}_B Z=0\}.
$$
Its image on traceless Hermitian inputs is the algebraic product tangent space
$$
\{X_A\otimes\rho_B+\rho_A\otimes X_B:
 X_A=X_A^\dagger,\ X_B=X_B^\dagger,\
 \operatorname{Tr}X_A=\operatorname{Tr}X_B=0\}.
$$
At full-rank factors this is the tangent space of the smooth normalized product-density manifold. At rank-deficient factors positivity imposes boundary constraints, so this algebraic space is not asserted to be the two-sided tangent space of all physical density curves.

*Proof.* Taking $\operatorname{Tr}_B$ of the three-term formula gives
$\operatorname{Tr}_B Z+\rho_A\operatorname{Tr}Z-\rho_A\operatorname{Tr}Z
=\operatorname{Tr}_B Z$; the other marginal is identical. These identities also preserve total trace. Applying the formula again therefore returns the same expression, proving idempotence. If $P_\rho Z=0$, marginal preservation forces both partial traces to vanish; the converse follows by substitution. On the traceless Hermitian slice the displayed formula has exactly the stated tangent form, and it fixes every vector of that form. $\square$

On the full ambient space $P_\rho\rho=\rho$. This trace-one scaling direction is not a normalized density tangent. Confusing these domains gives an incorrect image claim.

### 2.2 Marginal preservation and one-local isolation

A Hilbert--Schmidt orthogonal projection onto a product tangent space need not preserve reduced marginal derivatives. The retraction differential does preserve them. Particular states or directions can make the two projections coincide; no unqualified “unless maximally mixed” exclusion is used.

Let $Q_\rho=I-P_\rho$. For a one-local Hermitian term $h_A$,
$$
-i[h_A\otimes I,\rho_A\otimes\rho_B]
=(-i[h_A,\rho_A])\otimes\rho_B.
$$
The first factor is traceless, so Proposition 2.1 gives
$$
Q_\rho(-i[h_A\otimes I,\rho])=0.
$$
The same argument applies to $B$. A nonzero normal residual measures first-order departure from the product tangent description. It is not an if-and-only-if test for future correlations, and does not distinguish classical correlation from entanglement. A vanishing first derivative can coexist with higher-order departure.

### 2.3 Norm witnesses and the separate optimality condition (PO033-C3)

If $R=U\Sigma V^\dagger$ is a thin singular-value decomposition, $W=UV^\dagger$ satisfies
$$
\|W\|_\infty\le1,\qquad
\operatorname{Re}\operatorname{Tr}(W^\dagger R)=\|R\|_1.
$$
This gives a norm-duality witness, including for rectangular matrices. For a *best approximation* of $L$ in a real linear tangent space $\mathcal T$, a supporting witness must additionally annihilate that space:
$$
\operatorname{Re}\operatorname{Tr}(W^\dagger X)=0
\quad\text{for every }X\in\mathcal T.
$$
The polar witness returned by the package is not checked for this additional condition.

For example, take $\rho_A=\operatorname{diag}(0.8,0.2)$,
$\rho_B=\operatorname{diag}(0.7,0.3)$, and
$Z=\operatorname{diag}(1,0,0,-1)$. Then
$$
R=Z-P_\rho Z=\operatorname{diag}(-0.5,0.5,0.5,-0.5).
$$
For the tangent $X=\operatorname{diag}(1,-1)\otimes\rho_B$,
the polar witness has pairing $-0.8$ with $X$, and
$\|Z-(P_\rho Z-0.1X)\|_1=1.92<2=\|R\|_1$.
Thus this marginal-preserving projector is not generally a trace-norm best tangent approximation. The example is an executable regression.

### 2.4 Tensor-network scope

Pure product vectors are the bond-dimension-one corner of MPS. Mixed product density matrices and cluster-product density dynamics do not by themselves implement general MPS TDVP. Here `max_bond` is a ceiling on cluster size in **qubits**, not an MPS bond dimension. Extensions to other tensor-network, correlator-product, or neural-state tangent spaces require their own residual decomposition and integration analysis.

## 3. Conditional analytic observable bound

### 3.1 Duhamel estimate, including initial mismatch (PO033-C1)

Let $\dot\rho=\mathcal L\rho$ with a linear finite-dimensional generator whose forward propagator $\mathcal T_t$ is CPTP. Let $\widetilde\rho$ be a continuously differentiable density trajectory on $[0,T]$, and define its *actual* defect
$$
\mathcal R(t)=\mathcal L\widetilde\rho(t)-\dot{\widetilde\rho}(t),
\qquad \Delta(t)=\rho(t)-\widetilde\rho(t).
$$
Then $\dot\Delta=\mathcal L\Delta+\mathcal R$ and
$$
\Delta(t)=\mathcal T_t\Delta(0)+
\int_0^t\mathcal T_{t-s}\mathcal R(s)\,ds.
$$
For a Hermitian observable $O$, CPTP trace-norm contractivity on Hermitian inputs and Schatten duality imply
$$
\boxed{
|\operatorname{Tr}(O\Delta(t))|
\le \|O\|_\infty
\left(\|\Delta(0)\|_1+
\int_0^t\|\mathcal R(s)\|_1\,ds\right).
}
$$
Indeed, apply the triangle inequality to the Duhamel expression, contractivity to its Hermitian terms, and
$|\operatorname{Tr}(OX)|\le\|O\|_\infty\|X\|_1$.
This proof also applies to an absolutely continuous piecewise differentiable trajectory using its almost-everywhere actual defect.

For matching initial states the first term vanishes. Unitary propagators generated by $-i[H,\cdot]$ satisfy the assumptions. Finite-dimensional Lindblad propagators satisfy them too, but no Lindblad solver or dissipative local decomposition is implemented here. Time-dependent generators require the corresponding two-time propagator argument.

### 3.2 Product and cluster-product decomposition

For a two-local Hamiltonian and an ideal trajectory
$\widetilde\rho=\bigotimes_C\rho_C$ solving the self-consistent projected cluster equations, internal cluster terms are represented without a variational projection residual. On a boundary edge $e$ between clusters $A$ and $B$, embed its interaction as $h_e^{AB}$ on the **full** factors and set
$$
n_e=(I-P_{\rho_A\otimes\rho_B})
\bigl(-i[h_e^{AB},\rho_A\otimes\rho_B]\bigr),
\qquad \nu_e=\|n_e\|_1.
$$
The global embedded residual is $n_e\otimes\bigotimes_{C\ne A,B}\rho_C$,
with tensor factors permuted into site order. Summing these terms subtracts exactly the projected mean-field velocity from the full commutator. Because the remaining density factors have trace norm one,
$$
\|\mathcal R(s)\|_1\le\sum_{e\text{ boundary}}\nu_e(s).
$$
With matching initial states this yields the conditional analytic expression
$$
B_O(t)=\|O\|_\infty\int_0^t\sum_e\nu_e(s)\,ds.
$$
This spatial formula does not follow for an arbitrary correlated trajectory from products of its single-site marginals.

A concrete boundary example is a Bell state in cluster $\{0,1\}$, a maximally mixed qubit in cluster $\{2\}$, and interaction $Z_1Z_2$. Its single-site-marginal residual is zero, while its full cluster-factor residual has trace norm two. The repaired solver uses the latter construction after merging.

### 3.3 Short-time coefficient and observable cancellation (PO033-C5)

Write $r(t)=\sum_e\nu_e(t)$. If $r$ is continuous at zero, then
$$
\lim_{t\downarrow0}\frac{B_O(t)}{t}
=\|O\|_\infty r(0).
$$
Local Lipschitz regularity strengthens this to
$B_O(t)=\|O\|_\infty r(0)t+O(t^2)$.
These are classical integral statements. They do not imply that every observable error has this leading coefficient: for matching initial states, $O=I$ has identically zero error. Spatial cancellation and observable-specific cancellation can make the bound loose. The Lean `single_step_rate` theorem is a natural-number one-step identity, not this continuous limit.

### 3.4 Conditional total-correlation implication (PO033-C6)

This subsection retains the earlier correlation discussion with its missing premise made explicit. Let a finite simple interaction graph have maximum degree $\Delta\ge1$ and at least $aN$ edges. Suppose a fraction $\eta$ of its edges satisfies the independently established *exact evolved marginal* bound
$$
D_e(t):=\|\rho_e(t)-\rho_a(t)\otimes\rho_b(t)\|_1
\ge\nu t-Kt^2
$$
on a common interval, with $\nu>0$ and $K>0$. For base $b>1$ and
$0\le t\le\nu/(2K)$ within that interval,
$$
\frac{\operatorname{TC}_b(\rho(t))}{N}
\ge \frac{a\eta\nu^2}{8(2\Delta-1)\ln b}\,t^2.
$$

*Proof.* Greedily color the active-edge graph with at most $2\Delta-1$ colors: an edge meets at most $2\Delta-2$ previously colored edges. A largest color class is a matching of size at least $a\eta N/(2\Delta-1)$. Entropy subadditivity across that matching and the unused single sites gives
$\operatorname{TC}_b(\rho)\ge\sum_{e\text{ in matching}}I_b(a:b)$.
Quantum Pinsker gives $I_b(a:b)\ge D_e(t)^2/(2\ln b)$.
The assumed edge estimate yields $D_e(t)\ge\nu t/2$ on the stated interval. Substitute and sum. $\square$

No global $K=24g^2$ is derived here from a bound on one edge Hamiltonian: neighborhood terms and the actual remainder analysis must be accounted for. The edge estimate is a hypothesis, not a consequence of the code or Lean files. This implication bounds total correlation; it does not establish a bond-dimension lower bound or a numerical truncation rate.

## 4. Adaptive numerical prototype (PO033-C4)

### 4.1 Implemented event order

The state starts as a product of validated single-site density matrices. A full correlated initial density is rejected rather than silently replaced by its marginals, which would introduce an unaccounted initial error. Every solver interprets the initial state at the first sampling time, including translated grids.

At each requested time $t_k$ the adaptive implementation:

1. Advances the current partition to $t_k$ by frozen effective-Hamiltonian unitary substeps. All cluster Hamiltonians in a substep use the same incoming states.
2. Samples full cluster-factor boundary rates before refinement, denoted $r_k^-$.
3. Accumulates an interval estimate
   $\widehat I_k=\widehat I_{k-1}+\tfrac12(r_{k-1}^++r_k^-)(t_k-t_{k-1})$.
4. Uses $\|O\|_\infty[\widehat I_k+r_k^-(T-t_k)]$ and a local rate threshold to trigger at most one merge. Among positive-rate edges, it selects the largest feasible merge under the qubit ceiling.
5. Merges by a tensor product and site permutation, preserving the current global state. It recomputes all rates for the new partition, producing $r_k^+$, and records the state, rates, observables, and partition at the same time.

`cumulative_residual_estimates` stores $\widehat I_k$ and
`compute_cumulative_bounds` uses it. Reintegrating only post-merge rates can discard part of the preceding interval and is therefore inappropriate. A blocked strongest edge no longer prevents a weaker feasible merge. Periodic two-site models retain their two explicitly declared ordered bonds; each is counted once.

### 4.2 Certification boundary

The sampled $n_e$ measures the ideal self-consistent tangent field at the recorded state. The actual interpolated numerical velocity differs from that field during frozen substeps. The software does not bound this integration defect, quadrature error between output samples, floating-point error, or an initial mismatch accepted within input tolerance. Mean field uses RK4 with Hermiticity and trace corrections, not a positivity-preserving certified integrator. Numerical physicality must be checked for any selected run.

The sampled-bound utilities use an overflow-safe trapezoidal mean and raise
`NumericalRefusalError` when aggregation, integration or observable scaling
produces a nonfinite estimate. A refused streaming update preserves the last
accepted state. This is a numerical range check, not interval certification.
A positive reference error with a zero estimate is displayed as an infinite
error-to-estimate ratio, rather than a misleading zero ratio.

Thus $\widehat B_O=\|O\|_\infty\widehat I$ is a sampled estimate of the analytic expression, not a validated upper bound for the implemented trajectory. `estimated_target_met` reports only whether this estimate meets `tol`. The result status remains `HEURISTIC_UNCERTIFIED` whether that flag is true or false. A cluster ceiling, one merge per output sample, and a horizon extrapolation cannot enforce a requested tolerance.

Legacy names `CertificateTracker`, `certified_bounds`, and
`verify_bound_honesty` are retained for compatibility. The latter compares matching time grids against a dense floating-point reference; a nonnegative sampled margin is an observation, not a proof.

## 5. Reproduced numerical observations

The committed `review_observations.json` is generated by
`scripts/reproduce_review.py`. Reproduction uses open chains, output times
`np.linspace(0, 0.4, 9)`, and adaptive parameters
`tol=0.1, max_bond=4, refine_threshold=0.03`. TFIM has $J=h=1$ and polarized $+X$ initial state. XXZ has $J=\Delta=1$, $h=0.2$, and Néel initial state. The center $ZZ$ observable and normalized staggered magnetization both have norm one.

| Model | Observable | Method | Max reference error | Final sampled estimate |
|:--|:--|:--|--:|--:|
| TFIM, $N=4$ | Center $ZZ$ | Mean field | 0.418559 | 2.400000 |
| TFIM, $N=4$ | Center $ZZ$ | Adaptive | 0.072469 | 0.300000 |
| XXZ, $N=4$ | Staggered $Z$ | Mean field | 1.044816 | 4.800000 |
| XXZ, $N=4$ | Staggered $Z$ | Adaptive | 0.155356 | 0.596622 |
| TFIM, $N=6$ | Center $ZZ$ | Mean field | 0.418330 | 4.000000 |
| TFIM, $N=6$ | Center $ZZ$ | Adaptive | 0.139181 | 1.400000 |

All sampled margins in these six runs are nonnegative to $10^{-12}$; tiny negative initial values arise from reference roundoff. Every adaptive final estimate exceeds the requested 0.1 target. The observed improvements are fixture-specific and compare different parameter budgets. No Pareto-optimality, uniform improvement, $N=8$ benchmark, or formal certitude is asserted. The earlier unreproducible table and 24-fold reduction claim are replaced by these explicit observations.

The review also exercises the two-qubit all-$Z$-up TFIM on $[0,0.2]$ with a one-qubit ceiling. The repaired final sampled rate is approximately $0.299596$, its two-point integral estimate is $0.029960$, and the final reference $ZZ$ error is $0.00018447$. The previous implementation attached the initial zero rate to the final state and returned a zero estimate.

From the package root, with `code[dev,notebooks]` installed:

~~~bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/reproduce_review.py --check
python scripts/replay_notebook.py
python scripts/replay_notebook.py --from-notebook-dir
python verify_deposit.py --skip-lean
~~~

The explicit `--skip-lean` option reports a scoped check with Lean skipped. It is not a full formal verification result. The review environment and fresh test count are recorded in the review report and README.

## 6. Lean proof scope and audit provenance

The preserved Lean project contains an abstract `OperatorSpace` whose carrier is unspecified. Its norm fields return `Nat` and its pairing returns `Int`. Hölder and propagator contractivity are hypotheses supplied to `DiscreteTrajectory`; local residual domination is also assumed. Those properties are not proved for concrete quantum matrices.

| Module | Established statement in its declared model |
|:--|:--|
| `Core` | Definitions of an abstract carrier and hypothesis predicates |
| `Duhamel` | Finite pairing-sum bound under supplied Hölder and contractivity |
| `LocalDecomposition` | Finite local-rate bound under supplied residual domination |
| `ErrorBound` | Conditional tolerance implication and monotonicity under pointwise smaller rates |
| `ShortTimeRate` | One-step identities for sums of natural-number rates |
| `AxiomAudit` | Commands that print logical axiom dependencies |

There is no formal density-matrix model, continuous derivative or integral, proof that edge rates dominate the solver defect, or theorem that merging produces pointwise smaller future rates. Standard logical axiom dependencies do not enumerate mathematical hypotheses passed as parameters.

`lean4/axiom_report.txt` is retained as a historical report. The 2026-10-02
repair did not rerun Lean. On 2026-10-11, a fresh build with the pinned Lean
4.34.0 toolchain and all 11 audit declarations passed: nine use only
`propext` and `Quot.sound`, and two use no axioms. This checks the abstract
conditional statements above; it does not supply their physical hypotheses.
The reproduction commands are:

~~~bash
cd lean4
lake build
lake env lean CAQD/AxiomAudit.lean
~~~

The verifier performs both commands when Lean is not explicitly skipped, and rejects failed builds or `sorryAx`. See `lean4/README.md` for the precise scope and provenance.

## 7. Limits and next validation steps

The classical actual-defect bound is sound under its stated assumptions. It can be loose because it sums norms before integrating. For density trajectories it may be capped by the trivial observable bound $2\|O\|_\infty$. A residual integral need not grow linearly forever; its behavior depends on the rates. The finite dense reconstruction used here has exponential memory cost even if cluster propagation is smaller.

A numerically certified implementation would need a validated continuous trajectory or enclosure, rigorous control of its actual integration defect, conservative residual quadrature, and floating-point enclosures. It would also need to account for accepted initial mismatch. A refined scheduler could retry failed targets or report resource exhaustion, but scheduling alone would not supply these missing bounds.

The stable claim ledger separates the classical propositions, numerical observations, conditional discrete Lean statements, and open implementation work. Packaging checks establish byte integrity and reproducibility scope; they do not approve publication or mathematical correctness.

## References

1. R. Martinazzo and I. Burghardt, *Local-in-Time Error in Variational Quantum Dynamics*, Physical Review Letters **124**, 150601 (2020). [doi:10.1103/PhysRevLett.124.150601](https://doi.org/10.1103/PhysRevLett.124.150601); [arXiv:1907.00841](https://arxiv.org/abs/1907.00841).
2. C. Zoufal, D. Sutter, and S. Woerner, *Error Bounds for Variational Quantum Time Evolution*, Physical Review Applied **20**, 044059 (2023). [doi:10.1103/PhysRevApplied.20.044059](https://doi.org/10.1103/PhysRevApplied.20.044059); [arXiv:2108.00022](https://arxiv.org/abs/2108.00022).
3. J. Haegeman et al., *Time-Dependent Variational Principle for Matrix Product States*, Physical Review Letters **107**, 070601 (2011). [doi:10.1103/PhysRevLett.107.070601](https://doi.org/10.1103/PhysRevLett.107.070601).
4. CODA Research Consortium, *Finite Projection Obstruction and Retraction Calculus (PO-000)*, Research Atlas (2026). Mathematical background for the retraction and residual formulation. PO-033 applies the actual-defect estimate to ideal cluster-product trajectories; its sampled adaptive solver remains uncertified. The higher-product and scalar-cochain extension is PO-034, *Higher-Cell Product Retractions, Simplicial Cochains, and Finite Retraction Dynamics*. These relationships do not establish a quantum-to-cochain dynamics map.
