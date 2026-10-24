# Claim Hygiene: AuthorityEffect: None
# Tests verify multi-agent communicating hypergraph coupled co-adaptation,
# product-carrier capacity and horizon bounds (k <= N_A * N_B + 1), licensed carrier lift
# budget exhaustion, overlap gluing refusal (Phi_1 > 0), and refusal receipt cross-checks
# against Rust omega_epistemic_immune_system.
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = PACKAGE_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from multi_agent_hypergraph import (  # noqa: E402
    HypergraphAgentSpec,
    HypergraphObstructionReceipt,
    MultiAgentCommunicatingHypergraph,
    MultiAgentTransitionState,
    SharedTwoComplex,
    build_flat_shared_cochain,
    coupled_odometer_step_fn,
    uncoupled_parallel_step_fn,
)
from eis_verifier import cross_check_receipts_against_rust_eis  # noqa: E402


@pytest.mark.parametrize(
    "n_a,n_b",
    [
        (2, 2),
        (2, 3),
        (3, 3),
        (3, 4),
        (4, 5),
        (5, 7),
    ],
)
def test_multi_agent_hypergraph_coupled_coadaptation_delays_but_cannot_evade_product_bound(
    n_a: int, n_b: int
) -> None:
    """Verify that coupled co-adaptation across a shared 2-complex delays collision past max(N_A, N_B)
    to N_A * N_B, but cannot evade the joint product-carrier horizon bound k <= N_A * N_B + 1."""
    shared_complex = SharedTwoComplex(
        vertices=(0, 1, 2),
        triangles=((0, 1, 2),),
        shared_edges=((0, 1), (1, 2), (0, 2)),
    )
    hypergraph = MultiAgentCommunicatingHypergraph(
        agents=(
            HypergraphAgentSpec("agent_A", n_a),
            HypergraphAgentSpec("agent_B", n_b),
        ),
        initial_lift_budget=0,
        shared_complex=shared_complex,
    )
    assert hypergraph.product_carrier_capacity == n_a * n_b
    assert hypergraph.horizon_bound == n_a * n_b + 1
    assert hypergraph.single_agent_max_capacity == max(n_a, n_b)

    init_state = MultiAgentTransitionState(
        step_index=0,
        agent_reports=(0, 0),
        joint_internal_eval=0,
        remaining_budget=0,
        edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
    )

    # 1. Uncoupled evolution (when n_a == n_b, collides early at k = n_a < n_a * n_b)
    uncoupled_receipt = hypergraph.run_coupled_trajectory(
        init_state, uncoupled_parallel_step_fn((n_a, n_b), shared_complex)
    )
    assert uncoupled_receipt.halted is True
    assert uncoupled_receipt.obstruction_kind == "REPORT_COLLISION"
    assert uncoupled_receipt.termination_step <= n_a * n_b + 1
    if n_a == n_b:
        assert uncoupled_receipt.termination_step == n_a < n_a * n_b
        assert uncoupled_receipt.delayed_beyond_single_agent is False

    # 2. Coupled co-adaptation exchanging boundary projections pi_A(M_k), pi_B(M_k) across shared 2-complex:
    #    Strictly delays termination beyond max(N_A, N_B) to N_A * N_B, yet still halts at k = N_A * N_B <= N_A * N_B + 1.
    coupled_receipt = hypergraph.run_coupled_trajectory(
        init_state, coupled_odometer_step_fn((n_a, n_b), shared_complex)
    )
    assert coupled_receipt.halted is True
    assert coupled_receipt.obstruction_kind == "REPORT_COLLISION"
    assert coupled_receipt.termination_step == n_a * n_b
    assert coupled_receipt.termination_step <= n_a * n_b + 1
    assert coupled_receipt.termination_step > max(n_a, n_b)
    assert coupled_receipt.delayed_beyond_single_agent is True
    assert coupled_receipt.colliding_prior_step == 0
    assert coupled_receipt.colliding_joint_report == (0, 0)
    assert coupled_receipt.phi1_holonomy == Fraction(0, 1)
    assert len(coupled_receipt.boundary_exchange_trace) == n_a * n_b + 1
    assert len(set(coupled_receipt.boundary_exchange_trace[:-1])) == n_a * n_b
    assert "ok" in coupled_receipt.eis_independence_verdict


def test_multi_agent_three_way_hypergraph_product_bound() -> None:
    """Verify a 3-agent communicating hypergraph (N_A=2, N_B=3, N_C=2, N_prod=12) across a 2-triangle complex."""
    shared_complex = SharedTwoComplex(
        vertices=(0, 1, 2, 3),
        triangles=((0, 1, 2), (0, 2, 3)),
        shared_edges=((0, 1), (1, 2), (0, 2), (2, 3), (0, 3)),
    )
    hypergraph = MultiAgentCommunicatingHypergraph(
        agents=(
            HypergraphAgentSpec("agent_A", 2),
            HypergraphAgentSpec("agent_B", 3),
            HypergraphAgentSpec("agent_C", 2),
        ),
        initial_lift_budget=0,
        shared_complex=shared_complex,
    )
    assert hypergraph.product_carrier_capacity == 12
    assert hypergraph.horizon_bound == 13
    init_state = MultiAgentTransitionState(
        step_index=0,
        agent_reports=(0, 0, 0),
        joint_internal_eval=0,
        remaining_budget=0,
        edge_cochain=build_flat_shared_cochain((0, 0, 0), shared_complex),
    )
    receipt = hypergraph.run_coupled_trajectory(
        init_state, coupled_odometer_step_fn((2, 3, 2), shared_complex)
    )
    assert receipt.halted is True
    assert receipt.obstruction_kind == "REPORT_COLLISION"
    assert receipt.termination_step == 12 <= 13
    assert receipt.delayed_beyond_single_agent is True
    assert receipt.phi1_holonomy == Fraction(0, 1)


@pytest.mark.parametrize("defect_step", [0, 2, 5, 9])
def test_multi_agent_hypergraph_overlap_gluing_refusal_phi1_positive(defect_step: int) -> None:
    """Verify that uncoordinated boundary projection updates on the shared 2-complex induce exact rational
    Phi_1([delta]) > 0 and trigger OVERLAP_GLUING_REFUSAL at step k <= N_A * N_B + 1."""
    n_a, n_b = 3, 4
    shared_complex = SharedTwoComplex(
        vertices=(0, 1, 2, 3),
        triangles=((0, 1, 2), (0, 2, 3)),
        shared_edges=((0, 1), (1, 2), (0, 2), (2, 3), (0, 3)),
    )
    hypergraph = MultiAgentCommunicatingHypergraph(
        agents=(
            HypergraphAgentSpec("agent_A", n_a),
            HypergraphAgentSpec("agent_B", n_b),
        ),
        initial_lift_budget=2,
        shared_complex=shared_complex,
    )
    base_step = coupled_odometer_step_fn((n_a, n_b), shared_complex)

    def _inject_defect(state: MultiAgentTransitionState) -> MultiAgentTransitionState:
        cochain = dict(state.edge_cochain)
        # Triangle (0,1,2) defect of 3/7
        cochain[(0, 1)] = cochain.get((0, 1), Fraction(0, 1)) + Fraction(3, 7)
        # Inter-agent overlap section disagreement of 2/5 on shared edge (0, 2)
        prop_a = dict(state.edge_cochain)
        prop_b = dict(state.edge_cochain)
        prop_a[(0, 2)] = prop_b.get((0, 2), Fraction(0, 1)) + Fraction(2, 5)
        return MultiAgentTransitionState(
            step_index=state.step_index,
            agent_reports=state.agent_reports,
            joint_internal_eval=state.joint_internal_eval,
            remaining_budget=state.remaining_budget,
            requests_carrier_lift=state.requests_carrier_lift,
            edge_cochain=cochain,
            agent_edge_proposals={"agent_A": prop_a, "agent_B": prop_b},
            signal2_observer_id=state.signal2_observer_id,
        )

    init_flat = MultiAgentTransitionState(
        step_index=0,
        agent_reports=(0, 0),
        joint_internal_eval=0,
        remaining_budget=2,
        edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
    )
    init_state = _inject_defect(init_flat) if defect_step == 0 else init_flat

    def _step(s: MultiAgentTransitionState) -> MultiAgentTransitionState:
        nxt = base_step(s)
        if nxt.step_index == defect_step:
            return _inject_defect(nxt)
        return nxt

    receipt = hypergraph.run_coupled_trajectory(init_state, _step)
    expected_phi1 = Fraction(3, 7) + Fraction(2, 5)  # 29/35
    assert receipt.halted is True
    assert receipt.obstruction_kind == "OVERLAP_GLUING_REFUSAL"
    assert receipt.termination_step == defect_step
    assert receipt.termination_step <= n_a * n_b + 1
    assert receipt.phi1_holonomy == expected_phi1 == Fraction(29, 35)
    assert receipt.phi1_holonomy > Fraction(0, 1)


@pytest.mark.parametrize(
    "n_a,n_b,initial_budget,stride",
    [
        (3, 3, 0, 1),
        (3, 4, 2, 2),
        (4, 4, 5, 2),
    ],
)
def test_multi_agent_hypergraph_lift_budget_exhaustion(
    n_a: int, n_b: int, initial_budget: int, stride: int
) -> None:
    """Verify that coupled co-adapting trajectories requesting licensed carrier lifts hit
    LIFT_BUDGET_EXHAUSTION (budget = 0) at step k <= N_A * N_B + 1."""
    shared_complex = SharedTwoComplex()
    hypergraph = MultiAgentCommunicatingHypergraph(
        agents=(
            HypergraphAgentSpec("agent_A", n_a),
            HypergraphAgentSpec("agent_B", n_b),
        ),
        initial_lift_budget=initial_budget,
        shared_complex=shared_complex,
    )
    base_step = coupled_odometer_step_fn((n_a, n_b), shared_complex)
    init_state = MultiAgentTransitionState(
        step_index=0,
        agent_reports=(0, 0),
        joint_internal_eval=0,
        remaining_budget=initial_budget,
        requests_carrier_lift=True,
        edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
    )

    def _step(s: MultiAgentTransitionState) -> MultiAgentTransitionState:
        nxt = base_step(s)
        return MultiAgentTransitionState(
            step_index=nxt.step_index,
            agent_reports=nxt.agent_reports,
            joint_internal_eval=nxt.joint_internal_eval,
            remaining_budget=nxt.remaining_budget,
            requests_carrier_lift=(nxt.step_index % stride == 0),
            edge_cochain=nxt.edge_cochain,
            agent_edge_proposals=nxt.agent_edge_proposals,
            signal2_observer_id=nxt.signal2_observer_id,
        )

    receipt = hypergraph.run_coupled_trajectory(init_state, _step)
    assert receipt.halted is True
    assert receipt.obstruction_kind == "LIFT_BUDGET_EXHAUSTION"
    assert receipt.remaining_budget == 0
    assert receipt.termination_step == initial_budget * stride
    assert receipt.termination_step <= n_a * n_b + 1


def test_multi_agent_hypergraph_receipts_cross_checked_against_rust_eis() -> None:
    """Cross-check emitted multi-agent hypergraph refusal receipts (delayed product-carrier collision,
    lift-budget exhaustion, overlap gluing refusal, and adversarial self-critique observers) against
    the compiled Rust `rust_eis_companion` binary and `omega_epistemic_immune_system`."""
    shared_complex = SharedTwoComplex()
    hypergraph = MultiAgentCommunicatingHypergraph(
        agents=(
            HypergraphAgentSpec("agent_A", 3),
            HypergraphAgentSpec("agent_B", 4),
        ),
        initial_lift_budget=2,
        shared_complex=shared_complex,
    )
    receipts: list[HypergraphObstructionReceipt] = []

    # 1. Coupled co-adaptation delaying collision beyond max(3, 4) = 4 to N_A * N_B = 12 <= 13
    r_coupled = hypergraph.run_coupled_trajectory(
        MultiAgentTransitionState(
            step_index=0,
            agent_reports=(0, 0),
            joint_internal_eval=0,
            remaining_budget=2,
            edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
        ),
        coupled_odometer_step_fn((3, 4), shared_complex),
    )
    assert r_coupled.obstruction_kind == "REPORT_COLLISION"
    assert r_coupled.termination_step == 12 <= 3 * 4 + 1
    assert r_coupled.delayed_beyond_single_agent is True
    assert "ok" in r_coupled.eis_independence_verdict
    receipts.append(r_coupled)

    # 2. Lift-budget exhaustion on coupled hypergraph (budget = 0 at k = 2 <= 13)
    base_step = coupled_odometer_step_fn((3, 4), shared_complex)
    r_lift = hypergraph.run_coupled_trajectory(
        MultiAgentTransitionState(
            step_index=0,
            agent_reports=(0, 0),
            joint_internal_eval=0,
            remaining_budget=2,
            requests_carrier_lift=True,
            edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
        ),
        lambda s: MultiAgentTransitionState(
            step_index=s.step_index + 1,
            agent_reports=base_step(s).agent_reports,
            joint_internal_eval=base_step(s).joint_internal_eval,
            remaining_budget=s.remaining_budget,
            requests_carrier_lift=True,
            edge_cochain=base_step(s).edge_cochain,
        ),
    )
    assert r_lift.obstruction_kind == "LIFT_BUDGET_EXHAUSTION"
    assert r_lift.termination_step == 2 <= 3 * 4 + 1
    assert "ok" in r_lift.eis_independence_verdict
    receipts.append(r_lift)

    # 3. Overlap gluing refusal on shared 2-complex (Phi_1([delta]) = 5/6 > 0)
    r_glue = hypergraph.run_coupled_trajectory(
        MultiAgentTransitionState(
            step_index=0,
            agent_reports=(0, 0),
            joint_internal_eval=0,
            remaining_budget=2,
            edge_cochain={(0, 1): Fraction(1, 2), (1, 2): Fraction(2, 3), (0, 2): Fraction(1, 3)},
        ),
        base_step,
    )
    assert r_glue.obstruction_kind == "OVERLAP_GLUING_REFUSAL"
    assert r_glue.phi1_holonomy == Fraction(5, 6) > 0
    assert "ok" in r_glue.eis_independence_verdict
    receipts.append(r_glue)

    # 4. Adversarial peer/self-critique observers must trigger TWO_SIGNAL_COLLAPSE in both Python and Rust
    for bad_observer in (
        "agent",
        "model",
        "llm",
        "detector",
        "matcher",
        "detector.hypergraph_rsi_scanner",
    ):
        r_bad = hypergraph.run_coupled_trajectory(
            MultiAgentTransitionState(
                step_index=0,
                agent_reports=(0, 0),
                joint_internal_eval=0,
                remaining_budget=2,
                edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
                signal2_observer_id=bad_observer,
            ),
            lambda s: MultiAgentTransitionState(
                step_index=s.step_index + 1,
                agent_reports=(0, 0),
                joint_internal_eval=0,
                remaining_budget=s.remaining_budget,
                edge_cochain=s.edge_cochain,
                signal2_observer_id=bad_observer,
            ),
        )
        assert "error" in r_bad.eis_independence_verdict
        assert r_bad.eis_independence_verdict["error"]["code"] == "TWO_SIGNAL_COLLAPSE"  # type: ignore[index]
        receipts.append(r_bad)

    summary = cross_check_receipts_against_rust_eis(receipts)
    assert summary["metadata_record_count"] == len(receipts)
    assert summary["rust_companion_executed"] is True
    assert summary["eis_fixture_vectors"] == 55
    assert summary["eis_digest_vectors"] == 7
