#!/usr/bin/env python3
"""Build the publishable archive from the pinned set, and nothing else.

The deposit IS the SHA256SUMS-pinned file list.
"""

from __future__ import annotations

import datetime
import hashlib
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from deposit_paths import read_manifest, safe_path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "SHA256SUMS"
# The dated archive name determines its fixed member timestamp.


def default_archive_name() -> str:
    today_str = datetime.date.today().isoformat()
    return f"{ROOT.name}_{today_str}.zip"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(manifest_path: Path = MANIFEST, root: Path = ROOT) -> list[tuple[str, str]]:
    return read_manifest(root, manifest_path)


def build_archive(out: Path, entries: list[tuple[str, str]]) -> None:
    """Write the fixed-order, fixed-metadata public archive."""
    seen: set[str] = set()
    for relative, digest in entries:
        path = safe_path(ROOT, relative)
        if relative.casefold() in seen:
            raise ValueError(f"duplicate archive member: {relative}")
        seen.add(relative.casefold())
        if path.suffix.lower() == ".zip" or sha256_of(path) != digest:
            raise ValueError(f"invalid archive input: {relative}")
    match = re.fullmatch(rf"{re.escape(ROOT.name)}_(\d{{4}}-\d{{2}}-\d{{2}})\.zip", out.name)
    if match is None or out.is_symlink():
        raise ValueError("archive output must be a dated regular release ZIP")
    day = datetime.date.fromisoformat(match.group(1))
    zip_date = (day.year, day.month, day.day, 12, 0, 0)
    out.parent.mkdir(parents=True, exist_ok=True)
    prefix = ROOT.name
    members = sorted(entries + [("SHA256SUMS", "")])
    with zipfile.ZipFile(
        out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for rel, _ in members:
            info = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=zip_date)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / rel).read_bytes(), compresslevel=9)


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

    if "--out" in argv:
        index = argv.index("--out")
        if index + 1 >= len(argv):
            print("FAIL: --out requires a path", file=sys.stderr)
            return 2
        out = Path(argv[index + 1])
    else:
        out = ROOT / default_archive_name()
    build_archive(out, entries)

    size = out.stat().st_size
    print(f"wrote {out} -- {len(entries) + 1} files, {size / 1024:.0f} KB")
    print("contains exactly the pinned set; no build output, caches or scratch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
