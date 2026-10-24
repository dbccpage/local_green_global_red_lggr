"""Exact objectives, independent witness mutations, and resource refusals."""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import random
import json
import importlib.util
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contextuality_lp as lp
import epistemic_kernel as k


def bell(table):
    contexts = ((0, 2), (0, 3), (1, 2), (1, 3))
    return lp.Scenario((2, 2, 2, 2), contexts,
                       tuple(tuple(table[c].get(o, Q(0)) for o in product((0, 1), repeat=2))
                             for c in k.CONTEXTS))


@pytest.mark.parametrize("table,expected,kind", [
    (k.classical_mixture(), Q(0), "GlobalSection"),
    (k.pr_box(), Q(2), "Obstructed"),
    (k.near_tsirelson(), Q(4, 5), "Obstructed"),
])
def test_exact_bell_defects_and_independent_replay(table, expected, kind):
    model = bell(table)
    result = lp.evaluate(model)
    _, columns, target = lp.contextual_matrix(model)
    assert result.kind == kind
    assert result.certificate.defect == expected
    assert lp.verify_defect(columns, target, result.certificate)
    if expected == 0:
        joint = {g: w for g, w in zip(result.assignments, result.certificate.coefficients) if w}
        assert k.marginalises(joint, table)


def test_tiny_positive_defect_never_rounded_to_zero():
    s = Q(1, 2) + Q(1, 100000000)
    table = {ctx: {o: (1 + (s if (o[0] ^ o[1]) == (ctx[0] & ctx[1]) else -s)) / 4
                   for o in product((0, 1), repeat=2)} for ctx in k.CONTEXTS}
    assert lp.evaluate(bell(table)).certificate.defect == Q(1, 25000000)


def test_triangle_odd_parity():
    model = lp.Scenario((2, 2, 2), ((0, 1), (0, 2), (1, 2)),
                        ((Q(0), Q(1, 2), Q(1, 2), Q(0)),) * 3)
    assert lp.evaluate(model).certificate.defect == 2


@pytest.mark.parametrize("generators,target,expected", [
    (((0,), (2,)), (1,), 0),
    (((0,), (2,)), (3,), 1),
    (((0,), (2,)), (-1,), 1),
    (((1, 0), (0, 1)), (2, 2), 3),
    (((1, 1), (1, 1)), (0, 0), 2),
    (((),), (), 0),
])
def test_general_convex_hull_projection(generators, target, expected):
    assert lp.solve_l1(generators, target).defect == expected


def test_random_one_dimensional_hulls_have_closed_form():
    rng = random.Random(20261021)
    for _ in range(60):
        vertices = [Q(rng.randrange(-9, 10), rng.randrange(1, 6)) for _ in range(5)]
        target = Q(rng.randrange(-12, 13), rng.randrange(1, 6))
        expected = max(Q(0), min(vertices) - target, target - max(vertices))
        cert = lp.solve_l1(tuple((v,) for v in vertices), (target,))
        assert cert.defect == expected


@pytest.mark.parametrize("field", ["coefficients", "residual", "witness", "offset", "defect", "lp_primal", "lp_dual", "lp_value"])
def test_each_certificate_component_is_bound(field):
    _, columns, target = lp.contextual_matrix(bell(k.pr_box()))
    cert = lp.solve_l1(columns, target)
    if field.startswith("lp_"):
        inner = field[3:]
        old = getattr(cert.lp, inner)
        changed = old + 1 if inner == "value" else (old[0] + 1,) + old[1:]
        mutated = replace(cert, lp=replace(cert.lp, **{inner: changed}))
    else:
        old = getattr(cert, field)
        changed = old + 1 if field in {"offset", "defect"} else (old[0] + 1,) + old[1:]
        mutated = replace(cert, **{field: changed})
    assert not lp.verify_defect(columns, target, mutated)


def test_pivot_trace_is_not_part_of_mathematical_certificate():
    cert = lp.solve_l1(((0,), (2,)), (3,))
    assert lp.verify_defect(((0,), (2,)), (3,), replace(cert, lp=replace(cert.lp, pivots=99999)))


@pytest.mark.parametrize("kwargs,kind", [
    ({"max_pivots": 0}, "BUDGET_EXHAUSTED"),
    ({"max_pivots": -1}, "INVALID_BUDGET"),
    ({"max_assignments": 15}, "ENUMERATION_LIMIT"),
    ({"max_entries": 10}, "SIZE_LIMIT"),
])
def test_budget_and_size_refusals_are_not_verdicts(kwargs, kind):
    with pytest.raises(lp.Refusal) as exc:
        lp.evaluate(bell(k.pr_box()), **kwargs)
    assert exc.value.kind == kind


@pytest.mark.parametrize("bad", [0.5, "1/2", True])
def test_inexact_or_untyped_values_refused(bad):
    with pytest.raises(lp.Refusal, match="NONEXACT_INPUT"):
        lp.solve_l1(((0,), (2,)), (bad,))


def test_signalling_refused_before_solver():
    model = bell(k.classical_mixture())
    tables = list(model.tables)
    tables[0] = (Q(1), Q(0), Q(0), Q(0))
    with pytest.raises(lp.Refusal, match="SIGNALLING"):
        lp.evaluate(replace(model, tables=tuple(tables)))


@pytest.mark.parametrize("model,kind", [
    (lp.Scenario((2,), ((0,),), ((Q(-1), Q(2)),)), "NOT_A_DISTRIBUTION"),
    (lp.Scenario((2,), ((0,),), ((Q(1), Q(1)),)), "NOT_A_DISTRIBUTION"),
    (lp.Scenario((2,), ((0,),), ((Q(1),),)), "SHAPE"),
    (lp.Scenario((2, 2), ((0,),), ((Q(1), Q(0)),)), "UNCOVERED_MEASUREMENT"),
    (lp.Scenario((0,), ((0,),), ((),)), "SHAPE"),
])
def test_invalid_models_are_refused(model, kind):
    with pytest.raises(lp.Refusal) as exc:
        lp.evaluate(model)
    assert exc.value.kind == kind


@pytest.mark.parametrize("model", [
    None,
    lp.Scenario((2, 2), ((0, "1"),), ((1,),)),
    lp.Scenario((2,), (None,), ((1, 0),)),
    lp.Scenario((2,), ((0,),), (None,)),
    lp.Scenario(None, ((0,),), ((1, 0),)),
    lp.Scenario((2,), ((True,),), ((1, 0),)),
    lp.Scenario((2,), (([0],),), ((1, 0),)),
    lp.Scenario((2,), ((0,), [0]), ((1, 0), (1, 0))),
])
def test_context_validation_precedes_sorting_and_hashing(model):
    with pytest.raises(lp.Refusal, match="SHAPE"):
        lp.evaluate(model)


def test_list_contexts_are_canonicalized():
    assert lp.evaluate(lp.Scenario([2], [[0]], [[1, 0]])).kind == "GlobalSection"


@pytest.mark.parametrize("costs,matrix,rhs,kind", [
    ((1,), ((1,), (1,)), (0, 1), "INFEASIBLE"),
    ((-1,), (), (), "UNBOUNDED"),
    ((1,), ((1, 0),), (0,), "SHAPE"),
])
def test_general_lp_refusals(costs, matrix, rhs, kind):
    with pytest.raises(lp.Refusal) as exc:
        lp.solve_standard(costs, matrix, rhs)
    assert exc.value.kind == kind


def test_redundant_rows_and_negative_rhs():
    cert = lp.solve_standard((1, 2), ((-1, -1), (-2, -2)), (-1, -2))
    assert cert.value == 1 and cert.primal == (Q(1), Q(0))


def test_dual_offset_is_tight_at_some_generator():
    cert = lp.evaluate(bell(k.near_tsirelson())).certificate
    _, columns, target = lp.contextual_matrix(bell(k.near_tsirelson()))
    assert max(lp.dot(g, cert.witness) for g in columns) == -cert.offset
    assert lp.dot(target, cert.witness) - max(lp.dot(g, cert.witness) for g in columns) == cert.defect


def test_deposited_solver_outputs_and_lean_data_are_current():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('lp_fixture_generator', root / 'tools/generate_lp_certificates.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, text in module.generate().items():
        assert (root / name).read_text(encoding='utf-8') == text


def test_ported_rust_source_copies_match_recorded_bytes():
    import hashlib
    root = Path(__file__).resolve().parents[2]
    record = json.loads((root / 'docs/solver_provenance.json').read_text(encoding='utf-8'))
    for source in record['adapted_from'].values():
        assert hashlib.sha256((root / source['deposited_copy']).read_bytes()).hexdigest() == source['sha256']


def test_axiom_parser_handles_wrapped_lists_and_refuses_hidden_custom_axiom():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('lp_named_census', root / 'tools/replay_lean_axiom_census.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = "'Example.long_declaration' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]"
    assert module.rows(text) == [('Example.long_declaration', frozenset({'propext', 'Classical.choice', 'Quot.sound'}))]
    with pytest.raises(ValueError, match='Unapproved axiom'):
        module.rows(text.replace('Quot.sound', 'sorryAx'))
