"""Multi-agent communicating hypergraph over a shared 2-complex (C^1 -> C^2).

AuthorityEffect: None.

Models m >= 2 finite-state transition agents exchanging boundary projections
pi_A(M_k) across a shared 2-complex, demonstrating that coupled co-adaptation
can delay report collision to prod_i N_i, but cannot evade the joint
product-carrier horizon bound k <= prod_i(N_i) + 1.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import math

from eis_verifier import compute_signal1_digest, verify_signal_independence
from single_agent_graph import ObstructionReceipt, compute_phi1_holonomy


@dataclass(frozen=True)
class HypergraphAgentSpec:
    """Finite-state transition agent specification in a communicating hypergraph."""

    agent_id: str
    carrier_capacity: int

    def __post_init__(self) -> None:
        if not self.agent_id.strip():
            raise ValueError("agent_id must be non-empty")
        if (
            isinstance(self.carrier_capacity, bool)
            or not isinstance(self.carrier_capacity, int)
            or self.carrier_capacity <= 0
        ):
            raise ValueError("carrier_capacity N_i must be a positive integer")


@dataclass(frozen=True)
class SharedTwoComplex:
    """Shared 2-complex K = (V, E, T) across which communicating hypergraph agents exchange boundary projections."""

    vertices: tuple[int, ...] = (0, 1, 2)
    triangles: tuple[tuple[int, int, int], ...] = ((0, 1, 2),)
    shared_edges: tuple[tuple[int, int], ...] = ((0, 1), (1, 2), (0, 2))


@dataclass(frozen=True)
class MultiAgentTransitionState:
    """Joint state of m >= 2 finite relational models exchanging boundary projections pi_A(M_k) across a shared 2-complex."""

    step_index: int
    agent_reports: tuple[int, ...]
    joint_internal_eval: int
    remaining_budget: int
    requests_carrier_lift: bool = False
    edge_cochain: dict[tuple[int, int], Fraction] = field(default_factory=dict)
    agent_edge_proposals: dict[str, dict[tuple[int, int], Fraction]] = field(default_factory=dict)
    signal2_observer_id: str = "host.hypergraph_obstruction_gate"


@dataclass(frozen=True)
class HypergraphObstructionReceipt:
    """Exact obstruction termination receipt at step k <= N_A * N_B + 1 for a multi-agent communicating hypergraph."""

    halted: bool
    obstruction_kind: str
    termination_step: int
    agent_capacities: tuple[int, ...]
    product_carrier_capacity: int
    horizon_bound: int
    single_agent_max_capacity: int
    delayed_beyond_single_agent: bool
    colliding_prior_step: int | None
    colliding_joint_report: tuple[int, ...] | None
    remaining_budget: int
    phi1_holonomy: Fraction
    boundary_exchange_trace: tuple[tuple[int, ...], ...]
    eis_vector: dict[str, object]
    eis_independence_verdict: dict[str, object]

    @property
    def carrier_capacity(self) -> int:
        return self.product_carrier_capacity

    def to_obstruction_receipt(self) -> ObstructionReceipt:
        return ObstructionReceipt(
            halted=self.halted,
            obstruction_kind=self.obstruction_kind,
            termination_step=self.termination_step,
            carrier_capacity=self.product_carrier_capacity,
            horizon_bound=self.horizon_bound,
            colliding_prior_step=self.colliding_prior_step,
            remaining_budget=self.remaining_budget,
            phi1_holonomy=self.phi1_holonomy,
            eis_vector=self.eis_vector,
            eis_independence_verdict=self.eis_independence_verdict,
        )


def compute_hypergraph_phi1_holonomy(
    edge_cochain: dict[tuple[int, int], Fraction],
    agent_edge_proposals: dict[str, dict[tuple[int, int], Fraction]],
    shared_complex: SharedTwoComplex,
) -> Fraction:
    """Compute exact rational L1 holonomy Phi_1([delta]) on a shared 2-complex across communicating agents.

    Combines:
    1. Triangle coboundary circulation sum_{(u,v,w) in T} |(d^1 delta)(u,v,w)| on the shared 2-complex.
    2. Inter-agent overlap section disagreement sum_{i < j} sum_{e in E_shared} |delta^{(i)}(e) - delta^{(j)}(e)|.
    All quantities are strictly required to be exact `fractions.Fraction`.
    """
    total = compute_phi1_holonomy(edge_cochain, shared_complex.triangles)
    agent_ids = sorted(agent_edge_proposals.keys())
    for idx_i in range(len(agent_ids)):
        prop_i = agent_edge_proposals[agent_ids[idx_i]]
        for idx_j in range(idx_i + 1, len(agent_ids)):
            prop_j = agent_edge_proposals[agent_ids[idx_j]]
            for edge in shared_complex.shared_edges:
                if edge in prop_i and edge in prop_j:
                    val_i = prop_i[edge]
                    val_j = prop_j[edge]
                    if not isinstance(val_i, Fraction) or not isinstance(val_j, Fraction):
                        raise TypeError("Agent edge cochain proposals must be exact fractions.Fraction")
                    total += abs(val_i - val_j)
    return total


def build_flat_shared_cochain(
    agent_reports: tuple[int, ...],
    shared_complex: SharedTwoComplex = SharedTwoComplex(),
) -> dict[tuple[int, int], Fraction]:
    """Construct an exact 0-coboundary 1-cochain d^0(alpha) on `shared_complex` from exchanged boundary projections."""
    alpha: dict[int, Fraction] = {}
    for idx, v in enumerate(shared_complex.vertices):
        rep = agent_reports[idx % len(agent_reports)]
        alpha[v] = Fraction(int(rep), int(idx + 1))
    cochain: dict[tuple[int, int], Fraction] = {}
    for u, v, w in shared_complex.triangles:
        for src, dst in ((u, v), (v, w), (u, w)):
            cochain[(src, dst)] = alpha.get(dst, Fraction(0, 1)) - alpha.get(src, Fraction(0, 1))
    for src, dst in shared_complex.shared_edges:
        cochain[(src, dst)] = alpha.get(dst, Fraction(0, 1)) - alpha.get(src, Fraction(0, 1))
    return cochain


def coupled_odometer_step_fn(
    agent_capacities: tuple[int, ...],
    shared_complex: SharedTwoComplex = SharedTwoComplex(),
) -> Callable[[MultiAgentTransitionState], MultiAgentTransitionState]:
    """Coupled co-adaptation operator where agents exchange boundary projections pi_A(M_k), pi_B(M_k) across K.

    Agent m-1 advances every step; each upstream agent i advances iff all downstream boundary projections
    pi_j(M_k) (j > i) hit their boundary carry threshold N_j - 1. This co-adaptation delays joint report
    collision past max_i(N_i) to the exact product-carrier bound prod_i(N_i) <= prod_i(N_i) + 1 while
    maintaining exact rational Phi_1([delta]) = 0 on the shared 2-complex.
    """
    product_cap = math.prod(agent_capacities)

    def _step(state: MultiAgentTransitionState) -> MultiAgentTransitionState:
        next_reports = list(state.agent_reports)
        carry = True
        for idx in range(len(agent_capacities) - 1, -1, -1):
            if carry:
                if next_reports[idx] + 1 < agent_capacities[idx]:
                    next_reports[idx] += 1
                    carry = False
                else:
                    next_reports[idx] = 0
                    carry = True
        reports_tuple = tuple(next_reports)
        flat_cochain = build_flat_shared_cochain(reports_tuple, shared_complex)
        return MultiAgentTransitionState(
            step_index=state.step_index + 1,
            agent_reports=reports_tuple,
            joint_internal_eval=(state.joint_internal_eval + 1) % product_cap,
            remaining_budget=state.remaining_budget,
            requests_carrier_lift=state.requests_carrier_lift,
            edge_cochain=flat_cochain,
            agent_edge_proposals={
                f"agent_{i}": dict(flat_cochain) for i in range(len(agent_capacities))
            },
            signal2_observer_id=state.signal2_observer_id,
        )

    return _step


def uncoupled_parallel_step_fn(
    agent_capacities: tuple[int, ...],
    shared_complex: SharedTwoComplex = SharedTwoComplex(),
) -> Callable[[MultiAgentTransitionState], MultiAgentTransitionState]:
    """Uncoupled parallel evolution where each agent updates pi_i(M_{k+1}) = (pi_i(M_k) + 1) mod N_i without cross-reading."""
    product_cap = math.prod(agent_capacities)

    def _step(state: MultiAgentTransitionState) -> MultiAgentTransitionState:
        reports_tuple = tuple(
            (rep + 1) % cap for rep, cap in zip(state.agent_reports, agent_capacities)
        )
        flat_cochain = build_flat_shared_cochain(reports_tuple, shared_complex)
        return MultiAgentTransitionState(
            step_index=state.step_index + 1,
            agent_reports=reports_tuple,
            joint_internal_eval=(state.joint_internal_eval + 1) % product_cap,
            remaining_budget=state.remaining_budget,
            requests_carrier_lift=state.requests_carrier_lift,
            edge_cochain=flat_cochain,
            agent_edge_proposals={
                f"agent_{i}": dict(flat_cochain) for i in range(len(agent_capacities))
            },
            signal2_observer_id=state.signal2_observer_id,
        )

    return _step


class MultiAgentCommunicatingHypergraph:
    """Multi-agent communicating hypergraph of m >= 2 finite-state transition graphs exchanging pi_i(M_k) across a shared 2-complex."""

    def __init__(
        self,
        agents: Sequence[HypergraphAgentSpec],
        initial_lift_budget: int,
        shared_complex: SharedTwoComplex = SharedTwoComplex(),
        detector_id: str = "detector.hypergraph_rsi_scanner",
    ) -> None:
        if len(agents) < 2:
            raise ValueError("MultiAgentCommunicatingHypergraph requires at least 2 agents")
        if (
            isinstance(initial_lift_budget, bool)
            or not isinstance(initial_lift_budget, int)
            or initial_lift_budget < 0
        ):
            raise ValueError("initial_lift_budget B_0 must be a non-negative integer")
        self.agents: tuple[HypergraphAgentSpec, ...] = tuple(agents)
        self.agent_capacities: tuple[int, ...] = tuple(a.carrier_capacity for a in self.agents)
        self.product_carrier_capacity: int = math.prod(self.agent_capacities)
        self.horizon_bound: int = self.product_carrier_capacity + 1
        self.single_agent_max_capacity: int = max(self.agent_capacities)
        self.initial_lift_budget = initial_lift_budget
        self.shared_complex = shared_complex
        self.detector_id = detector_id

    def encode_joint_report(self, agent_reports: tuple[int, ...]) -> int:
        """Bijective mixed-radix encoding of (pi_1(M_k), ..., pi_m(M_k)) into Fin(prod_i N_i)."""
        if len(agent_reports) != len(self.agents):
            raise ValueError(
                f"Expected {len(self.agents)} agent boundary reports, got {len(agent_reports)}"
            )
        code = 0
        for idx, (rep, spec) in enumerate(zip(agent_reports, self.agents)):
            if isinstance(rep, bool) or not isinstance(rep, int) or rep < 0 or rep >= spec.carrier_capacity:
                raise ValueError(
                    f"Agent {spec.agent_id} (index {idx}) report_id {rep} outside Fin({spec.carrier_capacity})"
                )
            code = code * spec.carrier_capacity + rep
        return code

    def run_coupled_trajectory(
        self,
        initial_state: MultiAgentTransitionState,
        step_fn: Callable[[MultiAgentTransitionState], MultiAgentTransitionState],
    ) -> HypergraphObstructionReceipt:
        """Execute coupled transition M_{k+1} = Phi(M_k) and record exact step k <= prod_i(N_i) + 1 of obstruction."""
        seen_joint_reports: dict[int, int] = {}
        exchange_log: list[tuple[int, ...]] = []
        current = initial_state
        budget = self.initial_lift_budget

        for k in range(self.horizon_bound + 1):
            joint_code = self.encode_joint_report(current.agent_reports)
            exchange_log.append(tuple(current.agent_reports))

            # 1. Check Overlap Gluing Refusal on the shared 2-complex: Phi_1([delta_k]) > 0
            phi1 = compute_hypergraph_phi1_holonomy(
                current.edge_cochain, current.agent_edge_proposals, self.shared_complex
            )
            if phi1 > Fraction(0, 1):
                return self._build_hypergraph_receipt(
                    obstruction_kind="OVERLAP_GLUING_REFUSAL",
                    danger_type="PROTECTED_FIELD_VIOLATION",
                    step=k,
                    colliding_prior_step=None,
                    colliding_joint_report=None,
                    remaining_budget=budget,
                    phi1_holonomy=phi1,
                    exchange_log=tuple(exchange_log),
                    observer_id=current.signal2_observer_id,
                    pattern_matched=f"hypergraph_step_{k}_claim_glued_shared_2complex",
                )

            # 2. Check Lift-Budget Exhaustion: requests_carrier_lift when budget == 0
            if current.requests_carrier_lift:
                if budget == 0:
                    return self._build_hypergraph_receipt(
                        obstruction_kind="LIFT_BUDGET_EXHAUSTION",
                        danger_type="MANIFEST_CONTAMINATION",
                        step=k,
                        colliding_prior_step=None,
                        colliding_joint_report=None,
                        remaining_budget=0,
                        phi1_holonomy=phi1,
                        exchange_log=tuple(exchange_log),
                        observer_id=current.signal2_observer_id,
                        pattern_matched=f"hypergraph_step_{k}_claim_unlicensed_product_lift",
                    )
                budget -= 1

            # 3. Check Joint Internal Evaluation Capacity Threshold Exceeded (Goodhart Decoupling)
            if current.joint_internal_eval >= self.product_carrier_capacity:
                return self._build_hypergraph_receipt(
                    obstruction_kind="CAPACITY_THRESHOLD_EXCEEDED",
                    danger_type="REPLAY_FAILURE",
                    step=k,
                    colliding_prior_step=None,
                    colliding_joint_report=tuple(current.agent_reports),
                    remaining_budget=budget,
                    phi1_holonomy=phi1,
                    exchange_log=tuple(exchange_log),
                    observer_id=current.signal2_observer_id,
                    pattern_matched=(
                        f"hypergraph_step_{k}_goodhart_decoupled_joint_eval_{current.joint_internal_eval}"
                    ),
                )

            # 4. Check Joint Product-Carrier Report Collision at k <= N_A * N_B
            if joint_code in seen_joint_reports:
                prior_step = seen_joint_reports[joint_code]
                assert prior_step < k, (
                    f"REPORT_COLLISION requires strict step ordering prior_step ({prior_step}) < k ({k})"
                )
                return self._build_hypergraph_receipt(
                    obstruction_kind="REPORT_COLLISION",
                    danger_type="REPLAY_FAILURE",
                    step=k,
                    colliding_prior_step=prior_step,
                    colliding_joint_report=tuple(current.agent_reports),
                    remaining_budget=budget,
                    phi1_holonomy=phi1,
                    exchange_log=tuple(exchange_log),
                    observer_id=current.signal2_observer_id,
                    pattern_matched=(
                        f"hypergraph_step_{k}_joint_report_{joint_code}_collides_with_step_{prior_step}"
                    ),
                )

            seen_joint_reports[joint_code] = k
            current = step_fn(
                MultiAgentTransitionState(
                    step_index=k,
                    agent_reports=current.agent_reports,
                    joint_internal_eval=current.joint_internal_eval,
                    remaining_budget=budget,
                    requests_carrier_lift=current.requests_carrier_lift,
                    edge_cochain=current.edge_cochain,
                    agent_edge_proposals=current.agent_edge_proposals,
                    signal2_observer_id=current.signal2_observer_id,
                )
            )

        raise RuntimeError(
            "Unreachable: product-carrier pigeonhole forces joint collision by step prod(N_i) <= prod(N_i) + 1"
        )

    def _build_hypergraph_receipt(
        self,
        obstruction_kind: str,
        danger_type: str,
        step: int,
        colliding_prior_step: int | None,
        colliding_joint_report: tuple[int, ...] | None,
        remaining_budget: int,
        phi1_holonomy: Fraction,
        exchange_log: tuple[tuple[int, ...], ...],
        observer_id: str,
        pattern_matched: str,
    ) -> HypergraphObstructionReceipt:
        assert 0 <= step <= self.horizon_bound, (
            f"Step {step} exceeded product horizon N_prod + 1 = {self.horizon_bound}"
        )
        matches: list[dict[str, object]] = [
            {
                "epitope_name": f"rsi.hypergraph.{obstruction_kind.lower()}",
                "pattern_matched": pattern_matched,
                "offset": 0,
            }
        ]
        caps_str = "x".join(str(c) for c in self.agent_capacities)
        evidence_payload = (
            f"hypergraph_obstruction={obstruction_kind};step={step};"
            f"caps={caps_str};N_prod={self.product_carrier_capacity};"
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
            "agent_capacities": list(self.agent_capacities),
        }
        verdict = verify_signal_independence(matches, danger, context)
        return HypergraphObstructionReceipt(
            halted=True,
            obstruction_kind=obstruction_kind,
            termination_step=step,
            agent_capacities=self.agent_capacities,
            product_carrier_capacity=self.product_carrier_capacity,
            horizon_bound=self.horizon_bound,
            single_agent_max_capacity=self.single_agent_max_capacity,
            delayed_beyond_single_agent=(step > self.single_agent_max_capacity),
            colliding_prior_step=colliding_prior_step,
            colliding_joint_report=colliding_joint_report,
            remaining_budget=remaining_budget,
            phi1_holonomy=phi1_holonomy,
            boundary_exchange_trace=exchange_log,
            eis_vector=eis_vector,
            eis_independence_verdict=verdict,
        )
