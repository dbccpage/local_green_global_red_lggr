"""Exact rational L1 dual-witness repair solver for higher k-cell cochain complexes.

AuthorityEffect: None.

Implements the exact rational L1 dual-witness repair solver:
    min_{eta in C^{k-1}} ||delta^{(k)} - d^{k-1} eta||_1 = max_{w in ker((d^{k-1})^T), ||w||_inf <= 1} <w, delta^{(k)}>

Provides:
- Exact rational certificate with primal potential eta^{(k-1)}, repaired cochain delta_rep,
  residual r = delta - delta_rep, L1 repair cost, and dual witness w.
- Exact verification that D^T w = 0, ||w||_inf <= 1, duality gap is 0, and
  Phi_1([delta_rep]) = 0 via d^k o d^{k-1} = 0.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

from simplicial_complex import (HigherCellComplex, compute_higher_cell_phi1_holonomy,
                                build_exact_k_cochain_from_potential)


@dataclass(frozen=True)
class ExactL1DualWitnessRepairResult:
    """Exact rational L1 dual-witness repair certificate for a higher k-cell cochain.

    Certifies the optimal solution to:
        min_{eta in C^{k-1}} ||delta^{(k)} - d^{k-1} eta||_1
        = max_{w in ker((d^{k-1})^T), ||w||_inf <= 1} <w, delta^{(k)}>
    """

    degree: int
    primal_potential: dict[tuple[int, ...], Fraction]
    repaired_cochain: dict[tuple[int, ...], Fraction]
    residual: dict[tuple[int, ...], Fraction]
    l1_repair_cost: Fraction
    dual_witness: dict[tuple[int, ...], Fraction]
    dual_objective: Fraction
    duality_gap: Fraction
    is_certified: bool
    is_exact_repair: bool

    def to_json_dict(self) -> dict[str, object]:
        """Serialize certificate to a deterministic dictionary."""
        return {
            "degree": self.degree,
            "primal_potential": {
                str(k): f"{v.numerator}/{v.denominator}"
                for k, v in sorted(self.primal_potential.items())
            },
            "repaired_cochain": {
                str(k): f"{v.numerator}/{v.denominator}"
                for k, v in sorted(self.repaired_cochain.items())
            },
            "residual": {
                str(k): f"{v.numerator}/{v.denominator}"
                for k, v in sorted(self.residual.items())
            },
            "l1_repair_cost": f"{self.l1_repair_cost.numerator}/{self.l1_repair_cost.denominator}",
            "dual_witness": {
                str(k): f"{v.numerator}/{v.denominator}"
                for k, v in sorted(self.dual_witness.items())
            },
            "dual_objective": f"{self.dual_objective.numerator}/{self.dual_objective.denominator}",
            "duality_gap": f"{self.duality_gap.numerator}/{self.duality_gap.denominator}",
            "is_certified": self.is_certified,
            "is_exact_repair": self.is_exact_repair,
        }


def verify_exact_l1_repair(
    complex_k: HigherCellComplex,
    cochain: Mapping[tuple[int, ...], Fraction],
    result: ExactL1DualWitnessRepairResult,
) -> bool:
    """Independently replay an exact certificate, without trusting its flag or LP.

    Uses signed incidence and rational arithmetic only. A floating-point search
    or denominator cutoff can fail to produce a certificate; it cannot weaken
    reconstruction, feasibility or equality of the primal and dual objectives.
    """
    try:
        cells = complex_k.required_k_cells()
        faces = complex_k.required_k_minus_1_cells()
        if result.degree != complex_k.degree or set(cochain) != cells:
            return False
        for values, keys in ((cochain, cells), (result.primal_potential, faces),
                             (result.repaired_cochain, cells), (result.residual, cells),
                             (result.dual_witness, cells)):
            if set(values) != keys or any(type(v) not in (int, Fraction) for v in values.values()):
                return False
        if any(type(v) not in (int, Fraction) for v in
               (result.l1_repair_cost, result.dual_objective, result.duality_gap)):
            return False
        repaired = build_exact_k_cochain_from_potential(complex_k, result.primal_potential)
        if repaired != result.repaired_cochain:
            return False
        residual = {cell: cochain[cell] - repaired[cell] for cell in cells}
        cost = sum((abs(v) for v in residual.values()), Fraction(0))
        dual = sum((result.dual_witness[c] * cochain[c] for c in cells), Fraction(0))
        divergence = {face: Fraction(0) for face in faces}
        for cell in cells:
            w = result.dual_witness[cell]
            if abs(w) > 1:
                return False
            for sign, face in HigherCellComplex.boundary_faces_of_simplex(cell):
                divergence[face] += sign * w
        return (all(v == 0 for v in divergence.values())
                and result.residual == residual
                and result.l1_repair_cost == cost
                and result.dual_objective == dual
                and result.duality_gap == 0 and cost == dual
                and result.is_exact_repair == (cost == 0)
                and compute_higher_cell_phi1_holonomy(complex_k, repaired) == 0)
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


def build_coboundary_matrix(
    complex_k: HigherCellComplex,
) -> tuple[np.ndarray, list[tuple[int, ...]], list[tuple[int, ...]]]:
    """Build the exact matrix D representing d^{k-1} : C^{k-1} -> C^k.

    Row i corresponds to k-simplex sigma_i in sorted required_k_cells.
    Col j corresponds to (k-1)-simplex tau_j in sorted required_k_minus_1_cells.
    Entry D[i, j] = (-1)^p if tau_j is the p-th boundary face of sigma_i, else 0.
    """
    k_cells = sorted(complex_k.required_k_cells())
    km1_cells = sorted(complex_k.required_k_minus_1_cells())
    km1_indices = {face: idx for idx, face in enumerate(km1_cells)}

    m = len(k_cells)
    n = len(km1_cells)
    D = np.zeros((m, n), dtype=float)

    for i, k_cell in enumerate(k_cells):
        for sign, face in HigherCellComplex.boundary_faces_of_simplex(k_cell):
            if face in km1_indices:
                j = km1_indices[face]
                D[i, j] = float(sign)

    return D, k_cells, km1_cells


def solve_exact_rational_l1_dual_witness(
    complex_k: HigherCellComplex,
    k_cochain: Mapping[tuple[int, ...], Fraction],
    max_denominator: int = 1_000_000,
) -> ExactL1DualWitnessRepairResult:
    """Solve the exact rational L1 dual-witness repair problem for k_cochain on complex_k.

    Computes:
        eta* in C^{k-1},  w* in C^k
    such that:
        D^T w* = 0 in Q^n
        ||w*||_inf <= 1
        ||delta - D eta*||_1 = <w*, delta>
        gap = 0
        Phi_1([D eta*]) = 0
    """
    degree = complex_k.degree
    D_mat, k_cells, km1_cells = build_coboundary_matrix(complex_k)
    m = len(k_cells)
    n = len(km1_cells)

    # Closedness does not imply exactness: always reconstruct a potential.
    if set(k_cochain) != set(k_cells):
        raise ValueError("Cochain must cover exactly the declared k-cells")
    if any(type(v) not in (int, Fraction) for v in k_cochain.values()):
        raise ValueError("Cochain coefficients must be exact integers or Fractions")
    if type(max_denominator) is not int or max_denominator < 1:
        raise ValueError("max_denominator must be a positive integer")

    # Formulate Primal LP:
    # min sum_{i=1}^m t_i
    # s.t. D eta - t <= delta
    #     -D eta - t <= -delta
    #      t_i >= 0, eta_j free
    delta_vec = np.array([float(k_cochain[cell]) for cell in k_cells], dtype=float)

    c = np.concatenate([np.ones(m), np.zeros(n)])
    A_ub = np.vstack([
        np.hstack([-np.eye(m), D_mat]),
        np.hstack([-np.eye(m), -D_mat]),
    ])
    b_ub = np.concatenate([delta_vec, -delta_vec])
    bounds = [(0, None)] * m + [(None, None)] * n

    lp_res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not lp_res.success:
        raise RuntimeError(f"Linear programming solver failed: {lp_res.message}")

    eta_float = lp_res.x[m:]
    marginals = lp_res.ineqlin.marginals
    # In SciPy HiGHS, marginals are <= 0 for A x <= b.
    # Multiplying by -1 recovers positive Lagrange multipliers:
    # lambda_plus for D eta - t <= delta
    # lambda_minus for -D eta - t <= -delta
    # Dual variable w = lambda_minus - lambda_plus
    y_plus = -marginals[:m]
    y_minus = -marginals[m:]
    w_float = y_minus - y_plus

    # Rationalize solution
    eta_frac = [Fraction(x).limit_denominator(max_denominator) for x in eta_float]
    w_frac = [Fraction(x).limit_denominator(max_denominator) for x in w_float]
    delta_frac = [Fraction(k_cochain[cell]) for cell in k_cells]
    D_frac = [[Fraction(int(D_mat[i, j])) for j in range(n)] for i in range(m)]

    # Compute repaired cochain delta_rep = D @ eta
    rep_cochain_list = [
        sum((D_frac[i][j] * eta_frac[j] for j in range(n)), Fraction(0, 1))
        for i in range(m)
    ]
    residual_list = [delta_frac[i] - rep_cochain_list[i] for i in range(m)]
    l1_cost = sum((abs(r) for r in residual_list), Fraction(0, 1))

    # Compute dual objective <w, delta>
    dual_obj = sum((w_frac[i] * delta_frac[i] for i in range(m)), Fraction(0, 1))

    # Check dual feasibility: D^T w == 0
    DTw = [
        sum((D_frac[i][j] * w_frac[i] for i in range(m)), Fraction(0, 1))
        for j in range(n)
    ]
    dual_nullspace_satisfied = all(val == Fraction(0, 1) for val in DTw)
    dual_norm_satisfied = all(abs(val) <= Fraction(1, 1) for val in w_frac)
    gap = abs(l1_cost - dual_obj)

    # If minor denominator limit caused tiny gap, clean up using exact complementary slackness
    if (not dual_nullspace_satisfied or gap != Fraction(0, 1)) and l1_cost > Fraction(0, 1):
        # Enforce exact dual signs: w_i = sign(r_i) whenever r_i != 0
        w_reconstructed = []
        for r in residual_list:
            if r > 0:
                w_reconstructed.append(Fraction(1, 1))
            elif r < 0:
                w_reconstructed.append(Fraction(-1, 1))
            else:
                w_reconstructed.append(Fraction(0, 1))
        w_frac = w_reconstructed
        dual_obj = sum((w_frac[i] * delta_frac[i] for i in range(m)), Fraction(0, 1))
        DTw = [
            sum((D_frac[i][j] * w_frac[i] for i in range(m)), Fraction(0, 1))
            for j in range(n)
        ]
        dual_nullspace_satisfied = all(val == Fraction(0, 1) for val in DTw)
        dual_norm_satisfied = all(abs(val) <= Fraction(1, 1) for val in w_frac)
        gap = abs(l1_cost - dual_obj)

    primal_potential = {cell: eta_frac[idx] for idx, cell in enumerate(km1_cells)}
    repaired_cochain = {cell: rep_cochain_list[idx] for idx, cell in enumerate(k_cells)}
    residual = {cell: residual_list[idx] for idx, cell in enumerate(k_cells)}
    dual_witness = {cell: w_frac[idx] for idx, cell in enumerate(k_cells)}

    candidate = ExactL1DualWitnessRepairResult(
        degree=degree,
        primal_potential=primal_potential,
        repaired_cochain=repaired_cochain,
        residual=residual,
        l1_repair_cost=l1_cost,
        dual_witness=dual_witness,
        dual_objective=dual_obj,
        duality_gap=gap,
        is_certified=False,
        is_exact_repair=(l1_cost == Fraction(0, 1)),
    )

    return replace(candidate, is_certified=verify_exact_l1_repair(
        complex_k, k_cochain, candidate))
