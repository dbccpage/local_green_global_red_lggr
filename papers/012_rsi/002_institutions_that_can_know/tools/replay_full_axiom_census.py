#!/usr/bin/env python3
"""Replay axioms of all declarations in all deposited package-local Lean modules.

Lean enumerates the imported environment and selects declarations by their
defining module, including generated and private declarations. Imported Lean
library declarations are outside this package census. Historical named reports
remain unchanged. Run from the paper root after lake build.
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
from pathlib import Path

WHITELIST = {"propext", "Quot.sound", "Classical.choice"}
DEPENDENCY = re.compile(r"^'(.+)' depends on axioms: \[(.*)\]$")
NO_DEPENDENCY = re.compile(r"^'(.+)' does not depend on any axioms$")


def replay(root: Path, check: bool = True) -> int:
    lean = root / "lean4"
    modules = sorted(
        p.relative_to(lean).with_suffix("").as_posix().replace("/", ".")
        for p in lean.rglob("*.lean")
        if not any(part.startswith(".") for part in p.relative_to(lean).parts)
        and p.name not in {"lakefile.lean", "Census.lean", "FullCensus.lean"}
    )
    if not modules or any(not re.fullmatch(r"[A-Za-z0-9_.]+", m) for m in modules):
        raise ValueError("Missing or unsupported package-local module names")
    source = "\n".join(f"import {m}" for m in modules) + "\nimport Lean\n"
    source += "open Lean Elab Command\nrun_cmd do\n  let env ← getEnv\n"
    source += "  let modules : Array Name := #[" + ", ".join(f"`{m}" for m in modules) + "]\n"
    source += '''  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      if modules.contains env.header.moduleNames[idx.toNat]! then
        let axioms ← collectAxioms name
        if axioms.isEmpty then
          logInfo m!"'{name}' does not depend on any axioms"
        else
          let names := String.intercalate ", " (axioms.toList.map toString)
          logInfo m!"'{name}' depends on axioms: [{names}]"
'''
    census = lean / "FullCensus.lean"
    if check:
        # Compare text for portability, but compile the original sealed bytes.
        if not census.is_file() or census.read_text(encoding="utf-8") != source:
            raise ValueError("FullCensus.lean is missing or stale; regenerate explicitly with --write")
    else:
        census.write_bytes(source.encode("utf-8"))
    result = subprocess.run(["lake", "env", "lean", "FullCensus.lean"], cwd=lean,
                            text=True, encoding="utf-8", capture_output=True, timeout=1800)
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    rows = {}
    normalized = re.sub(r'(depends on axioms: \[)([^\]]*)(\])',
                        lambda m: m[1] + ' '.join(m[2].split()) + m[3], result.stdout)
    for line in normalized.splitlines():
        match = DEPENDENCY.fullmatch(line)
        empty = NO_DEPENDENCY.fullmatch(line)
        if match:
            name, axioms = match.groups()
            values = {v.strip() for v in axioms.split(",")}
        elif empty:
            name, values = empty.group(1), set()
        else:
            continue
        if name in rows:
            raise ValueError(f"Duplicate declaration: {name}")
        if not values <= WHITELIST:
            raise ValueError(f"Unapproved axioms for {name}: {sorted(values - WHITELIST)}")
        rows[name] = values
    if not rows:
        raise ValueError("Empty Lean declaration census")
    output = ["Full package-local Lean axiom census",
              f"Verification date: {datetime.date.today().isoformat()}",
              "Scope: all environment declarations defined in the listed package-local modules, including private and generated declarations.",
              "Modules: " + ", ".join(modules),
              f"Declarations listed: {len(rows)}",
              "Approved axioms: propext, Quot.sound, Classical.choice",
              "Execution: lake env lean FullCensus.lean exited 0.", ""]
    for name, values in sorted(rows.items()):
        output.append(f"'{name}' depends on axioms: [{', '.join(sorted(values))}]" if values
                      else f"'{name}' does not depend on any axioms")
    target = lean / "full_axiom_report.txt"
    rendered = "\n".join(output) + "\n"
    if check:
        stored = target.read_text(encoding="utf-8")
        normalize = lambda text: "\n".join(line for line in text.splitlines() if not line.startswith("Verification date:"))
        if normalize(stored) != normalize(rendered):
            raise ValueError("Full declaration report differs from current Lean output")
    else:
        target.write_bytes(rendered.encode("utf-8"))
    print(f"PASS: {len(rows)} package-local declarations; {len(modules)} modules; approved axioms only")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Read-only replay (the default)")
    mode.add_argument("--write", action="store_true", help="Regenerate census source and report")
    args = parser.parse_args()
    try:
        return replay(args.package.resolve(), check=not args.write)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
