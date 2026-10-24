"""Primal-dual numerical quotient distance solver across Minkowski norms (L1, L2, L_inf) with dual certificates."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Sequence, Union

import numpy as np
from scipy import linalg, optimize


class MinkowskiNorm(str, Enum):
    """Minkowski norms for quotient distance computation."""
    L1 = "l1"
    L2 = "l2"
    L_INF = "linf"

    @classmethod
    def from_value(cls, val: Union[MinkowskiNorm, int, float, str]) -> MinkowskiNorm:
        if isinstance(val, MinkowskiNorm):
            return val
        if isinstance(val, (int, float)):
            if val == 1:
                return cls.L1
            elif val == 2:
                return cls.L2
            elif np.isinf(val):
                return cls.L_INF
        elif isinstance(val, str):
            s = val.strip().lower()
            if s in ("1", "l1", "taxicab", "manhattan"):
                return cls.L1
            elif s in ("2", "l2", "euclidean", "hilbert"):
                return cls.L2
            elif s in ("inf", "linf", "infinity", "chebyshev", "max"):
                return cls.L_INF
        raise ValueError(f"Unsupported Minkowski norm: {val}. Must be 1, 2, or inf.")


def scaled_euclidean_norm(v: np.ndarray) -> float:
    """Compute scaled Euclidean norm s * sqrt(sum((v/s)**2)) to avoid underflow and overflow."""
    arr = np.asarray(v, dtype=float).ravel()
    if arr.size == 0:
        return 0.0
    s = float(np.max(np.abs(arr)))
    if s == 0.0:
        return 0.0
    scaled = arr / s
    val = s * float(np.sqrt(np.sum(scaled * scaled)))
    if not np.isfinite(val):
        raise ValueError(f"Computed Euclidean norm is non-finite: {val}")
    return val


@dataclass(frozen=True)
class QuotientResult:
    """Numerically certified quotient distance result with primal and dual witnesses."""
    norm: MinkowskiNorm
    primal_distance: float
    optimal_alpha: np.ndarray
    residual: np.ndarray
    dual_witness: np.ndarray
    dual_objective: float
    duality_gap: float
    is_numerically_certified: bool
    is_approximate_zero: bool = False

    @property
    def is_exact_certified(self) -> bool:
        """Deprecated: aliases is_numerically_certified. Numerical LP certificates are not exact rational certificates."""
        return self.is_numerically_certified


class QuotientDistanceSolver:
    """Computes numerical quotient distance dist_p(omega, im(D)) = inf_alpha ||omega - D alpha||_p.

    Provides dual witness certificates W:
    - For p=1: ||W||_inf <= 1, D^T W = 0, <W, omega> = ||omega - D alpha*||_1
    - For p=2: ||W||_2 <= 1, D^T W = 0, <W, omega> = ||omega - D alpha*||_2
    - For p=inf: ||W||_1 <= 1, D^T W = 0, <W, omega> = ||omega - D alpha*||_inf
    """

    @staticmethod
    def _equilibrate_columns(D: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Compute column scale factors s_j: divide by column L_inf norm when > 1e-14; otherwise s_j = 1.0 (unscaled)."""
        m, n = D.shape
        scales = np.ones(n, dtype=float)
        for j in range(n):
            col_max = float(np.max(np.abs(D[:, j])))
            if col_max > 1e-14:
                scales[j] = col_max
        D_scaled = D / scales[np.newaxis, :]
        return D_scaled, scales

    @staticmethod
    def _svd_rank_cutoff(S: np.ndarray, m: int, n: int) -> float:
        """Standard numerical rank threshold following NumPy linalg.matrix_rank."""
        if len(S) == 0 or S[0] <= 0.0:
            return 0.0
        return float(S[0] * max(m, n) * np.finfo(float).eps)

    @staticmethod
    def _exact_pivot_columns(D: np.ndarray) -> list[int]:
        """Find column indices that form a basis for im(D) using exact Gaussian elimination over Q."""
        m, n = D.shape
        if m == 0 or n == 0:
            return []
        A = [[Fraction(float(D[i, j])) for j in range(n)] for i in range(m)]
        pivot_cols: list[int] = []
        current_row = 0
        for col in range(n):
            pivot_row = None
            for row in range(current_row, m):
                if A[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row is not None:
                pivot_cols.append(col)
                A[current_row], A[pivot_row] = A[pivot_row], A[current_row]
                pivot_val = A[current_row][col]
                for j in range(col, n):
                    A[current_row][j] /= pivot_val
                for r in range(m):
                    if r != current_row and A[r][col] != 0:
                        factor = A[r][col]
                        for j in range(col, n):
                            A[r][j] -= factor * A[current_row][j]
                current_row += 1
                if current_row == m:
                    break
        return pivot_cols

    @staticmethod
    def _project_dual_witness(D: np.ndarray, witness: np.ndarray, norm: MinkowskiNorm, tol: float) -> tuple[np.ndarray, bool]:
        """Project witness onto ker(D^T) = (im D)^perp, normalize by dual norm, and check relative orthogonality."""
        m, n = D.shape
        pivot_cols = QuotientDistanceSolver._exact_pivot_columns(D) if (m > 0 and n > 0) else []
        if n > 0 and len(pivot_cols) < n:
            D_eff = D[:, pivot_cols] if len(pivot_cols) > 0 else np.zeros((m, 0), dtype=float)
        else:
            D_eff = D

        m_eff, n_eff = D_eff.shape
        if n_eff == 0:
            w_proj = witness.copy()
            if norm == MinkowskiNorm.L1:
                dual_norm = float(np.max(np.abs(w_proj))) if m > 0 else 0.0
            elif norm == MinkowskiNorm.L2:
                dual_norm = scaled_euclidean_norm(w_proj)
            else:
                dual_norm = float(np.sum(np.abs(w_proj)))
            if dual_norm > 1.0:
                w_proj = w_proj / dual_norm
            return w_proj, True

        U, S, _ = linalg.svd(D_eff, full_matrices=True)
        cutoff = QuotientDistanceSolver._svd_rank_cutoff(S, m_eff, n_eff)
        active_mask = S > cutoff
        rank = int(np.sum(active_mask))
        if rank >= m:
            return np.zeros(m, dtype=float), True

        if np.any((S > 0) & (S <= cutoff)):
            return np.zeros(m, dtype=float), False

        U_null = U[:, rank:]
        w_proj = U_null @ (U_null.T @ witness)

        if norm == MinkowskiNorm.L1:
            dual_norm = float(np.max(np.abs(w_proj))) if m > 0 else 0.0
        elif norm == MinkowskiNorm.L2:
            dual_norm = scaled_euclidean_norm(w_proj)
        else:
            dual_norm = float(np.sum(np.abs(w_proj)))

        if dual_norm > 1.0:
            w_proj = w_proj / dual_norm

        if rank > 0:
            U_img = U[:, :rank]
            subspace_defect = scaled_euclidean_norm(U_img.T @ w_proj)
            if subspace_defect > tol:
                return w_proj, False

        return w_proj, True

    @staticmethod
    def solve(
        omega: np.ndarray,
        D: np.ndarray,
        norm: Union[MinkowskiNorm, int, float, str] = MinkowskiNorm.L1,
        tol: float = 1e-7,
    ) -> QuotientResult:
        """Solve quotient distance minimization problem and certify with dual witness."""
        if not (isinstance(tol, (int, float)) and np.isfinite(tol) and 0 < tol < 1.0):
            raise ValueError(f"Solver tolerance must be a finite positive float < 1.0, got {tol}")

        omega_arr = np.asarray(omega, dtype=float).ravel()
        m = len(omega_arr)
        D_arr = np.asarray(D, dtype=float)
        if D_arr.ndim == 1:
            D_arr = D_arr.reshape(m, 1)
        elif D_arr.shape[0] != m:
            raise ValueError(f"Shape mismatch: omega has length {m}, but D has shape {D_arr.shape}")

        parsed_norm = MinkowskiNorm.from_value(norm)

        # Check for exact column redundancy
        n_cols = D_arr.shape[1]
        pivot_cols = QuotientDistanceSolver._exact_pivot_columns(D_arr) if n_cols > 0 else []
        if n_cols > 0 and len(pivot_cols) < n_cols:
            D_basis = D_arr[:, pivot_cols] if len(pivot_cols) > 0 else np.zeros((m, 0), dtype=float)
            res_basis = QuotientDistanceSolver.solve(omega_arr, D_basis, norm=parsed_norm, tol=tol)
            full_alpha = np.zeros(n_cols, dtype=float)
            if len(pivot_cols) > 0:
                full_alpha[pivot_cols] = res_basis.optimal_alpha
            return QuotientResult(
                norm=res_basis.norm,
                primal_distance=res_basis.primal_distance,
                optimal_alpha=full_alpha,
                residual=res_basis.residual,
                dual_witness=res_basis.dual_witness,
                dual_objective=res_basis.dual_objective,
                duality_gap=res_basis.duality_gap,
                is_numerically_certified=res_basis.is_numerically_certified,
                is_approximate_zero=res_basis.is_approximate_zero,
            )

        if parsed_norm == MinkowskiNorm.L2:
            res = QuotientDistanceSolver._solve_l2(omega_arr, D_arr, tol)
        elif parsed_norm == MinkowskiNorm.L1:
            res = QuotientDistanceSolver._solve_l1(omega_arr, D_arr, tol)
        else:
            res = QuotientDistanceSolver._solve_linf(omega_arr, D_arr, tol)

        # Check if D has discarded nonzero singular directions:
        # A positive quotient distance depending on discarded singular directions
        # cannot be certified without verifying against the original D.
        if m > 0 and n_cols > 0 and not np.all(D_arr == 0):
            S = linalg.svdvals(D_arr)
            cutoff = QuotientDistanceSolver._svd_rank_cutoff(S, m, n_cols)
            has_discarded_directions = bool(np.any((S > 0) & (S <= cutoff)))
        else:
            has_discarded_directions = False

        if has_discarded_directions:
            # Attempt to resolve via exact rational repair on the original problem
            exact_alpha, exact_res = QuotientDistanceSolver.solve_exact(
                [Fraction(float(x)) for x in omega_arr],
                [[Fraction(float(x)) for x in row] for row in D_arr],
            )

            if exact_alpha is not None:
                try:
                    alpha_cand = np.array([float(a) for a in exact_alpha], dtype=float)
                    if np.all(np.isfinite(alpha_cand)):
                        r_cand = omega_arr - D_arr @ alpha_cand
                        if np.all(np.isfinite(r_cand)):
                            if parsed_norm == MinkowskiNorm.L1:
                                cand_dist = float(np.sum(np.abs(r_cand)))
                            elif parsed_norm == MinkowskiNorm.L2:
                                cand_dist = scaled_euclidean_norm(r_cand)
                            else:
                                cand_dist = float(np.max(np.abs(r_cand)))
                            if cand_dist <= tol:
                                return QuotientResult(
                                    norm=parsed_norm,
                                    primal_distance=cand_dist,
                                    optimal_alpha=alpha_cand,
                                    residual=r_cand,
                                    dual_witness=np.zeros_like(omega_arr),
                                    dual_objective=0.0,
                                    duality_gap=cand_dist,
                                    is_numerically_certified=True,
                                    is_approximate_zero=True,
                                )
                except (OverflowError, ValueError):
                    # Exact repair coefficients exceed floating-point range; caller should use solve_exact
                    pass

            # If exact repair did not find a validated zero repair, a positive distance
            # cannot be certified over discarded singular directions.
            return QuotientResult(
                norm=res.norm,
                primal_distance=res.primal_distance,
                optimal_alpha=res.optimal_alpha,
                residual=res.residual,
                dual_witness=res.dual_witness,
                dual_objective=res.dual_objective,
                duality_gap=res.duality_gap,
                is_numerically_certified=False,
                is_approximate_zero=res.is_approximate_zero,
            )

        return res

    @staticmethod
    def solve_exact(
        omega: Sequence[int | str | Fraction],
        D: Sequence[Sequence[int | str | Fraction]],
    ) -> tuple[tuple[Fraction, ...] | None, tuple[Fraction, ...]]:
        """Solve D alpha = omega exactly over Q via Gaussian elimination.

        Returns (alpha, residual) where residual = omega - D @ alpha.
        If no exact solution exists, returns (None, omega).
        """
        from code_exact_obstruction import solve_exact_repair
        return solve_exact_repair(D, omega)

    @staticmethod
    def _solve_l2(omega: np.ndarray, D: np.ndarray, tol: float) -> QuotientResult:
        """L2 closed-form projection via pseudoinverse/lstsq."""
        alpha, _, _, _ = linalg.lstsq(D, omega)
        residual = omega - D @ alpha
        dist = scaled_euclidean_norm(residual)

        s = float(np.max(np.abs(residual))) if len(residual) > 0 else 0.0
        if s == 0.0 or dist == 0.0:
            witness = np.zeros_like(omega)
            dual_obj = 0.0
            gap = 0.0
            is_certified = True
        else:
            raw_witness = residual / dist
            witness, is_ortho = QuotientDistanceSolver._project_dual_witness(D, raw_witness, MinkowskiNorm.L2, tol)
            dual_obj = float(np.dot(witness, omega))
            gap = abs(dist - dual_obj)
            is_certified = bool(
                is_ortho
                and gap <= tol
                and scaled_euclidean_norm(witness) <= 1.0 + tol
            )

        return QuotientResult(
            norm=MinkowskiNorm.L2,
            primal_distance=dist,
            optimal_alpha=alpha,
            residual=residual,
            dual_witness=witness,
            dual_objective=dual_obj,
            duality_gap=gap,
            is_numerically_certified=is_certified,
            is_approximate_zero=bool(dist < tol),
        )

    @staticmethod
    def _solve_l1(omega: np.ndarray, D: np.ndarray, tol: float) -> QuotientResult:
        """L1 minimization via HiGHS linear programming with column equilibration."""
        D_scaled, scales = QuotientDistanceSolver._equilibrate_columns(D)
        m, n = D.shape
        c = np.concatenate([np.zeros(n), np.ones(m)])

        A_top = np.hstack([D_scaled, -np.eye(m)])
        A_bot = np.hstack([-D_scaled, -np.eye(m)])
        A_ub = np.vstack([A_top, A_bot])
        b_ub = np.concatenate([omega, -omega])

        bounds = [(None, None)] * n + [(0, None)] * m

        res = optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"L1 linear programming failed: {res.message}")

        alpha_scaled = res.x[:n]
        alpha = alpha_scaled / scales
        residual = omega - D @ alpha
        dist = float(np.sum(np.abs(residual)))

        marginals = res.ineqlin.marginals
        lambda_top = marginals[:m]
        lambda_bot = marginals[m:]
        raw_witness = lambda_top - lambda_bot
        if dist > 1e-15 and np.max(np.abs(raw_witness)) < 1e-7:
            raw_witness = np.sign(residual)

        witness, is_ortho = QuotientDistanceSolver._project_dual_witness(D, raw_witness, MinkowskiNorm.L1, tol)
        dual_obj = float(np.dot(witness, omega))
        gap = abs(dist - dual_obj)
        is_certified = bool(
            is_ortho
            and gap <= tol
            and np.max(np.abs(witness)) <= 1.0 + tol
        )

        return QuotientResult(
            norm=MinkowskiNorm.L1,
            primal_distance=dist,
            optimal_alpha=alpha,
            residual=residual,
            dual_witness=witness,
            dual_objective=dual_obj,
            duality_gap=gap,
            is_numerically_certified=is_certified,
            is_approximate_zero=bool(dist < tol),
        )

    @staticmethod
    def _solve_linf(omega: np.ndarray, D: np.ndarray, tol: float) -> QuotientResult:
        """L_inf Chebyshev minimization via HiGHS linear programming with column equilibration."""
        D_scaled, scales = QuotientDistanceSolver._equilibrate_columns(D)
        m, n = D.shape
        c = np.concatenate([np.zeros(n), [1.0]])

        ones = np.ones((m, 1))
        A_top = np.hstack([D_scaled, -ones])
        A_bot = np.hstack([-D_scaled, -ones])
        A_ub = np.vstack([A_top, A_bot])
        b_ub = np.concatenate([omega, -omega])

        bounds = [(None, None)] * n + [(0, None)]

        res = optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"L_inf linear programming failed: {res.message}")

        alpha_scaled = res.x[:n]
        alpha = alpha_scaled / scales
        residual = omega - D @ alpha
        dist = float(np.max(np.abs(residual)))

        marginals = res.ineqlin.marginals
        lambda_top = marginals[:m]
        lambda_bot = marginals[m:]
        raw_witness = lambda_top - lambda_bot
        if dist > 1e-15 and np.max(np.abs(raw_witness)) < 1e-7:
            k = int(np.argmax(np.abs(residual)))
            raw_witness = np.zeros_like(residual)
            raw_witness[k] = np.sign(residual[k])

        witness, is_ortho = QuotientDistanceSolver._project_dual_witness(D, raw_witness, MinkowskiNorm.L_INF, tol)
        dual_obj = float(np.dot(witness, omega))
        gap = abs(dist - dual_obj)
        is_certified = bool(
            is_ortho
            and gap <= tol
            and np.sum(np.abs(witness)) <= 1.0 + tol
        )

        return QuotientResult(
            norm=MinkowskiNorm.L_INF,
            primal_distance=dist,
            optimal_alpha=alpha,
            residual=residual,
            dual_witness=witness,
            dual_objective=dual_obj,
            duality_gap=gap,
            is_numerically_certified=is_certified,
            is_approximate_zero=bool(dist < tol),
        )

    @staticmethod
    def verify_certificate(
        omega: np.ndarray,
        D: np.ndarray,
        result: QuotientResult,
        tol: float = 1e-7,
    ) -> bool:
        """Independently audit primal-dual certificates against mathematical optimality criteria."""
        if not (isinstance(tol, (int, float)) and np.isfinite(tol) and tol > 0):
            return False

        if not result.is_numerically_certified:
            return False

        if result.norm not in (MinkowskiNorm.L1, MinkowskiNorm.L2, MinkowskiNorm.L_INF):
            return False

        omega_arr = np.asarray(omega, dtype=float).ravel()
        D_arr = np.asarray(D, dtype=float)
        if D_arr.ndim == 1:
            D_arr = D_arr.reshape(len(omega_arr), 1)

        m = len(omega_arr)
        if D_arr.ndim != 2 or D_arr.shape[0] != m:
            return False

        n = D_arr.shape[1]
        if (
            result.optimal_alpha.shape != (n,)
            or result.residual.shape != (m,)
            or result.dual_witness.shape != (m,)
        ):
            return False

        # 0. Check finiteness of candidate certificate and input data
        if not (
            np.all(np.isfinite(omega_arr))
            and np.all(np.isfinite(D_arr))
            and np.isfinite(result.primal_distance)
            and np.isfinite(result.dual_objective)
            and np.isfinite(result.duality_gap)
            and np.all(np.isfinite(result.optimal_alpha))
            and np.all(np.isfinite(result.residual))
            and np.all(np.isfinite(result.dual_witness))
        ):
            return False

        # 1. Check residual computation strictly without broadcasting: r = omega - D alpha
        d_alpha = D_arr @ result.optimal_alpha
        if not np.all(np.isfinite(d_alpha)):
            return False
        expected_r = omega_arr - d_alpha
        residual_diff = np.abs(result.residual - expected_r)
        max_diff_r = float(np.max(residual_diff)) if residual_diff.size > 0 else 0.0
        if not (np.isfinite(max_diff_r) and max_diff_r <= tol):
            return False

        # 2. Check primal distance calculation
        try:
            if result.norm == MinkowskiNorm.L1:
                expected_dist = float(np.sum(np.abs(result.residual)))
                dual_norm_val = float(np.max(np.abs(result.dual_witness))) if m > 0 else 0.0
            elif result.norm == MinkowskiNorm.L2:
                expected_dist = scaled_euclidean_norm(result.residual)
                dual_norm_val = scaled_euclidean_norm(result.dual_witness)
            else:
                expected_dist = float(np.max(np.abs(result.residual))) if m > 0 else 0.0
                dual_norm_val = float(np.sum(np.abs(result.dual_witness)))
        except (ValueError, OverflowError):
            return False

        if not (np.isfinite(expected_dist) and np.isfinite(dual_norm_val)):
            return False

        dist_diff = abs(result.primal_distance - expected_dist)
        if not (np.isfinite(dist_diff) and dist_diff <= tol):
            return False

        # 3. Check dual witness norm <= 1
        if not (np.isfinite(dual_norm_val) and dual_norm_val <= 1.0 + tol):
            return False

        # 4. Check orthogonality against original problem D
        # If primal distance > tol, the dual witness must certify a lower bound over unbounded alpha.
        # This requires D^T W = 0 on the actual matrix D, not a rank-truncated approximation.
        if result.primal_distance > tol:
            if n > 0 and not np.all(D_arr == 0):
                pivot_cols = QuotientDistanceSolver._exact_pivot_columns(D_arr)
                D_check = D_arr[:, pivot_cols] if (len(pivot_cols) < n and len(pivot_cols) > 0) else D_arr
                S = linalg.svdvals(D_check)
                cutoff = QuotientDistanceSolver._svd_rank_cutoff(S, D_check.shape[0], D_check.shape[1])
                # If there are discarded nonzero singular directions, positive distance cannot be certified
                if np.any((S > 0) & (S <= cutoff)):
                    return False

        for j in range(n):
            col = D_arr[:, j]
            col_norm = scaled_euclidean_norm(col)
            if col_norm > 0.0:
                dot_val = float(col @ result.dual_witness)
                defect = abs(dot_val) / col_norm
                if not (np.isfinite(defect) and defect <= tol):
                    return False

        if n > 0 and not np.all(D_arr == 0):
            pivot_cols = QuotientDistanceSolver._exact_pivot_columns(D_arr)
            D_check = D_arr[:, pivot_cols] if (len(pivot_cols) < n and len(pivot_cols) > 0) else D_arr
            U, S, _ = linalg.svd(D_check, full_matrices=False)
            cutoff = QuotientDistanceSolver._svd_rank_cutoff(S, D_check.shape[0], D_check.shape[1])
            active_U = U[:, S > cutoff]
            if active_U.shape[1] > 0:
                u_dot_w = active_U.T @ result.dual_witness
                subspace_defect = scaled_euclidean_norm(u_dot_w)
                if not (np.isfinite(subspace_defect) and subspace_defect <= tol):
                    return False

        # 5. Check duality gap consistency and certified optimality
        expected_gap = abs(result.primal_distance - result.dual_objective)
        gap_diff = abs(result.duality_gap - expected_gap)
        if not (np.isfinite(gap_diff) and gap_diff <= tol):
            return False

        computed_dual_obj = float(np.dot(result.dual_witness, omega_arr))
        obj_diff = abs(computed_dual_obj - result.dual_objective)
        if not (np.isfinite(obj_diff) and obj_diff <= tol):
            return False

        primal_dual_diff = abs(result.primal_distance - computed_dual_obj)
        if not (np.isfinite(primal_dual_diff) and primal_dual_diff <= tol):
            return False

        return True
