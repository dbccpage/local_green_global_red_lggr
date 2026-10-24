"""Exact solver for finite-cochain obstruction classification and rational repair over Q.

Port of omega_engine/crates/solver/solv_finite_cochain_obstruction.py and
omega_engine/crates/homology_theory/finite_cochain_complex.py into a self-contained
paper-package module. Operates purely over fractions.Fraction with zero floating-point error.

AuthorityEffect: None.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from hashlib import sha256
from typing import Iterable, Sequence, TypeAlias

Scalar: TypeAlias = Fraction
Vector: TypeAlias = tuple[Scalar, ...]
Matrix: TypeAlias = tuple[Vector, ...]
COEFFICIENT_DOMAIN = "Q"


class Verdict(str, Enum):
    """Exhaustive outcomes for a supplied finite C1 cochain."""

    INVALID_COMPLEX = "invalid_complex"
    CURVATURE = "curvature"
    EXACT_REPAIR = "exact_repair"
    CLOSED_RESIDUAL = "closed_residual"


def _scalar(value: int | str | Fraction) -> Scalar:
    """Coerce value to Fraction, strictly rejecting booleans and floating-point values."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(
            "use integers, strings, or Fraction; floating point is forbidden"
        )
    if not isinstance(value, (int, str, Fraction)):
        raise TypeError(f"unsupported exact scalar: {type(value).__name__}")
    return Fraction(value)


def coerce_vector(
    values: Iterable[int | str | Fraction], expected: int, label: str
) -> Vector:
    """Coerce an iterable of exact values to an exact Vector with expected dimension."""
    result = tuple(_scalar(value) for value in values)
    if len(result) != expected:
        raise ValueError(f"{label} has length {len(result)}; expected {expected}")
    return result


def _matrix(
    rows: Iterable[Iterable[int | str | Fraction]],
    row_count: int,
    column_count: int,
    label: str,
) -> Matrix:
    """Coerce nested iterables of exact values to an exact Matrix."""
    result = tuple(
        coerce_vector(row, column_count, f"{label}[{index}]")
        for index, row in enumerate(rows)
    )
    if len(result) != row_count:
        raise ValueError(f"{label} has {len(result)} rows; expected {row_count}")
    return result


def _matvec(matrix: Matrix, vector: Vector) -> Vector:
    """Exact matrix-vector product over Q."""
    return tuple(
        sum(
            (coefficient * value for coefficient, value in zip(row, vector)),
            Fraction(0),
        )
        for row in matrix
    )


def _matmul(
    left: Matrix,
    right: Matrix,
    inner_dimension: int,
    right_columns: int | None = None,
) -> Matrix:
    """Exact matrix-matrix multiplication over Q."""
    if not left:
        return ()
    if right_columns is None:
        right_columns = len(right[0]) if right else 0
    return tuple(
        tuple(
            sum(
                (left[row][k] * right[k][column] for k in range(inner_dimension)),
                Fraction(0),
            )
            for column in range(right_columns)
        )
        for row in range(len(left))
    )


def _transpose(matrix: Matrix, row_count: int, column_count: int) -> Matrix:
    """Transpose a matrix while retaining empty-dimension shape information."""
    return tuple(
        tuple(matrix[row][column] for row in range(row_count))
        for column in range(column_count)
    )


def _dot(left: Vector, right: Vector) -> Scalar:
    """Exact inner product over Q."""
    return sum(
        (left_value * right_value for left_value, right_value in zip(left, right)),
        Fraction(0),
    )


def _is_zero(values: Iterable[Scalar]) -> bool:
    """Check if all scalars in iterable are exact rational zero."""
    return all(value == 0 for value in values)


def _solve_exact(matrix: Matrix, rhs: Vector, variable_count: int) -> Vector | None:
    """Solve matrix @ x = rhs over Q, choosing all free variables as zero."""
    equation_count = len(rhs)
    if equation_count == 0:
        return tuple(Fraction(0) for _ in range(variable_count))

    augmented = [list(matrix[row]) + [rhs[row]] for row in range(equation_count)]
    pivot_columns: list[int] = []
    pivot_row = 0

    for column in range(variable_count):
        candidate = next(
            (
                row
                for row in range(pivot_row, equation_count)
                if augmented[row][column] != 0
            ),
            None,
        )
        if candidate is None:
            continue

        augmented[pivot_row], augmented[candidate] = (
            augmented[candidate],
            augmented[pivot_row],
        )
        pivot = augmented[pivot_row][column]
        augmented[pivot_row] = [value / pivot for value in augmented[pivot_row]]

        for row in range(equation_count):
            if row == pivot_row:
                continue
            factor = augmented[row][column]
            if factor != 0:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(augmented[row], augmented[pivot_row])
                ]

        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == equation_count:
            break

    for row_values in augmented:
        if _is_zero(row_values[:variable_count]) and row_values[variable_count] != 0:
            return None

    solution = [Fraction(0) for _ in range(variable_count)]
    for row, column in enumerate(pivot_columns):
        solution[column] = augmented[row][variable_count]
    return tuple(solution)


def _fraction_text(value: Scalar) -> str:
    """Format Fraction as numerator/denominator text."""
    return f"{value.numerator}/{value.denominator}"


def _encoded_vector(vector: Vector | None) -> list[str] | None:
    """Encode vector into JSON-serializable list of strings."""
    if vector is None:
        return None
    return [_fraction_text(value) for value in vector]


def _encoded_matrix(matrix: Matrix) -> list[list[str]]:
    """Encode matrix into JSON-serializable list of lists of strings."""
    return [[_fraction_text(value) for value in row] for row in matrix]


@dataclass(frozen=True)
class FiniteCochainComplex:
    """Finite 3-term cochain complex C0 -> C1 -> C2 over Q with coboundaries d0 and d1."""

    c0_dimension: int
    c1_dimension: int
    c2_dimension: int
    d0: Matrix
    d1: Matrix

    @classmethod
    def from_rows(
        cls,
        dimensions: tuple[int, int, int],
        d0: Sequence[Sequence[int | str | Fraction]],
        d1: Sequence[Sequence[int | str | Fraction]],
    ) -> "FiniteCochainComplex":
        """Construct FiniteCochainComplex from dimension triple and row sequences."""
        if len(dimensions) != 3 or any(
            isinstance(dimension, bool)
            or not isinstance(dimension, int)
            or dimension < 0
            for dimension in dimensions
        ):
            raise ValueError("dimensions must be three nonnegative integers")
        c0_dimension, c1_dimension, c2_dimension = dimensions
        return cls(
            c0_dimension=c0_dimension,
            c1_dimension=c1_dimension,
            c2_dimension=c2_dimension,
            d0=_matrix(d0, c1_dimension, c0_dimension, "d0"),
            d1=_matrix(d1, c2_dimension, c1_dimension, "d1"),
        )

    def complex_defect(self) -> Matrix:
        """Compute the complex defect d1 @ d0 over Q."""
        return _matmul(self.d1, self.d0, self.c1_dimension, right_columns=self.c0_dimension)


@dataclass(frozen=True)
class CochainAnalysis:
    """A deterministic, evidence-only result; never an authority certificate."""

    verdict: Verdict
    beta: Vector
    complex_defect: Matrix
    closure_defect: Vector
    primitive_witness: Vector | None
    residual_representative: Vector | None
    period_witness: Vector | None
    period_boundary_defect: Vector | None
    period_pairing: Scalar | None
    period_is_boundary: bool | None
    coefficient_domain: str
    evidence_sha256: str
    authority_effect: str = "None"


def analyze_finite_cochain(
    complex_: FiniteCochainComplex,
    beta: Sequence[int | str | Fraction],
) -> CochainAnalysis:
    """Classify beta and bind the complete exact computation to SHA-256."""
    checked_beta = coerce_vector(beta, complex_.c1_dimension, "beta")
    complex_defect = complex_.complex_defect()
    closure_defect = _matvec(complex_.d1, checked_beta)
    primitive_witness = _solve_exact(complex_.d0, checked_beta, complex_.c0_dimension)
    residual_representative: Vector | None = None
    period_witness: Vector | None = None
    period_boundary_defect: Vector | None = None
    period_pairing: Scalar | None = None
    period_is_boundary: bool | None = None

    if any(not _is_zero(row) for row in complex_defect):
        verdict = Verdict.INVALID_COMPLEX
    elif not _is_zero(closure_defect):
        if primitive_witness is not None:
            raise AssertionError("valid complex produced a nonclosed exact cochain")
        verdict = Verdict.CURVATURE
    else:
        if primitive_witness is not None:
            if _matvec(complex_.d0, primitive_witness) != checked_beta:
                raise AssertionError(
                    "internal exact solver produced an invalid witness"
                )
            verdict = Verdict.EXACT_REPAIR
        else:
            verdict = Verdict.CLOSED_RESIDUAL
            residual_representative = checked_beta
            boundary1 = _transpose(
                complex_.d0, complex_.c1_dimension, complex_.c0_dimension
            )
            period_constraints = boundary1 + (checked_beta,)
            period_rhs = tuple(Fraction(0) for _ in range(complex_.c0_dimension)) + (
                Fraction(1),
            )
            period_witness = _solve_exact(
                period_constraints, period_rhs, complex_.c1_dimension
            )
            if period_witness is None:
                raise AssertionError(
                    "closed nonexact cochain has no dual period witness"
                )
            period_boundary_defect = _matvec(boundary1, period_witness)
            period_pairing = _dot(checked_beta, period_witness)
            boundary2 = _transpose(
                complex_.d1, complex_.c2_dimension, complex_.c1_dimension
            )
            period_is_boundary = (
                _solve_exact(boundary2, period_witness, complex_.c2_dimension)
                is not None
            )
            if not _is_zero(period_boundary_defect):
                raise AssertionError("period witness is not a 1-cycle")
            if period_pairing == 0:
                raise AssertionError("period witness has zero pairing")
            if period_is_boundary:
                raise AssertionError("period witness is a 2-boundary")

    payload = {
        "authority_effect": "None",
        "beta": _encoded_vector(checked_beta),
        "coefficient_domain": COEFFICIENT_DOMAIN,
        "closure_defect": _encoded_vector(closure_defect),
        "complex_defect": _encoded_matrix(complex_defect),
        "d0": _encoded_matrix(complex_.d0),
        "d1": _encoded_matrix(complex_.d1),
        "dimensions": [
            complex_.c0_dimension,
            complex_.c1_dimension,
            complex_.c2_dimension,
        ],
        "primitive_witness": _encoded_vector(primitive_witness),
        "residual_representative": _encoded_vector(residual_representative),
        "period_witness": _encoded_vector(period_witness),
        "period_boundary_defect": _encoded_vector(period_boundary_defect),
        "period_pairing": None
        if period_pairing is None
        else _fraction_text(period_pairing),
        "period_is_boundary": period_is_boundary,
        "verdict": verdict.value,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    evidence_sha256 = sha256(canonical).hexdigest()

    return CochainAnalysis(
        verdict=verdict,
        beta=checked_beta,
        complex_defect=complex_defect,
        closure_defect=closure_defect,
        primitive_witness=primitive_witness,
        residual_representative=residual_representative,
        period_witness=period_witness,
        period_boundary_defect=period_boundary_defect,
        period_pairing=period_pairing,
        period_is_boundary=period_is_boundary,
        coefficient_domain=COEFFICIENT_DOMAIN,
        evidence_sha256=evidence_sha256,
    )


solve_finite_cochain_obstruction = analyze_finite_cochain


def solve_exact_repair(
    matrix: Sequence[Sequence[int | str | Fraction]],
    rhs: Sequence[int | str | Fraction],
) -> tuple[Vector | None, Vector]:
    """Solve matrix @ alpha = rhs exactly over Q using Gaussian elimination.

    Returns:
        (alpha, residual) where residual = rhs - matrix @ alpha.
        If no exact solution exists, returns (None, rhs).
    """
    row_count = len(rhs)
    matrix_rows = len(matrix)
    if row_count == 0 and matrix_rows == 0:
        return ((), ())
    if matrix_rows != row_count:
        raise ValueError(
            f"Dimension mismatch: matrix has {matrix_rows} rows, but rhs has {row_count} entries"
        )
    col_count = len(matrix[0]) if matrix_rows > 0 else 0
    mat = _matrix(matrix, row_count, col_count, "matrix")
    vec = coerce_vector(rhs, row_count, "rhs")
    sol = _solve_exact(mat, vec, col_count)
    if sol is None:
        return None, vec
    d_sol = _matvec(mat, sol)
    res = tuple(v - d for v, d in zip(vec, d_sol))
    return sol, res


def self_check() -> None:
    """Verify solver sanity on canonical 3-site cycle complex."""
    filled = FiniteCochainComplex.from_rows(
        (3, 3, 1),
        ((-1, 1, 0), (0, -1, 1), (-1, 0, 1)),
        ((1, 1, -1),),
    )
    assert analyze_finite_cochain(filled, (1, 2, 3)).verdict is Verdict.EXACT_REPAIR
    assert analyze_finite_cochain(filled, (1, 2, 4)).verdict is Verdict.CURVATURE
