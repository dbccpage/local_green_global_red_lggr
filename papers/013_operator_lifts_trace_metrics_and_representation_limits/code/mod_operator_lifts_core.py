r"""Reference implementation for Operator Lifts, Trace Metrics, and Representation Limits.

Implements:
- Linear trace-class embedding F_lin: v -> T(v)
- Nonlinear density lift F_den: v -> rho(v) via the classical Mazur map M_{1,2}
- Proof of Lossy Collision Principle: rho(c * v) == rho(v) for all c != 0
- Fiber characterization: Preimage F_den^-1(rho(v)) = {c * v : c in R \ {0}}
- Reconstruction obstruction: recovery requires extrinsic mass M(v) and yields candidate pair {v, -v}
- Local reconstruction charts and orientation functional condition ell(v) != 0
- Trace distance Xi as pseudometric on nonzero cochains and metric on the projective quotient
- Guarded descent evaluator enforcing the declared selection priority on discrete cell complexes
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np


@dataclass(frozen=True)
class LinearTraceOperator:
    """Diagonal trace-class operator representation of a finite real cochain."""
    _diagonal: np.ndarray

    def __init__(self, diagonal: np.ndarray | Sequence[float]) -> None:
        arr = np.ascontiguousarray(np.asarray(diagonal, dtype=np.float64))
        if arr.ndim != 1:
            raise ValueError("diagonal must be one-dimensional")
        if not np.all(np.isfinite(arr)):
            raise ValueError("diagonal must be finite")
        arr = arr + 0.0  # canonicalise -0.0 to +0.0
        arr.flags.writeable = False
        object.__setattr__(self, "_diagonal", arr)

    @property
    def diagonal(self) -> np.ndarray:
        """Read-only copy of diagonal vector, protected against post-construction mutation."""
        view = self._diagonal.copy()
        view.flags.writeable = False
        return view

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other) or not isinstance(other, LinearTraceOperator):
            return False
        return bool(np.array_equal(self._diagonal, other._diagonal))

    def __hash__(self) -> int:
        return hash((type(self), self._diagonal.tobytes()))

    @property
    def trace_norm(self) -> float:
        """Trace norm ||T||_tr = sum |lambda_i|."""
        return float(np.sum(np.abs(self._diagonal)))


@dataclass(frozen=True)
class DensityOperator:
    r"""Rank-1 density operator representation on finite real cochains.

    Represents rho = |psi><psi| where ||psi||_2 = 1.
    The factor psi is defined by the classical Mazur map M_{1,2}:
        psi(v)_i = sgn(v_i) * sqrt(|v_i| / ||v||_1)
    mapping the unit l^1 sphere homeomorphically onto the unit l^2 sphere.
    The internal state vector is canonicalized to positive initial gauge
    so that antipodal unit vectors psi and -psi yield the identical operator,
    matching density matrix equality rho(psi) == rho(-psi).
    """
    _state_vector: np.ndarray

    def __init__(self, state_vector: np.ndarray | Sequence[float]) -> None:
        arr = np.ascontiguousarray(np.asarray(state_vector, dtype=np.float64))
        if arr.ndim != 1:
            raise ValueError("state_vector must be one-dimensional")
        if not np.all(np.isfinite(arr)):
            raise ValueError("state_vector must contain only finite numbers")

        trace_val = float(np.sum(arr ** 2))
        if not math.isclose(trace_val, 1.0, abs_tol=1e-7):
            raise ValueError(f"state_vector must have unit L2 norm (trace = 1); got trace = {trace_val}")

        # Normalize accepted near-unit inputs to exact unit norm for pure-state distance identities
        arr = arr / math.sqrt(trace_val)

        # Gauge canonicalization: first coordinate above tolerance is strictly positive
        nonzero_idx = np.where(np.abs(arr) > 1e-15)[0]
        if len(nonzero_idx) > 0 and arr[nonzero_idx[0]] < 0.0:
            arr = -arr

        # Canonicalize -0.0 to +0.0 AFTER gauge canonicalization so that antipodal
        # inputs with zero coordinates compare equal, hash equally, and deduplicate in sets.
        arr[arr == 0.0] = 0.0

        arr.flags.writeable = False
        object.__setattr__(self, "_state_vector", arr)

    @property
    def state_vector(self) -> np.ndarray:
        """Read-only copy of canonical unit state vector."""
        view = self._state_vector.copy()
        view.flags.writeable = False
        return view

    @property
    def density_matrix(self) -> np.ndarray:
        """Full rank-1 density operator matrix rho = |psi><psi|."""
        mat = np.outer(self._state_vector, self._state_vector)
        mat.flags.writeable = False
        return mat

    @property
    def trace(self) -> float:
        """Trace of density operator, identically 1.0 for valid states."""
        return 1.0

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other) or not isinstance(other, DensityOperator):
            return False
        return bool(np.array_equal(self._state_vector, other._state_vector))

    def __hash__(self) -> int:
        return hash((type(self), self._state_vector.tobytes()))


class OperatorLifts:
    """Implements F_lin and F_den embeddings, reconstruction analysis, and trace distance."""

    @staticmethod
    def linear_embedding(vector: Sequence[float]) -> LinearTraceOperator:
        """Embed real vector v into diagonal trace-class operator T(v). Preserves l^1 norm."""
        arr = np.array(vector, dtype=float)
        return LinearTraceOperator(diagonal=arr)

    @staticmethod
    def density_lift(vector: Sequence[float]) -> DensityOperator:
        r"""Embed nonzero real vector v into rank-1 density operator rho(v).

        Discards scalar magnitude and unoriented line sign.
        Uses the classical Mazur map M_{1,2} on scale-normalized coordinates
        to prevent floating-point overflow on large inputs (e.g. 1e308)
        and admits any nonzero cochain down to float underflow limits.
        """
        arr = np.ascontiguousarray(np.asarray(vector, dtype=np.float64))
        if arr.ndim != 1:
            raise ValueError("cochain vector must be one-dimensional")
        if not np.all(np.isfinite(arr)):
            raise ValueError("cochain vector must contain only finite numbers")

        max_abs = float(np.max(np.abs(arr)))
        if max_abs == 0.0:
            raise ValueError("Density lift undefined for zero-mass cochains.")

        # Scale by max_abs to prevent intermediate sum overflow
        scaled = arr / max_abs
        scaled_mass = float(np.sum(np.abs(scaled)))
        magnitudes = np.sqrt(np.abs(scaled) / scaled_mass)
        signs = np.where(scaled >= 0.0, 1.0, -1.0)
        psi = signs * magnitudes
        return DensityOperator(state_vector=psi)

    @classmethod
    def attempt_reconstruction(
        cls,
        density: Union[DensityOperator, np.ndarray, Sequence[Sequence[float]]],
        admitted_mass: Optional[float] = None,
        orientation_anchor: Optional[Union[int, float, Sequence[float], np.ndarray]] = None,
    ) -> Tuple[bool, Optional[Union[Tuple[np.ndarray, np.ndarray], np.ndarray]], str]:
        r"""Attempt to reconstruct original cochain from density operator rho.

        The complete preimage fiber is F_den^-1(rho(v)) = {c * v : c in R \ {0}}.
        - Without extrinsic mass M(v): reconstruction fails completely.
        - With admitted mass M(v) > 0 but no orientation anchor: returns candidate pair {v, -v}.
        - With admitted mass M(v) > 0 and orientation anchor (sign +1/-1 or reference vector): returns single cochain.

        Domain requirements for density matrix:
        - Real symmetric (rho^T == rho)
        - Idempotent rank-1 projector (rho^2 == rho)
        - Unit trace (Tr(rho) == 1)
        - All entries finite
        Mixed states (e.g. 0.5 * I_2) are strictly rejected as outside the rank-1 image of F_den.

        Reference anchor requirements:
        - Must contain only finite numbers (no NaN or Inf).
        - Orientation functional ell must not vanish on candidates: |<a, v>| > 0.
          Orthogonal anchors cannot distinguish antipodes and return an unresolved result.
        """
        if admitted_mass is None:
            return (
                False,
                None,
                "Obstruction: Cannot reconstruct cochain without extrinsic mass M(v) (Lossy Collision Principle). Fiber is unoriented line {c * v : c != 0}.",
            )

        if not (isinstance(admitted_mass, (int, float)) and math.isfinite(admitted_mass) and admitted_mass > 0.0):
            raise ValueError(f"Invalid admitted_mass: must be finite and strictly positive (got {admitted_mass}).")

        # Extract and validate density matrix rho
        if isinstance(density, DensityOperator):
            mat = density.density_matrix
        else:
            mat = np.ascontiguousarray(np.asarray(density, dtype=np.float64))

        if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
            raise ValueError("Density matrix must be square 2D array.")
        if not np.all(np.isfinite(mat)):
            raise ValueError("Density matrix must contain only finite numbers.")

        # Domain verification: rho^T == rho, Tr(rho) == 1, rho^2 == rho
        if not np.allclose(mat, mat.T, atol=1e-8):
            return False, None, "Domain error: Density matrix must be symmetric (rho^T == rho)."

        tr = float(np.trace(mat))
        if not math.isclose(tr, 1.0, abs_tol=1e-6):
            return False, None, f"Domain error: Density matrix must have unit trace (Tr(rho) == 1, got {tr:.7f})."

        mat_sq = mat @ mat
        if not np.allclose(mat_sq, mat, atol=1e-6):
            return (
                False,
                None,
                "Domain error: Density matrix must be idempotent (rho^2 == rho; rank-1 orthogonal projector). Mixed states are outside the rank-1 image of F_den.",
            )

        diag = np.diag(mat)
        nonzero_diag = np.where(diag > 1e-15)[0]
        if len(nonzero_diag) == 0:
            return False, None, "Domain error: Density matrix has zero diagonal; cannot reconstruct."

        # Reconstruct unit vector factor purely from density matrix row
        k = nonzero_diag[0]
        mag_k = math.sqrt(diag[k])
        row_k = mat[k, :]
        psi_recon = row_k / mag_k

        # Candidate pair {v_pos, v_neg} with admitted mass
        v_pos = psi_recon * np.abs(psi_recon) * float(admitted_mass)
        v_neg = -v_pos

        # Postcondition checks: mass and re-lift agreement
        recon_mass = float(np.sum(np.abs(v_pos)))
        if not math.isclose(recon_mass, float(admitted_mass), rel_tol=1e-5, abs_tol=1e-7):
            return (
                False,
                None,
                f"Postcondition error: Reconstructed cochain mass ({recon_mass}) does not match admitted mass ({admitted_mass}).",
            )

        rho_check = OperatorLifts.density_lift(v_pos)
        if not np.allclose(rho_check.density_matrix, mat, atol=1e-6):
            return False, None, "Postcondition error: Re-lifted candidate density matrix does not match input matrix."

        if orientation_anchor is None:
            return (
                True,
                (v_pos, v_neg),
                "Success: Reconstructed candidate pair {v, -v} from density operator and admitted mass.",
            )

        if isinstance(orientation_anchor, (int, float)):
            if not math.isfinite(orientation_anchor):
                return False, None, "Invalid orientation anchor: scalar anchor must be finite."
            if orientation_anchor > 0:
                return (
                    True,
                    v_pos,
                    "Success: Reconstructed cochain with admitted mass and positive orientation anchor relative to canonical gauge convention.",
                )
            elif orientation_anchor < 0:
                return (
                    True,
                    v_neg,
                    "Success: Reconstructed cochain with admitted mass and negative orientation anchor relative to canonical gauge convention.",
                )
            else:
                return False, None, "Invalid orientation anchor: scalar anchor must be non-zero (+1 or -1)."

        # Reference vector anchor: choose candidate with positive inner product
        anchor_arr = np.ascontiguousarray(np.asarray(orientation_anchor, dtype=np.float64))
        if not np.all(np.isfinite(anchor_arr)):
            return False, None, "Invalid orientation anchor: reference anchor must contain only finite numbers (no NaN or Inf)."
        if anchor_arr.shape != v_pos.shape:
            return False, None, f"Orientation anchor shape {anchor_arr.shape} does not match cochain shape {v_pos.shape}."

        dot_pos = float(np.dot(anchor_arr, v_pos))
        if abs(dot_pos) <= 1e-12:
            return (
                False,
                None,
                "Unresolved anchor: Orientation functional vanishes on candidate pair (<a, v> = 0); cannot distinguish antipodes.",
            )

        if dot_pos > 0.0:
            return True, v_pos, "Success: Reconstructed cochain aligned with reference orientation anchor."
        else:
            return True, v_neg, "Success: Reconstructed cochain aligned with reference orientation anchor."

    @staticmethod
    def trace_distance(rho_a: DensityOperator, rho_b: DensityOperator) -> float:
        r"""Trace distance Xi(u, v) between two rank-1 density operators.

        Xi(u, v) = 1/2 ||rho_a - rho_b||_tr = sqrt(1 - |<psi_a | psi_b>|^2).
        Acts as a pseudometric on nonzero cochains and a metric on the projective quotient
        (C^1 \ {0}) / R^x (i.e. unoriented lines).

        Numerically stable calculation:
            Xi(a, b) = 1/2 ||a - b||_2 * ||a + b||_2
        Identity:
            1/4 ||a - b||_2^2 ||a + b||_2^2 = 1/4 (2 - 2<a, b>)(2 + 2<a, b>) = 1 - <a, b>^2.
        Avoids catastrophic cancellation near identity without artificial cutoffs,
        preserving the metric triangle inequality.
        """
        if rho_a == rho_b:
            return 0.0

        a = rho_a.state_vector
        b = rho_b.state_vector

        diff_norm = float(np.linalg.norm(a - b))
        sum_norm = float(np.linalg.norm(a + b))
        dist = 0.5 * diff_norm * sum_norm
        # Bound floating-point drift strictly into [0.0, 1.0]
        return max(0.0, min(1.0, dist))

    @staticmethod
    def _integer_coordinates(vector: Sequence[int]) -> list[int]:
        coordinates: list[int] = []
        for item in vector:
            if isinstance(item, bool) or not isinstance(item, int):
                raise TypeError("integer cochain coordinates must be int")
            coordinates.append(item)
        return coordinates

    @staticmethod
    def integer_trace_norm(vector: Sequence[int]) -> int:
        """Sum of absolute integer coordinates. This is the finite trace norm."""
        return sum(abs(item) for item in OperatorLifts._integer_coordinates(vector))

    @staticmethod
    def normalized_abs_weights(vector: Sequence[int]) -> tuple[Fraction, ...]:
        """Absolute coordinates divided by the integer trace norm."""
        coordinates = OperatorLifts._integer_coordinates(vector)
        total = sum(abs(item) for item in coordinates)
        if total == 0:
            raise ValueError("absolute weights are undefined at zero mass")
        return tuple(Fraction(abs(item), total) for item in coordinates)

    @staticmethod
    def cleared_homogeneous_pair(scale: int, numerator: int, denominator: int) -> tuple[int, int]:
        """Return (|c| n, |c| d) for a nonzero integer scale."""
        if isinstance(scale, bool) or not isinstance(scale, int):
            raise TypeError("scale must be int")
        if isinstance(numerator, bool) or not isinstance(numerator, int):
            raise TypeError("numerator must be int")
        if isinstance(denominator, bool) or not isinstance(denominator, int):
            raise TypeError("denominator must be int")
        if scale == 0:
            raise ValueError("homogeneous ratio is undefined at scale 0")
        if denominator == 0:
            raise ValueError("denominator must be nonzero")
        factor = abs(scale)
        return (factor * numerator, factor * denominator)

    @staticmethod
    def squared_trace_gap(left: Sequence[int], right: Sequence[int]) -> tuple[int, int]:
        """Both sides of the equal-norm integer identity.

        Returns
        ``(sum (a-b)^2 * sum (a+b)^2, 4 * (sum a^2 * sum b^2 - dot^2))``.
        """
        first = OperatorLifts._integer_coordinates(left)
        second = OperatorLifts._integer_coordinates(right)
        if len(first) != len(second):
            raise ValueError("squared trace gap requires equal lengths")
        sum_first = sum(item * item for item in first)
        sum_second = sum(item * item for item in second)
        if sum_first != sum_second:
            raise ValueError("squared trace gap requires equal sums of squares")
        dot = sum(item * other for item, other in zip(first, second))
        difference = [item - other for item, other in zip(first, second)]
        total = [item + other for item, other in zip(first, second)]
        left_side = sum(item * item for item in difference) * sum(item * item for item in total)
        right_side = 4 * (sum_first * sum_second - dot * dot)
        return (left_side, right_side)


@dataclass(frozen=True)
class DiagnosticState:
    """Diagnostic state tuple for a discrete graph cochain: (phi_1, gamma_2, r_cl, xi).

    - phi_1: Primary 1-cycle quotient residual (min ||omega - d_0 f||_1).
    - gamma_2: Secondary closure curvature / 2-cell boundary defect (||d_1 omega||_1).
    - r_cl: Piecewise boundary ratio gamma_2 / phi_1 (None indicates +infinity).
    - xi: Representative distortion metric in [0, 1] computed via density operator trace distance.
    """
    phi_1: float
    gamma_2: float
    r_cl: Optional[float]
    xi: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.phi_1) and self.phi_1 >= 0.0):
            raise ValueError(f"phi_1 must be non-negative and finite, got {self.phi_1}")
        if not (math.isfinite(self.gamma_2) and self.gamma_2 >= 0.0):
            raise ValueError(f"gamma_2 must be non-negative and finite, got {self.gamma_2}")
        if self.r_cl is not None and not (math.isfinite(self.r_cl) and self.r_cl >= 0.0):
            raise ValueError(f"r_cl must be None (+inf) or non-negative and finite, got {self.r_cl}")
        if not (math.isfinite(self.xi) and -1e-12 <= self.xi <= 1.0 + 1e-9):
            raise ValueError(f"xi must be in [0, 1], got {self.xi}")

        # Consistency validation between phi_1, gamma_2, and r_cl
        if self.phi_1 > 1e-9:
            expected_ratio = self.gamma_2 / self.phi_1
            if self.r_cl is None:
                raise ValueError(
                    f"Inconsistent diagnostic state: r_cl cannot be None (+inf) when phi_1 > 0 ({self.phi_1}); expected {expected_ratio}"
                )
            if not math.isclose(self.r_cl, expected_ratio, rel_tol=1e-4, abs_tol=1e-6):
                raise ValueError(
                    f"Inconsistent diagnostic state: r_cl ({self.r_cl}) does not match gamma_2/phi_1 ({expected_ratio})"
                )
        else:
            if self.gamma_2 > 1e-9:
                if self.r_cl is not None:
                    raise ValueError(
                        f"Inconsistent diagnostic state: r_cl must be None (+inf) when phi_1 == 0 and gamma_2 > 0; got {self.r_cl}"
                    )
            else:
                if self.r_cl is not None and not math.isclose(self.r_cl, 0.0, abs_tol=1e-6):
                    raise ValueError(
                        f"Inconsistent diagnostic state: r_cl must be 0.0 or None when phi_1 == 0 and gamma_2 == 0; got {self.r_cl}"
                    )


class GuardedDescentEvaluator:
    """Guarded descent evaluator enforcing the declared selection priority on discrete complexes.

    Hierarchy:
    1. Guardrail (R_cl): Boundary ratio R_cl = Gamma_2 / Phi_1 must satisfy R_cl <= r_max.
       A hard feasibility condition: proposals violating the ratio ceiling or possessing infinite
       curvature (R_cl is None, meaning Gamma_2 > eps while Phi_1 <= eps) are rejected before
       evaluating descent.
    2. Primary Gate (Phi_1): Strict quotient residual reduction.
       No candidate with Phi_1(S') > Phi_1(S) is accepted.
    3. Secondary Gate (Gamma_2): Curvature / closure defect reduction when Phi_1 is non-increasing.
       No candidate with Gamma_2(S') > Gamma_2(S) is accepted on tie-break.
    4. Tertiary Gate (Xi): Representative distortion tie-breaking when both Phi_1 and Gamma_2
       are non-increasing.
       Xi = 1/2 ||rho(omega) - rho(omega_ref)||_tr breaks ties between geometrically distinct cochains.

    Antipodal Boundary:
    Because Xi(v, -v) == 0, spectral trace metrics cannot distinguish antipodal proposals.
    Orientation must be certified combinatorially.
    """

    def __init__(self, r_max: float = 1.0, eps: float = 1e-9) -> None:
        self.r_max = r_max
        self.eps = eps

    def compute_r_cl(self, phi_1: float, gamma_2: float) -> Optional[float]:
        """Compute closure ratio R_cl = gamma_2 / phi_1 with piecewise guard against infinite curvature."""
        if phi_1 > self.eps:
            return gamma_2 / phi_1
        if gamma_2 <= self.eps:
            return 0.0
        return None  # Represents +infinity (curvature defect present while cycle obstruction resolved)

    def evaluate_transition(
        self,
        current: DiagnosticState,
        candidate: DiagnosticState,
    ) -> Tuple[bool, str]:
        """Evaluate admissibility of moving from current state to candidate state."""
        # 1. Guardrail check: R_cl must satisfy hard feasibility ceiling
        if candidate.r_cl is None:
            return False, "Rejected: Closure ratio R_cl is +infinity (curvature defect with vanished cycle obstruction)."
        if candidate.r_cl > self.r_max:
            return False, f"Rejected: Closure ratio R_cl ({candidate.r_cl:.4f}) exceeds policy ceiling ({self.r_max:.4f})."

        # 2. Primary check: Phi_1 reduction with fail-closed non-increase fence
        if candidate.phi_1 < current.phi_1 - self.eps:
            return True, "Accepted: Primary quotient residual Phi_1 decreased."
        if candidate.phi_1 > current.phi_1:
            return False, "Rejected: Primary quotient residual Phi_1 increased (spectral metrics cannot override topological boundary)."

        # 3. Secondary check: Gamma_2 reduction under Phi_1 non-increase
        if candidate.gamma_2 < current.gamma_2 - self.eps:
            return True, "Accepted: Secondary closure curvature Gamma_2 decreased with non-increasing Phi_1."
        if candidate.gamma_2 > current.gamma_2:
            return False, "Rejected: Secondary closure curvature Gamma_2 increased with non-increasing Phi_1."

        # 4. Tertiary check: Xi tie-breaking when (Phi_1, Gamma_2) are non-increasing within eps
        if candidate.xi < current.xi - self.eps:
            return True, "Accepted: Representative distortion Xi decreased on tie-break."

        return False, "Rejected: No improvement across diagnostic hierarchy (no strict descent)."

    def compare_candidates(
        self,
        cand_a: DiagnosticState,
        cand_b: DiagnosticState,
    ) -> int:
        """Compare two candidates directly under the declared selection priority.

        Enforces a strictly transitive lexicographic total order on stored finite values:
        1. Hard feasibility: candidates satisfying R_cl <= r_max strictly dominate invalid candidates.
        2. Primary: lower Phi_1.
        3. Secondary: lower Gamma_2.
        4. Tertiary: lower Xi.

        Avoids pairwise epsilon-equivalence cycles.

        Returns:
            -1 if cand_a is strictly preferred to cand_b
            +1 if cand_b is strictly preferred to cand_a
             0 if indistinguishable under the hierarchy
        """
        # Guardrail feasibility check
        a_valid = (cand_a.r_cl is not None) and (cand_a.r_cl <= self.r_max)
        b_valid = (cand_b.r_cl is not None) and (cand_b.r_cl <= self.r_max)
        if a_valid and not b_valid:
            return -1
        if b_valid and not a_valid:
            return 1
        if not a_valid and not b_valid:
            return 0

        # Primary: Phi_1 (exact lexicographic comparison of stored finite values)
        if cand_a.phi_1 < cand_b.phi_1:
            return -1
        if cand_a.phi_1 > cand_b.phi_1:
            return 1

        # Secondary: Gamma_2
        if cand_a.gamma_2 < cand_b.gamma_2:
            return -1
        if cand_a.gamma_2 > cand_b.gamma_2:
            return 1

        # Tertiary: Xi
        if cand_a.xi < cand_b.xi:
            return -1
        if cand_a.xi > cand_b.xi:
            return 1

        return 0

    def evaluate_candidates(
        self,
        current: DiagnosticState,
        candidates: Sequence[DiagnosticState],
    ) -> List[Tuple[int, bool, str]]:
        """Evaluate candidate transitions from current state, preserving original input order."""
        results = []
        for idx, cand in enumerate(candidates):
            admissible, reason = self.evaluate_transition(current, cand)
            results.append((idx, admissible, reason))
        return results

    def rank_candidates(
        self,
        current: DiagnosticState,
        candidates: Sequence[DiagnosticState],
    ) -> List[Tuple[int, bool, str]]:
        """Rank and sort candidate transitions from current state by selection priority.

        Returns a sorted list of (original_index, admissible, reason) tuples:
        - Admissible candidates precede inadmissible candidates.
        - Candidates are ordered from most preferred to least preferred according to compare_candidates.
        - Stable on ties using original index.
        """
        evaluations = []
        for idx, cand in enumerate(candidates):
            admissible, reason = self.evaluate_transition(current, cand)
            evaluations.append((idx, cand, admissible, reason))

        def sort_key(item: Tuple[int, DiagnosticState, bool, str]):
            idx, cand, admissible, _ = item
            feasibility_rank = 0 if admissible else 1
            return (feasibility_rank, cand.phi_1, cand.gamma_2, cand.xi, idx)

        sorted_evals = sorted(evaluations, key=sort_key)
        return [(idx, admissible, reason) for idx, _, admissible, reason in sorted_evals]

    @staticmethod
    def _exact_fraction(value: Fraction, name: str) -> Fraction:
        if isinstance(value, bool) or not isinstance(value, Fraction):
            raise TypeError(f"{name} must be Fraction")
        return value

    @staticmethod
    def exact_admits(
        current: tuple[Fraction, Fraction, Fraction],
        candidate: tuple[Fraction, Fraction, Fraction, Fraction | None],
        r_max: Fraction,
        eps: Fraction,
    ) -> bool:
        """Exact rational fence. The ratio ceiling is tested before a primary decrease."""
        if len(current) != 3 or len(candidate) != 4:
            raise ValueError("exact admits expects a 3-tuple current and a 4-tuple candidate")
        cur_phi = GuardedDescentEvaluator._exact_fraction(current[0], "current phi")
        cur_gamma = GuardedDescentEvaluator._exact_fraction(current[1], "current gamma")
        cur_xi = GuardedDescentEvaluator._exact_fraction(current[2], "current xi")
        cand_phi = GuardedDescentEvaluator._exact_fraction(candidate[0], "candidate phi")
        cand_gamma = GuardedDescentEvaluator._exact_fraction(candidate[1], "candidate gamma")
        cand_xi = GuardedDescentEvaluator._exact_fraction(candidate[2], "candidate xi")
        cand_rcl = candidate[3]
        if cand_rcl is not None:
            cand_rcl = GuardedDescentEvaluator._exact_fraction(cand_rcl, "candidate r_cl")
        ceiling = GuardedDescentEvaluator._exact_fraction(r_max, "r_max")
        tolerance = GuardedDescentEvaluator._exact_fraction(eps, "eps")
        if tolerance < 0:
            raise ValueError("eps must be nonnegative")
        if cand_rcl is None or ceiling < cand_rcl:
            return False
        if cand_phi < cur_phi - tolerance:
            return True
        if cur_phi < cand_phi:
            return False
        if cand_gamma < cur_gamma - tolerance:
            return True
        if cur_gamma < cand_gamma:
            return False
        if cand_xi < cur_xi - tolerance:
            return True
        return False

    @staticmethod
    def exact_compare(
        left: tuple[Fraction, Fraction, Fraction, Fraction | None],
        right: tuple[Fraction, Fraction, Fraction, Fraction | None],
        r_max: Fraction,
    ) -> int:
        """Return -1, 0, or 1 under feasibility, then phi, gamma, and xi."""
        if len(left) != 4 or len(right) != 4:
            raise ValueError("exact compare expects 4-tuples")
        ceiling = GuardedDescentEvaluator._exact_fraction(r_max, "r_max")

        def feasible(row: tuple[Fraction, Fraction, Fraction, Fraction | None]) -> bool:
            rcl = row[3]
            if rcl is None:
                return False
            rcl = GuardedDescentEvaluator._exact_fraction(rcl, "r_cl")
            return rcl <= ceiling

        for row, name in ((left, "left"), (right, "right")):
            GuardedDescentEvaluator._exact_fraction(row[0], f"{name} phi")
            GuardedDescentEvaluator._exact_fraction(row[1], f"{name} gamma")
            GuardedDescentEvaluator._exact_fraction(row[2], f"{name} xi")
        left_ok = feasible(left)
        right_ok = feasible(right)
        if left_ok and not right_ok:
            return -1
        if right_ok and not left_ok:
            return 1
        if not left_ok and not right_ok:
            return 0
        for index in range(3):
            if left[index] < right[index]:
                return -1
            if right[index] < left[index]:
                return 1
        return 0
