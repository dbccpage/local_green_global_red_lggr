"""Reference implementation for the Conditional Density Lift and Dual-Witness Xi Functional.

Provides:
- Conditional density lift: v -> psi(v), rho(v)
- Pure-state trace distance calculation
- Xi functional diagnostic calculation with declared zero-obstruction convention
- Evaluator tiered priority admission logic
- Zero-obstruction certificate validation
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

import numpy as np


@dataclass(frozen=True)
class ZeroObstructionCertificate:
    """Certificate validating that a cochain is an exact coboundary (omega = B @ alpha).

    An exact coboundary has zero quotient obstruction (Phi_1 = 0).
    """
    boundary_matrix: np.ndarray
    potential: np.ndarray  # alpha such that B @ alpha == omega
    cochain: np.ndarray    # omega
    tolerance: float = 1e-9

    def verify(self) -> bool:
        """Check equality over the exact rational values of finite binary inputs.

        The legacy tolerance argument cannot relax an exact zero certificate.
        """
        B = np.asarray(self.boundary_matrix, dtype=float)
        alpha = np.asarray(self.potential, dtype=float)
        omega = np.asarray(self.cochain, dtype=float)
        if B.ndim != 2 or alpha.ndim != 1 or omega.ndim != 1:
            return False
        if B.shape[0] != omega.shape[0] or B.shape[1] != alpha.shape[0]:
            return False
        if not np.all(np.isfinite(B)) or not np.all(np.isfinite(alpha)) or not np.all(np.isfinite(omega)):
            return False
        for row, target in zip(B, omega):
            value = sum((Fraction(float(a)) * Fraction(float(x)) for a, x in zip(row, alpha)), Fraction(0))
            if value != Fraction(float(target)):
                return False
        return True


@dataclass(frozen=True)
class DensityLift:
    """Represents a normalized rank-1 density operator constructed from a finite cochain.

    Coordinate signs of v are preserved in state_vector psi(v). The density matrix
    rho(v) = |psi><psi| is invariant under global sign inversion (rho(-v) = rho(v)).
    Total l1 mass ||v||_1 is recorded as metadata and discarded in rho(v).
    """
    state_vector: np.ndarray  # 1D array of floats, ||psi||_2 = 1
    total_mass: float         # ||v||_1 > 0

    def __post_init__(self) -> None:
        arr = np.ascontiguousarray(np.asarray(self.state_vector, dtype=np.float64))
        if arr.ndim != 1:
            raise ValueError("state_vector must be one-dimensional")
        if len(arr) == 0:
            raise ValueError("state_vector must not be empty")
        if not np.all(np.isfinite(arr)):
            raise ValueError("state_vector must be finite")
        norm = float(np.linalg.norm(arr))
        if not math.isclose(norm, 1.0, rel_tol=1e-7, abs_tol=1e-7):
            raise ValueError(f"state_vector must have unit 2-norm, got {norm}")
        arr = arr + 0.0  # canonicalise -0.0 to +0.0 so equal states hash equally
        arr.flags.writeable = False
        object.__setattr__(self, "state_vector", arr)

        mass = float(self.total_mass)
        if not math.isfinite(mass) or mass <= 0.0:
            raise ValueError(f"total_mass must be positive and finite, got {mass}")
        object.__setattr__(self, "total_mass", mass)

    def __eq__(self, other: object) -> bool:
        assert type(self) is type(other)
        assert isinstance(other, DensityLift)
        return np.array_equal(self.state_vector, other.state_vector) and self.total_mass == other.total_mass

    def __hash__(self) -> int:
        return hash((type(self), self.state_vector.tobytes(), self.total_mass))

    @property
    def density_matrix(self) -> np.ndarray:
        """Construct the outer product rho = |psi><psi|."""
        return np.outer(self.state_vector, self.state_vector)


class ConditionalDensityLift:
    """Computes normalized, scale-invariant density lifts and trace metrics."""

    @staticmethod
    def lift(vector: List[float], tolerance: float = 0.0) -> DensityLift:
        """Compute the normalized state vector psi(v)_e = sign(v_e) * sqrt(|v_e| / ||v||_1).

        Preserves normalized absolute coordinate weights; total mass is discarded in the projection.
        Default tolerance=0.0 allows lifting any non-zero vector down to floating-point underflow limits.
        Rejects nonfinite data (NaN, Inf) and empty inputs.
        Scales by the maximum coordinate before summing to protect against overflow/underflow.
        """
        arr = np.asarray(vector, dtype=np.float64)
        if arr.ndim != 1 or len(arr) == 0:
            raise ValueError("Input vector must be a non-empty 1D sequence.")
        if not np.all(np.isfinite(arr)):
            raise ValueError("Input vector contains non-finite values (NaN or Inf).")

        abs_arr = np.abs(arr)
        max_val = float(np.max(abs_arr))
        if max_val == 0.0:
            raise ValueError("Density lift undefined for zero-mass vector (max coordinate = 0.0).")

        # Scale by largest coordinate before summing to protect against overflow
        scaled_arr = abs_arr / max_val
        scaled_sum = float(np.sum(scaled_arr))

        # The normalized state can exist even when its mass cannot be stored.
        # Refuse that representation instead of recording a clipped mass.
        raw_mass = max_val * scaled_sum
        if math.isfinite(raw_mass):
            mass = float(raw_mass)
        else:
            raise FloatingPointError("Total l1 mass is not representable as a finite float")

        if mass <= tolerance:
            raise ValueError(f"Density lift undefined for zero-mass vector (mass={mass} <= tolerance={tolerance}).")

        # Normalized coordinate weights: (|v_e| / mass) == (scaled_arr / scaled_sum)
        weights = scaled_arr / scaled_sum
        magnitudes = np.sqrt(weights)
        signs = np.where(arr >= 0.0, 1.0, -1.0)
        state_vec = signs * magnitudes

        # Ensure exact unit 2-norm within numerical precision
        norm = float(np.linalg.norm(state_vec))
        if norm > 0.0:
            state_vec = state_vec / norm

        return DensityLift(state_vector=state_vec, total_mass=mass)

    @staticmethod
    def trace_distance(lift_a: DensityLift, lift_b: DensityLift) -> float:
        """Compute the normalized trace distance between two pure states.

        For rank-1 states, D(rho_a, rho_b) = sqrt(1 - |<psi_a | psi_b>|^2).
        """
        if len(lift_a.state_vector) != len(lift_b.state_vector):
            raise ValueError("State vector dimension mismatch.")

        # For real unit vectors, ||a-b|| ||a+b|| / 2 equals sqrt(1-<a,b>^2).
        # This avoids cancellation near equal rays without imposing a zero tolerance.
        difference = float(np.linalg.norm(lift_a.state_vector - lift_b.state_vector))
        total = float(np.linalg.norm(lift_a.state_vector + lift_b.state_vector))
        return min(1.0, difference * total / 2.0)

    @classmethod
    def compute_xi(
        cls,
        primal_residual: List[float],
        dual_witness: List[float],
        tolerance: float = 0.0,
        zero_certificate: ZeroObstructionCertificate | None = None,
        unverified_override: bool = False,
    ) -> float:
        """Compute the Xi functional between primal residual and dual witness.

        For Phi_1 > 0 (nonzero primal residual mass > tolerance):
        Computes the trace distance between the normalized density lifts of the
        canonical primal residual and dual witness:
            Xi = sqrt(1 - |<psi(h*) | psi(phi*)>|^2)

        For Phi_1 = 0 (exact cochain, zero primal residual mass == 0.0 or verified certificate):
        By declared convention (Definition 4.1 in monograph), Xi is defined strictly as 0.0,
        indicating the complete absence of obstruction distortion.

        Certificate / Override Separation:
        - An unverified caller assertion does not constitute a certificate. When
          primal_residual is non-zero or in the tolerance window, an independently
          checked ZeroObstructionCertificate must be provided to certify zero obstruction.
        - Passing zero_certificate=... executes an independent verification of the coboundary
          equation B @ alpha == omega. If verification fails, a ValueError is raised.
        - Explicitly unverified overrides must be requested via unverified_override=True.

        Numerical Uncertainty:
        When tolerance > 0 and 0.0 < mass_primal <= tolerance without a verified zero
        certificate or explicit unverified override, a ValueError is raised to treat numerical
        uncertainty as an explicit condition rather than silently erasing a positive obstruction.

        Note:
        This function accepts externally supplied cochain vectors (e.g. from an
        upstream LP solver using successive coordinate minimization). It does not
        itself compute or validate canonical optimality.
        """
        arr_primal = np.asarray(primal_residual, dtype=np.float64)
        if not np.all(np.isfinite(arr_primal)):
            raise ValueError("primal_residual must contain only finite numbers.")

        abs_primal = np.abs(arr_primal)
        max_p = float(np.max(abs_primal)) if len(abs_primal) > 0 else 0.0
        mass_primal = float(max_p * np.sum(abs_primal / max_p)) if max_p > 0.0 else 0.0

        # Check independently verified zero certificate if supplied
        if zero_certificate is not None:
            if not zero_certificate.verify():
                raise ValueError("Zero obstruction certificate verification failed: cochain is not an exact coboundary.")
            certified = np.asarray(zero_certificate.cochain, dtype=float)
            if certified.shape != arr_primal.shape or not np.array_equal(certified, arr_primal):
                raise ValueError("Zero obstruction certificate cochain does not match the supplied input")
            return 0.0

        # Explicitly unverified caller override
        if unverified_override:
            return 0.0

        # 1. Zero-obstruction convention on genuine zero vector
        if mass_primal == 0.0:
            return 0.0

        # 2. Numerical uncertainty: positive mass <= tolerance when tolerance > 0
        if mass_primal <= tolerance:
            raise ValueError(
                f"Numerical uncertainty: residual mass {mass_primal} <= tolerance {tolerance} "
                f"without verified zero certificate. Provide a verified zero_certificate, "
                f"or set unverified_override=True for an unverified override, "
                f"or set tolerance=0.0 to compute the non-zero density lift."
            )

        lift_primal = cls.lift(primal_residual, tolerance=tolerance)
        lift_dual = cls.lift(dual_witness, tolerance=tolerance)
        return cls.trace_distance(lift_primal, lift_dual)

    @staticmethod
    def normalized_abs_weights(vector: list[int]) -> tuple[Fraction, ...]:
        """Rational absolute weights |v_e| / ||v||_1. Their sum is 1 when the mass is positive."""
        coords = _integer_coordinates(vector)
        if not coords:
            raise ValueError("Input vector must be a non-empty 1D sequence.")
        mass = sum(abs(x) for x in coords)
        if mass == 0:
            raise ValueError("Density lift undefined for zero-mass vector.")
        return tuple(Fraction(abs(x), mass) for x in coords)

    @staticmethod
    def integer_cauchy_gap(left: list[int], right: list[int]) -> int:
        """Return (sum a_i^2)(sum b_i^2) - (sum a_i b_i)^2 for equal-length integer vectors."""
        if len(left) != len(right):
            raise ValueError("State vector dimension mismatch.")
        left_i = _integer_coordinates(left)
        right_i = _integer_coordinates(right)
        sum_left = sum(x * x for x in left_i)
        sum_right = sum(y * y for y in right_i)
        paired = sum(x * y for x, y in zip(left_i, right_i))
        return sum_left * sum_right - paired * paired

    @staticmethod
    def pairing_slack(dual: list[int], primal: list[int]) -> int:
        """Return sum (|h_e| - phi_e h_e). Each term is nonnegative when |phi_e| <= 1."""
        if len(dual) != len(primal):
            raise ValueError("State vector dimension mismatch.")
        dual_i = _integer_coordinates(dual)
        primal_i = _integer_coordinates(primal)
        if any(abs(p) > 1 for p in dual_i):
            raise ValueError("Dual coordinate is outside the unit infinity ball.")
        return sum(abs(x) - p * x for p, x in zip(dual_i, primal_i))

    @staticmethod
    def dual_mass_if_slack_vanishes(dual: list[int], primal: list[int]) -> int:
        """Return ||phi||_1 when the integer slack vanishes and the primal mass is positive."""
        slack = ConditionalDensityLift.pairing_slack(dual, primal)
        primal_i = _integer_coordinates(primal)
        dual_i = _integer_coordinates(dual)
        if slack != 0 or sum(abs(x) for x in primal_i) == 0:
            raise ValueError("Dual-mass bound requires vanishing slack and positive primal mass.")
        return sum(abs(p) for p in dual_i)


def _integer_coordinates(vector: List[int]) -> List[int]:
    if any(type(value) is not int for value in vector):
        raise TypeError("Exact coordinate routines require integer inputs without coercion")
    return list(vector)


class GuardedEvaluator:
    """Implements tiered priority admission with threshold gating and strict non-increase fences.

    Hierarchy:
    1. Primary: Phi_1 quotient residual reduction.
    2. Secondary: Gamma_2 curvature reduction when Phi_1 is non-increasing within tolerance.
    3. Tertiary: Xi tie-breaking when both Phi_1 and Gamma_2 are non-increasing within tolerance,
       subject to the boundary ratio guardrail R_cl <= r_max.

    Strict Non-Increase Fences:
    - Phi_1 may NEVER increase: any candidate with phi_cand > phi_curr is rejected immediately.
    - Gamma_2 may NEVER increase on tie-break: any candidate with gamma_cand > gamma_curr is rejected.
    """

    @staticmethod
    def is_admissible_transition(
        state_current: Tuple[float, float, float, float],
        state_candidate: Tuple[float, float, float, float],
        r_max: float = 1.0,
        eps: float = 1e-9,
    ) -> Tuple[bool, str]:
        """Evaluate admissibility of transition. State tuple is (phi_1, gamma_2, r_cl, xi).

        Validates all diagnostics and threshold parameters before evaluating any branch:
        - All diagnostics must be finite, non-negative numbers.
        - Xi must satisfy 0.0 <= xi <= 1.0.
        - r_max must be finite and strictly positive (r_max > 0).
        - eps must be finite and non-negative (eps >= 0).

        Invalid states (e.g. containing NaN, Inf, or negative values) are rejected immediately.

        Numerical policy with strict non-increase:
        - If phi_cand < phi_curr - eps: accepted (primary decrease).
        - If phi_cand > phi_curr: rejected (primary increase strictly forbidden, even for delta < eps).
        - When phi_curr - eps <= phi_cand <= phi_curr (literal non-increase within eps):
          - If gamma_cand < gamma_curr - eps: accepted (secondary decrease).
          - If gamma_cand > gamma_curr: rejected (secondary increase strictly forbidden).
          - When gamma_curr - eps <= gamma_cand <= gamma_curr:
            - If rcl_cand > r_max: rejected (guardrail violation).
            - If xi_cand < xi_curr - eps: accepted (tertiary tie-breaker decrease).
            - Otherwise: rejected (no improvement).
        """
        # Threshold validation
        if not math.isfinite(r_max) or r_max <= 0.0:
            raise ValueError(f"Evaluator threshold r_max must be positive and finite, got {r_max}")
        if not math.isfinite(eps) or eps < 0.0:
            raise ValueError(f"Evaluator tolerance eps must be non-negative and finite, got {eps}")

        def validate_state(s: Tuple[float, float, float, float], label: str) -> Tuple[bool, str]:
            if not isinstance(s, (tuple, list)) or len(s) != 4:
                return False, f"{label} state must be a 4-tuple (phi_1, gamma_2, r_cl, xi)."
            phi, gamma, rcl, xi = s
            names = ["phi_1", "gamma_2", "r_cl", "xi"]
            vals = [phi, gamma, rcl, xi]
            for n, v in zip(names, vals):
                if not isinstance(v, (int, float)) or not math.isfinite(v):
                    return False, f"{label} diagnostic {n} is non-finite or invalid ({v})."
                if v < 0.0:
                    return False, f"{label} diagnostic {n} is negative ({v})."
            if xi > 1.0 + 1e-7:
                return False, f"{label} diagnostic xi exceeds 1.0 ({xi})."
            return True, ""

        valid_curr, err_curr = validate_state(state_current, "Current")
        if not valid_curr:
            return False, f"Rejected: {err_curr}"

        valid_cand, err_cand = validate_state(state_candidate, "Candidate")
        if not valid_cand:
            return False, f"Rejected: {err_cand}"

        phi_curr, gamma_curr, rcl_curr, xi_curr = state_current
        phi_cand, gamma_cand, rcl_cand, xi_cand = state_candidate

        # 1. Primary: Phi_1 reduction with strict non-increase fence
        if phi_cand < phi_curr - eps:
            return True, "Accepted: Primary quotient residual Phi_1 decreased."
        if phi_cand > phi_curr:
            return False, "Rejected: Primary quotient residual Phi_1 increased."

        # 2. Secondary: Gamma_2 reduction when Phi_1 is non-increasing within eps
        if gamma_cand < gamma_curr - eps:
            return True, "Accepted: Closure curvature Gamma_2 decreased with non-increasing Phi_1."
        if gamma_cand > gamma_curr:
            return False, "Rejected: Closure curvature Gamma_2 increased with non-increasing Phi_1."

        # 3. Guardrail: R_cl must not exceed r_max (evaluated at Xi tie-break stage)
        if rcl_cand > r_max:
            return False, f"Rejected: Boundary ratio R_cl exceeds threshold ({rcl_cand} > {r_max})."

        # 4. Tertiary: Xi tie-breaking when Phi_1 and Gamma_2 non-increasing within eps
        if xi_cand < xi_curr - eps:
            return True, "Accepted: Representative distortion Xi decreased on tie-break."

        return False, "Rejected: No improvement across diagnostic hierarchy."

    @staticmethod
    def exact_admissible(
        state_current: Tuple[Fraction, Fraction, Fraction, Fraction],
        state_candidate: Tuple[Fraction, Fraction, Fraction, Fraction],
        r_max: Fraction,
        eps: Fraction,
    ) -> bool:
        """Exact rational form of the tiered admission policy."""
        current = tuple(Fraction(v) for v in state_current)
        candidate = tuple(Fraction(v) for v in state_candidate)
        if len(current) != 4 or len(candidate) != 4:
            raise ValueError("State must be a 4-tuple (phi_1, gamma_2, r_cl, xi).")
        r_max = Fraction(r_max)
        eps = Fraction(eps)
        if r_max <= 0 or eps < 0:
            raise ValueError("Evaluator thresholds are invalid.")
        for value in (*current, *candidate):
            if value < 0:
                raise ValueError("Diagnostic is negative.")
        if current[3] > 1 or candidate[3] > 1:
            raise ValueError("Xi exceeds 1.")
        phi, gamma, _rcl, xi = current
        phi2, gamma2, rcl2, xi2 = candidate
        if phi2 < phi - eps:
            return True
        if phi2 > phi:
            return False
        if gamma2 < gamma - eps:
            return True
        if gamma2 > gamma:
            return False
        if rcl2 > r_max:
            return False
        return xi2 < xi - eps
