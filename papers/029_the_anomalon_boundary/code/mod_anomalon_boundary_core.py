"""Reference implementation for The Anomalon Boundary.

Formalizes:
1. Finite Cochain Complex and Surviving Primitive Difference trichotomy:
   - Validates boundary operator composition d^1 d^0 = 0 over Q.
   - Exact discrepancies vanish as gauge (VanishesAsGauge, [h] = 0 in H^1).
   - Unclosed discrepancies represent active closure failures (ActiveIncoherence, Gamma_2 > 0).
   - Closed non-exact discrepancies survive local-to-global descent (SurvivingPrimitiveDifference, Gamma_2 = 0, [h] != 0).
   - Rejects mathematically inconsistent cochain defects fail-closed.
2. The Anomalon Boundary as an active recursion/restart firewall:
   - Positive residual mass and exhausted repairs required.
   - Three lawful continuations: TypedRefusal (recorded), RestartSeed (scheduled), LiftRequest (requested).
   - Lift authorization strictly gated by a validated LiftPreservationWitness (Delta_Lambda > 0).
   - Non-Promotion rule: Anomalon boundary cannot be promoted to authority.
3. Minimal Knowable System (MKS) role completeness:
   - Proposed interface specification for systems terminalizable under this calculus.
   - Scope fence: Boolean completeness verifies interface slot occupancy; it does not prove
     these roles necessary for knowability in general.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Sequence


class DefectStatus(str, Enum):
    VANISHES_AS_GAUGE = "VanishesAsGauge"
    ACTIVE_INCOHERENCE = "ActiveIncoherence"
    SURVIVING_PRIMITIVE_DIFFERENCE = "SurvivingPrimitiveDifference"


class ContinuationType(str, Enum):
    TYPED_REFUSAL = "TypedRefusal"
    LIFT_REQUEST = "LiftRequest"
    RESTART_SEED = "RestartSeed"


class FirewallViolationError(TypeError):
    """Raised when an illegal promotion of an Anomalon boundary object into authority is attempted."""
    pass


def _solve_linear_system_exact(
    A: Sequence[Sequence[Fraction | int]],
    b: Sequence[Fraction | int],
) -> bool:
    """Determine whether b in im(A) over Q using exact Gaussian elimination."""
    m = len(A)
    if m == 0:
        return len(b) == 0
    n = len(A[0])
    if len(b) != m:
        raise ValueError(f"Dimension mismatch: A has {m} rows, b has length {len(b)}")

    # Build augmented matrix [A | b]
    M = [[Fraction(A[i][j]) for j in range(n)] + [Fraction(b[i])] for i in range(m)]

    lead = 0
    for col in range(n):
        if lead >= m:
            break
        # Find pivot
        pivot_row = None
        for r in range(lead, m):
            if M[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue

        # Swap rows
        M[lead], M[pivot_row] = M[pivot_row], M[lead]

        # Normalize pivot row
        pivot_val = M[lead][col]
        for c in range(col, n + 1):
            M[lead][c] /= pivot_val

        # Eliminate other rows
        for r in range(m):
            if r != lead and M[r][col] != 0:
                factor = M[r][col]
                for c in range(col, n + 1):
                    M[r][c] -= factor * M[lead][c]

        lead += 1

    # Check consistency: no row [0 ... 0 | non-zero]
    for r in range(m):
        all_zero = all(M[r][c] == 0 for c in range(n))
        if all_zero and M[r][n] != 0:
            return False

    return True


@dataclass(frozen=True)
class CochainDefect:
    """A 1-cochain discrepancy in a finite complex with verified consistency invariants."""
    defect_id: str
    mass: Fraction
    is_closed: bool           # d^1 h == 0 (Gamma_2 == 0)
    is_exact: bool            # h in im(d^0) (removable by gauge)
    closure_defect: Fraction = Fraction(0)  # Gamma_2 = ||d_1 h||_1

    def __post_init__(self) -> None:
        """Fail-closed validation of cochain mathematical consistency."""
        if self.mass < 0:
            raise ValueError(f"CochainDefect mass cannot be negative, got {self.mass}")
        if self.closure_defect < 0:
            raise ValueError(f"CochainDefect closure_defect cannot be negative, got {self.closure_defect}")

        # Mathematical consistency invariants under d^1 d^0 = 0:
        # 1. An exact discrepancy h = d^0 alpha implies d^1 h = d^1 d^0 alpha = 0,
        #    so closure_defect (Gamma_2) must be 0 and is_closed must be True.
        if self.is_exact and (not self.is_closed or self.closure_defect > 0):
            raise ValueError(
                f"Inconsistent cochain defect: an exact discrepancy must be closed with zero closure defect "
                f"(d^1 d^0 = 0). Got is_closed={self.is_closed}, closure_defect={self.closure_defect}."
            )

        # 2. A closed cochain has Gamma_2 = 0.
        if self.is_closed and self.closure_defect > 0:
            raise ValueError(
                f"Inconsistent cochain defect: closed cochain must have closure_defect == 0, "
                f"got {self.closure_defect}."
            )

        # 3. An unclosed cochain has Gamma_2 > 0.
        if not self.is_closed and self.closure_defect == 0:
            raise ValueError(
                "Inconsistent cochain defect: unclosed cochain must have strictly positive closure defect."
            )

    def classify(self) -> DefectStatus:
        """Classify defect per Section 2.6 Surviving Primitive Difference trichotomy."""
        if self.is_exact:
            if not self.is_closed or self.closure_defect > 0:
                raise ValueError("Inconsistent exact defect with non-zero curvature.")
            return DefectStatus.VANISHES_AS_GAUGE
        if not self.is_closed or self.closure_defect > 0:
            return DefectStatus.ACTIVE_INCOHERENCE
        return DefectStatus.SURVIVING_PRIMITIVE_DIFFERENCE


@dataclass(frozen=True)
class CochainComplex:
    """A finite cochain complex C^0 -> C^1 -> C^2 with verified d^1 d^0 = 0."""
    d0: tuple[tuple[Fraction, ...], ...]  # shape (n1, n0)
    d1: tuple[tuple[Fraction, ...], ...]  # shape (n2, n1)

    def __init__(
        self,
        d0: Sequence[Sequence[Fraction | int]],
        d1: Sequence[Sequence[Fraction | int]],
    ) -> None:
        converted_d0 = tuple(tuple(Fraction(x) for x in row) for row in d0)
        converted_d1 = tuple(tuple(Fraction(x) for x in row) for row in d1)
        object.__setattr__(self, "d0", converted_d0)
        object.__setattr__(self, "d1", converted_d1)

        n1 = len(converted_d0)
        if n1 == 0:
            raise ValueError("d0 cannot have zero rows (C^1 cannot be empty).")
        n0 = len(converted_d0[0])
        for row in converted_d0:
            if len(row) != n0:
                raise ValueError("All rows of d0 must have the same length.")

        n2 = len(converted_d1)
        if n2 == 0:
            raise ValueError("d1 cannot have zero rows (C^2 cannot be empty).")
        for row in converted_d1:
            if len(row) != n1:
                raise ValueError(f"d1 row length ({len(row)}) must match d0 row count ({n1}).")

        # Verify d^1 d^0 = 0
        for i in range(n2):
            for k in range(n0):
                val = sum(converted_d1[i][j] * converted_d0[j][k] for j in range(n1))
                if val != 0:
                    raise ValueError(
                        f"Invalid cochain complex: (d1 * d0)[{i},{k}] = {val} != 0. "
                        f"Coboundary condition d^1 d^0 = 0 fails."
                    )

    @property
    def dim_c0(self) -> int:
        return len(self.d0[0])

    @property
    def dim_c1(self) -> int:
        return len(self.d0)

    @property
    def dim_c2(self) -> int:
        return len(self.d1)

    def analyze_defect(
        self,
        cochain: Sequence[Fraction | int],
        defect_id: str = "defect-1",
    ) -> CochainDefect:
        """Compute exact curvature, closure defect, and exactness from explicit boundary matrices."""
        if len(cochain) != self.dim_c1:
            raise ValueError(
                f"Cochain length {len(cochain)} does not match 1-cochain dimension {self.dim_c1}."
            )

        h = [Fraction(x) for x in cochain]
        mass = sum(abs(x) for x in h)

        # Curvature d^1 h
        curvature = [
            sum(self.d1[i][j] * h[j] for j in range(self.dim_c1))
            for i in range(self.dim_c2)
        ]
        closure_defect = sum(abs(c) for c in curvature)
        is_closed = (closure_defect == 0)

        # Exactness: does there exist alpha in C^0 such that d0 alpha = h?
        is_exact = _solve_linear_system_exact(self.d0, h)

        return CochainDefect(
            defect_id=defect_id,
            mass=mass,
            is_closed=is_closed,
            is_exact=is_exact,
            closure_defect=closure_defect,
        )


@dataclass(frozen=True)
class LiftPreservationWitness:
    """Witness certifying carrier extension with strictly positive preservation metric Delta_Lambda > 0."""
    contract_id: str
    target_dimension: int
    preservation_metric: Fraction  # Delta_Lambda > 0

    def __post_init__(self) -> None:
        if not self.contract_id or not self.contract_id.strip():
            raise ValueError("LiftPreservationWitness requires non-empty contract_id.")
        if self.target_dimension <= 0:
            raise ValueError(f"Target dimension must be positive, got {self.target_dimension}")
        if self.preservation_metric <= 0:
            raise ValueError(
                f"Preservation metric Delta_Lambda must be strictly positive, got {self.preservation_metric}"
            )


@dataclass(frozen=True)
class AnomalonBoundary:
    """The boundary object produced when a finite system exhausts admitted repairs and retains obstruction."""
    residual_id: str
    residual_mass: Fraction
    exhausted_repairs_count: int

    def __post_init__(self) -> None:
        if not self.residual_id or not self.residual_id.strip():
            raise ValueError("AnomalonBoundary requires non-empty residual_id.")
        if self.residual_mass <= 0:
            raise ValueError(
                f"AnomalonBoundary requires strictly positive residual mass (retained obstruction), "
                f"got {self.residual_mass}."
            )
        if self.exhausted_repairs_count <= 0:
            raise ValueError(
                f"AnomalonBoundary requires exhausted_repairs_count > 0, "
                f"got {self.exhausted_repairs_count}."
            )

    def request_continuation(
        self,
        continuation_type: ContinuationType,
        witness_or_reason: str,
    ) -> dict[str, str | ContinuationType | Fraction]:
        """Execute one of the three lawful continuations from an Anomalon boundary.
        
        Distinguishes requested lift (LIFT_REQUESTED) from an authorized lift (LIFT_AUTHORIZED).
        """
        if not isinstance(continuation_type, ContinuationType):
            raise TypeError(
                f"continuation_type must be a ContinuationType enum instance, "
                f"got {type(continuation_type).__name__}: {continuation_type!r}"
            )
        if not isinstance(witness_or_reason, str) or not witness_or_reason.strip():
            raise ValueError("Continuation requires non-empty witness or reason string.")

        if continuation_type == ContinuationType.TYPED_REFUSAL:
            status = "REFUSAL_RECORDED"
        elif continuation_type == ContinuationType.RESTART_SEED:
            status = "RESTART_SCHEDULED"
        elif continuation_type == ContinuationType.LIFT_REQUEST:
            status = "LIFT_REQUESTED"
        else:
            raise ValueError(f"Unknown continuation type: {continuation_type}")

        return {
            "residual_id": self.residual_id,
            "residual_mass": self.residual_mass,
            "continuation": continuation_type,
            "witness_or_reason": witness_or_reason.strip(),
            "status": status,
        }

    def authorize_lift(
        self,
        witness: LiftPreservationWitness,
    ) -> dict[str, str | ContinuationType | Fraction | int]:
        """Authorize a lift transition guarded by an explicit preservation witness."""
        if not isinstance(witness, LiftPreservationWitness):
            raise FirewallViolationError(
                f"Firewall Refusal: Authorizing a lift requires a valid LiftPreservationWitness, "
                f"got {type(witness).__name__}."
            )
        if witness.preservation_metric <= 0:
            raise FirewallViolationError(
                f"Firewall Refusal: Preservation metric Delta_Lambda must be strictly positive, "
                f"got {witness.preservation_metric}."
            )
        return {
            "residual_id": self.residual_id,
            "residual_mass": self.residual_mass,
            "continuation": ContinuationType.LIFT_REQUEST,
            "witness_or_reason": f"Contract {witness.contract_id}: dim {witness.target_dimension}",
            "status": "LIFT_AUTHORIZED",
            "target_dimension": witness.target_dimension,
            "preservation_metric": witness.preservation_metric,
        }

    def assert_no_authority_promotion(self) -> None:
        """Firewall rule: An Anomalon boundary object cannot be promoted to authority."""
        raise FirewallViolationError(
            f"Firewall Refusal: Anomalon boundary on residual {self.residual_id} "
            f"is a restart boundary, not an authority certificate."
        )


@dataclass(frozen=True)
class MinimalKnowableSystem:
    """Proposed interface schema for systems terminalizable under this finite obstruction calculus.
    
    The 10 essential roles define the minimal structural slots required for gauge, difference,
    local/global comparison, and terminal judgment to be jointly definable.
    
    Scope fence: The Boolean completeness check verifies whether a candidate system populates
    all 10 declared interface slots within this calculus; it does not prove these roles
    ontologically necessary for knowability in general.
    """
    carrier_support: bool = True
    local_state: bool = True
    gauge: bool = True
    coboundary: bool = True
    local_global_comparison: bool = True
    quotient_residual: bool = True
    closure_defect: bool = True
    observer_norm: bool = True
    terminal_rule: bool = True
    continuation_rule: bool = True

    def check_completeness(self) -> tuple[bool, list[str]]:
        """Verify role completeness per Section 2.5 table."""
        missing = []
        if not self.carrier_support:
            missing.append("Carrier/support")
        if not self.local_state:
            missing.append("Local state")
        if not self.gauge:
            missing.append("Gauge")
        if not self.coboundary:
            missing.append("Coboundary / primitive difference")
        if not self.local_global_comparison:
            missing.append("Local/global comparison")
        if not self.quotient_residual:
            missing.append("Quotient residual")
        if not self.closure_defect:
            missing.append("Closure defect")
        if not self.observer_norm:
            missing.append("Observer norm / cost")
        if not self.terminal_rule:
            missing.append("Terminal rule")
        if not self.continuation_rule:
            missing.append("Continuation rule")

        return len(missing) == 0, missing
