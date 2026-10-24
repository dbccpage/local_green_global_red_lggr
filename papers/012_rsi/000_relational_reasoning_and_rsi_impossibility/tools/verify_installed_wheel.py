#!/usr/bin/env python3
"""Build and smoke-test an installed wheel outside the source tree.

Needs Python 3.10+, pip, rustc on PATH, and a package index for isolated build
dependencies (or --wheelhouse containing setuptools/wheel and NumPy/SciPy).
No system site packages or checkout PYTHONPATH are inherited by the test.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import venv
import zipfile


SMOKE = r'''
import importlib, importlib.metadata as md, json
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys
names = ["communication_channels", "deposit_paths", "eis_verifier", "exact_dual_witness_solver",
         "finite_limits", "higher_cell_async_hypergraph", "memory_cli", "memory_machine",
         "multi_agent_hypergraph", "residual_memory", "rsi_transition_harness",
         "simplicial_complex", "simplicial_rewiring", "single_agent_graph", "rsi_eis_resources"]
for name in names:
    module = importlib.import_module(name)
    if not Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError("Module escaped installed environment: " + name)
import eis_verifier as eis
import single_agent_graph as g
import exact_dual_witness_solver as solver
from simplicial_complex import HigherCellComplex
cx = HigherCellComplex(1, ((0,1,4),(0,3,4),(1,2,5),(1,4,5),(0,2,3),(2,3,5)))
delta = dict.fromkeys(cx.required_k_cells(), Q(0))
for e in ((0,1),(1,2),(3,4),(4,5),(0,4),(1,5),(2,3)): delta[e]=Q(1)
for e in ((0,2),(3,5)): delta[e]=Q(-1)
certificate=solver.solve_exact_rational_l1_dual_witness(cx,delta)
if certificate.l1_repair_cost != 9 or not solver.verify_exact_l1_repair(cx,delta,certificate):
    raise RuntimeError("Installed solver failed the closed nonexact control")
receipt=g.FiniteStateSelfModifyingGraph(4,0).run_trajectory(g.TransitionState(0,0,0,0),lambda s:s)
parity=eis.cross_check_eis_metadata_against_rust([receipt])
print(json.dumps({"installed_modules": len(names), "parity": parity,
                  "versions": {n: md.version(n) for n in ("numpy","scipy","relational-reasoning-and-rsi-impossibility")}}, indent=2))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheelhouse', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env['PYTHONNOUSERSITE'] = '1'
    with tempfile.TemporaryDirectory(prefix='rsi_wheel_') as folder:
        tmp = Path(folder)
        def run(command, echo=True):
            p = subprocess.run(command, cwd=tmp, env=env, capture_output=True,
                               text=True, encoding='utf-8', timeout=300)
            if echo:
                print(p.stdout, end='')
            if p.returncode:
                raise RuntimeError(p.stdout + p.stderr)
            return p.stdout
        wheels = tmp/'wheels'
        build = [sys.executable, '-m', 'pip', 'wheel', str(root), '--no-deps', '-w', str(wheels)]
        if args.wheelhouse:
            build += ['--no-index', '--find-links', str(args.wheelhouse.resolve())]
        run(build)
        wheel, = wheels.glob('*.whl')
        payload_hashes = {}
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                if '.dist-info/' in name:
                    continue
                source = root/'code'/name
                data = archive.read(name)
                if not source.is_file() or data != source.read_bytes():
                    raise RuntimeError('Wheel contains missing or stale source: ' + name)
                payload_hashes[name] = hashlib.sha256(data).hexdigest()
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(tmp/'env')
        python = tmp/'env'/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        install = [str(python), '-I', '-m', 'pip', 'install', '--disable-pip-version-check']
        if args.wheelhouse:
            install += ['--no-index', '--find-links', str(args.wheelhouse.resolve())]
        run(install+[str(wheel)])
        smoke = json.loads(run([str(python), '-I', '-c', SMOKE]))
        cli = json.loads(run([str(python), '-I', '-m', 'rsi_transition_harness', '--json'], echo=False))
        if cli['eis_cross_check']['scope'] != 'EIS_METADATA_ONLY':
            raise RuntimeError('CLI metadata scope missing')
        report = {'status': 'PASS', 'wheel_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
                  'wheel_name': wheel.name, 'isolated_interpreter': True,
                  'system_site_packages': False, 'smoke': smoke, 'cli_executed': True,
                  'wheel_payload_sha256': payload_hashes}
        if args.output:
            args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
