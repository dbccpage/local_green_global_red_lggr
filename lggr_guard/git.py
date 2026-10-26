"""Git mode: compose real branches before merging them.

For each subset of the candidate branches (all subsets up to `exhaustive_limit`
branches, otherwise each branch alone plus all together), the base commit is
checked out in a temporary worktree, the branches are merged in order, and your
own check command runs there (exit 0 = pass). An optional observe command prints a
JSON object of observable behaviours (enabled gates, thresholds, default flags) used
for undeclared/emergent-change detection. Paths listed in `protected` (your probe and
acceptance tests, gate config, spec) are reset to the BASE commit after merging, so a
branch cannot weaken the checks that judge it. Merge conflicts count as failures.

AuthorityEffect: None. Nothing is merged or pushed; temporary worktrees are removed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .compose import Change, Check, compose_check


def _git(repo, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=check)


def _materialize(repo, base, branches, protected):
    """Return (worktree_path, merge_error)."""
    path = Path(tempfile.mkdtemp(prefix="lggr-guard-"))
    shutil.rmtree(path)
    _git(repo, "worktree", "add", "--detach", "--quiet", str(path), base)
    for branch in branches:
        merged = _git(path, "-c", "user.name=lggr-guard", "-c", "user.email=lggr-guard@localhost",
                      "merge", "--no-edit", "--quiet", branch, check=False)
        if merged.returncode:
            _git(path, "merge", "--abort", check=False)
            return path, f"merge conflict on {branch}"
    for item in protected:
        _git(path, "checkout", base, "--", item, check=False)
    return path, None


def compose_branches(repo, base, branches, check_cmd, observe_cmd=None, declares=None, protected=(),
                     exhaustive_limit=4, timeout=600):
    """`check_cmd`/`observe_cmd` are shell commands run inside each composed worktree."""
    repo = str(Path(repo).resolve())
    base_sha = _git(repo, "rev-parse", base).stdout.strip()
    cache = {}

    def evaluate(names):
        key = tuple(names)
        if key not in cache:
            path, error = _materialize(repo, base_sha, names, protected)
            try:
                if error:
                    cache[key] = {"pass": False, "detail": error, "behaviour": {}}
                else:
                    run = subprocess.run(check_cmd, cwd=path, shell=True, text=True, capture_output=True, timeout=timeout)
                    behaviour = {}
                    if observe_cmd:
                        out = subprocess.run(observe_cmd, cwd=path, shell=True, text=True, capture_output=True, timeout=timeout)
                        behaviour = json.loads(out.stdout or "{}")
                    cache[key] = {"pass": run.returncode == 0, "detail": (run.stdout + run.stderr)[-2000:], "behaviour": behaviour}
            finally:
                _git(repo, "worktree", "remove", "--force", str(path), check=False)
        return cache[key]

    # States are tuples of applied branch names; the gate composes them symbolically.
    changes = [Change(b, (lambda s, b=b: s + (b,)), frozenset((declares or {}).get(b, ()))) for b in branches]
    checks = [Check(check_cmd, lambda s: evaluate(s)["pass"])]
    report = compose_check((), changes, checks, observe=(lambda s: evaluate(s)["behaviour"]) if observe_cmd else None,
                           exhaustive_limit=exhaustive_limit)
    report["base"] = base_sha
    report["details"] = {"+".join(k) or "(base)": v["detail"] for k, v in cache.items()}
    return report
