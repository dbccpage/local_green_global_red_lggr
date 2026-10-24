import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('rsi_census', ROOT/'tools/replay_lean_axiom_census.py')
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)


def source_root(tmp_path, source):
    (tmp_path/'lean4').mkdir()
    (tmp_path/'lean4/Example.lean').write_text(source, encoding='utf-8')
    return tmp_path


def test_typed_constructor_is_not_a_proof_placeholder(tmp_path):
    source = 'namespace Example\ninductive Op (Mark : Type) where\n  | admit (m : Mark)\ntheorem ok : True := True.intro\nend Example\n'
    assert census.theorem_names(source_root(tmp_path, source)) == ['Example.ok']


@pytest.mark.parametrize('bad', [
    'theorem bad : False := by admit',
    'theorem bad : False := by sorry',
    'axiom unsupported : False',
    'theorem bad (b : Bool) : False := by\n  cases b with\n  | false => admit\n  | true => admit',
    'theorem bad : False := by\n  first\n  | admit\n  | trivial',
    'def bad : False := by admit',
])
def test_proof_holes_and_custom_axioms_still_refuse(tmp_path, bad):
    source = 'namespace Example\ninductive Op (Mark : Type) where\n  | admit (m : Mark)\n'+bad+'\nend Example\n'
    with pytest.raises(ValueError, match='Unfinished proof or custom axiom'):
        census.theorem_names(source_root(tmp_path, source))
