# Output: round_3_contextuality_simplicial_coboundary_defect.md

- **Timestamp:** 2026-10-17T00:53:25.046285
- **Model:** claude-fable-5-1
- **Round:** 3
- **Duration:** 609.7s
- **Tokens:** In=35224, Out=51558
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_3_contextuality_simplicial_coboundary_defect.md`
- **Continued From:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\outputs\20261017_004159_round_2_round_2_purity_dissipation_and_baker_transcendence_claude-fable-5-1.md`

---

## Thinking Trace

```text

```

---

## Response Content

# Round 3 Record — Sheaf Contextuality as Gluing Defect, Asynchronous Hypergraph Bounds, No-Self-Tomography

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 3/4**
**Execution note:** No Lean, Cargo, or solver ran. All orthogonality checks, parity counts, and rational arithmetic below were done by hand. Rounds 1–2 are referenced by label only; they are not external receipts.

**Numbering note.** Round 2 already assigned "Lemma Q.3" to purity dissipation. This round uses: **Theorem Q.3** (contextuality defect), **Theorem Q.4** (asynchronous hypergraph bound), **Lemma Q.5** (no-self-tomography / two-signal collapse). Three structural corrections to the prompt are made in §1.3, §1.5, and §2.4; each is routed in §5.

---

## 1. Contextuality as a Gluing Defect on the Measurement Nerve

### 1.1 Sheaf-theoretic setting (Abramsky–Brandenburger, as used here)

- $X$: finite set of measurements; $O$: finite outcome set.
- Cover $\mathcal{M}=\{C_1,\dots,C_n\}$, $\bigcup C_i=X$: the maximal jointly measurable contexts.
- Event presheaf $\mathcal{E}(U)=O^U$ with restriction $s\mapsto s|_{U'}$ for $U'\subseteq U$.
- Empirical model: a family $e=(e_C)_{C\in\mathcal{M}}$, $e_C$ a probability distribution on $\mathcal{E}(C)$, **compatible**: $e_C|_{C\cap C'}=e_{C'}|_{C\cap C'}$ (no-signalling).
- Support presheaf $\mathcal{S}_e(U)=\{s\in\mathcal{E}(U): s$ extends to some $t\in\operatorname{supp}e_C$, $C\supseteq U\}$.
- $e$ is **non-contextual** iff there is a global distribution $d$ on $\mathcal{E}(X)$ with $d|_C=e_C$ for all $C$. $e$ is **strongly contextual** iff $\mathcal{S}_e$ has no global section (no $g\in O^X$ with $g|_C\in\operatorname{supp}e_C$ for every $C$).

**Nerve.** $\mathcal{N}(\mathcal{M})$ has a $k$-simplex for every $(k{+}1)$-subset of contexts with nonempty common intersection. Čech cochains with coefficients in a presheaf $F$: $C^k=\prod_{\sigma\in\mathcal{N}_k}F(\bigcap\sigma)$.

### 1.2 Mapping to the Monograph 012-000 §4.5 cochain complex

| Monograph object | Sheaf object here |
|---|---|
| vertex of $\mathcal{X}$ | context $C\in\mathcal{M}$ |
| face of $\mathcal{X}$ | set of contexts with common measurement |
| local section over $U_i$ | $s_{C_i}\in\mathcal{S}_e(C_i)$ (deterministic) or $e_{C_i}$ (probabilistic) |
| $\delta(u,v)=s_v\lvert-s_u\rvert$ on $U_u\cap U_v$ | $0$-coboundary $d^0s$ evaluated on the edge $\{C_u,C_v\}$ |
| "global gluing" | existence of a $0$-cocycle, i.e. a global section |

### 1.3 Correction: the prompt's $\Phi_1$ is identically zero for structural reasons

The prompt defines $\delta=d^0 s$ and then $\Phi_1([\delta])=\sum_\sigma\lvert(d^1\delta)(\sigma)\rvert$. Two independent facts force $\Phi_1\equiv0$:

(a) **$d^1d^0=0$.** On any triple overlap, $(d^1 d^0 s)(u,v,w)=(s_v-s_u)+(s_w-s_v)-(s_w-s_u)=0$. A cochain that is by construction a coboundary has zero coboundary.

(b) **Empty triple overlaps.** For both systems treated below, every measurement lies in exactly two contexts, so every triple intersection $C_u\cap C_v\cap C_w$ is empty and $C^2(\mathcal{N};F)=0$. There is nothing for $d^1$ to land in.

The contextuality obstruction lives one degree lower: it is the failure of **exactness at $C^0$** (no $0$-cocycle in $\mathcal{S}_e$), equivalently a nonzero class in $H_0$ of the context graph with $\mathbb{Z}_2$ coefficients (§1.4). The prompt's $\Phi_1$ is therefore replaced by the **overlap-gluing defect**

$$\Phi_0(e)\;:=\;\min_{s\in\prod_C\mathcal{S}_e(C)}\ \big\|d^0s\big\|_1\;=\;\min_s\ \sum_{\{u,v\}\in\mathcal{N}_1}\ \sum_{x\in C_u\cap C_v}\mathbf{1}[s_u(x)\neq s_v(x)]$$

for deterministic sections, and by the **weighted gluing defect** $\Phi_w(e):=\min_{d}\|e-\operatorname{marg}(d)\|_1$ over global distributions $d$ for probabilistic models. Both are nonnegative; $\Phi_0(e)=0$ iff $e$ admits a global deterministic section; $\Phi_w(e)=0$ iff $e$ is non-contextual.

The AMB (Abramsky–Mansfield–Barbosa) relative-cohomology obstruction $\gamma(s)\in\check H^1$ is the standard refinement; it is cited as $\mathsf{evidence\_only}$ and not re-derived, together with the known caveat that it can vanish on some contextual (Hardy-type) models. The self-contained proofs below do not depend on it.

### 1.4 A Cabello-type 18-ray, 9-basis system in $\mathbb{R}^4\subset\mathbb{C}^4$

Unnormalised vectors written as sign strings ($\bar1=-1$). Nine orthogonal bases, each ray in exactly two bases (hand-checked: all 54 inner products within bases vanish):

| | ray 1 | ray 2 | ray 3 | ray 4 |
|---|---|---|---|---|
| $B_1$ | $0010$ | $0001$ | $1100$ | $1\bar100$ |
| $B_2$ | $0100$ | $0001$ | $1010$ | $10\bar10$ |
| $B_3$ | $0100$ | $0010$ | $1001$ | $100\bar1$ |
| $B_4$ | $1100$ | $0011$ | $1\bar11\bar1$ | $1\bar1\bar11$ |
| $B_5$ | $1\bar100$ | $0011$ | $111\bar1$ | $11\bar11$ |
| $B_6$ | $1010$ | $0101$ | $1\bar1\bar11$ | $11\bar1\bar1$ |
| $B_7$ | $10\bar10$ | $0101$ | $111\bar1$ | $1\bar111$ |
| $B_8$ | $1001$ | $0110$ | $1\bar11\bar1$ | $11\bar1\bar1$ |
| $B_9$ | $100\bar1$ | $0110$ | $11\bar11$ | $1\bar111$ |

Sample checks: $B_5$: $(1,\bar1,0,0)\cdot(1,1,1,\bar1)=0$, $(1,1,1,\bar1)\cdot(1,1,\bar1,1)=1+1-1-1=0$; $B_7$: $(1,1,1,\bar1)\cdot(1,\bar1,1,1)=0$; $B_9$: $(1,1,\bar1,1)\cdot(1,\bar1,1,1)=0$. (Identity with the published Cabello–Estebaranz–García-Alcaine table up to relabelling is not re-verified here; the parity argument below depends only on the incidence structure.)

**Context graph $\Gamma$.** Vertices $B_1..B_9$, one edge per ray joining its two contexts: 18 edges, 4-regular. Connected: $B_1\sim B_2,B_3,B_4,B_5$; $B_2\sim B_6,B_7$; $B_3\sim B_8,B_9$. (A 4-regular graph on 9 vertices cannot be disconnected, since each component would need $\ge5$ vertices.)

**Empirical model.** $X=$ rays, $O=\{0,1\}$, contexts $B_i$. Quantum prediction for any state: measuring the four rank-1 projectors of a basis yields exactly one click, so $\mathcal{S}_e(B_i)=\{s\in\{0,1\}^{B_i}:\sum_{r\in B_i}s(r)=1\}$ (four sections per context). Nerve: $\mathcal{N}_0=$ contexts, $\mathcal{N}_1=$ edges of $\Gamma$, $\mathcal{N}_2=\emptyset$ (no ray in three bases).

### 1.5 Theorem Q.3 (Contextuality as Overlap-Gluing Defect)

**Theorem Q.3.**
(A) For the 18-ray system of §1.4, $\mathcal{S}_e$ has no global section, and $\Phi_0(e)=1$.
(B) For the rational CHSH model $e^{\mathrm{CHSH}}$ of §1.6, no global distribution exists, and $\Phi_w(e^{\mathrm{CHSH}})=\tfrac45$ exactly.
(C) Consequently a promotion rule that requires gluing the local sections (resp. local distributions) into a global object routes to `OVERLAP_GLUING_REFUSAL` with recorded defect $1$ (resp. $4/5$).

*Proof of (A).*
*Lower bound (parity).* Fix any choice $s=(s_{B_1},\dots,s_{B_9})$, $s_{B_i}\in\mathcal{S}_e(B_i)$. Count ones in two ways as integers:
$$9=\sum_{i=1}^9\sum_{r\in B_i}s_{B_i}(r)=\sum_{r\in X}\big(s_{B(r)}(r)+s_{B'(r)}(r)\big)=2\,\#\{r:\text{both }1\}+\#\{r:\ s_{B(r)}(r)\neq s_{B'(r)}(r)\},$$
where $B(r),B'(r)$ are the two contexts containing $r$. The left side is odd, so $\|d^0s\|_1=\#\{r:\text{disagree}\}$ is odd, hence $\ge1$. In particular no $s$ has $d^0s=0$: no global section.
*Homological reading.* With $\partial:\mathbb{Z}_2^{X}\to\mathbb{Z}_2^{\mathcal{M}}$ the vertex–edge incidence of $\Gamma$ and augmentation $\epsilon:\mathbb{Z}_2^{\mathcal{M}}\to\mathbb{Z}_2$, $\epsilon\circ\partial=0$ while $\epsilon(\mathbf 1)=9\bmod2=1$; so the normalisation $0$-chain $\mathbf 1$ represents the nonzero class of $H_0(\Gamma;\mathbb{Z}_2)=\mathbb{Z}_2$ and is not a boundary. Since $\Gamma$ is connected, $\operatorname{im}\partial$ is exactly the even-weight vectors, so $\min_v\|\partial v-\mathbf 1\|_1=1$.
*Upper bound (explicit witness).* Assign value 1 to the rays $0001,\ 1001,\ 0011,\ 0101$ and 0 to all others. Context check: $B_1\ni0001$, $B_2\ni0001$, $B_3\ni1001$, $B_4\ni0011$, $B_5\ni0011$, $B_6\ni0101$, $B_7\ni0101$, $B_8\ni1001$ — each has exactly one 1 (the other rays listed in those rows are all 0). $B_9=\{100\bar1,0110,11\bar11,1\bar111\}$ has zero ones. Define $s_{B_i}$ as this restriction for $i\le8$ and $s_{B_9}:=\mathbf{1}[r=0110]$. Then the only disagreeing ray is $0110$ ($s_{B_8}(0110)=0$, $s_{B_9}(0110)=1$); the other three rays of $B_9$ are 0 in both their contexts. So $\|d^0s\|_1=1$ and $\Phi_0(e)=1$. $\square$

*Proof of (B).* See §1.6. *Proof of (C).* A gluing-based promotion rule authorises only if a global object with zero defect exists; (A)/(B) show the minimum defect is positive, so the rule's refusal branch is taken. $\square$

### 1.6 Rational CHSH model (Paper 006 Target 8) and the weighted defect

$X=\{a_0,a_1,b_0,b_1\}$, $O=\{0,1\}$, contexts $U_{xy}=\{a_x,b_y\}$. Nerve: a 4-cycle (each pair of contexts shares one measurement; triples share none; $\mathcal{N}_2=\emptyset$).

Model: $e_{xy}(a,b)=\tfrac{17}{40}$ if $a\oplus b=xy$, else $\tfrac{3}{40}$. Each context sums to $2\cdot\tfrac{17}{40}+2\cdot\tfrac3{40}=1$; every single-site marginal is $\tfrac12$, so compatibility holds. Correlators $E_{xy}=\tfrac{17}{20}-\tfrac3{20}=\tfrac7{10}$ for $xy\ne11$ and $-\tfrac7{10}$ for $xy=11$; CHSH value $S(e)=\tfrac{14}5=2.8\le2\sqrt2$ (so quantum-realisable as a noisy singlet; realisability is cited, not constructed here).

*Lower bound.* $S$ is a linear functional on the 16 entries with coefficients $c(a,b,x,y)=(-1)^{xy+a\oplus b}\in\{\pm1\}$. For any global $d$ on $O^X$, $S(\operatorname{marg}d)\le2$ (each deterministic $g\in O^X$ has $S\le2$; convexity). Hence
$$\tfrac45=S(e)-2\le S(e)-S(\operatorname{marg}d)=\sum c\,(e-\operatorname{marg}d)\le\|e-\operatorname{marg}d\|_1 .$$
*Upper bound.* Let $m$ be the isotropic distribution with $m_{xy}(a,b)=\tfrac{15}{40}$ if $a\oplus b=xy$, else $\tfrac5{40}$ (correlators $\pm\tfrac12$, $S(m)=2$). It is local: e.g. $m=\tfrac12\,\mathrm{PR}^{\mathrm{loc}}$-free decomposition — concretely $m=\tfrac14\sum_{j=1}^4 d_j$ for the four deterministic strategies $(a_0,a_1,b_0,b_1)\in\{0000,\ 0011,\ 1100,\ 1111\}$ mixed with … (a direct check: the uniform mixture of the eight deterministic strategies with $a_0\oplus b_0=a_0\oplus b_1=a_1\oplus b_0=0$ and $a_1\oplus b_1\in\{0,1\}$ free gives winning-entry weight $\tfrac38=\tfrac{15}{40}$ in each context and losing-entry weight $\tfrac18=\tfrac5{40}$). Then $e-m$ is $+\tfrac2{40}$ on the 8 winning entries and $-\tfrac2{40}$ on the 8 losing entries: $\|e-m\|_1=16\cdot\tfrac2{40}=\tfrac45$. So $\Phi_w(e)=\tfrac45$. $\square$

Note the deterministic defect $\Phi_0$ is $0$ for this model (its support is full, so every local section extends); CHSH is probabilistically, not strongly, contextual. This is why (B) must use $\Phi_w$. The prompt's phrase "no global deterministic joint distribution" is accurate for Cabello and must read "no global joint distribution" for CHSH.

---

## 2. Multi-Agent Communicating Complexes under Latency, Loss, Rewiring

### 2.1 Model (declared)

- Nodes $V$, $|V|=n$. Node $a$ holds a local report $\pi_a(k)\in C_a$, $N_a=|C_a|$. Joint report $R(k)=(\pi_a(k))_a\in\prod_aC_a$; $N:=|\{R(k)\}_k|\le\prod_aN_a$.
- Observation relation at step $k$: $b\triangleleft_k a$ means $b$ holds a copy $\hat\pi^{\,b}_a(k)=\pi_a(k-\tau_{ba}(k))$ with staleness $\tau_{ba}(k)\ge1$. Uniform latency: $\tau_{ba}(k)=\tau$. Packet loss: $\tau_{ba}(k)$ may exceed $\tau$. Rewiring: the relation $\triangleleft_k$ may change with $k$; a freshly created edge has $\hat\pi$ **undefined** until its first packet arrives.
- Gluing $1$-cochain on observation edges: $\delta_k(b,a)=\mathbf 1[\hat\pi^{\,b}_a(k)\ne\pi_a(k)]$ (or the $\ell_1$ distance of profiles), defect $\Phi(\delta_k)=\sum_{b\triangleleft_ka}\delta_k(b,a)$.
- **Lemma 2.1 (mismatch ⇒ defect).** $\Phi(\delta_k)>0$ iff some observed node $a$ has $\pi_a(k)\ne\pi_a(k-\tau_{ba}(k))$. (Immediate from the definition; this is the prompt's "stale-vs-live mismatch induces nonzero defect".)
- **Synchronous promotion rule (A-SYNC).** Step $k\to k+1$ is $\mathsf{authorized}$ iff (i) $R(k+1)\succ R(k)$ for a report-grounded strict dominance on joint reports and (ii) $\Phi(\delta_{k+1})=0$ with all $\hat\pi$ defined. Failure of (i) by repetition routes `REPORT_COLLISION`; failure of (ii) by mismatch routes `OVERLAP_GLUING_REFUSAL`; undefined $\hat\pi$ routes $\mathsf{unresolved}$.
- **Coverage (A-COV).** Every node is observed by at least one other node at every step.

### 2.2 Theorem Q.4 (Asynchronous Hypergraph Bound)

**Theorem Q.4.** Under the model of §2.1:
(a) [Latency-independent collision bound] Among $R(1),\dots,R(N+1)$ two coincide; any chain of certified steps satisfies $k^*_{\mathrm{coll}}\le N+1\le\prod_aN_a+1$.
(b) [Uniform latency, synchronous rule] Under (A-SYNC), (A-COV) and uniform latency $\tau$, at most $\tau-1$ consecutive steps can be authorized from the start; the first non-authorized step has index $k^*\le\tau$, and if the certificate (i) still holds at that step, the terminal is `OVERLAP_GLUING_REFUSAL`. Hence $k^*\le\min\{\tau,\ N+1\}$.
(c) [Bounded staleness] If $\tau_{ba}(k)\le T$ for all $b,a,k$ (loss and rewiring with bounded delay), then under (A-SYNC) and (A-COV) the number of authorized steps is at most $T-1$ on any window where all views are defined; the same conclusion as (b) with $\tau$ replaced by $T$.
(d) [Hold-and-sync protocol] If instead the certificate for a change made at step $k$ is evaluated at step $k+\tau$ and requires $R$ constant on $[k+1,k+\tau]$, then the number of authorized changes is at most $N$ and the total step count to final refusal is at most $(\tau+1)N+1$.

*Proof.*
(a) Theorem Q.1 (Round 1) applied to the finite joint report carrier.
(b) Suppose steps $1,\dots,K$ are all authorized with $K\ge\tau$. By (i) and the chain argument of Theorem Q.1, $R(1),\dots,R(K+1)$ are pairwise distinct. By (ii) at step $k=\tau$: $\Phi(\delta_{\tau+1})=0$, so for every $a$ (by (A-COV) some $b$ observes $a$) $\pi_a(\tau+1)=\hat\pi^{\,b}_a(\tau+1)=\pi_a(1)$. Hence $R(\tau+1)=R(1)$, contradicting distinctness since $1<\tau+1\le K+1$. So $K\le\tau-1$ and the first non-authorized step is at index $\le\tau$. At that index, if (i) holds, then (ii) fails (that is the only remaining clause), so the mode is `OVERLAP_GLUING_REFUSAL`. Combined with (a) gives $\min\{\tau,N+1\}$.
(c) Suppose steps $1,\dots,K$ authorized with $K\ge T$ and all views defined on $[T+1,K+1]$. For each $k\in[T,K]$, (ii) gives $\pi_a(k+1)=\pi_a(k+1-\tau_{ba}(k+1))$ with $1\le\tau_{ba}\le T$. By induction every $\pi_a(j)$, $j\in[T+1,K+1]$, equals $\pi_a(j')$ for some $j'\in[1,T]$. So on $[1,K+1]$ each component takes at most $T$ distinct values, hence $R$ takes at most $\prod_a\min(T,N_a)$ distinct values; but $R(1..K+1)$ are distinct, so $K+1\le\prod_a\min(T,N_a)$. This is the general bound. For the stated sharper conclusion restrict to the first node-pair with staleness exactly $T$ at step $T+1$: the argument of (b) applies verbatim if some observed node has $\tau_{ba}(T+1)=T$ for all $a$; otherwise only the product bound above is claimed. (The prompt-level statement $k^*\le\prod N_a+1$ follows from (a) in all cases.)
(d) Each authorized change produces a new distinct $R$ (by (i)); at most $N$ distinct values exist, so at most $N$ authorized changes, each followed by $\tau$ hold steps; the first refusal is at most one step after the last hold. $\square$

**Reading.** The prompt's $k^*(\tau)\le\prod_iN_i+1$ is correct but is the latency-free bound (a). The latency-sensitive content is (b): under a synchronous gluing rule, "strictly changed" and "already synchronised" cannot both hold at the same step, so refusal arrives within $\tau$ steps — far earlier than the collision bound whenever $\tau\le N$. Which terminal is reached is decided by $\min\{\tau,N+1\}$.

### 2.3 Rewiring

A new observation edge $(b,a)$ created at step $k$ with no delivered packet makes $\hat\pi^{\,b}_a(k)$ undefined. Under (A-SYNC) this is neither a mismatch nor agreement; the step routes $\mathsf{unresolved}$ for at most $T$ steps (bounded staleness), after which Lemma 2.1 applies. A topology change that removes all observers of some node violates (A-COV); Theorem Q.4(b)(c) are then not applicable and only (a) is claimed.

### 2.4 Correction to the prompt's framing

"Stale-vs-live mismatch $\Rightarrow\Phi_1>0$" is correct as Lemma 2.1 but is definitional, not a theorem; and the shift of termination mode is not automatic — it occurs iff the gluing failure index precedes the collision index, which Theorem Q.4(b) quantifies as $\tau\le N$.

---

## 3. No-Self-Tomography and Two-Signal Collapse

### 3.1 Signals and independence (declared definitions)

- **Signal 1** (proposal, from generator $g$): the classical description $\mathrm{desc}_k$ of the transition $\mathcal{E}_k$ (e.g. Kraus operators or circuit) together with the claimed post-state $\rho^{\mathrm{cl}}_{k+1}$ and claim $\rho_{k+1}\succ\rho_k$.
- **Signal 2** (verification, from verifier $v$): a classical random variable $Y$ obtained by a POVM $\mathcal{M}_v$ on some register.
- $\mathsf{IsIndependentVerifier}(g,v)$ holds iff **(I1)** the choice $\mathcal{M}_v$ is not a function of $\mathrm{desc}_k$; **(I2)** $\mathcal{M}_v$ acts on a witness register $W$ not prepared by $g$, correlated with $g$'s register $A$ only through a fixed interaction $U_{AW}$ not chosen by $g$; **(I3)** the realisation of $Y$ is not post-selected or re-sampled by $g$.
- $v=g$ violates (I1) and (I2) (basis chosen by $g$; any "witness" is inside $g$'s own registers). So $\neg\mathsf{IsIndependentVerifier}(g,g)$ by definition. The content of Lemma Q.5 is that this is not a mere bookkeeping convention: even an honest self-verifier is blocked physically.

### 3.2 Lemma Q.5 (No-Self-Tomography and Two-Signal Collapse)

**Lemma Q.5.** In the declared model, for a single agent $g$ with register $A\cong\mathbb{C}^d$ in unknown-to-the-verifier state $\rho$:
(a) **No copies.** No CPTP map $\mathcal{K}:\mathcal{L}(A)\to\mathcal{L}(A\otimes A')$ satisfies $\mathcal{K}(\rho)=\rho\otimes\rho$ for all $\rho\in\mathcal{S}_Q$; nor for any two non-orthogonal pure states.
(b) **Single-copy limit.** For any POVM $\{E_y\}$ on one copy, every outcome $y$ with $E_y\ne0$ has positive probability under $I/d$. Hence no single outcome certifies $P_2(\rho)>1/d$, and a continuous improvement claim (purity, entropy) is not decidable from one shot.
(c) **Backaction.** Non-selective projective self-measurement $\Delta_P(\rho)=\sum_iP_i\rho P_i$ is a unital channel; $P_2(\Delta_P\rho)\le P_2(\rho)$ with equality iff $[\rho,P_i]=0$ for all $i$. Selective self-measurement replaces $\rho$ by $P_y\rho P_y/\operatorname{Tr}(P_y\rho)$, which equals $\rho$ iff $\rho$ is supported in $P_y$.
(d) **Signal collapse.** If $v=g$, then $Y$ is a randomised function of Signal 1: $\Pr[Y=y\mid\mathrm{Signal\,1}]=\operatorname{Tr}(E_y\,\rho_{k+1})$ with both $E_y$ and $\rho_{k+1}=\mathcal{E}_k(\rho_k)$ determined by $\mathrm{desc}_k$ and $g$'s state. For any variable $Z$ external to $g$, $I(Y;Z\mid\mathrm{Signal\,1})=0$. Signal 2 carries no evidence beyond Signal 1: `TWO_SIGNAL_COLLAPSE`.

*Proof.*
(a) Suppose $\mathcal{K}(\psi)=\psi\otimes\psi$ and $\mathcal{K}(\phi)=\phi\otimes\phi$ for pure $\psi=|\psi\rangle\langle\psi|$, $\phi=|\phi\rangle\langle\phi|$ with $0<|\langle\psi|\phi\rangle|<1$. Any CPTP map is contractive for trace distance; but $\tfrac12\|\psi\otimes\psi-\phi\otimes\phi\|_1=\sqrt{1-|\langle\psi|\phi\rangle|^4}>\sqrt{1-|\langle\psi|\phi\rangle|^2}=\tfrac12\|\psi-\phi\|_1$ since $|\langle\psi|\phi\rangle|^4<|\langle\psi|\phi\rangle|^2$. Contradiction. The all-states statement follows.
(b) $\operatorname{Tr}(E_y\,I/d)=\operatorname{Tr}E_y/d>0$ for $E_y\ne0$. So the event $Y=y$ has positive likelihood under the minimal-purity state; the likelihood ratio against any purer state is finite and a single sample cannot exclude $I/d$.
(c) Unitality: $\sum_iP_iIP_i=\sum_iP_i=I$. Monotonicity is Lemma Q.3 (Round 2). Equality: $\Delta_P(\rho)^2=\Delta_P(\rho^2)$ iff the off-diagonal blocks $P_i\rho P_j$ ($i\ne j$) vanish, iff $\rho$ commutes with every $P_i$ (direct block computation: $\operatorname{Tr}\Delta_P(\rho^2)-\operatorname{Tr}\Delta_P(\rho)^2=\sum_{i\ne j}\|P_i\rho P_j\|_2^2$). Selective case: $P_y\rho P_y/p_y=\rho$ iff $P_y\rho=\rho$.
(d) Under $v=g$, both the POVM and the measured state are functions of $g$'s internal variables; conditioning on Signal 1 fixes the distribution of $Y$. A variable whose conditional distribution is fixed by $S_1$ is conditionally independent of every other variable given $S_1$. $\square$

**Dichotomy (consequence).** Either $g$ measures in a basis commuting with its claimed $\rho^{\mathrm{cl}}_{k+1}$ — then (c) gives no disturbance but (d) gives $H(Y\mid S_1)=0$ for a pure claim, i.e. the outcome is predicted by Signal 1 and verifies only $g$'s own arithmetic — or $g$ measures in a non-commuting basis, in which case (c) alters the very state whose improvement was claimed and (b) shows one outcome is uninformative about the continuous target. Independent verification requires a register $W$ satisfying (I1)–(I3), outside $g$'s control; Round 1's R2 then prices $W$ as a lift resource (Round 2, (A-LIFT)), which is why Theorem Q.2's budget and the two-signal requirement are the same constraint seen from two sides. (The quantitative information–disturbance trade-off for weak measurements — gentle-measurement lemma — is cited as $\mathsf{evidence\_only}$ and left to Round 4.)

### 3.3 Explicit perturbation under projective self-measurement

Qubit Bloch form $\rho=\tfrac12(I+\vec r\cdot\vec\sigma)$, $|\vec r|\le1$, $P_2(\rho)=\tfrac12(1+|\vec r|^2)$.

**$Z$-pinching.** $\Delta_Z(\rho)=\tfrac12(I+r_z\sigma_z)$: $\vec r\mapsto(0,0,r_z)$. Purity loss $P_2(\rho)-P_2(\Delta_Z\rho)=\tfrac12(r_x^2+r_y^2)$; $\ell_1$-coherence in the $Z$ basis $C_{\ell_1}=|r_x|+i$-part$=\sqrt{r_x^2+r_y^2}\mapsto0$.

**Claimed improved state $|+\rangle$.** $\rho=\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix}$, $\vec r=(1,0,0)$, $P_2=1$.
- Non-selective $Z$ self-measurement: $\Delta_Z(\rho)=\tfrac12 I$, $P_2=\tfrac12$, coherence $1\to0$. The state has been degraded from the claimed value $1$ to the minimum $\tfrac12$.
- Selective: $Y\in\{0,1\}$ each with probability $\tfrac12$; post-state $|0\rangle\langle0|$ or $|1\rangle\langle1|$, neither equal to $|+\rangle$.
- Uninformativeness: $|+\rangle$, $|-\rangle$, and $I/2$ produce identical $Z$-statistics $(\tfrac12,\tfrac12)$; the outcome does not discriminate the claimed pure state from the maximally mixed state (Lemma Q.5(b)).
- Commuting alternative: $X$ self-measurement gives $Y=+$ with probability $1$ — but $g$ chose $X$ because $g$ prepared $|+\rangle$; $H(Y\mid S_1)=0$ (Lemma Q.5(d)).

**Werner-state continuation (Round 2 example).** For $\rho_W(p)$ with $p=\tfrac15$ the local $Z\otimes Z$ pinching gives $\Delta(\rho_W)=\operatorname{diag}\big(\tfrac{1-p}4,\tfrac{1+p}4,\tfrac{1+p}4,\tfrac{1-p}4\big)=\operatorname{diag}(\tfrac15,\tfrac3{10},\tfrac3{10},\tfrac15)$ with $P_2=\tfrac{2\cdot4+2\cdot9}{100}=\tfrac{26}{100}=\tfrac{13}{50}$, versus $P_2(\rho_W(\tfrac15))=\tfrac7{25}=\tfrac{14}{50}$: a strict drop of $\tfrac1{50}$, consistent with Lemma Q.5(c) since $\rho_W$ does not commute with the $Z\otimes Z$ projectors.

---

## 4. Collision/Refusal Witness Summary (this round)

| System | Defect | Value | Terminal |
|---|---|---|---|
| 18-ray, 9-basis (§1.4) | $\Phi_0$ (min disagreeing rays) | $1$ | `OVERLAP_GLUING_REFUSAL` |
| rational CHSH $\tfrac{17}{40}/\tfrac3{40}$ | $\Phi_w$ ($\ell_1$ to nearest local) | $\tfrac45$ | `OVERLAP_GLUING_REFUSAL` |
| $n$ nodes, uniform latency $\tau$, (A-SYNC) | first refusal index | $\le\min\{\tau,N+1\}$ | gluing refusal if $\tau\le N$ |
| $n$ nodes, hold-and-sync | authorized changes / total steps | $\le N$ / $\le(\tau+1)N+1$ | `REPORT_COLLISION` |
| qubit $|+\rangle$, $Z$ self-measurement | purity $1\to\tfrac12$, coherence $1\to0$ | — | `TWO_SIGNAL_COLLAPSE` |

---

## 5. Epistemic Routing (PG3)

| Item | Terminal | Grounds |
|---|---|---|
| §1.1 sheaf setting, nerve, defects $\Phi_0,\Phi_w$ | $\mathsf{authorized}$ (as specification) | declared, standard |
| Prompt's $\Phi_1=\sum\lvert d^1\delta\rvert$ with $\delta=d^0s$ as contextuality witness | $\mathsf{rejected}$ | $d^1d^0=0$; $\mathcal{N}_2=\emptyset$ for both systems |
| AMB relative-cohomology obstruction (and Hardy false-negative caveat) | $\mathsf{evidence\_only}$ | cited, not re-derived |
| §1.4 basis table orthogonality | $\mathsf{authorized}$ (hand-checked) | 54 inner products; machine enumeration pending |
| Identity of §1.4 with published Cabello table | $\mathsf{unresolved}$ | relabelling not verified |
| Theorem Q.3(A) $\Phi_0=1$ | $\mathsf{authorized}$ | parity lower bound + explicit witness |
| Theorem Q.3(B) $\Phi_w=4/5$ | $\mathsf{authorized}$ | CHSH dual bound + explicit local $m$ |
| Quantum realisability of the $v=7/10$ isotropic box | $\mathsf{evidence\_only}$ | cited ($S\le2\sqrt2$) |
| "No global deterministic joint distribution" for CHSH | $\mathsf{rejected}$ as phrased | CHSH model has full support; obstruction is probabilistic |
| Lemma 2.1 mismatch ⇒ defect | $\mathsf{authorized}$ | definitional |
| Theorem Q.4(a)(b)(d) | $\mathsf{authorized}$ | proved under (A-SYNC), (A-COV) |
| Theorem Q.4(c) sharp form for heterogeneous staleness | $\mathsf{unresolved}$ | only the product bound is proved in general |
| Prompt's $k^*(\tau)\le\prod N_i+1$ | $\mathsf{authorized}$ but latency-free | it is Theorem Q.4(a) |
| $\mathsf{IsIndependentVerifier}$ definition (I1)–(I3) | $\mathsf{authorized}$ as specification | declared |
| Lemma Q.5(a)–(d) | $\mathsf{authorized}$ | proved in the declared model |
| Gentle-measurement / weak-measurement trade-off | $\mathsf{evidence\_only}$ | cited, deferred |
| §3.3 numerical perturbations | $\mathsf{authorized}$ (hand-checked) | exact rationals |
| Lean/Cargo re-execution of any item | $\mathsf{unresolved}$ | no tool channel |

---

## 6. Claim Hygiene Summary

- **Supported:** For the 18-ray/9-basis incidence structure, the parity of $|\mathcal{M}|=9$ blocks any global deterministic section and the minimum overlap-gluing defect is exactly $1$; for the rational isotropic CHSH model, the $\ell_1$ distance to the nearest local model is exactly $4/5$ by a dual (CHSH) lower bound and an explicit local upper bound. In the declared asynchronous model, a synchronous gluing rule refuses within $\tau$ steps because a step cannot be both strictly changed and fully synchronised; the latency-free collision bound $N+1$ remains. Self-verification by a single agent is blocked by no-cloning, single-shot uninformativeness about continuous targets, pinching backaction, and conditional independence of the self-generated signal from any external variable.
- **Not supported:** that the prompt's $\Phi_1$ (a $d^1$ of a $d^0$) detects anything; that CHSH lacks a global *deterministic* section; that latency alone changes the collision bound; a sharp refusal index under heterogeneous staleness; identity of the §1.4 table with the published Cabello set; any quantitative weak-measurement trade-off; any machine-checked status.
- **Narrowest defensible claim:** For the context graph of §1.4, $\min_s\|d^0s\|_1=1$; for $e^{\mathrm{CHSH}}$ with entries $\tfrac{17}{40},\tfrac3{40}$, $\min_d\|e-\operatorname{marg}d\|_1=\tfrac45$; under (A-SYNC)+(A-COV) with uniform latency $\tau$, at most $\tau-1$ initial steps are authorized.
- **Next check:** (i) enumerate all $\binom{4}{2}\cdot9=54$ in-basis inner products of §1.4 and all $2^{18}$ assignments (or an exact LP) to re-confirm $\Phi_0=1$; (ii) solve the 16-variable LP for $\Phi_w(e^{\mathrm{CHSH}})$ exactly (expect $4/5$); (iii) encode Theorem Q.4(b) as a finite-sequence lemma in Lean (`List` of reports with a periodicity hypothesis contradicting `Nodup`); (iv) compute the Round 2 Werner pinching purity $13/50$ in exact rationals.

```json
{
  "campaign_id": "FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION",
  "round": 3,
  "status": "VERIFIED_LOCAL_RESULT",
  "status_meaning": "hand-derived in this response; no Lean/Cargo/solver executed; not machine-checked",
  "derived_theorems": [
    "Theorem_Q_3_ContextualityAsOverlapGluingDefect",
    "Theorem_Q_3A_Cabello18Ray_Phi0_Equals_1",
    "Theorem_Q_3B_RationalCHSH_PhiW_Equals_4_over_5",
    "Lemma_2_1_StaleLiveMismatchImpliesDefect",
    "Theorem_Q_4_AsynchronousHypergraphBound",
    "Lemma_Q_5_NoSelfTomography_TwoSignalCollapse"
  ],
  "bounds_established": {
    "cabello_overlap_gluing_defect_Phi0": 1,
    "cabello_context_graph": "9 vertices, 18 edges, 4-regular, connected; H_0(Gamma;Z2) class of normalisation chain nonzero",
    "chsh_rational_model": "p = 17/40 if a xor b = xy else 3/40; S = 14/5",
    "chsh_weighted_gluing_defect_PhiW": "4/5 (exact; lower bound S-2, upper bound via isotropic local m with 15/40, 5/40)",
    "async_collision_bound": "k* <= N+1 <= prod N_a + 1 (latency-independent)",
    "async_sync_rule_refusal_index": "k* <= min(tau, N+1); at most tau-1 initial authorized steps",
    "async_bounded_staleness_product_bound": "K+1 <= prod_a min(T, N_a)",
    "async_hold_and_sync": "authorized changes <= N; total steps <= (tau+1)N + 1",
    "self_measurement_qubit_plus_Z": "purity 1 -> 1/2; l1-coherence 1 -> 0",
    "self_measurement_werner_p_1_5_ZZ": "purity 14/50 -> 13/50"
  },
  "corrections_to_prompt": [
    "Phi_1 = sum |d^1 delta| with delta = d^0 s is identically zero (d^1 d^0 = 0; triple overlaps empty for both systems); replaced by overlap-gluing defect Phi_0 (deterministic) and Phi_w (weighted).",
    "CHSH obstruction is probabilistic, not deterministic-section: Phi_0 = 0, Phi_w = 4/5; phrase 'no global deterministic joint distribution' applies to Cabello only.",
    "k*(tau) <= prod N_i + 1 is the latency-free collision bound; latency content is k* <= tau under a synchronous gluing rule.",
    "Prompt's 'Lemma Q.3' relabelled Lemma Q.5 (Round 2 already used Q.3).",
    "Self-measurement does not always alter the state: equality iff rho commutes with the projectors; in that case the signal is predicted by Signal 1 (H(Y|S1)=0 for a pure claim).",
    "Real vectors suffice for the 18-ray system; C^4 is not needed."
  ],
  "unresolved_obligations": [
    "Round 4: machine enumeration of the 18-ray orthogonality table and exact computation of Phi_0 (expect 1); verify relabelling against the published Cabello table.",
    "Round 4: exact LP for Phi_w(e_CHSH) (expect 4/5); relate Phi_w to contextual fraction CF = 2/5 for the isotropic box.",
    "Round 4: sharp refusal index under heterogeneous bounded staleness and rewiring (only the product bound is proved).",
    "Round 4: quantitative weak-measurement information-disturbance trade-off for self-verification (gentle measurement lemma) and its interaction with the Round 2 lift budget.",
    "Round 4: Lean encoding of Theorem Q.4(b) (periodicity contradicts Nodup) and of Lemma Q.5(c) equality condition.",
    "Carried from Rounds 1-2: stochastic single-shot reports; fractional/thermal lift budgets; effective-Baker decision procedure; majorization form of Theorem Q.2; F2/F4 carrier senses."
  ],
  "claim_hygiene": {
    "supported": "Parity of 9 contexts blocks any global deterministic section for the 18-ray incidence structure and the minimum overlap-gluing defect is exactly 1 (explicit witness); the rational CHSH model has weighted gluing defect exactly 4/5 (dual bound + explicit local model); under a synchronous gluing rule with uniform latency tau, at most tau-1 initial steps can be authorized while the latency-free collision bound N+1 persists; single-agent self-verification is blocked by no-cloning, single-shot uninformativeness, pinching backaction (with exact equality condition), and conditional independence of the self-generated signal from external variables.",
    "not_supported": "That the prompt's d^1-based Phi_1 detects contextuality; that CHSH lacks a global deterministic section; that latency alters the collision bound; a sharp refusal index under heterogeneous staleness; identity of the local 18-ray table with the published one; any weak-measurement quantitative claim; any machine-checked status.",
    "narrowest_claim": "min_s ||d^0 s||_1 = 1 for the context graph of Section 1.4; min_d ||e - marg d||_1 = 4/5 for the 17/40-3/40 CHSH model; under (A-SYNC)+(A-COV) with uniform latency tau, authorized initial steps <= tau - 1.",
    "next_check": "Enumerate in-basis inner products and all 2^18 assignments for Phi_0; solve the CHSH LP exactly; encode Theorem Q.4(b) in Lean; recompute Werner pinching purity 13/50 in exact rationals."
  }
}
```