"""Public checker contracts and sealed-release regression probes.

Census subprocesses here are mocks for orchestration, not Lean proof evidence.
The standalone deposit verifier separately performs actual Lean replay.
"""
from dataclasses import replace
from fractions import Fraction as Q
import datetime
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'code'))
import contextuality_lp as lp


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('costs,matrix,rhs', [
    ([1], [[1]], [1]),
    ([Q(1)], [[Q(1)]], [Q(1)]),
    ((1, Q(2)), [[Q(-1), -1]], [-1]),
    ([], [], []),
    ([], [[], []], [0, Q(0)]),
    ([1], [], []),
])
def test_original_inputs_replay_optimal_certificate(costs, matrix, rhs):
    cert = lp.solve_standard(costs, matrix, rhs)
    assert lp.verify_standard(costs, matrix, rhs, cert)


@pytest.mark.parametrize('change', [
    None, {}, {'primal': None}, {'dual': [Q(1)]}, {'primal': ()},
    {'primal': (1,)}, {'primal': (True,)}, {'primal': (1.0,)},
    {'value': 1}, {'value': True}, {'pivots': -1}, {'pivots': True},
    {'dual': (Q(2),)}, {'primal': (Q(2),)}, {'value': Q(2)},
])
def test_optimal_checker_rejects_malformed_or_false_witness(change):
    cert = lp.solve_standard([1], [[1]], [1])
    bad = replace(cert, **change) if change else change
    assert lp.verify_standard([1], [[1]], [1], bad) is False


@pytest.mark.parametrize('costs,matrix,rhs', [
    (None, [[1]], [1]), ([1], [None], [1]), ([1], [[1, 2]], [1]),
    ([1], [[1]], []), ([True], [[1]], [1]), ([1.0], [[1]], [1]),
    ([1], [[1]], ['1']), ([1], [[True]], [1]),
])
def test_optimal_checker_rejects_malformed_problem_without_raising(costs, matrix, rhs):
    cert = lp.solve_standard([1], [[1]], [1])
    assert lp.verify_standard(costs, matrix, rhs, cert) is False


@pytest.mark.parametrize('change', [None, {'lp': None}, {'coefficients': None}, {'defect': 1}])
def test_defect_checker_rejects_malformed_outer_and_nested_certificates(change):
    cert = lp.solve_l1(((0,), (2,)), (3,))
    bad = replace(cert, **change) if change else None
    assert lp.verify_defect(((0,), (2,)), (3,), bad) is False


@pytest.mark.parametrize('generators,target', [(None, [1]), ([None], [1]), ([[0]], None)])
def test_defect_checker_rejects_malformed_problem(generators, target):
    cert = lp.solve_l1(((0,),), (1,))
    assert lp.verify_defect(generators, target, cert) is False


def census_fixture(tmp_path, monkeypatch):
    module = load('review_full_census', 'tools/replay_full_axiom_census.py')
    lean = tmp_path / 'lean4'
    lean.mkdir()
    (lean / 'Example.lean').write_text('theorem example : True := True.intro\n')
    output = "'example' does not depend on any axioms\n"
    monkeypatch.setattr(module.subprocess, 'run', lambda *a, **kw: SimpleNamespace(
        returncode=0, stdout=output, stderr=''))
    module.replay(tmp_path, check=False)
    return module, lean


@pytest.mark.parametrize('ending', [b'\n', b'\r\n'])
@pytest.mark.parametrize('failure', [False, True])
def test_census_check_never_writes_sealed_source_or_report(tmp_path, monkeypatch, ending, failure):
    module, lean = census_fixture(tmp_path, monkeypatch)
    for path in (lean / 'FullCensus.lean', lean / 'full_axiom_report.txt'):
        path.write_bytes(path.read_text().replace('\n', ending.decode()).encode())
    before = {p.name: p.read_bytes() for p in lean.iterdir()}
    def forbidden(*a, **kw):
        pytest.fail('Check mode attempted a file write')
    monkeypatch.setattr(Path, 'write_text', forbidden)
    monkeypatch.setattr(Path, 'write_bytes', forbidden)
    if failure:
        monkeypatch.setattr(module.subprocess, 'run', lambda *a, **kw: SimpleNamespace(
            returncode=1, stdout='', stderr='deliberate Lean failure'))
        with pytest.raises(ValueError, match='deliberate Lean failure'):
            module.replay(tmp_path)
    else:
        assert module.replay(tmp_path) == 0
    assert {p.name: p.read_bytes() for p in lean.iterdir()} == before


def test_stale_census_is_refused_before_subprocess(tmp_path, monkeypatch):
    module, lean = census_fixture(tmp_path, monkeypatch)
    (lean / 'FullCensus.lean').write_bytes(b'-- stale\r\n')
    def forbidden(*a, **kw):
        pytest.fail('Stale census was compiled')
    monkeypatch.setattr(module.subprocess, 'run', forbidden)
    with pytest.raises(ValueError, match='--write'):
        module.replay(tmp_path)
    assert (lean / 'FullCensus.lean').read_bytes() == b'-- stale\r\n'


def release_fixture(tmp_path):
    module = load('review_rebuild', 'tools/rebuild_release.py')
    package = tmp_path / 'paper'
    package.mkdir()
    (package / 'zenodo_metadata.json').write_text(json.dumps({'publication_date': '2026-10-21'}))
    (package / 'CITATION.cff').write_text('date-released: 2026-10-21\n')
    (package / 'payload.txt').write_bytes(b'sealed content\r\n')
    entries = [(p.name, module.sha256_file(p)) for p in package.iterdir()]
    (package / 'MANIFEST.sha256').write_bytes(module.render(sorted(entries)))
    module.refresh(package)
    assert module.validate(package) == []
    return module, package


def envelope(package):
    return {p.name: p.read_bytes() for p in package.iterdir()
            if p.name in {'SHA256SUMS', 'MANIFEST.sha256'} or p.suffix == '.zip'}


def test_later_clock_reproduces_pinned_release_bytes(tmp_path, monkeypatch):
    module, package = release_fixture(tmp_path)
    before = envelope(package)
    class LaterDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2031, 4, 9)
    monkeypatch.setattr(module.datetime, 'date', LaterDate)
    module.refresh(package)
    assert module.validate(package) == []
    assert envelope(package) == before


@pytest.mark.parametrize('failure', ['build', 'validation', 'promotion'])
def test_failed_replacement_preserves_previous_envelope(tmp_path, monkeypatch, failure):
    module, package = release_fixture(tmp_path)
    before = envelope(package)
    (package / 'payload.txt').write_bytes(b'intended replacement')
    if failure == 'build':
        def fail(*a, **kw):
            raise ValueError('deliberate build failure')
        monkeypatch.setattr(module, 'build_archive', fail)
    elif failure == 'validation':
        monkeypatch.setattr(module, 'validate', lambda p: ['deliberate staged validation failure'])
    else:
        original = Path.replace
        def fail(source, target):
            if (Path(target).parent == package and source.suffix == '.zip'
                    and source.name == Path(target).name and source.parent != package):
                assert (package / 'MANIFEST.sha256').read_bytes() != before['MANIFEST.sha256']
                assert (package / 'SHA256SUMS').read_bytes() != before['SHA256SUMS']
                raise OSError('deliberate promotion failure')
            return original(source, target)
        monkeypatch.setattr(Path, 'replace', fail)
    with pytest.raises((ValueError, OSError), match='deliberate'):
        module.refresh(package)
    assert envelope(package) == before


def test_new_release_requires_explicit_mode_and_consistent_dates(tmp_path):
    module, package = release_fixture(tmp_path)
    before = envelope(package)
    (package / 'zenodo_metadata.json').write_text(json.dumps({'publication_date': '2026-10-23'}))
    with pytest.raises(ValueError, match='--new-release'):
        module.refresh(package)
    with pytest.raises(ValueError, match='CITATION.cff'):
        module.refresh(package, new_release=True)
    assert envelope(package) == before
    (package / 'CITATION.cff').write_text('date-released: 2026-10-23\n')
    module.refresh(package, new_release=True)
    assert module.validate(package) == []
    assert sorted(p.name for p in package.glob('*.zip')) == ['paper_2026-10-23.zip']


def test_version_change_on_same_date_requires_new_release(tmp_path):
    module, package = release_fixture(tmp_path)
    before = envelope(package)
    (package / 'zenodo_metadata.json').write_text(json.dumps({
        'publication_date': '2026-10-21', 'version': '2.0.0'}))
    with pytest.raises(ValueError, match='--new-release'):
        module.refresh(package)
    assert envelope(package) == before
    module.refresh(package, new_release=True)
    assert module.validate(package) == []


def test_final_seal_check_uses_original_manifest_even_if_rewritten(tmp_path, monkeypatch):
    module = load('review_deposit', 'verify_deposit.py')
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    payload = tmp_path / 'FullCensus.lean'
    payload.write_bytes(b'import Example\r\n')
    manifest = tmp_path / 'SHA256SUMS'
    manifest.write_text(f'{module.sha256_of(payload)}  FullCensus.lean\n')
    original = module.sealed_snapshot(manifest)
    assert module.check_seal_unchanged(original) == []
    payload.write_bytes(b'import Example\n')
    manifest.write_text(f'{module.sha256_of(payload)}  FullCensus.lean\n')
    errors = module.check_seal_unchanged(original)
    assert len(errors) == 2
    assert any('FullCensus.lean' in error for error in errors)
    assert any('SHA256SUMS' in error for error in errors)
