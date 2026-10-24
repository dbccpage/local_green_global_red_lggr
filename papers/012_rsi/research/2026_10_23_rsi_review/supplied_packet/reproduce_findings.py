"""Read-only negative controls for RSI review at e15a9d4 (2026-10-23).

Usage: python reproduce_findings.py /path/to/000_relational_reasoning_and_rsi_impossibility
Requires the scientific dependencies already imported by the reviewed code,
and rustc on PATH. A confirmed finding is a reproduced defect, not a code pass.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path

source = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(source / "code"))

from simplicial_complex import (  # noqa: E402
    HigherCellComplex,
    build_exact_k_cochain_from_potential,
    compute_higher_cell_phi1_holonomy,
)
from exact_dual_witness_solver import solve_exact_rational_l1_dual_witness  # noqa: E402
import rsi_transition_harness as monolith  # noqa: E402
import single_agent_graph as modular  # noqa: E402
from higher_cell_async_hypergraph import (  # noqa: E402
    HigherCellAsyncCommunicatingHypergraph,
    HigherCellAsyncState,
    make_async_uncompensated_stale_cochain_step_fn,
)
from eis_verifier import cross_check_receipts_against_rust_eis, verify_signal_independence  # noqa: E402

findings: dict[str, object] = {}


def record(name: str, **evidence: object) -> None:
    findings[name] = evidence


def bad_closed_certificate() -> None:
    complex_k = HigherCellComplex.standard_simplex(1)
    potential = {(0,): F(0), (1,): F(1), (2,): F(2)}
    cochain = build_exact_k_cochain_from_potential(complex_k, potential)
    result = solve_exact_rational_l1_dual_witness(complex_k, cochain)
    reconstructed = build_exact_k_cochain_from_potential(complex_k, result.primal_potential)
    assert result.is_certified
    assert reconstructed != result.repaired_cochain
    record("false_primal_certificate", confirmed=True,
           phi1=str(compute_higher_cell_phi1_holonomy(complex_k, cochain)),
           returned_potential={str(k): str(v) for k, v in result.primal_potential.items()},
           returned_cochain={str(k): str(v) for k, v in result.repaired_cochain.items()},
           reconstructed_cochain={str(k): str(v) for k, v in reconstructed.items()})


def closed_nonexact_annulus() -> None:
    complex_k = HigherCellComplex(1, ((0, 1, 4), (0, 3, 4), (1, 2, 5),
                                       (1, 4, 5), (0, 2, 3), (2, 3, 5)))
    cochain = {edge: F(0) for edge in complex_k.required_k_cells()}
    for edge in ((0, 1), (1, 2), (3, 4), (4, 5), (0, 4), (1, 5), (2, 3)):
        cochain[edge] = F(1)
    for edge in ((0, 2), (3, 5)):
        cochain[edge] = F(-1)
    phi1 = compute_higher_cell_phi1_holonomy(complex_k, cochain)
    loop = cochain[(0, 1)] + cochain[(1, 2)] - cochain[(0, 2)]
    # Three edge-disjoint oriented loops give an exact dual certificate of
    # optimal distance 9; the zero potential attains cost 9.
    witness = {edge: F(0) for edge in cochain}
    for edge in ((0, 1), (1, 2), (3, 4), (4, 5), (0, 4), (1, 5), (2, 3)):
        witness[edge] = F(1)
    for edge in ((0, 2), (3, 5), (1, 4), (2, 5), (0, 3)):
        witness[edge] = F(-1)
    divergence = {vertex: F(0) for edge in cochain for vertex in edge}
    for (u, v), weight in witness.items():
        divergence[u] -= weight
        divergence[v] += weight
    assert all(value == 0 for value in divergence.values())
    assert all(abs(value) <= 1 for value in witness.values())
    exact_optimum = sum((witness[edge] * value for edge, value in cochain.items()), F(0))
    assert exact_optimum == sum((abs(value) for value in cochain.values()), F(0)) == 9
    result = solve_exact_rational_l1_dual_witness(complex_k, cochain)
    assert phi1 == 0 and loop == 3
    assert result.is_certified and result.l1_repair_cost == 0
    # Every exact vertex coboundary sums to zero on the outer 0-1-2-0 loop.
    record("closed_is_not_exact", confirmed=True, phi1=str(phi1),
           outer_loop_period=str(loop), claimed_optimal_cost=str(result.l1_repair_cost),
           independently_certified_optimal_cost=str(exact_optimum))


def implementation_drift() -> None:
    results = {}
    for module in (monolith, modular):
        graph = module.FiniteStateSelfModifyingGraph(4, 0)
        initial = module.TransitionState(0, 0, 0, 0)
        receipt = graph.run_trajectory(initial, lambda state: replace(
            state, step_index=state.step_index + 1,
            report_id=(state.report_id + 1) % 4, internal_eval=state.internal_eval + 1))
        results[module.__name__] = {"kind": receipt.obstruction_kind,
                                    "step": receipt.termination_step}
    assert results["rsi_transition_harness"]["kind"] == "REPORT_COLLISION"
    assert results["single_agent_graph"]["kind"] == "CAPACITY_THRESHOLD_EXCEEDED"
    record("two_implementations_disagree", confirmed=True, results=results)


def forged_receipt_passes_parity() -> None:
    graph = modular.FiniteStateSelfModifyingGraph(4, 0)
    original = graph.run_trajectory(modular.TransitionState(0, 0, 0, 0), lambda state: state)
    forged = replace(original, obstruction_kind="OVERLAP_GLUING_REFUSAL",
                     phi1_holonomy=F(0), colliding_prior_step=None)
    summary = cross_check_receipts_against_rust_eis([forged])
    assert summary["verified_receipt_count"] == 1
    record("parity_does_not_validate_obstruction", confirmed=True,
           forged_kind=forged.obstruction_kind, forged_phi1=str(forged.phi1_holonomy),
           rust_summary=summary)


def unicode_identity_breaks_parity() -> None:
    graph = modular.FiniteStateSelfModifyingGraph(4, 0)
    original = graph.run_trajectory(modular.TransitionState(0, 0, 0, 0), lambda state: state)
    vector = deepcopy(original.eis_vector)
    vector["context"]["detector_id"] = "ss"
    vector["danger"]["observer_id"] = "ß"
    verdict = verify_signal_independence(vector["matches"], vector["danger"], vector["context"])
    assert verdict["error"]["code"] == "TWO_SIGNAL_COLLAPSE"
    altered = replace(original, eis_vector=vector, eis_independence_verdict=verdict)
    try:
        cross_check_receipts_against_rust_eis([altered])
    except AssertionError as error:
        assert "Rust/Python EIS mismatch" in str(error)
        record("unicode_identity_breaks_python_rust_parity", confirmed=True,
               detector_id="ss", observer_id="ß", python_verdict="TWO_SIGNAL_COLLAPSE",
               rust_verdict="OK", mismatch=str(error))
    else:
        raise AssertionError("Expected Rust ASCII lowercase to disagree with Python casefold")


def repair_cost_can_credit_budget() -> None:
    complex_k = HigherCellComplex.standard_simplex(1)
    cochain = {edge: F(0) for edge in complex_k.required_k_cells()}
    cochain[(0, 1)] = F(1)

    def step(state):
        a, b = state.agent_states
        return ((a + (b == 2)) % 2, (b + 1) % 3), cochain

    graph = HigherCellAsyncCommunicatingHypergraph(
        agent_capacities=(2, 3), higher_complex=complex_k, latency_steps=0,
        initial_agent_states=(0, 0), initial_budget=1,
        initial_k_cochain=cochain, step_fn=step,
        enable_active_repair=True, repair_budget_cost_fn=lambda _: -1)
    receipt = graph.run()
    assert receipt.total_repair_budget_expended < 0
    assert receipt.remaining_budget > graph.initial_budget
    record("negative_repair_cost_mints_budget", confirmed=True,
           initial_budget=graph.initial_budget, remaining_budget=receipt.remaining_budget,
           total_repair_budget_expended=receipt.total_repair_budget_expended,
           termination_step=receipt.termination_step, kind=receipt.obstruction_kind)


def contextual_fraction_is_not_general_l1_half() -> None:
    # Exact certificate: two disjoint PR scenarios, eight distinct contexts.
    # Each PR box has CF=1 because no deterministic global assignment lies in
    # its support. Their disjoint union therefore also has CF=1.
    # For one scenario, uniform weight on the eight CHSH=2 assignments gives
    # an attainable L1 distance 2 to the PR box; CHSH gives the matching lower
    # bound. The two independent components give distance 4.
    assignments = list(product((0, 1), repeat=4))
    contexts = ((0, 2), (0, 3), (1, 2), (1, 3))
    signs = (1, 1, 1, -1)

    def score(assignment):
        return sum(sign * (1 if assignment[a] == assignment[b] else -1)
                   for (a, b), sign in zip(contexts, signs))

    local_support = [assignment for assignment in assignments if score(assignment) == 2]
    assert len(local_support) == 8
    assert all(score(assignment) <= 2 for assignment in assignments)
    model = {}
    local = {}
    for c, ((a, b), sign) in enumerate(zip(contexts, signs)):
        for x, y in product((0, 1), repeat=2):
            model[c, x, y] = F(1, 2) if (1 if x == y else -1) == sign else F(0)
            local[c, x, y] = F(sum(g[a] == x and g[b] == y for g in local_support), 8)
    one_distance = sum((abs(model[key] - local[key]) for key in model), F(0))
    assert one_distance == 2
    assert not any(all(model[c, g[a], g[b]] > 0 for c, (a, b) in enumerate(contexts))
                   for g in assignments)
    record("contextual_fraction_normalization_counterexample", confirmed=True,
           disjoint_PR_contexts=8, exact_phi_w=str(2 * one_distance), exact_CF="1",
           claimed_phi_w_over_2=str(one_distance))


def stale_defect_is_injected_for_equal_reports() -> None:
    complex_k = HigherCellComplex.standard_simplex(1)
    state = HigherCellAsyncState(
        step=1, agent_states=(0, 0), emitted_projections=(0, 0),
        delivered_projections=(0, 0), effective_lags=(1, 1),
        remaining_budget=10,
        k_cochain={edge: F(0) for edge in complex_k.required_k_cells()})
    step = make_async_uncompensated_stale_cochain_step_fn((2, 3), complex_k)
    _, cochain = step(state)
    phi1 = compute_higher_cell_phi1_holonomy(complex_k, cochain)
    assert phi1 == F(1, 6)
    record("equal_reports_receive_prescribed_stale_defect", confirmed=True,
           emitted_reports=list(state.emitted_projections),
           delivered_reports=list(state.delivered_projections),
           prescribed_phi1=str(phi1))


for probe in (bad_closed_certificate, closed_nonexact_annulus, implementation_drift,
              forged_receipt_passes_parity, unicode_identity_breaks_parity,
              repair_cost_can_credit_budget,
              contextual_fraction_is_not_general_l1_half,
              stale_defect_is_injected_for_equal_reports):
    probe()

print(json.dumps({"source": str(source), "revision": "e15a9d4ac6298524ce370cae679314aa0fef7585",
                  "meaning": "confirmed means a defect was reproduced",
                  "findings": findings}, indent=2, sort_keys=True))
