"""Exact finite rational repair certificates. No NumPy, solver, or float tolerances.

A supplied dual annihilator certifies a lower bound. Matching primal evidence
certifies the optimum; a positive certified lower bound proves nonrepairability.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from .common import ValidationError, digest, json_value, sequence

Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]


def rational(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if type(value) not in (int, str):
        raise ValidationError("Exact coefficients must be integers, rational strings or Fraction objects; not floats/bools")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValidationError(f"Invalid rational coefficient: {value!r}") from exc


def vector(values: Any, name: str, size: int | None = None) -> Vector:
    result = tuple(rational(v) for v in sequence(values, name))
    if size is not None and len(result) != size:
        raise ValidationError(f"{name} must have length {size}, got {len(result)}")
    return result


def matrix(values: Any, name: str, *, rows: int | None = None, cols: int | None = None) -> Matrix:
    raw = sequence(values, name)
    if not raw:
        raise ValidationError(f"{name} must have at least one row")
    result = tuple(vector(row, name + " row") for row in raw)
    width = len(result[0])
    if not width or any(len(row) != width for row in result):
        raise ValidationError(f"{name} must be rectangular with at least one column")
    if rows is not None and len(result) != rows:
        raise ValidationError(f"{name} must have {rows} rows")
    if cols is not None and width != cols:
        raise ValidationError(f"{name} must have {cols} columns")
    return result


def transpose(a: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] for i in range(len(a))) for j in range(len(a[0])))


def matvec(a: Matrix, x: Vector) -> Vector:
    if len(a[0]) != len(x):
        raise ValidationError("Matrix/vector dimensions do not agree")
    return tuple(sum((c * v for c, v in zip(row, x)), Fraction(0)) for row in a)


def matmul(a: Matrix, b: Matrix) -> Matrix:
    if len(a[0]) != len(b):
        raise ValidationError("Matrix multiplication dimensions do not agree")
    bt = transpose(b)
    return tuple(tuple(sum((x * y for x, y in zip(row, col)), Fraction(0)) for col in bt) for row in a)


def identity(n: int) -> Matrix:
    return tuple(tuple(Fraction(int(i == j)) for j in range(n)) for i in range(n))


def subtract(a: Matrix, b: Matrix) -> Matrix:
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise ValidationError("Matrix subtraction dimensions do not agree")
    return tuple(tuple(x - y for x, y in zip(row_a, row_b)) for row_a, row_b in zip(a, b))


def is_zero(a: Matrix) -> bool:
    return all(v == 0 for row in a for v in row)


def solve_exact(a: Matrix, b: Vector) -> Vector | None:
    """Rational Gaussian elimination, with free variables set to zero.

    None means the finite rational linear system is inconsistent, not that a
    numerical solver timed out. Public entry points validate the dimensions.
    """
    if len(a) != len(b):
        raise ValidationError("Linear system dimensions do not agree")
    m, n = len(a), len(a[0])
    work = [list(row) + [rhs] for row, rhs in zip(a, b)]
    pivot_columns: list[int] = []
    pivot_row = 0
    for col in range(n):
        chosen = next((r for r in range(pivot_row, m) if work[r][col] != 0), None)
        if chosen is None:
            continue
        work[pivot_row], work[chosen] = work[chosen], work[pivot_row]
        pivot = work[pivot_row][col]
        work[pivot_row] = [v / pivot for v in work[pivot_row]]
        for r in range(m):
            if r != pivot_row:
                factor = work[r][col]
                work[r] = [v - factor * p for v, p in zip(work[r], work[pivot_row])]
        pivot_columns.append(col)
        pivot_row += 1
        if pivot_row == m:
            break
    if any(all(v == 0 for v in row[:n]) and row[n] != 0 for row in work):
        return None
    solution = [Fraction(0)] * n
    for r, col in enumerate(pivot_columns):
        solution[col] = work[r][n]
    return tuple(solution)


def verify_l1_certificate(D: Any, h: Any, weights: Any, potential: Any, dual: Any) -> dict[str, Any]:
    """Check supplied primal/dual evidence for min_x sum w[e]*abs(h[e]-(Dx)[e]).

    Does not search for a certificate. Every comparison uses exact arithmetic.
    Nonempty finite rational matrices and strictly positive weights are required.
    """
    d = matrix(D, "D")
    m, n = len(d), len(d[0])
    hv, w, x, z = (vector(h, "h", m), vector(weights, "weights", m),
                    vector(potential, "potential", n), vector(dual, "dual", m))
    if any(v <= 0 for v in w):
        raise ValidationError("All weights must be strictly positive")
    dx = matvec(d, x)
    residual = tuple(a - b for a, b in zip(hv, dx))
    annihilator = matvec(transpose(d), z)
    bounded = all(abs(a) <= b for a, b in zip(z, w))
    annihilates = all(v == 0 for v in annihilator)
    lower = sum((a * b for a, b in zip(z, hv)), Fraction(0))
    upper = sum((weight * abs(r) for weight, r in zip(w, residual)), Fraction(0))
    valid = bounded and annihilates
    matched = valid and lower == upper
    status = "OPTIMALITY_VERIFIED" if matched else "LOWER_BOUND_VERIFIED" if valid else "INVALID_CERTIFICATE"
    result = {"schema": "lggr.l1.v1", "authority_effect": "None", "status": status,
              "input_sha256": digest({"D": d, "h": hv, "weights": w, "potential": x, "dual": z}),
              "dual_bounded": bounded, "dual_annihilates": annihilates,
              "D_transpose_dual": annihilator, "residual": residual,
              "lower_bound": lower if valid else None, "upper_bound": upper,
              "duality_gap": upper - lower if valid else None,
              "optimum": upper if matched else None,
              "repair_impossible": valid and lower > 0,
              "supplied_potential_repairs": all(v == 0 for v in residual),
              "scope": "The supplied finite rational repair problem only; not an embedding of arbitrary software drift."}
    return json_value(result)


def classify_cochain(D0: Any, h: Any, D1: Any | None = None) -> dict[str, Any]:
    """Separate exactness, closure failure and a nonzero first cohomology class.

    D1=None means no degree-two structure has been supplied: no H^1 claim.
    D1=[] explicitly declares C^2={0}, i.e. the unfilled graph case.
    """
    d0 = matrix(D0, "D0")
    hv = vector(h, "h", len(d0))
    solution = solve_exact(d0, hv)
    result: dict[str, Any] = {"schema": "lggr.cochain.v1", "authority_effect": "None",
                              "input_sha256": digest({"D0": D0, "h": h, "D1": D1}),
                              "repair_exists": solution is not None,
                              "potential": solution, "closure": None,
                              "represents_nonzero_H1": None}
    if D1 is None:
        return json_value({**result, "status": "EXACT_REPAIR" if solution is not None else "NONREPAIRABLE",
                           "meaning": "No degree-two structure was supplied; no cohomology classification is made."})
    raw_d1 = sequence(D1, "D1")
    if raw_d1:
        d1 = matrix(raw_d1, "D1", cols=len(d0))
        composition = matmul(d1, d0)
        if not is_zero(composition):
            return json_value({**result, "status": "INVALID_COMPLEX", "D1_D0": composition})
        closure = matvec(d1, hv)
    else:
        closure = ()
    closed = all(v == 0 for v in closure)
    status = ("CLOSURE_FAILURE" if not closed else "EXACT" if solution is not None else "CLOSED_NONEXACT")
    return json_value({**result, "status": status, "closure": closure,
                       "represents_nonzero_H1": closed and solution is None})
