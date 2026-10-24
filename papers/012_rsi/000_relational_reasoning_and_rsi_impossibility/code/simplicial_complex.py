"""Shared higher k-cell simplicial complexes and coboundary holonomy.

AuthorityEffect: None.

Defines `HigherCellComplex` for degree k >= 1 cochain complexes (C^k -> C^{k+1}),
exact coboundary operators (d^k delta^{(k)}), potential-derived exact cochains,
and rational L1 holonomy functionals Phi_1([delta^{(k)}]).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from multi_agent_hypergraph import SharedTwoComplex


@dataclass(frozen=True)
class HigherCellComplex:
    """Shared higher k-cell cochain complex (C^k --d^k--> C^{k+1}) for multi-agent boundary gluing.

    An oriented (k+1)-cell is represented as a tuple of (k+2) distinct integer vertex indices
    `(v_0, v_1, ..., v_{k+1})`. Its boundary consists of (k+2) oriented k-cells
    `(v_0, ..., hat{v_i}, ..., v_{k+1})` with alternating signs `(-1)^i`.
    """

    degree: int
    k_plus_1_cells: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if self.degree < 1:
            raise ValueError(f"HigherCellComplex requires degree k >= 1, got {self.degree}")
        if not self.k_plus_1_cells:
            raise ValueError("HigherCellComplex requires at least one oriented (k+1)-simplex")
        expected_len = self.degree + 2
        for cell in self.k_plus_1_cells:
            if len(cell) != expected_len:
                raise ValueError(
                    f"Degree k={self.degree} requires (k+1)-cells of length {expected_len}, got {cell}"
                )
            if len(set(cell)) != expected_len:
                raise ValueError(f"Degenerate (k+1)-simplex is not allowed: {cell}")

    @classmethod
    def standard_simplex(
        cls, degree: int, num_cells: int = 1
    ) -> HigherCellComplex:
        """Construct a higher k-cell complex with `num_cells` oriented (k+1)-simplices `(0, 1, ..., k, k+1+idx)`."""
        if degree < 1:
            raise ValueError(f"degree must be >= 1, got {degree}")
        if num_cells < 1:
            raise ValueError(f"num_cells must be >= 1, got {num_cells}")
        cells: list[tuple[int, ...]] = []
        base = tuple(range(degree + 1))
        for c_idx in range(num_cells):
            apex = degree + 1 + c_idx
            cells.append((*base, apex))
        return cls(degree=degree, k_plus_1_cells=tuple(cells))

    @classmethod
    def from_shared_two_complex(cls, two_complex: SharedTwoComplex) -> HigherCellComplex:
        """Embed a `SharedTwoComplex` (C^1 --d^1--> C^2) as a degree k=1 `HigherCellComplex`."""
        return cls(degree=1, k_plus_1_cells=two_complex.triangles)

    @staticmethod
    def boundary_faces_of_simplex(
        simplex: tuple[int, ...],
    ) -> tuple[tuple[int, tuple[int, ...]], ...]:
        """Return alternating boundary faces `((-1)^i, (v_0, ..., hat{v_i}, ..., v_m))`."""
        faces: list[tuple[int, tuple[int, ...]]] = []
        for i in range(len(simplex)):
            sign = 1 if (i % 2 == 0) else -1
            face = simplex[:i] + simplex[i + 1 :]
            faces.append((sign, face))
        return tuple(faces)

    def required_k_cells(self) -> set[tuple[int, ...]]:
        """Return all oriented k-simplices appearing on the boundary of any (k+1)-cell."""
        k_cells: set[tuple[int, ...]] = set()
        for cell in self.k_plus_1_cells:
            for _, face in self.boundary_faces_of_simplex(cell):
                k_cells.add(face)
        return k_cells

    def required_k_minus_1_cells(self) -> set[tuple[int, ...]]:
        """Return all oriented (k-1)-simplices appearing on the boundary of any required k-cell."""
        km1_cells: set[tuple[int, ...]] = set()
        for k_cell in self.required_k_cells():
            for _, face in self.boundary_faces_of_simplex(k_cell):
                km1_cells.add(face)
        return km1_cells


def compute_dk_coboundary(
    k_cochain: Mapping[tuple[int, ...], Fraction],
    k_plus_1_cell: tuple[int, ...],
) -> Fraction:
    """Compute exact rational coboundary `(d^k delta^{(k)})(v_0, ..., v_{k+1})` in `C^{k+1}(X; Q)`.

    `(d^k delta^{(k)})(v_0, ..., v_{k+1}) = sum_{i=0}^{k+1} (-1)^i delta^{(k)}(v_0, ..., hat{v_i}, ..., v_{k+1})`.
    For k=1 on `(u, v, w)`, this equals `delta(v, w) - delta(u, w) + delta(u, v)`, matching `compute_d1_triangle`.
    For k=2 on `(u, v, w, z)`, this equals `delta(v,w,z) - delta(u,w,z) + delta(u,v,z) - delta(u,v,w)`,
    matching `OmegaRelationalRsi.d2` in `lean4/RelationalRsiNoGo.lean`.
    """
    if len(k_plus_1_cell) < 3:
        raise ValueError(f"(k+1)-simplex must have at least 3 vertices, got {k_plus_1_cell}")
    missing = [
        face
        for _, face in HigherCellComplex.boundary_faces_of_simplex(k_plus_1_cell)
        if face not in k_cochain
    ]
    if missing:
        raise KeyError(f"Missing k-cochain values for boundary k-faces: {missing}")
    total = Fraction(0, 1)
    for sign, face in HigherCellComplex.boundary_faces_of_simplex(k_plus_1_cell):
        val = k_cochain[face]
        if not isinstance(val, Fraction):
            raise TypeError("Higher k-cochain values must be exact fractions.Fraction")
        total += Fraction(sign, 1) * val
    return total


def build_exact_k_cochain_from_potential(
    complex_k: HigherCellComplex,
    k_minus_1_potential: Mapping[tuple[int, ...], Fraction],
) -> dict[tuple[int, ...], Fraction]:
    """Construct an exact k-cochain `delta^{(k)} = d^{k-1} eta^{(k-1)}` from a (k-1)-cochain potential.

    By the fundamental cochain identity `d^k o d^{k-1} = 0`, any k-cochain generated by this
    function satisfies `(d^k delta^{(k)})(sigma) = 0` on every (k+1)-cell `sigma`, and hence
    `Phi_1([delta^{(k)}]) = 0` in exact rational arithmetic.
    """
    required_km1 = complex_k.required_k_minus_1_cells()
    missing = [cell for cell in required_km1 if cell not in k_minus_1_potential]
    if missing:
        raise KeyError(f"Missing (k-1)-potential values for cells: {sorted(missing)}")
    k_cochain: dict[tuple[int, ...], Fraction] = {}
    for k_cell in sorted(complex_k.required_k_cells()):
        val = Fraction(0, 1)
        for sign, face in HigherCellComplex.boundary_faces_of_simplex(k_cell):
            pot_val = k_minus_1_potential[face]
            if not isinstance(pot_val, Fraction):
                raise TypeError("(k-1)-potential values must be exact fractions.Fraction")
            val += Fraction(sign, 1) * pot_val
        k_cochain[k_cell] = val
    return k_cochain


def compute_higher_cell_phi1_holonomy(
    complex_k: HigherCellComplex,
    k_cochain: Mapping[tuple[int, ...], Fraction],
) -> Fraction:
    """Compute exact rational L1 coboundary norm `Phi_1([delta^{(k)}]) = sum_{sigma in C_{k+1}} |(d^k delta^{(k)})(sigma)|`."""
    total = Fraction(0, 1)
    for cell in complex_k.k_plus_1_cells:
        total += abs(compute_dk_coboundary(k_cochain, cell))
    return total
