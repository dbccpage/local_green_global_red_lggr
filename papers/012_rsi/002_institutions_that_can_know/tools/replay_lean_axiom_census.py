#!/usr/bin/env python3
"""Source-covered named theorem census. Generated declarations have a separate audit."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

WHITELIST = {"propext", "Quot.sound", "Classical.choice"}
ROW = re.compile(r"^'(.+)' (?:does not depend on any axioms|depends on axioms: \[(.*)\])$")


def strip_comments(text):
    result = []
    i = depth = 0
    string = False
    while i < len(text):
        if depth:
            if text.startswith('/-', i): depth += 1; i += 2
            elif text.startswith('-/', i): depth -= 1; i += 2
            else:
                if text[i] == '\n': result.append('\n')
                i += 1
        elif string:
            result.append(text[i])
            if text[i] == '\\' and i + 1 < len(text):
                result.append(text[i + 1]); i += 2
            else:
                if text[i] == '"': string = False
                i += 1
        elif text.startswith('/-', i): depth = 1; result.append(' '); i += 2
        elif text.startswith('--', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        else:
            result.append(text[i])
            if text[i] == '"': string = True
            i += 1
    if depth or string: raise ValueError('Unterminated comment or string')
    return ''.join(result)


def theorem_names(root):
    names = []
    for path in sorted((root / 'lean4').glob('*.lean')):
        if path.stem in {'Census', 'FullCensus', 'lakefile'}: continue
        text = strip_comments(path.read_text(encoding='utf-8'))
        if re.search(r'\b(sorry|admit)\b|^\s*(?:unsafe\s+)?axiom\s+', text, re.M):
            raise ValueError(f'Unfinished proof or custom axiom in {path.name}')
        namespaces = re.findall(r'^namespace ([A-Za-z0-9_.]+)\s*$', text, re.M)
        theorems = re.findall(r'^theorem ([A-Za-z0-9_]+)\b', text, re.M)
        if theorems and len(namespaces) != 1:
            raise ValueError(f'Unsupported namespace layout in {path.name}')
        names.extend(f'{namespaces[0]}.{name}' for name in theorems)
    if not names or len(names) != len(set(names)): raise ValueError('Empty or duplicate theorem coverage')
    return names


def rows(text):
    text = re.sub(r'(depends on axioms: \[)([^\]]*)(\])',
                  lambda m: m[1] + ' '.join(m[2].split()) + m[3], text)
    result = []
    for line in text.splitlines():
        match = ROW.fullmatch(line)
        if match:
            axioms = frozenset(a.strip() for a in (match[2] or '').split(',') if a.strip())
            if not axioms <= WHITELIST: raise ValueError(f'Unapproved axiom: {line}')
            result.append((match[1], axioms))
    return result


def run(lean, args):
    proc = subprocess.run(['lake', *args], cwd=lean, text=True, encoding='utf-8',
                          capture_output=True, timeout=600)
    if proc.returncode: raise ValueError(proc.stdout + proc.stderr)
    return proc.stdout


def input_hashes(root):
    paths = [p for p in (root / 'lean4').glob('*.lean') if p.stem not in {'Census', 'FullCensus'}]
    paths += [root / p for p in ['lean4/lean-toolchain', 'lean4/lake-manifest.json',
        'tools/replay_lean_axiom_census.py', 'tools/replay_full_axiom_census.py']]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def audit(root, write=False, replay=False):
    names = theorem_names(root)
    bound = input_hashes(root)
    binding = root / 'lean4/source_hashes.json'
    if not write and json.loads(binding.read_text(encoding='utf-8')) != bound:
        raise ValueError('LEAN_SOURCE_CHANGED: current inputs differ from the audited source map')
    lean = root / 'lean4'
    census = lean / 'Census.lean'
    report = lean / 'axiom_report.txt'
    expected_source = '-- All explicitly named theorems in the proof modules.\nimport Core\n\n'
    expected_source += ''.join(f'#print axioms {name}\n' for name in names)
    if write: census.write_text(expected_source, encoding='utf-8')
    elif census.read_text(encoding='utf-8') != expected_source:
        raise ValueError('Census coverage differs from source theorem inventory')
    if write or replay:
        run(lean, ['build'])
        actual = rows(run(lean, ['env', 'lean', 'Census.lean']))
        if [name for name, _ in actual] != names: raise ValueError('Lean coverage differs from source')
        if write:
            out = ['Named theorem axiom census', f'Declarations listed: {len(actual)}',
                   f'Declarations with no axioms: {sum(not a for _, a in actual)}',
                   f'Declarations with axiom dependencies: {sum(bool(a) for _, a in actual)}',
                   'Approved axioms: propext, Quot.sound, Classical.choice', '']
            for name, axioms in actual:
                out.append(f"'{name}' depends on axioms: [{', '.join(sorted(axioms))}]" if axioms
                           else f"'{name}' does not depend on any axioms")
            report.write_text('\n'.join(out) + '\n', encoding='utf-8')
        elif rows(report.read_text(encoding='utf-8')) != actual:
            raise ValueError('Stored report differs from current Lean output')
    expected = rows(report.read_text(encoding='utf-8'))
    if [name for name, _ in expected] != names: raise ValueError('Report omits source theorems')
    if input_hashes(root) != bound:
        raise ValueError('LEAN_SOURCE_CHANGED during census collection')
    if write:
        binding.write_text(json.dumps(bound, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(names)} named theorems, complete source coverage, approved axioms only')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true')
    group.add_argument('--replay', action='store_true')
    group.add_argument('--check', action='store_true')
    parser.add_argument('package_path', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try: audit(args.package_path.resolve(), args.write, args.replay)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}')
        raise SystemExit(1)
