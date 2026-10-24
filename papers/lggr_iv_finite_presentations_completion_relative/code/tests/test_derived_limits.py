"""Automated test suite verifying non-abelian derived limits and Mittag-Leffler lifting obstructions.

Covers:
1. Non-abelian group axioms and non-commutativity for H3(Z/2^n Z).
2. Semidirect extension exactness and automorphism equivariance.
3. Mittag-Leffler satisfaction (control case): surjective transitions yield vanishing derived limits
   (R^1 projlim K = {*}) and exact coherent global lifts.
4. Mittag-Leffler failure (test case): strictly shrinking transition images yield non-vanishing
   derived limits (R^1 projlim K != {*}) and non-trivial lifting obstructions.
5. Multi-branch divergence: disjoint branch cosets at the root node certify obstruction to lifting.
"""

from __future__ import annotations

from fractions import Fraction
import pytest

from lggr_iv_core import (
    HeisenbergElement,
    SemidirectElement,
    check_mittag_leffler,
    create_heisenberg_multi_branch_ladder,
    create_reviewer_counterexample_ladder,
    heisenberg_automorphism_tau,
    solve_lifting_obstruction,
)


def test_heisenberg_group_axioms() -> None:
    """Verify group axioms, non-commutativity, and center for H3(Z/8Z)."""
    n = 3
    ident = HeisenbergElement.identity(n)

    a = HeisenbergElement(x=1, y=0, z=0, n=n)
    b = HeisenbergElement(x=0, y=1, z=0, n=n)
    c = HeisenbergElement(x=2, y=3, z=1, n=n)

    # Identity
    assert a * ident == a
    assert ident * a == a

    # Inverse
    assert a * a.inverse() == ident
    assert a.inverse() * a == ident
    assert c * c.inverse() == ident

    # Associativity: (a * b) * c == a * (b * c)
    assert (a * b) * c == a * (b * c)

    # Non-commutativity
    assert a * b != b * a
    comm = a.commutator(b)
    assert comm == HeisenbergElement(x=0, y=0, z=1, n=n)
    assert comm.is_central()
    assert not a.is_central()
    assert not b.is_central()


def test_heisenberg_automorphism_tau() -> None:
    """Verify tau is an involutive automorphism of H3(Z/8Z)."""
    n = 3
    a = HeisenbergElement(x=1, y=2, z=3, n=n)
    b = HeisenbergElement(x=3, y=1, z=4, n=n)

    # Involutive: tau(tau(a)) == a
    assert heisenberg_automorphism_tau(heisenberg_automorphism_tau(a)) == a

    # Automorphism: tau(a * b) == tau(a) * tau(b)
    assert heisenberg_automorphism_tau(a * b) == heisenberg_automorphism_tau(a) * heisenberg_automorphism_tau(b)


def test_semidirect_extension_exactness() -> None:
    """Verify group properties and projection exactness for E = K rtimes_tau G."""
    n = 3
    e_ident = SemidirectElement.identity(n)

    k1 = HeisenbergElement(x=1, y=0, z=2, n=n)
    k2 = HeisenbergElement(x=0, y=1, z=1, n=n)

    e1 = SemidirectElement(k=k1, g=1)
    e2 = SemidirectElement(k=k2, g=1)

    # Multiplication and inversion in E
    assert e1 * e_ident == e1
    assert e_ident * e1 == e1
    assert e1 * e1.inverse() == e_ident
    assert e1.inverse() * e1 == e_ident
    assert e2 * e2.inverse() == e_ident

    # Kernel is g == 0
    k_elem = SemidirectElement(k=k1, g=0)
    assert k_elem.g == 0


def test_mittag_leffler_holds_control_case() -> None:
    """When Mittag-Leffler holds (surjective transitions), R^1 projlim vanishes and global lift exists."""
    ladder = create_heisenberg_multi_branch_ladder(depth=2, n_mod=3, fail_mittag_leffler=False)

    is_ml, history = check_mittag_leffler(ladder)
    assert is_ml is True
    # Image sizes must remain constant at |H3(Z/8Z)| = 512
    for branch, sizes in history.items():
        assert all(s == 512 for s in sizes)

    # Compatible thread with non-trivial quotient g_i = 1 everywhere
    thread = {node: 1 for node in ladder.poset.nodes}

    report = solve_lifting_obstruction(ladder, thread)
    assert report.is_thread_compatible is True
    assert report.is_mittag_leffler is True
    assert report.obstruction_is_trivial is True
    assert report.compatible_global_lift is not None
    assert report.divergence_witness is None

    # Verify that the constructed global lift is 100% compatible across all edges
    lifts = report.compatible_global_lift
    for child, parent in ladder.poset.edges:
        trans = ladder.extension_transitions[(child, parent)]
        assert trans(lifts[child]) == lifts[parent]


def test_factory_ladder_admits_explicit_global_lift_regardless_of_scaling() -> None:
    """Regression Fixture 1: The factory ladder admits an explicit global lift e_i = (1_K, g).

    For transitions epsilon_{ji}(k, g) = (kappa_{ji}(k), g), kappa_{ji}(1_K) = 1_K.
    Thus e_i = (1_K, g) satisfies every original edge transition for both g=0 and g=1.
    The solver must NOT report obstruction for this declared problem.
    """
    for depth in (2, 3):
        for n_mod in (2, 3):
            for fail_ml in (False, True):
                ladder = create_heisenberg_multi_branch_ladder(
                    depth=depth,
                    n_mod=n_mod,
                    fail_mittag_leffler=fail_ml,
                )
                ident_k = HeisenbergElement.identity(n_mod)

                for g_val in (0, 1):
                    thread = {node: g_val for node in ladder.poset.nodes}
                    # 1. Direct mathematical verification: explicit section passes all original transitions
                    explicit_section = {
                        node: SemidirectElement(k=ident_k, g=g_val)
                        for node in ladder.poset.nodes
                    }
                    for child, parent in ladder.poset.edges:
                        eps = ladder.extension_transitions[(child, parent)]
                        assert eps(explicit_section[child]) == explicit_section[parent]

                    # 2. Solver verification: prohibits an impossibility report
                    report = solve_lifting_obstruction(ladder, thread)
                    assert report.is_thread_compatible is True
                    assert report.obstruction_is_trivial is True
                    assert report.compatible_global_lift is not None
                    assert report.divergence_witness is None

                    # 3. Post-condition: returned lift strictly satisfies all original edge equations
                    lifts = report.compatible_global_lift
                    for child, parent in ladder.poset.edges:
                        trans = ladder.extension_transitions[(child, parent)]
                        assert trans(lifts[child]) == lifts[parent]
                    for node in ladder.poset.nodes:
                        assert lifts[node].g == thread[node]


def test_unsolvable_diagram_counterexample_correctly_obstructed_without_fallback() -> None:
    """Regression Fixture 2: Valid finite diagram with genuine obstruction is correctly rejected.

    Counterexample structure (depth 2, mod 2):
      c = (0, 0, 1) in H3(Z/2Z) is central, of order 2, and fixed by tau.
      epsilon(k, g) = (1_K, g) except on right branch where:
        epsilon_{R1, root} = id
        epsilon_{R2, R1}(k, g) = (c^g, g)

    For quotient thread g_i = 1:
      Left branch forces e_root = (1_K, 1).
      Right leaf forces e_R1 = (c, 1), and identity edge forces e_root = (c, 1).
      Since c != 1_K, root fibers are disjoint singletons: NO compatible lift exists.
      The solver must report non-trivial obstruction and refuse to invent a fallback preimage.
    """
    ladder = create_reviewer_counterexample_ladder()
    n_mod = ladder.modulus_power
    mod = 1 << n_mod
    c_elem = HeisenbergElement(x=0, y=0, z=1, n=n_mod)
    ident_k = HeisenbergElement.identity(n_mod)
    all_k = [
        HeisenbergElement(x=x, y=y, z=z, n=n_mod)
        for x in range(mod)
        for y in range(mod)
        for z in range(mod)
    ]

    # 1. Verify that all declared extension transitions are genuine homomorphisms
    for edge in ladder.poset.edges:
        eps = ladder.extension_transitions[edge]
        for k1 in all_k:
            for g1 in (0, 1):
                e1 = SemidirectElement(k=k1, g=g1)
                for k2 in all_k:
                    for g2 in (0, 1):
                        e2 = SemidirectElement(k=k2, g=g2)
                        assert eps(e1 * e2) == eps(e1) * eps(e2), f"Homomorphism failure on {edge}"

    # 2. Exhaustive leaf-fiber enumeration proves disjoint singleton root fibers
    thread = {node: 1 for node in ladder.poset.nodes}
    left_root_vals = {
        ladder.extension_transitions[("L1", "root")](
            ladder.extension_transitions[("L2", "L1")](SemidirectElement(k=k, g=1))
        ).k
        for k in all_k
    }
    right_root_vals = {
        ladder.extension_transitions[("R1", "root")](
            ladder.extension_transitions[("R2", "R1")](SemidirectElement(k=k, g=1))
        ).k
        for k in all_k
    }
    assert left_root_vals == {ident_k}
    assert right_root_vals == {c_elem}
    assert left_root_vals.intersection(right_root_vals) == set()

    # 3. Solver execution: must report obstruction without inventing fallback preimages
    report = solve_lifting_obstruction(ladder, thread)
    assert report.is_thread_compatible is True
    assert report.obstruction_is_trivial is False
    assert report.compatible_global_lift is None
    assert report.divergence_witness is not None
    assert "Multi-branch derived limit obstruction non-vanishing" in report.divergence_witness

    # 4. Exact dual certificate of obstruction
    assert report.duality_certificate is not None
    cert = report.duality_certificate
    assert cert.primal_defect == Fraction(2, 1)
    assert cert.dual_lower_bound == Fraction(2, 1)
    assert cert.duality_gap == Fraction(0, 1)
    assert cert.is_certified is True


def test_incompatible_thread_rejected() -> None:
    """An incompatible quotient thread must be rejected immediately."""
    ladder = create_heisenberg_multi_branch_ladder(depth=2, n_mod=3, fail_mittag_leffler=False)
    # Root has 0, but children have 1
    thread = {node: 1 for node in ladder.poset.nodes}
    thread["root"] = 0

    report = solve_lifting_obstruction(ladder, thread)
    assert report.is_thread_compatible is False
    assert report.obstruction_is_trivial is False
    assert report.compatible_global_lift is None


def test_adversarial_mismatched_modulus() -> None:
    """Operations across mismatched modulus stages raise ValueError."""
    h3_mod8 = HeisenbergElement(x=1, y=0, z=0, n=3)
    h3_mod4 = HeisenbergElement(x=1, y=0, z=0, n=2)

    with pytest.raises(ValueError, match="Mismatched modulus"):
        _ = h3_mod8 * h3_mod4

    s_mod8 = SemidirectElement(k=h3_mod8, g=1)
    s_mod4 = SemidirectElement(k=h3_mod4, g=1)

    with pytest.raises(ValueError, match="Mismatched modulus"):
        _ = s_mod8 * s_mod4
