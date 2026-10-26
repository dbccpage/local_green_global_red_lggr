"""A quotient seminorm cannot bound raw coordinates, even with full coverage."""
from fractions import Fraction

import pytest

from mod_observer_robust_control_core import ObserverBundle, ObserverModel, ObserverRobustController


@pytest.mark.parametrize("coordinate", [1, 17, 10**6])
def test_exact_one_edge_counterexample_to_raw_coordinate_bound(coordinate):
    # The one-edge incidence map sends (0, t) to t, exactly over Q.
    potential = (Fraction(0), Fraction(coordinate))
    residual = Fraction(coordinate) - (-potential[0] + potential[1])
    assert residual == 0
    assert coordinate > 0

    # This LP observation illustrates the same example; it is not its proof.
    observer = ObserverModel(name="whole_edge", weights=(1.0,), d0=((-1.0, 1.0),))
    assert observer.evaluate_phi_1([float(coordinate)]) == 0.0
    controller = ObserverRobustController(ObserverBundle.create([observer]), eps=0.0)
    verdict = controller.evaluate_transition([0.0], [0.0], [("exact_shift", [float(coordinate)], [0.0], 0.0)])
    assert verdict.status == "Admitted"
    assert verdict.worst_case_phi_1 == 0.0


def test_negative_cost_is_not_a_nonnegative_policy_cost():
    observer = ObserverModel(name="input", weights=(1.0,))
    controller = ObserverRobustController(ObserverBundle.create([observer]))
    result = controller.evaluate_transition([1.0], [0.0], [("negative_cost", [0.0], [0.0], -1.0)])
    assert result.status == "RefusedStalled"


def test_nonfinite_current_diagnostic_is_not_an_unbounded_budget():
    observer = ObserverModel(name="input", weights=(2.0,))
    controller = ObserverRobustController(ObserverBundle.create([observer]))
    with pytest.raises(ValueError, match="Current observer diagnostics"):
        controller.evaluate_transition([1e308], [0.0], [("zero", [0.0], [0.0], 0.0)])


def test_overflowed_score_is_not_a_selected_candidate():
    observer = ObserverModel(name="input", weights=(1.0,))
    controller = ObserverRobustController(ObserverBundle.create([observer]))
    result = controller.evaluate_transition([1e308], [0.0], [("overflow", [1e308], [0.0], 1e308)])
    assert result.status == "RefusedStalled"
