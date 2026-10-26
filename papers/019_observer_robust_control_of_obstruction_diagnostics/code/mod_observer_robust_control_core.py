"""Reference implementation for finite-observer residual comparisons.

Implements:
- Observer specification: weights, projections, resolution tolerances, and coboundary maps
- Observer Bundle: collection of distinct observer models
- Observer-Robust Control Criterion: uniform descent, absolute curvature bounds, and R_cl stability
- Anti-spoofing filter: catches repairs that degrade unmonitored observers
- Minimax robust operator selection with multi-channel routing objective
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class ObserverModel:
    """Represents an evaluation observer with custom edge/face weights, tolerance, optional projection, and optional coboundary maps."""
    name: str
    weights: Tuple[float, ...]  # Edge / residual weights (C^1)
    boundary_weights: Optional[Tuple[float, ...]] = None  # Face / boundary weights (C^2)
    tolerance: float = 1e-9  # Observer resolution limit \varepsilon_{\mathcal{O}}
    d0: Optional[Tuple[Tuple[float, ...], ...]] = None  # Optional coboundary d_0: C^0 -> C^1
    d1: Optional[Tuple[Tuple[float, ...], ...]] = None  # Optional coboundary d_1: C^1 -> C^2
    projection_indices: Optional[Tuple[int, ...]] = None  # Optional coordinate projection \pi_{\mathcal{O}}: C^1(P) -> C^1(P_{\mathcal{O}})

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise ValueError("ObserverModel name must be a non-empty string")

        # 1. Weights: strictly positive and finite
        if not self.weights:
            raise ValueError(f"{self.name}: edge weights must be non-empty")
        for w in self.weights:
            if not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0.0:
                raise ValueError(f"{self.name}: all edge weights must be finite and strictly positive, got {w}")

        # 2. Boundary weights: strictly positive and finite if provided
        if self.boundary_weights is not None:
            if not self.boundary_weights:
                raise ValueError(f"{self.name}: boundary weights must be non-empty when specified")
            for w in self.boundary_weights:
                if not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0.0:
                    raise ValueError(f"{self.name}: all boundary weights must be finite and strictly positive, got {w}")

        # 3. Tolerance: finite and non-negative
        if not isinstance(self.tolerance, (int, float)) or not math.isfinite(self.tolerance) or self.tolerance < 0.0:
            raise ValueError(f"{self.name}: tolerance must be finite and non-negative, got {self.tolerance}")

        # 4. Coboundary d0: C^0 -> C^1 (matrix shape: m x n, where m == len(weights))
        if self.d0 is not None:
            if not self.d0:
                raise ValueError(f"{self.name}: d0 matrix must be non-empty when specified")
            m = len(self.d0)
            if m != len(self.weights):
                raise ValueError(f"{self.name}: d0 row count {m} != weights length {len(self.weights)}")
            n_cols = len(self.d0[0])
            if n_cols == 0:
                raise ValueError(f"{self.name}: d0 matrix must have at least one column (vertices)")
            for row_idx, row in enumerate(self.d0):
                if len(row) != n_cols:
                    raise ValueError(f"{self.name}: d0 row {row_idx} length {len(row)} != column count {n_cols}")
                for val in row:
                    if not isinstance(val, (int, float)) or not math.isfinite(val):
                        raise ValueError(f"{self.name}: d0 entries must be finite numbers, got {val}")

        # 5. Coboundary d1: C^1 -> C^2 (matrix shape: p x m, where m == len(weights))
        if self.d1 is not None:
            if not self.d1:
                raise ValueError(f"{self.name}: d1 matrix must be non-empty when specified")
            p = len(self.d1)
            for row_idx, row in enumerate(self.d1):
                if len(row) != len(self.weights):
                    raise ValueError(f"{self.name}: d1 row {row_idx} column count {len(row)} != weights length {len(self.weights)}")
                for val in row:
                    if not isinstance(val, (int, float)) or not math.isfinite(val):
                        raise ValueError(f"{self.name}: d1 entries must be finite numbers, got {val}")
            if self.boundary_weights is not None and len(self.boundary_weights) != p:
                raise ValueError(f"{self.name}: boundary weights length {len(self.boundary_weights)} != d1 face count {p}")

        # 6. Projection indices: tuple of non-negative integers matching len(weights)
        if self.projection_indices is not None:
            if not self.projection_indices:
                raise ValueError(f"{self.name}: projection_indices must be non-empty when specified")
            if len(self.projection_indices) != len(self.weights):
                raise ValueError(
                    f"{self.name}: projection_indices length {len(self.projection_indices)} != weights length {len(self.weights)}"
                )
            for idx in self.projection_indices:
                if not isinstance(idx, int) or idx < 0:
                    raise ValueError(f"{self.name}: projection index must be a non-negative integer, got {idx}")

    def project_cochain(self, vec: Sequence[float]) -> Sequence[float]:
        """Project carrier cochain onto this observer's monitored coordinates if projection_indices is declared."""
        if self.projection_indices is not None:
            if any(not isinstance(i, int) or i < 0 or i >= len(vec) for i in self.projection_indices):
                raise ValueError(
                    f"{self.name}: projection indices {self.projection_indices} out of range for vector of length {len(vec)}"
                )
            return tuple(vec[i] for i in self.projection_indices)
        return vec

    def _effective_boundary_weights(self) -> Tuple[float, ...]:
        if self.boundary_weights is not None:
            return self.boundary_weights
        if self.d1 is not None:
            return tuple(1.0 for _ in range(len(self.d1)))
        return self.weights

    def evaluate_phi_1(self, residual_vector: Sequence[float]) -> float:
        r"""
        Compute weighted l^1 quotient residual \Phi_1^{\mathcal{O}} under this observer.
        If d_0 is declared, minimizes over coboundaries \alpha \in C^0:
            \min_\alpha \|\pi_{\mathcal{O}}(\omega_1) - d_0 \alpha\|_{1, \mathcal{O}}.
        Otherwise, computes the weighted l^1 vector norm of the supplied residual
        (preconditioned on input being an externally certified optimal residual).
        """
        for x in residual_vector:
            if not isinstance(x, (int, float)) or not math.isfinite(x):
                return float("inf")

        if self.projection_indices is not None:
            omega_obs = self.project_cochain(residual_vector)
        else:
            omega_obs = residual_vector

        if len(omega_obs) != len(self.weights):
            raise ValueError(
                f"{self.name}: residual vector has {len(omega_obs)} coordinates (after projection) but the "
                f"observer declares {len(self.weights)} edge weights"
            )

        if self.d0 is not None:
            d0_mat = np.array(self.d0, dtype=float)
            w_arr = np.array(self.weights, dtype=float)
            omega = np.array(omega_obs, dtype=float)
            m, n = d0_mat.shape

            c = np.concatenate([np.zeros(n), w_arr])
            A_ub = np.vstack([
                np.hstack([-d0_mat, -np.eye(m)]),
                np.hstack([ d0_mat, -np.eye(m)])
            ])
            b_ub = np.concatenate([-omega, omega])
            bounds = [(None, None)] * n + [(0, None)] * m

            res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
            if res.success:
                return float(max(0.0, res.fun))
            raise RuntimeError(f"{self.name}: quotient LP minimization failed: {res.message}")

        return float(sum(w * abs(v) for w, v in zip(self.weights, omega_obs)))

    def evaluate_gamma_2(self, boundary_or_cochain: Sequence[float]) -> float:
        r"""
        Compute weighted 2-boundary curvature \Gamma_2^{\mathcal{O}} under this observer.
        If d_1 is declared and boundary_or_cochain has length matching C^1 (or carrier complex),
        evaluates \|d_1 \pi_{\mathcal{O}}(\omega_1)\|_{1, \mathcal{W}_2}.
        Otherwise, treats input as a 2-cochain / boundary vector in C^2.
        """
        for x in boundary_or_cochain:
            if not isinstance(x, (int, float)) or not math.isfinite(x):
                return float("inf")

        if self.d1 is not None:
            d1_mat = np.array(self.d1, dtype=float)
            b_weights = self.boundary_weights or tuple(1.0 for _ in range(d1_mat.shape[0]))
            w_arr = np.array(b_weights, dtype=float)

            if self.projection_indices is not None and len(boundary_or_cochain) > len(self.weights):
                omega_1 = np.array(self.project_cochain(boundary_or_cochain), dtype=float)
                boundary = d1_mat @ omega_1
                return float(np.sum(w_arr * np.abs(boundary)))
            elif len(boundary_or_cochain) == len(self.weights):
                omega_1 = np.array(boundary_or_cochain, dtype=float)
                boundary = d1_mat @ omega_1
                return float(np.sum(w_arr * np.abs(boundary)))

        b_weights = self._effective_boundary_weights()
        if len(boundary_or_cochain) != len(b_weights):
            raise ValueError(
                f"{self.name}: boundary vector has {len(boundary_or_cochain)} coordinates but the "
                f"observer declares {len(b_weights)} boundary weights"
            )
        return float(sum(w * abs(b) for w, b in zip(b_weights, boundary_or_cochain)))

    def evaluate_r_cl(self, residual_vector: Sequence[float], boundary_vector: Sequence[float]) -> float:
        r"""Compute piecewise closure ratio R_cl = \Gamma_2 / \Phi_1."""
        phi = self.evaluate_phi_1(residual_vector)
        gamma = self.evaluate_gamma_2(boundary_vector)
        if not math.isfinite(phi) or not math.isfinite(gamma):
            return float("inf")
        if phi > self.tolerance:
            return gamma / phi
        elif phi <= self.tolerance and gamma <= self.tolerance:
            return 0.0
        else:
            return float("inf")


@dataclass(frozen=True)
class ObserverBundle:
    """Bundle of admissible observers."""
    observers: Tuple[ObserverModel, ...]

    def __post_init__(self) -> None:
        if not self.observers:
            raise ValueError("ObserverBundle must contain at least one ObserverModel")

    @classmethod
    def create(cls, observers: Sequence[ObserverModel]) -> "ObserverBundle":
        if not observers:
            raise ValueError("ObserverBundle must contain at least one ObserverModel")
        return cls(observers=tuple(observers))


@dataclass
class RobustControlVerdict:
    """Outcome of observer-robust evaluation."""
    selected_operator: Optional[str]
    status: str  # "Admitted", "RejectedSpoofing", "RejectedDescentViolation", "RefusedStalled"
    worst_case_phi_1: float
    observer_diagnostics: Dict[str, Dict[str, float]]


class ObserverRobustController:
    """Selects repair operators enforcing uniform descent across all observers in the bundle."""

    def __init__(
        self,
        bundle: ObserverBundle,
        r_max: float = 1.0,
        m_max: float = float("inf"),
        gamma_max: float = float("inf"),
        delta_gamma_max: float = float("inf"),
        lam: float = 0.5,
        eps: float = 1e-9,
    ):
        if not isinstance(bundle, ObserverBundle):
            raise TypeError("bundle must be an instance of ObserverBundle")
        if not isinstance(r_max, (int, float)) or math.isnan(r_max) or r_max <= 0.0:
            raise ValueError(f"r_max must be positive and non-NaN, got {r_max}")
        if not isinstance(m_max, (int, float)) or math.isnan(m_max) or m_max <= 0.0:
            raise ValueError(f"m_max must be positive and non-NaN, got {m_max}")
        if not isinstance(gamma_max, (int, float)) or math.isnan(gamma_max) or gamma_max < 0.0:
            raise ValueError(f"gamma_max must be non-negative and non-NaN, got {gamma_max}")
        if not isinstance(delta_gamma_max, (int, float)) or math.isnan(delta_gamma_max) or delta_gamma_max < 0.0:
            raise ValueError(f"delta_gamma_max must be non-negative and non-NaN, got {delta_gamma_max}")
        if not isinstance(lam, (int, float)) or not math.isfinite(lam) or lam < 0.0:
            raise ValueError(f"lam must be finite and non-negative, got {lam}")
        if not isinstance(eps, (int, float)) or not math.isfinite(eps) or eps < 0.0:
            raise ValueError(f"eps must be finite and non-negative, got {eps}")

        self.bundle = bundle
        self.r_max = float(r_max)
        self.m_max = float(m_max)
        self.gamma_max = float(gamma_max)
        self.delta_gamma_max = float(delta_gamma_max)
        self.lam = float(lam)
        self.eps = float(eps)

    def evaluate_transition(
        self,
        curr_res: Sequence[float],
        curr_bnd: Sequence[float],
        candidate_transitions: Sequence[
            Tuple[str, Sequence[float], Sequence[float], float]
            | Tuple[str, Sequence[float], Sequence[float], float, float | Dict[str, float]]
        ]
    ) -> RobustControlVerdict:
        """Evaluate candidate transitions against the full observer bundle."""
        if not self.bundle.observers:
            return RobustControlVerdict(
                selected_operator=None,
                status="RefusedStalled",
                worst_case_phi_1=float("inf"),
                observer_diagnostics={},
            )

        for x in curr_res:
            if not isinstance(x, (int, float)) or not math.isfinite(x):
                raise ValueError(f"curr_res contains non-finite element: {x!r}")
        for x in curr_bnd:
            if not isinstance(x, (int, float)) or not math.isfinite(x):
                raise ValueError(f"curr_bnd contains non-finite element: {x!r}")

        surviving_candidates: List[Tuple[float, str, float, Dict[str, Dict[str, float]]]] = []

        for cand in candidate_transitions:
            if len(cand) == 4:
                op_name, next_res, next_bnd, cost = cand  # type: ignore[misc]
                phi_sat_in = None
            elif len(cand) == 5:
                op_name, next_res, next_bnd, cost, phi_sat_in = cand  # type: ignore[misc]
            else:
                continue

            if not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0.0:
                continue
            if any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in next_res):
                continue
            if any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in next_bnd):
                continue

            op_valid = True
            max_phi = 0.0
            obs_diag: Dict[str, Dict[str, float]] = {}

            for obs in self.bundle.observers:
                phi_curr = obs.evaluate_phi_1(curr_res)
                gamma_curr = obs.evaluate_gamma_2(curr_bnd)
                if not math.isfinite(phi_curr) or not math.isfinite(gamma_curr):
                    raise ValueError("Current observer diagnostics must be finite")
                phi_next = obs.evaluate_phi_1(next_res)
                gamma_next = obs.evaluate_gamma_2(next_bnd)
                rcl_next = obs.evaluate_r_cl(next_res, next_bnd)

                if not math.isfinite(phi_next) or not math.isfinite(gamma_next) or not math.isfinite(rcl_next):
                    op_valid = False
                    break

                # Resolve SAT channel input \Phi_{\mathrm{sat}}^{\mathcal{O}}
                if phi_sat_in is None:
                    phi_sat_val = min(phi_next, 1.0)
                elif isinstance(phi_sat_in, dict):
                    raw_sat = phi_sat_in.get(obs.name, min(phi_next, 1.0))
                    if not isinstance(raw_sat, (int, float)) or not math.isfinite(raw_sat) or raw_sat < 0.0:
                        op_valid = False
                        break
                    phi_sat_val = float(raw_sat)
                elif isinstance(phi_sat_in, (int, float)):
                    if not math.isfinite(phi_sat_in) or phi_sat_in < 0.0:
                        op_valid = False
                        break
                    phi_sat_val = float(phi_sat_in)
                else:
                    op_valid = False
                    break

                obs_diag[obs.name] = {
                    "phi_curr": phi_curr,
                    "phi_next": phi_next,
                    "gamma_curr": gamma_curr,
                    "gamma_next": gamma_next,
                    "rcl_next": rcl_next,
                    "phi_sat": phi_sat_val,
                }

                # Check 1: Per-observer uniform descent law: \Phi_1^{\mathcal{O}}(S_{t+1}) <= \Phi_1^{\mathcal{O}}(S_t) + \varepsilon_{\mathcal{O}}
                if phi_next > phi_curr + obs.tolerance:
                    op_valid = False
                    break

                # Check 2: Piecewise closure ratio guardrail: R_{cl}^{\mathcal{O}} <= R_{\max}
                if rcl_next > self.r_max + self.eps:
                    op_valid = False
                    break

                # Check 3: Absolute curvature stability guardrails (\Gamma_2 change and ceiling)
                if gamma_next > gamma_curr + self.delta_gamma_max + self.eps:
                    op_valid = False
                    break
                if gamma_next > self.gamma_max + self.eps:
                    op_valid = False
                    break

                if phi_next > max_phi:
                    max_phi = phi_next

            # Check 4: Worst-case residual boundedness: \sup_{\mathcal{O}} \Phi_1^{\mathcal{O}} <= M_{\max}
            if max_phi > self.m_max + self.eps:
                op_valid = False

            if op_valid:
                # Score implements Section 4 routing objective:
                # \mathcal{L}(o, S_t) = \sup_{\mathcal{O}} \Phi_1^{\mathcal{O}} + \lambda (1/|\mathfrak{O}|) \sum (\Phi_{\mathrm{sat}}^{\mathcal{O}} + R_{cl}^{\mathcal{O}}) + \operatorname{Cost}(o)
                avg_diagnostic = sum(
                    d["phi_sat"] + d["rcl_next"] for d in obs_diag.values()
                ) / max(1, len(self.bundle.observers))
                score = max_phi + self.lam * avg_diagnostic + float(cost)
                if not math.isfinite(score):
                    continue
                surviving_candidates.append((score, op_name, max_phi, obs_diag))

        if not surviving_candidates:
            return RobustControlVerdict(
                selected_operator=None,
                status="RefusedStalled",
                worst_case_phi_1=float("inf"),
                observer_diagnostics={},
            )

        surviving_candidates.sort(key=lambda x: x[0])
        best_score, best_op, best_max_phi, best_diag = surviving_candidates[0]

        return RobustControlVerdict(
            selected_operator=best_op,
            status="Admitted",
            worst_case_phi_1=best_max_phi,
            observer_diagnostics=best_diag,
        )
