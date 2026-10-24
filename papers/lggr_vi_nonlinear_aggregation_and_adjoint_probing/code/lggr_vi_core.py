"""Finite observation blind spots and adjoint probes.

The module implements only the objects used by the paper: a finite real
observation matrix, its Gram operator, deterministic aggregation checks,
central-difference directional probes, and explicit mutation falsifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Any, Callable, Iterable, Sequence, TypeVar

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
T = TypeVar("T")


def _finite_vector(value: ArrayLike, dimension: int, name: str) -> FloatArray:
    vector = np.asarray(value, dtype=float)
    if vector.shape != (dimension,):
        raise ValueError(f"{name} must have shape ({dimension},)")
    if not np.isfinite(vector).all():
        raise ValueError(f"{name} must contain only finite values")
    return vector


@dataclass(frozen=True)
class ObservationSystem:
    """A finite real observation operator ``Q : R^d -> R^m``."""

    matrix: Any
    atol: float = 1e-10

    def __post_init__(self) -> None:
        matrix = np.asarray(self.matrix, dtype=float)
        if matrix.ndim != 2 or 0 in matrix.shape:
            raise ValueError("matrix must be a nonempty two-dimensional array")
        if not np.isfinite(matrix).all():
            raise ValueError("matrix must contain only finite values")
        if not np.isfinite(self.atol) or self.atol <= 0:
            raise ValueError("atol must be a positive finite number")
        matrix = matrix.copy()
        matrix.setflags(write=False)
        object.__setattr__(self, "matrix", matrix)

    @property
    def domain_dimension(self) -> int:
        return int(self.matrix.shape[1])

    @property
    def codomain_dimension(self) -> int:
        return int(self.matrix.shape[0])

    @property
    def gram(self) -> FloatArray:
        """Return ``H = Q.T @ Q``."""

        return self.matrix.T @ self.matrix

    def vector(self, value: ArrayLike, name: str = "vector") -> FloatArray:
        return _finite_vector(value, self.domain_dimension, name)

    def observe(self, state: ArrayLike) -> FloatArray:
        return self.matrix @ self.vector(state, "state")

    def energy(self, state: ArrayLike) -> float:
        observation = self.observe(state)
        return float(0.5 * observation @ observation)

    def adjoint_signal(self, state: ArrayLike) -> FloatArray:
        return self.gram @ self.vector(state, "state")

    def is_in_kernel(self, state: ArrayLike) -> bool:
        return bool(np.linalg.norm(self.observe(state)) <= self.atol)

    def _svd(self) -> tuple[FloatArray, FloatArray]:
        singular_values = np.linalg.svd(self.matrix, compute_uv=False)
        _, _, vh = np.linalg.svd(self.matrix, full_matrices=True)
        return singular_values, vh

    def rank(self) -> int:
        singular_values, _ = self._svd()
        return int(np.count_nonzero(singular_values > self.atol))

    def kernel_basis(self) -> FloatArray:
        """Return an orthonormal basis for ``ker(Q)`` as matrix columns."""

        _, vh = self._svd()
        return vh[self.rank() :].T.copy()

    def visible_basis(self) -> FloatArray:
        """Return an orthonormal basis for ``ker(Q)^perp`` as matrix columns."""

        _, vh = self._svd()
        return vh[: self.rank()].T.copy()

    def distance_to_kernel(self, state: ArrayLike) -> float:
        state_vector = self.vector(state, "state")
        visible = self.visible_basis()
        if visible.shape[1] == 0:
            return 0.0
        return float(np.linalg.norm(visible @ (visible.T @ state_vector)))

    def smallest_positive_singular_value(self) -> float:
        singular_values, _ = self._svd()
        positive = singular_values[singular_values > self.atol]
        if positive.size == 0:
            raise ValueError(
                "the zero observation operator has no positive singular value"
            )
        return float(positive[-1])

    def cylinder_radius(self, observation_tolerance: float) -> float:
        if not np.isfinite(observation_tolerance) or observation_tolerance < 0:
            raise ValueError("observation_tolerance must be finite and non-negative")
        return observation_tolerance / self.smallest_positive_singular_value()


def unanimous_green(scores: Iterable[float], tolerance: float = 0.0) -> bool:
    """Return whether every finite score is at most ``tolerance``."""

    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    values = np.asarray(tuple(scores), dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("scores must be a one-dimensional finite sequence")
    return bool(np.all(values <= tolerance))


def k_of_n_green(scores: Sequence[float], k: int, tolerance: float = 0.0) -> bool:
    """Return whether at least ``k`` scores are at most ``tolerance``."""

    if k < 1 or k > len(scores):
        raise ValueError("k must satisfy 1 <= k <= len(scores)")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    values = np.asarray(scores, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("scores must be a one-dimensional finite sequence")
    return bool(np.count_nonzero(values <= tolerance) >= k)


def postprocessing_invariant(
    system: ObservationSystem,
    left: ArrayLike,
    right: ArrayLike,
    postprocess: Callable[[FloatArray], T],
) -> bool:
    """Evaluate the post-processing theorem after checking its premise."""

    left_observation = system.observe(left)
    right_observation = system.observe(right)
    if not np.array_equal(left_observation, right_observation):
        raise ValueError("states are not observationally equivalent")
    return bool(postprocess(left_observation) == postprocess(right_observation))


def central_directional_derivative(
    system: ObservationSystem,
    state: ArrayLike,
    direction: ArrayLike,
    step: float = 1e-4,
) -> float:
    """Two-query derivative of ``0.5 * ||Qx||^2`` along ``direction``."""

    if not np.isfinite(step) or step <= 0:
        raise ValueError("step must be a positive finite number")
    state_vector = system.vector(state, "state")
    direction_vector = system.vector(direction, "direction")
    plus = system.energy(state_vector + step * direction_vector)
    minus = system.energy(state_vector - step * direction_vector)
    return (plus - minus) / (2.0 * step)


def full_rademacher_directions(dimension: int) -> FloatArray:
    """Enumerate all sign directions for exact small-dimensional checks."""

    if dimension < 1 or dimension > 16:
        raise ValueError("dimension must lie between 1 and 16")
    return np.asarray(tuple(product((-1.0, 1.0), repeat=dimension)), dtype=float)


def rademacher_adjoint_estimate(
    system: ObservationSystem,
    state: ArrayLike,
    directions: ArrayLike,
    step: float = 1e-4,
) -> FloatArray:
    """Average SPSA-style sign probes of the quadratic energy gradient."""

    direction_array = np.asarray(directions, dtype=float)
    if (
        direction_array.ndim != 2
        or direction_array.shape[0] == 0
        or direction_array.shape[1] != system.domain_dimension
    ):
        raise ValueError(
            "directions must be a nonempty matrix with one column per state coordinate"
        )
    if not np.isin(direction_array, (-1.0, 1.0)).all():
        raise ValueError("directions must contain only -1 and +1")
    state_vector = system.vector(state, "state")
    terms = [
        central_directional_derivative(system, state_vector, direction, step)
        * direction
        for direction in direction_array
    ]
    return np.mean(terms, axis=0)


@dataclass(frozen=True)
class PowerIterationResult:
    vector: FloatArray
    rayleigh_quotient: float


def gram_power_iteration(
    system: ObservationSystem,
    initial: ArrayLike,
    iterations: int = 20,
) -> PowerIterationResult:
    """Iterate the Gram operator from a state with a visible component."""

    if iterations < 1:
        raise ValueError("iterations must be positive")
    vector = system.vector(initial, "initial").copy()
    if np.linalg.norm(vector) <= system.atol:
        raise ValueError("initial must be nonzero")
    for _ in range(iterations):
        candidate = system.gram @ vector
        norm = np.linalg.norm(candidate)
        if norm <= system.atol:
            raise ValueError("initial has no component in the visible subspace")
        vector = candidate / norm
    quotient = float(vector @ system.gram @ vector)
    return PowerIterationResult(vector=vector, rayleigh_quotient=quotient)


@dataclass(frozen=True)
class MutationReceipt:
    baseline_hidden: bool
    mutation_detected: bool
    restored_hidden: bool


def break_and_recover_kernel_vector(
    matrix: ArrayLike,
    claimed_kernel_vector: ArrayLike,
    entry: tuple[int, int],
    perturbation: float,
    atol: float = 1e-10,
) -> MutationReceipt:
    """Inject one watcher coefficient, detect the break, then restore it."""

    baseline_matrix = np.asarray(matrix, dtype=float)
    baseline = ObservationSystem(baseline_matrix, atol=atol)
    vector = baseline.vector(claimed_kernel_vector, "claimed_kernel_vector")
    if np.linalg.norm(vector) <= atol:
        raise ValueError("claimed_kernel_vector must be nonzero")
    if not baseline.is_in_kernel(vector):
        raise ValueError("claimed_kernel_vector is not hidden by the baseline matrix")
    row, column = entry
    if row not in range(baseline.codomain_dimension) or column not in range(
        baseline.domain_dimension
    ):
        raise IndexError("entry lies outside the observation matrix")
    if not np.isfinite(perturbation) or abs(perturbation) <= atol:
        raise ValueError("perturbation must be finite and larger than atol")
    mutated_matrix = baseline_matrix.copy()
    mutated_matrix[row, column] += perturbation
    mutation_detected = not ObservationSystem(mutated_matrix, atol=atol).is_in_kernel(
        vector
    )
    restored_hidden = ObservationSystem(baseline_matrix.copy(), atol=atol).is_in_kernel(
        vector
    )
    return MutationReceipt(True, mutation_detected, restored_hidden)


RationalMatrix = tuple[tuple[Fraction, ...], ...]
RationalVector = tuple[Fraction, ...]


def _as_fraction_matrix(matrix: Sequence[Sequence[Fraction | int]]) -> RationalMatrix:
    rows: list[tuple[Fraction, ...]] = []
    if not matrix:
        raise ValueError("matrix must be nonempty")
    width: int | None = None
    for row in matrix:
        values = tuple(Fraction(entry) for entry in row)
        if not values:
            raise ValueError("matrix rows must be nonempty")
        if width is None:
            width = len(values)
        elif len(values) != width:
            raise ValueError("matrix rows must have equal length")
        rows.append(values)
    return tuple(rows)


def _as_fraction_vector(
    vector: Sequence[Fraction | int], dimension: int, name: str
) -> RationalVector:
    values = tuple(Fraction(entry) for entry in vector)
    if len(values) != dimension:
        raise ValueError(f"{name} must have length {dimension}")
    return values


def exact_gram(matrix: Sequence[Sequence[Fraction | int]]) -> RationalMatrix:
    """Return Q transpose Q over the rationals."""

    rows = _as_fraction_matrix(matrix)
    codomain = len(rows)
    domain = len(rows[0])
    return tuple(
        tuple(
            sum(
                (rows[k][i] * rows[k][j] for k in range(codomain)),
                Fraction(0),
            )
            for j in range(domain)
        )
        for i in range(domain)
    )


def exact_mul_vec(
    matrix: Sequence[Sequence[Fraction | int]],
    vector: Sequence[Fraction | int],
) -> RationalVector:
    """Apply a rational matrix to a vector of the matching width."""

    rows = _as_fraction_matrix(matrix)
    state = _as_fraction_vector(vector, len(rows[0]), "vector")
    return tuple(
        sum((row[index] * state[index] for index in range(len(state))), Fraction(0))
        for row in rows
    )


def exact_apply_gram(
    matrix: Sequence[Sequence[Fraction | int]],
    vector: Sequence[Fraction | int],
) -> RationalVector:
    """Apply Q transpose Q to a rational vector."""

    return exact_mul_vec(exact_gram(matrix), vector)


def exact_dot(
    left: Sequence[Fraction | int], right: Sequence[Fraction | int]
) -> Fraction:
    """Dot product of two nonempty rational vectors of equal length."""

    left_values = tuple(Fraction(entry) for entry in left)
    right_values = tuple(Fraction(entry) for entry in right)
    if len(left_values) != len(right_values) or not left_values:
        raise ValueError("vectors must be nonempty and the same length")
    return sum(
        (item * other for item, other in zip(left_values, right_values, strict=True)),
        Fraction(0),
    )


def exact_energy(
    matrix: Sequence[Sequence[Fraction | int]],
    state: Sequence[Fraction | int],
) -> Fraction:
    """Return one half of the squared Euclidean observation, exactly."""

    observed = exact_mul_vec(matrix, state)
    return Fraction(1, 2) * exact_dot(observed, observed)


def exact_centered_derivative(
    matrix: Sequence[Sequence[Fraction | int]],
    state: Sequence[Fraction | int],
    direction: Sequence[Fraction | int],
    step: Fraction | int,
) -> Fraction:
    """Exact centered derivative of one-half the squared observation."""

    step_value = Fraction(step)
    if step_value == 0:
        raise ValueError("step must be nonzero")
    rows = _as_fraction_matrix(matrix)
    domain = len(rows[0])
    state_vector = _as_fraction_vector(state, domain, "state")
    direction_vector = _as_fraction_vector(direction, domain, "direction")
    plus = tuple(
        item + step_value * bit
        for item, bit in zip(state_vector, direction_vector, strict=True)
    )
    minus = tuple(
        item - step_value * bit
        for item, bit in zip(state_vector, direction_vector, strict=True)
    )
    return (exact_energy(rows, plus) - exact_energy(rows, minus)) / (2 * step_value)


def exact_sign_cube(dimension: int) -> tuple[RationalVector, ...]:
    """Enumerate the full rational sign cube in a small dimension."""

    if dimension < 1 or dimension > 8:
        raise ValueError("dimension must lie between 1 and 8")
    return tuple(
        tuple(Fraction(bit) for bit in signs)
        for signs in product((-1, 1), repeat=dimension)
    )


def exact_sign_cube_average(
    matrix: Sequence[Sequence[Fraction | int]],
    state: Sequence[Fraction | int],
    step: Fraction | int,
) -> RationalVector:
    """Average the exact centered sign probe over the full cube."""

    rows = _as_fraction_matrix(matrix)
    domain = len(rows[0])
    cube = exact_sign_cube(domain)
    total = [Fraction(0) for _ in range(domain)]
    for sign in cube:
        scalar = exact_centered_derivative(rows, state, sign, step)
        for index, bit in enumerate(sign):
            total[index] += scalar * bit
    count = Fraction(len(cube))
    return tuple(item / count for item in total)


__all__ = [
    "MutationReceipt",
    "ObservationSystem",
    "PowerIterationResult",
    "break_and_recover_kernel_vector",
    "central_directional_derivative",
    "exact_apply_gram",
    "exact_centered_derivative",
    "exact_dot",
    "exact_energy",
    "exact_gram",
    "exact_mul_vec",
    "exact_sign_cube",
    "exact_sign_cube_average",
    "full_rademacher_directions",
    "gram_power_iteration",
    "k_of_n_green",
    "postprocessing_invariant",
    "rademacher_adjoint_estimate",
    "unanimous_green",
]
