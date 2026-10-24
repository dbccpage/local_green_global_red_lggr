"""Bind reviewed sources, relevant API parity, and artifact distinctions to Git blobs."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess

PIN = "6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85"
LAB = Path(__file__).resolve().parents[2]
ROOT = LAB.parents[1]
HERE = Path(__file__).resolve().parent
PAPER = "papers/lggr_viii_online_streaming_discovery_and_runtime_gluing"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    head = git("rev-parse", "HEAD").decode().strip()
    groups = [
        ("1_readme", ["README.md"]),
        ("2_core", [f"lggr/{name}.py" for name in ("descent", "witnesses", "linear", "transport")]),
        ("3_streaming", ["lggr/streaming.py"]),
        ("4_cookbooks", [f"cookbooks/{name}.py" for name in
                         ("01_online_fiber_monitoring", "02_streaming_budget_audit", "03_cochain_cycle_repair", "04_swarm_runtime_guard")]),
        ("5_benchmarks_and_tests", ["lggr/benchmarks.py", "tests/test_streaming.py", "tests/test_stress_multicycle_and_merges.py", "tests/test_live_benchmarks.py"]),
        ("6_volume_viii", git("ls-tree", "-r", "--name-only", PIN, PAPER).decode().splitlines()),
        ("7_root_lean", ["lean4/LggrVIII.lean", "lean4/CheckAxioms.lean", "lean4/LggrVII.lean", "lean4/lean-toolchain", "lean4/lakefile.lean"]),
        ("additional_runtime", ["lggr/__main__.py", "lggr/common.py", "lggr/__init__.py"]),
    ]
    inspected = []
    for group, paths in groups:
        for path in paths:
            blob = git("show", f"{PIN}:{path}")
            item = {"group": group, "path": path, "size_bytes": len(blob),
                    "git_blob_sha1": git("rev-parse", f"{PIN}:{path}").decode().strip(),
                    "sha256": hashlib.sha256(blob).hexdigest(),
                    "current_git_blob_sha1": git("rev-parse", f"{head}:{path}").decode().strip()}
            item["same_git_blob_at_current_head"] = item["git_blob_sha1"] == item["current_git_blob_sha1"]
            inspected.append(item)
    selected = ["StreamingFiberMonitor", "StreamingAuditMonitor", "StreamingBaselineComparator"]
    def symbols(commit):
        code = git("show", f"{commit}:lggr/streaming.py")
        tree = ast.parse(code)
        return {node.name: ast.dump(node, include_attributes=False) for node in tree.body if isinstance(node, ast.ClassDef)}
    original, current = symbols(PIN), symbols(head)
    parity = {name: original[name] == current[name] for name in selected}
    receipts = []
    for name in ("empirical_ngd_benchmark", "test1_fiber_collision", "test2_prefix_breach", "test3_cochain_cycle", "test4_composable_lggg"):
        path = f"{PAPER}/receipts/{name}.json"
        data = json.loads(git("show", f"{PIN}:{path}"))
        receipts.append({"path": path, "model": data.get("model"), "completion_count": data.get("completion_count"),
                         "metrics": data.get("metrics"), "final_status": data.get("final_status"),
                         "scope": "Historical stored receipt inspected and replayed offline; no new model call"})
    record = {"schema": "grok-swarm-lab.source-inspection.v1", "reviewed_commit": PIN,
              "current_head_observed": head, "read_order": [g for g, _ in groups],
              "sources": inspected, "reused_streaming_class_ast_parity": parity,
              "historical_receipt_summaries": receipts,
              "root_and_paper_local_lean_are_identical":
                  git("show", f"{PIN}:lean4/LggrVIII.lean") == git("show", f"{PIN}:{PAPER}/lean4/LggrVIII.lean"),
              "root_and_paper_python_are_same_artifact": False,
              "limitations": ["AST equality ignores comments and source formatting; blob hashes preserve exact bytes.",
                              "Hashes bind bytes and do not establish truth or author identity.",
                              "Current complete checkout changed concurrently; the laboratory dependency remains pinned."]}
    (HERE / "inspected_source_manifest.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (HERE / "reviewed_to_current.diff").write_bytes(git("diff", PIN, head, "--", "lggr", "tests/test_stress_multicycle_and_merges.py", "lean4"))
    print(json.dumps({"sources": len(inspected), "selected_class_parity": parity, "current_head": head}, indent=2))


if __name__ == "__main__":
    main()
