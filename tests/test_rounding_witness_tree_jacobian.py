"""Data-free exact fixture for the rounding-witness proposal.

AuthorityEffect: None. Status: proposal fixture, not an admitted LGGR claim.
See proposals/rounding_witness/README.md.

A unit vector u in Q^n is built from n-1 Givens rotations on a tree. Step k
splits parent p_k into child c_k. Angles use the rational half-angle
parametrisation cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2), so u and every
column J_k = du/dtheta_k are exact Fractions. No floats, no external data.

Checked here, under the freshness rule (c_k carries no mass when split off):
  claim 1  <J_j, J_k> = 0 for j != k
  claim 2  |J_k|^2 = a_k^2, a_k = v_{k-1}[p_k]
  claim 3  <J_k, u> = 0
  linearised quadrature  |sum_k eps_k J_k|^2 = sum_k a_k^2 eps_k^2, and
  sqrt of that <= sum_k |a_k eps_k|, with equality iff at most one term is
  nonzero (checked on squares, so it stays exact).
Negative control: re-splitting into a child that already carries mass
breaks claim 1.

This is a reimplementation from the stated claims; it is not a byte copy of
any external script.
"""

import random
import unittest
from fractions import Fraction

N_TREES = 300
MAX_N = 9
SEED = 20261113


def cos_sin(t):
    d = 1 + t * t
    return (1 - t * t) / d, 2 * t / d


def rotate(v, p, c, cs, sn):
    """Givens rotation in the (p, c) plane: e_p -> cos e_p + sin e_c."""
    w = list(v)
    w[p] = cs * v[p] - sn * v[c]
    w[c] = sn * v[p] + cs * v[c]
    return w


def d_rotate(v, p, c, cs, sn):
    """d/dtheta of rotate(v, ...) at the same angle."""
    w = [Fraction(0)] * len(v)
    w[p] = -sn * v[p] - cs * v[c]
    w[c] = cs * v[p] - sn * v[c]
    return w


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def build(n, steps, ts):
    """Return (u, columns J_k, weights a_k) for steps [(p_k, c_k)]."""
    trig = [cos_sin(t) for t in ts]
    states = [[Fraction(1)] + [Fraction(0)] * (n - 1)]
    for (p, c), (cs, sn) in zip(steps, trig):
        states.append(rotate(states[-1], p, c, cs, sn))
    u = states[-1]
    cols, weights = [], []
    for k, ((p, c), (cs, sn)) in enumerate(zip(steps, trig)):
        w = d_rotate(states[k], p, c, cs, sn)
        for (p2, c2), (cs2, sn2) in zip(steps[k + 1:], trig[k + 1:]):
            w = rotate(w, p2, c2, cs2, sn2)
        cols.append(w)
        weights.append(states[k][p])
    return u, cols, weights


def random_fresh_tree(rng, n):
    """Admissible tree: node k is fresh when split off from an active node."""
    steps = [(rng.randrange(k), k) for k in range(1, n)]
    ts = [Fraction(rng.randint(-9, 9), rng.randint(1, 9)) for _ in steps]
    return steps, ts


class TreeJacobianExactTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(SEED)
        self.cases = []
        for _ in range(N_TREES):
            n = self.rng.randint(2, MAX_N)
            steps, ts = random_fresh_tree(self.rng, n)
            self.cases.append((n, steps, ts, build(n, steps, ts)))

    def test_u_is_exact_unit_vector(self):
        for _, _, _, (u, _, _) in self.cases:
            self.assertEqual(dot(u, u), 1)

    def test_claim1_columns_orthogonal(self):
        for _, _, _, (_, cols, _) in self.cases:
            for j in range(len(cols)):
                for k in range(j + 1, len(cols)):
                    self.assertEqual(dot(cols[j], cols[k]), 0)

    def test_claim2_column_norm_is_parent_mass(self):
        for _, _, _, (_, cols, a) in self.cases:
            for col, ak in zip(cols, a):
                self.assertEqual(dot(col, col), ak * ak)

    def test_claim3_columns_tangent_to_sphere(self):
        for _, _, _, (u, cols, _) in self.cases:
            for col in cols:
                self.assertEqual(dot(col, u), 0)

    def test_linearised_quadrature_and_equality_case(self):
        rng = random.Random(SEED + 1)
        saw_strict = saw_equal = False
        for n, _, _, (_, cols, a) in self.cases:
            eps = [Fraction(rng.randint(-4, 4), 2 ** rng.randint(1, 6))
                   for _ in cols]
            if rng.random() < 0.25:  # force a single-term case sometimes
                keep = rng.randrange(len(eps))
                eps = [e if i == keep else Fraction(0) for i, e in enumerate(eps)]
            d = [sum(e * col[i] for e, col in zip(eps, cols)) for i in range(n)]
            quad = sum((ak * e) ** 2 for ak, e in zip(a, eps))
            self.assertEqual(dot(d, d), quad)
            linear = sum(abs(ak * e) for ak, e in zip(a, eps))
            nonzero = sum(1 for ak, e in zip(a, eps) if ak * e != 0)
            if nonzero <= 1:
                self.assertEqual(quad, linear * linear)
                saw_equal = True
            else:
                self.assertLess(quad, linear * linear)
                saw_strict = True
        self.assertTrue(saw_strict and saw_equal)

    def test_sqrt_k_ratio_for_equal_weighted_errors(self):
        # k equal weighted errors x: quadrature^2 = k x^2, linear^2 = k^2 x^2.
        for k in range(1, 9):
            x = Fraction(1, 7)
            self.assertEqual((k * x) ** 2 / (k * x * x), k)

    def test_negative_control_non_fresh_child_breaks_claim1(self):
        # Fixed witness: split 0 -> 1, then rotate (0, 1) again while 1 has mass.
        t = Fraction(1, 2)
        _, cols, _ = build(2, [(0, 1), (0, 1)], [t, t])
        self.assertNotEqual(dot(cols[0], cols[1]), 0)
        # Random witnesses: re-split into an already-active child.
        rng = random.Random(SEED + 2)
        broken = 0
        for _ in range(50):
            n = rng.randint(3, MAX_N)
            steps, ts = random_fresh_tree(rng, n)
            k = rng.randrange(1, len(steps)) if len(steps) > 1 else 0
            p = steps[k][0]
            stale = [m for m in range(k + 1) if m != p]
            steps[k] = (p, rng.choice(stale))
            _, cols, _ = build(n, steps, ts)
            if any(dot(cols[i], cols[j]) != 0
                   for i in range(len(cols)) for j in range(i + 1, len(cols))):
                broken += 1
        self.assertGreater(broken, 25)


if __name__ == "__main__":
    unittest.main()
