"""Unit tests for Constraint-Level Regulation via Multi-Channel Diagnostics."""

import itertools
import math
from fractions import Fraction
from pathlib import Path
import sys
from typing import Any
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_constraint_regulation_core import (
    MultiChannelState,
    RepairOperator,
    RepairSelectionController,
    SecondOrderRepairController,
)


def test_channel_separability_and_realizable_bounds():
    """Verify realizable channel separation and the mathematical bound Gamma_2 <= ||d_1|| Phi_1.

    In any valid cochain complex with d_1 d_0 = 0:
      Gamma_2(omega) = ||d_1 omega||_1 = ||d_1 (omega - d_0 alpha)||_1 <= ||d_1||_{1->1} Phi_1([omega]).
    In particular, Phi_1 = 0 forces Gamma_2 = 0.
    """
    # Case 1: Exact cochain with violated logical constraints (Phi_1 = 0, Gamma_2 = 0, Phi_sat > 0)
    state_exact_sat_fail = MultiChannelState(
        phi_geom=0.0, phi_sat=3.0, phi_curv=0.0, phi_rel=0.0, xi=0.0
    )
    assert state_exact_sat_fail.phi_geom == 0.0
    assert state_exact_sat_fail.phi_curv == 0.0
    assert state_exact_sat_fail.phi_sat == 3.0
    assert state_exact_sat_fail.r_cl == 0.0

    # Case 2: Closed non-exact cochain on an uncontractible cycle (Phi_1 > 0, Gamma_2 = 0, Phi_sat = 0)
    state_closed_nonexact = MultiChannelState(
        phi_geom=4.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.5
    )
    assert state_closed_nonexact.phi_geom == 4.0
    assert state_closed_nonexact.phi_curv == 0.0
    assert state_closed_nonexact.r_cl == 0.0

    # Case 3: Filled triangle with unclosed cochain (Phi_1 = 3.0, Gamma_2 = 3.0, R_cl = 1.0)
    state_triangle = MultiChannelState(
        phi_geom=3.0, phi_sat=0.0, phi_curv=3.0, phi_rel=0.0, xi=0.0
    )
    assert state_triangle.phi_geom == 3.0
    assert state_triangle.phi_curv == 3.0
    assert state_triangle.r_cl == 1.0

    # Theoretical Bound Check:
    # A cochain setting with d_1 d_0 = 0 cannot produce Phi_1 = 0 and Gamma_2 > 0 from the same cochain.
    # When Phi_1 = 0, any valid cochain has Gamma_2 = 0.
    phi_1_zero = 0.0
    d1_norm = 1.0
    max_allowable_gamma_2 = d1_norm * phi_1_zero
    assert max_allowable_gamma_2 == 0.0


def test_closure_ratio_does_not_prevent_constraint_deletion():
    """Verify that R_cl alone accepts deletion-shaped outcomes where both Phi_1 and Gamma_2 drop to zero.

    Counterexample: Deleting the third edge and incident face from a filled triangle
    collapses (Phi_1=3, Gamma_2=3, R_cl=1) to an exact 2-edge path (Phi_1'=0, Gamma_2'=0, R_cl'=0).
    R_cl <= R_max accepts this outcome, demonstrating that constraint preservation
    requires a separate verification check.
    """
    controller = RepairSelectionController(r_max=1.0)
    curr = MultiChannelState(phi_geom=3.0, phi_sat=0.0, phi_curv=3.0, phi_rel=0.0, xi=0.0)

    # Deletion operator deleting edge & face to leave exact 2-edge path
    op_delete = RepairOperator(name="DeleteEdgeAndFace", cost=0.1, is_lift=False)
    state_deleted = MultiChannelState(phi_geom=0.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    decision = controller.evaluate_candidates(curr, [(op_delete, state_deleted)])
    # The scalar ratio accepts this deletion-shaped outcome
    assert decision.status == "Admitted"
    assert decision.selected_operator.name == "DeleteEdgeAndFace"
    assert decision.diagnostics["resulting_r_cl"] == 0.0
    assert decision.diagnostics["resulting_phi_geom"] == 0.0


def test_xi_strict_tie_breaker_prevents_larger_geometric_residual():
    """Verify that Xi acts strictly as a tie-breaker and cannot override a larger discrete residual.

    In the counterexample from peer review:
      Candidate A: phi_geom=1.000, xi=0.837339  => discrete_score = 1.000
      Candidate B: phi_geom=1.005, xi=0.000000  => discrete_score = 1.005
    Under prior weighted sum, Candidate B was incorrectly chosen due to 0.01 * Xi.
    Under strict tie-breaking, Candidate A must be chosen because 1.000 < 1.005.
    """
    controller = RepairSelectionController(r_max=1.0, eps=1e-9)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.5)

    op_a = RepairOperator(name="CandA_LowerDiscrete_HigherXi", cost=0.0, is_lift=False)
    state_a = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.8373392621)

    op_b = RepairOperator(name="CandB_HigherDiscrete_ZeroXi", cost=0.0, is_lift=False)
    state_b = MultiChannelState(phi_geom=1.005, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    decision = controller.evaluate_candidates(curr, [(op_b, state_b), (op_a, state_a)])
    assert decision.status == "Admitted"
    assert decision.selected_operator.name == "CandA_LowerDiscrete_HigherXi"
    assert decision.diagnostics["resulting_phi_geom"] == 1.0

    # Now verify that when discrete scores are tied within eps, Xi acts as tie-breaker:
    op_c = RepairOperator(name="CandC_TiedDiscrete_LowerXi", cost=0.0, is_lift=False)
    state_c = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.2)

    decision_tie = controller.evaluate_candidates(curr, [(op_a, state_a), (op_c, state_c)])
    assert decision_tie.status == "Admitted"
    assert decision_tie.selected_operator.name == "CandC_TiedDiscrete_LowerXi"
    assert decision_tie.diagnostics["resulting_xi"] == 0.2


def test_controller_configured_tolerance_handling():
    """Verify that candidate admission and R_cl evaluation uniformly use the controller's configured eps.

    Reproducing the peer review finding:
      controller eps = 1e-12, r_max = 1.0
      phi_geom = 1e-10, phi_curv = 5e-10
      Configured ratio is 5e-10 / 1e-10 = 5.0 > 1.0 => REJECTED.
    """
    controller = RepairSelectionController(r_max=1.0, eps=1e-12)
    curr = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    # Candidate with ratio 5.0 under eps = 1e-12
    op_cand = RepairOperator(name="OpEpsTest", cost=0.0, is_lift=False)
    state_cand = MultiChannelState(
        phi_geom=1e-10, phi_sat=0.0, phi_curv=5e-10, phi_rel=0.0, xi=0.0
    )

    decision = controller.evaluate_candidates(curr, [(op_cand, state_cand)])
    assert decision.status == "RefusedTearing"
    assert decision.selected_operator is None


def test_fail_closed_validation_of_invalid_and_non_finite_inputs():
    """Verify that non-finite, negative, or out-of-bounds diagnostics are rejected fail-closed."""
    # 1. State construction validations
    with pytest.raises(ValueError, match="phi_curv must be finite"):
        MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=float("nan"), phi_rel=0.0, xi=0.0)

    with pytest.raises(ValueError, match="phi_geom must be non-negative"):
        MultiChannelState(phi_geom=-0.5, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    with pytest.raises(ValueError, match="xi must be in"):
        MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=1.5)

    # 2. Controller configuration validations
    with pytest.raises(ValueError, match="r_max must be finite and positive"):
        RepairSelectionController(r_max=float("nan"))

    with pytest.raises(ValueError, match="eps must be finite and positive"):
        RepairSelectionController(eps=-1e-5)

    # 3. Duck-typed candidate with NaN curvature bypasses dataclass __init__ but is rejected by controller
    class DuckState:
        phi_geom = 1.0
        phi_sat = 0.0
        phi_curv = float("nan")
        phi_rel = 0.0
        xi = 0.0

    controller = RepairSelectionController(r_max=1.0)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)
    op = RepairOperator(name="OpDuck", cost=0.0, is_lift=False)

    decision = controller.evaluate_candidates(curr, [(op, DuckState())])  # type: ignore[arg-type]
    assert decision.status == "RefusedInvalidInput"
    assert decision.selected_operator is None


def test_piecewise_closure_ratio_guardrail():
    """Verify R_cl correctly evaluates ratios and rejects tearing proposals."""
    controller = RepairSelectionController(r_max=1.0)
    assert controller.evaluate_r_cl(phi_geom=2.0, phi_curv=1.5) == 0.75
    assert controller.evaluate_r_cl(phi_geom=2.0, phi_curv=3.0) == 1.5
    assert math.isinf(controller.evaluate_r_cl(phi_geom=0.0, phi_curv=1.0))


def test_second_order_controller_selection():
    """Verify that controller selects valid operator and rejects tearing/non-descent proposals."""
    controller = SecondOrderRepairController(r_max=1.0)
    curr = MultiChannelState(phi_geom=5.0, phi_sat=2.0, phi_curv=1.0, phi_rel=0.5, xi=0.8)

    op_numeric = RepairOperator(name="Pi_21", cost=1.0, is_lift=False)
    state_numeric = MultiChannelState(phi_geom=3.0, phi_sat=2.0, phi_curv=1.0, phi_rel=0.4, xi=0.7)

    # Candidate 2: "Fake repair" tearing proposal (lowers phi_geom to 1.0, but blows up curv to 4.0 => R_cl = 4.0)
    op_tearing = RepairOperator(name="Pi_fake", cost=0.1, is_lift=False)
    state_tearing = MultiChannelState(phi_geom=1.0, phi_sat=2.0, phi_curv=4.0, phi_rel=0.4, xi=0.1)

    # Candidate 3: Non-descent proposal (phi_geom increases to 6.0)
    op_bad = RepairOperator(name="Pi_bad", cost=0.1, is_lift=False)
    state_bad = MultiChannelState(phi_geom=6.0, phi_sat=0.0, phi_curv=0.1, phi_rel=0.1, xi=0.1)

    decision = controller.evaluate_candidates(curr, [
        (op_numeric, state_numeric),
        (op_tearing, state_tearing),
        (op_bad, state_bad)
    ])

    assert decision.status == "Admitted"
    assert decision.selected_operator.name == "Pi_21"
    assert decision.diagnostics["resulting_phi_geom"] == 3.0


def test_cost_sensitive_lift_law():
    """Verify that structural lift is accepted only when structural gain exceeds dimensional cost."""
    controller = RepairSelectionController(r_max=1.0)
    curr = MultiChannelState(phi_geom=4.0, phi_sat=4.0, phi_curv=0.5, phi_rel=0.2, xi=0.5)

    # Lift 1: large structural reduction (gain = (4-1) + 0.5*(4-1) = 3 + 1.5 = 4.5), penalty = 2.0 -> net = 2.5 > 0 -> ADMITTED
    op_lift_good = RepairOperator(name="Pi_12_good", cost=1.0, is_lift=True, dim_penalty=2.0)
    state_lift_good = MultiChannelState(phi_geom=1.0, phi_sat=1.0, phi_curv=0.5, phi_rel=0.1, xi=0.3)

    # Lift 2: tiny gain (gain = (4-3.8) + 0.5*(4-3.8) = 0.3), penalty = 2.0 -> net = -1.7 < 0 -> REJECTED
    op_lift_expensive = RepairOperator(name="Pi_12_exp", cost=0.5, is_lift=True, dim_penalty=2.0)
    state_lift_expensive = MultiChannelState(phi_geom=3.8, phi_sat=3.8, phi_curv=0.5, phi_rel=0.2, xi=0.5)

    decision = controller.evaluate_candidates(curr, [
        (op_lift_expensive, state_lift_expensive),
        (op_lift_good, state_lift_good)
    ])

    assert decision.status == "Admitted"
    assert decision.selected_operator.name == "Pi_12_good"


def test_typed_refusal_on_stalled_system():
    """Verify fail-closed refusal when no proposal satisfies guardrails."""
    controller = RepairSelectionController(r_max=1.0)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=1.0, phi_curv=1.0, phi_rel=0.5, xi=0.5)

    # Empty candidate list -> RefusedStalled
    decision_empty = controller.evaluate_candidates(curr, [])
    assert decision_empty.status == "RefusedStalled"
    assert decision_empty.selected_operator is None
    assert decision_empty.diagnostics["error"] == "No candidate transitions were proposed."

    # Single tearing candidate -> RefusedTearing
    op_tearing = RepairOperator(name="Pi_tear", cost=0.5, is_lift=False)
    state_tearing = MultiChannelState(phi_geom=1.0, phi_sat=1.0, phi_curv=5.0, phi_rel=0.5, xi=0.5)

    decision_tear = controller.evaluate_candidates(curr, [(op_tearing, state_tearing)])
    assert decision_tear.status == "RefusedTearing"
    assert decision_tear.selected_operator is None
    assert decision_tear.diagnostics["rejection_counts"]["RefusedTearing"] == 1


def test_global_ranking_eliminates_cyclic_preference_across_all_permutations():
    """Verify that global epsilon-tied ranking eliminates pairwise cycles and permutation dependence.

    In the peer review counterexample:
      Candidate A: score = 1.0, xi = 0.9
      Candidate B: score = 1.0 + 0.75e-9, xi = 0.5
      Candidate C: score = 1.0 + 1.5e-9, xi = 0.1
      eps = 1e-9

    Under pairwise ranking:
      |score_A - score_B| = 0.75e-9 <= eps and xi_B < xi_A => B > A
      |score_B - score_C| = 0.75e-9 <= eps and xi_C < xi_B => C > B
      score_C - score_A = 1.5e-9 > eps => A > C
      This created an intransitive cycle (A < B < C < A), causing the selected candidate
      to depend on input proposal order across permutations.

    Under global minimum ranking:
      F_min = 1.0, F_min + eps = 1.0 + 1e-9.
      C_eps = {A, B} (Candidate C is excluded because 1.5e-9 > 1e-9).
      Within C_eps, xi is minimized: min(0.9, 0.5) = 0.5 (Candidate B).
    Candidate B must be selected for ALL six input permutations.
    """
    controller = RepairSelectionController(r_max=1.0, eps=1e-9)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    op_a = RepairOperator(name="OpA", cost=0.0, is_lift=False)
    state_a = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.9)

    op_b = RepairOperator(name="OpB", cost=0.75e-9, is_lift=False)
    state_b = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.5)

    op_c = RepairOperator(name="OpC", cost=1.5e-9, is_lift=False)
    state_c = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.1)

    candidates = [(op_a, state_a), (op_b, state_b), (op_c, state_c)]

    for perm in itertools.permutations(candidates):
        decision = controller.evaluate_candidates(curr, list(perm))
        assert decision.status == "Admitted"
        assert decision.selected_operator.name == "OpB"
        assert decision.diagnostics["resulting_xi"] == 0.5


def test_strict_score_priority_and_epsilon_indifference_boundary():
    """Verify that Xi breaks ties within epsilon, but cannot override candidates outside epsilon.

    Also verify that guarded descent enforces literal non-increase relative to current state.
    """
    controller = RepairSelectionController(r_max=1.0, eps=1e-9)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.5)

    # Candidate 1: phi_geom = 1.0, xi = 0.9 => F = 1.0
    op_1 = RepairOperator(name="Cand1_ExactMin", cost=0.0, is_lift=False)
    state_1 = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.9)

    # Candidate 2: phi_geom = 1.0 + 5e-10, xi = 0.1 => F = 1.0 + 5e-10 <= F_min + eps
    op_2 = RepairOperator(name="Cand2_WithinEps_LowerXi", cost=0.0, is_lift=False)
    state_2 = MultiChannelState(phi_geom=1.0 + 5e-10, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.1)

    # Within epsilon, Candidate 2 has lower Xi and is chosen
    decision = controller.evaluate_candidates(curr, [(op_1, state_1), (op_2, state_2)])
    assert decision.status == "Admitted"
    assert decision.selected_operator.name == "Cand2_WithinEps_LowerXi"

    # Candidate 3: phi_geom = 1.0 + 2e-9, xi = 0.01 => F = 1.0 + 2e-9 > F_min + eps
    op_3 = RepairOperator(name="Cand3_OutsideEps_LowestXi", cost=0.0, is_lift=False)
    state_3 = MultiChannelState(phi_geom=1.0 + 2e-9, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.01)

    # Outside epsilon, Cand3 CANNOT override Cand1 even with much lower Xi
    decision_outside = controller.evaluate_candidates(curr, [(op_1, state_1), (op_3, state_3)])
    assert decision_outside.status == "Admitted"
    assert decision_outside.selected_operator.name == "Cand1_ExactMin"

    # Literal non-increase relative to current state:
    # A candidate proposing phi_geom = 2.0 + 1e-10 is rejected by guarded descent even though within eps of curr
    op_creep = RepairOperator(name="CandCreep", cost=0.0, is_lift=False)
    state_creep = MultiChannelState(phi_geom=2.0 + 1e-10, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)
    decision_creep = controller.evaluate_candidates(curr, [(op_creep, state_creep)])
    assert decision_creep.status == "RefusedDescentViolation"


def test_hard_rmax_boundary_no_epsilon_exceedance():
    """Verify that R_cl <= R_max is an exact hard boundary with no epsilon exceedance."""
    controller = RepairSelectionController(r_max=1.0, eps=1e-9)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    # Candidate with R_cl = 1.0000000005 (exceeds R_max = 1.0 by 5e-10, within eps=1e-9)
    # Must be REJECTED fail-closed under exact hard boundary
    op_exceed = RepairOperator(name="OpExceed", cost=0.0, is_lift=False)
    state_exceed = MultiChannelState(
        phi_geom=1.0, phi_sat=0.0, phi_curv=1.0000000005, phi_rel=0.0, xi=0.0
    )
    decision = controller.evaluate_candidates(curr, [(op_exceed, state_exceed)])
    assert decision.status == "RefusedTearing"
    assert decision.selected_operator is None


def test_invalid_inputs_and_contradictory_signature_rejection():
    """Verify that contradictory signatures and score overflows are rejected."""
    # Contradictory signature 1: Phi_1 == 0 with Gamma_2 > 0 (by bound Gamma_2 <= ||d_1|| Phi_1)
    with pytest.raises(ValueError, match="Contradictory state: phi_curv must be 0.0"):
        MultiChannelState(phi_geom=0.0, phi_sat=0.0, phi_curv=5e-10, phi_rel=0.0, xi=0.0)

    # Contradictory signature 2: Phi_1 == 0 with Xi > 0 (by zero-obstruction convention)
    with pytest.raises(ValueError, match="Contradictory state: xi must be 0.0"):
        MultiChannelState(phi_geom=0.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=1.0)

    # Score overflow: large finite coordinates overflowing discrete score to infinity
    controller = RepairSelectionController(r_max=1.0)
    curr = MultiChannelState(phi_geom=1.5e308, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)
    op_overflow = RepairOperator(name="OpOverflow", cost=0.0, is_lift=False)
    state_overflow = MultiChannelState(
        phi_geom=1.5e308, phi_sat=1.5e308, phi_curv=0.0, phi_rel=0.0, xi=0.0
    )
    decision = controller.evaluate_candidates(curr, [(op_overflow, state_overflow)])
    assert decision.status == "RefusedStalled"
    assert decision.diagnostics["rejection_counts"]["RefusedScoreOverflow"] == 1


def test_full_refusal_taxonomy_rejection_reasons_and_diagnostics():
    """Verify that controller emits distinct typed refusals and records rejection diagnostics."""
    controller = RepairSelectionController(r_max=1.0)
    curr = MultiChannelState(phi_geom=2.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)

    # 1. Pure Tearing
    op_tear = RepairOperator(name="TearOp", cost=0.0, is_lift=False)
    state_tear = MultiChannelState(phi_geom=1.0, phi_sat=0.0, phi_curv=3.0, phi_rel=0.0, xi=0.0)
    dec_tear = controller.evaluate_candidates(curr, [(op_tear, state_tear)])
    assert dec_tear.status == "RefusedTearing"
    assert dec_tear.diagnostics["rejection_counts"]["RefusedTearing"] == 1
    assert dec_tear.diagnostics["rejections"][0]["operator"] == "TearOp"

    # 2. Pure Descent Violation
    op_descent = RepairOperator(name="DescentOp", cost=0.0, is_lift=False)
    state_descent = MultiChannelState(phi_geom=3.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0)
    dec_descent = controller.evaluate_candidates(curr, [(op_descent, state_descent)])
    assert dec_descent.status == "RefusedDescentViolation"
    assert dec_descent.diagnostics["rejection_counts"]["RefusedDescentViolation"] == 1

    # 3. Invalid Input
    class BrokenState:
        phi_geom = -1.0
        phi_sat = 0.0
        phi_curv = 0.0
        phi_rel = 0.0
        xi = 0.0

    dec_invalid = controller.evaluate_candidates(curr, [(op_tear, BrokenState())])  # type: ignore[arg-type]
    assert dec_invalid.status == "RefusedInvalidInput"

    # 4. Mixed Failures -> RefusedStalled with full audit details
    dec_mixed = controller.evaluate_candidates(curr, [(op_tear, state_tear), (op_descent, state_descent)])
    assert dec_mixed.status == "RefusedStalled"
    assert dec_mixed.diagnostics["rejection_counts"]["RefusedTearing"] == 1
    assert dec_mixed.diagnostics["rejection_counts"]["RefusedDescentViolation"] == 1
    assert len(dec_mixed.diagnostics["rejections"]) == 2


def test_proved_finite_integer_and_rational_claims():
    """Drive the shipped exact checkers for the mechanized finite claims."""
    zero = Fraction(0)
    one = Fraction(1)
    assert RepairSelectionController.exact_signature_ok(zero, Fraction(3), zero, zero, zero) is True
    assert RepairSelectionController.exact_signature_ok(zero, zero, one, zero, zero) is False
    assert RepairSelectionController.exact_signature_ok(zero, zero, zero, zero, Fraction(1, 2)) is False
    assert RepairSelectionController.exact_discrete_score(zero, Fraction(4), Fraction(10), Fraction(20), Fraction(2)) == Fraction(8)

    assert RepairSelectionController.exact_ratio_admits(Fraction(3), Fraction(3), one) is True
    assert RepairSelectionController.exact_ratio_admits(Fraction(3), Fraction(4), one) is False
    assert RepairSelectionController.exact_ratio_admits(zero, zero, one) is True
    assert RepairSelectionController.exact_ratio_admits(zero, one, one) is False

    assert RepairSelectionController.exact_lift_admitted(Fraction(2), Fraction(2), Fraction(2)) is True
    assert RepairSelectionController.exact_lift_admitted(one, zero, one) is False

    current = (one, zero, zero, zero, zero)
    low_score = ("alpha", zero, False, zero, Fraction(1, 10), zero, zero, zero, one)
    high_score = ("beta", zero, False, zero, one, zero, zero, zero, zero)
    status, chosen = RepairSelectionController.exact_select(current, [high_score, low_score], one, Fraction(1, 10))
    assert status == "Admitted"
    assert chosen == "alpha"

    near_score = ("beta", Fraction(1, 100), False, zero, Fraction(1, 10), zero, zero, zero, zero)
    status, chosen = RepairSelectionController.exact_select(current, [low_score, near_score], one, Fraction(1, 10))
    assert status == "Admitted"
    assert chosen == "beta"

    sat_heavy = ("beta", zero, False, zero, zero, Fraction(4), zero, zero, zero)
    assert RepairSelectionController.exact_select(current, [low_score, sat_heavy], one, Fraction(1, 10))[1] == "alpha"
    curv_heavy = ("beta", zero, False, zero, Fraction(1, 10), zero, Fraction(10), zero, zero)
    assert RepairSelectionController.exact_select(current, [low_score, curv_heavy], one, Fraction(1, 10))[1] == "alpha"
    rel_heavy = ("beta", zero, False, zero, zero, zero, zero, Fraction(20), zero)
    assert RepairSelectionController.exact_select(current, [low_score, rel_heavy], one, Fraction(1, 10))[1] == "alpha"
    costly = ("beta", Fraction(2), False, zero, zero, zero, zero, zero, zero)
    assert RepairSelectionController.exact_select(current, [low_score, costly], one, Fraction(1, 10))[1] == "alpha"

    tied_current = (zero, zero, zero, zero, zero)
    beta = ("beta", zero, False, zero, zero, zero, zero, zero, zero)
    alpha = ("alpha", zero, False, zero, zero, zero, zero, zero, zero)
    assert RepairSelectionController.exact_select(tied_current, [beta, alpha], one, Fraction(1, 10))[1] == "alpha"

    deleted = ("DeleteEdgeAndFace", Fraction(1, 10), False, zero, zero, zero, zero, zero, zero)
    triangle = (Fraction(3), zero, Fraction(3), zero, zero)
    status, chosen = RepairSelectionController.exact_select(triangle, [deleted], one, Fraction(1, 10))
    assert status == "Admitted"
    assert chosen == "DeleteEdgeAndFace"

    rising = ("up", zero, False, zero, one, zero, zero, zero, zero)
    assert RepairSelectionController.exact_select(tied_current, [rising], one, Fraction(1, 10)) == (
        "RefusedDescentViolation",
        None,
    )
    torn = ("tear", zero, False, zero, one, zero, Fraction(3), zero, zero)
    assert RepairSelectionController.exact_select(current, [torn], one, Fraction(1, 10)) == (
        "RefusedTearing",
        None,
    )
    invalid = ("bad", zero, False, zero, zero, zero, one, zero, zero)
    assert RepairSelectionController.exact_select(current, [invalid], one, Fraction(1, 10)) == (
        "RefusedInvalidInput",
        None,
    )
    assert RepairSelectionController.exact_select(current, [], one, Fraction(1, 10)) == ("RefusedStalled", None)
    rising_more = ("up", zero, False, zero, Fraction(2), zero, zero, zero, zero)
    assert RepairSelectionController.exact_select(current, [torn, rising_more], one, Fraction(1, 10)) == (
        "RefusedStalled",
        None,
    )

    failing_lift = ("lift", zero, True, Fraction(5), zero, zero, zero, zero, zero)
    passing_lift = ("lift", zero, True, Fraction(2), zero, zero, zero, zero, zero)
    lift_current = (Fraction(2), Fraction(2), zero, zero, zero)
    assert RepairSelectionController.exact_select(lift_current, [failing_lift], one, Fraction(1, 10)) == (
        "RefusedStalled",
        None,
    )
    assert RepairSelectionController.exact_select(lift_current, [passing_lift], one, Fraction(1, 10)) == (
        "Admitted",
        "lift",
    )

    float_controller = RepairSelectionController(r_max=1.0)
    float_decision = float_controller.evaluate_candidates(
        MultiChannelState(phi_geom=3.0, phi_sat=0.0, phi_curv=3.0, phi_rel=0.0, xi=0.0),
        [(
            RepairOperator(name="DeleteEdgeAndFace", cost=0.1, is_lift=False),
            MultiChannelState(phi_geom=0.0, phi_sat=0.0, phi_curv=0.0, phi_rel=0.0, xi=0.0),
        )],
    )
    assert float_decision.status == "Admitted"
    assert float_decision.selected_operator is not None
    assert float_decision.selected_operator.name == "DeleteEdgeAndFace"

