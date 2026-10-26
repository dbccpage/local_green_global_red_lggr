"""Demo: two reviewed changes silently disable a gate's pre-review check.

AuthorityEffect: None. No model calls, no network. Builds a throwaway git repo in a temp dir.

Run:  python -m lggr_guard.ledger_demo        (add --json for full receipts)

The toy gate has a precheck that bounces undeclared behaviour changes.
  A  "make precheck configurable"  reads cfg["precheck_enabled"], adds it to defaults.json (default on)
  B  "reject unknown config keys"  config.load() keeps only keys in KNOWN_KEYS
Each passes alone. Merged together, B drops A's key, cfg.get(..., False) wins, and the
precheck silently stops bouncing anything. Git merges them without a conflict.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from .replay import GitComposer, MemoryComposer, candidate_from_branch, load_suite_from_ref
from .gate import CompositionGate
from .ledger import Ledger
from .model import Candidate, Fact, Suite, drift_budget

MAIN_FILES = {
    "gate/__init__.py": "",
    "gate/defaults.json": '{\n  "review_model": "opus",\n  "max_diff_lines": 800\n}\n',
    "gate/config.py": (
        "import json, pathlib\n\n"
        "DEFAULTS = pathlib.Path(__file__).with_name('defaults.json')\n\n\n"
        "def load(overrides=None):\n"
        "    cfg = json.loads(DEFAULTS.read_text())\n"
        "    cfg.update(overrides or {})\n"
        "    return cfg\n"
    ),
    "gate/precheck.py": (
        "def enabled(cfg):\n"
        "    return True\n\n\n"
        "def precheck(change, cfg):\n"
        "    if not enabled(cfg):\n"
        "        return 'SKIPPED'\n"
        "    return 'BOUNCE' if change.get('undeclared_behaviour') else 'PASS'\n"
    ),
    ".lggr/suite.py": '''"""Read from main by the gate. Workers cannot change what this file means for their own change."""
from lggr_guard import Contract, Fact, Suite, equals, run_json

# The probe: a deliberately bad change the running gate must still bounce.
OBSERVE = r"""
import json
from gate import config, precheck
cfg = config.load()
print(json.dumps({
    "precheck.bounces_undeclared": precheck.precheck({"undeclared_behaviour": True}, cfg) == "BOUNCE",
    "review.model": cfg.get("review_model"),
    "gate.max_diff_lines": cfg.get("max_diff_lines"),
}))
"""

SUITE = Suite(
    facts=(
        Fact("precheck.bounces_undeclared", (True, False)),
        Fact("review.model", ("opus", "sonnet", "haiku")),
        Fact("gate.max_diff_lines"),
    ),
    contracts=(
        equals("precheck-on-by-default", "precheck.bounces_undeclared", True,
               description="With default config, the precheck bounces an undeclared behaviour change"),
        equals("reviewer-is-opus", "review.model", "opus"),
        Contract("diff-cap", ("gate.max_diff_lines",), lambda f, a: f["gate.max_diff_lines"] <= 1000,
                 "Review never sees diffs over 1000 lines", probe=({"gate.max_diff_lines": 5000}, {})),
    ),
    observe=lambda worktree: run_json(worktree, OBSERVE),
    protected_paths=(".lggr/", "tests/protected/", "prompts/"),
)
''',
}

BRANCHES: dict[str, tuple[str, dict[str, str]]] = {
    "A-configurable-precheck": ("main", {
        "gate/defaults.json": '{\n  "precheck_enabled": true,\n  "review_model": "opus",\n  "max_diff_lines": 800\n}\n',
        "gate/precheck.py": MAIN_FILES["gate/precheck.py"].replace(
            "    return True\n", "    return bool(cfg.get('precheck_enabled', False))\n"),
    }),
    "B-reject-unknown-keys": ("main", {
        "gate/config.py": MAIN_FILES["gate/config.py"].replace(
            "DEFAULTS = pathlib", "KNOWN_KEYS = {'review_model', 'max_diff_lines'}\nDEFAULTS = pathlib").replace(
            "    cfg = json.loads(DEFAULTS.read_text())\n",
            "    cfg = {k: v for k, v in json.loads(DEFAULTS.read_text()).items() if k in KNOWN_KEYS}\n"),
    }),
}


def _git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "demo", "GIT_AUTHOR_EMAIL": "demo@example.invalid",
           "GIT_COMMITTER_NAME": "demo", "GIT_COMMITTER_EMAIL": "demo@example.invalid"}
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, env=env).stdout.strip()


def _commit(repo: Path, files: dict[str, str], message: str) -> None:
    for rel, body in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


def _branch(repo: Path, name: str, start: str, files: dict[str, str]) -> None:
    _git(repo, "checkout", "-q", "-b", name, start)
    _commit(repo, files, name)
    _git(repo, "checkout", "-q", "main")


def build_repo(root: Path) -> Path:
    repo = root / "gatebot"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _commit(repo, MAIN_FILES, "main: gate with precheck")
    for name, (start, files) in BRANCHES.items():
        _branch(repo, name, start, files)
    return repo


def _gate(repo: Path, ledger: Ledger) -> CompositionGate:
    suite = load_suite_from_ref(repo, "main")
    base = ledger.checkpoint["ref"] if ledger.checkpoint else "main"
    return CompositionGate(suite, GitComposer(repo, base, suite.observe), ledger)


def _row(label: str, receipt: dict[str, Any]) -> dict[str, Any]:
    named = next((f for f in receipt["findings"] if f["kind"] == receipt["status"]), {})
    return {"scenario": label, "status": receipt["status"],
            "changes": named.get("changes") or [receipt.get("candidate")],
            "contract": named.get("contract") or named.get("code"),
            "also": sorted({f.get("code") or f["kind"] for f in receipt["findings"]
                            if f is not named and f["kind"] != "LOCAL_GREEN_GLOBAL_RED"}),
            "receipt": receipt}


def run_git_demo(root: Path) -> list[dict[str, Any]]:
    repo = build_repo(root)
    ledger = Ledger.memory()
    suite = load_suite_from_ref(repo, "main")
    main_sha = _git(repo, "rev-parse", "main")
    ledger.record_checkpoint(main_sha, suite.observe(repo), smoke="passed")
    ledger.record_anchor(ledger.checkpoint["facts"], approved_by="owner")
    rows = []

    # Each change alone, against a fresh checkpoint: what a per-PR reviewer sees.
    for name in BRANCHES:
        lone = CompositionGate(suite, GitComposer(repo, main_sha, suite.observe), Ledger(list(ledger.entries)))
        rows.append(_row(f"{name[0]} alone on main",
                        lone.check(candidate_from_branch(repo, name, "main", change_id=name[0]))))

    # A is accepted and merged.
    a = candidate_from_branch(repo, "A-configurable-precheck", "main", change_id="A")
    receipt_a = _gate(repo, ledger).check(a)
    ledger.record_accept(a, receipt_a, approved_by="orchestrator+reviewer")
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge A", "A-configurable-precheck")

    # B was branched before A merged. Its diff is still clean. The composition is not.
    b = candidate_from_branch(repo, "B-reject-unknown-keys", "main", change_id="B")
    rows.append(_row("B after A accepted", _gate(repo, ledger).check(b)))

    # vaisov's literal case: a later self-modification turns the check off by default and declares nothing.
    _branch(repo, "C-faster-gate", "main", {
        "gate/defaults.json": BRANCHES["A-configurable-precheck"][1]["gate/defaults.json"].replace("true", "false")})
    c = candidate_from_branch(repo, "C-faster-gate", "main", change_id="C")
    rows.append(_row("C disables precheck default", _gate(repo, ledger).check(c)))

    # D does the same and also weakens the suite. The gate still judges it with main's suite.
    suite_text = (repo / ".lggr/suite.py").read_text()
    weakened = suite_text.replace('        equals("precheck-on-by-default"', '        # removed: equals("precheck-on-by-default"')
    weakened = weakened.replace('               description="With default config', '        #       description="With default config')
    _branch(repo, "D-faster-gate-and-suite", "main", {
        "gate/defaults.json": BRANCHES["A-configurable-precheck"][1]["gate/defaults.json"].replace("true", "false"),
        ".lggr/suite.py": weakened})
    d = candidate_from_branch(repo, "D-faster-gate-and-suite", "main", change_id="D")
    rows.append(_row("D also edits the suite", _gate(repo, ledger).check(d)))

    # Every contract still holds, but the observed effect was never declared: the model-mismatch alarm.
    _branch(repo, "F-bigger-diffs", "main", {
        "gate/defaults.json": BRANCHES["A-configurable-precheck"][1]["gate/defaults.json"].replace("800", "950")})
    f_quiet = candidate_from_branch(repo, "F-bigger-diffs", "main", change_id="F")
    rows.append(_row("F undeclared, contracts green", _gate(repo, ledger).check(f_quiet)))
    f_said = candidate_from_branch(repo, "F-bigger-diffs", "main", change_id="F'", declares={"gate.max_diff_lines": 950})
    rows.append(_row("F' same diff, declared", _gate(repo, ledger).check(f_said)))
    return rows


def run_drift_demo() -> list[dict[str, Any]]:
    """Two threshold relaxations, each inside the budget, together outside it."""
    suite = Suite(facts=(Fact("review.pass_threshold"),),
                  contracts=(drift_budget("threshold-drift", "review.pass_threshold", 5),),
                  observe=lambda state: {"review.pass_threshold": state["threshold"]})
    ledger = Ledger.memory()
    composer = MemoryComposer({"threshold": 90}, suite.observe)
    ledger.record_checkpoint("cfg@0", composer.facts([]), smoke="passed")
    ledger.record_anchor({"review.pass_threshold": 90}, approved_by="owner")

    def lower(by: int):
        return lambda state: state.__setitem__("threshold", state["threshold"] - by)

    e1 = Candidate("E1", {"review.pass_threshold": 87}, ref=lower(3))
    gate = CompositionGate(suite, composer, ledger)
    ledger.record_accept(e1, gate.check(e1), approved_by="reviewer")
    e2 = Candidate("E2", {"review.pass_threshold": 84}, ref=lower(3))
    return [_row("E2 after E1 (drift)", CompositionGate(suite, composer, ledger).check(e2))]


def main(argv: list[str] | None = None) -> int:
    as_json = "--json" in (argv or [])
    with tempfile.TemporaryDirectory(prefix="lggr-guard-demo-") as td:
        rows = run_git_demo(Path(td)) + run_drift_demo()
    if as_json:
        print(json.dumps([r["receipt"] for r in rows], indent=2, sort_keys=True))
        return 0
    width = max(len(r["scenario"]) for r in rows)
    for r in rows:
        print(f"{r['scenario']:<{width}}  {r['status']:<23} {'+'.join(r['changes']):<8} "
              f"{r['contract'] or '':<24} {', '.join(r['also'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
