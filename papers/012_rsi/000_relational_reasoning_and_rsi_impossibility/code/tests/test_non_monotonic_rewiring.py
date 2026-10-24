# Claim Hygiene: AuthorityEffect: None
# Tests verify non-monotonic message channels (packet loss, out-of-order permutations, causality),
# dynamic simplicial rewiring schedules across degrees k in {1, 2, 3}, and termination distribution
# shifts under Rust omega_epistemic_immune_system verification.
from __future__ import annotations

from pathlib import Path
import sys

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = PACKAGE_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from communication_channels import NonMonotonicMessageChannel  # noqa: E402
from simplicial_rewiring import DynamicSimplicialRewiringSchedule  # noqa: E402
from higher_cell_async_hypergraph import (  # noqa: E402
    evaluate_termination_distribution_under_non_monotonic_rewiring,
)


def test_non_monotonic_message_channel_packet_loss_and_out_of_order_permutations() -> None:
    """Verify `NonMonotonicMessageChannel` supports packet-loss hold-last-delivered semantics,
    non-FIFO out-of-order message permutations (`sigma_a(k_2) < sigma_a(k_1)`), and enforces
    causality (`0 <= sigma_a(k) <= k`)."""
    channel = NonMonotonicMessageChannel(
        num_agents=2,
        latency_steps=0,
        dropped_steps_per_agent={0: {2}},
        permutation_schedule_per_agent={1: {2: 2, 3: 1}},
    )
    assert channel.channel_mode == "packet_loss+out_of_order"

    emitted_seq = [(10, 100), (11, 101), (12, 102), (13, 103)]
    delivered_trace: list[tuple[int, ...]] = []
    source_trace: list[tuple[int, ...]] = []
    non_mono_flags: list[bool] = []

    for step, emitted in enumerate(emitted_seq):
        delivered, lags, src_steps, is_non_mono = channel.record_and_deliver_detailed(
            step, emitted
        )
        delivered_trace.append(delivered)
        source_trace.append(src_steps)
        non_mono_flags.append(is_non_mono)
        assert all(0 <= s <= step for s in src_steps)
        assert all(lag == step - s for lag, s in zip(lags, src_steps))

    assert source_trace == [(0, 0), (1, 1), (1, 2), (3, 1)]
    assert delivered_trace == [(10, 100), (11, 101), (11, 102), (13, 101)]
    assert non_mono_flags == [False, False, True, True]
    assert channel.non_monotonic_inversion_count == 2

    with pytest.raises(ValueError, match="Causal delivery violation"):
        NonMonotonicMessageChannel(
            num_agents=2,
            permutation_schedule_per_agent={0: {1: 2}},
        )


@pytest.mark.parametrize("degree", [1, 2, 3])
def test_dynamic_simplicial_rewiring_schedule_across_degrees(degree: int) -> None:
    """Verify `DynamicSimplicialRewiringSchedule` cycles across distinct `(k+1)`-complexes
    `C^k(X_t) --d_t^k--> C^{k+1}(X_t)` and detects topological rewiring transitions."""
    schedule = DynamicSimplicialRewiringSchedule.standard_rewiring_cycle(
        degree=degree, num_topologies=3, cells_per_topology=2
    )
    assert schedule.degree == degree
    c0 = schedule.complex_at(0)
    c1 = schedule.complex_at(1)
    c2 = schedule.complex_at(2)
    c3 = schedule.complex_at(3)
    assert c0.k_plus_1_cells != c1.k_plus_1_cells
    assert c1.k_plus_1_cells != c2.k_plus_1_cells
    assert c0.k_plus_1_cells == c3.k_plus_1_cells
    assert schedule.is_rewired_at(0) is False
    assert schedule.is_rewired_at(1) is True
    assert schedule.is_rewired_at(2) is True
    assert schedule.is_rewired_at(3) is True


@pytest.mark.parametrize("degree", [1, 2, 3])
def test_non_monotonic_delivery_and_dynamic_rewiring_shift_termination_distribution(
    degree: int,
) -> None:
    """Verify that packet-loss channels, non-FIFO out-of-order message permutations, and
    dynamic simplicial topology rewiring across `C^k --d^k--> C^{k+1}` shift the distribution
    of `OVERLAP_GLUING_REFUSAL` vs. `REPORT_COLLISION` termination steps while strictly
    obeying `k* <= N_A * N_B + 1` and passing Rust `omega_epistemic_immune_system` verification."""
    dist = evaluate_termination_distribution_under_non_monotonic_rewiring(
        agent_capacities=(3, 4),
        cochain_degree=degree,
        initial_budget=20,
    )
    assert dist["cochain_degree"] == degree
    assert dist["product_carrier_capacity"] == 12
    assert dist["horizon_bound"] == 13
    assert dist["total_ensemble_runs"] == 16
    assert dist["distribution_shift_verified"] is True

    regimes = dist["regimes"]
    fifo_reg = regimes["monotonic_fifo_static"]
    assert fifo_reg["counts"]["REPORT_COLLISION"] == 4
    assert fifo_reg["counts"]["OVERLAP_GLUING_REFUSAL"] == 0
    assert fifo_reg["all_within_product_horizon"] is True

    loss_reg = regimes["packet_loss_static"]
    assert loss_reg["counts"]["OVERLAP_GLUING_REFUSAL"] == 4
    assert loss_reg["counts"]["REPORT_COLLISION"] == 0
    assert loss_reg["termination_steps"] == [2, 3, 4, 5]
    assert loss_reg["all_within_product_horizon"] is True

    perm_reg = regimes["out_of_order_permutation_static"]
    assert perm_reg["counts"]["OVERLAP_GLUING_REFUSAL"] == 4
    assert perm_reg["counts"]["REPORT_COLLISION"] == 0
    assert perm_reg["termination_steps"] == [3, 4, 5, 6]
    assert perm_reg["all_within_product_horizon"] is True

    rew_reg = regimes["dynamic_simplicial_rewiring"]
    assert rew_reg["counts"]["REPORT_COLLISION"] == 2
    assert rew_reg["counts"]["OVERLAP_GLUING_REFUSAL"] == 2
    assert rew_reg["all_within_product_horizon"] is True

    eis_check = dist["eis_cross_check"]
    assert eis_check["metadata_record_count"] == 16
    assert eis_check["rust_companion_executed"] is True
