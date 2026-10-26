"""Integration tests comparing Phi_1, Gamma_2, and Xi orderings on discrete graph instances.

Validates the declared selection priority (Monograph §2 and GuardedDescentEvaluator):
1. Primary Dominance: Phi_1 reduction strictly dominates Xi reduction on discrete graphs.
2. Secondary Dominance: Gamma_2 closure curvature reduction strictly dominates Xi on Phi_1 ties.
3. Tertiary Decisiveness: Xi acts as a decisive diagnostic tie-breaker when (Phi_1, Gamma_2) tie.
4. Boundary Guardrail: R_cl = Gamma_2 / Phi_1 > r_max rejects candidate despite favorable Xi.
5. Infinite Curvature Refusal: Phi_1 <= eps while Gamma_2 > eps yields R_cl = +infinity, rejecting the proposal.
6. Fail-Closed Non-Increase Fence: Any increase in Phi_1 (even sub-epsilon creep) is rejected despite favorable Xi.
7. Antipodal Blindness: Xi(v, -v) == 0 confirms that spectral trace distance cannot distinguish
   orientation sign, which must be certified combinatorially.
8. Full Multi-Candidate Ordering: Verifies complete ordering of competing cochains on a cell complex.
"""

import math
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np
import pytest
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_operator_lifts_core import (
    DensityOperator,
    DiagnosticState,
    GuardedDescentEvaluator,
    OperatorLifts,
)


class DiscreteComplex:
    """Finite 2-dimensional cell complex (graph with 2-cells)."""

    def __init__(
        self,
        num_vertices: int,
        edges: List[Tuple[int, int]],
        faces: List[List[int]],  # list of signed edge incidence vectors
    ) -> None:
        self.num_vertices = num_vertices
        self.edges = edges
        self.num_edges = len(edges)
        self.num_faces = len(faces)

        # 1-boundary matrix B (edges x vertices): (B f)_e = f(v) - f(u) for e=(u, v)
        self.B = np.zeros((self.num_edges, self.num_vertices), dtype=float)
        for e, (u, v) in enumerate(edges):
            self.B[e, u] = -1.0
            self.B[e, v] = 1.0

        # 2-boundary matrix d1 (faces x edges)
        if faces:
            self.d1 = np.array(faces, dtype=float)
            if self.d1.shape != (self.num_faces, self.num_edges):
                raise ValueError("faces shape does not match (num_faces, num_edges)")
        else:
            self.d1 = np.zeros((0, self.num_edges), dtype=float)

    def compute_phi_1(self, omega: Sequence[float]) -> Tuple[float, np.ndarray]:
        """Compute Phi_1 = min ||omega - B alpha||_1 via LP."""
        arr = np.asarray(omega, dtype=float)
        m = self.num_edges
        n = self.num_vertices

        # min sum(h^+ + h^-) s.t. h^+ - h^- + B alpha = arr, h^+, h^- >= 0
        c = np.concatenate([np.ones(m), np.ones(m), np.zeros(n)])
        A_eq = np.hstack([np.eye(m), -np.eye(m), self.B])
        b_eq = arr
        bounds = [(0, None)] * (2 * m) + [(None, None)] * n

        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Phi_1 LP failed: {res.message}")

        phi_1 = float(res.fun)
        h = res.x[:m] - res.x[m : 2 * m]
        return phi_1, h

    def compute_gamma_2(self, omega: Sequence[float]) -> float:
        """Compute Gamma_2 = ||d_1 omega||_1."""
        if self.num_faces == 0:
            return 0.0
        arr = np.asarray(omega, dtype=float)
        curv = np.dot(self.d1, arr)
        return float(np.sum(np.abs(curv)))

    def verify_complex_integrity(self) -> bool:
        """Verify the d_1 d_0 == 0 chain complex identity."""
        if self.num_faces == 0 or self.num_edges == 0:
            return True
        d1_d0 = np.dot(self.d1, self.B)
        return bool(np.allclose(d1_d0, 0.0, atol=1e-12))

    @property
    def d1_operator_norm_1(self) -> float:
        """Induced l1 -> l1 operator norm of d_1: maximum column sum of |d_1|."""
        if self.num_faces == 0:
            return 0.0
        return float(np.max(np.sum(np.abs(self.d1), axis=0)))

    def evaluate_state(
        self,
        omega: Sequence[float],
        target_ref: Sequence[float],
        evaluator: GuardedDescentEvaluator,
    ) -> DiagnosticState:
        """Evaluate full diagnostic state (phi_1, gamma_2, r_cl, xi) for cochain omega."""
        phi_1, _ = self.compute_phi_1(omega)
        gamma_2 = self.compute_gamma_2(omega)
        r_cl = evaluator.compute_r_cl(phi_1, gamma_2)

        # Compute Xi trace distance to target reference with native zero-cochain handling
        omega_arr = np.asarray(omega, dtype=float)
        target_arr = np.asarray(target_ref, dtype=float)
        omega_mass = float(np.sum(np.abs(omega_arr)))
        target_mass = float(np.sum(np.abs(target_arr)))

        if omega_mass <= 1e-15:
            # Native clean closure: zero cochain has no projective direction
            xi = 0.0 if target_mass <= 1e-15 else 1.0
        elif target_mass <= 1e-15:
            xi = 1.0
        else:
            rho_omega = OperatorLifts.density_lift(omega_arr)
            rho_target = OperatorLifts.density_lift(target_arr)
            xi = OperatorLifts.trace_distance(rho_omega, rho_target)

        return DiagnosticState(phi_1=phi_1, gamma_2=gamma_2, r_cl=r_cl, xi=xi)


@pytest.fixture
def theta_complex() -> DiscreteComplex:
    """Theta graph with 4 vertices, 5 edges, and 2 oriented faces.

    Edges:
      e0: (0, 1)
      e1: (1, 2)
      e2: (0, 2)
      e3: (0, 3)
      e4: (3, 2)

    Cycles / Faces:
      f0: e0 + e1 - e2  (upper cycle: 0 -> 1 -> 2 <- 0)
      f1: e3 + e4 - e2  (lower cycle: 0 -> 3 -> 2 <- 0)
    """
    edges = [(0, 1), (1, 2), (0, 2), (0, 3), (3, 2)]
    faces = [
        [1.0, 1.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 1.0, 1.0],
    ]
    return DiscreteComplex(num_vertices=4, edges=edges, faces=faces)


@pytest.fixture
def triangle_complex() -> DiscreteComplex:
    """Oriented triangle C_3 with 3 vertices, 3 edges, and 1 face."""
    edges = [(0, 1), (1, 2), (2, 0)]
    faces = [[1.0, 1.0, 1.0]]
    return DiscreteComplex(num_vertices=3, edges=edges, faces=faces)


def test_primary_dominance_phi1_over_xi_on_discrete_theta_graph(theta_complex):
    """Verify that lower Phi_1 strictly dominates lower Xi on discrete cochains.

    Candidate A achieves a true reduction in 1-cycle obstruction Phi_1, but has higher Xi.
    Candidate B retains high Phi_1, but has lower Xi to the target reference.
    The evaluator MUST accept Candidate A and reject Candidate B.
    """
    evaluator = GuardedDescentEvaluator(r_max=2.0)
    target_ref = [1.0, 1.0, 0.0, 0.0, 0.0]

    # Current cochain: circulation on upper cycle, Phi_1 = 3.0
    omega_curr = [1.0, 1.0, -1.0, 0.0, 0.0]
    state_curr = theta_complex.evaluate_state(omega_curr, target_ref, evaluator)
    assert math.isclose(state_curr.phi_1, 3.0, abs_tol=1e-5)

    # Candidate A: partially repairs circulation, reducing Phi_1 to 1.5, Xi = 0.577
    omega_cand_a = [0.5, 0.5, -0.5, 0.0, 0.0]
    state_a = theta_complex.evaluate_state(omega_cand_a, target_ref, evaluator)
    assert math.isclose(state_a.phi_1, 1.5, abs_tol=1e-5)

    # Candidate B: worsens Phi_1 to 3.2, but modifies coordinate distribution to get low Xi = 0.250
    omega_cand_b = [1.5, 1.5, -0.2, 0.0, 0.0]
    state_b = theta_complex.evaluate_state(omega_cand_b, target_ref, evaluator)
    assert math.isclose(state_b.phi_1, 3.2, abs_tol=1e-5)
    assert state_b.xi < state_a.xi  # B looks better spectrally (0.250 < 0.577)

    # 1. Direct comparison: Candidate A is strictly preferred to Candidate B
    assert evaluator.compare_candidates(state_a, state_b) == -1
    assert evaluator.compare_candidates(state_b, state_a) == 1

    # 2. Transition evaluations from current state
    acc_a, msg_a = evaluator.evaluate_transition(state_curr, state_a)
    assert acc_a is True
    assert "Primary quotient residual Phi_1 decreased" in msg_a

    acc_b, msg_b = evaluator.evaluate_transition(state_curr, state_b)
    assert acc_b is False
    assert "Primary quotient residual Phi_1 increased" in msg_b


def test_secondary_dominance_gamma2_over_xi_on_tied_phi1(theta_complex):
    """Verify that when Phi_1 is tied, lower Gamma_2 strictly dominates lower Xi.

    Two candidates have identical 1-cycle obstruction Phi_1 = 1.0.
    Candidate A has lower closure defect Gamma_2 = 1.0 but higher Xi = 1.0.
    Candidate B has higher closure defect Gamma_2 = 2.0 but lower Xi = 0.0.
    The evaluator MUST prefer Candidate A.
    """
    evaluator = GuardedDescentEvaluator(r_max=2.5)
    target_ref = [0.0, 0.0, -1.0, 0.0, 0.0]

    # Candidate A: Edge 0 has Phi_1 = 1.0, Gamma_2 = 1.0, Xi = 1.0
    omega_a = [1.0, 0.0, 0.0, 0.0, 0.0]
    state_a = theta_complex.evaluate_state(omega_a, target_ref, evaluator)

    # Candidate B: Edge 2 (shared between faces) has Phi_1 = 1.0, Gamma_2 = 2.0, Xi = 0.0
    omega_b = [0.0, 0.0, -1.0, 0.0, 0.0]
    state_b = theta_complex.evaluate_state(omega_b, target_ref, evaluator)

    assert math.isclose(state_a.phi_1, 1.0, abs_tol=1e-5)
    assert math.isclose(state_b.phi_1, 1.0, abs_tol=1e-5)
    assert math.isclose(state_a.phi_1, state_b.phi_1, abs_tol=1e-5)

    # Candidate A has lower Gamma_2 (1.0 < 2.0)
    assert state_a.gamma_2 < state_b.gamma_2
    assert math.isclose(state_a.gamma_2, 1.0, abs_tol=1e-5)
    assert math.isclose(state_b.gamma_2, 2.0, abs_tol=1e-5)

    # Candidate B has lower Xi (0.0 < 1.0)
    assert state_b.xi < state_a.xi
    assert math.isclose(state_b.xi, 0.0, abs_tol=1e-5)
    assert math.isclose(state_a.xi, 1.0, abs_tol=1e-5)

    # Candidate A must be strictly preferred because Gamma_2 dominates Xi under tied Phi_1
    pref = evaluator.compare_candidates(state_a, state_b)
    assert pref == -1, f"Expected cand_a to win on Gamma_2, got {pref}"
    assert evaluator.compare_candidates(state_b, state_a) == 1


def test_tertiary_decisiveness_xi_on_tied_phi1_and_gamma2(theta_complex):
    """Verify that when both Phi_1 and Gamma_2 tie, Xi acts as the decisive tie-breaker."""
    evaluator = GuardedDescentEvaluator(r_max=2.0)
    target_ref = [1.0, 0.5, 0.0, 0.0, 0.0]

    # State current
    state_curr = DiagnosticState(phi_1=1.0, gamma_2=0.5, r_cl=0.5, xi=0.8)

    # Candidate A: identical Phi_1 and Gamma_2, lower Xi = 0.3
    state_cand_a = DiagnosticState(phi_1=1.0, gamma_2=0.5, r_cl=0.5, xi=0.3)

    # Candidate B: identical Phi_1 and Gamma_2, higher Xi = 0.7
    state_cand_b = DiagnosticState(phi_1=1.0, gamma_2=0.5, r_cl=0.5, xi=0.7)

    # Candidate A is strictly preferred to Candidate B
    assert evaluator.compare_candidates(state_cand_a, state_cand_b) == -1
    assert evaluator.compare_candidates(state_cand_b, state_cand_a) == 1

    # Transition from curr to A is accepted on Xi tie-break
    acc_a, msg_a = evaluator.evaluate_transition(state_curr, state_cand_a)
    assert acc_a is True
    assert "Xi decreased on tie-break" in msg_a

    # Transition from curr to B is accepted as well (Xi decreased from 0.8 to 0.7)
    acc_b, msg_b = evaluator.evaluate_transition(state_curr, state_cand_b)
    assert acc_b is True


def test_guardrail_refusal_exceeding_rmax_rejects_candidate():
    """Verify that boundary ratio R_cl > r_max rejects a candidate even when Xi is minimized."""
    evaluator = GuardedDescentEvaluator(r_max=1.0)
    state_curr = DiagnosticState(phi_1=1.0, gamma_2=0.8, r_cl=0.8, xi=0.9)

    # Candidate: tied Phi_1, lower Xi = 0.1, but high Gamma_2 = 1.5 -> R_cl = 1.5 > r_max = 1.0
    state_blown = DiagnosticState(phi_1=1.0, gamma_2=1.5, r_cl=1.5, xi=0.1)

    accepted, reason = evaluator.evaluate_transition(state_curr, state_blown)
    assert accepted is False
    assert "Closure ratio R_cl" in reason or "Secondary closure curvature Gamma_2 increased" in reason


def test_infinite_curvature_branch_rejection():
    """Verify that Phi_1 <= eps with Gamma_2 > eps yields R_cl = None (+inf) and is rejected.

    Note on Mathematical Realizability vs Numerical Classification:
    For any exact cochain complex with d_1 d_0 = 0, Gamma_2(v) <= ||d_1||_{1->1} Phi_1(v).
    Thus exact Phi_1(v) = 0 mathematically implies Gamma_2(v) = 0; an exact cochain with
    Phi_1 = 0 and Gamma_2 > 0 cannot exist on a valid complex.
    However, with floating-point numerical thresholding (eps), an approximate state may have
    Phi_1 <= eps (classified numerically as resolved) while Gamma_2 > eps persists.
    This fixture tests the evaluator's fail-closed guardrail against such numerical-threshold
    or inconsistent states, ensuring R_cl = None (+infinity) halts descent.
    """
    evaluator = GuardedDescentEvaluator(r_max=1.0, eps=1e-5)

    # Compute R_cl when Phi_1 = 0 and Gamma_2 = 0.5
    r_cl = evaluator.compute_r_cl(phi_1=0.0, gamma_2=0.5)
    assert r_cl is None  # represents +infinity

    state_curr = DiagnosticState(phi_1=1.0, gamma_2=0.2, r_cl=0.2, xi=0.5)
    # Candidate with vanished Phi_1 but persistent curvature tearing (numerical fixture)
    state_tear = DiagnosticState(phi_1=0.0, gamma_2=0.5, r_cl=None, xi=0.1)

    # In GuardedDescentEvaluator, hard feasibility check rejects state_tear because R_cl is None (+inf)
    acc, reason = evaluator.evaluate_transition(state_curr, state_tear)
    assert acc is False
    assert "+infinity" in reason

    state_zero_curr = DiagnosticState(phi_1=0.0, gamma_2=0.0, r_cl=0.0, xi=0.5)
    acc_z, reason_z = evaluator.evaluate_transition(state_zero_curr, state_tear)
    assert acc_z is False
    assert "+infinity" in reason_z


def test_strict_non_increase_fence_rejects_sub_epsilon_creep():
    """Verify that any increase in Phi_1 (even sub-epsilon creep) is strictly rejected despite favorable Xi."""
    evaluator = GuardedDescentEvaluator(r_max=1.0, eps=1e-6)
    state_curr = DiagnosticState(phi_1=1.0, gamma_2=0.2, r_cl=0.2, xi=0.8)

    # Candidate has slightly worse Phi_1 (+ 1e-8) with perfect Xi = 0.0
    state_creep = DiagnosticState(phi_1=1.0 + 1e-8, gamma_2=0.2, r_cl=0.2, xi=0.0)

    accepted, reason = evaluator.evaluate_transition(state_curr, state_creep)
    assert accepted is False
    assert "Primary quotient residual Phi_1 increased" in reason


def test_antipodal_blindness_demonstrates_need_for_topological_orientation(triangle_complex):
    """Verify that Xi(v, -v) == 0 cannot distinguish orientation sign, requiring combinatorial topology.

    On oriented triangle C_3:
    v = [1.0, 1.0, 1.0] has counter-clockwise circulation holonomy +3.
    -v = [-1.0, -1.0, -1.0] has clockwise circulation holonomy -3.
    Their trace distance Xi(v, -v) == 0.0!
    """
    v = [1.0, 1.0, 1.0]
    neg_v = [-1.0, -1.0, -1.0]

    rho_v = OperatorLifts.density_lift(v)
    rho_neg_v = OperatorLifts.density_lift(neg_v)

    # Spectral trace distance is zero
    xi_dist = OperatorLifts.trace_distance(rho_v, rho_neg_v)
    assert xi_dist == 0.0

    # But topological holonomy around face differs by sign (+3 vs -3)
    holonomy_v = float(np.dot(triangle_complex.d1[0], v))
    holonomy_neg_v = float(np.dot(triangle_complex.d1[0], neg_v))
    assert holonomy_v == 3.0
    assert holonomy_neg_v == -3.0
    assert holonomy_v != holonomy_neg_v

    # Combinatorial orientation must be maintained externally; spectral representation is blind to it
    assert math.isclose(abs(holonomy_v), abs(holonomy_neg_v))


def test_full_candidate_ranking_on_multicycle_cell_complex(theta_complex):
    """Verify complete ordering of multiple competing cochain proposals on a cell complex."""
    evaluator = GuardedDescentEvaluator(r_max=1.0)
    target_ref = [1.0, 1.0, 0.0, 0.0, 0.0]

    state_curr = DiagnosticState(phi_1=2.0, gamma_2=0.5, r_cl=0.25, xi=0.8)

    # Five competing proposals:
    # Cand 0: primary descent (Phi_1 = 1.0, Gamma_2 = 0.5, Xi = 0.9)
    # Cand 1: primary descent, better tie-break (Phi_1 = 1.0, Gamma_2 = 0.2, Xi = 0.4)
    # Cand 2: secondary descent on Phi_1 tie (Phi_1 = 2.0, Gamma_2 = 0.1, Xi = 0.7)
    # Cand 3: tertiary descent on (Phi_1, Gamma_2) tie (Phi_1 = 2.0, Gamma_2 = 0.5, Xi = 0.3)
    # Cand 4: worsening Phi_1 (Phi_1 = 3.0, Gamma_2 = 0.0, Xi = 0.0)
    cands = [
        DiagnosticState(phi_1=1.0, gamma_2=0.5, r_cl=0.5, xi=0.9),
        DiagnosticState(phi_1=1.0, gamma_2=0.2, r_cl=0.2, xi=0.4),
        DiagnosticState(phi_1=2.0, gamma_2=0.1, r_cl=0.05, xi=0.7),
        DiagnosticState(phi_1=2.0, gamma_2=0.5, r_cl=0.25, xi=0.3),
        DiagnosticState(phi_1=3.0, gamma_2=0.0, r_cl=0.0, xi=0.0),
    ]

    # 1. Unsorted candidate evaluations preserving original input order
    evals = evaluator.evaluate_candidates(state_curr, cands)
    assert [e[0] for e in evals] == [0, 1, 2, 3, 4]
    assert evals[0][1] is True  # Cand 0 accepted
    assert evals[1][1] is True  # Cand 1 accepted
    assert evals[2][1] is True  # Cand 2 accepted
    assert evals[3][1] is True  # Cand 3 accepted
    assert evals[4][1] is False  # Cand 4 rejected

    # 2. Sorted candidate ranking by declared selection priority
    ranked = evaluator.rank_candidates(state_curr, cands)
    # Cand 1 is best overall (Phi_1 = 1.0, Gamma_2 = 0.2, Xi = 0.4)
    # Cand 0 is second best (Phi_1 = 1.0, Gamma_2 = 0.5, Xi = 0.9)
    # Cand 2 is third best (Phi_1 = 2.0, Gamma_2 = 0.1, Xi = 0.7)
    # Cand 3 is fourth best (Phi_1 = 2.0, Gamma_2 = 0.5, Xi = 0.3)
    # Cand 4 is rejected and ranks last
    assert [r[0] for r in ranked] == [1, 0, 2, 3, 4]
    assert ranked[0][1] is True
    assert ranked[1][1] is True
    assert ranked[2][1] is True
    assert ranked[3][1] is True
    assert ranked[4][1] is False

    # Pairwise comparison verifies Cand 1 is the best overall:
    assert evaluator.compare_candidates(cands[1], cands[0]) == -1
    assert evaluator.compare_candidates(cands[1], cands[2]) == -1
    assert evaluator.compare_candidates(cands[1], cands[3]) == -1
    assert evaluator.compare_candidates(cands[1], cands[4]) == -1


def test_comparator_transitivity_no_preference_cycles(theta_complex):
    """Verify that candidate comparison is strictly transitive and admits no preference cycles.

    Review reproduction case:
    Phi_1 values: A = 1.00000000, B = 1.00000075, C = 1.00000150.
    Gamma_2 values: A = 1.5000030, B = 1.5000015, C = 1.5000000.
    Under pairwise epsilon ties, B < A, C < B, and A < C formed a preference cycle.
    Under exact lexicographical comparison of stored finite values:
    A.phi_1 < B.phi_1 < C.phi_1, so A is strictly preferred to B, B to C, and A to C.
    No preference cycle exists.
    """
    evaluator = GuardedDescentEvaluator(r_max=2.0)
    target_ref = [1.0, 0.0, 0.0, 0.0, 0.0]

    phi_a, gamma_a = 1.00000000, 1.5000030
    phi_b, gamma_b = 1.00000075, 1.5000015
    phi_c, gamma_c = 1.00000150, 1.5000000

    # Realizable cochains on theta complex: omega = (Phi_1, 0, 0, Gamma_2 - Phi_1, 0)
    omega_a = [phi_a, 0.0, 0.0, gamma_a - phi_a, 0.0]
    omega_b = [phi_b, 0.0, 0.0, gamma_b - phi_b, 0.0]
    omega_c = [phi_c, 0.0, 0.0, gamma_c - phi_c, 0.0]

    state_a = theta_complex.evaluate_state(omega_a, target_ref, evaluator)
    state_b = theta_complex.evaluate_state(omega_b, target_ref, evaluator)
    state_c = theta_complex.evaluate_state(omega_c, target_ref, evaluator)

    # Verify that all satisfy ratio ceiling R_cl <= 2.0
    assert state_a.r_cl <= 2.0
    assert state_b.r_cl <= 2.0
    assert state_c.r_cl <= 2.0

    # Comparisons must be strictly transitive without cycles:
    # A has lowest Phi_1 -> A preferred to B and C
    comp_ba = evaluator.compare_candidates(state_b, state_a)
    comp_cb = evaluator.compare_candidates(state_c, state_b)
    comp_ac = evaluator.compare_candidates(state_a, state_c)

    assert comp_ba == 1   # A is preferred to B
    assert comp_cb == 1   # B is preferred to C
    assert comp_ac == -1  # A is preferred to C

    # Strictly transitive: A preferred to B and B preferred to C implies A preferred to C
    assert not (comp_ba == -1 and comp_cb == -1 and comp_ac == 1)


def test_ratio_guard_consistent_between_transition_and_comparison(theta_complex):
    """Verify that ratio ceiling R_cl <= r_max is consistently enforced across transition and comparison.

    Review reproduction case:
    theta complex with r_max = 1.5:
    omega_curr = (2, 0, 0, 0, 0) -> Phi_1 = 2.0, Gamma_2 = 2.0, R_cl = 1.0.
    omega_cand = (0, 0, -1.5, 0, 0) -> Phi_1 = 1.5, Gamma_2 = 3.0, R_cl = 2.0.
    Candidate reduces Phi_1 from 2.0 to 1.5, but violates R_cl <= 1.5 (R_cl = 2.0).
    Both evaluate_transition and compare_candidates MUST reject the candidate as infeasible.
    """
    evaluator = GuardedDescentEvaluator(r_max=1.5)
    target_ref = [1.0, 0.0, 0.0, 0.0, 0.0]

    omega_curr = [2.0, 0.0, 0.0, 0.0, 0.0]
    omega_cand = [0.0, 0.0, -1.5, 0.0, 0.0]

    state_curr = theta_complex.evaluate_state(omega_curr, target_ref, evaluator)
    state_cand = theta_complex.evaluate_state(omega_cand, target_ref, evaluator)

    assert math.isclose(state_curr.phi_1, 2.0, abs_tol=1e-5)
    assert math.isclose(state_curr.gamma_2, 2.0, abs_tol=1e-5)
    assert math.isclose(state_curr.r_cl, 1.0, abs_tol=1e-5)

    assert math.isclose(state_cand.phi_1, 1.5, abs_tol=1e-5)
    assert math.isclose(state_cand.gamma_2, 3.0, abs_tol=1e-5)
    assert math.isclose(state_cand.r_cl, 2.0, abs_tol=1e-5)

    # 1. evaluate_transition: rejected because candidate R_cl (2.0) exceeds r_max (1.5)
    acc, msg = evaluator.evaluate_transition(state_curr, state_cand)
    assert acc is False
    assert "exceeds policy ceiling" in msg

    # 2. compare_candidates: current state preferred because candidate violates r_max
    assert evaluator.compare_candidates(state_curr, state_cand) == -1
    assert evaluator.compare_candidates(state_cand, state_curr) == 1


def test_zero_cochain_clean_closure_integration(theta_complex):
    """Verify that zero cochains evaluate cleanly and terminate before density diagnostics."""
    evaluator = GuardedDescentEvaluator(r_max=1.0)
    target_ref = [1.0, 1.0, 0.0, 0.0, 0.0]

    omega_curr = [1.0, 1.0, -1.0, 0.0, 0.0]
    state_curr = theta_complex.evaluate_state(omega_curr, target_ref, evaluator)

    # Zero cochain (clean closure, zero residual)
    omega_zero = [0.0, 0.0, 0.0, 0.0, 0.0]
    state_zero = theta_complex.evaluate_state(omega_zero, target_ref, evaluator)

    assert state_zero.phi_1 == 0.0
    assert state_zero.gamma_2 == 0.0
    assert state_zero.r_cl == 0.0
    assert state_zero.xi == 1.0  # maximal distortion to nonzero target_ref

    # Evaluating transition to zero cochain is accepted on primary quotient residual reduction
    acc, msg = evaluator.evaluate_transition(state_curr, state_zero)
    assert acc is True
    assert "Primary quotient residual Phi_1 decreased" in msg

    # When target_ref is also zero
    state_zero_target = theta_complex.evaluate_state(omega_zero, omega_zero, evaluator)
    assert state_zero_target.xi == 0.0


def test_chain_complex_compatibility_bound_and_exact_closure(theta_complex, triangle_complex):
    r"""Verify the chain complex identity d_1 d_0 == 0 and the compatibility bound.

    Theorem:
    For any cochain complex with d_1 d_0 = 0:
        Gamma_2(v) <= ||d_1||_{1->1} * Phi_1(v)
    Consequently, Phi_1(v) == 0 implies Gamma_2(v) == 0.
    """
    assert theta_complex.verify_complex_integrity()
    assert triangle_complex.verify_complex_integrity()

    norm_d1 = theta_complex.d1_operator_norm_1
    assert norm_d1 == 2.0  # maximum column sum of |d_1| on theta complex

    # Test across a variety of test cochains
    test_cochains = [
        [1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0],
        [1.0, 1.0, -1.0, 0.0, 0.0],
        [0.5, -0.5, 0.2, -0.1, 0.3],
        [2.0, -1.0, 0.0, 1.5, -0.5],
    ]

    for vec in test_cochains:
        phi_1, _ = theta_complex.compute_phi_1(vec)
        gamma_2 = theta_complex.compute_gamma_2(vec)
        assert gamma_2 <= norm_d1 * phi_1 + 1e-12, (
            f"Compatibility bound violated: Gamma_2={gamma_2} > {norm_d1} * Phi_1={phi_1}"
        )

    # Verify coboundary (exact cycle): Phi_1 == 0 -> Gamma_2 == 0
    alpha = np.array([1.0, 2.0, -1.0, 0.5])
    coboundary = np.dot(theta_complex.B, alpha)
    phi_exact, _ = theta_complex.compute_phi_1(coboundary)
    gamma_exact = theta_complex.compute_gamma_2(coboundary)
    assert math.isclose(phi_exact, 0.0, abs_tol=1e-9)
    assert math.isclose(gamma_exact, 0.0, abs_tol=1e-9)

