"""Tests for exact rational cochain obstruction solver over Q."""
from __future__ import annotations

from fractions import Fraction

import pytest
from code_exact_obstruction import (
    FiniteCochainComplex,
    Verdict,
    _encoded_matrix,
    _encoded_vector,
    _matmul,
    _matrix,
    _scalar,
    _solve_exact,
    _transpose,
    analyze_finite_cochain,
    coerce_vector,
    self_check,
    solve_exact_repair,
    solve_finite_cochain_obstruction,
)
from code_quotient_solver import QuotientDistanceSolver


def test_scalar_validation() -> None:
    assert _scalar(5) == Fraction(5)
    assert _scalar("3/7") == Fraction(3, 7)
    assert _scalar(Fraction(2, 5)) == Fraction(2, 5)

    with pytest.raises(TypeError, match="floating point is forbidden"):
        _scalar(1.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="floating point is forbidden"):
        _scalar(True)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="unsupported exact scalar"):
        _scalar([1, 2])  # type: ignore


def test_vector_and_matrix_coercion() -> None:
    v = coerce_vector([1, "2", Fraction(3)], 3, "test_v")
    assert v == (Fraction(1), Fraction(2), Fraction(3))

    with pytest.raises(ValueError, match="has length 2; expected 3"):
        coerce_vector([1, 2], 3, "test_v")

    m = _matrix([[1, 2], [3, 4]], 2, 2, "test_m")
    assert m == ((Fraction(1), Fraction(2)), (Fraction(3), Fraction(4)))

    with pytest.raises(ValueError, match="has 1 rows; expected 2"):
        _matrix([[1, 2]], 2, 2, "test_m")


def test_matmul_and_transpose() -> None:
    assert _matmul((), (), 0) == ()
    left = ((Fraction(1), Fraction(2)), (Fraction(3), Fraction(4)))
    right = ((Fraction(5), Fraction(6)), (Fraction(7), Fraction(8)))
    res = _matmul(left, right, 2)
    assert res == ((Fraction(19), Fraction(22)), (Fraction(43), Fraction(50)))

    t = _transpose(left, 2, 2)
    assert t == ((Fraction(1), Fraction(3)), (Fraction(2), Fraction(4)))


def test_solve_exact_edge_cases() -> None:
    # Empty system
    assert _solve_exact((), (), 3) == (Fraction(0), Fraction(0), Fraction(0))

    # Inconsistent system: 0*x = 1
    mat_inconsistent = ((Fraction(0),),)
    rhs_inconsistent = (Fraction(1),)
    assert _solve_exact(mat_inconsistent, rhs_inconsistent, 1) is None

    # Redundant row that matches equation count
    mat_redundant = ((Fraction(1), Fraction(1)), (Fraction(2), Fraction(2)))
    rhs_redundant = (Fraction(3), Fraction(6))
    sol = _solve_exact(mat_redundant, rhs_redundant, 2)
    assert sol is not None
    assert sol[0] + sol[1] == Fraction(3)


def test_encoded_helpers() -> None:
    assert _encoded_vector(None) is None
    assert _encoded_vector((Fraction(1, 2), Fraction(3, 4))) == ["1/2", "3/4"]
    mat = ((Fraction(1, 3),),)
    assert _encoded_matrix(mat) == [["1/3"]]


def test_finite_cochain_complex_validation() -> None:
    with pytest.raises(ValueError, match="dimensions must be three nonnegative integers"):
        FiniteCochainComplex.from_rows((1, 2), (), ())  # type: ignore
    with pytest.raises(ValueError, match="dimensions must be three nonnegative integers"):
        FiniteCochainComplex.from_rows((1, 2, True), (), ())  # type: ignore
    with pytest.raises(ValueError, match="dimensions must be three nonnegative integers"):
        FiniteCochainComplex.from_rows((1, 2, -1), (), ())

    complex_ = FiniteCochainComplex.from_rows(
        (2, 2, 1),
        ((1, 0), (0, 1)),
        ((1, -1),),
    )
    assert complex_.c0_dimension == 2
    assert complex_.c1_dimension == 2
    assert complex_.c2_dimension == 1


def test_analyze_finite_cochain_verdicts() -> None:
    # 1. Invalid complex: d1 @ d0 != 0
    bad_complex = FiniteCochainComplex.from_rows(
        (1, 1, 1),
        ((1,),),
        ((1,),),
    )
    res_bad = analyze_finite_cochain(bad_complex, (1,))
    assert res_bad.verdict == Verdict.INVALID_COMPLEX

    # 2. Triangle cycle complex
    # C0: 3 vertices, C1: 3 edges, C2: 1 face
    # d0: e01 = v1 - v0, e12 = v2 - v1, e20 = v2 - v0
    # d1: e01 + e12 - e20 = 0
    triangle = FiniteCochainComplex.from_rows(
        (3, 3, 1),
        ((-1, 1, 0), (0, -1, 1), (-1, 0, 1)),
        ((1, 1, -1),),
    )

    # EXACT_REPAIR: beta = d0 @ (1, 2, 3) = (1, 1, 2)
    res_exact = solve_finite_cochain_obstruction(triangle, (1, 1, 2))
    assert res_exact.verdict == Verdict.EXACT_REPAIR
    assert res_exact.primitive_witness is not None
    assert res_exact.period_witness is None

    # CURVATURE: d1 @ beta != 0
    res_curv = analyze_finite_cochain(triangle, (1, 2, 4))
    assert res_curv.verdict == Verdict.CURVATURE

    # 3. Non-trivial 1-homology (unfilled cycle / torus):
    # C0: 3 vertices, C1: 3 edges, C2: 0 faces (c2_dimension = 0)
    torus_cycle = FiniteCochainComplex.from_rows(
        (3, 3, 0),
        ((-1, 1, 0), (0, -1, 1), (1, 0, -1)),  # closed directed cycle
        (),
    )
    # Closed 1-cochain (1, 1, 1) has zero boundary on empty C2, but cannot be repaired by d0
    res_closed = analyze_finite_cochain(torus_cycle, (1, 1, 1))
    assert res_closed.verdict == Verdict.CLOSED_RESIDUAL
    assert res_closed.primitive_witness is None
    assert res_closed.period_witness is not None
    assert res_closed.period_pairing == Fraction(1)
    assert res_closed.period_is_boundary is False


def test_solve_exact_repair_nearly_dependent_r1() -> None:
    # R1 ill-conditioned matrix:
    # D = [[1, 1], [0, 1e-13]], omega = [0, 1]
    D = (
        (Fraction(1), Fraction(1)),
        (Fraction(0), Fraction(1, 10**13)),
    )
    omega = (Fraction(0), Fraction(1))

    alpha, res = solve_exact_repair(D, omega)
    assert alpha == (Fraction(-10**13), Fraction(10**13))
    assert res == (Fraction(0), Fraction(0))

    # Solver bridge via QuotientDistanceSolver
    alpha_bridge, res_bridge = QuotientDistanceSolver.solve_exact(omega, D)
    assert alpha_bridge == alpha
    assert res_bridge == res


def test_solve_exact_repair_inconsistent_and_empty() -> None:
    # Inconsistent
    D_inconsistent = ((Fraction(1),), (Fraction(1),))
    omega_inconsistent = (Fraction(1), Fraction(2))
    alpha_none, res_same = solve_exact_repair(D_inconsistent, omega_inconsistent)
    assert alpha_none is None
    assert res_same == (Fraction(1), Fraction(2))

    # Empty
    alpha_empty, res_empty = solve_exact_repair((), ())
    assert alpha_empty == ()
    assert res_empty == ()


def test_empty_space_complex_defect_and_dimensions() -> None:
    """Item 7 Regression: (3, 0, 2) complex must report 2 rows of 3 exact rational zeros."""
    c = FiniteCochainComplex.from_rows((3, 0, 2), (), ((), ()))
    defect = c.complex_defect()
    assert len(defect) == 2
    assert all(len(row) == 3 for row in defect)
    assert defect == (
        (Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0)),
    )
    result = analyze_finite_cochain(c, ())
    assert result.verdict == Verdict.EXACT_REPAIR
    assert result.primitive_witness == (Fraction(0), Fraction(0), Fraction(0))
    assert result.closure_defect == (Fraction(0), Fraction(0))


def test_solve_exact_repair_empty_rhs_mismatch() -> None:
    """Item 7 Regression: Nonempty matrix with empty RHS must raise dimension error."""
    with pytest.raises(ValueError, match="Dimension mismatch"):
        solve_exact_repair(((Fraction(1),),), ())


def test_self_check() -> None:
    self_check()


def test_internal_assertions_defensive_firewalls(monkeypatch: pytest.MonkeyPatch) -> None:
    import code_exact_obstruction as ceo

    real_solve = ceo._solve_exact
    real_matvec = ceo._matvec
    real_dot = ceo._dot

    triangle = ceo.FiniteCochainComplex.from_rows(
        (3, 3, 1),
        ((-1, 1, 0), (0, -1, 1), (-1, 0, 1)),
        ((1, 1, -1),),
    )

    torus = ceo.FiniteCochainComplex.from_rows(
        (3, 3, 0),
        ((-1, 1, 0), (0, -1, 1), (1, 0, -1)),
        (),
    )

    # 1. Nonclosed exact cochain (line 268)
    monkeypatch.setattr(ceo, "_solve_exact", lambda m, rhs, v: (Fraction(1), Fraction(1), Fraction(1)))
    with pytest.raises(AssertionError, match="valid complex produced a nonclosed exact cochain"):
        ceo.analyze_finite_cochain(triangle, (1, 2, 4))

    # 2. Internal exact solver produced an invalid witness (line 273)
    monkeypatch.setattr(ceo, "_solve_exact", lambda m, rhs, v: (Fraction(999), Fraction(999), Fraction(999)))
    with pytest.raises(AssertionError, match="internal exact solver produced an invalid witness"):
        ceo.analyze_finite_cochain(triangle, (1, 1, 2))

    # 3. Closed nonexact cochain has no dual period witness (line 291)
    call_count = 0
    def mock_no_period(m, rhs, v):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return None  # primitive_witness is None
        return None  # period_witness is None
    monkeypatch.setattr(ceo, "_solve_exact", mock_no_period)
    with pytest.raises(AssertionError, match="closed nonexact cochain has no dual period witness"):
        ceo.analyze_finite_cochain(torus, (1, 1, 1))

    # 4. Period witness is not a 1-cycle (line 304)
    monkeypatch.setattr(ceo, "_solve_exact", real_solve)
    def mock_matvec(m, v):
        if len(m) == 3 and len(v) == 3 and m[0][0] == Fraction(-1):
            return (Fraction(1), Fraction(0), Fraction(0))
        return real_matvec(m, v)
    monkeypatch.setattr(ceo, "_matvec", mock_matvec)
    with pytest.raises(AssertionError, match="period witness is not a 1-cycle"):
        ceo.analyze_finite_cochain(torus, (1, 1, 1))

    # 5. Period witness has zero pairing (line 306)
    monkeypatch.setattr(ceo, "_matvec", real_matvec)
    monkeypatch.setattr(ceo, "_dot", lambda left, right: Fraction(0))
    with pytest.raises(AssertionError, match="period witness has zero pairing"):
        ceo.analyze_finite_cochain(torus, (1, 1, 1))

    # 6. Period witness is a 2-boundary (line 308)
    monkeypatch.setattr(ceo, "_dot", real_dot)
    def mock_boundary(m, rhs, v):
        if v == 0 and len(m) == 3:
            return ()
        return real_solve(m, rhs, v)
    monkeypatch.setattr(ceo, "_solve_exact", mock_boundary)
    with pytest.raises(AssertionError, match="period witness is a 2-boundary"):
        ceo.analyze_finite_cochain(torus, (1, 1, 1))

