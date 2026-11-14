"""Regressions for v1.2.1 republication patch."""
from __future__ import annotations

import numpy as np
import pytest

from epk_core import (
    BoundarySlice,
    ComposedTrajectory,
    EvaluatedPathKernel,
    EvaluatorSet,
    State,
    TrajectorySegment,
    calculate_action_evaluator_residual,
    calculate_evaluator_residual,
    calculate_hybrid_evaluator_residual,
    calculate_proposal_cost_risk_evaluator_residual,
)


class TestRepublicationV121Regressions:
    """Regressions for v1.2.1 republication patch."""

    def test_section4_action_residual_independent_of_proposal_mass(self):
        """
        BLOCKER 1 Regression: Section 4 action residual R_Eval = sum Delta_E * exp(-beta * (A_1 + A_2))
        must remain strictly invariant to proposal probabilities P_theta(gamma) != 1.
        In contrast, proposal_cost_risk and hybrid residuals scale with P_theta product.
        """
        a, b, c = map(State, ["a", "b", "c"])
        # Trajectory pair with P_theta = 0.25 on each segment
        x_sub = TrajectorySegment(a, b, ("x",), proposal_prob=0.25, raw_action=0.4, cost=1.0, risk=0.2)
        y_sub = TrajectorySegment(b, c, ("y",), proposal_prob=0.25, raw_action=0.6, cost=1.5, risk=0.3)
        comp_sub = ComposedTrajectory(x_sub, y_sub)

        # Identical trajectory pair with unit proposal probabilities
        x_unit = TrajectorySegment(a, b, ("x",), proposal_prob=1.0, raw_action=0.4, cost=1.0, risk=0.2)
        y_unit = TrajectorySegment(b, c, ("y",), proposal_prob=1.0, raw_action=0.6, cost=1.5, risk=0.3)
        comp_unit = ComposedTrajectory(x_unit, y_unit)

        # Evaluator set producing NGD (Delta_E = 0 - 1*1 = -1)
        eval_set = EvaluatorSet(lambda _: 1, lambda _: 1, lambda _: 0)

        # 1. Action residual is strictly independent of proposal probability
        r_action_sub = EvaluatedPathKernel.compute_action_evaluator_residual([comp_sub], eval_set, beta=1.0)
        r_action_unit = EvaluatedPathKernel.compute_action_evaluator_residual([comp_unit], eval_set, beta=1.0)
        assert pytest.approx(r_action_sub) == r_action_unit
        # Exact Section 4 theoretical value: Delta_E * exp(-beta * (A_1 + A_2)) = -1 * exp(-1.0 * 1.0) = -exp(-1.0)
        expected_section4_action_res = -float(np.exp(-1.0))
        assert pytest.approx(r_action_sub) == expected_section4_action_res

        # compute_evaluator_residual in default "action" mode matches compute_action_evaluator_residual
        r_default = EvaluatedPathKernel.compute_evaluator_residual([comp_sub], eval_set, beta=1.0)
        assert pytest.approx(r_default) == r_action_sub

        # 2. Proposal-cost-risk and hybrid residuals scale with proposal mass product (0.25 * 0.25 = 0.0625)
        r_pcr_sub = EvaluatedPathKernel.compute_proposal_cost_risk_evaluator_residual([comp_sub], eval_set, lam=1.0, mu=1.0)
        r_pcr_unit = EvaluatedPathKernel.compute_proposal_cost_risk_evaluator_residual([comp_unit], eval_set, lam=1.0, mu=1.0)
        assert pytest.approx(r_pcr_sub) == r_pcr_unit * 0.0625
        assert pytest.approx(r_pcr_sub) != r_pcr_unit

        r_hyb_sub = EvaluatedPathKernel.compute_hybrid_evaluator_residual([comp_sub], eval_set, beta=1.0, lam=1.0, mu=1.0)
        r_hyb_unit = EvaluatedPathKernel.compute_hybrid_evaluator_residual([comp_unit], eval_set, beta=1.0, lam=1.0, mu=1.0)
        assert pytest.approx(r_hyb_sub) == r_hyb_unit * 0.0625
        assert pytest.approx(r_hyb_sub) != r_hyb_unit

    def test_residual_mode_differentiation(self):
        """Verifies distinct numerical values and contracts across the three residual modes."""
        a, b, c = map(State, ["a", "b", "c"])
        x = TrajectorySegment(a, b, ("x",), proposal_prob=0.8, raw_action=0.5, cost=1.0, risk=0.2)
        y = TrajectorySegment(b, c, ("y",), proposal_prob=0.5, raw_action=0.5, cost=1.0, risk=0.2)
        comp = ComposedTrajectory(x, y)
        eval_set = EvaluatorSet(lambda _: 1, lambda _: 1, lambda _: 0)

        r_action = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=1.0, mode="action")
        r_pcr = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, lam=1.0, mu=1.0, mode="proposal_cost_risk")
        r_hybrid = EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=1.0, lam=1.0, mu=1.0, mode="hybrid")

        # All three are non-zero and mutually distinct
        assert r_action != 0.0
        assert r_pcr != 0.0
        assert r_hybrid != 0.0
        assert r_action != r_pcr
        assert r_action != r_hybrid
        assert r_pcr != r_hybrid

    def test_fail_closed_on_invalid_modes(self):
        """Verifies fail-closed ValueError on invalid or unlisted kernel and residual modes."""
        a, b, c = map(State, ["a", "b", "c"])
        x = TrajectorySegment(a, b, ("x",), proposal_prob=1.0, raw_action=0.5, cost=1.0, risk=0.2)
        comp = ComposedTrajectory(x, TrajectorySegment(b, c, ("y",)))
        eval_set = EvaluatorSet(lambda _: 1, lambda _: 1, lambda _: 0)

        for invalid_mode in ["banana", "typo", "", "hybrid_extended"]:
            with pytest.raises(ValueError, match="Invalid mode"):
                EvaluatedPathKernel.compute_kernel([x], lambda _: 1, mode=invalid_mode)
            with pytest.raises(ValueError, match="Invalid mode"):
                EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, mode=invalid_mode)

    def test_residual_convenience_aliases(self):
        """Verifies module-level convenience exports for residual calculations."""
        a, b, c = map(State, ["a", "b", "c"])
        x = TrajectorySegment(a, b, ("x",), proposal_prob=0.8, raw_action=0.3, cost=0.5, risk=0.1)
        y = TrajectorySegment(b, c, ("y",), proposal_prob=0.6, raw_action=0.4, cost=0.5, risk=0.1)
        comp = ComposedTrajectory(x, y)
        eval_set = EvaluatorSet(lambda _: 1, lambda _: 1, lambda _: 0)

        r1 = calculate_action_evaluator_residual([comp], eval_set, beta=1.0)
        assert r1 == EvaluatedPathKernel.compute_action_evaluator_residual([comp], eval_set, beta=1.0)

        r2 = calculate_proposal_cost_risk_evaluator_residual([comp], eval_set, lam=0.5, mu=0.5)
        assert r2 == EvaluatedPathKernel.compute_proposal_cost_risk_evaluator_residual([comp], eval_set, lam=0.5, mu=0.5)

        r3 = calculate_hybrid_evaluator_residual([comp], eval_set, beta=1.0, lam=0.5, mu=0.5)
        assert r3 == EvaluatedPathKernel.compute_hybrid_evaluator_residual([comp], eval_set, beta=1.0, lam=0.5, mu=0.5)

        r4 = calculate_evaluator_residual([comp], eval_set, beta=1.0, mode="action")
        assert r4 == r1

    def test_residual_coefficient_validation(self):
        """Verifies fail-closed non-negative and finite validation for residual coefficients."""
        a, b, c = map(State, ["a", "b", "c"])
        comp = ComposedTrajectory(TrajectorySegment(a, b, ("x",)), TrajectorySegment(b, c, ("y",)))
        eval_set = EvaluatorSet(lambda _: 1, lambda _: 1, lambda _: 0)

        with pytest.raises(ValueError, match="non-negative"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=-1.0)
        with pytest.raises(ValueError, match="non-negative"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, lam=-0.5)
        with pytest.raises(ValueError, match="non-negative"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, mu=-0.5)
        with pytest.raises(ValueError, match="Residual coefficients must be finite"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=float("nan"))
        with pytest.raises(ValueError, match="Residual coefficients must be finite"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, lam=float("nan"))
        with pytest.raises(ValueError, match="Residual coefficients must be finite"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, mu=float("nan"))
        with pytest.raises(ValueError, match="Residual coefficients must be finite"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=float("inf"))
        with pytest.raises(ValueError, match="Residual coefficients must be finite"):
            EvaluatedPathKernel.compute_evaluator_residual([comp], eval_set, beta=float("-inf"))

    def test_undeclared_right_segment_decomposition_violation(self):
        """Verifies boundary slice validation detects undeclared right segments."""
        a, b, c = map(State, ["a", "b", "c"])
        x = TrajectorySegment(a, b, ("x",))
        y = TrajectorySegment(b, c, ("y",))
        y_undeclared = TrajectorySegment(b, c, ("y_other",))
        comp = ComposedTrajectory(x, y_undeclared)
        bs = BoundarySlice(states={b})
        valid, violations = bs.validate_unique_decomposition([comp], left_segments=[x], right_segments=[y])
        assert not valid
        assert any("undeclared right segment" in v for v in violations)
