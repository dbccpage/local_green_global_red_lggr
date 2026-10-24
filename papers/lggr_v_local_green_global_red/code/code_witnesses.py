"""Explicit finite systems: ThreePatchWitness (Theorem 3 & 4), CoupledWitness (Theorem 6), ScalarQuotient (Remark)."""
from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from code_core import Assignment, Evaluator, Interface, NormType, Site, System


class ThreePatchSystem:
    """Explicit 3-patch triangle overlap witness (Theorem 3 & 4).

    3 patches (u0, u1, u2) and 3 pairwise overlaps (x01, x12, x20) with 6 directed interfaces:
    - (x01, u0), (x01, u1)
    - (x12, u1), (x12, u2)
    - (x20, u2), (x20, u0)

    State space: R^3 with L1 norm on all sites.
    Translations: Identity matrix I_3.
    Evaluators: Evaluator a deletes coordinate a (ker = R e_a) for edges targeting u_a.
    """

    def __init__(self):
        self.system = System()
        dim = 3
        eye3 = np.eye(dim)

        # 3 patch sites and 3 overlap sites
        for name in ["u0", "u1", "u2", "x01", "x12", "x20"]:
            self.system.add_site(Site(name=name, dimension=dim, norm_type=NormType.L1))

        # 6 interfaces: each overlap x_{ij} to patch u_i
        # defect on e=(x, u) is r_e(s(u)) - s(x) = I * s(u) - 0 = s(u)
        self.edges = [
            ("e_x01_u0", "x01", "u0"),
            ("e_x01_u1", "x01", "u1"),
            ("e_x12_u1", "x12", "u1"),
            ("e_x12_u2", "x12", "u2"),
            ("e_x20_u2", "x20", "u2"),
            ("e_x20_u0", "x20", "u0"),
        ]

        for name, sa, sb in self.edges:
            self.system.add_interface(
                Interface(
                    name=name,
                    site_a=sa,
                    site_b=sb,
                    translation_matrix=eye3,
                    norm_type=NormType.L1,
                )
            )

        # 3 Evaluators:
        # Evaluator 0 (watches u0 edges: e_x01_u0, e_x20_u0) -> deletes coordinate 0 (keeps coords 1, 2)
        # Evaluator 1 (watches u1 edges: e_x01_u1, e_x12_u1) -> deletes coordinate 1 (keeps coords 0, 2)
        # Evaluator 2 (watches u2 edges: e_x12_u2, e_x20_u2) -> deletes coordinate 2 (keeps coords 0, 1)
        q0 = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        q1 = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        q2 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

        ev0 = Evaluator(
            name="evaluator_0",
            watched_interfaces=["e_x01_u0", "e_x20_u0"],
            measurement_matrices={"e_x01_u0": q0, "e_x20_u0": q0},
            value_norms={"e_x01_u0": NormType.L1, "e_x20_u0": NormType.L1},
        )
        ev1 = Evaluator(
            name="evaluator_1",
            watched_interfaces=["e_x01_u1", "e_x12_u1"],
            measurement_matrices={"e_x01_u1": q1, "e_x12_u1": q1},
            value_norms={"e_x01_u1": NormType.L1, "e_x12_u1": NormType.L1},
        )
        ev2 = Evaluator(
            name="evaluator_2",
            watched_interfaces=["e_x12_u2", "e_x20_u2"],
            measurement_matrices={"e_x12_u2": q2, "e_x20_u2": q2},
            value_norms={"e_x12_u2": NormType.L1, "e_x20_u2": NormType.L1},
        )

        self.system.add_evaluator(ev0)
        self.system.add_evaluator(ev1)
        self.system.add_evaluator(ev2)

    def create_scaled_assignment(self, lam: float) -> Assignment:
        """Create the section assignment s_R where s(u_i) = lam * e_i and overlaps are 0."""
        a = Assignment()
        e0 = np.array([lam, 0.0, 0.0])
        e1 = np.array([0.0, lam, 0.0])
        e2 = np.array([0.0, 0.0, lam])
        z = np.zeros(3)

        a.set_state("u0", e0)
        a.set_state("u1", e1)
        a.set_state("u2", e2)
        a.set_state("x01", z)
        a.set_state("x12", z)
        a.set_state("x20", z)
        return a


class TrivialKernelThreePatchSystem:
    """Three-patch system equipped with identity measurement maps (trivial blind spots).

    Used to demonstrate Theorem 5 positive soundness in numerical regression.
    """

    def __init__(self):
        self.system = System()
        dim = 3
        eye3 = np.eye(dim)

        for name in ["u0", "u1", "u2", "x01", "x12", "x20"]:
            self.system.add_site(Site(name=name, dimension=dim, norm_type=NormType.L1))

        self.edges = [
            ("e_x01_u0", "x01", "u0"),
            ("e_x01_u1", "x01", "u1"),
            ("e_x12_u1", "x12", "u1"),
            ("e_x12_u2", "x12", "u2"),
            ("e_x20_u2", "x20", "u2"),
            ("e_x20_u0", "x20", "u0"),
        ]

        for name, sa, sb in self.edges:
            self.system.add_interface(
                Interface(
                    name=name,
                    site_a=sa,
                    site_b=sb,
                    translation_matrix=eye3,
                    norm_type=NormType.L1,
                )
            )

        # Evaluators with identity measurement maps: ker(q) = {0}
        ev0 = Evaluator(
            name="evaluator_0",
            watched_interfaces=["e_x01_u0", "e_x20_u0"],
            measurement_matrices={"e_x01_u0": eye3, "e_x20_u0": eye3},
            value_norms={"e_x01_u0": NormType.L1, "e_x20_u0": NormType.L1},
        )
        ev1 = Evaluator(
            name="evaluator_1",
            watched_interfaces=["e_x01_u1", "e_x12_u1"],
            measurement_matrices={"e_x01_u1": eye3, "e_x12_u1": eye3},
            value_norms={"e_x01_u1": NormType.L1, "e_x12_u1": NormType.L1},
        )
        ev2 = Evaluator(
            name="evaluator_2",
            watched_interfaces=["e_x12_u2", "e_x20_u2"],
            measurement_matrices={"e_x12_u2": eye3, "e_x20_u2": eye3},
            value_norms={"e_x12_u2": NormType.L1, "e_x20_u2": NormType.L1},
        )

        self.system.add_evaluator(ev0)
        self.system.add_evaluator(ev1)
        self.system.add_evaluator(ev2)


class CoupledSystem:
    """Explicit coupled 2-edge carrier witness (Theorem 6 - S13 settlement).

    1 overlap x under 2 patches u0, u1 with ZERO translations r_e = 0.
    Interfaces go from patches into overlap x (site_a = 'x', site_b = 'u_i').
    Defect on e_i is r_e(s(u_i)) - s(x) = 0 - s(x) = -s(x).

    State space: R^2 with L1 norm.
    Evaluator 0 watches edge 0 and reads coordinate 1 (kernel = R b_0).
    Evaluator 1 watches edge 1 and reads coordinate 0 (kernel = R b_1).
    """

    def __init__(self):
        self.system = System()
        dim = 2
        zero2 = np.zeros((dim, dim))

        self.system.add_site(Site("u0", dimension=dim, norm_type=NormType.L1))
        self.system.add_site(Site("u1", dimension=dim, norm_type=NormType.L1))
        self.system.add_site(Site("x", dimension=dim, norm_type=NormType.L1))

        # 2 Interfaces targeting overlap x with zero restriction maps
        self.system.add_interface(
            Interface("e0", site_a="x", site_b="u0", translation_matrix=zero2, norm_type=NormType.L1)
        )
        self.system.add_interface(
            Interface("e1", site_a="x", site_b="u1", translation_matrix=zero2, norm_type=NormType.L1)
        )

        # Evaluator 0 watches e0, reads coordinate 1: q0 = [[0, 1]]
        # Evaluator 1 watches e1, reads coordinate 0: q1 = [[1, 0]]
        q0 = np.array([[0.0, 1.0]])
        q1 = np.array([[1.0, 0.0]])

        ev0 = Evaluator(
            name="evaluator_0",
            watched_interfaces=["e0"],
            measurement_matrices={"e0": q0},
            value_norms={"e0": NormType.L1},
        )
        ev1 = Evaluator(
            name="evaluator_1",
            watched_interfaces=["e1"],
            measurement_matrices={"e1": q1},
            value_norms={"e1": NormType.L1},
        )

        self.system.add_evaluator(ev0)
        self.system.add_evaluator(ev1)

    def create_section_assignment(
        self,
        sx: Sequence[float] | np.ndarray,
        su0: Sequence[float] | np.ndarray = (0.0, 0.0),
        su1: Sequence[float] | np.ndarray = (0.0, 0.0),
    ) -> Assignment:
        """Create section assignment with overlap value sx."""
        a = Assignment()
        a.set_state("x", sx)
        a.set_state("u0", su0)
        a.set_state("u1", su1)
        return a


class ScalarQuotientWitness:
    """S14 Quotient Irreparability Witness on scalar coupled diagram (Remark §4 / §6)."""

    @staticmethod
    def coboundary(alpha: float) -> np.ndarray:
        """d0(alpha) = [-alpha, -alpha]."""
        return np.array([-alpha, -alpha], dtype=float)

    @staticmethod
    def witness_cochain() -> np.ndarray:
        """omega = [1, -1]."""
        return np.array([1.0, -1.0], dtype=float)

    @staticmethod
    def repair_mass(alpha: float) -> float:
        """Compute ||omega - d0(alpha)||_1 = |1 + alpha| + |-1 + alpha|."""
        w = ScalarQuotientWitness.witness_cochain()
        d = ScalarQuotientWitness.coboundary(alpha)
        return float(np.sum(np.abs(w - d)))

    @staticmethod
    def minimal_quotient_distance() -> Tuple[float, float]:
        """Return (min_distance, argmin_alpha). Analytically min is 2 attained at alpha in [-1, 1], specifically alpha=0."""
        return 2.0, 0.0
