# Output: round_1_quantum_relational_axioms_and_povm_finitude.md

- **Timestamp:** 2026-10-17T00:07:30.775731
- **Model:** claude-fable-5-1
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_1_quantum_relational_axioms_and_povm_finitude.md`
- **Input Tokens:** 3746
- **Output Tokens:** 16384

---

## Response Content

# Round 1 Record — Quantum Relational Universe, POVM Report Finitude, Horizon Bounds

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 1/4**
**Execution note:** No Lean, Cargo, or solver ran. Everything below is a hand-derived specification and proof sketch at the level of rigor of a written mathematics note. References to "Monograph 012-000" and "Paper 006" are taken as the specification handed to this round; they are not treated as external receipts. Two items in the prompt are corrected below (§6.1 stabilizer count; §6.3 Eastin–Knill framing).

---

## 1. Definitions and Axioms

### 1.1 Container-free relational primitives (Monograph 012-000 §1, as specified)

**Axiom R1 (Primitive Difference, Zero-Relation).** There is a set of differences $D$ with a distinguished element $0_R \in D$ (the null difference). States are identified only up to the differences that separate them: for a state space $\mathcal{S}$ there is a map $\delta : \mathcal{S}\times\mathcal{S} \to D$ with $\delta(s,s) = 0_R$ and $\delta(s,t) = 0_R \Rightarrow s = t$. No ambient coordinate chart is a primitive; coordinates, where used, are derived from $\delta$.

**Axiom R2 (No-Outside / Internal Relational Closure).** Every evaluation operation available to an agent is either (a) an endomorphism $\mathcal{E}:\mathcal{S}\to\mathcal{S}$ internal to the universe, or (b) a *finite observer panel* $\Pi = \{E_1,\dots,E_M\}$ with a finite outcome alphabet. No evaluation may invoke an unindexed oracle $\Omega : \mathcal{S} \to \mathbb{R}$ that is not itself realized by (a) or (b).

**Axiom PG3 (Six-Terminal Epistemic Routing).** Every candidate transition or claim $c$ is assigned exactly one terminal
$$\operatorname{route}(c) \in T_6 := \{\mathsf{evidence\_only},\ \mathsf{authorized},\ \mathsf{rejected},\ \mathsf{unresolved},\ \mathsf{refused},\ \mathsf{not\_admitted}\}.$$

### 1.2 Five senses of "finite" in quantum mechanics (Paper 006 §1, reconstructed)

| Label | Sense | Object | Cardinality of pure/state set |
|---|---|---|---|
| F1 | finite dimension | $\dim\mathcal{H} = d < \infty$ | $\mathbb{C}P^{d-1}$: uncountable, continuous |
| F2 | exact algebraic carrier | $\mathcal{H} = K^d$, $K = \mathbb{Q}(\zeta_n)$ | countably infinite |
| F3 | finite discrete state set | $\mathcal{S}$ with $\lvert\mathcal{S}\rvert<\infty$ (e.g. stabilizer states) | finite |
| F4 | finite scalar field | $\mathbb{F}_q^d$ (not a Hilbert space; no positivity) | finite |
| F5 | finite observation/report alphabet | $Y=\{1,\dots,M\}$, $C_{\mathrm{rep}}$ | finite |

The central point of this round: **F1 alone yields no finiteness of states.** Finiteness of trajectories in Theorem Q.1 comes from F5 (and, in §6, from F3). F2 and F4 are recorded for later rounds and are not used in the proofs here.

### 1.3 The Quantum Relational Universe

**Definition 1 (Quantum Relational Universe).**
$$\mathcal{U}_Q = (\mathcal{H},\ \mathcal{S}_Q,\ \Pi,\ C_{\mathrm{rep}},\ \operatorname{report})$$
with

- $\mathcal{H} \cong \mathbb{C}^d$, $d\ge 2$ (or $K^d$ with $K=\mathbb{Q}(\zeta_n)$ embedded in $\mathbb{C}$);
- $\mathcal{S}_Q = \{\rho \in \mathcal{L}(\mathcal{H}) : \rho=\rho^\dagger,\ \rho\ge 0,\ \operatorname{Tr}\rho = 1\}$, a compact convex set;
- $\Pi = \{E_1,\dots,E_M\}$, $E_m \ge 0$, $\sum_{m=1}^M E_m = I$; $Y = \{1,\dots,M\}$;
- the **probability profile** $\pi : \mathcal{S}_Q \to \Delta^{M-1}$, $\pi(\rho)_m = \operatorname{Tr}(\rho E_m)$, which is affine and continuous; its image $\pi(\mathcal{S}_Q)$ is a compact convex subset of the simplex and is in general **uncountable**;
- a **quantizer** $\kappa : \Delta^{M-1} \to A$ into a finite alphabet $A$, and an injective encoding $\iota : A \hookrightarrow C_{\mathrm{rep}}$;
- $\operatorname{report} = \tau = \iota\circ\kappa\circ\pi : \mathcal{S}_Q \to C_{\mathrm{rep}}$.

**Declared assumption (A-REP).** $C_{\mathrm{rep}}$ is finite and $\operatorname{report}$ is a deterministic function of $\pi(\rho)$. Three admissible quantizers, with their report capacities $N := \lvert\operatorname{report}(\mathcal{S}_Q)\rvert$:

| Quantizer | Definition | Bound on $N$ |
|---|---|---|
| modal (single-click) | $\kappa_{\max}(p) = \min\{\arg\max_m p_m\}$ | $N \le M$ |
| $k$-shot sequence | $\kappa_{\mathrm{seq}}(p) \in Y^k$ (typical/rounded sequence) | $N \le M^k$ |
| $k$-level histogram | $\kappa_k(p) = (\lfloor k p_m\rfloor)_{m}$, with $\sum_m\lfloor kp_m\rfloor \le k$ | $N \le \binom{k+M}{M} \le (k+1)^M$ |

The prompt's "$N \le M$" is the modal-quantizer case. It is **not** a consequence of $\lvert\Pi\rvert = M$ alone: the raw profile map $\pi$ has an uncountable image, so some $\kappa$ with finite range must be declared. This is recorded as a hygiene point, not a defect of the theorem.

---

## 2. Accessible Information and the Holevo Horizon

Let an encoder prepare $\rho_x$ with prior $p_x$ ($x\in X$) and let a decoder apply $\Pi$ then $\kappa$. Three independent ceilings apply to the mutual information $I(X;\operatorname{report})$:

1. **Holevo.** $I(X;Y) \le \chi := S\!\left(\sum_x p_x\rho_x\right) - \sum_x p_x S(\rho_x) \le \log_2 d$. (Standard result; stated here, not re-derived — routed $\mathsf{evidence\_only}$.)
2. **Alphabet.** $I(X;Y) \le H(Y) \le \log_2 M$.
3. **Report carrier.** $I(X;\operatorname{report}) \le H(\operatorname{report}) \le \log_2 N$, and by the data-processing inequality $I(X;\operatorname{report}) \le I(X;Y)$.

**Proposition 2.1 (Horizon ceiling).** Under (A-REP),
$$I(X;\operatorname{report}) \;\le\; \min\{\log_2 d,\ \log_2 M,\ \log_2 N\}.$$
*Proof.* Each term is one of the three ceilings; the minimum of upper bounds is an upper bound. $\square$

Interpretation: $\log_2 N$ is the number of bits per report that can be intersubjectively distinguished. Any "improvement" that is not reflected in $\operatorname{report}$ carries zero bits across the boundary (R2).

---

## 3. Lemma Q.1 (POVM Report Carrier Finitude)

**Lemma Q.1.** Let $\mathcal{U}_Q$ satisfy (A-REP). Then although $\lvert\mathcal{S}_Q\rvert = 2^{\aleph_0}$, the effective report space $\operatorname{report}(\mathcal{S}_Q) \subseteq C_{\mathrm{rep}}$ is finite, with $\lvert\operatorname{report}(\mathcal{S}_Q)\rvert \le \lvert A\rvert$; in particular $\le M$ for the modal quantizer and $\le M^k$ for $k$-shot sequence reports.

*Proof.*
(i) $\operatorname{report} = \iota\circ\kappa\circ\pi$, so $\operatorname{report}(\mathcal{S}_Q) = \iota(\kappa(\pi(\mathcal{S}_Q))) \subseteq \iota(A)$.
(ii) $\iota$ is injective and $A$ is finite, so $\lvert\iota(A)\rvert = \lvert A\rvert < \infty$.
(iii) For the modal quantizer, $A = Y$, $\lvert A\rvert = M$. For $k$-shot sequences, $A \subseteq Y^k$, $\lvert A\rvert \le M^k$.
(iv) The cardinality of $\mathcal{S}_Q$ plays no role: an image of a set under a function has cardinality at most that of the codomain. $\square$

**Remark (what the lemma does not say).** It does not say two distinct $\rho\ne\sigma$ are "the same"; it says they are *report-indistinguishable*. By R1 they may still differ ($\delta(\rho,\sigma)\ne 0_R$), but that difference is invisible across the boundary alphabet. This is precisely the gap Theorem Q.1 exploits.

---

## 4. Strict Report-Grounded Dominance

**Definition 4.1 (Strict dominance).** $(\succ) \subseteq \mathcal{S}_Q\times\mathcal{S}_Q$ with
- (IRR) $\forall\rho:\ \neg(\rho\succ\rho)$;
- (TRANS) $\forall\rho,\sigma,\tau:\ \rho\succ\sigma \wedge \sigma\succ\tau \Rightarrow \rho\succ\tau$.

**Definition 4.2 (Report-grounded).** $(\succ)$ is report-grounded iff
$$\forall\rho_1,\rho_2,\sigma_1,\sigma_2:\ \operatorname{report}(\rho_1)=\operatorname{report}(\rho_2)\ \wedge\ \operatorname{report}(\sigma_1)=\operatorname{report}(\sigma_2)\ \wedge\ \rho_1\succ\sigma_1\ \Rightarrow\ \rho_2\succ\sigma_2 .$$

**Lemma Q.2 (Descent to the report carrier).** If $(\succ)$ is report-grounded, then
(a) $\operatorname{report}(\rho)=\operatorname{report}(\sigma) \Rightarrow \neg(\rho\succ\sigma)$;
(b) $\rho\succ\sigma \iff \operatorname{report}(\rho)\ \succ_{\mathrm{rep}}\ \operatorname{report}(\sigma)$ for a well-defined strict partial order $\succ_{\mathrm{rep}}$ on $\operatorname{report}(\mathcal{S}_Q)$.

*Proof.* (a) Suppose $\operatorname{report}(\rho)=\operatorname{report}(\sigma)$ and $\rho\succ\sigma$. Apply Definition 4.2 with $\rho_1=\rho$, $\rho_2=\sigma$, $\sigma_1=\sigma_2=\sigma$: the hypotheses hold, so $\sigma\succ\sigma$, contradicting (IRR).
(b) Define $a\succ_{\mathrm{rep}} b$ iff $\exists\rho,\sigma$ with $\operatorname{report}(\rho)=a$, $\operatorname{report}(\sigma)=b$, $\rho\succ\sigma$. Definition 4.2 makes this independent of the chosen representatives. Irreflexivity of $\succ_{\mathrm{rep}}$ is (a); transitivity is inherited from (TRANS) by picking representatives. $\square$

So a report-grounded strict dominance is nothing more than a strict partial order on a finite set of size $N$, pulled back along $\operatorname{report}$.

---

## 5. Theorem Q.1 (Quantum Bounded RSI Horizon — Report Collision)

### 5.1 Setup

A **recursive self-modifying quantum trajectory** is a sequence $(\rho_k)_{k\ge 1}$ in $\mathcal{S}_Q$ with
$$\rho_{k+1} = \mathcal{E}_k(\rho_k),\qquad \mathcal{E}_k \text{ CPTP on } \mathcal{L}(\mathcal{H})\ (\text{internal, per R2}),$$
together with the **strict improvement claim** $\rho_{k+1}\succ\rho_k$ for all $k$, where $(\succ)$ is report-grounded. Set $N := \lvert\operatorname{report}(\mathcal{S}_Q)\rvert \le \lvert C_{\mathrm{rep}}\rvert$.

### 5.2 Statement

**Theorem Q.1.** Under (A-REP) and Definitions 4.1–4.2, no trajectory satisfies $\rho_{k+1}\succ\rho_k$ for all $k\ge 1$. More precisely, among $\rho_1,\dots,\rho_{N+1}$ there exist $i<j\le N+1$ with $\operatorname{report}(\rho_i)=\operatorname{report}(\rho_j)$, and the improvement claim fails at or before step $k^* = j \le N+1 \le \lvert C_{\mathrm{rep}}\rvert+1$ (and $\le M+1$ for the modal quantizer). The terminal is `REPORT_COLLISION`.

### 5.3 Proof

1. **Pigeonhole.** The $N+1$ states $\rho_1,\dots,\rho_{N+1}$ map under $\operatorname{report}$ into a set of $N$ values. Hence $\exists\, i<j\le N+1$ with $\operatorname{report}(\rho_i)=\operatorname{report}(\rho_j)$.
2. **Chain.** Assume toward contradiction that $\rho_{k+1}\succ\rho_k$ for all $k<j$. Since $j-i\ge 1$, repeated use of (TRANS) on $\rho_j\succ\rho_{j-1}\succ\cdots\succ\rho_i$ gives $\rho_j\succ\rho_i$.
3. **Descent.** By Lemma Q.2(a), $\operatorname{report}(\rho_j)=\operatorname{report}(\rho_i)$ together with $\rho_j\succ\rho_i$ yields $\rho_i\succ\rho_i$ (equivalently, instantiate Definition 4.2 with $\rho_1=\rho_j,\rho_2=\rho_i,\sigma_1=\sigma_2=\rho_i$).
4. **Contradiction** with (IRR). Hence the strict-improvement claim is false for some step $k<j\le N+1$.
5. **Termination.** The first index $k^*$ at which $\operatorname{report}(\rho_{k^*})\in\{\operatorname{report}(\rho_1),\dots,\operatorname{report}(\rho_{k^*-1})\}$ satisfies $k^*\le N+1$, and at that index the transition $\rho_{k^*-1}\to\rho_{k^*}$ cannot be a report-grounded strict improvement. The process routes to `REPORT_COLLISION`. $\square$

**Remarks.**
- The CPTP property of $\mathcal{E}_k$ is not used in the proof; it fixes the class of *internal* transitions (R2) but the bound is purely combinatorial on the report carrier. A stronger structural statement using CPTP (e.g. contractivity of trace distance) is a Round 2 target, not claimed here.
- The bound is on the *claim*, not on the *dynamics*: the sequence $(\rho_k)$ can continue indefinitely; what cannot continue is a report-grounded strict-improvement certificate.
- Tightness: the witness in §7 attains $k^* = N+1$ exactly.

### 5.4 Goodhart proxy decoupling

Suppose the agent maintains an internal scalar $\mu:\mathcal{S}_Q\to\mathbb{R}$ (an evaluation of type R2(a), e.g. $\mu(\rho)=\operatorname{Tr}(\rho W)$ for some $W$, or an iteration counter) and certifies progress by $\mu(\rho_{k+1})\ge\mu(\rho_k)+1$, so $\mu(\rho_k)\ge\mu(\rho_1)+k-1$.

**Proposition 5.1 (Decoupling).** For $k\ge N+1$ (hence for $k\ge M+1$ under the modal quantizer), there is no function $f:C_{\mathrm{rep}}\to\mathbb{R}$ with $\mu(\rho_t)=f(\operatorname{report}(\rho_t))$ for all $t\le k$.

*Proof.* $\{\mu(\rho_t)\}_{t\le k}$ contains $k\ge N+1$ pairwise distinct values (strictly increasing), while $\{\operatorname{report}(\rho_t)\}_{t\le k}$ has at most $N$ values. A function of the report takes at most $N$ values on these indices. $\square$

Consequence under R2: once $k\ge N+1$, the proxy $\mu$ is attesting to differences that have no image in $C_{\mathrm{rep}}$. Such attestations route to $\mathsf{evidence\_only}$ (internal) and, if submitted as an intersubjective improvement claim, to $\mathsf{not\_admitted}$. This is the formal shape of Goodhart decoupling in this model: the proxy keeps increasing, the boundary alphabet is saturated.

---

## 6. Stabilizer Subsector

### 6.1 Orbit finitude and the count (correction to the prompt)

Let $\mathcal{S}_{\mathrm{Stab},n}\subset\mathcal{S}_Q$ be the $n$-qubit stabilizer states (pure states stabilized by a maximal abelian subgroup of the Pauli group not containing $-I$). The Clifford group $\mathcal{C}_n$ maps $\mathcal{S}_{\mathrm{Stab},n}$ to itself, and Pauli measurements followed by any Clifford correction also keep the state in $\mathcal{S}_{\mathrm{Stab},n}$.

**Gottesman–Knill (as used here).** For a trajectory whose transitions are Clifford unitaries, Pauli measurements, and Pauli-frame updates, every $\rho_k$ lies in the finite set $\mathcal{S}_{\mathrm{Stab},n}$, and the tableau representation is updated in $\mathrm{poly}(n)$ time per step.

**Cardinality.** The standard count (Aaronson–Gottesman) is
$$\lvert\mathcal{S}_{\mathrm{Stab},n}\rvert \;=\; 2^n\prod_{j=1}^{n}\left(2^{j}+1\right).$$
Check: $n=1$: $2\cdot 3 = 6$ (the six single-qubit stabilizer states $\lvert 0\rangle,\lvert 1\rangle,\lvert\pm\rangle,\lvert\pm i\rangle$). $n=2$: $4\cdot 3\cdot 5 = 60$.

The prompt's expression $2^n\prod_{j=1}^n(2^{2j-1}+1)$ agrees at $n=1$ but gives $4\cdot 3\cdot 9 = 108$ at $n=2$, which does not match the known count of 60. The factor $\prod_j(2^{2j}-1)$ appears in $\lvert\mathrm{Sp}(2n,\mathbb{F}_2)\rvert = 2^{n^2}\prod_{j=1}^n(2^{2j}-1)$ (Clifford group modulo Paulis and phases); the prompt's formula appears to conflate these. The prompt formula is routed $\mathsf{rejected}$; the corrected formula is used below.

### 6.2 Corollary Q.1.1

**Corollary Q.1.1.** Let $(\rho_k)$ be a trajectory in $\mathcal{S}_{\mathrm{Stab},n}$ under stabilizer-preserving internal transitions, with a strict dominance $(\succ)$ (any strict partial order; report-grounding not required). Then a state repetition $\rho_i=\rho_j$, $i<j$, occurs with $j\le\lvert\mathcal{S}_{\mathrm{Stab},n}\rvert+1$, and the strict-improvement claim fails by $k^*\le\lvert\mathcal{S}_{\mathrm{Stab},n}\rvert+1 = 2^n\prod_{j=1}^n(2^j+1)+1$.

*Proof.* Apply Theorem Q.1 with $\operatorname{report}=\mathrm{id}$ on the finite set $\mathcal{S}_{\mathrm{Stab},n}$ (so $N=\lvert\mathcal{S}_{\mathrm{Stab},n}\rvert$). Pigeonhole gives $\rho_i=\rho_j$; (TRANS) gives $\rho_j\succ\rho_i$, i.e. $\rho_i\succ\rho_i$, contradicting (IRR). Report-grounding is not needed because the collision is in the state itself. If additionally a coarser report with $N'<\lvert\mathcal{S}_{\mathrm{Stab},n}\rvert$ is used and $(\succ)$ is report-grounded, the bound improves to $N'+1$. $\square$

Explicit integers: $n=1$: $k^*\le 7$; $n=2$: $k^*\le 61$; $n=3$: $\lvert\mathcal{S}_{\mathrm{Stab},3}\rvert = 8\cdot3\cdot5\cdot9=1080$, $k^*\le 1081$.

### 6.3 Eastin–Knill (correction to the prompt's framing)

**Eastin–Knill theorem (statement).** For any quantum error-detecting code (detecting all single-site errors, on a nontrivial tensor-product partition), the group of logical operations implementable by transversal unitaries is finite; hence it is not universal.

Two points of hygiene:

1. The theorem does **not** state that transversal gates are Clifford. Counterexample: the 15-qubit Reed–Muller code has a transversal non-Clifford $T$ gate (and correspondingly lacks a transversal Hadamard). What the theorem forbids is a *dense* transversal gate set.
2. The relevant consequence for this campaign is therefore the **finite-orbit** statement, not a "Clifford confinement" statement: an agent whose only internal transitions are transversal logical gates of a fixed code acts through a finite group $G_{\mathrm{tr}}$, so the orbit of any logical state under $G_{\mathrm{tr}}$ is finite, with size $\le\lvert G_{\mathrm{tr}}\rvert$, and Corollary Q.1.1's argument applies with $N=\lvert G_{\mathrm{tr}}\cdot\rho_1\rvert$.

Escaping a finite orbit (whether the stabilizer orbit under Cliffords, or the transversal orbit under $G_{\mathrm{tr}}$) requires a transition outside that group: magic-state injection, code switching, gauge fixing, or a non-transversal physical gate. In the monograph's vocabulary these are **external lift** operations: they consume a resource (prepared magic states, additional code blocks) that is not an endomorphism of the current finite orbit. The counting of that budget is deferred to Round 2 as an unresolved obligation; this round only records that the transition is not available internally.

---

## 7. Countermodel and Collision Witness

### 7.1 Single-qubit, $M=2$, modal report (attains $k^*=M+1=3$)

- $\mathcal{H}=\mathbb{C}^2$, $\Pi=\{E_1=\lvert0\rangle\langle0\rvert,\ E_2=\lvert1\rangle\langle1\rvert\}$.
- $\kappa_{\max}(p)=\min\arg\max_m p_m$, $C_{\mathrm{rep}}=\{1,2\}$, $N=2$.
- $\succ_{\mathrm{rep}}$: $2\succ_{\mathrm{rep}}1$ only. Pull back to $\mathcal{S}_Q$ via Lemma Q.2(b): $\rho\succ\sigma$ iff $\operatorname{report}(\rho)=2$, $\operatorname{report}(\sigma)=1$. This is irreflexive, transitive, and report-grounded by construction.
- Trajectory: $\rho_1=\lvert0\rangle\langle0\rvert$; $\mathcal{E}_1(\cdot)=X(\cdot)X$ gives $\rho_2=\lvert1\rangle\langle1\rvert$; $\mathcal{E}_2(\cdot)=H(\cdot)H$ gives $\rho_3=\lvert-\rangle\langle-\rvert$.

| $k$ | $\rho_k$ | $\pi(\rho_k)$ | $\operatorname{report}$ | $\rho_k\succ\rho_{k-1}$? |
|---|---|---|---|---|
| 1 | $\lvert0\rangle\langle0\rvert$ | $(1,0)$ | 1 | — |
| 2 | $\lvert1\rangle\langle1\rvert$ | $(0,1)$ | 2 | yes |
| 3 | $\lvert-\rangle\langle-\rvert$ | $(\tfrac12,\tfrac12)$ | 1 (tie-break) | **no**: report 1 $\not\succ_{\mathrm{rep}}$ 2 |

Collision: $\operatorname{report}(\rho_3)=\operatorname{report}(\rho_1)$, $i=1$, $j=3=N+1$. Had $\rho_3\succ\rho_2$ held, transitivity would give $\rho_3\succ\rho_1$, and Lemma Q.2(a) would force $\rho_1\succ\rho_1$. Any choice of $\mathcal{E}_2$ gives a report in $\{1,2\}$, so no third step can be a strict improvement: $k^*=3$ exactly. `REPORT_COLLISION` at $k^*=3$.

Goodhart layer: let $\mu(\rho_k)=k$. Then $\mu(\rho_3)=3>\mu(\rho_2)=2$ while the report has returned to its $k=1$ value — Proposition 5.1 with $N=2$, $k=3$.

### 7.2 Single-qubit trine POVM, $M=3$ (attains $k^*=4$)

$E_m=\tfrac23\lvert\psi_m\rangle\langle\psi_m\rvert$, $\lvert\psi_m\rangle=\cos\theta_m\lvert0\rangle+\sin\theta_m\lvert1\rangle$, $\theta_m\in\{0,\tfrac{2\pi}{3},\tfrac{4\pi}{3}\}$; $\sum_m E_m=I$. Modal report, $N=3$, $\succ_{\mathrm{rep}}$ the chain $3\succ2\succ1$. Trajectory $\rho_k=\lvert\psi_k\rangle\langle\psi_k\rvert$ for $k=1,2,3$ (reports $1,2,3$; each a rotation $R_y(2\pi/3)$, a unitary CPTP map), then any $\rho_4$ has report in $\{1,2,3\}$, none of which is $\succ_{\mathrm{rep}}3$. Collision and failure at $k^*=4=M+1$.

### 7.3 Two-qubit Bell panel, $M=4$

$\Pi=\{\lvert\Phi^\pm\rangle\langle\Phi^\pm\rvert,\lvert\Psi^\pm\rangle\langle\Psi^\pm\rvert\}$, modal report, $N=4$. The Pauli frame $\rho_k=(I\otimes P_k)\lvert\Phi^+\rangle\langle\Phi^+\rvert(I\otimes P_k)$, $P_k\in\{I,X,Z,XZ\}$, visits all four reports in four steps; step 5 collides. $k^*\le 5$; attained with a 4-chain order on reports. All $\rho_k$ are 2-qubit stabilizer states, so Corollary Q.1.1 also applies with the looser bound $61$, and the report-grounded bound $5$ dominates.

---

## 8. Epistemic Routing (PG3)

| Item | Terminal | Grounds |
|---|---|---|
| Definition 1, (A-REP) | $\mathsf{authorized}$ (as specification) | declared, internally consistent |
| "$N\le M$" as a consequence of $\lvert\Pi\rvert=M$ alone | $\mathsf{not\_admitted}$ | $\pi$ has uncountable image; needs a quantizer |
| Prop. 2.1 (Holevo ceiling) | $\mathsf{evidence\_only}$ | relies on Holevo bound, stated not re-derived here |
| Lemma Q.1 | $\mathsf{authorized}$ | proved under (A-REP) |
| Lemma Q.2 | $\mathsf{authorized}$ | proved |
| Theorem Q.1 | $\mathsf{authorized}$ | proved; bound attained by §7 witnesses |
| Prop. 5.1 (Goodhart decoupling) | $\mathsf{authorized}$ | proved (counting) |
| Corollary Q.1.1 | $\mathsf{authorized}$ with corrected count | proved; count taken from standard literature |
| Prompt formula $2^n\prod(2^{2j-1}+1)$ | $\mathsf{rejected}$ | fails at $n=2$ (108 vs 60) |
| Prompt framing "Eastin–Knill ⇒ transversal gates are Clifford" | $\mathsf{rejected}$ | Reed–Muller counterexample; replaced by finite-group statement |
| External-lift budget accounting for orbit escape | $\mathsf{unresolved}$ | deferred to Round 2 |
| CPTP-structural strengthening of Theorem Q.1 | $\mathsf{unresolved}$ | not attempted |
| Machine-checked (Lean) versions | $\mathsf{unresolved}$ | no tool channel this round |

---

## 9. Claim Hygiene Summary

- **Supported:** Under a declared finite quantizer, a report-grounded strict dominance on $\mathcal{S}_Q$ descends to a strict partial order on a finite report set, and any strict-improvement chain fails by step $N+1$ (pigeonhole + transitivity + irreflexivity). Witnesses attain the bound. In the stabilizer subsector with Clifford/Pauli transitions the state set itself is finite with the corrected count.
- **Not supported:** that finite $d$ or finite $M$ *by themselves* bound trajectory length; that CPTP structure adds anything to the bound (not used); that transversality confines to Clifford operations; the prompt's stabilizer count; any empirical or machine-checked status.
- **Narrowest defensible claim:** In this model, with $\operatorname{report}$ a deterministic finite-valued function of the POVM profile and $(\succ)$ report-grounded, no sequence of internal transitions carries a strict-improvement certificate past index $\lvert\operatorname{report}(\mathcal{S}_Q)\rvert+1$.
- **Next check:** encode Definitions 4.1–4.2 and Theorem Q.1 as a finite-type pigeonhole argument in Lean (`Fintype.exists_ne_map_eq_of_card_lt` over `Fin (N+1) → C_rep`), and run the §7.1 witness as a unit test; separately, re-verify the stabilizer count for $n=2$ by enumeration (expect 60).

```json
{
  "campaign_id": "FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION",
  "round": 1,
  "status": "VERIFIED_LOCAL_RESULT",
  "status_meaning": "hand-derived in this response; no Lean/Cargo/solver executed; not machine-checked",
  "derived_theorems": [
    "Prop_2_1_HorizonCeiling",
    "Lemma_Q_1_POVM_ReportCarrierFinitude",
    "Lemma_Q_2_DescentToReportCarrier",
    "Theorem_Q_1_QuantumBoundedRSIHorizon_ReportCollision",
    "Prop_5_1_GoodhartProxyDecoupling",
    "Corollary_Q_1_1_StabilizerOrbitFinitude"
  ],
  "bounds_established": {
    "k_star_modal_report": "N+1 <= M+1",
    "k_star_k_shot_sequence_report": "N+1 <= M^k + 1",
    "k_star_k_level_histogram_report": "N+1 <= C(k+M, M) + 1",
    "goodhart_decoupling_index": "k >= N+1",
    "witness_qubit_M2": 3,
    "witness_qubit_trine_M3": 4,
    "witness_2qubit_bell_M4": 5,
    "stabilizer_n1_states": 6,
    "stabilizer_n1_k_star": 7,
    "stabilizer_n2_states": 60,
    "stabilizer_n2_k_star": 61,
    "stabilizer_n3_states": 1080,
    "stabilizer_n3_k_star": 1081,
    "stabilizer_count_formula_used": "2^n * prod_{j=1..n} (2^j + 1)",
    "accessible_info_bits_per_report": "min(log2 d, log2 M, log2 N)"
  },
  "corrections_to_prompt": [
    "Stabilizer count 2^n*prod(2^{2j-1}+1) rejected (gives 108 at n=2; standard count is 60).",
    "Eastin-Knill restated as finite transversal logical group, not Clifford confinement (15-qubit Reed-Muller transversal T is a counterexample).",
    "|C_rep| <= M requires a declared quantizer; the raw POVM profile map has uncountable image."
  ],
  "unresolved_obligations": [
    "Round 2: formalize the external lift budget for escaping finite stabilizer/transversal orbits (magic-state injection, code switching) and bound trajectory length as a function of that budget.",
    "Round 2: investigate whether CPTP contractivity (trace-distance monotonicity) yields a strengthening of Theorem Q.1 independent of report quantization.",
    "Round 2: extend Theorem Q.1 from deterministic quantizers to stochastic single-shot reports (collision in distribution vs. in realization).",
    "Round 2: treat the F2 (cyclotomic carrier) and F4 (finite field) senses, which were listed but not used in this round.",
    "Tooling: Lean encoding of Lemma Q.2 and Theorem Q.1 via Fintype pigeon