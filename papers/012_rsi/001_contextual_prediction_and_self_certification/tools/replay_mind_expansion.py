"""Replay source-pinned illustrative examples; no empirical cognition claims.

The supplied script includes floating finite differences and exponentials.
Those are illustrations, not the exact LP rail or Lean premises. This replay
uses only the standard-library branch and does not overwrite the source report.
"""
import argparse
import builtins
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def generate():
    inventory = json.loads((ROOT / 'docs/mind_expansion_sources.json').read_text(encoding='utf-8'))
    for path, digest in inventory['files_sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError('MIND_SOURCE_CHANGED: ' + path)
    source = ROOT / 'docs/source_inputs/mind_expansion/mind_extension_tests.py'
    namespace = runpy.run_path(str(source), run_name='preserved_mind_illustrations')
    original_import = builtins.__import__
    def standard_only(name, *args, **kwargs):
        if name.split('.')[0] in {'numpy', 'sympy'}:
            raise ImportError('optional checks deliberately outside this replay')
        return original_import(name, *args, **kwargs)
    try:
        builtins.__import__ = standard_only
        result = namespace['run']()
    finally:
        builtins.__import__ = original_import
    if (result['status'], result['test_groups'], result['assertions_passed']) != ('passed', 6, 19):
        raise ValueError('Unexpected source illustration scope')
    return {'schema': 'contextuality.mind-expansion-replay.v1',
            'scope': 'Six constructed groups, 19 assertions; mixed exact and floating illustrations. '
                     'No optional NumPy/SymPy, human/LLM experiment, or consciousness measure.',
            'source_sha256': inventory['files_sha256'], 'result': result}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    rendered = json.dumps(generate(), indent=2) + '\n'
    target = ROOT / 'docs/mind_expansion_replay.json'
    if args.write:
        target.write_text(rendered, encoding='utf-8')
    elif target.read_text(encoding='utf-8') != rendered:
        raise SystemExit('FAIL: mind expansion replay drift')
    print('PASS: six source-pinned illustration groups, 19 assertions (standard library only)')
