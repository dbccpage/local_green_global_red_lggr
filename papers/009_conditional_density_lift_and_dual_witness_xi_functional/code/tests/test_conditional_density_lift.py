"""Unit tests for the Conditional Density Lift and Xi Functional."""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_conditional_density_lift_core import (
    ConditionalDensityLift,
    DensityLift,
    GuardedEvaluator,
    ZeroObstructionCertificate,
)


def test_density_lift_properties():
    """Verify trace preservation, purity, and unit norm."""
    v = [2.0, -3.0, 5.0, 0.0]
    lift = ConditionalDensityLift.lift(v)
    assert math.isclose(lift.total_mass, 10.0, rel_tol=1e-9)
    # Unit 2-norm of state vector
    norm_sq = float(np.sum(lift.state_vector ** 2))
    assert math.isclose(norm_sq, 1.0, rel_tol=1e-9)
    # Density matrix trace == 1
    rho = lift.density_matrix
    assert math.isclose(float(np.trace(rho)), 1.0, rel_tol=1e-9)
    # Purity: rho^2 == rho
    rho_sq = np.dot(rho, rho)
    assert np.allclose(rho, rho_sq, atol=1e-9)


def test_finite_input_normalization_safe_large_coordinates():
    """Normalize large coordinates whose total mass remains representable."""
    v = [1e307, 1e307]
    lift = ConditionalDensityLift.lift(v)

    # Unit 2-norm of state vector: [1/sqrt(2), 1/sqrt(2)]
    norm = float(np.linalg.norm(lift.state_vector))
    assert math.isclose(norm, 1.0, rel_tol=1e-9)
    expected_comp = 1.0 / math.sqrt(2.0)
    assert math.isclose(lift.state_vector[0], expected_comp, rel_tol=1e-9)
    assert math.isclose(lift.state_vector[1], expected_comp, rel_tol=1e-9)

    # Density matrix has unit trace and rank 1
    rho = lift.density_matrix
    assert math.isclose(float(np.trace(rho)), 1.0, rel_tol=1e-9)
    assert np.allclose(rho @ rho, rho, atol=1e-9)

    # Total mass is positive and finite
    assert math.isfinite(lift.total_mass)
    assert lift.total_mass > 0.0

    # Trace distance between identical large-coordinate lifts is zero
    assert ConditionalDensityLift.trace_distance(lift, lift) == 0.0


def test_density_lift_validation_in_post_init():
    """Verify that DensityLift enforces unit norm and positive finite mass."""
    # Valid construction
    valid = DensityLift(state_vector=np.array([1.0, 0.0]), total_mass=5.0)
    assert valid.total_mass == 5.0

    # Non-unit norm raises ValueError
    with pytest.raises(ValueError, match="unit 2-norm"):
        DensityLift(state_vector=np.array([0.5, 0.5]), total_mass=1.0)

    # Zero vector raises ValueError
    with pytest.raises(ValueError, match="unit 2-norm"):
        DensityLift(state_vector=np.array([0.0, 0.0]), total_mass=1.0)

    # Non-finite state vector raises ValueError
    with pytest.raises(ValueError, match="finite"):
        DensityLift(state_vector=np.array([np.nan, 1.0]), total_mass=1.0)

    # Zero mass raises ValueError
    with pytest.raises(ValueError, match="positive and finite"):
        DensityLift(state_vector=np.array([1.0, 0.0]), total_mass=0.0)

    # Negative mass raises ValueError
    with pytest.raises(ValueError, match="positive and finite"):
        DensityLift(state_vector=np.array([1.0, 0.0]), total_mass=-2.0)

    # Infinite mass raises ValueError
    with pytest.raises(ValueError, match="positive and finite"):
        DensityLift(state_vector=np.array([1.0, 0.0]), total_mass=float("inf"))

    # NaN mass raises ValueError
    with pytest.raises(ValueError, match="positive and finite"):
        DensityLift(state_vector=np.array([1.0, 0.0]), total_mass=float("nan"))


def test_lift_rejects_nonfinite_and_empty_inputs():
    """Verify that ConditionalDensityLift.lift rejects NaN, Inf, and empty sequences."""
    with pytest.raises(ValueError, match="non-finite values"):
        ConditionalDensityLift.lift([np.nan, 1.0])

    with pytest.raises(ValueError, match="non-finite values"):
        ConditionalDensityLift.lift([np.inf, 1.0])

    with pytest.raises(ValueError, match="non-empty"):
        ConditionalDensityLift.lift([])

    with pytest.raises(ValueError, match="zero-mass"):
        ConditionalDensityLift.lift([0.0, 0.0, 0.0])


def test_density_lift_scale_invariance():
    """Verify scale invariance: rho(c * v) == rho(v) for all c > 0."""
    v = [1.5, -2.5, 4.0]
    lift_1 = ConditionalDensityLift.lift(v)
    lift_2 = ConditionalDensityLift.lift([x * 7.5 for x in v])
    assert np.allclose(lift_1.state_vector, lift_2.state_vector, atol=1e-9)
    assert np.allclose(lift_1.density_matrix, lift_2.density_matrix, atol=1e-9)


def test_trace_distance_formula():
    """Verify pure state trace distance formula D = sqrt(1 - overlap^2) on generic vectors."""
    # Orthogonal states: overlap = 0 => D = 1
    v_a = [1.0, 0.0]
    v_b = [0.0, 1.0]
    lift_a = ConditionalDensityLift.lift(v_a)
    lift_b = ConditionalDensityLift.lift(v_b)
    d_ortho = ConditionalDensityLift.trace_distance(lift_a, lift_b)
    assert math.isclose(d_ortho, 1.0, rel_tol=1e-9)

    # Identical states: overlap = 1 => D = 0
    d_ident = ConditionalDensityLift.trace_distance(lift_a, lift_a)
    assert math.isclose(d_ident, 0.0, abs_tol=1e-9)


def test_trace_distance_retains_tiny_distinct_rays_and_exact_equal_rays():
    a = ConditionalDensityLift.lift([1.0, 1.0, 1.0])
    opposite = ConditionalDensityLift.lift([-1.0, -1.0, -1.0])
    assert ConditionalDensityLift.trace_distance(a, a) == 0.0
    assert ConditionalDensityLift.trace_distance(a, opposite) == 0.0
    b = ConditionalDensityLift.lift([1.0, 1.0 + 1e-10, 1.0])
    distance = ConditionalDensityLift.trace_distance(a, b)
    assert 1e-12 < distance < 1e-9
    direct = float(np.linalg.svd(a.density_matrix - b.density_matrix, compute_uv=False).sum()) / 2
    assert math.isclose(distance, direct, rel_tol=1e-4, abs_tol=1e-16)


def test_zero_obstruction_domain_and_certificate_separation():
    """Verify that zero primal residual returns declared convention (0.0) and requires independent certification."""
    # Direct lift of zero vector is undefined and raises ValueError
    with pytest.raises(ValueError, match="zero-mass"):
        ConditionalDensityLift.lift([0.0, 0.0, 0.0])

    # compute_xi on zero primal residual returns declared convention 0.0
    xi_default = ConditionalDensityLift.compute_xi([0.0, 0.0, 0.0], [1.0, 1.0, 0.0])
    assert xi_default == 0.0

    # Non-zero residual does NOT return 0.0 without certificate or override
    xi_nonzero = ConditionalDensityLift.compute_xi([1.0, 0.0, 0.0], [1.0, 1.0, 1.0])
    assert xi_nonzero > 0.0

    # Explicitly unverified override returns 0.0 with clear parameter declaration
    xi_override = ConditionalDensityLift.compute_xi(
        [1.0, 0.0, 0.0], [1.0, 1.0, 1.0], unverified_override=True
    )
    assert xi_override == 0.0

    # Valid ZeroObstructionCertificate: B @ alpha == omega
    B = np.array([[-1.0, 1.0], [1.0, -1.0]])
    alpha = np.array([1.0, 2.0])
    omega = B @ alpha
    cert_valid = ZeroObstructionCertificate(boundary_matrix=B, potential=alpha, cochain=omega)
    assert cert_valid.verify()
    xi_cert = ConditionalDensityLift.compute_xi(list(omega), [1.0, 1.0], zero_certificate=cert_valid)
    assert xi_cert == 0.0

    # Invalid ZeroObstructionCertificate: B @ alpha != omega raises ValueError
    cert_invalid = ZeroObstructionCertificate(
        boundary_matrix=B, potential=alpha, cochain=np.array([9.9, 9.9])
    )
    assert not cert_invalid.verify()
    with pytest.raises(ValueError, match="Zero obstruction certificate verification failed"):
        ConditionalDensityLift.compute_xi(list(omega), [1.0, 1.0], zero_certificate=cert_invalid)


def test_optimal_pair_bounds_and_strictly_sub_unitary():
    """Verify optimal pair bounds: Xi < 1 strictly, with exact Xi=0 condition."""
    # Cyclic triangle with h = (2, 1, 1), phi = (1, 1, 1)
    h = [2.0, 1.0, 1.0]
    phi = [1.0, 1.0, 1.0]
    xi_triangle = ConditionalDensityLift.compute_xi(h, phi)

    # Analytical overlap: (1 + sqrt(2)) / sqrt(6)
    expected_overlap = (1.0 + math.sqrt(2.0)) / math.sqrt(6.0)
    expected_xi = math.sqrt(1.0 - expected_overlap ** 2)
    assert math.isclose(xi_triangle, expected_xi, rel_tol=1e-7)
    assert math.isclose(xi_triangle, 0.16910198, rel_tol=1e-6)

    # Strictly sub-unitary bound: Xi <= sqrt(1 - 1 / ||phi||_1) = sqrt(1 - 1/3) < 1
    phi_1_norm = sum(abs(x) for x in phi)
    bound = math.sqrt(1.0 - 1.0 / phi_1_norm)
    assert xi_triangle <= bound < 1.0

    # Exact zero distance condition: matching support, signs, AND uniform magnitude
    h_uniform = [1.0, 1.0, 1.0]
    xi_zero = ConditionalDensityLift.compute_xi(h_uniform, phi)
    assert math.isclose(xi_zero, 0.0, abs_tol=1e-9)


def test_evaluator_subordination_and_invalid_state_rejection():
    """Verify tiered priority admission policy and strict rejection of invalid evaluator states."""
    evaluator = GuardedEvaluator()
    curr = (2.0, 0.5, 0.25, 0.8)

    # Review counterexample: Candidate with NaN diagnostics (0, NaN, NaN, NaN) MUST BE REJECTED
    cand_nan = (0.0, float("nan"), float("nan"), float("nan"))
    accepted_nan, reason_nan = evaluator.is_admissible_transition(curr, cand_nan)
    assert not accepted_nan
    assert "Rejected" in reason_nan
    assert "non-finite or invalid" in reason_nan

    # Candidate with negative diagnostic MUST BE REJECTED
    cand_neg = (1.0, -0.5, 0.25, 0.4)
    accepted_neg, reason_neg = evaluator.is_admissible_transition(curr, cand_neg)
    assert not accepted_neg
    assert "negative" in reason_neg

    # Candidate with Xi > 1.0 MUST BE REJECTED
    cand_xi_overflow = (1.0, 0.5, 0.25, 1.5)
    accepted_xi, reason_xi = evaluator.is_admissible_transition(curr, cand_xi_overflow)
    assert not accepted_xi
    assert "exceeds 1.0" in reason_xi

    # Threshold validation: r_max <= 0 raises ValueError
    with pytest.raises(ValueError, match="r_max must be positive"):
        evaluator.is_admissible_transition(curr, (1.0, 0.5, 0.25, 0.4), r_max=0.0)

    # Threshold validation: eps < 0 raises ValueError
    with pytest.raises(ValueError, match="eps must be non-negative"):
        evaluator.is_admissible_transition(curr, (1.0, 0.5, 0.25, 0.4), eps=-1e-9)

    # 1. Primary branch: Phi_1 reduction accepts even if R_cl > R_max
    cand_phi_improved = (1.0, 0.5, 1.5, 0.4)
    accepted, reason = evaluator.is_admissible_transition(curr, cand_phi_improved, r_max=1.0)
    assert accepted
    assert "Phi_1 decreased" in reason

    # Candidate has worse Phi_1 but better Xi -> MUST BE REJECTED
    worse_phi = (2.5, 0.5, 0.25, 0.1)
    accepted, reason = evaluator.is_admissible_transition(curr, worse_phi)
    assert not accepted
    assert "increased" in reason

    # Candidate with sub-epsilon Phi_1 increase (creep within tolerance window) -> MUST BE REJECTED
    cand_phi_creep = (2.0 + 5e-10, 0.5, 0.25, 0.1)
    accepted, reason = evaluator.is_admissible_transition(curr, cand_phi_creep)
    assert not accepted
    assert "Primary quotient residual Phi_1 increased" in reason

    # 2. Secondary branch: Gamma_2 reduction accepts even if R_cl > R_max
    cand_gamma_improved = (2.0, 0.1, 1.5, 0.4)
    accepted, reason = evaluator.is_admissible_transition(curr, cand_gamma_improved, r_max=1.0)
    assert accepted
    assert "Gamma_2 decreased" in reason

    # Candidate with sub-epsilon Gamma_2 increase on tie-break -> MUST BE REJECTED
    cand_gamma_creep = (2.0, 0.5 + 5e-10, 0.25, 0.1)
    accepted, reason = evaluator.is_admissible_transition(curr, cand_gamma_creep)
    assert not accepted
    assert "Closure curvature Gamma_2 increased" in reason

    # 3. Tertiary branch: Guardrail R_cl <= R_max gating
    # Candidate with equal Phi_1, equal Gamma_2, lower Xi, but blown R_cl -> REJECTED
    blown_rcl = (2.0, 0.5, 1.5, 0.2)
    accepted, reason = evaluator.is_admissible_transition(curr, blown_rcl, r_max=1.0)
    assert not accepted
    assert "exceeds threshold" in reason

    # Candidate with equal Phi_1, equal Gamma_2, valid R_cl, lower Xi -> ACCEPTED
    cand_rcl_increase_within_bound = (2.0, 0.5, 0.75, 0.4)
    accepted, reason = evaluator.is_admissible_transition(curr, cand_rcl_increase_within_bound, r_max=1.0)
    assert accepted
    assert "tie-break" in reason

    # Candidate has equal Phi_1, equal Gamma_2, valid R_cl, but equal or worse Xi -> REJECTED
    worse_xi = (2.0, 0.5, 0.25, 0.9)
    accepted, reason = evaluator.is_admissible_transition(curr, worse_xi)
    assert not accepted
    assert "No improvement" in reason


def test_small_positive_obstruction_and_numerical_uncertainty():
    """Verify that small positive obstructions are not erased to zero, preserving scale invariance and explicit uncertainty."""
    # Review counterexample: oriented triangle with canonical residual (0, 0, 1e-13) and witness (1, 1, 1)
    h_small = [0.0, 0.0, 1e-13]
    phi_witness = [1.0, 1.0, 1.0]

    # Genuine obstruction: Phi_1 = 1e-13 > 0, Xi = sqrt(2/3) ~ 0.81649658
    xi_computed = ConditionalDensityLift.compute_xi(h_small, phi_witness)
    expected_xi = math.sqrt(2.0 / 3.0)
    assert math.isclose(xi_computed, expected_xi, rel_tol=1e-7)

    # Scale invariance holds down to float underflow regime
    for scale in [1.0, 1e-3, 1e-7, 1e-13, 1e-15]:
        h_scaled = [0.0, 0.0, 1.0 * scale]
        xi_scaled = ConditionalDensityLift.compute_xi(h_scaled, phi_witness)
        assert math.isclose(xi_scaled, expected_xi, rel_tol=1e-7)

    # When an explicit non-zero tolerance is specified without certificate, numerical uncertainty is raised
    with pytest.raises(ValueError, match="Numerical uncertainty"):
        ConditionalDensityLift.compute_xi(h_small, phi_witness, tolerance=1e-12)

    # When unverified_override=True is explicitly supplied, the zero-obstruction convention is invoked
    xi_override = ConditionalDensityLift.compute_xi(
        h_small, phi_witness, tolerance=1e-12, unverified_override=True
    )
    assert xi_override == 0.0


def test_density_lift_equality_and_hash_are_explicit():
    """Equal lifts compare equal and hash equal; the frozen array cannot be mutated afterwards."""
    a = ConditionalDensityLift.lift([1.0, -1.0])
    same = ConditionalDensityLift.lift([1.0, -1.0])
    scaled = ConditionalDensityLift.lift([2.0, -2.0])  # same state, different mass
    assert a == same
    assert hash(a) == hash(same)
    assert a != scaled
    assert len({a, same, scaled}) == 2
    with pytest.raises(ValueError):
        a.state_vector[0] = 5.0
    with pytest.raises(AssertionError):
        a == object()  # noqa: B015 - exact-type equality is asserted


def test_proved_finite_integer_and_rational_claims():
    """Drive the shipped exact checkers for the mechanized finite claims."""
    weights = ConditionalDensityLift.normalized_abs_weights([2, -3, 5, 0])
    assert weights == (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2), Fraction(0, 1))
    assert sum(weights) == 1
    assert ConditionalDensityLift.normalized_abs_weights([14, -21, 35, 0]) == weights
    assert ConditionalDensityLift.normalized_abs_weights([-2, 3, -5, 0]) == weights

    assert ConditionalDensityLift.integer_cauchy_gap([1, 0], [0, 1]) == 1
    assert ConditionalDensityLift.integer_cauchy_gap([3, 4], [3, 4]) == 0
    assert ConditionalDensityLift.integer_cauchy_gap([1, 2, 3], [3, -1, 2]) == 147

    assert ConditionalDensityLift.pairing_slack([1, 1, 1], [2, 1, 1]) == 0
    assert ConditionalDensityLift.pairing_slack([1, -1, 1], [2, 1, 1]) == 2
    assert ConditionalDensityLift.dual_mass_if_slack_vanishes([1, 1, 1], [2, 1, 1]) == 3
    assert ConditionalDensityLift.dual_mass_if_slack_vanishes([1, 0], [4, 0]) == 1
    assert ConditionalDensityLift.compute_xi([0, 0, 0], [1, 1, 1]) == 0.0

    eps = Fraction(1, 10**9)
    current = (Fraction(1), Fraction(1), Fraction(0), Fraction(1))
    increased = (Fraction(1) + Fraction(1, 10**10), Fraction(0), Fraction(0), Fraction(0))
    decreased = (Fraction(1) - 2 * eps, Fraction(1), Fraction(0), Fraction(1))
    gamma_up = (Fraction(1), Fraction(1) + Fraction(1, 10**10), Fraction(0), Fraction(0))
    gated = (Fraction(1), Fraction(1), Fraction(2), Fraction(0))
    assert GuardedEvaluator.exact_admissible(current, increased, Fraction(1), eps) is False
    assert GuardedEvaluator.exact_admissible(current, decreased, Fraction(1), eps) is True
    assert GuardedEvaluator.exact_admissible(current, gamma_up, Fraction(1), eps) is False
    assert GuardedEvaluator.exact_admissible(current, gated, Fraction(1), eps) is False
