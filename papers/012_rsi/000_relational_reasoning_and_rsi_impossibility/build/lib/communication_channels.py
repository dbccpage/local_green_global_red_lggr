"""Communication channels and latency buffers for multi-agent boundary projection exchange.

AuthorityEffect: None.

Provides:
- `AsynchronousMessageDelayBuffer`: Monotonic FIFO message latency buffer (tau >= 0).
- `NonMonotonicMessageChannel`: Causal message channel supporting packet loss (hold-last-delivered)
  and non-FIFO out-of-order message permutations (0 <= sigma_a(k) <= k).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


class AsynchronousMessageDelayBuffer:
    """Bounded FIFO communication latency buffer for multi-agent boundary projection exchange.

    At step `k`, agent `a` emits its current boundary projection `pi_a(M_k^{(a)})`, which is
    stored in the channel history. The channel delivers the delayed boundary projection
    `hat{pi}_a(k) = pi_a(M_{k - tau_{a,k}}^{(a)})` where `tau_{a,k} = min(k, tau_a)` for configured
    non-negative integer latency `tau_a >= 0`.
    """

    def __init__(self, num_agents: int, latency_steps: int | Sequence[int]) -> None:
        if num_agents < 2:
            raise ValueError(f"AsynchronousMessageDelayBuffer requires >= 2 agents, got {num_agents}")
        if isinstance(latency_steps, int):
            if latency_steps < 0:
                raise ValueError(f"latency_steps must be >= 0, got {latency_steps}")
            self._latency_per_agent = tuple(latency_steps for _ in range(num_agents))
        else:
            if len(latency_steps) != num_agents:
                raise ValueError(
                    f"Expected {num_agents} latency values, got {len(latency_steps)}"
                )
            for tau in latency_steps:
                if tau < 0:
                    raise ValueError(f"Per-agent latency must be >= 0, got {tau}")
            self._latency_per_agent = tuple(int(tau) for tau in latency_steps)
        self._num_agents = num_agents
        self._history: list[tuple[int, ...]] = []

    @property
    def latency_per_agent(self) -> tuple[int, ...]:
        """Configured non-negative integer latency steps `(tau_0, ..., tau_{m-1})`."""
        return self._latency_per_agent

    @property
    def max_latency(self) -> int:
        """Maximum communication latency `max_a tau_a` across all agents."""
        return max(self._latency_per_agent)

    def reset(self) -> None:
        """Clear buffered projection history."""
        self._history.clear()

    def record_and_deliver(
        self, step: int, emitted_projections: tuple[int, ...]
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        """Record `emitted_projections` at `step` and return `(delivered_projections, effective_lags)`."""
        if len(emitted_projections) != self._num_agents:
            raise ValueError(
                f"Expected {self._num_agents} projections, got {len(emitted_projections)}"
            )
        if step != len(self._history):
            raise ValueError(
                f"AsynchronousMessageDelayBuffer step {step} out of sync with history length {len(self._history)}"
            )
        self._history.append(tuple(int(p) for p in emitted_projections))
        delivered: list[int] = []
        lags: list[int] = []
        for agent_idx, tau in enumerate(self._latency_per_agent):
            eff_lag = min(step, tau)
            source_step = step - eff_lag
            delivered.append(self._history[source_step][agent_idx])
            lags.append(eff_lag)
        return tuple(delivered), tuple(lags)


class NonMonotonicMessageChannel:
    """Causal message-delivery channel supporting packet loss and non-FIFO out-of-order permutations.

    At step `k >= 0`, each agent `a` emits a boundary projection `pi_a(M_k)` into the channel.
    Unlike a strictly monotonic FIFO delay buffer (`sigma_a(k) = k - min(k, tau_a)`), a general
    causal delivery schedule `sigma_a : Nat -> Nat` satisfies `0 <= sigma_a(k) <= k` and supports:
      1. **Packet loss (hold-last-delivered)**: If step `k` is in `dropped_steps_per_agent[a]`,
         the incoming update for step `k` is dropped and the receiver retains the previously
         delivered source step `sigma_a(k) = sigma_a(k - 1)` (or `0` at `k = 0`).
      2. **Non-FIFO out-of-order message permutation**: If step `k` is in
         `permutation_schedule_per_agent[a]`, the channel delivers `sigma_a(k) = perm[k]`
         (validated to satisfy causality `0 <= sigma_a(k) <= k`), allowing out-of-order
         inversions `sigma_a(k_2) < sigma_a(k_1)` for `k_1 < k_2`.
      3. **Baseline latency fallback**: Otherwise, `sigma_a(k) = k - min(k, tau_a)`.
    """

    def __init__(
        self,
        num_agents: int,
        latency_steps: int | Sequence[int] = 0,
        dropped_steps_per_agent: Mapping[int, Sequence[int] | set[int]] | Sequence[int] | set[int] | None = None,
        permutation_schedule_per_agent: Mapping[int, Mapping[int, int]] | Mapping[int, int] | None = None,
    ) -> None:
        if num_agents < 2:
            raise ValueError(f"num_agents must be >= 2, got {num_agents}")
        if isinstance(latency_steps, int):
            if latency_steps < 0:
                raise ValueError(f"latency_steps must be >= 0, got {latency_steps}")
            self._latency_per_agent: tuple[int, ...] = tuple(
                latency_steps for _ in range(num_agents)
            )
        else:
            if len(latency_steps) != num_agents:
                raise ValueError(
                    f"latency_steps sequence length {len(latency_steps)} != num_agents {num_agents}"
                )
            for idx, tau in enumerate(latency_steps):
                if tau < 0:
                    raise ValueError(f"latency_steps[{idx}] must be >= 0, got {tau}")
            self._latency_per_agent = tuple(int(tau) for tau in latency_steps)

        self._num_agents = num_agents

        # Normalize dropped_steps_per_agent: dict[int, frozenset[int]]
        dropped_map: dict[int, frozenset[int]] = {a: frozenset() for a in range(num_agents)}
        if dropped_steps_per_agent is not None:
            if isinstance(dropped_steps_per_agent, Mapping):
                for a_idx, steps in dropped_steps_per_agent.items():
                    if not (0 <= int(a_idx) < num_agents):
                        raise ValueError(f"Invalid agent index {a_idx} in dropped_steps_per_agent")
                    for s in steps:
                        if int(s) < 0:
                            raise ValueError(f"Dropped step must be >= 0, got {s}")
                    dropped_map[int(a_idx)] = frozenset(int(s) for s in steps)
            else:
                shared_drops = frozenset(int(s) for s in dropped_steps_per_agent)
                for s in shared_drops:
                    if s < 0:
                        raise ValueError(f"Dropped step must be >= 0, got {s}")
                for a_idx in range(num_agents):
                    dropped_map[a_idx] = shared_drops
        self._dropped_steps_per_agent = dropped_map

        # Normalize permutation_schedule_per_agent: dict[int, dict[int, int]]
        perm_map: dict[int, dict[int, int]] = {a: {} for a in range(num_agents)}
        if permutation_schedule_per_agent is not None:
            first_val = next(iter(permutation_schedule_per_agent.values()), None)
            if isinstance(first_val, Mapping):
                for a_idx, sched in permutation_schedule_per_agent.items():
                    if not (0 <= int(a_idx) < num_agents):
                        raise ValueError(
                            f"Invalid agent index {a_idx} in permutation_schedule_per_agent"
                        )
                    agent_sched: dict[int, int] = {}
                    for k_step, src_step in sched.items():  # type: ignore[union-attr]
                        k_int, src_int = int(k_step), int(src_step)
                        if k_int < 0 or not (0 <= src_int <= k_int):
                            raise ValueError(
                                f"Causal delivery violation for agent {a_idx} at step {k_int}: "
                                f"source step {src_int} must satisfy 0 <= sigma_a(k) <= k"
                            )
                        agent_sched[k_int] = src_int
                    perm_map[int(a_idx)] = agent_sched
            else:
                shared_sched: dict[int, int] = {}
                for k_step, src_step in permutation_schedule_per_agent.items():
                    k_int, src_int = int(k_step), int(src_step)  # type: ignore[arg-type]
                    if k_int < 0 or not (0 <= src_int <= k_int):
                        raise ValueError(
                            f"Causal delivery violation at step {k_int}: "
                            f"source step {src_int} must satisfy 0 <= sigma_a(k) <= k"
                        )
                    shared_sched[k_int] = src_int
                for a_idx in range(num_agents):
                    perm_map[a_idx] = dict(shared_sched)
        self._permutation_schedule_per_agent = perm_map

        self._history: list[tuple[int, ...]] = []
        self._delivered_source_history: list[tuple[int, ...]] = []
        self._non_monotonic_inversion_count: int = 0

    @property
    def latency_per_agent(self) -> tuple[int, ...]:
        """Configured baseline communication latency `(tau_0, ..., tau_{m-1})`."""
        return self._latency_per_agent

    @property
    def non_monotonic_inversion_count(self) -> int:
        """Cumulative count of non-monotonic delivery inversions (`sigma_a(k) < sigma_a(k-1)`) or packet-loss holds."""
        return self._non_monotonic_inversion_count

    @property
    def channel_mode(self) -> str:
        """Descriptive channel mode (`fifo`, `packet_loss`, `out_of_order`, or `packet_loss+out_of_order`)."""
        has_drops = any(bool(s) for s in self._dropped_steps_per_agent.values())
        has_perms = any(bool(p) for p in self._permutation_schedule_per_agent.values())
        if has_drops and has_perms:
            return "packet_loss+out_of_order"
        if has_drops:
            return "packet_loss"
        if has_perms:
            return "out_of_order"
        return "fifo"

    def reset(self) -> None:
        """Clear recorded projection and delivery histories."""
        self._history.clear()
        self._delivered_source_history.clear()
        self._non_monotonic_inversion_count = 0

    def record_and_deliver_detailed(
        self, step: int, emitted_projections: tuple[int, ...]
    ) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], bool]:
        """Record `emitted_projections` at `step` and return `(delivered, effective_lags, source_steps, is_non_monotonic)`."""
        if len(emitted_projections) != self._num_agents:
            raise ValueError(
                f"Expected {self._num_agents} projections, got {len(emitted_projections)}"
            )
        if step != len(self._history):
            raise ValueError(
                f"NonMonotonicMessageChannel step {step} out of sync with history length {len(self._history)}"
            )
        self._history.append(tuple(int(p) for p in emitted_projections))

        delivered: list[int] = []
        lags: list[int] = []
        source_steps: list[int] = []
        step_non_monotonic = False

        for agent_idx, tau in enumerate(self._latency_per_agent):
            perm_sched = self._permutation_schedule_per_agent[agent_idx]
            dropped_set = self._dropped_steps_per_agent[agent_idx]

            if step in perm_sched:
                src_step = perm_sched[step]
            elif step in dropped_set:
                if step == 0:
                    src_step = 0
                else:
                    src_step = self._delivered_source_history[-1][agent_idx]
                if step > 0:
                    step_non_monotonic = True
            else:
                eff_lag = min(step, tau)
                src_step = step - eff_lag

            if not (0 <= src_step <= step):
                raise ValueError(
                    f"Causal violation for agent {agent_idx} at step {step}: source_step={src_step}"
                )

            if step > 0:
                prev_src = self._delivered_source_history[-1][agent_idx]
                if src_step < prev_src:
                    step_non_monotonic = True

            delivered.append(self._history[src_step][agent_idx])
            lags.append(step - src_step)
            source_steps.append(src_step)

        if step_non_monotonic:
            self._non_monotonic_inversion_count += 1
        self._delivered_source_history.append(tuple(source_steps))
        return tuple(delivered), tuple(lags), tuple(source_steps), step_non_monotonic

    def record_and_deliver(
        self, step: int, emitted_projections: tuple[int, ...]
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        """Compatibility wrapper returning `(delivered_projections, effective_lags)`."""
        delivered, lags, _, _ = self.record_and_deliver_detailed(step, emitted_projections)
        return delivered, lags
