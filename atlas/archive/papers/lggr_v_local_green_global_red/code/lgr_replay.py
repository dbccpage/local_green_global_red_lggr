"""Deterministic exact-arithmetic replays for "Local Green, Global Red" (v0.1).

Pure standard library, fractions.Fraction throughout: every value below is an
exact rational, so the tests assert equality, never approximate equality.

What this module is, and is not: these are finite-instance computations that
replay the witnesses' arithmetic from the note (the three-patch system of
Theorem 3, the scaling family of Theorem 4, the coupled system of Theorem 6,
and the repair-mass minimum of the Remark). They do not prove the for-all
quantified theorems; those proofs are the Lean 4 declarations in
lean4/po000_l004_observer_visibility.lean, mapped in the note's section 6 and
in the claim ledger.

Deterministic: no timestamps, no randomness, no environment reads, no I/O
except the optional __main__ receipt printer.

AuthorityEffect: None.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

Vec3 = tuple[Fraction, Fraction, Fraction]
Vec2 = tuple[Fraction, Fraction]
Edge3 = tuple[int, int]  # (i, k): patch i in {0,1,2}, side k in {0,1}

ZERO = Fraction(0)
ONE = Fraction(1)


def l1_3(v: Vec3) -> Fraction:
    """The l1 norm |v_0| + |v_1| + |v_2| of a 3-vector."""
    return abs(v[0]) + abs(v[1]) + abs(v[2])


def l1_2(v: Vec2) -> Fraction:
    """The l1 norm |v_0| + |v_1| of a 2-vector."""
    return abs(v[0]) + abs(v[1])


# ---------------------------------------------------------------------------
# Three-patch system (Theorem 3).
#
# Three sites u_0, u_1, u_2 in a triangle of pairwise overlaps: six interfaces
# (i, k) for i in 0..2, k in {0, 1} (patch u_i's two covering edges, one per
# neighbouring overlap). Restrictions are identities and the assignment puts
# zero on every overlap and lam * e_i on patch u_i, so the defect on edge
# (i, k) is exactly lam * e_i. The watcher of (i, k) is evaluator i, whose
# measurement deletes coordinate i.
# ---------------------------------------------------------------------------

THREE_PATCH_EDGES: tuple[Edge3, ...] = tuple(
    (i, k) for i in range(3) for k in (0, 1)
)


def basis3(i: int, lam: Fraction) -> Vec3:
    """lam * e_i in R^3."""
    return (
        lam if i == 0 else ZERO,
        lam if i == 1 else ZERO,
        lam if i == 2 else ZERO,
    )


def three_patch_defects(lam: Fraction) -> dict[Edge3, Vec3]:
    """Defect family of the scaled assignment: edge (i, k) carries lam * e_i.

    Mirrors the Lean `ThreePatch.scaledDefect` (identity restrictions, zero
    overlap values, patch values lam * e_i; `scaledDefect_is_section_defect`
    records that these are genuine section defects).
    """
    return {(i, k): basis3(i, lam) for (i, k) in THREE_PATCH_EDGES}


def three_patch_watcher(edge: Edge3) -> int:
    """The unique evaluator watching edge (i, k) is evaluator i."""
    return edge[0]


def delete_coord(a: int, v: Vec3) -> Vec2:
    """Evaluator a's measurement: delete coordinate a (kernel = the e_a line)."""
    kept = tuple(v[j] for j in range(3) if j != a)
    return (kept[0], kept[1])


def three_patch_raw_norm(lam: Fraction) -> Fraction:
    """Global inconsistency I(s_lam) = sum of l1 defect norms over all 6 edges."""
    defects = three_patch_defects(lam)
    total = ZERO
    for edge in THREE_PATCH_EDGES:
        total += l1_3(defects[edge])
    return total


def three_patch_tallies(lam: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """Evaluator scores J^0, J^1, J^2 at the scaled assignment."""
    defects = three_patch_defects(lam)
    tallies = [ZERO, ZERO, ZERO]
    for edge in THREE_PATCH_EDGES:
        a = three_patch_watcher(edge)
        tallies[a] += l1_2(delete_coord(a, defects[edge]))
    return (tallies[0], tallies[1], tallies[2])


def three_patch_full_coverage() -> bool:
    """Every one of the six interfaces has a watcher."""
    return all(
        three_patch_watcher(edge) in (0, 1, 2) for edge in THREE_PATCH_EDGES
    )


# ---------------------------------------------------------------------------
# Scaling family and the no-recovery witness (Theorem 4).
# ---------------------------------------------------------------------------


def defeat_recovery(f0: Fraction) -> tuple[Fraction, tuple[Fraction, ...], Fraction]:
    """Reproduce the Lean witness of `no_recovery_modulus` for a candidate f(0).

    Returns (lam, tallies, raw_norm) with lam = (|f0| + 1) / 6, exactly the
    witness scale used in the Lean proof. The caller checks that every tally
    is zero (All-Green, so max tally is 0 and the candidate bound is f(0))
    while raw_norm > f0.
    """
    lam = (abs(f0) + ONE) / 6
    return (lam, three_patch_tallies(lam), three_patch_raw_norm(lam))


# ---------------------------------------------------------------------------
# Coupled two-edge system (Theorem 6).
#
# One shared site x under two patches, both restriction maps zero, fibers R^2
# with the l1 norm. Both edge defects equal -s(x) (the zero restrictions erase
# the patch values). Evaluator a watches edge a alone and reads the OTHER
# coordinate, so each edge's blind spot is a full coordinate line.
# ---------------------------------------------------------------------------


def neg2(v: Vec2) -> Vec2:
    return (-v[0], -v[1])


def other(a: int) -> int:
    """The other coordinate: 0 -> 1, 1 -> 0."""
    return 1 - a


def coupled_defects(sx: Vec2) -> tuple[Vec2, Vec2]:
    """Both edge defects equal -s(x): the coupling forced by zero restrictions."""
    return (neg2(sx), neg2(sx))


def coupled_measure(a: int, v: Vec2) -> Fraction:
    """Evaluator a's measurement on its edge: read the other coordinate."""
    return v[other(a)]


def coupled_tallies(sx: Vec2) -> Vec2:
    """Scores (J^0, J^1) = (|s(x)_1|, |s(x)_0|): each reads the OTHER coordinate."""
    defects = coupled_defects(sx)
    return (
        abs(coupled_measure(0, defects[0])),
        abs(coupled_measure(1, defects[1])),
    )


def coupled_raw_norm(sx: Vec2) -> Fraction:
    """Global inconsistency of the coupled system: both edges carry -s(x)."""
    defects = coupled_defects(sx)
    return l1_2(defects[0]) + l1_2(defects[1])


def coupled_blind_spot_witness(e: int) -> Vec2:
    """A nonzero vector in edge e's blind spot: the basis vector e_e.

    Edge e's only watcher is evaluator e, which reads coordinate other(e),
    so e_e (nonzero) is measured as 0.
    """
    return (ONE if e == 0 else ZERO, ONE if e == 1 else ZERO)


def coupled_all_green_forces_zero(sx: Vec2) -> bool:
    """All-Green at s(x) forces s(x) = 0 and hence I = 0 (replays Theorem 6).

    Returns True exactly when: tallies zero implies sx == (0, 0) and I == 0.
    For a non-All-Green sx the implication is vacuously True.
    """
    t0, t1 = coupled_tallies(sx)
    if t0 == ZERO and t1 == ZERO:
        return sx == (ZERO, ZERO) and coupled_raw_norm(sx) == ZERO
    return True


# ---------------------------------------------------------------------------
# Repair mass and the Phi = 2 minimum (the Remark; Lean QuotientWitness).
#
# Scalar coupled diagram: any repair with overlap value alpha produces the
# pattern (-alpha, -alpha); the witness pattern is omega = (1, -1).
# ---------------------------------------------------------------------------

OMEGA: Vec2 = (ONE, -ONE)


def d0(alpha: Fraction) -> Vec2:
    """The pattern produced by the repair with overlap value alpha."""
    return (-alpha, -alpha)


def repair_mass(alpha: Fraction) -> Fraction:
    """l1 distance from omega = (1, -1) to the repair d0(alpha):
    |1 + alpha| + |alpha - 1|."""
    r = d0(alpha)
    return abs(OMEGA[0] - r[0]) + abs(OMEGA[1] - r[1])


def phi_lower_bound() -> Fraction:
    """The exact lower bound 2, via the triangle identity
    |1 + a| + |1 - a| >= |(1 + a) + (1 - a)| = 2."""
    return Fraction(2)


def attained_at_zero() -> bool:
    """The bound is attained by the zero repair: repair_mass(0) == 2."""
    return repair_mass(ZERO) == Fraction(2)


def omega_not_exact(alpha: Fraction) -> bool:
    """No repair reaches omega: d0(alpha) != (1, -1) for this alpha."""
    return d0(alpha) != OMEGA


def component_l1(residual: Vec2) -> Fraction:
    """Sum of absolute residual coordinates."""
    return abs(residual[0]) + abs(residual[1])


def component_l2_sq(residual: Vec2) -> Fraction:
    """Sum of squares of the residual coordinates. No square root."""
    return residual[0] * residual[0] + residual[1] * residual[1]


def component_linf(residual: Vec2) -> Fraction:
    """Largest absolute residual coordinate."""
    return max(abs(residual[0]), abs(residual[1]))


def diag_residual(a: Fraction, b: Fraction, alpha: Fraction) -> Vec2:
    """Residual (a+alpha, b+alpha) on the diagonal repair image."""
    return (a + alpha, b + alpha)


def skew_residual(a: Fraction, b: Fraction, alpha: Fraction) -> Vec2:
    """Residual (a+alpha, b+2*alpha) on the line (-alpha, -2*alpha)."""
    return (a + alpha, b + 2 * alpha)


def diag_closed(
    a: Fraction, b: Fraction
) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    """Diagonal closed forms: ell-one value, squared Euclidean value,
    supremum value, attainment lower endpoint, upper endpoint, and midpoint.

    The squared Euclidean value is (a-b)^2 / 2. The positive square root of
    that value is the manuscript name Phi_2; this function does not take it.
    """
    gap = abs(a - b)
    return (gap, gap * gap / 2, gap / 2, -max(a, b), -min(a, b), -(a + b) / 2)


def skew_closed(
    a: Fraction, b: Fraction
) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    """Skew closed forms: ell-one value, squared Euclidean value, supremum
    value, and the three attainment points.

    The squared Euclidean value is (2a-b)^2 / 5. The positive square root is
    the manuscript name Phi_2; this function does not take it.
    """
    gap = abs(2 * a - b)
    return (
        gap / 2,
        gap * gap / 5,
        gap / 3,
        -b / 2,
        -(a + 2 * b) / 5,
        -(a + b) / 3,
    )


def zero_repair_norm(a: Fraction, b: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """Ell-one, squared Euclidean, and supremum norms of the vector (a, b)."""
    return (abs(a) + abs(b), a * a + b * b, max(abs(a), abs(b)))


# ---------------------------------------------------------------------------
# Deterministic receipt.
# ---------------------------------------------------------------------------


def _receipt_lines() -> Sequence[str]:
    lam_checks = all(
        three_patch_raw_norm(lam) == 6 * abs(lam)
        and three_patch_tallies(lam) == (ZERO, ZERO, ZERO)
        for lam in (ONE, Fraction(2), Fraction(7, 3), Fraction(-5, 2))
    )
    coupled_ok = coupled_all_green_forces_zero((ZERO, ZERO)) and all(
        coupled_tallies(sx) != (ZERO, ZERO)
        for sx in ((ONE, ZERO), (ZERO, ONE), (ONE, ONE))
    )
    r2 = diag_closed(ONE, -ONE)
    r4 = skew_closed(ONE, -ONE)
    return (
        f"I={three_patch_raw_norm(ONE)}",
        f"J=[{', '.join(str(t) for t in three_patch_tallies(ONE))}]",
        f"coverage={'full' if three_patch_full_coverage() else 'PARTIAL'}",
        f"6lam-checks={'pass' if lam_checks else 'FAIL'}",
        f"coupled={'forced' if coupled_ok else 'FAIL'}",
        f"phi={phi_lower_bound()}",
        f"r2-l1={r2[0]}",
        f"r2-l2sq={r2[1]}",
        f"r2-linf={r2[2]}",
        f"r2-interval={r2[3]},{r2[4]}",
        f"r2-mid={r2[5]}",
        f"r4-l1={r4[0]}",
        f"r4-l2sq={r4[1]}",
        f"r4-linf={r4[2]}",
        f"r4-alpha={r4[3]},{r4[4]},{r4[5]}",
    )


if __name__ == "__main__":
    print(" ".join(_receipt_lines()))
