#!/usr/bin/env python3
"""Deterministically (re)generate or verify deposit checksum manifests.

A hash match certifies byte identity, not a mathematical claim.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from deposit_paths import walk_files

MANIFEST_NAME = "MANIFEST.sha256"
SUMS_NAME = "SHA256SUMS"

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", ".lake",
    "dist", "build", "htmlcov", "dev_rips", "rt", "target",
    "b", "scratch",
    "_support", "evidence", "reconstruction_v1",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".zip", ".log"}
EXCLUDED_NAMES = {
    ".coverage",
    ".env",
    MANIFEST_NAME,
    SUMS_NAME,
    "DEPOSIT_CHECKLIST.md",
    ".gitkeep",
}


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def iter_files(root: Path) -> list[Path]:
    return walk_files(root, EXCLUDED_DIRS, EXCLUDED_NAMES, EXCLUDED_SUFFIXES)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def render(root: Path) -> str:
    lines = [f"{sha256_of(p)}  {p.relative_to(root).as_posix()}" for p in iter_files(root)]
    return "\n".join(lines) + "\n"


def render_sums(root: Path, manifest: Path) -> str:
    """SHA256SUMS = every deposit file, plus MANIFEST.sha256 itself."""
    lines = [f"{sha256_of(p)}  {p.relative_to(root).as_posix()}" for p in iter_files(root)]
    lines.append(f"{sha256_of(manifest)}  {MANIFEST_NAME}")
    lines.sort(key=lambda s: s.partition("  ")[2])
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    root = package_root()
    manifest = root / MANIFEST_NAME
    sums = root / SUMS_NAME
    fresh = render(root)
    if "--check" in argv:
        problems: list[str] = []
        if not manifest.is_file():
            problems.append(f"{MANIFEST_NAME} is missing from {root}")
        elif manifest.read_bytes().decode("utf-8") != fresh:
            problems.append(f"{MANIFEST_NAME} does not match tree")
        if not sums.is_file():
            problems.append(f"{SUMS_NAME} is missing from {root}")
        elif not problems:
            if sums.read_bytes().decode("utf-8") != render_sums(root, manifest):
                problems.append(f"{SUMS_NAME} does not match tree")
        for p in problems:
            print(f"FAIL: {p}")
        if problems:
            return 1
        n = fresh.count("\n")
        print(f"OK: {MANIFEST_NAME} ({n} files) and {SUMS_NAME} ({n + 1}) match the tree")
        return 0
    manifest.write_bytes(fresh.encode("utf-8"))
    sums.write_bytes(render_sums(root, manifest).encode("utf-8"))
    print(
        f"wrote {MANIFEST_NAME} ({fresh.count(chr(10))} entries) "
        f"and {SUMS_NAME} ({fresh.count(chr(10)) + 1} entries)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
