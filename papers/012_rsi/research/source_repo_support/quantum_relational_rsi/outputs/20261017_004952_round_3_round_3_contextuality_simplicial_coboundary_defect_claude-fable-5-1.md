# Output: round_3_contextuality_simplicial_coboundary_defect.md

- **Timestamp:** 2026-10-17T00:49:52.261391
- **Model:** claude-fable-5-1
- **Round:** 3
- **Duration:** 389.6s
- **Tokens:** In=34796, Out=32729
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_3_contextuality_simplicial_coboundary_defect.md`
- **Continued From:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\outputs\20261017_003918_round_2_round_2_purity_dissipation_and_baker_transcendence_claude-fable-5-1.md`

---

## Thinking Trace

```text

```

---

## Response Content

# Round 3 Record — Sheaf Contextuality, Coboundary Defect, Latency Gluing, No-Self-Tomography

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 3/4**
**Execution note:** No Lean, Cargo, or solver ran. All vector, parity, and rational arithmetic below is hand-computed and not machine-checked. Rounds 1–2 (Theorem Q.1, Lemma Q.2 descent, Lemma Q.3 purity, Theorem Q.2 lift exhaustion) are referenced, not re-derived, and are not treated as external receipts.

**Numbering note.** The prompt's "Lemma Q.3" collides with Round 2's Lemma Q.3 (purity dissipation). The no-self-tomography lemma is labeled **Lemma Q.4** here. Three statements in the prompt are corrected: the coboundary formula for the defect (§1.2 — as written it is identically zero), the scope of "latency induces defect" (§2.3 — requires a report change inside the latency window, and rewiring can hide defects unless the complex is the declared coverage), and the scope of "collapses the coherence" (§3.2 — only off-diagonal blocks in the measured decomposition).

---

## 1. Contextuality as a Gluing Obstruction on the Measurement Complex

### 1.1 Abramsky–Brandenburger data (as used)

- Measurements $X$ (finite), outcomes $O$ (finite), cover $\mathcal{M}=\{C_1,\dots,C_n\}$, $C_i\subseteq X$ maximal jointly measurable contexts, $\bigcup_iC_i=X$.
- Event presheaf $\mathcal{E}(U)=O^U$ with restriction $s\mapsto s|_{U'}$.
- Empirical model $e=(e_C)_{C\in\mathcal{M}}$, $e_C$ a probability distribution on $O^C$, compatible: $e_C|_{C\cap C'}=e_{C'}|_{C\cap C'}$ (no-signalling).
- Support $\mathcal{S}_e(C)=\{s\in O^C:e_C(s)>0\}$.
- **Non-contextual (probabilistic):** $\exists$ distribution $\mu$ on $O^X$ with $\mu|_C=e_C$ for all $C$.
- **Strongly contextual:** no $g\in O^X$ with $g|_C\in\mathcal{S}_e(C)$ for all $C$.
- **Measurement complex** $\mathcal{X}$: vertices = contexts $C_i$; an edge $(i,j)$ iff $C_i\cap C_j\neq\emptyset$; a 2-face $(i,j,k)$ iff $C_i\cap C_j\cap C_k\ne\emptyset$ (nerve of the cover). Čech cochains $\check C^p(\mathcal{X};\mathcal{F})$ for an abelian presheaf $\mathcal{F}$, with $d^0s(i,j)=s_j|_{ij}-s_i|_{ij}$, $d^1\delta(i,j,k)=\delta(j,k)|_{ijk}-\delta(i,k)|_{ijk}+\delta(i,j)|_{ijk}$.

### 1.2 Correction: the prompt's $\Phi_1$ vanishes identically

The prompt defines $\delta(u,v)=s_v|_{uv}-s_u|_{uv}$ from a family of local sections $(s_u)$, i.e. $\delta=d^0s$, and then sets $\Phi_1([\delta])=\sum_\sigma|(d^1\delta)(\sigma)|$. Since $d^1d^0=0$ in any Čech complex, $d^1\delta=0$ on every 2-face for every choice of $(s_u)$, so this $\Phi_1$ is $0$ for every empirical model, contextual or not. As written, "$\Phi_1([\delta])>0$" cannot hold. The prompt formula is routed $\mathsf{rejected}$.

The obstruction lives one degree lower (edge mismatch of 0-cochains constrained to the support), or in a *different* cochain complex (the parity/incidence complex of §1.4), or in Abramsky–Mansfield–Barbosa's relative cohomology $\check H^1(\mathcal{M},\tilde{\mathcal{F}}_{C_0})$ — where the relevant object is a 1-*cocycle* $z=d^0c$ with $c\in C^0(\mathcal{F})$ that is not a coboundary in the *relative* presheaf. In all three cases, $d^1z=0$; the class, not the coboundary of the class, carries the obstruction.

### 1.3 Defect functionals (declared definitions)

**Definition 1.1 (Deterministic gluing defect).** For an empirical model $e$ on $\mathcal{X}$,
$$\Phi_{\mathrm{glue}}(e)\;=\;\min_{\,s\in\prod_i\mathcal{S}_e(C_i)}\ \sum_{(i,j)\in\mathcal{X}_1}\ \big\|\,s_j|_{ij}-s_i|_{ij}\,\big\|_1,$$
where $\|\cdot\|_1$ counts disagreements on the overlap (outcomes embedded as integers). $\Phi_{\mathrm{glue}}(e)=0$ iff some family of support sections glues to a global $g\in O^X$, i.e. iff $e$ is *not* strongly contextual.

**Definition 1.2 (Contextual fraction, Abramsky–Barbosa–Mansfield).** $\mathrm{NCF}(e)=\max\{\lambda\in[0,1]: e=\lambda e^{\mathrm{NC}}+(1-\lambda)e'\}$ with $e^{\mathrm{NC}}$ non-contextual and $e'$ an arbitrary no-signalling model; $\mathrm{CF}(e)=1-\mathrm{NCF}(e)$. $\mathrm{CF}(e)=0$ iff $e$ is non-contextual.

**Definition 1.3 (Parity cochain complex).** For a KS-type model with rays $R$ and contexts $\mathcal{C}$ (orthonormal bases), let $C^0=\mathbb{Z}_2^{R}$, $C^1=\mathbb{Z}_2^{\mathcal{C}}$, $(da)(C)=\sum_{r\in C}a(r)$, and $d^\top:C^1\to C^0$, $(d^\top b)(r)=\sum_{C\ni r}b(C)$. Write $H^1_{\mathrm{par}}=\operatorname{coker}d$.

`OVERLAP_GLUING_REFUSAL` is the terminal assigned when a promotion requires a glued global section and the relevant defect is nonzero.

### 1.4 Theorem Q.3 (Contextuality as Coboundary Defect — corrected form)

**Theorem Q.3.**
(a) *Cabello 18-ray system in $\mathbb{R}^4\subset\mathbb{C}^4$ (Target 6).* The model is strongly contextual; $\Phi_{\mathrm{glue}}=1$ exactly; and the all-ones cochain $\mathbf 1\in C^1$ represents a nonzero class $[\mathbf 1]\ne0$ in $H^1_{\mathrm{par}}$.
(b) *Rational CHSH model (Target 8)* with $|\Phi^+\rangle$ and correlators $E_{00}=E_{01}=E_{10}=\tfrac45$, $E_{11}=-\tfrac{44}{125}$: the model is not strongly contextual ($\Phi_{\mathrm{glue}}=0$) but is contextual, with $\mathrm{CF}\ge\tfrac{47}{125}>0$.
(c) In both cases any promotion rule requiring a glued global deterministic section (a) or a global joint distribution (b) routes to `OVERLAP_GLUING_REFUSAL`.

*Proof of (a).* Contexts and rays (bar denotes $-1$; vectors unnormalized):

| $C$ | rays |
|---|---|
| 1 | 0001, 0010, 1100, 1$\bar1$00 |
| 2 | 0001, 0100, 1010, 10$\bar1$0 |
| 3 | 1$\bar1\bar1$1, 1$\bar1$1$\bar1$, 1100, 0011 |
| 4 | 1$\bar1\bar1$1, 11$\bar1\bar1$, 1010, 0101 |
| 5 | 0010, 0100, 1001, 100$\bar1$ |
| 6 | 1$\bar1$1$\bar1$, 11$\bar1\bar1$, 1001, 0110 |
| 7 | 1$\bar1$00, 0011, 111$\bar1$, 11$\bar1$1 |
| 8 | 10$\bar1$0, 0101, 111$\bar1$, 1$\bar1$11 |
| 9 | 100$\bar1$, 0110, 11$\bar1$1, 1$\bar1$11 |

Orthogonality within each row is checked entrywise (e.g. row 7: $111\bar1\cdot11\bar11=1+1-1-1=0$; row 9: $11\bar11\cdot1\bar111=1-1-1+1=0$). Each of the 18 rays occurs in exactly two contexts; the 18 overlaps are single rays, giving $\mathcal{X}_1$ = 18 edges, each context of degree 4, no triple overlaps (so $\mathcal{X}_2=\emptyset$, which is another way of seeing that a triangle-based $d^1$ carries nothing here).

Support: for a projective measurement in basis $C$, exactly one outcome 1 occurs, so $\mathcal{S}_e(C)=\{s\in\{0,1\}^C:\sum_{r\in C}s(r)=1\}$.

*Strong contextuality (parity).* A global $g\in\{0,1\}^R$ with $g|_C\in\mathcal{S}_e(C)$ for all $C$ satisfies $\sum_C\sum_{r\in C}g(r)=9$. Since each ray lies in exactly two contexts, the same double sum equals $2\sum_rg(r)$, even. Contradiction.

*$\Phi_{\mathrm{glue}}=1$.* For any $s\in\prod_C\mathcal{S}_e(C)$ let $m$ = number of rays assigned 1 in both their contexts and $x$ = number assigned 1 in exactly one. Counting 1's over all contexts: $2m+x=9$, so $x$ is odd and $x\ge1$. The edge mismatch count is exactly $x$, so $\Phi_{\mathrm{glue}}\ge1$. Attainment: take the matching $\{(1,2)\!:\!0001,\ (3,4)\!:\!1\bar1\bar11,\ (5,6)\!:\!1001,\ (7,8)\!:\!111\bar1\}$ and assign 1 to each matched ray in both its contexts; in context 9 assign 1 to $1\bar111$ (shared with context 8, where it is 0 since 8's single 1 is on $111\bar1$). Every context has exactly one 1; mismatch occurs on the single edge $(8,9)$. Hence $\Phi_{\mathrm{glue}}=1$.

*Cohomology class.* The global-section condition is $da=\mathbf 1$ in $C^1$ (parity relaxation of "exactly one"). Over $\mathbb{Z}_2$, $\operatorname{im}d=(\ker d^\top)^\perp$. Now $d^\top\mathbf 1=0$ since $(d^\top\mathbf 1)(r)=|\{C\ni r\}|=2\equiv0$, so $\mathbf 1\in\ker d^\top$; and $\langle\mathbf 1,\mathbf 1\rangle=9\equiv1\ne0$. Thus $\mathbf 1\notin\operatorname{im}d$ and $[\mathbf 1]\ne0$ in $H^1_{\mathrm{par}}$. This is the parity argument restated as a nonzero cohomology class on a genuine cochain complex. $\square$

*Proof of (b).* For $|\Phi^+\rangle$ with real-plane measurement angles, $E(a,b)=\cos(a-b)$. Choose $a_0-b_0=a_0-b_1=a_1-b_0=\phi$, $a_1-b_1=3\phi$ (e.g. $a_0=0,\ b_0=-\phi,\ a_1=2\phi,\ b_1=-\phi$ — wait, set $b_0=\phi,\ b_1=-\phi,\ a_0=0,\ a_1=2\phi$: then $a_0-b_0=-\phi$, $a_0-b_1=\phi$, $a_1-b_0=\phi$, $a_1-b_1=3\phi$; cosines agree) with $\cos\phi=\tfrac45$. Then $\cos3\phi=4\cos^3\phi-3\cos\phi=\tfrac{256}{125}-\tfrac{300}{125}=-\tfrac{44}{125}$. Outcome tables: $p(++)=p(--)=\tfrac{1+E}{4}$, $p(+-)=p(-+)=\tfrac{1-E}{4}$, giving $\tfrac9{20},\tfrac1{20}$ for $E=\tfrac45$ and $\tfrac{81}{500},\tfrac{169}{500}$ for $E=-\tfrac{44}{125}$. All entries are positive rationals, marginals are uniform (no-signalling holds), and $\mathcal{S}_e(C)=O^C$ for every context, so any family of support sections glues: $\Phi_{\mathrm{glue}}=0$.

CHSH value $S=E_{00}+E_{01}+E_{10}-E_{11}=\tfrac{12}5+\tfrac{44}{125}=\tfrac{344}{125}$. For any non-contextual $e^{\mathrm{NC}}$, $S\le2$ (deterministic sections give $\pm2$; convexity). For any no-signalling $e'$, $S\le4$. If $e=\lambda e^{\mathrm{NC}}+(1-\lambda)e'$, then $\tfrac{344}{125}\le2\lambda+4(1-\lambda)=4-2\lambda$, so $\lambda\le\tfrac12\left(4-\tfrac{344}{125}\right)=\tfrac{78}{125}$. Hence $\mathrm{NCF}\le\tfrac{78}{125}$ and $\mathrm{CF}\ge\tfrac{47}{125}$. (ABM's theorem gives equality with the maximal normalized Bell violation; the other seven CHSH variants were not evaluated here, so only $\ge$ is claimed.) Quantum realizability: $\tfrac{344}{125}=2.752<2\sqrt2$, and the construction is explicit. $\square$

*Proof of (c).* A rule that promotes only on a glued global section fails in (a) because none exists (strong contextuality) and in (b) because no joint distribution reproduces $e$ ($\mathrm{CF}>0$). $\square$

**Remark (what the defect is not).** $\Phi_{\mathrm{glue}}$ and $\mathrm{CF}$ are properties of the empirical model, not of a trajectory; they become trajectory-relevant only via a promotion rule that demands gluing. This is the same shape as Round 1: the obstruction is in what can be certified across the boundary, not in the dynamics.

---

## 2. Communicating Quantum Nodes under Latency, Loss, and Rewiring

### 2.1 Model (declared)

- Nodes $a\in V$, $|V|=n$. Node $a$ runs its own $\mathcal{U}_Q^{(a)}$ with report carrier $C_a$, $N_a=|\operatorname{report}_a(\mathcal{S}_Q^{(a)})|$. Live joint report $\pi(k)=(\pi_a(k))_a\in\prod_aC_a$.
- **Coverage complex** $K$: vertices $V$, edges $E\subseteq\binom V2$ = pairs whose boundary syndromes are *required* to agree for a joint promotion. (Declared once; it is the analogue of the cover $\mathcal{M}$.)
- **Live link set** $E_k\subseteq E$ at step $k$ (rewiring); latency $\tau_{ab}(k)\in\{0,\dots,\tau\}$ on live links; a lost packet or a dead link leaves the receiver's view frozen at its last delivered value, so effectively $\tau_{ab}(k)$ can exceed $\tau$ on $E\setminus E_k$.
- Node $a$'s **view** $\hat\pi^{(a)}(k)$: $\hat\pi^{(a)}_a(k)=\pi_a(k)$; $\hat\pi^{(a)}_b(k)=\pi_b(k-\tau_{ab}(k))$ for $(a,b)\in E$.
- **Overlap cochain** $\delta_k(a,b)=\hat\pi^{(a)}_b(k)\ominus\pi_b(k)$ (formal difference; indicator of inequality suffices), on edges of $K$ (not of $E_k$).
- **Defect** $\Phi_1(\delta_k)=\sum_{(a,b)\in E}\big[\hat\pi^{(a)}_b(k)\ne\pi_b(k)\big]+\big[\hat\pi^{(b)}_a(k)\ne\pi_a(k)\big]$.
- **Promotion rule:** a joint step $k$ is admitted only if (i) the joint report-grounded strict-improvement claim $\pi(k)\succ_{\mathrm{rep}}\pi(k-1)$ holds (Round 1 on the product carrier), and (ii) $\Phi_1(\delta_k)=0$ (the views glue to a single global section, namely $\pi(k)$).

### 2.2 Lemma 2.1 (Defect characterization)

$\Phi_1(\delta_k)=0$ iff for every $(a,b)\in E$, $\pi_b$ is constant on $[k-\tau_{ab}(k),k]$ and $\pi_a$ is constant on $[k-\tau_{ba}(k),k]$.

*Proof.* $\hat\pi^{(a)}_b(k)=\pi_b(k-\tau_{ab}(k))$ equals $\pi_b(k)$ iff the report did not change over that window (if it changed and returned, equality holds, which is included in "constant on the endpoints"; the precise condition is $\pi_b(k-\tau_{ab}(k))=\pi_b(k)$). $\square$

### 2.3 Theorem Q.3.2 (Asynchronous horizon)

Let $T_{\mathrm{coll}}=\min\{k:\exists i<k,\ \pi(i)=\pi(k)\}$ and $T_{\mathrm{glue}}=\min\{k\ge2:\Phi_1(\delta_k)>0\}$ ($\infty$ if never). Then:

(a) $T_{\mathrm{coll}}\le\prod_aN_a+1$, by Round 1 Theorem Q.1 applied to the product carrier; at $T_{\mathrm{coll}}$ the joint improvement claim fails (`REPORT_COLLISION`).
(b) $k^*=\min\{T_{\mathrm{coll}},T_{\mathrm{glue}}\}\le\prod_aN_a+1$, with terminal `OVERLAP_GLUING_REFUSAL` if $T_{\mathrm{glue}}<T_{\mathrm{coll}}$.
(c) If some edge $(a,b)\in E$ has $\tau_{ab}(k)\ge1$ at every step $k\ge2$ and node $b$'s report changes at some step $k_0\le T_{\mathrm{coll}}-1$ (which is forced whenever node $b$ carries its own node-level strict claim, by Round 1 applied to $C_b$), then $T_{\mathrm{glue}}\le k_0+1$, and the terminal is `OVERLAP_GLUING_REFUSAL` strictly before joint collision unless $k_0+1\ge T_{\mathrm{coll}}$.
(d) Packet loss and rewiring only enlarge $\tau_{ab}(k)$ (a frozen view is a view with larger effective latency), so (b)–(c) hold with $\tau$ replaced by the effective latency; they never restore gluing.

*Proof.* (a) Pigeonhole on $\prod_aC_a$, then Lemma Q.2(a) of Round 1 on the product report. (b) $k^*$ is a minimum of two quantities one of which is bounded by (a). (c) At step $k_0+1$, $\hat\pi^{(a)}_b(k_0+1)=\pi_b(k_0+1-\tau_{ab}(k_0+1))$ with $\tau\ge1$; if $\pi_b(k_0+1)\ne\pi_b(k_0)$ take $k_0$ to be that change step; then the window $[k_0+1-\tau,\,k_0+1]$ contains $k_0$ and $k_0+1$ and the endpoints differ unless the report returned to its value at $k_0+1-\tau$, in which case node $b$ has a node-level collision at that step anyway. Either way a terminal is hit by $k_0+1$. (d) Immediate from the model. $\square$

**Scope corrections to the prompt.**
1. "Latency $\tau\ge1$ induces $\Phi_1>0$" is supported only together with a report *change* inside the window (Lemma 2.1). A trajectory whose reports never change has $\Phi_1=0$ at every step — and collides at $k=2$.
2. If the defect is computed over the *live* link set $E_k$ rather than the coverage complex $E$, rewiring can remove the mismatched edge and make the defect vanish vacuously. Under the declared model the defect is computed on $E$; a defect computed on $E_k$ is routed $\mathsf{not\_admitted}$ as a gluing certificate.

### 2.4 Two-node witness ($\tau=1$, $N_1=N_2=2$)

$C_1=C_2=\{1,2\}$, $E=\{(1,2)\}$, $\tau_{12}=\tau_{21}=1$. Trajectory: $\pi(1)=(1,1)$, $\pi(2)=(2,1)$, $\pi(3)=(2,2)$, $\pi(4)=(1,2)$.

| $k$ | $\pi(k)$ | $\hat\pi^{(1)}(k)$ | $\hat\pi^{(2)}(k)$ | $\Phi_1$ | joint claim | terminal |
|---|---|---|---|---|---|---|
| 1 | (1,1) | (1,·) | (·,1) | — | — | start |
| 2 | (2,1) | (2,1) | (1,1) | 1 | — | `OVERLAP_GLUING_REFUSAL` |
| 3 | (2,2) | (2,1) | (2,2) | 1 | — | — |
| 4 | (1,2) | (1,2) | (2,2) | 1 | — | — |
| 5 | any | | | | collision by $k\le5$ | `REPORT_COLLISION` bound |

Here $T_{\mathrm{glue}}=2<T_{\mathrm{coll}}\le5=\prod N_a+1$, so $k^*=2$ with mode `OVERLAP_GLUING_REFUSAL`. With $\tau=0$ the same trajectory has $\Phi_1=0$ at every step and reaches $k^*=5$ by collision. The shift of mode is attributable to latency alone, under the declared model.

---

## 3. No-Self-Tomography and Two-Signal Collapse

### 3.1 FV3 as used

Promotion of a candidate step requires Signal 1 (proposal by generator $g$) and Signal 2 (verdict by a verifier $v$) with $\mathsf{IsIndependentVerifier}(g,v)$. **Declared predicate:** $\mathsf{IsIndependentVerifier}(g,v)$ holds iff (i) $v$'s verdict is obtained by a measurement on a physical system $\mathcal{H}_V$ disjoint from $g$'s state register $\mathcal{H}_G$, (ii) the measurement $\{Q_m\}$ on $\mathcal{H}_V$ and the coupling $U_{GV}$ are fixed by protocol and not selectable by $g$, and (iii) the record of $m$ is not writable by $g$. Then $\neg\mathsf{IsIndependentVerifier}(g,g)$ by (i). The content of Lemma Q.4 is that self-measurement also fails (ii)'s intent informationally, and that the backaction is itself a Round-2 unital step.

### 3.2 Backaction (explicit)

Projective self-measurement $\{P_m\}$ with record register $M$: $\rho\mapsto\sum_mP_m\rho P_m\otimes|m\rangle\langle m|_M$; marginal on $\mathcal{H}_G$ is the pinching $\mathcal{P}(\rho)=\sum_mP_m\rho P_m$.

*Qubit, $Z$-measurement.* $\rho=\begin{pmatrix}p&c\\ \bar c&1-p\end{pmatrix}\mapsto\begin{pmatrix}p&0\\0&1-p\end{pmatrix}$. Purity $p^2+(1-p)^2+2|c|^2\to p^2+(1-p)^2$ (strict drop iff $c\ne0$); entropy non-decreasing (Lemma Q.3, pinching is unital). Example $\rho=|+\rangle\langle+|$: $P_2:1\to\tfrac12$, $S:0\to1$ bit, coherence $|c|:\tfrac12\to0$.

*Weak version (strength $\epsilon\in[0,1]$).* Kraus $A_0=\operatorname{diag}\!\big(\sqrt{\tfrac{1+\epsilon}2},\sqrt{\tfrac{1-\epsilon}2}\big)$, $A_1=\operatorname{diag}\!\big(\sqrt{\tfrac{1-\epsilon}2},\sqrt{\tfrac{1+\epsilon}2}\big)$; $A_0^\dagger A_0+A_1^\dagger A_1=I$. Diagonal unchanged; off-diagonal $c\mapsto c\sqrt{1-\epsilon^2}$; outcome-0 probability $\tfrac12+\epsilon(p-\tfrac12)$. Information about $p$ scales with $\epsilon$, coherence loss with $1-\sqrt{1-\epsilon^2}$; $\epsilon=1$ is the projective case. There is no $\epsilon>0$ with zero backaction on a state with $c\ne0$.

**Scope correction.** "Collapses the coherence of the state" is supported only for coherences between the measured blocks; coherences inside a block of a degenerate $P_m$ survive. The claim as stated is narrowed accordingly.

### 3.3 Lemma Q.4 (No-Self-Tomography and Two-Signal Collapse)

**Lemma Q.4.** Let $g$ propose $\rho_{k+1}=\mathcal{E}_k(\rho_k)$ and attempt to verify the claim $\rho_{k+1}\succ\rho_k$ by measurements on its own register. Then:
1. *(No cloning.)* There is no CPTP map $\Delta$ with $\Delta(\rho)=\rho\otimes\rho$ for all $\rho\in\mathcal{S}_Q$; hence $g$ cannot manufacture the ensemble of copies that tomography of an unknown $\rho_{k+1}$ requires.
2. *(Backaction.)* Every self-measurement is a budget-free unital step on $\mathcal{H}_G$ (marginally), so by Round 2 it never increases $P_2$ or decreases $S$; a verification that "purity increased" alters the quantity it reports on, strictly unless $\rho_{k+1}$ is already block-diagonal in the measured decomposition.
3. *(Coupling / collapse.)* If the measurement $\{P_m\}$ is selectable by $g$ (which is the case for self-measurement, since $g$ controls its own register), then $g$ can choose $P_1=|\psi\rangle\langle\psi|$ for its proposed pure $\rho_{k+1}=|\psi\rangle\langle\psi|$, obtaining outcome 1 with probability 1 for every proposal. The verdict $V$ is then a deterministic function of the proposal, so $I(V;\ \mathbb{1}[\rho_{k+1}\succ\rho_k])=0$. Signal 2 carries no information beyond Signal 1: `TWO_SIGNAL_COLLAPSE`. Under the declared predicate, $\neg\mathsf{IsIndependentVerifier}(g,g)$ holds by clause (i), and clause (ii) fails informationally as just shown.
4. *(What independence buys, and its limit.)* With $v$ on a disjoint $\mathcal{H}_V$ and protocol-fixed $(U_{GV},\{Q_m\})$, the verdict distribution $\operatorname{Tr}[(I\otimes Q_m)U(\rho_{k+1}\otimes\sigma_V)U^\dagger]$ is not selectable by $g$ and generically depends on $\rho_{k+1}$; but from a single copy it is a single sample, so the verdict is a noisy binary with error bounded away from 0 unless $\rho_{k+1}$ and the hypothesis state are orthogonal. Confidence amplification requires $n$ fresh copies (each a prepared resource, hence lift budget) with error decaying as $e^{-nD}$ for the quantum Chernoff exponent $D$ (cited, $\mathsf{evidence\_only}$).

*Proof.*
(1) Suppose $\Delta(\rho)=\rho\otimes\rho$ for all $\rho$. Take $\rho=\tfrac12(\rho_1+\rho_2)$ with $\rho_1\ne\rho_2$. Linearity gives $\Delta(\rho)=\tfrac12(\rho_1\otimes\rho_1+\rho_2\otimes\rho_2)$, while $\rho\otimes\rho=\tfrac14(\rho_1\otimes\rho_1+\rho_1\otimes\rho_2+\rho_2\otimes\rho_1+\rho_2\otimes\rho_2)$. Subtracting: $\tfrac14(\rho_1-\rho_2)\otimes(\rho_1-\rho_2)=0$, forcing $\rho_1=\rho_2$. Contradiction.
(2) $\mathcal{P}(I)=\sum_mP_m=I$, so the pinching is unital; apply Lemma Q.3 (Round 2). Equality iff the spectrum is unchanged, which for a pinching means $\rho$ commutes with all $P_m$.
(3) $\operatorname{Tr}(P_1\rho_{k+1})=\langle\psi|\psi\rangle=1$. A random variable that is almost surely constant has zero mutual information with anything. The agent's "verdict" is thus computable from the proposal alone.
(4) The first part is the definition; the second is the statement that a single Bernoulli sample with success probability $q\in(0,1)$ cannot decide between two hypotheses with zero error; the Chernoff statement is cited, not derived. $\square$

**Remark (self-measurement and Round 1).** A self-verification outcome $m$ is itself a report-valued object with $|M|$ values. If the agent's improvement certificate is "outcome $m=1$ observed", the certificate carrier has $N\le|M|$ values and Theorem Q.1 applies: at most $|M|$ distinct self-verification reports before collision. Self-verification does not enlarge the horizon; it is a report like any other, with the added defect that the proposer chose the panel.

---

## 4. Partial Joint Horizon (carried obligation from Rounds 1–2)

Under the union of the declared assumptions ((A-REP), (A-LIFT), the §2.1 communication model, and the FV3 predicate of §3.1), a trajectory carrying a strict-improvement claim is obstructed by
$$k^*\;\le\;\min\Big\{\ N+1,\ \ B_0+1\ (\text{purification claims}),\ \ T_{\mathrm{glue}},\ \ \textstyle\prod_aN_a+1\ (\text{multi-node})\Big\},$$
with terminal `REPORT_COLLISION`, `LIFT_BUDGET_EXHAUSTION`, or `OVERLAP_GLUING_REFUSAL` according to which minimum is attained, and with any self-verified step routed $\mathsf{evidence\_only}$ rather than $\mathsf{authorized}$ (`TWO_SIGNAL_COLLAPSE`). The external-lift accounting for stabilizer-orbit escape is still not integrated into this expression; it is forwarded.

---

## 5. Epistemic Routing (PG3)

| Item | Terminal | Grounds |
|---|---|---|
| Prompt's $\Phi_1([\delta])=\sum\lvert d^1d^0s\rvert$ | $\mathsf{rejected}$ | identically zero ($d^1d^0=0$) |
| Definitions 1.1–1.3 | $\mathsf{authorized}$ (as declared) | standard objects; §1.3 |
| Theorem Q.3(a): strong contextuality, $\Phi_{\mathrm{glue}}=1$, $[\mathbf 1]\ne0$ | $\mathsf{authorized}$ | parity proof + explicit attaining assignment; vector table hand-checked |
| Theorem Q.3(b): $\mathrm{CF}\ge47/125$ | $\mathsf{authorized}$ | convexity bound from explicit rational tables |
| $\mathrm{CF}=47/125$ (equality) | $\mathsf{unresolved}$ | other CHSH variants not evaluated |
| AB relative-cohomology obstruction nonvanishing for Cabello (every $s_0$) | $\mathsf{unresolved}$ | not computed here |
| Lemma 2.1, Theorem Q.3.2 | $\mathsf{authorized}$ under §2.1 model | proved |
| "Latency alone induces defect" | $\mathsf{not\_admitted}$ | needs a report change in the window |
| Defect computed on live links $E_k$ | $\mathsf{not\_admitted}$ as certificate | rewiring can hide mismatch |
| §3.2 backaction formulas (projective, weak) | $\mathsf{authorized}$ | explicit Kraus arithmetic |
| "Collapses the coherence" (all coherence) | $\mathsf{not\_admitted}$ | narrowed to measured blocks |
| Lemma Q.4(1)–(3) | $\mathsf{authorized}$ | proved |
| Lemma Q.4(4) Chernoff amplification | $\mathsf{evidence\_only}$ | cited |
| §4 joint horizon | $\mathsf{authorized}$ as a minimum of established bounds; integration incomplete | external-lift term missing |
| Hand-checked vector table, rational arithmetic | $\mathsf{evidence\_only}$ until machine-checked | no tool ran |

---

## 6. Claim Hygiene Summary

- **Supported:** In this model, the Cabello 18-ray cover admits no global deterministic section, the minimal edge-mismatch over support sections is exactly 1, and the all-ones context cochain is a nonzero class in the $\mathbb{Z}_2$ parity complex; the rational CHSH model with $S=344/125$ has contextual fraction at least $47/125$ while its deterministic gluing defect is 0; under the declared communication model, gluing fails exactly when a report changes inside a latency window, the combined horizon is bounded by $\prod_aN_a+1$, and a two-node $\tau=1$ witness shifts the terminal from collision at 5 to gluing refusal at 2; self-measurement is a unital (pinching) step with explicit coherence loss, no CPTP map clones, and a proposer-selected verification panel yields a verdict with zero mutual information with the improvement predicate.
- **Not supported:** the prompt's triangle-coboundary defect formula; that latency by itself produces a defect; that rewiring-based defects are visible on the live-link complex; that self-measurement destroys all coherence; equality $\mathrm{CF}=47/125$; nonvanishing of the AB relative-cohomology class for every local section of Cabello; any Chernoff-rate statement as a theorem of this round; machine-checked status of the vector and rational arithmetic.
- **Narrowest defensible claim:** Under the declared models, a promotion rule that requires a glued global section is refused on the Cabello and rational-CHSH models (deterministic and probabilistic senses respectively), is refused on any communicating complex at the first step where a report changes inside a nonzero latency window, and cannot be satisfied by a self-measured verdict, which routes to $\mathsf{evidence\_only}$.
- **Next check:** (i) enumerate all $3^{9}\cdot$… more practically all $4^9=262144$ support assignments for Cabello by script and confirm $\min$ mismatch $=1$ and the parity rank computation over $\mathbb{Z}_2$ (rank of the $9\times18$ incidence matrix $=8$, $\mathbf 1\notin$ row space); (ii) solve the ABM linear program for the §1.4(b) tables to settle $\mathrm{CF}$; (iii) simulate the §2.4 two-node model for random trajectories to confirm $T_{\mathrm{glue}}\le$ first-change$+1$; (iv) check the weak-measurement Kraus identities symbolically.

```json
{
  "campaign_id": "FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION",
  "round": 3,
  "status": "VERIFIED_LOCAL_RESULT",
  "status_meaning": "hand-derived in this response; no Lean/Cargo/solver executed; not machine-checked",
  "derived_theorems": [
    "Theorem_Q_3_ContextualityAsGluingDefect (corrected form: edge-level defect and Z2 parity cohomology class, not triangle coboundary)",
    "Theorem_Q_3a_Cabello18_StrongContextuality_PhiGlue_eq_1_ParityClassNonzero",
    "Theorem_Q_3b_RationalCHSH_344_over_125_CF_ge_47_over_125",
    "Lemma_2_1_LatencyDefectCharacterization",
    "Theorem_Q_3_2_AsynchronousHorizon_min(T_coll,T_glue)_le_prodN+1",
    "Lemma_Q_4_NoSelfTomography_TwoSignalCollapse (relabeled from prompt's Lemma Q.3)",
    "Partial_JointHorizon_Section4"
  ],
  "bounds_established": {
    "cabello_phi_glue": 1,
    "cabello_contexts": 9,
    "cabello_rays": 18,
    "cabello_overlap_edges": 18,
    "cabello_triple_overlaps": 0,
    "chsh_rational_S": "344/125",
    "chsh_rational_CF_lower_bound": "47/125",
    "multi_node_k_star": "min(T_coll, T_glue) <= prod_a N_a + 1",
    "latency_refusal_time": "<= (first in-window report change) + 1",
    "two_node_witness_tau1": {"k_star": 2, "mode": "OVERLAP_GLUING_REFUSAL"},
    "two_node_witness_tau0": {"k_star_bound": 5, "mode": "REPORT_COLLISION"},
    "self_measurement_plus_state": {"purity": "1 -> 1/2", "entropy_bits": "0 -> 1", "coherence": "1/2 -> 0"},
    "weak_measurement_coherence_factor": "sqrt(1 - eps^2)",
    "self_verified_verdict_mutual_information": 0,
    "joint_horizon_partial": "min(N+1, B_0+1, T_glue, prod N_a + 1)"
  },
  "corrections_to_prompt": [
    "Triangle coboundary defect sum of |d^1 d^0 s| is identically zero; replaced by edge-level support-constrained mismatch and Z2 parity cohomology class.",
    "Latency induces a defect only together with a report change inside the window; defect must be computed on the declared coverage complex, not the live link set.",
    "Self-measurement removes only coherences between measured blocks; narrowed accordingly.",
    "Lemma numbering: no-self-tomography lemma relabeled Q.4 to avoid collision with Round 2 Lemma Q.3."
  ],
  "unresolved_obligations": [
    "Round 4: compute the Abramsky-Mansfield-Barbosa relative cohomology obstruction for the Cabello model for each local section (or cite a checked computation) and relate it to the Z2 parity class used here.",
    "Round 4: solve the contextual-fraction LP for the rational CHSH tables to settle CF = 47/125 or larger.",
    "Round 4: integrate the external-lift budget for stabilizer/transversal orbit escape into the joint horizon expression (carried from Rounds 1-2).",
    "Round 4: stochastic single-shot reports and single-copy verification: bound the verdict error of an independent verifier as a function of copies consumed from the lift budget (quantum Chernoff), and fold into the joint horizon.",
    "Round 4: justify or replace (A-LIFT.2) (carried from Round 2).",
    "Round 4: F2/F4 finiteness senses and algebraic-eigenvalue enclosures (carried).",
    "Tooling: brute-force Cabello support enumeration and Z2 rank check; ABM LP; two-node latency simulation; Lean encodings carried from Rounds 1-2."
  ],
  "claim_hygiene": {
    "supported": "Cabello 18-ray: no global deterministic section, minimal edge mismatch exactly 1, nonzero Z2 parity class; rational CHSH S=344/125 with CF >= 47/125 and zero deterministic gluing defect; latency-window characterization of gluing failure with horizon <= prod N_a + 1 and an explicit two-node tau=1 witness at k*=2; self-measurement as unital pinching with explicit coherence loss; no-cloning; proposer-selected verification panel yields a verdict with zero mutual information with the improvement predicate.",
    "not_supported": "Prompt's triangle-coboundary defect formula; latency alone inducing defect; defects on live-link complexes as certificates; total coherence loss under self-measurement; CF equality; AB relative-cohomology nonvanishing for all local sections; Chernoff amplification as a theorem here; machine-checked arithmetic.",
    "narrowest_claim": "Under the declared models, any promotion rule requiring a glued global section is refused on the Cabello and rational-CHSH models, is refused on a communicating complex at the first step where a report changes inside a nonzero latency window, and cannot be satisfied by a self-measured verdict, which routes to evidence_only.",
    "next_check": "Brute-force enumeration of Cabello support assignments (min mismatch = 1) and Z2 rank of the 9x18 incidence matrix; ABM LP for the CHSH tables; simulation of the two-node latency model; symbolic check of the weak-measurement Kraus identities."
  }
}
```