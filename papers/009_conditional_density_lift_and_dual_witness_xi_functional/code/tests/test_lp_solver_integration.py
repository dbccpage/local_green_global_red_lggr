"""End-to-end integration tests pairing an external LP solver with compute_xi across connected cycle topologies.

Validates the canonical selector specified in Monograph 009 Section 3:
- Successive coordinate minimization over compact optimal primal and dual faces.
- End-to-end pairing with ConditionalDensityLift.compute_xi across non-trivial cycle topologies.
- Exact verification of LP strong duality, complementary slackness, and sub-unitary Xi bounds.
- Zero-obstruction handling on exact coboundaries.
- Evaluator tie-breaking behavior on competing candidate proposals.
- Explicit certification boundary separating certified canonical pairs from uncertain tolerance-level results.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pytest
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_conditional_density_lift_core import ConditionalDensityLift, GuardedEvaluator


def certify_canonical_primal_dual_pair(
    edges: List[Tuple[int, int]],
    num_vertices: int,
    omega: List[float],
    h_star: np.ndarray,
    phi_star: np.ndarray,
    phi_1: float,
    tol_feas: float = 1e-6,
    tol_gap: float = 1e-6,
    rel_gap_tol: float = 1e-3,
) -> None:
    """Verify primal feasibility, dual feasibility, and certified duality gap for a canonical pair.

    Enforces that:
    1. Primal feasibility: omega - h* is in im(B) (exists alpha such that ||omega - h* - B alpha||_inf <= tol_feas).
    2. Dual feasibility: div(phi*) = B^T phi* = 0, and ||phi*||_inf <= 1.0 + tol_feas.
    3. Duality gap / optimality: ||h*||_1 and <phi*, omega> agree with each other and with Phi_1.

    Raises ValueError if any feasibility or duality certificate fails.
    """
    m = len(edges)
    n = num_vertices
    B = np.zeros((m, n), dtype=float)
    for e, (u, v) in enumerate(edges):
        B[e, u] = -1.0
        B[e, v] = 1.0

    arr_omega = np.asarray(omega, dtype=float)

    if phi_1 == 0.0:
        if not np.allclose(h_star, 0.0, atol=1e-12):
            raise ValueError(f"Phi_1 is 0.0 but primal residual h* is non-zero: {h_star}")
        if not np.allclose(phi_star, 0.0, atol=1e-12):
            raise ValueError(f"Phi_1 is 0.0 but dual witness phi* is non-zero: {phi_star}")
        alpha, _, _, _ = np.linalg.lstsq(B, arr_omega, rcond=None)
        cobo_res = float(np.max(np.abs(arr_omega - B @ alpha)))
        scale_omega = max(float(np.max(np.abs(arr_omega))), 1.0)
        if cobo_res > 1e-12 * scale_omega:
            raise ValueError(f"False zero claim: cochain is not an exact coboundary (residual {cobo_res} > {1e-12 * scale_omega}).")
        return

    # 1. Primal feasibility
    alpha, _, _, _ = np.linalg.lstsq(B, arr_omega - h_star, rcond=None)
    primal_res = float(np.max(np.abs(arr_omega - h_star - B @ alpha)))
    scale_omega = max(float(np.max(np.abs(arr_omega))), 1.0)
    if primal_res / scale_omega > tol_feas:
        raise ValueError(f"Primal infeasibility: ||omega - h* - B alpha||_inf = {primal_res} > {tol_feas}")

    # 2. Dual feasibility
    div_phi = float(np.max(np.abs(B.T @ phi_star)))
    if div_phi > tol_feas:
        raise ValueError(f"Dual circulation violation: ||B^T phi*||_inf = {div_phi} > {tol_feas}")
    norm_phi_inf = float(np.max(np.abs(phi_star)))
    if norm_phi_inf > 1.0 + tol_feas:
        raise ValueError(f"Dual box violation: ||phi*||_inf = {norm_phi_inf} > 1.0 + {tol_feas}")

    # 3. Certified objective gap
    primal_obj = float(np.sum(np.abs(h_star)))
    dual_obj = float(np.dot(phi_star, arr_omega))
    gap = abs(primal_obj - dual_obj)
    scale = max(primal_obj, dual_obj, 1e-12)
    rel_gap = gap / scale

    if (scale > 1e-9 and rel_gap > rel_gap_tol) or gap > tol_gap:
        raise ValueError(f"Duality gap uncertified: primal {primal_obj} vs dual {dual_obj} (gap={gap}, rel={rel_gap})")
    if (scale > 1e-9 and abs(primal_obj - phi_1) / scale > rel_gap_tol) or abs(primal_obj - phi_1) > tol_gap:
        raise ValueError(f"Primal objective mismatch with Phi_1 ({phi_1}): primal {primal_obj}")
    if (scale > 1e-9 and abs(dual_obj - phi_1) / scale > rel_gap_tol) or abs(dual_obj - phi_1) > tol_gap:
        raise ValueError(f"Dual objective mismatch with Phi_1 ({phi_1}): dual {dual_obj}")


def solve_canonical_primal_dual_pair(
    edges: List[Tuple[int, int]],
    num_vertices: int,
    omega: List[float],
    tol: float = 1e-7,
    certify: bool = True,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Solve for canonical primal residual h* and dual witness phi* using successive coordinate minimization.

    Implements the canonical selector from Monograph 009 Section 3:
    1. Primary LP: Computes Phi_1 = min ||h||_1 subject to h in [omega] (h + B alpha = omega).
       Uses relative scale normalization (scale = ||omega||_inf) to maintain well-conditioned LP
       feasibility checks across all positive scales down to floating-point underflow.
    2. Primal Successive Coordinate Minimization: Successively minimizes h_{e_k} over the compact
       optimal face K_{k-1} for k = 0, ..., m-1.
    3. Dual Successive Coordinate Minimization: Successively minimizes phi_{e_k} over the compact
       optimal face L_{k-1} for k = 0, ..., m-1, where B^T phi = 0, ||phi||_inf <= 1, <phi, omega> = Phi_1.

    Zero-Obstruction and Uncertainty Boundary:
    - An exact coboundary is verified independently via least-squares coboundary projection.
      Only if ||omega - B alpha||_inf <= 1e-12 * scale is Phi_1 = 0 returned.
    - If Phi_1 / scale <= tol but omega is NOT an exact coboundary, the result is treated as
      numerically uncertain and a ValueError is raised rather than falsely reporting an exact zero.
    - When certify=True (default), primal feasibility, dual feasibility, and objective duality gap
      are strictly verified before calling the pair canonical.

    Returns:
        (h_star, phi_star, phi_1)
    """
    m = len(edges)
    n = num_vertices
    B = np.zeros((m, n), dtype=float)
    for e, (u, v) in enumerate(edges):
        B[e, u] = -1.0
        B[e, v] = 1.0

    arr_omega = np.asarray(omega, dtype=float)
    omega_inf = float(np.max(np.abs(arr_omega)))
    if omega_inf == 0.0:
        return np.zeros(m), np.zeros(m), 0.0

    # Scale-normalize to protect LP conditioning and preserve scale invariance for small positive scalings
    scale = omega_inf
    omega_norm = arr_omega / scale

    # Check for exact coboundary before LP optimization
    alpha_cobo, _, _, _ = np.linalg.lstsq(B, arr_omega, rcond=None)
    cobo_res = float(np.max(np.abs(arr_omega - B @ alpha_cobo)))
    if cobo_res <= 1e-12 * scale:
        return np.zeros(m), np.zeros(m), 0.0

    # 1. Primary LP: min sum(h^+ + h^-) s.t. h^+ - h^- + B alpha = omega_norm, h^+, h^- >= 0
    c = np.concatenate([np.ones(m), np.ones(m), np.zeros(n)])
    A_eq = np.hstack([np.eye(m), -np.eye(m), B])
    b_eq = omega_norm
    bounds = [(0, None)] * (2 * m) + [(None, None)] * n
    res0 = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res0.success:
        raise RuntimeError(f"Primary LP optimization failed: {res0.message}")
    phi_1_norm = float(res0.fun)

    if phi_1_norm <= tol:
        # Near-exact obstruction: within relative tolerance regime but NOT an exact coboundary
        raise ValueError(
            f"Numerical uncertainty: relative obstruction {phi_1_norm:.2e} <= tol={tol:.2e}, "
            f"but cochain is not an exact coboundary (residual={cobo_res:.2e}). "
            f"Cannot certify canonical optimal pair at tolerance {tol}."
        )

    # 2. Primal Successive Coordinate Minimization on scale-normalized cochain
    A_ub = np.array([np.concatenate([np.ones(m), np.ones(m), np.zeros(n)])])
    b_ub = np.array([phi_1_norm + 1e-9])
    current_A_eq = list(A_eq)
    current_b_eq = list(b_eq)
    h_star_norm = np.zeros(m)
    for k in range(m):
        c_k = np.zeros(2 * m + n)
        c_k[k] = 1.0
        c_k[m + k] = -1.0
        res_k = linprog(
            c_k,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=np.array(current_A_eq),
            b_eq=np.array(current_b_eq),
            bounds=bounds,
            method="highs",
        )
        if not res_k.success:
            raise RuntimeError(f"Primal coordinate {k} minimization failed: {res_k.message}")
        val_k = float(res_k.x[k] - res_k.x[m + k])
        h_star_norm[k] = val_k
        row = np.zeros(2 * m + n)
        row[k] = 1.0
        row[m + k] = -1.0
        current_A_eq.append(row)
        current_b_eq.append(val_k)

    # 3. Dual Successive Coordinate Minimization
    A_ub_dual = np.array([-omega_norm])
    b_ub_dual = np.array([-phi_1_norm + 1e-9])
    current_A_eq_dual = list(B.T)
    current_b_eq_dual = list(np.zeros(n))
    bounds_dual = [(-1.0, 1.0)] * m
    phi_star = np.zeros(m)
    for k in range(m):
        c_dual_k = np.zeros(m)
        c_dual_k[k] = 1.0
        res_dual_k = linprog(
            c_dual_k,
            A_ub=A_ub_dual,
            b_ub=b_ub_dual,
            A_eq=np.array(current_A_eq_dual),
            b_eq=np.array(current_b_eq_dual),
            bounds=bounds_dual,
            method="highs",
        )
        if not res_dual_k.success:
            raise RuntimeError(f"Dual coordinate {k} minimization failed: {res_dual_k.message}")
        val_dual_k = float(res_dual_k.x[k])
        phi_star[k] = val_dual_k
        row_dual = np.zeros(m)
        row_dual[k] = 1.0
        current_A_eq_dual.append(row_dual)
        current_b_eq_dual.append(val_dual_k)

    # Clean microscopic numerical zero noise relative to problem scale
    clean_tol = min(1e-7, max(1e-12, 1e-3 * phi_1_norm))
    h_star_norm = np.where(np.abs(h_star_norm) < clean_tol, 0.0, h_star_norm)
    phi_star = np.where(np.abs(phi_star) < clean_tol, 0.0, phi_star)
    h_star = h_star_norm * scale
    phi_1 = phi_1_norm * scale

    if certify:
        certify_canonical_primal_dual_pair(edges, num_vertices, omega, h_star, phi_star, phi_1)

    return h_star, phi_star, phi_1


def test_figure_eight_topology_shared_vertex_cycles():
    """Verify Figure-Eight topology B_2 (two independent cycles sharing a vertex)."""
    # 5 vertices (0 is shared hub), 6 edges
    # Cycle 1: (0, 1), (1, 2), (2, 0)
    # Cycle 2: (0, 3), (3, 4), (4, 0)
    edges = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]
    omega = [1.0, 0.0, 0.0, 2.0, 0.0, 0.0]

    h_star, phi_star, phi_1 = solve_canonical_primal_dual_pair(edges, 5, omega)

    # Verify LP strong duality
    assert math.isclose(float(np.sum(np.abs(h_star))), phi_1, rel_tol=1e-7)
    assert math.isclose(float(np.dot(phi_star, omega)), phi_1, rel_tol=1e-7)
    assert math.isclose(phi_1, 3.0, rel_tol=1e-7)

    # Verify dual circulation condition: div(phi) = 0 at every vertex
    B = np.zeros((6, 5))
    for e, (u, v) in enumerate(edges):
        B[e, u] = -1.0
        B[e, v] = 1.0
    div_phi = B.T @ phi_star
    assert np.allclose(div_phi, 0.0, atol=1e-7)

    # Verify complementary slackness: supp(h*) subset supp(phi*) and signs match
    for e in range(6):
        if abs(h_star[e]) > 1e-6:
            assert abs(phi_star[e]) > 0.99
            assert math.isclose(np.sign(phi_star[e]), np.sign(h_star[e]), abs_tol=1e-6)

    # Compute Xi functional
    xi = ConditionalDensityLift.compute_xi(list(h_star), list(phi_star))
    assert 0.0 < xi < 1.0

    # Verify strictly sub-unitary bound: Xi <= sqrt(1 - 1 / ||phi*||_1)
    phi_1_norm = float(np.sum(np.abs(phi_star)))
    bound = math.sqrt(1.0 - 1.0 / phi_1_norm)
    assert xi <= bound + 1e-9


def test_theta_graph_shared_edge_cycles():
    """Verify Theta graph topology (two fundamental cycles sharing an edge chord)."""
    # 4 vertices, 5 edges: (0, 1), (1, 2), (0, 2), (0, 3), (3, 2)
    # Edge 2 = (0, 2) is the shared chord coupling both cycles
    edges = [(0, 1), (1, 2), (0, 2), (0, 3), (3, 2)]
    omega = [1.0, 1.0, 0.0, 0.0, 0.0]

    h_star, phi_star, phi_1 = solve_canonical_primal_dual_pair(edges, 4, omega)

    assert math.isclose(phi_1, 2.0, rel_tol=1e-7)
    assert math.isclose(float(np.sum(np.abs(h_star))), 2.0, rel_tol=1e-7)
    assert math.isclose(float(np.dot(phi_star, omega)), 2.0, rel_tol=1e-7)

    # Dual circulation divergence is zero
    B = np.zeros((5, 4))
    for e, (u, v) in enumerate(edges):
        B[e, u] = -1.0
        B[e, v] = 1.0
    assert np.allclose(B.T @ phi_star, 0.0, atol=1e-7)

    # Compute Xi functional and check analytical bound
    xi = ConditionalDensityLift.compute_xi(list(h_star), list(phi_star))
    phi_1_norm = float(np.sum(np.abs(phi_star)))
    bound = math.sqrt(1.0 - 1.0 / phi_1_norm)
    assert 0.0 < xi <= bound + 1e-9 < 1.0


def test_dumbbell_graph_bridge_connected_cycles():
    """Verify Dumbbell graph topology (two cycle components connected by a cut edge bridge)."""
    # 6 vertices, 7 edges:
    # Cycle 1: (0, 1), (1, 2), (2, 0)
    # Bridge: (2, 3) (edge 3)
    # Cycle 2: (3, 4), (4, 5), (5, 3)
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
    omega = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    h_star, phi_star, phi_1 = solve_canonical_primal_dual_pair(edges, 6, omega)

    assert math.isclose(phi_1, 2.0, rel_tol=1e-7)
    # The bridge edge cannot sustain circulation in any cycle
    assert math.isclose(phi_star[3], 0.0, abs_tol=1e-7)

    xi = ConditionalDensityLift.compute_xi(list(h_star), list(phi_star))
    assert 0.0 < xi < 1.0


def test_complete_graph_k4_exact_vs_obstructed():
    """Verify Complete graph K_4 on both exact coboundaries and obstructed cochains."""
    # 4 vertices, 6 edges: (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    B = np.zeros((6, 4))
    for e, (u, v) in enumerate(edges):
        B[e, u] = -1.0
        B[e, v] = 1.0

    # 1. Exact coboundary: omega = B @ alpha
    alpha = np.array([1.5, -2.0, 3.5, 0.0])
    omega_exact = list(B @ alpha)
    h_exact, phi_exact, phi_1_exact = solve_canonical_primal_dual_pair(edges, 4, omega_exact)

    assert phi_1_exact == 0.0
    assert np.allclose(h_exact, 0.0)
    # compute_xi returns declared convention 0.0 for exact cochains
    xi_exact = ConditionalDensityLift.compute_xi(list(h_exact), list(phi_exact))
    assert xi_exact == 0.0

    # 2. Obstructed cochain with cycle obstruction
    omega_obstr = [2.0, 1.0, 0.0, 1.0, 0.0, 0.0]
    h_obstr, phi_obstr, phi_1_obstr = solve_canonical_primal_dual_pair(edges, 4, omega_obstr)

    assert phi_1_obstr > 0.0
    xi_obstr = ConditionalDensityLift.compute_xi(list(h_obstr), list(phi_obstr))
    phi_1_norm = float(np.sum(np.abs(phi_obstr)))
    bound = math.sqrt(1.0 - 1.0 / phi_1_norm)
    assert 0.0 < xi_obstr <= bound + 1e-9 < 1.0


def test_successive_coordinate_minimization_attains_minimum_where_support_first_fails():
    """Verify that successive coordinate minimization attains the exact unique minimum on the monograph Section 3 counterexample."""
    # Two disjoint triangles: edges 0..2 and 3..5
    edges = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]
    omega = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    h_star, phi_star, phi_1 = solve_canonical_primal_dual_pair(edges, 6, omega)

    # Primary quotient norm is 2.0
    assert math.isclose(phi_1, 2.0, rel_tol=1e-7)
    # Successive coordinate minimization successively minimizes coordinates 0, 1, ..., 5.
    # On triangle 1: h_0 is minimized to 0, h_1 to 0, leaving h_2 = 1.
    # On triangle 2: h_3 is minimized to 0, h_4 to 0, leaving h_5 = 1.
    expected_h = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    assert np.allclose(h_star, expected_h, atol=1e-6)

    # Dual circulation: phi* = (1, 1, 1, 1, 1, 1)
    expected_phi = np.ones(6)
    assert np.allclose(phi_star, expected_phi, atol=1e-6)

    # Compute Xi functional: overlap = 2 / (sqrt(2) * sqrt(6)) = 1 / sqrt(3)
    # Xi = sqrt(1 - 1/3) = sqrt(2/3) ~ 0.81649658
    xi = ConditionalDensityLift.compute_xi(list(h_star), list(phi_star))
    expected_xi = math.sqrt(2.0 / 3.0)
    assert math.isclose(xi, expected_xi, rel_tol=1e-7)


def test_evaluator_tie_breaking_on_competing_proposals():
    """Verify end-to-end integration with GuardedEvaluator on competing LP-solved proposals."""
    # Consider Theta graph: edges = [(0, 1), (1, 2), (0, 2), (0, 3), (3, 2)]
    edges = [(0, 1), (1, 2), (0, 2), (0, 3), (3, 2)]

    # Current state
    curr_state = (2.0, 0.5, 0.3, 0.85)
    evaluator = GuardedEvaluator()

    # Candidate 1: solved via LP, achieves Phi_1 = 2.0, with lower Xi = 0.8165 and valid R_cl = 0.4
    omega_cand1 = [1.0, 1.0, 0.0, 0.0, 0.0]
    h1, phi1, p1 = solve_canonical_primal_dual_pair(edges, 4, omega_cand1)
    xi1 = ConditionalDensityLift.compute_xi(list(h1), list(phi1))
    cand1_state = (p1, 0.5, 0.4, xi1)

    accepted1, reason1 = evaluator.is_admissible_transition(curr_state, cand1_state, r_max=1.0)
    assert accepted1
    assert "tie-break" in reason1

    # Candidate 2: identical Phi_1 and Gamma_2, lower Xi, but blown R_cl = 1.5 > R_max
    cand2_state = (p1, 0.5, 1.5, xi1)
    accepted2, reason2 = evaluator.is_admissible_transition(curr_state, cand2_state, r_max=1.0)
    assert not accepted2
    assert "exceeds threshold" in reason2

    # Candidate 3: sub-epsilon increase in Phi_1 (creep) with lower Xi -> MUST BE REJECTED
    cand3_state = (curr_state[0] + 5e-10, 0.5, 0.4, xi1)
    accepted3, reason3 = evaluator.is_admissible_transition(curr_state, cand3_state, r_max=1.0)
    assert not accepted3
    assert "Primary quotient residual Phi_1 increased" in reason3


def test_small_positive_scaling_preserves_scale_invariance_in_lp():
    """Verify that LP solver with relative scaling correctly identifies small positive obstructions and preserves scale invariance."""
    # Oriented triangle: 3 edges, 3 vertices
    edges = [(0, 1), (1, 2), (2, 0)]

    # Small positive obstruction: omega = (0, 0, 1e-13)
    omega_small = [0.0, 0.0, 1e-13]
    h_star, phi_star, phi_1 = solve_canonical_primal_dual_pair(edges, 3, omega_small)

    assert math.isclose(phi_1, 1e-13, rel_tol=1e-7)
    assert math.isclose(float(np.sum(np.abs(h_star))), 1e-13, rel_tol=1e-7)
    assert np.allclose(phi_star, np.ones(3), atol=1e-6)

    # Genuine obstruction: Xi = sqrt(2/3), NOT erased to 0
    xi = ConditionalDensityLift.compute_xi(list(h_star), list(phi_star))
    expected_xi = math.sqrt(2.0 / 3.0)
    assert math.isclose(xi, expected_xi, rel_tol=1e-7)

    # Unit scaled cochain: omega = (0, 0, 1.0) produces identical dual witness and Xi
    omega_unit = [0.0, 0.0, 1.0]
    h_unit, phi_unit, phi_1_unit = solve_canonical_primal_dual_pair(edges, 3, omega_unit)
    xi_unit = ConditionalDensityLift.compute_xi(list(h_unit), list(phi_unit))
    assert math.isclose(xi_unit, expected_xi, rel_tol=1e-7)
    assert np.allclose(phi_star, phi_unit, atol=1e-6)


def test_near_exact_lp_uncertainty_and_certification_boundary():
    """Verify that near-exact LP results are treated as uncertain rather than falsely labeled exact."""
    # Oriented triangle: 3 edges, 3 vertices
    edges = [(0, 1), (1, 2), (2, 0)]
    # Review counterexample: omega = (1.0, -1.0, 5e-8), exact cycle sum = 5e-8
    omega_near = [1.0, -1.0, 5e-8]

    # At tol = 1e-7, relative Phi_1 ~ 5e-8 <= 1e-7, but omega is NOT an exact coboundary.
    # Must raise ValueError for numerical uncertainty rather than reporting Phi_1 = 0 and zero vectors!
    with pytest.raises(ValueError, match="Numerical uncertainty"):
        solve_canonical_primal_dual_pair(edges, 3, omega_near, tol=1e-7)

    # Verification of certification gate:
    # 1. Claiming Phi_1 = 0 on non-coboundary fails certification
    with pytest.raises(ValueError, match="False zero claim"):
        certify_canonical_primal_dual_pair(edges, 3, omega_near, np.zeros(3), np.zeros(3), 0.0)

    # 2. Primal-dual objective mismatch fails certification
    with pytest.raises(ValueError, match="Duality gap uncertified"):
        certify_canonical_primal_dual_pair(
            edges, 3, omega_near, np.array([0.0, 0.0, 5e-8]), np.zeros(3), 5e-8
        )
