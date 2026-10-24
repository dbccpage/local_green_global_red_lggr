"""Pinned exact-value tests for the "Local Green, Global Red" replays (v0.1).

Every constant the note names is asserted here with exact Fraction equality —
never approximate equality. Pure standard library (unittest); also runnable
by pytest.

Run from the deposit root:
    python -m unittest discover -s code -p "test_lgr_replay.py"

AuthorityEffect: None.
"""

from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lgr_replay import (
    THREE_PATCH_EDGES,
    ZERO,
    attained_at_zero,
    component_l1,
    component_l2_sq,
    component_linf,
    coupled_all_green_forces_zero,
    diag_closed,
    diag_residual,
    coupled_blind_spot_witness,
    coupled_defects,
    coupled_measure,
    coupled_raw_norm,
    coupled_tallies,
    defeat_recovery,
    neg2,
    omega_not_exact,
    phi_lower_bound,
    repair_mass,
    skew_closed,
    skew_residual,
    three_patch_full_coverage,
    three_patch_raw_norm,
    three_patch_tallies,
    three_patch_watcher,
    zero_repair_norm,
)

Vec2 = tuple[Fraction, Fraction]

F = Fraction


class ThreePatchTests(unittest.TestCase):
    """Theorem 3: full coverage, All-Green, I = 6 at lam = 1."""

    def test_three_patch_I_is_exactly_6(self) -> None:
        self.assertEqual(three_patch_raw_norm(F(1)), F(6))

    def test_three_patch_all_green(self) -> None:
        self.assertEqual(three_patch_tallies(F(1)), (F(0), F(0), F(0)))

    def test_three_patch_every_interface_watched(self) -> None:
        self.assertTrue(three_patch_full_coverage())
        self.assertEqual(len(THREE_PATCH_EDGES), 6)
        for edge in THREE_PATCH_EDGES:
            self.assertEqual(three_patch_watcher(edge), edge[0])


class ScalingTests(unittest.TestCase):
    """Theorem 4: I(s_lam) = 6|lam| exactly, and the no-recovery witness."""

    def test_scaling_is_six_lambda(self) -> None:
        for lam in (F(1), F(2), F(7, 3), F(-5, 2), F(1000000)):
            with self.subTest(lam=str(lam)):
                self.assertEqual(three_patch_raw_norm(lam), 6 * abs(lam))
                self.assertEqual(three_patch_tallies(lam), (F(0), F(0), F(0)))
        # The negative case pins the absolute value:
        self.assertEqual(three_patch_raw_norm(F(-5, 2)), F(15))

    def test_no_recovery_witness_defeats_f(self) -> None:
        for f0 in (F(0), F(1), F(100), F(-3), F(999, 7), F(10**16), F(10**100)):
            with self.subTest(f0=str(f0)):
                lam, tallies, raw = defeat_recovery(f0)
                self.assertEqual(lam, (abs(f0) + 1) / 6)
                self.assertEqual(tallies, (F(0), F(0), F(0)))  # All-Green
                self.assertEqual(raw, abs(f0) + 1)  # 6 * |lam| exactly
                self.assertGreater(raw, f0)  # f(0) < I(s_lam)


class CoupledTests(unittest.TestCase):
    """Theorem 6: coupling, nontrivial blind spots, All-Green forces I = 0."""

    SAMPLES: tuple[Vec2, ...] = (
        (F(0), F(0)),
        (F(1), F(0)),
        (F(0), F(1)),
        (F(3), F(-2)),
        (F(-7, 5), F(11, 3)),
    )

    def test_coupled_defects_are_coupled(self) -> None:
        for sx in self.SAMPLES:
            with self.subTest(sx=str(sx)):
                d = coupled_defects(sx)
                self.assertEqual(d[0], neg2(sx))
                self.assertEqual(d[1], neg2(sx))
                self.assertEqual(d[0], d[1])  # the coupling

    def test_coupled_tallies_read_the_other_coordinate(self) -> None:
        for sx in self.SAMPLES:
            with self.subTest(sx=str(sx)):
                self.assertEqual(coupled_tallies(sx), (abs(sx[1]), abs(sx[0])))

    def test_coupled_blind_spots_nontrivial(self) -> None:
        for e in (0, 1):
            with self.subTest(edge=e):
                v = coupled_blind_spot_witness(e)
                self.assertNotEqual(v, (F(0), F(0)))  # nonzero...
                self.assertEqual(coupled_measure(e, v), F(0))  # ...measured 0

    def test_coupled_all_green_forces_zero(self) -> None:
        # Zero tallies => sx == (0, 0) => I == 0:
        self.assertEqual(coupled_tallies((ZERO, ZERO)), (F(0), F(0)))
        self.assertEqual(coupled_raw_norm((ZERO, ZERO)), F(0))
        for sx in self.SAMPLES:
            with self.subTest(sx=str(sx)):
                self.assertTrue(coupled_all_green_forces_zero(sx))
        # Contrapositive: any nonzero sx has a nonzero tally.
        for sx in self.SAMPLES:
            if sx == (ZERO, ZERO):
                continue
            with self.subTest(sx=str(sx)):
                self.assertNotEqual(coupled_tallies(sx), (F(0), F(0)))


class MinkowskiRepairTests(unittest.TestCase):
    """LGR-R2, LGR-R3, and LGR-R4: residual arithmetic against closed forms."""

    def test_r2_recovers_from_diagonal_closed_form(self) -> None:
        closed = diag_closed(F(1), F(-1))
        self.assertEqual(closed, (F(2), F(2), F(1), F(-1), F(1), F(0)))
        at_zero = diag_residual(F(1), F(-1), closed[5])
        self.assertEqual(component_l1(at_zero), closed[0])
        self.assertEqual(component_l2_sq(at_zero), closed[1])
        self.assertEqual(component_linf(at_zero), closed[2])
        at_end = diag_residual(F(1), F(-1), closed[4])
        self.assertEqual(component_l1(at_end), closed[0])
        self.assertGreater(component_l2_sq(at_end), closed[1])
        self.assertGreater(component_linf(at_end), closed[2])

    def test_diagonal_off_image_is_strict(self) -> None:
        closed = diag_closed(F(1), F(-1))
        off = diag_residual(F(1), F(-1), F(2))
        self.assertGreater(component_l1(off), closed[0])
        self.assertGreater(component_l2_sq(off), closed[1])
        self.assertGreater(component_linf(off), closed[2])

    def test_diagonal_vanishes_only_when_coordinates_agree(self) -> None:
        closed = diag_closed(F(3), F(3))
        self.assertEqual(closed[0], F(0))
        self.assertEqual(closed[1], F(0))
        self.assertEqual(closed[2], F(0))
        self.assertEqual(component_l1(diag_residual(F(3), F(3), closed[5])), F(0))
        moved = diag_closed(F(3), F(1))
        self.assertGreater(moved[0], F(0))

    def test_zero_repair_matches_diagonal_only_on_the_stated_signs(self) -> None:
        matched = zero_repair_norm(F(1), F(-1))
        closed = diag_closed(F(1), F(-1))
        self.assertEqual(matched[0], closed[0])
        self.assertEqual(matched[1], closed[1])
        self.assertEqual(matched[2], closed[2])
        strict = zero_repair_norm(F(2), F(3))
        other = diag_closed(F(2), F(3))
        self.assertGreater(strict[0], other[0])
        self.assertGreater(strict[1], other[1])
        self.assertGreater(strict[2], other[2])

    def test_skew_pair_attains_the_three_closed_values(self) -> None:
        closed = skew_closed(F(1), F(-1))
        self.assertEqual(
            closed, (F(3, 2), F(9, 5), F(1), F(1, 2), F(1, 5), F(0))
        )
        at_l1 = skew_residual(F(1), F(-1), closed[3])
        at_l2 = skew_residual(F(1), F(-1), closed[4])
        at_linf = skew_residual(F(1), F(-1), closed[5])
        self.assertEqual(component_l1(at_l1), closed[0])
        self.assertEqual(component_l2_sq(at_l2), closed[1])
        self.assertEqual(component_linf(at_linf), closed[2])
        off = skew_residual(F(1), F(-1), F(1))
        self.assertGreater(component_l1(off), closed[0])
        self.assertGreater(component_l2_sq(off), closed[1])
        self.assertGreater(component_linf(off), closed[2])

    def test_skew_vanishes_only_on_the_double_line(self) -> None:
        closed = skew_closed(F(4), F(8))
        self.assertEqual(closed[0], F(0))
        self.assertEqual(closed[1], F(0))
        self.assertEqual(closed[2], F(0))
        self.assertEqual(closed[3], closed[4])
        self.assertEqual(closed[4], closed[5])
        self.assertEqual(component_l1(skew_residual(F(4), F(8), closed[3])), F(0))
        moved = skew_closed(F(4), F(1))
        self.assertGreater(moved[0], F(0))

    def test_zero_repair_matches_skew_only_on_the_stated_lines(self) -> None:
        l1_only = zero_repair_norm(F(1), F(0))
        l1_closed = skew_closed(F(1), F(0))
        self.assertEqual(l1_only[0], l1_closed[0])
        self.assertGreater(l1_only[1], l1_closed[1])
        self.assertGreater(l1_only[2], l1_closed[2])
        l2_only = zero_repair_norm(F(2), F(-1))
        l2_closed = skew_closed(F(2), F(-1))
        self.assertGreater(l2_only[0], l2_closed[0])
        self.assertEqual(l2_only[1], l2_closed[1])
        self.assertGreater(l2_only[2], l2_closed[2])
        linf_only = zero_repair_norm(F(1), F(-1))
        linf_closed = skew_closed(F(1), F(-1))
        self.assertGreater(linf_only[0], linf_closed[0])
        self.assertGreater(linf_only[1], linf_closed[1])
        self.assertEqual(linf_only[2], linf_closed[2])


class RepairMassTests(unittest.TestCase):
    """The Remark: repair mass >= 2, attained at 0, Phi = 2, (1,-1) unreachable."""

    ALPHAS: tuple[Fraction, ...] = (
        F(0), F(1), F(-1), F(3, 7), F(-22, 9), F(2), F(1000000),
    )

    def test_repair_mass_min_is_exactly_2(self) -> None:
        for alpha in self.ALPHAS:
            with self.subTest(alpha=str(alpha)):
                self.assertGreaterEqual(repair_mass(alpha), F(2))
        self.assertEqual(repair_mass(F(0)), F(2))  # equality at alpha = 0
        self.assertTrue(attained_at_zero())
        self.assertEqual(phi_lower_bound(), F(2))

    def test_omega_not_exact(self) -> None:
        for alpha in self.ALPHAS + (F(-1), F(1)):
            with self.subTest(alpha=str(alpha)):
                self.assertTrue(omega_not_exact(alpha))


if __name__ == "__main__":
    unittest.main()
