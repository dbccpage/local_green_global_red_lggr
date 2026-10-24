"""Tests for exact rational duality certifier on the group algebra Q[G] in LGGR IV.

Validates:
1. Exact rational group algebra Q[G] vector operations, norms, and dual pairings.
2. Duality gap vanishing (Primal == Dual == 0) when Mittag-Leffler holds and lifts exist.
3. Explicit positive lower bound certification (Primal == Dual == 2(B - k*) >= 2 > 0) when Mittag-Leffler fails.
4. Complete machine verification of dual witness feasibility inequalities on Q[G].
5. Multi-branch (B = 2, B = 3) consensus certificates and moment matrix state positivity.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Callable

from lggr_iv_core import (
    GroupAlgebraElement,
    HeisenbergElement,
    MultiBranchLadderSystem,
    MultiBranchPoset,
    SemidirectElement,
    certify_non_abelian_lifting_duality,
    create_heisenberg_multi_branch_ladder,
    create_reviewer_counterexample_ladder,
    solve_lifting_obstruction,
)


def test_group_algebra_operations() -> None:
    """Validate exact rational vector operations, norms, and pairings on Q[G]."""
    g1 = HeisenbergElement(x=0, y=0, z=1, n=2)
    g2 = HeisenbergElement(x=1, y=0, z=0, n=2)
    g3 = HeisenbergElement(x=0, y=1, z=0, n=2)

    p1 = GroupAlgebraElement.pure(g1)
    p2 = GroupAlgebraElement.pure(g2)
    assert p1.l1_norm() == Fraction(1, 1)
    assert p1.l_inf_norm() == Fraction(1, 1)

    # Addition and scaling
    combo = p1 * Fraction(3, 4) + p2 * Fraction(-1, 2)
    assert combo.coeffs[g1] == Fraction(3, 4)
    assert combo.coeffs[g2] == Fraction(-1, 2)
    assert combo.l1_norm() == Fraction(3, 4) + Fraction(1, 2)  # 5/4
    assert combo.l_inf_norm() == Fraction(3, 4)

    # Subtraction to zero
    diff = p1 - p1
    assert diff.l1_norm() == Fraction(0, 1)
    assert len(diff.coeffs) == 0

    # Uniform distribution
    unif = GroupAlgebraElement.uniform([g1, g2, g3])
    assert unif.l1_norm() == Fraction(1, 1)
    assert unif.coeffs[g1] == Fraction(1, 3)
    assert unif.coeffs[g2] == Fraction(1, 3)
    assert unif.coeffs[g3] == Fraction(1, 3)

    # Dual pairing <W, alpha>
    w = GroupAlgebraElement(coeffs={g1: Fraction(1, 1), g2: Fraction(-1, 1)})
    assert w.l_inf_norm() == Fraction(1, 1)
    assert w.dot(p1) == Fraction(1, 1)
    assert w.dot(p2) == Fraction(-1, 1)
    # Holder inequality: |<W, alpha>| <= ||W||_inf * ||alpha||_1
    val = w.dot(combo)
    assert val == Fraction(3, 4) * 1 + Fraction(-1, 2) * (-1)  # 3/4 + 1/2 = 5/4
    assert abs(val) <= w.l_inf_norm() * combo.l1_norm()


def test_exact_duality_vanishing_when_mittag_leffler_holds() -> None:
    """Under Mittag-Leffler, lifting defect is 0 and dual lower bound is certified to be 0."""
    ladder = create_heisenberg_multi_branch_ladder(depth=2, n_mod=3, fail_mittag_leffler=False)
    thread = {node: 1 for node in ladder.poset.nodes}
    report = solve_lifting_obstruction(ladder, thread)

    assert report.is_thread_compatible is True
    assert report.is_mittag_leffler is True
    assert report.obstruction_is_trivial is True
    assert report.duality_certificate is not None

    cert = report.duality_certificate
    assert cert.is_mittag_leffler is True
    assert cert.primal_defect == Fraction(0, 1)
    assert cert.dual_lower_bound == Fraction(0, 1)
    assert cert.duality_gap == Fraction(0, 1)
    assert cert.is_certified is True
    assert cert.moment_matrix_is_psd is True


def test_exact_duality_positive_lower_bound_when_mittag_leffler_fails() -> None:
    """When a diagram has a genuine obstruction, dual certifier bounds lifting defect strictly from below."""
    ladder = create_reviewer_counterexample_ladder()
    thread = {node: 1 for node in ladder.poset.nodes}
    report = solve_lifting_obstruction(ladder, thread)

    assert report.is_thread_compatible is True
    assert report.obstruction_is_trivial is False
    assert report.duality_certificate is not None

    cert = report.duality_certificate
    assert cert.primal_defect == Fraction(2, 1)
    assert cert.dual_lower_bound == Fraction(2, 1)
    assert cert.duality_gap == Fraction(0, 1)
    assert cert.is_certified is True
    assert cert.dual_lower_bound > Fraction(0, 1)


def test_exact_dual_witness_feasibility_invariants() -> None:
    """Check every dual constraint in Q[G]* directly with exact rational arithmetic."""
    ladder = create_reviewer_counterexample_ladder()
    thread = {node: 1 for node in ladder.poset.nodes}
    report = solve_lifting_obstruction(ladder, thread)
    cert = report.duality_certificate
    assert cert is not None

    B = len(cert.dual_witness_cochains)
    assert B == 2

    # Check 1: ||W_b||_infty <= 1
    for b_idx in range(B):
        w = cert.dual_witness_cochains[b_idx]
        assert w.l_inf_norm() <= 1

    # Check 2: W_b(g) <= alpha_b for all g in branch coset T_b
    for b_idx in range(B):
        w = cert.dual_witness_cochains[b_idx]
        alpha = cert.dual_scalar_alphas[b_idx]
        coset = report.branch_cosets[b_idx]
        for g in coset:
            assert w.coeffs[g] <= alpha

    # Check 3: sum_b W_b(g) >= mu for all g in K_0
    mod = 1 << ladder.modulus_power
    for x in range(mod):
        for y in range(mod):
            for z in range(mod):
                elem = HeisenbergElement(x=x, y=y, z=z, n=ladder.modulus_power)
                total_w = sum((cert.dual_witness_cochains[b].coeffs[elem] for b in range(B)), Fraction(0, 1))
                assert total_w >= cert.dual_scalar_mu

    # Check 4: Dual objective value matches dual lower bound
    dual_obj = cert.dual_scalar_mu - sum(cert.dual_scalar_alphas, Fraction(0, 1))
    assert dual_obj == cert.dual_lower_bound == Fraction(2, 1)


def test_three_branch_exact_duality_consensus() -> None:
    """Validate duality certificate on a 3-branch ladder system."""
    root = "root"
    b1 = ("L1", "L2")
    b2 = ("M1", "M2")
    b3 = ("R1", "R2")
    nodes = (root, *b1, *b2, *b3)
    edges = (
        ("L1", root), ("L2", "L1"),
        ("M1", root), ("M2", "M1"),
        ("R1", root), ("R2", "R1"),
    )
    poset = MultiBranchPoset(nodes=nodes, edges=edges, root=root, branches=(b1, b2, b3))
    n_mod = 2
    mod = 1 << n_mod

    # Strictly shrinking kernel transitions (scale by 2)
    def trans(k: HeisenbergElement) -> HeisenbergElement:
        return HeisenbergElement(x=(2 * k.x) % mod, y=(2 * k.y) % mod, z=(4 * k.z) % mod, n=n_mod)

    kernel_trans: dict[tuple[str, str], Callable[[HeisenbergElement], HeisenbergElement]] = {
        edge: trans for edge in edges
    }
    ext_trans: dict[tuple[str, str], Callable[[SemidirectElement], SemidirectElement]] = {
        edge: (lambda e: SemidirectElement(k=trans(e.k), g=e.g)) for edge in edges
    }

    ladder = MultiBranchLadderSystem(
        poset=poset,
        modulus_power=n_mod,
        kernel_transitions=kernel_trans,
        extension_transitions=ext_trans,
        is_failing_mittag_leffler=True,
    )

    # Explicitly separate branch cosets at the root
    all_k = [HeisenbergElement(x=x, y=y, z=z, n=n_mod) for x in range(mod) for y in range(mod) for z in range(mod)]
    im = {trans(trans(k)) for k in all_k}

    c1 = HeisenbergElement(x=0, y=0, z=0, n=n_mod)
    c2 = HeisenbergElement(x=1, y=0, z=0, n=n_mod)
    c3 = HeisenbergElement(x=0, y=1, z=0, n=n_mod)

    t1 = {c1 * k for k in im}
    t2 = {c2 * k for k in im}
    t3 = {c3 * k for k in im}

    cert = certify_non_abelian_lifting_duality(ladder, [t1, t2, t3])
    assert cert.is_certified is True
    assert cert.duality_gap == Fraction(0, 1)
    # B = 3, branch cosets have pairwise disjointness or partial overlap
    assert cert.primal_defect >= Fraction(2, 1)
    assert cert.dual_lower_bound == cert.primal_defect


def test_empty_branch_edge_case() -> None:
    """Empty branch set edge case returns certified zero defect."""
    poset = MultiBranchPoset(nodes=("root",), edges=(), root="root", branches=())
    ladder = MultiBranchLadderSystem(
        poset=poset,
        modulus_power=2,
        kernel_transitions={},
        extension_transitions={},
        is_failing_mittag_leffler=False,
    )
    cert = certify_non_abelian_lifting_duality(ladder, [])
    assert cert.is_certified is True
    assert cert.primal_defect == Fraction(0, 1)
    assert cert.dual_lower_bound == Fraction(0, 1)
    assert cert.duality_gap == Fraction(0, 1)


def test_certify_duality_none_cosets_default() -> None:
    """Validate certify_non_abelian_lifting_duality when branch_cosets is None (computed internally)."""
    ladder = create_heisenberg_multi_branch_ladder(depth=2, n_mod=2, fail_mittag_leffler=True)
    cert = certify_non_abelian_lifting_duality(ladder, branch_cosets=None)
    assert cert.is_certified is True
    assert cert.duality_gap == Fraction(0, 1)


def test_group_algebra_and_classification_edge_cases() -> None:
    """Test group algebra empty cases and witness classification invalid cases."""
    from lggr_iv_core import WitnessClassification, classify_rational_witness

    empty_unif = GroupAlgebraElement.uniform([])
    assert empty_unif.l1_norm() == Fraction(0, 1)
    assert empty_unif.l_inf_norm() == Fraction(0, 1)

    g = HeisenbergElement(x=0, y=0, z=0, n=2)
    elem = GroupAlgebraElement.pure(g)
    zero_scale = elem * 0
    assert zero_scale.l1_norm() == Fraction(0, 1)

    # Denominator divisible by 2 for candidate satisfying equation (e.g. custom equation)
    # 2*z - 1 = 0 has solution 1/2 which has even denominator
    even_denom_class = classify_rational_witness(Fraction(1, 2), lambda z: 2 * z - 1)
    assert even_denom_class == WitnessClassification.INVALID

