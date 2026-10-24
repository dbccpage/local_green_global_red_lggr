# Output: round_2_purity_dissipation_and_baker_transcendence.md

- **Timestamp:** 2026-10-17T00:39:18.662049
- **Model:** claude-fable-5-1
- **Round:** 2
- **Duration:** 345.6s
- **Tokens:** In=18783, Out=30213
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_2_purity_dissipation_and_baker_transcendence.md`
- **Continued From:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\outputs\20261017_000730_round_1_quantum_relational_axioms_and_povm_finitude_claude-fable-5-1.md`

---

## Thinking Trace

```text

```

---

## Response Content

# Round 2 Record — CPTP Purity Dissipation, Lift Budget Exhaustion, Baker Transcendence

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 2/4**
**Execution note:** No Lean, Cargo, or solver ran. All arithmetic below is hand-computed exact rational arithmetic with decimal sanity checks; it is not machine-checked. Round 1 definitions ($\mathcal{U}_Q$, $\operatorname{report}$, $(\succ)$, Theorem Q.1, Corollary Q.1.1) are referenced, not re-derived, and are not treated as external receipts.

**Numbering note.** The prompt labels the purity lemma "Lemma Q.2", which collides with Round 1's Lemma Q.2 (descent to the report carrier). The purity lemma is labeled **Lemma Q.3** here. Three statements in the prompt are corrected below: the strictness clause of the purity lemma (§1.2), the off-by-one in the exhaustion bound (§1.5), and the scope of "cannot evaluate $S$ internally" (§2.2).

---

## 1. CPTP Purity Dissipation and Lift Budgeting

### 1.1 Setup

A CPTP channel $\mathcal{E}:\mathcal{L}(\mathcal{H})\to\mathcal{L}(\mathcal{H})$ has Kraus form $\mathcal{E}(\rho)=\sum_j A_j\rho A_j^\dagger$, $\sum_j A_j^\dagger A_j=I$. It is **unital** iff $\mathcal{E}(I)=I$, i.e. $\sum_j A_jA_j^\dagger=I$. Quadratic purity: $P_2(\rho)=\operatorname{Tr}\rho^2=\sum_i\lambda_i^2$ where $\lambda(\rho)$ is the spectrum. Von Neumann entropy in bits: $S(\rho)=-\sum_i\lambda_i\log_2\lambda_i$; in nats, $S_e=S\ln 2$.

**Lemma 1.1 (Doubly stochastic spectral transfer).** Let $\mathcal{E}$ be unital and trace-preserving, $\rho=\sum_i\lambda_i|i\rangle\langle i|$, $\mathcal{E}(\rho)=\sum_j\mu_j|j'\rangle\langle j'|$ (spectral decompositions). Define $D_{ji}=\langle j'|\mathcal{E}(|i\rangle\langle i|)|j'\rangle$. Then $D\ge 0$ entrywise, $D$ is doubly stochastic, and $\mu=D\lambda$.

*Proof.* $D_{ji}\ge0$ because $\mathcal{E}$ is positive. Row sums: $\sum_iD_{ji}=\langle j'|\mathcal{E}(I)|j'\rangle=1$ (unital). Column sums: $\sum_jD_{ji}=\operatorname{Tr}\mathcal{E}(|i\rangle\langle i|)=1$ (TP). Finally $\mu_j=\langle j'|\mathcal{E}(\rho)|j'\rangle=\sum_i\lambda_iD_{ji}$ by linearity. $\square$

### 1.2 Lemma Q.3 (Purity Dissipation under unital channels)

**Lemma Q.3.** For unital TP $\mathcal{E}$ and any $\rho\in\mathcal{S}_Q$:
$$P_2(\mathcal{E}(\rho))\le P_2(\rho),\qquad S(\mathcal{E}(\rho))\ge S(\rho),$$
with equality in either inequality iff $\lambda(\mathcal{E}(\rho))$ and $\lambda(\rho)$ coincide as multisets.

*Proof.* By Lemma 1.1, $\mu_j=\sum_iD_{ji}\lambda_i$ is a convex combination of the $\lambda_i$. For any convex $f$, Jensen gives $f(\mu_j)\le\sum_iD_{ji}f(\lambda_i)$; summing over $j$ and using column-stochasticity, $\sum_jf(\mu_j)\le\sum_if(\lambda_i)$. Take $f(x)=x^2$ for purity and $f(x)=x\log_2x$ (with $0\log 0=0$) for entropy; both are strictly convex on $[0,1]$. Equality in the summed inequality forces equality in every Jensen step, i.e. for each $j$ the values $\{\lambda_i:D_{ji}>0\}$ are all equal, so each $\mu_j$ equals some $\lambda_i$; combined with the symmetric argument on the doubly stochastic $D$ (the sum $\sum_j f(\mu_j) = \sum_i f(\lambda_i)$ for all strictly convex $f$ characterizes equal multisets), the spectra coincide. Conversely equal spectra give equal $P_2$ and $S$ trivially. $\square$

**Correction to the prompt's strictness clause.** "Strictly decreasing unless $\mathcal{E}$ is unitary on the support of $\rho$" is false in this model. Counterexample: the $Z$-dephasing channel $\mathcal{E}(\rho)=\tfrac12(\rho+Z\rho Z)$ is unital, non-unitary on every nonzero support, and fixes $\rho=\operatorname{diag}(3/5,2/5)$ with $P_2=13/25$ unchanged. The correct equality condition is spectral coincidence (Lemma Q.3). The prompt's clause is routed $\mathsf{rejected}$; the corrected clause is used below.

**Corollary 1.2.** Along any trajectory $\rho_{k+1}=\mathcal{E}_k(\rho_k)$ with every $\mathcal{E}_k$ unital, $P_2(\rho_k)$ is non-increasing and $S(\rho_k)$ is non-decreasing. Hence no unital trajectory realizes a strict-improvement certificate ordered by increasing purity or decreasing entropy, at any step. (Note $P_2(\rho)=\operatorname{Tr}\rho^2\in K$ whenever $\rho\in K^{d\times d}$, so this monotone is carrier-internal; see §2.4.)

### 1.3 Non-unital purification and the entropic cost

Non-unital channels can increase purity (amplitude damping maps every qubit state to $|0\rangle\langle0|$ at $\gamma=1$). Every CPTP channel has a Stinespring dilation
$$\mathcal{E}(\rho)=\operatorname{Tr}_A\!\left[U(\rho\otimes|0\rangle\langle0|_A)U^\dagger\right],\qquad \dim\mathcal{H}_A=d_A ,$$
with a pure ancilla. The following bound quantifies what the ancilla can absorb.

**Lemma 1.3 (Per-step entropy reduction bound).** For $\mathcal{E}$ as above, $S(\mathcal{E}(\rho))\ge S(\rho)-\log_2d_A$.

*Proof.* Let $\omega=U(\rho\otimes|0\rangle\langle0|)U^\dagger$ on $\mathcal{H}\otimes\mathcal{H}_A$; $S(\omega)=S(\rho)$ (unitary invariance, pure ancilla adds nothing). Araki–Lieb: $S(\omega_{\mathcal{H}})\ge S(\omega)-S(\omega_A)$. Since $\omega_{\mathcal{H}}=\mathcal{E}(\rho)$ and $S(\omega_A)\le\log_2d_A$, the bound follows. $\square$

So each fresh ancilla qubit ($d_A=2$) can remove at most one bit of entropy from the system, and the bit it absorbs must eventually be erased (Landauer, $k_BT\ln2$ per bit) or the ancilla is not fresh again. This is the thermodynamic reading of the lift budget; the bound used in Theorem Q.2 is the information-theoretic one (Lemma 1.3), not a thermodynamic one.

### 1.4 Declared lift-budget model (Axiom FV2 instance)

**Assumption (A-LIFT).**
1. The agent holds an integer budget $B_k\in\mathbb{Z}_{\ge0}$ of fresh ancilla qubits at step $k$, with $B_1=B_0$.
2. Internal (R2) transitions that consume no budget are unital channels on $\mathcal{H}$.
3. A **purification step** is a transition $\rho_{k+1}=\mathcal{E}_k(\rho_k)$ with $S(\rho_{k+1})<S(\rho_k)$. It is realized by a Stinespring dilation with $a_k\ge1$ fresh ancilla qubits, and the budget decrements $B_{k+1}=B_k-a_k<B_k$.
4. There is no ancilla re-preparation inside the trajectory (re-preparation is an external lift, counted in $B_0$).

Item 2 is a modeling choice: it identifies "no fresh resource" with "unital". Lemma Q.3 shows that under this choice entropy never decreases without budget, so items 2–3 are consistent. Projective measurement with feedback is not an exception: averaging over outcomes gives a unital (pinching) map; using the outcome requires a stored classical record, which is a one-bit ancilla and is charged to the budget.

### 1.5 Theorem Q.2 (Purity Lift Exhaustion)

**Theorem Q.2.** Under (A-LIFT), along any trajectory $(\rho_k)$ with every step a purification step:
(a) at most $B_0$ purification steps occur, so the $(B_0+1)$-th purification attempt is obstructed; the trajectory routes to `LIFT_BUDGET_EXHAUSTION` at $k^*\le B_0+1$;
(b) the total entropy removed satisfies $S(\rho_1)-S(\rho_{k^*})\le B_0$ bits, independently of how the budget is partitioned among steps;
(c) if the trajectory also carries a Round-1 report-grounded strict-improvement claim, the certificate fails by $\min\{B_0+1,\ N+1\}$, where $N=|\operatorname{report}(\mathcal{S}_Q)|$.

*Proof.* (a) $B_k$ is a non-negative integer, strictly decreasing on purification steps. After $m$ purification steps, $B\le B_0-m$, so $m\le B_0$; with $B=0$ no ancilla is available and (A-LIFT.2) leaves only unital maps, which by Lemma Q.3 cannot decrease $S$. (b) Lemma 1.3 at each step gives $S(\rho_k)-S(\rho_{k+1})\le a_k$; telescoping, $S(\rho_1)-S(\rho_{k^*})\le\sum_ka_k\le B_0$. (c) Both obstructions are independent; the earlier one applies. $\square$

**Off-by-one note.** The prompt writes $k^*\le B_0$. With Round 1's convention ($k^*$ = index of the obstructed step, so $k^*=N+1$ for report collision), the matching bound is $k^*\le B_0+1$; the count of *completed* purification steps is $\le B_0$. Both are recorded in the JSON block.

**Remark (Goodhart layer).** An internal counter $\mu(\rho_k)=k$ or a numerical "purification progress" proxy continues to increase through unital steps that leave $S$ unchanged or increase it; by Corollary 1.2 such increments carry no entropy reduction and route to $\mathsf{evidence\_only}$.

### 1.6 Explicit ancilla example: Werner state, depolarizing, amplitude damping ($B_0=2$)

Werner family $\rho_W(p)=p|\Psi^-\rangle\langle\Psi^-|+(1-p)\tfrac{I}{4}$, spectrum $\{\tfrac{1+3p}{4},\tfrac{1-p}{4}^{\times3}\}$, so
$$P_2(\rho_W(p))=\frac{(1+3p)^2+3(1-p)^2}{16}=\frac{1+3p^2}{4}.$$

Channels used: single-qubit depolarizing $\mathcal{D}_\lambda(\sigma)=\lambda\sigma+(1-\lambda)\tfrac{I}{2}$ (unital; on one qubit of a Werner state, $p\mapsto\lambda p$); amplitude damping $\mathcal{A}_\gamma$ with Kraus $A_0=\operatorname{diag}(1,\sqrt{1-\gamma})$, $A_1=\sqrt{\gamma}\,|0\rangle\langle1|$ (non-unital; $\mathcal{A}_1(\sigma)=|0\rangle\langle0|$ for every $\sigma$).

| $k$ | Transition | $\rho_{k+1}$ | Spectrum | $P_2$ | $S$ (bits) | $B$ | Step type |
|---|---|---|---|---|---|---|---|
| 1 | — | $\rho_W(1)=|\Psi^-\rangle\langle\Psi^-|$ | $\{1,0,0,0\}$ | $1$ | $0$ | $2$ | start |
| 2 | $\mathcal{D}_{1/2}\otimes\mathrm{id}$ | $\rho_W(1/2)$ | $\{5/8,1/8,1/8,1/8\}$ | $7/16$ | $\tfrac58\log_2\tfrac85+\tfrac98\approx1.549$ | $2$ | unital, no cost |
| 3 | $\mathrm{id}\otimes\mathcal{A}_1$ | $\tfrac{I}{2}\otimes|0\rangle\langle0|$ | $\{1/2,1/2,0,0\}$ | $1/2$ | $1$ | $1$ | purification, $-1$ |
| 4 | $\mathcal{A}_1\otimes\mathrm{id}$ | $|00\rangle\langle00|$ | $\{1,0,0,0\}$ | $1$ | $0$ | $0$ | purification, $-1$ |
| 5 | any non-unital | — | — | — | — | $0$ | **obstructed** |

Checks: step 2 decreases purity $1\to7/16$ and raises entropy, consistent with Lemma Q.3. Step 3: $\operatorname{Tr}_2\rho_W(1/2)=I/2$, so $\mathcal{A}_1$ on qubit 2 yields $\tfrac I2\otimes|0\rangle\langle0|$; entropy removed $\approx0.549<1$ bit, within Lemma 1.3. Step 4 removes exactly $1$ bit, saturating Lemma 1.3. Total removed $1.549\le B_0=2$ (Theorem Q.2(b)). The fifth step would be the third purification attempt with $B=0$: `LIFT_BUDGET_EXHAUSTION` at $k^*=5=B_0+3$ here because the trajectory contains one non-purifying step; counting purification steps only, exhaustion at the $(B_0+1)=3$rd attempt.

Intermediate $\gamma$ for reference: $\mathcal{A}_\gamma$ on qubit 2 of $|\Psi^-\rangle$ gives spectrum $\{\tfrac{2-\gamma}{2},\tfrac{\gamma}{2}\}$, $P_2=1-\gamma+\tfrac{\gamma^2}{2}$, which first *decreases* (the ancilla absorbs entanglement before it absorbs entropy) — a non-unital step is not automatically a purification step; (A-LIFT.3) charges the budget only when $S$ strictly drops.

---

## 2. The Baker Transcendental Entropy Boundary

### 2.1 Input facts (cited, not re-derived)

**Baker (homogeneous form).** Let $\alpha_1,\dots,\alpha_n$ be nonzero algebraic numbers. If $\ln\alpha_1,\dots,\ln\alpha_n$ are linearly independent over $\mathbb{Q}$, then $1,\ln\alpha_1,\dots,\ln\alpha_n$ are linearly independent over $\overline{\mathbb{Q}}$.

**Consequence used (B*).** For nonzero algebraic $\alpha_i$ and algebraic $\beta_i$ (not all zero), $\Lambda=\sum_i\beta_i\ln\alpha_i$ is either $0$ or transcendental; and $\Lambda=0$ iff the vector $(\beta_i)$ lies in the $\overline{\mathbb{Q}}$-span of the integer relation lattice $\{m\in\mathbb{Z}^n:\prod_i\alpha_i^{m_i}=1\}$.
*Derivation from Baker:* choose a maximal $\mathbb{Q}$-independent subset of the logs, write every $\ln\alpha_i$ as a rational combination of it, substitute; any $\overline{\mathbb{Q}}$-relation (including one with a nonzero constant term, which is where "$\Lambda$ algebraic $\Rightarrow$ relation with constant $1$" enters) must have all basis coefficients zero.

### 2.2 Theorem Q.2.1 (Transcendental Entropy Decoupling)

Let $\rho$ have real algebraic spectrum $\{p_1,\dots,p_r\}$, $p_i>0$, $r=\operatorname{rank}\rho\ge2$. (If $\rho\in K^{d\times d}$ with $K=\mathbb{Q}(\zeta_n)$, eigenvalues lie in a finite extension of $K$, hence are algebraic; they need not lie in $K$ itself.)

**Theorem Q.2.1.**
1. $S_e(\rho)=-\sum_ip_i\ln p_i$ is transcendental; in particular $S_e(\rho)\notin K$, and no element of $K$ equals $S_e(\rho)$. Base-2 entropy $S(\rho)=S_e(\rho)/\ln2$ is transcendental unless $(p_1,\dots,p_r,S(\rho))$ lies in the $\overline{\mathbb{Q}}$-span of the integer relation lattice of $\{p_1,\dots,p_r,2\}$ (§3 gives the dyadic case).
2. Any carrier-internal proxy $\tilde S:\mathcal{S}_K\to\mathbb{Q}$ differs from $S_e$ on every rank $\ge2$ state. A proxy obtained by fixed-order truncation of $\ln$ can order pairs of states oppositely to $S_e$ (explicit witness below); a proxy obtained by rounding to a $2^{-k}$ grid is non-strictly monotone and takes at most $\lceil2^k\log_2d\rceil+1$ values on $\mathcal{S}_Q$, so a strict-improvement certificate ordered by it fails by Round 1's Theorem Q.1 with $N\le\lceil2^k\log_2d\rceil+1$.
3. Exact carrier-internal tracking is available through (P4) integer-order power sums $P_m(\rho)=\operatorname{Tr}\rho^m\in K$, $m\ge2$, and (P3) certified rational enclosures $[L_k,U_k]\ni S_e(\rho)$ with $U_k-L_k\le2^{-k}$, computable by exact rational arithmetic when the spectrum is rational (algebraic spectra require enclosures of the eigenvalues first; deferred).

*Proof.*
(1) $S_e=\sum_i\beta_i\ln\alpha_i$ with $\alpha_i=p_i$ algebraic nonzero and $\beta_i=-p_i$ algebraic nonzero. Since $0<p_i<1$ for $r\ge2$, each term $-p_i\ln p_i>0$, so $S_e>0\neq0$. By (B*), $S_e$ is transcendental over $\mathbb{Q}$, hence over $K$ (an element algebraic over $K$ is algebraic over $\mathbb{Q}$). For base 2: $S$ algebraic, say $S=\gamma$, means $\sum_ip_i\ln p_i+\gamma\ln2=0$, a vanishing linear form in $\ln p_1,\dots,\ln p_r,\ln2$ with algebraic coefficients $(p_1,\dots,p_r,\gamma)$; (B*) gives the stated lattice condition.
(2) First claim: $\tilde S(\rho)\in\mathbb{Q}\subset\overline{\mathbb{Q}}$ while $S_e(\rho)\notin\overline{\mathbb{Q}}$. Order-inversion witness (first-order truncation $\ln p\approx p-1$ gives $\tilde S_1(\rho)=\sum_ip_i(1-p_i)=1-P_2(\rho)$):
   - $\rho_a=\operatorname{diag}(1/2,1/2,0)$: $\tilde S_1=1/2$, $S_e=\ln2\approx0.6931$.
   - $\rho_b=\operatorname{diag}(7/10,3/20,3/20)$: $\tilde S_1=1-\tfrac{214}{400}=\tfrac{93}{200}=0.465$, $S_e=\tfrac7{10}\ln\tfrac{10}{7}+\tfrac3{10}\ln\tfrac{20}{3}\approx0.2497+0.5691=0.8188$.
   So $\tilde S_1(\rho_a)>\tilde S_1(\rho_b)$ while $S_e(\rho_a)<S_e(\rho_b)$: optimizing $\tilde S_1$ in the direction $\rho_b\to\rho_a$ is certified as entropy *reduction* by the proxy and is entropy *increase* in fact. Rounding claim: $\lfloor2^kS\rfloor$ with $S\in[0,\log_2d]$ takes at most $\lceil2^k\log_2d\rceil+1$ integer values; apply Theorem Q.1 with $\operatorname{report}=\lfloor2^kS\rfloor$.
(3) $P_m(\rho)$ is a polynomial in the matrix entries of $\rho$ with integer coefficients, hence in $K$. Enclosures: §2.3 exhibits the construction; correctness rests on the exact tail bound of the series. $\square$

**Scope correction.** The prompt's clause "cannot evaluate $S(\rho)$ internally" is supported only in the sense "cannot represent $S(\rho)$ as an element of $K$". The carrier can represent $S(\rho)$ *as a certified interval* with rational endpoints (part 3), which is an internal evaluation in the R2 sense. The narrower claim is the one routed $\mathsf{authorized}$.

### 2.3 Certified interval example: $S_e(\operatorname{diag}(3/5,2/5))$

Target: $S_e=\tfrac35\ln\tfrac53+\tfrac25\ln\tfrac52$ (nats).

**Tool.** For $0<x<1$, $\ln\frac{1+x}{1-x}=2\sum_{k\ge0}\frac{x^{2k+1}}{2k+1}$; truncating after $k=n$ gives partial sum $L_n(x)$ and tail $0<T_n(x)\le\frac{2x^{2n+3}}{(2n+3)(1-x^2)}$ (geometric bound, all terms positive). So $\ln\frac{1+x}{1-x}\in[L_n(x),\,L_n(x)+\bar T_n(x)]$ with rational endpoints.

**$\ln(5/3)$, $x=1/4$, $n=2$.**
$L_2=2\left(\tfrac14+\tfrac1{192}+\tfrac1{5120}\right)=2\cdot\tfrac{3923}{15360}=\tfrac{3923}{7680}$.
$\bar T_2=\tfrac{2(1/4)^7}{7\cdot15/16}=\tfrac1{53760}$.
Enclosure: $\ln\tfrac53\in\left[\tfrac{3923}{7680},\ \tfrac{13731}{26880}\right]\approx[0.5108073,\ 0.5108259]$.

**$\ln(5/2)$, $x=3/7$, $n=4$.** Common denominator $5\cdot7^9=201768035$:
$\tfrac37=\tfrac{86472015}{\cdot}$, $\tfrac{9}{343}=\tfrac{5294205}{\cdot}$, $\tfrac{243}{84035}=\tfrac{583443}{\cdot}$, $\tfrac{2187}{5764801}=\tfrac{76545}{\cdot}$, $\tfrac{2187}{40353607}=\tfrac{10935}{\cdot}$; sum $=\tfrac{92437143}{201768035}$.
$L_4=\tfrac{184874286}{201768035}\approx0.9162714$.
$\bar T_4=\tfrac{2(3/7)^{11}}{11\cdot40/49}=\tfrac{177147}{8877793540}\approx1.9954\times10^{-5}$.
Enclosure: $\ln\tfrac52\in\left[\tfrac{184874286}{201768035},\ \tfrac{184874286}{201768035}+\tfrac{177147}{8877793540}\right]\approx[0.9162714,\ 0.9162914]$.

**Combine.** $L=\tfrac35L_2(\tfrac14)+\tfrac25L_4(\tfrac37)=\tfrac{3923}{12800}+\tfrac{369748572}{1008840175}=\tfrac{13904738765}{20661046784}$.
$U=L+\tfrac35\bar T_2+\tfrac25\bar T_4=L+\tfrac1{89600}+\tfrac{177147}{22194483850}=\tfrac{1911955961409}{2840893932800}$.
$$S_e(\operatorname{diag}(3/5,2/5))\in[L,U]=\left[\tfrac{13904738765}{20661046784},\ \tfrac{1911955961409}{2840893932800}\right]\approx[0.6729929,\ 0.6730121],$$
$$U-L=\tfrac{108762443}{5681787865600}\approx1.914\times10^{-5}<2^{-15}.$$
Decimal sanity check (not part of the certificate): $S_e\approx0.6730117$, inside. Every endpoint is an explicit rational produced by integer arithmetic; no floating-point value enters the enclosure. Baker (Theorem Q.2.1(1)) applies: $\ln\tfrac53,\ln\tfrac52,\ln2$ have trivial integer relation lattice ($3^a2^{b+c}5^{-a-b}=1\Rightarrow a=b=c=0$), so both $S_e$ and $S$ of this state are transcendental, and $[L,U]$ is the only kind of carrier-internal object that can hold the value.

### 2.4 Rényi power sums as exact monotones

For $\rho\in K^{d\times d}$, $P_2(\rho)\in K$ exactly, and by Lemma Q.3 it is a non-increasing monotone under unital steps. The Rényi-2 entropy $-\log_2P_2$ is again a logarithm of an algebraic number and is transcendental unless $P_2$ is a rational power of $2$; so the carrier-internal object is $P_2$ itself, not $-\log_2P_2$. Note from §2.2(2) that $P_2$ and $S_e$ induce different orders on $\mathcal{S}_Q$: $P_2$ is a legitimate exact monotone, not an exact entropy.

---

## 3. Dyadic Entropy Subsector (P2)

**Proposition 3.1.** If the spectrum is dyadic, $p_i=2^{-a_i}$ with $a_i\in\mathbb{Z}_{\ge0}$ (so $\sum_i2^{-a_i}=1$), then $S(\rho)=\sum_ia_i2^{-a_i}\in\mathbb{Q}$.

*Proof.* $-\log_2p_i=a_i$. $\square$

Examples: $\{\tfrac12,\tfrac12\}\mapsto S=1$; $\{\tfrac12,\tfrac14,\tfrac14\}\mapsto S=\tfrac32$; $\{\tfrac12,\tfrac14,\tfrac18,\tfrac18\}\mapsto S=\tfrac74$. In each case $S_e=S\ln2$ remains transcendental.

**Scope boundary.** By Theorem Q.2.1(1), for algebraic spectrum $S(\rho)$ is algebraic iff $(p_1,\dots,p_r,S)$ lies in the $\overline{\mathbb{Q}}$-span of the integer relation lattice of $\{p_1,\dots,p_r,2\}$. The dyadic case realizes this with relations $\ln p_i+a_i\ln2=0$. It does not extend to generic algebraic spectra: for $\{\tfrac13,\tfrac23\}$ the lattice is spanned by $(1,-1,1)$ and $(\tfrac13,\tfrac23,\gamma)$ is not a multiple of it, so $S(\tfrac13,\tfrac23)$ is transcendental; for $\{\tfrac35,\tfrac25\}$ the lattice is trivial (§2.3). Rationality of base-2 entropy is a measure-zero exception, not a route around the Baker boundary.

---

## 4. Epistemic Routing (PG3)

| Item | Terminal | Grounds |
|---|---|---|
| Lemma 1.1, Lemma Q.3 (inequalities and equality condition) | $\mathsf{authorized}$ | proved from doubly stochastic transfer + strict convexity |
| Prompt clause "strict unless unitary on support" | $\mathsf{rejected}$ | dephasing counterexample |
| Lemma 1.3 (Araki–Lieb step bound) | $\mathsf{authorized}$ | proved from cited Araki–Lieb |
| (A-LIFT) | $\mathsf{authorized}$ (as declared assumption) | modeling choice; consistency shown via Lemma Q.3 |
| Theorem Q.2 (a)(b)(c) | $\mathsf{authorized}$ under (A-LIFT) | proved; bound $k^*\le B_0+1$ (prompt's $\le B_0$ counts completed steps) |
| Landauer thermodynamic reading | $\mathsf{evidence\_only}$ | interpretive; not used in any proof |
| Theorem Q.2.1(1) transcendence | $\mathsf{authorized}$ conditional on cited Baker theorem | reduction to (B*) shown; Baker not re-derived |
| Theorem Q.2.1(2) proxy inversion witness | $\mathsf{authorized}$ | exact rational/closed-form check |
| Theorem Q.2.1(3) P3/P4 | $\mathsf{authorized}$ for rational spectra | §2.3 enclosure; algebraic-eigenvalue enclosures $\mathsf{unresolved}$ |
| Prompt clause "cannot evaluate $S$ internally" | $\mathsf{not\_admitted}$ as stated | narrowed to "cannot represent in $K$" |
| Proposition 3.1 and scope boundary | $\mathsf{authorized}$ | proved / follows from (B*) |
| Hand arithmetic in §2.3 | $\mathsf{evidence\_only}$ until machine-checked | decimals agree; no tool ran |

---

## 5. Claim Hygiene Summary

- **Supported:** In this model, unital channels never increase purity or decrease entropy (with equality iff spectra coincide); each fresh ancilla qubit removes at most one bit; under (A-LIFT) a purification-only trajectory is obstructed at the $(B_0+1)$-th attempt and removes at most $B_0$ bits in total; for algebraic spectra of rank $\ge2$, $S_e$ is transcendental (conditional on Baker) and so cannot be an element of $K$; a first-order truncated proxy order-inverts relative to $S_e$ on an explicit pair; a $2^{-15}$ rational enclosure of $S_e(\operatorname{diag}(3/5,2/5))$ was constructed by exact arithmetic; base-2 entropy is rational on dyadic spectra and the exception is characterized by a lattice condition.
- **Not supported:** the prompt's "strict unless unitary" clause; that purification is blocked without ancilla *in general* (it is blocked under the declared identification of budget-free with unital); any thermodynamic (Landauer) bound as a theorem of this round; that the agent "cannot evaluate" entropy in the interval sense; Theorem Q.2.1 for eigenvalues given only as algebraic numbers without enclosures; machine-checked status of the §2.3 rationals.
- **Narrowest defensible claim:** Under (A-LIFT), a self-modifying trajectory whose improvement claim is "entropy decreased" can be certified at most $B_0$ times, and an agent confined to an algebraic carrier can certify such decreases only through $K$-valued power sums or rational interval enclosures, never through an exact carrier value of $S$.
- **Next check:** (i) verify the §2.3 rationals by exact arithmetic (Rust `num-rational` or Lean `Rat`), including $\sum_i p_i=1$, $L<U$, $U-L<2^{-15}$, and containment against a high-precision $\ln$; (ii) check Lemma Q.3's equality condition on the dephasing counterexample numerically; (iii) encode Theorem Q.2(a) as a strictly decreasing `ℕ`-valued measure (`WellFounded` on `Nat.lt`) with the step count bound.

```json
{
  "campaign_id": "FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION",
  "round": 2,
  "status": "VERIFIED_LOCAL_RESULT",
  "status_meaning": "hand-derived in this response; no Lean/Cargo/solver executed; not machine-checked",
  "derived_theorems": [
    "Lemma_1_1_DoublyStochasticSpectralTransfer",
    "Lemma_Q_3_PurityDissipation_Unital (relabeled from prompt's Lemma Q.2)",
    "Corollary_1_2_UnitalMonotones",
    "Lemma_1_3_ArakiLieb_PerStepEntropyBound",
    "Theorem_Q_2_PurityLiftExhaustion",
    "Theorem_Q_2_1_TranscendentalEntropyDecoupling (conditional on Baker)",
    "Proposition_3_1_DyadicRationality_and_ScopeBoundary"
  ],
  "bounds_established": {
    "purification_steps_completed": "<= B_0",
    "k_star_lift_exhaustion": "<= B_0 + 1 (purification-only trajectory)",
    "total_entropy_removed_bits": "<= B_0 (one bit per fresh ancilla qubit)",
    "combined_with_round1": "min(B_0 + 1, N + 1)",
    "rounded_proxy_report_values": "<= ceil(2^k * log2 d) + 1",
    "werner_example_B0": 2,
    "werner_example_entropy_removed_bits": 1.549,
    "entropy_enclosure_diag_3_5_2_5": {
      "L": "13904738765/20661046784",
      "U": "1911955961409/2840893932800",
      "width": "108762443/5681787865600 (< 2^-15)"
    }
  },
  "corrections_to_prompt": [
    "Purity strictness: equality iff spectra coincide, not 'unless unitary on support' (dephasing counterexample).",
    "Exhaustion index: k* <= B_0 + 1 under Round 1's indexing; <= B_0 counts completed purification steps.",
    "'Cannot evaluate S internally' narrowed to 'cannot represent S as an element of K'; interval evaluation is internal.",
    "Lemma numbering: purity lemma relabeled Q.3 to avoid collision with Round 1 Lemma Q.2."
  ],
  "unresolved_obligations": [
    "Round 3: certified enclosures for entropy when eigenvalues are algebraic but not rational (eigenvalue interval isolation over K).",
    "Round 3: justify or replace (A-LIFT.2) — characterize which non-unital channels require a fresh (low-entropy) ancilla versus an equilibrium environment.",
    "Round 3: combine report-collision (Round 1) and lift-exhaustion (Round 2) into a single joint horizon with external-lift accounting for stabilizer-orbit escape (carried from Round 1).",
    "Round 3: stochastic single-shot reports (carried from Round 1).",
    "Round 3: F2/F4 senses of finiteness (cyclotomic carrier arithmetic, finite-field scalar models) still unused.",
    "Tooling: exact-rational check of section 2.3; Lean encoding of Theorem Q.2(a) as a well-founded descent on Nat; Lean encoding of Theorem Q.1 (carried)."
  ],
  "claim_hygiene": {
    "supported": "Unital channels are purity-non-increasing/entropy-non-decreasing with equality iff equal spectra; one bit per fresh ancilla qubit; at most B_0 certified purifications under (A-LIFT); S_e transcendental for algebraic rank>=2 spectra conditional on Baker; explicit proxy order inversion; exact rational 2^-15 enclosure of S_e(diag(3/5,2/5)); dyadic base-2 rationality with lattice-characterized scope.",
    "not_supported": "Prompt's 'strict unless unitary' clause; purification blocked without ancilla outside (A-LIFT); Landauer as a theorem here; 'cannot evaluate S' beyond non-representability in K; algebraic-eigenvalue enclosures; machine-checked arithmetic.",
    "narrowest_claim": "Under (A-LIFT), an entropy-decrease improvement claim can be certified at most B_0 times along a trajectory, and on an algebraic carrier such certification can only go through K-valued power sums or rational interval enclosures, never an exact carrier value of S.",
    "next_check": "Exact-rational verification of the section 2.3 enclosure (endpoints, width < 2^-15, containment vs high-precision ln); numeric check of the dephasing equality case; Lean well-founded-descent encoding of Theorem Q.2(a)."
  }
}
```