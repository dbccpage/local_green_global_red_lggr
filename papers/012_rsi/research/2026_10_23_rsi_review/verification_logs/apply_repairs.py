from pathlib import Path
import ast, hashlib, json, shutil

root = Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\000_relational_reasoning_and_rsi_impossibility')
work = Path(__file__).parent
packet = Path(r'C:\Users\a343o\Downloads\rsi_review_2026-10-23')
evidence = root.parent / 'research' / '2026_10_23_rsi_review'
evidence.mkdir(exist_ok=True)
shutil.copytree(packet, evidence / 'supplied_packet', dirs_exist_ok=True)
shutil.copy2(Path(r'C:\Users\a343o\.codex\attachments\f16d4309-db64-41ed-9ed9-e5d526c832ef\Pasted text.txt'), evidence / 'pasted_review.txt')
for p in work.glob('baseline_review.*'):
    shutil.copy2(p, evidence / p.name)
before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in root.rglob('*') if p.is_file() and '.lake' not in p.parts and '__pycache__' not in p.parts}
(evidence / 'before_hashes.json').write_text(json.dumps(before, indent=2)+'\n')
archive = next(root.glob('*.zip'))
shutil.copy2(archive, work / ('v1.2.2_' + archive.name))

def edit(name, f):
    p = root / name
    old = p.read_text(encoding='utf-8')
    backup = work / 'before' / name
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(old, encoding='utf-8')
    p.write_text(f(old), encoding='utf-8', newline='\n')

# One tested implementation, including all old public symbols.
modules = ['single_agent_graph', 'multi_agent_hypergraph', 'simplicial_complex',
           'communication_channels', 'simplicial_rewiring', 'higher_cell_async_hypergraph', 'eis_verifier']
imports = []
for module in modules:
    tree = ast.parse((root/'code'/f'{module}.py').read_text(encoding='utf-8'))
    names = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith('_')]
    imports.append(f'from {module} import (\n    '+',\n    '.join(names)+'\n)\n')
def facade(old):
    main = old[old.index('def main('):]
    main = main.replace('cross_check_receipts_against_rust_eis(', 'cross_check_eis_metadata_against_rust(')
    main = main.replace('f"[OK] Verified {len(all_receipts)} core receipts + ', 'f"[OK] Metadata parity for {len(all_receipts)} core records + ')
    main = main.replace('against Rust EIS companion ', 'under the synthetic fixture policy; Rust EIS metadata companion ')
    return ('"""Compatibility exports and CLI for the modular finite-report experiments.\n\n'
            'The Rust companion checks EIS metadata and digests, not obstruction truth.\n"""\n'
            'from __future__ import annotations\nimport argparse\nimport json\nfrom fractions import Fraction\n\n'
            + '\n'.join(imports) + '\n\n' + main)
edit('code/rsi_transition_harness.py', facade)

def solver(s):
    s = s.replace('from dataclasses import dataclass', 'from dataclasses import dataclass, replace')
    s = s.replace('from simplicial_complex import HigherCellComplex, compute_higher_cell_phi1_holonomy',
                  'from simplicial_complex import (HigherCellComplex, compute_higher_cell_phi1_holonomy,\n                                build_exact_k_cochain_from_potential)')
    start = s.index('    # Check if k_cochain is already')
    end = s.index('    # Formulate Primal LP:', start)
    s = s[:start] + ('    # Closedness does not imply exactness: always reconstruct a potential.\n'
                    '    if set(k_cochain) != set(k_cells):\n'
                    '        raise ValueError("Cochain must cover exactly the declared k-cells")\n'
                    '    if any(type(v) not in (int, Fraction) for v in k_cochain.values()):\n'
                    '        raise ValueError("Cochain coefficients must be exact integers or Fractions")\n'
                    '    if type(max_denominator) is not int or max_denominator < 1:\n'
                    '        raise ValueError("max_denominator must be a positive integer")\n\n') + s[end:]
    start = s.index('    # Verify that repaired cochain')
    end = s.index('    return ExactL1DualWitnessRepairResult(', start)
    s = s[:start] + s[end:].replace('    return ExactL1DualWitnessRepairResult(', '    candidate = ExactL1DualWitnessRepairResult(', 1)
    s = s.replace('is_certified=is_certified,', 'is_certified=False,')
    s += ('\n    return replace(candidate, is_certified=verify_exact_l1_repair(\n'
          '        complex_k, k_cochain, candidate))\n')
    return s
edit('code/exact_dual_witness_solver.py', solver)

# Canonical package resources, included in wheels and sdists.
res = root / 'code' / 'rsi_eis_resources'
res.mkdir(exist_ok=True)
(res/'__init__.py').write_text('"""Versioned inputs for the standalone ASCII-identity metadata checker."""\n')
shutil.move(root/'code/rust_eis_companion.rs', res/'rust_eis_companion.rs')
shutil.move(root/'code/eis_independence_vectors_v1.json', evidence/'eis_independence_vectors_v1.json')
data = json.loads((evidence/'eis_independence_vectors_v1.json').read_text())
allowed = lambda s: all(c.isascii() and (c.isalnum() or c in ' ._:-') for c in s)
invalid = {'error': {'code':'EIS_VALUE_ERROR','message':'EIS_VALUE_ERROR: identities must use ASCII letters, digits, spaces, dot, underscore, colon or hyphen'}}
for row in data['vectors']:
    x=row['input']; danger=x['danger']
    if danger is not None and x['detector_id'].strip() and danger['observer_id'].strip():
        if not allowed(x['detector_id']) or not allowed(danger['observer_id']): row['expected']=invalid
data['identity_contract']='ascii-identifiers-v2; not the upstream Unicode-casefold policy'
(res/'eis_independence_vectors_v2.json').write_text(json.dumps(data, ensure_ascii=True, indent=2)+'\n')

def eis(s):
    s = s.replace('from collections.abc import Sequence', 'from collections.abc import Sequence\nfrom importlib.resources import files, as_file')
    s = s.replace('    folded = _trim_python(observer).casefold()',
        '    if any(not ch.isascii() or not (ch.isalnum() or ch in " ._:-")\n'
        '           for identity in (observer, detector_id) for ch in identity):\n'
        '        return {"error": {"code": "EIS_VALUE_ERROR", "message":\n'
        '            "EIS_VALUE_ERROR: identities must use ASCII letters, digits, spaces, dot, underscore, colon or hyphen"}}\n\n'
        '    folded = _trim_python(observer).lower()')
    s = s.replace('_trim_python(detector_id).casefold()', '_trim_python(detector_id).lower()')
    s = s.replace('fixture_path = Path(__file__).resolve().parent / "eis_independence_vectors_v1.json"',
                  'fixture_path = files("rsi_eis_resources").joinpath("eis_independence_vectors_v2.json")')
    s = s.replace('def cross_check_receipts_against_rust_eis(', 'def cross_check_eis_metadata_against_rust(')
    a=s.index('    """Cross-check emitted single-agent')
    b=s.index('    fixture_stats =', a)
    s=s[:a]+'''    """Replay ASCII-identity metadata, digest and reported horizon arithmetic.

    This does not authenticate the host or validate an obstruction, trajectory,
    budget or cochain. The wire format supports one match, one span, at most one
    predicate and content offsets; unsupported inputs are refused explicitly.
    The 55 bundled vectors test the Python policy; supplied records also execute
    the native companion. This is a local policy, not upstream Unicode parity.
    """
'''+s[b:]
    s=s.replace('rust_src = Path(__file__).resolve().parent / "rust_eis_companion.rs"',
                'rust_src = files("rsi_eis_resources").joinpath("rust_eis_companion.rs")')
    s=s.replace('        m0 = matches[0]',
                '        if (len(matches) != 1 or len(danger["evidence_spans"]) != 1\n'
                '                or len(context.get("detector_predicates", [])) > 1\n'
                '                or context.get("offsets_are_content") is not True):\n'
                '            raise ValueError("Unsupported EIS metadata wire shape")\n'
                '        m0 = matches[0]')
    s=s.replace('        stdin_lines.append("\\t".join(fields))',
                '        if any(any(c in field for c in "\\t\\r\\n") for field in fields):\n'
                '            raise ValueError("EIS metadata fields cannot contain wire delimiters")\n'
                '        stdin_lines.append("\\t".join(fields))')
    s=s.replace('with tempfile.TemporaryDirectory(prefix="rsi_rust_eis_") as tmp_dir:',
                'with as_file(rust_src) as rust_path, tempfile.TemporaryDirectory(prefix="rsi_rust_eis_") as tmp_dir:')
    s=s.replace('str(rust_src), "-o"', 'str(rust_path), "-o"')
    s=s.replace('"verified_receipt_count":', '"metadata_record_count":')
    s=s.replace('        "rust_companion_executed": True,',
                '        "rust_companion_executed": True,\n'
                '        "scope": "EIS_METADATA_ONLY",\n'
                '        "obstruction_predicates_checked": False,\n'
                '        "identity_contract": "ascii-identifiers-v2",')
    s += '\n\n# Compatibility name; the returned scope explicitly excludes obstruction replay.\ncross_check_receipts_against_rust_eis = cross_check_eis_metadata_against_rust\n'
    s=s.replace('Verifies two-signal independence matching `omega_epistemic_immune_system::independence::assert_signals_independent`',
                'Checks the declared host-role metadata policy with ASCII identifiers')
    s=s.replace('"""Verify two-signal independence matching `omega_epistemic_immune_system::independence::assert_signals_independent`."""',
                '"""Check role-label separation; trusted-host authenticity is an external premise."""')
    s=s.replace('"""Verify parity against the 55 independence vectors and 7 digest vectors from `omega_epistemic_immune_system`."""',
                '"""Check 55 local ASCII-policy vectors and 7 upstream digest vectors."""')
    return s
edit('code/eis_verifier.py', eis)
def rust(s):
    marker='    let folded = trim_python(observer).to_ascii_lowercase();'
    check='''    if [&context.detector_id, observer].iter().any(|identity| {
        identity.chars().any(|c| !(c.is_ascii_alphanumeric() || " ._:-".contains(c)))
    }) {
        return Err(("EIS_VALUE_ERROR".into(),
            "EIS_VALUE_ERROR: identities must use ASCII letters, digits, spaces, dot, underscore, colon or hyphen".into()));
    }
'''
    return s.replace(marker,check+marker)
edit('code/rsi_eis_resources/rust_eis_companion.rs', rust)

def hyper(s):
    s=s.replace('    solve_exact_rational_l1_dual_witness,','    solve_exact_rational_l1_dual_witness,\n    verify_exact_l1_repair,')
    s=s.replace('                    assert repair_res.is_certified, (\n                        "Active repair dual witness certificate verification failed"\n                    )',
                '                    if not verify_exact_l1_repair(active_complex, k_cochain, repair_res):\n'
                '                        raise ValueError("Active repair certificate rejected")')
    s=s.replace('                    if budget >= budget_cost:',
                '                    if type(budget_cost) is not int or budget_cost < 0:\n'
                '                        raise ValueError("Repair price must be an exact nonnegative integer")\n'
                '                    if repair_res.l1_repair_cost > 0 and budget_cost == 0:\n'
                '                        raise ValueError("Nonzero repair requires a positive license price")\n'
                '                    if budget >= budget_cost:')
    s=s.replace('            # Even if modular wrap temporarily coincides, positive effective lag on a moving carrier\n            # induces stale-section mismatch proportional to the effective lag.',
                '            # Synthetic age-sensitive fixture policy: equal content can still\n            # receive an imposed age penalty. This is not a transport theorem.')
    s=s.replace('    Mathematical mechanism:', '    Controlled synthetic fixture, not a derived channel mechanism:')
    s=s.replace('        "distribution_shift_verified": (', '        "experiment_scope": "CONTROLLED_SYNTHETIC_DEFECT_INJECTION",\n        "distribution_shift_verified": (')
    s=s.replace('cross_check_receipts_against_rust_eis', 'cross_check_eis_metadata_against_rust')
    return s
edit('code/higher_cell_async_hypergraph.py', hyper)
# Updated imports for the facade's two explicitly named compatibility exports.
with (root/'code/rsi_transition_harness.py').open('a') as f:
    f.write('\n')
edit('code/rsi_transition_harness.py', lambda s:s.replace('    cross_check_receipts_against_rust_eis\n',
    '    cross_check_eis_metadata_against_rust,\n    cross_check_receipts_against_rust_eis\n'))
# Discovery excludes historical runtime snapshots. Flat public modules stay import-compatible.
edit('pyproject.toml',lambda s:s.replace('dependencies = []','dependencies = ["numpy>=1.24", "scipy>=1.10"]')
    .replace('package-dir = {"" = "code"}', 'package-dir = {"" = "code"}\n'
    'packages = ["rsi_eis_resources"]\n'
    'py-modules = ['+', '.join(json.dumps(p.stem) for p in sorted((root/'code').glob('*.py')))+']\n\n'
    '[tool.setuptools.package-data]\nrsi_eis_resources = ["*.json", "*.rs"]\n\n'
    '[project.scripts]\nrsi-transitions = "rsi_transition_harness:main"\nrsi-memory = "memory_cli:main"'))
edit('verify_deposit.py', lambda s:s.replace('code/rust_eis_companion.rs','code/rsi_eis_resources/rust_eis_companion.rs')
    .replace('code/eis_independence_vectors_v1.json','code/rsi_eis_resources/eis_independence_vectors_v2.json'))
for p in (root/'code/tests').glob('*.py'):
    s=p.read_text(encoding='utf-8')
    if 'verified_receipt_count' in s:
        edit(p.relative_to(root).as_posix(),lambda s:s.replace('verified_receipt_count','metadata_record_count'))
print('Prepared review custody and implementation repairs')
