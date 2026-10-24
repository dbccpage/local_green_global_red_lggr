#!/usr/bin/env python3
"""Read-only verification; requested replay profiles fail on missing dependencies."""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
from rebuild_release import read_manifest, safe_file, sha256_file, validate, current_entries
from replay_lean_axiom_census import audit


def verify_hashes():
    entries = read_manifest(ROOT / "MANIFEST.sha256", ROOT)
    sums = read_manifest(ROOT / "SHA256SUMS", ROOT)
    if dict(sums) != dict(entries + [("MANIFEST.sha256", sha256_file(ROOT / "MANIFEST.sha256"))]):
        raise ValueError("SHA256SUMS differs from manifest plus its digest")
    if dict(current_entries(ROOT)) != dict(entries):
        raise ValueError("Release membership or payload differs from manifest")
    for relative, expected in sums:
        if sha256_file(safe_file(ROOT, relative)) != expected:
            raise ValueError(f"Sealed byte mismatch: {relative}")
    return {name: digest for name, digest in sums}


def run(*args):
    result = subprocess.run([sys.executable, *args], cwd=ROOT, timeout=1800)
    if result.returncode:
        raise ValueError(f"Requested replay failed: {' '.join(args)}")


def binding_checks():
    custody = json.loads((ROOT / "docs/source_custody.json").read_text(encoding="utf-8"))
    for name, relative in {
        "institutional_reasoning.py": "code/institutional_reasoning.py",
        "test_institutional_reasoning.py": "code/tests/test_institutional_reasoning.py",
        "anomalon_institutional_reasoning.contract.yaml": "contracts/anomalon_institutional_reasoning.contract.yaml",
        "source_register.json": "docs/supplied_source_register.json",
    }.items():
        if sha256_file(ROOT / relative) != custody["supplied_files"][name]:
            raise ValueError(f"Unchanged supplied artifact drift: {relative}")
    execution = json.loads((ROOT / "docs/python_execution.json").read_text(encoding="utf-8"))
    if execution["success"] is not True or execution["tests_run"] != 17:
        raise ValueError("Unexpected finite execution receipt")
    for name, digest in execution["source_hashes"].items():
        if sha256_file(safe_file(ROOT, name)) != digest:
            raise ValueError(f"Execution source binding drift: {name}")
    receipt = json.loads((ROOT / "docs/render_receipt.json").read_text(encoding="utf-8"))
    for name, digest in receipt["artifacts"].items():
        if sha256_file(safe_file(ROOT, name)) != digest:
            raise ValueError(f"Rendered artifact drift: {name}")
    for key, name in {
        "spine_sha256": "institutions_that_can_know_math_spine.md",
        "registry_sha256": "institutions_that_can_know_math_spine.json",
        "preamble_sha256": "scripts/obstruction-preamble.tex",
        "builder_sha256": "scripts/paper_spine.py",
    }.items():
        if sha256_file(ROOT / name) != receipt[key]:
            raise ValueError(f"Render input drift: {name}")
    docx = json.loads((ROOT / "docs/docx_receipt.json").read_text(encoding="utf-8"))
    if (docx["manuscript_sha256"] != receipt["manuscript_sha256"] or
        sha256_file(safe_file(ROOT, docx["artifact"])) != docx["sha256"] or
        sha256_file(ROOT / "tools/build_docx.py") != docx["builder_sha256"]):
        raise ValueError("DOCX source/artifact binding drift")
    metadata = json.loads((ROOT / "zenodo_metadata.json").read_text(encoding="utf-8"))
    if (metadata["version"], metadata["publication_date"]) != ("0.1.0", "2026-10-23"):
        raise ValueError("Unexpected edition identity; update verifier deliberately for a new edition")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["test", "lean", "contract", "notebook", "documents", "archive"]:
        parser.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    try:
        sealed = verify_hashes()
        binding_checks()
        audit(ROOT, replay=args.lean)
        if args.test:
            run("tools/run_checks.py")
        if args.contract:
            run("tools/check_contract.py")
        if args.notebook:
            run("tools/replay_notebook.py")
        if args.lean:
            run("tools/replay_full_axiom_census.py", "--check")
        if args.documents:
            run("scripts/paper_spine.py", "verify")
        if args.archive:
            errors = validate(ROOT)
            if errors:
                raise ValueError("; ".join(errors))
        if verify_hashes() != sealed:
            raise ValueError("Sealed inputs changed during verification")
        print(f"PASS: {len(sealed)} sealed entries unchanged; bindings and requested profiles verified")
        return 0
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
