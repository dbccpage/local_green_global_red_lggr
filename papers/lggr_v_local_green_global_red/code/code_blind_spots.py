"""Blind spot kernel analysis and coverage geometry."""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from code_core import EvaluatorFamily, Interface, System, scaled_euclidean_norm


def numerical_rank_cutoff(
    singular_values: np.ndarray,
    shape: Tuple[int, int],
    rank_tol: Optional[float] = None,
) -> float:
    """Compute scale-aware singular value cutoff for numerical rank determination.

    Default policy: max(shape) * s[0] * eps.
    If singular values are all 0 or empty, returns 0.0.
    """
    if len(singular_values) == 0 or singular_values[0] <= 0.0:
        return 0.0
    if rank_tol is not None:
        return float(rank_tol)
    eps = np.finfo(float).eps
    return float(max(shape) * singular_values[0] * eps)


def compute_nullspace_basis(
    matrix: np.ndarray,
    rank_tol: Optional[float] = None,
    *,
    tol: Optional[float] = None,
) -> np.ndarray:
    """Compute orthonormal basis for nullspace (kernel) of a matrix via SVD.

    Uses scale-aware rank determination separate from any score/residual tolerance.
    For a 0 x n matrix (empty / unwatched), the nullspace is R^n, so returns I_n.
    """
    mat = np.asarray(matrix, dtype=float)
    if mat.size == 0 or mat.shape[0] == 0:
        n_cols = mat.shape[1] if mat.ndim == 2 else 0
        return np.eye(n_cols)
    if mat.ndim != 2:
        raise ValueError(f"Matrix must be 2D, got shape {mat.shape}")
    effective_rank_tol = rank_tol if rank_tol is not None else tol
    u, s, vh = np.linalg.svd(mat, full_matrices=True)
    n_cols = mat.shape[1]
    cutoff = numerical_rank_cutoff(s, mat.shape, rank_tol=effective_rank_tol)
    rank = int(np.sum(s > cutoff))
    null_basis = vh[rank:, :].T  # Columns form basis for nullspace
    return null_basis


def compute_interface_blind_spot_basis(
    interface_name: str,
    interface: Interface,
    evaluator_family: EvaluatorFamily,
    rank_tol: Optional[float] = None,
    *,
    tol: Optional[float] = None,
) -> np.ndarray:
    """Compute basis of the blind spot K_e = intersection of ker(q_e^alpha) for watchers of e."""
    watcher_matrices: List[np.ndarray] = []
    for ev in evaluator_family.evaluators.values():
        if interface_name in ev.watched_interfaces:
            q = ev.measurement_matrices[interface_name]
            watcher_matrices.append(q)

    dim_a = interface.translation_matrix.shape[0]

    # If unwatched, the blind spot is the entire space F(a)
    if not watcher_matrices:
        return np.eye(dim_a)

    # Stacking watcher measurement matrices: [q_e^1; q_e^2; ...]
    stacked = np.vstack(watcher_matrices)
    effective_rank_tol = rank_tol if rank_tol is not None else tol
    return compute_nullspace_basis(stacked, rank_tol=effective_rank_tol)


def is_in_blind_spot(
    defect: np.ndarray,
    blind_spot_basis: np.ndarray,
    tol: float = 1e-8,
) -> bool:
    """Check if defect vector lies in the subspace spanned by blind_spot_basis."""
    v = np.asarray(defect, dtype=float)
    if v.ndim != 1:
        raise ValueError(f"Expected 1D defect vector, got shape {v.shape}")
    if not np.all(np.isfinite(v)):
        raise ValueError("Defect vector contains non-finite values")
    if blind_spot_basis.shape[1] == 0:
        # Trivial subspace {0}
        return scaled_euclidean_norm(v) <= tol

    # Project v onto the orthogonal complement of the basis
    # Since basis columns from SVD are orthonormal:
    projection = blind_spot_basis @ (blind_spot_basis.T @ v)
    residual = v - projection
    return scaled_euclidean_norm(residual) <= tol


def has_full_coverage(system: System) -> bool:
    """Check if every interface is watched by at least one evaluator."""
    watched_all = set()
    for ev in system.evaluator_family.evaluators.values():
        watched_all.update(ev.watched_interfaces)
    return set(system.interfaces.keys()).issubset(watched_all)


def has_trivial_blind_spots(
    system: System,
    rank_tol: Optional[float] = None,
    *,
    tol: Optional[float] = None,
) -> bool:
    """Check if every interface has trivial blind spot K_e = {0}."""
    effective_rank_tol = rank_tol if rank_tol is not None else tol
    for iface_name, iface in system.interfaces.items():
        basis = compute_interface_blind_spot_basis(
            iface_name, iface, system.evaluator_family, rank_tol=effective_rank_tol
        )
        if basis.shape[1] > 0:
            return False
    return True
