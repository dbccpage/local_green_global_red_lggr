# LGGR Witness Audit

**AuthorityEffect: None.** Working Python reference implementation of the finite mechanisms in the supplied report, *Local Green, Global Red: cumulative drift under protected local evaluation*, connecting the **Local Green, Global Red (LGGR) Foundational Series (Volumes I–VI)** with **Bell's Theorem as a Positive-Extension Obstruction: Projection residuals, uncertainty, and embedded knowledge**.

**Description:** Finite witness-composition, report-fiber decoder/collision certification, exact rational $\ell^1$ repair and cochain classification, chain-retraction transport verification, and observer-sufficiency models for evaluating when locally passing reports fail to determine or satisfy a declared global requirement.

**Keywords:** `local-green-global-red`, `finite-obstruction-calculus`, `evaluated-path-kernels`, `organizational-gluing`, `observer-sufficiency`, `decoder-or-collision`, `witness-composition`, `cochain-obstruction`, `l1-duality`, `projection-residuals`, `positive-extensions`, `bell-inequalities`, `contextual-fraction`, `embedded-knowledge`, `recursive-self-improvement`

This is a standalone, tested adapter. It does **not** modify the Omega Engine or finite-QM repositories, execute a hosted model, authenticate an owner, or authorize a merge. The source report and companion papers supply the mathematical formulations; this package implements scoped checks on explicit finite data.

## Wiring a harness

If you are adding these checks to your own agent loop or swarm, start with [`learn/README.md`](learn/README.md). Ten lessons show which object is the report, which is the query, and which extra generation cannot shrink a fiber. From the repository root:

```console
python learn/check.py
```

**AuthorityEffect: None.** The course calls the monitors in this package. It does not admit an authority.

## Foundational Context: LGGR Series & Positive-Extension / Projection Residuals

This repository synthesizes executable finite verification rules from two related lines of work:

### 1. The Local Green, Global Red Foundational Series (Volumes I–VI) & Witnessed Difference Programme

The six-volume LGGR series (`001_local_green_global_red_foundational_series`) and the Witnessed Difference Programme (WDP) examine when local observations, step verdicts, or restricted reports fail to determine a declared global proposition:

| Volume / Source | Core Mathematical Mechanism | Role in This Repository |
|---|---|---|
| **WDP (`ComponentReports`)** | **Decoder-or-collision dichotomy (`decoder_xor_collision`):** For a report map $p: X \to A$ and protected query $q: X \to B$, a unique decoder $D: p(X) \to B$ with $D \circ p = q$ exists if and only if $q$ is constant on every realized fiber $p^{-1}(a)$; otherwise an explicit colliding pair $(x, y)$ with $p(x) = p(y)$ and $q(x) \ne q(y)$ witnesses report insufficiency. | Implemented in `lggr/descent.py` (`analyze_descent`, `verify_descent_certificate`, `decode`). |
| **LGGR I (*Evaluated Path Kernels*)** | **Boolean evaluator defect:** $\Delta_E = E_g - \prod_i E_i \in \{-1, 0, 1\}$, classifying triples into `NGD` ($-1$, local green / global red), `ZDR` ($0$, agreement including joint rejection), and `PGD` ($+1$, local red / global green). **Verdict ceiling (`verdict_ceiling`):** Any evaluator factoring solely through a colliding report disagrees with the target on at least one member of the colliding pair. | Implemented in `lggr/descent.py` (`evaluator_defect`) and exhausted across all 8 Boolean triples and 216 three-state report/query maps. |
| **LGGR II (*Organizational Evaluator Gluing*)** | **Boundary sufficiency vs. quotient factorization:** A boundary report can determine $E_g$ without making $E_g$ equal to the product of local verdicts; mixed carrier fibers block quotient factorization. Representation, ownership, temporal, and agreement requirements are declared closure conditions rather than automatic operational authority. | Reflected in `lggr/witnesses.py` via explicit boundary matching, policy-manifest digests, representation/evaluator/authority identity checks, and retained obligations. |
| **LGGR III (*Six-Role Evaluator Overlay*)** | **Role-indexed evaluation:** The same finite evaluator calculus recorded across six mathematical role profiles (*finite obstruction, foundations, representation, observer, continuum shadow, and action alignment*). These are accounting profiles rather than game-theoretic seats or anti-collusion theorems. | Preserved in the scope boundary: identity and role tags track declared provenance without asserting statistical independence or payoff dominance. |
| **LGGR IV (*Completion-Relative Obstruction*)** | **Stage-wise vs. completed solutions:** Compatible finite-stage solutions (such as $3x + 1 \equiv 0 \pmod{2^n}$) need not admit a single uncompleted witness; descent from a completion back to the original carrier requires membership in the reflection image (`reflection_descent_criterion`). | Reflected in explicit scope separation between finite-table certification, prefix vs. endpoint history queries, and uncertified extrapolation refusal. |
| **LGGR V (*Finite No-Recovery & Repair Distance*)** | **Realizable soundness and $\ell^1$ repair duality:** For linear section-defect map $D$ and observation map $Q$, soundness on realizable defects is $\mathrm{im}(D) \cap \ker(Q) = \{0\}$. Raw defect mass $\|Ds\|_1$ (distance $0$ to $\mathrm{im}(D)$) is kept distinct from weighted $\ell^1$ repair distance $\Phi(h) = \min_x \sum_e w_e |h_e - (Dx)_e|$, certified by a dual annihilator $D^\top z = 0$, $|z_e| \le w_e$, and matching primal residual. | Implemented in `lggr/linear.py` (`verify_l1_certificate`, `classify_cochain`), separating exact coboundaries, closure failures ($d_1 h \ne 0$), and closed nonexact 1-cochains. |
| **LGGR VI (*Nonlinear Aggregation & Adjoint Probing*)** | **Postprocessing invariance and Gram radical:** Deterministic postprocessing cannot separate states sharing an observation ($O(x) = O(y) \Rightarrow f(O(x)) = f(O(y))$). Over the rationals, $\ker(Q^\top Q) = \ker Q$; centered two-query and full sign-cube probes recover $Q^\top Q x$ but remain blind on $\ker Q$. | Motivates `lggr/transport.py` (`verify_transport`): forward commutation ($F_1 D_{\text{src}} = D_{\text{tgt}} F_0$) transports repairs, whereas preserving nonrepairability requires a verified left-inverse chain retraction ($G_k F_k = I$). |
| **LGGR VIII (*Online Streaming Discovery*)** | **Online streaming runtime monitor:** Incremental fiber collision detection ($p(x_1) = p(x_2)$ with $q(x_1) \ne q(x_2)$), streaming evaluator defect tracking ($\Delta_E \in \{-1, 0, 1\}$), monotonic `every_prefix` early stopping, and incremental 1-cochain cycle closure with exact rational $\ell^1$ dual witness repair certification. | Implemented in `lggr/streaming.py` (`StreamingFiberMonitor`, `StreamingAuditMonitor`, `StreamingCochainMonitor`) and demonstrated in `cookbooks/`. |

### 2. Bell Positive Extensions, Projection Residuals, and Embedded Task Sufficiency

The companion study *Bell's Theorem as a Positive-Extension Obstruction* (`003_bell_positive_extensions_and_projection_residuals`) connects finite obstruction certificates and projection residuals to empirical behavior tables, nonlocality measures, and recursive self-improvement (RSI) under fixed evidence:

1. **Four Distinct Obstruction Questions:**
   - *Product-state retraction residual:* $F_\rho = \rho - \rho_A \otimes \rho_B$ and $D_{\text{prod}}(\rho) = \|F_\rho\|_1$ measure departure from a single tensor product. A classically correlated separable state such as $\rho_{\text{cl}} = \frac{1}{2}|00\rangle\langle 00| + \frac{1}{2}|11\rangle\langle 11|$ has $D_{\text{prod}}(\rho_{\text{cl}}) = 1$ yet admits a local hidden-variable model for every local measurement choice.
   - *Overlap consistency:* Agreement of context distributions on restricted marginals (no-signalling). Quantum Bell violations satisfy overlap consistency, so linear overlap defects vanish even when global positive extension fails.
   - *Positive global extension:* Existence of a nonnegative distribution $q \ge 0$, $\mathbf{1}^\top q = 1$ over the finite deterministic response space $\Omega = A^X \times B^Y$ such that $Tq = p$ (defining the Bell-local polytope $\mathcal{L} = T\Delta(\Omega)$). In the CHSH no-signalling affine space, signed extensions $Tq = p$ with $\mathbf{1}^\top q = 1$ exist, whereas positive extensions fail above the classical threshold ($|S(p)| > 2$).
   - *Cochain / cohomology classes:* At the deterministic PR-box support endpoint ($v = 1$), parity equations $u_x + v_y = xy \pmod 2$ define a nonzero class in $H^1(K_{2,2}; \mathbb{F}_2)$. For full-support probabilistic quantum violations ($1/2 < v < 1$, including the Tsirelson point $v = 1/\sqrt{2}$), every deterministic assignment remains in the support; the obstruction is carried by probability weights and certified by separating linear dual witnesses rather than support cohomology.

2. **Projection Residuals, Signed Negative Mass, and Contextual Fraction:**
   - **Total-variation repair cost:** $R_\pi(p) = \min_{\ell \in \mathcal{L}} \|p - \ell\|_\pi$, certified via dual Bell functionals satisfying vertex bounds on $\Omega$.
   - **Signed-extension negative mass ($N_{\min}$) vs. contextual fraction ($CF$):** For a behavior $p$, $N_{\min}(p)$ minimizes $\sum_\lambda q_\lambda^-$ over normalized signed extensions $T(q^+ - q^-) = p$, whereas $CF(p) = 1 - \max\{\mathbf{1}^\top \gamma : \gamma \ge 0,\, T\gamma \le p\}$ measures the deficiency of the largest dominated local subdistribution.
   - **Symmetric equality vs. general three-party separation:** Along the real-parameter isotropic CHSH and eight-context Mermin families ($0 \le v \le 1$), both measures satisfy $N_{\min} = \max(0, v - \frac{1}{2})$ and $CF = \max(0, 2v - 1) = 2 N_{\min}$. On general three-party, two-setting, two-outcome no-signalling tables, exact rational primal/dual simplex certificates show that $CF \le 2 N_{\min}$ is not invariant: an explicit no-signalling mixture $p_*$ satisfies $CF(p_*) = \frac{19}{64}$ and $N_{\min}(p_*) = \frac{25}{256}$ ($CF - 2N_{\min} = \frac{13}{128} > 0$), reversing the relative ordering against $Q_{5/8}$ ($CF(Q_{5/8}) = \frac{1}{4} < CF(p_*)$ while $N_{\min}(Q_{5/8}) = \frac{1}{8} > N_{\min}(p_*)$). Across any finite scenario where every deterministic column has constant positive context weight $m$, a constructive packing bound gives $CF(p) \le (m - 1) N_{\min}(p)$.

3. **Observer-Fiber Minimax Floor and Evidence-Preserving RSI:**
   - Given a finite history carrier $\mathcal{H}$, presentation map $O: \mathcal{H} \to Y$ with fibers $\mathcal{H}_y = O^{-1}(y)$, and a scalar target $f: \mathcal{H} \to \mathbb{R}$ with fiber spread $W_f(y) = \max_{h \in \mathcal{H}_y} f(h) - \min_{h \in \mathcal{H}_y} f(h)$, exact prediction $f = g \circ O$ holds if and only if $W_f(y) = 0$ on every realized fiber. More generally, the worst-case scalar prediction error satisfies the minimax identity
     $$\inf_g \max_{h \in \mathcal{H}} |f(h) - g(O(h))| = \frac{1}{2} \max_{y \in O(\mathcal{H})} W_f(y),$$
     attained by the fiber midpoint predictor.
   - **Evidence-preserving recursion bound:** If a system updates its internal state, code, or predictor through any finite number of recursive steps using only fixed initial evidence $y = O(h)$ and randomness whose conditional law depends only on $y$, its output distribution is identical across all $h \in \mathcal{H}_y$, yielding
     $$\max_{h \in \mathcal{H}_y} \mathbb{E}|Z_n - f(h)| \ge \frac{1}{2} W_f(y).$$
     Internal self-modification or postprocessing on fixed evidence cannot shrink a nonzero fiber width; reducing the floor requires informative new observations that refine $O^{-1}(y)$ or a justified domain restriction on $\mathcal{H}$.

4. **Comparison of Failure Modes and Certificates:**

| Question | Mathematical Test | Failure Witness | Package Analog |
|---|---|---|---|
| **Bell-local positive extension** | Does $T^{-1}(p) \cap \Delta(\Omega)$ contain a point? | Separating Bell / LP dual functional | `lggr/linear.py` (`verify_l1_certificate`) |
| **Exact task/query recovery from report** | Is $q$ (or $f$) constant on every fiber $O^{-1}(y)$? | Colliding pair $h_0, h_1$ with $O(h_0) = O(h_1)$ and $q(h_0) \ne q(h_1)$ | `lggr/descent.py` (`analyze_descent`) |
| **Cumulative step-history budget** | Does $\sum_i (x_i - x_{i-1})$ stay within $[-B, B]$ from baseline $x_0$? | Signed endpoint witness exceeding $B$ (or `WITNESS_INCOMPLETE` if only unsigned local passes are retained) | `lggr/witnesses.py` (`audit_history`) |
| **Linear cochain repairability** | Does $h \in \mathrm{im}(D_0)$, and if not, is $D_1 h = 0$? | Dual annihilator $D_0^\top z = 0$ with $z^\top h > 0$; closure check $D_1 h$ | `lggr/linear.py` (`classify_cochain`) |
| **Representation transport** | Do chain maps $(F_0, F_1)$ commute with $D$, and do $(G_0, G_1)$ retract $(F_0, F_1)$? | Nonzero commutation defect or missing left inverse $G_k F_k \ne I$ | `lggr/transport.py` (`verify_transport`) |

## Papers and Lean 4 Formalizations

- **[`papers/`](papers/README.md):** Contains the eight-volume *Local Green, Global Red* series (`lggr_i_evaluated_path_kernels` through `lggr_viii_online_streaming_discovery_and_runtime_gluing`) and the [monograph and implementation index](papers/local_green_global_red_monograph_index.md):
  - [`papers/lggr_i_evaluated_path_kernels/`](papers/lggr_i_evaluated_path_kernels/lggr_i_evaluated_path_kernels.md) — Volume I: *Evaluated Path Kernels for Composed Agent Reliability*
  - [`papers/lggr_ii_organizational_gluing/`](papers/lggr_ii_organizational_gluing/lggr_ii_organizational_gluing.md) — Volume II: *Organizational Evaluator Gluing*
  - [`papers/lggr_iii_epk_gtla_overlay/`](papers/lggr_iii_epk_gtla_overlay/lggr_iii_epk_gtla_overlay.md) — Volume III: *A Finite Evaluator Overlay Across Six System Roles*
  - [`papers/lggr_iv_finite_presentations_completion_relative/`](papers/lggr_iv_finite_presentations_completion_relative/lggr_iv_finite_presentations_completion_relative.md) — Volume IV: *Finite Presentations and Completion-Relative Obstruction*
  - [`papers/lggr_v_local_green_global_red/`](papers/lggr_v_local_green_global_red/lggr_v_local_green_global_red.md) — Volume V: *Local Green, Global Red: When Local Evaluators Cannot Certify Global Exactness*
  - [`papers/lggr_vi_nonlinear_aggregation_and_adjoint_probing/`](papers/lggr_vi_nonlinear_aggregation_and_adjoint_probing/lggr_vi_nonlinear_aggregation_and_adjoint_probing.md) — Volume VI: *Nonlinear Aggregation, Gram Kernels, and Centered Adjoint Probing*
  - [`papers/lggr_vii_projection_residuals_and_witness_composition/`](papers/lggr_vii_projection_residuals_and_witness_composition/lggr_vii_projection_residuals_and_witness_composition.md) — Volume VII: *Positive-Extension Projection Residuals, Observer-Fiber Minimax Floors, and Witnessed Composition* (with typed [claim ledger](papers/lggr_vii_projection_residuals_and_witness_composition/lggr_vii_projection_residuals_and_witness_composition_claim_ledger.md) and exact rational Python derivations/tests under `code/`).
  - [`papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/`](papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/lggr_viii_online_streaming_discovery_and_runtime_gluing.md) — Volume VIII: *Online Streaming LGGG vs. LGGR Discovery for Agentic Swarms* (with typed [claim ledger](papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/lggr_viii_online_streaming_discovery_and_runtime_gluing_claim_ledger.md), companion Python derivations/tests under `code/`, and recorded OpenRouter benchmark receipts).
- **[`lean4/`](lean4/LggrVIII.lean):** Standalone Lean 4 (`v4.35.0`) formalization package (`LGGR` / `LggrVII.lean`, `LggrVIII.lean`, `CheckAxioms.lean`) proving the realized-image decoder/collision theorems, Boolean evaluator defect partition, multi-step history telescoping and prefix vs. endpoint separation, integer $\ell^1$ triangle primal/dual optimality, observer-fiber two-point minimax lower bound, online collision monotonicity under trace extensions, prefix budget violation monotonicity, and boundary-sufficient composable LGGG certificates with zero `sorry` and standard Lean core axioms only. Build with `cd lean4 && lake build`.

## Run without installing anything

Python **3.10 or newer**; standard-library runtime only. Tested here with Python 3.13.5 on Linux; other platforms/interpreters were not executed here. No API calls, tokens, Git checkout, NumPy, Lean, solver, or GPU are required.

Unzip the source archive, enter its directory, then run:

```console
python -m lggr demo
python -m unittest discover -s tests -v
```

A separately supplied single-file archive can run directly:

```console
python lggr_witness_audit.pyz selftest
python lggr_witness_audit.pyz demo
python lggr_witness_audit.pyz --help
```

The `.pyz` contains the same library code, not a native executable or model. The source ZIP also includes JSON examples, tests, documentation and execution receipts.

Optional installation from the extracted directory:

```console
python -m pip install --no-build-isolation .
lggr-audit demo
```

Installation requires a compatible local setuptools installation. It is unnecessary for either run method above; there are no third-party runtime dependencies.

## What is implemented

| Mechanism | Executable behavior | Boundary |
|---|---|---|
| Decoder-or-collision | Groups finite observations by report, constructs a decoder on the realized image or exhibits a colliding pair, and replays either certificate. | A decoder is certified only on the supplied table. A collision certifies report insufficiency in this model, not which history occurred. |
| Streaming fiber monitor | Ingests state observations incrementally, tracks realized report fibers, and immediately detects collisions $p(x_1) = p(x_2)$ with $q(x_1) \ne q(x_2)$. | Transitions contract status from `COMPOSABLE_LGGG` to `OBSTRUCTED_LGGR` upon the first observed collision; emits `lggr.online_collision.v1`. |
| Witness composition | Checks endpoint identity, signed differences, local verdicts, smoke observations, baseline, policy manifest, evaluator/spec/representation/authority identity, and open obligations. | Its global query is the declared integer budget requirement, not arbitrary software semantics. |
| Streaming audit monitor | Evaluates $G_1$–$G_4$ conditional gluing prefix-by-prefix, tracks signed delta drift, computes evaluator defect $\Delta_E \in \{-1,0,1\}$, and enforces early stopping under `every_prefix`. | Emits `lggr.online_alert.v1` and halts execution upon prefix budget breach or local/global defect. |
| Evaluator defect | Computes `Eg - E1*E2` and labels NGD/ZDR/PGD. | Requires an independently supplied global verdict. It does not manufacture one from local passes. |
| Exact L1 certificate | Checks `D.T z = 0`, `abs(z) <= w`, the primal residual and equality of bounds. | Verifies supplied rational certificates; does not optimize an arbitrary repair problem for you. |
| Cochain classification | Exact rational elimination separates repairability, closure failure and closed/nonexact classes. | A degree-two differential must be supplied before any H1 classification. |
| Streaming cochain monitor | Ingests graph edges incrementally, maintains an active spanning forest, and detects cycle closure. | On cycle closure, computes coboundary defect $(D_1 h)_C$, solves exact rational $\ell^1$ repair distance $\Phi(h)$, and verifies dual witness $z$. |
| Witness transport | Checks commuting squares and optional chain retractions. | Forward commutation preserves repairs; it does not alone preserve nonrepairability. |
| Retained obligations | Unions unresolved obligations across every supplied witness and prior obligation list. | The host must retain the original history/ledger. This package cannot prevent deletion outside its process. |

The added schema/version checks, exact finite elimination, JSON CLI and optional every-prefix query are **implementation extensions**, not claims that these exact Python APIs or statuses already exist as native OE/QM contracts.

## Reproduce the report

```console
python -m lggr audit examples/bad_history.json
python -m lggr audit examples/good_history.json
python -m lggr audit examples/reports_only.json
python -m lggr descent examples/report_collision.json
python -m lggr descent examples/refined_reports.json
python -m lggr linear examples/triangle_l1.json
python -m lggr cochain examples/triangle_filled.json
python -m lggr cochain examples/triangle_unfilled.json
python -m lggr cochain examples/budget_exact_cochain.json
python -m lggr transport examples/faithful_transport.json
python -m lggr transport examples/lossy_transport.json
```

Some commands intentionally return exit **1**: they found a counterexample or did not establish the requested claim. That is expected, not a crash.

### Expected results

| Input | Result |
|---|---|
| `0 -> 1 -> 2` | Both local gates pass; `OBSTRUCTION_DETECTED` because cumulative change is 2 and the bound is 1. |
| `0 -> 1 -> 0` | `COMPOSITION_VERIFIED` for the declared cumulative requirement. |
| Same local reports, endpoints unavailable | `WITNESS_INCOMPLETE`; no realized global failure is inferred. |
| Restricted reports for both histories | `REPORT_INSUFFICIENT`, with an explicit equal-report/different-query pair. |
| Signed-increment refinement | `DECODER_VERIFIED` on the supplied finite carrier. |
| A changed owner/evaluator/specification or policy manifest | `AUTHORITY_REQUIRED`; no self-approval fallback. |
| An untranslated representation | `UNSUPPORTED`; no automatic reinterpretation of its values. |
| An unresolved earlier obligation | `WITNESS_INCOMPLETE`, even if the endpoint budget holds. |
| Triangle `h=(1,1,1)`, `z=(1,1,-1)` | `OPTIMALITY_VERIFIED`, with exact `Phi=1`. |
| Same triangle, filled by a face | `CLOSURE_FAILURE`, **not** an H1 class. |
| Same triangle, no degree-two cells | `CLOSED_NONEXACT`. |
| Budget differences `h=(1,1,2)` | `EXACT`; the drift example is not a cohomological obstruction. |
| Edge-permutation chain retraction | `RETRACTION_VERIFIED`; repair reflection is certified. |
| Zero/lossy map | Forward commutation holds, but reflection is not certified. |

A fixed-baseline arithmetic check detects the same budget failure. **No greater detection power than that baseline is claimed.** The extra artifacts expose the scope, report loss, transport assumptions and unresolved obligations.

## Python API

### 1. Compose witnessed transitions

```python
from lggr import BudgetPolicy, StateRef, audit_history, make_witness

policy = BudgetPolicy()
s0 = StateRef("commit-0", 0)
s1 = StateRef("commit-1", 1)
s2 = StateRef("commit-2", 2)

w01 = make_witness(policy, s0, s1, witness_id="review-01")
w12 = make_witness(policy, s1, s2, witness_id="review-12")
receipt = audit_history(policy, s0, [w01, w12])

print(receipt["status"])                         # OBSTRUCTION_DETECTED
print(receipt["arithmetic"]["signed_total"])     # 2
print(receipt["arithmetic"]["global_verdict"])   # False
print(receipt["authority_effect"])               # None (the string)
```

`make_witness` evaluates the supplied finite model. It does not turn arbitrary code, an LLM's approval, or a commit hash into behavioral evidence.

`policy.sha256` binds the actual policy contents, not just its name. Each witness records this manifest digest and the evaluator, specification, representation and authority identities. These are **supplied identities**, not authentication or a certification that a hosted provider has remained unchanged.

The audit recomputes local verdicts instead of trusting the recorded flags. It rejects disconnected boundaries and conflicting observations for one state identity. All findings remain in the receipt even when a more conservative primary status takes precedence.

### Endpoint scope versus every-prefix scope

The source report's query is `abs(final - baseline) <= bound`. That is the default `query_scope="endpoint"`.

Under this query, `0 -> 1 -> 2 -> 1` has a valid final endpoint despite an earlier violation. The receipt exposes both the endpoint and every-prefix answers; it does not pretend they are the same proposition.

`StreamingAuditMonitor.step()` records these excursions in `g4_prefix_ok` without
raising an endpoint-budget alert. `get_receipt()` evaluates the supplied trace's
final endpoint and rejects any breach still present there. An empty audit stream
without an observed baseline remains `WITNESS_INCOMPLETE` (CLI exit code 1).

For a requirement that must hold after **every** accepted update, explicitly use:

```python
policy = BudgetPolicy(query_scope="every_prefix")
```

That policy rejects the excursion even after a return within bounds. Its different manifest must not be silently substituted into existing witnesses. Retain earlier decisions and obligations in protected storage.

### 2. Audit whether reports retain enough information

```python
from lggr import analyze_descent, verify_descent_certificate

rows = [
    {"state_id": "0,1,0", "report": [[1, True, True], [1, True, True]], "query": True},
    {"state_id": "0,1,2", "report": [[1, True, True], [1, True, True]], "query": False},
]
certificate = analyze_descent(rows, scope_id="two-explicit-budget-histories")
print(certificate["status"])  # REPORT_INSUFFICIENT
print(verify_descent_certificate(rows, certificate))  # True
```

To certify a finite carrier exhaustively, **you must supply the full declared carrier**. Passing a sample does not establish adequacy on unseen histories. A collision within a sample nevertheless refutes sufficiency for any larger declared carrier containing that pair under the same report and query maps.

Reports and query values use canonical JSON equality. In particular, JSON `true`, integer `1`, and string `"1"` remain distinct. Object key order is irrelevant. Repeated state IDs, unknown schema fields and floats are rejected.

`decode(certificate, report)` is a lookup convenience for a previously verified certificate. It raises `KeyError` outside the certified realized image; it never extrapolates. Replay an untrusted certificate against its source table before using it.

### 3. Verify a genuine nonrepairability certificate

```python
from lggr import verify_l1_certificate

receipt = verify_l1_certificate(
    D=[[-1, 1, 0], [0, -1, 1], [-1, 0, 1]],
    h=[1, 1, 1],
    weights=[1, 1, 1],
    potential=[0, 1, 2],
    dual=[1, 1, -1],
)
print(receipt["status"])             # OPTIMALITY_VERIFIED
print(receipt["optimum"])            # "1", an exact rational string
print(receipt["repair_impossible"])  # True
```

Acceptable coefficients are integers, rational strings such as `"1/3"`, or Python `Fraction` objects. No tolerance or approximate equality is used. The routines support nonempty finite rational repair matrices with positive weights. `classify_cochain(..., D1=[])` explicitly declares a zero-dimensional degree-two space; omitting `D1` makes no cohomology claim.

### 4. Check transport before reusing an obstruction

`verify_transport` accepts `D_source`, `D_target`, `F0`, `F1`, and optionally `G0`, `G1`.

It checks:

```text
F1 D_source = D_target F0          forward repair transport
G1 D_target = D_source G0          backward repair transport
G0 F0 = identity on source C0     left inverse
G1 F1 = identity on source C1     left inverse
```

The full verified chain retraction is a sufficient repair-reflection certificate. Failure to provide one does not show in this model that every conceivable reflection method fails. It means this checker has not certified reflection by this route.

This finite rational check is **not automatically connected to runtime representation migration** in the budget adapter. That connection needs an independently admitted interpretation of the maps and states. The adapter refuses unprovided transport instead of assuming it.

### 5. Online Streaming Monitors (`lggr.streaming`)

The following examples show five of the streaming monitors for verification during live agent execution:

```python
from lggr.streaming import (
    StreamingAuditMonitor,
    StreamingCochainMonitor,
    StreamingFiberMonitor,
    StreamingPositiveExtensionMonitor,
    StreamingTransportMonitor,
)
from lggr.witnesses import BudgetPolicy, StateRef, make_witness

# 1. Incremental fiber collision detection and concurrent branch merging
fiber_mon = StreamingFiberMonitor(scope_id="pipeline-scope")
fiber_mon.observe("state_1", report={"role": "worker"}, query={"tier": 1})
collision_receipt = fiber_mon.observe("state_2", report={"role": "worker"}, query={"tier": 2})
# Detects collision on-the-fly and transitions contract_status to "OBSTRUCTED_LGGR"

# 2. Prefix budget, evaluator defect tracking, and cross-stage witness splicing (.merge)
policy = BudgetPolicy(max_step=1, max_total=2, query_scope="every_prefix")
s0 = StateRef("s0", 0)
audit_mon = StreamingAuditMonitor(policy, s0)
w1 = make_witness(policy, s0, StateRef("s1", 1), witness_id="w1")
audit_mon.step(w1, global_evaluator_sample=1)

# 3. Incremental 1-cochain cycle closure, 2-cell cohomology, and global Edmonds-Karp L1 repair
cochain_mon = StreamingCochainMonitor()
cochain_mon.add_edge("Agent_A", "Agent_B", value=1, weight=1)
cochain_mon.add_edge("Agent_B", "Agent_C", value=1, weight=1)
cycle_receipt = cochain_mon.add_edge("Agent_C", "Agent_A", value=1, weight=1)
global_l1 = cochain_mon.solve_global_l1_repair()

# 4. Online chain-retraction synthesis vs. lossy coarse-graining projection audit
# StreamingTransportMonitor(src_mon, tgt_mon).synthesize_chain_retraction(F0, F1)

# 5. Online observer-fiber minimax error floor and CF vs. N_min order-reversal audit
minimax_mon = StreamingPositiveExtensionMonitor()
minimax_mon.observe_target("s1", report={"tag": "ok"}, target_value=2)
minimax_mon.observe_target("s2", report={"tag": "ok"}, target_value=6)
```

### Two-step optional-stopping receipts

`StreamingMartingaleOptionalStoppingMonitor` checks exact rational binary trees
and all four choices of stopping or continuing on the two first-step branches.
Its receipt separates four questions:

| Field | Meaning |
|---|---|
| `optional_stopping_theorem_applicable` | All three conditional martingale equations hold. |
| `optional_stopping_conservation_verified` | The computed stopped and full-horizon expectations both equal the initial value. Accidental equality can hold even when the martingale premise fails. |
| `global_drawdown_evaluator` | The worst stopped terminal loss from the initial value is within the declared budget, independently of martingale validity. |
| `joint_admission_evaluator` | Both the local martingale checks and the global loss-budget check pass. |

The corresponding aggregate applicability and conservation fields are separate
in `get_receipt()`. A non-martingale is still rejected by the overall contract,
even if its global loss-budget verdict is green (`evaluator_defect = +1`).

The legacy field `tail_drawdown` means
`max(0, x0 - min(stopped terminal values))`; it does not bound peak-to-trough
losses along a path. For example, the fair martingale
`0 -> (10, -10) -> (30, -10, -10, -10)`, continued on both branches, has
`tail_drawdown = 10` and passes budget 15, although one path falls 20 from its peak.

[Theorem 49](lean4/LggrVIII.lean) formalizes two fair-tree sum identities
(full horizon and stop-on-up/continue-on-down) and one fixed loss-budget example
over integers. Its proposition does not count the `3/4` win probability or cover
arbitrary rational probabilities and all four Python stopping rules. Those are
finite exact-arithmetic computations tested by the Python suite; the Lean result
is a finite instance of established optional-stopping mathematics.

## Practitioner Cookbooks (`cookbooks/`)

Four standalone, zero-dependency runnable scripts in `cookbooks/` illustrate real-world practitioner patterns:

```console
# 1. Two-agent handoff with online report-fiber collision detection
python cookbooks/01_online_fiber_monitoring.py

# 2. Multi-step tool action trajectory with every_prefix budget early stopping
python cookbooks/02_streaming_budget_audit.py

# 3. 3-agent circular review loop with exact rational L1 repair distance and dual witness
python cookbooks/03_cochain_cycle_repair.py

# 4. Multi-stage swarm runtime guard certifying composable LGGG (Delta_E = 0)
python cookbooks/04_swarm_runtime_guard.py
```

## Replay, receipts and exit codes

```console
python -m lggr audit examples/bad_history.json --output receipts/bad.json
python -m lggr replay examples/bad_history.json receipts/bad.json

python -m lggr descent examples/report_collision.json --output receipts/collision.json
python -m lggr replay examples/report_collision.json receipts/collision.json
```

A negative receipt can replay successfully. **Exit 0 from `replay` means the certificate was verified, not that its negative finding became an admission.** The full audit input is recomputed; a receipt hash alone is not accepted as proof.

| Command | Exit 0 means |
|---|---|
| `selftest` | All internal self-tests passed cleanly across descent, linear, cochain, transport, witnesses, and streaming. |
| `stream` | Online streaming event trace verified under declared monitor; inspect status for `COMPOSABLE_LGGG` vs. `OBSTRUCTED_LGGR`. |
| `demo` | The demonstration and exhaustive finite census completed. Expected counterexamples are included. |
| `audit` | `COMPOSITION_VERIFIED` for the declared query and supplied evidence. No merge grant. |
| `descent` | A decoder exists on the supplied finite table. |
| `linear` | A supplied lower-bound or matching-optimum certificate verified; inspect `status`. |
| `cochain` | An exact repair exists in the supplied rational model. |
| `transport` | Forward transport verified, and reflection too when `require_reflection` is true. |
| `replay` | The receipt's mathematical check replays against the supplied input, including valid negative findings. |

Exit **1** means a negative or uncertified result. Exit **2** means malformed input, unsupported CLI usage, or an input/output error. JSON errors go to stderr. Unexpected internal implementation errors are not converted into successful results.

`--output` writes a JSON receipt. Input `-` reads JSON from stdin. Verification does not depend on Python `assert`, so `python -O` does not remove the checks.

## Host integration boundary

A host should read the policy, baseline and retained obligations from protected accepted state; obtain candidate evidence from a separate execution/replay mechanism; then call this checker. Do not read the governing policy from a worker-controlled branch and assume its digest makes it trustworthy.

For the audit command, only exit 0 is a candidate **certificate success**. The owner's external admission rule still decides whether any change may merge. Do not treat successful CLI execution, a verified collision, a positive L1 obstruction, or successful receipt replay as permission to merge.

The current package deliberately has no `approve=True`, owner-signature bypass, mutable reviewer, obligation-clearing endpoint, GitHub write action, or autonomous gate-installation feature. It is a verification library and experiment, not a production security boundary. Untrusted JSON still requires normal host resource limits and sandboxing.

## Validation and source custody

`receipts/tests.txt` records the actual unit-test run. `receipts/validation.json` records execution details and limitations. The tests include the 216 finite report/query combinations, all eight Boolean verdict triples, all 363 histories of length one through five over the three-state domain, independent certificate replay, tampering and scope-change cases, exact arithmetic, and CLI exit behavior.

`SOURCE_NOTES.md` separates the uploaded report from this new implementation. `source/research_response.txt` preserves the supplied input. `provenance.json` records its SHA-256 and the repository pins **reported by that input**. Those repositories and Lean proofs were not independently fetched or rerun for this implementation.

The produced status names are adapter vocabulary. NGD/ZDR/PGD reproduce the report's mathematical sign convention; the original `epk_core.py` was not imported. There is no claim of native integration, general self-modification safety, quantum advantage, or stronger detection than a complete fixed-invariant checker.

## Claim Hygiene Summary

1. **What this repository supports:**
   - Exact finite verification of report-fiber sufficiency (`DECODER_VERIFIED` vs. `REPORT_INSUFFICIENT`) via realized-image decoder construction or explicit colliding-pair certificates on supplied tables.
   - Exact endpoint and prefix composition checks for witnessed integer-budget transitions under declared policy manifests, evaluator/specification/representation/authority identities, and retained obligations.
   - Exact rational verification of weighted $\ell^1$ primal/dual repair certificates (`verify_l1_certificate`), 1-cochain repair/closure/nonexactness classification (`classify_cochain`), and commuting chain-map / left-inverse chain-retraction transport (`verify_transport`).
2. **What this repository does not support:**
   - Automatic extraction of mathematical transition models from arbitrary source code, LLM outputs, or commit hashes.
   - Stronger detection power on the cumulative budget-drift example than an ordinary fixed-baseline invariant check given the same endpoint inputs.
   - Any identification of software evaluation drift with physical Bell nonlocality or quantum contextuality, or any claim that the cumulative budget violation is a nonzero cohomology class.
   - Cryptographic authentication of identities, prevention of out-of-band ledger deletion, or operational merge authorization (`AuthorityEffect: None`).
3. **Narrowest defensible claim:**
   - For an explicitly supplied finite carrier, report map, and target query (or rational repair matrix and cochain), this reference package checks whether the retained reports determine the target on the realized image, whether supplied step witnesses compose under a declared integer budget policy, and whether supplied rational primal/dual and chain-retraction certificates satisfy the algebraic conditions required to bound or reflect repair residuals.
4. **Next test needed:**
   - Controlled equal-information comparative evaluation against a conventional contract/baseline regression checker across multi-step histories that include representation migrations (with commuting and lossy maps) and deferred obligations, measuring false acceptance, false refusal, retained obligations, certificate replay cost, and fault-localization effort.

Support this research: [Buy Me a Coffee](https://buymeacoffee.com/ooutwire).

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


### Reviewed laboratory and benchmark evidence

The [swarm laboratory review revision](experiments/grok_swarm_lab/current/README.md) ships runnable offline source and regression evidence. The [original v1 archive](experiments/grok_swarm_lab/dist/lggr-swarm-lab-2026-10-24.zip) remains unchanged. v2 requires known scoped auxiliary evidence before admission and replays deterministic labels and counters. Its rerun uses already published fixtures; it is not a new held-out experiment.

`lggr.benchmarks.verify_frontier_benchmark(receipt)` checks the outer and monitor receipt hashes, regenerates inputs from the saved model responses, checks the prompts, and compares complete traces and metrics. The original 50-trace artifact remains unchanged and is covered by `MANIFEST.sha256`. New live runs reject malformed output explicitly and honor an explicitly requested model over environment defaults. Recorded model names identify client configuration, not independent authentication of the provider.

The frontier prompts often supply exact answers or impose incompatible requirements. The published 24/50 NGD count describes that selected fixture mixture, not a general swarm failure rate or an advantage over conventional checking. Theorem 54 proves an integer positivity statement and a fixed collapse example; the Python monitor's general rational, arbitrary-expert support calculation is not formalized by that theorem.

[Historical RSI research records](papers/012_rsi/research/) and all seven research links in the RSI index have been restored from commit `103daa366d4cd9ef06fc0def10edee497f547d8e`. Their [restoration receipt](receipts/pr51_research_restoration.json) binds the original Git bytes without upgrading their historical verification claims.
