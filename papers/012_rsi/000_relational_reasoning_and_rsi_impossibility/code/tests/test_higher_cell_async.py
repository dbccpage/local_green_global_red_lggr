# Claim Hygiene: AuthorityEffect: None
# Tests verify higher k-cell cochain complex exactness (d^k o d^{k-1} = 0), coboundary holonomy,
# FIFO asynchronous message delay buffer semantics, delay-compensated and uncompensated
# coadaptation, and cross-checks against Rust omega_epistemic_immune_system.
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = PACKAGE_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from single_agent_graph import compute_d1_triangle  # noqa: E402
from simplicial_complex import (  # noqa: E402
    HigherCellComplex,
    build_exact_k_cochain_from_potential,
    compute_dk_coboundary,
    compute_higher_cell_phi1_holonomy,
)
from communication_channels import AsynchronousMessageDelayBuffer  # noqa: E402
from higher_cell_async_hypergraph import (  # noqa: E402
    HigherCellAsyncCommunicatingHypergraph,
    HigherCellObstructionReceipt,
    make_async_delay_compensated_step_fn,
    make_async_uncompensated_stale_cochain_step_fn,
)
from eis_verifier import cross_check_receipts_against_rust_eis  # noqa: E402


@pytest.mark.parametrize("degree", [1, 2, 3, 4])
def test_higher_k_cell_cochain_complex_exactness_and_coboundary_holonomy(degree: int) -> None:
    """Verify exactness `d^k o d^{k-1} = 0` (`Phi_1([d^{k-1} eta^{(k-1)}]) = 0`) and non-exact
    coboundary holonomy `Phi_1([delta^{(k)}]) > 0` across higher k-cell complexes `C^k --d^k--> C^{k+1}`."""
    complex_k = HigherCellComplex.standard_simplex(degree=degree, num_cells=2)
    assert len(complex_k.k_plus_1_cells) == 2
    for cell in complex_k.k_plus_1_cells:
        assert len(cell) == degree + 2
        faces = HigherCellComplex.boundary_faces_of_simplex(cell)
        assert len(faces) == degree + 2

    # 1. Any k-cochain constructed as d^{k-1}(eta^{(k-1)}) must satisfy d^k(d^{k-1} eta) = 0 -> Phi_1 = 0
    km1_cells = sorted(complex_k.required_k_minus_1_cells())
    potential = {
        km1_cell: Fraction((idx * 3 + 2), (idx + 5))
        for idx, km1_cell in enumerate(km1_cells)
    }
    exact_k_cochain = build_exact_k_cochain_from_potential(complex_k, potential)
    for cell in complex_k.k_plus_1_cells:
        assert compute_dk_coboundary(exact_k_cochain, cell) == Fraction(0, 1)
    assert compute_higher_cell_phi1_holonomy(complex_k, exact_k_cochain) == Fraction(0, 1)

    # 2. For degree k=1, verify exact parity with compute_d1_triangle on (0, 1, 2)
    if degree == 1:
        test_1_cochain = {
            (0, 1): Fraction(2, 5),
            (1, 2): Fraction(3, 7),
            (0, 2): Fraction(1, 3),
            (1, 3): Fraction(1, 2),
            (0, 3): Fraction(1, 4),
        }
        assert compute_dk_coboundary(test_1_cochain, (0, 1, 2)) == compute_d1_triangle(
            test_1_cochain, 0, 1, 2
        )

    # 3. Perturbing a single k-face shared only by the first (k+1)-simplex induces exact rational Phi_1 > 0
    perturbed = dict(exact_k_cochain)
    # The last boundary face `simplex[:-1] = (0, 1, ..., k)` is shared by both cells, while
    # `simplex[1:] = (1, ..., k, k+1)` belongs exclusively to the first (k+1)-cell.
    exclusive_face = HigherCellComplex.boundary_faces_of_simplex(complex_k.k_plus_1_cells[0])[0][1]
    defect = Fraction(5, 13)
    perturbed[exclusive_face] = perturbed[exclusive_face] + defect
    assert compute_dk_coboundary(perturbed, complex_k.k_plus_1_cells[0]) == defect
    assert compute_dk_coboundary(perturbed, complex_k.k_plus_1_cells[1]) == Fraction(0, 1)
    assert compute_higher_cell_phi1_holonomy(complex_k, perturbed) == defect


def test_asynchronous_message_delay_buffer_fifo_semantics() -> None:
    """Verify that `AsynchronousMessageDelayBuffer` delivers `pi_a(M_{k - min(k, tau_a)}^{(a)})`."""
    buf = AsynchronousMessageDelayBuffer(num_agents=2, latency_steps=(1, 3))
    assert buf.latency_per_agent == (1, 3)
    assert buf.max_latency == 3

    emitted_seq = [(10, 100), (11, 101), (12, 102), (13, 103), (14, 104)]
    delivered_trace: list[tuple[int, ...]] = []
    lags_trace: list[tuple[int, ...]] = []
    for step, emitted in enumerate(emitted_seq):
        delivered, lags = buf.record_and_deliver(step, emitted)
        delivered_trace.append(delivered)
        lags_trace.append(lags)

    assert lags_trace == [(0, 0), (1, 1), (1, 2), (1, 3), (1, 3)]
    assert delivered_trace == [
        (10, 100),  # step 0: lag (0, 0) -> (step 0, step 0)
        (10, 100),  # step 1: lag (1, 1) -> (step 0, step 0)
        (11, 100),  # step 2: lag (1, 2) -> (step 1, step 0)
        (12, 100),  # step 3: lag (1, 3) -> (step 2, step 0)
        (13, 101),  # step 4: lag (1, 3) -> (step 3, step 1)
    ]


@pytest.mark.parametrize("degree", [1, 2, 3])
@pytest.mark.parametrize("latency_tau", [0, 1, 2, 3, 5])
def test_higher_cell_async_delay_compensated_coadaptation_alters_step_within_product_bound(
    degree: int, latency_tau: int
) -> None:
    """Verify that on higher k-cell complexes `C^k --d^k--> C^{k+1}`, bounded communication latency `tau`
    under delay-compensated cochain gluing (`Phi_1([delta^{(k)}]) = 0`) alters the trajectory and shifts
    the exact collision step `k*(tau)` while strictly obeying `k*(tau) <= N_A * N_B + 1`."""
    n_a, n_b = 3, 4
    higher_complex = HigherCellComplex.standard_simplex(degree=degree, num_cells=1)
    zero_cochain = {face: Fraction(0, 1) for face in higher_complex.required_k_cells()}

    hg = HigherCellAsyncCommunicatingHypergraph(
        agent_capacities=(n_a, n_b),
        higher_complex=higher_complex,
        latency_steps=latency_tau,
        initial_agent_states=(0, 0),
        initial_budget=25,
        initial_k_cochain=zero_cochain,
        step_fn=make_async_delay_compensated_step_fn((n_a, n_b), higher_complex),
    )
    receipt = hg.run()
    assert receipt.halted is True
    assert receipt.cochain_degree == degree
    assert receipt.latency_steps == (latency_tau, latency_tau)
    assert receipt.obstruction_kind == "REPORT_COLLISION"
    assert receipt.phi1_holonomy == Fraction(0, 1)
    assert 1 <= receipt.termination_step <= n_a * n_b + 1
    assert "ok" in receipt.eis_independence_verdict

    if latency_tau == 0:
        # Zero communication latency recovers full product-carrier traversal k*(0) = N_A * N_B = 12
        assert receipt.termination_step == n_a * n_b == 12
        assert receipt.delayed_beyond_single_agent is True
    elif latency_tau in (1, 2):
        # Non-zero communication latency alters the carry feedback phase and changes k*(tau) != k*(0)
        assert receipt.termination_step < n_a * n_b
        assert receipt.termination_step > max(n_a, n_b)
        assert receipt.delayed_beyond_single_agent is True


@pytest.mark.parametrize("degree", [1, 2, 3])
@pytest.mark.parametrize("latency_tau", [0, 1, 2, 3])
def test_higher_cell_async_uncompensated_latency_induces_phi1_holonomy_refusal(
    degree: int, latency_tau: int
) -> None:
    """Verify that uncompensated asynchronous communication latency `tau >= 1` on `C^k --d^k--> C^{k+1}`
    induces a stale-section coboundary defect `Phi_1([delta^{(k)}]) > 0` and shifts termination from
    `REPORT_COLLISION` (at `tau = 0`, `k* = 12`) to `OVERLAP_GLUING_REFUSAL` at `k* = defect_trigger_step <= N_A * N_B + 1`."""
    n_a, n_b = 3, 4
    trigger_step = 3
    higher_complex = HigherCellComplex.standard_simplex(degree=degree, num_cells=1)
    zero_cochain = {face: Fraction(0, 1) for face in higher_complex.required_k_cells()}

    hg = HigherCellAsyncCommunicatingHypergraph(
        agent_capacities=(n_a, n_b),
        higher_complex=higher_complex,
        latency_steps=latency_tau,
        initial_agent_states=(0, 0),
        initial_budget=25,
        initial_k_cochain=zero_cochain,
        step_fn=make_async_uncompensated_stale_cochain_step_fn(
            (n_a, n_b), higher_complex, defect_trigger_step=trigger_step
        ),
    )
    receipt = hg.run()
    assert receipt.halted is True
    assert receipt.cochain_degree == degree
    assert receipt.termination_step <= n_a * n_b + 1
    assert "ok" in receipt.eis_independence_verdict

    if latency_tau == 0:
        # With zero latency, delivered_projections == emitted_projections at every step -> Phi_1 = 0 -> REPORT_COLLISION at k* = 12
        assert receipt.obstruction_kind == "REPORT_COLLISION"
        assert receipt.phi1_holonomy == Fraction(0, 1)
        assert receipt.termination_step == n_a * n_b == 12
    else:
        # With latency tau >= 1, stale-vs-live projection mismatch induces Phi_1([delta^{(k)}]) > 0 at k* = trigger_step
        assert receipt.obstruction_kind == "OVERLAP_GLUING_REFUSAL"
        assert receipt.termination_step == trigger_step
        assert receipt.phi1_holonomy > Fraction(0, 1)


def test_higher_cell_async_hypergraph_receipts_cross_checked_against_rust_eis() -> None:
    """Cross-check emitted `HigherCellObstructionReceipt`s across degrees k in {1, 2, 3} (delay-compensated
    collision, uncompensated higher-coboundary refusal, lift-budget exhaustion, and adversarial self-critique
    observers) against the compiled Rust `rust_eis_companion` binary and `omega_epistemic_immune_system`."""
    receipts: list[HigherCellObstructionReceipt] = []

    for degree in (1, 2, 3):
        hc = HigherCellComplex.standard_simplex(degree=degree, num_cells=1)
        zero_c = {face: Fraction(0, 1) for face in hc.required_k_cells()}

        # 1. Delay-compensated collision receipt (Phi_1 = 0, REPORT_COLLISION at k* <= N_A * N_B + 1)
        hg_comp = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=(3, 4),
            higher_complex=hc,
            latency_steps=2,
            initial_agent_states=(0, 0),
            initial_budget=20,
            initial_k_cochain=zero_c,
            step_fn=make_async_delay_compensated_step_fn((3, 4), hc),
        )
        r_comp = hg_comp.run()
        assert r_comp.obstruction_kind == "REPORT_COLLISION"
        assert r_comp.termination_step == 9 <= 3 * 4 + 1
        assert "ok" in r_comp.eis_independence_verdict
        receipts.append(r_comp)

        # 2. Uncompensated stale-cochain refusal receipt (Phi_1 > 0, OVERLAP_GLUING_REFUSAL at k* = 2 <= 13)
        hg_stale = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=(3, 4),
            higher_complex=hc,
            latency_steps=2,
            initial_agent_states=(0, 0),
            initial_budget=20,
            initial_k_cochain=zero_c,
            step_fn=make_async_uncompensated_stale_cochain_step_fn(
                (3, 4), hc, defect_trigger_step=2
            ),
        )
        r_stale = hg_stale.run()
        assert r_stale.obstruction_kind == "OVERLAP_GLUING_REFUSAL"
        assert r_stale.termination_step == 2 <= 3 * 4 + 1
        assert r_stale.phi1_holonomy > Fraction(0, 1)
        assert "ok" in r_stale.eis_independence_verdict
        receipts.append(r_stale)

        # 3. Lift-budget exhaustion on higher k-cell async hypergraph (budget = 3 < k*(tau))
        hg_budget = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=(3, 4),
            higher_complex=hc,
            latency_steps=1,
            initial_agent_states=(0, 0),
            initial_budget=3,
            initial_k_cochain=zero_c,
            step_fn=make_async_delay_compensated_step_fn((3, 4), hc),
        )
        r_budget = hg_budget.run()
        assert r_budget.obstruction_kind == "LIFT_BUDGET_EXHAUSTION"
        assert r_budget.termination_step == 3 <= 3 * 4 + 1
        assert r_budget.remaining_budget == 0
        assert "ok" in r_budget.eis_independence_verdict
        receipts.append(r_budget)

    # 4. Adversarial self-critique observers on higher k-cell async hypergraph must trigger TWO_SIGNAL_COLLAPSE
    hc2 = HigherCellComplex.standard_simplex(degree=2, num_cells=1)
    zero_c2 = {face: Fraction(0, 1) for face in hc2.required_k_cells()}
    for bad_observer in ("agent", "model", "llm", "detector.higher_cell_async_rsi_scanner"):
        hg_bad = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=(3, 4),
            higher_complex=hc2,
            latency_steps=1,
            initial_agent_states=(0, 0),
            initial_budget=10,
            initial_k_cochain=zero_c2,
            step_fn=make_async_delay_compensated_step_fn((3, 4), hc2),
            signal2_observer_id=bad_observer,
        )
        r_bad = hg_bad.run()
        assert "error" in r_bad.eis_independence_verdict
        assert r_bad.eis_independence_verdict["error"]["code"] == "TWO_SIGNAL_COLLAPSE"  # type: ignore[index]
        receipts.append(r_bad)

    summary = cross_check_receipts_against_rust_eis(receipts)
    assert summary["metadata_record_count"] == len(receipts)
    assert summary["rust_companion_executed"] is True
    assert summary["eis_fixture_vectors"] == 55
    assert summary["eis_digest_vectors"] == 7
