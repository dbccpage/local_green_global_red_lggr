# Change log — Local Green, Global Red (Part V)

Paper: `lggr_v_local_green_global_red` (formerly `002_projection_obstruction/029_local_green_global_red`)
Series: `001_finite_obstruction_calculus/001_local_green_global_red_foundational_series/lggr_v_local_green_global_red`
Canonical version: 1.3.2 · Date: 2026-10-15
Scope: This log records version history and package modifications.

Entries are newest-last.

## v0.1 (2026-08-31) — first deposit

* **Extraction provenance.** This deposit is a plain-language,
  self-contained extraction of §7.4 of the anchor paper *Projection
  Obstruction for Factorized States* (anchor version v6.3). Theorem 6 and
  the irreparability remark are new at anchor v6.3.
* **Version renumbering recorded.** The pre-deposit repository draft
  carried "Note (v1.0)" in its front matter. The deposit lineage starts at
  **v0.1 Pre-Print** by author directive. No claim content changed by the
  renumbering; it is recorded here rather than silently applied.
* **Deposit-language pass.** "In this repository" phrasing replaced with
  deposit-relative paths (§6 now points at `lean4/` and
  `lean4/PROVENANCE.md`). The anchor citation moved to its Zenodo concept
  DOI (10.5281/zenodo.18896776) with an honest version caveat: the
  anchor's published record is v6.1, so the Lean module for this note is
  snapshotted here rather than cited. The §5 "forced" bullet now carries
  the anchor DOI. The axiom set is named explicitly (`propext`,
  `Classical.choice`, `Quot.sound`) instead of "Lean's three standard
  axioms" alone. A non-authority scope line was added to the paper's
  front matter (previously only the directory README carried one).
* **Inline §6 replay converted** from numpy floats to pure-standard-library
  exact integer arithmetic, matching `code/` (whose canonical replays use
  `fractions.Fraction` throughout).
* **License decision recorded.** The entire deposit is CC-BY-4.0, code
  included. The anchor exemplar dual-licenses its code Apache-2.0; this
  deposit deliberately does not — one license for everything.
* **Packaging deviations from the packaging plan, recorded.** (1) The
  verification script is named `verify_deposit.py`, not the plan's
  `verify.py`, per the packaging directive's explicit file name. (2) In
  the compile receipt inside `lean4/PROVENANCE.md`, the packaging
  machine's absolute path prefix is abbreviated to `<PATH>` (stated there);
  the warning positions and all fourteen axiom-report lines are verbatim.
  (3) In an earlier internal layout, `code/tests/` shipped without an
  `__init__.py` (this was later flattened to `code/test_lgr_replay.py`):
  `unittest` discovery does not need one on the supported Python versions
  (>= 3.10), and the test file inserts `code/` onto `sys.path` itself.

## v0.1 (2026-08-31, second pass) — the hybrid union, reconciled honestly

This directory turned out to be a **hybrid of two parallel builds by two
different automations**, and a verified code review (findings F1, F3, F4)
caught the seams. Build (a), made directly on the mainline: a full
computational package — `code/code_core.py` and its five sibling modules,
`code/test_*.py` and `code/run_tests.py` (49 tests, 100% coverage gate),
`docs/` (`claim_ir.yaml`, `descriptions.md`, `lean_claim_map.md`,
`quick_start.md`), `lean4/observer_visibility.lean` (the stronger
mechanization: vector no-recovery, master soundness criterion, non-linear
evaluation bounds, Minkowski chains), `manifest.json` files, and a public
zip. Build (b), layered on top: the self-contained Zenodo deposit — the
note, `code/lgr_replay.py` + `code/test_lgr_replay.py` (originally staged
under `code/tests/test_lgr_replay.py` in an earlier internal layout),
`verify_deposit.py`, `SHA256SUMS`, `.zenodo.json`, `lean4/PROVENANCE.md` +
the anchor snapshot `lean4/po000_l004_observer_visibility.lean`. Neither
build saw the other's files, so each document described only its own half.
Credit to both: build (a) contributed the stronger Lean results, harness,
and documentation (whose claims and declaration maps were consolidated into
`README.md`, `local_green_global_red_claim_ledger.md`, `manifest.json`, and
`.zenodo.json`); build (b) contributed the deposit discipline (manifest,
verifier, provenance receipts). This pass unions them honestly rather than
purging either:

* **Second Lean source adjudicated, kept first-class (F3).**
  `lean4/observer_visibility.lean` was compiled on 2026-08-31 against the
  pinned toolchain: exit 0, 43 `#print axioms` reports, all within
  `{propext, Classical.choice, Quot.sound}`, no `sorry`, and it contains
  every declaration `docs/claim_ir.yaml` names (including
  `vector_no_recovery_modulus`, `master_soundness_iff`, and the five
  `NonlinearEvaluation.*` theorems). The MECHANIZED rows in
  `claim_ir.yaml` therefore stand. `lean4/README.md` and
  `lean4/PROVENANCE.md` now describe BOTH files accurately (snapshot vs.
  this deposit's own mechanization), with the new compile receipt in
  PROVENANCE Part 2.
* **Joint-scores claim restored to full mechanized strength (F4).** The
  note's §3 Theorem 4 now states both the max form and the joint
  (score-vector) form, and §6 cites
  `ObserverVisibility.ThreePatch.vector_no_recovery_modulus` for the joint
  form — which is proved in the deposit's own Lean file only. The §6 map
  now cites the deposit's own file throughout (unprefixed namespace); the
  snapshot carries the same core declarations under the `PO000.` prefix,
  as §6's preamble and the claim ledger's Lean-bindings note say. Without
  the second file, the "no function of the evaluators' scores, jointly"
  prose was backed only by the scalar `no_recovery_modulus`.
* **SHA256SUMS rebuilt over the union (F1).** The manifest previously
  listed only build (b)'s 12 files while build (a)'s files shipped
  alongside, so `verify_deposit.py`'s own "nothing unlisted" sweep failed
  with 23 FAIL lines at head. It now covers every shipped file, and
  `python verify_deposit.py` passes on this exact tree.
* **Duplicate metadata reconciled.** One canonical `manifest.json` at the
  deposit root (build (a)'s `lean4/manifest.json`, a partial 15-theorem
  inventory, was absorbed into it and deleted; the dead `lean_home`
  pointer to a nonexistent tree was dropped).
  One canonical `pyproject.toml` at the root (`code/pyproject.toml` from
  an earlier internal layout was absorbed — its numpy/scipy dependencies
  survive as the optional `harness` extra — and deleted). Both
  absorptions are noted in the surviving files.
* **Stale public zip deleted.** `local_green_global_red_20260831_public.zip`
  was extracted and inspected: it contained build (a) only (no
  `lgr_replay.py`, no `verify_deposit.py`, no `SHA256SUMS`, no anchor
  snapshot, plus `.coverage`/`.pytest_cache` noise, and README/note bytes
  differing from the shipped ones), so it contradicted the unioned tree it
  sat in. Deleted for the same reason the author approved deleting the
  anchor's stale zip; a future release build can regenerate a faithful one.
* **Counts corrected in prose.** `docs/quick_start.md` said "35 tests" and
  "17 declarations"; the shipped counts are 49 tests and 22 named
  declarations (43 axiom reports). `lean4/README.md` said "All 14
  declarations" while naming `observer_visibility.lean` as source —
  corrected to the per-file counts. Corrections are recorded in place, not
  silently.
* **Both suites re-run green after the union:** `python verify_deposit.py`
  (manifest + 11 replay tests) and `python code/run_tests.py` (49 tests,
  100% coverage).

## v0.1 (2026-09-06) — pre-deposit review remediation

* **Theorem 3 site count and realization corrected.** Replaced the three-site
  phrasing with the implemented six-site construction: three component sites
  $u_0, u_1, u_2$ and three overlap sites $x_{01}, x_{12}, x_{20}$ (six sites
  total) with six directed interfaces, state spaces $\mathbb R^3$ ($\ell^1$ norm),
  identity translations, and section assignment $s_R(u_i) = \lambda e_i$,
  $s_R(x_{ij}) = 0$, with scale $\lambda = R/6$. Documented the mathematical rationale:
  on a literal bidirected 3-site triangle, opposite defects are negatives and
  cancel, forcing them to vanish when constrained to coordinate axes.
* **Lean mechanization claim tightened.** Clarified that
  `scaledDefect_is_section_defect` formalizes the per-edge algebraic identity
  $v = v - 0$ witnessing section realizability, without encoding the six sites
  or incidence boundary maps in Lean.
* **Irreparability remark distinguished.** Introduced the quotient projection
  functional $\Phi(\omega) = \inf_t \|\omega - Dt\|_1$. Contrasted
  $\omega = (1, -1) \notin \operatorname{im} D$ (where $\Phi(\omega) = 2 > 0$) with
  valid section defects $\Delta(s) \in \operatorname{im} D$ (where $\Phi(\Delta(s)) = 0$).
  Anchored against PO-000 §7.4.12 (`projection_obstruction.md#L1182`).
* **Headline claims qualified.** Specified finite-valued functions in Theorem 4.
  The accompanying assertion that metric rescaling escapes the bound was
  incorrect and is withdrawn by the merge review below.
  Stated the contractivity bound $I(s) \le 2B|E|$ for $\|s(x)\| \le B$.
  Replaced "smallest mathematical model" with "a small mathematical model" (two
  sites with one interface and $q(x, y) = y$ suffices). Softened "never means no
  defect" to "does not, without further assumptions, imply no defect".
* **Exact soundness criterion included.** Added $\operatorname{im} D \cap \prod_e K_e = \{0\}$
  connecting Theorem 5 and Theorem 6, referencing `master_soundness_iff`.
* **Reproducible Lean build.** Added `lean4/lakefile.lean` and `lean4/lean-toolchain`
  pinning `leanprover/lean4:v4.34.0-rc1` and Mathlib; documented Lake build in
  `docs/quick_start.md`.
* **Numerical certificate hardening.** Added upfront finiteness validation
  (`np.all(np.isfinite(...))`) in `code/code_quotient_solver.py` to prevent
  `NaN`/`inf` bypasses, with regression tests in `code/test_quotient_solver.py`
  (harness test count increased to 50, 100% coverage maintained).
* **Metadata & title synchronization.** Synchronized title to "Local Green,
  Global Red: A Finite No-Recovery Theorem for Composed Evaluation, with Lean 4
  Proofs" across `manifest.json`, `README.md`, `pyproject.toml`, and `.zenodo.json`.
  Updated deposit description in `.zenodo.json` and manuscript abstract to match
  `docs/descriptions.md`. Updated Section 7 anchor citation to version v6.3.
* **Readable PDF generated.** Generated `local_green_global_red.pdf` via Pandoc.
* **SHA256SUMS rebuilt:** Re-hashed all deposit files so `python verify_deposit.py`
  was intended to pass on a fresh unpack. The merge review found that this
  claim was false: the manifest named a missing coverage cache and the wrong
  Lake configuration bytes.

## v0.1 (2026-09-06) — exact-head merge review corrections

* Removed the unshipped coverage-cache manifest entry and corrected the Lake
  configuration hash. Neither proof source is changed.
* Withdrew the six-site minimality heading and the metric-rescaling escape
  claim. The no-recovery theorem excludes finite bounds, not `+∞`.
* Restored `hnorm_zero` to the Master Soundness Criterion's stated scope.
  The displayed set equality also uses that the realizable set contains zero.
* Distinguished exactness from zero distance to a possibly nonclosed image.
  The explicit finite-dimensional coupled example is unchanged.
* Replayed the 11 exact tests and the 50-test computational harness; the latter
  reached its declared 100% statement-coverage threshold with eight workers.

## v0.1 (2026-09-08, internal review pass 1) — code review remediation

* **F1: Corrected numerical certification in quotient solver.**
  Resolved false non-zero distance on ill-conditioned systems (such as
  $D = [10^{-10}], \omega = [1.0]$, where the true quotient distance is zero):
  * Added pre-equilibration scaling of columns before LP/QP optimization.
  * Implemented exact projection of the dual witness onto $\ker(D^T)$ via
    QR decomposition with nullspace projection.
  * Hardened certificate verification: replaced absolute column defect with
    relative column orthogonality $\lvert D_{:, j}^T W\rvert / \lVert D_{:, j}\rVert_2 \le \text{tol}$.
  * Deprecated `is_exact_certified` in favor of `is_numerically_certified`.
  * Added adversarial rejections in `code/test_quotient_solver.py` covering
    non-finite values, corrupted residuals, non-contractive witnesses, and
    gap tampering.
* **F2: Qualified mechanization scope across documents.**
  Clarified in front matter, §1, §6, and `local_green_global_red_claim_ledger.md`
  that Lean 4 proofs cover abstract observer theorems and per-edge defect
  calculations, while the six-site graph incidence diagram is established in
  prose and verified by exact integer arithmetic in `code/lgr_replay.py`.
  Classified row LGR-T3 as `PROVEN-MECHANIZED (Edge) + PROSE-REALIZED (Graph)`.
* **F3: Stated missing nontrivial fiber hypothesis in ledger.**
  Updated LGR-T5 to include the explicit nonzero vector hypothesis ($v \ne 0$)
  required by `ObserverVisibility.coverage_of_jointTrivial`. An unwatched
  zero-dimensional fiber ($F(e) = \{0\}$) trivially has zero defect without
  having any watcher.
* **F4: Harmonized theorem 2 tolerance propagation.**
  Updated `check_theorem_2_characterization` in `code/code_theorems.py` to
  propagate the `tol` parameter uniformly to both `system.is_all_green` and
  `is_in_blind_spot`. Added regression test.
* **F5: Enforced evaluator and system structural invariants.**
  * Added `Evaluator.__post_init__` enforcing uniqueness of `watched_interfaces`
    (raising `ValueError` on duplicate interfaces) and validating matrix finiteness.
  * Enforced dimension compatibility between interfaces and evaluators in
    `System.add_interface` and `System.add_evaluator`.
  * Added comprehensive validation tests in `code/test_core.py`.
* **F6: Hardened CLI failure announcement and exit codes.**
  Updated `code/code_cli.py`: `main()` aggregates all check results, returns
  exit code 1 and logs failing checks on any failure, and returns exit code 0
  with confirmation only when all checks pass. Added CLI error path test in
  `code/test_cli.py`.
* **Editorial, theoretical, and test suite improvements:**
  * Renamed §4 remark heading to "Raw inconsistency and irreparable quotient defect."
  * Explicitly listed all six directed interfaces in §3 Theorem 3:
    $e_{01}^0 = (x_{01}, u_0)$, $e_{01}^1 = (x_{01}, u_1)$, $e_{12}^1 = (x_{12}, u_1)$,
    $e_{12}^2 = (x_{12}, u_2)$, $e_{20}^2 = (x_{20}, u_2)$, and $e_{20}^0 = (x_{20}, u_0)$.
  * Harmonized evaluator indices across text and theorems to $\{0, 1, 2\}$.
  * Provided explicit proofs for Theorem 4 (no recovery modulus) and Theorem 6
    (coupled witness sufficiency without necessity).
  * Added remark on quantitative soundness bounds on finite-dimensional spaces
    via unit sphere compactness: $I(s) \le C \max_\alpha J^\alpha(s)$.
  * Rephrased §4 category distinction prose to eliminate forbidden rhetoric.
  * Relabeled nonlinear manifold perturbation test in `code/test_quotient_solver.py`
    as transverse perturbation $p(\alpha) = [\sin(\alpha), 0]^T$ with exact
    $L_1$ bound $\le \epsilon$.
  * Re-established 100% statement coverage across all 6 computational modules
    (54 passed, 47 subtests passed, 584 statements, 0 missing).
  * Synchronized `manifest.json`, `SHA256SUMS`, and recompiled PDF via Pandoc.

## v0.1 (2026-09-09, internal review pass 2) — computational supplement remediation

* **Theorem 6 replacement proof (site state correction):**
  * Corrected the interface defect derivation in the proof of Theorem 6 (`local_green_global_red.md`). Under zero translation maps $r_{e_0} = r_{e_1} = 0$, the interface defect is $\Delta(s)_{e_i} = r_{e_i} s(a_i) - s(b) = -s(b)$, which evaluates identically to $-s(b)$ on both interfaces $e_0$ and $e_1$, independent of the site states $s(a_0), s(a_1)$.
  * Replaced the proof text with the direct single-site evaluation proof, recompiled PDF via Pandoc/xelatex, and confirmed Lean mechanized parity in `ObserverVisibility.Coupled.allGreen_forces_zero`.
* **Requested tolerance certification & exact recovery:**
  * Fixed quotient solver numerical certification in `code/code_quotient_solver.py`: `is_numerically_certified` now requires the duality gap to satisfy `gap <= tol` (the caller-requested tolerance) rather than a hardcoded $10^{-5}$ threshold, and requires the dual certificate norm to satisfy $\lVert W\rVert \le 1.0 + \text{tol}$.
  * For ill-conditioned systems where requested tolerance exceeds machine floating-point precision (e.g., $D = [[1, 1], [0, 10^{-13}]], \omega = [0, 10^{-6}], \text{tol} = 10^{-12}$), the numerical solver appropriately reports `is_numerically_certified = False` and non-zero residual.
  * Verified that exact rational elimination via `solve_exact_repair` resolves the true quotient distance as exactly zero with exact rational repair $\alpha = (-10^7, 10^7)$.
* **SVD numerical rank cutoff on redundant columns:**
  * Replaced strict positivity threshold `S > 0.0` in `_project_dual_witness` and `verify_certificate` with standard NumPy floating-point cutoff `S[0] * max(m, n) * eps`.
  * Prevents machine roundoff singular values (e.g. $3.35 \times 10^{-17}$) on redundant/collinear columns ($D_2 = [[1, 1], [1, 1]]$ vs $D_1 = [[1], [1]]$) from being classified as full row rank, ensuring dual witness certification parity.
* **Theorem 2 & 5 operator theoretical bounds diagnostics:**
  * In `code/code_theorems.py`, updated `diagnose_theorem_2` to test consistency against operator theoretical bounds rather than unscaled pointwise thresholds, correctly handling anisotropic contractive measurements (e.g., $Q = \operatorname{diag}(0.1, 1)$ with defect $(0, 5\times 10^{-8})$) and multi-interface aggregation (summed evaluator scores).
  * Added `compute_recovery_constant` and updated `check_theorem_5_sufficiency` to verify quantitative recovery bound $I(s) \le C \max_\alpha J^\alpha(s) + \text{tol}$ for approximate green assignments.
* **Metadata and manifest reconciliation:**
  * Synchronized version labels across deposit files.
  * Recomputed SHA-256 digests in `SHA256SUMS`.

## v0.1 (2026-09-09, internal review pass 3) — layout, provenance, notation, and proof additions

* **Margin and text overflow remediation:**
  * Replaced the wide two-column declaration table in §6 with a clean full-width markdown list grouped by result and subnamespace.
  * Replaced the inline Python code block in §6 with the unit-scale formula $I(s_1)=6, (J^0(s_1), J^1(s_1), J^2(s_1))=(0,0,0)$ and explicit reference to `code/lgr_replay.py`.
  * Preserved §4 heading together with the Soundness Criterion displayed equation on Page 5 via clean page break.
* **Anchor provenance and DOI synchronization:**
  * Updated §7 to cite the published Zenodo release v6.3 Pre-Print (issued 2026-09-04, version DOI [10.5281/zenodo.22289548](https://doi.org/10.5281/zenodo.22289548) [1], concept family DOI 10.5281/zenodo.18896776).
  * Excised dead/moving GitHub line links and updated §5 additive-diagnostic bullet to cite [1].
  * Added formal `## References` section citing Carroll (2026) [1] and Boyd (2008) [2].
* **Explicit index sets, assignment/defect spaces, and cochain norms:**
  * Defined finite index sets $X, E, A$ in §1 while establishing that state spaces $F(x)$ are real normed vector spaces.
  * Explicitly defined assignment space $C^0 := \prod_{x\in X} F(x)$, defect space $C^1 := \prod_{e\in E} F(a(e))$, linear defect operator $(Ds)_e = r_e s(b(e)) - s(a(e))$, sum norm $\lVert\omega\rVert_{1,E}$, and quotient distance functional $\Phi(\omega) := \inf_{t\in C^0} \lVert\omega - Dt\rVert_{1,E}$.
* **Self-contained mathematical justifications:**
  * Added short proof for Theorem 2 (All-Green characterization via normed kernel vanishing).
  * Added short proof for Master Soundness Criterion ($\operatorname{im} D \cap K = \{0\}$).
  * Added finite-dimensional quantitative recovery proof via unit sphere compactness ($C = 1/m$).
  * Added elementary lower bound derivation $|1+\alpha| + |\alpha-1| \ge 2$ for the quotient distance remark.
  * Connected soundness null-space injectivity to standard linear observability (Boyd EE263 [2]).
* **Editorial sharpening and scope clarification:**
  * Clarified §6 formalization boundaries for Theorem 3, removing unreferenced Minkowski/nonlinear discussion from prose.
  * Excised historical review/retraction language from §3 and §4, sharpening non-independence scope of overlap sites and bounded family constraints ($I(s) \le 2B|E|$).
  * Replaced "What this note shows, in one paragraph" with the concise "Why this matters" section; separated metadata lines in front matter.
* **Verification and rendering:**
  * Verified all 9 rendered pages in `local_green_global_red.pdf` for margin conformance and visual integrity.

## v0.1 Pre-Print (2026-09-09, release candidate) — first-publication readiness, declaration list rendering, and verifier hardening

* **Consistent publication release version (v0.1 Pre-Print):**
  * Set manuscript YAML to `version: "v0.1"` and visible status line to `**Status:** v0.1 Pre-Print · **License:** CC-BY-4.0`.
  * Set `local_green_global_red_claim_ledger.md` identity to `Canonical version: v0.1 Pre-Print (2026-09-09)`.
  * Set `README.md` title and table entries to `v0.1 Pre-Print`.
  * Set `manifest.json` version to `"v0.1"`, `.zenodo.json` version to `"0.1"`, and `pyproject.toml` version to `"0.1.0"` with description `(v0.1 Pre-Print)`.
  * Clarified throughout that this paper has never been published before; all preceding change log entries represent internal pre-publication drafts, reviews, and remediation passes.
* **Declaration list layout repaired (§6):**
  * Added blank lines between bold headings and declaration bullet lists in §6 to ensure standard Markdown parsing into LaTeX bullet lists in Pandoc/XeLaTeX.
  * Changed opening sentence from "The table below maps..." to "The declaration list below maps...".
  * Verified that page 8 declarations render entirely within text margins without horizontal overflow.
* **Narrowed six-site graph realization claim:**
  * Replaced §6 sentence and ledger row LGR-T3 scope with: "For Theorem 3, the Lean declarations cover the edge-level defect calculations described below. The six-site graph realization follows from the explicit assignment and calculation in §3. The exact Python replay checks the resulting edge-cochain arithmetic; it does not independently reconstruct the graph incidence operator."
* **Quotient solver & verifier remediation:**
  * In `code/code_quotient_solver.py`, implemented the exact rational repair bridge via `solve_exact`: when $D$ has discarded singular directions ($0 < S \le \text{cutoff}$), exact elimination resolves whether $\omega \in \operatorname{im}(D)$ in exact arithmetic, returning validated zero-distance repairs and never certifying a false positive distance.
  * In `verify_certificate`, enforced strict finiteness checks across all intermediate matrix products, residuals, norms, defect bounds, and duality gaps before tolerance comparisons, correctly rejecting non-finite or overflowing candidates (e.g. $10^{200}$).
  * Excised unconditional `dist < 1e-15` shortcut in `_solve_l2` to respect requested tolerances, and enforced duality gap tolerance on all return paths.
  * Added three review counterexamples to regression suite in `code/test_quotient_solver.py`.
* **Notebook synchronizations:**
  * In `003_soundness_coupling_and_quotient_defect.ipynb`: replaced Theorem 6 derivation in Markdown cell 5 with the corrected single-site defect formulation ($\Delta(s)_{e_i} = -s(b)$), matching §3. Updated code cells 4 and 6 to report example checks passed. Replaced "exact LP" with floating-point linear programming estimation in cell 7 and 8. Updated synthesis takeaways 2 and 3.
  * In `001_intro_and_monitoring_blindspots.ipynb`: replaced formal verification phrasing in code cell 7 and 9 with numerical passivity and diagnostic wording.
  * In `002_false_green_and_no_recovery.ipynb`: sharpened overlap construction sentence in Markdown cell 2 and updated takeaway 2.
  * Verified that all three notebooks execute cleanly from start to finish.
* **Deposit verifier hardened (`verify_deposit.py`):**
  * Added mandatory verification of required replay files (`code/lgr_replay.py`, `code/test_lgr_replay.py`).
  * Enforced execution tracking across all 11 required baseline tests, rejecting empty suites, skipped tests, or incomplete fixtures.
  * Added unit test coverage for verifier branches in `code/test_cli.py`.
* **Test suite and coverage verification:**
  * Full computational harness expanded to 96 passed tests (49 subtests passed), achieving 100.00% statement coverage across all 7 modules (1020/1020 statements covered).
  * Recomputed SHA-256 digests for all 36 tracked files in `SHA256SUMS`.

## v0.1 Pre-Print (2026-09-09, publication review remediation) — numerical range hardening, column redundancy elimination, and verifier deposit alignment

* **Item 1: Norm underflow/overflow and invalid numerical results:**
  * Implemented `scaled_euclidean_norm` ($s \cdot \sqrt{\sum (v/s)^2}$) in `code/code_core.py` and `code/code_quotient_solver.py`, and integrated it across `code/code_blind_spots.py` and `code/code_theorems.py` to preserve representable values without floating-point underflow to zero or intermediate overflow to infinity.
  * In `code/code_core.py`, added range validation in `compute_norm` for $L_1, L_2, L_\infty$ (raising `ValueError` when computed norms exceed representable finite range) and in `compute_global_inconsistency` and `Evaluator.compute_score`.
  * In `code/code_quotient_solver.py` (`_solve_l2`), prevented underflow (such as $5 \times 10^{-200}$) from bypassing residual validation into zero-distance certification, ensuring nonzero residuals cannot be certified as zero distance. Added independent 1D oracle regression against $\operatorname{abs}(\omega[0])$ and verified rejection of fake zero-distance certificates.
  * In `code/code_theorems.py` (`check_theorem_1_passivity`), added upfront finiteness validation on $I(s)$ and $J^\alpha(s)$, detecting passivity failure on expanding measurements with large inputs ($10^{200}$) and rejecting non-finite candidates.
  * In `code/code_quotient_solver.py` exact-repair fallback, handled `(OverflowError, ValueError)` during float conversion of exact rational repair vectors (e.g., $D = [[1, 1], [0, 10^{-310}]], \omega = [0, 1]$), returning an uncertified `QuotientResult` instead of raising an unhandled exception.
  * In `code/test_quotient_solver.py`, corrected `test_verification_intermediate_overflow_rejected` to provide consistent primal data ($r = \omega - D\alpha$) while testing intermediate norm overflow rejection.
* **Item 2: Redundant matrix columns in SVD:**
  * Implemented `_exact_pivot_columns` in `code/code_quotient_solver.py` using exact Gauss-Jordan elimination over $\mathbb{Q}$ (`fractions.Fraction`) to identify the independent column basis $D_{\text{basis}}$ before floating-point SVD.
  * Solved optimization on $D_{\text{basis}}$ and zero-padded optimal coefficients back to the full $n$-dimensional space, preserving residual identity $\omega - D\alpha = \omega - D_{\text{basis}}\alpha_{\text{basis}}$ and original column dimensions.
  * In `_project_dual_witness` and `verify_certificate`, evaluated SVD singular value cutoffs on $D_{\text{basis}}$, eliminating LAPACK singular roundoff rejections ($\sim 3.35 \times 10^{-17} \le \text{cutoff}$) on redundant columns while preserving near-singular full-rank regression behavior ($D = [[1, 1], [0, 10^{-16}]]$ returning 0 distance in all three norms).
* **Item 3: Verifier alignment, full test suite pass, and notebook verification:**
  * Reconciled root `verify_deposit.py` with the exact 11 baseline replay tests and required deposit files.
  * Full computational harness expanded to 99 passed tests (49 subtests passed), achieving 100.00% statement and branch coverage across all 7 modules (1118/1118 statements covered).
  * Executed all 3 Jupyter notebooks (`001_intro_and_monitoring_blindspots.ipynb`, `002_false_green_and_no_recovery.ipynb`, `003_soundness_coupling_and_quotient_defect.ipynb`) with zero errors.
  * Recomputed SHA-256 digests for all 36 tracked files in `SHA256SUMS`, passing all 4 deposit verifier checks in `verify_deposit.py`.
  * Added PEP 517/518 build-system and setuptools py-modules discovery to `pyproject.toml`, ensuring pip installation without flat-layout package discovery errors in fresh downstream environments.

## v0.1 Pre-Print (2026-09-09, post-review revisions) — Lean coverage qualification, witness notation separation, documentation sync, and verifier expected-failure rejection

* **Rejection of expected failures in deposit verifier:**
  * In `verify_deposit.py`, added an explicit check rejecting non-empty `result.expectedFailures` before issuing the verification success receipt.
  * Added regression test `test_verify_deposit_main_expected_failure` in `code/test_cli.py`. Full test suite now passes with 100 tests (49 subtests passed) and 100.00% statement and branch coverage across all 7 modules (1118/1118 statements).
* **Separation of target severity from amplitude in witness notation:**
  * In `local_green_global_red.md` (Theorem 3), defined $s^{(\lambda)}$ for the amplitude-indexed assignment ($I(s^{(\lambda)}) = 6|\lambda|$) and retained $s_R := s^{(R/6)}$ for the severity-indexed assignment ($I(s_R) = R$).
  * In §6 last paragraph, updated receipt notation to unit amplitude $I(s^{(1)}) = 6$ with score vector $(0, 0, 0)$.
  * Recompiled `local_green_global_red.pdf` via Pandoc/XeLaTeX (verified 9 rendered pages without overflow).
* **Alignment of Lean coverage claims in supporting documents:**
  * In `README.md` and `local_green_global_red_claim_ledger.md`, replaced blanket mechanization statements with qualified scope: Lean covers abstract observer statements and edge-level defect calculations; the six-site graph realization is established by the explicit construction in §3; exact Python replays check finite-instance arithmetic; the finite-dimensional quantitative recovery bound is proved in prose.
  * In `local_green_global_red_claim_ledger.md`, added row `LGR-T5B` for the finite-dimensional quantitative recovery bound (labeled PROVED IN PROSE).
* **Documentation and path synchronization:**
  * In `README.md`: synchronized test counts in contents table and harness command comment to reflect 100 passed tests (49 subtests passed) with 100% coverage gate; updated Lean build pointer to shipped `lean4/README.md`; updated anchor publication record reference to v6.3; specified the scalar variant for the coupled distance-2 example.
  * In `local_green_global_red_claim_ledger.md`: updated second Lean source paragraph to reference declaration inventory in `manifest.json`; documented the coordinate/evaluator relabeling convention in row LGR-T6.

## v0.1 Pre-Print (2026-09-09, final Zenodo readiness pass) — metadata, Lean replay, and integrity closure

* **Publication metadata closure:**
  * Expanded `.zenodo.json` with the exact version DOI for the anchor release, retained the concept DOI, added seven keywords, and reshaped the description as abstract, why-care, and nonclaims text with no fake DOI.
  * Replaced stale live-document references in the Lean README with shipped deposit files (`local_green_global_red_claim_ledger.md` and `manifest.json`).
  * Corrected claim-ledger table/text defects and removed a stale internal-review "republication" phrase from the change log.
* **Lean package closure:**
  * Added `lean4/lake-manifest.json` to the intentional deposit surface and documented it in `README.md`, `lean4/README.md`, and `manifest.json`.
  * Preserved `po000_l004_observer_visibility.lean` as the byte-identical anchor snapshot (SHA-256 `aa34acc95bf399ac085ee4fcc379f6490e691e4bcb557d4ebe24200b6230f295`), including its two documented unused-simp-argument lint warnings.
  * Removed the same redundant simp arguments from the deposit-owned `observer_visibility.lean`, updated its provenance SHA-256 to `9585ff8f40d0c2f5fa45c3086bd1199fe4a65c37d94ba4af3643e7261000efec`, and recompiled it in the final Lake replay.
  * Replayed `lake exe cache get! observer_visibility.lean po000_l004_observer_visibility.lean` in a short Windows path: exit 0, 8691 cached files decompressed.
  * Replayed `lake build ObserverVisibility` against the exact shipped Lean sources: exit 0, `Build completed successfully (8709 jobs)`, all `#print axioms` reports within `{propext, Classical.choice, Quot.sound}`.
* **Code verification closure:**
  * Replayed the pure-stdlib exact tests with `py -3 -m unittest discover -s code -p "test_lgr_replay.py"`: 11 tests, OK.
  * Replayed `py -3 code\lgr_replay.py`: deterministic receipt `I=6 J=[0, 0, 0] coverage=full 6lam-checks=pass coupled=forced phi=2`.
  * Replayed the optional computational harness in a temporary Python 3.12 uv environment outside the deposit tree: 100 passed tests, 49 subtests passed, 100.00% coverage across the seven harness modules.

## v0.1 Pre-Print (2026-09-10, Zenodo release assembly and readiness review closure) — complete 37-file payload closure, license inclusion, Lake project verification, and layout normalization

* **Release payload closure (37 files):**
  * Included `LICENSE` (full text of Creative Commons Attribution 4.0 International, CC-BY-4.0) at the deposit root, resolving review blocker.
  * Shipped complete Lake project support files under `lean4/` (`lakefile.lean`, `lean-toolchain`, `lake-manifest.json`, and `README.md`) alongside `observer_visibility.lean`, `po000_l004_observer_visibility.lean`, and `PROVENANCE.md`, enabling full local replay of Lean 4 builds against `leanprover/lean4:v4.34.0-rc1`.
  * Included all three interactive Jupyter notebooks under `jupyter_notebooks/` (`001_intro_and_monitoring_blindspots.ipynb`, `002_false_green_and_no_recovery.ipynb`, `003_soundness_coupling_and_quotient_defect.ipynb`).
  * Reconciled total tracked payload count to 37 files across the deposit (10 root files + 17 code + 3 notebooks + 7 lean4).
* **Historical layout reference normalization:**
  * Explicitly marked legacy path references (`code/tests/`, `code/tests/test_lgr_replay.py`, `code/pyproject.toml`) in historical entries as earlier internal staging layouts superseded by `code/test_lgr_replay.py` and root `pyproject.toml`.
  * Clarified that legacy `docs/` artifacts from parallel build (a) were consolidated into canonical root documentation (`README.md`, `local_green_global_red_claim_ledger.md`, `manifest.json`, `.zenodo.json`).
* **Publication date reconciliation:**
  * Updated `.zenodo.json` publication date to `2026-09-10`.
  * Synchronized `README.md`, `manifest.json`, and `local_green_global_red_claim_ledger.md` to document both the manuscript completion date (`2026-09-09`) and Zenodo release deposit date (`2026-09-10`).
  * Retained exact byte identity of `local_green_global_red.pdf` and manuscript markdown `local_green_global_red.md` (dated 2026-09-09) to preserve verified visual formatting without pagination or font shifts.
* **Integrity verification pass:**
  * Recomputed official `SHA256SUMS` across all 37 payload files.
  * Executed `python verify_deposit.py`: passed 4/4 checks (37 files verified, 11 tests passed, all exact values matched).
  * Executed `python code/run_tests.py`: 100 passed tests, 49 subtests passed, 100.00% statement and branch coverage (1118/1118 statements).

## v1.0.0 (2026-09-13) — Consolidation into LGGR Foundational Series

* **Relocation to Foundational Series:** Moved package from `002_projection_obstruction/029_local_green_global_red` to `001_finite_obstruction_calculus/012_local_green_global_red_foundational_series/parts/lggr_v_local_green_global_red` as Part V of the unified master monograph.
* **Canonical document naming:** Renamed primary documents to `lggr_v_local_green_global_red.md`, `lggr_v_local_green_global_red_claim_ledger.md`, and `lggr_v_local_green_global_red_change_log.md`.
* **Cross-reference synchronization:** Reconciled series paths and sibling metadata links.

## Local repair (2026-10-09) — rational Minkowski identities, no version bump

* **Version.** Canonical version remains v1.3.0 (2026-10-05). No new DOI and no new deposit ZIP. `lggr_v_local_green_global_red_2026-10-05.zip` is unchanged.
* **LGR-T5B.** Withdrawn as a non-claim of this deposit. The compact-sphere existence argument remains visible and is not a Lean theorem here. `compute_recovery_constant` remains a singular-value formula and is not that infimum.
* **LGR-R2, LGR-R3, LGR-R4.** The rational identities are proved in `lean4/minkowski_repair.lean`, which is not a Lake root, and checked by exact `Fraction` replays in `code/lgr_replay.py`. Square-root symbols name the proved squares. The default verifier elaborates that Lean file with the pinned toolchain binary and does not run `lake`.
* **PDF.** `lggr_v_local_green_global_red.pdf` was rebuilt from the repaired tex with pdfLaTeX (21 pages). Earlier rows in this log that still call the recovery bound proved in prose are history.


## v1.3.1 (2026-10-10) — targeted republication consistency repair

* Restore LGR-T5B as proved in prose for a finite-dimensional realizable defect space, with its zero-space branch and explicit nonzero-space qualification for the normalized infimum. Preserve the narrower ambient-injectivity SVD helper contract.
* Reconcile the three mathematical Lean sources and 19 rational repair reports. Separate current manuscript claims from supplementary cycle, holonomy, redundancy, non-linear, and norm-chain development; distinguish real written proofs from Rat/squared-Euclidean formalization.
* Use manifest.json as canonical release identity and publication description; generate both Zenodo metadata files and descriptions, with identity/license drift checks. Record the licenses actually shipped: CC BY 4.0 for text/figures/docs and Apache 2.0 for code/Lean/notebooks/tooling. Earlier license entries above describe historical decisions, not the current LICENSE-CODE bytes.
* Accept flat code/test_*.py named targets while rejecting unsafe paths, empty collections, and failing tests. Validate the exact compiler release, isolate standalone outputs, and compare the optional Lake census by declaration name and axiom set. Missing pinned build resources remain verification failures.
* Regenerate TeX/PDF from the canonical Markdown, replacing the stale derived manuscript. Deterministic archive names and member timestamps use the release date rather than the rebuild day. Release checks do not constitute an external upload or new publication authority.

## v1.3.2 (2026-10-15) — release metadata, link, and prose hygiene synchronization

* Synchronized release date (`2026-10-15`) and version (`1.3.2`) across `lggr_v_local_green_global_red.md`, `manifest.json`, `README.md`, `pyproject.toml`, `zenodo_metadata.json`, `.zenodo.json`, `lggr_v_local_green_global_red_claim_ledger.md`, and `lggr_v_local_green_global_red_change_log.md`.
* Replaced relative Markdown file links in the manuscript header with inline code identifiers and removed internal governance boilerplate.
* Rebuilt `lggr_v_local_green_global_red.tex`, `lggr_v_local_green_global_red.pdf`, `MANIFEST.sha256`, `SHA256SUMS`, and `lggr_v_local_green_global_red_2026-10-15.zip`.
