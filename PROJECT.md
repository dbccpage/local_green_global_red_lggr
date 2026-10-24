# Project: Local Green, Global Red (LGGR) Volume VIII Advancement

## Architecture
The LGGR Volume VIII advancement establishes online, streaming detection of composability obstructions (Local Green, Global Red) in running agentic swarms, formalizes its guarantees in Lean 4, benchmarks empirical defect rates with live OpenRouter models, and delivers pedagogical practitioner cookbooks and synchronized wiki documentation.

### Architectural Modules:
1. **Streaming Runtime Monitor (`lggr/streaming.py`)**:
   - `StreamingFiberMonitor`: Incremental state observation, report-fiber mapping, and on-the-fly collision detection ($p(x_1) = p(x_2)$ while $q(x_1) \ne q(x_2)$).
   - `StreamingAuditMonitor`: Incremental step witness ingestion, $G_1$–$G_4$ conditional gluing checks, prefix-by-prefix signed budget drift evaluation (`every_prefix` vs `endpoint`), evaluator defect calculation $\Delta_E \in \{-1, 0, 1\}$ (`NGD`, `ZDR`, `PGD`), and mid-flight early-stopping alerts.
   - `StreamingCochainMonitor`: Incremental edge ingestion, cycle closure detection, $(D_1 h)_C$ defect checking, and exact rational $\ell^1$ primal/dual repair distance and witness certification.
2. **CLI & Standalone Zipapp (`lggr/__main__.py`, `lggr_witness_audit.pyz`)**:
   - Add `selftest` subcommand emitting JSON receipt `lggr.selftest.v1`.
   - Add `stream` subcommand consuming line-delimited JSON step/trace events and emitting streaming receipts.
   - Rebuild standalone zipapp via clean staging.
3. **Live Swarm Benchmarks (`tests/test_live_benchmarks.py`, `receipts/live_benchmarks/`)**:
   - Standard-library OpenRouter credentials loader (from sibling `.env`, zero secrets committed).
   - Bounded live completions ($\le 40$).
   - Volume I §9 empirical NGD/PGD rate measurement across fixed multi-stage tasks.
   - Tests 1–4 structured online discovery experiments (fiber collision, prefix drift breach, 1-cochain cycle, boundary-sufficient LGGG).
   - Deterministic offline JSON replay test suite.
4. **Lean 4 Formalization (`lean4/LggrVIII.lean`)**:
   - 12 formal theorems formalizing online prefix discovery, collision monotonicity, prefix vs endpoint admissibility, and boundary-sufficient certificates.
   - Zero `sorry`, zero custom axioms, builds cleanly under Lean 4.35.0.
5. **Volume VIII Paper Package (`papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/`)**:
   - Markdown manuscript, 14-row typed claim ledger (`C-01` to `C-14`), companion code, receipts, and mirrored `lean4/`.
6. **Cookbooks & Wiki Sync (`cookbooks/`, Wiki repo)**:
   - 4 runnable standalone cookbooks.
   - GitHub Wiki updates: Volume VIII page, Practitioner Guide page, updated sidebar and home.
   - MathJax compatibility: strictly zero `\operatorname` macros.
   - Monograph index and `MANIFEST.sha256` updates.

---

## Feature Inventory
Every feature from the survey phase is inventoried and assigned to a milestone.

| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| F01 | `StreamingFiberMonitor` | Incremental report-fiber mapping and instant collision detection | M1 | R1.1 |
| F02 | `StreamingAuditMonitor` | Prefix-by-prefix $G_1$–$G_4$ gluing, `every_prefix` vs `endpoint` drift, $\Delta_E \in \{-1,0,1\}$ | M1 | R1.2 |
| F03 | `StreamingCochainMonitor` | Incremental edge addition, cycle closure $(D_1 h)_C$, exact rational $\ell^1$ repair witness | M1 | R1.3 |
| F04 | Zipapp `selftest` subcommand | CLI subcommand in `lggr/__main__.py` and `lggr_witness_audit.pyz` emitting JSON receipt | M1 | Acceptance |
| F05 | Zipapp `stream` subcommand | CLI subcommand for streaming JSON event processing | M1 | R1, Acceptance |
| F06 | Rebuilt `lggr_witness_audit.pyz` | Standalone executable zipapp package with zero external dependencies | M1 | Acceptance |
| F07 | Unit tests for streaming | Test suite `tests/test_streaming.py` and CLI tests `tests/test_cli.py` | M1 | Acceptance |
| F08 | Zero-dep OpenRouter loader | Stdlib credential resolver loading from sibling `.env` with zero key leakage | M2 | R2, R5 |
| F09 | Empirical NGD/ZDR/PGD rates | Volume I §9 empirical measurement: LPR, GPR, NGD, ZDR, PGD, mean defect, EGD | M2 | R2.1 |
| F10 | Live Test 1: Fiber collision | Online detection of boundary insufficiency across multi-stage handoffs | M2 | R2.2 |
| F11 | Live Test 2: Prefix threshold breach | Online early-stopping on `every_prefix` violation during tool chains | M2 | R2.2 |
| F12 | Live Test 3: Incremental 1-cochain | Online detection of 3-agent cyclic inconsistency and exact $\ell^1$ repair cost | M2 | R2.2 |
| F13 | Live Test 4: Composable LGGG | Boundary-sufficient schema certifying $\Delta_E = 0$ throughout | M2 | R2.2 |
| F14 | Offline deterministic replay | JSON trace artifacts in `receipts/live_benchmarks/` replayable without network | M2 | R2.2, Acceptance |
| F15 | Lean 4 online discovery theorems | 12 theorems in `lean4/LggrVIII.lean` (collision monotonicity, prefix separation, etc.) | M3 | R3 |
| F16 | Lean 4 axiom audit | `lean4/CheckAxioms.lean` verifying zero `sorry` and standard core axioms only | M3 | R3, Acceptance |
| F17 | Volume VIII manuscript | `papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/` manuscript | M4 | R3 |
| F18 | Volume VIII claim ledger | 14-row typed claim ledger (`C-01` to `C-14`) with proof/code/receipt bindings | M4 | R3 |
| F19 | Volume VIII companion code & tests | Standalone companion code and tests matching paper claims | M4 | R3 |
| F20 | 4 Practitioner Cookbooks | Standalone scripts in `cookbooks/01_` through `04_` | M5 | R4 |
| F21 | Monograph Index update | Update `papers/local_green_global_red_monograph_index.md` with Volume VIII | M5 | R4 |
| F22 | Cloned Wiki sync | Update Wiki with Volume VIII page, Practitioner page, sidebar, no `\operatorname` | M5 | R4 |
| F23 | Git commit & push | Commit and push main repository and wiki repository | M5 | Acceptance |
| F24 | Manifest verification | Update and validate `MANIFEST.sha256` | M5 | Acceptance |
| F25 | Opaque-Box E2E Test Suite | 4-tier requirement-driven E2E test suite publishing `TEST_READY.md` | M-TEST | Dual Track |
| F26 | Final Integration & Hardening | Pass 100% E2E tests, Tier 5 adversarial coverage, claim hygiene audit | M-FINAL | Acceptance |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M-TEST | E2E Testing Track | Independent requirement-driven 4-tier test harness and test cases; publish `TEST_READY.md` | none | PLANNED |
| M1 | Core Streaming Monitor & Zipapp CLI | `lggr/streaming.py`, `lggr/__init__.py`, `lggr/__main__.py`, zipapp packaging, unit tests | none | PLANNED |
| M2 | Live Swarm Benchmarks & Replay | OpenRouter runner, Tests 1–4, empirical NGD/PGD, offline replay JSON artifacts | M1 | PLANNED |
| M3 | Lean 4 Formalization | `lean4/LggrVIII.lean`, `CheckAxioms.lean`, lake build verification (zero sorry/axioms) | none | PLANNED |
| M4 | Volume VIII Paper Package | `papers/lggr_viii_online_streaming_discovery_and_runtime_gluing/` manuscript, claim ledger, companion | M1, M2, M3 | PLANNED |
| M5 | Cookbooks, Docs & Wiki Sync | `cookbooks/`, `README.md`, monograph index, wiki repo update, `MANIFEST.sha256`, git commit/push | M1, M2, M3, M4 | PLANNED |
| M-FINAL | Final Milestone: E2E Pass & Hardening | Pass 100% E2E tests, Phase 2 Tier 5 adversarial hardening, zero-violation forensic audit | M-TEST, M1, M2, M3, M4, M5 | PLANNED |

---

## Interface Contracts

### 1. `lggr.streaming` Python API
```python
class StreamingFiberMonitor:
    def observe(self, state_id: str, report: Any, query: Any) -> dict[str, Any]:
        """Returns {"status": "OK" | "REPORT_INSUFFICIENT", "colliding_pair": ... | None}"""

class StreamingAuditMonitor:
    def __init__(self, policy: BudgetPolicy): ...
    def step(self, witness: StepWitness, global_evaluator_sample: int | None = None) -> dict[str, Any]:
        """Returns {"status": "OK" | "ALERT", "defect": -1|0|1, "classification": "NGD"|"ZDR"|"PGD", ...}"""

class StreamingCochainMonitor:
    def add_edge(self, u: str, v: str, value: Fraction | int | str, weight: Fraction | int = 1) -> dict[str, Any]:
        """Returns {"status": "OPEN_TREE" | "CYCLE_CLOSED", "closure_defect": Fraction | None, "l1_repair_distance": Fraction | None, "dual_witness": ...}"""
```

### 2. CLI Invocation Contracts
- `python lggr_witness_audit.pyz selftest` -> JSON `{"schema": "lggr.selftest.v1", "status": "PASS", "modules_tested": [...]}` with exit code `0`.
- `python -m lggr stream --monitor {fiber,audit,cochain}` -> processes line-delimited JSON events and writes JSON receipts to stdout.

### 3. OpenRouter Benchmarks & Replay Receipts
- Live runner bounds requests $\le 40$.
- Replay artifacts in `receipts/live_benchmarks/` matching schema `lggr.trace_replay.v1`.
- Offline unit tests in `tests/test_live_benchmarks.py` replay all traces with zero network access.

### 4. Lean 4 Formalization
- Package `LGGR` in `lean4/`.
- Root modules `LggrVII`, `LggrVIII`, `CheckAxioms`.
- `lake build` exits 0 with zero `sorry` and standard Lean core axioms only.

---

## Code Layout
- `lggr/` — Core Python package (standard library only).
- `tests/` — Unit and integration tests (standard library `unittest`).
- `cookbooks/` — Standalone runnable examples for practitioners.
- `lean4/` — Lean 4 library and proof audit.
- `papers/` — Monograph volume packages.
- `receipts/` — Verified machine-readable JSON receipts.
- `.agents/teamwork/` — Coordination metadata (strictly NO source code).
