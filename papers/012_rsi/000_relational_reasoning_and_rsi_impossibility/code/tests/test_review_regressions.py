"""Negative controls from the 2026-10-23 independent review, plus admission mutations."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import eis_verifier as eis
import exact_dual_witness_solver as solver
import higher_cell_async_hypergraph as hyper
import rsi_transition_harness as cli
import single_agent_graph as graph
from simplicial_complex import (HigherCellComplex, build_exact_k_cochain_from_potential,
                                compute_higher_cell_phi1_holonomy)


def annulus():
    complex_k = HigherCellComplex(1, ((0, 1, 4), (0, 3, 4), (1, 2, 5),
                                       (1, 4, 5), (0, 2, 3), (2, 3, 5)))
    cochain = dict.fromkeys(complex_k.required_k_cells(), Q(0))
    for edge in ((0, 1), (1, 2), (3, 4), (4, 5), (0, 4), (1, 5), (2, 3)):
        cochain[edge] = Q(1)
    for edge in ((0, 2), (3, 5)):
        cochain[edge] = Q(-1)
    return complex_k, cochain


def test_closed_nonexact_annulus_has_certified_cost_nine():
    cx, delta = annulus()
    assert compute_higher_cell_phi1_holonomy(cx, delta) == 0
    assert delta[0, 1] + delta[1, 2] - delta[0, 2] == 3
    result = solver.solve_exact_rational_l1_dual_witness(cx, delta)
    assert solver.verify_exact_l1_repair(cx, delta, result)
    assert result.is_certified and not result.is_exact_repair
    assert result.l1_repair_cost == result.dual_objective == 9
    assert build_exact_k_cochain_from_potential(cx, result.primal_potential) == result.repaired_cochain


def test_nonzero_exact_triangle_has_actual_reconstructing_potential():
    cx = HigherCellComplex.standard_simplex(1)
    delta = build_exact_k_cochain_from_potential(cx, {(0,): Q(0), (1,): Q(1), (2,): Q(2)})
    result = solver.solve_exact_rational_l1_dual_witness(cx, delta)
    assert result.is_certified and result.l1_repair_cost == 0
    assert solver.verify_exact_l1_repair(cx, delta, result)
    forged = replace(result, primal_potential=dict.fromkeys(result.primal_potential, Q(0)))
    assert forged.is_certified and not solver.verify_exact_l1_repair(cx, delta, forged)


def test_every_certificate_component_is_replayed():
    cx, delta = annulus()
    good = solver.solve_exact_rational_l1_dual_witness(cx, delta)
    mutations = []
    for field in ('primal_potential', 'repaired_cochain', 'residual', 'dual_witness'):
        values = dict(getattr(good, field))
        values[next(iter(values))] += 1
        mutations.append(replace(good, **{field: values}))
    for field in ('l1_repair_cost', 'dual_objective', 'duality_gap', 'degree'):
        mutations.append(replace(good, **{field: getattr(good, field) + 1}))
    mutations.append(replace(good, is_exact_repair=True))
    mutations.append(replace(good, dual_witness={}))
    for bad in mutations:
        assert not solver.verify_exact_l1_repair(cx, delta, bad)
    # The producer's certification flag is not evidence.
    assert solver.verify_exact_l1_repair(cx, delta, replace(good, is_certified=False))


def repairing_graph(price):
    cx = HigherCellComplex.standard_simplex(1)
    delta = dict.fromkeys(cx.required_k_cells(), Q(0))
    delta[0, 1] = Q(1)
    return hyper.HigherCellAsyncCommunicatingHypergraph(
        (2, 3), cx, 0, (0, 0), 1, delta,
        lambda state: (state.agent_states, delta),
        enable_active_repair=True, repair_budget_cost_fn=lambda _: price)


@pytest.mark.parametrize('price', [-1, False, True, Q(1), 1.0, 0])
def test_invalid_repair_price_cannot_mint_or_bypass_budget(price):
    with pytest.raises(ValueError, match='price'):
        repairing_graph(price).run()


def test_bad_certificate_is_refused_even_when_flag_is_true(monkeypatch):
    cx, delta = annulus()
    forged = solver.solve_exact_rational_l1_dual_witness(cx, delta)
    monkeypatch.setattr(hyper, 'solve_exact_rational_l1_dual_witness', lambda *a: forged)
    with pytest.raises(ValueError, match='certificate rejected'):
        repairing_graph(1).run()


def test_admission_checks_survive_python_optimization():
    program = '''from test_review_regressions import repairing_graph
try:
    repairing_graph(-1).run()
except ValueError:
    print("REFUSED")
else:
    raise RuntimeError("negative price admitted")
'''
    code = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(code), str(code/'tests'))))
    p = subprocess.run([sys.executable, '-O', '-c', program], cwd=code, env=env,
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0 and p.stdout.strip() == 'REFUSED', p.stdout + p.stderr


def base_receipt():
    return graph.FiniteStateSelfModifyingGraph(4, 0).run_trajectory(
        graph.TransitionState(0, 0, 0, 0), lambda state: state)


def test_cli_exports_the_same_implementation_and_policy():
    assert cli.FiniteStateSelfModifyingGraph is graph.FiniteStateSelfModifyingGraph
    assert cli.HigherCellAsyncCommunicatingHypergraph is hyper.HigherCellAsyncCommunicatingHypergraph
    values = []
    for mod in (cli, graph):
        values.append(mod.FiniteStateSelfModifyingGraph(4, 0).run_trajectory(
            mod.TransitionState(0, 0, 0, 0), lambda s: replace(s, report_id=(s.report_id+1)%4,
                internal_eval=s.internal_eval+1, step_index=s.step_index+1)))
    assert values[0] == values[1]
    assert values[0].obstruction_kind == 'CAPACITY_THRESHOLD_EXCEEDED'
    assert values[0].termination_step == 4


def test_adversarial_identities_agree_in_native_companion():
    receipts = []
    for detector, observer, expected in (
        ('ss', 'ß', 'EIS_VALUE_ERROR'), ('Straße', 'STRASSE', 'EIS_VALUE_ERROR'),
        ('σ', 'ς', 'EIS_VALUE_ERROR'), ('İ', 'i̇', 'EIS_VALUE_ERROR'),
        ('regex', 'MODEL\u200b', 'EIS_VALUE_ERROR'), ('regex', 'MODEL\u00a0', 'EIS_VALUE_ERROR'),
        ('REGEX', ' regex ', 'TWO_SIGNAL_COLLAPSE'), ('regex', 'host.safe', 'OK')):
        old = base_receipt()
        vec = deepcopy(old.eis_vector)
        vec['context']['detector_id'] = detector
        vec['danger']['observer_id'] = observer
        verdict = eis.verify_signal_independence(vec['matches'], vec['danger'], vec['context'])
        assert ('OK' if 'ok' in verdict else verdict['error']['code']) == expected
        receipts.append(replace(old, eis_vector=vec, eis_independence_verdict=verdict))
    result = eis.cross_check_eis_metadata_against_rust(receipts)
    assert result['metadata_record_count'] == 8 and result['rust_companion_executed']


def test_forged_obstruction_is_not_claimed_as_verified():
    forged = replace(base_receipt(), obstruction_kind='OVERLAP_GLUING_REFUSAL',
                     phi1_holonomy=Q(0), colliding_prior_step=None)
    result = eis.cross_check_eis_metadata_against_rust([forged])
    assert result['scope'] == 'EIS_METADATA_ONLY'
    assert result['obstruction_predicates_checked'] is False
    assert 'verified_receipt_count' not in result


def test_unsupported_metadata_shape_is_refused():
    old = base_receipt()
    vec = deepcopy(old.eis_vector)
    vec['context']['offsets_are_content'] = False
    verdict = eis.verify_signal_independence(vec['matches'], vec['danger'], vec['context'])
    with pytest.raises(ValueError, match='wire shape'):
        eis.cross_check_eis_metadata_against_rust([replace(old, eis_vector=vec,
                                                          eis_independence_verdict=verdict)])


def test_constant_and_equal_content_controls_expose_fixture_policy():
    cx = HigherCellComplex.standard_simplex(1)
    state = hyper.HigherCellAsyncState(1, (0, 0), (0, 0), (0, 0), (1, 1), 10,
                                      dict.fromkeys(cx.required_k_cells(), Q(0)))
    inject = hyper.make_async_uncompensated_stale_cochain_step_fn((2, 3), cx)
    compensate = hyper.make_async_delay_compensated_step_fn((2, 3), cx)
    assert compute_higher_cell_phi1_holonomy(cx, inject(state)[1]) == Q(1, 6)
    assert compute_higher_cell_phi1_holonomy(cx, inject(replace(state, effective_lags=(0, 0)))[1]) == 0
    assert compute_higher_cell_phi1_holonomy(cx, compensate(state)[1]) == 0
    unequal = replace(state, emitted_projections=(1, 0))
    assert compute_higher_cell_phi1_holonomy(cx, inject(unequal)[1]) == Q(1, 6)


def test_advertised_cli_executes_modular_scenarios():
    run = subprocess.run([sys.executable, '-m', 'rsi_transition_harness', '--json'],
                         cwd=Path(__file__).resolve().parents[1], capture_output=True,
                         text=True, encoding='utf-8', timeout=120)
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)
    assert result['eis_cross_check']['scope'] == 'EIS_METADATA_ONLY'
    assert result['non_monotonic_rewiring_distribution']['experiment_scope'] == 'CONTROLLED_SYNTHETIC_DEFECT_INJECTION'
