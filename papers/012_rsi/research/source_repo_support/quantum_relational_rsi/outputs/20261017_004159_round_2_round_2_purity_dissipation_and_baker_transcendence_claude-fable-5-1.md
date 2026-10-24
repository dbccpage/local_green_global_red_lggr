# Output: round_2_purity_dissipation_and_baker_transcendence.md

- **Timestamp:** 2026-10-17T00:41:59.397609
- **Model:** claude-fable-5-1
- **Round:** 2
- **Duration:** 308.0s
- **Tokens:** In=18783, Out=26752
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_2_purity_dissipation_and_baker_transcendence.md`
- **Continued From:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\outputs\20261017_000730_round_1_quantum_relational_axioms_and_povm_finitude_claude-fable-5-1.md`

---

## Thinking Trace

```text

```

---

## Response Content

# Round 2 Record — CPTP Purity Dissipation, Lift Budget Exhaustion, Baker Transcendence Boundary

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 2/4**
**Execution note:** No Lean, Cargo, or solver ran. All arithmetic below was done by hand in exact rationals; decimal values are annotations marked "≈", not computational receipts. Round 1 results are referenced by label only and are not treated as external verification.

**Numbering note.** Round 1 already assigned "Lemma Q.2" to the descent lemma (report-grounded dominance descends to a strict partial order on the report carrier). The prompt's "Lemma Q.2 (Purity Dissipation)" is therefore recorded here as **Lemma Q.3**. Theorem Q.2 and Theorem Q.2.1 keep the prompt's labels.

---

## 1. Purity Dissipation Under Unital Channels

### 1.1 Setting

$\mathcal{E}:\mathcal{L}(\mathcal{H})\to\mathcal{L}(\mathcal{H})$ with Kraus form $\mathcal{E}(X)=\sum_j A_jXA_j^\dagger$, $\sum_j A_j^\dagger A_j=I$ (CPTP). $\mathcal{E}$ is **unital** iff $\mathcal{E}(I)=I$, i.e. $\sum_j A_jA_j^\dagger=I$. Quadratic purity $P_2(\rho)=\operatorname{Tr}(\rho^2)\in[1/d,1]$.

**Fact K-S (Kadison–Schwarz, cited not re-derived).** For a unital 2-positive map $\Phi$ and any Hermitian $X$, $\Phi(X)^2\le\Phi(X^2)$ in the operator order. CP maps are 2-positive, so this applies to unital CPTP $\mathcal{E}$.

### 1.2 Lemma Q.3 (Purity Dissipation)

**Lemma Q.3.** If $\mathcal{E}$ is unital CPTP, then $P_2(\mathcal{E}(\rho))\le P_2(\rho)$ for all $\rho\in\mathcal{S}_Q$. Equality holds iff $\mathcal{E}(\rho)^2=\mathcal{E}(\rho^2)$.

*Proof.*
1. By Fact K-S with $X=\rho$: $\mathcal{E}(\rho^2)-\mathcal{E}(\rho)^2\ge 0$.
2. Taking the trace of a positive operator gives a non-negative number: $\operatorname{Tr}\mathcal{E}(\rho^2)-\operatorname{Tr}\mathcal{E}(\rho)^2\ge 0$.
3. Trace preservation: $\operatorname{Tr}\mathcal{E}(\rho^2)=\operatorname{Tr}\rho^2=P_2(\rho)$. Hence $P_2(\mathcal{E}(\rho))=\operatorname{Tr}\mathcal{E}(\rho)^2\le P_2(\rho)$.
4. Equality case: a positive operator has zero trace iff it is zero, so equality iff $\mathcal{E}(\rho^2)=\mathcal{E}(\rho)^2$. $\square$

**Correction to the prompt's strictness clause.** The prompt states purity is "strictly decreasing unless $\mathcal{E}$ is unitary on the support of $\rho$." This is not the equality condition. Two counter-witnesses:

- $\rho=I/2$ on a qubit, $\mathcal{E}$ = complete depolarizing (unital, not unitary anywhere): $P_2$ stays $1/2$.
- $\rho=\lvert0\rangle\langle0\rvert$, $\mathcal{E}$ = $Z$-dephasing $\rho\mapsto\tfrac12(\rho+Z\rho Z)$: $P_2$ stays $1$, and $\mathcal{E}$ is not a unitary channel.

The correct statement is the one in Lemma Q.3: equality iff $\mathcal{E}(\rho)^2=\mathcal{E}(\rho^2)$. Unitarity is a sufficient condition, not necessary. The prompt's clause is routed $\mathsf{rejected}$; sufficient condition $\mathsf{authorized}$.

**Remark (stronger monotone, cited).** Unital CPTP maps send $\operatorname{spec}(\rho)$ to a vector majorized by it (Uhlmann's theorem for doubly-stochastic quantum maps). Consequently every Schur-concave functional — all Rényi entropies $S_\alpha$, von Neumann $S$, and all $P_m$ in the reverse direction — is monotone under unital channels. Only $P_2$ is used in the proofs below; the majorization statement is routed $\mathsf{evidence\_only}$.

**Non-unital channels can increase purity.** Amplitude damping $\mathcal{A}_\gamma$ (Kraus $A_0=\lvert0\rangle\langle0\rvert+\sqrt{1-\gamma}\lvert1\rangle\langle1\rvert$, $A_1=\sqrt\gamma\lvert0\rangle\langle1\rvert$) is not unital ($\mathcal{A}_\gamma(I)=\operatorname{diag}(1+\gamma,1-\gamma)$) and sends $I/2\mapsto\operatorname{diag}(\tfrac{1+\gamma}{2},\tfrac{1-\gamma}{2})$, raising $P_2$ from $\tfrac12$ to $\tfrac{1+\gamma^2}{2}$. This is exactly the behaviour the budget model must price.

---

## 2. Lift Budget Model and Theorem Q.2

### 2.1 Internal vs. lift transitions (declared model)

**Assumption (A-ENV).** The agent's system register $\mathcal{H}$ has fixed dimension. Every transition is a Stinespring dilation $\rho\mapsto\operatorname{Tr}_E[U(\rho\otimes\omega_E)U^\dagger]$; after the step the environment factor $E$ is inaccessible (traced out; R2 closure). Two classes of environment state $\omega_E$:

- **Internal (class $\mathcal{U}$):** $\omega_E=I_E/d_E$ (no free purity available). Then $\mathcal{E}(I)=\operatorname{Tr}_E[U(I\otimes I/d_E)U^\dagger]=I$, so every internal transition is a unital CPTP map. (Converse not needed.)
- **Lift (class $\mathcal{L}$):** $\omega_E$ contains at least one fresh pure qubit $\lvert0\rangle\langle0\rvert$ (or any non-maximally-mixed resource). Resetting a used environment qubit to $\lvert0\rangle$ is itself a lift: by Landauer's bound (cited) it requires a thermal bath at temperature $T$ absorbing $\ge k_BT\ln2$ per bit, and a bath at finite $T$ is a non-maximally-mixed environment, hence class $\mathcal{L}$.

**Assumption (A-LIFT, Axiom FV2 as specified).** The agent starts with $B_0\in\mathbb{N}$ fresh ancilla units. A step in class $\mathcal{L}$ requires $B_k\ge1$ and sets $B_{k+1}=B_k-1$; a step in class $\mathcal{U}$ sets $B_{k+1}=B_k$. So $(B_k)$ is non-increasing, non-negative, and strictly decreases exactly at lift steps. Fractional budgets (partially mixed environments, finite-$T$ baths as effective fractional purity) are not modelled this round.

### 2.2 Theorem Q.2 (Purity Lift Exhaustion)

**Theorem Q.2.** Under (A-ENV), (A-LIFT), let $(\rho_k)_{k\ge1}$ with $\rho_{k+1}=\mathcal{E}_k(\rho_k)$, each $\mathcal{E}_k\in\mathcal{U}\cup\mathcal{L}$. Then:
(a) $\#\{k:\ P_2(\rho_{k+1})>P_2(\rho_k)\}\le B_0$;
(b) any trajectory whose improvement certificate is "strict purity increase at every step" fails by step index $k^*\le B_0+1$; the failing step occurs with $B_{k^*-1}=0$ and is routed `LIFT_BUDGET_EXHAUSTION`;
(c) if the strict dominance $(\succ)$ of Round 1 is both report-grounded and purity-strict (i.e. $\rho\succ\sigma\Rightarrow P_2(\rho)>P_2(\sigma)$), then $k^*\le\min\{N+1,\ B_0+1\}$.

*Proof.*
(a) If $P_2(\rho_{k+1})>P_2(\rho_k)$ then by Lemma Q.3 $\mathcal{E}_k\notin\mathcal{U}$, so $\mathcal{E}_k\in\mathcal{L}$ and $B_{k+1}=B_k-1$. Since $B_k\ge0$ for all $k$, at most $B_0$ decrements occur.
(b) Suppose $P_2(\rho_{k+1})>P_2(\rho_k)$ for all $k\le B_0$. By (a) each of these $B_0$ steps is a lift, so $B_{B_0+1}=0$. Step $B_0+1$ cannot be a lift (A-LIFT), so $\mathcal{E}_{B_0+1}\in\mathcal{U}$ and Lemma Q.3 gives $P_2(\rho_{B_0+2})\le P_2(\rho_{B_0+1})$: the certificate fails at $k^*=B_0+1$ with zero budget. If some earlier step already fails to increase purity, $k^*$ is smaller.
(c) Theorem Q.1 (Round 1) gives $k^*\le N+1$ from the report carrier; (b) gives $k^*\le B_0+1$; both constraints apply simultaneously. $\square$

**Reading of the prompt's "$k^*\le B_0$".** $B_0$ is the maximum number of *licensed* purity-increasing transitions; the first *obstructed* claim has index $B_0+1$. Both numbers are reported.

**What Theorem Q.2 does not say.** A lift step does not by itself raise purity (see §4, $p=0.9$ case); it only removes the Lemma Q.3 obstruction. Nor does the theorem bound the number of unital steps — a trajectory can run forever with non-increasing purity; what terminates is the *strict-improvement certificate*.

---

## 3. Baker Transcendence Boundary

### 3.1 Cited input

**Baker's theorem (qualitative form, cited).** Let $\alpha_1,\dots,\alpha_r$ be nonzero algebraic numbers and $\beta_1,\dots,\beta_r$ algebraic. Then $\Lambda=\sum_i\beta_i\ln\alpha_i$ is either $0$ or transcendental. (Homogeneous corollary: if $\ln\alpha_1,\dots,\ln\alpha_r$ are $\mathbb{Q}$-linearly independent they are $\overline{\mathbb{Q}}$-linearly independent.)

**Hermite–Lindemann (cited).** $e^\alpha$ is transcendental for every nonzero algebraic $\alpha$; hence $\ln\beta$ is transcendental for algebraic $\beta\ne0,1$ (real branch, $\beta>0$).

### 3.2 Boundary Theorem (Paper 006 BT1, restated and proved)

**Theorem B1.** Let $\rho\in\mathcal{S}_Q$ have matrix entries in a number field $K\subset\overline{\mathbb{Q}}$ (in particular $K=\mathbb{Q}(\zeta_n)$). If $\operatorname{rank}\rho\ge2$ then $S(\rho)=-\operatorname{Tr}\rho\ln\rho$ is transcendental; in particular $S(\rho)\notin K$.

*Proof.*
1. The eigenvalues $\lambda_1,\dots,\lambda_r$ ($r=\operatorname{rank}\rho$, zero eigenvalues omitted) are roots of $\det(\rho-\lambda I)\in K[\lambda]$, hence algebraic. (The prompt assumes spectrum in $K$; only algebraicity is needed.)
2. $S(\rho)=\sum_{i=1}^r(-\lambda_i)\ln\lambda_i$ is a linear form in logarithms of the algebraic numbers $\lambda_i$ with algebraic coefficients $-\lambda_i$.
3. Since $r\ge2$ and $\sum\lambda_i=1$, every $\lambda_i\in(0,1)$, so every term $-\lambda_i\ln\lambda_i>0$ and $S(\rho)>0\ne0$.
4. Baker: nonzero $\Rightarrow$ transcendental. Transcendental over $\mathbb{Q}$ implies not in any algebraic field $K$. $\square$

Rank-1 case: $S=0\in K$; the theorem's hypothesis excludes it correctly.

**Base dependence.** $S_b(\rho)=S(\rho)/\ln b$. For $b$ algebraic, $S_b$ is a *ratio* of two linear forms in logarithms and Theorem B1 does not apply directly; this is the opening for the dyadic exception (§3.4).

### 3.3 Theorem Q.2.1 (Transcendental Entropy Decoupling)

**Theorem Q.2.1.** Let the agent's internal scalar carrier be $K=\mathbb{Q}(\zeta_n)$ (or any number field), with exact arithmetic in $K$ only.

**(1) No exact internal evaluation.** For every $\rho$ with entries in $K$ and $\operatorname{rank}\rho\ge2$, there is no $s\in K$ with $s=S(\rho)$.
*Proof.* Theorem B1. $\square$

**(2) Proxy decoupling.** Let $\tilde S:\mathcal{S}_Q\to\mathbb{Q}$ be any proxy with $\lvert\tilde S(\rho)-S(\rho)\rvert\le\varepsilon$ for all $\rho$ and some $\varepsilon>0$. Then:
 (i) there exist $\rho,\sigma$ with $S(\rho)<S(\sigma)$ but $\tilde S(\rho)\ge\tilde S(\sigma)$ — i.e. no $\varepsilon$-accurate proxy is order-faithful;
 (ii) if $\tilde S$ takes finitely many values on the trajectory's reachable set (e.g. fixed-precision rationals, $N_{\tilde S}$ values), Theorem Q.1 applies to the report $\tilde S$ and any strict-$\tilde S$-improvement chain fails by $N_{\tilde S}+1$; a strict-$S$-improvement chain certified only through $\tilde S$ is $\mathsf{not\_admitted}$ once consecutive true gaps fall below $2\varepsilon$.
*Proof of (i).* $S$ is continuous and non-constant on the connected set $\mathcal{S}_Q$, so its image is an interval of positive length; pick $\rho_0$ with $S(\rho_0)$ in the interior and a continuous path $\rho_t$ with $S(\rho_t)$ strictly increasing on $t\in[0,1]$ and $S(\rho_1)-S(\rho_0)<\varepsilon$. Suppose $\tilde S$ were order-faithful on this path; then $t\mapsto\tilde S(\rho_t)$ would be strictly increasing, hence injective on $[0,1]$, hence $\tilde S$ would take uncountably many values on the path. But all these values lie in $[S(\rho_0)-\varepsilon,\ S(\rho_1)+\varepsilon]\cap\mathbb{Q}$, which is countable. Contradiction. (ii) is Theorem Q.1 plus the definition of $\varepsilon$-accuracy. $\square$

**(3) Carrier-internal tracking.** Exact progress tracking inside $K$ is available through either:
 (P4) **Power sums.** $P_m(\rho)=\operatorname{Tr}\rho^m\in K$ for all $m\ge1$ (products and traces of $K$-matrices stay in $K$). The vector $(P_1,\dots,P_d)$ determines $\operatorname{spec}(\rho)$ via Newton's identities, hence determines $S(\rho)$ as a real number, while each $P_m$ is exactly comparable in $K$. Note $S_2=-\ln P_2$ is itself transcendental whenever $P_2\ne1$ (Hermite–Lindemann), so the agent tracks $P_2$, not $S_2$.
 (P3) **Certified rational enclosures.** $[L_k,U_k]\subset\mathbb{Q}$ with $S(\rho)\in[L_k,U_k]$ and $U_k-L_k\le2^{-k}$, produced by series with explicit rational tail bounds (Lemma T below; worked instance in §5). Comparisons $S(\rho)<S(\sigma)$ are decided when enclosures are disjoint; overlapping enclosures route $\mathsf{unresolved}$ pending refinement.
*Proof.* (P4): closure of $K$ under ring operations; Newton identities. (P3): Lemma T. $\square$

**Remark (decidability of entropy order, $\mathsf{evidence\_only}$).** $S(\rho)-S(\sigma)$ is again a linear form in logarithms of algebraic numbers. By Baker's *effective* theorem it is either exactly $0$ or bounded below in absolute value by an explicit (very small) constant depending on heights and degrees. Hence interval refinement terminates in principle: either enclosures separate, or they shrink below the effective bound and equality is certified. Making this a usable procedure is forwarded to Round 3.

### 3.4 Dyadic exception (Proposal P2) and its exact scope

**Example.** $\rho=\operatorname{diag}(\tfrac12,\tfrac12)$: $S_2=1\in\mathbb{Q}$. More generally $\lambda_i=2^{-m_i}$ with $\sum_i2^{-m_i}=1$ gives $S_2=\sum_i m_i2^{-m_i}\in\mathbb{Q}$, e.g. $(\tfrac12,\tfrac14,\tfrac14)\mapsto S_2=\tfrac32$.

**Proposition D (scope boundary).** Let $\lambda_1,\dots,\lambda_r$ be positive algebraic with $\sum\lambda_i=1$, $r\ge2$. Let $G\subset\mathbb{R}_{>0}$ be the multiplicative group generated by $\lambda_1,\dots,\lambda_r,2$ (torsion-free), of rank $s$, with generators $g_1,\dots,g_s$, so $\ln\lambda_i=\sum_jc_{ij}\ln g_j$, $\ln2=\sum_je_j\ln g_j$, $c_{ij},e_j\in\mathbb{Q}$. Then $S_2=-\sum_i\lambda_i\log_2\lambda_i$ is algebraic (equal to $\beta$) iff
$$\sum_i(-\lambda_i)c_{ij}=\beta e_j\quad\text{for every }j=1,\dots,s .$$
In particular: dyadic spectra satisfy this with $s=1$, $g_1=2$; and if the $\lambda_i$ involve any prime not cancelled in the required way, $S_2$ is transcendental.

*Proof.* $S_2=\beta$ iff $\sum_i(-\lambda_i)\ln\lambda_i-\beta\ln2=0$ iff $\sum_j\big[\sum_i(-\lambda_i)c_{ij}-\beta e_j\big]\ln g_j=0$. The $\ln g_j$ are $\mathbb{Q}$-linearly independent by construction; by Baker's homogeneous corollary they are $\overline{\mathbb{Q}}$-linearly independent; so the coefficient of each $\ln g_j$ vanishes. $\square$

**Non-dyadic rational witness.** $\lambda=(\tfrac13,\tfrac23)$: $G=\langle2,3\rangle$, $s=2$; $\ln\tfrac13=-\ln3$, $\ln\tfrac23=\ln2-\ln3$, $e=(1,0)$. The $j=2$ ($\ln3$) equation reads $\tfrac13+\tfrac23=1=\beta\cdot0$, impossible. So $S_2(\tfrac13,\tfrac23)=\log_23-\tfrac23$ is transcendental. Base-2 rationality is thus confined to spectra multiplicatively generated by $2$ alone (up to the coefficient condition); it does not extend to generic algebraic, or even generic rational, spectra. Scope boundary routed $\mathsf{authorized}$ (as a consequence of cited Baker).

---

## 4. Explicit Ancilla Example — 2-Qubit Werner State

$\rho_W(p)=p\,\lvert\Psi^-\rangle\langle\Psi^-\rvert+(1-p)\tfrac{I}{4}$, $p\in[0,1]$.

**Purity.** $\rho_W^2=p^2\Psi+\tfrac{2p(1-p)}{4}\Psi+\tfrac{(1-p)^2}{16}I$, so
$$P_2(\rho_W(p))=p^2+\tfrac{p(1-p)}{2}+\tfrac{(1-p)^2}{4}=\frac{3p^2+1}{4}.$$
Checks: $p=1\mapsto1$; $p=0\mapsto\tfrac14$.

**Internal unital step (class $\mathcal{U}$).** Local depolarizing on qubit $A$: $\mathcal{D}_q=(1-q)\,\mathrm{id}+q\,(\tfrac{I}{2}\operatorname{Tr}_A\otimes\mathrm{id}_B)$, unital. Since $\operatorname{Tr}_A\Psi^-=I/2$, $\mathcal{D}_q(\Psi^-)=(1-q)\Psi^-+q\,I/4$, so $p\mapsto(1-q)p$ and $P_2\mapsto\tfrac{3(1-q)^2p^2+1}{4}$: strictly decreasing iff $p>0,q>0$ (consistent with Lemma Q.3; equality at $p=0$ with $\mathcal{D}_q$ non-unitary, matching the corrected equality condition).

**Lift step (class $\mathcal{L}$).** Full amplitude damping on $A$ via Stinespring with one fresh ancilla $\lvert0\rangle_E$, $U:\lvert1\rangle_A\lvert0\rangle_E\mapsto\lvert0\rangle_A\lvert1\rangle_E$, then trace $E$. Output: $\lvert0\rangle\langle0\rvert_A\otimes\operatorname{Tr}_A\rho_W=\lvert0\rangle\langle0\rvert\otimes\tfrac{I}{2}$, purity $\tfrac12$. Consumes one unit of $B$.

**Second lift.** Swap qubit $B$ with a second fresh $\lvert0\rangle$: output $\lvert00\rangle\langle00\rvert$, purity $1$. Consumes the second unit.

**Trajectory with $B_0=2$, start $p=\tfrac15$:**

| $k$ | transition | class | $\rho_k$ | $P_2(\rho_k)$ (exact) | $B_k$ | strict purity increase? |
|---|---|---|---|---|---|---|
| 1 | — | — | $\rho_W(\tfrac15)$ | $\tfrac{3/25+1}{4}=\tfrac{7}{25}$ | 2 | — |
| 2 | $\mathcal{D}_{1/2}$ on $A$ | $\mathcal{U}$ | $\rho_W(\tfrac1{10})$ | $\tfrac{3/100+1}{4}=\tfrac{103}{400}$ | 2 | no ($\tfrac{103}{400}<\tfrac{112}{400}$) |
| 3 | $\mathcal{A}_{1}$ on $A$ (fresh $\lvert0\rangle$) | $\mathcal{L}$ | $\lvert0\rangle\langle0\rvert\otimes I/2$ | $\tfrac12$ | 1 | yes |
| 4 | swap $B$ with fresh $\lvert0\rangle$ | $\mathcal{L}$ | $\lvert00\rangle\langle00\rvert$ | $1$ | 0 | yes |
| 5 | any $\mathcal{E}\in\mathcal{U}$ | $\mathcal{U}$ | $\mathcal{E}(\lvert00\rangle\langle00\rvert)$ | $\le1$ | 0 | **no** — `LIFT_BUDGET_EXHAUSTION` |

Two licensed increases ($=B_0$), obstruction at the third attempt, index $5=$ (two unital-or-lift steps before) — consistent with Theorem Q.2(a). If the trajectory had used lifts at steps 2 and 3 instead, the obstruction would be at $k^*=B_0+1=3$, the tight case of Theorem Q.2(b).

**Lift without improvement (hygiene witness).** Start $p=\tfrac9{10}$: $P_2=\tfrac{3\cdot81/100+1}{4}=\tfrac{343}{400}>\tfrac12$. Full damping on $A$ still yields purity $\tfrac12$: the lift was consumed and purity *fell*. Budget licenses, it does not deliver.

---

## 5. Certified Rational Interval Enclosure for $S(\operatorname{diag}(3/5,2/5))$

### 5.1 Reduction

$S=-\tfrac35\ln\tfrac35-\tfrac25\ln\tfrac25=\tfrac35\ln\tfrac53+\tfrac25\ln\tfrac52$, and $\ln\tfrac52=\ln\tfrac53+\ln\tfrac32$, so
$$S=\ln\tfrac53+\tfrac25\ln\tfrac32 .$$
By Theorem B1, $S$ is transcendental; the target is a rational enclosure.

### 5.2 Series with rational tail bound

**Lemma T.** For $x>0$, $u=\tfrac{x-1}{x+1}\in(-1,1)$: $\ln x=2\sum_{j\ \mathrm{odd}}\tfrac{u^j}{j}$. For $0<u<1$ and odd $n$, the partial sum $T_n=2\sum_{j\le n-2,\ \mathrm{odd}}\tfrac{u^j}{j}$ satisfies
$$T_n\ \le\ \ln x\ \le\ T_n+\frac{2u^{n}}{n(1-u^2)} .$$
*Proof.* All terms positive gives the lower bound. For the tail, $\tfrac{u^j}{j}\le\tfrac{u^j}{n}$ for $j\ge n$, and $\sum_{j\ge n,\ \mathrm{odd}}u^j=\tfrac{u^n}{1-u^2}$. $\square$

### 5.3 $\ln\tfrac53$ ($u=\tfrac14$, terms through $u^5$, $n=7$)

$T_7=2\big(\tfrac14+\tfrac1{192}+\tfrac1{5120}\big)=2\cdot\tfrac{3840+80+3}{15360}=\tfrac{3923}{7680}=\tfrac{27461}{53760}.$
Tail: $\tfrac{2(1/4)^7}{7\cdot(15/16)}=\tfrac{32}{1720320}=\tfrac1{53760}.$
$$\ln\tfrac53\in\Big[\tfrac{27461}{53760},\ \tfrac{27462}{53760}\Big]\quad(\approx[0.510807,\ 0.510826]).$$

### 5.4 $\ln\tfrac32$ ($u=\tfrac15$, terms through $u^5$, $n=7$)

$T_7=2\big(\tfrac15+\tfrac1{375}+\tfrac1{15625}\big)=2\cdot\tfrac{9375+125+3}{46875}=\tfrac{19006}{46875}.$
Tail: $\tfrac{2(1/5)^7}{7\cdot(24/25)}=\tfrac{50}{13125000}=\tfrac1{262500}.$
$$\ln\tfrac32\in\Big[\tfrac{19006}{46875},\ \tfrac{19006}{46875}+\tfrac1{262500}\Big]=\Big[\tfrac{532168}{1312500},\ \tfrac{532173}{1312500}\Big]\quad(\approx[0.4054613,\ 0.4054651]).$$

### 5.5 Combination (interval arithmetic in $\mathbb{Q}$)

$\tfrac25\cdot[\ln\tfrac32]\in\big[\tfrac{38012}{234375},\ \tfrac{532173}{3281250}\big]$.

$$L=\tfrac{27461}{53760}+\tfrac{38012}{234375}=\tfrac{429078125+136235008}{840000000}=\tfrac{565313133}{840000000}\approx0.6729918,$$
$$U=\tfrac{27462}{53760}+\tfrac{532173}{3281250}=\tfrac{2145468750+681181440}{4200000000}=\tfrac{282665019}{420000000}\approx0.6730120 .$$

**Certified statement (checked by hand, this oracle).** $S(\operatorname{diag}(\tfrac35,\tfrac25))\in[L,U]$ with $U-L=\tfrac{2826650190-2826565665}{4200000000}=\tfrac{84525}{4200000000}\approx2.01\times10^{-5}<2^{-15}$. The midpoint $m=\tfrac{L+U}{2}$ satisfies $\lvert S-m\rvert\le\tfrac{U-L}{2}<2^{-16}$. Every quantity used is a rational with explicit numerator and denominator; no floating-point operation enters the chain of inequalities. (The annotation $S\approx0.6730117$ is a decimal reference only and carries no certification weight.)

Refinement to $2^{-k}$ for larger $k$: take $n=2\lceil k/\log_2(1/u^2)\rceil+O(1)$ terms; for $u=\tfrac14$ each additional pair of terms gains $4$ bits, for $u=\tfrac15$ about $4.6$ bits.

---

## 6. Epistemic Routing (PG3)

| Item | Terminal | Grounds |
|---|---|---|
| Lemma Q.3 (purity dissipation, unital) | $\mathsf{authorized}$ | proved from cited Kadison–Schwarz |
| Prompt's strictness clause ("unless unitary on support") | $\mathsf{rejected}$ | depolarizing/dephasing counter-witnesses |
| Majorization monotonicity of all Schur-concave functionals | $\mathsf{evidence\_only}$ | cited, not re-derived |
| (A-ENV), (A-LIFT) integer budget model | $\mathsf{authorized}$ as specification | declared; fractional/thermal budgets not modelled |
| Theorem Q.2 (a)(b)(c) | $\mathsf{authorized}$ | proved under declared assumptions |
| Landauer erasure bound as the reason resets are lifts | $\mathsf{evidence\_only}$ | cited physical principle |
| Theorem B1 (entropy transcendence, rank ≥ 2) | $\mathsf{authorized}$ | proved from cited Baker; nonvanishing shown |
| Theorem Q.2.1 (1)(2)(3) | $\mathsf{authorized}$ | proved |
| Effective-Baker decidability of entropy order | $\mathsf{evidence\_only}$ / $\mathsf{unresolved}$ | principle cited; procedure not constructed |
| Proposition D (dyadic scope) | $\mathsf{authorized}$ | proved from cited Baker |
| §4 Werner trajectory | $\mathsf{authorized}$ (hand-checked) | exact rationals |
| §5 enclosure $[L,U]$ | $\mathsf{authorized}$ (hand-checked) | exact rationals; machine re-check pending |
| Lean/Cargo re-execution of §4–§5 arithmetic | $\mathsf{unresolved}$ | no tool channel |

---

## 7. Claim Hygiene Summary

- **Supported:** In this model, internal (maximally-mixed-environment) transitions are unital and cannot raise $P_2$; each purity-raising step consumes one integer unit of ancilla budget, so at most $B_0$ such steps occur and a strict-purity-improvement certificate fails by index $B_0+1$. For density matrices over a number field with rank ≥ 2, the von Neumann entropy is transcendental (nonzero linear form in logs of algebraic numbers), so it has no exact representative in the carrier; rational proxies cannot be order-faithful; exact $P_m$ and certified rational enclosures remain available. Base-2 rationality is characterized exactly and confined to spectra generated multiplicatively by 2.
- **Not supported:** that purity is strictly decreasing unless the channel is unitary; that non-unital channels decrease purity (amplitude damping is a counterexample); that lifts deliver improvement (they only license it); any accounting for fractional, thermal, or re-used environment resources; any claim about physical implementability beyond the declared Stinespring model; machine verification of the rational arithmetic in §4–§5.
- **Narrowest defensible claim:** Under (A-ENV) and (A-LIFT), the count of indices with $P_2(\rho_{k+1})>P_2(\rho_k)$ along any trajectory is at most $B_0$; and for $\rho=\operatorname{diag}(3/5,2/5)$, $S(\rho)\in[565313133/840000000,\ 282665019/420000000]$ by the series bounds of Lemma T.
- **Next check:** (i) re-verify §5 fractions by exact rational arithmetic in a tool (expect $U-L=84525/4200000000$ and containment of a high-precision reference value); (ii) encode Lemma Q.3's proof as `trace_nonneg` of the Kadison–Schwarz defect and Theorem Q.2(a) as a counting lemma over a `List` of transition tags in Lean; (iii) enumerate the $p=1/5$ Werner purity values in exact rationals.

```json
{
  "campaign_id": "FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION",
  "round": 2,
  "status": "VERIFIED_LOCAL_RESULT",
  "status_meaning": "hand-derived in this response in exact rationals; no Lean/Cargo/solver executed; not machine-checked",
  "derived_theorems": [
    "Lemma_Q_3_PurityDissipation_Unital",
    "Theorem_Q_2_PurityLiftExhaustion",
    "Theorem_B1_EntropyTranscendence_RankGe2",
    "Theorem_Q_2_1_TranscendentalEntropyDecoupling",
    "Proposition_D_DyadicScopeBoundary",
    "Lemma_T_RationalLogTailBound"
  ],
  "bounds_established": {
    "licensed_purity_increases": "<= B_0",
    "purity_certificate_failure_index": "k* <= B_0 + 1",
    "combined_with_round_1": "k* <= min(N+1, B_0+1)",
    "werner_example_B0": 2,
    "werner_example_obstruction_index": 5,
    "werner_tight_case_obstruction_index": 3,
    "entropy_enclosure_diag_3_5_2_5": {
      "L": "565313133/840000000",
      "U": "282665019/420000000",
      "width": "84525/4200000000",
      "width_bits": "< 2^-15",
      "midpoint_error_bits": "< 2^-16"
    }
  },
  "corrections_to_prompt": [
    "Purity equality condition is E(rho)^2 = E(rho^2), not 'unitary on support'; depolarizing on I/2 and Z-dephasing on |0><0| are counter-witnesses.",
    "Non-unital channels (e.g. amplitude damping) can raise purity; monotonicity requires unitality, and amplitude damping is modelled as the lift, not as dissipation.",
    "Prompt's 'k* <= B_0' read as number of licensed increases; first obstructed claim has index B_0 + 1.",
    "Prompt's 'Lemma Q.2' relabelled Lemma Q.3 to avoid collision with Round 1 Lemma Q.2.",
    "Baker's theorem requires the linear form to be nonzero; this is supplied by rank >= 2 (all terms positive). Only algebraicity of the spectrum is needed, not membership in K.",
    "'Transcendental over K' coincides with 'transcendental over Q' since K is algebraic."
  ],
  "unresolved_obligations": [
    "Round 3: fractional and thermal lift budgets (partially mixed or finite-temperature environments) and their conversion to effective purity units.",
    "Round 3: construct an effective-Baker-based decision procedure for S(rho) < S(sigma) with algebraic spectra (terminating interval refinement with certified equality detection).",
    "Round 3: extend Theorem Q.2 from P_2 to a majorization-based statement covering all Renyi orders, with its own proof rather than citation.",
    "Round 3: stochastic single-shot reports (collision in distribution vs realization), carried over from Round 1.",
    "Round 3: F2 (cyclotomic carrier) arithmetic cost model for exact P_m tracking; F4 (finite field) sense still unused.",
    "Tooling: machine re-check of Section 5 rational enclosure and Section 4 Werner purity table; Lean encoding of Lemma Q.3 and Theorem Q.2(a)."
  ],
  "claim_hygiene": {
    "supported": "Unital internal channels cannot raise P_2 (Kadison-Schwarz + trace preservation); at most B_0 purity-raising steps under the integer lift model; von Neumann entropy of rank>=2 algebraic-entry density matrices is transcendental (Baker), so inexpressible in K; rational proxies are not order-faithful; exact P_m and certified rational enclosures are available; base-2 rationality is exactly characterized and confined to 2-generated spectra.",
    "not_supported": "Strictness-unless-unitary clause; purity decrease under non-unital channels; lifts delivering improvement; fractional/thermal budgets; physical implementability beyond the declared Stinespring model; any machine verification of the arithmetic.",
    "narrowest_claim": "Under (A-ENV) and (A-LIFT), #{k : P_2(rho_{k+1}) > P_2(rho_k)} <= B_0; and S(diag(3/5,2/5)) lies in [565313133/840000000, 282665019/420000000] by Lemma T.",
    "next_check": "Re-verify the Section 5 fractions and the Werner purity table with exact rational arithmetic in a tool; encode Lemma Q.3 and Theorem Q.2(a) in Lean."
  }
}
```