#!/usr/bin/env python3
"""Build the deterministic public archive from the SHA256SUMS-pinned set."""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent.parent
SUMS = ROOT / "SHA256SUMS"
RELEASE_DATE = "2026-10-15"
ARCHIVE_NAME = f"{ROOT.name}_{RELEASE_DATE}.zip"
ZIP_DATE = (2026, 10, 15, 0, 0, 0)
PUBLIC_NOTEBOOKS = {
    "jupyter_notebooks/01_observation_blind_spots.ipynb",
    "jupyter_notebooks/02_adjoint_probes_and_falsifiers.ipynb",
}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validated_manifest_path(relative: str, line_number: int, root: Path) -> Path:
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
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        unsafe = True
    if candidate.is_symlink():
        unsafe = True
    if unsafe:
        raise ValueError(
            f"SHA256SUMS line {line_number} has unsafe path {relative!r}"
        )
    return candidate


def parse_sums(
    sums_path: Path = SUMS, root: Path = ROOT
) -> list[tuple[str, str]]:
    if not sums_path.is_file():
        raise ValueError("SHA256SUMS is missing; run scripts/regen_sha256sums.py")

    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(
        sums_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) is None:
            raise ValueError(f"SHA256SUMS line {line_number} is malformed: {raw!r}")
        relative = parts[1].strip().lstrip("*")
        _validated_manifest_path(relative, line_number, root)
        key = relative.casefold()
        if key in seen:
            raise ValueError(f"SHA256SUMS lists {relative} more than once")
        seen.add(key)
        entries.append((relative, parts[0].lower()))
    return entries


def main(argv: list[str]) -> int:
    try:
        entries = parse_sums()
    except ValueError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    problems: list[str] = []
    names = {relative for relative, _ in entries}
    notebooks = {name for name in names if name.endswith(".ipynb")}
    if notebooks != PUBLIC_NOTEBOOKS:
        problems.append(
            f"public notebook set mismatch: expected {sorted(PUBLIC_NOTEBOOKS)}, "
            f"got {sorted(notebooks)}"
        )
    if any(name.startswith("research/legacy_omnibus/") for name in names):
        problems.append("research/legacy_omnibus is forbidden in the public archive")
    for relative, expected in entries:
        path = ROOT / relative
        if not path.is_file():
            problems.append(f"missing: {relative}")
        elif sha256_of(path) != expected:
            problems.append(f"hash mismatch: {relative}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print("refusing to build an archive from an invalid pinned tree")
        return 1

    if "--out" in argv:
        try:
            output = Path(argv[argv.index("--out") + 1])
        except IndexError:
            print("FAIL: --out requires a path", file=sys.stderr)
            return 1
    else:
        output = ROOT / ARCHIVE_NAME
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = ROOT.name

    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative, _ in sorted(entries) + [("SHA256SUMS", "")]:
            info = zipfile.ZipInfo(f"{prefix}/{relative}", date_time=ZIP_DATE)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / relative).read_bytes())

    print(
        f"wrote {output} -- {len(entries) + 1} files, "
        f"{output.stat().st_size / 1024:.0f} KiB"
    )
    print("contains exactly the pinned public set; legacy, caches, and build output are excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
