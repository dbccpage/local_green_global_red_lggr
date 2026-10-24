"""Dynamic simplicial topology rewiring schedules over higher-cell complexes.

AuthorityEffect: None.

Models time-varying simplicial cochain complex schedules (C^k(X_t) -> C^{k+1}(X_t))_{t >= 0},
allowing (k+1)-cells to attach, detach, or cycle dynamically across steps t.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from simplicial_complex import HigherCellComplex


class DynamicSimplicialRewiringSchedule:
    """Time-varying simplicial cochain complex schedule `(C^k(X_t) --d_t^k--> C^{k+1}(X_t))_{t >= 0}`.

    Models dynamic topological rewiring of the shared `(k+1)`-complex across steps `t`.
    All complexes `X_t` share the same cochain degree `k >= 1`, while the active `(k+1)`-cells
    can attach, detach, or cycle across vertex sets as `t` advances.
    """

    def __init__(
        self,
        default_complex: HigherCellComplex,
        complex_by_step: Mapping[int, HigherCellComplex] | None = None,
        cyclic_complexes: Sequence[HigherCellComplex] | None = None,
    ) -> None:
        self._degree = default_complex.degree
        self._default_complex = default_complex
        self._complex_by_step: dict[int, HigherCellComplex] = {}
        if complex_by_step is not None:
            for step_idx, cpx in complex_by_step.items():
                if int(step_idx) < 0:
                    raise ValueError(f"Step index in complex_by_step must be >= 0, got {step_idx}")
                if cpx.degree != self._degree:
                    raise ValueError(
                        f"Complex at step {step_idx} has degree {cpx.degree} != expected {self._degree}"
                    )
                self._complex_by_step[int(step_idx)] = cpx

        self._cyclic_complexes: tuple[HigherCellComplex, ...] = ()
        if cyclic_complexes is not None:
            if len(cyclic_complexes) < 1:
                raise ValueError("cyclic_complexes must not be empty when provided")
            for idx, cpx in enumerate(cyclic_complexes):
                if cpx.degree != self._degree:
                    raise ValueError(
                        f"cyclic_complexes[{idx}] has degree {cpx.degree} != expected {self._degree}"
                    )
            self._cyclic_complexes = tuple(cyclic_complexes)

    @classmethod
    def standard_rewiring_cycle(
        cls, degree: int, num_topologies: int = 2, cells_per_topology: int = 2
    ) -> DynamicSimplicialRewiringSchedule:
        """Construct a deterministic cycle of distinct `(k+1)`-complex topologies of degree `k`."""
        if degree < 1:
            raise ValueError(f"degree must be >= 1, got {degree}")
        if num_topologies < 2:
            raise ValueError(f"num_topologies must be >= 2, got {num_topologies}")
        if cells_per_topology < 1:
            raise ValueError(f"cells_per_topology must be >= 1, got {cells_per_topology}")

        topologies: list[HigherCellComplex] = []
        base_verts = list(range(degree + 1))
        for topo_idx in range(num_topologies):
            cells: list[tuple[int, ...]] = []
            for c_idx in range(cells_per_topology):
                apex = degree + 1 + topo_idx * cells_per_topology + c_idx
                cells.append(tuple(base_verts + [apex]))
            topologies.append(HigherCellComplex(degree=degree, k_plus_1_cells=cells))
        return cls(default_complex=topologies[0], cyclic_complexes=topologies)

    @property
    def degree(self) -> int:
        """Cochain degree `k` shared across all time steps `t`."""
        return self._degree

    def complex_at(self, step: int) -> HigherCellComplex:
        """Return the active `HigherCellComplex` `X_t` at step `t = step`."""
        if step < 0:
            raise ValueError(f"step must be >= 0, got {step}")
        if step in self._complex_by_step:
            return self._complex_by_step[step]
        if self._cyclic_complexes:
            return self._cyclic_complexes[step % len(self._cyclic_complexes)]
        return self._default_complex

    def is_rewired_at(self, step: int) -> bool:
        """Return True if `X_step` has different `(k+1)`-cells from `X_{step-1}` (`step >= 1`)."""
        if step <= 0:
            return False
        return (
            self.complex_at(step).k_plus_1_cells
            != self.complex_at(step - 1).k_plus_1_cells
        )

    def all_required_k_cells(self, max_step: int = 32) -> set[tuple[int, ...]]:
        """Union of all `k`-faces across all topologies reachable up to `max_step`."""
        cells: set[tuple[int, ...]] = set(self._default_complex.required_k_cells())
        for cpx in self._complex_by_step.values():
            cells.update(cpx.required_k_cells())
        for cpx in self._cyclic_complexes:
            cells.update(cpx.required_k_cells())
        for t in range(max_step + 1):
            cells.update(self.complex_at(t).required_k_cells())
        return cells

    def all_required_k_minus_1_cells(self, max_step: int = 32) -> set[tuple[int, ...]]:
        """Union of all `(k-1)`-faces across all topologies reachable up to `max_step`."""
        cells: set[tuple[int, ...]] = set(self._default_complex.required_k_minus_1_cells())
        for cpx in self._complex_by_step.values():
            cells.update(cpx.required_k_minus_1_cells())
        for cpx in self._cyclic_complexes:
            cells.update(cpx.required_k_minus_1_cells())
        for t in range(max_step + 1):
            cells.update(self.complex_at(t).required_k_minus_1_cells())
        return cells
