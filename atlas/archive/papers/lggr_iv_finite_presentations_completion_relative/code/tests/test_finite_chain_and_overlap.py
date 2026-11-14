"""Finite-chain threads and the overlap defect identity for LGGR IV."""

from __future__ import annotations

from fractions import Fraction

import pytest

from lggr_iv_core import (
    check_finite_chain,
    create_heisenberg_multi_branch_ladder,
    finite_chain_thread,
    overlap_certificate,
    overlap_dual_matches,
    solve_lifting_obstruction,
)


def test_finite_chain_thread() -> None:
    """The shipped pullback is nonempty, ends at the top element, and matches each transition."""
    steps = (lambda stage: stage - 1, lambda stage: stage // 2)
    thread = finite_chain_thread(8, steps)
    assert check_finite_chain(thread, steps) is True
    assert thread[-1] == 8
    assert len(thread) == len(steps) + 1

    one_stage = finite_chain_thread(5, ())
    assert check_finite_chain(one_stage, ()) is True
    assert one_stage == [5]

    with pytest.raises(ValueError, match="empty thread"):
        check_finite_chain([], ())
    with pytest.raises(ValueError, match="bad length"):
        check_finite_chain([1, 2], ())
    with pytest.raises(ValueError, match="incompatible transition"):
        check_finite_chain([0, 1], (lambda stage: stage + 3,))


def test_overlap_certificate() -> None:
    """The shipped overlap defect equals the dual value and the ladder certificate."""
    full = ([1, 1, 2], [2, 3], [2])
    branch_count, max_overlap, primal = overlap_certificate(full)
    assert (branch_count, max_overlap, primal) == (3, 3, 0)
    assert overlap_dual_matches(full) == (0, 0)

    disjoint = ([1], [2], [3])
    branch_count, max_overlap, primal = overlap_certificate(disjoint)
    assert (branch_count, max_overlap, primal) == (3, 1, 4)
    primal_dual, dual = overlap_dual_matches(disjoint)
    assert primal_dual == dual == 4
    assert dual > 0

    empty_fibers = ([], [])
    assert overlap_certificate(empty_fibers) == (2, 0, 4)

    with pytest.raises(ValueError, match="families must be nonempty"):
        overlap_certificate(())

    for failing in (False, True):
        ladder = create_heisenberg_multi_branch_ladder(
            depth=2,
            n_mod=2,
            fail_mittag_leffler=failing,
        )
        thread = {node: 1 for node in ladder.poset.nodes}
        report = solve_lifting_obstruction(ladder, thread)
        assert report.duality_certificate is not None
        _, _, ladder_primal = overlap_certificate(report.branch_cosets)
        assert Fraction(ladder_primal) == report.duality_certificate.primal_defect
        matched_primal, matched_dual = overlap_dual_matches(report.branch_cosets)
        assert Fraction(matched_primal) == report.duality_certificate.primal_defect
        assert Fraction(matched_dual) == report.duality_certificate.dual_lower_bound
