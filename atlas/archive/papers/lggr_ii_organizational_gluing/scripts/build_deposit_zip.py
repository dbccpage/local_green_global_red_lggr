#!/usr/bin/env python3
"""Build the publishable archive from the pinned set, and nothing else.

The deposit IS the SHA256SUMS-pinned file list. Zipping the directory instead
would sweep in Lake build output (`lean4/b/`, whose `*.setup.json` embed
absolute local paths), pytest scratch, caches, the operator checklist, and any
material deliberately scoped out of the deposit. Those are not deposit members
and some of them leak local paths.

This reads SHA256SUMS, re-hashes every entry, refuses to build if anything
mismatches, and writes a deterministic zip containing exactly those files plus
SHA256SUMS itself.

    python scripts/build_deposit_zip.py            # -> <package>_2026-09-15.zip
    python scripts/build_deposit_zip.py --out X    # explicit output path

A hash match certifies that the bytes are the bytes that were hashed. It is
not evidence for any mathematical claim in the paper.
"""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "SHA256SUMS"
# Fixed timestamp so the archive is byte-reproducible across builds.
ZIP_DATE = (2026, 10, 15, 0, 0, 0)
RELEASE_DATE = "2026-10-15"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _validated_manifest_path(relative: str, lineno: int, root_dir: Path) -> Path:
    pure = PurePosixPath(relative)
    unsafe = (
        not relative
        or not pure.parts
        or pure.is_absolute()
        or pure.as_posix() != relative
        or ".." in pure.parts
        or "\\" in relative
        or ":" in pure.parts[0]
    )
    candidate = root_dir.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root_dir.resolve())
    except ValueError:
        unsafe = True
    current = root_dir
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            unsafe = True
            break
    if unsafe:
        raise ValueError(
            f"SHA256SUMS line {lineno} has unsafe path {relative!r}"
        )
    return candidate


def parse_manifest(
    manifest_path: Path = MANIFEST, root_dir: Path = ROOT
) -> list[tuple[str, str]]:
    if not manifest_path.is_file():
        raise ValueError("SHA256SUMS is missing; run scripts/regen_sha256sums.py first")
    entries: list[tuple[str, str]] = []
    seen_files_casefold: set[str] = set()
    seen_dirs: dict[str, str] = {}
    for lineno, raw in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) is None:
            raise ValueError(f"SHA256SUMS line {lineno} is malformed: {raw!r}")
        relative = parts[1].strip().lstrip("*")
        _validated_manifest_path(relative, lineno, root_dir)
        key = relative.casefold()
        if key in seen_files_casefold:
            raise ValueError(f"SHA256SUMS lists {relative} more than once")
        if key in seen_dirs:
            raise ValueError(
                f"SHA256SUMS path {relative!r} collides with directory {seen_dirs[key]!r}"
            )
        pure = PurePosixPath(relative)
        for i in range(1, len(pure.parts)):
            dir_parts = pure.parts[:i]
            dir_str = "/".join(dir_parts)
            dir_cf = dir_str.casefold()
            if dir_cf in seen_files_casefold:
                raise ValueError(
                    f"SHA256SUMS directory component {dir_str!r} collides with file path"
                )
            if dir_cf in seen_dirs:
                if seen_dirs[dir_cf] != dir_str:
                    raise ValueError(
                        f"SHA256SUMS directory component case collision: {dir_str!r} vs {seen_dirs[dir_cf]!r}"
                    )
            else:
                seen_dirs[dir_cf] = dir_str
        seen_files_casefold.add(key)
        entries.append((relative, parts[0].lower()))
    return entries


def main(argv: list[str]) -> int:
    try:
        entries = parse_manifest()
    except ValueError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    problems: list[str] = []
    for rel, digest in entries:
        p = ROOT / rel
        if not p.is_file():
            problems.append(f"missing: {rel}")
        elif sha256_of(p) != digest:
            problems.append(f"hash mismatch: {rel}")
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        print("refusing to build an archive from a tree that does not match its manifest")
        return 1

    out = (
        Path(argv[argv.index("--out") + 1])
        if "--out" in argv
        else ROOT / f"{ROOT.name}_{RELEASE_DATE}.zip"
    )
    prefix = ROOT.name

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, _ in sorted(entries) + [("SHA256SUMS", "")]:
            info = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (ROOT / rel).read_bytes())

    size = out.stat().st_size
    print(f"wrote {out} -- {len(entries) + 1} files, {size / 1024:.0f} KB")
    print("contains exactly the pinned set; no build output, caches or scratch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
