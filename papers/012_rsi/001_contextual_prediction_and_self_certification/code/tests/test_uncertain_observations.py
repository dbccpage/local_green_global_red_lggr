"""Unchanged observations, explicit error radius, independently checked bounds."""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contextuality_lp as lp
import epistemic_kernel as k


def bell(table):
    return lp.Scenario((2, 2, 2, 2), ((0, 2), (0, 3), (1, 2), (1, 3)),
                       tuple(tuple(table[c].get(o, Q(0)) for o in product((0, 1), repeat=2))
                             for c in k.CONTEXTS))


def noisy_classical():
    truth = bell(k.classical_mixture())
    tables = [list(row) for row in truth.tables]
    tables[0][0] -= Q(1, 100)
    tables[0][2] += Q(1, 100)
    return truth, replace(truth, tables=tables)


def test_review_noise_alone_erases_raw_margin_and_preserves_input():
    truth, observed = noisy_classical()
    original = [row[:] for row in observed.tables]
    with pytest.raises(lp.Refusal, match="SIGNALLING"):
        lp.evaluate(observed)
    assignments, columns, target = lp.contextual_matrix(truth)
    new_assignments, new_columns, noisy = lp.observed_matrix(observed)
    assert (assignments, columns) == (new_assignments, new_columns)
    radius = sum(abs(x-y) for x, y in zip(target, noisy))
    result = lp.evaluate_observed(observed, radius)
    assert radius == result.certificate.defect == Q(1, 50)
    assert result.guaranteed_margin == 0
    assert result.observed == tuple(x for row in original for x in row)
    assert observed.tables == original
    assert lp.verify_observed(observed, radius, result)
    assert not hasattr(result, "kind")  # no classification of the unknown true table
    observed.tables[0][0] -= Q(1, 100)
    observed.tables[0][2] += Q(1, 100)
    assert not lp.verify_observed(observed, radius, result)


@pytest.mark.parametrize("field", ["observed", "assignments", "radius", "certificate", "guaranteed_margin"])
def test_result_fields_are_bound_to_original_observations_and_radius(field):
    _, model = noisy_classical()
    result = lp.evaluate_observed(model, Q(1, 50))
    if field == "observed":
        value = (result.observed[0] + 1,) + result.observed[1:]
    elif field == "assignments":
        value = result.assignments[::-1]
    elif field == "certificate":
        value = replace(result.certificate, witness=(Q(0),)*len(result.observed))
    else:
        value = getattr(result, field) + 1
    assert not lp.verify_observed(model, Q(1, 50), replace(result, **{field: value}))


@pytest.mark.parametrize("radius,kind", [(Q(-1), "INVALID_RADIUS"), (True, "NONEXACT_INPUT"),
                                         (0.02, "NONEXACT_INPUT"), ("1/50", "NONEXACT_INPUT")])
def test_radius_requires_nonnegative_exact_input(radius, kind):
    _, model = noisy_classical()
    with pytest.raises(lp.Refusal, match=kind):
        lp.evaluate_observed(model, radius)


def test_zero_radius_and_radius_sensitivity():
    classical, observed = noisy_classical()
    assert lp.evaluate_observed(classical, 0).guaranteed_margin == 0
    result = lp.evaluate_observed(observed, Q(1, 50))
    assert not lp.verify_observed(observed, 0, result)
    # Smaller radii yield larger *conditional* bounds; they do not acquire coverage.
    assert lp.evaluate_observed(observed, Q(1, 100)).guaranteed_margin == Q(1, 100)
    assert lp.evaluate_observed(observed, 1).guaranteed_margin == 0


@pytest.mark.parametrize("field", ["coefficients", "witness", "lp"])
def test_malformed_certificate_fields_are_refused(field):
    _, observed = noisy_classical()
    result = lp.evaluate_observed(observed, Q(1, 50))
    damaged = replace(result.certificate, **{field: None})
    assert not lp.verify_observed(observed, Q(1, 50), replace(result, certificate=damaged))


def test_positive_bound_checked_against_known_compatible_truths():
    observed = bell(k.pr_box())
    result = lp.evaluate_observed(observed, Q(1, 2))
    assert result.guaranteed_margin == Q(3, 2)
    _, columns, e = lp.contextual_matrix(observed)
    classical = bell(k.classical_mixture())
    _, _, c = lp.contextual_matrix(classical)
    covered = 0
    for step in range(21):
        weight = Q(step, 20)
        truth = tuple((1-weight)*x + weight*y for x, y in zip(e, c))
        if sum(abs(a-b) for a, b in zip(e, truth)) <= result.radius:
            optimum = lp.solve_l1(columns, truth)
            assert result.guaranteed_margin <= optimum.defect
            covered += 1
    assert covered > 1


@pytest.mark.parametrize("model,kind", [
    (None, "SHAPE"), (lp.Scenario((2,), ((True,),), ((1, 0),)), "SHAPE"),
    (lp.Scenario((2,), ((0,),), ((1, 1),)), "NOT_A_DISTRIBUTION"),
    (lp.Scenario((2,), ((0,),), ((-1, 2),)), "NOT_A_DISTRIBUTION")])
def test_uncertain_route_preserves_shape_and_probability_validation(model, kind):
    with pytest.raises(lp.Refusal, match=kind):
        lp.evaluate_observed(model, 0)


def test_uncertain_route_keeps_resource_refusals():
    model = bell(k.pr_box())
    for kwargs, kind in (({"max_pivots": 0}, "BUDGET_EXHAUSTED"),
                         ({"max_assignments": 15}, "ENUMERATION_LIMIT"),
                         ({"max_entries": 10}, "SIZE_LIMIT")):
        with pytest.raises(lp.Refusal, match=kind):
            lp.evaluate_observed(model, 0, **kwargs)


def test_preserved_review_and_new_example_replay():
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "tools"))
    from replay_review_corrections import replay
    assert replay(root)["adjusted_margin"] == "0"


def test_full_release_includes_the_four_missing_review_dependencies():
    root = Path(__file__).resolve().parents[2]
    for name in ("docs/source_lineage.json", "docs/solver_provenance.json",
                 "tools/generate_lp_certificates.py", "tools/replay_lean_axiom_census.py",
                 "tools/replay_simplex_implementation.py", "docs/simplex_execution_cases.json",
                 "lean4/vendor/dependencies.tar.gz", "lean4/vendor/manifest.json", "lean4/lakefile.lean"):
        assert (root / name).is_file() and (root / name).stat().st_size > 0
