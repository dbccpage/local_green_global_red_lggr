"""Unit tests for Observer-Robust Control of Obstruction Diagnostics."""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_observer_robust_control_core import (
    ObserverBundle,
    ObserverModel,
    ObserverRobustController,
)


def test_observer_robust_criterion():
    """Verify that controller admits transition satisfying descent across all observers."""
    obs_a = ObserverModel(name="Observer_A", weights=(1.0, 1.0, 1.0))
    obs_b = ObserverModel(name="Observer_B", weights=(2.0, 0.5, 1.0))
    bundle = ObserverBundle.create([obs_a, obs_b])
    controller = ObserverRobustController(bundle, r_max=1.0)

    curr_res = [2.0, 2.0, 2.0]  # A: 6.0, B: 7.0
    curr_bnd = [0.5, 0.5, 0.5]

    next_res = [1.0, 1.0, 1.0]  # A: 3.0, B: 3.5 (decreased for both!)
    next_bnd = [0.2, 0.2, 0.2]  # low curvature, R_cl valid

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_good", next_res, next_bnd, 1.0)]
    )

    assert verdict.status == "Admitted"
    assert verdict.selected_operator == "Pi_good"
    assert verdict.worst_case_phi_1 == 3.5


def test_single_observer_spoofing_rejected():
    """Verify that a proposal that improves Observer A but worsens Observer B is caught and rejected using positive weights."""
    # Observers have strictly positive weights (Definition 2.1)
    obs_a = ObserverModel(name="Observer_A", weights=(10.0, 0.05, 0.05))  # dominant on coord 0
    obs_b = ObserverModel(name="Observer_B", weights=(0.05, 5.0, 5.0))    # dominant on coords 1 and 2
    bundle = ObserverBundle.create([obs_a, obs_b])
    controller = ObserverRobustController(bundle, r_max=1.0)

    curr_res = [3.0, 1.0, 1.0]  # A: 30.1, B: 10.15
    curr_bnd = [0.1, 0.1, 0.1]

    # Spoofing proposal: zeroes coord 0 (drastically lowers A to 0.4), but inflates coords 1 and 2 to 4.0 (balloons B to 40.0)
    spoof_res = [0.0, 4.0, 4.0]
    spoof_bnd = [0.1, 0.1, 0.1]

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_spoof", spoof_res, spoof_bnd, 0.1)]
    )

    # Must be rejected because Observer B suffered descent violation (10.15 -> 40.0)
    assert verdict.status == "RefusedStalled"
    assert verdict.selected_operator is None


def test_worst_case_boundedness():
    """Verify enforcement of worst-case residual bound M_max under multi-observer bundle."""
    obs = ObserverModel(name="O_test", weights=(1.0, 1.0))
    bundle = ObserverBundle.create([obs])

    # Controller with M_max = 50.0
    controller = ObserverRobustController(bundle, r_max=1.0, m_max=50.0)

    # Transition 1001 -> 1000 satisfies descent, but next residual 2000.0 exceeds M_max (50.0)
    curr_res = [501.0, 500.0]  # Phi_1 = 1001.0
    next_res = [500.0, 500.0]  # Phi_1 = 1000.0 > M_max
    curr_bnd = [1.0, 1.0]
    next_bnd = [1.0, 1.0]

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_over_mmax", next_res, next_bnd, 1.0)]
    )
    assert verdict.status == "RefusedStalled"

    # Transition descending below M_max is admitted
    admissible_res = [20.0, 20.0]  # Phi_1 = 40.0 <= M_max
    verdict_ok = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_under_mmax", admissible_res, next_bnd, 1.0)]
    )
    assert verdict_ok.status == "Admitted"
    assert verdict_ok.selected_operator == "Pi_under_mmax"


def test_cochain_quotient_minimization_triangle():
    """Verify that exact cochain (1, 1, -2) = d_0 alpha evaluates to Phi_1 = 0 on an oriented triangle."""
    # Oriented triangle: 3 vertices, 3 edges
    # e0 = v1 - v0, e1 = v2 - v1, e2 = v0 - v2
    d0 = (
        (-1.0,  1.0,  0.0),
        ( 0.0, -1.0,  1.0),
        ( 1.0,  0.0, -1.0),
    )
    obs = ObserverModel(name="O_tri", weights=(1.0, 1.0, 1.0), d0=d0)

    # Exact cochain alpha = (0, 1, 3) -> d0 alpha = (1, 2, -3)
    # alpha = (0, 1, 2) -> d0 alpha = (1, 1, -2)
    exact_cochain = [1.0, 1.0, -2.0]
    phi = obs.evaluate_phi_1(exact_cochain)
    assert math.isclose(phi, 0.0, abs_tol=1e-7)

    # Non-exact cycle (1, 1, 1) has minimal quotient norm 3.0
    cycle_cochain = [1.0, 1.0, 1.0]
    phi_cycle = obs.evaluate_phi_1(cycle_cochain)
    assert math.isclose(phi_cycle, 3.0, abs_tol=1e-7)


def test_dimension_separation_edges_and_faces():
    """Verify that C^1 (3 edges) and C^2 (1 face) with different dimensions evaluate without shape error."""
    # 3 edges, 1 face
    d1 = ((1.0, 1.0, 1.0),)  # 1 face boundary map
    obs = ObserverModel(
        name="O_complex",
        weights=(1.0, 1.0, 1.0),       # 3 edges
        boundary_weights=(2.0,),        # 1 face
        d1=d1,
    )

    # Passing 1-cochain of length 3 to evaluate_gamma_2 computes |d1 omega| under boundary_weights
    exact_cochain = [1.0, 1.0, -2.0]  # sum is 0 -> d1 omega = 0
    gamma = obs.evaluate_gamma_2(exact_cochain)
    assert math.isclose(gamma, 0.0, abs_tol=1e-9)

    # Explicit 1-coordinate boundary vector evaluated under boundary_weights
    gamma_explicit = obs.evaluate_gamma_2([3.0])
    assert math.isclose(gamma_explicit, 6.0, abs_tol=1e-9)


def test_absolute_curvature_guardrail_prevents_tearing():
    """Verify that transition (99, 1) -> (0, 50) is rejected by absolute curvature bound despite satisfying R_cl."""
    obs = ObserverModel(name="O_tear", weights=(1.0, 1.0))
    bundle = ObserverBundle.create([obs])

    # Guardrail with delta_gamma_max = 10.0 (prevents curvature jumps > 10.0)
    controller = ObserverRobustController(bundle, r_max=1.0, delta_gamma_max=10.0)

    # curr: Phi_1 = 99 + 1 = 100, Gamma_2 = 1.0, R_cl = 0.01
    curr_res = [99.0, 1.0]
    curr_bnd = [0.5, 0.5]  # Gamma_2 = 1.0

    # next: Phi_1 = 0 + 50 = 50, Gamma_2 = 50.0, R_cl = 50/50 = 1.0 <= r_max!
    # But Gamma_2 jumps from 1.0 to 50.0 (+49.0 > delta_gamma_max)!
    next_res = [0.0, 50.0]
    next_bnd = [25.0, 25.0]  # Gamma_2 = 50.0

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_tear", next_res, next_bnd, 1.0)]
    )

    assert verdict.status == "RefusedStalled"
    assert verdict.selected_operator is None


def test_routing_score_favors_lower_closure_ratio():
    """Verify that routing score L selects candidate with R_cl = 0 over candidate with R_cl = 1 when Phi_1 and cost are identical."""
    obs = ObserverModel(name="O_score", weights=(1.0, 1.0))
    bundle = ObserverBundle.create([obs])
    controller = ObserverRobustController(bundle, r_max=2.0, lam=1.0)

    curr_res = [5.0, 5.0]
    curr_bnd = [1.0, 1.0]

    # Both candidates lower Phi_1 to 4.0 with equal cost 1.0
    cand_high_rcl = ("Pi_high_rcl", [2.0, 2.0], [2.0, 2.0], 1.0)  # Gamma_2 = 4.0, R_cl = 1.0
    cand_zero_rcl = ("Pi_zero_rcl", [2.0, 2.0], [0.0, 0.0], 1.0)  # Gamma_2 = 0.0, R_cl = 0.0

    verdict = controller.evaluate_transition(curr_res, curr_bnd, [cand_high_rcl, cand_zero_rcl])
    assert verdict.status == "Admitted"
    # cand_zero_rcl must be chosen due to lower R_cl penalty in L
    assert verdict.selected_operator == "Pi_zero_rcl"


def test_uniform_descent_law():
    """Verify that worst-case residual is minimized among valid proposals."""
    obs_1 = ObserverModel(name="O1", weights=(1.0, 1.0))
    obs_2 = ObserverModel(name="O2", weights=(1.5, 0.5))
    bundle = ObserverBundle.create([obs_1, obs_2])
    controller = ObserverRobustController(bundle, r_max=1.0)

    curr_res = [4.0, 4.0]  # O1: 8.0, O2: 8.0
    curr_bnd = [0.5, 0.5]

    cand_1 = ("Pi_balanced", [2.0, 2.0], [0.1, 0.1], 1.0)
    cand_2 = ("Pi_skewed", [3.0, 1.0], [0.1, 0.1], 1.0)

    verdict = controller.evaluate_transition(curr_res, curr_bnd, [cand_2, cand_1])
    assert verdict.status == "Admitted"
    assert verdict.selected_operator == "Pi_balanced"
    assert verdict.worst_case_phi_1 == 4.0


def test_bundle_wide_refusal():
    """Verify that when no proposals satisfy all observers, a clean refusal is emitted."""
    obs_a = ObserverModel(name="A", weights=(1.0, 1.0))
    bundle = ObserverBundle.create([obs_a])
    controller = ObserverRobustController(bundle, r_max=0.5)

    curr_res = [2.0, 2.0]  # Phi_1 = 4.0
    curr_bnd = [0.5, 0.5]

    bad_rcl_res = [1.0, 1.0]  # Phi_1 = 2.0
    bad_rcl_bnd = [1.0, 1.0]  # Gamma_2 = 2.0 => R_cl = 1.0 > r_max (0.5)

    verdict = controller.evaluate_transition(curr_res, curr_bnd, [("Pi_tearing", bad_rcl_res, bad_rcl_bnd, 0.5)])
    assert verdict.status == "RefusedStalled"
    assert verdict.selected_operator is None


def test_shape_mismatch_is_refused_not_truncated():
    """A residual with different coordinates than the observer weighs is refused with ValueError."""
    obs = ObserverModel(name="Observer_A", weights=(1.0, 1.0))
    with pytest.raises(ValueError, match="coordinates"):
        obs.evaluate_phi_1([0.0, 0.0, 100.0])
    with pytest.raises(ValueError, match="coordinates"):
        obs.evaluate_gamma_2([1.0])

    controller = ObserverRobustController(ObserverBundle.create([obs]), r_max=1.0)
    with pytest.raises(ValueError):
        controller.evaluate_transition(
            [1.0, 1.0], [0.1, 0.1],
            [("Pi_inflate_unmonitored", [0.0, 0.0, 100.0], [0.1, 0.1], 0.1)]
        )


def test_empty_observer_bundle_rejected():
    """Verify that an empty observer bundle raises ValueError or refuses transitions."""
    with pytest.raises(ValueError, match="at least one"):
        ObserverBundle.create([])
    with pytest.raises(ValueError, match="at least one"):
        ObserverBundle(observers=())


def test_non_finite_and_nan_inputs_rejected_fail_closed():
    """Verify that candidates with NaN or infinite values are rejected fail-closed."""
    obs = ObserverModel("O", weights=(1.0, 1.0))
    bundle = ObserverBundle.create([obs])
    controller = ObserverRobustController(bundle)

    # 1. Candidate with NaN boundary
    v1 = controller.evaluate_transition(
        [1.0, 1.0], [0.1, 0.1],
        [("op_nan_bnd", [0.5, 0.5], [float("nan"), 0.1], 1.0)]
    )
    assert v1.status == "RefusedStalled"
    assert v1.selected_operator is None

    # 2. Candidate with NaN residual
    v2 = controller.evaluate_transition(
        [1.0, 1.0], [0.1, 0.1],
        [("op_nan_res", [float("nan"), 0.5], [0.1, 0.1], 1.0)]
    )
    assert v2.status == "RefusedStalled"

    # 3. Candidate with inf cost
    v3 = controller.evaluate_transition(
        [1.0, 1.0], [0.1, 0.1],
        [("op_inf_cost", [0.5, 0.5], [0.1, 0.1], float("inf"))]
    )
    assert v3.status == "RefusedStalled"

    # 4. Current state with non-finite element raises ValueError
    with pytest.raises(ValueError, match="non-finite"):
        controller.evaluate_transition([float("nan"), 1.0], [0.1, 0.1], [("op", [0.5, 0.5], [0.1, 0.1], 1.0)])


def test_genuine_degree_two_curvature_complex():
    """Verify that an observer on a 2-simplicial complex correctly handles degree-two (C^2) curvature."""
    # 3 edges (C^1), 1 face (C^2): d_1 = [[1.0, 1.0, -1.0]]
    d1 = ((1.0, 1.0, -1.0),)
    obs = ObserverModel(name="O_2complex", weights=(1.0, 1.0, 1.0), boundary_weights=(3.0,), d1=d1)

    # 1. Evaluate Gamma_2 by supplying 1-cochain (edges)
    omega_1 = [1.0, 0.0, 0.0]  # d1 @ omega_1 = [1.0] -> Gamma_2 = 3.0 * |1.0| = 3.0
    gamma_from_edges = obs.evaluate_gamma_2(omega_1)
    assert math.isclose(gamma_from_edges, 3.0, rel_tol=1e-7)

    # 2. Evaluate Gamma_2 by supplying genuine 2-cochain (1 face coordinate)
    face_cochain = [2.0]  # Gamma_2 = 3.0 * |2.0| = 6.0
    gamma_direct = obs.evaluate_gamma_2(face_cochain)
    assert math.isclose(gamma_direct, 6.0, rel_tol=1e-7)


def test_piecewise_closure_ratio_boundary_cases():
    """Verify piecewise R_cl definition handles zero and near-zero conditions properly."""
    obs = ObserverModel("O_pw", weights=(1.0,), tolerance=1e-6)

    # 1. Phi_1 = 0, Gamma_2 = 0 -> R_cl = 0.0
    r_exact = obs.evaluate_r_cl([0.0], [0.0])
    assert r_exact == 0.0

    # 2. Phi_1 = 0, Gamma_2 > 0 -> R_cl = inf (tearing on zero residual)
    r_tearing = obs.evaluate_r_cl([0.0], [1.0])
    assert math.isinf(r_tearing)

    # 3. Non-finite input -> R_cl = inf
    r_nan = obs.evaluate_r_cl([float("nan")], [0.0])
    assert math.isinf(r_nan)


def test_joint_detector_adequacy_blind_transfer_counterexample():
    """Demonstrate the reviewer's counterexample: without joint detector adequacy, defect can transfer into unmonitored coordinates.

    Three disjoint cycle classes with coordinates (c0, c1, c2).
    Observer 1 observes only c0 (weights 1, 0, 0 approximate via positive weights 10.0, 0.01, 0.01).
    Observer 2 observes only c1 (weights 0.01, 10.0, 0.01).
    Coordinate c2 is a blind mode unmonitored by either observer.
    """
    obs_1 = ObserverModel("O1", weights=(10.0, 0.01, 0.01))
    obs_2 = ObserverModel("O2", weights=(0.01, 10.0, 0.01))
    bundle = ObserverBundle.create([obs_1, obs_2])
    controller = ObserverRobustController(bundle, r_max=1.0)

    # Initial state (1, 1, 0): observed ~ 10.01 under both observers
    curr_res = [1.0, 1.0, 0.0]
    curr_bnd = [0.0, 0.0, 0.0]

    # Transfer to (0, 0, 2): unmonitored coordinate doubles, but observed residual drops to 0.02 under both!
    hidden_transfer_res = [0.0, 0.0, 2.0]
    hidden_transfer_bnd = [0.0, 0.0, 0.0]

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_hidden_transfer", hidden_transfer_res, hidden_transfer_bnd, 1.0)]
    )
    # Both observers see a drastic reduction in their observed residual, so the transfer is admitted
    assert verdict.status == "Admitted"
    # This test verifies that Proposition 3.1 mathematically requires the Joint Detector Adequacy hypothesis!


def test_invalid_observer_parameters_rejection():
    """Verify fail-closed rejection of non-finite weights, infinite tolerance, and malformed coboundaries."""
    # 1. Infinite or negative tolerance
    with pytest.raises(ValueError, match="tolerance"):
        ObserverModel("O_inf_tol", weights=(1.0, 1.0), tolerance=float("inf"))
    with pytest.raises(ValueError, match="tolerance"):
        ObserverModel("O_neg_tol", weights=(1.0, 1.0), tolerance=-1e-5)
    with pytest.raises(ValueError, match="tolerance"):
        ObserverModel("O_nan_tol", weights=(1.0, 1.0), tolerance=float("nan"))

    # 2. Non-finite or non-positive weights
    with pytest.raises(ValueError, match="edge weights"):
        ObserverModel("O_inf_w", weights=(1.0, float("inf")))
    with pytest.raises(ValueError, match="edge weights"):
        ObserverModel("O_nan_w", weights=(1.0, float("nan")))
    with pytest.raises(ValueError, match="edge weights"):
        ObserverModel("O_neg_w", weights=(1.0, -0.5))
    with pytest.raises(ValueError, match="edge weights"):
        ObserverModel("O_empty_w", weights=())

    # 3. Non-finite or non-positive boundary weights
    with pytest.raises(ValueError, match="boundary weights"):
        ObserverModel("O_inf_bw", weights=(1.0, 1.0), boundary_weights=(float("inf"),))
    with pytest.raises(ValueError, match="boundary weights"):
        ObserverModel("O_neg_bw", weights=(1.0, 1.0), boundary_weights=(-1.0,))

    # 4. Coboundary d0 shape / content mismatches
    with pytest.raises(ValueError, match="d0 row count"):
        ObserverModel("O_bad_d0_rows", weights=(1.0, 1.0), d0=((1.0,),))
    with pytest.raises(ValueError, match="d0 entries"):
        ObserverModel("O_nan_d0", weights=(1.0,), d0=((float("nan"),),))

    # 5. Coboundary d1 shape / content mismatches
    with pytest.raises(ValueError, match="d1 row 0 column count"):
        ObserverModel("O_bad_d1_cols", weights=(1.0, 1.0), d1=((1.0,),))
    with pytest.raises(ValueError, match="d1 face count"):
        ObserverModel("O_bad_d1_faces", weights=(1.0, 1.0), boundary_weights=(1.0, 1.0), d1=((1.0, 1.0),))
    with pytest.raises(ValueError, match="d1 entries"):
        ObserverModel("O_inf_d1", weights=(1.0,), d1=((float("inf"),),))

    # 6. Projection indices shape / content mismatches
    with pytest.raises(ValueError, match="projection_indices length"):
        ObserverModel("O_bad_proj_len", weights=(1.0, 1.0), projection_indices=(0,))
    with pytest.raises(ValueError, match="projection index"):
        ObserverModel("O_bad_proj_idx", weights=(1.0,), projection_indices=(-1,))


def test_controller_bound_validation():
    """Verify validation of ObserverRobustController bounds and parameters."""
    bundle = ObserverBundle.create([ObserverModel("O", weights=(1.0,))])

    with pytest.raises(ValueError, match="r_max"):
        ObserverRobustController(bundle, r_max=-1.0)
    with pytest.raises(ValueError, match="r_max"):
        ObserverRobustController(bundle, r_max=0.0)
    with pytest.raises(ValueError, match="r_max"):
        ObserverRobustController(bundle, r_max=float("nan"))

    with pytest.raises(ValueError, match="m_max"):
        ObserverRobustController(bundle, m_max=-5.0)
    with pytest.raises(ValueError, match="m_max"):
        ObserverRobustController(bundle, m_max=0.0)

    with pytest.raises(ValueError, match="gamma_max"):
        ObserverRobustController(bundle, gamma_max=-0.1)
    with pytest.raises(ValueError, match="delta_gamma_max"):
        ObserverRobustController(bundle, delta_gamma_max=-0.1)

    with pytest.raises(ValueError, match="lam"):
        ObserverRobustController(bundle, lam=-1.0)
    with pytest.raises(ValueError, match="lam"):
        ObserverRobustController(bundle, lam=float("inf"))

    with pytest.raises(ValueError, match="eps"):
        ObserverRobustController(bundle, eps=-1e-9)


def test_subcomplex_projection_and_monitoring():
    """Verify projection map pi_O correctly restricts evaluation to declared subcomplex coordinates."""
    # Carrier complex has 3 coordinates: (c0, c1, c2)
    # Observer A monitors (c0, c1); Observer B monitors (c1, c2)
    obs_a = ObserverModel(name="Obs_A", weights=(1.0, 2.0), projection_indices=(0, 1))
    obs_b = ObserverModel(name="Obs_B", weights=(2.0, 1.0), projection_indices=(1, 2))
    bundle = ObserverBundle.create([obs_a, obs_b])
    controller = ObserverRobustController(bundle, r_max=1.0)

    # Cochain on 3-cell carrier
    omega = [1.0, 2.0, 3.0]
    # Obs_A sees (1.0, 2.0): 1*1 + 2*2 = 5.0
    # Obs_B sees (2.0, 3.0): 2*2 + 1*3 = 7.0
    assert math.isclose(obs_a.evaluate_phi_1(omega), 5.0)
    assert math.isclose(obs_b.evaluate_phi_1(omega), 7.0)

    curr_res = [2.0, 2.0, 2.0]  # A sees (2,2) -> 6.0; B sees (2,2) -> 6.0
    curr_bnd = [0.1, 0.1]

    # Valid candidate reducing both subcomplexes
    cand_next_res = [1.0, 1.0, 1.0]  # A sees (1,1) -> 3.0; B sees (1,1) -> 3.0
    cand_next_bnd = [0.05, 0.05]

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_proj_reduce", cand_next_res, cand_next_bnd, 1.0)]
    )
    assert verdict.status == "Admitted"
    assert verdict.selected_operator == "Pi_proj_reduce"


def test_candidate_sat_channel_in_routing_objective():
    """Verify that routing score L uses the explicit SAT channel Phi_sat when provided in candidate transitions."""
    obs = ObserverModel(name="O_sat", weights=(1.0, 1.0))
    bundle = ObserverBundle.create([obs])
    controller = ObserverRobustController(bundle, r_max=2.0, lam=2.0)

    curr_res = [4.0, 4.0]
    curr_bnd = [0.5, 0.5]

    # Both candidates have identical next_res, next_bnd, and cost
    # Cand 1 has high SAT obstruction (phi_sat = 0.9)
    # Cand 2 has low SAT obstruction (phi_sat = 0.1)
    cand_high_sat = ("Pi_high_sat", [2.0, 2.0], [0.1, 0.1], 1.0, 0.9)
    cand_low_sat = ("Pi_low_sat", [2.0, 2.0], [0.1, 0.1], 1.0, 0.1)

    verdict = controller.evaluate_transition(curr_res, curr_bnd, [cand_high_sat, cand_low_sat])
    assert verdict.status == "Admitted"
    assert verdict.selected_operator == "Pi_low_sat"
    assert verdict.observer_diagnostics["O_sat"]["phi_sat"] == 0.1


def test_defect_transfer_between_monitored_subcomplexes_bounded_by_initial_norm():
    """Verify reviewer's case for Proposition 3.1:

    On two disjoint cycle classes, edge weights are 2.0 (cycle 1) and 1.0 (cycle 2).
    Moving unit defect from cycle 1 to cycle 2 reduces Phi_1 from 2.0 to 1.0 with Gamma_2 = 0.
    Under joint adequacy, this transfer satisfies descent and is admitted,
    and post-transition coordinate defect is bounded by the observer's initial budget.
    Attempted defect amplification beyond the initial budget is rejected fail-closed.
    """
    obs = ObserverModel(name="O_cycle", weights=(2.0, 1.0), tolerance=1e-9)
    bundle = ObserverBundle.create([obs])
    controller = ObserverRobustController(bundle, r_max=1.0)

    # Initial state: unit defect on cycle 1, zero on cycle 2. Phi_1 = 2.0 * 1.0 = 2.0
    curr_res = [1.0, 0.0]
    curr_bnd = [0.0, 0.0]

    # 1. Defect transfers to cycle 2: next_res = [0.0, 1.0].
    # Phi_1 = 1.0 * 1.0 = 1.0 <= 2.0 + eps. Gamma_2 = 0.0.
    # The transfer is admitted because it strictly reduces the observer's weighted norm!
    transfer_res = [0.0, 1.0]
    transfer_bnd = [0.0, 0.0]

    verdict = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_transfer", transfer_res, transfer_bnd, 1.0)]
    )
    assert verdict.status == "Admitted"
    assert verdict.selected_operator == "Pi_transfer"
    # Post-transition defect on cycle 2 is |c'_1| = 1.0 <= (Phi_1(c) + eps) / w_1 = 2.0 / 1.0 = 2.0
    assert transfer_res[1] <= 2.0

    # 2. Defect injection attempting to exceed the initial observer budget:
    # next_res = [0.0, 3.0]. Phi_1 = 3.0 > 2.0.
    # Rejected fail-closed by the observer-robust descent law!
    excess_res = [0.0, 3.0]
    verdict_excess = controller.evaluate_transition(
        curr_res, curr_bnd,
        [("Pi_excess", excess_res, transfer_bnd, 1.0)]
    )
    assert verdict_excess.status == "RefusedStalled"
    assert verdict_excess.selected_operator is None

