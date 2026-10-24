"""Tests for blind spot computation and coverage checks."""
from __future__ import annotations

import numpy as np
import pytest
from code_blind_spots import (
    compute_interface_blind_spot_basis,
    compute_nullspace_basis,
    has_full_coverage,
    has_trivial_blind_spots,
    is_in_blind_spot,
)
from code_core import Interface, NormType
from code_witnesses import ThreePatchSystem, TrivialKernelThreePatchSystem


def test_compute_nullspace_basis():
    # Empty / 0-row matrix has nullspace R^n -> returns I_n
    empty_mat = np.empty((0, 3))
    basis_empty = compute_nullspace_basis(empty_mat)
    assert np.allclose(basis_empty, np.eye(3))

    # Empty 0-size matrix
    empty_0 = np.empty((0, 0))
    basis_0 = compute_nullspace_basis(empty_0)
    assert basis_0.shape == (0, 0)

    # 1D projection matrix in R^3 deleting coordinate 0
    # q = [[0, 1, 0], [0, 0, 1]] -> nullspace is [1, 0, 0]^T
    q = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    basis = compute_nullspace_basis(q)
    assert basis.shape == (3, 1)
    assert np.allclose(np.abs(basis.ravel()), np.array([1.0, 0.0, 0.0]))


def test_interface_blind_spot_basis_unwatched_and_watched():
    tp = ThreePatchSystem()
    iface = tp.system.interfaces["e_x01_u0"]
    basis = compute_interface_blind_spot_basis("e_x01_u0", iface, tp.system.evaluator_family)
    assert basis.shape == (3, 1)

    # Unwatched interface has blind spot = entire fiber
    unwatched_iface = Interface(name="unwatched", site_a="x01", site_b="u0",
                                translation_matrix=np.eye(3), norm_type=NormType.L1)
    basis_unwatched = compute_interface_blind_spot_basis("unwatched", unwatched_iface, tp.system.evaluator_family)
    assert np.allclose(basis_unwatched, np.eye(3))


def test_is_in_blind_spot():
    basis = np.array([[1.0], [0.0], [0.0]])
    assert is_in_blind_spot(np.array([5.0, 0.0, 0.0]), basis) is True
    assert is_in_blind_spot(np.array([5.0, 1.0, 0.0]), basis) is False

    # Trivial basis {0}
    empty_basis = np.empty((3, 0))
    assert is_in_blind_spot(np.array([0.0, 0.0, 0.0]), empty_basis) is True
    assert is_in_blind_spot(np.array([0.0, 1.0, 0.0]), empty_basis) is False


def test_coverage_and_triviality():
    tp = ThreePatchSystem()
    assert has_full_coverage(tp.system) is True
    assert has_trivial_blind_spots(tp.system) is False

    tk = TrivialKernelThreePatchSystem()
    assert has_full_coverage(tk.system) is True
    assert has_trivial_blind_spots(tk.system) is True


def test_scale_aware_rank_and_kernel_separation():
    """Item 4 Regression: A nonzero scalar operator's kernel must not be reported as the whole space.

    Tests scalar measurements 1, 1e-10, 1e-12 (all have trivial kernel {0}),
    genuinely zero measurement [[0.0]] (has full kernel R^1), and unwatched interface.
    """
    for q_val in [1.0, 1e-10, 1e-12]:
        Q = np.array([[q_val]])
        basis = compute_nullspace_basis(Q)
        # Trivial kernel: basis must have 0 columns (shape (1, 0))
        assert basis.shape == (1, 0), f"Kernel for gain {q_val} must be trivial, got {basis.shape}"

    # Genuinely zero measurement has kernel R^1
    Q_zero = np.array([[0.0]])
    basis_zero = compute_nullspace_basis(Q_zero)
    assert basis_zero.shape == (1, 1)
    assert np.allclose(basis_zero, np.array([[1.0]]))

    # Rank tolerance parameter override vs score tolerance separation
    basis_override = compute_nullspace_basis(np.array([[1e-10]]), rank_tol=1e-8)
    assert basis_override.shape == (1, 1)  # explicit rank_tol forced cutoff above singular value

    # Non-2D matrix rejection
    with pytest.raises(ValueError, match="Matrix must be 2D"):
        compute_nullspace_basis(np.array([1.0, 2.0]))

    # Defect vector validation for is_in_blind_spot
    basis = np.eye(2)
    with pytest.raises(ValueError, match="Expected 1D defect vector"):
        is_in_blind_spot(np.ones((2, 2)), basis)

    with pytest.raises(ValueError, match="Defect vector contains non-finite values"):
        is_in_blind_spot(np.array([1.0, np.nan]), basis)

