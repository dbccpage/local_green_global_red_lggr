# Claim Hygiene: AuthorityEffect: None
# Canonical Aggregator Test Suite for Paper 012 RSI Verification Gate.
# Re-exports all partitioned test suites across:
# 1. Lean 4 formalization, axioms, and theorem census (test_lean_formalization.py)
# 2. Single-agent finite-state transition graph horizon bounds (test_single_agent_transitions.py)
# 3. Multi-agent communicating hypergraph coupled co-adaptation (test_multi_agent_hypergraph.py)
# 4. Higher k-cell cochain complexes & async message delays (test_higher_cell_async.py)
# 5. Non-monotonic message channels & dynamic simplicial rewiring (test_non_monotonic_rewiring.py)
#
# Total tests re-exported: 79 items (100% preservation of original suite).
from __future__ import annotations

from pathlib import Path
import sys

TESTS_DIR = Path(__file__).resolve().parent
CODE_DIR = TESTS_DIR.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from test_lean_formalization import (
    test_adversarial_counterexample_blocked,
    test_carrier_lifting_and_inhabitation_theorems,
    test_claim_hygiene_in_formalization_and_comments,
    test_constructive_horizon_decoupling_theorems,
    test_interleaved_and_budgeted_lifting_theorems,
    test_rsi_impossible_lean_compilation_and_axioms,
    test_rsi_obstructions_formal_structure,
    test_zero_suppressed_or_unused_hypotheses_in_theorems,
)
from test_single_agent_transitions import (
    test_refusal_receipts_cross_checked_against_omega_epistemic_immune_system,
    test_transition_graph_lift_budget_exhaustion_within_horizon,
    test_transition_graph_overlap_gluing_refusal_phi1_positive,
    test_transition_graph_report_collision_within_horizon,
)
from test_multi_agent_hypergraph import (
    test_multi_agent_hypergraph_coupled_coadaptation_delays_but_cannot_evade_product_bound,
    test_multi_agent_hypergraph_lift_budget_exhaustion,
    test_multi_agent_hypergraph_overlap_gluing_refusal_phi1_positive,
    test_multi_agent_hypergraph_receipts_cross_checked_against_rust_eis,
    test_multi_agent_three_way_hypergraph_product_bound,
)
from test_higher_cell_async import (
    test_asynchronous_message_delay_buffer_fifo_semantics,
    test_higher_cell_async_delay_compensated_coadaptation_alters_step_within_product_bound,
    test_higher_cell_async_hypergraph_receipts_cross_checked_against_rust_eis,
    test_higher_cell_async_uncompensated_latency_induces_phi1_holonomy_refusal,
    test_higher_k_cell_cochain_complex_exactness_and_coboundary_holonomy,
)
from test_non_monotonic_rewiring import (
    test_dynamic_simplicial_rewiring_schedule_across_degrees,
    test_non_monotonic_delivery_and_dynamic_rewiring_shift_termination_distribution,
    test_non_monotonic_message_channel_packet_loss_and_out_of_order_permutations,
)

__all__ = [
    # 1. Lean 4 formalization
    "test_rsi_impossible_lean_compilation_and_axioms",
    "test_rsi_obstructions_formal_structure",
    "test_adversarial_counterexample_blocked",
    "test_interleaved_and_budgeted_lifting_theorems",
    "test_zero_suppressed_or_unused_hypotheses_in_theorems",
    "test_carrier_lifting_and_inhabitation_theorems",
    "test_constructive_horizon_decoupling_theorems",
    "test_claim_hygiene_in_formalization_and_comments",
    # 2. Single-agent transitions
    "test_transition_graph_report_collision_within_horizon",
    "test_transition_graph_lift_budget_exhaustion_within_horizon",
    "test_transition_graph_overlap_gluing_refusal_phi1_positive",
    "test_refusal_receipts_cross_checked_against_omega_epistemic_immune_system",
    # 3. Multi-agent hypergraph
    "test_multi_agent_hypergraph_coupled_coadaptation_delays_but_cannot_evade_product_bound",
    "test_multi_agent_three_way_hypergraph_product_bound",
    "test_multi_agent_hypergraph_overlap_gluing_refusal_phi1_positive",
    "test_multi_agent_hypergraph_lift_budget_exhaustion",
    "test_multi_agent_hypergraph_receipts_cross_checked_against_rust_eis",
    # 4. Higher cell async
    "test_higher_k_cell_cochain_complex_exactness_and_coboundary_holonomy",
    "test_asynchronous_message_delay_buffer_fifo_semantics",
    "test_higher_cell_async_delay_compensated_coadaptation_alters_step_within_product_bound",
    "test_higher_cell_async_uncompensated_latency_induces_phi1_holonomy_refusal",
    "test_higher_cell_async_hypergraph_receipts_cross_checked_against_rust_eis",
    # 5. Non-monotonic rewiring
    "test_non_monotonic_message_channel_packet_loss_and_out_of_order_permutations",
    "test_dynamic_simplicial_rewiring_schedule_across_degrees",
    "test_non_monotonic_delivery_and_dynamic_rewiring_shift_termination_distribution",
]
