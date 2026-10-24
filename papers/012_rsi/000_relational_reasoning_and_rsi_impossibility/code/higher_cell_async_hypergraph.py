"""Higher k-cell asynchronous communicating hypergraph with non-monotonic channels and dynamic rewiring.

AuthorityEffect: None.

Extends multi-agent communicating hypergraphs from shared 2-complexes to arbitrary
degree k >= 1 cochain complexes (C^k(X_t) -> C^{k+1}(X_t)) coupled with:
1. `AsynchronousMessageDelayBuffer` (monotonic FIFO latency tau >= 0),
2. `NonMonotonicMessageChannel` (packet-loss hold-last-delivered and non-FIFO permutations), and
3. `DynamicSimplicialRewiringSchedule` (time-varying simplicial complexes).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import math

from communication_channels import AsynchronousMessageDelayBuffer, NonMonotonicMessageChannel
from eis_verifier import (
    compute_signal1_digest,
    cross_check_eis_metadata_against_rust,
    verify_signal_independence,
)
from exact_dual_witness_solver import (
    solve_exact_rational_l1_dual_witness,
    verify_exact_l1_repair,
)
from simplicial_complex import (
    HigherCellComplex,
    build_exact_k_cochain_from_potential,
    compute_higher_cell_phi1_holonomy,
)
from simplicial_rewiring import DynamicSimplicialRewiringSchedule


@dataclass(frozen=True)
class HigherCellAsyncState:
    """Joint multi-agent state at step `k` over a higher k-cell complex with asynchronous/non-monotonic latency and dynamic rewiring."""

    step: int
    agent_states: tuple[int, ...]
    emitted_projections: tuple[int, ...]
    delivered_projections: tuple[int, ...]
    effective_lags: tuple[int, ...]
    remaining_budget: int
    k_cochain: dict[tuple[int, ...], Fraction]
    delivered_source_steps: tuple[int, ...] = ()
    active_k_plus_1_cells: tuple[tuple[int, ...], ...] = ()
    is_non_monotonic_delivery: bool = False
    is_topology_rewired: bool = False


@dataclass(frozen=True)
class HigherCellObstructionReceipt:
    """Deterministic refusal receipt emitted by a `HigherCellAsyncCommunicatingHypergraph`."""

    halted: bool
    obstruction_kind: str
    termination_step: int
    cochain_degree: int
    latency_steps: tuple[int, ...]
    agent_capacities: tuple[int, ...]
    product_carrier_capacity: int
    horizon_bound: int
    single_agent_max_capacity: int
    delayed_beyond_single_agent: bool
    colliding_prior_step: int | None
    colliding_joint_report: tuple[int, ...] | None
    remaining_budget: int
    phi1_holonomy: Fraction
    async_exchange_trace: list[dict[str, object]]
    eis_vector: dict[str, object]
    eis_independence_verdict: dict[str, object]
    non_monotonic_inversions: int = 0
    topology_rewiring_events: int = 0
    channel_mode: str = "fifo"
    repair_events_count: int = 0
    total_repair_budget_expended: int = 0
    last_repair_l1_cost: Fraction | None = None

    @property
    def carrier_capacity(self) -> int:
        """Compatibility property returning `product_carrier_capacity` for EIS cross-check."""
        return self.product_carrier_capacity

    def to_json_dict(self) -> dict[str, object]:
        """Serialize receipt to a deterministic JSON-compatible dictionary."""
        return {
            "halted": self.halted,
            "obstruction_kind": self.obstruction_kind,
            "termination_step": self.termination_step,
            "cochain_degree": self.cochain_degree,
            "latency_steps": list(self.latency_steps),
            "agent_capacities": list(self.agent_capacities),
            "product_carrier_capacity": self.product_carrier_capacity,
            "horizon_bound": self.horizon_bound,
            "single_agent_max_capacity": self.single_agent_max_capacity,
            "delayed_beyond_single_agent": self.delayed_beyond_single_agent,
            "colliding_prior_step": self.colliding_prior_step,
            "colliding_joint_report": (
                list(self.colliding_joint_report)
                if self.colliding_joint_report is not None
                else None
            ),
            "remaining_budget": self.remaining_budget,
            "phi1_holonomy": f"{self.phi1_holonomy.numerator}/{self.phi1_holonomy.denominator}",
            "non_monotonic_inversions": self.non_monotonic_inversions,
            "topology_rewiring_events": self.topology_rewiring_events,
            "channel_mode": self.channel_mode,
            "repair_events_count": self.repair_events_count,
            "total_repair_budget_expended": self.total_repair_budget_expended,
            "last_repair_l1_cost": (
                f"{self.last_repair_l1_cost.numerator}/{self.last_repair_l1_cost.denominator}"
                if self.last_repair_l1_cost is not None
                else None
            ),
            "async_exchange_trace": self.async_exchange_trace,
            "eis_vector": self.eis_vector,
            "eis_independence_verdict": self.eis_independence_verdict,
        }


class HigherCellAsyncCommunicatingHypergraph:
    """Multi-agent communicating hypergraph over `C^k --d^k--> C^{k+1}` with asynchronous, non-monotonic, and dynamically rewired topologies.

    Extends `MultiAgentCommunicatingHypergraph` from shared 2-complexes (`C^1 --d^1--> C^2`) to
    arbitrary degree `k >= 1` cochain complexes (`C^k(X_t) --d_t^k--> C^{k+1}(X_t)`) coupled with:
      1. `AsynchronousMessageDelayBuffer` (monotonic FIFO latency `tau >= 0`),
      2. `NonMonotonicMessageChannel` (packet-loss hold-last-delivered and non-FIFO out-of-order
         message permutations `0 <= sigma_a(k) <= k`), and
      3. `DynamicSimplicialRewiringSchedule` (time-varying `(k+1)`-complexes `X_t`).
    """

    def __init__(
        self,
        agent_capacities: Sequence[int],
        higher_complex: HigherCellComplex,
        latency_steps: int | Sequence[int],
        initial_agent_states: Sequence[int],
        initial_budget: int,
        initial_k_cochain: Mapping[tuple[int, ...], Fraction],
        step_fn: Callable[
            [HigherCellAsyncState],
            tuple[tuple[int, ...], Mapping[tuple[int, ...], Fraction]],
        ],
        boundary_maps: Sequence[Callable[[int], int]] | None = None,
        detector_id: str = "detector.higher_cell_async_rsi_scanner",
        signal2_observer_id: str = "host.higher_cell_async_obstruction_gate",
        message_channel: NonMonotonicMessageChannel | None = None,
        rewiring_schedule: DynamicSimplicialRewiringSchedule | None = None,
        enable_active_repair: bool = False,
        repair_budget_cost_fn: Callable[[Fraction], int] | None = None,
    ) -> None:
        if len(agent_capacities) < 2:
            raise ValueError(
                f"HigherCellAsyncCommunicatingHypergraph requires >= 2 agents, got {len(agent_capacities)}"
            )
        for idx, cap in enumerate(agent_capacities):
            if cap < 1:
                raise ValueError(f"Agent {idx} capacity must be >= 1, got {cap}")
        if len(initial_agent_states) != len(agent_capacities):
            raise ValueError("initial_agent_states length must match agent_capacities length")
        if initial_budget < 0:
            raise ValueError(f"initial_budget must be >= 0, got {initial_budget}")

        self.agent_capacities: tuple[int, ...] = tuple(int(c) for c in agent_capacities)
        self.higher_complex = higher_complex
        if rewiring_schedule is not None and rewiring_schedule.degree != higher_complex.degree:
            raise ValueError(
                f"rewiring_schedule degree {rewiring_schedule.degree} != higher_complex degree {higher_complex.degree}"
            )
        self.rewiring_schedule = rewiring_schedule
        self.delay_buffer = AsynchronousMessageDelayBuffer(
            num_agents=len(self.agent_capacities),
            latency_steps=latency_steps,
        )
        self.message_channel = message_channel
        self.initial_agent_states: tuple[int, ...] = tuple(
            int(s) % cap for s, cap in zip(initial_agent_states, self.agent_capacities)
        )
        self.initial_budget = int(initial_budget)
        self.initial_k_cochain: dict[tuple[int, ...], Fraction] = {
            cell: Fraction(val) for cell, val in initial_k_cochain.items()
        }
        self.step_fn = step_fn
        if boundary_maps is None:
            self.boundary_maps: tuple[Callable[[int], int], ...] = tuple(
                (lambda s, cap=cap: s % cap) for cap in self.agent_capacities
            )
        else:
            if len(boundary_maps) != len(self.agent_capacities):
                raise ValueError("boundary_maps length must match agent_capacities length")
            self.boundary_maps = tuple(boundary_maps)
        self.detector_id = detector_id
        self.signal2_observer_id = signal2_observer_id
        self.enable_active_repair = bool(enable_active_repair)
        self.repair_budget_cost_fn = (
            repair_budget_cost_fn
            if repair_budget_cost_fn is not None
            else (lambda cost: max(1, int(math.ceil(cost))) if cost > Fraction(0, 1) else 0)
        )

    @property
    def product_carrier_capacity(self) -> int:
        """Joint product-carrier capacity `prod_i N_i` (e.g. `N_A * N_B`)."""
        return math.prod(self.agent_capacities)

    @property
    def horizon_bound(self) -> int:
        """Maximum admissible step count `prod_i N_i + 1`."""
        return self.product_carrier_capacity + 1

    @property
    def single_agent_max_capacity(self) -> int:
        """Maximum individual agent carrier capacity `max_i N_i`."""
        return max(self.agent_capacities)

    def _project_joint_boundary(self, agent_states: tuple[int, ...]) -> tuple[int, ...]:
        """Compute authoritative joint boundary report `(pi_0(s_0), ..., pi_{m-1}(s_{m-1}))`."""
        return tuple(
            int(proj_fn(state)) % cap
            for proj_fn, state, cap in zip(
                self.boundary_maps, agent_states, self.agent_capacities
            )
        )

    def _active_complex_at(self, step: int) -> HigherCellComplex:
        """Return the active `(k+1)`-complex at `step`."""
        if self.rewiring_schedule is not None:
            return self.rewiring_schedule.complex_at(step)
        return self.higher_complex

    def run(self) -> HigherCellObstructionReceipt:
        """Execute the higher k-cell hypergraph until the first obstruction at `k* <= prod_i N_i + 1`."""
        if self.message_channel is not None:
            self.message_channel.reset()
        else:
            self.delay_buffer.reset()
        seen_joint_reports: dict[tuple[int, ...], int] = {}
        exchange_log: list[dict[str, object]] = []

        agent_states = self.initial_agent_states
        budget = self.initial_budget
        k_cochain = dict(self.initial_k_cochain)
        rewiring_events = 0
        repair_events = 0
        total_repair_budget_expended = 0
        last_repair_l1_cost: Fraction | None = None

        for step in range(self.horizon_bound + 1):
            emitted_report = self._project_joint_boundary(agent_states)
            if self.message_channel is not None:
                (
                    delivered_report,
                    effective_lags,
                    source_steps,
                    is_non_monotonic,
                ) = self.message_channel.record_and_deliver_detailed(step, emitted_report)
            else:
                delivered_report, effective_lags = self.delay_buffer.record_and_deliver(
                    step, emitted_report
                )
                source_steps = tuple(step - lag for lag in effective_lags)
                is_non_monotonic = False

            active_complex = self._active_complex_at(step)
            is_rewired = (
                self.rewiring_schedule.is_rewired_at(step)
                if self.rewiring_schedule is not None
                else False
            )
            if is_rewired:
                rewiring_events += 1

            # Ensure all required k-cells of the active complex exist in k_cochain (defaulting missing newly attached faces to 0)
            for req_face in active_complex.required_k_cells():
                if req_face not in k_cochain:
                    k_cochain[req_face] = Fraction(0, 1)

            phi1_val = compute_higher_cell_phi1_holonomy(active_complex, k_cochain)

            exchange_log.append(
                {
                    "step": step,
                    "cochain_degree": active_complex.degree,
                    "active_k_plus_1_cells": [list(c) for c in active_complex.k_plus_1_cells],
                    "is_topology_rewired": is_rewired,
                    "agent_states": list(agent_states),
                    "emitted_boundary_projections": list(emitted_report),
                    "delivered_boundary_projections": list(delivered_report),
                    "delivered_source_steps": list(source_steps),
                    "effective_lags": list(effective_lags),
                    "is_non_monotonic_delivery": is_non_monotonic,
                    "remaining_budget": budget,
                    "phi1_holonomy": f"{phi1_val.numerator}/{phi1_val.denominator}",
                }
            )

            # 1. Check higher k-cell overlap gluing compatibility (Phi_1([delta^{(k)}]) > 0)
            if phi1_val > Fraction(0, 1):
                if self.enable_active_repair:
                    repair_res = solve_exact_rational_l1_dual_witness(active_complex, k_cochain)
                    if not verify_exact_l1_repair(active_complex, k_cochain, repair_res):
                        raise ValueError("Active repair certificate rejected")
                    budget_cost = self.repair_budget_cost_fn(repair_res.l1_repair_cost)
                    if type(budget_cost) is not int or budget_cost < 0:
                        raise ValueError("Repair price must be an exact nonnegative integer")
                    if repair_res.l1_repair_cost > 0 and budget_cost == 0:
                        raise ValueError("Nonzero repair requires a positive license price")
                    if budget >= budget_cost:
                        budget -= budget_cost
                        total_repair_budget_expended += budget_cost
                        repair_events += 1
                        last_repair_l1_cost = repair_res.l1_repair_cost
                        k_cochain = dict(repair_res.repaired_cochain)
                        phi1_val = Fraction(0, 1)
                        exchange_log.append(
                            {
                                "event": "active_cochain_repair",
                                "step": step,
                                "l1_repair_cost": f"{repair_res.l1_repair_cost.numerator}/{repair_res.l1_repair_cost.denominator}",
                                "budget_cost": budget_cost,
                                "remaining_budget": budget,
                                "dual_objective": f"{repair_res.dual_objective.numerator}/{repair_res.dual_objective.denominator}",
                                "duality_gap": f"{repair_res.duality_gap.numerator}/{repair_res.duality_gap.denominator}",
                                "dual_witness": {
                                    str(k): f"{v.numerator}/{v.denominator}"
                                    for k, v in repair_res.dual_witness.items()
                                },
                            }
                        )
                    else:
                        # Insufficient budget to repair defect: terminates via lift budget exhaustion!
                        return self._emit_receipt(
                            obstruction_kind="LIFT_BUDGET_EXHAUSTION",
                            danger_type="MANIFEST_CONTAMINATION",
                            step=step,
                            colliding_prior_step=None,
                            colliding_joint_report=None,
                            remaining_budget=budget,
                            phi1_holonomy=phi1_val,
                            exchange_log=exchange_log,
                            pattern_matched=(
                                f"higher_cell_c{active_complex.degree}_step_{step}_repair_budget_exhaustion"
                            ),
                            rewiring_events=rewiring_events,
                            repair_events_count=repair_events,
                            total_repair_budget_expended=total_repair_budget_expended,
                            last_repair_l1_cost=last_repair_l1_cost,
                        )
                else:
                    return self._emit_receipt(
                        obstruction_kind="OVERLAP_GLUING_REFUSAL",
                        danger_type="PROTECTED_FIELD_VIOLATION",
                        step=step,
                        colliding_prior_step=None,
                        colliding_joint_report=None,
                        remaining_budget=budget,
                        phi1_holonomy=phi1_val,
                        exchange_log=exchange_log,
                        pattern_matched=(
                            f"higher_cell_c{active_complex.degree}_step_{step}_gluing_refusal"
                        ),
                        rewiring_events=rewiring_events,
                        repair_events_count=repair_events,
                        total_repair_budget_expended=total_repair_budget_expended,
                        last_repair_l1_cost=last_repair_l1_cost,
                    )

            # 2. Check authoritative joint boundary report collision (Pi(M_k) = Pi(M_j) for j < k)
            if emitted_report in seen_joint_reports:
                prior_step = seen_joint_reports[emitted_report]
                assert prior_step < step, (
                    f"REPORT_COLLISION requires strict step ordering prior_step ({prior_step}) < step ({step})"
                )
                return self._emit_receipt(
                    obstruction_kind="REPORT_COLLISION",
                    danger_type="REPLAY_FAILURE",
                    step=step,
                    colliding_prior_step=prior_step,
                    colliding_joint_report=emitted_report,
                    remaining_budget=budget,
                    phi1_holonomy=phi1_val,
                    exchange_log=exchange_log,
                    pattern_matched=(
                        f"higher_cell_c{active_complex.degree}_step_{step}_collision_with_{prior_step}"
                    ),
                    rewiring_events=rewiring_events,
                    repair_events_count=repair_events,
                    total_repair_budget_expended=total_repair_budget_expended,
                    last_repair_l1_cost=last_repair_l1_cost,
                )
            seen_joint_reports[emitted_report] = step

            # 3. Check joint lift-budget exhaustion (budget = 0)
            if budget == 0:
                return self._emit_receipt(
                    obstruction_kind="LIFT_BUDGET_EXHAUSTION",
                    danger_type="MANIFEST_CONTAMINATION",
                    step=step,
                    colliding_prior_step=None,
                    colliding_joint_report=None,
                    remaining_budget=0,
                    phi1_holonomy=phi1_val,
                    exchange_log=exchange_log,
                    pattern_matched=(
                        f"higher_cell_c{active_complex.degree}_step_{step}_budget_exhaustion"
                    ),
                    rewiring_events=rewiring_events,
                    repair_events_count=repair_events,
                    total_repair_budget_expended=total_repair_budget_expended,
                    last_repair_l1_cost=last_repair_l1_cost,
                )

            current_state = HigherCellAsyncState(
                step=step,
                agent_states=agent_states,
                emitted_projections=emitted_report,
                delivered_projections=delivered_report,
                effective_lags=effective_lags,
                remaining_budget=budget,
                k_cochain=k_cochain,
                delivered_source_steps=source_steps,
                active_k_plus_1_cells=active_complex.k_plus_1_cells,
                is_non_monotonic_delivery=is_non_monotonic,
                is_topology_rewired=is_rewired,
            )
            next_states, next_cochain = self.step_fn(current_state)
            if len(next_states) != len(self.agent_capacities):
                raise ValueError(
                    f"step_fn returned {len(next_states)} states, expected {len(self.agent_capacities)}"
                )
            agent_states = tuple(
                int(s) % cap for s, cap in zip(next_states, self.agent_capacities)
            )
            budget -= 1
            k_cochain = {cell: Fraction(val) for cell, val in next_cochain.items()}

        raise RuntimeError(
            "Unreachable: joint pigeonhole bound forces collision or budget exhaustion within prod_i N_i + 1 steps"
        )

    def _emit_receipt(
        self,
        obstruction_kind: str,
        danger_type: str,
        step: int,
        colliding_prior_step: int | None,
        colliding_joint_report: tuple[int, ...] | None,
        remaining_budget: int,
        phi1_holonomy: Fraction,
        exchange_log: list[dict[str, object]],
        pattern_matched: str,
        rewiring_events: int = 0,
        repair_events_count: int = 0,
        total_repair_budget_expended: int = 0,
        last_repair_l1_cost: Fraction | None = None,
    ) -> HigherCellObstructionReceipt:
        assert 0 <= step <= self.horizon_bound, (
            f"Higher-cell async termination step {step} exceeded N_A * N_B + 1 = {self.horizon_bound}"
        )
        matches: list[dict[str, object]] = [
            {
                "epitope_name": f"rsi.higher_cell_c{self.higher_complex.degree}.{obstruction_kind.lower()}",
                "pattern_matched": pattern_matched,
                "offset": 0,
            }
        ]
        caps_str = "x".join(str(c) for c in self.agent_capacities)
        active_latencies = (
            self.message_channel.latency_per_agent
            if self.message_channel is not None
            else self.delay_buffer.latency_per_agent
        )
        non_mono_inversions = (
            self.message_channel.non_monotonic_inversion_count
            if self.message_channel is not None
            else 0
        )
        base_mode = (
            self.message_channel.channel_mode if self.message_channel is not None else "fifo"
        )
        channel_mode = (
            f"{base_mode}+rewired" if self.rewiring_schedule is not None else base_mode
        )
        lags_str = ",".join(str(tau) for tau in active_latencies)
        evidence_payload = (
            f"higher_cell_obstruction={obstruction_kind};degree={self.higher_complex.degree};"
            f"mode={channel_mode};tau={lags_str};step={step};caps={caps_str};"
            f"N_prod={self.product_carrier_capacity};prior={colliding_prior_step};"
            f"budget={remaining_budget};inversions={non_mono_inversions};"
            f"rewirings={rewiring_events};"
            f"phi1={phi1_holonomy.numerator}/{phi1_holonomy.denominator}"
        ).encode("utf-8")
        evidence_digest = "sha256:" + hashlib.sha256(evidence_payload).hexdigest()

        danger: dict[str, object] = {
            "danger_type": danger_type,
            "observer_id": self.signal2_observer_id,
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
        return HigherCellObstructionReceipt(
            halted=True,
            obstruction_kind=obstruction_kind,
            termination_step=step,
            cochain_degree=self.higher_complex.degree,
            latency_steps=active_latencies,
            agent_capacities=self.agent_capacities,
            product_carrier_capacity=self.product_carrier_capacity,
            horizon_bound=self.horizon_bound,
            single_agent_max_capacity=self.single_agent_max_capacity,
            delayed_beyond_single_agent=(step > self.single_agent_max_capacity),
            colliding_prior_step=colliding_prior_step,
            colliding_joint_report=colliding_joint_report,
            remaining_budget=remaining_budget,
            phi1_holonomy=phi1_val if (phi1_val := phi1_holonomy) is not None else Fraction(0, 1),
            async_exchange_trace=exchange_log,
            eis_vector=eis_vector,
            eis_independence_verdict=verdict,
            non_monotonic_inversions=non_mono_inversions,
            topology_rewiring_events=rewiring_events,
            channel_mode=channel_mode,
            repair_events_count=repair_events_count,
            total_repair_budget_expended=total_repair_budget_expended,
            last_repair_l1_cost=last_repair_l1_cost,
        )


def run_multi_epoch_lexicographical_descent(
    hg: HigherCellAsyncCommunicatingHypergraph,
) -> tuple[HigherCellObstructionReceipt, list[tuple[int, int]], bool]:
    """Execute hypergraph under multi-epoch lexicographical descent on (B, r) in Nat x Nat.

    Tracks at each step k:
        (B_k, r_k)
    where:
        B_k = remaining_budget
        r_k = within-epoch remaining steps (hg.product_carrier_capacity - 1 - (step % hg.product_carrier_capacity))

    Verifies that every transition (B_k, r_k) -> (B_{k+1}, r_{k+1}) satisfies:
        BudgetedDescentStep: (B' < B) or (B' == B and r' < r).
    """
    receipt = hg.run()
    trace = receipt.async_exchange_trace
    descent_states: list[tuple[int, int]] = []
    prod_cap = hg.product_carrier_capacity

    for entry in trace:
        b_val = int(entry["remaining_budget"])
        step_val = int(entry["step"])
        r_val = prod_cap - 1 - (step_val % prod_cap)
        descent_states.append((b_val, r_val))

    # Verify well-founded lexicographic descent between consecutive logged steps
    valid_descent = True
    for i in range(len(descent_states) - 1):
        b_cur, r_cur = descent_states[i]
        b_next, r_next = descent_states[i + 1]
        is_step_valid = (b_next < b_cur) or (b_next == b_cur and r_next < r_cur)
        if not is_step_valid:
            valid_descent = False
            break

    return receipt, descent_states, valid_descent


def make_async_delay_compensated_step_fn(
    agent_capacities: Sequence[int],
    higher_complex: HigherCellComplex,
) -> Callable[
    [HigherCellAsyncState],
    tuple[tuple[int, ...], dict[tuple[int, ...], Fraction]],
]:
    """Build a delay-compensated co-adaptation step function on `C^k --d^k--> C^{k+1}`.

    - Agents update their local states using the *delayed* boundary projections
      `delivered_projections = (hat{pi}_A(k), hat{pi}_B(k), ...)` received from the
      `AsynchronousMessageDelayBuffer`:
      - Agent 0 advances at every step: `s_0' = (s_0 + 1) mod N_0`.
      - Agent `i > 0` increments when the delayed lower-agent projections `hat{pi}_0(k), ..., hat{pi}_{i-1}(k)`
        all wrap at their maximal residues `N_j - 1`, plus a latency-sensitive phase shift when
        `effective_lags[i-1] > 0` and `hat{pi}_{i-1}(k) == (N_{i-1} - 1 - effective_lags[i-1]) % N_{i-1}`.
    - Both agents construct the next `k`-cochain `delta^{(k)} = d^{k-1} eta^{(k-1)}` from the shared
      delayed potential `eta^{(k-1)}` so that `d^k delta^{(k)} = 0` (`Phi_1([delta^{(k)}]) = 0`).
    - Consequently, varying the communication latency `tau` alters the exact trajectory and shifts
      the step `k*(tau)` at which `REPORT_COLLISION` occurs, while strictly obeying `k*(tau) <= prod_i N_i + 1`.
    """
    caps = tuple(int(c) for c in agent_capacities)
    prod_cap = math.prod(caps)
    sorted_km1_cells = sorted(higher_complex.required_k_minus_1_cells())

    def _step(
        state: HigherCellAsyncState,
    ) -> tuple[tuple[int, ...], dict[tuple[int, ...], Fraction]]:
        next_list = list(state.agent_states)
        delivered = state.delivered_projections
        lags = state.effective_lags

        # Agent 0 always steps forward
        next_list[0] = (state.agent_states[0] + 1) % caps[0]

        for idx in range(1, len(caps)):
            # Carry trigger driven by the delayed projection received across the buffer
            prev_delivered = delivered[idx - 1]
            prev_lag = lags[idx - 1]
            if prev_lag == 0:
                carry = all(delivered[j] == caps[j] - 1 for j in range(idx))
                stride = 1 if carry else 0
            else:
                # Under non-zero communication lag tau > 0, delayed feedback couples current and lagged residues
                trigger_residue = (caps[idx - 1] - 1) % caps[idx - 1]
                secondary_residue = (caps[idx - 1] - 1 - (prev_lag % caps[idx - 1])) % caps[idx - 1]
                if prev_delivered == trigger_residue:
                    stride = 1
                elif prev_delivered == secondary_residue and state.step >= prev_lag:
                    stride = 2 if caps[idx] > 2 else 1
                else:
                    stride = 0
            next_list[idx] = (state.agent_states[idx] + stride) % caps[idx]

        # Build an exact k-cochain delta^{(k)} = d^{k-1} eta^{(k-1)} from the delayed common-knowledge buffer
        delayed_sum = sum(delivered)
        potential: dict[tuple[int, ...], Fraction] = {}
        for cell_idx, km1_cell in enumerate(sorted_km1_cells):
            potential[km1_cell] = Fraction((delayed_sum + cell_idx + 1), prod_cap)
        exact_k_cochain = build_exact_k_cochain_from_potential(higher_complex, potential)
        return tuple(next_list), exact_k_cochain

    return _step


def make_async_uncompensated_stale_cochain_step_fn(
    agent_capacities: Sequence[int],
    higher_complex: HigherCellComplex,
    defect_trigger_step: int = 1,
) -> Callable[
    [HigherCellAsyncState],
    tuple[tuple[int, ...], dict[tuple[int, ...], Fraction]],
]:
    """Build an uncompensated asynchronous higher-cochain step function on `C^k --d^k--> C^{k+1}`.

    - Agents evolve via mixed-radix odometer transitions (`s_0' = (s_0 + 1) mod N_0`, etc.).
    - On the shared higher complex `C^k --d^k--> C^{k+1}`, all boundary `k`-faces of the primary
      `(k+1)`-simplex `sigma_0 = (v_0, ..., v_{k+1})` are initialized from an exact potential
      `d^{k-1} eta^{(k-1)}`, EXCEPT the closing face `face_0 = (v_1, ..., v_{k+1})`, where
      Agent A writes using the *delayed* projection `delivered_projections[0]` while Agent B
      evaluates compatibility against the *current* emitted projection `emitted_projections[0]`.
    - When `latency_steps == 0`, `delivered_projections == emitted_projections` at every step,
      so `Phi_1([delta^{(k)}]) == 0` everywhere and the system runs to `REPORT_COLLISION` at
      `k*(0) = prod_i N_i`.
    - When `latency_steps >= 1`, once `step + 1 >= defect_trigger_step`, the lag mismatch
      `|emitted_projections[0] - delivered_projections[0]| > 0` induces a non-zero coboundary defect
      `(d^k delta^{(k)})(sigma_0) != 0` (`Phi_1([delta^{(k)}]) > 0`), halting with
      `OVERLAP_GLUING_REFUSAL` at step `k*(tau) <= prod_i N_i + 1`.
    """
    if defect_trigger_step < 1:
        raise ValueError(f"defect_trigger_step must be >= 1, got {defect_trigger_step}")
    caps = tuple(int(c) for c in agent_capacities)
    prod_cap = math.prod(caps)
    sorted_km1_cells = sorted(higher_complex.required_k_minus_1_cells())
    primary_cell = higher_complex.k_plus_1_cells[0]
    closing_face = HigherCellComplex.boundary_faces_of_simplex(primary_cell)[0][1]

    def _step(
        state: HigherCellAsyncState,
    ) -> tuple[tuple[int, ...], dict[tuple[int, ...], Fraction]]:
        next_list = list(state.agent_states)
        carry = True
        for idx, cap in enumerate(caps):
            if carry:
                next_val = (state.agent_states[idx] + 1) % cap
                carry = next_val == 0
                next_list[idx] = next_val
            else:
                next_list[idx] = state.agent_states[idx]

        potential: dict[tuple[int, ...], Fraction] = {}
        for cell_idx, km1_cell in enumerate(sorted_km1_cells):
            potential[km1_cell] = Fraction((state.step + cell_idx + 1), prod_cap)
        k_cochain = build_exact_k_cochain_from_potential(higher_complex, potential)

        next_step = state.step + 1
        lag_mismatch = abs(state.emitted_projections[0] - state.delivered_projections[0])
        if max(state.effective_lags) > 0 and lag_mismatch == 0 and next_step >= defect_trigger_step:
            # Synthetic age-sensitive fixture policy: equal content can still
            # receive an imposed age penalty. This is not a transport theorem.
            lag_mismatch = max(state.effective_lags)

        if next_step >= defect_trigger_step and lag_mismatch > 0:
            k_cochain[closing_face] = k_cochain[closing_face] + Fraction(lag_mismatch, prod_cap)

        return tuple(next_list), k_cochain

    return _step


def make_non_monotonic_rewiring_step_fn(
    agent_capacities: Sequence[int],
    default_complex: HigherCellComplex,
    rewiring_schedule: DynamicSimplicialRewiringSchedule | None = None,
    compensate_rewiring_under_monotonic: bool = False,
) -> Callable[
    [HigherCellAsyncState],
    tuple[tuple[int, ...], dict[tuple[int, ...], Fraction]],
]:
    """Build a co-adaptation step function sensitive to non-monotonic delivery and dynamic simplicial rewiring.

    Controlled synthetic fixture, not a derived channel mechanism:
    - Agents evolve their local state coordinates using delivered boundary projections:
      - Under monotonic FIFO delivery (`is_non_monotonic_delivery == False`), the agents advance
        via a delay-compensated odometer over `prod_i N_i`.
      - When a packet drop or out-of-order message permutation (`is_non_monotonic_delivery == True`)
        occurs, or when `delivered_source_steps` are asymmetric across agents
        (`sigma_0(k) != sigma_1(k)`), Agent A updates boundary `k`-faces of the next complex
        `X_{k+1}` using potential `eta_A` anchored to `sigma_0(k)` while Agent B updates closing
        `k`-faces using potential `eta_B` anchored to `sigma_1(k)` (or to the inverted step defect).
    - Similarly, when `rewiring_schedule` rewires the topology at step `k + 1`
      (`X_{k+1} != X_k`) and `compensate_rewiring_under_monotonic == False`, newly attached
      `(k+1)`-simplices retain legacy `k`-face values on shared lower faces while receiving updated
      potentials on newly attached apex faces, inducing non-zero coboundary holonomy
      `(d_{k+1}^k delta_{k+1}^{(k)})(sigma) != 0` (`Phi_1([delta_{k+1}^{(k)}]) > 0`).
    - Conversely, under monotonic symmetric FIFO delivery on a static (or compensated) complex,
      `Phi_1([delta^{(k)}]) = 0` holds at every step, so the trajectory terminates strictly by
      `REPORT_COLLISION` at `k* <= prod_i N_i`.
    """
    caps = tuple(int(c) for c in agent_capacities)
    prod_cap = math.prod(caps)

    def _step(
        state: HigherCellAsyncState,
    ) -> tuple[tuple[int, ...], dict[tuple[int, ...], Fraction]]:
        next_step = state.step + 1
        delivered = state.delivered_projections
        lags = state.effective_lags

        next_list = list(state.agent_states)
        next_list[0] = (state.agent_states[0] + 1) % caps[0]
        for idx in range(1, len(caps)):
            prev_delivered = delivered[idx - 1]
            prev_lag = lags[idx - 1]
            if prev_lag == 0:
                carry = all(delivered[j] == caps[j] - 1 for j in range(idx))
                stride = 1 if carry else 0
            else:
                trigger_residue = (caps[idx - 1] - 1) % caps[idx - 1]
                secondary_residue = (
                    caps[idx - 1] - 1 - (prev_lag % caps[idx - 1])
                ) % caps[idx - 1]
                if prev_delivered == trigger_residue:
                    stride = 1
                elif prev_delivered == secondary_residue and state.step >= prev_lag:
                    stride = 2 if caps[idx] > 2 else 1
                else:
                    stride = 0
            next_list[idx] = (state.agent_states[idx] + stride) % caps[idx]

        current_complex = (
            rewiring_schedule.complex_at(state.step)
            if rewiring_schedule is not None
            else default_complex
        )
        next_complex = (
            rewiring_schedule.complex_at(next_step)
            if rewiring_schedule is not None
            else default_complex
        )
        will_rewire = next_complex.k_plus_1_cells != current_complex.k_plus_1_cells

        sorted_km1_cells = sorted(
            next_complex.required_k_minus_1_cells()
            | current_complex.required_k_minus_1_cells()
        )
        base_seed = sum(delivered) + next_step
        potential: dict[tuple[int, ...], Fraction] = {
            km1_cell: Fraction(base_seed + idx + 1, prod_cap)
            for idx, km1_cell in enumerate(sorted_km1_cells)
        }
        k_cochain = build_exact_k_cochain_from_potential(next_complex, potential)

        # Detect non-monotonic channel inversion or asymmetric source-step skew across agents
        source_steps = state.delivered_source_steps
        source_skew = (
            max(source_steps) - min(source_steps) if len(source_steps) >= 2 else 0
        )
        non_monotonic_defect = 0
        if state.is_non_monotonic_delivery:
            non_monotonic_defect += max(1, source_skew + max(lags, default=1))
        elif source_skew > 0:
            non_monotonic_defect += source_skew

        # Detect uncompensated dynamic simplicial topology rewiring defect
        rewiring_defect = 1 if (will_rewire and not compensate_rewiring_under_monotonic) else 0

        total_defect = non_monotonic_defect + rewiring_defect
        if total_defect > 0:
            target_simplex = next_complex.k_plus_1_cells[-1]
            closing_face = HigherCellComplex.boundary_faces_of_simplex(target_simplex)[0][1]
            k_cochain[closing_face] = k_cochain.get(closing_face, Fraction(0, 1)) + Fraction(
                total_defect, prod_cap
            )

        return tuple(next_list), k_cochain

    return _step


def evaluate_termination_distribution_under_non_monotonic_rewiring(
    agent_capacities: Sequence[int] = (3, 4),
    cochain_degree: int = 2,
    initial_budget: int = 20,
) -> dict[str, object]:
    """Quantify how packet-loss, non-FIFO out-of-order message permutation, and dynamic simplicial rewiring shift termination outcomes.

    Evaluates four regimes over `C^k(X_t) --d_t^k--> C^{k+1}(X_t)` within `k* <= N_A * N_B + 1`:
      1. `monotonic_fifo_static`: Monotonic symmetric FIFO channels (`tau in {0, 1, 2, 3}`) on a
         static complex `X_0`. Preserves `Phi_1([delta^{(k)}]) = 0`, yielding 100% `REPORT_COLLISION`.
      2. `packet_loss_static`: Channels with dropped updates (`dropped_steps_per_agent`) on `X_0`.
         Dropped updates induce stale-face coboundary mismatch `Phi_1([delta^{(k)}]) > 0`,
         shifting termination to `OVERLAP_GLUING_REFUSAL`.
      3. `out_of_order_permutation_static`: Non-FIFO out-of-order message permutation schedules
         (`sigma_a(k_2) < sigma_a(k_1)` for `k_1 < k_2`) on `X_0`. Out-of-order inversions shift
         termination to `OVERLAP_GLUING_REFUSAL` at the exact inversion step.
      4. `dynamic_simplicial_rewiring`: Time-varying `(k+1)`-complex schedules `X_t` combined with
         both monotonic FIFO and non-monotonic channels, comparing uncompensated vs. compensated
         simplicial rewiring.

    All emitted `HigherCellObstructionReceipt` instances are cross-checked against the Rust
    `omega_epistemic_immune_system` companion binary.
    """
    caps = tuple(int(c) for c in agent_capacities)
    prod_cap = math.prod(caps)
    horizon_bound = prod_cap + 1
    static_complex = HigherCellComplex.standard_simplex(degree=cochain_degree, num_cells=2)
    rewiring_schedule = DynamicSimplicialRewiringSchedule.standard_rewiring_cycle(
        degree=cochain_degree, num_topologies=3, cells_per_topology=2
    )
    zero_k_cochain = {
        face: Fraction(0, 1) for face in rewiring_schedule.all_required_k_cells(max_step=horizon_bound + 2)
    }
    init_states = tuple(0 for _ in caps)

    all_receipts: list[HigherCellObstructionReceipt] = []
    regime_summaries: dict[str, dict[str, object]] = {}

    def _summarize_regime(name: str, receipts: Sequence[HigherCellObstructionReceipt]) -> dict[str, object]:
        counts: dict[str, int] = {
            "OVERLAP_GLUING_REFUSAL": 0,
            "REPORT_COLLISION": 0,
            "LIFT_BUDGET_EXHAUSTION": 0,
            "CAPACITY_THRESHOLD_EXCEEDED": 0,
        }
        steps: list[int] = []
        for r in receipts:
            counts[r.obstruction_kind] = counts.get(r.obstruction_kind, 0) + 1
            steps.append(r.termination_step)
            if not (0 <= r.termination_step <= horizon_bound):
                raise AssertionError(
                    f"Regime {name} receipt step {r.termination_step} exceeded horizon {horizon_bound}"
                )
        total = len(receipts)
        return {
            "total_runs": total,
            "counts": counts,
            "gluing_refusal_fraction": f"{counts['OVERLAP_GLUING_REFUSAL']}/{total}",
            "report_collision_fraction": f"{counts['REPORT_COLLISION']}/{total}",
            "termination_steps": steps,
            "min_step": min(steps) if steps else 0,
            "max_step": max(steps) if steps else 0,
            "all_within_product_horizon": all(0 <= s <= horizon_bound for s in steps),
        }

    # Regime 1: Monotonic symmetric FIFO channels on static complex (tau = 0, 1, 2, 3)
    fifo_receipts: list[HigherCellObstructionReceipt] = []
    for tau in (0, 1, 2, 3):
        ch = NonMonotonicMessageChannel(num_agents=len(caps), latency_steps=tau)
        hg = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=caps,
            higher_complex=static_complex,
            latency_steps=tau,
            initial_agent_states=init_states,
            initial_budget=initial_budget,
            initial_k_cochain=zero_k_cochain,
            step_fn=make_non_monotonic_rewiring_step_fn(caps, static_complex),
            message_channel=ch,
        )
        r = hg.run()
        fifo_receipts.append(r)
        all_receipts.append(r)
    regime_summaries["monotonic_fifo_static"] = _summarize_regime(
        "monotonic_fifo_static", fifo_receipts
    )

    # Regime 2: Packet-loss channels on static complex (dropping at step d in {1, 2, 3, 4})
    loss_receipts: list[HigherCellObstructionReceipt] = []
    for drop_step in (1, 2, 3, 4):
        ch = NonMonotonicMessageChannel(
            num_agents=len(caps),
            latency_steps=0,
            dropped_steps_per_agent={0: {drop_step}},
        )
        hg = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=caps,
            higher_complex=static_complex,
            latency_steps=0,
            initial_agent_states=init_states,
            initial_budget=initial_budget,
            initial_k_cochain=zero_k_cochain,
            step_fn=make_non_monotonic_rewiring_step_fn(caps, static_complex),
            message_channel=ch,
        )
        r = hg.run()
        loss_receipts.append(r)
        all_receipts.append(r)
    regime_summaries["packet_loss_static"] = _summarize_regime(
        "packet_loss_static", loss_receipts
    )

    # Regime 3: Non-FIFO out-of-order message permutation channels on static complex
    perm_receipts: list[HigherCellObstructionReceipt] = []
    for inv_step in (2, 3, 4, 5):
        perm_sched = {0: {inv_step - 1: inv_step - 1, inv_step: inv_step - 2}}
        ch = NonMonotonicMessageChannel(
            num_agents=len(caps),
            latency_steps=0,
            permutation_schedule_per_agent=perm_sched,
        )
        hg = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=caps,
            higher_complex=static_complex,
            latency_steps=0,
            initial_agent_states=init_states,
            initial_budget=initial_budget,
            initial_k_cochain=zero_k_cochain,
            step_fn=make_non_monotonic_rewiring_step_fn(caps, static_complex),
            message_channel=ch,
        )
        r = hg.run()
        perm_receipts.append(r)
        all_receipts.append(r)
    regime_summaries["out_of_order_permutation_static"] = _summarize_regime(
        "out_of_order_permutation_static", perm_receipts
    )

    # Regime 4: Dynamic simplicial topology rewiring across C^k(X_t) --d_t^k--> C^{k+1}(X_t)
    rewired_receipts: list[HigherCellObstructionReceipt] = []
    for tau in (0, 2):
        ch_comp = NonMonotonicMessageChannel(num_agents=len(caps), latency_steps=tau)
        hg_comp = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=caps,
            higher_complex=static_complex,
            latency_steps=tau,
            initial_agent_states=init_states,
            initial_budget=initial_budget,
            initial_k_cochain=zero_k_cochain,
            step_fn=make_non_monotonic_rewiring_step_fn(
                caps,
                static_complex,
                rewiring_schedule=rewiring_schedule,
                compensate_rewiring_under_monotonic=True,
            ),
            message_channel=ch_comp,
            rewiring_schedule=rewiring_schedule,
        )
        r_comp = hg_comp.run()
        rewired_receipts.append(r_comp)
        all_receipts.append(r_comp)

    for drop_or_inv in (1, 2):
        ch_uncomp = NonMonotonicMessageChannel(
            num_agents=len(caps),
            latency_steps=1,
            dropped_steps_per_agent={0: {drop_or_inv}},
            permutation_schedule_per_agent={1: {2: 0}},
        )
        hg_uncomp = HigherCellAsyncCommunicatingHypergraph(
            agent_capacities=caps,
            higher_complex=static_complex,
            latency_steps=1,
            initial_agent_states=init_states,
            initial_budget=initial_budget,
            initial_k_cochain=zero_k_cochain,
            step_fn=make_non_monotonic_rewiring_step_fn(
                caps,
                static_complex,
                rewiring_schedule=rewiring_schedule,
                compensate_rewiring_under_monotonic=False,
            ),
            message_channel=ch_uncomp,
            rewiring_schedule=rewiring_schedule,
        )
        r_uncomp = hg_uncomp.run()
        rewired_receipts.append(r_uncomp)
        all_receipts.append(r_uncomp)

    regime_summaries["dynamic_simplicial_rewiring"] = _summarize_regime(
        "dynamic_simplicial_rewiring", rewired_receipts
    )

    eis_check = cross_check_eis_metadata_against_rust(all_receipts)
    return {
        "cochain_degree": cochain_degree,
        "agent_capacities": list(caps),
        "product_carrier_capacity": prod_cap,
        "horizon_bound": horizon_bound,
        "total_ensemble_runs": len(all_receipts),
        "regimes": regime_summaries,
        "experiment_scope": "CONTROLLED_SYNTHETIC_DEFECT_INJECTION",
        "distribution_shift_verified": (
            regime_summaries["monotonic_fifo_static"]["counts"]["REPORT_COLLISION"] == 4
            and regime_summaries["monotonic_fifo_static"]["counts"]["OVERLAP_GLUING_REFUSAL"] == 0
            and regime_summaries["packet_loss_static"]["counts"]["OVERLAP_GLUING_REFUSAL"] == 4
            and regime_summaries["out_of_order_permutation_static"]["counts"][
                "OVERLAP_GLUING_REFUSAL"
            ]
            == 4
            and regime_summaries["dynamic_simplicial_rewiring"]["counts"]["REPORT_COLLISION"] == 2
            and regime_summaries["dynamic_simplicial_rewiring"]["counts"][
                "OVERLAP_GLUING_REFUSAL"
            ]
            == 2
        ),
        "eis_cross_check": eis_check,
    }
