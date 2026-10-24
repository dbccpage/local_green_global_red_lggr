"""Check original-input witnesses, strict boundaries, and fail-closed extraction."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contextuality_lp as lp


@pytest.mark.parametrize("c,a,b", [
    ([1], [[1], [1]], [0, 1]), ([0], [[1]], [-1]),
    ([], [[]], [-1]), ([0, 1], [[1, 1], [-2, -2], [0, 0]], [1, -3, 0]),
])
def test_infeasibility_witness(c, a, b):
    with pytest.raises(lp.CertifiedInfeasible) as caught:
        lp.solve_standard(c, a, b)
    cert = caught.value.certificate
    assert lp.verify_infeasible(c, a, b, cert)
    assert not lp.verify_infeasible(c, a, b, replace(cert, dual=tuple(-y for y in cert.dual)))
    assert not lp.verify_infeasible(c, a, [0] * len(b), cert)
    assert not lp.verify_infeasible(c, a, b, replace(cert, dual=(Q(0),) * len(b)))


@pytest.mark.parametrize("c,a,b", [
    ([-1], [], []), ([-1, 0], [[1, -1]], [2]),
    ([-1, 0], [[-1, 1]], [-2]),
    ([-1, 0], [[1, -1], [2, -2], [0, 0]], [2, 4, 0]),
])
def test_unboundedness_witness(c, a, b):
    with pytest.raises(lp.CertifiedUnbounded) as caught:
        lp.solve_standard(c, a, b)
    cert = caught.value.certificate
    assert lp.verify_unbounded(c, a, b, cert)
    assert not lp.verify_unbounded(c, a, b, replace(cert, direction=(Q(0),) * len(c)))
    assert not lp.verify_unbounded([-v for v in c], a, b, cert)
    assert not lp.verify_unbounded(c, a, b, replace(cert, direction=tuple(-v for v in cert.direction)))
    # Replay the ray at exact parameters, including beyond the pivot search.
    for t in (Q(0), Q(1, 7), Q(10**9)):
        x = tuple(p + t * d for p, d in zip(cert.primal, cert.direction))
        assert all(v >= 0 for v in x)
        assert all(lp.dot(tuple(map(Q, row)), x) == v for row, v in zip(a, b))
        assert lp.dot(tuple(map(Q, c)), x) == lp.dot(c, cert.primal) + t * lp.dot(c, cert.direction)


@pytest.mark.parametrize("bad", [True, 0.0, "0", None])
def test_new_checkers_reject_nonexact_problem_inputs(bad):
    infeasible = lp.InfeasibilityCertificate((Q(1),), 0)
    unbounded = lp.UnboundednessCertificate((Q(0),), (Q(1),), 0)
    assert not lp.verify_infeasible([bad], [[Q(1)]], [Q(-1)], infeasible)
    assert not lp.verify_unbounded([bad], [], [], unbounded)


@pytest.mark.parametrize("bad", [True, 0, 0.0, "0", None])
def test_new_checkers_reject_nonexact_witness_entries(bad):
    assert not lp.verify_infeasible([0], [[1]], [-1], lp.InfeasibilityCertificate((bad,), 0))
    assert not lp.verify_unbounded([-1], [], [], lp.UnboundednessCertificate((bad,), (Q(1),), 0))
    assert not lp.verify_unbounded([-1], [], [], lp.UnboundednessCertificate((Q(0),), (bad,), 0))


@pytest.mark.parametrize("bad", [True, -1, 0.0, "0", None])
def test_new_checkers_reject_bad_metadata(bad):
    assert not lp.verify_infeasible([0], [[1]], [-1], lp.InfeasibilityCertificate((Q(1),), bad))
    assert not lp.verify_unbounded([-1], [], [], lp.UnboundednessCertificate((Q(0),), (Q(1),), bad))


@pytest.mark.parametrize("cert", [None, object(), (), lp.LPCertificate((), (), Q(0), 0)])
def test_new_checkers_reject_wrong_certificate_types(cert):
    assert not lp.verify_infeasible([0], [[1]], [-1], cert)
    assert not lp.verify_unbounded([-1], [], [], cert)


def test_ray_needs_feasible_base_and_original_rows():
    cert = lp.UnboundednessCertificate((Q(2), Q(0)), (Q(1), Q(1)), 1)
    assert lp.verify_unbounded([-1, 0], [[1, -1]], [2], cert)
    assert not lp.verify_unbounded([-1, 0], [[1, -1]], [3], cert)
    assert not lp.verify_unbounded([-1, 0], [[1, 1]], [2], cert)
    assert not lp.verify_unbounded([-1, 0], [[1, -1]], [2], replace(cert, primal=(Q(-1), Q(-3))))


def test_budget_refusal_carries_no_mathematical_certificate():
    with pytest.raises(lp.Refusal) as caught:
        lp.solve_standard([-1, 0], [[1, -1]], [2], max_pivots=0)
    assert type(caught.value) is lp.Refusal
    assert caught.value.kind == "BUDGET_EXHAUSTED"
    assert not hasattr(caught.value, "certificate")
    # No pivot is necessary for these two independently checkable outcomes.
    with pytest.raises(lp.CertifiedInfeasible):
        lp.solve_standard([], [[]], [-1], max_pivots=0)
    with pytest.raises(lp.CertifiedUnbounded):
        lp.solve_standard([-1], [], [], max_pivots=0)


@pytest.mark.parametrize("checker,c,a,b", [
    ("verify_infeasible", [0], [[1]], [-1]),
    ("verify_unbounded", [-1, 0], [[1, -1]], [2]),
])
def test_failed_final_replay_never_promotes_outcome(monkeypatch, checker, c, a, b):
    monkeypatch.setattr(lp, checker, lambda *args: False)
    with pytest.raises(lp.Refusal) as caught:
        lp.solve_standard(c, a, b)
    assert type(caught.value) is lp.Refusal
    assert caught.value.kind == "CERTIFICATE_MISMATCH"


def test_malformed_shapes_rejected_by_checkers():
    i = lp.InfeasibilityCertificate((Q(1),), 0)
    u = lp.UnboundednessCertificate((Q(0),), (Q(1),), 0)
    for c, a, b in (([0], [], [1]), ([0], [[1, 2]], [1]), (None, [], []), ([0], [None], [1])):
        assert not lp.verify_infeasible(c, a, b, i)
        assert not lp.verify_unbounded(c, a, b, u)
    assert not lp.verify_infeasible([0], [[1]], [-1], replace(i, dual=()))
    assert not lp.verify_unbounded([-1], [], [], replace(u, direction=()))
