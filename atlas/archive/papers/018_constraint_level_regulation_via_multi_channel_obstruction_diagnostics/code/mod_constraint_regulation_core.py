"""Reference implementation for Constraint-Level Regulation via Multi-Channel Diagnostics.

Implements:
- 5-Channel Diagnostic State Vector (Phi_geom, Phi_sat, Phi_curv, Phi_rel, Xi)
- Piecewise Closure Ratio R_cl with configured epsilon tolerance
- Repair Selection Controller filtering candidate transitions under descent and boundary stability
- Strict Xi tie-breaker: trace metric breaks ties only when discrete scores are equal within tolerance
- Cost-Sensitive Lift Law Delta_Lambda with explicit parameterization
- Typed Refusals for stalled, tearing, or invalid candidate states
"""

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class MultiChannelState:
    """Represents the 5-channel diagnostic signature of a constraint state."""

    phi_geom: float  # Phi_1: l^1 quotient residual [0, inf)
    phi_sat: float  # Phi_sat: violated logical clauses [0, inf)
    phi_curv: float  # Gamma_2: 2-boundary curvature / closure defect [0, inf)
    phi_rel: float  # Phi_rel: relational interface divergence [0, inf)
    xi: float  # Xi: normalized trace distance [0, 1]

    def __post_init__(self) -> None:
        """Validate finite, non-negative inputs and valid trace metric domain."""
        for name in ("phi_geom", "phi_sat", "phi_curv", "phi_rel", "xi"):
            val = getattr(self, name)
            if not math.isfinite(val):
                raise ValueError(f"{name} must be finite, got {val}")
            if val < 0.0:
                raise ValueError(f"{name} must be non-negative, got {val}")
        if self.xi > 1.0:
            raise ValueError(f"xi must be in [0.0, 1.0], got {self.xi}")

        # Contradictory signature rejection:
        # On a finite cochain complex with d_1 d_0 = 0, Gamma_2 <= ||d_1|| Phi_1.
        # When Phi_1 = 0, any realized cochain enforces Gamma_2 = 0.
        if self.phi_geom == 0.0 and self.phi_curv > 0.0:
            raise ValueError(
                f"Contradictory state: phi_curv must be 0.0 when phi_geom is 0.0 "
                f"(by Gamma_2 <= ||d_1|| Phi_1), got phi_curv={self.phi_curv}"
            )
        # By declared operational convention on unobstructed classes, Xi = 0.0 when Phi_1 = 0.
        if self.phi_geom == 0.0 and self.xi > 0.0:
            raise ValueError(
                f"Contradictory state: xi must be 0.0 when phi_geom is 0.0 "
                f"(by zero-obstruction convention), got xi={self.xi}"
            )

    def get_r_cl(self, eps: float = 1e-9) -> float:
        """Compute the piecewise closure ratio R_cl.

        Exact piecewise definition:
        - If phi_geom == 0.0: returns 0.0 if phi_curv == 0.0 else +inf
        - If phi_geom > 0.0: returns phi_curv / phi_geom
        """
        if not math.isfinite(self.phi_geom) or not math.isfinite(self.phi_curv):
            return float("nan")
        if self.phi_geom == 0.0:
            return 0.0 if self.phi_curv == 0.0 else float("inf")
        return self.phi_curv / self.phi_geom

    @property
    def r_cl(self) -> float:
        """Compute the piecewise closure ratio R_cl."""
        return self.get_r_cl(1e-9)


@dataclass(frozen=True)
class RepairOperator:
    """Represents a candidate repair operator."""

    name: str
    cost: float
    is_lift: bool
    dim_penalty: float = 0.0

    def __post_init__(self) -> None:
        """Validate operator cost parameters."""
        if not math.isfinite(self.cost) or self.cost < 0.0:
            raise ValueError(f"cost must be finite and non-negative, got {self.cost}")
        if not math.isfinite(self.dim_penalty) or self.dim_penalty < 0.0:
            raise ValueError(
                f"dim_penalty must be finite and non-negative, got {self.dim_penalty}"
            )


@dataclass
class ControllerDecision:
    """Result of repair controller candidate evaluation."""

    selected_operator: Optional[RepairOperator]
    status: str  # "Admitted", "RefusedTearing", "RefusedDescentViolation", "RefusedStalled", "RefusedInvalidInput"
    diagnostics: Dict[str, Any]


class RepairSelectionController:
    """Evaluates candidate operator proposals and routes repairs under topological guardrails."""

    def __init__(self, r_max: float = 1.0, eps: float = 1e-9):
        if not math.isfinite(r_max) or r_max <= 0.0:
            raise ValueError(f"r_max must be finite and positive, got {r_max}")
        if not math.isfinite(eps) or eps <= 0.0:
            raise ValueError(f"eps must be finite and positive, got {eps}")
        self.r_max = r_max
        self.eps = eps

    def evaluate_r_cl(self, phi_geom: float, phi_curv: float) -> float:
        """Evaluate piecewise R_cl convention."""
        if not math.isfinite(phi_geom) or not math.isfinite(phi_curv):
            return float("nan")
        if phi_geom == 0.0:
            return 0.0 if phi_curv == 0.0 else float("inf")
        if phi_geom < 0.0 or phi_curv < 0.0:
            return float("nan")
        return phi_curv / phi_geom

    def _is_valid_state(self, state: Any) -> bool:
        """Verify that state diagnostics are finite, non-contradictory, and within declared domain."""
        try:
            if not (
                math.isfinite(state.phi_geom)
                and state.phi_geom >= 0.0
                and math.isfinite(state.phi_sat)
                and state.phi_sat >= 0.0
                and math.isfinite(state.phi_curv)
                and state.phi_curv >= 0.0
                and math.isfinite(state.phi_rel)
                and state.phi_rel >= 0.0
                and math.isfinite(state.xi)
                and 0.0 <= state.xi <= 1.0
            ):
                return False
            # Reject contradictory signatures
            if state.phi_geom == 0.0 and (state.phi_curv > 0.0 or state.xi > 0.0):
                return False
            return True
        except (AttributeError, TypeError):
            return False

    def evaluate_candidates(
        self,
        current_state: MultiChannelState,
        candidate_transitions: List[Tuple[RepairOperator, MultiChannelState]],
    ) -> ControllerDecision:
        """Select optimal repair operator satisfying descent and R_cl guardrails.

        Candidate ranking policy:
        1. Guarded Descent: phi_geom(S') <= phi_geom(S_t) (literal non-increase).
        2. Boundary Stability: R_cl(S') <= r_max (exact hard boundary).
        3. Lift Law: if is_lift, Delta_Lambda > 0.
        4. Discrete score computation:
           F_discrete = phi_geom + 0.5 * phi_sat + 0.2 * phi_curv + 0.1 * phi_rel + op.cost
           (rejects non-finite score overflows).
        5. Global ranking over admissible proposals:
           Find F_min = min F_discrete(o).
           Form epsilon-optimal set: C_eps = { o : F_discrete(o) <= F_min + eps }.
           Within C_eps, find Xi_min = min Xi(o).
           Form tie set: T_eps = { o in C_eps : Xi(o) <= Xi_min + eps }.
           Break remaining ties by strictly smaller F_discrete, then smaller Xi, then op.name.
        """
        if not self._is_valid_state(current_state):
            return ControllerDecision(
                selected_operator=None,
                status="RefusedInvalidInput",
                diagnostics={"error": "current_state has non-finite or invalid out-of-range diagnostics."},
            )

        admissible: List[Tuple[float, float, RepairOperator, MultiChannelState, float]] = []
        rejections: List[Tuple[RepairOperator, str, str]] = []

        for op, cand_state in candidate_transitions:
            # 0. Fail-closed validation of candidate state
            if not self._is_valid_state(cand_state):
                rejections.append((
                    op,
                    "RefusedInvalidInput",
                    "Candidate state has non-finite, negative, out-of-range, or contradictory diagnostics.",
                ))
                continue

            # 1. Check descent condition: phi_geom must not increase above current_state (literal non-increase)
            if cand_state.phi_geom > current_state.phi_geom:
                rejections.append((
                    op,
                    "RefusedDescentViolation",
                    f"Geometric residual increased: {cand_state.phi_geom} > {current_state.phi_geom}.",
                ))
                continue

            # 2. Check stability guardrail: R_cl must not exceed exact hard boundary r_max
            cand_r_cl = self.evaluate_r_cl(cand_state.phi_geom, cand_state.phi_curv)
            if not math.isfinite(cand_r_cl) or cand_r_cl > self.r_max:
                rejections.append((
                    op,
                    "RefusedTearing",
                    f"Closure ratio {cand_r_cl} exceeds r_max {self.r_max}.",
                ))
                continue

            # 3. Check lift law if operator is a representation lift
            if op.is_lift:
                delta_geom = current_state.phi_geom - cand_state.phi_geom
                delta_sat = current_state.phi_sat - cand_state.phi_sat
                gain = delta_geom + 0.5 * delta_sat
                delta_lambda = gain - op.dim_penalty
                if delta_lambda <= 0.0:
                    rejections.append((
                        op,
                        "RefusedLiftLawViolation",
                        f"Lift gain {gain} does not exceed dimensional penalty {op.dim_penalty}.",
                    ))
                    continue

            # 4. Discrete objective score and overflow check
            discrete_score = (
                cand_state.phi_geom
                + 0.5 * cand_state.phi_sat
                + 0.2 * cand_state.phi_curv
                + 0.1 * cand_state.phi_rel
                + op.cost
            )
            if not math.isfinite(discrete_score):
                rejections.append((
                    op,
                    "RefusedScoreOverflow",
                    "Discrete objective score overflowed to non-finite value.",
                ))
                continue

            admissible.append((discrete_score, cand_state.xi, op, cand_state, cand_r_cl))

        if not admissible:
            rejection_counts: Dict[str, int] = {}
            for _, tag, _ in rejections:
                rejection_counts[tag] = rejection_counts.get(tag, 0) + 1

            diagnostics: Dict[str, Any] = {
                "rejections": [
                    {"operator": op.name, "reason": tag, "details": det}
                    for op, tag, det in rejections
                ],
                "rejection_counts": rejection_counts,
            }

            if not candidate_transitions:
                diagnostics["error"] = "No candidate transitions were proposed."
                return ControllerDecision(
                    selected_operator=None,
                    status="RefusedStalled",
                    diagnostics=diagnostics,
                )

            # Classify refusal status based on candidate rejections
            if all(tag == "RefusedInvalidInput" for _, tag, _ in rejections):
                diagnostics["error"] = "All proposed candidate transitions contained invalid state diagnostics."
                return ControllerDecision(
                    selected_operator=None,
                    status="RefusedInvalidInput",
                    diagnostics=diagnostics,
                )

            non_invalid = [tag for _, tag, _ in rejections if tag != "RefusedInvalidInput"]
            if non_invalid and all(tag == "RefusedTearing" for tag in non_invalid):
                diagnostics["error"] = "All valid candidate transitions violated boundary stability (tearing)."
                return ControllerDecision(
                    selected_operator=None,
                    status="RefusedTearing",
                    diagnostics=diagnostics,
                )

            if non_invalid and all(tag == "RefusedDescentViolation" for tag in non_invalid):
                diagnostics["error"] = "All valid candidate transitions violated guarded descent."
                return ControllerDecision(
                    selected_operator=None,
                    status="RefusedDescentViolation",
                    diagnostics=diagnostics,
                )

            diagnostics["error"] = "No candidate transition satisfied both descent and boundary stability guardrails."
            return ControllerDecision(
                selected_operator=None,
                status="RefusedStalled",
                diagnostics=diagnostics,
            )

        # Global ranking policy:
        # Step 1: Find the global minimum discrete score among all admissible candidates
        min_score = min(item[0] for item in admissible)

        # Step 2: Form the set of candidates whose discrete score is within eps of the global minimum
        c_eps = [item for item in admissible if item[0] <= min_score + self.eps]

        # Step 3: Within C_eps, find the minimum trace distance Xi
        min_xi = min(item[1] for item in c_eps)

        # Step 4: Form the tie set of candidates whose Xi is within eps of min_xi
        t_eps = [item for item in c_eps if item[1] <= min_xi + self.eps]

        # Step 5: Final deterministic tie rule: prefer strictly smaller discrete score,
        # then strictly smaller Xi, then alphabetical operator name.
        t_eps.sort(key=lambda x: (x[0], x[1], x[2].name))

        best_score, best_xi, best_op, best_state, best_r_cl = t_eps[0]

        return ControllerDecision(
            selected_operator=best_op,
            status="Admitted",
            diagnostics={
                "discrete_score": best_score,
                "objective_score": best_score,  # Alias for backward compatibility
                "resulting_xi": best_xi,
                "resulting_r_cl": best_r_cl,
                "resulting_phi_geom": best_state.phi_geom,
                "admissible_count": len(admissible),
                "eps_tied_count": len(c_eps),
            },
        )

    @staticmethod
    def _exact_fraction(value: Fraction, name: str) -> Fraction:
        if isinstance(value, bool) or not isinstance(value, Fraction):
            raise TypeError(f"{name} must be Fraction")
        return value

    @staticmethod
    def exact_signature_ok(
        phi_geom: Fraction,
        phi_sat: Fraction,
        phi_curv: Fraction,
        phi_rel: Fraction,
        xi: Fraction,
    ) -> bool:
        """Accept a rational channel tuple that is nonnegative and not contradictory."""
        geom = RepairSelectionController._exact_fraction(phi_geom, "phi_geom")
        sat = RepairSelectionController._exact_fraction(phi_sat, "phi_sat")
        curv = RepairSelectionController._exact_fraction(phi_curv, "phi_curv")
        rel = RepairSelectionController._exact_fraction(phi_rel, "phi_rel")
        distortion = RepairSelectionController._exact_fraction(xi, "xi")
        if geom < 0 or sat < 0 or curv < 0 or rel < 0 or distortion < 0 or distortion > 1:
            return False
        if geom == 0 and (curv > 0 or distortion > 0):
            return False
        return True

    @staticmethod
    def exact_ratio_admits(phi_geom: Fraction, phi_curv: Fraction, r_max: Fraction) -> bool:
        """Piecewise ratio guard. Positive geometry uses the cross-multiplied comparison."""
        geom = RepairSelectionController._exact_fraction(phi_geom, "phi_geom")
        curv = RepairSelectionController._exact_fraction(phi_curv, "phi_curv")
        ceiling = RepairSelectionController._exact_fraction(r_max, "r_max")
        if ceiling <= 0:
            raise ValueError("r_max must be positive")
        if geom < 0 or curv < 0:
            return False
        if geom == 0:
            return curv == 0
        return curv <= ceiling * geom

    @staticmethod
    def exact_lift_admitted(delta_geom: Fraction, delta_sat: Fraction, dim_penalty: Fraction) -> bool:
        """Admit a lift only when geom drop plus half the sat drop exceeds the penalty."""
        geom_drop = RepairSelectionController._exact_fraction(delta_geom, "delta_geom")
        sat_drop = RepairSelectionController._exact_fraction(delta_sat, "delta_sat")
        penalty = RepairSelectionController._exact_fraction(dim_penalty, "dim_penalty")
        gain = geom_drop + Fraction(1, 2) * sat_drop
        return gain > penalty

    @staticmethod
    def exact_discrete_score(
        phi_geom: Fraction,
        phi_sat: Fraction,
        phi_curv: Fraction,
        phi_rel: Fraction,
        cost: Fraction,
    ) -> Fraction:
        """Declared weights 1, 1/2, 1/5, 1/10, plus operator cost."""
        geom = RepairSelectionController._exact_fraction(phi_geom, "phi_geom")
        sat = RepairSelectionController._exact_fraction(phi_sat, "phi_sat")
        curv = RepairSelectionController._exact_fraction(phi_curv, "phi_curv")
        rel = RepairSelectionController._exact_fraction(phi_rel, "phi_rel")
        operator_cost = RepairSelectionController._exact_fraction(cost, "cost")
        return (
            geom
            + Fraction(1, 2) * sat
            + Fraction(1, 5) * curv
            + Fraction(1, 10) * rel
            + operator_cost
        )

    @staticmethod
    def exact_select(
        current: tuple[Fraction, Fraction, Fraction, Fraction, Fraction],
        candidates: list[tuple[str, Fraction, bool, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]],
        r_max: Fraction,
        eps: Fraction,
    ) -> tuple[str, str | None]:
        """Return ``(status, operator name)`` under the exact rational controller."""
        if len(current) != 5:
            raise ValueError("current state must be a 5-tuple")
        ceiling = RepairSelectionController._exact_fraction(r_max, "r_max")
        tolerance = RepairSelectionController._exact_fraction(eps, "eps")
        if ceiling <= 0:
            raise ValueError("r_max must be positive")
        if tolerance <= 0:
            raise ValueError("eps must be positive")
        if not RepairSelectionController.exact_signature_ok(*current):
            return ("RefusedInvalidInput", None)

        admissible: list[tuple[Fraction, Fraction, str]] = []
        tags: list[str] = []
        for row in candidates:
            if len(row) != 9 or not isinstance(row[0], str) or isinstance(row[2], bool) is False:
                raise TypeError("candidate must be (name, cost, is_lift, penalty, geom, sat, curv, rel, xi)")
            name, cost, is_lift, penalty, geom, sat, curv, rel, xi = row
            if not RepairSelectionController.exact_signature_ok(geom, sat, curv, rel, xi):
                tags.append("RefusedInvalidInput")
                continue
            if geom > current[0]:
                tags.append("RefusedDescentViolation")
                continue
            if not RepairSelectionController.exact_ratio_admits(geom, curv, ceiling):
                tags.append("RefusedTearing")
                continue
            if is_lift:
                gain_ok = RepairSelectionController.exact_lift_admitted(
                    current[0] - geom,
                    current[1] - sat,
                    penalty,
                )
                if not gain_ok:
                    tags.append("RefusedLiftLawViolation")
                    continue
            score = RepairSelectionController.exact_discrete_score(geom, sat, curv, rel, cost)
            admissible.append((score, xi, name))

        if not admissible:
            return (RepairSelectionController._exact_refusal(tags), None)

        minimum = min(item[0] for item in admissible)
        score_band = [item for item in admissible if item[0] <= minimum + tolerance]
        minimum_xi = min(item[1] for item in score_band)
        tie_band = [item for item in score_band if item[1] <= minimum_xi + tolerance]
        tie_band.sort(key=lambda item: (item[0], item[1], item[2]))
        return ("Admitted", tie_band[0][2])

    @staticmethod
    def _exact_refusal(tags: list[str]) -> str:
        if not tags:
            return "RefusedStalled"
        if all(tag == "RefusedInvalidInput" for tag in tags):
            return "RefusedInvalidInput"
        remaining = [tag for tag in tags if tag != "RefusedInvalidInput"]
        if remaining and all(tag == "RefusedTearing" for tag in remaining):
            return "RefusedTearing"
        if remaining and all(tag == "RefusedDescentViolation" for tag in remaining):
            return "RefusedDescentViolation"
        return "RefusedStalled"


# Backward-compatible alias for existing imports
SecondOrderRepairController = RepairSelectionController

