from __future__ import annotations

from collections.abc import Callable
from fractions import Fraction
from typing import Any

import numpy as np
import pytest

from lggr_vi_core import (
    ObservationSystem,
    break_and_recover_kernel_vector,
    central_directional_derivative,
    exact_apply_gram,
    exact_centered_derivative,
    exact_dot,
    exact_energy,
    exact_gram,
    exact_mul_vec,
    exact_sign_cube,
    exact_sign_cube_average,
    full_rademacher_directions,
    gram_power_iteration,
    k_of_n_green,
    postprocessing_invariant,
    rademacher_adjoint_estimate,
    unanimous_green,
)


def test_observation_system_basic_contract() -> None:
    system = ObservationSystem([[1.0, 0.0], [0.0, 2.0]])
    np.testing.assert_allclose(system.gram, [[1.0, 0.0], [0.0, 4.0]])
    np.testing.assert_allclose(system.observe([3.0, 4.0]), [3.0, 8.0])
    np.testing.assert_allclose(system.adjoint_signal([3.0, 4.0]), [3.0, 16.0])
    assert system.energy([3.0, 4.0]) == pytest.approx(36.5)
    assert system.domain_dimension == 2
    assert system.codomain_dimension == 2


@pytest.mark.parametrize("matrix", [[1.0, 2.0], [], [[1.0, np.nan]]])
def test_bad_observation_matrices_fail_closed(matrix: Any) -> None:
    with pytest.raises(ValueError):
        ObservationSystem(matrix)


@pytest.mark.parametrize("atol", [0.0, -1.0, np.inf])
def test_bad_absolute_tolerances_fail_closed(atol: float) -> None:
    with pytest.raises(ValueError):
        ObservationSystem([[1.0]], atol=atol)


@pytest.mark.parametrize("state", [[1.0], [1.0, 2.0, 3.0], [1.0, np.inf]])
def test_bad_vectors_fail_closed(state: list[float]) -> None:
    system = ObservationSystem([[1.0, 0.0]])
    with pytest.raises(ValueError):
        system.observe(state)


def test_kernel_visible_decomposition_and_cylinder_bound() -> None:
    system = ObservationSystem([[3.0, 0.0]])
    np.testing.assert_allclose(abs(system.kernel_basis()), [[0.0], [1.0]], atol=1e-12)
    np.testing.assert_allclose(abs(system.visible_basis()), [[1.0], [0.0]], atol=1e-12)
    assert system.rank() == 1
    assert system.is_in_kernel([0.0, 7.0])
    assert not system.is_in_kernel([0.01, 7.0])
    assert system.distance_to_kernel([2.0, 7.0]) == pytest.approx(2.0)
    assert system.smallest_positive_singular_value() == pytest.approx(3.0)
    assert system.cylinder_radius(0.6) == pytest.approx(0.2)


def test_zero_operator_special_cases() -> None:
    system = ObservationSystem([[0.0, 0.0]])
    assert system.rank() == 0
    assert system.visible_basis().shape == (2, 0)
    assert system.kernel_basis().shape == (2, 2)
    assert system.distance_to_kernel([4.0, -3.0]) == 0.0
    with pytest.raises(ValueError, match="no positive singular"):
        system.smallest_positive_singular_value()


@pytest.mark.parametrize("tolerance", [-0.1, np.inf])
def test_bad_cylinder_tolerances_fail_closed(tolerance: float) -> None:
    with pytest.raises(ValueError):
        ObservationSystem([[1.0]]).cylinder_radius(tolerance)


def test_zero_preserving_aggregators() -> None:
    assert unanimous_green([])
    assert unanimous_green([0.0, 0.1], tolerance=0.1)
    assert not unanimous_green([0.0, 0.2], tolerance=0.1)
    assert k_of_n_green([0.0, 0.2, 0.0], 2, tolerance=0.1)
    assert not k_of_n_green([0.0, 0.2, 0.3], 2, tolerance=0.1)


@pytest.mark.parametrize(
    ("call", "match"),
    [
        (lambda: unanimous_green([0.0], -1.0), "tolerance"),
        (lambda: unanimous_green([np.nan]), "scores"),
        (lambda: k_of_n_green([0.0], 0), "k"),
        (lambda: k_of_n_green([0.0], 2), "k"),
        (lambda: k_of_n_green([0.0], 1, -1.0), "tolerance"),
        (lambda: k_of_n_green([np.nan], 1), "scores"),
    ],
)
def test_bad_aggregator_inputs_fail_closed(
    call: Callable[[], bool], match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        call()


def test_deterministic_postprocessing_cannot_split_equal_observations() -> None:
    system = ObservationSystem([[1.0, 0.0]])

    def verdict(observation: np.ndarray) -> bool:
        return bool(float(np.linalg.norm(observation)) <= 0.5)

    assert postprocessing_invariant(system, [0.25, 0.0], [0.25, 99.0], verdict)
    with pytest.raises(ValueError, match="not observationally equivalent"):
        postprocessing_invariant(system, [0.0, 0.0], [1.0, 0.0], verdict)


def test_central_probe_equals_adjoint_pairing() -> None:
    system = ObservationSystem([[2.0, -1.0], [0.0, 0.5]])
    state = np.array([0.8, -0.4])
    direction = np.array([-1.0, 1.0])
    measured = central_directional_derivative(system, state, direction, step=1e-5)
    expected = float(direction @ system.adjoint_signal(state))
    assert measured == pytest.approx(expected, rel=1e-10, abs=1e-10)
    with pytest.raises(ValueError, match="step"):
        central_directional_derivative(system, state, direction, step=0.0)


def test_complete_rademacher_average_recovers_adjoint() -> None:
    system = ObservationSystem([[2.0, -1.0], [0.0, 0.5]])
    state = np.array([0.8, -0.4])
    directions = full_rademacher_directions(2)
    estimate = rademacher_adjoint_estimate(system, state, directions)
    np.testing.assert_allclose(estimate, system.adjoint_signal(state), atol=1e-10)


@pytest.mark.parametrize("dimension", [0, 17])
def test_bad_rademacher_dimension_fails_closed(dimension: int) -> None:
    with pytest.raises(ValueError, match="dimension"):
        full_rademacher_directions(dimension)


@pytest.mark.parametrize("directions", [[], [[1.0]], [[0.0, 1.0]], [[1.0, 1.0, 1.0]]])
def test_bad_probe_directions_fail_closed(directions: Any) -> None:
    with pytest.raises(ValueError, match="directions"):
        rademacher_adjoint_estimate(
            ObservationSystem([[1.0, 0.0]]), [1.0, 0.0], directions
        )


def test_gram_power_iteration_finds_dominant_visible_direction() -> None:
    system = ObservationSystem([[3.0, 0.0], [0.0, 1.0]])
    result = gram_power_iteration(system, [1.0, 1.0], iterations=12)
    np.testing.assert_allclose(abs(result.vector), [1.0, 0.0], atol=1e-9)
    assert result.rayleigh_quotient == pytest.approx(9.0)


def test_power_iteration_rejects_invalid_starts() -> None:
    with pytest.raises(ValueError, match="iterations"):
        gram_power_iteration(ObservationSystem([[1.0]]), [1.0], iterations=0)
    with pytest.raises(ValueError, match="nonzero"):
        gram_power_iteration(ObservationSystem([[1.0]]), [0.0])
    with pytest.raises(ValueError, match="visible subspace"):
        gram_power_iteration(ObservationSystem([[1.0, 0.0]]), [0.0, 1.0])


def test_mutation_breaks_and_restoration_recovers_kernel_claim() -> None:
    receipt = break_and_recover_kernel_vector([[1.0, 0.0]], [0.0, 1.0], (0, 1), 0.25)
    assert receipt.baseline_hidden
    assert receipt.mutation_detected
    assert receipt.restored_hidden


def test_mutation_gate_rejects_bad_inputs() -> None:
    with pytest.raises(ValueError, match="nonzero"):
        break_and_recover_kernel_vector([[1.0, 0.0]], [0.0, 0.0], (0, 1), 0.25)
    with pytest.raises(ValueError, match="not hidden"):
        break_and_recover_kernel_vector([[1.0, 0.0]], [1.0, 0.0], (0, 1), 0.25)
    with pytest.raises(IndexError, match="outside"):
        break_and_recover_kernel_vector([[1.0, 0.0]], [0.0, 1.0], (2, 1), 0.25)
    with pytest.raises(ValueError, match="perturbation"):
        break_and_recover_kernel_vector([[1.0, 0.0]], [0.0, 1.0], (0, 1), 0.0)


def test_exact_rational_identities_call_shipped_checkers() -> None:
    paper = ((1, 0),)
    hidden = (0, 1)
    visible = (1, 0)
    assert exact_mul_vec(paper, hidden) == (Fraction(0),)
    assert exact_apply_gram(paper, hidden) == (Fraction(0), Fraction(0))
    assert exact_energy(paper, hidden) == 0
    assert exact_mul_vec(paper, visible) == (Fraction(1),)
    visible_gram = exact_apply_gram(paper, visible)
    assert visible_gram == (Fraction(1), Fraction(0))
    assert (exact_apply_gram(paper, hidden) == (Fraction(0), Fraction(0))) is (
        exact_mul_vec(paper, hidden) == (Fraction(0),)
    )
    assert (visible_gram == (Fraction(0), Fraction(0))) is False

    matrix = ((2, -1), (0, Fraction(1, 2)))
    state = (Fraction(4, 5), Fraction(-2, 5))
    direction = (Fraction(1, 3), Fraction(-2, 5))
    gram_state = exact_apply_gram(matrix, state)
    assert exact_gram(matrix)[0][1] == exact_gram(matrix)[1][0]
    for step in (Fraction(3, 7), 1):
        assert exact_centered_derivative(matrix, state, direction, step) == exact_dot(
            direction, gram_state
        )
    assert exact_sign_cube_average(matrix, state, Fraction(3, 7)) == gram_state
    assert len(exact_sign_cube(2)) == 4


def test_exact_rational_checkers_fail_closed() -> None:
    with pytest.raises(ValueError, match="nonempty"):
        exact_gram([])
    with pytest.raises(ValueError, match="rows must be nonempty"):
        exact_gram([[]])
    with pytest.raises(ValueError, match="equal length"):
        exact_gram([[1, 2], [3]])
    with pytest.raises(ValueError, match="length"):
        exact_mul_vec([[1, 0]], [1])
    with pytest.raises(ValueError, match="nonzero"):
        exact_centered_derivative([[1, 0]], [0, 1], [1, 0], 0)
    with pytest.raises(ValueError, match="between 1 and 8"):
        exact_sign_cube(0)
    with pytest.raises(ValueError, match="between 1 and 8"):
        exact_sign_cube(9)
    with pytest.raises(ValueError, match="same length"):
        exact_dot([1], [1, 2])
    with pytest.raises(ValueError, match="nonempty"):
        exact_dot([], [])
