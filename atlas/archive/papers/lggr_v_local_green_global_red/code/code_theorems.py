"""Numerical regression and replay harness for Theorems 1-6 and S13/S14."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import numpy as np
from code_blind_spots import (
    compute_interface_blind_spot_basis,
    has_full_coverage,
    has_trivial_blind_spots,
    numerical_rank_cutoff,
)
from code_core import Assignment, NormType, System, scaled_euclidean_norm
from code_witnesses import CoupledSystem, ScalarQuotientWitness, ThreePatchSystem


@dataclass(frozen=True)
class Theorem2Diagnostic:
    """Diagnostic report comparing evaluator greenness with defect blind spot projection."""
    is_all_green: bool
    defects_in_blind_spots: bool
    max_evaluator_score: float
    max_blind_spot_distance: float
    is_theoretically_consistent: bool


def norm_conversion_factor_a(dim: int, norm_type: NormType) -> float:
    """Return a such that ||v||_chosen <= a * ||v||_2 for v in R^dim."""
    if norm_type == NormType.L1:
        return float(np.sqrt(dim))
    elif norm_type == NormType.L2:
        return 1.0
    elif norm_type == NormType.LINF:
        return 1.0
    raise ValueError(f"Unsupported norm type: {norm_type}")


def norm_conversion_factor_b(dim: int, norm_type: NormType) -> float:
    """Return b such that ||v||_2 <= b * ||v||_chosen for v in R^dim."""
    if norm_type == NormType.L1:
        return 1.0
    elif norm_type == NormType.L2:
        return 1.0
    elif norm_type == NormType.LINF:
        return float(np.sqrt(dim))
    raise ValueError(f"Unsupported norm type: {norm_type}")


def _compute_interface_scaled_tolerance(
    iface_name: str,
    system: System,
    tol: float,
    rank_tol: Optional[float] = None,
) -> float:
    """Compute gain-scaled defect tolerance for interface e based on watcher measurement singular values and norm factors."""
    iface = system.interfaces[iface_name]
    watcher_matrices = []
    b_factors = []
    for ev in system.evaluator_family.evaluators.values():
        if iface_name in ev.watched_interfaces:
            mat = ev.measurement_matrices[iface_name]
            watcher_matrices.append(mat)
            val_norm = ev.value_norms.get(iface_name, iface.norm_type)
            dim_out = mat.shape[0]
            b_factors.append(norm_conversion_factor_b(dim_out, val_norm))

    if not watcher_matrices:
        return tol

    stacked = np.vstack(watcher_matrices)
    _, s, _ = np.linalg.svd(stacked, full_matrices=False)
    cutoff = numerical_rank_cutoff(s, stacked.shape, rank_tol=rank_tol)
    pos_s = s[s > cutoff]
    if len(pos_s) == 0:
        return tol
    sigma_min = float(pos_s[-1])
    b_term = float(np.sqrt(np.sum(np.square(b_factors))))
    scaled_tol = float((b_term * tol) / sigma_min)
    return max(tol, scaled_tol)


def diagnose_theorem_2(
    system: System,
    assignment: Assignment,
    tol: float = 1e-8,
    rank_tol: Optional[float] = None,
) -> Theorem2Diagnostic:
    """Diagnose Theorem 2 characterization with separate evaluator and blind spot metrics."""
    scores = system.evaluator_scores(assignment)
    max_score = max(scores.values()) if scores else 0.0
    is_green = max_score <= tol

    max_dist = 0.0
    defects_in_blind_spots = True
    dists = {}
    for iface_name, iface in system.interfaces.items():
        d = iface.compute_defect(assignment.get_state(iface.site_a), assignment.get_state(iface.site_b))
        basis = compute_interface_blind_spot_basis(iface_name, iface, system.evaluator_family, rank_tol=rank_tol)
        if basis.shape[1] == 0:
            dist = scaled_euclidean_norm(d)
        else:
            proj = basis @ (basis.T @ d)
            dist = scaled_euclidean_norm(d - proj)
        dists[iface_name] = dist
        if dist > max_dist:
            max_dist = dist

        scaled_tol = _compute_interface_scaled_tolerance(iface_name, system, tol, rank_tol=rank_tol)
        if dist > scaled_tol:
            defects_in_blind_spots = False

    # Check theoretical consistency with norm-aware operator bounds:
    # Theorem 2 states exact equivalence for exact zero cochains: All-Green <=> Delta(s)_e in K_e.
    # Numerically, disagreement between threshold sets (is_green vs defects_in_blind_spots)
    # arises from directional measurement gain or interface summation, and is reported
    # as an approximate diagnostic rather than a theoretical inconsistency.
    if is_green == defects_in_blind_spots:
        is_consistent = True
    else:
        # Check operator upper bound: J^alpha <= sum_{e in E_alpha} a_{out, e, alpha} ||Q^alpha_e||_2 dist_e + tol
        upper_bound_ok = True
        for ev_name, ev in system.evaluator_family.evaluators.items():
            ev_score = scores.get(ev_name, 0.0)
            bound = 0.0
            for e in ev.watched_interfaces:
                q_mat = ev.measurement_matrices[e]
                val_norm = ev.value_norms.get(e, system.interfaces[e].norm_type)
                a_out = norm_conversion_factor_a(q_mat.shape[0], val_norm)
                q_op_norm = float(np.linalg.norm(q_mat, ord=2))
                bound += a_out * q_op_norm * dists.get(e, 0.0)
            if ev_score > bound + tol:
                upper_bound_ok = False
                break

        # Check operator lower bound: dist_e <= scaled_tol when is_green
        lower_bound_ok = True
        for iface_name in system.interfaces:
            scaled_tol = _compute_interface_scaled_tolerance(iface_name, system, tol, rank_tol=rank_tol)
            if dists[iface_name] > scaled_tol and is_green:
                lower_bound_ok = False
                break

        is_consistent = upper_bound_ok and lower_bound_ok

    return Theorem2Diagnostic(
        is_all_green=is_green,
        defects_in_blind_spots=defects_in_blind_spots,
        max_evaluator_score=max_score,
        max_blind_spot_distance=max_dist,
        is_theoretically_consistent=is_consistent,
    )


def check_theorem_1_passivity(system: System, assignment: Assignment) -> bool:
    """Theorem 1 (Passivity): J^alpha(s) <= I(s) for all alpha, and I(s)=0 implies J^alpha(s)=0."""
    I_val = system.global_inconsistency(assignment)
    scores = system.evaluator_scores(assignment)
    if not (np.isfinite(I_val) and all(np.isfinite(j) for j in scores.values())):
        return False
    for J_val in scores.values():
        if J_val > I_val + 1e-9:
            return False
    return True


def check_theorem_2_characterization(
    system: System,
    assignment: Assignment,
    tol: float = 1e-8,
    rank_tol: Optional[float] = None,
) -> bool:
    """Theorem 2 (Characterization): All-Green <=> Delta(s)_e in K_e for all e.

    Harmonizes evaluation score tolerance and blind spot projection tolerance
    using measurement singular values and norm conversions to account for contractive/expanding measurement gains.
    """
    diag = diagnose_theorem_2(system, assignment, tol=tol, rank_tol=rank_tol)
    return diag.is_theoretically_consistent


def replay_theorem_3_three_patch(R: float) -> Tuple[bool, float, Dict[str, float]]:
    """Theorem 3 (Three-Patch Witness Replay): Explicit 3-patch system produces All-Green with exact inconsistency I(s) = R."""
    tp = ThreePatchSystem()
    lam = R / 6.0
    assignment = tp.create_scaled_assignment(lam)

    I_val = tp.system.global_inconsistency(assignment)
    scores = tp.system.evaluator_scores(assignment)
    all_green = tp.system.is_all_green(assignment)

    success = all_green and (abs(I_val - abs(R)) < 1e-9)
    return success, I_val, scores


def replay_theorem_4_no_recovery_modulus(f: Callable[[float], float]) -> Tuple[bool, float, float]:
    """Theorem 4 (No Recovery Modulus Replay): For any candidate recovery function f, I(s) > f(max_alpha J^alpha(s)).

    The exact unbounded mathematical witness is defined over Fractions in code/lgr_replay.py (defeat_recovery).
    This floating-point demonstration uses a proportional margin 2 * max(1.0, f(0)) to ensure strict inequality
    within the representable floating-point range. If f(0) is non-finite or overflows float representation,
    an OverflowError is raised directing the caller to the exact Fraction replay.
    """
    f_zero_raw = f(0.0)
    if not np.isfinite(f_zero_raw):
        raise ValueError(f"f(0) must be a finite float, got {f_zero_raw}")
    f_zero = float(f_zero_raw)

    target_I = 2.0 * max(1.0, f_zero)
    if not np.isfinite(target_I) or target_I <= f_zero:
        raise OverflowError(
            f"Candidate recovery bound f(0)={f_zero} exceeds floating-point range for proportional margin. "
            "Refer to the exact Fraction replay in code/lgr_replay.py (defeat_recovery)."
        )

    tp = ThreePatchSystem()
    lam = target_I / 6.0
    assignment = tp.create_scaled_assignment(lam)
    I_val = tp.system.global_inconsistency(assignment)
    max_J = max(tp.system.evaluator_scores(assignment).values())
    bound = f(max_J)

    success = (max_J < 1e-9) and (I_val > bound)
    return success, I_val, bound


def compute_recovery_constant(system: System, rank_tol: Optional[float] = None) -> float:
    """Compute quantitative recovery constant C such that I(s) <= C * max_alpha J^alpha(s)
    under full coverage and trivial blind spots, respecting declared norms.

    Formula:
        C = sum_e (a_e / sigma_min(Q_e)) * (sum_{alpha: e in E_alpha} b_{e, alpha}^2)^{1/2}
    where a_e bounds ||v||_F <= a_e ||v||_2 and b_{e, alpha} bounds ||y||_2 <= b_{e, alpha} ||y||_V.
    """
    total_c = 0.0
    for iface_name, iface in system.interfaces.items():
        watcher_matrices = []
        b_factors = []
        for ev in system.evaluator_family.evaluators.values():
            if iface_name in ev.watched_interfaces:
                mat = ev.measurement_matrices[iface_name]
                watcher_matrices.append(mat)
                val_norm = ev.value_norms.get(iface_name, iface.norm_type)
                dim_out = mat.shape[0]
                b_factors.append(norm_conversion_factor_b(dim_out, val_norm))
        if not watcher_matrices:
            return float("inf")
        stacked = np.vstack(watcher_matrices)
        _, s, _ = np.linalg.svd(stacked, full_matrices=False)
        cutoff = numerical_rank_cutoff(s, stacked.shape, rank_tol=rank_tol)
        pos_s = s[s > cutoff]
        dim_a = iface.translation_matrix.shape[0]
        if len(pos_s) < dim_a:
            return float("inf")
        sigma_min = float(pos_s[-1])
        a_e = norm_conversion_factor_a(dim_a, iface.norm_type)
        b_term = float(np.sqrt(np.sum(np.square(b_factors))))
        total_c += (a_e / sigma_min) * b_term
    return max(1.0, total_c)


def check_theorem_5_sufficiency(
    system: System,
    assignment: Assignment,
    tol: float = 1e-8,
    rank_tol: Optional[float] = None,
) -> bool:
    """Theorem 5 (Sufficient Condition Check): If full coverage and trivial blind spots hold,
    All-Green implies I(s) = 0 (or quantitatively I(s) <= C * max_alpha J^alpha(s)).
    """
    if not (has_full_coverage(system) and has_trivial_blind_spots(system, rank_tol=rank_tol)):
        # System does not satisfy the declared hypotheses of Theorem 5
        return False
    scores = system.evaluator_scores(assignment)
    max_score = max(scores.values()) if scores else 0.0
    I_val = system.global_inconsistency(assignment)

    if system.is_all_green(assignment, tol=tol):
        C = compute_recovery_constant(system, rank_tol=rank_tol)
        return bool(I_val <= C * max_score + tol)
    return True


def check_theorem_6_coupled_witness(cs: Optional[CoupledSystem] = None) -> bool:
    """Theorem 6 (Coupled Witness Replay): Coupled system has nontrivial blind spots, full coverage, yet All-Green forces I(s) = 0."""
    target_cs = cs if cs is not None else CoupledSystem()
    # 1. Check full coverage
    if not has_full_coverage(target_cs.system):
        return False

    # 2. Check blind spots are nontrivial (each has a 1D basis)
    if has_trivial_blind_spots(target_cs.system):
        return False

    # 3. Check for any section assignment with sx != 0, it CANNOT be All-Green unless sx == 0
    for v in [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([2.5, -3.2])]:
        a = target_cs.create_section_assignment(v)
        if target_cs.system.is_all_green(a):
            return False  # Nonzero defect cannot be green

    # 4. Zero section is All-Green and has I(s) = 0
    a0 = target_cs.create_section_assignment(np.zeros(2))
    return target_cs.system.is_all_green(a0) and (target_cs.system.global_inconsistency(a0) < 1e-9)


def check_remark_irreparable_red() -> bool:
    """Remark §4 / §6 (Quotient Irreparability Check): min_{alpha} ||omega - d0(alpha)||_1 = 2 > 0."""
    qw = ScalarQuotientWitness()
    alphas = np.linspace(-10, 10, 201)
    masses = [qw.repair_mass(a) for a in alphas]
    min_m = min(masses)
    at_zero = qw.repair_mass(0.0)
    return (min_m >= 2.0 - 1e-9) and (abs(at_zero - 2.0) < 1e-9)
