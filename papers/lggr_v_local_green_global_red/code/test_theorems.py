"""Tests for theorem checks and replays."""
from __future__ import annotations

import numpy as np
import pytest
from code_core import Assignment, Evaluator, Interface, NormType, Site, System
from code_theorems import (
    check_remark_irreparable_red,
    check_theorem_1_passivity,
    check_theorem_2_characterization,
    check_theorem_5_sufficiency,
    check_theorem_6_coupled_witness,
    compute_recovery_constant,
    diagnose_theorem_2,
    replay_theorem_3_three_patch,
    replay_theorem_4_no_recovery_modulus,
)
from code_witnesses import CoupledSystem, ThreePatchSystem, TrivialKernelThreePatchSystem


def test_theorem_1_passivity():
    tp = ThreePatchSystem()
    a = tp.create_scaled_assignment(1.0)
    assert check_theorem_1_passivity(tp.system, a) is True

    # Test false branch where J > I (e.g. measurement matrix with norm > 1)
    bad_sys = System()
    bad_sys.add_site(Site("s1", 1, NormType.L1))
    bad_sys.add_site(Site("s2", 1, NormType.L1))
    bad_sys.add_interface(Interface("e", "s1", "s2", np.array([[1.0]]), NormType.L1))
    # Measurement matrix with large norm
    bad_ev = Evaluator("bad_ev", ["e"], {"e": np.array([[100.0]])}, {"e": NormType.L1})
    bad_sys.add_evaluator(bad_ev)
    bad_a = Assignment()
    bad_a.set_state("s1", [0.0])
    bad_a.set_state("s2", [1.0])
    assert check_theorem_1_passivity(bad_sys, bad_a) is False

    # Passivity regression: 1D system with source state 1e200, target state 0, L2 norms,
    # and measurement matrix [[2.0]] (expanding measurement).
    # Must compute I = 1e200, J = 2e200 and return False, never report passivity success.
    exp_sys = System()
    exp_sys.add_site(Site("a", 1, NormType.L2))
    exp_sys.add_site(Site("b", 1, NormType.L2))
    exp_sys.add_interface(Interface("e", "a", "b", np.array([[1.0]]), NormType.L2))
    exp_ev = Evaluator("alpha", ["e"], {"e": np.array([[2.0]])}, {"e": NormType.L2})
    exp_sys.add_evaluator(exp_ev)
    exp_assign = Assignment()
    exp_assign.set_state("a", [0.0])
    exp_assign.set_state("b", [1e200])
    assert check_theorem_1_passivity(exp_sys, exp_assign) is False

    # Passivity with non-finite score or inconsistency reports False
    class MockNonFiniteSystem:
        def global_inconsistency(self, _):
            return float("inf")
        def evaluator_scores(self, _):
            return {"e": 1.0}
    assert check_theorem_1_passivity(MockNonFiniteSystem(), exp_assign) is False  # type: ignore


def test_theorem_2_characterization():
    tp = ThreePatchSystem()
    a = tp.create_scaled_assignment(1.0)
    assert check_theorem_2_characterization(tp.system, a) is True

    # Test assignment where defect is NOT in blind spot
    a_not_in_bs = Assignment()
    # s(u0) has component along coord 1 (which evaluator 0 watches and does not delete)
    a_not_in_bs.set_state("u0", [1.0, 1.0, 0.0])
    a_not_in_bs.set_state("u1", [0.0, 0.0, 0.0])
    a_not_in_bs.set_state("u2", [0.0, 0.0, 0.0])
    a_not_in_bs.set_state("x01", [0.0, 0.0, 0.0])
    a_not_in_bs.set_state("x12", [0.0, 0.0, 0.0])
    a_not_in_bs.set_state("x20", [0.0, 0.0, 0.0])
    assert check_theorem_2_characterization(tp.system, a_not_in_bs) is True

    # F4 Regression: scalar identity system with defect 5e-9 evaluated under consistent tolerances
    scalar_sys = System()
    scalar_sys.add_site(Site("a", 1))
    scalar_sys.add_site(Site("b", 1))
    scalar_sys.add_interface(Interface("e", "a", "b", np.eye(1)))
    scalar_sys.add_evaluator(Evaluator("ev", ["e"], {"e": np.eye(1)}))
    scalar_a = Assignment()
    scalar_a.set_state("a", [0.0])
    scalar_a.set_state("b", [5e-9])
    assert check_theorem_2_characterization(scalar_sys, scalar_a, tol=1e-8) is True
    assert check_theorem_2_characterization(scalar_sys, scalar_a, tol=1e-9) is True

    # R3: Contractive measurement q(x) = 0.1x with defect 5e-8 and tol 1e-8
    contractive_sys = System()
    contractive_sys.add_site(Site("a", 1))
    contractive_sys.add_site(Site("b", 1))
    contractive_sys.add_interface(Interface("e", "a", "b", np.eye(1)))
    contractive_sys.add_evaluator(Evaluator("ev", ["e"], {"e": np.array([[0.1]])}))
    contractive_a = Assignment()
    contractive_a.set_state("a", [0.0])
    contractive_a.set_state("b", [5e-8])
    assert check_theorem_2_characterization(contractive_sys, contractive_a, tol=1e-8) is True
    diag = diagnose_theorem_2(contractive_sys, contractive_a, tol=1e-8)
    assert diag.is_all_green is True
    assert diag.defects_in_blind_spots is True
    assert diag.is_theoretically_consistent is True

    # Unwatched interface (exercises _compute_interface_scaled_tolerance empty branch)
    unw_sys = System()
    unw_sys.add_site(Site("a", 1))
    unw_sys.add_site(Site("b", 1))
    unw_sys.add_interface(Interface("e_unw", "a", "b", np.eye(1)))
    unw_a = Assignment()
    unw_a.set_state("a", [0.0])
    unw_a.set_state("b", [1.0])
    assert diagnose_theorem_2(unw_sys, unw_a).is_theoretically_consistent is True

    # All-zero measurement matrix (exercises _compute_interface_scaled_tolerance zero singular values branch)
    zero_sys = System()
    zero_sys.add_site(Site("a", 1))
    zero_sys.add_site(Site("b", 1))
    zero_sys.add_interface(Interface("e", "a", "b", np.eye(1)))
    zero_sys.add_evaluator(Evaluator("ev_zero", ["e"], {"e": np.zeros((1, 1))}))
    zero_a = Assignment()
    zero_a.set_state("a", [0.0])
    zero_a.set_state("b", [1.0])
    assert diagnose_theorem_2(zero_sys, zero_a).is_theoretically_consistent is True

    # Finding 3 Regression: Anisotropic measurement Q = diag(0.1, 1) with defect (0, 5e-8)
    aniso_sys = System()
    aniso_sys.add_site(Site("a", 2))
    aniso_sys.add_site(Site("b", 2))
    aniso_sys.add_interface(Interface("e", "a", "b", np.eye(2)))
    aniso_sys.add_evaluator(Evaluator("ev", ["e"], {"e": np.array([[0.1, 0.0], [0.0, 1.0]])}))
    aniso_a = Assignment()
    aniso_a.set_state("a", [0.0, 0.0])
    aniso_a.set_state("b", [0.0, 5e-8])
    aniso_diag = diagnose_theorem_2(aniso_sys, aniso_a, tol=1e-8)
    assert aniso_diag.is_all_green is False
    assert aniso_diag.is_theoretically_consistent is True
    assert check_theorem_2_characterization(aniso_sys, aniso_a, tol=1e-8) is True

    # Finding 3 Regression: Two scalar interfaces aggregated under one evaluator
    agg_sys = System()
    agg_sys.add_site(Site("a", 1))
    agg_sys.add_site(Site("b0", 1))
    agg_sys.add_site(Site("b1", 1))
    agg_sys.add_interface(Interface("e0", "a", "b0", np.eye(1)))
    agg_sys.add_interface(Interface("e1", "a", "b1", np.eye(1)))
    agg_sys.add_evaluator(Evaluator("ev", ["e0", "e1"], {"e0": np.eye(1), "e1": np.eye(1)}))
    agg_a = Assignment()
    agg_a.set_state("a", [0.0])
    agg_a.set_state("b0", [7.5e-9])
    agg_a.set_state("b1", [7.5e-9])
    agg_diag = diagnose_theorem_2(agg_sys, agg_a, tol=1e-8)
    assert agg_diag.is_all_green is False
    assert agg_diag.is_theoretically_consistent is True
    assert check_theorem_2_characterization(agg_sys, agg_a, tol=1e-8) is True


def test_theorem_3_three_patch():
    success, I_val, scores = replay_theorem_3_three_patch(6.0)
    assert success is True
    assert abs(I_val - 6.0) < 1e-9
    assert all(abs(s) < 1e-9 for s in scores.values())


def test_theorem_4_no_recovery_modulus():
    success, I_val, bound = replay_theorem_4_no_recovery_modulus(lambda x: 10.0 * x + 5.0)
    assert success is True
    assert I_val > bound


def test_theorem_5_sufficiency():
    tk = TrivialKernelThreePatchSystem()
    # 1. Zero assignment (all green -> I=0 -> returns True)
    a_zero = Assignment()
    for name in ["u0", "u1", "u2", "x01", "x12", "x20"]:
        a_zero.set_state(name, np.zeros(3))
    assert check_theorem_5_sufficiency(tk.system, a_zero) is True

    # 2. Nonzero assignment on trivial kernel (not all green -> returns True)
    a_nonzero = Assignment()
    a_nonzero.set_state("u0", [1.0, 0.0, 0.0])
    for name in ["u1", "u2", "x01", "x12", "x20"]:
        a_nonzero.set_state(name, np.zeros(3))
    assert check_theorem_5_sufficiency(tk.system, a_nonzero) is True

    # 3. System without trivial kernels fails hypotheses -> returns False
    tp = ThreePatchSystem()
    a_tp = tp.create_scaled_assignment(1.0)
    assert check_theorem_5_sufficiency(tp.system, a_tp) is False

    # 4. Finding 3 Regression: Contractive measurement q = 0.01 with defect 5e-8
    # Score is 5e-10 (green at 1e-8), defect is 5e-8 <= C * max_score + tol (where C = 100)
    system5 = System()
    system5.add_site(Site("a", 1))
    system5.add_site(Site("b", 1))
    system5.add_interface(Interface("e", "a", "b", np.eye(1)))
    system5.add_evaluator(Evaluator("observer", ["e"], {"e": np.array([[0.01]])}))
    assignment5 = Assignment()
    assignment5.set_state("a", [0.0])
    assignment5.set_state("b", [5e-8])
    assert check_theorem_5_sufficiency(system5, assignment5, tol=1e-8) is True


def test_theorem_6_necessity_fails_and_branches(monkeypatch):
    assert check_theorem_6_coupled_witness() is True

    # Test failure branches for coverage
    cs = CoupledSystem()
    # 1. Remove an interface to fail full coverage
    cs.system.interfaces.clear()
    assert check_theorem_6_coupled_witness(cs) is False

    # 2. Empty evaluators to fail trivial blind spots
    cs2 = CoupledSystem()
    cs2.system.evaluator_family.evaluators.clear()
    assert check_theorem_6_coupled_witness(cs2) is False

    # 3. Mock is_all_green returning True for nonzero section
    cs3 = CoupledSystem()
    monkeypatch.setattr(cs3.system, "is_all_green", lambda a: True)
    assert check_theorem_6_coupled_witness(cs3) is False


def test_remark_irreparable_red():
    assert check_remark_irreparable_red() is True


def test_diagnose_theorem_2_operator_bounds_failure_branches():
    # 1. upper_bound_ok = False: evaluator score exceeds operator upper bound
    sys_bad = System()
    sys_bad.add_site(Site("a", 1))
    sys_bad.add_site(Site("b", 1))
    sys_bad.add_interface(Interface("e", "a", "b", np.eye(1)))
    sys_bad.add_evaluator(Evaluator("ev", ["e"], {"e": np.zeros((1, 1))}))
    a_bad = Assignment()
    a_bad.set_state("a", [0.0])
    a_bad.set_state("b", [1.0])
    sys_bad.evaluator_scores = lambda a: {"ev": 10.0}
    diag_bad = diagnose_theorem_2(sys_bad, a_bad)
    assert diag_bad.is_theoretically_consistent is False

    # 2. lower_bound_ok = False: is_green=True (max_score <= tol) but dist > scaled_tol
    sys_low = System()
    sys_low.add_site(Site("a", 1))
    sys_low.add_site(Site("b", 1))
    sys_low.add_interface(Interface("e", "a", "b", np.eye(1)))
    sys_low.add_evaluator(Evaluator("ev", ["e"], {"e": np.eye(1)}))
    a_low = Assignment()
    a_low.set_state("a", [0.0])
    a_low.set_state("b", [1.0])
    sys_low.evaluator_scores = lambda a: {"ev": 0.0}
    diag_low = diagnose_theorem_2(sys_low, a_low, tol=1e-8)
    assert diag_low.is_theoretically_consistent is False


def test_compute_recovery_constant_unbounded_branches():
    # 1. Unwatched interface -> inf
    sys_unw = System()
    sys_unw.add_site(Site("a", 1))
    sys_unw.add_site(Site("b", 1))
    sys_unw.add_interface(Interface("e", "a", "b", np.eye(1)))
    assert compute_recovery_constant(sys_unw) == float("inf")

    # 2. Rank deficient measurement matrix -> inf
    sys_nt = System()
    sys_nt.add_site(Site("a", 2))
    sys_nt.add_site(Site("b", 2))
    sys_nt.add_interface(Interface("e", "a", "b", np.eye(2)))
    sys_nt.add_evaluator(Evaluator("ev", ["e"], {"e": np.array([[1.0, 0.0]])}))
    assert compute_recovery_constant(sys_nt) == float("inf")


def test_item_3_norm_aware_recovery_and_bounds():
    """Item 3 Regressions: Norm conversions on recovery constants and operator bounds."""
    # 1. L1 fiber, L1 measurement; Q = [[1, 1], [1, -1]] / 2
    # Defect (1, 1): C = 2.0, I = 2.0, J = 1.0. I <= C * J holds.
    sys1 = System()
    sys1.add_site(Site("s1", 2, NormType.L1))
    sys1.add_site(Site("s2", 2, NormType.L1))
    sys1.add_interface(Interface("e", "s1", "s2", np.eye(2), NormType.L1))
    Q1 = np.array([[1.0, 1.0], [1.0, -1.0]]) / 2.0
    sys1.add_evaluator(Evaluator("ev1", ["e"], {"e": Q1}, {"e": NormType.L1}))
    C1 = compute_recovery_constant(sys1)
    assert C1 == pytest.approx(2.0, rel=1e-5)
    a1 = Assignment()
    a1.set_state("s1", [0.0, 0.0])
    a1.set_state("s2", [1.0, 1.0])
    I1 = sys1.global_inconsistency(a1)
    J1 = sys1.evaluator_scores(a1)["ev1"]
    assert I1 == pytest.approx(2.0)
    assert J1 == pytest.approx(1.0)
    assert I1 <= C1 * J1 + 1e-9

    # 2. L1 fiber, L-infinity measurement; Q = identity(4)
    # Defect: four entries equal to 1e-8. C = 4.0.
    sys2 = System()
    sys2.add_site(Site("s1", 4, NormType.L1))
    sys2.add_site(Site("s2", 4, NormType.L1))
    sys2.add_interface(Interface("e", "s1", "s2", np.eye(4), NormType.L1))
    sys2.add_evaluator(Evaluator("ev2", ["e"], {"e": np.eye(4)}, {"e": NormType.LINF}))
    C2 = compute_recovery_constant(sys2)
    assert C2 == pytest.approx(4.0, rel=1e-5)
    a2 = Assignment()
    a2.set_state("s1", np.zeros(4))
    a2.set_state("s2", np.full(4, 1e-8))
    assert check_theorem_5_sufficiency(sys2, a2, tol=1e-8) is True

    # 3. L1 fiber and measurement; Q = diag(0.1, 1, 1)
    # Defect (0, 5e-8, 5e-8). At tol=1e-8, is_theoretically_consistent must be True.
    sys3 = System()
    sys3.add_site(Site("s1", 3, NormType.L1))
    sys3.add_site(Site("s2", 3, NormType.L1))
    sys3.add_interface(Interface("e", "s1", "s2", np.eye(3), NormType.L1))
    Q3 = np.diag([0.1, 1.0, 1.0])
    sys3.add_evaluator(Evaluator("ev3", ["e"], {"e": Q3}, {"e": NormType.L1}))
    a3 = Assignment()
    a3.set_state("s1", np.zeros(3))
    a3.set_state("s2", np.array([0.0, 5e-8, 5e-8]))
    diag3 = diagnose_theorem_2(sys3, a3, tol=1e-8)
    assert diag3.is_theoretically_consistent is True


def test_item_4_scalar_small_gain_not_blind_spot():
    """Item 4 Regression: Q = [[1e-10]] with defect 1e10. Kernel is {0}, not R^1."""
    sys = System()
    sys.add_site(Site("a", 1))
    sys.add_site(Site("b", 1))
    sys.add_interface(Interface("e", "a", "b", np.eye(1)))
    sys.add_evaluator(Evaluator("ev", ["e"], {"e": np.array([[1e-10]])}))

    a = Assignment()
    a.set_state("a", [0.0])
    a.set_state("b", [1e10])

    diag = diagnose_theorem_2(sys, a, tol=1e-8)
    assert diag.is_all_green is False
    assert diag.defects_in_blind_spots is False
    assert diag.max_blind_spot_distance == pytest.approx(1e10)
    assert diag.is_theoretically_consistent is True


def test_item_5_case_b_theorem_5_small_score():
    """Item 5 Regression (Case B): Q = [[1e-6]] with defect 5e-9 has I=5e-9, J=5e-15, C=1e6."""
    sys = System()
    sys.add_site(Site("a", 1))
    sys.add_site(Site("b", 1))
    sys.add_interface(Interface("e", "a", "b", np.eye(1)))
    sys.add_evaluator(Evaluator("ev", ["e"], {"e": np.array([[1e-6]])}))

    a = Assignment()
    a.set_state("a", [0.0])
    a.set_state("b", [5e-9])

    assert check_theorem_5_sufficiency(sys, a, tol=1e-8) is True


def test_item_8_floating_point_no_recovery_modulus_range():
    """Item 8 Regression: Honest numerical range for floating-point no-recovery replay."""
    # Large candidate bounds where +1 would lose strict inequality
    success_16, I_16, bound_16 = replay_theorem_4_no_recovery_modulus(lambda _: 1e16)
    assert success_16 is True
    assert I_16 > bound_16
    assert I_16 == pytest.approx(2e16)

    success_100, I_100, bound_100 = replay_theorem_4_no_recovery_modulus(lambda _: 1e100)
    assert success_100 is True
    assert I_100 > bound_100
    assert I_100 == pytest.approx(2e100)

    # Negative candidate bound
    success_neg, I_neg, bound_neg = replay_theorem_4_no_recovery_modulus(lambda _: -50.0)
    assert success_neg is True
    assert I_neg > bound_neg

    # Overflowing candidate raises OverflowError
    with pytest.raises(OverflowError, match="exceeds floating-point range"):
        replay_theorem_4_no_recovery_modulus(lambda _: 1e308)

    # Non-finite candidate raises ValueError
    with pytest.raises(ValueError, match="finite"):
        replay_theorem_4_no_recovery_modulus(lambda _: float("nan"))

    # Norm conversion factor branches
    from code_theorems import norm_conversion_factor_a, norm_conversion_factor_b
    assert norm_conversion_factor_a(4, NormType.L1) == 2.0
    assert norm_conversion_factor_a(4, NormType.L2) == 1.0
    assert norm_conversion_factor_a(4, NormType.LINF) == 1.0
    with pytest.raises(ValueError, match="Unsupported norm type"):
        norm_conversion_factor_a(4, "UNKNOWN")

    assert norm_conversion_factor_b(4, NormType.L1) == 1.0
    assert norm_conversion_factor_b(4, NormType.L2) == 1.0
    assert norm_conversion_factor_b(4, NormType.LINF) == 2.0
    with pytest.raises(ValueError, match="Unsupported norm type"):
        norm_conversion_factor_b(4, "UNKNOWN")


