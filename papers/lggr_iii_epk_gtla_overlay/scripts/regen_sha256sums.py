#!/usr/bin/env python3
"""Generate or verify the exact public-deposit checksum manifests."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MANIFEST_NAME = "MANIFEST.sha256"
SUMS_NAME = "SHA256SUMS"

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", ".uv-cache", ".uv-python", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", ".lake", "b", "scratch",
    "dist", "build", "htmlcov", "dev_rips", "rt", "_support", "research"
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".zip"}
EXCLUDED_NAMES = {
    ".coverage",
    MANIFEST_NAME,
    SUMS_NAME,
    "DEPOSIT_CHECKLIST.md",
    "0_lggr_iii_epk_gtla_overlay.pdf",
}

PUBLIC_NOTEBOOKS = {
    "00_start_here.ipynb",
    "01_two_passes_one_failure.ipynb",
    "02_why_zero_can_mislead.ipynb",
    "03_when_paths_compose.ipynb",
    "04_when_grouping_loses_information.ipynb",
    "05_one_record_six_roles.ipynb",
    "06_reviewer_verification.ipynb",
}
PUBLIC_LEAN_FILES = {
    "AXIOM_REPORT.txt",
    "Core.lean",
    "check_axioms.lean",
    "lakefile.lean",
    "lake-manifest.json",
    "lean-toolchain",
}


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root)
        if any(
            part in EXCLUDED_DIRS or part.endswith(".egg-info")
            for part in rel.parts
        ):
            continue
        if p.suffix in EXCLUDED_SUFFIXES:
            continue
        if p.name in EXCLUDED_NAMES or p.name.startswith(".coverage"):
            continue
        if rel.parts[0] == "jupyter_notebooks" and p.suffix == ".ipynb":
            if p.name not in PUBLIC_NOTEBOOKS:
                continue
        if rel.parts[0] == "lean4" and p.name not in PUBLIC_LEAN_FILES:
            continue
        out.append(p)
    out.sort(key=lambda p: p.relative_to(root).as_posix())
    return out


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def render(root: Path) -> str:
    lines = [f"{sha256_of(p)}  {p.relative_to(root).as_posix()}" for p in iter_files(root)]
    return "\n".join(lines) + "\n"


def render_sums(root: Path, manifest_bytes: bytes) -> str:
    lines = [
        f"{sha256_of(path)}  {path.relative_to(root).as_posix()}"
        for path in iter_files(root)
    ]
    lines.append(f"{hashlib.sha256(manifest_bytes).hexdigest()}  {MANIFEST_NAME}")
    lines.sort(key=lambda line: line.partition("  ")[2])
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    root = package_root()
    manifest = root / MANIFEST_NAME
    sums = root / SUMS_NAME
    fresh = render(root)
    fresh_bytes = fresh.encode("utf-8")
    fresh_sums = render_sums(root, fresh_bytes)
    if "--check" in argv:
        problems = []
        if not manifest.is_file() or manifest.read_text(encoding="utf-8") != fresh:
            problems.append(MANIFEST_NAME)
        if not sums.is_file() or sums.read_text(encoding="utf-8") != fresh_sums:
            problems.append(SUMS_NAME)
        if problems:
            print("FAIL: stale or missing " + ", ".join(problems))
            return 1
        print(f"OK: both manifests match the public tree ({fresh.count(chr(10))} files)")
        return 0
    manifest.write_bytes(fresh_bytes)
    sums.write_text(fresh_sums, encoding="utf-8", newline="\n")
    print(f"wrote {MANIFEST_NAME} and {SUMS_NAME}: {fresh.count(chr(10)) + 1} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
