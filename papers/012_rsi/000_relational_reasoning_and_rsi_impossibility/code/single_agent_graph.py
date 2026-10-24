"""Single-agent finite-state self-modifying transition graph.

AuthorityEffect: None.

Instantiates finite-state self-modifying transition graphs over container-free relational
carriers and records the exact step k <= N + 1 at which report collision, internal capacity
threshold exceeded, lift-budget exhaustion, or overlap gluing refusal occurs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib

from eis_verifier import compute_signal1_digest, verify_signal_independence


@dataclass(frozen=True)
class TransitionState:
    """State of a finite relational model at step k."""

    step_index: int
    report_id: int
    internal_eval: int
    remaining_budget: int
    requests_carrier_lift: bool = False
    edge_cochain: dict[tuple[int, int], Fraction] = field(default_factory=dict)
    signal2_observer_id: str = "host.rsi_obstruction_gate"


@dataclass(frozen=True)
class ObstructionReceipt:
    """Exact obstruction termination receipt at step k <= N + 1."""

    halted: bool
    obstruction_kind: str
    termination_step: int
    carrier_capacity: int
    horizon_bound: int
    colliding_prior_step: int | None
    remaining_budget: int
    phi1_holonomy: Fraction
    eis_vector: dict[str, object]
    eis_independence_verdict: dict[str, object]


def compute_d1_triangle(
    cochain: dict[tuple[int, int], Fraction], u: int, v: int, w: int
) -> Fraction:
    """Exact 1-coboundary (d^1 delta)(u, v, w) = delta(u, v) + delta(v, w) - delta(u, w)."""
    duv = cochain.get((u, v), Fraction(0, 1))
    dvw = cochain.get((v, w), Fraction(0, 1))
    duw = cochain.get((u, w), Fraction(0, 1))
    return duv + dvw - duw


def compute_phi1_holonomy(
    cochain: dict[tuple[int, int], Fraction],
    triangles: tuple[tuple[int, int, int], ...],
) -> Fraction:
    """Exact rational L1 coboundary holonomy functional Phi_1([delta]) = sum_{t in T} |d^1 delta(t)|."""
    total = Fraction(0, 1)
    for u, v, w in triangles:
        val = compute_d1_triangle(cochain, u, v, w)
        if not isinstance(val, Fraction):
            raise TypeError("Cochain values must be exact fractions.Fraction")
        total += abs(val)
    return total


class FiniteStateSelfModifyingGraph:
    """Finite-state self-modifying transition graph over a relational carrier of capacity N."""

    def __init__(
        self,
        carrier_capacity: int,
        initial_lift_budget: int,
        triangles: tuple[tuple[int, int, int], ...] = ((0, 1, 2),),
        detector_id: str = "detector.rsi_claim_scanner",
    ) -> None:
        if isinstance(carrier_capacity, bool) or not isinstance(carrier_capacity, int) or carrier_capacity <= 0:
            raise ValueError("carrier_capacity N must be a positive integer")
        if isinstance(initial_lift_budget, bool) or not isinstance(initial_lift_budget, int) or initial_lift_budget < 0:
            raise ValueError("initial_lift_budget B_0 must be a non-negative integer")
        self.carrier_capacity = carrier_capacity
        self.initial_lift_budget = initial_lift_budget
        self.triangles = triangles
        self.detector_id = detector_id

    def run_trajectory(
        self,
        initial_state: TransitionState,
        step_fn: Callable[[TransitionState], TransitionState],
    ) -> ObstructionReceipt:
        """Execute M_{k+1} = Phi(M_k) and record the exact step k <= N + 1 at which refusal occurs."""
        horizon_bound = self.carrier_capacity + 1
        seen_reports: dict[int, int] = {}
        current = initial_state
        budget = self.initial_lift_budget

        for k in range(horizon_bound + 1):
            if current.report_id < 0 or current.report_id >= self.carrier_capacity:
                raise ValueError(
                    f"report_id {current.report_id} outside finite carrierFin({self.carrier_capacity})"
                )

            # 1. Check Overlap Gluing Refusal: Phi_1([delta_k]) > 0
            phi1 = compute_phi1_holonomy(current.edge_cochain, self.triangles)
            if phi1 > Fraction(0, 1):
                return self._build_receipt(
                    obstruction_kind="OVERLAP_GLUING_REFUSAL",
                    danger_type="PROTECTED_FIELD_VIOLATION",
                    step=k,
                    colliding_prior_step=None,
                    remaining_budget=budget,
                    phi1_holonomy=phi1,
                    observer_id=current.signal2_observer_id,
                    pattern_matched=f"step_{k}_claim_glued_section",
                )

            # 2. Check Lift-Budget Exhaustion: requests_carrier_lift when budget == 0
            if current.requests_carrier_lift:
                if budget == 0:
                    return self._build_receipt(
                        obstruction_kind="LIFT_BUDGET_EXHAUSTION",
                        danger_type="MANIFEST_CONTAMINATION",
                        step=k,
                        colliding_prior_step=None,
                        remaining_budget=0,
                        phi1_holonomy=phi1,
                        observer_id=current.signal2_observer_id,
                        pattern_matched=f"step_{k}_claim_unlicensed_carrier_lift",
                    )
                budget -= 1

            # 3. Check Internal Evaluation Capacity Threshold Exceeded (Goodhart Decoupling)
            if current.internal_eval >= self.carrier_capacity:
                return self._build_receipt(
                    obstruction_kind="CAPACITY_THRESHOLD_EXCEEDED",
                    danger_type="REPLAY_FAILURE",
                    step=k,
                    colliding_prior_step=None,
                    remaining_budget=budget,
                    phi1_holonomy=phi1,
                    observer_id=current.signal2_observer_id,
                    pattern_matched=f"step_{k}_goodhart_decoupled_eval_{current.internal_eval}",
                )

            # 4. Check Report Collision (i < j with report(M_i) == report(M_j))
            if current.report_id in seen_reports:
                prior_step = seen_reports[current.report_id]
                assert prior_step < k, (
                    f"REPORT_COLLISION requires strict step ordering prior_step ({prior_step}) < k ({k})"
                )
                return self._build_receipt(
                    obstruction_kind="REPORT_COLLISION",
                    danger_type="REPLAY_FAILURE",
                    step=k,
                    colliding_prior_step=prior_step,
                    remaining_budget=budget,
                    phi1_holonomy=phi1,
                    observer_id=current.signal2_observer_id,
                    pattern_matched=f"step_{k}_claim_strict_dominance_over_step_{prior_step}",
                )

            seen_reports[current.report_id] = k
            current = step_fn(
                TransitionState(
                    step_index=k,
                    report_id=current.report_id,
                    internal_eval=current.internal_eval,
                    remaining_budget=budget,
                    requests_carrier_lift=current.requests_carrier_lift,
                    edge_cochain=current.edge_cochain,
                    signal2_observer_id=current.signal2_observer_id,
                )
            )

        raise RuntimeError("Unreachable: pigeonhole principle forces collision by step N <= N + 1")

    def _build_receipt(
        self,
        obstruction_kind: str,
        danger_type: str,
        step: int,
        colliding_prior_step: int | None,
        remaining_budget: int,
        phi1_holonomy: Fraction,
        observer_id: str,
        pattern_matched: str,
    ) -> ObstructionReceipt:
        horizon_bound = self.carrier_capacity + 1
        assert 0 <= step <= horizon_bound, f"Step {step} exceeded N + 1 = {horizon_bound}"

        matches: list[dict[str, object]] = [
            {
                "epitope_name": f"rsi.{obstruction_kind.lower()}",
                "pattern_matched": pattern_matched,
                "offset": 0,
            }
        ]
        evidence_payload = (
            f"obstruction={obstruction_kind};step={step};N={self.carrier_capacity};"
            f"prior={colliding_prior_step};budget={remaining_budget};"
            f"phi1={phi1_holonomy.numerator}/{phi1_holonomy.denominator}"
        ).encode("utf-8")
        evidence_digest = "sha256:" + hashlib.sha256(evidence_payload).hexdigest()

        danger: dict[str, object] = {
            "danger_type": danger_type,
            "observer_id": observer_id,
            "evidence_digest": evidence_digest,
            "defect_count": 1,
            "evidence_spans": [[128, 192]],
        }
        context: dict[str, object] = {
            "detector_id": self.detector_id,
            "detector_predicates": ["UNREGISTERED_SELF_PROXY"],
            "offsets_are_content": True,
        }
        eis_vector: dict[str, object] = {
            "matches": matches,
            "danger": danger,
            "context": context,
            "signal1_digest": compute_signal1_digest(matches),
        }
        verdict = verify_signal_independence(matches, danger, context)
        return ObstructionReceipt(
            halted=True,
            obstruction_kind=obstruction_kind,
            termination_step=step,
            carrier_capacity=self.carrier_capacity,
            horizon_bound=horizon_bound,
            colliding_prior_step=colliding_prior_step,
            remaining_budget=remaining_budget,
            phi1_holonomy=phi1_holonomy,
            eis_vector=eis_vector,
            eis_independence_verdict=verdict,
        )
