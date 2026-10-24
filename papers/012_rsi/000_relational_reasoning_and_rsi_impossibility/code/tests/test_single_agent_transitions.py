# Claim Hygiene: AuthorityEffect: None
# Tests verify single-agent finite-state self-modifying transition graph horizon bounds
# (k <= N + 1), licensed carrier lift budget exhaustion, overlap gluing refusal (Phi_1 > 0),
# and refusal receipt cross-checks against omega_epistemic_immune_system.
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = PACKAGE_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from single_agent_graph import (  # noqa: E402
    FiniteStateSelfModifyingGraph,
    ObstructionReceipt,
    TransitionState,
    compute_d1_triangle,
    compute_phi1_holonomy,
)
from eis_verifier import (  # noqa: E402
    cross_check_receipts_against_rust_eis,
)


@pytest.mark.parametrize("carrier_n", [1, 2, 3, 5, 8, 13])
def test_transition_graph_report_collision_within_horizon(carrier_n: int) -> None:
    """Verify that finite-state self-modifying transition graphs hit REPORT_COLLISION at step k <= N + 1."""
    graph = FiniteStateSelfModifyingGraph(carrier_capacity=carrier_n, initial_lift_budget=0)

    # 1. Full cyclic traversal: visits 0, 1, ..., N-1, then collides at step k = N <= N + 1
    init_state = TransitionState(step_index=0, report_id=0, internal_eval=0, remaining_budget=0)
    receipt = graph.run_trajectory(
        init_state,
        lambda s: TransitionState(
            step_index=s.step_index + 1,
            report_id=(s.report_id + 1) % carrier_n,
            internal_eval=(s.internal_eval + 1) % carrier_n,
            remaining_budget=s.remaining_budget,
        ),
    )
    assert receipt.halted is True
    assert receipt.obstruction_kind == "REPORT_COLLISION"
    assert receipt.termination_step == carrier_n
    assert receipt.termination_step <= carrier_n + 1
    assert receipt.colliding_prior_step == 0
    assert "ok" in receipt.eis_independence_verdict

    # 2. Early collision: fixed-point attractor collides at step k = 1 <= N + 1
    fixed_receipt = graph.run_trajectory(
        init_state,
        lambda s: TransitionState(
            step_index=s.step_index + 1,
            report_id=0,
            internal_eval=0,
            remaining_budget=s.remaining_budget,
        ),
    )
    assert fixed_receipt.halted is True
    assert fixed_receipt.obstruction_kind == "REPORT_COLLISION"
    assert fixed_receipt.termination_step == 1
    assert fixed_receipt.termination_step <= carrier_n + 1
    assert fixed_receipt.colliding_prior_step == 0


@pytest.mark.parametrize(
    "carrier_n,initial_budget,interleave_stride",
    [
        (5, 0, 1),
        (5, 1, 1),
        (6, 2, 1),
        (8, 3, 2),
        (10, 4, 2),
    ],
)
def test_transition_graph_lift_budget_exhaustion_within_horizon(
    carrier_n: int, initial_budget: int, interleave_stride: int
) -> None:
    """Verify that licensed carrier lift trajectories hit LIFT_BUDGET_EXHAUSTION (budget = 0) at k <= N + 1."""
    graph = FiniteStateSelfModifyingGraph(
        carrier_capacity=carrier_n, initial_lift_budget=initial_budget
    )
    init_state = TransitionState(
        step_index=0,
        report_id=0,
        internal_eval=0,
        remaining_budget=initial_budget,
        requests_carrier_lift=True,
    )

    def _step(s: TransitionState) -> TransitionState:
        next_k = s.step_index + 1
        requests_lift = (next_k % interleave_stride) == 0
        return TransitionState(
            step_index=next_k,
            report_id=next_k % carrier_n,
            internal_eval=next_k % carrier_n,
            remaining_budget=s.remaining_budget,
            requests_carrier_lift=requests_lift,
        )

    receipt = graph.run_trajectory(init_state, _step)
    assert receipt.halted is True
    assert receipt.obstruction_kind == "LIFT_BUDGET_EXHAUSTION"
    assert receipt.remaining_budget == 0
    expected_step = initial_budget * interleave_stride
    assert receipt.termination_step == expected_step
    assert receipt.termination_step <= carrier_n + 1
    assert receipt.eis_vector["danger"]["danger_type"] == "MANIFEST_CONTAMINATION"  # type: ignore[index]


@pytest.mark.parametrize("defect_step", [0, 1, 3, 5])
def test_transition_graph_overlap_gluing_refusal_phi1_positive(defect_step: int) -> None:
    """Verify that non-exact 1-cochain overlap modifications (Phi_1([delta]) > 0) refuse sheaf gluing at step k <= N + 1."""
    carrier_n = 6
    triangles = ((0, 1, 2), (0, 2, 3))
    graph = FiniteStateSelfModifyingGraph(
        carrier_capacity=carrier_n,
        initial_lift_budget=2,
        triangles=triangles,
    )

    # Exact 0-coboundary d^0(alpha) has Phi_1 = 0
    alpha = {0: Fraction(1, 5), 1: Fraction(4, 5), 2: Fraction(2, 5), 3: Fraction(7, 5)}
    exact_cochain = {
        (u, v): alpha[v] - alpha[u]
        for u in range(4)
        for v in range(u + 1, 4)
    }
    assert compute_phi1_holonomy(exact_cochain, triangles) == Fraction(0, 1)

    # Non-exact 1-cochain with holonomy 2/3 on (0,1,2) and 1/4 on (0,2,3) -> Phi_1 = 11/12 > 0
    non_exact_cochain = dict(exact_cochain)
    non_exact_cochain[(0, 1)] += Fraction(2, 3)
    non_exact_cochain[(2, 3)] += Fraction(1, 4)
    expected_phi1 = Fraction(2, 3) + Fraction(1, 4)
    assert compute_d1_triangle(non_exact_cochain, 0, 1, 2) == Fraction(2, 3)
    assert compute_d1_triangle(non_exact_cochain, 0, 2, 3) == Fraction(1, 4)
    assert compute_phi1_holonomy(non_exact_cochain, triangles) == expected_phi1

    init_cochain = non_exact_cochain if defect_step == 0 else exact_cochain
    init_state = TransitionState(
        step_index=0,
        report_id=0,
        internal_eval=0,
        remaining_budget=2,
        edge_cochain=init_cochain,
    )

    def _step(s: TransitionState) -> TransitionState:
        next_k = s.step_index + 1
        cochain = non_exact_cochain if next_k == defect_step else exact_cochain
        return TransitionState(
            step_index=next_k,
            report_id=next_k % carrier_n,
            internal_eval=next_k % carrier_n,
            remaining_budget=s.remaining_budget,
            edge_cochain=cochain,
        )

    receipt = graph.run_trajectory(init_state, _step)
    assert receipt.halted is True
    assert receipt.obstruction_kind == "OVERLAP_GLUING_REFUSAL"
    assert receipt.termination_step == defect_step
    assert receipt.termination_step <= carrier_n + 1
    assert receipt.phi1_holonomy == expected_phi1
    assert receipt.phi1_holonomy > Fraction(0, 1)
    assert receipt.eis_vector["danger"]["danger_type"] == "PROTECTED_FIELD_VIOLATION"  # type: ignore[index]


def test_refusal_receipts_cross_checked_against_omega_epistemic_immune_system() -> None:
    """Cross-check all emitted transition-graph refusal receipts against Rust `omega_epistemic_immune_system`."""
    receipts: list[ObstructionReceipt] = []

    # 1. Host-corroborated REPORT_COLLISION receipt
    g_col = FiniteStateSelfModifyingGraph(carrier_capacity=4, initial_lift_budget=0)
    r_col = g_col.run_trajectory(
        TransitionState(step_index=0, report_id=0, internal_eval=0, remaining_budget=0),
        lambda s: TransitionState(
            step_index=s.step_index + 1,
            report_id=(s.report_id + 1) % 4,
            internal_eval=(s.internal_eval + 1) % 4,
            remaining_budget=0,
            signal2_observer_id="host.rsi_obstruction_gate",
        ),
    )
    assert r_col.obstruction_kind == "REPORT_COLLISION"
    assert r_col.termination_step == 4 <= 4 + 1
    assert "ok" in r_col.eis_independence_verdict
    receipts.append(r_col)

    # 2. Host-corroborated LIFT_BUDGET_EXHAUSTION receipt
    g_lift = FiniteStateSelfModifyingGraph(carrier_capacity=5, initial_lift_budget=2)
    r_lift = g_lift.run_trajectory(
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
            signal2_observer_id="host.lift_budget_auditor",
        ),
    )
    assert r_lift.obstruction_kind == "LIFT_BUDGET_EXHAUSTION"
    assert r_lift.termination_step == 2 <= 5 + 1
    assert "ok" in r_lift.eis_independence_verdict
    receipts.append(r_lift)

    # 3. Host-corroborated OVERLAP_GLUING_REFUSAL receipt (Phi_1([delta]) > 0)
    g_glue = FiniteStateSelfModifyingGraph(carrier_capacity=4, initial_lift_budget=1)
    r_glue = g_glue.run_trajectory(
        TransitionState(
            step_index=0,
            report_id=0,
            internal_eval=0,
            remaining_budget=1,
            edge_cochain={(0, 1): Fraction(1, 2), (1, 2): Fraction(1, 2), (0, 2): Fraction(1, 4)},
            signal2_observer_id="host.sheaf_holonomy_gate",
        ),
        lambda s: s,
    )
    assert r_glue.obstruction_kind == "OVERLAP_GLUING_REFUSAL"
    assert r_glue.phi1_holonomy == Fraction(3, 4) > 0
    assert "ok" in r_glue.eis_independence_verdict
    receipts.append(r_glue)

    # 4. Adversarial self-certifying / self-critique observers must trigger TWO_SIGNAL_COLLAPSE
    for bad_observer in ("agent", "model", "llm", "detector", "matcher", "detector.rsi_claim_scanner"):
        r_self = g_col.run_trajectory(
            TransitionState(
                step_index=0,
                report_id=0,
                internal_eval=0,
                remaining_budget=0,
                signal2_observer_id=bad_observer,
            ),
            lambda s: TransitionState(
                step_index=s.step_index + 1,
                report_id=0,
                internal_eval=0,
                remaining_budget=0,
                signal2_observer_id=bad_observer,
            ),
        )
        assert "error" in r_self.eis_independence_verdict
        err = r_self.eis_independence_verdict["error"]
        assert isinstance(err, dict)
        assert err["code"] == "TWO_SIGNAL_COLLAPSE"
        receipts.append(r_self)

    # Cross-check all 9 dynamic receipts + 55 EIS fixture vectors + 7 digest vectors against compiled Rust companion
    summary = cross_check_receipts_against_rust_eis(receipts)
    assert summary["metadata_record_count"] == len(receipts)
    assert summary["rust_companion_executed"] is True
    assert summary["eis_fixture_vectors"] == 55
    assert summary["eis_digest_vectors"] == 7
