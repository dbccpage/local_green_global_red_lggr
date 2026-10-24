"""Compatibility exports and CLI for the modular finite-report experiments.

The Rust companion checks EIS metadata and digests, not obstruction truth.
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction

from single_agent_graph import (
    TransitionState,
    ObstructionReceipt,
    compute_d1_triangle,
    compute_phi1_holonomy,
    FiniteStateSelfModifyingGraph
)

from multi_agent_hypergraph import (
    HypergraphAgentSpec,
    SharedTwoComplex,
    MultiAgentTransitionState,
    HypergraphObstructionReceipt,
    compute_hypergraph_phi1_holonomy,
    build_flat_shared_cochain,
    coupled_odometer_step_fn,
    uncoupled_parallel_step_fn,
    MultiAgentCommunicatingHypergraph
)

from simplicial_complex import (
    HigherCellComplex,
    compute_dk_coboundary,
    build_exact_k_cochain_from_potential,
    compute_higher_cell_phi1_holonomy
)

from communication_channels import (
    AsynchronousMessageDelayBuffer,
    NonMonotonicMessageChannel
)

from simplicial_rewiring import (
    DynamicSimplicialRewiringSchedule
)

from higher_cell_async_hypergraph import (
    HigherCellAsyncState,
    HigherCellObstructionReceipt,
    HigherCellAsyncCommunicatingHypergraph,
    run_multi_epoch_lexicographical_descent,
    make_async_delay_compensated_step_fn,
    make_async_uncompensated_stale_cochain_step_fn,
    make_non_monotonic_rewiring_step_fn,
    evaluate_termination_distribution_under_non_monotonic_rewiring
)

from eis_verifier import (
    compute_signal1_digest,
    verify_signal_independence,
    verify_bundled_eis_fixture,
    cross_check_eis_metadata_against_rust,
    cross_check_receipts_against_rust_eis
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point running single-agent, 2-complex, and higher k-cell async/non-monotonic/rewired hypergraph scenarios."""
    parser = argparse.ArgumentParser(
        description="Execute finite-state self-modifying transition graphs, shared 2-complexes, and higher k-cell async/non-monotonic/rewired hypergraphs with EIS cross-checking."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary.",
    )
    args = parser.parse_args(argv)

    # 1. Single-agent report collision at k = N (with N = 4, budget = 0)
    g_collision = FiniteStateSelfModifyingGraph(carrier_capacity=4, initial_lift_budget=0)
    r_collision = g_collision.run_trajectory(
        TransitionState(step_index=0, report_id=0, internal_eval=0, remaining_budget=0),
        lambda s: TransitionState(
            step_index=s.step_index + 1,
            report_id=(s.report_id + 1) % 4,
            internal_eval=(s.internal_eval + 1) % 4,
            remaining_budget=s.remaining_budget,
        ),
    )

    # 2. Single-agent lift-budget exhaustion at k = 2 <= N + 1 (with N = 5, budget = 2)
    g_budget = FiniteStateSelfModifyingGraph(carrier_capacity=5, initial_lift_budget=2)
    r_budget = g_budget.run_trajectory(
        TransitionState(
            step_index=0,
            report_id=0,
            internal_eval=0,
            remaining_budget=2,
            requests_carrier_lift=True,
        ),
        lambda s: TransitionState(
            step_index=s.step_index + 1,
            report_id=(s.report_id + 1) % 5,
            internal_eval=(s.internal_eval + 1) % 5,
            remaining_budget=s.remaining_budget,
            requests_carrier_lift=True,
        ),
    )

    # 3. Single-agent overlap gluing refusal (Phi_1([delta]) = 3/4 > 0 at step k = 0 <= N + 1)
    g_holonomy = FiniteStateSelfModifyingGraph(carrier_capacity=4, initial_lift_budget=1)
    r_holonomy = g_holonomy.run_trajectory(
        TransitionState(
            step_index=0,
            report_id=0,
            internal_eval=0,
            remaining_budget=1,
            edge_cochain={(0, 1): Fraction(1, 2), (1, 2): Fraction(1, 2), (0, 2): Fraction(1, 4)},
        ),
        lambda s: s,
    )

    # 4. Multi-agent coupled co-adaptation on SharedTwoComplex delaying termination to k = N_A * N_B = 12
    shared_complex = SharedTwoComplex()
    hg_delayed = MultiAgentCommunicatingHypergraph(
        agents=(
            HypergraphAgentSpec("agent_A", 3),
            HypergraphAgentSpec("agent_B", 4),
        ),
        initial_lift_budget=2,
        shared_complex=shared_complex,
    )
    r_hg_delayed = hg_delayed.run_coupled_trajectory(
        MultiAgentTransitionState(
            step_index=0,
            agent_reports=(0, 0),
            joint_internal_eval=0,
            remaining_budget=2,
            edge_cochain=build_flat_shared_cochain((0, 0), shared_complex),
        ),
        coupled_odometer_step_fn((3, 4), shared_complex),
    )

    # 5. Multi-agent shared 2-complex overlap gluing refusal at step k = 0 <= N_A * N_B + 1
    r_hg_gluing = hg_delayed.run_coupled_trajectory(
        MultiAgentTransitionState(
            step_index=0,
            agent_reports=(0, 0),
            joint_internal_eval=0,
            remaining_budget=2,
            edge_cochain={(0, 1): Fraction(1, 2), (1, 2): Fraction(2, 3), (0, 2): Fraction(1, 3)},
        ),
        coupled_odometer_step_fn((3, 4), shared_complex),
    )

    # 6. Higher k-cell (degree k=2, C^2 --d^2--> C^3) async hypergraph with delay-compensated co-adaptation (tau=2)
    higher_c2 = HigherCellComplex.standard_simplex(degree=2, num_cells=1)
    zero_c2 = {face: Fraction(0, 1) for face in higher_c2.required_k_cells()}
    hg_higher_compensated = HigherCellAsyncCommunicatingHypergraph(
        agent_capacities=(3, 4),
        higher_complex=higher_c2,
        latency_steps=2,
        initial_agent_states=(0, 0),
        initial_budget=20,
        initial_k_cochain=zero_c2,
        step_fn=make_async_delay_compensated_step_fn((3, 4), higher_c2),
    )
    r_higher_compensated = hg_higher_compensated.run()

    # 7. Higher k-cell (degree k=3, C^3 --d^3--> C^4) async hypergraph with uncompensated stale-cochain defect (tau=2)
    higher_c3 = HigherCellComplex.standard_simplex(degree=3, num_cells=1)
    zero_c3 = {face: Fraction(0, 1) for face in higher_c3.required_k_cells()}
    hg_higher_stale = HigherCellAsyncCommunicatingHypergraph(
        agent_capacities=(3, 4),
        higher_complex=higher_c3,
        latency_steps=2,
        initial_agent_states=(0, 0),
        initial_budget=20,
        initial_k_cochain=zero_c3,
        step_fn=make_async_uncompensated_stale_cochain_step_fn(
            (3, 4), higher_c3, defect_trigger_step=2
        ),
    )
    r_higher_stale = hg_higher_stale.run()

    # 8. Non-monotonic channel (packet-loss + out-of-order permutation) and dynamic simplicial rewiring ensemble
    dist_eval = evaluate_termination_distribution_under_non_monotonic_rewiring(
        agent_capacities=(3, 4),
        cochain_degree=2,
        initial_budget=20,
    )

    all_receipts: list[
        ObstructionReceipt | HypergraphObstructionReceipt | HigherCellObstructionReceipt
    ] = [
        r_collision,
        r_budget,
        r_holonomy,
        r_hg_delayed,
        r_hg_gluing,
        r_higher_compensated,
        r_higher_stale,
    ]
    cross_check = cross_check_eis_metadata_against_rust(all_receipts)

    summary = {
        "single_agent_count": 3,
        "multi_agent_hypergraph_count": 2,
        "higher_cell_async_scenarios": [
            r_higher_compensated.to_json_dict(),
            r_higher_stale.to_json_dict(),
        ],
        "non_monotonic_rewiring_distribution": dist_eval,
        "eis_cross_check": cross_check,
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            f"[OK] Metadata parity for {len(all_receipts)} core records + {dist_eval['total_ensemble_runs']} "
            f"non-monotonic/rewired ensemble runs under the synthetic fixture policy; Rust EIS metadata companion "
            f"(distribution_shift_verified={dist_eval['distribution_shift_verified']})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
