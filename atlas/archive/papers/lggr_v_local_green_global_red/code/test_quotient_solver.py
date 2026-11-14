"""Tests for certified quotient distance solver across Minkowski norms."""
from __future__ import annotations

import warnings

import numpy as np
import pytest
from code_quotient_solver import MinkowskiNorm, QuotientDistanceSolver, QuotientResult


def test_minkowski_norm_from_value():
    assert MinkowskiNorm.from_value(MinkowskiNorm.L1) == MinkowskiNorm.L1
    assert MinkowskiNorm.from_value(1) == MinkowskiNorm.L1
    assert MinkowskiNorm.from_value(1.0) == MinkowskiNorm.L1
    assert MinkowskiNorm.from_value("1") == MinkowskiNorm.L1
    assert MinkowskiNorm.from_value("l1") == MinkowskiNorm.L1
    assert MinkowskiNorm.from_value("taxicab") == MinkowskiNorm.L1
    assert MinkowskiNorm.from_value("manhattan") == MinkowskiNorm.L1

    assert MinkowskiNorm.from_value(2) == MinkowskiNorm.L2
    assert MinkowskiNorm.from_value(2.0) == MinkowskiNorm.L2
    assert MinkowskiNorm.from_value("2") == MinkowskiNorm.L2
    assert MinkowskiNorm.from_value("l2") == MinkowskiNorm.L2
    assert MinkowskiNorm.from_value("euclidean") == MinkowskiNorm.L2
    assert MinkowskiNorm.from_value("hilbert") == MinkowskiNorm.L2

    assert MinkowskiNorm.from_value(float("inf")) == MinkowskiNorm.L_INF
    assert MinkowskiNorm.from_value("inf") == MinkowskiNorm.L_INF
    assert MinkowskiNorm.from_value("linf") == MinkowskiNorm.L_INF
    assert MinkowskiNorm.from_value("infinity") == MinkowskiNorm.L_INF
    assert MinkowskiNorm.from_value("chebyshev") == MinkowskiNorm.L_INF
    assert MinkowskiNorm.from_value("max") == MinkowskiNorm.L_INF

    with pytest.raises(ValueError, match="Unsupported Minkowski norm"):
        MinkowskiNorm.from_value(3)
    with pytest.raises(ValueError, match="Unsupported Minkowski norm"):
        MinkowskiNorm.from_value("l3")


def test_quotient_solver_shape_mismatch():
    omega = np.array([1.0, 2.0])
    D = np.array([[1.0], [2.0], [3.0]])
    with pytest.raises(ValueError, match="Shape mismatch"):
        QuotientDistanceSolver.solve(omega, D)


def test_quotient_solver_1d_input():
    omega = np.array([1.0, -1.0])
    D_1d = np.array([-1.0, -1.0])  # 1D array should be auto-reshaped
    res = QuotientDistanceSolver.solve(omega, D_1d, norm=MinkowskiNorm.L1)
    assert abs(res.primal_distance - 2.0) < 1e-5
    assert res.is_numerically_certified is True
    assert res.is_exact_certified is True
    # Test verify_certificate with 1D D_arr
    assert QuotientDistanceSolver.verify_certificate(omega, D_1d, res) is True


def test_scalar_quotient_witness_all_minkowski_norms():
    omega = np.array([1.0, -1.0])
    D = np.array([[-1.0], [-1.0]])

    # L1: dist = 2.0 (alpha in [-1, 1])
    res_l1 = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
    assert abs(res_l1.primal_distance - 2.0) < 1e-5
    assert abs(res_l1.duality_gap) < 1e-5
    assert res_l1.is_numerically_certified is True
    assert QuotientDistanceSolver.verify_certificate(omega, D, res_l1) is True

    # L2: dist = sqrt(2) approx 1.41421356 (alpha = 0)
    res_l2 = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2)
    assert abs(res_l2.primal_distance - np.sqrt(2.0)) < 1e-5
    assert abs(res_l2.duality_gap) < 1e-5
    assert res_l2.is_numerically_certified is True
    assert QuotientDistanceSolver.verify_certificate(omega, D, res_l2) is True

    # L_inf: dist = 1.0 (alpha = 0)
    res_linf = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L_INF)
    assert abs(res_linf.primal_distance - 1.0) < 1e-5
    assert abs(res_linf.duality_gap) < 1e-5
    assert res_linf.is_numerically_certified is True
    assert QuotientDistanceSolver.verify_certificate(omega, D, res_linf) is True

    # Minkowski chain verification
    assert res_linf.primal_distance <= res_l2.primal_distance + 1e-9
    assert res_l2.primal_distance <= res_l1.primal_distance + 1e-9


def test_exact_coboundary_zero_distance():
    D = np.array([[-1.0], [-1.0]])
    alpha_true = 3.5
    omega_coboundary = D @ np.array([alpha_true])

    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF]:
        res = QuotientDistanceSolver.solve(omega_coboundary, D, norm=norm)
        assert abs(res.primal_distance) < 1e-5
        assert abs(res.duality_gap) < 1e-5
        assert res.is_numerically_certified is True
        assert QuotientDistanceSolver.verify_certificate(omega_coboundary, D, res) is True


def test_verify_certificate_adversarial_rejections():
    omega = np.array([1.0, -1.0])
    D = np.array([[-1.0], [-1.0]])
    res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)

    # 1. Corrupted residual
    bad_res = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=np.array([0.0, 0.0]),
        dual_witness=res.dual_witness,
        dual_objective=res.dual_objective,
        duality_gap=res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_res) is False

    # 2. Corrupted primal distance (different from expected norm of residual)
    bad_dist = QuotientResult(
        norm=res.norm,
        primal_distance=99.0,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=res.dual_objective,
        duality_gap=res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_dist) is False

    # 3. Corrupted dual witness norm (> 1.0)
    bad_witness = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=np.array([2.0, -2.0]),
        dual_objective=res.dual_objective,
        duality_gap=res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_witness) is False

    # 4. Corrupted orthogonality
    bad_ortho = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=np.array([1.0, 0.0]),
        dual_objective=res.dual_objective,
        duality_gap=res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_ortho) is False

    # 5. Corrupted dual objective value
    bad_obj = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=0.0,
        duality_gap=2.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_obj) is False

    # 6. Corrupted duality gap mismatch (<W, omega> != primal_distance)
    QuotientResult(
        norm=res.norm,
        primal_distance=10.0,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=res.dual_objective,
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    # Monkeypatch residual to match primal_dist 10.0
    QuotientResult(
        norm=res.norm,
        primal_distance=10.0,
        optimal_alpha=res.optimal_alpha,
        residual=np.array([5.0, 5.0]),
        dual_witness=res.dual_witness,
        dual_objective=float(np.dot(res.dual_witness, omega)),
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    # expected_r is omega - D alpha = [1, -1] - 0 = [1, -1], so bad_gap2 fails residual check
    # Instead, let's create a case where residual matches, expected_dist matches, but primal_distance != computed_dual_obj
    bad_gap3 = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=np.array([0.5, -0.5]),  # ||W||_inf = 0.5 <= 1, D^T W = 0, but <W, omega> = 1.0 != 2.0
        dual_objective=1.0,
        duality_gap=1.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_gap3) is False

    # 7. Corrupted duality gap field (e.g. 12345.0)
    bad_gap_num = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=res.dual_objective,
        duality_gap=12345.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_gap_num) is False

    # 8. Invalid non-positive or non-finite tolerances
    assert QuotientDistanceSolver.verify_certificate(omega, D, res, tol=-1e-5) is False
    assert QuotientDistanceSolver.verify_certificate(omega, D, res, tol=0.0) is False
    assert QuotientDistanceSolver.verify_certificate(omega, D, res, tol=float("nan")) is False

    # 9. Invalid norm object
    bad_norm_res = QuotientResult(
        norm="invalid_norm",  # type: ignore
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=res.dual_objective,
        duality_gap=res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_norm_res) is False

    # 10. Dimension mismatches in alpha or dual witness
    bad_dim_alpha = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=np.array([1.0, 2.0]),  # Expected shape (1,)
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=res.dual_objective,
        duality_gap=res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_dim_alpha) is False

    # 11. Fake dual witness not annihilating column with small norm
    fake_scalar = QuotientResult(
        norm=MinkowskiNorm.L1,
        primal_distance=1.0,
        optimal_alpha=np.array([0.0]),
        residual=np.array([1.0]),
        dual_witness=np.array([1.0]),
        dual_objective=1.0,
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(np.array([1.0]), np.array([[1e-10]]), fake_scalar) is False

    # 12. Dimension mismatch on D rows or D ndim > 2
    assert QuotientDistanceSolver.verify_certificate(omega, np.zeros((len(omega) + 1, 1)), res) is False
    assert QuotientDistanceSolver.verify_certificate(omega, np.zeros((len(omega), 1, 1)), res) is False

    # 13. Dual objective in result does not match computed dot product <W, omega>
    bogus_dual_obj = res.dual_objective + 0.5
    bad_dual_dot = QuotientResult(
        norm=res.norm,
        primal_distance=res.primal_distance,
        optimal_alpha=res.optimal_alpha,
        residual=res.residual,
        dual_witness=res.dual_witness,
        dual_objective=bogus_dual_obj,
        duality_gap=abs(res.primal_distance - bogus_dual_obj),
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_dual_dot) is False


def test_linprog_failure_branches(monkeypatch):
    omega = np.array([1.0, -1.0])
    D = np.array([[-1.0], [-1.0]])

    class FakeLinprogResult:
        success = False
        message = "Mocked optimizer failure"

    monkeypatch.setattr("scipy.optimize.linprog", lambda *args, **kwargs: FakeLinprogResult())

    with pytest.raises(RuntimeError, match="L1 linear programming failed"):
        QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)

    with pytest.raises(RuntimeError, match="L_inf linear programming failed"):
        QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L_INF)


def test_coordinate_signed_permutation_isometry_invariance():
    rng = np.random.default_rng(42)
    m, n = 5, 2
    D = rng.standard_normal((m, n))
    omega = rng.standard_normal(m)

    # Solve base problem
    res_l1_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
    res_l2_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2)
    res_linf_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L_INF)

    # Construct coordinate signed permutation matrix P
    perm = rng.permutation(m)
    signs = rng.choice([-1.0, 1.0], size=m)
    P = np.diag(signs)[perm, :]

    omega_iso = P @ omega
    D_iso = P @ D

    res_l1_iso = QuotientDistanceSolver.solve(omega_iso, D_iso, norm=MinkowskiNorm.L1)
    res_l2_iso = QuotientDistanceSolver.solve(omega_iso, D_iso, norm=MinkowskiNorm.L2)
    res_linf_iso = QuotientDistanceSolver.solve(omega_iso, D_iso, norm=MinkowskiNorm.L_INF)

    assert abs(res_l1_iso.primal_distance - res_l1_base.primal_distance) < 1e-5
    assert abs(res_l2_iso.primal_distance - res_l2_base.primal_distance) < 1e-5
    assert abs(res_linf_iso.primal_distance - res_linf_base.primal_distance) < 1e-5


def test_coordinate_so2_rotation_isometry_invariance():
    _m, _n = 2, 1
    D = np.array([[1.5], [-0.5]])
    omega = np.array([2.0, 3.0])

    res_l2_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2)

    theta = np.pi / 3.0
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])

    omega_rot = R @ omega
    D_rot = R @ D

    res_l2_rot = QuotientDistanceSolver.solve(omega_rot, D_rot, norm=MinkowskiNorm.L2)
    assert abs(res_l2_rot.primal_distance - res_l2_base.primal_distance) < 1e-5


def test_source_gauge_basis_change_invariance():
    rng = np.random.default_rng(123)
    m, n = 4, 2
    D = rng.standard_normal((m, n))
    omega = rng.standard_normal(m)

    res_l1_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
    res_l2_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2)
    res_linf_base = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L_INF)

    M = rng.standard_normal((n, n))
    while abs(np.linalg.det(M)) < 0.1:
        M = rng.standard_normal((n, n))

    D_gauged = D @ M

    res_l1_gauged = QuotientDistanceSolver.solve(omega, D_gauged, norm=MinkowskiNorm.L1)
    res_l2_gauged = QuotientDistanceSolver.solve(omega, D_gauged, norm=MinkowskiNorm.L2)
    res_linf_gauged = QuotientDistanceSolver.solve(omega, D_gauged, norm=MinkowskiNorm.L_INF)

    assert abs(res_l1_gauged.primal_distance - res_l1_base.primal_distance) < 1e-5
    assert abs(res_l2_gauged.primal_distance - res_l2_base.primal_distance) < 1e-5
    assert abs(res_linf_gauged.primal_distance - res_linf_base.primal_distance) < 1e-5


def test_quotient_distance_subadditivity_and_strict_subadditivity():
    _m, _n = 2, 1
    D = np.array([[-1.0], [-1.0]])

    omega_1 = np.array([1.0, -1.0])
    omega_2 = np.array([-1.0, 1.0])
    omega_sum = omega_1 + omega_2  # [0, 0]

    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF]:
        res_1 = QuotientDistanceSolver.solve(omega_1, D, norm=norm)
        res_2 = QuotientDistanceSolver.solve(omega_2, D, norm=norm)
        res_sum = QuotientDistanceSolver.solve(omega_sum, D, norm=norm)

        # General subadditivity
        assert res_sum.primal_distance <= res_1.primal_distance + res_2.primal_distance + 1e-7

        # Strict subadditivity: dist(sum) = 0 < dist(1) + dist(2)
        assert res_sum.primal_distance < res_1.primal_distance + res_2.primal_distance - 0.5


def test_nonlinear_contractive_evaluation_bound():
    """Verify non-linear contractive evaluation map bounds: ||Psi(omega) - Psi(D alpha)||_p <= ||omega - D alpha||_p."""
    _m, _n = 3, 1
    D = np.array([[-1.0], [-1.0], [0.5]])
    omega = np.array([1.0, -1.0, 2.0])

    res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
    alpha_opt = res.optimal_alpha

    # Non-linear contractive maps: tanh, relu, clamp[-1, 1]
    def psi_tanh(x): return np.tanh(x)
    def psi_relu(x): return np.maximum(0.0, x)
    def psi_clamp(x): return np.clip(x, -1.0, 1.0)

    for psi in [psi_tanh, psi_relu, psi_clamp]:
        # Contractivity: ||psi(u) - psi(v)||_1 <= ||u - v||_1
        obs_discrepancy = np.sum(np.abs(psi(omega) - psi(D @ alpha_opt)))
        raw_discrepancy = np.sum(np.abs(omega - D @ alpha_opt))
        assert obs_discrepancy <= raw_discrepancy + 1e-9


def test_nonlinear_lipschitz_evaluation_bound():
    """Verify non-linear L-Lipschitz evaluation map bounds: ||Psi(omega) - Psi(D alpha)||_p <= L * ||omega - D alpha||_p."""
    D = np.array([[-1.0], [-1.0]])
    omega = np.array([1.0, -1.0])

    res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2)
    alpha_opt = res.optimal_alpha

    # Sigmoid has Lipschitz constant L = 0.25; 2 * sigmoid has L = 0.5
    def psi_sigmoid2(x): return 2.0 / (1.0 + np.exp(-x))
    L = 0.5

    obs_l2 = float(np.linalg.norm(psi_sigmoid2(omega) - psi_sigmoid2(D @ alpha_opt), ord=2))
    raw_l2 = float(np.linalg.norm(omega - D @ alpha_opt, ord=2))
    assert obs_l2 <= L * raw_l2 + 1e-9


def test_nonlinear_perturbed_manifold_quotient_bounds():
    """Verify quotient distance bounds under non-linear transverse perturbations m_nl(alpha) = D alpha + eps * p(alpha)."""
    D = np.array([[-1.0], [-1.0]])
    omega = np.array([1.0, -1.0])
    res_linear = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
    linear_dist = res_linear.primal_distance

    eps = 0.05
    # Transverse perturbation p(alpha) = [sin(alpha), 0]^T with ||p(alpha)||_1 = |sin(alpha)| <= 1.
    # The perturbation shifts points transversely off the diagonal range of D.
    alphas = np.linspace(-3, 3, 601)
    nl_distances = [
        float(np.sum(np.abs(omega - (D @ np.array([a]) + eps * np.array([np.sin(a), 0.0])))))
        for a in alphas
    ]
    min_nl_dist = min(nl_distances)

    # Transverse perturbation triangle inequality bound: |dist_nl - dist_linear| <= max_alpha ||eps * p(alpha)||_1 <= eps
    assert abs(min_nl_dist - linear_dist) <= eps + 1e-5


def test_verify_certificate_rejects_nonfinite_certificates():
    """Verify that candidate certificates with non-finite values (NaN, inf) are rejected."""
    omega = np.array([1.0, -1.0])
    D = np.array([[-1.0], [-1.0]])
    valid_res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)

    # 1. NaN in primal_distance
    bad_dist_nan = QuotientResult(
        norm=valid_res.norm,
        primal_distance=float("nan"),
        optimal_alpha=valid_res.optimal_alpha,
        residual=valid_res.residual,
        dual_witness=valid_res.dual_witness,
        dual_objective=valid_res.dual_objective,
        duality_gap=valid_res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_dist_nan) is False

    # 2. NaN in dual_objective
    bad_dual_nan = QuotientResult(
        norm=valid_res.norm,
        primal_distance=valid_res.primal_distance,
        optimal_alpha=valid_res.optimal_alpha,
        residual=valid_res.residual,
        dual_witness=valid_res.dual_witness,
        dual_objective=float("nan"),
        duality_gap=valid_res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_dual_nan) is False

    # 3. NaN in optimal_alpha
    bad_alpha_nan = QuotientResult(
        norm=valid_res.norm,
        primal_distance=valid_res.primal_distance,
        optimal_alpha=np.array([float("nan")]),
        residual=valid_res.residual,
        dual_witness=valid_res.dual_witness,
        dual_objective=valid_res.dual_objective,
        duality_gap=valid_res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_alpha_nan) is False

    # 4. NaN in residual
    bad_res_nan = QuotientResult(
        norm=valid_res.norm,
        primal_distance=valid_res.primal_distance,
        optimal_alpha=valid_res.optimal_alpha,
        residual=np.array([float("nan"), 0.0]),
        dual_witness=valid_res.dual_witness,
        dual_objective=valid_res.dual_objective,
        duality_gap=valid_res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_res_nan) is False

    # 5. NaN in dual_witness
    bad_witness_nan = QuotientResult(
        norm=valid_res.norm,
        primal_distance=valid_res.primal_distance,
        optimal_alpha=valid_res.optimal_alpha,
        residual=valid_res.residual,
        dual_witness=np.array([float("nan"), 0.0]),
        dual_objective=valid_res.dual_objective,
        duality_gap=valid_res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_witness_nan) is False

    # 6. Inf in dual_witness
    bad_witness_inf = QuotientResult(
        norm=valid_res.norm,
        primal_distance=valid_res.primal_distance,
        optimal_alpha=valid_res.optimal_alpha,
        residual=valid_res.residual,
        dual_witness=np.array([float("inf"), 0.0]),
        dual_objective=valid_res.dual_objective,
        duality_gap=valid_res.duality_gap,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, bad_witness_inf) is False

    # 7. Non-finite input data (omega or D)
    assert QuotientDistanceSolver.verify_certificate(np.array([float("nan"), 0.0]), D, valid_res) is False
    assert QuotientDistanceSolver.verify_certificate(omega, np.array([[float("nan")], [0.0]]), valid_res) is False


def test_scalar_tiny_column_zero_quotient_distance():
    """F1 Regression: For D = [1e-10], omega = [1.0], true quotient distance is 0.0 and must be certified."""
    omega = np.array([1.0])
    D = np.array([[1e-10]])
    for norm in MinkowskiNorm:
        r = QuotientDistanceSolver.solve(omega, D, norm=norm)
        assert r.primal_distance == 0.0
        assert r.is_numerically_certified is True
        assert r.is_exact_certified is True  # deprecated alias
        assert QuotientDistanceSolver.verify_certificate(omega, D, r) is True
        # Check optimal alpha is 1e10
        assert np.allclose(r.optimal_alpha, [1e10], rtol=1e-5)
        assert np.allclose(r.residual, [0.0], atol=1e-7)


def test_scalar_source_basis_rescaling_invariance():
    """Verify that quotient distance on scalar problem is invariant under non-zero source column rescaling."""
    omega = np.array([2.0])
    for gamma in [1e-12, 1e-10, 1e-6, 1e-3, 1.0, 1e3, 1e6]:
        D = np.array([[gamma]])
        r = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
        assert r.primal_distance == 0.0
        assert r.is_numerically_certified is True
        assert QuotientDistanceSolver.verify_certificate(omega, D, r) is True
        assert np.allclose(D @ r.optimal_alpha, omega, atol=1e-7)


def test_nearly_dependent_columns_unresolved_certification():
    """R1 Regression: D = [[1, 1], [0, 1e-13]], omega = [0, 1] is nearly dependent with true distance 0.

    When numerical LP solver does not resolve alpha = [-1e13, 1e13] and returns positive distance,
    it must NOT certify the result, and independent verification must reject it.
    """
    D = np.array([[1.0, 1.0], [0.0, 1e-13]])
    omega = np.array([0.0, 1.0])
    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L_INF]:
        r = QuotientDistanceSolver.solve(omega, D, norm=norm)
        assert r.is_numerically_certified is False
        assert QuotientDistanceSolver.verify_certificate(omega, D, r) is False


def test_tiny_column_verifier_bypass_rejected():
    """R1 Regression: Verifier must reject fake certificates for tiny columns (D=[1e-15], D=[1e-14])
    and nearly dependent matrices rather than skipping them with a col_norm threshold.
    """
    fake = QuotientResult(
        norm=MinkowskiNorm.L1,
        primal_distance=1.0,
        optimal_alpha=np.array([0.0]),
        residual=np.array([1.0]),
        dual_witness=np.array([1.0]),
        dual_objective=1.0,
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(np.array([1.0]), np.array([[1e-15]]), fake) is False
    assert QuotientDistanceSolver.verify_certificate(np.array([1.0]), np.array([[1e-14]]), fake) is False

    # Also test fake certificate on nearly dependent D with W = [0, 1] to exercise subspace defect
    D = np.array([[1.0, 1.0], [0.0, 1e-13]])
    fake2 = QuotientResult(
        norm=MinkowskiNorm.L1,
        primal_distance=1.0,
        optimal_alpha=np.array([0.0, 0.0]),
        residual=np.array([0.0, 1.0]),
        dual_witness=np.array([0.0, 1.0]),
        dual_objective=1.0,
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(np.array([0.0, 1.0]), D, fake2) is False


def test_small_nonzero_residuals_preserved_and_reported():
    """R2 Regression: With D = [0], omega = [5e-8], computed nonzero residual must be preserved
    and reported with is_approximate_zero=True, without zeroing out primal_distance or residual.
    """
    D = np.array([[0.0]])
    omega = np.array([5e-8])
    for norm in MinkowskiNorm:
        r = QuotientDistanceSolver.solve(omega, D, norm=norm)
        assert r.primal_distance == pytest.approx(5e-8, rel=1e-5)
        assert np.allclose(r.residual, [5e-8], atol=1e-12)
        assert np.allclose(omega - D @ r.optimal_alpha, r.residual, atol=1e-12)
        assert r.is_approximate_zero is True
        assert r.is_numerically_certified is True
        assert QuotientDistanceSolver.verify_certificate(omega, D, r) is True


def test_solver_tolerance_validation():
    """R2: Solver tolerance must be validated as a finite positive float < 1.0."""
    omega = np.array([1.0])
    D = np.array([[1.0]])
    with pytest.raises(ValueError, match="Solver tolerance must be a finite positive float < 1.0"):
        QuotientDistanceSolver.solve(omega, D, tol=-1.0)
    with pytest.raises(ValueError, match="Solver tolerance must be a finite positive float < 1.0"):
        QuotientDistanceSolver.solve(omega, D, tol=2.0)
    with pytest.raises(ValueError, match="Solver tolerance must be a finite positive float < 1.0"):
        QuotientDistanceSolver.solve(omega, D, tol=float("nan"))


def test_project_dual_witness_tolerance_firewall():
    """Directly test _project_dual_witness orthogonality check branches."""
    D = np.array([[1.0], [2.0]])
    w = np.array([1.0, -0.5])  # orthogonal to D
    # Normal tolerance passes
    _, is_ortho = QuotientDistanceSolver._project_dual_witness(D, w, MinkowskiNorm.L2, tol=1e-5)
    assert is_ortho is True
    # Impossibly small tolerance triggers defect firewall
    _, is_ortho_fail = QuotientDistanceSolver._project_dual_witness(D, w, MinkowskiNorm.L2, tol=1e-25)
    assert is_ortho_fail is False


def test_scaled_nearly_dependent_requested_tolerance_unresolved():
    """Finding 2 Regression: D = [[1, 1], [0, 1e-13]], omega = [0, 1e-6], tol = 1e-12.

    When numerical LP solver returns gap 1e-6 exceeding requested tolerance 1e-12,
    it must NOT report certified, and independent verifier must reject it at requested tolerance.
    """
    D = np.array([[1.0, 1.0], [0.0, 1e-13]])
    omega = np.array([0.0, 1e-6])
    tol = 1e-12
    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L_INF]:
        r = QuotientDistanceSolver.solve(omega, D, norm=norm, tol=tol)
        assert r.is_numerically_certified is False
        assert r.duality_gap > tol
        assert QuotientDistanceSolver.verify_certificate(omega, D, r, tol=tol) is False
        assert QuotientDistanceSolver.verify_certificate(omega, D, r) is False


def test_redundant_columns_svd_certification_parity():
    """Finding 4 Regression: Adding redundant columns D2 = [[1, 1], [1, 1]] vs D1 = [[1], [1]]
    must preserve certified quotient distance across all Minkowski norms without rank misclassification.
    """
    omega = np.array([1.0, -1.0])
    D1 = np.array([[1.0], [1.0]])
    D2 = np.array([[1.0, 1.0], [1.0, 1.0]])

    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF]:
        r1 = QuotientDistanceSolver.solve(omega, D1, norm=norm)
        r2 = QuotientDistanceSolver.solve(omega, D2, norm=norm)

        assert r2.is_numerically_certified is True
        assert r1.is_numerically_certified is True
        assert r2.primal_distance == pytest.approx(r1.primal_distance, rel=1e-5)
        assert r2.duality_gap < 1e-7
        assert QuotientDistanceSolver.verify_certificate(omega, D2, r2) is True


def test_discarded_singular_direction_zero_distance_remediation():
    """Item 1 Regression: D = [[1, 1], [0, 1e-16]], omega = [0, 1].

    The true quotient distance is zero via exact repair (-10^16, 10^16).
    The solver must return a validated zero-distance repair or an explicit uncertified result.
    It must NEVER certify distance 1.0.
    """
    D = np.array([[1.0, 1.0], [0.0, 1e-16]])
    omega = np.array([0.0, 1.0])

    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF]:
        res = QuotientDistanceSolver.solve(omega, D, norm=norm)
        # Must never certify distance 1.0
        if res.is_numerically_certified:
            assert res.primal_distance == pytest.approx(0.0, abs=1e-5)
            assert QuotientDistanceSolver.verify_certificate(omega, D, res) is True
        else:
            # If uncertified, that is also valid (explicitly uncertified)
            assert res.is_numerically_certified is False

        # Independent verifier must strictly reject a truncated certificate claiming distance 1.0
        bad_result = QuotientResult(
            norm=norm,
            primal_distance=1.0,
            optimal_alpha=np.zeros(2),
            residual=np.array([0.0, 1.0]),
            dual_witness=np.array([0.0, 1.0]),
            dual_objective=1.0,
            duality_gap=0.0,
            is_numerically_certified=True,
        )
        assert QuotientDistanceSolver.verify_certificate(omega, D, bad_result) is False

    # Test equivalent nonzero source-column rescalings
    D_scaled_col = np.array([[1.0, 1e5], [0.0, 1e-11]])
    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF]:
        res_scaled = QuotientDistanceSolver.solve(omega, D_scaled_col, norm=norm)
        if res_scaled.is_numerically_certified:
            assert res_scaled.primal_distance == pytest.approx(0.0, abs=1e-5)
            assert QuotientDistanceSolver.verify_certificate(omega, D_scaled_col, res_scaled) is True


def test_verification_intermediate_overflow_rejected():
    """Item 2 Regression: Finite candidate inputs whose intermediate product overflows.

    D = full((2, 4), 1e200), alpha = [1e200, -1e200, 1e200, -1e200].
    D @ alpha produces [nan, nan]. Must be rejected by verify_certificate, never pass.
    """
    D = np.full((2, 4), 1e200)
    omega = np.array([1.0, -1.0])
    fake = QuotientResult(
        norm=MinkowskiNorm.L1,
        primal_distance=0.0,
        optimal_alpha=np.array([1e200, -1e200, 1e200, -1e200]),
        residual=np.zeros(2),
        dual_witness=np.zeros(2),
        dual_objective=0.0,
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        assert QuotientDistanceSolver.verify_certificate(omega, D, fake) is False


    # Consistent primal data for L2 norm evaluation:
    # omega = [1e200, 1e200], D = zeros((2, 4)), alpha = zeros(4), so omega - D @ alpha = [1e200, 1e200]
    # Primal distance is representable (~1.414e200), so a fake claiming primal_distance = 1e200
    # must be rejected because primal_distance != ||residual||_2.
    omega_l2 = np.full(2, 1e200)
    D_l2 = np.zeros((2, 4))
    fake_l2 = QuotientResult(
        norm=MinkowskiNorm.L2,
        primal_distance=1e200,
        optimal_alpha=np.zeros(4),
        residual=np.full(2, 1e200),
        dual_witness=np.zeros(2),
        dual_objective=0.0,
        duality_gap=1e200,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega_l2, D_l2, fake_l2) is False

    # Truly unrepresentable L2 residual overflowing float range (> 1.79e308)
    omega_unrep = np.full(2, 1.5e308)
    D_unrep = np.zeros((2, 4))
    fake_unrep = QuotientResult(
        norm=MinkowskiNorm.L2,
        primal_distance=1.5e308,
        optimal_alpha=np.zeros(4),
        residual=np.full(2, 1.5e308),
        dual_witness=np.zeros(2),
        dual_objective=0.0,
        duality_gap=1.5e308,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega_unrep, D_unrep, fake_unrep) is False

    # Truly unrepresentable L1 residual overflowing float range (> 1.79e308)
    omega_l1_unrep = np.full(2, 1e308)
    fake_l1_unrep = QuotientResult(
        norm=MinkowskiNorm.L1,
        primal_distance=1e308,
        optimal_alpha=np.zeros(4),
        residual=np.full(2, 1e308),
        dual_witness=np.zeros(2),
        dual_objective=0.0,
        duality_gap=1e308,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega_l1_unrep, D_unrep, fake_l1_unrep) is False


def test_l2_solver_verifier_tolerance_agreement():
    """Item 5 Regression (Case A): omega = [5e-16], D = [[0]], tol = 1e-20.

    Solver and verifier must agree across strict tolerances without dist < 1e-15 bypassing.
    """
    omega = np.array([5e-16])
    D = np.zeros((1, 1))

    for tol in [1e-20, 1e-15, 1e-10]:
        res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2, tol=tol)
        v_passed = QuotientDistanceSolver.verify_certificate(omega, D, res, tol=tol)
        assert res.is_numerically_certified == v_passed
        assert res.duality_gap <= tol or not res.is_numerically_certified


def test_discarded_singular_direction_positive_distance_uncertified():
    # D has a discarded singular direction (0 < S2 <= cutoff), but omega is NOT in the image.
    # The solver cannot certify a positive distance and must set is_numerically_certified = False.
    D = np.array([[1.0, 1.0], [0.0, 1e-16], [0.0, 0.0]])
    omega = np.array([0.0, 0.0, 1.0])
    res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L1)
    assert res.is_numerically_certified is False


def test_l2_norm_underflow_residual_preservation_and_oracle():
    """Item 1 Regression: omega = [5e-200], D = [[0]], tol = 1e-220.

    True distance is abs(omega[0]) = 5e-200.
    The solver must compute primal_distance = 5e-200 (not 0.0), certifying against
    the independent 1D oracle abs(omega[0]).
    The verifier must reject any false zero-distance certificate.
    """
    omega = np.array([5e-200])
    D = np.zeros((1, 1))
    tol = 1e-220

    res = QuotientDistanceSolver.solve(omega, D, norm=MinkowskiNorm.L2, tol=tol)
    assert res.is_numerically_certified is True
    # Independent 1D oracle comparison
    assert res.primal_distance == pytest.approx(abs(omega[0]), rel=1e-12)
    assert res.primal_distance > tol
    assert QuotientDistanceSolver.verify_certificate(omega, D, res, tol=tol) is True

    # Verifier must reject fake certificate claiming distance 0.0 on nonzero residual [5e-200]
    fake_zero = QuotientResult(
        norm=MinkowskiNorm.L2,
        primal_distance=0.0,
        optimal_alpha=np.zeros(1),
        residual=np.array([5e-200]),
        dual_witness=np.zeros(1),
        dual_objective=0.0,
        duality_gap=0.0,
        is_numerically_certified=True,
    )
    assert QuotientDistanceSolver.verify_certificate(omega, D, fake_zero, tol=tol) is False


def test_exact_repair_fallback_float_overflow_uncertified():
    """Range-handling follow-up: D = [[1, 1], [0, 1e-310]], omega = [0, 1].

    Exact rational repair yields alpha = (-10^310, 10^310), which overflows float64.
    The solver must catch OverflowError, report uncertified result without crashing,
    and never claim false zero distance.
    """
    D = np.array([[1.0, 1.0], [0.0, 1e-310]])
    omega = np.array([0.0, 1.0])

    for norm in [MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF]:
        res = QuotientDistanceSolver.solve(omega, D, norm=norm)
        assert res.is_numerically_certified is False
        assert res.primal_distance == pytest.approx(1.0, abs=1e-5)


def test_exact_pivot_columns_edge_cases():
    assert QuotientDistanceSolver._exact_pivot_columns(np.zeros((0, 0))) == []
    assert QuotientDistanceSolver._exact_pivot_columns(np.zeros((3, 0))) == []
    assert QuotientDistanceSolver._exact_pivot_columns(np.zeros((0, 3))) == []
    assert QuotientDistanceSolver._exact_pivot_columns(np.zeros((3, 3))) == []

    # svd_rank_cutoff edge cases
    assert QuotientDistanceSolver._svd_rank_cutoff(np.array([]), 0, 0) == 0.0
    assert QuotientDistanceSolver._svd_rank_cutoff(np.array([0.0]), 1, 1) == 0.0

    # scaled_euclidean_norm empty and non-finite input
    from code_quotient_solver import scaled_euclidean_norm
    assert scaled_euclidean_norm(np.array([])) == 0.0
    with pytest.raises(ValueError, match="Computed Euclidean norm is non-finite"):
        scaled_euclidean_norm(np.array([1.5e308, 1.5e308]))

    # 0 columns witness projection
    w, is_ortho = QuotientDistanceSolver._project_dual_witness(
        np.zeros((2, 0)), np.array([3.0, 4.0]), MinkowskiNorm.L2, tol=1e-7
    )
    assert is_ortho is True
    assert np.linalg.norm(w) <= 1.0 + 1e-7

    # Non-empty matrix with 0 pivot columns (all zero columns)
    w0, is_ortho0 = QuotientDistanceSolver._project_dual_witness(
        np.zeros((3, 2)), np.array([1.0, 2.0, 3.0]), MinkowskiNorm.L2, tol=1e-7
    )
    assert is_ortho0 is True
    assert np.linalg.norm(w0) <= 1.0 + 1e-7





