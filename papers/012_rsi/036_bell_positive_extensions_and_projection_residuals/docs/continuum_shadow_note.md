# Finite Bell tables and selected continuum shadows

The finite construction does not require a continuous physical substrate. For
each integer k >= 2 it has k^2 settings per party, four outcomes per context,
a rational complete probability table, and finite signed-assignment weights.
The square roots used to normalize vectors cancel from the probability table.
The quantum realization uses finite matrices. None of these assertions requires
a differential equation, an infinite apparatus, or an observer outside the model.

There are three distinct mathematical operations here.

1. Finite calculation constructs each member and checks its certificates.
2. Quantification says that for every proposed finite coefficient C, some
   finite member violates CF <= C N_min. This is an all-size theorem, not an
   experiment at k=infinity.
3. Completion chooses a presentation, a notion of closeness, and a target
   query that respects that closeness. It is an additional mathematical
   construction. Different choices can retain different information.

The WDP presentation-completion criterion (Appendix O, PC-1) says more than
constancy on equality fibers: arbitrarily close presentations must force
arbitrarily close query values, uniformly on the actual image. Under this
condition a query factors through the presentation and extends uniquely to its
completion in a complete target. The CODA-CS-Q finite bridge supplies the
factorization and fiber-error boundary; CODA-CS describes the descended
shadow. These are representation statements, not evidence that a river
implements real numbers or calculus.

## A declared Archimedean presentation

Choose h=1/k with the usual real metric. This is an explicit choice, not a
consequence of the finite table alone. Write

s(h) = 1-h/3+h^3/3,
alpha(h) = 1-h/s(h),
beta(h) = (1-s(h))/s(h).

For h=1/k, the Bell certificates prove alpha <= CF <= 1 and
0 < N_min <= beta. Their ratio envelope is

alpha/beta = 3/h-4+3h/(1+h).

The pair (alpha,beta) extends at h=0 to (1,0). The actual optimization values
have the same scalar shadow by squeezing. An explicit cutoff is k>2/epsilon:
both |CF-1| and |N_min| are then less than epsilon. The ratio has no finite
real endpoint. An extended-real infinity symbol or a reciprocal coordinate
would change the target presentation; it would not add a new finite behavior.

These conclusions concern scalar summaries across a growing family.
They do not identify all the differently sized behavior tables with one fixed
Bell scenario, or create a limiting density operator in a fixed Hilbert space.
A limiting field of measurement settings would require a declared common
domain and a topology plus a separate convergence proof.

## What the local shadow forgets

The explicit local comparison L_k=s_k P_k+(1-s_k)W_k approaches P_k in every
cell: |P_k(a,b|x,y)-L_k(a,b|x,y)| <= (1-s_k)/4.
The per-context total-variation distance is at most (1-s_k)/2.
Yet CF(P_k) approaches one while CF(L_k)=0. Thus no modulus independent
of the scenario size can recover contextual fraction from this cellwise
accuracy alone. A witness aggregates a growing number of contexts.

This is the useful obstruction: the probability data can become uniformly
close to local tables in that chosen comparison while the global extension
query remains far apart. It illustrates why a query must satisfy the WDP
uniform-control premise before it descends to a completion. It is not a
claim that all continuum reasoning is invalid.

## Source custody and proof scope

The WDP references are the exact Git blobs from commit
762671d8cd1d61fbd30212d2bebb869aadc95850. The small source documents and their
hashes are preserved in source_inputs/wdp_continuum/ and
wdp_continuum_sources.json. The deleted WDP directory is not restored.
They are historical references, not replacement instructions.

The scalar finite cutoff and failure of a finite ratio endpoint are checked
in Bell.ContinuumShadows. The finite table construction and its optimizers
are connected separately by Bell.SmoothedFamily and
Bell.CompleteQuantumUnbounded. The cellwise local-shadow explanation above
is an algebraic written consequence of the explicit convex-mixture identity;
it is not presented as a formal theorem unless named in the axiom census.
