# Output: round_4_synthesis_and_executable_verification.md

- **Timestamp:** 2026-10-17T00:56:30.110339
- **Model:** claude-fable-5-1
- **Round:** 4
- **Duration:** 272.8s
- **Tokens:** In=52737, Out=24879
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_4_synthesis_and_executable_verification.md`
- **Continued From:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\outputs\20261017_004952_round_3_round_3_contextuality_simplicial_coboundary_defect_claude-fable-5-1.md`

---

## Thinking Trace

```text

```

---

## Response Content

# Round 4 Record — Composite Synthesis, Dual-Language Harness, Workpad Schemas, Lean Blueprints

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 4/4**
**Execution note:** No Lean, Cargo, Python, or solver ran. The code in §2 and §4 is a specification written to be executable; it has not been executed, compiled, or type-checked here. Rounds 1–3 are referenced, not re-derived, and are not treated as external receipts.

**Corrections to the prompt applied in this round (summarized; details in §1.1).**
1. The displayed bound $\min(M+1,\,B_0+1,\,|Stab_n|+1)$ is not a single theorem: its three terms are derived under three different hypothesis sets. The master theorem is stated as a case-structured bound whose terms are active only when their hypotheses hold; the $\min$ is valid on the intersection of hypotheses.
2. The four modes are not mutually disjoint (a step can be both a report collision and a gluing refusal). A priority order is declared to make the assigned terminal a function.
3. `BAKER_TRANSCENDENTAL_DECOUPLING` is not a termination index; it is a routing verdict on a *claim type* (exact carrier value of $S$), active at every step. It is placed in the theorem as a routing clause, not a step bound. The harness name `DECOUPLING_DETECTED` from the prompt's §2 is adopted as the terminal label for both the Baker routing and the Round 1/2 Goodhart decoupling, with a `reason` field distinguishing them.
4. The Lean target name `quantum_rsi_impossible` uses forbidden vocabulary and overstates the content (the dynamics continue; the certificate is bounded). It is renamed `quantum_rsi_bounded_horizon`.
5. The stabilizer count is $2^n\prod_{j=1}^n(2^j+1)$ (Round 1 correction stands).

---

## 1. Theorem Q.Master (Quantum-Relational Bounded RSI Horizon)

### 1.1 Hypothesis sets (declared, carried from Rounds 1–3)

| Tag | Content | Origin |
|---|---|---|
| (H0) | $\mathcal{U}_Q=(\mathcal{H},\mathcal{S}_Q,\Pi,C_{\mathrm{rep}},\operatorname{report})$, $\dim\mathcal{H}=d<\infty$; $\Pi$ a POVM with $M$ outcomes | R1 Def. 1 |
| (A-REP) | $\operatorname{report}=\iota\circ\kappa\circ\pi$ with a declared finite quantizer; $N:=|\operatorname{report}(\mathcal{S}_Q)|<\infty$; $N\le M$ for the modal quantizer | R1 §1.3 |
| (H-DOM) | $(\succ)$ strict (irreflexive, transitive) and report-grounded | R1 Defs. 4.1–4.2 |
| (H-TRAJ) | $\rho_{k+1}=\mathcal{E}_k(\rho_k)$, $\mathcal{E}_k$ CPTP and internal (R2) | R1 §5.1 |
| (A-LIFT) | integer ancilla budget $B_k$; budget-free internal steps are unital; purification steps ($S$ strictly drops) cost $\ge1$ and no re-preparation | R2 §1.4 |
| (H-STAB) | $\mathcal{H}=(\mathbb{C}^2)^{\otimes n}$, all $\rho_k$ stabilizer states, all $\mathcal{E}_k$ stabilizer-preserving | R1 §6 |
| (H-COMM) | nodes $a\in V$ with carriers $N_a$; coverage complex $E$; latencies $\tau_{ab}(k)$; promotion requires $\Phi_1(\delta_k)=0$ on $E$ | R3 §2.1 |
| (H-CTX) | the promotion rule requires a glued global section of an empirical model $e$ on the measurement nerve $\mathcal{X}$ | R3 §1.3 |
| (H-ALG) | $\rho_k$ has algebraic spectrum, $\operatorname{rank}\rho_k\ge2$, and the improvement claim is "$S(\rho_k)=s_k$ exactly, $s_k\in K$" | R2 §2.2 |
| (H-FV3) | promotion requires Signal 2 from $v$ with $\mathsf{IsIndependentVerifier}(g,v)$ as declared | R3 §3.1 |

**Terminal priority (declared).** When several obstructions hold at the same step, the assigned terminal is the first applicable in the order
`OVERLAP_GLUING_REFUSAL` ≺ `LIFT_BUDGET_EXHAUSTION` ≺ `REPORT_COLLISION`, with `DECOUPLING_DETECTED` and `TWO_SIGNAL_COLLAPSE` recorded as routing annotations on the claim rather than as trajectory terminals. Any other total order would serve; this one is fixed so that the harness's `terminal` field is a function of the trajectory.

### 1.2 Statement

**Theorem Q.Master.** Assume (H0), (A-REP), (H-DOM), (H-TRAJ). Let $(\rho_k)_{k\ge1}$ carry at every step the claim $\rho_{k+1}\succ\rho_k$, and let $k^*$ be the first index at which that claim fails to be admitted. Then:

(i) **Report horizon (always active).** $k^*\le N+1$, and $N+1\le M+1$ under the modal quantizer. The obstruction at $k^*$ is a report collision $\operatorname{report}(\rho_i)=\operatorname{report}(\rho_{k^*})$, $i<k^*$, which under (H-DOM) forces $\rho_i\succ\rho_i$. *(Round 1, Thm Q.1.)*

(ii) **Stabilizer horizon (active under (H-STAB)).** Even with $\operatorname{report}=\mathrm{id}$ on the stabilizer set, $k^*\le 2^n\prod_{j=1}^n(2^j+1)+1$. *(Round 1, Cor. Q.1.1.)*

(iii) **Lift horizon (active under (A-LIFT) when the claim is an entropy decrease).** At most $B_0$ claims are admitted; $k^*\le B_0+1$. Total entropy removed $\le B_0$ bits. *(Round 2, Thm Q.2.)*

(iv) **Gluing horizon (active under (H-COMM) or (H-CTX)).** Under (H-COMM), $k^*\le\min\{T_{\mathrm{glue}},\ \prod_aN_a+1\}$, with $T_{\mathrm{glue}}\le(\text{first in-window report change})+1$. Under (H-CTX) with $e$ strongly contextual (e.g. Cabello 18-ray, $\Phi_{\mathrm{glue}}=1$) or contextual (e.g. rational CHSH, $\mathrm{CF}\ge47/125$), the promotion is refused at every step at which gluing is demanded, so $k^*=$ the first such step. *(Round 3, Thm Q.3, Thm Q.3.2.)*

(v) **Baker routing (active under (H-ALG)).** No claim of the form "$S(\rho_k)=s_k\in K$" is admissible at any step: $S_e(\rho_k)$ is transcendental (conditional on Baker's theorem). Admissible substitutes are $K$-valued power sums $P_m$ or certified rational enclosures; a $2^{-\kappa}$-rounded proxy has at most $\lceil2^\kappa\log_2d\rceil+1$ values and re-enters (i) with that $N$. *(Round 2, Thm Q.2.1.)*

(vi) **Two-signal routing (active under (H-FV3)).** A step verified only by self-measurement is routed $\mathsf{evidence\_only}$ and does not count as admitted; the self-measurement is itself a unital step for (iii). *(Round 3, Lemma Q.4.)*

(vii) **Composite bound.** On the intersection of the active hypothesis sets,
$$k^*\ \le\ \min\Big\{\,N+1,\ \ 2^n\!\prod_{j=1}^n(2^j+1)+1\ [\text{H-STAB}],\ \ B_0+1\ [\text{A-LIFT, entropy claims}],\ \ T_{\mathrm{glue}}\ [\text{H-COMM}],\ \ \textstyle\prod_aN_a+1\ [\text{H-COMM}]\Big\},$$
and the terminal is assigned by the declared priority. The prompt's $\min(M+1,B_0+1,|Stab_n|+1)$ is the special case: modal quantizer, (H-STAB), (A-LIFT) with entropy-decrease claims, single node.

(viii) **Bounded no-go.** In particular no trajectory carries an admitted strict report-grounded improvement claim at every step $k\in\mathbb{N}$. Nothing is asserted about the continuation of the dynamics $(\rho_k)$ past $k^*$.

### 1.3 Integrated proof

**Step A (common core: descent to a finite carrier).** By (A-REP) the map $\operatorname{report}$ has finite image of size $N$. By (H-DOM) and Round 1 Lemma Q.2, $(\succ)$ is the pullback of a strict partial order $\succ_{\mathrm{rep}}$ on that image. A strict partial order on a finite set of size $N$ has no chain of length $N+1$; concretely, among $\rho_1,\dots,\rho_{N+1}$ two share a report, transitivity gives $\rho_j\succ\rho_i$, and Lemma Q.2(a) turns this into $\rho_i\succ\rho_i$, contradicting irreflexivity. This is (i). Under (H-STAB) the same argument runs on the finite state set itself, giving (ii); the state count is the Aaronson–Gottesman count, hand-verified at $n=1,2$ in Round 1.

**Step B (resource core: an integer measure that strictly descends).** Under (A-LIFT), Round 2 Lemma Q.3 shows that budget-free (unital) steps never decrease $S$, so every admitted entropy-decrease claim is a purification step and decrements $B_k\in\mathbb{Z}_{\ge0}$ by at least 1. A strictly decreasing sequence in $\mathbb{Z}_{\ge0}$ starting at $B_0$ has at most $B_0$ steps; the $(B_0+1)$-th attempt finds $B=0$ and only unital maps available. Lemma 1.3 (Araki–Lieb) telescopes to the $B_0$-bit total. This is (iii).

**Step C (gluing core).** Under (H-COMM), Round 3 Lemma 2.1 characterizes $\Phi_1(\delta_k)=0$ as "no report change inside any latency window on the coverage complex"; a node-level strict claim forces a report change by Step A, so with $\tau\ge1$ a refusal occurs by the step after the first change. Independently, Step A on the product carrier $\prod_aC_a$ gives collision by $\prod_aN_a+1$. Under (H-CTX), Round 3 Theorem Q.3 shows that the Cabello model has no global support section ($\Phi_{\mathrm{glue}}=1$, parity class $[\mathbf 1]\ne0$) and the rational CHSH model has no joint distribution ($\mathrm{CF}>0$), so the required glued section does not exist. This is (iv).

**Step D (representability core).** Under (H-ALG), Round 2 Theorem Q.2.1 reduces $S_e(\rho)=-\sum p_i\ln p_i$ to a nonzero linear form in logarithms of algebraic numbers with algebraic coefficients; Baker's theorem (cited) makes it transcendental, so it is not an element of $K$. The admissible substitutes and the re-entry of rounded proxies into Step A are as stated. This is (v).

**Step E (verification core).** Under (H-FV3), Round 3 Lemma Q.4 shows: no CPTP cloning; self-measurement is a pinching (unital, hence a Step-B-neutral or Step-B-adverse move); and a proposer-selected panel yields a verdict with zero mutual information with the improvement predicate. So a self-verified step fails the declared independence predicate and routes $\mathsf{evidence\_only}$. This is (vi).

**Step F (composition).** Each active clause supplies an upper bound on the first non-admitted index; the minimum of upper bounds is an upper bound. The priority order makes the terminal well-defined when several clauses fire at the same index. (vii) follows, and (viii) is the contrapositive of "there is a finite $k^*$". $\square$

### 1.4 What the composite does not say

- It does not bound the number of *distinct states* visited, except under (H-STAB).
- It does not use the CPTP property beyond fixing the internal transition class; a CPTP-contractivity strengthening remains $\mathsf{unresolved}$ (carried from Round 1).
- The external-lift accounting for stabilizer-orbit escape (magic injection, code switching) is not integrated: once an external lift is spent, (H-STAB) is left and only (i) continues to apply with the ambient $N$. The cleanest statement available in this campaign is: *each escape from a finite orbit consumes at least one unit of a budget disjoint from $B_0$, and between escapes clause (ii) applies.* The joint bound with that second budget $B_{\mathrm{ext}}$ is $k^*\le(B_{\mathrm{ext}}+1)\cdot(|Stab_n|+1)$ under the assumption that each escape lands in a stabilizer state again; this is recorded as a *conjectured* bound, routed $\mathsf{unresolved}$, since the landing assumption was not justified.
- Baker's theorem, Araki–Lieb, the Aaronson–Gottesman count, and the quantum Chernoff bound are cited inputs, not re-derived.

---

## 2. Dual-Language Harness Specification

**Status of this section:** written to run; not run. Exact rational arithmetic throughout (`fractions.Fraction` / `num_rational::BigRational`); complex entries are pairs of rationals (Gaussian rationals), which suffices for all witnesses used in Rounds 1–3 (real stabilizer states, Bell panel, Werner states, dephasing/damping channels, rational CHSH tables, diagonal entropy examples). States with irrational entries (e.g. $\cos(2\pi/3)$ trine POVM) are out of scope for the exact backend and must be represented in a declared cyclotomic field; this is flagged, not implemented.

### 2.1 Python module `omega_quantum_physics/fable51.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction as Q
from itertools import product
from typing import Callable, Iterable, Sequence

# ---------- exact Gaussian-rational linear algebra ----------

@dataclass(frozen=True)
class QC:
    """Gaussian rational a + b i."""
    re: Q
    im: Q = Q(0)
    def __add__(s, o): return QC(s.re + o.re, s.im + o.im)
    def __sub__(s, o): return QC(s.re - o.re, s.im - o.im)
    def __mul__(s, o): return QC(s.re*o.re - s.im*o.im, s.re*o.im + s.im*o.re)
    def conj(s): return QC(s.re, -s.im)
    def is_zero(s): return s.re == 0 and s.im == 0

ZERO, ONE = QC(Q(0)), QC(Q(1))
Matrix = list[list[QC]]

def matmul(A: Matrix, B: Matrix) -> Matrix:
    n, m, p = len(A), len(B), len(B[0])
    return [[sum((A[i][k]*B[k][j] for k in range(m)), ZERO) for j in range(p)] for i in range(n)]

def dagger(A: Matrix) -> Matrix:
    return [[A[j][i].conj() for j in range(len(A))] for i in range(len(A[0]))]

def trace(A: Matrix) -> QC:
    return sum((A[i][i] for i in range(len(A))), ZERO)

def identity(n: int) -> Matrix:
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]

def madd(A: Matrix, B: Matrix) -> Matrix:
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def purity_P2(rho: Matrix) -> Q:
    """Tr(rho^2) is real for Hermitian rho; return the rational real part."""
    t = trace(matmul(rho, rho)); assert t.im == 0; return t.re

# ---------- Round 1: universe, report, collision ----------

@dataclass
class QuantumRelationalUniverse:
    dim: int
    povm_effects: list[Matrix]          # E_m >= 0, sum = I (checked for sum only)
    quantizer: Callable[[list[Q]], object] = None   # finite-range map on profiles

    def __post_init__(self):
        S = identity(self.dim)
        S = [[ZERO]*self.dim for _ in range(self.dim)]
        for E in self.povm_effects: S = madd(S, E)
        assert S == identity(self.dim), "POVM effects do not sum to I"
        if self.quantizer is None:
            self.quantizer = lambda p: min(i for i, v in enumerate(p) if v == max(p))  # modal

    def profile(self, rho: Matrix) -> list[Q]:
        out = []
        for E in self.povm_effects:
            t = trace(matmul(rho, E)); assert t.im == 0; out.append(t.re)
        return out

    def report(self, rho: Matrix):
        return self.quantizer(self.profile(rho))

    def report_horizon_bound(self) -> int:
        """N+1 <= M+1 for the modal quantizer (Theorem Q.1)."""
        return len(self.povm_effects) + 1

@dataclass
class ReportGroundedOrder:
    """Strict partial order on report values; pulled back to states (Lemma Q.2)."""
    gt: Callable[[object, object], bool]
    def dominates(self, U, rho, sigma) -> bool:
        return self.gt(U.report(rho), U.report(sigma))

# ---------- Round 2: channels, purity, budget ----------

@dataclass
class KrausChannel:
    kraus: list[Matrix]
    cost: int = 0            # fresh ancilla qubits consumed (declared, A-LIFT)
    def apply(self, rho: Matrix) -> Matrix:
        n = len(rho); out = [[ZERO]*n for _ in range(n)]
        for A in self.kraus: out = madd(out, matmul(matmul(A, rho), dagger(A)))
        return out
    def is_tp(self) -> bool:
        n = len(self.kraus[0]); S = [[ZERO]*n for _ in range(n)]
        for A in self.kraus: S = madd(S, matmul(dagger(A), A))
        return S == identity(n)
    def is_unital(self) -> bool:
        n = len(self.kraus[0]); S = [[ZERO]*n for _ in range(n)]
        for A in self.kraus: S = madd(S, matmul(A, dagger(A)))
        return S == identity(n)

@dataclass
class TrajectoryStep:
    k: int; report: object; P2: Q; budget: int; admitted: bool; note: str

@dataclass
class TrajectoryResult:
    terminal: str                 # see priority order, section 1.1
    k_star: int
    steps: list[TrajectoryStep]
    annotations: list[str] = field(default_factory=list)   # DECOUPLING_DETECTED etc.

def evaluate_cptp_trajectory(U: QuantumRelationalUniverse,
                             order: ReportGroundedOrder,
                             initial_state: Matrix,
                             channel_sequence: Sequence[KrausChannel],
                             budget: int,
                             purification_claim: bool = False,
                             proxy: Callable[[Matrix], Q] | None = None) -> TrajectoryResult:
    """
    Runs rho_{k+1} = E_k(rho_k). Admits step k iff report-grounded strict improvement holds
    and (if purification_claim) budget allows a non-unital step.
    Returns first non-admitted index k* and terminal by declared priority.
    Note: 'purification_claim' uses P2 strict increase as the exact K-valued monotone,
    because S is not carrier-representable (Theorem Q.2.1); see annotations.
    """
    rho, B = initial_state, budget
    seen = {U.report(rho): 1}
    steps = [TrajectoryStep(1, U.report(rho), purity_P2(rho), B, True, "start")]
    ann, proxy_vals = [], [proxy(rho)] if proxy else []
    for k, ch in enumerate(channel_sequence, start=2):
        assert ch.is_tp(), f"channel {k-1} not trace-preserving"
        new = ch.apply(rho)
        r_new, r_old = U.report(new), U.report(rho)
        # --- lift accounting (A-LIFT) ---
        if ch.cost > 0:
            if B < ch.cost:
                steps.append(TrajectoryStep(k, r_new, purity_P2(new), B, False, "budget exhausted"))
                return TrajectoryResult("LIFT_BUDGET_EXHAUSTION", k, steps, ann)
            B -= ch.cost
        elif purification_claim and purity_P2(new) > purity_P2(rho) and ch.is_unital():
            # unreachable by Lemma Q.3 for exact arithmetic; kept as a consistency assertion
            raise AssertionError("unital channel increased P2 (contradicts Lemma Q.3)")
        # --- report collision (Theorem Q.1) ---
        collided = r_new in seen
        improved = order.gt(r_new, r_old)
        if proxy:
            proxy_vals.append(proxy(new))
            if len(set(proxy_vals)) > len(seen | {r_new}):
                ann.append(f"DECOUPLING_DETECTED(goodhart) at k={k}")
        if collided or not improved:
            steps.append(TrajectoryStep(k, r_new, purity_P2(new), B, False,
                                        "collision" if collided else "no strict improvement"))
            return TrajectoryResult("REPORT_COLLISION", k, steps, ann)
        seen[r_new] = k
        steps.append(TrajectoryStep(k, r_new, purity_P2(new), B, True, "admitted"))
        rho = new
    return TrajectoryResult("TRAJECTORY_EXHAUSTED_NO_TERMINAL", len(channel_sequence)+1, steps, ann)

# ---------- Round 3: nerve, gluing defect, parity class, latency ----------

@dataclass
class SimplicialNerve:
    contexts: list[list[int]]              # each context = list of measurement ids
    support: Callable[[int, tuple], bool]  # support(ctx_index, local_section) -> bool
    outcomes: tuple = (0, 1)

    def edges(self) -> list[tuple[int, int]]:
        n = len(self.contexts)
        return [(i, j) for i in range(n) for j in range(i+1, n)
                if set(self.contexts[i]) & set(self.contexts[j])]

    def support_sections(self, i: int) -> list[dict]:
        C = self.contexts[i]
        return [dict(zip(C, s)) for s in product(self.outcomes, repeat=len(C)) if self.support(i, s)]

def compute_simplicial_holonomy(nerve: SimplicialNerve, cochain=None) -> dict:
    """
    Corrected defect (Round 3 Def. 1.1): minimal edge mismatch over support sections.
    The prompt's triangle coboundary sum |d^1 d^0 s| is identically zero and is NOT computed;
    it is returned as the constant 0 under key 'prompt_d1d0_defect' for parity-assert purposes.
    Also returns the Z2 parity-class test for 'exactly one outcome 1 per context' models.
    """
    secs = [nerve.support_sections(i) for i in range(len(nerve.contexts))]
    E = nerve.edges(); best = None
    for choice in product(*secs):
        mism = sum(1 for (i, j) in E for m in set(nerve.contexts[i]) & set(nerve.contexts[j])
                   if choice[i][m] != choice[j][m])
        best = mism if best is None else min(best, mism)
        if best == 0: break
    return {"phi_glue": best, "prompt_d1d0_defect": 0,
            "parity_class_nonzero": _parity_class_nonzero(nerve)}

def _parity_class_nonzero(nerve: SimplicialNerve) -> bool:
    """Is the all-ones context vector outside the GF(2) row space of the incidence matrix?"""
    rays = sorted({m for C in nerve.contexts for m in C})
    rows = [[1 if r in C else 0 for r in rays] + [1] for C in nerve.contexts]  # augmented
    # Gaussian elimination over GF(2) on columns = rays; 1 in augmented column => inconsistent
    piv = 0; n = len(rays)
    for c in range(n):
        p = next((i for i in range(piv, len(rows)) if rows[i][c]), None)
        if p is None: continue
        rows[piv], rows[p] = rows[p], rows[piv]
        for i in range(len(rows)):
            if i != piv and rows[i][c]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[piv])]
        piv += 1
    return any(all(x == 0 for x in r[:-1]) and r[-1] == 1 for r in rows)

def latency_defect(reports: dict[int, list], coverage: list[tuple[int, int]],
                   latency: Callable[[int, int, int], int], k: int) -> int:
    """Phi_1(delta_k) on the coverage complex (Round 3 section 2.1)."""
    d = 0
    for a, b in coverage:
        for x, y in ((a, b), (b, a)):
            t = latency(x, y, k)
            if reports[y][max(0, k - t)] != reports[y][k]: d += 1
    return d

# ---------- Round 2: certified rational entropy enclosure ----------

def _atanh_series_enclosure(p: Q, q: Q, n: int) -> tuple[Q, Q]:
    """Enclosure of ln(q/p) for 0<p<q via x=(q-p)/(q+p), ln(q/p)=2*sum x^(2k+1)/(2k+1)."""
    x = (q - p) / (q + p); assert 0 < x < 1
    L = 2 * sum(x**(2*k+1) / (2*k+1) for k in range(n+1))
    tail = 2 * x**(2*n+3) / ((2*n+3) * (1 - x*x))
    return L, L + tail

def verify_rational_entropy_interval(density_matrix: Matrix, precision: int) -> dict:
    """
    For a DIAGONAL density matrix with rational spectrum: certified [L,U] ∋ S_e with U-L <= 2^-precision.
    Non-diagonal / algebraic spectra: raise (eigenvalue enclosure is an unresolved obligation).
    """
    n = len(density_matrix)
    for i in range(n):
        for j in range(n):
            if i != j: assert density_matrix[i][j].is_zero(), "non-diagonal: not supported"
    spec = [density_matrix[i][i].re for i in range(n)]
    assert sum(spec) == 1 and all(p >= 0 for p in spec)
    L = U = Q(0); terms = 0
    for p in spec:
        if p == 0 or p == 1: continue
        for order in range(2, 200):               # increase series order until width target
            l, u = _atanh_series_enclosure(p, Q(1), order)   # ln(1/p)
            if p*(u - l) <= Q(1, 2**(precision+1)) / max(1, n): break
        L += p*l; U += p*u; terms += 1
    width = U - L
    return {"L": L, "U": U, "width": width,
            "certified": width <= Q(1, 2**precision),
            "rank_ge_2": terms >= 2,
            "annotation": "DECOUPLING_DETECTED(baker): S_e not representable in K" if terms >= 2 else None}
```

### 2.2 Rust companion `omega_quantum_physics/src/fable51.rs`

```rust
//! Exact-rational companion to fable51.py. Zero floats by construction:
//! `#![forbid(clippy::float_arithmetic)]` is to be enabled in lib.rs; no f32/f64 appears here.
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Zero};
use std::collections::{HashMap, HashSet};

type Q = BigRational;

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct QC { pub re: Q, pub im: Q }
impl QC {
    pub fn zero() -> Self { QC { re: Q::zero(), im: Q::zero() } }
    pub fn one()  -> Self { QC { re: Q::one(),  im: Q::zero() } }
    pub fn conj(&self) -> Self { QC { re: self.re.clone(), im: -self.im.clone() } }
    pub fn add(&self, o: &QC) -> QC { QC { re: &self.re + &o.re, im: &self.im + &o.im } }
    pub fn mul(&self, o: &QC) -> QC {
        QC { re: &self.re*&o.re - &self.im*&o.im, im: &self.re*&o.im + &self.im*&o.re }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Matrix { pub n: usize, pub m: usize, pub a: Vec<QC> }
impl Matrix {
    pub fn identity(n: usize) -> Self { /* diag ones */ unimplemented!() }
    pub fn matmul(&self, b: &Matrix) -> Matrix { unimplemented!() }
    pub fn dagger(&self) -> Matrix { unimplemented!() }
    pub fn add(&self, b: &Matrix) -> Matrix { unimplemented!() }
    pub fn trace(&self) -> QC { unimplemented!() }
    /// Tr(rho^2), asserting the imaginary part vanishes.
    pub fn purity_p2(&self) -> Q { let t = self.matmul(self).trace(); assert!(t.im.is_zero()); t.re }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Terminal {
    ReportCollision,
    LiftBudgetExhaustion,
    OverlapGluingRefusal,
    TrajectoryExhaustedNoTerminal,
}
impl Terminal {
    pub fn label(&self) -> &'static str {
        match self {
            Terminal::ReportCollision => "REPORT_COLLISION",
            Terminal::LiftBudgetExhaustion => "LIFT_BUDGET_EXHAUSTION",
            Terminal::OverlapGluingRefusal => "OVERLAP_GLUING_REFUSAL",
            Terminal::TrajectoryExhaustedNoTerminal => "TRAJECTORY_EXHAUSTED_NO_TERMINAL",
        }
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Annotation { DecouplingDetected { reason: String } , TwoSignalCollapse }

pub trait Report { type Carrier: Eq + std::hash::Hash + Clone; fn report(&self, rho: &Matrix) -> Self::Carrier; }

pub struct QuantumRelationalUniverse { pub dim: usize, pub povm: Vec<Matrix> }
impl QuantumRelationalUniverse {
    pub fn new(dim: usize, povm: Vec<Matrix>) -> Self {
        let s = povm.iter().fold(Matrix { n: dim, m: dim, a: vec![QC::zero(); dim*dim] }, |acc, e| acc.add(e));
        assert_eq!(s, Matrix::identity(dim), "POVM does not sum to I");
        Self { dim, povm }
    }
    pub fn profile(&self, rho: &Matrix) -> Vec<Q> {
        self.povm.iter().map(|e| { let t = rho.matmul(e).trace(); assert!(t.im.is_zero()); t.re }).collect()
    }
    pub fn report_horizon_bound(&self) -> usize { self.povm.len() + 1 }
}
impl Report for QuantumRelationalUniverse {
    type Carrier = usize;                        // modal quantizer, first argmax
    fn report(&self, rho: &Matrix) -> usize {
        let p = self.profile(rho); let mx = p.iter().max().unwrap().clone();
        p.iter().position(|v| *v == mx).unwrap()
    }
}

pub struct KrausChannel { pub kraus: Vec<Matrix>, pub cost: u32 }
impl KrausChannel {
    pub fn apply(&self, rho: &Matrix) -> Matrix { unimplemented!() }
    pub fn is_tp(&self) -> bool { unimplemented!() }
    pub fn is_unital(&self) -> bool { unimplemented!() }
}

/// Round 2: tracks P2 and asserts Lemma Q.3 on unital steps.
pub struct PurityMonitor { pub history: Vec<Q> }
impl PurityMonitor {
    pub fn observe(&mut self, rho: &Matrix, ch_unital: bool) {
        let p = rho.purity_p2();
        if let Some(last) = self.history.last() { if ch_unital { assert!(p <= *last, "Lemma Q.3 violated"); } }
        self.history.push(p);
    }
}

pub struct TrajectoryResult { pub terminal: Terminal, pub k_star: usize, pub annotations: Vec<Annotation> }

pub fn evaluate_cptp_trajectory<U: Report>(
    u: &U, gt: impl Fn(&U::Carrier, &U::Carrier) -> bool,
    rho0: &Matrix, channels: &[KrausChannel], budget: u32,
) -> TrajectoryResult {
    let (mut rho, mut b) = (rho0.clone(), budget);
    let mut seen: HashSet<U::Carrier> = HashSet::new(); seen.insert(u.report(&rho));
    for (idx, ch) in channels.iter().enumerate() {
        let k = idx + 2;
        assert!(ch.is_tp());
        let new = ch.apply(&rho);
        if ch.cost > 0 {
            if b < ch.cost { return TrajectoryResult { terminal: Terminal::LiftBudgetExhaustion, k_star: k, annotations: vec![] }; }
            b -= ch.cost;
        }
        let (rn, ro) = (u.report(&new), u.report(&rho));
        if seen.contains(&rn) || !gt(&rn, &ro) {
            return TrajectoryResult { terminal: Terminal::ReportCollision, k_star: k, annotations: vec![] };
        }
        seen.insert(rn); rho = new;
    }
    TrajectoryResult { terminal: Terminal::TrajectoryExhaustedNoTerminal, k_star: channels.len() + 1, annotations: vec![] }
}

/// Round 3: measurement nerve with support predicate; corrected defect.
pub struct SimplicialNerve { pub contexts: Vec<Vec<usize>>, pub support: Box<dyn Fn(usize, &[u8]) -> bool> }
impl SimplicialNerve {
    pub fn edges(&self) -> Vec<(usize, usize)> { unimplemented!() }
    /// Minimal edge mismatch over support sections (Def. 1.1). Exhaustive; fine for Cabello (4^9).
    pub fn phi_glue(&self) -> usize { unimplemented!() }
    /// GF(2): is the all-ones context vector outside the incidence row space?
    pub fn parity_class_nonzero(&self) -> bool { unimplemented!() }
    /// Prompt's |d^1 d^0 s| sum: identically zero; kept for parity assertion.
    pub fn prompt_d1d0_defect(&self) -> usize { 0 }
}

/// Latency defect on a coverage complex (Round 3 section 2.1).
pub fn latency_defect(reports: &HashMap<usize, Vec<usize>>, coverage: &[(usize, usize)],
                      latency: impl Fn(usize, usize, usize) -> usize, k: usize) -> usize {
    let mut d = 0;
    for &(a, b) in coverage { for (x, y) in [(a, b), (b, a)] {
        let t = latency(x, y, k); let r = &reports[&y];
        if r[k.saturating_sub(t)] != r[k] { d += 1; }
    } }
    d
}

/// Round 2: certified rational enclosure.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RationalInterval { pub lo: Q, pub hi: Q }
impl RationalInterval {
    pub fn width(&self) -> Q { &self.hi - &self.lo }
    /// ln(q/p) via atanh series, order n; tail bound 2x^(2n+3)/((2n+3)(1-x^2)).
    pub fn ln_ratio(p: &Q, q: &Q, n: usize) -> Self { unimplemented!() }
    pub fn entropy_nats_diag(spectrum: &[Q], precision: u32) -> Self { unimplemented!() }
}

#[cfg(test)]
mod tests {
    use super::*;
    /// Parity-assertion suite: terminal labels and k* must equal the Python harness output
    /// on the Round 1-3 witnesses. Expected values are the hand-derived ones; a mismatch is a
    /// defect in the derivation or the code, not a verified fact.
    #[test] fn qubit_m2_modal_collision_at_3()     { /* expect ReportCollision, k*=3 */ }
    #[test] fn bell_panel_m4_collision_at_5()      { /* expect ReportCollision, k*=5 */ }
    #[test] fn werner_amplitude_damping_budget_2() { /* expect LiftBudgetExhaustion at 3rd purification */ }
    #[test] fn dephasing_fixes_diag_3_5_2_5()      { /* P2 = 13/25 before and after (Lemma Q.3 equality) */ }
    #[test] fn cabello_phi_glue_is_1_parity_nonzero() { /* phi_glue == 1, parity_class_nonzero == true */ }
    #[test] fn two_node_tau1_refusal_at_2()        { /* latency_defect(k=2) == 1 */ }
    #[test] fn entropy_diag_3_5_2_5_enclosure()    { /* L=13904738765/20661046784, U=1911955961409/2840893932800 */ }
}
```

**Parity assertion.** A harness runner (`tools/parity.py`) executes the seven witness cases in both languages and asserts byte-equality of `(terminal_label, k_star, sorted(annotations))` and of every rational printed as `num/den` in lowest terms. The Python side outputs `DECOUPLING_DETECTED(...)` annotations; the Rust side must produce the same strings. The label set is the four prompt labels plus `TWO_SIGNAL_COLLAPSE` and `TRAJECTORY_EXHAUSTED_NO_TERMINAL`.

---

## 3. PFP Workpad Contract Schemas (`pfp_calculation_contracts.py`)

All numeric fields are strings of the form `"num/den"` (lowest terms, `den > 0`); no JSON numbers are used for rationals. `claim_status` is one of the six PG3 terminals.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "fable51/pfp_workpads",
  "$defs": {
    "Rational": { "type": "string", "pattern": "^-?[0-9]+/[1-9][0-9]*$" },
    "GaussianRational": { "type": "object", "required": ["re", "im"],
      "properties": { "re": { "$ref": "#/$defs/Rational" }, "im": { "$ref": "#/$defs/Rational" } } },
    "Matrix": { "type": "array", "items": { "type": "array", "items": { "$ref": "#/$defs/GaussianRational" } } },
    "PG3": { "enum": ["evidence_only", "authorized", "rejected", "unresolved", "refused", "not_admitted"] },
    "Terminal": { "enum": ["REPORT_COLLISION", "LIFT_BUDGET_EXHAUSTION", "OVERLAP_GLUING_REFUSAL",
                           "DECOUPLING_DETECTED", "TWO_SIGNAL_COLLAPSE", "TRAJECTORY_EXHAUSTED_NO_TERMINAL"] }
  },

  "PfpQubitPovmWorkpad": {
    "type": "object",
    "required": ["dim", "effects", "effect_traces", "sum_is_identity", "gram_matrix", "gram_determinant",
                 "report_capacity_N", "horizon_bound", "claim_status"],
    "properties": {
      "dim": { "type": "integer", "minimum": 2 },
      "effects": { "type": "array", "items": { "$ref": "#/$defs/Matrix" } },
      "effect_traces": { "type": "array", "items": { "$ref": "#/$defs/Rational" } },
      "sum_is_identity": { "type": "boolean" },
      "gram_matrix": { "description": "G_mn = Tr(E_m E_n)", "type": "array",
                       "items": { "type": "array", "items": { "$ref": "#/$defs/Rational" } } },
      "gram_determinant": { "$ref": "#/$defs/Rational",
                            "description": "det G; nonzero iff effects linearly independent (informational only; not used by Theorem Q.1)" },
      "quantizer": { "enum": ["modal", "k_shot", "histogram"] },
      "report_capacity_N": { "type": "integer" },
      "horizon_bound": { "type": "integer", "description": "N+1" },
      "claim_status": { "$ref": "#/$defs/PG3" }
    }
  },

  "PfpPurityBudgetWorkpad": {
    "type": "object",
    "required": ["steps", "B0", "terminal", "k_star", "lemma_q3_checked", "claim_status"],
    "properties": {
      "B0": { "type": "integer", "minimum": 0 },
      "steps": { "type": "array", "items": { "type": "object",
        "required": ["k", "P2", "budget_after", "channel_unital", "channel_cost", "admitted"],
        "properties": {
          "k": { "type": "integer" }, "P2": { "$ref": "#/$defs/Rational" },
          "budget_after": { "type": "integer" }, "channel_unital": { "type": "boolean" },
          "channel_cost": { "type": "integer" }, "admitted": { "type": "boolean" },
          "spectrum": { "type": "array", "items": { "$ref": "#/$defs/Rational" } } } } },
      "lemma_q3_checked": { "type": "boolean", "description": "P2 non-increasing on every unital step" },
      "terminal": { "$ref": "#/$defs/Terminal" }, "k_star": { "type": "integer" },
      "claim_status": { "$ref": "#/$defs/PG3" }
    }
  },

  "PfpContextualityHolonomyWorkpad": {
    "type": "object",
    "required": ["contexts", "support_rule", "edges", "phi_glue", "prompt_d1d0_defect",
                 "parity_class_nonzero", "contextual_fraction_lower", "terminal", "claim_status"],
    "properties": {
      "contexts": { "type": "array", "items": { "type": "array", "items": { "type": "integer" } } },
      "support_rule": { "enum": ["exactly_one", "full", "custom"] },
      "edges": { "type": "array", "items": { "type": "array", "items": { "type": "integer" }, "minItems": 2, "maxItems": 2 } },
      "triple_overlaps": { "type": "integer" },
      "phi_glue": { "type": "integer", "description": "Def. 1.1 minimal edge mismatch" },
      "prompt_d1d0_defect": { "const": 0, "description": "identically zero; retained to document the correction" },
      "parity_class_nonzero": { "type": "boolean" },
      "contextual_fraction_lower": { "$ref": "#/$defs/Rational" },
      "latency_defect_trace": { "type": "array", "items": { "type": "integer" } },
      "terminal": { "$ref": "#/$defs/Terminal" }, "claim_status": { "$ref": "#/$defs/PG3" }
    }
  },

  "PfpRationalIntervalWorkpad": {
    "type": "object",
    "required": ["spectrum", "precision_bits", "L", "U", "width", "certified", "baker_applies", "claim_status"],
    "properties": {
      "spectrum": { "type": "array", "items": { "$ref": "#/$defs/Rational" } },
      "series_orders": { "type": "array", "items": { "type": "integer" } },
      "precision_bits": { "type": "integer" },
      "L": { "$ref": "#/$defs/Rational" }, "U": { "$ref": "#/$defs/Rational" },
      "width": { "$ref": "#/$defs/Rational" },
      "certified": { "type": "boolean", "description": "width <= 2^-precision_bits by exact comparison" },
      "baker_applies": { "type": "boolean", "description": "rank >= 2 with algebraic spectrum" },
      "relation_lattice_trivial": { "type": "boolean" },
      "decimal_sanity_check": { "type": "string", "description": "informational only; never used in the certificate" },
      "claim_status": { "$ref": "#/$defs/PG3" }
    }
  }
}
```

---

## 4. Lean 4 Blueprints (`OmegaQuantumRelationalRsi`)

**Status:** declarations with intended proof terms; not elaborated here. Only Mathlib and the standard Lean axioms (`propext`, `Quot.sound`, `Classical.choice`) are intended; no `axiom` declarations. Baker's theorem is not in Mathlib and is therefore a *hypothesis* of the one theorem that needs it, not an axiom.

```lean
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Fintype.Pigeonhole
import Mathlib.Order.Basic
import Mathlib.Order.WellFounded

namespace OmegaQuantumRelationalRsi

/-! ## Round 1 core: report-grounded strict order on an arbitrary state type -/

structure ReportGrounded {S C : Type*} (report : S → C) (gt : S → S → Prop) : Prop where
  irrefl : ∀ ρ, ¬ gt ρ ρ
  trans  : ∀ ρ σ τ, gt ρ σ → gt σ τ → gt ρ τ
  grounded : ∀ ρ₁ ρ₂ σ₁ σ₂, report ρ₁ = report ρ₂ → report σ₁ = report σ₂ → gt ρ₁ σ₁ → gt ρ₂ σ₂

/-- Round 1 Lemma Q.2(a): equal reports exclude strict dominance. -/
theorem no_dominance_of_report_eq {S C : Type*} {report : S → C} {gt : S → S → Prop}
    (h : ReportGrounded report gt) {ρ σ : S} (e : report ρ = report σ) : ¬ gt ρ σ :=
  fun hg => h.irrefl σ (h.grounded ρ σ σ σ e rfl hg)

/-- Chain closure under transitivity. -/
theorem chain_dominates {S : Type*} {gt : S → S → Prop}
    (htrans : ∀ ρ σ τ, gt ρ σ → gt σ τ → gt ρ τ) (f : ℕ → S)
    (hstep : ∀ k, gt (f (k+1)) (f k)) : ∀ i j, i < j → gt (f j) (f i) := by
  intro i j hij
  induction hij with
  | refl => exact hstep i
  | step _ ih => exact htrans _ _ _ (hstep _) ih

/-- Round 1 Theorem Q.1: no trajectory carries a strict report-grounded
improvement claim at every step; a failing step exists with index ≤ card C. -/
theorem report_collision_horizon {S C : Type*} [Fintype C] [DecidableEq C]
    (report : S → C) (gt : S → S → Prop) (h : ReportGrounded report gt)
    (f : ℕ → S) :
    ∃ k, k ≤ Fintype.card C ∧ ¬ gt (f (k+1)) (f k) := by
  by_contra hall
  push_neg at hall
  -- hall : ∀ k, k ≤ card C → gt (f (k+1)) (f k)
  -- pigeonhole on (Fin (card C + 1) → C) via report ∘ f
  obtain ⟨i, j, hne, hij⟩ := Fintype.exists_ne_map_eq_of_card_lt
    (fun i : Fin (Fintype.card C + 1) => report (f i)) (by simp)
  -- WLOG i < j; chain gives gt (f j) (f i); no_dominance_of_report_eq contradicts.
  sorry  -- proof skeleton; to be discharged in the tooling pass

/-! ## Round 2 core: strictly descending integer budget -/

/-- Round 2 Theorem Q.2(a): a budget strictly decreasing on every "purification" step
admits at most B₀ such steps. -/
theorem lift_budget_exhaustion (B : ℕ → ℕ) (pur : ℕ → Prop) [DecidablePred pur]
    (hdec : ∀ k, pur k → B (k+1) < B k) (hmono : ∀ k, B (k+1) ≤ B k) :
    ∀ n, (Finset.range n).filter pur |>.card ≤ B 0 := by
  sorry  -- induction on n using hdec/hmono; each purification step removes ≥1 from a ℕ

/-! ## Round 3 core: gluing refusal as a decidable predicate on a finite complex -/

structure CoverageComplex (V : Type*) where
  edges : Finset (V × V)

/-- Φ₁(δ_k) = 0 iff no in-window report change on any coverage edge. -/
def gluesAt {V C : Type*} [DecidableEq C] (K : CoverageComplex V)
    (rep : V → ℕ → C) (lat : V → V → ℕ → ℕ) (k : ℕ) : Prop :=
  ∀ e ∈ K.edges, rep e.2 (k - lat e.1 e.2 k) = rep e.2 k ∧ rep e.1 (k - lat e.2 e.1 k) = rep e.1 k

/-! ## Round 2 representability: Baker as an explicit hypothesis -/

/-- Shape of the Baker consequence (B*) used in Theorem Q.2.1. Not provable in Mathlib today;
carried as a hypothesis, never as an axiom. -/
def BakerLinearForms : Prop :=
  ∀ (n : ℕ) (α β : Fin n → ℝ), (∀ i, IsAlgebraic ℚ (α i) ∧ 0 < α i) → (∀ i, IsAlgebraic ℚ (β i)) →
    (∑ i, β i * Real.log (α i)) ≠ 0 → Transcendental ℚ (∑ i, β i * Real.log (α i))

/-- Round 2 Theorem Q.2.1(1), conditional. -/
theorem entropy_transcendental_of_baker (hB : BakerLinearForms) (n : ℕ) (p : Fin n → ℝ)
    (halg : ∀ i, IsAlgebraic ℚ (p i)) (hpos : ∀ i, 0 < p i) (hsum : ∑ i, p i = 1) (hrank : 2 ≤ n) :
    Transcendental ℚ (-(∑ i, p i * Real.log (p i))) := by
  sorry  -- apply hB with α = p, β = -p; nonvanishing from 0<p_i<1

/-! ## Composite -/

/-- Round 4 Theorem Q.Master clause (vii)/(viii), combinatorial content only:
under report-groundedness the first non-admitted index is ≤ min of the active bounds.
Renamed from the prompt's `quantum_rsi_impossible`. -/
theorem quantum_rsi_bounded_horizon {S C : Type*} [Fintype C] [DecidableEq C]
    (report : S → C) (gt : S → S → Prop) (h : ReportGrounded report gt)
    (f : ℕ → S)
    (B : ℕ → ℕ) (pur : ℕ → Prop) [DecidablePred pur]
    (hdec : ∀ k, pur k → B (k+1) < B k) (hmono : ∀ k, B (k+1) ≤ B k)
    (hclaim : ∀ k, pur k → gt (f (k+1)) (f k)) :
    ∃ k, k ≤ min (Fintype.card C) (B 0) ∧
         (¬ gt (f (k+1)) (f k) ∨ (pur k ∧ B k = 0)) := by
  sorry  -- combine report_collision_horizon and lift_budget_exhaustion; take the earlier index

end OmegaQuantumRelationalRsi
```

Notes on the blueprint: (1) `report_collision_horizon` bounds the failing index by `card C` with 0-based `f`, matching Round 1's $N+1$ with 1-based $\rho_k$. (2) `BakerLinearForms` is stated in the shape actually used; a Mathlib-faithful statement would need the full homogeneous Baker theorem, and discharging it is out of scope. (3) The stabilizer clause is obtained from `report_collision_horizon` by instantiating `C` with a `Fintype` of stabilizer states of the correct cardinality; that `Fintype` instance and its `card` lemma are tooling obligations.

---

## 5. Epistemic Routing (PG3)

| Item | Terminal | Grounds |
|---|---|---|
| Theorem Q.Master (i)–(vi) | $\mathsf{authorized}$ under the respective declared hypotheses | each clause is a Round 1–3 result, re-cited with its hypotheses |
| Theorem Q.Master (vii) composite min | $\mathsf{authorized}$ on the intersection of hypotheses | minimum of upper bounds |
| Prompt's unconditional $\min(M+1,B_0+1,\lvert Stab_n\rvert+1)$ | $\mathsf{not\_admitted}$ as stated | terms derived under different hypotheses |
| "Four mutually disjoint failure modes" | $\mathsf{rejected}$ | modes can coincide; replaced by priority order |
| Baker decoupling as a step-indexed terminal | $\mathsf{rejected}$ | it is a claim-type routing, active at every step |
| Conjectured $(B_{\mathrm{ext}}+1)(\lvert Stab_n\rvert+1)$ bound | $\mathsf{unresolved}$ | landing assumption not justified |
| §2 Python/Rust harness | $\mathsf{evidence\_only}$ | specification; not executed |
| §3 schemas | $\mathsf{authorized}$ as declared contracts | syntactic |
| §4 Lean blueprint | $\mathsf{evidence\_only}$ | contains `sorry`; not elaborated |
| Status label `VERIFIED_SYNTHESIS_COMPLETE` | $\mathsf{authorized}$ only with the attached `status_meaning` | no tool ran |

---

## 6. Claim Hygiene Summary

- **Supported:** In this model, a strict report-grounded improvement claim cannot be admitted at every step; the first non-admitted index is bounded, under the respective declared hypotheses, by $N+1$ (report collision), by the corrected stabilizer count plus one, by $B_0+1$ for entropy-decrease claims, and by the first in-window report change plus one or $\prod_aN_a+1$ on a communicating complex; exact carrier values of von Neumann entropy are not admissible on an algebraic carrier (conditional on Baker); self-verified steps route $\mathsf{evidence\_only}$; the minimum of the active bounds is a bound. Explicit witnesses from Rounds 1–3 attain the report, latency, and lift bounds.
- **Not supported:** the prompt's unconditional three-term minimum; mutual disjointness of the four modes; Baker decoupling as a termination index; any statement about the dynamics past $k^*$; the external-lift composite bound; that the harness runs, compiles, or agrees across languages; that the Lean declarations elaborate; Baker's theorem itself; algebraic (non-rational) eigenvalue enclosures.
- **Narrowest defensible claim:** Under (H0), (A-REP), (H-DOM), (H-TRAJ), a self-modifying quantum trajectory's strict improvement certificate fails by index $N+1$; each additional declared hypothesis set (stabilizer confinement, ancilla budget, communication latency, contextual nerve, algebraic carrier, two-signal verification) supplies a further bound or routing, and the admitted certificate length is at most the minimum of the bounds whose hypotheses hold.
- **Next check:** run the dual-language parity suite on the seven witnesses (expected: collision at 3 and 5; lift exhaustion at the third purification; dephasing fixed point $13/25$; Cabello $\Phi_{\mathrm{glue}}=1$ with nonzero parity class; two-node $\tau=1$ refusal at 2; entropy enclosure endpoints as recorded) and treat any mismatch as a defect in either the derivation or the code; then discharge the `sorry`s in `report_collision_horizon` and `lift_budget_exhaustion` and check `#print axioms quantum_rsi_bounded_horizon` shows only the standard three.

```json
{
  "campaign_id": "FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION",
  "round": 4,
  "status": "VERIFIED_SYNTHESIS_COMPLETE",
  "status_meaning": "synthesis of hand-derived Rounds 1-3 into a case-structured composite theorem plus harness/schema/Lean specifications; no Python, Rust, Lean, or solver executed; nothing machine-checked; code and Lean are specifications with explicit unimplemented!/sorry markers",
  "theorems_derived": [
    "R1: Prop_2_1_HorizonCeiling",
    "R1: Lemma_Q_1_POVM_ReportCarrierFinitude",
    "R1: Lemma_Q_2_DescentToReportCarrier",
    "R1: Theorem_Q_1_QuantumBoundedRSIHorizon_ReportCollision",
    "R1: Prop_5_1_GoodhartProxyDecoupling",
    "R1: Corollary_Q_1_1_StabilizerOrbitFinitude (count 2^n prod (2^j+1))",
    "R2: Lemma_1_1_DoublyStochasticSpectralTransfer",
    "R2: Lemma_Q_3_PurityDissipation_Unital",
    "R2: Corollary_1_2_UnitalMonotones",
    "R2: Lemma_1_3_ArakiLieb_PerStepEntropyBound",
    "R2: Theorem_Q_2_PurityLiftExhaustion",
    "R2: Theorem_Q_2_1_TranscendentalEntropyDecoupling (conditional on Baker)",
    "R2: Proposition_3_1_DyadicRationality_and_ScopeBoundary",
    "R3: Theorem_Q_3_ContextualityAsGluingDefect (corrected form)",
    "R3: Theorem_Q_3a_Cabello18_StrongContextuality_PhiGlue_eq_1_ParityClassNonzero",
    "R3: Theorem_Q_3b_RationalCHSH_344_over_125_CF_ge_47_over_125",
    "R3: Lemma_2_1_LatencyDefectCharacterization",
    "R3: Theorem_Q_3_2_AsynchronousHorizon",
    "R3: Lemma_Q_4_NoSelfTomography_TwoSignalCollapse",
    "R4: Theorem_Q_Master_QuantumRelationalBoundedRSIHorizon (case-structured; clauses i-viii)"
  ],
  "composite_bound": "k* <= min{ N+1 ; 2^n prod_{j=1..n}(2^j+1)+1 [H-STAB] ; B_0+1 [A-LIFT, entropy claims] ; T_glue [H-COMM] ; prod_a N_a + 1 [H-COMM] }, terminal by priority OVERLAP_GLUING_REFUSAL < LIFT_BUDGET_EXHAUSTION < REPORT_COLLISION; DECOUPLING_DETECTED and TWO_SIGNAL_COLLAPSE are claim-routing annotations",
  "corrections_to_prompt": [
    "Unconditional min(M+1, B_0+1, |Stab_n|+1) replaced by a case-structured bound; the prompt form is the modal-quantizer, stabilizer, entropy-claim, single-node special case.",
    "Failure modes are not mutually disjoint; a declared priority order makes the terminal a function.",
    "BAKER_TRANSCENDENTAL_DECOUPLING is a claim-type routing active at every step, not a step-indexed terminal; harness label unified to DECOUPLING_DETECTED with a reason field.",
    "Lean target renamed quantum_rsi_impossible -> quantum_rsi_bounded_horizon (vocabulary and content).",
    "Stabilizer count correction from Round 1 retained."
  ],
  "verification_artifacts": {
    "python_module": "omega_quantum_physics/fable51.py",
    "python_contracts": "omega_quantum_physics/pfp_calculation_contracts.py",
    "python_parity_runner": "tools/parity.py",
    "rust_crate": "omega_quantum_physics/src/fable51.rs",
    "rust_tests": "omega_quantum_physics/src/fable51.rs#tests (7 witness cases)",
    "lean_file": "OmegaQuantumRelationalRsi/Core.lean",
    "lean_targets": [
      "no_dominance_of_report_eq", "chain_dominates", "report_collision_horizon",
      "lift_budget_exhaustion", "gluesAt", "entropy_transcendental_of_baker",
      "quantum_rsi_bounded_horizon"
    ],
    "lean_axiom_check": "#print axioms quantum_rsi_bounded_horizon (expected: propext, Quot.sound, Classical.choice only)",
    "execution_state": "none of the above executed, compiled, or elaborated in this campaign"
  },
  "unresolved_obligations": [
    "External-lift budget integration for stabilizer/transversal orbit escape; conjectured bound (B_ext+1)(|Stab_n|+1) requires a justified landing assumption.",
    "CPTP contractivity strengthening of Theorem Q.1 (unused CPTP structure).",
    "Justify or replace (A-LIFT.2) identifying budget-free steps with unital channels.",
    "Certified enclosures for algebraic non-rational spectra (eigenvalue isolation over K).",
    "Contextual-fraction LP for the rational CHSH tables (CF = 47/125 or larger).",
    "Abramsky-Mansfield-Barbosa relative cohomology obstruction for Cabello across all local sections.",
    "Stochastic single-shot reports and single-copy verifier error (quantum Chernoff) folded into the joint horizon.",
    "F2/F4 finiteness senses (cyclotomic carrier arithmetic, finite-field scalar models) never exercised.",
    "Discharge all sorry markers; implement unimplemented! stubs; run the parity suite."
  ],
  "claim_hygiene": {
    "supported": "Under the declared hypothesis sets, a strict report-grounded improvement certificate fails by index N+1, and additional declared structure supplies further bounds (corrected stabilizer count +1; B_0+1 for entropy-decrease claims; first in-window report change +1 and prod N_a + 1 on communicating complexes) and routings (Baker non-representability of exact S on algebraic carriers, conditional on Baker; self-verified steps evidence_only); the minimum of active bounds is a bound; Round 1-3 witnesses attain the report, latency, and lift bounds.",
    "not_supported": "The prompt's unconditional three-term minimum; mutual disjointness of the four modes; Baker decoupling as a step index; statements about dynamics past k*; the external-lift composite; that the harness runs or agrees across languages; that the Lean file elaborates; Baker's theorem itself; algebraic-eigenvalue enclosures.",
    "narrowest_claim": "Under (H0), (A-REP), (H-DOM), (H-TRAJ), a self-modifying quantum trajectory's strict improvement certificate fails by index N+1; each further declared hypothesis set adds a bound or routing, and the admitted certificate length is at most the minimum of the bounds whose hypotheses hold.",
    "next_check": "Execute the dual-language parity suite on the seven recorded witnesses and treat any mismatch as a defect; then discharge the Lean sorry markers for report_collision_horizon and lift_budget_exhaustion and confirm the axiom print shows only propext, Quot.sound, Classical.choice."
  }
}
```