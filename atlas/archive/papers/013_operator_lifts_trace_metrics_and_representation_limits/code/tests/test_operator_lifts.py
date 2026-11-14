"""Unit tests for Operator Lifts, Trace Metrics, and Representation Limits."""

import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_operator_lifts_core import DensityOperator, GuardedDescentEvaluator, OperatorLifts


def test_linear_trace_embedding_isometry():
    """Verify that ||F_lin(v)||_tr == ||v||_1."""
    v = [3.0, -4.0, 12.0, 0.0]
    l1_norm = sum(abs(x) for x in v)
    t_op = OperatorLifts.linear_embedding(v)
    assert math.isclose(t_op.trace_norm, l1_norm, rel_tol=1e-9)
    assert math.isclose(t_op.trace_norm, 19.0, rel_tol=1e-9)


def test_lossy_collision_principle_positive_and_negative():
    """Verify that F_den(c * v) == F_den(v) for all nonzero scalars c (both c > 0 and c < 0)."""
    v = [2.0, -1.0, 5.0]
    rho_1 = OperatorLifts.density_lift(v)
    rho_2 = OperatorLifts.density_lift([x * 42.0 for x in v])
    rho_3 = OperatorLifts.density_lift([x * -1.0 for x in v])
    rho_4 = OperatorLifts.density_lift([x * -0.001 for x in v])

    # State vectors match under canonical gauge
    assert np.allclose(rho_1.state_vector, rho_2.state_vector, atol=1e-9)
    assert np.allclose(rho_1.state_vector, rho_3.state_vector, atol=1e-9)
    assert np.allclose(rho_1.state_vector, rho_4.state_vector, atol=1e-9)

    # Density matrices are identically equal
    assert np.allclose(rho_1.density_matrix, rho_2.density_matrix, atol=1e-9)
    assert np.allclose(rho_1.density_matrix, rho_3.density_matrix, atol=1e-9)
    assert np.allclose(rho_1.density_matrix, rho_4.density_matrix, atol=1e-9)

    # Direct operator equality
    assert rho_1 == rho_2 == rho_3 == rho_4


def test_reconstruction_obstruction_and_fiber():
    """Verify fiber structure and reconstruction requirements with mass and orientation anchor."""
    v = [1.0, -2.0, 3.0]
    v_arr = np.array(v, dtype=float)
    v_neg_arr = -v_arr
    mass_true = float(sum(abs(x) for x in v))
    rho_pos = OperatorLifts.density_lift(v)
    rho_neg = OperatorLifts.density_lift([-x for x in v])

    # 1. Attempt reconstruction without mass -> MUST FAIL
    success, recon, msg = OperatorLifts.attempt_reconstruction(rho_pos, admitted_mass=None)
    assert not success
    assert recon is None
    assert "Lossy Collision Principle" in msg

    # 2. Attempt reconstruction with true mass -> Returns candidate pair {v, -v}
    success_with_mass, pair, _ = OperatorLifts.attempt_reconstruction(rho_pos, admitted_mass=mass_true)
    assert success_with_mass
    assert isinstance(pair, tuple) and len(pair) == 2
    cand1, cand2 = pair
    assert (np.allclose(cand1, v_arr, atol=1e-9) and np.allclose(cand2, v_neg_arr, atol=1e-9)) or (
        np.allclose(cand1, v_neg_arr, atol=1e-9) and np.allclose(cand2, v_arr, atol=1e-9)
    )

    # 3. Compare reconstruction for v and -v: both yield identical candidate pair
    success_neg, pair_neg, _ = OperatorLifts.attempt_reconstruction(rho_neg, admitted_mass=mass_true)
    assert success_neg
    cand_neg1, cand_neg2 = pair_neg
    assert (np.allclose(cand_neg1, v_arr, atol=1e-9) and np.allclose(cand_neg2, v_neg_arr, atol=1e-9)) or (
        np.allclose(cand_neg1, v_neg_arr, atol=1e-9) and np.allclose(cand_neg2, v_arr, atol=1e-9)
    )

    # 4. Reconstruction with orientation anchor (+1 or -1) resolves to a single vector
    succ_pos, single_pos, _ = OperatorLifts.attempt_reconstruction(
        rho_pos, admitted_mass=mass_true, orientation_anchor=+1
    )
    assert succ_pos
    assert np.allclose(single_pos, v_arr, atol=1e-9)

    succ_neg, single_neg, _ = OperatorLifts.attempt_reconstruction(
        rho_pos, admitted_mass=mass_true, orientation_anchor=-1
    )
    assert succ_neg
    assert np.allclose(single_neg, v_neg_arr, atol=1e-9)

    # 5. Reconstruction with reference vector anchor
    succ_ref, single_ref, _ = OperatorLifts.attempt_reconstruction(
        rho_pos, admitted_mass=mass_true, orientation_anchor=v_arr
    )
    assert succ_ref
    assert np.allclose(single_ref, v_arr, atol=1e-9)


def test_density_operator_rejects_unnormalized():
    """Verify that direct construction of DensityOperator strictly rejects non-unit trace vectors."""
    # Trace of |psi><psi| where psi = [2.0, 0.0] is 4.0 != 1.0
    with pytest.raises(ValueError, match="unit L2 norm"):
        DensityOperator([2.0, 0.0])

    # Trace of [0.5, 0.5] is 0.5 != 1.0
    with pytest.raises(ValueError, match="unit L2 norm"):
        DensityOperator([0.5, 0.5])

    # Trace of [0.0, 0.0] is 0.0 != 1.0
    with pytest.raises(ValueError, match="unit L2 norm"):
        DensityOperator([0.0, 0.0])

    # Valid unit state vector succeeds
    valid_psi = [1.0 / math.sqrt(2), -1.0 / math.sqrt(2)]
    d = DensityOperator(valid_psi)
    assert math.isclose(d.trace, 1.0, abs_tol=1e-9)


def test_density_lift_small_mass_domain():
    """Verify that density_lift accepts nonzero vectors with small mass (e.g. 1e-13), matching Definition 4.1."""
    small_v = [1e-13, 0.0, -1e-13]
    rho = OperatorLifts.density_lift(small_v)
    assert math.isclose(rho.trace, 1.0, abs_tol=1e-9)
    assert rho.state_vector.shape == (3,)


def test_array_objects_defend_against_post_construction_mutation():
    """Verify that array-backed operators protect internal state and set hashing against mutation."""
    # 1. LinearTraceOperator
    t = OperatorLifts.linear_embedding([1.0, -2.0])
    s_t = {t}
    diag = t.diagonal
    with pytest.raises(ValueError):
        diag[0] = 999.0
    # Even if caller forces writeable flag on the returned copy:
    diag.flags.writeable = True
    diag[0] = 999.0
    # Original operator remains intact and hash in set is preserved
    assert t.diagonal[0] == 1.0
    assert t in s_t

    # 2. DensityOperator
    rho = OperatorLifts.density_lift([3.0, -4.0])
    s_rho = {rho}
    sv = rho.state_vector
    with pytest.raises(ValueError):
        sv[0] = 999.0
    sv.flags.writeable = True
    sv[0] = 999.0
    assert rho.state_vector[0] != 999.0
    assert rho in s_rho

    mat = rho.density_matrix
    with pytest.raises(ValueError):
        mat[0, 0] = 999.0
    mat.flags.writeable = True
    mat[0, 0] = 999.0
    assert rho.density_matrix[0, 0] != 999.0
    assert rho in s_rho


def test_pseudometric_on_unoriented_lines():
    """Verify trace distance Xi: zero on unoriented lines (u = c*v for c != 0), positive otherwise."""
    v = [1.0, 2.0, -3.0]
    rho_v = OperatorLifts.density_lift(v)
    rho_neg_v = OperatorLifts.density_lift([-x for x in v])
    rho_scaled_v = OperatorLifts.density_lift([x * -4.5 for x in v])

    # Distance between v and -v is exactly 0.0
    dist_antipodal = OperatorLifts.trace_distance(rho_v, rho_neg_v)
    assert math.isclose(dist_antipodal, 0.0, abs_tol=1e-9)

    # Distance between v and c*v (c < 0) is 0.0
    dist_scaled = OperatorLifts.trace_distance(rho_v, rho_scaled_v)
    assert math.isclose(dist_scaled, 0.0, abs_tol=1e-9)

    # Non-collinear cochains have strictly positive distance
    w = [0.0, 1.0, 1.0]
    rho_w = OperatorLifts.density_lift(w)
    dist_diff = OperatorLifts.trace_distance(rho_v, rho_w)
    assert dist_diff > 0.0

    # Orthogonal vectors have distance 1.0
    e1 = OperatorLifts.density_lift([1.0, 0.0])
    e2 = OperatorLifts.density_lift([0.0, 1.0])
    assert math.isclose(OperatorLifts.trace_distance(e1, e2), 1.0, abs_tol=1e-9)


def test_large_finite_inputs_overflow_prevention():
    """Verify that density_lift handles large finite inputs near float64 limits without overflow."""
    v_large = [1e308, 1e308]
    rho = OperatorLifts.density_lift(v_large)
    assert math.isclose(rho.trace, 1.0, abs_tol=1e-9)
    assert np.all(np.isfinite(rho.state_vector))
    assert np.all(np.isfinite(rho.density_matrix))
    expected_entry = 1.0 / math.sqrt(2.0)
    assert np.allclose(rho.state_vector, [expected_entry, expected_entry], atol=1e-9)


def test_reconstruction_invalid_and_nonfinite_mass():
    """Verify that attempt_reconstruction strictly rejects nonfinite or nonpositive admitted mass."""
    rho = OperatorLifts.density_lift([1.0, 2.0, 3.0])
    for invalid_mass in (float("nan"), float("inf"), float("-inf"), -1.0, 0.0, -1e-15):
        with pytest.raises(ValueError, match="Invalid admitted_mass"):
            OperatorLifts.attempt_reconstruction(rho, admitted_mass=invalid_mass)


def test_trace_distance_identical_projectors_stability():
    """Verify that trace_distance of identical or sign-flipped lifts returns exactly 0.0 without roundoff."""
    v = [1.0, 1.0, 1.0]
    rho = OperatorLifts.density_lift(v)
    rho_neg = OperatorLifts.density_lift([-1.0, -1.0, -1.0])

    # Direct self-distance
    d_self = OperatorLifts.trace_distance(rho, rho)
    assert d_self == 0.0

    # Antipodal distance
    d_neg = OperatorLifts.trace_distance(rho, rho_neg)
    assert d_neg == 0.0


def test_reconstruction_directly_from_raw_matrix():
    """Verify that attempt_reconstruction operates directly on a 2D density matrix without wrapper."""
    v = [3.0, -4.0]
    rho = OperatorLifts.density_lift(v)
    mat = rho.density_matrix  # raw 2D numpy array

    mass = float(sum(abs(x) for x in v))  # 7.0
    succ, pair, _ = OperatorLifts.attempt_reconstruction(mat, admitted_mass=mass)
    assert succ
    assert isinstance(pair, tuple) and len(pair) == 2
    cand1, cand2 = pair
    v_arr = np.array(v, dtype=float)
    assert (np.allclose(cand1, v_arr, atol=1e-9) and np.allclose(cand2, -v_arr, atol=1e-9)) or (
        np.allclose(cand1, -v_arr, atol=1e-9) and np.allclose(cand2, v_arr, atol=1e-9)
    )


def test_quotient_equality_and_hash_consistency_with_zero_coordinates():
    """Verify that antipodal inputs with zero coordinates compare equal, hash identically, and deduplicate in sets."""
    # Review reproduction: lifts of (0, -1) and (0, 1)
    rho_pos = OperatorLifts.density_lift([0.0, 1.0])
    rho_neg = OperatorLifts.density_lift([0.0, -1.0])

    assert rho_pos == rho_neg
    assert hash(rho_pos) == hash(rho_neg)
    quotient_set = {rho_pos, rho_neg}
    assert len(quotient_set) == 1, f"Expected set cardinality 1 for equal quotient objects, got {len(quotient_set)}"

    # Multiple zero coordinates
    v1 = [1.0, 0.0, -2.0, 0.0]
    v2 = [-1.0, 0.0, 2.0, 0.0]
    r1 = OperatorLifts.density_lift(v1)
    r2 = OperatorLifts.density_lift(v2)
    assert r1 == r2
    assert hash(r1) == hash(r2)
    assert len({r1, r2}) == 1


def test_trace_distance_preserves_triangle_inequality_without_near_identity_clipping():
    r"""Verify that trace distance preserves the metric triangle inequality without artificial near-identity cutoff.

    Review reproduction:
    v(t) = (cos^2 t, sin^2 t), t in {0, theta, 2*theta}, theta = 1e-7.
    Exact distances: sin(theta), sin(theta), sin(2*theta).
    The stable formulation Xi(a, b) = 1/2 ||a - b||_2 ||a + b||_2 must yield non-zero distances
    and satisfy Xi(A, C) <= Xi(A, B) + Xi(B, C).
    """
    theta = 1e-7
    t_vals = [0.0, theta, 2.0 * theta]
    rhos = []
    for t in t_vals:
        v = [math.cos(t) ** 2, math.sin(t) ** 2]
        rhos.append(OperatorLifts.density_lift(v))

    xi_ab = OperatorLifts.trace_distance(rhos[0], rhos[1])
    xi_bc = OperatorLifts.trace_distance(rhos[1], rhos[2])
    xi_ac = OperatorLifts.trace_distance(rhos[0], rhos[2])

    # All distances must be strictly positive (no spurious zero cutoff)
    assert xi_ab > 0.0
    assert xi_bc > 0.0
    assert xi_ac > 0.0

    # Distances match exact analytical values to high floating-point precision
    assert math.isclose(xi_ab, math.sin(theta), rel_tol=1e-6)
    assert math.isclose(xi_bc, math.sin(theta), rel_tol=1e-6)
    assert math.isclose(xi_ac, math.sin(2.0 * theta), rel_tol=1e-6)

    # Triangle inequality Xi(A, C) <= Xi(A, B) + Xi(B, C)
    assert xi_ac <= xi_ab + xi_bc + 1e-15


def test_reconstruction_rejects_mixed_states_outside_rank1_image():
    """Verify that attempt_reconstruction strictly rejects mixed states (e.g. 0.5 * I_2) outside rank-1 image."""
    # Mixed density matrix 0.5 * I_2
    rho_mixed = 0.5 * np.eye(2)
    succ, cand, msg = OperatorLifts.attempt_reconstruction(rho_mixed, admitted_mass=2.0)
    assert succ is False
    assert cand is None
    assert "idempotent" in msg or "Mixed states" in msg

    # Asymmetric matrix
    mat_asym = np.array([[0.8, 0.1], [0.3, 0.2]])
    succ_asym, _, msg_asym = OperatorLifts.attempt_reconstruction(mat_asym, admitted_mass=2.0)
    assert succ_asym is False
    assert "symmetric" in msg_asym

    # Non-unit trace matrix
    mat_trace = np.array([[2.0, 0.0], [0.0, 0.0]])
    succ_trace, _, msg_trace = OperatorLifts.attempt_reconstruction(mat_trace, admitted_mass=2.0)
    assert succ_trace is False
    assert "unit trace" in msg_trace


def test_reconstruction_rejects_orthogonal_and_nonfinite_anchors():
    r"""Verify that attempt_reconstruction requires ell(v) != 0 and rejects nonfinite or orthogonal anchors.

    Review reproduction:
    v = (1, 1), a = (1, -1) has <a, v> = <a, -v> = 0.
    The anchor provides no orientation information and must be rejected as unresolved.
    """
    v = [1.0, 1.0]
    rho = OperatorLifts.density_lift(v)
    mass = 2.0

    # Orthogonal anchor <a, v> == 0
    anchor_ortho = [1.0, -1.0]
    succ_ortho, cand_ortho, msg_ortho = OperatorLifts.attempt_reconstruction(
        rho, admitted_mass=mass, orientation_anchor=anchor_ortho
    )
    assert succ_ortho is False
    assert cand_ortho is None
    assert "vanishes" in msg_ortho or "Unresolved anchor" in msg_ortho

    # Anchor containing NaN
    anchor_nan = [float("nan"), 1.0]
    succ_nan, _, msg_nan = OperatorLifts.attempt_reconstruction(
        rho, admitted_mass=mass, orientation_anchor=anchor_nan
    )
    assert succ_nan is False
    assert "finite" in msg_nan

    # Zero scalar anchor
    succ_zero_s, _, msg_zero_s = OperatorLifts.attempt_reconstruction(
        rho, admitted_mass=mass, orientation_anchor=0
    )
    assert succ_zero_s is False
    assert "non-zero" in msg_zero_s

    # Non-orthogonal reference anchor succeeds
    anchor_valid = [2.0, 1.0]
    succ_v, single_v, _ = OperatorLifts.attempt_reconstruction(
        rho, admitted_mass=mass, orientation_anchor=anchor_valid
    )
    assert succ_v is True
    assert np.allclose(single_v, [1.0, 1.0], atol=1e-9)


def test_proved_finite_integer_and_rational_claims():
    """Drive the shipped exact checkers for the mechanized finite claims."""
    embedded = OperatorLifts.linear_embedding([2, -3, 5, 0])
    assert embedded.trace_norm == 10.0
    assert OperatorLifts.integer_trace_norm([2, -3, 5, 0]) == 10
    assert OperatorLifts.integer_trace_norm([6, -9, 15, 0]) == 30

    weights = OperatorLifts.normalized_abs_weights([2, -3, 5, 0])
    assert weights == (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2), Fraction(0, 1))
    assert sum(weights) == 1
    assert OperatorLifts.normalized_abs_weights([6, -9, 15, 0]) == weights
    assert OperatorLifts.normalized_abs_weights([-2, 3, -5, 0]) == weights
    assert OperatorLifts.integer_trace_norm([-2, 3, -5, 0]) == 10

    blocked, missing, _message = OperatorLifts.attempt_reconstruction(
        OperatorLifts.density_lift([2, -3, 5]),
        admitted_mass=None,
    )
    assert blocked is False
    assert missing is None

    cleared = OperatorLifts.cleared_homogeneous_pair(-3, 2, 4)
    assert cleared == (6, 12)
    assert Fraction(*cleared) == Fraction(2, 4)
    assert OperatorLifts.cleared_homogeneous_pair(5, 2, 4) == (10, 20)

    assert OperatorLifts.squared_trace_gap([1, 0], [0, 1]) == (4, 4)
    assert OperatorLifts.squared_trace_gap([3, 4], [4, -3]) == (2500, 2500)

    eps = Fraction(1, 10**9)
    ceiling = Fraction(1)
    current = (Fraction(1), Fraction(1), Fraction(1))
    decreased = (Fraction(1) - 2 * eps, Fraction(1), Fraction(1), Fraction(1))
    increased = (Fraction(1) + Fraction(1, 10**10), Fraction(0), Fraction(0), Fraction(0))
    gamma_up = (Fraction(1), Fraction(1) + Fraction(1, 10**10), Fraction(0), Fraction(0))
    gated = (Fraction(1) - 2 * eps, Fraction(0), Fraction(0), Fraction(2))
    infinite = (Fraction(1) - 2 * eps, Fraction(0), Fraction(0), None)
    assert GuardedDescentEvaluator.exact_admits(current, decreased, ceiling, eps) is True
    assert GuardedDescentEvaluator.exact_admits(current, increased, ceiling, eps) is False
    assert GuardedDescentEvaluator.exact_admits(current, gamma_up, ceiling, eps) is False
    assert GuardedDescentEvaluator.exact_admits(current, gated, ceiling, eps) is False
    assert GuardedDescentEvaluator.exact_admits(current, infinite, ceiling, eps) is False

    feasible = (Fraction(1, 2), Fraction(9), Fraction(9), Fraction(1))
    infeasible = (Fraction(0), Fraction(0), Fraction(0), Fraction(5))
    lower = (Fraction(1, 10), Fraction(9), Fraction(9), Fraction(1))
    higher = (Fraction(1, 2), Fraction(0), Fraction(0), Fraction(1))
    assert GuardedDescentEvaluator.exact_compare(feasible, infeasible, ceiling) == -1
    assert GuardedDescentEvaluator.exact_compare(lower, higher, ceiling) == -1
    assert GuardedDescentEvaluator.exact_compare(higher, lower, ceiling) == 1


