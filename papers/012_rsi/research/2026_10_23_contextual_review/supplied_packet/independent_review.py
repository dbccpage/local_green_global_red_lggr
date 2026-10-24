"""Independent review probes; no modifications to the reviewed source tree.

Usage: python independent_review.py SOURCE_DIRECTORY OUTPUT_JSON
SciPy is a numerical cross-check, not a proof oracle. Certificate checks below
use exact Fraction arithmetic independently of the package's checker functions.
The census subprocess is mocked only to isolate its Python file-write behavior.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from unittest.mock import patch
from types import SimpleNamespace
import hashlib
import json
import random
import shutil
import sys
import tempfile

ROOT = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(ROOT / 'code'), str(ROOT / 'tools')]
import contextuality_lp as lp
import replay_full_axiom_census as census
import rebuild_release as release
from scipy.optimize import linprog

def dot(a, b):
    assert len(a) == len(b)
    return sum((Q(x) * Q(y) for x, y in zip(a, b)), Q(0))

def independently_check(c, A, b, cert, kind):
    n, m = len(c), len(b)
    if kind == 'infeasible':
        assert len(cert.dual) == m
        assert all(sum((Q(A[i][j])*cert.dual[i] for i in range(m)), Q(0)) >= 0 for j in range(n))
        assert dot(b, cert.dual) < 0
    elif kind == 'unbounded':
        assert len(cert.primal) == len(cert.direction) == n
        assert all(x >= 0 for x in cert.primal + cert.direction)
        assert all(dot(row, cert.primal) == v and dot(row, cert.direction) == 0 for row, v in zip(A, b))
        assert dot(c, cert.direction) < 0
    else:
        assert len(cert.primal) == n and len(cert.dual) == m
        assert all(x >= 0 for x in cert.primal)
        assert all(dot(row, cert.primal) == v for row, v in zip(A, b))
        assert all(sum((Q(A[i][j])*cert.dual[i] for i in range(m)), Q(0)) <= c[j] for j in range(n))
        assert dot(c, cert.primal) == dot(b, cert.dual) == cert.value

def fuzz():
    rng = random.Random(20261023)
    counts = Counter()
    mismatches = []
    for trial in range(1000):
        n, m = rng.randrange(1, 7), rng.randrange(0, 6)
        c = [rng.randrange(-5, 6) for _ in range(n)]
        A = [[rng.randrange(-4, 5) for _ in range(n)] for _ in range(m)]
        witness = [rng.randrange(0, 5) for _ in range(n)]
        b = [sum(x*y for x, y in zip(row, witness)) for row in A] if trial % 2 else [rng.randrange(-8, 9) for _ in range(m)]
        try:
            cert = lp.solve_standard(c, A, b, max_pivots=1000)
            kind = 'optimal'
        except lp.CertifiedInfeasible as exc:
            cert, kind = exc.certificate, 'infeasible'
        except lp.CertifiedUnbounded as exc:
            cert, kind = exc.certificate, 'unbounded'
        except lp.Refusal as exc:
            mismatches.append({'trial': trial, 'refusal': exc.kind, 'c': c, 'A': A, 'b': b})
            continue
        independently_check(c, A, b, cert, kind)
        numeric = linprog(c, A_eq=A if m else None, b_eq=b if m else None, bounds=(0, None), method='highs', options={'presolve': False})
        numeric_kind = {0: 'optimal', 2: 'infeasible', 3: 'unbounded'}.get(numeric.status, 'numeric_unresolved')
        counts[kind] += 1
        if numeric_kind != kind or (kind == 'optimal' and abs(float(cert.value) - numeric.fun) > 1e-7 * max(1, abs(numeric.fun))):
            mismatches.append({'trial': trial, 'exact_kind': kind, 'numeric_kind': numeric_kind, 'numeric_message': numeric.message, 'c': c, 'A': A, 'b': b})
    return {'seed': 20261023, 'cases': 1000, 'outcomes': dict(counts), 'mismatches': mismatches}

def optimal_checker_boundary():
    c, A, b = [1], [[1]], [1]
    cert = lp.solve_standard(c, A, b)
    result = {'certificate_value': str(cert.value), 'integer_replay': lp.verify_standard(c, A, b, cert),
              'fraction_replay': lp.verify_standard([Q(1)], [[Q(1)]], [Q(1)], cert)}
    try:
        result['none_certificate'] = lp.verify_standard([Q(1)], [[Q(1)]], [Q(1)], None)
    except Exception as exc:
        result['none_certificate_exception'] = type(exc).__name__ + ': ' + str(exc)
    return result

def census_write_probe():
    # Do not invoke Lean or claim that the mocked transcript verifies any proof.
    with tempfile.TemporaryDirectory(prefix='census-review-') as directory:
        root = Path(directory)
        lean = root / 'lean4'
        lean.mkdir()
        for p in (ROOT / 'lean4').glob('*.lean'):
            shutil.copy2(p, lean / p.name)
        shutil.copy2(ROOT / 'lean4/full_axiom_report.txt', lean / 'full_axiom_report.txt')
        path = lean / 'FullCensus.lean'
        before = path.read_bytes()
        stored = (lean / 'full_axiom_report.txt').read_text()
        output = '\n'.join(line for line in stored.splitlines() if line.startswith("'")) + '\n'
        with patch.object(census.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=output, stderr='')):
            exit_code = census.replay(root, check=True)
        after = path.read_bytes()
        return {'isolated_python_orchestration_only': True, 'lean_subprocess_mocked': True,
                'exit_code': exit_code, 'changed': before != after,
                'before_bytes': len(before), 'after_bytes': len(after),
                'before_sha256': hashlib.sha256(before).hexdigest(),
                'after_sha256': hashlib.sha256(after).hexdigest(),
                'difference_is_only_CRLF_to_LF': before.replace(b'\r\n', b'\n') == after}

def later_date_release_probe():
    with tempfile.TemporaryDirectory(prefix='release-date-review-') as directory:
        root = Path(directory) / 'paper'
        root.mkdir()
        data = b'{"publication_date":"2026-10-21"}\n'
        (root / 'zenodo_metadata.json').write_bytes(data)
        (root / 'MANIFEST.sha256').write_text(hashlib.sha256(data).hexdigest() + '  zenodo_metadata.json\n')
        release.refresh(root)
        return {'fixture_metadata_date': '2026-10-21',
                'produced_archive': [p.name for p in root.glob('*.zip')],
                'errors': release.validate(root)}

if __name__ == '__main__':
    report = {'source_commit': 'e15a9d4ac6298524ce370cae679314aa0fef7585',
              'fresh_lean_build': False, 'fuzz': fuzz(),
              'optimal_checker_boundary': optimal_checker_boundary(),
              'census_write_probe': census_write_probe(),
              'later_date_release_probe': later_date_release_probe()}
    Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
