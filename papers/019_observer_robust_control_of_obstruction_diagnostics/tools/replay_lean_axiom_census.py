"""Replay the declared Lean census and bind its exact names to source bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT / "lean4", capture_output=True,
                            text=True, encoding="utf-8", timeout=180, check=False)
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    return result.stdout


def replay(write: bool) -> None:
    census = ROOT / "lean4/Census.lean"
    requested = re.findall(r"(?m)^#print axioms ([\w.']+)$", census.read_text(encoding="utf-8"))
    if not requested or len(set(requested)) != len(requested):
        raise ValueError("Missing or duplicate census declarations")
    declarations = []
    for path in sorted((ROOT / "lean4").glob("*.lean")):
        if path.name in {"lakefile.lean", "Census.lean"}:
            continue
        namespace = []
        for line in path.read_text(encoding="utf-8").splitlines():
            opening = re.match(r"^namespace\s+(\w+)", line)
            if opening:
                namespace.append(opening.group(1))
            if re.match(r"^end(?:\s|$)", line) and namespace:
                namespace.pop()
            declaration = re.match(r"^(?:noncomputable\s+)?(?:def|theorem|lemma|structure|inductive|abbrev|axiom|opaque|constant)\s+([\w']+)", line)
            if declaration:
                declarations.append(".".join(namespace + [declaration.group(1)]))
    if set(requested) != set(declarations) or len(declarations) != len(requested):
        raise ValueError("Census does not cover the exact source declaration set")
    source_paths = sorted((ROOT / "lean4").glob("*.lean"))
    source_paths += [ROOT / "lean4/lean-toolchain", ROOT / "lean4/lake-manifest.json", Path(__file__).resolve()]
    before = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    run(["lake", "build"])
    output = run(["lake", "env", "lean", "Census.lean"])
    reports = {}
    for line in output.splitlines():
        match = re.search(r"'([^']+)' (depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
        if not match:
            continue
        name = match.group(1)
        if name in reports:
            raise ValueError(f"Duplicate axiom report: {name}")
        axioms = sorted(x.strip() for x in (match.group(3) or "").split(",") if x.strip())
        if not set(axioms) <= ALLOWED:
            raise ValueError(f"Unadmitted axioms for {name}: {axioms}")
        reports[name] = axioms
    if set(reports) != set(requested):
        raise ValueError(f"Declaration-set mismatch: {set(reports) ^ set(requested)}")
    after = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    if before != after:
        raise ValueError("Formal sources changed during replay")
    report = "".join(f"'{name}' depends on axioms: [{', '.join(reports[name])}]\n" for name in requested)
    binding = {"declarations": requested, "source_sha256": before,
               "axiom_report_sha256": hashlib.sha256(report.encode("utf-8")).hexdigest(),
               "toolchain": (ROOT / "lean4/lean-toolchain").read_text(encoding="utf-8").strip()}
    serialized = json.dumps(binding, indent=2) + "\n"
    if write:
        (ROOT / "lean4/axiom_report.txt").write_text(report, encoding="utf-8", newline="\n")
        (ROOT / "lean4/axiom_binding.json").write_text(serialized, encoding="utf-8", newline="\n")
    elif (ROOT / "lean4/axiom_report.txt").read_text(encoding="utf-8") != report or (
        ROOT / "lean4/axiom_binding.json").read_text(encoding="utf-8") != serialized:
        raise ValueError("Stale axiom report or source binding")
    print(f"PASS: {len(requested)} exact declarations; only standard kernel axioms; source hashes unchanged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--write", action="store_true")
    choice.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        replay(args.write)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
