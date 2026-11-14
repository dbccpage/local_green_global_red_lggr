#!/usr/bin/env python3
"""Deterministically regenerate or verify the public-file manifests.

A hash match certifies only byte identity. It is not evidence for a
mathematical claim in the paper.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


MANIFEST_NAME = "MANIFEST.sha256"
SUMS_NAME = "SHA256SUMS"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    ".lake",
    "dist",
    "build",
    "htmlcov",
    "dev_rips",
    "rt",
    "scratch",
    "legacy_omnibus",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".zip"}
EXCLUDED_NAMES = {
    ".coverage",
    MANIFEST_NAME,
    SUMS_NAME,
    "DEPOSIT_CHECKLIST.md",
}
PUBLIC_NOTEBOOKS = {
    "01_observation_blind_spots.ipynb",
    "02_adjoint_probes_and_falsifiers.ipynb",
}


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def iter_files(root: Path) -> list[Path]:
    """Return the exact public-file set in stable path order."""

    output: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if any(part.endswith(".egg-info") for part in relative.parts):
            continue
        if (
            relative.parts[0] == "jupyter_notebooks"
            and path.suffix == ".ipynb"
            and path.name not in PUBLIC_NOTEBOOKS
        ):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.name in EXCLUDED_NAMES:
            continue
        output.append(path)
    output.sort(key=lambda path: path.relative_to(root).as_posix())
    return output


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render(root: Path) -> str:
    lines = [
        f"{sha256_of(path)}  {path.relative_to(root).as_posix()}"
        for path in iter_files(root)
    ]
    return "\n".join(lines) + "\n"


def render_sums(root: Path, manifest: Path) -> str:
    """Render every public file plus the finalized carrier manifest."""

    lines = [
        f"{sha256_of(path)}  {path.relative_to(root).as_posix()}"
        for path in iter_files(root)
    ]
    lines.append(f"{sha256_of(manifest)}  {MANIFEST_NAME}")
    lines.sort(key=lambda line: line.partition("  ")[2])
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
        elif manifest.read_text(encoding="utf-8") != fresh:
            problems.append(f"{MANIFEST_NAME} does not match tree")
        if not sums.is_file():
            problems.append(f"{SUMS_NAME} is missing from {root}")
        elif not problems and sums.read_text(encoding="utf-8") != render_sums(
            root, manifest
        ):
            problems.append(f"{SUMS_NAME} does not match tree")
        for problem in problems:
            print(f"FAIL: {problem}")
        if problems:
            return 1
        count = fresh.count("\n")
        print(
            f"OK: {MANIFEST_NAME} ({count} files) and "
            f"{SUMS_NAME} ({count + 1}) match the tree"
        )
        return 0

    manifest.write_text(fresh, encoding="utf-8", newline="\n")
    sums.write_text(render_sums(root, manifest), encoding="utf-8", newline="\n")
    count = fresh.count("\n")
    print(
        f"wrote {MANIFEST_NAME} ({count} entries) and "
        f"{SUMS_NAME} ({count + 1} entries)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
