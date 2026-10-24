"""Tests for explicit finite system witnesses."""
from __future__ import annotations

import numpy as np
from code_witnesses import (
    CoupledSystem,
    ScalarQuotientWitness,
    ThreePatchSystem,
    TrivialKernelThreePatchSystem,
)


def test_three_patch_system_properties():
    tp = ThreePatchSystem()
    assert len(tp.system.sites) == 6
    assert len(tp.system.interfaces) == 6
    assert len(tp.system.evaluator_family.evaluators) == 3

    a = tp.create_scaled_assignment(1.0)
    assert tp.system.is_all_green(a) is True
    assert abs(tp.system.global_inconsistency(a) - 6.0) < 1e-9


def test_trivial_kernel_system():
    tk = TrivialKernelThreePatchSystem()
    assert len(tk.system.sites) == 6
    assert len(tk.system.interfaces) == 6


def test_coupled_system_properties():
    cs = CoupledSystem()
    assert len(cs.system.sites) == 3
    assert len(cs.system.interfaces) == 2

    # Zero section
    a0 = cs.create_section_assignment(np.zeros(2))
    assert cs.system.is_all_green(a0) is True
    assert cs.system.global_inconsistency(a0) < 1e-9

    # Nonzero section
    a_nz = cs.create_section_assignment(np.array([1.0, 0.0]))
    assert cs.system.is_all_green(a_nz) is False
    assert abs(cs.system.global_inconsistency(a_nz) - 2.0) < 1e-9


def test_scalar_quotient_witness():
    qw = ScalarQuotientWitness()
    assert abs(qw.repair_mass(0.0) - 2.0) < 1e-9
    min_dist, argmin_a = qw.minimal_quotient_distance()
    assert abs(min_dist - 2.0) < 1e-9
    assert abs(argmin_a - 0.0) < 1e-9
