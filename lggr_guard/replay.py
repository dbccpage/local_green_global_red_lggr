"""Composers build "base + these changes" and hand it to the suite's observer.

AuthorityEffect: None.
Standard library only: Python 3.10+.

``GitComposer`` replays each change's diff onto the last checkpoint in a throwaway
worktree. ``MemoryComposer`` does the same on a dict, for tests and for systems
whose state is configuration rather than code.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from typing import Any, Callable, Mapping, Sequence

from .model import Candidate, Suite


class CompositionError(Exception):
    """A composition could not be built or observed. ``code`` is MERGE_CONFLICT or OBSERVER_FAILED."""

    def __init__(self, code: str, detail: str, change_id: str | None = None) -> None:
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.change_id = code, detail, change_id


# ---------------------------------------------------------------- memory
class MemoryComposer:
    """State is a dict. A change's ``ref`` is a dict patch or a callable that edits the state in place.

    A dict patch may carry ``"_touches": [paths]`` so authority checks have something to read.
    """

    def __init__(self, base: Mapping[str, Any], observe: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        self.base = dict(base)
        self.observe = observe
        self.builds = 0

    def facts(self, changes: Sequence[Candidate]) -> dict[str, Any]:
        self.builds += 1
        state = copy.deepcopy(self.base)
        for change in changes:
            if callable(change.ref):
                change.ref(state)
            elif isinstance(change.ref, Mapping):
                state.update({k: v for k, v in change.ref.items() if not k.startswith("_")})
        try:
            return dict(self.observe(state))
        except Exception as exc:  # observer failure is out-of-model, not a pass
            raise CompositionError("OBSERVER_FAILED", repr(exc)) from exc

    def touched(self, change: Candidate) -> set[str]:
        if isinstance(change.ref, Mapping):
            return set(change.ref.get("_touches", ()))
        return set()


# ------------------------------------------------------------------- git
def git(repo: Path, *args: str, input: bytes | None = None, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", "-C", str(repo), *args], input=input, capture_output=True)
    if check and proc.returncode != 0:
        raise CompositionError("GIT_FAILED", proc.stderr.decode(errors="replace").strip())
    return proc


def rev_parse(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").stdout.decode().strip()


def candidate_from_branch(repo: str | Path, branch: str, main: str, *, change_id: str | None = None,
                       declares: Mapping[str, Any] | None = None, obligations: Sequence[str] = ()) -> Candidate:
    """The change a branch carries relative to its merge-base with ``main``."""
    repo = Path(repo)
    head = rev_parse(repo, branch)
    parent = git(repo, "merge-base", rev_parse(repo, main), head).stdout.decode().strip()
    return Candidate(change_id or branch, dict(declares or {}), tuple(obligations), (parent, head))


class GitComposer:
    """Apply each change's ``parent..head`` diff, three-way, onto ``base_ref`` in a temporary worktree."""

    def __init__(self, repo: str | Path, base_ref: str, observe: Callable[[Path], dict[str, Any]]) -> None:
        self.repo = Path(repo).resolve()
        self.base = rev_parse(self.repo, base_ref)
        self.observe = observe
        self.builds = 0

    def facts(self, changes: Sequence[Candidate]) -> dict[str, Any]:
        self.builds += 1
        with tempfile.TemporaryDirectory(prefix="lggr-guard-") as td:
            wt = Path(td) / "wt"
            git(self.repo, "worktree", "add", "--detach", "--quiet", str(wt), self.base)
            try:
                for change in changes:
                    parent, head = change.ref
                    diff = git(self.repo, "diff", "--binary", parent, head).stdout
                    if not diff:
                        continue
                    proc = git(wt, "apply", "--3way", "--index", "--whitespace=nowarn", input=diff, check=False)
                    if proc.returncode != 0:
                        raise CompositionError("MERGE_CONFLICT", proc.stderr.decode(errors="replace").strip(),
                                               change.change_id)
                try:
                    return dict(self.observe(wt))
                except CompositionError:
                    raise
                except Exception as exc:
                    raise CompositionError("OBSERVER_FAILED", repr(exc)) from exc
            finally:
                git(self.repo, "worktree", "remove", "--force", str(wt), check=False)

    def touched(self, change: Candidate) -> set[str]:
        parent, head = change.ref
        out = git(self.repo, "diff", "--name-only", parent, head).stdout.decode()
        return {line for line in out.splitlines() if line}


def run_json(worktree: str | Path, code: str, *, timeout: int = 120) -> dict[str, Any]:
    """Observer helper: run ``code`` with Python inside the worktree; its last stdout line must be a JSON object."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(worktree), env=env,
                          capture_output=True, text=True, timeout=timeout)
    lines = proc.stdout.strip().splitlines()
    if proc.returncode != 0 or not lines:
        raise CompositionError("OBSERVER_FAILED", (proc.stderr or proc.stdout).strip()[-800:])
    return json.loads(lines[-1])


# ---------------------------------------------------------------- suites
def _exec_suite(source: str, origin: str) -> Suite:
    module = types.ModuleType("lggr_guard_suite")
    module.__file__ = origin
    exec(compile(source, origin, "exec"), module.__dict__)
    suite = getattr(module, "SUITE", None)
    if not isinstance(suite, Suite):
        raise CompositionError("SUITE_INVALID", f"{origin} does not define SUITE = Suite(...)")
    suite.source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return suite


def load_suite_from_ref(repo: str | Path, ref: str, path: str = ".lggr/suite.py") -> Suite:
    """Read the suite from ``ref`` (main), never from the working tree or the candidate."""
    proc = git(Path(repo), "show", f"{rev_parse(Path(repo), ref)}:{path}", check=False)
    if proc.returncode != 0:
        raise CompositionError("SUITE_INVALID", f"{ref}:{path} not found")
    return _exec_suite(proc.stdout.decode("utf-8"), f"{ref}:{path}")


def load_suite_from_file(path: str | Path) -> Suite:
    return _exec_suite(Path(path).read_text(encoding="utf-8"), str(path))
