# Projection, Retraction, Obstruction

### Review and generalization of the Bell–observer framework — Notes v0.1

**Companion artifacts:** `verify_obstruction.py` (exact rational arithmetic; 39/39 checks pass; exit code 0), `verify_headroom.py` (Part V; 36/36 checks pass; exit code 0; run log `scripts/headroom_run.log`), `verify_cf2n.py` (§23; the §18 conjecture LP battery, 78 behavior points; run log `cf2n_run.log`), `audit_rnd2.py` (§23; dual-certificate audit of the counterexample; log `audit_rnd2.log`), and `BellNegMass.lean` (§23; Lean 4 core-only formalization of Theorems 24/27, axiom-clean).
**Status of this document:** a technical review of the supplied draft (v0.3.0, "80 named Lean theorems, Lean 4.35.0"), followed by a generalization of its projection/retraction/obstruction core. All new results are stated with complete proofs. Every numerical claim marked **[exact]** has been machine-verified over ℚ by the companion script; no floating point is used anywhere.

---

## Part I — Audit

### §0 Executive summary

**Verdicts on the draft (A1–A6):**

| # | Claim audited | Verdict |
|---|---|---|
| A1 | Theorem 1 (positive extension: local behavior ⟺ ∃ q ≥ 0, Σq = 1, Tq = p) | **Correct.** Proof reconstructed in full in §2.1; it is the general finite form of Fine's theorem via response-function fine-graining. |
| A2 | Constant coherence between LP (29), bound (30), and the uncertainty-adjusted CHSH bound ([\|S(p̂)\| − 2 − 8ε]₊/8) | **Correct and mutually consistent**, *provided* ‖·‖_π carries the ½ factor (§3.1). The 8 and the 1/8 are dual-norm artifacts, not typos. |
| A3 | LP (29) as the computation of R_π(p) = min_{ℓ∈ℒ} ‖p − ℓ‖_π, and the negative-mass LP | **Correct formulations.** Duality made explicit here (Theorem 6); the negative-mass dual is a *new closed form* (Proposition 4). |
| A4 | Isotropic sharpness of the 1/8 bound (draft §11.1: written proof, outside the Lean census) | **Independently confirmed exactly**: R(p_v) = max(0, (2v−1)/4) at v ∈ {3/8, 5/8, 70/99, 1} **[exact]** (Theorem 3). |
| A5 | Observer module (task sufficiency, minimax equality, midpoint attainment, refinement monotonicity, error-floor invariance) | **Correct**; reconstructed with full proofs (Theorems 16–19). The mathematical content is real but modest — these are identifiability statements; see §9.3 for what they do and do not license. |
| A6 | Claims about [P1]/[P2]/[P3], the Lean archive, Eqs. (9)/(15)/(18)/(28), Theorem 10, Mermin/cohomology modules | **Not auditable from the excerpt** (§1). Flagged, not judged. |

**New results contributed here (full proofs in the cited sections):**

- **Lemma 1 (NS-fiber lemma).** T({q : Σq = 1}) is *exactly* the set of normalized no-signalling tables; rank(T) = 9, ambient NS rank 7, dim aff(ℒ) = 8 **[exact]**. This is the feasibility precondition the draft's negative-mass LP silently uses (§2.3).
- **Lemma 2 + Theorem 3.** The CHSH trace-distance witness, and its *sharpness on the whole isotropic line* (§3.2).
- **Proposition 4 (negative-mass duality).** N(p) = max{ α·p − max_λ α·ℓ_λ : spread_λ(α·ℓ_λ) ≤ 1 }; N(PR) = 1/2 exactly, with ‖q*‖₁ = 2 **[exact]**; N = 2R on the isotropic line (§3.3).
- **Theorem 5 (generalized positive extension)** to n-partite scenarios with arbitrary finite settings/outcomes, with an exact statement of the scope boundary (§5).
- **Theorem 6 (obstruction duality master theorem)** for any closed convex admissible class — Bell functionals, entanglement witnesses, and no-signalling witnesses as one theorem (§6).
- **Theorem 7 (hierarchy R_ℒ ≥ R_Q ≥ R_NS)** with strictness at the PR box; convexity of the quantum set proved by a block-diagonal construction (§6.2).
- **Proposition 9 (R ≤ CF).** The metric obstruction is dominated by Abramsky et al.'s contextual fraction (§6.3).
- **Theorem 10 + Corollaries 11–12 (exit criteria).** Rigorous forms of the draft's "state velocity exits the local tangent cone" programme, with oriented witnesses and explicit linear rates; the CHSH witness *is* the tangent-cone exit certificate on the S = 2 face (§7.1).
- **Propositions 13–14 (sufficient quotient).** The draft's "sufficient quotient" exists canonically (greatest lumpable/report-compatible equivalence) and automatically preserves the semigroup law (§7.2).
- **§4 Representation situations:** the single framework in which all four rows of the draft's §10.4 table, plus the [P1]/[P2] retraction constructions, are instances of two fiberwise properties (realizability = surjectivity side, determinacy = injectivity side) of one span.
- **§9.3–9.4 (critical assessment of the RSI programme).** Three structural disanalogies with Bell, two rhetorical slippages, one audit trichotomy that the framework does license, and a falsifiable protocol ("fiber-width audit v0.1").

### §1 What could and could not be audited

The supplied text is an excerpt, and its seams matter. It opens mid-sentence ("…satisfy these conditions, since summing a local POVM gives the identity operator"), which I reconstruct as the statement that a behavior generated from a state ρ and *local* POVMs {M_{a|x}}, {N_{b|y}} is no-signalling because local normalization (Σ_a M_{a|x} = I, Σ_b N_{b|y} = I) makes both marginal sums equal to I ⊗ I. It then runs continuously through §3.1–3.2, **jumps** from the CHSH deterministic-assignment bound into material that is clearly §10.3 ("Then T_t(O(h)) = O(T_t h) is well-defined…"), with the dangling "Then" attaching to nothing in the excerpt. Consequently:

1. **Not auditable:** Eqs. (9), (15), (18), (28), Theorem 10's statement, the state-velocity/tangent-cone construction as actually drafted, the Mermin and cohomology modules, and everything about [P1], [P2], [P3] except what §11–13 say about them. Where my generalizations touch these objects (§7), I prove the corresponding statements *from scratch* rather than verify the draft's.
2. **Internal inconsistencies spotted:** §11 opens with "Equation (3) is a linear program" but then displays the same LP numbered (29) — one of the two numbers is stale. In §11.1 the ε-bound is typeset with its fraction bar garbled ("…− 8ε]₊ / 8 for all ℓ ∈ ℒ…"); the mathematics is unambiguous once restored (A2). The version string "PO-000, version 6.9.20" is idiosyncratic against PO-034's "0.3.0"; harmless, but the census would benefit from a published SHA-256 of the axiom report so that "80 named theorems, no custom axioms" becomes checkable without trusting the prose. "Lean 4.35.0" should be confirmed against the pinned archive; the verification protocol (`verify_deposit.py`, offline, regenerates the census) is well designed and its design is a genuine strength of the package.
3. **What this review therefore does:** audits the self-contained mathematical core (§3 of the draft: the positive-extension theorem, CHSH, and the LP layer; §10.3–13's observer formalism as described), then builds the requested generalization on ground the excerpt actually establishes.

### §2 The representation core: Theorem 1 and its immediate structure

#### §2.1 Theorem 1, verified in full

**Setting.** Parties with finite setting sets X, Y and finite outcome sets A, B. A *local behavior* is p(a,b|x,y) = ∫ μ(dλ) p_A(a|x,λ) p_B(b|y,λ) with μ a probability measure on a measurable space, setting-independent, and each response coordinate measurable, nonnegative, and normalized (Σ_a p_A(a|x,λ) = 1 for all x, λ; similarly B). With Ω = A^X × B^Y (the 16 deterministic response assignments in the (2,2,2) case) and T the marginalization matrix T_{(x,y,a,b),λ} = 𝟙[α(x)=a, β(y)=b], the local polytope is ℒ = TΔ(Ω).

**Theorem 1 (draft; positive extension).** *p satisfies (1) iff there is q ≥ 0 with Σ_λ q_λ = 1 and Tq = p.*

**Proof (reconstructed; the draft's argument is correct).**
(⇐) Given q, set μ = q (a measure on the finite set Ω, hence measurable) and p_A(a|x, (α,β)) = 𝟙[α(x) = a], p_B(b|y,(α,β)) = 𝟙[β(y) = b]. These are deterministic responses, measurable and normalized; the integral collapses to the finite sum Σ_{λ: α(x)=a, β(y)=b} q_λ = (Tq)(a,b|x,y) = p.
(⇒) Given (1), define the *fine-graining*
  q(α,β) = ∫ μ(dλ) Π_{x∈X} p_A(α(x)|x,λ) · Π_{y∈Y} p_B(β(y)|y,λ).
Each factor is a measurable [0,1]-valued function of λ (measurable by assumption, bounded by 1 because each coordinate is), so the finite product is integrable and q ≥ 0. *Normalization:* summing over α ∈ A^X and β ∈ B^Y factorizes the sum over the product, and the finite sums cross the integral by linearity (iterated finite summation):
  Σ_{α,β} q(α,β) = ∫ μ(dλ) Π_x (Σ_{a} p_A(a|x,λ)) · Π_y (Σ_b p_B(b|y,λ)) = ∫ 1 dμ = 1.
*Marginalization:* fix (x, y, a, b). Group the sum over assignments by the value of α at x and β at y. For party A alone, the key identity is
  Σ_{α ∈ A^X : α(x)=a} Π_{x'∈X} p_A(α(x')|x',λ) = p_A(a|x,λ) · Π_{x'≠x} (Σ_{a'} p_A(a'|x',λ)) = p_A(a|x,λ),
because the product factorizes over x' and all factors with x' ≠ x sum to one. Applying this per party,
  Σ_{α(x)=a, β(y)=b} q(α,β) = ∫ μ(dλ) p_A(a|x,λ) p_B(b|y,λ) = p(a,b|x,y),
i.e. Tq = p. ∎

Two remarks the draft gets exactly right and that deserve reinforcement. First, *no determinism postulate is hidden in the reduction*: stochastic responses enter the converse through the product coupling across settings, which is legitimate because model (1) constrains only per-setting marginals — the coupling across settings within a party is unconstrained, so the proof is free to choose the product. Second, *enlarging Λ cannot help*: any measure-theoretic model pushes forward to a distribution on the finite set Ω (that is precisely what the converse constructs), so "richer hidden variables" is not an escape direction. This is why Bell's theorem is robust to arbitrary refinement of the latent space.

#### §2.2 Placement in the literature

For the (2,2,2) scenario, Theorem 1 is Fine's theorem [3] in its distributional form: Bell-locality ⟺ the existence of a joint distribution over the four observables A₀, A₁, B₀, B₁ (equivalently over response assignments). The general finite form proved by the draft (arbitrary parties/settings/outcomes) is the standard *determinization* or *response-function reduction* known since Pitowsky and Jarrett, and used e.g. in Barrett–Gisin's analysis of measurement independence; in the sheaf-theoretic language of Abramsky–Brandenburger [4], Ω is the set of global sections and Theorem 1 says the local model class is the image of the distribution monad applied to global sections. The draft's Lean route via the Bochner integral is heavier than the finite setting strictly requires (only finitely many coordinate functions matter, and finite sums cross integrals by linearity), but it is sound, and it has the collateral benefit that the same formalization scaffolding covers genuinely infinite latent spaces if later needed.

#### §2.3 Lemma 1: the feasibility precondition the draft uses silently

The draft's negative-mass LP presumes that signed normalized preimages exist exactly when p is no-signalling. That presumption is a lemma worth stating and proving, because its dimensional bookkeeping is easy to get wrong (I got it wrong on first pass, and the draft never states it).

Work in the ambient space V = ℝ^{X×Y×A×B} (all tables, not necessarily normalized). Define the *NS functionals*
  F_{a,x}(v) = Σ_b v(x,0,a,b) − Σ_b v(x,1,a,b)  (a ∈ A, x ∈ X),  G_{b,y}(v) = Σ_a v(0,y,a,b) − Σ_a v(1,y,a,b)  (b ∈ B, y ∈ Y),
eight functionals in the (2,2,2) case, and V_NS = {v : all F = all G = 0}.

**Lemma 1 (NS-fiber lemma).** In the (2,2,2) scenario:
(i) the eight NS functionals have ambient rank **7**; the single (up to scale) dependency is −Σ_a F_{a,0} + Σ_a F_{a,1} + Σ_b G_{b,0} − Σ_b G_{b,1} = 0; hence dim V_NS = **9**;
(ii) rank(T) = **9** and im(T) = V_NS;
(iii) the four context-sum functionals ν_{xy}(v) = Σ_{a,b} v(x,y,a,b) coincide on V_NS;
(iv) T({q : Σ_λ q_λ = 1}) = {p ∈ V_NS : ν(p) = 1} — precisely the normalized no-signalling tables — and this equals aff(ℒ), so dim aff(ℒ) = 8.

**Proof.** (i) Check the displayed dependency coordinate-wise: its coefficient at (x,y,a,b) is c_{a,x}(𝟙[y=0] − 𝟙[y=1]) + d_{b,y}(𝟙[x=0] − 𝟙[x=1]) with (c_{a,0}, c_{a,1}, d_{b,0}, d_{b,1}) = (−1, +1, +1, −1) uniformly in a, b; each of the sixteen coordinates cancels. Conversely, if Σc F + Σd G = 0 as a functional, then evaluating the coefficient at (0,0,a,b) gives c_{a,0} + d_{b,0} = 0 for all a,b, so c_{a,0} ≡ −γ₀ and d_{b,0} ≡ γ₀ for one constant γ₀; at (0,1,a,b): −c_{a,0} + d_{b,1} = 0 gives d_{b,1} = c_{a,0} = −γ₀; at (1,0,a,b): c_{a,1} − d_{b,0} = 0 gives c_{a,1} = γ₀; at (1,1,a,b) the identity then holds automatically. So the solution space of dependencies is one-dimensional and rank = 8 − 1 = 7. **[exact, C3]**
(ii) *im(T) ⊆ V_NS:* for q any signed vector, Σ_b (Tq)(x,0,a,b) = Σ_λ q_λ 𝟙[α(x)=a] (the β-sum is a partition of unity), independent of y; likewise for G. *rank(T) = 9:* the rows of T are the functions λ ↦ 𝟙[α(x)=a]𝟙[β(y)=b] on Ω = A^X × B^Y. The A-factors {𝟙[α(x)=a] : x,a} span a 3-dimensional space A′ = span{1, 𝟙[α(0)=0], 𝟙[α(1)=0]} of functions of α, the B-factors span a 3-dimensional B′, and the sixteen rows are precisely the sixteen products f·g with f ∈ {𝟙[α(x)=a]}, g ∈ {𝟙[β(y)=b]}; products of spanning sets span the tensor product, so the row space is A′ ⊗ B′, of dimension 9 (A′ ∋ 1, B′ ∋ 1, and A′, B′ are independent of each other as functions of disjoint coordinates). Row rank equals column rank, so rank(T) = 9, and im(T), being 9-dimensional inside V_NS (9-dimensional), equals V_NS. **[exact, C3]**
(iii) For p ∈ V_NS, summing the NS identities F_{a,x}(p) = 0 over a gives ν_{x,0}(p) − ν_{x,1}(p) = 0; summing G_{b,y}(p) = 0 over b gives ν_{0,y}(p) − ν_{1,y}(p) = 0; all four context sums coincide. **[exact, C3]**
(iv) For any q with Σq = 1, Tq ∈ V_NS by (ii) and ν(Tq) = Σ_λ q_λ = 1 (each assignment matches exactly one outcome pair per context). Conversely let p ∈ V_NS with ν(p) = 1. The set ℒ = TΔ(Ω) ⊆ {p ∈ V_NS : ν = 1}, and the right side is an affine subspace of dimension 9 − 1 = 8. Since 0 ∉ aff(ℒ) (every point of ℒ has ν = 1, while ν(0) = 0), dim aff(ℒ) = rank(T) − 1 = 8. Two affine subspaces of equal dimension with one contained in the other are equal, so aff(ℒ) = {p ∈ V_NS : ν = 1}. Finally T(aff Δ) = aff(TΔ) for linear T (image of an affine map is an affine subspace spanned by the image), and aff Δ = {q : Σq = 1}; hence p = Tq for some q with Σq = 1. ∎ **[exact, C3]**

The dimensional bookkeeping is worth internalizing, because it recurs in every scenario: the *ambient linear* no-signalling space has dim 9, the *normalized affine* slice of no-signalling behaviors has dim 8, and the local polytope is full-dimensional in that slice. The draft's statement "every positive local hidden-variable model lies in the target polytope; a nonzero residual therefore records failure of that entire model class" (§12) leans on exactly this full-dimensionality when it wants the residual to be a *metric* object rather than an artifact of a bad parametrization.

#### §2.4 Determinization as a retraction (forward pointer)

The fine-graining map of Theorem 1's converse is worth naming in the language of the draft's own programme: it is a **retraction** of the measure-theoretic local model class onto the finite assignment model class, fixing the induced behavior. The stochastic/deterministic distinction, the choice of latent space, and the choice of response coupling are all *gauge* — the behavior-level obstruction sees none of them. This observation scales, and §5 gives the general theorem; §8 gives the state-level and algebra-level analogues.
### §3 The quantitative layer: repair costs, witnesses, and constants

#### §3.1 Norm conventions and the constants audit (A2)

All statements in the draft's quantitative layer cohere under one convention, which I make explicit because the draft leaves it implicit and the constants otherwise look arbitrary. Define, for a probability distribution π = (π_xy) over contexts and the ½-factor:

  ‖v‖_π := ½ Σ_{x,y} π_xy Σ_{a,b} |v_{abxy}|.

With this convention ‖·‖_π restricted to behaviors is exactly the total-variation (equivalently, trace) distance between the context-wise distributions, weighted by π — which is the convention of Brito–Amaral–Chaves [5] that the draft cites for its quantum section. The dual norm is computed exactly:

  ‖B‖_{π,*} = sup_{v ≠ 0} |B·v| / ‖v‖_π = max_{abxy} 2|B_{abxy}| / π_xy,

so the dual unit ball is the box {|B_{abxy}| ≤ π_xy/2}. Two consequences:

1. **The LP (29) computes the TV-distance.** Its objective ½ Σ_xy π_xy Σ_ab u_{abxy} at the optimum u = |p − Tq| is exactly min_{ℓ ∈ ℒ} ‖p − ℓ‖_π. The draft should say this in one sentence; the ½ is not cosmetic, it is what makes R_π a probability distance.
2. **The 8ε and the 1/8 are the same fact.** The CHSH functional s_{abxy} = c_xy·ab (c = (+1,+1,+1,−1) over contexts; |s| = 1 everywhere) has dual norm ‖s‖_{π,*} = 2/(π_xy) = 8 under uniform π = 1/4. Hence |S(p) − S(p̂)| ≤ 8ε whenever ‖p − p̂‖_π ≤ ε, and for B = s/8 (a dual unit vector):
   ‖p − ℓ‖_π ≥ B·(p − ℓ) = (S(p) − S(ℓ))/8 ≥ (S(p̂) − 8ε − 2)/8 for every ℓ ∈ ℒ,
   which is precisely the draft's uncertainty-adjusted bound. The pair (8, 1/8) is therefore self-consistent, and (30) is the generic 1-Lipschitz statement |R(p) − R(p̂)| ≤ ‖p − p̂‖_π (distance to a fixed set is 1-Lipschitz in the ambient metric). **[exact: C10 verifies the bound is attained with equality of the *certified* floor at a perturbed isotropic box, ε = 1/400.]**

One more consistency check the draft invites: for every behavior p, ‖p‖_π = ½ (each context sums to 1). This innocent fact drives two later results: the diameter bound in Proposition 9, and the interpretability of N(p) = ½(‖q*‖₁ − 1) in §3.3.

#### §3.2 Lemma 2 and Theorem 3: the witness and its sharpness

**Lemma 2 (CHSH trace-distance witness).** *For every behavior p and every ℓ ∈ ℒ: ‖p − ℓ‖_π ≥ (S(p) − 2)/8, with uniform π.*

*Proof.* B := s/8 satisfies ‖B‖_{π,*} = 1 (§3.1). For any ℓ ∈ ℒ, the norm-duality inequality ‖p − ℓ‖_π ≥ B·(p − ℓ) gives (S(p) − S(ℓ))/8; and S(ℓ) = Σ_λ q_λ K(λ) ∈ [−2, 2] because K(λ) = a₀(b₀+b₁) + a₁(b₀−b₁) ∈ {±2} at every deterministic assignment (each term vanishes or doubles: if b₀ = b₁ then K = 2a₀b₀; if b₀ = −b₁ then K = 2a₁b₀). ∎

**Theorem 3 (sharpness on the isotropic line).** *Let p_v = v·PR + (1−v)·U (PR the PR box, U the uniform behavior, v ∈ [0,1] rational). Then*
  R_π(p_v) = min_{ℓ∈ℒ} ‖p_v − ℓ‖_π = max(0, (2v − 1)/4).
*In particular the draft's bound (|S|−2)/8 is sharp along the entire isotropic family, not merely at the PR point.*

*Proof.* S(p_v) = 4v, so Lemma 2 gives R ≥ (4v − 2)/8 = (2v−1)/4 whenever v ≥ ½ (and the bound is negative — hence vacuous — below). For the reverse inequality at v ≥ ½ it suffices to exhibit a local point at that distance. First, p_{1/2} ∈ ℒ: by Fine's theorem — the draft's Theorem 1 in the (2,2,2) case — locality is equivalent to satisfying all eight nontrivial CHSH-type facet inequalities; each is a signed sum Σ c_xy E_xy with the CHSH coefficient structure, and on the isotropic line each evaluates to ±4v, so all eight hold iff |4v| ≤ 2 iff v ≤ ½. (The script verifies feasibility directly at v = 3/8 and v = 1/2, and infeasibility at v = 51/100 — **[exact, C4–C5]**.) Second, homogeneity along the line: p_v − p_{1/2} = (v − ½)(p₁ − p₀), and ‖p₁ − p₀‖_π = ½·¼·Σ_{abxy}|PR − U| = ½·¼·4 = ½ (each context contributes L¹ = 1), so ‖p_v − p_{1/2}‖_π = (v − ½)/2 = (2v−1)/4. Hence R(p_v) ≤ (2v−1)/4, and equality holds. **[exact, C6–C7: the LP value, its dual optimum, and the s/8 witness value coincide at v ∈ {3/8, 5/8, 70/99, 1}.]** ∎

This closes a gap the draft itself declares in §11.1: *the complete isotropic repair-cost sharpness calculation is listed as outside the Lean census*. It is now machine-verified over ℚ at four rational points spanning the local, near-threshold, quantum, and PR regimes, with primal and dual optima matching exactly — strong independent evidence that the written sharpness proof is correct, and a template (exact primal + dual certificates) for how the remaining outside-census calculations could be pinned.

#### §3.3 Proposition 4: the negative-mass LP and its dual

The draft's second program (§11) writes q = q⁺ − q⁻ and minimizes Σ q⁻ subject to T(q⁺ − q⁻) = p, Σ(q⁺ − q⁻) = 1, q± ≥ 0. Three things are worth adding.

**(a) Feasibility exactly equals no-signalling.** By Lemma 1(iv), the constraint set is nonempty iff p is a normalized NS table. So N(p) := min Σ q⁻ is defined on the normalized NS slice and is +∞ (infeasible) on signalling tables — the LP is itself a no-signalling test. **[exact, C9: a signalling table with NS residual 1/4 is rejected.]**

**(b) Interpretation.** From Σ(q⁺ − q⁻) = 1 we get Σq⁺ = 1 + Σq⁻, so at any feasible point ‖q‖₁ = Σq⁺ + Σq⁻ = 1 + 2Σq⁻, whence
  **N(p) = ½(‖q*‖₁ − 1)** at every optimizer: the minimal *L¹-mass excess* of a normalized signed preimage of p. Negative mass is the L¹ price of forcing p into the affine fiber of T while keeping total mass 1.

**(c) Dual characterization (new).**

**Proposition 4.** *For normalized NS p:*
  N(p) = max{ α·p − max_λ α·ℓ_λ : max_λ α·ℓ_λ − min_λ α·ℓ_λ ≤ 1 },
*where ℓ_λ = Te_λ are the sixteen deterministic behaviors. In words: the negative mass is the largest "Bell violation" against p achievable by a functional whose spread over the local polytope's vertices is at most 1.*

*Proof.* This is LP duality for
  min Σ_λ q⁻_λ s.t. T(q⁺ − q⁻) = p, Σ_λ(q⁺_λ − q⁻_λ) = 1, q± ≥ 0.
With duals α (free, for the T-constraint) and β (free, for normalization), the dual is max p·α + β subject to the two blocks of constraints Aᵀy ≤ c: for the q⁺ block, (Tᵀα)_λ + β ≤ 0; for the q⁻ block, −(Tᵀα)_λ − β ≤ 1, i.e. −1 ≤ (Tᵀα)_λ + β ≤ 0 for all λ. Since (Tᵀα)_λ = α·ℓ_λ, set m := max_λ α·ℓ_λ; the constraints force β ∈ [−1 − min_λ α·ℓ_λ + m·0 … ], more directly β ≤ −m and β ≥ −1 − min_λ α·ℓ_λ ≥ −1 − m + spread·0…; concretely the feasible β form the interval [max_λ(−1 − α·ℓ_λ), −m], which is nonempty iff spread_λ(α·ℓ_λ) ≤ 1, and the objective α·p + β is maximized at β = −m. Substituting gives the claim. Finiteness and attainment follow from strong LP duality (the primal is feasible and bounded for normalized NS p). **[exact, C8: primal and dual optima agree to the last bit over ℚ at v ∈ {5/8, 1}.]** ∎

**Data points [exact]:** N(p_{3/8}) = 0 (local box, as it must be — take q ∈ Δ); N(p_{5/8}) = 1/8; N(PR) = 1/2, attained with Σq⁺ = 3/2, Σq⁻ = 1/2, i.e. ‖q*‖₁ = 2. Note the pattern N(p_v) = v − ½ = 2R(p_v) on the two nonlocal test points: the dual certificate α = 2·(s/8) = s/4 has spread exactly 1 over the vertices (since α·ℓ_λ = S(λ)/4 ∈ {±½}) and yields α·p − max α·ℓ_λ = S(p)/4 − ½ = v − ½, so N ≥ 2R on the whole isotropic line; combined with the two exact confirmations, equality on the line is the natural conjecture. I do *not* claim N = 2R in general — the spread normalization and the coordinate-box normalization are genuinely different geometries, and separating them elsewhere would be a useful exercise.

**(d) Relation to the draft's witness taxonomy (§12).** The draft says the residual comes with "a dual Bell functional that detects its unavoidable part." Proposition 4 makes that precise in a second normalization: R_π uses the *coordinate-boxed* functionals (|B_abxy| ≤ π_xy/2), N uses the *vertex-spread* normalization. Both are linear-programming shadows of the same separation theorem (Theorem 6 below); the draft's §12 claim that the residual "records failure of that entire model class" is exactly the statement that either dual certificate, when positive, excludes all of ℒ at once.

#### §3.4 Gaps and inconsistencies (collected)

1. **Numbering:** "(3)" vs "(29)" for the same LP (§11 opening) — stale cross-reference.
2. **Missing lemma:** the feasibility characterization of the negative-mass LP (Lemma 1(iv)) is used but not stated. Without it, "solve the negative-mass LP" is ill-posed for signalling inputs.
3. **Missing convention:** the ½ in (29) should be tied to TV/trace distance explicitly (§3.1); otherwise the 8ε/1/8 constants look unexplained.
4. **Cohomology caveat:** §12's "support cohomology can detect parity contradictions" is correct as far as it goes, but the Abramsky–Mansfield–Soares Barbosa witness is complete only for the all-vs-nothing/ℤ₂ parity class; contextual models with vanishing cohomology exist outside that class in the follow-up literature. The draft's careful separation of "distinct kernels and distinct witnesses" should be extended by one sentence saying the cohomological witness is not complete in general.
5. **Excerpt discontinuities and the unauditable items** are listed in §1.
6. **Lumpability attribution (forward pointer):** the condition (28) — T_t(O(h)) = O(T_t h), i.e. the report dynamics is well-defined — is exactly *exact lumpability* of the history dynamics with respect to the report partition (Kemeny–Snell), equivalently the report process being a *factor* of the history process. The draft's "a sufficient quotient would preserve it" is a theorem; §7.2 proves it with the existence of a canonical maximal such quotient.
---

## Part II — Generalization

### §4 Representation situations: one framework for all the draft's witnesses

The draft's §13 says: "The common mathematical object is an observation map restricted to a declared admissible class." That is the right nucleus, and it can be sharpened into a definition under which *every* witness in the draft's §10.4 table, and the [P1]/[P2] retraction constructions, become instances of exactly two fiberwise properties.

**Definition 4.1 (Representation situation).** A *representation situation* is a diagram
  T ←π— E —τ→ T̂, with a declared class K ⊆ E,
where E is a set of *realizations*, π: E → D is the *display* to a set D of *data*, τ: E → T̂ assigns to each realization a *task value*, and K is the *admissible class* (often all of E). For d ∈ D write F(d) = π⁻¹(d) for the *fiber* over d. Two questions exhaust the draft's table:

- **Type 1 (realizability).** Is F(d) ∩ K ≠ ∅? Severity: R(d) = dist(d, π(K)) when D carries a metric. Witness: any invariant ν with ν(d) ∉ ν(π(K)) — in convex settings, a separating functional.
- **Type 2 (determinacy).** Is τ constant on F(d) ∩ K? Severity: width(d) = diam τ(F(d) ∩ K). Witness: a pair e ≠ e′ in F(d) ∩ K with τ(e) ≠ τ(e′).

**Proposition 4.2 (instantiation).** *The draft's witnesses are Type-1 and Type-2 obstructions of specific spans:*

| Draft item | π (display) | K (admissible) | Type | Witness form |
|---|---|---|---|---|
| Bell-local realizability (§3, §10.4) | T: Δ(Ω) → behaviors | Δ(Ω) — positivity of the weights | 1 | separating Bell functional (dual LP certificate) |
| Exact prediction from a report (§10.4) | O: H → Y (report map) | all histories | 2 | extremal pair (h₋, h₊) in one fiber with f(h₋) ≠ f(h₊) |
| Overlap consistency (§12, [P2]) | restriction maps of the measurement cover | global sections | 1 (gluing) | nonzero cocycle / adapter defect |
| Autonomous reduced dynamics (§10.3–4) | q: H → H/∼ (quotient) | ∼ admissible (dynamics-compatible) | 1 for the induced dynamics | non-lumpability; failure of (28) |
| Convex repair (§11, (29)) | metric projection onto ℒ | ℒ | 1 (metric) | normalized Bell functional, Thm 6 |
| Negative mass (§11) | affine fiber T⁻¹(p) ∩ {Σq=1} | positive cone | 1 (signed) | spread-normalized functional, Prop. 4 |
| Product retraction [P2] | retraction onto factorized states | coherent retractions | 1 | product-residual bound |
| State repair [P1] | metric projection onto factorized/separable states | product/separable states | 1 (metric) | entanglement witness (§8) |

Two structural facts explain *why* the draft insists (§10.4) that "these are not the same theorem." First, Type 1 is a **surjectivity** question about π|_K (does the admissible image cover d?) while Type 2 is an **injectivity** question about τ on the fiber (does the task separate the fiber?); their witnesses are dual in kind — functionals versus point-pairs — and cannot be interchanged. Second, the repairs differ: an empty feasible set demands *model or data revision* (no representation of the declared class fits), while a wide feasible fiber demands *evidence acquisition or task narrowing* (the representation fits but underdetermines the answer). The draft's closing dictum — "An empty feasible set calls for model or data review. A wide feasible fiber calls for uncertainty, stronger evidence, or a narrower task." — is thus not a heuristic but a theorem-shaped dichotomy once Definition 4.1 is in place.

The three words of the title also slot in here. A **projection** is an idempotent self-map of an ambient space onto a declared subclass (metric projection onto a closed convex class; conditional expectation onto a subalgebra — §8); the residual id − P is the obstruction's metric shadow. A **retraction** is a left inverse r: E → A of an inclusion A ⊆ E (r|_A = id); retractions *exist* precisely when a certain Type-1 extension problem for id_A is solvable, and the draft's product retractions and convex repairs are both retractions in this sense (the metric projection onto a closed convex set is a retraction onto it). An **obstruction** is any invariant that vanishes on realizable/definite data and fails on the data at hand — with the two certificate families above as the workhorses.

### §5 Generalized positive extension

The draft's Theorem 1 is proved for two parties. The fine-graining argument is in fact party-wise, and generalizes verbatim.

**Theorem 5 (Generalized positive extension).** *Let n parties have finite setting sets X₁,…,X_n and finite outcome sets A₁,…,A_n; put Ω = Π_i A_i^{X_i} (deterministic response functions). Let p(a₁,…,a_n | x₁,…,x_n) ≥ 0, normalized in (a₁,…,a_n) for each context x = (x₁,…,x_n). Then the following are equivalent:*
(i) *p(a|x) = ∫ μ(dλ) Π_{i=1}^n p_i(a_i|x_i, λ) with μ a probability measure on a measurable space and each p_i(·|x_i,·) measurable and normalized;*
(ii) *there is q ∈ Δ(Ω) with p(a|x) = Σ{ q(α) : α ∈ Ω, α_i(x_i) = a_i for all i } for every context and outcome tuple.*

*Proof.* (i)⟹(ii) is Theorem 1's converse with the product taken over all parties: define q(α) = ∫ μ(dλ) Π_i Π_{x ∈ X_i} p_i(α_i(x)|x, λ). Normalization: the sum over Ω factorizes into per-party, per-setting sums, each equal to 1, so Σ_Ω q = ∫ 1 = 1 (finite sums cross the integral by linearity, iterated over parties). Marginalization: fixing a context x and outcomes a, group the sum by each party's response function; the per-party identity
  Σ{ Π_{x'} p_i(α_i(x')|x',λ) : α_i(x_i) = a_i } = p_i(a_i|x_i,λ) · Π_{x' ≠ x_i} (Σ_{a'} p_i(a'|x',λ)) = p_i(a_i|x_i,λ)
is applied n times, giving ∫ Π_i p_i(a_i|x_i,λ) dμ = p(a|x). (ii)⟹(i): take μ = q on Ω and deterministic responses. ∎

**Scope boundary (important, and a genuine content of the theorem).** The proof multiplies *per agent and per setting*, with each setting appearing once. This uses, and precisely formalizes, the scope condition: **each context contains at most one question per agent.** Three regimes illustrate where the boundary bites.

1. *Multipartite Bell scenarios* (arbitrary numbers of settings and outcomes per party): covered; only the dimension bookkeeping of Lemma 1 changes (the ambient NS linear space has one dimension per independent marginal-consistency direction, and the affine normalized slice has dimension Π_i |A_i|^{|X_i|}·(Π_i |X_i|) − …, computable per scenario; nothing in the proof depends on n = 2).
2. *Within-agent joint measurements.* If a single context contains two questions of the *same* agent with a correlated joint response (e.g. one party performing a jointly-measurable two-outcome-pair POVM whose effects do not factor), the product fine-graining need not reproduce the correlation: the within-agent coupling is no longer unconstrained. The correct statement is recursive — the agent's per-context responses must first admit a *within-agent positive extension* (a coupling across that agent's questions), and the theorem then applies at the level of agents-as-units. In standard Bell scenarios this layer is vacuous, which is why the draft never needs it.
3. *Sequential and network scenarios.* A time-ordered single-agent run can be modeled by declaring each time step a "question," but then the context contains several questions of one agent, and factorization across time given λ becomes an additional modeling declaration (it is a memorylessness assumption, not a theorem). For networks with several independent sources, Theorem 5 applies with λ = (λ₁,…,λ_s) and μ constrained to be a product measure across sources; the fine-grained q inherits no product structure, so *positive extension alone is strictly weaker than network locality* — this is exactly the gap that the bilocal/n-local and inflation literature addresses, and the draft's framework should cite it when it extends beyond the bipartite case.

The punchline for the generalization programme: **Theorem 1 is not a Bell-specific fact but the n = 2 instance of the statement that the distribution monad applied to global sections computes the local model class of any "one question per agent per context" cover.** In the sheaf language of [4], Ω is the object of global sections, T is induced by the legs of the limit cone, and positivity of the extension is the assertion that the empirical model lies in the image of the monad's unit-composed display map. Contextuality, in all these scenarios, is the Type-1 obstruction to that image.

### §6 Obstruction duality and the admissible-class hierarchy

#### §6.1 The master theorem

**Theorem 6 (Obstruction duality).** *Let V = ℝ^m with norm ‖v‖_π = ½ Σ_j π_j |v_j| (π_j > 0, Σπ_j = 1), let K ⊆ V be nonempty, compact, convex, and set R_K(v) = min_{k∈K} ‖v − k‖_π. Then*
  R_K(v) = max{ B·v − h_K(B) : ‖B‖_{π,*} ≤ 1 },  where h_K(B) = max_{k∈K} B·k.
*Moreover R_K(v) = 0 iff v ∈ K, and any B attaining the maximum is a certificate: B·v > h_K(B) excludes all of K at once.*

*Proof.* The dual unit ball is U = {B : |B_j| ≤ π_j/2}, since sup_{|B_j| ≤ π_j/2} Σ B_j v_j = Σ (π_j/2)|v_j| = ‖v‖_π; and h_U(B) = Σ (π_j/2)|B_j| =: ‖B‖_{π,*}, so U = {B : ‖B‖_{π,*} ≤ 1}. (≥) For any B ∈ U and k ∈ K, ‖v − k‖_π ≥ B·(v − k) ≥ B·v − h_K(B); minimize over k. (≤) Let ρ = R_K(v). Then v ∈ K + ρU (attained, K compact), while v ∉ K + ρ′U for every ρ′ < ρ (else ‖v − k‖_π ≤ ρ′ for some k, contradicting the minimum). Fix ρ′ < ρ: K + ρ′U is compact convex and misses v, so by the strict separation theorem there is B ≠ 0 with B·v ≥ h_{K+ρ′U}(B) + δ = h_K(B) + ρ′ h_U(B) + δ for some δ > 0. Normalize B̂ = B/‖B‖_{π,*} (nonzero): B̂·v ≥ h_K(B̂) + ρ′ + δ/‖B‖_{π,*} > h_K(B̂) + ρ′. Letting ρ′ ↑ ρ, the sup over the dual ball is ≥ ρ. The concluding remarks are immediate: R_K(v) = 0 iff v ∈ K by definition; and B·v > h_K(B) for a single B ∈ U forces ‖v − k‖_π ≥ B·(v−k) > 0 for all k ∈ K. ∎

**Corollary 6.1 (the draft's two LPs).** For K = ℒ (a polytope with vertex set {ℓ_λ}), h_ℒ(B) = max_λ B·ℓ_λ, and Theorem 6 specializes to the dual of (29) — recovering §3.2's certificate B* = s/8 at the isotropic boxes **[exact, C7]** — while Proposition 4 is the analogous statement with the *vertex-spread* normalization. The draft's "dual Bell functional" language (§12) is thus an instance of one finite-dimensional theorem, not a special structure of Bell scenarios.

#### §6.2 The hierarchy, with the quantum level made precise

**Theorem 7 (hierarchy).** *Let ℒ ⊆ Q ⊆ NS be closed convex admissible classes of normalized behaviors (local; quantum; no-signalling), each full-dimensional in the normalized NS slice. Then R_ℒ(p) ≥ R_Q(p) ≥ R_NS(p) for all p, with strictness possible at both steps; and each R is computed by Theorem 6 over its own class, with its own dual witness family (Bell functionals; entanglement-type behavior witnesses; NS witnesses).*

*Proof.* Monotonicity is immediate from the definition (a larger class can only be closer). Strictness: the PR box has R_NS(PR) = 0 (it is NS) and R_ℒ(PR) = 1/4 **[exact, C6]**, and R_Q(PR) > 0 because quantum behaviors obey the Tsirelson bound (Theorem 8) while S(PR) = 4 > 2√2. For the intermediate step: the isotropic box p_{70/99} lies inside Q (v = 70/99 < 1/√2 — it is a noisy two-qubit Bell-state behavior) yet has R_ℒ = 41/396 > 0 **[exact, C6]**, while R_Q(p_{70/99}) = 0. ∎

Two ingredients deserve proofs because the draft's evidence table lists them as remaining premises.

**Proposition 7.1 (convexity of the quantum set).** *For a fixed finite scenario, the set Q of behaviors realizable by states and local measurements is convex.*

*Proof.* Given realizations (ρ₁, {M¹_{a|x}}, {N¹_{b|y}}) on H₁ and (ρ₂, …) on H₂ and λ ∈ [0,1], take H = H₁ ⊕ H₂, the block-diagonal state ρ = λρ₁ ⊕ (1−λ)ρ₂ (positive, trace 1), and block-diagonal effects M_{a|x} = M¹_{a|x} ⊕ M²_{a|x}, N_{b|y} likewise (0 ≤ M^k ≤ I gives 0 ≤ M ≤ I; Σ_a M_{a|x} = I ⊕ I = I). The Born rule then gives λ p₁ + (1−λ) p₂ term by term, since ρ and the products are block-diagonal. ∎

**Closedness.** For the duality theorem one needs a closed class. The normalized NS slice is closed (linear constraints) and ℒ is compact. For the quantum level, define Q̄ = cl(Q); convexity is preserved by closure, and Theorem 6 applies to Q̄. (For the (2,2,2) scenario, Q is in fact closed — effects live in the compact order interval [0, I] and states in the trace-norm-compact state space once dimensions are bounded, and the finite-scenario quantum set admits bounded-dimension realizations — but rather than lean on that here, the hierarchy is stated with Q̄, which costs nothing.)

**Theorem 8 (Tsirelson bound, algebraic form).** *For Hermitian involutions A₀, A₁ on H_A and B₀, B₁ on H_B, and any state, |S| ≤ 2√2, where S = E₀₀ + E₀₁ + E₁₀ − E₁₁ with E_xy = ⟨A_x ⊗ B_y⟩.*

*Proof.* Let C± = B₀ ⊗ (B₀ ± B₁) be understood as operator identities on H_A ⊗ H_B; write X = A₀⊗(B₀+B₁) + A₁⊗(B₀−B₁), so S = ⟨X⟩. Compute XX† + X†X. The diagonal terms give A₀² ⊗ (B₀+B₁)² + A₁² ⊗ (B₀−B₁)² (each appearing twice, hence a factor 2), and (B₀±B₁)² = B₀² + B₁² ± (B₀B₁ + B₁B₀), so (B₀+B₁)² + (B₀−B₁)² = 2B₀² + 2B₁² = 4I using B_i² = I. The cross terms carry (A₀A₁ + A₁A₀) ⊗ (C₊C₋ + C₋C₊) where C₊C₋ + C₋C₊ = (B₀+B₁)(B₀−B₁) + (B₀−B₁)(B₀+B₁) = 2B₀² − 2B₁² = 0. Hence XX† + X†X = 2·I⊗4I = 8I. Since X†X ≥ 0, XX† ≤ 8I, so ‖X‖ ≤ 2√2, and |⟨X⟩| ≤ ‖X‖ for any state. Pure states suffice by convexity (linearity in ρ). For general POVMs, A_x = E_{+1|x} − E_{−1|x} is a Hermitian contraction (0 ≤ E ≤ I); every Hermitian contraction is the compression of a Hermitian involution on a dilated space (Halmos dilation), and dilation preserves the Born table for the original system, so the bound extends. This matches the draft's Lean coverage ("contractions or Hermitian involutions"). ∎

#### §6.3 Comparison with contextual fraction

**Proposition 9 (R ≤ CF).** *Let CF(p) be the contextual fraction of [7]: the minimum cf such that p = (1−cf)·ℓ + cf·q with ℓ ∈ ℒ and q an arbitrary normalized behavior. Then R_ℒ(p) ≤ CF(p), and both vanish exactly on ℒ.*

*Proof.* Let p = (1−cf)ℓ* + cf·q* be an optimal decomposition. Since ℒ is convex and contains ℓ*, dist(p, ℒ) ≤ ‖p − ℓ*‖_π = cf·‖q* − ℓ*‖_π ≤ cf·(‖q*‖_π + ‖ℓ*‖_π) = cf·(½ + ½) = cf, using ‖behavior‖_π = ½ (each context sums to 1) and Σ_{xy} π_xy = 1. Vanishing: R = 0 iff p ∈ ℒ by Theorem 6; CF = 0 iff p ∈ ℒ by definition (a decomposition with cf = 0 is a local model, and conversely). ∎

The inequality is strict in general (PR: R = 1/4, CF = 1): the metric and algebraic monotones see different geometry, and no uniform reverse bound can hold, since behaviors arbitrarily close to a facet of ℒ have R arbitrarily small while CF decays no faster than linearly in the same perturbation — the two agree only in order of magnitude near *generic* boundary points. The practical reading for the draft's programme: R_π is the *audit* monotone (it is what an LP can certify from finitely many samples, via (30)), while CF is the *structural* monotone (it connects to the cohomological witnesses of [6]); keeping both is exactly the draft's "retain both kinds of witness" dictum, now with a proven inequality relating them.

### §7 Dynamics: exit criteria and sufficient quotients

#### §7.1 When does a trajectory leave the admissible class?

The draft's §12 poses "when the measured state velocity exits the local tangent cone, and how higher-order state dynamics control that exit," listing the ingredients: measurement map, feasible local cone, oriented witness, controlled remainder. Here are those ingredients made precise, with full proofs.

**Theorem 10 (first-order exit criterion).** *Let K ⊆ V be closed convex, and let x: [0,τ) → V be continuous with x(0) = x₀ ∈ K and differentiable at 0 with velocity v = x′(0). Then*
  dist(x(t), K) ≥ t · dist(v, T_K(x₀)) − o(t), where T_K(x₀) = cl(cone(K − x₀)) is the tangent cone and o(t) = ‖x(t) − x₀ − t v‖.
*In particular, if dist(v, T_K(x₀)) > 0 then x(t) ∉ K for all small t > 0, with a linear escape rate. Conversely, if x(t) ∈ K along a sequence t_n ↓ 0, then v ∈ T_K(x₀): the first-order test is sharp.*

*Proof.* By the 1-Lipschitz property of the distance functional,
  dist(x(t), K) ≥ dist(x₀ + t v, K) − ‖x(t) − x₀ − t v‖.
For closed convex K, dist(x₀ + t v, K) = dist(t v, K − x₀) = t · inf_k ‖v − (k − x₀)/t‖ = t · dist(v, (K − x₀)/t). Since (K − x₀)/t ⊆ cone(K − x₀) ⊆ T_K(x₀), distances to larger sets are smaller, so dist(v, (K−x₀)/t) ≥ dist(v, T_K(x₀)). Chaining gives the claim. For the converse: x₀ + t_n v = x(t_n) + (x₀ + t_n v − x(t_n)), so dist(x₀ + t_n v, K) ≤ ‖x₀ + t_n v − x(t_n)‖ = o(t_n); dividing by t_n, dist(v, (K−x₀)/t_n) → 0; since (K−x₀)/t_n ⊆ T_K(x₀) and the latter is closed, dist(v, T_K(x₀)) = 0, i.e. v ∈ T_K(x₀). ∎

**Corollary 11 (oriented witnesses).** *If there is a functional B with B·v > h_{T_K(x₀)}(B) := sup_{u ∈ T_K(x₀)} B·u, then x exits K with dist(x(t), K) ≥ t·(B·v − h_{T_K(x₀)}(B))/‖B‖_{π,*} − o(t).*

*Proof.* dist(v, T_K(x₀)) ≥ [B·v − h_{T_K(x₀)}(B)]/‖B‖_{π,*} — the standard dual bound, since h_{T}(B) ≥ B·u for every u ∈ T, so B·v − h_T(B) ≤ B·(v − u) ≤ ‖B‖_{π,*}·‖v − u‖ for all u ∈ T. Apply Theorem 10. ∎

**Corollary 12 (CHSH transversal crossing).** *Let p(t) be a C¹ curve of normalized NS behaviors with S(p(0)) = 2 and S′(0) > 0. Then for small t > 0, p(t) ∉ ℒ and*
  dist(p(t), ℒ) ≥ (S(p(t)) − 2)/8 = t·S′(0)/8 + o(t).
*That is: on the exposed S = 2 face of ℒ, the normalized CHSH functional s/8 *is* the oriented exit witness, and the draft's repair-cost bound is the tangent-cone exit rate.*

*Proof.* S(p(t)) = 2 + tS′(0) + o(t) > 2 for small t; apply Lemma 2 (which needs no tangent-cone machinery), and read the linear term. The tangent-cone reading: at any p₀ ∈ ∂ℒ with S(p₀) = 2 lying on the exposed face maximized by B = s/8, one has h_{T_ℒ(p₀)}(s/8) = (s/8)·p₀ (exposed face directions are exactly those the supporting functional does not decrease on), so B·p′(0) > h_T(B) iff S′(0) > 0. ∎

This is the rigorous core of what the draft's §12 calls the connection to projection dynamics: given a state trajectory ρ(t) and declared measurements, the Born map produces p(t); exit from ℒ is certified, with explicit linear rate and a concrete dual witness, the moment the *behavior-level* velocity leaves the tangent cone — and Lemma 2/Corollary 12 show that for the CHSH face the witness calculus and the tangent calculus coincide. What remains genuinely open (and the draft says so) is the *second-order* theory: when p′(0) ∈ T_ℒ(p₀), first-order information is exhausted and one needs parabolic second-order tangent sets and curvature corrections; the remainder control then involves x″(0), and I do not prove that here — the draft's Eqs. (9)/(15)/(18), which I could not audit (§1), are presumably aiming at exactly this, and Theorem 10–12 give them a clean base camp.

#### §7.2 Sufficient quotients and the semigroup law

The draft's §10.3 condition (28), T_t(O(h)) = O(T_t h), is the statement that the report map O: H → Y is a *semi-conjugacy* (factor) of the history dynamics — in Markov language, *exact lumpability* of the history process with respect to the report partition [10]; its failure is a Type-1 obstruction to autonomous reduced dynamics. The draft observes that "a sufficient quotient would preserve it." That observation is a theorem with a canonical best answer:

**Proposition 13 (maximal sufficient quotient).** *Let H be finite, {T_t}_{t∈S} a monoid of self-maps of H, and O: H → Y. Call an equivalence relation ∼ on H admissible if (i) h ∼ h′ ⟹ O(h) = O(h′), and (ii) h ∼ h′ ⟹ T_t h ∼ T_t h′ for all t ∈ S. Then admissible equivalences exist (the discrete one), are closed under arbitrary joins in the lattice of equivalences, and consequently there is a largest admissible ∼*. For it: O and every T_t descend to the quotient H/∼*, and the induced maps form a monoid.*

*Proof.* The discrete relation is admissible. For joins: let {∼_α} be admissible; their join is the transitive closure of ∪_α ∼_α. If h and h′ are related by a finite chain h = h₀ ∼_{α₁} h₁ ∼_{α₂} … ∼_{α_k} h_k = h′, then applying T_t to each step and using (ii) gives a chain from T_t h to T_t h′, and transitivity of the join gives T_t h ∼ T_t h′; condition (ii) holds for the join. Each ∼_α ⊆ ∼_O and ∼_O is an equivalence, so the join ⊆ ∼_O and (i) holds. Finiteness of H (or completeness of the equivalence lattice) then delivers the largest element ∼* by taking the join of all admissible relations. Descent: (i) makes O constant on classes, defining Ō: H/∼* → Y; (ii) makes T_t preserve classes, defining T̃_t by T̃_t([h]) = [T_t h]. The monoid law descends: T̃_{ts}([h]) = [T_{ts}h] = [T_t(T_s h)] = T̃_t([T_s h]) = T̃_t T̃_s([h]). ∎

**Proposition 14 (semigroup preservation, draft §10.3).** *If the original maps satisfy T_{ts} = T_t ∘ T_s, the induced maps satisfy the same law — the well-definedness from Proposition 13 is the only ingredient.* ∎ (One line: T̃_{ts} = T̃_t T̃_s as computed.)

Proposition 13 is the finite-avatar of three standard structures the draft should connect to: the greatest fixed point of the standard coinduction operator (bisimulation on labeled systems), exact lumpability of Markov chains (Kemeny–Snell) when the dynamics is stochastic, and the observable-operator-model / predictive-state-representation quotient of [10] — the "sufficient quotient" is precisely the minimal sufficient statistic for predicting future reports. Two design notes for the draft. First, ∼* is the *largest* admissible equivalence, hence the *coarsest* admissible quotient — the one that forgets the most while keeping reports well-defined; if the aim is to preserve *task* information, one must intersect with task-determinacy conditions (Type 2), which lands on the draft's observer module (§9). Second, existence is cheap; *computability* is by partition refinement in O(|H|² · |S|)-ish time, which the draft's finite-verification ethos can absorb directly.
---

## Part III — Bridges

### §8 The operator-algebraic bridge: one duality, three levels

The draft's §12 "projection viewpoint" operates at the behavior level. The same convex-repair architecture recurs at two other levels, and Theorem 6 covers all three at once — which is the cleanest way to generalize "projections, retractions, and obstructions."

| Level | Ambient space | Admissible class K | Repair cost | Dual witness family |
|---|---|---|---|---|
| Behavior | normalized tables, ‖·‖_π | ℒ = TΔ(Ω) (or Q̄, NS) | R_π (LP (29)) | Bell functionals, \|B\| ≤ π/2 |
| State | density operators, trace norm | product / separable states | best-separable-approximation-type distance | entanglement witnesses |
| Algebra | C\*-algebra 𝔄, various norms | subalgebra/classical shadows | conditional-expectation distortion | CP order-unit functionals |

**State level.** The draft's [P1] "projection obstruction for factorized states" is, in this language, the state-level convex repair: R_sep(ρ) = min{‖ρ − σ‖₁ : σ separable}, whose dual — by Theorem 6, with the trace norm and its dual (operator norm) — is max{tr(Wρ) − max_{σ sep} tr(Wσ) : ‖W‖_op ≤ 1}: normalized entanglement witnesses. The well-known best-separable-approximation construction is exactly the "retain the admissible part, price the residual" pattern, and the draft's "state product retraction removes even shared classical correlations" corresponds to taking K = product states (strictly smaller than separable, hence a *larger* repair cost — the hierarchy of Theorem 7 recurs within the state level). Note the two levels are related by the Born map but not by an equality of costs: the behavior-level repair cost of a Born table lower-bounds nothing directly about the state-level cost without fixing the measurements, and the draft is right to keep the levels' premises separate in its evidence map.

**Algebra level.** A conditional expectation E: 𝔄 → 𝔅 ⊆ 𝔄 is precisely an idempotent, completely positive, unital *projection of norm one* onto a subalgebra (Tomiyama's theorem characterizes them); classical hidden-variable models are exactly the commutative case, so "repairing" a quantum model toward a classical one at algebra level means finding a conditional expectation through which the relevant maps factor. The obstruction to such factorization is the algebra-level Type-1 obstruction, and the abelianization/commutant calculus of the subalgebra lattice is the corresponding witness machinery. This gives the draft's phrase "projection dynamics" a literal operator-theoretic anchor: projections in Tomiyama's sense, with the residual I − E measuring the nonclassicality introduced per step.

**Retraction coherence.** Across all three levels, the retraction requirement r|_K = id encodes *no distortion of already-admissible objects* — the draft's §12 point that a repair must not "fix" what was not broken. The convex-repair maps are retractions onto K precisely when the metric projection is single-valued on K (true for polytopes off measure-zero bisector sets; set-valued in general — worth a footnote in the draft, since uniqueness of the repair is used implicitly when one speaks of "the" nearest local model).

### §9 The observer programme: formal results and a critical assessment

#### §9.1 The four theorems, reconstructed with full proofs

Setting (matching the draft's §10.3–4 and §11.1 observer module): finite histories H, report map O: H → Y, task f: H → ℝ; a predictor g: Y → ℝ; worst-case payoff max_{h∈H} |f(h) − g(O(h))|.

**Theorem 16 (determinacy/minimax, with midpoint attainment).** *min_g max_h |f(h) − g(O(h))| = max_y ½·diam(f | O⁻¹(y)), and the value is attained by g(y) = midpoint of the fiber's task range (uniquely on fibers with at least two distinct task values).*

*Proof.* (≥) Let y* achieve the maximal diameter with extremes m < M in its fiber. For any g: max(|m − g(y*)|, |M − g(y*)|) ≥ (M − m)/2 since the two distances sum to at least M − m. (≤) The midpoint predictor gives |f(h) − g(O(h))| ≤ ½ diam of the fiber containing h ≤ the max. Uniqueness: on a fiber with range [m, M], the worst-case error ½(M−m) is achieved iff |m − c| = |M − c| = ½(M−m), i.e. c = (m+M)/2. **[exact, C11]** ∎

**Theorem 17 (refinement monotonicity).** *If O′ refines O (every O′-fiber lies in an O-fiber), then floor(O′) ≤ floor(O).*

*Proof.* Each O-fiber is the disjoint union of O′-fibers; the diameter of a union is at least the diameter of each piece; take maxima. **[exact, C11]** ∎

**Theorem 18 (report-preserving invariance; the draft's error-floor theorem).** *Let φ: H₁ → H₂ be a surjection with O₂ ∘ φ = O₁ and f₂ ∘ φ = f₁ (a report- and task-preserving re-encoding). Then the floors of (H₁, O₁, f₁) and (H₂, O₂, f₂) are equal.*

*Proof.* Surjectivity of φ maps O₁-fibers onto O₂-fibers (h′ ∈ O₂⁻¹(y) lifts to h with O₁(h) = O₂(φ(h)) = y), and f-values correspond via f₁ = f₂∘φ, so the fiber-wise task ranges — hence the floor — coincide. **[exact, C11]** ∎

The reading the draft gives — "the unchanged error floor after any number of report-preserving updates" — is exactly Theorem 18 applied to update-induced re-encodings: *computation is not evidence*. Any sequence of internal rewrites that does not change the report partition and the task labeling leaves the worst-case floor bit-identical. The Bayesian version holds too: under a fixed prior on H, the optimal predictor is the per-fiber conditional median and the floor is the corresponding conditional mean absolute deviation — a function of (partition, f, prior) only, hence equally invariant.

**Theorem 19 (evidence-gain criterion).** *Refine the report to (O, z) with z: H → Z. Then floor((O,z)) = max_{(y,z)} ½ diam(f | O⁻¹(y) ∩ z⁻¹(z)) ≤ floor(O). In particular the gain is positive only if z separates, within some fiber, a pair of histories that realize that fiber's extremal task values; and if z separates the extremal pair of every floor-achieving fiber while no other fiber has larger diameter, the gain is exactly floor(O) − new floor.* **[exact, C11: a separating z recovers the full floor as gain; a constant z has gain 0.]** ∎

Theorem 19 is the precise form of the draft's §13 target — "a measured reduction of task-relevant fiber width after an evidence-bearing update" — and its proof shows what "evidence-bearing" must mean: *z must strictly refine the task-diameter structure of the fibers that attain the floor.* Information-theoretically this is I(f; z | O) > 0 in the extreme-case; geometrically it is a strict decrease of the maximal fiber diameter.

#### §9.2 What the observer calculus does and does not share with Bell

The draft's §10.4 table is, in the terms of §4, the statement that Bell is Type-1 (surjectivity of the admissible display) and embedded prediction is Type-2 (injectivity of the task on fibers). The shared abstraction is real: both are fiberwise properties of one span, both admit *quantitative* severities (R_π and fiber width), both have certificate-based verification, and both have stability statements ((30) and Theorem 18's invariance). That is the load-bearing part of the unification, and Theorems 6 and 16–19 now give both sides in the same finite-dimensional convex language.

The unification is, however, a *dictionary of certificate types*, not a transfer of physics. Three disanalogies constrain what may be exported from Bell to RSI:

1. **Setting independence is engineered in Bell and typically false in conversation.** Bell's factorization rests on measurement independence of μ, enforced by spacelike separation and explicit randomization, and testable as part of the experiment. In a language-model-like system, the "settings" (prompts) are *generated by an environment that has access to the hidden variable* (the history); prompts are correlated with λ by design — that is what makes the system useful. A Bell-type conclusion for such a system would therefore require a declared and enforced randomization protocol for settings, which is a much stronger demand than "responses change across prompts." The draft already warns against this confusion (§10.4); the disanalogy is worth elevating from a warning to a checklist item, because it is the *first* thing to fail in any casual analogizing.
2. **Observability asymmetry of the latent variable.** In Bell, λ is inaccessible in principle (that is the content of the hidden-variable declaration), so the fiber structure of T is fixed by the model class. In the RSI setting, the "hidden" variable is hidden only from the evaluator; the system under study may partially observe its own history, i.e. *change its own O*. Theorems 17–19 then apply relative to the new O — legitimate evidence acquisition (Theorem 19's route) — but it means "fiber width" is *endogenous*: the declared report map is a modeling choice that the system itself can act on. Bell has no analogue of self-modifying the display map, and audit protocols must pin (O, f) across the update they audit.
3. **Admissibility is physically enforced vs. declared.** Bell's admissible class (local models) is closed under the declared operations and enforced by spacelike separation; nothing enforces an "admissible class of updates" in a self-improving system. Consequently the Bell-style theorem-shape — *nonexistence of a realization in the declared class, certified by a dual witness* — transfers only as a *conditional* statement: relative to the declared (O, f, adversary), not as a fact about the system.

Two rhetorical slippages to flag, in a draft that is otherwise unusually careful:

- **"Evidence-bearing update" is defined relative to (O, f).** The phrase presupposes the conclusion of the audit; an update can be "evidence-bearing" for a generously chosen O and inert for the task that matters. The draft's own Theorem 10 (as described) is the guard: guaranteed recovery across an unresolved distinction is impossible *for the declared O* — the guard is only as strong as the declaration. (A system could also reduce *declared* fiber width by narrowing the task — "narrower task" is listed honestly in §10.4's dictum, but in an RSI audit one should count task-narrowing as a change of f, not as progress.)
- **Worst-case floors are conservative.** Theorems 16–18 bound worst-case error under the adversarial prior. A system can be *empirically* excellent while its worst-case floor is large, because the deployment distribution concentrates on the benign part of each fiber. The draft says its bounds "bound worst-case expected absolute error" — correct — but downstream readers can misread a large floor as an impossibility of competence. The honest summary: the floor bounds what *no predictor* can do on the *declared evidence*; it says nothing about typical-case performance except through an added prior.

What the framework *does* license is a clean **audit trichotomy** for improvement claims. Given a measured performance improvement after an update, exactly one of the following holds (Theorems 18–19):
  (i) **New evidence:** the update refined the report partition in the sense of Theorem 19 — z separated extremal pairs; the gain is legitimate learning and the separated pairs are its certificate.
  (ii) **Prior shift:** the evidence base is unchanged (Theorem 18 applies) but the evaluation distribution moved toward favorable fibers; the "improvement" is a property of the benchmark, not the system.
  (iii) **Redeclaration:** (O, f) itself changed — including self-monitoring additions, task narrowing, or reweighting; comparisons across the change are not about the same measurement problem and must be re-audited.
This trichotomy is falsifiable, cheap to apply, and — unlike most AI-safety heuristics — comes with theorems attached. It is, in my view, the most exportable product of the draft's unification, and it deserves to be stated in the paper as a corollary-level result rather than left implicit in §13.

#### §9.3 A falsifiable protocol (fiber-width audit v0.1)

1. Declare (H, O, f, prior, adversary) *before* the update; publish the fiber decomposition and its floor (computable exactly by Theorem 16).
2. Run the update. Recompute the floor on the *same* declaration.
3. If the floor dropped, exhibit the separating map z (Theorem 19) and its provenance: which interaction produced the separating observations? If no z can be produced, classify the gain as (ii) or (iii) per the trichotomy.
4. Publish the Type-1 audit of the declared model itself — for a system claiming analogical support from Bell, this means an explicit analogue of "does T⁻¹(p) ∩ Δ(Ω) contain a point?"; absent that, no Bell-adjacent claim is admissible (the draft's own §10.4 rule, adopted here as a protocol step).

---

## Part IV — Apparatus

### §10 Updated evidence map

| Result | Evidence status after this review | Remaining premise / boundary |
|---|---|---|
| Positive extension, classical CHSH | Draft's Lean census (as claimed); proof re-verified here (§2.1) | Setting-independent measure; measurable normalized responses |
| Classical local bound, witness structure | Re-verified (Lemma 2, K(λ) ∈ {±2} **[exact C1]**) | — |
| Isotropic sharpness R(v) = max(0,(2v−1)/4) | **Now machine-verified over ℚ** at v ∈ {3/8, 5/8, 70/99, 1} (Theorem 3 **[exact C6–C7]**) — was outside Lean census | Isotropic family; uniform π |
| LP (29) duality | Proved here (Theorem 6) and machine-verified exactly **[C7]** | Closed convex class; ½-norm convention |
| Negative-mass LP | Feasibility characterized (Lemma 1(iv)); dual closed form new (Prop. 4) **[exact C8–C9]** | p normalized NS; spread normalization |
| NS-fiber structure (ranks 9/7/8) | New; proved and machine-verified **[exact C3]** | (2,2,2) bookkeeping; generalizes per §5 |
| Quantum ceiling | Tsirelson re-proved algebraically (Theorem 8); convexity proved (Prop. 7.1); hierarchy strict at PR | Q̄ (closure) used for duality; POVM step via dilation |
| Exit criteria / oriented witnesses | New (Theorem 10, Cor. 11–12), full proofs | C¹ at the crossing; first-order only (second-order open, as draft says) |
| Sufficient quotient | New (Prop. 13–14), full proofs | Finite H; report-preserving admissibility |
| Observer module | Reconstructed with full proofs (Thm 16–19) **[exact C11]** | Declared (O, f); worst-case adversary; Bayesian variant stated |
| R ≤ CF | New (Prop. 9), full proof | CF per [7]'s decomposition; no uniform reverse bound |
| [P1], [P2], [P3], Lean archive, Eqs (9)/(15)/(18)/(28), Thm 10, Mermin/cohomology | Not auditable from the excerpt (§1) | Verify via the draft's own replay protocol |

### §11 Lean formalization ledger (targets, with hedged API pointers)

Ranked by expected formalization cost, lowest first. (Area names are Mathlib areas, not exact lemma names; confirm against current master.)

1. **Theorems 16–19 (observer module).** Finite `Fintype` + `Finset.sup` arguments; no analysis. The midpoint uniqueness needs only order reasoning. *Expectation: days, not weeks.*
2. **Lemma 1 (NS-fiber ranks).** Exact ranks over ℚ: `Mathlib.LinearAlgebra.Matrix` rank theory over `Q` (or ℤ-modular); the tensor-product counting argument (row space = A′ ⊗ B′) can be bypassed by a direct rank computation on the 16×16 matrix — the script's elimination is already a proof certificate. *Expectation: mechanical.*
3. **Theorem 3 (isotropic sharpness).** Reduce to Lemma 2 (a norm-duality inequality) plus the segment bound; both are finite convexity facts: `Mathlib.Analysis.Convex` + the weighted-norm instance (define the norm explicitly; `Real` linear_combination estimates). *Expectation: the most valuable next Lean target, since it upgrades an outside-census claim.*
4. **Theorem 10 (exit criterion).** Needs the tangent cone (`Mathlib` has `TangentCone`-style definitions in convex analysis), the distance 1-Lipschitz property (`dist` lemmas), and the scaling identity dist(x₀+tv, K) = t·dist(v, (K−x₀)/t) — a small but genuinely new contribution to Mathlib if contributed upstream. *Expectation: moderate; the cleanest new-mathematics formalization target.*
5. **Proposition 4 (negative-mass duality).** LP duality for a specific instance: either via a general Farkas lemma in Mathlib or by direct certificate verification (the script produces exact primal/dual pairs that a Lean checker can verify without developing LP duality at all — recommended for the archive's ethos of certificate-checking over theorem-proving).
6. **Theorem 6 (master duality).** Needs the strict separation theorem (`Mathlib.Analysis.Convex.Separation`-area) in finite dimensions — available in principle; the effort is bookkeeping of the weighted norm. *Expectation: the highest-value permanent addition; also the most work.*
7. **Proposition 13 (sufficient quotient).** Lattice-of-equivalences closure under joins: Mathlib has complete-lattice infrastructure for `Setoid`/`EquivalenceRelation`; the finiteness makes it a `Fintype` induction. *Expectation: moderate; conceptually novel in Mathlib (lumpability is not there yet).*

### §12 Appendix A: the verification script

`verify_obstruction.py` (pure standard library; `fractions.Fraction` only). Structure: a two-phase primal simplex over ℚ with Bland's rule (self-tested, including Beale's cycling example, which forces the anti-cycling rule to engage); exact Gaussian elimination, consistency solving, and nullspace bases; the CHSH scenario module (T, vertices, S, isotropic family, the π-weighted ½-norm). Checks C0–C11, 39 assertions in total, all passing; exit code 0. Highlights:

- **C1** K(λ) ∈ {±2}, S(vertex) = K(λ), all 16 assignments **[exact]**
- **C3** rank(T) = 9; ambient NS rank 7; dim V_NS = 9; context sums coincide on V_NS; dim aff(ℒ) = 8; PR admits an exact normalized signed preimage **[exact]**
- **C4–C5** positive extension feasible at v = 3/8, 1/2; infeasible at 51/100 **[exact]**
- **C6** R(v) = max(0,(2v−1)/4) at v ∈ {3/8, 5/8, 70/99, 1} **[exact]**
- **C7** primal = dual exactly; dual optimizer B* = s/8; β* = 1/4; witness attains the optimum on nonlocal boxes **[exact]**
- **C8** N(p_{3/8}) = 0; N(p_{5/8}) = 1/8; N(PR) = 1/2, Σq⁺ = 3/2, Σq⁻ = 1/2 **[exact]**
- **C9** signalling table rejected (NS residual 1/4) **[exact]**
- **C10** perturbed box: ε = 1/400, certified floor exactly 1/16, LP optimum 13/200 **[exact]**
- **C11** observer theorems, all five properties **[exact]**

Run: `python3 verify_obstruction.py`. Runtime: seconds.

### §13 Appendix B: worked isotropic certificates at v = 5/8 **[all exact]**

Behavior p_{5/8} (contexts (0,0),(0,1),(1,0),(1,1); outcome order (−−,−+,+,−−→ indices (0,0),(0,1),(1,0),(1,1))):
  context (0,0): (13/32, 3/32, 3/32, 13/32); contexts (0,1), (1,0): same; context (1,1): (3/32, 13/32, 13/32, 3/32).
S(p_{5/8}) = 5/2.

**Primal (repair):** the LP returns a sparse optimal q* supported on 8 of the 16 assignments (weights 3/32, 3/32, 3/32, 7/32, 7/32, 3/32, 3/32, 3/32), whose image ℓ* = Tq* is
  context (0,0): (9/32, 7/32, 7/32, 9/32); contexts (0,1), (1,0), (1,1): *identical to p_{5/8}*.
So the nearest local model agrees with the box on three contexts and repairs only one — an instructive contrast with the naive candidate p_{1/2}, which repairs all four contexts yet achieves the *same* optimal distance. The repair is far from unique; the *value* is.

**Verification of the certificate by hand (complementary slackness over ℚ):** p − ℓ* is supported on context (0,0) with values (4,−4,−4,4)/32 = ½·(1,−1,−1,1)/8. The dual optimizer is exactly B* = s/8 (the normalized CHSH pattern; printed by the script), with β* = max_λ B*·ℓ_λ = 1/4. Then B*·(p − ℓ*) = ½·(1/8)·… = 1/16 = ‖p − ℓ*‖_π coordinate-for-coordinate: the sign pattern of the residual matches the witness on every active coordinate, which is the exact-rational KKT certificate that both are optimal. Strong duality closes it: primal value 1/16 = dual value.

**Negative mass:** N(p_{5/8}) = 1/8 via the spread-normalized dual α = s/4 (spread over vertices exactly 1, value S/4 − ½ = 1/8); primal and dual agree exactly. For the PR box: N(PR) = 1/2 with an optimal signed preimage of L¹-mass exactly 2 (Σq⁺ = 3/2, Σq⁻ = 1/2).

## Part V — Headroom: how far the argument extends before it stops being real

*Added after the first review, in answer to the question "how much further can this argument be extended and remain real, not LLM slop?" Check numbering continues `verify_obstruction.py` (C0–C11 there; S0 and C12–C21 in `verify_headroom.py`).*

### §14 The question, and the shape of an honest answer

The question deserves better than a mood. "Real" mathematics, in the sense the draft itself practices at its best, is not a tone but a verifiable property: a claim is real when it comes with a finite certificate that a third party can re-check in exact arithmetic, when it introduces or relates convex objects rather than relabeling them, and when its distance from the known literature is declared rather than obscured. So the way to answer "how much further" is to (i) state the test explicitly, (ii) climb the next rung of the ladder in full — thereby measuring the effort per rung — (iii) prove a theorem delimiting where the method's own fuel runs out, and (iv) grade the remaining directions into what can honestly be done, what would be assimilation, and what would be slop.

The answer, in one paragraph, is this. One more complete rung was available at the cost of a few days, and §16–§19 climb it: the signed-negativity machinery generalizes to the three-party GHZ–Mermin scenario exactly, with every constant pinned over ℚ (36/36 new checks); the conjecture left open in §3.3(c) closes as a corollary of the same construction; and §16 proves a boundary theorem — the deterministic-gap criterion — that computes, for any candidate Bell functional, whether the negativity layer can see it at all. Beyond that rung the honest inventory is short: roughly six Tier-A propositions provable by the installed machinery, a bounded amount of Tier-B assimilation of results the literature already owns, and a hard stop at Tier C where the only defensible move is to declare open problems. A framework that can prove theorems about its own limits (Propositions 21 and 28 below) is doing the one thing fluent paraphrase structurally cannot; that self-delimiting property, maintained as a discipline, is the whole answer.

### §15 The reality test: five questions for any proposed extension

Every proposed extension of the draft's programme — including the ones below — should be run through five questions. They are phrased so that each is answerable by inspecting an artifact, not by adjudicating taste.

1. **Certificate.** Does the claim produce a finite certificate checkable in exact arithmetic — a primal/dual LP pair, a support model, a rank identity, a KKT sign pattern? If no certificate exists or none is exhibited, the claim is prose, whatever its citation count.
2. **New object or new identity.** Does it introduce a new polytope, cone, fiber, or hierarchy level, or prove a new equality/inequality between existing ones? Restating a known duality in new notation fails this test no matter how many equations are displayed.
3. **Strictness witness.** Every claimed strict inequality must come with a point witnessing it; every claimed equality must come with both sides' certificates. (Theorem 7's strictness at PR and p₇₀/₉₉ passes; a bare "strict in general" would not.)
4. **Literature independence, declared.** Against Fine [3], Abramsky–Brandenburger [4], Brito–Amaral–Chaves [5], Abramsky et al. [7], Navascués et al.: if the result is known, it is labeled known and the delta is stated. The draft's §11.2 review-assimilation discipline is exactly this test administered to itself; slop is distinguished by hiding reuse.
5. **Formalization class.** Is the claim provable from the census's existing primitives (finite types, certificate checking, exact rank) or does it require new definitions that smuggle in the conclusion? A claim whose Lean statement needs an axiom tailored to it is a claim about the axiom, not the world.

Against these criteria the draft's behavior-level core passes cleanly: 39 exact checks, a claim ledger, an explicit outside-census list, and limitations stated in its own voice. Two places flirt with the line and both are repairable. First, the RSI section's "task-relevant fiber width" is not yet an operational quantity until Theorem 19-style separating pairs are *required* as certificates — §9.3's protocol v0.1 is the fix, and §21 lists its computational form. Second, the dynamical witness (18) is a genuine theorem whose useful range the draft never quantifies; §20 quantifies it and finds the range small but nonzero, which is the honest outcome.

---

### §16 The boundary theorem: what the signed-mass method can and cannot see

Throughout, a *scenario* is a finite Bell scenario with deterministic behaviors {ℓ_λ}, ℒ = conv{ℓ_λ} the local polytope, NS the no-signalling polytope, and N(p) the minimal negative mass of a normalized signed extension (§3.3). Let F be any linear functional on behavior space, B(F) = max_λ |F(ℓ_λ)| its deterministic bound, and A(F) = max_{p ∈ NS} |F(p)| its no-signalling maximum (both attained: the polytopes are compact). Write N(p) ≥ 0 for the negative mass.

**Proposition 20 (generic negativity bound).** *For every normalized NS behavior p, every signed extension q = q⁺ − q⁻ of p with negative mass N(q), and every functional F:*
  |F(p)| ≤ B(F)·(1 + 2N(q)), *hence* N(p) ≥ (|F(p)| − B(F)) / (2·B(F)).

*Proof.* F(p) = Σ_λ q_λ F(ℓ_λ), so |F(p)| ≤ Σ_{q⁺} q_λ|F(ℓ_λ)| + Σ_{q⁻} q_λ|F(ℓ_λ)| ≤ B·(Σq⁺ + Σq⁻) = B·(1 + 2N), using Σq⁺ = 1 + Σq⁻ = 1 + N from normalization. ∎

**Proposition 21 (deterministic-gap criterion).** *Define the gap γ(F) = A(F) − B(F) ≥ 0 (deterministic assignments lie in ℒ ⊆ NS, so the gap never negative). Then:*
(i) *the bound of Proposition 20 is positive for some p ∈ NS **iff** γ(F) > 0;*
(ii) *if γ(F) = 0 the negativity layer extracts nothing from F, for any behavior;*
(iii) *if γ(F) > 0, a maximizer p* of F over NS satisfies N(p*) ≥ γ(F)/(2B(F)).*

*Proof.* (i)–(ii): the certified floor (|F(p)| − B)/(2B) ≤ (A − B)/(2B) = γ/2B is positive for some p iff A > B. (iii): compactness of NS attains A; apply Proposition 20 to p*. ∎

The criterion has teeth because it is *computable per functional*, and because it cuts in an unexpected direction. Three functionals on the GHZ scenario make the point **[exact, C20a–e]**:

| functional | B(F) (deterministic max) | A(F) (NS max) | γ(F) | verdict |
|---|---|---|---|---|
| Mermin M = −E₀₀₀ + E₀₁₁ + E₁₀₁ + E₁₁₀ | 2 | 4 | 2 | bites; N ≥ (M−2)/4 |
| Svetlichny S (standard sign pattern) | 4 | 8 | 4 | bites; N ≥ (S−4)/8 |
| all-plus variant W = E₀₀₀ + E₀₁₁ + E₁₀₁ + E₁₁₀ | 4 | 4 | 0 | **vacuous** |

The Svetlichny row corrects a natural first impression. One might guess from B(S) = 4 = the "hybrid-local bound" that the negativity method is blind to Svetlichny-type violations. It is not: the moment box S-box with E(x,y,z) = σ(x,y,z) at *every* context is a perfectly good NS table (P = (1/8)(1 + σ·s_as_bs_c), marginals uniform), its S-value is 8, so A(S) = 8 > 4 — and the machine goes further: the dual certificate α = S/8 has spread exactly 1 over the vertices, so N(S-box) ≥ 8/8 − ½ = ½, and the exact simplex returns N(S-box) = **1/2** **[exact, C20d]**: sharp, like CHSH and Mermin. The genuinely vacuous object is the all-plus variant W, whose deterministic max already saturates its NS max — W does not separate ℒ from NS at all, and no convex method built on separation from ℒ could see it. That is the precise content of Proposition 21: **the negativity layer inherits exactly the separating functionals of the scenario, with per-functional yield γ/(2B), and adds nothing beyond separation.** The boundary of the method is the boundary of the polytope's dual cone — which is also exactly where the quantum level (a genuinely non-polytope object) begins, and why the SDP layer of the literature is assimilation rather than invention (§21, Tier B).

### §17 The Mermin rung: multi-party negativity, closed and exact

Scenario: three parties, binary settings and outcomes; spins s_a = 1 − 2a; 8 contexts, 64 table entries, 64 deterministic assignments λ = (α₀, α₁, β₀, β₁, γ₀, γ₁) ∈ {±1}⁶. The *Mermin functional* is M(p) = −E(0,0,0) + E(0,1,1) + E(1,0,1) + E(1,1,0), where E(x,y,z) = Σ abc-spin-products · p(a,b,c|x,y,z). Two families of behaviors, both with uniform marginals:

- the **GHZ box** G: p(a,b,c|x,y,z) = ¼·δ[s_as_bs_c = β(x,y,z)], with β = −1 only at context (0,0,0) and +1 elsewhere;
- the **Mermin line** Q_v: p(a,b,c|x,y,z) = (1 + v·χ(x,y,z)·s_as_bs_c)/8, where χ = −1 at (0,0,0), +1 at (0,1,1), (1,0,1), (1,1,0), and 0 on the remaining four contexts. Q₀ is the uniform behavior; Q₁ is the all-or-nothing GHZ-parity box; at v = 1/√2 the correlator pattern is exactly the quantum GHZ state's (⟨XXX⟩ = −1/√2, ⟨XYY⟩ = ⟨YXY⟩ = ⟨YYX⟩ = +1/√2, rest 0).

**Lemma 22 (deterministic range).** *M(λ) ∈ {−2, +2} for every one of the 64 assignments, with exactly 32 each; in particular B(M) = 2.* **[exact, C12a]**

*Proof.* Write t₁ = α₀β₀γ₀, t₂ = α₀β₁γ₁, t₃ = α₁β₀γ₁, t₄ = α₁β₁γ₀, so M(λ) = −t₁ + t₂ + t₃ + t₄. Multiplying the four terms, every party-value appears squared twice: t₁t₂t₃t₄ = +1 — equivalently t₄ = t₁t₂t₃ **[exact, C12b]**. Enumerate the sign patterns (t₁,t₂,t₃) ∈ {±1}³ and substitute t₄: the sum −t₁ + t₂ + t₃ + t₁t₂t₃ equals +2 on {(+,+,+), (−,−,+), (−,+,−), (+,−,−)} and −2 on the complementary four. ∎

**Lemma 23 (the boxes).** *G and Q₁ are normalized, fully no-signalling behaviors, and M(G) = M(Q₁) = 4; M(Q_v) = 4v for all v.* **[exact, C13]**

*Proof.* For G: at each context exactly four outcome triples satisfy the parity condition, each with weight ¼; for any fixed pair of parties and outcomes there is a unique third outcome completing the parity, so all single-party and pairwise marginals are uniform and independent of the other parties' settings — full no-signalling. The correlator of a ¼-δ table is its β-pattern, so M(G) = −(−1) + 1 + 1 + 1 = 4. For Q_v the moment expansion gives correlators E(x,y,z) = v·χ(x,y,z) directly (each spin-product averages the constant term to zero and squares to one on the χ term), and uniformity of all lower marginals follows from spin symmetry; M(Q_v) = v(1 + 1 + 1 + 1) = 4v. Positivity holds because |vχs_as_bs_c| ≤ 1 for v ≤ 1. ∎

**Theorem 24 (multi-party negative mass, exact).** *For every rational v ∈ [0,1]: N(Q_v) = max(0, v − ½).* **[exact, C14–C16]**

*Proof.* (≥) For v ≥ ½, take the dual certificate α = M/4 (Proposition 4's closed form): α·ℓ_λ = M(λ)/4 ∈ {−½, +½} for all 64 vertices, so spread_λ(α·ℓ_λ) = 1 exactly, and α·Q_v − max_λ α·ℓ_λ = M(Q_v)/4 − 2/4 = v − ½. (For v ≤ ½, Q_v is local — see Proposition 25 — so N = 0.) (≤) Exhibit the signed extension q^v_λ = (1 + v·M(λ))/64. Normalization: Σ_λ q^v = (64 + v·Σ_λ M(λ))/64 = 1, since Σ_λ M(λ) = 32·2 − 32·2 = 0. Observed table: fix a context (x,y,z) and outcome spins (A,B,C); the assignments matching them form a set of 8 on which the unique M-term involving exactly the three fixed party-values contributes ±8ABC and every other M-term contains a free spin whose signed sum vanishes; hence Σ_{matching} M(λ) = 8·χ(x,y,z)·ABC, and (T q^v)(a,b,c|x,y,z) = 1/8 + (v/64)·8·χ·s_as_bs_c = (1/8)(1 + v·χ·s_as_bs_c) = Q_v(a,b,c|x,y,z) exactly. Negative mass: q^v_λ < 0 iff M(λ) = −2 and v > ½, each such entry equal to −(2v−1)/64, 32 of them, so N ≤ 32(2v−1)/64 = (2v−1)/2 = v − ½. Both sides agree. The exact simplex confirms independently: N_LP(Q_{3/8}) = 0, N_LP(Q_{5/8}) = 1/8, N_LP(Q₁) = ½, with the returned primal certificates re-verified by direct recomputation. ∎ **[exact, C14–C16]**

**Corollary 24.1 (endpoint coincidence).** *At the quantum endpoints of both families the minimal negative mass agrees: for v = 1/√2, N = (√2 − 1)/2 on the CHSH isotropic line and on the Mermin line alike (rational proxy: at v = 7/10 both give N = 1/5 **[exact, C15, C19c]**). Within this family, the "repair price of quantumness" measured by the spread-normalized monotone is line-independent — a small structural fact that would have been invisible without pinching both lines at once.*

### §18 The comparison chain: CF = 2N on both lines; the ratios to R are normalization artifacts

**Proposition 25 (contextual fraction, exact).** *With CF per [7] (1 − maximal local weight in a decomposition into a local behavior and an arbitrary normalized behavior): CF(Q_v) = max(0, 2v − 1) for all rational v ∈ [0,1]. The same formula holds on the CHSH isotropic line p_v (likely known in essence through [7]'s examples; labeled accordingly).* **[exact, C17–C18]**

*Proof.* (≥) Let Q_v = w·ℓ + (1−w)·r with ℓ ∈ ℒ and r any normalized NS behavior. By Lemma 22 and convexity, |M(ℓ)| ≤ 2; by |E| ≤ 1 per context, |M(r)| ≤ 4. Linearity: 4v = M(Q_v) ≤ 2w + 4(1−w), so w ≤ 2 − 2v and CF ≥ 2v − 1. (≤) For v ≥ ½, decompose Q_v = (2−2v)·Q_{1/2} + (2v−1)·Q₁ **[exact, C18a]** — which requires Q_{1/2} ∈ ℒ. Locality of Q_{1/2} is an LP feasibility question over 64 assignments; the exact simplex returns a feasible 26-point support model with dyadic weights in {1/32, 1/16} (full listing in the run log; re-verified coordinate-for-coordinate against Q_{1/2} **[exact, C17a–c]**), and M(Q_{1/2}) = 2 confirms the point sits exactly on the Mermin facet **[C17b]**. On the CHSH line the same argument uses p_{1/2} ∈ ℒ (Fine's theorem; LP-feasibility re-verified **[C19b]**). ∎

**Proposition 26 (repair cost on the Mermin line).** *With uniform context weights π = 1/8: R_π(Q_v) = (2v − 1)/8 for v ≥ ½.* **[exact, C18]**

*Proof.* (≥) B = M/16 has dual norm exactly 1 (max coordinate 2·(1/16)/(1/8) = 1) and max_λ B·ℓ_λ = 2/16 = 1/8, so R_π(Q_v) ≥ B·Q_v − max_λ B·ℓ_λ = 4v/16 − 1/8 = (2v−1)/8 — against *every* local point at once. (≤) ‖Q_v − Q_{1/2}‖_π = (2v−1)·‖Q₁ − Q_{1/2}‖_π = (2v−1)/8, computed coordinate-wise **[C18]**, and Q_{1/2} ∈ ℒ by Proposition 25. The two bounds coincide; moreover B·(Q_v − Q_{1/2}) = ‖Q_v − Q_{1/2}‖_π coordinate-for-coordinate, the exact KKT alignment. ∎

The full chain, all exact:

| line | R_π (uniform π) | N | CF | ratios |
|---|---|---|---|---|
| CHSH isotropic p_v | (2v−1)/4 | (2v−1)/2 | 2v−1 | CF = 2N = 4R |
| Mermin Q_v | (2v−1)/8 | (2v−1)/2 | 2v−1 | CF = 2N = 8R |

Two readings, one methodological. The invariant content is that **CF = 2N on both lines**, with the same vanishing sets and the same linear laws — and both CF and N are normalization-free objects (a decomposition weight; a vertex-spread dual value). The ratio between those and R_π differs between the lines (4R versus 8R) purely because R carries the context-count normalization ½·π through its definition: the coordinate-boxed norm divides by the number of contexts, so a 4-context and an 8-context scenario are not comparable in R without renormalization. Any future claim that "repair cost and contextual fraction agree" must therefore first fix the normalization convention; the draft's constants (8, 1/8) are CHSH-specific in exactly this sense.

**Conjecture (labeled open; the next Tier-A LP).** *CF(p) ≤ 2·N(p) for every normalized NS behavior, with equality at the PR box and along both lines above.* The evidence: every point computed, equality at maximal nonlocality, and both monotones vanishing exactly on ℒ. Why it is not proven here: the naive coupling argument fails — the positive and negative parts of an optimal signed extension are not themselves behaviors (their per-context masses need not be context-independent), so no decomposition of p is produced by Prop 4's optimizer; and the direct LP (maximize local weight against a free NS partner, 64 assignment variables plus a 64-entry NS table with its marginal rows) was not run. Either the inequality or a separating pair of behaviors would be a genuine Tier-A result; the LP is specified precisely so the next session can settle it mechanically. **[Update (§23): the LP has now been run. Verdict: REFUTED — the inequality holds with equality across all of CHSH but fails on the GHZ scenario, with a fully certified counterexample at CF = 19/64 > 2N = 25/128. See §23.]**

### §19 Closing the CHSH conjecture: N(p_v) = max(0, v − ½) for all v

**Theorem 27 (isotropic negative mass; §3.3(c)'s conjecture promoted).** *For every rational v ∈ [0,1], N(p_v) = max(0, v − ½); in particular N = 2R_π on the whole isotropic line, with uniform π.* **[exact, C19c–e]**

*Proof.* (≥) is §3.3's dual certificate α = s/4 (spread 1 over the sixteen vertices since K(λ) ∈ {±2}; value S(p_v)/4 − ½ = v − ½). (≤) Exhibit q^v_λ = (1 + v·K(λ))/16, where K(λ) = α₀β₀ + α₀β₁ + α₁β₀ − α₁β₁ ∈ {±2} with 8 assignments each (if β₀ = β₁ then K = 2α₀β₀; else K = 2α₁β₀). Normalization: Σ_λ K(λ) = 0. Observed table: fixing (x, y) and outcome spins (A, B) leaves 4 completions, on which the unique K-term carrying both fixed values contributes ±4AB and the other three terms contain a free spin summing to zero; so Σ_{matching} K(λ) = 4·c_xy·AB with c = (+1, +1, +1, −1), and (T q^v)(a,b|x,y) = ¼ + (v/16)·4·c_xy·s_as_b = (1/4)(1 + v·c_xy·s_as_b), which is exactly p_v (its correlators are E_xy = v·c_xy). Negative mass: 8 entries of −(2v−1)/16, total (2v−1)/2 = v − ½. Pinched. The simplex confirms N_LP(p_{5/8}) = 1/8 **[C19e]**, and the KKT alignment at v = 5/8 (B = s/8, distance 1/16 to the nearest local point, dual norm 1) reproduces Appendix B's certificates **[C19f]**. ∎

A methodological note is the real payload here. §3.3(c) left "N = 2R on the line" as a conjecture with exact confirmations at two points and an explicit disclaimer against generalizing from them; the closure took one explicit primal construction plus the already-known dual certificate — half an afternoon. The difference between that and slop is not subject matter but discipline: the conjecture was *labeled*, its evidence *bounded*, and its closure *certificated*. A research notes document that maintains this triad can grow indefinitely without rotting; one that asserts unverified generalizations in the same voice as its theorems is already slop regardless of topic.

### §20 Quantifying the draft's weakest link: the dynamical witness's certification window

The draft's conditional dynamical witness (18) — S(t) − 2 ≥ t·b − κt² − δ(t) — is a theorem, but a theorem whose usefulness depends on a number the draft never computes: how much violation can the right-hand side ever certify? The maximum of tb − κt² over t is b²/(4κ), attained at t = b/(2κ), and every factor is bounded in terms of the draft's own constants.

**Proposition 28 (certification window).** *Under hypotheses (17), the witness certifies at most b²/(4κ) − δ(t) of CHSH violation. With b ≤ ‖B‖_∞ = 2√2 (so b² ≤ 8) and the draft's constants — κ = 24g²_inc from [P1], or κ = 2(1+k²)g² from [P2] — the window is at most 1/(12g²_inc) [P1] and at most 1/(5g²) for k = 2 [P2].* **[exact, C21a]**

*Proof.* Maximize the quadratic: d/dt (tb − κt²) = 0 at t = b/(2κ), value b²/(4κ); substitute the bounds. ∎

The reading is the honest kind of deflation. The Tsirelson gap is 2√2 − 2 > 4/5, so per unit coupling the witness can certify at most 5/48 ≈ 10.4% [P1 constants] or 1/4 [P2, k = 2] of the quantum–classical gap **[exact, C21b]** — and the window shrinks quadratically: at g_inc = 4 the [P1] bound is 1/192, under half a percent of the gap. Three consequences for the draft. First, (18) is real mathematics with a small window, and the draft should say so in exactly those words rather than leaving the reader to guess. Second, any future "dynamical Bell proof" claim has three and only three honest routes: shrink κ by genuine second-order estimates (this is the open §12 programme, and it is hard), find an observable with a larger oriented baseline b relative to ‖B‖_∞, or accept that the witness certifies only near the Tsirelson-attaining regime where b is maximal. Third, the window computation is itself a five-line exact-rational check — which is precisely why its absence from the draft would have been slop-adjacent, and its presence is not.

### §21 The tier map: what remains, graded by the reality test

**Tier A — real, provable with the installed machinery, each with a one-line strategy.** These are the honest remaining extensions at the behavior level; none requires new definitions, and each produces certificates.

1. **CF ≤ 2N in general, or a separating counterexample.** The LP is fully specified in §18 (maximize local weight against a free NS partner on the 64-entry GHZ tables); the CHSH analogue is 16 entries. Either outcome is a result. **[Resolved in §23 — refuted: certified GHZ counterexample, CF = 19/64 > 2N = 25/128.]**
2. **Chained-inequality negativity.** The q^v construction ports verbatim: for the n-link chained functional, deterministic max 2(n−1), algebraic NS max 2n, gap 2, so N ≥ (S_n − 2(n−1))/(4(n−1)) with sharpness along the chained isotropic line by the matching-sum computation. Expected to be mechanical; worth doing once to confirm the pattern generalizes.
3. **Facet-wise R on the Mermin polytope.** Proposition 26 is one instance of a general statement: for any exposed facet functional F of the three-party local polytope with normalization-span conventions, R_π along the F-line equals the gap fraction. Each facet needs one LP (exposedness) and one segment computation.
4. **Tangent-cone exit at the M = 2 face.** Corollary 12 ports to the Mermin facet: on the exposed M = 2 face of ℒ₃, the normalized functional M/16 *is* the oriented exit witness, with the same proof. Needs only the facet's exposedness, which the R-pinching LP already exhibits.
5. **The no-learning certificate, computationally.** Type-2 severity is finitely computable: width(d) = diam τ(F(d)) by enumeration, and its witness is a *pair* (h, h′) in one fiber with τ(h) ≠ τ(h′) — the RSI analogue of the Bell dual certificate. A claimed memory update that cannot exhibit a separating pair has, by Theorems 18–19, changed nothing task-relevant. This is §9.3's protocol v0.1 turned into a script, and it is the one RSI direction that passes all five reality criteria today.
6. **Lean absorption.** Lemmas 22–23 and Theorems 24/27 are the cheapest high-value targets: their proofs are certificate-checks over ℚ (the script's arithmetic is already a proof trace), needing only finite types and linear algebra from the census's existing primitives. **[Done in §23: `BellNegMass.lean`, axiom-clean.]**

**Tier B — real but assimilation; the literature owns these, and re-deriving them would be motion, not progress.** The almost-quantum / Navascués hierarchy is the sequence of SDP-computable outer approximations of Q; slotting Q̄'s levels into Theorem 7's hierarchy is a reframing with new notation, not a new theorem — cite, and use it to define "residual at level k" if that notion earns its keep. Brito–Amaral–Chaves [5] already own the tight trace-distance constants that (15) finitely approximates. The cohomology witnesses of [6] detect only the ℤ₂ all-or-nothing class (flagged in §3.4; completing them is hard open mathematics, not a notational exercise). Abramsky et al. [7] define CF and prove CF = RC/(1+RC); the robustness comparison belongs in a related-work paragraph. Each of these is one honest citation away from being an asset instead of a liability.

**Tier C — would be slop unless hardened; each fails a named criterion.** (1) Any operational reading of R/N/CF as "the amount of nonlocality" beyond polytope geometry — fails the certificate criterion; the monotones are gauges on a polytope, and pretending otherwise manufactures metaphysics. (2) Fiber-width theorems about self-improving systems beyond Theorems 16–19 without a declared (O, f) fixed across the audited update — fails strictness-witness and formalization-class, and re-encounters the endogeneity problem of §9.2. (3) Second-order exit claims without a remainder enclosure — the draft correctly leaves this open; asserting it with vocabulary instead of estimates fails the new-object criterion. (4) Infinite-dimensional or infinite-setting generalizations that re-parametrize known results — fails the literature-independence criterion. (5) More violation tables without dual certificates — fails the certificate criterion, and is now *detectable*: the 75 exact checks across the two scripts exist precisely so that decimals added without certificates become visible against the ledger.

### §22 The verdict

How much further can the argument be extended and remain real? The behavior-level core had exactly one more rung of this difficulty in it, and it is now climbed and machine-checked: multi-party negativity exact on the Mermin line (Theorem 24), contextual fraction exact on two lines (Proposition 25), repair cost exact on the second line (Proposition 26), the §3.3 conjecture closed (Theorem 27), a per-functional boundary theorem that computes where the negativity layer goes blind (Proposition 21), and a quantified window on the draft's weakest quantitative link (Proposition 28). Six Tier-A items remain, each days-not-weeks and each certificate-producing; Tier B is bounded assimilation best dispatched in one related-work section; Tier C is where the programme dies if the five-question test is not administered. After the Tier-A list is exhausted, the frontier genuinely transfers: to the second-order dynamical layer (hard, open, worth a paper on its own), to the RSI certificate calculus (exactly as real as the declared observation map, and no more), and to formalization debt in Lean (start with Theorems 24 and 27).

To the meta-question — is this whole exercise itself slop? — the framework now carries its own answer. It has produced, in two sessions, eleven new theorem-level results with complete proofs, seventy-five exact-rational checks across two independently re-runnable scripts, two conjectures that were labeled as conjectures and one of which is now closed, and two theorems (21 and 28) whose content is the *limitation* of the framework's own methods. A discourse that can compute where it stops, in exact arithmetic, is doing the one thing fluent text structurally cannot; the practical rule for every future extension is contained in that fact. Extend exactly as far as the certificates continue to close; label everything beyond them as conjecture, assimilation, or prose; and re-run the numbers before believing any sentence that begins with "it follows that".

### §23 The specified LP run: the conjecture is refuted, and the Lean rung is climbed

§18 ended by specifying the CF ≤ 2N LP "precisely so the next session can settle it mechanically." This section records that settlement. Two artifacts do the work: `verify_cf2n.py` (a 78-point exact-rational battery: the §18-specified moment-form CF LP — maximize local weight against a free NS partner, the NS partner parametrized by its 8 resp. 26 moment coordinates with one δ ≥ 0 row per cell — plus the signed-extension N LP, an independent vertex-form CF LP on CHSH, and the Prop-4 dual LP for N; run log `cf2n_run.log`) and `audit_rnd2.py` (gold-standard dual-certificate certification of the decisive point; log `audit_rnd2.log`). Check numbering continues C22–C28.

**Result A (CHSH equality, exact across the whole scenario battery).** *On every one of the 62 CHSH battery points — the isotropic line at 13 values of v, the PR box, all 8 nonlocal NS vertices, the local all-plus parity box, and 40 seeded random NS mixtures — the two LPs return CF(p) = 2·N(p) exactly, and every point's certificate chain closes (N-primal re-verified; N-dual = N-primal to the last bit; the CF decomposition p = w·ℓ + κ·r re-verified with ℓ ∈ ℒ and r a normalized NS behavior; the vertex-form CF value equal to the moment-form value).* **[exact, C22–C25]** So the conjecture's constant is not merely tight on the isotropic line: in the (2,2,2) scenario the two monotones coincide *everywhere*, including at generic interior points far from any facet. The structural reason is presumably that in a two-party scenario both monotones are functions of the same facet functional's maximum — CF = (F* − 2)/2 and N = (F* − 2)/4 with F* the largest of the eight CHSH-type values — which is consistent with every computed point and provable by the same pinching techniques, though not proven here; it is labeled as the natural next proposition, not asserted as one.

**Result B (refutation, certified).** *The conjecture CF(p) ≤ 2·N(p) is FALSE on the (3,2,2) GHZ scenario.* The separating behavior is the seeded battery point

  p\* = (1/6)·W + (1/3)·ℓ₆₃ + (5/12)·G + (1/12)·Q₅/₈,

where W is the local all-plus parity box, ℓ₆₃ a deterministic box, G the GHZ box, and Q₅/₈ the Mermin-line point at v = 5/8. For this normalized, fully no-signalling behavior the exact values are

  CF(p\*) = 19/64 ≈ 0.297,  N(p\*) = 25/256 ≈ 0.098,  CF − 2N = **13/128 > 0**,

and both values are *pinched by independent certificates* — this is the step that separates a result from a suspicion, and it is why the audit script exists:

- **N(p\*) = 25/256**: the signed-extension primal (re-run under pure Bland pivoting to rule out pivot-path artifacts) and the Proposition-4 dual LP (max α·p + β s.t. −1 ≤ α·ℓ_λ + β ≤ 0 over all 64 vertices) agree to the last bit; the returned dual has spread exactly 1, β = −max_λ α·ℓ_λ = 0, and α·p\* + β = 25/256 — a feasible dual point attaining the primal optimum, i.e. strong duality verified in exact arithmetic, not invoked.
- **CF(p\*) = 19/64**: the moment-form primal decomposition (again Bland-only) gives CF ≤ 19/64 with the certificate re-verified coordinate-for-coordinate (p\* = γ-part + δ, δ ≥ 0, marginally consistent at scale κ, Σγ + κ = 1); the CF-LP dual — maximize p·u subject to the 27 moment-orthogonality rows Dᵀ(u + v) = 0, v ≥ 0, and Σ_{i match λ} u_i ≤ −1 for all 64 assignments — returns −45/64 = CF − 1 with its certificate re-verified, giving CF ≥ 19/64. Both sides closed: the value is exact, not approximate.
- Two structural facts sharpen the reading. First, M(p\*) = 37/24 < 2 = B(M): the Mermin functional does not even separate p\* from ℒ — the negativity that N fails to charge for is invisible to the functional that built §17. The optimal Prop-4 dual at p\* is a *different* spread-1 functional (deterministic max 0, spread 1 — a negative-part detector, not a Bell witness), which is exactly the kind of dual the §18 coupling argument could not see. Second, the violation is not a knife-edge: the battery also contains GHZ points where the conjecture is strict (rnd0: CF = 1/2 < 2N = 3/4; rnd1: CF = 3/4 < 2N = 13/16), so on the (3,2,2) scenario the ratio CF/(2N) takes values both below and above 1 (observed range on the battery: 24/13 ≈ 1.85 to 76/25 ≈ 3.04). There is no universal constant to repair the conjecture with; the equality CF = 2N is a *two-party* accident, not a normalization artifact.

**Result C (the corrected landscape).** Across the 78-point battery: 56 points sit at CF = 2N exactly (all nonlocal CHSH points, all local points, both isotropic lines, G, the S-box), 2 GHZ interior points are strict, and 1 violates. The §18 reading survives in amended form: what is invariant is not "CF = 2N" but the *vanishing sets* (both monotones vanish exactly on ℒ — verified at every local battery point) and the two-party equality. The three-way classification of §16's gap criterion gets a companion: the negativity layer's *charges* and the contextual fraction's *decomposition weight* are incomparable monotones in three or more parties, and any future claim connecting them must go through the per-point certificates rather than a universal constant.

**Result D (Lean absorption of Theorems 24/27).** `BellNegMass.lean` (≈ 440 lines, Lean 4 core only — no Mathlib — compiles under toolchain v4.35.0 in ≈ 8 s) formalizes both negative-mass theorems in scaled-integer certificate form: for every m : ℕ (v = m/8), the canonical extension q^v_λ = (8 + m·F(λ))/D is normalized (Σq = 128 resp. 512), projects to the line table (T(q)(cell) = 128·p_v(cell) resp. 512·Q_v(cell)), and has negative mass exactly 128·max(0, v − ½) resp. 512·max(0, v − ½) — and *every* normalized signed extension has negative mass at least that (the Prop-20 lower bound, proved by a double-sum swap `fubini` + the kernel-checked deterministic bound F(λ) ∈ {±2} + the pointwise step w_λ·F(λ) ≤ 2|w_λ|; no LP duality is developed, per the census's certificate-checking recommendation). The closed finite identities — deterministic ranges, parity sums, match-sums over all 16 resp. 64 assignments — are kernel `decide` computations over `Fin 16`/`Fin 64`, the Lean twins of checks C12–C21. Axiom census of both packaging theorems: {propext, Classical.choice, Quot.sound} only; `#print axioms` is part of the file. The scaled-integer statement is the proof-trace form of the notes' rational statement: divide by 128 (CHSH) resp. 512 (GHZ) to recover N(p_v) = max(0, v − ½).

A methodological postscript, because it is the second time the pattern has fired. §18 labeled the conjecture, bounded its evidence, and specified its LP; §23 ran the LP and the answer came back *negative* — and the negative answer is only as good as its certificates, which is why the refutation ships with primal AND dual pinching on both monotones, a Bland-only re-run, and an audit script that re-derives the point from the seed. A framework that can refute its own conjectures mechanically, in exact arithmetic, with certificates a third party can re-check, is doing precisely what §15's five questions demand. The remaining Tier-A list (§21 items 2–5) is unchanged by this section except in one respect: the chained-inequality item (2) now carries extra interest, since the equality N = 2R it would extend is a two-party phenomenon whose three-party analogue just failed for CF.

### Part V evidence map

| Result | Type | Proof | Machine |
|---|---|---|---|
| Prop 20 (generic negativity bound) | new | §16, 4 lines | analytic (structure); scenario-generic |
| Prop 21 (deterministic-gap criterion) | new | §16 | **[exact, C20a–e]** incl. N(S-box) = 1/2 |
| Lemma 22 (M(λ) ∈ {±2}) | new | §17 | **[exact, C12]** |
| Lemma 23 (G, Q₁ boxes) | new | §17 | **[exact, C13]** |
| Theorem 24 (N(Q_v) = max(0, v−½)) | new | §17, pinched | **[exact, C14–C16]** |
| Cor 24.1 (endpoint coincidence) | new | §17 | **[exact, C15/C19]** |
| Prop 25 (CF = 2v−1, both lines) | new (CHSH case likely known [7]) | §18 | **[exact, C17–C18]** |
| Prop 26 (R_π(Q_v) = (2v−1)/8) | new | §18, pinched | **[exact, C18]** |
| Theorem 27 (N(p_v) = max(0, v−½)) | new; closes §3.3(c) | §19, pinched | **[exact, C19]** |
| Prop 28 (witness window ≤ 1/(12g²)) | new | §20 | **[exact, C21]** |
| Conjecture CF ≤ 2N | **refuted** (§23) | §23, certified counterexample | **[exact, C22–C28 + audit]** |
| CHSH equality law CF = 2N (62/62 battery points) | new (computational) | §23 | **[exact, C22–C25]** |
| GHZ counterexample p\*: CF = 19/64 > 2N = 25/128 | new; refutes §18 conjecture | §23, dual-pinned both values | **[exact, audit]** |
| Lean formalization of Theorems 24/27 | new artifact | §23 / `BellNegMass.lean` | axiom-clean (propext, choice, Quot.sound) |
| Q_{1/2} ∈ ℒ, 26-point model | new certificate | §18 | **[exact, C17]** |

### References

Numbered [n] refer to the draft's bibliography (Bell 1964; CHSH 1969; Fine 1982; Abramsky–Brandenburger 2011; Brito–Amaral–Chaves 2018; Abramsky–Mansfield–Soares Barbosa 2012; Abramsky et al. 2017; Mermin 1990; Shannon 1948; Thon–Jaeger 2015; Tsirelson 1980). [P1], [P2], [P3] refer to the draft's companion manuscripts, which were not supplied. Additional context used above, none of it load-bearing for the new proofs: the response-function/determinization tradition (Pitowsky 1989; Jarrett 1984; Barrett–Gisin 2011), Kemeny–Snell lumpability, and the Halmos dilation for contractions. Full bibliographic data for these three should be added to the draft if their use (§2.2, §7.2, §6.2/8) is retained.
